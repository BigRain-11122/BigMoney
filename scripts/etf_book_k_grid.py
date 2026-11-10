"""Does the book re-lever on days it does not re-decide?

r1536 made the *decision clock* single-source and, in passing, printed a column nobody
had read before: of the k changes in the order ledger, six fall on bars that are not
decision bars. This face asks where those six come from, and what they are worth.

Two grids live inside one book and they are not the same grid:

    the book re-decides      every 20th bar of its own 2020 window -- panel row 0, 20,
                             40 ... The official calendar's phase of 2020-01-02 is 0, so
                             the book's decision bars sit on official phase 0.
    the overlay re-levers    `etf_book_order.k_schedule` walks `rp.index[min_hist::20]`,
                             i.e. it starts counting 126 panel rows in -- phase 6. It is
                             not a different *interval*, it is a different *set of days*:
                             k is refreshed six sessions after every decision and never
                             on one.

An overlay that re-levers off-grid is not obviously wrong; k is a risk rule and the
panel's own risk moves every bar. The question is what the extra refreshes buy and what
they cost, so this face prices it the only way that answers anything:

    production   the ticket's own path, verbatim: 5 names, beta target 0.20, 8 bp a
                 side, repo carry -- `etf_book_order.k_schedule` exactly as shipped
    grid_only    the same book, fills, costs and carry; the same beta estimate; k is
                 refreshed only on bars that are the book's decision bars and held
                 between them

and then it refuses to quote one cell: the phase of the overlay grid is a free choice,
so all twenty are priced. If the spread across phases is wider than the difference
between production and the decision-grid arm, the face says the phase is doing the
talking and no rule is being described (r1213's lesson, r1325's path test).

The identity arm is the published one: `etf_book_band_ruler` prints the ticket's own
held config at 12.56%/yr on its 2024+ window. This face rebuilds that path through the
band ruler's own helpers and must land on it, or nothing here is quoted.

Usage:
    python scripts/etf_book_k_grid.py run
    python scripts/etf_book_k_grid.py --check
    python scripts/etf_book_k_grid.py --selftest
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
import etf_book_order as O
import etf_book_band_ruler as BR
import etf_book_next_decision as ND
import etf_phase_beta_target as BT
import etf_phase_beta_window as BW

OUT_JSON = os.path.join(E.PATHS.results_dir, "etf_book_k_grid.json")
OUT_MD = os.path.join(ROOT, "research", "ETF_BOOK_K_GRID.md")
LEDGER = os.path.join(E.PATHS.results_dir, "etf_book_order", "ledger.jsonl")
PRODUCTION = os.path.join(E.PATHS.results_dir, "etf_book_production", "latest.json")
BAND_RULER = os.path.join(E.PATHS.results_dir, "etf_book_band_ruler.json")
BAND_KEY = "held/causal/ticket"

REBAL = int(O.REBAL)
MIN_HIST = int(O.MIN_HIST)
# ---------------------------------------------------------------- frozen criteria
# A quarter of a point of annual return is the smallest difference this company names as
# a difference (the same line etf_book_band_ruler draws). Below it, one rule.
TOL_PP = 0.25
# The identity arm must reproduce the band ruler's published ticket cell to an eighth of a
# point; that cell is printed to two decimals and this arm is not.
IDENT_TOL_PP = 0.125
CRITERIA = {
    "tol_pp_per_year": TOL_PP,
    "identity_tol_pp": IDENT_TOL_PP,
    "identity_anchor": "%s ticket_window cagr (results/etf_book_band_ruler.json)" % BAND_KEY,
    "held_config": {"n_hold": BR.N_HOLD, "beta_target": BR.BETA_TARGET, "rebal": REBAL,
                    "cost_bp_per_side": round(BR.COST_BP * 1e4, 1),
                    "universe": "ticket classes " + str(list(BR.V.KEEP)),
                    "ordering": "decide at bar d's close, fill at bar d+1's open",
                    "cash_leg": "repo ladder, same series as the card"},
    "phases_priced": "all 20 phases of the official calendar, 0..19",
    "verdict_rule": (
        "GRID_COSTS iff the decision-grid arm's cagr is below production by tol; "
        "GRID_SAVES iff above it by tol; otherwise GRID_NEUTRAL. PHASE_DOMINATES is "
        "reported whenever the spread across the twenty phases is wider than "
        "|grid - production| -- then the phase, not the rule, is what a single cell "
        "would be quoting."),
    "frozen": ("thresholds, the phase sweep and the rule were written before the first "
               "run; --check refuses a face whose published verdict or ledger line does "
               "not re-derive"),
}


# ---------------------------------------------------------------- grid arithmetic
def official_grid(days, bars, rebal=REBAL, phase=0):
    """The bars that land on `phase` of the official calendar. Off-calendar bars never do.

    A grid read off a panel with holes is not the exchange's grid (r1286).
    """
    if phase is None:
        return set()
    out = set()
    for b in bars:
        i = ND.index_of(days, b)
        if i is not None and i % int(rebal) == int(phase) % int(rebal):
            out.add(b)
    return out


def phase_of_bar(days, bar, rebal=REBAL):
    return ND.phase_of(days, bar, rebal)


def k_schedule_grid(rp, rm, target, grid, min_hist=MIN_HIST):
    """`etf_book_order.k_schedule` restricted to the book's own decision bars.

    Same expanding beta, same clip, same de-risking-only rule -- only the set of bars on
    which the answer is allowed to change differs.
    """
    var = rm.expanding(min_periods=2).var()
    cov = rp.expanding(min_periods=2).cov(rm)
    beta = cov / var
    out = []
    for i in range(int(min_hist), len(rp)):
        if rp.index[i].strftime("%Y-%m-%d") not in grid:
            continue
        b = beta.iloc[i]
        if b is None or not np.isfinite(b) or b <= 1e-6:
            continue
        out.append((rp.index[i], float(min(1.0, max(0.0, target / b))), float(b)))
    return out


def sched_phase(days, sched, rebal=REBAL):
    """The official phase the overlay's own bars sit on, and how many miss it."""
    if not sched:
        return {"phase": None, "n_bars": 0}
    phases = {}
    for d, _k, _b in sched:
        p = phase_of_bar(days, d.strftime("%Y-%m-%d"))
        if p is not None:
            phases[p] = phases.get(p, 0) + 1
    if not phases:
        return {"phase": None, "n_bars": 0}
    top = max(phases.items(), key=lambda kv: kv[1])
    return {"phase": int(top[0]), "n_bars": len(sched), "phase_counts": phases}


