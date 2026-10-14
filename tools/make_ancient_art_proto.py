# -*- coding: utf-8 -*-
"""临时原型：先古卡全框卡图（606x852）两种构图方案对比。
A=cover 覆盖裁切（锐利满幅，裁掉左右）  B=blur-extend 模糊延展（保留全构图，上下补模糊带）
输出 tools\_anc_cand.png 对比图供人工挑选。
"""
import os
from PIL import Image, ImageFilter, ImageDraw

TOOLS = os.path.dirname(os.path.abspath(__file__))
W, H = 606, 852

CARDS = {
    'aegis': (r'D:\MyCardLibrary\ygopro\pics\25218587.jpg', (48, 103, 350, 417)),
    'lod':   (r'D:\MyCardLibrary\ygopro\pics\83027236.jpg',  (50, 100, 350, 417)),
}


def cover(src, win):
    art = src.crop(win)
    aw, ah = art.size
    scale = H / ah
    big = art.resize((round(aw * scale), H), Image.LANCZOS)
    left = (big.width - W) // 2
    return big.crop((left, 0, left + W, H))


def extend(src, win):
    art = src.crop(win)
    aw, ah = art.size
    scale = W / aw
    mid = art.resize((W, round(ah * scale)), Image.LANCZOS)
    canvas = Image.new('RGB', (W, H))
    y0 = (H - mid.height) // 2
    # 背景：整张拉伸模糊
    bg = art.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(24))
    canvas.paste(bg, (0, 0))
    # 边缘带：把顶行/底行拉伸填充后再轻微模糊
    top = art.crop(win[0:1] + (win[1], win[2], win[1] + max(1, ah // 8)))
    bot = art.crop((win[0], win[3] - max(1, ah // 8), win[2], win[3]))
    canvas.paste(top.resize((W, y0), Image.LANCZOS).filter(ImageFilter.GaussianBlur(10)), (0, 0))
    canvas.paste(bot.resize((W, H - y0 - mid.height), Image.LANCZOS).filter(ImageFilter.GaussianBlur(10)),
                 (0, y0 + mid.height))
    canvas.paste(mid, (0, y0))
    return canvas


def main():
    sheet = Image.new('RGB', (4 * (W // 3 + 8) + 8, H // 3 + 40), (25, 25, 25))
    d = ImageDraw.Draw(sheet)
    x = 8
    for name, (srcp, win) in CARDS.items():
        src = Image.open(srcp).convert('RGB')
        for label, img in (('A-cover', cover(src, win)), ('B-extend', extend(src, win))):
            small = img.resize((W // 3, H // 3), Image.LANCZOS)
            sheet.paste(small, (x, 28))
            d.text((x, 10), f'{name} {label}', fill=(255, 255, 255))
            x += small.width + 8
    out = os.path.join(TOOLS, '_anc_cand.png')
    sheet.save(out)
    print('written', out, sheet.size)


if __name__ == '__main__':
    main()
