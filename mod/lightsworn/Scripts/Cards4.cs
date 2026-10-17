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
using MegaCrit.Sts2.Core.Rewards;
using MegaCrit.Sts2.Core.Rooms;
using MegaCrit.Sts2.Core.Runs;
using MegaCrit.Sts2.Core.ValueProps;

namespace Lightsworn;

// ================= 本家·魔法/陷阱 =================

// 光道的神域（回合开始可选发动：弃1张手牌光道 → 从弃牌堆拿{Take}张光道；问题3：1费。
// 本批反馈：降蓝（稀有→非普通））
[RegisterCard(typeof(LightswornCardPool))]
public class Sanctuary : LsCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars => [new DynamicVar("Take", 1m)];

    public Sanctuary() : base(1, CardType.Power, CardRarity.Uncommon, TargetType.Self) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await PowerCmd.Apply<SanctuaryPower>(choiceContext, Owner.Creature,
            DynamicVars["Take"].IntValue, Owner.Creature, this);
    }

    protected override void OnUpgrade() => DynamicVars["Take"].UpgradeValueBy(1);
}

// 光道细剑（从卡组被弃置时自动加入手牌且本回合费用变为0）
// 本批反馈问题9：+4/6临时力量改为获得6/8点活力（原版VigorPower：下一拳+Amount，打完消耗）
[RegisterCard(typeof(LightswornCardPool))]
public class Sabre : LsCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars =>
    [
        new DynamicVar("Vigor", 6m),
        new DynamicVar("Mill", 2m),
    ];
    public override IEnumerable<CardKeyword> CanonicalKeywords => [LsKeywords.Mill];

    public Sabre() : base(1, CardType.Skill, CardRarity.Common, TargetType.Self) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await LsUtil.Mill(choiceContext, this, (int)DynamicVars["Mill"].BaseValue);
        await PowerCmd.Apply<VigorPower>(choiceContext, Owner.Creature, (int)DynamicVars["Vigor"].BaseValue, Owner.Creature, this);
    }

    protected override void OnUpgrade() => DynamicVars["Vigor"].UpgradeValueBy(2);

    public override async Task AfterCardChangedPiles(CardModel card, PileType oldPileType, AbstractModel? clonedBy)
    {
        if (card == this && oldPileType == PileType.Draw && card.Pile?.Type == PileType.Discard)
            await LsUtil.TryRecallOnMill(this, true);
    }
}

// 光之放逐（本批反馈问题22：改为对目标施加2层易伤和2层虚弱（敲后3层）；
// 强制弃光道——必须手牌中有「光道」牌才能打出，打出时强制弃置1张手牌「光道」牌）
[RegisterCard(typeof(LightswornCardPool))]
public class LightImprisoning : LsCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars =>
    [
        new DynamicVar("Weak", 2m),
        new DynamicVar("Vul", 2m),
    ];

    public LightImprisoning() : base(1, CardType.Skill, CardRarity.Uncommon, TargetType.AnyEnemy) { }

    // 问题22：强制弃光道——手牌中没有「光道」牌时不可打出
    protected override bool IsPlayable => base.IsPlayable && PileType.Hand.GetPile(Owner).Cards.Any(LsUtil.IsLs);
    protected override bool ShouldGlowGoldInternal => IsPlayable;

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        // 强制弃置手牌中的1张「光道」牌（若手牌光道只有1张则直接弃它）
        List<CardModel> lsInHand = PileType.Hand.GetPile(Owner).Cards.Where(LsUtil.IsLs).ToList();
        if (lsInHand.Count > 0)
        {
            if (lsInHand.Count == 1)
            {
                await CardCmd.Discard(choiceContext, lsInHand[0]);
            }
            else
            {
                CardSelectorPrefs prefs = new(LsUtil.Prompt("LIGHTSWORN_TO_DISCARD"), 1);
                List<CardModel> chosen = (await CardSelectCmd.FromHand(choiceContext, Owner, prefs, LsUtil.IsLs, this))
                    .Where(LsUtil.IsLs).ToList();
                if (chosen.Count > 0)
                    await CardCmd.Discard(choiceContext, chosen);
            }
        }
        await PowerCmd.Apply<WeakPower>(choiceContext, cardPlay.Target!,
            DynamicVars["Weak"].BaseValue, Owner.Creature, this);
        await PowerCmd.Apply<VulnerablePower>(choiceContext, cardPlay.Target!,
            DynamicVars["Vul"].BaseValue, Owner.Creature, this);
    }

    // 问题22：敲后易伤、虚弱同为3层
    protected override void OnUpgrade()
    {
        DynamicVars["Weak"].UpgradeValueBy(1);
        DynamicVars["Vul"].UpgradeValueBy(1);
    }
}

