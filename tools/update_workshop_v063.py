# -*- coding: utf-8 -*-
"""v0.6.3 工坊条目元数据更新：changeNote 覆盖 v0.6.1/v0.6.2/v0.6.3，四神将描述改为诅咒卡。"""
import io
import json

p = r"D:\1-workdata\lightsworn_mod-tools\workshop\lightsworn\workshop.json"

with io.open(p, encoding='utf-8') as f:
    d = json.load(f)

desc = d['description']
assert '四神将攻击卡' in desc, 'description 里没找到“四神将攻击卡”'
desc = desc.replace('四神将攻击卡不进卡牌奖励/商店', '四神将诅咒卡不进卡牌奖励/商店', 1)
d['description'] = desc

d['changeNote'] = (
    "v0.6.3 格拉法新战斗立绘 + v0.6.2 动态数值 + v0.6.1 朋友实机14条修复\n"
    "【v0.6.3】\n"
    "· 三层 Boss「暗黑界的龙神王 格拉法」战斗立绘换用重绘版（去除旧图白边/锯齿）\n"
    "【v0.6.2】\n"
    "· 光道龙 格拉古尼斯：伤害改为动态显示（18/22 + 弃牌堆每张「光道」+2/+3），卡面直接显示当前总值\n"
    "· 光道圣灵 夏尔：格挡改为动态显示（8/10 + 弃牌堆每张「光道」+1）\n"
    "【v0.6.1 修复（朋友实机反馈）】\n"
    "· 光道龙斩杀回手后费用现在会真正变为0（之前只回手、费用不变）\n"
    "· 未见过格拉法时，三层 Boss 现在会优先出现格拉法（打过一次后恢复原版顺序；仅新开的局生效）\n"
    "· 四神将改为诅咒卡：打出时伤害指向自己；「暗黑界的诱惑」弃置它们时改为复制同名牌（不再给 Boss 力量）\n"
    "· 龙神回归吸收范围追加消耗堆，回血 30→50/张\n"
    "· 「暗黑界的诱惑」现在弃光也会触发（不再只限手牌弃置）\n"
    "· 光道之龙 0费/6伤；光道恶魔 魏丝 +8/12格挡；光道天使 基路伯 5×3/5×4\n"
    "· 光道的裁决生成的裁决之龙不再带「保留」（敲后版本自带保留）；太阳交换/惩戒之龙/虚影依/神影依融合删去多余括号说明\n"
    "· 加洛斯文案改为「光道牌弃光后」（行为不变）\n"
    "! 联机时所有玩家必须安装【同版本】本 mod + RitsuLib 前置（请让朋友一起更新到 v0.6.3）"
)

with io.open(p, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(d, f, ensure_ascii=False, indent=4)
    f.write('\n')

print('workshop.json updated')
print('desc has 四神将诅咒卡:', '四神将诅咒卡' in d['description'])
print('changeNote head:', d['changeNote'][:50])
