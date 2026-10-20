"""Build the MAIN page: itinerary/shanghai-itinerary-palette.html.

Run after editing trip_data.json:  python theme_palette.py  (writes the itinerary/ copy AND public/index.html)
It builds the page from trip_data.json (into a temp file), recolours it with the reference palette
(colours plus a readability pass: type floor, line-height, tap targets, spacing) and writes the palette page.
itinerary/shanghai-itinerary.html is the earlier design and is NOT touched any more.
Palette: #41436A indigo, #984063 plum, #F64668 coral, #FE9677 peach.
"""
import io
import re
import os
import subprocess
import sys
import tempfile

BUILDER = os.path.expanduser("~/.claude/skills/china-amap-rednote-itinerary/scripts/build_itinerary_html.py")
SRC = None  # filled by build()
OUT = "itinerary/shanghai-itinerary-palette.html"

CSS = r"""
  /* palette recolour: #41436A / #984063 / #F64668 / #FE9677 — colours only */
  body.theme-ink, :root{
    --bg:#e9e7ef; --surface:#f8f6f9; --surface-2:#efecf3; --line:#d8d4e0;
    --ink:#1e1e33; --ink-soft:#5c5b75; --shadow:rgba(65,67,106,.18);
    --accent:#984063; --accent-soft:#fde8e0; --accent-ink:#7a3050;
    --jade:#41436A; --jade-soft:#e0e0ec; --jade-ink:#33355a;
    --amap-bg:#41436A; --amap-ink:#f0f0f7;
    --rn-bg:#984063; --rn-ink:#fff5f8;
    --tc-bg:#6b6a8c; --tc-ink:#ffffff;
    --gold:#F64668; --gold-soft:#fde3e8; --gold-ink:#a8203f;
  }
  body.theme-ink .tag, body.theme-ink .tag.day, body.theme-ink .tag.optional, body.theme-ink .badge.optional,
  body.theme-ink #panel-food .tag{background:#6b6a8c; color:#ffffff}  /* time / 备选 / food category: same as the Trip.com button */
  body.theme-ink .catnav a{background:#6b6a8c; border-color:#6b6a8c; color:#ffffff}
  body.theme-ink .daychip[aria-selected="true"], body.theme-ink .foodnav-btn[aria-current="true"],
  body.theme-ink .mapchip[aria-selected="true"]{background:#41436A; border-color:#41436A; color:#ffffff}
  body.theme-ink .tab[aria-selected="true"]{color:#41436A}
  body.theme-ink .head{border-bottom-color:#FE9677}
  body.theme-ink .tip{border-left-color:#FE9677}
  body.theme-ink .pin, body.theme-ink .maplist .n{background:#41436A !important}
  body.theme-ink .pin.hotel, body.theme-ink .maplist .n.hotel{background:#F64668 !important}
  body.theme-ink .amap-btn.rn{max-width:100%; text-align:left}  /* long post titles wrap instead of overflowing */
  body.theme-ink path.leaflet-interactive{stroke:#F64668 !important}
  /* readability pass */
  body.theme-ink{line-height:1.7}  /* 1. roomier lines for CJK text */
  body.theme-ink .badge, body.theme-ink .tag, body.theme-ink .img-credit, body.theme-ink .rt-chip, body.theme-ink .mapnote,
  body.theme-ink .maplist .nm em, body.theme-ink .tip .src, body.theme-ink .note-text .src, body.theme-ink .amap-btn,
  body.theme-ink .tip .amap-btn, body.theme-ink .group-head .amap-btn, body.theme-ink .maplist a{font-size:12.5px}  /* 2. no text under 12.5px */
  body.theme-ink .rt-time, body.theme-ink .rt-zone-h, body.theme-ink .stop-time, body.theme-ink .img-credit, body.theme-ink .rt-chip{color:#7a3050; border-color:#7a3050}  /* 3. time/credit text had ~4:1 contrast */
  body.theme-ink .head h1{font-family:'LXGW WenKai','Noto Serif SC',serif; font-weight:700; letter-spacing:.02em}  /* 4. plain bold title, readable */
  body.theme-ink .day-head, body.theme-ink .maptitle{font-family:'LXGW WenKai','Noto Serif SC',serif; font-weight:700}
  body.theme-ink .tip{line-height:1.75; padding:11px 13px}
  body.theme-ink .timeline{gap:20px}  /* 5. air between stops, softer cards */
  body.theme-ink .stop{padding:13px 15px 15px; border-color:transparent; box-shadow:0 1px 3px var(--shadow)}
  @media (max-width:719px){
    body.theme-ink .head .sub{white-space:normal; overflow:visible; font-size:12.5px; line-height:1.5}  /* trip dates/flights no longer cut off */
    body.theme-ink .daychip{min-height:38px; padding:7px 14px; font-size:13px}  /* thumb-sized chips */
    body.theme-ink .amap-btn, body.theme-ink .maplist a{min-height:34px; display:inline-flex; align-items:center}
    body.theme-ink .tip .amap-btn, body.theme-ink .group-head .amap-btn{min-height:0}
    body.theme-ink .maplist li{padding:3px 0}
  }

  body.theme-ink .panels{background-image:url("data:image/svg+xml,%3Csvg%20xmlns=%27http://www.w3.org/2000/svg%27%20width=%27260%27%20height=%27260%27%20viewBox=%270%200%20260%20260%27%20fill=%27none%27%20stroke=%27%2341436A%27%20stroke-width=%271.6%27%20stroke-linecap=%27round%27%20stroke-linejoin=%27round%27%3E%3Cg%20opacity=%27.12%27%3E%3Cg%20transform=%27translate(48%2056)%27%3E%3C%21--%20Oriental%20Pearl%20Tower%20--%3E%3Cpath%20d=%27M0%20-50V30%27/%3E%3Ccircle%20cx=%270%27%20cy=%27-22%27%20r=%275%27/%3E%3Ccircle%20cx=%270%27%20cy=%270%27%20r=%279%27%20fill=%27%2341436A%27%20fill-opacity=%27.25%27/%3E%3Ccircle%20cx=%270%27%20cy=%2722%27%20r=%275%27/%3E%3Cpath%20d=%27M-12%2044L-2%2028M12%2044L2%2028M0%2028V44%27/%3E%3C/g%3E%3Cg%20transform=%27translate(190%2056)%27%3E%3C%21--%20xiaolongbao%20--%3E%3Cpath%20d=%27M-20%206Q-22%20-14%200%20-16Q22%20-14%2020%206Q0%2014%20-20%206Z%27%20fill=%27%2341436A%27%20fill-opacity=%27.12%27/%3E%3Cpath%20d=%27M0%20-16V-8M-8%20-14L-5%20-6M8%20-14L5%20-6M-14%20-10L-9%20-3M14%20-10L9%20-3%27/%3E%3Cpath%20d=%27M-8%20-26q-4%20-5%200%20-9M2%20-26q-4%20-5%200%20-9M12%20-26q-4%20-5%200%20-9%27/%3E%3C/g%3E%3Cg%20transform=%27translate(52%20184)%27%3E%3C%21--%20Lujiazui:%20Jin%20Mao%20%2B%20SWFC%20--%3E%3Cpath%20d=%27M-30%2034V-10H-18V-18H-10V-28H-4V34M-30%2034H0%27/%3E%3Cpath%20d=%27M10%2034V-26L24%20-34L30%20-26V34Z%27/%3E%3Cpath%20d=%27M17%20-14L23%20-14L20%20-4Z%27%20fill=%27%2341436A%27%20fill-opacity=%27.3%27/%3E%3C/g%3E%3Cg%20transform=%27translate(190%20180)%27%3E%3C%21--%20Yuyuan%20roof%20--%3E%3Cpath%20d=%27M-30%20-4Q-14%20-2%20-6%20-16Q0%20-24%206%20-16Q14%20-2%2030%20-4%27/%3E%3Cpath%20d=%27M-24%20-2V22H24V-2%27/%3E%3Cpath%20d=%27M-6%2022V8H6V22M-24%2012h12M12%2012h12%27/%3E%3C/g%3E%3C/g%3E%3Cg%20opacity=%27.12%27%20transform=%27translate(130%20130)%27%3E%3C%21--%20yulan%20magnolia%20--%3E%3Cpath%20d=%27M0%206C-8%20-2%20-6%20-14%200%20-18C6%20-14%208%20-2%200%206ZM-3%206C-14%204%20-16%20-6%20-12%20-12C-6%20-8%20-2%20-2%20-3%206ZM3%206C14%204%2016%20-6%2012%20-12C6%20-8%202%20-2%203%206Z%27/%3E%3C/g%3E%3C/svg%3E"); background-size:260px 260px; background-repeat:repeat}

  body.theme-ink .tabbar, .tabbar{grid-template-columns:repeat(5,1fr)}  /* 行程 美食 景点 穿搭 注意事项 */
"""

