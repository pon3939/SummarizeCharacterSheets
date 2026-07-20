# -*- coding: utf-8 -*-


from aws_lambda_powertools.utilities.typing import LambdaContext
from my_modules.aws.cloud_formation_response import CloudFormationResponse
from my_modules.aws.my_dynamo_db_client import MyDynamoDBClient
from my_modules.aws.my_s3_client import MyS3Client
from my_modules.common_functions import putCloudFormationResponse
from my_modules.constants.aws import (
    CLOUD_FORMATION_REQUEST_TYPE_CREATE,
    CLOUD_FORMATION_REQUEST_TYPE_MANUAL,
    CLOUD_FORMATION_STATUS_FAILED,
)
from mypy_boto3_dynamodb.type_defs import (
    AttributeValueTypeDef,
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
        restoreDynamoDb(tableNames)
        putCloudFormationResponse(cloudFormationResponse)
    except Exception as e:
        putCloudFormationResponse(
            cloudFormationResponse,
            CLOUD_FORMATION_STATUS_FAILED,
            str(e),
        )


def restoreDynamoDb(tableNames: list[str]):
    """Dynamo DBをリストアする

    Args:
        tableNames: list[str]: リストア対象のテーブル名
    """

    dynamoDb: MyDynamoDBClient = MyDynamoDBClient()
    s3: MyS3Client = MyS3Client()
    requestItems: dict[str, list[WriteRequestTypeDef]] = {}
    for tableName in tableNames:
        items: list[dict[str, AttributeValueTypeDef]] = s3.GetBackupObject(
            tableName,
        )
        if len(items) == 0:
            # ファイルが空の場合はスキップ
            continue

        requestItems[tableName] = []
        for item in items:
            requestItems[tableName].append({"PutRequest": {"Item": item}})

    if len(requestItems) == 0:
        # リストア対象がない場合は何もしない
        return

    dynamoDb.BatchWriteItem(requestItems)
