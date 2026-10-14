import io, re, os
p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'design', '卡牌图鉴.md')
t = io.open(p, encoding='utf-8').read()
checks = [
    ('珠泪哀歌族 塞壬人鱼', '改名'),
    ('珠泪哀歌族 卡雷多哈特', '改名'),
    ('含「珠泪哀歌族 雷诺哈特」', '交叉引用'),
    ('神光回响', '新能力'),
    ('额外造成5点伤害', '神光之龙'),
    ('获得2点格挡', '米迦勒'),
    ('将弃牌堆中最多{Picks:diff()}张牌洗回抽牌堆，抽1张牌；若抽到的是攻击牌', '姆多拉渲染'),
    ('重放', '神影依融合'),
    ('圣影依 商神杖灵」可充当光道牌', '拿非利条件'),
    ('仅在融合「神影依·拿非利」时可作为「光道」牌使用', '圣影依'),
    ('发动影融——从弃牌堆选2张', '虚影依'),
    ('{Vigor:diff()}', '正义世界渲染'),
    ('{Vul:diff()}层易伤', '珍珠世界渲染'),
    ('{Picks:diff()}张「光道」牌洗回抽牌堆', '雷喵渲染'),
    ('对随机敌人造成{Damage:diff()}点伤害', '凯尔柏克渲染'),
    ('若其中有2张以上技能牌', '阿基多'),
    ('获得8点格挡', '救影依'),
    ('限「影依」牌', '影依融合'),
]
for s, tag in checks:
    print(('OK  ' if s in t else 'MISS'), tag, s)
# 渲染完整性：不应再有裸 {Var:diff()} 之外的未知变量残留警告——统计 MUDORA/KELDO/RINYAN 段
for name in ['剑神官 姆多拉', '宿神像 凯尔多', '光道贼猫 雷喵', '正义世界', '珍珠世界']:
    i = t.find('## ' + name)
    if i < 0: i = t.find(name)
    seg = t[i:i+700] if i >= 0 else '(未找到)'
    print('----', name, '=>', seg.split('\n')[1][:120] if '\n' in seg else seg[:120])
