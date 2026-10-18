using MegaCrit.Sts2.Core.CardSelection;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using System.Runtime.CompilerServices;

namespace Lightsworn;

public static class LsUtil
{
    public static CardPile DiscardPile(CardModel card) => PileType.Discard.GetPile(card.Owner);
    public static CardPile DrawPile(CardModel card) => PileType.Draw.GetPile(card.Owner);
    public static CardPile ExhaustPile(CardModel card) => PileType.Exhaust.GetPile(card.Owner);

    // 能力/无触发卡场合（影依的伪典改能力后的回合开始影融）
    public static CardPile DiscardPile(Player player) => PileType.Discard.GetPile(player);
    public static CardPile DrawPile(Player player) => PileType.Draw.GetPile(player);

    public static bool IsLs(CardModel card) => card.Tags.Contains(Ls.Lightsworn);
    public static bool IsEarthAngel(CardModel card) => card.Tags.Contains(Ls.EarthAngel);
    public static bool IsFiendsmith(CardModel card) => card.Tags.Contains(Ls.Fiendsmith);
    public static bool IsTear(CardModel card) => card.Tags.Contains(Ls.Tearlaments);
    // 珠泪攻击牌：珠泪哀歌族标签 + 攻击牌（能力牌珍珠世界不是融合素材）
    public static bool IsTearAttack(CardModel card) => IsTear(card) && card.Type == CardType.Attack;

    // 弃光：从抽牌堆顶部将count张牌弃置。
    // 暮光（v0.4.11 重做）：弃光数量超过卡组剩余时，消耗2层暮光把弃牌堆洗回抽牌堆并补完剩余弃光（回1费）。
    // 卡牌来源的弃光：若是「光道」牌（=光道牌发动弃光），触发加洛斯能力（追加弃光2）；
    // 被弃置的 LsCard 会收到 OnMilledByLsCard 钩子（黄昏之抹杀/黄昏之双龙的"被光道牌从卡组弃掉"联动）。
    // 加洛斯的追加弃光走player来源重载，不会递归触发。除光无暮光联动。
    public static async Task<List<CardModel>> Mill(PlayerChoiceContext ctx, CardModel source, int count)
    {
        List<CardModel> milled = await MillCore(ctx, source.Owner, count, garothAny: true);
        if (IsLs(source))
        {
            foreach (CardModel card in milled)
                if (card is LsCard lsCard)
                    await lsCard.OnMilledByLsCard(ctx, source);
            if (milled.Count > 0)
                foreach (GarothPower power in source.Owner.Creature.Powers.OfType<GarothPower>().ToList())
                    await power.OnLightswornMilled(ctx, source.Owner);
        }
        return milled;
    }

    public static Task<List<CardModel>> Mill(PlayerChoiceContext ctx, Player player, int count)
        => MillCore(ctx, player, count, garothAny: true);

    // garothAny=false：本批问题34——加洛斯（强化版）的"任意弃光"通知在追加弃光的载荷里必须关掉
    // （否则载荷弃光→再触发→无限递归）；珍妮丝/破坏之光/正义世界的通知照常（载荷弃光同样算弃光事件）。
    internal static async Task<List<CardModel>> MillCore(PlayerChoiceContext ctx, Player player, int count, bool garothAny)
    {
        List<CardModel> milled = new();
        CardPile draw = PileType.Draw.GetPile(player);
        for (int i = 0; i < count; i++)
        {
            CardModel? card = draw.Cards.FirstOrDefault();
            if (card == null) break;
            await CardPileCmd.Add(card, PileType.Discard);
            milled.Add(card);
        }
        // 光道祭司（珍妮丝）能力：记录"本回合发动过弃光"
        foreach (JanicePower power in player.Creature.Powers.OfType<JanicePower>().ToList())
            power.OnMillHappened();
        // 暮光：卡组不够弃光数量→耗2层暮光洗回弃牌堆、回1费并补完剩余弃光（补完部分计入返回值）
        if (milled.Count < count)
            milled.AddRange(await TwilightPower.RefillOnMill(ctx, player, count - milled.Count));
        // 破坏之光（先古牌）：每次弃光（一次Mill调用=1次，含暮光补完）对所有敌人施加Amount层灾厄
        if (milled.Count > 0)
            foreach (LightOfDestructionPower power in player.Creature.Powers.OfType<LightOfDestructionPower>().ToList())
                await power.OnMillHappened(ctx);
        // 加洛斯（强化版·问题34）：任意弃光都触发（不限光道、不限来源）
        if (garothAny && milled.Count > 0)
            foreach (GarothPower power in player.Creature.Powers.OfType<GarothPower>().ToList())
                await power.OnAnyMill(ctx, player, milled);
        // 正义世界（问题36）：每次弃光，可以将弃置的牌中的1张加入手牌（0~1可选）
        if (milled.Count > 0)
            foreach (JusticeWorldPower power in player.Creature.Powers.OfType<JusticeWorldPower>().ToList())
                await power.OnMillHappened(ctx, milled);
        return milled;
    }

    // 卡牌来源的弃光：见 Mill(ctx, source, count)。
    public static Task<List<CardModel>> MillLsTracked(PlayerChoiceContext ctx, CardModel source, int count)
        => Mill(ctx, source, count);

    // 除光（本批反馈问题26）：由"抽牌堆顶N张"改为从抽牌堆**自选**count张消耗（不足时全部消耗，
    // 无选择）。除光是消耗不是弃置：不触发加洛斯联动，也不触发光道弃光钩子。
    public static Task<List<CardModel>> Banish(PlayerChoiceContext ctx, CardModel source, int count)
        => Banish(ctx, source.Owner, count);

    public static async Task<List<CardModel>> Banish(PlayerChoiceContext ctx, Player player, int count)
    {
        List<CardModel> banished = new();
        List<CardModel> draw = PileType.Draw.GetPile(player).Cards.ToList();
        if (draw.Count == 0) return banished;
        List<CardModel> chosen = draw.Count <= count
            ? draw   // 不足时全部消耗
            : await PickFromList(ctx, player, draw, "LIGHTSWORN_TO_EXHAUST", count);
        foreach (CardModel card in chosen)
        {
            await LsCompat.ExhaustCompat(ctx, card);
            banished.Add(card);
        }
        return banished;
    }

    // 选择性弃置：把指定的牌（应在抽牌堆中）弃到弃牌堆，逐张触发光道弃光钩子；
    // 来源是光道牌时触发加洛斯（雅典娜"从卡组丢弃2张不同的光道牌"、宰制者"从卡组弃一张卡"）。
    public static async Task<List<CardModel>> MillSelected(PlayerChoiceContext ctx, CardModel source, List<CardModel> cards)
    {
        List<CardModel> milled = new();
        foreach (CardModel card in cards)
        {
            if (card.Pile?.Type != PileType.Draw) continue;
            await CardPileCmd.Add(card, PileType.Discard);
            milled.Add(card);
            if (card is LsCard lsCard)
                await lsCard.OnMilledByLsCard(ctx, source);
        }
        if (milled.Count > 0 && IsLs(source))
        {
            foreach (GarothPower power in source.Owner.Creature.Powers.OfType<GarothPower>().ToList())
                await power.OnLightswornMilled(ctx, source.Owner);
        }
        return milled;
    }

    // 弃光并在弃置的牌中找光道牌
    public static int CountTag(List<CardModel> milled, CardTag tag) => milled.Count(c => c.Tags.Contains(tag));

    // 选择器：从弃牌堆选count张（供检索类效果使用，结果会与候选集取交集）
    public static async Task<List<CardModel>> SelectFromPile(PlayerChoiceContext ctx, CardModel source,
        CardPile pile, LocString prompt, int count)
    {
        CardSelectorPrefs prefs = new(prompt, count);
        return (await CardSelectCmd.FromCombatPile(ctx, pile, source.Owner, prefs)).ToList();
    }

