# -*- coding: utf-8 -*-
"""v0.7.3 本地化：已知问题 1-4 的文案同步（zhs + eng 回退）。"""
import io, json, os

ROOT = r'D:\1-workdata\lightsworn_mod\mod\lightsworn\lightsworn\localization'


def load(path):
    with io.open(path, encoding='utf-8') as f:
        return json.load(f)


def save(path, data):
    # 仓库内本地化 json 统一 CRLF（与既有文件一致，避免整文件 diff）
    with io.open(path, 'w', encoding='utf-8', newline='\r\n') as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def put(data, key, value):
    assert key in data, 'missing key: ' + key
    data[key] = value


EVENT = 'LIGHTSWORN_EVENT_THIRD_ACT_BOSS_CHOICE_ENCOUNTER'
ev_zhs = {
    f'{EVENT}.title': '最远方的宇宙',
    f'{EVENT}.pages.INITIAL.description':
        '第二层的首领已经倒下，通往第三层的阶梯尽头忽然豁开。\n'
        '那是一片[purple]星光璀璨的宇宙[/purple]，星尘在无边的黑暗里静静旋转，远比尖塔的任何一扇窗都要辽阔。\n'
        '只要向前一步，就能踏入这片宇宙；但脚下的尖塔仍在低语，提醒你遵从那古老而熟悉的秩序。\n'
        '要踏入这片宇宙吗？',
    f'{EVENT}.pages.INITIAL.options.CHOOSE_MOD.title': '踏入这片宇宙',
    f'{EVENT}.pages.INITIAL.options.CHOOSE_MOD.description':
        '第三层的首领将来自[purple]宇宙的另一侧[/purple]。',
    f'{EVENT}.pages.INITIAL.options.CHOOSE_VANILLA.title': '停留在原地',
    f'{EVENT}.pages.INITIAL.options.CHOOSE_VANILLA.description':
        '第三层仍将遵从这个世界的法则。',
    f'{EVENT}.pages.DONE.description':
        '你迈出脚步，星光在身后合拢。\n'
        '第三层的深处，有什么东西缓缓睁开了眼睛。',
    f'{EVENT}.pages.NO_BOSS.description':
        '你伸手触碰星海，却只摸到一片虚空。\n（未找到任何可用的 Boss，本事件不会改写第三层。）',
}
ev_eng = {
    f'{EVENT}.title': 'The Farthest Universe',
    f'{EVENT}.pages.INITIAL.description':
        'The Act II boss has fallen, and the stairway to Act III breaks open at its end.\n'
        'Beyond it lies a [purple]starry universe[/purple], its dust turning silently in the endless dark, vaster than any window of the Spire.\n'
        'One step forward would carry you into that universe; yet the Spire whispers beneath your feet, urging you to keep to its ancient, familiar order.\n'
        'Will you step into this universe?',
    f'{EVENT}.pages.INITIAL.options.CHOOSE_MOD.title': 'Step Into the Universe',
    f'{EVENT}.pages.INITIAL.options.CHOOSE_MOD.description':
        'The Act III boss will come from [purple]the far side of the universe[/purple].',
    f'{EVENT}.pages.INITIAL.options.CHOOSE_VANILLA.title': 'Remain Where You Stand',
    f'{EVENT}.pages.INITIAL.options.CHOOSE_VANILLA.description':
        'Act III will still follow the laws of this world.',
    f'{EVENT}.pages.DONE.description':
        'You take a step, and the starlight closes behind you.\n'
        'Deep in Act III, something slowly opens its eyes.',
    f'{EVENT}.pages.NO_BOSS.description':
        'You reach into the starry sea, but find only emptiness.\n'
        '(No eligible boss was found; the event will not change Act III.)',
}

BRAINWASH_DESC = '打出的下一张攻击、技能或能力牌无效（费用照付，牌进入弃牌堆）。可叠加；每层吞掉一张牌。'
BRAINWASH_SMART = BRAINWASH_DESC + '（剩余[blue]{Amount}[/blue]层）'
BRAINWASH_CARD = '抽到时自动打出：获得1层[gold]洗脑[/gold]。\n[gold]洗脑[/gold]：打出的下一张攻击、技能或能力牌无效（可叠加、跨回合保留）。'

PUNISH_DESC = (
    '消耗堆中存在4种以上「光道」牌时才能打出。\n'
    '将弃牌堆与消耗堆中所有非「光道」的攻击、技能、能力牌返回卡组，每有一张，所有敌人随机获得1层负面状态'
    '（易伤、虚弱、中毒或灾厄；每次有1%概率改为击晕所有敌人）。'
    '造成{Damage:diff()}点伤害，并获得1层[gold]暮光[/gold]。'
)

for lang, ev, brain_desc, brain_smart, brain_card, punish in [
    ('zhs', ev_zhs, BRAINWASH_DESC, BRAINWASH_SMART, BRAINWASH_CARD, PUNISH_DESC),
    ('eng', ev_eng, BRAINWASH_DESC, BRAINWASH_SMART, BRAINWASH_CARD, PUNISH_DESC),
]:
    ep = os.path.join(ROOT, lang, 'events.json')
    d = load(ep)
    for k, v in ev.items():
        put(d, k, v)
    save(ep, d)

    pp = os.path.join(ROOT, lang, 'powers.json')
    d = load(pp)
    for base in ('LIGHTSWORN_POWER_DARK_WORLD_BRAINWASH_POWER', 'DARK_WORLD_BRAINWASH_POWER'):
        put(d, base + '.description', brain_desc)
        put(d, base + '.smartDescription', brain_smart)
    save(pp, d)

    cp = os.path.join(ROOT, lang, 'cards.json')
    d = load(cp)
    put(d, 'LIGHTSWORN_CARD_DARK_WORLD_BRAINWASHING.description', brain_card)
    if 'LIGHTSWORN_CARD_PUNISH_DRAGON.description' in d:
        d['LIGHTSWORN_CARD_PUNISH_DRAGON.description'] = punish
    save(cp, d)

print('loc updated: events/powers/cards (zhs+eng)')
