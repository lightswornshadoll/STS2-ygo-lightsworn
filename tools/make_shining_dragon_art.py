from PIL import Image

# 神光之龙卡图：ygopro 46186135 → 裁插画面区域 → 250x190 ShiningDragon.png
src = Image.open(r'D:\MyCardLibrary\ygopro\pics\46186135.jpg').convert('RGB')
# 插画框约 (38,100)-(360,428)；取 25:19 比例的横幅，龙头居中略偏上
crop = src.crop((38, 118, 360, 363))  # 322 x 245 = 25:19
out = crop.resize((250, 190), Image.LANCZOS)
out.save(r'mod\lightsworn\lightsworn\images\cards\ShiningDragon.png')
print('saved', out.size)
