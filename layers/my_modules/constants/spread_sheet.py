# -*- coding: utf-8 -*-

"""
スプレッドシート関係の定数
"""


# スプレッドシート全体に適用するテキストの書式
DEFAULT_TEXT_FORMAT: dict = {
    "fontFamily": "Meiryo",
}

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

# 合計行のラベル
TOTAL_TEXT: str = "合計"
