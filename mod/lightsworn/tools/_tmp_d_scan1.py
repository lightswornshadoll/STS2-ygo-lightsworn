import os

root = r'D:\1-workdata\lightsworn_mod\mod\lightsworn\Scripts'
pats = ['OnMilledByLsCard', 'class LsCard', 'class JudgementDragon', 'class PunishDragon',
        'class FlashFantasy', 'class SolarExchange', 'class TwilightErasure',
        'class TwinTwilightDragon', 'class JusticeWorld', 'class LightBounce',
        'Engraver', 'Lacrima', 'Hymn', 'RequiemCoffin', 'Lament']
for dirpath, dirs, files in os.walk(root):
    for fn in sorted(files):
        if not fn.endswith('.cs'):
            continue
        p = os.path.join(dirpath, fn)
        with open(p, encoding='utf-8') as f:
            for i, line in enumerate(f, 1):
                for pat in pats:
                    if pat in line:
                        print(f'{fn}:{i}: {line.rstrip()}')
