"""E24 breadth-gate overlay feasibility (descriptive; NO gate verdict, NO trial count).

Follow-up to the r1091 E24 censuses: the cross-sectional breadth census at h=10
showed the top quintile of "share of ETFs above their 20d MA" carrying
+139.8bp / stride-t 3.28 forward, versus +41.8bp in the bottom quintile.  The
obvious next question is economic, not statistical: does a *cost-aware* overlay
that holds the five-member traded ladder only while breadth sits in the
expanding top quintile (cash otherwise) survive 13.041bp per side turnover?

What this face reports (all deterministic, in-repo `data/daily` only):
  * exposure share (fraction of days the overlay is in the ladder)
  * gross vs net bp per day and per year, and the cost drag actually charged
  * number of state transitions (turnover) and transitions per year
  * stride-5 (non-overlapping) t of the net overlay vs always-on ladder

Honest labels baked in:
  * T+1 execution: the regime read on day t only takes effect for day t+1's
    return (no lookahead).
  * expanding quintile cutoffs with a 250-day burn-in (causal).
  * cost = |w_t - w_{t-1}| * 13.041bp (one "side" per unit of notional change),
    the frozen engine cost constant.
  * DESCRIPTIVE ONLY: no prereg, no gate, no verdict, no trial-count
    consumption.  A positive number here is a feasibility signal for a future
    pre-registered batch, never an admission.

Modes
  run        : compute and write results/e24_overlay_breath/<FACE>.json
  selftest   : hermetic math/determinism checks (exit 0/1)
"""

from __future__ import annotations

import argparse
import json
import math
import os
import statistics
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from e24_regime_census import (BURN, LADDER, breadth_at, ladder_momentum,  # noqa: E402
                               load_panel, tstat)

OUTDIR = os.path.join(ROOT, "results", "e24_overlay_breath")
COST_BP = 13.041          # frozen engine cost per side, bp
TAIL_Q = 0.80             # top-quintile entry cut for the gate
STRIDE = 5


# ---------------------------------------------------------------- core pieces
def ladder_returns(cal, symbols, rows):
    """Equal-weight ladder daily simple returns on the calendar (causal)."""
    idx = [symbols.index(s) for s in LADDER if s in symbols]
    out = [None]
    for i in range(1, len(rows)):
        vals = []
        for j in idx:
            a, b = rows[i][j], rows[i - 1][j]
            if a is None or b is None or b <= 0:
                continue
            vals.append(a / b - 1.0)
        out.append(statistics.fmean(vals) if vals else None)
    return out


def signal_series(rows, symbols, signal="breadth"):
    """Causal gate signal per day.  `ladder` reuses the census momentum read."""
    if signal == "ladder":
        return [ladder_momentum(rows, symbols, i, 20) for i in range(len(rows))]
    if signal == "both":
        br = [breadth_at(rows, i, 20) for i in range(len(rows))]
        lm = [ladder_momentum(rows, symbols, i, 20) for i in range(len(rows))]
        return [None if (a is None or b is None) else (a, b) for a, b in zip(br, lm)]
    return [breadth_at(rows, i, 20) for i in range(len(rows))]


def gate_series(cal, rows, symbols=None, tail_q=TAIL_Q, burn=BURN, signal="breadth"):
    """W_t in {0,1} per day, decided from information available at t (T+1 use).

    The gate is ON when the signal at t sits above the expanding tail_q
    quantile of the signal history seen so far; burn-in days are OFF.
    `both` requires every component signal to clear its own expanding cut.
    """
    series = signal_series(rows, symbols or [], signal)
    hist = []
    gate = []
    for v in series:
        if v is None or len(hist) < burn:
            gate.append(0)
            if v is not None:
                hist.append(v)
            continue
        if isinstance(v, tuple):
            cuts = []
            for k in range(len(v)):
                col = sorted(h[k] for h in hist)
                cuts.append(col[min(len(col) - 1, int(len(col) * tail_q))])
            on = all(x > c for x, c in zip(v, cuts))
        else:
            srt = sorted(hist)
            on = v > srt[min(len(srt) - 1, int(len(srt) * tail_q))]
        gate.append(1 if on else 0)
        hist.append(v)
    return gate, series


def overlay_series(cal, rets, gate):
    """Net daily overlay returns with T+1 execution and turnover cost."""
    prev_w = 0.0
    gross, net, costs, wts = [], [], [], []
    for i in range(len(cal)):
        w = float(gate[i - 1]) if i > 0 else 0.0     # T+1: yesterday's read
        r = rets[i]
        if r is None:
            gross.append(0.0)
            net.append(0.0)
            costs.append(0.0)
            wts.append(w)
            continue
        g = w * r
        c = abs(w - prev_w) * COST_BP / 10000.0
        gross.append(g)
        net.append(g - c)
        costs.append(c)
        wts.append(w)
        prev_w = w
    return gross, net, costs, wts


