# -*- coding: utf-8 -*-
"""三层 Boss 抉择事件新立绘「最远方的宇宙」：1248x1248 方图 → 原版事件画布 3440x1613。
方图直接中心 cover 裁切（2.133:1）后 LANCZOS 放大；星空纹理连续，无需模糊延展。"""
from PIL import Image
import os

SRC = r"D:\download\chrome_download\光道mod素材\最远方的宇宙.jpeg"
OUT = r"D:\1-workdata\lightsworn_mod\mod\lightsworn\lightsworn\images\events\farthest_universe.png"
PREVIEW = r"D:\1-workdata\lightsworn_mod\tools\probe_universe_event_art.jpg"
os.makedirs(os.path.dirname(OUT), exist_ok=True)

CW, CH = 3440, 1613
im = Image.open(SRC).convert("RGB")
w, h = im.size
print("source:", im.size)

crop_h = int(round(w * CH / CW))
top = (h - crop_h) // 2
im = im.crop((0, top, w, top + crop_h))
print("cropped:", im.size, "aspect", im.size[0] / im.size[1])

canvas = im.resize((CW, CH), Image.LANCZOS)
canvas.save(OUT)
print("saved:", OUT, canvas.size)

canvas.resize((1290, 605), Image.LANCZOS).save(PREVIEW, quality=90)
print("preview:", PREVIEW)
