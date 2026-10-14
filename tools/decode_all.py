"""批量解码 .godot/imported/*.ctex -> research/decoded/*.png"""
import glob, io, os, struct
from PIL import Image

os.makedirs(r'research/decoded', exist_ok=True)
for src in glob.glob(r'research/pck_dump/.godot/imported/*.ctex'):
    d = open(src, 'rb').read()
    if d[:4] != b'GST2':
        print('skip(non-gst2):', src)
        continue
    ver, w, h, flags = struct.unpack_from('<IHHI', d, 4)
    i = d.find(b'RIFF', 16)
    base = os.path.basename(src).split('.png-')[0]
    try:
        if i >= 0:
            riff = struct.unpack_from('<I', d, i + 4)[0] + 8
            img = Image.open(io.BytesIO(d[i:i + riff]))
        else:
            # 压缩纹理(bptc等)无法直接解码，跳过
            print(f'skip(compressed): {base} ver={ver} {w}x{h}')
            continue
        out = rf'research/decoded/{base}.png'
        img.save(out)
        print(f'{base}: {w}x{h} -> {img.size} {img.mode}')
    except Exception as e:
        print('FAIL', base, e)
