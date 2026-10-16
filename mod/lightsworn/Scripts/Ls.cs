using MegaCrit.Sts2.Core.Entities.Cards;

namespace Lightsworn;

// 自定义标签与关键词（v0.5.0 RitsuLib 迁移：BaseLib 的 [CustomEnum] 特性 → ModCardTagRegistry/ModKeywordRegistry 铸造）
// ——在 Entry.Init 里调用 RegisterAll()，早于 ModelDb 初始化/RitsuLib 冻结。
public static class Ls
{
    public static CardTag Lightsworn;   // 光道
    public static CardTag EarthAngel;   // 地天使（现世与冥界）
    public static CardTag Fiendsmith;   // 刻魔
    public static CardTag Tearlaments;  // 珠泪哀歌族（捕食植物犀角龙不含珠泪字段，不打此标）
    public static CardTag Shaddoll;     // 影依（白名单见 ShaddollNamed，神影依Token同打此标）

    public static void RegisterTags()
    {
        ModCardTagRegistry registry = ModCardTagRegistry.For("lightsworn");
        Lightsworn = registry.RegisterOwned("LIGHTSWORN").CardTagValue;
        EarthAngel = registry.RegisterOwned("EARTH_ANGEL").CardTagValue;
        Fiendsmith = registry.RegisterOwned("FIENDSMITH").CardTagValue;
        Tearlaments = registry.RegisterOwned("TEARLAMENTS").CardTagValue;
        Shaddoll = registry.RegisterOwned("SHADDOLL").CardTagValue;
    }

    // 中文名含「光道」的卡（问题5：只有卡名里有光道的卡才标记为光道卡）
    public static readonly HashSet<string> LightswornNamed = new()
    {
        nameof(Aegis), nameof(Barrier), nameof(Celestia), nameof(Decree), nameof(Ehren),
        nameof(Felis), nameof(Garoth), nameof(Gragonith), nameof(Jain), nameof(Janice),
        nameof(Kiryu), nameof(Layden), nameof(LightswornDragon), nameof(Lumina), nameof(Lyla),
        nameof(MaidenMinerva), nameof(Michael), nameof(MinervaExalted), nameof(MinervaSaint),
        nameof(Orcus), nameof(Rinyan), nameof(Ryko), nameof(Sabre), nameof(Shire), nameof(TwilightJain),
        nameof(TwilightLumina), nameof(TwilightLyla), nameof(TwilightRyko), nameof(Weiss), nameof(Wulf),
    };

    // 影依系列白名单（问题5：只有中文名含「影依」的卡才算影依卡，且是唯一判定来源——
    // ShaddollCard/ShaddollToken 基类不再直接打标。炼狱的乖放/堕影的蠢动/影牢之咒缚卡名不带影依，
    // 不入名单：不作影融素材、不被检索、被弃置不计咒缚/影文蒂联动，自身的「被弃置时」效果不受影响。
    // 订正名（蛇影依/圣影依/羽影依/虚影依/神影依融合/魂影依融合/心影依融合/联结之影依化身/
    // 神我影依流世/翼影依）写作xx读作xx全带影依）
    public static readonly HashSet<string> ShaddollNamed = new()
    {
        nameof(ShaddollBeast), nameof(ShaddollDragon), nameof(ShaddollSquamata), nameof(ShaddollHedgehog),
        nameof(ShaddollFalco), nameof(ShaddollHound), nameof(NaelshaddollAriel), nameof(NehshaddollGenius),
        nameof(QadshaddollKeios), nameof(ReeshaddollWendi), nameof(HelshaddollHollow), nameof(TohushaddollGrysta),
        nameof(ShaddollConstruct), nameof(ShaddollZefranaga), nameof(ShaddollZefracore),
        nameof(ShaddollFusion), nameof(ElShaddollFusion), nameof(NepheShaddollFusion), nameof(FrozenHeartShadow),
        nameof(ShaddollCore), nameof(ShaddollSchism), nameof(ReshShaddollIncarnation), nameof(PurushaddollAeon),
        nameof(ElShaddollWinda), nameof(ElShaddollConstruct), nameof(ElShaddollWendigo), nameof(ElShaddollGrysta),
        nameof(ElShaddollShekhinaga), nameof(ElShaddollAnoyatyllis), nameof(ElShaddollApkallone),
        nameof(ElShaddollMeshahrail), nameof(ReeshaddollWendikurhu),
    };
}

