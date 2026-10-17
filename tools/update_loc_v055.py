# v0.5.5 本地化：裁决/惩戒/神光/黄昏双龙文案 + 两件先古遗物词条
import json, os

ROOT = r"D:\1-workdata\lightsworn_mod\mod\lightsworn\lightsworn\localization\zhs"

def load(name):
    with open(os.path.join(ROOT, name), encoding="utf-8") as f:
        return json.load(f)

def save(name, data):
    with open(os.path.join(ROOT, name), "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

cards = load("cards.json")
cards["LIGHTSWORN_CARD_PUNISH_DRAGON.description"] = (
    "消耗堆中存在4种以上「光道」牌时才能打出。\n"
    "将弃牌堆与消耗堆中所有非「光道」的攻击、技能、能力牌返回卡组，"
    "每有一张，所有敌人随机获得1层负面状态（人工制品可抵挡）。"
    "造成{Damage:diff()}点伤害，并获得1层[gold]暮光[/gold]。"
)
cards["LIGHTSWORN_CARD_TWIN_TWILIGHT_DRAGON.description"] = (
    "若手牌中有「惩戒之龙」：将弃牌堆中1张「裁决之龙」加入手牌，然后[gold]弃光[/gold]{Mill:diff()}。\n"
    "否则：将1张「裁决之龙」和1张「惩戒之龙」置入弃牌堆{IfUpgraded:show:（改为生成强化版）|}。\n"
    "[gold]从卡组被弃置时[/gold]将弃牌堆中1张「惩戒之龙」加入手牌（没有则无事发生），然后[gold]除光[/gold]4。"
)
# 伤害数值走 {Damage:diff()}，35→30 无需改文案；保留由关键词自动显示。
save("cards.json", cards)

relics = load("relics.json")
relics["LIGHTSWORN_RELIC_BETTER_MUST_PLAY_YUGIOH.title"] = "更好的游戏王"
relics["LIGHTSWORN_RELIC_BETTER_MUST_PLAY_YUGIOH.description"] = (
    "你的卡组数量不够，但我修复了这一点。战斗开始时，若抽牌堆不足40张，"
    "只生成普通、罕见、稀有卡牌补足，比例为5:3:2。"
)
relics["LIGHTSWORN_RELIC_LIGHTSWORN_SCEPTER.title"] = "光道权杖"
relics["LIGHTSWORN_RELIC_LIGHTSWORN_SCEPTER.description"] = (
    "每回合开始时，[gold]弃光[/gold]3。每有1张因此被弃置的「光道」牌，抽1张牌。"
)
save("relics.json", relics)

print("cards:", len(cards), "relics:", len(relics))
print("ok")
