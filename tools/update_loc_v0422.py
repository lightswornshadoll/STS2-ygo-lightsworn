# -*- coding: utf-8 -*-
# v0.4.22 文案同步：羽影依文蒂/虚影依神子晶/联结之影依化身的"伤害变为0"改为只持续一次，
# 补"（打出一次后恢复）"。带键存在+旧文案校验，保持 ensure_ascii=False + indent=2
import io, json, sys, os

root = os.path.join(os.path.dirname(__file__), '..', 'mod', 'lightsworn', 'lightsworn', 'localization', 'zhs')
path = os.path.normpath(os.path.join(root, 'cards.json'))

with io.open(path, encoding='utf-8') as f:
    d = json.load(f)

changes = [
    ('LIGHTSWORN-REESHADDOLL_WENDI.description',
     '本回合其费用变为0，其伤害变为0。', '本回合其费用变为0，其伤害变为0（打出一次后恢复）。'),
    ('LIGHTSWORN-TOHUSHADDOLL_GRYSTA.description',
     '本回合其费用变为0，其伤害变为0。', '本回合其费用变为0，其伤害变为0（打出一次后恢复）。'),
    ('LIGHTSWORN-RESH_SHADDOLL_INCARNATION.description',
     '其费用变为0，伤害变为0。', '其费用变为0，伤害变为0（打出一次后恢复）。'),
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
