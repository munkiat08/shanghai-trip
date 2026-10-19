# -*- coding: utf-8 -*-
"""上海 trip: trip_data.json (master, all details)  <->  simple Excel  ->  HTML.

  python excel_tool.py export            # trip_data.json -> trip.xlsx   (edit this file)
  python excel_tool.py import [xlsx]     # merge Excel edits into trip_data.json
  python excel_tool.py build  [xlsx]     # merge, then build itinerary/shanghai-itinerary.html (+ copy to C:\\claude)

The Excel has two sheets and only these columns:
  行程: 天 | 时间 | 地点        (every stop, hotel check-in/out and 回酒店 rows included)
  美食: 天 | 地点              (food / snack / drink / coffee places of each day)
Everything else (tips, transit text, Amap / RedNote / Trip.com links, notes, sights) stays in trip_data.json
and is re-attached by place name:
  * same place name          -> all its details are kept, only time / order / day change
  * new or renamed place     -> a stub with an Amap search link; the tool lists them so details can be filled in
  * route button of a stop   -> rebuilt from the previous place -> this place when the previous place changed
    (its minutes text is then marked as unverified)
The previous trip_data.json is saved as trip_data.bak.json before it is overwritten.
"""
import copy, datetime, json, shutil, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = Path.home() / ".claude" / "skills" / "china-amap-rednote-itinerary" / "scripts"
sys.path.insert(0, str(SKILL))
from amap_links import search_url, route_url, parse_marker_coords  # noqa: E402
from openpyxl import Workbook, load_workbook  # noqa: E402
from openpyxl.styles import Alignment, Font, PatternFill  # noqa: E402

DATA = HERE / "trip_data.json"
XLSX = HERE / "trip.xlsx"
OUT = HERE / "itinerary" / "shanghai-itinerary.html"
COPY_TO = None  # everything stays inside the repo folder
ROUTE_MODE = {"taxi": "car", "drive": "car", "transit": "bus", "train": "bus", "walk": "walk", "bike": "ride"}
STALE = "⚠️上一站已改,用时未重新核实:"
CITY = {1: "上海", 2: "上海", 3: "上海", 4: "苏州", 5: "苏州", 6: "嘉兴", 7: "杭州", 8: "杭州", 9: "杭州"}  # day -> city for Amap search stubs


def coords(url):
    try:
        return parse_marker_coords(url) if url else None
    except Exception:
        return None


def merged(day):
    """Chronological entries; the stay is slotted in by its time (same rule as the HTML page)."""
    stay, stops = day["stay"], day["stops"]
    ent = [("stop", s) for s in stops]
    if not stay.get("time"):
        return [("stay", stay)] + ent
    at = next((i for i, s in enumerate(stops) if s.get("time") and s["time"] > stay["time"]), len(stops))
    return ent[:at] + [("stay", stay)] + ent[at:]


def tstr(v):
    if v is None:
        return ""
    if isinstance(v, (datetime.time, datetime.datetime)):
        return v.strftime("%H:%M")
    if isinstance(v, float):  # Excel day-fraction
        m = round(v * 24 * 60)
        return f"{m // 60:02d}:{m % 60:02d}"
    return str(v).strip()


def fmt_date(iso):
    y, m, d = iso.split("-")
    return f"{m}/{d}/{y}"


def day_of(v, d):
    """Excel 日期 cell (text 11/23/2026, a real date, or ISO) -> day number of the trip; None if blank/unknown."""
    if v in (None, ""):
        return None
    if isinstance(v, (datetime.datetime, datetime.date)):
        iso = v.strftime("%Y-%m-%d")
    else:
        t = str(v).strip().replace(".", "/").replace("-", "/")
        p = t.split("/")
        if len(p) == 3 and len(p[0]) == 4:
            iso = f"{int(p[0]):04d}-{int(p[1]):02d}-{int(p[2]):02d}"
        elif len(p) == 3:
            iso = f"{int(p[2]):04d}-{int(p[0]):02d}-{int(p[1]):02d}"
        else:
            return None
    return next((x["day"] for x in d["days"] if x["date"] == iso), None)


def _style(ws, widths, center_cols=()):
    for c in ws[1]:
        c.fill, c.font = PatternFill("solid", fgColor="8C231C"), Font(bold=True, color="FFFFFF")
    for col, w in zip("ABCDE", widths):
        ws.column_dimensions[col].width = w
    for row in ws.iter_rows(min_row=2):
        for i in center_cols:
            row[i].number_format = "@"
            row[i].alignment = Alignment(horizontal="center")
    ws.freeze_panes = "A2"


def export():
    d = json.load(open(DATA, encoding="utf-8"))
    wb = Workbook()
    ws = wb.active
    ws.title = "行程"
    ws.append(["日期", "时间", "地点"])
    for day in d["days"]:
        for _, e in merged(day):
            ws.append([fmt_date(day["date"]), e.get("time", ""), e["name"]])
    _style(ws, (12, 9, 70), center_cols=(0, 1))
    wf = wb.create_sheet("美食")
    wf.append(["日期", "地点"])
    for f in sorted(d["food"], key=lambda x: x.get("day") or 99):
        dd = next((x["date"] for x in d["days"] if x["day"] == f.get("day")), "")
        wf.append([fmt_date(dd) if dd else "", f["name"]])
    _style(wf, (12, 70), center_cols=(0,))
    note = wb.create_sheet("说明")
    for line in ["【行程】每行 = 一个时间点：日期(如 11/23/2026，11/23/2026–11/30/2026)、时间(如 09:30)、地点。",
                 "改时间/顺序/删行/增行 = 直接改；地点名保持原样就会带上原来的全部资料(提示、链接、路线)。",
                 "同一天里的行会按时间自动排序；时间留空的行(如「今晚住」)排在当天最前面。",
                 "酒店入住/退房/回酒店也在表里(名称里带「回酒店」的是每天最后一站)。",
                 "【美食】每行 = 一个餐厅/小吃/饮料/咖啡地点，填它属于哪一天(日期)。换食物 = 改地点名或删行/加行。",
                 "新增或改名的地点没有资料，交回来后我会用高德/小红书补上坐标、提示和链接。"]:
        note.append([line])
    note.column_dimensions["A"].width = 110
    wb.save(XLSX)
    print("wrote", XLSX, f"(行程 {ws.max_row - 1} 行, 美食 {wf.max_row - 1} 行)")


