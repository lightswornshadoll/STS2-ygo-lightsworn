using MegaCrit.Sts2.Core.CardSelection;
using STS2RitsuLib.Combat.Powers;
using STS2RitsuLib.Patching.Models;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Commands.Builders;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.Runs;
using MegaCrit.Sts2.Core.ValueProps;

namespace Lightsworn;

// ============ 暮光：纯层数资源（v0.4.11 重做：不再"打出光道牌弃光3"）。
// 触发弃光时若抽牌堆不够弃光数量→消耗2层暮光，弃牌堆洗回抽牌堆、回复1费，补完剩余弃光 ============
public class TwilightPower : ModPowerTemplate
{
    public const int ShuffleCost = 2;

    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;
    public override PowerAssetProfile AssetProfile => new(
        IconPath: "res://lightsworn/images/powers/twilight.png",
        BigIconPath: "res://lightsworn/images/powers/twilight_big.png");

    // LsUtil.Mill 检测到"弃光数量 > 卡组剩余"时调用。弃牌堆为空则不触发（洗不回任何牌，白耗层数）。
    // 补完弃光走下面的裸循环，不再进入 Mill 判定（防递归）；Flash 是 protected，故逻辑放在本类。
    public static async Task<List<CardModel>> RefillOnMill(PlayerChoiceContext choiceContext, Player player, int remaining)
    {
        List<CardModel> extra = new();
        if (remaining <= 0) return extra;
        TwilightPower? twilight = player.Creature.Powers.OfType<TwilightPower>().FirstOrDefault();
        CardPile discard = PileType.Discard.GetPile(player);
        if (twilight == null || twilight.Amount < ShuffleCost || discard.Cards.Count == 0) return extra;

        twilight.Flash();
        await PowerCmd.ModifyAmount(choiceContext, twilight, -ShuffleCost, null, null);
        // CardPileCmd.Shuffle 的语义就是把整个弃牌堆洗进抽牌堆（米迦勒教训：这正是这里要的效果）
        await CardPileCmd.Shuffle(choiceContext, player);
        await PlayerCmd.GainEnergy(1m, player);

        CardPile draw = PileType.Draw.GetPile(player);
        for (int i = 0; i < remaining; i++)
        {
            CardModel? card = draw.Cards.FirstOrDefault();
            if (card == null) break;
            await CardPileCmd.Add(card, PileType.Discard);
            extra.Add(card);
        }
        return extra;
    }
}

// ============ 加洛斯（本批反馈：回调为初版——敲前只追加弃光；敲后追加弃光并抽其中「光道」牌数） ============
// 基础（GarothPower）：「光道」牌弃光后触发（LsUtil.Mill 卡牌重载调用 OnLightswornMilled）——追加弃光2。
// 强化（GarothPowerPlus）：追加弃光2，并抽其中「光道」牌数量的牌。
// v0.4.39 的"基础=抽牌 / 敲后=任意弃光都触发"整体作废（OnAnyMill 通知点保留但两个版本都不响应）。
public class GarothPower : ModPowerTemplate
{
    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;
    public override PowerAssetProfile AssetProfile => new(
        IconPath: "res://lightsworn/images/powers/garoth.png",
        BigIconPath: "res://lightsworn/images/powers/garoth_big.png");

    // 「光道」牌来源的弃光触发（LsUtil.Mill 卡牌重载）
    public virtual Task OnLightswornMilled(PlayerChoiceContext choiceContext, Player player)
        => Trigger(choiceContext, player);

    // 任意弃光触发（LsUtil.MillCore 每次弃光事件通知）——初版不响应（保留签名不动通知点）
    public virtual Task OnAnyMill(PlayerChoiceContext choiceContext, Player player, List<CardModel> milled)
        => Task.CompletedTask;

    // 载荷：追加弃光2。追加弃光不再触发"任意弃光"（防递归，garothAny:false），
    // 但照常计入珍妮丝/破坏之光/正义世界的弃光事件
    protected virtual async Task Trigger(PlayerChoiceContext choiceContext, Player player)
    {
        await LsUtil.MillCore(choiceContext, player, 2, garothAny: false);
    }
}

