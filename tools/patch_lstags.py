import io

p = r'D:\1-workdata\lightsworn_mod\mod\lightsworn\Scripts\LightswornContent.cs'
t = io.open(p, encoding='utf-8').read()
old = '''                if (Ls.LightswornNamed.Contains(GetType().Name))
                    tags.Add(Ls.Lightsworn);'''
new = '''                if (Ls.LightswornNamed.Contains(GetType().Name))
                    tags.Add(Ls.Lightsworn);
                if (Ls.ShaddollNamed.Contains(GetType().Name))
                    tags.Add(Ls.Shaddoll);'''
n = t.count(old)
assert n == 1, f'expect 1 occurrence, got {n}'
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new))
print('patched OK')
