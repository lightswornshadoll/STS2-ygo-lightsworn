# -*- coding: utf-8 -*-
"""设计文档尾部追加 v1.43（联机兼容轮，v0.5.1）"""
import io

PATH = r'D:\1-workdata\lightsworn_mod\design\光道mod设计文档.md'

ENTRY = """

## v1.43 联机（多人联机）兼容（2026-10-14，v0.5.1，用户任务「保证联机模式下大家可以一起玩」）

**背景（游戏本体联机架构实证，research\\sts2src_0111）**：STS2 联机=主机定序的确定性同步——
①握手校验「游戏版本 + gameplay 内容 mod 名单（清单 affects_gameplay=true，条目=id-版本）+ ModelIdSerializationCache.Hash
（全部模型/ID/属性名的全局哈希）」；②战斗为全端本地确定性模拟，每次行动结束/回合节点/事件退出各方上报
NetFullCombatState 的 XxHash32 校验和（含全部生物 HP/能力、玩家能量/金币、5 个战斗牌堆、RNG 集、
nextChoiceIds（玩家选择ID向量）、hook id），主机比对不一致→StateDivergence→断线弃局（无重同步）；
③玩家选择=PlayerChoiceSynchronizer 按玩家槽位自增 ID 同步（ReserveChoiceId 全端同点、本地 UI+SyncLocalChoice /
远端 WaitForRemoteChoice），选择 ID 向量进校验和；④行动同步 ActionQueueSynchronizer（hook 动作按自增 id 全端对齐）。
**结论：mod 内容只要全端同版本安装且行为确定（同输入同代码路径），即可联机；本 mod 的 gameplay 声明正确
（affects_gameplay=true，RitsuLib 内容注册哈希由 RitsuLib 确定性重建保障）。**

### 修复（三处，v0.5.1）

1. **玩家级钩子的 Owner 过滤缺失**（联机同角色时串效果/串弃牌）——`AfterPlayerTurnStartEarly` 是"每个玩家的回合
   开始各触发一轮"、`AfterCardPlayed` 是全场广播、卡牌钩子对所有玩家的牌触发，本体**不做 Owner 过滤**（过滤责任在模型）：
   - `Powers.cs`：SanctuaryPower/JanicePower/PrimevalScreamPower/ShaddollSchismPower/PurushaddollAeonPower/
     ShaddollZefracorePower/ShaddollZefranagaPower 的 `AfterPlayerTurnStartEarly` 加 `player != Owner.Player return`；
     LightBouncePower/HonestPower/ShaddollHoundPower 的 `AfterCardPlayed` 加 `cardPlay.Player != Owner.Player return`
     （照本体 StampedePower/HellraiserPower 范式）。
   - `LightswornContent.cs`：LightswornSigil.AfterPlayerTurnStartEarly 加 `player != Owner return`（圣徽弃光只在自己回合开始）。
   - 其余钩子（卡牌实例钩子 `card != this`、CatsAndDogs 的 `card.Owner != Owner`、Janice/Hound/TwilightGarb 的
     `participants.Contains(Owner)`、卡雷多哈特的 `player == Owner`）原本就正确，未动。
2. **融合生成锁按玩家隔离**（`LsUtil`）——原"每回合每张1次/文迪戈本场1次"锁是**每场战斗全局**（双光道组队互相抢锁、
   图鉴被队友的锁置灰）。改为 `FusionLockState` 内三个 `Dictionary<Player, HashSet<ModelId>>`
   （TearFusedThisTurn/ShaddollFusedThisTurn/BattleLocked），`RegisterFusionGenerated/IsFusionLocked/IsFusionUsedForCodex/
   CanFuseInto/IsFusionGenerated/LockFusionGeneratedThisTurn` 全部加 player 参数；单机行为不变（单玩家=全局）。
3. **起始遗物二选一的联机一致性**（`StartingRelicChoice.cs`）——原实现"弹窗任务里现场 ReserveChoiceId"：
   弹窗（独立任务、非阻塞）+ 队友可能抢先进房/出牌时，选择 ID 预定时点不可控 → ID 向量分叉 → 校验和分歧断线。
   改为：**选择 ID 在 FinalizeStartingRelics（StartRun 的 await 段，各端都跑且此刻无人能行动）里按 state.Players
   顺序一次性预定**；弹窗任务只做 本地开原版界面+SyncLocalChoice / 远端 WaitForRemoteChoice 配对
   （ChooseRelicCompat=RelicChoiceCmd.FromChooseARelicScreen 等价实现，只是 ID 预定时点不同）；
   界面异常时也同步一个"跳过"结果（否则对端永远停在 WaitForRemoteChoice）。日志加"已预定 N 个选择 ID（联机=…）"。

### 顺带修复（联机实测中发现的真 bug，非联机特有）

4. **角色语法/代词本地化键缺失 → 涅奥事件房卡死**（0.111 新增古代对话系统按 `{pronounSubject}` 等取词）：
   `LIGHTSWORN_CHARACTER_LIGHTSWORN_CHARACTER` 缺 `.titleObject/.pronounSubject/.pronounObject/.pronounPossessive/
   .possessiveAdjective` → `LocTable.GetRawText` 抛 LocException（BaseLib 先打 WARN）→ 事件 SetupLayout 中断 →
   选项渲染但不响应（同坑23 家族）。修复=补全 15 键（含 bestiaryQuote/eventDeathPrevention/goldMonologue/
   cardsModifierTitle/Description/aromaPrinciple/banter.alive|dead.endTurnPing——endTurnPing=联机回合结束喊话），
   并加 `localization\\eng\\characters.json` 回退拷贝（照 events.json 先例）。

### 验证（实机）

- 单机（beta 0.111.0）：0.5.1 加载零异常；涅奥事件（修复前选项无响应）修复后完整可选并给奖励；起始遗物二选一正常；
  融合图鉴 UI 正常。
- **联机（本机双开：官方测试台）**：游戏内置 `multiplayer test` 控制台命令（控制台=反引号键）
  → 内建 ENet 直连（host 127.0.0.1:33771 / join netId 1000）；**两个客户端进程各跑一份**
  （`tools\\wininput.ps1` 提供窗口摆放/截图/点击/按键/拖拽；游戏目录放 `steam_appid.txt`=2868840 才能免 Steam 直启）。
  双光道圣女组队实测：握手通过（MODDED(3) / HASH 一致）→ 对局开始 → 起始遗物二选一双方各自弹窗并同步成功
  （日志"已预定 2 个选择 ID（联机=True，玩家=1,1000）"）→ 双方均获光道圣徽 → 涅奥事件双方各自选择 →
  `fight CULTISTS_NORMAL`（控制台命令 IsNetworked=true 全端同步）进战斗 → 双方画面状态完全一致
  （HP 78/78、敌 88/88 与 116/116、能量 3/3、光道圣女立绘、mod 卡手牌）→
  **ChecksumTracker 4 次校验和（事件退出 id0 + 回合开始 id1，覆盖双光道回合开始的全部 mod 钩子：
  圣徽弃光/补卡组40/所有能力钩子/选择ID向量）全部匹配，日志零 divergence、零 ERROR**。
  未覆盖项（合成输入限制）：单张卡打出的 UI 拖拽流程未用自动化验证（代码路径与单机一致；弃牌/融合交互建议
  用户与朋友实机复测）。
- **联机使用须知**：所有玩家必须安装**同版本** mod（affects_gameplay=true → 版本不一致握手即 ModMismatch 拒绝；
  RitsuLib 亦需安装——依赖声明会强制）；混合队伍（光道+其他角色）可玩：事件「于珍珠世界相逢」按原设计
  IsAllowed=全员光道才出现（保留原设计）；选择界面弹出期间全桌等待（无 ctx 钩子里的 Blocking 选择上下文，
  与本体同类路径一致）。
"""

def main():
    with io.open(PATH, 'a', encoding='utf-8') as f:
        f.write(ENTRY)
    print('appended v1.43, new size:', __import__('os').path.getsize(PATH))

if __name__ == '__main__':
    main()
