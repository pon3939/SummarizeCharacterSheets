# -*- coding: utf-8 -*-


from typing import Any

from aws_lambda_powertools.utilities.typing import LambdaContext
from gspread.utils import rowcol_to_a1
from gspread.worksheet import CellFormat
from my_modules.common_functions import initializePlayers
from my_modules.constants.spread_sheet import (
    ACTIVE_HEADER_TEXT,
    DEFAULT_TEXT_FORMAT,
    HORIZONTAL_ALIGNMENT_CENTER,
    NO_HEADER_TEXT,
    PLAYER_CHARACTER_NAME_HEADER_TEXT,
    TRUE_STRING,
)
from my_modules.constants.sword_world import STYLES
from my_modules.my_dynamo_db_client import ConvertDynamoDBToJson
from my_modules.my_worksheet import ConvertToVerticalHeaders, MyWorksheet
from my_modules.player import Player

"""
名誉点・流派シートを更新
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

    updateHonorSheet(
        environment["spreadsheet_id"], googleServiceAccount, players
    )


def updateHonorSheet(
    spreadsheetId: str,
    googleServiceAccount: dict[str, str],
    players: list[Player],
):
    """名誉点・流派シートを更新する

    Args:
        spreadsheetId: (str): スプレッドシートのID
        googleServiceAccount: (dict[str, str]): スプレッドシート認証情報
        players: (list[Player]): プレイヤー情報
    """

    worksheet: MyWorksheet = MyWorksheet(
        googleServiceAccount, spreadsheetId, "名誉点・流派"
    )
    updateData: list[list] = []

    # ヘッダー
    headers: list[str] = [
        NO_HEADER_TEXT,
        PLAYER_CHARACTER_NAME_HEADER_TEXT,
        ACTIVE_HEADER_TEXT,
        "冒険者ランク",
        "累計名誉点",
        "入門数",
    ]
    verticalHeaders: list[str] = ["2.0流派"]
    verticalHeaders.extend(list(map(lambda x: x.Name, STYLES)))

    # 縦書きに変換
    headers.extend(ConvertToVerticalHeaders(verticalHeaders))
    updateData.append(headers)

    formats: list[CellFormat] = []
    no: int = 0
    for player in players:
        for character in player.Characters:
            row: list = []

            # 流派の情報を取得
            is20: bool = False
            learnedStyles: list[str] = []
            for style in STYLES:
                learnedStyle: str = ""
                if style in character.Styles:
                    # 該当する流派に入門している
                    learnedStyle = TRUE_STRING
                    if style.Is20:
                        is20 = True

                learnedStyles.append(learnedStyle)

            # No.
            no += 1
            row.append(no)

            # PC
            row.append(character.Name)

            # 参加傾向
            row.append(character.ActiveStatus.GetStrForSpreadsheet())

            # 冒険者ランク
            row.append(character.AdventurerRank)

            # 累計名誉点
            row.append(character.TotalHonor)

            # 加入数
            row.append(len(character.Styles))

            # 2.0流派
            row.append(TRUE_STRING if is20 else "")

            # 各流派
            row += learnedStyles

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
                    "format": {"textFormat": pcTextFormat},
                }
            )

    # 合計行
    notTotalColumnCount: int = len(headers) - len(STYLES) - 1
    total: list = [None] * notTotalColumnCount

    # 2.0流派所持
    total.append(
        sum(
            sum(1 for y in x.Characters if any(z.Is20 for z in y.Styles))
            for x in players
        )
    )

    # 各流派
    total += list(
        map(
            lambda x: sum(
                sum(1 for z in y.Characters if x in z.Styles) for y in players
            ),
            STYLES,
        )
    )
    updateData.append(total)

    # 書式設定
    # 流派のヘッダー
    startA1: str = rowcol_to_a1(1, notTotalColumnCount + 1)
    endA1: str = rowcol_to_a1(1, len(headers))
    formats.append(
        {
            "range": f"{startA1}:{endA1}",
            "format": {"textRotation": {"vertical": True}},
        }
    )

    # アクティブ
    updateDataCount: int = len(updateData)
    activeCountIndex: int = headers.index(ACTIVE_HEADER_TEXT)
    startA1 = rowcol_to_a1(2, activeCountIndex + 1)
    endA1: str = rowcol_to_a1(updateDataCount - 1, activeCountIndex + 1)
    formats.append(
        {
            "range": f"{startA1}:{endA1}",
            "format": HORIZONTAL_ALIGNMENT_CENTER,
        }
    )

    # ○
    startA1 = rowcol_to_a1(2, notTotalColumnCount + 1)
    endA1: str = rowcol_to_a1(updateDataCount - 1, len(headers))
    formats.append(
        {
            "range": f"{startA1}:{endA1}",
            "format": HORIZONTAL_ALIGNMENT_CENTER,
        }
    )

    # 更新
    worksheet.Update(updateData, formats, True)
