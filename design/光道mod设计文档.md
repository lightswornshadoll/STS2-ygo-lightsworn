# 杀戮尖塔2 mod《光道》设计文档 v1.1

> v1.1（mod v0.3.0）：根据首轮试玩反馈调整——修复选取bug（改用MultiPileCardSelect，选择界面只显示候选牌）；白雪重做为本体+雪之化身令牌；裁决/惩戒之龙改0费条件打出（墓地≥4种光道，同华丽收场机制）；沃尔夫/费莉丝改0费"非抽牌入手才能打出+被弃光自动跳进手牌"；光道细剑增加被弃光自动入手且当回合0费。

> 主题：游戏王「光道（ライトロード / Lightsworn）」 archetype
>   
> 平台：杀戮尖塔2（Slay the Spire 2，v0.107.1，Godot 4.5.1 Mono）
>   
> 基础库：BaseLib v3.4.7
>   
> mod形式：新增角色「光道召唤师」+ 专属卡池（占位人物模型，使用原版资源兜底）

## 一、机制映射总则

| 游戏王           | 杀戮尖塔2     | 说明                                                |
| ------------- | --------- | ------------------------------------------------- |
| 卡组            | 抽牌堆       | —                                                 |
| 墓地            | 弃牌堆       | 弃牌堆循环洗回抽牌堆（尖塔规则），所以「堆墓」在尖塔里是**加速循环、喂养墓地收益**，越堆越强  |
| 除外            | 消耗堆       | 「除外」=将卡牌移入消耗堆。本mod描述里统一写「消耗」，消耗即除外                |
| 上级召唤/同调/超量/连接 | 高费稀有卡     | 本家怪兽按星级映射费用：1~~4星→0~~1费，5~~6星→1~~2费，同调/超量/连接→2~3费 |
| 攻击力           | 伤害        | 约 700 ATK ≈ 9 伤害                                  |
| 结束阶段堆墓        | 卡牌效果的「弃光」 | 打出即结算，不再按回合                                       |

### 自定义关键词

- **弃光 N**：从抽牌堆顶部将 N 张牌弃置。这是光道的灵魂机制：弃掉的牌进入弃牌堆（墓地），成为各种收益的燃料。
- **消耗（除外）**：将一张牌移入消耗堆。「消耗弃牌堆中的1张牌」即"除外墓地里的卡"，那场战斗中它不会再回来。
- **「光道」**：本家43张共有的标签（tag）。能力与卡牌效果里"打出/弃置「光道」牌"都以此判定。
- **「地天使」**：现世与冥界四件套（阿基多/凯尔柏克/凯尔多/姆多拉）的标签。
- **「刻魔」**：刻魔系列卡的标签。
- **暮光**：暮光道萨满给予的可叠加能力，见卡片设计。

> 弃牌堆=墓地的深意：尖塔2里弃牌堆不会消失、会重新洗回抽牌堆，所以**弃光是赚不是亏**；真正的代价（真正让牌离场）用「消耗」承担，这正是暮光道系列的"除外"玩法。堆墓轴的强度以「卡组里光道浓度」和「墓地收益卡的稀有度」来平衡。

## 二、初始卡组（10张）

| 卡名   | 类型 | 费用 | 效果                             | 升级    |
| ---- | -- | -- | ------------------------------ | ----- |
| 光刃×5 | 攻击 | 1  | 造成6点伤害。                        | +3    |
| 光盾×4 | 技能 | 1  | 获得5点格挡。                        | +3    |
| 光之援军 | 技能 | 1  | **从抽牌堆**将1张「光道」牌加入手牌（本回合费用为0）。 | 费用1→0 |

## 三、本家43张

### 怪兽（26张）

**通用（Common）**

1. **光道猎犬 雷光**（Ryko，反转：破坏1张卡+堆3）
     
   技能 1费：**弃光3**。移除目标敌人的1个随机增益。
     
   ＋：改为移除2个随机增益。
2. **光道圣骑士 简**（Jain，战斗时+300攻+堆2）
     
   攻击 1费：造成9点伤害。**弃光2**。
     
   ＋：+4伤害。
3. **光道魔术师 丽拉**（Lyla，破坏魔陷+堆3）
     
   技能 1费：**弃光3**。抽1张牌。
     
   ＋：抽2张牌。
4. **光道武僧 艾琳**（Ehren，弹回守备怪兽+堆3）
     
   攻击 1费：造成6点伤害。**弃光3**。若弃置的牌中有「光道」牌，抽1张牌。
     
   ＋：+4伤害。
5. **光道兽 沃尔夫**（Wulf，被堆墓即免费上场的大打点）
     
   攻击 1费：造成12点伤害。**弃光3**。
     
   ＋：+4伤害。
6. **光道之龙**（新支援龙，墓地有光道就强化）
     
   攻击 1费：造成9点伤害。**弃光3**。若弃牌堆中存在「光道」牌，此牌伤害+3。
     
   ＋：+4伤害（含加成的+3→+7）。
7. **光道祭司 珍妮丝**（光道被堆墓的回合回血奶）
     
   技能 1费：**弃光3**。每弃置1张「光道」牌，回复3点生命。
     
   ＋：改为回复4点。
8. **光道防护罩**（堆2无效一次攻击）
     
   技能 1费：**弃光2**。获得10点格挡。
     
   ＋：+3格挡。
9. **光道贼猫 雷喵**（反转：墓地光道回卡组+抽1）
     
   技能 1费：将弃牌堆中最多2张「光道」牌洗回抽牌堆，抽1张牌。
     
   ＋：改为最多3张。
10. **光道暗杀者 莱登**（Link4，堆2+光道则加攻）
      
    攻击 1费：造成8点伤害。**弃光2**。若弃置了「光道」牌，此牌伤害+4。
      
    ＋：+4伤害。
11. **光道弓手 费莉丝**（被堆墓自动上场；解放点杀+堆3）
      
    攻击 1费：造成8点伤害。**弃光3**。若弃置了「光道」牌，再造成6点伤害。
      
    ＋：+4伤害。

**非通用（Uncommon）**

1. **光道战士 加洛斯**（Garoth，其他光道堆墓时跟进堆2并补牌）
     
   能力 2费：每当你打出其他「光道」牌，**弃光2**。
     
   ＋：弃光2→3。
2. **光道召唤师 露米娜丝**（Lumina，丢1复活光道；核心引擎）→ 稀有（见下）
3. **光道天使 塞勒斯特 基路伯**（Celestia，解放→堆4炸2）
     
   攻击 2费：对目标造成12点伤害，对所有其他敌人造成6点伤害。**弃光4**。
     
   ＋：16 / 9。
4. **光道龙 格拉古尼斯**（Gragonith，墓地光道种类×300攻）
     
   攻击 2费：造成14点伤害，弃牌堆中每有1张「光道」牌额外+2点。**弃光3**。
     
   ＋：基础14→18。
5. **光道圣灵 夏尔**（Shire，墓地光道×300攻的守壁）
     
   技能 1费：获得10点格挡，弃牌堆中每有1张「光道」牌额外+1点。
     
   ＋：基础10→14。
6. **光道德鲁伊 奥库斯**（Orcus，保护光道的结界兽）
     
   能力 2费：每回合开始时，**弃光2**并获得6点格挡。
     
   ＋：改为8点格挡。
7. **光道恶魔 魏丝**（Weiss，手卡光道回卡组顶特招）
     
   技能 1费：将手牌中最多2张「光道」牌洗回抽牌堆，然后抽2张牌。
     
   ＋：抽2→3。
8. **光道少女 密涅瓦**（Link3少女，检索龙族）
     
   技能 1费：将抽牌堆中1张「光道」牌加入手牌。**弃光2**。
     
   ＋：弃光2→3。
9. **暮光道斗犬 雷光**（除1光道→除外场上1卡）
     
   技能 1费：**消耗弃牌堆中的1张「光道」牌**。移除目标敌人2个随机增益。
     
   ＋：改为3个。
10. **暮光道巫师 丽拉**（除1光道→破坏魔陷）
      
    技能 1费：**消耗弃牌堆中的1张「光道」牌**。抽2张牌。
      
    ＋：抽2→3。
11. **暮光道将军 简**（除1光道→降攻降守）
      
    攻击 1费：**消耗弃牌堆中的1张「光道」牌**。造成16点伤害。
      
    ＋：+6伤害。
12. **光道宰制者 基里奥斯**（Link3，连接成功堆1卡；离开时回收）
      
    攻击 2费：造成20点伤害。**弃光3**。将弃置的1张「光道」牌加入手牌。
      
    ＋：+4伤害。
13. **光道的裁决**（被光道堆墓时检索裁决之龙）
      
    技能 1费：**弃光3**。将「裁决之龙」加入手牌（从抽牌堆或弃牌堆找，找不到则抽1张牌）。
      
    ＋：弃光3→4。

### 稀有（Rare）

1. **光道召唤师 露米娜丝**（Lumina，光道引擎本体）
     
   技能 1费：**弃光3**。将弃牌堆中1张「光道」牌加入手牌，其费用在本回合内变为0。
     
   ＋：改为将2张加入手牌（均变为0费）。
2. **暮光道萨满 露米娜丝**（Twilight Lumina，**按用户指定设计**）
     
   技能 1费：**消耗弃牌堆中的1张「光道」牌**，将消耗堆中的1张「光道」牌加入手牌，其费用变为0。获得1层**暮光**。
     
   能力「暮光」（可叠加）：当你打出「光道」牌时，**弃光3**，然后层数-1。
     
   ＋：获得2层暮光。
3. **光道主·大天使 米迦勒**（同调7，支付1000除外场上1卡）
     
   攻击 2费：造成24点伤害。**消耗弃牌堆中的1张「光道」牌**。
     
   ＋：+8伤害。
4. **光道雅典娜 密涅瓦**（同调8，按同调素材数量堆墓；除外墓地光道→等量堆墓）
     
   能力 3费：每回合开始时，**弃光4**，每弃置1张「光道」牌抽1张牌。
     
   ＋：弃光4→6。
5. **光道圣女 密涅瓦**（超量4，取素材堆3，堆到光道就抽等量）
     
   技能 1费：**弃光3**，每弃置1张「光道」牌抽1张牌。
     
   ＋：弃光3→4。
6. **裁决之龙**（3000打点核弹，烧1000清场）
     
   攻击 3费：对所有敌人造成26点伤害。**弃光4**。
     
   ＋：+8伤害。
7. **惩戒之龙**（除外4种以上才能召唤；双方墓地全部回卡组）
     
   攻击 2费：**消耗弃牌堆中最多4张牌**，每消耗1张，对所有敌人造成5点伤害。
     
   ＋：每张7点。

### 魔法·陷阱（本家，5张）

1. **光道的神域**（场地：丢光道→回收；光指示物保护）
     
   能力 2费：每回合开始时，**弃光2**，并从弃牌堆将1张「光道」牌洗回抽牌堆。
     
   ＋：改为洗回2张。
2. **光道细剑**（装备+700；被堆墓时自动装备）
     
   技能 1费：本回合你打出的攻击牌伤害+4。**弃光2**。
     
   ＋：+4→6。
3. **光道埃癸斯盾**（按场上光道数无效对方效果）
     
   能力 2费：每当你打出「光道」牌，获得4点格挡。
     
   ＋：4→6。
4. **光之援军**（堆3检索4星以下光道）
     
   技能 1费：**弃光3**。若其中有「光道」牌，将其中1张加入手牌。
     
   ＋：弃光3→4。
5. **太阳交换**（丢光道抽2+堆2）
     
   技能 1费：将手牌中1张「光道」牌弃置。抽2张牌。**弃光2**。
     
   ＋：抽2→3。
6. **暗之进军**（墓地光道回手，再按等级除外卡组顶）
     
   技能 1费：将弃牌堆中1张「光道」牌加入手牌。**弃光2**。
     
   ＋：该牌本回合费用变为0。
7. **正义世界**（场地，堆墓就叠光指示物加攻）
     
   能力 1费：每当你弃置1张「光道」牌，获得1点格挡（每回合至多6次）。
     
   ＋：上限6→10。
8. **光之回弹**（光道堆墓→除外对方卡组）
     
   能力 2费：每当你弃置1张「光道」牌，获得1点力量（每回合至多5次）。
     
   ＋：上限5→8。
9. **黄昏之抹杀**（除外墓地2光道→除外场上2卡）
     
   技能 1费：**消耗弃牌堆中的2张「光道」牌**。移除目标敌人的2个随机增益，抽1张牌。
     
   ＋：改为3个增益。
10. **黄昏之交衣**（除外墓地光道→加攻加守）
      
    技能 1费：**消耗弃牌堆中任意数量的「光道」牌**，每消耗1张获得3点格挡。
      
    ＋：3→4。
11. **闪光之幻想**（墓地光道特招）
      
    技能 1费：将弃牌堆中1张「光道」牌置于抽牌堆顶。**弃光2**。
      
    ＋：弃光2→3。
12. **黄昏之双龙**（裁决/惩戒双检索）
      
    技能 1费：**弃光3**。将弃牌堆中1张「裁决之龙」或「惩戒之龙」加入手牌（没有则抽1张牌）。
      
    ＋：该牌本回合费用变为0。

> 注：光之援军/太阳交换等支援卡在游戏王里不属于「光道」字段，但本mod里43张全部打上「光道」标签（它们都被光道构筑使用，且都围绕堆墓），符合用户"本家43张"的定义。

## 四、非本家卡（12张）

### 地天使·现世与冥界四件套（标签「地天使」）

1. **古卫兵 阿基多**（对方墓地动→自特招；被堆墓→双方各堆5）
     
   技能 1费：**弃光5**。若其中有「光道」牌，抽1张牌。
     
   ＋：弃光5→7。
2. **古尖兵 凯尔柏克**（被堆墓→双方各堆5，可盖陷阱）
     
   技能 1费：**弃光5**。若其中有「光道」牌，获得8点格挡。
     
   ＋：弃光5→7。
3. **宿神像 凯尔多**（丢地天使→自特招检索现冥；除外自己→洗回墓地）
     
   技能 0费：将弃牌堆中1张「光道」牌洗回抽牌堆，抽1张牌。
     
   ＋：改为2张。
4. **剑神官 姆多拉**（丢地天使→自特招盖陷阱）
     
   攻击 1费：造成9点伤害。**弃光3**。若弃置了「地天使」牌，此牌伤害+5。
     
   ＋：+4伤害。

### 其他常用外挂

1. **妖精传姬-白雪**（除外7张→墓地复活；反制怪兽）
     
   技能 1费：**消耗弃牌堆中的3张牌**（任意牌）。造成10点伤害。
     
   ＋：+4伤害。
2. **邻家割草**（把卡组堆到和对方一样多）
     
   技能 1费：**弃光**（抽牌堆牌数的一半，向下取整）。
     
   ＋：改为弃光后抽1张牌。
3. **欧尼斯特**（光属性战斗要塞，老光道必带）
     
   技能 0费（消耗）：本回合你的下一次攻击伤害翻倍。
     
   ＋：改为下两次攻击。

### 刻魔系列（标签「刻魔」）

1. **刻印群魔的刻魔锻冶师**（丢自己→检索刻魔魔陷）
     
   技能 1费：**弃光2**。将弃牌堆中1张「刻魔」牌加入手牌。
     
   ＋：弃光2→3。
2. **刻魔 落泪之日**（融合怪兽，登场回收+烧1200）
     
   攻击 1费：造成8点伤害。**消耗弃牌堆中的1张「刻魔」牌**（若有），此牌伤害+8。
     
   ＋：+4伤害。
3. **刻魔的咏圣**（检索刻魔→丢1张手卡）
     
   技能 1费：将抽牌堆中1张「刻魔」牌加入手牌，然后弃置1张手牌（任意）。
     
   ＋：改为从抽牌堆或弃牌堆中找。
4. **刻魔的镇魂棺**（自解放→特招刻魔+装备+600）
     
   技能 1费：**消耗弃牌堆中的1张「刻魔」牌**（若有）。本回合获得4点力量。
     
   ＋：4→6。
5. **刻魔的怜歌**（战斗保护；除外墓地→融合）
     
   技能 1费：**消耗弃牌堆中的2张牌**（任意牌）。获得10点格挡。
     
   ＋：+4格挡。

## 五、稀有度分布

- 通用（Common）15张：雷光、圣骑士简、魔术师丽拉、武僧艾琳、沃尔夫、光道之龙、珍妮丝、防护罩、贼猫雷喵、暗杀者莱登、弓手费莉丝、光之援军、太阳交换、闪光之幻想、宿神像凯尔多、欧尼斯特、刻魔的咏圣、刻魔的怜歌（+初始光刃/光盾/光之援军）
- 非通用（Uncommon）17张：加洛斯、基路伯、格拉古尼斯、夏尔、奥库斯、魏丝、少女密涅瓦、暮雷光、暮丽拉、暮简、基里奥斯、光道的裁决、埃癸斯盾、暗之进军、正义世界、黄昏之抹杀、黄昏之交衣、黄昏之双龙、阿基多、凯尔柏克、剑神官姆多拉、妖精传姬白雪、邻家割草、刻魔锻冶师、落泪之日、镇魂棺
- 稀有（Rare）9张：露米娜丝、暮萨满、米迦勒、雅典娜密涅瓦、圣女密涅瓦、裁决之龙、惩戒之龙、神域、光之回弹

## 六、平衡设计说明

1. **弃光是收益引擎，不是代价**：尖塔里弃牌堆会洗回抽牌堆，弃光本质是"定向过滤+喂养墓地收益"。强度阀门：光道浓度（55张里~70%是光道tag）与墓地收益卡的稀有度。
2. **消耗（除外）是真正代价**：暮光道/黄昏系列/惩戒之龙把墓地燃料烧成即战力，烧掉的就没了——与堆墓轴形成"存 vs 烧"的资源张力。
3. **单卡数值对齐原版**：1费普通攻击≈9~~12（打击6、原版普通攻击卡8~~12），2费≈16~~24，3费≈26+；格挡1费≈8~~12。与尖塔2首发数值（打击/防御体系）同档。
4. **每回合触发类能力都设上限或资源门**（正义世界≤6/回合、光之回弹≤5/回合、雅典娜密涅瓦固定弃光4），避免无上限滚雪球。
5. **暮光**严格按用户指定：打出光道牌→弃光3→层数-1；提供"自动堆墓"的节奏引擎，层数用尽即消失。

## 七、实现备注（开发用）

### 实现版与设计的少量差异（以游戏内实际为准）

- 欧尼斯特：实现为"下一次攻击伤害翻倍"（更贴近原卡），升级为两次。
- 光之放逐：额外附加虚弱层数（2/升级3）。
- 白雪：伤害=4+2×消耗牌数（最多3张，即最高10，升级基础+4）。
- 刻魔的怜歌：格挡=4+3×消耗牌数（最多2张，升级6+4×）。
- 黄昏之交衣：自动消耗最多4张（无选取界面）。
- 暮光道萨满的"暮光"严格按指定设计实现。
- 人物名本地化经 `characters.json` 注入；遗物轮廓图复用主图。


### 开发环境

