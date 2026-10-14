from PIL import Image
import os, sys

# 破坏之光卡图：ygopro 83027236 → 裁插画面区域 → 250x190 LightOfDestruction.png
# + 能力图标（复用 make_power_icons.make_round 圆形裁切）→ powers/lightofdestruction(_big).png
sys.path.insert(0, os.path.dirname(__file__))
import make_power_icons

src = Image.open(r'D:\MyCardLibrary\ygopro\pics\83027236.jpg').convert('RGB')
print('source size:', src.size)
# 该图为 400x580（非标准421x625），实测插画框内沿约 x55-345；取 25:19 比例横幅
crop = src.crop((55, 110, 345, 330))  # 290 x 220 = 25:19
out = crop.resize((250, 190), Image.LANCZOS)
card_png = r'mod\lightsworn\lightsworn\images\cards\LightOfDestruction.png'
out.save(card_png)
print('saved', card_png, out.size)

make_power_icons.make_round(card_png, 'lightofdestruction')
