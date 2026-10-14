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

// ================= 神影依（全部为战斗内Token：0费、离开弃牌堆时消耗（被效果从消耗堆加入手牌则保留）、带影依标可当影融素材） =================
// 生成规则：每回合每张只能生成1次（LsUtil.ShaddollFusion / PickAndGenerateShaddoll 内置锁）；
// 文迪戈特殊=本场战斗只能生成1次。生成时触发卡已升级 → 强化版；「第2次打出时消耗」已删除（本批问题35）。
// 检索规则（v0.4.21 用户点名）：神影依「拿影依卡」的效果一律不能拿神影依（防米德拉什回费等检索循环），
// 普通影依卡的检索效果不受限，仍可从弃牌堆拿神影依。

// 神影依·米德拉什（0费攻击Token：打6/9，回3费（本批反馈问题1：回调2→3），从弃牌堆将1张影依技能加入手牌）
[RegisterCard(typeof(LightswornCardPool))]
public sealed class ElShaddollWinda : ShaddollToken
{
    protected override IEnumerable<DynamicVar> CanonicalVars => [new DamageVar(6, ValueProp.Move)];

    public ElShaddollWinda() : base(0, CardType.Attack, CardRarity.Token, TargetType.AnyEnemy) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await DamageCmd.Attack(DynamicVars.Damage.BaseValue).FromCardCompat(this, cardPlay)
            .Targeting(cardPlay.Target!).Execute(choiceContext);
        // 问题1：回调回费2→3
        await PlayerCmd.GainEnergy(3m, Owner);
        if (!LsUtil.HandHasSpace(this)) return;
        CardModel? pick = await LsUtil.PickFromDiscard(choiceContext, this,
            c => LsUtil.IsShaddollSkill(c) && !LsUtil.IsElShaddollToken(c));
        if (pick != null)
            await CardPileCmd.Add(pick, PileType.Hand);
    }

    protected override void OnUpgrade() => DynamicVars.Damage.UpgradeValueBy(3);
}

// 神影依·拿非利（0费攻击Token：打16/22；本批问题28：去掉"清除格挡"部分，改为对Boss伤害翻倍；
// 从卡组弃置1张影依卡；从弃牌堆将1张影依技能加入手牌。剧情融合体：影融素材要1影依+1光道——光道桥）
[RegisterCard(typeof(LightswornCardPool))]
public sealed class ElShaddollConstruct : ShaddollToken
{
    protected override IEnumerable<DynamicVar> CanonicalVars => [new DamageVar(16, ValueProp.Move)];

    public ElShaddollConstruct() : base(0, CardType.Attack, CardRarity.Token, TargetType.AnyEnemy) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        // 问题28：去掉清除格挡；对Boss伤害翻倍（Boss战判定=当前房间类型，与原版遗物同款）
        decimal damage = DynamicVars.Damage.BaseValue;
        if (Owner.RunState.CurrentRoom?.RoomType == RoomType.Boss)
            damage *= 2;
        await DamageCmd.Attack(damage).FromCardCompat(this, cardPlay)
            .Targeting(cardPlay.Target!).Execute(choiceContext);

        // 从卡组弃置1张影依卡（被弃置时效果照常触发）
        List<CardModel> candidates = LsUtil.DrawPile(this).Cards.Where(LsUtil.IsShaddoll).ToList();
        if (candidates.Count > 0)
        {
            CardSelectorPrefs prefs = new(LsUtil.Prompt("LIGHTSWORN_TO_DISCARD"), 1, 1);
            List<CardModel> chosen = (await MultiPileCardSelect.Select(choiceContext, Owner, prefs, candidates,
                [PileType.Draw])).ToList();
            if (chosen.Count > 0)
                await LsUtil.MillSelected(choiceContext, this, chosen);
        }

        if (!LsUtil.HandHasSpace(this)) return;
        CardModel? pick = await LsUtil.PickFromDiscard(choiceContext, this,
            c => LsUtil.IsShaddollSkill(c) && !LsUtil.IsElShaddollToken(c));
        if (pick != null)
            await CardPileCmd.Add(pick, PileType.Hand);
    }

    protected override void OnUpgrade() => DynamicVars.Damage.UpgradeValueBy(6);
}

