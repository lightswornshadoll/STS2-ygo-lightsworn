"""临时：对比 locfrag\\cards_6.json 与已部署 cards.json 的差异（输出到 tools\\_locdiff.txt，UTF-8）。"""
import io, json, os

here = os.path.dirname(__file__)
frag = json.load(io.open(os.path.join(here, 'locfrag', 'cards_6.json'), encoding='utf-8'))
frag7 = json.load(io.open(os.path.join(here, 'locfrag', 'cards_7.json'), encoding='utf-8'))
base = os.path.join(here, '..', 'mod', 'lightsworn', 'lightsworn', 'localization', 'zhs')
cards = json.load(io.open(os.path.join(base, 'cards.json'), encoding='utf-8'))

out = []
for name, fragd in (('cards_6', frag), ('cards_7', frag7)):
    for k, v in fragd.items():
        cur = cards.get(k)
        if cur != v:
            out.append(f"== {name} {k}\n  frag: {json.dumps(v, ensure_ascii=False)}\n  json: {json.dumps(cur, ensure_ascii=False)}")
io.open(os.path.join(here, '_locdiff.txt'), 'w', encoding='utf-8').write('\n'.join(out) if out else '(no diff)')
print(f"diffs={len(out)}")
