# -*- coding: utf-8 -*-
# 狱火机·提耶拉 / 创星神·提耶拉 Boss 素材：
#   ① 两阶段立绘（1536×1536 透明底）
#   ② 地图节点 350×307 白色蒙版（+描边）
#   ③ 历史记录 85×85（裁创星神头部，+白色描边底）
#   ④ 10 张诅咒卡图 250×190（ygopro pics）
#   ⑤ 能力图标 64/256 圆裁
from PIL import Image, ImageDraw, ImageFilter
import os
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
SRC = r'D:\download\chrome_download\光道mod素材\提耶拉'
YGOPRO = r'D:\MyCardLibrary\ygopro\pics'
IMG = os.path.join(ROOT, 'mod', 'lightsworn', 'lightsworn', 'images')
MONSTER_DIR = os.path.join(IMG, 'monsters')
CARD_DIR = os.path.join(IMG, 'cards')
POWER_DIR = os.path.join(IMG, 'powers')
MAP_DIR = os.path.join(IMG, 'map', 'lightsworn')
HISTORY_DIR = os.path.join(IMG, 'ui', 'run_history')

for d in (MONSTER_DIR, CARD_DIR, POWER_DIR, MAP_DIR, HISTORY_DIR):
    os.makedirs(d, exist_ok=True)

failures = []

# ---------- ① 立绘 ----------
try:
    p1 = Image.open(os.path.join(SRC, '狱火机 提耶拉.png')).convert('RGBA')
    p2 = Image.open(os.path.join(SRC, '创星神 提耶拉.png')).convert('RGBA')
    p1.save(os.path.join(MONSTER_DIR, 'infernoid_tierra.png'))
    p2.save(os.path.join(MONSTER_DIR, 'infernoid_tierra_source.png'))
    print('monster portraits copied:', p1.size, p2.size)
except Exception as e:
    failures.append(('portraits', str(e)))
    print('FAILED portraits', e)
    p1 = p2 = None

