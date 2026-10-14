from PIL import Image, ImageDraw
src = Image.open(r'mod/lightsworn/lightsworn/visuals/silent.png').convert('RGBA')
orig = Image.open(r'research/silent_atlas.png').convert('RGBA')
crops = [('arms', (180, 30, 330, 230)), ('head', (540, 140, 618, 230)), ('hands', (540, 60, 618, 140)), ('skull', (540, 230, 618, 300))]
W = sum((c[1][2] - c[1][0]) * 3 + 12 for c in crops)
H = max((c[1][3] - c[1][1]) * 3 for c in crops) + 30
sheet = Image.new('RGBA', (W * 2 + 30, H), (25, 25, 35, 255))
d = ImageDraw.Draw(sheet)
x = 6
for label, (a, b, c2, dd) in crops:
    for im, ox in ((orig, 0), (src, W + 30)):
        cc = im.crop((a, b, c2, dd))
        cc = cc.resize((cc.width * 3, cc.height * 3), Image.NEAREST)
        sheet.paste(cc, (x + ox, 24), cc)
    d.text((x + 4, 4), label + ' (before)', fill=(255, 255, 0, 255))
    d.text((x + 4 + W + 30, 4), label + ' (after)', fill=(0, 255, 128, 255))
    x += (c2 - a) * 3 + 12
sheet.save(r'research/zoom_check.png')
print('ok')
