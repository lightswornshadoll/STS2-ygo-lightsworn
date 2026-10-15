using System.Reflection;
using Godot;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Commands.Builders;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;

namespace Lightsworn;

// ============ 跨游戏版本兼容层（v0.5.0：0.107.1 正式版 ↔ 0.111.0 beta 同一份 dll） ============
// 以下热修复在 0.107.1 → 0.111.0 之间被游戏改掉签名/新增，且旧签名直接删除——静态绑定任一版本都会在
// 另一版本抛 MissingMethodException（"编译过、正式版炸"）。这里统一用"反射探测+调用"的兼容入口
//（MethodInfo 缓存，只在卡牌结算时调用，开销可忽略）。
// ⚠ 新增代码引用游戏 API 前先对着 0.107 试编译（见手册 §4「API 兼容试编译」）：csc 的声明级错误
//（如 CS0115）会抑制方法体内的绑定错误，试编译必须加 -p:LsCompatTrial=true 屏蔽已知差异再跑。
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

    // ④ CardPlay.Player：0.111 新增属性（0.107 不存在——直接调用=MissingMethodException，本批"卡牌卡在空中"根因之一）。
    // 0.107 回退 Card.Owner（语义=卡的所有者；0.111 的 Player 仅在 TheBall 等"打出后换主"的牌上有差别，
    // 本 mod 用途=联机钩子过滤"只认自己打出的牌"，两者一致）。
    private static readonly MethodInfo? CardPlayPlayerGetter = typeof(CardPlay).GetProperty("Player")?.GetGetMethod();

    public static Player CardPlayPlayer(CardPlay cardPlay)
        => CardPlayPlayerGetter != null
            ? (Player)CardPlayPlayerGetter.Invoke(cardPlay, null)!
            : cardPlay.Card.Owner;

    // ⑤ CardCmd.Exhaust：参数两端相同，但返回类型 0.107=Task / 0.111=Task<CardPileAddResult?>——
    // 签名（含返回类型）不同=编译绑 0.111、0.107 运行时报 MissingMethodException（"卡牌卡在空中"主根因）。
    // 按参数表反射取方法（两端唯一），拿 Task 直接 await。
    private static readonly MethodInfo? ExhaustMethod = typeof(CardCmd)
        .GetMethod("Exhaust", [typeof(PlayerChoiceContext), typeof(CardModel), typeof(bool), typeof(bool)]);

    public static Task ExhaustCompat(PlayerChoiceContext ctx, CardModel card, bool causedByEthereal = false, bool skipVisuals = false)
        => (Task)(ExhaustMethod
            ?? throw new MissingMethodException("CardCmd.Exhaust(PlayerChoiceContext, CardModel, bool, bool) not found"))
            .Invoke(null, [ctx, card, causedByEthereal, skipVisuals])!;
}
