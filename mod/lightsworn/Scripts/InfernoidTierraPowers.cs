using MegaCrit.Sts2.Core.CardSelection;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.Random;
using MegaCrit.Sts2.Core.ValueProps;
using STS2RitsuLib.Patching.Models;

namespace Lightsworn;

// ================= 一阶段核心：逆生命树节点数 = 动作等级 =================
// 数值只升不降：初始 1；每张新的不同名、非十进管的狱火机诅咒进入玩家消耗堆时点亮 1 个节点（上限 10）。
// 同名复制品不加；8 级回收只把牌从除外区挪回弃牌堆，不改变节点数；10 级拿玛攻击后回 1。
// 3/5/8 在节点数“正好达到”时立即触发一次（7→9 会跳过 8）；10 到达时立刻弃光玩家手牌并生成诅咒，
// 并把下一次出招标记为拿玛（PendingNaamah）；拿玛动作结算完之后才重置为 1。
public class InfernoidMaterialPower : ModPowerTemplate
{
    // 种类按玩家隔离：同一名狱火机在不同玩家手里各算一次；节点条全局共享。
    private readonly Dictionary<Player, HashSet<string>> _namesByPlayer = new();
    private bool _threshold3;
    private bool _threshold5;
    private bool _threshold8;
    private bool _pendingNaamah;
    private bool _fusionCompleteTriggered;
    private bool _batching;
    private bool _checking;

    public int Material => Amount;

    public bool PendingNaamah => _pendingNaamah;

    private int PlayerCount => Math.Max(1, Owner.CombatState?.Players.Count ?? 1);

    public int MaxNodes => 10 * PlayerCount;

    /// <summary>动作等级=节点数按玩家数折算回 1-10（3人初始3节点=1级，9节点=3级）。</summary>
    public int ActionLevel => Math.Clamp((Material + PlayerCount - 1) / PlayerCount, 1, 10);

    public override LocString Description
    {
        get
        {
            LocString text = base.Description;
            int players = PlayerCount;
            text.Add("T3", 3 * players);
            text.Add("T5", 5 * players);
            text.Add("T8", 8 * players);
            text.Add("T10", 10 * players);
            text.Add("Base", players);
            text.Add("Max", 10 * players);
            return text;
        }
    }

    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;

    public override PowerAssetProfile AssetProfile => new(
        IconPath: "res://lightsworn/images/powers/infernoidmaterial.png",
        BigIconPath: "res://lightsworn/images/powers/infernoidmaterial_big.png");

    public override async Task AfterCardChangedPiles(CardModel card, PileType oldPileType, AbstractModel? clonedBy)
    {
        if (_pendingNaamah) return;
        if (card is not InfernoidCurseCard curse) return;
        if (curse.Level <= 1) return;
        if (card.Pile?.Type != PileType.Exhaust || oldPileType == PileType.Exhaust) return;
        if (card.Owner?.Creature?.Side != CombatSide.Player) return;
        if (!Owner.IsAlive) return;

        Player? player = card.Owner;
        if (player == null) return;
        if (!_namesByPlayer.TryGetValue(player, out HashSet<string>? names))
        {
            names = new HashSet<string>();
            _namesByPlayer[player] = names;
        }
        if (!names.Add(curse.MaterialKey)) return;
        if (Amount >= MaxNodes)
        {
            _pendingNaamah = true;
            Flash();
            return;
        }

        SetAmount(Math.Min(MaxNodes, Amount + 1));
        Flash();
        if (!_batching)
            await CheckThresholdsAsync();
    }

    public void BeginBatch() => _batching = true;

    public async Task EndBatchAsync()
    {
        _batching = false;
        await CheckThresholdsAsync();
    }

