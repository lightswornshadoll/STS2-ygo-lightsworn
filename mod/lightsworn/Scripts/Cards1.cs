using MegaCrit.Sts2.Core.CardSelection;
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

// ================= 初始卡 =================

// 打击（原光刃，问题7：打Strike标签与原版打击联动；Basic稀有度不进战斗奖励）
[RegisterCard(typeof(LightswornCardPool))]
public class LightBlade : LsCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars => [new DamageVar(6, ValueProp.Move)];
    protected override HashSet<CardTag> CanonicalTags => [CardTag.Strike];

    public LightBlade() : base(1, CardType.Attack, CardRarity.Basic, TargetType.AnyEnemy) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await DamageCmd.Attack(DynamicVars.Damage.BaseValue).FromCardCompat(this, cardPlay)
            .Targeting(cardPlay.Target!).Execute(choiceContext);
    }

    protected override void OnUpgrade() => DynamicVars.Damage.UpgradeValueBy(3);
}

// 防御（原光盾，问题7：打Defend标签与原版防御联动）
[RegisterCard(typeof(LightswornCardPool))]
public class LightWard : LsCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars => [new BlockVar(5, ValueProp.Move)];
    protected override HashSet<CardTag> CanonicalTags => [CardTag.Defend];

    public LightWard() : base(1, CardType.Skill, CardRarity.Basic, TargetType.Self) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await CreatureCmd.GainBlock(Owner.Creature, DynamicVars.Block.BaseValue, ValueProp.Move, cardPlay);
    }

    protected override void OnUpgrade() => DynamicVars.Block.UpgradeValueBy(3);
}

// ================= 本家·普通 =================

// 光道猎犬 雷光（问题5：移除增益改为施加虚弱+易伤）
[RegisterCard(typeof(LightswornCardPool))]
public class Ryko : LsCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars => [new DynamicVar("Mill", 3m)];
    public override IEnumerable<CardKeyword> CanonicalKeywords => [LsKeywords.Mill];

    public Ryko() : base(1, CardType.Skill, CardRarity.Common, TargetType.AnyEnemy) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await LsUtil.Mill(choiceContext, this, (int)DynamicVars["Mill"].BaseValue);
        await PowerCmd.Apply<WeakPower>(choiceContext, cardPlay.Target!, 1, Owner.Creature, this);
        await PowerCmd.Apply<VulnerablePower>(choiceContext, cardPlay.Target!, 1, Owner.Creature, this);
    }

    // 问题9：升级改为0费
    protected override void OnUpgrade() => EnergyCost.UpgradeBy(-1);
}

// 光道圣骑士 简（本批：数值上调10/13；稀有度改基础卡——不再从战斗奖励/商店获取）
[RegisterCard(typeof(LightswornCardPool))]
public class Jain : LsCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars =>
    [
        new DamageVar(10, ValueProp.Move),
        new DynamicVar("Mill", 2m),
    ];
    public override IEnumerable<CardKeyword> CanonicalKeywords => [LsKeywords.Mill];

    public Jain() : base(1, CardType.Attack, CardRarity.Basic, TargetType.AnyEnemy) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await DamageCmd.Attack(DynamicVars.Damage.BaseValue).FromCardCompat(this, cardPlay)
            .Targeting(cardPlay.Target!).Execute(choiceContext);
        await LsUtil.Mill(choiceContext, this, (int)DynamicVars["Mill"].BaseValue);
    }

    protected override void OnUpgrade()
    {
        DynamicVars.Damage.UpgradeValueBy(3);
    }
}

