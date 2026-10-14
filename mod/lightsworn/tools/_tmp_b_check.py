# -*- coding: utf-8 -*-
# 临时脚本：Cards2.cs 修改后的静态自检（花括号配平、遗留引用、关键点存在性）
import io, re, os

fp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Scripts", "Cards2.cs")
src = io.open(fp, "r", encoding="utf-8").read()

# 1) 花括号/圆括号配平（忽略字符串与注释粗略处理：本文件无字符串含括号的干扰项，先直接数）
bal_brace = src.count("{") - src.count("}")
bal_paren = src.count("(") - src.count(")")
print("brace balance:", bal_brace, " paren balance:", bal_paren)

# 2) 不应再出现的引用
gone = {
    "OrcusPower in Cards2": "OrcusPower" in src,
    "CardsVar in Cards2": "CardsVar" in src,
    "Decree mill leftover": re.search(r"class Decree.*?LsUtil\.Mill", src, re.S) is not None,
}
for k, v in gone.items():
    print(("FAIL " if v else "ok   ") + k)

# 3) 应出现的关键点
need = [
    "using MegaCrit.Sts2.Core.Models.Powers;",
    "ArtifactPower>",
    "TwilightPower>",
    "StrengthPower>",
    "DexterityPower>",
    "EnergyCost.UpgradeBy(-1)",
    "LsUtil.Banish(choiceContext, this, (int)DynamicVars[\"Banish\"].BaseValue)",
    "[LsKeywords.Banish];",
    "LsUtil.MillSelected(choiceContext, this, chosen)",
    '"LIGHTSWORN_TO_DISCARD"',
    "CreateToken<JudgementDragon>(new BlockingPlayerChoiceContext(), this, PileType.Discard, ethereal: true, exhaust: true)",
    'new DynamicVar("BlockGain", 4m)',
    'DynamicVars["BlockGain"].UpgradeValueBy(1)',
    'new DynamicVar("Debuff", 1m)',
    'DynamicVars["Debuff"].UpgradeValueBy(1)',
    'new DynamicVar("Strip", 1m)',
    "base(0, CardType.Skill",
    "base(1, CardType.Power",   # Aegis 1费
    "base(1, CardType.Skill, CardRarity.Uncommon, TargetType.Self) { }",  # Orcus 1费
]
for n in need:
    print(("ok   " if n in src else "MISS ") + n)

# 4) 每个目标类的起止行号
for cls in ["Orcus", "TwilightRyko", "TwilightLyla", "Kiryu", "Decree", "Aegis", "DarkMarch"]:
    m = re.search(r"public class %s : LsCard" % cls, src)
    line = src[:m.start()].count("\n") + 1 if m else -1
    print(f"class {cls} at line {line}")
