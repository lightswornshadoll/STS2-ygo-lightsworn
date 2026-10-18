# -*- coding: utf-8 -*-
"""v0.7.4 工坊条目元数据更新：三层事件立绘高清重制。"""
import io
import json

p = r"D:\1-workdata\lightsworn_mod-tools\workshop\lightsworn\workshop.json"

with io.open(p, encoding='utf-8') as f:
    d = json.load(f)

d['changeNote'] = (
    "v0.7.4 三层事件立绘高清重制\n"
    "【美术】\n"
    "· 「最远方的宇宙」事件立绘换成更高清素材（1536×1337 原图 → 3440×1613 画布），星空细节更锐利\n"
    "【兼容】\n"
    "· 版本号 0.7.4；联机时所有玩家必须安装【同版本】本 mod + RitsuLib 前置（请让朋友一起更新到 v0.7.4）\n"
    "· 旧存档可继续使用"
)

with io.open(p, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(d, f, ensure_ascii=False, indent=4)
    f.write('\n')

print('workshop.json updated')
print('changeNote head:', d['changeNote'][:50])
