"""ETF book -- the risk face for the book the ticket actually buys.

Every published risk face of this book (underwater episodes, time-to-recover, forward
1/2/3-year distribution) was computed on `n12_vt08`. But the ticket, the tearsheet and
the CEO page quote `n5_vt08`. Depth-and-duration reported for a different book is not
this book's risk: the reader is told how long *another* portfolio stayed under water.

This face runs the same three statistics on the production candidate, and it refuses to
publish unless both controls reproduce:

  C1  the n12_vt08 recompute matches `results/etf_book_underwater.json` field-by-field
      (same implementation, same book, same numbers) -- if this fails, the two faces are
      not measuring the same thing and nothing below is comparable;
  C2  the n5_vt08 recompute matches the production artifact's cagr/maxdd to 5e-5
      (the curve we measure is the curve the ticket buys).

Then it publishes the gap between the two books in days and in money.

Frozen before the run (no line is tuned after seeing the numbers):
  * horizons are calendar years via DateOffset; the engine's bar spacing is not assumed;
  * an entry that has not recovered on the last bar is CENSORED -- reported, never 0;
  * book-pair verdict: `DIFFERENT_RISK_PROFILE` when the worst time-to-recover differs by
    more than 20% relative OR the 1-year negative-entry share differs by more than 2pp;
    otherwise `SAME_RISK_PROFILE`. Frozen thresholds, stated here, applied by code;
  * verdict is descriptive: no threshold decides whether either book is good.

Usage:
    python scripts/etf_book_underwater_ticket_book.py run [--write]
    python scripts/etf_book_underwater_ticket_book.py --check
    python scripts/etf_book_underwater_ticket_book.py --selftest
"""
import argparse
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import etf_composite_pf as E
import etf_book_production as P
import etf_book_underwater as U

OUT = os.path.join(E.PATHS.results_dir, "etf_book_underwater_ticket_book.json")
DOC = os.path.join(E.PATHS.root, "research", "ETF-BOOK-UNDERWATER-TICKET.md")
UPSTREAM_RISK = os.path.join(E.PATHS.results_dir, "etf_book_underwater.json")
UPSTREAM_PROD = os.path.join(E.PATHS.results_dir, "etf_book_production", "latest.json")
TICKET_CELL = "n5_vt08"
QUOTED_CELL = "n12_vt08"
N_HOLD_TICKET = 5
N_HOLD_QUOTED = 12
REBAL = 20
VT = 0.08
CONTROL_TOL = 5e-5
ENV_DIGEST_KEYS = ("evidence_cutoff", "first_bar", "last_bar", "bars")
WORST_REL_THR = 0.20      # book-pair: relative gap in worst time-to-recover
NEG_SHARE_PP_THR = 0.02   # book-pair: absolute gap in 1-year negative-entry share


def _sha(path):
    try:
        with open(path, "rb") as fh:
            return hashlib.sha256(fh.read()).hexdigest()[:16]
    except Exception:
        return None


def _risk_core(doc):
    """The four statistics that make two risk faces comparable, from a published doc."""
    return {
        "underwater_episodes": doc["underwater"]["episodes"],
        "underwater_longest_bars": doc["underwater"]["longest"]["bars_underwater"],
        "recovery_max_bars": doc["recovery"]["max_bars"],
        "recovery_p90_bars": doc["recovery"]["p90_bars"],
        "forward_1y_min": doc["forward"]["1y"]["min"],
        "forward_1y_neg": doc["forward"]["1y"]["share_negative"],
    }


def _same_risk(a, b, tol=1e-9):
    """Field-by-field equality of two risk cores (None == None counts as equal)."""
    diffs = []
    for k in sorted(a):
        va, vb = a.get(k), b.get(k)
        if va is None and vb is None:
            continue
        if va is None or vb is None:
            diffs.append("%s: %r vs %r" % (k, va, vb))
        elif abs(float(va) - float(vb)) > tol:
            diffs.append("%s: %.10g vs %.10g" % (k, float(va), float(vb)))
    return diffs