// 光道魔术师 丽拉（原抽牌效果改为削减目标力量；脆弱改虚弱，稀有度调为蓝卡；
// 本批反馈问题20：敲后虚弱改2层——Weak 变量 1→2，削力量升级保留）
[RegisterCard(typeof(LightswornCardPool))]
public class Lyla : LsCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars =>
    [
        new DynamicVar("Mill", 3m),
        new DynamicVar("Debuff", 1m),
        new DynamicVar("Weak", 1m),
    ];
    public override IEnumerable<CardKeyword> CanonicalKeywords => [LsKeywords.Mill, CardKeyword.Exhaust];

    public Lyla() : base(1, CardType.Skill, CardRarity.Uncommon, TargetType.AnyEnemy) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await LsUtil.Mill(choiceContext, this, (int)DynamicVars["Mill"].BaseValue);
        Creature target = cardPlay.Target!;
        decimal debuff = DynamicVars["Debuff"].BaseValue;
        // 负数amount=减益（原版先例：Resonance/SharedFate对目标施加负数StrengthPower）
        await PowerCmd.Apply<StrengthPower>(choiceContext, target, -debuff, Owner.Creature, this);
        // 减敏捷效果改为虚弱层数（问题20：敲后2层）
        await PowerCmd.Apply<WeakPower>(choiceContext, target, (int)DynamicVars["Weak"].BaseValue, Owner.Creature, this);
    }

    protected override void OnUpgrade()
    {
        DynamicVars["Debuff"].UpgradeValueBy(1);
        DynamicVars["Weak"].UpgradeValueBy(1);
    }
}

// 光道武僧 艾琳（伤害8/11；清除格挡后仍照常造成伤害。本批反馈问题4：伤害+1 → 9/12）
[RegisterCard(typeof(LightswornCardPool))]
public class Ehren : LsCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars =>
    [
        new DamageVar(9, ValueProp.Move),
        new DynamicVar("Mill", 3m),
    ];
    public override IEnumerable<CardKeyword> CanonicalKeywords => [LsKeywords.Mill];

    public Ehren() : base(1, CardType.Attack, CardRarity.Common, TargetType.AnyEnemy) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await LsUtil.Mill(choiceContext, this, (int)DynamicVars["Mill"].BaseValue);
        Creature target = cardPlay.Target!;
        // 本批：目标有格挡时先清除其所有格挡，然后照常造成伤害
        // v0.5.0 兼容：0.111 起 LoseBlock 需要 choiceContext+remover（反射兼容层）
        if (target.Block > 0)
            await LsCompat.LoseBlockCompat(choiceContext, target, target.Block, Owner.Creature);
        await DamageCmd.Attack(DynamicVars.Damage.BaseValue).FromCardCompat(this, cardPlay)
            .Targeting(target).Execute(choiceContext);
    }

    protected override void OnUpgrade() => DynamicVars.Damage.UpgradeValueBy(3);
}

// 光道兽 沃尔夫（0费；从卡组被弃置时自动加入手牌；只有通过抽牌以外的方式入手时才能打出）
[RegisterCard(typeof(LightswornCardPool))]
public class Wulf : LsCard
{
    private bool _playable;

    protected override bool IsPlayable => _playable;
    protected override bool ShouldGlowGoldInternal => _playable;

    protected override IEnumerable<DynamicVar> CanonicalVars => [new DamageVar(12, ValueProp.Move)];

    public Wulf() : base(0, CardType.Attack, CardRarity.Common, TargetType.AnyEnemy) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await DamageCmd.Attack(DynamicVars.Damage.BaseValue).FromCardCompat(this, cardPlay)
            .Targeting(cardPlay.Target!).Execute(choiceContext);
    }

    protected override void OnUpgrade() => DynamicVars.Damage.UpgradeValueBy(4);

    public override Task AfterCardDrawn(PlayerChoiceContext choiceContext, CardModel card, bool fromHandDraw)
    {
        if (card == this) _playable = false;
        return Task.CompletedTask;
    }

    public override async Task AfterCardChangedPiles(CardModel card, PileType oldPileType, AbstractModel? clonedBy)
    {
        if (card != this) return;
        if (oldPileType == PileType.Draw && card.Pile?.Type == PileType.Discard)
        {
            if (await LsUtil.TryRecallOnMill(this, false)) _playable = true;
        }
        else if (card.Pile?.Type == PileType.Hand)
        {
            _playable = oldPileType != PileType.Draw;
        }
    }
}

