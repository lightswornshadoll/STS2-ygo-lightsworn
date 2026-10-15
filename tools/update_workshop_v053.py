# -*- coding: utf-8 -*-
"""v0.5.3 工坊条目元数据更新：changeNote 换成 v0.5.3 更新说明（本次为联机实战四连修）。"""
import io, json

p = r"D:\1-workdata\lightsworn_mod-tools\workshop\lightsworn\workshop.json"

d = json.load(io.open(p, encoding='utf-8'))

d['changeNote'] = (
    "v0.5.3 联机实测修复：卡牌卡在空中 / 融合融不出来 / 能力没名字 / 图标占位\n"
    "· 修复一批卡牌与融合在【正式版 0.107.1】上会中途报错的问题：表现为打出的牌卡在半空不落地、"
    "影依/珠泪融合满足条件却融不出来（正式版专属 bug，beta 分支不受影响）\n"
    "· 修复能力（增益/减益图标）的名字与描述显示不出来\n"
    "· 修复「光道暗杀者 莱登」的临时力量图标显示为占位图\n"
    "! 联机时所有玩家必须安装【同版本】本mod + RitsuLib 前置（请让朋友一起更新到 v0.5.3）"
)

with io.open(p, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(d, f, ensure_ascii=False, indent=4)
    f.write('\n')

print('workshop.json updated')
print('changeNote head:', d['changeNote'][:60])
