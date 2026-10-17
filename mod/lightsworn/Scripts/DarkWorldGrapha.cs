using Godot;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Ascension;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Acts;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.MonsterMoves.Intents;
using MegaCrit.Sts2.Core.MonsterMoves.MonsterMoveStateMachine;
using MegaCrit.Sts2.Core.Nodes.Cards;
using MegaCrit.Sts2.Core.Nodes.Combat;
using MegaCrit.Sts2.Core.Nodes.Rooms;
using MegaCrit.Sts2.Core.Random;
using MegaCrit.Sts2.Core.Rooms;
using MegaCrit.Sts2.Core.ValueProps;

namespace Lightsworn;

// ================= 暗黑界的龙神王 格拉法（三层超规格 Boss） =================
// 设计基线：design\暗黑界龙神王boss设计.md（方案 B：雷→军势→登极→回归→取引→洗脑）。
// 基础 800 血（高进阶 880）；6 招固定循环；无阶段转换。
// 全部随机数使用 monster.Rng（联机确定性）；被动按玩家回合记「本回合是否已触发」。
[RegisterMonster]
public class DarkWorldGrapha : ModMonsterTemplate
{
    public const int ReturnHealPerCard = 30;

    public const string ThunderMoveId = "DARK_WORLD_THUNDER";
    public const string ForcesMoveId = "DARK_WORLD_FORCES";
    public const string AscensionMoveId = "DARK_WORLD_ASCENSION";
    public const string ReturnMoveId = "DARK_WORLD_RETURN";
    public const string DealingsMoveId = "DARK_WORLD_DEALINGS";
    public const string BrainwashMoveId = "DARK_WORLD_BRAINWASH";

    private const int ThunderHits = 3;
    private const int ThunderDebuff = 3;
    private const int ForcesCards = 3;
    private const int DealingsDebuff = 5;
    private const int BrainwashCards = 3;

    // 进阶伤害（DeadlyEnemies）：与原版 Boss 一致，只有攻击伤害随进阶提高；
    // 意图读取的是同一组属性，所以显示数字会同步变。
    private int ThunderDamage => AscensionHelper.GetValueIfAscension(AscensionLevel.DeadlyEnemies, 9, 8);
    private int ForcesDamage => AscensionHelper.GetValueIfAscension(AscensionLevel.DeadlyEnemies, 11, 10);
    private int AscensionDamage => AscensionHelper.GetValueIfAscension(AscensionLevel.DeadlyEnemies, 33, 30);

