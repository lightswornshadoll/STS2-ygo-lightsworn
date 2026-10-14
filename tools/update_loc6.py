# v0.4.6 米迦勒文案（用户拍板：先伤害→再只回收光道）
import io, json, os

base = os.path.join(os.path.dirname(__file__), "..", "mod", "lightsworn", "lightsworn", "localization", "zhs")
p = os.path.join(base, "cards.json")
d = json.load(io.open(p, encoding="utf-8"))
d["LIGHTSWORN-MICHAEL.description"] = "造成{Damage:diff()}点伤害。将弃牌堆中的「光道」牌全部洗回抽牌堆，每洗回1张获得3点格挡。"
with io.open(p, "w", encoding="utf-8") as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
    f.write("\n")
print("MICHAEL =", d["LIGHTSWORN-MICHAEL.description"])
