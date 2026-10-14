using MegaCrit.Sts2.Core.CardSelection;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.ValueProps;

namespace Lightsworn;

// ================= 影依本家怪兽（15张） =================

// 影依兽（2费攻击：打15/20，抽2张牌再强制弃置1张手牌（手牌为空则跳过）。
// 被弃置时：抽1张牌。本批反馈：升蓝（普通→非普通））
[RegisterCard(typeof(LightswornCardPool))]
public sealed class ShaddollBeast : ShaddollCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars => [new DamageVar(15, ValueProp.Move)];

    public ShaddollBeast() : base(2, CardType.Attack, CardRarity.Uncommon, TargetType.AnyEnemy) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await DamageCmd.Attack(DynamicVars.Damage.BaseValue).FromCardCompat(this, cardPlay)
            .Targeting(cardPlay.Target!).Execute(choiceContext);
        await CardPileCmd.Draw(choiceContext, 2, Owner);

        // 强制弃置1张手牌（手牌为空则跳过；弃置会触发其「被弃置时」效果）
        List<CardModel> hand = PileType.Hand.GetPile(Owner).Cards.ToList();
        if (hand.Count == 0) return;
        CardSelectorPrefs prefs = new(LsUtil.Prompt("LIGHTSWORN_TO_DISCARD"), 1, 1);
        List<CardModel> chosen = (await MultiPileCardSelect.Select(choiceContext, Owner, prefs, hand)).ToList();
        if (chosen.Count > 0)
            await CardCmd.Discard(choiceContext, chosen);
    }

    // 被弃置时：抽1张牌
    protected internal override async Task OnDiscardedEffect(PlayerChoiceContext ctx)
    {
        await CardPileCmd.Draw(ctx, 1, Owner);
    }

    // 问题8：15/20
    protected override void OnUpgrade() => DynamicVars.Damage.UpgradeValueBy(5);
}

// 影依龙（1费攻击：打5/7，获得5/7格挡。被弃置时：随机1名敌人获得1层易伤。
// 敲后：伤害+2、格挡+2）
[RegisterCard(typeof(LightswornCardPool))]
public sealed class ShaddollDragon : ShaddollCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        [new DamageVar(5, ValueProp.Move), new BlockVar(5, ValueProp.Move)];

    public ShaddollDragon() : base(1, CardType.Attack, CardRarity.Common, TargetType.AnyEnemy) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await DamageCmd.Attack(DynamicVars.Damage.BaseValue).FromCardCompat(this, cardPlay)
            .Targeting(cardPlay.Target!).Execute(choiceContext);
        await CreatureCmd.GainBlock(Owner.Creature, DynamicVars.Block.BaseValue, ValueProp.Move, cardPlay);
    }

    // 被弃置时：随机1名敌人获得1层易伤（RNG必须玩家侧，先例=费莉丝）
    protected internal override async Task OnDiscardedEffect(PlayerChoiceContext ctx)
    {
        List<Creature> enemies = Owner.Creature.CombatState!.HittableEnemies.ToList();
        if (enemies.Count == 0) return;
        Creature victim = Owner.RunState.Rng.CombatCardSelection.NextItem(enemies)!;
        await PowerCmd.Apply<VulnerablePower>(ctx, victim, 1, Owner.Creature, this);
    }

    protected override void OnUpgrade()
    {
        DynamicVars.Damage.UpgradeValueBy(2);
        DynamicVars.Block.UpgradeValueBy(2);
    }
}

