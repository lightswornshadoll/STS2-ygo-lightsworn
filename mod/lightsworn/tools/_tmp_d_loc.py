import json, os

p = r'D:\1-workdata\lightsworn_mod\mod\lightsworn\lightsworn\localization\zhs\cards.json'
with open(p, encoding='utf-8') as f:
    data = json.load(f)

print('type:', type(data).__name__, 'count:', len(data))
keys = list(data.keys())
print('first 5 keys:', keys[:5])

targets = ['FLASH_FANTASY', 'SOLAR_EXCHANGE', 'TWILIGHT_ERASURE', 'TWIN_TWILIGHT_DRAGON',
           'JUSTICE_WORLD', 'LIGHT_BOUNCE', 'ENGRAVER', 'LACRIMA', 'HYMN', 'REQUIEM_COFFIN',
           'LAMENT', 'SABRE', 'SANCTUARY', 'JUDGEMENT_DRAGON', 'PUNISH_DRAGON']
for k, v in data.items():
    for t in targets:
        if t in k:
            print(repr(k), '=>', json.dumps(v, ensure_ascii=False))
