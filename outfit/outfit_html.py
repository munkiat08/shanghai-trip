# -*- coding: utf-8 -*-
"""Standalone outfit page: public/outfit.html (+ compressed photos in public/images/outfit/).
Run from anywhere:  python outfit/outfit_html.py
Photos come from outfit/outfit_images/ (originals, any format); each is resized to 720 px wide JPEG."""
import html
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
:root{--paper:#E9E7EF;--panel:#F8F6F9;--ink:#1E1E33;--ink-soft:#5C5B75;--line:#D8D4E0;--accent:#984063;--accent-ink:#7A3050;--accent-soft:#FDE8E0;--sky:#41436A;--coral:#F64668;--peach:#FE9677;color-scheme:light}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font:14px 'Manrope',-apple-system,'PingFang SC','Microsoft YaHei',sans-serif;padding:0 16px;line-height:1.7}
.wrap{max-width:640px;margin:0 auto;padding-block:28px 60px}
.serif{font-family:'Noto Serif SC','Songti SC',serif}.mono{font-family:'IBM Plex Mono',ui-monospace,monospace}
.back{display:inline-block;margin-bottom:10px;font-size:13px;font-weight:600;color:var(--sky);text-decoration:none}
.hero{padding-block:8px 20px;border-bottom:2px solid var(--peach);margin-bottom:18px}
.eyebrow{font-size:12px;letter-spacing:.12em;color:var(--accent);font-weight:600;text-transform:uppercase}
.hero h1{font-size:30px;font-weight:700;margin:10px 0 8px;color:var(--accent-ink);text-wrap:balance}.hero p{color:var(--ink-soft);font-size:14px;margin:0}
.navrow{position:sticky;top:0;display:flex;gap:8px;overflow-x:auto;padding:10px 0;margin:0 0 22px;background:var(--paper);border-bottom:1px solid var(--line);z-index:5;-webkit-overflow-scrolling:touch}
.navrow a{flex:0 0 auto;font-family:'IBM Plex Mono',monospace;font-size:12px;font-weight:600;color:var(--ink-soft);background:var(--panel);border:1px solid var(--line);border-radius:999px;padding:7px 14px;text-decoration:none;white-space:nowrap}
.navrow a:hover{color:#fff;background:var(--sky);border-color:var(--sky)}
.day{margin-bottom:44px;scroll-margin-top:56px}
.day-head{display:flex;align-items:baseline;gap:14px;margin-bottom:4px;flex-wrap:wrap}
.day-num{font-size:34px;font-weight:600;color:var(--coral);line-height:1}.day-title{font-size:20px;font-weight:700;flex:1 1 auto;min-width:0;margin:0}
.day-meta{color:var(--ink-soft);font-size:12px;margin:0 0 16px}
.shots{display:flex;gap:10px;margin:0 0 14px}.shots figure{margin:0;flex:1 1 0;min-width:0}.shots-1 figure{flex:0 1 320px}.shots img{width:100%;height:auto;display:block;border-radius:10px;border:1px solid var(--line)}.shots figcaption{font:600 11px 'IBM Plex Mono',monospace;color:var(--ink-soft);margin-top:6px}
.looks{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:14px}
.look-item{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:12px 12px 11px}
.look-item:last-child:nth-child(odd){grid-column:1/-1}
.swatch{width:22px;height:22px;border-radius:6px;border:1px solid rgba(0,0,0,.12);margin-bottom:8px}
.look-cat{font-family:'IBM Plex Mono',monospace;font-size:11px;letter-spacing:.08em;color:var(--ink-soft);margin-bottom:3px}
.look-desc{font-size:13px;font-weight:500}
.palette{display:flex;height:8px;border-radius:4px;overflow:hidden;margin-bottom:16px;border:1px solid var(--line)}.palette span{flex:1}
.tip{font-family:'Noto Serif SC',serif;font-size:14px;color:var(--ink-soft);border-left:3px solid var(--peach);padding-left:12px;margin:0}
.pack{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:20px;margin-top:8px}
.pack h2{font-size:16px;margin:0 0 10px;color:var(--accent-ink)}.pack ul{margin:0;padding-left:18px;font-size:14px;color:var(--ink-soft)}.pack li{margin-bottom:6px}
.note{font-size:12px;color:var(--ink-soft);margin-top:28px;padding-top:16px;border-top:1px solid var(--line)}
@media (max-width:420px){.looks{grid-template-columns:1fr}.hero h1{font-size:26px}}
"""


def photo(stem):
    OUT_IMG.mkdir(parents=True, exist_ok=True)
    src = next(p for p in (HERE / "outfit_images").glob(stem + ".*"))
    im = Image.open(src).convert("RGB")
    im.thumbnail((720, 1080))
    im.save(OUT_IMG / f"{stem}.jpg", "JPEG", quality=82, optimize=True)
    return f"images/outfit/{stem}.jpg"


def shots_html(shots):
    figs = "".join(
        f'<figure><img src="{photo(s)}" alt="{html.escape(cap or "当天穿搭示意图")}" loading="lazy">'
        + (f"<figcaption>{html.escape(cap)}</figcaption>" if cap else "") + "</figure>"
        for s, cap in shots)
    return f'<div class="shots shots-{len(shots)}">{figs}</div>'


nav = "".join(f'<a href="#day{n}">第{int(n)}天 {d}</a>' for n, d, *_ in DAYS)
secs = []
for n, date, title, meta, looks, pal, tip, shots in DAYS:
    items = "".join(
        f'<div class="look-item"><div class="swatch" style="background:{c}"></div>'
        f'<div class="look-cat">{html.escape(cat)}</div><div class="look-desc">{html.escape(d)}</div></div>'
        for cat, d, c in looks)
    bar = "".join(f'<span style="background:{c}"></span>' for c in pal)
    secs.append(
        f'  <section class="day" id="day{n}">\n'
        f'    <div class="day-head"><span class="day-num mono">{n}</span><h2 class="day-title serif">{html.escape(title)}</h2></div>\n'
        f'    <p class="day-meta mono">{date} · {html.escape(meta)}</p>\n'
        f'    {shots_html(shots)}\n'
        f'    <div class="looks">{items}</div>\n'
        f'    <div class="palette">{bar}</div>\n'
        f'    <p class="tip">{html.escape(tip)}</p>\n'
        f'  </section>')
pack = "".join(f"<li>{html.escape(x)}</li>" for x in PACK)
page = (
    '<!doctype html><html lang="zh"><head><meta charset="utf-8">'
    '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><title>上海苏州乌镇杭州九日穿搭</title>\n'
    '<meta name="theme-color" content="#41436A">\n'
    '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@600;700&family=Manrope:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500;600&display=swap" rel="stylesheet">\n'
    f"<style>{CSS}</style></head><body>\n<div class=\"wrap\">\n"
    '  <a class="back" href="./">← 返回行程</a>\n'
    '  <div class="hero"><div class="eyebrow">Shanghai · Suzhou · Wuzhen · Hangzhou · March OOTD</div>\n'
    '    <h1 class="serif">上海苏州乌镇杭州 九日穿搭</h1>\n'
    "    <p>女生 170 cm · 3/8–3/16 · 早晚凉、多细雨 · 拍照出片 —— 按往年气候估计，不是预报，出发前一周再看实际天气</p></div>\n"
    f'  <nav class="navrow">{nav}</nav>\n' + "\n".join(secs) + "\n"
    f'  <div class="pack"><h2 class="serif">打包建议</h2><ul>{pack}</ul></div>\n'
    f'  <p class="note">{NOTE}</p>\n</div></body></html>')
(PUB / "outfit.html").write_text(page, encoding="utf-8")
print("saved public/outfit.html", len(page))
