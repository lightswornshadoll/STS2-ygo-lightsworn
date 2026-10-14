# -*- coding: utf-8 -*-
# 影依（Shaddoll）系列 35 张卡卡图：ygopro <passcode>.jpg → 裁插画面区域 → 250x190 <类名>.png
# 裁切参数与 make_tear_cards_art.py 相同：400x580 整卡图，插画窗口 313x313（x 44..356、y 101..413），
# 取全宽 313、高 238（25:19），默认窗口内垂直居中 y0=138，个别卡按构图用 Y_OFF 微调。
# 类名与 design\影依卡牌设计初稿.md 一一对应。
from PIL import Image
import os, sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
SRC_DIR = r'D:\MyCardLibrary\ygopro\pics'
OUT_DIR = os.path.join(ROOT, 'mod', 'lightsworn', 'lightsworn', 'images', 'cards')

# (类名.png, passcode, 原卡名, y0 偏移: -N 上移 / +N 下移, 0=居中)
CARDS = [
    # ---- 本家怪兽 15 ----
    ('ShaddollBeast',          '3717252',   '影依兽',              0),
    ('ShaddollDragon',         '77723643',  '影依龙',              0),
    ('ShaddollSquamata',       '30328508',  '影依蜥蜴',            0),
    ('ShaddollFalco',          '37445295',  '影依猎鹰',            0),
    ('ShaddollHedgehog',       '4939890',   '影依刺猬',            0),
    ('ShaddollHound',          '52551211',  '影依猎犬',            0),
    ('NaelshaddollAriel',      '97518132',  '影依巫女 艾莉娅儿',    0),
    ('NehshaddollGenius',      '66675911',  '神星之影 路径灵',      0),
    ('QadshaddollKeios',       '24635329',  '神圣之影 商神杖灵',    0),
    ('ReeshaddollWendi',       '51023024',  '影灵之翼 文蒂',        0),
    ('HelshaddollHollow',      '92079625',  '影依的炎核 虚梦狱',    0),
    ('TohushaddollGrysta',     '95072744',  '影雄之烬 神子晶',      0),
    ('ShaddollConstruct',      '86938484',  '影依·拿非利',          0),
    ('ShaddollZefranaga',      '58016954',  '救影依-神数纳迦',      0),
    ('ShaddollZefracore',      '95401059',  '绊影依-神数原核',      0),
    # ---- 神影依 Token 9 ----
    ('ElShaddollWinda',        '94977269',  '神影依·米德拉什',      0),
    ('ElShaddollConstruct',    '20366274',  '神影依·拿非利',        0),
    ('ElShaddollWendigo',      '74009824',  '神影依·文迪戈',        0),
    ('ElShaddollGrysta',       '48424886',  '神影依·神子晶',        0),
    ('ElShaddollShekhinaga',   '74822425',  '神影依·舍金纳迦',      0),
    ('ElShaddollAnoyatyllis',  '19261966',  '神影依·异花莉莉丝',    0),
    ('ElShaddollApkallone',    '50907446',  '神影依·七贤巨鲲魔',    0),
    ('ElShaddollMeshahrail',   '32467459',  '神影依·米沙赫雷恶',    0),
    ('ReeshaddollWendikurhu',  '8852158',   '影灵翼骑 影文蒂',      0),
    # ---- 魔法 5 ----
    ('ShaddollFusion',         '44394295',  '影依融合',            0),
    ('ElShaddollFusion',       '6417578',   '与神之假身的接触',      0),
    ('NepheShaddollFusion',    '60226558',  '假魂的同化',           0),
    ('PurgatoryRelease',       '61345801',  '炼狱的乖放',           0),
    ('FrozenHeartShadow',      '34950192',  '冻结之心映照的神影',    0),
    # ---- 陷阱 6 ----
    ('ShaddollCore',           '4904633',   '影依的原核',           0),
    ('ShaddollSchism',         '21011044',  '影依的伪典',           0),
    ('ReshShaddollIncarnation','23912837',  '影光的圣选士',         0),
    ('PurushaddollAeon',       '78942513',  '通向魂源的影劫回归',    0),
    ('SinisterShadowGames',    '77505534',  '堕影的蠢动',           0),
    ('CurseShadowPrison',      '81788994',  '影牢之咒缚',           0),
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
        print('saved %-26s <- %s (%s) crop y %d-%d -> %dx%d' % (
            name + '.png', code, cn, y0, y1, out.size[0], out.size[1]))
    except Exception as e:
        failures.append((name, code, str(e)))
        print('FAILED %-26s <- %s: %s' % (name, code, e))

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
