# -*- coding: utf-8 -*-
# 一次性：设计文档尾部追加 v1.27 变更记录
p = r"D:\1-workdata\lightsworn_mod\design\光道mod设计文档.md"
t = open(p, encoding="utf-8").read()
assert "## v1.27" not in t, "already appended"
entry = """
---

## v1.27 融合生成锁跨战斗/跨存档泄漏修复（2026-10-11，v0.4.29，朋友实测反馈）

**现象**：①上一场战斗最后一个回合融合出的怪，下一次战斗开始时不重置（图鉴仍置灰/同回合不能再融）；②第一回合影融（影依+光道攻击→拿非利/神子晶二选一）选拿非利后保存退出→继续（本场重打）→再融只出神子晶→再保存退出→继续→什么都融不了。

**根因**：融合生成锁（v0.4.24 统一引擎）是 static 集合、只按 "回合数:行动方" 字符串键控，不按战斗实例隔离——回合号每场从1重计（CombatState 构造器 RoundNumber=1，存档不含战斗状态）：①跨战斗同回合号碰撞（上一场第N回合的锁漏进下一场第N回合，末回合=第1回合时下一场开局即中）；②保存退出→继续=本场重打（新 CombatState 回到第1回合），键 "1:Player" 未变→拿非利仍锁→只出神子晶；再锁一轮→全锁死。

**改动**：LsUtil.cs 锁状态重做——5个静态字段收敛为 `ConditionalWeakTable<ICombatState, FusionLockState>`（TurnKey+两套本回合已生成集合+文迪戈本场锁），战斗结束随 CombatState 一起被 GC 回收，新战斗/读档重打天然全新；`IsFusionLocked/RegisterFusionGenerated` 补 combat 参数，`ValidMaterialCandidates` 透传；图鉴置灰 `IsFusionUsedForCodex` 改查实例状态（文迪戈项不再需要引用比较）。「本回合不能打出」play 锁本就带实例引用守卫，未动。

**验证**：v0.4.29 构建部署，日志加载零异常。融合场景实机复验待用户/朋友确认（两场战斗连续融合 + 融合后保存退出再继续）。
"""
open(p, "a", encoding="utf-8").write(entry)
print("appended v1.27")