// 太阳交换
[RegisterCard(typeof(LightswornCardPool))]
public class SolarExchange : LsCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars =>
    [
        new CardsVar(2),
        new DynamicVar("Mill", 2m),
    ];
    public override IEnumerable<CardKeyword> CanonicalKeywords => [LsKeywords.Mill];

    public SolarExchange() : base(1, CardType.Skill, CardRarity.Common, TargetType.Self) { }

    // 问题10：手牌有「光道」牌才能打出（弃置步骤只认光道牌；此卡名无「光道」不在白名单，不会把自己算进去）
    protected override bool IsPlayable => base.IsPlayable && PileType.Hand.GetPile(Owner).Cards.Any(LsUtil.IsLs);
    protected override bool ShouldGlowGoldInternal => IsPlayable;

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        // 丢1张手牌中的光道牌（若有）
        List<CardModel> lsInHand = PileType.Hand.GetPile(Owner).Cards.Where(LsUtil.IsLs).ToList();
        if (lsInHand.Count == 1)
        {
            await CardCmd.Discard(choiceContext, lsInHand[0]);
        }
        else if (lsInHand.Count > 1)
        {
            CardSelectorPrefs prefs = new(LsUtil.Prompt("LIGHTSWORN_TO_DISCARD"), 1);
            List<CardModel> chosen = (await CardSelectCmd.FromHand(choiceContext, Owner, prefs, LsUtil.IsLs, this))
                .Where(LsUtil.IsLs).ToList();
            if (chosen.Count > 0)
                await CardCmd.Discard(choiceContext, chosen);
        }
        await CardPileCmd.Draw(choiceContext, DynamicVars.Cards.IntValue, Owner);
        await LsUtil.Mill(choiceContext, this, (int)DynamicVars["Mill"].BaseValue);
    }

    protected override void OnUpgrade() => EnergyCost.UpgradeBy(-1);
}

// 正义世界（本批反馈问题36：改成3费能力、升金——每次弃光，可以将弃置的牌中的1张加入手牌。
// 订正：敲后是正义世界**自己**获得「保留」（回合结束留在手牌，等攒够费用再打出），
// 不是拿回的牌带保留——原 JusticeWorldPowerPlus/GrantsRetain 作废）
[RegisterCard(typeof(LightswornCardPool))]
public class JusticeWorld : LsCard
{
    // 已知问题4（v0.5.4）：正文内联的"[gold]弃光[/gold]"（触发条件）需要悬浮提示可查
    public override IEnumerable<CardKeyword> CanonicalKeywords => [LsKeywords.Mill];

    public JusticeWorld() : base(3, CardType.Power, CardRarity.Rare, TargetType.Self) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await PowerCmd.Apply<JusticeWorldPower>(choiceContext, Owner.Creature, 1, Owner.Creature, this);
    }

    // 订正：敲后自己获得「保留」
    protected override void OnUpgrade() => AddKeyword(CardKeyword.Retain);
}

// 光之回弹（本批反馈问题29：效果改为原「光道埃癸斯盾」的效果——每当你打出「光道」牌，获得格挡
// （原埃癸斯盾的BlockGain 2/敲后3不变；埃癸斯盾本批被改造成防护罩的先古版）。
// 本批反馈：调蓝（稀有→非普通））
[RegisterCard(typeof(LightswornCardPool))]
public class LightBounce : LsCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars => [new DynamicVar("BlockGain", 2m)];

    public LightBounce() : base(1, CardType.Power, CardRarity.Uncommon, TargetType.Self) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await PowerCmd.Apply<LightBouncePower>(choiceContext, Owner.Creature, (int)DynamicVars["BlockGain"].BaseValue, Owner.Creature, this);
    }

    protected override void OnUpgrade() => DynamicVars["BlockGain"].UpgradeValueBy(1);
}

