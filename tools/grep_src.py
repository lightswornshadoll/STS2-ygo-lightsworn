import io, os, re, sys

src = r'D:\1-workdata\lightsworn_mod\research\sts2src'
pat = re.compile(sys.argv[1], re.I)
file_filter = sys.argv[2].lower() if len(sys.argv) > 2 else ''
hits = 0
for root, dirs, files in os.walk(src):
    for f in files:
        if not f.endswith('.cs'):
            continue
        if file_filter and file_filter not in f.lower():
            continue
        p = os.path.join(root, f)
        t = io.open(p, encoding='utf-8-sig', errors='ignore').read()
        for n, line in enumerate(t.splitlines(), 1):
            if pat.search(line):
                print(p.replace(src + os.sep, ''), n, line.strip()[:170])
                hits += 1
print(f'--- {hits} hits ---')
