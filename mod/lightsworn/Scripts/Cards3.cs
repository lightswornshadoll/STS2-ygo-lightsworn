using MegaCrit.Sts2.Core.CardSelection;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Commands.Builders;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;

namespace Lightsworn;

// ================= 本家·稀有 =================

// 光道召唤师 露米娜丝（问题7：弃光→追加丢弃1张手牌→从弃牌堆拿「光道」牌变0费；升级后0费。
// 问题17：拿取数1→2。问题11：回调为1+10格挡。问题3：再次回调——去掉格挡，拿取2张。
// v0.4.36：敲前拿1、敲后拿2，升级不再变为0费（同暮光道萨满范式）。
// 本批反馈：必须弃置1张手牌才能发动拿回——手牌只剩自己时不能再白嫖拿牌（打出条件+运行期双保险））
[RegisterCard(typeof(LightswornCardPool))]
public class Lumina : LsCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars =>
    [
        new DynamicVar("Mill", 3m),
        new DynamicVar("Picks", 1m),
    ];
    public override IEnumerable<CardKeyword> CanonicalKeywords => [LsKeywords.Mill];

    public Lumina() : base(1, CardType.Skill, CardRarity.Rare, TargetType.Self) { }

    // 本批反馈（同雪之化身范式）：手牌中除自己外还有牌（可弃）时才能打出
    protected override bool IsPlayable =>
        base.IsPlayable && PileType.Hand.GetPile(Owner).Cards.Any(c => !ReferenceEquals(c, this));
    protected override bool ShouldGlowGoldInternal => IsPlayable;

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await LsUtil.Mill(choiceContext, this, (int)DynamicVars["Mill"].BaseValue);
        // 丢弃1张手牌（任意牌）——本批反馈：这是后续拿牌的代价，没弃成就不拿
        CardSelectorPrefs prefs = new(CardSelectorPrefs.DiscardSelectionPrompt, 1);
        List<CardModel> chosen = (await CardSelectCmd.FromHandForDiscard(choiceContext, Owner, prefs, null, this)).ToList();
        if (chosen.Count == 0) return;   // 未弃置=拿牌效果不发动（IsPlayable 已挡常态，双保险）
        await CardCmd.Discard(choiceContext, chosen);
        // 从弃牌堆拿「光道」牌（刚丢弃的手牌若是光道牌也可选），本回合0费
        int picks = (int)DynamicVars["Picks"].BaseValue;
        for (int i = 0; i < picks; i++)
        {
            CardModel? pick = await LsUtil.PickFromDiscard(choiceContext, this, LsUtil.IsLs);
            if (pick == null) break;
            await CardPileCmd.Add(pick, PileType.Hand);
            pick.EnergyCost.SetUntilPlayed(0);
        }
    }

    // v0.4.36：升级=拿取数1→2（原"费用1→0"作废，升级后仍是1费）
    protected override void OnUpgrade() => DynamicVars["Picks"].UpgradeValueBy(1);
}

// 暮光道萨满 露米娜丝（用户指定设计；本批问题22：回调——敲前拿1张、敲后拿2张，不再获得格挡（原10格挡删除），
// 升级=拿取数1→2（原敲后0费作废）。
// 本批反馈：必须消耗1张「光道」才能发动拿回——弃牌堆没有光道不能再白拿（打出条件+运行期双保险））
[RegisterCard(typeof(LightswornCardPool))]
public class TwilightLumina : LsCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars =>
    [
        new DynamicVar("Picks", 1m),
        new DynamicVar("Twilight", 1m),
    ];

    public override IEnumerable<CardKeyword> CanonicalKeywords => [LsKeywords.Twilight];

    public TwilightLumina() : base(1, CardType.Skill, CardRarity.Rare, TargetType.Self) { }

    // 本批反馈（同雪之化身范式）：弃牌堆中有「光道」牌（可消耗）时才能打出
    protected override bool IsPlayable =>
        base.IsPlayable && LsUtil.DiscardPile(this).Cards.Any(LsUtil.IsLs);
    protected override bool ShouldGlowGoldInternal => IsPlayable;

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        // 消耗墓地1张光道——本批反馈：这是后续拿回的代价，没消耗就不拿
        CardModel? burned = await LsUtil.ExhaustOneFromDiscard(choiceContext, this, LsUtil.IsLs);
        if (burned != null)
        {
            // 从消耗堆一次选{Picks}张光道拿回（0费）
            List<CardModel> candidates = LsUtil.ExhaustPile(this).Cards.Where(LsUtil.IsLs).ToList();
            List<CardModel> picked = await LsUtil.PickFromList(choiceContext, Owner, candidates,
                "LIGHTSWORN_TO_HAND", (int)DynamicVars["Picks"].BaseValue);
            foreach (CardModel card in picked)
            {
                await CardPileCmd.Add(card, PileType.Hand);
                card.EnergyCost.SetUntilPlayed(0);
            }
        }
        await PowerCmd.Apply<TwilightPower>(choiceContext, Owner.Creature, (int)DynamicVars["Twilight"].BaseValue, Owner.Creature, this);
    }

    // 问题22：升级=拿取数1→2
    protected override void OnUpgrade() => DynamicVars["Picks"].UpgradeValueBy(1);
}

