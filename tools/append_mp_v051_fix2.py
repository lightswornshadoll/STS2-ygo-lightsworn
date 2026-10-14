# -*- coding: utf-8 -*-
"""设计文档追加 v1.43 补记2（角色资源修复）——先清掉上一条被 bash 转义弄坏的半成品，再写正确内容。"""
import io

PATH = r'D:\1-workdata\lightsworn_mod\design\光道mod设计文档.md'

ADD = """
### v1.43 补记2：角色资源修复（2026-10-14 晚，用户目击反馈）

**用户反馈**：「左上角的头像和能量球都变回战士了」（联机实测期间目击）。核查确认属实，**根因=RitsuLib 占位资源继承**：
`ModCharacterTemplate.ResolvedAssetProfile` 会把**未覆盖的资源槽从占位角色（PlaceholderCharacterId=ironclad）继承**。
- 左上角角落头像 = `Character.Icon` 场景（`NTopBarPortrait.AddChild(player.Character.Icon)`）——mod 只给了
  `CustomIconTexturePath`（顶栏图标贴图，另一槽位），没给 `CustomIconPath`（**图标场景**）→ 继承铁甲的
  `ui/character_icons/ironclad_icon.tscn` → 角落头像显示铁甲。
- 能量球：0.5.0 的自建 `NEnergyCounter.Create` 前缀**从未生效**——RitsuLib 自己的同点前缀带 `[HarmonyPriority(800)]`，
  先解析到「继承来的铁甲能量球场景」建球并 return false 中止补丁链，mod 前缀（默认优先级 400）跑不到 → 显示铁甲的红色八角球。

**修复**：
1. 新场景 `lightsworn\\visuals\\saint_icon.tscn`（纯 TextureRect + icon.png，构型照原版 ironclad_icon.tscn）
   + 角色覆写 `CustomIconPath`。
2. 新场景 `lightsworn\\visuals\\saint_energy_counter.tscn`（镜像原版 ironclad_energy_counter.tscn 的
   Layers/RotationLayers/Layer1-5，**去掉 script/material/VFX 实例**——mod 导 pck 不能引游戏脚本）
   + 角色覆写 `CustomEnergyCounterPath`；由 RitsuLib `RitsuNEnergyCounterNodeFactory` 转换建球并自动补齐
   %EnergyVfxBack/%EnergyVfxFront/Label/%StarAnchor 槽位。删除 LightswornEnergyCounter.cs 里的自建 build patch
   （保留 OutlineColor 描边补丁），Entry 同步取消注册。
3. 实机验证（beta 0.111.0 单机，读档 + 控制台 fight 进战斗）：左上角头像=光道圣女 OK、能量球=圣女金色菱形球+3/3 OK、
   日志零 ERROR（仅 "Asset not cached: icon.png" 按需加载的无害警告）。证据图 `tools\\mp_evidence\\09*.png`。
4. 已同步 dist / 游戏 mods / 工坊 workspace（三处 md5 一致：dll 78ed1271 / pck cad22f81c / json 0.5.1）。
"""


def main():
    with io.open(PATH, encoding='utf-8') as f:
        text = f.read()
    # 清掉被 bash 转义弄坏的半成品补记2（若存在）
    marker = '### v1.43 补记2'
    idx = text.find(marker)
    if idx != -1:
        text = text[:idx].rstrip() + '\n'
        print('removed broken addendum at offset', idx)
    text = text.rstrip() + '\n' + ADD
    with io.open(PATH, 'w', encoding='utf-8') as f:
        f.write(text)
    print('appended fix2, new size:', len(text))


if __name__ == '__main__':
    main()
