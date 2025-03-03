# -*- coding: utf-8 -*-

from __future__ import annotations

from dataclasses import dataclass

"""
一般技能
"""


@dataclass
class CombatSkill:
    """
    一般技能
    Attributes:
        Names str: スキル名
        Job str: 職業名
        Lv int: レベル
    """

    SkillName: str
    Level: int
