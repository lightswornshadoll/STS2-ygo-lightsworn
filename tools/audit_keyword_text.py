# -*- coding: utf-8 -*-
"""审计：卡类关键词声明 vs 正文机制词出现情况（v0.5.4 内联文案改造用）
输出：
  1) 每个 card 类声明的 LsKeywords.Mill/Banish/Twilight
  2) cards.json 每条 description 含 弃光/除光/暮光 的位置片段
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "mod", "lightsworn", "Scripts")
CARDS_JSON = os.path.join(ROOT, "mod", "lightsworn", "lightsworn", "localization", "zhs", "cards.json")


def pascal_to_snake_upper(name: str) -> str:
    return re.sub(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])", "_", name).upper()


decls = {}  # class -> set of keyword stems
for fn in sorted(os.listdir(SCRIPTS)):
    if not fn.endswith(".cs"):
        continue
    text = open(os.path.join(SCRIPTS, fn), encoding="utf-8").read()
    # 找每个 class 块（粗略：按 public class X : ... 切分）
    matches = list(re.finditer(r"public (?:sealed |abstract )?class (\w+)\s*:\s*(\w+)", text))
    for i, m in enumerate(matches):
        cls = m.group(1)
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        block = text[start:end]
        kws = set()
        for km in re.finditer(r"CanonicalKeywords\s*=>\s*\[(.*?)\]", block, re.S):
            body = km.group(1)
            if "LsKeywords.Mill" in body:
                kws.add("Mill")
            if "LsKeywords.Banish" in body:
                kws.add("Banish")
            if "LsKeywords.Twilight" in body:
                kws.add("Twilight")
        if cls not in decls:
            decls[cls] = set()
        decls[cls] |= kws

cards = json.load(open(CARDS_JSON, encoding="utf-8"))
desc_by_id = {k.split(".")[0]: v for k, v in cards.items() if k.endswith(".description")}

print("== 声明了 Mill/Banish/Twilight 的卡类 ==")
for cls in sorted(decls):
    if decls[cls]:
        cid = "LIGHTSWORN_CARD_" + pascal_to_snake_upper(cls)
        text = desc_by_id.get(cid, "")
        marks = []
        for w in ("弃光", "除光", "暮光"):
            if w in text:
                marks.append(w)
        print(f"{cls:28s} {sorted(decls[cls])!s:38s} 正文含: {marks}")

print()
print("== 正文含机制词但无对应声明的卡 ==")
for cid, text in sorted(desc_by_id.items()):
    cls = re.sub(r"_(.)", lambda m: m.group(1), cid.replace("LIGHTSWORN_CARD_", "").title().replace("_", "") )
    # 手工反推：用 decls 的 key 匹配 snake
    cand = [c for c in decls if pascal_to_snake_upper(c) == cid.replace("LIGHTSWORN_CARD_", "")]
    kws = decls[cand[0]] if cand else set()
    need = set()
    if "弃光" in text:
        need.add("Mill")
    if "除光" in text:
        need.add("Banish")
    if "暮光" in text:
        need.add("Twilight")
    missing = need - kws
    if missing:
        print(f"{cid:48s} 需 {sorted(missing)} 实际声明 {sorted(kws)}")

print()
print("== 正文机制词上下文（弃光/除光/暮光 片段）==")
for cid, text in sorted(desc_by_id.items()):
    for w in ("弃光", "除光", "暮光"):
        for m in re.finditer(w, text):
            s = max(0, m.start() - 8)
            e = min(len(text), m.end() + 8)
            print(f"{cid:48s} …{text[s:e]}…")