// 黄昏之抹杀
[RegisterCard(typeof(LightswornCardPool))]
public class TwilightErasure : LsCard
{
    public TwilightErasure() : base(1, CardType.Skill, CardRarity.Uncommon, TargetType.AnyEnemy) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        int burned = 0;
        for (int i = 0; i < 2; i++)
        {
            CardModel? pick = await LsUtil.PickFromDiscard(choiceContext, this, LsUtil.IsLs, "LIGHTSWORN_TO_EXHAUST");
            if (pick == null) break;
            await LsCompat.ExhaustCompat(choiceContext, pick);
            burned++;
        }
        // 问题5：原"每消耗1张移除目标1个随机增益"改为施加等量虚弱+易伤
        if (burned > 0)
        {
            await PowerCmd.Apply<WeakPower>(choiceContext, cardPlay.Target!, burned, Owner.Creature, this);
            await PowerCmd.Apply<VulnerablePower>(choiceContext, cardPlay.Target!, burned, Owner.Creature, this);
        }
    }

    protected override void OnUpgrade() { }

    // 自己被光道卡从卡组弃掉时：手牌中随机1张（敲后2张）光道牌本回合费用变为0（没有候选则无事发生）
    protected internal override async Task OnMilledByLsCard(PlayerChoiceContext ctx, CardModel source)
    {
        List<CardModel> candidates = PileType.Hand.GetPile(Owner).Cards.Where(LsUtil.IsLs).ToList();
        int count = Math.Min(IsUpgraded ? 2 : 1, candidates.Count);
        for (int i = 0; i < count; i++)
        {
            CardModel pick = Owner.RunState.Rng.CombatCardSelection.NextItem(candidates);
            candidates.Remove(pick);
            pick.EnergyCost.SetThisTurnOrUntilPlayed(0);
        }
    }
}

// 黄昏之交衣（v0.4.39 问题39：升金；效果="弃牌堆中每有1张「光道」牌，获得1层暮光"，消耗；
// 敲后去掉消耗。本批反馈追加：被从卡组弃置时，获得"本回合打出「光道」牌得2格挡（敲后3）"效果
// ——即光之回弹效果的临时版（TwilightGarbPower，回合结束自动移除））
[RegisterCard(typeof(LightswornCardPool))]
public class TwilightGarb : LsCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars => [new DynamicVar("Guard", 2m)];

    public override IEnumerable<CardKeyword> CanonicalKeywords => [CardKeyword.Exhaust, LsKeywords.Twilight];

    public TwilightGarb() : base(1, CardType.Skill, CardRarity.Rare, TargetType.Self) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        int count = LsUtil.DiscardPile(this).Cards.Count(LsUtil.IsLs);
        if (count > 0)
            await PowerCmd.Apply<TwilightPower>(choiceContext, Owner.Creature, count, Owner.Creature, this);
    }

    // 问题39：敲后去掉消耗；本批追加：被从卡组弃置时获得 2→3 格挡的临时回弹能力
    protected override void OnUpgrade()
    {
        RemoveKeyword(CardKeyword.Exhaust);
        DynamicVars["Guard"].UpgradeValueBy(1);
    }

    // 本批追加：被从卡组弃置时（弃光/卡组弃置，任意来源）→ 获得本回合的"打出光道牌得格挡"效果
    public override async Task AfterCardChangedPiles(CardModel card, PileType oldPileType, AbstractModel? clonedBy)
    {
        if (card != this) return;
        if (oldPileType != PileType.Draw || card.Pile?.Type != PileType.Discard) return;
        if (Owner.Creature.CombatState == null) return;
        await PowerCmd.Apply<TwilightGarbPower>(new BlockingPlayerChoiceContext(), Owner.Creature,
            (int)DynamicVars["Guard"].BaseValue, Owner.Creature, this);
    }
}

