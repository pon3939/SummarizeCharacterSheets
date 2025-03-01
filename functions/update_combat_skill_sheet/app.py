# -*- coding: utf-8 -*-


from typing import Any, Union

from aws_lambda_powertools.utilities.typing import LambdaContext
from gspread.utils import rowcol_to_a1
from gspread.worksheet import CellFormat
from my_modules.common_functions import initializePlayers
from my_modules.constants.spread_sheet import (
    ACTIVE_HEADER_TEXT,
    BATTLE_DANCER_HEADER_TEXT,
    DEFAULT_TEXT_FORMAT,
    HORIZONTAL_ALIGNMENT_CENTER,
    LEVEL_HEADER_TEXT,
    NO_HEADER_TEXT,
    PLAYER_CHARACTER_NAME_HEADER_TEXT,
)
from my_modules.constants.sword_world import BATTLE_DANCER_LEVEL_KEY
from my_modules.my_dynamo_db_client import ConvertDynamoDBToJson
from my_modules.my_worksheet import MyWorksheet
from my_modules.player import Player

"""
戦闘特技シートを更新
"""

MAX_LEVEL: int = 13


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

    updateCombatSkillSheet(
        environment["spreadsheet_id"], googleServiceAccount, players
    )


def updateCombatSkillSheet(
    spreadsheetId: str,
    googleServiceAccount: dict[str, str],
    players: list[Player],
):
    """戦闘特技シートを更新する

    Args:
        spreadsheetId: (str): スプレッドシートのID
        googleServiceAccount: (dict[str, str]): スプレッドシート認証情報
        players: (list[Player]): プレイヤー情報
    """

    worksheet: MyWorksheet = MyWorksheet(
        googleServiceAccount, spreadsheetId, "戦闘特技"
    )
    updateData: list[list] = []

    # ヘッダー
    headers: list[str] = [
        NO_HEADER_TEXT,
        PLAYER_CHARACTER_NAME_HEADER_TEXT,
        ACTIVE_HEADER_TEXT,
        BATTLE_DANCER_HEADER_TEXT,
    ]
    for level in range(1, MAX_LEVEL + 1, 2):
        headers.append(f"{LEVEL_HEADER_TEXT}{level}")

    headers.append("自動取得")
    updateData.append(headers)

    formats: list[CellFormat] = []
    no: int = 0
    for player in players:
        for character in player.Characters:
            row: list = []

            # No.
            no += 1
            row.append(no)

            # PC
            row.append(character.Name)

            # 参加傾向
            row.append(character.ActiveStatus.GetStrForSpreadsheet())

            # バトルダンサー
            row.append(character.CombatFeatsLv1bat)

            # Lv.1
            row.append(character.CombatFeatsLv1)

            # Lv.3
            row.append(character.CombatFeatsLv3)

            # Lv.5
            row.append(character.CombatFeatsLv5)

            # Lv.7
            row.append(character.CombatFeatsLv7)

            # Lv.9
            row.append(character.CombatFeatsLv9)

            # Lv.11
            row.append(character.CombatFeatsLv11)

            # Lv.13
            row.append(character.CombatFeatsLv13)

            # 自動取得
            for autoCombatFeat in character.AutoCombatFeats:
                row.append(autoCombatFeat)

            updateData.append(row)

            # 書式設定
            rowIndex: int = no + 1

            # PC列のハイパーリンク
            pcTextFormat: dict = DEFAULT_TEXT_FORMAT.copy()
            pcTextFormat["link"] = {"uri": character.GetYtsheetUrl()}
            formats.append(
                {
                    "range": rowcol_to_a1(
                        rowIndex,
                        headers.index(PLAYER_CHARACTER_NAME_HEADER_TEXT) + 1,
                    ),
                    "format": {"textFormat": pcTextFormat},
                }
            )

            # 習得レベルに満たないものはグレーで表示
            grayOutTextFormat: dict = DEFAULT_TEXT_FORMAT.copy()
            grayOutTextFormat["foregroundColorStyle"] = {
                "rgbColor": {"red": 0.4, "green": 0.4, "blue": 0.4}
            }

            grayOutStartIndex: Union[int, None] = None
            for level in range(3, MAX_LEVEL + 1, 2):
                if character.Level < level:
                    grayOutStartIndex = (
                        headers.index(f"{LEVEL_HEADER_TEXT}{level}") + 1
                    )
                    break

            if grayOutStartIndex is not None:
                startA1: str = rowcol_to_a1(rowIndex, grayOutStartIndex)
                endA1: str = rowcol_to_a1(
                    rowIndex,
                    headers.index(f"{LEVEL_HEADER_TEXT}{MAX_LEVEL}") + 1,
                )
                formats.append(
                    {
                        "range": f"{startA1}:{endA1}",
                        "format": {"textFormat": grayOutTextFormat},
                    }
                )

            # バトルダンサー未習得もグレーで表示
            if character.Skills.get(BATTLE_DANCER_LEVEL_KEY, 0) == 0:
                formats.append(
                    {
                        "range": rowcol_to_a1(
                            rowIndex,
                            headers.index(BATTLE_DANCER_HEADER_TEXT) + 1,
                        ),
                        "format": {"textFormat": grayOutTextFormat},
                    }
                )

    # 書式設定
    # アクティブ
    activeCountIndex: int = headers.index(ACTIVE_HEADER_TEXT)
    startA1 = rowcol_to_a1(2, activeCountIndex + 1)
    endA1 = rowcol_to_a1(len(updateData), activeCountIndex + 1)
    formats.append(
        {
            "range": f"{startA1}:{endA1}",
            "format": HORIZONTAL_ALIGNMENT_CENTER,
        }
    )

    # 更新
    worksheet.Update(updateData, formats, False)
