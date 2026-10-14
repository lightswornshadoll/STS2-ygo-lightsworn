using MegaCrit.Sts2.Core.CardSelection;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.ValueProps;

namespace Lightsworn;

// ================= 珠泪哀歌族（v0.4.14 新机制：珠泪融合） =================

// 珠泪融合卡基类：被弃置时（弃光=Draw→Discard，或手牌弃置=AfterCardDiscarded）发动珠泪融合。
// 打出不触发（打出是 Hand→Discard 但不走 AfterCardDiscarded，雷光同款判定）。
public abstract class TearFusionCard : LsCard
{
    protected TearFusionCard(int baseCost, CardType type, CardRarity rarity, TargetType target)
        : base(baseCost, type, rarity, target) { }

    protected override HashSet<CardTag> CanonicalTags => [Ls.Tearlaments];

    public override IEnumerable<CardKeyword> CanonicalKeywords => [LsKeywords.TearFusion];

    public override async Task AfterCardChangedPiles(CardModel card, PileType oldPileType, AbstractModel? clonedBy)
    {
        if (card != this) return;
        if (oldPileType != PileType.Draw || card.Pile?.Type != PileType.Discard) return;
        await LsUtil.TearFusion(new BlockingPlayerChoiceContext(), this);
    }

    public override async Task AfterCardDiscarded(PlayerChoiceContext choiceContext, CardModel card)
    {
        if (card != this || card.Pile?.Type != PileType.Discard) return;
        await LsUtil.TearFusion(choiceContext, this);
    }
}

// 珠泪融合Token基类：战斗内生成（不进卡池/图鉴库）。消耗语义（本批问题35/9 订正，回到初版"离开弃牌堆时消耗"）：
// ①离开弃牌堆（回手牌/回抽牌堆）→消耗；②回到抽牌堆（无论从哪个牌堆来）→消耗；
// ③被效果直接从消耗堆加入手牌→保留。被选做珠泪融合素材"返回卡组"前已由引擎直接消耗（LsUtil.TearFusion）。
public abstract class TearFusionToken : LsCard
{
    protected TearFusionToken(int baseCost, CardType type, CardRarity rarity, TargetType target)
        : base(baseCost, type, rarity, target, showInCardLibrary: false) { }

    public override bool CanBeGeneratedInCombat => false;

    protected override HashSet<CardTag> CanonicalTags => [Ls.Tearlaments];

    public override async Task AfterCardChangedPiles(CardModel card, PileType oldPileType, AbstractModel? clonedBy)
    {
        if (card != this) return;
        PileType? now = card.Pile?.Type;
        bool leavingDiscard = oldPileType == PileType.Discard && now is PileType.Hand or PileType.Draw;
        bool toDeck = now == PileType.Draw;   // 任何来源回卡组都消耗（进消耗堆本身=离场，不在此列，防递归）
        if (leavingDiscard || toDeck)
            await CardCmd.Exhaust(new ThrowingPlayerChoiceContext(), this);
    }
}

// ================= 散卡三张 =================

// 真血公 吸血鬼（2费攻击：打18/敲后20，弃光4/6，从本次弃光的牌中选1张攻击牌0费入手。
// 本批反馈问题15：敲后伤害20——Damage 升级+2 与弃光升级+2 并行）
[RegisterCard(typeof(LightswornCardPool))]
public class TrueBloodVampire : LsCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        [new DamageVar(18, ValueProp.Move), new DynamicVar("Mill", 4m)];

    public override IEnumerable<CardKeyword> CanonicalKeywords => [LsKeywords.Mill];

    public TrueBloodVampire() : base(2, CardType.Attack, CardRarity.Uncommon, TargetType.AnyEnemy) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await DamageCmd.Attack(DynamicVars.Damage.BaseValue).FromCardCompat(this, cardPlay)
            .Targeting(cardPlay.Target!).Execute(choiceContext);
        List<CardModel> milled = await LsUtil.Mill(choiceContext, this, (int)DynamicVars["Mill"].BaseValue);
        List<CardModel> attacks = milled.Where(c => c.Type == CardType.Attack).ToList();
        if (attacks.Count == 0) return;
        CardModel? pick = await LsUtil.PickFirst(choiceContext, Owner, attacks, "LIGHTSWORN_TO_HAND");
        if (pick != null && await LsUtil.TryRecallOnMill(pick, false))
            pick.EnergyCost.SetUntilPlayed(0);
    }

    protected override void OnUpgrade()
    {
        DynamicVars.Damage.UpgradeValueBy(2);
        DynamicVars["Mill"].UpgradeValueBy(2);
    }
}

