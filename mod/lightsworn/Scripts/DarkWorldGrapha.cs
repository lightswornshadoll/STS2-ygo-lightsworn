using Godot;
using HarmonyLib;
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
using STS2RitsuLib.Patching.Models;

namespace Lightsworn;

// ================= 暗黑界的龙神王 格拉法（三层超规格 Boss） =================
// 设计基线：design\暗黑界龙神王boss设计.md（方案 B：雷→军势→登极→回归→取引→洗脑）。
// 基础 800 血（高进阶 880）；6 招固定循环；无阶段转换。
// v0.6.4：起手手牌塞 2/3 张诅咒；新增「暗黑界的侵蚀」（每弃 2 张手牌塞 1 张诅咒回手）；
// 三招伤害 ×1.3；取引改为生成 2 张诅咒并弃光手牌诅咒；洗脑数量 = ceil(当前回合/2)；
// 诱惑的攻击分支改为 +2 力量。
// 全部随机数使用 monster.Rng（联机确定性）；被动按玩家回合记「本回合是否已触发」。
[RegisterMonster]
public class DarkWorldGrapha : ModMonsterTemplate
{
    public const int ReturnHealPerCard = 50;

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
    private const int DealingsCurses = 2;

    // v0.6.4：三招伤害统一按旧值 ×1.3 后四舍五入（8→10、9→12、10→13、11→14、30→39、33→43）。
    // 四张暗黑界诅咒卡的自伤不算“Boss 攻击伤害”，保持不变。
    private int ThunderDamage => AscensionHelper.GetValueIfAscension(AscensionLevel.DeadlyEnemies, 12, 10);
    private int ForcesDamage => AscensionHelper.GetValueIfAscension(AscensionLevel.DeadlyEnemies, 14, 13);
    private int AscensionDamage => AscensionHelper.GetValueIfAscension(AscensionLevel.DeadlyEnemies, 43, 39);

    // 洗脑数量 = ceil(当前回合数 / 2)。RoundNumber 在敌方回合结束、玩家回合开始时递增：
    // 第一次洗脑（B6）为 3 张，第二次（B12）为 6 张，依此类推。
    private int BrainwashCount => CombatState == null ? 1 : (CombatState.RoundNumber + 1) / 2;

