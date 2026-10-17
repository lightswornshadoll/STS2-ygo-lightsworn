# -*- coding: utf-8 -*-
"""生成《光道》mod 卡牌图鉴（design\卡牌图鉴.md）。

数据源：
  1. mod\lightsworn\Scripts\Cards1-4.cs —— 费用/类型/稀有度/动态变量基础值/OnUpgrade 增量
  2. mod\lightsworn\lightsworn\localization\zhs\cards.json —— 中文名与描述文本（{Var:diff()} 占位符）
改卡后重跑本脚本即可重新生成图鉴（python tools\gen_card_doc.py）。

约12张卡的升级逻辑是内联代码（IsUpgraded ? x : y，不走 UpgradeValueBy），由 SPECIAL 表手工覆盖。
"""
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "mod" / "lightsworn" / "Scripts"
LOC = ROOT / "mod" / "lightsworn" / "lightsworn" / "localization" / "zhs"
OUT = ROOT / "design" / "卡牌图鉴.md"

VAR_LABEL = {
    "Damage": "伤害", "Block": "格挡", "Cards": "抽牌数", "Mill": "弃光",
    "Banish": "除光", "Strip": "移除增益数", "Debuff": "力量/敏捷降低",
    "Splash": "溅射伤害", "Scale": "每张额外值", "Dump": "选择弃置数",
    "Amount": "数值", "Back": "置顶张数", "Tier1": "挡位1", "Tier2": "挡位2",
    "Tier3": "挡位3", "Picks": "拿取数", "Take": "拿取数", "Weak": "虚弱",
    "Bonus": "额外加成", "BlockGain": "格挡", "Doom": "灾厄", "Twilight": "暮光",
    "BlockPerBurn": "每张格挡", "MaxBurn": "最多消耗数", "SabrePower": "力量",
    "Times": "翻倍次数", "Vigor": "活力", "Thorns": "荆棘",
    "Next": "触发张数", "Gain": "活力倍率", "Recall": "回手门槛", "Pick": "生成张数",
    "Buffer": "缓冲层数", "Hits": "攻击次数", "Vul": "易伤",
    "Max": "最多消耗数", "Artifact": "人工制品", "Guard": "格挡", "Temp": "临时力量",
    # 完美打击范式（CalculatedDamage/CalculatedBlock）
    "CalculationBase": "基础值", "ExtraDamage": "每张加成", "CalculationExtra": "每张加成",
    "CalculatedDamage": "动态伤害", "CalculatedBlock": "动态格挡",
}
RARITY = {"Basic": "初始", "Common": "普通", "Uncommon": "非普通", "Rare": "稀有", "Ancient": "先古", "Token": "特殊"}
TYPE = {"Attack": "攻击", "Skill": "技能", "Power": "能力"}
TARGET = {"Self": "自身", "AnyEnemy": "单体", "AllEnemies": "全体"}

