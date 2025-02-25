# -*- coding: utf-8 -*-

from json import loads
from os import getenv
from time import sleep

from aws_lambda_powertools.utilities.typing import LambdaContext
from my_modules.common_functions import MakeYtsheetUrl
from my_modules.constants.env_keys import (
    GET_YTSHEET_INTERVAL_SECONDS,
    MY_BUCKET_NAME,
    PLAYERS_TABLE_NAME,
)
from my_modules.my_dynamo_db_client import (
    ConvertDynamoDBToJson,
    ConvertJsonToDynamoDB,
    GetCurrentDateTimeForDynamoDB,
    MyDynamoDBClient,
)
from my_modules.my_s3_client import MyS3Client
from requests import Response, get

"""
ゆとシートデータを取得
"""


def lambda_handler(event: dict, context: LambdaContext):
    """

    メイン処理

    Args:
        event dict: イベント
        context LambdaContext: コンテキスト
    """

    seasonId: int = int(event["SeasonId"])
    player: dict = ConvertDynamoDBToJson(event["Player"])
    playerId: int = int(player["id"])
    characters: list[dict] = player["characters"]
    getYtsheetData(
        seasonId, playerId, list(map(lambda x: x["ytsheet_id"], characters))
    )


def getYtsheetData(
    seasonId: int,
    playerId: int,
    ytsheetIds: list[str],
):
    """ゆとシートデータを取得

    Args:
        seasonId: (int): シーズンID
        playerId: (int): プレイヤーID
        ytsheetIds: (list[str]): ゆとシートのID
    """

    s3: MyS3Client = MyS3Client()
    dynamoDb: MyDynamoDBClient = MyDynamoDBClient()
    updateCharacters: list[dict[str, str]] = []
    for ytsheetId in ytsheetIds:
        # ゆとシートにアクセス
        response: Response = get(f"{MakeYtsheetUrl(ytsheetId)}&mode=json")

        # ステータスコード200以外は例外発生
        response.raise_for_status()

        # JSON形式でなければエラー
        responseText: str = response.text
        loads(responseText)

        # S3に保存
        s3.PutPlayerCharacterObject(
            getenv(MY_BUCKET_NAME, ""), seasonId, ytsheetId, responseText
        )

        # 更新情報を追加
        updateCharacters.append(
            {
                "ytsheet_id": ytsheetId,
                "update_datetime": GetCurrentDateTimeForDynamoDB(),
            }
        )

        if ytsheetIds.index(ytsheetId) != len(ytsheetIds) - 1:
            # 連続アクセスを避けるために待機
            sleep(int(getenv(GET_YTSHEET_INTERVAL_SECONDS, "5")))

    # 最終更新日時を更新
    dynamoDb.UpdateItem(
        getenv(PLAYERS_TABLE_NAME, ""),
        ConvertJsonToDynamoDB({"season_id": seasonId, "id": playerId}),
        "SET characters = :characters",
        ConvertJsonToDynamoDB(
            {
                ":characters": updateCharacters,
            }
        ),
    )
