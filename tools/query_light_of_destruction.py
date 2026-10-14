import sqlite3, io, sys

db = r'D:\MyCardLibrary\ygopro\cards.cdb'
con = sqlite3.connect(db)
cur = con.cursor()
out = io.open(r'D:\1-workdata\lightsworn_mod\tools\lod_search.txt', 'w', encoding='utf-8')
for kw in ['破坏之光', '破坏%光', '破壞之光', '光之破坏', '毁灭之光', '破壊']:
    rows = cur.execute(
        "SELECT t.id, t.name FROM texts t WHERE t.name LIKE ? LIMIT 30", (kw,)).fetchall()
    out.write(f'==== {kw} ({len(rows)})\n')
    for r in rows:
        out.write(f'  {r[0]} | {r[1]}\n')
con.close()
print('done')