- 工程目录：`mod\lightsworn\`（Godot.NET.Sdk 4.5.1 / net9.0）
- .NET SDK 9：`tools\dotnet`（用户级安装）；Godot 4.5.1 Mono：`research\Godot_v4.5.1-stable_mono_win64`
- BaseLib：编译引用Steam工坊版3.3.0（与运行时一致，避免程序集版本混载）
- 卡图：YGOPRODeck `images/cards_cropped`（624×624）居中裁剪为250×190
- 反编译参考：`research\sts2src`（ILSpy导出的sts2.dll源码，v0.107.1）
- 注意：本机沙箱对 D:\Program Files 的写入对其他进程有延迟可见性，部署mod文件务必使用无沙箱模式（robocopy）后重启游戏。

> v1.2（mod v0.3.1）：第二轮试玩反馈调整——神域改为回合开始可选发动（弃1张手牌光道→从弃牌堆拿光道，升级拿2张）；光之援军改为从抽牌堆检索（升级0费）；沃尔夫去掉弃光3（伤害12→18，升级+6）；光道之龙改为条件选弃工具+被弃置时检索裁决/惩戒之龙；魏丝改为弃光2+手牌光道压卡组顶（被弃置时回收其他光道并临时0费，升级回2张）；少女密涅瓦改0费、按弃牌堆光道种类阶梯检索龙（4/6/8种→之龙/格拉古尼斯/裁决之龙，升级阈值-1，被弃置时追加弃光1）；艾琳增加对格挡目标的特化（无伤害清全部格挡+自身回卡组顶）。
>   
> v1.3（mod v0.3.2，按用户"已知问题"清单修复）：修复雷光/暮雷光移除敌方增益时的NRE死锁（原代码用creature.Player取RNG，敌人身上为null，改用玩家RunState）；**修复标签体系缺失bug**——此前仅光刃/光盾/雪之化身带「光道」标签，其余40张全没打标（选择器只见初始牌的根因），现按问题5规则重做：仅中文名含「光道」的29张卡自动带标（LsCard.Tags重写+Ls.LightswornNamed白名单）；光刃/光盾改CardRarity.Basic（不进战斗选牌奖励、不带光道标）；加洛斯能力改为"光道牌弃光后弃光2"（LsUtil.Mill卡牌来源统一触发，强化版GarothPowerPlus追加按光道数抽牌，圣徽弃光不触发）；少女密涅瓦改为从已达挡位的龙中自选；光道之龙加回9点伤害且弃置来源扩为手牌+抽牌堆；露米娜丝追加丢弃1张手牌+从弃牌堆拿任意牌变0费；费莉丝(守2000>攻1100)与姆多拉(守1800>攻1500)伤害转格挡；艾琳去掉回牌堆顶；雷光/雷喵升级改0费；魏丝改为先回卡组顶再弃光2；援军加弃光3、检索源扩为卡组+弃牌堆。

> v1.4（mod v0.3.3，第四轮反馈25条，design\已知问题.txt）：初始牌组打击5→4+加入光道暗杀者莱登；**删除刻魔系列5张**（锻冶师/落泪之日/咏圣/镇魂棺/怜歌及孤儿能力，卡池52张）；艾琳去掉抽卡；光道之龙升级改+4伤害（9→13）；费莉丝去掉弃光道加格挡、基础格挡8→10、新增随机敌人1层易伤；珍妮丝改为能力牌「光道祭司」（本回合发动过弃光→回合结束回Amount血+对随机敌人Amount伤害，5/敲后8，JanicePower由LsUtil.Mill通知计数）；丽拉抽牌改目标敌人-1力-1敏（敲后-2-2，目标Self→AnyEnemy）；闪光之幻想改从弃牌堆拿1张光道当回合0费+弃光2（敲后3）；太阳交换敲后0费；基里奥斯新增从卡组弃1张（LsUtil.MillSelected）+墓地拿卡不限光道；光道的裁决改0费置于抽牌堆顶+被从卡组弃置时生成虚无·消耗的裁决之龙Token（敲后2张，LsUtil.CreateToken）；奥库斯改1费技能弃光2+1层人工制品（敲弃光3，OrcusPower删除）；**新增关键词除光**（抽牌堆顶N张消耗，LsUtil.Banish/LsKeywords.Banish，不触发加洛斯/弃光钩子），暗之进军弃光全部改除光；黄昏之抹杀去抽牌+被光道卡从卡组弃掉时随机1张（敲2张）手牌光道0费（LsCard.OnMilledByLsCard钩子）；黄昏之双龙重做（手牌有惩戒之龙→弃牌堆拿裁决之龙+弃光4，否则生成虚无裁决/惩戒Token；被光道卡弃掉→拿惩戒之龙+除光4，敲后除光6）；暮光道斗犬消除buff改1+1层暮光（敲0费）；暮光道巫师改消耗弃牌堆1张光道→目标-1力-1敏+1层暮光（敲-2-2，目标Self→AnyEnemy）；正义世界重做（牌从抽牌堆弃到弃牌堆+1光指示物，攻击伤害时消耗全部每层+1，ModifyDamageAdditive+AfterAttack SetAmount(0)，敲后固有）；埃癸斯盾改1费（敲后AegisPower量+1）；光之回弹改1费重做（每次弃牌→所有敌人各+等同弃牌数的**灾厄**=原版死灵法师DoomPower，不筛光道无上限）；裁决之龙条件改弃牌堆4种不同光道（DistinctLsInDiscard）；米迦勒去掉消耗光道→弃牌堆光道全部洗回卡组每张3格挡；雅典娜改攻击牌（弃2张不同名光道+可选消耗墓地光道≤4张x→弃光x+9伤害，敲+5=14）；露米娜丝拿牌限光道（敲0费）；圣女加敌人意图为攻击时再弃光3、每张光道给1层虚弱。

> v1.5（mod v0.4.0，自定义角色形象）：新增独立角色视觉「光道圣女」，替换原铁甲战士占位模型。技术路线：BaseLib CustomCharacterModel 全套 Custom* 路径接线；战斗/商人/休息处骨骼复用原版 Silent（女性体型，Spine 4.2.43），贴图用 tools\make_saint_assets.py 按部件重上色（绿袍→白袍/绷带→米白/白发→橙金发/深肤→浅肤/青匕首→金光刃/兽骨徽记→白金圣徽），spatlas(JSON) 的 source_path 改指本 mod、页贴图按「目录+页名」解析到重上色 PNG；商人/休息处用纯核心节点脚手架场景 + NodeFactory.RegisterSceneType 转换后注入运行时构建的 SpineSprite（避免编辑器导 pck 需要 spine 扩展）；能量球/卡牌拖尾/选人转场/地图标记复用原版黄金角色 Regent 资源；选人图标/顶栏图标用重上色立绘，选人背景用本地 ygopro 高清「光道圣女 密涅瓦」(30100551) 卡图金化合成；音效/多人手势沿用 Silent（女声）。角色名改为「光道圣女」。版本 0.3.3→0.4.0。

> v1.6（mod v0.4.1，回滚）：按用户要求把角色形象**回滚为默认铁甲战士占位**（v0.4.0 的「光道圣女」自定义形象移除），角色名恢复「光道召唤师」，pck 中圣女资源（visuals/、images/character/）已删除，export include_filter 回退。原因：用户主动要求回退（视觉效果未达预期）。**方案与素材管线完整保留备查**：贴图重上色生成器 tools\make_saint_assets.py、pck 解包器 tools\pck.py、研究材料 research\pck_dump、开发手册 §5「角色外观」（运行时 Spine 注入做法）均未删除，随时可恢复或改造成豆包分层素材+自建骨骼的新方案。版本 0.4.0→0.4.1。
>   
> v1.7（mod v0.4.2，第五轮反馈4条，design\已知问题.txt）：①光之援军检索源改回只从卡组（LsUtil.PickFromDraw，符合原版「增援部队」效果）；②**修复光道细剑不触发「光道的甲铠」**——Ls.LightswornNamed 白名单漏了 nameof(Sabre)，补上（光道卡 29→30 张），带标后 AegisPower 判定生效；③金卡强度调整（AI拍板，未降稀有度）：露米娜丝拿取数 1→2（升级仍0费）、暮光道萨满露米娜丝暮光 1/2→2/3（改 {Twilight:diff()} 变量）；④光之回弹重做为按**弃牌次数**触发：每次弃牌事件对所有敌人施加固定2层灾厄（敲后3，{Doom:diff()}），不再按张数计——LightBouncePower 用 ActionExecutor.CurrentlyRunningAction 做「同一次结算只触发1次」批处理（无动作环境时按回合同侧兜底键），Amount=每次弃牌的灾厄层数，多张叠加。版本 0.4.1→0.4.2。
>   
> v1.7（mod v0.4.3，按用户第六轮"已知问题"9条修复）：①修复第三层boss后见建筑师无对话卡住——根因是Architect事件只认角色专属对话（AgnosticDialogues为空+allowAnyCharacterDialogues:false），mod角色无对话时NextItem(空列表)异常；新增本地化zhs/ancients.json（THE_ARCHITECT.talk.LIGHTSWORN-LIGHTSWORN_CHARACTER.0-*-r键，BaseLib AddAncientDialogues patch在PopulateLocKeys时自动挂载，日志已确认"Found 1 additional dialogues"）。②小龙重做：0费；弃置对象只从抽牌堆选（走MillSelected触发弃光钩子+加洛斯）；检索双龙条件从"仅从卡组被弃置"扩为任意弃置（AfterCardChangedPiles管弃光+新增AfterCardDiscarded管手牌弃置/窥探，打出不走该钩子不会误触发）。③神域2费→1费。④雅典娜3费→2费，伤害9→18（敲后23）。⑤惩戒之龙重做：打出条件改为消耗堆4种以上光道（新增LsUtil.DistinctLsInExhaust）；效果改为将弃牌堆+消耗堆所有非光道卡返回卡组、每有一张全体敌人随机1层负面状态（新LsUtil.ApplyRandomDebuffs：易伤/虚弱/脆弱/中毒/灾厄五选一，玩家侧RNG，均为PowerType.Debuff故人工制品可抵挡），伤害26+暮光1，敲后34。⑥雪之化身追加18伤害（改Attack/AnyEnemy，先伤害后消耗7张）。⑦光刃/光盾改名打击/防御并打CardTag.Strike/Defend标签（IsBasicStrikeOrDefend判定、打击/防御联动类遗物事件生效）。⑧8个自定义能力图标改为对应卡牌卡图中心裁圆（tools\make_power_icons.py，64/256两档）。⑨细剑{nosp}占位符修复——{TempStr}不是注册动态变量，改用PowerVar<SabrePower>（var名=类名，同原版SetupStrike的{StrengthPower}写法），描述同步{SabrePower:diff()}。
>   
> v1.8（mod v0.4.4，卡牌图鉴核对发现的5处文案/预览问题修复）：①凯尔多：强化后洗回2张此前文案未体现——新增 Picks 动态变量（1→2），描述改 {Picks:diff()}，升级预览与文案自动正确；②欧尼斯特：强化后翻倍2次此前文案未体现——新增 Times 动态变量（1→2），描述改"你的下{Times:diff()}次攻击伤害翻倍"；③邻家割草：强化后追加抽1张牌此前文案未体现——描述追加"强化后：追加抽1张牌。"（纯文案，代码原本就有）；④光之放逐：虚弱 2→3 原写在 OnPlay 内联（IsUpgraded?1:0），升级预览不显示——改为 OnUpgrade DynamicVars["Weak"].UpgradeValueBy(1)；⑤黄昏之交衣：每张格挡 3→4 同样内联——改为 OnUpgrade DynamicVars["BlockPerBurn"].UpgradeValueBy(1)。另新增 tools\gen_card_doc.py 卡牌图鉴生成器（解析Cards1-4.cs数值+OnUpgrade增量套cards.json文案 → design\卡牌图鉴.md，53张含基础/敲后双版本+升级变化摘要，内联升级卡在脚本 SPECIAL 表覆盖）。部署验证：v0.4.4 日志加载无异常。版本 0.4.3→0.4.4。

> v1.9（mod v0.4.5，第七轮"已知问题"9条）：①**修移除增益误删Boss专属能力导致暴毙**——沙虫TheInsatiable的SandpitPower（Buff型独有计数器）AfterRemoved直接处决玩家，LsUtil.StripBuffs/StripAllBuffs 现跳过一切重写了 PowerModel.AfterRemoved 的能力（反射判定；常规增益力量/金属化等均不重写它，Boss机制 Sandpit/Burrowed/Slumber/SwordSage/VitalSpark 全重写，精准排除）；②米迦勒按游戏王原卡效果重做：弃牌堆存在「光道」牌时才能打出（IsPlayable+金光，同小龙模式），效果改为回收弃牌堆**全部**卡（原只回收光道），每张3格挡保留，伤害24→20（敲26）；③打击/防御改名v0.4.3已做，本轮复核确认；④初始卡组改 4打击+4防御+1光道圣骑士简+1光道防护罩（原1莱登+1援军）；⑤弃光/除光/暮光**卡组不够时不再自动洗回弃牌堆**——LsUtil.Mill/Banish 移除 ShuffleIfNecessary，抽牌堆空即停（卡片来源/能力来源/圣徽全部生效），弃光关键词释义同步；⑥清除描述里"强化后xxx/敲后"硬文案，改用引擎原生 {IfUpgraded:show:升级后|基础}（UpgradePreview绿色高亮，CardModel.cs:1377自动注入变量；原版DARKNESS/ARMAMENTS同款），涉及加洛斯/暮雷光/暗之进军/割草/裁决/双龙/抹杀7张；⑦数值：防护罩10/13→8/12（敲+4）、裁决之龙26/34→22/28（敲+6）、惩戒之龙26/34→22/28（敲+6）、米迦勒24/32→20/26（敲+6）、沃尔夫18/24→12/16（敲+4）、费莉丝10/13→7/10；⑧光之援军去掉检索牌0费（删SetUntilPlayed(0)，升级仍费用-1）；⑨光道细剑+4/6临时力量改为获得**6/8点活力**（原版VigorPower，删SabrePower类），正义世界"光指示物增伤"整机制改为"每当有牌从抽牌堆弃到弃牌堆获得1点活力"（JusticeWorldPower只剩AfterCardChangedPiles一个钩子）。部署验证：v0.4.5 日志加载无异常。版本 0.4.4→0.4.5。

> v1.10（mod v0.4.6，用户对米迦勒效果的追注定稿）：撤销 v1.9② 的"回收全部卡+打出条件"解读，按用户拍板定稿：**无打出条件；打出先造成伤害，再回收弃牌堆中的「光道」牌（非光道不回收），每回收1张获得3点格挡**（即恢复 v0.4.5 之前"只回收光道"的行为，仅把结算顺序改为先伤害后回收）。伤害维持第七轮下调值 20/26（敲+6）。描述同步："造成{Damage:diff()}点伤害。将弃牌堆中的「光道」牌全部洗回抽牌堆，每洗回1张获得3点格挡。"。部署验证：v0.4.6 日志加载无异常。版本 0.4.5→0.4.6。

> v1.11（mod v0.4.8，第八轮反馈6条）：①**米迦勒"洗回全部卡"真根因修复**：前两轮过滤逻辑都是对的，真凶是回收后调用的 `CardPileCmd.Shuffle`——游戏源码注释明确其语义是"把玩家整个弃牌堆洗进抽牌堆"（打击/防御等非光道牌全被它洗回）。删除该调用，回收牌直接 Add 到抽牌堆底；描述"洗回"改"加入"，米迦勒判断逻辑不变（v0.4.6 定稿）；②珍妮丝：能力"回合结束回血N"改为"获得N点格挡"（JanicePower.BeforeSideTurnEnd Heal→GainBlock，文案同步）；③光道的裁决：被弃置时裁决之龙Token改加入**手牌**（原弃牌堆）；敲后从"2张"改为"1张**强化后的**裁决之龙"（Token 走 UpgradeInternal+FinalizeUpgradeInternal，参考 CardCmd.Upgrade 引擎实现；手牌满则不生成）；④**全部"移除敌方增益"效果按用户要求废除**（StripBuffs bug 多难修），改为施加对应层数的虚弱+易伤：雷光 1弱1易、暮雷光 1弱1易、黄昏之抹杀 每消耗1张=1弱1易；LsUtil.StripBuffs/StripAllBuffs/HasRemovalSideEffect 整体删除（v0.4.5 的 AfterRemoved 防护机制随之作废）；⑤光之放逐重做（问题3）：丢弃手牌中1张「光道」牌（自选，有则必选）+对目标施加虚弱2/敲后3，删除"移除所有增益"；⑥**新增卡 神光之龙 ShiningDragon**（稀有攻击，0费消耗）：弃牌堆存在「裁决之龙」和「惩戒之龙」时才能打出（金色发光）；消耗弃牌堆所有卡→对所有敌人造成44/56伤害（敲+12）并施加3层虚弱3层易伤→从消耗堆把两种龙各1张加入手牌（手牌满留在消耗堆）。原型=YGO 46186135（裁决+惩戒融合），卡图 tools\make_shining_dragon_art.py 裁切 ygopro pics\46186135.jpg；不打「光道」标（同裁决/惩戒）。部署验证：v0.4.8 日志加载无异常。版本 0.4.7→0.4.8。

> v1.12（mod v0.4.9，用户点名新增遗物）：**新增初始遗物「你必须玩游戏王」MustPlayYugioh**（Starter，图标=ygopro 卡背 cover.jpg 漩涡正方形裁剪，tools\make_yugioh_relic_icon.py 生成 64/256 两档；效果文本用户钦定："你的卡组数量不够，但我修复了这一点"）。效果：战斗开始时（BeforeCombatStart）若抽牌堆不足40张，从角色专属卡池随机生成卡牌、随机位置插入抽牌堆直至满40（游戏王"卡组最低40张"规则梗）。生成概率**白(普通):蓝(罕见):金(稀有)=6:3:1**（Rng.CombatCardGeneration.NextInt(10) 分段 0-5/6-8/9）；实现走 Metamorphosis 原版范式：Character.CardPool.GetUnlockedCards → 只取 Common/Uncommon/Rare 且 CanBeGeneratedInCombat（打击/防御=Basic、白雪化身=Token 不参与）→ CombatState.CreateCard(canonical, player) → CardPileCmd.AddGeneratedCardToCombat(Draw, Random)。**原初始遗物光道圣徽转入遗物池**：稀有度 Starter→Uncommon（游戏 RelicGrabBag 只收录白/蓝/金/Shop 四档，Starter 永不掉落，改稀有度即自动进掉落/商店池），商店价随稀有度默认 MerchantCost=225（未覆写）。部署验证：v0.4.9 日志加载无异常。版本 0.4.8→0.4.9。
>   
> v1.9（mod v0.4.10，第九轮反馈17条全部落地）：①珍妮丝文案"回复生命"→"获得格挡"（v0.4.8改代码时漏改文案）；②沃尔夫/费莉丝描述改写为"只有从抽牌堆以外的地方加入手牌时，此牌才能打出"（代码行为本就如此，仅文案明确化，已核对）；③光道之龙 0费→1费；④多张选牌一次选完（参考雪之化身，LsUtil 新增 PickSomeFromList(min,max)）：雷喵洗回改 0~~2 张自选（原自动取前2张）、雅典娜①弃2张改一次选完②消耗至多4张改 0~~4 一次选完、黄昏之交衣消耗改 0~4 一次选完（原自动取前4张）。**设计决策：雅典娜"2张不同名"约束随一次性选牌移除**（MultiPileCardSelect 不支持跨选校验）；⑤圣女：追加弃光原硬编码3改与首段共用 {Mill} 变量，敲后两处同时 3→4；⑥丽拉/暮光道巫师：减敏捷改为1层脆弱；⑦埃癸斯盾 BlockGain 4→2（敲后3）；⑧少女：检索的龙牌加入手牌时 AddKeyword(Exhaust)；⑨丽拉/暮光道巫师整卡加消耗（CanonicalKeywords）；⑩米迦勒每回收1张 3→1 格挡；⑪悬浮预览（问题11）：暮光注册为自定义关键词（LsKeywords.Twilight + card_keywords.json 词条），暮雷/暮丽拉/暮简/暮萨满/惩戒之龙挂 CanonicalKeywords——卡牌停留提示面板显示暮光效果；6张关联牌卡覆写 ExtraHoverTips=HoverTipFactory.FromCardWithCardHoverTips<T>()（游戏官方范式）：光道之龙/少女/裁决/双龙/神光→龙牌预览，白雪→雪之化身；⑫魏丝敲后强化改弃光3（原压回+1）；⑬暮光道萨满：消耗堆拿1→2张（一次选完）、暮光 2→1 层、敲后改0费；⑭暮光道四卡全部获得1层暮光（暮简补上）；⑮暮光机制重做：打出光道牌→弃光3→层数-1；若本次弃光不满3（卡组不够）且剩余≥2层，再消耗2层把弃牌堆洗回抽牌堆（CardPileCmd.Shuffle 正合"洗整个弃牌堆"语义）并补完剩余弃光。**决策：2层是洗牌额外代价（触发本身仍耗1层，共3层）**；⑯你必须玩游戏王：生成比例改 打击:防御:白:蓝:金=50:50:85:15:5（NextInt(205) 分段，打击/防御直接生成初始牌 LightBlade/LightWard）；⑰闪光之幻想重做：选弃牌堆1张「光道」攻击牌→获得其面板伤害数值的格挡（DamageVar.BaseValue，含该卡敲后增量）→弃光2；敲后 Bonus 0→3（描述 IfUpgraded 显示（+3））。新增选牌提示 LIGHTSWORN_FLASH_PICK。部署验证：v0.4.10 日志加载无异常。版本 0.4.9→0.4.10。
>   
> v1.13（mod v0.4.11，用户点名暮光机制再重做，原有效果全部废除）：暮光推倒重做：v0.4.10 的"打出光道牌→弃光3→层数-1"整体删除（TwilightPower 不再覆写 AfterCardPlayed），暮光改为**纯被动层数资源**——判定挪进 LsUtil.Mill（player 重载，卡牌/能力/加洛斯追加等一切弃光来源统一覆盖）：单次弃光数量 > 抽牌堆剩余时，消耗2层暮光→CardPileCmd.Shuffle 把整个弃牌堆洗回抽牌堆→PlayerCmd.GainEnergy 回1费→补完剩余弃光。**设计决策：**&#x2460;弃牌堆为空不触发（洗不回任何牌，白耗层数）；②暮光不足2层不触发；③补完弃光走裸循环不再触发暮光判定（防递归），补完的牌计入 Mill 返回值（光道来源卡的 OnMilledByLsCard 钩子照常覆盖，加洛斯按来源触发）；④除光(Banish)与 MillSelected 选择性弃置不联动暮光（只有"弃光"关键词触发）。文案同步 card_keywords.json（暮光关键词释义）与 powers.json（能力描述/smartDescription），暮光系5张卡只"获得N层暮光"不受影响。新增 tools\update_loc_twilight.py。部署验证：v0.4.11 日志加载无异常。版本 0.4.10→0.4.11。
>   
> v1.14（mod v0.4.12，用户报第三层先古之民达弗卡死）：**根因**：达弗(Darv)的第三个选项「布满灰尘的古卷」(DustyTome)在生成选项时调 SetupForPlayer，从角色卡池抽一张 CardRarity.Ancient（先古）稀有度的卡（原版 Quadcast/成神等复古卡即此，DustyTome 赠送时自动升级1次）；光道池没有先古牌 → Rng.NextItem 空列表返回 null → `.Id` 抛 NRE → 事件选项生成失败卡死（达弗 50% 概率走该分支）。对话系统不受影响（达弗有 ANY 兜底台词；建筑师那种卡死是另一回事，v0.4.3 已修）。**修复**：新增两张先古牌（数值=对应基础牌2.5倍：9伤→23 四舍五入、8格→20、弃光2→5，敲后各+4，费用1不变）：「先古光道圣骑士 简」AncientJain（1费攻击，23伤弃光5）、「先古光道防护罩」AncientBarrier（1费技能，20格挡弃光5）。**设计决策**：①新建先古稀有度新卡而非改动基础牌（先古牌不会进战斗奖励/商店/战斗生成，基础牌继续初始卡组与奖励池）；②卡名含「光道」→ 白名单补 AncientJain/AncientBarrier（30→32张，保留光道标签联动甲铠/加洛斯/弃光引擎）；③卡图暂复制基础牌（Jain.png/Barrier.png），后续可换专属图。卡牌图鉴重新生成见 design\卡牌图鉴.md。部署验证：v0.4.12 日志加载无异常。版本 0.4.11→0.4.12。
>   
> v1.15（mod v0.4.13，用户纠错先古机制并点名新卡）：**机制纠正（原版源码实证）**：先古牌有两条获取线——①欧洛巴斯的遗物「古老牙齿」ArchaicTooth：把卡组里的**基础启动牌**升级成对应先古版（硬编码五组：痛击→破击、中和→压制、释放→守护、陨星→陨石雨、双重施法→四重施法，只认原版那五张基础牌，光道角色永远不触发→欧洛巴斯处显示锁定选项，不卡）；②达弗的「尘封魔典」DustyTome：从角色卡池抽一张先古稀有度的卡，但 **排除 TranscendenceCards（上述五组先古版）**——铁甲池里破击/腐化都在，魔典实际**只能给到没有基础版的腐化**，破击拿不到。**对应调整**：①删除 v0.4.12 的先古光道圣骑士 简/先古光道防护罩（对应"基础牌的先古版"，光道角色无获取途径=死卡；类/白名单（回到30张）/文案/卡图全清）；②新增先古牌**破坏之光 LightOfDestruction**（腐化定位=无基础版，达弗尘封魔典可给，获得时已升级1次；卡图=ygopro 83027236「破坏之光」持续陷阱，tools\make_light_of_destruction_art.py 裁插画区(55,110,345,330)→250x190+圆形能力图标）：1费能力、**固有**，效果=每次弃光对所有敌人施加{Doom}层**灾厄**（6/敲后8，DoomPower 原版能力）。**实现**：LightOfDestructionPower 触发=LsUtil.Mill player重载每次调用通知一次（一次弃光事件1次，与珍妮丝 OnMillHappened 同源；暮光补完计入同一次不另触发；milled=0 不触发）；灾厄施加用 PowerCmd.Apply<DoomPower> 集合重载（光之回弹同款）。白名单不动（卡名无「光道」）。文案 cards.json/powers.json（LIGHT_OF_DESTRUCTION/\_POWER）。部署验证：v0.4.13 日志加载无异常。版本 0.4.12→0.4.13。

> v1.16（mod v0.4.14，用户点名新卡：珠泪哀歌族系列+散卡3张，design\新卡牌.txt）：**新增机制「珠泪融合」+12张卡（卡图全部取自 ygopro pics，tools\make_tear_cards_art.py 统一裁插画区 x44-356→250×190）。**
>   
> **①珠泪融合引擎**（LsUtil.TearFusion + LsKeywords.TearFusion 自定义关键词三件套 + Ls.Tearlaments 标签）：拥有「珠泪融合」的卡被弃置时（弃光=AfterCardChangedPiles Draw→Discard；手牌弃置=AfterCardDiscarded；打出不触发，雷光同款双钩子判定，原版源码实证 AfterCardDiscarded 只在 CardCmd.Discard 内触发、弃光只走 AfterCardChangedPiles，不会双重融合）——从弃牌堆选2~3张珠泪攻击牌→非融合牌 CardPileCmd.Add(…Draw, CardPilePosition.Random) 放回抽牌堆随机位置（融合Token当素材=CardCmd.Exhaust 消耗而非返回），然后从条件满足且本回合未生成过的融合卡中选1张（概念卡 ModelDb.Card<T> 作候选→combat.CreateCard(概念,player) 生成→trigger.IsUpgraded 则 UpgradeInternal+FinalizeUpgradeInternal 融合出强化版）加入手牌。同一回合每张融合卡只能生成1次（LsUtil 静态 HashSet<ModelId> 按 回合:侧 键重置）；每次融合成功通知 PearlWorldPower。融合条件（对所选素材判定，≥语义）：水仙女人鱼=2张珠泪攻击牌；鲁莎卡人鱼=含水仙女人鱼的2张；卡雷多哈特=含雷诺哈特的3张；捕食植物犀角龙=含融合卡的2张。
>   
> **②融合Token×4**（TearFusionToken 基类：CardRarity.Token + CanBeGeneratedInCombat:false + showInCardLibrary:false → 不进奖励/商店/战斗生成/图鉴库；BaseLib 强制 mod 卡必须挂 [Pool] 故保留 Pool 属性，奖励路径由 CanBeGeneratedInCombat 过滤；"离开弃牌堆时消耗"=基类 AfterCardChangedPiles 拦截 Discard→Hand/Draw 转 CardCmd.Exhaust，自耗进消耗堆的事件因 Pile 已是 Exhaust 被守卫跳过防递归）：水仙女人鱼 Kitkallos（0费攻击：卡组选1张珠泪卡0费入手→弃光5→打7/10）；鲁莎卡人鱼 Rulkallos（0费攻击：打15/20、目标 HasPower<MinionPower> 爪牙则伤害翻倍、本回合每打出过1张珠泪卡+2格挡——计数=CombatManager.History.CardPlaysFinished 中 HappenedThisTurn 且带珠泪标的牌+自身1张）；卡雷多哈特 KaleidoHeart（0费攻击：打15/20→卡组选1张珠泪卡弃置（MillSelected，可连锁触发其珠泪融合）→获得荆棘3=原版 ThornsPower）；捕食植物 犀角龙 Dragostapelia（0费攻击：打7/10→对目标施加1层**缩小**=原版 ShrinkPower，对怪物生效：ModifyDamageMultiplicative 减其攻击伤害30%且 AfterApplied 自带 ScaleTo(0.5) 体型缩小动画，怪物回合结束-1层；CanonicalTags 覆写为空=不含珠泪字段）。升级增量：水仙/犀角龙伤害+3（7/10）、鲁莎卡/卡雷多+5（15/20）。
>   
> **③珠泪常驻卡×5**（TearFusionCard 基类：CanonicalTags=[Ls.Tearlaments]、CanonicalKeywords=[珠泪融合]、融合触发双钩子、ExtraHoverTips 预览4张融合卡；**统一规则：升级=融合出强化后的融合卡，自身数值不变**）：塞壬人鱼 Suliek（非普通，1费攻击8：然后可丢弃1张手牌攻击牌→回1费+弃光3）；小美人鱼 Merrli（普通，1费攻击7：目标意图不为攻击（Monster.IntendsToAttack）→回1费+弃光3）；梅洛人鱼 Havnis（普通，1费攻击6+4格挡：弃光3）；雷诺哈特 Reinohart（稀有，1费攻击7/10：卡组选1张珠泪攻击牌弃置（MillSelected→可连锁融合）；**不含珠泪融合**；被弃置时（弃光/手牌弃置）可丢弃1张手牌珠泪攻击牌→若丢弃了将自己0费（SetUntilPlayed）回手并 AddKeyword(Exhaust) 获得消耗——已不在弃牌堆（如被融合当素材回收）则不触发）；珍珠世界 Perlereino（稀有能力：每次发动珠泪融合→对所有敌人施加1层易伤（PowerCmd.Apply<VulnerablePower> 集合重载）；敲后追加：打出时从卡组将1张珠泪攻击牌加入手牌）。
>   
> **④散卡×3**：真血公 TrueBloodVampire（稀有，2费攻击18：弃光4/6（敲后 Mill+2）→从本次弃光的牌中选1张攻击牌 TryRecallOnMill 0费入手（SetUntilPlayed）；打出顺序按文案=先伤害后弃光）；手札抹杀 HandDestruction（非普通，0费技能消耗：弃所有手牌再抽等量——CardCmd.DiscardAndDraw（原版 CalculatedGamble 范式，弃置钩子统一在抽牌完成后触发，珠泪融合不吞抽牌）；敲后 RemoveKeyword(Exhaust) 移除消耗，原版 Fusion/Hologram 同款）；愚蠢的埋葬 FoolishBurial（非普通，0费技能消耗：从卡组选1张牌弃置（MillSelected）；敲后移除消耗）。
>   
> **稀有度拍板**（用户授权按强度自定）：小美人鱼/梅洛人鱼=普通，塞壬人鱼/手札抹杀/愚蠢的埋葬=非普通，真血公/雷诺哈特/珍珠世界=稀有。**设计决策**：①珠泪攻击牌=带 Ls.Tearlaments 标的攻击牌（珍珠世界是能力牌不算素材；捕食植物犀角龙不打珠泪标）；②珠泪卡不进 Ls.LightswornNamed 白名单（不触发加洛斯/甲铠等光道联动，两系列互相独立）；③鲁莎卡人鱼的"打出过珠泪卡"计数含本次打出的自身；④手札抹杀弃置的手牌若含珠泪融合卡会触发融合（DiscardAndDraw 后置钩子）。新增选牌提示5条（LIGHTSWORN_TEAR\_*）、card_keywords.json 珠泪融合词条、能力图标 pearlworld（make_power_icons.py）。卡牌图鉴重生成（67张，gen_card_doc.py 适配 Cards5/sealed类/Token稀有度）。部署验证：v0.4.14 日志加载无异常。版本 0.4.13→0.4.14。

> v1.17（mod v0.4.15，用户点名：融合条件改严格判定）：珠泪融合的素材条件从「≥语义」（v1.16 拍板）改为**严格语义**（游戏王原版风格，LsUtil.FusionOptions 四条条件全部加 `m.Count(IsTearAttack) == 2/3` 数量精确判定）：2张条件的融合卡（水仙女人鱼/鲁莎卡人鱼/捕食植物犀角龙）不能拿3张素材发动；3张条件的卡雷多哈特必须恰好3张且含雷诺哈特。**行为变化**：选3张素材但其中没有雷诺哈特时，无可用融合→素材已放回抽牌堆（白洗回，严格判定的自然代价）；选择界面只显示当前素材下可用的融合卡，玩家可据此控制选2张还是3张。card_keywords.json 珠泪融合释义补「素材数量须与条件严格一致」。版本 0.4.14→0.4.15，部署验证日志加载无异常。

> v1.18（mod v0.4.16，用户点名：初始遗物可切换）：**新开局时二选一初始遗物**——原版「选择遗物」覆盖界面（珠宝盒同款 NChooseARelicSelection，横幅=官方 CHOOSE_RELIC_HEADER）在「你必须玩游戏王」和「光道圣徽」之间选一个；**跳过=保持游戏王**。实现（Scripts\StartingRelicChoice.cs，Harmony prefix 替换 `RunManager.FinalizeStartingRelics` 返回 Task）：先原样跑完原逻辑（初始遗物逐个 AfterObtained）→ 对每个持「你必须玩游戏王」的光道玩家弹选择 → `RelicCmd.Replace` 原位换遗物。设计决策：①选圣徽时 RelicCmd.Obtain 自动把它从本局 RelicGrabBag 移除（IsStackable=false，不会掉落第二枚）；选游戏王/跳过则圣徽留在遗物池照常掉落（v0.4.9 行为保留，圣徽仍是 Uncommon 池内遗物）；②读档（LoadRun）不调 FinalizeStartingRelics，已选结果天然随存档持久、不重复弹窗；③同一 RunState 用 ConditionalWeakTable 去重防多入口重弹；④TestMode/PlayerChoiceSynchronizer 为空时跳过走原版逻辑。**关键坑**：LocalContext.NetId 要到 RunManager.Launch()（在 FinalizeStartingRelics 之后）才赋值，弹原生选择界面前必须手动 `LocalContext.NetId = manager.NetService.NetId`，否则 IsMe=false 走 WaitForRemoteChoice 分支开局死锁。版本 0.4.15→0.4.16，部署验证日志加载无异常（选择界面流程待玩家实机确认）。

> v1.18（mod v0.4.16，用户点名：初始遗物可切换）：**新开局时二选一初始遗物**——原版「选择遗物」覆盖界面（珠宝盒同款 NChooseARelicSelection，横幅=官方 CHOOSE_RELIC_HEADER）在「你必须玩游戏王」和「光道圣徽」之间选一个；**跳过=保持游戏王**。实现（Scripts\StartingRelicChoice.cs，Harmony prefix 替换 `RunManager.FinalizeStartingRelics` 返回 Task）：先原样跑完原逻辑（初始遗物逐个 AfterObtained）→ 对每个持「你必须玩游戏王」的光道玩家弹选择 → `RelicCmd.Replace` 原位换遗物。设计决策：①选圣徽时 RelicCmd.Obtain 自动把它从本局 RelicGrabBag 移除（IsStackable=false，不会掉落第二枚）；选游戏王/跳过则圣徽留在遗物池照常掉落（v0.4.9 行为保留，圣徽仍是 Uncommon 池内遗物）；②读档（LoadRun）不调 FinalizeStartingRelics，已选结果天然随存档持久、不重复弹窗；③同一 RunState 用 ConditionalWeakTable 去重防多入口重弹；④TestMode/PlayerChoiceSynchronizer 为空时跳过走原版逻辑。**关键坑**：LocalContext.NetId 要到 RunManager.Launch()（在 FinalizeStartingRelics 之后）才赋值，弹原生选择界面前必须手动 `LocalContext.NetId = manager.NetService.NetId`，否则 IsMe=false 走 WaitForRemoteChoice 分支开局死锁。版本 0.4.15→0.4.16，部署验证日志加载无异常（选择界面流程待玩家实机确认）。

---

## v1.17 影依（Shaddoll）系列落地（2026-10-07，v0.4.18）

**来源**：`design\影依卡牌设计初稿.md`（用户逐条订正后拍板：稀有度分配/影融做成关键词/Token可作素材/生成即强化保留/蠢动数值维持现设计/数值已自行调整），另追加：**神影依每回合每张只能生成1次**。**10处卡名更新**（写作xx读作xx，本质都带影依）：神星之影 路径灵→蛇影依 路径灵、神圣之影 商神杖灵→圣影依 商神杖灵、影灵之翼 文蒂→羽影依 文蒂、影雄之烬 神子晶→虚影依 神子晶、与神之假身的接触→神影依融合、假魂的同化→魂影依融合、冻结之心映照的神影→心影依融合、影光的圣选士→联结之影依化身、通向魂源的影劫回归→神我影依流世、影灵翼骑 影文蒂→翼影依 影文蒂。

**实现总览（35张：本家怪15 + 魔法5 + 陷阱6 + 神影依Token9；普通7/非普通12/稀有7，Token9不进池）**：

- **ShaddollCard/ShaddollToken 基类**（ShaddollBase.cs）：影依标自动挂（基类直接打 + Ls.ShaddollNamed 35张白名单兜底）；被弃置双钩子照珠泪先例（弃光=AfterCardChangedPiles Draw→Discard，手牌弃置=AfterCardDiscarded，打出不触发）→统一管线 `LsUtil.OnShaddollDiscarded`：①触发该卡 OnDiscardedEffect（堕影的蠢动/翼影依影文蒂在场时触发2次，加法叠加=3次；影文蒂每次弃置事件耗1层）②影牢之咒缚每次弃置事件+1镀层（PlatingPower，与触发次数无关）。ShaddollToken：Token三要件+打出后消耗（基类CanonicalKeywords=Exhaust）+洗回抽牌堆/回手自动消耗（珠泪Token同款兜底）。
- **影融引擎**（LsUtil.ShaddollFusion）：三模式——Hand（默认弃手牌2~3素材）/DiscardExhaust（弃牌堆2张影依消耗、不触发被弃置时）/Exempt（任意2张手牌含≥1影依→任意神影依）；includeDraw 参数（影依融合强化后素材可从卡组选，卡组素材走MillSelected同样触发钩子）。素材候选预筛（组合枚举：只显示能参与至少一个可用融合的牌）；选定素材无可用融合=不弃置不消耗什么都没发生（严格判定，v0.4.15珠泪精神）；手牌素材弃置触发各自被弃置时效果。9张神影依注册表条件严格匹配（2张条件拿3张不能发动）；生成锁=每回合每张1次（"回合:侧"键照珠泪）+文迪戈本场战斗1次（战斗引用比对清空）。trigger升级或forceUpgraded（神影依融合）→生成强化版。`LsUtil.PickAndGenerateShaddoll`=心影依融合专用（选神影依生成入手+伤害置0，同样吃生成锁）。
- **「影融」自定义关键词**（SHADDOLLFUSION，暮光三件套先例）：LsKeywords+card_keywords.json 全条件表+7张影融卡挂 ExtraHoverTips=>ShaddollFusionTips() 悬浮列出9张神影依。
- **「本回合不能打出」**（影依巫女回收的牌）：LsUtil.LockPlayThisTurn/IsPlayLocked——回合键控+战斗引用清空的静态锁，ShaddollCard/ShaddollToken 的 IsPlayable 拦截（BlockedByCardLogic）。
- **能力×4**（Powers.cs）：SinisterShadowGamesPower（永续标记）/CurseShadowPrisonPower（OnShaddollDiscarded 通知+镀层）/ShaddollHoundPower（AfterCardPlayed=影依攻击牌打出时额外触发其OnDiscardedEffect，Amount=1/2，AfterSideTurnEnd自删=TangledPower范式）/WendikurhuPower（3次计数，管线内Decrement）。图标=对应卡图圆形裁切（tools\make_shaddoll_power_icons.py）。

**AI拍板事项（用户订正稿之外的自定决策，可再调）**：①翼影依影文蒂敲后"格挡10→14"无落点→基础效果补"获得10点格挡"；②心影依融合"触发其效果"实现为生成入手牌+伤害置0（非程序化打出），其升级=选2张时生成的神影依不升级（它不是影融卡，不吃"trigger升级→强化版"规则）；③影依·拿非利被弃置回手计数"弃牌堆中其他影依牌"不含自身；④蠢动+影文蒂同时在场触发次数加法叠加（1+1+1=3次）；⑤文迪戈"本场战斗不可再使用"=只锁生成（被其它效果回收入手后再打出不拦）；⑥选定素材无可用融合时不弃置不消耗（严格判定的自然代价）；⑦影融素材候选界面预筛（只显示可参与的牌）；⑧白名单 ShaddollNamed 35张照设计稿实现（与基类打标双保险）；⑨猎犬加成（打出触发）不与蠢动/影文蒂（弃置事件加成）叠加计算；⑩艾莉娅儿被弃置时消耗弃牌堆牌0~2可选。

---

## v1.18 融合体验五条优化（2026-10-07，v0.4.19，design\已知问题.txt）

**来源**：用户批次反馈5条，全部按字面落实。

1. **神影依Token消耗时机改珠泪同款**：ShaddollToken 基类删掉 `CanonicalKeywords=[Exhaust]`（不再"打出后消耗"），保留已有的 AfterCardChangedPiles 拦截（离开弃牌堆回手/回卡组→消耗，TearFusionToken 同款）。打出后留在墓地可继续当影融素材（DiscardExhaust 模式）或被检索效果使用；一旦离开弃牌堆即消耗。card_keywords.json 影融释义同步"离开弃牌堆时消耗"。
2. **影融/珠泪融合触发卡升级加"+"**：卡片悬浮面板的词条说明是静态缓存（HoverTipFactory.FromKeyword，无卡牌上下文），词条 title 吃不到 IfUpgraded——因此"+"加在**各触发卡自己的描述文本**里：`{IfUpgraded:show:+|}` 跟在"影融"/"珠泪融合"词后（珠泪3张原本描述不含词条词，补写"珠泪融合{IfUpgraded:show:+|}。"），升级预览可见"影融+/珠泪融合+"。
3. **融合条件挪到各融合卡卡面**：13张融合卡（珠泪4+神影依9）描述前置"融合条件：…
     
   "行（措辞沿用原词条里的条件表）；TEARFUSION/SHADDOLLFUSION 词条描述删掉条件清单，改为"素材数量须与融合条件严格一致，各融合卡的条件见其卡面说明"。
4. **顶栏融合图鉴按钮**（新文件 Scripts\FusionCodex.cs）：NTopBar.Initialize 的 Harmony postfix 在 RightAlignedStuff（HBox）里、"卡组"左侧插 80×80 槽位+NButton 子类按钮（BaseLib NModListButton 先例：ctor 建子节点、\_Ready 调 ConnectSignals；仅本地玩家是光道角色时添加）。点击=NCardPileScreen.ShowScreen(new CardPile(PileType.Deck) 装13张概念卡的 MutableClone)（原版抽/弃/消耗堆同款界面，Deck 类型走牌库视图渲染、底栏说明自动隐藏；PreloadManager.Cache.GetScene 对未预载场景有 ResourceLoader 同步兜底——坑18同源结论），再点一次=关闭（toggle，只认自己打开的那次）。**置灰**=FusionLockWatcher（Node.\_Process 逐帧递归遍历 CardGrid 的 NCardHolder，按 holder.CardModel.Id 查 `LsUtil.IsFusionUsedForCodex`：珠泪/影依"本回合已生成"∪文迪戈"本场战斗已生成"，回合/战斗键控失配视为未生成）命中→holder.Modulate 灰色(0.45,0.45,0.5)。图标=ygopro cover.jpg 圆形裁切+描边圈 144×144（tools\make_fusion_codex_icon.py→images\ui\fusion_codex.png，res://lightsworn/images/ui/ 加载）。悬浮提示=LocString("static_hover_tips","LIGHTSWORN_FUSION_CODEX.*")，mod 本地化按文件名合并进游戏 static_hover_tips 表（v0.4.3 ancients.json 同机制，新增 localization\zhs\static_hover_tips.json）。按钮 hover=NHoverTipSet（NTopBarDeckButton 同款）+图标 Modulate 提亮。
5. **删词条关联卡悬浮预览**：TearFusionCard.ExtraHoverTips（4张珠泪融合卡）与 ShaddollCard.ShaddollFusionTips()（9张神影依，7张影融卡+心影依融合挂的）整体删除；影融/珠泪融合词条的悬浮面板说明保留（CanonicalKeywords 机制不变）。其它 ExtraHoverTips（龙牌/白雪等 v0.4.10 的关联预览）不受影响。

**AI拍板事项**：①"+"加在卡面描述而非词条面板（词条说明无卡牌上下文，加不了动态标记）；②图鉴只展示基础版融合卡（强化版差异见各触发卡升级说明）；③神影依Token回手类效果（如米德拉什检索影依技能）从弃牌堆捡起Token会立即消耗——珠泪Token同款语义，按"离开弃牌堆时消耗"字面执行；④图鉴按钮仅光道角色显示（多人局其他角色不显示）。

---

## v1.19 融合Token消耗语义订正（2026-10-07，v0.4.20，对话点名）

**来源**：用户对 v0.4.19 第①条的澄清——"我想的是回到卡组消耗，如果有办法直接从弃牌堆加入手牌是不消耗的"。

**改动**：TearFusionToken 与 ShaddollToken 两个基类的 AfterCardChangedPiles 拦截范围从"弃牌堆→手牌/卡组都消耗"收窄为**只拦截"弃牌堆→卡组（抽牌堆）"时消耗**；被效果直接从弃牌堆加入手牌则保留（可继续打出，打出后回墓地不消耗）。v0.4.14 起"离开弃牌堆时消耗"的旧语义（含回手）作废——当时是按设计稿字面+AI拍板实现的，用户本意一直是"回卡组才消耗"。

**行为变化**：①神影依Token被米德拉什/文迪戈等"从弃牌堆将1张影依(技能)卡加入手牌"检索回手时不再自燃，可以继续打出（打出回墓地，仍可再检索/当影融素材）——Token检索连锁成立；②珠泪Token被真血公等效果从弃牌堆回手同理保留；③洗回卡组的一切来源（暮光洗回/CardPileCmd.Shuffle/融合素材返回等）照旧消耗；④珠泪融合把Token当素材、影融 DiscardExhaust 模式消耗素材=代码里显式 Exhaust，与钩子无关，不变。

**文案**：card_keywords.json 两个融合词条的消耗措辞同步改为"回到卡组（抽牌堆）时消耗，被效果直接加入手牌则保留"。

---

## v1.20 影依两条反馈（2026-10-07，v0.4.21，对话点名）

**来源**：用户直接对话反馈两条：①影依卡伤害变为0的效果改为只持续一次，当前是永久；②神影依从弃牌堆拿影依卡的效果加上限制，不能拿神影依，普通影依还是可以从弃牌堆拿神影依。

**①心影依融合伤害置0改一次性**：原实现（v0.4.18）=PickAndGenerateShaddoll 里直接 `token.DynamicVars["Damage"].BaseValue = 0m`，永久生效（Token被检索回手再打出仍是0伤害）。现改为：生成时把原伤害记在Token实例新字段 `ShaddollToken.DamageRestoreAfterPlay` 上再置0，覆写 `AfterCardPlayed`（游戏钩子，AbstractModel 虚方法；实证时序=CardModel.cs:1959 在牌从打出堆移入弃牌堆*之前*触发，故落弃牌堆时已是正常伤害，检索方拿到即为原值）打出后恢复原值并清标志。只影响心影依融合生成的攻击Token（zeroDamage 参数唯一调用点 Cards7 心影依融合），影融/神影依融合正常生成的Token不变。**AfterCardPlayed 能收到"正在打出的牌自己"**：PlayPile 在 PlayerCombatState.AllPiles 里（5堆含打出堆），IterateHookListeners 遍历全部牌堆。

**②神影依检索不能拿神影依**：9张神影依Token（Cards8.cs）的"从弃牌堆拿影依卡"类效果全部加过滤 `!LsUtil.IsElShaddollToken(c)`（新判定= `card is ShaddollToken`，神影依=9张战斗Token 的类型学判定；普通影依=ShaddollCard 子类不受影响）。覆盖：米德拉什/拿非利/文迪戈/神子晶/舍金纳迦（影依技能）、异花莉莉丝（影依牌×2）、七贤巨鲲魔（卡组或弃牌堆影依卡）、米沙赫雷恶（弃牌堆影依攻击卡+卡组影依卡顺手同滤，防御性）、翼影依 影文蒂（影依卡）。动机=v0.4.20 Token检索连锁成立后，米德拉什（回3费）等可构成神影依互检循环。AI拍板：七贤巨鲲魔/米沙赫雷恶的**卡组半边**也一并过滤（Token事实上进不了卡组——弃牌堆→卡组即被钩子消耗，文案无需加限定）；"从卡组弃置影依卡"（拿非利）、"丢弃手牌影依卡"（神子晶/舍金纳迦）是弃置不是检索，不动。

**文案**：cards.json 10条——心影依融合加"（打出一次后恢复）"；9张神影依检索句加"非神影依的"限定（卡组半边措辞不动）。工具 tools\update_loc_v0421.py（含旧文案校验，Apkallone 那句后接"，然后弃置1张手牌"不是句号）。

---

## v1.21 伤害置0一次性·补全漏网三卡（2026-10-07，v0.4.22，对话点名）

**来源**：用户追问"还有张影依卡也有变0的效果，修了吗"——v0.4.21 只修了心影依融合，全量 grep `BaseValue = 0` 后发现**另有3张影依卡**是同样的永久伤害置0：**羽影依 文蒂**（Cards6，从卡组拿影依攻击卡）、**虚影依 神子晶**（Cards6，从弃牌堆拿）、**联结之影依化身**（Cards7，从弃牌堆拿）。三张原本描述写"本回合…其伤害变为0"，实现却是永久（文/实不符）。

**改动**：①恢复机制从 ShaddollToken **上移到 LsCard 基类**（`DamageRestoreAfterPlay` + AfterCardPlayed 覆写）——这三张拿的是普通影依攻击卡不是Token，且联结化身/虚影依神子晶作为普通影依可从弃牌堆拿到神影依攻击Token（用户规则②明文允许），机制必须在 LsCard 层才能同时覆盖两类卡；②LsUtil 新增 `ZeroDamageOnce(CardModel)` 统一入口（记录原值+置0），4个调用点全部改走它（心影依融合 PickAndGenerateShaddoll / 羽影依文蒂 / 虚影依神子晶 / 联结之影依化身）；③行为=伤害0持续到该卡**打出一次后恢复**（费用0的语义不变：文蒂/神子晶=SetThisTurnOrUntilPlayed，化身=SetUntilPlayed）。

**语义拍板**：用户规则字面是"只持续一次"，故文蒂/神子晶描述里的"本回合"对**伤害**部分不再成立（可跨回合保留到打出为止）——文案改为"其伤害变为0（打出一次后恢复）"，"本回合"仅修饰费用。cards.json 3条（tools\update_loc_v0422.py）。

**排查结论**：全mod伤害置0共4处（`DynamicVars["Damage"].BaseValue = 0m`）已全部收编；其余"变0"均为费用（EnergyCost.SetUntilPlayed/SetThisTurnOrUntilPlayed），不在本次范围。部署验证：日志 0.4.22 加载无异常。

---

## v1.22 第十轮反馈11条（2026-10-10，v0.4.23）

**来源**：`design\已知问题.txt`（11条）。

**核心根因（问题1/3共因）**：融合结果选择界面把**不可变概念卡**（ModelDb 范例卡）直接传进
  
MultiPileCardSelect——`NSimpleCardSelectScreen._Ready` 读 `card.Owner` 时对不可变模型抛
  
**CanonicalModelException**，界面初始化中断、点击卡牌 NRE（v0.4.20 会话日志实证：珠泪融合选
  
Rulkallos、影融选 ElShaddollWinda 两处 `_Ready` 崩溃 + 2次 OnCardClicked NRE；选完虽能恢复
  
但交互残废）。影响全部融合触发卡（影依融合/神影依融合/魂影依融合/影依的原核/影依的伪典/
  
虚影依 神子晶/影依·拿非利 + 塞壬/小美/梅洛 + 心影依融合）的结果选择。修复=**LsUtil.PickConcept**：
  
概念卡先 `MutableClone()`+设 Owner 再进选择界面（FusionCodex 可变克隆先例的推广），
  
选中后按 Id 映射回原概念卡供 CreateCard。伤害置0（问题1）的 v0.4.22 恢复机制经源码核对无误；
  
心影依融合"伤害变0"观感失效即此界面崩溃所致。ZeroDamageOnce/恢复顺带 TryGetValue 加固。

11条逐一：

1. **伤害临时变0没有生效**：根因见上；v0.4.22 的"打出一次后恢复"机制本身有效。
2. **神我影依流世高亮**：`IsPlayable` 的 `Any(IsShaddoll)` 把手牌中的**自己**算进去（打出前本卡
     
   在手牌且自带影依标）→手牌无其他影依牌也高亮黄光、判为可打出（实际无牌可弃）。已排除自身
     
   （IsPlayable 与 OnPlay 弃置候选都加 `!ReferenceEquals(c, this)`）。
3. **魂影依融合不能手动选素材**：同问题1根因——素材选择（手牌真卡）没问题，坏在结果选择的
     
   概念卡界面崩溃。
4. **神影依第二次使用消耗**：ShaddollToken 实例计数 `_playCount`，`AfterCardPlayed` 计数≥2 时
     
   Exhaust（配合联结之影依化身的循环上限=每张2次）；9张神影依描述+影融词条同步加
     
   "第2次打出时消耗"。
5. **只有名字带影依才是影依卡**：ShaddollCard/ShaddollToken 基类**不再直接打标**，统一走
     
   Ls.ShaddollNamed 白名单（35→32张：移除炼狱的乖放/堕影的蠢动/影牢之咒缚）；
     
   LsUtil.OnShaddollDiscarded 的蠢动加倍/影文蒂层数/咒缚计数按 IsShaddoll 门控；
     
   ShaddollHoundPower 改标签制判定。三张卡自身被弃置只走自己的 OnDiscardedEffect（本无）。
6. **影融素材双角色占位**：新助手 **DistinctPair**——一张牌不能同时占「影依位」和「类型位」。
     
   文迪戈=影依+另1张技能、神子晶=影依+另1张攻击：影依攻击卡+非影依技能卡现在只能融文迪戈；
     
   拿非利同改（防患）。
7. **米德拉什**：融合条件=1张影依+1张影依/珠泪牌（DistinctPair：影依位+影依/珠泪位，双影依照旧）。
8. **珠泪融合素材必含触发卡**：TearFusion 选素材=触发卡（自动占1席）+其他珠泪攻击牌1~2张；
     
   珠泪融合词条与选牌提示同步。
9. **犀角龙融合卡位适配神影依**：条件=1张融合卡（TearFusionToken 或 ShaddollToken）+1张珠泪
     
   攻击牌（DistinctPair）。
10. **太阳交换**：IsPlayable=手牌有「光道」牌（+金光高亮）；描述加"仅当手牌中有「光道」牌时才能打出"。
11. **露米娜丝/暮露米娜丝**：拿2→1，各追加获得10格挡（BlockVar 10）。

**AI拍板**：①问题2按bug修复并在汇报里解释成因；②米德拉什=两角色语义（影依位+影依/珠泪位）；
  
③犀角龙"融合卡"定义=TearFusionToken 或 ShaddollToken；④神影依二打计数按实例（每张生成物
  
独立2次上限，实例随战斗销毁不跨局）；⑤暮露米娜丝格挡在拿牌后、给暮光前结算。

**验证**：v0.4.23 加载无异常（godot.log 实证）。

---

## v1.23 融合双bug修复（2026-10-11，v0.4.24，用户实测反馈）

**来源**：用户实测「两个bug在最新一次对战都有触发」（godot.log 会话 Seed CDUDBVL19P 实证），
  
已知问题.txt 两条：①影依伤害临时变0未生效（化身拿影依兽打出仍9点）；②弃置梅洛人鱼墓地有
  
影依卡未触发珠泪融合（应可融合米德拉什）。

**问题1真根因（v0.4.21/22 两轮修复都修错方向）**：`Hook.AfterCardPlayed` 是**广播钩子**
  
（`combatState.IterateHookListeners()` 遍历全部牌堆的所有模型，CardModel.cs:1959 在 OnPlay
  
之后调用）——v0.4.21 的设计文档只记对了「能收到打出的牌自己」，漏了反向：**它也会收到
  
「别的卡被打出」的通知**。化身 OnPlay 尾部把影依兽置0（DamageRestoreAfterPlay=9,
  
BaseValue=0）→ 化身自己打完 → 广播把手牌里影依兽的 AfterCardPlayed 也调了 → 恢复机制当场
  
把 BaseValue 恢复回9 → 打出9点。零化从未活过一整个 OnPlay，这就是「检测仍然未修复」的原因
  
（v0.4.22 把锅判给融合选择界面崩溃 CanonicalModelException，误诊）。修复=两处覆写加
  
`cardPlay.Card == this` 自判：**LsCard.AfterCardPlayed**（伤害恢复）与 **ShaddollToken.AfterCardPlayed**
  
（二打计数——原实现打2张别的卡也会累计计数误消耗Token，属同根因的隐藏bug）。能力的
  
AfterCardPlayed（甲铠/猎犬等）本就是广播语义且自带 cardPlay.Card 判定，不动。

**问题2**：珠泪融合引擎（LsUtil.TearFusion）素材池只筛 `IsTearAttack`、产出只有4张珠泪Token，
  
影依牌永远进不来；墓地无其他珠泪攻击牌时静默 return（用户看到=没触发）。修复四件套：
  
①素材池扩为「珠泪攻击牌 或 影依牌」+候选预筛（照影融 ValidMaterialCandidates 精神，只显示与
  
触发卡组合后至少一种可用融合的牌）；②FusionOptions 加入**米德拉什**（条件与影融同：1影依+
  
1影依/珠泪，DistinctPair——触发卡自己占珠泪位）；③**严格判定前置**：available 判定挪到素材
  
弃置/回卡组之前，选出无融合的组合=什么都没发生（v0.4.15「白洗回」代价废除：素材池跨系后
  
误选概率大增）；④**生成锁跨引擎统一**：ResetShaddollFusionKeys→ResetFusionKeys（清两个
  
集合+文迪戈锁，一个 turnKey），生成时双登记（RegisterFusionGenerated），IsFusionLocked/
  
IsFusionUsedForCodex 双查——杜绝「珠泪融合与影融各生成一次米德拉什」的绕锁。

**文案**：card_keywords.json 珠泪融合词条（素材=珠泪攻击牌或影依牌、产出=融合卡）、
  
card_selection.json LIGHTSWORN_TEAR_MATERIAL。米德拉什卡面条件行不变（两引擎同条件）。

**AI拍板**：①严格判定前置（废除白洗回）②锁跨引擎统一（每回合每张全引擎共1次）③预筛只
  
对「trigger+单素材」组合判定，双素材组合靠前置 available 兜底。

**验证**：0.4.24 加载无异常（checklog + 全日志过滤 0 ERROR）。

---

## v1.24 珠泪融合产出神子晶（2026-10-11，v0.4.25，用户点名）

**反馈**：触发珠泪融合时，珠泪攻击卡+影依卡应当满足神影依·神子晶（ElShaddollGrysta）的融合条件。

**修复**：LsUtil.FusionOptions（珠泪融合产出注册表）加入神子晶——条件与影融同：`m.Count == 2 &&
DistinctPair(m, IsShaddoll, c => c.Type == CardType.Attack)`（1张影依+1张攻击牌）。珠泪融合触发卡
  
（塞壬人鱼/小美人鱼/梅洛人鱼均为攻击牌）自己占攻击位，另选1张影依牌当影依位即可融合。严格数量
  
判定不变：选2张素材=共3张材料，神子晶/米德拉什（均2张条件）不满足，此时只有珠泪系条件可能满足。
  
候选预筛自动覆盖（[trigger, 影依卡]组合经神子晶条件判定通过，影依牌全量进选择界面）。

**文案**：无需改——珠泪融合词条/选牌提示为通用表述（"满足融合条件的融合卡"），神子晶卡面
  
「融合条件：1张影依卡+1张攻击牌」本就准确，珠泪融合素材组合可自然满足。

**验证**：v0.4.25 加载无异常（checklog：Version=0.4.25.0 + Lightsworn mod initialized +
  
NO RELEVANT ERRORS）。

---

## v0.4.26（2026-10-11）：事件「于珍珠世界相逢」+ 遗物「猫狗双全」（用户点名两张素材图）

**事件：于珍珠世界相逢**（首个自定义事件，Scripts\Events.cs，mod 新增 localization\zhs\events.json）：

- BaseLib `CustomEventModel` 范式：构造时自动注册进共享事件池（**BaseLib 不会反射实例化事件类，
    
  必须 Entry.Init 里手动 `new PearlWorldEncounter()`**）；`Acts=[]`=任意幕可刷，
    
  `IsAllowed` 限定全部玩家都是光道角色才出现；非共享事件（各玩家独立选择）。
- 选项一「与珠泪哀歌族同行」=塞壬人鱼/梅洛人鱼/小美人鱼三张加入卡组（RunState.CreateCard +
    
  CardPileCmd.Add(Deck) + PreviewCardPileAdd，TheLegendsWereTrue 原版范式）；选项二=珍珠换
    
  **100 金币**（对齐原版无代价给金档：LostWisp 60 / TrashHeap 100 / TheLanternKey 100，
    
  GoldVar + {Gold} 在选项描述里渲染，NEventOptionButton 自带 DynamicVars.AddTo）。
- 选项悬停预览三张人鱼卡面（HoverTipFactory.FromCardWithCardHoverTips 三连）。
- 事件 ID=`LIGHTSWORN-PEARL_WORLD_ENCOUNTER`（GetPrefix=命名空间首段大写+'-'，Entry=类名蛇形），
    
  loc 键={Id}.title / .pages.INITIAL.description / .pages.INITIAL.options.{方法名蛇形}.title/.description /
    
  .pages.{页}.description（结局页）。选项键由 CustomEventModel.Option(方法组) 按方法名自动推导。
- **事件立绘规格=3440×1613**（Godot 无头读原版 round_tea_party ctex 实测；正好填满默认布局
    
  %Portrait 的 2560×1200 KeepAspectCentered 框）。素材 1536×1174 → cover 模糊底 + 等高居中前景
    
  左右羽化 80px 合成（tools\make_pearl_event_art.py）。路径=res://lightsworn/images/events/pearl_world_encounter.png
    
  （CustomInitialPortraitPath 覆写；**新 PNG 必须先 Godot --headless --import 再 ExportPck**）。
- 实测捷径：run 中控制台 `event LIGHTSWORN-PEARL_WORLD_ENCOUNTER` 直达（EventConsoleCmd 按 Id.Entry 匹配）。

**遗物：猫狗双全**（CatsAndDogs，普通/Common，进光道遗物池掉落+商店 175）：

- 效果=每当抽到「光道兽 沃尔夫」或「光道弓手 费莉丝」时再抽 1 张。实现=覆写
    
  `AfterCardDrawn(ctx, card, fromHandDraw)`——**该钩子的监听者含玩家全部未熔解遗物**（CombatState.IterateHookListeners
    
  实证），fromHandDraw 不筛（回合抽牌/效果抽到都触发）；连锁抽到继续触发（CardPileCmd.Draw 自带
    
  手牌上限/洗牌/空堆检查，天然终止）；`card.Owner != Owner` 过滤他玩家。
- 图标=素材中央金环徽章圆裁 256/64（径向中值+最小二乘拟合圆心 r=476，tools\make_catdog_relic_icon.py），
    
  **右下角「豆包AI生成」水印用整块横向克隆（同高度干净区 830..1050）+羽化+残条洋葱填充修掉**，
    
  去水印整图存 `D:\download\chrome_download\光道mod素材\猫狗双全_去水印.png`（素材库备用，不入 mod）。

**验证**：v0.4.26 加载无异常（checklog：Version=0.4.26.0 + Lightsworn mod initialized + NO RELEVANT
  
ERRORS；pck 内 events.json/立绘 ctex/遗物图标 ctex 齐全）。

---

## v1.25 事件黑屏修复（2026-10-11，v0.4.27，朋友实测反馈）

**来源**：用户朋友实测 v0.4.26，走进「于珍珠世界相逢」事件房**黑屏卡死**（本机从未实际进过该事件——v0.4.26 会话只验证了"加载无异常 + pck 含资源"，事件屏幕从未视觉验证过）。

**根因（代码级实证）**：`PearlWorldEncounter` **漏写 `CustomInitialPortraitPath` 覆写**（开发手册 §5 记了这条做法，但 v0.4.26 的 Events.cs 里没有）→ 事件立绘路径走原版规则 `res://images/events/pearl_world_encounter.png`（游戏本体目录，mod 立绘实际在 `res://lightsworn/images/events/`）→ 进事件房预载失败，`AssetCache.MarkAssetFailed` 标记该路径 → `NEventRoom.SetupLayout()` 第一行 `Layout.SetEvent()` 内 `CreateInitialPortrait()` 对已标记失败路径**抛 AssetLoadException** → `SetTitle`/`SetDescription`/选项渲染全部不执行（异常被 `TaskHelper.RunSafely` 吞进日志）→ 空黑界面永久卡死。与坑18 同族：SetupLayout 中途抛异常=事件房半初始化。

