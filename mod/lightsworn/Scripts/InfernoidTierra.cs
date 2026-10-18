using Godot;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Commands.Builders;
using MegaCrit.Sts2.Core.Entities.Ascension;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Acts;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.MonsterMoves.Intents;
using MegaCrit.Sts2.Core.MonsterMoves.MonsterMoveStateMachine;
using MegaCrit.Sts2.Core.Nodes.Combat;
using MegaCrit.Sts2.Core.Random;
using MegaCrit.Sts2.Core.Rooms;
using MegaCrit.Sts2.Core.ValueProps;
using STS2RitsuLib.Patching.Models;

namespace Lightsworn;

// ================= 狱火机·提耶拉 / 创星神·提耶拉（三层双阶段超规格 Boss） =================
// 设计基线：design\提耶拉boss设计.md v0.8。
// 一阶段：融合素材数（1-10）= 本回合动作等级；诅咒被弃置时引爆；3/5/8/10 阈值。
// 二阶段：创星 0-10；四招循环；真正引爆诅咒种类 +1；到 10 用「创星·灭世」重罚。
// 全部随机数使用 monster.Rng（联机确定性）。
[RegisterMonster]
public class InfernoidTierra : ModMonsterTemplate
{
    public const string DecatronMoveId = "INFERNOID_DECATRON";
    public const string BeelzebubMoveId = "INFERNOID_BEELZEBUB";
    public const string LucifugusMoveId = "INFERNOID_LUCIFUGUS";
    public const string AstarothMoveId = "INFERNOID_ASTAROTH";
    public const string AsmodeusMoveId = "INFERNOID_ASMODEUS";
    public const string BelphegorMoveId = "INFERNOID_BELPHEGOR";
    public const string BaalMoveId = "INFERNOID_BAAL";
    public const string AdrammelechMoveId = "INFERNOID_ADRAMMELECH";
    public const string LilithMoveId = "INFERNOID_LILITH";
    public const string NaamahMoveId = "INFERNOID_NAAMAH";
    public const string StarTransformMoveId = "STAR_TRANSFORM";
    public const string EvilMoveId = "INFERNOID_EVIL";
    public const string FloodMoveId = "INFERNOID_FLOOD";
    public const string VirtualDreamMoveId = "VOID_IMAGINATION";
    public const string DisasterMoveId = "VOID_APOCALYPSE";
    public const string StarCreationMoveId = "STAR_CREATION";

    private bool _startCursesAdded;
    private InfernoidDecatronMoveState? _decatronMove;
    private MoveState? _starTransformMove;
    private int _phaseTwoIndex;

    /// <summary>1=狱火机·提耶拉；2=创星神·提耶拉。</summary>
    public int Phase { get; private set; } = 1;

    public int PhaseTwoIndex => _phaseTwoIndex;