// 光道主·大天使 米迦勒（用户拍板：无打出条件；打出先造成伤害，再回收弃牌堆「光道」牌
// （非光道不回收），每回收1张获得2点格挡（问题11）；问题2：稀有度改非普通）
[RegisterCard(typeof(LightswornCardPool))]
public class Michael : LsCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars => [new DamageVar(20, ValueProp.Move)];

    public Michael() : base(2, CardType.Attack, CardRarity.Uncommon, TargetType.AnyEnemy) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await DamageCmd.Attack(DynamicVars.Damage.BaseValue).FromCardCompat(this, cardPlay)
            .Targeting(cardPlay.Target!).Execute(choiceContext);
        // 回收弃牌堆中的「光道」牌（ReferenceEquals 防御性排除自身），加到抽牌堆底。
        // ⚠ 绝不能调 CardPileCmd.Shuffle——它的语义是"把整个弃牌堆洗回抽牌堆"（前两轮反馈
        // 误修于此：过滤对了但 Shuffle 把非光道牌也全洗了回去）。问题11：每回收1张获得2点格挡。
        List<CardModel> lsInDiscard = LsUtil.DiscardPile(this).Cards
            .Where(c => LsUtil.IsLs(c) && !ReferenceEquals(c, this))
            .ToList();
        if (lsInDiscard.Count > 0)
        {
            foreach (CardModel card in lsInDiscard)
                await CardPileCmd.Add(card, PileType.Draw);
            await CreatureCmd.GainBlock(Owner.Creature, lsInDiscard.Count * 2, ValueProp.Unpowered, null);
        }
    }

    protected override void OnUpgrade() => DynamicVars.Damage.UpgradeValueBy(6);
}

// 光道雅典娜 密涅瓦（问题3重做：改为攻击牌：选弃2张光道→可选消耗弃牌堆光道至多4张（x张）→弃光x→造成伤害）
// 问题4：两处多张选择都改为一个界面一次选完；问题11：2费，伤害18，敲后23
[RegisterCard(typeof(LightswornCardPool))]
public class MinervaExalted : LsCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars => [new DamageVar(18, ValueProp.Move)];
    public override IEnumerable<CardKeyword> CanonicalKeywords => [LsKeywords.Mill];

    public MinervaExalted() : base(2, CardType.Attack, CardRarity.Rare, TargetType.AnyEnemy) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        // ① 从卡组一次选2张「光道」牌弃置（不足2张则有多少选多少），逐张触发光道弃光钩子+加洛斯
        List<CardModel> drawCandidates = LsUtil.DrawPile(this).Cards.Where(LsUtil.IsLs).ToList();
        List<CardModel> toMill = await LsUtil.PickFromList(choiceContext, Owner, drawCandidates,
            "LIGHTSWORN_TO_DISCARD", 2);
        if (toMill.Count > 0)
            await LsUtil.MillSelected(choiceContext, this, toMill);

        // ② 可选消耗弃牌堆中的「光道」牌，至多4张一次选完（x=实际消耗数）；可全不选
        List<CardModel> discardCandidates = LsUtil.DiscardPile(this).Cards.Where(LsUtil.IsLs).ToList();
        List<CardModel> toBurn = await LsUtil.PickSomeFromList(choiceContext, Owner, discardCandidates,
            "LIGHTSWORN_TO_EXHAUST", 0, 4);
        foreach (CardModel card in toBurn)
            await LsCompat.ExhaustCompat(choiceContext, card);
        int x = toBurn.Count;

        // ③ 弃光x
        if (x > 0)
            await LsUtil.Mill(choiceContext, this, x);

        // ④ 造成伤害
        await DamageCmd.Attack(DynamicVars.Damage.BaseValue).FromCardCompat(this, cardPlay)
            .Targeting(cardPlay.Target!).Execute(choiceContext);
    }

    protected override void OnUpgrade() => DynamicVars.Damage.UpgradeValueBy(5);
}

