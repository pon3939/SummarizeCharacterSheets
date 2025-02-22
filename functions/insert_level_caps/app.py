# -*- coding: utf-8 -*-

from datetime import datetime
from os import getenv
from typing import Any
from zoneinfo import ZoneInfo

from aws_lambda_powertools.utilities.typing import LambdaContext
from my_modules.cloud_formation_response import CloudFormationResponse
from my_modules.common_functions import putCloudFormationResponse
from my_modules.constants.aws import (
    CLOUD_FORMATION_REQUEST_TYPE_CREATE,
    CLOUD_FORMATION_REQUEST_TYPE_MANUAL,
    CLOUD_FORMATION_STATUS_FAILED,
)
from my_modules.constants.env_keys import LEVEL_CAPS_TABLE_NAME
from my_modules.my_dynamo_db_client import (
    ConvertJsonToDynamoDB,
    DateTimeToStrForDynamoDB,
    MyDynamoDBClient,
)
from mypy_boto3_dynamodb.type_defs import WriteRequestTypeDef

"""
level_capsに登録
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
        seasons: list[dict[str, Any]] = inputData["Seasons"]
        insertLevelCaps(seasons)
        putCloudFormationResponse(cloudFormationResponse)
    except Exception as e:
        putCloudFormationResponse(
            cloudFormationResponse,
            CLOUD_FORMATION_STATUS_FAILED,
            str(e),
        )


def insertLevelCaps(
    seasons: list[dict[str, Any]],
):
    """レベルキャップを挿入する

    Args:
        seasons: list[dict[str, Any]]: レベルキャップ情報
    """

    dynamoDb: MyDynamoDBClient = MyDynamoDBClient()
    requestItems: list[WriteRequestTypeDef] = []
    for season in seasons:
        seasonId: int = int(season["SeasonId"])
        levelCaps: list[dict] = season["LevelCaps"]
        for levelCap in levelCaps:
            # JSTをGMTに変換
            startDatetimeInJst: datetime = datetime.strptime(
                levelCap["StartDatetime"], r"%Y/%m/%d"
            ).replace(tzinfo=ZoneInfo("Asia/Tokyo"))

            requestItem: WriteRequestTypeDef = {}
            requestItem["PutRequest"] = {"Item": {}}
            item: dict = {
                "season_id": seasonId,
                "start_datetime"
                "": DateTimeToStrForDynamoDB(startDatetimeInJst),
                "max_exp": int(levelCap["MaxExp"]),
                "minimum_exp": int(levelCap["MinimumExp"]),
            }
            requestItem["PutRequest"]["Item"] = ConvertJsonToDynamoDB(item)
            requestItems.append(requestItem)

    dynamoDb.BatchWriteItem({getenv(LEVEL_CAPS_TABLE_NAME, ""): requestItems})
