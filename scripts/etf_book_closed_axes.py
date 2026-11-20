"""What the select leg's floor has been asked, and answered, along every axis we own.

r1762 built the ruler (the select leg's own MDE80 at the 5-seat book), r1764 closed breadth
(2..30 seats: 8.74 -> 6.87pp, slope -0.13 instead of the -0.5 that pure diversification
gives), r1765 closed pairwise de-correlation (8.74 -> 6.98pp, and 4.68pp of annual return
paid for it), r1766 closed the ranking's own tilt (8.72 -> 7.95pp), and r1872 priced the era
roster (names and depth oppose, so breadth is not one dial).

Each of those lives in its own face with its own sentence. Read one at a time, a reader can
always believe the next axis is the one that will do it. This face asks the only question
that needs all four: **does any axis we own put the floor under 5pp, and if not, what does
the ruler itself say it would take?**

Rules:
  * every number is quoted from the face that measured it, with that face's own generated /
    cutoff printed beside it -- this script never re-prices a book;
  * a missing face is `CANNOT_VERIFY_ALL_AXES`, never "closed" (r98: a missing reading must
    never print the same sentence as a measured one);
  * an axis whose best floor is `None` (the era roster has no single floor number) does not
    count as "under target" -- None is not zero;
  * the bars arithmetic comes from the 5-seat row of the ruler face (`bars_needed_for_target`),
    which was written by the face that owns it, not recomputed here.

Usage:
  python scripts/etf_book_closed_axes.py run
  python scripts/etf_book_closed_axes.py --check
  python scripts/etf_book_closed_axes.py --selftest
  python scripts/etf_book_closed_axes.py --md
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

OUT_JSON = os.path.join(ROOT, "results", "etf_book_closed_axes.json")
OUT_MD = os.path.join(ROOT, "research", "ETF_BOOK_CLOSED_AXES.md")

SEAT_JSON = os.path.join(ROOT, "results", "etf_book_seat_mde.json")
CORR_JSON = os.path.join(ROOT, "results", "etf_book_corr_select.json")
TILT_JSON = os.path.join(ROOT, "results", "etf_book_tilt_neutral.json")
ROSTER_JSON = os.path.join(ROOT, "results", "etf_book_era_roster.json")

TARGET_PP = 5.0            # the published target the three axes were all measured against
BASE_SEATS = 5             # the book the company actually runs
EPS = 1e-9


def _load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _rel(path):
    try:
        return os.path.relpath(path, ROOT).replace(os.sep, "/")
    except ValueError:                                   # cross-drive fixture (r1594/r1745)
        return path


def _face(path):
    return _load(path) if os.path.exists(path) else None


def seats_axis(face):
    """Breadth: the ruler's own sweep, base row vs the narrowest floor it found."""
    rows = (face or {}).get("rows") or []
    base = next((r for r in rows if r.get("n_hold") == BASE_SEATS), None)
    usable = [r for r in rows if r.get("select_mde80_pp") is not None]
    if base is None or not usable:
        return {"axis": "seats", "readable": False,
                "detail": "the ruler face carries no %d-seat row" % BASE_SEATS,
                "artifact": _rel(SEAT_JSON), "cutoff": (face or {}).get("evidence_cutoff")}
    best = min(usable, key=lambda r: r["select_mde80_pp"])
    base_cagr = base.get("book_cagr_pct")
    best_cagr = best.get("book_cagr_pct")
    return {"axis": "seats", "readable": True,
            "label": "座数（2~30 座全扫）",
            "base_pp": round(base["select_mde80_pp"], 4),
            "best_pp": round(best["select_mde80_pp"], 4),
            "best_cell": "%d 座" % best["n_hold"],
            "move_pp": round(base["select_mde80_pp"] - best["select_mde80_pp"], 4),
            "annual_cost_pp": (round(base_cagr - best_cagr, 4)
                               if base_cagr is not None and best_cagr is not None else None),
            "cost_label": "年化让掉",
            "verdict": ((face or {}).get("verdict") or {}).get("verdict"),
            "artifact": _rel(SEAT_JSON), "cutoff": (face or {}).get("evidence_cutoff"),
            "bars_needed": base.get("bars_needed_for_target"),
            "bars_now": base.get("bars")}


