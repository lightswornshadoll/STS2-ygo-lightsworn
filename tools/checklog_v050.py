import re, sys, os, glob
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

logs = sorted(glob.glob(r'C:\Users\light\AppData\Roaming\SlayTheSpire2\logs\*.log'), key=os.path.getmtime, reverse=True)
path = logs[0]
print('LOG:', os.path.basename(path), 'lines:', sum(1 for _ in open(path, encoding='utf-8', errors='replace')))
txt = open(path, encoding='utf-8', errors='replace').read()
lines = txt.splitlines()

# 关键行：mod 加载/版本/RitsuLib/Lightsworn/异常
keys = ['Loading mod', 'Found mod manifest', 'Loading assembly DLL', 'Loading Godot PCK',
        'Lightsworn', 'RitsuLib', 'Keywords', 'Content]', 'Registered', 'Exception', 'ERROR',
        'Failed', 'MissingMethod', 'TypeLoad', 'Harmony', 'patches', 'Naive game version', 'version']
hits = []
for i, l in enumerate(lines):
    if any(k in l for k in keys):
        hits.append((i, l.strip()[:230]))

seen = set()
shown = 0
for i, l in hits:
    key = re.sub(r'\d', '#', l[:120])
    if key in seen:
        continue
    seen.add(key)
    print(f'{i:5d} {l}')
    shown += 1
    if shown > 120:
        print('...truncated')
        break
