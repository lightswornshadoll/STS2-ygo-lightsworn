# 对比 RitsuLib 0.107.1 与 0.111.0 两个编译变体的反编译源码
import os, hashlib, collections

OLD = r'D:\1-workdata\lightsworn_mod\research\RitsuLibSrc\0107_runtime'
NEW = r'D:\1-workdata\lightsworn_mod\research\RitsuLibSrc\0111_runtime'


def scan(root):
    files = {}
    for dirpath, dirnames, filenames in os.walk(root):
        for fn in filenames:
            if not fn.endswith('.cs'):
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, root).replace('\\', '/')
            txt = open(full, encoding='utf-8', errors='replace').read()
            body = '\n'.join(l.strip() for l in txt.splitlines() if l.strip())
            files[rel] = (hashlib.md5(body.encode('utf-8', 'replace')).hexdigest(), body)
    return files


old = scan(OLD)
new = scan(NEW)
oldset, newset = set(old), set(new)
added = sorted(newset - oldset)
removed = sorted(oldset - newset)
changed = sorted(k for k in oldset & newset if old[k][0] != new[k][0])
print(f'0107 files: {len(old)}  0111 files: {len(new)}')
print(f'ADDED: {len(added)}  REMOVED: {len(removed)}  CHANGED: {len(changed)}')
print('==== ADDED ====')
for a in added:
    print('  ', a)
print('==== REMOVED ====')
for r in removed:
    print('  ', r)
print('==== CHANGED ====')
for c in changed:
    print('  ', c)

# 对改动文件输出 difflib 结果到文件
import difflib
out = open(r'D:\1-workdata\lightsworn_mod\tools\_ritsu_variant_diff.txt', 'w', encoding='utf-8')
for c in changed:
    out.write('=' * 100 + '\n')
    out.write(f'FILE: {c}\n')
    diff = difflib.unified_diff(old[c][1].splitlines(), new[c][1].splitlines(), lineterm='')
    n = 0
    for line in diff:
        out.write(line + '\n')
        n += 1
        if n > 400:
            out.write('...(truncated)\n')
            break
out.close()
print('diff written to tools\\_ritsu_variant_diff.txt')