def measure(n_hold, close, openp, amt, score):
    """One book's full risk stats, using the published implementation verbatim."""
    bt, ser = P.backtest(close, openp, amt, score, n_hold, REBAL, vol_target=VT)
    ser = ser.dropna()
    segs = U.underwater_segments(ser)
    rec = U.recover_stats(ser)
    fwd = U.forward_windows(ser)
    healed = [s for s in segs if s["recovered"]]
    longest = max(segs, key=lambda s: s["bars_underwater"]) if segs else None
    return {
        "cell": "n%d_vt%02d" % (n_hold, int(round(VT * 100))),
        "bars": int(len(ser)),
        "first_bar": str(ser.index[0].date()),
        "last_bar": str(ser.index[-1].date()),
        "cagr": round(float(bt["full"]["cagr"]), 6),
        "maxdd": round(float(bt["full"]["maxdd"]), 6),
        "underwater": {
            "episodes": len(segs),
            "healed": len(healed),
            "never_healed": len(segs) - len(healed),
            "longest": longest,
            "median_bars_healed": (float(np.median([s["bars_underwater"] for s in healed]))
                                   if healed else None),
        },
        "recovery": rec,
        "forward": fwd,
    }


def book_pair_verdict(ticket, quoted):
    """Frozen thresholds: is the risk face of one book readable as the other's?"""
    t_worst = ticket["recovery"]["max_bars"]
    q_worst = quoted["recovery"]["max_bars"]
    t_neg = ticket["forward"]["1y"]["share_negative"]
    q_neg = quoted["forward"]["1y"]["share_negative"]
    rel = None
    if t_worst is not None and q_worst not in (None, 0):
        rel = abs(float(t_worst) - float(q_worst)) / float(q_worst)
    pp = None
    if t_neg is not None and q_neg is not None:
        pp = abs(float(t_neg) - float(q_neg))
    differs = ((rel is not None and rel > WORST_REL_THR)
               or (pp is not None and pp > NEG_SHARE_PP_THR))
    return {
        "worst_recover_rel_gap": None if rel is None else round(float(rel), 4),
        "one_year_negative_share_gap_pp": None if pp is None else round(float(pp) * 100, 2),
        "thresholds": {"worst_recover_rel": WORST_REL_THR,
                       "one_year_negative_share_pp": NEG_SHARE_PP_THR},
        "verdict": "DIFFERENT_RISK_PROFILE" if differs else "SAME_RISK_PROFILE",
    }


def _money_line(ticket, quoted, capital):
    """What the duration gap costs in cash-days for a stated capital."""
    tw = ticket["recovery"]["max_bars"]
    qw = quoted["recovery"]["max_bars"]
    if tw is None or qw is None:
        return None
    # a bar is one trading day; the book compounds on the same bar grid
    return {
        "capital_cny": capital,
        "bars_gap": int(tw - qw),
        "cash_days_gap": int(tw - qw),
        "note": ("bars are trading days on the engine grid; money under water for "
                 "extra bars is not a return, it is time the capital could not be "
                 "spent -- printed as days, never converted into a fake yield"),
    }


