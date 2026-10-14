import json, io, os, sys
root = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'mod', 'lightsworn', 'lightsworn', 'localization', 'zhs')
ids = sys.argv[1:]
cards = json.load(io.open(os.path.join(root, 'cards.json'), encoding='utf-8'))
powers = json.load(io.open(os.path.join(root, 'powers.json'), encoding='utf-8'))
kw = json.load(io.open(os.path.join(root, 'card_keywords.json'), encoding='utf-8'))
sel = json.load(io.open(os.path.join(root, 'card_selection.json'), encoding='utf-8'))
for i in ids:
    hit = False
    for table, name in ((cards, 'cards'), (powers, 'powers'), (kw, 'card_keywords'), (sel, 'card_selection')):
        for k in table:
            if i in k:
                print(f'--- {name}: {k}')
                print(table[k])
                hit = True
    if not hit:
        print(f'--- !! {i}: NOT FOUND')
