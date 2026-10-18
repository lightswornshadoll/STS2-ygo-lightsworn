# -*- coding: utf-8 -*-
# 提耶拉 Boss 本地化（zhs + eng 回退；能力短键 + 长键并存）。
import io
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOC = os.path.join(ROOT, 'mod', 'lightsworn', 'lightsworn', 'localization')


def load(path):
    with io.open(path, encoding='utf-8-sig') as f:
        return json.load(f)


def save(path, data):
    text = json.dumps(data, ensure_ascii=False, indent=2)
    text = text.replace('\n', '\r\n')
    with io.open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(text)


def update(lang, filename, entries):
    path = os.path.join(LOC, lang, filename)
    data = load(path) if os.path.isfile(path) else {}
    for key, value in entries.items():
        data[key] = value
    save(path, data)
    print(lang, filename, 'updated', len(entries))


PREFIX = 'LIGHTSWORN_MONSTER_INFERNOID_TIERRA'

monster_entries = {
    f'{PREFIX}.name': '狱火机·提耶拉',
    f'{PREFIX}.phase2Name': '创星神·提耶拉',
    f'{PREFIX}.moves.INFERNOID_DECATRON.title': '十进管',
    f'{PREFIX}.moves.INFERNOID_BEELZEBUB.title': '别西卜',
    f'{PREFIX}.moves.INFERNOID_LUCIFUGUS.title': '路西弗格',
    f'{PREFIX}.moves.INFERNOID_ASTAROTH.title': '阿斯塔罗特',
    f'{PREFIX}.moves.INFERNOID_ASMODEUS.title': '阿斯蒙蒂斯',
    f'{PREFIX}.moves.INFERNOID_BELPHEGOR.title': '贝尔芬格',
    f'{PREFIX}.moves.INFERNOID_BAAL.title': '巴力',
    f'{PREFIX}.moves.INFERNOID_ADRAMMELECH.title': '亚得米勒',
    f'{PREFIX}.moves.INFERNOID_LILITH.title': '莉莉丝',
    f'{PREFIX}.moves.INFERNOID_NAAMAH.title': '拿玛',
    f'{PREFIX}.moves.STAR_TRANSFORM.title': '创星',
    f'{PREFIX}.moves.INFERNOID_EVIL.title': '邪恶',
    f'{PREFIX}.moves.INFERNOID_FLOOD.title': '洪水',
    f'{PREFIX}.moves.VOID_IMAGINATION.title': '虚梦',
    f'{PREFIX}.moves.VOID_APOCALYPSE.title': '灾天',
    f'{PREFIX}.moves.STAR_CREATION.title': '创星·灭世',
    f'{PREFIX}.intents.TRIBUTE': '献祭：弃1张非狱火机，塞1张诅咒',
    f'{PREFIX}.intents.TRIBUTE_SHORT': '献祭',
    f'{PREFIX}.intents.TRIBUTE_TIP': '从弃牌堆消耗1张非狱火机；然后Boss将1张随机狱火机诅咒洗入你的抽牌堆。',
    f'{PREFIX}.intents.DECATRON_SHORT': '复制：{Demon}',
    f'{PREFIX}.intents.DECATRON_TIP': '十进管：随机复制2-10中一只狱火机的动作。本次复制：{Demon}（{Damage}伤害 / 对应效果）。',
    f'{PREFIX}.intents.DECATRON_COPY_ATTACK': '十进管复制：{Demon}（{Damage}伤害）',
    f'{PREFIX}.intents.DECATRON_COPY_DEFEND': '十进管复制：{Demon}（获得20格挡）',
    f'{PREFIX}.intents.NULLIFY_FUSION_SHORT': '融合无效',
    f'{PREFIX}.intents.NULLIFY_FUSION_TIP': '你的下1张融合卡无效（费用照付，不执行效果）。',
    f'{PREFIX}.intents.EXHAUST_SKILLS_SHORT': '清技能',
    f'{PREFIX}.intents.EXHAUST_SKILLS_TIP': '消耗你弃牌堆中所有技能牌；你的下1张攻击卡无效。',
    f'{PREFIX}.intents.EXHAUST_ATTACKS_SHORT': '清攻击',
    f'{PREFIX}.intents.EXHAUST_ATTACKS_TIP': '消耗你弃牌堆中所有攻击牌；你的下1张技能卡无效。',
    f'{PREFIX}.intents.EXHAUST_GENERATE_SHORT': '除外生成',
    f'{PREFIX}.intents.EXHAUST_GENERATE_TIP': '随机除外弃牌堆1张狱火机，生成等于其等级的随机狱火机到弃牌堆。',
    f'{PREFIX}.intents.TRIBUTE_ON_EXHAUST_SHORT': '除外献祭',
    f'{PREFIX}.intents.TRIBUTE_ON_EXHAUST_TIP': '下回合每除外1张狱火机诅咒，从弃牌堆选1张非狱火机消耗。',
    f'{PREFIX}.intents.RETURN_FUEL_SHORT': '回收燃料',
    f'{PREFIX}.intents.RETURN_FUEL_TIP': '将除外区2张狱火机放回弃牌堆。',
    f'{PREFIX}.intents.HALF_DAMAGE_SHORT': '半伤',
    f'{PREFIX}.intents.HALF_DAMAGE_TIP': '你的下2张攻击卡伤害减半。',
    f'{PREFIX}.intents.DISCARD_ONE_SHORT': '随机弃牌',
    f'{PREFIX}.intents.DISCARD_ONE_TIP': '下回合抽牌后随机弃置1张手牌。',
    f'{PREFIX}.intents.GENERATE_FUEL_SHORT': '生成燃料',
    f'{PREFIX}.intents.GENERATE_FUEL_TIP': '生成2张随机狱火机诅咒到弃牌堆；有融合卡时再生成6张。',
    f'{PREFIX}.intents.APOCALYPSE_SHORT': '灭世',
    f'{PREFIX}.intents.APOCALYPSE_TIP': '手牌与弃牌堆洗回抽牌堆；下回合只抽1张并失去1点能量；Boss回复100生命并获得2仪式。',
    f'{PREFIX}.intents.NULLIFY_FUSION': '下张融合无效',
    f'{PREFIX}.intents.EXHAUST_SKILLS': '消耗弃牌堆全部技能',
    f'{PREFIX}.intents.EXHAUST_ATTACKS': '消耗弃牌堆全部攻击',
    f'{PREFIX}.intents.EXHAUST_GENERATE': '除外1张狱火机，生成等量诅咒',
    f'{PREFIX}.intents.TRIBUTE_ON_EXHAUST': '除外诅咒时献祭',
    f'{PREFIX}.intents.RETURN_FUEL': '回收2张狱火机',
    f'{PREFIX}.intents.HALF_DAMAGE': '下2张攻击伤害减半',
    f'{PREFIX}.intents.DISCARD_ONE': '下回合随机弃1张',
    f'{PREFIX}.intents.GENERATE_FUEL': '生成狱火机诅咒',
    f'{PREFIX}.intents.APOCALYPSE': '创星·灭世（重罚）',
}