def corr_axis(face):
    """Pairwise de-correlation: the same five seats, picked to not move together."""
    if not face or face.get("mde80_pp") is None or face.get("base_mde80_pp") is None:
        return {"axis": "corr", "readable": False,
                "detail": "the de-correlation face carries no floor pair",
                "artifact": _rel(CORR_JSON), "cutoff": (face or {}).get("evidence_cutoff")}
    primary = face.get("primary") or {}
    control = face.get("control") or {}
    cost = None
    if primary.get("book_cagr_pct") is not None and control.get("published_cagr_pct") is not None:
        cost = round(control["published_cagr_pct"] - primary["book_cagr_pct"], 4)
    return {"axis": "corr", "readable": True,
            "label": "成对去相关选股",
            "base_pp": round(face["base_mde80_pp"], 4),
            "best_pp": round(face["mde80_pp"], 4),
            "best_cell": face.get("arm"),
            "move_pp": round(face["base_mde80_pp"] - face["mde80_pp"], 4),
            "annual_cost_pp": cost, "cost_label": "年化让掉",
            "verdict": face.get("verdict"),
            "artifact": _rel(CORR_JSON), "cutoff": face.get("evidence_cutoff"),
            "sentence": face.get("sentence")}


def tilt_axis(face):
    """The ranking's own common tilt, hedged out of the book."""
    if not face or face.get("mde80_pp") is None:
        return {"axis": "tilt", "readable": False,
                "detail": "the tilt face carries no hedged floor",
                "artifact": _rel(TILT_JSON), "cutoff": (face or {}).get("evidence_cutoff")}
    leg = face.get("select_leg") or {}
    primary = face.get("primary") or {}
    return {"axis": "tilt", "readable": True,
            "label": "对冲排名自身倾斜",
            "base_pp": (round(leg["mde80_pp"], 4) if leg.get("mde80_pp") is not None
                        else None),
            "best_pp": round(face["mde80_pp"], 4),
            "best_cell": face.get("primary", {}).get("arm"),
            "move_pp": (round(face.get("improve_pp"), 4)
                        if face.get("improve_pp") is not None else None),
            "annual_cost_pp": (round(primary["alpha_given_up_pp"], 4)
                               if primary.get("alpha_given_up_pp") is not None else None),
            "cost_label": "让掉的 alpha",
            "verdict": face.get("verdict"),
            "artifact": _rel(TILT_JSON), "cutoff": face.get("evidence_cutoff"),
            "sentence": face.get("sentence")}


def roster_axis(face):
    """The era roster: names and depth oppose, so breadth is not one number."""
    if not face:
        return {"axis": "roster", "readable": False,
                "detail": "the era roster face is absent",
                "artifact": _rel(ROSTER_JSON), "cutoff": None}
    s = face.get("summary") or {}
    return {"axis": "roster", "readable": bool(s.get("verdict")),
            "label": "历史宽度（名册 vs 深度）",
            # deliberately no floor: this axis answers "does breadth point one way", and the
            # face's own verdict is that the two halves oppose. Printing a number here would
            # be this script inventing a floor the roster never measured.
            "base_pp": None, "best_pp": None, "move_pp": None,
            "annual_cost_pp": None, "cost_label": "—",
            "verdict": s.get("verdict"),
            "roster_multiple": s.get("roster_multiple"),
            "slots_multiple": s.get("slots_multiple"),
            "adv_median_multiple": s.get("adv_median_multiple"),
            "first_anchor": s.get("first_anchor"), "last_anchor": s.get("last_anchor"),
            "artifact": _rel(ROSTER_JSON), "cutoff": face.get("evidence_cutoff"),
            "detail": s.get("verdict") and None or "the roster face carries no verdict"}


def classify(axes, target=TARGET_PP):
    """The verdict, decided by counts this function can see (never by a name)."""
    readable = [a for a in axes if a.get("readable")]
    if not readable or any(not a.get("readable") for a in axes):
        return ("CANNOT_VERIFY_ALL_AXES",
                "有一条轴这一窗读不到，**不能把「没读」读成「关掉了」**（r98）。")
    priced = [a for a in readable if a.get("best_pp") is not None]
    under = [a for a in priced if a["best_pp"] <= target + EPS]
    if under:
        return ("AN_AXIS_REACHES_THE_FLOOR",
                "至少一条轴的地板已经到 %.1fpp 以下（%s）——下一步是买它，不是再关轴。"
                % (target, "、".join(a["axis"] for a in under)))
    return ("NO_AXIS_REACHES_THE_FLOOR",
            "我们手里的每一条轴都推到头了，选股腿的地板仍然在 %.1fpp 之上。"
            % target)