def move_stats(series):
    moves = []
    for i in range(1, len(series)):
        if abs(float(series[i]) - float(series[i - 1])) > 1e-12:
            moves.append(i)
    return moves


def ledger_k_trace(path=LEDGER, days=None, rebal=REBAL, phase=0):
    """The ledger's own k changes against the book's decision phase."""
    rows = []
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    rows.append(json.loads(line))
                except ValueError:
                    continue
    if not rows:
        return {"unreadable": "no ledger rows"}
    days = ND.load_calendar() if days is None else days
    dates = [str(r.get("date") or "")[:10] for r in rows]
    ks = [r.get("k") for r in rows]
    moves = []
    for i in range(1, len(rows)):
        try:
            if abs(float(ks[i]) - float(ks[i - 1])) > 1e-12:
                moves.append(dates[i])
        except (TypeError, ValueError):
            continue
    off, unk, phases = [], [], {}
    for d in moves:
        i = ND.index_of(days, d)
        if i is None:
            unk.append(d)
            continue
        phases[i % int(rebal)] = phases.get(i % int(rebal), 0) + 1
        if i % int(rebal) != int(phase):
            off.append(d)
    return {"rows": len(rows), "first": dates[0], "last": dates[-1],
            "n_moves": len(moves), "n_off_grid": len(off),
            "off_grid_recent": off[-6:], "off_calendar": len(unk),
            "move_phases": {str(k): v for k, v in sorted(phases.items())},
            "decision_phase": int(phase),
            "grid_read_as": "official calendar index mod REBAL == decision phase"}


