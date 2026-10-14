import numpy as np, json
from PIL import Image

img = Image.open(r'research/silent_atlas.png').convert('RGBA')
alpha = np.array(img)[..., 3] > 8
j = json.loads(open(r'research/pck_dump/.godot/imported/silent.atlas-46990217b356d22b4cd3471fdb3c4d7a.spatlas', encoding='utf-8').read())

entries = []  # (name, bounds, rotate)
cur = None
for ln in j['atlas_data'].split('\n'):
    ln = ln.strip()
    if ln.startswith('bounds:') and cur:
        entries.append((cur, tuple(map(int, ln[7:].split(','))))); cur = None; continue
    if ln.startswith('rotate:'):
        entries[-1] = (entries[-1][0], entries[-1][1], True); continue
    if ln and ':' not in ln and not ln.startswith(('offsets', 'size', 'filter', 'scale')):
        cur = ln

rots = [e for e in entries if len(e) == 3 and e[2]]
print('rotate regions:', len(rots))
for name, (x, y, w, h), _ in rots:
    fillA = alpha[y:y+h, x:x+w].mean() if w > 0 and h > 0 else 0
    # B: x,y 不动, 交换 w/h
    fillB = alpha[y:y+w, x:x+h].mean() if y + w <= alpha.shape[0] and x + h <= alpha.shape[1] else -1
    print(f'{name:26s} bounds=({x},{y},{w}x{h})  fill_asis={fillA:.2f}  fill_swapped@xy={fillB:.2f}')