    public override int MinInitialHp => AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 880, 800);
    public override int MaxInitialHp => MinInitialHp;

    // 运行时构建静态立绘（同圣女角色方案，不能用引用游戏脚本的 tscn）。
    // 这里仍把 PNG 填进 AssetProfile：RitsuLib 的 MonsterVisualsPathPatch 会让 AssetPaths 预载这张图；
    // CreateVisuals 的实际路径由 TryCreateCreatureVisuals 接管。
    public override MonsterAssetProfile AssetProfile => new(
        VisualsScenePath: "res://lightsworn/images/monsters/dark_world_grapha.png");

    public override async Task AfterAddedToRoom()
    {
        if (Creature.Powers.Any(p => p is DarkWorldTemptationPower)) return;
        await PowerCmd.Apply<DarkWorldTemptationPower>(
            new ThrowingPlayerChoiceContext(), Creature, 1, Creature, null);
    }

    protected override MonsterMoveStateMachine GenerateMoveStateMachine()
    {
        MoveState thunder = new(ThunderMoveId, ThunderMove,
            new MultiAttackIntent(ThunderDamage, ThunderHits), new DebuffIntent(strong: true));
        MoveState forces = new(ForcesMoveId, ForcesMove,
            new SingleAttackIntent(ForcesDamage), new StatusIntent(ForcesCards));
        MoveState ascension = new(AscensionMoveId, AscensionMove,
            new SingleAttackIntent(AscensionDamage));
        MoveState returnMove = new(ReturnMoveId, ReturnMove,
            new DarkWorldReturnIntent(CountAbsorbableCards));
        MoveState dealings = new(DealingsMoveId, DealingsMove,
            new DebuffIntent(strong: true), new CardDebuffIntent());
        MoveState brainwash = new(BrainwashMoveId, BrainwashMove,
            new StatusIntent(BrainwashCards));

        thunder.FollowUpState = forces;
        forces.FollowUpState = ascension;
        ascension.FollowUpState = returnMove;
        returnMove.FollowUpState = dealings;
        dealings.FollowUpState = brainwash;
        brainwash.FollowUpState = thunder;

        return new MonsterMoveStateMachine(
            [thunder, forces, ascension, returnMove, dealings, brainwash], thunder);
    }

    // 暗黑界之雷：8×3 伤害；施加 3 易伤 + 3 虚弱。
    private async Task ThunderMove(IReadOnlyList<Creature> targets)
    {
        await DamageCmd.Attack(ThunderDamage).FromMonster(this)
            .WithHitCount(ThunderHits)
            .WithAttackerAnim("Attack", 0.4f)
            .WithHitFx("vfx/vfx_attack_slash")
            .Execute(null);

        PlayerChoiceContext ctx = new ThrowingPlayerChoiceContext();
        foreach (Creature target in targets)
        {
            if (!target.IsAlive) continue;
            await PowerCmd.Apply<VulnerablePower>(ctx, target, ThunderDebuff, Creature, null);
            await PowerCmd.Apply<WeakPower>(ctx, target, ThunderDebuff, Creature, null);
        }
    }

    // 暗黑界的军势：10 伤害；给每个玩家洗入 3 张随机暗黑界攻击卡。
    private async Task ForcesMove(IReadOnlyList<Creature> targets)
    {
        await DamageCmd.Attack(ForcesDamage).FromMonster(this)
            .WithAttackerAnim("Attack", 0.4f)
            .WithHitFx("vfx/vfx_attack_blunt")
            .Execute(null);

        PlayerChoiceContext ctx = new ThrowingPlayerChoiceContext();
        foreach (Player player in CombatState.Players)
        {
            if (!player.Creature.IsAlive) continue;
            for (int i = 0; i < ForcesCards; i++)
                await DarkWorldBossCards.AddRandomAttackToDraw(ctx, player, Rng);
        }
    }

    // 暗黑界的登极：30 伤害（吃易伤/力量）。
    private async Task AscensionMove(IReadOnlyList<Creature> targets)
    {
        await DamageCmd.Attack(AscensionDamage).FromMonster(this)
            .WithAttackerAnim("Attack", 0.5f)
            .WithHitFx("vfx/vfx_heavy_blunt")
            .Execute(null);
    }

    // 龙神回归：吸收玩家抽牌堆 + 弃牌堆中所有暗黑界攻击卡，每张回复 30 生命。
    // 被吸收的卡移出战斗（不进消耗堆）；手牌是玩家的安全区，不吸收。
    private async Task ReturnMove(IReadOnlyList<Creature> targets)
    {
        await CreatureCmd.TriggerAnim(Creature, "Cast", 0.5f);
        List<CardModel> absorbed = new();
        foreach (Player player in CombatState.Players)
        {
            absorbed.AddRange(PileType.Draw.GetPile(player).Cards.Where(IsDarkWorldAttack));
            absorbed.AddRange(PileType.Discard.GetPile(player).Cards.Where(IsDarkWorldAttack));
        }

        if (absorbed.Count > 0)
        {
            await CardPileCmd.RemoveFromCombat(absorbed);
            await CreatureCmd.Heal(Creature, absorbed.Count * ReturnHealPerCard);
        }
    }

    // 暗黑界的取引：施加 5 虚弱 + 5 易伤；玩家抽 2，然后随机弃置 2 张手牌。
    // 强制弃置走 CardCmd.Discard → 正常触发「暗黑界的诱惑」与四神将的弃置效果。
    private async Task DealingsMove(IReadOnlyList<Creature> targets)
    {
        await CreatureCmd.TriggerAnim(Creature, "Cast", 0.4f);
        PlayerChoiceContext ctx = new ThrowingPlayerChoiceContext();
        foreach (Player player in CombatState.Players)
        {
            if (!player.Creature.IsAlive) continue;
            await PowerCmd.Apply<WeakPower>(ctx, player.Creature, DealingsDebuff, Creature, null);
            await PowerCmd.Apply<VulnerablePower>(ctx, player.Creature, DealingsDebuff, Creature, null);
            await CardPileCmd.Draw(ctx, 2m, player);

            List<CardModel> hand = PileType.Hand.GetPile(player).Cards.ToList();
            List<CardModel> discarded = new();
            for (int i = 0; i < 2 && hand.Count > 0; i++)
            {
                CardModel? pick = Rng.NextItem(hand);
                if (pick == null) break;
                hand.Remove(pick);
                discarded.Add(pick);
            }
            if (discarded.Count > 0)
                await CardCmd.Discard(ctx, discarded);
        }
    }

    // 暗黑界的洗脑：给每个玩家洗入 3 张「暗黑界的洗脑」状态。
    private async Task BrainwashMove(IReadOnlyList<Creature> targets)
    {
        await CreatureCmd.TriggerAnim(Creature, "Cast", 0.4f);
        PlayerChoiceContext ctx = new ThrowingPlayerChoiceContext();
        foreach (Player player in CombatState.Players)
        {
            if (!player.Creature.IsAlive) continue;
            for (int i = 0; i < BrainwashCards; i++)
                await DarkWorldBossCards.AddBrainwashingToDraw(ctx, player);
        }
    }

    private static bool IsDarkWorldAttack(CardModel card) => card is DarkWorldAttackCard;

    private int CountAbsorbableCards()
    {
        if (CombatState == null) return 0;
        int count = 0;
        foreach (Player player in CombatState.Players)
        {
            count += PileType.Draw.GetPile(player).Cards.Count(IsDarkWorldAttack);
            count += PileType.Discard.GetPile(player).Cards.Count(IsDarkWorldAttack);
        }
        return count;
    }

    // ---------- 静态立绘 + 四条简单动画（hurt/attack/cast/die） ----------
    protected override NCreatureVisuals? TryCreateCreatureVisuals()
    {
        var root = new NCreatureVisuals { Name = "DarkWorldGraphaVisuals" };

        void AddOwned(Node node, bool unique = true)
        {
            root.AddChild(node);
            node.Owner = root;
            if (unique) node.UniqueNameInOwner = true;
        }

        // 1600×1200 横向构图；内容底边 y≈1122。0.5 缩放 → 宽约 728、高约 522，脚底贴场景原点。
        var sprite = new Sprite2D
        {
            Name = "Visuals",
            Texture = ResourceLoader.Load<Texture2D>("res://lightsworn/images/monsters/dark_world_grapha.png"),
            Position = new Vector2(0f, -261f),
            Scale = new Vector2(0.5f, 0.5f),
        };
        AddOwned(sprite);

        var bounds = new Control
        {
            Name = "Bounds",
            MouseFilter = Control.MouseFilterEnum.Ignore,
            Position = new Vector2(-300f, -520f),
            Size = new Vector2(600f, 520f),
        };
        AddOwned(bounds);

        var centerPos = new Marker2D { Name = "CenterPos", Position = new Vector2(0f, -260f) };
        AddOwned(centerPos);

        var intentPos = new Marker2D { Name = "IntentPos", Position = new Vector2(0f, -600f) };
        AddOwned(intentPos);

        var talkPos = new Marker2D { Name = "TalkPos", Position = new Vector2(0f, -400f) };
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

        // Boss 站在右侧，攻击时向左突进。
        var attack = new Animation { Length = 0.36f };
        int at = attack.AddTrack(Animation.TrackType.Value);
        attack.TrackSetPath(at, "Visuals:position");
        attack.TrackInsertKey(at, 0.00, basePos);
        attack.TrackInsertKey(at, 0.12, basePos + new Vector2(-42, 0));
        attack.TrackInsertKey(at, 0.26, basePos + new Vector2(-14, 0));
        attack.TrackInsertKey(at, 0.36, basePos);
        lib.AddAnimation("attack", attack);

        var cast = new Animation { Length = 0.42f };
        int ct = cast.AddTrack(Animation.TrackType.Value);
        cast.TrackSetPath(ct, "Visuals:position");
        cast.TrackInsertKey(ct, 0.00, basePos);
        cast.TrackInsertKey(ct, 0.16, basePos + new Vector2(0, -16));
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
}

