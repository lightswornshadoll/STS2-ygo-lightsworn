# -*- coding: utf-8 -*-
"""光道圣女角色资产构建脚本
从 research/pck_dump 提取的 Silent(女刺客) Spine 资源生成「光道圣女」形象:
  - 绿斗篷→白袍, 青匕首→金光刃, 白发→橙金发, 深肤→浅肤, 兽骨→白金圣徽
  - 修改 .spatlas 的 source_path 指向 mod 自己的贴图
  - 生成商人/休息处/选人背景的最小场景脚手架(纯核心节点, 编辑器可解析)
输出到 mod/lightsworn/lightsworn/{visuals,images/character}/
"""
import json, os, shutil
import numpy as np
from PIL import Image, ImageFilter, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PCK = os.path.join(ROOT, 'research', 'pck_dump', '.godot', 'imported')
DEC = os.path.join(ROOT, 'research', 'decoded')
MOD = os.path.join(ROOT, 'mod', 'lightsworn', 'lightsworn')
VIS = os.path.join(MOD, 'visuals')
CHAR = os.path.join(MOD, 'images', 'character')
os.makedirs(VIS, exist_ok=True)
os.makedirs(CHAR, exist_ok=True)

# ---------------- HSV 基础 (8bit: H 0-255 ≈ 0-360°) ----------------
def to_hsv(img):
    rgba = img.convert('RGBA')
    hsv = np.array(rgba.convert('RGB').convert('HSV'), dtype=np.int16)
    return hsv, np.array(rgba)[..., 3].copy()

def from_hsv(hsv, alpha):
    hsv = np.clip(hsv, 0, 255).astype(np.uint8)
    rgb = Image.fromarray(hsv.astype(np.uint8), 'HSV').convert('RGB')
    out = np.dstack([np.array(rgb), alpha])
    return Image.fromarray(out, 'RGBA')

# 目标色 (8bit H): 金≈32, 暖象牙≈33, 橙发≈16, 浅肤≈17
def apply_rules(hsv, alpha, region_rules):
    """region_rules: list of (mask_fn(hsv)->bool2d, transform_fn(hsv)->hsv) 按顺序应用"""
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    for mask_fn, tf in region_rules:
        try:
            m = mask_fn(h, s, v) & (alpha > 0)
        except Exception:
            print('DEBUG mask fail: mask_fn=', mask_fn, 'h type=', type(h), h.dtype if hasattr(h, 'dtype') else '?', 's=', type(s), 'v=', type(v))
            raise
        if not m.any():
            continue
        nh, ns, nv = tf(h, s, v)
        h = np.where(m, nh, h); s = np.where(m, ns, s); v = np.where(m, nv, v)
    return np.stack([h, s, v], axis=-1)

def c(val):  # 常量通道
    return lambda h, s, v: np.full_like(h, val)

# ---- 通用像素带判定 ----
def m_green(h, s, v):  return (h >= 60) & (h <= 118) & (s >= 30)
def m_cyan(h, s, v):   return (h >= 119) & (h <= 155) & (s >= 30)
def m_tan(h, s, v):    return (h >= 4) & (h <= 64) & (s >= 28) & (v >= 100)
def m_darkbrown(h, s, v): return (h <= 45) & (s >= 38) & (v < 145)
def m_yellow(h, s, v): return (h >= 33) & (h <= 62) & (s >= 70)
def m_dark(h, s, v):   return v < 70

