// v0.5.0 RitsuLib 迁移：全局引入 RitsuLib 命名空间（各卡牌文件无需逐个加 using）
global using STS2RitsuLib.Interop.AutoRegistration;  // [RegisterCard]/[RegisterRelic]/[RegisterSharedEvent]/[RegisterArchaicToothTranscendence]/[RegisterPower]
global using STS2RitsuLib.Scaffolding.Content;       // ModCardTemplate/ModRelicTemplate/ModPowerTemplate/ModEventTemplate/TypeList*PoolModel/AssetProfile
global using STS2RitsuLib.Content;                   // ModContentRegistry
global using STS2RitsuLib.Keywords;                  // ModKeywordRegistry/ModKeywordCardDescriptionPlacement
global using STS2RitsuLib.CardTags;                  // ModCardTagRegistry