    public override int MinInitialHp => AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 660, 600);
    public override int MaxInitialHp => MinInitialHp;

    private static int PhaseTwoBaseHp =>
        AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 550, 500);

    private static int StartCurseCount =>
        AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 2, 1);

    private int EvilDamage => AscensionHelper.GetValueIfAscension(AscensionLevel.DeadlyEnemies, 13, 11);
    private int FloodDamage => AscensionHelper.GetValueIfAscension(AscensionLevel.DeadlyEnemies, 30, 26);
    private int RitualAmount => AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 3, 2);

    // 高进阶（DeadlyEnemies）：8 级 24+24→26+26；9 级 29→32；10 级 30→33（设计 §6.5）。
    public static int LevelDamage(int level) => level switch
    {
        3 => 16,
        4 => 18,
        5 => 22,
        6 => 24,
        7 => 26,
        8 => AscensionHelper.GetValueIfAscension(AscensionLevel.DeadlyEnemies, 26, 24),
        9 => AscensionHelper.GetValueIfAscension(AscensionLevel.DeadlyEnemies, 32, 29),
        10 => AscensionHelper.GetValueIfAscension(AscensionLevel.DeadlyEnemies, 33, 30),
        _ => 0,
    };

    public override LocString Title => new("monsters", Phase == 2
        ? "LIGHTSWORN_MONSTER_INFERNOID_TIERRA.phase2Name"
        : "LIGHTSWORN_MONSTER_INFERNOID_TIERRA.name");

    public override MonsterAssetProfile AssetProfile => new(
        VisualsScenePath: "res://lightsworn/images/monsters/infernoid_tierra.png");

    public InfernoidMaterialPower? MaterialPower =>
        Creature.Powers.OfType<InfernoidMaterialPower>().FirstOrDefault();

    public StarCreationPower? StarPower =>
        Creature.Powers.OfType<StarCreationPower>().FirstOrDefault();

    public override async Task AfterAddedToRoom()
    {
        PlayerChoiceContext ctx = new ThrowingPlayerChoiceContext();
        if (!Creature.Powers.Any(p => p is InfernoidTierraPhaseGatePower))
            await PowerCmd.Apply<InfernoidTierraPhaseGatePower>(ctx, Creature, 1, Creature, null);
        if (!Creature.Powers.Any(p => p is InfernoidMaterialPower))
        {
            InfernoidMaterialPower? material =
                await PowerCmd.Apply<InfernoidMaterialPower>(ctx, Creature, 1, Creature, null);
            material?.SetAmount(1);
        }
        Log.Info($"[LsTierra] AfterAddedToRoom powers={string.Join(",", Creature.Powers.Select(p => p.Id.Entry))}");
    }

    // 开局把 1 张（高进阶 2 张）随机狱火机诅咒洗入每名玩家的抽牌堆。
    // 必须在 BeforeCombatStart（IsInProgress=true 之后、开局抽牌之前）。
    public override async Task BeforeCombatStart()
    {
        if (_startCursesAdded) return;
        _startCursesAdded = true;
        if (Creature.CombatState == null) return;
        PlayerChoiceContext ctx = new ThrowingPlayerChoiceContext();
        foreach (Player player in Creature.CombatState.Players)
        {
            if (!player.Creature.IsAlive) continue;
            for (int i = 0; i < StartCurseCount; i++)
                await InfernoidTierraCards.AddRandomCurseToDraw(ctx, player, Rng);
        }
    }

    // ================= 状态机 =================
    protected override MonsterMoveStateMachine GenerateMoveStateMachine()
    {
        PhaseOneSelectState phaseOneSelect = new(this);
        PhaseTwoSelectState phaseTwoSelect = new(this);

        InfernoidDecatronIntent decatronIntent = new(() => _decatronMove?.CopyLevel ?? 2);
        _decatronMove = new InfernoidDecatronMoveState(this, DecatronMoveId, PerformDecatronMove,
            decatronIntent, new InfernoidTributeIntent());

        MoveState beelzebub = new(BeelzebubMoveId, targets => PerformLevel(2, targets),
            new DefendIntent(), new InfernoidTributeIntent());
        MoveState lucifugus = new(LucifugusMoveId, targets => PerformLevel(3, targets),
            new SingleAttackIntent(LevelDamage(3)), new DebuffIntent(strong: true), new InfernoidTributeIntent());
        MoveState astaroth = new(AstarothMoveId, targets => PerformLevel(4, targets),
            new SingleAttackIntent(LevelDamage(4)), new DebuffIntent(strong: true), new InfernoidTributeIntent());
        MoveState asmodeus = new(AsmodeusMoveId, targets => PerformLevel(5, targets),
            new SingleAttackIntent(LevelDamage(5)), new DebuffIntent(strong: true), new InfernoidTributeIntent());
        MoveState belphegor = new(BelphegorMoveId, targets => PerformLevel(6, targets),
            new SingleAttackIntent(LevelDamage(6)), new InfernoidCardOpsIntent("NULLIFY_FUSION"), new InfernoidTributeIntent());
        MoveState baal = new(BaalMoveId, targets => PerformLevel(7, targets),
            new SingleAttackIntent(LevelDamage(7)), new InfernoidTributeIntent());
        MoveState adrammelech = new(AdrammelechMoveId, targets => PerformLevel(8, targets),
            new InfernoidMultiAttackIntent(() => LevelDamage(8), 2), new InfernoidTributeIntent());
        MoveState lilith = new(LilithMoveId, targets => PerformLevel(9, targets),
            new SingleAttackIntent(() => LevelDamage(9)), new InfernoidCardOpsIntent("EXHAUST_SKILLS"), new InfernoidTributeIntent());
        MoveState naamah = new(NaamahMoveId, targets => PerformLevel(10, targets, isCopy: false),
            new SingleAttackIntent(() => LevelDamage(10)), new InfernoidCardOpsIntent("EXHAUST_ATTACKS"), new InfernoidTributeIntent());

        _starTransformMove = new MoveState(StarTransformMoveId, StarTransformMove,
            new HealIntent(), new BuffIntent());
        MoveState evil = new(EvilMoveId, EvilMove,
            new InfernoidMultiAttackIntent(() => EvilDamage, 2), new InfernoidCardOpsIntent("EXHAUST_GENERATE"), new StatusIntent(1));
        MoveState flood = new(FloodMoveId, FloodMove,
            new SingleAttackIntent(() => FloodDamage), new InfernoidCardOpsIntent("NULLIFY_FUSION"),
            new InfernoidCardOpsIntent("TRIBUTE_ON_EXHAUST"));
        MoveState virtualDream = new(VirtualDreamMoveId, VirtualDreamMove,
            new DefendIntent(), new InfernoidCardOpsIntent("RETURN_FUEL"), new InfernoidCardOpsIntent("HALF_DAMAGE"));
        MoveState disaster = new(DisasterMoveId, DisasterMove,
            new InfernoidCardOpsIntent("DISCARD_ONE"), new InfernoidCardOpsIntent("GENERATE_FUEL"));
        MoveState starCreation = new(StarCreationMoveId, StarCreationMove,
            new InfernoidCardOpsIntent("APOCALYPSE"));

        foreach (MoveState state in new[] { _decatronMove, beelzebub, lucifugus, astaroth, asmodeus,
                     belphegor, baal, adrammelech, lilith, naamah })
            state.FollowUpState = phaseOneSelect;

        _starTransformMove.FollowUpState = phaseTwoSelect;
        evil.FollowUpState = phaseTwoSelect;
        flood.FollowUpState = phaseTwoSelect;
        virtualDream.FollowUpState = phaseTwoSelect;
        disaster.FollowUpState = phaseTwoSelect;
        starCreation.FollowUpState = phaseTwoSelect;

        return new MonsterMoveStateMachine(
            [_decatronMove, beelzebub, lucifugus, astaroth, asmodeus, belphegor, baal,
             adrammelech, lilith, naamah, _starTransformMove, evil, flood, virtualDream, disaster,
             starCreation, phaseOneSelect, phaseTwoSelect],
            phaseOneSelect);
    }

    // ================= 一阶段动作 =================
    private Task PerformDecatronMove(IReadOnlyList<Creature> targets)
        => PerformLevel(_decatronMove?.CopyLevel ?? 2, targets, isCopy: true);

    private async Task PerformLevel(int level, IReadOnlyList<Creature> targets, bool isCopy = false)
    {
        PlayerChoiceContext ctx = new BlockingPlayerChoiceContext();
        switch (level)
        {
            case 1:
                // 不会发生：十进管在状态机里直接复制 2-10。
                break;
            case 2:
                await CreatureCmd.GainBlock(Creature, 20m, ValueProp.Move, null);
                break;
            case 3:
                await AttackAll(LevelDamage(3), "vfx/vfx_attack_slash");
                break;
            case 4:
                await AttackAll(LevelDamage(4), "vfx/vfx_attack_slash");
                break;
            case 5:
            {
                AttackCommand attack = await AttackAll(LevelDamage(5), "vfx/vfx_attack_blunt");
                foreach (Creature receiver in UnblockedTargets(attack))
                    await PowerCmd.Apply<TierraDiscardOnePower>(ctx, receiver, 1m, Creature, null);
                break;
            }
            case 6:
                await AttackAll(LevelDamage(6), "vfx/vfx_attack_blunt");
                await ApplyToAllPlayers<TierraFusionNullifyPower>(ctx, 1);
                break;
            case 7:
                await AttackAll(LevelDamage(7), "vfx/vfx_heavy_blunt");
                break;
            case 8:
            {
                AttackCommand attack = await AttackAll(LevelDamage(8), "vfx/vfx_heavy_blunt");
                List<Creature> unblocked = UnblockedTargets(attack);
                if (unblocked.Count > 0)
                {
                    await CreatureCmd.TriggerAnim(Creature, "Attack", 0.3f);
                    foreach (Creature receiver in unblocked)
                    {
                        if (!receiver.IsAlive) continue;
                        await CreatureCmd.Damage(ctx, receiver, LevelDamage(8), ValueProp.Move, Creature);
                    }
                }
                break;
            }
            case 9:
            {
                await AttackAll(LevelDamage(9), "vfx/vfx_heavy_blunt");
                if (Creature.CombatState != null)
                {
                    foreach (Player player in Creature.CombatState.Players)
                    {
                        List<CardModel> skills = PileType.Discard.GetPile(player).Cards
                            .Where(c => c.Type == CardType.Skill).ToList();
                        foreach (CardModel card in skills)
                            await LsCompat.ExhaustCompat(ctx, card);
                    }
                }
                await ApplyToAllPlayers<TierraAttackNullifyPower>(ctx, 1);
                break;
            }
            case 10:
            {
                await AttackAll(LevelDamage(10), "vfx/vfx_heavy_blunt");
                if (Creature.CombatState != null)
                {
                    foreach (Player player in Creature.CombatState.Players)
                    {
                        List<CardModel> attacks = PileType.Discard.GetPile(player).Cards
                            .Where(c => c.Type == CardType.Attack).ToList();
                        foreach (CardModel card in attacks)
                            await LsCompat.ExhaustCompat(ctx, card);
                    }
                }
                await ApplyToAllPlayers<TierraSkillNullifyPower>(ctx, 1);
                break;
            }
        }

        await ResolveTributeAndCurse(ctx, level);

        // 10 级特效：拿玛动作（含 Tribute / 塞诅咒）全部结算完之后才融合完成。
        // 十进管复制 10 级动作只复制“动作”，不触发阈值特效。
        if (level == 10 && !isCopy && MaterialPower is InfernoidMaterialPower material)
            await material.CompleteFusionAsync(ctx);
    }

    private async Task<AttackCommand> AttackAll(int damage, string hitFx)
        => await DamageCmd.Attack(damage).FromMonster(this)
            .WithAttackerAnim("Attack", 0.4f)
            .WithHitFx(hitFx)
            .Execute(null);

    private static List<Creature> UnblockedTargets(AttackCommand attack)
        => attack.Results.SelectMany(r => r)
            .Where(r => r.UnblockedDamage > 0 && r.Receiver.IsAlive)
            .Select(r => r.Receiver)
            .Distinct()
            .ToList();

    private async Task ApplyToAllPlayers<T>(PlayerChoiceContext ctx, int amount) where T : PowerModel
    {
        if (Creature.CombatState == null) return;
        foreach (Player player in Creature.CombatState.Players)
        {
            if (!player.Creature.IsAlive) continue;
            await PowerCmd.Apply<T>(ctx, player.Creature, amount, Creature, null);
        }
    }

    // 每招：玩家从弃牌堆选 1 张非狱火机消耗；然后塞 1 张随机狱火机诅咒进抽牌堆。
    // Tribute 成功才结算该等级的墓地效果；失败也照常塞诅咒。
    private async Task ResolveTributeAndCurse(PlayerChoiceContext ctx, int level)
    {
        if (Creature.CombatState == null) return;
        foreach (Player player in Creature.CombatState.Players)
        {
            if (!player.Creature.IsAlive) continue;
            List<CardModel> candidates = PileType.Discard.GetPile(player).Cards
                .Where(c => c is not InfernoidCurseCard).ToList();
            bool tribute = false;
            if (candidates.Count > 0)
            {
                List<CardModel> picked = await LsUtil.PickFromList(ctx, player, candidates,
                    "LIGHTSWORN_TIERRA_TRIBUTE", 1);
                if (picked.Count > 0)
                {
                    await LsCompat.ExhaustCompat(ctx, picked[0]);
                    tribute = true;
                }
            }
            if (tribute)
                await ApplyTributeEffect(ctx, player, level);
        }

        // 无论 Tribute 是否成功，每名玩家抽牌堆塞 1 张随机诅咒。
        foreach (Player player in Creature.CombatState.Players)
        {
            if (!player.Creature.IsAlive) continue;
            await InfernoidTierraCards.AddRandomCurseToDraw(ctx, player, Rng);
        }
    }

    private async Task ApplyTributeEffect(PlayerChoiceContext ctx, Player player, int level)
    {
        switch (level)
        {
            case 2:
                await PowerCmd.Apply<TierraShuffleOnePower>(ctx, player.Creature, 1m, Creature, null);
                break;
            case 3:
                await PowerCmd.Apply<WeakPower>(ctx, player.Creature, 2m, Creature, null);
                await PowerCmd.Apply<VulnerablePower>(ctx, player.Creature, 2m, Creature, null);
                break;
            case 4:
                await PowerCmd.Apply<StrengthPower>(ctx, player.Creature, -2m, Creature, null);
                await PowerCmd.Apply<DexterityPower>(ctx, player.Creature, -2m, Creature, null);
                break;
            case 7:
            {
                List<CardModel> draw = PileType.Draw.GetPile(player).Cards.ToList();
                CardModel? pick = player.RunState.Rng.CombatCardSelection.NextItem(draw);
                if (pick != null)
                    await LsCompat.ExhaustCompat(ctx, pick);
                break;
            }
        }
    }

    // ================= 转阶段 =================
    /// <summary>一阶段生命打空时由阶段门调用：下一次出招固定为「创星」。</summary>
    public void OnPhaseOneDefeated()
    {
        if (Phase != 1 || _starTransformMove == null) return;
        Log.Info($"[LsTierra] phase1 defeated: hp={Creature.CurrentHp}/{Creature.MaxHp} phase={Phase}");
        SetMoveImmediate(_starTransformMove, forceTransition: true);
    }

    private async Task StarTransformMove(IReadOnlyList<Creature> targets)
    {
        PlayerChoiceContext ctx = new BlockingPlayerChoiceContext();
        Log.Info($"[LsTierra] STAR_TRANSFORM start: hp={Creature.CurrentHp}/{Creature.MaxHp} dead={Creature.IsDead} phase={Phase}");
        await CreatureCmd.TriggerAnim(Creature, "Cast", 0.6f);

        // 先结算玩家侧与该回合无关的清理（此时阶段门还在，CombatManager 不会把战斗判负/结束）。
        if (Creature.CombatState != null)
        {
            foreach (Player player in Creature.CombatState.Players)
            {
                await PowerCmd.Remove<WeakPower>(player.Creature);
                await PowerCmd.Remove<VulnerablePower>(player.Creature);

                // 手牌/弃牌堆的诅咒洗回抽牌堆；消耗堆的诅咒放进弃牌堆（二阶段引爆来源）。
                List<CardModel> toDraw = PileType.Hand.GetPile(player).Cards
                    .Concat(PileType.Discard.GetPile(player).Cards)
                    .Where(c => c is InfernoidCurseCard).ToList();
                foreach (CardModel card in toDraw)
                    await CardPileCmd.Add(card, PileType.Draw, CardPilePosition.Random);

                List<CardModel> toDiscard = PileType.Exhaust.GetPile(player).Cards
                    .Where(c => c is InfernoidCurseCard).ToList();
                foreach (CardModel card in toDiscard)
                    await CardPileCmd.Add(card, PileType.Discard);
            }
        }

        // 关键顺序：先设置最大生命并治疗（阶段门仍在 → IsEnding=false，Heal 不会被跳过），
        // 治疗成功后再移除阶段门、切 Phase=2。反序会让 Heal 因“唯一敌人已死、战斗判定结束”直接 return，
        // Boss 永久保持 0 血、战斗被判定胜利（实测）。
        decimal scaledHp = MegaCrit.Sts2.Core.Entities.Creatures.Creature.ScaleHpForMultiplayer(
            PhaseTwoBaseHp, CombatState.Encounter, CombatState.Players.Count, CombatState.RunState.CurrentActIndex);
        await CreatureCmd.SetMaxHp(Creature, scaledHp);
        await CreatureCmd.Heal(Creature, scaledHp);
        Log.Info($"[LsTierra] STAR_TRANSFORM healed: hp={Creature.CurrentHp}/{Creature.MaxHp} dead={Creature.IsDead} phase={Phase}");

        Phase = 2;
        _phaseTwoIndex = 0;
        await PowerCmd.Remove<InfernoidTierraPhaseGatePower>(Creature);
        await PowerCmd.Remove<InfernoidMaterialPower>(Creature);
        await LsCompat.LoseBlockCompat(ctx, Creature, Creature.Block, Creature);

        StarCreationPower? star = await PowerCmd.Apply<StarCreationPower>(ctx, Creature, 1m, Creature, null);
        star?.SetAmount(1);          // 显示 0
        star?.SkipNextTurnEnd();     // 创星动作所在的 Boss 回合结束不 +2

        await PowerCmd.Apply<RitualPower>(ctx, Creature, RitualAmount, Creature, null);
        SwitchToPhaseTwoVisuals();
    }

    // ================= 二阶段四招 =================
    private async Task EvilMove(IReadOnlyList<Creature> targets)
    {
        await DamageCmd.Attack(EvilDamage).WithHitCount(2).FromMonster(this)
            .WithAttackerAnim("Attack", 0.4f)
            .WithHitFx("vfx/vfx_attack_slash")
            .Execute(null);

        PlayerChoiceContext ctx = new BlockingPlayerChoiceContext();
        if (Creature.CombatState != null)
        {
            List<CardModel> curses = Creature.CombatState.Players
                .SelectMany(p => PileType.Discard.GetPile(p).Cards)
                .Where(c => c is InfernoidCurseCard).ToList();
            CardModel? pick = Rng.NextItem(curses);
            if (pick is InfernoidCurseCard curse && curse.Owner != null)
            {
                int level = curse.Level;
                Player owner = curse.Owner;
                await LsCompat.ExhaustCompat(ctx, curse);
                await InfernoidTierraCards.AddRandomCursesToDiscard(ctx, owner, Rng, level);
            }

            foreach (Player player in Creature.CombatState.Players)
            {
                if (!player.Creature.IsAlive) continue;
                await InfernoidTierraCards.AddRandomCurseToDraw(ctx, player, Rng);
            }
        }
        AdvancePhaseTwo();
    }

    private async Task FloodMove(IReadOnlyList<Creature> targets)
    {
        await DamageCmd.Attack(FloodDamage).FromMonster(this)
            .WithAttackerAnim("Attack", 0.5f)
            .WithHitFx("vfx/vfx_heavy_blunt")
            .Execute(null);

        PlayerChoiceContext ctx = new BlockingPlayerChoiceContext();
        await ApplyToAllPlayers<TierraFusionNullifyPower>(ctx, 1);
        await ApplyToAllPlayers<TierraFloodTributePower>(ctx, 1);
        AdvancePhaseTwo();
    }

    private async Task VirtualDreamMove(IReadOnlyList<Creature> targets)
    {
        await CreatureCmd.GainBlock(Creature, 20m, ValueProp.Move, null);
        PlayerChoiceContext ctx = new BlockingPlayerChoiceContext();
        if (Creature.CombatState != null)
        {
            foreach (Player player in Creature.CombatState.Players)
            {
                if (!player.Creature.IsAlive) continue;

                List<CardModel> curses = PileType.Exhaust.GetPile(player).Cards
                    .Where(c => c is InfernoidCurseCard).Take(2).ToList();
                foreach (CardModel card in curses)
                    await CardPileCmd.Add(card, PileType.Discard);

                await PowerCmd.Apply<TierraHalfDamagePower>(ctx, player.Creature, 2m, Creature, null);

                if (HasFusionCard(player))
                    await InfernoidTierraCards.AddRandomCursesToDiscard(ctx, player, Rng, 6);
            }
        }
        AdvancePhaseTwo();
    }

    private async Task DisasterMove(IReadOnlyList<Creature> targets)
    {
        PlayerChoiceContext ctx = new BlockingPlayerChoiceContext();
        if (Creature.CombatState != null)
        {
            foreach (Player player in Creature.CombatState.Players)
            {
                if (!player.Creature.IsAlive) continue;
                await PowerCmd.Apply<TierraDiscardOnePower>(ctx, player.Creature, 1m, Creature, null);
                await InfernoidTierraCards.AddRandomCursesToDiscard(ctx, player, Rng, 2);
                if (HasFusionCard(player))
                    await InfernoidTierraCards.AddRandomCursesToDiscard(ctx, player, Rng, 6);
            }
        }
        AdvancePhaseTwo();
    }

    private async Task StarCreationMove(IReadOnlyList<Creature> targets)
    {
        PlayerChoiceContext ctx = new BlockingPlayerChoiceContext();
        await CreatureCmd.TriggerAnim(Creature, "Cast", 0.8f);

        if (Creature.CombatState != null)
        {
            foreach (Player player in Creature.CombatState.Players)
            {
                // 手牌洗回抽牌堆 → 弃牌堆整体洗入抽牌堆 → 消耗堆里的狱火机诅咒洗回抽牌堆。
                List<CardModel> hand = PileType.Hand.GetPile(player).Cards.ToList();
                foreach (CardModel card in hand)
                    await CardPileCmd.Add(card, PileType.Draw, CardPilePosition.Random);
                await CardPileCmd.Shuffle(ctx, player);
                List<CardModel> exhaustedCurses = PileType.Exhaust.GetPile(player).Cards
                    .Where(c => c is InfernoidCurseCard).ToList();
                foreach (CardModel card in exhaustedCurses)
                    await CardPileCmd.Add(card, PileType.Draw, CardPilePosition.Random);

                await PowerCmd.Apply<TierraApocalypsePower>(ctx, player.Creature, 1m, Creature, null);
            }
        }

        await CreatureCmd.Heal(Creature, 100m);
        await PowerCmd.Apply<RitualPower>(ctx, Creature, 2m, Creature, null);
        StarPower?.ResetGauge();
        _phaseTwoIndex = 0;
    }

    private void AdvancePhaseTwo()
    {
        _phaseTwoIndex = (_phaseTwoIndex + 1) % 4;
    }

    private static bool HasFusionCard(Player player)
    {
        return PileType.Hand.GetPile(player).Cards
            .Concat(PileType.Discard.GetPile(player).Cards)
            .Concat(PileType.Exhaust.GetPile(player).Cards)
            .Any(c => c is TearFusionToken or ShaddollToken);
    }

    // ================= 静态立绘 + 二阶段换图 =================
    protected override NCreatureVisuals? TryCreateCreatureVisuals()
    {
        var root = new NCreatureVisuals { Name = "InfernoidTierraVisuals" };

        void AddOwned(Node node, bool unique = true)
        {
            root.AddChild(node);
            node.Owner = root;
            if (unique) node.UniqueNameInOwner = true;
        }

        // 一阶段素材 bbox=(100,137)-(1340,1413)：内容中心 x=720（相对画布中心 -48）、
        // 内容底边相对纹理中心 +645。0.48 缩放 → Position=(-23, -309.6) 时脚底贴场景原点；
        // 高度约 612，给头顶意图留出约 20px 空间（0.5 缩放时 Boss 太高，意图会被顶栏裁掉）。
        var sprite = new Sprite2D
        {
            Name = "Visuals",
            Texture = ResourceLoader.Load<Texture2D>("res://lightsworn/images/monsters/infernoid_tierra.png"),
            Position = new Vector2(-23f, -309.6f),
            Scale = new Vector2(0.48f, 0.48f),
        };
        AddOwned(sprite);

        var bounds = new Control
        {
            Name = "Bounds",
            MouseFilter = Control.MouseFilterEnum.Ignore,
            Position = new Vector2(-350f, -670f),
            Size = new Vector2(700f, 670f),
        };
        AddOwned(bounds);

        var centerPos = new Marker2D { Name = "CenterPos", Position = new Vector2(0f, -310f) };
        AddOwned(centerPos);

        var intentPos = new Marker2D { Name = "IntentPos", Position = new Vector2(0f, -620f) };
        AddOwned(intentPos);

        var talkPos = new Marker2D { Name = "TalkPos", Position = new Vector2(0f, -470f) };
        AddOwned(talkPos);

        var anim = new AnimationPlayer { Name = "AnimationPlayer" };
        AddOwned(anim, unique: false);

        Vector2 basePos = sprite.Position;
        var lib = new AnimationLibrary();

        var hurt = new Animation { Length = 0.24f };
        int ht = hurt.AddTrack(Animation.TrackType.Value);
        hurt.TrackSetPath(ht, "Visuals:position");
        hurt.TrackInsertKey(ht, 0.00, basePos);
        hurt.TrackInsertKey(ht, 0.04, basePos + new Vector2(10, 0));
        hurt.TrackInsertKey(ht, 0.08, basePos - new Vector2(10, 0));
        hurt.TrackInsertKey(ht, 0.12, basePos + new Vector2(7, 0));
        hurt.TrackInsertKey(ht, 0.16, basePos - new Vector2(7, 0));
        hurt.TrackInsertKey(ht, 0.20, basePos + new Vector2(3, 0));
        hurt.TrackInsertKey(ht, 0.24, basePos);
        lib.AddAnimation("hurt", hurt);

        var attack = new Animation { Length = 0.36f };
        int at = attack.AddTrack(Animation.TrackType.Value);
        attack.TrackSetPath(at, "Visuals:position");
        attack.TrackInsertKey(at, 0.00, basePos);
        attack.TrackInsertKey(at, 0.12, basePos + new Vector2(-48, 0));
        attack.TrackInsertKey(at, 0.26, basePos + new Vector2(-16, 0));
        attack.TrackInsertKey(at, 0.36, basePos);
        lib.AddAnimation("attack", attack);

        var cast = new Animation { Length = 0.42f };
        int ct = cast.AddTrack(Animation.TrackType.Value);
        cast.TrackSetPath(ct, "Visuals:position");
        cast.TrackInsertKey(ct, 0.00, basePos);
        cast.TrackInsertKey(ct, 0.16, basePos + new Vector2(0, -18));
        cast.TrackInsertKey(ct, 0.42, basePos);
        lib.AddAnimation("cast", cast);

        var die = new Animation { Length = 1.20f };
        int dt = die.AddTrack(Animation.TrackType.Value);
        die.TrackSetPath(dt, "Visuals:modulate:a");
        die.TrackInsertKey(dt, 0.00, 1.0f);
        die.TrackInsertKey(dt, 1.00, 0.0f);
        lib.AddAnimation("die", die);

        anim.AddAnimationLibrary("", lib);
        return root;
    }

    // 二阶段换成立绘并同步位移：两图同为 1536×1536，但内容 bbox 不同。
    // 创星神 bbox=(165,67)-(1307,1287) → 0.48 缩放 Position=(-15.36, -249.12)。
    // 位置轨道的所有关键帧同步平移 delta，攻击/受击动画收尾不会把立绘拉回一阶段坐标。
    private void SwitchToPhaseTwoVisuals()
    {
        NCreature? node = Creature.GetCreatureNode();
        Sprite2D? sprite = node?.GetSpecialNode<Sprite2D>("Visuals");
        if (sprite == null) return;
        Texture2D? texture = ResourceLoader.Load<Texture2D>(
            "res://lightsworn/images/monsters/infernoid_tierra_source.png");
        if (texture == null) return;

        Vector2 oldPos = sprite.Position;
        Vector2 newPos = new(-15.36f, -249.12f);
        Vector2 delta = newPos - oldPos;
        sprite.Texture = texture;
        sprite.Position = newPos;

        // 一阶段死亡时 RitsuLib 会把 "Dead" 转发到我们的 "die" 动画，把 modulate.a 淡到 0。
        // StartReviveAnim 对非 Spine/非玩家单位不做恢复，这里手动停掉动画并恢复不透明度。
        AnimationPlayer? anim = node?.GetSpecialNode<AnimationPlayer>("AnimationPlayer");
        anim?.Stop();
        sprite.Modulate = new Color(1f, 1f, 1f, 1f);
        sprite.Visible = true;

        if (anim == null) return;
        foreach (string name in anim.GetAnimationList())
        {
            Animation? animation = anim.GetAnimation(name);
            if (animation == null) continue;
            for (int track = 0; track < animation.GetTrackCount(); track++)
            {
                if (animation.TrackGetPath(track).ToString() != "Visuals:position") continue;
                int keys = animation.TrackGetKeyCount(track);
                for (int key = 0; key < keys; key++)
                {
                    Vector2 value = (Vector2)animation.TrackGetKeyValue(track, key);
                    animation.TrackSetKeyValue(track, key, value + delta);
                }
            }
        }
    }

    // ================= 静态查询（诅咒引爆管线用） =================
    public static InfernoidMaterialPower? FindMaterialPower(Player player)
        => player.Creature.CombatState?.Enemies
            .SelectMany(e => e.Powers)
            .OfType<InfernoidMaterialPower>()
            .FirstOrDefault();

    public static void NotifyCurseDetonated(Player player, int level, string materialKey)
    {
        StarCreationPower? star = player.Creature.CombatState?.Enemies
            .SelectMany(e => e.Powers)
            .OfType<StarCreationPower>()
            .FirstOrDefault();
        star?.OnCurseDetonated(materialKey);
    }
}

