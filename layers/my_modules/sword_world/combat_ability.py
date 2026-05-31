# -*- coding: utf-8 -*-

from __future__ import annotations

from dataclasses import dataclass

"""
冒険者技能
"""


@dataclass
class CombatAbility:
    """
    冒険者技能
    Attributes:
        Names str: スキル名
        Level int: レベル
    """

    SkillName: str
    Level: int
