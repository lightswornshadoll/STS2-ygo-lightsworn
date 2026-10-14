import os, re, io

def scan(root, patterns, exts=('.cs',), limit=40):
    hits = {p: [] for p in patterns}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in ('.godot', 'bin', 'obj', '.git')]
        for fn in filenames:
            if not fn.endswith(exts):
                continue
            fp = os.path.join(dirpath, fn)
            try:
                with io.open(fp, 'r', encoding='utf-8', errors='ignore') as f:
                    for i, line in enumerate(f, 1):
                        for p in patterns:
                            if re.search(p, line):
                                hits[p].append((fp, i, line.strip()[:200]))
            except OSError:
                pass
    return hits

SRC = r"D:\1-workdata\lightsworn_mod\research\sts2src"
BASELIB = r"D:\1-workdata\lightsworn_mod\research\BaseLib-StS2-master"
MOD = r"D:\1-workdata\lightsworn_mod\mod\lightsworn"

print("=== 1. EnergyCost UpgradeBy (sts2src) ===")
h = scan(SRC, [r'UpgradeBy', r'class EnergyCost', r'public .*EnergyCost\s'])
for p, rows in h.items():
    print(f"-- pattern {p}: {len(rows)} hits")
    for fp, i, line in rows[:25]:
        print(f"   {fp}:{i}: {line}")

print()
print("=== 2. LsKeywords (mod Ls.cs) ===")
h = scan(MOD, [r'LsKeywords', r'Banish', r'MillSelected'])
for p, rows in h.items():
    print(f"-- pattern {p}: {len(rows)} hits")
    for fp, i, line in rows[:30]:
        print(f"   {os.path.relpath(fp, MOD)}:{i}: {line}")

print()
print("=== 3. negative StrengthPower precedent (sts2src) ===")
h = scan(SRC, [r'Apply<StrengthPower>', r'AllowNegative'])
for p, rows in h.items():
    print(f"-- pattern {p}: {len(rows)} hits")
    for fp, i, line in rows[:20]:
        print(f"   {fp}:{i}: {line}")
