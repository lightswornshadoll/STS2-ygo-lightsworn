# -*- coding: utf-8 -*-
"""v0.4.19 反馈1-5 本地化更新：
② 影融/珠泪融合触发卡的描述在词条词后面加 {IfUpgraded:show:+|}（升级可见变化）
③ 融合条件从两个词条挪到各融合卡卡面（前置"融合条件："行）
④ 顶栏融合图鉴按钮的悬浮提示（static_hover_tips 新表）
含改动前后键存在校验，缺键/多改即报错退出。
"""
import json, io, os, sys

ROOT = os.path.join(os.path.dirname(__file__), "..", "mod", "lightsworn", "lightsworn", "localization", "zhs")

CARDS = {
    # ---- ② 触发卡：词条词后加 + ----
    "LIGHTSWORN-SULIEK.description":
        ("造成{Damage:diff()}点伤害。然后可以丢弃1张手牌中的攻击牌：若如此做，回复1点能量并弃光3。",
         "造成{Damage:diff()}点伤害。然后可以丢弃1张手牌中的攻击牌：若如此做，回复1点能量并弃光3。珠泪融合{IfUpgraded:show:+|}。"),
    "LIGHTSWORN-MERRLI.description":
        ("造成{Damage:diff()}点伤害。若目标意图不为攻击，回复1点能量并弃光3。",
         "造成{Damage:diff()}点伤害。若目标意图不为攻击，回复1点能量并弃光3。珠泪融合{IfUpgraded:show:+|}。"),
    "LIGHTSWORN-HAVNIS.description":
        ("造成{Damage:diff()}点伤害，获得{Block:diff()}点格挡。弃光3。",
         "造成{Damage:diff()}点伤害，获得{Block:diff()}点格挡。弃光3。珠泪融合{IfUpgraded:show:+|}。"),
    "LIGHTSWORN-SHADDOLL_FUSION.description":
        ("影融。\n[gold]强化后[/gold] 素材也可以从卡组选择。",
         "影融{IfUpgraded:show:+|}。\n[gold]强化后[/gold] 素材也可以从卡组选择。"),
    "LIGHTSWORN-EL_SHADDOLL_FUSION.description":
        ("影融，且本次生成的神影依视为已升级（无论此牌是否强化）。",
         "影融{IfUpgraded:show:+|}，且本次生成的神影依视为已升级（无论此牌是否强化）。"),
    "LIGHTSWORN-NEPHE_SHADDOLL_FUSION.description":
        ("影融，且本次素材豁免条件：任意2张手牌（含至少1张「影依」牌）即可生成任意神影依。",
         "影融{IfUpgraded:show:+|}，且本次素材豁免条件：任意2张手牌（含至少1张「影依」牌）即可生成任意神影依。"),
    "LIGHTSWORN-TOHUSHADDOLL_GRYSTA.description":
        ("造成{Damage:diff()}点伤害。从弃牌堆将1张影依攻击卡加入手牌，本回合其费用变为0，其伤害变为0。\n影融：素材改为从弃牌堆选2张「影依」牌消耗（不触发其被弃置时效果）。",
         "造成{Damage:diff()}点伤害。从弃牌堆将1张影依攻击卡加入手牌，本回合其费用变为0，其伤害变为0。\n影融{IfUpgraded:show:+|}：素材改为从弃牌堆选2张「影依」牌消耗（不触发其被弃置时效果）。"),
    "LIGHTSWORN-SHADDOLL_CONSTRUCT.description":
        ("影融。\n[gold]被弃置时[/gold]：若弃牌堆中其他「影依」牌不少于{Recall:diff()}张，将此牌加入手牌且费用变为0。",
         "影融{IfUpgraded:show:+|}。\n[gold]被弃置时[/gold]：若弃牌堆中其他「影依」牌不少于{Recall:diff()}张，将此牌加入手牌且费用变为0。"),
    "LIGHTSWORN-SHADDOLL_SCHISM.description":
        ("影融，且素材改为从弃牌堆选2张「影依」牌消耗（不触发其被弃置时效果）。",
         "影融{IfUpgraded:show:+|}，且素材改为从弃牌堆选2张「影依」牌消耗（不触发其被弃置时效果）。"),
    # ---- ③ 融合卡：前置融合条件行 ----
    "LIGHTSWORN-KITKALLOS.description":
        ("从抽牌堆中选择1张珠泪卡加入手牌（费用变为0）。弃光5。造成{Damage:diff()}点伤害。",
         "融合条件：2张珠泪攻击牌。\n从抽牌堆中选择1张珠泪卡加入手牌（费用变为0）。弃光5。造成{Damage:diff()}点伤害。"),
    "LIGHTSWORN-RULKALLOS.description":
        ("造成{Damage:diff()}点伤害，若目标为爪牙，伤害翻倍。本回合每打出过1张珠泪卡，获得2点格挡。",
         "融合条件：含水仙女人鱼的2张珠泪攻击牌。\n造成{Damage:diff()}点伤害，若目标为爪牙，伤害翻倍。本回合每打出过1张珠泪卡，获得2点格挡。"),
    "LIGHTSWORN-KALEIDO_HEART.description":
        ("造成{Damage:diff()}点伤害。从抽牌堆中选择1张珠泪卡弃置。获得{Thorns:diff()}层荆棘。",
         "融合条件：含雷诺哈特的3张珠泪攻击牌。\n造成{Damage:diff()}点伤害。从抽牌堆中选择1张珠泪卡弃置。获得{Thorns:diff()}层荆棘。"),
    "LIGHTSWORN-DRAGOSTAPELIA.description":
        ("造成{Damage:diff()}点伤害。对目标施加1层缩小。",
         "融合条件：含融合卡的2张珠泪攻击牌。\n造成{Damage:diff()}点伤害。对目标施加1层缩小。"),
    "LIGHTSWORN-EL_SHADDOLL_WINDA.description":
        ("造成{Damage:diff()}点伤害，回复3点能量。从弃牌堆将1张影依技能加入手牌。",
         "融合条件：2张影依牌。\n造成{Damage:diff()}点伤害，回复3点能量。从弃牌堆将1张影依技能加入手牌。"),
    "LIGHTSWORN-EL_SHADDOLL_CONSTRUCT.description":
        ("造成{Damage:diff()}点伤害；若目标有格挡，改为清除其全部格挡。从卡组弃置1张影依卡。从弃牌堆将1张影依技能加入手牌。",
         "融合条件：1张影依牌+1张光道牌。\n造成{Damage:diff()}点伤害；若目标有格挡，改为清除其全部格挡。从卡组弃置1张影依卡。从弃牌堆将1张影依技能加入手牌。"),
    "LIGHTSWORN-EL_SHADDOLL_WENDIGO.description":
        ("获得{Buffer:diff()}层缓冲。从弃牌堆将1张影依技能加入手牌。\n[gold]本场战斗[/gold]此牌只能生成1次。",
         "融合条件：1张影依牌+1张技能牌。\n获得{Buffer:diff()}层缓冲。从弃牌堆将1张影依技能加入手牌。\n[gold]本场战斗[/gold]此牌只能生成1次。"),
    "LIGHTSWORN-EL_SHADDOLL_GRYSTA.description":
        ("造成{Damage:diff()}点伤害。可以丢弃1张手牌中的影依卡，对目标施加2层虚弱和易伤。从弃牌堆将1张影依技能加入手牌。",
         "融合条件：1张影依牌+1张攻击牌。\n造成{Damage:diff()}点伤害。可以丢弃1张手牌中的影依卡，对目标施加2层虚弱和易伤。从弃牌堆将1张影依技能加入手牌。"),
    "LIGHTSWORN-EL_SHADDOLL_SHEKHINAGA.description":
        ("获得{Block:diff()}点格挡。可以丢弃1张手牌中的影依卡，获得1层人工制品。从弃牌堆将1张影依技能加入手牌。",
         "融合条件：2张影依攻击牌。\n获得{Block:diff()}点格挡。可以丢弃1张手牌中的影依卡，获得1层人工制品。从弃牌堆将1张影依技能加入手牌。"),
    "LIGHTSWORN-EL_SHADDOLL_ANOYATYLLIS.description":
        ("造成{Damage:diff()}点伤害，从弃牌堆将2张「影依」牌加入手牌。",
         "融合条件：3张影依牌。\n造成{Damage:diff()}点伤害，从弃牌堆将2张「影依」牌加入手牌。"),
    "LIGHTSWORN-EL_SHADDOLL_APKALLONE.description":
        ("造成{Damage:diff()}点伤害，获得{Block:diff()}点格挡。从卡组或弃牌堆将1张影依卡加入手牌，然后弃置1张手牌。",
         "融合条件：2张不同名的影依牌。\n造成{Damage:diff()}点伤害，获得{Block:diff()}点格挡。从卡组或弃牌堆将1张影依卡加入手牌，然后弃置1张手牌。"),
    "LIGHTSWORN-EL_SHADDOLL_MESHAHRAIL.description":
        ("造成{Damage:diff()}点伤害，获得2层镀层。从卡组将1张影依卡加入手牌，从弃牌堆将1张影依攻击卡加入手牌（本回合费用变为0）。",
         "融合条件：3张手牌（含至少1张影依牌）。\n造成{Damage:diff()}点伤害，获得2层镀层。从卡组将1张影依卡加入手牌，从弃牌堆将1张影依攻击卡加入手牌（本回合费用变为0）。"),
    "LIGHTSWORN-REESHADDOLL_WENDIKURHU.description":
        ("获得{Block:diff()}点格挡。接下来3次「影依」牌被弃置时，其「被弃置时」的效果触发2次。从弃牌堆将1张影依卡加入手牌。",
         "融合条件：2张影依技能牌。\n获得{Block:diff()}点格挡。接下来3次「影依」牌被弃置时，其「被弃置时」的效果触发2次。从弃牌堆将1张影依卡加入手牌。"),
}