    public override int MinInitialHp => AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 880, 800);
    public override int MaxInitialHp => MinInitialHp;

    // 运行时构建静态立绘（同圣女角色方案，不能用引用游戏脚本的 tscn）。
    // 这里仍把 PNG 填进 AssetProfile：RitsuLib 的 MonsterVisualsPathPatch 会让 AssetPaths 预载这张图；
    // CreateVisuals 的实际路径由 TryCreateCreatureVisuals 接管。
    public override MonsterAssetProfile AssetProfile => new(
        VisualsScenePath: "res://lightsworn/images/monsters/dark_world_grapha.png");

    public override async Task AfterAddedToRoom()
    {
        PlayerChoiceContext ctx = new ThrowingPlayerChoiceContext();
        if (!Creature.Powers.Any(p => p is DarkWorldTemptationPower))
            await PowerCmd.Apply<DarkWorldTemptationPower>(ctx, Creature, 1, Creature, null);
        if (!Creature.Powers.Any(p => p is DarkWorldErosionPower))
            await PowerCmd.Apply<DarkWorldErosionPower>(ctx, Creature, 1, Creature, null);
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
            new DarkWorldBrainwashIntent(() => BrainwashCount));

        thunder.FollowUpState = forces;
        forces.FollowUpState = ascension;
        ascension.FollowUpState = returnMove;
        returnMove.FollowUpState = dealings;
        dealings.FollowUpState = brainwash;
        brainwash.FollowUpState = thunder;

        return new MonsterMoveStateMachine(
            [thunder, forces, ascension, returnMove, dealings, brainwash], thunder);
    }

    // 暗黑界之雷：10×3 伤害（高进阶 12×3）；施加 3 易伤 + 3 虚弱。
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

    // 暗黑界的军势：13 伤害（高进阶 14）；给每个玩家洗入 3 张随机暗黑界诅咒卡。
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

    // 暗黑界的登极：39 伤害（高进阶 43，吃易伤/力量）。
    private async Task AscensionMove(IReadOnlyList<Creature> targets)
    {
        await DamageCmd.Attack(AscensionDamage).FromMonster(this)
            .WithAttackerAnim("Attack", 0.5f)
            .WithHitFx("vfx/vfx_heavy_blunt")
            .Execute(null);
    }

    // 龙神回归：吸收玩家抽牌堆 + 弃牌堆 + 消耗堆中所有暗黑界诅咒卡，每张回复 50 生命。
    // 被吸收的卡移出战斗（不进消耗堆）；手牌是玩家的安全区，不吸收。
    // v0.6.1 已知问题4：吸收范围追加消耗堆，回血 30/张 → 50/张。
    private async Task ReturnMove(IReadOnlyList<Creature> targets)
    {
        await CreatureCmd.TriggerAnim(Creature, "Cast", 0.5f);
        List<CardModel> absorbed = new();
        foreach (Player player in CombatState.Players)
        {
            absorbed.AddRange(PileType.Draw.GetPile(player).Cards.Where(IsDarkWorldAttack));
            absorbed.AddRange(PileType.Discard.GetPile(player).Cards.Where(IsDarkWorldAttack));
            absorbed.AddRange(PileType.Exhaust.GetPile(player).Cards.Where(IsDarkWorldAttack));
        }

        if (absorbed.Count > 0)
        {
            await CardPileCmd.RemoveFromCombat(absorbed);
            await CreatureCmd.Heal(Creature, absorbed.Count * ReturnHealPerCard);
        }
    }

    // 暗黑界的取引：施加 5 虚弱 + 5 易伤；随机生成 2 张暗黑界诅咒到手牌，
    // 然后弃置手牌中所有暗黑界诅咒。强制弃置走 CardCmd.Discard → 正常触发诅咒自身、
    // 「暗黑界的诱惑」与「暗黑界的侵蚀」的弃置效果。
    private async Task DealingsMove(IReadOnlyList<Creature> targets)
    {
        await CreatureCmd.TriggerAnim(Creature, "Cast", 0.4f);
        PlayerChoiceContext ctx = new ThrowingPlayerChoiceContext();
        foreach (Player player in CombatState.Players)
        {
            if (!player.Creature.IsAlive) continue;
            await PowerCmd.Apply<WeakPower>(ctx, player.Creature, DealingsDebuff, Creature, null);
            await PowerCmd.Apply<VulnerablePower>(ctx, player.Creature, DealingsDebuff, Creature, null);

            for (int i = 0; i < DealingsCurses; i++)
                await DarkWorldBossCards.AddRandomAttackToHand(ctx, player, Rng);

            List<CardModel> curses = PileType.Hand.GetPile(player).Cards
                .Where(IsDarkWorldAttack).ToList();
            foreach (CardModel curse in curses)
            {
                // 军神被弃置时会把 2 张手牌洗回抽牌堆；这些牌已经不在手牌，跳过。
                // 逐张弃置还能让侵蚀在每 2 张后塞回来的新诅咒留在手里（不在快照里）。
                if (curse.Pile?.Type != PileType.Hand) continue;
                await CardCmd.Discard(ctx, curse);
            }
        }
    }

    // 暗黑界的洗脑：给每个玩家洗入 ceil(当前回合/2) 张「暗黑界的洗脑」状态。
    private async Task BrainwashMove(IReadOnlyList<Creature> targets)
    {
        await CreatureCmd.TriggerAnim(Creature, "Cast", 0.4f);
        int count = BrainwashCount;
        PlayerChoiceContext ctx = new ThrowingPlayerChoiceContext();
        foreach (Player player in CombatState.Players)
        {
            if (!player.Creature.IsAlive) continue;
            for (int i = 0; i < count; i++)
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
            count += PileType.Exhaust.GetPile(player).Cards.Count(IsDarkWorldAttack);
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

        // v0.6.3：换用用户重扣的 1536×1536 立绘（内容 bbox≈(52,296)-(1505,1339)，可见区 1453×1043）。
        // 0.5 缩放 → 宽约 727、高约 522；内容底边相对纹理中心 571px → Position.Y=-285.5 时脚底贴场景原点；
        // 内容中心相对纹理中心偏右 10.5px → Position.X=-5.25 让内容视觉居中。
        var sprite = new Sprite2D
        {
            Name = "Visuals",
            Texture = ResourceLoader.Load<Texture2D>("res://lightsworn/images/monsters/dark_world_grapha.png"),
            Position = new Vector2(-5.25f, -285.5f),
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

// 洗脑意向：数量随当前回合增长（ceil(n/2)）。
// StatusIntent 的 CardCount 是只读构造参数，这里用 Func<int> 在渲染/结算时现算，
// 并同时覆写数字标签与悬浮描述，避免悬浮提示里仍显示构造时的 0。
public sealed class DarkWorldBrainwashIntent : StatusIntent
{
    private readonly Func<int> _count;

    public DarkWorldBrainwashIntent(Func<int> count) : base(0)
    {
        _count = count;
    }

    public override LocString GetIntentLabel(IEnumerable<Creature> targets, Creature owner)
    {
        LocString label = new("intents", "FORMAT_STATUS_CARD_COUNT");
        label.Add("CardCount", _count());
        return label;
    }

    protected override LocString GetIntentDescription(IEnumerable<Creature> targets, Creature owner)
    {
        LocString description = new("intents", "STATUS.description");
        ICombatState? combatState = owner.CombatState;
        description.Add("IsMultiplayer", combatState != null && combatState.RunState.Players.Count > 1);
        description.Add("CardCount", _count());
        return description;
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
// 每玩家回合的第一次弃置（含弃光；不含回合结束清理）触发，按第一张牌类型分支，然后额外塞1张暗黑界诅咒卡。
// 手牌弃置=CardCmd.Discard → AfterCardDiscarded；弃光=抽牌堆→弃牌堆 → AfterCardChangedPiles。
// 两条钩子互斥（原版源码实证：手牌弃置不会走 Draw→Discard 分支），不会重复触发。
// 回合结束 Flush 走 CardPileCmd.Add + AfterFlush，两条钩子都不经过。
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
        if (card.Pile?.Type != PileType.Discard) return;
        await TryTrigger(choiceContext, card);
    }

    // 弃光（从抽牌堆弃到弃牌堆）：v0.6.1 已知问题5——原实现只监听手牌弃置，弃光完全不触发。
    // 该钩子没有 PlayerChoiceContext，用 BlockingPlayerChoiceContext（内部只做随机弃牌/生成，无玩家选择）。
    public override async Task AfterCardChangedPiles(CardModel card, PileType oldPileType, AbstractModel? clonedBy)
    {
        if (oldPileType != PileType.Draw || card.Pile?.Type != PileType.Discard) return;
        await TryTrigger(new BlockingPlayerChoiceContext(), card);
    }

    private async Task TryTrigger(PlayerChoiceContext choiceContext, CardModel card)
    {
        Player? player = card.Owner;
        if (!Owner.IsAlive) return;
        if (player?.Creature == null || player.Creature.Side != CombatSide.Player) return;
        if (!_triggeredThisTurn.Add(player)) return;
        if (Owner.Monster == null) return;

        Flash();

        // ① 卡牌自身的「从手牌被弃置时」效果：玩家方监听器排在敌人能力之前，已经先结算。
        // ② 按第一张牌的类型结算被动分支。
        switch (card.Type)
        {
            case CardType.Attack:
                await PowerCmd.Apply<StrengthPower>(
                    choiceContext, Owner, 2, Owner, null);
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

        // ③ 每次触发额外塞 1 张随机暗黑界诅咒卡。
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

// ================= 被动：暗黑界的侵蚀 =================
// 战斗开始时把 2 张（高进阶 3 张）随机暗黑界诅咒直接塞进玩家手牌；
// 之后每从手牌弃置 2 张牌，就把 1 张随机暗黑界诅咒塞回玩家手牌（按玩家独立计数，余数保留）。
// 关键时序：AfterAddedToRoom 早于 CombatManager.IsInProgress=true，不能在那里生成战斗卡；
// BeforeCombatStart 在 IsInProgress=true 之后、开局抽牌之前执行，是起手塞牌的正确钩子。
// 回合结束的手牌清理走 Flush，不经过 AfterCardDiscarded，因此不会白送诅咒（与诱惑一致）。
public class DarkWorldErosionPower : ModPowerTemplate
{
    private readonly Dictionary<Player, int> _discardedSinceLastCurse = new();
    private bool _startCursesAdded;

    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Single;

    public override PowerAssetProfile AssetProfile => new(
        IconPath: "res://lightsworn/images/powers/darkworlderosion.png",
        BigIconPath: "res://lightsworn/images/powers/darkworlderosion_big.png");

    private static int StartCurseCount =>
        AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 3, 2);

    public override async Task BeforeCombatStart()
    {
        if (_startCursesAdded) return;
        _startCursesAdded = true;
        if (Owner.CombatState == null || Owner.Monster == null) return;

        PlayerChoiceContext ctx = new ThrowingPlayerChoiceContext();
        foreach (Player player in Owner.CombatState.Players)
        {
            if (!player.Creature.IsAlive) continue;
            for (int i = 0; i < StartCurseCount; i++)
                await DarkWorldBossCards.AddRandomAttackToHand(ctx, player, Owner.Monster.Rng);
        }
    }

    public override async Task AfterCardDiscarded(PlayerChoiceContext choiceContext, CardModel card)
    {
        if (card.Pile?.Type != PileType.Discard) return;
        Player? player = card.Owner;
        if (player?.Creature == null || player.Creature.Side != CombatSide.Player) return;
        if (!Owner.IsAlive || Owner.Monster == null) return;

        int count = _discardedSinceLastCurse.TryGetValue(player, out int previous)
            ? previous + 1
            : 1;
        if (count < 2)
        {
            _discardedSinceLastCurse[player] = count;
            return;
        }

        _discardedSinceLastCurse[player] = count - 2;
        await DarkWorldBossCards.AddRandomAttackToHand(
            choiceContext, player, Owner.Monster.Rng);
    }
}

// ================= 战斗内生成工具 =================
internal static class DarkWorldBossCards
{
    private static CardModel CreateRandomAttackCard(Player player, Rng rng)
    {
        CardModel canonical = rng.NextInt(4) switch
        {
            0 => ModelDb.Card<DarkWorldKelt>(),
            1 => ModelDb.Card<DarkWorldLatinum>(),
            2 => ModelDb.Card<DarkWorldSillva>(),
            _ => ModelDb.Card<DarkWorldGoldd>(),
        };
        return player.Creature.CombatState!.CreateCard(canonical, player);
    }

    public static async Task AddRandomAttackToDraw(PlayerChoiceContext ctx, Player player, Rng rng)
    {
        CardModel card = CreateRandomAttackCard(player, rng);
        await CardPileCmd.AddGeneratedCardToCombat(
            card, PileType.Draw, player, CardPilePosition.Random);
    }

    public static async Task AddRandomAttackToHand(PlayerChoiceContext ctx, Player player, Rng rng)
    {
        CardModel card = CreateRandomAttackCard(player, rng);
        // 手牌上限 10：满手时改为进入弃牌堆，避免把 UI/牌堆撑坏。
        PileType target = PileType.Hand.GetPile(player).Cards.Count < CardPile.MaxCardsInHand
            ? PileType.Hand
            : PileType.Discard;
        await CardPileCmd.AddGeneratedCardToCombat(
            card, target, player, CardPilePosition.Random);
    }

    public static async Task AddBrainwashingToDraw(PlayerChoiceContext ctx, Player player)
    {
        CardModel card = player.Creature.CombatState!.CreateCard<DarkWorldBrainwashing>(player);
        await CardPileCmd.AddGeneratedCardToCombat(
            card, PileType.Draw, player, CardPilePosition.Random);
    }
}

// ================= 遭遇（三层 Glory Boss 池） =================
// 已知问题2（v0.6.1）：原版 Glory.BossDiscoveryOrder 只有女王/试验体/万象玻璃，
// RunManager.GenerateRooms → ApplyDiscoveryOrderModifications 会把「第一个未见过」的原版 Boss
// 直接强制成本局三层 Boss——mod Boss 不在该列表里，所以没打过格拉法的玩家永远先见女王。
// RitsuLib 的 BossDiscoveryOrderPostfix 只做 act 有效性过滤，不会追加 mod Boss。
// 这里给 Glory 的具体 getter 挂 postfix，把格拉法插到最前：未见过时必出，见过后自然回到原版顺序。
[RegisterActEncounter(typeof(Glory))]
public class DarkWorldGraphaBoss : ModEncounterTemplate
{
    public override RoomType RoomType => RoomType.Boss;

    public override IEnumerable<MonsterModel> AllPossibleMonsters => [ModelDb.Monster<DarkWorldGrapha>()];

    // 地图节点图标走原版 PNG Boss 的约定：BossNodePath 是无扩展名的 _icon 基路径，
    // 游戏自己拼 ".png" / "_outline.png"。不能填进 RitsuLib 的 AssetProfile.BossNodeSpinePath：
    // 那个补丁会先做 ResourceLoader.Exists(路径) 校验，无扩展名路径在 Godot 里恒为 false，
    // 自定义路径被丢弃后回退到不存在的默认 Spine 路径 → 地图上不显示图标。
    public override string BossNodePath => "res://lightsworn/images/map/lightsworn/dark_world_grapha_boss_icon";

    public override EncounterAssetProfile AssetProfile => new(
        RunHistoryIconPath: "res://lightsworn/images/ui/run_history/dark_world_grapha_boss.png",
        RunHistoryIconOutlinePath: "res://lightsworn/images/ui/run_history/dark_world_grapha_boss_outline.png");

    protected override IReadOnlyList<(MonsterModel, string?)> GenerateMonsters() =>
        [(ModelDb.Monster<DarkWorldGrapha>().ToMutable(), null)];
}

internal sealed class DarkWorldGraphaDiscoveryPatch : IPatchMethod
{
    public static string PatchId => "lightsworn_act3_boss_discovery";
    public static string Description => "Prioritize Lightsworn act 3 bosses (Grapha, then Tierra) in boss discovery until first seen";
    public static ModPatchTarget[] GetTargets() =>
        [new ModPatchTarget(typeof(Glory), "BossDiscoveryOrder", MethodType.Getter)];

    public static void Postfix(ref IEnumerable<EncounterModel> __result)
    {
        EncounterModel grapha = ModelDb.Encounter<DarkWorldGraphaBoss>();
        EncounterModel tierra = ModelDb.Encounter<InfernoidTierraBoss>();
        __result = new[] { grapha, tierra }.Concat(__result.Where(e => e.Id != grapha.Id && e.Id != tierra.Id));
    }
}
