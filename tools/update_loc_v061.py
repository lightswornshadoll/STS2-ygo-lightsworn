"""v0.6.1 已知问题 14 条的本地化更新。

只改 cards.json / powers.json（zhs），保持 ensure_ascii=False + indent=2。
用法: py tools\\update_loc_v061.py
"""
import io
import json
import os

here = os.path.dirname(os.path.abspath(__file__))
base = os.path.join(here, '..', 'mod', 'lightsworn', 'lightsworn', 'localization', 'zhs')

cards_path = os.path.join(base, 'cards.json')
powers_path = os.path.join(base, 'powers.json')

cards = json.load(io.open(cards_path, encoding='utf-8'))
powers = json.load(io.open(powers_path, encoding='utf-8'))

CARD_UPDATES = {
    # 问题13：文本"光道牌被弃光"→"光道牌弃光"（=光道牌发动弃光；行为不变，代码=来源为光道牌）
    'LIGHTSWORN_CARD_GAROTH.description':
        '每当「光道」牌[gold]弃光[/gold]后，追加[gold]弃光[/gold]2'
        '{IfUpgraded:show:，并抽其中「光道」牌数量的牌|}。',

    # 问题7：光道恶魔 魏丝追加 8/12 格挡
    'LIGHTSWORN_CARD_WEISS.description':
        '将手牌中{Back:diff()}张「光道」牌置于抽牌堆顶，获得{Block:diff()}点格挡，然后[gold]弃光[/gold]{Mill:diff()}。\n'
        '[gold]从卡组被弃置时[/gold]：将弃牌堆中1张「光道恶魔」以外的「光道」牌加入手牌，其费用临时变为0。',

    # 问题12：裁决之龙Token去掉「保留」（敲后的裁决之龙自带保留）
    'LIGHTSWORN_CARD_DECREE.description':
        '打出后，将此牌置于抽牌堆顶。\n'
        '[gold]从卡组被弃置时[/gold]：将1张消耗的「裁决之龙{IfUpgraded:show:+|}」加入手牌。',

    # 问题9：必须手牌有光道才能打出 → 弃置步骤不会再"若有"
    'LIGHTSWORN_CARD_SOLAR_EXCHANGE.description':
        '仅当手牌中有「光道」牌时才能打出。\n'
        '将手牌中1张「光道」牌弃置。抽{Cards:diff()}张牌。[gold]弃光[/gold]{Mill:diff()}。',

    # 问题10：人工制品本来就能挡，不需要括号
    'LIGHTSWORN_CARD_PUNISH_DRAGON.description':
        '消耗堆中存在4种以上「光道」牌时才能打出。\n'
        '将弃牌堆与消耗堆中所有非「光道」的攻击、技能、能力牌返回卡组，每有一张，所有敌人随机获得1层负面状态。'
        '造成{Damage:diff()}点伤害，并获得1层[gold]暮光[/gold]。',

    # 问题11：影融消耗弃牌堆素材本来就不触发被弃置时效果，不需要括号
    'LIGHTSWORN_CARD_TOHUSHADDOLL_GRYSTA.description':
        '造成{Damage:diff()}点伤害。从弃牌堆将1张影依攻击卡加入手牌，本回合其费用变为0，其伤害变为0（打出一次后恢复）。\n'
        '[gold]被弃置时[/gold]：发动影融{IfUpgraded:show:+|}——从弃牌堆选2张「影依」牌消耗，融合1张神影依加入手牌。',

    # 问题14：重放本身就是额外打出X次，不需要括号解释
    'LIGHTSWORN_CARD_EL_SHADDOLL_FUSION.description':
        '影融{IfUpgraded:show:+|}，且本次融合生成的神影依获得1次[gold]重放[/gold]。',

    # 问题3：四神将改为诅咒卡，打出时伤害指向自己
    'LIGHTSWORN_CARD_DARK_WORLD_KELT.description':
        '打出时：对自己造成{Damage:diff()}点伤害。\n'
        '[gold]从手牌被弃置时[/gold]：对自己造成12点伤害。',
    'LIGHTSWORN_CARD_DARK_WORLD_LATINUM.description':
        '打出时：对自己造成{Damage:diff()}点伤害。\n'
        '[gold]从手牌被弃置时[/gold]：龙神王获得3点力量。',
    'LIGHTSWORN_CARD_DARK_WORLD_SILLVA.description':
        '打出时：对自己造成{Damage:diff()}点伤害。\n'
        '[gold]从手牌被弃置时[/gold]：随机将2张手牌洗入抽牌堆。',
    'LIGHTSWORN_CARD_DARK_WORLD_GOLDD.description':
        '打出时：对自己造成{Damage:diff()}点伤害。\n'
        '[gold]从手牌被弃置时[/gold]：对自己施加1层虚弱和1层易伤。',
}

for key, value in CARD_UPDATES.items():
    assert key in cards, f'cards.json missing key: {key}'
    cards[key] = value

# 问题5：暗黑界的诱惑同样响应弃光
temptation = (
    '每玩家回合第一次弃置或弃光卡牌时，根据第一张牌的类型触发：'
    '攻击→获得1点力量；技能→洗入1张「暗黑界的洗脑」；能力→随机弃置2张手牌；'
    '其他→复制1张同名牌洗入抽牌堆。然后，将1张随机暗黑界诅咒卡洗入其抽牌堆。'
    '回合结束的手牌清理不触发。'
)
temptation_smart = (
    '每玩家回合第一次弃置或弃光卡牌时，根据第一张牌的类型触发：'
    '攻击→获得1点力量；技能→洗入1张「暗黑界的洗脑」；能力→随机弃置2张手牌；'
    '其他→复制1张同名牌洗入抽牌堆。然后，将1张随机暗黑界诅咒卡洗入其抽牌堆。'
    '回合结束的手牌清理不触发。'
)

POWER_UPDATES = {}
for prefix in ('LIGHTSWORN_POWER_DARK_WORLD_TEMPTATION_POWER', 'DARK_WORLD_TEMPTATION_POWER'):
    POWER_UPDATES[f'{prefix}.description'] = temptation
    POWER_UPDATES[f'{prefix}.smartDescription'] = temptation_smart

for key, value in POWER_UPDATES.items():
    assert key in powers, f'powers.json missing key: {key}'
    powers[key] = value

with io.open(cards_path, 'w', encoding='utf-8') as f:
    json.dump(cards, f, ensure_ascii=False, indent=2)
    f.write('\n')
with io.open(powers_path, 'w', encoding='utf-8') as f:
    json.dump(powers, f, ensure_ascii=False, indent=2)
    f.write('\n')

print(f'cards.json updated: {len(CARD_UPDATES)} keys')
print(f'powers.json updated: {len(POWER_UPDATES)} keys')