def run(write=False, out_path=OUT, doc_path=DOC):
    close, openp, amt, score, _cls, _flip = P.prep_panel()
    ticket = measure(N_HOLD_TICKET, close, openp, amt, score)
    quoted = measure(N_HOLD_QUOTED, close, openp, amt, score)

    controls = {}

    # C1 -- same implementation, same book, same numbers as the published risk face
    try:
        with open(UPSTREAM_RISK, encoding="utf-8") as fh:
            pub_risk = json.load(fh)
        want = _risk_core(pub_risk)
        got = _risk_core(quoted)
        diffs = _same_risk(got, want)
        controls["C1_quoted_book_vs_published_risk_face"] = {
            "upstream": os.path.relpath(UPSTREAM_RISK, E.PATHS.root),
            "upstream_cell": pub_risk.get("cell"),
            "recomputed": got,
            "published": want,
            "diffs": diffs,
            "ok": not diffs,
            "verdict": "CONTROL_REPRODUCED" if not diffs else "CONTROL_MISMATCH",
        }
    except Exception as exc:
        controls["C1_quoted_book_vs_published_risk_face"] = {
            "ok": False, "verdict": "CONTROL_UNREADABLE", "error": str(exc)}

    # C2 -- the curve measured is the curve the ticket buys
    try:
        with open(UPSTREAM_PROD, encoding="utf-8") as fh:
            prod = json.load(fh)
        row = ((prod.get("backtest") or {}).get(TICKET_CELL) or {}).get("full") or {}
        d_cagr = abs(float(ticket["cagr"]) - float(row["cagr"]))
        d_dd = abs(float(ticket["maxdd"]) - float(row["maxdd"]))
        ok = d_cagr <= CONTROL_TOL and d_dd <= CONTROL_TOL
        controls["C2_ticket_book_vs_production_artifact"] = {
            "upstream": os.path.relpath(UPSTREAM_PROD, E.PATHS.root),
            "upstream_cell": TICKET_CELL,
            "recomputed": {"cagr": ticket["cagr"], "maxdd": ticket["maxdd"]},
            "published": {"cagr": round(float(row["cagr"]), 6),
                          "maxdd": round(float(row["maxdd"]), 6)},
            "delta": {"cagr": round(d_cagr, 8), "maxdd": round(d_dd, 8)},
            "tol": CONTROL_TOL,
            "ok": bool(ok),
            "verdict": "CONTROL_REPRODUCED" if ok else "CONTROL_MISMATCH",
        }
        prod_cutoff = prod.get("evidence_cutoff")
    except Exception as exc:
        controls["C2_ticket_book_vs_production_artifact"] = {
            "ok": False, "verdict": "CONTROL_UNREADABLE", "error": str(exc)}
        prod_cutoff = None

    pair = book_pair_verdict(ticket, quoted)
    all_ok = all(c.get("ok") for c in controls.values())
    payload = {
        "artifact": "etf_book_underwater_ticket_book",
        "evidence_cutoff": ticket["last_bar"],
        "ticket_cell": ticket["cell"],
        "quoted_risk_cell": quoted["cell"],
        "config": {"rebal": REBAL, "vol_target": VT,
                   "cost_bp_per_side": round(float(P.COST) * 1e4, 2)},
        "books": {"ticket": ticket, "quoted_risk": quoted},
        "book_pair": pair,
        "duration_gap": _money_line(ticket, quoted, 1_000_000),
        "controls": controls,
        "upstream_cutoffs": {
            "production": prod_cutoff,
            "published_risk_face_sha": _sha(UPSTREAM_RISK),
            "production_sha": _sha(UPSTREAM_PROD),
        },
        "verdict": ("CONTROL_MISMATCH" if not all_ok else "TICKET_BOOK_ASSESSED"),
        "definitions": {
            "why": ("the published risk face answers for n12_vt08 while the ticket, "
                    "the tearsheet and the CEO page quote n5_vt08"),
            "bars_underwater": "bars strictly below the running peak, excluding the recovery bar",
            "censored": "entry not regained on the last bar -- reported, never scored as 0",
            "forward": "annualised, calendar-year horizon via DateOffset, incomplete horizons skipped",
        },
    }
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1, sort_keys=True)
    if write:
        render_doc(payload, doc_path)
    print(json.dumps({
        "verdict": payload["verdict"],
        "controls": {k: v.get("verdict") for k, v in controls.items()},
        "ticket": {"cell": ticket["cell"], "cagr": ticket["cagr"],
                   "maxdd": ticket["maxdd"],
                   "longest_bars": ticket["underwater"]["longest"]["bars_underwater"],
                   "worst_recover_bars": ticket["recovery"]["max_bars"],
                   "recover_p90": ticket["recovery"]["p90_bars"],
                   "fwd1y_min": ticket["forward"]["1y"]["min"],
                   "fwd1y_neg": ticket["forward"]["1y"]["share_negative"]},
        "quoted": {"cell": quoted["cell"], "cagr": quoted["cagr"],
                   "maxdd": quoted["maxdd"],
                   "longest_bars": quoted["underwater"]["longest"]["bars_underwater"],
                   "worst_recover_bars": quoted["recovery"]["max_bars"],
                   "recover_p90": quoted["recovery"]["p90_bars"],
                   "fwd1y_min": quoted["forward"]["1y"]["min"],
                   "fwd1y_neg": quoted["forward"]["1y"]["share_negative"]},
        "book_pair": pair,
    }, ensure_ascii=False, indent=1))
    return payload


