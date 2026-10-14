# -*- coding: utf-8 -*-
"""findids：全量输出 中文名→ID 映射（cards/powers）+ Scripts 各类声明行号。
v0.3.3 重写为 dumptoc 式全量 dump（改了内容重跑即可，永远是最新的）。"""
import json, re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = r"D:\1-workdata\lightsworn_mod"
cards_json = ROOT + r"\mod\lightsworn\lightsworn\localization\zhs\cards.json"
powers_json = ROOT + r"\mod\lightsworn\lightsworn\localization\zhs\powers.json"

with open(cards_json, encoding="utf-8") as f:
    cards = json.load(f)
with open(powers_json, encoding="utf-8") as f:
    powers = json.load(f)

print("==== CARDS (title -> ID) ====")
for k in sorted(cards):
    if k.endswith(".title"):
        print(f"{cards[k]}\t{k[:-len('.title')]}")

print("\n==== POWERS (title -> ID) ====")
for k in sorted(powers):
    if k.endswith(".title"):
        print(f"{powers[k]}\t{k[:-len('.title')]}")

print("\n==== CLASSES in Scripts（文件:行号 + 类名；ID=LIGHTSWORN-类名大写蛇形）====")
for i in range(1, 5):
    p = ROOT + rf"\mod\lightsworn\Scripts\Cards{i}.cs"
    for n, line in enumerate(open(p, encoding="utf-8"), 1):
        m = re.match(r"public class (\w+)", line.strip())
        if m:
            print(f"Cards{i}.cs:{n}\t{m.group(1)}")
for extra in ("Powers.cs", "LightswornContent.cs", "Ls.cs", "LsUtil.cs"):
    p = ROOT + rf"\mod\lightsworn\Scripts\{extra}"
    for n, line in enumerate(open(p, encoding="utf-8"), 1):
        m = re.match(r"public class (\w+)", line.strip())
        if m:
            print(f"{extra}:{n}\t{m.group(1)}")