// 光道之龙（小龙，问题2重做：从抽牌堆选光道弃置；被弃置（弃光或手牌弃置）时检索双龙；问题3：1费）
[RegisterCard(typeof(LightswornCardPool))]
public class LightswornDragon : LsCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars =>
    [
        new DamageVar(9, ValueProp.Move),
        new DynamicVar("Dump", 1m),
    ];

    // 问题11：卡牌停留时预览关联牌（裁决之龙/惩戒之龙）卡图
    protected override IEnumerable<IHoverTip> AdditionalHoverTips =>
        HoverTipFactory.FromCardWithCardHoverTips<JudgementDragon>()
            .Concat(HoverTipFactory.FromCardWithCardHoverTips<PunishDragon>());

    public LightswornDragon() : base(1, CardType.Attack, CardRarity.Common, TargetType.AnyEnemy) { }

    protected override bool IsPlayable => LsUtil.DiscardPile(this).Cards.Any(LsUtil.IsLs);
    protected override bool ShouldGlowGoldInternal => IsPlayable;

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        // 问题2：只从抽牌堆选（走 MillSelected，触发光道弃光钩子+加洛斯）
        List<CardModel> candidates = LsUtil.DrawPile(this).Cards.Where(LsUtil.IsLs).ToList();
        if (candidates.Count > 0)
        {
            CardSelectorPrefs prefs = new(LsUtil.Prompt("LIGHTSWORN_TO_DISCARD"), (int)DynamicVars["Dump"].BaseValue);
            List<CardModel> chosen = (await MultiPileCardSelect.Select(choiceContext, Owner, prefs, candidates,
                [PileType.Draw])).ToList();
            if (chosen.Count > 0)
                await LsUtil.MillSelected(choiceContext, this, chosen);
        }
        await DamageCmd.Attack(DynamicVars.Damage.BaseValue).FromCardCompat(this, cardPlay)
            .Targeting(cardPlay.Target!).Execute(choiceContext);
    }

    // 升级改为提高伤害（弃光数量增量删除，基础弃光数不变）
    protected override void OnUpgrade() => DynamicVars.Damage.UpgradeValueBy(4);

    // 问题2：被弃置时检索双龙——弃光（Draw→Discard）与手牌弃置（CardCmd.Discard，含窥探）都触发；
    // 打出不走 AfterCardDiscarded，不会误触发
    public override async Task AfterCardChangedPiles(CardModel card, PileType oldPileType, AbstractModel? clonedBy)
    {
        if (card != this) return;
        if (oldPileType != PileType.Draw || card.Pile?.Type != PileType.Discard) return;
        await RecallDragon();
    }

    public override async Task AfterCardDiscarded(PlayerChoiceContext choiceContext, CardModel card)
    {
        if (card != this || card.Pile?.Type != PileType.Discard) return;
        await RecallDragon();
    }

    private async Task RecallDragon()
    {
        List<CardModel> dragons = LsUtil.DrawPile(this).Cards
            .Where(c => c is JudgementDragon or PunishDragon).ToList();
        if (dragons.Count == 0 || !LsUtil.HandHasSpace(this)) return;
        CardModel? pick = await LsUtil.PickFirst(new BlockingPlayerChoiceContext(), Owner, dragons, "LIGHTSWORN_TO_HAND");
        if (pick != null)
            await CardPileCmd.Add(pick, PileType.Hand);
    }
}

// 光道祭司 珍妮丝（能力牌：本回合发动过弃光→回合结束时获得N点格挡并对随机一名敌人造成N点伤害。
// v0.4.36：稀有度 Common→Uncommon（蓝卡））
[RegisterCard(typeof(LightswornCardPool))]
public class Janice : LsCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars => [new DynamicVar("Amount", 5m)];

    public Janice() : base(1, CardType.Power, CardRarity.Uncommon, TargetType.Self) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        // 施加数值取自DynamicVar，升级时UpgradeValueBy自动生效
        await PowerCmd.Apply<JanicePower>(choiceContext, Owner.Creature, (int)DynamicVars["Amount"].BaseValue, Owner.Creature, this);
    }

    protected override void OnUpgrade() => DynamicVars["Amount"].UpgradeValueBy(3);
}

