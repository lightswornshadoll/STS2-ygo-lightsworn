# -*- coding: utf-8 -*-
"""校验部署 pck 内的文案与源文件逐字节一致（v0.5.4 文案验证）"""
import hashlib
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "mod", "lightsworn", "lightsworn", "localization", "zhs", "cards.json")
ext = os.path.join(ROOT, "research", "pck_verify", "lightsworn", "localization", "zhs", "cards.json")

a = open(src, "rb").read()
b = open(ext, "rb").read()
print("源文件 sha256:", hashlib.sha256(a).hexdigest()[:16], len(a))
print("pck内  sha256:", hashlib.sha256(b).hexdigest()[:16], len(b))
print("逐字节一致:", a == b)
d = json.loads(b.decode("utf-8"))
for k in ["LIGHTSWORN_CARD_RYKO", "LIGHTSWORN_CARD_DARK_MARCH", "LIGHTSWORN_CARD_LAWN_MOWING",
          "LIGHTSWORN_CARD_TWIN_TWILIGHT_DRAGON", "LIGHTSWORN_CARD_SULIEK"]:
    print(k, "->", d[k + ".description"])
