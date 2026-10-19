# -*- coding: utf-8 -*-
# 暗黑界龙神王 Boss 本地化：四神将卡面/洗脑状态/能力/怪物/遭遇。
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOC = os.path.join(ROOT, 'mod', 'lightsworn', 'lightsworn', 'localization')


def load(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print('written', os.path.relpath(path, ROOT))


cards_add = {
    'LIGHTSWORN_CARD_DARK_WORLD_KELT.title': '暗黑界的鬼神',
    'LIGHTSWORN_CARD_DARK_WORLD_KELT.description':
        '对自己造成{Damage:diff()}点伤害。打出后移出战斗。\n[gold]从手牌被弃置时[/gold]：对自己造成12点伤害。',
    'LIGHTSWORN_CARD_DARK_WORLD_LATINUM.title': '暗黑界的斗神',
    'LIGHTSWORN_CARD_DARK_WORLD_LATINUM.description':
        '对自己造成{Damage:diff()}点伤害。打出后移出战斗。\n[gold]从手牌被弃置时[/gold]：龙神王获得3点力量。',
    'LIGHTSWORN_CARD_DARK_WORLD_SILLVA.title': '暗黑界的军神',
    'LIGHTSWORN_CARD_DARK_WORLD_SILLVA.description':
        '对自己造成{Damage:diff()}点伤害。打出后移出战斗。\n[gold]从手牌被弃置时[/gold]：随机将2张手牌洗入抽牌堆。',
    'LIGHTSWORN_CARD_DARK_WORLD_GOLDD.title': '暗黑界的武神',
    'LIGHTSWORN_CARD_DARK_WORLD_GOLDD.description':
        '对自己造成{Damage:diff()}点伤害。打出后移出战斗。\n[gold]从手牌被弃置时[/gold]：对自己施加1层虚弱和1层易伤。',
    'LIGHTSWORN_CARD_DARK_WORLD_BRAINWASHING.title': '暗黑界的洗脑',
    'LIGHTSWORN_CARD_DARK_WORLD_BRAINWASHING.description':
        '抽到时自动打出：获得1层[gold]洗脑[/gold]。\n[gold]洗脑[/gold]：打出的下一张攻击、技能或能力牌无效（可叠加、跨回合保留）。',
}

powers_add = {
    'LIGHTSWORN_POWER_DARK_WORLD_BRAINWASH_POWER.title': '洗脑',
    'DARK_WORLD_BRAINWASH_POWER.title': '洗脑',
    'LIGHTSWORN_POWER_DARK_WORLD_BRAINWASH_POWER.description':
        '打出的下一张攻击、技能或能力牌无效（费用照付，牌进入弃牌堆）。可叠加；每层吞掉一张牌。',
    'DARK_WORLD_BRAINWASH_POWER.description':
        '打出的下一张攻击、技能或能力牌无效（费用照付，牌进入弃牌堆）。可叠加；每层吞掉一张牌。',
    'LIGHTSWORN_POWER_DARK_WORLD_BRAINWASH_POWER.smartDescription':
        '打出的下一张攻击、技能或能力牌无效（费用照付，牌进入弃牌堆）。可叠加；每层吞掉一张牌。（剩余[blue]{Amount}[/blue]层）',
    'DARK_WORLD_BRAINWASH_POWER.smartDescription':
        '打出的下一张攻击、技能或能力牌无效（费用照付，牌进入弃牌堆）。可叠加；每层吞掉一张牌。（剩余[blue]{Amount}[/blue]层）',

    'LIGHTSWORN_POWER_DARK_WORLD_TEMPTATION_POWER.title': '暗黑界的诱惑',
    'DARK_WORLD_TEMPTATION_POWER.title': '暗黑界的诱惑',
    'LIGHTSWORN_POWER_DARK_WORLD_TEMPTATION_POWER.description':
        '每玩家回合第一次弃置卡牌时，根据第一张牌的类型触发：攻击→获得2点力量；技能→洗入1张「暗黑界的洗脑」；能力→随机弃置2张手牌；其他→复制1张同名牌洗入抽牌堆。然后，将1张随机暗黑界牌洗入其抽牌堆。回合结束的手牌清理不触发。',
    'DARK_WORLD_TEMPTATION_POWER.description':
        '每玩家回合第一次弃置卡牌时，根据第一张牌的类型触发：攻击→获得2点力量；技能→洗入1张「暗黑界的洗脑」；能力→随机弃置2张手牌；其他→复制1张同名牌洗入抽牌堆。然后，将1张随机暗黑界牌洗入其抽牌堆。回合结束的手牌清理不触发。',
    'LIGHTSWORN_POWER_DARK_WORLD_TEMPTATION_POWER.smartDescription':
        '每玩家回合第一次弃置卡牌时，根据第一张牌的类型触发：攻击→获得2点力量；技能→洗入1张「暗黑界的洗脑」；能力→随机弃置2张手牌；其他→复制1张同名牌洗入抽牌堆。然后，将1张随机暗黑界牌洗入其抽牌堆。回合结束的手牌清理不触发。',
    'DARK_WORLD_TEMPTATION_POWER.smartDescription':
        '每玩家回合第一次弃置卡牌时，根据第一张牌的类型触发：攻击→获得2点力量；技能→洗入1张「暗黑界的洗脑」；能力→随机弃置2张手牌；其他→复制1张同名牌洗入抽牌堆。然后，将1张随机暗黑界牌洗入其抽牌堆。回合结束的手牌清理不触发。',
}

encounters = {
    'LIGHTSWORN_ENCOUNTER_DARK_WORLD_GRAPHA_BOSS.title': '暗黑界的龙神王 格拉法',
    'LIGHTSWORN_ENCOUNTER_DARK_WORLD_GRAPHA_BOSS.loss':
        '{character}被[gold]{encounter}[/gold]拖入了黑暗世界的深渊。',
}

monsters = {
    'LIGHTSWORN_MONSTER_DARK_WORLD_GRAPHA.name': '暗黑界的龙神王 格拉法',
    'LIGHTSWORN_MONSTER_DARK_WORLD_GRAPHA.moves.DARK_WORLD_THUNDER.title': '暗黑界之雷',
    'LIGHTSWORN_MONSTER_DARK_WORLD_GRAPHA.moves.DARK_WORLD_FORCES.title': '暗黑界的军势',
    'LIGHTSWORN_MONSTER_DARK_WORLD_GRAPHA.moves.DARK_WORLD_ASCENSION.title': '暗黑界的登极',
    'LIGHTSWORN_MONSTER_DARK_WORLD_GRAPHA.moves.DARK_WORLD_RETURN.title': '龙神回归',
    'LIGHTSWORN_MONSTER_DARK_WORLD_GRAPHA.moves.DARK_WORLD_RETURN.intentLabel': '回复 {Amount} 点生命',
    'LIGHTSWORN_MONSTER_DARK_WORLD_GRAPHA.moves.DARK_WORLD_DEALINGS.title': '暗黑界的取引',
    'LIGHTSWORN_MONSTER_DARK_WORLD_GRAPHA.moves.DARK_WORLD_BRAINWASH.title': '暗黑界的洗脑',
    'LIGHTSWORN_MONSTER_DARK_WORLD_GRAPHA.intents.RETURN_TIP':
        '吸收玩家抽牌堆、弃牌堆、消耗堆中的所有暗黑界牌（不含「暗黑界的洗脑」），每张回复{Heal}点生命；本次共{Count}张，预计回复{Total}点。被吸收的牌移出战斗。',
    'LIGHTSWORN_MONSTER_DARK_WORLD_GRAPHA.intents.DEALINGS_SHORT': '取引',
    'LIGHTSWORN_MONSTER_DARK_WORLD_GRAPHA.intents.DEALINGS_TIP':
        '施加5层虚弱和5层易伤；生成2张随机暗黑界牌到手牌，然后弃置手牌中所有暗黑界牌（「暗黑界的洗脑」除外）。',
    'LIGHTSWORN_MONSTER_DARK_WORLD_GRAPHA.intents.BRAINWASH_TIP':
        '将{CardCount}张「暗黑界的洗脑」洗入你的抽牌堆。',
}

for lang in ('zhs', 'eng'):
    base = os.path.join(LOC, lang)
    os.makedirs(base, exist_ok=True)

    cards_path = os.path.join(base, 'cards.json')
    cards = load(cards_path) if os.path.exists(cards_path) else {}
    cards.update(cards_add)
    save(cards_path, cards)

    powers_path = os.path.join(base, 'powers.json')
    powers = load(powers_path) if os.path.exists(powers_path) else {}
    powers.update(powers_add)
    save(powers_path, powers)

    encounters_path = os.path.join(base, 'encounters.json')
    encounters_data = load(encounters_path) if os.path.exists(encounters_path) else {}
    encounters_data.update(encounters)
    save(encounters_path, encounters_data)

    monsters_path = os.path.join(base, 'monsters.json')
    monsters_data = load(monsters_path) if os.path.exists(monsters_path) else {}
    monsters_data.update(monsters)
    save(monsters_path, monsters_data)

# 校验
for lang in ('zhs', 'eng'):
    base = os.path.join(LOC, lang)
    for fname, expected in (('cards.json', cards_add), ('powers.json', powers_add),
                            ('encounters.json', encounters), ('monsters.json', monsters)):
        data = load(os.path.join(base, fname))
        missing = [k for k in expected if k not in data]
        if missing:
            raise SystemExit('%s/%s missing keys: %s' % (lang, fname, missing))
print('all localization keys verified (zhs + eng fallback)')
