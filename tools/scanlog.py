import io, os, glob

logdir = os.path.join(os.environ['APPDATA'], r'SlayTheSpire2\logs')
files = sorted(glob.glob(os.path.join(logdir, '*.log')))
for f in files:
    lines = io.open(f, encoding='utf-8', errors='ignore').read().splitlines()
    print('=' * 30, os.path.basename(f), len(lines), 'lines', '=' * 30)
    hits = 0
    for n, line in enumerate(lines, 1):
        low = line.lower()
        if ('error' in low or 'exception' in low or 'harmony' in low or 'relic' in low or 'finalizestartingrelics' in low or 'choosearelic' in low) \
           and 'minionlib' not in low and 'shadowverse' not in low \
           and 'rid alloc' not in low and 'shaders' not in low and 'resources still in use' not in low:
            print(n, line[:220])
            hits += 1
            if hits > 60:
                print('...truncated')
                break
    if hits == 0:
        print('(no matching lines)')
    print()
