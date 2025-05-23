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
    HORIZONTAL_ALIGNMENT_RIGHT,
    NO_HEADER_TEXT,
    PLAYER_CHARACTER_NAME_HEADER_TEXT,
    TOTAL_COLUMN_INDEX,
    TOTAL_TEXT,
)
from my_modules.constants.sword_world import OFFICIAL_GENERAL_SKILLS
from my_modules.spreadsheet.my_worksheet import (
    ConvertToVerticalHeaders,
    MyWorksheet,
)
from my_modules.sword_world.general_skill import GeneralSkill
from my_modules.sword_world.player import Player

"""
一般技能シートを更新
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

    updateGeneralSkillSheet(
        environment["spreadsheet_id"], googleServiceAccount, players
    )


def updateGeneralSkillSheet(
    spreadsheetId: str,
    googleServiceAccount: dict[str, str],
    players: list[Player],
):
    """一般技能シートを更新する

    Args:
        spreadsheetId: (str): スプレッドシートのID
        googleServiceAccount: (dict[str, str]): スプレッドシート認証情報
        players: (list[Player]): プレイヤー情報
    """

    worksheet: MyWorksheet = MyWorksheet(
        googleServiceAccount, spreadsheetId, "一般技能"
    )
    updateData: list[list] = []

    # ヘッダー
    headers: list[str] = [
        NO_HEADER_TEXT,
        PLAYER_CHARACTER_NAME_HEADER_TEXT,
        ACTIVE_HEADER_TEXT,
        "公式技能",
        "オリジナル技能",
    ]

    # 縦書きヘッダー
    headers.extend(
        ConvertToVerticalHeaders(
            list(
                map(
                    lambda x: x.getFormattedSkill(),
                    OFFICIAL_GENERAL_SKILLS,
                )
            )
        )
    )
    updateData.append(headers)

    formats: list[CellFormat] = []
    no: int = 0
    for player in players:
        for character in player.Characters:
            # 公式一般技能のレベル取得
            officialGeneralSkills: list[GeneralSkill] = list(
                filter(
                    lambda x: not x.IsOriginal,
                    character.GeneralSkills,
                )
            )

            row: list = []

            # No.
            no += 1
            row.append(no)

            # PC
            row.append(character.Name)

            # 参加傾向
            row.append(character.ActiveStatus.GetStrForSpreadsheet())

            # 公式技能
            row.append(
                "\n".join(
                    [
                        x.getFormattedSkillAndLevel()
                        for x in officialGeneralSkills
                    ]
                )
            )

            # オリジナル技能
            row.append(
                "\n".join(
                    [
                        x.getFormattedSkillAndLevel()
                        for x in list(
                            filter(
                                lambda x: x.IsOriginal,
                                character.GeneralSkills,
                            )
                        )
                    ]
                )
            )

            # 公式技能のレベル
            for officialGeneralSkill in OFFICIAL_GENERAL_SKILLS:
                row.append(
                    next(
                        (
                            x.Level
                            for x in officialGeneralSkills
                            if x.compareWithGeneralSkill(officialGeneralSkill)
                        ),
                        None,
                    )
                )

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
    notTotalColumnCount: int = len(headers) - len(OFFICIAL_GENERAL_SKILLS)
    total: list = [None] * notTotalColumnCount
    total[TOTAL_COLUMN_INDEX] = TOTAL_TEXT
    for officialGeneralSkill in OFFICIAL_GENERAL_SKILLS:
        total.append(
            sum(
                sum(
                    1
                    for y in x.Characters
                    if any(
                        z.compareWithGeneralSkill(officialGeneralSkill)
                        for z in y.GeneralSkills
                    )
                )
                for x in players
            )
        )

    updateData.append(total)

    # 書式設定
    # 縦書きヘッダー
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
    endA1 = rowcol_to_a1(updateDataCount - 1, activeCountIndex + 1)
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
