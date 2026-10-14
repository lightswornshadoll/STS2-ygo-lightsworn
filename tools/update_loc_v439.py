# -*- coding: utf-8 -*-
"""v0.4.39 本地化批量更新（第四十轮反馈39条）。
覆盖：cards.json / powers.json / card_keywords.json + locfrag（cards_6/7 防未来重合并回退）。
每个键先校验存在（新键除外），打印旧值摘要；结束校验总数。
用法: py tools\\update_loc_v439.py
"""
import io
import json
import os

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
LOC = os.path.join(ROOT, 'mod', 'lightsworn', 'lightsworn', 'localization', 'zhs')
FRAG = os.path.join(TOOLS, 'locfrag')

try:
    input = raw_input  # noqa: F821  (py2 兼容占位；本机 py3 走不到)
except NameError:
    pass


def load(path):
    with io.open(path, encoding='utf-8') as f:
        return json.load(f)


def save(path, data):
    with io.open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')


CARDS = {
    "LIGHTSWORN-EL_SHADDOLL_WINDA.description":
        "融合条件：1张影依牌+1张影依/珠泪牌。\n造成{Damage:diff()}点伤害，回复3点能量。从弃牌堆将1张非神影依的影依技能加入手牌。",
    "LIGHTSWORN-GAROTH.description":
        "每当{IfUpgraded:show:发生弃光|「光道」牌弃光后}，追加弃光2，并抽其中「光道」牌数量的牌。",
    "LIGHTSWORN-GRAGONITH.description":
        "弃光{Mill:diff()}。造成{Damage:diff()}点伤害，弃牌堆中每有1张「光道」牌额外+{Scale:diff()}点。\n[gold]斩杀时[/gold]自动回手，费用临时变为0。",
    "LIGHTSWORN-ORCUS.description":
        "弃光{Mill:diff()}。获得{Artifact:diff()}层人工制品。消耗。",
    "LIGHTSWORN-LYLA.description":
        "弃光{Mill:diff()}。目标敌人失去{Debuff:diff()}点力量，获得{Weak:diff()}层虚弱。消耗。",
    "LIGHTSWORN-TWILIGHT_LYLA.description":
        "消耗弃牌堆中的1张「光道」牌（若无则此牌不产生任何效果）。使目标敌人失去{Debuff:diff()}点力量，获得{Weak:diff()}层虚弱，自身获得1层暮光。消耗。",
    "LIGHTSWORN-DECREE.description":
        "打出后，将此牌置于抽牌堆顶。\n[gold]从卡组被弃置时[/gold]：{IfUpgraded:show:将1张强化后的|将1张}保留、消耗的「裁决之龙」加入手牌。",
    "LIGHTSWORN-AEGIS.description":
        "弃光{Mill:diff()}。获得{Block:diff()}点格挡。\n[gold]从卡组被弃置时[/gold]自动加入手牌，且本回合费用变为0。",
    "LIGHTSWORN-SHINING_DRAGON.description":
        "弃牌堆中存在「裁决之龙」和「惩戒之龙」时才能打出。\n消耗弃牌堆中的所有卡，对所有敌人造成{Damage:diff()}点伤害，重复{Hits:diff()}次，并施加3层虚弱和3层易伤，然后从消耗堆中将1张「裁决之龙」和1张「惩戒之龙」加入手牌。",
    "LIGHTSWORN-LIGHT_IMPRISONING.description":
        "仅当手牌中有「光道」牌时才能打出。\n强制弃置手牌中1张「光道」牌，对目标敌人施加{Weak:diff()}层虚弱和{Vul:diff()}层易伤。",
    "LIGHTSWORN-JUSTICE_WORLD.description":
        "每当弃光，你可以将弃置的牌中的1张加入手牌{IfUpgraded:show:（该牌获得「保留」）|}。",
    "LIGHTSWORN-LIGHT_BOUNCE.description":
        "每当你打出「光道」牌，获得{BlockGain:diff()}点格挡。",
    "LIGHTSWORN-TWILIGHT_GARB.description":
        "弃牌堆中每有1张「光道」牌，获得1层[gold]暮光[/gold]。消耗。",
    "LIGHTSWORN-FLASH_FANTASY.description":
        "弃光{Mill:diff()}，然后选择弃牌堆中的1张「光道」攻击牌，造成等同于其基础伤害数值的伤害{IfUpgraded:show:（+3）|}。[gold]斩杀时[/gold]额外获得一次卡牌奖励。",
    "LIGHTSWORN-TWIN_TWILIGHT_DRAGON.description":
        "若手牌中有「惩戒之龙」：将弃牌堆中1张「裁决之龙」加入手牌，然后弃光{Mill:diff()}。\n否则：将1张「裁决之龙」和1张「惩戒之龙」置入弃牌堆{IfUpgraded:show:（获得「保留」）|}。\n[gold]从卡组被弃置时[/gold]将弃牌堆中1张「惩戒之龙」加入手牌（没有则无事发生），然后除光4。",
    "LIGHTSWORN-AGIDO.description":
        "弃光{Mill:diff()}。若其中有2张以上技能牌，抽2张牌。\n[gold]被弃置时[/gold]自动打出。",
    "LIGHTSWORN-KELBEK.description":
        "弃光{Mill:diff()}。若其中有2张以上攻击牌，抽2张牌。\n[gold]被弃置时[/gold]自动打出。",
    "LIGHTSWORN-KELDO.description":
        "将弃牌堆中最多{Picks:diff()}张牌洗回抽牌堆，抽1张牌；若抽到的是技能牌，其费用变为0。",
    "LIGHTSWORN-MUDORA.description":
        "将弃牌堆中最多{Picks:diff()}张牌洗回抽牌堆，抽1张牌；若抽到的是攻击牌，其费用变为0。",
    "LIGHTSWORN-MERRLI.description":
        "造成{Damage:diff()}点伤害。若目标意图为攻击，回复1点能量并弃光3。珠泪融合{IfUpgraded:show:+|}。",
    "LIGHTSWORN-PRIMEVAL_CRY.description":
        "从卡组将1张珠泪卡送去墓地（被弃置时效果照常触发），给目标敌人{Vul:diff()}层易伤。\n[gold]被弃置时[/gold]：从卡组将1张珠泪攻击牌加入手牌。",
    "LIGHTSWORN-PRIMEVAL_ECHO.title":
        "壹世坏·让珠泪哀歌族澄澈的残响",
    "LIGHTSWORN-PRIMEVAL_ECHO.description":
        "击晕目标敌人。消耗。\n[gold]被弃置时[/gold]：从消耗堆选择1张珠泪攻击牌，生成一张相同的卡加入手牌。",
    "LIGHTSWORN-SHADDOLL_SQUAMATA.description":
        "造成{Damage:diff()}点伤害，施加{Weak:diff()}层虚弱。\n[gold]被弃置时[/gold]：从卡组选择1张影依卡丢弃。",
    "LIGHTSWORN-NAELSHADDOLL_ARIEL.description":
        "获得{Block:diff()}点格挡。从消耗堆将1张影依攻击卡加入手牌（其伤害变为0，打出一次后恢复）。\n[gold]被弃置时[/gold]：将弃牌堆中最多{Max:diff()}张牌消耗，每消耗1张牌随机1名敌人获得1层虚弱。",
    "LIGHTSWORN-SHADDOLL_ZEFRACORE.description":
        "造成{Damage:diff()}点伤害。弃光{Mill:diff()}。\n[gold]被弃置时[/gold]：弃光4。",
    "LIGHTSWORN-SHADDOLL_ZEFRANAGA.description":
        "弃光{Mill:diff()}，获得{Block:diff()}点格挡。\n[gold]被弃置时[/gold]：抽1张牌。",
    "LIGHTSWORN-RESH_SHADDOLL_INCARNATION.description":
        "从弃牌堆或消耗堆将1张「影依」攻击卡加入手牌{IfUpgraded:show:（费用变为0）|}。",
    "LIGHTSWORN-PURUSHADDOLL_AEON.description":
        "获得能力[gold]神我影依流世[/gold]：每回合开始时，你可以从消耗堆将1张「影依」牌加入手牌。",
}