def prune_css(html):
    """Drop CSS rules whose classes/ids appear nowhere in the page (HTML + scripts). Leaflet's own stylesheet and
    any leaflet-* class (created by the library at run time) are left alone."""
    src = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.S)

    def present(tok):
        name = tok[1:]
        return name.startswith("leaflet") or re.search(r"(?<![\w-])" + re.escape(name) + r"(?![\w-])", src) is not None

    def rules(css):
        out, i = [], 0
        while True:
            j = css.find("{", i)
            if j < 0:
                break
            sel, depth, k = css[i:j].strip(), 1, j + 1
            while depth and k < len(css):
                depth += (css[k] == "{") - (css[k] == "}")
                k += 1
            out.append((sel, css[j + 1:k - 1]))
            i = k
        return out

    def keep(sel):
        toks = re.findall(r"[.#][\w-]+", re.sub(r"\[[^\]]*\]|:[\w-]+(\([^)]*\))?", "", sel))
        return all(present(t) for t in toks)

    def prune_block(css):
        res = []
        for sel, body in rules(css):
            if sel.startswith("@media") or sel.startswith("@supports"):
                inner = prune_block(body)
                if inner.strip():
                    res.append(sel + "{" + inner + "}")
            elif sel.startswith("@"):
                res.append(sel + "{" + body + "}")
            else:
                parts = [p.strip() for p in sel.split(",") if keep(p.strip())]
                if parts:
                    res.append(",".join(parts) + "{" + body + "}")
        return chr(10).join(res)

    def fix(m):
        css = m.group(2)
        if "leaflet-container{" in css.replace(" ", "") and ".leaflet-pane" in css:
            return m.group(0)  # the Leaflet library stylesheet itself
        css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
        return m.group(1) + prune_block(css) + m.group(3)

    return re.sub(r"(<style[^>]*>)(.*?)(</style>)", fix, html, flags=re.S)