    // 从任意候选列表中选count张（BaseLib MultiPileCardSelect：选择界面只显示候选牌，杜绝误选）
    public static async Task<List<CardModel>> PickFromList(PlayerChoiceContext ctx, Player player,
        List<CardModel> candidates, string promptKey, int count = 1)
    {
        if (candidates.Count == 0) return new List<CardModel>();
        CardSelectorPrefs prefs = new(Prompt(promptKey), count, count);
        return (await MultiPileCardSelect.Select(ctx, player, prefs, candidates)).ToList();
    }

    // 从候选列表中一次选完min~max张（问题4：多张选择参考雪之化身，一个界面选完，不再逐张弹窗）
    public static async Task<List<CardModel>> PickSomeFromList(PlayerChoiceContext ctx, Player player,
        List<CardModel> candidates, string promptKey, int min, int max)
    {
        if (candidates.Count == 0) return new List<CardModel>();
        CardSelectorPrefs prefs = new(Prompt(promptKey), min, max);
        return (await MultiPileCardSelect.Select(ctx, player, prefs, candidates)).ToList();
    }

    // 从候选列表中选一张
    public static async Task<CardModel?> PickFirst(PlayerChoiceContext ctx, Player player,
        List<CardModel> candidates, string promptKey)
    {
        List<CardModel> sel = await PickFromList(ctx, player, candidates, promptKey, 1);
        return sel.FirstOrDefault();
    }

    // 从"刚弃置的一批牌"中挑一张满足条件的牌（只在候选内选取）
    public static Task<CardModel?> PickFromMilled(PlayerChoiceContext ctx, CardModel source,
        List<CardModel> milled, Func<CardModel, bool> filter)
        => PickFirst(ctx, source.Owner, milled.Where(filter).ToList(), "LIGHTSWORN_TO_HAND");

    // 从指定牌堆按条件挑一张（玩家只在满足条件的牌中选取）
    public static Task<CardModel?> PickFromPile(PlayerChoiceContext ctx, CardModel source,
        CardPile pile, Func<CardModel, bool> filter, string promptKey = "LIGHTSWORN_TO_HAND")
        => PickFirst(ctx, source.Owner, pile.Cards.Where(filter).ToList(), promptKey);

    public static Task<CardModel?> PickFromDiscard(PlayerChoiceContext ctx, CardModel source,
        Func<CardModel, bool> filter, string promptKey = "LIGHTSWORN_TO_HAND")
        => PickFromPile(ctx, source, DiscardPile(source), filter, promptKey);

    public static Task<CardModel?> PickFromDraw(PlayerChoiceContext ctx, CardModel source,
        Func<CardModel, bool> filter)
        => PickFromPile(ctx, source, DrawPile(source), filter);

    // 从多个牌堆中按条件挑一张（选择界面带来源牌堆标记；用于"卡组或弃牌堆"类检索）
    public static async Task<CardModel?> PickFromPiles(PlayerChoiceContext ctx, CardModel source,
        Func<CardModel, bool> filter, string promptKey, params PileType[] pileTypes)
    {
        List<CardModel> candidates = pileTypes
            .SelectMany(p => p.GetPile(source.Owner).Cards)
            .Where(filter).ToList();
        if (candidates.Count == 0) return null;
        CardSelectorPrefs prefs = new(Prompt(promptKey), 1);
        List<CardModel> sel = (await MultiPileCardSelect.Select(ctx, source.Owner, prefs, candidates, pileTypes)).ToList();
        return sel.FirstOrDefault();
    }

    // 消耗弃牌堆中一张满足条件的牌（玩家自选；没有则什么都不做）
    public static async Task<CardModel?> ExhaustOneFromDiscard(PlayerChoiceContext ctx, CardModel source,
        Func<CardModel, bool> filter)
    {
        CardModel? pick = await PickFromDiscard(ctx, source, filter, "LIGHTSWORN_TO_EXHAUST");
        if (pick == null) return null;
        await LsCompat.ExhaustCompat(ctx, pick);
        return pick;
    }

    // 消耗指定牌堆中一张满足条件的牌（玩家自选）
    public static async Task<CardModel?> ExhaustOneFromPile(PlayerChoiceContext ctx, CardModel source,
        CardPile pile, Func<CardModel, bool> filter)
    {
        CardModel? pick = await PickFromPile(ctx, source, pile, filter, "LIGHTSWORN_TO_EXHAUST");
        if (pick == null) return null;
        await LsCompat.ExhaustCompat(ctx, pick);
        return pick;
    }

    // 从弃牌堆手动选择count张牌并消耗（不足则全部），返回消耗数量（白雪化身）
    public static async Task<int> BurnSelectedFromDiscard(PlayerChoiceContext ctx, CardModel source, int count)
    {
        List<CardModel> sel = await PickFromList(ctx, source.Owner, DiscardPile(source).Cards.ToList(),
            "LIGHTSWORN_TO_EXHAUST", count);
        foreach (CardModel card in sel)
            await LsCompat.ExhaustCompat(ctx, card);
        return sel.Count;
    }

    // 弃牌堆+消耗堆中不同名「光道」牌的数量（惩戒之龙的打出条件）
    public static int DistinctLsInGravezones(CardModel card)
    {
        IEnumerable<CardModel> all = DiscardPile(card).Cards.Concat(ExhaustPile(card).Cards).Where(IsLs);
        return all.Select(c => c.Id).Distinct().Count();
    }

    // 弃牌堆中不同名「光道」牌的数量（裁决之龙新打出条件：只看弃牌堆，问题21）
    public static int DistinctLsInDiscard(CardModel card)
        => DiscardPile(card).Cards.Where(IsLs).Select(c => c.Id).Distinct().Count();

    // 消耗堆中不同名「光道」牌的数量（惩戒之龙问题5重做后的打出条件：只看消耗堆）
    public static int DistinctLsInExhaust(CardModel card)
        => ExhaustPile(card).Cards.Where(IsLs).Select(c => c.Id).Distinct().Count();

    // ============ 珠泪融合引擎 ============
    // 拥有「珠泪融合」的卡被弃置时（弃光或手牌弃置，打出不触发）由 TearFusionCard 的两个钩子调到这里。
    // 流程：从弃牌堆选1~2张素材（珠泪攻击牌或影依牌，v0.4.24 问题2 扩展）→非融合牌放回抽牌堆随机位置
    // （融合Token当素材=消耗而非返回），然后从条件满足且本回合未生成过的融合卡中选1张加入手牌
    // （触发卡已升级→融合出强化版）。同一回合每张融合卡只能生成1次；每次融合成功通知珍珠世界
    // （对所有敌人施加1层易伤）。生成锁=跨引擎统一（见下方 ResetFusionKeys/RegisterFusionGenerated）。

    // 一张牌不能同时占两个素材角色（问题6：影依攻击卡+非影依技能卡不该满足神子晶的
    // "影依+攻击"——类型位必须由另一张牌担任）。a=主判定（如影依），b=另一张牌要满足的谓词。
    private static bool DistinctPair(List<CardModel> m, Func<CardModel, bool> a, Func<CardModel, bool> b)
        => m.Any(x => a(x) && m.Any(y => !ReferenceEquals(y, x) && b(y)));

