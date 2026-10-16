using Godot;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Characters;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Relics;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Cards;
using MegaCrit.Sts2.Core.Nodes.Combat;
using MegaCrit.Sts2.Core.Random;
using MegaCrit.Sts2.Core.Rooms;
using MegaCrit.Sts2.Core.Saves.Runs;
using MegaCrit.Sts2.Core.Unlocks;
using STS2RitsuLib.Scaffolding.Characters;
// 问题6：WorldProceduralVisuals（商店/火堆程序化形象）所需命名空间
using STS2RitsuLib.Scaffolding.Characters.Visuals.Definition;
using STS2RitsuLib.Scaffolding.Visuals.Definition;

namespace Lightsworn;

// ============ 卡池（v0.5.0：BaseLib CustomCardPoolModel → RitsuLib TypeList*PoolModel） ============
// 卡/遗物/药水通过 [RegisterCard]/[RegisterRelic] 特性注入池（ModHelper.AddModelToPool）；
// 池的 EnergyColorName 系 BaseLib 自动行为的替代（能量图标按此前缀映射到 TextEnergyIconPath/BigEnergyIconPath）。
public class LightswornCardPool : TypeListCardPoolModel
{
    public override string Title => "lightsworn";
    public override string EnergyColorName => "lightsworn";
    public override string? TextEnergyIconPath => "res://lightsworn/images/energy.png";
    public override string? BigEnergyIconPath => "res://lightsworn/images/energy_big.png";
    public override Color DeckEntryCardColor => new(0.98f, 0.87f, 0.44f);
    public override bool IsColorless => false;

    // 金色卡框（原 BaseLib ShaderColor(0.96,0.82,0.38) 的替代）：游戏 HSV shader 材质
    public override Material? PoolFrameMaterial => LsCompat.LightswornFrameMaterial(
        new Color(0.96f, 0.82f, 0.38f).H, new Color(0.96f, 0.82f, 0.38f).S, new Color(0.96f, 0.82f, 0.38f).V);

    // ⚠ 雪之化身修复（本批用户反馈）：mod 卡全部经 [RegisterCard] 注进本池（含战斗内令牌），
    // 而原版卡池从不收录令牌——雪之化身改金卡(Rare)后就失去了"Token 稀有度不进奖励"的保护，
    // 会以金卡身份出现在战斗奖励/事件选牌/尘封魔典等一切"卡池来源"里（原版 CreateForReward 对
    // Rare 没有额外过滤）。统一剔除所有"不进卡牌图鉴"的战斗专属牌（SnowSpirit/神影依/珠泪融合
    // Token，即全部 showInCardLibrary:false 的牌）：它们只由战斗内效果生成，永远不该被当作可获得卡。
    protected override IEnumerable<CardModel> FilterThroughEpochs(UnlockState unlockState, IEnumerable<CardModel> cards)
        => base.FilterThroughEpochs(unlockState, cards).Where(c => c.ShouldShowInCardLibrary);
}

public class LightswornRelicPool : TypeListRelicPoolModel
{
    public override string EnergyColorName => "lightsworn";
    public override string? TextEnergyIconPath => "res://lightsworn/images/energy.png";
    public override string? BigEnergyIconPath => "res://lightsworn/images/energy_big.png";
}

public class LightswornPotionPool : TypeListPotionPoolModel
{
    public override string EnergyColorName => "lightsworn";
    public override string? TextEnergyIconPath => "res://lightsworn/images/energy.png";
    public override string? BigEnergyIconPath => "res://lightsworn/images/energy_big.png";
}

// ============ 卡牌基类：统一卡图路径 + 「光道」标签按卡名自动授予 ============
public abstract class LsCard : ModCardTemplate
{
    public override string? CustomPortraitPath => $"res://lightsworn/images/cards/{GetType().Name}.png";

    private IEnumerable<CardTag>? _lsTags;

    // 问题5：只有中文名含「光道」的卡才打「光道」标签（在类声明标签基础上追加）
    public override IEnumerable<CardTag> Tags
    {
        get
        {
            if (_lsTags == null)
            {
                HashSet<CardTag> tags = new(CanonicalTags);
                if (Ls.LightswornNamed.Contains(GetType().Name))
                    tags.Add(Ls.Lightsworn);
                if (Ls.ShaddollNamed.Contains(GetType().Name))
                    tags.Add(Ls.Shaddoll);
                _lsTags = tags;
            }
            return _lsTags;
        }
    }

    protected LsCard(int baseCost, CardType type, CardRarity rarity, TargetType target, bool showInCardLibrary = true)
        : base(baseCost, type, rarity, target, showInCardLibrary)
    {
    }