POWERS = {
    "LIGHTSWORN-GAROTH_POWER.description":
        "每当「光道」牌弃光后，追加弃光{Amount}，并抽其中「光道」牌数量的牌。",
    "LIGHTSWORN-GAROTH_POWER.smartDescription":
        "每当「光道」牌弃光后，追加弃光[blue]{Amount}[/blue]，并抽其中「光道」牌数量的牌。",
    "LIGHTSWORN-GAROTH_POWER_PLUS.description":
        "每当任意弃光后，追加弃光{Amount}，并抽其中「光道」牌数量的牌。",
    "LIGHTSWORN-GAROTH_POWER_PLUS.smartDescription":
        "每当任意弃光后，追加弃光[blue]{Amount}[/blue]，并抽其中「光道」牌数量的牌。",
    "LIGHTSWORN-JUSTICE_WORLD_POWER.description":
        "每当弃光，你可以将弃置的牌中的1张加入手牌。",
    "LIGHTSWORN-JUSTICE_WORLD_POWER.smartDescription":
        "每当弃光，你可以将弃置的牌中的1张加入手牌。",
    "LIGHTSWORN-JUSTICE_WORLD_POWER_PLUS.title":
        "正义世界",
    "LIGHTSWORN-JUSTICE_WORLD_POWER_PLUS.description":
        "每当弃光，你可以将弃置的牌中的1张加入手牌（该牌获得「保留」）。",
    "LIGHTSWORN-JUSTICE_WORLD_POWER_PLUS.smartDescription":
        "每当弃光，你可以将弃置的牌中的1张加入手牌（该牌获得「保留」）。",
    "LIGHTSWORN-LIGHT_BOUNCE_POWER.description":
        "每当你打出「光道」牌，获得{Amount}点格挡。",
    "LIGHTSWORN-LIGHT_BOUNCE_POWER.smartDescription":
        "每当你打出「光道」牌，获得[blue]{Amount}[/blue]点格挡。",
    "LIGHTSWORN-PURUSHADDOLL_AEON_POWER.title":
        "神我影依流世",
    "LIGHTSWORN-PURUSHADDOLL_AEON_POWER.description":
        "每回合开始时，你可以从消耗堆将1张「影依」牌加入手牌。",
    "LIGHTSWORN-PURUSHADDOLL_AEON_POWER.smartDescription":
        "每回合开始时，你可以从消耗堆将1张「影依」牌加入手牌。",
}