// 神影依·文迪戈（0费技能Token：获得1/2层缓冲，从弃牌堆将1张影依技能加入手牌；
// 之后本场战斗不可再生成——生成锁在 LsUtil.ShaddollFusion / PickAndGenerateShaddoll 内置）
[RegisterCard(typeof(LightswornCardPool))]
public sealed class ElShaddollWendigo : ShaddollToken
{
    protected override IEnumerable<DynamicVar> CanonicalVars => [new DynamicVar("Buffer", 1m)];

    public ElShaddollWendigo() : base(0, CardType.Skill, CardRarity.Token, TargetType.Self) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await PowerCmd.Apply<BufferPower>(choiceContext, Owner.Creature,
            (int)DynamicVars["Buffer"].BaseValue, Owner.Creature, this);
        if (!LsUtil.HandHasSpace(this)) return;
        CardModel? pick = await LsUtil.PickFromDiscard(choiceContext, this,
            c => LsUtil.IsShaddollSkill(c) && !LsUtil.IsElShaddollToken(c));
        if (pick != null)
            await CardPileCmd.Add(pick, PileType.Hand);
    }

    protected override void OnUpgrade() => DynamicVars["Buffer"].UpgradeValueBy(1);
}

// 神影依·神子晶（0费攻击Token：打12/16，可以从手牌丢弃1张影依卡→对目标施加2层虚弱和易伤；
// 从弃牌堆将1张影依技能加入手牌）
[RegisterCard(typeof(LightswornCardPool))]
public sealed class ElShaddollGrysta : ShaddollToken
{
    protected override IEnumerable<DynamicVar> CanonicalVars => [new DamageVar(12, ValueProp.Move)];

    public ElShaddollGrysta() : base(0, CardType.Attack, CardRarity.Token, TargetType.AnyEnemy) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await DamageCmd.Attack(DynamicVars.Damage.BaseValue).FromCardCompat(this, cardPlay)
            .Targeting(cardPlay.Target!).Execute(choiceContext);

        // 可选：丢弃1张手牌影依卡（被弃置时效果照常触发）
        List<CardModel> handShaddoll = PileType.Hand.GetPile(Owner).Cards.Where(LsUtil.IsShaddoll).ToList();
        if (handShaddoll.Count > 0)
        {
            CardSelectorPrefs prefs = new(LsUtil.Prompt("LIGHTSWORN_SHADDOLL_DISCARD_MATERIAL"), 0, 1);
            List<CardModel> chosen = (await MultiPileCardSelect.Select(choiceContext, Owner, prefs, handShaddoll)).ToList();
            if (chosen.Count > 0)
            {
                await CardCmd.Discard(choiceContext, chosen);
                if (cardPlay.Target != null)
                {
                    await PowerCmd.Apply<WeakPower>(choiceContext, cardPlay.Target, 2, Owner.Creature, this);
                    await PowerCmd.Apply<VulnerablePower>(choiceContext, cardPlay.Target, 2, Owner.Creature, this);
                }
            }
        }

        if (!LsUtil.HandHasSpace(this)) return;
        CardModel? pick = await LsUtil.PickFromDiscard(choiceContext, this,
            c => LsUtil.IsShaddollSkill(c) && !LsUtil.IsElShaddollToken(c));
        if (pick != null)
            await CardPileCmd.Add(pick, PileType.Hand);
    }

    protected override void OnUpgrade() => DynamicVars.Damage.UpgradeValueBy(4);
}

// 神影依·舍金纳迦（0费技能Token：获得18/24格挡，可以从手牌丢弃1张影依卡→获得1层人工制品；
// 从弃牌堆将1张影依技能加入手牌）
[RegisterCard(typeof(LightswornCardPool))]
public sealed class ElShaddollShekhinaga : ShaddollToken
{
    protected override IEnumerable<DynamicVar> CanonicalVars => [new BlockVar(18, ValueProp.Move)];

