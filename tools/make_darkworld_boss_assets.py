# -*- coding: utf-8 -*-
# 暗黑界的龙神王 Boss 素材：四神将 + 洗脑状态卡图（250x190），洗脑/诱惑能力图标（64/256 圆形）。
from PIL import Image, ImageDraw
import os
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
SRC_DIR = r'D:\MyCardLibrary\ygopro\pics'
IMG = os.path.join(ROOT, 'mod', 'lightsworn', 'lightsworn', 'images')
CARD_DIR = os.path.join(IMG, 'cards')
POWER_DIR = os.path.join(IMG, 'powers')

CARDS = [
    ('DarkWorldKelt',        '34968834', '暗黑界的鬼神 凯勒特'),
    ('DarkWorldLatinum',     '15667446', '暗黑界的斗神 拉提纳'),
    ('DarkWorldSillva',      '32619583', '暗黑界的军神 希尔瓦'),
    ('DarkWorldGoldd',       '78004197', '暗黑界的武神 高尔德'),
    ('DarkWorldBrainwashing', '10131855', '暗黑界的洗脑'),
]

X0, X1 = 44, 357
ART_TOP, ART_BOT = 101, 414
CROP_H = 238
Y0 = ART_TOP + (ART_BOT - ART_TOP - CROP_H) // 2

failures = []


def crop_card(code, out_path):
    src = Image.open(os.path.join(SRC_DIR, code + '.jpg')).convert('RGB')
    crop = src.crop((X0, Y0, X1, Y0 + CROP_H))
    out = crop.resize((250, 190), Image.LANCZOS)
    out.save(out_path)
    return out


def make_round(card_img, out_base):
    w, h = card_img.size
    side = min(w, h)
    left, top = (w - side) // 2, (h - side) // 2
    square = card_img.crop((left, top, left + side, top + side)).convert('RGBA')
    big = side * 4
    mask = Image.new('L', (big, big), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, big - 1, big - 1), fill=255)
    mask = mask.resize((side, side), Image.LANCZOS)
    out = Image.new('RGBA', (side, side), (0, 0, 0, 0))
    out.paste(square, (0, 0), mask)
    for size in (64, 256):
        suffix = '' if size == 64 else '_big'
        out.resize((size, size), Image.LANCZOS).save(
            os.path.join(POWER_DIR, out_base + suffix + '.png'))


os.makedirs(CARD_DIR, exist_ok=True)
os.makedirs(POWER_DIR, exist_ok=True)

card_imgs = {}
for name, code, cn in CARDS:
    try:
        out_path = os.path.join(CARD_DIR, name + '.png')
        card_imgs[name] = crop_card(code, out_path)
        print('card  %-24s <- %s (%s)' % (name, code, cn))
    except Exception as e:
        failures.append((name, str(e)))
        print('FAILED card', name, e)

if 'DarkWorldBrainwashing' in card_imgs:
    make_round(card_imgs['DarkWorldBrainwashing'], 'darkworldbrainwash')
    print('power darkworldbrainwash <- DarkWorldBrainwashing')

try:
    import tempfile
    tmp = os.path.join(tempfile.gettempdir(), 'dw_grapha_card.png')
    boss_card = crop_card('39552584', tmp)
    make_round(boss_card, 'darkworldtemptation')
    print('power darkworldtemptation <- 39552584')
except Exception as e:
    failures.append(('darkworldtemptation', str(e)))
    print('FAILED power darkworldtemptation', e)

# v0.6.4「暗黑界的侵蚀」：用「暗黑界之门」卡图做图标。
try:
    import tempfile
    tmp = os.path.join(tempfile.gettempdir(), 'dw_erosion_card.png')
    gate_card = crop_card('33017655', tmp)
    make_round(gate_card, 'darkworlderosion')
    print('power darkworlderosion <- 33017655')
except Exception as e:
    failures.append(('darkworlderosion', str(e)))
    print('FAILED power darkworlderosion', e)

bad = []
for name, code, cn in CARDS:
    path = os.path.join(CARD_DIR, name + '.png')
    if not os.path.isfile(path):
        bad.append((name, 'missing'))
        continue
    im = Image.open(path)
    if im.size != (250, 190):
        bad.append((name, im.size))
for stem in ('darkworldbrainwash', 'darkworldtemptation', 'darkworlderosion'):
    for suffix, size in (('', 64), ('_big', 256)):
        path = os.path.join(POWER_DIR, stem + suffix + '.png')
        if not os.path.isfile(path):
            bad.append((stem + suffix, 'missing'))
            continue
        im = Image.open(path)
        if im.size != (size, size):
            bad.append((stem + suffix, im.size))

if bad or failures:
    print('VERIFY FAILED:', bad, failures)
    sys.exit(1)
print('all card art 250x190 + power icons 64/256 verified')
