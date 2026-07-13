# -*- coding: utf-8 -*-

from gspread.exceptions import APIError
from gspread.utils import ValueInputOption, rowcol_to_a1
from gspread.worksheet import CellFormat, Worksheet
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_fixed,
)

from ..constants.spread_sheet import (
    API_RETRY_COUNT,
    API_RETRY_WAIT_SECOND,
    DEFAULT_TEXT_FORMAT,
    HORIZONTAL_ALIGNMENT_CENTER,
)
from .my_spreadsheet import MySpreadsheet

"""
Worksheet拡張クラス
"""


class MyWorksheet:
    """
    Worksheet拡張クラス
    """

    def __init__(
        self,
        googleServiceAccount: dict[str, str],
        spreadsheetId: str,
        worksheetName: str,
    ):
        """コンストラクター

        Args:
            googleServiceAccount (dict[str, str]): 認証情報
            spreadsheetId (str): スプレッドシートのID
            worksheetName (str): シート名
        """

        # サービスアカウントでスプレッドシートにログイン
        spreadsheet: MySpreadsheet = MySpreadsheet(
            googleServiceAccount, spreadsheetId
        )
        self.worksheet: Worksheet = spreadsheet.getWorksheet(worksheetName)

    @retry(
        stop=stop_after_attempt(API_RETRY_COUNT),
        wait=wait_fixed(API_RETRY_WAIT_SECOND),
        retry=retry_if_exception_type(APIError),
    )
    def Update(
        self,
        values: list[list],
        additionalFormats: list[CellFormat],
        isContainTotalRow: bool,
    ):
        """更新する

        Args:
            values (list[list]): 更新する値
            additionalFormats (list[CellFormat]): 書式
            isContainTotalRow (bool): 合計行を含むか
        """
        # 初期化
        self.worksheet.clear()
        self.worksheet.clear_basic_filter()

        # 更新
        self.worksheet.update(
            values, value_input_option=ValueInputOption.user_entered
        )

        formats: list[CellFormat] = []
        rowCount: int = len(values)
        columnCount: int = max(map(lambda x: len(x), values))

        # デフォルトの書式設定
        startA1: str = rowcol_to_a1(1, 1)
        endA1: str = rowcol_to_a1(rowCount, columnCount)
        formats.append(
            {
                "range": f"{startA1}:{endA1}",
                "format": {
                    "verticalAlignment": "MIDDLE",
                    "textFormat": DEFAULT_TEXT_FORMAT,
                },
            }
        )

        # ヘッダーの書式設定
        startA1 = rowcol_to_a1(1, 1)
        endA1 = rowcol_to_a1(1, columnCount)
        formats.append(
            {
                "range": f"{startA1}:{endA1}",
                "format": HORIZONTAL_ALIGNMENT_CENTER
                | {
                    "verticalAlignment": "BOTTOM",
                    "textRotation": {"vertical": False},
                },
            }
        )

        formats.extend(additionalFormats)
        self.worksheet.batch_format(formats)

        # 行列の固定
        self.worksheet.freeze(1, 2)

        # フィルター
        self.worksheet.set_basic_filter(
            1,
            1,
            rowCount
            - (1 if isContainTotalRow else 0),  # 合計行はフィルターしない
            columnCount,
        )


def ConvertToVerticalHeaders(horizontalHeaders: list[str]) -> list[str]:
    """

    ヘッダーを縦書き用の文字に変換する

    Args:
        horizontalHeader (list[str]): ヘッダー
    Returns:
        list[str]: 縦書きヘッダー
    """

    return list(
        map(
            lambda x: x.replace("ー", "｜")
            .replace("(", "︵")
            .replace(")", "︶"),
            horizontalHeaders,
        )
    )