    // ================= v0.5.4：正文内联关键词的悬浮提示（无需手写） =================
    // MILL/BANISH/TWILIGHT 已改为 ModKeywordCardDescriptionPlacement.None（卡面不再有独立词条行，
    // 见 Ls.cs 的说明）——机制名现在只出现在正文里（`[gold]弃光[/gold]{Mill:diff()}`）。
    // **悬浮提示不需要本类操心**，链路已由原版+RitsuLib 闭环（反编译实证，勿再加手写 tips）：
    //   ① 原版 `CardModel.HoverTips`：`foreach (CardKeyword keyword in Keywords)
    //      list.Add(HoverTipFactory.FromKeyword(keyword));`（sts2.decompiled.cs:65580）——
    //      `Keywords` 含 CanonicalKeywords，所以只要卡类声明了关键词就自动有提示；
    //   ② RitsuLib `HoverTipFactoryFromKeywordPatch`（Prefix，decompiled.cs:177489）把 mod 关键词
    //      改路由到 `ModKeywordRegistry.CreateHoverTip`，用注册的 title/description 建提示；
    //   ③ `IncludeInCardHoverTip: true`（默认，本 mod 未改）保留该提示；置 false 才由
    //      CardModelHoverTipsModKeywordPatch 后置剔除。
    // ⚠ 反面教训（v0.5.4 中途写过一版本）：在 AdditionalHoverTips 里对 Keywords 再挂一遍
    //   `HoverTipFactory.FromKeyword` 是**重复挂载**——原版已挂过一次，而 mod 关键词的提示实例
    //   不经原版 `_keywordHoverTips` 缓存（RitsuLib 每次 new），`Distinct()` 去不掉 → 卡面会出现
    //   两份同名提示。已删除，**别再写回来**。

    // 被光道卡从抽牌堆弃光（弃置到弃牌堆）时触发（黄昏之抹杀/黄昏之双龙的弃光联动，问题13/15）。
    // 只在 LsUtil.Mill / MillSelected 的卡牌来源重载中触发，且来源必须是光道牌；
    // 能力/遗物来源的弃光、以及除光（消耗）都不触发。
    protected internal virtual Task OnMilledByLsCard(PlayerChoiceContext ctx, CardModel source)
        => Task.CompletedTask;

    // 「伤害置0只持续一次」（LsUtil.ZeroDamageOnce：心影依融合/羽影依文蒂/虚影依神子晶/联结之影依化身）：
    // 原值记在卡上，打出后恢复。AfterCardPlayed 在牌离开打出堆之前触发——落弃牌堆时已是正常伤害。
    internal decimal? DamageRestoreAfterPlay;

    public override async Task AfterCardPlayed(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        // Hook.AfterCardPlayed 是广播：所有牌堆里的模型都会收到"任意卡打出"的通知（v0.4.24 实证：
        // 化身刚置0的影依兽在手牌里被化身打出的广播立刻恢复回9点）。必须只在自己被打出时恢复。
        if (cardPlay.Card == this && DamageRestoreAfterPlay is decimal restore)
        {
            DamageRestoreAfterPlay = null;
            if (DynamicVars.TryGetValue("Damage", out var damage))
                damage.BaseValue = restore;
        }
        await base.AfterCardPlayed(choiceContext, cardPlay);
    }
}

// ============ 光道圣徽（原初始遗物，v0.4.9 起进遗物池：每场战斗第一回合开始时弃光3） ============
// 稀有度从 Starter 改为 Uncommon 后才会被 RelicGrabBag 收录（掉落/商店只收白蓝金商店四档），
// 商店价走 Rarity 默认 MerchantCost=225。图标=RelicAssetProfile（原 BaseLib RelicImageOverridePatch 的替代）。
[RegisterRelic(typeof(LightswornRelicPool))]
public class LightswornSigil : ModRelicTemplate
{
    private bool _usedThisCombat;

    public override RelicRarity Rarity => RelicRarity.Uncommon;

    public override RelicAssetProfile AssetProfile => new(
        IconPath: "res://lightsworn/images/relics/sigil.png",
        IconOutlinePath: "res://lightsworn/images/relics/sigil.png",
        BigIconPath: "res://lightsworn/images/relics/sigil_big.png");

    public override Task AfterPlayerTurnStartEarly(PlayerChoiceContext choiceContext, Player player)
    {
        // 联机：AfterPlayerTurnStartEarly 对每个玩家的回合开始各触发一轮（含队友）——
        // 只在自己的回合开始弃光（不过滤会把队友的卡组当自己的弃）
        if (player != Owner) return Task.CompletedTask;
        if (_usedThisCombat) return Task.CompletedTask;
        return OnFirstTurn(choiceContext, player);
    }

    private async Task OnFirstTurn(PlayerChoiceContext ctx, Player player)
    {
        _usedThisCombat = true;
        Flash();
        // 用玩家来源弃光（不触发加洛斯的「光道牌弃光」联动——圣徽不是光道卡）
        await LsUtil.Mill(ctx, player, 3);
    }

    public override Task AfterCombatEnd(CombatRoom room)
    {
        _usedThisCombat = false;
        return Task.CompletedTask;
    }
}