    private async Task CheckThresholdsAsync()
    {
        if (_checking || Owner.Monster is not InfernoidTierra tierra || tierra.Phase != 1) return;
        _checking = true;
        try
        {
            PlayerChoiceContext ctx = new BlockingPlayerChoiceContext();
            int players = PlayerCount;
            if (Amount == 3 * players && !_threshold3)
            {
                _threshold3 = true;
                await TriggerFusionSeal(ctx);
            }
            if (Amount == 5 * players && !_threshold5)
            {
                _threshold5 = true;
                await TriggerGraveFill(ctx);
            }
            if (Amount == 8 * players && !_threshold8)
            {
                _threshold8 = true;
                await TriggerRecovery(ctx);
            }
            if (Amount >= 10 * players && !_fusionCompleteTriggered)
            {
                _fusionCompleteTriggered = true;
                _pendingNaamah = true;
                await TriggerFusionCompletionAsync(ctx);
            }
        }
        finally
        {
            _checking = false;
        }
    }

    // 节点数到达 10 时立刻结算：弃光每名玩家当前手牌，每弃 1 张将 1 张随机诅咒置入弃牌堆。
    // 弃置期间屏蔽诅咒触发；Boss 的下一次出招固定为拿玛，所以这里只触发“弃手牌”，不重置节点。
    private async Task TriggerFusionCompletionAsync(PlayerChoiceContext ctx)
    {
        if (Owner.CombatState == null) return;
        foreach (Player player in Owner.CombatState.Players)
        {
            if (!player.Creature.IsAlive) continue;
            List<CardModel> hand = PileType.Hand.GetPile(player).Cards.ToList();
            if (hand.Count == 0) continue;

            InfernoidCurseCard.SuppressionDepth++;
            try
            {
                await CardCmd.Discard(ctx, hand);
            }
            finally
            {
                InfernoidCurseCard.SuppressionDepth--;
            }

            Rng rng = player.RunState.Rng.CombatCardSelection;
            for (int i = 0; i < hand.Count; i++)
                await InfernoidTierraCards.AddRandomCurseToDiscard(ctx, player, rng);
        }
    }

    // 3 级：融合封印。每名光道玩家选至多 3 张本回合尚未生成的融合卡，本回合视为已生成；
    // 没有融合卡/非光道玩家获得 1 张随机狱火机诅咒（洗入抽牌堆）。
    private async Task TriggerFusionSeal(PlayerChoiceContext ctx)
    {
        if (Owner.CombatState == null) return;
        foreach (Player player in Owner.CombatState.Players)
        {
            if (!player.Creature.IsAlive) continue;
            bool hasFusionOptions = false;
            if (player.Character is LightswornCharacter && player.Creature.CombatState != null)
            {
                ICombatState combat = player.Creature.CombatState;
                List<CardModel> concepts = LsUtil.FusionCodexConcepts()
                    .Where(c => !LsUtil.IsFusionUsedForCodex(combat, player, c))
                    .ToList();
                if (concepts.Count > 0)
                {
                    hasFusionOptions = true;
                    List<CardModel> clones = new();
                    foreach (CardModel concept in concepts)
                    {
                        CardModel clone = (CardModel)concept.MutableClone();
                        clone.Owner = player;
                        clones.Add(clone);
                    }
                    CardSelectorPrefs prefs = new(
                        new LocString("card_selection", "LIGHTSWORN_TIERRA_SEAL_FUSION"),
                        0, Math.Min(3, clones.Count));
                    List<CardModel> picked = (await MultiPileCardSelect.Select(ctx, player, prefs, clones)).ToList();
                    foreach (CardModel clone in picked)
                    {
                        CardModel? concept = concepts.FirstOrDefault(c => c.Id == clone.Id);
                        if (concept == null) continue;
                        LsUtil.LockFusionGeneratedThisTurn(combat, player, concept);
                    }
                }
            }
            if (!hasFusionOptions)
                await InfernoidTierraCards.AddRandomCurseToDraw(ctx, player, Owner.Monster!.Rng);
        }
    }

    // 5 级：弃光牌堆顶 3 张；将 3 张随机狱火机诅咒直接加入弃牌堆（不触发引爆）。
    private async Task TriggerGraveFill(PlayerChoiceContext ctx)
    {
        if (Owner.CombatState == null || Owner.Monster == null) return;
        foreach (Player player in Owner.CombatState.Players)
        {
            if (!player.Creature.IsAlive) continue;
            await LsUtil.Mill(ctx, player, 3);
            for (int i = 0; i < 3; i++)
                await InfernoidTierraCards.AddRandomCurseToDiscard(ctx, player, Owner.Monster.Rng);
        }
    }

