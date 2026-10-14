using MegaCrit.Sts2.Core.CardSelection;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;

namespace Lightsworn;

// ============ 选牌界面（v0.5.0 迁移：BaseLib.Commands.MultiPileCardSelect → 游戏原生 CardSelectCmd.FromSimpleGrid） ============
// 语义与旧实现一致：界面只显示候选牌、按 prefs 的 min/max 选取、候选不足 min 时自动全选、
// 多人同步走 FromSimpleGrid 内建。**失去"牌堆来源角标"**（BaseLib 的 NPCardGrid transpiler 牌堆标记；
// 游戏本体没有这套 UI，0.111 与 0.107.1 的 FromSimpleGrid 签名完全一致是双版本兼容的首选）。
// 保留类名/方法名与旧调用点一致，卡牌文件无需改动。
public static class MultiPileCardSelect
{
    public static async Task<IEnumerable<CardModel>> Select(PlayerChoiceContext context, Player player,
        CardSelectorPrefs prefs, List<CardModel> cards, PileType[]? pileTypes = null)
    {
        if (cards.Count == 0) return [];
        return await CardSelectCmd.FromSimpleGrid(context, cards, player, prefs);
    }
}
