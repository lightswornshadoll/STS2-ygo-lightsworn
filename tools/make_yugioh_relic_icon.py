# 生成「你必须玩游戏王」遗物图标：取 ygopro 卡背 cover.jpg 中央漩涡正方形裁剪，
# 输出遗物小图 64x64 / 大图 256x256（RGBA PNG）到 mod 的 images\relics\。
from PIL import Image

SRC = r"D:\MyCardLibrary\ygopro\textures\cover.jpg"
OUT_DIR = r"D:\1-workdata\lightsworn_mod\mod\lightsworn\lightsworn\images\relics"

im = Image.open(SRC).convert("RGBA")
w, h = im.size
side = min(w, h)  # 400x580 -> 正方形边长400
left = (w - side) // 2
top = (h - side) // 2  # 漩涡在卡背中央
sq = im.crop((left, top, left + side, top + side))

for name, size in (("yugioh.png", 64), ("yugioh_big.png", 256)):
    img = sq.resize((size, size), Image.LANCZOS)
    img.save(f"{OUT_DIR}\\{name}")
    print(name, img.size)
