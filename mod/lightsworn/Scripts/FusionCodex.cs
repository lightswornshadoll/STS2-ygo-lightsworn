using Godot;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Nodes.Cards;
using MegaCrit.Sts2.Core.Nodes.Cards.Holders;
using MegaCrit.Sts2.Core.Nodes.Screens;
using MegaCrit.Sts2.Core.Nodes.Screens.Capstones;
using STS2RitsuLib.TopBar;

namespace Lightsworn;

// ============ 融合图鉴（v0.4.19 问题4；v0.5.0 迁 RitsuLib 顶栏按钮） ============
// 点击展示全部13张融合卡（珠泪4 + 神影依9，基础版）；战斗中本回合已生成过的卡整格置灰
// （文迪戈=本场战斗已生成也置灰），复用 LsUtil 的生成锁状态。
// 界面=原版 NCardPileScreen（抽/弃/消耗堆同款，"任意牌堆"传 PileType.Deck 走牌库视图渲染路径）。
// v0.5.0：按钮从"自 patch NTopBar + 自建 NButton 子类"改为 RitsuLib ModTopBarButtonRegistry
// （自动挂在「卡组」左侧、自动绑定本地玩家、带手柄导航）；用 Register(全局ID) 保留旧 loc 键
// LIGHTSWORN_FUSION_CODEX.title/.description（static_hover_tips 表）。
internal static class FusionCodexUI
{
    private static CardPile? _codexPile;

    // 打开图鉴的玩家（watcher 逐帧取战斗状态用；随图鉴界面回收）
    internal static Player? LocalPlayer { get; private set; }

    internal static void Register()
    {
        ModTopBarButtonRegistry.For("lightsworn").Register("LIGHTSWORN_FUSION_CODEX", new ModTopBarButtonSpec
        {
            IconPath = "res://lightsworn/images/ui/fusion_codex.png",
            Order = 100,
            OnClick = Toggle,
            VisibleWhen = static ctx => ctx.Player?.Character is LightswornCharacter,
        });
    }

    private static void Toggle(ModTopBarButtonContext ctx)
    {
        try
        {
            // 已打开时再点=关闭（照卡组按钮的 toggle 行为；只认自己那次打开的界面）
            if (NCapstoneContainer.Instance.CurrentCapstoneScreen is NCardPileScreen current && current.Pile == _codexPile)
            {
                NCapstoneContainer.Instance.Close();
                return;
            }

            CardPile pile = new(PileType.Deck);
            foreach (CardModel concept in LsUtil.FusionCodexConcepts())
            {
                CardModel clone = (CardModel)concept.MutableClone();
                pile.AddInternal(clone, -1, silent: true);
            }
            _codexPile = pile;
            LocalPlayer = ctx.Player;
            NCardPileScreen screen = NCardPileScreen.ShowScreen(pile, Array.Empty<string>());
            AddChildDeferred(screen, new FusionLockWatcher());
        }
        catch (Exception e)
        {
            Log.Warn($"FusionCodex open failed: {e}");
        }
    }

    private static void AddChildDeferred(Node parent, Node child)
    {
        if (parent.IsInsideTree()) parent.AddChild(child);
        else parent.CallDeferred(Node.MethodName.AddChild, child);
    }
}

// 置灰 watcher：挂在 NCardPileScreen 下逐帧刷新（13格，开销可忽略）。
// 牌堆里的卡是概念卡的可变克隆，Id 与概念卡一致，直接对生成锁 HashSet 判定。
internal sealed partial class FusionLockWatcher : Node
{
    private static readonly Color LockedTint = new(0.45f, 0.45f, 0.5f, 1f);

    public FusionLockWatcher()
    {
        Name = "LightswornFusionLockWatcher";
    }

    public override void _Process(double delta)
    {
        if (GetParent() is not NCardPileScreen screen) return;
        NCardGrid? grid = screen.GetNodeOrNull<NCardGrid>("CardGrid");
        if (grid == null) return;
        Player? me = FusionCodexUI.LocalPlayer;
        ICombatState? combat = me?.Creature?.CombatState;
        foreach (Node node in Descendants(grid))
        {
            if (node is not NCardHolder holder || holder.CardModel == null) continue;
            bool locked = combat != null && LsUtil.IsFusionUsedForCodex(combat, holder.CardModel);
            holder.Modulate = locked ? LockedTint : Colors.White;
        }
    }

    private static IEnumerable<Node> Descendants(Node root)
    {
        foreach (Node child in root.GetChildren())
        {
            yield return child;
            foreach (Node sub in Descendants(child))
                yield return sub;
        }
    }
}
