# v0.4.23 变更记录追加到 design\光道mod设计文档.md 尾部（一次性脚本）
import io

p = r'D:\1-workdata\lightsworn_mod\design\光道mod设计文档.md'

record = '''
---

## v1.22 第十轮反馈11条（2026-10-10，v0.4.23）

**来源**：`design\\已知问题.txt`（11条）。

**核心根因（问题1/3共因）**：融合结果选择界面把**不可变概念卡**（ModelDb 范例卡）直接传进
MultiPileCardSelect——`NSimpleCardSelectScreen._Ready` 读 `card.Owner` 时对不可变模型抛
**CanonicalModelException**，界面初始化中断、点击卡牌 NRE（v0.4.20 会话日志实证：珠泪融合选
Rulkallos、影融选 ElShaddollWinda 两处 `_Ready` 崩溃 + 2次 OnCardClicked NRE；选完虽能恢复
但交互残废）。影响全部融合触发卡（影依融合/神影依融合/魂影依融合/影依的原核/影依的伪典/
虚影依 神子晶/影依·拿非利 + 塞壬/小美/梅洛 + 心影依融合）的结果选择。修复=**LsUtil.PickConcept**：
概念卡先 `MutableClone()`+设 Owner 再进选择界面（FusionCodex 可变克隆先例的推广），
选中后按 Id 映射回原概念卡供 CreateCard。伤害置0（问题1）的 v0.4.22 恢复机制经源码核对无误；
心影依融合"伤害变0"观感失效即此界面崩溃所致。ZeroDamageOnce/恢复顺带 TryGetValue 加固。

11条逐一：
1. **伤害临时变0没有生效**：根因见上；v0.4.22 的"打出一次后恢复"机制本身有效。
2. **神我影依流世高亮**：`IsPlayable` 的 `Any(IsShaddoll)` 把手牌中的**自己**算进去（打出前本卡
   在手牌且自带影依标）→手牌无其他影依牌也高亮黄光、判为可打出（实际无牌可弃）。已排除自身
   （IsPlayable 与 OnPlay 弃置候选都加 `!ReferenceEquals(c, this)`）。
3. **魂影依融合不能手动选素材**：同问题1根因——素材选择（手牌真卡）没问题，坏在结果选择的
   概念卡界面崩溃。
4. **神影依第二次使用消耗**：ShaddollToken 实例计数 `_playCount`，`AfterCardPlayed` 计数≥2 时
   Exhaust（配合联结之影依化身的循环上限=每张2次）；9张神影依描述+影融词条同步加
   "第2次打出时消耗"。
5. **只有名字带影依才是影依卡**：ShaddollCard/ShaddollToken 基类**不再直接打标**，统一走
   Ls.ShaddollNamed 白名单（35→32张：移除炼狱的乖放/堕影的蠢动/影牢之咒缚）；
   LsUtil.OnShaddollDiscarded 的蠢动加倍/影文蒂层数/咒缚计数按 IsShaddoll 门控；
   ShaddollHoundPower 改标签制判定。三张卡自身被弃置只走自己的 OnDiscardedEffect（本无）。
6. **影融素材双角色占位**：新助手 **DistinctPair**——一张牌不能同时占「影依位」和「类型位」。
   文迪戈=影依+另1张技能、神子晶=影依+另1张攻击：影依攻击卡+非影依技能卡现在只能融文迪戈；
   拿非利同改（防患）。
7. **米德拉什**：融合条件=1张影依+1张影依/珠泪牌（DistinctPair：影依位+影依/珠泪位，双影依照旧）。
8. **珠泪融合素材必含触发卡**：TearFusion 选素材=触发卡（自动占1席）+其他珠泪攻击牌1~2张；
   珠泪融合词条与选牌提示同步。
9. **犀角龙融合卡位适配神影依**：条件=1张融合卡（TearFusionToken 或 ShaddollToken）+1张珠泪
   攻击牌（DistinctPair）。
10. **太阳交换**：IsPlayable=手牌有「光道」牌（+金光高亮）；描述加"仅当手牌中有「光道」牌时才能打出"。
11. **露米娜丝/暮露米娜丝**：拿2→1，各追加获得10格挡（BlockVar 10）。

**AI拍板**：①问题2按bug修复并在汇报里解释成因；②米德拉什=两角色语义（影依位+影依/珠泪位）；
③犀角龙"融合卡"定义=TearFusionToken 或 ShaddollToken；④神影依二打计数按实例（每张生成物
独立2次上限，实例随战斗销毁不跨局）；⑤暮露米娜丝格挡在拿牌后、给暮光前结算。

**验证**：v0.4.23 加载无异常（godot.log 实证）。
'''

with io.open(p, 'a', encoding='utf-8') as f:
    f.write(record)
print('OK: design doc appended')
