# refs —— 编译参考程序集（固定副本）

这个目录存放**编译期**引用的程序集，不随 Steam 分支切换变化。**不进 git 仓库**（游戏/RitsuLib 二进制版权文件）。

| 文件 | 来源 | 作用 |
|---|---|---|
| `data\sts2.dll` | 游戏 **0.111.0** 分支的 `data_sts2_windows_x86_64\sts2.dll` | 源码按 0.111 的 6 参 `ModifyDamageMultiplicative` 编译（迁移方案表 3） |
| `data\0Harmony.dll` | 同上目录 | patch 框架 |
| `RitsuLib\` | 创意工坊 RitsuLib 全量（3747602295） | `RitsuLib.References.props` + compat 变体 |

## 首次采集

1. Steam 里把游戏切到 **0.111.0** 测试分支并等更新完成
2. 运行 `tools\collect_refs.ps1`（会校验版本并复制）
3. 校验通过后即可把游戏切回正式版，**之后编译永远读本目录，不用再切分支**

## 为什么必须固定成 0.111

正式版 0.107.1 的 `sts2.dll` 只有 **5 参** `ModifyDamageMultiplicative`（`Creature, decimal, ValueProp, Creature, CardModel`），
而源码 `Powers.cs` 里 `HonestPower` 是 **6 参 override**（+`CardPlay?`）—— 直接引用游戏目录编译会报 `CS0115`。

编译产物在运行期对两个版本都兼容：跨版本差异由 `LsCompat`（反射）与 `HonestPowerLegacyPatch`（0.107 上给 5 参方法打 postfix 转发）闭合。
