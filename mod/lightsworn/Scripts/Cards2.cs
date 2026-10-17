using MegaCrit.Sts2.Core.CardSelection;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Commands.Builders;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.ValueProps;

namespace Lightsworn;

// ================= 本家·非普通 =================

// 光道战士 加洛斯（本批反馈问题34：升金；敲后效果改到敲前——基础=弃光2+按其中光道牌抽牌；
// 敲后=触发条件改为任意弃光都触发，不限制光道）
// 已知问题4（v0.5.4）：正文内联的"[gold]弃光[/gold]"要能悬浮查定义 → 声明 MILL 关键词
// （placement=None 不注入词条行；声明的唯一效果=原版 CardModel.HoverTips 自动带出提示）
[RegisterCard(typeof(LightswornCardPool))]
public class Garoth : LsCard
{
    public override IEnumerable<CardKeyword> CanonicalKeywords => [LsKeywords.Mill];

    public Garoth() : base(2, CardType.Power, CardRarity.Rare, TargetType.Self) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        if (IsUpgraded)
            await PowerCmd.Apply<GarothPowerPlus>(choiceContext, Owner.Creature, 2, Owner.Creature, this);
        else
            await PowerCmd.Apply<GarothPower>(choiceContext, Owner.Creature, 2, Owner.Creature, this);
    }

    protected override void OnUpgrade() { }
}

// 光道天使 塞勒斯特 基路伯（伤害5×3/5×4"对所有敌人"结算，删除溅射。
// 本批反馈问题2修复：多段伤害必须用原生多段攻击（WithHitCount）+ TargetingAllOpponents——
// 原来逐段独立 DamageCmd.Execute=每段一个 AttackCommand，活力（VigorPower）的 BeforeAttack 只
// 认第一个命令（AfterAttack 后层数消耗归零），后续段落吃不到活力加成；原生多段=单个 AttackCommand
// 内部循环，BeforeAttack/AfterAttack 只包一次，全部段落都吃活力）
// v0.6.1 已知问题8：基础伤害4→5（5×3 / 敲后5×4，仍靠 Hits+1 升级）
[RegisterCard(typeof(LightswornCardPool))]
public class Celestia : LsCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars =>
    [
        new DamageVar(5, ValueProp.Move),
        new DynamicVar("Hits", 3m),
        new DynamicVar("Mill", 4m),
    ];
    public override IEnumerable<CardKeyword> CanonicalKeywords => [LsKeywords.Mill];

    public Celestia() : base(2, CardType.Attack, CardRarity.Common, TargetType.AllEnemies) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await LsUtil.Mill(choiceContext, this, (int)DynamicVars["Mill"].BaseValue);
        // 对所有敌人造成4点伤害，重复{Hits}次（原生多段攻击：命中目标逐段刷新，死亡自动退出）
        await DamageCmd.Attack(DynamicVars.Damage.BaseValue).FromCardCompat(this, cardPlay)
            .TargetingAllOpponents(Owner.Creature.CombatState!)
            .WithHitCount((int)DynamicVars["Hits"].BaseValue)
            .Execute(choiceContext);
    }

    // 敲后：攻击次数3→4
    protected override void OnUpgrade() => DynamicVars["Hits"].UpgradeValueBy(1);
}