// ============ 加洛斯（强化版）：追加弃光2，并抽其中「光道」牌数量的牌 ============
public class GarothPowerPlus : GarothPower
{
    protected override async Task Trigger(PlayerChoiceContext choiceContext, Player player)
    {
        List<CardModel> milled = await LsUtil.MillCore(choiceContext, player, 2, garothAny: false);
        int draw = milled.Count(LsUtil.IsLs);
        if (draw > 0)
            await CardPileCmd.Draw(choiceContext, draw, player);
    }
}

// ============ 光道的神域：回合开始可选发动，弃1张手牌光道，从弃牌堆拿Amount张光道 ============
public class SanctuaryPower : ModPowerTemplate
{
    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;
    public override PowerAssetProfile AssetProfile => new(
        IconPath: "res://lightsworn/images/powers/sanctuary.png",
        BigIconPath: "res://lightsworn/images/powers/sanctuary_big.png");

    public override async Task AfterPlayerTurnStartEarly(PlayerChoiceContext choiceContext, Player player)
    {
        // 联机：该钩子对每个玩家的回合开始各触发一轮（含队友），只在自己回合开始生效（StampedePower 同款）
        if (player != Owner.Player) return;
        if (Amount <= 0) return;
        List<CardModel> lsInHand = PileType.Hand.GetPile(player).Cards.Where(LsUtil.IsLs).ToList();
        if (lsInHand.Count == 0) return;

        // 可选发动：选0~1张手牌中的光道牌弃置，不选则跳过
        CardSelectorPrefs prefs = new(LsUtil.Prompt("LIGHTSWORN_SANCTUARY_DISCARD"), 0, 1);
        List<CardModel> chosen = (await MultiPileCardSelect.Select(choiceContext, player, prefs, lsInHand)).ToList();
        if (chosen.Count == 0) return;
        await CardCmd.Discard(choiceContext, chosen);

        List<CardModel> ls = PileType.Discard.GetPile(player).Cards.Where(LsUtil.IsLs).ToList();
        if (ls.Count == 0) return;
        int take = Math.Min(Amount, ls.Count);
        List<CardModel> picked = await LsUtil.PickFromList(choiceContext, player, ls, "LIGHTSWORN_TO_HAND", take);
        foreach (CardModel card in picked)
            await CardPileCmd.Add(card, PileType.Hand);
    }
}

// ============ 光道祭司 珍妮丝：本回合发动过弃光时，回合结束时获得Amount点格挡，并对随机一名敌人造成Amount点伤害 ============
public class JanicePower : ModPowerTemplate
{
    private bool _milledThisTurn;

    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;
    public override PowerAssetProfile AssetProfile => new(
        IconPath: "res://lightsworn/images/powers/janice.png",
        BigIconPath: "res://lightsworn/images/powers/janice_big.png");

    // LsUtil.Mill 的 player 重载在每次弃光后对所有 JanicePower 实例调用（主会话已写好调用点，签名勿改）
    public void OnMillHappened() => _milledThisTurn = true;

    public override Task AfterPlayerTurnStartEarly(PlayerChoiceContext choiceContext, Player player)
    {
        // 联机：队友回合开始的广播会打到这里——只在自己的回合开始重置标记
        if (player != Owner.Player) return Task.CompletedTask;
        _milledThisTurn = false;
        return Task.CompletedTask;
    }

