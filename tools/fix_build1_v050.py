# 修复编译错误第一批：
# 1) ExtraHoverTips（ModCardTemplate 已 sealed）→ AdditionalHoverTips（6 处）
# 2) Powers.cs 补 using STS2RitsuLib.Patching.Models
import re, sys, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
root = r'D:\1-workdata\lightsworn_mod\mod\lightsworn\Scripts'

n_total = 0
for fn in os.listdir(root):
    if not fn.endswith('.cs'):
        continue
    p = os.path.join(root, fn)
    s = open(p, encoding='utf-8').read()
    n = s.count('protected override IEnumerable<IHoverTip> ExtraHoverTips')
    if n:
        s = s.replace('protected override IEnumerable<IHoverTip> ExtraHoverTips',
                      'protected override IEnumerable<IHoverTip> AdditionalHoverTips')
        open(p, 'w', encoding='utf-8', newline='\n').write(s)
        print(f'{fn}: {n} hover tip overrides renamed')
        n_total += n

p = os.path.join(root, 'Powers.cs')
s = open(p, encoding='utf-8').read()
if 'using STS2RitsuLib.Patching.Models;' not in s:
    s = s.replace('using STS2RitsuLib.Combat.Powers;',
                  'using STS2RitsuLib.Combat.Powers;\nusing STS2RitsuLib.Patching.Models;')
    open(p, 'w', encoding='utf-8', newline='\n').write(s)
    print('Powers.cs: added Patching.Models using')
print('total hover renames:', n_total)
