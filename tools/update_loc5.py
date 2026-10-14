"""第六轮反馈本地化同步：打击/防御改名、小龙/惩戒之龙/雪之化身/细剑描述。"""
import io, json, os

PATH = os.path.join(os.path.dirname(__file__), '..', 'mod', 'lightsworn', 'lightsworn',
                    'localization', 'zhs', 'cards.json')

CHANGES = {
    'LIGHTSWORN-LIGHT_BLADE.title': '打击',
    'LIGHTSWORN-LIGHT_WARD.title': '防御',
    'LIGHTSWORN-LIGHTSWORN_DRAGON.description':
        '弃牌堆中存在「光道」牌时才能打出。从抽牌堆中选择{Dump:diff()}张「光道」牌弃置，然后造成{Damage:diff()}点伤害。\n'
        '[gold]被弃置时[/gold]：若抽牌堆中有「裁决之龙」或「惩戒之龙」，选择1张加入手牌。',
    'LIGHTSWORN-PUNISH_DRAGON.description':
        '消耗堆中存在4种以上「光道」牌时才能打出。\n'
        '将弃牌堆与消耗堆中所有非「光道」牌返回卡组，每有一张，所有敌人随机获得1层负面状态（人工制品可抵挡）。'
        '造成{Damage:diff()}点伤害，并获得1层[gold]暮光[/gold]。',
    'LIGHTSWORN-SNOW_SPIRIT.description':
        '造成{Damage:diff()}点伤害。选择弃牌堆中的7张牌（不足则全部选择），将其消耗。',
    'LIGHTSWORN-SABRE.description':
        '弃光{Mill:diff()}。本回合获得{SabrePower:diff()}点[gold]力量[/gold]。\n'
        '[gold]从卡组被弃置时[/gold]自动加入手牌，且本回合费用变为0。',
}

def main():
    with io.open(PATH, encoding='utf-8-sig') as f:
        data = json.load(f)
    for k, v in CHANGES.items():
        if k not in data:
            raise SystemExit('missing key: ' + k)
        data[k] = v
    with io.open(PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print('updated', len(CHANGES), 'entries')

if __name__ == '__main__':
    main()