# ---------------------------------------------------------------- verdict (from rows)
def decide(rows, tol_pp=TOL_PP):
    by = {r["arm"]: r for r in rows}
    if "production" not in by or "grid_only" not in by:
        return {"state": "INCOMPLETE", "why": "missing a required arm"}
    pc, gc = by["production"].get("cagr"), by["grid_only"].get("cagr")
    if pc is None or gc is None:
        return {"state": "INCOMPLETE", "why": "an arm has no cagr"}
    delta = 100.0 * (gc - pc)
    if delta < -tol_pp:
        state = "GRID_COSTS"
    elif delta > tol_pp:
        state = "GRID_SAVES"
    else:
        state = "GRID_NEUTRAL"
    vals = [r.get("cagr") for r in rows if r["arm"].startswith("phase_")]
    vals = [v for v in vals if v is not None]
    spread = None if len(vals) < 2 else 100.0 * (max(vals) - min(vals))
    return {
        "state": state,
        "delta_pp": round(delta, 3),
        "tol_pp": tol_pp,
        "phase_spread_pp": None if spread is None else round(spread, 3),
        "phase_dominates": bool(spread is not None and abs(delta) < spread),
        "rule": CRITERIA["verdict_rule"],
    }


# ---------------------------------------------------------------- arms
def overlay_strat(rp, rm, sched, cash_rf):
    """One overlay path, sliced to the bars on which the schedule is in force.

    The toll is in basis points, exactly as `etf_book_band_ruler._overlay_path` passes it:
    a fraction here would be charged ten thousand times over and every cell would read as
    a crash rather than a comparison (measured once, kept as a selftest note).
    """
    strat, _bench, _kk = BT.apply_overlay(rp, rm, sched, 0.0, BR.COST_BP, rf=cash_rf)
    if strat is None:
        return None
    live_k = O.in_force(sched, rp.index).dropna()
    if len(live_k):
        strat = strat[strat.index >= live_k.index[0]]
    return strat