def sentence(axes, verdict, target=TARGET_PP):
    """One sentence a reader can act on: the best road, its price, and the ruler's own bill."""
    base = next((a["base_pp"] for a in axes if a.get("base_pp") is not None), None)
    priced = [a for a in axes if a.get("best_pp") is not None]
    if verdict == "CANNOT_VERIFY_ALL_AXES":
        missing = "、".join(a["axis"] for a in axes if not a.get("readable"))
        return ("这一窗读不全（缺：%s），**「没读」不等于「关掉了」**。" % missing)
    best = min(priced, key=lambda a: a["best_pp"])
    parts = []
    for a in priced:
        parts.append("%s %.2fpp" % (a["label"].split("（")[0], a["best_pp"]))
    head = "把 %s 各推到头，选股腿的地板从 %.2fpp 最窄只到 **%.2fpp**（%s）" % (
        "、".join(a["label"].split("（")[0] for a in priced),
        base if base is not None else float("nan"),
        best["best_pp"], best.get("best_cell") or best["label"])
    tail = "——**没有一条路把 %.1fpp 以下拿到手**" % target if verdict == "NO_AXIS_REACHES_THE_FLOOR" \
        else "——**有一条到线了**"
    s = head + "（%s）%s。" % ("；".join(parts), tail)
    if best.get("annual_cost_pp") is not None:
        s += "最快那条要付 %.2fpp 年化。" % best["annual_cost_pp"]
    seat = next((a for a in axes if a.get("axis") == "seats"), None)
    if seat and seat.get("bars_needed") and seat.get("bars_now"):
        s += ("按这格自己的尺子，把 %.2fpp 压到 %.1fpp 要 %s 根 bar（现 %s 根）——"
              "这条路要再攒 %s 根。" % (seat["base_pp"] or 0.0, target,
                                       format(int(seat["bars_needed"]), ","),
                                       format(int(seat["bars_now"]), ","),
                                       format(max(0, int(seat["bars_needed"])
                                                  - int(seat["bars_now"])), ",")))
    return s


def build_payload():
    seats = seats_axis(_face(SEAT_JSON))
    corr = corr_axis(_face(CORR_JSON))
    tilt = tilt_axis(_face(TILT_JSON))
    roster = roster_axis(_face(ROSTER_JSON))
    axes = [seats, corr, tilt, roster]
    verdict, sentence_short = classify(axes)
    cutoffs = [a.get("cutoff") for a in axes if a.get("cutoff")]
    return {"face": "etf_book_closed_axes",
            "script": _rel(os.path.abspath(__file__)),
            "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "evidence_cutoff": max(cutoffs) if cutoffs else None,
            "target_pp": TARGET_PP, "base_seats": BASE_SEATS,
            "axes": axes,
            "n_readable": sum(1 for a in axes if a.get("readable")),
            "n_priced": sum(1 for a in axes if a.get("best_pp") is not None),
            "verdict": verdict,
            "sentence_short": sentence_short,
            "sentence": sentence(axes, verdict),
            "question": ("does any axis we already own put the select leg's MDE80 under "
                         "%.1fpp, and if not, how many bars would" % TARGET_PP)}


def _payload_key(d):
    """The part of the payload --check can re-derive offline (everything but the clock)."""
    keys = ("face", "target_pp", "base_seats", "verdict", "sentence", "sentence_short",
            "axes", "n_readable", "n_priced", "evidence_cutoff")
    return {k: d.get(k) for k in keys}


def run():
    d = build_payload()
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(d, fh, ensure_ascii=False, indent=1)
    print("[write] %s" % OUT_JSON)
    print("verdict=%s axes=%d/%d" % (d["verdict"], d["n_readable"], len(d["axes"])))
    print(d["sentence"])
    return 0