V2_CSS = r"""
  /* v2 — 1. hierarchy */
  body.theme-ink .stop-time{font-size:13px; font-weight:700; color:var(--jade-ink); letter-spacing:.02em}
  body.theme-ink .stop-name{font-size:18px; line-height:1.4; cursor:pointer}
  body.theme-ink .stop-time{cursor:pointer}
  body.theme-ink .stop-time::after{content:"▾"; margin-left:auto; font-size:13px; color:var(--ink-soft); font-weight:400}
  body.theme-ink .stop.open .stop-time::after{content:"▴"}
  body.theme-ink .stop-name .en{display:block; margin:2px 0 0; font-size:12.5px; font-weight:400}
  body.theme-ink .stop:not(.open) .tip{display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden}
  body.theme-ink .stop:not(.open) .row-actions .amap-btn.rn{display:none}
  /* v2 — 2. calm cards, more air */
  body.theme-ink .panels{padding:20px 22px 104px}
  body.theme-ink .timeline{gap:28px}
  body.theme-ink .stop{background:transparent; box-shadow:none; border:0; border-bottom:1px solid var(--line); border-radius:0; padding:2px 0 22px}
  body.theme-ink .tip{background:transparent; border-left:3px solid var(--line); border-radius:0; padding:2px 0 2px 12px; margin-top:8px}
  body.theme-ink .stop-img{border-radius:10px; margin-top:10px}
  body.theme-ink .row-actions{margin-top:12px; gap:10px}
  body.theme-ink .leg{font-size:12.5px; padding-top:6px; padding-bottom:6px}
  /* v2 — 3. bold sans headings over kai body */
  body.theme-ink h1, body.theme-ink .head h1, body.theme-ink .day-head, body.theme-ink .maptitle, body.theme-ink .stop-name{
    font-family:'PingFang SC','Microsoft YaHei','Noto Sans SC','Helvetica Neue',sans-serif; font-weight:700}
  body.theme-ink .day-head{font-size:19px; margin:26px 0 12px}
"""
V2_JS = """<script>document.addEventListener('click',e=>{const n=e.target.closest('.stop-name,.stop-time');if(n)n.closest('.stop').classList.toggle('open')})</script>"""

