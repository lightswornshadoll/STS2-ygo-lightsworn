import os, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

sts2 = r"D:\1-workdata\lightsworn_mod\research\sts2src"
baselib = r"D:\1-workdata\lightsworn_mod\research\BaseLib-StS2-master"
mod = r"D:\1-workdata\lightsworn_mod\mod\lightsworn"

def scan(base, pats, exts=(".cs",), maxhits=40):
    n = 0
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d not in (".godot", "bin", "obj")]
        for f in files:
            if f.endswith(exts) and not f.startswith("_tmp_c_"):
                p = os.path.join(root, f)
                try:
                    lines = open(p, encoding="utf-8", errors="replace").read().splitlines()
                except Exception:
                    continue
                for i, l in enumerate(lines):
                    if any(re.search(p, l) for p in pats):
                        print(f"{p}:{i+1}: {l.strip()}")
                        n += 1
                        if n >= maxhits: return

print("=== UpgradeBy definition in sts2src ===")
scan(sts2, [r"(decimal|void|CardEnergyCost|EnergyCost)\s+UpgradeBy|public.*UpgradeBy"], maxhits=12)
print("=== mod usage of UpgradeBy(-1) / EnergyCost upgrades ===")
scan(mod, [r"UpgradeBy\(-1\)", r"EnergyCost\.Upgrade"], maxhits=12)
print("=== sts2src usage of UpgradeBy(-1) ===")
scan(sts2, [r"EnergyCost\.UpgradeBy\(-1\)|EnergyCost\.UpgradeBy"], maxhits=8)

print("=== namespace of MultiPileCardSelect.cs ===")
for root, dirs, files in os.walk(baselib):
    if "MultiPileCardSelect.cs" in files:
        p = os.path.join(root, "MultiPileCardSelect.cs")
        for l in open(p, encoding="utf-8", errors="replace").read().splitlines():
            if l.startswith("namespace"):
                print(p, "->", l)
print("=== namespace of CardSelectorPrefs (sts2src) ===")
for root, dirs, files in os.walk(sts2):
    if "CardSelectorPrefs.cs" in files:
        p = os.path.join(root, "CardSelectorPrefs.cs")
        for l in open(p, encoding="utf-8", errors="replace").read().splitlines():
            if l.startswith("namespace"):
                print(p, "->", l)

print("=== EnergyCost class: find where upgradeable cost lives ===")
scan(sts2, [r"class \w*EnergyCost"], maxhits=6)