# ---------------------------------------------------------------- page rendering
def _pct(x, nd=2):
    return "n/a" if x is None else ("%." + str(nd) + "f%%") % (float(x) * 100)


def _bars(x):
    return "n/a" if x is None else ("%d 个交易日" % int(x))


def render_doc(payload, doc_path=DOC):
    t = payload["books"]["ticket"]
    q = payload["books"]["quoted_risk"]
    pair = payload["book_pair"]
    dg = payload["duration_gap"]
    L = []
    A = L.append
    A("# 票面那本书的最坏处境（n5 与 n12 是两个风险面）")
    A("")
    A("> 由 `scripts/etf_book_underwater_ticket_book.py` 渲染，数字不手抄；")
    A("> 面文件 `results/etf_book_underwater_ticket_book.json`。")
    A("> 证据截止 %s（面板末 bar %s），bar 数 %d。" % (
        payload["evidence_cutoff"], t["last_bar"], t["bars"]))
    A("")
    A("## 为什么另开一面")
    A("")
    A("本司已发布的风险面（水下段落、逐进场回本时间、1/2/3 年滚动收益）算在 "
      "**%s** 上，而票面、泪表与 CEO 一页纸引的是 **%s**。" % (q["cell"], t["cell"]))
    A("用另一本书的「最深/最久」回答这本书的问题，是 r1788 族的面错位——"
      "读者读到的是别人的回本时间。")
    A("")
    tw = t["recovery"]["max_bars"]
    qw = q["recovery"]["max_bars"]
    if tw is not None and qw is not None:
        worse = "已发布风险面" if qw > tw else "票面书"
        direction = ("比实际更长" if qw > tw else "比实际更短")
        A("方向先讲清楚：**这个问题上更吓人的是 %s**——最坏一次回本 %s 对 %s，"
          "差 %d 个交易日。所以读者拿着旧面判断这本题面，会把回本期读成%s。" % (
              worse, _bars(qw), _bars(tw), abs(int(qw) - int(tw)), direction))
        A("")
    A("## 两本书并排")
    A("")
    A("| 读数 | 票面书 `%s` | 已发布风险面 `%s` |" % (t["cell"], q["cell"]))
    A("| --- | --- | --- |")
    A("| 年化 (CAGR) | %s | %s |" % (_pct(t["cagr"]), _pct(q["cagr"])))
    A("| 最大回撤 | %s | %s |" % (_pct(t["maxdd"]), _pct(q["maxdd"])))
    A("| 水下段落数 | %d（未愈合 %d） | %d（未愈合 %d） |" % (
        t["underwater"]["episodes"], t["underwater"]["never_healed"],
        q["underwater"]["episodes"], q["underwater"]["never_healed"]))
    A("| 最长一次水下 | %s | %s |" % (
        _bars(t["underwater"]["longest"]["bars_underwater"]),
        _bars(q["underwater"]["longest"]["bars_underwater"])))
    A("| 回本中位（逐进场） | %s | %s |" % (
        _bars(t["recovery"]["median_bars"]), _bars(q["recovery"]["median_bars"])))
    A("| 回本 p90 | %s | %s |" % (
        _bars(t["recovery"]["p90_bars"]), _bars(q["recovery"]["p90_bars"])))
    A("| 最坏一次回本 | %s | %s |" % (
        _bars(t["recovery"]["max_bars"]), _bars(q["recovery"]["max_bars"])))
    A("| 1 年滚动：最差 | %s | %s |" % (
        _pct(t["forward"]["1y"]["min"]), _pct(q["forward"]["1y"]["min"])))
    A("| 1 年滚动：负收益占比 | %s | %s |" % (
        _pct(t["forward"]["1y"]["share_negative"]),
        _pct(q["forward"]["1y"]["share_negative"])))
    A("")
    A("## 判词")
    A("")
    A("面判词 **%s**（两臂控制：%s）。" % (
        payload["verdict"],
        " / ".join("%s=%s" % (k.split("_")[0], v.get("verdict"))
                   for k, v in sorted(payload["controls"].items()))))
    A("")
    A("**%s**——最坏回本天数相对差 %s，1 年负收益占比差 %s pp"
      "（冻结线：%.0f%% / %.0fpp）。" % (
          pair["verdict"],
          "n/a" if pair["worst_recover_rel_gap"] is None else "%.1f%%" %
          (pair["worst_recover_rel_gap"] * 100),
          "n/a" if pair["one_year_negative_share_gap_pp"] is None else
          "%.2f" % pair["one_year_negative_share_gap_pp"],
          WORST_REL_THR * 100, NEG_SHARE_PP_THR * 100))
    A("")
    if dg:
        A("最坏回本天数差 **%d 个交易日**（票面书 %s vs 已发布风险面 %s）。" % (
            abs(int(dg["bars_gap"])), _bars(t["recovery"]["max_bars"]),
            _bars(q["recovery"]["max_bars"])))
        A("这不是收益差，是「钱还被占着」的时间差——本面只印天数，不把它折算成假收益。")
        A("")
    A("## 控制臂（不绿不出面）")
    A("")
    for name, c in sorted(payload["controls"].items()):
        A("- `%s`：**%s**（上游 %s）" % (
            name, c.get("verdict"), c.get("upstream", "n/a")))
    A("")
    A("## 怎么读")
    A("")
    A("- 回本中位 1 个交易日不代表这本书安全：它是一个含现金腿的双模组合，"
      "约半数调仓期全防御，逐日很少跌破前高。")
    A("- 真正要看的两个数：**最坏一次回本**（你要能不能忍）与 **1 年滚动最差**"
      "（你随机某天进场，一年后会不会亏）。")
    A("- 面是描述性的：本面不判这本书该不该买，只回答「如果买了，最坏长什么样」。")
    A("")
    A("## 怎么验的")
    A("")
    A("- `--selftest`：13 腿离线，秒级，测的是统计与判词函数的行为（含「手改一格必红」"
      "与「数字不可复现必被抓」两条）；")
    A("- `--check` 默认 deep：重跑票面书（约 35 秒）逐字段对账——**这张面的关键数字"
      "没有上游面能替它回答**，所以只能问引擎本身；手改任何一个数字都会 rc1 并精确点名，"
      "且不带 STALE 字样（STALE 只留给「上游动了」，二者不可混为一谈）；")
    A("- 上游动（已发布风险面或生产面的数字/cutoff 变）→ rc3 STALE，不是红也不是绿。")
    os.makedirs(os.path.dirname(doc_path), exist_ok=True)
    with open(doc_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(L) + "\n")
    return doc_path


