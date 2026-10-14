# -*- coding: utf-8 -*-
"""临时：查看 mod 目录 locfrag 片段里与第四十轮改动相关的键（判断是否需要同步）。"""
import io
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, 'mod', 'lightsworn', 'tools', 'locfrag')

KEYS = [
    'LIGHTSWORN-AEGIS', 'LIGHTSWORN-GAROTH', 'LIGHTSWORN-LIGHT_BOUNCE',
    'LIGHTSWORN-JUSTICE_WORLD', 'LIGHTSWORN-TWILIGHT_GARB', 'LIGHTSWORN-FLASH_FANTASY',
    'LIGHTSWORN-KELBEK', 'LIGHTSWORN-AGIDO', 'LIGHTSWORN-MERRLI', 'LIGHTSWORN-PRIMEVAL_CRY',
    'LIGHTSWORN-PRIMEVAL_ECHO', 'LIGHTSWORN-PURUSHADDOLL_AEON', 'LIGHTSWORN-NAELSHADDOLL_ARIEL',
    'LIGHTSWORN-SHADDOLL_ZEFRACORE', 'LIGHTSWORN-GRAGONITH', 'LIGHTSWORN-ORCUS',
    'LIGHTSWORN-SHINING_DRAGON', 'LIGHTSWORN-TWIN_TWILIGHT_DRAGON', 'LIGHTSWORN-DECREE',
]

for f in sorted(os.listdir(D)):
    if not f.endswith('.json'):
        continue
    data = json.load(io.open(os.path.join(D, f), encoding='utf-8'))
    hits = [k for k in data if any(k.startswith(p) or k.replace('_POWER', '') == p for p in KEYS)]
    print(f'== {f}: {len(data)} keys, 相关命中 {len(hits)}')
    for h in hits:
        print('   ', h, '=', data[h][:60])
