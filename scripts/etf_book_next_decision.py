"""ETF book -- "when is the next decision bar?" had three answers on one sheet.

The 2026-11-10 ticket says it twice, and disagrees with itself. The cut-permission block reads
`decision_date 2026-11-11` and the production sheet reads `last_decision_bar 2026-10-14,
1 bar until the next decision` -- both of those mean 2026-11-11. Half a page later the swap
section reads "下一个决策 bar（每 20 根）读作 2026-12-08". Nineteen trading days apart, and the
later one is not even on the grid: 2026-12-08 sits at index 8779 of the official calendar and
8779 % 20 == 19, so it is the bar *before* a grid bar, not a grid bar.

The cause is a rolling anchor, one line in `etf_book_swap_units.compute`:
`after[rebal - 1]` counts 20 sessions from whatever bar the sheet was printed on. A rolling
anchor moves forward every day the sheet is printed, so its "next decision bar" is only ever a
grid date by accident.

This face is the single clock, read off facts other faces already committed to:

  * the anchor is the published `last_decision_bar`, checked against the OFFICIAL calendar --
    never re-derived from this chain's own panel (r1286: a panel cannot say when its own grid
    should tick);
  * the phase is that anchor's index mod REBAL, and the next grid bar is the first official
    session after the sheet's bar that lands on the same phase;
  * every face that prints a decision date is read, and each one travels with its distance in
    bars, its face path, and whether its date is on the grid at all;
  * a date the official calendar does not contain is named unreadable -- never printed as if it
    existed, never zeroed;
  * `check` re-derives and goes red if a published row stops matching the calendar it claims.

Usage:
    python scripts/etf_book_next_decision.py run
    python scripts/etf_book_next_decision.py check
    python scripts/etf_book_next_decision.py selftest
"""

from __future__ import annotations

import argparse
import datetime as dt
import io
import json
import os
import sys
from contextlib import redirect_stdout

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import exchange_calendar_audit as CA   # noqa: E402  (the official calendar owner)

OUT_JSON = os.path.join(ROOT, "results", "etf_book_next_decision.json")
OUT_MD = os.path.join(ROOT, "results", "etf_book_next_decision.md")
PUBLISH = (OUT_JSON, OUT_MD)

AGREE = "AGREE"
DISAGREE = "DISAGREE"
UNKNOWN = "UNKNOWN"

REBAL_FALLBACK = 20

PRODUCTION = "results/etf_book_production/latest.json"
PERMISSION = "results/etf_book_rebalance_permission.json"
SWAP_UNITS = "results/etf_book_swap_units.json"
ORDER_LEDGER = "results/etf_book_order/ledger.jsonl"


