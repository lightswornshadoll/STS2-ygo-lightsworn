# -*- coding: utf-8 -*-
t = '''
> v1.6（mod v0.4.1，回滚）：按用户要求把角色形象**回滚为默认铁甲战士占位**（v0.4.0 的「光道圣女」自定义形象移除），角色名恢复「光道召唤师」，pck 中圣女资源（visuals/、images/character/）已删除，export include_filter 回退。原因：用户主动要求回退（视觉效果未达预期）。**方案与素材管线完整保留备查**：贴图重上色生成器 tools\\make_saint_assets.py、pck 解包器 tools\\pck.py、研究材料 research\\pck_dump、开发手册 §5「角色外观」（运行时 Spine 注入做法）均未删除，随时可恢复或改造成豆包分层素材+自建骨骼的新方案。版本 0.4.0→0.4.1。
'''
open(r'design/光道mod设计文档.md', 'a', encoding='utf-8').write(t)
print('ok')
