import io, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
p = r"D:\1-workdata\lightsworn_mod\mod\lightsworn\Scripts\Cards3.cs"
src = open(p, encoding="utf-8").read()
lines = src.splitlines()
print("total lines:", len(lines))
# brace/paren balance (crude, string-literal-aware enough for this file)
bal = {"{": 0, "(": 0, "[": 0}
pairs = {")": "(", "]": "[", "}": "{"}
in_str = False
prev = ""
ok = True
for ch in src:
    if in_str:
        if ch == '"' and prev != "\\":
            in_str = False
    else:
        if ch == '"':
            in_str = True
        elif ch in bal:
            bal[ch] += 1
        elif ch in pairs:
            bal[pairs[ch]] -= 1
    prev = ch
print("balance:", bal, "in_str_at_eof:", in_str)
for kw in ["MinervaAthenaPower", "DistinctLsInGravezones", "ExhaustOneFromDiscard", "DistinctLsInDiscard",
           "UpgradeBy(-1)", "IntendsToAttack", "MillSelected", "MultiPileCardSelect", "WeakPower",
           "Shuffle(choiceContext", "GainBlock", "UpgradeValueBy(5)"]:
    hits = [i + 1 for i, l in enumerate(lines) if kw in l]
    print(f"{kw}: {hits}")
