# -*- coding: utf-8 -*-

from json import loads
from os import getenv
from typing import Any

from aws_lambda_powertools.utilities.typing import LambdaContext
from my_modules.common_functions import MakeYtsheetUrl
from my_modules.constants.env_keys import MY_BUCKET_NAME
from my_modules.my_dynamo_db_client import ConvertDynamoDBToJson
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
    players: list[dict[str, Any]] = ConvertDynamoDBToJson(event["Players"])
    getYtsheetData(seasonId, players)


def getYtsheetData(
    seasonId: int,
    players: list[dict[str, Any]],
):
    """ゆとシートデータを取得

    Args:
        seasonId: int: シーズンID
        players: list[dict[str, Any]]: レベルキャップ情報
    """

    s3: MyS3Client = MyS3Client()
    for player in players:
        for ytsheetId in player["ytsheet_ids"]:
            # ゆとシートにアクセス
            response: Response = get(f"{MakeYtsheetUrl(ytsheetId)}&mode=json")

            # ステータスコード200以外は例外発生
            response.raise_for_status()

            # JSON形式でなければエラー
            responseText: str = response.text
            loads(responseText)

            s3.PutPlayerCharacterObject(
                getenv(MY_BUCKET_NAME, ""), seasonId, ytsheetId, responseText
            )
