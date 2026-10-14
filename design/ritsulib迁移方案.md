# 《光道》mod:BaseLib → RitsuLib 迁移 + beta 双版本兼容方案

> v0.5.0（2026-10-14）。目标：①去掉 BaseLib 依赖、全面接入 RitsuLib 0.6.7；
> ②同一份 dll 同时支持正式版 0.107.1 与 beta 0.111.0；③救影依/绊影依改1费+敲后固有。

## 0. 环境事实（调研结论）

- 游戏 0.111.0（beta，`release_info.json`），稳定版=0.107.1（mod 原编译目标，BaseLib 3.4.7 支持）。
- RitsuLib 0.6.7（workshop 3747602295）：**分版本编译**，`compat/{0.107.1,0.109.0,0.110.0,0.111.0}/STS2-RitsuLib[.Runtime].dll` 对外 API 相同（0.110/0.111 变体源码逐文件一致；0.107 仅少数内部补丁文件有差异）。运行期 loader 按游戏版本选变体 → **mod 只需引用一个目标版本编译**。
- 引 RitsuLib：`<Import Project="$(RitsuLibDir)\RitsuLib.References.props"/>` + `<RitsuLibReferenceTarget>0.111.0</RitsuLibReferenceTarget>`。
- 0.111 的 ModelDb 原生发现 mod 程序集的 AbstractModel 子类型（`ReflectionHelper.GetSubtypesInMods`）；池成员通过 `ModHelper.AddModelToPool`（RitsuLib 的 `[RegisterCard]` 底层就是它）。

## 1. 破坏性 API 差异（0.107.1 → 0.111.0，mod 用到的部分）

| # | 旧 (0.107.1) | 新 (0.111.0) | 处理 |
|---|---|---|---|
| 1 | `AttackCommand.FromCard(CardModel)` | `FromCard(CardModel, CardPlay?)`（旧签名删除） | **反射兼容**：`LsCompat.FromCard(this, card, cardPlay)`，42 处调用点机械替换 |
| 2 | `CreatureCmd.LoseBlock(Creature, decimal)` | `LoseBlock(PlayerChoiceContext, Creature, decimal, Creature?)` | 反射兼容 `LsCompat.LoseBlock(...)`（1 处：艾琳） |
| 3 | `ModifyDamageMultiplicative(…, CardModel?)` 5参 | 6参（+`CardPlay?`） | 欧尼斯特：编译期写 6 参 override（0.111 生效）；**0.107.1 运行时**在 Init 里检测 5 参方法存在→给 `AbstractModel.ModifyDamageMultiplicative`(5参) 打 Harmony postfix 转发到 HonestPower 的逻辑 |

其余 mod 用到的全部 API 经逐项审计（130 使用点 + 42 override + Harmony 目标 + 枚举）**签名一致**，安全。
（`Hook.ModifyDamage` 加 CardPlay、`FromCard` 等变化不影响我们直接使用面。）

## 2. BaseLib → RitsuLib 对照（本项目实际用到的）

