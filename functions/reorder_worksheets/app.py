# -*- coding: utf-8 -*-


from typing import Any

from aws_lambda_powertools.utilities.typing import LambdaContext
from my_modules.aws.my_dynamo_db_client import ConvertDynamoDBToJson
from my_modules.spreadsheet.my_spreadsheet import MySpreadsheet

"""
ワークシートを並べ変える
"""


def lambda_handler(event: dict, context: LambdaContext):
    """

    メイン処理

    Args:
        event dict: イベント
        context LambdaContext: コンテキスト
    """
    environment: dict[str, Any] = ConvertDynamoDBToJson(event["Environment"])
    googleServiceAccount: dict[str, str] = ConvertDynamoDBToJson(
        event["GoogleServiceAccount"]
    )

    reorderWorksheets(environment["spreadsheet_id"], googleServiceAccount)


def reorderWorksheets(
    spreadsheetId: str,
    googleServiceAccount: dict[str, str],
):
    """ワークシートを並べ変える

    Args:
        spreadsheetId: (str): スプレッドシートのID
        googleServiceAccount: (dict[str, str]): スプレッドシート認証情報
    """

    spreadsheet: MySpreadsheet = MySpreadsheet(
        googleServiceAccount, spreadsheetId
    )
    spreadsheet.reorderWorksheets(
        [
            "使い方",
            "グラフ",
            "PL",
            "基本",
            "技能",
            "能力値",
            "戦闘特技",
            "名誉点・流派",
            "アビスカース",
            "一般技能",
        ]
    )
