# -*- coding: utf-8 -*-
"""v0.6.0 工坊条目元数据更新：加三层 Boss 说明、遗物数 4→6、changeNote 覆盖 0.5.5/0.5.6/0.6.0。"""
import io, json

p = r"D:\1-workdata\lightsworn_mod-tools\workshop\lightsworn\workshop.json"

with io.open(p, encoding='utf-8') as f:
    d = json.load(f)

desc = d['description']
assert '+ 4遗物 + 1事件' in desc, desc[:300]
desc = desc.replace('+ 4遗物 + 1事件', '+ 6遗物（含初始/先古/事件）+ 1事件')
boss_line = (
    "【三层Boss】暗黑界的龙神王 格拉法：800血（进阶880），6招固定循环；"
    "塞暗黑界卡污染手牌、弃牌按牌型触发被动、龙神回归吸卡回血；"
    "四神将攻击卡不进卡牌奖励/商店，洗脑状态可被人工制品挡住。\n"
)
marker = "【联机】"
assert marker in desc
desc = desc.replace(marker, boss_line + marker, 1)
d['description'] = desc

d['changeNote'] = (
    "v0.6.0 三层 Boss「暗黑界的龙神王 格拉法」+ v0.5.5/v0.5.6 内容（工坊从 v0.5.4 直接升级）\n"
    "【v0.6.0 新内容】\n"
    "· 新增三层 Boss「暗黑界的龙神王 格拉法」：800血（进阶880），6招循环（雷8×3+3易伤/虚弱→军势10+塞3卡→登极30→龙神回归吸卡每张回30→取引5/5+抽2弃2→洗脑塞3状态）\n"
    "· 被动「暗黑界的诱惑」：每回合第一次弃置按第一张牌类型触发（攻击+1力量/技能塞洗脑/能力随机弃2/其他复制同名牌），并额外塞1张随机暗黑界攻击卡；回合结束清理不触发\n"
    "· 四神将（鬼神/斗神/军神/武神）：1费攻击·保留，被弃置时有各自代价；Token 稀有度不进图鉴，不会出现在卡牌奖励/商店/变形\n"
    "· 洗脑状态：抽到自动打出，下一张牌无效（费用照付、效果不生效），人工制品可挡；能力牌被无效时不再卡在空中\n"
    "· 进阶强化：血量800→880，雷8→9、军势10→11、登极30→33（意图同步显示）\n"
    "【v0.5.6 订正】\n"
    "· 神光之龙敲后只加「保留」不加伤害；多段伤害统一官方句式「对所有敌人造成X点伤害Y次」；双龙敲后用「裁决之龙+ / 惩戒之龙+」写法\n"
    "· 修复百科大全「初始」页看不到圣徽/光道权杖（LocalStartingRelics 四件齐全，实际仍只持有二选一结果）\n"
    "【v0.5.5 内容】\n"
    "· 雷喵基础拿3/敲后去消耗；裁决/惩戒伤害30、敲后保留；双龙敲后生成强化版；神光30×3；惩戒只回收攻击/技能/能力牌\n"
    "· 游戏王与圣徽改为初始遗物二选一；新增先古遗物「更好的游戏王」与「光道权杖」（欧洛巴斯之触精炼）\n"
    "! 联机时所有玩家必须安装【同版本】本mod + RitsuLib 前置（请让朋友一起更新到 v0.6.0）"
)

with io.open(p, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(d, f, ensure_ascii=False, indent=4)
    f.write('\n')

print('workshop.json updated')
print('desc has boss:', '暗黑界的龙神王' in d['description'])
print('desc has 6 relics:', '6遗物' in d['description'])
print('changeNote head:', d['changeNote'][:60])
