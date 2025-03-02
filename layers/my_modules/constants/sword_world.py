# -*- coding: utf-8 -*-

from ..general_skill import GeneralSkill
from ..style import Style

"""
SW2.5関係の定数
"""

# 戦闘技能
BATTLE_DANCER_SKILL_NAME: str = "バトルダンサー"
COMBAT_SKILLS: dict[str, str] = {
    "lvFig": "ファイター",
    "lvGra": "グラップラー",
    "lvBat": BATTLE_DANCER_SKILL_NAME,
    "lvFen": "フェンサー",
    "lvSho": "シューター",
    "lvSor": "ソーサラー",
    "lvCon": "コンジャラー",
    "lvPri": "プリースト",
    "lvMag": "マギテック",
    "lvFai": "フェアリーテイマー",
    "lvDru": "ドルイド",
    "lvDem": "デーモンルーラー",
    "lvAby": "アビスゲイザー",
    "lvSco": "スカウト",
    "lvRan": "レンジャー",
    "lvSag": "セージ",
    "lvEnh": "エンハンサー",
    "lvBar": "バード",
    "lvRid": "ライダー",
    "lvAlc": "アルケミスト",
    "lvGeo": "ジオマンサー",
    "lvWar": "ウォーリーダー",
    "lvDar": "ダークハンター",
}

# 流派
STYLES: list[Style] = [
    Style("イーヴァル狂闘術", ["イーヴァル"]),
    Style("ミハウ式流円闘技", ["ミハウ"]),
    Style("カスロット豪砂拳・バタス派", ["カスロット", "バタス"]),
    Style("マカジャハット・プロ・グラップリング", ["マカジャハット"]),
    Style("ナルザラント柔盾活用術", ["ナルザラント"]),
    Style("アースト強射術", ["アースト"]),
    Style("ヒアデム魔力流転操撃", ["ヒアデム"]),
    Style("古モルガナンシン王国式戦域魔導術", ["モルガナンシン"]),
    Style("ダイケホーン双霊氷法", ["ダイケホーン"]),
    Style("スホルテン騎乗戦技", ["スホルテン"]),
    Style(
        "アードリアン流古武道・メルキアノ道場", ["アードリアン", "メルキアノ"]
    ),
    Style("エルエレナ惑乱操布術", ["エルエレナ"]),
    Style("ファイラステン古流ヴィンド派(双剣の型)", ["ファイラステン"]),
    Style("クウェラン闇弓術改式", ["クウェラン"]),
    Style("ヴァルト式戦場剣殺法", ["ヴァルト"]),
    Style("ガオン無双獣投術", ["ガオン"]),
    Style("聖戦士ローガン鉄壁の型", ["ローガン"]),
    Style("クーハイケン強竜乗法", ["クーハイケン"]),
    Style(
        "七色のマナ：魔法行使法学派",
        ["七色のマナ：", "七色のマナ:", "魔法行使"],
    ),
    Style("キルガリー双刃戦舞闘技", ["キルガリー"]),
    Style("エステル式ポール舞闘術", ["エステル", "ポール"]),
    Style("銛王ナイネルガの伝承", ["ナイネルガ"]),
    Style("死骸銃遊戯", ["死骸銃"]),
    Style("対奈落教会議・奈落反転神術", ["奈落"]),
    Style("「七色のマナ」式召異魔法術・魔使影光学理論", ["式召異", "魔使影"]),
    Style("アルショニ軽身跳闘法", ["アルショニ"]),
    Style("ノーザンファング鉱士削岩闘法", ["ノーザンファング"]),
    Style("キングスレイ式近接銃撃術", ["キングスレイ"]),
    Style("ネルネアニン騎獣調香術", ["ネルネアニン"]),
    Style("オルフィード式蒸発妖精術", ["オルフィード"]),
    Style("フィノア派森羅導術", ["フィノア"]),
    Style("ソムバートル制圧弓騎兵団", ["ソムバートル"]),
    Style("ハールーン魔精解放術式", ["ハールーン"]),
    Style("ウル・ディ・ガウル秘薬刀術", ["ガウル"]),
    Style("アヴァル口伝・森択演奏術", ["アヴァル"]),
    Style("オークファルト念闘術", ["オークファルト"]),
    Style("ガムベイ奈落技術討究派", ["ガムベイ"]),
    Style("アゴウ重槌破闘術", ["アゴウ"], True),
    Style("岩流斧闘術アズラック派", ["アズラック"], True),
    Style("リシバル集団運槍術", ["リシバル"], True),
    Style("イーリー流幻闘道化術", ["イーリー"], True),
    Style("ギルヴァン流愚人剣", ["ギルヴァン"], True),
    Style("ネレホーサ舞剣術", ["ネレホーサ"], True),
    Style("ドーザコット潜弓道", ["ドーザコット"], True),
    Style("マルガ＝ハーリ天地銃剣術", ["マルガ", "ハーリ"], True),
    Style("ライロック魔刃術", ["ライロック"], True),
    Style("ルシェロイネ魔導術", ["ルシェロイネ"], True),
    Style("クラウゼ流一刀魔王剣", ["クラウゼ"], True),
    Style("ベネディクト流紳士杖道", ["ベネディクト"], True),
    Style("ハーデン鷹爪流投擲術", ["ハーデン"], True),
    Style("エイントゥク十字弓道場", ["エイントゥク"], True),
    Style("ジアンブリック攻盾法", ["ジアンブリック"], True),
    Style("ルキスラ銀鱗隊護衛術", ["ルキスラ"], True),
    Style("ティルダンカル古代光魔党", ["ティルダンカル"], True),
    Style("カサドリス戦奏術", ["カサドリス"], True),
    Style("ファルネアス重装馬闘技", ["ファルネアス"], True),
    Style("タマフ＝ダツエ流浪戦瞳", ["タマフ", "ダツエ"], True),
    Style("ドバルス螺旋運手", ["ドバルス"], True),
    Style("ニルデスト流実戦殺法", ["ニルデスト"], True),
    Style("オーロンセシーレ中隊軽装突撃術", ["オーロンセシーレ"], True),
    Style("ラステンルフト双盾護身術", ["ラステンルフト"], True),
    Style("ホプレッテン機動重弩弓法", ["ホプレッテン"], True),
    Style("エイスンアデアル召喚術", ["エイスンアデアル"], True),
    Style("眠り猫流擬態術", ["眠り猫"], True),
    Style("カンフォーラ博物学派", ["カンフォーラ"], True),
    Style("不死者討滅武技バニシングデス", ["バニシングデス"], True),
    Style("ダルポン流下克戦闘術", ["ダルボン", "ダルポン"], True),
    Style("ヴェルクンスト砦建築一党", ["ヴェルクンスト"], True),
    Style("神速確勝ボルンの精髄", ["ボルン"], True),
    Style("バルナッド英雄庭流派・封神舞踏剣", ["バルナッド"], True),
    Style("森の吹き矢使いたち", ["吹き矢"], True),
    Style("ウォーディアル流竜騎神槍", ["ウォーディアル"], True),
    Style("ギルツ屠竜輝剛拳", ["ギルツ"], True),
    Style("ガドハイ狩猟術", ["ガドハイ"], True),
    Style("ソソ破皇戦槌術", ["ソソ"], True),
    Style("バルカン流召精術", ["バルカン"], True),
    Style("ジーズドルフ騎竜術", ["ジーズドルフ"], True),
]

