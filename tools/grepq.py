"""递归正则搜索：grepq.py <pattern> [根目录...] [--py]  默认搜 sts2src + BaseLib 源码，--py 只搜本项目 Scripts"""
import re, sys, os, io

def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    flags = [a for a in sys.argv[1:] if a.startswith('--')]
    if not args:
        print("usage: grepq.py <pattern> [roots...] [--py]"); return
    pat = re.compile(args[0], re.I)
    here = os.path.dirname(__file__)
    if '--py' in flags:
        roots = args[1:] or [os.path.join(here, '..', 'mod', 'lightsworn', 'Scripts')]
    else:
        roots = [r for r in (args[1:] or [
            os.path.join(here, '..', 'research', 'sts2src'),
            os.path.join(here, '..', 'research', 'BaseLib-StS2-master')]) if os.path.exists(r)]
    hits = 0
    for root in roots:
        if os.path.isfile(root):
            walk = [(os.path.dirname(root), [], [os.path.basename(root)])]
        else:
            walk = list(os.walk(root))
        for dirpath, dirs, files in walk:
            dirs[:] = [d for d in dirs if d not in ('.git', 'bin', 'obj', '.godot')]
            for f in files:
                if not f.endswith('.cs'):
                    continue
                p = os.path.join(dirpath, f)
                try:
                    text = io.open(p, encoding='utf-8', errors='replace').read()
                except OSError:
                    continue
                for i, line in enumerate(text.splitlines(), 1):
                    if pat.search(line):
                        rel = os.path.relpath(p, root)
                        print(f"{os.path.basename(root)}\\{rel}:{i}: {line.strip()}")
                        hits += 1
                        if hits > 400:
                            print("...too many hits, stop"); return

main()
