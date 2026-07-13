# -*- coding: utf-8 -*-

from google.oauth2 import service_account
from gspread.auth import authorize
from gspread.client import Client
from gspread.exceptions import APIError
from gspread.spreadsheet import Spreadsheet
from gspread.worksheet import Worksheet
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_fixed,
)

from ..constants.spread_sheet import API_RETRY_COUNT, API_RETRY_WAIT_SECOND

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

    @retry(
        stop=stop_after_attempt(API_RETRY_COUNT),
        wait=wait_fixed(API_RETRY_WAIT_SECOND),
        retry=retry_if_exception_type(APIError),
    )
    def getWorksheet(self, title: str) -> Worksheet:
        """ワークシート取得

        Args:
            title (str): ワークシート名

        Returns:
            Worksheet: ワークシート
        """
        return self.spreadsheet.worksheet(title)

    @retry(
        stop=stop_after_attempt(API_RETRY_COUNT),
        wait=wait_fixed(API_RETRY_WAIT_SECOND),
        retry=retry_if_exception_type(APIError),
    )
    def reorderWorksheets(self, titles: list[str]):
        """シートを並び替える

        Args:
            titles (list[str]): シートの並び順に格納されたシート名
        """
        self.spreadsheet.reorder_worksheets(
            map(lambda x: self.getWorksheet(x), titles)
        )
