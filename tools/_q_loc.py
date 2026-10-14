"""临时：打印本地化 json 中匹配关键词的键值（zhs）。用法：py tools\\_q_loc.py <substr> [substr2...]"""
import io, json, os, sys

here = os.path.dirname(__file__)
base = os.path.join(here, '..', 'mod', 'lightsworn', 'lightsworn', 'localization', 'zhs')
keys = sys.argv[1:]
for fn in ('cards.json', 'powers.json', 'card_keywords.json', 'card_selection.json'):
    p = os.path.join(base, fn)
    if not os.path.exists(p):
        continue
    data = json.load(io.open(p, encoding='utf-8'))
    for k, v in data.items():
        if any(kw.lower() in k.lower() for kw in keys):
            print(f"[{fn}] {k} = {json.dumps(v, ensure_ascii=False)}")
