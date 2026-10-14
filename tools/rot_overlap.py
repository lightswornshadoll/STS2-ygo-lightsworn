import json
j = json.loads(open(r'research/pck_dump/.godot/imported/silent.atlas-46990217b356d22b4cd3471fdb3c4d7a.spatlas', encoding='utf-8').read())
entries = []
cur = None
for ln in j['atlas_data'].split('\n'):
    ln = ln.strip()
    if ln.startswith('bounds:') and cur:
        entries.append([cur, tuple(map(int, ln[7:].split(','))), False]); cur = None; continue
    if ln.startswith('rotate:'):
        entries[-1][2] = True; continue
    if ln and ':' not in ln and not ln.startswith(('offsets', 'size', 'filter', 'scale')):
        cur = ln

def rects(mode):
    out = {}
    for name, (x, y, w, h), rot in entries:
        if rot and mode == 'B':
            w, h = h, w  # 左上角锚定交换
        out[name] = (x, y, w, h)
    return out

def overlaps(rs):
    names = list(rs)
    bad = []
    for i in range(len(names)):
        for k in range(i + 1, len(names)):
            a = rs[names[i]]; b = rs[names[k]]
            ax, ay, aw, ah = a; bx, by, bw, bh = b
            if ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + ah:
                area = (min(ax+aw,bx+bw)-max(ax,bx)) * (min(ay+ah,by+bh)-max(ay,by))
                if area > 4:
                    bad.append((names[i], names[k], area))
    return bad

for mode in ('A', 'B'):
    bad = overlaps(rects(mode))
    print(mode, 'overlaps:', len(bad))
    for n1, n2, area in bad[:12]:
        print('   ', n1, '<->', n2, area)
