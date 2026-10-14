# -*- coding: utf-8 -*-
import os, re, io

root = r"D:\1-workdata\lightsworn_mod\research\sts2src"

targets = {
    "Rng.cs": None,
    "VulnerablePower.cs": None,
    "StrengthPower.cs": None,
    "DexterityPower.cs": None,
}
for dirpath, dirnames, filenames in os.walk(root):
    for fn in filenames:
        if fn in targets and targets[fn] is None:
            targets[fn] = os.path.join(dirpath, fn)

for fn, p in targets.items():
    print("=== %s -> %s ===" % (fn, p))
    if p:
        with io.open(p, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
        # print signatures only: lines with public/namespace/class
        for line in text.splitlines():
            s = line.strip()
            if s.startswith("namespace") or s.startswith("public") or s.startswith("    public") and "(" in s or "class " in s:
                print("  " + s[:200])
    print()
