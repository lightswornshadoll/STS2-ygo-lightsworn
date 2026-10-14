import re, sys, os, glob
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

logs = sorted(glob.glob(r'C:\Users\light\AppData\Roaming\SlayTheSpire2\logs\*.log'), key=os.path.getmtime, reverse=True)
path = logs[0]
lines = open(path, encoding='utf-8', errors='replace').read().splitlines()

print('=== exceptions / errors ===')
shown = 0
for i, l in enumerate(lines):
    low = l.lower()
    if ('exception' in low or 'error' in low or 'fail' in low or 'warn' in low
            or 'missingmethod' in low or 'typeloadexception' in low):
        # 过滤已知无关（Sentry/Steam/音频等），但仍然打印以便判断
        print(f'{i:5d} {l.strip()[:220]}')
        shown += 1
        if shown > 60:
            print('...(truncated)')
            break
if shown == 0:
    print('(none)')

print()
print('=== lightsworn / ritsulib 后期日志（150 行后） ===')
shown = 0
for i, l in enumerate(lines):
    if i < 150:
        continue
    if 'lightsworn' in l.lower() or 'ritsulib' in l.lower():
        print(f'{i:5d} {l.strip()[:200]}')
        shown += 1
        if shown > 40:
            print('...(truncated)')
            break
