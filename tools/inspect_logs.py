import re, sys, io, os, glob

logs = sorted(glob.glob(r'C:\Users\light\AppData\Roaming\SlayTheSpire2\logs\*.log'), key=os.path.getmtime, reverse=True)
for path in logs[:2]:
    print('=' * 30, os.path.basename(path), '=', str(round(os.path.getmtime(path))))
    txt = open(path, encoding='utf-8', errors='replace').read()
    lines = txt.splitlines()
    print('total lines:', len(lines))
    # 找 mod 加载相关 + 异常
    keys = ['Lightsworn', 'BaseLib', 'RitsuLib', 'MinionLib', 'Loading mod', 'mod', 'Exception', 'ERROR', 'error', 'Failed', 'failed', 'Harmony']
    hits = []
    for i, l in enumerate(lines):
        for k in keys:
            if k in l:
                hits.append((i, l))
                break
    # 打印去重后的前 150 条
    seen = set()
    out = 0
    for i, l in hits:
        key = l.strip()[:150]
        if key in seen:
            continue
        seen.add(key)
        print(f'{i:6d} {l.strip()[:200]}')
        out += 1
        if out > 180:
            print('... (truncated)')
            break
