using System.Reflection;
using Godot;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Commands.Builders;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;

namespace Lightsworn;

// ============ 跨游戏版本兼容层（v0.5.0：0.107.1 正式版 ↔ 0.111.0 beta 同一份 dll） ============
// 三处签名在 0.107.1 → 0.111.0 之间被游戏改掉，且旧签名直接删除——静态绑定任一版本都会在另一版本
// 抛 MissingMethodException。这里统一用"反射探测+调用"的兼容入口（MethodInfo 缓存，只在卡牌结算时调用，开销可忽略）。
internal static class LsCompat
{
    // ① AttackCommand.FromCard：0.111 起必须带 CardPlay（旧单参重载删除）
    private static readonly MethodInfo? FromCardWithPlay = typeof(AttackCommand)
        .GetMethod("FromCard", [typeof(CardModel), typeof(CardPlay)]);
    private static readonly MethodInfo? FromCardLegacy = typeof(AttackCommand)
        .GetMethod("FromCard", [typeof(CardModel)]);

    // 卡牌攻击统一入口：卡内调用传 OnPlay 的 cardPlay；无 CardPlay 上下文（能力/遗物触发）传 null
    public static AttackCommand FromCardCompat(this AttackCommand command, CardModel card, CardPlay? cardPlay)
    {
        if (FromCardWithPlay != null)
            return (AttackCommand)FromCardWithPlay.Invoke(command, [card, cardPlay])!;
        return (AttackCommand)FromCardLegacy!.Invoke(command, [card])!;
    }

    // ② CreatureCmd.LoseBlock：0.111 起需要 PlayerChoiceContext + remover（旧两参重载删除）
    private static readonly MethodInfo? LoseBlockWithContext = typeof(CreatureCmd)
        .GetMethod("LoseBlock", [typeof(PlayerChoiceContext), typeof(Creature), typeof(decimal), typeof(Creature)]);
    private static readonly MethodInfo? LoseBlockLegacy = typeof(CreatureCmd)
        .GetMethod("LoseBlock", [typeof(Creature), typeof(decimal)]);

    public static Task LoseBlockCompat(PlayerChoiceContext ctx, Creature target, decimal amount, Creature? remover)
    {
        if (LoseBlockWithContext != null)
            return (Task)LoseBlockWithContext.Invoke(null, [ctx, target, amount, remover])!;
        return (Task)LoseBlockLegacy!.Invoke(null, [target, amount])!;
    }

    // ③ 金色卡框材质：游戏 HSV shader（res://shaders/hsv.gdshader）+ h/s/v 参数
    // （BaseLib ShaderUtils.GenerateHsv 的移植——原卡池 ShaderColor 的替代）
    private static ShaderMaterial? _frameMaterial;

    public static ShaderMaterial LightswornFrameMaterial(float h, float s, float v)
    {
        if (_frameMaterial != null) return _frameMaterial;
        Shader shader = GD.Load<Shader>("res://shaders/hsv.gdshader").Duplicate() as Shader
            ?? throw new InvalidOperationException("Failed to load HSV shader (res://shaders/hsv.gdshader).");
        ShaderMaterial material = new() { Shader = shader };
        material.SetShaderParameter("h", h);
        material.SetShaderParameter("s", s);
        material.SetShaderParameter("v", v);
        _frameMaterial = material;
        return material;
    }
}