// ================= 状态机分支 =================
// 一阶段：回合开始 RollMove 时按当时素材数锁定本回合动作（玩家回合中变化不重新掷）。
public sealed class PhaseOneSelectState : MonsterState
{
    private readonly InfernoidTierra _monster;

    public PhaseOneSelectState(InfernoidTierra monster) => _monster = monster;

    public override string Id => "INFERNOID_PHASE_ONE_SELECT";
    public override bool ShouldAppearInLogs => false;
    public override bool CanTransitionAway => true;

    public override string GetNextState(Creature owner, Rng rng)
    {
        InfernoidMaterialPower? material = _monster.MaterialPower;
        if (material?.PendingNaamah == true) return InfernoidTierra.NaamahMoveId;
        int level = material?.Material ?? 1;
        return level switch
        {
            2 => InfernoidTierra.BeelzebubMoveId,
            3 => InfernoidTierra.LucifugusMoveId,
            4 => InfernoidTierra.AstarothMoveId,
            5 => InfernoidTierra.AsmodeusMoveId,
            6 => InfernoidTierra.BelphegorMoveId,
            7 => InfernoidTierra.BaalMoveId,
            8 => InfernoidTierra.AdrammelechMoveId,
            9 => InfernoidTierra.LilithMoveId,
            10 => InfernoidTierra.NaamahMoveId,
            _ => InfernoidTierra.DecatronMoveId,
        };
    }

