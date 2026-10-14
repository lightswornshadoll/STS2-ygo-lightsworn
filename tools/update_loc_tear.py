import json, io, os

base = r'D:\1-workdata\lightsworn_mod\mod\lightsworn\lightsworn\localization\zhs'

def load(name):
    with io.open(os.path.join(base, name), encoding='utf-8') as f:
        return json.load(f)

def save(name, data):
    with io.open(os.path.join(base, name), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')

# ============ cards.json ============
cards = load('cards.json')
new_cards = {
    'LIGHTSWORN-TRUE_BLOOD_VAMPIRE.title': '真血公',
    'LIGHTSWORN-TRUE_BLOOD_VAMPIRE.description': '造成{Damage:diff()}点伤害。弃光{Mill:diff()}，从本次弃光的牌中选择1张攻击牌加入手牌，其费用变为0。',
    'LIGHTSWORN-HAND_DESTRUCTION.title': '手札抹杀',
    'LIGHTSWORN-HAND_DESTRUCTION.description': '将所有手牌弃置，再抽等量的牌。',
    'LIGHTSWORN-FOOLISH_BURIAL.title': '愚蠢的埋葬',
    'LIGHTSWORN-FOOLISH_BURIAL.description': '从抽牌堆中选择1张牌弃置。',
    'LIGHTSWORN-SULIEK.title': '塞壬人鱼',
    'LIGHTSWORN-SULIEK.description': '造成{Damage:diff()}点伤害。然后可以丢弃1张手牌中的攻击牌：若如此做，回复1点能量并弃光3。',
    'LIGHTSWORN-MERRLI.title': '小美人鱼',
    'LIGHTSWORN-MERRLI.description': '造成{Damage:diff()}点伤害。若目标意图不为攻击，回复1点能量并弃光3。',
    'LIGHTSWORN-HAVNIS.title': '梅洛人鱼',
    'LIGHTSWORN-HAVNIS.description': '造成{Damage:diff()}点伤害，获得{Block:diff()}点格挡。弃光3。',
    'LIGHTSWORN-REINOHART.title': '雷诺哈特',
    'LIGHTSWORN-REINOHART.description': '造成{Damage:diff()}点伤害。从抽牌堆中选择1张珠泪攻击牌弃置。\n[gold]这张卡被弃置时[/gold]：可以丢弃1张手牌中的珠泪攻击牌，若如此做，将它加入手牌（费用变为0）并获得消耗。',
    'LIGHTSWORN-PERLEREINO.title': '珍珠世界',
    'LIGHTSWORN-PERLEREINO.description': '每次发动珠泪融合时，对所有敌人施加1层易伤{IfUpgraded:show:。打出时，从抽牌堆中选择1张珠泪攻击牌加入手牌|}。',
    'LIGHTSWORN-KITKALLOS.title': '水仙女人鱼',
    'LIGHTSWORN-KITKALLOS.description': '从抽牌堆中选择1张珠泪卡加入手牌（费用变为0）。弃光5。造成{Damage:diff()}点伤害。',
    'LIGHTSWORN-RULKALLOS.title': '鲁莎卡人鱼',
    'LIGHTSWORN-RULKALLOS.description': '造成{Damage:diff()}点伤害，若目标为爪牙，伤害翻倍。本回合每打出过1张珠泪卡，获得2点格挡。',
    'LIGHTSWORN-KALEIDO_HEART.title': '卡雷多哈特',
    'LIGHTSWORN-KALEIDO_HEART.description': '造成{Damage:diff()}点伤害。从抽牌堆中选择1张珠泪卡弃置。获得{Thorns:diff()}层荆棘。',
    'LIGHTSWORN-DRAGOSTAPELIA.title': '捕食植物 犀角龙',
    'LIGHTSWORN-DRAGOSTAPELIA.description': '造成{Damage:diff()}点伤害。对目标施加1层缩小。',
}
cards.update(new_cards)
save('cards.json', cards)

# ============ card_keywords.json ============
kw = load('card_keywords.json')
kw['LIGHTSWORN-TEARFUSION.title'] = '珠泪融合'
kw['LIGHTSWORN-TEARFUSION.description'] = ('珠泪融合：拥有此效果的卡被弃置时发动——从弃牌堆选择2~3张珠泪攻击牌放回抽牌堆'
    '（融合卡被选做素材时改为消耗），然后从满足条件的珠泪融合卡中选择1张加入手牌（触发卡已升级则融合出强化版）。'
    '同一回合每张融合卡只能生成1次；融合卡离开弃牌堆时消耗。'
    '融合条件：水仙女人鱼=2张珠泪攻击牌；鲁莎卡人鱼=含水仙女人鱼的2张珠泪攻击牌；卡雷多哈特=含雷诺哈特的3张珠泪攻击牌；捕食植物犀角龙=含融合卡的2张珠泪攻击牌。')
save('card_keywords.json', kw)

# ============ card_selection.json ============
sel = load('card_selection.json')
sel.update({
    'LIGHTSWORN_TEAR_MATERIAL': '珠泪融合：选择2~3张珠泪攻击牌放回抽牌堆',
    'LIGHTSWORN_TEAR_FUSION': '珠泪融合：选择1张融合卡加入手牌',
    'LIGHTSWORN_TEAR_DISCARD_ATTACK': '丢弃1张攻击牌（可不选）',
    'LIGHTSWORN_TEAR_DUMP': '选择1张珠泪卡弃置',
    'LIGHTSWORN_REINOHART_DISCARD': '雷诺哈特：丢弃1张珠泪攻击牌（可不选）',
})
save('card_selection.json', sel)

print('cards.json +%d entries (total %d)' % (len(new_cards), len(cards)))
print('card_keywords.json total %d' % len(kw))
print('card_selection.json total %d' % len(sel))
