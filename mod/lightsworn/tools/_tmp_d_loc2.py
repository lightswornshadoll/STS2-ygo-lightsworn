import json

p = r'D:\1-workdata\lightsworn_mod\mod\lightsworn\lightsworn\localization\zhs\cards.json'
with open(p, encoding='utf-8') as f:
    data = json.load(f)

for pat in ['除光', '虚无', '灾厄', '{Banish', 'Banish']:
    print(f'--- entries containing {pat!r}:')
    for k, v in data.items():
        if pat in str(v):
            print(' ', k, '=>', str(v)[:120])
