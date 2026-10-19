# -*- coding: utf-8 -*-
# 只生成新增「狱火机·撒旦」的卡图与能力图标（不重跑整套提耶拉素材）。
# 卡图规格与 make_tierra_boss_assets.py 的诅咒卡一致：ygopro 卡图裁切 250×190。
from PIL import Image, ImageDraw
import os

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
YGOPRO = r'D:\MyCardLibrary\ygopro\pics'
IMG = os.path.join(ROOT, 'mod', 'lightsworn', 'lightsworn', 'images')
CARD_DIR = os.path.join(IMG, 'cards')
POWER_DIR = os.path.join(IMG, 'powers')

CODE = '60551528'  # 狱火机·撒旦（Infernoid Pirmais）
X0, X1 = 44, 357
ART_TOP, ART_BOT = 101, 414
CROP_H = 238
Y0 = ART_TOP + (ART_BOT - ART_TOP - CROP_H) // 2

os.makedirs(CARD_DIR, exist_ok=True)
os.makedirs(POWER_DIR, exist_ok=True)

src = Image.open(os.path.join(YGOPRO, CODE + '.jpg')).convert('RGB')
crop = src.crop((X0, Y0, X1, Y0 + CROP_H)).resize((250, 190), Image.LANCZOS)
crop.save(os.path.join(CARD_DIR, 'InfernoidSatan.png'))
print('card InfernoidSatan.png')


def round_icon(img, stem):
    w, h = img.size
    side = min(w, h)
    square = img.crop(((w - side) // 2, (h - side) // 2,
                       (w - side) // 2 + side, (h - side) // 2 + side)).convert('RGBA')
    big = side * 4
    mask = Image.new('L', (big, big), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, big - 1, big - 1), fill=255)
    mask = mask.resize((side, side), Image.LANCZOS)
    out = Image.new('RGBA', (side, side), (0, 0, 0, 0))
    out.paste(square, (0, 0), mask)
    for size in (64, 256):
        suffix = '' if size == 64 else '_big'
        out.resize((size, size), Image.LANCZOS).save(
            os.path.join(POWER_DIR, stem + suffix + '.png'))
    print('power', stem + '.png/_big.png')


round_icon(crop, 'tierrasatanshuffle')
