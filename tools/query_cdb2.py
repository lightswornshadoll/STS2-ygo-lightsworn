import sqlite3, io, sys

db = r'D:\MyCardLibrary\ygopro\cards.cdb'
con = sqlite3.connect(db)
cur = con.cursor()
names = ['真血公', '手札抹杀', '愚蠢的埋葬', '塞壬人鱼', '小美人鱼', '梅洛人鱼', '雷诺哈特',
         '珍珠世界', '水仙女人鱼', '鲁莎卡人鱼', '卡雷多哈特', '犀角龙', '捕食植物']
out = io.open(r'D:\1-workdata\lightsworn_mod\tools\tear_query.txt', 'w', encoding='utf-8')
for n in names:
    rows = cur.execute(
        "SELECT t.id, t.name, d.atk, d.def, d.level FROM datas d JOIN texts t ON t.id=d.id "
        "WHERE t.name LIKE ? LIMIT 12", ('%' + n + '%',)).fetchall()
    out.write(f'==== {n}\n')
    for r in rows:
        out.write(f'  {r[0]} | {r[1]} | ATK {r[2]} / DEF {r[3]} | lv {r[4]}\n')
    if not rows:
        out.write('  (not found)\n')
out.close()
print('done')
