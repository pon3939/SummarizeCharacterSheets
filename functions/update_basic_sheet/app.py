# -*- coding: utf-8 -*-


from typing import Any

from aws_lambda_powertools.utilities.typing import LambdaContext
from gspread.utils import rowcol_to_a1
from gspread.worksheet import CellFormat
from my_modules.common_functions import initializePlayers
from my_modules.constants.spread_sheet import (
    ACTIVE_HEADER_TEXT,
    DEFAULT_TEXT_FORMAT,
    DIED_TIMES_HEADER_TEXT,
    FAITH_HEADER_TEXT,
    GAME_MASTER_COUNT_HEADER_TEXT,
    HORIZONTAL_ALIGNMENT_CENTER,
    NO_HEADER_TEXT,
    NUMBER_FORMAT_TYPE_DATE_TIME,
    PLAYER_CHARACTER_NAME_HEADER_TEXT,
    PLAYER_COUNT_HEADER_TEXT,
    PLAYER_NAME_HEADER_TEXT,
    RACE_HEADER_TEXT,
    TOTAL_GAME_COUNT_HEADER_TEXT,
    TRUE_STRING,
    UPDATE_DATETIME_HEADER_TEXT,
    VAGRANTS_HEADER_TEXT,
)
from my_modules.my_dynamo_db_client import ConvertDynamoDBToJson
from my_modules.my_worksheet import MyWorksheet
from my_modules.player import Player

"""
基本シートを更新
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

    updateBasicSheet(
        environment["spreadsheet_id"], googleServiceAccount, players
    )


def updateBasicSheet(
    spreadsheetId: str,
    googleServiceAccount: dict[str, str],
    players: list[Player],
):
    """基本シートを更新する

    Args:
        spreadsheetId: (str): スプレッドシートのID
        googleServiceAccount: (dict[str, str]): スプレッドシート認証情報
        players: (list[Player]): プレイヤー情報
    """

    worksheet: MyWorksheet = MyWorksheet(
        googleServiceAccount, spreadsheetId, "基本"
    )
    updateData: list[list] = []

    # ヘッダー
    header: list[str] = [
        NO_HEADER_TEXT,
        PLAYER_CHARACTER_NAME_HEADER_TEXT,
        ACTIVE_HEADER_TEXT,
        PLAYER_NAME_HEADER_TEXT,
        RACE_HEADER_TEXT,
        "種族\nﾏｲﾅｰﾁｪﾝｼﾞ除く",
        "年齢",
        "性別",
        "身長",
        "体重",
        FAITH_HEADER_TEXT,
        VAGRANTS_HEADER_TEXT,
        "穢れ",
        PLAYER_COUNT_HEADER_TEXT,
        GAME_MASTER_COUNT_HEADER_TEXT,
        TOTAL_GAME_COUNT_HEADER_TEXT,
        "累計ガメル",
        DIED_TIMES_HEADER_TEXT,
        UPDATE_DATETIME_HEADER_TEXT,
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

            # 参加傾向
            row.append(character.ActiveStatus.GetStrForSpreadsheet())

            # PL
            row.append(player.Name)

            # 種族
            row.append(character.GetMinorRace())

            # 種族(マイナーチェンジ除く)
            row.append(character.GetMajorRace())

            # 年齢
            row.append(character.Age)

            # 性別
            row.append(character.Gender)

            # 身長
            row.append(character.Height)

            # 体重
            row.append(character.Weight)

            # 信仰
            row.append(character.Faith)

            # ヴァグランツ
            row.append(TRUE_STRING if character.IsVagrants() else "")

            # 穢れ
            row.append(character.Sin)

            # 参加
            playerTimes: int = character.PlayerTimes
            row.append(playerTimes)

            # GM
            gameMasterTimes: int = character.GetGameMasterTimes()
            row.append(gameMasterTimes)

            # 参加+GM
            row.append(playerTimes + gameMasterTimes)

            # ガメル
            row.append(character.HistoryMoneyTotal)

            # 死亡
            row.append(character.DiedTimes)

            # 更新日時
            row.append(character.UpdateDatetime.strftime("%Y/%m/%d %H:%M:%S"))

            updateData.append(row)

            # PC列のハイパーリンク
            pcTextFormat: dict = DEFAULT_TEXT_FORMAT.copy()
            pcTextFormat["link"] = {"uri": character.GetYtsheetUrl()}
            formats.append(
                {
                    "range": rowcol_to_a1(
                        no + 1,
                        header.index(PLAYER_CHARACTER_NAME_HEADER_TEXT) + 1,
                    ),
                    "format": {"textFormat": pcTextFormat},
                }
            )

    # 合計行
    total: list = [None] * len(header)
    activeCountIndex: int = header.index(ACTIVE_HEADER_TEXT)

    # アクティブ
    total[activeCountIndex] = sum(
        x.CountActivePlayerCharacters() for x in players
    )

    # ヴァグランツ
    vagrantsCountIndex: int = header.index(VAGRANTS_HEADER_TEXT)
    total[vagrantsCountIndex] = sum(
        x.CountVagrantsPlayerCharacters() for x in players
    )

    # 死亡回数
    total[header.index(DIED_TIMES_HEADER_TEXT)] = sum(
        sum(y.DiedTimes for y in x.Characters) for x in players
    )
    updateData.append(total)

    # アクティブ
    updateDataCount: int = len(updateData)
    startA1: str = rowcol_to_a1(2, activeCountIndex + 1)
    endA1: str = rowcol_to_a1(updateDataCount - 1, activeCountIndex + 1)
    formats.append(
        {
            "range": f"{startA1}:{endA1}",
            "format": HORIZONTAL_ALIGNMENT_CENTER,
        }
    )

    # ヴァグランツ
    startA1 = rowcol_to_a1(2, vagrantsCountIndex + 1)
    endA1: str = rowcol_to_a1(updateDataCount - 1, vagrantsCountIndex + 1)
    formats.append(
        {
            "range": f"{startA1}:{endA1}",
            "format": HORIZONTAL_ALIGNMENT_CENTER,
        }
    )

    # 更新日時
    updateDatetimeIndex: int = header.index(UPDATE_DATETIME_HEADER_TEXT)
    startA1 = rowcol_to_a1(2, updateDatetimeIndex + 1)
    endA1 = rowcol_to_a1(updateDataCount - 1, updateDatetimeIndex + 1)
    formats.append(
        {
            "range": f"{startA1}:{endA1}",
            "format": NUMBER_FORMAT_TYPE_DATE_TIME,
        }
    )

    # 更新
    worksheet.Update(updateData, formats, True)
