"""本批（幻色珍珠/事件文案/召唤师萨满）本地化更新
- events.json（zhs+eng）：梅洛↔小美人鱼 身份性格对调；选项二改为给遗物幻色珍珠
- relics.json（zhs）：新增 LIGHTSWORN_RELIC_PHANTOM_PEARL
- cards.json（zhs）：LUMINA/TWILIGHT_LUMINA 补"才能打出"条件文案
"""
import io, json, os

ROOT = r"D:\1-workdata\lightsworn_mod\mod\lightsworn\lightsworn\localization"

def load(p):
    with io.open(p, encoding='utf-8') as f:
        return json.load(f)

def save(p, d):
    with io.open(p, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
        f.write('\n')

# ---------- events.json ----------
INITIAL = ("浅滩上泛着[purple]珍珠色的微光[/purple]，一阵歌声顺着水面飘来。\n"
           "三位人鱼从涟漪中探出头来——[blue]塞壬[/blue]、[blue]梅洛[/blue]和[blue]小美人鱼[/blue]，珠泪哀歌族的三姐妹。\n"
           "「哎呀，是陆地的旅人。」塞壬歪着头打量你，「你身上的光……好温暖。」\n"
           "「她的眼睛亮晶晶的！」梅洛拍起水花，「和我们收集的珍珠一样！」\n"
           "小美人鱼什么也没说，只是从水里捧起一把珍珠，朝你眨了眨眼。")

JOIN_DESC = ("[blue]塞壬人鱼[/blue]、[blue]梅洛人鱼[/blue]和[blue]小美人鱼[/blue]加入你的[gold]卡组[/gold]。\n"
             "「作为同行的信物——」塞壬把一片[red]腐朽的鳞[/red]按进你的手心，冰凉刺骨。")

TAKE_PEARLS_DESC = "获得遗物[gold]幻色珍珠[/gold]。"

JOIN_END = ("「跟我们走……真的吗？」\n"
            "三双湿润的眼睛同时亮了起来。\n"
            "塞壬将一颗泪珠凝成卡牌的模样，轻轻放进你的卡组；小美人鱼用珍珠串起卡组的锁链；梅洛高兴地唱起了不成调的歌。\n"
            "临别时，小美人鱼又从水底捞起一片[red]腐朽的鳞片[/red]塞进你的卡组，「陆地的路很长，」她轻声说，「疼的时候，就当我们在陪你。」\n"
            "「呐——要是难过了，就把我们[red]融合[/red]起来吧。」梅洛凑过来补了一句。\n"
            "「在眼泪流干之前，我们会一直陪着你的。」")

PEARLS_END = ("你婉拒了同行的邀请。\n"
              "「这样呀……」塞壬的耳朵耷拉了一下，但很快又笑起来，「那，至少带上这些。」\n"
              "小美人鱼把那颗[gold]幻色珍珠[/gold]塞进你手里，冰凉温润，在光下泛着彩虹色的光晕。\n"
              "「陆地的路很长，」她轻声说，「别让自己太辛苦。」\n"
              "人鱼们向你挥别，沉入珍珠色的水光之中。")

for lang in ('zhs', 'eng'):
    p = os.path.join(ROOT, lang, 'events.json')
    d = load(p)
    P = 'LIGHTSWORN_EVENT_PEARL_WORLD_ENCOUNTER.'
    for k in (P + 'pages.INITIAL.description', P + 'pages.INITIAL.options.JOIN_TEARLAMENTS.description',
              P + 'pages.INITIAL.options.TAKE_PEARLS.description', P + 'pages.JOIN.description',
              P + 'pages.PEARLS.description'):
        assert k in d, (p, k)
    d[P + 'pages.INITIAL.description'] = INITIAL
    d[P + 'pages.INITIAL.options.JOIN_TEARLAMENTS.description'] = JOIN_DESC
    d[P + 'pages.INITIAL.options.TAKE_PEARLS.description'] = TAKE_PEARLS_DESC
    d[P + 'pages.JOIN.description'] = JOIN_END
    d[P + 'pages.PEARLS.description'] = PEARLS_END
    save(p, d)
    print('events updated:', p)

# ---------- relics.json（只有 zhs） ----------
p = os.path.join(ROOT, 'zhs', 'relics.json')
d = load(p)
d['LIGHTSWORN_RELIC_PHANTOM_PEARL.title'] = '幻色珍珠'
d['LIGHTSWORN_RELIC_PHANTOM_PEARL.description'] = (
    '拾起时，随机变成[gold]金色珍珠[/gold]或[red]诅咒珍珠[/red]的效果；有1%的概率变成[blue]发光珍珠[/blue]的效果。\n'
    '当前效果：{Effect}')
save(p, d)
print('relics updated:', p)

# ---------- cards.json（zhs） ----------
p = os.path.join(ROOT, 'zhs', 'cards.json')
d = load(p)
lum = 'LIGHTSWORN_CARD_LUMINA.description'
twl = 'LIGHTSWORN_CARD_TWILIGHT_LUMINA.description'
assert lum in d and twl in d
d[lum] = '手牌中有其他牌时才能打出。\n弃光{Mill:diff()}。弃置1张手牌，从弃牌堆中将{Picks:diff()}张「光道」牌加入手牌（本回合费用为0）。'
d[twl] = '弃牌堆中有「光道」牌时才能打出。\n消耗弃牌堆中的1张「光道」牌，将消耗堆中的{Picks:diff()}张「光道」牌加入手牌（费用变为0）。获得{Twilight:diff()}层暮光。'
save(p, d)
print('cards updated:', p)
print('OK')
