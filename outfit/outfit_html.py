# -*- coding: utf-8 -*-
"""Builds the 穿搭 tab fragment (outfit/outfit_panel.html) + compressed photos in public/images/outfit/.
Run from anywhere before theme_palette.py:  python outfit/outfit_html.py
Photos come from outfit/outfit_images/ (originals, any format); each is resized to 720 px wide JPEG."""
import html
import json
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
PUB = HERE.parent / "public"
OUT_IMG = PUB / "images" / "outfit"

# (num, date, title, meta, [(part, desc, colour)], palette, tip, [(image stem, caption)])
DAYS = [
    ("01", "3/8", "抵达浦东 · 川沙古镇", "MH388 抵达，下午逛古镇 · 驼色牛仔蓝 · 8–14℃",
     [("上衣", "燕麦色薄针织衫，里面白色长袖 T 恤", "#E4D5BB"), ("下装", "蓝色直筒牛仔裤，盖到鞋面", "#4F78A0"),
      ("外套", "驼色长款双排扣大衣，敞穿", "#B98A55"), ("鞋", "白灰厚底运动鞋，石板路走着稳", "#D8D6D0"),
      ("配饰", "绿棕色小斜挎包", "#7A7A5A")],
     ["#E4D5BB", "#B98A55", "#4F78A0", "#7A7A5A"], "刚落地先用大衣挡一下潮冷，古镇的灰瓦、红灯笼和驼色最搭。",
     [("day01", "")]),
    ("02", "3/9", "静安寺 · 宫宴汉服 · 陆家嘴 · 外滩夜景", "06:30 出门，22:45 到酒店 · 浅杏灰蓝黑 · 6–13℃",
     [("上衣", "浅杏色开衫，里面灰蓝长袖打底", "#F0D9B8"), ("下装", "黑色高腰直筒裤", "#2B2B2E"),
      ("外套", "炭灰色薄呢大衣，天冷时披肩上，不用时搭在手臂", "#3A3D3F"), ("鞋", "白色运动鞋，全天走路", "#EDEDED"),
      ("配饰", "浅灰围巾，晚上外滩江边风大时系上", "#C5C8CE")],
     ["#F0D9B8", "#2B2B2E", "#3A3D3F", "#C5C8CE"], "早上和夜里的温差最大，围巾和外套要随身带；宫宴换装时选浅色系的汉服，和杏色开衫一样柔和。",
     [("day02", "白天到夜晚 · 外滩"), ("day02_hanfu", "宫宴 · 汉服妆造")]),
    ("03", "3/10", "上海迪士尼", "07:20 出门，22:20 班车回 · 奶油白浅蓝 · 8–15℃",
     [("上衣", "奶油白拉链连帽衫", "#F2EEE6"), ("下装", "浅色水洗直筒牛仔裤", "#BCD3E8"),
      ("外套", "浅蓝轻薄羽绒背心，早晚冷就套上，热了脱下放包里", "#A8C4E0"), ("鞋", "白色厚底运动鞋，一整天排队走路", "#EDEDED"),
      ("配饰", "米奇发箍 + 红色小斜挎包 + 一次性雨披", "#C0392B")],
     ["#F2EEE6", "#A8C4E0", "#BCD3E8", "#C0392B"], "背心比外套方便，排队时冷、玩项目时热；雨披放在包里，下雨时不用买贵的。",
     [("day03", "")]),
    ("04", "3/11", "上海 → 苏州 · 虎丘 · 七里山塘", "07:30 出发，20:30 回 · 墨绿燕麦米白 · 7–15℃",
     [("上衣", "燕麦色薄针织衫", "#D9C8A8"), ("下装", "米白色直筒裤", "#EDE6D6"),
      ("外套", "墨绿色薄防风夹克，船上和山塘河边风凉", "#2F4A3D"), ("鞋", "棕色皮边运动鞋，爬虎丘的石阶不滑", "#7A5A3C"),
      ("配饰", "米色薄围巾 + 棕灰小斜挎包", "#C9B79C")],
     ["#D9C8A8", "#2F4A3D", "#EDE6D6", "#7A5A3C"], "山塘街的白墙黑瓦配墨绿和米白最安静；坐船和过桥时风大，围巾别省。",
     [("day04", "")]),
    ("05", "3/12", "拙政园 · 平江路 · 金鸡湖", "09:00 出门，21:30 回 · 苔绿雾粉奶油 · 6–15℃",
     [("上衣", "苔绿色针织开衫，里面奶油色长袖", "#AEBE8C"), ("下装", "雾粉色百褶长裙，里面穿黑色保暖打底裤", "#C9A9A6"),
      ("外套", "灰色薄披肩，肩上一搭，傍晚金鸡湖风大时裹上", "#B9B6AE"), ("鞋", "米色平底运动鞋，园林里的木桥和石板路走着稳", "#E4D8BF"),
      ("配饰", "绿棕色小斜挎包", "#7A7A5A")],
     ["#AEBE8C", "#C9A9A6", "#F2EBDD", "#7A7A5A"], "园林里的绿、粉和木色最好拍；裙子里面一定穿保暖打底，傍晚的湖边还要加披肩。",
     [("day05", "")]),
    ("06", "3/13", "苏州 → 乌镇 · 西栅 · 汉服", "08:30 出发，20:30 回 · 浅蓝奶白 · 5–14℃",
     [("上衣", "浅天蓝 + 奶白汉服交领上襦", "#BFD7E3"), ("下装", "奶白色长裙，里面穿保暖裤", "#F2EBDD"),
      ("外套", "奶白色羊毛披肩，晚上水边凉，一定要带", "#F3EEE4"), ("鞋", "浅色布面平底鞋（租店里配的），换回运动鞋放包里", "#DCE6EB"),
      ("配饰", "发饰 + 竹骨纸伞", "#C9A880")],
     ["#BFD7E3", "#F2EBDD", "#F3EEE4", "#C9A880"], "水乡的黑瓦、红灯笼和浅蓝奶白最出片；汉服里面穿保暖贴身衣，披肩晚上是救命稿，19:30 回店归还前别弄脏。",
     [("day06", "")]),
    ("07", "3/14", "乌镇 → 杭州 · 河坊街 · 西湖 · 武林夜市", "06:50 出门，21:30 回 · 雾蓝白深灰 · 7–16℃",
     [("上衣", "白色薄针织衫", "#F3F1EC"), ("下装", "深灰色直筒裤", "#4A4D52"),
      ("外套", "雾蓝色薄风衣，敞穿，傍晚西湖边风凉", "#A9BCC8"), ("鞋", "白色运动鞋，坐车、走街都舒服", "#EDEDED"),
      ("配饰", "黑色小斜挎包", "#2B2B2E")],
     ["#A9BCC8", "#F3F1EC", "#4A4D52", "#2B2B2E"], "杭州比乌镇暖一点，白天一件风衣够；晚上去武林夜市吃小吃，深色裤子不显油。",
     [("day07", "")]),
    ("08", "3/15", "法喜寺 · 灵隐寺 · 西湖 · 湖滨", "06:20 出门，21:30 回 · 米色深灰蓝墨绿 · 6–15℃",
     [("上衣", "米色长袖针织小高领，肩膀手臂都遮住", "#D9C4A5"), ("下装", "深灰蓝直筒长裤，不穿短裤，寺庙更得体", "#4A5568"),
      ("外套", "墨绿轻薄防风冲锋衣，早上山里有雾，防潮防风", "#3F5A48"), ("鞋", "灰绿防滑徒步运动鞋，石阶和青苔路不滑", "#7A8478"),
      ("配饰", "小丝巾 / 薄围巾，山里早晚凉时围上", "#C7B88A")],
     ["#D9C4A5", "#4A5568", "#3F5A48", "#7A8478"], "寺庙和山路要走很多石阶，遮肩长袖长裤 + 防滑鞋最合适；早上山里比市区低几度，别只穿薄外套。",
     [("day08", "")]),
    ("09", "3/16", "杭州 → 浦东机场 → 回吉隆坡", "09:00 出发，15:25 起飞 · 燕麦浅灰驼色 · 8–17℃",
     [("上衣", "燕麦色柔软针织衫", "#D8C9B2"), ("下装", "浅灰色松紧腰直筒裤，坐地铁和飞机都舒服", "#CFCFCF"),
      ("外套", "驼色薄风衣，不冷时搭在手臂，落地吉隆坡前收进手提", "#C9A57A"), ("鞋", "白色运动鞋，换乘多，走得快", "#EDEDED"),
      ("配饰", "帆布托特包 + 银灰色登机箱", "#B8B8B8")],
     ["#D8C9B2", "#CFCFCF", "#C9A57A", "#B8B8B8"], "这天要坐地铁、高铁、机场线，换乘多；吉隆坡是热带，下飞机前把长袖脱掉，多带一双干袜子。",
     [("day09", "")]),
]
PACK = [
    "鞋只带 2 双：① 白色或米色厚底运动鞋（第 1、2、3、5、7、9 天，逛街和排队都舒服）；② 防滑徒步运动鞋或带皮边的运动鞋（第 4、8 天，虎丘的石阶、灵隐寺的青苔路）",
    "大衣和风衣：驼色长款大衣（第 1 天）、炭灰薄呢大衣（第 2 天）、驼色薄风衣（第 9 天）、雾蓝薄风衣（第 7 天），按当天天气选",
    "轻薄外套：浅蓝羽绒背心（第 3 天）、墨绿防风夹克（第 4 天）、墨绿冲锋衣（第 8 天），热了脱下放包里",
    "围巾和披肩：浅灰围巾（第 2 天）、米色围巾（第 4 天）、灰色披肩（第 5 天）、奶白羊毛披肩（第 6 天，汉服时用），每天都带一条，早晚温差大",
    "裙装：第 5 天雾粉百褶裙，里面一定穿保暖打底裤；汉服在第 2、6 天，里面穿保暖贴身衣",
    "雨具：一次性雨披或折叠伞，3 月华东多细雨，迪士尼和西湖都用得上",
    "长裤 4 条：直筒牛仔裤、黑色高腰直筒裤、米白直筒裤、深灰蓝直筒裤；薄毛衣和长袖打底各带 3–4 件，叠穿不显臃肿",
    "第 8 天去寺庙，肩膀手臂和腿都要遮住，不穿短裤、吊带",
]
NOTE = ("按女生 170 cm 的身材写，外套长度和裤型是通用的比例建议，随个人腿长和肩宽微调；气温是按往年 3 月上中旬估的，不是预报，出发前一周再看各城市实际天气；"
        "每天的人物图是 AI 生成的示意图，不是实拍；第 6 天汉服是在乌镇半城红妆店租的，实际款式以店里为准。")

