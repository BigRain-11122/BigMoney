"""Is the fill itself the last lever? Slicing the rebalance over k consecutive opens (E27).

E25: the 1.14 pp/yr between the card's as-coded arm and its declared arm is information --
smoothing recovers +0.07 pp of it (signal +0.06 / cost +0.01). E26: the only information
channel that exists between the decision close and the fill open is the overnight gap,
worth +0.81 pp/yr on the full span but winning only 2 of 4 decision phases, and negative as a
ranking signal. Information and price are both exhausted, so what remains is the mechanic of
the fill: put the whole delta through ONE open print, or through k consecutive opens in equal
slices.

What slicing can and cannot buy is fixed by construction, not by argument: the slices sum to
the same absolute delta, so commission is identical to the single-open fill (asserted in
`audit_participation`, 1e-9), and the book ends on the same target weights. Only the price
path changes -- part of the position is paid at a later, different open, and the book carries
cash during the transition.

Frozen criterion (`research/CASE_PREREG_E27_OPEN_SLICING.md`, committed before the first run):
k is admissible iff it beats the k=1 control by >= 0.57 pp/yr on the full span, wins >= 3 of 4
decision phases, and is no deeper in drawdown than control - 2.0 pp.

Usage:
    python scripts/etf_book_open_slicing.py run
    python scripts/etf_book_open_slicing.py --check
    python scripts/etf_book_open_slicing.py --selftest
"""
from __future__ import annotations

import io
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import numpy as np
import pandas as pd

import etf_book_forward as F
import etf_equity_alpha as A
import etf_robust_pf as R
import etf_composite_pf as E
import etf_book_vol_window_phase as PH

OUT_JSON = os.path.join(ROOT, "results", "etf_book_open_slicing.json")
OUT_MD = os.path.join(ROOT, "research", "ETF_BOOK_OPEN_SLICING.md")
PRODUCTION_JSON = os.path.join(ROOT, "results", "etf_book_production", "latest.json")

# ---------------------------------------------------------------- frozen criteria
SLICE_MIN_PP = 0.57
DD_TOL_PP = 2.0
N_PHASES = 4
PHASE_SHARE_MIN = 0.75
IDENT_TOL_PP = 0.05
IDENT_TOL_SERIES = 1e-12
PARTICIPATION_TOL = 1e-9
OOS_FROM = "2023-12-31"

REBAL = F.CONFIG["rebal"]
N_HOLD = F.CONFIG["n_hold"]
COST = F.CONFIG["cost_per_side"]
VOL_TARGET = F.CONFIG["vol_target"]

SLICES = (1, 2, 3, 5)
ARMS = tuple("k%d" % k for k in SLICES)
CONTROL = "k1"

CRITERIA = {
    "slice_min_pp": SLICE_MIN_PP,
    "dd_tol_pp": DD_TOL_PP,
    "n_phases": N_PHASES,
    "phase_share_min": PHASE_SHARE_MIN,
    "identity_tol_pp": IDENT_TOL_PP,
    "identity_tol_series": IDENT_TOL_SERIES,
    "participation_tol": PARTICIPATION_TOL,
    "oos_from": OOS_FROM,
}


