"""v0.5.3：莱登临时力量（LaydenTempStrengthPower）能力图标。

背景：该能力用 RitsuLib `ModTemporaryAppliedPowerTemplate`（原 BaseLib 临时力量包装器的 RitsuLib 版），
类上没有 AssetProfile → CustomIconPath=null → 游戏回退 `res://images/powers/layden_temp_strength_power.png`
（不存在）→ 显示占位符。修复=从莱登卡图圆裁一枚图标（沿用「问题8」卡图圆裁惯例）。

输出：images/powers/laydentempstrength.png（64）+ laydentempstrength_big.png（256）
⚠ 生成后必须 Godot --headless --import 再 ExportPck（坑13：新 PNG 未导入不进 pck）。
"""
import os
from PIL import Image, ImageDraw

ROOT = os.path.join(os.path.dirname(__file__), '..', 'mod', 'lightsworn', 'lightsworn', 'images')
SRC = os.path.join(ROOT, 'cards', 'Layden.png')
OUT_BASE = os.path.join(ROOT, 'powers', 'laydentempstrength')
SIZES = [64, 256]


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
    for size in SIZES:
        out = round_img.resize((size, size), Image.LANCZOS)
        suffix = '' if size == 64 else '_big'
        out.save(out_base + suffix + '.png')
        print(f'wrote {out_base + suffix}.png ({size}x{size})')


make_round(SRC, OUT_BASE)