# 内联升级逻辑 / 特殊卡的覆盖表（依据 Cards1-4.cs 逐张核对，2026-10-05 v0.4.3）
# base/up：基础与强化的展示文本；delta：并入自动解析的变量增量；note：追加到"升级变化"
SPECIAL = {
    "Gragonith": {
        "note": "卡面数值动态显示；实际伤害在本次弃光后结算，可能高于手牌预览",
        "delta": {"CalculatedDamage": 4},
    },
    "Shire": {
        "note": "卡面数值动态显示（基础值 + 弃牌堆每张「光道」×1）",
        "delta": {"CalculatedBlock": 2},
    },
    "Garoth": {
        "base": "每当「光道」牌弃光后，追加弃光2。",
        "up": "每当「光道」牌弃光后，追加弃光2，并抽其中「光道」牌数量的牌。",
        "note": "强化后：追加弃光后按其中「光道」牌数量抽牌（初版效果回调，任意弃光触发已作废）",
    },
    "Decree": {
        "base": "打出后，将此牌置于抽牌堆顶。\n[gold]从卡组被弃置时[/gold]：将1张消耗的「裁决之龙」加入手牌。",
        "up": "打出后，将此牌置于抽牌堆顶。\n[gold]从卡组被弃置时[/gold]：将1张消耗的「裁决之龙+」加入手牌。",
        "note": "被弃置时生成的裁决之龙Token只带消耗（v0.6.1 去掉保留）；强化后Token已升级（裁决之龙+自带「保留」）",
    },
    "DarkMarch": {
        "base": "将弃牌堆中1张「光道」牌加入手牌。除光2。",
        "up": "将弃牌堆中1张「光道」牌加入手牌（其费用变为0）。除光2。",
        "note": "检索的牌费用临时变为0",
    },
    "TwilightRyko": {
        "base": "消耗弃牌堆中的1张「光道」牌（若有）。移除目标敌人的1个随机增益，获得1层暮光。",
        "up": "消耗弃牌堆中的1张「光道」牌（若有）。移除目标敌人的1个随机增益，获得1层暮光。",
    },
    "TwilightErasure": {
        "base": "消耗弃牌堆中最多2张「光道」牌，每消耗1张移除目标敌人1个随机增益。\n[gold]从卡组被弃置时[/gold]手牌中随机1张「光道」牌本回合费用变为0。",
        "up": "消耗弃牌堆中最多2张「光道」牌，每消耗1张移除目标敌人1个随机增益。\n[gold]从卡组被弃置时[/gold]手牌中随机2张「光道」牌本回合费用变为0。",
        "note": "被弃置联动：0费光道牌 1→2张",
    },
    "TwinTwilightDragon": {
        "base": "若手牌中有「惩戒之龙」：将弃牌堆中1张「裁决之龙」加入手牌，然后弃光4。\n否则：将1张「裁决之龙」和1张「惩戒之龙」置入弃牌堆。\n[gold]从卡组被弃置时[/gold]将弃牌堆中1张「惩戒之龙」加入手牌（没有则无事发生），然后除光4。",
        "up": "若手牌中有「惩戒之龙」：将弃牌堆中1张「裁决之龙」加入手牌，然后弃光4。\n否则：将1张「裁决之龙+」和1张「惩戒之龙+」置入弃牌堆。\n[gold]从卡组被弃置时[/gold]将弃牌堆中1张「惩戒之龙」加入手牌（没有则无事发生），然后除光4。",
        "note": "生成的裁决/惩戒去掉虚无；强化后改为生成「裁决之龙+ / 惩戒之龙+」（自带「保留」；除光固定4）",
    },
    "LawnMowing": {
        "base": "弃光抽牌堆牌数的一半（向下取整）。",
        "up": "弃光抽牌堆牌数的一半（向下取整），然后抽1张牌。",
        "note": "强化后追加抽1张牌",
    },
    "HandDestruction": {
        "note": "强化后移除「消耗」",
    },
    "FoolishBurial": {
        "note": "强化后移除「消耗」",
    },
    "Suliek": {"note": "强化后：珠泪融合产出强化版融合卡"},
    "Merrli": {"note": "意图为攻击时触发特效；强化后：伤害+3，珠泪融合产出强化版融合卡"},
    "Havnis": {"note": "强化后：珠泪融合产出强化版融合卡"},
    "Reinohart": {"note": "不含「珠泪融合」；卡雷多哈特的融合素材"},
    "Kitkallos": {"note": "Token：珠泪融合生成，离开弃牌堆时消耗"},
    "Rulkallos": {"note": "Token：珠泪融合生成，离开弃牌堆时消耗；格挡固定5"},
    "KaleidoHeart": {"note": "Token：珠泪融合生成，离开弃牌堆时消耗；带「消耗」，在消耗区时每回合开始自动打出；本场战斗限生成1次"},
    "Dragostapelia": {"note": "Token：珠泪融合生成，离开弃牌堆时消耗；不含珠泪字段"},
    "ElShaddollWinda": {"note": "神影依Token：影融生成，离开弃牌堆时消耗；每回合每张限生成1次"},
    "ElShaddollConstruct": {"note": "神影依Token：影融生成（素材要1影依+1光道，圣影依可代光道位），离开弃牌堆时消耗；对Boss伤害翻倍；每回合每张限生成1次"},
    "ElShaddollWendigo": {"note": "神影依Token：影融生成，离开弃牌堆时消耗；本场战斗限生成1次"},
    "ElShaddollGrysta": {"note": "神影依Token：影融生成，离开弃牌堆时消耗；每回合每张限生成1次"},
    "ElShaddollShekhinaga": {"note": "神影依Token：影融生成，离开弃牌堆时消耗；每回合每张限生成1次"},
    "ElShaddollAnoyatyllis": {"note": "神影依Token：影融生成（3张影依素材），离开弃牌堆时消耗；每回合每张限生成1次"},
    "ElShaddollApkallone": {"note": "神影依Token：影融生成（2张不同名影依），离开弃牌堆时消耗；每回合每张限生成1次"},
    "ElShaddollMeshahrail": {"note": "神影依Token：影融生成（3张手牌素材，从卡组选的素材不能凑数），离开弃牌堆时消耗；每回合每张限生成1次"},
    "ReeshaddollWendikurhu": {"note": "神影依Token：影融生成（2张影依技能素材），离开弃牌堆时消耗；每回合每张限生成1次"},
    "ShaddollFusion": {"note": "强化后：处于精英战或Boss战时素材也可以从卡组选择（限「影依」牌）"},
    "ElShaddollFusion": {"note": "生成的神影依获得1次重放；强化后不减费（升级=影融+，产出强化版）"},
    "NepheShaddollFusion": {"note": "强化后移除消耗"},
    "FrozenHeartShadow": {"note": "生成的神影依伤害置0；强化后0费（选牌数不变）"},
    "SinisterShadowGames": {"note": "能力：影依牌被弃置时触发2次；强化后1费"},
    "CurseShadowPrison": {"note": "能力：每次影依牌被弃置+1镀层；强化后固有"},
    "TohushaddollGrysta": {"note": "影融在被弃置时发动（弃光/手牌弃置均触发）；升级=影融+（产出强化版；伤害8不变）"},
    "PurgatoryRelease": {"note": "强化后加入手牌的2张牌费用变为0"},
    "ShaddollCore": {"note": "作为影融素材时本次影融可融合任意神影依；强化=影融+（素材为强化版原核时产出强化版神影依）"},
    "ShaddollSchism": {"note": "能力：每回合开始时可以消耗弃牌堆2张影依发动一次影融（可不发动）；强化=影融+（产出强化版神影依）、费用保持1费"},
    "ReshShaddollIncarnation": {"note": "强化后加入手牌的影依卡费用变为0"},
    "QadshaddollKeios": {"note": "素材时充当拿非利融合的光道位；强化后=影融+（产出强化版拿非利）"},
    "Rinyan": {"note": "洗回上限固定3张（原升级+1改为基础效果）；基础带「消耗」，强化后移除「消耗」"},
    "MaidenMinerva": {"note": "强化后：被从卡组弃置时追加抽1张牌（挡位不再降低）"},
    "ShiningDragon": {"note": "伤害不变（仍30×3）"},
    "SnowSpirit": {"note": "衍生Token（金卡展示）：弃牌堆≥7张才能打出"},
    "Perlereino": {"note": "不含珠泪哀歌族标签"},
    "PrimevalCry": {"note": "不含珠泪哀歌族标签（不计「打出珠泪卡」）；被弃置时从卡组拿1张珠泪攻击牌；强化后易伤+1"},
    "PrimevalEcho": {"note": "不含珠泪哀歌族标签；击晕=原版先古卡「吹哨」的眩晕效果；被弃置时从消耗堆复制1张珠泪攻击牌（升级状态保留；拿回的是融合卡时本回合不能再融合出对应怪）"},
    "PrimevalScream": {"note": "不含珠泪哀歌族标签；能力来源弃光（不触发光道的连锁）；强化后获得固有（弃光不变）"},
    "PurushaddollAeon": {"note": "能力：回合开始可从消耗堆拿1张影依（0~1可选）；强化后1费"},
    "JusticeWorld": {"note": "能力：每次弃光可将其中一张加入手牌（0~1可选）；强化后自己获得「保留」"},
    "TwilightGarb": {"note": "强化后移除「消耗」"},
    "Aegis": {"note": "先古牌：古老牙齿把初始牌「光道防护罩」转化为此牌（BaseLib ITranscendenceCard）；被弃置（弃光/手牌弃置）时自动回手且本回合0费"},
    "ShaddollZefracore": {"note": "能力：回合开始随机生成「影依的炎核 虚梦狱」「虚影依 神子晶」「神影依·神子晶」之一（获得「消耗」；神影依占用融合生成次数）"},
    "ShaddollZefranaga": {"note": "能力：回合开始随机生成「圣影依 商神杖灵」「联结之影依化身」「影依的伪典」之一（获得「消耗」）"},
}


