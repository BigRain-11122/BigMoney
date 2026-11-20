#!/usr/bin/env python3
"""The same three rulers over the year axis: how much of "this book is good" is the era?

``etf_book_start_grid`` (r1869) exhausted one rebalance block and produced a reading the
five-point phase face could not: the distance of a refusal to its line, measured against the
size of the step the same ruler takes when the start moves by ONE BAR. It closed with its own
limit -- "25 rows are 25 views of one price series" -- and named the next question: is the
gate reading a property of the book, or of the era the series was started in?

This face asks that question on the year axis, in the same currency:

* **anchors** -- the book is priced at the first bar of each year 2015..2025 (11 starts). The
  per-start verdicts, the four-word aggregate and the three rulers are
  ``etf_book_phase_admission``'s / ``candidate_year_gate``'s own functions, imported.
* **era step** -- the median one-YEAR step of each ruler, printed next to the one-BAR step
  that the start-grid face already published (read from its receipt, not recomputed). The
  ratio is the new number: how many bars of warm-up one year of start is worth.
* **where the money came from** -- the earliest anchor's level curve, cut into calendar years
  and into four eras, with each era's share of the summed yearly return. That answers the
  half of "is it the book or the era" that a verdict word cannot: the money is not spread
  evenly over the tape.

Two things this face must say out loud, because they change how the anchors are read:

1. the gate's out-of-sample window is FIXED at 2024-01-01 (``GATE_OOS_START``). Moving the
   start earlier does not add OOS evidence -- it adds in-sample warm-up. So S1 at, say,
   2015-01-05 is the same 690 OOS bars reached by a nine-year-longer path; what an anchor
   measures is the path, not more evidence.
2. membership is today's (the bond-free universe and the volatility classes are derived from
   the whole panel). A 2015 anchor is today's names priced backwards, not the ETF menu of
   2015.

Nothing here moves a gate line: the thresholds are ``candidate_year_gate``'s, the verdict
words are its ``decision_block``, and the aggregate is ``etf_book_phase_admission.aggregate``.

    python scripts/etf_book_era_grid.py run       # ~2 min (11 repricings + one universe build)
    python scripts/etf_book_era_grid.py check     # re-derive the words and the sums
    python scripts/etf_book_era_grid.py selftest  # fixtures only
"""

import argparse
import io
import json
import os
import statistics
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)

import pandas as pd  # noqa: E402

import candidate_year_gate as G  # noqa: E402
import etf_book_phase_admission as PA  # noqa: E402
import etf_book_scale_floor as S  # noqa: E402
import etf_equity_alpha as A  # noqa: E402

OUT = os.path.join(ROOT, "results", "etf_book_era_grid.json")
GATE = PA.GATE
GRID_FACE = os.path.join(ROOT, "results", "etf_book_start_grid.json")
BOOK = PA.BOOK
ANCHOR_FROM_YEAR = 2015
ANCHOR_TO_YEAR = 2025
ERAS = (("2015-2017", 2015, 2017), ("2018-2020", 2018, 2020),
        ("2021-2023", 2021, 2023), ("2024-2026", 2024, 2026))


def year_anchors(index, first=ANCHOR_FROM_YEAR, last=ANCHOR_TO_YEAR):
    """The first bar on or after 1 January of each year -- a pure slice of the panel index."""
    out = []
    for y in range(first, last + 1):
        cut = pd.Timestamp("%04d-01-01" % y)
        after = [d for d in index if d >= cut]
        if not after:
            continue
        # a panel that starts mid-year has no anchor for that year: labelling the panel's
        # first bar as "2015-01-01" would print a year the panel never saw (self-caught by
        # selftest L2 on a 2016-03-01 start).
        if pd.Timestamp(after[0]).year != y:
            continue
        out.append({"year": y, "label": "%04d-01-01" % y,
                    "first_bar": str(pd.Timestamp(after[0]).date())})
    return out


def _levels(ser):
    """A level curve with its NaN bars dropped and its index sorted."""
    s = ser.dropna()
    return s[s.index.notna()]


