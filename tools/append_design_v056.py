# 设计文档追加 v1.50（v0.5.6 四条订正）
from pathlib import Path

DOC = Path(r"D:\1-workdata\lightsworn_mod\design\光道mod设计文档.md")
TEXT = """

---

## v1.50 第四十二轮追加订正四条（2026-10-17，v0.5.6）

**用户条目**：①神光之龙敲后不加伤害、只加保留；②神光/光道天使多段伤害文本改官方句式；
③黄昏之双龙敲后文案用「裁决之龙+」格式；④百科大全遗物收集看不到其他 mod 遗物。

### 1. 神光之龙

- `OnUpgrade` 删除 `DynamicVars.Damage.UpgradeValueBy(4)`，只保留 `AddKeyword(CardKeyword.Retain)`。
- 结果：基础/敲后都是 **30×3**；敲后额外获得「保留」。卡牌图鉴同步“伤害不变（仍30×3）”。

### 2. 多段伤害官方句式

- 官方中文卡面写法实测（游戏 `localization/zhs/cards.json`，如 CONFLAGRATION/EXTERMINATE）：
  `对所有敌人造成{Damage:diff()}点伤害{Repeat:diff()}次。` —— **不用“重复Y次”**。
- 光道天使 基路伯：`对所有敌人造成{Damage:diff()}点伤害{Hits:diff()}次。`
- 神光之龙：`对所有敌人造成{Damage:diff()}点伤害{Hits:diff()}次，并施加3层虚弱和3层易伤…`
  修复了之前“造成30点伤害，重复3次”的非官方语序。

### 3. 「卡名+」写法

- 黄昏之双龙：`否则：将1张「裁决之龙{IfUpgraded:show:+|}」和1张「惩戒之龙{IfUpgraded:show:+|}」置入弃牌堆。`
  基础显示「裁决之龙」/「惩戒之龙」，敲后显示「裁决之龙+」/「惩戒之龙+」；
  不再出现“（改为生成强化版）”。
- 顺带把「光道的裁决」的 `强化后的…「裁决之龙」` 也统一为 `「裁决之龙{IfUpgraded:show:+|}」`。
- 卡牌图鉴 `gen_card_doc.py` 的 SPECIAL 覆盖同步。

### 4. 百科大全遗物收集：圣徽/权杖不可见（根因 + 修复）

**根因**（反编译 `NRelicCollectionCategory.LoadRelics` 实证）：
- 「初始」页**不读** `ModelDb.AllRelics.Where(Rarity == Starter)`，而是：
  1. `ModelDb.AllCharacters.SelectMany(c => c.StartingRelics)`；
  2. 再对每件起始遗物调用 `TouchOfOrobas.GetUpgradedStarterRelic()` 追加先古版；
  3. 然后 **直接 return**。
- 所以只有写进 `Character.StartingRelics` 的遗物（及其欧洛巴斯先古版）会出现在初始页。
  游戏王在 `LocalStartingRelics` 里 → 游戏王 + 更好的游戏王可见；
  圣徽只改了 `Rarity=Starter`、没写进 `StartingRelics` → 圣徽和光道权杖都不显示。
- 猫狗双全（Common）/幻色珍珠（Event）本来就在“普通/事件”分区，不在初始页。

**修复**（`LightswornContent.cs` + `StartingRelicChoice.cs`）：
- `LocalStartingRelics` 改为 `[MustPlayYugioh, LightswornSigil]` —— 让收藏页的初始页能枚举到
  游戏王/圣徽，以及它们各自的先古版（更好的游戏王/光道权杖）。
- 实际开局两件都会先发下来；`FinalizeThenOffer` 在 `AfterObtained` 之前把
  `LightswornSigil` 从“持有游戏王”的玩家身上 Remove 掉（按 state.Players 顺序、各端一致），
  玩家仍然只持有游戏王，然后走原二选一（选圣徽=Replace 游戏王；skip=保留游戏王）。
- 这样收藏页四件齐全，实际开局/存档不会同时持有两件初始遗物。

### 验证

- 构建 0 错误；memberref 审计 0.107.1+0.111.0 **双 PASS**（methods=189）。
- pck 解包核对：CELESTIA/SHINING/TWIN/DECREE 四条文案逐字正确。
- 实机（0.107.1）：收藏页「初始」实拍=第一行含 **游戏王 + 光道圣徽**、第二行含
  **更好的游戏王 + 光道权杖**（权杖为未见过暗色）；用户确认“遗物没问题了”。
- 产物：dll `f59e1695…`(353280) / json `b9d4023f…`(561) / pck `e419e893…`(21032072)；v0.5.6 **未发布**。
"""

with DOC.open("a", encoding="utf-8", newline="\n") as f:
    f.write(TEXT)
print("appended", len(TEXT), "chars")