    // 融合卡注册表：概念卡（选择界面展示用）+ 材料条件（对所选素材判定，严格语义：
    // 素材数量须与条件完全一致——2张条件的融合卡不能拿3张素材发动，反之亦然）
    private static List<(CardModel Concept, Func<List<CardModel>, bool> Cond)> FusionOptions() => new()
    {
        // ⚠ 已知问题3（v0.5.4 修复）：每个条件都必须显式约束**素材总数**（m.Count == N）。
        // 原 Rulkallos/KaleidoHeart 只判 Count(IsTearAttack) 而漏了总量——玩家选「水仙女+影依」时
        // material=[触发珠泪攻击牌, 水仙女(Kitkallos), 影依] 共3张，Count(IsTearAttack)==2 与
        // Any(is Kitkallos) 双双成立 → 3张素材融出了卡面写明"2张珠泪攻击牌"的鲁莎卡人鱼。
        // 卡雷多哈特同理（Count(IsTearAttack)==3 成立但总量可能是4）。
        (ModelDb.Card<Kitkallos>(),    m => m.Count == 2 && m.Count(IsTearAttack) == 2),
        (ModelDb.Card<Rulkallos>(),    m => m.Count == 2 && m.Count(IsTearAttack) == 2 && m.Any(c => c is Kitkallos)),
        (ModelDb.Card<KaleidoHeart>(), m => m.Count == 3 && m.Count(IsTearAttack) == 3 && m.Any(c => c is Reinohart)),
        // 犀角龙=融合卡+珠泪卡（问题9）：融合卡位适配珠泪融合Token与神影依Token
        (ModelDb.Card<Dragostapelia>(), m => m.Count == 2 && DistinctPair(m,
            c => c is TearFusionToken or ShaddollToken, IsTearAttack)),
        // 米德拉什（问题2/v0.4.24）：1张影依+1张影依/珠泪牌——与影融同条件（LsUtil.ShaddollFusionOptions），
        // 珠泪融合触发卡（珠泪攻击牌）自己占珠泪位，影依牌当影依位。珠泪融合从此也能产出神影依。
        (ModelDb.Card<ElShaddollWinda>(), m => m.Count == 2 && DistinctPair(m, IsShaddoll,
            c => IsShaddoll(c) || IsTear(c))),
        // 神子晶（v0.4.25 用户点名）：1张影依+1张攻击牌——与影融同条件，触发卡（珠泪攻击牌）
        // 自己占攻击位，影依牌当影依位。
        (ModelDb.Card<ElShaddollGrysta>(), m => m.Count == 2 && DistinctPair(m, IsShaddoll,
            c => c.Type == CardType.Attack)),
    };

    public static async Task TearFusion(PlayerChoiceContext ctx, CardModel trigger)
    {
        Player player = trigger.Owner;
        ICombatState? combat = player.Creature.CombatState;
        if (combat == null) return;
        ResetFusionKeys(combat);

        List<(CardModel Concept, Func<List<CardModel>, bool> Cond)> options = FusionOptions();
        if (options.All(o => IsFusionLocked(combat, player, o.Concept)))
        {
            TearLog($"cast trigger={trigger.Id.Entry} → abort：全部融合卡本回合已生成（生成锁）");
            return;
        }

        // 问题8：素材必须包含触发珠泪融合的卡本身（触发卡已随弃置落入弃牌堆）。
        // 问题2/v0.4.24：其他素材=珠泪攻击牌 或 影依牌——珠泪位走米德拉什（触发卡自己担任）、
        // 攻击位走神子晶（触发卡是攻击牌，同自己担任，v0.4.25）。
        List<CardModel> others = DiscardPile(trigger).Cards
            .Where(c => (IsTearAttack(c) || IsShaddoll(c)) && !ReferenceEquals(c, trigger)).ToList();
        TearLog($"cast trigger={trigger.Id.Entry} upgraded={trigger.IsUpgraded} others={others.Count}");
        if (others.Count < 1) return;
        // 候选预筛（影融 ValidMaterialCandidates 同精神）：只显示与触发卡组合后至少有一种可用融合的牌。
        // ⚠ v0.4.37：素材必须含触发卡（问题8），组合=触发卡+1张 或 触发卡+2张——旧实现只测
        // {触发卡, 单张}：3素材融合（卡雷多哈特 m.Count==3）恒不命中，只能参与3素材组合的牌
        // 会被"挡枪"选不了（朋友实测：弃牌堆有雷诺哈特+鲁莎卡人鱼，本回合 Kitkallos 已生成
        // 被锁时雷诺哈特在选材界面不显示→卡雷多哈特融不出）。改为枚举两种长度的全部组合，
        // 命中组合的所有牌都标记（同 v0.4.35 影融预筛修复精神）。
        HashSet<CardModel> useful = new();
        foreach (var o in options)
        {
            if (IsFusionLocked(combat, player, o.Concept)) continue;
            foreach (List<CardModel> combo in Combinations(others, 1))
                if (o.Cond([trigger, .. combo])) useful.UnionWith(combo);
            if (others.Count >= 2)
                foreach (List<CardModel> combo in Combinations(others, 2))
                    if (o.Cond([trigger, .. combo])) useful.UnionWith(combo);
        }
        List<CardModel> candidates = others.Where(useful.Contains).ToList();
        TearLog($"candidates={candidates.Count}：{string.Join(" ; ", candidates.Select(MatDescr))}");
        if (candidates.Count < 1) { TearLog("abort：无候选（无可用融合组合）"); return; }
        List<CardModel> extra = await PickSomeFromList(ctx, player, candidates, "LIGHTSWORN_TEAR_MATERIAL", 1,
            Math.Min(2, candidates.Count));
        if (extra.Count < 1) { TearLog("abort：素材选择取消"); return; }
        List<CardModel> material = [trigger, .. extra];
        TearLog($"picked n={material.Count}：{string.Join(" ; ", material.Select(MatDescr))}");

        // 严格判定（问题2）：选出的组合无可用融合=**作废**（不弃置不消耗、什么都没发生）。
        // ⚠ 已知问题3（v0.5.4，用户订正）：此处**不做向下兼容**——用户明确要求"选超素材就作废"。
        //   即玩家在选材界面选了不满足任何融合条件的组合时，整个发动作废、素材原样不动。
        //   （曾试实现"降级到合法子集"，用户否决；严格语义与 v0.4.15 起的既有设计一致。）
        List<CardModel> available = options
            .Where(o => o.Cond(material) && !IsFusionLocked(combat, player, o.Concept))
            .Select(o => o.Concept).ToList();
        if (available.Count == 0)
        {
            TearLog($"abort：组合无可用融合（素材未动、作废）｜{OptionLine(combat, player, options, material)}");
            return;
        }
        // v0.4.37：融合卡选择与手牌空间判定前移到素材移动之前——取消选择/手牌满时不再白吃素材
        if (!HandHasSpace(trigger)) { TearLog("abort：手牌已满（素材未动）"); return; }
        CardModel? pick = await PickConcept(ctx, player, available, "LIGHTSWORN_TEAR_FUSION");
        if (pick == null) { TearLog("abort：融合卡选择取消（素材未动）"); return; }

        foreach (CardModel card in material)
        {
            if (card is TearFusionToken)
                await LsCompat.ExhaustCompat(ctx, card);   // 融合卡被选做素材=消耗，而不是返回卡组
            else
                await CardPileCmd.Add(card, PileType.Draw, CardPilePosition.Random);
        }

        CardModel? token = combat.CreateCard(pick, player);
        if (token == null) { TearLog("abort：CreateCard 失败（素材已被消费）"); return; }
        if (trigger.IsUpgraded)
        {
            token.UpgradeInternal();
            token.FinalizeUpgradeInternal();
        }
        RegisterFusionGenerated(combat, player, token);
        await CardPileCmd.AddGeneratedCardToCombat(token, PileType.Hand, player);
        TearLog($"生成 {token.Id.Entry} upgraded={trigger.IsUpgraded} → 已入手牌");

        foreach (PearlWorldPower power in player.Creature.Powers.OfType<PearlWorldPower>().ToList())
            await power.OnFusionHappened(ctx);
    }

    // ============ 影依系列（v0.5 需求：影融 + 被弃置时管线） ============

    // 问题5：只有中文名含「影依」的卡才打「影依」标（Ls.ShaddollNamed 白名单，LsCard.Tags 自动追加）——
    // 堕影的蠢动/影牢之咒缚/炼狱的乖放卡名无影依字样，不算影依卡（不作影融素材、不被检索、不计弃置联动）
    public static bool IsShaddoll(CardModel card) => card.Tags.Contains(Ls.Shaddoll);
    public static bool IsShaddollSkill(CardModel card) => IsShaddoll(card) && card.Type == CardType.Skill;
    public static bool IsShaddollAttack(CardModel card) => IsShaddoll(card) && card.Type == CardType.Attack;

