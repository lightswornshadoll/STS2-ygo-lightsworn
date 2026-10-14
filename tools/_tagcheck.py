import io, os, sys

root = r'D:\1-workdata\lightsworn_mod\tools\_decomp\Lightsworn'
files = ['TearFusionToken.cs', 'TearFusionCard.cs', 'Kitkallos.cs', 'Rulkallos.cs',
         'KaleidoHeart.cs', 'Dragostapelia.cs', 'Reinohart.cs', 'Suliek.cs',
         'Merrli.cs', 'Havnis.cs', 'LsCard.cs']
keys = ('CanonicalTags', 'base(', ' class ', 'CanonicalKeywords', 'Tearlaments')
for f in files:
    p = os.path.join(root, f)
    if not os.path.exists(p):
        print('=' * 20, f, '(missing)')
        continue
    t = io.open(p, encoding='utf-8-sig', errors='replace').read()
    print('=' * 20, f)
    for i, l in enumerate(t.splitlines(), 1):
        s = l.strip()
        if any(k in s for k in keys):
            print(' ', i, s[:160])