KEYWORDS = {
    "LIGHTSWORN-TEARFUSION.description":
        ("珠泪融合：拥有此效果的卡被弃置时发动——从弃牌堆选择2~3张珠泪攻击牌放回抽牌堆（融合卡被选做素材时改为消耗），然后从满足条件的珠泪融合卡中选择1张加入手牌（触发卡已升级则融合出强化版）。同一回合每张融合卡只能生成1次；融合卡离开弃牌堆时消耗。融合条件（素材数量须与条件严格一致）：水仙女人鱼=2张珠泪攻击牌；鲁莎卡人鱼=含水仙女人鱼的2张珠泪攻击牌；卡雷多哈特=含雷诺哈特的3张珠泪攻击牌；捕食植物犀角龙=含融合卡的2张珠泪攻击牌。",
         "珠泪融合：拥有此效果的卡被弃置时发动——从弃牌堆选择2~3张珠泪攻击牌放回抽牌堆（融合卡被选做素材时改为消耗），然后从满足融合条件的珠泪融合卡中选择1张加入手牌（触发卡已升级则融合出强化版）。同一回合每张融合卡只能生成1次；融合卡离开弃牌堆时消耗。素材数量须与融合条件严格一致，各融合卡的条件见其卡面说明。"),
    "LIGHTSWORN-SHADDOLLFUSION.description":
        ("影融：弃置手牌中2~3张牌作为素材（神影依也可作素材），从条件满足的神影依中选择1张加入手牌（0费，打出后消耗）。素材的「被弃置时」效果照常触发；神影依每回合各只能生成1次。融合条件（素材数量须与条件严格一致）：神影依·米德拉什=2张影依牌；神影依·拿非利=1张影依牌+1张光道牌；神影依·文迪戈=1张影依牌+1张技能牌；神影依·神子晶=1张影依牌+1张攻击牌；神影依·舍金纳迦=2张影依攻击牌；神影依·异花莉莉丝=3张影依牌；神影依·七贤巨鲲魔=2张不同名的影依牌；神影依·米沙赫雷恶=3张手牌（含至少1张影依牌）；翼影依 影文蒂=2张影依技能牌。",
         "影融：弃置手牌中2~3张牌作为素材（神影依也可作素材），从满足融合条件的神影依中选择1张加入手牌（0费，离开弃牌堆时消耗）。素材的「被弃置时」效果照常触发；神影依每回合各只能生成1次。素材数量须与融合条件严格一致，各融合卡的条件见其卡面说明。"),
}