// 光道龙 格拉古尼斯（本批反馈：基础伤害14→18，敲后22（升级=伤害+4）；每张「光道」+2 的加成保留、
// 升级后每张+3（订正：Scale 2→3 的升级保留，与伤害+4 并改）。
// 凯旋：斩杀时自动回手，费用临时变为0（v0.4.39 追加，照原版击杀判定=DamageResult.WasTargetKilled）
// ⚠ 已知问题1（v0.5.4 曾误修，v0.6.1 再修）：现象"斩杀时卡回手了、但仍是2费"，根因=0费的**清理时机**。
//   原版 `CardModel.OnPlayWrapper` 在 OnPlay 返回后、结算末尾**无条件**执行
//   `EnergyCost.AfterCardPlayedCleanup()`：
//     `_localModifiers.RemoveAll(m => m.Expiration.HasFlag(WhenPlayed))`
//   —— 它清的是 **this 这张卡**的修正，而此刻这张卡已经被 OnPlay 挪回手牌。
//   `SetUntilPlayed(0)` 与 `SetToFreeThisTurn()`（=SetThisTurnOrUntilPlayed(0)）的 Expiration 都**含
//   WhenPlayed 位**，因此都会被这行原地抹掉；v0.5.4 以为"EndOfTurn 位能保命"是错的（HasFlag(WhenPlayed)
//   只看该位，不看是否还有别的位）。唯一能在清理后存活又不跨回合的写法=**`EnergyCost.SetThisTurn(0)`**
//   （Expiration=EndOfTurn，不含 WhenPlayed），回合结束自然失效——这就是本卡"临时0费"的语义。
//   同时保留"按 Add 的实际结果判定"：`IsEnding`（=所有 primary enemy 已死）为 true 时
//   `CardPileCmd.Add` 会静默返回 success=false（守卫见 CardPileCmd.Add 开头），
//   那种情况（例如直接击杀 boss 本体）确实什么都没发生，不应白给0费标记。
[RegisterCard(typeof(LightswornCardPool))]
public class Gragonith : LsCard
{
    // 完美打击范式（PerfectedStrike）：基础值 + 每张光道 × ExtraDamage，卡面动态显示总和。
    // 面板预览按"当前弃牌堆"计算；实际伤害在 OnPlay 弃光3之后结算，所以实战数字可能比手牌预览更高。
    protected override IEnumerable<DynamicVar> CanonicalVars =>
    [
        new CalculationBaseVar(18m),
        new ExtraDamageVar(2m),
        new CalculatedDamageVar(ValueProp.Move)
            .WithMultiplier((card, _) => LsUtil.DiscardPile(card).Cards.Count(LsUtil.IsLs)),
        new DynamicVar("Mill", 3m),
    ];
    public override IEnumerable<CardKeyword> CanonicalKeywords => [LsKeywords.Mill];

    public Gragonith() : base(2, CardType.Attack, CardRarity.Rare, TargetType.AnyEnemy) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await LsUtil.Mill(choiceContext, this, (int)DynamicVars["Mill"].BaseValue);
        // CalculatedDamage 在结算时重新 Calculate：弃光后的弃牌堆光道数会算进去（与旧版一致）
        AttackCommand attack = await DamageCmd.Attack(DynamicVars.CalculatedDamage).FromCardCompat(this, cardPlay)
            .Targeting(cardPlay.Target!).Execute(choiceContext);
        // 斩杀时（原版击杀判定 WasTargetKilled）自动回手且费用临时变为0
        if (!attack.Results.SelectMany(r => r).Any(r => r.WasTargetKilled)) return;
        if (!LsUtil.HandHasSpace(this)) return;
        // 已知问题1：按 Add 的实际结果判定——IsEnding（所有 primary enemy 已死，如直接击杀 boss）时
        // 该 API 静默失败（success=false），此时什么都没发生，不能白给0费标记
        CardPileAddResult added = await CardPileCmd.Add(this, PileType.Hand);
        if (!added.success) return;
        // 已知问题1：必须用 SetThisTurn（Expiration=EndOfTurn，不含 WhenPlayed）——
        // SetUntilPlayed / SetToFreeThisTurn 的 Expiration 都含 WhenPlayed，会被 OnPlayWrapper 尾部的
        // AfterCardPlayedCleanup() 原地清掉（见类上方注释）。
        EnergyCost.SetThisTurn(0);
        InvokeEnergyCostChanged();
    }

    // 基础伤害18→22；每张「光道」+2→+3（与原数值一致，只换成动态显示）
    protected override void OnUpgrade()
    {
        DynamicVars.CalculationBase.UpgradeValueBy(4);
        DynamicVars.ExtraDamage.UpgradeValueBy(1);
    }
}

