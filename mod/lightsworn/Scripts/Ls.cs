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
// loc 键=`LIGHTSWORN_KEYWORD_{STEM}.title/.description`（card_keywords 表）；BeforeCardDescription ≈
// BaseLib 的 [KeywordProperties(AutoKeywordPosition.Before)]（关键词行自动插到卡面描述前）。
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
        Mill = Register(registry, "MILL");
        Banish = Register(registry, "BANISH");
        Twilight = Register(registry, "TWILIGHT");
        TearFusion = Register(registry, "TEARFUSION");
        ShaddollFusion = Register(registry, "SHADDOLLFUSION");
    }

    private static CardKeyword Register(ModKeywordRegistry registry, string stem)
        => registry.RegisterCardKeywordOwnedByLocNamespace(stem, iconPath: null,
            ModKeywordCardDescriptionPlacement.BeforeCardDescription, includeInCardHoverTip: true).CardKeywordValue;
}
