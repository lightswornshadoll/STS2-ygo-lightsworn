# -*- coding: utf-8 -*-
"""临时：查 dist / 游戏目录三件套时间戳与大小。"""
import datetime
import hashlib
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME = r'D:\Program Files (x86)\Steam\steamapps\common\Slay the Spire 2\mods\Lightsworn'
for d in (os.path.join(ROOT, 'dist', 'lightsworn'), GAME):
    print('==', d)
    for f in sorted(os.listdir(d)):
        p = os.path.join(d, f)
        h = hashlib.md5(open(p, 'rb').read()).hexdigest()[:10]
        print(f'   {f:20s} {datetime.datetime.fromtimestamp(os.path.getmtime(p))} {os.path.getsize(p):9d} md5:{h}')