V2_JS += r"""<script>(function(){
  var COL=['#b8402f','#2b6f5e','#3a5f9c','#7a3d8f','#c26a1b'], LF=window.L, built=false;
  var pos=function(u){var m=(u||'').match(/position=([\d.]+)(?:%2C|,)([\d.]+)/);return m?[+m[1],+m[2]]:null;};
  function build(){
    if(built||!LF||!LF.map) return; built=true;
    document.querySelectorAll('#panel-sights .day-head[id^="sight-day-"]').forEach(function(h){
      var d=TRIP.days.find(function(x){return 'sight-day-'+x.day===h.id;}); if(!d) return;
      var i=TRIP.days.indexOf(d), c=COL[i%COL.length], n=0;
      var pts=d.stops.map(function(s){return {s:s,ll:pos(s.amap)};}).filter(function(p){return p.ll;});
      if(!pts.length) return;
      var t=document.createElement('div'); t.className='maptitle'; t.textContent=dayLabel(d.day)+' 路线地图'; h.insertAdjacentElement('afterend',t);
      var el=document.createElement('div'); el.className='daymini'; t.insertAdjacentElement('afterend',el);
      var m=LF.map(el,{zoomControl:false,attributionControl:false});
      LF.tileLayer('https://webrd0{s}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}',{subdomains:'1234',maxZoom:18}).addTo(m);
      LF.polyline(pts.map(function(p){return [p.ll[1],p.ll[0]];}),{color:c,weight:3,opacity:.75,dashArray:'6 6'}).addTo(m);
      pts.forEach(function(p){var hotel=!!(p.s.isStay||p.s.tripcom); if(!hotel) n++;
        LF.marker([p.ll[1],p.ll[0]],{icon:LF.divIcon({className:'',html:'<div class="pin'+(hotel?' hotel':'')+'" style="background:'+c+'">'+(hotel?'宿':n)+'</div>',iconSize:[24,24],iconAnchor:[12,12]})}).addTo(m);});
      m.fitBounds(pts.map(function(p){return [p.ll[1],p.ll[0]];}),{padding:[20,20],maxZoom:15});
      el._m=m; el._b=pts.map(function(p){return [p.ll[1],p.ll[0]];});
      var esc2=function(x){return String(x==null?'':x).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});};
      var k=0, li=pts.map(function(p){var s=p.s, hotel=!!(s.isStay||s.tripcom); if(!hotel) k++;
        return '<li><span class="n'+(hotel?' hotel':'')+'" style="background:'+c+'">'+(hotel?'宿':k)+'</span><span class="t">'+esc2(s.time)+'</span><span class="nm">'+esc2(s.name)+(s.optional?'<em>可选</em>':'')+'</span><a href="'+esc2(s.amap)+'" target="_blank" rel="noreferrer">高德</a>'+(s.tripcom?'<a class="tc" href="'+esc2(s.tripcom)+'" target="_blank" rel="noreferrer">Trip.com</a>':'')+'</li>';}).join('');
      var url='https://uri.amap.com/marker?markers='+pts.slice(0,40).map(function(p){return p.ll[0]+','+p.ll[1]+','+encodeURIComponent(String(p.s.name).replace(/[,|]/g,' ').slice(0,28));}).join('|')+'&src=itinerary&coordinate=gaode&callnative=1';
      el.insertAdjacentHTML('afterend','<ul class="maplist">'+li+'</ul><div class="row-actions mapall"><a class="amap-btn" href="'+esc2(url)+'" target="_blank" rel="noreferrer">在高德地图查看当天 '+pts.length+' 个地点</a></div>');
    });
  }
  function fix(){build(); document.querySelectorAll('.daymini').forEach(function(e){if(e._m){e._m.invalidateSize(); e._m.fitBounds(e._b,{padding:[20,20],maxZoom:15});}});}
  document.querySelectorAll('.tab').forEach(function(t){t.addEventListener('click',function(){ if(t.dataset.tab==='sights') setTimeout(function(){fix();},120); });});
})();</script>"""
V2_CSS += """
  body.theme-ink #mapcard{display:none}  /* top all-days map removed; the script still needs it */
  body.theme-ink .daymini+*{}
  body.theme-ink .day-head+.maptitle{font-size:16px; margin:0 0 8px}
  body.theme-ink .daymini{height:210px; border-radius:12px; border:1px solid var(--line); margin:0 0 10px}
  body.theme-ink .maplist{margin-bottom:10px}
"""