    public override void RegisterStates(Dictionary<string, MonsterState> monsterStates)
        => monsterStates.Add(Id, this);
}

// 二阶段：创星到 10 → 下一招「创星·灭世」；否则按 邪恶→洪水→虚梦→灾天 循环。
public sealed class PhaseTwoSelectState : MonsterState
{
    private readonly InfernoidTierra _monster;

    public PhaseTwoSelectState(InfernoidTierra monster) => _monster = monster;

    public override string Id => "INFERNOID_PHASE_TWO_SELECT";
    public override bool ShouldAppearInLogs => false;
    public override bool CanTransitionAway => true;

    public override string GetNextState(Creature owner, Rng rng)
    {
        if (_monster.StarPower?.Gauge >= 10) return InfernoidTierra.StarCreationMoveId;
        return _monster.PhaseTwoIndex switch
        {
            1 => InfernoidTierra.FloodMoveId,
            2 => InfernoidTierra.VirtualDreamMoveId,
            3 => InfernoidTierra.DisasterMoveId,
            _ => InfernoidTierra.EvilMoveId,
        };
    }

    public override void RegisterStates(Dictionary<string, MonsterState> monsterStates)
        => monsterStates.Add(Id, this);
}

// 十进管：进入状态时（玩家回合开始 RollMove）随机复制 2-10 中的一个动作；
// 意图读取 CopyLevel 动态显示复制了谁。
public sealed class InfernoidDecatronMoveState : MoveState
{
    private readonly InfernoidTierra _monster;