# アビスカース
ABYSS_CURSES: list[str] = [
    "自傷の",
    "嘆きの",
    "優しき",
    "差別の",
    "脆弱な",
    "無謀な",
    "重い",
    "難しい",
    "軟弱な",
    "病弱な",
    "過敏な",
    "陽気な",
    "たどたどしい",
    "代弁する",
    "施しは受けない",
    "死に近い",
    "おしゃれな",
    "マナを吸う",
    "鈍重な",
    "定まらない",
    "錯乱の",
    "足絡みの",
    "滑り落ちる",
    "悪臭放つ",
    "醜悪な",
    "唸る",
    "ふやけた",
    "古傷の",
    "まばゆい",
    "栄光なき",
    "正直者の",
    "乗り物酔いの",
    "碧を厭う",
    "我慢できない",
    "つきまとう",
    "のろまな",
    "衰退の",
    "怠惰の",
    "慌てる",
    "喉が詰まる",
    "無駄遣いの",
    "空腹の",
    "疲れが取れない",
    "薬物が効きにくい",
    "死体漁りの",
    "従わない",
    "一服を取る",
    "余裕を見せる",
    "息が荒い",
    "音痴の",
    "信頼しきれない",
    "手から零れる",
    "天地荒ぶる",
    "失敗を嘲る",
    "学ばない",
    "完璧主義な",
    "華美を嫌う",
    "昏睡の",
    "烙印を受ける",
    "散漫な",
    "命を削る",
    "マナを削る",
    "誇示する",
    "踏ん張りがきかない",
    "身を晒す",
    "いたぶる",
    "残心の",
    "マナが漏れやすい",
    "退けたがる",
    "手加減する",
    "調子が悪い",
]