def apply_v2(h):
    """Design v2 (readability, per-day maps in 景点, tap-to-expand stops). Runs AFTER prune_css because its classes are added by JS."""
    h = h.replace("</style>\n</head>", "</style>\n<style id=\"v2\">" + V2_CSS + "</style>\n</head>", 1) if '<style id="palette-theme">' in h else h
    h = h.replace("</body>", V2_JS + "\n</body>", 1)
    # map: 行程 -> 景点 (the map script inserts into #panel-itinerary and redraws when that tab opens)
    a = "const panel=document.getElementById('panel-itinerary');"
    assert a in h
    h = h.replace(a, a.replace("panel-itinerary", "panel-sights"), 1)
    b = "t.dataset.tab==='itinerary') setTimeout"
    assert b in h
    h = h.replace(b, "t.dataset.tab==='sights') setTimeout", 1)
    # lighter doodle background: scale the whole SVG's opacity (it is a data-URI, so CSS opacity cannot reach it)
    bg = "%3Csvg xmlns='http://www.w3.org/2000/svg' width='260'"
    assert bg in h
    h = h.replace(bg, bg.replace("xmlns=", "opacity='.7' xmlns=", 1), 1)
    assert 'id="v2"' in h and "classList.toggle('open')" in h
    return h

COVER = """
<div id="cover" role="dialog" aria-label="封面" tabindex="0">
  <img src="images/cover.webp" alt="2027年3月 江浙沪9天 一路往南走，四座城">
  <button type="button" id="cover-go">进入行程 →</button>
</div>
<style>
  #cover{position:fixed; inset:0; z-index:1000; background:#EAE8F2; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:12px; cursor:pointer; transition:opacity .35s ease}
  #cover.hide{opacity:0; pointer-events:none}
  #cover img{max-width:100%; max-height:calc(100dvh - 92px); width:auto; height:auto; object-fit:contain; display:block}
  #cover-go{margin-bottom:calc(8px + env(safe-area-inset-bottom)); border:0; border-radius:999px; background:#F64668; color:#fff; font-weight:700; font-size:16px; font-family:inherit; line-height:1; padding:14px 28px; box-shadow:0 6px 18px rgba(65,67,106,.35); cursor:pointer}
  body.cover-open{overflow:hidden}
</style>
<script>
(function(){
  var c = document.getElementById("cover"); if(!c) return;
  document.body.classList.add("cover-open");
  function close(){ c.classList.add("hide"); document.body.classList.remove("cover-open"); setTimeout(function(){ c.remove(); }, 400); }
  c.addEventListener("click", close);
  document.addEventListener("keydown", function(e){ if(e.key === "Escape" || e.key === "Enter") close(); });
})();
</script>
"""


