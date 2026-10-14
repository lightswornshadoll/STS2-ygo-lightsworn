import json, collections, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
for f in ('cards_6.json', 'cards_7.json'):
    p = r'D:\1-workdata\lightsworn_mod\tools\locfrag\%s' % f
    d = json.load(open(p, encoding='utf-8'), object_pairs_hook=collections.OrderedDict)
    out = collections.OrderedDict()
    for k, v in d.items():
        out[('LIGHTSWORN_CARD_' + k[len('LIGHTSWORN-'):]) if k.startswith('LIGHTSWORN-') else k] = v
    json.dump(out, open(p, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=2)
    print(f, '->', len(out), 'keys, first:', next(iter(out)))
