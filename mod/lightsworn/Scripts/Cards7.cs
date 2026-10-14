using MegaCrit.Sts2.Core.CardSelection;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.Rooms;
using MegaCrit.Sts2.Core.ValueProps;

namespace Lightsworn;

// ================= 影依魔法（5张） =================

// 影依融合（本批问题33：0费→1费技能：影融。
// 本批问题21：敲后效果改为"若在精英战或Boss战，素材也可以从卡组选择（限「影依」牌）"）
[RegisterCard(typeof(LightswornCardPool))]
public sealed class ShaddollFusion : ShaddollCard
{
    public override IEnumerable<CardKeyword> CanonicalKeywords => [LsKeywords.ShaddollFusion];

    public ShaddollFusion() : base(1, CardType.Skill, CardRarity.Rare, TargetType.Self) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        // 问题21：强化内容=仅精英/Boss战可从卡组选素材（含素材限「影依」牌，引擎内置）
        bool canDraw = IsUpgraded &&
            Owner.RunState.CurrentRoom?.RoomType is RoomType.Elite or RoomType.Boss;
        await LsUtil.ShaddollFusion(choiceContext, this, includeDraw: canDraw);
    }

    // 强化内容=精英/Boss战素材可以从卡组选择，无数值变化
    protected override void OnUpgrade() { }
}

// 神影依融合（1费技能：影融，且本次生成的神影依获得1次重放（打出时效果额外执行1次，
// 原版 BaseReplayCount 机制）。敲后不减费——升级效果=影融+（引擎按触发卡已升级产出强化版）。
// 本批反馈问题32：稀有度升金）
[RegisterCard(typeof(LightswornCardPool))]
public sealed class ElShaddollFusion : ShaddollCard
{
    public override IEnumerable<CardKeyword> CanonicalKeywords => [LsKeywords.ShaddollFusion];

    public ElShaddollFusion() : base(1, CardType.Skill, CardRarity.Rare, TargetType.Self) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await LsUtil.ShaddollFusion(choiceContext, this, replayCount: 1);
    }

    // 问题17：敲后不减费（升级=影融+：生成强化版神影依，由引擎自动处理）
    protected override void OnUpgrade() { }
}

// 魂影依融合（本批问题33：0费→1费技能：影融，且本次素材豁免（任意2张手牌含≥1影依→任意神影依）。消耗。敲后：移除消耗）
[RegisterCard(typeof(LightswornCardPool))]
public sealed class NepheShaddollFusion : ShaddollCard
{
    public override IEnumerable<CardKeyword> CanonicalKeywords => [LsKeywords.ShaddollFusion, CardKeyword.Exhaust];

    public NepheShaddollFusion() : base(1, CardType.Skill, CardRarity.Uncommon, TargetType.Self) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await LsUtil.ShaddollFusion(choiceContext, this, LsUtil.ShaddollFusionMode.Exempt);
    }

    protected override void OnUpgrade() => RemoveKeyword(CardKeyword.Exhaust);
}

// 炼狱的乖放（1费技能：从抽牌堆将2张类型不同的「影依」牌加入手牌，然后弃置1张手牌。
// 敲后：加入手牌的2张牌费用变为0）
// 问题5：卡名无「影依」二字，不是影依卡（不打影依标：不作影融素材、不计弃置联动）
[RegisterCard(typeof(LightswornCardPool))]
public sealed class PurgatoryRelease : ShaddollCard
{
    public PurgatoryRelease() : base(1, CardType.Skill, CardRarity.Rare, TargetType.Self) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        // 两张分两步选以保证类型不同；第一张没选到（无候选/手牌满/取消）则第二张也跳过
        CardModel? first = null;
        if (LsUtil.HandHasSpace(this))
            first = await LsUtil.PickFromDraw(choiceContext, this, LsUtil.IsShaddoll);
        if (first != null)
        {
            await CardPileCmd.Add(first, PileType.Hand);
            if (IsUpgraded)
                first.EnergyCost.SetUntilPlayed(0);

            if (LsUtil.HandHasSpace(this))
            {
                CardModel? second = await LsUtil.PickFromDraw(choiceContext, this,
                    c => LsUtil.IsShaddoll(c) && c.Type != first.Type);
                if (second != null)
                {
                    await CardPileCmd.Add(second, PileType.Hand);
                    if (IsUpgraded)
                        second.EnergyCost.SetUntilPlayed(0);
                }
            }
        }

