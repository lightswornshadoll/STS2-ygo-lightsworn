# -*- coding: utf-8 -*-
# v0.4.30 本轮18条反馈的本地化批量更新（含旧文案校验，键缺失/旧文不符即报错中止）
import json, io, os, sys

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    'mod', 'lightsworn', 'lightsworn', 'localization', 'zhs')

def load(name):
    return json.load(io.open(os.path.join(ROOT, name), encoding='utf-8'))

def save(name, data):
    with io.open(os.path.join(ROOT, name), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')

cards = load('cards.json')
powers = load('powers.json')
sel = load('card_selection.json')

errors = []

def setd(table, key, expect_sub, new, table_name):
    old = table.get(key)
    if old is None:
        if expect_sub == '':   # 允许新增键（expect_sub 为空=不校验旧文）
            table[key] = new
            return
        errors.append(f'[{table_name}] 缺键: {key}')
        return
    if expect_sub and expect_sub not in old:
        errors.append(f'[{table_name}] {key} 旧文案不含预期片段: {expect_sub!r}\n  实际: {old!r}')
        return
    table[key] = new

# ============ cards.json ============
# 1 影依融合强化后文本（素材从卡组选=限影依牌）
setd(cards, 'LIGHTSWORN-SHADDOLL_FUSION.description',
     '素材也可以从卡组选择',
     '影融{IfUpgraded:show:+|}。\n[gold]强化后[/gold] 素材也可以从卡组选择（限「影依」牌）。', 'cards')

# 17 神影依融合=重放1
setd(cards, 'LIGHTSWORN-EL_SHADDOLL_FUSION.description',
     '视为已升级',
     '影融{IfUpgraded:show:+|}，且本次融合生成的神影依获得1次[gold]重放[/gold]（将这张牌额外打出1次）。', 'cards')

# 16 虚影依 神子晶=被弃置时影融
setd(cards, 'LIGHTSWORN-TOHUSHADDOLL_GRYSTA.description',
     '影融{IfUpgraded:show:+|}：素材改为从弃牌堆选2张',
     '造成{Damage:diff()}点伤害。从弃牌堆将1张影依攻击卡加入手牌，本回合其费用变为0，其伤害变为0（打出一次后恢复）。\n[gold]被弃置时[/gold]：发动影融——从弃牌堆选2张「影依」牌消耗（不触发其被弃置时效果），融合1张神影依加入手牌。', 'cards')

# 13 圣影依=仅融合拿非利时可当光道牌
setd(cards, 'LIGHTSWORN-QADSHADDOLL_KEIOS.description',
     '获得（其费用+1）×{Gain:diff()}的活力',
     '造成{Damage:diff()}点伤害。手牌中1张「影依」攻击牌变成0费。\n[gold]被弃置时[/gold]：可以丢弃1张手牌中的影依攻击牌，获得（其费用+1）×{Gain:diff()}的活力。\n作为影融素材时，仅在融合「神影依·拿非利」时可作为「光道」牌使用。', 'cards')

# 13 神影依·拿非利融合条件注明圣影依代位
setd(cards, 'LIGHTSWORN-EL_SHADDOLL_CONSTRUCT.description',
     '融合条件：1张影依牌+1张光道牌。',
     '融合条件：1张影依牌+1张光道牌（「圣影依 商神杖灵」可充当光道牌）。\n造成{Damage:diff()}点伤害；若目标有格挡，改为清除其全部格挡。从卡组弃置1张影依卡。从弃牌堆将1张非神影依的影依技能加入手牌。\n第2次打出时消耗。', 'cards')

# 12 救影依=追加8格挡
setd(cards, 'LIGHTSWORN-SHADDOLL_ZEFRANAGA.description',
     '弃光{Mill:diff()}。',
     '弃光{Mill:diff()}，获得8点格挡。\n[gold]被弃置时[/gold]：抽1张牌。', 'cards')

# 3 露米娜丝回调=去格挡、拿2张
setd(cards, 'LIGHTSWORN-LUMINA.description',
     '获得{Block:diff()}点格挡',
     '弃光{Mill:diff()}。弃置1张手牌，从弃牌堆中将{Picks:diff()}张「光道」牌加入手牌（本回合费用为0）。', 'cards')

# 11 米迦勒=每张2格挡
setd(cards, 'LIGHTSWORN-MICHAEL.description',
     '每回收1张获得1点格挡',
     '造成{Damage:diff()}点伤害。将弃牌堆中的「光道」牌全部加入抽牌堆，每回收1张获得2点格挡。', 'cards')

# 10 神光之龙=+5/光道卡+神光回响
setd(cards, 'LIGHTSWORN-SHINING_DRAGON.description',
     '施加3层虚弱和3层易伤',
     '弃牌堆中存在「裁决之龙」和「惩戒之龙」时才能打出。\n消耗弃牌堆中的所有卡，对所有敌人造成{Damage:diff()}点伤害（消耗堆每有一张「光道」牌，额外造成5点伤害）并施加3层虚弱和3层易伤，然后从消耗堆中将1张「裁决之龙」和1张「惩戒之龙」加入手牌。\n获得能力[gold]神光回响[/gold]：回合开始时，从弃牌堆随机将{Recall:diff()}张「光道」牌加入手牌并变为0费。', 'cards')

# 6 正义世界=3/4活力
setd(cards, 'LIGHTSWORN-JUSTICE_WORLD.description',
     '获得1点[gold]活力[/gold]',
     '每当有牌从抽牌堆弃置到弃牌堆时，你获得{Vigor:diff()}点[gold]活力[/gold]（不限「光道」牌）。', 'cards')

# 5 珍珠世界=基础效果用强化版，敲后易伤2层
setd(cards, 'LIGHTSWORN-PERLEREINO.description',
     '施加1层易伤',
     '每次发动珠泪融合时，对所有敌人施加{Vul:diff()}层易伤。打出时，从抽牌堆中选择1张珠泪攻击牌加入手牌。', 'cards')

# 18 雷喵=0费、敲后+1张
setd(cards, 'LIGHTSWORN-RINYAN.description',
     '将弃牌堆中最多2张',
     '将弃牌堆中最多{Picks:diff()}张「光道」牌洗回抽牌堆，抽1张牌。', 'cards')

# 14 地天使四张重做
setd(cards, 'LIGHTSWORN-MUDORA.description',
     '若弃置了「地天使」牌',
     '将弃牌堆中最多{Picks:diff()}张牌洗回抽牌堆，抽1张牌；若抽到的是攻击牌，其费用-1。', 'cards')
setd(cards, 'LIGHTSWORN-KELDO.description',
     '「光道」牌洗回抽牌堆',
     '将弃牌堆中最多{Picks:diff()}张牌洗回抽牌堆，抽1张牌；若抽到的是技能牌，其费用-1。', 'cards')
setd(cards, 'LIGHTSWORN-KELBEK.description',
     '若其中有「光道」牌，获得',
     '弃光{Mill:diff()}。若其中有2张以上攻击牌，对随机敌人造成{Damage:diff()}点伤害。', 'cards')
setd(cards, 'LIGHTSWORN-AGIDO.description',
     '若其中有「光道」牌，抽1张牌',
     '弃光{Mill:diff()}。若其中有2张以上技能牌，获得{Block:diff()}点格挡。', 'cards')

# 15 七张珠泪卡改名+两处交叉引用
for key, old_t, new_t in [
    ('LIGHTSWORN-SULIEK.title', '塞壬人鱼', '珠泪哀歌族 塞壬人鱼'),
    ('LIGHTSWORN-MERRLI.title', '小美人鱼', '珠泪哀歌族 小美人鱼'),
    ('LIGHTSWORN-HAVNIS.title', '梅洛人鱼', '珠泪哀歌族 梅洛人鱼'),
    ('LIGHTSWORN-REINOHART.title', '雷诺哈特', '珠泪哀歌族 雷诺哈特'),
    ('LIGHTSWORN-KITKALLOS.title', '水仙女人鱼', '珠泪哀歌族 水仙女人鱼'),
    ('LIGHTSWORN-RULKALLOS.title', '鲁莎卡人鱼', '珠泪哀歌族 鲁莎卡人鱼'),
    ('LIGHTSWORN-KALEIDO_HEART.title', '卡雷多哈特', '珠泪哀歌族 卡雷多哈特'),
]:
    setd(cards, key, old_t, new_t, 'cards')

setd(cards, 'LIGHTSWORN-RULKALLOS.description',
     '含水仙女人鱼的2张珠泪攻击牌',
     '融合条件：含「珠泪哀歌族 水仙女人鱼」的2张珠泪攻击牌。\n造成{Damage:diff()}点伤害，若目标为爪牙，伤害翻倍。本回合每打出过1张珠泪卡，获得2点格挡。', 'cards')
setd(cards, 'LIGHTSWORN-KALEIDO_HEART.description',
     '含雷诺哈特的3张珠泪攻击牌',
     '融合条件：含「珠泪哀歌族 雷诺哈特」的3张珠泪攻击牌。\n造成{Damage:diff()}点伤害。从抽牌堆中选择1张珠泪卡弃置。获得{Thorns:diff()}层荆棘。', 'cards')

# ============ powers.json ============
setd(powers, 'LIGHTSWORN-JUSTICE_WORLD_POWER.description',
     '获得1点[gold]活力[/gold]',
     '每当有牌从抽牌堆弃置到弃牌堆时，你获得{Amount}点[gold]活力[/gold]（不限「光道」牌）。', 'powers')
setd(powers, 'LIGHTSWORN-JUSTICE_WORLD_POWER.smartDescription',
     '获得1点[gold]活力[/gold]',
     '每当有牌从抽牌堆弃置到弃牌堆时，你获得[blue]{Amount}[/blue]点[gold]活力[/gold]（不限「光道」牌）。', 'powers')

# 5 珍珠世界能力（此前无词条，补齐；{Amount}=易伤层数）
setd(powers, 'LIGHTSWORN-PEARL_WORLD_POWER.description', '',
     '每次发动珠泪融合时，对所有敌人施加{Amount}层易伤。', 'powers')
setd(powers, 'LIGHTSWORN-PEARL_WORLD_POWER.smartDescription', '',
     '每次发动珠泪融合时，对所有敌人施加[blue]{Amount}[/blue]层易伤。', 'powers')
setd(powers, 'LIGHTSWORN-PEARL_WORLD_POWER.title', '',
     '珍珠世界', 'powers')

# 10 神光回响新能力
setd(powers, 'LIGHTSWORN-SHINING_DRAGON_POWER.description', '',
     '回合开始时，从弃牌堆随机将{Amount}张「光道」牌加入手牌并变为0费。', 'powers')
setd(powers, 'LIGHTSWORN-SHINING_DRAGON_POWER.smartDescription', '',
     '回合开始时，从弃牌堆随机将[blue]{Amount}[/blue]张「光道」牌加入手牌并变为0费。', 'powers')
setd(powers, 'LIGHTSWORN-SHINING_DRAGON_POWER.title', '',
     '神光回响', 'powers')

# ============ card_selection.json ============
setd(sel, 'LIGHTSWORN_REINOHART_DISCARD',
     '雷诺哈特：丢弃1张珠泪攻击牌',
     '珠泪哀歌族 雷诺哈特：丢弃1张珠泪攻击牌（可不选）', 'card_selection')

if errors:
    print('!! 校验失败，未写入：')
    for e in errors:
        print(e)
    sys.exit(1)

save('cards.json', cards)
save('powers.json', powers)
save('card_selection.json', sel)
print('OK: cards/powers/card_selection 已更新')
