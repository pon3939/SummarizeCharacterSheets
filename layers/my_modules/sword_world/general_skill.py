# -*- coding: utf-8 -*-

from __future__ import annotations

from dataclasses import dataclass

"""
一般技能
"""


@dataclass
class GeneralSkill:
    """
    一般技能
    Attributes:
        Names str: スキル名
        Job str: 職業名
        Lv int: レベル
    """

    SkillName: str
    Job: str
    Level: int = 0
    IsOriginal: bool = False

    def getFormattedSkill(self) -> str:
        """
        整形した一般技能名を返す

        Returns:
            str: 整形した一般技能名
        """
        return f"{self.SkillName}" + (f"({self.Job})" if self.Job else "")

    def getFormattedSkillAndLevel(self) -> str:
        """
        整形した一般技能情報を返す

        Returns:
            str: 整形した一般技能情報
        """
        return f"{self.getFormattedSkill()} : {self.Level}"

    def compareWithListOfStr(self, target: list[str]) -> bool:
        """
        引数とこのオブジェクトを比較する

        Args:
            target(list[str]): 比較対象

        Returns:
            bool: True: 一致
        """
        for ytsheetSkillName in target:
            if any(ytsheetSkillName in x for x in [self.SkillName, self.Job]):
                # スキル名か職業名と一致
                return True

        return False

    def compareWithGeneralSkill(self, target: GeneralSkill) -> bool:
        """
        引数とこのオブジェクトを比較する

        Args:
            target(GeneralSkill): 比較対象

        Returns:
            bool: True: 一致
        """
        return self.SkillName == target.SkillName and self.Job == target.Job
