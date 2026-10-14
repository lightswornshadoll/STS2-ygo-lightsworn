# 临时：在反编译源码里按正则找行并打印上下文（每次按需改写）
# 用法: py tools\peek.py <正则> [上下文行数] [根目录]
import re, sys, os

ROOT = r"D:\1-workdata\lightsworn_mod\research\sts2src"
pattern = sys.argv[1] if len(sys.argv) > 1 else r"_state = "
ctx = int(sys.argv[2]) if len(sys.argv) > 2 else 2
root = sys.argv[3] if len(sys.argv) > 3 else ROOT

for dirpath, dirs, files in os.walk(root):
    for f in files:
        if not f.endswith(".cs"):
            continue
        p = os.path.join(dirpath, f)
        try:
            lines = open(p, encoding="utf-8", errors="ignore").readlines()
        except OSError:
            continue
        for i, line in enumerate(lines):
            if re.search(pattern, line):
                print(f"--- {os.path.relpath(p, ROOT)}:{i+1}")
                for j in range(max(0, i - ctx), min(len(lines), i + ctx + 1)):
                    print(f"{j+1}: {lines[j].rstrip()}")
