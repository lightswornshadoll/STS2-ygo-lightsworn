# 事件立绘「于珍珠世界相逢」v2：1920×1080 → 原版事件画布 3440×1613（比例 2.133:1）
# 新素材是 16:9（2.133 目标只多裁一点天空），直接底部锚定 cover 裁切 + LANCZOS 放大，无模糊边条。
from PIL import Image
import os

SRC = r"D:\download\chrome_download\光道mod素材\Cache_574a0c16ebe486ca.png"
OUT = r"D:\1-workdata\lightsworn_mod\mod\lightsworn\lightsworn\images\events\pearl_world_encounter.png"
PREVIEW = r"D:\1-workdata\lightsworn_mod\tools\probe_event_art_v2.jpg"
CROP_TOP = 180  # 从顶部裁掉的天空像素（1080 - 180 = 900 高度 ≈ 2.133:1）

CW, CH = 3440, 1613
im = Image.open(SRC).convert("RGB")
w, h = im.size
print("source:", im.size)

crop_h = 900
top = min(CROP_TOP, h - crop_h)
im = im.crop((0, top, w, top + crop_h))
print("cropped:", im.size, "aspect", im.size[0] / im.size[1])

canvas = im.resize((CW, CH), Image.LANCZOS)
canvas.save(OUT)
print("saved:", OUT, canvas.size)

canvas.resize((1290, 605), Image.LANCZOS).save(PREVIEW, quality=90)
print("preview:", PREVIEW)
