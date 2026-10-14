using System.Runtime.CompilerServices;
using System.Threading.Tasks;
using HarmonyLib;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Context;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.GameActions;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Multiplayer.Game;
using MegaCrit.Sts2.Core.Nodes;
using MegaCrit.Sts2.Core.Nodes.Screens;
using MegaCrit.Sts2.Core.Nodes.Screens.Map;
using MegaCrit.Sts2.Core.Nodes.Screens.Overlays;
using MegaCrit.Sts2.Core.Runs;
using MegaCrit.Sts2.Core.Saves;
using MegaCrit.Sts2.Core.TestSupport;
using STS2RitsuLib.Patching.Models;

namespace Lightsworn;

// ============ 初始遗物二选一（v0.4.16；v0.4.17 修选人后开局黑屏；v0.5.1 联机一致性重做） ============
// 新开局用原版「选择遗物」覆盖界面（NChooseARelicSelection）让玩家在「你必须玩游戏王」和
// 「光道圣徽」里挑一个当初始遗物；跳过 = 保持「你必须玩游戏王」。圣徽在遗物池的掉落不受影响
// （被选为初始遗物时 RelicCmd.Obtain 会把它从本局 RelicGrabBag 移除，IsStackable=false，不会刷出第二个）。
//
// 实现 = 换掉 RunManager.FinalizeStartingRelics 返回的 Task：先原样跑完原逻辑（初始遗物逐个
// AfterObtained），然后**在同样的确定性时点预定全部目标玩家的选择 ID**（见下），最后把弹窗挪进独立任务。
// ⚠ 弹窗绝不能在这里同步做（v0.4.16 事故）：原版界面要压进 NOverlayStack（= NRun.GlobalUi.Overlays），
// 而 NRun 场景要到 StartRun 后半段 SetCurrentScene(NRun.Create(...)) 才创建——在 FinalizeStartingRelics
// 里弹 = NOverlayStack.Instance 为 null 抛 NRE，中断 StartRun → 选人转场后永久黑屏。
// 且 StartRun 的 EnterAct(0) 开头还有 ClearScreens()（NOverlayStack.Clear）会清掉早弹的界面。
// 所以独立任务等到「NRun 已建 + 已过 ClearScreens + 地图界面已显示或已进首个房间」再弹（正常开局
// 就是地图出现的瞬间，压深色背板，与原版珠宝盒类局内界面同款表现）；选择流程再出异常只记日志
// （保持游戏王），不再打断开局。Launch() 在 FinalizeStartingRelics 之后马上赋值 LocalContext.NetId，
// 弹窗时 IsMe 天然正确，v0.4.16 的坑18手动补丁随之作废。读档（LoadRun）不走本方法，不弹窗。
//
// ⚠ v0.5.1 联机（Multiplayer）：
// 玩家选择由 PlayerChoiceSynchronizer 按「玩家槽位自增 ID」同步，且该 ID 向量进战斗校验和——
// **必须全端在同一确定性时点、按同一顺序预定**，否则队友抢先出牌/进房预定到别的 ID 时会向量分叉，
// 第一个校验和就判定分歧断线（StateDivergence）。因此预定被移进 FinalizeThenOffer（= StartRun 的
// await 段，各端都跑且此刻任何玩家都无法行动），按 state.Players 顺序一次性预定；
// 弹窗任务里只用预定的 ID 做 本地开界面+SyncLocalChoice / 远端 WaitForRemoteChoice 配对
// （ChooseRelicCompat = RelicSelectCmd.FromChooseARelicScreen 的等价实现，区别只是 ID 预定时点）。
// 界面异常时同步一个"跳过"结果——否则等待端永远停在 WaitForRemoteChoice（联机挂起）。
internal sealed class StartingRelicChoicePatch : IPatchMethod
{
    public static string PatchId => "lightsworn_starting_relic_choice";
    public static string Description => "Offer a starting relic choice after FinalizeStartingRelics";

    public static ModPatchTarget[] GetTargets() =>
        [new ModPatchTarget(typeof(RunManager), nameof(RunManager.FinalizeStartingRelics))];

    // 单次开局只问一次（单人/多人/bootstrap 多入口都可能调到 FinalizeStartingRelics），按 RunState 实例去重
    private static readonly ConditionalWeakTable<RunState, object?> Prompted = new();

    public static bool Prefix(RunManager __instance, ref Task __result)
    {
        if (TestMode.IsOn) return true;

        // RunManager.State 是 private，用 Traverse 读
        RunState? state = Traverse.Create(__instance).Property("State").GetValue<RunState?>();
        if (state == null || __instance.PlayerChoiceSynchronizer == null) return true;

        List<Player> targets = state.Players
            .Where(p => p.Character is LightswornCharacter && p.Relics.Any(r => r is MustPlayYugioh))
            .ToList();
        if (targets.Count == 0) return true;
        if (!Prompted.TryAdd(state, null)) return true;

        __result = FinalizeThenOffer(__instance, state, targets);
        return false;
    }

