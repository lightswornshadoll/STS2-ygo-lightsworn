# -*- coding: utf-8 -*-
"""v0.4.42 先古卡全框卡图：向 design\光道mod设计文档.md 尾部追加变更记录（每次重写后运行）。"""
import io
import os

p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                 'design', '光道mod设计文档.md')

record = '''
---

## v1.39 先古卡全框卡图修复（2026-10-13，v0.4.42，用户点名）

**真因**（用户提示"先古卡卡图是全框的、有单独比例"后实证）：对 `CardRarity.Ancient` 的卡，NCard 用独立的 **%AncientPortrait** 渲染（`scenes/cards/card.tscn`：全卡锚点 rect 598×842、scale 0.5 → 显示 299×421、**STRETCH_SCALE 拉伸铺满**），卡图**不是常规的 250×190 竖窗**。从游戏 pck 解出官方先古卡纹理实测（`.godot/imported/corruption.png-*.ctex`、`whistle.png-*.ctex` → `tools\\ctex.py` 解码）：**官方规格 = 606×852**（≈0.711 全卡比例，无缝满幅）。v0.4.41 那张 250×190 的埃癸斯盾在 299×421 的框里被横向拉宽——这就是"变形"的真因（我 v0.4.41 误判为旧图问题，实际比例本身就不对）。
**修复**：`tools\\make_ancient_cards_art.py`（新）——两张先古卡（光道埃癸斯盾 25218587 / 破坏之光 83027236）YGO 插画区（边缘亮度采样实测内沿：左50/右350/顶106-107/底408，避开卡框内沿灰条）→ 等比放大到高 852 → 居中裁 606 宽（cover：无拉伸，左右各裁约13%）。**破坏之光旧图另有一处问题一并对齐**：原 250×190 只裁了插画上半截（y110-330），本次取全插画。
**通用知识（已入手册）**：先古卡（Ancient）卡图规格 = **606×852 全框**（常规卡才是 250×190）；两张先古卡的卡图以后按此重裁。Power 图标（圆形裁切）仍从卡图中心取，不受影响。
**验证**：重导入 → ExportPck → 部署；从部署 pck 解出两张纹理与本地 **0 diff（md5 相同）**、尺寸 606×852；日志 Version=0.4.42.0 零 Lightsworn 异常。
'''

t = io.open(p, encoding='utf-8').read()
assert '## v1.39' not in t, 'already appended'
io.open(p, 'a', encoding='utf-8', newline='').write(record)
print('设计文档已追加 v1.39')
