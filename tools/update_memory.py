# 更新记忆文件 lightsworn-sts2-mod.md：版本行 + 插入 v0.4.26 段落
import io

p = r'C:\Users\light\.zcode\cli\memories\projects\default-151545a626f02190\memory\lightsworn-sts2-mod.md'
t = io.open(p, encoding='utf-8').read()
assert 'v0.4.25' in t
t = t.replace('（2026-10 v0.4.25，102张卡+2遗物；', '（2026-10 v0.4.26，102张卡+3遗物+1事件；', 1)
t = t.replace('当前 **v0.4.25**（2026-10-11，102张卡+2遗物）', '当前 **v0.4.26**（2026-10-11，102张卡+3遗物+1事件）', 1)

newpara = '''**v0.4.26（2026-10-11）首个自定义事件+第三遗物**（用户给两张素材图点名）：**事件「于珍珠世界相逢」**（Scripts\\Events.cs + mod localization\\zhs\\events.json 新文件）：BaseLib CustomEventModel 范式——**BaseLib 不会反射实例化事件类，必须 Entry.Init 里手动 new**；Acts=[]=任意幕共享池，IsAllowed 限定全玩家 LightswornCharacter；非共享=各玩家独立选。选项一=三张珠泪人鱼入卡组（RunState.CreateCard+CardPileCmd.Add(Deck)+PreviewCardPileAdd，TheLegendsWereTrue 范式），选项二=100金币（原版无代价给金档 LostWisp60/TrashHeap100/TheLanternKey100；GoldVar+选项描述{Gold} 由 NEventOptionButton 自动渲染）。**事件ID=LIGHTSWORN-PEARL_WORLD_ENCOUNTER**（GetPrefix=命名空间首段大写+'-'，Entry=类名蛇形；选项键=方法名蛇形，CustomEventModel.Option(方法组) 自动拼）。**事件立绘规格=3440×1613**（Godot无头读原版ctex实测；填满默认布局%Portrait 2560×1200 KeepAspectCentered框）；素材合成=cover模糊底+等高居中前景+左右羽化（tools\\make_pearl_event_art.py）。run中控制台 `event LIGHTSWORN-PEARL_WORLD_ENCOUNTER` 直达。**遗物「猫狗双全」CatsAndDogs（Common）**：抽到沃尔夫/费莉丝再抽1张=覆写 AfterCardDrawn（**监听者含玩家全部未熔解遗物**，CombatState.IterateHookListeners 实证）；fromHandDraw 不筛；连锁抽到继续触发（Draw 自带手牌上限/洗牌/空堆终止）。图标=素材中央金环徽章圆裁256/64（径向中值+最小二乘拟合圆，tools\\make_catdog_relic_icon.py）；「豆包AI生成」水印=同高度干净区整块横向克隆+羽化修掉，去水印整图存素材目录。验证：v0.4.26 加载无异常、pck 含 events.json/立绘ctex/图标ctex。

'''
anchor = '**v0.4.25（2026-10-11）珠泪融合产出神子晶**'
assert anchor in t
t = t.replace(anchor, newpara + anchor, 1)
io.open(p, 'w', encoding='utf-8').write(t)
print('memory updated OK')