**改动**：①Events.cs 补 `CustomInitialPortraitPath => res://lightsworn/images/events/{Id.Entry 蛇形小写}.png`（顺手在 JoinTearlaments 加 `Cmd.CustomScaledWait(0.5f,1.2f)` 对齐原版 TheLegendsWereTrue 的入组动画节奏）；②新增 `localization\eng\events.json`（zhs 内容原样复制）——EventOption 构造对缺键返回 null LocString，`AddLocVars` 里 `description.Add()` 直接 NRE，非中文玩家进同样黑屏；eng 表作为所有非 zhs 语言的回退兜底。

**验证**：v0.4.27 加载无异常，日志确认 `eng events.json` 与 `zhs events.json` 均合并。事件屏幕实机复验待用户/朋友下次进事件确认（控制台 `event LIGHTSWORN-PEARL_WORLD_ENCOUNTER` 可直达）。

---

## v1.26 事件黑屏二次修复（2026-10-11，v0.4.28，用户控制台实测反馈）

**来源**：用户在控制台重试 `event LIGHTSWORN-PEARL_WORLD_ENCOUNTER`，事件仍未弹出。日志实证：`No loader found for resource: res://lightsworn/images/events/lightsworn-pearl_world_encounter.png`——v0.4.27 的覆写写成 `{Id.Entry.ToLowerInvariant()}`，拼出的路径比实际文件名**多了 mod 前缀**（`Id.Entry`="LIGHTSWORN-PEARL_WORLD_ENCOUNTER" 自带前缀；实际立绘文件=类名蛇形 `pearl_world_encounter.png`）。同样的预载失败→MarkAssetFailed→同样的 AssetLoadException 黑屏。