    // 神影依=9张战斗内生成的Token（ShaddollToken子类）。神影依的「从弃牌堆拿影依卡」效果
    // 不能拿神影依（防米德拉什回费等检索循环，v0.4.21 用户点名）；普通影依卡不受此限。
    public static bool IsElShaddollToken(CardModel card) => card is ShaddollToken;

    // 伤害置0只持续一次（心影依融合/羽影依文蒂/虚影依神子晶/联结之影依化身）：
    // 原值记在卡上（LsCard.DamageRestoreAfterPlay），打出后恢复（LsCard.AfterCardPlayed）。
    public static void ZeroDamageOnce(CardModel card)
    {
        if (card is LsCard ls && card.DynamicVars.TryGetValue("Damage", out var damage))
        {
            ls.DamageRestoreAfterPlay = damage.BaseValue;
            damage.BaseValue = 0m;
        }
    }

    // 概念卡（ModelDb 范例卡，不可变）不能直接进选择界面：NSimpleCardSelectScreen._Ready 会读
    // card.Owner，get_Owner 对不可变卡抛 CanonicalModelException——界面初始化中断、点击 NRE
    // （v0.4.20 实测日志：珠泪/影融的结果选择界面全中招）。先 MutableClone+设 Owner 再选择，
    // 返回值映射回原概念卡供 CreateCard。
    public static async Task<CardModel?> PickConcept(PlayerChoiceContext ctx, Player player,
        List<CardModel> concepts, string promptKey)
    {
        if (concepts.Count == 0) return null;
        List<CardModel> clones = new();
        foreach (CardModel concept in concepts)
        {
            CardModel clone = (CardModel)concept.MutableClone();
            clone.Owner = player;
            clones.Add(clone);
        }
        CardModel? picked = await PickFirst(ctx, player, clones, promptKey);
        return picked == null ? null : concepts.FirstOrDefault(c => c.Id == picked.Id);
    }

    // 影融素材来源模式
    public enum ShaddollFusionMode
    {
        Hand,           // 默认：弃手牌2~3张作素材（影依融合/神影依融合/影依·拿非利）
        DiscardExhaust, // 素材从弃牌堆选2张影依牌消耗，不触发其被弃置时效果（影依的伪典/虚影依 神子晶）
        Exempt,         // 素材豁免：任意2张手牌（含至少1张影依牌）生成任意神影依（魂影依融合/影依的原核）
    }

    // 神影依注册表 + 素材条件（严格判定：素材数量须与条件完全一致——v0.4.15 珠泪同款精神）。
    // exempt=豁免模式：任意2张手牌（含至少1张影依牌）可生成任意神影依。
    private static List<(CardModel Concept, Func<List<CardModel>, bool> Cond)> ShaddollFusionOptions(bool exempt)
    {
        if (exempt)
        {
            Func<List<CardModel>, bool> any = m => m.Count == 2 && m.Any(IsShaddoll);
            return new()
            {
                (ModelDb.Card<ElShaddollWinda>(),       any),
                (ModelDb.Card<ElShaddollConstruct>(),   any),
                (ModelDb.Card<ElShaddollWendigo>(),     any),
                (ModelDb.Card<ElShaddollGrysta>(),      any),
                (ModelDb.Card<ElShaddollShekhinaga>(),  any),
                (ModelDb.Card<ElShaddollAnoyatyllis>(), any),
                (ModelDb.Card<ElShaddollApkallone>(),   any),
                (ModelDb.Card<ElShaddollMeshahrail>(),  any),
                (ModelDb.Card<ReeshaddollWendikurhu>(), any),
            };
        }
        return new()
        {
            // 米德拉什：1张影依+1张影依/珠泪牌（问题7）
            (ModelDb.Card<ElShaddollWinda>(),       m => m.Count == 2 && DistinctPair(m, IsShaddoll,
                                                        c => IsShaddoll(c) || IsTear(c))),
            // 拿非利（光道桥）：1张影依+1张光道（问题13：圣影依 商神杖灵仅在融合拿非利时可充当光道位）
            (ModelDb.Card<ElShaddollConstruct>(),   m => m.Count == 2 && DistinctPair(m, IsShaddoll,
                                                        c => IsLs(c) || c is QadshaddollKeios)),
            // 文迪戈：1张影依+另1张技能牌（问题6：技能位须由另一张牌担任）
            (ModelDb.Card<ElShaddollWendigo>(),     m => m.Count == 2 && DistinctPair(m, IsShaddoll,
                                                        c => c.Type == CardType.Skill)),
            // 神子晶：1张影依+另1张攻击牌（问题6：影依攻击卡+非影依技能卡不能再凭一张牌双占两 位）
            (ModelDb.Card<ElShaddollGrysta>(),      m => m.Count == 2 && DistinctPair(m, IsShaddoll,
                                                        c => c.Type == CardType.Attack)),
            // 舍金纳迦：2张影依攻击牌
            (ModelDb.Card<ElShaddollShekhinaga>(),  m => m.Count == 2 && m.All(IsShaddoll) && m.All(c => c.Type == CardType.Attack)),
            // 异花莉莉丝：3张影依
            (ModelDb.Card<ElShaddollAnoyatyllis>(), m => m.Count == 3 && m.All(IsShaddoll)),
            // 七贤巨鲲魔：2张不同名的影依
            (ModelDb.Card<ElShaddollApkallone>(),   m => m.Count == 2 && m.All(IsShaddoll) && m.Select(c => c.Id).Distinct().Count() == 2),
            // 米沙赫雷恶：3张手牌（含至少1张影依）——本批问题21 bug：素材必须全部来自手牌，
            // 影依融合敲后从卡组选的素材不能凑它的"3张手牌"（朋友实测可白嫖卡组素材）
            (ModelDb.Card<ElShaddollMeshahrail>(),  m => m.Count == 3 && m.Any(IsShaddoll)
                                                        && m.All(c => c.Pile?.Type == PileType.Hand)),
            // 翼影依 影文蒂：2张影依技能牌
            (ModelDb.Card<ReeshaddollWendikurhu>(), m => m.Count == 2 && m.All(IsShaddoll) && m.All(c => c.Type == CardType.Skill)),
        };
    }

    // 问题36：影依的原核作为影融素材时，本次影融可以融合任意神影依（条件=任意2张含≥1影依，同豁免模式）。
    // 按素材组合动态改写每个融合卡的条件：组合含原核→豁免条件，否则原条件。
    private static List<(CardModel Concept, Func<List<CardModel>, bool> Cond)> WithCoreRule(
        List<(CardModel Concept, Func<List<CardModel>, bool> Cond)> options)
    {
        static bool AnyFusion(List<CardModel> m) => m.Count == 2 && m.Any(IsShaddoll);
        return options.Select(o => (o.Concept, (Func<List<CardModel>, bool>)(m =>
            m.Any(c => c is ShaddollCore) ? AnyFusion(m) : o.Cond(m)))).ToList();
    }

    // 素材组合是否满足指定神影依的融合条件且未被生成锁拦下（影依的原核规则生效）。
    // 供圣影依 商神杖灵（问题32）等"指定融合目标"的效果使用。含 ResetFusionKeys，可随时调用。
    // v0.5.1：生成锁按玩家判定——传入发动方（卡主）。
    public static bool CanFuseInto(ICombatState combat, Player player, List<CardModel> material, CardModel concept)
    {
        ResetFusionKeys(combat);
        var opt = WithCoreRule(ShaddollFusionOptions(false))
            .FirstOrDefault(o => o.Concept.Id == concept.Id);
        if (opt.Concept == null || !opt.Cond(material)) return false;
        return !IsFusionLocked(combat, player, opt.Concept);
    }