// 光道圣灵 夏尔（本批反馈：进白（普通）；格挡8/10，弃牌堆光道牌每张+1。
// v0.6.2：改用完美打击范式的动态格挡（CalculationBase + CalculationExtra × 弃牌堆光道数），卡面显示实时总值）
[RegisterCard(typeof(LightswornCardPool))]
public class Shire : LsCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars =>
    [
        new CalculationBaseVar(8m),
        new CalculationExtraVar(1m),
        new CalculatedBlockVar(ValueProp.Move)
            .WithMultiplier((card, _) => LsUtil.DiscardPile(card).Cards.Count(LsUtil.IsLs)),
    ];

    public Shire() : base(1, CardType.Skill, CardRarity.Common, TargetType.Self) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await CreatureCmd.GainBlock(Owner.Creature, DynamicVars.CalculatedBlock.Calculate(cardPlay.Target),
            DynamicVars.CalculatedBlock.Props, cardPlay);
    }

    // 基础格挡8→10；每张「光道」加成固定+1
    protected override void OnUpgrade() => DynamicVars.CalculationBase.UpgradeValueBy(2);
}

// 光道德鲁伊 奥库斯（0费、消耗。弃光2+1层人工制品不变。本批反馈问题13：敲后2层人工
// ——Artifact 变量 1→2；弃光数的升级保留）
[RegisterCard(typeof(LightswornCardPool))]
public class Orcus : LsCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars =>
    [
        new DynamicVar("Mill", 2m),
        new DynamicVar("Artifact", 1m),
    ];
    public override IEnumerable<CardKeyword> CanonicalKeywords => [LsKeywords.Mill, CardKeyword.Exhaust];

    public Orcus() : base(0, CardType.Skill, CardRarity.Uncommon, TargetType.Self) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await LsUtil.Mill(choiceContext, this, (int)DynamicVars["Mill"].BaseValue);
        await PowerCmd.Apply<ArtifactPower>(choiceContext, Owner.Creature, (int)DynamicVars["Artifact"].BaseValue, Owner.Creature, this);
    }

    protected override void OnUpgrade()
    {
        DynamicVars["Mill"].UpgradeValueBy(1);
        DynamicVars["Artifact"].UpgradeValueBy(1);
    }
}

// 光道恶魔 魏丝（弃光后把手牌光道压回卡组顶；被弃置时从弃牌堆回收其他光道并临时0费；
// 敲后强化改为弃光3。本批反馈问题19：费用1→0。v0.6.1 已知问题7：追加8/12格挡（敲后+4））
[RegisterCard(typeof(LightswornCardPool))]
public class Weiss : LsCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars =>
    [
        new BlockVar(8, ValueProp.Move),
        new DynamicVar("Mill", 2m),
        new DynamicVar("Back", 1m),
    ];
    public override IEnumerable<CardKeyword> CanonicalKeywords => [LsKeywords.Mill];

    public Weiss() : base(0, CardType.Skill, CardRarity.Uncommon, TargetType.Self) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        // 问题10：先把手牌光道压回卡组顶，再弃光2（刚放回的牌会被弃光弃掉——按用户要求）
        List<CardModel> lsInHand = PileType.Hand.GetPile(Owner).Cards.Where(LsUtil.IsLs).ToList();
        List<CardModel> chosen = await LsUtil.PickFromList(choiceContext, Owner, lsInHand,
            "LIGHTSWORN_TO_DRAW_TOP", (int)DynamicVars["Back"].BaseValue);
        foreach (CardModel card in chosen)
            await CardPileCmd.Add(card, PileType.Draw, CardPilePosition.Top);
        await CreatureCmd.GainBlock(Owner.Creature, DynamicVars.Block.BaseValue, ValueProp.Move, cardPlay);
        await LsUtil.Mill(choiceContext, this, (int)DynamicVars["Mill"].BaseValue);
    }

    // 敲后：格挡8→12，弃光2→3
    protected override void OnUpgrade()
    {
        DynamicVars.Block.UpgradeValueBy(4);
        DynamicVars["Mill"].UpgradeValueBy(1);
    }

    public override async Task AfterCardChangedPiles(CardModel card, PileType oldPileType, AbstractModel? clonedBy)
    {
        if (card != this) return;
        if (oldPileType != PileType.Draw || card.Pile?.Type != PileType.Discard) return;
        List<CardModel> candidates = LsUtil.DiscardPile(this).Cards
            .Where(c => LsUtil.IsLs(c) && c != this).ToList();
        if (candidates.Count == 0 || !LsUtil.HandHasSpace(this)) return;
        CardModel? pick = await LsUtil.PickFirst(new BlockingPlayerChoiceContext(), Owner, candidates, "LIGHTSWORN_TO_HAND");
        if (pick != null)
        {
            await CardPileCmd.Add(pick, PileType.Hand);
            pick.EnergyCost.SetThisTurnOrUntilPlayed(0);
        }
    }
}