def add_cover(h):
    """Full-screen cover (public/images/cover.webp) shown on open; tap anywhere / button / Esc / Enter to enter."""
    import re
    m = re.search(r"<body[^>]*>", h)
    assert m
    return h[:m.end()] + COVER + h[m.end():]


def add_outfit_tab(h):
    """穿搭 tab between 景点 and 注意事项: button + panel (outfit/outfit_panel.html) + tab-switch JS patches."""
    frag = io.open("outfit/outfit_panel.html", encoding="utf-8").read()
    btn = '<button type="button" class="tab" data-tab="notes"'
    assert btn in h
    tab = """<button type="button" class="tab" data-tab="outfit" aria-selected="false">
      <svg viewBox="0 0 24 24"><path d="M12 4.5a2 2 0 012 2c0 1.2-2 1.6-2 3.2M12 9.7L3.5 15a1.3 1.3 0 00.7 2.4h15.6a1.3 1.3 0 00.7-2.4L12 9.7z" stroke-linecap="round" stroke-linejoin="round"/></svg>
<span class="tab-label">穿搭</span>
    </button>
    """
    h = h.replace(btn, tab + btn, 1)
    pan = '<section class="panel" id="panel-notes"></section>'
    assert pan in h
    h = h.replace(pan, '<section class="panel" id="panel-outfit">' + frag + "</section>" + chr(10) + "    " + pan, 1)
    for old, new in [
        ('notes: document.getElementById("panel-notes")};', 'notes: document.getElementById("panel-notes"), outfit: document.getElementById("panel-outfit")};'),
        ('cur==="notes" ? "note-day-" : "sight-day-"', 'cur==="notes" ? "note-day-" : cur==="outfit" ? "outfit-day-" : "sight-day-"'),
        ('if(name==="food" || name==="sights" || name==="notes") jump(false);', 'if(name==="food" || name==="sights" || name==="notes" || name==="outfit") jump(false);'),
        ('(cur==="food" || cur==="sights" || cur==="notes")) setTimeout', '(cur==="food" || cur==="sights" || cur==="notes" || cur==="outfit")) setTimeout'),
    ]:
        assert old in h, old
        h = h.replace(old, new, 1)
    return h


tmp = tempfile.NamedTemporaryFile(suffix=".html", delete=False)
tmp.close()
subprocess.run([sys.executable, BUILDER, "trip_data.json", tmp.name], check=True, stdout=subprocess.DEVNULL)
html = io.open(tmp.name, encoding="utf-8").read()
os.remove(tmp.name)
block = '<meta name="theme-color" content="#41436A">\n<style id="palette-theme">' + CSS + "</style>\n</head>"
html = html.replace("</head>", block, 1)
before = len(html)
html = prune_css(html)
print("pruned CSS:", before - len(html), "bytes removed")
html = apply_v2(html)
html = add_outfit_tab(html)
html = add_cover(html)
for out in (OUT, "public/index.html"):
    io.open(out, "w", encoding="utf-8").write(html)
    print("wrote", out, len(html.encode("utf-8")), "bytes")