// ============ 初始遗物：你必须玩游戏王（游戏王规则：卡组不满40张，战斗开始时补到40） ============
// 效果文本由用户钦定。生成来源=角色专属卡池；问题16：打击:防御:白:蓝:金 = 50:50:85:15:5
// （打击/防御直接生成初始牌「打击」「防御」），随机位置插入抽牌堆（Metamorphosis 原版范式：
// GetUnlockedCards + CombatState.CreateCard + AddGeneratedCardToCombat(Random)；
// RNG 用 CombatCardGeneration 通道保证种子可复现）。
// Starter 稀有度不会被 RelicGrabBag 收录，虽然挂着池标也只在初始遗物里出现。
//
// ⚠ v0.5.3 问题5修复：打/防保底上限。
// 旧实现每张牌独立 roll(205)，打击 50/205≈24.4% + 防御 50/205≈24.4% = 48.8% 打防。
// 独立同分布下打防数量服从 B(need, 0.4878)，右尾很厚：
//   实战最常见的 need=30（初始10张卡组）时 E=14.63 张(48.8%)、σ≈2.74，
//   旧实现有 P(打防 > 18 张=60%) ≈ 7.9%，95 分位是 19 张(63.3%)，最坏理论上 30 张(100%)。
// 用户要求「最多 60% 的卡是打/防」，即打防数必须 ≤ floor(need×0.6)。
// 新实现：先算上限 cap=floor(need×0.6)，边生成边计数，打防数一旦触顶，后续全部改为卡池抽取。
// 触顶后该次 roll 不再作废，而是归一化到卡池段继续使用（见下方 else 分支注释），
// 因此**每张牌仍然恰好消耗一次 NextInt(205)** → RNG 序列与消耗次数确定，同一 seed 各端结果一致。
// 只砍右尾、不设下限（用户只要求「最多」），运气极好时打防可以为 0。
[RegisterRelic(typeof(LightswornRelicPool))]
public class MustPlayYugioh : ModRelicTemplate
{
    private const int MinDeckSize = 40;

    public override RelicRarity Rarity => RelicRarity.Starter;

    public override RelicAssetProfile AssetProfile => new(
        IconPath: "res://lightsworn/images/relics/yugioh.png",
        IconOutlinePath: "res://lightsworn/images/relics/yugioh.png",
        BigIconPath: "res://lightsworn/images/relics/yugioh_big.png");

    public override async Task BeforeCombatStart()
    {
        CardPile draw = PileType.Draw.GetPile(Owner);
        int need = MinDeckSize - draw.Cards.Count;
        if (need <= 0) return;

        // 只取白/蓝/金三档（基础牌打击/防御、白雪Token等不参与生成）
        List<CardModel> pool = Owner.Character.CardPool
            .GetUnlockedCards(Owner.UnlockState, Owner.RunState.CardMultiplayerConstraint)
            .Where(c => c.CanBeGeneratedInCombat)
            .Where(c => c.Rarity is CardRarity.Common or CardRarity.Uncommon or CardRarity.Rare)
            .ToList();
        if (pool.Count == 0) return;
        Dictionary<CardRarity, List<CardModel>> byRarity = pool.GroupBy(c => c.Rarity)
            .ToDictionary(g => g.Key, g => g.ToList());

        Rng rng = Owner.RunState.Rng.CombatCardGeneration;
        var combatState = Owner.Creature.CombatState;
        if (combatState == null) return;

        // 问题5：打/防保底上限。need 张里最多 floor(need×0.6) 张是打击/防御，其余强制走卡池。
        // 用整数下取整（cap = need*3/5）：这是唯一能对**所有** need 都保证「打防 ≤ 60%」的取整方式。
        // 若用 ceil(need×0.6)，小 need 时会突破 60%（need=1→100%、2→100%、3→66.7%、4→75%、7→71.4%），
        // 与用户「最多60%」的硬性要求冲突；floor 的最大占比恰为 60.0%（在 need 为 5 的倍数时取到，
        // 例如实战最常见的 need=30 → cap=18=60%）。
        int basicCap = need * 3 / 5;
        int basicCount = 0;

        for (int i = 0; i < need; i++)
        {
            // 问题16：打击:防御:白:蓝:金 = 50:50:85:15:5（总205；打击/防御=本角色初始牌「打击」「防御」）
            // 注意：roll 必须无条件消耗一次，否则触顶后 RNG 序列会与旧版本分叉（联机/种子复现要求）。
            int roll = rng.NextInt(205);
            CardModel card;
            if (roll < 100 && basicCount < basicCap)
            {
                // 问题5：打防额度未用尽才允许生成；roll<50 打击 / 50-99 防御 的原始切分保持不变。
                basicCount++;
                card = roll < 50
                    ? combatState.CreateCard(ModelDb.Card<LightBlade>(), Owner)
                    : combatState.CreateCard(ModelDb.Card<LightWard>(), Owner);
            }
            else
            {
                // 白:蓝:金 = 85:15:5。
                // 问题5：打防触顶后，原本落入打防段的 roll∈[0,100) 也会走到这里，若直接沿用
                // 原边界（<185普通/<200罕见/稀有）会把白卡比例抬到 90%（185/205），偏离设计。
                // 所以先把 roll 归一化到卡池段的 105 个取值上：roll∈[100,205) 直接减100；
                // roll∈[0,100) 用整数等比缩放 roll*105/100 铺满同一区间（无浮点、纯整数 → 各端一致）。
                // 归一后落在卡池段的比例恰为 80.98:14.63:4.39，与 85:15:5（即 80.95:14.29:4.76）几乎一致。
                int poolRoll = roll < 100 ? roll * 105 / 100 : roll - 100;
                CardRarity rarity = poolRoll < 85 ? CardRarity.Common
                    : poolRoll < 100 ? CardRarity.Uncommon
                    : CardRarity.Rare;
                List<CardModel> options = byRarity.TryGetValue(rarity, out List<CardModel>? opts) && opts.Count > 0
                    ? opts
                    : pool;
                card = combatState.CreateCard(rng.NextItem(options)!, Owner);
            }
            await CardPileCmd.AddGeneratedCardToCombat(card, PileType.Draw, Owner, CardPilePosition.Random);
        }
        Flash();
    }
}