# ---------------------------------------------------------------- pricing
def sliced_equity(close, openp, amt, score, k, start, cost, vol_target=VOL_TARGET,
                  vol_window=60, vol_cap=1.0):
    """`k=1` is bit-identical to etf_robust_pf.open_to_open_equity (same loop, same sizing).

    For k>1 the delta decided at bar d is spread over the opens d .. d+k-1 in equal slices
    of the *original* delta; the target is reached exactly on the last slice.
    """
    if k < 1:
        raise ValueError("k must be >= 1")
    hist = close.notna().cumsum()
    elig = (amt >= E.MIN_AMT) & (hist >= E.MIN_HIST)
    score = score.where(elig)
    op = openp.reindex(columns=close.columns)
    dates = [d for d in op.index if d >= pd.Timestamp(start)]
    equity, held, daily, turns = 1.0, {}, [], []
    rets = op.pct_change()

    def book_vol(book, upto):
        if not book:
            return np.nan
        window = rets.loc[:upto].tail(vol_window)[list(book)]
        if window.shape[0] < 20:
            return np.nan
        w = np.array([book[kk] for kk in window.columns])
        cov = window.cov().to_numpy()
        return float(np.sqrt(w @ cov @ w) * np.sqrt(252))

    pending = None  # {"target": w, "remaining": n, "delta": {...}}
    decisions = 0
    for i in range(len(dates) - 1):
        d = dates[i]
        if i % REBAL == 0:
            s = score.loc[d].dropna()
            if len(s) >= N_HOLD:
                decisions += 1
                picks = list(s.nlargest(N_HOLD).index)
                w = {p: 1.0 / N_HOLD for p in picks}
                scale = 1.0
                if vol_target:
                    v = book_vol(w, d)
                    if np.isfinite(v) and v > 0:
                        scale = float(min(vol_cap, vol_target / v))
                w = {p: wt * scale for p, wt in w.items()}
                if pending is not None and pending["remaining"] > 0:
                    # k is shorter than the grid, so this cannot happen; never trade blind.
                    raise AssertionError("previous slice ladder unfinished at a new decision")
                delta = {n: w.get(n, 0.0) - held.get(n, 0.0) for n in set(w) | set(held)}
                if k == 1:
                    turn = sum(abs(x) for x in delta.values())
                    equity *= (1.0 - cost * turn)
                    turns.append(turn)
                    held = dict(w)
                else:
                    pending = {"target": dict(w), "remaining": k,
                               "step": {n: x / float(k) for n, x in delta.items()}}

        if pending is not None:
            # one equal slice of the ORIGINAL delta per open (not 1/remaining, which would
            # re-trade the whole delta on the last day)
            step = pending["step"]
            turn = sum(abs(x) for x in step.values())
            equity *= (1.0 - cost * turn)
            turns.append(turn)
            nxt_held = dict(held)
            for n, x in step.items():
                if x:
                    nxt_held[n] = nxt_held.get(n, 0.0) + x
            held = {n: v for n, v in nxt_held.items() if abs(v) > 1e-15}
            pending["remaining"] -= 1
            if pending["remaining"] == 0:
                held = dict(pending["target"])
                pending = None

        nxt = dates[i + 1]
        r = 0.0
        for p, wt in held.items():
            a, b = op.at[d, p], op.at[nxt, p]
            if np.isfinite(a) and np.isfinite(b) and a > 0:
                r += wt * (b / a - 1.0)
        equity *= (1.0 + r)
        daily.append((nxt, equity))
    ser = pd.Series(dict(daily)).sort_index()
    # turnover is reported PER DECISION (the sum over a slice ladder), so a k-slice schedule
    # is comparable with the single-open fill it is measured against.
    return ser, (float(sum(turns) / decisions) if decisions else 0.0)


def _stats(ser):
    full = A.stats2(ser, "full")
    oos = A.stats2(ser[ser.index > pd.Timestamp(OOS_FROM)], "oos") if len(ser) else {}
    return {
        "cagr": full.get("cagr"),
        "sharpe": full.get("sharpe"),
        "maxdd": full.get("maxdd"),
        "vol": full.get("vol"),
        "years": full.get("years"),
        "oos_cagr": oos.get("cagr"),
        "oos_sharpe": oos.get("sharpe"),
        "bars": int(len(ser)),
    }


def _row(phase, arm, k, ser, turn, cost):
    st = _stats(ser)
    row = {"phase": int(phase), "arm": arm, "k": int(k), "cost_per_side": cost,
           "turnover": round(turn, 4)}
    row.update({kk: (None if v is None else (round(v, 6) if isinstance(v, float) else v))
                for kk, v in st.items()})
    return row


