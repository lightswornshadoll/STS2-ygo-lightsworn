# -*- coding: utf-8 -*-
"""v0.6.5 工坊条目元数据更新：格拉法地图图标修复 + 三层 Boss 抉择事件。"""
import io
import json

p = r"D:\1-workdata\lightsworn_mod-tools\workshop\lightsworn\workshop.json"

with io.open(p, encoding='utf-8') as f:
    d = json.load(f)

old_events = "+ 6遗物（含初始/先古/事件）+ 1事件。"
new_events = "+ 6遗物（含初始/先古/事件）+ 2事件（珍珠世界 / 岔路：第三层的王座）。"
if old_events in d['description']:
    d['description'] = d['description'].replace(old_events, new_events, 1)
else:
    print('WARN: event count block not found; left unchanged')

old_boss = "【三层Boss】暗黑界的龙神王 格拉法：800血（进阶880），6招固定循环；"
new_boss = "【三层Boss】暗黑界的龙神王 格拉法：800血（进阶880），6招固定循环；第二层战后可在「岔路：第三层的王座」选择第三层走 mod 首领或原版首领池；"
if old_boss in d['description']:
    d['description'] = d['description'].replace(old_boss, new_boss, 1)
else:
    print('WARN: boss description block not found; left unchanged')

d['changeNote'] = (
    "v0.6.5 地图图标修复 + 三层首领抉择事件\n"
    "【修复】\n"
    "· 修复第三层地图上龙神王（格拉法）节点不显示图标的问题；现在与原版 Boss 一样显示专属地图图标\n"
    "【新事件】\n"
    "· 「岔路：第三层的王座」：第二层首领战后、第三层地图出现前触发\n"
    "· 可选择第三层首领从【mod 首领】或【原版首领】池中随机（进阶双 Boss 同步处理）\n"
    "· 多人联机为全队共享选择，所有玩家投票/确认后生效\n"
    "【兼容】\n"
    "· 版本号 0.6.5；联机时所有玩家必须安装【同版本】本 mod + RitsuLib 前置（请让朋友一起更新到 v0.6.5）\n"
    "· 旧存档可继续使用"
)

with io.open(p, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(d, f, ensure_ascii=False, indent=4)
    f.write('\n')

print('workshop.json updated')
print('event count updated:', new_events in d['description'])
print('boss desc updated:', new_boss in d['description'])
print('changeNote head:', d['changeNote'][:80])
