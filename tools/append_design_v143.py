# 设计文档尾部追加 v0.4.43 变更记录（第四十一轮17条，一次性脚本）
import io

DOC = r"D:\1-workdata\lightsworn_mod\design\光道mod设计文档.md"
record = """

---

## v1.40 第四十一轮17条（2026-10-14，v0.4.43，design\\已知问题.txt 下发）

1. **光之回弹调蓝**：Rare→Uncommon（效果不变：打出光道牌得2/3格挡）。
2. **影依的炎核 虚梦狱（HelshaddollHollow）重做**：2费攻击打15/20（升级=伤害+5不变）；主动打出的效果改为
   **弃光X（X=手牌中不同名「神影依」数量+1）**——原"可以从卡组弃置1张影依攻击卡→施加1层虚弱和易伤"作废；
   被弃置时弃光4 保留；加回「弃光」关键词。「神影依」判定=`LsUtil.IsElShaddollToken`（9张ShaddollToken，含翼影依影文蒂）。
3. **莱登（Layden）**："+4伤害"改为**弃光到「光道」牌→在本回合结束前获得2点临时力量**（先结算临时力量再打伤害，
   本次攻击也吃加成）。实现=BaseLib `CustomTemporaryPowerModelWrapper<Layden, StrengthPower>`（`LaydenTempStrengthPower`）：
   应用原版 StrengthPower、回合结束自动返还；图标/文案走 BaseLib 通用临时力量资源+游戏本体 TEMPORARY_STRENGTH_POWER 文案
   （中文=「在本回合结束前获得力量」），标题=卡牌名。升级仍=伤害+4（9/13）。
4. **光道天使 基路伯进白**：Uncommon→Common。
5. **影依兽升蓝**：Common→Uncommon。
6. **绊影依-神数原核（ShaddollZefracore）重做为2费能力·蓝卡**：获得能力「绊影依-神数原核」——**回合开始时从
   「影依的炎核 虚梦狱」「虚影依 神子晶」「神影依·神子晶」中随机生成1张加入手牌，其获得「消耗」**；
   生成的是神影依（ElShaddollGrysta，ShaddollToken）时**登记融合生成锁**（同残响=本回合不能再融合出该卡、图鉴置灰）；
   敲后费用2→1。原"打8/12+弃光4"作废；被弃置时（v0.4.40 订正）"从弃牌堆将1张影依牌置于抽牌堆顶"**保留**。
7. **救影依-神数纳迦（ShaddollZefranaga）重做为2费能力·蓝卡**：回合开始时从「圣影依 商神杖灵」「联结之影依化身」
   「影依的伪典」中随机生成1张加入手牌（同上获得「消耗」；三张都不是神影依、不占生成次数）；敲后2→1费。
   被弃置时"抽1张牌"保留（同上，未点名删除）。
8. **古尖兵/古卫兵**：条件由"2张以上→抽2"改为**每有3张对应类型牌→抽1**（弃光5/7；技能=阿基多、攻击=凯尔柏克；
   向下取整）。"被弃置时自动打出"保留。
9. **雷喵（Rinyan）重做**：0费、升蓝、加「消耗」；**从弃牌堆将最多{Picks}张「光道」牌洗回抽牌堆（自选0~上限），
   每有1种不同名的「光道」牌→获得1点费用**；洗回上限2/敲后3。原"洗回→抽X张"作废。
10. **光道龙 格拉古尼斯**：基础伤害18/敲后22（升级由"每张+3"改为**伤害+4**；"弃牌堆每张「光道」+2"保留）。
11. **加洛斯回调初版**：敲前=「光道」牌弃光后**只追加弃光2**；敲后=追加弃光2**并抽其中「光道」牌数量**的牌。
    v0.4.39 的"基础=抽牌 / 敲后=任意弃光都触发"整体作废（MillCore 的 OnAnyMill 通知点保留但两级都不响应；
    powers.json 双词条同步）。
12. **光道神域降蓝**：Rare→Uncommon。
13. **暮光道将军 简重做+进白**：Uncommon→Common；1费攻击**打9/12**，**可以**（0~1可选）消耗弃牌堆中1张「光道」牌，
    若如此做**额外造成5/7点伤害**；获得1层暮光（无条件）。原"消耗1张→16伤、没有则整张牌无效"作废。
14. **光道圣灵 夏尔进白**：Uncommon→Common。
15. **羽影依 文蒂**：被弃置效果**改成和打出相同**——回收影依攻击卡之外，同样给"本回合费用为0、伤害为0（打出一次后恢复）"
    （原被弃置只回收不加buff）。抽出 `FetchBuff` 私有方法供 OnPlay/OnDiscardedEffect 共用。
16. **黄昏之交衣追加效果**：**被从卡组弃置时（Draw→Discard，任意来源），获得"本回合打出「光道」牌获得2格挡（敲后3）"**
    ——新能力 `TwilightGarbPower : LightBouncePower`（继承光之回弹的 AfterCardPlayed；`AfterSideTurnEnd` 自我移除=
    "本回合"一次性），图标=卡图圆裁（zefracore/zefranaga/twilightgarb 三套新图标，tools\\make_power_icons_v443.py）。
    卡面新增 `Guard` 变量（2→3）驱动文案。
17. **卡雷多哈特全局限1次生成**：与文迪戈同款——**本场战斗只能生成1次**（`Locks(combat).BattleLocked`，
    RegisterFusionGenerated 内统一登记，WendigoLocked 改名 BattleLocked）；图鉴置灰同步；卡面加"[gold]本场战斗[/gold]此牌只能生成1次。"

**实现细节/拍板点**：
- 新能力 `ShaddollZefracorePower`/`ShaddollZefranagaPower`（Powers.cs；AfterPlayerTurnStartEarly，流世同款）：随机生成走
  `LsUtil.GenerateRandomToHand`（玩家侧 RNG `RunState.Rng.CombatCardSelection.NextItem` → `combat.CreateCard(概念卡, player)`
  → AddKeyword(Exhaust) → ShaddollToken 时 `LockFusionGeneratedThisTurn` → AddGeneratedCardToCombat(Hand)）。
- 炎核的"弃光X"在**造成伤害之后**结算（保留原顺序）；X 动态、卡面写死"X=手牌中不同名「神影依」的数量+1"（不进动态变量）。
- 莱登的临时力量在**攻击前**施加（本次攻击也受益）。
- 雷喵"回墓地x张光道"=从弃牌堆洗回**抽牌堆**（原卡定位"墓地光道回卡组"不变，仅地址词按用户说法"回墓地"）；能量按
  **所选牌的不同名数**给（1种=1费）。
- 交衣的"被从卡组弃置时"=Draw→Discard 任意来源（mod 惯用），非限光道卡来源。
- 绊影依/救影依的「被弃置时」效果按既有设计**保留**（用户未点名删除；绊影依的为 v0.4.40 用户点名订正）。
- 图鉴 gen_card_doc.py：VAR_LABEL 补 Guard/Temp；SPECIAL 表同步 Garoth/KaleidoHeart/Rinyan/TwilightGarb +
  新增 ShaddollZefranaga 条目；tools\\locfrag\\cards_6/7.json **全量同步**至当前 cards.json（此前有12处陈旧漂移，
  防未来重跑合并脚本回退旧文案；tools\\sync_locfrag.py）。
- 三张新能力图标（zefracore/zefranaga/twilightgarb 64/256）=卡图中心圆裁（make_power_icons_v443.py）。

**验证**：v0.4.43 构建（0错误）→ 新 PNG 先 Godot --headless --import → ExportPck（pck 20,466,604B）→
dist 三件套 md5 与游戏目录一致 → 启动游戏日志 `Version=0.4.43.0` + `Lightsworn mod initialized!` 零 Lightsworn 异常；
从部署 pck 解出 cards/powers.json 抽查（炎核/雷喵/交衣/加洛斯/绊影依/救影依）全部为新版；卡牌图鉴重跑（105张）。
**待用户/朋友复测**：炎核弃光X、莱登临时力量（BaseLib 包装器首次使用）、绊影依/救影依能力随机生成 + 消耗 + 神影依占锁、
雷喵0费回费、加洛斯初版双态、暮将军可选消耗、交衣被弃置临时回弹、卡雷多哈特本场限1。
"""
text = io.open(DOC, encoding="utf-8").read()
if "v1.40 第四十一轮17条" in text:
    print("already appended, skip")
else:
    io.open(DOC, "a", encoding="utf-8").write(record)
    print("appended v1.40 record")
