"""把已解码的 Boss 美术与原始配置整理成参考文件夹。
前置：先跑 research/dirtest/extract_boss_lagavulin.gd（Godot headless 解码 PNG 到 tools/_bossref_out），
      且 tools/_bossref_raw 已由 pck.py extract ... lagavulin 解出。
"""
import json
import os
import shutil

SRC_PNG = r"D:/1-workdata/lightsworn_mod/tools/_bossref_out"
SRC_RAW = r"D:/1-workdata/lightsworn_mod/tools/_bossref_raw"
DST = r"D:/1-workdata/lightsworn_mod/design/boss美术参考/lagavulin_matriarch"

SUB = {
    "spine": "01_战斗形象_Spine",
    "map": "02_地图节点图标",
    "history": "03_历史记录图标",
    "bg": "04_战斗背景_Underdocks",
    "cfg": "05_原版配置参考",
}

dirs = {k: os.path.join(DST, v) for k, v in SUB.items()}
for d in dirs.values():
    os.makedirs(d, exist_ok=True)

copies = [
    ("spine", ["lagavulin_matriarch.png"]),
    ("map", ["lagavulin_matriarch_boss_icon.png", "lagavulin_matriarch_boss_icon_outline.png"]),
    ("history", ["lagavulin_matriarch_boss.png", "lagavulin_matriarch_boss_outline.png"]),
    ("bg", [f for f in os.listdir(SRC_PNG) if f.startswith("underdocks_")]),
]
for key, files in copies:
    for f in files:
        shutil.copy2(os.path.join(SRC_PNG, f), os.path.join(dirs[key], f))

# Spine 源文件：.spatlas 是 JSON 包装，取出里面的 atlas 文本；.spskel 即二进制 skeleton
imp = os.path.join(SRC_RAW, ".godot", "imported")
spatlas = [f for f in os.listdir(imp) if f.endswith(".spatlas")][0]
spskel = [f for f in os.listdir(imp) if f.endswith(".spskel")][0]
with open(os.path.join(imp, spatlas), "r", encoding="utf-8") as fh:
    atlas_text = json.load(fh)["atlas_data"]
with open(os.path.join(dirs["spine"], "lagavulin_matriarch.atlas"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write(atlas_text)
shutil.copy2(os.path.join(imp, spskel), os.path.join(dirs["spine"], "lagavulin_matriarch.skel"))
shutil.copy2(
    os.path.join(SRC_RAW, "animations", "monsters", "lagavulin_matriarch", "lagavulin_matriarch_skel_data.tres"),
    os.path.join(dirs["spine"], "lagavulin_matriarch_skel_data.tres"),
)

# 场景/配置/反编译源码
shutil.copy2(
    os.path.join(SRC_RAW, "scenes", "creature_visuals", "lagavulin_matriarch.tscn"),
    os.path.join(dirs["cfg"], "creature_visuals_lagavulin_matriarch.tscn"),
)
bg_src = os.path.join(SRC_RAW, "scenes", "backgrounds", "lagavulin_matriarch_boss")
shutil.copy2(
    os.path.join(bg_src, "lagavulin_matriarch_boss_background.tscn"),
    os.path.join(dirs["cfg"], "lagavulin_matriarch_boss_background.tscn"),
)
layers_dst = os.path.join(dirs["cfg"], "background_layers")
os.makedirs(layers_dst, exist_ok=True)
for f in os.listdir(os.path.join(bg_src, "layers")):
    shutil.copy2(os.path.join(bg_src, "layers", f), os.path.join(layers_dst, f))

decomp = r"D:/1-workdata/lightsworn_mod/research/sts2src_0111"
shutil.copy2(
    os.path.join(decomp, "MegaCrit.Sts2.Core.Models.Encounters", "LagavulinMatriarchBoss.cs"),
    os.path.join(dirs["cfg"], "LagavulinMatriarchBoss.cs"),
)
shutil.copy2(
    os.path.join(decomp, "MegaCrit.Sts2.Core.Models.Monsters", "LagavulinMatriarch.cs"),
    os.path.join(dirs["cfg"], "LagavulinMatriarch.cs"),
)

print("OK ->", DST)
for k, d in dirs.items():
    print(f"  {SUB[k]}: {len(os.listdir(d))} 项")