    // 8 级：玩家从除外区选至多 3 张非狱火机 + 3 张狱火机放回弃牌堆。素材数保持不变。
    private async Task TriggerRecovery(PlayerChoiceContext ctx)
    {
        if (Owner.CombatState == null) return;
        foreach (Player player in Owner.CombatState.Players)
        {
            if (!player.Creature.IsAlive) continue;
            CardPile exhaust = PileType.Exhaust.GetPile(player);
            List<CardModel> nonInfernoid = exhaust.Cards.Where(c => c is not InfernoidCurseCard).ToList();
            List<CardModel> infernoid = exhaust.Cards.Where(c => c is InfernoidCurseCard).ToList();

            if (nonInfernoid.Count > 0)
            {
                List<CardModel> picked = await LsUtil.PickSomeFromList(ctx, player, nonInfernoid,
                    "LIGHTSWORN_TIERRA_RECOVER_NONINFERNOID", 0, Math.Min(3, nonInfernoid.Count));
                foreach (CardModel card in picked)
                    await CardPileCmd.Add(card, PileType.Discard);
            }
            if (infernoid.Count > 0)
            {
                List<CardModel> picked = await LsUtil.PickSomeFromList(ctx, player, infernoid,
                    "LIGHTSWORN_TIERRA_RECOVER_INFERNOID", 0, Math.Min(3, infernoid.Count));
                foreach (CardModel card in picked)
                    await CardPileCmd.Add(card, PileType.Discard);
            }
        }
    }

    // 拿玛动作结算完之后：除外区所有狱火机诅咒回弃牌堆；节点回 1；阈值重置。
    // 10 节点的弃手牌已在到达 10 的瞬间结算（TriggerFusionCompletionAsync），这里不再重复。
    public async Task CompleteFusionAsync(PlayerChoiceContext ctx)
    {
        if (Owner.CombatState == null) return;
        foreach (Player player in Owner.CombatState.Players)
        {
            List<CardModel> exhausted = PileType.Exhaust.GetPile(player).Cards
                .Where(c => c is InfernoidCurseCard).ToList();
            foreach (CardModel card in exhausted)
                await CardPileCmd.Add(card, PileType.Discard);
        }

        _namesByPlayer.Clear();
        _threshold3 = false;
        _threshold5 = false;
        _threshold8 = false;
        _pendingNaamah = false;
        _fusionCompleteTriggered = false;
        SetAmount(PlayerCount);
        Flash();
    }
}

// ================= 二阶段核心：创星 =================
// 显示为 0 - 10×玩家数（内部 Amount=显示值+1，保证 0 时能力仍可见）。
// 每个 Boss 回合结束 +2×玩家数；阶段 2 内每名玩家每真正引爆一种新的狱火机诅咒 +1。
// 到 10×玩家数后 Boss 的下一招变为「创星·灭世」；灭世后重置 0 / 种类清空。
public class StarCreationPower : ModPowerTemplate
{
    private static readonly Dictionary<string, string> TypeNames = new()
    {
        ["InfernoidDecatron"] = "十进管",
        ["InfernoidBeelzebub"] = "别西卜",
        ["InfernoidLucifugus"] = "路西弗格",
        ["InfernoidAstaroth"] = "阿斯塔罗特",
        ["InfernoidAsmodeus"] = "阿斯蒙蒂斯",
        ["InfernoidBelphegor"] = "贝尔芬格",
        ["InfernoidBaal"] = "巴力",
        ["InfernoidAdrammelech"] = "亚得米勒",
        ["InfernoidLilith"] = "莉莉丝",
        ["InfernoidOnuncu"] = "拿玛",
    };

    // 种类按玩家隔离：同一名狱火机在不同玩家手里各算一次；创星条全局共享。
    private readonly Dictionary<Player, HashSet<string>> _typesByPlayer = new();
    private bool _skipNextTurnEnd;

    private int PlayerCount => Math.Max(1, Owner.CombatState?.Players.Count ?? 1);

