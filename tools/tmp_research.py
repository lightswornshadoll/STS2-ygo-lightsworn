"""临时研究脚本：看原版事件loc的键位格式（取LOST_WISP和ROUND_TEA_PARTY样例）"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

d = json.load(io.open(r'D:\1-workdata\lightsworn_mod\research\pck_tmp\localization\zhs\events.json', encoding='utf-8'))
print('type:', type(d), 'top keys:', list(d.keys())[:5] if isinstance(d, dict) else '')
# godot loc json 可能是 {"keys": [...]} 或平铺
def entries(d):
    if isinstance(d, dict):
        if 'keys' in d:
            return {k['id']: k.get('text', '') for k in d['keys'] if isinstance(k, dict)}
        return d
    return {}

flat = entries(d)
print('entry count:', len(flat))
for k in sorted(flat):
    if k.startswith('LOST_WISP') or k.startswith('ROUND_TEA_PARTY'):
        v = flat[k]
        print(f'{k} = {v[:90]}')