// 影依蜥蜴（1费攻击：打8/10，对目标施加虚弱。被弃置时：从卡组选择1张影依卡丢弃。
// 本批反馈问题5：伤害改成8/10，敲后虚弱+1层（Weak 变量 1→2））
[RegisterCard(typeof(LightswornCardPool))]
public sealed class ShaddollSquamata : ShaddollCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        [new DamageVar(8, ValueProp.Move), new DynamicVar("Weak", 1m)];

    public ShaddollSquamata() : base(1, CardType.Attack, CardRarity.Common, TargetType.AnyEnemy) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await DamageCmd.Attack(DynamicVars.Damage.BaseValue).FromCardCompat(this, cardPlay)
            .Targeting(cardPlay.Target!).Execute(choiceContext);
        if (cardPlay.Target != null)
            await PowerCmd.Apply<WeakPower>(choiceContext, cardPlay.Target, (int)DynamicVars["Weak"].BaseValue, Owner.Creature, this);
    }

    // 被弃置时：从卡组选择1张影依卡丢弃（没有则跳过；被弃置时效果照常触发）
    protected internal override async Task OnDiscardedEffect(PlayerChoiceContext ctx)
    {
        List<CardModel> candidates = LsUtil.DrawPile(this).Cards.Where(LsUtil.IsShaddoll).ToList();
        if (candidates.Count == 0) return;
        CardSelectorPrefs prefs = new(LsUtil.Prompt("LIGHTSWORN_TO_DISCARD"), 1, 1);
        List<CardModel> chosen = (await MultiPileCardSelect.Select(ctx, Owner, prefs, candidates,
            [PileType.Draw])).ToList();
        if (chosen.Count > 0)
            await LsUtil.MillSelected(ctx, this, chosen);
    }

    // 问题5：伤害8/10（+2），敲后虚弱1→2层
    protected override void OnUpgrade()
    {
        DynamicVars.Damage.UpgradeValueBy(2);
        DynamicVars["Weak"].UpgradeValueBy(1);
    }
}

// 影依刺猬（1费攻击：打3。从卡组将1张影依技能卡加入手牌。
// 被弃置时：从抽牌堆将1张「影依」攻击牌加入手牌。敲后：费用1→0。问题2：稀有度改蓝色）
[RegisterCard(typeof(LightswornCardPool))]
public sealed class ShaddollHedgehog : ShaddollCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars => [new DamageVar(3, ValueProp.Move)];

    public ShaddollHedgehog() : base(1, CardType.Attack, CardRarity.Uncommon, TargetType.AnyEnemy) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await DamageCmd.Attack(DynamicVars.Damage.BaseValue).FromCardCompat(this, cardPlay)
            .Targeting(cardPlay.Target!).Execute(choiceContext);
        if (!LsUtil.HandHasSpace(this)) return;
        CardModel? pick = await LsUtil.PickFromDraw(choiceContext, this, LsUtil.IsShaddollSkill);
        if (pick != null)
            await CardPileCmd.Add(pick, PileType.Hand);
    }

    // 被弃置时：从抽牌堆将1张「影依」攻击牌加入手牌
    protected internal override async Task OnDiscardedEffect(PlayerChoiceContext ctx)
    {
        if (!LsUtil.HandHasSpace(this)) return;
        CardModel? pick = await LsUtil.PickFromDraw(ctx, this, LsUtil.IsShaddollAttack);
        if (pick != null)
            await CardPileCmd.Add(pick, PileType.Hand);
    }

    protected override void OnUpgrade() => EnergyCost.UpgradeBy(-1);
}

// 影依猎鹰（1费技能：从弃牌堆将1张影依攻击卡加入手牌，本回合其费用变为0。
// 被弃置时：获得5/7格挡。本批问题24：格挡改5/7）
[RegisterCard(typeof(LightswornCardPool))]
public sealed class ShaddollFalco : ShaddollCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars => [new BlockVar(5, ValueProp.Move)];

    public ShaddollFalco() : base(1, CardType.Skill, CardRarity.Uncommon, TargetType.Self) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        if (!LsUtil.HandHasSpace(this)) return;
        CardModel? pick = await LsUtil.PickFromDiscard(choiceContext, this, LsUtil.IsShaddollAttack);
        if (pick == null) return;
        await CardPileCmd.Add(pick, PileType.Hand);
        pick.EnergyCost.SetThisTurnOrUntilPlayed(0);
    }

    // 被弃置时：获得{Block}点格挡
    protected internal override async Task OnDiscardedEffect(PlayerChoiceContext ctx)
    {
        await CreatureCmd.GainBlock(Owner.Creature, DynamicVars.Block.BaseValue, ValueProp.Move, null);
    }

    protected override void OnUpgrade() => DynamicVars.Block.UpgradeValueBy(2);
}

