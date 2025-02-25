# -*- coding: utf-8 -*-

from os import getenv
from typing import Union

from aws_lambda_powertools.utilities.typing import LambdaContext
from my_modules.constants.env_keys import (
    PLAYERS_SEASON_ID_NAME_INDEX_NAME,
    PLAYERS_TABLE_NAME,
)
from my_modules.my_dynamo_db_client import (
    ConvertDynamoDBToJson,
    ConvertJsonToDynamoDB,
    GetCurrentDateTimeForDynamoDB,
    MyDynamoDBClient,
)
from mypy_boto3_dynamodb.type_defs import (
    QueryOutputTypeDef,
    WriteRequestTypeDef,
)

"""
Playersに登録
"""


DynamoDb: Union[MyDynamoDBClient, None] = None


def lambda_handler(event: dict, context: LambdaContext):
    """

    メイン処理

    Args:
        event dict: イベント
        context LambdaContext: コンテキスト
    """

    global DynamoDb

    seasonId: int = int(event["SeasonId"])
    players: list[dict] = event["Players"]

    DynamoDb = MyDynamoDBClient()
    maxId: int = GetMaxId(seasonId)
    putPlayers(players, seasonId, maxId)


def GetMaxId(seasonId: int) -> int:
    """IDの最大値を取得する

    Args:
        seasonId int: シーズンID

    Returns:
        int: 最大ID
    """
    global DynamoDb

    if DynamoDb is None:
        raise Exception("DynamoDBが初期化されていません")

    projectionExpression: str = "id"
    KeyConditionExpression: str = "season_id = :season_id"
    expressionAttributeValues: dict = ConvertJsonToDynamoDB(
        {":season_id": seasonId}
    )
    response: QueryOutputTypeDef = DynamoDb.Query(
        getenv(PLAYERS_TABLE_NAME, ""),
        projectionExpression,
        KeyConditionExpression,
        expressionAttributeValues,
        scanIndexForward=False,
        limit=1,
    )

    dynamoDbPlayers: list[dict] = response["Items"]
    if len(dynamoDbPlayers) == 0:
        return 0

    player: dict = ConvertDynamoDBToJson(dynamoDbPlayers[0])
    return int(player["id"])


def putPlayers(players: list[dict], seasonId: int, maxId: int):
    """Playersを挿入する

    Args:
        players: list[dict]: PC情報
        seasonId: int: シーズンID
        maxId: int: 既存IDの最大値
    """
    global DynamoDb

    if DynamoDb is None:
        raise Exception("DynamoDBが初期化されていません")

    id: int = maxId
    requestItems: list[WriteRequestTypeDef] = []
    for player in players:
        # プレイヤー名で存在チェック
        queryResult: QueryOutputTypeDef = DynamoDb.Query(
            getenv(PLAYERS_TABLE_NAME, ""),
            "id",
            "season_id = :season_id AND #name = :name",
            ConvertJsonToDynamoDB(
                {":season_id": seasonId, ":name": player["Name"]}
            ),
            {"#name": "name"},
            getenv(PLAYERS_SEASON_ID_NAME_INDEX_NAME, ""),
            limit=1,
        )

        newCharacters: list[dict[str, str]] = list(
            map(
                lambda x: {
                    "ytsheet_id": x,
                    "update_datetime": GetCurrentDateTimeForDynamoDB(),
                },
                player["YtsheetIds"],
            )
        )
        existsPlayers: list[dict] = ConvertDynamoDBToJson(queryResult["Items"])
        if len(existsPlayers) > 0:
            # 更新
            DynamoDb.UpdateItem(
                getenv(PLAYERS_TABLE_NAME, ""),
                ConvertJsonToDynamoDB(
                    {"season_id": seasonId, "id": existsPlayers[0]["id"]}
                ),
                "SET characters = list_append(characters, :new_characters) ",
                ConvertJsonToDynamoDB({":new_characters": newCharacters}),
            )
            continue

        # 新規作成
        id += 1
        newPlayer: dict = {
            "season_id": seasonId,
            "id": id,
            "name": player["Name"],
            "characters": newCharacters,
        }
        requestItem: WriteRequestTypeDef = {}
        requestItem["PutRequest"] = {"Item": {}}
        requestItem["PutRequest"]["Item"] = ConvertJsonToDynamoDB(newPlayer)
        requestItems.append(requestItem)

    if len(requestItems) == 0:
        return

    DynamoDb.BatchWriteItem({getenv(PLAYERS_TABLE_NAME, ""): requestItems})
