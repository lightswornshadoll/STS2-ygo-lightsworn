"""v0.6.2：光道龙/光道圣灵 改动态数值显示（完美打击范式）。

用法: py tools\\update_loc_v062.py
"""
import io
import json
import os

here = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(here, '..', 'mod', 'lightsworn', 'lightsworn', 'localization', 'zhs', 'cards.json')
cards = json.load(io.open(path, encoding='utf-8'))

updates = {
    # 完美打击句式：第一个数=当前总值（随弃牌堆光道数实时变化），第二个数=每张加成
    'LIGHTSWORN_CARD_GRAGONITH.description':
        '造成{CalculatedDamage:diff()}点伤害。弃牌堆中每有1张「光道」牌，伤害+{ExtraDamage:diff()}。\n'
        '[gold]斩杀时[/gold]自动回手，费用临时变为0。',
    'LIGHTSWORN_CARD_SHIRE.description':
        '获得{CalculatedBlock:diff()}点格挡。弃牌堆中每有1张「光道」牌，格挡+{CalculationExtra:diff()}。',
}

for key, value in updates.items():
    assert key in cards, f'missing key: {key}'
    cards[key] = value

with io.open(path, 'w', encoding='utf-8') as f:
    json.dump(cards, f, ensure_ascii=False, indent=2)
    f.write('\n')
print(f'updated {len(updates)} keys')
