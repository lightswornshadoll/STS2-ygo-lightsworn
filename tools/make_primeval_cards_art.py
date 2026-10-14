# -*- coding: utf-8 -*-
"""v0.4.32 新卡美术：壹世坏2张卡图（ygopro 400x580 → 裁插画区 → 250x190）+ 2张能力图标（卡图中央圆形 64/256）。
用法: py tools\\make_primeval_cards_art.py
裁切参数与 make_tear_cards_art.py 一致：插画内沿 x 44..356、y 101..413，取 313x238（25:19）垂直居中。
"""
import os
from PIL import Image, ImageDraw

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
SRC_DIR = r'D:\MyCardLibrary\ygopro\pics'
IMAGES = os.path.join(ROOT, 'mod', 'lightsworn', 'lightsworn', 'images')

# (类名, passcode, 原卡名, 卡图y0偏移)
CARDS = [
    ('PrimevalCry',    '74920585', '壹世坏奏响的哀唱', 0),
    ('PrimevalScream', '6767771',  '劈穿壹世坏的弦声', 0),
    ('PrimevalEcho',   '1329620',  '壹世坏清澈的残响', 0),
]
# 能力图标：power文件名 -> 卡图类名
POWER_ICONS = {
    'primevalscream': 'PrimevalScream',
    'shaddollschism': 'ShaddollSchism',
    'purushaddollaeon': 'PurushaddollAeon',
}

X0, X1 = 44, 357
ART_TOP, ART_BOT = 101, 414
CROP_H = 238
Y0_DEFAULT = ART_TOP + (ART_BOT - ART_TOP - CROP_H) // 2


def make_card_art():
    for name, code, cn, yoff in CARDS:
        src_path = os.path.join(SRC_DIR, code + '.jpg')
        out_path = os.path.join(IMAGES, 'cards', name + '.png')
        src = Image.open(src_path).convert('RGB')
        y0 = Y0_DEFAULT + yoff
        y1 = y0 + CROP_H
        assert ART_TOP <= y0 and y1 <= ART_BOT, f'{name} crop out of art window'
        crop = src.crop((X0, y0, X1, y1))
        out = crop.resize((250, 190), Image.LANCZOS)
        out.save(out_path)
        print('card art written:', os.path.normpath(out_path))


def make_round(src_path, out_base):
    img = Image.open(src_path).convert('RGBA')
    w, h = img.size
    side = min(w, h)
    left, top = (w - side) // 2, (h - side) // 2
    square = img.crop((left, top, left + side, top + side))
    big = side * 4
    mask = Image.new('L', (big, big), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, big - 1, big - 1), fill=255)
    mask = mask.resize((side, side), Image.LANCZOS)
    round_img = Image.new('RGBA', (side, side), (0, 0, 0, 0))
    round_img.paste(square, (0, 0), mask)
    for size in (64, 256):
        out = round_img.resize((size, size), Image.LANCZOS)
        suffix = '' if size == 64 else '_big'
        out_path = os.path.join(IMAGES, 'powers', out_base + suffix + '.png')
        out.save(out_path)
        print('power icon written:', os.path.normpath(out_path))


def main():
    make_card_art()
    for base, card in POWER_ICONS.items():
        src = os.path.join(IMAGES, 'cards', card + '.png')
        if not os.path.exists(src):
            print('!! 缺卡图（影依的伪典卡图待有后再补图标）:', src)
            continue
        make_round(src, base)


if __name__ == '__main__':
    main()
