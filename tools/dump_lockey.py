import json, os, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
base = r'D:\1-workdata\lightsworn_mod\mod\lightsworn\lightsworn\localization\zhs'
for fn in sorted(os.listdir(base)):
    if not fn.endswith('.json'):
        continue
    d = json.load(open(os.path.join(base, fn), encoding='utf-8'))
    print('=' * 20, fn, len(d), 'keys')
    keys = list(d.keys())
    for k in keys[:200]:
        print('   ', k)
    if len(keys) > 200:
        print(f'    ...({len(keys)-200} more)')
