# -*- coding: utf-8 -*-
from dataclasses import dataclass

"""
種族ごとのステータスの基準値
"""


@dataclass
class RacesBaseStatus:
    """
    種族ごとのステータスの基準値
    Attributes:
        DiceCount (int): ダイスの数
        FixedValue (int): 固定値
    """

    DiceCount: int
    FixedValue: int

    def GetAllocationsPoint(self, status: int) -> int:
        """
        割り振りポイントを取得する
        Args:
            status (int): ステータス
        Returns:
            int: 割り振りポイント
        """
        # 出目を取得
        pip: int = status - self.FixedValue
        if self.DiceCount == 1:
            if pip == 1:
                return -15
            elif pip == 2:
                return -10
            elif pip == 3:
                return -5
            elif pip == 4:
                return 5
            elif pip == 5:
                return 10
            else:
                return 20
        else:
            if pip == 2:
                return -25
            elif pip == 3:
                return -20
            elif pip == 4:
                return -15
            elif pip == 5:
                return -10
            elif pip == 6:
                return -5
            elif pip == 7:
                return 0
            elif pip == 8:
                return 5
            elif pip == 9:
                return 10
            elif pip == 10:
                return 20
            elif pip == 11:
                return 40
            else:
                return 70