// 光道防护罩（初始卡。本批反馈问题28：作为「古老牙齿」的转化源——v0.5.0 起改用 RitsuLib 的
// [RegisterArchaicToothTranscendence(typeof(Aegis))] 注册"防护罩→光道埃癸斯盾"映射
// （原 BaseLib ITranscendenceCard 接口的替代；先古目标不入尘封魔典=原版规则））
[RegisterCard(typeof(LightswornCardPool))]
[RegisterArchaicToothTranscendence(typeof(Aegis))]
public class Barrier : LsCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars =>
    [
        new BlockVar(8, ValueProp.Move),
        new DynamicVar("Mill", 2m),
    ];
    public override IEnumerable<CardKeyword> CanonicalKeywords => [LsKeywords.Mill];

    public Barrier() : base(1, CardType.Skill, CardRarity.Basic, TargetType.Self) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await LsUtil.Mill(choiceContext, this, (int)DynamicVars["Mill"].BaseValue);
        await CreatureCmd.GainBlock(Owner.Creature, DynamicVars.Block.BaseValue, ValueProp.Move, cardPlay);
    }

    protected override void OnUpgrade() => DynamicVars.Block.UpgradeValueBy(4);
}

// ============ 破坏之光（先古牌 v0.4.13）：达弗「尘封魔典」赠送（获得时已升级1次）。
// 先古牌机制（原版实证）：尘封魔典从角色卡池抽 CardRarity.Ancient 的卡，但排除古老牙齿的五组
// 基础牌升级对（痛击→破击等）——只有"无基础版"的先古牌能被抽到（铁甲=腐化）。光道对应=破坏之光。
// 上轮的先古光道圣骑士/防护罩（对应基础牌的先古版）光道角色拿不到（古老牙齿只认原版基础牌），已删除。
[RegisterCard(typeof(LightswornCardPool))]
public class LightOfDestruction : LsCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars => [new DynamicVar("Doom", 9m)];
    public override IEnumerable<CardKeyword> CanonicalKeywords => [CardKeyword.Innate];

    public LightOfDestruction() : base(1, CardType.Power, CardRarity.Ancient, TargetType.Self) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await PowerCmd.Apply<LightOfDestructionPower>(choiceContext, Owner.Creature, (int)DynamicVars["Doom"].BaseValue, Owner.Creature, this);
    }

    protected override void OnUpgrade() => DynamicVars["Doom"].UpgradeValueBy(3);
}

// 光道贼猫 雷喵（本批反馈重做：0费、升蓝、消耗——从弃牌堆将最多{Picks}张「光道」牌洗回抽牌堆，
// 每有1种不同名的「光道」牌，获得1点费用。原"洗回→抽等量牌"作废）
[RegisterCard(typeof(LightswornCardPool))]
public class Rinyan : LsCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars => [new DynamicVar("Picks", 2m)];
    public override IEnumerable<CardKeyword> CanonicalKeywords => [CardKeyword.Exhaust];

    public Rinyan() : base(0, CardType.Skill, CardRarity.Uncommon, TargetType.Self) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        List<CardModel> ls = LsUtil.DiscardPile(this).Cards.Where(LsUtil.IsLs).ToList();
        if (ls.Count == 0) return;
        int max = Math.Min((int)DynamicVars["Picks"].BaseValue, ls.Count);
        List<CardModel> chosen = await LsUtil.PickSomeFromList(choiceContext, Owner, ls,
            "LIGHTSWORN_TO_DECK", 0, max);
        foreach (CardModel card in chosen)
            await CardPileCmd.Add(card, PileType.Draw, CardPilePosition.Random);
        // 每有1种不同名的「光道」牌（按返回的牌算）→ 获得1点费用
        int distinct = chosen.Select(c => c.Id).Distinct().Count();
        if (distinct > 0)
            await PlayerCmd.GainEnergy(distinct, Owner);
    }

    // 升级=洗回上限2→3（Picks 变量；行为型升级先例=暮萨满）
    protected override void OnUpgrade() => DynamicVars["Picks"].UpgradeValueBy(1);
}