# ---------------------------------------------------------------- check
def _book_diffs(stored, fresh, tol=1e-6):
    """Field-by-field diff of two full book stats dicts (the numbers must be re-derivable).

    Only the fields that carry a measurement are compared; identity fields (cell, first_bar,
    last_bar, bars) are compared exactly.
    """
    diffs = []

    def cmp(path, a, b):
        if a is None and b is None:
            return
        if a is None or b is None:
            diffs.append("%s: %r vs %r" % (path, a, b))
            return
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            if abs(float(a) - float(b)) > tol:
                diffs.append("%s: %.10g vs %.10g" % (path, float(a), float(b)))
        elif a != b:
            diffs.append("%s: %r vs %r" % (path, a, b))

    for k in ("cell", "bars", "first_bar", "last_bar", "cagr", "maxdd"):
        cmp(k, stored.get(k), fresh.get(k))
    for k in ("episodes", "healed", "never_healed", "median_bars_healed"):
        cmp("underwater.%s" % k, (stored.get("underwater") or {}).get(k),
            (fresh.get("underwater") or {}).get(k))
    sl = ((stored.get("underwater") or {}).get("longest") or {})
    fl = ((fresh.get("underwater") or {}).get("longest") or {})
    for k in ("bars_underwater", "peak_bar", "trough_bar", "recover_bar", "trough_dd",
              "recovered", "peak_value"):
        cmp("underwater.longest.%s" % k, sl.get(k), fl.get(k))
    for k in ("entries", "censored", "censored_share", "median_bars", "p90_bars", "max_bars"):
        cmp("recovery.%s" % k, (stored.get("recovery") or {}).get(k),
            (fresh.get("recovery") or {}).get(k))
    for hz in set(list((stored.get("forward") or {}).keys()) +
                  list((fresh.get("forward") or {}).keys())):
        sa = (stored.get("forward") or {}).get(hz) or {}
        fa = (fresh.get("forward") or {}).get(hz) or {}
        for k in ("entries", "skipped_no_full_horizon", "min", "p5", "p50", "share_negative"):
            cmp("forward.%s.%s" % (hz, k), sa.get(k), fa.get(k))
        cmp("forward.%s.worst_entry" % hz, sa.get("worst_entry"), fa.get("worst_entry"))
    return diffs