    public int MaxGauge => 10 * PlayerCount;

    public int Gauge => Math.Clamp(Amount - 1, 0, MaxGauge);

    public int TriggeredTypeCount => _typesByPlayer.Values.Sum(s => s.Count);

    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;

    public override PowerAssetProfile AssetProfile => new(
        IconPath: "res://lightsworn/images/powers/starcreation.png",
        BigIconPath: "res://lightsworn/images/powers/starcreation_big.png");

    public override int DisplayAmount => Gauge;

    public override LocString Description
    {
        get
        {
            LocString text = base.Description;
            string names = TriggeredTypeCount == 0
                ? "无"
                : string.Join("、", _typesByPlayer.Values
                    .SelectMany(s => s)
                    .GroupBy(k => k)
                    .OrderBy(g => g.Key)
                    .Select(g =>
                    {
                        string name = TypeNames.TryGetValue(g.Key, out string? n) ? n : g.Key;
                        return g.Count() > 1 ? $"{name}×{g.Count()}" : name;
                    }));
            text.Add("Gauge", Gauge);
            text.Add("Max", MaxGauge);
            text.Add("Types", names);
            text.Add("TypeCount", TriggeredTypeCount);
            return text;
        }
    }

    public void SkipNextTurnEnd() => _skipNextTurnEnd = true;

    /// <summary>由诅咒引爆管线调用；只统计阶段 2 内该玩家真正引爆的新种类。</summary>
    public void OnCurseDetonated(Player player, string materialKey)
    {
        if (Owner.Monster is not InfernoidTierra tierra || tierra.Phase != 2) return;
        if (Gauge >= MaxGauge) return;
        if (!_typesByPlayer.TryGetValue(player, out HashSet<string>? types))
        {
            types = new HashSet<string>();
            _typesByPlayer[player] = types;
        }
        if (!types.Add(materialKey)) return;
        SetAmount(Math.Min(MaxGauge + 1, Amount + 1));
        Flash();
    }

    public override async Task AfterSideTurnEnd(PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        if (side != CombatSide.Enemy || !participants.Contains(Owner)) return;
        if (_skipNextTurnEnd)
        {
            _skipNextTurnEnd = false;
            return;
        }
        if (Gauge >= MaxGauge) return;
        SetAmount(Math.Min(MaxGauge + 1, Amount + 2 * PlayerCount));
        Flash();
        await Task.CompletedTask;
    }

    public void ResetGauge()
    {
        SetAmount(1);
        _typesByPlayer.Clear();
        _skipNextTurnEnd = true;
        Flash();
    }
}

// ================= 阶段门：一阶段生命打空时不死亡，转入「创星」 =================
// 仿 TestSubject 的 AdaptablePower：死亡事件照常发生，但怪物不被移出战斗、战斗不结束；
// 死亡钩子把 NextMove 换成「创星」，创星动作里重置生命并切换到二阶段。
// 该能力对玩家可见：战斗一开始就说明“一阶段死亡会进入二阶段”。
public class InfernoidTierraPhaseGatePower : ModPowerTemplate
{
    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Single;

    public override PowerAssetProfile AssetProfile => new(
        IconPath: "res://lightsworn/images/powers/tierraphasegate.png",
        BigIconPath: "res://lightsworn/images/powers/tierraphasegate_big.png");

    public override bool ShouldStopCombatFromEnding() => Owner.Monster is InfernoidTierra { Phase: 1 };

    public override bool ShouldCreatureBeRemovedFromCombatAfterDeath(Creature creature)
    {
        bool result = !(creature == Owner && Owner.Monster is InfernoidTierra { Phase: 1 });
        MegaCrit.Sts2.Core.Logging.Log.Info(
            $"[LsTierra] gate removal check creature={creature.LogName} owner={Owner.LogName} phase={PhaseOf()} result={result}");
        return result;
    }

    private int PhaseOf() => Owner.Monster is InfernoidTierra tierra ? tierra.Phase : -1;

    public override bool ShouldPowerBeRemovedAfterOwnerDeath() => false;

