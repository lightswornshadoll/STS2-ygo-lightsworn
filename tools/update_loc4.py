# 第七轮反馈本地化更新（v0.4.4）
import io, json, os

base = os.path.join(os.path.dirname(__file__), "..", "mod", "lightsworn", "lightsworn", "localization", "zhs")

def load(name):
    return json.load(io.open(os.path.join(base, name), encoding="utf-8"))

def save(name, d):
    with io.open(os.path.join(base, name), "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
        f.write("\n")

cards = load("cards.json")
powers = load("powers.json")
keywords = load("card_keywords.json")

cards["LIGHTSWORN-MICHAEL.description"] = (
    "弃牌堆中存在「光道」牌时才能打出。"
    "将弃牌堆中的所有牌洗回抽牌堆，每洗回1张获得3点格挡。造成{Damage:diff()}点伤害。"
)
cards["LIGHTSWORN-REINFORCE.description"] = "弃光{Mill:diff()}。从卡组中将1张「光道」牌加入手牌。"
cards["LIGHTSWORN-GAROTH.description"] = "每当「光道」牌弃光后，追加弃光2{IfUpgraded:show:，并抽其中「光道」牌数量的牌|}。"
cards["LIGHTSWORN-TWILIGHT_RYKO.description"] = "消耗弃牌堆中的1张「光道」牌（若有）。移除目标敌人的{Strip:diff()}个随机增益，获得1层暮光。"
cards["LIGHTSWORN-DARK_MARCH.description"] = "将弃牌堆中1张「光道」牌加入手牌{IfUpgraded:show:，其费用变为0|}。除光{Banish:diff()}。"
cards["LIGHTSWORN-LAWN_MOWING.description"] = "弃光抽牌堆牌数的一半（向下取整）{IfUpgraded:show:，追加抽1张牌|}。"
cards["LIGHTSWORN-SABRE.description"] = (
    "弃光{Mill:diff()}。获得{Vigor:diff()}点[gold]活力[/gold]。\n"
    "[gold]从卡组被弃置时[/gold]自动加入手牌，且本回合费用变为0。"
)
cards["LIGHTSWORN-JUSTICE_WORLD.description"] = "每当有牌从抽牌堆弃置到弃牌堆时，你获得1点[gold]活力[/gold]（不限「光道」牌）。"
cards["LIGHTSWORN-DECREE.description"] = (
    "打出后，将此牌置于抽牌堆顶。\n"
    "[gold]从卡组被弃置时[/gold]：{IfUpgraded:show:将2张|将1张}虚无、消耗的「裁决之龙」加入弃牌堆。"
)
cards["LIGHTSWORN-TWIN_TWILIGHT_DRAGON.description"] = (
    "若手牌中有「惩戒之龙」：将弃牌堆中1张「裁决之龙」加入手牌，然后弃光{Mill:diff()}。\n"
    "否则：将1张虚无的「裁决之龙」和1张虚无的「惩戒之龙」置入弃牌堆。\n"
    "[gold]从卡组被弃置时[/gold]将弃牌堆中1张「惩戒之龙」加入手牌（没有则无事发生），然后除光{IfUpgraded:show:6|4}。"
)
cards["LIGHTSWORN-TWILIGHT_ERASURE.description"] = (
    "消耗弃牌堆中最多2张「光道」牌，每消耗1张移除目标敌人1个随机增益。\n"
    "[gold]从卡组被弃置时[/gold]手牌中随机{IfUpgraded:show:2|1}张「光道」牌本回合费用变为0。"
)

powers["LIGHTSWORN-JUSTICE_WORLD_POWER.description"] = "每当有牌从抽牌堆弃置到弃牌堆时，你获得1点[gold]活力[/gold]（不限「光道」牌）。"
powers["LIGHTSWORN-JUSTICE_WORLD_POWER.smartDescription"] = powers["LIGHTSWORN-JUSTICE_WORLD_POWER.description"]

keywords["LIGHTSWORN-MILL.description"] = (
    "弃光N：从抽牌堆顶部将N张牌弃置。弃牌堆即墓地——弃掉的牌会喂养墓地收益。"
    "抽牌堆不足时只弃现有部分，不会自动把弃牌堆洗回。"
)

save("cards.json", cards)
save("powers.json", powers)
save("card_keywords.json", keywords)
print("loc updated:")
for k in ("LIGHTSWORN-MICHAEL.description", "LIGHTSWORN-REINFORCE.description",
          "LIGHTSWORN-GAROTH.description", "LIGHTSWORN-TWILIGHT_RYKO.description",
          "LIGHTSWORN-DARK_MARCH.description", "LIGHTSWORN-LAWN_MOWING.description",
          "LIGHTSWORN-SABRE.description", "LIGHTSWORN-JUSTICE_WORLD.description",
          "LIGHTSWORN-DECREE.description", "LIGHTSWORN-TWIN_TWILIGHT_DRAGON.description",
          "LIGHTSWORN-TWILIGHT_ERASURE.description"):
    print(" ", k, "=", cards[k])
print(" ", "LIGHTSWORN-JUSTICE_WORLD_POWER.description =", powers["LIGHTSWORN-JUSTICE_WORLD_POWER.description"])
print(" ", "LIGHTSWORN-MILL.description =", keywords["LIGHTSWORN-MILL.description"])
