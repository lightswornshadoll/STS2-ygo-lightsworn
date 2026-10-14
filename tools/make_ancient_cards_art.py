# -*- coding: utf-8 -*-
"""先古卡全框卡图生成（606×852）。
背景（游戏本体实证）：NCard 对 CardRarity.Ancient 的卡用独立的 %AncientPortrait 全卡铺满
（scenes/cards/card.tscn：rect 598×842、scale 0.5、STRETCH_SCALE=拉伸铺满），官方先古卡图规格
= 606×852（从游戏 pck 解出 corruption/whistle 的 card_portraits 纹理实测）——**不是常规的 250×190 竖窗**，
用 250×190 会在先古卡上被横向拉宽（用户报"卡图变形"的真因）。

做法：YGO 卡图插画区（约 300×310 方形）→ 等比放大到高 852 → 居中裁到 606 宽（cover：无拉伸、裁掉左右各约13%）。
适用卡：光道埃癸斯盾（25218587）、破坏之光（83027236，本mod两张先古牌）。
用法: py tools\\make_ancient_cards_art.py
"""
import os
from PIL import Image

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
SRC_DIR = r'D:\MyCardLibrary\ygopro\pics'
CARDS_DIR = os.path.join(ROOT, 'mod', 'lightsworn', 'lightsworn', 'images', 'cards')

W, H = 606, 852

# (类名, passcode, 插画窗口(x0,y0,x1,y1)=边缘亮度采样实测内沿：左50/右350/顶107/底408，避开卡框内沿灰条)
CARDS = [
    ('Aegis',             '25218587', (50, 107, 350, 408)),
    ('LightOfDestruction', '83027236', (50, 106, 350, 408)),
]


def cover_crop(src_path, win):
    art = Image.open(src_path).convert('RGB').crop(win)
    aw, ah = art.size
    scale = H / ah
    big = art.resize((round(aw * scale), H), Image.LANCZOS)
    left = (big.width - W) // 2
    return big.crop((left, 0, left + W, H))


def main():
    for name, code, win in CARDS:
        out = cover_crop(os.path.join(SRC_DIR, code + '.jpg'), win)
        path = os.path.join(CARDS_DIR, name + '.png')
        out.save(path)
        print(f'{name}: {out.size} -> {os.path.normpath(path)}')


if __name__ == '__main__':
    main()
