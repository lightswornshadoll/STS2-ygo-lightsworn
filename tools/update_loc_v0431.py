# -*- coding: utf-8 -*-
# v0.4.31 订正两条：地天使减费=仅一次（直到打出）；雷喵敲后=抽X+1张（X=洗回数量）
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
errors = []

def setd(key, expect_sub, new):
    old = cards.get(key)
    if old is None:
        errors.append(f'缺键: {key}')
        return
    if expect_sub not in old:
        errors.append(f'{key} 旧文案不含预期片段: {expect_sub!r}\n  实际: {old!r}')
        return
    cards[key] = new

setd('LIGHTSWORN-MUDORA.description',
     '若抽到的是攻击牌，其费用-1',
     '将弃牌堆中最多{Picks:diff()}张牌洗回抽牌堆，抽1张牌；若抽到的是攻击牌，其费用-1（直到打出）。')
setd('LIGHTSWORN-KELDO.description',
     '若抽到的是技能牌，其费用-1',
     '将弃牌堆中最多{Picks:diff()}张牌洗回抽牌堆，抽1张牌；若抽到的是技能牌，其费用-1（直到打出）。')
setd('LIGHTSWORN-RINYAN.description',
     '洗回抽牌堆，抽1张牌',
     '将弃牌堆中最多2张「光道」牌洗回抽牌堆{IfUpgraded:show:，然后抽X+1张牌（X=洗回的牌数）|，然后抽1张牌}。')

if errors:
    print('!! 校验失败，未写入：')
    for e in errors:
        print(e)
    sys.exit(1)

save('cards.json', cards)
print('OK: cards.json 已更新（3条订正）')
