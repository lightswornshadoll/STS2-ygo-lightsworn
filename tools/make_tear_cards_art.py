# -*- coding: utf-8 -*-
# 珠泪哀歌族（光道 mod）12 张新卡卡图：ygopro <passcode>.jpg → 裁插画面区域 → 250x190 <类名>.png
# 源图均为 400x580 标准 YGO 整卡图（已用像素探测核对橙/绿两种卡框）：
# 插画窗口为 313x313 正方形，内沿 x 44..356、y 101..413（44/357 列与 100/414 行是框的暗边线）。
# 通用裁切：取插画窗口全宽 313px，按 25:19 取高 238px（313*19/25≈237.9），
# 默认在窗口内垂直居中 y0 = 101 + (313-238)//2 = 138；个别卡按构图用 Y_OFF 微调。
from PIL import Image
import os, sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
SRC_DIR = r'D:\MyCardLibrary\ygopro\pics'
OUT_DIR = os.path.join(ROOT, 'mod', 'lightsworn', 'lightsworn', 'images', 'cards')

# (类名.png, passcode, 原卡名, y0 偏移: -N 上移 / +N 下移, 0=居中)
CARDS = [
    ('TrueBloodVampire', '73082255', '真血公 吸血鬼',           0),
    ('HandDestruction',  '72892473', '手札抹杀',                0),
    ('FoolishBurial',    '81439173', '愚蠢的埋葬',              0),
    ('Suliek',           '572850',   '珠泪哀歌族·塞壬人鱼',     0),
    ('Merrli',           '37961969', '珠泪哀歌族·小美人鱼',     0),
    ('Havnis',           '74078255', '珠泪哀歌族·梅洛人鱼',     0),
    ('Reinohart',        '73956664', '珠泪哀歌族·雷诺哈特',     0),
    ('Perlereino',       '77103950', '壹世坏-珍珠世界',         0),
    ('Kitkallos',        '92731385', '珠泪哀歌族·水仙女人鱼',   0),
    ('Rulkallos',        '84330567', '珠泪哀歌族·鲁莎卡人鱼',   0),
    ('KaleidoHeart',     '28226490', '珠泪哀歌族·卡雷多哈特',   0),
    ('Dragostapelia',    '69946549', '捕食植物 犀角龙',         0),
]

X0, X1 = 44, 357           # 插画窗口内沿（宽 313；右开区间，含列 44..356）
ART_TOP, ART_BOT = 101, 414  # 插画窗口内沿上下（下开区间，含行 101..413）
CROP_H = 238               # 313 * 19 / 25 ≈ 237.9 → 238
Y0_DEFAULT = ART_TOP + (ART_BOT - ART_TOP - CROP_H) // 2  # 138

failures = []
for name, code, cn, yoff in CARDS:
    src_path = os.path.join(SRC_DIR, code + '.jpg')
    out_path = os.path.join(OUT_DIR, name + '.png')
    try:
        src = Image.open(src_path).convert('RGB')
        y0 = Y0_DEFAULT + yoff
        y1 = y0 + CROP_H
        if y0 < ART_TOP or y1 > ART_BOT:
            raise ValueError('crop %s out of art window: y %d-%d' % (name, y0, y1))
        crop = src.crop((X0, y0, X1, y1))
        if crop.size != (X1 - X0, CROP_H):
            raise ValueError('bad crop size %s for %s' % (crop.size, name))
        out = crop.resize((250, 190), Image.LANCZOS)
        out.save(out_path)
        print('saved %-20s <- %s (%s) crop y %d-%d -> %dx%d' % (
            name + '.png', code, cn, y0, y1, out.size[0], out.size[1]))
    except Exception as e:
        failures.append((name, code, str(e)))
        print('FAILED %-20s <- %s: %s' % (name, code, e))

# 逐张校验：存在且尺寸恰为 250x190
print('--- verify ---')
bad = []
for name, code, cn, yoff in CARDS:
    out_path = os.path.join(OUT_DIR, name + '.png')
    if not os.path.isfile(out_path):
        bad.append((name, 'missing'))
        continue
    im = Image.open(out_path)
    if im.size != (250, 190) or im.format != 'PNG':
        bad.append((name, '%s %s' % (im.format, im.size)))
if bad:
    print('VERIFY FAILED:', bad)
else:
    print('all %d cards verified: 250x190 PNG' % len(CARDS))
if failures:
    print('PROCESS FAILURES:', failures)
    sys.exit(1)
