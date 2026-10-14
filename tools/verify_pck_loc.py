# -*- coding: utf-8 -*-
"""临时：校验部署 pck 内 cards.json/powers.json 的关键新文案。"""
import io
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, 'tools', '_pckdump')

targets = {}
for r, dirs, fs in os.walk(BASE):
    for f in fs:
        if f in ('cards.json', 'powers.json', 'card_keywords.json'):
            targets[f] = os.path.join(r, f)

checks = {
    'cards.json': ['LIGHTSWORN-PRIMEVAL_ECHO.title', 'LIGHTSWORN-AEGIS.description'],
    'powers.json': ['LIGHTSWORN-PURUSHADDOLL_AEON_POWER.title', 'LIGHTSWORN-GAROTH_POWER.description'],
    'card_keywords.json': ['LIGHTSWORN-BANISH.description'],
}
for name, path in targets.items():
    data = json.load(io.open(path, encoding='utf-8'))
    print('==', name, len(data), 'keys ->', os.path.relpath(path, BASE))
    for k in checks.get(name, []):
        print('   ', k, ':', data.get(k))
    if name == 'cards.json':
        print('   AEGIS_POWER 残留:', [k for k in data if 'AEGIS_POWER' in k])
