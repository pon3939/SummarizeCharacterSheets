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
    """

    def __init__(
        self,
        SkillName: str,
        DisplayJob: str,
        Level: int = 0,
        IsOriginal: bool = False,
        keywords: list[str] = [],
    ):
        """
        コンストラクタ

        Args:
            SkillName (str): スキル名
            DisplayJob (str): 表示される職業名
            Level (int): レベル
            IsOriginal (bool): 原始スキルかどうか
            keywords (list[str]): 関連するキーワードのリスト
        """

        self.SkillName: str = SkillName
        self.DisplayJob: str = DisplayJob
        self.Level: int = Level
        self.IsOriginal: bool = IsOriginal
        self.keywords: list[str] = [DisplayJob]
        for keyword in keywords:
            self.keywords.append(keyword)

    def getFormattedSkill(self) -> str:
        """
        整形した一般技能名を返す

        Returns:
            str: 整形した一般技能名
        """
        return (
            f"{self.SkillName}"
            + (f"({self.DisplayJob})" if self.DisplayJob else "")
        )

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
            if ytsheetSkillName == self.SkillName:
                # スキル名と一致
                return True

            if ytsheetSkillName == self.DisplayJob:
                # 職業名と一致
                return True

            if ytsheetSkillName in self.keywords:
                # 表示される職業名に関連する職業名が含まれている
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
        return (
            self.SkillName == target.SkillName
            and self.DisplayJob == target.DisplayJob
        )
