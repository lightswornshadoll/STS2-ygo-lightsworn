"""解码 Godot 4 .ctex (CompressedTexture2D) -> PNG
用法: py ctex.py <in.ctex> <out.png>
"""
import struct, sys, io

def main():
    src, dst = sys.argv[1], sys.argv[2]
    d = open(src, 'rb').read()
    if d[:4] != b'GST2':
        raise SystemExit('not ctex: ' + src)
    ver, w, h, flags = struct.unpack_from('<IHHI', d, 4)
    print(f'ver={ver} {w}x{h} flags={flags:#x} size={len(d)}')
    i = d.find(b'RIFF', 16)
    if i < 0:
        raise SystemExit('no RIFF/webp payload')
    riff_size = struct.unpack_from('<I', d, i + 4)[0] + 8
    payload = d[i:i + riff_size]
    print(f'webp payload @{i:#x} {riff_size} bytes')
    from PIL import Image
    img = Image.open(io.BytesIO(payload))
    print('decoded:', img.size, img.mode)
    img.save(dst)

main()
