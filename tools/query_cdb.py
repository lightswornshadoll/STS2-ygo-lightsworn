import sqlite3, io, sys

db = r'D:\MyCardLibrary\ygopro\cards.cdb'
con = sqlite3.connect(db)
cur = con.cursor()
names = ['费莉丝', '艾琳', '沃尔夫', '雷光', '格拉古尼斯', '姆多拉', '基路伯', '米迦勒',
         '基里奥斯', '简', '莱登', '凯尔柏克', '阿基多', '凯尔多', '夏尔', '魏丝',
         '落泪之日', '裁决之龙', '惩戒之龙', '欧尼斯特', '丽拉', '珍妮丝', '露米娜丝',
         '密涅瓦', '奥库斯', '雷喵', '锻冶师', '怜歌', '咏圣', '镇魂棺', '割草']
out = io.open(r'D:\1-workdata\lightsworn_mod\tools\atkdef.txt', 'w', encoding='utf-8')
for n in names:
    rows = cur.execute(
        "SELECT t.name, d.atk, d.def, d.level FROM datas d JOIN texts t ON t.id=d.id "
        "WHERE t.name LIKE ? LIMIT 6", ('%' + n + '%',)).fetchall()
    out.write(f'==== {n}\n')
    for r in rows:
        out.write(f'  {r[0]} | ATK {r[1]} / DEF {r[2]} | lv {r[3]}\n')
    if not rows:
        out.write('  (not found)\n')
out.close()
print('done')
