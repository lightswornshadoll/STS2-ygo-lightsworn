import json, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

frag = {
    "LIGHTSWORN-JUDGEMENT_DRAGON.title": "裁决之龙",
    "LIGHTSWORN-JUDGEMENT_DRAGON.description": "弃牌堆中存在4种不同「光道」牌时才能打出。\n弃光{Mill:diff()}。对所有敌人造成{Damage:diff()}点伤害。",
    "LIGHTSWORN-MICHAEL.title": "光道主·大天使 米迦勒",
    "LIGHTSWORN-MICHAEL.description": "将弃牌堆中的「光道」牌全部洗回抽牌堆，每洗回1张获得3点格挡。造成{Damage:diff()}点伤害。",
    "LIGHTSWORN-MINERVA_EXALTED.title": "光道雅典娜 密涅瓦",
    "LIGHTSWORN-MINERVA_EXALTED.description": "从卡组选择2张不同名的「光道」牌弃置（不足则有多少弃多少）。然后可选择消耗弃牌堆中至多4张「光道」牌，再弃光相同数量。造成{Damage:diff()}点伤害。",
    "LIGHTSWORN-LUMINA.title": "光道召唤师 露米娜丝",
    "LIGHTSWORN-LUMINA.description": "弃光{Mill:diff()}。弃置1张手牌，然后从弃牌堆中将{Picks:diff()}张「光道」牌加入手牌（本回合费用为0）。",
    "LIGHTSWORN-MINERVA_SAINT.title": "光道圣女 密涅瓦",
    "LIGHTSWORN-MINERVA_SAINT.description": "弃光{Mill:diff()}，每弃置1张「光道」牌抽1张牌。若有敌人意图为攻击：再弃光3，每弃置1张「光道」牌使该敌人获得1层虚弱。",
}

out = r"D:\1-workdata\lightsworn_mod\mod\lightsworn\tools\locfrag\cards_C.json"
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, "w", encoding="utf-8") as f:
    json.dump(frag, f, ensure_ascii=False, indent=2)
    f.write("\n")
print("written:", out)
print(open(out, encoding="utf-8").read())
