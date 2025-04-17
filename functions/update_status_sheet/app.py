# -*- coding: utf-8 -*-


from typing import Any, Union

from aws_lambda_powertools.utilities.typing import LambdaContext
from gspread.utils import rowcol_to_a1
from gspread.worksheet import CellFormat
from my_modules.aws.my_dynamo_db_client import ConvertDynamoDBToJson
from my_modules.common_functions import initializePlayers
from my_modules.constants.spread_sheet import (
    ACTIVE_HEADER_TEXT,
    ADVENTURER_BIRTH_HEADER_TEXT,
    DEFAULT_TEXT_FORMAT,
    DICE_AVERAGE_HEADER_TEXT,
    HORIZONTAL_ALIGNMENT_CENTER,
    NO_HEADER_TEXT,
    NUMBER_FORMAT_TYPE_REAL_NUMBER,
    PLAYER_CHARACTER_NAME_HEADER_TEXT,
    RACE_HEADER_TEXT,
    TRUE_STRING,
)
from my_modules.constants.sword_world import RACES
from my_modules.spreadsheet.my_worksheet import MyWorksheet
from my_modules.sword_world.player import Player
from my_modules.sword_world.race import Race
from my_modules.sword_world.races_base_status import RacesBaseStatus

"""
能力値シートを更新
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

    updateStatusSheet(
        environment["spreadsheet_id"], googleServiceAccount, players
    )


def updateStatusSheet(
    spreadsheetId: str,
    googleServiceAccount: dict[str, str],
    players: list[Player],
):
    """能力値シートを更新する

    Args:
        spreadsheetId: (str): スプレッドシートのID
        googleServiceAccount: (dict[str, str]): スプレッドシート認証情報
        players: (list[Player]): プレイヤー情報
    """

    worksheet: MyWorksheet = MyWorksheet(
        googleServiceAccount, spreadsheetId, "能力値"
    )
    updateData: list[list] = []

    # ヘッダー
    headers: list[str] = [
        NO_HEADER_TEXT,
        PLAYER_CHARACTER_NAME_HEADER_TEXT,
        ACTIVE_HEADER_TEXT,
        RACE_HEADER_TEXT,
        "器用",
        "敏捷",
        "筋力",
        "生命",
        "知力",
        "精神",
        "成長",
        "HP",
        "MP",
        "生命抵抗",
        "精神抵抗",
        "魔物知識",
        "先制",
        DICE_AVERAGE_HEADER_TEXT,
        "割り振り\nポイント",
        ADVENTURER_BIRTH_HEADER_TEXT,
    ]
    updateData.append(headers)

    diceAverageIndex: int = headers.index(DICE_AVERAGE_HEADER_TEXT) + 1
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

            # 種族
            row.append(character.GetMinorRace())

            # 器用
            row.append(character.Dexterity.GetTotalStatus())

            # 敏捷
            row.append(character.Agility.GetTotalStatus())

            # 筋力
            row.append(character.Strength.GetTotalStatus())

            # 生命
            row.append(character.Vitality.GetTotalStatus())

            # 知力
            row.append(character.Intelligence.GetTotalStatus())

            # 精神
            row.append(character.Mental.GetTotalStatus())

            # 成長
            row.append(character.GrowthTimes)

            # HP
            row.append(character.Hp)

            # MP
            row.append(character.Mp)

            # 生命抵抗力
            row.append(character.LifeResistance)

            # 精神抵抗力
            row.append(character.SpiritResistance)

            # 魔物知識
            row.append(character.MonsterKnowledge)

            # 先制力
            row.append(character.Initiative)

            diceAverage: float = 0.0
            allocationsPoint: int = 0
            race: Union[Race, None] = next(
                (x for x in RACES if x.Name == character.GetMajorRace()),
                None,
            )
            if race is not None:
                # 種族指定時のみ値を設定
                totalBaseStatus: RacesBaseStatus = race.GetTotalBaseStatus()
                diceAverage = (
                    character.Dexterity.Base
                    + character.Agility.Base
                    + character.Strength.Base
                    + character.Vitality.Base
                    + character.Intelligence.Base
                    + character.Mental.Base
                    - totalBaseStatus.FixedValue
                ) / totalBaseStatus.DiceCount
                allocationsPoint = race.GetAllocationsPoint(character)

            # ダイス平均
            row.append(diceAverage)

            # 割り振りポイント
            row.append(allocationsPoint)

            # 冒険者生まれ
            if character.Birth == "冒険者":
                row.append(TRUE_STRING)

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

            # ダイス平均4.5を超える場合は赤文字
            if diceAverage > 4.5:
                diceAverageTextFormat: dict = DEFAULT_TEXT_FORMAT.copy()
                diceAverageTextFormat["foregroundColorStyle"] = {
                    "rgbColor": {"red": 1, "green": 0, "blue": 0}
                }
                formats.append(
                    {
                        "range": rowcol_to_a1(rowIndex, diceAverageIndex),
                        "format": {"textFormat": diceAverageTextFormat},
                    }
                )

    # 書式設定
    # アクティブ
    updateDataCount: int = len(updateData)
    activeCountIndex: int = headers.index(ACTIVE_HEADER_TEXT)
    startA1: str = rowcol_to_a1(2, activeCountIndex + 1)
    endA1: str = rowcol_to_a1(updateDataCount, activeCountIndex + 1)
    formats.append(
        {
            "range": f"{startA1}:{endA1}",
            "format": HORIZONTAL_ALIGNMENT_CENTER,
        }
    )

    # ダイス平均
    startA1: str = rowcol_to_a1(1, diceAverageIndex)
    endA1: str = rowcol_to_a1(updateDataCount, diceAverageIndex)
    formats.append(
        {
            "range": f"{startA1}:{endA1}",
            "format": NUMBER_FORMAT_TYPE_REAL_NUMBER,
        }
    )

    # 冒険者生まれ
    adventurerBirthIndex: int = headers.index(ADVENTURER_BIRTH_HEADER_TEXT)
    startA1 = rowcol_to_a1(2, adventurerBirthIndex + 1)
    endA1: str = rowcol_to_a1(updateDataCount, adventurerBirthIndex + 1)
    formats.append(
        {
            "range": f"{startA1}:{endA1}",
            "format": HORIZONTAL_ALIGNMENT_CENTER,
        }
    )

    # 更新
    worksheet.Update(updateData, formats, False)
