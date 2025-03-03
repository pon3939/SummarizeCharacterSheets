# -*- coding: utf-8 -*-


from typing import Any

from aws_lambda_powertools.utilities.typing import LambdaContext
from gspread.utils import rowcol_to_a1
from gspread.worksheet import CellFormat
from my_modules.aws.my_dynamo_db_client import ConvertDynamoDBToJson
from my_modules.common_functions import initializePlayers
from my_modules.constants.spread_sheet import (
    ACTIVE_HEADER_TEXT,
    DEFAULT_TEXT_FORMAT,
    HORIZONTAL_ALIGNMENT_CENTER,
    NO_HEADER_TEXT,
    PLAYER_CHARACTER_NAME_HEADER_TEXT,
    TRUE_STRING,
)
from my_modules.constants.sword_world import ABYSS_CURSES
from my_modules.spreadsheet.my_worksheet import MyWorksheet
from my_modules.sword_world.player import Player

"""
アビスカースシートを更新
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
    levelCap: dict[str, Any] = ConvertDynamoDBToJson(event["LevelCap"])
    playerJsons: list[dict[str, Any]] = ConvertDynamoDBToJson(event["Players"])

    players: list[Player] = initializePlayers(
        playerJsons, levelCap, int(environment["season_id"])
    )

    updateAbyssCurseSheet(
        environment["spreadsheet_id"], googleServiceAccount, players
    )


def updateAbyssCurseSheet(
    spreadsheetId: str,
    googleServiceAccount: dict[str, str],
    players: list[Player],
):
    """アビスカースシートを更新する

    Args:
        spreadsheetId: (str): スプレッドシートのID
        googleServiceAccount: (dict[str, str]): スプレッドシート認証情報
        players: (list[Player]): プレイヤー情報
    """

    worksheet: MyWorksheet = MyWorksheet(
        googleServiceAccount, spreadsheetId, "アビスカース"
    )
    updateData: list[list] = []

    # ヘッダー
    headers: list[str] = [
        NO_HEADER_TEXT,
        PLAYER_CHARACTER_NAME_HEADER_TEXT,
        ACTIVE_HEADER_TEXT,
        "数",
    ]
    for abyssCurse in ABYSS_CURSES:
        headers.append(abyssCurse)

    # ヘッダーを追加
    updateData.append(headers)

    formats: list[CellFormat] = []
    no: int = 0
    for player in players:
        for character in player.Characters:
            row: list = []

            # アビスカースの情報を取得
            receivedCurses: list[str] = []
            receivedCursesString: str = ""
            for abyssCurse in ABYSS_CURSES:
                receivedCurse: str = ""
                if abyssCurse in character.AbyssCurses:
                    receivedCurse = TRUE_STRING
                    receivedCursesString += abyssCurse

                receivedCurses.append(receivedCurse)

            # No.
            no += 1
            row.append(no)

            # PC
            row.append(receivedCursesString + character.Name)

            # 参加傾向
            row.append(character.ActiveStatus.GetStrForSpreadsheet())

            # 数
            row.append(len(character.AbyssCurses))

            # 各アビスカース
            row.extend(receivedCurses)

            updateData.append(row)

            # PC列のハイパーリンク
            pcTextFormat: dict = DEFAULT_TEXT_FORMAT.copy()
            pcTextFormat["link"] = {"uri": character.GetYtsheetUrl()}
            formats.append(
                {
                    "range": rowcol_to_a1(
                        no + 1,
                        headers.index(PLAYER_CHARACTER_NAME_HEADER_TEXT) + 1,
                    ),
                    "format": {
                        "wrapStrategy": "WRAP",
                        "textFormat": pcTextFormat,
                    },
                }
            )

    # 合計行
    notTotalColumnCount: int = len(headers) - len(ABYSS_CURSES) - 1
    total: list = [None] * notTotalColumnCount

    # アビスカースの数
    total.append(
        sum(sum(len(y.AbyssCurses) for y in x.Characters) for x in players)
    )

    # 各カースの数
    total += list(
        map(
            lambda x: sum(
                sum(1 for z in y.Characters if x in z.AbyssCurses)
                for y in players
            ),
            ABYSS_CURSES,
        )
    )
    updateData.append(total)

    # 書式設定
    # アクティブ
    updateDataCount: int = len(updateData)
    activeCountIndex: int = headers.index(ACTIVE_HEADER_TEXT)
    startA1: str = rowcol_to_a1(2, activeCountIndex + 1)
    endA1: str = rowcol_to_a1(updateDataCount - 1, activeCountIndex + 1)
    formats.append(
        {
            "range": f"{startA1}:{endA1}",
            "format": HORIZONTAL_ALIGNMENT_CENTER,
        }
    )

    # ○
    startA1 = rowcol_to_a1(2, len(headers) - len(ABYSS_CURSES) + 1)
    endA1 = rowcol_to_a1(updateDataCount - 1, len(headers))
    formats.append(
        {
            "range": f"{startA1}:{endA1}",
            "format": HORIZONTAL_ALIGNMENT_CENTER,
        }
    )

    # 更新
    worksheet.Update(updateData, formats, True)