| BaseLib | RitsuLib 替代 | 备注 |
|---|---|---|
| `CustomCardModel` | `Scaffolding.Content.ModCardTemplate` | 构造签名相同；`CustomPortraitPath` 保留可覆写（IModCardAssetOverrides） |
| `CustomCardPoolModel`/`CustomRelicPoolModel`/`CustomPotionPoolModel` | `TypeList{Card,Relic,Potion}PoolModel` | `Title/DeckEntryCardColor/IsColorless/EnergyColorName` 覆写游戏成员；要自己覆写 `EnergyColorName`（BaseLib 是自动的） |
| `ShaderColor`（金色卡框） | `PoolFrameMaterial`（自建 ShaderMaterial） | 用游戏 `res://shaders/hsv.gdshader` + h/s/v 参数（移植 BaseLib ShaderUtils.GenerateHsv） |
| `[Pool(typeof(X))]` | `[RegisterCard(typeof(X))]`（`STS2RitsuLib.Interop.AutoRegistration`） | 遗物 `[RegisterRelic]`；池/角色按注册表 |
| `CustomRelicModel` | `ModRelicTemplate` | 图标：`RelicAssetProfile(IconPath, IconOutlinePath, BigIconPath)` |
| `PlaceholderCharacterModel` | `ModCharacterTemplate<TCardPool,TRelicPool,TPotionPool>` | `PlaceholderCharacterId="ironclad"` 缺省补全；`LocalStartingDeck/LocalStartingRelics` 覆写（sealed 的 StartingDeck 自动合并） |
| `CreateCustomVisuals()` | `TryCreateCreatureVisuals()` | 纯 C# 建 NCreatureVisuals；动画（hurt/attack/cast/die）由 RitsuLib `ModCreatureVisualPlayback` 自动转发（别名表命中） |
| `CustomEnergyCounter`(legacy) | **无对应** → 自建 | 自写 `NEnergyCounter.Create` 前缀补丁，C# 运行时构建（移植 BaseLib FromLegacy 精简版） |
| `CustomEventModel` | `ModEventTemplate` + `[RegisterSharedEvent]` | 不再构造自注册；Option 键=`InitialOptionKey("JOIN_TEARLAMENTS")` 同旧格式 |
| `[CustomEnum]`+`[KeywordProperties]`（关键词） | `ModKeywordRegistry.For(modId).RegisterOwned(...)` | 铸真 CardKeyword 值；loc 键=显式传入；`BeforeCardDescription` ≈ BaseLib `AutoKeywordPosition.Before` |
| `[CustomEnum]`（CardTag） | `ModCardTagRegistry.For(modId).RegisterOwned(stem)` | 同上 |
| `ITranscendenceCard` | `[RegisterArchaicToothTranscendence(typeof(Aegis))]`（标在 Barrier 上） | 或 `RitsuLibFramework.RegisterArchaicToothTranscendenceMapping` |
| `MultiPileCardSelect` | **无对应** → 自建 `Lightsworn.MultiPileCardSelect`（同名同签名 shim） | 内部=`CardSelectCmd.FromSimpleGrid`（两版本签名一致）；**失去牌堆来源角标**（游戏无此 UI；候选仍严格限定） |
| `RelicImageOverridePatch` | `ModRelicTemplate.AssetProfile`（自有遗物） | |
| 顶栏按钮（自 patch NTopBar + NButton 子类） | `ModTopBarButtonRegistry.For("lightsworn").Register("LIGHTSWORN_FUSION_CODEX", spec)` | 用 Register(全局ID) 保留旧 loc 键；删除自建按钮类与 NTopBar 补丁 |
| `CustomTemporaryPowerModelWrapper<TModel,TPower>` | `Combat.Powers.ModTemporaryAppliedPowerTemplate<TOriginModel,TPower>` | 泛型顺序相同（莱登临时力量） |
| `Harmony.PatchAll` | `RitsuLibFramework.CreatePatcher("lightsworn", ...)` + `RegisterPatch<IPatchMethod>` | 或保留裸 Harmony patch（RitsuLib 兼容）；本项目用 ModPatcher |
| `ScriptManagerBridge.LookupScriptsInAssembly` | 不需要 | pck 内的 tscn 无脚本引用 |

## 3. 本地化键迁移（RitsuLib 固定条目 = `{MOD}_{CATEGORY}_{TYPENAME}`）

`Id.Entry` 变化 ⇒ loc 键必须整体重命名（写入脚本一次性完成）：

| 表 | 旧 | 新 |
|---|---|---|
| cards.json | `LIGHTSWORN-LIGHT_BLADE.title` | `LIGHTSWORN_CARD_LIGHT_BLADE.title` |
| powers.json | `LIGHTSWORN-GAROTH_POWER.title` | `LIGHTSWORN_POWER_GAROTH_POWER.title` |
| relics.json | `LIGHTSWORN-MUST_PLAY_YUGIOH.title` | `LIGHTSWORN_RELIC_MUST_PLAY_YUGIOH.title` |
| characters.json | `LIGHTSWORN-LIGHTSWORN_CHARACTER.title` | `LIGHTSWORN_CHARACTER_LIGHTSWORN_CHARACTER.title` |
| events.json | `LIGHTSWORN-PEARL_WORLD_ENCOUNTER…` | `LIGHTSWORN_EVENT_PEARL_WORLD_ENCOUNTER…` |
| card_keywords.json | `LIGHTSWORN-MILL.title` | `LIGHTSWORN_KEYWORD_MILL.title` |
| ancients.json | `THE_ARCHITECT.talk.LIGHTSWORN-LIGHTSWORN_CHARACTER.…` | `…talk.LIGHTSWORN_CHARACTER_LIGHTSWORN_CHARACTER.…` |
| card_selection.json / static_hover_tips.json | 自建键，**不变** | `LIGHTSWORN_TO_HAND` / `LIGHTSWORN_FUSION_CODEX`（顶栏按钮用 Register(全局ID) 保持一致） |

⚠ 存档兼容：卡牌 ModelId 变化，旧存档（含进行中的 run）中旧 ID 的卡解析不到——升级即换新存档/新开 run。
（Beta 与稳定版之间的存档同样不通用。）

## 4. 构建/验证

- csproj：删 BaseLib 引用，Import RitsuLib props（target 0.111.0），仍引用 sts2/0Harmony。
- 清单：dependencies 改 `STS2-RitsuLib >= 0.6.7`。
- 构建→导出 pck→部署 beta→查日志（应见 RitsuLib 初始化 + Lightsworn 关键词/内容注册 + 零异常）。
- 稳定版（0.107.1）无法本机实测（Steam 只有 beta 一份安装）：
  用"破坏性差异清单（§1）逐条闭合 + 其余 API 审计为安全"的方式保证；
  上线观察视角：正式版日志若见 `MissingMethodException`/`TypeLoadException` 即 §1 漏网。