// 影依猎犬（1费攻击：打8。从弃牌堆将1张影依卡加入手牌。稀有度白卡。本批反馈问题4：伤害+1 → 8/8
// （升级=Next+1，伤害不变）。
// 被弃置时：获得「猎犬」加成——本回合打出的接下来{Next}张影依攻击卡会额外触发其「被弃置时」效果
// （ShaddollHoundPower，回合结束移除））
[RegisterCard(typeof(LightswornCardPool))]
public sealed class ShaddollHound : ShaddollCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        [new DamageVar(8, ValueProp.Move), new DynamicVar("Next", 1m)];

    public ShaddollHound() : base(1, CardType.Attack, CardRarity.Common, TargetType.AnyEnemy) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await DamageCmd.Attack(DynamicVars.Damage.BaseValue).FromCardCompat(this, cardPlay)
            .Targeting(cardPlay.Target!).Execute(choiceContext);
        if (!LsUtil.HandHasSpace(this)) return;
        CardModel? pick = await LsUtil.PickFromDiscard(choiceContext, this, LsUtil.IsShaddoll);
        if (pick != null)
            await CardPileCmd.Add(pick, PileType.Hand);
    }

    // 被弃置时：施加猎犬加成能力
    protected internal override async Task OnDiscardedEffect(PlayerChoiceContext ctx)
    {
        await PowerCmd.Apply<ShaddollHoundPower>(ctx, Owner.Creature,
            (int)DynamicVars["Next"].BaseValue, Owner.Creature, this);
    }

    protected override void OnUpgrade() => DynamicVars["Next"].UpgradeValueBy(1);
}

// 影依巫女 艾莉娅儿（1费技能：获得8格挡，从消耗堆将1张影依攻击卡加入手牌。
// 本批反馈问题11：拿回来的影依卡改为可以打出但伤害为0（打出一次后恢复，ZeroDamageOnce，
// 原"本回合不能打出"的锁作废）；被弃置时：消耗至多{Max}张（基础1/敲后2），每消耗1张牌随机1名敌人获得1层虚弱，统一文本）
[RegisterCard(typeof(LightswornCardPool))]
public sealed class NaelshaddollAriel : ShaddollCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars =>
    [
        new BlockVar(8, ValueProp.Move),
        new DynamicVar("Max", 1m),
    ];

    public NaelshaddollAriel() : base(1, CardType.Skill, CardRarity.Common, TargetType.Self) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await CreatureCmd.GainBlock(Owner.Creature, DynamicVars.Block.BaseValue, ValueProp.Move, cardPlay);

        // 从消耗堆强制选1张影依攻击卡入手；问题11：可以打出但伤害变为0（打出一次后恢复）
        List<CardModel> candidates = LsUtil.ExhaustPile(this).Cards.Where(LsUtil.IsShaddollAttack).ToList();
        if (candidates.Count == 0 || !LsUtil.HandHasSpace(this)) return;
        CardModel? pick = await LsUtil.PickFirst(choiceContext, Owner, candidates, "LIGHTSWORN_TO_HAND");
        if (pick == null) return;
        await CardPileCmd.Add(pick, PileType.Hand);
        LsUtil.ZeroDamageOnce(pick);
    }

    // 被弃置时：将弃牌堆中除自身外的最多{Max}张牌消耗（0~Max可选），每消耗1张牌随机1名敌人获得1层虚弱。
    // 问题11：基础1张/敲后2张，文本与行为统一
    protected internal override async Task OnDiscardedEffect(PlayerChoiceContext ctx)
    {
        List<CardModel> candidates = LsUtil.DiscardPile(this).Cards
            .Where(c => !ReferenceEquals(c, this)).ToList();
        if (candidates.Count > 0)
        {
            List<CardModel> chosen = await LsUtil.PickSomeFromList(ctx, Owner, candidates, "LIGHTSWORN_TO_EXHAUST",
                0, (int)DynamicVars["Max"].BaseValue);
            foreach (CardModel card in chosen)
            {
                await CardCmd.Exhaust(ctx, card);
                List<Creature> enemies = Owner.Creature.CombatState!.HittableEnemies.ToList();
                if (enemies.Count == 0) return;
                Creature victim = Owner.RunState.Rng.CombatCardSelection.NextItem(enemies)!;
                await PowerCmd.Apply<WeakPower>(ctx, victim, 1, Owner.Creature, this);
            }
        }
    }

    // 问题11：敲后消耗上限1→2（格挡8保持不变）
    protected override void OnUpgrade() => DynamicVars["Max"].UpgradeValueBy(1);
}