def run():
    t0 = time.time()
    panel = BR._panel("ticket")
    close = panel[0]
    days = ND.load_calendar()
    prod_face = {}
    if os.path.exists(PRODUCTION):
        try:
            prod_face = json.load(open(PRODUCTION, encoding="utf-8"))
        except ValueError:
            prod_face = {}
    sheet = prod_face.get("sheet") or {}
    decision_bar = sheet.get("last_decision_bar")
    decision_phase = phase_of_bar(days, decision_bar) if decision_bar else 0
    if decision_phase is None:
        raise RuntimeError("the published last_decision_bar %r is not on the official "
                           "calendar -- refusing to guess a phase" % (decision_bar,))

    ser, _turn = BR._book_series(panel, "causal", BR.N_HOLD, cost_bp=O.COST_BP)
    mkt_col = next((c for c in BT.MKT if c in close.columns), None)
    if mkt_col is None:
        raise RuntimeError("no 510300 column on this panel")
    mkt = close[mkt_col]
    idx = ser.index.intersection(mkt.index)
    rp, rm = BT.rets(ser.reindex(idx)), BT.rets(mkt.reindex(idx))
    rates = BW.load_repo_rates()
    cash_rf, cash_missing = BW.repo_daily_cash(idx, rates)
    cash_rf = cash_rf.reindex(idx).fillna(0.0)

    bars = [d.strftime("%Y-%m-%d") for d in rp.index]
    decision_grid = official_grid(days, bars, REBAL, decision_phase)

    prod_sched = O.k_schedule(rp, rm, BR.BETA_TARGET)
    prod_strat = overlay_strat(rp, rm, prod_sched, cash_rf)
    grid_sched = k_schedule_grid(rp, rm, BR.BETA_TARGET, decision_grid)
    grid_strat = overlay_strat(rp, rm, grid_sched, cash_rf)
    if prod_strat is None or grid_strat is None:
        raise RuntimeError("an overlay produced no live window")

    rows = []
    for label, strat in (("production", prod_strat), ("grid_only", grid_strat)):
        cells = BR._cells(strat, label)
        row = {"arm": label}
        for win in ("full", "ticket_window", "is", "oos"):
            node = cells.get(win) or {}
            row[win] = {"cagr_pp": node.get("cagr_pp"), "sharpe": node.get("sharpe"),
                        "maxdd_pp": node.get("maxdd_pp"), "vol": node.get("vol"),
                        "bars": node.get("bars")}
        row["cagr"] = (cells.get("full") or {}).get("cagr")
        row["k_moves"] = len(move_stats([k for _d, k, _b in
                                         (prod_sched if label == "production"
                                          else grid_sched)]))
        row["n_sched_bars"] = len(prod_sched if label == "production" else grid_sched)
        rows.append(row)
    pc = rows[0]["cagr"]
    for r in rows:
        r["cagr_delta_vs_production_pp"] = (
            None if r.get("cagr") is None or pc is None
            else round(100.0 * (r["cagr"] - pc), 3))

    # the phase sweep: the same rule at every phase the calendar offers
    for p in range(REBAL):
        g = official_grid(days, bars, REBAL, p)
        s = k_schedule_grid(rp, rm, BR.BETA_TARGET, g)
        strat = overlay_strat(rp, rm, s, cash_rf)
        cell = BR._cells(strat, "phase_%02d" % p) if strat is not None else {}
        row = {"arm": "phase_%02d" % p, "phase": p,
               "cagr": (cell.get("full") or {}).get("cagr"),
               "full": cell.get("full"), "ticket_window": cell.get("ticket_window"),
               "k_moves": len(move_stats([k for _d, k, _b in s])), "n_sched_bars": len(s)}
        row["cagr_delta_vs_production_pp"] = (
            None if row.get("cagr") is None or pc is None
            else round(100.0 * (row["cagr"] - pc), 3))
        rows.append(row)

    ident = {}
    pub_pp = None
    if os.path.exists(BAND_RULER):
        try:
            br = json.load(open(BAND_RULER, encoding="utf-8"))
            pub_pp = ((br.get("cells") or {}).get(BAND_KEY) or {}).get("ticket_window", {}) \
                .get("cagr_pp")
        except ValueError:
            pub_pp = None
    measured_pp = (rows[0].get("ticket_window") or {}).get("cagr_pp")
    if pub_pp is not None and measured_pp is not None:
        ident = {"published_pp": pub_pp, "measured_pp": measured_pp,
                 "gap_pp": round(measured_pp - pub_pp, 3), "tol_pp": IDENT_TOL_PP,
                 "passes": abs(measured_pp - pub_pp) <= IDENT_TOL_PP,
                 "anchor": CRITERIA["identity_anchor"]}
    else:
        ident = {"passes": None, "why": "anchor face unreadable",
                 "anchor": CRITERIA["identity_anchor"]}

    led = ledger_k_trace(days=days, phase=decision_phase)
    overl = sched_phase(days, prod_sched)
    verdict = decide(rows)

    doc = {
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "elapsed_sec": round(time.time() - t0, 1),
        "evidence_cutoff": str(rp.index[-1].date()),
        "bars": len(rp),
        "config": CRITERIA["held_config"],
        "criteria": CRITERIA,
        "grids": {
            "decision_bar_published": decision_bar,
            "decision_phase": decision_phase,
            "decision_bars": len(decision_grid),
            "overlay_phase": overl.get("phase"),
            "overlay_sched_bars": overl.get("n_bars"),
            "overlay_on_decision_grid": len({d for d, _k, _b in prod_sched
                                             if d.strftime("%Y-%m-%d") in decision_grid}),
            "min_hist": MIN_HIST,
            "bar_that_anchors_the_overlay": bars[MIN_HIST] if len(bars) > MIN_HIST else None,
            "sentence": ("the book re-decides on official phase %s; its k is refreshed on "
                         "phase %s" % (decision_phase, overl.get("phase"))),
        },
        "identity": ident,
        "ledger": led,
        "arms": rows,
        "verdict": verdict,
        "notes": [
            "every arm shares one book: same names, same fills, same 8 bp, same repo carry; "
            "only the set of bars on which k may change differs",
            "the overlay grid is anchored at panel row MIN_HIST (%d), the decision grid at "
            "the book's own first bar -- %s sessions apart" % (MIN_HIST, MIN_HIST % REBAL),
            "all twenty phases are priced so that no single cell can be quoted as the rule",
            "an arm with no schedule bars would be a silent identity arm; the selftest "
            "refuses that shape",
        ],
    }
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    write_md(doc)
    print("k_grid: %s delta=%spp spread=%spp | decision phase %s vs overlay phase %s | "
          "ledger %s/%s moves off the decision grid -> %s"
          % (verdict["state"], verdict.get("delta_pp"), verdict.get("phase_spread_pp"),
             decision_phase, overl.get("phase"), led.get("n_off_grid"), led.get("n_moves"),
             OUT_JSON))
    return doc


