# -*- coding: utf-8 -*-
"""圣女静态立绘角色资产生成（v0.4.7）
源图: D:\\download\\chrome_download\\光道圣女\\{圣女战斗,背景,能量球}.png
输出: mod\\lightsworn\\lightsworn\\images\\character\\*.png
      mod\\lightsworn\\lightsworn\\visuals\\saint_select_bg.tscn 之外的图全在这里生成；
      战斗图抠图(白底floodfill+种子连通域保大弃水印)、选人按钮/图标/地图标记从背景图裁脸、
      能量球抠白底。跑完自动输出预览图到 tools\\preview_static_char\\。
"""
import os
from collections import deque
from PIL import Image, ImageDraw, ImageFilter, ImageOps

SRC = r"D:\download\chrome_download\光道圣女"
DST = r"D:\1-workdata\lightsworn_mod\mod\lightsworn\lightsworn\images\character"
PREVIEW = r"D:\1-workdata\lightsworn_mod\tools\preview_static_char"

# ---- 背景图裁脸参数（占源图宽/高的比例，跑了看预览再调） ----
# 按钮框：宽0.16 高按 132:195 比例推出；圆心=脸中心
FACE_CX, FACE_CY = 0.500, 0.300   # 脸中心（含兜帽整体略下）
BUTTON_W = 0.170                   # 按钮裁剪宽（比例）
ICON_W   = 0.135                   # 顶栏图标裁剪宽（近方形）
MARKER_W = 0.150                   # 地图标记裁剪宽（49:64 比例）

os.makedirs(DST, exist_ok=True)
os.makedirs(PREVIEW, exist_ok=True)


def floodfill_white_to_alpha(im: Image.Image, thresh: int) -> Image.Image:
    """四角 floodfill 白底 → alpha=0，返回 RGBA。"""
    im = im.convert("RGB")
    marker = (255, 0, 254)
    w, h = im.size
    for pt in [(1, 1), (w - 2, 1), (1, h - 2), (w - 2, h - 2)]:
        try:
            ImageDraw.floodfill(im, pt, marker, thresh=thresh)
        except Exception:
            pass
    px = im.load()
    rgba = im.convert("RGBA")
    p = rgba.load()
    for y in range(h):
        for x in range(w):
            if px[x, y] == marker:
                p[x, y] = (0, 0, 0, 0)
    return rgba


def keep_component_from_seed(rgba: Image.Image, seed_frac=(0.50, 0.45)) -> Image.Image:
    """只保留包含 seed 的不透明连通域（丢掉水印等孤岛）。纯 BFS，1152² 约3-6秒。"""
    w, h = rgba.size
    px = rgba.load()
    sx, sy = int(w * seed_frac[0]), int(h * seed_frac[1])
    if px[sx, sy][3] == 0:
        # seed 被抠了就向右下扫到第一个不透明点
        found = False
        for dy in range(0, h - sy, 4):
            for dx in range(0, w - sx, 4):
                if px[min(sx + dx, w - 1), min(sy + dy, h - 1)][3] > 0:
                    sx, sy = min(sx + dx, w - 1), min(sy + dy, h - 1)
                    found = True
                    break
            if found:
                break
        print(f"  [warn] seed 落在透明区，改用 ({sx},{sy})")
    import numpy as np
    arr = np.zeros((h, w), dtype=bool)
    for y in range(h):
        for x in range(w):
            arr[y, x] = px[x, y][3] > 0
    keep = np.zeros((h, w), dtype=bool)
    q = deque([(sy, sx)])
    keep[sy, sx] = True
    while q:
        y, x = q.popleft()
        if x > 0 and arr[y, x - 1] and not keep[y, x - 1]:
            keep[y, x - 1] = True; q.append((y, x - 1))
        if x < w - 1 and arr[y, x + 1] and not keep[y, x + 1]:
            keep[y, x + 1] = True; q.append((y, x + 1))
        if y > 0 and arr[y - 1, x] and not keep[y - 1, x]:
            keep[y - 1, x] = True; q.append((y - 1, x))
        if y < h - 1 and arr[y + 1, x] and not keep[y + 1, x]:
            keep[y + 1, x] = True; q.append((y + 1, x))
    r, g, b, a = rgba.split()
    import numpy as np
    a_np = np.array(a) * keep
    a = Image.fromarray(a_np.astype("uint8"))
    rgba.putalpha(a)
    return rgba


