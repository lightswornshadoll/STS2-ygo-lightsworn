"""临时：在设计文档/图鉴中按关键词搜索（含上下文行）。"""
import io, os, re, sys

here = os.path.dirname(__file__)
root = os.path.join(here, '..')
targets = [
    os.path.join(root, 'design', '光道mod设计文档.md'),
    os.path.join(root, 'design', '卡牌图鉴.md'),
]
kws = sys.argv[1:]
for t in targets:
    if not os.path.exists(t):
        continue
    lines = io.open(t, encoding='utf-8', errors='replace').read().splitlines()
    for i, line in enumerate(lines, 1):
        for kw in kws:
            if kw in line:
                print(f"{os.path.basename(t)}:{i}: {line.strip()[:400]}")
                break