def parse_cards():
    """解析 Cards1-5.cs，返回按文件顺序的卡牌信息列表。"""
    cards = []
    for i in (1, 2, 3, 4, 5, 6, 7, 8):
        src = (SCRIPTS / f"Cards{i}.cs").read_text(encoding="utf-8")
        matches = list(re.finditer(r"public (?:sealed )?class (\w+) : (?:LsCard|TearFusionCard|TearFusionToken|ShaddollCard|ShaddollToken)", src))
        for idx, m in enumerate(matches):
            name = m.group(1)
            body = src[m.start(): matches[idx + 1].start() if idx + 1 < len(matches) else len(src)]
            ctor = re.search(r": base\((\d+), CardType\.(\w+), CardRarity\.(\w+), TargetType\.(\w+)", body)
            cost, ctype, rarity, target = int(ctor.group(1)), ctor.group(2), ctor.group(3), ctor.group(4)

            vars_ = {}  # var名 -> 基础值
            for vm in re.finditer(
                r'new (DamageVar|BlockVar|CardsVar|DynamicVar|PowerVar<\w+>|CalculationBaseVar|CalculationExtraVar|ExtraDamageVar)\(("(\w+)", )?(\d+)m?[^)]*\)', body
            ):
                kind, explicit, val = vm.group(1), vm.group(3), int(vm.group(4))
                vname = None
                if kind == "DynamicVar":
                    vname = explicit
                elif kind.startswith("PowerVar"):
                    vname = kind[9:-1]  # PowerVar<SabrePower> -> SabrePower
                else:
                    vname = kind.replace("Var", "")  # Damage/Block/Cards/CalculationBase/CalculationExtra/ExtraDamage
                vars_[vname] = val
            # CalculatedDamage/CalculatedBlock 自身无数值，展示基数=CalculationBase（动态部分由 Extra 表示）
            for cm in re.finditer(r'new (CalculatedDamageVar|CalculatedBlockVar)\(', body):
                vname = "CalculatedDamage" if cm.group(1) == "CalculatedDamageVar" else "CalculatedBlock"
                vars_[vname] = vars_.get("CalculationBase", 0)

            deltas, cost_delta = {}, 0
            up = re.search(r"protected override void OnUpgrade\(\)\s*=>\s*([^;]+);", body)
            if up:
                up_text = up.group(1)
            else:
                up = re.search(r"protected override void OnUpgrade\(\)\s*\{(.*?)\n    \}", body, re.S)
                up_text = up.group(1) if up else ""
            for dm in re.finditer(r'DynamicVars(?:\.(\w+)|\["(\w+)"\])\.UpgradeValueBy\((-?\d+)\)', up_text):
                deltas[dm.group(1) or dm.group(2)] = int(dm.group(3))
            for cm in re.finditer(r"EnergyCost\.UpgradeBy\((-?\d+)\)", up_text):
                cost_delta = int(cm.group(1))
            for km in re.finditer(r"AddKeyword\(CardKeyword\.(\w+)\)", up_text):
                deltas[f"kw:{km.group(1)}"] = 1

            kw_src = re.search(r"CanonicalKeywords => \[(.*?)\]", body, re.S)
            kw_text = kw_src.group(1) if kw_src else ""
            keywords = re.findall(r"CardKeyword\.(\w+)|LsKeywords\.(Mill|Banish)", kw_text)
            kws = sorted({a or b for a, b in keywords})
            tags = []
            tm = re.search(r"CanonicalTags => \[(.*?)\]", body, re.S)
            if tm:
                tags = re.findall(r"CardTag\.(\w+)|Ls\.(\w+)", tm.group(1))
                tags = [a or b for a, b in tags]

            cards.append(dict(cls=name, cost=cost, type=ctype, rarity=rarity, target=target,
                              vars=vars_, deltas=deltas, cost_delta=cost_delta, kws=kws, tags=tags,
                              special=bool(SPECIAL.get(name))))
    return cards


