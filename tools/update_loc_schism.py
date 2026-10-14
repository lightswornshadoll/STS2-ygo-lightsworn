# v0.4.37 影依的伪典口径订正：
# ① cards.json —— 卡面描述在"影融"后加 {IfUpgraded:show:+（本次产出强化版神影依）|}（敲后1费+影融+）；
# ② powers.json —— 新增强化版能力词条 ShaddollSchismPowerPlus（GarothPowerPlus 同款：打出强化版能力）。
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOC = ROOT / "mod" / "lightsworn" / "lightsworn" / "localization" / "zhs"

cards_path = LOC / "cards.json"
cards = json.loads(cards_path.read_text(encoding="utf-8"))
key = "LIGHTSWORN-SHADDOLL_SCHISM.description"
old = "获得能力[gold]影依的伪典[/gold]：每回合开始时，可以消耗弃牌堆中的2张「影依」牌发动一次影融（不触发其被弃置时效果）。"
new = "获得能力[gold]影依的伪典[/gold]：每回合开始时，可以消耗弃牌堆中的2张「影依」牌发动一次影融{IfUpgraded:show:+（本次产出强化版神影依）|}（不触发其被弃置时效果）。"
assert cards[key] == old, "旧文案不匹配，已中止：" + cards[key]
cards[key] = new
cards_path.write_text(json.dumps(cards, ensure_ascii=False, indent=2), encoding="utf-8")
print("cards.json ok:", cards[key])

pw_path = LOC / "powers.json"
pw = json.loads(pw_path.read_text(encoding="utf-8"))
assert "LIGHTSWORN-SHADDOLL_SCHISM_POWER.title" in pw
plus = "每回合开始时，你可以消耗弃牌堆中的2张「影依」牌发动一次影融+（本次产出强化版神影依；不触发其被弃置时效果；可不发动）。"
pw["LIGHTSWORN-SHADDOLL_SCHISM_POWER_PLUS.title"] = "影依的伪典"
pw["LIGHTSWORN-SHADDOLL_SCHISM_POWER_PLUS.description"] = plus
pw["LIGHTSWORN-SHADDOLL_SCHISM_POWER_PLUS.smartDescription"] = plus
pw_path.write_text(json.dumps(pw, ensure_ascii=False, indent=2), encoding="utf-8")
print("powers.json ok:", plus)
