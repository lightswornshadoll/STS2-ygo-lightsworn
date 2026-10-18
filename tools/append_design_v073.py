# -*- coding: utf-8 -*-
"""v0.7.3：向设计文档尾部追加变更记录（已知问题.txt 四条）。"""
import io
import os

p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                 'design', '光道mod设计文档.md')

record = '''
---

## v1.56 第四十四轮「已知问题」4 条（2026-10-18，v0.7.3）

1. **格拉法的洗脑只无效攻击/技能/能力牌**（`DarkWorldGrapha.cs` 的 `ModifyCardPlayCount`）：
   白名单判定 `card.Type is Attack or Skill or Power`；诅咒与状态（含抽到时自动打出的「暗黑界的洗脑」本身）
   照常结算，不再被吞、也不消耗层数。文案同步：能力词条与状态卡描述改为「下一张攻击、技能或能力牌无效」。
2. **三层 Boss 抉择事件换立绘与文案**（`Act3BossChoice.cs` + `localization/{zhs,eng}/events.json`）：
   新立绘「最远方的宇宙」（`tools\\make_universe_event_art.py`：1248×1248 中心 cover 裁 2.133:1 →
   3440×1613，LANCZOS 放大）；标题/正文/选项改为「星光璀璨的宇宙，是否踏入」；选项 1 踏入=mod Boss 池、
   选项 2 停留=原版池；**结局页不再显示第三层 Boss 名字**（删除 `{Boss}` 变量注入）。
3. **惩戒之龙负面状态池**（`LsUtil.ApplyRandomDebuffs`）：移除脆弱，池=易伤/虚弱/中毒/灾厄；
   每次另有 **1%** 概率改为 `CreatureCmd.Stun` 击晕所有敌人（残响同款；不消耗人工制品）。
   卡面文案补充池与 1% 说明。
4. **暗黑界诅咒牌打出伤害减半**（`Cards9.cs`）：鬼神 12→6、斗神 8→4、军神 11→5、武神 11→5
   （11/2 向下取整，保持整数显示）；「从手牌被弃置时」的鬼神 12 点伤害不变（不是打出伤害）。

**验证**：build 0 错误；0.107 试编译 PASS；memberref 0.107.1 + 0.111.0 双 PASS（methods=286）；
pck 含 `farthest_universe.png` 与更新后的本地化；0.107.1 实机 `Version=0.7.3` 零相关异常。
实机事件（控制台 `event LIGHTSWORN_EVENT_THIRD_ACT_BOSS_CHOICE_ENCOUNTER`）立绘/文案/两个选项/结局页正常，
结局页无 Boss 名；格拉法战斗中洗脑 4 层时打出「暗黑界的鬼神」→ 玩家 78→72（6 伤，洗脑仍 4 层），
打出防御 → 费用 -1、洗脑 4→3、无格挡（技能仍被无效）。惩戒之龙的 1% 击晕为概率效果，未做逐次实测。
'''
t = io.open(p, encoding='utf-8').read()
assert '## v1.56' not in t, 'already appended'
io.open(p, 'a', encoding='utf-8', newline='').write(record)
print('设计文档已追加 v1.56')