def _read_json(path):
    try:
        with open(os.path.join(ROOT, path), encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def _read_jsonl(path):
    out = []
    try:
        with open(os.path.join(ROOT, path), encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    out.append(json.loads(line))
    except (OSError, ValueError):
        return None
    return out


def load_calendar(cal_path=None):
    """The official session list. A panel would judge the grid by its own tail (r1286)."""
    return list(CA.load_calendar(cal_path or CA.CAL_PATH) or [])


def grid_constant():
    """REBAL from its owner, with the fallback disclosed rather than silent."""
    try:
        from scripts.etf_book_order import REBAL  # noqa: PLC0415
        return int(REBAL), "import"
    except Exception:                                      # noqa: BLE001
        try:
            import etf_book_order                       # noqa: PLC0415
            return int(etf_book_order.REBAL), "import"
        except Exception:                                  # noqa: BLE001
            return REBAL_FALLBACK, "fallback"


def index_of(days, bar):
    """Position of `bar` in the official calendar, or None when the calendar has no such day."""
    if not bar or not days:
        return None
    try:
        return days.index(str(bar)[:10])
    except ValueError:
        return None


def phase_of(days, bar, rebal):
    i = index_of(days, bar)
    return None if i is None else i % int(rebal)


def next_grid(days, as_of, phase, rebal):
    """First official session after `as_of` that lands on `phase`."""
    i = index_of(days, as_of)
    if i is None or phase is None:
        return {"bar": None, "bars_away": None, "index": None}
    j = i + 1
    while j < len(days):
        if j % int(rebal) == int(phase):
            return {"bar": days[j], "bars_away": j - i, "index": j}
        j += 1
    return {"bar": None, "bars_away": None, "index": None}


def bars_between(days, a, b):
    """Signed distance in official sessions from `a` to `b` (None if either is off-calendar)."""
    ia, ib = index_of(days, a), index_of(days, b)
    return None if ia is None or ib is None else ib - ia


def next_decision(as_of, days=None, rebal=None, anchor=None):
    """The clock, for producers that need the date and not the whole comparison.

    The anchor is the published `last_decision_bar` -- a fact another face already committed to.
    When no anchor is readable the phase falls back to the calendar's own origin, and says so.
    """
    days = days if days is not None else load_calendar()
    rebal = int(rebal or grid_constant()[0])
    if anchor is None:
        anchor = ((_read_json(PRODUCTION) or {}).get("sheet") or {}).get("last_decision_bar")
    phase = phase_of(days, anchor, rebal)
    out = {"bar": None, "grid": rebal, "grid_source": "anchor", "anchor_bar": anchor,
           "phase": phase, "bars_away": None, "rule": None, "why": ""}
    if phase is None:
        phase = 0
        out["grid_source"] = "calendar_origin_fallback"
        out["phase"] = phase
        out["why"] = ("锚点 last_decision_bar %r 读不出，相位回落到官方日历原点（已披露）"
                      % (anchor,))
    nxt = next_grid(days, as_of, phase, rebal)
    out["bar"] = nxt["bar"]
    out["bars_away"] = nxt["bars_away"]
    out["rule"] = ("%s 之后第一个落在官方日历相位 %d mod %d 的交易日"
                   % (as_of, phase, rebal))
    if nxt["bar"] is None and not out["why"]:
        out["why"] = "官方日历里 %r 之后没有落在相位 %d 的交易日" % (as_of, phase)
    return out


# --------------------------------------------------------------------------- claims
def _claim(name, face, key, printed, note, extra=None):
    row = {"name": name, "face": face, "key": key, "printed": printed, "note": note}
    row.update(extra or {})
    return row


def production_claim(days, face):
    """`last_decision_bar` + `bars_until_next_decision`, turned into a date by the calendar."""
    if face is None:
        return _claim("production_sheet", PRODUCTION, "sheet.bars_until_next_decision", None,
                      "面缺失，读不出下一根决策 bar", {"unreadable": "no face published"})
    sh = face.get("sheet") or {}
    as_of, last, n = sh.get("as_of_bar"), sh.get("last_decision_bar"), sh.get("bars_until_next_decision")
    i = index_of(days, as_of)
    if i is None or not isinstance(n, int):
        return _claim("production_sheet", PRODUCTION, "sheet.bars_until_next_decision", None,
                      "面里的 as_of_bar/bars_until_next_decision 读不出",
                      {"unreadable": "as_of_bar=%r bars_until_next_decision=%r" % (as_of, n)})
    j = i + n
    if j >= len(days):
        return _claim("production_sheet", PRODUCTION, "sheet.bars_until_next_decision", None,
                      "官方日历没有越过 %s 的第 %d 个交易日" % (as_of, n),
                      {"unreadable": "calendar ends at %s" % (days[-1] if days else "?")})
    return _claim("production_sheet", PRODUCTION, "sheet.bars_until_next_decision", days[j],
                  "%s 起第 %d 根（面自己写的 bars_until_next_decision）" % (as_of, n),
                  {"sheet": {"as_of_bar": as_of, "last_decision_bar": last,
                             "bars_until_next_decision": n, "is_grid_decision_bar":
                             sh.get("is_grid_decision_bar")}})


def permission_claim(days, face):
    if face is None:
        return _claim("cut_permission", PERMISSION, "decision_date", None,
                      "面缺失，读不出它签给哪一天", {"unreadable": "no face published"})
    d = face.get("decision_date")
    if index_of(days, d) is None:
        return _claim("cut_permission", PERMISSION, "decision_date", None,
                      "面签的 %r 不在官方日历上" % (d,),
                      {"unreadable": "decision_date=%r off-calendar" % (d,)})
    return _claim("cut_permission", PERMISSION, "decision_date", str(d)[:10],
                  "权限面自己签的决策日")


def swap_units_claim(days, face):
    if face is None:
        return _claim("swap_section", SWAP_UNITS, "next_decision_bar.bar", None,
                      "面缺失，读不出它印的日期", {"unreadable": "no face published"})
    nd = face.get("next_decision_bar") or {}
    bar = nd.get("bar")
    if not bar:
        return _claim("swap_section", SWAP_UNITS, "next_decision_bar.bar", None,
                      "面里的 next_decision_bar.bar 是空的",
                      {"unreadable": "next_decision_bar.bar=%r" % (bar,), "grid": nd.get("grid")})
    return _claim("swap_section", SWAP_UNITS, "next_decision_bar.bar", str(bar)[:10],
                  "换票节自己算的（grid=%s，来源=%s）" % (nd.get("grid"), nd.get("grid_source")),
                  {"grid": nd.get("grid")})


def ledger_trace(days, rows, rebal):
    """What the book actually does: the bars on which its k was re-decided."""
    if not rows:
        return {"bars": [], "off_grid": [], "unreadable": "no ledger rows"}
    dates = [str(r.get("date") or "")[:10] for r in rows]
    ks = [r.get("k") for r in rows]
    moves = []
    for i in range(1, len(rows)):
        try:
            if abs(float(ks[i]) - float(ks[i - 1])) > 1e-12:
                moves.append(dates[i])
        except (TypeError, ValueError):
            continue
    off = [d for d in moves if index_of(days, d) is not None and (index_of(days, d) % int(rebal)) != 0]
    return {"bars": moves[-6:], "n_moves": len(moves), "off_grid": off[-6:],
            "first": dates[0] if dates else None, "last": dates[-1] if dates else None}


# --------------------------------------------------------------------------- assess
def load_faces():
    """The published faces this clock compares, in one read (also a seam for callers)."""
    return {"production": _read_json(PRODUCTION), "permission": _read_json(PERMISSION),
            "swap_units": _read_json(SWAP_UNITS), "ledger": _read_jsonl(ORDER_LEDGER)}


def assess(now=None, days=None, faces=None, rebal=None):
    """Compare every printed answer with the grid the anchor implies.

    `faces` maps {"production","permission","swap_units","ledger"} to payloads (fixture seam).
    """
    now = now or dt.datetime.now()
    days = days if days is not None else load_calendar()
    rebal = int(rebal or grid_constant()[0])
    grid_source = grid_constant()[1] if rebal == grid_constant()[0] else "explicit"

    if faces is None:
        faces = load_faces()
    prod, perm, swu, led = (faces.get("production"), faces.get("permission"),
                            faces.get("swap_units"), faces.get("ledger"))

    claims = [production_claim(days, prod), permission_claim(days, perm),
              swap_units_claim(days, swu)]
    sheet = (prod or {}).get("sheet") or {}
    as_of = sheet.get("as_of_bar")
    anchor = sheet.get("last_decision_bar")
    phase = phase_of(days, anchor, rebal)

    grid = {"rebal": rebal, "grid_source": grid_source, "as_of": as_of,
            "anchor_bar": anchor, "anchor_source": "%s#sheet.last_decision_bar" % PRODUCTION,
            "anchor_on_calendar": index_of(days, anchor) is not None,
            "phase": phase, "next_bar": None, "bars_away": None, "crosscheck": None,
            "why": ""}
    if not days:
        grid["why"] = "官方日历读不出来，任何日期都不印"
    elif index_of(days, as_of) is None:
        grid["why"] = "as_of_bar %r 不在官方日历上，网格无从对齐" % (as_of,)
    elif phase is None:
        grid["why"] = "锚点 last_decision_bar %r 不在官方日历上，相位读不出" % (anchor,)
    else:
        nxt = next_grid(days, as_of, phase, rebal)
        grid.update({"next_bar": nxt["bar"], "bars_away": nxt["bars_away"]})
        # the panel-start rule (index 0 of the calendar) should agree; when it does not, the
        # anchor won and the disagreement is published rather than averaged away.
        origin = next_grid(days, as_of, 0, rebal)
        grid["crosscheck"] = {"rule": "official calendar origin mod rebal == 0",
                              "next_bar": origin["bar"],
                              "agrees": origin["bar"] == nxt["bar"],
                              "note": ("面板起点与日历原点同相位" if origin["bar"] == nxt["bar"]
                                       else "同一天，两条规则的答案不同——锚点为准，差异随件披露")}

    for c in claims:
        c["bars_from_sheet"] = (bars_between(days, as_of, c["printed"])
                                if (c["printed"] and as_of) else None)
        i = index_of(days, c["printed"])
        c["on_grid"] = None if (i is None or phase is None) else (i % rebal) == phase
        c["agrees"] = None if (c["printed"] is None or grid["next_bar"] is None) else \
            c["printed"] == grid["next_bar"]

    readable = [c for c in claims if c["printed"]]
    if grid["next_bar"] is None or not readable:
        verdict = UNKNOWN
    elif any(c["agrees"] is False for c in claims):
        # a readable face that dissents is evidence; it outranks an unreadable sibling
        verdict = DISAGREE
    elif len(readable) < len(claims):
        # nothing disagrees, but nothing proves agreement either: a missing face is not a pass
        verdict = UNKNOWN
    else:
        verdict = AGREE

    wrong = [c for c in claims if c["printed"] and c["agrees"] is False]
    off_grid = [c["name"] for c in readable if c["on_grid"] is False]
    gaps = [abs(c["bars_from_sheet"]) for c in wrong if c.get("bars_from_sheet") is not None]

    face = {
        "artifact": "etf_book_next_decision",
        "generated": now.isoformat(timespec="seconds"),
        "evidence_cutoff": as_of,
        "calendar_source": os.path.relpath(CA.CAL_PATH, ROOT).replace(os.sep, "/"),
        "calendar_last": days[-1] if days else None,
        "grid": grid,
        "claims": claims,
        "wrong_claims": [c["name"] for c in wrong],
        "off_grid_claims": off_grid,
        "worst_gap_bars": (max(gaps) if gaps else None),
        "ledger_trace": ledger_trace(days, led, rebal),
        "verdict": verdict,
    }
    face["sentence"] = sentence(face)
    face["caveats"] = [
        "网格只回答「下一次重排是哪一天」，它对此外的事（触发面、过路费、折扣兑现）一无所知，"
        "也不替它们作证。",
        "相位取自已发布的 last_decision_bar（别人已经落账的事实），不是本面自选；"
        "官方日历原点的同相位只是交叉核对，两者不一致时以锚点为准并披露。",
        "账本里 k 的变动只作行为样本列出：它动在哪一天，不等于那一天该决策（也可能是规则内的"
        "风控改档），本面不据此判对错。",
        "日历里没有的日期一律不印；读不出的面列 unreadable，不按 0 或最近日期顶替。",
    ]
    return face


def sentence(face):
    g = face["grid"]
    if g["next_bar"] is None and g["why"]:
        return "下一根决策 bar 读不出来：%s。" % g["why"]
    head = ("下一根决策 bar = %s（锚点 %s 起每 %d 根，距 %s %d 根）。"
            % (g["next_bar"], g["anchor_bar"], g["rebal"], g["as_of"], g["bars_away"]))
    if face["verdict"] == AGREE:
        return head + "票面上三个面都这么说。"
    if face["verdict"] == UNKNOWN:
        return head + "但票面至少有一面读不出来，不能据此称「一致」。"
    worst = [c for c in face["claims"] if c["name"] in face["wrong_claims"]]
    parts = ["%s 写的是 %s（%+d 根%s）"
             % (c["name"], c["printed"], c.get("bars_from_sheet") or 0,
                "，且那天不在网格上" if c["on_grid"] is False else "")
             for c in worst]
    return head + "票面不同意：" + "；".join(parts) + "。"


# --------------------------------------------------------------------------- render
def md_lines(face, heading="## 下一根决策 bar 是哪一天（r1536）"):
    L = ["", heading]
    if not face:
        L += ["- **这一问答不了**：本面没有随本单给出——不是「一致」，也不是「没有下一根」。", ""]
        return L
    g = face.get("grid") or {}
    if g.get("next_bar") is None:
        L += ["- **这一问答不了**：%s。不拿最近一根 bar 顶替。" % (g.get("why") or "网格读不出"), ""]
        return L
    L += ["- 下一根决策 bar：**%s**（距 %s %d 个交易日；锚点 `last_decision_bar` = %s，每 %d 根）。"
          % (g["next_bar"], g.get("as_of") or "?", int(g.get("bars_away") or 0),
             g.get("anchor_bar") or "?", int(g.get("rebal") or 0)),
          "", "| 面 | 它印的 | 距本单票面 | 落在网格上 | 一致 |", "|---|---|---|---|---|"]
    for c in face.get("claims") or []:
        if c.get("printed") is None:
            L.append("| %s | 读不出（%s） | – | – | – |" % (c["name"], c.get("unreadable") or c.get("note")))
            continue
        L.append("| %s | %s | %+d 根 | %s | %s |"
                 % (c["name"], c["printed"], int(c.get("bars_from_sheet") or 0),
                    "是" if c.get("on_grid") else ("否" if c.get("on_grid") is False else "?"),
                    "是" if c.get("agrees") else ("否" if c.get("agrees") is False else "?")))
    cc = g.get("crosscheck") or {}
    if cc:
        L.append("- 交叉核对：%s → %s（%s）。" % (cc.get("rule"), cc.get("next_bar"),
                                          "一致" if cc.get("agrees") else "不一致"))
    tr = face.get("ledger_trace") or {}
    if tr.get("bars"):
        L.append("- 账本自己的 k 最近动在这几根：%s（共 %d 次，其中不在网格上 %d 次）——"
                 "这是行为样本，不是判据。" % ("、".join(tr["bars"]), tr.get("n_moves") or 0,
                                        len(tr.get("off_grid") or [])))
    L += ["- 判词：**%s**%s" % (face.get("verdict"),
                            ("（最大差 %d 根）" % face["worst_gap_bars"])
                            if face.get("worst_gap_bars") else ""),
          "- %s" % face.get("sentence") if face.get("sentence") else "- ", ""]
    return L


def write_out(face, out=None):
    out = out or PUBLISH
    payload = dict(face)
    payload.pop("generated", None)
    with open(out[0], "w", encoding="utf-8") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
    with open(out[1], "w", encoding="utf-8") as fh:
        fh.write("# 下一根决策 bar 是哪一天\n\n```json\n")
        json.dump(payload, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n```\n\n" + "\n".join(md_lines(face)) + "\n")


# --------------------------------------------------------------------------- check
def check():
    """Re-derive and refuse a published face that no longer matches the calendar it names."""
    published = _read_json(os.path.relpath(OUT_JSON, ROOT).replace(os.sep, "/"))
    if not published:
        print("CHECK_FAIL no published face")
        return 2
    fresh = assess()
    problems = []
    if published.get("verdict") != fresh.get("verdict"):
        problems.append("verdict %s != %s" % (published.get("verdict"), fresh.get("verdict")))
    if (published.get("grid") or {}).get("next_bar") != (fresh.get("grid") or {}).get("next_bar"):
        problems.append("next_bar %s != %s" % ((published.get("grid") or {}).get("next_bar"),
                                               (fresh.get("grid") or {}).get("next_bar")))
    # every printed date must still be an official session, and the grid flag must still hold
    days = load_calendar()
    rebal = int((fresh.get("grid") or {}).get("rebal") or REBAL_FALLBACK)
    phase = (fresh.get("grid") or {}).get("phase")
    for c in published.get("claims") or []:
        if not c.get("printed"):
            continue
        i = index_of(days, c["printed"])
        if i is None:
            problems.append("%s prints %s, which the official calendar does not have"
                            % (c.get("name"), c.get("printed")))
            continue
        on_grid = (i % rebal) == phase if phase is not None else None
        if c.get("on_grid") is not None and on_grid != c.get("on_grid"):
            problems.append("%s on_grid %s != %s" % (c.get("name"), c.get("on_grid"), on_grid))
    if problems:
        print("CHECK_FAIL " + "; ".join(problems[:4]))
        return 1
    print("CHECK_OK verdict=%s next=%s claims=%d off_grid=%d"
          % (fresh.get("verdict"), (fresh.get("grid") or {}).get("next_bar"),
             len(fresh.get("claims") or []), len(fresh.get("off_grid_claims") or [])))
    return 0


def run(now=None, faces=None, days=None, out=None):
    face = assess(now=now, days=days, faces=faces)
    write_out(face, out)
    print("NEXT-DECISION %s next=%s anchor=%s phase=%s wrong=%s off_grid=%s worst_gap=%s"
          % (face["verdict"], face["grid"].get("next_bar"), face["grid"].get("anchor_bar"),
             face["grid"].get("phase"), ",".join(face["wrong_claims"]) or "-",
             ",".join(face["off_grid_claims"]) or "-", face.get("worst_gap_bars")))
    return 0


# --------------------------------------------------------------------------- selftest
def selftest():
    legs = []

    def leg(name, ok, detail=""):
        legs.append((name, bool(ok), detail))

    cal = (["2026-10-%02d" % d for d in range(1, 32)] + ["2026-11-%02d" % d for d in range(1, 31)]
           + ["2026-12-%02d" % d for d in range(1, 32)])
    # a clean 20-bar grid every 20 rows, anchor on one of its own bars
    anchor_idx = 20
    anchor = cal[anchor_idx]
    as_of = cal[41]                       # deliberately OFF the grid, like the live sheet
    phase = anchor_idx % 20
    nxt = next_grid(cal, as_of, phase, 20)

    leg("L1 phase comes from the anchor's own position", phase == 0, str(phase))
    leg("L2 the next grid bar is the first later bar on that phase",
        nxt["bar"] == cal[60] and nxt["bars_away"] == 19, str(nxt))
    on_grid = next_grid(cal, cal[40], phase, 20)
    leg("L3 a sheet printed ON a grid bar reads exactly rebal bars ahead",
        on_grid["bar"] == cal[60] and on_grid["bars_away"] == 20, str(on_grid))
    # the live defect: as_of + rebal lands off-grid whenever as_of is not on the grid
    rolling = cal[41 + 20]
    leg("L4 the shape of the published bug is reproducible",
        (cal.index(rolling) % 20) != phase, rolling)

    faces = {
        "production": {"sheet": {"as_of_bar": as_of, "last_decision_bar": anchor,
                                 "bars_until_next_decision": nxt["bars_away"],
                                 "is_grid_decision_bar": False}},
        "permission": {"decision_date": nxt["bar"]},
        "swap_units": {"next_decision_bar": {"bar": nxt["bar"], "grid": 20, "grid_source": "import"}},
        "ledger": [{"date": cal[40], "k": 0.5}, {"date": cal[41], "k": 0.4}],
    }
    f = assess(now=dt.datetime(2026, 11, 11, 5, 30), days=cal, faces=faces, rebal=20)
    leg("L5 three faces that agree read AGREE", f["verdict"] == AGREE, f["verdict"])
    leg("L6 the grid names the anchor it was read from",
        f["grid"]["anchor_bar"] == anchor and f["grid"]["anchor_on_calendar"] is True, f["grid"])

    bad = dict(faces)
    bad["swap_units"] = {"next_decision_bar": {"bar": rolling, "grid": 20, "grid_source": "import"}}
    fb = assess(now=dt.datetime(2026, 11, 11, 5, 30), days=cal, faces=bad, rebal=20)
    leg("L7 one disagreeing face is DISAGREE, not a majority vote", fb["verdict"] == DISAGREE, fb["verdict"])
    leg("L8 the wrong face is named and its off-grid date is flagged",
        fb["wrong_claims"] == ["swap_section"] and "swap_section" in fb["off_grid_claims"],
        (fb["wrong_claims"], fb["off_grid_claims"]))
    leg("L9 the gap is measured in bars, not printed as a bare pair of dates",
        fb["worst_gap_bars"] == abs(bars_between(cal, as_of, rolling)), str(fb["worst_gap_bars"]))

    missing = dict(faces)
    missing["swap_units"] = None
    fm = assess(now=dt.datetime(2026, 11, 11, 5, 30), days=cal, faces=missing, rebal=20)
    leg("L10 a missing face is unreadable, never 'agrees'",
        fm["verdict"] == UNKNOWN and any(c.get("unreadable") for c in fm["claims"]), fm["verdict"])

    offcal = dict(faces)
    offcal["permission"] = {"decision_date": "2027-01-04"}
    fo = assess(now=dt.datetime(2026, 11, 11, 5, 30), days=cal, faces=offcal, rebal=20)
    perm_row = [c for c in fo["claims"] if c["name"] == "cut_permission"][0]
    leg("L11 a date the calendar does not have is refused, not printed",
        perm_row["printed"] is None and "off-calendar" in (perm_row.get("unreadable") or ""), perm_row)

    noanchor = dict(faces)
    noanchor["production"] = {"sheet": {"as_of_bar": as_of, "last_decision_bar": "2026-09-30",
                                        "bars_until_next_decision": 1}}
    fa = assess(now=dt.datetime(2026, 11, 11, 5, 30), days=cal, faces=noanchor, rebal=20)
    leg("L12 an anchor off the calendar reads UNKNOWN with a reason",
        fa["verdict"] == UNKNOWN and fa["grid"]["next_bar"] is None, fa["grid"].get("why"))

    stale = dict(faces)
    stale["production"] = {"sheet": {"as_of_bar": None, "last_decision_bar": anchor,
                                     "bars_until_next_decision": 1}}
    fs = assess(now=dt.datetime(2026, 11, 11, 5, 30), days=cal, faces=stale, rebal=20)
    leg("L13 a face with no as_of_bar cannot date anything", fs["grid"]["next_bar"] is None,
        fs["grid"].get("why"))

    # the grid answer is read off the anchor + the sheet's bar, so a one-bar move in the sheet
    # moves the answer by one bar instead of typing a date into the code
    one_earlier = dict(faces)
    one_earlier["production"] = {"sheet": {"as_of_bar": cal[39], "last_decision_bar": anchor,
                                           "bars_until_next_decision": 1}}
    fs2 = assess(now=dt.datetime(2026, 11, 11, 5, 30), days=cal, faces=one_earlier, rebal=20)
    leg("L14 moving the sheet's bar by one moves the grid answer (the rule is anchored, not typed)",
        fs2["grid"]["next_bar"] == cal[40] and fs2["grid"]["bars_away"] == 1,
        str(fs2["grid"].get("next_bar")))

    txt = "\n".join(md_lines(fb))
    leg("L15 md names each face, the printed date and the distance",
        "swap_section" in txt and rolling in txt and "| 面 |" in txt, txt[:80])
    leg("L16 md says an unreadable face out loud instead of zeroing it",
        "读不出" in "\n".join(md_lines(fm)), "")
    leg("L17 the face carries evidence_cutoff so the science gate can key on it",
        f.get("evidence_cutoff") == as_of, str(f.get("evidence_cutoff")))
    leg("L18 every printed claim is an official session",
        all(index_of(cal, c["printed"]) is not None for c in f["claims"]), "")

    live_days = load_calendar()
    leg("L19 the calendar this face reads is the official csv",
        os.path.basename(CA.CAL_PATH) == "exchange_calendar.csv", os.path.basename(CA.CAL_PATH))
    leg("L20 the live anchor 2026-10-14 sits on the grid the calendar implies",
        index_of(live_days, "2026-10-14") is not None
        and index_of(live_days, "2026-10-14") % 20 == 0, "")

    passed = sum(1 for _, ok, _ in legs if ok)
    for name, ok, detail in legs:
        print(("[PASS] " if ok else "[FAIL] ") + name + ("" if ok else "  -> " + str(detail)[:160]))
    print("%d/%d PASS" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cmd", nargs="?", default="run")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.cmd == "selftest" or args.selftest:
        return selftest()
    if args.cmd == "check":
        return check()
    return run()


if __name__ == "__main__":
    sys.exit(main())