    // 指定神影依是否已被生成锁拦下（本回合已生成/文迪戈本场已生成）——供 IsPlayable 预判
    public static bool IsFusionGenerated(ICombatState combat, Player player, CardModel concept)
    {
        ResetFusionKeys(combat);
        return IsFusionLocked(combat, player, concept);
    }

    // 回合开始时"从列表中随机生成1张加入手牌并获得「消耗」"（绊影依/救影依能力，本批反馈）。
    // 生成的是神影依（融合Token）时登记融合生成锁（同残响：本回合不能再融合出该卡、图鉴置灰）。
    // 随机数走玩家侧 RNG（坑5：creature.Player 对怪物为 null）。
    public static async Task GenerateRandomToHand(PlayerChoiceContext ctx, Player player, List<CardModel> pool)
    {
        if (pool.Count == 0 || !HandHasSpace(player)) return;
        ICombatState? combat = player.Creature.CombatState;
        if (combat == null) return;
        CardModel? concept = player.RunState.Rng.CombatCardSelection.NextItem(pool);
        if (concept == null) return;
        CardModel? card = combat.CreateCard(concept, player);
        if (card == null) return;
        card.AddKeyword(CardKeyword.Exhaust);
        if (card is ShaddollToken)
            LockFusionGeneratedThisTurn(combat, player, card);
        await CardPileCmd.AddGeneratedCardToCombat(card, PileType.Hand, player);
        FusionLog($"随机生成 {card.Id.Entry}（{concept.Id.Entry}）→ 已入手牌");
    }

    // 把一张（已存在的）融合Token登记为"本回合已生成"——供残响（PrimevalEcho）使用：
    // 从消耗堆拿回的珠泪融合Token视同本回合已融合，本回合不能再融合出对应的融合卡（图鉴同步置灰）。
    // v0.5.1：显式传发动方玩家（生成锁按玩家隔离）。
    public static void LockFusionGeneratedThisTurn(ICombatState combat, Player player, CardModel card)
    {
        ResetFusionKeys(combat);
        RegisterFusionGenerated(combat, player, card);
    }

    // 融合生成锁（v0.4.24 跨引擎统一；v0.4.29 改为按战斗实例隔离）：每回合每张只能生成1次
    //（用户点名，照珠泪同款）；文迪戈额外=本场战斗只能生成1次（本批反馈：卡雷多哈特同文迪戈）。
    // 米德拉什可从珠泪融合与影融两个引擎生成，故两套"本回合已生成"集合统一登记/判定
    //（图鉴置灰 IsFusionUsedForCodex 同步双查）。
    // ⚠ 状态必须挂在 CombatState 实例上（ConditionalWeakTable，战斗结束随状态一起回收），
    // 不能用 static+回合号键控——回合号每场战斗都从1重计：①上一场最后回合生成的锁会漏进
    // 下一场战斗的同回合（朋友实测：上一场最后回合融合的怪，下一场同回合不能再融/图鉴仍置灰）；
    // ②存档里没有战斗状态，"保存并退出→继续"=本场重打（新实例、回到第1回合），静态锁不失效
    // →同一回合只能融另一种、再退再进后全都融不了（朋友实测）。
    // ⚠ v0.5.1 联机：锁按玩家隔离（Dictionary 以 Player 实例为键，同端同实例）——"每回合每张1次"
    // 是各玩家自己的融合引擎规则，双光道组队时不能互相抢锁（否则队友融过 Kitkallos，我本回合
    // 就融不出、图鉴还被队友的锁置灰）。
    private sealed class FusionLockState
    {
        public object? TurnKey;
        public readonly Dictionary<Player, HashSet<ModelId>> TearFusedThisTurn = new();
        public readonly Dictionary<Player, HashSet<ModelId>> ShaddollFusedThisTurn = new();
        // 本场战斗只能生成1次：文迪戈（神影依）+ 卡雷多哈特（本批反馈）
        public readonly Dictionary<Player, HashSet<ModelId>> BattleLocked = new();
    }

    private static readonly ConditionalWeakTable<ICombatState, FusionLockState> _fusionLocks = new();

    private static FusionLockState Locks(ICombatState combat) => _fusionLocks.GetOrCreateValue(combat);

    // 取（或新建）该玩家在本场战斗中的键集合
    private static HashSet<ModelId> PlayerSet(Dictionary<Player, HashSet<ModelId>> map, Player player)
    {
        if (!map.TryGetValue(player, out HashSet<ModelId>? set))
        {
            set = new HashSet<ModelId>();
            map[player] = set;
        }
        return set;
    }

    // ===== 诊断日志（v0.4.34：排查"素材满足条件却没出神影依"类问题）=====
    // 以 "[LsShaddoll] FUSION ..." 前缀写入游戏日志（%APPDATA%\SlayTheSpire2\logs\godot.log）。
    // 每次发动记录：触发/房间/素材（含牌堆与影依标）/逐张条件与锁判定/中止原因/生成结果——静默分支从此可取证。
    private static void FusionLog(string message) => MegaCrit.Sts2.Core.Logging.Log.Info($"[LsShaddoll] FUSION {message}");

    // 珠泪融合诊断日志（v0.4.37）：与影融 FusionLog 同精神——前缀 [LsTear] FUSION，
    // 记录触发卡/素材池/候选预筛/逐处中止原因，供"选不了素材/静默无事发生"类反馈取证。
    private static void TearLog(string message) => MegaCrit.Sts2.Core.Logging.Log.Info($"[LsTear] FUSION {message}");

    // 日志用素材描述：卡名[牌堆|影依标|升级态]
    private static string MatDescr(CardModel c)
        => $"{c.Title}[{c.Pile?.Type.ToString() ?? "无堆"}|{(IsShaddoll(c) ? "影依" : "非影依")}|{(c.IsUpgraded ? "强化" : "基础")}]";

    // 日志用全选项判定：entry=cond:T/F/lock:T/F（锁按发动方玩家判定）
    private static string OptionLine(ICombatState combat, Player player,
        List<(CardModel Concept, Func<List<CardModel>, bool> Cond)> options, List<CardModel> material)
        => string.Join(" ", options.Select(o => $"{o.Concept.Id.Entry}=cond:{(o.Cond(material) ? "T" : "F")}/lock:{(IsFusionLocked(combat, player, o.Concept) ? "T" : "F")}"));

    // 回合/侧切换时清空该战斗的"本回合已生成"跟踪（文迪戈锁按战斗实例天然隔离，无需手动清）。
    private static void ResetFusionKeys(ICombatState combat)
    {
        FusionLockState st = Locks(combat);
        object turnKey = $"{combat.RoundNumber}:{combat.CurrentSide}";
        if (!Equals(turnKey, st.TurnKey))
        {
            if (st.TurnKey != null)
                FusionLog($"turn-reset {st.TurnKey} -> {turnKey}（本回合生成锁清空）");
            st.TurnKey = turnKey;
            st.TearFusedThisTurn.Clear();
            st.ShaddollFusedThisTurn.Clear();
        }
    }

    private static void RegisterFusionGenerated(ICombatState combat, Player player, CardModel token)
    {
        FusionLockState st = Locks(combat);
        PlayerSet(st.TearFusedThisTurn, player).Add(token.Id);
        PlayerSet(st.ShaddollFusedThisTurn, player).Add(token.Id);
        // 本场战斗只能生成1次：文迪戈（原有）+ 卡雷多哈特（本批反馈："和文迪戈一样"）
        if (token is ElShaddollWendigo or KaleidoHeart)
            PlayerSet(st.BattleLocked, player).Add(token.Id);
        FusionLog($"lock-add {token.Id.Entry}（玩家 {player.NetId}，本回合 {st.TurnKey}" +
            $"{(token is ElShaddollWendigo or KaleidoHeart ? "，本场战斗锁" : "")}）");
    }