        // 然后弃置1张手牌（手牌非空时强制选1张；弃置会触发其「被弃置时」效果）
        List<CardModel> hand = PileType.Hand.GetPile(Owner).Cards.ToList();
        if (hand.Count == 0) return;
        CardSelectorPrefs prefs = new(LsUtil.Prompt("LIGHTSWORN_TO_DISCARD"), 1, 1);
        List<CardModel> chosen = (await MultiPileCardSelect.Select(choiceContext, Owner, prefs, hand)).ToList();
        if (chosen.Count > 0)
            await CardCmd.Discard(choiceContext, chosen);
    }
}

// 心影依融合（1费技能：从神影依中选择1张加入手牌，其伤害变为0。消耗。
// 本批问题23：敲后从"选择2张"改为0费、仍选1张）
[RegisterCard(typeof(LightswornCardPool))]
public sealed class FrozenHeartShadow : ShaddollCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars => [new DynamicVar("Pick", 1m)];

    public override IEnumerable<CardKeyword> CanonicalKeywords => [CardKeyword.Exhaust];

    public FrozenHeartShadow() : base(1, CardType.Skill, CardRarity.Rare, TargetType.Self) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        for (int i = 0; i < (int)DynamicVars["Pick"].BaseValue; i++)
            await LsUtil.PickAndGenerateShaddoll(choiceContext, this, upgraded: false, zeroDamage: true);
    }

    // 问题23：敲后=费用1→0（不再加选牌张数）
    protected override void OnUpgrade() => EnergyCost.UpgradeBy(-1);
}

// ================= 影依陷阱（6张） =================

// 影依的原核（本批问题36重做：1费技能——获得8格挡。作为影融素材时，本次影融可以融合任意神影依
// （引擎按素材含原核走豁免条件）；问题31：敲后不增加数值，改为影融+（素材为强化版原核时产出强化版神影依）。
// 被弃置时的效果照旧：从弃牌堆将这张卡以外的一张影依技能卡加入手牌）
[RegisterCard(typeof(LightswornCardPool))]
public sealed class ShaddollCore : ShaddollCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars => [new BlockVar(8, ValueProp.Move)];

    public ShaddollCore() : base(1, CardType.Skill, CardRarity.Uncommon, TargetType.Self) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await CreatureCmd.GainBlock(Owner.Creature, DynamicVars.Block.BaseValue, ValueProp.Move, cardPlay);
    }

    // 被弃置时（弃光或手牌弃置）：从弃牌堆将这张卡以外的一张影依技能卡加入手牌
    protected internal override async Task OnDiscardedEffect(PlayerChoiceContext ctx)
    {
        if (!LsUtil.HandHasSpace(this)) return;
        CardModel? pick = await LsUtil.PickFromDiscard(ctx, this,
            c => LsUtil.IsShaddollSkill(c) && c != this);
        if (pick != null)
            await CardPileCmd.Add(pick, PileType.Hand);
    }

    // 问题31：敲后不增加格挡数值——升级=影融+（作为素材时产出强化版神影依，引擎读取素材升级状态）
    protected override void OnUpgrade() { }
}

// 影依的伪典（本批问题30：改为能力——获得能力「影依的伪典」：每回合开始时，可以消耗弃牌堆中的
// 2张「影依」牌发动一次影融（不触发其被弃置时效果；0~2可选=不选则不发动）。
// v0.4.37 用户口径订正：敲后费用保持1费（原 EnergyCost.UpgradeBy(-1) 降费作废），
// 升级=影融+——打出的是强化版能力 ShaddollSchismPowerPlus，回合开始的影融产出强化版神影依）
[RegisterCard(typeof(LightswornCardPool))]
public sealed class ShaddollSchism : ShaddollCard
{
    public override IEnumerable<CardKeyword> CanonicalKeywords => [LsKeywords.ShaddollFusion];

