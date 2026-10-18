using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Modding;
using STS2RitsuLib;
using STS2RitsuLib.Patching.Core;

namespace Lightsworn;

// Mod入口（v0.5.0：BaseLib → RitsuLib 迁移）。
// - 标签/关键词铸造必须早于 ModelDb 初始化（RitsuLib 在模型初始化时冻结注册）
// - 内容注册（卡/遗物/池/角色/事件）全部走 RitsuLib 特性自动发现（[RegisterCard] 等），这里无需手动注册
// - 补丁统一走 RitsuLib ModPatcher（patch id 注册、失败隔离/日志；不再 Harmony.PatchAll）
// - ScriptManagerBridge 不再需要（pck 内场景不引用游戏 C# 脚本）
[ModInitializer(nameof(Init))]
public static class Entry
{
    public static void Init()
    {
        Ls.RegisterTags();
        LsKeywords.RegisterAll();
        FusionCodexUI.Register();                                     // 顶栏「融合图鉴」按钮（RitsuLib 顶栏注册表）

        ModPatcher patcher = RitsuLibFramework.CreatePatcher("lightsworn", "core");
        patcher.RegisterPatch<StartingRelicChoicePatch>();            // 初始遗物二选一
        patcher.RegisterPatch<LightswornEnergyCounterOutlinePatch>(); // 能量球描边色（球体本体走 RitsuLib 场景路径，见角色类）
        patcher.RegisterPatch<HonestPowerLegacyPatch>();              // 欧尼斯特：0.107.x 五参 ModifyDamageMultiplicative
        patcher.RegisterPatch<TierraHalfDamageLegacyPatch>();         // 提耶拉·虚梦：0.107.x 五参伤害减半
        patcher.RegisterPatch<DarkWorldGraphaDiscoveryPatch>();       // 三层 Boss 发现顺序优先 mod Boss（格拉法→提耶拉）

        if (!RitsuLibFramework.ApplyRequiredPatcher(patcher, static () => { }, "Lightsworn core patches failed"))
            Log.Error("[Lightsworn] core patches failed; some features may be unavailable");
        else
            Log.Info("Lightsworn mod initialized!");

        // 三层 Boss 抉择事件：Act 2→3 过渡完成后、地图出现前插入（replay=false，避免初始化时误触发）。
        RitsuLibFramework.SubscribeLifecycle<ActEnteredEvent>(
            ThirdActBossChoiceTrigger.OnActEntered, replayCurrentState: false);
    }
}