def crop_resize(img: Image.Image, cx, cy, box_w_frac, aspect, out_size):
    """按比例框裁剪后缩放。cx/cy/宽均为占原图宽/高比例，aspect=宽/高。"""
    W, H = img.size
    bw = box_w_frac * W
    bh = bw / aspect
    x0 = cx * W - bw / 2
    y0 = cy * H - bh / 2
    box = (x0, y0, x0 + bw, y0 + bh)
    return img.crop(tuple(int(round(v)) for v in box)).resize(out_size, Image.LANCZOS)


def on_dark(img: Image.Image, name):
    """拼到深灰底上出预览（检查白边/水印）。"""
    bg = Image.new("RGBA", img.size, (40, 44, 52, 255))
    bg.alpha_composite(img.convert("RGBA"))
    bg.convert("RGB").save(os.path.join(PREVIEW, name))


def main():
    # ============ 1. 战斗立绘抠图 ============
    print("== 战斗立绘 ==")
    battle = Image.open(os.path.join(SRC, "圣女战斗.png"))
    print("  源尺寸:", battle.size)
    cut = floodfill_white_to_alpha(battle, thresh=30)
    cut = keep_component_from_seed(cut, seed_frac=(0.50, 0.45))
    a = cut.getchannel("A").filter(ImageFilter.MinFilter(3))  # 收1px白边
    cut.putalpha(a)
    bbox = cut.getbbox()
    cut = cut.crop(bbox)
    # 内容归一到高1000
    scale = 1000 / cut.height
    cut = cut.resize((round(cut.width * scale), 1000), Image.LANCZOS)
    cut.save(os.path.join(DST, "battle.png"))
    print("  battle.png:", cut.size, " (C# 场景锚点：脚底≈bbox底)")
    on_dark(cut, "preview_battle.png")

    # ============ 2. 背景图 → 选人背景 + 按钮脸 + 图标 + 地图标记 ============
    print("== 背景图 ==")
    bg = Image.open(os.path.join(SRC, "背景.png")).convert("RGB")
    W, H = bg.size
    print("  源尺寸:", bg.size)
    bg.save(os.path.join(DST, "select_bg.png"))

    btn = crop_resize(bg, FACE_CX, FACE_CY, BUTTON_W, 132 / 195, (132, 195))
    btn.save(os.path.join(DST, "select_button.png"))
    on_dark(btn, "preview_button.png")

    icon = crop_resize(bg, FACE_CX, FACE_CY, ICON_W, 1.0, (96, 96))
    icon.save(os.path.join(DST, "icon.png"))
    on_dark(icon, "preview_icon.png")

    # 描边版：白色剪影
    sil = Image.new("RGBA", icon.size, (255, 255, 255, 0))
    sil.paste((255, 255, 255, 255), mask=icon.convert("L"))
    sil.save(os.path.join(DST, "icon_outline.png"))

    marker = crop_resize(bg, FACE_CX, FACE_CY, MARKER_W, 49 / 64, (49, 64))
    marker.save(os.path.join(DST, "map_marker.png"))
    on_dark(marker, "preview_marker.png")

    # ============ 3. 能量球抠图 ============
    print("== 能量球 ==")
    orb = Image.open(os.path.join(SRC, "能量球.png"))
    print("  源尺寸:", orb.size)
    # 白底 floodfill（低阈值只抠纯白，保住辉光渐变）+ alpha 高斯羽化
    ocut = floodfill_white_to_alpha(orb, thresh=12)
    a = ocut.getchannel("A").filter(ImageFilter.GaussianBlur(1.5))
    ocut.putalpha(a)
    ob = ocut.getbbox()
    ocut = ocut.crop(ob)
    if max(ocut.size) > 512:
        s = 512 / max(ocut.size)
        ocut = ocut.resize((round(ocut.width * s), round(ocut.height * s)), Image.LANCZOS)
    ocut.save(os.path.join(DST, "energy_orb.png"))
    print("  energy_orb.png:", ocut.size)
    on_dark(ocut, "preview_orb.png")

    # 4×4 全透明（能量计数器旋转层占位）
    Image.new("RGBA", (4, 4), (0, 0, 0, 0)).save(os.path.join(DST, "transparent.png"))

    print("完成 →", DST)


if __name__ == "__main__":
    main()
