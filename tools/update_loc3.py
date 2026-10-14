import json, io, os

base = r'D:\1-workdata\lightsworn_mod\mod\lightsworn\lightsworn\localization\zhs'
paths = {
    'cards.json': {
        'LIGHTSWORN-REINFORCE.description':
            '弃光{Mill:diff()}。从卡组中将1张「光道」牌加入手牌（本回合费用为0）。',
        'LIGHTSWORN-TWILIGHT_LUMINA.description':
            '消耗弃牌堆中的1张「光道」牌（若有），将消耗堆中的1张「光道」牌加入手牌（费用变为0）。获得{Twilight:diff()}层暮光。',
        'LIGHTSWORN-LIGHT_BOUNCE.description':
            '每当你的牌从抽牌堆被弃置时（无论几张都算1次弃牌），对所有敌人施加{Doom:diff()}层「灾厄」。',
    },
    'powers.json': {
        'LIGHTSWORN-LIGHT_BOUNCE_POWER.description':
            '每当你的牌从抽牌堆被弃置时（无论几张都算1次弃牌），对所有敌人施加{Amount}层灾厄（不限「光道」牌）。',
        'LIGHTSWORN-LIGHT_BOUNCE_POWER.smartDescription':
            '每当你的牌从抽牌堆被弃置时（无论几张都算1次弃牌），对所有敌人施加[blue]{Amount}[/blue]层灾厄（不限「光道」牌）。',
    },
}

for fname, updates in paths.items():
    p = os.path.join(base, fname)
    data = json.load(io.open(p, encoding='utf-8'))
    for k, v in updates.items():
        if k not in data:
            print(f'!! MISSING KEY {k} in {fname}')
            continue
        print(f'{fname}: {k}\n  旧: {data[k]}\n  新: {v}')
        data[k] = v
    io.open(p, 'w', encoding='utf-8').write(
        json.dumps(data, ensure_ascii=False, indent=2) + '\n')
print('done')
