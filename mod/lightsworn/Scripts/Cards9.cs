using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.ValueProps;

namespace Lightsworn;

// ================= 暗黑界的龙神王 Boss 战斗内专属牌 =================
// 四神将（v0.6.1 已知问题3：攻击卡→诅咒卡，1费·保留，TargetType.None）：
//   打出时对自己的主人（玩家）造成伤害——牌面写"造成X点伤害"，实际结算目标固定为自己。
//   Curse 稀有度 + showInCardLibrary:false → LightswornCardPool.FilterThroughEpochs 会把它们从一切
//   "卡池来源"剔除（战斗奖励/商店/变形/事件选牌）。
// 只由 Boss 的「暗黑界的军势」/被动「暗黑界的诱惑」在战斗内生成，战斗结束随战斗状态回收。
// 打出后进弃牌堆（不消耗），因此可以被「龙神回归」吸收给 Boss 回血。
public abstract class DarkWorldAttackCard : LsCard
{
    private readonly int _damage;

    protected DarkWorldAttackCard(int damage)
        : base(1, CardType.Curse, CardRarity.Curse, TargetType.None, showInCardLibrary: false)
    {
        _damage = damage;
    }

    protected override IEnumerable<DynamicVar> CanonicalVars => [new DamageVar(_damage, ValueProp.Move)];

    public override IEnumerable<CardKeyword> CanonicalKeywords => [CardKeyword.Retain];

    public override bool CanBeGeneratedInCombat => false;

    public override int MaxUpgradeLevel => 0;

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        // 诅咒牌：伤害指向自己（吃到自己的力量/格挡/易伤等玩家侧修正）
        await DamageCmd.Attack(DynamicVars.Damage.BaseValue).FromCardCompat(this, cardPlay)
            .Targeting(Owner.Creature).Execute(choiceContext);
    }

    protected override void OnUpgrade() { }

    // 只认「从手牌被弃置」：CardCmd.Discard 在把牌放进弃牌堆后才发这个钩子；
    // 回合结束的手牌清理走 CardPileCmd.Add + AfterFlush，不发该钩子（设计 §3.1）。
    // 抽牌堆→弃牌堆的弃光也不经过这里，所以不会误触发。
    public override async Task AfterCardDiscarded(PlayerChoiceContext choiceContext, CardModel card)
    {
        if (card != this || card.Pile?.Type != PileType.Discard) return;
        await OnDiscardedFromHand(choiceContext);
    }

    protected abstract Task OnDiscardedFromHand(PlayerChoiceContext choiceContext);
}

// 暗黑界的鬼神 凯勒特：从手牌被弃置时，对自己造成12点伤害（可格挡）。
[RegisterCard(typeof(LightswornCardPool))]
public class DarkWorldKelt : DarkWorldAttackCard
{
    public DarkWorldKelt() : base(12) { }

    protected override async Task OnDiscardedFromHand(PlayerChoiceContext choiceContext)
    {
        // 5 参 dealer 重载 = 双版本都有（0.107/0.111 的 Damage(ctx,target,amount,props,cardSource,cardPlay)
        // 只有 0.111 侧完整；Unpowered 已排除力量修正，self dealer 不会改变数值）。
        await CreatureCmd.Damage(choiceContext, Owner.Creature, 12m,
            ValueProp.Unpowered | ValueProp.Move, Owner.Creature);
    }
}

// 暗黑界的斗神 拉提纳：从手牌被弃置时，龙神王获得3点力量。
[RegisterCard(typeof(LightswornCardPool))]
public class DarkWorldLatinum : DarkWorldAttackCard
{
    public DarkWorldLatinum() : base(8) { }

    protected override async Task OnDiscardedFromHand(PlayerChoiceContext choiceContext)
    {
        Creature? boss = Owner.Creature.CombatState?.Enemies
            .FirstOrDefault(c => c.Monster is DarkWorldGrapha && c.IsAlive);
        if (boss == null) return;
        await PowerCmd.Apply<StrengthPower>(choiceContext, boss, 3, Owner.Creature, this);
    }
}

// 暗黑界的军神 希尔瓦：从手牌被弃置时，随机将2张手牌洗入抽牌堆（反屯牌）。
[RegisterCard(typeof(LightswornCardPool))]
public class DarkWorldSillva : DarkWorldAttackCard
{
    public DarkWorldSillva() : base(11) { }

    protected override async Task OnDiscardedFromHand(PlayerChoiceContext choiceContext)
    {
        List<CardModel> hand = PileType.Hand.GetPile(Owner).Cards.ToList();
        for (int i = 0; i < 2 && hand.Count > 0; i++)
        {
            CardModel? pick = Owner.RunState.Rng.CombatCardSelection.NextItem(hand);
            if (pick == null) break;
            hand.Remove(pick);
            await CardPileCmd.Add(pick, PileType.Draw, CardPilePosition.Random);
        }
    }
}

// 暗黑界的武神 高尔德：从手牌被弃置时，对自己施加1层虚弱和1层易伤（人工制品可挡）。
[RegisterCard(typeof(LightswornCardPool))]
public class DarkWorldGoldd : DarkWorldAttackCard
{
    public DarkWorldGoldd() : base(11) { }

    protected override async Task OnDiscardedFromHand(PlayerChoiceContext choiceContext)
    {
        await PowerCmd.Apply<WeakPower>(choiceContext, Owner.Creature, 1, Owner.Creature, this);
        await PowerCmd.Apply<VulnerablePower>(choiceContext, Owner.Creature, 1, Owner.Creature, this);
    }
}

// 暗黑界的洗脑（状态）：0费·消耗。抽到时自动打出，获得1层「洗脑」debuff。
// 手动打出同样生效；自动打出也算打出（走 CardCmd.AutoPlay 的完整卡牌流程）。
// 洗脑 debuff 用 PowerCmd.Apply 施加（PowerType.Debuff + 可见）→ 人工制品会正常抵消。
[RegisterCard(typeof(LightswornCardPool))]
public class DarkWorldBrainwashing : LsCard
{
    private bool _autoPlaying;

    public DarkWorldBrainwashing()
        : base(0, CardType.Status, CardRarity.Status, TargetType.None, showInCardLibrary: false) { }

    public override IEnumerable<CardKeyword> CanonicalKeywords => [CardKeyword.Exhaust];

    public override bool CanBeGeneratedInCombat => false;

    public override int MaxUpgradeLevel => 0;

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        // 人工制品挡一次 debuff：显式消费 1 层并跳过施加（保证无论通用 PowerCmd.Apply 的
        // artifact 钩子在本版本/联机端表现如何，洗脑都一定被人工制品挡住；不会二次消耗）。
        ArtifactPower? artifact = Owner.Creature.Powers
            .OfType<ArtifactPower>()
            .FirstOrDefault(p => p.Amount > 0);
        if (artifact != null)
        {
            await PowerCmd.Decrement(artifact);
            return;
        }

        await PowerCmd.Apply<DarkWorldBrainwashPower>(
            choiceContext, Owner.Creature, 1, Owner.Creature, this);
    }

    protected override void OnUpgrade() { }

    public override async Task AfterCardDrawn(PlayerChoiceContext choiceContext, CardModel card, bool fromHandDraw)
    {
        if (card != this || _autoPlaying) return;
        if (Pile?.Type != PileType.Hand) return;
        _autoPlaying = true;
        try
        {
            await CardCmd.AutoPlay(new BlockingPlayerChoiceContext(), this, null);
        }
        finally
        {
            _autoPlaying = false;
        }
    }
}
