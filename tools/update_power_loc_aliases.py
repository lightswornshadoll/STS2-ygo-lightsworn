"""v0.5.3 修复「能力没名字/没描述」：能力本地化短键别名。

根因（2026-10-15 日志+反编译实证）：mod 的能力没有走 RitsuLib 特性注册（无 [RegisterPower]），
运行时按类型解析，ModelId.Entry = `ModelDb.GetEntry(type)` = `StringHelper.Slugify(类名)`
（游戏本体规则，**不带 mod 前缀**）——如 ShaddollHoundPower → `SHADDOLL_HOUND_POWER`。
而 powers.json 里的键是 `LIGHTSWORN_POWER_SHADDOLL_HOUND_POWER`（带前缀）→ PowerModel.Title/
Description/SmartDescription 全部取不到 → 能力名字/描述空白（BaseLib 只兜底打出原始键名）。

修复=为每个带前缀的键补一份**去掉 `LIGHTSWORN_POWER_` 前缀的别名**（同值），两套机制下都能命中；
前缀键保留（未来若给能力补 [RegisterPower] 注册仍有效）。

另：LaydenTempStrengthPower（莱登临时力量，RitsuLib ModTemporaryAppliedPowerTemplate）此前完全没有
词条（日志里 `LAYDEN_TEMP_STRENGTH_POWER.description` not found），按原版 TemporaryStrengthPower 的
中文文案补上（title 由 RitsuLib 模板走来源卡「光道暗杀者 莱登」的卡名，无需词条）。
"""
import json
import os

POWERS_JSON = os.path.join(
    os.path.dirname(__file__), '..', 'mod', 'lightsworn', 'lightsworn',
    'localization', 'zhs', 'powers.json')
PREFIX = 'LIGHTSWORN_POWER_'

with open(POWERS_JSON, encoding='utf-8') as f:
    data = json.load(f)

# 1) 生成短键别名（按原文件顺序，主键后紧跟别名，便于人工核对）
out = {}
added = 0
for k, v in data.items():
    out[k] = v
    if k.startswith(PREFIX):
        short = k[len(PREFIX):]
        if short not in data and short not in out:
            out[short] = v
            added += 1

# 2) 莱登临时力量：原版 TemporaryStrengthPower 中文文案
layden = {
    'LAYDEN_TEMP_STRENGTH_POWER.description': '在本回合结束前获得[gold]力量[/gold]。',
    'LAYDEN_TEMP_STRENGTH_POWER.smartDescription': '在本回合结束前获得[blue]{Amount}[/blue]点[gold]力量[/gold]。',
}
for k, v in layden.items():
    if k not in out:
        out[k] = v
        added += 1

with open(POWERS_JSON, 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
    f.write('\n')

print(f'powers.json: {len(data)} keys -> {len(out)} keys (+{added})')