// 蛇影依 路径灵（1费攻击：打7/10，获得1层人工制品，消耗。被弃置时：获得1层镀层。敲后：伤害+3）
// 本批订正：追加「消耗」关键词（打出后进消耗堆；被弃置时效果不受影响）
[RegisterCard(typeof(LightswornCardPool))]
public sealed class NehshaddollGenius : ShaddollCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars => [new DamageVar(7, ValueProp.Move)];

    public override IEnumerable<CardKeyword> CanonicalKeywords => [CardKeyword.Exhaust];

    public NehshaddollGenius() : base(1, CardType.Attack, CardRarity.Uncommon, TargetType.AnyEnemy) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await DamageCmd.Attack(DynamicVars.Damage.BaseValue).FromCardCompat(this, cardPlay)
            .Targeting(cardPlay.Target!).Execute(choiceContext);
        await PowerCmd.Apply<ArtifactPower>(choiceContext, Owner.Creature, 1, Owner.Creature, this);
    }

    // 被弃置时：获得1层镀层
    protected internal override async Task OnDiscardedEffect(PlayerChoiceContext ctx)
    {
        await PowerCmd.Apply<PlatingPower>(ctx, Owner.Creature, 1, Owner.Creature, this);
    }

    protected override void OnUpgrade() => DynamicVars.Damage.UpgradeValueBy(3);
}

// 圣影依 商神杖灵（本批问题32重做：1费技能——和手牌另外一张「影依」卡发动影融，融合出「神影依·拿非利」；
// 敲后=影融+（产出强化版）。被弃置时：可以丢弃1张手牌中的影依攻击牌，对其伤害数值随机攻击一名敌人。
// 仍保留"作为影融素材时可充当拿非利融合的光道位"（问题13）
[RegisterCard(typeof(LightswornCardPool))]
public sealed class QadshaddollKeios : ShaddollCard
{
    public override IEnumerable<CardKeyword> CanonicalKeywords => [LsKeywords.ShaddollFusion];

    // 融合目标预览：拿非利
    protected override IEnumerable<IHoverTip> AdditionalHoverTips =>
        HoverTipFactory.FromCardWithCardHoverTips<ElShaddollConstruct>();

    public QadshaddollKeios() : base(1, CardType.Skill, CardRarity.Uncommon, TargetType.Self) { }

