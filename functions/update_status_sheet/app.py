# -*- coding: utf-8 -*-


from re import sub
from typing import Any

from aws_lambda_powertools.utilities.typing import LambdaContext
from gspread import utils
from gspread.worksheet import CellFormat
from my_modules.common_functions import initializePlayers
from my_modules.constants.spread_sheet import (
    ACTIVE_HEADER_TEXT,
    ADVENTURER_BIRTH_HEADER_TEXT,
    DEFAULT_TEXT_FORMAT,
    DICE_AVERAGE_HEADER_TEXT,
    NO_HEADER_TEXT,
    PLAYER_CHARACTER_NAME_HEADER_TEXT,
    RACE_HEADER_TEXT,
    TRUE_STRING,
)
from my_modules.my_dynamo_db_client import ConvertDynamoDBToJson
from my_modules.my_worksheet import MyWorksheet
from my_modules.player import Player

"""
能力値シートを更新
"""

RACES_STATUSES: dict = {
    "人間": {"diceCount": 12, "fixedValue": 0},
    "エルフ": {"diceCount": 11, "fixedValue": 0},
    "ドワーフ": {"diceCount": 10, "fixedValue": 12},
    "タビット": {"diceCount": 9, "fixedValue": 6},
    "ルーンフォーク": {"diceCount": 10, "fixedValue": 0},
    "ナイトメア": {"diceCount": 10, "fixedValue": 0},
    "リカント": {"diceCount": 8, "fixedValue": 9},
    "リルドラケン": {"diceCount": 10, "fixedValue": 6},
    "グラスランナー": {"diceCount": 10, "fixedValue": 12},
    "メリア": {"diceCount": 7, "fixedValue": 6},
    "ティエンス": {"diceCount": 10, "fixedValue": 6},
    "レプラカーン": {"diceCount": 11, "fixedValue": 0},
    "ウィークリング": {"diceCount": 12, "fixedValue": 3},
    "ソレイユ": {"diceCount": 9, "fixedValue": 6},
    "アルヴ": {"diceCount": 8, "fixedValue": 12},
    "シャドウ": {"diceCount": 10, "fixedValue": 0},
    "スプリガン": {"diceCount": 8, "fixedValue": 0},
    "アビスボーン": {"diceCount": 9, "fixedValue": 6},
    "ハイマン": {"diceCount": 8, "fixedValue": 0},
    "フロウライト": {"diceCount": 11, "fixedValue": 12},
    "ダークドワーフ": {"diceCount": 9, "fixedValue": 12},
    "ディアボロ": {"diceCount": 10, "fixedValue": 12},
    "ドレイク": {"diceCount": 10, "fixedValue": 6},
    "バジリスク": {"diceCount": 9, "fixedValue": 6},
    "ダークトロール": {"diceCount": 10, "fixedValue": 6},
    "アルボル": {"diceCount": 10, "fixedValue": 3},
    "バーバヤガー": {"diceCount": 8, "fixedValue": 6},
    "ケンタウロス": {"diceCount": 10, "fixedValue": 6},
    "シザースコーピオン": {"diceCount": 10, "fixedValue": 6},
    "ドーン": {"diceCount": 10, "fixedValue": 6},
    "コボルド": {"diceCount": 10, "fixedValue": 0},
    "ドレイクブロークン": {"diceCount": 10, "fixedValue": 6},
    "ラミア": {"diceCount": 10, "fixedValue": 0},
    "ラルヴァ": {"diceCount": 9, "fixedValue": 6},
}


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
    bucketName: str = event["BucketName"]

    players: list[Player] = initializePlayers(
        playerJsons, levelCap, bucketName, int(environment["season_id"])
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

            # ダイス平均
            racesStatus: dict = RACES_STATUSES[sub("（.*", "", character.Race)]
            diceAverage: float = (
                character.Dexterity.Base
                + character.Agility.Base
                + character.Strength.Base
                + character.Vitality.Base
                + character.Intelligence.Base
                + character.Mental.Base
                - racesStatus["fixedValue"]
            ) / racesStatus["diceCount"]
            row.append(diceAverage)

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
                    "range": utils.rowcol_to_a1(
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
                        "range": utils.rowcol_to_a1(
                            rowIndex, diceAverageIndex
                        ),
                        "format": {"textFormat": diceAverageTextFormat},
                    }
                )

    # 書式設定
    # アクティブ
    activeCountIndex: int = headers.index(ACTIVE_HEADER_TEXT)
    startA1: str = utils.rowcol_to_a1(2, activeCountIndex + 1)
    endA1: str = utils.rowcol_to_a1(len(updateData), activeCountIndex + 1)
    formats.append(
        {
            "range": f"{startA1}:{endA1}",
            "format": {"horizontalAlignment": "CENTER"},
        }
    )

    # ダイス平均
    startA1: str = utils.rowcol_to_a1(1, diceAverageIndex)
    endA1: str = utils.rowcol_to_a1(len(updateData), diceAverageIndex)
    formats.append(
        {
            "range": f"{startA1}:{endA1}",
            "format": {"numberFormat": {"type": "NUMBER", "pattern": "0.00"}},
        }
    )

    # 冒険者生まれ
    adventurerBirthIndex: int = headers.index(ADVENTURER_BIRTH_HEADER_TEXT)
    startA1 = utils.rowcol_to_a1(2, adventurerBirthIndex + 1)
    endA1: str = utils.rowcol_to_a1(len(updateData), adventurerBirthIndex + 1)
    formats.append(
        {
            "range": f"{startA1}:{endA1}",
            "format": {"horizontalAlignment": "CENTER"},
        }
    )

    # 更新
    worksheet.Update(updateData, formats, False)
