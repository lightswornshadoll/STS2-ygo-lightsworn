# -*- coding: utf-8 -*-
"""临时：抽查卡牌图鉴条目（py tools\\peek_doc.py 卡名1 卡名2 ...）"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
t = io.open(os.path.join(ROOT, 'design', '卡牌图鉴.md'), encoding='utf-8').read()
keys = sys.argv[1:] or ['光道埃癸斯盾', '正义世界', '神光之龙', '古尖兵', '光之回弹', '神我影依流世', '残响', '影依巫女']
for k in keys:
    i = t.find('### ' + k)
    print('=' * 10, k)
    print(t[i:i + 430] if i >= 0 else '(未找到)')
