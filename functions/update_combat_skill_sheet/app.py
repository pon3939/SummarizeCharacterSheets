# -*- coding: utf-8 -*-


from typing import Any, Union

from aws_lambda_powertools.utilities.typing import LambdaContext
from gspread.utils import rowcol_to_a1
from gspread.worksheet import CellFormat
from my_modules.aws.my_dynamo_db_client import ConvertDynamoDBToJson
from my_modules.common_functions import initializePlayers
from my_modules.constants.spread_sheet import (
    ACTIVE_HEADER_TEXT,
    BATTLE_DANCER_HEADER_TEXT,
    DEFAULT_TEXT_FORMAT,
    HORIZONTAL_ALIGNMENT_CENTER,
    HORIZONTAL_ALIGNMENT_RIGHT,
    LEVEL_HEADER_TEXT,
    NO_HEADER_TEXT,
    PLAYER_CHARACTER_NAME_HEADER_TEXT,
    SUMMARY_HEADER_TEXT,
    TOTAL_COLUMN_INDEX,
    TOTAL_TEXT,
    TRUE_STRING,
)
from my_modules.constants.sword_world import COMBAT_SKILLS
from my_modules.spreadsheet.my_worksheet import (
    ConvertToVerticalHeaders,
    MyWorksheet,
)
from my_modules.sword_world.combat_skill import CombatSkill
from my_modules.sword_world.player import Player

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
        SUMMARY_HEADER_TEXT,
        BATTLE_DANCER_HEADER_TEXT,
    ]

    # レベルごとの戦闘特技
    for level in range(1, MAX_LEVEL + 1, 2):
        headers.append(f"{LEVEL_HEADER_TEXT}{level}")

    # 戦闘特技の取得状況(縦書き)
    headers.extend(ConvertToVerticalHeaders(COMBAT_SKILLS))
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

            summary: list[str] = []
            skillByLevel: list[str] = []
            battleDancerCombatSkill: str = ""
            if (
                character.IsBattleDancer()
                and character.CombatFeatsLv1bat is not None
            ):
                # バトルダンサー
                summary.append(f"1+ : {character.CombatFeatsLv1bat.SkillName}")
                battleDancerCombatSkill = character.CombatFeatsLv1bat.SkillName

            skillByLevel.append(battleDancerCombatSkill)
            level1CombatSkill: str = ""
            if character.CombatFeatsLv1 is not None:
                # Lv.1
                summary.append(f"1 : {character.CombatFeatsLv1.SkillName}")
                level1CombatSkill = character.CombatFeatsLv1.SkillName

            skillByLevel.append(level1CombatSkill)
            level3CombatSkill: str = ""
            if character.CombatFeatsLv3 is not None:
                # Lv.3
                summary.append(f"3 : {character.CombatFeatsLv3.SkillName}")
                level3CombatSkill = character.CombatFeatsLv3.SkillName

            skillByLevel.append(level3CombatSkill)
            level5CombatSkill: str = ""
            if character.CombatFeatsLv5 is not None:
                # Lv.5
                summary.append(f"5 : {character.CombatFeatsLv5.SkillName}")
                level5CombatSkill = character.CombatFeatsLv5.SkillName

            skillByLevel.append(level5CombatSkill)
            level7CombatSkill: str = ""
            if character.CombatFeatsLv7 is not None:
                # Lv.7
                summary.append(f"7 : {character.CombatFeatsLv7.SkillName}")
                level7CombatSkill = character.CombatFeatsLv7.SkillName

            skillByLevel.append(level7CombatSkill)
            level9CombatSkill: str = ""
            if character.CombatFeatsLv9 is not None:
                # Lv.9
                summary.append(f"9 : {character.CombatFeatsLv9.SkillName}")
                level9CombatSkill = character.CombatFeatsLv9.SkillName

            skillByLevel.append(level9CombatSkill)
            level11CombatSkill: str = ""
            if character.CombatFeatsLv11 is not None:
                # Lv.11
                summary.append(f"11 : {character.CombatFeatsLv11.SkillName}")
                level11CombatSkill = character.CombatFeatsLv11.SkillName

            skillByLevel.append(level11CombatSkill)
            level13CombatSkill: str = ""
            if character.CombatFeatsLv13 is not None:
                # Lv.13
                summary.append(f"13 : {character.CombatFeatsLv13.SkillName}")
                level13CombatSkill = character.CombatFeatsLv13.SkillName

            skillByLevel.append(level13CombatSkill)

            # 自動取得
            for autoCombatFeat in character.AutoCombatFeats:
                summary.append(autoCombatFeat.SkillName)

            # サマリー
            row.append("\n".join(summary))

            # レベルごとの取得戦闘特技
            row += skillByLevel

            # 戦闘特技の取得状況
            for combatSkillName in COMBAT_SKILLS:
                combatSkillStatus: str = ""
                combatSkill: Union[CombatSkill, None] = (
                    character.GetCombatSkillByName(combatSkillName)
                )
                if combatSkill is not None:
                    if combatSkill.detail == "":
                        # 習得している戦闘特技で、詳細がない場合は○を表示
                        combatSkillStatus = TRUE_STRING
                    else:
                        # 詳細(魔法拡大/数など)を表示
                        combatSkillStatus = combatSkill.detail

                row.append(combatSkillStatus)

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
            if not character.IsBattleDancer():
                formats.append(
                    {
                        "range": rowcol_to_a1(
                            rowIndex,
                            headers.index(BATTLE_DANCER_HEADER_TEXT) + 1,
                        ),
                        "format": {"textFormat": grayOutTextFormat},
                    }
                )

    # 合計行
    notTotalColumnCount: int = len(headers) - len(COMBAT_SKILLS)
    total: list = [None] * notTotalColumnCount
    total[TOTAL_COLUMN_INDEX] = TOTAL_TEXT
    for totalCombatSkill in COMBAT_SKILLS:
        total.append(
            sum(
                sum(
                    1
                    for y in x.Characters
                    if any(
                        z.IsSameCombatSkill(totalCombatSkill)
                        for z in y.GetCombatSkills()
                    )
                )
                for x in players
            )
        )

    updateData.append(total)

    # 書式設定
    # 縦書きヘッダー
    startA1 = rowcol_to_a1(1, notTotalColumnCount + 1)
    endA1 = rowcol_to_a1(1, len(headers))
    formats.append(
        {
            "range": f"{startA1}:{endA1}",
            "format": {"textRotation": {"vertical": True}},
        }
    )

    # アクティブ
    activeCountIndex: int = headers.index(ACTIVE_HEADER_TEXT)
    updateDataCount: int = len(updateData)
    startA1 = rowcol_to_a1(2, activeCountIndex + 1)
    endA1 = rowcol_to_a1(updateDataCount, activeCountIndex + 1)
    formats.append(
        {
            "range": f"{startA1}:{endA1}",
            "format": HORIZONTAL_ALIGNMENT_CENTER,
        }
    )

    # ○
    startA1 = rowcol_to_a1(2, notTotalColumnCount + 1)
    endA1 = rowcol_to_a1(updateDataCount - 1, len(headers))
    formats.append(
        {
            "range": f"{startA1}:{endA1}",
            "format": HORIZONTAL_ALIGNMENT_CENTER,
        }
    )

    # 合計行
    startA1 = rowcol_to_a1(updateDataCount, notTotalColumnCount + 1)
    endA1 = rowcol_to_a1(updateDataCount, len(headers))
    formats.append(
        {
            "range": f"{startA1}:{endA1}",
            "format": HORIZONTAL_ALIGNMENT_RIGHT,
        }
    )

    # 更新
    worksheet.Update(updateData, formats, True)
