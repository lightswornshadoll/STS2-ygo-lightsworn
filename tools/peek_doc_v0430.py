import io, os
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
t = io.open(os.path.join(root, 'design', '卡牌图鉴.md'), encoding='utf-8').read()
for name in ['剑神官 姆多拉', '宿神像 凯尔多', '古尖兵 凯尔柏克', '古卫兵 阿基多', '光道贼猫 雷喵',
             '正义世界', '珍珠世界', '神光之龙', '神影依融合', '影依的炎核 虚梦狱', '影依·拿非利',
             '虚影依 神子晶', '光道召唤师 露米娜丝', '光道主·大天使 米迦勒']:
    i = t.find(name)
    seg = t[i:i + 560] if i >= 0 else '(未找到)'
    parts = [x.strip() for x in seg.split('\n')[1:6] if x.strip()]
    print('==', name, '=>', ' | '.join(parts)[:430])
