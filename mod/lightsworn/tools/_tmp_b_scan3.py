import os, re, io

MOD = r"D:\1-workdata\lightsworn_mod\mod\lightsworn"
for dirpath, dirnames, filenames in os.walk(MOD):
    dirnames[:] = [d for d in dirnames if d not in ('.godot', 'bin', 'obj', '.git')]
    for fn in filenames:
        if not fn.endswith('.cs'):
            continue
        fp = os.path.join(dirpath, fn)
        with io.open(fp, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        if 'class LsCard' in content:
            idx = content.find('class LsCard')
            print("FOUND LsCard in:", fp)
            start = content.rfind('\n', 0, idx)
            print(content[max(0, idx-200): idx+3000])
            break
