# 光道权杖遗物图标：从圣女战斗立绘 battle.png 裁出权杖顶部（绿色宝石+银色刃框+金色底座）
# 输出 relics/scepter.png(64) / scepter_big.png(256)，圆形透明底（与猫狗双全/幻色珍珠同规格）。
# 裁剪区域按立绘实测标定：权杖头在 x≈150-265、y≈205-345。
from PIL import Image, ImageDraw

SRC = r"D:\1-workdata\lightsworn_mod\mod\lightsworn\lightsworn\images\character\battle.png"
OUT_DIR = r"D:\1-workdata\lightsworn_mod\mod\lightsworn\lightsworn\images\relics"

# 正方形裁剪（含完整杖头：银刃尖→绿宝石→金色底座；白翼作底）
box = (105, 195, 305, 395)

im = Image.open(SRC).convert("RGBA")
print("source", im.size, "crop", box)
sq = im.crop(box)

big = sq.resize((256, 256), Image.LANCZOS)
mask = Image.new("L", (512, 512), 0)
ImageDraw.Draw(mask).ellipse((6, 6, 506, 506), fill=255)
mask256 = mask.resize((256, 256), Image.LANCZOS)
big.putalpha(mask256)
big.save(OUT_DIR + r"\scepter_big.png")

small = sq.resize((64, 64), Image.LANCZOS)
small.putalpha(mask.resize((64, 64), Image.LANCZOS))
small.save(OUT_DIR + r"\scepter.png")

# 预览（放大看构图）
big.resize((320, 320), Image.LANCZOS).save(r"D:\1-workdata\lightsworn_mod\tools\_scepter_icon_preview.png")
print("saved scepter(_big).png")
