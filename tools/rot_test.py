from PIL import Image, ImageDraw
img = Image.open(r'research/silent_atlas.png').convert('RGBA')

# (name, bounds, rotate?) — 从 atlas 文本
cases = [
    ('hair', (286, 29, 140, 17), True),
    ('hair_as_swapped', (286 + 70 - 8, 29 + 8 - 70, 17, 140), False),
    ('back hand', (591, 98, 27, 24), True),
    ('bh_swapped', (591, 98, 24, 27), False),
    ('back arm cloak back', (2, 62, 18, 107), True),
    ('bacb_swapped', (2, 62, 107, 18), False),
    ('hair top', (506, 9, 5, 61), True),
]
tiles = []
for name, (x, y, w, h), rot in cases:
    c = img.crop((x, y, x + w, y + h))
    c = c.resize((w * 4, h * 4), Image.NEAREST)
    tiles.append((f'{name} {w}x{h}', c))
cw = max(t[1].width for t in tiles) + 10
ch = max(t[1].height for t in tiles) + 24
sheet = Image.new('RGBA', (cw * 4, ch * 2), (30, 30, 40, 255))
d = ImageDraw.Draw(sheet)
for i, (name, c) in enumerate(tiles):
    px, py = (i % 4) * cw, (i // 4) * ch
    sheet.paste(c, (px + 4, py + 18), c)
    d.text((px + 4, py + 2), name, fill=(255, 255, 0, 255))
sheet.save(r'research/rot_test.png')
print('ok')
