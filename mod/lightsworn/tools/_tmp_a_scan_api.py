# -*- coding: utf-8 -*-
import os, re, io

roots = [
    r"D:\1-workdata\lightsworn_mod\research\sts2src",
    r"D:\1-workdata\lightsworn_mod\research\BaseLib-StS2-master",
]

patterns = {
    "neg_strength": re.compile(r"Apply<StrengthPower>\([^;]*-\d"),
    "neg_dex": re.compile(r"Apply<DexterityPower>\([^;]*-\d"),
    "any_strength_apply": re.compile(r"Apply<StrengthPower>\("),
    "any_dex_apply": re.compile(r"Apply<DexterityPower>\("),
    "vuln_apply": re.compile(r"Apply<VulnerablePower>\("),
    "var_classes": re.compile(r"class\s+(\w*Var)\s*:"),
    "dynamicvars_props": re.compile(r"public static\s+DynamicVar\w*\s+(\w+)"),
}

hits = {k: [] for k in patterns}

for root in roots:
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
            for key, pat in patterns.items():
                for m in pat.finditer(text):
                    line_start = text.rfind("\n", 0, m.start()) + 1
                    line_end = text.find("\n", m.end())
                    line = text[line_start:line_end if line_end != -1 else len(text)].strip()
                    rel = os.path.relpath(p, root)
                    hits[key].append((rel, line[:200]))

for key in patterns:
    lst = hits[key]
    print("=== %s (%d) ===" % (key, len(lst)))
    shown = set()
    count = 0
    for rel, line in lst:
        sig = (rel, line[:80])
        if sig in shown:
            continue
        shown.add(sig)
        print("  %s :: %s" % (rel, line))
        count += 1
        if count >= 25:
            print("  ... more")
            break