def write_md(doc):
    v = doc.get("verdict") or {}
    g = doc.get("grids") or {}
    lines = ["# 杠杆那一天：k 在不在决策 bar 上动，值多少（r1538）", "",
             "账本自证：%s；账本 %s 行里 k 动过 %s 次，其中 %s 次不落在决策相位的 bar 上。" % (
                 g.get("sentence"), (doc.get("ledger") or {}).get("rows"),
                 (doc.get("ledger") or {}).get("n_moves"),
                 (doc.get("ledger") or {}).get("n_off_grid")), "",
             "| 手臂 | 全窗年化 | 2024+ 年化 | 夏普 | 最大回撤 | k 变动次数 | 相对生产 pp |",
             "|---|---|---|---|---|---|---|"]
    for r in doc.get("arms") or []:
        lines.append("| %s | %s | %s | %s | %s | %s | %s |" % (
            r.get("arm"), (r.get("full") or {}).get("cagr_pp"),
            (r.get("ticket_window") or {}).get("cagr_pp"),
            (r.get("full") or {}).get("sharpe"), (r.get("full") or {}).get("maxdd_pp"),
            r.get("k_moves"), r.get("cagr_delta_vs_production_pp")))
    lines += ["", "判决：**%s**（Δ=%s pp，容差 %s pp）；二十个相位的跨度 %s pp，相位主导=%s。" % (
        v.get("state"), v.get("delta_pp"), v.get("tol_pp"), v.get("phase_spread_pp"),
        v.get("phase_dominates")), ""]
    os.makedirs(os.path.dirname(OUT_MD), exist_ok=True)
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def _num(x, d=6):
    try:
        return round(float(x), d)
    except (TypeError, ValueError):
        return None


