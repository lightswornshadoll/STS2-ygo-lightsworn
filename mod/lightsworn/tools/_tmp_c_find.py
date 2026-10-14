import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

base = r"D:\1-workdata\lightsworn_mod\research\sts2src"
hits = []
for root, dirs, files in os.walk(base):
    for f in files:
        if f == "MonsterModel.cs":
            hits.append(os.path.join(root, f))
print("HITS:", hits)
for h in hits[:1]:
    lines = open(h, encoding="utf-8", errors="replace").read().splitlines()
    print("TOTAL LINES:", len(lines))
    for i in range(230, min(275, len(lines))):
        print(f"{i+1}\t{lines[i]}")
