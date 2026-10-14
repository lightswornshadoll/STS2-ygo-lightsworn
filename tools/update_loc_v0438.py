# -*- coding: utf-8 -*-
"""v0.4.38 蛇影依 路径灵 追加「消耗」：本地化同步。
cards.json 与 locfrag\cards_6.json 同改（带旧文校验）。
用法: py tools\\update_loc_v0438.py
"""
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOC = os.path.join(ROOT, 'mod', 'lightsworn', 'lightsworn', 'localization', 'zhs')
FRAG = os.path.join(ROOT, 'tools', 'locfrag', 'cards_6.json')

OLD = '造成{Damage:diff()}点伤害，获得1层人工制品。\n[gold]被弃置时[/gold]：获得1层镀层。'
NEW = '造成{Damage:diff()}点伤害，获得1层人工制品。消耗。\n[gold]被弃置时[/gold]：获得1层镀层。'
KEY = 'LIGHTSWORN-NEHSHADDOLL_GENIUS.description'

errors = []
for path in (os.path.join(LOC, 'cards.json'), FRAG):
    data = json.load(io.open(path, encoding='utf-8'))
    cur = data.get(KEY)
    if cur is None:
        errors.append('缺键 %s (%s)' % (KEY, path))
    elif cur != OLD:
        errors.append('%s 旧文不符 (%s)：\n  实际=%r\n  期望=%r' % (KEY, path, cur, OLD))
    else:
        data[KEY] = NEW
        json.dump(data, io.open(path, 'w', encoding='utf-8', newline='\n'),
                  ensure_ascii=False, indent=2)
        io.open(path, 'a', encoding='utf-8', newline='').write('\n')
        print('OK 已更新', os.path.relpath(path, ROOT))

if errors:
    print('!! 校验失败：')
    for e in errors:
        print('  -', e)
    sys.exit(1)
print('v0.4.38 蛇影依 路径灵 描述已追加「消耗。」（cards.json + locfrag）')