    public ElShaddollShekhinaga() : base(0, CardType.Skill, CardRarity.Token, TargetType.Self) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await CreatureCmd.GainBlock(Owner.Creature, DynamicVars.Block.BaseValue, ValueProp.Move, cardPlay);

        List<CardModel> handShaddoll = PileType.Hand.GetPile(Owner).Cards.Where(LsUtil.IsShaddoll).ToList();
        if (handShaddoll.Count > 0)
        {
            CardSelectorPrefs prefs = new(LsUtil.Prompt("LIGHTSWORN_SHADDOLL_DISCARD_MATERIAL"), 0, 1);
            List<CardModel> chosen = (await MultiPileCardSelect.Select(choiceContext, Owner, prefs, handShaddoll)).ToList();
            if (chosen.Count > 0)
            {
                await CardCmd.Discard(choiceContext, chosen);
                await PowerCmd.Apply<ArtifactPower>(choiceContext, Owner.Creature, 1, Owner.Creature, this);
            }
        }

        if (!LsUtil.HandHasSpace(this)) return;
        CardModel? pick = await LsUtil.PickFromDiscard(choiceContext, this,
            c => LsUtil.IsShaddollSkill(c) && !LsUtil.IsElShaddollToken(c));
        if (pick != null)
            await CardPileCmd.Add(pick, PileType.Hand);
    }

    protected override void OnUpgrade() => DynamicVars.Block.UpgradeValueBy(6);
}

// 神影依·异花莉莉丝（0费攻击Token：打12/17，从弃牌堆将2张影依牌加入手牌）
[RegisterCard(typeof(LightswornCardPool))]
public sealed class ElShaddollAnoyatyllis : ShaddollToken
{
    protected override IEnumerable<DynamicVar> CanonicalVars => [new DamageVar(12, ValueProp.Move)];

    public ElShaddollAnoyatyllis() : base(0, CardType.Attack, CardRarity.Token, TargetType.AnyEnemy) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await DamageCmd.Attack(DynamicVars.Damage.BaseValue).FromCardCompat(this, cardPlay)
            .Targeting(cardPlay.Target!).Execute(choiceContext);

        List<CardModel> candidates = LsUtil.DiscardPile(this).Cards
            .Where(c => LsUtil.IsShaddoll(c) && !LsUtil.IsElShaddollToken(c)).ToList();
        int space = CardPile.MaxCardsInHand - PileType.Hand.GetPile(Owner).Cards.Count;
        if (candidates.Count == 0 || space <= 0) return;
        List<CardModel> picked = await LsUtil.PickSomeFromList(choiceContext, Owner, candidates,
            "LIGHTSWORN_TO_HAND", 0, Math.Min(2, space));
        foreach (CardModel card in picked)
            await CardPileCmd.Add(card, PileType.Hand);
    }

    protected override void OnUpgrade() => DynamicVars.Damage.UpgradeValueBy(5);
}

// 神影依·七贤巨鲲魔（0费攻击Token：打10/13并获得10/13格挡，从卡组或弃牌堆将1张影依卡加入手牌，
// 然后弃置1张手牌）
[RegisterCard(typeof(LightswornCardPool))]
public sealed class ElShaddollApkallone : ShaddollToken
{
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        [new DamageVar(10, ValueProp.Move), new BlockVar(10, ValueProp.Move)];

    public ElShaddollApkallone() : base(0, CardType.Attack, CardRarity.Token, TargetType.AnyEnemy) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await DamageCmd.Attack(DynamicVars.Damage.BaseValue).FromCardCompat(this, cardPlay)
            .Targeting(cardPlay.Target!).Execute(choiceContext);
        await CreatureCmd.GainBlock(Owner.Creature, DynamicVars.Block.BaseValue, ValueProp.Move, cardPlay);