// 回归意向：图标=原版 Heal，文本显示「回复 X 点生命」。
// ⚠ NIntent 只给 AttackIntent / StatusIntent 渲染数字标签（HealIntent 永远只显示图标），
// 因此这里继承 StatusIntent 并改回 Heal 的图标/意图类型；HasIntentTip=false 避免悬浮标题
// 仍显示「状态牌」。
public sealed class DarkWorldReturnIntent : StatusIntent
{
    private readonly Func<int> _cardCount;

    public DarkWorldReturnIntent(Func<int> cardCount) : base(0)
    {
        _cardCount = cardCount;
    }

    public override IntentType IntentType => IntentType.Heal;

    protected override string SpritePath => "atlases/intent_atlas.sprites/intent_heal.tres";

    public override bool HasIntentTip => false;

    public override LocString GetIntentLabel(IEnumerable<Creature> targets, Creature owner)
    {
        LocString label = new("monsters",
            "LIGHTSWORN_MONSTER_DARK_WORLD_GRAPHA.moves.DARK_WORLD_RETURN.intentLabel");
        label.Add("Amount", _cardCount() * DarkWorldGrapha.ReturnHealPerCard);
        return label;
    }
}

// ================= 洗脑 debuff =================
// 「打出的下一张牌无效」：ModifyCardPlayCount 返回 0 → 费用照付、牌进弃牌堆、不执行任何 OnPlay 效果。
// 本身是可见 Debuff → 人工制品在 PowerCmd.Apply 阶段会正常抵消（每层人工制品挡一次施加）。
// 状态牌（洗脑本身）不消耗层数，避免抽到第二张洗脑时把它自己吞掉。
public class DarkWorldBrainwashPower : ModPowerTemplate
{
    public override PowerType Type => PowerType.Debuff;
    public override PowerStackType StackType => PowerStackType.Counter;

