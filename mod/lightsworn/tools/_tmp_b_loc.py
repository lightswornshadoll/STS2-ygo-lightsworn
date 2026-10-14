# -*- coding: utf-8 -*-
# 临时脚本：生成 tools\locfrag\cards_B.json（Cards2.cs 七张卡改动的中文文案片段）
import json, os, io

frag = {
    "LIGHTSWORN-KIRYU.title": "光道宰制者 基里奥斯",
    "LIGHTSWORN-KIRYU.description": "弃光{Mill:diff()}。造成{Damage:diff()}点伤害。将弃置的1张牌加入手牌，然后从抽牌堆选择1张牌弃置。",

    "LIGHTSWORN-DECREE.title": "光道的裁决",
    "LIGHTSWORN-DECREE.description": "打出后，将此牌置于抽牌堆顶。\n[gold]从卡组被弃置时[/gold]：将1张虚无、消耗的「裁决之龙」加入弃牌堆。",

    "LIGHTSWORN-ORCUS.title": "光道德鲁伊 奥库斯",
    "LIGHTSWORN-ORCUS.description": "弃光{Mill:diff()}。获得1层人工制品。",

    "LIGHTSWORN-DARK_MARCH.title": "暗之进军",
    "LIGHTSWORN-DARK_MARCH.description": "将弃牌堆中1张「光道」牌加入手牌（强化后：该牌费用变为0）。除光{Banish:diff()}。",

    "LIGHTSWORN-TWILIGHT_RYKO.title": "暮光道斗犬 雷光",
    "LIGHTSWORN-TWILIGHT_RYKO.description": "消耗弃牌堆中的1张「光道」牌（若有）。移除目标敌人的{Strip:diff()}个随机增益，获得1层暮光。强化后：费用变为0。",

    "LIGHTSWORN-TWILIGHT_LYLA.title": "暮光道巫师 丽拉",
    "LIGHTSWORN-TWILIGHT_LYLA.description": "消耗弃牌堆中的1张「光道」牌（若无则此牌不产生任何效果）。使目标敌人失去{Debuff:diff()}点力量和{Debuff:diff()}点敏捷，获得1层暮光。",

    "LIGHTSWORN-AEGIS.title": "光道埃癸斯盾",
    "LIGHTSWORN-AEGIS.description": "每当你打出「光道」牌，获得{BlockGain:diff()}点格挡。",
}

out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "locfrag")
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "cards_B.json")
with io.open(out_path, "w", encoding="utf-8") as f:
    json.dump(frag, f, ensure_ascii=False, indent=2)
    f.write("\n")
print("written:", out_path)
with io.open(out_path, "r", encoding="utf-8") as f:
    data = json.load(f)
print("valid JSON, entries:", len(data))
