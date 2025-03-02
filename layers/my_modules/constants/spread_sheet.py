# -*- coding: utf-8 -*-

"""
スプレッドシート関係の定数
"""

# APIリトライ設定
API_RETRY_COUNT = 3
API_RETRY_WAIT_SECOND = 5

# スプレッドシート全体に適用するテキストの書式
DEFAULT_TEXT_FORMAT: dict = {
    "fontFamily": "Meiryo",
}

# 水平位置を中央にする書式
HORIZONTAL_ALIGNMENT_CENTER: dict = {"horizontalAlignment": "CENTER"}
HORIZONTAL_ALIGNMENT_RIGHT: dict = {"horizontalAlignment": "RIGHT"}

# セルの数値形式
NUMBER_FORMAT_TYPE_INTEGER: dict = {"numberFormat": {"type": "NUMBER"}}
NUMBER_FORMAT_TYPE_REAL_NUMBER: dict = {
    "numberFormat": {"type": "NUMBER", "pattern": "0.00"}
}
NUMBER_FORMAT_TYPE_DATE_TIME: dict = {"numberFormat": {"type": "DATE_TIME"}}

# Trueのときに表示する文字列
TRUE_STRING: str = "○"

# ヘッダーに出力する文字列
NO_HEADER_TEXT: str = "No."
PLAYER_NAME_HEADER_TEXT: str = "PL名"
ACTIVE_HEADER_TEXT: str = "ｱｸﾃｨﾌﾞ"
PLAYER_COUNT_HEADER_TEXT: str = "PL"
GAME_MASTER_COUNT_HEADER_TEXT: str = "GM"
TOTAL_GAME_COUNT_HEADER_TEXT: str = "総卓数"
UPDATE_DATETIME_HEADER_TEXT: str = "更新日時"
PLAYER_CHARACTER_NAME_HEADER_TEXT: str = "PC名"
FAITH_HEADER_TEXT: str = "信仰"
VAGRANTS_HEADER_TEXT: str = "ｳﾞｧｸﾞﾗﾝﾂ"
DIED_TIMES_HEADER_TEXT: str = "死亡"
EXP_HEADER_TEXT: str = "経験点"
RACE_HEADER_TEXT: str = "種族"
DICE_AVERAGE_HEADER_TEXT: str = "ﾀﾞｲｽ平均"
ADVENTURER_BIRTH_HEADER_TEXT: str = "冒険者\n生まれ"
BATTLE_DANCER_HEADER_TEXT: str = "バトルダンサー"
LEVEL_HEADER_TEXT: str = "Lv."
