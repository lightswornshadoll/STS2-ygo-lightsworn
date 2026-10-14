# 对比 sts2 0.107.1 与 0.111.0 反编译源码树，找破坏性变更
import os, re, sys, hashlib

OLD = r'D:\1-workdata\lightsworn_mod\research\sts2src'
NEW = r'D:\1-workdata\lightsworn_mod\research\sts2src_0111'


def norm(path, root):
    rel = os.path.relpath(path, root).replace('\\', '/')
    return rel


def scan(root):
    files = {}
    for dirpath, dirnames, filenames in os.walk(root):
        for fn in filenames:
            if not fn.endswith('.cs'):
                continue
            full = os.path.join(dirpath, fn)
            rel = norm(full, root)
            try:
                txt = open(full, encoding='utf-8', errors='replace').read()
            except Exception as e:
                txt = f'<ERROR {e}>'
            # 归一化：去空行、去行首行尾空白，便于比较
            body = '\n'.join(l.strip() for l in txt.splitlines() if l.strip())
            files[rel] = hashlib.md5(body.encode('utf-8', 'replace')).hexdigest()
    return files


old = scan(OLD)
new = scan(NEW)
oldset, newset = set(old), set(new)

print(f'OLD files: {len(old)}  NEW files: {len(new)}')
added = sorted(newset - oldset)
removed = sorted(oldset - newset)
changed = sorted(k for k in oldset & newset if old[k] != new[k])

print(f'ADDED: {len(added)}  REMOVED: {len(removed)}  CHANGED: {len(changed)}')

with open(r'D:\1-workdata\lightsworn_mod\tools\_apidiff_files.txt', 'w', encoding='utf-8') as f:
    f.write('==== ADDED ====\n')
    f.write('\n'.join(added))
    f.write('\n==== REMOVED ====\n')
    f.write('\n'.join(removed))
    f.write('\n==== CHANGED ====\n')
    f.write('\n'.join(changed))

# 按命名空间聚合 changed
import collections
byns = collections.Counter()
for c in changed:
    parts = c.split('/')
    ns = '/'.join(parts[:-1]) if len(parts) > 1 else '(root)'
    byns[ns] += 1
print('\n=== CHANGED by directory (top 80) ===')
for k, v in byns.most_common(80):
    print(f'{v:5d}  {k}')