    public int CopyLevel { get; private set; } = 2;

    public InfernoidDecatronMoveState(InfernoidTierra monster, string id,
        Func<IReadOnlyList<Creature>, Task> onPerform, params AbstractIntent[] intents)
        : base(id, onPerform, intents)
    {
        _monster = monster;
    }

    public override void OnEnterState()
    {
        CopyLevel = _monster.Rng.NextInt(2, 11);
        base.OnEnterState();
    }
}

// ================= 自定义意图 =================
// 统一继承 StatusIntent：NIntent 只在 intent is AttackIntent / StatusIntent 时渲染文字标签，
// 纯 AbstractIntent 子类会得到空标签（实测整个意图行看起来像消失了）。
// 献祭：从弃牌堆消耗 1 张非狱火机，然后 Boss 塞 1 张随机诅咒进抽牌堆。
public sealed class InfernoidTributeIntent : StatusIntent
{
    public InfernoidTributeIntent() : base(1) { }

    public override IntentType IntentType => IntentType.CardDebuff;

    protected override string IntentPrefix => "CARD_DEBUFF";
    protected override string SpritePath => "atlases/intent_atlas.sprites/intent_card_debuff.tres";

    public override bool HasIntentTip => true;

    public override LocString GetIntentLabel(IEnumerable<Creature> targets, Creature owner)
        => new("monsters", "LIGHTSWORN_MONSTER_INFERNOID_TIERRA.intents.TRIBUTE_SHORT");