    // 回合结束做"对敌人造成伤害"的事必须用 BeforeSideTurnEnd（AbstractModel 文档明确：
    // The Bomb 等伤害型效果不能放 AfterSideTurnEnd），side/participants 判定沿用 DoomPower/TheBombPower 范式
    public override async Task BeforeSideTurnEnd(PlayerChoiceContext choiceContext, CombatSide side, IEnumerable<Creature> participants)
    {
        if (!participants.Contains(Owner) || Owner.IsDead) return;
        bool milled = _milledThisTurn;
        _milledThisTurn = false;
        if (!milled || Amount <= 0) return;

        Flash();
        await CreatureCmd.GainBlock(Owner, Amount, ValueProp.Unpowered, null);

        List<Creature> enemies = CombatState.HittableEnemies.ToList();
        if (enemies.Count == 0) return;
        Player? player = Owner.Player;
        if (player == null) return;
        Creature target = player.RunState.Rng.CombatCardSelection.NextItem(enemies);
        await CreatureCmd.Damage(choiceContext, target, Amount, ValueProp.Unpowered, Owner);
    }
}

// ============ 正义世界（本批反馈问题36重做）：每次弃光，可以将弃置的牌中的1张加入手牌 ============
// 触发=LsUtil.MillCore 每次弃光事件后通知（同珍妮丝/破坏之光，含加洛斯/暮光补完；0~1可选）；
// 订正：敲后是正义世界**自己**获得「保留」（卡面 OnUpgrade），能力本身无强化版。
// 原"每次弃牌获得活力"作废。
public class JusticeWorldPower : ModPowerTemplate
{
    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;
    public override PowerAssetProfile AssetProfile => new(
        IconPath: "res://lightsworn/images/powers/justice.png",
        BigIconPath: "res://lightsworn/images/powers/justice_big.png");

    // LsUtil.MillCore 每次弃光后对所有 JusticeWorldPower 实例调用（签名勿改）
    public async Task OnMillHappened(PlayerChoiceContext ctx, List<CardModel> milled)
    {
        if (Amount <= 0 || Owner.IsDead || milled.Count == 0) return;
        Player? player = Owner.Player;
        if (player == null || !LsUtil.HandHasSpace(player)) return;
        List<CardModel> chosen = await LsUtil.PickSomeFromList(ctx, player, milled.ToList(),
            "LIGHTSWORN_TO_HAND", 0, 1);
        foreach (CardModel card in chosen)
            await CardPileCmd.Add(card, PileType.Hand);
    }
}

// ============ 光之回弹（本批反馈问题29重做）：每当你打出「光道」牌，获得Amount点格挡 ============
// （原「光道埃癸斯盾」的能力效果整体移交——埃癸斯盾本批被改造成防护罩的先古版；原"每次弃牌→灾厄"作废）
public class LightBouncePower : ModPowerTemplate
{
    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;
    public override PowerAssetProfile AssetProfile => new(
        IconPath: "res://lightsworn/images/powers/bounce.png",
        BigIconPath: "res://lightsworn/images/powers/bounce_big.png");

    public override async Task AfterCardPlayed(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        // 联机：AfterCardPlayed 是全场广播（队友打牌也会通知）——只认自己打出的「光道」牌
        if (cardPlay.Player != Owner.Player) return;
        if (Amount <= 0) return;
        if (!cardPlay.Card.Tags.Contains(Ls.Lightsworn)) return;
        await CreatureCmd.GainBlock(Owner, Amount, ValueProp.Unpowered, null);
    }
}

// ============ 破坏之光（先古牌）：固有。每次弃光，对所有敌人施加Amount层灾厄 ============
// 触发=LsUtil.Mill player重载每次调用通知一次（一次弃光事件1次，与珍妮丝通知点同源）；
// 补完（暮光洗回）计入同一次弃光，不再单独触发。Amount=灾厄层数（基础6/升级8）。
public class LightOfDestructionPower : ModPowerTemplate
{
    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;
    public override PowerAssetProfile AssetProfile => new(
        IconPath: "res://lightsworn/images/powers/lightofdestruction.png",
        BigIconPath: "res://lightsworn/images/powers/lightofdestruction_big.png");

