import sqlite3

db = r'D:\MyCardLibrary\ygopro\cards.cdb'
con = sqlite3.connect(db)
cur = con.cursor()
for row in cur.execute("select t.id,t.name,d.type,d.atk,d.def,t.desc from texts t left join datas d on d.id=t.id where t.name like '%暗黑界%' order by t.id"):
    print(row[0], '|', row[1], '| type', row[2], '|', row[3], '/', row[4])
    print('   ', (row[5] or '').replace('\n', ' ')[:300])