// 手札抹杀（0费技能：弃所有手牌再抽等量；消耗；敲后移除消耗）
[RegisterCard(typeof(LightswornCardPool))]
public class HandDestruction : LsCard
{
    public override IEnumerable<CardKeyword> CanonicalKeywords => [CardKeyword.Exhaust];

    public HandDestruction() : base(0, CardType.Skill, CardRarity.Uncommon, TargetType.Self) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        List<CardModel> hand = PileType.Hand.GetPile(Owner).Cards.ToList();
        // DiscardAndDraw：弃置相关钩子（珠泪融合）统一在抽牌完成后触发
        await CardCmd.DiscardAndDraw(choiceContext, hand, hand.Count);
    }

    protected override void OnUpgrade() => RemoveKeyword(CardKeyword.Exhaust);
}

// 愚蠢的埋葬（0费技能：从卡组选1张牌弃置；消耗；敲后移除消耗）
[RegisterCard(typeof(LightswornCardPool))]
public class FoolishBurial : LsCard
{
    public override IEnumerable<CardKeyword> CanonicalKeywords => [CardKeyword.Exhaust];

    public FoolishBurial() : base(0, CardType.Skill, CardRarity.Uncommon, TargetType.Self) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        List<CardModel> candidates = LsUtil.DrawPile(this).Cards.ToList();
        if (candidates.Count == 0) return;
        CardSelectorPrefs prefs = new(LsUtil.Prompt("LIGHTSWORN_TO_DISCARD"), 1, 1);
        List<CardModel> chosen = (await MultiPileCardSelect.Select(choiceContext, Owner, prefs, candidates,
            [PileType.Draw])).ToList();
        if (chosen.Count > 0)
            await LsUtil.MillSelected(choiceContext, this, chosen);
    }

    protected override void OnUpgrade() => RemoveKeyword(CardKeyword.Exhaust);
}

// ================= 珠泪哀歌族·常驻卡 =================

// 塞壬人鱼（1费攻击：打8，然后可以丢弃1张手牌攻击牌：回1费并弃光3；珠泪融合）
[RegisterCard(typeof(LightswornCardPool))]
public sealed class Suliek : TearFusionCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars => [new DamageVar(8, ValueProp.Move)];

    public Suliek() : base(1, CardType.Attack, CardRarity.Uncommon, TargetType.AnyEnemy) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await DamageCmd.Attack(DynamicVars.Damage.BaseValue).FromCardCompat(this, cardPlay)
            .Targeting(cardPlay.Target!).Execute(choiceContext);

        List<CardModel> handAttacks = PileType.Hand.GetPile(Owner).Cards
            .Where(c => c.Type == CardType.Attack).ToList();
        if (handAttacks.Count == 0) return;
        CardSelectorPrefs prefs = new(LsUtil.Prompt("LIGHTSWORN_TEAR_DISCARD_ATTACK"), 0, 1);
        List<CardModel> chosen = (await MultiPileCardSelect.Select(choiceContext, Owner, prefs, handAttacks)).ToList();
        if (chosen.Count == 0) return;
        await CardCmd.Discard(choiceContext, chosen);
        await PlayerCmd.GainEnergy(1m, Owner);
        await LsUtil.Mill(choiceContext, this, 3);
    }

    // 统一规则：珠泪融合卡的升级=融合出强化后的融合卡，自身数值不变
    protected override void OnUpgrade() { }
}