// 光道少女 密涅瓦（0费；按弃牌堆光道种类阶梯检索龙，获得的龙牌获得消耗（问题8）；
// 被弃置时追加弃光1；本批问题14：敲后改为"被从卡组弃置时抽1"（原降挡位升级作废））
[RegisterCard(typeof(LightswornCardPool))]
public class MaidenMinerva : LsCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars =>
    [
        new DynamicVar("Mill", 2m),
        new DynamicVar("Tier1", 4m),
        new DynamicVar("Tier2", 6m),
        new DynamicVar("Tier3", 8m),
    ];
    public override IEnumerable<CardKeyword> CanonicalKeywords => [LsKeywords.Mill];

    // 问题11：卡牌停留时预览三条龙卡图
    protected override IEnumerable<IHoverTip> AdditionalHoverTips =>
        HoverTipFactory.FromCardWithCardHoverTips<LightswornDragon>()
            .Concat(HoverTipFactory.FromCardWithCardHoverTips<Gragonith>())
            .Concat(HoverTipFactory.FromCardWithCardHoverTips<JudgementDragon>());

    public MaidenMinerva() : base(0, CardType.Skill, CardRarity.Uncommon, TargetType.Self) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await LsUtil.Mill(choiceContext, this, (int)DynamicVars["Mill"].BaseValue);
        int count = LsUtil.DiscardPile(this).Cards.Where(LsUtil.IsLs)
            .Select(c => c.Id).Distinct().Count();
        if (!LsUtil.HandHasSpace(this)) return;

        // 问题3：从满足挡位的龙中选择（挡位满足越多可选越多）
        List<CardModel> options = new();
        if (count >= (int)DynamicVars["Tier1"].BaseValue) options.Add(ModelDb.Card<LightswornDragon>());
        if (count >= (int)DynamicVars["Tier2"].BaseValue) options.Add(ModelDb.Card<Gragonith>());
        if (count >= (int)DynamicVars["Tier3"].BaseValue) options.Add(ModelDb.Card<JudgementDragon>());
        if (options.Count == 0) return;
        CardModel? chosen = (await LsUtil.PickFromList(choiceContext, Owner, options, "LIGHTSWORN_TO_HAND", 1)).FirstOrDefault();
        if (chosen == null) return;

        // 优先从抽牌堆/弃牌堆拿实体牌，找不到则生成一张（奖励不落空）
        CardModel? pick = LsUtil.DrawPile(this).Cards.FirstOrDefault(c => c.GetType() == chosen.GetType())
            ?? LsUtil.DiscardPile(this).Cards.FirstOrDefault(c => c.GetType() == chosen.GetType());
        if (pick == null)
        {
            pick = chosen switch
            {
                JudgementDragon => Owner.Creature.CombatState?.CreateCard<JudgementDragon>(Owner),
                Gragonith => Owner.Creature.CombatState?.CreateCard<Gragonith>(Owner),
                _ => Owner.Creature.CombatState?.CreateCard<LightswornDragon>(Owner),
            };
        }
        if (pick != null)
        {
            // 问题8：获得的龙牌增加消耗
            pick.AddKeyword(CardKeyword.Exhaust);
            await CardPileCmd.Add(pick, PileType.Hand);
        }
    }

    protected override void OnUpgrade()
    {
        // 本批问题14：升级从"降低挡位需求"改为追加"被从卡组弃置时抽1"（行为型升级，挡位不变）
    }

    public override async Task AfterCardChangedPiles(CardModel card, PileType oldPileType, AbstractModel? clonedBy)
    {
        if (card != this) return;
        if (oldPileType != PileType.Draw || card.Pile?.Type != PileType.Discard) return;
        await LsUtil.Mill(new BlockingPlayerChoiceContext(), this, 1);
        // 问题14：敲后追加——被从卡组弃置时抽1张牌
        if (IsUpgraded)
            await CardPileCmd.Draw(new BlockingPlayerChoiceContext(), 1, Owner);
    }
}

