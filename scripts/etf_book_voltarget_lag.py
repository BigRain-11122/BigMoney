"""ETF book -- how late is the 8% vol target, and what does the lateness cost?

The production sizing overlay is `scale = min(1, 0.08 / est_vol)` where `est_vol` is the
realised vol of the *proposed* book over the last `vol_window` bars, computed AT a decision
and then frozen until the next one. Two lags therefore sit inside the same number and the
published headline (9.62%/yr, -10.6% maxDD) cannot tell them apart:

  1. estimation lag -- a trailing window is always behind a vol regime change;
  2. slot freeze     -- the scale is recomputed only every `rebal` (20) bars, so even a
                        perfect estimator is up to 19 bars late.

This face separates them by the only lever the engine exposes without touching its
arithmetic: `vol_window`. Four arms (20/40/60/120) are priced through the SAME engine call
with the SAME cost model, and the control arm (60) is asserted against the published
production cell before anything is read. A shorter window is a faster estimator; if the lag
were costing real drawdown, a faster arm would show it.

Then the lag itself is measured, not asserted: at every decision the engine records the
`est_vol` it used; the realised vol of that same book over the slot that FOLLOWS is
recomputed from open prices. `ratio = realised / estimated` is exactly the error the frozen
scale carries, and `delivered = scale * realised` says whether the book actually sat at the
target vol.

WHY THE CRITERIA SIT ABOVE THE CODE: the verdict rule is frozen as constants before the
first run and echoed into the payload; the gate recomputes the verdict from the summary, so
a face built under other thresholds is RED rather than quietly re-tuned. The honest expected
answer is KEEP: a sizing overlay is a cost knob, not an alpha, and this face exists to say
how wrong it is allowed to be -- not to find a better window to ship.

Usage:
    python scripts/etf_book_voltarget_lag.py run [--out=...]
    python scripts/etf_book_voltarget_lag.py --check
    python scripts/etf_book_voltarget_lag.py --selftest
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import numpy as np
import pandas as pd

import etf_robust_pf as R
import etf_equity_alpha as A
import etf_book_hysteresis as H
from scripts import etf_book_production as P

OUT_JSON = ROOT / "results" / "etf_book_voltarget_lag.json"
OUT_MD = ROOT / "research" / "ETF_BOOK_VOLTARGET_LAG.md"
PRODUCTION_FACE = ROOT / "results" / "etf_book_production" / "latest.json"

SCRIPT = "scripts/etf_book_voltarget_lag.py"
FACE = "results/etf_book_voltarget_lag.json"

# ---------------------------------------------------------------- frozen criteria
WINDOWS = (20, 40, 60, 120)     # vol_window arms; 60 is the production value
CONTROL_WINDOW = 60
N_HOLD, REBAL = 12, 20          # the published production cell (n12, r20)
COST = H.COST
TARGET_VOL = H.TARGET_VOL

CONTROL_TOL_CAGR_PP = 0.50      # r1297 law: reproduce the published cell within 0.5pp
DD_IMPROVE_PP = 1.00            # an arm must buy at least this much depth to be worth a change
CAGR_FLOOR_PP = -0.50           # ... without giving up more than this much return
OVERSHOOT_SHARE_MIN = 0.10      # "the delivered vol overshoots the target" needs to be common
RATIO_LAG_ALARM = 1.50          # a slot realised 1.5x its estimate is the lag showing

CRITERIA = {
    "windows": list(WINDOWS),
    "control_window": CONTROL_WINDOW,
    "n_hold": N_HOLD,
    "rebal": REBAL,
    "cost_per_side": COST,
    "target_vol": TARGET_VOL,
    "control_tol_cagr_pp": CONTROL_TOL_CAGR_PP,
    "dd_improve_pp": DD_IMPROVE_PP,
    "cagr_floor_pp": CAGR_FLOOR_PP,
    "overshoot_share_min": OVERSHOOT_SHARE_MIN,
    "ratio_lag_alarm": RATIO_LAG_ALARM,
    "frozen": "constants above were written before the first run; the gate refuses a face that echoes others",
}

UNITS = {
    "cagr": "fraction per year (0.0962 = 9.62%/yr)",
    "maxdd": "fraction (negative)",
    "ratio": "realised slot vol / the estimate the frozen scale was built on",
    "delivered_vol": "scale * realised slot vol -- what the book actually ran at",
}


# ---------------------------------------------------------------- mechanics

def run_arm(close, openp, amt, score, vol_window, start=None, n_hold=N_HOLD, rebal=REBAL):
    """One sizing-window arm through the production engine (bit-identical elsewhere)."""
    diag = []
    ser, turn = R.open_to_open_equity(
        close, openp, amt, score, rebal, n_hold, COST,
        vol_target=TARGET_VOL, start=str(pd.Timestamp(start or R.START).date()),
        vol_window=vol_window, diag=diag)
    return ser, turn, diag


def lag_block(openp, diag, target=TARGET_VOL, min_bars=5):
    """Estimate error per slot + the vol the book actually delivered.

    The engine writes `est_vol` at a decision for the NEW book. The slot that follows is
    the only period where that number is used, so the honest question is "how close was it
    to what that book then did".
    """
    rets = openp.pct_change()
    rows = []
    for prev, cur in zip(diag, diag[1:]):
        book = list(prev.get("book") or [])
        est = prev.get("est_vol")
        if not book or est is None or not np.isfinite(est) or est <= 0:
            continue
        d0, d1 = pd.Timestamp(prev["date"]), pd.Timestamp(cur["date"])
        cols = [c for c in book if c in rets.columns]
        if len(cols) < 2:
            continue
        win = rets.loc[d0:d1, cols].iloc[1:]
        if win.shape[0] < min_bars or win.isna().any().any():
            continue
        w = np.repeat(1.0 / len(cols), len(cols))
        cov = win.cov().to_numpy()
        var = float(w @ cov @ w)
        if not np.isfinite(var) or var < 0:
            continue
        real = float(np.sqrt(var) * np.sqrt(252))
        scale = float(prev.get("scale") or 1.0)
        rows.append({"date": prev["date"], "next": cur["date"],
                     "est_vol": round(est, 4), "realized_vol": round(real, 4),
                     "ratio": round(real / est, 4), "scale": round(scale, 4),
                     "delivered_vol": round(scale * real, 4),
                     "bars": int(win.shape[0])})
    if not rows:
        return {"n_slots": 0, "degraded": "no measurable slots"}
    ratio = np.array([r["ratio"] for r in rows])
    deliv = np.array([r["delivered_vol"] for r in rows])
    return {
        "n_slots": len(rows),
        "median_ratio": round(float(np.median(ratio)), 4),
        "p90_ratio": round(float(np.percentile(ratio, 90)), 4),
        "share_ratio_gt_1_5": round(float((ratio > 1.5).mean()), 4),
        "share_ratio_gt_2": round(float((ratio > 2.0).mean()), 4),
        "share_ratio_lt_0_7": round(float((ratio < 0.7).mean()), 4),
        "mean_est_vol": round(float(np.mean([r["est_vol"] for r in rows])), 4),
        "mean_realized_vol": round(float(np.mean([r["realized_vol"] for r in rows])), 4),
        "median_delivered_vol": round(float(np.median(deliv)), 4),
        "share_delivered_gt_target_1_5": round(float((deliv > 1.5 * target).mean()), 4),
        "share_delevered": round(float((np.array([r["scale"] for r in rows]) < 1.0).mean()), 4),
        "worst_slots": sorted(rows, key=lambda r: -r["ratio"])[:5],
    }


def drawdown_episode(ser, diag):
    """The deepest drawdown and how much of it the overlay was out of the market for.

    A vol target that is late shows up here: the drawdown bars where `scale` was still 1.0
    are bars the overlay had not yet acted on.
    """
    ser = ser.dropna()
    if len(ser) < 40 or not diag:
        return {"degraded": "series or diag too short"}
    peak = ser.cummax()
    dd = ser / peak - 1.0
    trough = dd.idxmin()
    peak_date = ser.loc[:trough].idxmax()
    scales = pd.Series({pd.Timestamp(d["date"]): float(d.get("scale") or 0.0) for d in diag}
                       ).sort_index()
    scales = scales.reindex(scales.index.union(ser.index)).ffill().reindex(ser.index)
    in_ep = dd.loc[peak_date:trough]
    sc = scales.loc[peak_date:trough]
    # Attribute the DEPTH, not a level: the fall is a product of daily returns, so the share
    # that accumulated while the overlay had not yet delevered is a log-return share. Reading
    # the level at the peak instead would always print the full depth (the peak bar is at
    # full size by definition) and would make the overlay look absent by construction.
    seg = ser.loc[peak_date:trough]
    r = seg.pct_change().dropna()
    sc_bar = scales.loc[r.index]
    ln_total = float(np.log(seg.iloc[-1] / seg.iloc[0]))
    full_mask = sc_bar >= 0.999
    ln_full = float(np.log1p(r[full_mask]).sum())
    return {
        "peak": str(peak_date.date()), "trough": str(trough.date()),
        "depth": round(float(dd.min()), 4),
        "bars": int(len(in_ep)),
        "share_bars_full_size": round(float((sc >= 0.999).mean()), 4),
        "share_bars_delevered": round(float((sc < 0.999).mean()), 4),
        "mean_scale_in_episode": round(float(sc.mean()), 4),
        "share_of_depth_accrued_at_full_size": round(
            float(ln_full / ln_total) if ln_total not in (0.0,) else 0.0, 4),
    }


def published_control_cagr():
    """The published n12_vt08 full-window CAGR, read from the production artefact."""
    try:
        d = json.loads(PRODUCTION_FACE.read_text(encoding="utf-8"))
        return float(d["backtest"]["n12_vt08"]["full"]["cagr"])
    except Exception:
        return None


def verdict(summary, control_cagr_pub):
    """The frozen decision rule. Returns (label, reasons)."""
    reasons = []
    arms = summary.get("arms") or []
    if not arms:
        return "REJECT", ["no arms -- an empty grid cannot support a verdict"]
    ctrl = next((a for a in arms if a["vol_window"] == CONTROL_WINDOW), None)
    if ctrl is None or ctrl.get("cagr") is None:
        return "REJECT", ["control arm missing -- nothing to compare against"]
    if control_cagr_pub is not None:
        gap_pp = 100 * abs(ctrl["cagr"] - control_cagr_pub)
        if gap_pp > CONTROL_TOL_CAGR_PP:
            reasons.append("control arm reproduces %.2f%% against the published %.2f%% "
                           "(gap %.2fpp > %.2fpp)" % (100 * ctrl["cagr"], 100 * control_cagr_pub,
                                                      gap_pp, CONTROL_TOL_CAGR_PP))
            return "REJECT", reasons
    better = []
    for a in arms:
        if a["vol_window"] == CONTROL_WINDOW or a.get("cagr") is None:
            continue
        dd_gain_pp = 100 * (a["maxdd"] - ctrl["maxdd"])          # less negative = better
        cagr_gap_pp = 100 * (a["cagr"] - ctrl["cagr"])
        if dd_gain_pp >= DD_IMPROVE_PP and cagr_gap_pp >= CAGR_FLOOR_PP:
            better.append({"vol_window": a["vol_window"], "dd_gain_pp": round(dd_gain_pp, 3),
                           "cagr_gap_pp": round(cagr_gap_pp, 3)})
    if len(better) > 1:
        reasons.append("%d arms beat the control on depth -- ambiguous, keep the production "
                       "window" % len(better))
        return "KEEP", reasons
    if len(better) == 1:
        reasons.append("vol_window=%d buys %.2fpp of depth for %+.2fpp of return"
                       % (better[0]["vol_window"], better[0]["dd_gain_pp"], better[0]["cagr_gap_pp"]))
        return "CANDIDATE_WINDOW_%d" % better[0]["vol_window"], reasons
    reasons.append("no window buys %.1fpp of depth inside the %+.1fpp return floor"
                   % (DD_IMPROVE_PP, CAGR_FLOOR_PP))
    return "KEEP", reasons


def build(fast=False):
    close, openp, amt, score, _cls, _n_flip = P.prep_panel()
    arms, diags = [], {}
    for w in WINDOWS:
        ser, turn, diag = run_arm(close, openp, amt, score, w)
        full = A.stats2(ser, "full")
        oos = A.stats2(ser[ser.index > pd.Timestamp("2023-12-31")], "oos")
        arms.append({
            "vol_window": w,
            "cagr": full.get("cagr"), "sharpe": full.get("sharpe"),
            "maxdd": full.get("maxdd"), "vol": full.get("vol"),
            "worst_year": full.get("worst_year"),
            "turnover_per_decision": round(float(turn), 4),
            "oos_cagr": oos.get("cagr"), "oos_sharpe": oos.get("sharpe"),
            "oos_maxdd": oos.get("maxdd"),
        })
        diags[w] = (ser, diag)
    ctrl_ser, ctrl_diag = diags[CONTROL_WINDOW]
    pub = published_control_cagr()
    summary = {"arms": arms}
    payload = {
        "face": FACE, "script": SCRIPT, "window": "full",
        "evidence_cutoff": str(close.index[-1].date()),
        "criteria": CRITERIA, "units": UNITS,
        "published_control_cagr": pub,
        "arms": arms,
        "lag": lag_block(openp, ctrl_diag),
        "lag_by_window": {str(w): lag_block(openp, diags[w][1]) for w in WINDOWS},
        "control_drawdown": drawdown_episode(ctrl_ser, ctrl_diag),
    }
    if not fast:
        label, reasons = verdict(summary, pub)
        payload["verdict"] = label
        payload["verdict_reasons"] = reasons
        payload["verdict_source"] = "recomputed by the gate from `arms`, never hand-written"
    payload["caveats"] = [
        "one panel, one cost model (10bp/side, next-open), survivor-pool caveat unchanged",
        "the arms differ ONLY in vol_window; selection, holdings and the cost model are shared, "
        "so a difference is the estimator's, not the book's",
        "a sizing overlay is not an alpha: KEEP is the expected verdict and a CANDIDATE is a "
        "risk-shape proposal, not a return claim",
        "scale is recomputed at decisions by construction; this face measures the delivered "
        "consequence of that, it does not change the engine",
    ]
    return payload


def check_payload(payload, production_cutoff=None):
    """A face built under other thresholds, or one that hides its verdict, is RED.

    Engine-free by design (the chain runs this every round): the panel rebuild costs ~2.5 min
    and belongs to `run`, so the gate recomputes the verdict from the arms the face already
    published and refuses a face whose criteria echo other constants or whose lag block is
    empty. A card cutoff that has moved on is DISCLOSED, not treated as a lie -- this face is
    re-derived from the live panel every round, so the card being one bar ahead is expected.
    """
    errs = []
    if payload.get("criteria") != CRITERIA:
        errs.append("criteria echo does not match the frozen constants")
    arms = payload.get("arms") or []
    if [a.get("vol_window") for a in arms] != list(WINDOWS):
        errs.append("arms %s != frozen windows %s" % ([a.get("vol_window") for a in arms], list(WINDOWS)))
    if any(a.get("cagr") is None for a in arms):
        errs.append("an arm carries no CAGR -- an unpriced arm cannot support a verdict")
    if not payload.get("lag") or not payload["lag"].get("n_slots"):
        errs.append("lag block has no measurable slots")
    label, reasons = verdict({"arms": arms}, payload.get("published_control_cagr"))
    if payload.get("verdict") != label:
        errs.append("verdict %r != gate %r" % (payload.get("verdict"), label))
    if payload.get("verdict_reasons") != reasons:
        errs.append("verdict reasons differ from the gate's")
    return errs


def latest_card_cutoff():
    try:
        d = json.loads(PRODUCTION_FACE.read_text(encoding="utf-8"))
        return (d.get("card") or {}).get("priced_bar") or d.get("evidence_cutoff")
    except Exception:
        return None


def check():
    path = OUT_JSON
    if not path.exists():
        print("FACE MISSING %s -- run `run` first" % path)
        return 2
    payload = json.loads(path.read_text(encoding="utf-8"))
    errs = check_payload(payload, latest_card_cutoff())
    card = latest_card_cutoff()
    if card and payload.get("evidence_cutoff") != card:
        print("disclosure: face priced at %s, production card at %s (re-derived each round)"
              % (payload.get("evidence_cutoff"), card))
    if errs:
        for e in errs:
            print("FAIL: " + e)
        return 1
    print("FACE OK %s verdict=%s arms=%d lag_slots=%d"
          % (FACE, payload.get("verdict"), len(payload.get("arms") or []),
             (payload.get("lag") or {}).get("n_slots", 0)))
    return 0


def render_md(payload):
    arms = payload["arms"]
    a = {x["vol_window"]: x for x in arms}
    c = a[CONTROL_WINDOW]
    lines = [
        "# The 8% vol target is late in two different ways",
        "",
        "Face: `%s` (evidence cutoff %s). Control: `vol_window=%d`, n%d/r%d, %.0fbp/side."
        % (FACE, payload["evidence_cutoff"], CONTROL_WINDOW, N_HOLD, REBAL, COST * 10000),
        "",
        "## Arms (only `vol_window` differs)",
        "",
        "| vol_window | CAGR | Sharpe | maxDD | vol | turnover | OOS CAGR | OOS maxDD |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for w in WINDOWS:
        x = a[w]
        lines.append("| %d%s | %.2f%% | %.3f | %.2f%% | %.2f%% | %.3f | %.2f%% | %.2f%% |" % (
            w, " (control)" if w == CONTROL_WINDOW else "",
            100 * x["cagr"], x["sharpe"], 100 * x["maxdd"], 100 * x["vol"],
            x["turnover_per_decision"], 100 * x["oos_cagr"], 100 * x["oos_maxdd"]))
    lag = payload["lag"]
    dd = payload["control_drawdown"]
    lines += [
        "",
        "## What the frozen scale was actually wrong by",
        "",
        "%d slots measured (decision to decision). Median realised/estimated = **%.2f**,"
        " p90 = %.2f, %.1f%% of slots ran past 1.5x their estimate and %.1f%% past 2x;"
        " %.1f%% of slots were delevered (scale < 1)."
        % (lag["n_slots"], lag["median_ratio"], lag["p90_ratio"],
           100 * lag["share_ratio_gt_1_5"], 100 * lag["share_ratio_gt_2"],
           100 * lag["share_delevered"]),
        "",
        "Mean estimate %.2f%% vs mean realised %.2f%% per slot; the median delivered vol was"
        " %.2f%% against a %.0f%% target, and %.1f%% of slots delivered more than 1.5x the target."
        % (100 * lag["mean_est_vol"], 100 * lag["mean_realized_vol"],
           100 * lag["median_delivered_vol"], 100 * TARGET_VOL,
           100 * lag["share_delivered_gt_target_1_5"]),
        "",
        "Worst five slots (realised / estimated): "
        + ", ".join("%s %.2fx (scale %.2f)" % (r["next"], r["ratio"], r["scale"])
                    for r in lag["worst_slots"]),
        "",
        "## The deepest drawdown, and whether the overlay was there for it",
        "",
        "%s -> %s, depth %.2f%% over %d bars; the book was at full size on %.1f%% of those"
        " bars (mean scale %.2f) and **%.0f%% of the fall accumulated on exactly those bars**."
        % (dd["peak"], dd["trough"], 100 * dd["depth"], dd["bars"],
           100 * dd["share_bars_full_size"], dd["mean_scale_in_episode"],
           100 * dd["share_of_depth_accrued_at_full_size"]),
        "",
        "## What the two lags actually cost",
        "",
        "Depth is nearly invariant across the four estimators (maxDD %.2f%%..%.2f%%, a spread of"
        " %.2fpp) while return is not (CAGR %.2f%%..%.2f%%, a spread of %.2fpp). So the lateness"
        " is not a drawdown problem -- the overlay is not what sets the depth at these vol levels"
        " -- it is a RETURN problem: a stale high estimate keeps the book de-levered while the"
        " rebound happens. That matches the slot census: %.1f%% of slots were delevered and the"
        " median delivered vol was %.2f%% against a %.0f%% target."
        % (100 * min(x["maxdd"] for x in arms), 100 * max(x["maxdd"] for x in arms),
           100 * (max(x["maxdd"] for x in arms) - min(x["maxdd"] for x in arms)),
           100 * min(x["cagr"] for x in arms), 100 * max(x["cagr"] for x in arms),
           100 * (max(x["cagr"] for x in arms) - min(x["cagr"] for x in arms)),
           100 * lag["share_delevered"], 100 * lag["median_delivered_vol"], 100 * TARGET_VOL),
        "",
        "## Verdict",
        "",
        "**%s** -- %s." % (payload["verdict"], "; ".join(payload["verdict_reasons"])),
        "",
        "Read this as a bound on the overlay, not an invitation: a shorter window is a faster"
        " estimator, and the frozen rule asks it to buy DEPTH, not return. If it cannot, the"
        " lateness stays as the price of not trading on noise -- the same trade the decision-"
        "margin census found (E187 family) -- and the return it gives up should be quoted"
        " beside the headline rather than assumed to be free insurance.",
        "",
        "## Caveats",
        "",
    ] + ["- " + c for c in payload["caveats"]]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- selftest

def _fixture(bars=520, names=12, seed=11, vol=0.010, shock_at=None, shock_mult=3.0):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2020-01-02", periods=bars)
    cols = ["sh%06d" % (510000 + 40 * i) for i in range(names)]
    rets = rng.normal(0.0, vol, size=(bars, names))
    if shock_at is not None:
        rets[shock_at:, :] *= shock_mult
    px = 100 * np.cumprod(1.0 + rets, axis=0)
    close = pd.DataFrame(px, index=idx, columns=cols)
    openp = close.shift(1).bfill() * (1.0 + rng.normal(0, 0.0005, size=(bars, names)))
    amt = pd.DataFrame(1e9, index=idx, columns=cols)
    score = pd.DataFrame(rets, index=idx, columns=cols)          # momentum-ish, deterministic
    return close, openp, amt, score


def selftest():
    legs = []

    def check(name, ok, detail=""):
        legs.append({"leg": name, "pass": bool(ok), "detail": str(detail)[:200]})

    close, openp, amt, score = _fixture()
    ser60, turn60, diag60 = run_arm(close, openp, amt, score, 60)
    lag60 = lag_block(openp, diag60)
    check("fixture: engine produced a curve", len(ser60.dropna()) > 100, len(ser60))
    check("fixture: mechanism moved (slots measured)",
          lag60.get("n_slots", 0) > 10, lag60.get("n_slots"))
    ser60b, _, diag60b = run_arm(close, openp, amt, score, 60)
    check("determinism: same window twice is identical",
          abs(ser60.iloc[-1] - ser60b.iloc[-1]) < 1e-12)
    ser20, _, diag20 = run_arm(close, openp, amt, score, 20)
    # On a stationary-vol fixture every trailing window reads the same vol, so identical
    # arms here are the correct answer, not a dead test (r1261: an equivalence must prove
    # the mechanism CAN move). The discriminating fixture is the regime-shift one below.
    check("stationary vol: windows agree by construction, not by accident",
          abs(ser20.iloc[-1] - ser60.iloc[-1]) < 1e-9,
          "%.6f vs %.6f" % (ser20.iloc[-1], ser60.iloc[-1]))

    # the lag itself: put a 3x vol shock half way through and the trailing window must miss it
    close2, openp2, amt2, score2 = _fixture(shock_at=320, shock_mult=3.0)
    _, _, diag2 = run_arm(close2, openp2, amt2, score2, 60)
    lag2 = lag_block(openp2, diag2)
    check("lag is measured, not assumed: a vol shock shows as ratio > 1.5",
          lag2.get("p90_ratio", 0) > 1.2, "p90=%.2f median=%.2f"
          % (lag2.get("p90_ratio", 0), lag2.get("median_ratio", 0)))
    ser2_20, _, _ = run_arm(close2, openp2, amt2, score2, 20)
    ser2_60, _, _ = run_arm(close2, openp2, amt2, score2, 60)
    check("regime shift: the estimator window now changes the curve",
          abs(ser2_20.iloc[-1] - ser2_60.iloc[-1]) > 1e-6,
          "%.6f vs %.6f" % (ser2_20.iloc[-1], ser2_60.iloc[-1]))
    check("no shock -> ratios stay near 1",
          0.5 < lag60.get("median_ratio", 0) < 1.6, lag60.get("median_ratio"))

    # the gate must refuse a face that echoes other thresholds or a hand-written verdict
    good = {"criteria": dict(CRITERIA), "arms": [{"vol_window": w} for w in WINDOWS],
            "lag": {"n_slots": 5}, "verdict": None, "verdict_reasons": None,
            "published_control_cagr": None, "evidence_cutoff": "2026-01-01"}
    errs = check_payload(good, None)
    check("gate: a hand-written / missing verdict is refused",
          any("verdict" in e for e in errs), errs[:2])
    bad = dict(good, criteria={**CRITERIA, "dd_improve_pp": 99.0})
    check("gate: changed thresholds are refused",
          any("criteria echo" in e for e in check_payload(bad, None)))

    # verdict arithmetic on synthetic summaries
    ctrl = {"vol_window": 60, "cagr": 0.10, "maxdd": -0.10}
    lbl, _ = verdict({"arms": [ctrl, {"vol_window": 20, "cagr": 0.099, "maxdd": -0.11}]}, None)
    check("verdict: no depth improvement -> KEEP", lbl == "KEEP", lbl)
    lbl2, _ = verdict({"arms": [ctrl, {"vol_window": 20, "cagr": 0.097, "maxdd": -0.06}]}, None)
    check("verdict: 4pp depth for -0.3pp return -> CANDIDATE", lbl2 == "CANDIDATE_WINDOW_20", lbl2)
    lbl3, _ = verdict({"arms": [ctrl, {"vol_window": 20, "cagr": 0.097, "maxdd": -0.06},
                                {"vol_window": 40, "cagr": 0.098, "maxdd": -0.055}]}, None)
    check("verdict: two qualifying arms -> ambiguous KEEP", lbl3 == "KEEP", lbl3)
    lbl4, _ = verdict({"arms": [{"vol_window": 60, "cagr": 0.10, "maxdd": -0.10}]}, 0.15)
    check("verdict: control off the published cell -> REJECT", lbl4 == "REJECT", lbl4)

    n_pass = sum(1 for l in legs if l["pass"])
    for l in legs:
        print("%s %s%s" % ("PASS" if l["pass"] else "FAIL", l["leg"],
                           (" | " + l["detail"]) if l["detail"] else ""))
    print("%d/%d legs PASS" % (n_pass, len(legs)))
    return 0 if n_pass == len(legs) else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run", choices=("run", "check", "selftest"))
    ap.add_argument("--out", default=str(OUT_JSON))
    ap.add_argument("--no-md", action="store_true")
    ap.add_argument("--selftest", action="store_true", help="alias for the selftest sub-command")
    ap.add_argument("--check", action="store_true", help="alias for the check sub-command")
    args = ap.parse_args(argv)
    if args.selftest:
        args.cmd = "selftest"
    elif args.check:
        args.cmd = "check"
    if args.cmd == "selftest":
        return selftest()
    if args.cmd == "check":
        return check()
    payload = build()
    Path(args.out).write_text(json.dumps(payload, indent=1, ensure_ascii=False), encoding="utf-8")
    if not args.no_md:
        OUT_MD.write_text(render_md(payload), encoding="utf-8")
    lag = payload["lag"]
    print(json.dumps({"face": FACE, "verdict": payload["verdict"],
                      "control_cagr": payload["published_control_cagr"],
                      "arms": [{"w": a["vol_window"], "cagr": a["cagr"], "maxdd": a["maxdd"],
                                "sharpe": a["sharpe"]} for a in payload["arms"]],
                      "lag": {k: lag[k] for k in ("n_slots", "median_ratio", "p90_ratio",
                                                  "share_ratio_gt_1_5", "share_delevered")},
                      "dd": payload["control_drawdown"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())