    protected override LocString GetIntentDescription(IEnumerable<Creature> targets, Creature owner)
        => new("monsters", "LIGHTSWORN_MONSTER_INFERNOID_TIERRA.intents.TRIBUTE_TIP");
}

// 十进管复制意图：显示复制了哪只狱火机（攻击/格挡图标随复制目标变化）。
public sealed class InfernoidDecatronIntent : StatusIntent
{
    private readonly Func<int> _level;

    public InfernoidDecatronIntent(Func<int> level) : base(1) => _level = level;

    private int Level => _level();

    public override IntentType IntentType => IntentType.StatusCard;

    protected override string IntentPrefix => "STATUS";

    // 静态使用状态牌图标：动作等级在 RollMove 时才确定，动态切换 attack/defend 图标会导致
    // AssetPaths 预载的是另一张纹理、渲染时取不到（实测整个意图行不显示）。复制了谁由文字标签说明。
    protected override string SpritePath => "atlases/intent_atlas.sprites/intent_status_card.tres";

    public override bool HasIntentTip => true;

    public override LocString GetIntentLabel(IEnumerable<Creature> targets, Creature owner)
    {
        LocString label = new("monsters", "LIGHTSWORN_MONSTER_INFERNOID_TIERRA.intents.DECATRON_SHORT");
        label.Add("Demon", DemonName(Level));
        return label;
    }

