import zipfile, os, sys, hashlib
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
src = r'D:\1-workdata\lightsworn_mod\dist\lightsworn'
dst = r'D:\Program Files (x86)\Steam\steamapps\common\Slay the Spire 2\mods\Lightsworn.zip'
tmp = dst + '.new'
with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for name in ('Lightsworn.dll', 'Lightsworn.json', 'Lightsworn.pck'):
        z.write(os.path.join(src, name), 'Lightsworn/' + name)
os.replace(tmp, dst)
print('zip refreshed:', dst, os.path.getsize(dst), 'bytes')
with zipfile.ZipFile(dst) as z:
    for i in z.infolist():
        print(' ', i.filename, i.file_size)
