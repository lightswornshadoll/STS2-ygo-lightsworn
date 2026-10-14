import json, io

# 第八轮反馈（v0.4.8）文案：雷光/暮雷光/抹杀/放逐 移除增益→虚弱易伤；裁决Token入手牌；米迦勒措辞；珍妮丝回血→格挡；新增神光之龙
cards_path = r'mod\lightsworn\lightsworn\localization\zhs\cards.json'
powers_path = r'mod\lightsworn\lightsworn\localization\zhs\powers.json'

cards = json.load(io.open(cards_path, encoding='utf-8'))
powers = json.load(io.open(powers_path, encoding='utf-8'))

def rep(d, key, old, new):
    assert key in d, f'missing {key}'
    if new in d[key]:
        return
    assert old in d[key], f'{key}: pattern not found: {old}'
    d[key] = d[key].replace(old, new)

rep(cards, 'LIGHTSWORN-RYKO.description',
    '移除目标敌人的{Strip:diff()}个随机增益。', '目标敌人获得1层虚弱和1层易伤。')
rep(cards, 'LIGHTSWORN-TWILIGHT_RYKO.description',
    '移除目标敌人的{Strip:diff()}个随机增益，获得1层暮光。', '对目标敌人施加1层虚弱和1层易伤，自身获得1层暮光。')
rep(cards, 'LIGHTSWORN-DECREE.description',
    '{IfUpgraded:show:将2张|将1张}虚无、消耗的「裁决之龙」加入弃牌堆。',
    '{IfUpgraded:show:将1张强化后的|将1张}虚无、消耗的「裁决之龙」加入手牌。')
rep(cards, 'LIGHTSWORN-MICHAEL.description',
    '「光道」牌全部洗回抽牌堆，每洗回1张获得3点格挡。', '「光道」牌全部加入抽牌堆，每回收1张获得3点格挡。')
rep(cards, 'LIGHTSWORN-LIGHT_IMPRISONING.description',
    '消耗手牌中的1张「光道」牌（若有）。移除目标敌人的所有增益，并施加{Weak:diff()}层虚弱。',
    '丢弃手牌中的1张「光道」牌（若有）。对目标敌人施加{Weak:diff()}层虚弱。')
rep(cards, 'LIGHTSWORN-TWILIGHT_ERASURE.description',
    '每消耗1张移除目标敌人1个随机增益。', '每消耗1张对目标敌人施加1层虚弱和1层易伤。')

cards['LIGHTSWORN-SHINING_DRAGON.title'] = '神光之龙'
cards['LIGHTSWORN-SHINING_DRAGON.description'] = (
    '弃牌堆中存在「裁决之龙」和「惩戒之龙」时才能打出。\n'
    '消耗弃牌堆中的所有卡，对所有敌人造成{Damage:diff()}点伤害并施加3层虚弱和3层易伤，'
    '然后从消耗堆中将1张「裁决之龙」和1张「惩戒之龙」加入手牌。')

rep(powers, 'LIGHTSWORN-JANICE_POWER.description',
    '回合结束时回复{Amount}点生命', '回合结束时获得{Amount}点格挡')
rep(powers, 'LIGHTSWORN-JANICE_POWER.smartDescription',
    '回合结束时回复[blue]{Amount}[/blue]点生命', '回合结束时获得[blue]{Amount}[/blue]点格挡')

for path, d in [(cards_path, cards), (powers_path, powers)]:
    io.open(path, 'w', encoding='utf-8').write(
        json.dumps(d, ensure_ascii=False, indent=2) + '\n')
print('loc updated')
print('SHINING_DRAGON:', cards['LIGHTSWORN-SHINING_DRAGON.description'])
