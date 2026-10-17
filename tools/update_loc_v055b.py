# v0.5.5 追加订正：神光之龙 30×3 敲后只保留；多段伤害官方句式；双龙/裁决用「卡名+」写法
import json, os

ROOT = r"D:\1-workdata\lightsworn_mod\mod\lightsworn\lightsworn\localization\zhs"
path = os.path.join(ROOT, "cards.json")
with open(path, encoding="utf-8") as f:
    cards = json.load(f)

# 1) 多段伤害：官方写法「对所有敌人造成X点伤害Y次」，不再用「重复Y次」
cards["LIGHTSWORN_CARD_CELESTIA.description"] = (
    "[gold]弃光[/gold]{Mill:diff()}。对所有敌人造成{Damage:diff()}点伤害{Hits:diff()}次。"
)
cards["LIGHTSWORN_CARD_SHINING_DRAGON.description"] = (
    "弃牌堆中存在「裁决之龙」和「惩戒之龙」时才能打出。\n"
    "消耗弃牌堆中的所有卡，对所有敌人造成{Damage:diff()}点伤害{Hits:diff()}次，"
    "并施加3层虚弱和3层易伤，然后从消耗堆中将1张「裁决之龙」和1张「惩戒之龙」加入手牌。"
)

# 2) 黄昏之双龙：强化后用「裁决之龙+ / 惩戒之龙+」，不再写“生成强化版”
cards["LIGHTSWORN_CARD_TWIN_TWILIGHT_DRAGON.description"] = (
    "若手牌中有「惩戒之龙」：将弃牌堆中1张「裁决之龙」加入手牌，然后[gold]弃光[/gold]{Mill:diff()}。\n"
    "否则：将1张「裁决之龙{IfUpgraded:show:+|}」和1张「惩戒之龙{IfUpgraded:show:+|}」置入弃牌堆。\n"
    "[gold]从卡组被弃置时[/gold]将弃牌堆中1张「惩戒之龙」加入手牌（没有则无事发生），然后[gold]除光[/gold]4。"
)

# 3) 光道的裁决：统一「裁决之龙+」写法（顺带，避免“强化后的”）
cards["LIGHTSWORN_CARD_DECREE.description"] = (
    "打出后，将此牌置于抽牌堆顶。\n"
    "[gold]从卡组被弃置时[/gold]：将1张保留、消耗的「裁决之龙{IfUpgraded:show:+|}」加入手牌。"
)

with open(path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(cards, f, ensure_ascii=False, indent=2)
    f.write("\n")
print("updated cards:", len(cards))