// 暮光道斗犬 雷光（问题5：移除增益改为施加虚弱+易伤；获得1层暮光；强化后0费；
// 问题11：暮光注册为关键词，卡牌停留可看效果）
[RegisterCard(typeof(LightswornCardPool))]
public class TwilightRyko : LsCard
{
    public TwilightRyko() : base(1, CardType.Skill, CardRarity.Uncommon, TargetType.AnyEnemy) { }

    public override IEnumerable<CardKeyword> CanonicalKeywords => [LsKeywords.Twilight];

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await LsUtil.ExhaustOneFromDiscard(choiceContext, this, LsUtil.IsLs);
        await PowerCmd.Apply<WeakPower>(choiceContext, cardPlay.Target!, 1, Owner.Creature, this);
        await PowerCmd.Apply<VulnerablePower>(choiceContext, cardPlay.Target!, 1, Owner.Creature, this);
        await PowerCmd.Apply<TwilightPower>(choiceContext, Owner.Creature, 1, Owner.Creature, this);
    }

    protected override void OnUpgrade() => EnergyCost.UpgradeBy(-1);
}

// 暮光道巫师 丽拉（消耗弃牌堆1张光道：削目标敌人力量并获得暮光；没有光道可消耗则整张牌无效。
// 脆弱改虚弱，稀有度保持蓝卡；增加消耗；暮光关键词。本批反馈问题20：敲后虚弱改2层）
[RegisterCard(typeof(LightswornCardPool))]
public class TwilightLyla : LsCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars =>
    [
        new DynamicVar("Debuff", 1m),
        new DynamicVar("Weak", 1m),
    ];

    public override IEnumerable<CardKeyword> CanonicalKeywords => [CardKeyword.Exhaust, LsKeywords.Twilight];

    public TwilightLyla() : base(1, CardType.Skill, CardRarity.Uncommon, TargetType.AnyEnemy) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        CardModel? burned = await LsUtil.ExhaustOneFromDiscard(choiceContext, this, LsUtil.IsLs);
        if (burned == null) return;
        await PowerCmd.Apply<StrengthPower>(choiceContext, cardPlay.Target!, -(int)DynamicVars["Debuff"].BaseValue, Owner.Creature, this);
        // 减敏捷效果改为虚弱层数（问题20：敲后2层）
        await PowerCmd.Apply<WeakPower>(choiceContext, cardPlay.Target!, (int)DynamicVars["Weak"].BaseValue, Owner.Creature, this);
        await PowerCmd.Apply<TwilightPower>(choiceContext, Owner.Creature, 1, Owner.Creature, this);
    }

    protected override void OnUpgrade()
    {
        DynamicVars["Debuff"].UpgradeValueBy(1);
        DynamicVars["Weak"].UpgradeValueBy(1);
    }
}

