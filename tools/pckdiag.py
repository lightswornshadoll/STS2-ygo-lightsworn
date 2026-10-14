import struct
P = r'D:\Program Files (x86)\Steam\steamapps\common\Slay the Spire 2\SlayTheSpire2.pck'
DIR = 1899867440
f = open(P, 'rb')
f.seek(DIR)
d = f.read(2 * 1024 * 1024)
count, = struct.unpack_from('<I', d, 0)
print('count', count)
off = 4
bad = 0
for i in range(count):
    plen, = struct.unpack_from('<I', d, off)
    raw = d[off+4:off+4+plen]
    try:
        p = raw.rstrip(b'\0').decode('utf-8')
        ok = p.startswith('.') or p.startswith('res://') or p.startswith('/')
    except UnicodeDecodeError:
        p = None
        ok = False
    if not ok:
        bad += 1
        if bad <= 5:
            print(f'BAD entry {i} @dir+{off}: plen={plen} raw={raw[:60].hex()} ctx={d[off-16:off+64].hex()}')
            print('   prev path bytes:', d[off-64:off])
    offset, size = struct.unpack_from('<QQ', d, off + 4 + plen)
    off += 4 + plen + 8 + 8 + 16 + 4
    if p and i % 3000 == 0:
        print(f'{i}: {p} size={size}')
print('bad entries:', bad, 'consumed', off, 'of', len(d))
