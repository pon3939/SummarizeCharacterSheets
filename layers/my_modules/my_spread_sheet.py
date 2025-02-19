# -*- coding: utf-8 -*-

from google.oauth2 import service_account
from gspread.auth import authorize
from gspread.client import Client
from gspread.spreadsheet import Spreadsheet
from gspread.utils import ValueInputOption, rowcol_to_a1
from gspread.worksheet import CellFormat, Worksheet

from .constants.spread_sheet import DEFAULT_TEXT_FORMAT

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
        credentials = service_account.Credentials.from_service_account_info(
            googleServiceAccount,
            scopes=["https://www.googleapis.com/auth/spreadsheets"],
        )
        client: Client = authorize(credentials)
        spreadsheet: Spreadsheet = client.open_by_key(spreadsheetId)
        self.worksheet: Worksheet = spreadsheet.worksheet(worksheetName)

    def Update(
        self,
        values: list[list],
        formats: list[CellFormat],
        isContainTotalRow: bool,
    ):
        """更新する

        Args:
            values (list[list]): 更新する値
            formats (list[CellFormat]): 書式
            isContainTotalRow (bool): 合計行を含むか
        """
        # 初期化
        self.worksheet.clear()
        self.worksheet.clear_basic_filter()

        # 更新
        self.worksheet.update(
            values, value_input_option=ValueInputOption.user_entered
        )

        # デフォルトの書式設定
        rowCount: int = len(values)
        columnCount: int = max(map(lambda x: len(x), values))
        startA1: str = rowcol_to_a1(1, 1)
        endA1: str = rowcol_to_a1(rowCount, columnCount)
        self.worksheet.format(
            f"{startA1}:{endA1}",
            {
                "verticalAlignment": "MIDDLE",
                "textFormat": DEFAULT_TEXT_FORMAT,
            },
        )

        # ヘッダーの書式設定
        startA1 = rowcol_to_a1(1, 1)
        endA1 = rowcol_to_a1(1, columnCount)
        self.worksheet.format(
            f"{startA1}:{endA1}",
            {
                "horizontalAlignment": "CENTER",
                "verticalAlignment": "BOTTOM",
                "textRotation": {"vertical": False},
            },
        )

        self.worksheet.batch_format(formats)

        # 行列の固定
        self.worksheet.freeze(1, 2)

        # フィルター
        self.worksheet.set_basic_filter(
            1, 1, rowCount - (1 if isContainTotalRow else 0), columnCount
        )
