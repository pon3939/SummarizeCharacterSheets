# -*- coding: utf-8 -*-

from google.oauth2 import service_account
from gspread.auth import authorize
from gspread.client import Client
from gspread.spreadsheet import Spreadsheet
from gspread.worksheet import Worksheet

"""
Spreadsheet拡張クラス
"""


class MySpreadsheet:
    """
    Spreadsheet拡張クラス
    """

    def __init__(
        self,
        googleServiceAccount: dict[str, str],
        spreadsheetId: str,
    ):
        """コンストラクター

        Args:
            googleServiceAccount (dict[str, str]): 認証情報
            spreadsheetId (str): スプレッドシートのID
        """

        # サービスアカウントでスプレッドシートにログイン
        credentials = service_account.Credentials.from_service_account_info(
            googleServiceAccount,
            scopes=["https://www.googleapis.com/auth/spreadsheets"],
        )
        client: Client = authorize(credentials)
        self.spreadsheet: Spreadsheet = client.open_by_key(spreadsheetId)

    def getWorksheet(self, title: str) -> Worksheet:
        """ワークシート取得

        Args:
            title (str): ワークシート名

        Returns:
            Worksheet: ワークシート
        """
        return self.spreadsheet.worksheet(title)

    def reorderWorksheets(self, titles: list[str]):
        """シートを並び替える

        Args:
            titles (list[str]): シートの並び順に格納されたシート名
        """
        self.spreadsheet.reorder_worksheets(
            map(lambda x: self.getWorksheet(x), titles)
        )
