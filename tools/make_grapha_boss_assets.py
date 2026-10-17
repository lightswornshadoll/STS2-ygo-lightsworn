"""把《暗黑界的龙神王 格拉法》三张素材处理成 mod 可直接使用的规格。

输入: D:/download/chrome_download/光道mod素材/暗黑界的龙神王
输出: D:/1-workdata/lightsworn_mod/design/boss素材_暗黑界的龙神王

- 战斗立绘: 去白底 / 去封闭白洞 / 1600x1200 透明画布
- 地图节点: 350x307 白色线稿遮罩 + 350x307 白色圆盘描边（游戏内会被 act 颜色染色）
- 历史记录: 85x85 彩色头部特写 + 85x85 白色剪影描边
"""
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import numpy as np
from collections import deque
import os

SRC = r"D:/download/chrome_download/光道mod素材/暗黑界的龙神王"
BATTLE = os.path.join(SRC, "暗黑界的龙神王 格拉法.png")
MAP = os.path.join(SRC, "格拉法地图节点.png")
HIST = os.path.join(SRC, "格拉法历史记录.png")

OUT = r"D:/1-workdata/lightsworn_mod/design/boss素材_暗黑界的龙神王"
D_BATTLE = os.path.join(OUT, "01_战斗立绘")
D_MAP = os.path.join(OUT, "02_地图节点")
D_HIST = os.path.join(OUT, "03_历史记录")
for d in (D_BATTLE, D_MAP, D_HIST):
    os.makedirs(d, exist_ok=True)

SLUG = "dark_world_grapha"