// 光道暗杀者 莱登（本批反馈：弃光后若弃置到「光道」牌→在本回合结束前获得2点临时力量
// （原"此牌伤害+4"作废；临时力量=BaseLib 临时力量包装器，对本次攻击与后续攻击都生效）
[RegisterCard(typeof(LightswornCardPool))]
public class Layden : LsCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars =>
    [
        new DamageVar(9, ValueProp.Move),
        new DynamicVar("Mill", 2m),
        new DynamicVar("Temp", 2m),
    ];
    public override IEnumerable<CardKeyword> CanonicalKeywords => [LsKeywords.Mill];

    public Layden() : base(1, CardType.Attack, CardRarity.Common, TargetType.AnyEnemy) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        List<CardModel> milled = await LsUtil.Mill(choiceContext, this, (int)DynamicVars["Mill"].BaseValue);
        if (milled.Any(LsUtil.IsLs))
            await PowerCmd.Apply<LaydenTempStrengthPower>(choiceContext, Owner.Creature,
                (int)DynamicVars["Temp"].BaseValue, Owner.Creature, this);
        await DamageCmd.Attack(DynamicVars.Damage.BaseValue).FromCardCompat(this, cardPlay)
            .Targeting(cardPlay.Target!).Execute(choiceContext);
    }

    protected override void OnUpgrade() => DynamicVars.Damage.UpgradeValueBy(4);
}

// 光道弓手 费莉丝（0费；从卡组被弃置时自动加入手牌；只有通过抽牌以外的方式入手时才能打出）
[RegisterCard(typeof(LightswornCardPool))]
public class Felis : LsCard
{
    private bool _playable;

    protected override bool IsPlayable => _playable;
    protected override bool ShouldGlowGoldInternal => _playable;

    protected override IEnumerable<DynamicVar> CanonicalVars =>
    [
        new BlockVar(7, ValueProp.Move),
        new DynamicVar("Mill", 3m),
    ];
    public override IEnumerable<CardKeyword> CanonicalKeywords => [LsKeywords.Mill];

    public Felis() : base(0, CardType.Skill, CardRarity.Common, TargetType.Self) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        // 问题6：费莉丝守(2000)大于攻(1100)，效果为格挡
        await LsUtil.Mill(choiceContext, this, (int)DynamicVars["Mill"].BaseValue);
        await CreatureCmd.GainBlock(Owner.Creature, DynamicVars.Block.BaseValue, ValueProp.Move, cardPlay);
        // 随机一名敌人获得1层易伤（RNG必须玩家侧，参考LsUtil.StripBuffs；HittableEnemies参考Celestia）
        List<Creature> enemies = Owner.Creature.CombatState!.HittableEnemies.ToList();
        if (enemies.Count > 0)
        {
            Creature victim = Owner.RunState.Rng.CombatCardSelection.NextItem(enemies)!;
            await PowerCmd.Apply<VulnerablePower>(choiceContext, victim, 1, Owner.Creature, this);
        }
    }

    protected override void OnUpgrade() => DynamicVars.Block.UpgradeValueBy(3);

    public override Task AfterCardDrawn(PlayerChoiceContext choiceContext, CardModel card, bool fromHandDraw)
    {
        if (card == this) _playable = false;
        return Task.CompletedTask;
    }

    public override async Task AfterCardChangedPiles(CardModel card, PileType oldPileType, AbstractModel? clonedBy)
    {
        if (card != this) return;
        if (oldPileType == PileType.Draw && card.Pile?.Type == PileType.Discard)
        {
            if (await LsUtil.TryRecallOnMill(this, false)) _playable = true;
        }
        else if (card.Pile?.Type == PileType.Hand)
        {
            _playable = oldPileType != PileType.Draw;
        }
    }
}

// 光之援军（初始卡 & 常规卡）：弃光3后从卡组检索光道（问题12+13；只从卡组，符合原版效果；
// 本批反馈：去掉检索牌的0费效果）
[RegisterCard(typeof(LightswornCardPool))]
public class Reinforce : LsCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars => [new DynamicVar("Mill", 3m)];
    public override IEnumerable<CardKeyword> CanonicalKeywords => [LsKeywords.Mill];

    public Reinforce() : base(1, CardType.Skill, CardRarity.Common, TargetType.Self) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await LsUtil.Mill(choiceContext, this, (int)DynamicVars["Mill"].BaseValue);
        CardModel? pick = await LsUtil.PickFromDraw(choiceContext, this, LsUtil.IsLs);
        if (pick != null)
            await CardPileCmd.Add(pick, PileType.Hand);
    }

    protected override void OnUpgrade() => EnergyCost.UpgradeBy(-1);
}