    private static bool IsFusionLocked(ICombatState combat, Player player, CardModel concept)
    {
        FusionLockState st = Locks(combat);
        return (st.TearFusedThisTurn.TryGetValue(player, out var tear) && tear.Contains(concept.Id))
            || (st.ShaddollFusedThisTurn.TryGetValue(player, out var shaddoll) && shaddoll.Contains(concept.Id))
            || (st.BattleLocked.TryGetValue(player, out var battle) && battle.Contains(concept.Id));
    }

    // 组合枚举（素材候选预筛用；手牌≤10、弃牌堆影依有限，开销可忽略）
    private static IEnumerable<List<CardModel>> Combinations(List<CardModel> pool, int size)
    {
        CardModel[] buffer = new CardModel[size];
        for (int i = 0; i < size; i++) buffer[i] = pool[i];
        // 迭代式组合（字典序下一个组合）
        while (true)
        {
            yield return new List<CardModel>(buffer);
            int i = size - 1;
            while (i >= 0 && buffer[i] == pool[pool.Count - size + i]) i--;
            if (i < 0) yield break;
            buffer[i] = pool[pool.IndexOf(buffer[i]) + 1];
            for (int j = i + 1; j < size; j++) buffer[j] = pool[pool.IndexOf(buffer[j - 1]) + 1];
        }
    }

    // 素材候选预筛：只显示"至少能参与一个可用融合组合"的牌（选择界面只显示候选，杜绝选出必然无融合的组合）
    private static List<CardModel> ValidMaterialCandidates(ICombatState combat, Player player, List<CardModel> pool,
        int[] sizes, List<(CardModel Concept, Func<List<CardModel>, bool> Cond)> options)
    {
        HashSet<CardModel> useful = new();
        foreach (int size in sizes)
        {
            if (pool.Count < size) continue;
            foreach (var o in options)
            {
                if (IsFusionLocked(combat, player, o.Concept)) continue;
                foreach (List<CardModel> combo in Combinations(pool, size))
                {
                    if (o.Cond(combo))
                        useful.UnionWith(combo);
                    // ⚠ v0.4.35：原来这里 break（每张融合卡只标记"第一个命中的组合"）——同样能参与融合的
                    // 牌会被别的牌"挡枪"而在选材界面里选不了（用户实测：影融时打击不可选）。改为标全部命中组合。
                }
            }
        }
        return pool.Where(useful.Contains).ToList();
    }

    // 生成神影依战斗卡入手牌并登记生成锁（每回合每张1次；文迪戈本场战斗1次）。
    // replayCount>0 时为生成的神影依附加原版「重放」（BaseReplayCount：打出时效果额外执行N次，
    // HiddenGem/Transfigure 同机制，UI自动显示重放提示）。
    private static async Task<CardModel?> GenerateShaddollToken(ICombatState combat, Player player, CardModel pick, bool upgraded, int replayCount = 0)
    {
        CardModel? token = combat.CreateCard(pick, player);
        if (token == null) return null;
        if (upgraded)
        {
            token.UpgradeInternal();
            token.FinalizeUpgradeInternal();
        }
        if (replayCount > 0)
            token.BaseReplayCount += replayCount;
        RegisterFusionGenerated(combat, player, token);
        await CardPileCmd.AddGeneratedCardToCombat(token, PileType.Hand, player);
        FusionLog($"生成 {token.Id.Entry} upgraded={upgraded} replay={replayCount} → 已入手牌");
        return token;
    }

    // 影融主流程（影依融合/神影依融合/魂影依融合/影依·拿非利/影依的伪典/虚影依 神子晶）：
    // 选素材→（手牌素材逐张弃置=被弃置时效果照常触发；弃牌堆素材直接消耗=不触发）→
    // 从条件满足的神影依中选1张生成入手牌（0费消耗，带影依标可作后续素材连锁）。
    // trigger 已升级（或 forceUpgraded=神影依融合）→ 神影依为强化版；素材含已升级的影依的原核 → 同样强化版（问题31 影融+）。
    // includeDraw=true（影依融合强化后、仅精英/Boss战）：素材也可以从卡组选（弃置路径照常触发钩子）。
    // optional=true（影依的伪典能力）：弃牌堆素材0~2可选（不选=不发动）。
    // 选出的素材组合无可用融合时：不弃置不消耗，什么都没发生（照 v0.4.15 珠泪严格判定的自然代价）。
    // replayCount>0（神影依融合）：生成的神影依获得重放（打出时效果额外执行N次）。
    public static Task ShaddollFusion(PlayerChoiceContext ctx, CardModel trigger,
        ShaddollFusionMode mode = ShaddollFusionMode.Hand, bool forceUpgraded = false, bool includeDraw = false,
        int replayCount = 0, bool optional = false)
        => ShaddollFusionCore(ctx, trigger.Owner, trigger, mode, forceUpgraded, includeDraw, replayCount, optional);

    // 问题30：影依的伪典改能力后由能力在回合开始时调用——无触发卡、素材只从弃牌堆0~2张可选消耗、不升级不重放
    // v0.4.37：forceUpgraded=true=强化版伪典（影融+，ShaddollSchismPowerPlus 施加）→ 产出强化版神影依
    public static Task ShaddollFusionFromPower(PlayerChoiceContext ctx, Player player, bool forceUpgraded = false)
        => ShaddollFusionCore(ctx, player, null, ShaddollFusionMode.DiscardExhaust, forceUpgraded, false, 0, optional: true);

