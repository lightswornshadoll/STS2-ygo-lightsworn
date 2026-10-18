# -*- coding: utf-8 -*-
"""v0.7.4：设计文档追加事件立绘高清重制记录。"""
import io
import os

p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                 'design', '光道mod设计文档.md')

record = '''
---

## v1.57 三层事件立绘高清重制（2026-10-18，v0.7.4）

用户提供同一画面更高清素材 `D:\\download\\chrome_download\\光道mod素材\\最远方的宇宙.jpeg`（1536×1337 RGBA；
v0.7.3 用的是 1248×1248）。`tools\\make_universe_event_art.py` 的 SRC 切到新图后重跑：中心 cover 裁
1536×720（2.133:1）→ LANCZOS 放大 3440×1613，输出仍为 `lightsworn\\images\\events\\farthest_universe.png`，
`CustomInitialPortraitPath` 不用改。

**验证**：`Godot --headless --import` 重导 → ExportPck；pck 内 `farthest_universe.png-8c68…ctex`
（5,097,338B，v0.7.3 为 3,294,576B）解码为 3440×1613，与本地 PNG 逐像素 diff=None；
build 0 错误、memberref 双 PASS（methods=286）、0.107.1 实机 `Version=0.7.4.0` 零异常。
'''
t = io.open(p, encoding='utf-8').read()
assert '## v1.57' not in t, 'already appended'
io.open(p, 'a', encoding='utf-8', newline='').write(record)
print('设计文档已追加 v1.57')
