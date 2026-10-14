import io, os

f = os.path.join(os.environ['APPDATA'], r'SlayTheSpire2\logs\godot.log')
lines = io.open(f, encoding='utf-8', errors='ignore').read().splitlines()
ver = [l for l in lines if 'Lightsworn, Version' in l]
init = [l for l in lines if 'Lightsworn mod initialized' in l or 'Finished mod initialization' in l and 'lightsworn' in l.lower()]
print('VERSION:', ver)
print('INIT:', init)
errs = 0
for n, line in enumerate(lines, 1):
    if ('ERROR' in line or 'Exception' in line) and 'MinionLib' not in line and 'shadowverse' not in line and 'RID alloc' not in line and 'shaders' not in line and 'resources still in use' not in line:
        print(n, line[:190])
        errs += 1
        if errs > 15:
            break
if errs == 0:
    print('NO RELEVANT ERRORS')