def calendar_returns(ser, upto_year=None):
    """Year-by-year net return in percent, read off the level curve itself.

    The first year measures from the series' own first bar (there is no prior close), the
    last year is partial whenever the panel's last bar is not a 31 December -- and it is
    printed as partial rather than annualised, because a partial year is a real return.
    """
    s = _levels(ser)
    if s.empty:
        return []
    rows = []
    years = sorted({int(d.year) for d in s.index})
    for i, y in enumerate(years):
        sl = s[[int(d.year) == y for d in s.index]]
        if sl.empty:
            continue
        if i == 0:
            base = float(sl.iloc[0])
        else:
            prev = s[[int(d.year) < y for d in s.index]]
            if prev.empty:
                base = float(sl.iloc[0])
            else:
                base = float(prev.iloc[-1])
        if base <= 0:
            continue
        last = float(sl.iloc[-1])
        bars = int(len(sl))
        # A year is full when it ran into December AND the panel keeps going past it. The
        # trading calendar rarely prints a 12-31 bar (30 Dec is the last session most years),
        # so "must end on 12-31" would label a dozen complete years partial -- the flag is
        # only for a year the panel CUT SHORT (the current one) or one it started inside.
        last_ts = pd.Timestamp(sl.index[-1])
        continues = any(int(d.year) > y for d in s.index)
        full = last_ts.month == 12 and continues and bars >= 200
        rows.append({"year": y, "net_pct": round((last / base - 1.0) * 100.0, 4),
                     "bars": bars, "partial": not full,
                     "first_bar": str(pd.Timestamp(sl.index[0]).date()),
                     "last_bar": str(last_ts.date())})
    if upto_year is not None:
        rows = [r for r in rows if r["year"] <= upto_year]
    return rows


def era_rows(ser, years):
    """Group the calendar rows into eras and price each era on its own bars."""
    s = _levels(ser)
    out = []
    for name, lo, hi in ERAS:
        members = [r for r in years if lo <= r["year"] <= hi]
        sl = s[[lo <= int(d.year) <= hi for d in s.index]]
        st = A.stats2(sl, name)
        out.append({"era": name, "years": [r["year"] for r in members],
                    "net_pct_sum": round(sum(r["net_pct"] for r in members), 4),
                    "positive_years": sum(1 for r in members if r["net_pct"] > 0),
                    "worst_year_pct": (round(min(r["net_pct"] for r in members), 4)
                                       if members else None),
                    "best_year_pct": (round(max(r["net_pct"] for r in members), 4)
                                      if members else None),
                    "bars": int(len(sl)),
                    "cagr_pct": None if st.get("cagr") is None
                                else round(float(st["cagr"]) * 100.0, 4),
                    "sharpe": None if st.get("sharpe") is None
                              else round(float(st["sharpe"]), 4),
                    "maxdd_pct": None if st.get("maxdd") is None
                                 else round(float(st["maxdd"]) * 100.0, 4),
                    "has_partial_year": any(r["partial"] for r in members)})
    total = sum(r["net_pct_sum"] for r in out)
    for r in out:
        r["share_of_sum"] = (round(r["net_pct_sum"] / total, 4) if total else None)
    return out, round(total, 4)


def step_readings(rows, key, value_key):
    """Median one-year step of one ruler, plus the bar step the start grid published."""
    vals = [float(r[value_key]) for r in rows if r.get(value_key) is not None]
    jumps = [round(abs(b - a), 4) for a, b in zip(vals, vals[1:])]
    return {"readable": len(vals),
            "min": round(min(vals), 4) if vals else None,
            "median": round(statistics.median(vals), 4) if vals else None,
            "max": round(max(vals), 4) if vals else None,
            "spread": round(max(vals) - min(vals), 4) if vals else None,
            "one_year_step_median": round(statistics.median(jumps), 4) if jumps else None,
            "one_year_step_max": round(max(jumps), 4) if jumps else None,
            "ruler": key}


def bar_steps(path=GRID_FACE):
    """The one-bar steps already published by etf_book_start_grid -- read, never recomputed."""
    try:
        with io.open(path, encoding="utf-8") as f:
            d = json.load(f)
    except Exception:                                            # noqa: BLE001
        return {}
    dist = d.get("distribution") or {}
    out = {}
    for key in ("S1_oos_sharpe", "A1_cagr_after_cost"):
        jm = (dist.get(key) or {}).get("neighbour_jump_median")
        out[key] = {"one_bar_step_median": jm, "source": "results/etf_book_start_grid.json",
                    "starts": dist.get("starts"), "asof": d.get("asof")}
    return out