    public ShaddollSchism() : base(1, CardType.Power, CardRarity.Rare, TargetType.Self) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        if (IsUpgraded)
            await PowerCmd.Apply<ShaddollSchismPowerPlus>(choiceContext, Owner.Creature, 1, Owner.Creature, this);
        else
            await PowerCmd.Apply<ShaddollSchismPower>(choiceContext, Owner.Creature, 1, Owner.Creature, this);
    }

    // v0.4.37：敲后费用保持1费（不再降为0费）；升级=影融+（打出强化版能力，见 OnPlay）
    protected override void OnUpgrade() { }
}

// 联结之影依化身（1费技能：从弃牌堆或消耗堆将1张「影依」攻击卡加入手牌；敲后：加入手牌的影依卡费用变为0。
// 本批反馈问题3：去掉"消耗弃牌堆1张影依"的代价部分）
[RegisterCard(typeof(LightswornCardPool))]
public sealed class ReshShaddollIncarnation : ShaddollCard
{
    public ReshShaddollIncarnation() : base(1, CardType.Skill, CardRarity.Common, TargetType.Self) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        // 问题3：不再消耗弃牌堆影依，直接从弃牌堆或消耗堆拿1张影依攻击卡
        if (!LsUtil.HandHasSpace(this)) return;
        CardModel? pick = await LsUtil.PickFromPiles(choiceContext, this, LsUtil.IsShaddollAttack,
            "LIGHTSWORN_TO_HAND", PileType.Discard, PileType.Exhaust);
        if (pick == null) return;
        await CardPileCmd.Add(pick, PileType.Hand);
        // 敲后——加入手牌的影依卡费用变为0
        if (IsUpgraded)
            pick.EnergyCost.SetUntilPlayed(0);
    }

    protected override void OnUpgrade() { }
}

// 神我影依流世（本批反馈问题37：升金；改为2费能力——每回合开始时可以(0~1可选)从消耗堆将1张
// 「影依」牌加入手牌；敲后1费。原"弃1张手牌影依换格挡"的技能效果作废）
[RegisterCard(typeof(LightswornCardPool))]
public sealed class PurushaddollAeon : ShaddollCard
{
    public PurushaddollAeon() : base(2, CardType.Power, CardRarity.Rare, TargetType.Self) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await PowerCmd.Apply<PurushaddollAeonPower>(choiceContext, Owner.Creature, 1, Owner.Creature, this);
    }

    // 问题37：敲后费用2→1
    protected override void OnUpgrade() => EnergyCost.UpgradeBy(-1);
}

// 堕影的蠢动（2费能力：「影依」牌被弃置时，其「被弃置时」的效果触发2次。敲后：费用2→1）
// 问题5：卡名无「影依」二字，不是影依卡（不打影依标：不作影融素材、不计弃置联动）
[RegisterCard(typeof(LightswornCardPool))]
public sealed class SinisterShadowGames : ShaddollCard
{
    public SinisterShadowGames() : base(2, CardType.Power, CardRarity.Rare, TargetType.Self) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await PowerCmd.Apply<SinisterShadowGamesPower>(choiceContext, Owner.Creature, 1, Owner.Creature, this);
    }

    protected override void OnUpgrade() => EnergyCost.UpgradeBy(-1);
}

// 影牢之咒缚（2费能力（本批反馈问题25：1费→2费）：每当「影依」牌被弃置时，获得1层镀层。敲后：获得固有）
// 问题5：卡名无「影依」二字，不是影依卡（不打影依标：不作影融素材、自己被弃置也不计咒缚镀层）
[RegisterCard(typeof(LightswornCardPool))]
public sealed class CurseShadowPrison : ShaddollCard
{
    public CurseShadowPrison() : base(2, CardType.Power, CardRarity.Rare, TargetType.Self) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await PowerCmd.Apply<CurseShadowPrisonPower>(choiceContext, Owner.Creature, 1, Owner.Creature, this);
    }

    protected override void OnUpgrade() => AddKeyword(CardKeyword.Innate);
}
