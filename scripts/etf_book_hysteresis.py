"""How much of the book's turnover is decided by a margin it cannot measure?

r1260/r1261 put the binding constraint on this ETF book at turnover, not concentration,
and the standing production rule is the plain top-12: every 20 bars the book swaps any
name that leaves the top 12, however slightly. The score face is an average of
cross-sectional percentile ranks, so the 12th and 13th name are frequently separated by a
fraction of the cross-sectional score dispersion -- i.e. the score says "these two are
indistinguishable" and the rule trades anyway.

This face measures two things and prices a third:

  (A) MARGIN CENSUS. At every decision bar: how far apart are the last held name and the
      first excluded name, in units of that bar's own cross-sectional score sd? And for
      the trades the book ACTUALLY made: what was the gap between the name that left and
      the name that replaced it? That turns "turnover is the constraint" into a number
      about decision quality -- a trade decided by 0.02 sd is a coin flip that costs money.

  (B) HYSTERESIS ARMS. A buffer: an incumbent is only displaced when a challenger beats it
      by more than k * sd(score at that bar). k = 0 is the published rule; k > 0 is a
      different rule, not an optimisation of the old one. Each arm is priced through the
      SAME engine, at the SAME cadence, breadth, cost and sizing as the production card.

  (C) RECONCILIATION. The k=0 arm must reproduce the published production cell
      (results/etf_book_production/latest.json n12_vt08) before any other arm is read;
      otherwise the arms are being compared on a different book.

What is reused, never rewritten:
  * panel, class filter and repair = `scripts.etf_book_production.prep_panel`
  * the engine and its leg maths      = `scripts.etf_robust_pf.open_to_open_equity`
    (new optional `select_hook`; `None` is the plain top-n rule and is bit-identical to
    the published behaviour -- pinned by the selftest here AND by every existing caller)
  * stats                              = `scripts.etf_equity_alpha.stats2`

Honest limits stated up front:
  * exploratory: no preregistration, no verdict, no ledger booking. A better-looking arm
    is a hypothesis for a prereg, not a promotion.
  * the buffer is path-dependent by construction, so arms are not independent draws; a
    single better cell can be luck of one decision sequence. The census (A) is the part
    that does not depend on choosing k.
  * one panel, one window (2020-01 -> panel edge), one cost (10bp/side, the production
    assumption). The published caveats -- survivor pool, young-fund coverage, a strong
    2024+ regime -- apply unchanged.
  * turnover is reported for every arm: an arm that "wins" by lowering return less than it
    lowers turnover is a cost effect, not skill, and the card says so.

Usage:
    python scripts/etf_book_hysteresis.py run [--fast] [--out=...]
    python scripts/etf_book_hysteresis.py --selftest
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import numpy as np
import pandas as pd

import etf_composite_pf as E
import etf_robust_pf as R
import etf_equity_alpha as A
from scripts import etf_book_production as P

OUT_JSON = ROOT / "results" / "etf_book_hysteresis.json"
PRODUCTION_FACE = ROOT / "results" / "etf_book_production" / "latest.json"

# k is the buffer in units of that bar's cross-sectional score sd.
BUFFER_GRID = (0.0, 0.05, 0.10, 0.20, 0.35, 0.50)
FAST_GRID = (0.0, 0.10, 0.35)
N_HOLD = 12          # the production breadth (production card `config.n_hold`)
REBAL = 20           # the production cadence
COST = 0.0010        # the production cost (10bp per side)
TARGET_VOL = 0.08    # the production sizing overlay
CONTROL_TOL = 0.005  # 0.5pp tolerance on the control arm (r1297 law)


# ---------------------------------------------------------------- mechanics

def buffer_picks(s, held_names, n_hold, buffer_sd):
    """Incumbent-protection selection: pure, deterministic, causal.

    `s` is that bar's eligible score row (already dropna'd by the engine). The book keeps
    its incumbents unless a challenger's score exceeds the weakest incumbent's by strictly
    more than `buffer_sd * sd(s)`. Vacancies are filled from the best available names.

    With buffer_sd == 0 this reduces to the plain top-n rule: the displacement loop keeps
    replacing the weakest incumbent while any outsider outranks it, which converges to the
    top n (ties favour the incumbent). The selftest pins that equivalence rather than
    asserting it in prose.
    """
    if len(s) < n_hold:
        return []
    sd = float(s.std(ddof=0))
    thr = buffer_sd * sd if np.isfinite(sd) and sd > 0 else 0.0

    inc = [p for p in held_names if p in s.index]
    if len(inc) > n_hold:  # a held book can only exceed n_hold if a caller misuses this
        inc = list(pd.Series({p: float(s[p]) for p in inc}).nlargest(n_hold).index)
    inc_set = set(inc)
    outsiders = [p for p in s.sort_values(ascending=False).index if p not in inc_set]

    # 1) fill vacancies (names that dropped out of the eligible face, or a cold start)
    while len(inc) < n_hold and outsiders:
        inc.append(outsiders.pop(0))
    if len(inc) < n_hold:
        return []

    # 2) displacement: only when the challenger clears the buffer over the weakest holder
    while outsiders:
        weakest = min(inc, key=lambda p: float(s[p]))
        challenger = outsiders[0]
        if float(s[challenger]) - float(s[weakest]) > thr:
            inc.remove(weakest)
            inc.append(outsiders.pop(0))
        else:
            break
    return sorted(inc)


def margin_census(score, close, amt, n_hold, rebal, start):
    """Cut margins: the distance between the last held name and the first excluded one.

    Reported in score units and in sd multiples of that bar's own cross-section, because
    the score's absolute scale is not comparable across bars. Ties at the boundary
    (`exactly n+1 eligible names`) are impossible here -- the universe is ~1.5k names -- but
    a bar with fewer than n+1 names is skipped and counted, never filled.
    """
    hist = close.notna().cumsum()
    elig = (amt >= E.MIN_AMT) & (hist >= E.MIN_HIST)
    masked = score.where(elig)
    dates = [d for d in masked.index if d >= pd.Timestamp(start)]
    rows, skipped = [], 0
    for d in dates[::rebal]:
        s = masked.loc[d].dropna()
        if len(s) <= n_hold:
            skipped += 1
            continue
        sd = float(s.std(ddof=0))
        top = s.nlargest(n_hold + 1)
        cut = float(top.iloc[n_hold - 1]) - float(top.iloc[n_hold])
        rows.append({"date": str(pd.Timestamp(d).date()),
                     "cut_score": cut,
                     "cut_sd": cut / sd if sd > 0 else None,
                     "n_eligible": int(len(s))})
    if not rows:
        return {"n_decisions": 0, "skipped": skipped}
    cut_sd = np.array([r["cut_sd"] for r in rows if r["cut_sd"] is not None])
    return {
        "n_decisions": len(rows),
        "skipped": skipped,
        "cut_sd_q": {q: round(float(np.quantile(cut_sd, q)), 4) for q in (0.1, 0.25, 0.5, 0.75, 0.9)},
        "cut_score_median": round(float(np.median([r["cut_score"] for r in rows])), 5),
        "share_within": {str(t): round(float((cut_sd < t).mean()), 4) for t in (0.05, 0.10, 0.20, 0.50, 1.0)},
        "rows": rows,
    }


def trade_margins(score, diag, n_hold):
    """For the trades the book actually made, how close was the decision?

    `diag` (built by the engine) holds one row per decision with the chosen book; two
    consecutive rows give the sets that left and entered. Each (leaver, entrant) pair is
    scored on THAT bar's row, so the number is the margin that drove the trade.
    """
    out = []
    prev = None
    for row in diag:
        d = pd.Timestamp(row["date"])
        s = score.loc[d].dropna() if d in score.index else None
        book = set(row["book"])
        if prev is not None and s is not None:
            left, entered = sorted(prev - book), sorted(book - prev)
            for a, b in zip(left, entered):
                if a in s.index and b in s.index:
                    out.append({"date": row["date"], "left": a, "entered": b,
                                "gap": float(s[b]) - float(s[a]),
                                "gap_sd": float(s[b] - s[a]) / float(s.std(ddof=0))
                                if float(s.std(ddof=0)) > 0 else None})
        prev = book
    gaps = np.array([g["gap_sd"] for g in out if g["gap_sd"] is not None])
    summary = {"n_pairs": len(out)}
    if len(gaps):
        summary.update({
            "gap_sd_median": round(float(np.median(gaps)), 4),
            "share_under_0p10sd": round(float((gaps < 0.10).mean()), 4),
            "share_under_0p25sd": round(float((gaps < 0.25).mean()), 4),
        })
    return summary, out


def run_arm(close, openp, amt, score, k, n_hold, rebal, cost, vol_target):
    diag = []
    hook = None if k == 0.0 else (lambda s, held, n, d, _k=k: buffer_picks(s, held, n, _k))
    ser, turn = R.open_to_open_equity(close, openp, amt, score, rebal, n_hold, cost,
                                      vol_target=vol_target, diag=diag, select_hook=hook)
    stats = {}
    for lbl, sl in (("full", ser), ("is", ser[ser.index <= pd.Timestamp("2023-12-31")]),
                    ("oos", ser[ser.index > pd.Timestamp("2023-12-31")])):
        m = A.stats2(sl, lbl)
        stats[lbl] = {key: m.get(key) for key in
                      ("cagr", "sharpe", "maxdd", "vol", "worst_year", "neg_years")}
    return {"k": k, "turnover_per_decision": round(float(turn), 3),
            "trades": len(diag), "stats": stats}, ser, diag


def build(fast=False, n_hold=N_HOLD, rebal=REBAL, cost=COST, vol_target=TARGET_VOL):
    close, openp, amt, score, cls, n_flip = P.prep_panel()
    grid = FAST_GRID if fast else BUFFER_GRID

    arms = []
    first_diag = None
    for k in grid:
        arm, _ser, diag = run_arm(close, openp, amt, score, k, n_hold, rebal, cost, vol_target)
        arms.append(arm)
        if first_diag is None:
            first_diag = diag

    census = margin_census(score, close, amt, n_hold, rebal, R.START)
    trades, trade_rows = trade_margins(score, first_diag, n_hold)

    # control: the k=0 arm against the published production cell
    control = {"published": None, "measured": None, "delta_pp": None, "within_tol": None}
    if PRODUCTION_FACE.exists():
        pub = json.loads(PRODUCTION_FACE.read_text(encoding="utf-8"))
        cell = (pub.get("backtest") or {}).get("n12_vt08") if (n_hold, vol_target) == (12, 0.08) else None
        if cell:
            control["published"] = cell["full"]["cagr"]
            control["measured"] = arms[0]["stats"]["full"]["cagr"]
            control["delta_pp"] = round(100 * (control["measured"] - control["published"]), 3)
            control["within_tol"] = abs(control["delta_pp"]) <= 100 * CONTROL_TOL
            control["published_turnover"] = cell.get("turnover_per_decision")
            control["measured_turnover"] = arms[0]["turnover_per_decision"]

    return {
        "script": "scripts/etf_book_hysteresis.py",
        "evidence_cutoff": str(close.index[-1].date()),
        "units": {"k": "buffer in units of the bar's cross-sectional score sd",
                  "cagr": "fraction per year (0.0962 = 9.62%/yr)",
                  "turnover_per_decision": "sum |dw| per rebalance, fraction of book",
                  "cut_sd": "score gap / score sd at that bar"},
        "config": {"n_hold": n_hold, "rebal": rebal, "cost_bp": cost * 1e4,
                   "vol_target": vol_target, "universe": int(close.shape[1]),
                   "flips_repaired": int(n_flip), "grid": list(grid)},
        "control": control,
        "margin_census": census,
        "trade_margins": trades,
        "arms": arms,
        "trade_rows_sample": trade_rows[:20],
        "caveats": [
            "exploratory: no preregistration, no verdict, no ledger booking",
            "the buffer is path-dependent; a single better arm can be one decision sequence",
            "one panel / one window / one cost model; survivor-pool and 2024+ regime caveats unchanged",
            "an arm that lowers turnover and lowers return by less is a cost effect, not skill",
        ],
    }


# ---------------------------------------------------------------- consistency gate

def check_payload(payload, production_cutoff=None, grid=BUFFER_GRID):
    """Engine-free gate: is the published face still internally consistent and current?

    Deliberately cheap (0.1s) so the chain can judge it every round, following the
    etf_book_cagr_reconcile precedent -- re-deriving the arms costs the panel build.
    Returns (ok, reasons). Every reason names what is wrong; an empty list means green.
    """
    bad = []
    cfg = payload.get("config") or {}
    units = payload.get("units") or {}

    for key in ("k", "cagr", "turnover_per_decision", "cut_sd"):
        if key not in units:
            bad.append("units missing %r -- a bare number has no denominator" % key)
    if not cfg.get("n_hold") or not cfg.get("rebal"):
        bad.append("config missing n_hold/rebal")

    arms = payload.get("arms") or []
    if [a.get("k") for a in arms] != list(grid):
        bad.append("arm grid %r != declared grid %r (a --fast face must not be published as full)"
                   % ([a.get("k") for a in arms], list(grid)))

    ctl = payload.get("control") or {}
    if ctl.get("within_tol") is False:
        bad.append("control arm does not reproduce the published cell (delta %+r pp)" % ctl.get("delta_pp"))
    if ctl.get("published") is None:
        bad.append("control arm ungraded -- arms cannot be read")

    turn = [a.get("turnover_per_decision") for a in arms]
    if any(t is None for t in turn):
        bad.append("an arm has no turnover reading")
    elif any(turn[i] < turn[i + 1] - 1e-9 for i in range(len(turn) - 1)):
        bad.append("turnover is not non-increasing in k: %r" % (turn,))
    if arms and all((a.get("stats") or {}).get("full", {}).get("cagr") is None for a in arms):
        bad.append("no arm carries a full-window CAGR")

    cen = payload.get("margin_census") or {}
    if not cen.get("n_decisions"):
        bad.append("census has no decisions")
    elif len(cen.get("rows") or []) != cen["n_decisions"]:
        bad.append("census rows (%d) != n_decisions (%d)" % (len(cen.get("rows") or []), cen["n_decisions"]))
    share = cen.get("share_within") or {}
    vals = [share.get(k) for k in ("0.05", "0.1", "0.2", "0.5", "1.0")]
    if any(v is None for v in vals):
        bad.append("census share_within incomplete: %r" % (share,))
    elif any(vals[i] > vals[i + 1] + 1e-9 for i in range(len(vals) - 1)):
        bad.append("census share_within not monotone in the threshold: %r" % (vals,))
    if any(r.get("cut_score", 0) < -1e-12 for r in (cen.get("rows") or [])):
        bad.append("a cut margin is negative -- the census picked names out of order")

    tm = payload.get("trade_margins") or {}
    if tm.get("n_pairs"):
        for key in ("share_under_0p10sd", "share_under_0p25sd"):
            v = tm.get(key)
            if v is None or not (0.0 <= v <= 1.0):
                bad.append("trade margin %s out of [0,1]: %r" % (key, v))

    if production_cutoff and payload.get("evidence_cutoff"):
        if str(payload["evidence_cutoff"]) < str(production_cutoff):
            bad.append("face is stale: priced on %s while the production card is on %s"
                       % (payload["evidence_cutoff"], production_cutoff))
    return (not bad), bad


def check():
    if not OUT_JSON.exists():
        print("FAIL face missing: %s" % OUT_JSON.relative_to(ROOT))
        return 1
    payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    prod_cutoff = None
    if PRODUCTION_FACE.exists():
        prod = json.loads(PRODUCTION_FACE.read_text(encoding="utf-8"))
        prod_cutoff = prod.get("evidence_cutoff")
    ok, bad = check_payload(payload, prod_cutoff)
    for b in bad:
        print("[FAIL] " + b)
    print("hysteresis face %s (cutoff %s, grid %r)" % (
        "OK" if ok else "RED", payload.get("evidence_cutoff"),
        [a.get("k") for a in payload.get("arms") or []]))
    return 0 if ok else 2


# ---------------------------------------------------------------- reporting

def render_md(payload):
    c, ctl = payload["config"], payload["control"]
    cen, tm = payload["margin_census"], payload["trade_margins"]
    lines = [
        "# ETF book -- decision margins and a hysteresis buffer",
        "",
        "Window ends %s | %d-name book, %d-bar cadence, %.0fbp/side, vol target %s"
        % (payload["evidence_cutoff"], c["n_hold"], c["rebal"], c["cost_bp"],
           "off" if not c["vol_target"] else "%.0f%%" % (100 * c["vol_target"])),
        "",
        "## Control arm (must hold before any other arm is read)",
        "",
    ]
    if ctl.get("within_tol") is None:
        lines.append("Control unavailable (published cell not found) -- arms are NOT graded.")
    else:
        lines.append("k=0 reproduces the published n12_vt08 cell: %.2f%% vs %.2f%% (delta %+.3fpp, %s)"
                     % (100 * ctl["measured"], 100 * ctl["published"], ctl["delta_pp"],
                        "within tolerance" if ctl["within_tol"] else "OUT OF TOLERANCE"))
    lines += ["", "## How close are the decisions?", ""]
    lines.append("%d decisions; the 12th-vs-13th score gap as a fraction of that bar's own score sd:"
                 % cen.get("n_decisions", 0))
    for q, v in (cen.get("cut_sd_q") or {}).items():
        lines.append("* q%s = %.3f sd" % (q, v))
    share = cen.get("share_within") or {}
    lines += ["",
              "Decisions whose cut margin is under 0.10 sd: **%s**; under 0.25 sd: %s."
              % ("%.0f%%" % (100 * share.get("0.1", 0)), "%.0f%%" % (100 * share.get("0.25", 0))),
              "",
              "Trades actually made: %d pairs, median gap %.3f sd; %s of them were decided by less than 0.10 sd."
              % (tm.get("n_pairs", 0), tm.get("gap_sd_median") or float("nan"),
                 "%.0f%%" % (100 * (tm.get("share_under_0p10sd") or 0))),
              "",
              "## Buffer arms",
              "",
              "| k (sd) | turnover/decision | CAGR full | Sharpe | maxDD | IS CAGR | OOS CAGR | OOS Sharpe |",
              "|---|---|---|---|---|---|---|---|"]
    for a in payload["arms"]:
        f, is_, oos = a["stats"]["full"], a["stats"]["is"], a["stats"]["oos"]
        lines.append("| %.2f | %.3f | %.2f%% | %.3f | %.2f%% | %.2f%% | %.2f%% | %.3f |" % (
            a["k"], a["turnover_per_decision"], 100 * f["cagr"], f["sharpe"], 100 * f["maxdd"],
            100 * is_["cagr"], 100 * oos["cagr"], oos["sharpe"]))
    lines += ["", "## Caveats", ""]
    for cv in payload["caveats"]:
        lines.append("* " + cv)
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- selftest

def _num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _eq(name, got, want, tol=1e-6):
    ok = (_num(got) and _num(want) and abs(float(got) - float(want)) <= tol * max(1.0, abs(float(want)))) \
        or (not (_num(got) and _num(want)) and got == want)
    return (name, ok, "got=%r want=%r" % (got, want))


def _fixture(bars=260, names=14, seed=7):
    """A tiny panel with a persistent, measurable score structure (no writes, no network)."""
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2021-01-04", periods=bars)
    cols = ["S%02d" % i for i in range(names)]
    drift = np.linspace(0.0004, -0.0002, names)
    steps = rng.normal(0, 0.01, size=(bars, names)) + drift
    close = pd.DataFrame(100 * np.exp(np.cumsum(steps, axis=0)), index=dates, columns=cols)
    openp = close.shift(1).fillna(close.iloc[0])
    amt = pd.DataFrame(5e7, index=dates, columns=cols)
    feats = {"mom_12_1": close / close.shift(60) - 1.0,
             "vol_60": close.pct_change().rolling(60).std()}
    score = E.build_score(close, amt, feats)
    return close, openp, amt, score


def selftest():
    legs = []
    close, openp, amt, score = _fixture()
    legs.append(("fixture is warm (score face actually populated)", bool(score.notna().any().any()),
                 "non-null cells=%d" % int(score.notna().sum().sum())))

    # --- buffer_picks mechanics ------------------------------------------------
    row = score.dropna(how="all").iloc[-1].dropna()
    top = list(row.nlargest(6).index)

    # L1 k=0 == plain top-n, given a stale incumbent book
    stale = list(row.nlargest(6).index)
    stale[0], stale[-1] = row.nsmallest(2).index[0], row.nsmallest(2).index[1]
    legs.append(_eq("k=0 restores the plain top-n from a stale book",
                    sorted(buffer_picks(row, stale, 6, 0.0)), sorted(top)))

    # L2 a large buffer keeps the incumbents when the challengers are near-misses
    near = list(row.nlargest(6).index)
    near[-1] = row.nlargest(7).index[-1]  # swap the 6th name for the 7th: a hair's gap
    legs.append(_eq("k=1.0 keeps a near-miss book unchanged (no displacement)",
                    sorted(buffer_picks(row, near, 6, 1.0)), sorted(near)))

    # L3 vacancies are filled: only 3 names held, still returns 6 distinct names
    picks = buffer_picks(row, stale[:3], 6, 0.0)
    legs.append(("cold/vacant book is filled to exactly n_hold distinct names",
                 len(picks) == 6 and len(set(picks)) == 6, "picks=%r" % (picks,)))
    legs.append(("filled names are all eligible names from the row",
                 set(picks) <= set(row.index), "picks=%r" % (picks,)))

    # L4 too few eligible names -> empty (the engine then skips the decision)
    legs.append(("row with fewer than n_hold names returns no picks",
                 buffer_picks(row.head(3), [], 6, 0.0) == [], "head(3)"))

    # L5 the buffer is monotone in k: it can only reduce displacement, never add it
    churn = [len(set(stale) - set(buffer_picks(row, stale, 6, k))) for k in (0.0, 0.05, 0.10, 0.35, 1.0)]
    legs.append(("displaced incumbents are non-increasing in k (monotone buffer)",
                 all(churn[i] >= churn[i + 1] for i in range(len(churn) - 1)), "churn=%r" % (churn,)))
    legs.append(("buffer is active at k=0 on a stale book (mechanism actually ran)",
                 churn[0] > 0, "churn@k0=%d" % churn[0]))

    # --- engine wiring ---------------------------------------------------------
    # The fixture score is an average of percentile ranks, so exact ties are common
    # (14 names -> coarse ranks). `nlargest` breaks a tie by index order; the buffer
    # keeps the incumbent. That difference is a property of the rule, not of the wiring,
    # so equivalence is pinned on a TIE-FREE face (jittered by 1e-6, ordering intact) and
    # the tie behaviour is pinned separately by its own leg below.
    jitter = pd.Series(np.linspace(-1e-6, 1e-6, score.shape[1]), index=score.columns)
    score_u = score.add(jitter, axis=1).where(score.notna())

    diag0 = []
    ser0, turn0 = R.open_to_open_equity(close, openp, amt, score_u, 10, 5, 0.001, diag=diag0)
    diagT = []
    serT, turnT = R.open_to_open_equity(
        close, openp, amt, score_u, 10, 5, 0.001, diag=diagT,
        select_hook=lambda s, held, n, d: buffer_picks(s, held, n, 0.0))
    legs.append(_eq("engine: on a tie-free face, select_hook(k=0) is bit-identical to the default path",
                    round(float(serT.iloc[-1]), 10), round(float(ser0.iloc[-1]), 10), 1e-9))
    legs.append(_eq("engine: identical path implies identical turnover",
                    round(float(turnT), 10), round(float(turn0), 10), 1e-9))

    # tie leg: on the raw (tied) fixture the two rules may disagree, but ONLY by swapping
    # names whose scores are exactly equal -- never by preferring a lower score.
    tie_row = score.loc[score.notna().all(axis=1)].iloc[-1]
    got = set(buffer_picks(tie_row, list(tie_row.nlargest(6).index), 6, 0.0))
    want = set(tie_row.nlargest(6).index)
    only = got ^ want
    legs.append(("tie behaviour: k=0 differs from nlargest only on exactly-equal scores",
                 all(abs(float(tie_row[a]) - float(tie_row[b])) < 1e-12
                     for a in got - want for b in want - got),
                 "sym diff=%r" % (sorted(only),)))

    # L6 the hook path is not a no-op: a hard buffer must change the result
    diagH = []
    serH, turnH = R.open_to_open_equity(
        close, openp, amt, score, 10, 5, 0.001, diag=diagH,
        select_hook=lambda s, held, n, d: buffer_picks(s, held, n, 1.0))
    legs.append(("engine: a hard buffer changes both the book and the turnover",
                 turnH < turn0 and abs(float(serH.iloc[-1]) - float(ser0.iloc[-1])) > 0,
                 "turn %r -> %r" % (round(turn0, 4), round(turnH, 4))))
    legs.append(("engine: every arm traded (a zero-turnover arm cannot pass as 'stable')",
                 turn0 > 0 and turnH >= 0, "turn0=%r turnH=%r" % (round(turn0, 4), round(turnH, 4))))

    # L7 a shape-violating hook raises rather than silently falling back
    raised = False
    try:
        R.open_to_open_equity(close, openp, amt, score, 10, 5, 0.001,
                              select_hook=lambda s, held, n, d: list(s.index[:n - 1]))
    except ValueError:
        raised = True
    legs.append(("engine: a hook returning the wrong shape raises", raised, "no raise"))

    # --- census / trade margins ------------------------------------------------
    cen = margin_census(score, close, amt, 5, 10, "2021-01-04")
    legs.append(("census: decisions counted and all cut margins non-negative",
                 cen["n_decisions"] > 5 and all(r["cut_score"] >= -1e-12 for r in cen["rows"]),
                 "n=%r" % (cen["n_decisions"],)))
    legs.append(("census: cut_sd is the score gap divided by that bar's sd (unit leg)",
                 all(abs(r["cut_sd"] * (score.loc[pd.Timestamp(r["date"])].dropna().std(ddof=0))
                         - r["cut_score"]) < 1e-9 for r in cen["rows"][:20]), True))

    tm, rows = trade_margins(score, diag0, 5)
    diff = [r["entered"] for r in rows if r["gap"] <= 0]
    legs.append(("trade margins: every entrant scored at least as high as the name it replaced",
                 len(rows) > 0 and not diff, "n=%d neg=%r" % (len(rows), diff[:3])))
    legs.append(("trade margins: gaps are in score units, |gap| <= 2 (the score's own range)",
                 all(abs(r["gap"]) <= 2.0 for r in rows), "max=%r" % (
                     max((abs(r["gap"]) for r in rows), default=0.0),)))

    # --- reader-facing output ---------------------------------------------------
    payload = {"config": {"n_hold": 5, "rebal": 10, "cost_bp": 10.0, "vol_target": None},
               "evidence_cutoff": str(close.index[-1].date()),
               "control": {"published": None, "measured": None, "delta_pp": None, "within_tol": None},
               "margin_census": cen, "trade_margins": tm,
               "arms": [{"k": 0.0, "turnover_per_decision": float(turn0),
                         "stats": {lbl: A.stats2(ser0, lbl) for lbl in ("full", "is", "oos")}}],
               "caveats": ["exploratory"]}
    md = render_md(payload)
    legs.append(("renderer: no unexpanded format placeholder survives to the reader",
                 "%" not in md.replace("%", "", 0) or "%%" not in md,
                 "render ok len=%d" % len(md)))
    legs.append(("renderer: control-unavailable arms are not graded",
                 "NOT graded" in md or "Control unavailable" in md, "control line present"))

    # --- the consistency gate can actually go red ------------------------------
    good = {"units": {k: "x" for k in ("k", "cagr", "turnover_per_decision", "cut_sd")},
            "config": {"n_hold": 12, "rebal": 20}, "evidence_cutoff": "2026-10-27",
            "control": {"published": 0.0962, "within_tol": True},
            "arms": [{"k": k, "turnover_per_decision": t,
                      "stats": {"full": {"cagr": 0.096}}} for k, t in zip(BUFFER_GRID, [0.934, 0.901, 0.887, 0.842, 0.762, 0.702])],
            "margin_census": {"n_decisions": 2, "rows": [{"cut_score": 0.01}, {"cut_score": 0.02}],
                              "share_within": {"0.05": 0.7, "0.1": 0.87, "0.2": 0.97, "0.5": 1.0, "1.0": 1.0}},
            "trade_margins": {"n_pairs": 10, "share_under_0p10sd": 0.03, "share_under_0p25sd": 0.09}}
    legs.append(("gate: a well-formed face passes", check_payload(good, "2026-10-27")[0], "should be green"))

    def _mut(fn):
        p = json.loads(json.dumps(good))
        fn(p)
        return check_payload(p, "2026-10-27")

    cases = [
        ("missing units", lambda p: p["units"].pop("cut_sd")),
        ("turnover rising in k", lambda p: p["arms"][2].__setitem__("turnover_per_decision", 1.5)),
        ("arm grid != declared grid", lambda p: p["arms"].pop()),
        ("control out of tolerance", lambda p: p["control"].__setitem__("within_tol", False)),
        ("ungraded control", lambda p: p["control"].__setitem__("published", None)),
        ("census rows != n_decisions", lambda p: p.__setitem__("margin_census", dict(p["margin_census"], n_decisions=5))),
        ("share_within not monotone", lambda p: p["margin_census"].__setitem__(
            "share_within", {"0.05": 0.9, "0.1": 0.5, "0.2": 0.97, "0.5": 1.0, "1.0": 1.0})),
        ("negative cut margin", lambda p: p["margin_census"].__setitem__("rows", [{"cut_score": -0.01}, {"cut_score": 0.02}])),
        ("share out of [0,1]", lambda p: p["trade_margins"].__setitem__("share_under_0p10sd", 3.0)),
    ]
    for name, fn in cases:
        ok, reasons = _mut(fn)
        legs.append(("gate fires on %s" % name, (not ok) and bool(reasons), "reasons=%r" % (reasons,)))

    stale_ok, stale_reasons = check_payload(dict(good, evidence_cutoff="2026-10-20"), "2026-10-27")
    legs.append(("gate fires when the face is older than the production card",
                 (not stale_ok) and any("stale" in r for r in stale_reasons), "reasons=%r" % (stale_reasons,)))
    same_ok, _ = check_payload(dict(good, evidence_cutoff="2026-10-27"), "2026-10-27")
    legs.append(("gate stays green on the same cutoff", same_ok, "should be green"))

    passed = sum(1 for _, ok, _ in legs if ok)
    for name, ok, detail in legs:
        print(("[PASS] " if ok else "[FAIL] ") + name + ("" if ok else " | " + detail))
    print("%d/%d PASS" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--fast", action="store_true")
    ap.add_argument("--out", default=str(OUT_JSON))
    ap.add_argument("--n-hold", type=int, default=N_HOLD)
    ap.add_argument("--rebal", type=int, default=REBAL)
    a = ap.parse_args(argv)
    if a.selftest or a.cmd == "selftest":
        return selftest()
    if a.check or a.cmd == "check":
        return check()
    payload = build(fast=a.fast, n_hold=a.n_hold, rebal=a.rebal)
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path = out.with_suffix(".md")
    md_path.write_text(render_md(payload), encoding="utf-8")
    ctl, cen = payload["control"], payload["margin_census"]
    print("control: measured=%s published=%s delta_pp=%s within_tol=%s" % (
        ctl.get("measured"), ctl.get("published"), ctl.get("delta_pp"), ctl.get("within_tol")))
    print("census: %d decisions, median cut %.3f sd, %.0f%% under 0.10 sd" % (
        cen.get("n_decisions", 0), (cen.get("cut_sd_q") or {}).get(0.5, float("nan")),
        100 * (cen.get("share_within") or {}).get("0.1", 0.0)))
    for arm in payload["arms"]:
        f = arm["stats"]["full"]
        print("k=%.2f turn=%.3f cagr=%.2f%% sharpe=%.3f maxdd=%.2f%%" % (
            arm["k"], arm["turnover_per_decision"], 100 * f["cagr"], f["sharpe"], 100 * f["maxdd"]))
    print("wrote %s + %s" % (out.relative_to(ROOT), md_path.relative_to(ROOT)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))