# ---------------------------------------------------------------- mechanism audits
def audit_identity(close, openp, amt, score, start, cost):
    """A9: k=1 is the published engine, not a lookalike."""
    ser_k1, turn_k1 = sliced_equity(close, openp, amt, score, 1, start, cost)
    ser_ref, turn_ref = R.open_to_open_equity(close, openp, amt, score, REBAL, N_HOLD, cost,
                                             vol_target=VOL_TARGET, start=start)
    common = ser_k1.index.intersection(ser_ref.index)
    diff = float(np.max(np.abs(ser_k1.reindex(common).to_numpy()
                               - ser_ref.reindex(common).to_numpy()))) if len(common) else None
    return {"ok": bool(diff is not None and diff <= IDENT_TOL_SERIES
                       and abs(turn_k1 - turn_ref) <= 1e-9),
            "max_abs_equity_diff": diff,
            "turnover_k1": round(turn_k1, 6), "turnover_engine": round(float(turn_ref), 6),
            "bars": int(len(common)),
            "rule": "A wrapper that does not reproduce the engine at k=1 is a new engine, "
                    "and the comparison would be between two experiments."}


def audit_participation(close, openp, amt, score, start, cost, k):
    """A10: slicing changes the price path, not the position and not the commission.

    Injects a probe into the slice loop by replaying the same decisions and comparing the
    total turnover charged over k slices with the single-open turnover of the same grid.
    """
    if k == 1:
        return {"k": 1, "trivial": True, "ok": True}
    # the same decision grid, priced both ways
    ser1, _ = sliced_equity(close, openp, amt, score, 1, start, 0.0)
    serk, _ = sliced_equity(close, openp, amt, score, k, start, 0.0)
    # zero-cost runs must be identical only if the book is identical; they are not (cash
    # during the transition), so what is asserted is the turnover identity, measured on the
    # cost-paying runs.
    ser_c1, turn1 = sliced_equity(close, openp, amt, score, 1, start, cost)
    ser_ck, turnk = sliced_equity(close, openp, amt, score, k, start, cost)
    return {"k": int(k), "trivial": False,
            "ok": bool(abs(turn1 - turnk) <= PARTICIPATION_TOL),
            "turnover_single_open": round(turn1, 9),
            "turnover_sliced": round(turnk, 9),
            "bars_identical_path_free": int(len(ser1.index.intersection(serk.index))),
            "rule": "Equal slices sum to the same absolute delta, so k cannot buy anything "
                    "through commission -- only through the price path. A sliced arm that "
                    "also shrinks the book would be a different experiment (E197)."}