def render(desc, vals, upgraded=False):
    # {IfUpgraded:show:A|B} → 强化版取A、基础版取B（B缺省=空，同 CASCADE/DARKNESS 原版用法）
    desc = re.sub(r"\{IfUpgraded:show:([^{}]*?)(?:\|([^{}]*?))?\}",
                  lambda m: m.group(1) if upgraded else (m.group(2) or ""), desc)
    return re.sub(r"\{(\w+)(?::diff\(\))?\}", lambda m: str(vals.get(m.group(1), m.group(1))), desc)


def change_line(card, vals, up_vals):
    sp = SPECIAL.get(card["cls"], {})
    deltas = {**card["deltas"], **sp.get("delta", {})}
    kw_deltas = {k: v for k, v in deltas.items() if k.startswith("kw:")}
    # CalculatedDamage/CalculatedBlock 只是 CalculationBase 的动态镜像，升级增量已在"基础值"里展示
    deltas = {k: v for k, v in deltas.items()
              if not k.startswith("kw:") and k not in ("CalculatedDamage", "CalculatedBlock")}
    parts = []
    if card["cost_delta"]:
        parts.append(f"费用 {card['cost']}→{card['cost'] + card['cost_delta']}")
    for vn, d in deltas.items():
        parts.append(f"{VAR_LABEL.get(vn, vn)} {vals[vn]}→{up_vals[vn]}")
    if kw_deltas:
        kw_names = {"Exhaust": "消耗", "Innate": "固有", "Ethereal": "虚无", "Retain": "保留"}
        parts.append("获得关键词：" + "、".join(f"「{kw_names.get(k[3:], k[3:])}」" for k in kw_deltas))
    if sp.get("note"):
        parts.append(sp["note"])
    return "；".join(parts) if parts else "无变化"


