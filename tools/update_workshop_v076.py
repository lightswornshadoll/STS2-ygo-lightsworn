# -*- coding: utf-8 -*-
"""v0.7.6 工坊条目元数据更新：提耶拉 v0.12 机制调整（含 v0.7.5 内容）。"""
import io
import json

p = r"D:\1-workdata\lightsworn_mod-tools\workshop\lightsworn\workshop.json"

with io.open(p, encoding='utf-8') as f:
    d = json.load(f)

d['changeNote'] = (
    "v0.7.6 提耶拉机制调整（含 v0.7.5 内容）\n"
    "【v0.7.5】\n"
    "· 逆生命树：每名玩家每弃置30张牌，将1张随机狱火机诅咒洗入抽牌堆；随机生成优先未拥有的种类\n"
    "【v0.7.6】\n"
    "· 莉莉丝诅咒：改为弃置手牌中所有技能牌；拿玛诅咒：改为弃置手牌中所有攻击牌\n"
    "· 10N 触发：弃光手牌，但不再每弃1张生成1张诅咒\n"
    "· 拿玛重置：不再把消耗堆中的狱火机诅咒放回弃牌堆；只清空种类/阈值记录并把节点重置为 N\n"
    "· 十进管诅咒：没有「被弃置时」效果，也不计入引爆种类\n"
    "· 虚梦/灾天：额外6张燃料只看该玩家本回合是否生成过融合卡，不再检查消耗堆\n"
    "【兼容】\n"
    "· 版本号 0.7.6；联机时所有玩家必须安装【同版本】本 mod + RitsuLib 前置\n"
    "· 旧存档可继续使用"
)

with io.open(p, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(d, f, ensure_ascii=False, indent=4)
    f.write('\n')

print('workshop.json updated')
print('changeNote head:', d['changeNote'][:50])
