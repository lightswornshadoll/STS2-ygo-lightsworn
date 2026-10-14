# -*- coding: utf-8 -*-
"""v0.4.20：融合Token消耗语义改「回到卡组时消耗，直接回手保留」——只改两个融合词条的消耗措辞。"""
import json, io, os, sys

ROOT = os.path.join(os.path.dirname(__file__), "..", "mod", "lightsworn", "lightsworn", "localization", "zhs")

KEYWORDS = {
    "LIGHTSWORN-TEARFUSION.description":
        ("同一回合每张融合卡只能生成1次；融合卡离开弃牌堆时消耗。",
         "同一回合每张融合卡只能生成1次；融合卡回到卡组（抽牌堆）时消耗，被效果直接加入手牌则保留。"),
    "LIGHTSWORN-SHADDOLLFUSION.description":
        ("（0费，离开弃牌堆时消耗）",
         "（0费，回到卡组时消耗）"),
    "LIGHTSWORN-SHADDOLLFUSION.description#2":
        ("神影依每回合各只能生成1次。",
         "神影依每回合各只能生成1次，回到卡组（抽牌堆）时消耗，被效果直接加入手牌则保留。"),
}

path = os.path.join(ROOT, "card_keywords.json")
data = json.load(io.open(path, encoding="utf-8"))
for key, (old, new) in KEYWORDS.items():
    base = key.split("#")[0]
    cur = data.get(base)
    if cur is None:
        sys.exit(f"[FAIL] 缺键: {base}")
    if new in cur:
        print(f"[SKIP] {base}（{key}）已是新文案")
        continue
    if old not in cur:
        sys.exit(f"[FAIL] {base}（{key}）当前文案不含预期片段：\n  {cur}")
    data[base] = cur.replace(old, new)
    print(f"[OK] {base}（{key}）")
with io.open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
    f.write("\n")
print("card_keywords.json 已更新")