// ============ 猫狗双全：抽到光道兽 沃尔夫或光道弓手 费莉丝时，再抽1张牌（普通遗物） ============
// 图标=用户提供素材的中央徽章圆裁（自动避开右下角水印）。
// AfterCardDrawn 是战斗广播钩子：IterateHookListeners 含玩家全部未熔解遗物，每次有卡被抽到都会通知；
// 这里只对沃尔夫/费莉丝响应。再抽的1张若也是它们会继续触发（连锁抽牌，抽牌堆耗尽自动停止——
// CardPileCmd.Draw 自带手牌上限/洗牌/空堆检查）。fromHandDraw 不筛：回合抽牌与效果抽到都算「抽到」。
[RegisterRelic(typeof(LightswornRelicPool))]
public class CatsAndDogs : ModRelicTemplate
{
    public override RelicRarity Rarity => RelicRarity.Common;

    public override RelicAssetProfile AssetProfile => new(
        IconPath: "res://lightsworn/images/relics/cats_and_dogs.png",
        IconOutlinePath: "res://lightsworn/images/relics/cats_and_dogs.png",
        BigIconPath: "res://lightsworn/images/relics/cats_and_dogs_big.png");

    public override async Task AfterCardDrawn(PlayerChoiceContext choiceContext, CardModel card, bool fromHandDraw)
    {
        if (card.Owner != Owner || card is not (Wulf or Felis)) return;
        Flash();
        await CardPileCmd.Draw(choiceContext, 1m, Owner);
    }
}

// ============ 幻色珍珠（事件遗物，本批新增；「于珍珠世界相逢」选项二奖励） ============
// 图标=金色珍珠遗物原图 → 珠泪海蓝重上色（tools\make_phantom_pearl_icon.py，64/256 两档）。
// 效果：拾起时随机变成「金色珍珠」或「诅咒珍珠」的效果（各50%），1%概率是「发光珍珠」的效果。
//   ·金色珍珠（原版 GoldenPearl）：拾起时获得150金币；
//   ·诅咒珍珠（原版 CursedPearl）：拾起时加入1张诅咒「贪婪」并获得333金币；
//   ·发光珍珠（原版 RadiantPearl）：每场战斗第一回合抽牌时（BeforeHandDraw/TurnNumber==1），
//     将1张「冷光」加入手牌。
// 稀有度 Event：RelicGrabBag.Populate 只收 Common/Uncommon/Rare/Shop（Event 档被剔除），
// 商店价 999999999（RelicModel.MerchantCost）——只能由本事件发放（事件遗物语义）。
// 抽到的模式持久化用 [SavedProperty]（RitsuLib 把 mod 类型注入保存属性缓存；读档 Fill 走属性 setter，
// 会把描述里的「当前效果」刷新成对应文本）。RNG=玩家侧 PlayerRng.Rewards（联机同种子、各端确定性一致；
// 绝不能用 UnityEngine.Random 之类非同步源——联机校验和会断线）。
[RegisterRelic(typeof(LightswornRelicPool))]
public class PhantomPearl : ModRelicTemplate
{
    private const int ModeGolden = 0;
    private const int ModeCursed = 1;
    private const int ModeRadiant = 2;

    private const int GoldenGold = 150;   // = 原版金色珍珠 GoldVar
    private const int CursedGold = 333;   // = 原版诅咒珍珠 GoldVar

    public override RelicRarity Rarity => RelicRarity.Event;

    public override bool HasUponPickupEffect => true;

    public override RelicAssetProfile AssetProfile => new(
        IconPath: "res://lightsworn/images/relics/phantom_pearl.png",
        IconOutlinePath: "res://lightsworn/images/relics/phantom_pearl.png",
        BigIconPath: "res://lightsworn/images/relics/phantom_pearl_big.png");

    // 关联牌悬浮预览：可能抽到的两种素材牌（贪婪=诅咒牌，冷光=发光珍珠产物）
    protected override IEnumerable<IHoverTip> AdditionalHoverTips =>
        HoverTipFactory.FromCardWithCardHoverTips<Greed>()
            .Concat(HoverTipFactory.FromCardWithCardHoverTips<Luminesce>());

