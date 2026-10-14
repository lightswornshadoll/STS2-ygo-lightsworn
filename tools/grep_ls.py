import os, re, sys

root = r'D:\1-workdata\lightsworn_mod\mod\lightsworn\Scripts'
patterns = [p.strip() for p in sys.argv[1:]] if len(sys.argv) > 1 else []
if not patterns:
    patterns = ['AfterCardDiscarded', 'OnMilledByLsCard', 'CreateToken', 'UpgradeInternal',
                'OnMillHappened', 'LightswornCardPool', 'CanonicalTags', 'AfterCardChangedPiles',
                'class.*Power', 'CanBeGenerated', 'ModelDb', 'CardType.Power']
for fn in sorted(os.listdir(root)):
    if not fn.endswith('.cs'):
        continue
    path = os.path.join(root, fn)
    with open(path, encoding='utf-8') as f:
        lines = f.readlines()
    for i, line in enumerate(lines, 1):
        for p in patterns:
            if re.search(p, line):
                print(f'{fn}:{i}: {line.rstrip()}')
                break
