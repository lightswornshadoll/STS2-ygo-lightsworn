import struct
P = r'D:\Program Files (x86)\Steam\steamapps\common\Slay the Spire 2\SlayTheSpire2.pck'
BASE = 1899867440
f = open(P, 'rb')
f.seek(BASE)
d = f.read(400)
for i in range(0, 160, 4):
    v = struct.unpack_from('<I', d, i)[0]
    print(i, v, hex(v))
print(repr(d[0:120]))
