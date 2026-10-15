# -*- coding: utf-8 -*-
"""v0.5.2（本批 5 项，对话直接下发）：design\光道mod设计文档.md 尾部追加 v1.44 变更记录。"""
import io
import os

p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                 'design', '光道mod设计文档.md')

record = '''
---

## v1.44 珍珠世界事件重做 + 幻色珍珠 + 召唤师/萨满代价判定 + 雪之化身奖励泄漏（2026-10-15，v0.5.2，对话直接下发 5 项）

**任务与改动**（用户 5 条原话 → 实现）：

1. **事件立绘换图**：`Cache_574a0c16ebe486ca.png`（1920×1080，珠泪三姐妹海边）→ 原版事件画布 3440×1613。
   新素材是 16:9，与目标 2.133:1 接近，改成**顶部裁 180px 后 LANCZOS 直出**（不再模糊延展边条）——
   脚本 `tools\\make_pearl_event_art_v2.py`。产物覆盖 `...\\images\\events\\pearl_world_encounter.png`
   （文件名不变，`CustomInitialPortraitPath` 不用改；改图后必须 `Godot --headless --import` 再 ExportPck）。

2. **文案人设对调**：梅洛改活泼、小美人鱼改安静（原本相反）。三页全量对调：
   INITIAL（拍水花质问/捧珍珠眨眼两句互换）、JOIN 结局（唱歌、捞鳞片说"疼的时候就当我们在陪你"两句互换，
   并给"融合起来吧"补了"梅洛凑过来补了一句"点明说话人）、PEARLS 结局（递珍珠+轻声宽慰的人换成小美人鱼）。
   zhs 与 eng（回退副本）两份 events.json 同步。

3. **新增事件遗物「幻色珍珠」PhantomPearl**（`LightswornContent.cs`；id=`LIGHTSWORN_RELIC_PHANTOM_PEARL`）：
   - **图标**：游戏 pck 解出原版金色珍珠大图（BPTC ctex 用 Godot 解码：`research\\dirtest\\extract_pearls.gd`，
     在 headless Godot 里 `ProjectSettings.load_resource_pack` 游戏 pck 后 `get_image().save_png`），
     再 HSV 色相重映射成珠泪海蓝（`tools\\make_phantom_pearl_icon.py`，灰描边转微蓝）→ 64/256 两档进 `images\\relics\\`。
   - **效果**（拾起时以 `Owner.PlayerRng.Rewards` 掷一次，确定性同步）：1% → 发光珍珠（原版 RadiantPearl：
     每场战斗第一回合抽牌时 1 张「冷光」入手，`BeforeHandDraw`+`TurnNumber==1`+Owner 过滤）；其余各 50% →
     金色珍珠（+150 金）/诅咒珍珠（+1 张「贪婪」+333 金）。掷到的模式 `[SavedProperty] PearlMode` 持久化，
     描述里 `{Effect}` StringVar 在 setter 里刷新（读档 Fill 走 setter，文本自动恢复）。
   - **事件遗物语义**：`RelicRarity.Event`——RelicGrabBag.Populate 只收 Common/Uncommon/Rare/Shop，Event 档天然
     不进随机掉落；商店价 999999999。选项二悬停预览用 `HoverTipFactory.FromRelic<PhantomPearl>()`
     （原版 GraveOfTheForgotten 范式）。
   - **坑**：mod 类型用 `[SavedProperty]` 依赖 RitsuLib 的 `SavedPropertiesTypeCacheInjectionPatch`（0107/0111 都有）；
     新增带 SavedProperty 的模型会触发 ModelDb 确定性排序 → 联机握手哈希变，两端必须同 mod 版本（工坊更新说明已含此惯例）。

4. **选项二改赠遗物**：`TakePearls` 从 `PlayerCmd.GainGold(100)` 改为 `RelicCmd.Obtain<PhantomPearl>(Owner)`；
   事件 `CanonicalVars` 的 GoldVar(100) 删除；选项文案改"获得遗物[gold]幻色珍珠[/gold]。"；结局页文案同步点出幻色珍珠。

5. **雪之化身奖励泄漏（真 bug，用户此前反馈过）**：`SnowSpirit` 早前按用户要求从 Token 稀有度改金卡(Rare)后，
   原版 `CardFactory.CreateForReward` 对 Rare 没有任何令牌保护（只过滤 Basic/Ancient；Token 档靠"卡池不收录令牌"
   规避，mod 卡却全部挂在 LightswornCardPool 里）→ 会以金卡身份出现在战斗奖励/尘封魔典等。
   **修复**：`LightswornCardPool.FilterThroughEpochs` 覆写，剔除所有 `ShouldShowInCardLibrary==false` 的战斗专属牌
   （SnowSpirit/神影依/珠泪融合 Token），即它们从一切"卡池来源"（奖励/事件选牌/商店/变形/随机生成）消失，
   只保留战斗内效果生成。卡牌图鉴走 `ModelDb.AllCards`，不受影响。

6. **召唤师/萨满"必须付出代价才能发动"**（用户反馈：手牌只有光道召唤师也能发动拿卡回来）：
   - `Lumina`：`IsPlayable` 追加"手牌中除自己外还有牌"（可弃）；`OnPlay` 里没弃成（`chosen.Count==0`）直接 return，
     拿牌效果不发动（IsPlayable 挡常态 + 运行期双保险）；`ShouldGlowGoldInternal` 同步。
   - `TwilightLumina`：`IsPlayable` 追加"弃牌堆有「光道」牌"（可消耗）；`OnPlay` 里 `ExhaustOneFromDiscard` 返回
     null 时跳过拿回段（暮光能力照常施加）；`ShouldGlowGoldInternal` 同步。
   - 卡面文案补"手牌中有其他牌时才能打出。"/"弃牌堆中有「光道」牌时才能打出。"（同雪之化身范式）。

**验证（beta 0.107.1 实机，wininput.ps1 驱动 + 控制台）**：
- 编译 0 错误；Godot 重导入 3 张新 PNG；ExportPck 后 dist 与游戏 mods **pck md5 一致（182db22a…）**；
  日志 `Lightsworn, Version=0.5.2.0` + `Registered relic: PhantomPearl` + 零异常。
- 控制台 `event LIGHTSWORN_EVENT_PEARL_WORLD_ENCOUNTER` 直达 → `Preloading 'Event Room' Complete: assets=2` 无 Failed；
  **实机截图**：新立绘+对调文案+两选项正常显示；选项二悬停预览=幻色珍珠遗物卡 + 贪婪/冷光关联牌提示；
  点击选项二 → **掷到诅咒珍珠**（金币 99→432=+333）、左上角遗物栏出现蓝色珍珠图标、遗物悬浮框
  "当前效果：诅咒珍珠（获得1张贪婪与333金币）"——掷取/持久化/动态文本全链路实机通过。
- 附带发现（非本次改动引入，供后续排查）：涅奥事件交互时 BaseLib 3.4.7（工坊仍装的旧库，MissingLocPatch）
  会对本 mod 的 21 个能力打印 `GetRawText: Key 'XX_POWER.title' not found in table 'powers'`（旧格式键名），
  WARN 级、功能无影响；本批未动能力代码。
'''

t = io.open(p, encoding='utf-8').read()
assert '## v1.44' not in t, 'already appended'
io.open(p, 'a', encoding='utf-8', newline='').write(record)
print('design doc appended v1.44')
