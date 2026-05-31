# -*- coding: utf-8 -*-

"""
戦闘特技
"""

from my_modules.constants.sword_world import COMBAT_SKILLS


class CombatSkill:
    """
    戦闘特技
    Attributes:
        Names str: スキル名
        detail str: 詳細。魔法拡大の数など
    """

    def __init__(self, skillName: str):
        """
        コンストラクタ

        Args:
            skillName str: スキル名
        """
        self.detail = ""
        for combatSkill in COMBAT_SKILLS:
            if combatSkill == skillName:
                # スキル名と一致
                self.SkillName = combatSkill
                return

            if skillName.startswith(combatSkill):
                # スキル名が前方一致
                self.SkillName = skillName

                # 武器習熟や魔法拡大などの詳細部分のみを設定
                self.detail = skillName.removeprefix(combatSkill).removeprefix(
                    "／"
                )
                return

        raise ValueError(f"未対応の戦闘特技: {skillName}")

    def IsSameCombatSkill(self, skillName: str) -> bool:
        """
        スキル名が同じ戦闘特技か

        Args:
            skillName str: スキル名
        Returns:
            bool: 同じ戦闘特技の場合はTrue、それ以外はFalse
        """
        return self.SkillName.startswith(skillName)
