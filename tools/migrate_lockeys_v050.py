# v0.5.0 本地化键迁移：BaseLib 时代 `{MOD}-{NAME}` → RitsuLib 固定条目 `{MOD}_{CATEGORY}_{NAME}`
#   cards.json      LIGHTSWORN-X           → LIGHTSWORN_CARD_X
#   powers.json     LIGHTSWORN-X           → LIGHTSWORN_POWER_X
#   relics.json     LIGHTSWORN-X           → LIGHTSWORN_RELIC_X
#   characters.json LIGHTSWORN-LIGHTSWORN_CHARACTER → LIGHTSWORN_CHARACTER_LIGHTSWORN_CHARACTER
#   events.json     LIGHTSWORN-PEARL_WORLD_ENCOUNTER → LIGHTSWORN_EVENT_PEARL_WORLD_ENCOUNTER
#   card_keywords.json LIGHTSWORN-X        → LIGHTSWORN_KEYWORD_X
#   ancients.json   talk.LIGHTSWORN-LIGHTSWORN_CHARACTER. → talk.LIGHTSWORN_CHARACTER_LIGHTSWORN_CHARACTER.
#   card_selection.json / static_hover_tips.json：自建键，不动
import json, os, sys, re, collections
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE = r'D:\1-workdata\lightsworn_mod\mod\lightsworn\lightsworn\localization'


def rewrite_keys(path, keymap):
    with open(path, encoding='utf-8') as f:
        data = json.load(f, object_pairs_hook=collections.OrderedDict)
    out = collections.OrderedDict()
    changed = 0
    for k, v in data.items():
        nk = keymap(k)
        if nk != k:
            changed += 1
        if nk in out:
            raise SystemExit(f'KEY COLLISION in {path}: {nk}')
        out[nk] = v
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
        f.write('\n')
    return changed


def prefix_rule(old_prefix, new_prefix):
    def f(k):
        return new_prefix + k[len(old_prefix):] if k.startswith(old_prefix) else k
    return f


RULES = {
    'cards.json': prefix_rule('LIGHTSWORN-', 'LIGHTSWORN_CARD_'),
    'powers.json': prefix_rule('LIGHTSWORN-', 'LIGHTSWORN_POWER_'),
    'relics.json': prefix_rule('LIGHTSWORN-', 'LIGHTSWORN_RELIC_'),
    'characters.json': prefix_rule('LIGHTSWORN-LIGHTSWORN_CHARACTER', 'LIGHTSWORN_CHARACTER_LIGHTSWORN_CHARACTER'),
    'events.json': prefix_rule('LIGHTSWORN-PEARL_WORLD_ENCOUNTER', 'LIGHTSWORN_EVENT_PEARL_WORLD_ENCOUNTER'),
    'card_keywords.json': prefix_rule('LIGHTSWORN-', 'LIGHTSWORN_KEYWORD_'),
    'ancients.json': prefix_rule('THE_ARCHITECT.talk.LIGHTSWORN-LIGHTSWORN_CHARACTER.',
                                 'THE_ARCHITECT.talk.LIGHTSWORN_CHARACTER_LIGHTSWORN_CHARACTER.'),
}

for lang in sorted(os.listdir(BASE)):
    d = os.path.join(BASE, lang)
    if not os.path.isdir(d):
        continue
    for fn in sorted(os.listdir(d)):
        if fn not in RULES:
            continue
        p = os.path.join(d, fn)
        n = rewrite_keys(p, RULES[fn])
        print(f'{lang}/{fn}: {n} keys rewritten')
print('done')
