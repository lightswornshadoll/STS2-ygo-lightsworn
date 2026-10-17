# 做一个 Boss 需要准备什么（光道 mod，2026-10-17 探查）

> 结论先说：**一个可玩 Boss 的最小美术集 = 1 张 Boss 全身图 + 1 张 Boss 地图节点图标（含描边）+ 1 张历史记录小图标（含描边）**；  
> 背景可以先直接复用所在章节背景，音效先用原版通用音效，不做 Spine 也能上线。  
> 真正的工作量在**战斗设计（招式表/阶段/数值）**&#x548C;**动画表现**，不在“画一张 Boss 图”。

本文所有规格都来自游戏本体反编译源码与 pck 实测，路径/尺寸可直接照抄。

---

## 1. 技术结构：Boss = 一个 Encounter + 一个 Monster

RitsuLib 已提供 mod 遭遇/怪物的基类与注册特性，不需要改游戏本体：

```csharp
// 怪物：血量、招式状态机、意图、动画触发器
[RegisterMonster]
public class LightswornJudge : ModMonsterTemplate
{
    public override int MinInitialHp => ...;   // 普通难度基准
    public override int MaxInitialHp => ...;
    protected override MonsterMoveStateMachine GenerateMoveStateMachine() { ... }
}

// 遭遇：Boss 房间、出场怪物、地图节点、背景、BGM
[RegisterActEncounter(typeof(Underdocks))]     // 挂在哪个章节
public class LightswornJudgeBoss : ModEncounterTemplate
{
    public override RoomType RoomType => RoomType.Boss;
    public override IEnumerable<MonsterModel> AllPossibleMonsters => [ModelDb.Monster<LightswornJudge>()];
    protected override IReadOnlyList<(MonsterModel, string?)> GenerateMonsters()
        => [(ModelDb.Monster<LightswornJudge>().ToMutable(), null)];
    // 背景：默认 UseActCombatBackground = true（复用章节背景）；要专属背景再覆盖 AssetProfile
    // 地图节点/历史图标：EncounterAssetProfile
}
```

关键点（已核实）：

- **Boss 池来源**：`ActModel.AllBossEncounters = AllEncounters.Where(RoomType == Boss)`，  
  而 RitsuLib 把 `[RegisterActEncounter]` 的遭遇追加进 `GenerateAllEncounters()` → **注册后自动进入该章 Boss 随机池**。
- **Boss 奖励**：`RoomType.Boss` 会自动走原版 Boss 奖励流程（金币 100/100 + 卡牌 + Boss 遗物），不需要自己写奖励。
- **多人**：Boss HP 由 `Creature.ScaleHpForMultiplayer` 自动按人数与章节缩放；  
  招式里的随机数必须用 `monster.Rng` / `RunRng`（不要用 `GD.Rand`），否则联机校验和会断线。
- **首轮剧透顺序**：`ActModel.BossDiscoveryOrder` 只影响“未见过的 Boss 优先出场”，  
  原版 3 个 Boss 都见过之后，mod Boss 才会进入随机轮换；调试用控制台 `fight <ENCOUNTER_ID>` 直接打。  
  如果希望 mod Boss 更早出现，需要额外 patch `BossDiscoveryOrder`（目前 RitsuLib 只过滤、不追加）。

---

## 2. 美术素材清单（按必要性排序）

### 2.1 必需（没有就做不出来/会显示异常）

| 素材          | 规格                                       | 放哪里 / 命名                                                              | 备注                                                                                                               |
| ----------- | ---------------------------------------- | --------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| Boss 战斗形象   | 透明底全身立绘，建议 **1200×1600 以上**（越大越好，游戏内会缩放） | `mod\lightsworn\lightsworn\images\monsters\<boss_id>.png`             | 2D 静态方案：运行时建 `NCreatureVisuals`，参考本 mod 圣女的 `TryCreateCreatureVisuals()`；不要用引用游戏 C# 脚本的 tscn（导 pck 会丢脚本，坑 13/23） |
| Boss 地图节点图标 | **350×307 PNG** + 同尺寸 `_outline` 描边图     | `images\map\lightsworn\<encounter_id>_icon.png` / `_icon_outline.png` | 原版实测（lagavulin_matriarch_boss_icon = 350×307）；也可用 Spine 节点，但 PNG 最省事                                             |
| 历史记录小图标     | **85×85 PNG** + 同尺寸 `_outline`           | `images\ui\run_history\<encounter_id>.png` / `_outline.png`           | 原版实测 85×85；RitsuLib 的 `EncounterAssetProfile.RunHistoryIconPath` 可改路径                                            |
| 意图/血条/UI    | 不用画                                      | —                                                                     | 全部用原版通用资源（攻击/防御/增益/减益/召唤/睡眠等意图图标）                                                                                |
| 卡牌/遗物奖励     | 不用画                                      | —                                                                     | 用现有奖励池；除非你要专属 Boss 遗物（另加 64/256 遗物图标 + 大图）                                                                       |

