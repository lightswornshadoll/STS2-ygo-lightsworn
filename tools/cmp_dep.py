# -*- coding: utf-8 -*-
"""临时：比对部署 pck 解出的先古卡纹理与本地文件。"""
import hashlib
import os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pairs = [
    (os.path.join(ROOT, 'tools', '_dep_aegis.png'), os.path.join(ROOT, 'mod', 'lightsworn', 'lightsworn', 'images', 'cards', 'Aegis.png')),
    (os.path.join(ROOT, 'tools', '_dep_lod.png'), os.path.join(ROOT, 'mod', 'lightsworn', 'lightsworn', 'images', 'cards', 'LightOfDestruction.png')),
]
for dep, loc in pairs:
    a = Image.open(dep)
    b = Image.open(loc)
    da, db = a.tobytes(), b.tobytes()
    diff = sum(1 for x, y in zip(da, db) if abs(x - y) > 8)
    print(os.path.basename(loc), 'deployed', a.size, 'local', b.size,
          'diff', diff, '/', len(da),
          'md5', hashlib.md5(da).hexdigest()[:10], hashlib.md5(db).hexdigest()[:10])