# ---- 变换 ----
def tf_robe(h, s, v):  # 绿→象牙白袍(大幅提亮); 深绿→冷灰阴影
    dark = v < 80
    nh = np.where(dark, 168, 33)
    ns = np.where(dark, 26, 10 + (s.astype(np.int32) * 10 // 100))
    nv = np.where(dark, 60 + v // 2, 118 + (v.astype(np.int32) * 78 // 100))
    return nh, ns, nv
def tf_wrap(h, s, v):  # 绷带→柔和米白; 深色带扣→暗金
    dark = v < 70
    nh = np.where(dark, 28, 30)
    ns = np.where(dark, 70, 14 + (s.astype(np.int32) * 8 // 100))
    nv = np.where(dark, v + 25, 118 + (v.astype(np.int32) * 55 // 100))
    return nh, ns, nv
def tf_hair(h, s, v):  # 白/灰发→橙金
    nh = np.full_like(h, 16)
    ns = np.minimum(160, 60 + v.astype(np.int32) * 45 // 100)
    return nh, ns, v
def tf_skin(h, s, v):  # 深肤→浅肤
    nh = np.full_like(h, 17)
    ns = np.full_like(s, 80)
    nv = np.minimum(242, v.astype(np.int32) + 105)
    return nh, ns, nv
def tf_gold(h, s, v):  # 青/黄效果→金光
    nh = np.full_like(h, 32)
    ns = np.minimum(210, (s.astype(np.int32) * 115 // 100) + 50)
    nv = np.minimum(255, v.astype(np.int32) + 12)
    return nh, ns, nv
def tf_bone(h, s, v):  # 骨白保留, 暗部→金
    dark = v < 125
    nh = np.where(dark, 28, h)
    ns = np.where(dark, 115, s)
    nv = np.where(dark, np.minimum(180, v.astype(np.int32) + 55), np.minimum(255, v.astype(np.int32) + 18))
    return nh, ns, nv
def tf_eye(h, s, v):
    return c(32)(h, s, v), c(235)(h, s, v), c(255)(h, s, v)
def tf_mask(h, s, v):  # 眼罩→金色额饰
    return np.full_like(h, 30), np.full_like(s, 150), np.full_like(v, 175)

def rules_robe():   return [(m_green, tf_robe)]
def rules_wrap():   return [(m_tan, tf_wrap), (m_darkbrown, tf_wrap), (m_green, tf_robe)]
def rules_hair():   return [(lambda h, s, v: (s < 60) & (v >= 60), tf_hair), (m_green, tf_robe)]
def rules_skin():   return [(m_darkbrown, tf_skin)]
def rules_gold():   return [(lambda h, s, v: ((s >= 28) | (v >= 200)) & ~m_green(h, s, v), tf_gold)]
def rules_bone():   return [(m_green, tf_robe), (lambda h, s, v: v < 200, tf_bone)]
def rules_head():   return [(m_darkbrown, tf_skin),
                            (lambda h, s, v: (s < 40) & (v >= 25) & (v < 125), tf_skin),
                            (lambda h, s, v: (s < 55) & (v >= 110), tf_hair),
                            (m_green, tf_robe)]
def rules_eye():    return [(lambda h, s, v: s >= 40, tf_eye)]
def rules_shadow(): return []
def rules_default():
    return [(m_green, tf_robe), (m_cyan, tf_gold), (m_tan, tf_wrap),
            (m_darkbrown, tf_skin), (m_yellow, tf_gold)]

# ---- 部件名 → 规则 (战斗图集专用名 + 关键词兜底) ----
EXACT = {
    'back dagger': rules_gold, 'top dagger': rules_gold, 'blade_shine': rules_gold,
    'blade_twirls': rules_gold, 'shiv_blur': rules_gold, 'slash': rules_gold,
    'shiv_hand': rules_wrap, 'eye': rules_eye, 'head': rules_head, 'shadow': rules_shadow,
    'hair': rules_hair, 'hair top': rules_hair, 'skull': rules_bone, 'badge': rules_bone,
    'bottom horn': rules_bone, 'top horn': rules_bone, 'death_antlers': rules_bone, 'death_skull': rules_bone,
}
KEYWORDS = [
    (('dagger', 'blade', 'shiv', 'slash', 'twirl', 'sparkle'), rules_gold),
    (('hair',), rules_hair),
    (('head', 'face'), rules_head),
    (('eye',), rules_eye),
    (('skull', 'bone', 'horn', 'antler', 'badge'), rules_bone),
    (('shadow',), rules_shadow),
    (('hood', 'cloak', 'cape', 'dress', 'skirt', 'robe', 'garment'), rules_robe),
    (('arm', 'hand', 'leg', 'foot', 'torso', 'neck', 'body', 'bandage', 'sash'), rules_wrap),
]

def rule_for(name):
    n = name.strip().lower()
    if n in EXACT:
        return EXACT[n]
    base = n.split('/')[-1]
    if base in EXACT:
        return EXACT[base]
    for keys, r in KEYWORDS:
        if any(k in base for k in keys):
            return r
    return rules_default

# ---- 图集 region 解析。rotate:90 时 bounds 的 w/h 是部件原始尺寸,
# 实际在图集中的占位 = (x, y, h, w) (已用矩形互不重叠验证) ----
def parse_regions(atlas_text):
    entries = []
    cur = None
    for ln in atlas_text.split('\n'):
        ln = ln.strip()
        if ln.startswith('bounds:') and cur:
            try:
                entries.append([cur, tuple(map(int, ln[7:].split(',')))])
            except ValueError:
                entries.append([cur, (0, 0, 0, 0)])
            cur = None
            continue
        if ln.startswith('rotate:') and entries:
            if ln.endswith('90') or ln.endswith('270'):
                x, y, w, h = entries[-1][1]
                entries[-1][1] = (x, y, h, w)
            continue
        if ln and ':' not in ln and not ln.startswith(('offsets', 'size', 'filter', 'scale')):
            cur = ln
    return {name: rect for name, rect in entries}

def recolor_atlas(img, atlas_text, label):
    hsv, alpha = to_hsv(img)
    regions = parse_regions(atlas_text)
    print(f'{label}: {len(regions)} regions')
    used = np.zeros(hsv.shape[:2], dtype=bool)
    for name, (x, y, w, h) in regions.items():
        x2, y2 = min(x + w, img.width), min(y + h, img.height)
        if x >= x2 or y >= y2:
            print('  !! 越界 region:', name, (x, y, w, h))
            continue
        sub = hsv[y:y2, x:x2]
        sub_a = alpha[y:y2, x:x2]
        hsv[y:y2, x:x2] = apply_rules(sub, sub_a, rule_for(name)())
        used[y:y2, x:x2] = True
    # 未覆盖像素走默认规则
    hsv[~used] = apply_rules(hsv[~used], alpha[~used], rules_default())
    return from_hsv(hsv, alpha)

def recolor_global(img):
    hsv, alpha = to_hsv(img)
    return from_hsv(apply_rules(hsv, alpha, rules_default()), alpha)

# ---------------- 1. 战斗 / 商店 / 休息处 贴图 ----------------
ATLASES = [
    ('silent.atlas-46990217b356d22b4cd3471fdb3c4d7a.spatlas', 'silent.png-532f26487787523b822e8e427d84a24f.ctex',
     'saint.atlas', 'silent.png', 'combat'),
    ('silent_shop.atlas-caa62d54e37e739cae6904bdcb2cadeb.spatlas', 'silent_shop.png-5a34f8c9d08fd88ba72ba5c5b4459b58.ctex',
     'saint_shop.atlas', 'silent_shop.png', 'shop'),
    ('restsite_silent.atlas-5a20a7d911b91df8c492ff4737ce2db0.spatlas', 'restsite_silent.png-3a55621a5041df24437d31131cbc57c2.ctex',
     'saint_rest.atlas', 'restsite_silent.png', 'rest'),
]

def find_file(prefix):
    for f in os.listdir(PCK):
        if f.startswith(prefix):
            return f
    raise FileNotFoundError(prefix)

for spatlas_name, ctex_hint, out_atlas, page_png, label in ATLASES:
    real_spatlas = find_file(spatlas_name.split('-')[0])
    j = json.loads(open(os.path.join(PCK, real_spatlas), encoding='utf-8').read())
    atlas_text = j['atlas_data']
    # 贴图: 优先用已解码 png
    dec = os.path.join(DEC, ctex_hint.split('.ctex')[0] + '.png')
    if not os.path.exists(dec):
        real_ctex = find_file(ctex_hint.split('.png-')[0] + '.png-')
        dec = os.path.join(DEC, real_ctex.split('.png-')[0] + '.png')
    src = Image.open(dec)
    out = recolor_atlas(src, atlas_text, label)
    out.save(os.path.join(VIS, page_png))
    print('  saved', page_png, out.size)
    # 原始 atlas 文本 + 修改 source_path 的 spatlas
    open(os.path.join(VIS, out_atlas), 'w', encoding='utf-8').write(atlas_text)
    j['source_path'] = 'res://lightsworn/visuals/' + out_atlas
    open(os.path.join(VIS, out_atlas + '.spatlas'), 'w', encoding='utf-8').write(json.dumps(j, ensure_ascii=False, separators=(',', ':')))

# ---------------- 2. 骨骼 .spskel 原样复制 ----------------
shutil.copyfile(os.path.join(PCK, find_file('silent.skel-')),
                os.path.join(VIS, 'saint.skel.spskel'))
shutil.copyfile(os.path.join(PCK, find_file('restsite_silent.skel-')),
                os.path.join(VIS, 'saint_rest.skel.spskel'))

# ---------------- 3. 选人图标 / 顶栏图标 / 地图标记 ----------------
sel = recolor_global(Image.open(os.path.join(DEC, 'char_select_silent.png')))
sel.save(os.path.join(CHAR, 'select_icon.png'))
locked = sel.convert('RGBA')
la = np.array(locked).astype(np.int16)
gray = (la[..., 0] * 3 + la[..., 1] * 5 + la[..., 2] * 2) // 10
la[..., 0] = gray * 55 // 100; la[..., 1] = gray * 55 // 100; la[..., 2] = gray * 70 // 100
Image.fromarray(la.astype(np.uint8), 'RGBA').save(os.path.join(CHAR, 'select_icon_locked.png'))

# 顶栏图标 85x85: 选人图上部裁方
w, h = sel.size
side = w
crop = sel.crop((0, max(0, h // 2 - side // 2), w, max(0, h // 2 - side // 2) + side)).resize((85, 85), Image.LANCZOS)
crop.save(os.path.join(CHAR, 'top_icon.png'))
# 描边版: alpha 膨胀+黑色
a = np.array(crop)
al = Image.fromarray(a[..., 3]).filter(ImageFilter.MaxFilter(5))
outline = Image.new('RGBA', crop.size, (20, 14, 4, 255))
outline.putalpha(al)
outline.save(os.path.join(CHAR, 'top_icon_outline.png'))

marker = recolor_global(Image.open(os.path.join(DEC, 'map_marker_silent.png')))
marker.save(os.path.join(CHAR, 'map_marker.png'))

# ---------------- 4. 选人背景 (圣女密涅瓦卡图 金色化) ----------------
art = Image.open(r'D:\MyCardLibrary\ygopro\pics\30100551.jpg').convert('RGB')
W, H = 1920, 1080
bg = Image.new('RGB', (W, H))
# 模糊放大卡图铺满
scale = max(W / art.width, H / art.height) * 1.15
big = art.resize((int(art.width * scale), int(art.height * scale)), Image.LANCZOS).filter(ImageFilter.GaussianBlur(14))
bx, by = (big.width - W) // 2, (big.height - H) // 2
bg.paste(big.crop((bx, by, bx + W, by + H)))
bg = np.array(bg).astype(np.float32)
# 金色渐变叠加: 上亮金 下深蓝棕
yy = np.linspace(0, 1, H)[:, None, None]
top = np.array([255, 236, 190], np.float32)
bot = np.array([38, 30, 52], np.float32)
grad = top * (1 - yy) + bot * yy
bg = bg * 0.45 + grad * 0.55
# 中央光晕
xx = np.linspace(-1, 1, W)[None, :, None]
yy2 = np.linspace(-1, 1, H)[:, None, None]
r = np.sqrt(xx * xx + (yy2 * 1.2) ** 2)
glow = np.clip(1.15 - r, 0, 1) ** 2
gold = np.array([255, 232, 170], np.float32)
bg = bg + glow * gold * 0.35
# 四角压暗
vign = np.clip(1.25 - r * 0.9, 0, 1)
bg = bg * (0.55 + 0.45 * vign)
Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8)).save(os.path.join(CHAR, 'select_bg.png'))

# ---------------- 5. 场景脚手架 (纯核心节点, 编辑器安全) ----------------
open(os.path.join(VIS, 'saint_rest_site.tscn'), 'w', encoding='utf-8').write(
"""[gd_scene load_steps=1 format=3]

[node name="SaintRestSite" type="Node2D"]
position = Vector2(-2, 42)
scale = Vector2(0.760006, 0.760006)

[node name="ControlRoot" type="Control" parent="."]
offset_left = 68.4205
offset_top = -9.21045
offset_right = 68.4205
offset_bottom = -9.21045

[node name="Hitbox" type="Control" parent="ControlRoot"]
unique_name_in_owner = true
offset_left = -302.629
offset_top = -410.523
offset_right = 102.371
offset_bottom = 284.477
""")

open(os.path.join(VIS, 'saint_merchant.tscn'), 'w', encoding='utf-8').write(
"""[gd_scene load_steps=1 format=3]

[node name="SaintMerchant" type="Node2D"]
""")

open(os.path.join(VIS, 'saint_select_bg.tscn'), 'w', encoding='utf-8').write(
"""[gd_scene load_steps=2 format=3]

[ext_resource type="Texture2D" path="res://lightsworn/images/character/select_bg.png" id="1_bg"]

[node name="LightswornSelectBg" type="Control"]
layout_mode = 3
anchors_preset = 8
anchor_left = 0.5
anchor_top = 0.5
anchor_right = 0.5
anchor_bottom = 0.5
offset_left = -960.0
offset_top = -521.0
offset_right = 1600.0
offset_bottom = 679.0
grow_horizontal = 2
grow_vertical = 2
pivot_offset = Vector2(1280, 600)

[node name="TextureRect" type="TextureRect" parent="."]
layout_mode = 1
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
grow_horizontal = 2
grow_vertical = 2
texture = ExtResource("1_bg")
expand_mode = 1
stretch_mode = 6
""")

print('DONE ->', VIS)