def check(path=OUT_JSON):
    if not os.path.exists(path):
        print("[check] no face at %s" % path)
        return 2
    doc = json.load(open(path, encoding="utf-8"))
    asks = []
    want = decide(doc.get("arms") or [])
    got = doc.get("verdict") or {}
    if got.get("state") != want.get("state"):
        asks.append("published verdict %r != re-derived %r"
                    % (got.get("state"), want.get("state")))
    if abs(float(got.get("delta_pp") or 0.0) - float(want.get("delta_pp") or 0.0)) > 1e-6:
        asks.append("delta %r != %r" % (got.get("delta_pp"), want.get("delta_pp")))
    if bool(got.get("phase_dominates")) != bool(want.get("phase_dominates")):
        asks.append("phase_dominates %r != %r" % (got.get("phase_dominates"),
                                                  want.get("phase_dominates")))
    crit = doc.get("criteria") or {}
    if float(crit.get("tol_pp_per_year") or -1) != float(TOL_PP):
        asks.append("face frozen at tol %r, source says %r"
                    % (crit.get("tol_pp_per_year"), TOL_PP))
    ident = doc.get("identity") or {}
    if ident.get("passes") is False:
        asks.append("identity arm does not reproduce %s (gap %r pp)"
                    % (ident.get("anchor"), ident.get("gap_pp")))
    phases = [r for r in (doc.get("arms") or []) if r["arm"].startswith("phase_")]
    if len(phases) != REBAL:
        asks.append("%d phases priced, the rule says %d" % (len(phases), REBAL))
    for r in phases:
        if not r.get("n_sched_bars"):
            asks.append("%s has no schedule bars -- a silent identity arm" % r["arm"])
            break
    led_now = ledger_k_trace(phase=int((doc.get("grids") or {}).get("decision_phase") or 0))
    led_face = doc.get("ledger") or {}
    if led_now.get("n_moves") != led_face.get("n_moves"):
        asks.append("ledger k moves moved: face %r, now %r"
                    % (led_face.get("n_moves"), led_now.get("n_moves")))
    if led_now.get("last") != led_face.get("last"):
        asks.append("ledger last bar moved: face %r, now %r"
                    % (led_face.get("last"), led_now.get("last")))
    if doc.get("evidence_cutoff") and led_now.get("last") \
            and str(doc["evidence_cutoff"]) < str(led_now["last"]):
        asks.append("face cutoff %s is behind the ledger's last bar %s"
                    % (doc.get("evidence_cutoff"), led_now.get("last")))
    if asks:
        for a in asks:
            print("[check] " + a)
        return 1
    print("[check] OK verdict=%s delta=%spp spread=%spp | decision phase %s, overlay phase %s"
          " | ledger %s/%s off-grid"
          % (want.get("state"), want.get("delta_pp"), want.get("phase_spread_pp"),
             (doc.get("grids") or {}).get("decision_phase"),
             (doc.get("grids") or {}).get("overlay_phase"),
             led_now.get("n_off_grid"), led_now.get("n_moves")))
    return 0