# ---------------------------------------------------------------- helpers
def fg_mask(im, lum_thresh=232, sat_thresh=30):
    """从四边泛洪，标记与边缘相连的浅色背景；返回前景 bool mask。"""
    rgb = np.asarray(im.convert("RGB")).astype(np.int16)
    lum = rgb.mean(axis=2)
    sat = rgb.max(axis=2) - rgb.min(axis=2)
    cand = ((lum > lum_thresh) & (sat < sat_thresh)).astype(np.uint8) * 255
    m = Image.fromarray(cand, "L").copy()
    w, h = m.size
    step = max(1, min(w, h) // 200)
    seeds = []
    for x in range(0, w, step):
        seeds += [(x, 0), (x, h - 1)]
    for y in range(0, h, step):
        seeds += [(0, y), (w - 1, y)]
    for s in seeds:
        if m.getpixel(s) == 255:
            ImageDraw.floodfill(m, s, 128, thresh=0)
    return ~(np.asarray(m) == 128)


def remove_white_holes(fg, lum, scale=4, area_min=100):
    """翅膀/肢体之间被包住的纯白背景：低分辨率连通域标记后挖掉。"""
    h, w = lum.shape
    light = ((lum > 242) & fg).astype(np.uint8) * 255
    small = Image.fromarray(light).resize((max(1, w // scale), max(1, h // scale)), Image.BOX)
    small_arr = np.asarray(small)
    sm = small_arr > 245
    H, W = sm.shape
    keep = np.zeros_like(sm, bool)
    visited = np.zeros_like(sm, bool)
    for y in range(H):
        for x in range(W):
            if sm[y, x] and not visited[y, x]:
                q = deque([(y, x)]); visited[y, x] = True; pts = []
                while q:
                    yy, xx = q.popleft(); pts.append((yy, xx))
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ny, nx = yy + dy, xx + dx
                        if 0 <= ny < H and 0 <= nx < W and sm[ny, nx] and not visited[ny, nx]:
                            visited[ny, nx] = True; q.append((ny, nx))
                if len(pts) >= area_min:
                    for yy, xx in pts:
                        keep[yy, xx] = True
    keep_img = Image.fromarray((keep * 255).astype(np.uint8)).resize((w, h), Image.NEAREST)
    hole = (np.asarray(keep_img) > 0) & fg & (lum > 235)
    hole = np.asarray(Image.fromarray((hole * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5))) > 0
    return fg & ~hole, int(hole.sum())


def fg_to_rgba(im, fg, erode_px=2, white=245.0, boost=1.35):
    """把白底 RGB + 前景 mask 转成 RGBA；边界用亮度估 alpha 并反白边。"""
    rgb = np.asarray(im.convert("RGB")).astype(np.float32)
    fg_img = Image.fromarray((fg * 255).astype(np.uint8), "L")
    inner = np.asarray(fg_img.filter(ImageFilter.MinFilter(erode_px * 2 + 1))) > 128
    band = fg & ~inner
    lum = rgb.mean(axis=2)
    alpha = np.where(fg, 255.0, 0.0).astype(np.float32)
    a_band = np.clip((white - lum) / white * 255.0 * boost, 0, 255)
    alpha[band] = a_band[band]
    a = np.clip(alpha / 255.0, 1e-6, 1.0)
    C = np.clip((rgb - 255.0 * (1 - a)[..., None]) / a[..., None], 0, 255)
    C[~fg] = 0
    rgba = Image.fromarray(np.dstack([C, alpha]).astype(np.uint8), "RGBA")
    rgba.putalpha(rgba.getchannel("A").filter(ImageFilter.GaussianBlur(0.5)))
    return rgba


def centered(im, w, h):
    canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    canvas.alpha_composite(im, ((w - im.width) // 2, (h - im.height) // 2))
    return canvas


def pad_square(im, pct=0.04):
    side = max(im.width, im.height)
    pad = int(side * pct)
    side += pad * 2
    return centered(im, side, side)


# ---------------------------------------------------------------- 1. battle
b = Image.open(BATTLE).convert("RGB").crop((50, 293, 1508, 1340))  # 已排除右下角水印
rgb = np.asarray(b).astype(np.int16)
blum = rgb.mean(axis=2)
bfg = fg_mask(b)
bfg, holes_px = remove_white_holes(bfg, blum, 4, 100)
brgba = fg_to_rgba(b, bfg, erode_px=2)
battle = centered(brgba, 1600, 1200)
battle.save(os.path.join(D_BATTLE, f"{SLUG}.png"))
print("battle:", battle.size, "holes removed px:", holes_px, "alpha bbox:", battle.getchannel("A").getbbox())


# ---------------------------------------------------------------- 2. map
m = Image.open(MAP).convert("RGB")
marr = np.asarray(m).astype(np.int16)
mlum = marr.mean(axis=2)
black = mlum < 60
ys, xs = np.where(black)
x0, y0, x1, y1 = int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1
cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
rx, ry = (x1 - x0) / 2.0, (y1 - y0) / 2.0

disc = Image.new("L", m.size, 0)
ImageDraw.Draw(disc).ellipse([cx - rx + 4, cy - ry + 4, cx + rx - 4, cy + ry - 4], fill=255)
disc_a = np.asarray(disc).astype(np.float32) / 255.0

# 白色线稿遮罩（alpha=亮度） + 白色圆盘描边（比线稿外扩 25px）
icon_alpha = np.clip((mlum - 90.0) / 120.0 * 255.0, 0, 255) * disc_a
white = np.full_like(mlum, 255, dtype=np.uint8)
icon_hi = Image.fromarray(np.dstack([white, white, white, icon_alpha.astype(np.uint8)]), "RGBA")

outline_l = Image.new("L", m.size, 0)
ImageDraw.Draw(outline_l).ellipse([cx - rx - 25, cy - ry - 25, cx + rx + 25, cy + ry + 25], fill=255)
outline_hi = Image.fromarray(np.dstack([white, white, white, np.asarray(outline_l)]), "RGBA")

# 原色版（黑圆盘 + 白线稿），只给自定义地图节点用
color_hi = Image.fromarray(np.dstack([marr.astype(np.uint8), (disc_a * 255).astype(np.uint8)]), "RGBA")

TARGET_DISC = 290.0
scale = TARGET_DISC / (2 * max(rx, ry))

def place_map(img):
    w = max(1, round(img.width * scale))
    h = max(1, round(img.height * scale))
    return centered(img.resize((w, h), Image.LANCZOS), 350, 307)

icon_350 = place_map(icon_hi)
outline_350 = place_map(outline_hi)
color_350 = place_map(color_hi)
icon_350.save(os.path.join(D_MAP, f"{SLUG}_boss_icon.png"))
outline_350.save(os.path.join(D_MAP, f"{SLUG}_boss_icon_outline.png"))
color_350.save(os.path.join(D_MAP, f"{SLUG}_boss_icon_color.png"))
print("map:", icon_350.size, "disc", (round(2 * rx * scale), round(2 * ry * scale)),
      "icon bbox", icon_350.getchannel("A").getbbox())


# ---------------------------------------------------------------- 3. history
h = Image.open(HIST).convert("RGB")

def load_hist_rgba(box):
    c = h.crop(box)
    rgbc = np.asarray(c).astype(np.int16)
    lum = rgbc.mean(axis=2)
    fg = fg_mask(c)
    fg, _ = remove_white_holes(fg, lum, 4, 60)
    return fg_to_rgba(c, fg, erode_px=2)

def make_outline(icon, grow):
    sil = (np.asarray(icon.getchannel("A")) > 128).astype(np.uint8) * 255
    sil_img = Image.fromarray(sil, "L").filter(ImageFilter.MaxFilter(grow))
    outline = Image.new("RGBA", icon.size, (255, 255, 255, 255))
    outline.putalpha(sil_img)
    return outline

# 主图标：头部特写，圆形取景（85x85 可读性最好，也不会出现方形裁切边）
head = load_hist_rgba((760, 300, 1340, 880))
w, hh = head.size
cx, cy = w / 2.0, hh / 2.0 - 10
rad = min(w, hh) / 2.0 - 8
circle = Image.new("L", (w, hh), 0)
ImageDraw.Draw(circle).ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=255)
circle = circle.filter(ImageFilter.GaussianBlur(1.2))
head.putalpha(Image.composite(head.getchannel("A"), Image.new("L", (w, hh), 0), circle))
head85 = Image.new("RGBA", (85, 85), (0, 0, 0, 0))
head85.alpha_composite(head.resize((81, 81), Image.LANCZOS), (2, 2))
head85.save(os.path.join(D_HIST, f"{SLUG}_boss.png"))
make_outline(head85, 5).save(os.path.join(D_HIST, f"{SLUG}_boss_outline.png"))
print("hist head 85 bbox", head85.getchannel("A").getbbox())

# 备选：全身（保留原图构图，85x85 下头部较小；需要“整条龙”时用）
full = load_hist_rgba((68, 399, 2007, 1780))
full85 = pad_square(full, 0.10).resize((85, 85), Image.LANCZOS)
full85.save(os.path.join(D_HIST, f"{SLUG}_boss_full.png"))
make_outline(full85, 11).save(os.path.join(D_HIST, f"{SLUG}_boss_full_outline.png"))
print("hist full 85 bbox", full85.getchannel("A").getbbox())


# ---------------------------------------------------------------- 4. preview
BG = (24, 20, 30)
sheet = Image.new("RGB", (1400, 980), BG)
d = ImageDraw.Draw(sheet)
font_path = r"C:/Windows/Fonts/msyh.ttc"
font_b = ImageFont.truetype(font_path, 34)
font = ImageFont.truetype(font_path, 22)
font_s = ImageFont.truetype(font_path, 18)
d.text((40, 28), "暗黑界的龙神王 格拉法 — Boss 素材处理预览", font=font_b, fill=(238, 230, 245))

# battle thumb
bt = battle.copy(); bt.thumbnail((820, 615), Image.LANCZOS)
sheet.paste(bt, (40, 100), bt)
d.text((40, 735), "01 战斗立绘  1600×1200 RGBA（透明底，已去水印/白洞）", font=font, fill=(210, 200, 220))

# map tint composite
ot = Image.new("RGBA", (350, 307), (159, 149, 165, 255)); ot.putalpha(outline_350.getchannel("A"))
it = Image.new("RGBA", (350, 307), (24, 15, 36, 255)); it.putalpha(icon_350.getchannel("A"))
comp = Image.new("RGBA", (350, 307), (0, 0, 0, 0)); comp.alpha_composite(ot); comp.alpha_composite(it)
comp_big = comp.resize((480, 421), Image.LANCZOS)
sheet.paste(comp_big, (890, 100), comp_big)
d.text((890, 535), "02 地图节点 350×307（游戏内染色模拟）", font=font, fill=(210, 200, 220))
d.text((890, 565), "深色线稿 = 图标遮罩，浅灰圆盘 = 描边", font=font_s, fill=(170, 160, 185))

# history thumb
hi = Image.open(os.path.join(D_HIST, f"{SLUG}_boss.png")).resize((340, 340), Image.NEAREST)
sheet.paste(hi, (890, 610), hi)
d.text((890, 960 - 30), "03 历史记录 85×85（头部特写，主图标）", font=font, fill=(210, 200, 220))

sheet.save(os.path.join(OUT, "00_预览.png"))
print("preview saved")
