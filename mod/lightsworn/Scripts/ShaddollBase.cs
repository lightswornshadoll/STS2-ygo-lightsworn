using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;

namespace Lightsworn;

// ================= 影依（Shaddoll）基类 =================

// 影依本家卡基类：「被弃置时」效果走统一管线（打出不触发）。
// 弃光（抽牌堆→弃牌堆）与手牌弃置都触发：双钩子照珠泪 TearFusionCard 先例（v0.4.14 实证互斥不重复）。
// 堕影的蠢动/翼影依 影文蒂在场时「被弃置时」效果触发2次（LsUtil.OnShaddollDiscarded 判定）。
// 问题5：「影依」标不在基类打——统一走 Ls.ShaddollNamed 白名单（LsCard.Tags 按类名自动追加），
// 只有中文名含「影依」的卡才算影依卡（堕影的蠢动/影牢之咒缚/炼狱的乖放等不打标、不作影融素材）。
public abstract class ShaddollCard : LsCard
{
    protected ShaddollCard(int baseCost, CardType type, CardRarity rarity, TargetType target)
        : base(baseCost, type, rarity, target) { }

    protected override HashSet<CardTag> CanonicalTags => [];

    // 影依巫女从消耗堆回收的牌"本回合不能打出"（LsUtil.LockPlayThisTurn，回合键控自动失效）
    protected override bool IsPlayable => base.IsPlayable && !LsUtil.IsPlayLocked(this);

    // 「被弃置时」效果：子类覆写（注意 protected internal override，漏 internal = CS0507）。
    // 打出时被影依猎犬的能力额外触发时也会调用（调用点=ShaddollHoundPower.AfterCardPlayed）。
    protected internal virtual Task OnDiscardedEffect(PlayerChoiceContext ctx) => Task.CompletedTask;

    public override async Task AfterCardChangedPiles(CardModel card, PileType oldPileType, AbstractModel? clonedBy)
    {
        if (card != this) return;
        if (oldPileType != PileType.Draw || card.Pile?.Type != PileType.Discard) return;
        await LsUtil.OnShaddollDiscarded(new BlockingPlayerChoiceContext(), this);
    }

    public override async Task AfterCardDiscarded(PlayerChoiceContext choiceContext, CardModel card)
    {
        if (card != this || card.Pile?.Type != PileType.Discard) return;
        await LsUtil.OnShaddollDiscarded(choiceContext, this);
    }
}

// 神影依Token基类：战斗内生成（不进卡池/图鉴库），0费、带「影依」标（白名单制，可当影融素材连锁）。
// 消耗语义（本批问题35/9 订正，回到初版"离开弃牌堆时消耗"）：
// ①离开弃牌堆（回手牌/回抽牌堆）→消耗；②回到抽牌堆（无论从哪个牌堆来，含被影依巫女从消耗堆取出后再回卡组）→消耗；
// ③被效果直接从消耗堆加入手牌→保留（影依巫女/联结之影依化身的回收设计依赖此条）。
// 「第2次打出时消耗」的实例计数已按问题35删除。
public abstract class ShaddollToken : LsCard
{
    protected ShaddollToken(int baseCost, CardType type, CardRarity rarity, TargetType target)
        : base(baseCost, type, rarity, target, showInCardLibrary: false) { }

    public override bool CanBeGeneratedInCombat => false;

    protected override HashSet<CardTag> CanonicalTags => [];

    protected override bool IsPlayable => base.IsPlayable && !LsUtil.IsPlayLocked(this);

    public override async Task AfterCardChangedPiles(CardModel card, PileType oldPileType, AbstractModel? clonedBy)
    {
        if (card != this) return;
        PileType? now = card.Pile?.Type;
        bool leavingDiscard = oldPileType == PileType.Discard && now is PileType.Hand or PileType.Draw;
        bool toDeck = now == PileType.Draw;   // 任何来源回卡组都消耗（Problem9 bug：巫女从消耗堆拿的神影依回卡组逃跑）
        // 进消耗堆本身就是离场，不再处理（递归守卫：消耗自身会触发本钩子，但那时 now=Exhaust 不满足条件）
        if (leavingDiscard || toDeck)
            await CardCmd.Exhaust(new ThrowingPlayerChoiceContext(), this);
    }

    public override async Task AfterCardDiscarded(PlayerChoiceContext choiceContext, CardModel card)
    {
        if (card != this || card.Pile?.Type != PileType.Discard) return;
        // Token没有「被弃置时」效果，但被弃置=「影依」牌被弃置（影牢之咒缚计数、影文蒂触发次数消耗照常）
        await LsUtil.OnShaddollDiscarded(choiceContext, this);
    }
}