    // 有另外一张手牌影依卡、且拿非利本回合未生成时才能打出
    protected override bool IsPlayable => base.IsPlayable &&
        PileType.Hand.GetPile(Owner).Cards.Any(c => !ReferenceEquals(c, this) && LsUtil.IsShaddoll(c)) &&
        (Owner.Creature.CombatState is not { } cbt || !LsUtil.IsFusionGenerated(cbt, ModelDb.Card<ElShaddollConstruct>()));
    protected override bool ShouldGlowGoldInternal => IsPlayable;

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        // 和手牌另外一张影依卡影融出拿非利（素材=本卡+所选牌；本卡以"拿非利的光道位"参与条件判定）
        List<CardModel> others = PileType.Hand.GetPile(Owner).Cards
            .Where(c => LsUtil.IsShaddoll(c) && !ReferenceEquals(c, this)).ToList();
        if (others.Count == 0) return;
        CardModel? pick = await LsUtil.PickFirst(choiceContext, Owner, others, "LIGHTSWORN_SHADDOLL_MATERIAL");
        if (pick == null) return;
        ICombatState? combat = Owner.Creature.CombatState;
        if (combat == null) return;
        CardModel concept = ModelDb.Card<ElShaddollConstruct>();
        if (!LsUtil.CanFuseInto(combat, [this, pick], concept)) return;   // 未锁定+条件满足
        await CardCmd.Discard(choiceContext, new List<CardModel> { pick });   // 素材弃置（被弃置时效果照常触发）
        await LsUtil.GenerateShaddollByConcept(choiceContext, this, concept, IsUpgraded);
    }

    // 被弃置时：可以丢弃1张手牌中的影依攻击牌（0~1可选），造成其伤害数值（随机一名敌人；RNG玩家侧）
    protected internal override async Task OnDiscardedEffect(PlayerChoiceContext ctx)
    {
        List<CardModel> handAttacks = PileType.Hand.GetPile(Owner).Cards.Where(LsUtil.IsShaddollAttack).ToList();
        if (handAttacks.Count == 0) return;
        CardSelectorPrefs prefs = new(LsUtil.Prompt("LIGHTSWORN_TO_DISCARD"), 0, 1);
        List<CardModel> chosen = (await MultiPileCardSelect.Select(ctx, Owner, prefs, handAttacks)).ToList();
        if (chosen.Count == 0) return;
        decimal dmg = chosen[0].DynamicVars.TryGetValue("Damage", out var dv) ? dv.BaseValue : 0m;
        await CardCmd.Discard(ctx, chosen);
        if (dmg <= 0) return;
        List<Creature> enemies = Owner.Creature.CombatState!.HittableEnemies.ToList();
        if (enemies.Count == 0) return;
        Creature victim = Owner.RunState.Rng.CombatCardSelection.NextItem(enemies)!;
        await CreatureCmd.Damage(ctx, victim, dmg, ValueProp.Unpowered, Owner.Creature);
    }

    // 问题32：敲后=影融+（产出强化版拿非利，生成时读取 IsUpgraded，升级为行为型）
    protected override void OnUpgrade() { }
}

// 羽影依 文蒂（1费攻击：打7/10。从卡组将1张影依攻击卡加入手牌，本回合其费用变为0，其伤害变为0（打出一次后恢复）。
// 本批反馈：被弃置效果改成和打出相同（同样给"费用0+伤害0"，原"仅加入手牌"作废）。稀有度金卡）
[RegisterCard(typeof(LightswornCardPool))]
public sealed class ReeshaddollWendi : ShaddollCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars => [new DamageVar(7, ValueProp.Move)];

    public ReeshaddollWendi() : base(1, CardType.Attack, CardRarity.Rare, TargetType.AnyEnemy) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await DamageCmd.Attack(DynamicVars.Damage.BaseValue).FromCardCompat(this, cardPlay)
            .Targeting(cardPlay.Target!).Execute(choiceContext);
        await FetchBuff(choiceContext);
    }

    // 本批：被弃置时与打出效果相同（回收影依攻击卡+本回合费用0+伤害0）
    protected internal override Task OnDiscardedEffect(PlayerChoiceContext ctx) => FetchBuff(ctx);

    private async Task FetchBuff(PlayerChoiceContext ctx)
    {
        if (!LsUtil.HandHasSpace(this)) return;
        CardModel? pick = await LsUtil.PickFromDraw(ctx, this, LsUtil.IsShaddollAttack);
        if (pick == null) return;
        await CardPileCmd.Add(pick, PileType.Hand);
        pick.EnergyCost.SetThisTurnOrUntilPlayed(0);
        LsUtil.ZeroDamageOnce(pick);
    }

    protected override void OnUpgrade() => DynamicVars.Damage.UpgradeValueBy(3);
}

