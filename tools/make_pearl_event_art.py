# 事件立绘「于珍珠世界相逢」：1536×1152 原图 → 原版事件画布 3440×1613（比例 2.133:1，与 vanilla 一致）
# 底=放大裁切+高斯模糊延展，前景=等高居中+左右羽化融入
from PIL import Image, ImageFilter
import numpy as np
import os

SRC = r"D:\download\chrome_download\光道mod素材\于珍珠世界相逢.png"
OUT = r"D:\1-workdata\lightsworn_mod\mod\lightsworn\lightsworn\images\events\pearl_world_encounter.png"
PREVIEW = r"D:\1-workdata\lightsworn_mod\tools\probe_event_art.jpg"
os.makedirs(os.path.dirname(OUT), exist_ok=True)

CW, CH = 3440, 1613  # 原版事件图实测尺寸（round_tea_party 等）
im = Image.open(SRC).convert("RGB")
w, h = im.size
print("source:", im.size)

# 底：cover 铺满 + 重模糊
scale = max(CW / w, CH / h)
bw, bh = int(w * scale + 0.5), int(h * scale + 0.5)
bg = im.resize((bw, bh), Image.LANCZOS)
left = (bw - CW) // 2
top = min(max((bh - CH) // 2, 0), bh - CH)  # 居中裁切
bg = bg.crop((left, top, left + CW, top + CH)).filter(ImageFilter.GaussianBlur(48))

# 前：等高缩放居中，左右羽化80px
fw = int(w * CH / h + 0.5)
fg = im.resize((fw, CH), Image.LANCZOS)
alpha = np.ones((CH, fw))
edge = 80
ramp = np.minimum(np.arange(fw) / edge, np.arange(fw)[::-1] / edge).clip(0, 1)
alpha *= ramp[None, :]
fg.putalpha(Image.fromarray((alpha * 255).astype(np.uint8)))

canvas = bg.convert("RGBA")
fx = (CW - fw) // 2
canvas.alpha_composite(fg, (fx, 0))
canvas.convert("RGB").save(OUT)
print("saved:", OUT, canvas.size)

canvas.convert("RGB").resize((1290, 605), Image.LANCZOS).save(PREVIEW, quality=90)
print("preview:", PREVIEW)
