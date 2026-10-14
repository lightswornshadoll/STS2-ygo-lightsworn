# -*- coding: utf-8 -*-
import os, re, io

root = r"D:\1-workdata\lightsworn_mod\research\sts2src"
base = r"D:\1-workdata\lightsworn_mod\research\BaseLib-StS2-master"

pat_var_amount = re.compile(r'new DynamicVar\(\s*"Amount"')
pat_reserved = re.compile(r'"\s*Amount\s*"')
pat_diff = re.compile(r':diff\(\)')

# 1. does any vanilla card use key "Amount"?
print("=== 'Amount' as DynamicVar key / string literal in CardModel-ish contexts ===")
count = 0
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
        for m in pat_var_amount.finditer(text):
            line_start = text.rfind("\n", 0, m.start()) + 1
            line = text[line_start:text.find("\n", m.end())].strip()
            print("  %s :: %s" % (os.path.relpath(p, root), line[:150]))
            count += 1
print("  total new DynamicVar(\"Amount\"):", count)

# 2. check BaseLib LsCard / CardModel patch: DynamicVars setup, special keys
print()
print("=== BaseLib files mentioning DynamicVars keys ===")
for dirpath, dirnames, filenames in os.walk(base):
    for fn in filenames:
        if not fn.endswith(".cs"):
            continue
        p = os.path.join(dirpath, fn)
        try:
            with io.open(p, "r", encoding="utf-8", errors="replace") as f:
                text = f.read()
        except Exception:
            continue
        if "DynamicVar" in text and ("Diff" in text or "diff" in text or "CardDescription" in text or "ParseDescription" in text):
            print("  FILE:", os.path.relpath(p, base))

# 3. find how description placeholder diff() is resolved (sts2src)
print()
print("=== diff() placeholder resolution (sts2src) ===")
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
        if ":diff()" in text and ("ParseCardDescription" in text or "FormatDescription" in text or "DynamicVar" in text):
            for i, line in enumerate(text.splitlines()):
                if ":diff()" in line:
                    print("  %s:%d :: %s" % (os.path.relpath(p, root), i + 1, line.strip()[:180]))
                    break
