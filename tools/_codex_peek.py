"""临时：抽取图鉴中指定卡名的条目，输出到 tools\\_codex_peek.txt（UTF-8）。"""
import io, os

here = os.path.dirname(os.path.abspath(__file__))
t = io.open(os.path.join(here, '..', 'design', '卡牌图鉴.md'), encoding='utf-8').read()
names = ['光道贼猫 雷喵', '光道暗杀者 莱登', '暮光道将军 简', '黄昏之交衣', '古尖兵 凯尔柏克',
         '影依的炎核 虚梦狱', '绊影依-神数原核', '救影依-神数纳迦', '光道战士 加洛斯',
         '光道龙 格拉古尼斯', '珠泪哀歌族 卡雷多哈特', '羽影依 文蒂', '光道天使 基路伯', '影依兽']
out = []
for n in names:
    i = t.find('### ' + n + '\n')
    if i < 0:
        out.append(f'### {n}  → 未找到')
        continue
    j = t.find('\n---', i)
    out.append(t[i:j].strip())
io.open(os.path.join(here, '_codex_peek.txt'), 'w', encoding='utf-8').write('\n\n'.join(out))
print('written', len(out))