# ---------- ② 地图图标（白色蒙版） ----------
# 源图 2048×2048 是纯剪影（alpha 为主）+ 外圈。取 alpha>64 作为实心区，
# icon 与 outline 共用同一裁剪/缩放，保证叠放时严格对齐。
try:
    map_src = Image.open(os.path.join(SRC, '提耶拉地图.png')).convert('RGBA')
    alpha = map_src.getchannel('A')
    mask = alpha.point(lambda v: 255 if v > 64 else 0)
    bbox = mask.getbbox()
    mask = mask.crop(bbox)
    # 外扩描边：MaxFilter 让白色蒙版外缘长出一圈
    outline_mask = mask.filter(ImageFilter.MaxFilter(11))

    target_w, target_h = 350, 307
    pad = 6
    scale = min((target_w - pad * 2) / mask.width, (target_h - pad * 2) / mask.height)
    new_w, new_h = max(1, round(mask.width * scale)), max(1, round(mask.height * scale))

    def fit(m):
        m = m.resize((new_w, new_h), Image.LANCZOS)
        canvas = Image.new('L', (target_w, target_h), 0)
        canvas.paste(m, ((target_w - new_w) // 2, (target_h - new_h) // 2))
        return canvas

    icon_mask = fit(mask)
    outline_mask_fit = fit(outline_mask)
    icon = Image.new('RGBA', (target_w, target_h), (255, 255, 255, 0))
    icon.putalpha(icon_mask)
    outline = Image.new('RGBA', (target_w, target_h), (255, 255, 255, 0))
    outline.putalpha(outline_mask_fit)
    icon.save(os.path.join(MAP_DIR, 'infernoid_tierra_boss_icon.png'))
    outline.save(os.path.join(MAP_DIR, 'infernoid_tierra_boss_icon_outline.png'))
    print('map icon:', icon.size, 'source bbox', bbox)
except Exception as e:
    failures.append(('map_icon', str(e)))
    print('FAILED map icon', e)

# ---------- ③ 历史记录图标（裁创星神头部） ----------
try:
    head_box = (590, 200, 970, 580)   # 380×380，含角与火焰
    head = p2.crop(head_box).resize((85, 85), Image.LANCZOS)
    big = 85 * 4
    circle = Image.new('L', (big, big), 0)
    ImageDraw.Draw(circle).ellipse((0, 0, big - 1, big - 1), fill=255)
    circle = circle.resize((85, 85), Image.LANCZOS)
    icon = Image.new('RGBA', (85, 85), (0, 0, 0, 0))
    icon.paste(head, (0, 0), circle)
    icon.save(os.path.join(HISTORY_DIR, 'infernoid_tierra_boss.png'))

    big2 = 86 * 4
    circle2 = Image.new('L', (big2, big2), 0)
    ImageDraw.Draw(circle2).ellipse((0, 0, big2 - 1, big2 - 1), fill=255)
    circle2 = circle2.resize((86, 86), Image.LANCZOS)
    ol = Image.new('RGBA', (85, 85), (255, 255, 255, 0))
    ol.paste(Image.new('RGBA', (86, 86), (255, 255, 255, 255)), (-1, -1), circle2)
    ol.save(os.path.join(HISTORY_DIR, 'infernoid_tierra_boss_outline.png'))
    print('history icon 85x85 from p2 head', head_box)
except Exception as e:
    failures.append(('history_icon', str(e)))
    print('FAILED history icon', e)

# ---------- ④ 诅咒卡图（ygopro 250×190） ----------
CARDS = [
    ('InfernoidDecatron',     '58446973', '狱火机十进管'),
    ('InfernoidBeelzebub',    '26034577', '狱火机·别西卜'),
    ('InfernoidLucifugus',    '52038272', '狱火机·路西弗格'),
    ('InfernoidAstaroth',     '89423971', '狱火机·阿斯塔罗特'),
    ('InfernoidAsmodeus',     '25811989', '狱火机·阿斯蒙蒂斯'),
    ('InfernoidBelphegor',    '96055137', '狱火机·贝尔芬格'),
    ('InfernoidBaal',         '51316684', '狱火机·巴力'),
    ('InfernoidAdrammelech',  '88301393', '狱火机·亚得米勒'),
    ('InfernoidLilith',       '23440231', '狱火机·莉莉丝'),
    ('InfernoidOnuncu',       '14799437', '狱火机·拿玛'),
]

X0, X1 = 44, 357
ART_TOP, ART_BOT = 101, 414
CROP_H = 238
Y0 = ART_TOP + (ART_BOT - ART_TOP - CROP_H) // 2

card_imgs = {}
for name, code, cn in CARDS:
    try:
        src = Image.open(os.path.join(YGOPRO, code + '.jpg')).convert('RGB')
        crop = src.crop((X0, Y0, X1, Y0 + CROP_H)).resize((250, 190), Image.LANCZOS)
        crop.save(os.path.join(CARD_DIR, name + '.png'))
        card_imgs[name] = crop
        print('card %-24s <- %s (%s)' % (name, code, cn))
    except Exception as e:
        failures.append((name, str(e)))
        print('FAILED card', name, e)

def round_icon(src_img, stem, crop_box=None):
    img = src_img
    if crop_box:
        img = img.crop(crop_box)
    w, h = img.size
    side = min(w, h)
    square = img.crop(((w - side) // 2, (h - side) // 2,
                       (w - side) // 2 + side, (h - side) // 2 + side)).convert('RGBA')
    big = side * 4
    m = Image.new('L', (big, big), 0)
    ImageDraw.Draw(m).ellipse((0, 0, big - 1, big - 1), fill=255)
    m = m.resize((side, side), Image.LANCZOS)
    out = Image.new('RGBA', (side, side), (0, 0, 0, 0))
    out.paste(square, (0, 0), m)
    for size in (64, 256):
        suffix = '' if size == 64 else '_big'
        out.resize((size, size), Image.LANCZOS).save(os.path.join(POWER_DIR, stem + suffix + '.png'))
    print('power %-24s <- %s' % (stem, 'crop'))

# ---------- ⑤ 能力图标 ----------
try:
    def card(name):
        return card_imgs[name]

    round_icon(card('InfernoidDecatron'), 'infernoidmaterial')
    round_icon(p2, 'starcreation', (590, 200, 970, 580))
    round_icon(card('InfernoidOnuncu'), 'starcreationlock')
    round_icon(card('InfernoidBeelzebub'), 'tierrabeelzebub')
    round_icon(card('InfernoidBeelzebub'), 'tierrashuffleone')
    round_icon(card('InfernoidAsmodeus'), 'tierraasmodeus')
    round_icon(card('InfernoidAsmodeus'), 'tierradiscardone')
    round_icon(card('InfernoidBelphegor'), 'tierrabelphegor')
    round_icon(card('InfernoidLilith'), 'tierralilith')
    round_icon(card('InfernoidLilith'), 'tierraattacknullify')
    round_icon(card('InfernoidOnuncu'), 'tierranaamah')
    round_icon(card('InfernoidOnuncu'), 'tierraskillnullify')
    # 提耶拉本体卡图/头像用于融合、封印与终局图标
    tierra_tmp = os.path.join(ROOT, 'research', 'tierra_preview', '_tierra_card.png')
    src = Image.open(os.path.join(YGOPRO, '82734805.jpg')).convert('RGB')
    crop_t = src.crop((X0, Y0, X1, Y0 + CROP_H)).resize((250, 190), Image.LANCZOS)
    crop_t.save(tierra_tmp)
    round_icon(crop_t, 'tierrafusionnullify')
    round_icon(crop_t, 'tierrafusioncomplete')
    # 阶段门 buff 图标 =「炼狱的狂宴」（Void Feast）
    feast = Image.open(os.path.join(YGOPRO, '31548814.jpg')).convert('RGB')
    feast_crop = feast.crop((X0, Y0, X1, Y0 + CROP_H)).resize((250, 190), Image.LANCZOS)
    round_icon(feast_crop, 'tierraphasegate')
    round_icon(p2, 'tierraapocalypse', (590, 200, 970, 580))
    # 二阶段四招中的洪水/虚梦/灾天用原卡图
    for name, code, stem in (
            ('Flood', '34446231', 'tierraflood'),
            ('VoidImagination', '31444249', 'tierravirtualdream'),
            ('VoidImagination', '31444249', 'tierrahalfdamage'),
            ('VoidApocalypse', '7337976', 'tierradisaster')):
        s = Image.open(os.path.join(YGOPRO, code + '.jpg')).convert('RGB')
        c = s.crop((X0, Y0, X1, Y0 + CROP_H)).resize((250, 190), Image.LANCZOS)
        round_icon(c, stem)
except Exception as e:
    failures.append(('power_icons', str(e)))
    print('FAILED power icons', e)

# ---------- 校验 ----------
bad = []
for name, _, _ in CARDS:
    p = os.path.join(CARD_DIR, name + '.png')
    if not os.path.isfile(p):
        bad.append((name, 'missing'))
    else:
        im = Image.open(p)
        if im.size != (250, 190):
            bad.append((name, im.size))

for stem in ('infernoidmaterial', 'starcreation', 'starcreationlock', 'tierrabeelzebub',
             'tierrashuffleone', 'tierraasmodeus', 'tierradiscardone', 'tierrabelphegor',
             'tierralilith', 'tierraattacknullify', 'tierranaamah', 'tierraskillnullify',
             'tierrafusionnullify', 'tierrafusioncomplete', 'tierraphasegate',
             'tierraapocalypse', 'tierraflood', 'tierravirtualdream', 'tierrahalfdamage', 'tierradisaster'):
    for suffix, size in (('', 64), ('_big', 256)):
        p = os.path.join(POWER_DIR, stem + suffix + '.png')
        if not os.path.isfile(p):
            bad.append((stem + suffix, 'missing'))
        else:
            im = Image.open(p)
            if im.size != (size, size):
                bad.append((stem + suffix, im.size))

for p, size in (
        (os.path.join(MONSTER_DIR, 'infernoid_tierra.png'), (1536, 1536)),
        (os.path.join(MONSTER_DIR, 'infernoid_tierra_source.png'), (1536, 1536)),
        (os.path.join(MAP_DIR, 'infernoid_tierra_boss_icon.png'), (350, 307)),
        (os.path.join(MAP_DIR, 'infernoid_tierra_boss_icon_outline.png'), (350, 307)),
        (os.path.join(HISTORY_DIR, 'infernoid_tierra_boss.png'), (85, 85)),
        (os.path.join(HISTORY_DIR, 'infernoid_tierra_boss_outline.png'), (85, 85))):
    if not os.path.isfile(p):
        bad.append((os.path.basename(p), 'missing'))
    else:
        im = Image.open(p)
        if im.size != size:
            bad.append((os.path.basename(p), im.size))

if bad or failures:
    print('VERIFY FAILED:', bad, failures)
    sys.exit(1)
print('all Tierra boss assets verified')
