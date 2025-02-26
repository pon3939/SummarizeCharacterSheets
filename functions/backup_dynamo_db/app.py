# -*- coding: utf-8 -*-


from aws_lambda_powertools.utilities.typing import LambdaContext
from my_modules.cloud_formation_response import CloudFormationResponse
from my_modules.common_functions import putCloudFormationResponse
from my_modules.constants.aws import (
    CLOUD_FORMATION_REQUEST_TYPE_DELETE,
    CLOUD_FORMATION_REQUEST_TYPE_MANUAL,
    CLOUD_FORMATION_STATUS_FAILED,
)
from my_modules.my_dynamo_db_client import MyDynamoDBClient
from my_modules.my_s3_client import MyS3Client
from mypy_boto3_dynamodb.type_defs import ScanOutputTypeDef

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
        backupDynamoDb(tableNames)
        putCloudFormationResponse(cloudFormationResponse)
    except Exception as e:
        putCloudFormationResponse(
            cloudFormationResponse,
            CLOUD_FORMATION_STATUS_FAILED,
            str(e),
        )


def backupDynamoDb(tableNames: list[str]):
    """Dynamo DBをバックアップする

    Args:
        tableNames: list[str]: バックアップ対象のテーブル名
    """
    dynamoDb: MyDynamoDBClient = MyDynamoDBClient()
    s3: MyS3Client = MyS3Client()
    for tableName in tableNames:
        # 全件取得
        response: ScanOutputTypeDef = dynamoDb.Scan(
            tableName,
        )

        # S3に保存
        s3.PutBackupObject(
            tableName,
            response["Items"],
        )
