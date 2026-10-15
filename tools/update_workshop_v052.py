# -*- coding: utf-8 -*-
"""v0.5.2 工坊条目元数据更新：description 遗物数 3→4；changeNote 换成 v0.5.2 更新说明。"""
import io, json

p = r"D:\1-workdata\lightsworn_mod-tools\workshop\lightsworn\workshop.json"

d = json.load(io.open(p, encoding='utf-8'))

old_desc = d['description']
assert '+ 3遗物 + 1事件' in old_desc, old_desc[:200]
d['description'] = old_desc.replace('+ 3遗物 + 1事件', '+ 4遗物 + 1事件')

d['changeNote'] = (
    "v0.5.2 事件「于珍珠世界相逢」重做 + 新遗物「幻色珍珠」\n"
    "· 事件换新立绘；剧情文案重写（梅洛改成活泼、小美人鱼改成安静的人设对调）\n"
    "· 事件选项二不再是给金币，改为获得新事件遗物「幻色珍珠」：拾起时随机变成金色珍珠(+150金币)或诅咒珍珠(+1贪婪+333金币)的效果，"
    "另有1%概率是发光珍珠(每场战斗第一回合加入1张冷光到手牌)的效果\n"
    "· 修复「雪之化身」会作为金卡出现在战斗奖励/尘封魔典里（它只是战斗内令牌）\n"
    "· 修复光道召唤师/暮光道萨满可以在没弃置/没消耗时白拿卡（现在必须付出代价才能发动）\n"
    "! 联机时所有玩家必须安装【同版本】本mod + RitsuLib 前置"
)

with io.open(p, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(d, f, ensure_ascii=False, indent=4)
    f.write('\n')

print('workshop.json updated')
print('desc has 4遗物:', '+ 4遗物 + 1事件' in d['description'])
print('changeNote head:', d['changeNote'][:40])