// 自定义关键词：弃光 / 除光 / 暮光 / 珠泪融合 / 影融
// v0.5.0：RitsuLib 铸造真实 CardKeyword 值（存档/克隆/原版查询全兼容）。
// loc 键=`LIGHTSWORN_KEYWORD_{STEM}.title/.description`（card_keywords 表）。
//
// ⚠ v0.5.4 用户订正（关键词不再作为独立词条行，改为正文内联着色）：
//   用户点名的目标观感=「[gold]弃光[/gold]3。目标敌人获得1层虚弱和1层易伤。」——
//   即机制名与数值写在正文里、**卡面没有独立的词条行**。官方范式实证（未掘宝石 HIDDEN_GEM）：
//     正文 `获得{Replay:diff()}层[gold]重放[/gold]`；官方 `CardKeyword` 枚举里**根本没有 Replay**
//     （只有 None/Exhaust/Ethereal/Innate/Unplayable/Retain/Sly/Eternal）——它是靠
//     「正文内联 + HoverTipFactory.Static(StaticHoverTip.ReplayStatic) 悬浮提示」实现的，
//     两个机制名（重放/君王之剑的 SwordSage）都**没有词条行**。
//   据此把 MILL/BANISH/TWILIGHT 三个机制从 BeforeCardDescription 改为 None：
//     · 卡面不再注入 `[gold]弃光[/gold]。` 词条行（消除"同一机制在卡面出现两次"）；
//     · 悬浮提示**自动**出（原版 `CardModel.HoverTips` 遍历 Keywords → `HoverTipFactory.FromKeyword`
//       → RitsuLib 路由到 ModKeywordRegistry 提示），**不要手挂**（详见 LightswornContent.cs LsCard 注释）；
//     · 正文由本地化负责写成 `[gold]弃光[/gold]{Mill:diff()}` 形式（LocString 的 [gold] 是
//       官方惯用的"语义指代/术语强调"用法，与 `[gold]抽牌堆[/gold]` 同类，**不影响数值渲染**）。
//   TEARFUSION/SHADDOLLFUSION 保持 BeforeCardDescription：**不是**因为"长篇机制说明"（那是误解——
//   placement 注入的是"金色标题+句号"的短行，长说明在悬浮提示里），而是因为有 11 张卡
//   （真血公/手札抹杀/愚蠢的埋葬/影依猎犬/影依巫女/路径灵/文蒂/虚梦狱/乖放/心影依融合）
//   **正文没有内联机制名**，词条行是它们唯一的卡面标记（审计=`tools\audit_fusion_inline.py`）。
//   Exhaust 由引擎自动追加（CardKeywordOrder.afterDescription），不受本处改动影响。
public static class LsKeywords
{
    public static CardKeyword Mill;                // 弃光N：从抽牌堆顶部将N张牌弃置
    public static CardKeyword Banish;              // 除光N：从抽牌堆中选择N张牌消耗
    public static CardKeyword Twilight;            // 暮光：弃光不够时耗2层洗回弃牌堆并补完
    public static CardKeyword TearFusion;          // 珠泪融合：被弃置时发动（选弃牌堆素材回卡组→融合卡入手）
    public static CardKeyword ShaddollFusion;      // 影融：弃手牌素材→生成神影依入手牌（影依系列机制）

    public static void RegisterAll()
    {
        ModKeywordRegistry registry = ModKeywordRegistry.For("lightsworn");
        // v0.5.4：正文内联式（不注入词条行）——弃光/除光/暮光
        Mill = Register(registry, "MILL", ModKeywordCardDescriptionPlacement.None);
        Banish = Register(registry, "BANISH", ModKeywordCardDescriptionPlacement.None);
        Twilight = Register(registry, "TWILIGHT", ModKeywordCardDescriptionPlacement.None);
        // 保留词条行：这些卡正文没有内联机制名，行是唯一卡面标记（见上）
        TearFusion = Register(registry, "TEARFUSION", ModKeywordCardDescriptionPlacement.BeforeCardDescription);
        ShaddollFusion = Register(registry, "SHADDOLLFUSION", ModKeywordCardDescriptionPlacement.BeforeCardDescription);
    }

    private static CardKeyword Register(ModKeywordRegistry registry, string stem,
        ModKeywordCardDescriptionPlacement placement)
        => registry.RegisterCardKeywordOwnedByLocNamespace(stem, iconPath: null,
            placement, includeInCardHoverTip: true).CardKeywordValue;
}
