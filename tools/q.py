import sqlite3, io, sys

db = r'D:\MyCardLibrary\ygopro\cards.cdb'
con = sqlite3.connect(db)
cur = con.cursor()
kw = sys.argv[1] if len(sys.argv) > 1 else '神光之龙'
rows = cur.execute(
    "SELECT t.id, t.name, d.atk, d.def, d.level, t.desc FROM datas d JOIN texts t ON t.id=d.id "
    "WHERE t.name LIKE ? LIMIT 20", ('%' + kw + '%',)).fetchall()
for r in rows:
    print(f'{r[0]} | {r[1]} | ATK {r[2]} / DEF {r[3]} | lv {r[4]}')
    print('   ' + (r[5] or '')[:80].replace('\n', ' '))
if not rows:
    print('(not found)')