// 暮光道将军 简（本批反馈重做：进白（普通）——1费打9/12；可以消耗弃牌堆中的1张「光道」牌，
// 若如此做，额外造成5/7点伤害；获得1层暮光。原"消耗1张光道→16伤、没有则整张牌无效"作废）
[RegisterCard(typeof(LightswornCardPool))]
public class TwilightJain : LsCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars =>
    [
        new DamageVar(9, ValueProp.Move),
        new DynamicVar("Bonus", 5m),
    ];

    public override IEnumerable<CardKeyword> CanonicalKeywords => [LsKeywords.Twilight];

    public TwilightJain() : base(1, CardType.Attack, CardRarity.Common, TargetType.AnyEnemy) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        // "可以"消耗=0~1可选（不选则没有额外伤害；弃牌堆无光道牌则直接跳过）
        bool burned = false;
        List<CardModel> candidates = LsUtil.DiscardPile(this).Cards.Where(LsUtil.IsLs).ToList();
        if (candidates.Count > 0)
        {
            List<CardModel> picked = await LsUtil.PickSomeFromList(choiceContext, Owner, candidates,
                "LIGHTSWORN_TO_EXHAUST", 0, 1);
            if (picked.Count > 0)
            {
                await LsCompat.ExhaustCompat(choiceContext, picked[0]);
                burned = true;
            }
        }
        decimal damage = DynamicVars.Damage.BaseValue + (burned ? DynamicVars["Bonus"].BaseValue : 0);
        await DamageCmd.Attack(damage).FromCardCompat(this, cardPlay)
            .Targeting(cardPlay.Target!).Execute(choiceContext);
        await PowerCmd.Apply<TwilightPower>(choiceContext, Owner.Creature, 1, Owner.Creature, this);
    }

    // 本批：9/12 与额外 5/7（伤害+3、额外+2）
    protected override void OnUpgrade()
    {
        DynamicVars.Damage.UpgradeValueBy(3);
        DynamicVars["Bonus"].UpgradeValueBy(2);
    }
}

// 光道宰制者 基里奥斯（新增：从抽牌堆选择1张牌弃置；拿回弃置牌不再限制光道）
[RegisterCard(typeof(LightswornCardPool))]
public class Kiryu : LsCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars =>
    [
        new DamageVar(20, ValueProp.Move),
        new DynamicVar("Mill", 3m),
    ];
    public override IEnumerable<CardKeyword> CanonicalKeywords => [LsKeywords.Mill];

    public Kiryu() : base(2, CardType.Attack, CardRarity.Rare, TargetType.AnyEnemy) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        List<CardModel> milled = await LsUtil.Mill(choiceContext, this, (int)DynamicVars["Mill"].BaseValue);
        await DamageCmd.Attack(DynamicVars.Damage.BaseValue).FromCardCompat(this, cardPlay)
            .Targeting(cardPlay.Target!).Execute(choiceContext);
        // 将弃置的1张牌加入手牌（不限光道）
        CardModel? pick = await LsUtil.PickFromMilled(choiceContext, this, milled, _ => true);
        if (pick != null)
            await CardPileCmd.Add(pick, PileType.Hand);
        // 从抽牌堆选择1张牌弃置（走 MillSelected：逐张触发光道弃光钩子并触发加洛斯）
        List<CardModel> drawCandidates = LsUtil.DrawPile(this).Cards.ToList();
        if (drawCandidates.Count > 0)
        {
            List<CardModel> chosen = await LsUtil.PickFromList(choiceContext, Owner, drawCandidates, "LIGHTSWORN_TO_DISCARD", 1);
            if (chosen.Count > 0)
                await LsUtil.MillSelected(choiceContext, this, chosen);
        }
    }

    protected override void OnUpgrade() => DynamicVars.Damage.UpgradeValueBy(4);
}

// 光道的裁决（0费；打出后自己置于抽牌堆顶；任意来源把自己从抽牌堆弃到弃牌堆时，
// 1张消耗的裁决之龙Token加入手牌；敲后改为1张强化后的裁决之龙。
// 本批反馈问题16：Token的「虚无」改为「保留」——回合结束不弃置，可留到下回合打出。
// v0.6.1 已知问题12：去掉Token的「保留」——基础裁决之龙不需要保留；敲后的裁决之龙自带保留（OnUpgrade））
[RegisterCard(typeof(LightswornCardPool))]
public class Decree : LsCard
{
    public Decree() : base(0, CardType.Skill, CardRarity.Uncommon, TargetType.Self) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        // 自己回到抽牌堆顶（Play→Draw 移动不会误触发下面的弃置钩子）
        await CardPileCmd.Add(this, PileType.Draw, CardPilePosition.Top);
    }

    protected override void OnUpgrade() { }

    // 任意来源：当自己被从抽牌堆弃到弃牌堆时（弃光/弃置等），1张消耗的裁决之龙Token加入手牌
    // （敲后=1张强化后的裁决之龙，强化版自带「保留」；手牌满则不生成）
    public override async Task AfterCardChangedPiles(CardModel card, PileType oldPileType, AbstractModel? clonedBy)
    {
        if (card != this) return;
        if (oldPileType != PileType.Draw || card.Pile?.Type != PileType.Discard) return;
        if (!LsUtil.HandHasSpace(this)) return;
        CardModel? token = await LsUtil.CreateToken<JudgementDragon>(new BlockingPlayerChoiceContext(), this, PileType.Hand, exhaust: true);
        if (token != null && IsUpgraded)
        {
            token.UpgradeInternal();
            token.FinalizeUpgradeInternal();
        }
    }
}