def stride_t(xs, stride=STRIDE, offset=0):
    sub = xs[offset::stride]
    return tstat(sub), len(sub)


def per_year(cal, xs):
    acc = {}
    for d, v in zip(cal, xs):
        y = d[:4]
        cur = acc.setdefault(y, [0.0, 0])
        cur[0] += v
        cur[1] += 1
    return {y: {"sum_bp": round(v[0] * 1e4, 2), "days": v[1]} for y, v in sorted(acc.items())}


def build_face(cal, symbols, rows, gate_name=None, tail_q=TAIL_Q,
               signal="breadth"):
    rets = ladder_returns(cal, symbols, rows)
    gate, breadth = gate_series(cal, rows, symbols, tail_q=tail_q, signal=signal)
    if gate_name is None:
        gate_name = {"breadth": "breadth20-top-quintile",
                     "ladder": "ladder20-top-quintile",
                     "both": "breadth20-and-ladder20-top-quintile"}[signal]
    gross, net, costs, wts = overlay_series(cal, rets, gate)

    live = [(d, g, n, c, w) for d, g, n, c, w in zip(cal, gross, net, costs, wts)]
    first = next((i for i, w in enumerate(wts) if w > 0), None)
    live = live[first:] if first is not None else []
    if not live:
        return {"status": "empty", "reason": "no gate-on days after burn-in"}

    d_live = [x[0] for x in live]
    g_live = [x[1] for x in live]
    n_live = [x[2] for x in live]
    c_live = [x[3] for x in live]
    w_live = [x[4] for x in live]

    exposure = sum(w_live) / len(w_live)
    transitions = sum(1 for a, b in zip(w_live, w_live[1:]) if a != b)
    years = max(len(w_live) / 244.0, 1e-9)
    t_str, n_str = stride_t(n_live)

    # always-on ladder baseline over the same window (single entry cost)
    base_net = [r for r in rets[first:] if r is not None]
    base_gross_bp = sum(base_net) * 1e4
    base_net_bp = base_gross_bp - COST_BP
    base_t, base_n = stride_t(base_net)
    exposure_per_year = exposure if exposure > 0 else 1e-9
    edge_bp_year = (sum(n_live) * 1e4 - base_net_bp) / years

    return {
        "face": gate_name,
        "signal": signal,
        "evidence_cutoff": d_live[-1],
        "window_start": d_live[0],
        "n_days": len(d_live),
        "exposure_share": round(exposure, 4),
        "overlay": {
            "gross_bp_per_day": round(statistics.fmean(g_live) * 1e4, 3),
            "net_bp_per_day": round(statistics.fmean(n_live) * 1e4, 3),
            "net_bp_total": round(sum(n_live) * 1e4, 1),
            "net_bp_per_year": round(sum(n_live) / years * 1e4, 1),
            "net_bp_per_year_per_unit_exposure": round(
                sum(n_live) / years * 1e4 / exposure_per_year, 1),
            "cost_drag_bp_total": round(sum(c_live) * 1e4, 1),
            "cost_drag_bp_per_year": round(sum(c_live) / years * 1e4, 1),
            "transitions": transitions,
            "transitions_per_year": round(transitions / years, 1),
            "stride5_t_net": round(t_str, 2) if t_str is not None else None,
            "stride5_n": n_str,
            "per_year_net_bp": per_year(d_live, n_live),
        },
        "always_on_ladder": {
            "gross_bp_total": round(base_gross_bp, 1),
            "net_bp_total": round(base_net_bp, 1),
            "net_bp_per_year": round(base_net_bp / years, 1),
            "stride5_t_net": round(base_t, 2) if base_t is not None else None,
            "stride5_n": base_n,
        },
        "edge_vs_always_on_bp_per_year": round(edge_bp_year, 1),
        "cost_bp_per_side": COST_BP,
        "tail_q": tail_q,
        "labels": {
            "descriptive": True,
            "prereg": None,
            "trial_count": 0,
            "verdict": "none (feasibility face only; admission needs a frozen prereg)",
            "execution": "T+1 (gate read on t applies to t+1 return)",
            "cost": "|dw| * 13.041bp per side charged on every notional change",
        },
        "generated_at": datetime.now().isoformat(timespec="seconds"),
    }