// 影依的炎核 虚梦狱（2费攻击：打15/20（升级=伤害+5）；可以从卡组弃置1张影依攻击卡，若如此做，
// 对目标施加1层虚弱和易伤。订正：**被弃置时：弃光X——X=手牌中不同名「神影依」数量+1**（原固定弃光4））
[RegisterCard(typeof(LightswornCardPool))]
public sealed class HelshaddollHollow : ShaddollCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars => [new DamageVar(15, ValueProp.Move)];

    public override IEnumerable<CardKeyword> CanonicalKeywords => [LsKeywords.Mill];

    public HelshaddollHollow() : base(2, CardType.Attack, CardRarity.Uncommon, TargetType.AnyEnemy) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await DamageCmd.Attack(DynamicVars.Damage.BaseValue).FromCardCompat(this, cardPlay)
            .Targeting(cardPlay.Target!).Execute(choiceContext);

        // 可选：从卡组弃置1张影依攻击卡（被弃置时效果照常触发）
        List<CardModel> candidates = LsUtil.DrawPile(this).Cards.Where(LsUtil.IsShaddollAttack).ToList();
        if (candidates.Count == 0) return;
        CardSelectorPrefs prefs = new(LsUtil.Prompt("LIGHTSWORN_TO_DISCARD"), 0, 1);
        List<CardModel> chosen = (await MultiPileCardSelect.Select(choiceContext, Owner, prefs, candidates,
            [PileType.Draw])).ToList();
        if (chosen.Count == 0) return;
        await LsUtil.MillSelected(choiceContext, this, chosen);
        if (cardPlay.Target != null)
        {
            await PowerCmd.Apply<WeakPower>(choiceContext, cardPlay.Target, 1, Owner.Creature, this);
            await PowerCmd.Apply<VulnerablePower>(choiceContext, cardPlay.Target, 1, Owner.Creature, this);
        }
    }

    // 订正：被弃置时：弃光X（X=手牌中不同名「神影依」数量+1；原固定弃光4作废）
    protected internal override async Task OnDiscardedEffect(PlayerChoiceContext ctx)
    {
        int x = PileType.Hand.GetPile(Owner).Cards.Where(LsUtil.IsElShaddollToken)
            .Select(c => c.Id).Distinct().Count() + 1;
        await LsUtil.Mill(ctx, this, x);
    }

    protected override void OnUpgrade() => DynamicVars.Damage.UpgradeValueBy(5);
}

// 虚影依 神子晶（1费攻击：打8（本批反馈问题14：6→8）。从弃牌堆将1张影依攻击卡加入手牌，本回合其费用变为0，其伤害变为0（打出一次后恢复）。
// 被弃置时：影融——素材为弃牌堆2张「影依」牌消耗（不触发其被弃置时效果），融合1张神影依入手牌。
// 升级同时为"影融+"（生成强化版神影依；引擎按触发卡已升级自动处理））
[RegisterCard(typeof(LightswornCardPool))]
public sealed class TohushaddollGrysta : ShaddollCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars => [new DamageVar(8, ValueProp.Move)];

    public override IEnumerable<CardKeyword> CanonicalKeywords => [LsKeywords.ShaddollFusion];

    public TohushaddollGrysta() : base(1, CardType.Attack, CardRarity.Uncommon, TargetType.AnyEnemy) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await DamageCmd.Attack(DynamicVars.Damage.BaseValue).FromCardCompat(this, cardPlay)
            .Targeting(cardPlay.Target!).Execute(choiceContext);

        if (LsUtil.HandHasSpace(this))
        {
            CardModel? pick = await LsUtil.PickFromDiscard(choiceContext, this, LsUtil.IsShaddollAttack);
            if (pick != null)
            {
                await CardPileCmd.Add(pick, PileType.Hand);
                pick.EnergyCost.SetThisTurnOrUntilPlayed(0);
                LsUtil.ZeroDamageOnce(pick);
            }
        }
    }

    // 被弃置时（弃光或手牌弃置）发动影融：素材=弃牌堆2张「影依」牌消耗（引擎排除自身）。
    // 本卡升级时该影融为"影融+"（引擎按 trigger.IsUpgraded 产出强化版）
    protected internal override async Task OnDiscardedEffect(PlayerChoiceContext ctx)
    {
        await LsUtil.ShaddollFusion(ctx, this, LsUtil.ShaddollFusionMode.DiscardExhaust);
    }

    // 本批订正：敲后伤害保持6（不增加数值），升级=影融+（产出强化版，引擎自动）
    protected override void OnUpgrade() { }
}

