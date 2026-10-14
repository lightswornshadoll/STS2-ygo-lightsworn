import json, re
from PIL import Image

img = Image.open(r'research/silent_atlas.png')
d = open(r'research/pck_dump/.godot/imported/silent.atlas-46990217b356d22b4cd3471fdb3c4d7a.spatlas', encoding='utf-8').read()
j = json.loads(d)
atlas_text = j['atlas_data']
# 解析 regions: 名字行后跟 bounds:x,y,w,h（可能有 rotate:90 在前面）
lines = atlas_text.split('\n')
regions = {}
cur = None
for ln in lines:
    m = re.match(r'bounds:(\d+),(\d+),(\d+),(\d+)', ln.strip())
    if m and cur:
        x, y, w, h = map(int, m.groups())
        regions[cur] = (x, y, w, h)
        cur = None
        continue
    if ln.strip() and not ln.startswith(('bounds:', 'rotate:', 'offsets:', 'size:', 'filter:', 'scale:')) and ':' not in ln:
        cur = ln.strip()
print(len(regions), 'regions')
# 拼贴关键部件放大图
picks = ['head', 'eye', 'hair', 'hair top', 'top hand', 'top dagger', 'back dagger', 'skull', 'badge',
         'hood top', 'bottom hood', 'top arm', 'dress', 'torso copy', 'blade_shine', 'slash', 'neck top', 'shiv_hand']
tiles = []
for name in picks:
    if name not in regions:
        print('missing:', name)
        continue
    x, y, w, h = regions[name]
    c = img.crop((x, y, x + w, y + h)).resize((w * 3, h * 3), Image.NEAREST)
    tiles.append((name, c))
cols = 6
cw = max(t[1].width for t in tiles) + 8
ch = max(t[1].height for t in tiles) + 20
rows = (len(tiles) + cols - 1) // cols
sheet = Image.new('RGBA', (cols * cw, rows * ch), (30, 30, 40, 255))
from PIL import ImageDraw
dr = ImageDraw.Draw(sheet)
for i, (name, c) in enumerate(tiles):
    px, py = (i % cols) * cw, (i // cols) * ch
    sheet.paste(c, (px + 4, py + 16), c)
    dr.text((px + 4, py + 2), name, fill=(255, 255, 0, 255))
sheet.save(r'research/part_preview.png')
print('saved research/part_preview.png')