def merge(xlsx):
    d = json.load(open(DATA, encoding="utf-8"))
    wb = load_workbook(xlsx, data_only=True)

    # ------------------------------- 行程 -------------------------------
    rows = {}
    for r in wb["行程"].iter_rows(min_row=2, values_only=True):
        if not r or r[0] in (None, "") or not (r[2] and str(r[2]).strip()):
            continue
        dn = day_of(r[0], d)
        if dn is None:
            print("⚠️ 日期无法识别，已跳过:", r[0], r[2])
            continue
        rows.setdefault(dn, []).append((tstr(r[1]), str(r[2]).strip()))

    pool = {}
    for day in d["days"]:
        prev = None
        for kind, e in merged(day):
            pool.setdefault(e["name"], []).append((kind, copy.deepcopy(e), day["day"], prev))
            prev = e["name"]

    new_places, changed_legs, warnings = [], [], []
    for day in d["days"]:
        n = day["day"]
        stay, stops = None, []
        for t, name in rows.get(n, []):
            hit = pool.get(name)
            if hit:
                i = next((k for k, x in enumerate(hit) if x[2] == n), 0)
                kind, e, _, oldprev = hit.pop(i)
                e["time"] = t
                if not t:
                    e.pop("time", None)
                if kind == "stay":
                    stay = e
                else:
                    stops.append((e, oldprev))
            else:
                e = {"time": t, "name": name, "en": "", "amap": search_url(name, CITY.get(n, "")), "rednote": "", "tip": ""}
                stops.append((e, None))
                new_places.append(f"第{n}天 {t} {name}")
        if stay is None:
            warnings.append(f"第{n}天的住宿行(酒店入住/退房)被删了,已保留原来的")
            stay = day["stay"]
        stops.sort(key=lambda x: x[0].get("time") or "")  # stable
        ordered = merged({"stay": stay, "stops": [s for s, _ in stops]})
        prevname, prevc = None, None
        oldprev = {id(s): p for s, p in stops}
        for kind, e in ordered:
            c = coords(e.get("amap"))
            if kind == "stop":
                tr = e.get("transit")
                if tr and tr.get("mode") in ROUTE_MODE and prevname is not None:
                    if oldprev.get(id(e)) != prevname:
                        if prevc and c:
                            tr["amap"] = route_url(prevc, c, mode=ROUTE_MODE[tr["mode"]], dest_name=e["name"])
                            if not tr.get("detail", "").startswith(STALE):
                                tr["detail"] = STALE + tr.get("detail", "")
                        else:
                            tr.pop("amap", None)
                        changed_legs.append(f"第{n}天 {prevname} → {e['name']}")
            prevname, prevc = e["name"], c if c else prevc
        day["stay"], day["stops"] = stay, [s for s, _ in stops]
    dropped = [f"第{x[2]}天 {name}" for name, lst in pool.items() for x in lst if x[0] == "stop"]

    # ------------------------------- 美食 -------------------------------
    new_food, dropped_food = [], []
    if "美食" in wb.sheetnames:
        fpool = {}
        for f in d["food"]:
            fpool.setdefault(f["name"], []).append(f)
        food = []
        for r in wb["美食"].iter_rows(min_row=2, values_only=True):
            if not r or not (len(r) > 1 and r[1] and str(r[1]).strip()):
                continue
            day = day_of(r[0], d)
            name = str(r[1]).strip()
            hit = fpool.get(name)
            if hit:
                f = hit.pop(0)
                f["day"] = day
            else:
                f = {"name": name, "en": "", "day": day, "amap": search_url(name, CITY.get(day or 0, "")), "rednote": "", "note": ""}
                new_food.append(f"第{day}天 {name}")
            food.append(f)
        dropped_food = [f"第{f.get('day')}天 {n}" for n, lst in fpool.items() for f in lst]
        d["food"] = food

    shutil.copyfile(DATA, HERE / "trip_data.bak.json")
    json.dump(d, open(DATA, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("merged ->", DATA)
    for title, lst in (("新增/改名的行程地点(需要补资料)", new_places), ("路线已重建、用时待核实", changed_legs),
                       ("从行程里删掉的地点", dropped), ("新增/改名的美食(需要补资料)", new_food),
                       ("从美食里删掉的地点", dropped_food), ("提醒", warnings)):
        if lst:
            print(f"\n{title}:")
            for x in lst:
                print("  -", x)


def build(xlsx):
    merge(xlsx)
    OUT.parent.mkdir(exist_ok=True)
    subprocess.check_call([sys.executable, str(SKILL / "build_itinerary_html.py"), str(DATA), str(OUT)])
    print("built", OUT)


if __name__ == "__main__":
    a = sys.argv[1:]
    cmd = a[0] if a else ""
    x = Path(a[1]) if len(a) > 1 else XLSX
    if cmd == "export":
        export()
    elif cmd == "import":
        merge(x)
    elif cmd == "build":
        build(x)
    else:
        print(__doc__)