    public override async Task AfterDeath(PlayerChoiceContext choiceContext, Creature creature,
        bool wasRemovalPrevented, float deathAnimLength)
    {
        MegaCrit.Sts2.Core.Logging.Log.Info(
            $"[LsTierra] gate AfterDeath creature={creature.LogName} prevented={wasRemovalPrevented} phase={PhaseOf()}");
        if (wasRemovalPrevented || creature != Owner) return;
        if (Owner.Monster is InfernoidTierra { Phase: 1 } tierra)
            tierra.OnPhaseOneDefeated();
        await Task.CompletedTask;
    }
}

// ================= 延迟 debuff 基类 =================
// 由 Boss 在敌方回合施加，在下一次玩家回合触发。若在下一次玩家回合结束前未被消耗则自动移除。
public abstract class TierraDelayedPower : ModPowerTemplate
{
    protected bool Armed;

    public override PowerType Type => PowerType.Debuff;
    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task AfterPlayerTurnStartEarly(PlayerChoiceContext choiceContext, Player player)
    {
        if (player != Owner.Player) return;
        Armed = true;
        await OnPlayerTurnStart(choiceContext, player);
    }

    protected virtual Task OnPlayerTurnStart(PlayerChoiceContext choiceContext, Player player)
        => Task.CompletedTask;

    public override async Task AfterSideTurnEnd(PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        if (side != CombatSide.Player || !participants.Contains(Owner)) return;
        Armed = false;
        await PowerCmd.Remove(this);
    }
}

// 别西卜：下回合抽牌后，随机将 1 张手牌洗回抽牌堆。
public class TierraShuffleOnePower : TierraDelayedPower
{
    public override PowerAssetProfile AssetProfile => new(
        IconPath: "res://lightsworn/images/powers/tierrashuffleone.png",
        BigIconPath: "res://lightsworn/images/powers/tierrashuffleone_big.png");

    protected override async Task OnPlayerTurnStart(PlayerChoiceContext ctx, Player player)
    {
        List<CardModel> hand = PileType.Hand.GetPile(player).Cards.ToList();
        for (int i = 0; i < Math.Max(1, Amount) && hand.Count > 0; i++)
        {
            CardModel? pick = player.RunState.Rng.CombatCardSelection.NextItem(hand);
            if (pick == null) break;
            hand.Remove(pick);
            await CardPileCmd.Add(pick, PileType.Draw, CardPilePosition.Random);
        }
        await PowerCmd.Remove(this);
    }
}

// 阿斯蒙蒂斯 / 灾天：下回合抽牌后，随机弃置 1 张手牌。
public class TierraDiscardOnePower : TierraDelayedPower
{
    public override PowerAssetProfile AssetProfile => new(
        IconPath: "res://lightsworn/images/powers/tierradiscardone.png",
        BigIconPath: "res://lightsworn/images/powers/tierradiscardone_big.png");

    protected override async Task OnPlayerTurnStart(PlayerChoiceContext ctx, Player player)
    {
        List<CardModel> hand = PileType.Hand.GetPile(player).Cards.ToList();
        for (int i = 0; i < Math.Max(1, Amount) && hand.Count > 0; i++)
        {
            CardModel? pick = player.RunState.Rng.CombatCardSelection.NextItem(hand);
            if (pick == null) break;
            hand.Remove(pick);
            await CardCmd.Discard(ctx, pick);
        }
        await PowerCmd.Remove(this);
    }
}

// 贝尔芬格 / 洪水：下 1 张融合卡无效（费用照付、不执行效果）。
// Lv6 的诅咒引爆在玩家回合内施加，立即生效；Boss 版本在敌方回合施加，下回合生效。
public class TierraFusionNullifyPower : ModPowerTemplate
{
    public override PowerType Type => PowerType.Debuff;
    public override PowerStackType StackType => PowerStackType.Counter;

    public override PowerAssetProfile AssetProfile => new(
        IconPath: "res://lightsworn/images/powers/tierrafusionnullify.png",
        BigIconPath: "res://lightsworn/images/powers/tierrafusionnullify_big.png");