    // LsUtil.Mill 的 player 重载在每次弃光后调用（milled>0 时）；签名勿改
    public async Task OnMillHappened(PlayerChoiceContext ctx)
    {
        if (Amount <= 0 || Owner.IsDead) return;
        List<Creature> enemies = CombatState.HittableEnemies.ToList();
        if (enemies.Count == 0) return;
        Flash();
        // 灾厄=原版死灵法师 DoomPower；集合重载先例见原版 Deathbringer.OnPlay
        await PowerCmd.Apply<DoomPower>(ctx, enemies, Amount, Owner, null);
    }
}

// ============ 珍珠世界（珠泪）：每次发动珠泪融合，对所有敌人施加1层易伤 ============
// 触发=LsUtil.TearFusion 在每次融合成功生成后通知（签名勿改）
public class PearlWorldPower : ModPowerTemplate
{
    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;
    public override PowerAssetProfile AssetProfile => new(
        IconPath: "res://lightsworn/images/powers/pearlworld.png",
        BigIconPath: "res://lightsworn/images/powers/pearlworld_big.png");

    public async Task OnFusionHappened(PlayerChoiceContext ctx)
    {
        if (Amount <= 0 || Owner.IsDead) return;
        List<Creature> enemies = CombatState.HittableEnemies.ToList();
        if (enemies.Count == 0) return;
        Flash();
        // 问题5：易伤层数=Amount（基础1/敲后2）
        await PowerCmd.Apply<VulnerablePower>(ctx, enemies, Amount, Owner, null);
    }
}

// ============ 壹世坏·弦声（本批问题25 新卡）：回合开始时弃光Amount ============
// 弃光走能力来源的 player 重载（不触发加洛斯；珍妮丝/破坏之光/暮光的通知点照常）
public class PrimevalScreamPower : ModPowerTemplate
{
    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;
    public override PowerAssetProfile AssetProfile => new(
        IconPath: "res://lightsworn/images/powers/primevalscream.png",
        BigIconPath: "res://lightsworn/images/powers/primevalscream_big.png");

    // AfterPlayerTurnStartEarly 在抽牌之后触发（手牌已就绪），神域同款
    public override async Task AfterPlayerTurnStartEarly(PlayerChoiceContext choiceContext, Player player)
    {
        if (player != Owner.Player) return;   // 联机：只在自己的回合开始弃光
        if (Amount <= 0) return;
        await LsUtil.Mill(choiceContext, player, Amount);
    }
}

// ============ 影依的伪典（本批问题30 改能力）：回合开始时可以消耗弃牌堆2张「影依」牌发动一次影融 ============
// 0~2可选（不选=不发动）；素材消耗不触发其被弃置时效果（DiscardExhaust 模式）；产出遵守生成锁
public class ShaddollSchismPower : ModPowerTemplate
{
    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;
    public override PowerAssetProfile AssetProfile => new(
        IconPath: "res://lightsworn/images/powers/shaddollschism.png",
        BigIconPath: "res://lightsworn/images/powers/shaddollschism_big.png");

    public override async Task AfterPlayerTurnStartEarly(PlayerChoiceContext choiceContext, Player player)
    {
        if (player != Owner.Player) return;   // 联机：只在自己的回合开始影融
        if (Amount <= 0) return;
        await OnTurnStartFusion(choiceContext, player);
    }

    // v0.4.37（影融+）：强化版子类重写本方法产出强化版神影依（GarothPowerPlus 同款范式）
    public virtual Task OnTurnStartFusion(PlayerChoiceContext choiceContext, Player player)
        => LsUtil.ShaddollFusionFromPower(choiceContext, player);
}

// 影依的伪典（强化版·影融+）：升级后的伪典打出时施加——回合开始的影融产出强化版神影依
public class ShaddollSchismPowerPlus : ShaddollSchismPower
{
    public override Task OnTurnStartFusion(PlayerChoiceContext choiceContext, Player player)
        => LsUtil.ShaddollFusionFromPower(choiceContext, player, forceUpgraded: true);
}

