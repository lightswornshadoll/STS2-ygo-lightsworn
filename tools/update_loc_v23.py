# v0.4.23 批次：问题2/3/4/5/6/7/8/9/10/11 文案同步
# cards.json（露米娜丝x2/太阳交换/神影依9张/犀角龙）+ card_keywords.json（两个融合词条）+ card_selection.json（珠泪素材提示）
import io, json, os, sys

BASE = os.path.join(os.path.dirname(__file__), "..", "mod", "lightsworn", "lightsworn", "localization", "zhs")

def load(name):
    return json.load(io.open(os.path.join(BASE, name), encoding="utf-8"))

def save(name, data):
    with io.open(os.path.join(BASE, name), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

def replace(d, key, old, new):
    assert key in d, f"missing key: {key}"
    assert old in d[key], f"old text not found in {key}: {old!r}"
    d[key] = d[key].replace(old, new)

cards = load("cards.json")
kw = load("card_keywords.json")
sel = load("card_selection.json")

# ---- 问题11：露米娜丝/暮露米娜丝 拿1张+10格挡 ----
replace(cards, "LIGHTSWORN-LUMINA.description",
    "弃光{Mill:diff()}。弃置1张手牌，然后从弃牌堆中将{Picks:diff()}张「光道」牌加入手牌（本回合费用为0）。",
    "弃光{Mill:diff()}。弃置1张手牌，从弃牌堆中将{Picks:diff()}张「光道」牌加入手牌（本回合费用为0），获得{Block:diff()}点格挡。")
replace(cards, "LIGHTSWORN-TWILIGHT_LUMINA.description",
    "将消耗堆中的{Picks:diff()}张「光道」牌加入手牌（费用变为0）。获得{Twilight:diff()}层暮光。",
    "将消耗堆中的{Picks:diff()}张「光道」牌加入手牌（费用变为0），获得{Block:diff()}点格挡。获得{Twilight:diff()}层暮光。")

# ---- 问题10：太阳交换打出条件 ----
replace(cards, "LIGHTSWORN-SOLAR_EXCHANGE.description",
    "将手牌中1张「光道」牌弃置（若有）。",
    "仅当手牌中有「光道」牌时才能打出。\n将手牌中1张「光道」牌弃置（若有）。")

# ---- 问题7/6：融合条件行 ----
replace(cards, "LIGHTSWORN-EL_SHADDOLL_WINDA.description",
    "融合条件：2张影依牌。", "融合条件：1张影依牌+1张影依/珠泪牌。")
replace(cards, "LIGHTSWORN-EL_SHADDOLL_WENDIGO.description",
    "融合条件：1张影依牌+1张技能牌。", "融合条件：1张影依牌+另1张技能牌。")
replace(cards, "LIGHTSWORN-EL_SHADDOLL_GRYSTA.description",
    "融合条件：1张影依牌+1张攻击牌。", "融合条件：1张影依牌+另1张攻击牌。")

# ---- 问题9：犀角龙融合卡位适配神影依 ----
replace(cards, "LIGHTSWORN-DRAGOSTAPELIA.description",
    "融合条件：含融合卡的2张珠泪攻击牌。", "融合条件：1张融合卡+1张珠泪攻击牌（融合卡可为珠泪融合卡或神影依）。")

# ---- 问题4：神影依9张 第2次打出时消耗 ----
tokens = ["EL_SHADDOLL_WINDA", "EL_SHADDOLL_CONSTRUCT", "EL_SHADDOLL_WENDIGO", "EL_SHADDOLL_GRYSTA",
          "EL_SHADDOLL_SHEKHINAGA", "EL_SHADDOLL_ANOYATYLLIS", "EL_SHADDOLL_APKALLONE",
          "EL_SHADDOLL_MESHAHRAIL", "REESHADDOLL_WENDIKURHU"]
for t in tokens:
    key = f"LIGHTSWORN-{t}.description"
    assert key in cards, f"missing key: {key}"
    assert "第2次打出时消耗" not in cards[key], f"already patched: {key}"
    cards[key] = cards[key].rstrip() + "\n第2次打出时消耗。"

# ---- 问题8：珠泪融合词条 + 选牌提示（素材必含触发卡） ----
replace(kw, "LIGHTSWORN-TEARFUSION.description",
    "从弃牌堆选择2~3张珠泪攻击牌放回抽牌堆（融合卡被选做素材时改为消耗）",
    "从弃牌堆选择1~2张其他珠泪攻击牌（触发珠泪融合的卡本身自动作为素材）放回抽牌堆（融合卡被选做素材时改为消耗）")
replace(kw, "LIGHTSWORN-SHADDOLLFUSION.description",
    "（0费，回到卡组时消耗）", "（0费，回到卡组时消耗，第2次打出时也消耗）")
replace(sel, "LIGHTSWORN_TEAR_MATERIAL",
    "珠泪融合：选择2~3张珠泪攻击牌放回抽牌堆",
    "珠泪融合：选择1~2张其他珠泪攻击牌放回抽牌堆（触发卡自动作为素材）")

save("cards.json", cards)
save("card_keywords.json", kw)
save("card_selection.json", sel)
print("OK: cards.json / card_keywords.json / card_selection.json updated")
