# -*- coding: utf-8 -*-
"""v0.5.4 文案收尾：把 v1.46 的"动作化"弃光/除光描述改回**正文内联机制词**形式。

目标（用户点名）：卡面不出现独立的"弃光。/除光。/暮光。"词条行（已由 Ls.cs 的
placement=None 解决），机制名只以 `[gold]弃光[/gold]{Mill:diff()}` 形式出现在正文里，
观感对齐官方"重放"范式（`[gold]重放[/gold]{SwordSagePower:diff()}`）。

本脚本只动 cards.json 的 description，键集不变；每条替换都做**精确计数断言**。
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "mod", "lightsworn", "lightsworn", "localization", "zhs", "cards.json")

with open(PATH, encoding="utf-8") as f:
    raw = f.read()
cards = json.loads(raw)

# (旧片段, 新片段, 期望出现次数)
RULES = [
    # —— 弃光：顶部随机弃置 → 内联机制词（正文唯一一次出现，数值挂词后，同"重放N"）
    ("从[gold]抽牌堆[/gold]顶部弃置{Mill:diff()}张牌",
     "[gold]弃光[/gold]{Mill:diff()}", 26),
    # 固定数值（珠泪三姐妹 3 / 水仙女人鱼 5 / 少女密涅瓦的"被弃置时"1）
    ("从[gold]抽牌堆[/gold]顶部弃置3张牌", "[gold]弃光[/gold]3", 3),
    ("从[gold]抽牌堆[/gold]顶部弃置5张牌", "[gold]弃光[/gold]5", 1),
    ("从[gold]抽牌堆[/gold]顶部弃置1张牌", "[gold]弃光[/gold]1", 1),
    # 动态数量：X=手牌中不同名神影依数量+1（原 v0.5.3 即"弃光X（X=…）"）
    ("从[gold]抽牌堆[/gold]顶部弃置X张牌（X=", "[gold]弃光[/gold]X（X=", 1),
    # 雅典娜：与"消耗"数量相同的那次（原 v0.5.3="再弃光相同数量"）
    ("再从[gold]抽牌堆[/gold]顶部弃置相同数量的牌", "再[gold]弃光[/gold]相同数量", 1),
    # —— 除光：从抽牌堆选牌消耗 → 内联机制词
    ("从[gold]抽牌堆[/gold]中选择{Banish:diff()}张牌[gold]消耗[/gold]",
     "[gold]除光[/gold]{Banish:diff()}", 1),
]

# 全局替换（对整份 JSON 文本做，逐条断言计数）
text = raw
for old, new, expect in RULES:
    n = text.count(old)
    assert n == expect, f"期望 {expect} 次，实际 {n} 次：{old}"
    text = text.replace(old, new)

# 断言：不再残留旧的"顶部弃置"动作化写法；JSON 仍可解析且键集不变
assert "顶部弃置" not in text, "仍有残留的'顶部弃置'写法"
new_cards = json.loads(text)
assert set(new_cards.keys()) == set(cards.keys()), "键集发生变化"

# 断言：不再有裸写（未上色）的机制词 弃光/除光——出现处必须紧跟 [gold]
import re
for k, v in new_cards.items():
    if not k.endswith(".description"):
        continue
    for m in re.finditer("(?<!\[gold])弃光|(?<!\[gold])除光", v):
        raise AssertionError(f"{k}: 未上色的机制词 {m.group(0)!r} @ {m.start()}")

with open(PATH, "w", encoding="utf-8", newline="\n") as f:
    f.write(text)

print("OK: 替换完成")
for old, new, expect in RULES:
    print(f"  {expect:2d} × {old[:34]}… → {new[:34]}…")
# 概览：剩余含机制词的行
for k, v in new_cards.items():
    if k.endswith(".description") and ("弃光" in v or "除光" in v or "暮光" in v):
        print(f"  {k}: {v[:70]}")