**改动**：`CustomInitialPortraitPath` 改为硬编码真实文件名 `res://lightsworn/images/events/pearl_world_encounter.png`（新事件立绘文件按类名蛇形命名）。手册坑23 补两轮踩坑经过，§5 立绘约定订正为"<类名蛇形小写>.png 不含 mod 前缀"。

**验证**：v0.4.28 部署后用户控制台实测：日志 `Preloading 'Event Room' Complete: assets=2` 全部加载、零异常（此前每次该行后必跟 Failed+AssetLoadException），事件房完整构建，用户随后正常返回主菜单退出。**事件验证通过标准=Event Room 预载完成后无 Failed/Exception**。

---

## v1.27 融合生成锁跨战斗/跨存档泄漏修复（2026-10-11，v0.4.29，朋友实测反馈）

**现象**：①上一场战斗最后一个回合融合出的怪，下一次战斗开始时不重置（图鉴仍置灰/同回合不能再融）；②第一回合影融（影依+光道攻击→拿非利/神子晶二选一）选拿非利后保存退出→继续（本场重打）→再融只出神子晶→再保存退出→继续→什么都融不了。

**根因**：融合生成锁（v0.4.24 统一引擎）是 static 集合、只按 "回合数:行动方" 字符串键控，不按战斗实例隔离——回合号每场从1重计（CombatState 构造器 RoundNumber=1，存档不含战斗状态）：①跨战斗同回合号碰撞（上一场第N回合的锁漏进下一场第N回合，末回合=第1回合时下一场开局即中）；②保存退出→继续=本场重打（新 CombatState 回到第1回合），键 "1:Player" 未变→拿非利仍锁→只出神子晶；再锁一轮→全锁死。

**改动**：LsUtil.cs 锁状态重做——5个静态字段收敛为 `ConditionalWeakTable<ICombatState, FusionLockState>`（TurnKey+两套本回合已生成集合+文迪戈本场锁），战斗结束随 CombatState 一起被 GC 回收，新战斗/读档重打天然全新；`IsFusionLocked/RegisterFusionGenerated` 补 combat 参数，`ValidMaterialCandidates` 透传；图鉴置灰 `IsFusionUsedForCodex` 改查实例状态（文迪戈项不再需要引用比较）。「本回合不能打出」play 锁本就带实例引用守卫，未动。

**验证**：v0.4.29 构建部署，日志加载零异常。融合场景实机复验待用户/朋友确认（两场战斗连续融合 + 融合后保存退出再继续）。

---

## v1.28 第二十二轮反馈18条：数值回调+稀有度调整+地天使重做+重放接入（2026-10-12，v0.4.30，朋友实测反馈）

**素材/融合引擎（LsUtil.cs）**：

1. 影依融合强化后素材可从卡组选——代码本就没筛，实际可选面比文案宽；按用户拍板"正好控制强度"收紧为**只允许「影依」牌**（includeDraw 池加 IsShaddoll 过滤），文案同步"（限「影依」牌）"。
2. 神影依融合效果调整：生成的神影依**获得1次重放**（原版 BaseReplayCount 机制=打出时效果额外执行1次，HiddenGem/Transfigure 同款，UI自动显示"重放"提示）；不再强制视为已升级（forceUpgraded 移除）；敲后仍=0费。GenerateShaddollToken/ShaddollFusion 加 replayCount 参数。
3. 神影依·拿非利融合条件（1影依+1光道）扩：**圣影依 商神杖灵可充当光道位**（`c is QadshaddollKeios`）；圣影依卡面追加说明、拿非利融合条件行同步。
4. 虚影依 神子晶影融改为**被弃置时发动**（OnDiscardedEffect→DiscardExhaust），打出时不再影融；DiscardExhaust 素材池排除触发卡自身（触发时自己已在弃牌堆）。
5. 珍珠世界能力补齐 powers.json 词条（此前缺失）；易伤层数=Amount（1/敲后2）。

**数值/稀有度**：
  
6\. 蓝卡（Uncommon）×6：虚影依 神子晶、真血公、雷诺哈特、影依刺猬（白→蓝）、惩戒之龙、光道主·大天使 米迦勒。
  
7\. 金卡（Rare）×2：邻家割草、光道宰制者 基里奥斯。白卡（Common）×1：影依巫女 艾莉娅儿。
  
8\. 影依·拿非利 0费→1费。
  
9\. 影依的炎核 虚梦狱：基础改2费15伤；敲后保持原强化版（2费20伤）=升级改为伤害+5（拍板：升级结果与旧强化版完全一致）。
  
10\. 正义世界：每次弃牌3点活力（敲后4）；升级由"获得固有"改为活力+1（拍板）。能力改用 Amount 传层数。
  
11\. 光之回弹：每次弃牌3层灾厄（敲后4）。破坏之光：9层灾厄（敲后12）。
  
12\. 光道主·大天使 米迦勒：每回收1张光道牌格挡1→2。
  
13\. 雷喵：改敲前0费，敲后=洗回数量+1（Picks 变量化，原升级0费作废）。

**效果重做**：
  
14\. 地天使4张（问题14）：姆多拉/凯尔多=0费、回弃牌堆任意2张（敲后3张）到卡组、抽1、抽到攻击/技能牌其费用-1（EnergyCost.UpgradeBy(-1)+FinalizeUpgrade；抽牌堆空触发洗牌时跳过）；凯尔柏克=弃光5，其中2张以上攻击牌→随机敌人7伤（敲后弃光7/10伤）；阿基多=弃光5，其中2张以上技能牌→6格挡（敲后弃光7/9格挡）。
  
15\. 神光之龙（问题10）：消耗堆每有一张「光道」牌额外+5伤害（在消耗弃牌堆之后结算，刚弃光的光道牌计入）；获得新能力**神光回响**（ShiningDragonPower）：回合开始时从弃牌堆随机将1张「光道」牌加入手牌并变为0费（SetUntilPlayed），敲后2张；图标暂复制神域占位。
  
16\. 珍珠世界（问题5）：基础效果=原强化版（每次珠泪融合全体1层易伤+打出时从卡组检索1张珠泪攻击牌），敲后=易伤2层；**去掉珠泪哀歌族标签**（问题15，不再计入"打出珠泪卡"计数）。
  
17\. 珠泪7卡改名（问题15）：珠泪哀歌族 塞壬人鱼/小美人鱼/梅洛人鱼/雷诺哈特/水仙女人鱼/鲁莎卡人鱼/卡雷多哈特；鲁莎卡/卡雷多哈特融合条件行的卡名引用同步。
  
18\. 露米娜丝（问题3）：效果回调——去掉格挡，从弃牌堆拿「光道」牌1→2张（回到 v0.4.10 前）。

**验证**：v0.4.30 构建部署，日志加载零异常；卡牌图鉴已重跑（gen_card_doc SPECIAL 表订正 4 条过时升级说明）。

---

## v1.29 第二十二轮订正两条（2026-10-12，v0.4.31，用户点名）

1. **地天使减费改"仅一次"**（姆多拉/凯尔多）：抽到的攻击/技能牌费用-1 不再是战斗内永久降费（`EnergyCost.UpgradeBy(-1)+FinalizeUpgrade()` 作废），改用原版 `EnergyCost.AddUntilPlayed(-1, reduceOnly: true)`（SlumberingEssence"费用-1直到打出"同款 API）——减费持续到该牌下一次打出，打出后恢复。文案加"（直到打出）"。
2. **雷喵敲后=抽X+1张牌**（X=其效果洗回抽牌堆的牌数）：原拍板"洗回数量2→3"作废；洗回上限固定2，基础固定抽1，敲后抽 chosen.Count+1（洗回0张时=抽1，与基础一致）；Picks 变量删除，升级为行为型（OnUpgrade 空），文案用 {IfUpgraded:show:，然后抽X+1张牌（X=洗回的牌数）|，然后抽1张牌}。

**验证**：v0.4.31 构建部署，日志加载零异常；卡牌图鉴已重跑。

---

## v1.30 第三十八轮反馈37条：数值修正+影依融合体验重做+壹世坏2新卡（2026-10-12，v0.4.32）

**事件/本家（Cards1-4）**：

1. 事件「于珍珠世界相逢」选项一追加诅咒牌「腐朽」（原版 Decay：不可打出，回合结束在手牌受到2点伤害；选项悬停可预览）。
2. 光道贼猫 雷喵：1费（0→1）；抽牌数=洗回牌数X（不再固定1），敲后X+1。
3. 光道武僧 艾琳：伤害8/11（原6/10）；改为"先清除目标所有格挡，然后照常造成伤害"（原清格挡时不打伤害）。
4. 光道圣骑士 简：10/13（原9/13）；稀有度改基础卡。
5. 光道魔术师 丽拉/暮光道巫师 丽拉：脆弱→虚弱；丽拉稀有度白→蓝。
6. 神我影依流世：格挡10/15（原8/12）。
7. 闪光之幻想：弃光移到最前结算。
8. 光道龙 格拉古尼斯：基础伤害固定14（升级不再+4），敲后改为"每张光道+3"（升级改加成，原+2）。
9. 光道天使 基路伯：主目标伤害改4点×3段（敲后4段），溅射6/9不变。
10. 光道少女 密涅瓦：升级从"降挡位"改为"被从卡组弃置时追加抽1张牌"（挡位不再降低）。
11. 光道德鲁伊 奥库斯：0费（1→0）+追加「消耗」。
12. 光道圣灵 夏尔：格挡5/7（原10/14）。
13. 妖精传姬-白雪 雪之化身：弃牌堆≥7张才能打出（必须消耗7张），稀有度Token→金卡。
14. 裁决之龙：稀有度金→蓝。
15. 神光之龙：去掉"消耗堆光道+5伤害"与获得能力「神光回响」两部分；基础伤害固定60；敲后获得「保留」。ShiningDragonPower 类已删除（配套 powers.json 条目已清）。
16. 暮光道萨满 露米娜丝：去掉10格挡；升级改为拿取数1→2（原敲后0费作废）。
17. 光道防护罩：稀有度改基础卡（与简一起，不再从奖励/商店获取）。

**影依系（Cards5-8/LsUtil/ShaddollBase）**：
  
18\. 救影依-神数纳迦：1费（0→1）、获得6格挡。此前本地化写了8格挡但代码漏了GainBlock——本批一并补上并按用户要求改6。
  
19\. 影依巫女 艾莉娅儿：敲后不再加格挡；升级=被弃置时"每消耗1张牌随机敌人获得1层虚弱"（基础=1层虚弱不变）。
  
**两个bug修复**：①打出锁改用**卡牌实例**键控——原 ModelId（卡名）键控导致巫女锁1张神影依后"融的同名神影依也被连坐不能打出"，且回合过期判定只在加锁时执行=旧锁永不失效；②融合Token消耗语义回（改）订为最终版：**离开弃牌堆（回手牌/回卡组）都消耗 + 任何来源"回卡组"都消耗**（原先只拦"弃牌堆→抽牌堆"，"从消耗堆回卡组"会漏=巫女bug）+ 被效果从消耗堆加入手牌保留；删除"第2次打出时消耗"（ShaddollToken 实例计数）。card_keywords 两词条已同步。
  
20\. 虚影依 神子晶：伤害6/9；升级同时为影融+（产出强化版，引擎自动）。
  
21\. 影依猎犬：稀有度蓝→白。
  
22\. 影依猎鹰：被弃置格挡5/7（原9/12）。
  
23\. 圣影依 商神杖灵重做：**1费技能**——和手牌另一张影依卡影融出拿非利（有另一张影依+拿非利未生成才可打出；素材弃置照常触发被弃置时）；敲后=影融+（强化版拿非利）；被弃置时改为"丢弃1张影依攻击牌→对随机1名敌人造成其伤害"（原活力效果删除）。保留"素材时充当拿非利光道位"。
  
24\. 影依融合/神影依融合/魂影依融合：均1费。影依融合敲后=**仅精英/Boss战**可从卡组选素材（当前房间 RoomType 判定）。
  
另修朋友反馈bug：**米沙赫雷恶素材收紧为"3张手牌"**（素材须全部来自手牌）——从卡组选的素材不能凑数。
  
25\. 神影依融合敲后不减费（升级=影融+，由引擎自动产出强化版）。
  
26\. 心影依融合敲后从"选牌张数+1"改为0费（仍选1张）。
  
27\. 影依的伪典改**能力**（新能力 ShaddollSchismPower）：每回合开始可以消耗弃牌堆2张「影依」牌发动一次影融（0~2可选=可不发动；DiscardExhaust 模式；引擎新增 `ShaddollFusionFromPower` 无触发卡入口）。
  
28\. 影依的原核重做：1费技能=8格挡（去掉"丢影融卡触发影融"部分）；**作为影融素材时本次影融可融合任意神影依**（引擎 `WithCoreRule`：组合含原核→豁免条件"任意2张含≥1影依"）；敲后=影融+（素材为强化版原核时产出强化版神影依）；被弃置效果不变。
  
29\. 联结之影依化身重做：1费——消耗弃牌堆1张影依（没有则不产生效果），从弃牌堆或消耗堆将1张影依攻击卡加入手牌；敲后加入手牌的卡0费（原"伤害置0一次"机制从该卡移除，ZeroDamageOnce 余3处：心影依/文蒂/神子晶）。
  
30\. 神影依·拿非利：去掉清除格挡；**对Boss伤害翻倍**（当前房间 RoomType.Boss 判定）。
  
31\. 神影依·米德拉什：回费3→2。
  
32\. 珠泪融合卡：鲁莎卡格挡固定5（去掉"每打出1张珠泪卡+2格挡"计数）；卡雷多哈特重做=打15+**消耗**+在消耗区时每回合开始自动打出（原版 Bombardment 范式：`AfterAutoPrePlayPhaseEnteredEarly` + `CardCmd.AutoPlay`；原弃珠泪/荆棘效果删除）。

**新卡2张（问题25）**：
  
33\. 壹世坏·为珠泪哀歌族奏起的哀唱（1费技能·单体）：从卡组将1张珠泪卡送去墓地（走 MillSelected，弃置钩子照常触发——珠泪融合可由此发动），给目标敌人1层易伤。【AI拍板：敲后易伤2】
  
34\. 壹世坏·向珠泪哀歌族劈斩的弦声（1费能力）：每回合开始时弃光3（能力来源弃光：不触发光道的连锁，珍妮丝/破坏之光/暮光照常）。【AI拍板：敲后弃光4】
  
两张均**不打珠泪标**（同珍珠世界，不计"打出珠泪卡"）；卡图=YGO 74920585/6767771（tools\make_primeval_cards_art.py）；能力图标=卡图圆形裁切。

**AI拍板/歧义决策（待用户确认，如有出入下轮修正）**：
  
① #10"虚影依伤害改为6/9"与#31"虚影依敲后不增加数值，改为影融+"字面冲突——采用6/9（显式数值优先），升级同时为影融+。
  
② 光道天使"4x3/4x4"按"主目标4伤×3/4段"落地，溅射按"未提及=不动"保留并参与升级。
  
③ 新卡2张的升级数值与稀有度（均蓝卡）为AI拍板。
  
④ 米沙赫雷恶修复=素材须全部来自手牌（"3张手牌"字面）；如需干脆禁止卡组模式选它请指出。
  
⑤ 暮光道萨满升级=拿取数1→2（顺带撤掉原"敲后0费"）；贼猫升级=X+1（行为型）。

**验证**：v0.4.32 构建部署，日志加载零异常（Version=0.4.32.0 + Lightsworn mod initialized!）；卡牌图鉴重跑（104张，含2新卡；SnowSpirit 移入金卡组）。

---

## v1.31 第三十八轮订正三条（2026-10-12，v0.4.33，用户验收反馈）

1. **虚影依 神子晶敲后也是6**（#10"6/9"的9作废）：伤害固定6（升级不再+3），升级=影融+（产出强化版，引擎按触发卡已升级自动处理）。
2. **光道天使 基路伯**：改为**对所有敌人**造成4点伤害×3次（敲后×4次），**删除溅射部分**（目标类型 AnyEnemy→AllEnemies；升级=攻击次数3→4）。
3. **升级文案条件化**：敲前文本不再出现"强化后xxx"字样——影依融合（"处于精英战或Boss战时…"改为 {IfUpgraded:show:…|} 仅强化后显示）、炼狱的乖放（"加入手牌的2张牌费用变为0"同上）；裁决之龙/雷喵/闪光之幻想等原本就是升级后才显示，无改动。**gen_card_doc 的 render() 同步支持 {IfUpgraded:show:A|B}**（基础取B、强化取A，B缺省=空——图鉴不再显示字面占位符，该脚本既有局限已消除）。

**验证**：v0.4.33 构建部署（部署时用户正在实测 v0.4.32，游戏进程锁定 dll——先关闭游戏再换包），日志零异常（Version=0.4.33.0 + initialized）；卡牌图鉴重跑。

## v1.32 米沙赫雷恶「素材被吃却融不出」修复 + 素材预筛挡枪修复（2026-10-13，v0.4.35，用户控制台实测+日志实证）

**现象**：使用强化后的影依融合（精英/Boss战），选「手牌猎犬＋打击/防御/光道圣女等任意3张手牌（含≥1影依）」→ 三张手牌被弃置、什么都没发生（不弹神影依选择界面、不生成Token）。用户控制台实测日志实锤：picked n=3 → discard 手牌3张 → available=[] → abort。朋友此前反馈的「融合了手牌中的影依猎犬、打击、防御，结果没有获得米沙赫雷恶」即此（与生成锁无关——融合图鉴确认未锁）。

**根因**：v0.4.32 给米沙赫雷恶收紧的「素材须全部来自手牌」条件含牌堆判定（c.Pile?.Type == PileType.Hand），而引擎在流程里判定【两次】：第一次在弃置素材前（素材在手牌→成立→放行并弃置），第二次在弃置素材后（素材已进弃牌堆→必然不成立）→ 可用神影依列表为空 → 静默中止，此时素材已被消耗。⇒ v0.4.32 起米沙赫雷恶实际完全融不出；从卡组选的组合因第一次判定就失败、素材无损（收紧本身按预期拦截）。

**修复**（LsUtil.cs）：两个素材来源分支的可用神影依列表 available 改为在素材移动（弃置/消耗）之前判定一次并复用（弃置后不再重新判定）。**另修**：素材候选预筛 ValidMaterialCandidates 原实现每张融合卡只标记「第一个命中的组合」（break），同样能参与融合的牌会被别的牌挡枪而在选材界面选不了（用户实测：加进手牌的打击不可选）——改为遍历全部命中组合标记。诊断日志（[LsShaddoll] FUSION 前缀，v0.4.34 加入）保留。

**验证**：v0.4.35 构建部署（dll 哈希与 dist 一致、含 Version=0.4.35.0）；待用户复测：手牌三人组→直接入手米沙赫雷恶；卡组素材混选→弃置前拦截、素材无损。

---

## v1.33 三条稀有度/升级调整（2026-10-13，v0.4.36，用户点名）

1. **妖精传姬-白雪**：稀有度 Uncommon→Rare（金卡）。衍生Token「雪之化身」此前已是金卡展示，本次为白雪本体入金卡池。
2. **光道祭司 珍妮丝**：稀有度 Common→Uncommon（蓝卡）。数值/效果无改动（5/敲后8格挡+同额随机敌人伤害）。
3. **光道召唤师 露米娜丝**：升级重做——**敲前拿1张、敲后拿2张，升级不再变为0费**（原"费用1→0"作废，升级后仍1费；与暮光道萨满同范式）。基础拿取数 2→1（`Picks` DynamicVar 1m；OnUpgrade=UpgradeValueBy(1)）。被拿取牌的"本回合费用为0"保留不变（用户字面"不再变为0费"指升级后卡牌自身费用，非被拿的牌）。

**验证**：v0.4.36 构建部署（dist 与游戏目录三件套哈希一致；部署前先关闭用户实测中的游戏进程），日志零异常（Version=0.4.36.0 + Lightsworn mod initialized!）；卡牌图鉴重跑，三张卡显示已核对（珍妮丝"非普通"、白雪"稀有"、露米娜丝"敲后拿2、升级变化：拿取数1→2"）。

---

## v1.34 珠泪融合素材预筛修复 + 影依的伪典升级订正（2026-10-13，v0.4.37，用户/朋友反馈）

**① 珠泪融合「选不了雷诺哈特」修复**（朋友实测）：弃牌堆有雷诺哈特+鲁莎卡人鱼，弃置一张珠泪触发珠泪融合，结果选材界面里雷诺哈特不可选、卡雷多哈特融不出。根因=LsUtil.TearFusion 的素材候选预筛只测「触发卡+单张候选」两卡组合：卡雷多哈特条件为 3 张素材（`m.Count(IsTearAttack)==3` 且含雷诺哈特），两卡列表恒不命中——当本回合已生成过 Kitkallos（生成锁挡住其两卡组合）时，雷诺哈特没有任何可用组合为其背书 → 在候选预筛中被挡枪、界面选不了。**与 v0.4.35 影融「打击不可选」同族（预筛挡枪）**，但机制不同：影融是 break 只标首个命中组合，珠泪是组合长度只枚举到两卡。修复：预筛改为枚举「触发卡+1张」「触发卡+2张」的全部组合（触发卡必须参与——问题8），命中组合的所有牌都标记；顺带：融合卡选择与手牌空间判定前移到素材移动之前（取消选择/手牌满不再白吃素材）；新增 **[LsTear] FUSION** 诊断日志（触发卡/素材池/候选/逐处中止原因）。

**② 影依的伪典升级订正**（用户口径）：**敲后费用保持1费**（原 v0.4.32 定的"费用1→0"作废），**升级=影融+**——打出的是强化版能力 `ShaddollSchismPowerPlus`（GarothPowerPlus 同款子类范式：基类加 `virtual OnTurnStartFusion`，强化版重写为 `ShaddollFusionFromPower(forceUpgraded:true)`），回合开始的影融产出强化版神影依；卡面描述"影融"后加 `{IfUpgraded:show:+（本次产出强化版神影依）|}`（敲前不显示）。能力词条 powers.json 新增 ShaddollSchismPowerPlus 三键（标题同基础版，同 GarothPowerPlus 惯例）。

**验证**：v0.4.37 构建部署（dist 与游戏目录三件套 md5 一致），日志零异常（Version=0.4.37.0 + Lightsworn mod initialized!）；卡牌图鉴重跑（伪典显示"1费"、敲后"影融+（本次产出强化版神影依）"）。待用户/朋友复测：弃牌堆鲁莎卡+雷诺哈特+任意珠泪触发→三张同选可融卡雷多哈特（Kitkallos 本回合已生成也不影响）；强化伪典回合开始的影融产出强化版神影依。

---

## v1.35 蛇影依追加「消耗」+ 影依·拿非利1费复查（2026-10-13，v0.4.38，用户点名）

1. **蛇影依 路径灵**：追&#x52A0;**「消耗」**&#x5173;键词（打出后进消耗堆）。「被弃置时：获得1层镀层」不受影响——弃置（手牌/弃光）仍是弃置、照常触发；消耗只是打出后的去向。升级（伤害7→10）**保留消耗**。卡面描述追加「消耗。」（cards.json 与 tools\locfrag\cards_6.json 同改，locfrag 保持同步防止未来重合并回退）。
2. **影依·拿非利 1费复查**（用户口径"确认敲后也是1费"）：基础与敲后均为 **1费**——升级只改"被弃置回手门槛 Recall 2→1"，OnUpgrade 无费用改动。**双证**：①源码 Cards6.cs `base(1, …)`；②部署版 v0.4.37 dll ILSpy 反编译核对（构造 `base(1, …)`、`OnUpgrade` 仅 `Recall.UpgradeValueBy(-1)`）。用户看到的 0费 系朋友机上旧版本（v0.4.30"0费→1费"之前的包）。**无改动**。

**验证**：v0.4.38 构建部署（dist 与游戏目录三件套 md5 一致），日志零异常（Version=0.4.38.0 + Lightsworn mod initialized!）；卡牌图鉴重跑——蛇影依条目= `攻击 · 非普通 · 1费 · 目标：单体 · 「消耗」`，敲前/敲后描述均含"消耗。"。

---

## v1.36 第四十轮反馈39条（2026-10-13，v0.4.39，design\已知问题.txt 下发）

### 一、数值与费用微调（歧义处理原则=字面优先；"X/Y"=基础/强化；未提及的既有升级保留）