    protected override LocString GetIntentDescription(IEnumerable<Creature> targets, Creature owner)
    {
        LocString tip = new("monsters", "LIGHTSWORN_MONSTER_INFERNOID_TIERRA.intents.DECATRON_TIP");
        tip.Add("Demon", DemonName(Level));
        int damage = InfernoidTierra.LevelDamage(Level);
        tip.Add("Damage", Level == 8 ? $"{damage}×2" : damage.ToString());
        return tip;
    }

    private static string DemonName(int level) => level switch
    {
        2 => "别西卜", 3 => "路西弗格", 4 => "阿斯塔罗特", 5 => "阿斯蒙蒂斯",
        6 => "贝尔芬格", 7 => "巴力", 8 => "亚得米勒", 9 => "莉莉丝", 10 => "拿玛", _ => "？",
    };
}

// 多段攻击意图；damage 用委托现算，便于高进阶动态数值。
public sealed class InfernoidMultiAttackIntent : MultiAttackIntent
{
    public InfernoidMultiAttackIntent(Func<int> damage, int repeat) : base(0, repeat)
    {
        DamageCalc = () => damage();
    }
}

// 二阶段/特殊动作的卡牌操作意图（除外/生成/放回/无效）。
public sealed class InfernoidCardOpsIntent : StatusIntent
{
    private readonly string _key;