// 小美人鱼（1费攻击：打6/9，若目标意图为攻击：回1费并弃光3；珠泪融合。
// 本批反馈问题7：触发条件改为"目标意图为攻击时"，伤害6/9——注意本卡珠泪融合照旧按触发卡升级产出强化版）
[RegisterCard(typeof(LightswornCardPool))]
public sealed class Merrli : TearFusionCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars => [new DamageVar(6, ValueProp.Move)];

    public Merrli() : base(1, CardType.Attack, CardRarity.Common, TargetType.AnyEnemy) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await DamageCmd.Attack(DynamicVars.Damage.BaseValue).FromCardCompat(this, cardPlay)
            .Targeting(cardPlay.Target!).Execute(choiceContext);
        // 问题7：改为目标意图为攻击时触发特效
        if (cardPlay.Target is Creature target && (target.Monster?.IntendsToAttack ?? false))
        {
            await PlayerCmd.GainEnergy(1m, Owner);
            await LsUtil.Mill(choiceContext, this, 3);
        }
    }

    // 问题7：伤害6/9（珠泪融合的强化副产物照常：引擎按触发卡升级状态产出强化版融合卡）
    protected override void OnUpgrade() => DynamicVars.Damage.UpgradeValueBy(3);
}

// 梅洛人鱼（1费攻击：打7并获得5格挡，弃光3；珠泪融合。本批反馈问题6：伤害/格挡各+1，敲前敲后都提升
// ——升级仍为纯珠泪融合型，基础数值在两种状态下通用）
[RegisterCard(typeof(LightswornCardPool))]
public sealed class Havnis : TearFusionCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        [new DamageVar(7, ValueProp.Move), new BlockVar(5, ValueProp.Move)];

    public override IEnumerable<CardKeyword> CanonicalKeywords => [LsKeywords.TearFusion, LsKeywords.Mill];

    public Havnis() : base(1, CardType.Attack, CardRarity.Common, TargetType.AnyEnemy) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await DamageCmd.Attack(DynamicVars.Damage.BaseValue).FromCardCompat(this, cardPlay)
            .Targeting(cardPlay.Target!).Execute(choiceContext);
        await LsUtil.Mill(choiceContext, this, 3);
        await CreatureCmd.GainBlock(Owner.Creature, DynamicVars.Block.BaseValue, ValueProp.Move, cardPlay);
    }

    protected override void OnUpgrade() { }
}

