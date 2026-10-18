using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Cards;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.Random;
using MegaCrit.Sts2.Core.ValueProps;

namespace Lightsworn;

// ================= 狱火机·提耶拉的一阶段诅咒（10 只狱火机） =================
// 设计：design\提耶拉boss设计.md §4.3 / §8 规则 7-8。
// 统一规格：Curse + Curse 稀有度 + 不可打出 + showInCardLibrary:false + 不可生成。
// 被「弃置」时（手牌弃置 / 弃光 Draw→Discard）检查弃牌堆里其他狱火机数量：
//   数量 ≥ 召唤代价（Lv2-4=1、Lv5-8=2、Lv9-10=3、十进管=0）→ 随机消耗对应数量的其他狱火机，
//   触发本卡的召唤时/场上效果。**诅咒本身不消耗，留在弃牌堆**。
// 回合结束的手牌清理走 CardPileCmd.Add + AfterFlush，不经过这两个钩子，因此不触发。
public abstract class InfernoidCurseCard : LsCard
{
    protected InfernoidCurseCard()
        : base(0, CardType.Curse, CardRarity.Curse, TargetType.None, showInCardLibrary: false)
    {
    }

    /// <summary>原卡等级（1-10）。决定引爆代价；十进管为 1。</summary>
    public abstract int Level { get; }

    /// <summary>素材去重键：同名复制品不重复增加融合素材数。</summary>
    public virtual string MaterialKey => GetType().Name;

    public override IEnumerable<CardKeyword> CanonicalKeywords => [CardKeyword.Unplayable];

    public override bool CanBeGeneratedInCombat => false;

    public override int MaxUpgradeLevel => 0;

