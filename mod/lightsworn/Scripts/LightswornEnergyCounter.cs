using System.Reflection;
using Godot;
using Godot.Collections;
using HarmonyLib;
using MegaCrit.Sts2.addons.mega_text;
using MegaCrit.Sts2.Core.Assets;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Nodes.Combat;
using MegaCrit.Sts2.Core.Nodes.Vfx.Utilities;
using MegaCrit.Sts2.Core.TestSupport;
using STS2RitsuLib.Patching.Models;

namespace Lightsworn;

// ============ 圣女能量球（v0.5.0 迁移自建） ============
// RitsuLib 的能量球走"场景路径"（tscn 内需含 %EnergyVfxBack/%Layers/%RotationLayers/%EnergyVfxFront/Label 等
// 游戏脚本节点）——而 mod 导 pck 无法引用游戏 C# 脚本（v0.4.7 立绘同坑），因此自建：
// patch NEnergyCounter.Create(Player)（两版本签名一致），纯 C# 构建节点树后返回。
// 节点结构/配色/标签主题=BaseLib NEnergyCounterFactory.FromLegacy 的移植：
// Layer1=圣女能量球、Layer2-5=透明占位；描边色=深棕、粒子爆发色=金；数字标签 auto-size 32-36。
internal sealed class LightswornEnergyCounterPatch : IPatchMethod
{
    public static string PatchId => "lightsworn_energy_counter_create";
    public static string Description => "Build the Lightsworn character's energy counter at runtime (NEnergyCounter.Create prefix)";
    public static ModPatchTarget[] GetTargets() => [new ModPatchTarget(typeof(NEnergyCounter), "Create")];

    private const string AssetDir = "res://lightsworn/images/character/";
    private static readonly FieldInfo? PlayerField = AccessTools.Field(typeof(NEnergyCounter), "_player");
    private static readonly FieldInfo? ParticlesField = AccessTools.Field(typeof(NParticlesContainer), "_particles");

    // 描边色（原 CustomEnergyCounter.outlineColor；圣女=深棕）
    internal static readonly Color OutlineColor = new(0.25f, 0.18f, 0.05f);
    // 粒子爆发色（原 burstColor；圣女=金）
    private static readonly Color BurstColor = new(0.98f, 0.87f, 0.44f);

    public static bool Prefix(Player player, ref NEnergyCounter? __result)
    {
        if (player.Character is not LightswornCharacter) return true;
        if (TestMode.IsOn)
        {
            __result = null;
            return false;   // 对齐原版 Create 的 TestMode 行为
        }
        NEnergyCounter counter = Build();
        PlayerField?.SetValue(counter, player);
        __result = counter;
        return false;
    }

    private static NEnergyCounter Build()
    {
        NEnergyCounter counter = new() { Name = "LightswornEnergyCounter", Size = new Vector2(128f, 128f), PivotOffset = new Vector2(64f, 64f) };

        NParticlesContainer back = Particles("EnergyVfxBack");
        AttachUnique(counter, back);

        Control layers = FullRect();
        Control rotation = FullRect();
        rotation.PivotOffset = new Vector2(64f, 64f);
        AttachUnique(layers, rotation);   // %RotationLayers（layers 自身后挂，见下）
        AddLayer(layers, "Layer1", AssetDir + "energy_orb.png");
        AddLayer(rotation, "Layer2", AssetDir + "transparent.png", rotates: true);
        AddLayer(rotation, "Layer3", AssetDir + "transparent.png", rotates: true);
        AddLayer(layers, "Layer4", AssetDir + "transparent.png");
        AddLayer(layers, "Layer5", AssetDir + "transparent.png");
        AttachUnique(counter, layers);    // %Layers

        NParticlesContainer front = Particles("EnergyVfxFront");
        AttachUnique(counter, front);

        MegaLabel label = CreateDefaultLabel();
        counter.AddChild(label);
        label.Owner = counter;
        return counter;
    }

    // BaseLib NodeExtensions.AddUnique 的移植（Name + UniqueNameInOwner + 树外 Owner 注册）
    private static void AttachUnique(Node parent, Node child)
    {
        child.UniqueNameInOwner = true;
        parent.AddChild(child);
        child.Owner = parent;
    }

    private static NParticlesContainer Particles(StringName name)
    {
        NParticlesContainer container = new() { Name = name, Position = new Vector2(64f, 64f), Modulate = BurstColor };
        // _particles 私有：显式置空数组（否则能量增减的粒子调用 NRE）；照 BaseLib 反射写法
        ParticlesField?.SetValue(container, new Array<GpuParticles2D>());
        return container;
    }

    private static Control FullRect() => new()
    {
        AnchorRight = 1f,
        AnchorBottom = 1f,
        GrowHorizontal = Control.GrowDirection.Both,
        GrowVertical = Control.GrowDirection.Both,
        MouseFilter = Control.MouseFilterEnum.Ignore,
    };

    private static void AddLayer(Control parent, string name, string texturePath, bool rotates = false)
    {
        TextureRect layer = new()
        {
            Name = name,
            AnchorRight = 1f,
            AnchorBottom = 1f,
            GrowHorizontal = Control.GrowDirection.Both,
            GrowVertical = Control.GrowDirection.Both,
            MouseFilter = Control.MouseFilterEnum.Ignore,
            Texture = ResourceLoader.Load<Texture2D>(texturePath),
            ExpandMode = TextureRect.ExpandModeEnum.IgnoreSize,
            StretchMode = TextureRect.StretchModeEnum.KeepAspectCentered,
        };
        if (rotates) layer.PivotOffset = new Vector2(64f, 64f);
        parent.AddChild(layer);
        layer.Owner = parent;
    }

    private static MegaLabel CreateDefaultLabel()
    {
        MegaLabel label = new()
        {
            Name = "Label",
            AnchorRight = 1f,
            AnchorBottom = 1f,
            OffsetLeft = 16f,
            OffsetTop = -29f,
            OffsetRight = -16f,
            OffsetBottom = 29f,
            GrowHorizontal = Control.GrowDirection.Both,
            GrowVertical = Control.GrowDirection.Both,
            HorizontalAlignment = HorizontalAlignment.Center,
            VerticalAlignment = VerticalAlignment.Center,
            Text = "3/3",
            AutoSizeEnabled = true,
            MinFontSize = 32,
            MaxFontSize = 36,
        };
        label.AddThemeFontOverride(ThemeConstants.Label.Font, PreloadManager.Cache.GetAsset<Font>("res://themes/kreon_bold_shared.tres"));
        label.AddThemeColorOverride(ThemeConstants.Label.FontColor, new Color(1f, 0.964706f, 0.886275f, 1f));
        label.AddThemeColorOverride(ThemeConstants.Label.FontShadowColor, new Color(0f, 0f, 0f, 0.188235f));
        label.AddThemeColorOverride(ThemeConstants.Label.FontOutlineColor, new Color(0.3f, 0.0759f, 0.051f, 1f));
        label.AddThemeConstantOverride("shadow_offset_x", 3);
        label.AddThemeConstantOverride("shadow_offset_y", 2);
        label.AddThemeConstantOverride(ThemeConstants.Label.OutlineSize, 16);
        label.AddThemeConstantOverride("shadow_outline_size", 16);
        label.AddThemeFontSizeOverride(ThemeConstants.Label.FontSize, 36);
        return label;
    }
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
            __result = LightswornEnergyCounterPatch.OutlineColor;
            return false;
        }
        return true;
    }
}