// 雷诺哈特（1费攻击：打7/10，从卡组选1张珠泪攻击牌弃置；被弃置时可丢弃1张手牌珠泪攻击牌→
// 将自己加入手牌（费用变为0）并获得消耗。不含珠泪融合（不能自己融合自己），是卡雷多哈特的关键素材）
[RegisterCard(typeof(LightswornCardPool))]
public sealed class Reinohart : LsCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        [new DamageVar(7, ValueProp.Move), new DynamicVar("Dump", 1m)];

    protected override HashSet<CardTag> CanonicalTags => [Ls.Tearlaments];

    public Reinohart() : base(1, CardType.Attack, CardRarity.Uncommon, TargetType.AnyEnemy) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await DamageCmd.Attack(DynamicVars.Damage.BaseValue).FromCardCompat(this, cardPlay)
            .Targeting(cardPlay.Target!).Execute(choiceContext);
        List<CardModel> candidates = LsUtil.DrawPile(this).Cards.Where(LsUtil.IsTearAttack).ToList();
        if (candidates.Count == 0) return;
        CardSelectorPrefs prefs = new(LsUtil.Prompt("LIGHTSWORN_TEAR_DUMP"), (int)DynamicVars["Dump"].BaseValue);
        List<CardModel> chosen = (await MultiPileCardSelect.Select(choiceContext, Owner, prefs, candidates,
            [PileType.Draw])).ToList();
        if (chosen.Count > 0)
            await LsUtil.MillSelected(choiceContext, this, chosen);
    }

    protected override void OnUpgrade() => DynamicVars.Damage.UpgradeValueBy(3);

    // 被弃置时（弃光或手牌弃置）：可丢弃1张手牌中的珠泪攻击牌，若丢弃了→自己0费回手并获得消耗
    public override async Task AfterCardChangedPiles(CardModel card, PileType oldPileType, AbstractModel? clonedBy)
    {
        if (card != this) return;
        if (oldPileType != PileType.Draw || card.Pile?.Type != PileType.Discard) return;
        await SelfRecallOnDiscard();
    }

    public override async Task AfterCardDiscarded(PlayerChoiceContext choiceContext, CardModel card)
    {
        if (card != this || card.Pile?.Type != PileType.Discard) return;
        await SelfRecallOnDiscard();
    }

    private async Task SelfRecallOnDiscard()
    {
        if (this.Pile?.Type != PileType.Discard) return;   // 可能已被融合等其它效果处理
        List<CardModel> tearHand = PileType.Hand.GetPile(Owner).Cards.Where(LsUtil.IsTearAttack).ToList();
        bool discarded = false;
        if (tearHand.Count > 0)
        {
            CardSelectorPrefs prefs = new(LsUtil.Prompt("LIGHTSWORN_REINOHART_DISCARD"), 0, 1);
            List<CardModel> chosen = (await MultiPileCardSelect.Select(new BlockingPlayerChoiceContext(), Owner,
                prefs, tearHand)).ToList();
            if (chosen.Count > 0)
            {
                await CardCmd.Discard(new BlockingPlayerChoiceContext(), chosen);
                discarded = true;
            }
        }
        if (!discarded || !LsUtil.HandHasSpace(this) || this.Pile?.Type != PileType.Discard) return;
        AddKeyword(CardKeyword.Exhaust);
        EnergyCost.SetUntilPlayed(0);
        await CardPileCmd.Add(this, PileType.Hand);
    }
}

// 珍珠世界（问题5重做：基础效果=原强化版（每次珠泪融合全体1层易伤+打出时从卡组拿1张珠泪攻击牌），
// 敲后=易伤2层。问题15：去掉珠泪哀歌族标签——珍珠世界不再算珠泪卡（不计"打出珠泪卡"计数））
[RegisterCard(typeof(LightswornCardPool))]
public sealed class Perlereino : LsCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars => [new DynamicVar("Vul", 1m)];

    protected override HashSet<CardTag> CanonicalTags => [];

    public Perlereino() : base(1, CardType.Power, CardRarity.Rare, TargetType.Self) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await PowerCmd.Apply<PearlWorldPower>(choiceContext, Owner.Creature, (int)DynamicVars["Vul"].BaseValue, Owner.Creature, this);
        List<CardModel> candidates = LsUtil.DrawPile(this).Cards.Where(LsUtil.IsTearAttack).ToList();
        if (candidates.Count == 0 || !LsUtil.HandHasSpace(this)) return;
        CardModel? pick = await LsUtil.PickFirst(choiceContext, Owner, candidates, "LIGHTSWORN_TO_HAND");
        if (pick != null)
            await CardPileCmd.Add(pick, PileType.Hand);
    }

    protected override void OnUpgrade() => DynamicVars["Vul"].UpgradeValueBy(1);
}

// ================= 壹世坏（本批问题25新增2张） =================

