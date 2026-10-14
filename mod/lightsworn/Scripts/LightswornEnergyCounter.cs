using System.Reflection;
using Godot;
using HarmonyLib;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Nodes.Combat;
using STS2RitsuLib.Patching.Models;

namespace Lightsworn;

// ============ 圣女能量球（v0.5.1：改走 RitsuLib 场景路径） ============
// 历史：
//  v0.4.x（BaseLib）—— BaseLib legacy CustomEnergyCounter(pathFunc, outlineColor, burstColor) → 工厂 FromLegacy 五层结构。
//  v0.5.0（RitsuLib）—— 误以为 RitsuLib 只支持"含游戏脚本节点的场景"，改为自建 patch NEnergyCounter.Create 前缀
//                        + 纯 C# 建节点树。**实测失效**：RitsuLib 自己的 Create 前缀（HarmonyPriority 800）
//                        在 mod 前缀（默认优先级）之前运行——它解析到"从占位角色（铁甲）继承的能量球场景"后
//                        建球并 return false，中止整条补丁链 → 游戏里显示的是铁甲的红色八角球。
//  v0.5.1 —— 改回正规入口：角色给 CustomEnergyCounterPath（saint_energy_counter.tscn，纯节点、无游戏脚本），
//            RitsuLib 的 CharacterEnergyCounterRuntimeFactoryPatch 会用 RitsuNEnergyCounterNodeFactory 转换建球，
//            缺失槽位（%EnergyVfxBack/%EnergyVfxFront/Label/%StarAnchor）自动补齐；自建 build 代码删除。
// 保留：OutlineColor getter 补丁（能量 0 时数字描边=深棕，原 BaseLib CustomEnergyCounter.OutlineColor 的替代）。

// 描边色（圣女=深棕）
internal static class LightswornEnergyColors
{
    internal static readonly Color OutlineColor = new(0.25f, 0.18f, 0.05f);
}

// 描边色：能量数字 0 时原版会取 Character.EnergyLabelOutlineColor，BaseLib 当年用 CustomEnergyCounter.OutlineColor
// 覆盖（深棕）。移植同款前缀补丁，保持观感一致。
internal sealed class LightswornEnergyCounterOutlinePatch : IPatchMethod
{
    public static string PatchId => "lightsworn_energy_counter_outline";
    public static string Description => "Outline color for the Lightsworn energy counter";
    public static ModPatchTarget[] GetTargets() => [new ModPatchTarget(typeof(NEnergyCounter), "OutlineColor", MethodType.Getter)];

    private static readonly FieldInfo? PlayerField = AccessTools.Field(typeof(NEnergyCounter), "_player");

    public static bool Prefix(NEnergyCounter __instance, ref Color __result)
    {
        if (PlayerField?.GetValue(__instance) is Player player && player.Character is LightswornCharacter)
        {
            __result = LightswornEnergyColors.OutlineColor;
            return false;
        }
        return true;
    }
}
