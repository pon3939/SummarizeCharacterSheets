# -*- coding: utf-8 -*-


from os import getenv

from aws_lambda_powertools.utilities.typing import LambdaContext
from my_modules.cloud_formation_response import CloudFormationResponse
from my_modules.common_functions import putCloudFormationResponse
from my_modules.constants.aws import (
    CLOUD_FORMATION_REQUEST_TYPE_DELETE,
    CLOUD_FORMATION_REQUEST_TYPE_MANUAL,
    CLOUD_FORMATION_STATUS_FAILED,
)
from my_modules.constants.env_keys import TEMPORARY_CAPACITY_UNITS
from my_modules.my_dynamo_db_client import MyDynamoDBClient
from my_modules.my_s3_client import MyS3Client
from mypy_boto3_dynamodb.type_defs import (
    DescribeTableOutputTypeDef,
    ProvisionedThroughputDescriptionTypeDef,
    ScanOutputTypeDef,
    TableDescriptionTypeDef,
)

"""
Dynamo DBをバックアップ
"""


def lambda_handler(event: dict, context: LambdaContext):
    """

    メイン処理

    Args:
        event dict: イベント
        context LambdaContext: コンテキスト
    """
    cloudFormationResponse: CloudFormationResponse = CloudFormationResponse(
        event
    )

    try:
        if cloudFormationResponse.RequestType not in (
            CLOUD_FORMATION_REQUEST_TYPE_DELETE,
            CLOUD_FORMATION_REQUEST_TYPE_MANUAL,
        ):
            # 削除時以外はスキップする
            putCloudFormationResponse(cloudFormationResponse)
            return

        tableNames: list[str] = event["ResourceProperties"]["TableNames"]
        bucketName: str = event["ResourceProperties"]["BucketName"]
        backupDynamoDb(tableNames, bucketName)
        putCloudFormationResponse(cloudFormationResponse)
    except Exception as e:
        putCloudFormationResponse(
            cloudFormationResponse,
            CLOUD_FORMATION_STATUS_FAILED,
            str(e),
        )


def backupDynamoDb(tableNames: list[str], bucketName: str):
    """Dynamo DBをバックアップする

    Args:
        tableNames: list[str]: バックアップ対象のテーブル名
        bucketName: str: バックアップ先のバケット名
    """
    dynamoDb: MyDynamoDBClient = MyDynamoDBClient()
    s3: MyS3Client = MyS3Client()
    for tableName in tableNames:
        # 読み込みキャパシティを一時的に増やす
        describeTableResponse: DescribeTableOutputTypeDef = (
            dynamoDb.DescribeTable(tableName)
        )
        table: TableDescriptionTypeDef = describeTableResponse["Table"]
        provisionedThroughput: ProvisionedThroughputDescriptionTypeDef = (
            table.get("ProvisionedThroughput", {})
        )
        readCapacityUnits: int = -1
        writeCapacityUnits: int = -1
        indexNames: list[str] = []
        updateReadCapacityUnits: int = int(
            getenv(TEMPORARY_CAPACITY_UNITS, "1")
        )
        if len(provisionedThroughput) != 0:
            for index in table.get("GlobalSecondaryIndexes", []):
                indexName: str = index.get("IndexName", "")
                if indexName == "":
                    continue

                indexNames.append(indexName)

            readCapacityUnits = provisionedThroughput.get(
                "ReadCapacityUnits", 1
            )
            writeCapacityUnits = provisionedThroughput.get(
                "WriteCapacityUnits", 1
            )
            if readCapacityUnits != updateReadCapacityUnits:
                dynamoDb.UpdateTable(
                    tableName,
                    updateReadCapacityUnits,
                    writeCapacityUnits,
                    indexNames,
                )

        # 全件取得
        response: ScanOutputTypeDef = dynamoDb.Scan(
            tableName,
        )

        if (
            readCapacityUnits != -1
            and writeCapacityUnits != -1
            and readCapacityUnits != updateReadCapacityUnits
        ):
            # もとのキャパシティに戻す
            dynamoDb.UpdateTable(
                tableName,
                readCapacityUnits,
                writeCapacityUnits,
                indexNames,
            )

        # S3に保存
        s3.PutBackupObject(
            bucketName,
            tableName,
            response["Items"],
        )
