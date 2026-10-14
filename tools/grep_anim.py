import re, sys, pathlib
root = pathlib.Path(r"D:\1-workdata\lightsworn_mod\research\sts2src")
pat = re.compile(sys.argv[1])
for p in root.rglob("*.cs"):
    try:
        for i, line in enumerate(p.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            if pat.search(line):
                print(f"{p.relative_to(root)}:{i}: {line.strip()}")
    except Exception:
        pass
