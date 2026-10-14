# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
path = r'D:\1-workdata\lightsworn_mod\design\光道mod设计文档.md'
entry = '''

---

## v1.23 融合双bug修复（2026-10-11，v0.4.24，用户实测反馈）

**来源**：用户实测「两个bug在最新一次对战都有触发」（godot.log 会话 Seed CDUDBVL19P 实证），
已知问题.txt 两条：①影依伤害临时变0未生效（化身拿影依兽打出仍9点）；②弃置梅洛人鱼墓地有
影依卡未触发珠泪融合（应可融合米德拉什）。

**问题1真根因（v0.4.21/22 两轮修复都修错方向）**：`Hook.AfterCardPlayed` 是**广播钩子**
（`combatState.IterateHookListeners()` 遍历全部牌堆的所有模型，CardModel.cs:1959 在 OnPlay
之后调用）——v0.4.21 的设计文档只记对了「能收到打出的牌自己」，漏了反向：**它也会收到
「别的卡被打出」的通知**。化身 OnPlay 尾部把影依兽置0（DamageRestoreAfterPlay=9,
BaseValue=0）→ 化身自己打完 → 广播把手牌里影依兽的 AfterCardPlayed 也调了 → 恢复机制当场
把 BaseValue 恢复回9 → 打出9点。零化从未活过一整个 OnPlay，这就是「检测仍然未修复」的原因
（v0.4.22 把锅判给融合选择界面崩溃 CanonicalModelException，误诊）。修复=两处覆写加
`cardPlay.Card == this` 自判：**LsCard.AfterCardPlayed**（伤害恢复）与 **ShaddollToken.AfterCardPlayed**
（二打计数——原实现打2张别的卡也会累计计数误消耗Token，属同根因的隐藏bug）。能力的
AfterCardPlayed（甲铠/猎犬等）本就是广播语义且自带 cardPlay.Card 判定，不动。

**问题2**：珠泪融合引擎（LsUtil.TearFusion）素材池只筛 `IsTearAttack`、产出只有4张珠泪Token，
影依牌永远进不来；墓地无其他珠泪攻击牌时静默 return（用户看到=没触发）。修复四件套：
①素材池扩为「珠泪攻击牌 或 影依牌」+候选预筛（照影融 ValidMaterialCandidates 精神，只显示与
触发卡组合后至少一种可用融合的牌）；②FusionOptions 加入**米德拉什**（条件与影融同：1影依+
1影依/珠泪，DistinctPair——触发卡自己占珠泪位）；③**严格判定前置**：available 判定挪到素材
弃置/回卡组之前，选出无融合的组合=什么都没发生（v0.4.15「白洗回」代价废除：素材池跨系后
误选概率大增）；④**生成锁跨引擎统一**：ResetShaddollFusionKeys→ResetFusionKeys（清两个
集合+文迪戈锁，一个 turnKey），生成时双登记（RegisterFusionGenerated），IsFusionLocked/
IsFusionUsedForCodex 双查——杜绝「珠泪融合与影融各生成一次米德拉什」的绕锁。

**文案**：card_keywords.json 珠泪融合词条（素材=珠泪攻击牌或影依牌、产出=融合卡）、
card_selection.json LIGHTSWORN_TEAR_MATERIAL。米德拉什卡面条件行不变（两引擎同条件）。

**AI拍板**：①严格判定前置（废除白洗回）②锁跨引擎统一（每回合每张全引擎共1次）③预筛只
对「trigger+单素材」组合判定，双素材组合靠前置 available 兜底。

**验证**：0.4.24 加载无异常（checklog + 全日志过滤 0 ERROR）。
'''
with open(path, 'a', encoding='utf-8') as f:
    f.write(entry)
print('appended v1.23')
