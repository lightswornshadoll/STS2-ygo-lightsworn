import json
import io
import os

ROOT = r'D:\1-workdata\lightsworn_mod'
LOC = os.path.join(ROOT, r'mod\lightsworn\lightsworn\localization\zhs')


def load(name):
    with io.open(os.path.join(LOC, name), encoding='utf-8') as f:
        return json.load(f)


def save(name, data):
    with io.open(os.path.join(LOC, name), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')


def merge(target, frag, label):
    added = 0
    for k, v in frag.items():
        if k in target and target[k] != v:
            print(f'  [warn] {label} 覆盖已有key: {k}')
        if k not in target:
            added += 1
        target[k] = v
    print(f'  {label}: +{added} 条（共 {len(frag)}）')
    return target


# ============ 1. cards.json：agent片段 + 9张神影依Token ============
cards = load('cards.json')
for frag in ('cards_6.json', 'cards_7.json'):
    with io.open(os.path.join(ROOT, 'tools', 'locfrag', frag), encoding='utf-8') as f:
        merge(cards, json.load(f), frag)

tokens = {
    'LIGHTSWORN-EL_SHADDOLL_WINDA.title': '神影依·米德拉什',
    'LIGHTSWORN-EL_SHADDOLL_WINDA.description': '造成{Damage:diff()}点伤害，回复3点能量。从弃牌堆将1张影依技能加入手牌。',
    'LIGHTSWORN-EL_SHADDOLL_CONSTRUCT.title': '神影依·拿非利',
    'LIGHTSWORN-EL_SHADDOLL_CONSTRUCT.description': '造成{Damage:diff()}点伤害；若目标有格挡，改为清除其全部格挡。从卡组弃置1张影依卡。从弃牌堆将1张影依技能加入手牌。',
    'LIGHTSWORN-EL_SHADDOLL_WENDIGO.title': '神影依·文迪戈',
    'LIGHTSWORN-EL_SHADDOLL_WENDIGO.description': '获得{Buffer:diff()}层缓冲。从弃牌堆将1张影依技能加入手牌。\n[gold]本场战斗[/gold]此牌只能生成1次。',
    'LIGHTSWORN-EL_SHADDOLL_GRYSTA.title': '神影依·神子晶',
    'LIGHTSWORN-EL_SHADDOLL_GRYSTA.description': '造成{Damage:diff()}点伤害。可以丢弃1张手牌中的影依卡，对目标施加2层虚弱和易伤。从弃牌堆将1张影依技能加入手牌。',
    'LIGHTSWORN-EL_SHADDOLL_SHEKHINAGA.title': '神影依·舍金纳迦',
    'LIGHTSWORN-EL_SHADDOLL_SHEKHINAGA.description': '获得{Block:diff()}点格挡。可以丢弃1张手牌中的影依卡，获得1层人工制品。从弃牌堆将1张影依技能加入手牌。',
    'LIGHTSWORN-EL_SHADDOLL_ANOYATYLLIS.title': '神影依·异花莉莉丝',
    'LIGHTSWORN-EL_SHADDOLL_ANOYATYLLIS.description': '造成{Damage:diff()}点伤害，从弃牌堆将2张「影依」牌加入手牌。',
    'LIGHTSWORN-EL_SHADDOLL_APKALLONE.title': '神影依·七贤巨鲲魔',
    'LIGHTSWORN-EL_SHADDOLL_APKALLONE.description': '造成{Damage:diff()}点伤害，获得{Block:diff()}点格挡。从卡组或弃牌堆将1张影依卡加入手牌，然后弃置1张手牌。',
    'LIGHTSWORN-EL_SHADDOLL_MESHAHRAIL.title': '神影依·米沙赫雷恶',
    'LIGHTSWORN-EL_SHADDOLL_MESHAHRAIL.description': '造成{Damage:diff()}点伤害，获得2层镀层。从卡组将1张影依卡加入手牌，从弃牌堆将1张影依攻击卡加入手牌（本回合费用变为0）。',
    'LIGHTSWORN-REESHADDOLL_WENDIKURHU.title': '翼影依 影文蒂',
    'LIGHTSWORN-REESHADDOLL_WENDIKURHU.description': '获得{Block:diff()}点格挡。接下来3次「影依」牌被弃置时，其「被弃置时」的效果触发2次。从弃牌堆将1张影依卡加入手牌。',
}
merge(cards, tokens, 'tokens')
save('cards.json', cards)

# 校验35张卡的文案齐全
CLASSES = ['SHADDOLL_BEAST', 'SHADDOLL_DRAGON', 'SHADDOLL_SQUAMATA', 'SHADDOLL_HEDGEHOG', 'SHADDOLL_FALCO',
           'SHADDOLL_HOUND', 'NAELSHADDOLL_ARIEL', 'NEHSHADDOLL_GENIUS', 'QADSHADDOLL_KEIOS', 'REESHADDOLL_WENDI',
           'HELSHADDOLL_HOLLOW', 'TOHUSHADDOLL_GRYSTA', 'SHADDOLL_CONSTRUCT', 'SHADDOLL_ZEFRANAGA', 'SHADDOLL_ZEFRACORE',
           'SHADDOLL_FUSION', 'EL_SHADDOLL_FUSION', 'NEPHE_SHADDOLL_FUSION', 'PURGATORY_RELEASE', 'FROZEN_HEART_SHADOW',
           'SHADDOLL_CORE', 'SHADDOLL_SCHISM', 'RESH_SHADDOLL_INCARNATION', 'PURUSHADDOLL_AEON', 'SINISTER_SHADOW_GAMES',
           'CURSE_SHADOW_PRISON', 'EL_SHADDOLL_WINDA', 'EL_SHADDOLL_CONSTRUCT', 'EL_SHADDOLL_WENDIGO', 'EL_SHADDOLL_GRYSTA',
           'EL_SHADDOLL_SHEKHINAGA', 'EL_SHADDOLL_ANOYATYLLIS', 'EL_SHADDOLL_APKALLONE', 'EL_SHADDOLL_MESHAHRAIL',
           'REESHADDOLL_WENDIKURHU']
missing = [c for c in CLASSES if f'LIGHTSWORN-{c}.title' not in cards or f'LIGHTSWORN-{c}.description' not in cards]
print(f'cards.json 校验: {"35/35 齐全" if not missing else "缺失: " + str(missing)}')

# ============ 2. card_keywords.json：影融 ============
kw = load('card_keywords.json')
merge(kw, {
    'LIGHTSWORN-SHADDOLLFUSION.title': '影融',
    'LIGHTSWORN-SHADDOLLFUSION.description': '影融：弃置手牌中2~3张牌作为素材（神影依也可作素材），从条件满足的神影依中选择1张加入手牌（0费，打出后消耗）。素材的「被弃置时」效果照常触发；神影依每回合各只能生成1次。融合条件（素材数量须与条件严格一致）：神影依·米德拉什=2张影依牌；神影依·拿非利=1张影依牌+1张光道牌；神影依·文迪戈=1张影依牌+1张技能牌；神影依·神子晶=1张影依牌+1张攻击牌；神影依·舍金纳迦=2张影依攻击牌；神影依·异花莉莉丝=3张影依牌；神影依·七贤巨鲲魔=2张不同名的影依牌；神影依·米沙赫雷恶=3张手牌（含至少1张影依牌）；翼影依 影文蒂=2张影依技能牌。',
}, 'keyword')
save('card_keywords.json', kw)

# ============ 3. card_selection.json：选牌提示 ============
sel = load('card_selection.json')
merge(sel, {
    'LIGHTSWORN_SHADDOLL_MATERIAL': '选择影融素材',
    'LIGHTSWORN_SHADDOLL_FUSION': '选择要生成的神影依',
    'LIGHTSWORN_SHADDOLL_DISCARD_MATERIAL': '丢弃1张影依卡',
}, 'selection')
save('card_selection.json', sel)

# ============ 4. powers.json：4个影依能力 ============
powers = load('powers.json')
merge(powers, {
    'LIGHTSWORN-SINISTER_SHADOW_GAMES_POWER.title': '堕影的蠢动',
    'LIGHTSWORN-SINISTER_SHADOW_GAMES_POWER.description': '「影依」牌被弃置时，其「被弃置时」的效果触发2次。',
    'LIGHTSWORN-SINISTER_SHADOW_GAMES_POWER.smartDescription': '「影依」牌被弃置时，其「被弃置时」的效果触发2次。',
    'LIGHTSWORN-CURSE_SHADOW_PRISON_POWER.title': '影牢之咒缚',
    'LIGHTSWORN-CURSE_SHADOW_PRISON_POWER.description': '每当「影依」牌被弃置时，获得1层镀层。',
    'LIGHTSWORN-CURSE_SHADOW_PRISON_POWER.smartDescription': '每当「影依」牌被弃置时，获得[blue]{Amount}[/blue]层镀层。',
    'LIGHTSWORN-SHADDOLL_HOUND_POWER.title': '影依猎犬的加成',
    'LIGHTSWORN-SHADDOLL_HOUND_POWER.description': '本回合打出的下一张影依攻击卡，会额外触发其「被弃置时」的效果。',
    'LIGHTSWORN-SHADDOLL_HOUND_POWER.smartDescription': '本回合打出的接下来[blue]{Amount}[/blue]张影依攻击卡，会额外触发其「被弃置时」的效果。',
    'LIGHTSWORN-WENDIKURHU_POWER.title': '翼影依影文蒂的加成',
    'LIGHTSWORN-WENDIKURHU_POWER.description': '接下来3次「影依」牌被弃置时，其「被弃置时」的效果触发2次。',
    'LIGHTSWORN-WENDIKURHU_POWER.smartDescription': '接下来[blue]{Amount}[/blue]次「影依」牌被弃置时，其「被弃置时」的效果触发2次。',
}, 'powers')
save('powers.json', powers)

print('DONE')
