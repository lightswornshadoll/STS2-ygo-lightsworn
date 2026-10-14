import struct, os
P = r'D:\Program Files (x86)\Steam\steamapps\common\Slay the Spire 2\SlayTheSpire2.pck'
d = open(P, 'rb').read(4096)
size = os.path.getsize(P)
print('pck size', size, hex(size))
for i in range(4, 160, 4):
    v = struct.unpack_from('<I', d, i)[0]
    print(i, v, hex(v))
print(repr(d[100:200]))