    public InfernoidCardOpsIntent(string key) : base(1) => _key = key;

    public override IntentType IntentType => IntentType.StatusCard;

    protected override string IntentPrefix => "STATUS";
    protected override string SpritePath => "atlases/intent_atlas.sprites/intent_status_card.tres";

    public override bool HasIntentTip => true;

    public override LocString GetIntentLabel(IEnumerable<Creature> targets, Creature owner)
        => new("monsters", $"LIGHTSWORN_MONSTER_INFERNOID_TIERRA.intents.{_key}_SHORT");

    protected override LocString GetIntentDescription(IEnumerable<Creature> targets, Creature owner)
        => new("monsters", $"LIGHTSWORN_MONSTER_INFERNOID_TIERRA.intents.{_key}_TIP");
}

// ================= 遭遇（三层 Glory Boss 池） =================
[RegisterActEncounter(typeof(Glory))]
public class InfernoidTierraBoss : ModEncounterTemplate
{
    public override RoomType RoomType => RoomType.Boss;

    public override IEnumerable<MonsterModel> AllPossibleMonsters => [ModelDb.Monster<InfernoidTierra>()];

    // PNG 地图图标：无扩展名 _icon 基路径（游戏自动拼 .png / _outline.png），
    // 不能走 RitsuLib AssetProfile.BossNodeSpinePath（开发手册坑 38）。
    public override string BossNodePath =>
        "res://lightsworn/images/map/lightsworn/infernoid_tierra_boss_icon";

    public override EncounterAssetProfile AssetProfile => new(
        RunHistoryIconPath: "res://lightsworn/images/ui/run_history/infernoid_tierra_boss.png",
        RunHistoryIconOutlinePath: "res://lightsworn/images/ui/run_history/infernoid_tierra_boss_outline.png");

    protected override IReadOnlyList<(MonsterModel, string?)> GenerateMonsters() =>
        [(ModelDb.Monster<InfernoidTierra>().ToMutable(), null)];
}
