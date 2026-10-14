# 猫狗双全遗物：①中央徽章圆裁 → 遗物图标 64/256（圆形透明底）
#                ②顺手把原图右下角「豆包AI生成」水印抹掉，输出去水印版（仅素材库备用，不入 mod）
from PIL import Image, ImageFilter, ImageDraw
import numpy as np

SRC = r"D:\download\chrome_download\光道mod素材\猫狗双全.png"
OUT_DIR = r"D:\1-workdata\lightsworn_mod\mod\lightsworn\lightsworn\images\relics"
CLEAN_OUT = r"D:\download\chrome_download\光道mod素材\猫狗双全_去水印.png"

im = Image.open(SRC).convert("RGBA")
w, h = im.size
print("source size:", im.size)

# ---------- ① 径向中值+最小二乘拟合金色圆环（避开外框与四角爪印） ----------
a = np.asarray(im.convert("RGB"), dtype=np.int16)
r_, g_, b_ = a[..., 0], a[..., 1], a[..., 2]
gold = (r_ > 130) & (g_ > 90) & (r_ + g_ > 2.0 * b_) & (r_ - b_ > 40)
H, W = gold.shape
ccx, ccy = W // 2, H // 2
for it in range(3):
    ys, xs = np.nonzero(gold)
    dx = xs - ccx
    dy = ys - ccy
    dist = np.sqrt(dx * dx + dy * dy)
    ang = np.arctan2(dy, dx)
    keep = dist < 600  # 圆环+环内金色；外框/爪印在600以外
    dist_k, ang_k = dist[keep], ang[keep]
    bins = ((ang_k + np.pi) / (2 * np.pi) * 360).astype(int).clip(0, 359)
    maxr = np.full(360, 0.0)
    np.maximum.at(maxr, bins, dist_k)
    valid = maxr > 50
    r_med = float(np.median(maxr[valid]))
    # 取中值附近±10px的环上点拟合圆心 (x²+y²+Dx+Ey+F=0)
    sel = keep & (np.abs(dist - r_med) < 10)
    sx = xs[sel].astype(np.float64)
    sy = ys[sel].astype(np.float64)
    A = np.stack([sx, sy, np.ones_like(sx)], axis=1)
    bb = -(sx * sx + sy * sy)
    D, E, F = np.linalg.lstsq(A, bb, rcond=None)[0]
    ncx, ncy = -D / 2, -E / 2
    nr = float(np.sqrt(ncx * ncx + ncy * ncy - F))
    print(f"iter{it}: center=({ncx:.1f},{ncy:.1f}) r={nr:.1f} (median {r_med:.1f}, ring pts {int(sel.sum())})")
    if abs(ncx - ccx) < 0.5 and abs(ncy - ccy) < 0.5:
        ccx, ccy, ring_r = int(round(ncx)), int(round(ncy)), nr
        break
    ccx, ccy = int(round(ncx)), int(round(ncy))
ring_r = nr
side = int(round(ring_r)) * 2 + 4
half = side // 2
print("ring center", (ccx, ccy), "r", int(ring_r), "half", half)
sq = im.crop((ccx - half, ccy - half, ccx + half, ccy + half))

# 圆形透明底（往里收2px防杂边）
big = sq.resize((256, 256), Image.LANCZOS)
mask = Image.new("L", (512, 512), 0)
ImageDraw.Draw(mask).ellipse((4, 4, 508, 508), fill=255)
mask256 = mask.resize((256, 256), Image.LANCZOS)
big.putalpha(mask256)
big.save(f"{OUT_DIR}\\cats_and_dogs_big.png")

small = sq.resize((64, 64), Image.LANCZOS)
small.putalpha(mask.resize((64, 64), Image.LANCZOS))
small.save(f"{OUT_DIR}\\cats_and_dogs.png")
print("saved cats_and_dogs(_big).png, crop center", (ccx, ccy), "half", half)

# ---------- ② 去水印：右下角「豆包AI生成」→ 同高度干净区整块横向克隆（行结构对齐，骨头在其左侧不受影响） ----------
im2 = im.convert("RGB")
work = np.asarray(im2, dtype=np.float64).copy()
RX0, RX1, RY0, RY1 = 1295, 1515, 1433, 1521  # 文字主体+暗描边全部覆盖；骨头最右到~1280，安全
SX = RX0 - 465  # 克隆源 x 830..1050：中轴饰物(~810)与右下骨头(~1170)之间的干净底纹+卷草带
patch = work[RY0:RY1, SX:SX + (RX1 - RX0)].copy()
# 羽化边缘融合（左右各12px、上下各8px渐变），避免生硬接缝
ph, pw = RY1 - RY0, RX1 - RX0
feather = np.ones((ph, pw))
ramp_x = np.minimum(np.arange(pw) / 12.0, np.arange(pw)[::-1] / 12.0).clip(0, 1)
ramp_y = np.minimum(np.arange(ph) / 8.0, np.arange(ph)[::-1] / 8.0).clip(0, 1)
feather = np.minimum(ramp_x[None, :], ramp_y[:, None])
region = work[RY0:RY1, RX0:RX1]
work[RY0:RY1, RX0:RX1] = patch * feather[..., None] + region * (1 - feather[..., None])
out = Image.fromarray(work.astype(np.uint8))
# 左侧剩余的「豆」字左边一小段（x<1295 且在金带上方）：洋葱填充
rgb = work
mx = rgb.max(axis=2)
mn = rgb.min(axis=2)
lum = rgb.mean(axis=2)
strip = np.zeros(lum.shape, dtype=bool)
strip[1443:1519, 1258:1295] = (lum[1443:1519, 1258:1295] > 100) & ((mx - mn)[1443:1519, 1258:1295] < 75)
# 该竖条内骨头最右到x≈1262、y<1455，只保护那几像素
strip[1443:1455, 1258:1263] = False
todo = strip.copy()
known = ~todo
for _ in range(300):
    if not todo.any():
        break
    ksum = np.zeros_like(known, dtype=np.float64)
    acc = np.zeros_like(work)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dy == 0 and dx == 0:
                continue
            ksum += np.roll(known.astype(np.float64), (dy, dx), (0, 1))
            acc += np.roll(work * known[..., None], (dy, dx), (0, 1))
    fillnow = todo & (ksum > 0)
    work[fillnow] = acc[fillnow] / ksum[fillnow][..., None]
    known |= fillnow
    todo &= ~fillnow
out = Image.fromarray(work.astype(np.uint8))
blur = out.filter(ImageFilter.GaussianBlur(1.5))
m = Image.fromarray((strip * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.0))
out = Image.composite(blur, out, m)
out.convert("RGB").save(CLEAN_OUT)
print("saved cleaned:", CLEAN_OUT)