// 壹世坏·为珠泪哀歌族奏起的哀唱（1费技能：从卡组将1张珠泪卡送去墓地（弃置钩子照常触发——
// 珠泪融合可由此发动）；给目标敌人1层易伤。敲后易伤2层。原型=YGO 74920585；不打珠泪标（同珍珠世界）。
// 本批反馈问题23：追加——被弃置时从卡组拿1张珠泪攻击牌加入手牌）
[RegisterCard(typeof(LightswornCardPool))]
public sealed class PrimevalCry : LsCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars => [new DynamicVar("Vul", 1m)];

    protected override HashSet<CardTag> CanonicalTags => [];

    public PrimevalCry() : base(1, CardType.Skill, CardRarity.Uncommon, TargetType.AnyEnemy) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        // 从卡组选1张珠泪卡弃置（走 MillSelected：Draw→Discard 触发被弃置时管线，珠泪融合可由此发动）
        List<CardModel> candidates = LsUtil.DrawPile(this).Cards.Where(LsUtil.IsTear).ToList();
        if (candidates.Count > 0)
        {
            CardSelectorPrefs prefs = new(LsUtil.Prompt("LIGHTSWORN_TO_MILL"), 1, 1);
            List<CardModel> chosen = (await MultiPileCardSelect.Select(choiceContext, Owner, prefs, candidates,
                [PileType.Draw])).ToList();
            if (chosen.Count > 0)
                await LsUtil.MillSelected(choiceContext, this, chosen);
        }
        if (cardPlay.Target != null)
            await PowerCmd.Apply<VulnerablePower>(choiceContext, cardPlay.Target,
                (int)DynamicVars["Vul"].BaseValue, Owner.Creature, this);
    }

    // 敲后：易伤1→2层
    protected override void OnUpgrade() => DynamicVars["Vul"].UpgradeValueBy(1);

    // 问题23：被弃置时（弃光/手牌弃置）从卡组（抽牌堆）将1张珠泪攻击牌加入手牌（LsCard双钩子先例）
    public override async Task AfterCardChangedPiles(CardModel card, PileType oldPileType, AbstractModel? clonedBy)
    {
        if (card != this) return;
        if (oldPileType != PileType.Draw || card.Pile?.Type != PileType.Discard) return;
        await FetchTearAttack(new BlockingPlayerChoiceContext());
    }

    public override async Task AfterCardDiscarded(PlayerChoiceContext choiceContext, CardModel card)
    {
        if (card != this || card.Pile?.Type != PileType.Discard) return;
        await FetchTearAttack(choiceContext);
    }

    private async Task FetchTearAttack(PlayerChoiceContext ctx)
    {
        if (!LsUtil.HandHasSpace(this)) return;
        CardModel? pick = await LsUtil.PickFromDraw(ctx, this, LsUtil.IsTearAttack);
        if (pick != null)
            await CardPileCmd.Add(pick, PileType.Hand);
    }
}

// 壹世坏·向珠泪哀歌族劈斩的弦声（1费能力：每回合开始时弃光3。原型=YGO 6767771；不打珠泪标。
// 弃光走能力来源（player 重载）：不触发加洛斯，珍妮丝/破坏之光/暮光照常。
// 本批反馈问题30：敲后改为固有（Innate），不再增加弃光）
[RegisterCard(typeof(LightswornCardPool))]
public sealed class PrimevalScream : LsCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars => [new DynamicVar("Mill", 3m)];

    protected override HashSet<CardTag> CanonicalTags => [];

    public override IEnumerable<CardKeyword> CanonicalKeywords => [LsKeywords.Mill];

    public PrimevalScream() : base(1, CardType.Power, CardRarity.Uncommon, TargetType.Self) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await PowerCmd.Apply<PrimevalScreamPower>(choiceContext, Owner.Creature,
            (int)DynamicVars["Mill"].BaseValue, Owner.Creature, this);
    }

    // 问题30：敲后获得固有（弃光保持3，原"弃光3→4"作废）
    protected override void OnUpgrade() => AddKeyword(CardKeyword.Innate);
}

// 壹世坏·让珠泪哀歌族澄澈的残响（本批反馈问题38新卡：金卡2费技能——击晕目标敌人（眩晕=原版先古卡
// 「吹哨」施加的 CreatureCmd.Stun）；消耗；被弃置时从消耗堆选1张珠泪攻击牌，生成一张相同的卡加入手牌
// （原版复制范式=CardModel.CreateClone，升级状态保留）。
// 订正：拿回的是融合生成的珠泪攻击Token（水仙女人鱼等）时，登记本回合融合生成锁——
// 本回合不能再融合出对应的融合卡（与融合引擎/图鉴的"每回合每张1次"锁同源）。
// 原型=YGO 1329620；不打珠泪标）
[RegisterCard(typeof(LightswornCardPool))]
public sealed class PrimevalEcho : LsCard
{
    protected override HashSet<CardTag> CanonicalTags => [];