    protected override IEnumerable<DynamicVar> CanonicalVars =>
    [
        new StringVar("Effect", "未定"),   // 描述里 {Effect}：拾起后在 setter 里刷新为实际抽到的效果
    ];

    private int _pearlMode = ModeGolden;

    /// <summary>拾起时抽到的效果（0=金色 / 1=诅咒 / 2=发光）。</summary>
    [SavedProperty]
    public int PearlMode
    {
        get => _pearlMode;
        set
        {
            AssertMutable();
            _pearlMode = value;
            RefreshEffectText();
        }
    }

    public override async Task AfterObtained()
    {
        Rng rng = Owner.PlayerRng.Rewards;
        // 1% → 发光珍珠；其余各 50% → 金色 / 诅咒珍珠（掷两次只在非发光时发生，各端求值顺序一致）
        int mode = rng.NextInt(100) == 0
            ? ModeRadiant
            : (rng.NextInt(2) == 0 ? ModeGolden : ModeCursed);
        PearlMode = mode;   // setter 刷新描述里的「当前效果」
        Flash();
        switch (mode)
        {
            case ModeGolden:
                await PlayerCmd.GainGold(GoldenGold, Owner);
                break;
            case ModeCursed:
                await CardPileCmd.AddCurseToDeck<Greed>(Owner);
                await PlayerCmd.GainGold(CursedGold, Owner);
                break;
            case ModeRadiant:
                // 拾起时无即时效果：战斗内由 BeforeHandDraw 生效
                break;
        }
    }

    // 发光珍珠效果：每场战斗第一回合抽牌时，将1张「冷光」加入手牌（原版 RadiantPearl 同款钩子，
    // 联机：BeforeHandDraw 对每个玩家各触发一轮，必须过滤 Owner）
    public override async Task BeforeHandDraw(Player player, PlayerChoiceContext choiceContext, ICombatState combatState)
    {
        if (PearlMode != ModeRadiant || player != Owner) return;
        if (Owner.PlayerCombatState.TurnNumber != 1) return;
        List<CardModel> cards = [];
        cards.Add(Owner.Creature.CombatState.CreateCard<Luminesce>(Owner));
        Flash();
        await CardPileCmd.AddGeneratedCardsToCombat(cards, PileType.Hand, Owner);
    }

    private void RefreshEffectText()
    {
        if (DynamicVars.TryGetValue("Effect", out DynamicVar? effect) && effect is StringVar text)
        {
            text.StringValue = _pearlMode switch
            {
                ModeCursed => $"诅咒珍珠（获得1张贪婪与{CursedGold}金币）",
                ModeRadiant => "发光珍珠（每场战斗的第一回合，将1张冷光加入手牌）",
                _ => $"金色珍珠（获得{GoldenGold}金币）",
            };
        }
    }
}

// ============ 人物：光道圣女 密勒瓦（静态立绘形象，v0.4.7） ============
// v0.5.0：BaseLib PlaceholderCharacterModel → RitsuLib ModCharacterTemplate（PlaceholderCharacterId="ironclad"，
// 缺省外观从铁甲战士补全——商人/休息处/卡牌拖尾/选人转场/多人手势/音效/锁定立绘）。
// 无 Spine：战斗形象 = 全 C# 运行时构建的纯 Godot 节点树（Sprite2D 立绘 + AnimationPlayer）；
// 动画转发由 RitsuLib ModCreatureVisualPlayback 自动完成（Hit→hurt、Attack→attack、Cast→cast、Dead→die，
// 见 RitsuLib 别名表；收尾帧必须回到起始位置）。不能用 tscn 引 NCreatureVisuals 脚本——mod 导 pck
// 时解析不了游戏本体的 C# 脚本，会被导出器丢脚本。%独特名靠 Owner=根 + UniqueNameInOwner 注册。
[RegisterCharacter]
public class LightswornCharacter : ModCharacterTemplate<LightswornCardPool, LightswornRelicPool, LightswornPotionPool>
{
    private const string AssetDir = "res://lightsworn/images/character/";

    // ================= 问题6：商店 / 火堆取景常量 =================
    // 素材：battle.png 984×1000（RGBA，透明底）。实测不透明内容 bbox 覆盖整幅画布
    // （x 0-983、y 0-999：展开的双翼与法杖顶到边缘，"图心"≈画布中心，故缩放锚点用图心即可）。
    // 原版房间相机高约 720 逻辑像素、角色脚下约在房间中线偏下；战斗立绘当前用 0.33 缩放
    // （见 TryCreateCreatureVisuals：984×0.33≈325 宽）。
    //
    // 商店：商人摊位是直立站姿，脚本里 Merchant 的 Sprite2D 基准被放在 (0,-H/2)
    // （decompiled.cs:85042，H=纹素高=1000）→ 不覆盖样式时立绘会以"图片中心"贴在房间原点，
    // 1:1 的 984×1000 直接溢出。这里显式给 Scale，把立绘收到双脚落在摊位上的尺寸：
    //   0.34 → 984×0.34≈335 宽、1000×0.34≈340 高，与战斗立绘（0.33）几乎一致，观感统一；
    //   Position.Y 用 -H*scale/2 = -170 把"图心"从房间原点抬到脚底贴地
    //   （图心到图底 = H/2 = 500 纹素 → ×0.34 ≈ 170）。
    private static VisualNodeStyle MerchantStyle => VisualNodeStyle.Create(
        position: new Vector2(0f, -170f),
        scale: new Vector2(0.34f, 0.34f));

