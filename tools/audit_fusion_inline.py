# -*- coding: utf-8 -*-
"""检查：声明 TearFusion / ShaddollFusion 的卡，正文是否内联出现「珠泪融合」/「影融」
（若全部内联 → 词条行改为 None 不会让卡面失去机制标记）"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "mod", "lightsworn", "Scripts")
CARDS_JSON = os.path.join(ROOT, "mod", "lightsworn", "lightsworn", "localization", "zhs", "cards.json")


def snake(name):
    return re.sub(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])", "_", name).upper()


cards = json.load(open(CARDS_JSON, encoding="utf-8"))
desc = {k.split(".")[0]: v for k, v in cards.items() if k.endswith(".description")}

rows = []
for fn in sorted(os.listdir(SCRIPTS)):
    if not fn.endswith(".cs"):
        continue
    text = open(os.path.join(SCRIPTS, fn), encoding="utf-8").read()
    for m in re.finditer(r"public (?:sealed |abstract )?class (\w+)\s*:\s*(\w+)", text):
        cls = m.group(1)
        block = text[m.start(): m.start() + 6000]
        kw = set()
        for km in re.finditer(r"CanonicalKeywords\s*=>\s*\[(.*?)\]", block, re.S):
            body = km.group(1)
            if "TearFusion" in body:
                kw.add("TearFusion")
            if "ShaddollFusion" in body:
                kw.add("ShaddollFusion")
        if not kw:
            continue
        cid = "LIGHTSWORN_CARD_" + snake(cls)
        t = desc.get(cid, "")
        inline = ("珠泪融合" in t) or ("影融" in t)
        rows.append((cls, sorted(kw), cid in desc, inline, t[:56]))

for r in rows:
    flag = "OK " if r[3] else "!! 无内联"
    print(f"{flag} {r[0]:26s} {r[1]!s:32s} 有desc={r[2]}  {r[4]}")
print(f"\n合计 {len(rows)} 张；缺内联 {sum(1 for r in rows if not r[3])} 张")
