# -*- coding: utf-8 -*-


from os import getenv
from typing import Union

from aws_lambda_powertools.utilities.typing import LambdaContext
from my_modules.cloud_formation_response import CloudFormationResponse
from my_modules.common_functions import putCloudFormationResponse
from my_modules.constants.aws import (
    CLOUD_FORMATION_REQUEST_TYPE_CREATE,
    CLOUD_FORMATION_REQUEST_TYPE_MANUAL,
    CLOUD_FORMATION_STATUS_FAILED,
)
from my_modules.constants.env_keys import TEMPORARY_CAPACITY_UNITS
from my_modules.my_dynamo_db_client import MyDynamoDBClient
from my_modules.my_s3_client import MyS3Client
from mypy_boto3_dynamodb.type_defs import (
    AttributeValueTypeDef,
    DescribeTableOutputTypeDef,
    ProvisionedThroughputDescriptionTypeDef,
    TableDescriptionTypeDef,
    WriteRequestTypeDef,
)

"""
Dynamo DBをリストア
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
            CLOUD_FORMATION_REQUEST_TYPE_CREATE,
            CLOUD_FORMATION_REQUEST_TYPE_MANUAL,
        ):
            # 初回デプロイ時以外はスキップする
            putCloudFormationResponse(cloudFormationResponse)
            return

        tableNames: list[str] = event["ResourceProperties"]["TableNames"]
        bucketName: str = event["ResourceProperties"]["BucketName"]
        restoreDynamoDb(tableNames, bucketName)
        putCloudFormationResponse(cloudFormationResponse)
    except Exception as e:
        putCloudFormationResponse(
            cloudFormationResponse,
            CLOUD_FORMATION_STATUS_FAILED,
            str(e),
        )


def restoreDynamoDb(tableNames: list[str], bucketName: str):
    """Dynamo DBをリストアする

    Args:
        tableNames: list[str]: リストア対象のテーブル名
        bucketName: str: リストア先のバケット名
    """

    dynamoDb: MyDynamoDBClient = MyDynamoDBClient()
    s3: MyS3Client = MyS3Client()
    requestItems: dict[str, list[WriteRequestTypeDef]] = {}
    originalCapacityUnits: dict[str, dict[str, Union[int, list[str]]]] = {}
    for tableName in tableNames:
        items: list[dict[str, AttributeValueTypeDef]] = s3.GetBackupObject(
            bucketName,
            tableName,
        )
        if len(items) == 0:
            # ファイルが空の場合はスキップ
            continue

        requestItems[tableName] = []
        for item in items:
            requestItems[tableName].append({"PutRequest": {"Item": item}})

        # 書き込みキャパシティを一時的に増やす
        describeTableResponse: DescribeTableOutputTypeDef = (
            dynamoDb.DescribeTable(tableName)
        )
        table: TableDescriptionTypeDef = describeTableResponse["Table"]
        provisionedThroughput: ProvisionedThroughputDescriptionTypeDef = (
            table.get("ProvisionedThroughput", {})
        )
        if len(provisionedThroughput) == 0:
            # オンデマンドのため何もしない
            continue

        indexNames: list[str] = []
        for index in table.get("GlobalSecondaryIndexes", []):
            indexName: str = index.get("IndexName", "")
            if indexName == "":
                continue

            indexNames.append(indexName)

        readCapacityUnits: int = provisionedThroughput.get(
            "ReadCapacityUnits", 1
        )
        writeCapacityUnits: int = provisionedThroughput.get(
            "WriteCapacityUnits", 1
        )
        updateWriteCapacityUnits: int = int(
            getenv(TEMPORARY_CAPACITY_UNITS, "1")
        )
        if writeCapacityUnits == updateWriteCapacityUnits:
            # 変更不要
            continue

        dynamoDb.UpdateTable(
            tableName,
            readCapacityUnits,
            updateWriteCapacityUnits,
            indexNames,
        )

        # もとのキャパシティを保持しておく
        originalCapacityUnits[tableName] = {
            "readCapacityUnits": readCapacityUnits,
            "writeCapacityUnits": writeCapacityUnits,
            "indexNames": indexNames,
        }

    if len(requestItems) == 0:
        # リストア対象がない場合は何もしない
        return

    dynamoDb.BatchWriteItem(requestItems)

    for capacityUnitsTableName, capacityUnit in originalCapacityUnits.items():
        if (
            not isinstance(capacityUnit["readCapacityUnits"], int)
            or not isinstance(capacityUnit["writeCapacityUnits"], int)
            or not isinstance(capacityUnit["indexNames"], list)
        ):
            continue

        # もとのキャパシティに戻す
        dynamoDb.UpdateTable(
            capacityUnitsTableName,
            capacityUnit["readCapacityUnits"],
            capacityUnit["writeCapacityUnits"],
            capacityUnit["indexNames"],
        )
