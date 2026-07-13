# -*- coding: utf-8 -*-


from typing import Any

from aws_lambda_powertools.utilities.typing import LambdaContext
from gspread.utils import rowcol_to_a1
from gspread.worksheet import CellFormat
from my_modules.aws.my_dynamo_db_client import ConvertDynamoDBToJson
from my_modules.common_functions import initializePlayers
from my_modules.constants.spread_sheet import (
    DEFAULT_TEXT_FORMAT,
    NO_HEADER_TEXT,
    PLAYER_CHARACTER_NAME_HEADER_TEXT,
)
from my_modules.spreadsheet.my_worksheet import MyWorksheet
from my_modules.sword_world.player import Player

"""
テンプレートシートを更新
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

    updateTemplateSheet(
        environment["spreadsheet_id"], googleServiceAccount, players
    )


def updateTemplateSheet(
    spreadsheetId: str,
    googleServiceAccount: dict[str, str],
    players: list[Player],
):
    """テンプレートシートを更新する

    Args:
        spreadsheetId: (str): スプレッドシートのID
        googleServiceAccount: (dict[str, str]): スプレッドシート認証情報
        players: (list[Player]): プレイヤー情報
    """

    worksheet: MyWorksheet = MyWorksheet(
        googleServiceAccount, spreadsheetId, "テンプレート"
    )
    updateData: list[list] = []

    # ヘッダー
    header: list[str] = [
        NO_HEADER_TEXT,
        PLAYER_CHARACTER_NAME_HEADER_TEXT,
        "参加申請",
    ]
    updateData.append(header)

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

            # 参加申請
            character.CombatAbilities.sort(
                key=lambda combatAbility: combatAbility.Level, reverse=True
            )
            combatAbilityStr: str = "、".join(
                [
                    f"{combatAbility.SkillName}{combatAbility.Level}"
                    for combatAbility in character.CombatAbilities
                ]
            )
            url: str = character.GetYtsheetUrl()
            row.append(
                "\n".join(
                    [
                        f"PC名【{character.Name}】",
                        f"技能【{combatAbilityStr}】",
                        f"キャラ紙URL【 {url} 】",
                        "所持サプリ【ET,ML,MA,BM,CBB,OPB,KF,CO,ES,VC,DL,"
                        "GR,DA,BL,AR,RL,DD,AB,BR,BS,US,TS,IC,TC,BN,"
                        "BIG,BIG2,MF】",
                    ]
                )
            )

            updateData.append(row)

            # PC列のハイパーリンク
            pcTextFormat: dict = DEFAULT_TEXT_FORMAT.copy()
            pcTextFormat["link"] = {"uri": url}
            formats.append(
                {
                    "range": rowcol_to_a1(
                        no + 1,
                        header.index(PLAYER_CHARACTER_NAME_HEADER_TEXT) + 1,
                    ),
                    "format": {"textFormat": pcTextFormat},
                }
            )

    # 更新
    worksheet.Update(updateData, formats, False)