| #  | 卡                         | 改动                                                                      |
| -- | ------------------------- | ----------------------------------------------------------------------- |
| 1  | 神影依·米德拉什                  | 回费回调 2→**3**（v0.4.32 的 3→2 作废）                                          |
| 4  | 光道武僧 艾琳 / 光道暗杀者 莱登 / 影依猎犬 | 伤害各 +1：艾琳 8→**9**/12（敲+3）、莱登 8→**9**/13（敲+4）、猎犬 7→**8**（升级=Next+1，伤害不变） |
| 5  | 影依蜥蜴                      | 伤害 **8/10**（敲+2）；**敲后虚弱 1→2 层**（新增 Weak 变量）                             |
| 6  | 珠泪哀歌族 梅洛人鱼                | 伤害 6→**7**、格挡 4→**5**（升级纯珠泪融合型，数值两态通用）                                  |
| 8  | 影依兽                       | 伤害 **15/20**（敲+5）                                                       |
| 9  | 救影依-神数纳迦                  | 格挡 6→**8/10**（敲+2）；弃光升级（1→2）保留                                          |
| 13 | 光道德鲁伊 奥库斯                 | **敲后 2 层人工制品**（新增 Artifact 变量 1→2）；弃光升级（2→3）保留                          |
| 14 | 虚影依 神子晶                   | 伤害 6→**8**（升级=影融+ 行为型，两态均 8）                                            |
| 15 | 真血公                       | **敲后伤害 20**（新增 Damage 升级 +2）；弃光升级（4→6）保留                                |
| 18 | 暗之进军                      | 费用 1→**0**                                                              |
| 19 | 光道恶魔 魏丝                   | 费用 1→**0**                                                              |
| 20 | 光道魔术师 丽拉 / 暮光道巫师 丽拉       | **敲后虚弱 2 层**（新增 Weak 变量 1→2）；原削力量升级保留                                   |
| 21 | 光道圣灵 夏尔                   | 格挡 5→**8/10**（敲+2）；每张光道 +1 保留                                           |
| 25 | 影牢之咒缚                     | 费用 1→**2**（升级=固有 不变）                                                    |
| 30 | 壹世坏·弦声                    | **敲后改为固有（Innate），不再加弃光**（原 3→4 作废）                                      |

### 二、重做/机制类

1. **光道天使 基路伯 多段伤害不吃活力的 bug 修复**（用户实测：只有第一段吃活力）：根因=原实现逐段 `DamageCmd.Attack(...).Execute()`，每段是独立 AttackCommand，而原版 VigorPower 的 BeforeAttack 只认第一个命令、AfterAttack 后层数清零（源码实证）→改为**原生多段攻击** `.TargetingAllOpponents(CombatState).WithHitCount(Hits)`：单个 AttackCommand 内部循环，BeforeAttack/AfterAttack 只包一次，全部段落吃活力。**通用教训：mod 里任何"同一张卡打多段"都必须用 WithHitCount，不要手写 for 循环逐段 Execute**（神光之龙同步改）。
2. **联结之影依化身**：去掉"消耗弃牌堆1张影依"的代价部分，直接"从弃牌堆或消耗堆将1张影依攻击卡加入手牌（敲后费用0）"。
3. **小美人鱼**：触发条件反转——**目标意图为攻击时**回1费并弃光3（原"不为攻击"作废）；伤害 **6/9**（新增数值升级 +3，珠泪融合强化副产物照常）。
4. **闪光之幻想**（升金）：弃光2→**3**；格挡改为**造成伤害**（数值公式不变=所选牌基础伤害+0/敲后3，单体）；**斩杀时额外获得一次卡牌奖励**——照原版 TheHunt 范式：`CombatRoom.AddExtraReward(Owner, new CardReward(CardCreationOptions.ForRoom(...), 3, Owner))`，附 TheHunt 同款 `ShouldOwnerDeathTriggerFatal` 判定（爪牙死亡不算）。
5. **影依巫女 艾莉娅儿**：被弃置效果重做=**消耗至多{Max}张**（基础1/敲后2，新增 Max 变量）、**每消耗1张牌随机1名敌人获得1层虚弱**、文本统一（原"基础1层固定/敲后按数量"作废）；**拿回来的影依卡改为可以打出但伤害为0**（`LsUtil.ZeroDamageOnce`，打出一次后恢复）——原"本回合不能打出"的实例锁作废（锁机制代码保留备用）。
6. **绊影依-神数原核**：被弃置效果改为**弃光4**（原"获得6点格挡"作废；用户描述"放1张影依到牌堆顶"与部署 dll 不符——ILSpy 反编译核对为 GainBlock 6，按指令直接改弃光4）。
7. **光道的裁决**：生成的裁决之龙Token **「虚无」改「保留」**（CreateToken 新增 retain 参数；回合结束不弃置，可留到下回合）。
8. **剑神官 姆多拉 / 宿神像 凯尔多**：抽到对应牌（攻击/技能）的降费改为**本次费用变为0**（`SetUntilPlayed(0)`；原 `AddUntilPlayed(-1, reduceOnly)` 作废）。
9. **光之放逐**：施加 **2层虚弱+2层易伤**（敲后各3，新增 Vul 变量）；**强制弃光道**=手牌无「光道」牌时不可打出（IsPlayable 门禁）+打出时强制弃1张手牌光道（仅1张光道时直接弃，免选）。
10. **壹世坏·哀唱**：追加**被弃置时（弃光/手牌弃置）从卡组将1张珠泪攻击牌加入手牌**（LsCard 双钩子，LsUtil.PickFromDraw 检索）。
11. **神光之龙**：伤害 60 → **22×3**（敲后 **26×3**，Damage +4 保留「保留」升级；原生多段攻击同第2条）。
12. **除光机制重做**（LsUtil.Banish）：从"抽牌堆顶N张"改为**从抽牌堆自选N张消耗**（MultiPileCardSelect 界面；不足N张时全部消耗、无选择界面）。card_keywords.json 词条同步。影响：暗之进军、黄昏之双龙的被弃置联动。
13. **黄昏之双龙**：生成的裁决/惩戒**去掉虚无**；**敲后不再增加除光**（固定4，原4→6 作废）；**敲后生成的牌获得「保留」**。
14. **光道埃癸斯盾 = 光道防护罩的先古版**（用户拍板）：类重做为 1费 技能、弃光4、**15/20 格挡**、**被弃置（弃光）时自动加入手牌且费用变0**（细剑同款弃光回手钩子）；稀有度 Ancient。**获取途径=古老牙齿**：`Barrier : ITranscendenceCard`（BaseLib Abstracts）——`ArchaicToothTranscendenceUpgradesPatch` 自动收集 mod 卡映射（防护罩→埃癸斯盾），古老牙齿从卡组把防护罩转化（升级态保留）；因进 TranscendenceCards，达弗尘封魔典不会给到（原版规则）；「你必须玩游戏王」生成池只收白/蓝/金，不受影响。**v0.4.13 的"防护罩先古版是死卡"作废**。
15. **光之回弹**（升金）：效果改为**原埃癸斯盾的效果**=每当你打出「光道」牌，获得 **2/3** 点格挡（原"每次弃牌→灾厄3/4"作废；AegisPower 类删除、效果并入 LightBouncePower）。
16. **古尖兵 凯尔柏克 / 古卫兵 阿基多**（升金）：满足条件（弃光中有2张以上攻击/技能牌）后**改为抽2张牌**（原伤害7/10、格挡6/9 作废）；**追加"被弃置时自动打出"**（弃光/手牌弃置均触发，`LsUtil.AutoPlayOnDiscard`=CardCmd.AutoPlay，卡雷多哈特同款；打出不触发）。
17. **光道战士 加洛斯**（升金）：**敲后效果改到敲前**——基础=「光道」牌弃光后追加弃光2**并抽其中「光道」牌数量的牌**（原强化版效果）；**敲后=触发条件放宽为任意弃光都触发，不限制光道**（不限来源：能力弃光、非光道牌弃光等全部触发）。实现：`LsUtil.MillCore(garothAny:)` 每次弃光后通知 `GarothPower.OnAnyMill`（强化版响应、基础版空操作）；强化版 `OnLightswornMilled` 置空防双重触发；**载荷追加弃光关掉 any 通知防递归**（garothAny:false）。
18. **光道龙 格拉古尼斯**（升金）：追加**斩杀时（DamageResult.WasTargetKilled）自动回手、费用临时变为0**（手牌满不回）。
19. **正义世界**（升金）：改为 **3费能力**——**每当弃光，可以将弃置的牌中的1张加入手牌**（0~1可选，LsUtil.MillCore 每次弃光事件通知）；**敲后：加入手牌的牌获得「保留」**（JusticeWorldPower/Plus 子类，GrantsRetain）。原"每次弃牌获得活力3/4"作废。
20. **神我影依流世**（升金）：改为 **2费能力**（敲后**1费**）——每回合开始时**可以（0~1可选）从消耗堆将1张「影依」牌加入手牌**（PurushaddollAeonPower，AfterPlayerTurnStartEarly 同神域）。原"弃手牌影依换格挡"技能作废。
21. **新卡「壹世坏·让珠泪哀歌族澄澈的残响」**（金卡2费技能，原型=YGO 1329620）：**击晕目标敌人**（眩晕=原版先古卡「吹哨」施加的 `CreatureCmd.Stun`）、**消耗**；**被弃置时（弃光/手牌弃置）从消耗堆选1张珠泪攻击牌，生成一张相同的卡加入手牌**（`CardModel.CreateClone`=升级状态/关键词完整复制，原版双重施法范式）。不打珠泪标（同哀唱/弦声/珍珠世界）。卡图=tools\make_primeval_cards_art.py（ygopro 1329620 裁切）+能力图标管线同步。
22. **黄昏之交衣**（升金）：效果重做为**弃牌堆中每有1张「光道」牌获得1层暮光**、**消耗**；**敲后去掉消耗**（原"消耗至多4张换格挡"作废；BlockPerBurn/MaxBurn 变量删除）。

### 三、歧义拍板记录（汇报中已列出）

- **29 光之回弹"光道埃癸斯盾的效果"**：埃癸斯盾本批被改为防护罩先古版，"埃癸斯盾的效果"按**原能力版效果**（打出光道牌→获得2/3格挡）移交（数值与升级沿用原案）；若用户原意是别的（如按弃牌触发），下轮订正即可。
- **17"本次变0费"**= SetUntilPlayed(0)（直到打出），与露米娜丝/细剑同族的"0费直到打出"语义。
- **13/20 的"敲后X"**= 在既有升级之上**新增**该升级项（弃光/削力量升级保留）。
- **9/21 的"X/Y"**= 被提及数值的基础/强化两态（格挡 8/10），未提及的升级（弃光+1、每张+1）保留。
- **7 小美人鱼"改成为攻击时触发特效"**= 触发条件反转为"目标意图为攻击时"。
- **12 绊影依**：用户描述（放影依到牌堆顶）与部署 dll（获得6格挡）不符，按指令"改成弃光4"落地。
- **28 古老牙齿**：只为防护罩做映射（打击/防御/圣骑士简无先古版=用户未点名）；防护罩的弃置回手按 mod 惯用的"从卡组被弃置（弃光）时"实现（非任意弃置）。
- **10 闪光之幻想**：仍为技能牌（只改效果与目标类型为单体），未改攻击牌类型。

**验证**：v0.4.39 构建部署（dist 与游戏目录三件套 md5 一致），日志零 Lightsworn 异常（Version=0.4.39.0 + Lightsworn mod initialized!）；pck 内文案抽查（残响/埃癸斯盾/加洛斯能力/除光词条）全部为新版；卡牌图鉴重跑（105张）。**待用户/朋友复测**：古老牙齿转化埃癸斯盾、正义世界每次弃光的拾回UI、加洛斯强化版任意弃光触发、古尖兵被弃置自动打出、闪光之幻想斩杀奖励、残响的复制与击晕。

---

## v1.37 用户订正4条（2026-10-13，v0.4.40，对话直接下发）

1. **正义世界（敲后）订正**："敲后是**正义世界自己**获得保留，不是拿回的牌保留"——OnUpgrade 改为 `AddKeyword(CardKeyword.Retain)`（3费攒费期间回合结束留在手牌，不弃置）；`JusticeWorldPowerPlus`/GrantsRetain 机制整体删除（能力无强化版），powers.json 的 `JUSTICE_WORLD_POWER_PLUS.*` 词条删除；卡面文案去掉"（该牌获得「保留」）"。
2. **残响（PrimevalEcho）补锁**：用户问"从消耗堆拿回的珠泪攻击卡如果是融合的卡，本回合是不是就不能融合对应的怪"——**原实现并不会**（CreateClone 只复制牌，不登记融合生成锁）。已补：拿回的卡是 `TearFusionToken`（融合生成的珠泪攻击Token）时，`LsUtil.LockFusionGeneratedThisTurn` 登记本回合生成锁——本回合不能再融合出对应的融合卡，融合图鉴同步置灰（与"每回合每张1次"锁同源）。卡面描述补充该规则说明。
3. **绊影依-神数原核（ShaddollZefracore）订正重做**：用户澄清本批第12条的原意=①**主动打出时弃光 2→4**（`Mill` 变量 4，升级仍只加伤害+4）；②**被弃置时：由"获得6点格挡"改为"从弃牌堆将1张影依牌置于抽牌堆顶"**（不能选自身——触发时自己在弃牌堆；v0.4.39 先误实现的"被弃置时弃光4"作废）。排查插曲：用户原始描述"放一个影依到牌堆顶"其实就是想要的效果本身，部署 dll 核对显示旧版是 6 格挡（ILSpy 双证）。
4. **埃癸斯盾加强**：加入"被从手牌弃置也能拿回来"——补 `AfterCardDiscarded` 钩子（弃光 Draw→Discard + 手牌弃置都回手且本回合0费，"类似影依的被弃置时"双钩子范式）；卡面文案去掉"从卡组"。**机制核查**：回合结束的手牌清理走 `CardPileCmd.Add + Hook.AfterFlush`，**不触发 AfterCardDiscarded**（CombatManager.FlushPlayerHand 源码实证）——不会每回合自动回手。

**验证**：v0.4.40 构建部署（dist 与游戏目录三件套 md5 一致），日志零 Lightsworn 异常（Version=0.4.40.0 + Lightsworn mod initialized!）；图鉴重跑（105张）。

---

## v1.38 埃癸斯盾卡图重裁（2026-10-13，v0.4.41，用户点名）

用户反馈"卡图变形"。排查：从部署 pck 解出旧纹理（pck list `.godot/imported/Aegis.png-*.ctex` → `tools\pck.py extract` → `tools\ctex.py` 解码）与源卡逐像素比对——旧图**横向拉宽**（脸/法杖/光球都偏胖，与源图比例不符；推测为早期手工/旧脚本产物，非标准裁切管线）。
  
修复：`tools\make_aegis_art.py`（新）按标准管线重裁——ygopro 25218587「光道埃癸斯盾」400×580 → 插画区 x44..357、y101..414 取 313×238（25:19，比例与 250×190 一致）垂直居中 → resize 250×190。**注意：卡图窗口与裁切比例必须一致（313/238≈250/190），比例不符=拉伸变形**。
  
验证：重导入（Godot --headless --import）→ ExportPck；部署后从新 pck 解出纹理与本地文件逐像素比对 **0 diff（md5 相同）**；游戏加载 Version=0.4.41.0、零 Lightsworn 异常。

---

## v1.39 先古卡全框卡图修复（2026-10-13，v0.4.42，用户点名）

**真因**（用户提示"先古卡卡图是全框的、有单独比例"后实证）：对 `CardRarity.Ancient` 的卡，NCard 用独立的 **%AncientPortrait** 渲染（`scenes/cards/card.tscn`：全卡锚点 rect 598×842、scale 0.5 → 显示 299×421、**STRETCH_SCALE 拉伸铺满**），卡图**不是常规的 250×190 竖窗**。从游戏 pck 解出官方先古卡纹理实测（`.godot/imported/corruption.png-*.ctex`、`whistle.png-*.ctex` → `tools\ctex.py` 解码）：**官方规格 = 606×852**（≈0.711 全卡比例，无缝满幅）。v0.4.41 那张 250×190 的埃癸斯盾在 299×421 的框里被横向拉宽——这就是"变形"的真因（我 v0.4.41 误判为旧图问题，实际比例本身就不对）。
  
**修复**：`tools\make_ancient_cards_art.py`（新）——两张先古卡（光道埃癸斯盾 25218587 / 破坏之光 83027236）YGO 插画区（边缘亮度采样实测内沿：左50/右350/顶106-107/底408，避开卡框内沿灰条）→ 等比放大到高 852 → 居中裁 606 宽（cover：无拉伸，左右各裁约13%）。**破坏之光旧图另有一处问题一并对齐**：原 250×190 只裁了插画上半截（y110-330），本次取全插画。
  
**通用知识（已入手册）**：先古卡（Ancient）卡图规格 = **606×852 全框**（常规卡才是 250×190）；两张先古卡的卡图以后按此重裁。Power 图标（圆形裁切）仍从卡图中心取，不受影响。
  
**验证**：重导入 → ExportPck → 部署；从部署 pck 解出两张纹理与本地 **0 diff（md5 相同）**、尺寸 606×852；日志 Version=0.4.42.0 零 Lightsworn 异常。

---

## v1.40 第四十一轮17条（2026-10-14，v0.4.43，design\已知问题.txt 下发）

1. **光之回弹调蓝**：Rare→Uncommon（效果不变：打出光道牌得2/3格挡）。
2. **影依的炎核 虚梦狱（HelshaddollHollow）重做**：2费攻击打15/20（升级=伤害+5不变）；主动打出的效果改为
     
   **弃光X（X=手牌中不同名「神影依」数量+1）**——原"可以从卡组弃置1张影依攻击卡→施加1层虚弱和易伤"作废；
     
   被弃置时弃光4 保留；加回「弃光」关键词。「神影依」判定=`LsUtil.IsElShaddollToken`（9张ShaddollToken，含翼影依影文蒂）。
3. **莱登（Layden）**："+4伤害"改为**弃光到「光道」牌→在本回合结束前获得2点临时力量**（先结算临时力量再打伤害，
     
   本次攻击也吃加成）。实现=BaseLib `CustomTemporaryPowerModelWrapper<Layden, StrengthPower>`（`LaydenTempStrengthPower`）：
     
   应用原版 StrengthPower、回合结束自动返还；图标/文案走 BaseLib 通用临时力量资源+游戏本体 TEMPORARY_STRENGTH_POWER 文案
     
   （中文=「在本回合结束前获得力量」），标题=卡牌名。升级仍=伤害+4（9/13）。
4. **光道天使 基路伯进白**：Uncommon→Common。
5. **影依兽升蓝**：Common→Uncommon。
6. **绊影依-神数原核（ShaddollZefracore）重做为2费能力·蓝卡**：获得能力「绊影依-神数原核」——**回合开始时从
     
   「影依的炎核 虚梦狱」「虚影依 神子晶」「神影依·神子晶」中随机生成1张加入手牌，其获得「消耗」**；
     
   生成的是神影依（ElShaddollGrysta，ShaddollToken）时**登记融合生成锁**（同残响=本回合不能再融合出该卡、图鉴置灰）；
     
   敲后费用2→1。原"打8/12+弃光4"作废；被弃置时（v0.4.40 订正）"从弃牌堆将1张影依牌置于抽牌堆顶"**保留**。
7. **救影依-神数纳迦（ShaddollZefranaga）重做为2费能力·蓝卡**：回合开始时从「圣影依 商神杖灵」「联结之影依化身」
     
   「影依的伪典」中随机生成1张加入手牌（同上获得「消耗」；三张都不是神影依、不占生成次数）；敲后2→1费。
     
   被弃置时"抽1张牌"保留（同上，未点名删除）。
8. **古尖兵/古卫兵**：条件由"2张以上→抽2"改为**每有3张对应类型牌→抽1**（弃光5/7；技能=阿基多、攻击=凯尔柏克；
     
   向下取整）。"被弃置时自动打出"保留。
9. **雷喵（Rinyan）重做**：0费、升蓝、加「消耗」；**从弃牌堆将最多{Picks}张「光道」牌洗回抽牌堆（自选0~上限），
     
   每有1种不同名的「光道」牌→获得1点费用**；洗回上限2/敲后3。原"洗回→抽X张"作废。
10. **光道龙 格拉古尼斯**：基础伤害18/敲后22（升级由"每张+3"改为**伤害+4**；"弃牌堆每张「光道」+2"保留）。
11. **加洛斯回调初版**：敲前=「光道」牌弃光后**只追加弃光2**；敲后=追加弃光2**并抽其中「光道」牌数量**的牌。
      
    v0.4.39 的"基础=抽牌 / 敲后=任意弃光都触发"整体作废（MillCore 的 OnAnyMill 通知点保留但两级都不响应；
      
    powers.json 双词条同步）。
12. **光道神域降蓝**：Rare→Uncommon。
13. **暮光道将军 简重做+进白**：Uncommon→Common；1费攻击**打9/12**，**可以**（0~1可选）消耗弃牌堆中1张「光道」牌，
      
    若如此做**额外造成5/7点伤害**；获得1层暮光（无条件）。原"消耗1张→16伤、没有则整张牌无效"作废。
14. **光道圣灵 夏尔进白**：Uncommon→Common。
15. **羽影依 文蒂**：被弃置效果**改成和打出相同**——回收影依攻击卡之外，同样给"本回合费用为0、伤害为0（打出一次后恢复）"
      
    （原被弃置只回收不加buff）。抽出 `FetchBuff` 私有方法供 OnPlay/OnDiscardedEffect 共用。
16. **黄昏之交衣追加效果**：**被从卡组弃置时（Draw→Discard，任意来源），获得"本回合打出「光道」牌获得2格挡（敲后3）"**
      
    ——新能力 `TwilightGarbPower : LightBouncePower`（继承光之回弹的 AfterCardPlayed；`AfterSideTurnEnd` 自我移除=
      
    "本回合"一次性），图标=卡图圆裁（zefracore/zefranaga/twilightgarb 三套新图标，tools\make_power_icons_v443.py）。
      
    卡面新增 `Guard` 变量（2→3）驱动文案。
17. **卡雷多哈特全局限1次生成**：与文迪戈同款——**本场战斗只能生成1次**（`Locks(combat).BattleLocked`，
      
    RegisterFusionGenerated 内统一登记，WendigoLocked 改名 BattleLocked）；图鉴置灰同步；卡面加"[gold]本场战斗[/gold]此牌只能生成1次。"

**实现细节/拍板点**：

- 新能力 `ShaddollZefracorePower`/`ShaddollZefranagaPower`（Powers.cs；AfterPlayerTurnStartEarly，流世同款）：随机生成走
    
  `LsUtil.GenerateRandomToHand`（玩家侧 RNG `RunState.Rng.CombatCardSelection.NextItem` → `combat.CreateCard(概念卡, player)`
    
  → AddKeyword(Exhaust) → ShaddollToken 时 `LockFusionGeneratedThisTurn` → AddGeneratedCardToCombat(Hand)）。
- 炎核的"弃光X"在**造成伤害之后**结算（保留原顺序）；X 动态、卡面写死"X=手牌中不同名「神影依」的数量+1"（不进动态变量）。
- 莱登的临时力量在**攻击前**施加（本次攻击也受益）。
- 雷喵"回墓地x张光道"=从弃牌堆洗回**抽牌堆**（原卡定位"墓地光道回卡组"不变，仅地址词按用户说法"回墓地"）；能量按
    
  **所选牌的不同名数**给（1种=1费）。
- 交衣的"被从卡组弃置时"=Draw→Discard 任意来源（mod 惯用），非限光道卡来源。
- 绊影依/救影依的「被弃置时」效果按既有设计**保留**（用户未点名删除；绊影依的为 v0.4.40 用户点名订正）。
- 图鉴 gen_card_doc.py：VAR_LABEL 补 Guard/Temp；SPECIAL 表同步 Garoth/KaleidoHeart/Rinyan/TwilightGarb +
    
  新增 ShaddollZefranaga 条目；tools\locfrag\cards_6/7.json **全量同步**至当前 cards.json（此前有12处陈旧漂移，
    
  防未来重跑合并脚本回退旧文案；tools\sync_locfrag.py）。
- 三张新能力图标（zefracore/zefranaga/twilightgarb 64/256）=卡图中心圆裁（make_power_icons_v443.py）。

**验证**：v0.4.43 构建（0错误）→ 新 PNG 先 Godot --headless --import → ExportPck（pck 20,466,604B）→
  
dist 三件套 md5 与游戏目录一致 → 启动游戏日志 `Version=0.4.43.0` + `Lightsworn mod initialized!` 零 Lightsworn 异常；
  
从部署 pck 解出 cards/powers.json 抽查（炎核/雷喵/交衣/加洛斯/绊影依/救影依）全部为新版；卡牌图鉴重跑（105张）。
  
**待用户/朋友复测**：炎核弃光X、莱登临时力量（BaseLib 包装器首次使用）、绊影依/救影依能力随机生成 + 消耗 + 神影依占锁、
  
雷喵0费回费、加洛斯初版双态、暮将军可选消耗、交衣被弃置临时回弹、卡雷多哈特本场限1。

---

## v1.41 用户订正3条（2026-10-14，v0.4.44，对话直接下发）

1. **炎核订正**：v1.40 第2条理解错误——"弃光X"是改在**被弃置时**：`弃光4 → 弃光X（X=手牌中不同名「神影依」的数量+1）`；
     
   主动打出的效果**恢复原样**（造成15/20伤害；可以从卡组弃置1张影依攻击卡，若如此做对目标施加1层虚弱和易伤）。
2. **光道龙订正**：升级**同时**改两项——伤害 18→22 **并且** 每张「光道」+2→+3（v1.40 把 Scale 升级删掉是错的，已恢复；
     
   OnUpgrade = Damage+4 与 Scale+1 并改）。
3. **绊影依/救影依订正**：两张重做卡&#x7684;**「被弃置时」效果整体删除**（绊影依"从弃牌堆将1张影依牌置于抽牌堆顶"、
     
   救影依"抽1张牌"；v1.40 保留的判断作废）。被弃置仍走 ShaddollCard 管线（照常计「影依」弃置事件=咒缚/蠢动/影文蒂联动），
     
   只是不再有效果本身。

**验证**：v0.4.44 构建（0错误）→ ExportPck（pck 20,466,556B）→ dist 与游戏目录三件套 md5 一致
  
（dll cf5274ab…/pck ce97d722…）→ 从部署 pck 解出 cards.json 抽查三条新文案全部到位 → 日志 Version=0.4.44.0

- Lightsworn mod initialized! 零异常；图鉴重跑（炎核恢复原效果+弃光X、两张影依无被弃置段、光道龙 18/22 且每张 2→3）。

---

## v1.42 BaseLib→RitsuLib 迁移 + beta 双版本兼容（2026-10-14，v0.5.0，用户三项任务）

**背景**：用户把游戏切到 beta（0.111.0）并下载 RitsuLib 0.6.7；三项任务：①mod 从 BaseLib 迁移到 RitsuLib；
  
②同一份 dll 同时支持正式版 0.107.1 与 beta 0.111.0；③救影依/绊影依 2费→1费、敲后固有。

**迁移总览**（完整对照表与风险清单见 `design\ritsulib迁移方案.md`）：

- 卡牌/遗物/能力/池/角色/事件基类 → RitsuLib：`ModCardTemplate` / `ModRelicTemplate` / `ModPowerTemplate` /
    
  `TypeList{Card,Relic,Potion}PoolModel` / `ModCharacterTemplate<...>` / `ModEventTemplate`。
- `[Pool(typeof(X))]` → `[RegisterCard(typeof(X))]`（遗物 `[RegisterRelic]`、角色 `[RegisterCharacter]`、
    
  事件 `[RegisterSharedEvent]`；105 张卡 + 3 遗物全量替换，脚本 tools\migrate_bulk_v050.py）。
- 标签（Lightsworn/EarthAngel/Fiendsmith/Tearlaments/Shaddoll）→ `ModCardTagRegistry` 铸造真实 CardTag；
    
  关键词（弃光/除光/暮光/珠泪融合/影融）→ `ModKeywordRegistry` 铸造真实 CardKeyword（id=LIGHTSWORN_KEYWORD\_*，
    
  loc 键=LIGHTSWORN_KEYWORD\_*.title/.description，BeforeCardDescription ≈ 旧 AutoKeywordPosition.Before）。
