import io, os

root = r'D:\1-workdata\lightsworn_mod\tools\_decomp\Lightsworn'
p = os.path.join(root, 'LsUtil.cs')
t = io.open(p, encoding='utf-8-sig', errors='replace').read()
lines = t.splitlines()
pats = ['IsTearAttack', 'IsTear(', 'FusionOptions', 'Kitkallos', 'Reinohart', 'DiscardPile(', 'where', 'Where(']
for i, l in enumerate(lines, 1):
    s = l.strip()
    if 'IsTearAttack' in s or 'public static bool IsTear' in s:
        print(i, s[:170])
print('---- FusionOptions block ----')
start = None
for i, l in enumerate(lines, 1):
    if 'FusionOptions' in l:
        start = i
        break
if start:
    for i in range(start - 1, min(start + 40, len(lines))):
        print(i + 1, lines[i].rstrip()[:190])