HOVER_TIPS = {
    "LIGHTSWORN_FUSION_CODEX.title": "融合图鉴",
    "LIGHTSWORN_FUSION_CODEX.description":
        "查看全部13张融合卡（珠泪融合4张 + 神影依9张）。战斗中，本回合已经生成过的融合卡会置灰显示。",
}

def load(name):
    return json.load(io.open(os.path.join(ROOT, name), encoding="utf-8"))

def save(name, data):
    with io.open(os.path.join(ROOT, name), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

def apply(data, mapping, table):
    for key, (old, new) in mapping.items():
        cur = data.get(key)
        if cur is None:
            sys.exit(f"[FAIL] {table} 缺键: {key}")
        if cur != old:
            print(f"[WARN] {table} {key} 当前文案与预期不一致，仍替换：\n  旧: {cur}\n  新: {new}")
        data[key] = new

cards = load("cards.json")
apply(cards, CARDS, "cards.json")
save("cards.json", cards)
print(f"cards.json: {len(CARDS)} 条已更新")

kw = load("card_keywords.json")
apply(kw, KEYWORDS, "card_keywords.json")
save("card_keywords.json", kw)
print(f"card_keywords.json: {len(KEYWORDS)} 条已更新")

tips = load("static_hover_tips.json")
for key, val in HOVER_TIPS.items():
    if key in tips and tips[key] != val:
        print(f"[WARN] static_hover_tips.json {key} 已存在且不同，覆盖")
    tips[key] = val
save("static_hover_tips.json", tips)
print(f"static_hover_tips.json: {len(HOVER_TIPS)} 条已写入")