// 闪光之幻想（本批反馈问题10：升金；弃光2→3；不再获得格挡改为造成伤害（数值公式照旧=所选牌的基础伤害+0/3）；
// 斩杀时额外获得一次卡牌奖励——原版 TheHunt 范式：CombatRoom.AddExtraReward + CardReward）
[RegisterCard(typeof(LightswornCardPool))]
public class FlashFantasy : LsCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars =>
    [
        new DynamicVar("Mill", 3m),
        new DynamicVar("Bonus", 0m),
    ];
    public override IEnumerable<CardKeyword> CanonicalKeywords => [LsKeywords.Mill];

    public FlashFantasy() : base(1, CardType.Skill, CardRarity.Rare, TargetType.AnyEnemy) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        // 先弃光（弃掉的牌本也可以作为下面的候选）
        await LsUtil.Mill(choiceContext, this, (int)DynamicVars["Mill"].BaseValue);
        List<CardModel> candidates = LsUtil.DiscardPile(this).Cards
            .Where(c => LsUtil.IsLs(c) && c.Type == CardType.Attack).ToList();
        CardModel? pick = (await LsUtil.PickFromList(choiceContext, Owner, candidates,
            "LIGHTSWORN_FLASH_PICK", 1)).FirstOrDefault();
        if (pick == null) return;
        // "基础伤害"=该卡当前面板伤害（DamageVar 的 BaseValue 含敲后增量）；本mod攻击牌均注册 Damage 变量
        decimal damage = pick.DynamicVars["Damage"].BaseValue + DynamicVars["Bonus"].BaseValue;
        if (damage <= 0) return;
        // 问题10：造成伤害；斩杀时额外获得一次卡牌奖励（原版判例：TheHunt/Feed 的 WasTargetKilled+致命判定）
        Creature? target = cardPlay.Target;
        if (target == null) return;
        bool shouldTriggerFatal = target.Powers.All(p => p.ShouldOwnerDeathTriggerFatal());
        AttackCommand attack = await DamageCmd.Attack(damage).FromCardCompat(this, cardPlay)
            .Targeting(target).Execute(choiceContext);
        if (!shouldTriggerFatal) return;
        if (!attack.Results.SelectMany(r => r).Any(r => r.WasTargetKilled)) return;
        if (Owner.RunState.CurrentRoom is CombatRoom combatRoom)
            combatRoom.AddExtraReward(Owner, new CardReward(
                CardCreationOptions.ForRoom(Owner, combatRoom.RoomType), 3, Owner));
    }

    // 敲后伤害+3（Bonus 0→3，文本用 {IfUpgraded:show:（+3）|} 展示）
    protected override void OnUpgrade() => DynamicVars["Bonus"].UpgradeValueBy(3);
}

// 黄昏之双龙（本批反馈问题27：生成的裁决/惩戒去掉「虚无」；敲后不再增加除光（固定4）；
// 敲后生成的裁决和惩戒加「保留」）
// ⚠ 已知问题4（v0.5.4，用户："卡牌文本没有单独的弃光/除光/暮光"）：
//   本卡曾静态声明 `[LsKeywords.Mill, LsKeywords.Banish]`，卡面恒定叠两行孤立短词
//   "[gold]弃光[/gold]。" + "[gold]除光[/gold]。"。——用户点名的正是这种"独立词条行"。
//   全局收敛（不是本卡单独处理）：三个机制关键词 MILL/BANISH/TWILIGHT 已改为
//   `ModKeywordCardDescriptionPlacement.None`（Ls.cs），**任何卡都不再注入词条行**；
//   机制名只在正文里以 `[gold]弃光[/gold]{Mill:diff()}` 内联出现（官方"重放"范式）。
//   因此本卡**恢复常规声明**（声明与否只影响悬浮提示，不影响卡面文本/逻辑——
//   LsKeywords.Mill/Banish 在 mod 内无任何读取点，grep `Keywords.Contains(LsKeywords` 零命中）：
//   声明的关键词由原版 CardModel.HoverTips 自动带出提示（详见 LightswornContent.cs LsCard 注释），
//   不需要 AdditionalHoverTips 手工挂载（那会与原版自动提示**重复**）。
[RegisterCard(typeof(LightswornCardPool))]
public class TwinTwilightDragon : LsCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars => [new DynamicVar("Mill", 4m)];
    public override IEnumerable<CardKeyword> CanonicalKeywords => [LsKeywords.Mill, LsKeywords.Banish];

    public TwinTwilightDragon() : base(1, CardType.Skill, CardRarity.Uncommon, TargetType.Self) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        if (PileType.Hand.GetPile(Owner).Cards.Any(c => c is PunishDragon))
        {
            // 手牌中有惩戒之龙：从弃牌堆将1张裁决之龙加入手牌，然后弃光4
            CardModel? pick = await LsUtil.PickFromDiscard(choiceContext, this, c => c is JudgementDragon);
            if (pick != null)
                await CardPileCmd.Add(pick, PileType.Hand);
            await LsUtil.Mill(choiceContext, this, (int)DynamicVars["Mill"].BaseValue);
        }
        else
        {
            // 手牌中没有惩戒之龙：生成1张裁决之龙和1张惩戒之龙到弃牌堆。
            // 问题27：去掉虚无（不再回合结束消耗）。
            // 本批反馈：两条龙的「保留」改由强化版自带，敲后改为生成**强化后的对应卡**
            // （范式同融合产出：UpgradeInternal + FinalizeUpgradeInternal）。
            CardModel? jd = await LsUtil.CreateToken<JudgementDragon>(choiceContext, this, PileType.Discard);
            CardModel? pd = await LsUtil.CreateToken<PunishDragon>(choiceContext, this, PileType.Discard);
            if (IsUpgraded)
            {
                if (jd is { IsUpgraded: false })
                {
                    jd.UpgradeInternal();
                    jd.FinalizeUpgradeInternal();
                }
                if (pd is { IsUpgraded: false })
                {
                    pd.UpgradeInternal();
                    pd.FinalizeUpgradeInternal();
                }
            }
        }
    }

    // 自己被光道卡从卡组弃掉时：从弃牌堆将1张惩戒之龙加入手牌，然后除光4（问题27：敲后不再增加为6）
    protected internal override async Task OnMilledByLsCard(PlayerChoiceContext ctx, CardModel source)
    {
        CardModel? pick = await LsUtil.PickFromDiscard(ctx, this, c => c is PunishDragon);
        if (pick == null) return;
        await CardPileCmd.Add(pick, PileType.Hand);
        await LsUtil.Banish(ctx, this, 4);
    }

    // 问题11：卡牌停留时预览关联牌（裁决之龙/惩戒之龙）卡图
    // （「弃光」「除光」的悬浮提示由原版自动带出——上面已恢复关键词声明，勿再手工挂）
    protected override IEnumerable<IHoverTip> AdditionalHoverTips =>
        HoverTipFactory.FromCardWithCardHoverTips<JudgementDragon>()
            .Concat(HoverTipFactory.FromCardWithCardHoverTips<PunishDragon>());

    protected override void OnUpgrade() { }
}

