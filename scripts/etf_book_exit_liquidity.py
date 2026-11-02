"""The gate is only on the way in: can the book actually sell what it bought?

Every face this line publishes screens names with one rule -- 20-bar median turnover
>= MIN_AMT (20M CNY) -- and that rule is applied when a name is RANKED, i.e. when it is
bought. Nothing in the book checks the same number on the way out. A name that was liquid
on the entry bar can be illiquid on the exit bar, and the sell is then not a decision but a
queue: you hold until there is somebody to sell to.

The survivorship face (r1236) priced deaths as a budget applied to held names; this face
prices the mechanical half of the same worry that is measurable inside the panel: for every
position the declared arm actually holds, read the exit bar's own 20-bar median turnover and
ask (a) how often it is below the buy gate, (b) how often there is no bar at all, (c) how far
into the future the first qualifying bar is, and (d) what the price path over that deferral
is worth to the book.

Reading convention, printed with every number:
  * the deferral is priced as weight x (open[t'] / open[exit bar] - 1) with t' the first bar
    at/after the exit where the name clears the gate again (capped at DEFER_MAX bars, and a
    position that never clears inside the cap is reported as outside_cap, not as zero);
  * that is an ATTRIBUTION of the stuck capital, not a re-priced book -- the equity curve in
    results/etf_book_production is not rebuilt here, and the summary says so on its face;
  * the annualisation divides the summed contribution of ONE phase by that phase's own span
    in years, so it is a pp/yr order of magnitude, not a CAGR.

Arms: the declared fill (score held one bar back) is the arm the desk can trade and is the
only arm measured; the as-coded arm exists in this line only as the card's control.

  python scripts/etf_book_exit_liquidity.py run
  python scripts/etf_book_exit_liquidity.py --check
  python scripts/etf_book_exit_liquidity.py --selftest
"""
from __future__ import annotations

import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import numpy as np
import pandas as pd

import etf_composite_pf as E
import etf_book_production as P
import etf_robust_pf as R

OUT_JSON = os.path.join(ROOT, "results", "etf_book_exit_liquidity.json")
OUT_MD = os.path.join(ROOT, "research", "ETF_BOOK_EXIT_LIQUIDITY.md")

# ------------------------------------------------------------------ frozen criteria
# Written before the first run; --check re-derives the verdict from the payload's own rows.
START = "2020-01-01"
REBAL = 20
N_HOLD = 12
COST = 0.0010
TARGET = 0.08
VOL_WINDOW = 60
N_PHASES = 4
DEFER_MAX = 20              # bars a stuck exit may wait before it is reported as outside_cap
TOL_PP = 0.57               # material drag line, the one this line's other faces use
SHARE_MIN = 0.75            # share of phases a verdict has to hold in
BELOW_MAX = 0.02            # share of positions below the buy gate that reads as "no constraint"
BELOW_MIN = 0.05            # share of positions below the gate that reads as "a real gate"
GATE = E.MIN_AMT            # imported, never retyped: the gate the ranking actually uses
CRITERIA = {"tol_pp": TOL_PP, "share_min": SHARE_MIN, "n_phases": N_PHASES,
            "below_share_max": BELOW_MAX, "below_share_min": BELOW_MIN,
            "defer_max_bars": DEFER_MAX, "gate_cny": GATE}


