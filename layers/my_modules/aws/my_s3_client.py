# -*- coding: utf-8 -*-

from json import dumps, loads
from os import getenv
from typing import Any

from boto3 import client
from botocore.exceptions import ClientError
from mypy_boto3_dynamodb.type_defs import AttributeValueTypeDef
from mypy_boto3_s3.client import S3Client
from mypy_boto3_s3.type_defs import GetObjectOutputTypeDef
from pytz import timezone

from ..constants.common import BACKUP_KEY, TIMEZONE
from ..constants.env_keys import MY_AWS_REGION, MY_BUCKET_NAME

"""
S3Client拡張クラス
"""


class MyS3Client:
    """
    S3Client拡張クラス
    """

    # S3のディレクトリ名
    _S3_DIRECTORY_BACKUPS: str = "backups"
    _S3_DIRECTORY_PLAYER_CHARACTERS: str = "player_characters"

    def __init__(self):
        """
        コンストラクタ
        """

        self.Client: S3Client = client(
            "s3", region_name=getenv(MY_AWS_REGION, "")
        )

    def PutBackupObject(
        self,
        tableName: str,
        body: list[dict[str, AttributeValueTypeDef]],
    ) -> None:
        """

        バックアップオブジェクトを保存

        Args:
            tableName (str): テーブル名
            body (list[dict[str, AttributeValueTypeDef]]): バックアップデータ
        """

        self.Client.put_object(
            Bucket=getenv(MY_BUCKET_NAME, ""),
            Key=f"{self._S3_DIRECTORY_BACKUPS}/{tableName}.json",
            Body=dumps({BACKUP_KEY: body}, ensure_ascii=False),
        )

    def GetBackupObject(
        self, tableName: str
    ) -> list[dict[str, AttributeValueTypeDef]]:
        """

        バックアップオブジェクトを取得

        Args:
            tableName (str): ファイル名

        Returns:
            list[dict[str, AttributeValueTypeDef]]: バックアップデータ
        """
        try:
            # バケットからファイルを取得
            response: GetObjectOutputTypeDef = self.Client.get_object(
                Bucket=getenv(MY_BUCKET_NAME, ""),
                Key=f"{self._S3_DIRECTORY_BACKUPS}/{tableName}.json",
            )
        except ClientError as e:
            if e.response.get("Error", {}).get("Code", "") == "NoSuchKey":
                # ファイルが存在しない
                return []

            raise e

        responseJson: dict = loads(
            response["Body"].read().decode("utf-8"),
        )
        return responseJson[BACKUP_KEY]

    def PutPlayerCharacterObject(
        self,
        seasonId: int,
        ytsheetId: str,
        body: str,
    ) -> None:
        """

        PCオブジェクトを保存

        Args:
            seasonId (int): シーズンID
            ytsheetId (str): ファイル名
            body (list[dict]): ゆとシートのデータ
        """
        # バケットからファイルを取得
        self.Client.put_object(
            Bucket=getenv(MY_BUCKET_NAME, ""),
            Key=(
                f"{self._S3_DIRECTORY_PLAYER_CHARACTERS}/"
                f"{seasonId}/{ytsheetId}.json"
            ),
            Body=body,
        )

    def GetPlayerCharacterObject(
        self, seasonId: int, ytsheetId: str
    ) -> dict[str, Any]:
        """

        PCオブジェクトを取得

        Args:
            seasonId (int): シーズンID
            ytsheetId (str): ファイル名

        Returns:
            dict: PCデータ
        """
        # バケットからファイルを取得
        response: GetObjectOutputTypeDef = self.Client.get_object(
            Bucket=getenv(MY_BUCKET_NAME, ""),
            Key=(
                f"{self._S3_DIRECTORY_PLAYER_CHARACTERS}/"
                f"{seasonId}/{ytsheetId}.json"
            ),
        )

        return {
            "Body": loads(
                response["Body"].read().decode("utf-8"),
            ),
            "LastModified": response["LastModified"].astimezone(
                timezone(TIMEZONE)
            ),
        }