- 金色卡框：BaseLib ShaderColor → `PoolFrameMaterial`（游戏 hsv.gdshader + h/s/v，移植 BaseLib ShaderUtils）。
- 顶栏融合图鉴按钮：自 patch NTopBar + NButton 子类 → `ModTopBarButtonRegistry.Register("LIGHTSWORN_FUSION_CODEX", spec)`
    
  （保留旧 loc 键；打开界面/watcher 逻辑不变）。
- 古老牙齿：Barrier 上的 `ITranscendenceCard` → `[RegisterArchaicToothTranscendence(typeof(Aegis))]`。
- 金色卡框/临时力量/选牌/能量球的替代：见下"自建三件套"。
- 补丁：Harmony.PatchAll → `RitsuLibFramework.CreatePatcher` + `IPatchMethod`（3 生效 + 1 按设计忽略）。
- **Localization 键全量迁移**（RitsuLib 固定条目 = `{MOD}_{CATEGORY}_{TYPENAME}`）：
    
  cards→`LIGHTSWORN_CARD_*`、powers→`LIGHTSWORN_POWER_*`、relics→`LIGHTSWORN_RELIC_*`、
    
  character→`LIGHTSWORN_CHARACTER_LIGHTSWORN_CHARACTER`、event→`LIGHTSWORN_EVENT_PEARL_WORLD_ENCOUNTER`、
    
  关键词→`LIGHTSWORN_KEYWORD_*`、ancients 对白键同步（脚本 tools\migrate_lockeys_v050.py + locfrag 同步迁移）。
    
  card_selection / static_hover_tips 为自建键不动。**旧存档（含进行中 run）因 ModelId 变化不再可用**。
- **双版本兼容层（tools 无关，代码层）**：0.107.1→0.111.0 三处硬签名破坏，全部以反射探测闭合：
    
  ①`AttackCommand.FromCard(card)`→`(card, cardPlay)`（42 处调用点→`LsCompat.FromCardCompat`）；
    
  ②`CreatureCmd.LoseBlock`→需 ctx+remover（艾琳 1 处→`LsCompat.LoseBlockCompat`）；
    
  ③`ModifyDamageMultiplicative` 5参→6参（欧尼斯特：编译期 6 参 override 覆盖 beta；正式版由
    
  `HonestPowerLegacyPatch` 对 5 参基类方法打 postfix 转发，ignoreIfMissing 让 beta 自动跳过）。
    
  其余 130+ 使用点/42 处 override 经双版本源码全量审计**签名一致**（审计脚本留 research\api_audit\）。
- **自建三件套**（RitsuLib 无对应物）：
    
  ①`MultiPileCardSelect` shim（浅封装 `CardSelectCmd.FromSimpleGrid`，签名同旧；**失去牌堆来源角标**）；
    
  ②能量球 `LightswornEnergyCounterPatch`（patch `NEnergyCounter.Create`，纯 C# 建节点树，移植 BaseLib FromLegacy
    
  精简版）+ 描边色补丁；③欧尼斯特正式版 postfix（见上）。
- 构建：csproj Import `RitsuLib.References.props`（`RitsuLibReferenceTarget=0.111.0`），删 BaseLib 引用；
    
  清单依赖改 `STS2-RitsuLib >= 0.6.7`；min_game_version 保持 0.107.1。

**③救影依/绊影依**：基础费用 2→1；敲后由"费用-1"改为**获得「固有」**（`OnUpgrade → AddKeyword(CardKeyword.Innate)`，
  
升级预览/卡面关键词行自动显示）。

**验证（beta 0.111.0 实机）**：构建 0 错 0 警 → ExportPck → robocopy /MIR /IS /IT → 启动：
  
`RitsuLib 0.6.7 [compat branch: 0.111.0]` 加载、5 标签/5 关键词铸造成功、顶栏按钮注册、
  
`[AutoRegister] Lightsworn: 111 operations, 111 succeeded, 0 failed`（105卡+3遗物+角色+事件+池）、
  
3 补丁生效 + 1 按设计忽略（honest_107）、日志零异常。图鉴重跑 105 张。
  
**正式版（0.107.1）无法本机实测**（Steam 只装了 beta 一份）——以"三处破坏点反射闭合 + 其余审计安全"背书；
  
正式版上线若见 MissingMethodException/TypeLoadException 即漏网（排查入口：本记录 §兼容层 三条）。

## v1.43 联机（多人联机）兼容（2026-10-14，v0.5.1，用户任务「保证联机模式下大家可以一起玩」）

**背景（游戏本体联机架构实证，research\sts2src_0111）**：STS2 联机=主机定序的确定性同步——
  
①握手校验「游戏版本 + gameplay 内容 mod 名单（清单 affects_gameplay=true，条目=id-版本）+ ModelIdSerializationCache.Hash
  
（全部模型/ID/属性名的全局哈希）」；②战斗为全端本地确定性模拟，每次行动结束/回合节点/事件退出各方上报
  
NetFullCombatState 的 XxHash32 校验和（含全部生物 HP/能力、玩家能量/金币、5 个战斗牌堆、RNG 集、
  
nextChoiceIds（玩家选择ID向量）、hook id），主机比对不一致→StateDivergence→断线弃局（无重同步）；
  
③玩家选择=PlayerChoiceSynchronizer 按玩家槽位自增 ID 同步（ReserveChoiceId 全端同点、本地 UI+SyncLocalChoice /
  
远端 WaitForRemoteChoice），选择 ID 向量进校验和；④行动同步 ActionQueueSynchronizer（hook 动作按自增 id 全端对齐）。
  
**结论：mod 内容只要全端同版本安装且行为确定（同输入同代码路径），即可联机；本 mod 的 gameplay 声明正确
  
（affects_gameplay=true，RitsuLib 内容注册哈希由 RitsuLib 确定性重建保障）。**

### 修复（三处，v0.5.1）

1. **玩家级钩子的 Owner 过滤缺失**（联机同角色时串效果/串弃牌）——`AfterPlayerTurnStartEarly` 是"每个玩家的回合
     
   开始各触发一轮"、`AfterCardPlayed` 是全场广播、卡牌钩子对所有玩家的牌触发，本体**不做 Owner 过滤**（过滤责任在模型）：
   - `Powers.cs`：SanctuaryPower/JanicePower/PrimevalScreamPower/ShaddollSchismPower/PurushaddollAeonPower/
       
     ShaddollZefracorePower/ShaddollZefranagaPower 的 `AfterPlayerTurnStartEarly` 加 `player != Owner.Player return`；
       
     LightBouncePower/HonestPower/ShaddollHoundPower 的 `AfterCardPlayed` 加 `cardPlay.Player != Owner.Player return`
       
     （照本体 StampedePower/HellraiserPower 范式）。
   - `LightswornContent.cs`：LightswornSigil.AfterPlayerTurnStartEarly 加 `player != Owner return`（圣徽弃光只在自己回合开始）。
   - 其余钩子（卡牌实例钩子 `card != this`、CatsAndDogs 的 `card.Owner != Owner`、Janice/Hound/TwilightGarb 的
       
     `participants.Contains(Owner)`、卡雷多哈特的 `player == Owner`）原本就正确，未动。
2. **融合生成锁按玩家隔离**（`LsUtil`）——原"每回合每张1次/文迪戈本场1次"锁是**每场战斗全局**（双光道组队互相抢锁、
     
   图鉴被队友的锁置灰）。改为 `FusionLockState` 内三个 `Dictionary<Player, HashSet<ModelId>>`
     
   （TearFusedThisTurn/ShaddollFusedThisTurn/BattleLocked），`RegisterFusionGenerated/IsFusionLocked/IsFusionUsedForCodex/
   CanFuseInto/IsFusionGenerated/LockFusionGeneratedThisTurn` 全部加 player 参数；单机行为不变（单玩家=全局）。
3. **起始遗物二选一的联机一致性**（`StartingRelicChoice.cs`）——原实现"弹窗任务里现场 ReserveChoiceId"：
     
   弹窗（独立任务、非阻塞）+ 队友可能抢先进房/出牌时，选择 ID 预定时点不可控 → ID 向量分叉 → 校验和分歧断线。
     
   改为：**选择 ID 在 FinalizeStartingRelics（StartRun 的 await 段，各端都跑且此刻无人能行动）里按 state.Players
     
   顺序一次性预定**；弹窗任务只做 本地开原版界面+SyncLocalChoice / 远端 WaitForRemoteChoice 配对
     
   （ChooseRelicCompat=RelicChoiceCmd.FromChooseARelicScreen 等价实现，只是 ID 预定时点不同）；
     
   界面异常时也同步一个"跳过"结果（否则对端永远停在 WaitForRemoteChoice）。日志加"已预定 N 个选择 ID（联机=…）"。

### 顺带修复（联机实测中发现的真 bug，非联机特有）

1. **角色语法/代词本地化键缺失 → 涅奥事件房卡死**（0.111 新增古代对话系统按 `{pronounSubject}` 等取词）：
     
   `LIGHTSWORN_CHARACTER_LIGHTSWORN_CHARACTER` 缺 `.titleObject/.pronounSubject/.pronounObject/.pronounPossessive/
   .possessiveAdjective` → `LocTable.GetRawText` 抛 LocException（BaseLib 先打 WARN）→ 事件 SetupLayout 中断 →
     
   选项渲染但不响应（同坑23 家族）。修复=补全 15 键（含 bestiaryQuote/eventDeathPrevention/goldMonologue/
     
   cardsModifierTitle/Description/aromaPrinciple/banter.alive|dead.endTurnPing——endTurnPing=联机回合结束喊话），
     
   并加 `localization\eng\characters.json` 回退拷贝（照 events.json 先例）。

### 验证（实机）

- 单机（beta 0.111.0）：0.5.1 加载零异常；涅奥事件（修复前选项无响应）修复后完整可选并给奖励；起始遗物二选一正常；
    
  融合图鉴 UI 正常。
- **联机（本机双开：官方测试台）**：游戏内置 `multiplayer test` 控制台命令（控制台=反引号键）
    
  → 内建 ENet 直连（host 127.0.0.1:33771 / join netId 1000）；**两个客户端进程各跑一份**
    
  （`tools\wininput.ps1` 提供窗口摆放/截图/点击/按键/拖拽；游戏目录放 `steam_appid.txt`=2868840 才能免 Steam 直启）。
    
  双光道圣女组队实测：握手通过（MODDED(3) / HASH 一致）→ 对局开始 → 起始遗物二选一双方各自弹窗并同步成功
    
  （日志"已预定 2 个选择 ID（联机=True，玩家=1,1000）"）→ 双方均获光道圣徽 → 涅奥事件双方各自选择 →
    
  `fight CULTISTS_NORMAL`（控制台命令 IsNetworked=true 全端同步）进战斗 → 双方画面状态完全一致
    
  （HP 78/78、敌 88/88 与 116/116、能量 3/3、光道圣女立绘、mod 卡手牌）→
    
  **ChecksumTracker 4 次校验和（事件退出 id0 + 回合开始 id1，覆盖双光道回合开始的全部 mod 钩子：
    
  圣徽弃光/补卡组40/所有能力钩子/选择ID向量）全部匹配，日志零 divergence、零 ERROR**。
    
  未覆盖项（合成输入限制）：单张卡打出的 UI 拖拽流程未用自动化验证（代码路径与单机一致；弃牌/融合交互建议
    
  用户与朋友实机复测）。
- **联机使用须知**：所有玩家必须安装**同版本** mod（affects_gameplay=true → 版本不一致握手即 ModMismatch 拒绝；
    
  RitsuLib 亦需安装——依赖声明会强制）；混合队伍（光道+其他角色）可玩：事件「于珍珠世界相逢」按原设计
    
  IsAllowed=全员光道才出现（保留原设计）；选择界面弹出期间全桌等待（无 ctx 钩子里的 Blocking 选择上下文，
    
  与本体同类路径一致）。

### v1.43 补记：本地化修复版换包复测（2026-10-14 晚）

统一本地化修复后重新构建部署（dll d7a5c94a / pck 0b21cb01 / json 0.5.1，dist=游戏 mods=工坊 workspace 三处 md5 一致），
  
**双光道圣女双进程联机第二遍完整复测通过**：握手（MODDED(3)、HASH 一致）→ 开局 → 双方各自起始遗物二选一
  
（日志"已预定 2 个选择 ID（联机=True，玩家=1,1000）"）→ 双方均获光道圣徽 → 涅奥事件双方均正常渲染/可交互
  
（**零缺键警告**）→ 控制台 fight 跳战斗 → 双方画面状态逐项一致（HP 78/78×2、敌 88/88 与 112/112、能量 3/3、手牌相同）
  
→ ChecksumTracker 校验和全匹配、双实例日志零 divergence 零 ERROR。
  
**单机复测**（同版包）：涅奥事件完整可选并结算奖励、起始遗物二选一正常、融合图鉴 UI 正常、日志零异常。
  
证据截图：tools\mp_evidence\（01-08）。

### v1.43 补记2：角色资源修复（2026-10-14 晚，用户目击反馈）

**用户反馈**：「左上角的头像和能量球都变回战士了」（联机实测期间目击）。核查确认属实，**根因=RitsuLib 占位资源继承**：
  
`ModCharacterTemplate.ResolvedAssetProfile` 会把**未覆盖的资源槽从占位角色（PlaceholderCharacterId=ironclad）继承**。

- 左上角角落头像 = `Character.Icon` 场景（`NTopBarPortrait.AddChild(player.Character.Icon)`）——mod 只给了
    
  `CustomIconTexturePath`（顶栏图标贴图，另一槽位），没给 `CustomIconPath`（**图标场景**）→ 继承铁甲的
    
  `ui/character_icons/ironclad_icon.tscn` → 角落头像显示铁甲。
- 能量球：0.5.0 的自建 `NEnergyCounter.Create` 前缀**从未生效**——RitsuLib 自己的同点前缀带 `[HarmonyPriority(800)]`，
    
  先解析到「继承来的铁甲能量球场景」建球并 return false 中止补丁链，mod 前缀（默认优先级 400）跑不到 → 显示铁甲的红色八角球。

**修复**：

1. 新场景 `lightsworn\visuals\saint_icon.tscn`（纯 TextureRect + icon.png，构型照原版 ironclad_icon.tscn）
   - 角色覆写 `CustomIconPath`。
2. 新场景 `lightsworn\visuals\saint_energy_counter.tscn`（镜像原版 ironclad_energy_counter.tscn 的
     
   Layers/RotationLayers/Layer1-5，**去掉 script/material/VFX 实例**——mod 导 pck 不能引游戏脚本）
   - 角色覆写 `CustomEnergyCounterPath`；由 RitsuLib `RitsuNEnergyCounterNodeFactory` 转换建球并自动补齐
       
     %EnergyVfxBack/%EnergyVfxFront/Label/%StarAnchor 槽位。删除 LightswornEnergyCounter.cs 里的自建 build patch
       
     （保留 OutlineColor 描边补丁），Entry 同步取消注册。
3. 实机验证（beta 0.111.0 单机，读档 + 控制台 fight 进战斗）：左上角头像=光道圣女 OK、能量球=圣女金色菱形球+3/3 OK、
     
   日志零 ERROR（仅 "Asset not cached: icon.png" 按需加载的无害警告）。证据图 `tools\mp_evidence\09*.png`。
4. 已同步 dist / 游戏 mods / 工坊 workspace（三处 md5 一致：dll 78ed1271 / pck cad22f81c / json 0.5.1）。

---

## v1.44 珍珠世界事件重做 + 幻色珍珠 + 召唤师/萨满代价判定 + 雪之化身奖励泄漏（2026-10-15，v0.5.2，对话直接下发 5 项）

**任务与改动**（用户 5 条原话 → 实现）：

1. **事件立绘换图**：`Cache_574a0c16ebe486ca.png`（1920×1080，珠泪三姐妹海边）→ 原版事件画布 3440×1613。  
   新素材是 16:9，与目标 2.133:1 接近，改成**顶部裁 180px 后 LANCZOS 直出**（不再模糊延展边条）——  
   脚本 `tools\make_pearl_event_art_v2.py`。产物覆盖 `...\images\events\pearl_world_encounter.png`  
   （文件名不变，`CustomInitialPortraitPath` 不用改；改图后必须 `Godot --headless --import` 再 ExportPck）。
2. **文案人设对调**：梅洛改活泼、小美人鱼改安静（原本相反）。三页全量对调：  
   INITIAL（拍水花质问/捧珍珠眨眼两句互换）、JOIN 结局（唱歌、捞鳞片说"疼的时候就当我们在陪你"两句互换，  
   并给"融合起来吧"补了"梅洛凑过来补了一句"点明说话人）、PEARLS 结局（递珍珠+轻声宽慰的人换成小美人鱼）。  
   zhs 与 eng（回退副本）两份 events.json 同步。
3. **新增事件遗物「幻色珍珠」PhantomPearl**（`LightswornContent.cs`；id=`LIGHTSWORN_RELIC_PHANTOM_PEARL`）：
   - **图标**：游戏 pck 解出原版金色珍珠大图（BPTC ctex 用 Godot 解码：`research\dirtest\extract_pearls.gd`，  
     在 headless Godot 里 `ProjectSettings.load_resource_pack` 游戏 pck 后 `get_image().save_png`），  
     再 HSV 色相重映射成珠泪海蓝（`tools\make_phantom_pearl_icon.py`，灰描边转微蓝）→ 64/256 两档进 `images\relics\`。
   - **效果**（拾起时以 `Owner.PlayerRng.Rewards` 掷一次，确定性同步）：1% → 发光珍珠（原版 RadiantPearl：  
     每场战斗第一回合抽牌时 1 张「冷光」入手，`BeforeHandDraw`+`TurnNumber==1`+Owner 过滤）；其余各 50% →  
     金色珍珠（+150 金）/诅咒珍珠（+1 张「贪婪」+333 金）。掷到的模式 `[SavedProperty] PearlMode` 持久化，  
     描述里 `{Effect}` StringVar 在 setter 里刷新（读档 Fill 走 setter，文本自动恢复）。
   - **事件遗物语义**：`RelicRarity.Event`——RelicGrabBag.Populate 只收 Common/Uncommon/Rare/Shop，Event 档天然  
     不进随机掉落；商店价 999999999。选项二悬停预览用 `HoverTipFactory.FromRelic<PhantomPearl>()`  
     （原版 GraveOfTheForgotten 范式）。
   - **坑**：mod 类型用 `[SavedProperty]` 依赖 RitsuLib 的 `SavedPropertiesTypeCacheInjectionPatch`（0107/0111 都有）；  
     新增带 SavedProperty 的模型会触发 ModelDb 确定性排序 → 联机握手哈希变，两端必须同 mod 版本（工坊更新说明已含此惯例）。
4. **选项二改赠遗物**：`TakePearls` 从 `PlayerCmd.GainGold(100)` 改为 `RelicCmd.Obtain<PhantomPearl>(Owner)`；  
   事件 `CanonicalVars` 的 GoldVar(100) 删除；选项文案改"获得遗物[gold]幻色珍珠[/gold]。"；结局页文案同步点出幻色珍珠。
5. **雪之化身奖励泄漏（真 bug，用户此前反馈过）**：`SnowSpirit` 早前按用户要求从 Token 稀有度改金卡(Rare)后，  
   原版 `CardFactory.CreateForReward` 对 Rare 没有任何令牌保护（只过滤 Basic/Ancient；Token 档靠"卡池不收录令牌"  
   规避，mod 卡却全部挂在 LightswornCardPool 里）→ 会以金卡身份出现在战斗奖励/尘封魔典等。  
   **修复**：`LightswornCardPool.FilterThroughEpochs` 覆写，剔除所有 `ShouldShowInCardLibrary==false` 的战斗专属牌  
   （SnowSpirit/神影依/珠泪融合 Token），即它们从一切"卡池来源"（奖励/事件选牌/商店/变形/随机生成）消失，  
   只保留战斗内效果生成。卡牌图鉴走 `ModelDb.AllCards`，不受影响。
6. **召唤师/萨满"必须付出代价才能发动"**（用户反馈：手牌只有光道召唤师也能发动拿卡回来）：
   - `Lumina`：`IsPlayable` 追加"手牌中除自己外还有牌"（可弃）；`OnPlay` 里没弃成（`chosen.Count==0`）直接 return，  
     拿牌效果不发动（IsPlayable 挡常态 + 运行期双保险）；`ShouldGlowGoldInternal` 同步。
   - `TwilightLumina`：`IsPlayable` 追加"弃牌堆有「光道」牌"（可消耗）；`OnPlay` 里 `ExhaustOneFromDiscard` 返回  
     null 时跳过拿回段（暮光能力照常施加）；`ShouldGlowGoldInternal` 同步。
   - 卡面文案补"手牌中有其他牌时才能打出。"/"弃牌堆中有「光道」牌时才能打出。"（同雪之化身范式）。

**验证（beta 0.107.1 实机，wininput.ps1 驱动 + 控制台）**：

- 编译 0 错误；Godot 重导入 3 张新 PNG；ExportPck 后 dist 与游戏 mods **pck md5 一致（182db22a…）**；  
  日志 `Lightsworn, Version=0.5.2.0` + `Registered relic: PhantomPearl` + 零异常。
- 控制台 `event LIGHTSWORN_EVENT_PEARL_WORLD_ENCOUNTER` 直达 → `Preloading 'Event Room' Complete: assets=2` 无 Failed；  
  **实机截图**：新立绘+对调文案+两选项正常显示；选项二悬停预览=幻色珍珠遗物卡 + 贪婪/冷光关联牌提示；  
  点击选项二 → **掷到诅咒珍珠**（金币 99→432=+333）、左上角遗物栏出现蓝色珍珠图标、遗物悬浮框  
  "当前效果：诅咒珍珠（获得1张贪婪与333金币）"——掷取/持久化/动态文本全链路实机通过。
- 附带发现（非本次改动引入，供后续排查）：涅奥事件交互时 BaseLib 3.4.7（工坊仍装的旧库，MissingLocPatch）  
  会对本 mod 的 21 个能力打印 `GetRawText: Key 'XX_POWER.title' not found in table 'powers'`（旧格式键名），  
  WARN 级、功能无影响；本批未动能力代码。

## v1.45 联机实战四连修：卡牌卡空中 / 能力没名字 / 占位符图标 / 融合失败（2026-10-15，v0.5.3，用户对话下发 + 朋友反馈）

**背景**：用户与朋友用 v0.5.2 联机实战一轮（0.107.1 正式版），事后日志（`godot.log`）与截图暴露 4 个问题：  
「经常有卡牌卡在空中」「能力没名字」「光道暗杀者临时力量图标是占位符」「朋友说满足条件融不出来」。  
排查后 4 个问题分属 **2 类根因**：

### 一、卡牌卡在空中 + 融合失败 = 0.111 专有 API 在 0.107.1 运行时炸（同一根因）

v0.5.0 起的架构决定：**编译对齐 0.111 refs、运行时兼容 0.107.1**（个别差异走 LsCompat 反射）。  
本批日志实证还有 2 处 v0.5.0 迁移清单没覆盖到的差异，且都属于"编译能过、正式版运行时报  
MissingMethodException"：

1. **`CardCmd.Exhaust` 返回类型差异**（本次最大凶手）：参数表两版完全相同，但  
   0.107.1 返回 `Task`、0.111 返回 `Task<CardPileAddResult?>`——**CLR 方法签名含返回类型**，  
   按 0.111 编译出的调用点在 0.107.1 找不到方法。13 处调用点全部命中（弃光/除光/融合/珠泪引擎 +  
   多张卡的消耗），症状=`PlayCardAction … completed with exception` → 卡牌动画停在空中不落地。  
   **朋友的"融不出来"就是这条**：`ShaddollFusionCore`（影依融合引擎）在素材消耗处调 Exhaust → 炸。  
   修复=`LsCompat.ExhaustCompat`（反射按参数表取方法缓存，两版各自命中；返回 Task 供 await）。
2. **`CardPlay.Player` 属性 0.111 才有**（0.107 无此属性）：v0.5.1 联机过滤新增的  
   `cardPlay.Player != Owner.Player` 过滤全数变成运行时炸弹（LightBounce/Honest/ShaddollHound 的  
   AfterCardPlayed），症状=队友打牌时持有这三能力的一方炸（日志里 ShaddollHoundPower 的  
   MissingMethodException 即此）。修复=`LsCompat.CardPlayPlayer`（属性存在则反射取，否则回退  
   `cardPlay.Card.Owner`——语义等价，仅 TheBall 之类"打出后换主"的牌有差别，与本 mod 用途无关）。

**为什么两轮测试都没抓到**：①"试编译（对 0.107 refs）"只能抓"成员不存在/参数表不同"，  
**抓不到"仅返回类型不同"**；②v0.5.1 联机实测是在 0.111 beta 分支上做的。  
**制度性修复（本批建立，见手册 §4）**：

- `tools\memberref_audit`（新工具，System.Reflection.Metadata）：把 mod dll 里指向 sts2 的全部  
  memberref（**含返回类型**逐签名）+ 基类/接口 typeref 与目标 sts2.dll 比对，0.107 与 0.111 两端  
  PASS 才可发布。在旧 v0.5.2 dll 上实测：189 个引用中精确报出上述 2 个坏引用。
- csproj 新增 `LsCompatTrial=true`（试编译开关）：对 0.107 refs 编译时必须定义 `LS_TRIAL_107`  
  屏蔽"只存在于 0.111"的 override（欧尼斯特 6 参）——**csc 的声明级错误（CS0115）会抑制方法体内的  
  绑定错误**，不屏蔽就看不到真实差异（本轮实测教训）。

### 二、能力没名字 = 能力本地化键格式错（短键别名制度）

**实证（日志+控制台+游戏源码三方对齐）**：mod 的**能力**没有走 `[RegisterPower]` 特性注册  
（卡牌走 `[RegisterCard]`），运行时按类型解析，`ModelId.Entry = ModelDb.GetEntry(type) =
StringHelper.Slugify(类名)`——**不带 mod 前缀**（如 `ShaddollHoundPower → SHADDOLL_HOUND_POWER`），  
与卡牌 ID（`LIGHTSWORN_CARD_*`）不同。而 powers.json 的键全是 `LIGHTSWORN_POWER_*`（v0.5.0 迁移时  
按"统一 `{MOD}_{CATEGORY}_{TYPENAME}`"写的）→ `PowerModel.Title/Description/SmartDescription`  
全部取不到 → 能力名字/描述空白（BaseLib 的 MissingLocPatch 只把原始键名当文本兜底）。  
日志实证：一次全能力枚举打出 21 条 `GetRawText: Key 'XX_POWER.title' not found in table 'powers'`；  
控制台 `power LIGHT_BOUNCE_POWER 3 0` 按短名精确命中，`AppliedPower: [PLAYER]`。

**修复**：`tools\update_power_loc_aliases.py`——为 21 个能力各生成一份**去 `LIGHTSWORN_POWER_`  
前缀的短键别名**（`SHADDOLL_HOUND_POWER.title` 等，与原键同值并存，两套机制下都命中）；  
另补齐 `LAYDEN_TEMP_STRENGTH_POWER.description/.smartDescription`（原版 TEMPORARY_STRENGTH_POWER  
中文文案："在本回合结束前获得[blue]{Amount}[/blue]点[gold]力量[/gold]。"——title 由 RitsuLib  
模板走来源卡「光道暗杀者 莱登」的卡名，无需词条）。

### 三、莱登临时力量图标占位符

`LaydenTempStrengthPower : ModTemporaryAppliedPowerTemplate<Layden, StrengthPower>` 类上没有  
AssetProfile → `CustomIconPath=null` → 游戏回退 `res://images/powers/<entry小写>.png`（不存在）  
=占位符。修复=卡图圆裁图标（新脚本 `tools\make_layden_temp_strength_icon.py`：  
`images/cards/Layden.png` 中心方形→圆形蒙版→64/256 两档→`images/powers/laydentempstrength(_big).png`）

- 类上补 `AssetProfile`。新 PNG 走 Godot `--headless --import` 再 ExportPck（坑13）。

### 实机验证（0.107.1，wininput.ps1 + 控制台）