    private static async Task FinalizeThenOffer(RunManager runManager, RunState state, List<Player> targets)
    {
        // 原版 FinalizeStartingRelics 的全部逻辑（走到这里的 run 已确认含光道玩家）
        foreach (Player player in state.Players)
        {
            foreach (RelicModel relic in player.Relics)
            {
                await relic.AfterObtained();
            }
        }

        // ⚠ 联机：选择 ID 在确定性时点按 state.Players 顺序一次性预定（全部目标；见类注释）。
        // 各端都在这里跑（FinalizeStartingRelics 被 StartRun await，玩家此刻都还无法行动），顺序一致。
        List<(Player Target, uint ChoiceId)> reserved = new();
        foreach (Player player in targets)
            reserved.Add((player, runManager.PlayerChoiceSynchronizer.ReserveChoiceId(player)));
        Log.Info($"[Lightsworn] 初始遗物选择：已预定 {reserved.Count} 个选择 ID" +
            $"（联机={runManager.NetService.Type != NetGameType.Singleplayer}，玩家={string.Join(",", targets.Select(p => p.NetId))}）");

        // 不 await：StartRun 还要走 Launch → 建 NRun 场景 → EnterAct(0)，弹窗等那边就绪（见类注释）
        _ = OfferChoiceWhenRunReady(state, reserved);
    }

    private static async Task OfferChoiceWhenRunReady(RunState state, List<(Player Target, uint ChoiceId)> targets)
    {
        try
        {
            // 等 NRun 场景 + overlay 栈可用，且已过 EnterAct(0) 开头的 ClearScreens()：
            // 「地图界面已显示」（正常开局）或「已进首个房间」（带初始事件的开局）二者其一即安全
            bool sawRun = false;
            for (int i = 0; i < 2400; i++)   // 0.05s × 2400 = 2 分钟上限，正常几秒内就绪
            {
                if (NRun.Instance == null)
                {
                    if (sawRun) return;      // run 已结束（回主菜单），放弃弹窗
                }
                else
                {
                    sawRun = true;
                    if (NOverlayStack.Instance != null
                        && ((NMapScreen.Instance?.IsVisibleInTree() ?? false) || state.CurrentRoom != null))
                    {
                        break;
                    }
                }
                await Cmd.Wait(0.05f, ignoreCombatEnd: true);
            }

            if (NRun.Instance == null || NOverlayStack.Instance == null) return;   // 超时放弃
            await Cmd.Wait(0.3f, ignoreCombatEnd: true);   // 等 EnterAct 的 FadeIn 收尾

            foreach ((Player player, uint choiceId) in targets)
            {
                MustPlayYugioh? yugioh = player.Relics.OfType<MustPlayYugioh>().FirstOrDefault();
                if (yugioh == null) continue;

                RelicModel? chosen = await ChooseRelicCompat(player, yugioh, choiceId);
                if (chosen == null || ReferenceEquals(chosen, yugioh)) continue;

                await RelicCmd.Replace(yugioh, chosen);
                // 对齐原版 PopulateStartingRelics 的初始标记（Replace→Obtain 写入的是 TotalFloor，开局时为 0）
                chosen.FloorAddedToDeck = 1;
            }
        }
        catch (Exception e)
        {
            // 界面被局内 ClearScreens 清掉（多人队友抢先进图等）也会到这：记日志，保持游戏王
            Log.Error($"[Lightsworn] 初始遗物二选一未完成（保持「你必须玩游戏王」）：{e}");
        }
    }

    // 选择本体 = RelicSelectCmd.FromChooseARelicScreen 的等价实现（区别=选择 ID 已预先预定，见 FinalizeThenOffer）。
    // 本地玩家=弹原版界面（点谁返回谁，跳过返回 null），远端玩家=等待其选择消息；两端用同一预定 ID 配对。
    // ⚠ 界面异常也必须同步一个"跳过"结果：否则等待端永远停在 WaitForRemoteChoice（联机挂起）。
    private static async Task<RelicModel?> ChooseRelicCompat(Player player, MustPlayYugioh yugioh, uint choiceId)
    {
        PlayerChoiceSynchronizer sync = RunManager.Instance.PlayerChoiceSynchronizer;
        // 圣徽给全新可变实例（玩家手上没有）；列表两端同序（[游戏王, 圣徽]）、线上只传下标
        List<RelicModel> options = [yugioh, ModelDb.Relic<LightswornSigil>().ToMutable()];

        if (LocalContext.IsMe(player) && RunManager.Instance.NetService.Type != NetGameType.Replay)
        {
            int index = -1;
            try
            {
                foreach (RelicModel relic in options)
                    SaveManager.Instance.MarkRelicAsSeen(relic);
                NChooseARelicSelection screen = NChooseARelicSelection.ShowScreen(options);
                RelicModel? picked = (await screen.RelicsSelected()).FirstOrDefault();
                index = picked == null ? -1 : options.IndexOf(picked);
            }
            catch (Exception e)
            {
                Log.Error($"[Lightsworn] 初始遗物界面异常（按跳过处理，保持游戏王）：{e}");
            }
            sync.SyncLocalChoice(player, choiceId, PlayerChoiceResult.FromIndex(index));
            return index < 0 || index >= options.Count ? null : options[index];
        }

        int remote = (await sync.WaitForRemoteChoice(player, choiceId)).AsIndex();
        return remote < 0 || remote >= options.Count ? null : options[remote];
    }
}
