# -*- coding: utf-8 -*-

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from re import Match, search, split, sub
from typing import Union
from unicodedata import normalize

from my_modules.constants.sword_world import RACES
from my_modules.sword_world.combat_skill import CombatSkill
from my_modules.sword_world.language import Language
from my_modules.sword_world.race import Race

from ..constants import sword_world
from .combat_ability import CombatAbility
from .exp_status import ExpStatus
from .general_skill import GeneralSkill
from .status import Status
from .style import Style

"""
PC
"""

# 自分が開催したときのGM名
_SELF_GAME_MASTER_NAMES: list[str] = [
    "俺",
    "私",
    "自分",
]

# 死亡時の備考
_DIED_REGEXP: str = "死亡"


@dataclass
class PlayerCharacter:
    """
    PC
    """

    def __init__(
        self,
        characterJson: dict,
        playerName: str,
        maxExp: int,
        minimumExp: int,
        updateTime: datetime,
    ):
        """
        コンストラクタ

        Args:
            characterJson dict: PC情報
            playerName str: 最終更新日時
            maxExp int: 最大経験点
            minimumExp int: 最小経験点
            updateTime datetime: 最終更新日時
        """
        self.UpdateDatetime: datetime = updateTime

        # 文字列
        self.YtsheetId: str = characterJson["id"]
        self.Race: str = characterJson.get("race", "")
        self.Age: str = characterJson.get("age", "")
        self.Gender: str = characterJson.get("gender", "")
        self.Birth: str = characterJson.get("birth", "")
        self.CombatFeatsLv1: Union[CombatSkill, None] = None
        if "combatFeatsLv1" in characterJson:
            self.CombatFeatsLv1 = CombatSkill(characterJson["combatFeatsLv1"])

        self.CombatFeatsLv3: Union[CombatSkill, None] = None
        if "combatFeatsLv3" in characterJson:
            self.CombatFeatsLv3 = CombatSkill(characterJson["combatFeatsLv3"])
        self.CombatFeatsLv5: Union[CombatSkill, None] = None
        if "combatFeatsLv5" in characterJson:
            self.CombatFeatsLv5 = CombatSkill(characterJson["combatFeatsLv5"])
        self.CombatFeatsLv7: Union[CombatSkill, None] = None
        if "combatFeatsLv7" in characterJson:
            self.CombatFeatsLv7 = CombatSkill(characterJson["combatFeatsLv7"])
        self.CombatFeatsLv9: Union[CombatSkill, None] = None
        if "combatFeatsLv9" in characterJson:
            self.CombatFeatsLv9 = CombatSkill(characterJson["combatFeatsLv9"])
        self.CombatFeatsLv11: Union[CombatSkill, None] = None
        if "combatFeatsLv11" in characterJson:
            self.CombatFeatsLv11 = CombatSkill(
                characterJson["combatFeatsLv11"]
            )
        self.CombatFeatsLv13: Union[CombatSkill, None] = None
        if "combatFeatsLv13" in characterJson:
            self.CombatFeatsLv13 = CombatSkill(
                characterJson["combatFeatsLv13"]
            )
        self.CombatFeatsLv1bat: Union[CombatSkill, None] = None
        if "combatFeatsLv1bat" in characterJson:
            self.CombatFeatsLv1bat = CombatSkill(
                characterJson["combatFeatsLv1bat"]
            )
        self.AdventurerRank: str = characterJson.get("rank", "")

        # 数値
        self.Level: int = int(characterJson.get("level", "0"))
        self.Exp: int = int(characterJson.get("expTotal", "0"))
        self.GrowthTimes: int = int(characterJson.get("historyGrowTotal", "0"))
        self.TotalHonor: int = int(characterJson.get("historyHonorTotal", "0"))
        self.Hp: int = int(characterJson.get("hpTotal", "0"))
        self.Mp: int = int(characterJson.get("mpTotal", "0"))
        self.LifeResistance: int = int(
            characterJson.get("vitResistTotal", "0")
        )
        self.SpiritResistance: int = int(
            characterJson.get("mndResistTotal", "0")
        )
        self.MonsterKnowledge: int = int(characterJson.get("monsterLore", "0"))
        self.Initiative: int = int(characterJson.get("initiative", "0"))
        self.HistoryMoneyTotal: int = int(
            characterJson.get("historyMoneyTotal", "0")
        )

        # 特殊な変数
        self.Sin: str = characterJson.get("sin", "0")

        # メジャー種族
        majorRace: Union[Race, None] = next(
            (x for x in RACES if x.Name == self.GetMajorRace()),
            None,
        )
        if majorRace is None:
            raise ValueError(f"不正な種族 : {self.GetMajorRace()}")

        self.MajorRace: Race = majorRace

        # 言語(生まれつき習得しているものを除く)
        self.LearnedLanguages: list[Language] = []
        languageNum: int = int(characterJson.get("languageNum", "0"))
        for i in range(1, languageNum + 1):
            languageName: str = characterJson.get(f"language{i}", "")
            if not languageName:
                # 未設定は読み飛ばす
                continue

            canTalk: bool = characterJson.get(f"language{i}Talk", "") != ""
            canRead: bool = characterJson.get(f"language{i}Read", "") != ""
            if canTalk or canRead:
                # 会話か読文が可能なものを設定する
                self.LearnedLanguages.append(
                    Language(languageName, canTalk, canRead)
                )

        # PC名
        # フリガナを削除
        self.Name: str = sub(
            r"\|([^《]*)《[^》]*》",
            r"\1",
            characterJson.get("characterName", ""),
        )
        if self.Name == "":
            # PC名が空の場合は二つ名を表示
            self.Name = characterJson.get("aka", "")

        # 経験点の状態
        self.ActiveStatus: ExpStatus = ExpStatus.INACTIVE
        if self.Exp >= maxExp:
            self.ActiveStatus = ExpStatus.MAX
        elif self.Exp >= minimumExp:
            self.ActiveStatus = ExpStatus.ACTIVE

        # 信仰
        self.Faith: str = characterJson.get("faith", "なし")
        if self.Faith == "その他の信仰":
            self.Faith = characterJson.get("faithOther", self.Faith)

        # 自動取得
        self.AutoCombatFeats: list[CombatSkill] = []
        if "combatFeatsAuto" in characterJson:
            for skillName in characterJson["combatFeatsAuto"].split(","):
                self.AutoCombatFeats.append(CombatSkill(skillName))

        # 技能レベル
        self.CombatAbilities: list[CombatAbility] = []
        for key, skillName in sword_world.COMBAT_ABILITIES.items():
            skillLevel: int = int(characterJson.get(key, "0"))
            if skillLevel > 0:
                self.CombatAbilities.append(
                    CombatAbility(skillName, skillLevel)
                )

        # 各能力値
        self.Dexterity: Status = Status(
            int(characterJson.get("sttBaseA", "0")),
            int(characterJson.get("sttDex", "0")),
            int(characterJson.get("sttAddA", "0")),
            int(characterJson.get("sttEquipA", "0")),
        )
        self.Agility: Status = Status(
            int(characterJson.get("sttBaseB", "0")),
            int(characterJson.get("sttAgi", "0")),
            int(characterJson.get("sttAddB", "0")),
            int(characterJson.get("sttEquipB", "0")),
        )
        self.Strength: Status = Status(
            int(characterJson.get("sttBaseC", "0")),
            int(characterJson.get("sttStr", "0")),
            int(characterJson.get("sttAddC", "0")),
            int(characterJson.get("sttEquipC", "0")),
        )
        self.Vitality: Status = Status(
            int(characterJson.get("sttBaseD", "0")),
            int(characterJson.get("sttVit", "0")),
            int(characterJson.get("sttAddD", "0")),
            int(characterJson.get("sttEquipD", "0")),
        )
        self.Intelligence: Status = Status(
            int(characterJson.get("sttBaseE", "0")),
            int(characterJson.get("sttInt", "0")),
            int(characterJson.get("sttAddE", "0")),
            int(characterJson.get("sttEquipE", "0")),
        )
        self.Mental: Status = Status(
            int(characterJson.get("sttBaseF", "0")),
            int(characterJson.get("sttMnd", "0")),
            int(characterJson.get("sttAddF", "0")),
            int(characterJson.get("sttEquipF", "0")),
        )

        # 秘伝
        self.Styles: list[Style] = []
        mysticArtsNum: int = int(characterJson.get("mysticArtsNum", "0"))
        for i in range(1, mysticArtsNum + 1):
            style: Union[Style, None] = _FindStyle(
                characterJson.get(f"mysticArts{i}", "")
            )
            if style is not None and style not in self.Styles:
                self.Styles.append(style)

        # 秘伝魔法
        mysticMagicNum: int = int(characterJson.get("mysticMagicNum", "0"))
        for i in range(1, mysticMagicNum + 1):
            style = _FindStyle(characterJson.get(f"mysticMagic{i}", ""))
            if style is not None and style not in self.Styles:
                self.Styles.append(style)

        # 名誉アイテム
        honorItemsNum: int = int(characterJson.get("honorItemsNum", "0"))
        for i in range(1, honorItemsNum + 1):
            style = _FindStyle(characterJson.get(f"honorItem{i}", ""))
            if style is not None and style not in self.Styles:
                self.Styles.append(style)

        # 不名誉詳細
        disHonorItemsNum: int = int(characterJson.get("dishonorItemsNum", "0"))
        for i in range(1, disHonorItemsNum + 1):
            style = _FindStyle(characterJson.get(f"dishonorItem{i}", ""))
            if style is not None and style not in self.Styles:
                self.Styles.append(style)

        # 武器
        self.Accuracy: int = 0
        self.AbyssCurses: list[str] = []
        weaponNum: int = int(characterJson.get("weaponNum", "0"))

        for i in range(1, weaponNum + 1):
            # 命中
            self.Accuracy = max(
                self.Accuracy,
                int(characterJson.get(f"weapon{i}AccTotal", "0")),
            )

            # アビスカース
            self.AbyssCurses += _FindAbyssCurses(
                characterJson.get(f"weapon{i}Name", "")
            )
            self.AbyssCurses += _FindAbyssCurses(
                characterJson.get(f"weapon{i}Note", "")
            )

        # 鎧
        armourNum: int = int(characterJson.get("armourNum", "0"))
        for i in range(1, armourNum + 1):
            self.AbyssCurses += _FindAbyssCurses(
                characterJson.get(f"armour{i}Name", "")
            )
            self.AbyssCurses += _FindAbyssCurses(
                characterJson.get(f"armour{i}Note", "")
            )

        # 回避合計など
        self.Evasion: int = 0
        defenseNum: int = int(characterJson.get("defenseNum", "0"))
        for i in range(1, defenseNum + 1):
            # 回避
            self.Evasion = max(
                self.Evasion,
                int(characterJson.get(f"defenseTotal{i}Eva", "0")),
            )

        # 所持品
        self.AbyssCurses += _FindAbyssCurses(characterJson.get("items", ""))

        # 自由記入の表
        effectBoxNum: int = int(characterJson.get("effectBoxNum", "0"))
        for i in range(1, effectBoxNum + 1):
            if (
                characterJson.get(f"effect{i}Name", "") != "アビス侵蝕"
                and characterJson.get(f"effect{i}NameFree", "")
                != "アビスカース"
            ):
                # 表のタイトルが特定の値でなければ処理しない
                continue

            effectNum: int = int(characterJson.get(f"effect{i}Num", "0"))
            for j in range(1, effectNum + 1):
                self.AbyssCurses += _FindAbyssCurses(
                    characterJson.get(f"effect{i}-{j}", "")
                )

        # 重複を削除
        self.AbyssCurses = list(set(self.AbyssCurses))

        # 一般技能
        self.GeneralSkills: list[GeneralSkill] = []
        for i in range(1, int(characterJson.get("commonClassNum", "0")) + 1):
            ytsheetGeneralSkillName: str = characterJson.get(
                f"commonClass{i}", ""
            )
            if ytsheetGeneralSkillName == "":
                continue

            # カッコの中と外で分割
            skillNameAndJob: list[str] = split(
                r"[\(（《]+",
                ytsheetGeneralSkillName.removeprefix("|")
                .removesuffix(")")
                .removesuffix("）")
                .removesuffix("》"),
                1,
            )
            generalSkillLevel: int = int(
                characterJson.get(f"lvCommon{i}", "0")
            )
            if sword_world.PROSTITUTE_GENERAL_SKILL.compareWithListOfStr(
                skillNameAndJob
            ):
                # 男娼と高級男娼を誤検知するので個別対応
                copiedOfficialGeneralSkill: GeneralSkill = deepcopy(
                    sword_world.PROSTITUTE_GENERAL_SKILL
                )
                copiedOfficialGeneralSkill.Level = generalSkillLevel
                self.GeneralSkills.append(copiedOfficialGeneralSkill)
                continue

            officialGeneralSkill: Union[GeneralSkill, None] = next(
                filter(
                    lambda x: x.compareWithListOfStr(skillNameAndJob),
                    sword_world.OFFICIAL_GENERAL_SKILLS,
                ),
                None,
            )
            if officialGeneralSkill is None:
                # オリジナル一般技能
                self.GeneralSkills.append(
                    GeneralSkill(
                        skillNameAndJob[0],
                        skillNameAndJob[1] if len(skillNameAndJob) > 1 else "",
                        generalSkillLevel,
                        True,
                    )
                )
            else:
                # 公式一般技能
                copiedOfficialGeneralSkill = deepcopy(officialGeneralSkill)
                copiedOfficialGeneralSkill.Level = generalSkillLevel
                self.GeneralSkills.append(copiedOfficialGeneralSkill)

        # セッション履歴を集計
        self.GameMasterScenarioKeys: list[str] = []
        self.PlayerTimes: int = 0
        self.DiedTimes: int = 0
        historyNum: int = int(characterJson.get("historyNum", "0"))
        for i in range(1, historyNum + 1):
            gameMaster: str = characterJson.get(f"history{i}Gm", "")
            if gameMaster == "":
                continue

            # 参加、GM回数を集計
            if (
                gameMaster == playerName
                or gameMaster in _SELF_GAME_MASTER_NAMES
            ):
                # 複数PC所持PLのGM回数集計のため、シナリオごとに一意のキーを作成
                date: str = characterJson.get(f"history{i}Date", "")
                count: int = len(
                    [
                        x
                        for x in self.GameMasterScenarioKeys
                        if x.startswith(date)
                    ]
                )

                # 重複を避けるため、同一日の場合は連番を付与
                self.GameMasterScenarioKeys.append(f"{date}_{count}")
            else:
                self.PlayerTimes += 1

            # 備考
            if search(_DIED_REGEXP, characterJson.get(f"history{i}Note", "")):
                # 死亡回数を集計
                self.DiedTimes += 1

        # 経歴を1行ごとに分割
        freeNotes: list[str] = characterJson.get("freeNote", "").split(
            "&lt;br&gt;"
        )

        self.Height: str = ""
        self.Weight: str = ""
        for freeNote in freeNotes:
            if "身長" in freeNote:
                height: str = sub(
                    r".*身長[^\d\.\|]*\|*[^\d\.\|]*([\d\.]+).*",
                    r"\1",
                    freeNote,
                )
                if height != freeNote:
                    self.Height = normalize("NFKC", height)

            if "背丈" in freeNote:
                height = sub(
                    r".*背丈[^\d\.\|]*\|*[^\d\.\|]*([\d\.]+).*",
                    r"\1",
                    freeNote,
                )
                if height != freeNote:
                    self.Height = normalize("NFKC", height)

            if "体重" in freeNote:
                weight: str = sub(
                    r".*体重[^\d\.\|]*\|*[^\d\.\|]*([\d\.]+).*",
                    r"\1",
                    freeNote,
                )
                if weight != freeNote:
                    self.Weight = normalize("NFKC", weight)

    def GetMinorRace(self) -> str:
        """

        マイナー種族を返却する

        Returns:
            str: マイナー種族
        """

        if "ナイトメア" in self.Race or "ウィークリング" in self.Race:
            # 特定種族はかっこをつけたまま返却
            return self.Race

        minorRaceMatch: Union[Match[str], None] = search(
            r"(?<=（)(.+)(?=）)", self.Race
        )
        if minorRaceMatch is None:
            # カッコなしなのでそのまま返却
            return self.Race

        # カッコの中身を返却
        return minorRaceMatch.group()

    def GetMajorRace(self) -> str:
        """

        メジャー種族を返却する

        Returns:
            str: メジャー種族
        """

        return sub(r"（.+）", "", self.Race)

    def IsBattleDancer(self) -> bool:
        """

        バトルダンサーかどうか

        Returns:
            bool: True バトルダンサー
        """

        return any(
            map(
                lambda x: x.SkillName
                == sword_world.BATTLE_DANCER_ABILITY_NAME,
                self.CombatAbilities,
            )
        )

    def IsVagrants(self) -> bool:
        """

        ヴァグランツかどうか

        Returns:
            bool: True ヴァグランツ
        """

        if self.IsBattleDancer() and any(
            list(
                map(
                    lambda x: self.CombatFeatsLv1bat is not None
                    and self.CombatFeatsLv1bat.IsSameCombatSkill(x),
                    sword_world.VAGRANTS_COMBAT_SKILLS,
                )
            )
        ):
            return True

        if any(
            list(
                map(
                    lambda x: self.CombatFeatsLv1 is not None
                    and self.CombatFeatsLv1.IsSameCombatSkill(x),
                    sword_world.VAGRANTS_COMBAT_SKILLS,
                )
            )
        ):
            return True

        if self.Level < 3:
            return False

        if any(
            list(
                map(
                    lambda x: self.CombatFeatsLv3 is not None
                    and self.CombatFeatsLv3.IsSameCombatSkill(x),
                    sword_world.VAGRANTS_COMBAT_SKILLS,
                )
            )
        ):
            return True

        if self.Level < 5:
            return False

        if any(
            list(
                map(
                    lambda x: self.CombatFeatsLv5 is not None
                    and self.CombatFeatsLv5.IsSameCombatSkill(x),
                    sword_world.VAGRANTS_COMBAT_SKILLS,
                )
            )
        ):
            return True

        if self.Level < 7:
            return False

        if any(
            list(
                map(
                    lambda x: self.CombatFeatsLv7 is not None
                    and self.CombatFeatsLv7.IsSameCombatSkill(x),
                    sword_world.VAGRANTS_COMBAT_SKILLS,
                )
            )
        ):
            return True

        if self.Level < 9:
            return False

        if any(
            list(
                map(
                    lambda x: self.CombatFeatsLv9 is not None
                    and self.CombatFeatsLv9.IsSameCombatSkill(x),
                    sword_world.VAGRANTS_COMBAT_SKILLS,
                )
            )
        ):
            return True

        if self.Level < 11:
            return False

        if any(
            list(
                map(
                    lambda x: self.CombatFeatsLv11 is not None
                    and self.CombatFeatsLv11.IsSameCombatSkill(x),
                    sword_world.VAGRANTS_COMBAT_SKILLS,
                )
            )
        ):
            return True

        if self.Level < 13:
            return False

        if any(
            list(
                map(
                    lambda x: self.CombatFeatsLv13 is not None
                    and self.CombatFeatsLv13.IsSameCombatSkill(x),
                    sword_world.VAGRANTS_COMBAT_SKILLS,
                )
            )
        ):
            return True

        return False

    def GetYtsheetUrl(self) -> str:
        """

        ゆとシートのURLを作成

        Args:
            id str: ゆとシートのID
        Returns:
            str: URL
        """
        # 循環参照対策で遅延インポート
        from ..common_functions import MakeYtsheetUrl

        return MakeYtsheetUrl(self.YtsheetId)

    def GetGameMasterTimes(self) -> int:
        """GM回数を取得

        Returns:
            int: GM回数
        """
        return len(self.GameMasterScenarioKeys)

    def GetCombatSkillByName(self, skillName: str) -> Union[CombatSkill, None]:
        """指定された戦闘特技を返却

        Args:
            skillName str: 検索する戦闘特技名

        Returns:
            Union[CombatSkill, None]: 戦闘特技、存在しない場合はNone
        """
        for skill in self.GetCombatSkills():
            if skill.IsSameCombatSkill(skillName):
                return skill

        return None

    def GetCombatSkills(self) -> list[CombatSkill]:
        """戦闘特技のリストを返却

        Returns:
            list[CombatSkill]: 戦闘特技のリスト
        """
        combatSkills: list[CombatSkill] = []
        if self.CombatFeatsLv1 is not None:
            combatSkills.append(self.CombatFeatsLv1)

        if self.CombatFeatsLv3 is not None:
            combatSkills.append(self.CombatFeatsLv3)

        if self.CombatFeatsLv5 is not None:
            combatSkills.append(self.CombatFeatsLv5)

        if self.CombatFeatsLv7 is not None:
            combatSkills.append(self.CombatFeatsLv7)

        if self.CombatFeatsLv9 is not None:
            combatSkills.append(self.CombatFeatsLv9)

        if self.CombatFeatsLv11 is not None:
            combatSkills.append(self.CombatFeatsLv11)

        if self.CombatFeatsLv13 is not None:
            combatSkills.append(self.CombatFeatsLv13)

        if self.IsBattleDancer() and self.CombatFeatsLv1bat is not None:
            combatSkills.append(self.CombatFeatsLv1bat)

        combatSkills += self.AutoCombatFeats

        return combatSkills

    def GetLanguages(self) -> list[Language]:
        """言語のリストを返却

        Returns:
            list[Language]: 言語のリスト
        """
        languages: list[Language] = []
        for language in self.MajorRace.Languages:
            languages.append(language)

        for language in self.LearnedLanguages:
            if language not in languages:
                languages.append(language)

        return languages


def _FindStyle(string: str) -> Union[Style, None]:
    """

    引数が流派を表す文字列か調べ、一致する流派を返却する

    Args:
        string str: 確認する文字列

    Returns:
        Union[Style, None]: 存在する場合は流派、それ以外はNone
    """

    for style in sword_world.STYLES:
        if search(style.GetKeywordsRegexp(), string):
            return style

    return None


def _FindAbyssCurses(string: str) -> list[str]:
    """

    引数に含まれるアビスカースを返却する

    Args:
        string str: 確認する文字列

    Returns:
        list[str]: 引数に含まれるアビスカース
    """

    result: list[str] = []
    for abyssCurse in sword_world.ABYSS_CURSES:
        if abyssCurse in string:
            result.append(abyssCurse)

    return result