- 战斗内打出 莱登 / 打击×2 / 费莉丝 / 愚蠢的埋葬 / 魂影依融合 全部正常结算，**整局日志 0 ERROR**；
- 欧尼斯特钩子：`power HONEST_POWER 1 0` 后打出攻击 → 层数 1→0（AfterCardPlayed + CardPlayPlayer 生效）；
- 光之回弹钩子：费莉丝打出后格挡 = 7（自身）+3（回弹）=10（触发与加格挡都生效）；
- **融合全链路**：魂影依融合 → 选材（影依巫女艾莉娅+防御）→ 弃置 → 选要生成的神影依（9 候选）  
  → 神影依·神子晶入手牌；日志 `[LsShaddoll] FUSION cast/pool/picked/discard/available/生成` 各步齐全；  
  朋友那局崩的路径（影依怪被弃置触发的 DiscardExhaust 融合）素材消耗同样走通；
- 能力悬浮框：光之回弹=「光之回弹 / 每当你打出「光道」牌，获得3点格挡。」；莱登临时力量=  
  「光道暗杀者 莱登 / 在本回合结束前获得2点力量。」+ 力量关联提示；图标栏第二格=莱登卡图圆裁图标；
- 日志 `not found in table 'powers'` 计数 **0**（修复前 199+）。
- 审计：新 dll 对 0.107.1 与 0.111.0 两端 memberref 审计 **双 PASS**。

### 附带观察（本机无法定位，留观）

- 朋友一局里休息处 SMITH 一次失败（选择结果空、success False）——客户端侧现象，本机日志只见结果空；  
  若复现再查（可能与当时朋友端的崩溃残留有关）。
- 一次 `MapDrawingMessage` 报错（player not in drawing mode）——地图涂鸦消息时序，疑似原版行为，未处理。

### 发布注意

- 本次改了 dll（兼容层）与 pck（本地化/图标）→ 联机两端必须同时升到 v0.5.3（mod 版本握手校验）；  
  朋友端需重新订阅/更新工坊条目。

---

## v1.46 已知问题清单六条修复（2026-10-16，v0.5.4，用户《已知问题》反馈）

**背景**：用户提交 `design\已知问题.txt` 六条反馈，多数来自 mod 用户实机（本地无日志），要求**从代码本身分析定位**。本轮全部定位到根因并修复，逐条如下。

### 问题1：光道龙 格拉古尼斯斩杀时并未变成0费（场景：2层boss帝皇蟹）

**根因（两个叠加缺陷，均在反编译产物中双证据确认）**：

1. **回手本身就失败了**。原实现无条件调 `CardPileCmd.Add(this, PileType.Hand)`，而该 API 在战斗收尾时**静默失败**：
   反编译 `CardPileCmd.Add(IEnumerable<CardModel>, CardPile, ...)` 开头即
   `if (newPile.IsCombatPile && CombatManager.Instance.IsEnding) return ...{success=false}`；
   而 `IsEnding ← IsCombatEnding(turnState)` 的判据是
   `!Enemies.Any(e => e.IsAlive && e.IsPrimaryEnemy)` —— 打死**主敌人**的瞬间即为 true。
   帝皇蟹是 boss=primary enemy，所以击杀后卡**根本没回手**，玩家看到的"没变0费"其实是"连回手都没发生"。
2. **0费时机错误**。原用 `EnergyCost.SetUntilPlayed(0)`，其 `LocalCostModifierExpiration=WhenPlayed`；
   而 `CardModel.OnPlayWrapper` 在 `OnPlay` 返回后**紧接着**执行 `EnergyCost.AfterCardPlayedCleanup()`
   （删除全部 `WhenPlayed` 标记）→ 0费在本次结算末尾就被抹掉。

**修复**（`Cards2.cs` Gragonith.OnPlay）：
- 按 `CardPileAddResult.success` 判定回手是否真的发生，失败则什么都不做（不白给0费标记）。
- 改用原版"击杀手牌"范式 **`CardModel.SetToFreeThisTurn()`**（= `EnergyCost.SetThisTurnOrUntilPlayed(0)`，
  `Expiration=EndOfTurn|WhenPlayed`）：既跨越本次结算的 `WhenPlayed` 清理，又在回合结束时自然失效
  ——与原版"暂时0费"语义一致。原版先例：`CardModel.SetToFreeThisTurn()` 被官方药水/能力复用。

### 问题2：残响敲前敲后效果没变 —— **确认是真 bug，不只是文本问题**

**根因**：`PrimevalEcho` 原先**没有覆写 `OnUpgrade()`**，而基类 `CardModel.OnUpgrade()` 是空实现
（反编译证据：`protected virtual void OnUpgrade() { }`）→ 升级对它**完全无效果**。

**全 mod 排查结论**：把"全部卡类"与"是否定义 OnUpgrade"做差集，只有 3 个命中——
`TearFusionCard`（abstract 基类，非实体卡）、`PurgatoryRelease`（无 OnUpgrade 但其 `OnPlay` 里
`if (IsUpgraded)` 分支生效，功能正常）、`PrimevalEcho`（**唯一真漏**）。

**修复**（`Cards5.cs`）：`protected override void OnUpgrade() => EnergyCost.UpgradeBy(-1);` —— 敲后费用 **2 → 1**。
照本 mod 稀有技能牌既有范式（`FrozenHeartShadow` 心影依融合同款）。**文案不写降费**（官方 1217 张卡中
31 处 `{IfUpgraded:show:}` 涉费用的为 **0** 处；降费由卡面左上角数字自动体现）→ 标注**待用户确认**。

### 问题3：珠泪融合素材向下兼容（选了水仙女+影依会出鲁莎卡人鱼；影融选超素材时无事发生）

**根因A（会出鲁莎卡人鱼）**：`FusionOptions` 里 Rulkallos / KaleidoHeart **缺少素材总数判定**：
```csharp
// 旧：Count(IsTearAttack)==2 && Any(is Kitkallos)   ← 没有 m.Count
```
玩家选「水仙女 + 影依」后 `material`=[触发珠泪攻击牌, 水仙女, 影依] 共 3 张，
`Count(IsTearAttack)==2`（触发卡+水仙女）与 `Any(is Kitkallos)` **双双成立** → 3 张素材融出了
卡面写明"**2张**珠泪攻击牌"的鲁莎卡人鱼。同类 `ShaddollFusionOptions` 全部带 `m.Count == 2/3`，珠泪这两个漏了。

**根因B（影融选超素材无事发生）**：`ShaddollFusionCore` 的严格判定在 `available.Count == 0` 时直接 return
（"素材未动、什么都没发生"）。但影融界面是 `PickSomeFromList(2, 3)` **单界面一次选完**，
玩家选 3 张而只有其中 2 张构成有效组合时，**整个操作作废** → 用户观感"白选了"。

**修复**（`LsUtil.cs`）：
1. 给 Rulkallos / KaleidoHeart 补 `m.Count == 2` / `m.Count == 3`，并把"每个条件都必须显式约束素材总数"
   写进注释（与文件既有"严格语义"设计原则对齐）。
2. 新增 **`BestCompatibleSubset`** 向下兼容助手：当选出组合不满足任何融合条件时，回退到
   "所选素材中仍能满足某融合条件的**最佳子集**"，只消耗该子集。选优规则=优先张数多者，
   同张数下优先**含触发卡**者；无任何可用子集才真的什么都不发生。
3. 珠泪引擎（`TearFusion`）与影融引擎（`ShaddollFusionCore` 的 Hand/Exempt 分支）双双接入。
   `DiscardExhaust` 分支是固定 2 张（min=max=2），不可能超选，无需接入。

**行为结果**（用独立模拟程序验证）：用户场景 `[触发珠泪攻击牌, 水仙女, 影依]` 下，
鲁莎卡不再由 3 张素材违规产出，而是**降级到合法子集 `[触发卡, 水仙女]` 照常产出鲁莎卡**
——玩家的融合意图仍被满足，且多选的影依**不再被静默消耗**（留在弃牌堆）。这正是用户要的"向下兼容"。

### 问题4：卡面文案全面审计与规范化（黄昏之交衣敲后仍有"消耗" / 重复消耗 / 弃光独立成词）

**改动 `lightsworn\localization\zhs\cards.json`（唯一文件，49 个 description，键集 210 未变）**：

1. **黄昏之交衣敲后"消耗"**：`OnUpgrade()` 已 `RemoveKeyword(Exhaust)`，但描述是静态文本。
   修复=**直接删正文"消耗。"，不用 `{IfUpgraded:...}`**——引擎在
   `GetDescriptionForPile` 末尾 `CardKeywordOrder.afterDescription.Intersect(keywords)` 自动追加
   `[gold]消耗[/gold]。`，关键词被移除后该行**自动消失**；用 IfUpgraded 反而基态会叠两行。
2. **消除重复消耗（9 张）**：凡 `CanonicalKeywords` 已含 `CardKeyword.Exhaust` 且正文句尾又写独立"消耗。"者，
   删正文那两字，交给引擎。**保留**效果动词（"将其消耗""消耗弃牌堆中的N张牌"）与区域名（"消耗堆/消耗区"）。
   交叉验证：唯一剩余两个"以消耗。结尾"的是 SnowSpirit（"将其消耗"，句中动作）与 Reinohart
   （"并获得消耗"，运行时 `AddKeyword` 而非静态声明）——均为**合法效果**，不动。
3. **"弃光/除光"规范化（30 张）**：用户点名"参考未掘宝石的文本"。核实结论：
   官方 `HIDDEN_GEM.description = "你[gold]抽牌堆[/gold]中的一张没有[gold]重放[/gold]的随机牌获得{Replay:diff()}层[gold]重放[/gold]。"`
   ——**句中内联 `[gold]` + 数值留在句中**，而非独立成词。RitsuLib 的关键词注入只给标题（无值），
   所以正文裸写"弃光3"会与自动注入的关键词行**双重表述**（这正是用户抱怨的"单独在文本有个词"）。
   落地规范=**动作写动作、资源名写 `[gold]资源名[/gold]`**：
   - `弃光{Mill:diff()}` → `从[gold]抽牌堆[/gold]顶部弃置{Mill:diff()}张牌`
   - `除光{Banish:diff()}` → `从[gold]抽牌堆[/gold]中选择{Banish:diff()}张牌[gold]消耗[/gold]`
   - 触发条件里的机制名内联上色（比照官方"每当有一张牌被[gold]消耗[/gold]时"）
   - 资源名统一 `[gold]暮光[/gold]`（原先 3 处裸词 / 3 处上色**自相矛盾**，已统一为全部上色）
4. **关键词行 placement 保持不变**（`Ls.cs` 的 5 个关键词仍为 `BeforeCardDescription`）。
   理由：独立成行本身符合官方惯例（`CardKeywordOrder.beforeDescription/afterDescription` 即为此设计），
   且若改为 `None`，卡面将失去"弃光/除光/暮光"的彩色可识别标记（引擎不会自动给正文里的机制名上色）。

**残留开放项**（非缺陷，待用户拍板）：`TWIN_TWILIGHT_DRAGON` 是唯一同时挂 MILL+BANISH 的卡，
卡面仍会叠 `[gold]弃光[/gold]。`+`[gold]除光[/gold]。` 两行短词。若用户仍嫌观感，
建议**只对这张卡**把 BANISH 改为 `None`，而非全局调整。

### 问题5：初始遗物补牌增加打防保底（最多 60% 是打/防）

**改动 `LightswornContent.cs` `MustPlayYugioh.BeforeCombatStart`**：
- `int basicCap = need * 3 / 5;`（= **floor**(0.6·need)）+ `basicCount` 计数；
  `roll < 100 && basicCount < basicCap` 才出打击/防御，触顶后全部走卡池。
- **roll 仍每张牌无条件消耗一次 `NextInt(205)`** → RNG 序列与消耗次数确定，同 seed 各端一致（联机要求）。
- **为何用 floor 而非 ceil**：ceil(0.6·need) 在小 need 时会突破 60%（need=1→100%、3→66.7%、4→75%、7→71.4%），
  与"最多60%"硬要求冲突；**floor 是唯一对所有 need 都 ≤60% 的取整**（上界恰 60.0%，need 为 5 的倍数时取得，
  实战最常见 need=30 → cap=18=60%）。
- **最坏占比证明**：`basicCount` 仅在 `< basicCap` 时自增 ⟹ 恒有 `basicCount ≤ floor(0.6·need) ≤ 0.6·need`
  ⟹ **打防占比 ≤ 60.0%，对任意 need 恒成立**。
- **连带修正**：触顶后原本 `roll∈[0,100)` 也会进卡池分支，若沿用旧边界（<185 普通）会把白卡比例抬到 90%。
  已用整数归一 `roll<100 ? roll*105/100 : roll-100` 铺满卡池段，实测 **80.98 : 14.63 : 4.39**，
  对齐设计的 85:15:5（=80.95 : 14.29 : 4.76），纯整数运算、各端一致。
- 修复前越线概率（打防 ~ B(need, 48.78%)）：need=30 时 **P(打防>18张=超60%)≈7.86%**、need=40 时 5.70%；
  修复后 **P=0**。

### 问题6：商店与火堆形象改用战斗立绘 + 火堆"坐在木头上"的比例调整

**根因（与 v0.5.1 的头像/能量球问题同源，且是双重继承）**：
1. `ModCharacterTemplate.ResolvedAssetProfile` 会把**未覆盖的资源槽从占位角色继承**
   （`PlaceholderCharacterId="ironclad"`）。
2. 更关键的二次兜底：`CharacterWorldScenePathFactoryHelper.EnumerateCandidatePaths` 写死
   "角色 id 非 ironclad 时，再试一次 ironclad 的 `Scenes.MerchantAnimPath` / `Scenes.RestSiteAnimPath`"
   → 不覆盖时商店/火堆都拿铁甲的 `_merchant` / `_rest_site` 场景。

**修复**（`LightswornContent.cs`）：新增 `WorldProceduralVisuals` 覆写，用
`CharacterWorldProceduralVisualSetBuilder` + `VisualNodeStyle` 精确控制（**无需新建 tscn**，
天然绕开"pck 解析不了游戏本体 C# 脚本"的坑——证据：两个槽位的 `IsCompatibleResource` 均允许
`PackedScene` **或** `Texture2D`）。cue key 全部显式绑定：火堆 `overgrowth_loop`/`hive_loop`/`glory_loop`
（三章循环名，其它 act 回落 overgrowth）、商店 `relaxed_loop` + `idle` 兜底。

**视觉参数与依据**（素材 `battle.png` 984×1000，实测不透明内容 bbox 覆盖全画布）：
- **商店**：Scale `0.34` / Position `(0,-170)` —— 约 335×340，与战斗立绘 0.33（≈325）观感统一；
  Y = -H·s/2 把图心抬到脚底贴地。
- **火堆**：Scale `0.38` / Position `(0,-236)` / Offset `(0,-8)`。
  关键发现：**这张立绘本就是坐姿**（实测 y≥780 内容收窄到 x182-765，最底 y≥960 只剩 x375-447
  = 裙摆铺开 + 双脚下垂的轮廓），所以**不需要新素材**。Y 取 `-H·s·0.62`（而非 0.5）——
  因坐姿有效底边不在画布底（最底 40px 只有鞋，裙摆主体在 y780-940），0.62 让图心比"脚底贴地"
  再低约 46px，使裙摆正好搭在木头上、鞋略垂到木头前侧；Offset -8 贴合木桩顶面高于地面。
- Hitbox 照原尺寸纹素给定、不随 Scale 收缩，点击热区仍覆盖整图，无需处理。
- **美术需求：不需要新素材**（现有 battle.png 已是坐姿）。非阻塞建议：若要做火堆专用坐姿图
  （画布约 800×800、裙摆下沿与木桩顶面同线），可把 RestSiteStyle 的 Y 简化回 -H·s/2。

### 验证（v0.5.4）

- **构建**：`dotnet build` **0 错误 / 12 警告 = 基线**（警告文件与类别完全一致，仅 LightswornContent.cs
  行号因新增代码位移）。
- **memberref 审计**：对 **0.107.1 正式版** 与 **0.111.0 beta** 双目标 **AUDIT PASS**
  （methods=188 / fields=1 / base-iface typerefs=0）。