    public override PowerAssetProfile AssetProfile => new(
        IconPath: "res://lightsworn/images/powers/darkworldbrainwash.png",
        BigIconPath: "res://lightsworn/images/powers/darkworldbrainwash_big.png");

    public override int ModifyCardPlayCount(CardModel card, Creature? target, int playCount)
    {
        if (playCount <= 0) return playCount;
        if (card.Owner?.Creature != Owner) return playCount;
        if (card.Type == CardType.Status) return playCount;
        if (Amount <= 0) return playCount;

        Flash();
        SetAmount(Amount - 1);
        if (Amount <= 0)
            RemoveInternal();

        // 能力牌的特例：正常打出时 OnPlayWrapper 会先播 PlayPowerCardFlyVfx 把卡节点飞走；
        // playCount=0 跳过整个循环 → 模型被 RemoveFromCombat 移除，但 NCard 节点留在场上
        // （RemoveFromCombat 对 "Power in Play" 故意跳过节点动画）。这里补一次纯 UI 清理。
        if (card.Type == CardType.Power)
            TaskHelper.RunSafely(RemoveNullifiedPowerCardNode(card));

        return 0;
    }

    private static async Task RemoveNullifiedPowerCardNode(CardModel card)
    {
        // 等 OnPlayWrapper 走完结算（模型移出战斗），再清理残留节点；纯本地表现，不参与校验和。
        await Cmd.CustomScaledWait(0.35f, 0.6f);
        NCard? node = NCard.FindOnTable(card);
        if (node == null) return;
        NCombatRoom? room = NCombatRoom.Instance;
        if (room != null)
        {
            if (room.Ui.PlayQueue.IsAncestorOf(node))
                room.Ui.PlayQueue.RemoveCardFromQueueForCancellation(node);
            if (room.Ui.Hand.IsAncestorOf(node))
                room.Ui.Hand.Remove(card);
        }
        node.QueueFree();
    }
}

// ================= 被动：暗黑界的诱惑 =================
// 每玩家回合的第一次弃置（不含回合结束清理）触发，按第一张牌类型分支，然后额外塞1张暗黑界攻击卡。
// 只监听 CardCmd.Discard（AfterCardDiscarded）——回合结束 Flush 走 CardPileCmd.Add + AfterFlush，不经过这里。
public class DarkWorldTemptationPower : ModPowerTemplate
{
    private readonly HashSet<Player> _triggeredThisTurn = new();

    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Single;

    public override PowerAssetProfile AssetProfile => new(
        IconPath: "res://lightsworn/images/powers/darkworldtemptation.png",
        BigIconPath: "res://lightsworn/images/powers/darkworldtemptation_big.png");

    public override Task AfterPlayerTurnStartEarly(PlayerChoiceContext choiceContext, Player player)
    {
        if (player.Creature.CombatState == Owner.CombatState)
            _triggeredThisTurn.Remove(player);
        return Task.CompletedTask;
    }