    public override IEnumerable<CardKeyword> CanonicalKeywords => [CardKeyword.Exhaust];

    public PrimevalEcho() : base(2, CardType.Skill, CardRarity.Rare, TargetType.AnyEnemy) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        // 击晕目标敌人（同先古卡「吹哨」：CreatureCmd.Stun）
        if (cardPlay.Target != null)
            await CreatureCmd.Stun(cardPlay.Target);
    }

    // 被弃置时（弃光/手牌弃置）从消耗堆选1张珠泪攻击卡，生成一张相同的珠泪攻击卡加入手牌
    public override async Task AfterCardChangedPiles(CardModel card, PileType oldPileType, AbstractModel? clonedBy)
    {
        if (card != this) return;
        if (oldPileType != PileType.Draw || card.Pile?.Type != PileType.Discard) return;
        await CopyTearAttackFromExhaust(new BlockingPlayerChoiceContext());
    }

    public override async Task AfterCardDiscarded(PlayerChoiceContext choiceContext, CardModel card)
    {
        if (card != this || card.Pile?.Type != PileType.Discard) return;
        await CopyTearAttackFromExhaust(choiceContext);
    }

    private async Task CopyTearAttackFromExhaust(PlayerChoiceContext ctx)
    {
        if (!LsUtil.HandHasSpace(this)) return;
        List<CardModel> candidates = LsUtil.ExhaustPile(this).Cards.Where(LsUtil.IsTearAttack).ToList();
        CardModel? pick = await LsUtil.PickFirst(ctx, Owner, candidates, "LIGHTSWORN_TO_HAND");
        if (pick == null) return;
        // CreateClone = 完全相同的副本（升级状态/关键词一并复制，原版双重施法范式）
        CardModel copy = pick.CreateClone();
        await CardPileCmd.AddGeneratedCardToCombat(copy, PileType.Hand, Owner);
        // 订正：拿回的是融合生成的珠泪攻击Token时，视同"本回合已生成"——本回合不能再融合出对应的融合卡
        // （登记融合生成锁；珠泪融合引擎与融合图鉴同步生效）
        if (copy is TearFusionToken && Owner.Creature.CombatState is { } cbt)
            LsUtil.LockFusionGeneratedThisTurn(cbt, copy);
    }
}

// ================= 珠泪融合卡（全部为战斗内Token） =================

// 水仙女人鱼（0费攻击Token：从卡组选1张珠泪卡0费入手，弃光5，打7/10）
[RegisterCard(typeof(LightswornCardPool))]
public sealed class Kitkallos : TearFusionToken
{
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        [new DamageVar(7, ValueProp.Move), new DynamicVar("Mill", 5m)];

    public override IEnumerable<CardKeyword> CanonicalKeywords => [LsKeywords.Mill];

    public Kitkallos() : base(0, CardType.Attack, CardRarity.Token, TargetType.AnyEnemy) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        List<CardModel> candidates = LsUtil.DrawPile(this).Cards.Where(LsUtil.IsTear).ToList();
        if (candidates.Count > 0 && LsUtil.HandHasSpace(this))
        {
            CardModel? pick = await LsUtil.PickFirst(choiceContext, Owner, candidates, "LIGHTSWORN_TO_HAND");
            if (pick != null)
            {
                await CardPileCmd.Add(pick, PileType.Hand);
                pick.EnergyCost.SetUntilPlayed(0);
            }
        }
        await LsUtil.Mill(choiceContext, this, (int)DynamicVars["Mill"].BaseValue);
        await DamageCmd.Attack(DynamicVars.Damage.BaseValue).FromCardCompat(this, cardPlay)
            .Targeting(cardPlay.Target!).Execute(choiceContext);
    }

    protected override void OnUpgrade() => DynamicVars.Damage.UpgradeValueBy(3);
}

