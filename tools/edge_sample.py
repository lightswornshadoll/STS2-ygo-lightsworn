# -*- coding: utf-8 -*-
"""临时：采样源卡图插画窗口四边，找精确内沿（暗=卡框，亮=插画）。"""
import os
from PIL import Image

for name, code, (x0, y0, x1, y1) in [
    ('aegis', '25218587', (44, 100, 357, 417)),
    ('lod', '83027236', (44, 100, 357, 417)),
]:
    im = Image.open(r'D:\MyCardLibrary\ygopro\pics' + '\\' + code + '.jpg').convert('L')
    px = im.load()
    print('==', name)
    for label, rng in [('top rows y', range(98, 118)), ('bottom rows y', range(404, 420))]:
        s = []
        for y in rng:
            vals = [px[x, y] for x in range(60, 340, 7)]
            s.append((y, round(sum(vals) / len(vals))))
        print(' ', label, s)
    for label, rng in [('left cols x', range(42, 60)), ('right cols x', range(342, 360))]:
        s = []
        for x in rng:
            vals = [px[x, y] for y in range(120, 400, 7)]
            s.append((x, round(sum(vals) / len(vals))))
        print(' ', label, s)