// ================= 非本家 =================

// 妖精传姬-白雪（1费正常使用；费用不为0时将0费的雪之化身加入手牌；问题11：停留时预览雪之化身卡图。
// v0.4.36：稀有度 Uncommon→Rare（金卡））
[RegisterCard(typeof(LightswornCardPool))]
public class Snow : LsCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars => [new DamageVar(9, ValueProp.Move)];

    protected override IEnumerable<IHoverTip> AdditionalHoverTips =>
        HoverTipFactory.FromCardWithCardHoverTips<SnowSpirit>();

    public Snow() : base(1, CardType.Skill, CardRarity.Rare, TargetType.AnyEnemy) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await DamageCmd.Attack(DynamicVars.Damage.BaseValue).FromCardCompat(this, cardPlay)
            .Targeting(cardPlay.Target!).Execute(choiceContext);
        if (EnergyCost.GetResolved() > 0)
        {
            CardModel? token = Owner.Creature.CombatState?.CreateCard<SnowSpirit>(Owner);
            if (token != null)
                await CardPileCmd.AddGeneratedCardToCombat(token, PileType.Hand, Owner);
        }
    }

    protected override void OnUpgrade() => DynamicVars.Damage.UpgradeValueBy(4);
}

// 妖精传姬-白雪 雪之化身（0费令牌：造成伤害+从弃牌堆手动选7张消耗。
// 本批问题18：必须消耗弃牌堆7张才能打出（打出条件=弃牌堆≥7张），稀有度Token→金卡）
[RegisterCard(typeof(LightswornCardPool))]
public class SnowSpirit : LsCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars => [new DamageVar(18, ValueProp.Move)];

    public SnowSpirit() : base(0, CardType.Attack, CardRarity.Rare, TargetType.AnyEnemy, showInCardLibrary: false) { }

    // 稀有度改金卡后不再靠 Token 稀有度被战斗生成过滤，由本属性兜底（「你必须玩游戏王」等生成池）
    public override bool CanBeGeneratedInCombat => false;

    public override IEnumerable<CardKeyword> CanonicalKeywords => [CardKeyword.Exhaust];

    // 问题18：弃牌堆有7张以上牌时才能打出
    protected override bool IsPlayable => base.IsPlayable && LsUtil.DiscardPile(this).Cards.Count >= 7;
    protected override bool ShouldGlowGoldInternal => IsPlayable;

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await DamageCmd.Attack(DynamicVars.Damage.BaseValue).FromCardCompat(this, cardPlay)
            .Targeting(cardPlay.Target!).Execute(choiceContext);
        await LsUtil.BurnSelectedFromDiscard(choiceContext, this, 7);
    }

    protected override void OnUpgrade() { }
}

