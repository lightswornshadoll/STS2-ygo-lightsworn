import re
t = open(r'research/pck_dump/scenes/rest_site/characters/silent_rest_site.tscn', 'rb').read().decode('utf-8', errors='replace')
i = t.find('[gd_')
t = t[i:]
# 过滤掉 SpineMesh2D 节点段落，打印其余部分
out = []
skip = False
for block in t.split('\n\n'):
    if 'SpineMesh2D' in block.split('\n')[0]:
        skip = True
        continue
    skip = False
    out.append(block)
print('\n\n'.join(out))
