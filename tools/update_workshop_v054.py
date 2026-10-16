# -*- coding: utf-8 -*-
"""v0.5.4 工坊条目元数据更新：changeNote 换成 v0.5.4 更新说明（六条修复 + 卡面文案定稿）。"""
import io, json

p = r"D:\1-workdata\lightsworn_mod-tools\workshop\lightsworn\workshop.json"

d = json.load(io.open(p, encoding='utf-8'))

d['changeNote'] = (
    "v0.5.4 六条修复 + 卡面文案定稿（全部为修复，无卡牌ID变更，旧存档兼容）\n"
    "· 修复「光道龙 格拉古尼斯」斩杀后牌回到手牌但仍显示2费的问题（现在正确变为本回合0费）\n"
    "· 修复「壹世坏·让珠泪哀歌族澄澈的残响」敲前敲后效果无差别的问题（敲后拿回的牌为强化版）\n"
    "· 珠泪融合/影融素材改为严格判定：素材数量须与融合条件完全一致；选超素材的组合将作废（不消耗素材）\n"
    "· 卡面文案整理：「弃光」「除光」等机制名不再单独占一行，与数值合并写在正文里（如「弃光3」），"
    "观感对齐官方的「重放」写法；机制说明仍可在卡牌悬浮提示中查看\n"
    "· 初始卡组补牌时，打击/防御最多占 60%\n"
    "· 商店与营火处的角色形象改用本 mod 立绘（不再借用铁甲战士占位）\n"
    "! 联机时所有玩家必须安装【同版本】本mod + RitsuLib 前置（请让朋友一起更新到 v0.5.4）"
)

with io.open(p, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(d, f, ensure_ascii=False, indent=4)
    f.write('\n')

print('workshop.json updated')
print('changeNote head:', d['changeNote'][:60])
print('changeNote len:', len(d['changeNote']))
