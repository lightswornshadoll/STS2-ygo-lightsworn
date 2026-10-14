import sys, glob
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
for f in glob.glob(r'D:\1-workdata\lightsworn_mod\research\BaseLib-StS2-master\**\*.cs', recursive=True):
    t = open(f, encoding='utf-8', errors='replace').read()
    if 'AddChildSafely' in t and ('public static' in t):
        for i, l in enumerate(t.splitlines()):
            if 'AddChildSafely' in l and 'public static' in l:
                print(f)
                lines = t.splitlines()
                print('\n'.join(lines[max(0, i - 2):i + 16]))
                sys.exit()
print('not found')
