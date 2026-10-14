# 设计文档尾部追加 v0.4.26 变更记录（一次性脚本）
import io

DOC = r"D:\1-workdata\lightsworn_mod\design\光道mod设计文档.md"
record = """

---

## v0.4.26（2026-10-11）：事件「于珍珠世界相逢」+ 遗物「猫狗双全」（用户点名两张素材图）

**事件：于珍珠世界相逢**（首个自定义事件，Scripts\\Events.cs，mod 新增 localization\\zhs\\events.json）：
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
  左右羽化 80px 合成（tools\\make_pearl_event_art.py）。路径=res://lightsworn/images/events/pearl_world_encounter.png
  （CustomInitialPortraitPath 覆写；**新 PNG 必须先 Godot --headless --import 再 ExportPck**）。
- 实测捷径：run 中控制台 `event LIGHTSWORN-PEARL_WORLD_ENCOUNTER` 直达（EventConsoleCmd 按 Id.Entry 匹配）。

**遗物：猫狗双全**（CatsAndDogs，普通/Common，进光道遗物池掉落+商店 175）：
- 效果=每当抽到「光道兽 沃尔夫」或「光道弓手 费莉丝」时再抽 1 张。实现=覆写
  `AfterCardDrawn(ctx, card, fromHandDraw)`——**该钩子的监听者含玩家全部未熔解遗物**（CombatState.IterateHookListeners
  实证），fromHandDraw 不筛（回合抽牌/效果抽到都触发）；连锁抽到继续触发（CardPileCmd.Draw 自带
  手牌上限/洗牌/空堆检查，天然终止）；`card.Owner != Owner` 过滤他玩家。
- 图标=素材中央金环徽章圆裁 256/64（径向中值+最小二乘拟合圆心 r=476，tools\\make_catdog_relic_icon.py），
  **右下角「豆包AI生成」水印用整块横向克隆（同高度干净区 830..1050）+羽化+残条洋葱填充修掉**，
  去水印整图存 `D:\\download\\chrome_download\\光道mod素材\\猫狗双全_去水印.png`（素材库备用，不入 mod）。

**验证**：v0.4.26 加载无异常（checklog：Version=0.4.26.0 + Lightsworn mod initialized + NO RELEVANT
ERRORS；pck 内 events.json/立绘 ctex/遗物图标 ctex 齐全）。
"""

text = io.open(DOC, encoding="utf-8").read()
if "v0.4.26（2026-10-11）" in text:
    print("already appended, skip")
else:
    io.open(DOC, "a", encoding="utf-8").write(record)
    print("appended v0.4.26 record")