    public override int ModifyCardPlayCount(CardModel card, Creature? target, int playCount)
    {
        if (playCount <= 0 || Amount <= 0) return playCount;
        if (card.Owner?.Creature != Owner) return playCount;
        if (card is not (TearFusionToken or ShaddollToken)) return playCount;
        Flash();
        SetAmount(Amount - 1);
        if (Amount <= 0) RemoveInternal();
        return 0;
    }

    public override async Task AfterSideTurnEnd(PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        if (side != CombatSide.Player || !participants.Contains(Owner)) return;
        await PowerCmd.Remove(this);
    }
}

// 莉莉丝：下 1 张攻击卡无效。
public class TierraAttackNullifyPower : ModPowerTemplate
{
    public override PowerType Type => PowerType.Debuff;
    public override PowerStackType StackType => PowerStackType.Counter;

    public override PowerAssetProfile AssetProfile => new(
        IconPath: "res://lightsworn/images/powers/tierraattacknullify.png",
        BigIconPath: "res://lightsworn/images/powers/tierraattacknullify_big.png");

    public override int ModifyCardPlayCount(CardModel card, Creature? target, int playCount)
    {
        if (playCount <= 0 || Amount <= 0) return playCount;
        if (card.Owner?.Creature != Owner) return playCount;
        if (card.Type != CardType.Attack) return playCount;
        Flash();
        SetAmount(Amount - 1);
        if (Amount <= 0) RemoveInternal();
        return 0;
    }

    public override async Task AfterSideTurnEnd(PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        if (side != CombatSide.Player || !participants.Contains(Owner)) return;
        await PowerCmd.Remove(this);
    }
}

// 拿玛：下 1 张技能卡无效。
public class TierraSkillNullifyPower : ModPowerTemplate
{
    public override PowerType Type => PowerType.Debuff;
    public override PowerStackType StackType => PowerStackType.Counter;

    public override PowerAssetProfile AssetProfile => new(
        IconPath: "res://lightsworn/images/powers/tierraskillnullify.png",
        BigIconPath: "res://lightsworn/images/powers/tierraskillnullify_big.png");

    public override int ModifyCardPlayCount(CardModel card, Creature? target, int playCount)
    {
        if (playCount <= 0 || Amount <= 0) return playCount;
        if (card.Owner?.Creature != Owner) return playCount;
        if (card.Type != CardType.Skill) return playCount;
        Flash();
        SetAmount(Amount - 1);
        if (Amount <= 0) RemoveInternal();
        return 0;
    }

    public override async Task AfterSideTurnEnd(PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        if (side != CombatSide.Player || !participants.Contains(Owner)) return;
        await PowerCmd.Remove(this);
    }
}

// 虚梦：下 2 张攻击伤害减半。伤害修正走 0.111 六参 override + 0.107 五参 postfix 转发。
public class TierraHalfDamagePower : ModPowerTemplate
{
    public override PowerType Type => PowerType.Debuff;
    public override PowerStackType StackType => PowerStackType.Counter;

    public override PowerAssetProfile AssetProfile => new(
        IconPath: "res://lightsworn/images/powers/tierrahalfdamage.png",
        BigIconPath: "res://lightsworn/images/powers/tierrahalfdamage_big.png");

#if !LS_TRIAL_107
    public override decimal ModifyDamageMultiplicative(Creature? target, decimal amount, ValueProp props,
        Creature? dealer, CardModel? cardSource, CardPlay? cardPlay)
        => CompatModifyDamage(target, amount, props, dealer, cardSource);
#endif

    internal decimal CompatModifyDamage(Creature? target, decimal amount, ValueProp props,
        Creature? dealer, CardModel? cardSource)
    {
        if (dealer != Owner || Amount <= 0) return 1m;
        if (!props.IsPoweredAttack()) return 1m;
        if (cardSource == null || cardSource.Type != CardType.Attack) return 1m;
        return 0.5m;
    }

    public override async Task AfterCardPlayed(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        if (LsCompat.CardPlayPlayer(cardPlay) != Owner.Player) return;
        if (Amount <= 0 || cardPlay.Card.Type != CardType.Attack) return;
        await PowerCmd.Decrement(this);
    }

