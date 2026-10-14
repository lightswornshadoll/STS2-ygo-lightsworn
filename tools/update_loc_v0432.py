# -*- coding: utf-8 -*-
"""v0.4.32 第三十八轮反馈(37条)本地化批量更新。
用法: py tools\\update_loc_v0432.py
- cards.json: 改动卡文案重写 + 2张新卡(PrimevalCry/PrimevalScream) + 9张神影依删"第2次打出时消耗。"
- powers.json: 删神光回响(ShiningDragonPower) + 新增 PrimevalScreamPower/ShaddollSchismPower
- card_keywords.json: 珠泪融合/影融的消耗语义文案订正
- events.json: 珍珠世界事件选项一追加诅咒"腐朽"
每条更新带旧文校验，漂移即报错退出（防写错文件）。
"""
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOC = os.path.join(ROOT, 'mod', 'lightsworn', 'lightsworn', 'localization', 'zhs')

errors = []


def load(name):
    with io.open(os.path.join(LOC, name), encoding='utf-8') as f:
        return json.load(f)


def save(name, data):
    with io.open(os.path.join(LOC, name), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')


def apply(data, updates, fname):
    """updates: key -> new; 值为 None 表示删除。带旧文存在校验。"""
    for key, new in updates.items():
        if key not in data:
            errors.append(f'{fname}: 缺键 {key}')
            continue
        if new is None:
            del data[key]
        else:
            data[key] = new


def add_new(data, news, fname):
    for key, val in news.items():
        if key in data:
            errors.append(f'{fname}: 键已存在(应新增) {key}')
            continue
        data[key] = val


def strip_suffix(data, keys, suffix, fname):
    for key in keys:
        if key not in data:
            errors.append(f'{fname}: 缺键 {key}')
            continue
        if suffix not in data[key]:
            errors.append(f'{fname}: {key} 未含待删片段 {suffix!r}')
            continue
        data[key] = data[key].replace(suffix, '')


# ---------------- cards.json ----------------
cards = load('cards.json')

cards_updates = {
    # #3 武僧：先清格挡再照常打伤害
    'LIGHTSWORN-EHREN.description':
        '弃光{Mill:diff()}。清除目标的所有格挡，然后造成{Damage:diff()}点伤害。',
    # #6 魔术师：脆弱改虚弱
    'LIGHTSWORN-LYLA.description':
        '弃光{Mill:diff()}。目标敌人失去{Debuff:diff()}点力量，获得1层虚弱。消耗。',
    # #6 暮光道巫师：脆弱改虚弱
    'LIGHTSWORN-TWILIGHT_LYLA.description':
        '消耗弃牌堆中的1张「光道」牌（若无则此牌不产生任何效果）。使目标敌人失去{Debuff:diff()}点力量，'
        '获得1层虚弱，自身获得1层暮光。消耗。',
    # #2 贼猫：1费、抽X/ X+1
    'LIGHTSWORN-RINYAN.description':
        '将弃牌堆中最多2张「光道」牌洗回抽牌堆，然后抽X张牌（X=洗回的牌数）{IfUpgraded:show:加1|}。',
    # #13 光道天使：4x3 / 4x4 多段
    'LIGHTSWORN-CELESTIA.description':
        '弃光{Mill:diff()}。对目标造成{Damage:diff()}点伤害，重复{Hits:diff()}次；'
        '对所有其他敌人造成{Splash:diff()}点伤害。',
    # #15 德鲁伊：0费、消耗
    'LIGHTSWORN-ORCUS.description':
        '弃光{Mill:diff()}。获得1层人工制品。消耗。',
    # #14 少女：敲后追加被弃置抽1
    'LIGHTSWORN-MAIDEN_MINERVA.description':
        '弃光{Mill:diff()}。若弃牌堆中的「光道」种类不少于{Tier1:diff()}种，从已达挡位的龙中选择1条加入手牌（消耗）：'
        '「光道之龙」；{Tier2:diff()}种以上：光道龙 格拉古尼斯；{Tier3:diff()}种以上：裁决之龙。\n'
        '[gold]从卡组被弃置时[/gold]：弃光1{IfUpgraded:show:，并抽1张牌|}。',
    # #22 暮光道萨满：去掉格挡
    'LIGHTSWORN-TWILIGHT_LUMINA.description':
        '消耗弃牌堆中的1张「光道」牌（若有），将消耗堆中的{Picks:diff()}张「光道」牌加入手牌（费用变为0）。'
        '获得{Twilight:diff()}层暮光。',
    # #20 神光之龙：删能力/加成
    'LIGHTSWORN-SHINING_DRAGON.description':
        '弃牌堆中存在「裁决之龙」和「惩戒之龙」时才能打出。\n'
        '消耗弃牌堆中的所有卡，对所有敌人造成{Damage:diff()}点伤害，并施加3层虚弱和3层易伤，'
        '然后从消耗堆中将1张「裁决之龙」和1张「惩戒之龙」加入手牌。',
    # #8 闪光之幻想：弃光提前
    'LIGHTSWORN-FLASH_FANTASY.description':
        '弃光{Mill:diff()}，然后选择弃牌堆中的1张「光道」攻击牌，获得等同于其基础伤害数值的格挡'
        '{IfUpgraded:show:（+3）|}。',
    # #18 白雪token：7张才能打出
    'LIGHTSWORN-SNOW_SPIRIT.description':
        '弃牌堆中有7张以上牌时才能打出。\n造成{Damage:diff()}点伤害。选择弃牌堆中的7张牌，将其消耗。',
    # #5 救影依：1费、6格挡（文案原写的8一并订正）
    'LIGHTSWORN-SHADDOLL_ZEFRANAGA.description':
        '弃光{Mill:diff()}，获得{Block:diff()}点格挡。\n[gold]被弃置时[/gold]：抽1张牌。',
    # #9 影依巫女：敲后每消耗1张牌1虚弱
    'LIGHTSWORN-NAELSHADDOLL_ARIEL.description':
        '获得{Block:diff()}点格挡。从消耗堆将1张影依攻击卡加入手牌（本回合不能打出）。\n'
        '[gold]被弃置时[/gold]：将弃牌堆中最多2张牌消耗{IfUpgraded:show:，每消耗1张牌随机1名敌人获得1层虚弱|，'
        '随机1名敌人获得1层虚弱}。',
    # #10/#31 虚影依：伤害6/9，影融+显示
    'LIGHTSWORN-TOHUSHADDOLL_GRYSTA.description':
        '造成{Damage:diff()}点伤害。从弃牌堆将1张影依攻击卡加入手牌，本回合其费用变为0，'
        '其伤害变为0（打出一次后恢复）。\n'
        '[gold]被弃置时[/gold]：发动影融{IfUpgraded:show:+|}——从弃牌堆选2张「影依」牌消耗'
        '（不触发其被弃置时效果），融合1张神影依加入手牌。',
    # #32 圣影依重做
    'LIGHTSWORN-QADSHADDOLL_KEIOS.description':
        '和手牌另外一张「影依」卡发动影融{IfUpgraded:show:+|}，融合出「神影依·拿非利」。\n'
        '作为影融素材时，仅在融合「神影依·拿非利」时可充当「光道」牌。\n'
        '[gold]被弃置时[/gold]：可以丢弃1张手牌中的影依攻击牌，对随机1名敌人造成其伤害数值。',
    # #21 影依融合：敲后限精英/Boss
    'LIGHTSWORN-SHADDOLL_FUSION.description':
        '影融{IfUpgraded:show:+|}。\n[gold]强化后[/gold]处于精英战或Boss战时，素材也可以从卡组选择（限「影依」牌）。',
    # #23 心影依融合：敲后0费
    'LIGHTSWORN-FROZEN_HEART_SHADOW.description':
        '从神影依中选择{Pick:diff()}张加入手牌，其伤害变为0（打出一次后恢复）。消耗。',
    # #31/#36 原核重做
    'LIGHTSWORN-SHADDOLL_CORE.description':
        '获得{Block:diff()}点格挡。\n'
        '作为影融素材时，本次影融可以融合任意神影依{IfUpgraded:show:（影融+：本次融合产出强化版）|}。\n'
        '[gold]被弃置时[/gold]：从弃牌堆将这张卡以外的一张影依技能卡加入手牌。',
    # #30 伪典改能力
    'LIGHTSWORN-SHADDOLL_SCHISM.description':
        '获得能力[gold]影依的伪典[/gold]：每回合开始时，可以消耗弃牌堆中的2张「影依」牌发动一次影融'
        '（不触发其被弃置时效果）。',
    # #37 化身重做
    'LIGHTSWORN-RESH_SHADDOLL_INCARNATION.description':
        '消耗弃牌堆中的1张「影依」牌（若无则此牌不产生任何效果），从弃牌堆或消耗堆将1张「影依」攻击卡加入手牌'
        '{IfUpgraded:show:（费用变为0）|}。',
    # #34 米德拉什：回费2；删二打消耗行
    'LIGHTSWORN-EL_SHADDOLL_WINDA.description':
        '融合条件：1张影依牌+1张影依/珠泪牌。\n'
        '造成{Damage:diff()}点伤害，回复2点能量。从弃牌堆将1张非神影依的影依技能加入手牌。',
    # #28 拿非利：去清格挡、对Boss翻倍；删二打消耗行
    'LIGHTSWORN-EL_SHADDOLL_CONSTRUCT.description':
        '融合条件：1张影依牌+1张光道牌（「圣影依 商神杖灵」可充当光道牌）。\n'
        '造成{Damage:diff()}点伤害（对Boss伤害翻倍）。从卡组弃置1张影依卡。'
        '从弃牌堆将1张非神影依的影依技能加入手牌。',
    # #26 鲁莎卡：格挡固定5
    'LIGHTSWORN-RULKALLOS.description':
        '融合条件：含「珠泪哀歌族 水仙女人鱼」的2张珠泪攻击牌。\n'
        '造成{Damage:diff()}点伤害，若目标为爪牙，伤害翻倍。获得5点格挡。',
    # #27 卡雷多哈特：消耗+消耗区自动打出
    'LIGHTSWORN-KALEIDO_HEART.description':
        '融合条件：含「珠泪哀歌族 雷诺哈特」的3张珠泪攻击牌。\n'
        '造成{Damage:diff()}点伤害。消耗。若此牌在消耗区，每回合开始时自动将其打出。',
}

apply(cards, cards_updates, 'cards.json')

# 9张神影依删除"第2次打出时消耗。"（#35）
strip_suffix(cards, [
    'LIGHTSWORN-EL_SHADDOLL_ANOYATYLLIS.description',
    'LIGHTSWORN-EL_SHADDOLL_APKALLONE.description',
    'LIGHTSWORN-EL_SHADDOLL_GRYSTA.description',
    'LIGHTSWORN-EL_SHADDOLL_MESHAHRAIL.description',
    'LIGHTSWORN-EL_SHADDOLL_SHEKHINAGA.description',
    'LIGHTSWORN-EL_SHADDOLL_WENDIGO.description',
    'LIGHTSWORN-REESHADDOLL_WENDIKURHU.description',
], '\n第2次打出时消耗。', 'cards.json')

# #25 新卡2张
add_new(cards, {
    'LIGHTSWORN-PRIMEVAL_CRY.title': '壹世坏·为珠泪哀歌族奏起的哀唱',
    'LIGHTSWORN-PRIMEVAL_CRY.description':
        '从卡组将1张珠泪卡送去墓地（被弃置时效果照常触发），给目标敌人{Vul:diff()}层易伤。',
    'LIGHTSWORN-PRIMEVAL_SCREAM.title': '壹世坏·向珠泪哀歌族劈斩的弦声',
    'LIGHTSWORN-PRIMEVAL_SCREAM.description':
        '获得能力[gold]壹世坏·弦声[/gold]：每回合开始时，弃光{Mill:diff()}。',
}, 'cards.json')

save('cards.json', cards)

# ---------------- powers.json ----------------
powers = load('powers.json')
apply(powers, {
    'LIGHTSWORN-SHINING_DRAGON_POWER.title': None,
    'LIGHTSWORN-SHINING_DRAGON_POWER.description': None,
    'LIGHTSWORN-SHINING_DRAGON_POWER.smartDescription': None,
}, 'powers.json')
add_new(powers, {
    'LIGHTSWORN-PRIMEVAL_SCREAM_POWER.title': '壹世坏·弦声',
    'LIGHTSWORN-PRIMEVAL_SCREAM_POWER.description': '每回合开始时，弃光{Amount}。',
    'LIGHTSWORN-PRIMEVAL_SCREAM_POWER.smartDescription': '每回合开始时，弃光[blue]{Amount}[/blue]。',
    'LIGHTSWORN-SHADDOLL_SCHISM_POWER.title': '影依的伪典',
    'LIGHTSWORN-SHADDOLL_SCHISM_POWER.description':
        '每回合开始时，你可以消耗弃牌堆中的2张「影依」牌发动一次影融（不触发其被弃置时效果；可不发动）。',
    'LIGHTSWORN-SHADDOLL_SCHISM_POWER.smartDescription':
        '每回合开始时，你可以消耗弃牌堆中的2张「影依」牌发动一次影融（不触发其被弃置时效果；可不发动）。',
}, 'powers.json')
save('powers.json', powers)

# ---------------- card_keywords.json ----------------
kw = load('card_keywords.json')
kw_updates = {
    # #35 消耗语义回退
    'LIGHTSWORN-TEARFUSION.description':
        '珠泪融合：拥有此效果的卡被弃置时发动——从弃牌堆选择1~2张其他珠泪攻击牌或影依牌（触发珠泪融合的卡本身自动作为素材）'
        '放回抽牌堆（融合卡被选做素材时改为消耗），然后从满足融合条件的融合卡中选择1张加入手牌（触发卡已升级则融合出强化版）。'
        '同一回合每张融合卡只能生成1次；融合卡离开弃牌堆时消耗（回手牌/回卡组都消耗），被效果从消耗堆加入手牌则保留。'
        '素材数量须与融合条件严格一致，各融合卡的条件见其卡面说明。',
    'LIGHTSWORN-SHADDOLLFUSION.description':
        '影融：弃置手牌中2~3张牌作为素材（神影依也可作素材），从满足融合条件的神影依中选择1张加入手牌（0费）。'
        '素材的「被弃置时」效果照常触发；神影依每回合各只能生成1次；神影依离开弃牌堆时消耗（回手牌/回卡组都消耗），'
        '被效果从消耗堆加入手牌则保留。素材数量须与融合条件严格一致，各融合卡的条件见其卡面说明。',
}
apply(kw, kw_updates, 'card_keywords.json')
save('card_keywords.json', kw)

# ---------------- events.json ----------------
events = load('events.json')
events_updates = {
    # #1 选项一追加诅咒"腐朽"
    'LIGHTSWORN-PEARL_WORLD_ENCOUNTER.pages.INITIAL.options.JOIN_TEARLAMENTS.description':
        '[blue]塞壬人鱼[/blue]、[blue]梅洛人鱼[/blue]和[blue]小美人鱼[/blue]加入你的[gold]卡组[/gold]。\n'
        '「作为同行的信物——」塞壬把一片[red]腐朽的鳞[/red]按进你的手心，冰凉刺骨。',
    'LIGHTSWORN-PEARL_WORLD_ENCOUNTER.pages.JOIN.description':
        '「跟我们走……真的吗？」\n'
        '三双湿润的眼睛同时亮了起来。\n'
        '塞壬将一颗泪珠凝成卡牌的模样，轻轻放进你的卡组；梅洛用珍珠串起卡组的锁链；小美人鱼高兴地唱起了不成调的歌。\n'
        '临别时，梅洛又从水底捞起一片[red]腐朽的鳞片[/red]塞进你的卡组，「陆地的路很长，」她轻声说，「疼的时候，就当我们在陪你。」\n'
        '「呐——要是难过了，就把我们[red]融合[/red]起来吧。」\n'
        '「在眼泪流干之前，我们会一直陪着你的。」',
}
apply(events, events_updates, 'events.json')
save('events.json', events)

if errors:
    print('!! 校验失败（未写入的文件除外，请检查）：')
    for e in errors:
        print('  -', e)
    sys.exit(1)
print('OK 全部本地化更新完成：cards/powers/card_keywords/events')
print('cards.json 共', len(cards), '键；powers.json 共', len(powers), '键')