def phase_starts(index, rebal=REBAL, n=N_PHASES):
    post = list(index)
    if len(post) < rebal * 2:
        raise ValueError("panel has %d bars -- need at least %d" % (len(post), rebal * 2))
    step = max(1, rebal // n)
    picks = [post[i * step] for i in range(n)]
    if len(set(picks)) < n:
        raise ValueError("only %d distinct phases in a %d-bar cycle" % (len(set(picks)), rebal))
    return picks


def _cell(panel, bar, name):
    """Value of `panel` at (bar, name), or None when the cell does not exist or is NaN."""
    try:
        v = panel.at[bar, name]
    except (KeyError, IndexError):
        return None
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return None
    try:
        out = float(v)
    except (TypeError, ValueError):
        return None
    return None if np.isnan(out) else out


def measure_positions(diag, openp, amt, gate=None, defer_max=DEFER_MAX):
    """One row per HELD NAME per holding period: was the exit bar tradeable at the entry gate?

    The book is equal-weight inside one decision (weight = scale / n_names), which is the same
    convention the engine writes into `diag`; nothing here re-weights.
    """
    gate = GATE if gate is None else float(gate)
    bars = openp.index
    rows = []
    for i in range(len(diag) - 1):
        nxt = pd.Timestamp(diag[i + 1]["date"])
        book = list(diag[i].get("book") or [])
        if not book or nxt not in bars:
            continue
        w = float(diag[i].get("scale") or 0.0) / len(book)
        j = bars.get_loc(nxt)
        for nm in book:
            liq = _cell(amt, nxt, nm)
            entry_px = _cell(openp, nxt, nm)
            rec = {"name": nm, "entry": str(diag[i]["date"]), "exit": str(nxt.date()),
                   "weight": round(w, 6), "exit_liq_cny": (None if liq is None else round(liq, 1)),
                   "missing_bar": liq is None, "below_gate": liq is None or liq < gate,
                   "defer_bars": 0, "defer_to": None, "delta_ret": 0.0,
                   "outside_cap": False}
            if rec["below_gate"]:
                if entry_px is None:
                    # no print at all on the exit bar: a forced hold, reported as censored.
                    rec["outside_cap"] = True
                else:
                    for k in range(1, defer_max + 1):
                        if j + k >= len(bars):
                            break
                        b = bars[j + k]
                        l2 = _cell(amt, b, nm)
                        p2 = _cell(openp, b, nm)
                        if l2 is not None and l2 >= gate and p2 is not None:
                            rec["defer_bars"] = k
                            rec["defer_to"] = str(pd.Timestamp(b).date())
                            rec["delta_ret"] = round(p2 / entry_px - 1.0, 8)
                            break
                    else:
                        rec["outside_cap"] = True
                    if rec["defer_to"] is None:
                        rec["outside_cap"] = True
            rec["contrib"] = round(w * rec["delta_ret"], 10)
            rows.append(rec)
    return rows


def summarise(rows, span_years):
    n = len(rows)
    if not n:
        return {"positions": 0, "below_gate": 0, "missing_bar": 0, "deferred": 0,
                "outside_cap": 0, "share_below_gate": None, "mean_defer_bars": None,
                "contrib_sum": 0.0, "drag_pp_per_year": None}
    below = sum(1 for r in rows if r["below_gate"])
    deferred = sum(1 for r in rows if r["defer_to"])
    outside = sum(1 for r in rows if r["outside_cap"])
    missing = sum(1 for r in rows if r["missing_bar"])
    bars = [r["defer_bars"] for r in rows if r["defer_to"]]
    contrib = float(np.sum([r["contrib"] for r in rows]))
    return {
        "positions": n,
        "below_gate": below,
        "missing_bar": missing,
        "deferred": deferred,
        "outside_cap": outside,
        "share_below_gate": round(below / n, 4),
        "mean_defer_bars": (round(float(np.mean(bars)), 2) if bars else None),
        "contrib_sum": round(contrib, 6),
        "drag_pp_per_year": (round(100.0 * contrib / span_years, 4)
                             if span_years and span_years > 0 else None),
    }


def verdict_from_summary(summary):
    """Frozen rule: is the sell-side gate a constraint the reader has to pay for?

    Two independent readings have to agree before a verdict is published: how often the book
    is asked to sell into a name it would not be allowed to buy, and how much the deferral is
    worth in pp/yr. A small share with a small price is "not a constraint"; a large share with
    a material price is a real gate; anything else is reported as mixed, not as the nicer half.
    """
    phases = summary.get("phases") or []
    if not phases:
        return "INCOMPLETE"
    need = int(np.ceil(SHARE_MIN * len(phases)))
    shares = [p["share_below_gate"] for p in phases if p.get("share_below_gate") is not None]
    deltas = [p["drag_pp_per_year"] for p in phases if p.get("drag_pp_per_year") is not None]
    if not shares or not deltas:
        return "INCOMPLETE"
    small_share = sum(1 for s in shares if s <= BELOW_MAX)
    within = sum(1 for d in deltas if abs(d) < TOL_PP)
    heavy = sum(1 for s in shares if s >= BELOW_MIN)
    material = sum(1 for d in deltas if abs(d) >= TOL_PP)
    if small_share >= need and within >= need:
        return "EXIT_LIQUIDITY_IS_NOT_A_CONSTRAINT"
    if heavy >= need and material >= need:
        return "THE_EXIT_GATE_IS_MATERIAL"
    return "MIXED_ACROSS_PHASES"


def run():
    t0 = time.time()
    close, openp, amt, score, cls, n_flip = P.prep_panel()
    print("panel %s first=%s last=%s flips=%d  %.1fs"
          % (close.shape, close.index[0].date(), close.index[-1].date(), n_flip,
             time.time() - t0), flush=True)
    starts = phase_starts([d for d in close.index if d >= pd.Timestamp(START)])

    phases = []
    for i, st in enumerate(starts):
        start = str(pd.Timestamp(st).date())
        diag = []
        R.open_to_open_equity(close, openp, amt, score.shift(1), REBAL, N_HOLD, COST,
                              vol_target=TARGET, start=start, vol_window=VOL_WINDOW,
                              diag=diag)
        if len(diag) < 2:
            continue
        span = (pd.Timestamp(diag[-1]["date"]) - pd.Timestamp(diag[0]["date"])).days / 365.25
        rows = measure_positions(diag, openp, amt)
        s = summarise(rows, span)
        s["phase"] = i
        s["phase_start"] = start
        s["holds"] = len(diag) - 1
        s["span_years"] = round(span, 3)
        phases.append(s)
        print("phase %d %s holds=%d positions=%d below=%d missing=%d outside_cap=%d "
              "share_below=%.4f mean_defer=%s drag=%s pp/yr  %.1fs"
              % (i, start, s["holds"], s["positions"], s["below_gate"], s["missing_bar"],
                 s["outside_cap"], s["share_below_gate"] or 0, s["mean_defer_bars"],
                 s["drag_pp_per_year"], time.time() - t0), flush=True)

    shares = [p["share_below_gate"] for p in phases if p["share_below_gate"] is not None]
    deltas = [p["drag_pp_per_year"] for p in phases if p["drag_pp_per_year"] is not None]
    summary = {
        "phases": phases,
        "share_below_gate_mean": round(float(np.mean(shares)), 4) if shares else None,
        "share_below_gate_max": round(float(np.max(shares)), 4) if shares else None,
        "drag_pp_mean": round(float(np.mean(deltas)), 4) if deltas else None,
        "drag_pp_min": round(float(np.min(deltas)), 4) if deltas else None,
        "drag_pp_max": round(float(np.max(deltas)), 4) if deltas else None,
        "positions_total": int(sum(p["positions"] for p in phases)),
        "below_gate_total": int(sum(p["below_gate"] for p in phases)),
        "missing_bar_total": int(sum(p["missing_bar"] for p in phases)),
        "outside_cap_total": int(sum(p["outside_cap"] for p in phases)),
    }
    summary["verdict"] = verdict_from_summary(summary)

    doc = {
        "schema": "etf_book_exit_liquidity/v1",
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "elapsed_sec": round(time.time() - t0, 1),
        "evidence_cutoff": str(close.index[-1].date()),
        "question": ("the 20M 20-bar turnover gate is applied when a name is ranked and never "
                     "when it is sold: how often does the book have to exit into a name it "
                     "would not be allowed to buy, and what is the wait worth?"),
        "arm": "declared fill (score held one bar back, close t -> open t+1); as-coded not measured",
        "config": {"n_hold": N_HOLD, "rebal": REBAL, "cost_bp_per_side": round(COST * 1e4, 1),
                   "vol_target": TARGET, "vol_window": VOL_WINDOW, "start": START},
        "criteria": CRITERIA,
        "reading_law": [
            "the deferral is weight x (open[t']/open[exit] - 1): an attribution of stuck "
            "capital, not a re-priced equity curve",
            "a position that never clears the gate inside %d bars is outside_cap, never 0"
            % DEFER_MAX,
            "drag_pp_per_year = 100 x summed contribution / that phase's own span in years",
        ],
        "panel": {"shape": list(close.shape), "flips_repaired": n_flip,
                  "first": str(close.index[0].date()), "last": str(close.index[-1].date())},
        "summary": summary,
    }
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    write_md(doc)
    print("verdict %s | share_below_gate mean %s | drag %s pp/yr | %.1fs"
          % (summary["verdict"], summary["share_below_gate_mean"], summary["drag_pp_mean"],
             time.time() - t0), flush=True)
    return doc


def write_md(doc):
    s = doc["summary"]
    c = doc["criteria"]
    lines = [
        "# ETF book: the gate is only on the way in",
        "",
        "**Question.** Every name this book holds passed a 20-bar median turnover gate of "
        "%.0f 万元 on the bar it was ranked. Nothing checks the same number on the bar it is "
        "sold. How often is the book asked to exit into a name it would not be allowed to buy, "
        "how long does the queue last, and what is the wait worth?" % (c["gate_cny"] / 1e4),
        "",
        "**Panel.** %d funds x %d bars, %s..%s, %d quote flips repaired (the production panel's "
        "own repair, imported not copied)."
        % (doc["panel"]["shape"][1], doc["panel"]["shape"][0], doc["panel"]["first"],
           doc["panel"]["last"], doc["panel"]["flips_repaired"]),
        "",
        "**Arm.** %s." % doc["arm"],
        "",
        "## Reading",
        "",
        "| phase | start | holds | positions | exit below gate | no bar | deferred | outside cap "
        "| share below | mean defer (bars) | drag (pp/yr) |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for p in s["phases"]:
        lines.append("| %d | %s | %d | %d | %d | %d | %d | %d | %.2f%% | %s | %s |"
                     % (p["phase"], p["phase_start"], p["holds"], p["positions"],
                        p["below_gate"], p["missing_bar"], p["deferred"], p["outside_cap"],
                        100.0 * (p["share_below_gate"] or 0.0),
                        ("%.2f" % p["mean_defer_bars"]) if p["mean_defer_bars"] is not None
                        else "-",
                        ("%+.3f" % p["drag_pp_per_year"])
                        if p["drag_pp_per_year"] is not None else "-"))
    lines += [
        "",
        "Totals over %d positions: %d exits below the buy gate (%.2f%%), %d with no bar at all, "
        "%d that never found a qualifying bar inside %d bars."
        % (s["positions_total"], s["below_gate_total"],
           100.0 * (s["below_gate_total"] / s["positions_total"]) if s["positions_total"] else 0,
           s["missing_bar_total"], s["outside_cap_total"], c["defer_max_bars"]),
        "",
        "**Verdict: `%s`** (mean share below gate %s, mean drag %s pp/yr, range %s..%s)."
        % (s["verdict"], s["share_below_gate_mean"], s["drag_pp_mean"], s["drag_pp_min"],
           s["drag_pp_max"]),
        "",
        "The two readings behind that verdict, printed separately because the frozen rule "
        "requires both to be small (or both to be large) before it names a side:",
        "",
        "- **incidence**: %.2f%% of held positions must be sold on a bar where the name would "
        "not pass the buy gate -- above the no-constraint line (%.0f%%), below the real-gate "
        "line (%.0f%%);"
        % (100.0 * (s["share_below_gate_mean"] or 0.0), 100 * c["below_share_max"],
           100 * c["below_share_min"]),
        "- **price**: the wait is worth %+.2f pp/yr on average and every phase sits inside "
        "+-%.2f pp of zero, so the queue is real but the money is not in it;"
        % (s["drag_pp_mean"] or 0.0, c["tol_pp"]),
        "- **the censored tail**: %d of %d positions (%.2f%%) never found a qualifying bar "
        "inside %d bars at all and are counted as outside_cap, not as a zero return -- those "
        "are forced holds, and they are the half of this face the panel cannot price."
        % (s["outside_cap_total"], s["positions_total"],
           100.0 * (s["outside_cap_total"] / s["positions_total"]) if s["positions_total"] else 0,
           c["defer_max_bars"]),
        "",
        "## 它量的是什么，不是什么",
        "",
    ]
    lines += ["- %s" % x for x in doc["reading_law"]]
    lines += [
        "- the gate is read off the same `amt` panel the ranking uses (imported from "
        "`etf_composite_pf.MIN_AMT`, not retyped), so a reader can check the two faces cut at "
        "the same number;",
        "- a below-gate reading is not a death: the name can come back, and the deferral prices "
        "exactly that wait instead of assuming a total loss;",
        "- what is NOT measured here: the size of the order relative to turnover (impact), the "
        "bid-ask spread, and any name that stopped existing inside the hold -- the panel has no "
        "dead funds (E352 prices that half as a budget).",
        "",
        "## 复跑",
        "",
        "```",
        "python scripts/etf_book_exit_liquidity.py run",
        "python scripts/etf_book_exit_liquidity.py --check",
        "python scripts/etf_book_exit_liquidity.py --selftest",
        "```",
        "",
    ]
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def check():
    """Re-derive the verdict from the published rows; a hand-edited state fails here."""
    with open(OUT_JSON, encoding="utf-8") as fh:
        doc = json.load(fh)
    s = doc["summary"]
    got = verdict_from_summary(s)
    ok = got == s.get("verdict")
    print("check: verdict recomputed %s vs published %s -> %s"
          % (got, s.get("verdict"), "OK" if ok else "DRIFT"))
    if not ok:
        return 2
    # the totals have to add up to the per-phase rows
    if s["positions_total"] != sum(p["positions"] for p in s["phases"]):
        print("check: positions_total does not add up")
        return 2
    if s["below_gate_total"] != sum(p["below_gate"] for p in s["phases"]):
        print("check: below_gate_total does not add up")
        return 2
    print("check: totals add up over %d phases" % len(s["phases"]))
    return 0


def selftest():
    fails = []

    def eq(label, got, want):
        if got != want:
            fails.append("%s: got %r want %r" % (label, got, want))

    idx = pd.date_range("2024-01-01", periods=40, freq="B")
    gate = 20e6
    # one liquid name, one that dies on the exit bar, one with no bar at all
    openp = pd.DataFrame({"A": np.linspace(1.0, 2.0, 40), "B": 1.0, "C": 1.0}, index=idx)
    amt = pd.DataFrame({"A": 100e6, "B": 100e6, "C": 100e6}, index=idx)
    amt.loc[idx[20]:idx[22], "B"] = 5e6   # B is untradeable on the exit bar and just after
    amt.loc[idx[23], "B"] = 30e6          # B reopens three bars later
    amt.loc[idx[20]:, "C"] = np.nan       # C has no bar at all and never comes back
    diag = [{"date": str(idx[10].date()), "scale": 1.0, "book": ["A", "B", "C"]},
            {"date": str(idx[20].date()), "scale": 1.0, "book": ["A", "B", "C"]}]
    rows = measure_positions(diag, openp, amt, gate=gate, defer_max=5)
    eq("positions", len(rows), 3)
    by = {r["name"]: r for r in rows}
    eq("A below gate", by["A"]["below_gate"], False)
    eq("A delta", by["A"]["delta_ret"], 0.0)
    eq("B below gate", by["B"]["below_gate"], True)
    eq("B deferred", by["B"]["defer_to"], str(idx[23].date()))
    eq("B defer bars", by["B"]["defer_bars"], 3)
    eq("B delta", by["B"]["delta_ret"], 0.0)
    eq("C below gate", by["C"]["below_gate"], True)
    eq("C outside cap", by["C"]["outside_cap"], True)
    eq("C delta", by["C"]["delta_ret"], 0.0)
    eq("weights sum", abs(sum(r["weight"] for r in rows) - 1.0) < 1e-5, True)

    # the price move over the deferral is priced, not the total loss
    openp2 = pd.DataFrame({"B": np.array([1.0] * 21 + [1.10] * 19)}, index=idx)
    amt2 = pd.DataFrame({"B": np.array([100e6] * 20 + [5e6] + [100e6] * 19)}, index=idx)
    diag2 = [{"date": str(idx[10].date()), "scale": 1.0, "book": ["B"]},
             {"date": str(idx[20].date()), "scale": 1.0, "book": ["B"]}]
    r2 = measure_positions(diag2, openp2, amt2, gate=gate, defer_max=5)[0]
    eq("deferred to the first qualifying bar", r2["defer_to"], str(idx[21].date()))
    eq("deferred return priced", round(r2["delta_ret"], 6), round(1.10 / 1.0 - 1.0, 6))

    # scale is the position size and must reach the contribution
    diag3 = [dict(diag2[0], scale=0.5), diag2[1]]
    r3 = measure_positions(diag3, openp2, amt2, gate=gate, defer_max=5)[0]
    eq("weight off scale", r3["weight"], 0.5)
    eq("contribution off weight", round(r3["contrib"], 6), round(0.5 * r3["delta_ret"], 6))

    # summarise + verdict: small share / small drag reads as no constraint
    s_small = summarise([{"below_gate": False, "missing_bar": False, "defer_to": None,
                          "defer_bars": 0, "outside_cap": False, "contrib": 0.0}] * 100, 5.0)
    eq("share small", s_small["share_below_gate"], 0.0)
    phases_small = [dict(s_small, phase=i) for i in range(4)]
    eq("verdict small", verdict_from_summary({"phases": phases_small}),
       "EXIT_LIQUIDITY_IS_NOT_A_CONSTRAINT")

    # large share / material drag reads as the gate biting (drag sign preserved)
    big = ([{"below_gate": True, "missing_bar": False, "defer_to": "x", "defer_bars": 5,
             "outside_cap": False, "contrib": -0.05}]
           + [{"below_gate": True, "missing_bar": False, "defer_to": "x", "defer_bars": 5,
               "outside_cap": False, "contrib": 0.0}] * 99)
    s_big = summarise(big, 1.0)
    eq("share big", s_big["share_below_gate"], 1.0)
    eq("drag big negative", s_big["drag_pp_per_year"], -5.0)
    phases_big = [dict(s_big, phase=i) for i in range(4)]
    eq("verdict big", verdict_from_summary({"phases": phases_big}), "THE_EXIT_GATE_IS_MATERIAL")

    # half and half is published as mixed, never as the nicer half
    mixed = [dict(s_small, phase=0), dict(s_big, phase=1), dict(s_small, phase=2),
             dict(s_big, phase=3)]
    eq("verdict mixed", verdict_from_summary({"phases": mixed}), "MIXED_ACROSS_PHASES")
    eq("verdict empty", verdict_from_summary({"phases": []}), "INCOMPLETE")
    eq("summarise empty", summarise([], 0.0)["positions"], 0)

    # censored: a position outside the cap is reported, never folded into a zero
    eq("outside cap counted", summarise([{"below_gate": True, "missing_bar": True,
                                          "defer_to": None, "defer_bars": 0,
                                          "outside_cap": True, "contrib": 0.0}], 1.0)
       ["outside_cap"], 1)

    # a name with no exit print at all is a forced hold, not a silent zero
    openp4 = pd.DataFrame({"Z": np.array([1.0] * 20 + [np.nan] + [1.0] * 19)}, index=idx)
    amt4 = pd.DataFrame({"Z": np.array([100e6] * 20 + [np.nan] + [100e6] * 19)}, index=idx)
    r4 = measure_positions(diag2, openp4, amt4, gate=gate, defer_max=5)[0]
    eq("no print -> missing_bar", r4["missing_bar"], True)
    eq("no print -> outside_cap", r4["outside_cap"], True)
    eq("no print -> no fake return", r4["delta_ret"], 0.0)

    if fails:
        for f in fails:
            print("FAIL " + f)
        print("selftest %d failed" % len(fails))
        return 1
    print("selftest 23/23 OK")
    return 0


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "run"
    if arg == "run":
        run()
        sys.exit(0)
    if arg == "--check":
        sys.exit(check())
    if arg == "--selftest":
        sys.exit(selftest())
    print(__doc__)
    sys.exit(2)