encounter_entries = {
    'LIGHTSWORN_ENCOUNTER_INFERNOID_TIERRA_BOSS.title': '狱火机·提耶拉',
    'LIGHTSWORN_ENCOUNTER_INFERNOID_TIERRA_BOSS.loss':
        '{character}被[gold]{encounter}[/gold]炼成了创星的燃料。',
}

cards = {
    'InfernoidDecatron': ('狱火机 十进管',
        '不可打出。被弃置时：随机复制2-10中一张狱火机诅咒的触发效果（无需召唤代价）。'),
    'InfernoidBeelzebub': ('狱火机·别西卜',
        '不可打出。被弃置时：消耗弃牌堆1张其他狱火机，将1张随机手牌洗回抽牌堆。'),
    'InfernoidLucifugus': ('狱火机·路西弗格',
        '不可打出。被弃置时：消耗弃牌堆1张其他狱火机，获得2层虚弱。'),
    'InfernoidAstaroth': ('狱火机·阿斯塔罗特',
        '不可打出。被弃置时：消耗弃牌堆1张其他狱火机，消耗手牌中1张技能牌。'),
    'InfernoidAsmodeus': ('狱火机·阿斯蒙蒂斯',
        '不可打出。被弃置时：消耗弃牌堆2张其他狱火机，随机弃置1张手牌。'),
    'InfernoidBelphegor': ('狱火机·贝尔芬格',
        '不可打出。被弃置时：消耗弃牌堆2张其他狱火机，本回合下1张融合卡无效。'),
    'InfernoidBaal': ('狱火机·巴力',
        '不可打出。被弃置时：消耗弃牌堆2张其他狱火机，消耗抽牌堆和弃牌堆各1张牌。'),
    'InfernoidAdrammelech': ('狱火机·亚得米勒',
        '不可打出。被弃置时：消耗弃牌堆2张其他狱火机，受到8点伤害两次。'),
    'InfernoidLilith': ('狱火机·莉莉丝',
        '不可打出。被弃置时：消耗弃牌堆3张其他狱火机，消耗手牌和弃牌堆中所有技能牌。'),
    'InfernoidOnuncu': ('狱火机·拿玛',
        '不可打出。被弃置时：消耗弃牌堆3张其他狱火机，弃置所有手牌。'),
}