// 古卫兵 阿基多（本批反馈：弃光5（敲后7）；其中每有3张技能牌，抽1张牌（原"2张以上→抽2"作废）；
// 追加"被弃置时自动打出"）
[RegisterCard(typeof(LightswornCardPool))]
public class Agido : LsCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars => [new DynamicVar("Mill", 5m)];
    public override IEnumerable<CardKeyword> CanonicalKeywords => [LsKeywords.Mill];
    protected override HashSet<CardTag> CanonicalTags => [Ls.EarthAngel];

    public Agido() : base(1, CardType.Skill, CardRarity.Rare, TargetType.Self) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        List<CardModel> milled = await LsUtil.Mill(choiceContext, this, (int)DynamicVars["Mill"].BaseValue);
        // 本批：每有3张技能牌被弃置→抽1张牌（向下取整，0则不抽）
        int draws = milled.Count(c => c.Type == CardType.Skill) / 3;
        if (draws > 0)
            await CardPileCmd.Draw(choiceContext, draws, Owner);
    }

    protected override void OnUpgrade() => DynamicVars["Mill"].UpgradeValueBy(2);

    // 问题33：追加——被弃置时（弃光/手牌弃置）自动打出
    public override async Task AfterCardChangedPiles(CardModel card, PileType oldPileType, AbstractModel? clonedBy)
    {
        if (card == this && oldPileType == PileType.Draw && card.Pile?.Type == PileType.Discard)
            await LsUtil.AutoPlayOnDiscard(this);
    }

    public override async Task AfterCardDiscarded(PlayerChoiceContext choiceContext, CardModel card)
    {
        if (card == this && card.Pile?.Type == PileType.Discard)
            await LsUtil.AutoPlayOnDiscard(this);
    }
}

// 古尖兵 凯尔柏克（本批反馈：弃光5（敲后7）；其中每有3张攻击牌，抽1张牌（原"2张以上→抽2"作废）；
// 追加"被弃置时自动打出"）
[RegisterCard(typeof(LightswornCardPool))]
public class Kelbek : LsCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars => [new DynamicVar("Mill", 5m)];
    public override IEnumerable<CardKeyword> CanonicalKeywords => [LsKeywords.Mill];
    protected override HashSet<CardTag> CanonicalTags => [Ls.EarthAngel];

    public Kelbek() : base(1, CardType.Skill, CardRarity.Rare, TargetType.Self) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        List<CardModel> milled = await LsUtil.Mill(choiceContext, this, (int)DynamicVars["Mill"].BaseValue);
        // 本批：每有3张攻击牌被弃置→抽1张牌（向下取整，0则不抽）
        int draws = milled.Count(c => c.Type == CardType.Attack) / 3;
        if (draws > 0)
            await CardPileCmd.Draw(choiceContext, draws, Owner);
    }

    protected override void OnUpgrade() => DynamicVars["Mill"].UpgradeValueBy(2);

    // 问题33：追加——被弃置时（弃光/手牌弃置）自动打出
    public override async Task AfterCardChangedPiles(CardModel card, PileType oldPileType, AbstractModel? clonedBy)
    {
        if (card == this && oldPileType == PileType.Draw && card.Pile?.Type == PileType.Discard)
            await LsUtil.AutoPlayOnDiscard(this);
    }

    public override async Task AfterCardDiscarded(PlayerChoiceContext choiceContext, CardModel card)
    {
        if (card == this && card.Pile?.Type == PileType.Discard)
            await LsUtil.AutoPlayOnDiscard(this);
    }
}

