import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
p1 = r'D:\1-workdata\lightsworn_mod\research\sts2src\MegaCrit.Sts2.Core.Commands.Builders\AttackCommand.cs'
p2 = r'D:\1-workdata\lightsworn_mod\research\sts2src_0111\MegaCrit.Sts2.Core.Commands.Builders\AttackCommand.cs'
for label, p in (('OLD-0.107.1', p1), ('NEW-0.111.0', p2)):
    print('=' * 20, label)
    for i, l in enumerate(open(p, encoding='utf-8', errors='replace')):
        if 'FromCard' in l:
            print(f'  {i+1}: {l.rstrip()}')
