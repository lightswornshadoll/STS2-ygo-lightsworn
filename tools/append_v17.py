import io, os

base = r'D:\1-workdata\lightsworn_mod'
p = os.path.join(base, r'design\光道mod设计文档.md')
t = io.open(p, encoding='utf-8').read()
if 'v1.7（mod v0.4.2' not in t:
    entry = '\n> v1.7（mod v0.4.2，第五轮反馈4条，design\\已知问题.txt）：①光之援军检索源改回只从卡组（LsUtil.PickFromDraw，符合原版「增援部队」效果）；②**修复光道细剑不触发「光道的甲铠」**——Ls.LightswornNamed 白名单漏了 nameof(Sabre)，补上（光道卡 29→30 张），带标后 AegisPower 判定生效；③金卡强度调整（AI拍板，未降稀有度）：露米娜丝拿取数 1→2（升级仍0费）、暮光道萨满露米娜丝暮光 1/2→2/3（改 {Twilight:diff()} 变量）；④光之回弹重做为按**弃牌次数**触发：每次弃牌事件对所有敌人施加固定2层灾厄（敲后3，{Doom:diff()}），不再按张数计——LightBouncePower 用 ActionExecutor.CurrentlyRunningAction 做「同一次结算只触发1次」批处理（无动作环境时按回合同侧兜底键），Amount=每次弃牌的灾厄层数，多张叠加。版本 0.4.1→0.4.2。\n'
    io.open(p, 'w', encoding='utf-8').write(t.rstrip('\n') + entry)
    print('appended v1.7')
else:
    print('v1.7 already present')

ki = os.path.join(base, r'design\已知问题.txt')
if os.path.exists(ki):
    os.remove(ki)
    print('known-issues deleted')
else:
    print('known-issues already gone')
