# -*- coding: utf-8 -*-
# 查询本地 ygopro cards.cdb 中影依(Shaddoll)系列全部卡
# 输出 tools\shaddoll_query.txt（名字/密码/类型/攻守/描述），stdout 打印摘要
# 并校验 D:\MyCardLibrary\ygopro\pics\<密码>.jpg 卡图是否齐全
import sqlite3, io, os, sys

DB = r'D:\MyCardLibrary\ygopro\cards.cdb'
PIC_DIR = r'D:\MyCardLibrary\ygopro\pics'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'shaddoll_query.txt')

FLAGS = [
    (0x1, '怪兽'), (0x2, '魔法'), (0x4, '陷阱'), (0x10, '通常'), (0x20, '效果'), (0x40, '融合'),
    (0x80, '仪式'), (0x100, '陷阱怪'), (0x200, '灵魂'), (0x400, '同盟'), (0x800, '二重'),
    (0x1000, '调整'), (0x2000, '同调'), (0x4000, '衍生物'), (0x8000, '速攻'), (0x10000, '永续'),
    (0x20000, '反击'), (0x40000, '装备'), (0x80000, '场地'), (0x100000, '反转'),
    (0x200000, '卡通'), (0x400000, '超量'), (0x800000, '灵摆'), (0x1000000, '连接'),
]

def decode_type(t):
    parts = [cn for bit, cn in FLAGS if t & bit]
    return '/'.join(parts) if parts else hex(t)

con = sqlite3.connect(DB)
cur = con.cursor()
patterns = ['%影依%', '%シャドール%', '%Shaddoll%']
seen = {}
for pat in patterns:
    rows = cur.execute(
        "SELECT t.id, t.name, d.type, d.atk, d.def, d.level, d.race, d.attribute, d.setcode, t.desc "
        "FROM texts t JOIN datas d ON d.id=t.id WHERE t.name LIKE ?", (pat,)).fetchall()
    for r in rows:
        seen[r[0]] = r

rows = sorted(seen.values(), key=lambda r: r[0])
print('matched %d cards' % len(rows))

with io.open(OUT, 'w', encoding='utf-8') as out:
    for r in rows:
        cid, name, typ, atk, df, lv, race, attr, setcode, desc = r
        has_pic = os.path.isfile(os.path.join(PIC_DIR, str(cid) + '.jpg'))
        out.write('==== %s | %d | %s | ATK %s / DEF %s | lv %s | setcode %s | pic:%s\n' % (
            name, cid, decode_type(typ), atk, df, lv, hex(setcode), 'Y' if has_pic else 'MISSING'))
        out.write(desc + '\n\n')

missing = [r[1] for r in rows if not os.path.isfile(os.path.join(PIC_DIR, str(r[0]) + '.jpg'))]
print('pics missing for: %s' % (missing if missing else 'none'))
# 打印一行摘要（名字+类型+密码）方便核对张数
for r in rows:
    print('%-24s %-14s %d' % (r[1], decode_type(r[2]), r[0]))
