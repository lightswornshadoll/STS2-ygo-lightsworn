import io, sys, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
base = r'D:\1-workdata\lightsworn_mod\mod\lightsworn\lightsworn\localization\zhs'

def load(name):
    return json.load(open(os.path.join(base, name), encoding='utf-8'))

def save(name, data):
    with open(os.path.join(base, name), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ---- card_keywords.json：珠泪融合词条（素材扩到影依牌，米德拉什可产出） ----
kw = load('card_keywords.json')
k = 'LIGHTSWORN-TEARFUSION.description'
old = kw[k]
assert '其他珠泪攻击牌' in old, '旧文案不匹配: ' + old
kw[k] = ('珠泪融合：拥有此效果的卡被弃置时发动——从弃牌堆选择1~2张其他珠泪攻击牌或影依牌'
         '（触发珠泪融合的卡本身自动作为素材）放回抽牌堆（融合卡被选做素材时改为消耗），'
         '然后从满足融合条件的融合卡中选择1张加入手牌（触发卡已升级则融合出强化版）。'
         '同一回合每张融合卡只能生成1次；融合卡回到卡组（抽牌堆）时消耗，被效果直接加入手牌则保留。'
         '素材数量须与融合条件严格一致，各融合卡的条件见其卡面说明。')
save('card_keywords.json', kw)
print('card_keywords.json: TEARFUSION 词条已更新')

# ---- card_selection.json：素材选择提示 ----
cs = load('card_selection.json')
k = 'LIGHTSWORN_TEAR_MATERIAL'
assert '珠泪攻击牌' in cs[k], '旧文案不匹配: ' + cs[k]
cs[k] = '珠泪融合：选择1~2张其他珠泪攻击牌或影依牌放回抽牌堆（触发卡自动作为素材）'
save('card_selection.json', cs)
print('card_selection.json: TEAR_MATERIAL 提示已更新')