        if (LsUtil.HandHasSpace(this))
        {
            CardModel? pick = await LsUtil.PickFromPiles(choiceContext, this,
                c => LsUtil.IsShaddoll(c) && !LsUtil.IsElShaddollToken(c),
                "LIGHTSWORN_TO_HAND", PileType.Draw, PileType.Discard);
            if (pick != null)
                await CardPileCmd.Add(pick, PileType.Hand);
        }

        List<CardModel> hand = PileType.Hand.GetPile(Owner).Cards.ToList();
        if (hand.Count == 0) return;
        CardSelectorPrefs prefs = new(LsUtil.Prompt("LIGHTSWORN_TO_DISCARD"), 1, 1);
        List<CardModel> chosen = (await MultiPileCardSelect.Select(choiceContext, Owner, prefs, hand)).ToList();
        if (chosen.Count > 0)
            await CardCmd.Discard(choiceContext, chosen);
    }

    protected override void OnUpgrade()
    {
        DynamicVars.Damage.UpgradeValueBy(3);
        DynamicVars.Block.UpgradeValueBy(3);
    }
}

// 神影依·米沙赫雷恶（0费攻击Token：打16/22，获得2层镀层，从卡组将1张影依卡加入手牌，
// 从弃牌堆将1张影依攻击卡加入手牌并本回合变成0费）
[RegisterCard(typeof(LightswornCardPool))]
public sealed class ElShaddollMeshahrail : ShaddollToken
{
    protected override IEnumerable<DynamicVar> CanonicalVars => [new DamageVar(16, ValueProp.Move)];

    public ElShaddollMeshahrail() : base(0, CardType.Attack, CardRarity.Token, TargetType.AnyEnemy) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await DamageCmd.Attack(DynamicVars.Damage.BaseValue).FromCardCompat(this, cardPlay)
            .Targeting(cardPlay.Target!).Execute(choiceContext);
        await PowerCmd.Apply<PlatingPower>(choiceContext, Owner.Creature, 2, Owner.Creature, this);

        if (LsUtil.HandHasSpace(this))
        {
            CardModel? fromDraw = await LsUtil.PickFromDraw(choiceContext, this,
                c => LsUtil.IsShaddoll(c) && !LsUtil.IsElShaddollToken(c));
            if (fromDraw != null)
                await CardPileCmd.Add(fromDraw, PileType.Hand);
        }
        if (LsUtil.HandHasSpace(this))
        {
            CardModel? fromDiscard = await LsUtil.PickFromDiscard(choiceContext, this,
                c => LsUtil.IsShaddollAttack(c) && !LsUtil.IsElShaddollToken(c));
            if (fromDiscard != null)
            {
                await CardPileCmd.Add(fromDiscard, PileType.Hand);
                fromDiscard.EnergyCost.SetThisTurnOrUntilPlayed(0);
            }
        }
    }

    protected override void OnUpgrade() => DynamicVars.Damage.UpgradeValueBy(6);
}

// 翼影依 影文蒂（0费技能Token：获得10/14格挡，接下来3次「影依」牌被弃置时其「被弃置时」效果触发2次，
// 从弃牌堆将1张影依卡加入手牌）
[RegisterCard(typeof(LightswornCardPool))]
public sealed class ReeshaddollWendikurhu : ShaddollToken
{
    protected override IEnumerable<DynamicVar> CanonicalVars => [new BlockVar(10, ValueProp.Move)];

    public ReeshaddollWendikurhu() : base(0, CardType.Skill, CardRarity.Token, TargetType.Self) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await CreatureCmd.GainBlock(Owner.Creature, DynamicVars.Block.BaseValue, ValueProp.Move, cardPlay);
        await PowerCmd.Apply<WendikurhuPower>(choiceContext, Owner.Creature, 3, Owner.Creature, this);
        if (!LsUtil.HandHasSpace(this)) return;
        CardModel? pick = await LsUtil.PickFromDiscard(choiceContext, this,
            c => LsUtil.IsShaddoll(c) && !LsUtil.IsElShaddollToken(c));
        if (pick != null)
            await CardPileCmd.Add(pick, PileType.Hand);
    }

    protected override void OnUpgrade() => DynamicVars.Block.UpgradeValueBy(4);
}