# 一般技能
PROSTITUTE_GENERAL_SKILL: GeneralSkill = GeneralSkill(
    "プロスティチュート", "娼婦/男娼"
)
OFFICIAL_GENERAL_SKILLS: list[GeneralSkill] = [
    GeneralSkill("アーマラー", "防具職人"),
    GeneralSkill("インベンター", "発明家"),
    GeneralSkill("ウィーバー", "織り子"),
    GeneralSkill("ウィッチドクター", "祈祷師"),
    GeneralSkill("ウェイター/ウェイトレス", "給仕"),
    GeneralSkill("ウェザーマン", "天候予報士"),
    GeneralSkill("ウェポンスミス", "武器職人"),
    GeneralSkill("ウッドクラフトマン", "木工職人"),
    GeneralSkill("エンジニア", "機関士"),
    GeneralSkill("オーサー", "作家"),
    GeneralSkill("オフィシャル", "役人"),
    GeneralSkill("ガーデナー", "庭師"),
    GeneralSkill("カーペンター", "大工"),
    GeneralSkill("カラーマン", "絵具師"),
    GeneralSkill("キースミス", "鍵屋"),
    GeneralSkill("クレリック", "聖職者"),
    GeneralSkill("グレイブキーパー", "墓守"),
    GeneralSkill("コーチマン", "御者"),
    GeneralSkill("コーティザン", "高級娼婦/男娼"),
    GeneralSkill("コック", "料理人"),
    GeneralSkill("コンポーザー", "作曲家"),
    GeneralSkill("サージョン", "外科医"),
    GeneralSkill("シグナルマン", "信号士"),
    GeneralSkill("シューメイカー", "靴職人"),
    GeneralSkill("ジュエラー", "宝飾師"),
    GeneralSkill("シンガー", "歌手"),
    GeneralSkill("スカラー", "学生/学者"),
    GeneralSkill("スカルプター", "彫刻家"),
    GeneralSkill("スクライブ", "筆写人"),
    GeneralSkill("セイラー", "水夫/船乗り"),
    GeneralSkill("ソルジャー", "兵士"),
    GeneralSkill("タワーマン", "高所作業員"),
    GeneralSkill("ダンサー", "踊り子"),
    GeneralSkill("ツアーガイド", "旅先案内人"),
    GeneralSkill("ディスティラー", "(蒸留)酒造家"),
    GeneralSkill("テイマー", "調教師"),
    GeneralSkill("テイラー", "仕立て屋"),
    GeneralSkill("ドクター", "医者"),
    GeneralSkill("ドラッグメイカー", "薬剤師"),
    GeneralSkill("ナース", "看護師"),
    GeneralSkill("ナビゲーター", "航海士"),
    GeneralSkill("ノーブル", "貴族"),
    GeneralSkill("ハーズマン", "牧童"),
    GeneralSkill("バーバー", "髪結い/理髪師"),
    GeneralSkill("ハウスキーパー", "家政婦(夫)"),
    GeneralSkill("バトラー", "執事"),
    GeneralSkill("パヒューマー", "調香師"),
    GeneralSkill("パフォーマー", "芸人"),
    GeneralSkill("ハンター", "狩人"),
    GeneralSkill("ファーマー", "農夫"),
    GeneralSkill("フィッシャーマン", "漁師"),
    GeneralSkill("フォーチュンテラー", "占い師"),
    GeneralSkill("ブラックスミス", "鍛冶師"),
    GeneralSkill("ブルワー", "醸造家"),
    GeneralSkill("プレスティディジテイター", "手品師"),
    PROSTITUTE_GENERAL_SKILL,
    GeneralSkill("ペインター", "絵師"),
    GeneralSkill("ベガー", "物乞い"),
    GeneralSkill("ヘラルディスト", "紋章学者"),
    GeneralSkill("ボーンカーバー", "骨細工師"),
    GeneralSkill("マーチャント", "商人"),
    GeneralSkill("マイナー", "鉱夫"),
    GeneralSkill("ミートパッカー", "精肉業者"),
    GeneralSkill("ミッドワイフ", "産婆"),
    GeneralSkill("ミュージシャン", "演奏家"),
    GeneralSkill("メーソン", "石工"),
    GeneralSkill("ライブラリアン", "司書"),
    GeneralSkill("ランバージャック", "木こり"),
    GeneralSkill("リペアラー", "復元師"),
    GeneralSkill("リンギスト", "通訳"),
    GeneralSkill("レイバー", "肉体労働者"),
    GeneralSkill("レザーワーカー", "皮革職人"),
    GeneralSkill("エクスプローラー", "探検家"),
    GeneralSkill("エンチャンター", "付与術師"),
    GeneralSkill("オラトール", "雄弁家"),
    GeneralSkill("カートグラファー", "地図屋"),
    GeneralSkill("ギャングスタ", "ギャング"),
    GeneralSkill("ギャンブラー", "賭博師"),
    GeneralSkill("ストーリーテラー", "語り部"),
    GeneralSkill("ディテクティヴ", "探偵"),
    GeneralSkill("マネージャー", "元締め"),
    GeneralSkill("マナアプレイザー", "魔力鑑定士"),
    GeneralSkill("フォレストガイド", "森林案内人"),
    GeneralSkill("アーティストマネージャー", "芸能補佐"),
    GeneralSkill("チーフタン", "族長"),
    GeneralSkill("ピアインスペクター", "橋脚点検士"),
    GeneralSkill("プロスペクター", "山師"),
    GeneralSkill("マリンアニマルトレーナー", "海獣調教師"),
]

# ヴァグランツ戦闘特技
VAGRANTS_COMBAT_SKILLS: list[str] = [
    "追い打ち",
    "抵抗強化",
    "カニングキャスト",
    "クイックキャスト",
    "シールドバッシュ",
    "シャドウステップ",
    "捨て身攻撃",
    "露払い",
    "乱撃",
    "クルードテイク",
    "掠め取り",
]