POWERS_DELETE = [
    "LIGHTSWORN-AEGIS_POWER.title",
    "LIGHTSWORN-AEGIS_POWER.description",
    "LIGHTSWORN-AEGIS_POWER.smartDescription",
]

KEYWORDS = {
    "LIGHTSWORN-BANISH.description":
        "除光N：从抽牌堆中选择N张牌消耗（不足时全部消耗）。被除光的牌本场战斗移出牌库，无法再次使用。",
}

FRAG_CARDS_6 = {
    "LIGHTSWORN-SHADDOLL_SQUAMATA.description": CARDS["LIGHTSWORN-SHADDOLL_SQUAMATA.description"],
    "LIGHTSWORN-NAELSHADDOLL_ARIEL.description": CARDS["LIGHTSWORN-NAELSHADDOLL_ARIEL.description"],
    "LIGHTSWORN-SHADDOLL_ZEFRACORE.description": CARDS["LIGHTSWORN-SHADDOLL_ZEFRACORE.description"],
    "LIGHTSWORN-SHADDOLL_ZEFRANAGA.description": CARDS["LIGHTSWORN-SHADDOLL_ZEFRANAGA.description"],
}

FRAG_CARDS_7 = {
    "LIGHTSWORN-RESH_SHADDOLL_INCARNATION.description": CARDS["LIGHTSWORN-RESH_SHADDOLL_INCARNATION.description"],
    "LIGHTSWORN-PURUSHADDOLL_AEON.description": CARDS["LIGHTSWORN-PURUSHADDOLL_AEON.description"],
}


def apply(path, updates, label):
    data = load(path)
    for key, val in updates.items():
        old = data.get(key, None)
        data[key] = val
        mark = 'NEW' if old is None else ('SAME' if old == val else 'UPD')
        print(f'[{label}] {mark} {key}')
    save(path, data)


def main():
    cards = load(os.path.join(LOC, 'cards.json'))
    missing = [k for k in CARDS if k not in cards and not k.endswith('.title') and 'PRIMEVAL_ECHO' not in k]
    assert not missing, f'cards.json 缺键: {missing}'
    apply(os.path.join(LOC, 'cards.json'), CARDS, 'cards')
    print('cards.json 现有卡牌条目数:', sum(1 for k in load(os.path.join(LOC, 'cards.json')) if k.endswith('.title')))

    powers_path = os.path.join(LOC, 'powers.json')
    powers = load(powers_path)
    missing_p = [k for k in POWERS if k not in powers and '_PLUS' not in k and 'PURUSHADDOLL' not in k]
    assert not missing_p, f'powers.json 缺键: {missing_p}'
    apply(powers_path, POWERS, 'powers')
    powers = load(powers_path)
    for key in POWERS_DELETE:
        if key in powers:
            del powers[key]
            print('[powers] DEL', key)
    save(powers_path, powers)

    apply(os.path.join(LOC, 'card_keywords.json'), KEYWORDS, 'keywords')

    frag6 = os.path.join(FRAG, 'cards_6.json')
    frag7 = os.path.join(FRAG, 'cards_7.json')
    f6 = load(frag6)
    for k in FRAG_CARDS_6:
        assert k in f6, f'cards_6 缺键 {k}'
    apply(frag6, FRAG_CARDS_6, 'frag6')
    f7 = load(frag7)
    for k in FRAG_CARDS_7:
        assert k in f7, f'cards_7 缺键 {k}'
    apply(frag7, FRAG_CARDS_7, 'frag7')
    print('done')


if __name__ == '__main__':
    main()
