# -*- coding: utf-8 -*-
import os, re, io

root = r"D:\1-workdata\lightsworn_mod\research\sts2src"
base = r"D:\1-workdata\lightsworn_mod\research\BaseLib-StS2-master"

# 1. print Resonance.cs and SharedFate.cs fully
for rel in [r"MegaCrit.Sts2.Core.Models.Cards\Resonance.cs",
            r"MegaCrit.Sts2.Core.Models.Cards\SharedFate.cs"]:
    p = os.path.join(root, rel)
    print("=== %s ===" % rel)
    with io.open(p, "r", encoding="utf-8", errors="replace") as f:
        print(f.read())
    print()

# 2. find random-enemy pick precedents: Rng.*Selection usage on HittableEnemies
pat = re.compile(r"(HittableEnemies[^\n]{0,160})")
pat2 = re.compile(r"(Rng\.(Combat\w*Selection)[^\n]{0,120})")
seen = set()
print("=== HittableEnemies / Rng usages ===")
for dirpath, dirnames, filenames in os.walk(root):
    for fn in filenames:
        if not fn.endswith(".cs"):
            continue
        p = os.path.join(dirpath, fn)
        try:
            with io.open(p, "r", encoding="utf-8", errors="replace") as f:
                text = f.read()
        except Exception:
            continue
        for m in pat2.finditer(text):
            line_start = text.rfind("\n", 0, m.start()) + 1
            line_end = text.find("\n", m.end())
            line = text[line_start:line_end if line_end != -1 else len(text)].strip()
            key = line[:100]
            if key in seen:
                continue
            seen.add(key)
            print("  %s :: %s" % (os.path.relpath(p, root), line[:200]))