def write_md():
    d = _load(OUT_JSON)
    L = ["# 选股腿的地板：每一条轴都推到头了（%s）\n\n" % (d.get("evidence_cutoff") or "")]
    L.append("**%s**\n\n" % d.get("sentence"))
    L.append("| 轴 | 基线 | 最窄 | 挪动 | 代价 | 判词 | 出处（cutoff） |\n")
    L.append("|---|---|---|---|---|---|---|\n")
    for a in d.get("axes") or []:
        if not a.get("readable"):
            L.append("| %s | — | 读不到 | — | — | %s | %s（%s） |\n"
                     % (a.get("axis"), a.get("detail"), a.get("artifact"), a.get("cutoff")))
            continue
        L.append("| %s | %s | %s | %s | %s | %s | %s（%s） |\n" % (
            a.get("label"), _pp(a.get("base_pp")), _pp(a.get("best_pp")),
            _pp(a.get("move_pp"), signed=True),
            (("%s %s" % (a.get("cost_label"), _pp(a.get("annual_cost_pp"), signed=True)))
             if a.get("annual_cost_pp") is not None else "—"),
            a.get("verdict"), a.get("artifact"), a.get("cutoff")))
    L.append("\n## 这张面的边界\n\n")
    L.append("- 每个数来自测它的那张面，本面只搬不重算；cutoff 印在旁边。\n")
    L.append("- 名册那一条没有单一地板读数：「名字涨、深度跌」是它自己的判词，"
             "硬塞一个 pp 数就是本面替它发明量尺。\n")
    L.append("- bar 数来自尺子面 5 座那行自带的 `bars_needed_for_target`，不是本面用 SE 反推的。\n")
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("".join(L))
    print("[write] %s" % OUT_MD)
    return 0


def _pp(x, signed=False):
    if x is None:
        return "—"
    return ("%+.2fpp" % x) if signed else ("%.2fpp" % x)


def _check():
    d = _load(OUT_JSON)
    fresh = build_payload()
    a = _payload_key(d)
    b = _payload_key(fresh)
    if json.dumps(a, sort_keys=True, ensure_ascii=False) != \
            json.dumps(b, sort_keys=True, ensure_ascii=False):
        # r1850 lesson: the chain only pays the writer when the probe says STALE, so a
        # check that prints "CHECK FAILED" would go red for ever while the writer it was
        # supposed to call never ran.
        print("STALE FACE_BEHIND: the published face no longer quotes the faces it reads")
        for k in a:
            if json.dumps(a[k], sort_keys=True) != json.dumps(b[k], sort_keys=True):
                print("  %s: published=%s" % (k, json.dumps(a[k], ensure_ascii=False)[:200]))
                print("  %s: rederived=%s" % (k, json.dumps(b[k], ensure_ascii=False)[:200]))
        return 1
    # the sentence has to quote each priced axis' own best floor, to one decimal
    for axis in fresh["axes"]:
        if axis.get("best_pp") is None:
            continue
        token = "%.2fpp" % axis["best_pp"]
        if token not in d["sentence"]:
            print("CHECK FAILED: sentence does not quote %s (%s)" % (axis["axis"], token))
            return 1
    print("check ok: verdict=%s axes=%d/%d sentence=%d chars"
          % (d["verdict"], d["n_readable"], len(d["axes"]), len(d["sentence"])))
    return 0


