import io

p = r'D:\1-workdata\lightsworn_mod\tools\gen_card_doc.py'
t = io.open(p, encoding='utf-8').read()

# 1. 文件范围 1-5 -> 1-8
old = '    for i in (1, 2, 3, 4, 5):'
assert t.count(old) == 1
t = t.replace(old, '    for i in (1, 2, 3, 4, 5, 6, 7, 8):')

# 2. 基类正则加 ShaddollCard/ShaddollToken
old_line = [l for l in t.splitlines() if 'matches = list(re.finditer' in l]
assert len(old_line) == 1, old_line
old_line = old_line[0]
new_line = old_line.replace('TearFusionToken', 'TearFusionToken|ShaddollCard|ShaddollToken')
assert new_line != old_line, old_line
t = t.replace(old_line, new_line)

# 3. VAR_LABEL 补新变量
old = '    "Times": "翻倍次数", "Vigor": "活力", "Thorns": "荆棘",'
assert t.count(old) == 1
t = t.replace(old, '    "Times": "翻倍次数", "Vigor": "活力", "Thorns": "荆棘",\n'
                   '    "Next": "触发张数", "Gain": "活力倍率", "Recall": "回手门槛", "Pick": "生成张数",\n'
                   '    "Buffer": "缓冲层数",')

# 4. SPECIAL 补神影依 Token 备注（追加到 Dragostapelia 条目后）
old = '    "Dragostapelia": {"note": "Token：珠泪融合生成，离开弃牌堆时消耗；不含珠泪字段"},\n}'
assert t.count(old) == 1
new = '''    "Dragostapelia": {"note": "Token：珠泪融合生成，离开弃牌堆时消耗；不含珠泪字段"},
    "ElShaddollWinda": {"note": "神影依Token：影融生成，打出后消耗；每回合每张限生成1次"},
    "ElShaddollConstruct": {"note": "神影依Token：影融生成（素材要1影依+1光道），打出后消耗；每回合每张限生成1次"},
    "ElShaddollWendigo": {"note": "神影依Token：影融生成，打出后消耗；本场战斗限生成1次"},
    "ElShaddollGrysta": {"note": "神影依Token：影融生成，打出后消耗；每回合每张限生成1次"},
    "ElShaddollShekhinaga": {"note": "神影依Token：影融生成，打出后消耗；每回合每张限生成1次"},
    "ElShaddollAnoyatyllis": {"note": "神影依Token：影融生成（3张影依素材），打出后消耗；每回合每张限生成1次"},
    "ElShaddollApkallone": {"note": "神影依Token：影融生成（2张不同名影依），打出后消耗；每回合每张限生成1次"},
    "ElShaddollMeshahrail": {"note": "神影依Token：影融生成（3张手牌素材），打出后消耗；每回合每张限生成1次"},
    "ReeshaddollWendikurhu": {"note": "神影依Token：影融生成（2张影依技能素材），打出后消耗；每回合每张限生成1次"},
    "ShaddollFusion": {"note": "强化后素材也可以从卡组选择"},
    "ElShaddollFusion": {"note": "生成的神影依视为已升级"},
    "NepheShaddollFusion": {"note": "强化后移除消耗"},
    "FrozenHeartShadow": {"note": "生成的神影依伤害为0；强化后选2张"},
    "SinisterShadowGames": {"note": "能力：影依牌被弃置时触发2次；强化后1费"},
    "CurseShadowPrison": {"note": "能力：每次影依牌被弃置+1镀层；强化后固有"},
}'''
t = t.replace(old, new)

io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('gen_card_doc.py patched OK')