    // 火堆：用户要"坐在木头上"的感觉。battle.png 本身就是**坐姿**——双腿交叠、长裙铺开
    // （实测 y≥780 处不透明内容收窄到 x 182-765、最底部 y≥960 只剩 x 375-447，
    //  正是"裙摆铺在座面、双脚下垂"的轮廓）。所以不需要新素材，只需把这张坐姿图**放在木头上**：
    //   1) 比商店略放大（0.38 vs 0.34）：坐姿立绘的视觉重心更低，放大后裙摆才够宽盖住木桩顶面，
    //      避免"浮在木头上方"；984×0.38≈374 宽。
    //   2) Position.Y = -H*scale*0.62 ≈ -236：把图心抬到"裙摆下沿压住木头"的高度。
    //      取 0.62 而不是 0.5，是因为坐姿内容的**有效底边不在画布底**——最底部 40px 只有
    //      一双鞋（x 375-447），而裙摆主体在 y 780-940。用 0.62 让图心比"脚底贴地"
    //      再低约 0.12×1000×0.38≈46px，使裙摆正好搭在木头上、鞋略垂到木头前侧。
    //   3) Offset 再向下 -8：火堆木桩的顶面在房间地面之上，微调贴合。
    // 注：RitsuGodotNodeRestSiteCharacterFactory 的 Hitbox 是照**原尺寸纹素**给的
    //   （decompiled.cs:85171/85185，size=img*1.05、top=-size.Y*0.6），不随 Scale 收缩，
    //   所以点击热区仍覆盖整张立绘，无需额外处理。
    private static Vector2 RestSiteScale => new(0.38f, 0.38f);

    private static VisualNodeStyle RestSiteStyle => VisualNodeStyle.Create(
        position: new Vector2(0f, -236f),
        offset: new Vector2(0f, -8f),
        scale: RestSiteScale);

    public override Color NameColor => new(0.98f, 0.87f, 0.44f);
    public override Color EnergyLabelOutlineColor => new(0.85f, 0.68f, 0.25f);
    public override Color MapDrawingColor => new(0.98f, 0.87f, 0.44f);

    public override int StartingHp => 78;
    public override CharacterGender Gender => CharacterGender.Feminine;

    // RitsuLib ModCharacterTemplate 未实现的 CharacterModel 抽象成员（照铁甲战士默认值）
    public override int StartingGold => 99;
    public override float AttackAnimDelay => 0.15f;
    public override float CastAnimDelay => 0.25f;
    public override List<string> GetArchitectAttackVfx() =>
    [
        "vfx/vfx_attack_blunt", "vfx/vfx_heavy_blunt", "vfx/vfx_attack_slash",
        "vfx/vfx_bloody_impact", "vfx/vfx_rock_shatter",
    ];

    // 本批反馈问题4：初始卡组=4打击+4防御+1光道圣骑士简+1光道防护罩
    // （RitsuLib：StartingDeck 是 sealed，覆写 LocalStartingDeck 即可，注册表追加自动合并）
    protected override IEnumerable<CardModel> LocalStartingDeck =>
    [
        ModelDb.Card<LightBlade>(), ModelDb.Card<LightBlade>(), ModelDb.Card<LightBlade>(),
        ModelDb.Card<LightBlade>(),
        ModelDb.Card<LightWard>(), ModelDb.Card<LightWard>(), ModelDb.Card<LightWard>(),
        ModelDb.Card<LightWard>(),
        ModelDb.Card<Jain>(),
        ModelDb.Card<Barrier>(),
    ];

    // v0.4.9：初始遗物换为「你必须玩游戏王」，圣徽转入遗物池（稀有度已改 Uncommon）
    protected override IEnumerable<RelicModel> LocalStartingRelics => [ModelDb.Relic<MustPlayYugioh>()];

