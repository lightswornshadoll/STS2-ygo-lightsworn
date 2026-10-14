from PIL import Image
import io, sys

# 对比 mod 卡图与 ygopro 原图，推断裁切框：在不同缩放/偏移假设下算 MSE
mod = Image.open(r'mod\lightsworn\lightsworn\images\cards\JudgementDragon.png').convert('RGB')
src_id = '57774843'  # 裁决之龙
src = Image.open(rf'D:\MyCardLibrary\ygopro\pics\{src_id}.jpg').convert('RGB')
sw, sh = src.size
print('mod', mod.size, 'src', src.size)

def mse(a, b):
    pa, pb = a.tobytes(), b.tobytes()
    n = min(len(pa), len(pb))
    s = sum(abs(pa[i] - pb[i]) for i in range(0, n, 997))
    return s / (n // 997)

# 假设1：等比缩放裁切（cover）：把 src 裁成 25:19 再缩到 250x190
target_ar = 250 / 190
best = []
for y0 in range(0, int(sh - sw / target_ar) + 1, 10):
    h = int(sw / target_ar)
    if y0 + h > sh:
        break
    crop = src.crop((0, y0, sw, y0 + h)).resize((250, 190))
    best.append((mse(crop, mod), ('full-width', 0, y0, sw, y0 + h)))
# 假设2：任意框
w_cands = [sw, int(sw * 0.9), int(sw * 0.8), 320, 300, 280]
for w in w_cands:
    h = int(w / target_ar)
    if h > sh:
        continue
    for x0 in range(0, sw - w + 1, 20):
        for y0 in range(0, sh - h + 1, 20):
            crop = src.crop((x0, y0, x0 + w, y0 + h)).resize((250, 190))
            best.append((mse(crop, mod), ('box', x0, y0, x0 + w, y0 + h)))
best.sort()
for b in best[:5]:
    print(b)
