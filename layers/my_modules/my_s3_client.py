# -*- coding: utf-8 -*-

from json import dumps, loads
from os import getenv

from boto3 import client
from botocore.exceptions import ClientError
from mypy_boto3_dynamodb.type_defs import AttributeValueTypeDef
from mypy_boto3_s3.client import S3Client
from mypy_boto3_s3.type_defs import GetObjectOutputTypeDef

from .constants.aws import S3_DIRECTORY_BACKUPS, S3_ERROR_CODE_NOT_FOUND
from .constants.common import BACKUP_KEY
from .constants.env_keys import MY_AWS_REGION

"""
S3Client拡張クラス
"""


class MyS3Client:
    """
    S3Client拡張クラス
    """

    def __init__(self):
        """
        コンストラクタ
        """

        self.Client: S3Client = client(
            "s3", region_name=getenv(MY_AWS_REGION, "")
        )

    def PutBackupObject(
        self,
        bucketName: str,
        tableName: str,
        body: list[dict[str, AttributeValueTypeDef]],
    ) -> None:
        """

        バックアップオブジェクトを保存

        Args:
            bucketName (str): バケット名
            tableName (str): テーブル名
            body (list[dict[str, AttributeValueTypeDef]]): バックアップデータ
        """

        self.Client.put_object(
            Bucket=bucketName,
            Key=f"{S3_DIRECTORY_BACKUPS}/{tableName}.json",
            Body=dumps({BACKUP_KEY: body}, ensure_ascii=False),
        )

    def GetBackupObject(
        self, bucketName: str, tableName: str
    ) -> list[dict[str, AttributeValueTypeDef]]:
        """

        バックアップオブジェクトを取得

        Args:
            bucketName (str): バケット名
            tableName (str): ファイル名

        Returns:
            list[dict[str, AttributeValueTypeDef]]: バックアップデータ
        """
        try:
            # バケットからファイルを取得
            response: GetObjectOutputTypeDef = self.Client.get_object(
                Bucket=bucketName,
                Key=f"{S3_DIRECTORY_BACKUPS}/{tableName}.json",
            )
        except ClientError as e:
            if (
                e.response.get("Error", {}).get("Code", "")
                == S3_ERROR_CODE_NOT_FOUND
            ):
                # ファイルが存在しない
                return []

            raise e

        responseJson: dict = loads(
            response["Body"].read().decode("utf-8"),
        )
        return responseJson[BACKUP_KEY]
