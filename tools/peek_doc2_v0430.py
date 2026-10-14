import io, os
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
t = io.open(os.path.join(root, 'design', '卡牌图鉴.md'), encoding='utf-8').read()
for key in ['LIGHTSWORN-SHADDOLL_CONSTRUCT', 'LIGHTSWORN-EL_SHADDOLL_FUSION', 'LIGHTSWORN-PERLEREINO']:
    i = t.find(key)
    seg = t[max(0, i - 260):i + 240]
    print('====', key)
    print(seg.strip()[:460])
    print()