def main():
    loc = json.loads((LOC / "cards.json").read_text(encoding="utf-8"))
    mod_json = json.loads((ROOT / "mod" / "lightsworn" / "Lightsworn.json").read_text(encoding="utf-8"))
    cards = parse_cards()

    for c in cards:  # 校验：每张卡都有本地化，每个描述里的变量都有值
        # v0.5.0 RitsuLib 迁移：固定条目=MOD_CATEGORY_TYPENAME（卡=LIGHTSWORN_CARD_）
        key = "LIGHTSWORN_CARD_" + re.sub(r"(?<!^)(?=[A-Z])", "_", c["cls"]).upper()
        c["id"], c["title"], c["desc"] = key, loc.get(key + ".title"), loc.get(key + ".description")
        assert c["title"] and c["desc"], f"{c['cls']}: 缺本地化 {key}"
        sp = SPECIAL.get(c["cls"], {})
        c["vals"] = dict(c["vars"])
        c["up_vals"] = {k: v + {**c["deltas"], **sp.get("delta", {})}.get(k, 0) for k, v in c["vars"].items()}
        missing = set(re.findall(r"\{(\w+)(?::diff\(\))?\}", c["desc"])) - set(c["vals"])
        assert not missing, f"{c['cls']}: 描述含未定义变量 {missing}"

    groups = {}
    for c in cards:
        groups.setdefault(c["rarity"], []).append(c)

    lines = [
        "# 《光道 Lightsworn》卡牌图鉴",
        "",
        f"> 自动生成于 tools\\gen_card_doc.py（mod v{mod_json.get('version', '?')}，{date.today().isoformat()}）。"
        "改卡后重跑 `py tools\\gen_card_doc.py` 即可更新。",
        "> 「敲后」= 强化（升级）后。**弃光**=从抽牌堆顶弃N张到弃牌堆；**除光**=从抽牌堆顶消耗N张（本场战斗移除）；",
        "> **暮光**=打出「光道」牌时弃光3然后层数-1；**光道牌**=中文名含「光道」的卡（地天使与裁决之龙/惩戒之龙等不带此标）。",
        "",
        f"共 {len(cards)} 张（含1张衍生Token「雪之化身」，不进卡池/图鉴）：初始 {len(groups.get('Basic', []))}、"
        f"普通 {len(groups.get('Common', []))}、非普通 {len(groups.get('Uncommon', []))}、"
        f"稀有 {len(groups.get('Rare', []))}、先古 {len(groups.get('Ancient', []))}、特殊 {len(groups.get('Token', []))}。"
        "先古牌=达弗「布满灰尘的古卷」赠送（自带升级），不进战斗奖励/商店。",
        "",
    ]

    for rarity in ("Basic", "Common", "Uncommon", "Rare", "Ancient", "Token"):
        group = groups.get(rarity, [])
        if not group:
            continue
        lines += [f"## {RARITY[rarity]}（{len(group)}张）", ""]
        if rarity == "Token":
            lines += ["*衍生Token，不会出现在卡组/奖励中。*", ""]
        if rarity == "Ancient":
            lines += ["*先古稀有度：仅达弗的「布满灰尘的古卷」赠送（获得时已升级1次），不会出现在战斗奖励/商店/卡组生成中。*", ""]
        for c in group:
            sp = SPECIAL.get(c["cls"], {})
            cost_note = f"{c['cost']}费" + (f"（敲后{c['cost'] + c['cost_delta']}费）" if c["cost_delta"] else "")
            meta = f"{TYPE[c['type']]} · {RARITY[c['rarity']]} · {cost_note} · 目标：{TARGET.get(c['target'], c['target'])}"
            if c["kws"]:
                kw_names = {"Exhaust": "消耗", "Innate": "固有", "Mill": "弃光", "Banish": "除光"}
                meta += " · " + " ".join(f"「{kw_names.get(k, k)}」" for k in c["kws"])
            base_text = sp.get("base", render(c["desc"], c["vals"], upgraded=False))
            up_text = sp.get("up", render(c["desc"], c["up_vals"], upgraded=True))
            lines += [
                f"### {c['title']}",
                f"`{meta}`　`{c['id']}`",
                "",
                base_text.replace("\n", "  \n"),
                "",
            ]
            if c["rarity"] != "Token" and base_text != up_text:
                lines += [f"**敲后**：{up_text.replace(chr(10), '  ')}", ""]
            if c["rarity"] != "Token":
                lines += [f"> 升级变化：{change_line(c, c['vals'], c['up_vals'])}", ""]
            lines += ["---", ""]

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"OK 已生成 {OUT}，共 {len(cards)} 张卡")
    for c in cards:
        print(f"  [{RARITY[c['rarity']]}] {c['title']}  ({c['cls']}, {'含特殊覆盖' if c['special'] else '自动'})")


if __name__ == "__main__":
    main()