// ============ 神我影依流世（本批反馈问题37）：回合开始时，可以从消耗堆将1张「影依」牌加入手牌（0~1可选） ============
// 卡费升级=2→1（卡面 OnUpgrade），能力本身无强化版
public class PurushaddollAeonPower : ModPowerTemplate
{
    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;
    public override PowerAssetProfile AssetProfile => new(
        IconPath: "res://lightsworn/images/powers/purushaddollaeon.png",
        BigIconPath: "res://lightsworn/images/powers/purushaddollaeon_big.png");

    // AfterPlayerTurnStartEarly 在抽牌之后触发（手牌已就绪），神域/伪典同款
    public override async Task AfterPlayerTurnStartEarly(PlayerChoiceContext choiceContext, Player player)
    {
        if (player != Owner.Player) return;   // 联机：只在自己的回合开始回收
        if (Amount <= 0) return;
        List<CardModel> candidates = PileType.Exhaust.GetPile(player).Cards.Where(LsUtil.IsShaddoll).ToList();
        if (candidates.Count == 0 || !LsUtil.HandHasSpace(player)) return;
        List<CardModel> picked = await LsUtil.PickSomeFromList(choiceContext, player, candidates,
            "LIGHTSWORN_TO_HAND", 0, 1);
        foreach (CardModel card in picked)
            await CardPileCmd.Add(card, PileType.Hand);
    }
}

// ============ 欧尼斯特：下一次攻击伤害翻倍 ============
// v0.5.0 双版本兼容：0.111 的基类虚方法带 6 参（+CardPlay?）；0.107.x 是 5 参——两者不能共存于一个
// override。方案：编译期写 6 参 override（beta 生效）；正式版由 HonestPowerLegacyPatch 对基类 5 参方法
// 打 postfix 转发到 CompatModifyDamage（见类尾）。
public class HonestPower : ModPowerTemplate
{
    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;
    public override PowerAssetProfile AssetProfile => new(
        IconPath: "res://lightsworn/images/powers/honest.png",
        BigIconPath: "res://lightsworn/images/powers/honest_big.png");

    public override decimal ModifyDamageMultiplicative(Creature? target, decimal amount, ValueProp props, Creature? dealer, CardModel? cardSource, CardPlay? cardPlay)
        => CompatModifyDamage(target, amount, props, dealer, cardSource);

    // 判定逻辑共用（供 6 参 override 与 0.107.x 的 postfix 转发）
    internal decimal CompatModifyDamage(Creature? target, decimal amount, ValueProp props, Creature? dealer, CardModel? cardSource)
    {
        if (dealer != Owner) return 1m;
        if (!props.IsPoweredAttack()) return 1m;
        if (cardSource == null) return 1m;
        return 2m;
    }

    public override Task AfterCardPlayed(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        // 联机：只认自己打出的攻击牌（队友攻击是全场广播，不过滤会白白消耗层数）
        if (cardPlay.Player != Owner.Player) return Task.CompletedTask;
        if (cardPlay.Card.Type == CardType.Attack) return PowerCmd.Decrement(this);
        return Task.CompletedTask;
    }
}

// 欧尼斯特在 0.107.x（正式版）的兼容补丁：给 AbstractModel.ModifyDamageMultiplicative(5参) 打 postfix，
// 命中 HonestPower 实例时替换返回值。0.111 上该 5 参方法不存在 → ignoreIfMissing 跳过（由 6 参 override 生效）。
internal sealed class HonestPowerLegacyPatch : IPatchMethod
{
    public static string PatchId => "lightsworn_honest_legacy_107";
    public static bool IsCritical => false;
    public static string Description => "Honest power damage doubling on game 0.107.x (5-param ModifyDamageMultiplicative)";
    public static ModPatchTarget[] GetTargets() =>
    [
        new ModPatchTarget(typeof(AbstractModel), "ModifyDamageMultiplicative",
            [typeof(Creature), typeof(decimal), typeof(ValueProp), typeof(Creature), typeof(CardModel)],
            ignoreIfMissing: true),
    ];

