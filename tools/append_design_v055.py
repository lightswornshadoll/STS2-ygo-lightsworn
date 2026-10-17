# 设计文档追加 v1.49（v0.5.5 第四十二轮反馈）
from pathlib import Path

DOC = Path(r"D:\1-workdata\lightsworn_mod\design\光道mod设计文档.md")
TEXT = """

---

## v1.49 第四十二轮反馈：六条（2026-10-17，v0.5.5，已知问题.txt 下发）

**用户条目**：①雷喵敲后效果改敲前、敲后取消消耗；②裁决/惩戒伤害 30、敲后保留；双龙强化改为生成强化版；神光 30×3；
③惩戒只回攻击/技能/能力牌；④游戏王/圣徽都做成初始遗物，二选一丢另一个、skip 保留第一个；
⑤新增先古遗物「更好的游戏王」「光道权杖」；⑥探查做 Boss 所需美术/设计。

### 1. 雷喵（Rinyan）

- 基础 `Picks` 2→3（原升级 +1 改为基础效果）；`OnUpgrade` 从 `Picks+1` 改为 `RemoveKeyword(CardKeyword.Exhaust)`。
- 结果：基础 0 费、洗回最多 3 张、带「消耗」；强化后张数不变、移除「消耗」。
- 文案无需改（`{Picks:diff()}` 自动显示 3；消耗关键词由原版自动显示）。

### 2. 裁决之龙 / 惩戒之龙 / 双龙 / 神光之龙

- 裁决之龙：`DamageVar` 22→30；`OnUpgrade` 从伤害 +6 改为 `AddKeyword(CardKeyword.Retain)`。
- 惩戒之龙：`DamageVar` 22→30；`OnUpgrade` 同上改为「保留」；回收过滤加
  `c.Type is CardType.Attack or CardType.Skill or CardType.Power`（诅咒/状态等不回）。
- 黄昏之双龙：敲后不再 `AddKeyword(Retain)` 给生成的龙，而是对生成的
  `JudgementDragon`/`PunishDragon` 执行 `UpgradeInternal()+FinalizeUpgradeInternal()`（生成强化版对应卡；
  两条龙的「保留」由强化版自带）。cards.json 与卡牌图鉴同步为“改为生成强化版”。
- 神光之龙：`DamageVar` 22→30；升级仍为 +4（30×3/34×3）+ 保留。
- ⚠ 设计提醒（留给用户裁决）：`光道的裁决` 的 Token 本来就带「保留」；现在裁决之龙的强化只剩「保留」，
  所以「光道的裁决」敲后生成的强化版与基础版**不再有伤害差**。如希望这条升级仍有意义，
  建议给该 Token 换一个升级收益（例如费用 0→保留+抽 1，或提高 Token 伤害），本轮未擅自改。

### 3. 初始遗物（游戏王 / 圣徽）

- `LightswornSigil.Rarity` 从 `Uncommon` 改为 `Starter`——与 `MustPlayYugioh` 一样是初始遗物，不再进随机遗物池。
- 二选一逻辑保持：界面选项 `[游戏王, 圣徽]`；选圣徽→`RelicCmd.Replace(游戏王, 圣徽)`（丢弃另一个）；
  跳过→保留第一个游戏王。读档不走该流程，选择随存档持久。
- 说明：角色 `LocalStartingRelics` 仍只列游戏王；圣徽作为二选一的另一选项，稀有度已是 Starter。

### 4. 先古遗物（欧洛巴斯之触）

- 新增 `BetterMustPlayYugioh : MustPlayYugioh`：`Rarity => Ancient`；沿用基础版图标；
  `BeforeCombatStart` 只生成白/蓝/金卡，比例 **5:3:2**（每张固定 `NextInt(10)`，联机同种子可复现；不再生成打击/防御）。
- 新增 `LightswornScepter`：`Rarity => Ancient`；每回合开始 `LsUtil.Mill(player, 3)`，
  按弃置牌中「光道」牌数量抽牌（Owner 过滤，联机只在自己回合触发）。
- **欧洛巴斯精炼映射**（RitsuLib 正规入口）：
  - `[RegisterTouchOfOrobasRefinement(typeof(BetterMustPlayYugioh))]` 挂在 `MustPlayYugioh`
  - `[RegisterTouchOfOrobasRefinement(typeof(LightswornScepter))]` 挂在 `LightswornSigil`
  - 玩家最终持有的初始遗物是哪个，欧洛巴斯之触就替换成对应先古版（`TouchOfOrobasGetUpgradedStarterRelicPatch`）。
- 图标：权杖从 `images/character/battle.png` 裁杖头（`tools\\make_scepter_relic_icon.py`，裁切框 105,195–305,395），
  输出 64/256 圆形透明底 `relics/scepter.png`、`scepter_big.png`；更好的游戏王直接复用 `yugioh.png/_big`。
- 本地化：`relics.json` 新增 `LIGHTSWORN_RELIC_BETTER_MUST_PLAY_YUGIOH.title/.description`、
  `LIGHTSWORN_RELIC_LIGHTSWORN_SCEPTER.title/.description`。

### 5. Boss 探查

- 新增 `design\\boss制作需求.md`：技术结构（Encounter+Monster+RitsuLib 注册）、美术清单与实测规格
  （Boss 立绘、地图节点 350×307+描边、历史图标 85×85+描边、背景层约 2048×960）、
  设计清单（招式表/阶段/进阶/多人/奖励/文本）、静态图 vs Spine 路线与 MVP 模板。

### 验证（本轮）

- 构建：`dotnet build` **0 错误**（12 警告为历史基线）。
- memberref 审计：0.107.1 与 0.111.0 **双 PASS**（methods=188）。
- 部署：robocopy `/MIR /IS /IT` → 游戏 0.111.0 启动日志
  `Version=0.5.5.0`、`Lightsworn mod initialized!`、新遗物
  `BetterMustPlayYugioh / LightswornScepter` 均注册、**零 ERROR/Exception**。
- pck：`tools\\pck.py list` 确认含 `scepter.png / scepter_big.png`；解包 `relics.json` 两条新词条逐字正确。
- 产物：dll `4a6b78bf…`(352768) / json `5db7ec77…`(561) / pck `d7ca15da…`(21032120)。

### 发布注意

- 本轮改 dll + pck → 联机两端必须同为 **v0.5.5**；旧存档兼容（无内部 ID 变更）。
- 新增先古遗物依赖 RitsuLib 的欧洛巴斯精炼补丁（随 RitsuLib 0.6.7 已启用）。
"""

with DOC.open("a", encoding="utf-8", newline="\n") as f:
    f.write(TEXT)
print("appended", len(TEXT), "chars")
