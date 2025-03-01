# -*- coding: utf-8 -*-


from typing import Any

from aws_lambda_powertools.utilities.typing import LambdaContext
from gspread.utils import rowcol_to_a1
from gspread.worksheet import CellFormat
from my_modules.common_functions import initializePlayers
from my_modules.constants.spread_sheet import (
    ACTIVE_HEADER_TEXT,
    DEFAULT_TEXT_FORMAT,
    EXP_HEADER_TEXT,
    FAITH_HEADER_TEXT,
    HORIZONTAL_ALIGNMENT_CENTER_FORMAT,
    LEVEL_HEADER_TEXT,
    NO_HEADER_TEXT,
    PLAYER_CHARACTER_NAME_HEADER_TEXT,
)
from my_modules.constants.sword_world import SKILLS
from my_modules.exp_status import ExpStatus
from my_modules.my_dynamo_db_client import ConvertDynamoDBToJson
from my_modules.my_worksheet import ConvertToVerticalHeaders, MyWorksheet
from my_modules.player import Player

"""
技能シートを更新
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

    updateAbilitySheet(
        environment["spreadsheet_id"], googleServiceAccount, players
    )


def updateAbilitySheet(
    spreadsheetId: str,
    googleServiceAccount: dict[str, str],
    players: list[Player],
):
    """技能シートを更新する

    Args:
        spreadsheetId: (str): スプレッドシートのID
        googleServiceAccount: (dict[str, str]): スプレッドシート認証情報
        players: (list[Player]): プレイヤー情報
    """

    worksheet: MyWorksheet = MyWorksheet(
        googleServiceAccount, spreadsheetId, "技能"
    )
    updateData: list[list] = []

    # ヘッダー
    headers: list[str] = [
        NO_HEADER_TEXT,
        PLAYER_CHARACTER_NAME_HEADER_TEXT,
        ACTIVE_HEADER_TEXT,
        FAITH_HEADER_TEXT,
        LEVEL_HEADER_TEXT,
        EXP_HEADER_TEXT,
    ]

    # ヘッダーを縦書き用に変換
    headers.extend(
        ConvertToVerticalHeaders(
            ConvertToVerticalHeaders(list(map(lambda x: x, SKILLS.values())))
        )
    )
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

            # 信仰
            row.append(character.Faith)

            # Lv
            row.append(character.Level)

            # 経験点
            row.append(character.Exp)

            # 技能レベル
            for skill in SKILLS:
                row.append(character.Skills.get(skill, ""))

            updateData.append(row)

            # 書式設定
            rowIndex: int = no + 1

            # 経験点の文字色
            expTextFormat: dict = DEFAULT_TEXT_FORMAT.copy()
            if character.ActiveStatus == ExpStatus.MAX:
                expTextFormat["foregroundColorStyle"] = {
                    "rgbColor": {"red": 1, "green": 0, "blue": 0}
                }
            elif character.ActiveStatus == ExpStatus.INACTIVE:
                expTextFormat["foregroundColorStyle"] = {
                    "rgbColor": {"red": 0, "green": 0, "blue": 1}
                }

            if character.ActiveStatus in [ExpStatus.MAX, ExpStatus.INACTIVE]:
                formats.append(
                    {
                        "range": rowcol_to_a1(
                            rowIndex, headers.index(EXP_HEADER_TEXT) + 1
                        ),
                        "format": {"textFormat": expTextFormat},
                    }
                )

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

    # 合計行
    notSkillColumnCount: int = len(headers) - len(SKILLS)
    total: list = [None] * notSkillColumnCount
    total += list(
        map(
            lambda x: sum(
                sum(1 for z in y.Characters if z.GetSkillLevel(x) > 0)
                for y in players
            ),
            SKILLS.keys(),
        )
    )
    updateData.append(total)

    # 書式設定
    # 技能レベルのヘッダー
    startA1: str = rowcol_to_a1(1, notSkillColumnCount + 1)
    endA1: str = rowcol_to_a1(1, len(headers))
    formats.append(
        {
            "range": f"{startA1}:{endA1}",
            "format": {"textRotation": {"vertical": True}},
        }
    )

    # アクティブ
    activeCountIndex: int = headers.index(ACTIVE_HEADER_TEXT)
    startA1 = rowcol_to_a1(2, activeCountIndex + 1)
    endA1 = rowcol_to_a1(len(updateData) - 1, activeCountIndex + 1)
    formats.append(
        {
            "range": f"{startA1}:{endA1}",
            "format": HORIZONTAL_ALIGNMENT_CENTER_FORMAT,
        }
    )

    # 更新
    worksheet.Update(updateData, formats, True)
