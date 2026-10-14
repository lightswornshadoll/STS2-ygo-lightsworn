import numpy as np, json, os
from PIL import Image

img = Image.open(r'research/silent_atlas.png').convert('RGBA')
hsv = np.array(img.convert('RGB').convert('HSV'), dtype=np.int16)
a = np.array(img)[..., 3]
j = json.loads(open(r'research/pck_dump/.godot/imported/silent.atlas-46990217b356d22b4cd3471fdb3c4d7a.spatlas', encoding='utf-8').read())
regions = {}
cur = None
for ln in j['atlas_data'].split('\n'):
    ln = ln.strip()
    if ln.startswith('bounds:') and cur:
        x, y, w, h = map(int, ln[7:].split(','))
        regions[cur] = (x, y, w, h); cur = None; continue
    if ln and ':' not in ln:
        cur = ln

def stats(name):
    x, y, w, h = regions[name]
    sub = hsv[y:y+h, x:x+w].reshape(-1, 3)
    al = a[y:y+h, x:x+w].reshape(-1) > 0
    sub = sub[al]
    if len(sub) == 0:
        print(name, 'empty'); return
    # 只看有彩度的像素
    print(f'{name:22s} n={len(sub):5d}  H p10/50/90={np.percentile(sub[:,0],10):.0f}/{np.percentile(sub[:,0],50):.0f}/{np.percentile(sub[:,0],90):.0f}'
          f'  S={np.percentile(sub[:,1],10):.0f}/{np.percentile(sub[:,1],50):.0f}/{np.percentile(sub[:,1],90):.0f}'
          f'  V={np.percentile(sub[:,2],10):.0f}/{np.percentile(sub[:,2],50):.0f}/{np.percentile(sub[:,2],90):.0f}')

for n in ['cloak back', 'cape_front_attack', 'hood top', 'bottom hood', 'dress', 'top arm', 'back arm',
          'top hand', 'head', 'hair', 'hair top', 'skull', 'badge', 'top dagger', 'eye', 'neck top', 'torso copy', 'shadow']:
    try: stats(n)
    except Exception as e: print(n, 'ERR', e)