def decide(rows, criteria=CRITERIA):
    """Verdict from the published rows only -- re-derivable, never re-run."""
    full = {}
    for r in rows:
        full.setdefault(r["arm"], r)
    if CONTROL not in full:
        return {"state": "INCOMPLETE", "why": "no `%s` control arm" % CONTROL}
    d = full[CONTROL]
    if d.get("cagr") is None:
        return {"state": "INCOMPLETE", "why": "control arm did not price"}
    dd_floor = (d["maxdd"] or 0.0) - criteria["dd_tol_pp"] / 100.0

    phases = sorted({r["phase"] for r in rows})
    by_phase = {p: {r["arm"]: r for r in rows if r["phase"] == p} for p in phases}

    arms = []
    for name, r in full.items():
        if name == CONTROL or r.get("cagr") is None:
            continue
        gained_pp = 100.0 * (r["cagr"] - d["cagr"])
        full_ok = (gained_pp >= criteria["slice_min_pp"]
                   and (r.get("sharpe") or 0.0) >= (d.get("sharpe") or 0.0)
                   and (r.get("maxdd") or 0.0) >= dd_floor)
        wins = 0
        for p in phases:
            pr, pd_ = by_phase[p].get(name), by_phase[p].get(CONTROL)
            if pr and pd_ and pr.get("cagr") is not None and pd_.get("cagr") is not None:
                if pr["cagr"] > pd_["cagr"]:
                    wins += 1
        share = (float(wins) / len(phases)) if phases else 0.0
        arms.append({
            "arm": name,
            "k": r.get("k"),
            "gained_pp": round(gained_pp, 2),
            "full_span_tests_pass": bool(full_ok),
            "phase_wins": wins,
            "phase_share": round(share, 3),
            "phase_share_pass": bool(share >= criteria["phase_share_min"]),
            "admissible": bool(full_ok and share >= criteria["phase_share_min"]),
        })
    if not arms:
        return {"state": "INCOMPLETE", "why": "no sliced arm priced"}

    win = [a for a in arms if a["admissible"]]
    best = max(arms, key=lambda a: a["gained_pp"])
    line_ok = best["gained_pp"] >= criteria["slice_min_pp"]
    if win:
        state = "ADOPT_SLICED"
        chosen = max(win, key=lambda a: a["gained_pp"])
    elif line_ok and (best["full_span_tests_pass"] or best["phase_share_pass"]):
        state = "MIXED_ACROSS_PHASES"
        chosen = None
    else:
        state = "NO_SLICING_EDGE"
        chosen = None
    return {
        "state": state,
        "state_rule_detail": ("MIXED_ACROSS_PHASES requires the return line first; a gain "
                              "below slice_min_pp is NO_SLICING_EDGE however consistently it "
                              "wins"),
        "control_cagr": round(d["cagr"], 4),
        "control_sharpe": d.get("sharpe"),
        "control_maxdd": d.get("maxdd"),
        "dd_floor": round(dd_floor, 4),
        "best_arm": best["arm"],
        "best_gained_pp": best["gained_pp"],
        "admissible_arms": [a["arm"] for a in win],
        "chosen_arm": chosen["arm"] if chosen else None,
        "recommended_fill": ("split over k=%d opens" % chosen["k"]) if chosen else
                            "single open (unchanged)",
        "arms": arms,
        "phases": len(phases),
    }


# ---------------------------------------------------------------- run
def run():
    t0 = time.time()
    close, openp, amt, feats, score, _cls, _flip = F.build_inputs()
    # The desk's real ladder starts from the DECLARED arm: decide on bar d's close, fill no
    # earlier than bar d+1's open. Slicing is measured against that arm, never against the
    # as-coded (look-ahead) one, which the desk cannot trade.
    declared = score.shift(1)

    trade_dates = [d for d in close.index if d >= pd.Timestamp(R.START)]
    starts = PH.phase_starts(trade_dates)

    rows = []
    for i, st in enumerate(starts):
        for k in SLICES:
            ser, turn = sliced_equity(close, openp, amt, declared, k, st, COST)
            rows.append(_row(i, "k%d" % k, k, ser, turn, COST))

    sample_start = starts[0]
    audits = {
        "A9_engine_identity": audit_identity(close, openp, amt, declared, sample_start, COST),
        "A10_participation_not_rescaled": [audit_participation(close, openp, amt, declared,
                                                               sample_start, COST, k)
                                           for k in SLICES],
    }
    # context, never an arm: the look-ahead fill the desk cannot trade, for scale only
    ref_ser, _ = sliced_equity(close, openp, amt, score, 1, sample_start, COST)
    reference = {"as_coded_k1_cagr": _stats(ref_ser).get("cagr"),
                 "note": "single open, as coded (fill at bar d's open) -- the arm the card "
                         "calls untradeable; printed for scale only"}

    try:
        with io.open(PRODUCTION_JSON, encoding="utf-8") as fh:
            prod = json.load(fh)
        eb = prod.get("execution_basis") or {}
        pub = {"declared_cagr": eb.get("declared_cagr"),
               "as_coded_cagr": eb.get("as_coded_cagr"),
               "source": "results/etf_book_production/latest.json::execution_basis"}
    except Exception as exc:
        pub = {"declared_cagr": None, "as_coded_cagr": None,
               "source": "unreadable: %s" % exc}

    controls = []
    got = next((r["cagr"] for r in rows if r["phase"] == 0 and r["arm"] == CONTROL), None)
    want = pub.get("declared_cagr")
    gap_pp = None if (got is None or want is None) else 100.0 * (got - want)
    controls.append({"arm": CONTROL, "got_cagr": got, "published_cagr": want,
                     "gap_pp": None if gap_pp is None else round(gap_pp, 3),
                     "ok": bool(gap_pp is not None and abs(gap_pp) <= IDENT_TOL_PP)})

    payload = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "script": os.path.relpath(os.path.abspath(__file__), ROOT),
        "evidence_cutoff": str(pd.Timestamp(close.index[-1]).date()),
        "prereg": "research/CASE_PREREG_E27_OPEN_SLICING.md",
        "criteria": CRITERIA,
        "config": {"n_hold": N_HOLD, "rebal": REBAL, "cost_per_side": COST,
                   "vol_target": VOL_TARGET, "slices": list(SLICES),
                   "phases": [str(p.date()) for p in starts]},
        "published": pub,
        "controls": controls,
        "audits": audits,
        "reference": reference,
        "rows": rows,
        "verdict": decide(rows),
        "elapsed_sec": round(time.time() - t0, 1),
    }
    _write_json(payload)
    _write_md(payload)
    _print_summary(payload)
    return payload


