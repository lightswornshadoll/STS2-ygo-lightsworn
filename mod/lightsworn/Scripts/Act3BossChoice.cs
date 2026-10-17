using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Acts;
using MegaCrit.Sts2.Core.Models.Encounters;
using MegaCrit.Sts2.Core.Nodes;
using MegaCrit.Sts2.Core.Nodes.Screens.Map;
using MegaCrit.Sts2.Core.Rooms;
using MegaCrit.Sts2.Core.Runs;
using STS2RitsuLib;

namespace Lightsworn;

// ============ 事件：第三层首领的抉择 ============
// 触发点：第二层 Boss 奖励领完、Act 2→3 过渡完成之后，第三层地图出现之前（RitsuLib ActEnteredEvent）。
// 第三层 Boss 在 RunManager.GenerateRooms（整局开局）时已经随机确定；MapCmd.SetBossEncounter 可以在
// 进入 Boss 房之前整体替换，所以这里不需要重掷三层房间。
// 保留第三层原有的先古事件：本事件是地图出现前额外插入的独立事件房，结束后地图正常打开，
// 玩家仍可进入起始 Ancient 节点（原版先古祝福不受影响）。
// 注册为「三层 ActEvent」而不是 shared event：模型仍会被 ModelDb 收录，但只挂到 Glory 的事件表；
// IsAllowed=false 再把它从随机抽取里过滤掉，避免影响一、二层的事件/房间 RNG。
[RegisterActEvent(typeof(Glory))]
public sealed class ThirdActBossChoiceEncounter : ModEventTemplate
{
    // 只为手动触发存在：IsAllowed=false 让 ActModel.EnsureNextEventIsValid 在普通事件抽取时跳过它，
    // 避免它混进第三层的随机事件池。手动 EnterRoom 不检查 IsAllowed。
    public override bool IsAllowed(IRunState runState) => false;

    // 改写的是全队共用的第三层 Boss，必须走共享事件投票，多人两端才会执行同一个选择。
    public override bool IsShared => true;

    // 复用格拉法立绘（pck 里已有）；以后要做专用 event 图时只改这里。
    public override string? CustomInitialPortraitPath
        => "res://lightsworn/images/monsters/dark_world_grapha.png";

    protected override IReadOnlyList<EventOption> GenerateInitialOptions()
    {
        return
        [
            new EventOption(this, ChooseModBoss, InitialOptionKey("CHOOSE_MOD")),
            new EventOption(this, ChooseVanillaBoss, InitialOptionKey("CHOOSE_VANILLA")),
        ];
    }

    private Task ChooseModBoss() => ChooseBoss(useModBosses: true);

    private Task ChooseVanillaBoss() => ChooseBoss(useModBosses: false);

    private Task ChooseBoss(bool useModBosses)
    {
        IRunState runState = Owner!.RunState;
        List<EncounterModel> all = runState.Act.AllBossEncounters
            .Where(e => e is not DeprecatedEncounter)
            .ToList();

        // mod Boss = 本 mod 程序集里的遭遇；原版 Boss = 游戏本体程序集里的遭遇。
        // 其他 mod 注册到 Glory 的 Boss 不归这里管，两个池都不收，避免误改别家内容。
        List<EncounterModel> pool = all
            .Where(e => IsModBoss(e) == useModBosses)
            .ToList();
        if (pool.Count == 0)
        {
            pool = all;
        }
        if (pool.Count == 0)
        {
            SetEventFinished(L10NLookup($"{Id.Entry}.pages.NO_BOSS.description"));
            return Task.CompletedTask;
        }

        EncounterModel chosen = pool[Rng.NextInt(pool.Count)];

        // 进阶 10 双 Boss：第二个 Boss 也按同一选择重掷，排除刚选中的第一个。
        // 先改第二个再走 MapCmd（它会重建地图/顶栏图标），否则第二个 Boss 图标可能是旧的。
        if (runState.Act.SecondBossEncounter != null)
        {
            List<EncounterModel> secondPool = pool.Where(e => e.Id != chosen.Id).ToList();
            if (secondPool.Count > 0)
            {
                runState.Act.SetSecondBossEncounter(secondPool[Rng.NextInt(secondPool.Count)]);
            }
        }

        MapCmd.SetBossEncounter(runState, chosen);

        LocString done = L10NLookup($"{Id.Entry}.pages.DONE.description");
        done.Add("Boss", chosen.Title);
        SetEventFinished(done);
        return Task.CompletedTask;
    }

    private static bool IsModBoss(EncounterModel encounter)
        => encounter.GetType().Assembly == typeof(LightswornCharacter).Assembly;

    internal static bool ActHasModBoss(IRunState runState)
        => runState.Act.AllBossEncounters.Any(IsModBoss);
}

// ActEnteredEvent 在 EnterAct 完成（地图/Act 房间已经打开）之后发布；这里把它切成
// 「关地图 → 事件房 → 事件 Proceed 后地图重新打开」。事件房结束不会标记起始 Ancient 节点，
// 因此玩家随后仍能正常进入原版第三层先古事件。
internal static class ThirdActBossChoiceTrigger
{
    private static IRunState? _shownForRun;

    public static void OnActEntered(ActEnteredEvent evt)
    {
        if (evt.CurrentActIndex != 2 || !ThirdActBossChoiceEncounter.ActHasModBoss(evt.RunState))
        {
            return;
        }
        if (ReferenceEquals(_shownForRun, evt.RunState))
        {
            return;
        }
        _shownForRun = evt.RunState;
        TaskHelper.RunSafely(ShowAsync(evt.RunState));
    }

    private static async Task ShowAsync(IRunState runState)
    {
        await Task.Yield();

        NMapScreen? map = NMapScreen.Instance;
        if (map != null)
        {
            map.SetTravelEnabled(enabled: false);
            map.Close(animateOut: false);
        }

        RunManager runManager = RunManager.Instance;
        // 0.107.1 没有 RunManager.FadeOut/FadeIn（0.111 才加），这里走两端都有的 NTransition。
        await NGame.Instance.Transition.RoomFadeOut();
        await runManager.EnterRoom(new EventRoom(ModelDb.Event<ThirdActBossChoiceEncounter>()));
        await NGame.Instance.Transition.RoomFadeIn();
    }
}
