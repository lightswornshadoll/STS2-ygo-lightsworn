import re, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
t = open(r'D:\1-workdata\lightsworn_mod\tools\_ritsu_variant_diff.txt', encoding='utf-8', errors='replace').read()
blocks = t.split('=' * 100)
want = ['ModCharacterTemplate', 'RitsuNCreatureVisualsNodeFactory', 'ModContentRegistry',
        'Sts2ModManagerCompat', 'CardOnPlayHookPatch', 'ModCardVars', 'SpineAnimationBackend']
out = []
for b in blocks:
    m = re.search(r'FILE: (.+)', b)
    if m and any(w in m.group(1) for w in want):
        out.append('=' * 90)
        out.append(b.strip()[:5000])
print('\n'.join(out))