    public static void Postfix(AbstractModel __instance, ref decimal __result, Creature? target, decimal amount,
        ValueProp props, Creature? dealer, CardModel? cardSource)
    {
        if (__instance is HonestPower honest)
            __result = honest.CompatModifyDamage(target, amount, props, dealer, cardSource);
    }
}

// ============ 堕影的蠢动（影依）：「影依」牌被弃置时，其「被弃置时」效果触发2次（永续） ============
// 判定点=LsUtil.OnShaddollDiscarded（只查在场与否，不消耗层数）；与翼影依影文蒂的3次触发加法叠加
public class SinisterShadowGamesPower : ModPowerTemplate
{
    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;
    public override PowerAssetProfile AssetProfile => new(
        IconPath: "res://lightsworn/images/powers/sinistershadowgames.png",
        BigIconPath: "res://lightsworn/images/powers/sinistershadowgames_big.png");
}

// ============ 影牢之咒缚（影依）：每当「影依」牌被弃置，获得1层镀层（原版PlatingPower） ============
public class CurseShadowPrisonPower : ModPowerTemplate
{
    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;
    public override PowerAssetProfile AssetProfile => new(
        IconPath: "res://lightsworn/images/powers/curseshadowprison.png",
        BigIconPath: "res://lightsworn/images/powers/curseshadowprison_big.png");

    // LsUtil.OnShaddollDiscarded 在每次影依牌弃置事件后通知（签名勿改；与触发次数无关）
    public async Task OnShaddollDiscarded(PlayerChoiceContext ctx)
    {
        if (Amount <= 0 || Owner.IsDead) return;
        Flash();
        await PowerCmd.Apply<PlatingPower>(ctx, Owner, 1, Owner, null);
    }
}

// ============ 影依猎犬的"被弃置时"加成：本回合打出的下N张影依攻击卡额外触发其「被弃置时」效果 ============
// 猎犬被弃置时施加（Amount=1，强化后2）；回合结束移除（TangledPower 同款 AfterSideTurnEnd 自删）。
// 打出触发的「被弃置时」效果不与蠢动/影文蒂叠加（那是弃置事件的加成，这里是打出的额外触发）
public class ShaddollHoundPower : ModPowerTemplate
{
    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;
    public override PowerAssetProfile AssetProfile => new(
        IconPath: "res://lightsworn/images/powers/shaddollhound.png",
        BigIconPath: "res://lightsworn/images/powers/shaddollhound_big.png");

    public override async Task AfterCardPlayed(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        // 联机：只认自己打出的影依攻击卡（队友打牌是全场广播，不过滤会消耗我的层数并重复触发）
        if (cardPlay.Player != Owner.Player) return;
        if (Amount <= 0) return;
        // 问题5：影依判定走标签（卡名无影依的 ShaddollCard 子类不再算影依卡）
        if (!LsUtil.IsShaddoll(cardPlay.Card) || cardPlay.Card.Type != CardType.Attack) return;
        if (cardPlay.Card is not ShaddollCard shaddoll) return;
        Flash();
        await shaddoll.OnDiscardedEffect(choiceContext);
        await PowerCmd.Decrement(this);
    }

    public override async Task AfterSideTurnEnd(PlayerChoiceContext choiceContext, CombatSide side, IEnumerable<Creature> participants)
    {
        if (participants.Contains(Owner))
        {
            Flash();
            await PowerCmd.Remove(this);
        }
    }
}

// ============ 翼影依 影文蒂的"被弃置时"加成：接下来3次「影依」牌被弃置时效果触发2次 ============
// 无自身钩子：LsUtil.OnShaddollDiscarded 检查 Amount>0 时消耗1层（PowerCmd.Decrement）
public class WendikurhuPower : ModPowerTemplate
{
    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;
    public override PowerAssetProfile AssetProfile => new(
        IconPath: "res://lightsworn/images/powers/wendikurhu.png",
        BigIconPath: "res://lightsworn/images/powers/wendikurhu_big.png");
}

