# -*- coding: utf-8 -*-
"""更新工坊 workspace 的 workshop.json（v0.5.1 联机支持）与 mod 清单描述。
- workshop.json：changeNote（更新说明，突出联机支持）+ description 追加【联机】段
- mod/lightsworn/Lightsworn.json：description 追加联机说明（游戏内模组列表可见）
改完记得把 Lightsworn.json 同步到 dist/ 并重新部署（部署脚本 tools\\deploy_dist.ps1）。
"""
import io
import json
import os

WS = r'D:\1-workdata\lightsworn_mod-tools\workshop\lightsworn\workshop.json'
MOD_JSON = r'D:\1-workdata\lightsworn_mod\mod\lightsworn\Lightsworn.json'

CHANGE_NOTE = (
    "v0.5.1 联机支持！（双光道组队实机验证通过：握手/开局/起始遗物/事件/战斗全程一致、零分歧）\n"
    "· 联机兼容：修复队友事件串触发（玩家级钩子补 Owner 过滤）、融合生成锁按玩家隔离、起始遗物选择的联机一致性\n"
    "· 修复涅奥事件选项卡死（角色代词/语法本地化键缺失）\n"
    "· 修复左上角头像与能量球显示成铁甲占位\n"
    "! 联机时所有玩家必须安装【同版本】本mod + RitsuLib 前置，否则无法加入房间"
)

MP_DESC_LINE = (
    "\n【联机】支持多人联机（v0.5.1 起）：所有玩家需安装同版本 mod 与 RitsuLib 前置；"
    "双光道组队/混合角色队伍均可，选择界面弹出时全桌等待。\n"
)


def main():
    with io.open(WS, encoding='utf-8-sig') as f:
        ws = json.load(f)
    old_note = ws.get('changeNote')
    ws['changeNote'] = CHANGE_NOTE
    desc = ws.get('description', '')
    if '【联机】' not in desc:
        desc = desc.replace('【依赖】', MP_DESC_LINE.strip() + '\n【依赖】', 1)
        if '【联机】' not in desc:      # 兜底：直接追加
            desc = desc + '\n' + MP_DESC_LINE.strip()
    ws['description'] = desc
    with io.open(WS, 'w', encoding='utf-8') as f:
        json.dump(ws, f, ensure_ascii=False, indent=4)
    print('workshop.json updated. old changeNote:', old_note)

    with io.open(MOD_JSON, encoding='utf-8-sig') as f:
        mj = json.load(f)
    mdesc = mj.get('description', '')
    if '联机' not in mdesc:
        mj['description'] = mdesc + ' 支持联机（所有玩家需同版本 mod + RitsuLib）。'
    with io.open(MOD_JSON, 'w', encoding='utf-8') as f:
        json.dump(mj, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print('Lightsworn.json description updated.')


if __name__ == '__main__':
    main()
