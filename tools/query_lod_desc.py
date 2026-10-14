import sqlite3, io

db = r'D:\MyCardLibrary\ygopro\cards.cdb'
con = sqlite3.connect(db)
cur = con.cursor()
row = cur.execute(
    "SELECT t.name, t.desc, d.atk, d.def, d.level, d.type FROM datas d JOIN texts t ON t.id=d.id WHERE t.id=83027236").fetchone()
con.close()
out = io.open(r'D:\1-workdata\lightsworn_mod\tools\lod_desc.txt', 'w', encoding='utf-8')
out.write(f'name: {row[0]}\n ATK {row[2]} / DEF {row[3]} / lv {row[4]} / type {row[5]}\n\ndesc:\n{row[1]}\n')
out.close()
print('done')
