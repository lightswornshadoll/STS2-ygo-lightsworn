# -*- coding: utf-8 -*-
"""v0.6.4 工坊条目元数据更新：格拉法平衡调整。"""
import io
import json

p = r"D:\1-workdata\lightsworn_mod-tools\workshop\lightsworn\workshop.json"

with io.open(p, encoding='utf-8') as f:
    d = json.load(f)

old = "【三层Boss】暗黑界的龙神王 格拉法：800血（进阶880），6招固定循环；塞暗黑界卡污染手牌、弃牌按牌型触发被动、龙神回归吸卡回血；四神将诅咒卡不进卡牌奖励/商店，洗脑状态可被人工制品挡住。"
new = "【三层Boss】暗黑界的龙神王 格拉法：800血（进阶880），6招固定循环；战斗开始塞2张暗黑界诅咒到手牌（进阶3张），每从手牌弃2张再塞1张；弃牌按牌型触发被动、龙神回归吸卡回血；四神将诅咒卡不进卡牌奖励/商店，洗脑状态可被人工制品挡住。"
if old in d['description']:
    d['description'] = d['description'].replace(old, new, 1)
else:
    print('WARN: boss description block not found; left unchanged')

d['changeNote'] = (
    "v0.6.4 格拉法平衡调整（朋友 N0 3 回合击杀反馈）\n"
    "【起手压力】\n"
    "· 战斗开始时将 2 张随机暗黑界诅咒置入你的手牌（高进阶 3 张）\n"
    "· 新能力「暗黑界的侵蚀」：每从手牌弃置 2 张，生成 1 张随机暗黑界诅咒到手牌（余数保留）\n"
    "【伤害】\n"
    "· 暗黑界之雷 10×3（进阶 12×3）；暗黑界的军势 13（进阶 14）；暗黑界的登极 39（进阶 43）\n"
    "【取引】\n"
    "· 保留 5 虚弱/易伤；改为生成 2 张暗黑界诅咒到手牌，然后弃置手牌中所有暗黑界诅咒\n"
    "【洗脑】\n"
    "· 数量改为 ceil(当前回合/2)：第一次 3 张，第二次 6 张；意图数字动态显示\n"
    "【被动】\n"
    "· 「暗黑界的诱惑」弃到攻击卡时 +1 力量 → +2 力量\n"
    "· 龙神回归仍为 50/张，Boss 血量仍为 800/880\n"
    "! 联机时所有玩家必须安装【同版本】本 mod + RitsuLib 前置（请让朋友一起更新到 v0.6.4）"
)

with io.open(p, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(d, f, ensure_ascii=False, indent=4)
    f.write('\n')

print('workshop.json updated')
print('boss desc updated:', new in d['description'])
print('changeNote head:', d['changeNote'][:60])
