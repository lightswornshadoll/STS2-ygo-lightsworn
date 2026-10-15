using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Cards;
using MegaCrit.Sts2.Core.Runs;

namespace Lightsworn;

// ============ 事件：于珍珠世界相逢 ============
// 珠泪哀歌族三姐妹（塞壬/梅洛/小美人鱼）在珍珠色的浅滩与玩家相遇。
// 仅光道角色可见（IsAllowed 按角色过滤）。
// 选项一：三姐妹加入卡组（各得1张塞壬人鱼/梅洛人鱼/小美人鱼，悬停选项可预览卡面）
//         + 本批问题1：还要获得诅咒牌「腐朽」（原版 Decay：不可打出，回合结束时在手牌中→受到2点伤害）；
// 选项二（本批改）：不再直接给金币，改为获得事件遗物「幻色珍珠」PhantomPearl
//         （拾起时随机变成金色珍珠/诅咒珍珠的效果，1%概率为发光珍珠的效果；图标=金色珍珠染珠泪蓝）。
// 人设（本批改）：梅洛活泼、小美人鱼安静——两位的身份性格全文案对调。
// 机制（v0.5.0 RitsuLib 迁移）：ModEventTemplate + [RegisterSharedEvent] 注册（不再构造自注册、
// Entry.Init 不再手动 new）；选项 loc 键=InitialOptionKey（{Entry}.pages.INITIAL.options.{键}，与旧格式一致）。
// 本地化=mod localization\zhs\events.json（按文件名并入游戏 events 表），选项键=方法名蛇形大写。
// 发卡/发遗物=原版 TheLegendsWereTrue / GraveOfTheForgotten 范式（RunState.CreateCard + CardPileCmd.Add(Deck) +
// PreviewCardPileAdd；RelicCmd.Obtain<T>(Owner)）。
[RegisterSharedEvent]
public sealed class PearlWorldEncounter : ModEventTemplate
{
    // 必须覆写：默认路径指向游戏本体 res://images/events/<entry小写>.png（mod 立绘不在那里），
    // 预载失败会被 AssetCache.MarkAssetFailed 标记，进事件房时 CreateInitialPortrait 抛
    // AssetLoadException 中断 SetupLayout → 标题/描述/选项全不渲染 → 黑屏卡死（v0.4.26 事故）。
    // ⚠ 文件名=类名蛇形小写（pearl_world_encounter.png），不带 mod 前缀（v0.4.27 二次踩坑）。
    public override string? CustomInitialPortraitPath
        => "res://lightsworn/images/events/pearl_world_encounter.png";

    public override bool IsAllowed(IRunState runState)
        => runState.Players.All(p => p.Character is LightswornCharacter);

    protected override IReadOnlyList<EventOption> GenerateInitialOptions()
    {
        List<IHoverTip> mermaidTips = new();
        mermaidTips.AddRange(HoverTipFactory.FromCardWithCardHoverTips<Suliek>());
        mermaidTips.AddRange(HoverTipFactory.FromCardWithCardHoverTips<Havnis>());
        mermaidTips.AddRange(HoverTipFactory.FromCardWithCardHoverTips<Merrli>());
        mermaidTips.AddRange(HoverTipFactory.FromCardWithCardHoverTips<Decay>());   // 问题1：附带的诅咒「腐朽」
        return
        [
            new EventOption(this, JoinTearlaments, InitialOptionKey("JOIN_TEARLAMENTS"), mermaidTips),
            // 选项二：收下幻色珍珠（悬停预览遗物；原版 GraveOfTheForgotten 范式）
            new EventOption(this, TakePearls, InitialOptionKey("TAKE_PEARLS"),
                HoverTipFactory.FromRelic<PhantomPearl>()),
        ];
    }

    // 选项一：三张珠泪人鱼加入卡组（逐张播放入组动画）+ 1张诅咒牌「腐朽」（本批问题1）
    private async Task JoinTearlaments()
    {
        await AddToDeck<Suliek>();
        await AddToDeck<Havnis>();
        await AddToDeck<Merrli>();
        await AddToDeck<Decay>();
        await Cmd.CustomScaledWait(0.5f, 1.2f);   // TheLegendsWereTrue 范式：等入组动画播完再切结局页
        SetEventFinished(L10NLookup($"{Id.Entry}.pages.JOIN.description"));
    }

    private async Task AddToDeck<T>() where T : CardModel
    {
        CardModel card = Owner.RunState.CreateCard<T>(Owner);
        CardCmd.PreviewCardPileAdd(await CardPileCmd.Add(card, PileType.Deck));
    }

    // 选项二（本批改）：获得事件遗物「幻色珍珠」（拾起时随机变成金/诅咒珍珠的效果，1%发光珍珠）
    private async Task TakePearls()
    {
        await RelicCmd.Obtain<PhantomPearl>(Owner);
        SetEventFinished(L10NLookup($"{Id.Entry}.pages.PEARLS.description"));
    }
}
