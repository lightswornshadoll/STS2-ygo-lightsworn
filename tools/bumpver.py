import io, json, os, re

base = r'D:\1-workdata\lightsworn_mod\mod\lightsworn'

# 1) Lightsworn.json: 版本号 +0.0.1
jp = os.path.join(base, 'Lightsworn.json')
d = json.load(io.open(jp, encoding='utf-8'))
ver = d['version']
parts = ver.split('.')
parts[-1] = str(int(parts[-1]) + 1)
newver = '.'.join(parts)
d['version'] = newver
io.open(jp, 'w', encoding='utf-8', newline='\n').write(json.dumps(d, ensure_ascii=False, indent=2) + '\n')

# 2) Lightsworn.csproj: <Version> 同步
cp = os.path.join(base, 'Lightsworn.csproj')
t = io.open(cp, encoding='utf-8-sig').read()
t2 = re.sub(r'<Version>[^<]+</Version>', f'<Version>{newver}</Version>', t)
io.open(cp, 'w', encoding='utf-8-sig', newline='').write(t2)

print(f'version {ver} -> {newver} (json + csproj)')