CSS = """
#panel-outfit .of-card{background:var(--surface,#fff);border:1px solid var(--line);border-radius:14px;padding:14px;margin-bottom:6px}
#panel-outfit .of-meta{color:var(--ink-soft);font-size:12.5px;margin:0 0 10px}
#panel-outfit .of-shots{display:flex;gap:10px;margin:0 0 12px}
#panel-outfit .of-shots figure{margin:0;flex:1 1 0;min-width:0}
#panel-outfit .of-shots-1 figure{flex:0 1 320px}
#panel-outfit .of-shots img{width:100%;height:auto;display:block;border-radius:10px;border:1px solid var(--line)}
#panel-outfit .of-shots figcaption{font-size:12.5px;font-weight:600;color:var(--ink-soft);margin-top:6px}
#panel-outfit .of-looks{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:12px}
#panel-outfit .of-item{background:var(--surface-2,#f4f4f4);border-radius:10px;padding:10px 11px}
#panel-outfit .of-item:last-child:nth-child(odd){grid-column:1/-1}
#panel-outfit .of-sw{width:20px;height:20px;border-radius:6px;border:1px solid rgba(0,0,0,.12);margin-bottom:6px}
#panel-outfit .of-cat{font-size:12.5px;color:var(--ink-soft);margin-bottom:2px}
#panel-outfit .of-desc{font-size:14px;font-weight:500;line-height:1.55}
#panel-outfit .of-pal{display:flex;height:8px;border-radius:4px;overflow:hidden;margin-bottom:12px;border:1px solid var(--line)}
#panel-outfit .of-pal span{flex:1}
#panel-outfit .of-tip{font-size:14px;color:var(--ink-soft);border-left:3px solid #FE9677;padding-left:12px;margin:0}
#panel-outfit .of-pack ul{margin:6px 0 0;padding-left:18px;font-size:14px;color:var(--ink-soft)}
#panel-outfit .of-pack li{margin-bottom:6px}
#panel-outfit .of-note{font-size:12.5px;color:var(--ink-soft);margin:14px 0 0}
@media (max-width:420px){#panel-outfit .of-looks{grid-template-columns:1fr}}
"""