    // ---------- 静态立绘战斗形象 ----------
    protected override NCreatureVisuals? TryCreateCreatureVisuals()
    {
        var root = new NCreatureVisuals { Name = "SaintVisuals" };

        void AddOwned(Node node, bool unique = true)
        {
            root.AddChild(node);
            node.Owner = root;
            if (unique) node.UniqueNameInOwner = true;
        }

        // 立绘：battle.png 984×1000，缩放 0.33 → 台上约 325×330（对照原版角色），脚底贴场景原点
        var sprite = new Sprite2D
        {
            Name = "Visuals",
            Texture = ResourceLoader.Load<Texture2D>("res://lightsworn/images/character/battle.png"),
            Position = new Vector2(0f, -165f),
            Scale = new Vector2(0.33f, 0.33f),
        };
        AddOwned(sprite);

        var bounds = new Control
        {
            Name = "Bounds",
            MouseFilter = Control.MouseFilterEnum.Ignore,
            Position = new Vector2(-122f, -244f),
            Size = new Vector2(244f, 244f),
        };
        AddOwned(bounds);

        var centerPos = new Marker2D { Name = "CenterPos", Position = new Vector2(0f, -146f) };
        AddOwned(centerPos);

        var intentPos = new Marker2D { Name = "IntentPos", Position = new Vector2(0f, -302f) };
        AddOwned(intentPos);

        var anim = new AnimationPlayer { Name = "AnimationPlayer" };
        AddOwned(anim, unique: false);
        Vector2 basePos = sprite.Position;
        var lib = new AnimationLibrary();

        var hurt = new Animation { Length = 0.24f };
        int ht = hurt.AddTrack(Animation.TrackType.Value);
        hurt.TrackSetPath(ht, "Visuals:position");
        hurt.TrackInsertKey(ht, 0.00, basePos);
        hurt.TrackInsertKey(ht, 0.04, basePos + new Vector2(9, 0));
        hurt.TrackInsertKey(ht, 0.08, basePos - new Vector2(9, 0));
        hurt.TrackInsertKey(ht, 0.12, basePos + new Vector2(6, 0));
        hurt.TrackInsertKey(ht, 0.16, basePos - new Vector2(6, 0));
        hurt.TrackInsertKey(ht, 0.20, basePos + new Vector2(3, 0));
        hurt.TrackInsertKey(ht, 0.24, basePos);
        lib.AddAnimation("hurt", hurt);

        var attack = new Animation { Length = 0.30f };
        int at = attack.AddTrack(Animation.TrackType.Value);
        attack.TrackSetPath(at, "Visuals:position");
        attack.TrackInsertKey(at, 0.00, basePos);
        attack.TrackInsertKey(at, 0.10, basePos + new Vector2(26, 0));
        attack.TrackInsertKey(at, 0.22, basePos + new Vector2(10, 0));
        attack.TrackInsertKey(at, 0.30, basePos);
        lib.AddAnimation("attack", attack);

        var cast = new Animation { Length = 0.30f };
        int ct = cast.AddTrack(Animation.TrackType.Value);
        cast.TrackSetPath(ct, "Visuals:position");
        cast.TrackInsertKey(ct, 0.00, basePos);
        cast.TrackInsertKey(ct, 0.12, basePos + new Vector2(0, -12));
        cast.TrackInsertKey(ct, 0.30, basePos);
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

    // ---------- 选人界面 ----------
    public override string? CustomCharacterSelectBgPath => "res://lightsworn/visuals/saint_select_bg.tscn";
    public override string? CustomCharacterSelectIconPath => AssetDir + "select_button.png";

    // ---------- 顶栏/统计/战绩图标（v0.5.0：BaseLib CustomIcon(Control) → RitsuLib 纹理路径） ----------
    public override string? CustomIconTexturePath => AssetDir + "icon.png";
    public override string? CustomIconOutlineTexturePath => AssetDir + "icon_outline.png";

    // ---------- 左上角（顶栏）角色头像 = Character.Icon 场景（NTopBarPortrait.AddChild(player.Character.Icon)） ----------
    // ⚠ v0.5.1 修复：RitsuLib 的 ModCharacterTemplate.ResolvedAssetProfile 会把**未覆盖的资源槽从占位角色
    // （PlaceholderCharacterId=ironclad）继承**——不设置本项时头像场景继承铁甲的 ui/character_icons/ironclad_icon
    // → 对局里左上角头像显示铁甲。mod 版=同结构的纯 TextureRect 场景（saint_icon.tscn，无游戏脚本，可正常导 pck）。
    public override string? CustomIconPath => "res://lightsworn/visuals/saint_icon.tscn";

    // ---------- 能量球：走 RitsuLib 的"场景路径"正规入口（saint_energy_counter.tscn） ----------
    // ⚠ v0.5.1 修复：同一继承问题——不设置本项时 RitsuLib 的 NEnergyCounter.Create 前缀（HarmonyPriority 800）
    // 会用"继承自铁甲的能量球场景"建球并 return false 中止补丁链；mod 自建的 Create 前缀（默认优先级）永远跑不到
    // → 显示铁甲的红色八角球。改用场景后由 RitsuLib 的 RitsuNEnergyCounterNodeFactory 转换建球
    // （缺 %EnergyVfxBack/%EnergyVfxFront/Label/%StarAnchor 等槽位时自动补齐），自建 build 代码删除。
    public override string? CustomEnergyCounterPath => "res://lightsworn/visuals/saint_energy_counter.tscn";

    // ---------- 地图标记 ----------
    public override string? CustomMapMarkerPath => AssetDir + "map_marker.png";

    // ================= 商店 / 火堆形象（v0.5.3 问题6修复） =================
    // ⚠ 根因与 v0.5.1 的 CustomIconPath / CustomEnergyCounterPath 完全同源：
    //   RitsuLib 的 ModCharacterTemplate.ResolvedAssetProfile 会把**未覆盖的资源槽从占位角色
    //   （PlaceholderCharacterId="ironclad"）继承**（见 STS2-RitsuLib.Runtime.xml:50865-50873、
    //   decompiled.cs:105386 MergeScenes/MergeWorldProceduralVisuals）。而这两个槽位的取用点还会
    //   **二次兜底到 ironclad**：CharacterWorldScenePathFactoryHelper.EnumerateCandidatePaths
    //   在 decompiled.cs:111264-111271 明确写死「若角色 id 不是 ironclad，就再试一次 ironclad 的
    //   Scenes.MerchantAnimPath / Scenes.RestSiteAnimPath」。所以不覆盖时：
    //     商店 → 铁甲战士的 _merchant 场景；火堆 → 铁甲战士的 _rest_site 场景。
    //   原版取值见 sts2.decompiled.cs:66821 / 66823：
    //     CharacterModel.MerchantAnimPath => "merchant/characters/<id>_merchant"
    //     CharacterModel.RestSiteAnimPath => "rest_site/characters/<id>_rest_site"
    // 槽位名（已核对 RitsuLib 0.111.0）：
    //   CustomMerchantAnimPath（商店） / CustomRestSiteAnimPath（火堆）
    //   —— 声明见 STS2-RitsuLib.Runtime.xml:50544 / 50550（IModCharacterAssetOverrides），
    //      虚拟机实现见 decompiled.cs:106601，Harmony 补丁见 decompiled.cs:109686 / 109718。
    // 这两个槽位**允许直接给 Texture2D**（不必是场景）：
    //   decompiled.cs:109534-109535 IsCompatibleResource 对二者都用 IsLoadableAsAny(..., "PackedScene",
    //   typeof(PackedScene), typeof(Texture2D))；创建走 CreateFromSceneOrTexture（decompiled.cs:111203），
    //   Texture2D 分支交给 RitsuGodotNodeFactories.CreateFromResource —— 由
    //   RitsuNMerchantCharacterNodeFactory / RitsuNRestSiteCharacterNodeFactory 建节点
    //   （decompiled.cs:85025 / 85143）。所以**不需要新建 tscn**，也就绕开了
    //   「mod 导 pck 解析不了游戏本体 C# 脚本」的坑（见上方 TryCreateCreatureVisuals 注释）。
    //
    // 为什么不直接把 battle.png 丢给这两个槽位：
    //   1) 工厂给的默认取景是「整图按原尺寸居中」——RitsuNMerchantCharacterNodeFactory.FromTexture
    //      （decompiled.cs:85042）把 Sprite2D 放在 (0, -H/2)；火堆版（decompiled.cs:85193）放在
    //      (0, -H/10)。984×1000 的立绘按 1:1 塞进 1280×720 的房间会**远远溢出屏幕**，
    //      而且完全无法调比例——正是用户说的「比例不对」。
    //   2) 用户要的是「在火堆有坐在木头上的感觉」，这需要**可控的偏移/缩放/裁切**。
    //   所以改用 WorldProceduralVisuals（数据驱动，无需 tscn）把同一张 battle.png 绑到提示键上，
    //   并用 VisualNodeStyle 精确给位置/缩放/裁切区域。
    //   证据：CharacterWorldProceduralVisualSet（xml:52001-52012）就是为「让 mod 免于提供专用 tscn」
    //   而设；builder 见 xml:52140-52188；样式类型 VisualNodeStyle 见 decompiled.cs:82565。
    // 提示键（cue key）：火堆必须用原版三章循环名 overgrowth_loop / hive_loop / glory_loop
    //   （sts2.decompiled.cs:400835-400841 在 NRestSiteCharacter._Ready 里按 CurrentActIndex 选名，
    //     xml:52102-52107 也点名这三个）；商店用 relaxed_loop
    //   （sts2.decompiled.cs:292198 NMerchantCharacter._Ready 里 PlayAnimation("relaxed_loop", loop:true)）。
    //   另补 idle 兜底，防止某条状态机路径找不到键时变成空图。
    public override CharacterWorldProceduralVisualSet? WorldProceduralVisuals =>
        ModCharacterWorldSceneVisuals.Procedural()
            // --- 商店：站立立绘，略小于战斗尺寸，脚底对齐摊位 ---
            .Merchant(cues => cues
                .Single("relaxed_loop", AssetDir + "battle.png", MerchantStyle)
                .Single("idle", AssetDir + "battle.png", MerchantStyle))
            // --- 火堆：同一张立绘下移+放大，让裙摆/腿部落在木头上 ---
            .RestSite(cues => cues
                .Single("overgrowth_loop", AssetDir + "battle.png", RestSiteStyle)
                .Single("hive_loop", AssetDir + "battle.png", RestSiteStyle)
                .Single("glory_loop", AssetDir + "battle.png", RestSiteStyle))
            .Build();

    // ---------- 能量球：saint_energy_counter.tscn（见上方 CustomEnergyCounterPath 注释）；
    // 数字描边深棕=LightswornEnergyCounterOutlinePatch（OutlineColor getter 补丁，保留）。 ----------
}