    // 不可打出：OnPlay 只作为兜底（正常不会执行）。
    protected override Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay) => Task.CompletedTask;

    protected override void OnUpgrade() { }

    /// <summary>引爆代价：Lv2-4=1，Lv5-8=2，Lv9-10=3，Lv1=0。</summary>
    public int SummonCost => Level switch
    {
        <= 1 => 0,
        <= 4 => 1,
        <= 8 => 2,
        _ => 3,
    };

    // 手牌弃置（CardCmd.Discard 把牌放进弃牌堆后才发这个钩子）。
    public override async Task AfterCardDiscarded(PlayerChoiceContext choiceContext, CardModel card)
    {
        if (card != this || card.Pile?.Type != PileType.Discard) return;
        await TryDetonate(choiceContext);
    }

    // 弃光 / 其他来源的 Draw→Discard。
    public override async Task AfterCardChangedPiles(CardModel card, PileType oldPileType, AbstractModel? clonedBy)
    {
        if (card != this || oldPileType != PileType.Draw || card.Pile?.Type != PileType.Discard) return;
        await TryDetonate(new BlockingPlayerChoiceContext());
    }

    // 10 级融合完成的「弃光手牌」不触发引爆（设计 §8 规则 13）。用计数支持多玩家同时结算。
    internal static int SuppressionDepth;

    private async Task TryDetonate(PlayerChoiceContext choiceContext)
    {
        if (SuppressionDepth > 0) return;
        if (CombatManager.Instance.IsOverOrEnding) return;
        Player? player = Owner;
        if (player?.Creature == null || player.Creature.IsDead) return;
        ICombatState? combat = player.Creature.CombatState;
        if (combat == null) return;

        // 其他狱火机（不含自身）作为召唤代价。
        List<CardModel> fuel = PileType.Discard.GetPile(player).Cards
            .Where(c => c is InfernoidCurseCard && !ReferenceEquals(c, this))
            .ToList();
        int cost = SummonCost;
        if (fuel.Count < cost) return;

        List<CardModel> paid = new();
        if (cost > 0)
        {
            List<CardModel> pool = fuel.ToList();
            for (int i = 0; i < cost && pool.Count > 0; i++)
            {
                CardModel? pick = player.RunState.Rng.CombatCardSelection.NextItem(pool);
                if (pick == null) break;
                pool.Remove(pick);
                paid.Add(pick);
            }
        }

        InfernoidMaterialPower? material = InfernoidTierra.FindMaterialPower(player);
        material?.BeginBatch();
        try
        {
            foreach (CardModel card in paid)
                await LsCompat.ExhaustCompat(choiceContext, card);
        }
        finally
        {
            if (material != null)
                await material.EndBatchAsync();
        }

        // 代价不够（理论上不会）就不触发效果。
        if (paid.Count < cost) return;

        await ExecuteEffect(choiceContext);
        InfernoidTierra.NotifyCurseDetonated(player, Level, MaterialKey);
    }

    private async Task ExecuteEffect(PlayerChoiceContext ctx)
    {
        Player player = Owner;
        int level = Level;
        if (level == 1)
        {
            // 十进管：随机复制 2-10 中一张诅咒的触发效果。
            level = player.RunState.Rng.CombatCardSelection.NextInt(2, 11);
        }

        switch (level)
        {
            case 2:
            {
                // 别西卜：将 1 张随机手牌洗回抽牌堆。
                List<CardModel> hand = PileType.Hand.GetPile(player).Cards.ToList();
                CardModel? pick = player.RunState.Rng.CombatCardSelection.NextItem(hand);
                if (pick != null)
                    await CardPileCmd.Add(pick, PileType.Draw, CardPilePosition.Random);
                break;
            }
            case 3:
                // 路西弗格：获得 2 层虚弱。
                await PowerCmd.Apply<WeakPower>(ctx, player.Creature, 2m, player.Creature, this);
                break;
            case 4:
            {
                // 阿斯塔罗特：消耗手牌中 1 张技能牌。
                List<CardModel> skills = PileType.Hand.GetPile(player).Cards
                    .Where(c => c.Type == CardType.Skill).ToList();
                CardModel? pick = player.RunState.Rng.CombatCardSelection.NextItem(skills);
                if (pick != null)
                    await LsCompat.ExhaustCompat(ctx, pick);
                break;
            }
            case 5:
            {
                // 阿斯蒙蒂斯：随机弃置 1 张手牌。
                List<CardModel> hand = PileType.Hand.GetPile(player).Cards.ToList();
                CardModel? pick = player.RunState.Rng.CombatCardSelection.NextItem(hand);
                if (pick != null)
                    await CardCmd.Discard(ctx, pick);
                break;
            }
            case 6:
                // 贝尔芬格：本回合下 1 张融合卡无效（玩家回合内触发，立即生效）。
                await PowerCmd.Apply<TierraFusionNullifyPower>(ctx, player.Creature, 1m, player.Creature, this);
                break;
            case 7:
            {
                // 巴力：消耗抽牌堆和弃牌堆各 1 张牌。
                CardModel? fromDraw = player.RunState.Rng.CombatCardSelection.NextItem(
                    PileType.Draw.GetPile(player).Cards.ToList());
                if (fromDraw != null)
                    await LsCompat.ExhaustCompat(ctx, fromDraw);
                CardModel? fromDiscard = player.RunState.Rng.CombatCardSelection.NextItem(
                    PileType.Discard.GetPile(player).Cards.ToList());
                if (fromDiscard != null)
                    await LsCompat.ExhaustCompat(ctx, fromDiscard);
                break;
            }
            case 8:
                // 亚得米勒：受到 8 点伤害两次（可格挡）。
                for (int i = 0; i < 2; i++)
                    await CreatureCmd.Damage(ctx, player.Creature, 8m,
                        ValueProp.Unpowered | ValueProp.Move, player.Creature);
                break;
            case 9:
            {
                // 莉莉丝：消耗手牌和弃牌堆中所有技能牌。
                List<CardModel> skills = PileType.Hand.GetPile(player).Cards
                    .Concat(PileType.Discard.GetPile(player).Cards)
                    .Where(c => c.Type == CardType.Skill).ToList();
                foreach (CardModel card in skills)
                {
                    if (card.Pile?.Type is not (PileType.Hand or PileType.Discard)) continue;
                    await LsCompat.ExhaustCompat(ctx, card);
                }
                break;
            }
            case 10:
            {
                // 拿玛：弃置所有手牌。连锁弃置会继续触发其他诅咒。
                List<CardModel> hand = PileType.Hand.GetPile(player).Cards.ToList();
                if (hand.Count > 0)
                    await CardCmd.Discard(ctx, hand);
                break;
            }
        }
    }
}

// ---------- 十只主卡狱火机 ----------
// 数值/效果见设计 §4.3 表；卡图来自 ygopro pics（tools\make_tierra_boss_assets.py）。

[RegisterCard(typeof(LightswornCardPool))]
public class InfernoidDecatron : InfernoidCurseCard
{
    public override int Level => 1;
}

