import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
path = r'C:\Users\light\AppData\Roaming\SlayTheSpire2\logs\godot.log'
noise = re.compile(r'Progress parse|Asset not cached|PSO caching|Unknown (character|card|CardModel|RelicModel)|shadowversebydmod|MinionLib|SteamCallResult|Steam.*branch', re.I)
for i, line in enumerate(open(path, encoding='utf-8', errors='replace'), 1):
    s = line.rstrip()
    if not s:
        continue
    if noise.search(s):
        continue
    if re.search(r'ERROR|WARN|Exception|Lightsworn|Shaddoll|Tear|Fusion|融合|影依|珠泪', s, re.I):
        print(f'{i}: {s}')
