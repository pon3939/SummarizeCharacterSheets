# -*- coding: utf-8 -*-

from os import getenv
from typing import Any

from aws_lambda_powertools.utilities.typing import LambdaContext
from my_modules.aws.cloud_formation_response import CloudFormationResponse
from my_modules.aws.my_dynamo_db_client import MyDynamoDBClient
from my_modules.common_functions import putCloudFormationResponse
from my_modules.constants.aws import (
    CLOUD_FORMATION_REQUEST_TYPE_CREATE,
    CLOUD_FORMATION_REQUEST_TYPE_MANUAL,
    CLOUD_FORMATION_STATUS_FAILED,
)
from my_modules.constants.env_keys import PREFIX
from mypy_boto3_dynamodb.type_defs import WriteRequestTypeDef

"""
Dynamo DBに登録
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

        inputData: dict[str, Any] = event["ResourceProperties"]["InputData"]
        tables: list[dict[str, Any]] = inputData["Tables"]
        insertDynamoDb(tables)
        putCloudFormationResponse(cloudFormationResponse)
    except Exception as e:
        putCloudFormationResponse(
            cloudFormationResponse,
            CLOUD_FORMATION_STATUS_FAILED,
            str(e),
        )


def insertDynamoDb(
    tables: list[dict[str, Any]],
):
    """DynamoDBにレコードを挿入する

    Args:
        tables: (list[dict[str, Any]]): 登録する情報
    """

    dynamoDb: MyDynamoDBClient = MyDynamoDBClient()
    requestItems: dict[str, list[WriteRequestTypeDef]] = {}
    for table in tables:
        tableName: str = f"{getenv(PREFIX)}_{table['Name']}"
        records: list[dict] = table["Records"]
        requestItems[tableName] = []
        for record in records:
            requestItem: WriteRequestTypeDef = {}
            item: dict = {}
            for column, value in record.items():
                item[column] = value

            requestItem["PutRequest"] = {"Item": item}
            requestItems[tableName].append(requestItem)

    dynamoDb.BatchWriteItem(requestItems)
