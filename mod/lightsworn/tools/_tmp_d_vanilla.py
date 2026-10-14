import os

roots = [
    r'D:\1-workdata\lightsworn_mod\research\sts2src',
    r'D:\1-workdata\lightsworn_mod\research\BaseLib-StS2-master',
]
pats = ['AddKeyword', 'UpgradeBy', 'class DoomPower', 'SetThisTurnOrUntilPlayed', 'class Aggression']
for root in roots:
    if not os.path.isdir(root):
        print('MISSING ROOT:', root)
        continue
    for dirpath, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in ('.git', 'obj', 'bin')]
        for fn in files:
            if not fn.endswith('.cs'):
                continue
            p = os.path.join(dirpath, fn)
            try:
                with open(p, encoding='utf-8-sig') as f:
                    for i, line in enumerate(f, 1):
                        for pat in pats:
                            if pat in line:
                                print(f'{p[len(root)+1:]}:{i}: {line.strip()[:160]}')
            except OSError as e:
                print('ERR', p, e)
