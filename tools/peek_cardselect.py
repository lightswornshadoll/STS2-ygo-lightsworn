import sys, re
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
paths = {
    'OLD-0107': r'D:\1-workdata\lightsworn_mod\research\sts2src\MegaCrit.Sts2.Core.Commands\CardSelectCmd.cs',
    'NEW-0111': r'D:\1-workdata\lightsworn_mod\research\sts2src_0111\MegaCrit.Sts2.Core.Commands\CardSelectCmd.cs',
}
pat = re.compile(r'public static (?:async )?(?:Task<[^>]*>|Task|void)[^(]*\b('
                 r'FromSimpleGrid|FromCombatPile|FromHand|FromHandForDiscard|FromDeckGeneric|FromChooseACardScreen)\b')
for label, p in paths.items():
    print('=' * 25, label)
    for i, l in enumerate(open(p, encoding='utf-8', errors='replace')):
        if pat.search(l):
            print(f'  {i+1}: {l.strip()}')
