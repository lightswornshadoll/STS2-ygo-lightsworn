"""同步 tools\\locfrag\\cards_6.json / cards_7.json 中与已部署 cards.json 不一致的键（以 cards.json 为准）。
防未来重跑 update_shaddoll_loc.py 类合并脚本时把旧文案写回。用法: py tools\\sync_locfrag.py
"""
import io
import json
import os

here = os.path.dirname(os.path.abspath(__file__))
base = os.path.join(here, '..', 'mod', 'lightsworn', 'lightsworn', 'localization', 'zhs')
cards = json.load(io.open(os.path.join(base, 'cards.json'), encoding='utf-8'))

total = 0
for frag_name in ('cards_6.json', 'cards_7.json'):
    path = os.path.join(here, 'locfrag', frag_name)
    frag = json.load(io.open(path, encoding='utf-8'))
    changed = 0
    missing = []
    for k in list(frag.keys()):
        if k not in cards:
            missing.append(k)
            continue
        if frag[k] != cards[k]:
            frag[k] = cards[k]
            changed += 1
            print(f"[{frag_name}] sync {k}")
    with io.open(path, 'w', encoding='utf-8') as f:
        json.dump(frag, f, ensure_ascii=False, indent=2)
        f.write('\n')
    total += changed
    if missing:
        print(f"[{frag_name}] 片段中 cards.json 不存在的键（保留原样）: {missing}")
print(f"done, {total} keys synced")
