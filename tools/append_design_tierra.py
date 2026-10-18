# -*- coding: utf-8 -*-
# 修正 design\提耶拉boss设计.md 的附录 C（上次用 bash 内联 python，反引号被 shell 执行，代码名被吞）。
import io
import os

path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    'design', '提耶拉boss设计.md')
with io.open(path, encoding='utf-8', newline='') as f:
    text = f.read()

marker = '\n---\n\n## 附录 C：实现记录'
pos = text.find(marker)
if pos >= 0:
    text = text[:pos]

appendix = '''

---

## 附录 C：实现记录（2026-10-18，mod v0.7.0）

- 代码：`Scripts\\InfernoidTierra.cs`（怪物/Glory 遭遇/状态机/十级动作/转阶段/二阶段四招/静态立绘换图）、`Scripts\\InfernoidTierraCards.cs`（10 张不可打出诅咒 + 引爆管线）、`Scripts\\InfernoidTierraPowers.cs`（融合素材/阈值/创星/延迟 debuff）。
- 美术：`tools\\make_tierra_boss_assets.py`（两阶段 1536 立绘、350×307 白色地图蒙版+描边、85×85 历史图标=创星神头部裁切、10 张 250×190 诅咒卡图、能力图标 64/256）。
- 本地化：`tools\\update_loc_tierra.py`（zhs+eng；能力长键+短键）。
- 注册：`InfernoidTierraBoss` 加入 Glory Boss 池；`DarkWorldGraphaDiscoveryPatch` 改为 [格拉法, 提耶拉] 优先发现顺序；三幕 Boss 抉择事件自动包含。
- 版本：`Lightsworn.csproj` / `Lightsworn.json` 0.7.0。
- 验证：build 0 错误；0.107 LsCompatTrial PASS；memberref 0.107+0.111 双 PASS；实机 `fight LIGHTSWORN_ENCOUNTER_INFERNOID_TIERRA_BOSS` 验证：600→创星→500、素材 3/5/8/10 阈值、拿玛动作后素材回1+下回合弃手牌、二阶段邪恶/洪水循环与创星+2、500 血击杀正常结算。
- 实现口径/坑：
  1. **转阶段治疗必须在移除阶段门之前**：先 `SetMaxHp`+`Heal`（阶段门仍在，战斗未被判结束），再移除阶段门/切 Phase=2；反序会让 Heal 因 `IsEnding` 直接 return，Boss 保持 0 血、战斗判胜。
  2. 静态立绘的死亡动画会把 `Visuals:modulate:a` 淡到 0；转阶段换图时需 `AnimationPlayer.Stop()` + 恢复 `Modulate=White`。
  3. 自定义意图必须继承 `StatusIntent` 才会渲染文字标签（纯 `AbstractIntent` 标签为空）；长文本放到 tooltip，意图行只放短标签（复制：XX / 献祭 / 融合无效等）。
  4. 立绘缩放 0.48、IntentPos=(0,-620)；0.5 缩放时 Boss 太高，意图会被顶栏裁掉。
  5. 素材数按“正好达到 3/5/8”触发；一次引爆的代价在 `BeginBatch/EndBatch` 内结算，7→9 会跳过 8。
  6. 8 级回收不降素材数；10 级拿玛动作结算完才 `CompleteFusionAsync`；十进管复制 10 级动作不触发 10 特效。
  7. 3 级融合封印复用 `LsUtil.FusionCodexConcepts`/`LockFusionGeneratedThisTurn`；若本回合已有融合生成锁，候选会相应减少（既有语义）。
'''

with io.open(path, 'w', encoding='utf-8', newline='') as f:
    f.write(text + appendix)
print('fixed appendix C')