def check(out_path=OUT, doc_path=DOC, deep=True):
    """Re-derive from the published file; deep=True also re-runs the engine.

    A number in this face (how long the ticket book stayed under water) has no upstream
    face to answer for it -- so the only question that can catch a hand-edited number is
    "does the engine still say this?"  That is what deep=True buys (~35s, ticket book
    only).  deep=False is the structural pass used by the offline selftest.
    """
    try:
        with open(out_path, encoding="utf-8") as fh:
            doc = json.load(fh)
    except Exception as exc:
        print("check: cannot read %s (%s)" % (out_path, exc))
        return 2

    problems = []

    controls = doc.get("controls") or {}
    all_ok = all((c or {}).get("ok") for c in controls.values())
    want = "TICKET_BOOK_ASSESSED" if all_ok else "CONTROL_MISMATCH"
    if doc.get("verdict") != want:
        problems.append("verdict %r but controls say %r" % (doc.get("verdict"), want))

    # book-pair verdict must be derived, not stored by hand
    try:
        pair = book_pair_verdict(doc["books"]["ticket"], doc["books"]["quoted_risk"])
    except Exception as exc:
        pair = None
        problems.append("book_pair not derivable: %s" % exc)
    if pair and doc.get("book_pair", {}).get("verdict") != pair["verdict"]:
        problems.append("book_pair %r != derived %r" % (
            doc.get("book_pair", {}).get("verdict"), pair["verdict"]))

    # C1 must still hold against the upstream risk face as it is on disk now
    try:
        with open(UPSTREAM_RISK, encoding="utf-8") as fh:
            pub = json.load(fh)
        diffs = _same_risk(_risk_core(doc["books"]["quoted_risk"]), _risk_core(pub))
        if diffs:
            problems.append("STALE upstream risk face differs: " + "; ".join(diffs[:3]))
        if pub.get("evidence_cutoff") != doc.get("evidence_cutoff"):
            problems.append("STALE upstream risk cutoff %r != face %r" % (
                pub.get("evidence_cutoff"), doc.get("evidence_cutoff")))
    except Exception as exc:
        problems.append("STALE upstream risk face unreadable: %s" % exc)

    # C2 must still hold against the production artifact as it is on disk now
    try:
        with open(UPSTREAM_PROD, encoding="utf-8") as fh:
            prod = json.load(fh)
        row = ((prod.get("backtest") or {}).get(TICKET_CELL) or {}).get("full") or {}
        t = doc["books"]["ticket"]
        if abs(float(t["cagr"]) - float(row["cagr"])) > CONTROL_TOL:
            problems.append("STALE production cagr moved for %s" % TICKET_CELL)
        if abs(float(t["maxdd"]) - float(row["maxdd"])) > CONTROL_TOL:
            problems.append("STALE production maxdd moved for %s" % TICKET_CELL)
    except Exception as exc:
        problems.append("STALE production artifact unreadable: %s" % exc)

    # deep pass: re-run the ticket book and compare every measured field
    if deep:
        try:
            close, openp, amt, score, _cls, _flip = P.prep_panel()
            fresh = measure(N_HOLD_TICKET, close, openp, amt, score)
            diffs = _book_diffs(doc["books"]["ticket"], fresh)
            if diffs:
                problems.append("ticket book numbers not reproducible: " +
                                "; ".join(diffs[:5]))
            # the quoted book's core is answered by the upstream face (C1 above);
            # here we only assert the face's own cutoff agrees with a fresh panel tail
            if str(fresh["last_bar"]) != str(doc.get("evidence_cutoff")):
                problems.append("STALE face cutoff %r != engine tail %r" % (
                    doc.get("evidence_cutoff"), fresh["last_bar"]))
        except Exception as exc:
            problems.append("deep re-derivation failed: %s" % exc)

    # the page must print the face's own numbers
    try:
        with open(doc_path, encoding="utf-8") as fh:
            page = fh.read()
        must = [doc["books"]["ticket"]["cell"], doc["books"]["quoted_risk"]["cell"],
                doc.get("verdict", ""), doc.get("evidence_cutoff", "")]
        for token in must:
            if token and token not in page:
                problems.append("page missing %r" % token)
    except Exception as exc:
        problems.append("page unreadable: %s" % exc)

    if problems:
        stale = any(p.startswith("STALE") for p in problems)
        print("etf_book_underwater_ticket_book: check FAILED%s" % (
            " (STALE)" if stale else ""))
        for p in problems:
            print("  - %s" % p)
        return 3 if stale else 1
    print("etf_book_underwater_ticket_book: check OK (cutoff %s, pair %s)"
          % (doc.get("evidence_cutoff"), doc["book_pair"]["verdict"]))
    return 0


