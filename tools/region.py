import struct
P = r'D:\Program Files (x86)\Steam\steamapps\common\Slay the Spire 2\SlayTheSpire2.pck'
f = open(P, 'rb')
START = 0x1b9c5d00
LEN = 0x1600
f.seek(START)
d = f.read(LEN)
# 打印可读化 dump
for i in range(0, LEN, 32):
    chunk = d[i:i+32]
    hexs = ' '.join(f'{b:02x}' for b in chunk)
    text = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
    print(f'{START+i:08x}  {hexs}  {text}')
