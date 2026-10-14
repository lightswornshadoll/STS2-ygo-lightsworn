# -*- coding: utf-8 -*-
# 影依第二轮查询：
# 1) 按 passcode 精确取 ygoprodeck 卡表里本地 cdb 缺的 11 张（CN名/效果）
# 2) name LIKE '%影依%' OR desc LIKE '%影依%' 全量（验证用户的"38张"口径）
import sqlite3, io, os

DB = r'D:\MyCardLibrary\ygopro\cards.cdb'
PIC_DIR = r'D:\MyCardLibrary\ygopro\pics'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'shaddoll_query2.txt')

API_IDS = [81788994, 19261966, 50907446, 20366274, 6417578, 48424886, 32467459, 74822425,
           74009824, 94977269, 92079625, 97518132, 66675911, 60226558, 78942513, 24635329,
           51023024, 8852158, 23912837, 3717252, 86938484, 4904633, 77723643, 37445295,
           44394295, 4939890, 52551211, 21011044, 30328508, 95401059, 58016954,
           77505534, 95072744]

con = sqlite3.connect(DB)
cur = con.cursor()

def fmt(r):
    cid, name, typ, atk, df, lv, desc = r
    has = 'Y' if os.path.isfile(os.path.join(PIC_DIR, str(cid) + '.jpg')) else 'MISSING'
    return '==== %s | %d | type %s | ATK %s / DEF %s | lv %s | pic:%s\n%s\n' % (
        name, cid, typ, atk, df, lv, has, desc)

with io.open(OUT, 'w', encoding='utf-8') as out:
    out.write('########## A. 按 passcode 精确查 API 卡表 33 张 ##########\n')
    for cid in API_IDS:
        r = cur.execute(
            "SELECT t.id, t.name, d.type, d.atk, d.def, d.level, t.desc "
            "FROM texts t JOIN datas d ON d.id=t.id WHERE t.id=?", (cid,)).fetchone()
        out.write(fmt(r) if r else '==== %d | 本地cdb无此卡\n\n' % cid)

    out.write('########## B. name或desc含影依 全量 ##########\n')
    rows = cur.execute(
        "SELECT t.id, t.name, d.type, d.atk, d.def, d.level, t.desc "
        "FROM texts t JOIN datas d ON d.id=t.id "
        "WHERE t.name LIKE ? OR t.desc LIKE ? ORDER BY t.id",
        ('%影依%', '%影依%')).fetchall()
    name_only = cur.execute(
        "SELECT COUNT(*) FROM texts WHERE name LIKE ?", ('%影依%',)).fetchone()[0]
    out.write('## name命中 %d 张；name+desc命中 %d 张\n\n' % (name_only, len(rows)))
    for r in rows:
        out.write(fmt(r))

print('A done; B name+desc total =', len(rows), '; name only =', name_only)