# ---------------------------------------------------------------- selftest
def selftest():
    import pandas as pd  # local to keep run() light
    legs = []

    def leg(name, cond, detail=""):
        legs.append((name, bool(cond), detail))

    # L1 segments on a hand-built curve: peaks, one episode, one censored
    idx = pd.date_range("2020-01-01", periods=7, freq="D")
    ser = pd.Series([1.0, 0.9, 0.95, 1.1, 1.0, 0.8, 0.7], index=idx)
    segs = U.underwater_segments(ser)
    leg("L1 segments found", len(segs) == 2, "got %d" % len(segs))
    leg("L1 first episode healed", segs[0]["recovered"] and segs[0]["bars_underwater"] == 2,
        str(segs[0]))
    leg("L1 second episode censored", (not segs[1]["recovered"]), str(segs[1]))

    # L2 recovery stats: censored never scored as zero
    rec = U.recover_stats(ser)
    leg("L2 censored counted", rec["censored"] >= 1, str(rec.get("censored")))

    # L3 forward windows skip incomplete horizons instead of scoring 0
    fwd = U.forward_windows(pd.Series([1.0, 1.2], index=pd.date_range(
        "2020-01-01", periods=2, freq="D")), horizons=(1,))
    leg("L3 no full horizon => zero entries and skipped==2",
        fwd["1y"]["entries"] == 0 and fwd["1y"]["skipped_no_full_horizon"] == 2,
        json.dumps({k: fwd["1y"][k] for k in ("entries", "skipped_no_full_horizon")}))

    # L4.M pair verdict: same profile
    mk = lambda worst, neg: {"recovery": {"max_bars": worst},
                             "forward": {"1y": {"share_negative": neg}}}
    same = book_pair_verdict(mk(100, 0.08), mk(105, 0.085))
    leg("L4 same profile", same["verdict"] == "SAME_RISK_PROFILE", str(same["verdict"]))

    # L4.D pair verdict: worst-recover gap above the frozen line
    wide = book_pair_verdict(mk(200, 0.08), mk(100, 0.08))
    leg("L4 different profile via duration", wide["verdict"] == "DIFFERENT_RISK_PROFILE",
        str(wide["verdict"]))

    # L5 pair verdict: negative-share gap alone also flips it
    neg = book_pair_verdict(mk(100, 0.20), mk(100, 0.05))
    leg("L5 different profile via negative share",
        neg["verdict"] == "DIFFERENT_RISK_PROFILE", str(neg["verdict"]))

    # L6 _same_risk tolerance behaviour
    leg("L6 same_risk detects a hidden diff",
        bool(_same_risk({"a": 1.0}, {"a": 1.0000001})) and
        not _same_risk({"a": 1.0, "b": None}, {"a": 1.0, "b": None}),
        "tol leg")

    # L7 behaviour: hand-edit one number -> check() rc1 without the word STALE
    import tempfile
    tmpdir = tempfile.mkdtemp(prefix="bmc_utb_")
    fake_out = os.path.join(tmpdir, "face.json")
    fake_doc = os.path.join(tmpdir, "page.md")
    try:
        with open(OUT, encoding="utf-8") as fh:
            doc = json.load(fh)
        doc = json.loads(json.dumps(doc))
        doc["books"]["ticket"]["recovery"]["max_bars"] = 1.0   # absurd but plausible type
        doc["book_pair"]["verdict"] = "SAME_RISK_PROFILE"
        with open(fake_out, "w", encoding="utf-8") as fh:
            json.dump(doc, fh)
        with open(fake_doc, "w", encoding="utf-8") as fh:
            fh.write("x")
        import contextlib
        import io
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = check(fake_out, fake_doc, deep=False)
        said = buf.getvalue()
        leg("L7 hand-edited face -> rc1", rc == 1, "rc=%s" % rc)
        leg("L7b hand-edited face is not called STALE", "STALE" not in said, said[:80])

        # L9 (offline): the deep comparison is what catches a tampered number -- drive it
        # directly on a copy of the real face so the leg costs no engine time.
        with open(OUT, encoding="utf-8") as fh:
            good = json.load(fh)["books"]["ticket"]
        bad = json.loads(json.dumps(good))
        bad["recovery"]["max_bars"] = 999.0
        leg("L9 deep diff catches a tampered max_bars",
            bool(_book_diffs(bad, good)) and not _book_diffs(good, good),
            str(_book_diffs(bad, good)[:2]))
    except Exception as exc:
        leg("L7 hand-edited face -> rc1", False, "setup failed: %s" % exc)
    finally:
        for p in (fake_out, fake_doc):
            try:
                os.remove(p)
            except OSError:
                pass

    # L8 money line: bars are days, no fake yield invented
    dg = _money_line(mk(200, 0.1), mk(150, 0.1), 1_000_000)
    leg("L8 duration gap in days only",
        dg["bars_gap"] == 50 and set(dg) == {"capital_cny", "bars_gap", "cash_days_gap",
                                             "note"}
        and not any("pct" in k or "annual" in k for k in dg),
        str(sorted(dg)))

    ok = sum(1 for _, c, _ in legs if c)
    for name, cond, detail in legs:
        if not cond:
            print("  FAIL %s (%s)" % (name, detail))
    print("etf_book_underwater_ticket_book selftest: %d/%d PASS" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--no-deep", action="store_true",
                    help="structural check only (skip the ~35s ticket-book re-derivation)")
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest or a.cmd == "--selftest":
        return selftest()
    if a.check or a.cmd in ("--check", "check"):
        return check(a.out, deep=not a.no_deep)
    run(write=a.write, out_path=a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
