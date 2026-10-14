# 盘点光道mod源码对 BaseLib 的全部 API 依赖（迁移用清单）
import os, re, glob, collections

ROOT = r'D:\1-workdata\lightsworn_mod\mod\lightsworn'
files = [f for f in glob.glob(os.path.join(ROOT, '**', '*.cs'), recursive=True)]

usings = collections.Counter()
symbols = collections.Counter()
sym_lines = collections.defaultdict(list)

# BaseLib 的命名空间前缀
ns_pat = re.compile(r'^\s*using\s+(BaseLib[\w\.]*)\s*;')
# 常见 BaseLib 类型/成员引用（含全限定与非全限定）
sym_pat = re.compile(r'\b('
    r'PoolAttribute|Pool|ITranscendenceCard|CustomTemporaryPowerModelWrapper|'
    r'MultiPileCardSelect|PlaceholderCharacterModel|CustomEventModel|'
    r'CustomEnergyCounter|RelicImageOverridePatch|RelicIconData|'
    r'ArchaicToothTranscendenceUpgradesPatch|ContentPatches|'
    r'BaseLibMain|ModHelper|CustomCardPool|CustomRelicPool|CustomPotionPool|'
    r'CustomCharacter|CustomPotion|CustomRelic|CustomCard|AbstractModel|'
    r'CardImageOverridePatch|PowerImageOverridePatch|'
    r'HoverTipFactory|NModListButton|Config|'
    r'TemporaryPowerModelWrapper|CustomAnimationPatch|SpineAnimationAccess'
    r')\b')

for f in files:
    rel = os.path.relpath(f, ROOT)
    for i, line in enumerate(open(f, encoding='utf-8'), 1):
        m = ns_pat.match(line)
        if m:
            usings[m.group(1)] += 1
        for m2 in sym_pat.finditer(line):
            sym = m2.group(1)
            symbols[sym] += 1
            if len(sym_lines[sym]) < 6:
                sym_lines[sym].append(f'{rel}:{i}: {line.strip()[:110]}')

print('=== files:', len(files))
print('=== using BaseLib.* namespaces ===')
for k, v in usings.most_common():
    print(f'  {v:4d}  {k}')
print('=== symbol occurrences ===')
for k, v in symbols.most_common():
    print(f'  {v:4d}  {k}')
print('=== sample lines per symbol ===')
for k in symbols:
    print(f'--- {k}')
    for l in sym_lines[k]:
        print('   ', l)
