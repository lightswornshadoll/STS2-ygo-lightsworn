import json, io, os

base = r'D:\1-workdata\lightsworn_mod\mod\lightsworn\lightsworn\localization\zhs'
cj = os.path.join(base, 'cards.json')
data = json.load(io.open(cj, encoding='utf-8'))
for k in sorted(data):
    if k.startswith('LIGHTSWORN-GAROTH.') or k.startswith('LIGHTSWORN-LUMINA.'):
        print(k, '=>', data[k])

cards = {
    'LIGHTSWORN-REINFORCE.description':
        '弃光{Mill:diff()}。将抽牌堆或弃牌堆中的1张「光道」牌加入手牌（本回合费用为0）。',
    'LIGHTSWORN-LIGHTSWORN_DRAGON.description':
        '弃牌堆中存在「光道」牌时才能打出。从手牌或抽牌堆中选择{Dump:diff()}张「光道」牌弃置，然后造成{Damage:diff()}点伤害。\n[gold]从卡组被弃置时[/gold]：若抽牌堆中有「裁决之龙」或「惩戒之龙」，选择1张加入手牌。',
    'LIGHTSWORN-MAIDEN_MINERVA.description':
        '弃光{Mill:diff()}。若弃牌堆中的「光道」种类不少于{Tier1:diff()}种，从已达挡位的龙中选择1条加入手牌：「光道之龙」；{Tier2:diff()}种以上：光道龙 格拉古尼斯；{Tier3:diff()}种以上：裁决之龙。\n[gold]从卡组被弃置时[/gold]：弃光1。',
    'LIGHTSWORN-EHREN.description':
        '弃光{Mill:diff()}。造成{Damage:diff()}点伤害。若目标有格挡，则不造成伤害，改为清除其所有格挡。若弃置了「光道」牌，抽1张牌。',
    'LIGHTSWORN-WEISS.description':
        '将手牌中{Back:diff()}张「光道」牌置于抽牌堆顶，然后弃光{Mill:diff()}。\n[gold]从卡组被弃置时[/gold]：将弃牌堆中1张「光道恶魔」以外的「光道」牌加入手牌，其费用临时变为0。',
    'LIGHTSWORN-LUMINA.description':
        '弃光{Mill:diff()}。弃置1张手牌，然后从弃牌堆中将{Picks:diff()}张牌加入手牌（本回合费用为0）。',
    'LIGHTSWORN-FELIS.description':
        '弃光{Mill:diff()}。获得{Block:diff()}点格挡；若弃置了「光道」牌，额外+{Bonus:diff()}。\n[gold]从卡组被弃置时[/gold]自动加入手牌。只有通过抽牌以外的方式入手时才能打出。',
    'LIGHTSWORN-MUDORA.description':
        '弃光{Mill:diff()}。获得{Block:diff()}点格挡；若弃置了「地天使」牌，额外+{Bonus:diff()}。',
    'LIGHTSWORN-GAROTH.description':
        '每当「光道」牌弃光后，追加弃光2。强化后：追加弃光2，并抽其中「光道」牌数量的牌。',
}

powers = {
    'LIGHTSWORN-GAROTH_POWER.description':
        '每当「光道」牌弃光后，弃光{Amount}。',
    'LIGHTSWORN-GAROTH_POWER.smartDescription':
        '每当「光道」牌弃光后，弃光[blue]{Amount}[/blue]。',
    'LIGHTSWORN-GAROTH_POWER_PLUS.title':
        '光道的连锁',
    'LIGHTSWORN-GAROTH_POWER_PLUS.description':
        '每当「光道」牌弃光后，弃光{Amount}，并抽其中「光道」牌数量的牌。',
    'LIGHTSWORN-GAROTH_POWER_PLUS.smartDescription':
        '每当「光道」牌弃光后，弃光[blue]{Amount}[/blue]，并抽其中「光道」牌数量的牌。',
}


def apply(fname, updates, create_ok=False):
    p = os.path.join(base, fname)
    data = json.load(io.open(p, encoding='utf-8'))
    missing = [k for k in updates if k not in data]
    for k, v in updates.items():
        data[k] = v
    io.open(p, 'w', encoding='utf-8', newline='\n').write(
        json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    print(fname, 'updated,', len(updates), 'keys, new keys:', missing)


apply('cards.json', cards)
apply('powers.json', powers)