def _write_json(payload):
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with io.open(OUT_JSON, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")


def _write_md(payload):
    v, cfg = payload["verdict"], payload["config"]
    line_pp = payload["criteria"]["slice_min_pp"]
    phase_need = int(payload["criteria"]["phase_share_min"] * payload["criteria"]["n_phases"])
    lines = [
        "# E27 — is the fill the last lever? (slicing the rebalance over k opens)",
        "",
        "Verdict **%s** · cutoff %s · control `%s` %s · evidence `%s`"
        % (v.get("state"), payload["evidence_cutoff"], CONTROL,
           _pct(v.get("control_cagr")), payload["script"]),
        "",
        "Frozen criterion: >= %.2f pp/yr on the full span · >= %d/%d decision phases"
        % (line_pp, phase_need, payload["criteria"]["n_phases"]),
        "",
        "| arm | k | CAGR | Sharpe | maxDD | vs control (pp/yr) | phases won | admissible |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in sorted(payload["rows"], key=lambda x: (x["phase"], x["k"])):
        a = next((x for x in v.get("arms", []) if x["arm"] == r["arm"]), None)
        lines.append("| %s | %d | %s | %s | %s | %s | %s | %s |" % (
            r["arm"], r["k"], _pct(r["cagr"]), _num(r["sharpe"]), _pct(r["maxdd"]),
            _num(a["gained_pp"]) if a else "—",
            ("%d/%d" % (a["phase_wins"], v.get("phases", 0))) if a else "—",
            ("yes" if a and a["admissible"] else "no") if a else "—"))
    idt = payload["audits"]["A9_engine_identity"]
    lines += [
        "",
        "## Mechanism audits",
        "",
        "- **A9 engine identity**: k=1 reproduces `etf_robust_pf.open_to_open_equity` to "
        "%.1e over %d bars (turnover %.6f vs %.6f) — %s"
        % (idt["max_abs_equity_diff"] or 0.0, idt["bars"], idt["turnover_k1"],
           idt["turnover_engine"], "OK" if idt["ok"] else "FAIL"),
    ]
    for a in payload["audits"]["A10_participation_not_rescaled"]:
        if a.get("trivial"):
            lines.append("- **A10 participation**: k=1 is the trivial case.")
        else:
            lines.append("- **A10 participation** k=%d: turnover %.6f vs single-open %.6f — %s"
                         % (a["k"], a["turnover_sliced"], a["turnover_single_open"],
                            "identical (commission cannot be what moves)" if a["ok"]
                            else "DIFFERS"))
    lines += [
        "",
        "## What was tested and what was not",
        "",
        "- Same book, same 8%% vol-target sizing (de-lever only), same 10 bp per side, same",
        "  four decision phases as E26. Only the execution schedule differs.",
        "- Equal slices sum to the same absolute delta, so slicing **cannot** buy anything",
        "  through commission; it can only change the price path (and hold cash while the",
        "  transition is in flight).",
        "- No market-impact model: the desk is small enough that the published per-side cost",
        "  is the whole story, and this face inherits that assumption rather than testing it.",
        "- Research face: it never rewrites the production config. An ADOPT verdict licenses",
        "  the next frozen change window, not this run.",
        "",
        "_generated by %s at %s_" % (payload["script"], payload["ts"]),
        "",
    ]
    with io.open(OUT_MD, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines))


def _pct(x):
    return "—" if x is None else "%.2f%%" % (100.0 * x)


def _num(x):
    return "—" if x is None else "%.2f" % x


def _print_summary(p):
    v = p["verdict"]
    print("verdict  %s" % v.get("state"))
    print("control  %s %s  Sharpe %s  maxDD %s"
          % (CONTROL, _pct(v.get("control_cagr")), _num(v.get("control_sharpe")),
             _pct(v.get("control_maxdd"))))
    for a in v.get("arms", []):
        print("  %-3s %+.2f pp/yr  phases %d/%d  admissible %s"
              % (a["arm"], a["gained_pp"], a["phase_wins"], v.get("phases", 0),
                 a["admissible"]))
    ref = (p.get("reference") or {}).get("as_coded_k1_cagr")
    if ref is not None:
        print("scale    as-coded single open (untradeable) %.2f%%" % (100.0 * ref))
    print("fill     %s" % v.get("recommended_fill"))
    print("cutoff   %s   %.1fs" % (p["evidence_cutoff"], p["elapsed_sec"]))


# ---------------------------------------------------------------- check / selftest
def read_published(path=None):
    with io.open(path or OUT_JSON, encoding="utf-8") as fh:
        return json.load(fh)


def check(path=None):
    p = read_published(path)
    fresh = decide(p["rows"], p["criteria"])
    old = p.get("verdict") or {}
    idt = (p.get("audits") or {}).get("A9_engine_identity") or {}
    ok = (fresh.get("state") == old.get("state")
          and fresh.get("best_arm") == old.get("best_arm")
          and bool(idt.get("ok")))
    print("%s %s (re-derived from published rows; identity leg %s)"
          % ("OK" if ok else "DRIFT", fresh.get("state"),
             "ok" if idt.get("ok") else "FAILED"))
    return 0 if ok else 2


def _fixture(n_names=14, n_bars=900, seed=27, rebal=20):
    rs = np.random.default_rng(seed)
    dates = pd.bdate_range("2019-01-02", periods=n_bars)
    names = ["N%02d" % i for i in range(n_names)]
    drift = rs.normal(0.0005, 0.0002, n_names)
    ret = rs.normal(0.0, 0.013, (n_bars, n_names)) + drift
    close = pd.DataFrame(100.0 * np.cumprod(1.0 + ret, axis=0), index=dates, columns=names)
    openp = close.shift(1) * (1.0 + rs.normal(0.0, 0.004, (n_bars, n_names)))
    openp.iloc[0] = close.iloc[0]
    amt = pd.DataFrame(1e9, index=dates, columns=names)
    score = pd.DataFrame(rs.normal(0, 1, (n_bars, n_names)), index=dates, columns=names)
    return close, openp, amt, score


def selftest():
    legs = []
    close, openp, amt, score = _fixture()
    start = close.index[0]

    # L1 identity: k=1 is the engine
    a = audit_identity(close, openp, amt, score, start, 0.001)
    legs.append(("L1 k=1 reproduces the engine bit for bit", a["ok"]))

    # L2 slicing does not change the commission
    parts = [audit_participation(close, openp, amt, score, start, 0.001, k) for k in (2, 3, 5)]
    legs.append(("L2 k>1 pays exactly the single-open turnover", all(x["ok"] for x in parts)))

    # L3 the two paths are not the same series (otherwise the experiment is empty)
    s1, _ = sliced_equity(close, openp, amt, score, 1, start, 0.001)
    s3, _ = sliced_equity(close, openp, amt, score, 3, start, 0.001)
    d = float(np.max(np.abs(s1.to_numpy() - s3.to_numpy())))
    legs.append(("L3 the sliced arm actually prices a different path", d > 1e-9))

    # L4 a synthetic arm that beats the control by 1 pp wins the verdict
    rows = [{"phase": p, "arm": CONTROL, "k": 1, "cagr": 0.080, "sharpe": 0.9,
             "maxdd": -0.12} for p in range(4)]
    rows += [{"phase": p, "arm": "k2", "k": 2, "cagr": 0.090, "sharpe": 0.95,
              "maxdd": -0.125} for p in range(4)]
    legs.append(("L4 an arm clearing the line in every phase is ADOPT_SLICED",
                 decide(rows)["state"] == "ADOPT_SLICED"))

    # L5 a gain below the line is NO_SLICING_EDGE however consistent
    rows = [dict(r) for r in rows]
    for r in rows:
        if r["arm"] == "k2":
            r["cagr"] = 0.084
    legs.append(("L5 a sub-line gain is NO_SLICING_EDGE even at 4/4",
                 decide(rows)["state"] == "NO_SLICING_EDGE"))

    # L6 clearing the line in only half the phases is MIXED, not adoption
    rows = [{"phase": p, "arm": CONTROL, "k": 1, "cagr": 0.080, "sharpe": 0.9,
             "maxdd": -0.12} for p in range(4)]
    for p in range(4):
        rows.append({"phase": p, "arm": "k2", "k": 2,
                     "cagr": 0.095 if p < 2 else 0.070, "sharpe": 0.95, "maxdd": -0.125})
    v = decide(rows)
    legs.append(("L6 winning 2/4 phases is MIXED_ACROSS_PHASES",
                 v["state"] == "MIXED_ACROSS_PHASES"))

    # L7 a deeper drawdown fails the full-span test
    rows = [{"phase": p, "arm": CONTROL, "k": 1, "cagr": 0.080, "sharpe": 0.9,
             "maxdd": -0.12} for p in range(4)]
    rows += [{"phase": p, "arm": "k2", "k": 2, "cagr": 0.095, "sharpe": 0.95,
              "maxdd": -0.20} for p in range(4)]
    legs.append(("L7 a 8 pp deeper drawdown is not admissible",
                 decide(rows)["state"] == "MIXED_ACROSS_PHASES"))

    # L8 an unreadable control is not a verdict
    legs.append(("L8 no control arm is INCOMPLETE not NO_SLICING_EDGE",
                 decide([{"phase": 0, "arm": "k2", "k": 2, "cagr": 0.09}])["state"]
                 == "INCOMPLETE"))

    # L9 the published face is re-derivable
    if os.path.exists(OUT_JSON):
        p = read_published()
        fresh = decide(p["rows"], p["criteria"])
        legs.append(("L9 published verdict is re-derivable from its rows",
                     fresh.get("state") == (p.get("verdict") or {}).get("state")))
    else:
        legs.append(("L9 published verdict is re-derivable from its rows", True,
                     "skipped: no published face yet"))

    bad = [x for x in legs if not x[1]]
    for name, ok in [(x[0], x[1]) for x in legs]:
        print("%s %s" % ("PASS" if ok else "FAIL", name))
    print("%d/%d" % (len(legs) - len(bad), len(legs)))
    return 0 if not bad else 1


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "run":
        run()
        return 0
    if cmd == "--check" or cmd == "check":
        return check()
    if cmd == "--selftest" or cmd == "selftest":
        return selftest()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))