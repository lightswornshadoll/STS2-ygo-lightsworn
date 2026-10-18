# -*- coding: utf-8 -*-
"""v0.7.3 工坊条目元数据更新：提耶拉 Boss + 最远方的宇宙事件 + 已知问题四条。"""
import io
import json

p = r"D:\1-workdata\lightsworn_mod-tools\workshop\lightsworn\workshop.json"

with io.open(p, encoding='utf-8') as f:
    d = json.load(f)

old_events = "2事件（珍珠世界 / 岔路：第三层的王座）"
new_events = "2事件（珍珠世界 / 最远方的宇宙）"
assert old_events in d['description'], 'event block not found'
d['description'] = d['description'].replace(old_events, new_events, 1)

old_boss = (
    "【三层Boss】暗黑界的龙神王 格拉法：800血（进阶880），6招固定循环；第二层战后可在「岔路：第三层的王座」"
    "选择第三层走 mod 首领或原版首领池；战斗开始塞2张暗黑界诅咒到手牌（进阶3张），每从手牌弃2张再塞1张；"
    "弃牌按牌型触发被动、龙神回归吸卡回血；四神将诅咒卡不进卡牌奖励/商店，洗脑状态可被人工制品挡住。"
)
new_boss = (
    "【三层Boss】三层共有两位 mod 首领：①暗黑界的龙神王 格拉法：800血（进阶880），6招固定循环；"
    "战斗开始塞2张暗黑界诅咒到手牌（进阶3张），每从手牌弃2张再塞1张；弃牌按牌型触发被动、龙神回归吸卡回血；"
    "四神将诅咒卡不进卡牌奖励/商店；洗脑只无效攻击/技能/能力牌，可被人工制品挡住。"
    "②狱火机·提耶拉 / 创星神·提耶拉：点数=融合素材数（3/5/8/10），诅咒牌被弃置时引爆；"
    "二阶段「创星神」灭世机制；多人联机节点/创星条共享、按玩家人数缩放。"
    "第二层战后在「最远方的宇宙」事件选择：踏入宇宙→mod 首领池，留在原地→原版首领池。"
)
assert old_boss in d['description'], 'boss block not found'
d['description'] = d['description'].replace(old_boss, new_boss, 1)

d['changeNote'] = (
    "v0.7.3 已知问题修复 + 三层新 Boss「狱火机·提耶拉」\n"
    "【新增 Boss】三层第二 Boss：狱火机·提耶拉 / 创星神·提耶拉\n"
    "· 点数=融合素材数（3/5/8/10），诅咒牌被弃置时引爆；Boss 每招塞 1 张诅咒\n"
    "· 二阶段「创星神」：创星条蓄满即灭世；多人联机节点/创星条共享、按人数缩放\n"
    "【事件】「最远方的宇宙」（原「岔路：第三层的王座」）\n"
    "· 新立绘与剧情：星光璀璨的宇宙，选择踏入（mod 首领池）或留在原地（原版首领池）\n"
    "· 结局页不再提前显示第三层 Boss 名字\n"
    "【修复/调整】\n"
    "· 格拉法的洗脑改为只无效攻击/技能/能力牌；诅咒/状态（含自动打出的「暗黑界的洗脑」）照常结算\n"
    "· 惩戒之龙：负面状态池移除脆弱（易伤/虚弱/中毒/灾厄），每次有 1% 概率改为击晕所有敌人\n"
    "· 暗黑界诅咒牌打出伤害减半：鬼神 6 / 斗神 4 / 军神 5 / 武神 5（被弃置时的效果不变）\n"
    "【兼容】\n"
    "· 版本号 0.7.3；联机时所有玩家必须安装【同版本】本 mod + RitsuLib 前置（请让朋友一起更新到 v0.7.3）\n"
    "· 旧存档可继续使用"
)

with io.open(p, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(d, f, ensure_ascii=False, indent=4)
    f.write('\n')

print('workshop.json updated')
print('event name updated:', new_events in d['description'])
print('boss desc updated:', new_boss in d['description'])
print('changeNote head:', d['changeNote'][:60])