def selftest():
    fails = []
    n = [0]

    def chk(name, cond, detail=""):
        n[0] += 1
        if not cond:
            fails.append("%s %s" % (name, detail))

    def ax(name, base, best, cost=None, readable=True, verdict="V"):
        return {"axis": name, "label": name, "readable": readable, "base_pp": base,
                "best_pp": best, "move_pp": (base - best) if (base is not None and best is not None)
                else None, "annual_cost_pp": cost, "cost_label": "年化让掉", "verdict": verdict,
                "artifact": "results/x.json", "cutoff": "2026-11-19", "best_cell": "5 座"}

    # L1 every axis above the target -> the honest negative
    v, _ = classify([ax("a", 8.74, 6.87), ax("b", 8.74, 6.98), ax("c", 8.72, 7.95)])
    chk("L1 all above target", v == "NO_AXIS_REACHES_THE_FLOOR", v)

    # L2 one axis under the target -> must not be reported as closed
    v, _ = classify([ax("a", 8.74, 6.87), ax("b", 8.74, 4.9)])
    chk("L2 one under target", v == "AN_AXIS_REACHES_THE_FLOOR", v)

    # L3 a missing axis is not a closed axis (r98)
    v, short = classify([ax("a", 8.74, 6.87), ax("b", None, None, readable=False)])
    chk("L3 missing axis refuses", v == "CANNOT_VERIFY_ALL_AXES", v)
    chk("L3 sentence says read-failure", "读不全" in sentence(
        [ax("a", 8.74, 6.87), ax("b", None, None, readable=False)], v))

    # L4 None is not zero -- an unpriced axis must never satisfy the target
    v, _ = classify([ax("a", 8.74, 6.87), ax("b", None, None)])
    chk("L4 None is not a pass", v == "NO_AXIS_REACHES_THE_FLOOR", v)

    # L5 the sentence quotes every priced axis' own number
    s = sentence([ax("a", 8.74, 6.87), ax("b", 8.74, 6.98)], "NO_AXIS_REACHES_THE_FLOOR")
    chk("L5 quotes seats", "6.87pp" in s, s)
    chk("L5 quotes corr", "6.98pp" in s, s)
    chk("L5 names the best road", "6.87pp**" in s, s)

    # L6 cost is quoted when the winner carries one, and never invented
    s_cost = sentence([ax("a", 8.74, 6.98, cost=4.68)], "NO_AXIS_REACHES_THE_FLOOR")
    chk("L6 cost quoted", "4.68pp 年化" in s_cost, s_cost)
    s_free = sentence([ax("a", 8.74, 6.98)], "NO_AXIS_REACHES_THE_FLOOR")
    chk("L6 no invented cost", "年化" not in s_free, s_free)

    # L7 bars arithmetic only when the owner published it
    seat = ax("seats", 8.74, 6.87)
    seat["bars_needed"] = 7657
    seat["bars_now"] = 1662
    chk("L7 bars quoted", "7,657" in sentence([seat], "NO_AXIS_REACHES_THE_FLOOR"))
    bare = ax("seats", 8.74, 6.87)
    chk("L7 absent bars not printed as 0",
        "0 根" not in sentence([bare], "NO_AXIS_REACHES_THE_FLOOR"))

    # L8 the base floor is the 5-seat row, not the widest one
    face = {"evidence_cutoff": "2026-11-13", "verdict": {"verdict": "SEAT_TARGET_NOT_REACHED"},
            "rows": [{"n_hold": 2, "select_mde80_pp": 10.73, "book_cagr_pct": 7.88},
                     {"n_hold": 5, "select_mde80_pp": 8.74, "book_cagr_pct": 9.12,
                      "bars": 1662, "bars_needed_for_target": 7657},
                     {"n_hold": 30, "select_mde80_pp": 6.87, "book_cagr_pct": 7.0}]}
    sa = seats_axis(face)
    chk("L8 base is the 5-seat row", abs(sa["base_pp"] - 8.74) < 1e-9, sa)
    chk("L8 best is the narrowest", abs(sa["best_pp"] - 6.87) < 1e-9, sa)
    chk("L8 move is base-best", abs(sa["move_pp"] - 1.87) < 1e-9, sa)
    chk("L8 cost is base-best cagr", abs(sa["annual_cost_pp"] - 2.12) < 1e-9, sa)

    # L9 a face with no 5-seat row is unreadable, not "zero movement"
    chk("L9 missing base row refuses",
        seats_axis({"rows": [{"n_hold": 30, "select_mde80_pp": 6.87}]})["readable"] is False)

    # L10 an absent face is unreadable, and says which file
    c = corr_axis(None)
    chk("L10 absent face names the file",
        c["readable"] is False and c["artifact"].endswith("etf_book_corr_select.json"), c)

    # L11 the payload key ignores the clock, so --check is stable across reruns
    k1 = {k: 1 for k in ("face", "target_pp", "verdict")}
    chk("L11 payload key excludes generated", "generated" not in _payload_key(
        {"face": "f", "generated": "now"}))

    total = n[0]
    print("selftest %d/%d PASS" % (total - len(fails), total))
    for f in fails:
        print("  FAIL", f)
    return 1 if fails else 0


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if "--check" in argv:
        return _check()
    if "--md" in argv:
        return write_md()
    return run()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
