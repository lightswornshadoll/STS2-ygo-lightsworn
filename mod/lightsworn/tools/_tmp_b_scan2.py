import os, re, io

def scan(root, patterns, exts=('.cs',), limit=60):
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
MOD = r"D:\1-workdata\lightsworn_mod\mod\lightsworn"

print("=== 1. ArtifactPower class ===")
h = scan(SRC, [r'class ArtifactPower'])
for p, rows in h.items():
    for fp, i, line in rows[:10]:
        print(f"   {fp}:{i}: {line}")

print("=== 2. vanilla: cards that Add THEMSELVES to another pile on play (self-recall pattern) ===")
h = scan(SRC, [r'CardPileCmd\.Add\(this', r'Add\(base\.this'])
for p, rows in h.items():
    print(f"-- pattern {p}: {len(rows)} hits")
    for fp, i, line in rows[:20]:
        print(f"   {fp}:{i}: {line}")

print("=== 3. play flow: where played card goes after OnPlay ===")
h = scan(SRC, [r'AfterCardPlayed\(', r'MoveCardToDiscard|DiscardPlayedCard|ReturnCardToHand|SendToDiscard'])
for p, rows in h.items():
    print(f"-- pattern {p}: {len(rows)} hits")
    for fp, i, line in rows[:25]:
        print(f"   {fp}:{i}: {line}")

print("=== 4. mod Cards4 banish card (context around line 237/265) ===")
fp = os.path.join(MOD, r"Scripts\Cards4.cs")
with io.open(fp, 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()
for i in range(225, 285):
    if i < len(lines):
        print(f"{i+1}: {lines[i]}", end='')