// 光道圣女 密涅瓦（问题5：若有敌人意图为攻击，再弃光N，每弃1张光道牌给该敌人1层虚弱；
// 问题5本批：两个弃光共用同一数值，敲后同时变4）
[RegisterCard(typeof(LightswornCardPool))]
public class MinervaSaint : LsCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars => [new DynamicVar("Mill", 3m)];
    public override IEnumerable<CardKeyword> CanonicalKeywords => [LsKeywords.Mill];

    public MinervaSaint() : base(1, CardType.Skill, CardRarity.Rare, TargetType.Self) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        List<CardModel> milled = await LsUtil.Mill(choiceContext, this, (int)DynamicVars["Mill"].BaseValue);
        int count = milled.Count(LsUtil.IsLs);
        if (count > 0)
            await CardPileCmd.Draw(choiceContext, count, Owner);

        // 目标敌人：本卡为自体目标，cardPlay.Target 通常是玩家或空；优先用 Target（若为意图攻击的敌人），
        // 否则任取一名意图为攻击的敌人。意图判定同原版 MonsterModel.IntendsToAttack（Attack/DeathBlow）。
        Creature? enemy = cardPlay.Target;
        if (enemy == null || !(enemy.Monster?.IntendsToAttack ?? false))
        {
            enemy = Owner.Creature.CombatState!.HittableEnemies
                .FirstOrDefault(e => e.Monster?.IntendsToAttack ?? false);
        }
        if (enemy != null && (enemy.Monster?.IntendsToAttack ?? false))
        {
            // 问题5：再弃光与首次弃光共用 {Mill} 变量，敲后两处同时+1（都变4）
            List<CardModel> extra = await LsUtil.Mill(choiceContext, this, (int)DynamicVars["Mill"].BaseValue);
            int weak = extra.Count(LsUtil.IsLs);
            if (weak > 0)
                await PowerCmd.Apply<MegaCrit.Sts2.Core.Models.Powers.WeakPower>(
                    choiceContext, enemy, weak, Owner.Creature, this);
        }
    }

    protected override void OnUpgrade() => DynamicVars["Mill"].UpgradeValueBy(1);
}

// 裁决之龙（0费；弃牌堆中存在4种不同「光道」牌时才能打出，不再算消耗堆。本批：稀有度改蓝卡）
[RegisterCard(typeof(LightswornCardPool))]
public class JudgementDragon : LsCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars =>
    [
        new DamageVar(22, ValueProp.Move),
        new DynamicVar("Mill", 4m),
    ];
    public override IEnumerable<CardKeyword> CanonicalKeywords => [LsKeywords.Mill];

    public JudgementDragon() : base(0, CardType.Attack, CardRarity.Uncommon, TargetType.AllEnemies) { }

    protected override bool IsPlayable => LsUtil.DistinctLsInDiscard(this) >= 4;
    protected override bool ShouldGlowGoldInternal => IsPlayable;

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await LsUtil.Mill(choiceContext, this, (int)DynamicVars["Mill"].BaseValue);
        foreach (Creature enemy in Owner.Creature.CombatState!.HittableEnemies.ToList())
        {
            await DamageCmd.Attack(DynamicVars.Damage.BaseValue).FromCardCompat(this, cardPlay)
                .Targeting(enemy).Execute(choiceContext);
        }
    }

    protected override void OnUpgrade() => DynamicVars.Damage.UpgradeValueBy(6);
}

// 惩戒之龙（问题5重做：0费；消耗堆中存在4种以上「光道」牌时才能打出；将弃牌堆与消耗堆所有非光道卡
// 返回卡组，每有一张所有敌人获得随机1层负面状态；造成伤害并获得暮光）
[RegisterCard(typeof(LightswornCardPool))]
public class PunishDragon : LsCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars =>
    [
        new DamageVar(22, ValueProp.Move),
        new DynamicVar("Twilight", 1m),
    ];

    public PunishDragon() : base(0, CardType.Attack, CardRarity.Uncommon, TargetType.AllEnemies) { }

    public override IEnumerable<CardKeyword> CanonicalKeywords => [LsKeywords.Twilight];

    protected override bool IsPlayable => LsUtil.DistinctLsInExhaust(this) >= 4;
    protected override bool ShouldGlowGoldInternal => IsPlayable;

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        // 将弃牌堆与消耗堆中的所有非「光道」卡返回抽牌堆
        List<CardModel> nonLs = LsUtil.DiscardPile(this).Cards.Where(c => !LsUtil.IsLs(c))
            .Concat(LsUtil.ExhaustPile(this).Cards.Where(c => !LsUtil.IsLs(c))).ToList();
        foreach (CardModel card in nonLs)
            await CardPileCmd.Add(card, PileType.Draw);
        // 每有一张，所有敌人获得随机一层负面状态（人工制品可抵挡）
        await LsUtil.ApplyRandomDebuffs(choiceContext, Owner,
            Owner.Creature.CombatState!.HittableEnemies.ToList(), nonLs.Count);
        // 造成伤害
        foreach (Creature enemy in Owner.Creature.CombatState!.HittableEnemies.ToList())
        {
            await DamageCmd.Attack(DynamicVars.Damage.BaseValue).FromCardCompat(this, cardPlay)
                .Targeting(enemy).Execute(choiceContext);
        }
        // 获得1层暮光
        await PowerCmd.Apply<TwilightPower>(choiceContext, Owner.Creature,
            (int)DynamicVars["Twilight"].BaseValue, Owner.Creature, this);
    }

    protected override void OnUpgrade() => DynamicVars.Damage.UpgradeValueBy(6);
}