    private static async Task ShaddollFusionCore(PlayerChoiceContext ctx, Player player, CardModel? trigger,
        ShaddollFusionMode mode, bool forceUpgraded, bool includeDraw, int replayCount, bool optional)
    {
        ICombatState? combat = player.Creature.CombatState;
        if (combat == null) return;
        ResetFusionKeys(combat);

        // 问题36：含影依的原核的组合按豁免条件判定（WithCoreRule 逐组合改写）
        List<(CardModel Concept, Func<List<CardModel>, bool> Cond)> options =
            WithCoreRule(ShaddollFusionOptions(mode == ShaddollFusionMode.Exempt));

        FusionLog($"cast mode={mode} trigger={trigger?.Id.Entry ?? "（无触发卡）"} upgraded={trigger?.IsUpgraded ?? false} " +
            $"room={player.RunState.CurrentRoom?.RoomType} includeDraw={includeDraw} optional={optional}");

        // 1. 选素材
        List<CardModel> material;
        // ⚠ v0.4.35：可用神影依必须在【素材被弃置/消耗之前】判定一次并复用。
        // 米沙赫雷恶的条件含"素材此刻在手牌"的牌堆判定（c.Pile?.Type == Hand）：v0.4.32 起若在
        // 弃置素材之后再判定一次，素材已进弃牌堆 → 条件必然不成立 → 素材被吃却什么都融不出（静默）。
        List<CardModel> available;
        if (mode == ShaddollFusionMode.DiscardExhaust)
        {
            // 排除触发卡自身（虚影依 神子晶的影融在被弃置时发动，触发时自己已在弃牌堆）
            List<CardModel> pool = DiscardPile(player).Cards
                .Where(c => IsShaddoll(c) && !ReferenceEquals(c, trigger)).ToList();
            List<CardModel> candidates = ValidMaterialCandidates(combat, player, pool, new[] { 2 }, options);
            FusionLog($"pool=弃牌堆 poolN={pool.Count} candidates={candidates.Count}");
            if (candidates.Count < 2) { FusionLog("abort：弃牌堆候选不足2张"); return; }
            material = await PickSomeFromList(ctx, player, candidates, "LIGHTSWORN_SHADDOLL_MATERIAL",
                optional ? 0 : 2, 2);
            FusionLog($"picked n={material.Count}：{string.Join(" ; ", material.Select(MatDescr))}");
            available = options.Where(o => o.Cond(material) && !IsFusionLocked(combat, player, o.Concept))
                .Select(o => o.Concept).ToList();
            if (material.Count != 2 || available.Count == 0)
            {
                FusionLog($"abort：组合无可用融合（不消耗）｜{OptionLine(combat, player, options, material)}");
                return;   // 选出的组合无可用融合：不消耗，留在弃牌堆
            }
            foreach (CardModel card in material)
                await LsCompat.ExhaustCompat(ctx, card);
        }
        else
        {
            int[] sizes = mode == ShaddollFusionMode.Exempt ? new[] { 2 } : new[] { 2, 3 };
            List<CardModel> pool = PileType.Hand.GetPile(player).Cards.ToList();
            int handN = pool.Count;
            // 问题1：从卡组选素材限「影依」牌（用户拍板=控制强度；文案与行为对齐）
            if (includeDraw)
                pool.AddRange(DrawPile(player).Cards.Where(IsShaddoll));
            List<CardModel> candidates = ValidMaterialCandidates(combat, player, pool, sizes, options);
            FusionLog($"pool=手牌{handN}张+卡组影依{pool.Count - handN}张 candidates={candidates.Count}");
            if (candidates.Count < sizes[0]) { FusionLog($"abort：候选不足{sizes[0]}张"); return; }
            material = await PickSomeFromList(ctx, player, candidates, "LIGHTSWORN_SHADDOLL_MATERIAL", sizes[0], sizes[^1]);
            FusionLog($"picked n={material.Count}：{string.Join(" ; ", material.Select(MatDescr))}");
            if (material.Count < sizes[0]) { FusionLog("abort：选牌不足最小张数（素材未动）"); return; }
            available = options.Where(o => o.Cond(material) && !IsFusionLocked(combat, player, o.Concept))
                .Select(o => o.Concept).ToList();
            if (available.Count == 0)
            {
                // ⚠ 已知问题3（v0.5.4，用户订正）：选超素材=**作废**，不做向下兼容降级。
                // 素材弃置发生在本判定之后，故作废时素材原样留在手牌、什么都没发生。
                FusionLog($"abort：组合无可用融合（素材未弃置、作废）｜{OptionLine(combat, player, options, material)}");
                return;
            }

            // 弃置素材（触发各自「被弃置时」效果）：手牌走 CardCmd.Discard，卡组走 MillSelected（Draw→Discard 同样触发管线）
            List<CardModel> handMats = material.Where(c => c.Pile?.Type == PileType.Hand).ToList();
            List<CardModel> drawMats = material.Where(c => c.Pile?.Type == PileType.Draw).ToList();
            FusionLog($"discard 手牌{handMats.Count}张/卡组{drawMats.Count}张");
            if (handMats.Count > 0)
                await CardCmd.Discard(ctx, handMats);
            if (drawMats.Count > 0 && trigger != null)
                await MillSelected(ctx, trigger, drawMats);
        }

        // 2. 可用神影依（素材移动前已判定并复用——不要再在弃置后重新判定，见上）
        FusionLog($"available=[{string.Join(",", available.Select(c => c.Id.Entry))}] handSpace={HandHasSpace(player)}");
        if (available.Count == 0 || !HandHasSpace(player)) { FusionLog("abort：无可用神影依或手牌已满"); return; }
        CardModel? pick = await PickConcept(ctx, player, available, "LIGHTSWORN_SHADDOLL_FUSION");
        if (pick == null) { FusionLog("abort：神影依选择界面取消"); return; }

        // 3. 生成（问题31：素材含已升级的「影依的原核」→ 影融+，产出强化版）
        bool upgraded = (trigger?.IsUpgraded ?? false) || forceUpgraded
            || material.Any(c => c is ShaddollCore && c.IsUpgraded);
        await GenerateShaddollToken(combat, player, pick, upgraded, replayCount);
    }

    // 生成指定神影依（圣影依 商神杖灵"影融出拿非利"，问题32）：遵守生成锁与手牌上限。
    public static async Task<CardModel?> GenerateShaddollByConcept(PlayerChoiceContext ctx, CardModel source,
        CardModel concept, bool upgraded)
    {
        ICombatState? combat = source.Owner.Creature.CombatState;
        if (combat == null || !HandHasSpace(source)) return null;
        ResetFusionKeys(combat);
        if (IsFusionLocked(combat, source.Owner, concept)) return null;
        return await GenerateShaddollToken(combat, source.Owner, concept, upgraded);
    }

    // 直接生成神影依（心影依融合"选一张神影依触发其效果"）：从9张概念卡中选1张生成入手牌，遵守生成锁。
    // zeroDamage=true 时伤害置0（心影依融合）。upgraded=强化版（心影依融合传false，其升级=选2张）。
    // 返回生成的战斗卡（null=没有可用候选/手牌满/取消）。
    public static async Task<CardModel?> PickAndGenerateShaddoll(PlayerChoiceContext ctx, CardModel source,
        bool upgraded, bool zeroDamage)
    {
        ICombatState? combat = source.Owner.Creature.CombatState;
        if (combat == null || !HandHasSpace(source))
        {
            FusionLog($"cast(选神影依) source={source.Id.Entry} abort：无战斗或手牌已满");
            return null;
        }
        ResetFusionKeys(combat);
        List<CardModel> available = ShaddollFusionOptions(exempt: true)
            .Select(o => o.Concept).Where(c => !IsFusionLocked(combat, source.Owner, c)).ToList();
        FusionLog($"cast(选神影依) source={source.Id.Entry} upgraded={upgraded} zeroDamage={zeroDamage} available={available.Count}");
        if (available.Count == 0) { FusionLog("abort：9张神影依全被本回合生成锁挡住"); return null; }
        CardModel? pick = await PickConcept(ctx, source.Owner, available, "LIGHTSWORN_SHADDOLL_FUSION");
        if (pick == null) { FusionLog("abort：选择界面取消"); return null; }
        CardModel? token = await GenerateShaddollToken(combat, source.Owner, pick, upgraded);
        if (token != null && zeroDamage && token.Type == CardType.Attack)
            ZeroDamageOnce(token);
        return token;
    }

    // ============ 融合图鉴（v0.4.19 问题4） ============
    // 图鉴展示的全部融合卡概念卡（珠泪4 + 神影依9，基础版）
    public static List<CardModel> FusionCodexConcepts() => new()
    {
        ModelDb.Card<Kitkallos>(), ModelDb.Card<Rulkallos>(),
        ModelDb.Card<KaleidoHeart>(), ModelDb.Card<Dragostapelia>(),
        ModelDb.Card<ElShaddollWinda>(), ModelDb.Card<ElShaddollConstruct>(),
        ModelDb.Card<ElShaddollWendigo>(), ModelDb.Card<ElShaddollGrysta>(),
        ModelDb.Card<ElShaddollShekhinaga>(), ModelDb.Card<ElShaddollAnoyatyllis>(),
        ModelDb.Card<ElShaddollApkallone>(), ModelDb.Card<ElShaddollMeshahrail>(),
        ModelDb.Card<ReeshaddollWendikurhu>(),
    };

    // 图鉴置灰判定：珠泪/影依融合「本回合已生成」（两引擎统一登记，双查）或文迪戈「本场战斗已生成」。
    // 状态按战斗实例隔离（v0.4.29）：回合计数在实例内推进，跨战斗/读档重打自动全新。
    // v0.5.1：按玩家判定——图鉴显示的是"当前查看玩家自己"的本回合生成记录（联机不串）。
    public static bool IsFusionUsedForCodex(ICombatState combat, Player player, CardModel concept)
    {
        FusionLockState st = Locks(combat);
        object turnKey = $"{combat.RoundNumber}:{combat.CurrentSide}";
        if (Equals(turnKey, st.TurnKey) &&
            ((st.TearFusedThisTurn.TryGetValue(player, out var tear) && tear.Contains(concept.Id))
             || (st.ShaddollFusedThisTurn.TryGetValue(player, out var shaddoll) && shaddoll.Contains(concept.Id)))) return true;
        return st.BattleLocked.TryGetValue(player, out var battle) && battle.Contains(concept.Id);
    }

