# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .races_base_status import RacesBaseStatus

if TYPE_CHECKING:
    # 循環参照対策
    from ..player_character import PlayerCharacter

"""
種族
"""


@dataclass
class Race:
    """
    種族
    Attributes:
        Name str: 名前
        Dexterity (RacesBaseStatus): 器用
        Agility (RacesBaseStatus): 敏捷
        Strength (RacesBaseStatus): 筋力
        Vitality (RacesBaseStatus): 生命力
        Intelligence (RacesBaseStatus): 知力
        Mental (RacesBaseStatus): 精神力
    """

    Name: str
    Dexterity: RacesBaseStatus
    Agility: RacesBaseStatus
    Strength: RacesBaseStatus
    Vitality: RacesBaseStatus
    Intelligence: RacesBaseStatus
    Mental: RacesBaseStatus

    def GetTotalBaseStatus(self) -> RacesBaseStatus:
        """
        合計ステータスを取得する
        Returns:
            RacesBaseStatus: 合計ステータス
        """
        return RacesBaseStatus(
            self.Dexterity.DiceCount
            + self.Agility.DiceCount
            + self.Strength.DiceCount
            + self.Vitality.DiceCount
            + self.Intelligence.DiceCount
            + self.Mental.DiceCount,
            self.Dexterity.FixedValue
            + self.Agility.FixedValue
            + self.Strength.FixedValue
            + self.Vitality.FixedValue
            + self.Intelligence.FixedValue
            + self.Mental.FixedValue,
        )

    def GetAllocationsPoint(self, playerCharacter: "PlayerCharacter") -> int:
        """
        割り振りポイントを取得する
        Args:
            playerCharacter (PlayerCharacter): プレイヤーキャラクター
        Returns:
            int: 割り振りポイント
        """
        return (
            self.Dexterity.GetAllocationsPoint(playerCharacter.Dexterity.Base)
            + self.Agility.GetAllocationsPoint(playerCharacter.Agility.Base)
            + self.Strength.GetAllocationsPoint(playerCharacter.Strength.Base)
            + self.Vitality.GetAllocationsPoint(playerCharacter.Vitality.Base)
            + self.Intelligence.GetAllocationsPoint(
                playerCharacter.Intelligence.Base
            )
            + self.Mental.GetAllocationsPoint(playerCharacter.Mental.Base)
        )