// 宿神像 凯尔多（回弃牌堆任意2张牌到卡组，抽1；本批反馈问题17：若抽到技能牌，其费用改为0
// ——原"费用-1仅一次"作废。敲后：回3张。Picks 变量驱动文案与升级预览）
[RegisterCard(typeof(LightswornCardPool))]
public class Keldo : LsCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars => [new DynamicVar("Picks", 2m)];

    public Keldo() : base(0, CardType.Skill, CardRarity.Uncommon, TargetType.Self) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        List<CardModel> candidates = LsUtil.DiscardPile(this).Cards.ToList();
        int want = Math.Min((int)DynamicVars["Picks"].BaseValue, candidates.Count);
        if (want > 0)
        {
            List<CardModel> chosen = await LsUtil.PickSomeFromList(choiceContext, Owner, candidates,
                "LIGHTSWORN_TO_DECK", want, want);
            foreach (CardModel card in chosen)
                await CardPileCmd.Add(card, PileType.Draw, CardPilePosition.Random);
        }
        // 记录抽到的牌（抽牌堆顶；堆空触发洗牌时跳过降费）
        CardModel? drawn = LsUtil.DrawPile(this).Cards.FirstOrDefault();
        await CardPileCmd.Draw(choiceContext, 1, Owner);
        // 问题17：抽到技能牌→本次费用变为0（SetUntilPlayed(0)，直到打出）
        if (drawn != null && drawn.Type == CardType.Skill && drawn.Pile?.Type == PileType.Hand)
            drawn.EnergyCost.SetUntilPlayed(0);
    }

    protected override void OnUpgrade() => DynamicVars["Picks"].UpgradeValueBy(1);
    protected override HashSet<CardTag> CanonicalTags => [Ls.EarthAngel];
}

// 剑神官 姆多拉（回弃牌堆任意2张牌到卡组，抽1；本批反馈问题17：若抽到攻击牌，其费用改为0
// ——原"费用-1仅一次"作废。敲后：回3张）
[RegisterCard(typeof(LightswornCardPool))]
public class Mudora : LsCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars => [new DynamicVar("Picks", 2m)];

    public Mudora() : base(0, CardType.Skill, CardRarity.Uncommon, TargetType.Self) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        List<CardModel> candidates = LsUtil.DiscardPile(this).Cards.ToList();
        int want = Math.Min((int)DynamicVars["Picks"].BaseValue, candidates.Count);
        if (want > 0)
        {
            List<CardModel> chosen = await LsUtil.PickSomeFromList(choiceContext, Owner, candidates,
                "LIGHTSWORN_TO_DECK", want, want);
            foreach (CardModel card in chosen)
                await CardPileCmd.Add(card, PileType.Draw, CardPilePosition.Random);
        }
        CardModel? drawn = LsUtil.DrawPile(this).Cards.FirstOrDefault();
        await CardPileCmd.Draw(choiceContext, 1, Owner);
        // 问题17：抽到攻击牌→本次费用变为0（SetUntilPlayed(0)，直到打出）
        if (drawn != null && drawn.Type == CardType.Attack && drawn.Pile?.Type == PileType.Hand)
            drawn.EnergyCost.SetUntilPlayed(0);
    }

    protected override void OnUpgrade() => DynamicVars["Picks"].UpgradeValueBy(1);
    protected override HashSet<CardTag> CanonicalTags => [Ls.EarthAngel];
}

// 邻家割草（问题7：稀有度改金色）
[RegisterCard(typeof(LightswornCardPool))]
public class LawnMowing : LsCard
{
    // 已知问题4（v0.5.4）：正文内联的"[gold]弃光[/gold]"（数量=抽牌堆一半）需要悬浮提示可查
    public override IEnumerable<CardKeyword> CanonicalKeywords => [LsKeywords.Mill];

    public LawnMowing() : base(1, CardType.Skill, CardRarity.Rare, TargetType.Self) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        int count = LsUtil.DrawPile(this).Cards.Count / 2;
        await LsUtil.Mill(choiceContext, this, count);
        if (IsUpgraded)
            await CardPileCmd.Draw(choiceContext, 1, Owner);
    }

    protected override void OnUpgrade() { }
}

// 欧尼斯特（强化后翻倍2次：Times 变量驱动文案与升级预览）
[RegisterCard(typeof(LightswornCardPool))]
public class Honest : LsCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars => [new DynamicVar("Times", 1m)];

    public Honest() : base(0, CardType.Skill, CardRarity.Uncommon, TargetType.Self) { }
    public override IEnumerable<CardKeyword> CanonicalKeywords => [CardKeyword.Exhaust];

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await PowerCmd.Apply<HonestPower>(choiceContext, Owner.Creature, (int)DynamicVars["Times"].BaseValue, Owner.Creature, this);
    }

    protected override void OnUpgrade() => DynamicVars["Times"].UpgradeValueBy(1);
}
