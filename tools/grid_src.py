# -*- coding: utf-8 -*-
"""临时：给两张源卡图叠坐标网格（2倍放大，25px 刻度），用于核对插画窗口坐标。"""
import os
from PIL import Image, ImageDraw

TOOLS = os.path.dirname(os.path.abspath(__file__))
for name, src in [('aegis', r'D:\MyCardLibrary\ygopro\pics\25218587.jpg'),
                  ('lod', r'D:\MyCardLibrary\ygopro\pics\83027236.jpg')]:
    im = Image.open(src).convert('RGB').resize((800, 1160), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    for x in range(0, 401, 25):
        col = (0, 255, 0) if x % 50 == 0 else (0, 160, 0)
        d.line([(x * 2, 0), (x * 2, 1160)], fill=col, width=1)
        if x % 50 == 0:
            d.text((x * 2 + 3, 3), str(x), fill=(0, 255, 0))
    for y in range(0, 581, 25):
        col = (255, 255, 0) if y % 50 == 0 else (160, 130, 0)
        d.line([(0, y * 2), (800, y * 2)], fill=col, width=1)
        if y % 50 == 0:
            d.text((3, y * 2 + 3), str(y), fill=(255, 255, 0))
    im.save(os.path.join(TOOLS, f'_grid_{name}.png'))
print('ok')
