# -*- coding: utf-8 -*-


from dataclasses import dataclass

from .exp_status import ExpStatus
from .my_dynamo_db_client import StrForDynamoDBToDateTime
from .player_character import PlayerCharacter

"""
PL
"""


@dataclass
class Player:
    """
    PL
    """

    def __init__(
        self,
        name: str,
        strUpdateTime: str,
        maxExp: int,
        minimumExp: int,
        characterJsons: list[dict],
    ):
        """
        コンストラクタ

        Args:
            name str: PL名
            strUpdateTime (str): 最終更新日時
            maxExp (int): 最大経験点
            minimumExp (int): 最小経験点
            characterJsons (list[dict]): PC情報
        """

        self.Name: str = name

        # 更新日時をスプレッドシートが理解できる形式に変換
        self.UpdateTime: str = StrForDynamoDBToDateTime(
            strUpdateTime
        ).strftime("%Y/%m/%d %H:%M:%S")

        self.Characters: list[PlayerCharacter] = list(
            map(
                lambda x: PlayerCharacter(x, self.Name, maxExp, minimumExp),
                characterJsons,
            )
        )

    def CountActivePlayerCharacters(self) -> int:
        """

        アクティブなPC数を返却する

        Returns:
            (int): アクティブなPC数
        """

        return sum(1 for x in self.Characters if x.ActiveStatus.IsActive())

    def CountVagrantsPlayerCharacters(self) -> int:
        """

        ヴァグランツのPC数を返却する

        Returns:
            (int): ヴァグランツのPC数
        """

        return sum(1 for x in self.Characters if x.IsVagrants())

    def GetActiveStatus(self) -> ExpStatus:
        """アクティブ状態を取得

        Returns:
            ExpStatus: アクティブ状態
        """
        return max(
            map(
                lambda x: x.ActiveStatus,
                self.Characters,
            )
        )

    def GetPlayerTimes(self) -> int:
        """PL参加回数を取得

        Returns:
            int: PL参加回数
        """
        return sum(map(lambda x: x.PlayerTimes, self.Characters))

    def GetGameMasterTimes(self) -> int:
        gameMasterScenarioKeys: list[str] = []
        for character in self.Characters:
            gameMasterScenarioKeys.extend(character.GameMasterScenarioKeys)

        # 同一シナリオの重複を排除してGM回数を集計
        return len(set(gameMasterScenarioKeys))
