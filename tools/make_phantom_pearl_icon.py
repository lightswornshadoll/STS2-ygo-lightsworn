# 幻色珍珠（事件遗物）图标：金色珍珠遗物图 → 珠泪特色的海蓝色（HSV 色相重映射，保留明度/描边）
# 产出 mod images/relics/phantom_pearl.png(64) + phantom_pearl_big.png(256)
from PIL import Image
import numpy as np

SRC = r"D:\1-workdata\lightsworn_mod\research\relic_icons\golden_pearl.png"
OUT64 = r"D:\1-workdata\lightsworn_mod\mod\lightsworn\lightsworn\images\relics\phantom_pearl.png"
OUT256 = r"D:\1-workdata\lightsworn_mod\mod\lightsworn\lightsworn\images\relics\phantom_pearl_big.png"
PREVIEW = r"D:\1-workdata\lightsworn_mod\tools\probe_phantom_pearl.png"

GOLD_H = 33.0    # 金色主色相（PIL 0-255 标度，约 46°）
TARGET_H = 142.0 # 珠泪海蓝（约 200°）
SAT_BOOST = 1.18

im = Image.open(SRC).convert("RGBA")
r, g, b, a = im.split()
hsv = np.array(Image.merge("RGB", (r, g, b)).convert("HSV")).astype(np.float32)
h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]

# 有色彩的像素（珍珠本体）：色相整体平移到海蓝，保留相对色相差（高光/暗部层次）
colored = s > 40
dh = h - GOLD_H
h2 = np.where(colored, (TARGET_H + dh * 0.55) % 256.0, h)
s2 = np.where(colored, np.clip(s * SAT_BOOST, 0, 255), s)
# 灰描边/灰高光：保持中性，微微偏蓝（+8% 蓝染）
grey = ~colored
h2 = np.where(grey, (TARGET_H * 0.86), h2)
s2 = np.where(grey, np.clip(s + 12, 0, 255), s2)

out = Image.merge("HSV", (
    Image.fromarray(h2.astype(np.uint8)),
    Image.fromarray(s2.astype(np.uint8)),
    Image.fromarray(v.astype(np.uint8)),
)).convert("RGB").convert("RGBA")
out.putalpha(a)

out.save(OUT256)
out.resize((64, 64), Image.LANCZOS).save(OUT64)
print("saved:", OUT256, OUT64)

# 预览：原图 + 新图并排
prev = Image.new("RGB", (512, 256), (24, 24, 32))
prev.paste(Image.open(SRC).convert("RGB").resize((256, 256), Image.LANCZOS), (0, 0))
prev.paste(out.convert("RGB"), (256, 0))
prev.save(PREVIEW)
print("preview:", PREVIEW)
