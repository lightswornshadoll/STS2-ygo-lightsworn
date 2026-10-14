import os, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
mod = r"D:\1-workdata\lightsworn_mod\mod\lightsworn\Scripts"
for f in sorted(os.listdir(mod)):
    if not f.endswith(".cs"): continue
    p = os.path.join(mod, f)
    lines = open(p, encoding="utf-8", errors="replace").read().splitlines()
    cls = None
    for i, l in enumerate(lines):
        m = re.search(r"public class (\w+)", l)
        if m: cls = m.group(1)
        if re.search(r"new DamageVar\(", l):
            print(f"{f}:{i+1}: {cls}: {l.strip()}")
