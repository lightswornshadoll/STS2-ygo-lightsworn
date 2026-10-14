# -*- coding: utf-8 -*-
# v0.4.21 文案同步：
# 1. 心影依融合：伤害置0改为只持续一次（打出一次后恢复）
# 2. 神影依9张：检索效果文案加"非神影依"限定（检索不能拿神影依）
# 带键存在+旧文案校验，保持 ensure_ascii=False + indent=2
import io, json, sys, os

root = os.path.join(os.path.dirname(__file__), '..', 'mod', 'lightsworn', 'lightsworn', 'localization', 'zhs')
path = os.path.normpath(os.path.join(root, 'cards.json'))

with io.open(path, encoding='utf-8') as f:
    d = json.load(f)

# (key, old_substring, new_substring) —— 按 old 全量替换校验
changes = [
    ('LIGHTSWORN-FROZEN_HEART_SHADOW.description',
     '其伤害变为0。', '其伤害变为0（打出一次后恢复）。'),
    ('LIGHTSWORN-EL_SHADDOLL_WINDA.description',
     '从弃牌堆将1张影依技能加入手牌。', '从弃牌堆将1张非神影依的影依技能加入手牌。'),
    ('LIGHTSWORN-EL_SHADDOLL_CONSTRUCT.description',
     '从弃牌堆将1张影依技能加入手牌。', '从弃牌堆将1张非神影依的影依技能加入手牌。'),
    ('LIGHTSWORN-EL_SHADDOLL_WENDIGO.description',
     '从弃牌堆将1张影依技能加入手牌。', '从弃牌堆将1张非神影依的影依技能加入手牌。'),
    ('LIGHTSWORN-EL_SHADDOLL_GRYSTA.description',
     '从弃牌堆将1张影依技能加入手牌。', '从弃牌堆将1张非神影依的影依技能加入手牌。'),
    ('LIGHTSWORN-EL_SHADDOLL_SHEKHINAGA.description',
     '从弃牌堆将1张影依技能加入手牌。', '从弃牌堆将1张非神影依的影依技能加入手牌。'),
    ('LIGHTSWORN-EL_SHADDOLL_ANOYATYLLIS.description',
     '从弃牌堆将2张「影依」牌加入手牌。', '从弃牌堆将2张非神影依的「影依」牌加入手牌。'),
    ('LIGHTSWORN-EL_SHADDOLL_APKALLONE.description',
     '从卡组或弃牌堆将1张影依卡加入手牌，', '从卡组或弃牌堆将1张非神影依的影依卡加入手牌，'),
    ('LIGHTSWORN-EL_SHADDOLL_MESHAHRAIL.description',
     '从弃牌堆将1张影依攻击卡加入手牌（本回合费用变为0）。',
     '从弃牌堆将1张非神影依的影依攻击卡加入手牌（本回合费用变为0）。'),
    ('LIGHTSWORN-REESHADDOLL_WENDIKURHU.description',
     '从弃牌堆将1张影依卡加入手牌。', '从弃牌堆将1张非神影依的影依卡加入手牌。'),
]

failed = False
for key, old, new in changes:
    if key not in d:
        print(f'[缺失键] {key}')
        failed = True
        continue
    text = d[key]
    if text.count(old) != 1:
        print(f'[旧文案不符] {key}: 出现{old} {text.count(old)} 次')
        print(f'  现文案: {text}')
        failed = True
        continue
    d[key] = text.replace(old, new)
    print(f'[OK] {key}')

if failed:
    print('有校验失败项，未写入文件')
    sys.exit(1)

with io.open(path, 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)

print(f'已写入 {path}（共改 {len(changes)} 条）')
