import os, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

sts2 = r"D:\1-workdata\lightsworn_mod\research\sts2src"
baselib = r"D:\1-workdata\lightsworn_mod\research\BaseLib-StS2-master"
mod = r"D:\1-workdata\lightsworn_mod\mod\lightsworn"

def show(path, pats, ctx=0, maxhits=8):
    hits = 0
    try:
        lines = open(path, encoding="utf-8", errors="replace").read().splitlines()
    except Exception as e:
        print("ERR", path, e); return
    for i, l in enumerate(lines):
        if any(re.search(p, l) for p in pats):
            for j in range(max(0, i-ctx), min(len(lines), i+ctx+1)):
                print(f"{path.split(os.sep)[-1]}:{j+1}: {lines[j]}")
            print("---")
            hits += 1
            if hits >= maxhits: return

def find(base, name):
    out = []
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d not in (".godot", "bin", "obj")]
        if name in files:
            out.append(os.path.join(root, name))
    return out

print("=== CardSelectorPrefs ctor (sts2src) ===")
for p in find(sts2, "CardSelectorPrefs.cs"): show(p, [r"public CardSelectorPrefs"], 3, 6)

print("=== MultiPileCardSelect.Select (baselib + sts2src) ===")
for p in find(baselib, "MultiPileCardSelect.cs") + find(sts2, "MultiPileCardSelect.cs"):
    show(p, [r"public static.*Select"], 4, 6)
    print("NS file head:")
    print("".join(open(p, encoding="utf-8", errors="replace").read().splitlines(True)[:12]))

print("=== CardPileCmd.Shuffle / Add / ShuffleIfNecessary ===")
p = find(sts2, "CardPileCmd.cs")[0]
show(p, [r"public static.*(Shuffle|Add)\b"], 1, 12)

print("=== Creature.Monster property ===")
p = find(sts2, "Creature.cs")[0]
show(p, [r"public.*Monster\b"], 2, 4)

print("=== EnergyCost.UpgradeBy ===")
for root, dirs, files in os.walk(sts2):
    for f in files:
        if f == "EnergyCost.cs":
            fp = os.path.join(root, f)
            show(fp, [r"public.*Upgrade"], 1, 6)

print("=== CardPlay.Target ===")
p = find(sts2, "CardPlay.cs")[0]
show(p, [r"public.*Target"], 1, 6)

print("=== WeakPower namespace ===")
for p in find(sts2, "WeakPower.cs"):
    print(p)
    print("".join(open(p, encoding="utf-8", errors="replace").read().splitlines(True)[:12]))

print("=== PowerCmd.Apply overloads (first lines of each) ===")
p = find(sts2, "PowerCmd.cs")[0]
show(p, [r"public static.*Apply"], 0, 12)

print("=== GainBlock signature ===")
p = find(sts2, "CreatureCmd.cs")[0]
show(p, [r"public static.*GainBlock"], 0, 4)

print("=== mod cards.json: lines containing 才能打出 ===")
cards_json = open(os.path.join(mod, "lightsworn", "localization", "zhs", "cards.json"), encoding="utf-8").read()
for i, l in enumerate(cards_json.splitlines()):
    if "才能打出" in l or "[gold]" in l:
        print(f"cards.json:{i+1}: {l.strip()}")
