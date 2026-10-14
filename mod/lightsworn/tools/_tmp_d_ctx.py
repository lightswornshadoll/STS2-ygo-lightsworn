import os

root = r'D:\1-workdata\lightsworn_mod\research\sts2src'
files = [
    r'MegaCrit.Sts2.Core.Models.Cards\Aggression.cs',
    r'MegaCrit.Sts2.Core.Models.Cards\Afterimage.cs',
    r'MegaCrit.Sts2.Core.Models.Cards\Arsenal.cs',
    r'MegaCrit.Sts2.Core.Models.Cards\BeaconOfHope.cs',
    r'MegaCrit.Sts2.Core.Models.Cards\Alchemize.cs',
    r'MegaCrit.Sts2.Core.Models.Powers\DoomPower.cs',
]
for rel in files:
    p = os.path.join(root, rel)
    if not os.path.isfile(p):
        print('MISSING:', rel)
        continue
    print('=' * 20, rel)
    with open(p, encoding='utf-8-sig') as f:
        print(f.read())
