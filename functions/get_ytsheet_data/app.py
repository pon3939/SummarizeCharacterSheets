# -*- coding: utf-8 -*-

from os import getenv
from time import sleep
from typing import Any

from aws_lambda_powertools.utilities.typing import LambdaContext
from my_modules.common_functions import MakeYtsheetUrl
from my_modules.constants.env_keys import GET_YTSHEET_INTERVAL_SECONDS
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
    player: dict = ConvertDynamoDBToJson(event["Player"])
    characters: list[dict] = player["characters"]
    getYtsheetData(seasonId, characters)


def getYtsheetData(
    seasonId: int,
    characters: list[dict[str, Any]],
):
    """ゆとシートデータを取得

    Args:
        seasonId: (int): シーズンID
        characters: (list[dict[str, Any]]): キャラクター情報
    """

    s3: MyS3Client = MyS3Client()
    isAccessedYtsheet: bool = False
    for character in characters:
        if character["is_deleted"]:
            # 削除済みの場合はスキップ
            continue

        if isAccessedYtsheet:
            # 連続アクセスを避けるために待機
            sleep(int(getenv(GET_YTSHEET_INTERVAL_SECONDS, "5")))

        isAccessedYtsheet = True

        # ゆとシートにアクセス
        ytsheetId: str = character["ytsheet_id"]
        response: Response = get(f"{MakeYtsheetUrl(ytsheetId)}&mode=json")

        # ステータスコード200以外は例外発生
        response.raise_for_status()

        # JSON形式でなければエラー
        if response.headers["Content-Type"] != "application/json":
            raise Exception(
                f"ytsheet_id={character['ytsheet_id']} : "
                "Content-Type が application/json ではありません"
            )

        # S3に保存
        s3.PutPlayerCharacterObject(seasonId, ytsheetId, response.text)