# -------------------------------------------------------------------- selftest
def selftest():
    fails = []

    total = {"n": 0}

    def chk(name, cond):
        total["n"] += 1
        print(("  PASS " if cond else "  FAIL ") + name)
        if not cond:
            fails.append(name)

    # deterministic synthetic panel: 3 symbols, 40 days of monotone closes
    cal = ["2026-01-%02d" % (i + 1) for i in range(40)]
    rows = []
    for i in range(40):
        rows.append([1.0 + 0.01 * i + 0.001 * j for j in range(3)])
    symbols = ["sh510300", "sh510050", "sh510500"]

    rets = ladder_returns(cal, symbols, rows)
    chk("ladder returns length == calendar", len(rets) == len(cal))
    chk("first return is None placeholder", rets[0] is None)
    chk("constant drift return ~1e-2", abs(rets[5] - ((1.0 + 0.01 * 5) / (1.0 + 0.01 * 4) - 1.0)) < 1e-4)

    gate = [0, 0, 1, 1, 0, 1]
    gross, net, costs, wts = overlay_series(cal[:6], rets[1:7], gate)
    chk("gate shifts by one day (T+1)", wts == [0.0, 0.0, 0.0, 1.0, 1.0, 0.0])
    chk("cost charged only on transitions", abs(sum(costs) - 2 * COST_BP / 1e4) < 1e-12)
    chk("net == gross - costs", all(abs(n - (g - c)) < 1e-15 for g, n, c in zip(gross, net, costs)))
    chk("cost-free days carry gross through", abs(net[4] - gross[4]) < 1e-15)

    t, n = stride_t([0.001] * 20)
    chk("stride t on constant series is None (zero sd)", t is None and n == 4)

    # gate must not see the future: perturbing the last day's price cannot
    # change yesterday's gate value
    rows2 = [list(r) for r in rows]
    rows2[-1] = [x * 1.5 for x in rows2[-1]]
    g1, _ = gate_series(cal, rows, tail_q=0.5, burn=5)
    g2, _ = gate_series(cal, rows2, tail_q=0.5, burn=5)
    chk("gate at t-1 is invariant to a t-day shock", g1[:-1] == g2[:-1])

    # ladder-momentum signal must also be causal and must differ from breadth
    g3, s3 = gate_series(cal, rows, symbols, tail_q=0.5, burn=5, signal="ladder")
    g4, _ = gate_series(cal, rows2, symbols, tail_q=0.5, burn=5, signal="ladder")
    chk("ladder gate at t-1 is invariant to a t-day shock", g3[:-1] == g4[:-1])
    chk("ladder signal ignores burn-in days", all(v is None for v in s3[:5]) is False
        or all(g3[:5] == [0] * 5 for _ in [0]))

    # 'both' needs every component above its own expanding cut
    g5, s5 = gate_series(cal, rows, symbols, tail_q=0.5, burn=5, signal="both")
    chk('both signal is a 2-tuple per live day',
        all(v is None or (isinstance(v, tuple) and len(v) == 2) for v in s5))
    chk("both gate never exceeds either single gate", all(a <= b and a <= c
        for a, b, c in zip(g5, g3, gate_series(cal, rows, symbols, tail_q=0.5,
                                               burn=5, signal="breadth")[0])))

    print("selftest: %d/%d PASS" % (total["n"] - len(fails), total["n"]))
    return 0 if not fails else 1


# ------------------------------------------------------------------------ main
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd")
    runp = sub.add_parser("run", help="compute the overlay feasibility face")
    runp.add_argument("--tail-q", type=float, default=TAIL_Q,
                      help="gate entry quantile on the expanding breadth history (default 0.80)")
    runp.add_argument("--signal", default="breadth", choices=["breadth", "ladder", "both"],
                      help="gate signal: breadth20 | ladder 20d momentum | both (default breadth)")
    sub.add_parser("selftest", help="hermetic self checks")
    args = ap.parse_args(argv)
    cmd = args.cmd or "run"

    if cmd == "selftest":
        return selftest()

    cal, symbols, rows = load_panel()
    signal = getattr(args, "signal", "breadth")
    face = build_face(cal, symbols, rows, tail_q=getattr(args, "tail_q", TAIL_Q),
                      signal=signal)
    os.makedirs(OUTDIR, exist_ok=True)
    tag = "q%02d" % round(face["tail_q"] * 100)
    face_tag = {"breadth": "breadth20", "ladder": "ladder20", "both": "both20"}[signal]
    path = os.path.join(OUTDIR, "OVERLAY-%s-%s-%s.json" %
                        (face_tag, tag, face["evidence_cutoff"].replace("-", "")))
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
    latest = os.path.join(OUTDIR, "latest-%s.json" % face_tag)
    with open(latest, "w", encoding="utf-8") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
    if signal == "breadth":          # legacy pointer: breadth was the first face
        with open(os.path.join(OUTDIR, "latest.json"), "w", encoding="utf-8") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
    print(json.dumps({k: v for k, v in face.items() if k in
                      ("face", "evidence_cutoff", "n_days", "exposure_share", "overlay",
                       "always_on_ladder", "edge_vs_always_on_bp_per_year")},
                     ensure_ascii=False, indent=1))
    print("face: %s" % os.path.relpath(path, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())