// 影依·拿非利（1费技能：影融（问题4：0费→1费）。
// 被弃置时：若弃牌堆中其他「影依」牌不少于{Recall}张，将此牌加入手牌且费用变为0。敲后：Recall 2→1）
[RegisterCard(typeof(LightswornCardPool))]
public sealed class ShaddollConstruct : ShaddollCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars => [new DynamicVar("Recall", 2m)];

    public override IEnumerable<CardKeyword> CanonicalKeywords => [LsKeywords.ShaddollFusion];

    public ShaddollConstruct() : base(1, CardType.Skill, CardRarity.Uncommon, TargetType.Self) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await LsUtil.ShaddollFusion(choiceContext, this);
    }

    // 被弃置时：弃牌堆中其他「影依」牌不少于{Recall}张→自己回手且费用变为0
    protected internal override async Task OnDiscardedEffect(PlayerChoiceContext ctx)
    {
        if (this.Pile?.Type != PileType.Discard) return;   // 可能已被融合等其它效果处理
        int others = LsUtil.DiscardPile(this).Cards
            .Where(c => LsUtil.IsShaddoll(c) && !ReferenceEquals(c, this)).Count();
        if (others < (int)DynamicVars["Recall"].BaseValue) return;
        if (!LsUtil.HandHasSpace(this)) return;
        await CardPileCmd.Add(this, PileType.Hand);
        EnergyCost.SetUntilPlayed(0);
    }

    protected override void OnUpgrade() => DynamicVars["Recall"].UpgradeValueBy(-1);
}

// 救影依-神数纳迦（本批反馈重做：2费能力·蓝卡——回合开始时,从「圣影依 商神杖灵」「联结之影依化身」
// 「影依的伪典」中随机生成1张加入手牌，其获得「消耗」。
// v0.5.0（用户）：基础费用2→1；敲后=固有（开局起手必在，原"敲后1费"作废）。
// 订正：原「被弃置时：抽1张牌」整体删除——被弃置不再有效果（仍算「影依」弃置事件，供咒缚/蠢动等联动））
[RegisterCard(typeof(LightswornCardPool))]
public sealed class ShaddollZefranaga : ShaddollCard
{
    public ShaddollZefranaga() : base(1, CardType.Power, CardRarity.Uncommon, TargetType.Self) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await PowerCmd.Apply<ShaddollZefranagaPower>(choiceContext, Owner.Creature, 1, Owner.Creature, this);
    }

    // v0.5.0：敲后=固有
    protected override void OnUpgrade() => AddKeyword(CardKeyword.Innate);
}

// 绊影依-神数原核（本批反馈重做：2费能力·蓝卡——回合开始时，从「影依的炎核 虚梦狱」「虚影依 神子晶」
// 「神影依·神子晶」中随机生成1张加入手牌，其获得「消耗」；生成的是神影依时会占用融合生成次数
// （同残响：本回合不能再融合出该卡、图鉴置灰）。
// v0.5.0（用户）：基础费用2→1；敲后=固有（原"敲后1费"作废）。
// 订正：「被弃置时：从弃牌堆将1张影依牌置于抽牌堆顶」整体删除——被弃置不再有效果
// （仍算「影依」弃置事件，供咒缚/蠢动等联动））
[RegisterCard(typeof(LightswornCardPool))]
public sealed class ShaddollZefracore : ShaddollCard
{
    public ShaddollZefracore() : base(1, CardType.Power, CardRarity.Uncommon, TargetType.Self) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await PowerCmd.Apply<ShaddollZefracorePower>(choiceContext, Owner.Creature, 1, Owner.Creature, this);
    }

    // v0.5.0：敲后=固有
    protected override void OnUpgrade() => AddKeyword(CardKeyword.Innate);
}