- **API 兼容试编译**：对 0.107 refs + `LsCompatTrial=true` **0 错误**
  （验证 `SetToFreeThisTurn` / `CardPileAddResult` / `EnergyCost.UpgradeBy` 在两端均可绑定）。
  注：`refs107\` 原先缺少 `RitsuLib\` 子目录，手册 §4 记载的试编译命令会因 props 未被 import
  而报 732 个 `CS0246: STS2RitsuLib 未找到`（**环境缺陷而非代码缺陷**）；本轮已补齐
  `refs107\RitsuLib\`（props + 0.107.1 compat + shared），该命令现可直接使用。
- **pck 校验**：导出后解包比对，`lightsworn/localization/zhs/cards.json` 与源文件
  **sha256 完全一致**（29959 bytes），确认 `ExportPck`（`ContinueOnError=WarnAndContinue`）真的把本轮文案打进去了。
- **逻辑验证**：问题3 用独立模拟程序跑用户原场景与边界用例（2 素材正常融合、3 素材违规被拦、
  4 素材、超选降级），结果符合预期；问题5 的归一化分布与 floor/ceil 占比均实测复核。

### 发布注意

- 本次改了 **dll**（问题1/2/3/5/6）与 **pck**（问题4 文案）→ 联机两端必须同时升到 **v0.5.4**
  （mod 版本握手校验，`Lightsworn.json` 与 `.csproj` 版本号已同步为 0.5.4）；朋友端需重新更新工坊条目。
- 全部为修复，**无卡牌内部 ID 变更 → 旧存档兼容**。

---

## v1.47 用户订正 v1.46 的三处（2026-10-16，v0.5.4，对话直接下发）

用户看过 v1.46 汇报后订正三处，**其中一条推翻了我对问题1的根因判断**，记录如下（v1.46 原文保留不动，以本节为准）。

### 订正1（问题1 根因修正）：帝皇蟹左右钳子场景，卡回来了、但仍2费

**用户原话**：「光道龙的具体问题是这样的，帝皇蟹有左右两个钳子，只击杀右侧钳子，左侧钳子存在的情况下，卡回来了，但是仍然是2费」。

**我在 v1.46 的判断错在哪**：我据 `IsEnding`（=所有 primary enemy 已死）推断"击杀 boss 导致 `CardPileCmd.Add` 静默失败、卡压根没回手"。
但用户给的是**只杀一只钳子**——帝皇蟹本体仍在（primary enemy 存活）→ `IsEnding` = false → `Add` **不会失败，卡确实回手了**。
所以"回手失败"不是本场景的根因，**实测直接证伪了我的推断**。

**修正后的真根因（单因，仅"0费的清理时机"）**：走一遍原版 `OnPlayWrapper` 的结算顺序即可复现：
1. `OnPlay` 里 `CardPileCmd.Add(this, PileType.Hand)` 把卡从 Play 移到 Hand —— **成功**（本场景 IsEnding=false）。
2. `OnPlay` 返回后，`OnPlayWrapper` 尾部**无条件**执行
   `if (EnergyCost.AfterCardPlayedCleanup()) { this.EnergyCostChanged?.Invoke(); }`，
   而 `AfterCardPlayedCleanup()` = `_localModifiers.RemoveAll(m => m.Expiration.HasFlag(WhenPlayed))`
   —— 它清理的是 **`this` 这张卡**的修正，而 `this` 此刻**正躺在手牌里**。
3. 原实现用的 `SetUntilPlayed(0)` 其 `Expiration=WhenPlayed` → 被第2步原地抹掉 → 手牌里仍是 2 费。

**修复仍有效且方向正确**（v1.46 已落地，未改）：`CardModel.SetToFreeThisTurn()`
（= `EnergyCost.SetThisTurnOrUntilPlayed(0)`，`Expiration=EndOfTurn|WhenPlayed`）——`EndOfTurn` 位让它在第2步的清理中**存活**，回合结束才自然失效。
代码里保留了 `CardPileAddResult.success` 判定作为防御（直接击杀 boss 本体时 `IsEnding` 确为 true、`Add` 确会失败，那时不该白给0费标记），但它**不是**本次用户场景的成因。Cards2.cs 的注释已按此改写。

### 订正2（问题2 升级项）：残响敲后 = 生成强化后的版本（不是费用-1）

**用户原话**：「残响敲后改为生成强化后的版本，而不是费用-1」。

- 作废：`OnUpgrade() => EnergyCost.UpgradeBy(-1)`（我原先选的最小改动方案）。
- 现行：`OnUpgrade() { }` **留空体**，升级语义交给复制路径 —— `CopyTearAttackFromExhaust` 里
  `if (IsUpgraded && !copy.IsUpgraded) { copy.UpgradeInternal(); copy.FinalizeUpgradeInternal(); }`
  → 残响已升级时，被弃置拿回的珠泪攻击牌**以强化版入手牌**；素材本身已是强化版则不重复升。
  范式与 mod 既有的融合产出（`LsUtil.TearFusion` / `GenerateShaddollToken`）完全一致。
  依据：反编译 `UpgradeInternal()` = `CurrentUpgradeLevel++ ; OnUpgrade() ; DynamicVars.RecalculateForUpgradeOrEnchant()`，
  空体 `OnUpgrade` 安全，数值升级由 `RecalculateForUpgradeOrEnchant` 承担。
- 文案（loc-auditor 落地）：`…生成一张相同的卡加入手牌{IfUpgraded:show:（强化版）|}（若为融合生成的卡…）`。
  ⚠ 这里用 `{IfUpgraded:show:}` 是**正确**的——上一轮"不写正文"的裁定**只针对费用数字**
  （费用由卡面左上角经 `SetCustomBaseCost → InvokeEnergyCostChanged` 自动体现），而"强化版"是**效果差异**、必须写出。

### 订正3（问题3）：选超素材 = 作废，**不做向下兼容**

**用户原话**：「我希望的是选超素材作废，而不是向下兼容」。

- 作废：我新增的 `BestCompatibleSubset` 降级助手**整体删除**（含两处接线）。
- 现行：`TearFusion` 与 `ShaddollFusionCore` 恢复严格语义 —— 所选组合不满足任何融合条件时
  **整个发动作废**（不弃置、不消耗，素材原样不动）。与 v0.4.15 起的既有设计一致。
- **保留的修复**：`FusionOptions` 的**素材总数约束**（`m.Count == 2/3`）必须留着 —— 那修的是
  用户对同一句话的**另一半**抱怨「珠泪融合选了水仙女和影依，会出鲁莎卡人鱼」：
  缺了总量判定时 3 张素材也能满足"2张珠泪攻击牌"的鲁莎卡条件。二者合起来才是完整需求：
  **条件要精确（不许违规产出）+ 超选要作废（不许静默降级）**。
- 因"作废"对玩家是惩罚性结果，同步在选材提示里写明规则（"素材数量须与融合条件完全一致，不满足条件的组合将作废"）：
  `card_selection.json` 的 `LIGHTSWORN_TEAR_MATERIAL` 与 `LIGHTSWORN_SHADDOLL_MATERIAL`。

### 订正4（问题4 追加）：TWIN_TWILIGHT_DRAGON 单独收敛 —— 用户质疑「为什么不能像别人一样改」

**用户原话**：「TWIN_TWILIGHT_DRAGON 需要单独收敛，我印象中它的文本里有弃光和除光吧，为什么不能像别人一样改」。

**结论：用户是对的，我 v1.46 的处置偏保守。** 该卡原先静态声明 `[LsKeywords.Mill, LsKeywords.Banish]`，
卡面**恒定**叠两行孤立短词；但它两个机制都是**条件性**使用：
- 弃光只在「手牌中有惩戒之龙」分支发生（否则走"置入弃牌堆"分支，不弃光）；
- 除光只在「被从卡组弃置时」（`OnMilledByLsCard`）发生 —— **根本不是本卡打出时的效果**。
故两行词条多数情况下是误导性的。

**处置**：从该类**删除** `CanonicalKeywords` 的两个声明（安全前提已证：`LsKeywords.Mill/Banish`
在 mod 内**无任何读取点**，grep `Keywords.Contains(LsKeywords` 零命中，纯声明式，删除只影响词条行与 hover tip）；
正文写回机制名并 `[gold]` 内联：`然后[gold]弃光[/gold]{Mill:diff()}` / `然后[gold]除光[/gold]4`
（与官方未掘宝石的 `[gold]重放[/gold]` 同构）；另用 `AdditionalHoverTips`
`HoverTipFactory.FromKeyword(LsKeywords.Mill/Banish)` **手工挂回两个 hover tip**，补偿删词条后失去的可查性。

**由此定稿的文案双规范**（判定依据=「卡面是否已有该词条行」，两条并存不冲突）：

| 情形 | 正文写法 | 例 |
|---|---|---|
| 卡**有**关键词行（引擎 `beforeDescription` 自动注入 `[gold]弃光[/gold]。`） | **不写**机制名，展开为动作：`从[gold]抽牌堆[/gold]顶部弃置{N}张牌` | RYKO/JAIN/…（29 张 MILL 卡） |
| 卡**无**关键词行（声明已删） | **必须写回**机制名并 `[gold]` 内联：`[gold]弃光[/gold]{N}` / `[gold]除光[/gold]4` | TWIN_TWILIGHT_DRAGON |

### v0.5.4 最终验证（订正后重跑）

- `dotnet build` **0 错误 / 12 警告 = 基线**。
- memberref 审计：0.107.1 与 0.111.0 **双 PASS**（methods=189 —— 较上轮 188 增 1，为新增的
  `HoverTipFactory.FromKeyword` 引用）。
- 0.107 API 兼容试编译（`LsCompatTrial=true`）：**0 错误**。
- pck 内容校验：`cards.json`（29929 bytes）与 `card_selection.json` 均与源文件**逐字节一致**，
  确认订正后的文案真的进了包。
- 最终三件套哈希：dll `9BDE09CF…`(348672) / json `75F98F02…`(561) / pck `E6CAB19D…`(20932560)；
  `dist\lightsworn\` 与游戏 `mods\Lightsworn\` 一致。

---

## v1.48 卡面机制词文案终稿：弃光/除光/暮光 全部「正文内联、无词条行」（2026-10-16，v0.5.4，用户点名直改）

**用户原话**：「目标是让卡牌文本没有单独的弃除光暮光。比如雷光，现在的文本是：弃光。弃光3，施加一层虚弱和易伤。
我感觉2个弃光太重复了，参考重放3。这种，不会同时有重放和重放3两次关键字」

> **以本节为准**：v1.46 问题4 的「动作化改写」与 v1.47 的「文案双规范」表（含"placement 保持不变"的判断）
> **一并作废**。上一轮把正文写成"从抽牌堆顶部弃置N张牌"是**过度解读**——用户要的是把**机制名+数值**留在正文
> （`弃光3`），删掉的是**独立词条行**；两份并存才是"2个弃光太重复"的根源。

### 关键实证（决定方案的三条反编译证据）

1. **RitsuLib 的 placement 注入的是"短标题行"，不是说明文本**：`ModKeywordCardDescriptionInjector`
   （STS2-RitsuLib.Runtime.decompiled.cs:176091）取 `ModKeywordRegistry.GetCardText(id)`，
   而其自述是「关键词的**内联卡牌文本（金色标题及其后的句号）**」——即卡面只多一行 `[gold]弃光[/gold]。`。
   （v1.46 曾以为注入的是"长篇机制说明"故保留词条行；实机放大截图证实卡面就是一行短标题，长的在悬浮提示里。）
2. **官方"重放"范式 = 正文内联 + 悬浮提示、无词条行**：`HiddenGem` 正文
   `获得{Replay:diff()}层[gold]重放[/gold]`；原版 `CardKeyword` 枚举**没有 Replay**
   （`HoverTipFactory.FromKeyword` 只服务枚举值，sts2.decompiled.cs:153244），
   官方用 `StaticHoverTip.ReplayStatic` 单独挂提示。用户说的"参考重放3"即此形态。
3. **悬浮提示是自动的，不需要手写**：原版 `CardModel.HoverTips`
   （sts2.decompiled.cs:65552）`foreach (CardKeyword keyword in Keywords) list.Add(HoverTipFactory.FromKeyword(keyword));`；
   RitsuLib `HoverTipFactoryFromKeywordPatch`（decompiled.cs:177489，Prefix）把 mod 铸造的关键词
   路由到 `ModKeywordRegistry.CreateHoverTip`（用注册的 title/description 建提示）；
   `IncludeInCardHoverTip: true` 保留，置 false 才由后置补丁剔除。

### 落地（四处）

1. **`Ls.cs`**：`MILL/BANISH/TWILIGHT` 的 placement = `ModKeywordCardDescriptionPlacement.None`
   —— 卡面不再注入任何词条行（上个模型 23:19 已写，本 session 复核确认）。
2. **`cards.json`（33 处）**：正文动作化写法回改内联机制词 ——
   `从[gold]抽牌堆[/gold]顶部弃置{Mill:diff()}张牌` → `[gold]弃光[/gold]{Mill:diff()}`
   （含固定值 `弃光3/5/1`、动态 `弃光X`、雅典娜"再[gold]弃光[/gold]相同数量"）；
   除光：`从[gold]抽牌堆[/gold]中选择{Banish:diff()}张牌[gold]消耗[/gold]` → `[gold]除光[/gold]{Banish:diff()}`。
   执行脚本 `tools\apply_inline_text_v054.py`（逐条**计数断言** + 键集断言 + 裸词断言）。
3. **删除上一轮中途手写的 `LsCard.AdditionalHoverTips` 关键词挂载**（LightswornContent.cs）：
   原版已自动挂（实证3），手挂会因 mod 提示不走原版 `_keywordHoverTips` 缓存而**重复显示两份同名提示**；
   该处现在留注释说明"勿写回来"。
4. **关键词声明补齐/恢复**（声明唯一作用=自动带出悬浮提示，不改卡面文本）：
   - 补 `MILL`：加洛斯 / 珍妮丝 / 正义世界 / 邻家割草 / 破坏之光（正文提到弃光但原先未声明）；
   - **黄昏之双龙**：恢复 `[LsKeywords.Mill, LsKeywords.Banish]`（v1.47 的"删声明+手挂提示"作废），
     `AdditionalHoverTips` 只留两张龙牌预览。

### 有意未动：TEARFUSION / SHADDOLLFUSION 仍用 `BeforeCardDescription`

- **理由修正**：保留它们的真实理由是——`tools\audit_fusion_inline.py` 实测 **11 张卡正文没有内联机制名**
  （真血公/手札抹杀/愚蠢的埋葬/影依猎犬/影依巫女/路径灵/文蒂/虚梦狱/炼狱的乖放/心影依融合），
  词条行是这些卡**唯一的卡面标记**（删掉等于卡面完全不提它是什么机制）。
- **已知副作用（留待用户裁决）**：另 11 张"正文已内联"的珠泪/影依卡会出现两处机制名
  （顶部短词条行 `珠泪融合。` + 正文尾 `珠泪融合+`）。若要彻底统一，方案=这两个关键词也改 None
  + 给上述 11 张补内联机制名（一次到位）；本轮**不动**（超出用户点名范围）。

### 验证（本轮全量重跑，证据 tools\_v054_*.png）

- **构建**：`dotnet build` 0 错误 / 12 警告（基线）；0.107 试编译（`LsCompatTrial=true`）**0 错误**。
- **memberref 审计**：0.107.1 与 0.111.0 **双 PASS**（methods=**188**；较"订正4"版少 1 = 删掉的手挂
  `HoverTipFactory.FromKeyword` 引用）。
- **pck**：解包比对 `cards.json` **逐字节一致**（29097 bytes / sha256 `470cf817…`；较上轮 29929 缩小 = 动作化长句变短）。
- **实机（0.107.1 正式版，直启 + wininput 驱动，百科大全实拍）**：
  - 日志：`Lightsworn.Entry … Version=0.5.4.0`、112 项注册 0 失败、**零 Exception / 零 `GetRawText`**；
  - 卡面：**雷光 =「弃光3。目标敌人获得1层虚弱和1层易伤。」**（`弃光` 金色、只出现一次、上方无词条行；
    3× 放大图 `tools\_v054_ryko_zoom.png`）；太阳交换/简/防护罩/莱登/艾琳/费莉丝/光之援军/夏尔 同款；
    升级视图（勾选"查看升级"）裁决之龙「弃光4。」、塞壬人鱼「…回复1点能量并弃光3。珠泪融合。」正常；
  - 悬浮提示：卡牌悬浮区实拍同时出「珠泪融合」（长说明）+「**弃光N：从抽牌堆顶部将N张牌弃置。…**」+「暮光：…」
    ——**placement=None 完全不影响到 hover tip**。
- **图鉴**：`tools\gen_card_doc.py` 重跑（雷光条目=`[gold]弃光[/gold]3。…`）。
- **本轮最终三件套**：dll `f71eae44…`(349184) / json `fd1d7b38…`(561) / pck `c27cbd55…`(20931728)，
  `dist\lightsworn\` 与游戏 `mods\Lightsworn\` md5 一致（dll 在注释微调后重编过一次；两轮审计均 PASS）。
  注：**注释也会改变 dll 字节**（PDB GUID 内嵌于 dll 调试目录）——最终产物以最后一次 build 为准。

### 发布注意

- 本轮改 **dll**（关键词声明/删手挂提示）与 **pck**（文案）→ 两端必须同升 **v0.5.4**。
- **✅ 已发布（2026-10-16）**：git main `3404c26`；创意工坊 3819657802（Steam 日志
  `Uploaded new content (ManifestID 5140002338743634096)` + `Upload finished : OK`；v0.5.3 为 1518804264528828898）。
  发布流程=dist 三件套 → `lightsworn_mod-tools\workshop\lightsworn\Content\` → `py tools\update_workshop_v054.py`（changeNote）
  → `ModUploader.exe upload -w <workspace>`；朋友端需重新更新订阅。
- 无卡牌内部 ID 变更 → 旧存档兼容。


---

## v1.49 第四十二轮反馈：六条（2026-10-17，v0.5.5，已知问题.txt 下发）

**用户条目**：①雷喵敲后效果改敲前、敲后取消消耗；②裁决/惩戒伤害 30、敲后保留；双龙强化改为生成强化版；神光 30×3；
③惩戒只回攻击/技能/能力牌；④游戏王/圣徽都做成初始遗物，二选一丢另一个、skip 保留第一个；
⑤新增先古遗物「更好的游戏王」「光道权杖」；⑥探查做 Boss 所需美术/设计。

### 1. 雷喵（Rinyan）

- 基础 `Picks` 2→3（原升级 +1 改为基础效果）；`OnUpgrade` 从 `Picks+1` 改为 `RemoveKeyword(CardKeyword.Exhaust)`。
- 结果：基础 0 费、洗回最多 3 张、带「消耗」；强化后张数不变、移除「消耗」。
- 文案无需改（`{Picks:diff()}` 自动显示 3；消耗关键词由原版自动显示）。

### 2. 裁决之龙 / 惩戒之龙 / 双龙 / 神光之龙

- 裁决之龙：`DamageVar` 22→30；`OnUpgrade` 从伤害 +6 改为 `AddKeyword(CardKeyword.Retain)`。
- 惩戒之龙：`DamageVar` 22→30；`OnUpgrade` 同上改为「保留」；回收过滤加
  `c.Type is CardType.Attack or CardType.Skill or CardType.Power`（诅咒/状态等不回）。
- 黄昏之双龙：敲后不再 `AddKeyword(Retain)` 给生成的龙，而是对生成的
  `JudgementDragon`/`PunishDragon` 执行 `UpgradeInternal()+FinalizeUpgradeInternal()`（生成强化版对应卡；
  两条龙的「保留」由强化版自带）。cards.json 与卡牌图鉴同步为“改为生成强化版”。
- 神光之龙：`DamageVar` 22→30；升级仍为 +4（30×3/34×3）+ 保留。
- ⚠ 设计提醒（留给用户裁决）：`光道的裁决` 的 Token 本来就带「保留」；现在裁决之龙的强化只剩「保留」，
  所以「光道的裁决」敲后生成的强化版与基础版**不再有伤害差**。如希望这条升级仍有意义，
  建议给该 Token 换一个升级收益（例如费用 0→保留+抽 1，或提高 Token 伤害），本轮未擅自改。

### 3. 初始遗物（游戏王 / 圣徽）

- `LightswornSigil.Rarity` 从 `Uncommon` 改为 `Starter`——与 `MustPlayYugioh` 一样是初始遗物，不再进随机遗物池。
- 二选一逻辑保持：界面选项 `[游戏王, 圣徽]`；选圣徽→`RelicCmd.Replace(游戏王, 圣徽)`（丢弃另一个）；
  跳过→保留第一个游戏王。读档不走该流程，选择随存档持久。
- 说明：角色 `LocalStartingRelics` 仍只列游戏王；圣徽作为二选一的另一选项，稀有度已是 Starter。

### 4. 先古遗物（欧洛巴斯之触）

- 新增 `BetterMustPlayYugioh : MustPlayYugioh`：`Rarity => Ancient`；沿用基础版图标；
  `BeforeCombatStart` 只生成白/蓝/金卡，比例 **5:3:2**（每张固定 `NextInt(10)`，联机同种子可复现；不再生成打击/防御）。
- 新增 `LightswornScepter`：`Rarity => Ancient`；每回合开始 `LsUtil.Mill(player, 3)`，
  按弃置牌中「光道」牌数量抽牌（Owner 过滤，联机只在自己回合触发）。
- **欧洛巴斯精炼映射**（RitsuLib 正规入口）：
  - `[RegisterTouchOfOrobasRefinement(typeof(BetterMustPlayYugioh))]` 挂在 `MustPlayYugioh`
  - `[RegisterTouchOfOrobasRefinement(typeof(LightswornScepter))]` 挂在 `LightswornSigil`
  - 玩家最终持有的初始遗物是哪个，欧洛巴斯之触就替换成对应先古版（`TouchOfOrobasGetUpgradedStarterRelicPatch`）。
- 图标：权杖从 `images/character/battle.png` 裁杖头（`tools\make_scepter_relic_icon.py`，裁切框 105,195–305,395），
  输出 64/256 圆形透明底 `relics/scepter.png`、`scepter_big.png`；更好的游戏王直接复用 `yugioh.png/_big`。
- 本地化：`relics.json` 新增 `LIGHTSWORN_RELIC_BETTER_MUST_PLAY_YUGIOH.title/.description`、
  `LIGHTSWORN_RELIC_LIGHTSWORN_SCEPTER.title/.description`。

### 5. Boss 探查

- 新增 `design\boss制作需求.md`：技术结构（Encounter+Monster+RitsuLib 注册）、美术清单与实测规格
  （Boss 立绘、地图节点 350×307+描边、历史图标 85×85+描边、背景层约 2048×960）、
  设计清单（招式表/阶段/进阶/多人/奖励/文本）、静态图 vs Spine 路线与 MVP 模板。

### 验证（本轮）

- 构建：`dotnet build` **0 错误**（12 警告为历史基线）。
- memberref 审计：0.107.1 与 0.111.0 **双 PASS**（methods=188）。
- 部署：robocopy `/MIR /IS /IT` → 游戏（本机实际为 **0.107.1 正式版**）启动日志
  `Version=0.5.5.0`、`Lightsworn mod initialized!`、新遗物
  `BetterMustPlayYugioh / LightswornScepter` 均注册；整局测试仅 1 条与 mod 无关的
  `current_run.save.backup` 删除失败 ERROR，**无 Lightsworn Exception**。
- pck：`tools\pck.py list` 确认含 `scepter.png / scepter_big.png`；解包 `relics.json` 两条新词条逐字正确。
- **实机 UI 逐条验证（wininput 驱动，截图 tools\_v055_*.png）**：
  - 初始遗物二选一弹窗同时显示「你必须玩游戏王 / 光道圣徽」；点 Skip 后遗物栏只剩游戏王（第一个），
    圣徽未进栏 → “skip 保留第一个”成立。
  - 控制台 `event OROBAS` 直达欧洛巴斯：第三个选项文本=**「将你必须玩游戏王替换为更好的游戏王」**
    → RitsuLib 精炼映射已生效；选中并继续后，更好的游戏王进遗物栏，**图标与基础版同为 yugioh 漩涡**，
    悬浮描述=“只生成普通、罕见、稀有卡牌补足，比例为5:3:2”。
  - 控制台 `relic add LIGHTSWORN_RELIC_LIGHTSWORN_SCEPTER` → 权杖图标正常显示；
    `fight CULTISTS_NORMAL` 第1回合结束弃牌堆=3张（每回合弃光3生效），手牌 5 张。
  - 卡面：雷喵=“最多3张…消耗。”；升级雷喵+=“最多3张…”且**无「消耗」**、无消耗悬浮提示；
    裁决之龙/惩戒之龙基础=30 伤害；升级后卡面出现「保留」关键词行与悬浮说明；
    神光之龙=“造成30点伤害，重复3次”；惩戒之龙文案=“所有非「光道」的攻击、技能、能力牌”。
- 产物：dll `4a6b78bf…`(352768) / json `5db7ec77…`(561) / pck `d7ca15da…`(21032120)。

### 发布注意

- 本轮改 dll + pck → 联机两端必须同为 **v0.5.5**；旧存档兼容（无内部 ID 变更）。
- 新增先古遗物依赖 RitsuLib 的欧洛巴斯精炼补丁（随 RitsuLib 0.6.7 已启用）。


---

## v1.50 第四十二轮追加订正四条（2026-10-17，v0.5.6）

**用户条目**：①神光之龙敲后不加伤害、只加保留；②神光/光道天使多段伤害文本改官方句式；
③黄昏之双龙敲后文案用「裁决之龙+」格式；④百科大全遗物收集看不到其他 mod 遗物。

### 1. 神光之龙

- `OnUpgrade` 删除 `DynamicVars.Damage.UpgradeValueBy(4)`，只保留 `AddKeyword(CardKeyword.Retain)`。
- 结果：基础/敲后都是 **30×3**；敲后额外获得「保留」。卡牌图鉴同步“伤害不变（仍30×3）”。

### 2. 多段伤害官方句式

- 官方中文卡面写法实测（游戏 `localization/zhs/cards.json`，如 CONFLAGRATION/EXTERMINATE）：
  `对所有敌人造成{Damage:diff()}点伤害{Repeat:diff()}次。` —— **不用“重复Y次”**。
- 光道天使 基路伯：`对所有敌人造成{Damage:diff()}点伤害{Hits:diff()}次。`
- 神光之龙：`对所有敌人造成{Damage:diff()}点伤害{Hits:diff()}次，并施加3层虚弱和3层易伤…`
  修复了之前“造成30点伤害，重复3次”的非官方语序。

### 3. 「卡名+」写法

- 黄昏之双龙：`否则：将1张「裁决之龙{IfUpgraded:show:+|}」和1张「惩戒之龙{IfUpgraded:show:+|}」置入弃牌堆。`
  基础显示「裁决之龙」/「惩戒之龙」，敲后显示「裁决之龙+」/「惩戒之龙+」；
  不再出现“（改为生成强化版）”。
- 顺带把「光道的裁决」的 `强化后的…「裁决之龙」` 也统一为 `「裁决之龙{IfUpgraded:show:+|}」`。
- 卡牌图鉴 `gen_card_doc.py` 的 SPECIAL 覆盖同步。

### 4. 百科大全遗物收集：圣徽/权杖不可见（根因 + 修复）

**根因**（反编译 `NRelicCollectionCategory.LoadRelics` 实证）：
- 「初始」页**不读** `ModelDb.AllRelics.Where(Rarity == Starter)`，而是：
  1. `ModelDb.AllCharacters.SelectMany(c => c.StartingRelics)`；
  2. 再对每件起始遗物调用 `TouchOfOrobas.GetUpgradedStarterRelic()` 追加先古版；
  3. 然后 **直接 return**。
- 所以只有写进 `Character.StartingRelics` 的遗物（及其欧洛巴斯先古版）会出现在初始页。
  游戏王在 `LocalStartingRelics` 里 → 游戏王 + 更好的游戏王可见；
  圣徽只改了 `Rarity=Starter`、没写进 `StartingRelics` → 圣徽和光道权杖都不显示。
- 猫狗双全（Common）/幻色珍珠（Event）本来就在“普通/事件”分区，不在初始页。

**修复**（`LightswornContent.cs` + `StartingRelicChoice.cs`）：
- `LocalStartingRelics` 改为 `[MustPlayYugioh, LightswornSigil]` —— 让收藏页的初始页能枚举到
  游戏王/圣徽，以及它们各自的先古版（更好的游戏王/光道权杖）。
- 实际开局两件都会先发下来；`FinalizeThenOffer` 在 `AfterObtained` 之前把
  `LightswornSigil` 从“持有游戏王”的玩家身上 Remove 掉（按 state.Players 顺序、各端一致），
  玩家仍然只持有游戏王，然后走原二选一（选圣徽=Replace 游戏王；skip=保留游戏王）。
- 这样收藏页四件齐全，实际开局/存档不会同时持有两件初始遗物。

### 验证

- 构建 0 错误；memberref 审计 0.107.1+0.111.0 **双 PASS**（methods=189）。
- pck 解包核对：CELESTIA/SHINING/TWIN/DECREE 四条文案逐字正确。
- 实机（0.107.1）：收藏页「初始」实拍=第一行含 **游戏王 + 光道圣徽**、第二行含
  **更好的游戏王 + 光道权杖**（权杖为未见过暗色）；用户确认“遗物没问题了”。
- 产物：dll `f59e1695…`(353280) / json `b9d4023f…`(561) / pck `e419e893…`(21032072)；v0.5.6 **未发布**。

---

## v1.51 第四十三轮「已知问题」14 条（2026-10-17，v0.6.1）

**背景**：用户看朋友共享屏幕玩 v0.6.0，把问题记在 `design\已知问题.txt`（14 条，未带日志）。
全部按代码定位修复；本轮是 **v0.6.0 Boss 的第一轮实机反馈**。

### 1. 光道龙 格拉古尼斯：斩杀回手仍不是0费（**v0.5.4 的修法是错的**）

- **根因**：`CardModel.OnPlayWrapper` 在 OnPlay 返回后执行 `EnergyCost.AfterCardPlayedCleanup()` =
  `RemoveAll(m => m.Expiration.HasFlag(WhenPlayed))`。v0.5.4 改用的 `SetToFreeThisTurn()`
  = `SetThisTurnOrUntilPlayed(0)`，其 Expiration=`EndOfTurn|WhenPlayed`，**HasFlag(WhenPlayed) 为 true**
  → 同样被当场删掉。v0.5.4 注释里"EndOfTurn 位能让它存活"的判断错误。
- **修复**：改用 `EnergyCost.SetThisTurn(0)`（Expiration=EndOfTurn，不含 WhenPlayed）+ `InvokeEnergyCostChanged()`。
  回合结束自然失效，语义仍是"临时0费"。

### 2. 三层 Boss 优先格拉法（朋友没打过格拉法却出女王）

- **根因**：`RunManager.GenerateRooms` → `ActModel.ApplyDiscoveryOrderModifications` 会把
  `Glory.BossDiscoveryOrder` 里**第一个未见过**的 Boss 强制成本局 Boss；原版列表只有女王/试验体/万象玻璃，
  mod Boss 不在其中。RitsuLib 的 `BossDiscoveryOrderPostfix` 只做 act 有效性过滤，不追加 mod Boss。
  所以没打过格拉法的玩家必先见女王/其他原版 Boss，格拉法只能等三个原版都见过后靠随机。
- **修复**：新增 `DarkWorldGraphaDiscoveryPatch`（Entry 注册）——给 `Glory.BossDiscoveryOrder` 的
  **具体 getter** 挂 postfix，把格拉法插到结果最前。`ApplyDiscoveryOrderModifications` 读到的是这个 getter，
  因此未见过时必出格拉法；见过一次后自动回落到原版顺序。

### 3. 四神将改为诅咒卡，打出时伤害指向玩家

- `DarkWorldAttackCard`：`1费 / CardType.Curse / CardRarity.Curse / TargetType.None`（保留 Retain）；
  `OnPlay` 的 `DamageCmd.Attack(...).Targeting(Owner.Creature)`——固定打自己。
- **副作用（有意）**：「暗黑界的诱惑」的被动分支按**第一张牌类型**结算，四神将从 Attack 变 Curse 后，
  弃置它们会走 default 分支（复制同名牌洗入抽牌堆），不再给 Boss 力量。这是类型改成诅咒后的自然结果。
- 文案四条统一为"打出时：对自己造成X点伤害。" + 弃置效果。

### 4. 龙神回归（用户称"龙神的吸收"）

- 吸收范围：抽牌堆 + 弃牌堆 **+ 消耗堆**；回血 **30 → 50/张**。
- 意图 `DarkWorldReturnIntent` 的 `Amount` 用同一常量，数字自动同步；`CountAbsorbableCards` 同步加消耗堆。

### 5. 暗黑界的诱惑：弃光不触发

- **根因**：只监听了 `AfterCardDiscarded`（手牌弃置），弃光走 `CardPileCmd.Add(Draw→Discard)` 不经过它。
- **修复**：新增 `AfterCardChangedPiles` 覆写，判 `old=Draw && new=Discard` 后走同一 `TryTrigger`。
  两条钩子互斥（原版源码实证），`_triggeredThisTurn` 仍保证每玩家回合一次。能力描述同步
  "第一次弃置或弃光卡牌时…随机暗黑界**诅咒**卡"。

### 6-8. 数值

- 光道之龙：费用 1→0，伤害 9→6（升级仍 +4）。
- 光道恶魔 魏丝：追加 `BlockVar(8)`，敲后 +4（8/12），描述插入 `{Block:diff()}`。
- 光道天使 基路伯：`DamageVar` 4→5 → 5×3 / 敲后 5×4（升级仍是 Hits+1）。

### 9-12 / 14. 文案与 Token

- 太阳交换：已有 `IsPlayable` 要求手牌有「光道」→ 删"（若有）"。
- 惩戒之龙：删"（人工制品可抵挡）"（行为不变：PowerType.Debuff 本来就被人工制品挡）。
- 虚影依 神子晶：删"（不触发其被弃置时效果）"（DiscardExhaust 本来就不触发）。
- 神影依融合：删"（将这张牌额外打出1次）"（重放定义本身如此）。
- 光道的裁决：`CreateToken<JudgementDragon>` 去掉 `retain: true`；基础 Token 只有消耗，
  敲后 `UpgradeInternal` 会让裁决之龙自带「保留」。描述删"保留、"。

### 13. 光道战士 加洛斯：**行为本来就是来源=光道牌，只改文案**

- 代码：`LsUtil.Mill(ctx, source, n)` 里 `if (IsLs(source))` 才通知 `GarothPower.OnLightswornMilled`；
  追加弃光2走 `MillCore(garothAny:false)`；强化版按**追加弃光的那2张里**的光道数抽牌——与用户描述一致。
- 文案原写「每当『光道』牌**被**弃光后」有歧义（像"光道牌被弃"），改为「每当『光道』牌弃光后」。
- 顺手补守卫：本次弃光 0 张（抽牌堆空）不触发加洛斯，避免空触发。

### 验证

- 构建 0 错误；0.107 refs 试编译（`-p:LsCompatTrial=true`）0 错误；
  memberref 审计 0.107.1 + 0.111.0 **双 PASS**（methods=228）。
- pck 解包核对：GAROTH/WEISS/DECREE/TOHUSHADDOLL_GRYSTA/EL_SHADDOLL_FUSION/四张 DARK_WORLD/GOLDD
  与 temptation 能力描述逐字正确。
- 0.107.1 实机：`Version=0.6.1`、`Lightsworn mod initialized!`、core 4 patches applied / 0 failed、
  无 LocException / 无 Lightsworn 异常。
- 产物：dll `635ccab5…`(385536) / pck `d869dde6…`(22938216)；**未上传工坊**。

---

## v1.52 动态数值显示：光道龙 / 光道圣灵（2026-10-17，v0.6.2）

**需求**：用户要求两张卡的数值像战士「完美打击」一样在卡面动态变化。

### 实现（完美打击 / 堆栈范式）

| 卡 | 变量 | 卡面文本 |
|---|---|---|
| 光道龙 格拉古尼斯 | `CalculationBaseVar(18)` + `ExtraDamageVar(2)` + `CalculatedDamageVar(Move).WithMultiplier(弃牌堆光道数)` | `造成{CalculatedDamage:diff()}点伤害。弃牌堆中每有1张「光道」牌，伤害+{ExtraDamage:diff()}。` |
| 光道圣灵 夏尔 | `CalculationBaseVar(8)` + `CalculationExtraVar(1)` + `CalculatedBlockVar(Move).WithMultiplier(弃牌堆光道数)` | `获得{CalculatedBlock:diff()}点格挡。弃牌堆中每有1张「光道」牌，格挡+{CalculationExtra:diff()}。` |

- 结算：光道龙 `DamageCmd.Attack(DynamicVars.CalculatedDamage)`（原版专为动态伤害提供的重载，在每段结算时重新 `Calculate`）；
  夏尔 `CreatureCmd.GainBlock(..., CalculatedBlock.Calculate(cardPlay.Target), CalculatedBlock.Props, cardPlay)`。
- 升级保持原数值：光道龙 `CalculationBase +4` / `ExtraDamage +1`（18/22、+2/+3）；夏尔 `CalculationBase +2`（8/10、+1 不变）。
- **已知预览差**：光道龙在手牌里的动态数字按"当前弃牌堆"计算，而实际伤害在本次弃光3之后结算，
  所以实际伤害可能比手牌预览高（最多3张光道）。这是"自身先弃光再伤害"的固有顺序，预览无法预知弃光内容。
- 工具链：`tools\gen_card_doc.py` 已支持 `CalculationBaseVar/CalculationExtraVar/ExtraDamageVar/CalculatedDamageVar/CalculatedBlockVar`
  的解析；卡牌图鉴重新生成（v0.6.2）。SPECIAL 同步修正 Decree（去掉"保留"）与 ElShaddollFusion（去掉重放括号解释）两条旧覆盖。

### 验证

- 构建 0 错误；0.107 试编译 PASS；memberref 双 PASS（methods=241）。
- 0.107.1 实机 v0.6.2 加载零异常；用户实机查看卡面确认"没问题"。
- 产物 dll `ef46c924…`(386048) / pck `d7e92839…`(22938216)；**未上传工坊**。

---

## v1.53 格拉法战斗立绘换图（2026-10-17，v0.6.3）

**用户素材**：`D:\download\chrome_download\光道mod素材\暗黑界的龙神王\暗黑界的龙神王 格拉法.png`
（用户重新抠图，替代旧版白边/锯齿明显的立绘）。

- 新图：**1536×1536 RGBA**，内容 alpha bbox = `(52,296)-(1505,1339)`（可见区 **1453×1043**，与旧图 1456×1044 几乎一致）。
- 直接覆盖 `lightsworn\images\monsters\dark_world_grapha.png`（路径/AssetProfile 不变），
  先 `Godot --headless --import` 重导（坑13），再 ExportPck。
- `TryCreateCreatureVisuals` 对位修正（Sprite2D 居中锚点）：
  - `Position.Y = -285.5`：内容底边相对纹理中心 571px × 0.5 = 285.5 → 脚底仍贴场景原点；
  - `Position.X = -5.25`：内容中心相对纹理中心偏右 10.5px × 0.5 → 视觉居中；
  - `Scale` 仍 0.5，可见区约 727×522；`CenterPos/Bounds/IntentPos/TalkPos` 不变。
- 验证：pck 内 `.godot/imported/dark_world_grapha.png-5301…ctex` 解出 1536×1536，与原图**逐像素 diff=None**；
  构建 0 错误、memberref 双 PASS（methods=241）、0.107.1 实机 `Version=0.6.3` 加载零异常。
- 产物 dll `8f238246…`(386048) / pck `5d82d0dc…`(22983560)。
- **已发布**：git `5af0ff4` 已推送；创意工坊 v0.6.3 上传成功（ManifestID `4204301308830997520`，2026-10-17 22:55）。
