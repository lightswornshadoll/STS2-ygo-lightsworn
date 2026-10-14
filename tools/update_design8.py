import io

p = r'D:\1-workdata\lightsworn_mod\design\光道mod设计文档.md'
t = io.open(p, encoding='utf-8').read()
entry = (
    '\n> v1.11（mod v0.4.8，第八轮反馈6条）：'
    '①**米迦勒"洗回全部卡"真根因修复**：前两轮过滤逻辑都是对的，真凶是回收后调用的 '
    '`CardPileCmd.Shuffle`——游戏源码注释明确其语义是"把玩家整个弃牌堆洗进抽牌堆"'
    '（打击/防御等非光道牌全被它洗回）。删除该调用，回收牌直接 Add 到抽牌堆底；'
    '描述"洗回"改"加入"，米迦勒判断逻辑不变（v0.4.6 定稿）；'
    '②珍妮丝：能力"回合结束回血N"改为"获得N点格挡"（JanicePower.BeforeSideTurnEnd '
    'Heal→GainBlock，文案同步）；'
    '③光道的裁决：被弃置时裁决之龙Token改加入**手牌**（原弃牌堆）；敲后从"2张"改为'
    '"1张**强化后的**裁决之龙"（Token 走 UpgradeInternal+FinalizeUpgradeInternal，'
    '参考 CardCmd.Upgrade 引擎实现；手牌满则不生成）；'
    '④**全部"移除敌方增益"效果按用户要求废除**（StripBuffs bug 多难修），改为施加'
    '对应层数的虚弱+易伤：雷光 1弱1易、暮雷光 1弱1易、黄昏之抹杀 每消耗1张=1弱1易；'
    'LsUtil.StripBuffs/StripAllBuffs/HasRemovalSideEffect 整体删除（v0.4.5 的 '
    'AfterRemoved 防护机制随之作废）；'
    '⑤光之放逐重做（问题3）：丢弃手牌中1张「光道」牌（自选，有则必选）+对目标施加'
    '虚弱2/敲后3，删除"移除所有增益"；'
    '⑥**新增卡 神光之龙 ShiningDragon**（稀有攻击，0费消耗）：弃牌堆存在「裁决之龙」'
    '和「惩戒之龙」时才能打出（金色发光）；消耗弃牌堆所有卡→对所有敌人造成44/56伤害'
    '（敲+12）并施加3层虚弱3层易伤→从消耗堆把两种龙各1张加入手牌（手牌满留在消耗堆）。'
    '原型=YGO 46186135（裁决+惩戒融合），卡图 tools\\make_shining_dragon_art.py 裁切 '
    'ygopro pics\\46186135.jpg；不打「光道」标（同裁决/惩戒）。部署验证：v0.4.8 日志'
    '加载无异常。版本 0.4.7→0.4.8。\n'
)
if 'v1.11（mod v0.4.8' not in t:
    t = t.rstrip('\n') + '\n' + entry
    io.open(p, 'w', encoding='utf-8').write(t)
    print('changelog appended')
else:
    print('already present')