[RegisterCard(typeof(LightswornCardPool))]
public class InfernoidBeelzebub : InfernoidCurseCard
{
    public override int Level => 2;
}

[RegisterCard(typeof(LightswornCardPool))]
public class InfernoidLucifugus : InfernoidCurseCard
{
    public override int Level => 3;
}

[RegisterCard(typeof(LightswornCardPool))]
public class InfernoidAstaroth : InfernoidCurseCard
{
    public override int Level => 4;
}

[RegisterCard(typeof(LightswornCardPool))]
public class InfernoidAsmodeus : InfernoidCurseCard
{
    public override int Level => 5;
}

[RegisterCard(typeof(LightswornCardPool))]
public class InfernoidBelphegor : InfernoidCurseCard
{
    public override int Level => 6;
}

[RegisterCard(typeof(LightswornCardPool))]
public class InfernoidBaal : InfernoidCurseCard
{
    public override int Level => 7;
}

[RegisterCard(typeof(LightswornCardPool))]
public class InfernoidAdrammelech : InfernoidCurseCard
{
    public override int Level => 8;
}

[RegisterCard(typeof(LightswornCardPool))]
public class InfernoidLilith : InfernoidCurseCard
{
    public override int Level => 9;
}

[RegisterCard(typeof(LightswornCardPool))]
public class InfernoidOnuncu : InfernoidCurseCard
{
    public override int Level => 10;
}

// ================= 战斗内生成工具 =================
internal static class InfernoidTierraCards
{
    private static readonly Type[] CurseTypes =
    [
        typeof(InfernoidDecatron), typeof(InfernoidBeelzebub), typeof(InfernoidLucifugus),
        typeof(InfernoidAstaroth), typeof(InfernoidAsmodeus), typeof(InfernoidBelphegor),
        typeof(InfernoidBaal), typeof(InfernoidAdrammelech), typeof(InfernoidLilith),
        typeof(InfernoidOnuncu),
    ];

    public static InfernoidCurseCard? CreateRandomCurse(Player player, Rng rng)
    {
        int index = rng.NextInt(CurseTypes.Length);
        CardModel canonical = CurseTypes[index] switch
        {
            Type t when t == typeof(InfernoidDecatron) => ModelDb.Card<InfernoidDecatron>(),
            Type t when t == typeof(InfernoidBeelzebub) => ModelDb.Card<InfernoidBeelzebub>(),
            Type t when t == typeof(InfernoidLucifugus) => ModelDb.Card<InfernoidLucifugus>(),
            Type t when t == typeof(InfernoidAstaroth) => ModelDb.Card<InfernoidAstaroth>(),
            Type t when t == typeof(InfernoidAsmodeus) => ModelDb.Card<InfernoidAsmodeus>(),
            Type t when t == typeof(InfernoidBelphegor) => ModelDb.Card<InfernoidBelphegor>(),
            Type t when t == typeof(InfernoidBaal) => ModelDb.Card<InfernoidBaal>(),
            Type t when t == typeof(InfernoidAdrammelech) => ModelDb.Card<InfernoidAdrammelech>(),
            Type t when t == typeof(InfernoidLilith) => ModelDb.Card<InfernoidLilith>(),
            _ => ModelDb.Card<InfernoidOnuncu>(),
        };
        return player.Creature.CombatState?.CreateCard(canonical, player) as InfernoidCurseCard;
    }

    public static async Task AddRandomCurseToDraw(PlayerChoiceContext ctx, Player player, Rng rng)
    {
        InfernoidCurseCard? card = CreateRandomCurse(player, rng);
        if (card == null) return;
        await CardPileCmd.AddGeneratedCardToCombat(card, PileType.Draw, player, CardPilePosition.Random);
    }

    public static async Task AddRandomCurseToDiscard(PlayerChoiceContext ctx, Player player, Rng rng)
    {
        InfernoidCurseCard? card = CreateRandomCurse(player, rng);
        if (card == null) return;
        await CardPileCmd.AddGeneratedCardToCombat(card, PileType.Discard, player, CardPilePosition.Bottom);
    }

    /// <summary>二阶段「邪恶」：按被除外诅咒的等级生成等量燃料到弃牌堆。</summary>
    public static async Task AddRandomCursesToDiscard(PlayerChoiceContext ctx, Player player, Rng rng, int count)
    {
        for (int i = 0; i < count; i++)
            await AddRandomCurseToDiscard(ctx, player, rng);
    }
}