// 光道埃癸斯盾（本批反馈问题28：重做为「光道防护罩」的先古版——1费技能：弃光4，获得15/20格挡，
// "从卡组被弃置时"自动加入手牌且费用变为0（细剑同款的弃光回手钩子）。
// 获取途径=欧洛巴斯遗物「古老牙齿」（初始卡组中的光道防护罩→此卡，见 Cards1.cs Barrier 的
// ITranscendenceCard 钩子）；因是 TranscendenceCard，达弗尘封魔典不会给到（原版规则）。
// 旧版（打出光道牌获得2/3格挡的能力）整体移交给「光之回弹」，见 Cards4.cs/LightBouncePower）
[RegisterCard(typeof(LightswornCardPool))]
public class Aegis : LsCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars =>
    [
        new BlockVar(15, ValueProp.Move),
        new DynamicVar("Mill", 4m),
    ];
    public override IEnumerable<CardKeyword> CanonicalKeywords => [LsKeywords.Mill];

    public Aegis() : base(1, CardType.Skill, CardRarity.Ancient, TargetType.Self) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await LsUtil.Mill(choiceContext, this, (int)DynamicVars["Mill"].BaseValue);
        await CreatureCmd.GainBlock(Owner.Creature, DynamicVars.Block.BaseValue, ValueProp.Move, cardPlay);
    }

    protected override void OnUpgrade() => DynamicVars.Block.UpgradeValueBy(5);

    // 被弃置时自动加入手牌，费用变为0（订正：做强一点——"类似影依的被弃置时"双钩子：
    // 弃光（Draw→Discard）+ 手牌弃置（AfterCardDiscarded）都回手。
    // 注意回合结束的手牌清理走 CardPileCmd.Add+AfterFlush，不触发 AfterCardDiscarded，不会每回合自动回手）
    public override async Task AfterCardChangedPiles(CardModel card, PileType oldPileType, AbstractModel? clonedBy)
    {
        if (card == this && oldPileType == PileType.Draw && card.Pile?.Type == PileType.Discard)
            await LsUtil.TryRecallOnMill(this, true);
    }

    public override async Task AfterCardDiscarded(PlayerChoiceContext choiceContext, CardModel card)
    {
        if (card != this || card.Pile?.Type != PileType.Discard) return;
        await LsUtil.TryRecallOnMill(this, true);
    }
}

// 暗之进军（除光抽牌堆自选N张——除光是消耗，不触发加洛斯/光道弃光钩子。本批反馈问题18：费用1→0）
[RegisterCard(typeof(LightswornCardPool))]
public class DarkMarch : LsCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars => [new DynamicVar("Banish", 2m)];
    public override IEnumerable<CardKeyword> CanonicalKeywords => [LsKeywords.Banish];

    public DarkMarch() : base(0, CardType.Skill, CardRarity.Uncommon, TargetType.Self) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        CardModel? pick = await LsUtil.PickFromDiscard(choiceContext, this, LsUtil.IsLs);
        if (pick != null)
        {
            await CardPileCmd.Add(pick, PileType.Hand);
            if (IsUpgraded)
                pick.EnergyCost.SetUntilPlayed(0);
        }
        await LsUtil.Banish(choiceContext, this, (int)DynamicVars["Banish"].BaseValue);
    }

    protected override void OnUpgrade() { }
}
