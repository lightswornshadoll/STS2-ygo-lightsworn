# v0.4.11 暮光机制重做：更新 card_keywords.json 与 powers.json 的暮光文案
import json
import os

base = os.path.join(os.path.dirname(__file__), '..', 'mod', 'lightsworn', 'lightsworn', 'localization', 'zhs')

kw_desc = ('暮光：触发弃光时，若抽牌堆的牌不够弃光数量，消耗2层暮光，'
           '将弃牌堆洗回抽牌堆，回复1点能量，并补完剩余弃光。')
power_desc = ('触发弃光时，若抽牌堆的牌不够弃光数量，消耗2层暮光，'
              '将弃牌堆洗回抽牌堆，回复1点能量，并补完剩余弃光。')
power_smart = power_desc + '（剩余[blue]{Amount}[/blue]层）'


def patch(filename, updates):
    path = os.path.normpath(os.path.join(base, filename))
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    for k, v in updates.items():
        old = data.get(k)
        data[k] = v
        print(f'{filename}: {k}\n  - {old}\n  + {v}')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


patch('card_keywords.json', {'LIGHTSWORN-TWILIGHT.description': kw_desc})
patch('powers.json', {
    'LIGHTSWORN-TWILIGHT_POWER.description': power_desc,
    'LIGHTSWORN-TWILIGHT_POWER.smartDescription': power_smart,
})
print('done')