// ============ 光道暗杀者 莱登的临时力量（本批反馈：弃光到「光道」牌→本回合结束前获得2点力量） ============
// BaseLib 的临时力量包装器：应用原版 StrengthPower、回合结束时自动返还（同原版柔性药水范式）。
// 图标/文案走 BaseLib 通用临时力量资源 + 游戏本体 TEMPORARY_STRENGTH_POWER 文案；标题=卡牌名（OriginModel）。
public class LaydenTempStrengthPower : ModTemporaryAppliedPowerTemplate<Layden, StrengthPower> { }

// ============ 绊影依-神数原核（本批反馈重做）：回合开始时随机生成「影依的炎核 虚梦狱」「虚影依 神子晶」
// 「神影依·神子晶」中的一张加入手牌，其获得「消耗」；生成的是神影依→登记融合生成锁（同残响：
// 本回合不能再融合出该卡、图鉴同步置灰）。v0.5.0：基础1费、敲后=固有（卡面 OnUpgrade），能力本身无强化版 ============
public class ShaddollZefracorePower : ModPowerTemplate
{
    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;
    public override PowerAssetProfile AssetProfile => new(
        IconPath: "res://lightsworn/images/powers/zefracore.png",
        BigIconPath: "res://lightsworn/images/powers/zefracore_big.png");

    // AfterPlayerTurnStartEarly 在抽牌之后触发（手牌已就绪），流世/弦声同款
    public override async Task AfterPlayerTurnStartEarly(PlayerChoiceContext choiceContext, Player player)
    {
        if (player != Owner.Player) return;   // 联机：只在自己的回合开始随机生成
        if (Amount <= 0) return;
        await LsUtil.GenerateRandomToHand(choiceContext, player,
            [ModelDb.Card<HelshaddollHollow>(), ModelDb.Card<TohushaddollGrysta>(), ModelDb.Card<ElShaddollGrysta>()]);
    }
}

// ============ 救影依-神数纳迦（本批反馈重做）：回合开始时随机生成「圣影依 商神杖灵」「联结之影依化身」
// 「影依的伪典」中的一张加入手牌，其获得「消耗」。v0.5.0：基础1费、敲后=固有（卡面 OnUpgrade），能力本身无强化版 ============
public class ShaddollZefranagaPower : ModPowerTemplate
{
    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;
    public override PowerAssetProfile AssetProfile => new(
        IconPath: "res://lightsworn/images/powers/zefranaga.png",
        BigIconPath: "res://lightsworn/images/powers/zefranaga_big.png");

    public override async Task AfterPlayerTurnStartEarly(PlayerChoiceContext choiceContext, Player player)
    {
        if (player != Owner.Player) return;   // 联机：只在自己的回合开始随机生成
        if (Amount <= 0) return;
        await LsUtil.GenerateRandomToHand(choiceContext, player,
            [ModelDb.Card<QadshaddollKeios>(), ModelDb.Card<ReshShaddollIncarnation>(), ModelDb.Card<ShaddollSchism>()]);
    }
}

// ============ 黄昏之交衣（本批反馈追加）：被从卡组弃置时获得的"本回合"光之回弹效果——
// 本回合内打出「光道」牌获得格挡（继承 LightBouncePower.AfterCardPlayed），回合结束时自动移除。
// "本回合"=一次性临时效果：副手回合结束（AfterSideTurnEnd）就消失 ============
public class TwilightGarbPower : LightBouncePower
{
    public override PowerAssetProfile AssetProfile => new(
        IconPath: "res://lightsworn/images/powers/twilightgarb.png",
        BigIconPath: "res://lightsworn/images/powers/twilightgarb_big.png");

    public override async Task AfterSideTurnEnd(PlayerChoiceContext choiceContext, CombatSide side, IEnumerable<Creature> participants)
    {
        if (!participants.Contains(Owner)) return;
        Flash();
        await PowerCmd.Remove(this);
    }
}
