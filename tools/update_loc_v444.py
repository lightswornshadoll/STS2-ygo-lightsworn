# -*- coding: utf-8 -*-
"""v0.4.44 订正3条本地化更新：炎核（被弃置时弃光X、主动效果恢复原样）/ 绊影依·救影依去掉被弃置效果。
（光道龙文案靠 {Damage:diff()}/{Scale:diff()} 自动渲染，无需改文案）
用法: py tools\\update_loc_v444.py
"""
import io
import json
import os

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
LOC = os.path.join(ROOT, 'mod', 'lightsworn', 'lightsworn', 'localization', 'zhs')

CARDS = {
    # 炎核：主动效果恢复"从卡组弃置1张影依攻击卡→虚弱易伤"；被弃置时 弃光4 → 弃光X
    "LIGHTSWORN-HELSHADDOLL_HOLLOW.description":
        "造成{Damage:diff()}点伤害。可以从卡组弃置1张影依攻击卡，若如此做，对目标施加1层虚弱和易伤。\n[gold]被弃置时[/gold]：弃光X（X=手牌中不同名「神影依」的数量+1）。",
    # 绊影依：去掉被弃置时效果
    "LIGHTSWORN-SHADDOLL_ZEFRACORE.description":
        "获得能力[gold]绊影依-神数原核[/gold]：每回合开始时，从「影依的炎核 虚梦狱」「虚影依 神子晶」「神影依·神子晶」中随机生成1张加入手牌，其获得「消耗」。",
    # 救影依：去掉被弃置时效果
    "LIGHTSWORN-SHADDOLL_ZEFRANAGA.description":
        "获得能力[gold]救影依-神数纳迦[/gold]：每回合开始时，从「圣影依 商神杖灵」「联结之影依化身」「影依的伪典」中随机生成1张加入手牌，其获得「消耗」。",
}


def main():
    cards_path = os.path.join(LOC, 'cards.json')
    cards = json.load(io.open(cards_path, encoding='utf-8'))
    for k, v in CARDS.items():
        assert k in cards, f'cards.json 缺键 {k}'
        old = cards[k]
        cards[k] = v
        print('UPD' if old != v else 'SAME', k)
    with io.open(cards_path, 'w', encoding='utf-8') as f:
        json.dump(cards, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print('done')


if __name__ == '__main__':
    main()
