# -*- coding: utf-8 -*-


from json import dumps
from typing import Any

from requests import put

from .cloud_formation_response import CloudFormationResponse
from .constants.aws import (
    CLOUD_FORMATION_REQUEST_TYPE_MANUAL,
    CLOUD_FORMATION_STATUS_SUCCESS,
)
from .my_s3_client import MyS3Client
from .player import Player
from .player_character import PlayerCharacter

"""
汎用関数
"""


def MakeYtsheetUrl(id: str) -> str:
    """

    ゆとシートのURLを作成

    Args:
        id (str): ゆとシートのID
    Returns:
        str: URL
    """
    return f"https://yutorize.2-d.jp/ytsheet/sw2.5/?id={id}"


def putCloudFormationResponse(
    response: CloudFormationResponse,
    status: str = CLOUD_FORMATION_STATUS_SUCCESS,
    reason: str = "成功",
) -> None:
    """

    CloudFormationにレスポンスを返す
    Custom Resourceの処理完了を知らせるために使用

    Args:
        response (CloudFormationResponse): レスポンス情報
        status (str): ステータス
        reason (str): 理由
    """
    if response.RequestType == CLOUD_FORMATION_REQUEST_TYPE_MANUAL:
        # 手動実行なので何もしない
        return

    responseBody: str = dumps(
        {
            "Status": status,
            "Reason": reason,
            "PhysicalResourceId": response.PhysicalResourceId,
            "StackId": response.StackId,
            "RequestId": response.RequestId,
            "LogicalResourceId": response.LogicalResourceId,
            "Data": {},
        }
    )

    headers: dict[str, str] = {
        "content-type": "",
        "content-length": str(len(responseBody)),
    }
    put(response.ResponseUrl, data=responseBody, headers=headers)


def initializePlayers(
    playerJsons: list[dict[str, Any]],
    levelCap: dict[str, Any],
    bucketName: str,
    seasonId: int,
) -> list[Player]:
    """プレイヤー情報初期化

    Args:
        playerJsons (list[dict[str, Any]]): プレイヤー情報のJSON
        levelCap (dict[str, Any]): レベルキャップ
        bucketName (str): プレイヤー情報が保存されているバケット名
        seasonId (int): シーズンID

    Raises:
        Exception: playerJsonsのフォーマット不正

    Returns:
        list[Player]: プレイヤー情報
    """
    s3: MyS3Client = MyS3Client()
    players: list[Player] = []
    for playerJson in playerJsons:
        characters: list[PlayerCharacter] = []
        playerName: str = playerJson["name"]
        for character in playerJson["characters"]:
            # S3から取得
            playerCharacterJson: dict[str, Any] = s3.GetPlayerCharacterObject(
                bucketName, seasonId, character["ytsheet_id"]
            )
            characters.append(
                PlayerCharacter(
                    playerCharacterJson,
                    playerName,
                    levelCap["max_exp"],
                    levelCap["minimum_exp"],
                    character["update_datetime"],
                )
            )

        players.append(
            Player(
                playerName,
                characters,
            )
        )

    return players