KEEP_ORIGINAL = {"day05"}  # shown at its original 896x1200 size


def photo(stem):
    OUT_IMG.mkdir(parents=True, exist_ok=True)
    src = next(p for p in (HERE / "outfit_images").glob(stem + ".*"))
    im = Image.open(src).convert("RGB")
    if stem not in KEEP_ORIGINAL:
        im.thumbnail((720, 1080))
    im.save(OUT_IMG / f"{stem}.jpg", "JPEG", quality=82, optimize=True)
    return f"images/outfit/{stem}.jpg"


def shots_html(shots):
    figs = "".join(
        f'<figure><img src="{photo(s)}" alt="{html.escape(cap or "当天穿搭示意图")}" loading="lazy">'
        + (f"<figcaption>{html.escape(cap)}</figcaption>" if cap else "") + "</figure>"
        for s, cap in shots)
    return f'<div class="of-shots of-shots-{len(shots)}">{figs}</div>'


LABEL = {d["day"]: d["label"] for d in json.loads((HERE.parent / "trip_data.json").read_text(encoding="utf-8"))["days"]}
secs = []
for n, date, title, meta, looks, pal, tip, shots in DAYS:
    k = int(n)
    items = "".join(
        f'<div class="of-item"><div class="of-sw" style="background:{c}"></div>'
        f'<div class="of-cat">{html.escape(cat)}</div><div class="of-desc">{html.escape(d)}</div></div>'
        for cat, d, c in looks)
    bar = "".join(f'<span style="background:{c}"></span>' for c in pal)
    mm, dd = date.split("/")
    secs.append(
        f'<p class="day-head" id="outfit-day-{k}">第{k}天 · {int(mm):02d}/{int(dd):02d} · {html.escape(LABEL.get(k, title))}</p>'
        f'<div class="of-card"><p class="of-meta">{html.escape(meta)}</p>{shots_html(shots)}'
        f'<div class="of-looks">{items}</div><div class="of-pal">{bar}</div><p class="of-tip">{html.escape(tip)}</p></div>')
pack = "".join(f"<li>{html.escape(x)}</li>" for x in PACK)
frag = (f"<style>{CSS}</style>" + "".join(secs)
        + f'<p class="day-head">打包建议</p><div class="of-card of-pack"><ul>{pack}</ul></div>'
        + f'<p class="of-note">{html.escape(NOTE)}</p>')
(HERE / "outfit_panel.html").write_text(frag, encoding="utf-8")
print("saved outfit/outfit_panel.html", len(frag))
