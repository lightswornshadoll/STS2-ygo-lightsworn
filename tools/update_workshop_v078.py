# -*- coding: utf-8 -*-
"""v0.7.8 工坊条目元数据更新：提耶拉撒旦/0级十进管 + 状态牌/阈值/格拉法策略调整。"""
import io
import json

p = r"D:\1-workdata\lightsworn_mod-tools\workshop\lightsworn\workshop.json"

with io.open(p, encoding='utf-8') as f:
    d = json.load(f)

d['changeNote'] = (
    "v0.7.8 提耶拉撒旦/0级十进管 + 状态牌、阈值与格拉法策略调整\n"
    "【v0.7.7】\n"
    "· 提耶拉新增0级十进管、1级撒旦；初始节点0；十进管复制1-10级动作\n"
    "· 诅咒池去掉十进管、加入撒旦（代价1，被弃置时除外弃牌堆1张）\n"
    "【v0.7.8】\n"
    "· 逆生命树/创星文案简化；创星数值按玩家人数动态显示\n"
    "· 阶段门「不灭之核」改名「炼狱的狂宴」\n"
    "· 3/5/8节点阈值改为达到或超过即触发；一次跨过多个阈值会依次结算\n"
    "· 提耶拉10张狱火机诅咒、格拉法四神将改为状态牌\n"
    "· 格拉法龙神回归吸收洗脑以外的暗黑界牌\n"
    "· 四神将伤害回调12/8/11/11，打出后移出战斗（不进弃牌堆/消耗堆）\n"
    "· 回归/取引/洗脑的意图悬浮说明补全\n"
    "【兼容】\n"
    "· 版本号 0.7.8；联机时所有玩家必须安装【同版本】本 mod + RitsuLib 前置\n"
    "· 旧存档可继续使用"
)

with io.open(p, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(d, f, ensure_ascii=False, indent=4)
    f.write('\n')

print('workshop.json updated')
print('changeNote head:', d['changeNote'][:60])
