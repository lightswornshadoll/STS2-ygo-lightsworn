# 设计文档尾部追加 v0.4.44 订正记录（一次性脚本）
import io

DOC = r"D:\1-workdata\lightsworn_mod\design\光道mod设计文档.md"
record = """

---

## v1.41 用户订正3条（2026-10-14，v0.4.44，对话直接下发）

1. **炎核订正**：v1.40 第2条理解错误——"弃光X"是改在**被弃置时**：`弃光4 → 弃光X（X=手牌中不同名「神影依」的数量+1）`；
   主动打出的效果**恢复原样**（造成15/20伤害；可以从卡组弃置1张影依攻击卡，若如此做对目标施加1层虚弱和易伤）。
2. **光道龙订正**：升级**同时**改两项——伤害 18→22 **并且** 每张「光道」+2→+3（v1.40 把 Scale 升级删掉是错的，已恢复；
   OnUpgrade = Damage+4 与 Scale+1 并改）。
3. **绊影依/救影依订正**：两张重做卡的**「被弃置时」效果整体删除**（绊影依"从弃牌堆将1张影依牌置于抽牌堆顶"、
   救影依"抽1张牌"；v1.40 保留的判断作废）。被弃置仍走 ShaddollCard 管线（照常计「影依」弃置事件=咒缚/蠢动/影文蒂联动），
   只是不再有效果本身。

**验证**：v0.4.44 构建（0错误）→ ExportPck（pck 20,466,556B）→ dist 与游戏目录三件套 md5 一致
（dll cf5274ab…/pck ce97d722…）→ 从部署 pck 解出 cards.json 抽查三条新文案全部到位 → 日志 Version=0.4.44.0
+ Lightsworn mod initialized! 零异常；图鉴重跑（炎核恢复原效果+弃光X、两张影依无被弃置段、光道龙 18/22 且每张 2→3）。
"""
text = io.open(DOC, encoding="utf-8").read()
if "v1.41 用户订正3条" in text:
    print("already appended, skip")
else:
    io.open(DOC, "a", encoding="utf-8").write(record)
    print("appended v1.41 record")
