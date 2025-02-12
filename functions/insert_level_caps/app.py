# -*- coding: utf-8 -*-

from datetime import datetime
from os import getenv
from typing import Any
from zoneinfo import ZoneInfo

from aws_lambda_powertools.utilities.typing import LambdaContext
from my_modules.cloud_formation_response import CloudFormationResponse
from my_modules.common_functions import (
    ConvertJsonToDynamoDB,
    DateTimeToStrForDynamoDB,
    InitDb,
    putCloudFormationResponse,
)
from my_modules.constants.aws import (
    CLOUD_FORMATION_REQUEST_TYPE_CREATE,
    CLOUD_FORMATION_REQUEST_TYPE_MANUAL,
    CLOUD_FORMATION_STATUS_FAILED,
)
from my_modules.constants.env_keys import LEVEL_CAPS_TABLE_NAME
from mypy_boto3_dynamodb.client import DynamoDBClient
from mypy_boto3_dynamodb.type_defs import (
    BatchWriteItemOutputTypeDef,
    WriteRequestTypeDef,
)

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
        if (
            cloudFormationResponse.RequestType
            != CLOUD_FORMATION_REQUEST_TYPE_CREATE
            and cloudFormationResponse.RequestType
            != CLOUD_FORMATION_REQUEST_TYPE_MANUAL
        ):
            # 初回デプロイ時以外はスキップする
            putCloudFormationResponse(cloudFormationResponse)
            return

        inputData: dict[str, Any] = event["ResourceProperties"]["InputData"]
        seasonId: int = int(inputData["SeasonId"])
        levelCaps: list[dict[str, str]] = inputData["LevelCaps"]
        insertLevelCaps(levelCaps, seasonId)
        putCloudFormationResponse(cloudFormationResponse)
    except Exception as e:
        putCloudFormationResponse(
            cloudFormationResponse,
            CLOUD_FORMATION_STATUS_FAILED,
            str(e),
        )


def insertLevelCaps(
    levelCaps: "list[dict[str, str]]",
    seasonId: int,
):
    """レベルキャップを挿入する

    Args:
        levelCaps: list[dict[str, str]]: レベルキャップ
        seasonId: int: シーズンID
    """

    dynamoDb: DynamoDBClient = InitDb()

    requestItems: list[WriteRequestTypeDef] = []
    for levelCap in levelCaps:
        # JSTをGMTに変換
        startDatetimeInJst: datetime = datetime.strptime(
            levelCap["startDatetime"], r"%Y/%m/%d"
        ).replace(tzinfo=ZoneInfo("Asia/Tokyo"))

        requestItem: WriteRequestTypeDef = {}
        requestItem["PutRequest"] = {"Item": {}}
        item: dict = {
            "season_id": seasonId,
            "start_datetime" "": DateTimeToStrForDynamoDB(startDatetimeInJst),
            "max_exp": levelCap["maxExp"],
            "minimum_exp": levelCap["minimumExp"],
        }
        requestItem["PutRequest"]["Item"] = ConvertJsonToDynamoDB(item)
        requestItems.append(requestItem)

    response: BatchWriteItemOutputTypeDef = dynamoDb.batch_write_item(
        RequestItems={getenv(LEVEL_CAPS_TABLE_NAME, ""): requestItems}
    )

    while response["UnprocessedItems"] != {}:
        response = dynamoDb.batch_write_item(
            RequestItems=response["UnprocessedItems"]
        )
