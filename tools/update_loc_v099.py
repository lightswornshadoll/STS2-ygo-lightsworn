# 第九轮反馈（v0.5.0）本地化批量更新
# cards.json / powers.json / card_keywords.json / card_selection.json
import io, json, os

BASE = r'D:\1-workdata\lightsworn_mod\mod\lightsworn\lightsworn\localization\zhs'

def load(name):
    with io.open(os.path.join(BASE, name), encoding='utf-8') as f:
        return json.load(f)

def save(name, data):
    with io.open(os.path.join(BASE, name), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')

# ---------- cards.json ----------
cards = load('cards.json')
card_updates = {
    # 问题1：珍妮丝 回血→格挡（上轮已改代码，文本漏改）
    "LIGHTSWORN-JANICE.description":
        "本回合若发动过弃光，回合结束时获得{Amount:diff()}点格挡，并对随机一名敌人造成{Amount:diff()}点伤害。",
    # 问题2：沃尔夫/费莉丝 文本按实际规则重写（从抽牌堆以外的地方加入手牌才能打出）
    "LIGHTSWORN-WULF.description":
        "造成{Damage:diff()}点伤害。\n[gold]从卡组被弃置时[/gold]自动加入手牌。只有从抽牌堆以外的地方加入手牌时，此牌才能打出。",
    "LIGHTSWORN-FELIS.description":
        "弃光{Mill:diff()}。获得{Block:diff()}点格挡。随机一名敌人获得1层易伤。\n[gold]从卡组被弃置时[/gold]自动加入手牌。只有从抽牌堆以外的地方加入手牌时，此牌才能打出。",
    # 问题6+9：丽拉 减敏→1层脆弱，增加消耗
    "LIGHTSWORN-LYLA.description":
        "弃光{Mill:diff()}。目标敌人失去{Debuff:diff()}点力量，获得1层脆弱。消耗。",
    # 问题8：少女获得的龙牌增加消耗
    "LIGHTSWORN-MAIDEN_MINERVA.description":
        "弃光{Mill:diff()}。若弃牌堆中的「光道」种类不少于{Tier1:diff()}种，从已达挡位的龙中选择1条加入手牌（消耗）：「光道之龙」；{Tier2:diff()}种以上：光道龙 格拉古尼斯；{Tier3:diff()}种以上：裁决之龙。\n[gold]从卡组被弃置时[/gold]：弃光1。",
    # 问题6+9：暮丽拉 减敏→1层脆弱，增加消耗
    "LIGHTSWORN-TWILIGHT_LYLA.description":
        "消耗弃牌堆中的1张「光道」牌（若无则此牌不产生任何效果）。使目标敌人失去{Debuff:diff()}点力量，获得1层脆弱，自身获得1层暮光。消耗。",
    # 问题14：暮简 获得1层暮光
    "LIGHTSWORN-TWILIGHT_JAIN.description":
        "消耗弃牌堆中的1张「光道」牌（若有）。造成{Damage:diff()}点伤害，获得1层暮光。",
    # 问题10：米迦勒 每回收1张1格挡
    "LIGHTSWORN-MICHAEL.description":
        "造成{Damage:diff()}点伤害。将弃牌堆中的「光道」牌全部加入抽牌堆，每回收1张获得1点格挡。",
    # 问题4：雅典娜 两处选牌一个界面一次选完（不再限不同名）
    "LIGHTSWORN-MINERVA_EXALTED.description":
        "从卡组选择2张「光道」牌弃置（不足则有多少选多少）。然后可选择消耗弃牌堆中至多4张「光道」牌，再弃光相同数量。造成{Damage:diff()}点伤害。",
    # 问题5本批：圣女两个弃光共用数值，敲后都变4
    "LIGHTSWORN-MINERVA_SAINT.description":
        "弃光{Mill:diff()}，每弃置1张「光道」牌抽1张牌。若有敌人意图为攻击：再弃光{Mill:diff()}，每弃置1张「光道」牌使该敌人获得1层虚弱。",
    # 问题13：暮萨满 拿2张、暮光1层
    "LIGHTSWORN-TWILIGHT_LUMINA.description":
        "消耗弃牌堆中的1张「光道」牌（若有），将消耗堆中的{Picks:diff()}张「光道」牌加入手牌（费用变为0）。获得{Twilight:diff()}层暮光。",
    # 问题17：闪光之幻想重做
    "LIGHTSWORN-FLASH_FANTASY.description":
        "选择弃牌堆中的1张「光道」攻击牌，获得等同于其基础伤害数值的格挡{IfUpgraded:show:（+3）|}，然后弃光{Mill:diff()}。",
}
for k, v in card_updates.items():
    assert k in cards, f'missing cards key: {k}'
    cards[k] = v
save('cards.json', cards)
print(f'cards.json: {len(card_updates)} entries updated')

# ---------- powers.json ----------
powers = load('powers.json')
power_updates = {
    # 问题15：暮光效果重做
    "LIGHTSWORN-TWILIGHT_POWER.description":
        "当你打出「光道」牌时，弃光3，然后层数-1。若抽牌堆的牌不够弃光，消耗2层暮光，将弃牌堆洗回抽牌堆并补完弃光。",
    "LIGHTSWORN-TWILIGHT_POWER.smartDescription":
        "当你打出「光道」牌时，弃光3，然后层数-1。若抽牌堆的牌不够弃光，消耗2层暮光，将弃牌堆洗回抽牌堆并补完弃光。（剩余[blue]{Amount}[/blue]层）",
}
for k, v in power_updates.items():
    assert k in powers, f'missing powers key: {k}'
    powers[k] = v
save('powers.json', powers)
print(f'powers.json: {len(power_updates)} entries updated')

# ---------- card_keywords.json ----------
kw = load('card_keywords.json')
kw["LIGHTSWORN-TWILIGHT.title"] = "暮光"
kw["LIGHTSWORN-TWILIGHT.description"] = (
    "暮光：每打出1张「光道」牌，弃光3并消耗1层暮光。"
    "若抽牌堆的牌不够弃光，消耗2层暮光，将弃牌堆洗回抽牌堆并补完弃光。"
)
save('card_keywords.json', kw)
print('card_keywords.json: TWILIGHT entry added')

# ---------- card_selection.json ----------
sel = load('card_selection.json')
sel["LIGHTSWORN_FLASH_PICK"] = "选择1张「光道」攻击牌（弃牌堆）"
save('card_selection.json', sel)
print('card_selection.json: FLASH_PICK entry added')