    public override async Task AfterSideTurnEnd(PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        if (side != CombatSide.Player || !participants.Contains(Owner)) return;
        await PowerCmd.Remove(this);
    }
}

// 0.107.x 兼容：五参 ModifyDamageMultiplicative postfix（同 HonestPowerLegacyPatch 范式）。
internal sealed class TierraHalfDamageLegacyPatch : IPatchMethod
{
    public static string PatchId => "lightsworn_tierra_half_damage_legacy_107";
    public static bool IsCritical => false;
    public static string Description => "Tierra half damage power on game 0.107.x (5-param ModifyDamageMultiplicative)";
    public static ModPatchTarget[] GetTargets() =>
    [
        new ModPatchTarget(typeof(AbstractModel), "ModifyDamageMultiplicative",
            [typeof(Creature), typeof(decimal), typeof(ValueProp), typeof(Creature), typeof(CardModel)],
            ignoreIfMissing: true),
    ];

    public static void Postfix(AbstractModel __instance, ref decimal __result, Creature? target, decimal amount,
        ValueProp props, Creature? dealer, CardModel? cardSource)
    {
        if (__instance is TierraHalfDamagePower power)
            __result = power.CompatModifyDamage(target, amount, props, dealer, cardSource);
    }
}

// 洪水：玩家下回合每除外 1 张狱火机诅咒，从弃牌堆选 1 张非狱火机消耗。
public class TierraFloodTributePower : ModPowerTemplate
{
    private bool _armed;

    public override PowerType Type => PowerType.Debuff;
    public override PowerStackType StackType => PowerStackType.Single;

    public override PowerAssetProfile AssetProfile => new(
        IconPath: "res://lightsworn/images/powers/tierraflood.png",
        BigIconPath: "res://lightsworn/images/powers/tierraflood_big.png");

    public override Task AfterPlayerTurnStartEarly(PlayerChoiceContext choiceContext, Player player)
    {
        if (player == Owner.Player)
            _armed = true;
        return Task.CompletedTask;
    }

    public override async Task AfterCardChangedPiles(CardModel card, PileType oldPileType, AbstractModel? clonedBy)
    {
        if (!_armed || card is not InfernoidCurseCard) return;
        if (card.Pile?.Type != PileType.Exhaust || oldPileType == PileType.Exhaust) return;
        Player? player = card.Owner;
        if (player == null || player.Creature != Owner) return;

        PlayerChoiceContext ctx = new BlockingPlayerChoiceContext();
        List<CardModel> candidates = PileType.Discard.GetPile(player).Cards
            .Where(c => c is not InfernoidCurseCard).ToList();
        if (candidates.Count == 0) return;
        List<CardModel> picked = await LsUtil.PickFromList(ctx, player, candidates,
            "LIGHTSWORN_TIERRA_TRIBUTE", 1);
        foreach (CardModel pick in picked)
            await LsCompat.ExhaustCompat(ctx, pick);
    }

    public override async Task AfterSideTurnEnd(PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        if (side != CombatSide.Player || !participants.Contains(Owner)) return;
        _armed = false;
        await PowerCmd.Remove(this);
    }
}

// 创星·灭世：下回合只能抽 1 张牌，并失去 1 点能量。
public class TierraApocalypsePower : ModPowerTemplate
{
    public override PowerType Type => PowerType.Debuff;
    public override PowerStackType StackType => PowerStackType.Single;

    public override PowerAssetProfile AssetProfile => new(
        IconPath: "res://lightsworn/images/powers/tierraapocalypse.png",
        BigIconPath: "res://lightsworn/images/powers/tierraapocalypse_big.png");

    public override decimal ModifyHandDraw(Player player, decimal count)
    {
        if (player != Owner.Player) return count;
        return Math.Min(count, 1m);
    }

    public override async Task AfterPlayerTurnStartEarly(PlayerChoiceContext ctx, Player player)
    {
        if (player != Owner.Player) return;
        await PlayerCmd.LoseEnergy(1m, player);
        await PowerCmd.Remove(this);
    }
}