// 神光之龙（0费消耗；弃牌堆存在「裁决之龙」和「惩戒之龙」时才能打出；
// 消耗弃牌堆所有卡→对所有敌人造成22点×3次伤害（敲后26点×3）并施加3层虚弱和易伤→从消耗堆把两种龙各1张加入手牌。
// 本批反馈问题24：伤害改成22x3/26x3（原生多段攻击 WithHitCount，全部段落吃活力加成）；
// 敲后保留（问题20的「保留」升级不变）。原型=YGO 46186135；卡名不含「光道」，不打光道标，同裁决/惩戒）
[RegisterCard(typeof(LightswornCardPool))]
public class ShiningDragon : LsCard
{
    protected override IEnumerable<DynamicVar> CanonicalVars =>
    [
        new DamageVar(22, ValueProp.Move),
        new DynamicVar("Hits", 3m),
    ];
    public override IEnumerable<CardKeyword> CanonicalKeywords => [CardKeyword.Exhaust];

    public ShiningDragon() : base(0, CardType.Attack, CardRarity.Rare, TargetType.AllEnemies) { }

    // 问题11：卡牌停留时预览关联牌（裁决之龙/惩戒之龙）卡图
    protected override IEnumerable<IHoverTip> AdditionalHoverTips =>
        HoverTipFactory.FromCardWithCardHoverTips<JudgementDragon>()
            .Concat(HoverTipFactory.FromCardWithCardHoverTips<PunishDragon>());

    protected override bool IsPlayable =>
        LsUtil.DiscardPile(this).Cards.Any(c => c is JudgementDragon) &&
        LsUtil.DiscardPile(this).Cards.Any(c => c is PunishDragon);
    protected override bool ShouldGlowGoldInternal => IsPlayable;

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        // ① 消耗弃牌堆中的所有卡（ReferenceEquals 防御性排除自身）
        List<CardModel> inDiscard = LsUtil.DiscardPile(this).Cards
            .Where(c => !ReferenceEquals(c, this)).ToList();
        foreach (CardModel card in inDiscard)
            await LsCompat.ExhaustCompat(choiceContext, card);
        // ② 对所有敌人造成伤害（问题24：22×3/26×3，原生多段攻击让全部段落吃活力）
        await DamageCmd.Attack(DynamicVars.Damage.BaseValue).FromCardCompat(this, cardPlay)
            .TargetingAllOpponents(Owner.Creature.CombatState!)
            .WithHitCount((int)DynamicVars["Hits"].BaseValue)
            .Execute(choiceContext);
        // ③ 所有敌人施加3层虚弱和3层易伤
        List<Creature> enemies = Owner.Creature.CombatState!.HittableEnemies.ToList();
        if (enemies.Count > 0)
        {
            await PowerCmd.Apply<MegaCrit.Sts2.Core.Models.Powers.WeakPower>(
                choiceContext, enemies, 3, Owner.Creature, this);
            await PowerCmd.Apply<MegaCrit.Sts2.Core.Models.Powers.VulnerablePower>(
                choiceContext, enemies, 3, Owner.Creature, this);
        }
        // ④ 从消耗堆将1张裁决之龙、1张惩戒之龙加入手牌（手牌满则留在消耗堆）
        if (LsUtil.HandHasSpace(this))
        {
            CardModel? jd = LsUtil.ExhaustPile(this).Cards.FirstOrDefault(c => c is JudgementDragon);
            if (jd != null)
                await CardPileCmd.Add(jd, PileType.Hand);
            if (LsUtil.HandHasSpace(this))
            {
                CardModel? pd = LsUtil.ExhaustPile(this).Cards.FirstOrDefault(c => c is PunishDragon);
                if (pd != null)
                    await CardPileCmd.Add(pd, PileType.Hand);
            }
        }
    }

    // 敲后：伤害22→26（段数不变）并获得「保留」
    protected override void OnUpgrade()
    {
        DynamicVars.Damage.UpgradeValueBy(4);
        AddKeyword(CardKeyword.Retain);
    }
}
