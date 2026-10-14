import io, os, re, sys

# 用法: py tools\grepbl.py <正则> [文件名过滤]
roots = [
    r'D:\1-workdata\lightsworn_mod\research\BaseLib-StS2-master',
    r'D:\1-workdata\lightsworn_mod\research\sts2src',
]
pat = re.compile(sys.argv[1], re.I)
file_filter = sys.argv[2].lower() if len(sys.argv) > 2 else ''
hits = 0
for src in roots:
    for dp, _, fs in os.walk(src):
        for fn in fs:
            if not fn.endswith('.cs'):
                continue
            if file_filter and file_filter not in fn.lower():
                continue
            p = os.path.join(dp, fn)
            t = io.open(p, encoding='utf-8-sig', errors='ignore').read()
            for i, line in enumerate(t.splitlines(), 1):
                if pat.search(line):
                    print(os.path.relpath(p, src), i, line.strip()[:170])
                    hits += 1
print(f'--- {hits} hits ---')
