# v0.5.0 RitsuLib 迁移批量转换：
# 1) 删除 using BaseLib.*;
# 2) [Pool(typeof(X))] → [RegisterCard(typeof(X))]
# 3) .FromCard(this) → .FromCardCompat(this, cardPlay)
# 4) Powers.cs: CustomPowerModel → ModPowerTemplate；图标两属性 → AssetProfile；临时力量包装器换名
import re, sys, os, glob
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
root = r'D:\1-workdata\lightsworn_mod\mod\lightsworn\Scripts'

changed_summary = []

def transform(path, fn):
    src = open(path, encoding='utf-8').read()
    out = fn(src)
    if out != src:
        open(path, 'w', encoding='utf-8', newline='\n').write(out)
        return True
    return False

# ---------- Cards1-8 ----------
for i in range(1, 9):
    p = os.path.join(root, f'Cards{i}.cs')
    def f(s):
        s = re.sub(r'^\s*using BaseLib\.[^;]+;\r?\n', '', s, flags=re.M)
        s = s.replace('[Pool(typeof(', '[RegisterCard(typeof(')
        s = s.replace('.FromCard(this)', '.FromCardCompat(this, cardPlay)')
        return s
    if transform(p, f):
        changed_summary.append(f'Cards{i}.cs')

# ---------- Powers.cs ----------
p = os.path.join(root, 'Powers.cs')
def f_powers(s):
    s = re.sub(r'^\s*using BaseLib\.[^;]+;\r?\n', '', s, flags=re.M)
    s = s.replace('using MegaCrit.Sts2.Core.CardSelection;',
                  'using MegaCrit.Sts2.Core.CardSelection;\nusing STS2RitsuLib.Combat.Powers;')
    s = s.replace(': CustomPowerModel', ': ModPowerTemplate')
    s = s.replace('CustomTemporaryPowerModelWrapper<Layden, StrengthPower>',
                  'ModTemporaryAppliedPowerTemplate<Layden, StrengthPower>')
    # 图标两行 → AssetProfile record
    pat = re.compile(
        r'public override string\? CustomPackedIconPath => "(res://lightsworn/images/powers/[^"]+)";\r?\n'
        r'([ \t]*)public override string\? CustomBigIconPath => "(res://lightsworn/images/powers/[^"]+)";')
    def rep(m):
        return (f'public override PowerAssetProfile AssetProfile => new(\n'
                f'{m.group(2)}    IconPath: "{m.group(1)}",\n'
                f'{m.group(2)}    BigIconPath: "{m.group(3)}");')
    s, n = pat.subn(rep, s)
    print(f'Powers.cs: {n} 个图标对转换为 AssetProfile')
    return s
if transform(p, f_powers):
    changed_summary.append('Powers.cs')

print('changed:', changed_summary)
