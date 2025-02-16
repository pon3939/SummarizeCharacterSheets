# -*- coding: utf-8 -*-

from os import getenv

from boto3 import client
from mypy_boto3_dynamodb.client import DynamoDBClient
from mypy_boto3_dynamodb.type_defs import (
    BatchWriteItemOutputTypeDef,
    DescribeTableOutputTypeDef,
    GlobalSecondaryIndexUpdateTypeDef,
    QueryOutputTypeDef,
    ScanOutputTypeDef,
    UpdateTableInputRequestTypeDef,
    WriteRequestTypeDef,
)

from .constants.aws import DYNAMO_DB_MAX_BATCH_WRITE_ITEM
from .constants.env_keys import MY_AWS_REGION

"""
DynamoDBClient拡張クラス
"""


class MyDynamoDBClient:
    """
    DynamoDBClient拡張クラス
    """

    def __init__(self):
        """
        コンストラクタ
        """

        self.Client: DynamoDBClient = client(
            "dynamodb", region_name=getenv(MY_AWS_REGION, "")
        )

    def BatchWriteItem(
        self, requestItems: dict[str, list[WriteRequestTypeDef]]
    ) -> None:
        """

        一括登録

        Args:
            requestItems dict: リクエストアイテム

        Returns:
            int: アクティブなPC数
        """

        separatedRequestItems: dict[str, list[WriteRequestTypeDef]] = {}
        count: int = 0
        for tableName, requests in requestItems.items():
            for request in requests:
                if tableName not in separatedRequestItems:
                    separatedRequestItems[tableName] = []

                separatedRequestItems[tableName].append(request)
                count += 1
                if count == DYNAMO_DB_MAX_BATCH_WRITE_ITEM:
                    # 処理件数上限に達した場合は登録
                    batchWriteItemResponse: BatchWriteItemOutputTypeDef = (
                        self.Client.batch_write_item(
                            RequestItems=separatedRequestItems
                        )
                    )

                    while len(batchWriteItemResponse["UnprocessedItems"]) != 0:
                        batchWriteItemResponse = self.Client.batch_write_item(
                            RequestItems=batchWriteItemResponse[
                                "UnprocessedItems"
                            ]
                        )

                    # 初期化
                    separatedRequestItems = {}
                    count = 0

        if count != 0:
            # 処理件数上限に満たなかった分を登録
            batchWriteItemResponse = self.Client.batch_write_item(
                RequestItems=separatedRequestItems
            )

            while len(batchWriteItemResponse["UnprocessedItems"]) != 0:
                batchWriteItemResponse = self.Client.batch_write_item(
                    RequestItems=batchWriteItemResponse["UnprocessedItems"]
                )

    def Scan(self, tableName: str) -> ScanOutputTypeDef:
        """

        スキャン

        Args:
            tableName str: テーブル名

        Returns:
            dict: スキャン結果
        """
        response: ScanOutputTypeDef = self.Client.scan(
            TableName=tableName,
        )

        # ページ分割分を取得
        currentResponse: ScanOutputTypeDef = response
        while "LastEvaluatedKey" in currentResponse:
            currentResponse = self.Client.scan(
                TableName=tableName,
                ExclusiveStartKey=currentResponse["LastEvaluatedKey"],
            )
            response["Items"] += currentResponse["Items"]

        return response

    def Query(
        self,
        tableName: str,
        projectionExpression: str,
        keyConditionExpression: str,
        expressionAttributeValues: dict,
        expressionAttributeNames: dict = {},
        indexName: str = "",
    ) -> QueryOutputTypeDef:
        """

        クエリ

        Args:
            tableName str: テーブル名
            projectionExpression str: 取得するカラム
            keyConditionExpression str: 取得条件
            expressionAttributeValues dict: パラメーター
            expressionAttributeNames dict: エスケープしたパラメーター
            indexName str: インデックス名
        Returns:
            QueryOutputTypeDef: クエリ結果
        """
        kwargs: dict = {
            "TableName": tableName,
            "ProjectionExpression": projectionExpression,
            "KeyConditionExpression": keyConditionExpression,
            "ExpressionAttributeValues": expressionAttributeValues,
        }
        if len(expressionAttributeNames) != 0:
            kwargs["ExpressionAttributeNames"] = expressionAttributeNames

        if indexName != "":
            kwargs["IndexName"] = indexName

        response: QueryOutputTypeDef = self.Client.query(**kwargs)

        # ページ分割分を取得
        currentResponse: QueryOutputTypeDef = response
        while "LastEvaluatedKey" in currentResponse:
            currentResponse = self.Client.query(
                **kwargs,
                ExclusiveStartKey=currentResponse["LastEvaluatedKey"],
            )
            response["Items"] += currentResponse["Items"]

        return response

    def UpdateItem(
        self,
        tableName: str,
        key: dict,
        updateExpression: str,
        expressionAttributeValues: dict,
    ):
        """

        更新

        Args:
            tableName str: テーブル名
            key dict: 更新条件
            updateExpression str: 更新内容
            expressionAttributeValues dict: パラメーター
        """
        self.Client.update_item(
            TableName=tableName,
            Key=key,
            UpdateExpression=updateExpression,
            ExpressionAttributeValues=expressionAttributeValues,
        )

    def UpdateTable(
        self,
        tableName: str,
        readCapacity: int,
        writeCapacity: int,
        indexNames: list[str] = [],
    ):
        """

        テーブル定義更新

        Args:
            tableName (str): テーブル名
            read_capacity (int): 読み取りキャパシティー
            write_capacity (int): 書き込みキャパシティー
            indexNames (list[str]): インデックス名
        """
        kwargs: UpdateTableInputRequestTypeDef = {
            "TableName": tableName,
            "ProvisionedThroughput": {
                "ReadCapacityUnits": readCapacity,
                "WriteCapacityUnits": writeCapacity,
            },
        }
        if len(indexNames) != 0:
            globalSecondaryIndexUpdates: list[
                GlobalSecondaryIndexUpdateTypeDef
            ] = []
            for indexName in indexNames:
                globalSecondaryIndexUpdates.append(
                    {
                        "Update": {
                            "IndexName": indexName,
                            "ProvisionedThroughput": {
                                "ReadCapacityUnits": readCapacity,
                                "WriteCapacityUnits": writeCapacity,
                            },
                        }
                    }
                )

            kwargs["GlobalSecondaryIndexUpdates"] = globalSecondaryIndexUpdates

        self.Client.update_table(**kwargs)

    def DescribeTable(self, tableName: str) -> DescribeTableOutputTypeDef:
        """

        テーブル情報取得

        Args:
            tableName (str): テーブル名

        Returns:
            DescribeTableOutputTypeDef: _description_
        """
        return self.Client.describe_table(TableName=tableName)
