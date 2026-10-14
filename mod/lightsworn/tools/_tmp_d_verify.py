import os, re

# 1) Reference scan for the 5 deleted Fiendsmith classes across ALL Scripts\*.cs
names = ['Engraver', 'Lacrima', 'Hymn', 'RequiemCoffin', 'Lament']
script_root = r'D:\1-workdata\lightsworn_mod\mod\lightsworn\Scripts'
print('=== reference scan (Scripts/*.cs) ===')
hits = 0
for dirpath, dirs, files in os.walk(script_root):
    for fn in sorted(files):
        if not fn.endswith('.cs'):
            continue
        p = os.path.join(dirpath, fn)
        with open(p, encoding='utf-8') as f:
            for i, line in enumerate(f, 1):
                for n in names:
                    if re.search(r'\b' + n + r'\b', line):
                        print(f'{fn}:{i}: {line.strip()}')
                        hits += 1
print('total hits:', hits)

# 2) Brace balance of Cards4.cs
p4 = os.path.join(script_root, 'Cards4.cs')
with open(p4, encoding='utf-8') as f:
    src = f.read()
print('=== Cards4.cs checks ===')
print('open braces:', src.count('{'), 'close braces:', src.count('}'))
print('ends with:', repr(src[-30:]))
for n in names:
    if re.search(r'\b' + n + r'\b', src):
        print('STILL CONTAINS:', n)
print('class list:')
for m in re.finditer(r'public class (\w+)', src):
    print(' ', m.group(1))
