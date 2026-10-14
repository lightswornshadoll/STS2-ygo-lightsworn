# -*- coding: utf-8 -*-
"""v0.4.43 本轮反馈17条本地化更新（雷喵/莱登/暮将军/交衣/古尖兵古卫兵/影依兽集/绊影依救影依/加洛斯/卡雷多哈特）。
覆盖：cards.json / powers.json（新增3能力词条、更新加洛斯双词条）。
用法: py tools\\update_loc_v443.py
"""
import io
import json
import os

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
LOC = os.path.join(ROOT, 'mod', 'lightsworn', 'lightsworn', 'localization', 'zhs')


def load(path):
    with io.open(path, encoding='utf-8') as f:
        return json.load(f)


def save(path, data):
    with io.open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')


CARDS = {
    # 1 光之回弹：仅稀有度（调蓝），文案不动
    # 2 炎核：弃光X（手牌中神影依种类+1）
    "LIGHTSWORN-HELSHADDOLL_HOLLOW.description":
        "造成{Damage:diff()}点伤害。弃光X（X=手牌中不同名「神影依」的数量+1）。\n[gold]被弃置时[/gold]：弃光4。",
    # 3 莱登：弃到光道→本回合临时力量2
    "LIGHTSWORN-LAYDEN.description":
        "弃光{Mill:diff()}。造成{Damage:diff()}点伤害；若弃置了「光道」牌，在本回合结束前获得{Temp:diff()}点[gold]力量[/gold]。",
    # 4 光道天使：仅稀有度（进白）
    # 5 影依兽：仅稀有度（升蓝）
    # 6 绊影依：2费能力重做
    "LIGHTSWORN-SHADDOLL_ZEFRACORE.description":
        "获得能力[gold]绊影依-神数原核[/gold]：每回合开始时，从「影依的炎核 虚梦狱」「虚影依 神子晶」「神影依·神子晶」中随机生成1张加入手牌，其获得「消耗」。\n[gold]被弃置时[/gold]：从弃牌堆将1张影依牌置于抽牌堆顶。",
    # 7 救影依：2费能力重做
    "LIGHTSWORN-SHADDOLL_ZEFRANAGA.description":
        "获得能力[gold]救影依-神数纳迦[/gold]：每回合开始时，从「圣影依 商神杖灵」「联结之影依化身」「影依的伪典」中随机生成1张加入手牌，其获得「消耗」。\n[gold]被弃置时[/gold]：抽1张牌。",
    # 8 古尖兵古卫兵：每3张对应类型牌抽1
    "LIGHTSWORN-AGIDO.description":
        "弃光{Mill:diff()}。其中每有3张技能牌，抽1张牌。\n[gold]被弃置时[/gold]自动打出。",
    "LIGHTSWORN-KELBEK.description":
        "弃光{Mill:diff()}。其中每有3张攻击牌，抽1张牌。\n[gold]被弃置时[/gold]自动打出。",
    # 9 雷喵：0费/回墓地/回费/消耗
    "LIGHTSWORN-RINYAN.description":
        "从弃牌堆将最多{Picks:diff()}张「光道」牌洗回抽牌堆，每有1种不同名的「光道」牌，获得1点费用。消耗。",
    # 10 光道龙：仅数值（基础18/敲后22，文案变量自动）
    # 11 加洛斯：回调初版（敲前只追加弃光，敲后追加+抽）
    "LIGHTSWORN-GAROTH.description":
        "每当「光道」牌弃光后，追加弃光2{IfUpgraded:show:，并抽其中「光道」牌数量的牌|}。",
    # 13 暮光道将军：1费打9/12 + 可选消耗光道额外5/7
    "LIGHTSWORN-TWILIGHT_JAIN.description":
        "造成{Damage:diff()}点伤害；可以消耗弃牌堆中的1张「光道」牌，若如此做，额外造成{Bonus:diff()}点伤害。获得1层[gold]暮光[/gold]。",
    # 15 羽影依：被弃置效果与打出相同
    "LIGHTSWORN-REESHADDOLL_WENDI.description":
        "造成{Damage:diff()}点伤害。从卡组将1张影依攻击卡加入手牌，本回合其费用变为0，其伤害变为0（打出一次后恢复）。\n[gold]被弃置时[/gold]：和打出时效果相同（回收的牌同样费用变为0、伤害变为0）。",
    # 16 交衣：追加被从卡组弃置时的临时回弹
    "LIGHTSWORN-TWILIGHT_GARB.description":
        "弃牌堆中每有1张「光道」牌，获得1层[gold]暮光[/gold]。消耗。\n[gold]被从卡组弃置时[/gold]：在本回合结束前，每当你打出「光道」牌，获得{Guard:diff()}点格挡。",
    # 17 卡雷多哈特：本场战斗只能生成1次（同文迪戈）
    "LIGHTSWORN-KALEIDO_HEART.description":
        "融合条件：含「珠泪哀歌族 雷诺哈特」的3张珠泪攻击牌。\n造成{Damage:diff()}点伤害。消耗。若此牌在消耗区，每回合开始时自动将其打出。\n[gold]本场战斗[/gold]此牌只能生成1次。",
}