> **2026-10-17 实测补充（拆了原版 Lagavulin Matriarch 全套素材核对）**：  
> ① 地图节点图标和描边都是**白色蒙版**，进图后由 `NBossMapPoint` 染色（图标=`act.MapTraveledColor`，描边=`act.MapBgColor`）——  
> 画成彩色图会被乘成近黑色，mod 图标要按白色线稿 + 白色实心剪影来画。  
> ② 历史/顶栏图标是 85×85 彩色成品，可照常画。  
> ③ 原版 Boss 的“专属背景”并不新画纹理：Lagavulin 的 14 个图层场景（15 张纹理）全部复用 `images/rooms/underdocks/` 的章节图，  
> 专属的只是图层组合 + 视差 + 雾/水/灯光 shader。  
> 完整参考（含尺寸、Spine 动画名、可复现导出脚本）：`design\boss美术参考\lagavulin_matriarch\`。

> 如果做 **Spine** 动画版：额外需要 `.skel` / `.atlas` / 图集 PNG / `_skel_data.tres`，  
> 以及 `idle_loop / attack / cast / hurt / die` 五套动画（可加特殊 trigger）。  
> 原版 Boss 的图集纹理实测约 **1900×965** 起，Boss 往往 3000+；这是最大的美术成本项。

### 2.2 强烈建议（影响体验，但不影响能不能跑）

| 素材          | 规格                                                                                                               | 说明                                                                                                                  |
| ----------- | ---------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| 专属战斗背景      | 若不复用章节背景：多层 2D 视差，单层纹理实测约 **2048×960**；命名 `_bg_00_a`、`_bg_01_a/b/c`…`_fg_a/b`，场景 `scenes/backgrounds/<id>_boss/` | 原版 Lagavulin Boss 有 4 组背景层 + 2 层前景；也可以只做 `bg_00_a` + `fg_a` 两层的静态背景。**最省事：`UseActCombatBackground = true` 直接用章节背景** |
| 攻击/受击/死亡音效  | FMOD event 路径                                                                                                    | 不填就用原版通用音效；专属音效需要 FMOD Studio 工程与 bank 打包，成本高，建议二期                                                                  |
| Boss 专属 BGM | FMOD event + bank                                                                                                | 原版 Boss 都有专属曲；不做就沿用章节 BGM（`CustomBgm` 留空）                                                                           |
| 技能特效        | 复用原版 VFX                                                                                                         | 斩击/爆炸/治疗/护盾等原版 VFX 可直接引用；专属 VFX 是加分项                                                                                |

### 2.3 静态图方案 vs Spine 方案

|      | 静态图（推荐先做）                                                                                                              | Spine 骨骼                                 |
| ---- | ---------------------------------------------------------------------------------------------------------------------- | ---------------------------------------- |
| 美术成本 | 1 张图 + 2 个小图标                                                                                                          | 拆件、绑定、蒙皮、5+ 套动画                          |
| 动画表现 | 运行时 `AnimationPlayer` 做 hurt/attack/cast/die（位移/缩放/透明度），本 mod 角色已验证                                                    | 原版标准链路，表现最好                              |
| 技术风险 | 需要 RitsuLib 的非 Spine 动画状态机（`SetupCustomCombatAnimationStateMachine` / `ModAnimStateMachine`）；本 mod 角色用的是角色专用转发，怪物侧要单独接 | 按原版 `MonsterModel.GenerateAnimator` 写，成熟 |
| 适合   | AI 立绘、快速上线、先验证玩法                                                                                                       | 正式 Boss、要上工坊精品                           |

**建议路线**：先用静态图 + 复用章节背景 + 原版音效做出可玩版本（MVP），  
验证招式/数值/多人；确认好玩后再决定是否补 Spine、专属背景和 BGM。

---

## 3. 设计工作清单（比美术更花时间）

### 3.1 战斗设计（必须先定）

1. **定位**：第几章 Boss？单体 / 多部件 / 带召唤物？HP 基准参考（普通难度）：
   - 一章：Vantom 173、Ceremonial Beast 252（The Kin 为多怪）
   - 二章：Knowledge Demon 379、Kaiser Crab（多部件）
   - 三章：Queen 400、Aeonglass 512、Test Subject（多形态）
   - 高进阶用 `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 高, 低)` 加 HP/伤害。
2. **招式表**：4~7 个 `MoveState`，每招写明：
   - 意图类型（`SingleAttackIntent` / `MultiAttackIntent` / `DefendIntent` / `BuffIntent` / `DebuffIntent` / `HealIntent` / `SummonIntent` / `SleepIntent` / `StunIntent` / `StatusIntent` …）
   - 伤害/段数/格挡/施加的 debuff 层数
   - 后续状态（`FollowUpState`）、随机分支（`RandomBranchState`）、条件分支（`ConditionalBranchState`）
   - 是否必须打一次才能转阶段（`MustPerformOnceBeforeTransitioning`）
3. **阶段设计**：半血转阶段？转阶段清 debuff？召唤小怪？改变意图池？阶段转换的动画/台词提示。
4. **反套路**：不能有“无限眩晕/无限格挡”导致软锁；Boss 的随机数必须可复现；避免一回合秒杀/无限循环。
5. **多人**：HP 自动缩放；AOE/单体目标；队友死亡后的继续战斗；禁止使用非确定性随机。
6. **奖励**：Boss 遗物（原版池自动给）、卡牌奖励、金币；是否掉专属遗物/事件。
7. **数值验收**：用控制台 `fight` 反复打，记录 3~~5 局的回合数、掉血、手牌曲线；目标回合数参考原版 Boss（约 8~~15 回合）。

### 3.2 叙事 / 文本

- Boss 名（`encounters` 表 `<ENCOUNTER_ID>.title`）
- 失败文案（`<ENCOUNTER_ID>.loss`，原版格式：`{character} was cut in half by the [gold]{encounter}[/gold].`，中文对应）
- 怪物名（`monsters` 表 `<MONSTER_ID>.name`）
- 每个招式的名字（`monsters` 表 `<MONSTER_ID>.moves.<MOVE_ID>.title`）
- 可选：图鉴描述、出场台词、击败台词、与光道角色的剧情关联
- 所有语言目录至少要给 `eng` 回退（本 mod 是 zhs-only，但事件/怪物缺键会 LocException/空界面）

### 3.3 本地化与资源导入

1. `Lightsworn.pck` 内置：`lightsworn/localization/zhs/encounters.json`、`monsters.json`
2. 新 PNG 必须先 `Godot --headless --import`，再 `dotnet build -t:ExportPck`（坑 13）
3. 部署后核对 pck 里确实有图/文案（`tools\pck.py list/extract`）
4. 进游戏用控制台 `fight <ENCOUNTER_ID>` 直达 Boss 战；日志搜 `Preloading ... Failed/Exception`
5. 多人测试：双开 + `multiplayer test`，确认零 divergence

---

## 4. 一个具体的 MVP Boss 模板（可直接照填）

以“光道主题的审判者”为例（名字/设定可换）：

- **章节**：Underdocks（二章）或 Overgrowth（一章）；建议二章，空间大。
- **HP**：普通 360 / 高进阶 400（参考二章 379~400）
- **形态**：单体，半血进入第二阶段（换意图池、获得 1 层人工制品/格挡）
- **招式**（5 个）：
  1. `JUDGEMENT`：单体 18 伤害 + 2 层虚弱
  2. `SCALES`：获得 15 格挡 + 1 层力量
  3. `VERDICT`：全体 9×2 伤害
  4. `PURGE`：弃置玩家 1 张手牌（`CardDebuffIntent`）＋自身获得 1 层仪式
  5. `EXECUTION`（半血后）：单体 30 伤害，每 3 回合一次（`ConditionalBranchState` 计数）
- **美术**：1 张 1400×1800 透明立绘 + 350×307 地图图标 + 85×85 历史图标
- **背景**：复用 Underdocks 章节背景
- **音效**：沿用原版通用攻击/受击/死亡音效
- **文本**：Boss 名/5 个招式名/失败文案/怪物名，中英各一份

这套 MVP 的美术工作量约 **1~2 天**（有现成立绘的话），  
代码+数值+联机验证约 **2~4 天**；加 Spine/专属背景/BGM 则按周计。

---

## 5. 需要你拍板的 5 件事

1. Boss 的主题/名字/原型（光道角色？暮光？珠泪？影依？还是原创）——决定立绘与配色。
2. 放第几章（一章/二章/三章），决定 HP/伤害基准与背景复用。
3. 单体还是多阶段/多部件——决定代码复杂度与美术数量。
4. 静态图还是 Spine——决定是否需要拆分绑定。
5. 是否要专属 Boss 遗物/事件/剧情——决定额外图标与文本量。

拍板后我可以直接按本文的清单开工：先出 `MonsterModel` + `EncounterModel` 骨架和一套可打数值，再逐步替换美术。
