# -*- coding: utf-8 -*-
"""v0.4.40 订正4条本地化更新（正义世界敲后自保留 / 残响锁说明 / 绊影依重做 / 埃癸斯盾被弃置）。
覆盖：cards.json / powers.json（删 JUSTICE_WORLD_POWER_PLUS）。
用法: py tools\\update_loc_v440.py
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
    "LIGHTSWORN-JUSTICE_WORLD.description":
        "每当弃光，你可以将弃置的牌中的1张加入手牌。",
    "LIGHTSWORN-SHADDOLL_ZEFRACORE.description":
        "造成{Damage:diff()}点伤害。弃光{Mill:diff()}。\n[gold]被弃置时[/gold]：从弃牌堆将1张影依牌置于抽牌堆顶。",
    "LIGHTSWORN-AEGIS.description":
        "弃光{Mill:diff()}。获得{Block:diff()}点格挡。\n[gold]被弃置时[/gold]自动加入手牌，且本回合费用变为0。",
    "LIGHTSWORN-PRIMEVAL_ECHO.description":
        "击晕目标敌人。消耗。\n[gold]被弃置时[/gold]：从消耗堆选择1张珠泪攻击牌，生成一张相同的卡加入手牌（若为融合生成的卡，本回合不能再融合出对应的融合卡）。",
}

POWERS_DELETE = [
    "LIGHTSWORN-JUSTICE_WORLD_POWER_PLUS.title",
    "LIGHTSWORN-JUSTICE_WORLD_POWER_PLUS.description",
    "LIGHTSWORN-JUSTICE_WORLD_POWER_PLUS.smartDescription",
]


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
    for k in POWERS_DELETE:
        if k in powers:
            del powers[k]
            print('DEL', k)
    save(p_path, powers)
    print('done')


if __name__ == '__main__':
    main()
