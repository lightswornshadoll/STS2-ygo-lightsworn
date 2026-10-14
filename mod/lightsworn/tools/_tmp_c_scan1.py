import os, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

mod = r"D:\1-workdata\lightsworn_mod\mod\lightsworn"
research = r"D:\1-workdata\lightsworn_mod\research"

def scan(base, pats, exts=(".cs",)):
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d not in (".godot", "bin", "obj", "Godot_v4.5.1-stable_mono_win64")]
        for f in files:
            if f.endswith(exts) and not f.startswith("_tmp_c_"):
                p = os.path.join(root, f)
                try:
                    lines = open(p, encoding="utf-8", errors="replace").read().splitlines()
                except Exception as e:
                    print("ERR", p, e); continue
                for i, l in enumerate(lines):
                    for pat in pats:
                        if re.search(pat, l):
                            print(f"{p}:{i+1}: {l.strip()}")
                            break

print("=== mod usages of IntendsToAttack / MonsterModel / as Monster ===")
scan(mod, [r"IntendsToAttack", r"MonsterModel", r"as Monster ", r"\bIsMonster\b", r"IntentType"])

print("=== CardSelectorPrefs constructor in BaseLib ===")
scan(os.path.join(research, "BaseLib-StS2-master"), [r"class CardSelectorPrefs", r"public CardSelectorPrefs"])

print("=== HittableEnemies definition ===")
scan(os.path.join(research, "sts2src"), [r"HittableEnemies"], )

print("=== MinervaAthenaPower references in mod ===")
scan(mod, [r"MinervaAthenaPower"])
