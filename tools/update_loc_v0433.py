# -*- coding: utf-8 -*-
"""v0.4.33 订正三条（用户验收反馈）：本地化批量更新。
1. 光道天使：4x3/4x4改为对所有敌人，删除溅射文本
2. 影依融合："强化后…"字样从敲前文本移到仅强化后显示（{IfUpgraded:show:…|}）
3. 炼狱的乖放：同上
用法: py tools\\update_loc_v0433.py（带旧文校验）
"""
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOC = os.path.join(ROOT, 'mod', 'lightsworn', 'lightsworn', 'localization', 'zhs')

cards_path = os.path.join(LOC, 'cards.json')
cards = json.load(io.open(cards_path, encoding='utf-8'))

updates = {
    'LIGHTSWORN-CELESTIA.description': (
        '弃光{Mill:diff()}。对目标造成{Damage:diff()}点伤害，重复{Hits:diff()}次；'
        '对所有其他敌人造成{Splash:diff()}点伤害。',
        '弃光{Mill:diff()}。对所有敌人造成{Damage:diff()}点伤害，重复{Hits:diff()}次。',
    ),
    'LIGHTSWORN-SHADDOLL_FUSION.description': (
        '影融{IfUpgraded:show:+|}。\n[gold]强化后[/gold]处于精英战或Boss战时，素材也可以从卡组选择（限「影依」牌）。',
        '影融{IfUpgraded:show:+。处于精英战或Boss战时，素材也可以从卡组选择（限「影依」牌）|}。',
    ),
    'LIGHTSWORN-PURGATORY_RELEASE.description': (
        '从抽牌堆将2张类型不同的「影依」牌加入手牌，然后弃置1张手牌。\n[gold]强化后[/gold] 加入手牌的2张牌费用变为0。',
        '从抽牌堆将2张类型不同的「影依」牌加入手牌，然后弃置1张手牌。'
        '{IfUpgraded:show:加入手牌的2张牌费用变为0。|}',
    ),
}

errors = []
for key, (old, new) in updates.items():
    if key not in cards:
        errors.append('缺键 ' + key)
    elif cards[key] != old:
        errors.append('%s 旧文不符：\n  实际=%r\n  期望=%r' % (key, cards[key], old))
    else:
        cards[key] = new

if errors:
    print('!! 校验失败：')
    for e in errors:
        print('  -', e)
    sys.exit(1)

json.dump(cards, io.open(cards_path, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=2)
io.open(cards_path, 'a', encoding='utf-8', newline='').write('\n')
print('OK cards.json 已更新 3 条（天使全体化 / 影依融合+炼狱的乖放 升级文案条件化）')
