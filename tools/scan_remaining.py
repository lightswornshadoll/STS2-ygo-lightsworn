import re, sys, glob, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
root = r'D:\1-workdata\lightsworn_mod\mod\lightsworn\Scripts'
pats = {
    'using-BaseLib': re.compile(r'^\s*using BaseLib\.'),
    'Pool-attr': re.compile(r'\[Pool\('),
    'BaseLib.Utils.Pool': re.compile(r'BaseLib\.Utils\.Pool'),
    'FromCard': re.compile(r'\.FromCard\('),
    'CustomPowerModel': re.compile(r'CustomPowerModel'),
    'CustomPackedIconPath': re.compile(r'CustomPackedIconPath'),
    'CustomBigIconPath': re.compile(r'CustomBigIconPath'),
    'TemporaryWrapper': re.compile(r'CustomTemporaryPowerModelWrapper'),
    'ITranscendence': re.compile(r'ITranscendenceCard'),
    'CustomCardModel': re.compile(r'CustomCardModel'),
    'HoverTipFactory': re.compile(r'HoverTipFactory'),
    'AddChildSafely': re.compile(r'AddChildSafely'),
    'CustomEventModel': re.compile(r'CustomEventModel'),
    'MultiPileCardSelect': re.compile(r'MultiPileCardSelect'),
    'CustomEnergyCounter': re.compile(r'CustomEnergyCounter'),
    'LoseBlock': re.compile(r'LoseBlock\('),
    'ModifyDamageMultiplicative': re.compile(r'ModifyDamageMultiplicative'),
    'RelicImageOverride': re.compile(r'RelicImageOverridePatch|RelicIconData'),
    'PlaceholderCharacter': re.compile(r'PlaceholderCharacterModel'),
    'NModListButton-NButton': re.compile(r'NButton'),
    'KeywordProps': re.compile(r'KeywordProperties|CustomEnum'),
}
for name, pat in pats.items():
    print('=' * 25, name)
    for f in sorted(glob.glob(os.path.join(root, '*.cs'))):
        base = os.path.basename(f)
        if base in ('GlobalUsings.cs', 'LsCompat.cs', 'MultiPileCardSelect.cs', 'LightswornEnergyCounter.cs'):
            continue
        for i, l in enumerate(open(f, encoding='utf-8'), 1):
            if pat.search(l):
                print(f'  {base}:{i}: {l.strip()[:130]}')
