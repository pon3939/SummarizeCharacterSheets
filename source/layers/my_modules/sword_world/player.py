# -*- coding: utf-8 -*-


from dataclasses import dataclass
from datetime import datetime

from .exp_status import ExpStatus
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
        characters: list[PlayerCharacter],
    ):
        """
        コンストラクタ

        Args:
            name (str): PL名
            characters (list[PlayerCharacter]): PC情報
        """

        self.Name: str = name
        self.Characters: list[PlayerCharacter] = characters

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
        """GM回数を取得

        Returns:
            int: GM回数
        """
        gameMasterScenarioKeys: list[str] = []
        for character in self.Characters:
            gameMasterScenarioKeys.extend(character.GameMasterScenarioKeys)

        # 同一シナリオの重複を排除してGM回数を集計
        return len(set(gameMasterScenarioKeys))

    def GetUpdateDatetime(self) -> datetime:
        """最終更新日時を取得

        Returns:
            datetime: 最終更新日時
        """
        return max(map(lambda x: x.UpdateDatetime, self.Characters))
