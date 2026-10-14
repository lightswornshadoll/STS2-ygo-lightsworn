"""问题8：能力图标改用对应卡牌卡图裁成的圆形。
从 images/cards/{Card}.png 中心裁正方形 -> 圆形蒙版 -> 缩放 64/256 ->
保存 images/powers/{name}.png 和 {name}_big.png（覆盖同名文件）。
"""
import os
from PIL import Image, ImageDraw, ImageOps

ROOT = os.path.join(os.path.dirname(__file__), '..', 'mod', 'lightsworn', 'lightsworn', 'images')

# 能力图标名(不含.png) -> 卡牌类名.png
MAPPING = {
    'twilight': 'TwilightLumina',
    'garoth': 'Garoth',
    'sanctuary': 'Sanctuary',
    'janice': 'Janice',
    'aegis': 'Aegis',
    'justice': 'JusticeWorld',
    'bounce': 'LightBounce',
    'honest': 'Honest',
    'pearlworld': 'Perlereino',
}

SIZES = [64, 256]

def make_round(src_path, out_base):
    img = Image.open(src_path).convert('RGBA')
    w, h = img.size
    side = min(w, h)
    left, top = (w - side) // 2, (h - side) // 2
    square = img.crop((left, top, left + side, top + side))
    # 圆形蒙版（4x超采样抗锯齿）
    big = side * 4
    mask = Image.new('L', (big, big), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, big - 1, big - 1), fill=255)
    mask = mask.resize((side, side), Image.LANCZOS)
    round_img = Image.new('RGBA', (side, side), (0, 0, 0, 0))
    round_img.paste(square, (0, 0), mask)
    for size in SIZES:
        out = round_img.resize((size, size), Image.LANCZOS)
        suffix = '' if size == 64 else '_big'
        out_path = os.path.join(ROOT, 'powers', out_base + suffix + '.png')
        out.save(out_path)
        print('written', os.path.normpath(out_path))

def main():
    for name, card in MAPPING.items():
        src = os.path.join(ROOT, 'cards', card + '.png')
        if not os.path.exists(src):
            print('MISSING card art:', src)
            continue
        make_round(src, name)

if __name__ == '__main__':
    main()