def resolution(era, bars):
    """One year of start, measured in the bars it is worth -- per ruler."""
    out = {}
    for key, unit in (("S1_oos_sharpe", "sharpe"), ("A1_cagr_after_cost", "pp")):
        yr = era.get(key) or {}
        br = bars.get(key) or {}
        es, bs = yr.get("one_year_step_median"), br.get("one_bar_step_median")
        ratio = None
        if es is not None and bs:
            ratio = round(float(es) / float(bs), 2)
        out[key] = {"unit": unit,
                    "one_year_step_median": es,
                    "one_bar_step_median": bs,
                    "years_per_bar_step": ratio,
                    "bar_step_source": br.get("source"),
                    "readable": es is not None and bs is not None,
                    "sentence": (
                        "no bar step is published, so the two steps are not compared"
                        if ratio is None else
                        "moving the start by one year moves this ruler by %.4f (%s), one "
                        "bar by %.4f: a year of start is worth %.2f bar-steps"
                        % (es, unit, bs, ratio))}
    return out


def run() -> int:
    t0 = time.time()
    close, openp, amt, sc, n_flip = S.nobond_universe()
    picks, advs, adv_weakest = PA.live_picks(sc, amt)
    anchors = year_anchors(openp.index)
    rows = []
    base_ser = None
    for a in anchors:
        ser, turn = PA.P.arm(close, openp, amt, sc, 0.08, 0.0, a["label"])
        if base_ser is None:
            base_ser = ser
        osr = G.oos_sharpe(ser)
        cagr = A.stats2(ser, BOOK).get("cagr")
        cagr_pct = None if cagr is None else round(float(cagr) * 100.0, 4)
        blk = G.decision_block(osr, cagr_pct, adv_weakest, len(picks) or None)
        s = _levels(ser)
        rows.append({"year": a["year"], "start": a["label"], "verdict": blk["verdict"],
                     "oos_sharpe": osr, "cagr_pct": cagr_pct,
                     "checks": blk["checks"], "failed_checks": blk["failed_checks"],
                     "bars": int(len(s)),
                     "first_bar": str(pd.Timestamp(s.index[0]).date()),
                     "last_bar": str(pd.Timestamp(s.index[-1]).date()),
                     "turnover_per_side": round(float(turn), 3)})
        print("  %s -> %-12s oos_sharpe %s cagr %s bars %d"
              % (a["label"], blk["verdict"], osr, cagr_pct, len(s)), flush=True)

    agg = PA.aggregate(rows)
    print("%s over %d year anchors -> %s (%s)"
          % (BOOK, len(rows), agg["state"], agg.get("reason")), flush=True)

    era_step = {"S1_oos_sharpe": step_readings(rows, "S1_oos_sharpe", "oos_sharpe"),
                "A1_cagr_after_cost": step_readings(rows, "A1_cagr_after_cost", "cagr_pct")}
    bars = bar_steps()
    res = resolution(era_step, bars)
    for key, blk in res.items():
        print("  %s: %s" % (key, blk["sentence"]), flush=True)

    years = calendar_returns(base_ser)
    eras, total = era_rows(base_ser, years)
    print("  money by era: %s" % json.dumps(
        [{"era": e["era"], "sum_pct": e["net_pct_sum"], "share": e["share_of_sum"]}
         for e in eras], ensure_ascii=False), flush=True)

    # cross-face: 2020-01-01 is both a year anchor and the first start of the block grid.
    cross = {"grid_face": None, "compared": [], "disagreements": []}
    try:
        with io.open(GRID_FACE, encoding="utf-8") as f:
            gf = json.load(f)
        cross["grid_face"] = {"asof": gf.get("asof"), "evidence_cutoff": gf.get("evidence_cutoff"),
                              "starts": (gf.get("distribution") or {}).get("starts")}
        by_start = {r["start"]: r for r in rows}
        by_first = {r["first_bar"]: r for r in rows}
        for gr in (gf.get("start_rows") or []):
            # the two faces label a start differently: the block grid keeps the panel's own
            # bar date, a year anchor keeps "2020-01-01". Matching on the requested label
            # finds nothing and reads as "the faces disagree" -- match on the priced bar.
            mine = by_first.get(gr.get("first_bar")) or by_start.get(gr.get("start"))
            if not mine:
                continue
            ds = None if (gr.get("oos_sharpe") is None or mine.get("oos_sharpe") is None) \
                else round(float(mine["oos_sharpe"]) - float(gr["oos_sharpe"]), 6)
            dc = None if (gr.get("cagr_pct") is None or mine.get("cagr_pct") is None) \
                else round(float(mine["cagr_pct"]) - float(gr["cagr_pct"]), 6)
            same = (mine.get("verdict") == gr.get("verdict")
                    and ds is not None and abs(ds) <= 1e-6
                    and dc is not None and abs(dc) <= 1e-6)
            cross["compared"].append({"start": gr.get("start"), "verdict": mine.get("verdict"),
                                      "delta_oos_sharpe": ds, "delta_cagr_pp": dc,
                                      "reproduces": same})
            if not same:
                cross["disagreements"].append(
                    {"start": gr.get("start"), "why": "priced differently here",
                     "mine": mine.get("verdict"), "theirs": gr.get("verdict"),
                     "delta_oos_sharpe": ds, "delta_cagr_pp": dc})
        if not cross["compared"]:
            cross["disagreements"].append(
                {"why": "no year anchor coincides with a start of the block grid; "
                        "the two faces priced different starts"})
    except Exception as exc:                                     # noqa: BLE001
        cross["disagreements"].append({"why": "start-grid face unreadable: %s" % exc})

    gate_face = None
    try:
        with io.open(GATE, encoding="utf-8") as f:
            gj = json.load(f)
        gate_face = {"asof": gj.get("asof"),
                     "data_last": (gj.get("data") or {}).get("last"),
                     "verdict": (gj.get("decision") or {}).get("verdict")}
    except Exception:                                            # noqa: BLE001
        gate_face = {"verdict": None, "why": "YEAR-GATE.json is not readable"}

    out = {
        "artifact": "etf_book_era_grid",
        "face": "etf_book_era_grid",
        "asof": pd.Timestamp.now(tz="Asia/Shanghai").isoformat(timespec="seconds"),
        "evidence_cutoff": str(pd.Timestamp(close.index[-1]).date()),
        "question": ("the block grid exhausted the day axis and closed with its own limit -- "
                     "25 views of one series; ask the same question on the year axis: is the "
                     "verdict a property of the book or of the era the series started in"),
        "book": BOOK,
        "anchors": {"from": ANCHOR_FROM_YEAR, "to": ANCHOR_TO_YEAR,
                    "count": len(rows),
                    "first": rows[0]["start"] if rows else None,
                    "last": rows[-1]["start"] if rows else None,
                    "why_annual": "one anchor per calendar year: the coarsest move a reader "
                                  "actually contemplates (start the book this year vs next)"},
        "gate_lines_imported": {
            "oos_sharpe_min": G.GATE_OOS_SHARPE_MIN,
            "oos_start": G.GATE_OOS_START,
            "cagr_min_pct": G.GATE_CAGR_MIN_PCT,
            "impact_max_pct_of_adv": G.GATE_IMPACT_MAX * 100.0,
            "capacity_lens": [t for _c, t in G.GATE_CAPITALS_CNY]},
        "data": {"bars": int(len(close.index)),
                 "first": str(pd.Timestamp(close.index[0]).date()),
                 "last": str(pd.Timestamp(close.index[-1]).date()),
                 "flips_repaired": int(n_flip),
                 "bond_free_universe": int(len(close.columns)),
                 "live_picks": picks,
                 "live_picks_asof": str(pd.Timestamp(sc.index[-1]).date()),
                 "adv_weakest_cny": None if adv_weakest is None else round(adv_weakest, 0)},
        "start_rows": rows,
        "adjudication": agg,
        "era_step": era_step,
        "resolution": res,
        "money": {"base_anchor": rows[0]["start"] if rows else None,
                  "years": years, "eras": eras, "sum_pct": total,
                  "identity_delta": round(sum(r["net_pct_sum"] for r in eras) - total, 6)},
        "cross_face_vs_start_grid": cross,
        "gate_face": gate_face,
        "honest": [
            "the gate's out-of-sample window is FIXED at %s: an earlier anchor adds "
            "in-sample warm-up, not OOS evidence -- what moves with the anchor is the path "
            "that reaches the same 2024+ bars" % G.GATE_OOS_START,
            "membership is today's: the bond-free universe and the volatility classes are "
            "derived from the whole panel, so a 2015 anchor is today's names priced "
            "backwards, not the 2015 ETF menu",
            "K1 is a reading of today's tape and is identical at every anchor by construction; "
            "only S1 and A1 can move with the anchor",
            "yearly returns are read off the same level curve and summed, not compounded; the "
            "last year is partial and is not annualised into the era table",
            "the era step is a description of resolution, never an admission rule: the "
            "admission lines remain candidate_year_gate's and the faces keep their verdicts",
            "the verdict words and the aggregate are the phase face's / year gate's own "
            "functions; this face adds no threshold",
        ],
        "elapsed_sec": round(time.time() - t0, 1),
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    tmp = OUT + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    os.replace(tmp, OUT)
    print(json.dumps({"state": agg["state"], "anchors": len(rows),
                      "deny": sum(1 for r in rows if r["verdict"] == "DENY"),
                      "insufficient": sum(1 for r in rows if r["verdict"] == "INSUFFICIENT"),
                      "cross_face_disagreements": len(cross["disagreements"]),
                      "elapsed_sec": out["elapsed_sec"]}, ensure_ascii=False))
    print("saved", OUT)
    return 0


def check() -> int:
    """Re-derive the words, the sums and the era table from the published rows."""
    if not os.path.exists(OUT):
        print("FACE MISSING: %s" % OUT)
        return 3
    with io.open(OUT, encoding="utf-8") as f:
        face = json.load(f)
    problems = []
    rows = face.get("start_rows") or []
    if not rows:
        problems.append("FACE EMPTY: no anchor rows")
    agg = PA.aggregate(rows) if rows else {"state": "CANNOT_VERIFY", "reason": "no rows"}
    pub = face.get("adjudication") or {}
    if pub.get("state") != agg["state"]:
        problems.append("VERDICT DRIFT: published %s, re-derived %s"
                        % (pub.get("state"), agg["state"]))
    for key in ("admit_phases", "deny_phases", "insufficient_phases",
                "oos_sharpe_spread", "cagr_spread_pp"):
        if agg.get(key) != pub.get(key):
            problems.append("NUMBER DRIFT %s: published %r, re-derived %r"
                            % (key, pub.get(key), agg.get(key)))

    # every anchor's verdict must re-derive from its own checks and its own two numbers
    for r in rows:
        blk = G.decision_block(r.get("oos_sharpe"), r.get("cagr_pct"), None, None)
        want = blk["verdict"] if r.get("checks", {}).get("K1_capacity_1pct_adv") is not None \
            else blk["verdict"]
        k1 = (r.get("checks") or {}).get("K1_capacity_1pct_adv")
        s1 = (r.get("checks") or {}).get("S1_oos_sharpe")
        a1 = (r.get("checks") or {}).get("A1_cagr_after_cost")
        if s1 is None or a1 is None:
            expect = "INSUFFICIENT"
        elif not (s1 and a1 and bool(k1)):
            expect = "DENY"
        else:
            expect = "ADMIT"
        if r.get("verdict") != expect:
            problems.append("ANCHOR VERDICT DRIFT %s: published %s, re-derived %s"
                            % (r.get("start"), r.get("verdict"), expect))
        if s1 is not None and r.get("oos_sharpe") is not None:
            if s1 != (float(r["oos_sharpe"]) >= G.GATE_OOS_SHARPE_MIN):
                problems.append("S1 CHECK DRIFT %s" % r.get("start"))
        if a1 is not None and r.get("cagr_pct") is not None:
            if a1 != (float(r["cagr_pct"]) >= G.GATE_CAGR_MIN_PCT):
                problems.append("A1 CHECK DRIFT %s" % r.get("start"))
        del want

    money = face.get("money") or {}
    yrs = money.get("years") or []
    eras_pub = money.get("eras") or []
    if not yrs:
        problems.append("MONEY EMPTY: no calendar year was priced")
    total = round(sum(float(y["net_pct"]) for y in yrs), 4)
    if money.get("sum_pct") is not None and abs(total - float(money["sum_pct"])) > 1e-4:
        problems.append("YEAR SUM DRIFT: published %r, re-derived %r"
                        % (money.get("sum_pct"), total))
    for e in eras_pub:
        lo, hi = [int(x) for x in e["era"].split("-")]
        want = round(sum(float(y["net_pct"]) for y in yrs if lo <= int(y["year"]) <= hi), 4)
        if e.get("net_pct_sum") is not None and abs(want - float(e["net_pct_sum"])) > 1e-4:
            problems.append("ERA SUM DRIFT %s: published %r, re-derived %r"
                            % (e["era"], e["net_pct_sum"], want))
        if e.get("share_of_sum") is not None and total:
            share = round(want / total, 4)
            if abs(share - float(e["share_of_sum"])) > 1e-4:
                problems.append("ERA SHARE DRIFT %s: published %r, re-derived %r"
                                % (e["era"], e["share_of_sum"], share))
        want_members = sum(1 for y in yrs if lo <= int(y["year"]) <= hi)
        if len(e.get("years") or []) != want_members:
            problems.append("ERA MEMBERSHIP DRIFT %s: published %d years, table has %d"
                            % (e["era"], len(e.get("years") or []), want_members))

    # the two steps must come from the two faces they name, and a missing bar step is not 1.0
    bars = bar_steps()
    for key in ("S1_oos_sharpe", "A1_cagr_after_cost"):
        pub_res = ((face.get("resolution") or {}).get(key) or {})
        now = resolution(face.get("era_step") or {}, bars).get(key) or {}
        if pub_res.get("one_bar_step_median") != now.get("one_bar_step_median"):
            problems.append("BAR STEP DRIFT %s: published %r, re-derived %r"
                            % (key, pub_res.get("one_bar_step_median"),
                               now.get("one_bar_step_median")))
        if pub_res.get("years_per_bar_step") != now.get("years_per_bar_step"):
            problems.append("RATIO DRIFT %s: published %r, re-derived %r"
                            % (key, pub_res.get("years_per_bar_step"),
                               now.get("years_per_bar_step")))

    cross = face.get("cross_face_vs_start_grid") or {}
    if (cross.get("disagreements") or []):
        problems.append("CROSS FACE: %d disagreement(s) with the block grid: %s"
                        % (len(cross["disagreements"]),
                           json.dumps(cross["disagreements"][:2], ensure_ascii=False)))
    if not (cross.get("compared") or []):
        problems.append("CROSS FACE: no anchor was compared against the block grid")

    cut = face.get("evidence_cutoff")
    if not cut:
        problems.append("NO CUTOFF: the face does not say which bar it priced")
    try:
        with io.open(GATE, encoding="utf-8") as f:
            gate_last = ((json.load(f) or {}).get("data") or {}).get("last")
        if cut and gate_last and str(cut) < str(gate_last):
            problems.append("STALE FACE_BEHIND_GATE: this face priced %s, the gate's panel "
                            "is %s" % (cut, gate_last))
    except Exception:                                            # noqa: BLE001
        problems.append("UNREADABLE GATE: cannot check freshness against %s" % GATE)

    if problems:
        print(json.dumps({"ok": False, "problems": problems}, ensure_ascii=False, indent=1))
        return 3
    print(json.dumps({"ok": True, "state": agg["state"], "anchors": len(rows),
                      "evidence_cutoff": cut, "eras": len(eras_pub)}, ensure_ascii=False))
    return 0


def selftest() -> int:
    """Fixtures only -- both directions of every sentence this face prints."""
    legs = []

    def leg(name, fn):
        try:
            fn()
            legs.append((name, True, ""))
        except AssertionError as exc:
            legs.append((name, False, str(exc)))

    def anchor(start, verdict, sharpe=1.0, cagr=10.0, k1=True):
        return {"start": start, "verdict": verdict, "oos_sharpe": sharpe, "cagr_pct": cagr,
                "checks": {"S1_oos_sharpe": None if sharpe is None
                           else sharpe >= G.GATE_OOS_SHARPE_MIN,
                           "A1_cagr_after_cost": None if cagr is None
                           else cagr >= G.GATE_CAGR_MIN_PCT,
                           "K1_capacity_1pct_adv": k1},
                "failed_checks": []}

    def L1_anchors_are_annual_and_ordered():
        idx = pd.bdate_range("2014-06-02", "2017-12-29")
        a = year_anchors(idx, 2015, 2017)
        assert [x["year"] for x in a] == [2015, 2016, 2017], a
        assert all(x["first_bar"][5:] == "01-0" or x["first_bar"][5:] <= "01-05" for x in a), a

    def L2_missing_years_are_skipped_not_blank_rows():
        idx = pd.bdate_range("2016-03-01", "2017-12-29")
        a = year_anchors(idx, 2015, 2017)
        assert [x["year"] for x in a] == [2016, 2017], a

    def L3_calendar_returns_reconstruct_the_curve():
        idx = pd.bdate_range("2020-01-01", "2021-12-31")
        vals = [100.0 * (1.0 + 0.001) ** i for i in range(len(idx))]
        rows = calendar_returns(pd.Series(vals, index=idx))
        assert [r["year"] for r in rows] == [2020, 2021], rows
        assert rows[0]["net_pct"] > 0 and rows[-1]["net_pct"] > 0, rows
        # the first year ran the whole way (the panel starts before it); the last year is
        # the one the panel stops inside, so it is the partial one
        assert rows[0]["partial"] is False, rows[0]
        assert rows[-1]["partial"] is True, rows[-1]

    def L4_a_partial_year_is_named_partial():
        idx = pd.bdate_range("2024-01-01", "2024-06-28")
        rows = calendar_returns(pd.Series([100.0 + i for i in range(len(idx))], index=idx))
        assert rows and rows[0]["partial"] is True, rows

    def L5_era_shares_sum_to_one():
        years = [{"year": 2015, "net_pct": 10.0, "bars": 240, "partial": False},
                 {"year": 2019, "net_pct": -5.0, "bars": 240, "partial": False},
                 {"year": 2022, "net_pct": 15.0, "bars": 240, "partial": False},
                 {"year": 2025, "net_pct": 20.0, "bars": 240, "partial": False}]
        idx = pd.bdate_range("2015-01-01", periods=2500)
        ser = pd.Series([100.0 + i * 0.01 for i in range(len(idx))], index=idx)
        eras, total = era_rows(ser, years)
        assert abs(sum(e["share_of_sum"] for e in eras) - 1.0) < 1e-3, eras
        assert abs(sum(e["net_pct_sum"] for e in eras) - total) < 1e-6, (eras, total)
        assert [e["era"] for e in eras] == ["2015-2017", "2018-2020", "2021-2023",
                                           "2024-2026"], eras

    def L6_era_members_are_actually_the_years_in_that_era():
        years = [{"year": y, "net_pct": 1.0, "bars": 240, "partial": False}
                 for y in range(2014, 2027)]
        idx = pd.bdate_range("2014-01-01", "2026-01-30")
        ser = pd.Series([100.0 + i * 0.01 for i in range(len(idx))], index=idx)
        eras, _t = era_rows(ser, years)
        assert eras[0]["years"] == [2015, 2016, 2017], eras[0]
        assert eras[-1]["years"] == [2024, 2025, 2026], eras[-1]
        assert all(2014 not in e["years"] for e in eras), "2014 is outside every era"

    def L7_one_year_step_is_the_median_of_adjacent_gaps():
        rows = [anchor("2018-01-01", "ADMIT", sharpe=v) for v in (1.79, 1.61, 1.23)]
        st = step_readings(rows, "S1_oos_sharpe", "oos_sharpe")
        jumps = sorted([abs(1.61 - 1.79), abs(1.23 - 1.61)])
        assert abs(st["one_year_step_median"] - statistics.median(jumps)) < 1e-9, st
        assert st["spread"] == round(1.79 - 1.23, 4), st

    def L8_a_missing_bar_step_is_not_one():
        era = {"S1_oos_sharpe": {"one_year_step_median": 0.4}}
        res = resolution(era, {})["S1_oos_sharpe"]
        assert res["years_per_bar_step"] is None and res["readable"] is False, res
        assert "not compared" in res["sentence"], res

    def L9_the_ratio_is_years_over_bars():
        era = {"S1_oos_sharpe": {"one_year_step_median": 0.40},
               "A1_cagr_after_cost": {"one_year_step_median": 2.0}}
        bars = {"S1_oos_sharpe": {"one_bar_step_median": 0.05, "source": "x"},
                "A1_cagr_after_cost": {"one_bar_step_median": 0.50, "source": "x"}}
        res = resolution(era, bars)
        assert res["S1_oos_sharpe"]["years_per_bar_step"] == 8.0, res
        assert res["A1_cagr_after_cost"]["years_per_bar_step"] == 4.0, res
        assert "worth 8.00 bar-steps" in res["S1_oos_sharpe"]["sentence"], res

    def L10_unreadable_anchor_cannot_be_read_as_a_pass():
        rows = [anchor("2020-01-01", "INSUFFICIENT", sharpe=None, cagr=None),
                anchor("2021-01-01", "ADMIT")]
        agg = PA.aggregate(rows)
        assert agg["state"] == "INSUFFICIENT_AT_SOME_PHASE", agg

    def L11_two_anchors_that_disagree_are_not_summed_into_one_word():
        rows = [anchor("2020-01-01", "ADMIT"), anchor("2021-01-01", "DENY", sharpe=0.4)]
        agg = PA.aggregate(rows)
        assert agg["state"] == "REFUSED_AT_SOME_PHASE" and agg["deny_phases"] == 1, agg

    def L12_empty_is_cannot_verify():
        assert PA.aggregate([])["state"] == "CANNOT_VERIFY"

    def L13_verdict_words_come_from_the_year_gate():
        blk = G.decision_block(0.90, 8.0, 25_000_000.0, 5)
        assert blk["verdict"] == "ADMIT", blk
        blk2 = G.decision_block(0.69, 8.0, 25_000_000.0, 5)
        assert blk2["verdict"] == "DENY" and blk2["failed_checks"] == ["S1_oos_sharpe"], blk2

    def L14_a_year_that_ends_on_dec_30_is_not_partial():
        # the defect this leg exists for: the first version asked for a 12-31 bar and
        # labelled ten complete years partial (the calendar prints 30 Dec most years).
        idx = pd.bdate_range("2016-01-01", "2017-12-29")
        vals = [100.0 + i * 0.01 for i in range(len(idx))]
        rows = calendar_returns(pd.Series(vals, index=idx))
        by = {r["year"]: r for r in rows}
        assert by[2016]["partial"] is False, by[2016]
        assert by[2017]["partial"] is True, by[2017]   # the panel stops inside this year

    for name, fn in [
        ("L1 年代锚=每年首根且有序", L1_anchors_are_annual_and_ordered),
        ("L2 面板缺年=跳过不造空行", L2_missing_years_are_skipped_not_blank_rows),
        ("L3 逐年收益从净值曲线读出", L3_calendar_returns_reconstruct_the_curve),
        ("L4 部分年标 partial 不进年化", L4_a_partial_year_is_named_partial),
        ("L5 各年代份额相加=1（同一年尺）", L5_era_shares_sum_to_one),
        ("L6 年代成员确实是该年代的年份", L6_era_members_are_actually_the_years_in_that_era),
        ("L7 一年步长=相邻锚差的中位", L7_one_year_step_is_the_median_of_adjacent_gaps),
        ("L8 缺一跳步长=不比较（不印 1.0）", L8_a_missing_bar_step_is_not_one),
        ("L9 倍数=一年步长/一跳步长", L9_the_ratio_is_years_over_bars),
        ("L10 读不出不得读成通过（r98）", L10_unreadable_anchor_cannot_be_read_as_a_pass),
        ("L11 锚之间不一致不得被抹成一个词", L11_two_anchors_that_disagree_are_not_summed_into_one_word),
        ("L12 空面=CANNOT_VERIFY", L12_empty_is_cannot_verify),
        ("L13 判词与闸线来自年门", L13_verdict_words_come_from_the_year_gate),
        ("L14 12-30 收年的完整年不得被标 partial", L14_a_year_that_ends_on_dec_30_is_not_partial),
    ]:
        leg(name, fn)

    passed = sum(1 for _n, ok, _m in legs if ok)
    for n, ok, msg in legs:
        print("%s %s%s" % ("PASS" if ok else "FAIL", n, "" if ok else "  <- " + msg))
    print("selftest %d/%d" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "check", "selftest"])
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest or args.cmd == "selftest":
        return selftest()
    if args.check or args.cmd == "check":
        return check()
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
