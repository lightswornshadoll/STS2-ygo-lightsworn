# -*- coding: utf-8 -*-
"""融合图鉴按钮图标（v0.4.19 问题4）：ygopro 卡背 cover.jpg 圆形裁切 → 144x144 PNG 带暗色描边圈。
产物: mod/lightsworn/lightsworn/images/ui/fusion_codex.png
"""
import os
from PIL import Image, ImageDraw, ImageFilter

SRC = r"D:\MyCardLibrary\ygopro\textures\cover.jpg"
DST = os.path.join(os.path.dirname(__file__), "..", "mod", "lightsworn", "lightsworn",
                   "images", "ui", "fusion_codex.png")
SIZE = 144  # 2x of 72 显示尺寸，TopBar 里 KeepAspectCentered 缩放

def main():
    img = Image.open(SRC).convert("RGBA")
    w, h = img.size
    side = min(w, h)
    img = img.crop(((w - side) // 2, (h - side) // 2, (w + side) // 2, (h + side) // 2))
    img = img.resize((SIZE, SIZE), Image.LANCZOS)

    # 圆形蒙版（含1.5px羽化边）
    mask = Image.new("L", (SIZE * 4, SIZE * 4), 0)
    d = ImageDraw.Draw(mask)
    pad = 6 * 4
    d.ellipse((pad, pad, SIZE * 4 - pad, SIZE * 4 - pad), fill=255)
    mask = mask.resize((SIZE, SIZE), Image.LANCZOS).filter(ImageFilter.GaussianBlur(0.8))

    out = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    out.paste(img, (0, 0), mask)

    # 暗色描边圈（与游戏顶栏按钮的深色边一致）
    ring = Image.new("RGBA", (SIZE * 4, SIZE * 4), (0, 0, 0, 0))
    dr = ImageDraw.Draw(ring)
    pad = 6 * 4
    width = 3 * 4
    dr.ellipse((pad, pad, SIZE * 4 - pad, SIZE * 4 - pad), outline=(12, 24, 28, 255), width=width)
    ring = ring.resize((SIZE, SIZE), Image.LANCZOS)
    out = Image.alpha_composite(out, ring)

    os.makedirs(os.path.dirname(DST), exist_ok=True)
    out.save(DST)
    print("saved:", os.path.abspath(DST), out.size)

main()
