# -*- coding: utf-8 -*-
from datetime import datetime
from functools import singledispatch
from os import getenv
from typing import Any, Union

from boto3 import client
from mypy_boto3_dynamodb.client import DynamoDBClient
from mypy_boto3_dynamodb.type_defs import (
    BatchWriteItemOutputTypeDef,
    QueryOutputTypeDef,
    ScanOutputTypeDef,
    WriteRequestTypeDef,
)

from ..constants.env_keys import MY_AWS_REGION

"""
DynamoDBClient拡張クラス
"""


class MyDynamoDBClient:
    """
    DynamoDBClient拡張クラス
    """

    # DynamoDBのバッチ書き込み最大数
    _DYNAMO_DB_MAX_BATCH_WRITE_ITEM: int = 25

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
            requestItems (dict): リクエストアイテム

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
                if count == self._DYNAMO_DB_MAX_BATCH_WRITE_ITEM:
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
            tableName (str): テーブル名

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
        scanIndexForward: Union[None, bool] = None,
        limit: int = 0,
    ) -> QueryOutputTypeDef:
        """

        クエリ

        Args:
            tableName (str): テーブル名
            projectionExpression (str): 取得するカラム
            keyConditionExpression (str): 取得条件
            expressionAttributeValues (dict): パラメーター
            expressionAttributeNames (dict): エスケープしたパラメーター
            indexName (str): インデックス名
            scanIndexForward (Union[None, bool]): True: 昇順, False: 降順
            limit (int): 最大取得件数
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

        if scanIndexForward is not None:
            kwargs["ScanIndexForward"] = scanIndexForward

        if limit > 0:
            kwargs["Limit"] = limit

        response: QueryOutputTypeDef = self.Client.query(**kwargs)

        # ページ分割分を取得
        currentResponse: QueryOutputTypeDef = response
        while (
            "LastEvaluatedKey" in currentResponse
            and len(response["Items"]) < limit
        ):
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
            tableName (str): テーブル名
            key (dict): 更新条件
            updateExpression (str): 更新内容
            expressionAttributeValues (dict): パラメーター
        """
        self.Client.update_item(
            TableName=tableName,
            Key=key,
            UpdateExpression=updateExpression,
            ExpressionAttributeValues=expressionAttributeValues,
        )


@singledispatch
def ConvertDynamoDBToJson(dynamoDBData) -> Any:
    """

    DynamoDBから取得したデータを適切な型に変換する
    未対応の型の場合、例外を発生させる

    Args:
        dynamoDBData: DynamoDBから取得したデータ
    """
    raise Exception("未対応の型です")


@ConvertDynamoDBToJson.register
def _(dynamoDBData: dict) -> dict:
    """

    DynamoDBから取得したデータを適切な型に変換する

    Args:
        dynamoDBData dict: DynamoDBから取得したデータ
    Returns:
        dict: 変換後のJSON
    """

    convertedJson: dict = {}
    for key, value in dynamoDBData.items():
        if isinstance(value, dict):
            # 適切な型に変換する
            convertedJson[key] = _ConvertDynamoDBToJsonByTypeKey(value)
        else:
            raise Exception("未対応の型です")

    return convertedJson


@ConvertDynamoDBToJson.register
def _(dynamoDBData: list) -> list:
    """

    DynamoDBから取得したデータを適切な型に変換する

    Args:
        dynamoDBData list: DynamoDBから取得したデータ
    Returns:
        list: 変換後のJSON
    """
    return list(map(ConvertDynamoDBToJson, dynamoDBData))


def _ConvertDynamoDBToJsonByTypeKey(
    dynamoDBData: dict,
) -> Union[str, float, list, dict]:
    """

    DynamoDBから取得したデータを適切な型に変換する

    Args:
        dynamoDBData dict: DynamoDBから取得したデータ
    Returns:
        Union[str, float, list, dict]: 変換後のJSON
    """

    key = next(iter(dynamoDBData.keys()))
    value = next(iter(dynamoDBData.values()))
    if key == "S":
        # 文字列
        return value
    elif key == "Bool":
        # 真偽
        return value
    elif key == "N":
        # 数値
        return float(value)
    elif key == "M":
        # 辞書
        return ConvertDynamoDBToJson(value)
    elif key == "L":
        # リスト
        return list(map(_ConvertDynamoDBToJsonByTypeKey, value))

    raise Exception("未対応の型です")


def ConvertJsonToDynamoDB(json: dict) -> dict:
    """

    データをDynamoDBで扱える型に変換する

    Args:
        json dict: 変換するデータ
    Returns:
        dict: 変換後のデータ
    """
    convertedJson: dict = {}
    for key, value in json.items():
        convertedJson[key] = _ConvertJsonToDynamoDBByTypeKey(value)

    return convertedJson


def _ConvertJsonToDynamoDBByTypeKey(
    value: Union[str, int, float, dict, list]
) -> dict:
    """

    データをDynamoDBで扱える型に変換する

    Args:
        json dict: 変換するデータ
    Returns:
        dict: 変換後のデータ
    """
    # 適切な型に変換する
    if isinstance(value, str):
        # 文字列
        return {"S": value}
    elif isinstance(value, bool):
        # 真偽
        return {"BOOL": value}
    elif isinstance(value, (int, float)):
        # 数値
        return {"N": str(value)}
    elif isinstance(value, dict):
        # 辞書
        return {"M": ConvertJsonToDynamoDB(value)}
    elif isinstance(value, list):
        # リスト
        return {
            "L": list(map(lambda x: _ConvertJsonToDynamoDBByTypeKey(x), value))
        }
    else:
        raise Exception("未対応の型です")


def DateTimeToStrForDynamoDB(target: datetime) -> str:
    """

    DynamoDBに登録するための日時文字列を取得

    Args:
        target datetime: 変換する日時
    Returns:
        str: 日時文字列
    """
    gmt = target
    if target.tzinfo is not None:
        gmt = target.astimezone(None).replace(tzinfo=None)

    return f"{gmt.isoformat(timespec='milliseconds')}Z"
