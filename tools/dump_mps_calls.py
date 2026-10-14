import re, sys, glob, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
root = r'D:\1-workdata\lightsworn_mod\mod\lightsworn\Scripts'
pat = re.compile(r'MultiPileCardSelect\.Select')
for f in glob.glob(os.path.join(root, '*.cs')):
    lines = open(f, encoding='utf-8').read().splitlines()
    for i, l in enumerate(lines):
        if pat.search(l):
            # print call with continuation lines until ');' or balanced
            chunk = [l.strip()]
            j = i
            while ')' not in chunk[-1] or chunk[-1].count('(') > chunk[-1].count(')'):
                j += 1
                if j >= len(lines):
                    break
                chunk.append(lines[j].strip())
                if len(chunk) > 8:
                    break
            print(os.path.basename(f), i + 1)
            for c in chunk:
                print('    ', c)