card_entries = {}
for cls, (title, desc) in cards.items():
    base = 'LIGHTSWORN_CARD_' + ''.join(
        ('_' + ch if ch.isupper() and i else ch) for i, ch in enumerate(cls)).upper()
    card_entries[base + '.title'] = title
    card_entries[base + '.description'] = desc

powers = {
    'INFERNOID_MATERIAL_POWER': (
        '逆生命树',
        'Boss 的动作取决于回合开始时点亮的节点数。每当新的非十进管狱火机诅咒进入消耗堆时，点亮1个节点（每名玩家每种只算一次）。' + chr(10) +
        '点亮第{T3}个节点：融合封印——选择至多3张本回合尚未生成的融合卡，本回合视为已生成；没有可选融合卡时，将1张随机狱火机诅咒洗入抽牌堆。' + chr(10) +
        '点亮第{T5}个节点：弃光3，并将3张随机狱火机诅咒置入弃牌堆。' + chr(10) +
        '点亮第{T8}个节点：从除外区选至多3张非狱火机与3张狱火机放回弃牌堆。' + chr(10) +
        '点亮第{T10}个节点：丢弃全部手牌，每弃1张将1张随机狱火机诅咒置入弃牌堆。Boss 下个回合攻击结算完毕时，节点重置为{Base}。' + chr(10) +
        '当前节点：{Amount}/{Max}。'),
    'STAR_CREATION_POWER': (
        '创星',
        '创星 {Gauge}/{Max}：每个 Boss 回合结束+2×玩家数；阶段2内每名玩家每引爆一种新的狱火机诅咒+1。'
        '达到{Max}时，提耶拉的下一招变为「创星·灭世」。已引爆种类：{Types}（{TypeCount}/{Max}）。'),
    'INFERNOID_TIERRA_PHASE_GATE_POWER': (
        '不灭之核',
        '一阶段生命打空时不会死亡，而是进入第二阶段「创星神·提耶拉」。'),
    'TIERRA_SHUFFLE_ONE_POWER': (
        '别西卜之惑',
        '下回合抽牌后，随机将1张手牌洗回抽牌堆。'),
    'TIERRA_DISCARD_ONE_POWER': (
        '阿斯蒙蒂斯之惑',
        '下回合抽牌后，随机弃置1张手牌。'),
    'TIERRA_FUSION_NULLIFY_POWER': (
        '融合封锁',
        '下1张融合卡无效（费用照付，不执行效果）。剩余[blue]{Amount}[/blue]张。'),
    'TIERRA_ATTACK_NULLIFY_POWER': (
        '攻击封锁',
        '下1张攻击卡无效。剩余[blue]{Amount}[/blue]张。'),
    'TIERRA_SKILL_NULLIFY_POWER': (
        '技能封锁',
        '下1张技能卡无效。剩余[blue]{Amount}[/blue]张。'),
    'TIERRA_HALF_DAMAGE_POWER': (
        '虚梦',
        '接下来[blue]{Amount}[/blue]张攻击卡造成的伤害减半。'),
    'TIERRA_FLOOD_TRIBUTE_POWER': (
        '洪水',
        '本回合每除外1张狱火机诅咒，从弃牌堆选1张非狱火机消耗。'),
    'TIERRA_APOCALYPSE_POWER': (
        '创星·灭世',
        '下回合只能抽1张牌，并失去1点能量。'),
}

power_entries = {}
for stem, (title, desc) in powers.items():
    power_entries[f'LIGHTSWORN_POWER_{stem}.title'] = title
    power_entries[f'{stem}.title'] = title
    power_entries[f'LIGHTSWORN_POWER_{stem}.description'] = desc
    power_entries[f'{stem}.description'] = desc

selection = {
    'LIGHTSWORN_TIERRA_TRIBUTE': '献祭：从弃牌堆选择1张非狱火机消耗',
    'LIGHTSWORN_TIERRA_RECOVER_NONINFERNOID': '回收：从消耗堆选择至多3张非狱火机放回弃牌堆（可不选）',
    'LIGHTSWORN_TIERRA_RECOVER_INFERNOID': '回收：从消耗堆选择至多3张狱火机放回弃牌堆（可不选）',
    'LIGHTSWORN_TIERRA_SEAL_FUSION': '融合封印：选择至多3张本回合尚未生成的融合卡（本回合视为已生成）',
}

for lang in ('zhs', 'eng'):
    update(lang, 'monsters.json', monster_entries)
    update(lang, 'encounters.json', encounter_entries)
    update(lang, 'cards.json', card_entries)
    update(lang, 'powers.json', power_entries)
    update(lang, 'card_selection.json', selection)

print('done')