POWERS = {
    "LIGHTSWORN-GAROTH_POWER.title": "光道的连锁",
    "LIGHTSWORN-GAROTH_POWER.description": "每当「光道」牌弃光后，追加弃光{Amount}。",
    "LIGHTSWORN-GAROTH_POWER.smartDescription": "每当「光道」牌弃光后，追加弃光[blue]{Amount}[/blue]。",
    "LIGHTSWORN-GAROTH_POWER_PLUS.title": "光道的连锁",
    "LIGHTSWORN-GAROTH_POWER_PLUS.description": "每当「光道」牌弃光后，追加弃光{Amount}，并抽其中「光道」牌数量的牌。",
    "LIGHTSWORN-GAROTH_POWER_PLUS.smartDescription": "每当「光道」牌弃光后，追加弃光[blue]{Amount}[/blue]，并抽其中「光道」牌数量的牌。",
    "LIGHTSWORN-SHADDOLL_ZEFRACORE_POWER.title": "绊影依-神数原核",
    "LIGHTSWORN-SHADDOLL_ZEFRACORE_POWER.description": "每回合开始时，从「影依的炎核 虚梦狱」「虚影依 神子晶」「神影依·神子晶」中随机生成1张加入手牌，其获得「消耗」。",
    "LIGHTSWORN-SHADDOLL_ZEFRACORE_POWER.smartDescription": "每回合开始时，从「影依的炎核 虚梦狱」「虚影依 神子晶」「神影依·神子晶」中随机生成1张加入手牌，其获得「消耗」。",
    "LIGHTSWORN-SHADDOLL_ZEFRANAGA_POWER.title": "救影依-神数纳迦",
    "LIGHTSWORN-SHADDOLL_ZEFRANAGA_POWER.description": "每回合开始时，从「圣影依 商神杖灵」「联结之影依化身」「影依的伪典」中随机生成1张加入手牌，其获得「消耗」。",
    "LIGHTSWORN-SHADDOLL_ZEFRANAGA_POWER.smartDescription": "每回合开始时，从「圣影依 商神杖灵」「联结之影依化身」「影依的伪典」中随机生成1张加入手牌，其获得「消耗」。",
    "LIGHTSWORN-TWILIGHT_GARB_POWER.title": "黄昏之交衣",
    "LIGHTSWORN-TWILIGHT_GARB_POWER.description": "本回合内，每当你打出「光道」牌，获得{Amount}点格挡。",
    "LIGHTSWORN-TWILIGHT_GARB_POWER.smartDescription": "本回合内，每当你打出「光道」牌，获得[blue]{Amount}[/blue]点格挡。",
}


def main():
    cards_path = os.path.join(LOC, 'cards.json')
    cards = load(cards_path)
    for k, v in CARDS.items():
        assert k in cards, f'cards.json 缺键 {k}'
        old = cards[k]
        cards[k] = v
        print('UPD' if old != v else 'SAME', k)
    save(cards_path, cards)

    p_path = os.path.join(LOC, 'powers.json')
    powers = load(p_path)
    for k, v in POWERS.items():
        if k not in powers:
            print('ADD', k)
        else:
            print('UPD' if powers[k] != v else 'SAME', k)
        powers[k] = v
    save(p_path, powers)
    print('done')


if __name__ == '__main__':
    main()
