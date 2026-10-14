# -*- coding: utf-8 -*-
"""v0.5.0 大版本：BaseLib→RitsuLib 迁移 + beta 双版本兼容 + 救影依/绊影依调整。
向 design\光道mod设计文档.md 尾部追加变更记录（每次重写后运行）。"""
import io
import os

p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                 'design', '光道mod设计文档.md')

record = '''
---

## v1.42 BaseLib→RitsuLib 迁移 + beta 双版本兼容（2026-10-14，v0.5.0，用户三项任务）

**背景**：用户把游戏切到 beta（0.111.0）并下载 RitsuLib 0.6.7；三项任务：①mod 从 BaseLib 迁移到 RitsuLib；
②同一份 dll 同时支持正式版 0.107.1 与 beta 0.111.0；③救影依/绊影依 2费→1费、敲后固有。

**迁移总览**（完整对照表与风险清单见 `design\\ritsulib迁移方案.md`）：
- 卡牌/遗物/能力/池/角色/事件基类 → RitsuLib：`ModCardTemplate` / `ModRelicTemplate` / `ModPowerTemplate` /
  `TypeList{Card,Relic,Potion}PoolModel` / `ModCharacterTemplate<...>` / `ModEventTemplate`。
- `[Pool(typeof(X))]` → `[RegisterCard(typeof(X))]`（遗物 `[RegisterRelic]`、角色 `[RegisterCharacter]`、
  事件 `[RegisterSharedEvent]`；105 张卡 + 3 遗物全量替换，脚本 tools\\migrate_bulk_v050.py）。
- 标签（Lightsworn/EarthAngel/Fiendsmith/Tearlaments/Shaddoll）→ `ModCardTagRegistry` 铸造真实 CardTag；
  关键词（弃光/除光/暮光/珠泪融合/影融）→ `ModKeywordRegistry` 铸造真实 CardKeyword（id=LIGHTSWORN_KEYWORD_*，
  loc 键=LIGHTSWORN_KEYWORD_*.title/.description，BeforeCardDescription ≈ 旧 AutoKeywordPosition.Before）。
- 金色卡框：BaseLib ShaderColor → `PoolFrameMaterial`（游戏 hsv.gdshader + h/s/v，移植 BaseLib ShaderUtils）。
- 顶栏融合图鉴按钮：自 patch NTopBar + NButton 子类 → `ModTopBarButtonRegistry.Register("LIGHTSWORN_FUSION_CODEX", spec)`
  （保留旧 loc 键；打开界面/watcher 逻辑不变）。
- 古老牙齿：Barrier 上的 `ITranscendenceCard` → `[RegisterArchaicToothTranscendence(typeof(Aegis))]`。
- 金色卡框/临时力量/选牌/能量球的替代：见下"自建三件套"。
- 补丁：Harmony.PatchAll → `RitsuLibFramework.CreatePatcher` + `IPatchMethod`（3 生效 + 1 按设计忽略）。
- **Localization 键全量迁移**（RitsuLib 固定条目 = `{MOD}_{CATEGORY}_{TYPENAME}`）：
  cards→`LIGHTSWORN_CARD_*`、powers→`LIGHTSWORN_POWER_*`、relics→`LIGHTSWORN_RELIC_*`、
  character→`LIGHTSWORN_CHARACTER_LIGHTSWORN_CHARACTER`、event→`LIGHTSWORN_EVENT_PEARL_WORLD_ENCOUNTER`、
  关键词→`LIGHTSWORN_KEYWORD_*`、ancients 对白键同步（脚本 tools\\migrate_lockeys_v050.py + locfrag 同步迁移）。
  card_selection / static_hover_tips 为自建键不动。**旧存档（含进行中 run）因 ModelId 变化不再可用**。
- **双版本兼容层（tools 无关，代码层）**：0.107.1→0.111.0 三处硬签名破坏，全部以反射探测闭合：
  ①`AttackCommand.FromCard(card)`→`(card, cardPlay)`（42 处调用点→`LsCompat.FromCardCompat`）；
  ②`CreatureCmd.LoseBlock`→需 ctx+remover（艾琳 1 处→`LsCompat.LoseBlockCompat`）；
  ③`ModifyDamageMultiplicative` 5参→6参（欧尼斯特：编译期 6 参 override 覆盖 beta；正式版由
  `HonestPowerLegacyPatch` 对 5 参基类方法打 postfix 转发，ignoreIfMissing 让 beta 自动跳过）。
  其余 130+ 使用点/42 处 override 经双版本源码全量审计**签名一致**（审计脚本留 research\\api_audit\\）。
- **自建三件套**（RitsuLib 无对应物）：
  ①`MultiPileCardSelect` shim（浅封装 `CardSelectCmd.FromSimpleGrid`，签名同旧；**失去牌堆来源角标**）；
  ②能量球 `LightswornEnergyCounterPatch`（patch `NEnergyCounter.Create`，纯 C# 建节点树，移植 BaseLib FromLegacy
  精简版）+ 描边色补丁；③欧尼斯特正式版 postfix（见上）。
- 构建：csproj Import `RitsuLib.References.props`（`RitsuLibReferenceTarget=0.111.0`），删 BaseLib 引用；
  清单依赖改 `STS2-RitsuLib >= 0.6.7`；min_game_version 保持 0.107.1。

**③救影依/绊影依**：基础费用 2→1；敲后由"费用-1"改为**获得「固有」**（`OnUpgrade → AddKeyword(CardKeyword.Innate)`，
升级预览/卡面关键词行自动显示）。

**验证（beta 0.111.0 实机）**：构建 0 错 0 警 → ExportPck → robocopy /MIR /IS /IT → 启动：
`RitsuLib 0.6.7 [compat branch: 0.111.0]` 加载、5 标签/5 关键词铸造成功、顶栏按钮注册、
`[AutoRegister] Lightsworn: 111 operations, 111 succeeded, 0 failed`（105卡+3遗物+角色+事件+池）、
3 补丁生效 + 1 按设计忽略（honest_107）、日志零异常。图鉴重跑 105 张。
**正式版（0.107.1）无法本机实测**（Steam 只装了 beta 一份）——以"三处破坏点反射闭合 + 其余审计安全"背书；
正式版上线若见 MissingMethodException/TypeLoadException 即漏网（排查入口：本记录 §兼容层 三条）。
'''
t = io.open(p, encoding='utf-8').read()
assert '## v1.42' not in t, 'already appended'
io.open(p, 'a', encoding='utf-8', newline='').write(record)
print('设计文档已追加 v1.42')
