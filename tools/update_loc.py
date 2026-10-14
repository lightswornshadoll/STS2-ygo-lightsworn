import json, io, os

base = r'D:\1-workdata\lightsworn_mod\mod\lightsworn\lightsworn\localization\zhs'

cards = {
    'LIGHTSWORN-SANCTUARY.description':
        '每回合开始时，你可以选择发动：将手牌中1张「光道」牌弃置，然后从弃牌堆将{Take:diff()}张「光道」牌加入手牌。',
    'LIGHTSWORN-REINFORCE.description':
        '从抽牌堆中将1张「光道」牌加入手牌（本回合费用为0）。',
    'LIGHTSWORN-WULF.description':
        '造成{Damage:diff()}点伤害。\n[gold]从卡组被弃置时[/gold]自动加入手牌。只有通过抽牌以外的方式加入手牌时才能打出。',
    'LIGHTSWORN-LIGHTSWORN_DRAGON.description':
        '弃牌堆中存在「光道」牌时才能打出。从抽牌堆中选择{Dump:diff()}张「光道」牌弃置。\n[gold]从卡组被弃置时[/gold]：若抽牌堆中有「裁决之龙」或「惩戒之龙」，选择1张加入手牌。',
    'LIGHTSWORN-WEISS.description':
        '弃光{Mill:diff()}。将手牌中{Back:diff()}张「光道」牌置于抽牌堆顶。\n[gold]从卡组被弃置时[/gold]：将弃牌堆中1张「光道恶魔」以外的「光道」牌加入手牌，其费用临时变为0。',
    'LIGHTSWORN-MAIDEN_MINERVA.description':
        '弃光{Mill:diff()}。若弃牌堆中的「光道」种类不少于{Tier1:diff()}种，将1张「光道之龙」加入手牌；不少于{Tier2:diff()}种，改为「光道龙 格拉古尼斯」；不少于{Tier3:diff()}种，改为「裁决之龙」。\n[gold]从卡组被弃置时[/gold]：弃光1。',
    'LIGHTSWORN-EHREN.description':
        '弃光{Mill:diff()}。造成{Damage:diff()}点伤害。若目标有格挡，则不造成伤害，改为清除其所有格挡，并将此牌置于抽牌堆顶。若弃置了「光道」牌，抽1张牌。',
}

powers = {
    'LIGHTSWORN-SANCTUARY_POWER.description':
        '每回合开始时，你可以选择发动：将手牌中1张「光道」牌弃置，然后从弃牌堆将{Amount}张「光道」牌加入手牌。',
    'LIGHTSWORN-SANCTUARY_POWER.smartDescription':
        '每回合开始时，你可以选择发动：将手牌中1张「光道」牌弃置，然后从弃牌堆将[blue]{Amount}[/blue]张「光道」牌加入手牌。',
}

selection = {
    'LIGHTSWORN_TO_DRAW_TOP': '置于抽牌堆顶',
    'LIGHTSWORN_TO_MILL': '弃置（从抽牌堆选择）',
    'LIGHTSWORN_SANCTUARY_DISCARD': '神域：弃置1张「光道」牌（可不选）',
}


def apply(fname, updates):
    p = os.path.join(base, fname)
    data = json.load(io.open(p, encoding='utf-8'))
    missing = []
    for k, v in updates.items():
        if k not in data:
            missing.append(k)
        data[k] = v
    io.open(p, 'w', encoding='utf-8', newline='\n').write(
        json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    print(fname, 'updated,', len(updates), 'keys, new keys:', missing)


apply('cards.json', cards)
apply('powers.json', powers)
apply('card_selection.json', selection)
