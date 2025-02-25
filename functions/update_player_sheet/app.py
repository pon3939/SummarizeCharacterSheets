# -*- coding: utf-8 -*-


from typing import Any

from aws_lambda_powertools.utilities.typing import LambdaContext
from gspread import utils
from gspread.worksheet import CellFormat
from my_modules.common_functions import initializePlayers
from my_modules.constants.spread_sheet import (
    ACTIVE_HEADER_TEXT,
    DEFAULT_TEXT_FORMAT,
    GAME_MASTER_COUNT_HEADER_TEXT,
    NO_HEADER_TEXT,
    PLAYER_COUNT_HEADER_TEXT,
    PLAYER_NAME_HEADER_TEXT,
    TOTAL_GAME_COUNT_HEADER_TEXT,
    TOTAL_TEXT,
    TRUE_STRING,
    UPDATE_DATETIME_HEADER_TEXT,
)
from my_modules.my_dynamo_db_client import ConvertDynamoDBToJson
from my_modules.my_worksheet import MyWorksheet
from my_modules.player import Player

"""
PLシートを更新
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
    bucketName: str = event["BucketName"]

    players: list[Player] = initializePlayers(
        playerJsons, levelCap, bucketName, int(environment["season_id"])
    )

    updatePlayerSheet(
        environment["spreadsheet_id"], googleServiceAccount, players
    )


def updatePlayerSheet(
    spreadsheetId: str,
    googleServiceAccount: dict[str, str],
    players: list[Player],
):
    """PLシートを更新する

    Args:
        spreadsheetId: (str): スプレッドシートのID
        googleServiceAccount: (dict[str, str]): スプレッドシート認証情報
        players: (list[Player]): プレイヤー情報
    """

    worksheet: MyWorksheet = MyWorksheet(
        googleServiceAccount, spreadsheetId, "PL"
    )
    updateData: list[list] = []

    # ヘッダー
    maxPcCount: int = max(map(lambda x: len(x.Characters), players))
    header: list[str] = [
        NO_HEADER_TEXT,
        PLAYER_NAME_HEADER_TEXT,
        ACTIVE_HEADER_TEXT,
    ]
    for i in range(maxPcCount):
        header.append(f"{i + 1}人目")

    header.extend(
        [
            PLAYER_COUNT_HEADER_TEXT,
            GAME_MASTER_COUNT_HEADER_TEXT,
            TOTAL_GAME_COUNT_HEADER_TEXT,
            UPDATE_DATETIME_HEADER_TEXT,
        ]
    )
    updateData.append(header)

    formats: list[CellFormat] = []
    no: int = 0
    for player in players:
        row: list = []

        # No.
        no += 1
        row.append(no)

        # PL
        row.append(player.Name)

        # 参加傾向
        row.append(TRUE_STRING if player.GetActiveStatus().IsActive() else "")

        # PC名
        for i in range(maxPcCount):
            if len(player.Characters) <= i:
                # PCなし
                row.append("")
                continue

            row.append(player.Characters[i].Name)
            pcIndex: int = header.index(f"{i + 1}人目") + 1
            pcTextFormat: dict = DEFAULT_TEXT_FORMAT.copy()
            pcTextFormat["link"] = {
                "uri": player.Characters[i].GetYtsheetUrl()
            }
            formats.append(
                {
                    "range": utils.rowcol_to_a1(no + 1, pcIndex),
                    "format": {"textFormat": pcTextFormat},
                }
            )

        # 参加
        playerTimes: int = player.GetPlayerTimes()
        row.append(playerTimes)

        # GM
        gameMasterTimes: int = player.GetGameMasterTimes()
        row.append(gameMasterTimes)

        # 参加+GM
        row.append(playerTimes + gameMasterTimes)

        # 更新日時
        row.append(player.GetUpdateDatetime().strftime("%Y/%m/%d %H:%M:%S"))

        updateData.append(row)

    # 合計行
    total: list = [None] * len(header)
    activeCountIndex: int = header.index(ACTIVE_HEADER_TEXT)
    total[activeCountIndex - 1] = TOTAL_TEXT

    # アクティブ
    total[activeCountIndex] = sum(
        1 for x in players if x.GetActiveStatus().IsActive()
    )

    # サブキャラ以降
    for i in range(1, maxPcCount):
        pcIndex: int = header.index(f"{i + 1}人目")
        total[pcIndex] = sum(1 for x in players if len(x.Characters) > i)

    updateData.append(total)

    # 書式設定
    # アクティブ
    startA1: str = utils.rowcol_to_a1(2, activeCountIndex + 1)
    endA1: str = utils.rowcol_to_a1(len(updateData) - 1, activeCountIndex + 1)
    formats.append(
        {
            "range": f"{startA1}:{endA1}",
            "format": {"horizontalAlignment": "CENTER"},
        }
    )

    # 更新
    worksheet.Update(updateData, formats, True)