    // ============ 影依弃置触发管线 ============
    // 影依牌被弃置（弃光=Draw→Discard，或手牌弃置；打出不触发）时由 ShaddollCard/ShaddollToken 双钩子调到这里：
    // 1) 触发该牌的「被弃置时」效果——堕影的蠢动/翼影依影文蒂在场时改为触发2次（加法叠加，同在场=3次）；
    // 2) 影牢之咒缚：每次弃置事件获得1层镀层（与触发次数无关，一次弃置只通知1次）。
    // 问题5：联动计数只认带「影依」标的卡——堕影的蠢动/影牢之咒缚/炼狱的乖放等无影依字样的卡
    // 被弃置只走自己的 OnDiscardedEffect（它们本来就没有），不消耗影文蒂层数、不触发蠢动加倍、不计咒缚。
    public static async Task OnShaddollDiscarded(PlayerChoiceContext ctx, CardModel card)
    {
        bool isShaddoll = IsShaddoll(card);
        Player player = card.Owner;
        int times = 1;
        if (isShaddoll && player.Creature.Powers.OfType<SinisterShadowGamesPower>().Any())
            times++;
        WendikurhuPower? wendikurhu = player.Creature.Powers.OfType<WendikurhuPower>().FirstOrDefault();
        if (isShaddoll && wendikurhu is { Amount: > 0 })
        {
            times++;
            await PowerCmd.Decrement(wendikurhu);
        }
        if (card is ShaddollCard shaddoll)
            for (int i = 0; i < times; i++)
                await shaddoll.OnDiscardedEffect(ctx);
        if (!isShaddoll) return;
        CurseShadowPrisonPower? curse = player.Creature.Powers.OfType<CurseShadowPrisonPower>().FirstOrDefault();
        if (curse != null)
            await curse.OnShaddollDiscarded(ctx);
    }

    // ============ "本回合不能打出"（影依巫女从消耗堆回收的牌） ============
    // 回合键控的打出锁：IsPlayable 拦截（BlockedByCardLogic），回合切换自动失效；战斗切换时整体清空。
    // 本批问题9 bug：锁必须按**卡牌实例**记录——原先用 ModelId（卡名）做键，巫女锁了1张神影依后，
    // 本回合融合出的同名神影依也被"连坐"不能打出；且回合失效判定只在加锁时执行过，没人再加锁时
    // 旧锁永不失效。现在：实例集合 + 查询时同步做回合失效判定。
    private static readonly HashSet<CardModel> _playLockedThisTurn = new();   // CardModel 未重写 Equals=引用相等
    private static ICombatState? _playLockCombat;
    private static object? _playLockTurnKey;

    public static void LockPlayThisTurn(CardModel card)
    {
        ICombatState? combat = card.Owner.Creature.CombatState;
        if (combat == null) return;
        if (!ReferenceEquals(_playLockCombat, combat))
        {
            _playLockCombat = combat;
            _playLockTurnKey = null;
            _playLockedThisTurn.Clear();
        }
        object turnKey = $"{combat.RoundNumber}:{combat.CurrentSide}";
        if (!Equals(turnKey, _playLockTurnKey))
        {
            _playLockTurnKey = turnKey;
            _playLockedThisTurn.Clear();
        }
        _playLockedThisTurn.Add(card);
    }

    public static bool IsPlayLocked(CardModel card)
    {
        ICombatState? combat = card.Owner.Creature.CombatState;
        if (combat == null || !ReferenceEquals(_playLockCombat, combat)) return false;
        // 已过回合（含敌方侧）→ 旧锁失效（无加锁调用方时也能自动解锁）
        if (!Equals($"{combat.RoundNumber}:{combat.CurrentSide}", _playLockTurnKey)) return false;
        return _playLockedThisTurn.Contains(card);
    }

    // 每层随机选一种原版负面状态（易伤/虚弱/中毒/灾厄），施加到所有目标各1层；
    // 每次另有 1% 概率改为击晕所有目标（残响同款 CreatureCmd.Stun，不属于可被人工制品抵消的能力）。
    // 均为 PowerType.Debuff 的可见能力：人工制品（ArtifactPower）会自动抵挡。
    // RNG 必须用玩家侧 RunState（坑5：creature.Player 对怪物为 null）。
    public static async Task ApplyRandomDebuffs(PlayerChoiceContext ctx, Player player, List<Creature> targets, int stacks)
    {
        if (targets.Count == 0) return;
        Creature applier = player.Creature;
        for (int i = 0; i < stacks; i++)
        {
            if (player.RunState.Rng.CombatCardSelection.NextInt(100) == 0)
            {
                foreach (Creature target in targets.Where(t => t.IsAlive))
                    await CreatureCmd.Stun(target);
                continue;
            }
            switch (player.RunState.Rng.CombatCardSelection.NextInt(4))
            {
                case 0: await PowerCmd.Apply<VulnerablePower>(ctx, targets, 1, applier, null); break;
                case 1: await PowerCmd.Apply<WeakPower>(ctx, targets, 1, applier, null); break;
                case 2: await PowerCmd.Apply<PoisonPower>(ctx, targets, 1, applier, null); break;
                default: await PowerCmd.Apply<DoomPower>(ctx, targets, 1, applier, null); break;
            }
        }
    }

    // 生成一张战斗内临时Token牌并置入指定牌堆（裁决之龙/惩戒之龙的Token）。
    // ethereal=虚无（回合结束在手牌中会消耗），exhaust=消耗（打出后消耗），retain=保留（回合结束不弃置）。
    // Token用AddKeyword动态加关键词。
    public static async Task<CardModel?> CreateToken<T>(PlayerChoiceContext ctx, CardModel source, PileType pile,
        bool ethereal = false, bool exhaust = false, bool retain = false) where T : CardModel
    {
        CardModel? token = source.Owner.Creature.CombatState?.CreateCard<T>(source.Owner);
        if (token == null) return null;
        if (ethereal) token.AddKeyword(CardKeyword.Ethereal);
        if (exhaust) token.AddKeyword(CardKeyword.Exhaust);
        if (retain) token.AddKeyword(CardKeyword.Retain);
        await CardPileCmd.AddGeneratedCardToCombat(token, pile, source.Owner);
        return token;
    }

    // "被弃置时自动打出"（本批问题33 古尖兵/古卫兵）：弃光（Draw→Discard）与手牌弃置都触发；
    // 无战斗状态（战斗收尾）时跳过防 AutoPlay 异常；打出自身不触发（Play→Discard 不匹配该判定）。
    public static async Task AutoPlayOnDiscard(CardModel card)
    {
        if (card.Pile?.Type != PileType.Discard) return;
        if (card.Owner.Creature.CombatState == null) return;
        await CardCmd.AutoPlay(new BlockingPlayerChoiceContext(), card, null);
    }

    public static bool HandHasSpace(CardModel card) => HandHasSpace(card.Owner);

    public static bool HandHasSpace(Player player)
        => PileType.Hand.GetPile(player).Cards.Count < CardPile.MaxCardsInHand;

    // "被弃光时自动加入手牌"的共用钩子（沃尔夫/费莉丝/光道细剑）。
    // recallCost0=true 时同时把费用变为0（细剑）；返回true表示发生了回收。
    public static async Task<bool> TryRecallOnMill(CardModel card, bool recallCost0)
    {
        if (card.Pile?.Type != PileType.Discard) return false;
        if (!HandHasSpace(card)) return false;
        await CardPileCmd.Add(card, PileType.Hand);
        if (recallCost0)
            card.EnergyCost.SetThisTurnOrUntilPlayed(0);
        return true;
    }

    public static LocString Prompt(string key) => new("card_selection", key);
}