    public override async Task AfterCardDiscarded(PlayerChoiceContext choiceContext, CardModel card)
    {
        Player? player = card.Owner;
        if (!Owner.IsAlive) return;
        if (player?.Creature == null || player.Creature.Side != CombatSide.Player) return;
        if (card.Pile?.Type != PileType.Discard) return;
        if (!_triggeredThisTurn.Add(player)) return;
        if (Owner.Monster == null) return;

        Flash();

        // ① 卡牌自身的「从手牌被弃置时」效果：玩家方监听器排在敌人能力之前，已经先结算。
        // ② 按第一张牌的类型结算被动分支。
        switch (card.Type)
        {
            case CardType.Attack:
                await PowerCmd.Apply<StrengthPower>(
                    choiceContext, Owner, 1, Owner, null);
                break;

            case CardType.Skill:
                await DarkWorldBossCards.AddBrainwashingToDraw(choiceContext, player);
                break;

            case CardType.Power:
                await DiscardRandomHandCards(choiceContext, player, 2);
                break;

            default:
                // 其他（状态/诅咒等）：复制一张同名牌洗入抽牌堆。
                CardModel clone = card.CreateClone();
                await CardPileCmd.AddGeneratedCardToCombat(
                    clone, PileType.Draw, player, CardPilePosition.Random);
                break;
        }

        // ③ 每次触发额外塞 1 张随机暗黑界攻击卡。
        await DarkWorldBossCards.AddRandomAttackToDraw(choiceContext, player, Owner.Monster.Rng);
    }

    private async Task DiscardRandomHandCards(PlayerChoiceContext choiceContext, Player player, int count)
    {
        List<CardModel> hand = PileType.Hand.GetPile(player).Cards.ToList();
        List<CardModel> discarded = new();
        for (int i = 0; i < count && hand.Count > 0; i++)
        {
            CardModel? pick = Owner.Monster.Rng.NextItem(hand);
            if (pick == null) break;
            hand.Remove(pick);
            discarded.Add(pick);
        }
        if (discarded.Count > 0)
            await CardCmd.Discard(choiceContext, discarded);
    }
}

// ================= 战斗内生成工具 =================
internal static class DarkWorldBossCards
{
    public static async Task AddRandomAttackToDraw(PlayerChoiceContext ctx, Player player, Rng rng)
    {
        CardModel canonical = rng.NextInt(4) switch
        {
            0 => ModelDb.Card<DarkWorldKelt>(),
            1 => ModelDb.Card<DarkWorldLatinum>(),
            2 => ModelDb.Card<DarkWorldSillva>(),
            _ => ModelDb.Card<DarkWorldGoldd>(),
        };
        CardModel card = player.Creature.CombatState!.CreateCard(canonical, player);
        await CardPileCmd.AddGeneratedCardToCombat(
            card, PileType.Draw, player, CardPilePosition.Random);
    }

    public static async Task AddBrainwashingToDraw(PlayerChoiceContext ctx, Player player)
    {
        CardModel card = player.Creature.CombatState!.CreateCard<DarkWorldBrainwashing>(player);
        await CardPileCmd.AddGeneratedCardToCombat(
            card, PileType.Draw, player, CardPilePosition.Random);
    }
}

// ================= 遭遇（三层 Glory Boss 池） =================
// Boss 发现顺序：原版 3 个三层 Boss 都见过后才会轮到 mod Boss（调试用控制台 fight <ID> 直达）。
[RegisterActEncounter(typeof(Glory))]
public class DarkWorldGraphaBoss : ModEncounterTemplate
{
    public override RoomType RoomType => RoomType.Boss;

    public override IEnumerable<MonsterModel> AllPossibleMonsters => [ModelDb.Monster<DarkWorldGrapha>()];

    public override EncounterAssetProfile AssetProfile => new(
        BossNodeSpinePath: "res://lightsworn/images/map/lightsworn/dark_world_grapha_boss_icon",
        RunHistoryIconPath: "res://lightsworn/images/ui/run_history/dark_world_grapha_boss.png",
        RunHistoryIconOutlinePath: "res://lightsworn/images/ui/run_history/dark_world_grapha_boss_outline.png");

    protected override IReadOnlyList<(MonsterModel, string?)> GenerateMonsters() =>
        [(ModelDb.Monster<DarkWorldGrapha>().ToMutable(), null)];
}