// 鲁莎卡人鱼（0费攻击Token：打15/20，目标为爪牙则伤害翻倍；本批问题26：格挡改为固定5点）
[RegisterCard(typeof(LightswornCardPool))]
public sealed class Rulkallos : TearFusionToken
{
    protected override IEnumerable<DynamicVar> CanonicalVars => [new DamageVar(15, ValueProp.Move)];

    public Rulkallos() : base(0, CardType.Attack, CardRarity.Token, TargetType.AnyEnemy) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        decimal damage = DynamicVars.Damage.BaseValue;
        if (cardPlay.Target is Creature target && target.HasPower<MinionPower>())
            damage *= 2;
        await DamageCmd.Attack(damage).FromCardCompat(this, cardPlay).Targeting(cardPlay.Target!).Execute(choiceContext);
        // 问题26：格挡部分改为固定5（不再按本回合打出的珠泪卡计数）
        await CreatureCmd.GainBlock(Owner.Creature, 5, ValueProp.Move, cardPlay);
    }

    protected override void OnUpgrade() => DynamicVars.Damage.UpgradeValueBy(5);
}

// 卡雷多哈特（0费攻击Token：打15/20。本批问题27：改为"造成伤害+消耗，若此牌在消耗区，每回合开始时自动将其打出"。
// 实现=原版战士参考卡的范式：AfterAutoPrePlayPhaseEnteredEarly 钩子检查自身在消耗堆则 CardCmd.AutoPlay；
// 打出后因带消耗关键词回到消耗堆，下一回合再次自动打出（雷诺哈特融合素材条件不变））
[RegisterCard(typeof(LightswornCardPool))]
public sealed class KaleidoHeart : TearFusionToken
{
    protected override IEnumerable<DynamicVar> CanonicalVars => [new DamageVar(15, ValueProp.Move)];

    public override IEnumerable<CardKeyword> CanonicalKeywords => [CardKeyword.Exhaust];

    public KaleidoHeart() : base(0, CardType.Attack, CardRarity.Token, TargetType.AnyEnemy) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await DamageCmd.Attack(DynamicVars.Damage.BaseValue).FromCardCompat(this, cardPlay)
            .Targeting(cardPlay.Target!).Execute(choiceContext);
    }

    // 每回合开始时（自动预打出阶段，抽牌后），若此牌在消耗区则自动打出。
    // 用 Early 防二次触发（同原版参考卡：Mayhem 等自动打出效果也在该阶段消耗卡牌）
    public override async Task AfterAutoPrePlayPhaseEnteredEarly(PlayerChoiceContext choiceContext, Player player)
    {
        CardPile? pile = Pile;
        if (pile != null && pile.Type == PileType.Exhaust && player == Owner)
            await CardCmd.AutoPlay(choiceContext, this, null);
    }

    protected override void OnUpgrade() => DynamicVars.Damage.UpgradeValueBy(5);
}

// 捕食植物 犀角龙（0费攻击Token：打7/10，对目标施加1层缩小）
// 注意：不含「珠泪」字段——不是珠泪卡，不能当融合素材，也不计入"打出珠泪卡"计数
[RegisterCard(typeof(LightswornCardPool))]
public sealed class Dragostapelia : TearFusionToken
{
    protected override HashSet<CardTag> CanonicalTags => [];

    protected override IEnumerable<DynamicVar> CanonicalVars => [new DamageVar(7, ValueProp.Move)];

    public Dragostapelia() : base(0, CardType.Attack, CardRarity.Token, TargetType.AnyEnemy) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await DamageCmd.Attack(DynamicVars.Damage.BaseValue).FromCardCompat(this, cardPlay)
            .Targeting(cardPlay.Target!).Execute(choiceContext);
        if (cardPlay.Target != null)
            await PowerCmd.Apply<ShrinkPower>(choiceContext, cardPlay.Target, 1, Owner.Creature, this);
    }

    protected override void OnUpgrade() => DynamicVars.Damage.UpgradeValueBy(3);
}
