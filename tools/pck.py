"""Godot 4 pck 解包工具 (支持 format v2/v3)
用法:
  py pck.py list <pck路径> [过滤子串]
  py pck.py extract <pck路径> <输出目录> [过滤子串]
"""
import struct, sys, os

def read_pck(path):
    with open(path, 'rb') as f:
        data = f.read(128)
    if data[:4] != b'GDPC':
        raise SystemExit('not a pck: ' + path)
    fmt, ver_maj, ver_min, ver_patch = struct.unpack_from('<4I', data, 4)
    if fmt >= 2:
        if fmt >= 3:
            dir_off, = struct.unpack_from('<Q', data, 32)  # v3: 目录在文件尾，头部偏移32存目录偏移
        else:
            dir_off = 112
        pack_flags, file_base = struct.unpack_from('<IQ', data, 20)
    with open(path, 'rb') as f:
        f.seek(dir_off)
        dirdata = f.read(64 * 1024 * 1024)
    count, = struct.unpack_from('<I', dirdata, 0)
    off = 4
    entries = []
    for _ in range(count):
        plen, = struct.unpack_from('<I', dirdata, off); off += 4
        p = dirdata[off:off+plen].rstrip(b'\0').decode('utf-8'); off += plen
        offset, size = struct.unpack_from('<QQ', dirdata, off); off += 16
        off += 16  # md5
        flags, = struct.unpack_from('<I', dirdata, off); off += 4
        entries.append((p, file_base + offset, size, flags))
    return entries

def main():
    mode = sys.argv[1]
    pck = sys.argv[2]
    entries = read_pck(pck)
    if mode == 'list':
        filt = sys.argv[3] if len(sys.argv) > 3 else ''
        if filt:
            entries = [e for e in entries if filt.lower() in e[0].lower()]
        for p, o, s, fl in entries:
            print(f'{s:>10}  0x{o:08x}  f{fl}  {p}')
        print(f'-- {len(entries)} files')
    elif mode == 'extract':
        outdir = sys.argv[3]
        filt = sys.argv[4] if len(sys.argv) > 4 else ''
        if filt:
            entries = [e for e in entries if filt.lower() in e[0].lower()]
        with open(pck, 'rb') as f:
            for p, o, s, fl in entries:
                dst = os.path.join(outdir, p.replace('res://', '').replace('/', os.sep))
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                f.seek(o)
                with open(dst, 'wb') as g:
                    g.write(f.read(s))
        print(f'-- extracted {len(entries)} files to {outdir}')

if __name__ == '__main__':
    main()