# ---------------------------------------------------------------- selftest
def selftest():
    fails = []

    def leg(name, ok, detail=""):
        if not ok:
            fails.append(name)
        print("[%s] %s%s" % ("PASS" if ok else "FAIL", name,
                             (" | " + detail) if detail else ""))

    days = ["2026-01-05", "2026-01-06", "2026-01-07", "2026-01-08", "2026-01-09",
            "2026-01-12", "2026-01-13", "2026-01-14", "2026-01-15", "2026-01-16",
            "2026-01-19", "2026-01-20", "2026-01-21", "2026-01-22", "2026-01-23",
            "2026-01-26", "2026-01-27", "2026-01-28", "2026-01-29", "2026-01-30",
            "2026-02-02", "2026-02-03", "2026-02-04", "2026-02-05"]
    g0 = official_grid(days, days, 5, 0)
    leg("L1 phase 0 picks every fifth official session",
        g0 == {days[0], days[5], days[10], days[15], days[20]}, str(sorted(g0)[:5]))
    g2 = official_grid(days, days, 5, 2)
    leg("L2 phase 2 is a disjoint set of sessions, and the sets do not overlap",
        len(g2) == 5 and not (g2 & g0) and days[2] in g2, str(sorted(g2) or ""))
    leg("L3 a bar the official calendar does not contain is never a decision bar",
        official_grid(days, ["2026-02-09"], 5, 0) == set() and
        official_grid([], days, 5, 0) == set(), "")
    leg("L4 no phase means no grid -- refuse, never guess",
        official_grid(days, days, 5, None) == set(), "")
    leg("L5 phase wraps: 22 and 2 are the same phase on a 20-grid",
        official_grid(days, days, 20, 22) == official_grid(days, days, 20, 2), "")
    leg("L6 the decision phase comes from the published bar, not from row 0",
        phase_of_bar(days, days[2], 5) == 2 and phase_of_bar(days, "1999-01-01", 5) is None, "")

    idx = pd.DatetimeIndex(pd.to_datetime(days[:20]))
    rng = np.random.RandomState(7)
    rm = pd.Series(rng.normal(0, 0.01, 20), index=idx)
    rp = pd.Series(1.2 * rm.values + rng.normal(0, 0.002, 20), index=idx)
    grid = {days[0], days[5], days[10], days[15]}
    s = k_schedule_grid(rp, rm, 0.20, grid, min_hist=2)
    leg("L7 the grid schedule only emits on grid bars",
        all(d.strftime("%Y-%m-%d") in grid for d, _k, _b in s) and len(s) > 0, str(len(s)))
    leg("L8 the grid schedule emits the same k the unrestricted rule would on that bar",
        all(abs(k - min(1.0, max(0.0, 0.20 / b))) < 1e-12 for _d, k, b in s), "")
    free = O.k_schedule(rp, rm, 0.20, min_hist=2)
    free_bars = {d.strftime("%Y-%m-%d") for d, _k, _b in free}
    grid_bars = {d.strftime("%Y-%m-%d") for d, _k, _b in s}
    leg("L9 the free rule's own first emit is not a decision bar (the two grids differ)",
        bool(free_bars) and not (free_bars & grid_bars)
        and days[2] in free_bars and days[2] not in grid_bars,
        "free=%s grid=%s" % (sorted(free_bars), sorted(grid_bars)))
    leg("L10 a schedule on no grid bars is empty, not silently the free rule",
        k_schedule_grid(rp, rm, 0.20, set(), min_hist=2) == [], "")
    leg("L11 an empty schedule has no phase (unknown is not zero)",
        sched_phase(days, []) == {"phase": None, "n_bars": 0}, "")

    rows = [{"arm": "production", "cagr": 0.0900},
            {"arm": "grid_only", "cagr": 0.0850},
            {"arm": "phase_00", "cagr": 0.0851}, {"arm": "phase_01", "cagr": 0.0849}]
    v = decide(rows)
    leg("L12 half a point below production is GRID_COSTS",
        v["state"] == "GRID_COSTS" and v["delta_pp"] == -0.5, str(v.get("delta_pp")))
    rows2 = [{"arm": "production", "cagr": 0.0900},
             {"arm": "grid_only", "cagr": 0.0910},
             {"arm": "phase_00", "cagr": 0.0911}]
    leg("L13 a tenth of a point is inside the tolerance and reads NEUTRAL",
        decide(rows2)["state"] == "GRID_NEUTRAL", decide(rows2)["state"])
    rows3 = [{"arm": "production", "cagr": 0.0900},
             {"arm": "grid_only", "cagr": 0.0899},
             {"arm": "phase_00", "cagr": 0.0870},
             {"arm": "phase_05", "cagr": 0.0930}]
    v3 = decide(rows3)
    leg("L14 a phase spread wider than the effect is named, not hidden",
        v3["state"] == "GRID_NEUTRAL" and v3["phase_dominates"] is True
        and v3["phase_spread_pp"] == 0.6, str(v3.get("phase_spread_pp")))
    leg("L15 a missing arm is INCOMPLETE, not a pass",
        decide([{"arm": "production", "cagr": 0.09}])["state"] == "INCOMPLETE", "")
    leg("L16 the verdict re-derives from the rows alone (no re-run, no clock)",
        decide(json.loads(json.dumps(rows)))["state"] == "GRID_COSTS", "")
    leg("L17 the tolerance and phase count are the frozen ones",
        abs(TOL_PP - 0.25) < 1e-12 and CRITERIA["tol_pp_per_year"] == 0.25
        and REBAL == 20, "rebal=%s" % REBAL)

    n = 17
    print("\nselftest: %d/%d passed" % (n - len(fails), n))
    if fails:
        for f in fails:
            print("  FAILED: " + f)
        return 1
    return 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--selftest" in argv:
        return selftest()
    if "--check" in argv:
        return check()
    run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
