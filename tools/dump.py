import io, re

src = r'D:\1-workdata\lightsworn_mod\research\sts2src'
p = src + r'\MegaCrit.Sts2.Core.Models\CardModel.cs'
t = io.open(p, encoding='utf-8-sig', errors='ignore').read()
for m in re.finditer(r'(public[^\n]*\bTags\b[^\n]*\n(?:.*\n){0,18})', t):
    print(m.group(0)[:1200])
    print('======')
