"""Why the ETF book's 8% label delivers ~10%: the sizing cap, measured.

r1270 found the 12-name sleeve runs ~27% hotter than its label and left it reported, not
explained. This script separates the two candidate mechanisms by running the SAME book
with the overlay's cap removed:

  arm A  no target          -- the un-de-levered book (reference).
  arm B  target 8%, cap 1.0 -- the published production behaviour (de-lever only).
  arm C  target 8%, cap 3.0 -- same estimator, same window, but allowed to lever up.

Read-off:
  * If arm C lands on ~8% delivered, the estimator is accurate and the whole gap is the
    one-sided cap: the overlay never re-levers after a calm stretch, so the book carries
    the scale of a higher-vol past into a lower-vol present.
  * If arm C also overshoots, part of the gap is estimator lag (60d backward vol on a
    20-bar decision grid) and the split is reported as such.

Nothing here re-picks a parameter: both arms use the frozen production config (12 names,
20-bar grid, 10bp/side, next-open fills) and only the cap differs. The implied label
(what target would deliver 8% at the cap) is arithmetic on the measured ratio, reported
with IS/OOS ratios beside it so a reader can see whether the ratio is stable or fitted.

  python scripts/etf_vol_delivery_audit.py run
  python scripts/etf_vol_delivery_audit.py --selftest
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import numpy as np
import pandas as pd

import etf_equity_alpha as A
import etf_book_production as P
import etf_robust_pf as R
from config import PATHS

SCHEMA = "etf-vol-delivery-audit/v1"
OUT = os.path.join(PATHS.results_dir, "etf_vol_delivery_audit.json")
N_HOLD = 12
REBAL = 20
COST = 0.0010
TARGET = 0.08
CAP_UNCAPPED = 3.0


def windows(ser):
    out = {}
    for lbl, sl in (("full", ser), ("is", ser[ser.index <= R.IS_END]),
                    ("oos", ser[ser.index > R.IS_END])):
        m = A.stats2(sl, lbl)
        out[lbl] = {k: m.get(k) for k in ("cagr", "sharpe", "maxdd", "vol", "years")}
    return out


def arm(close, openp, amt, score, vol_target, cap):
    diag = []
    ser, turn = R.open_to_open_equity(close, openp, amt, score, REBAL, N_HOLD, COST,
                                     vol_target=vol_target, vol_cap=cap, diag=diag)
    w = windows(ser)
    scales = [d["scale"] for d in diag]
    ests = [d["est_vol"] for d in diag if d["est_vol"] is not None]
    return {
        "vol_target": vol_target,
        "vol_cap": cap,
        "turnover_per_decision": round(turn, 3),
        "windows": w,
        "decisions": len(diag),
        "scale_mean": round(float(np.mean(scales)), 4) if scales else None,
        "scale_min": round(float(np.min(scales)), 4) if scales else None,
        "scale_max": round(float(np.max(scales)), 4) if scales else None,
        "share_at_cap": round(float(np.mean([1.0 if abs(s - cap) < 1e-12 else 0.0
                                             for s in scales])), 4) if scales else None,
        "est_vol_mean": round(float(np.mean(ests)), 4) if ests else None,
        "est_vol_median": round(float(np.median(ests)), 4) if ests else None,
        "_ser": ser,
    }


def implied_label(vt_arm, delivered_target=TARGET):
    """Target value whose capped delivery equals `delivered_target`, by the measured ratio.

    Pure arithmetic on the arm's own ratio (ratio = delivered / label), NOT a fit: if the
    ratio moved a lot between IS and OOS the label it implies is not stable either, and
    that is stated in `ratio_stability`.
    """
    w = vt_arm["windows"]
    r_full = (w["full"]["vol"] or 0.0) / TARGET
    r_is = (w["is"]["vol"] or 0.0) / TARGET
    r_oos = (w["oos"]["vol"] or 0.0) / TARGET
    return {
        "ratio_full": round(r_full, 3),
        "ratio_is": round(r_is, 3),
        "ratio_oos": round(r_oos, 3),
        "implied_label_full": round(TARGET / r_full, 4) if r_full else None,
        "ratio_spread_is_oos": round(abs(r_is - r_oos), 3),
        "note": "implied_label = label / measured_ratio; only meaningful if the spread is small",
    }


def forward_bias(diag, openp):
    """Backward estimate at the decision vs the book's OWN realised vol over the hold.

    Each decision is sized on a 60-bar backward vol of the names it just picked. Those
    names were picked partly BECAUSE their trailing vol was low (the score carries vol_60
    with a negative sign), so the estimator can be biased low by selection alone. Measuring
    est/forward per decision says whether the 25% overshoot is noise or a tilt.
    """
    rets = openp.pct_change()
    rows = []
    for d in diag:
        if d["est_vol"] is None:
            continue
        try:
            i = list(rets.index).index(pd.Timestamp(d["date"]))
        except ValueError:
            continue
        fwd = rets.iloc[i + 1:i + 1 + REBAL][d["book"]]
        if fwd.shape[0] < 5:
            continue
        f = fwd.mean(axis=1)  # equal weights, the book before sizing
        v = float(f.std() * np.sqrt(252))
        if not np.isfinite(v) or v <= 0:
            continue
        rows.append({"date": d["date"], "est": d["est_vol"], "fwd": v, "ratio": d["est_vol"] / v,
                     "scale": d["scale"]})
    if not rows:
        return None
    ratios = [r["ratio"] for r in rows]
    predicted = float(np.mean([r["scale"] * r["fwd"] for r in rows]))
    return {
        "n": len(rows),
        "est_mean": round(float(np.mean([r["est"] for r in rows])), 4),
        "fwd_mean": round(float(np.mean([r["fwd"] for r in rows])), 4),
        "scale_mean": round(float(np.mean([r["scale"] for r in rows])), 4),
        "predicted_delivered_vol": round(predicted, 4),
        "est_over_fwd_median": round(float(np.median(ratios)), 4),
        "est_over_fwd_mean": round(float(np.mean(ratios)), 4),
        "share_underestimated": round(float(np.mean([1.0 if x < 1.0 else 0.0 for x in ratios])), 4),
        "note": "ratio<1 on most decisions = the 60d backward estimator is biased low for the "
                "names this score picks; predicted_delivered_vol = mean(scale * realised vol of "
                "that same hold), so the gap to the actual figure is intra-hold clustering",
    }


def run():
    close, openp, amt, score, cls, n_flip = P.prep_panel()
    arms = {
        "A_no_target": arm(close, openp, amt, score, None, 1.0),
        "B_capped_1.0": arm(close, openp, amt, score, TARGET, 1.0),
        "C_capped_3.0": arm(close, openp, amt, score, TARGET, CAP_UNCAPPED),
    }
    diag = []
    R.open_to_open_equity(close, openp, amt, score, REBAL, N_HOLD, COST,
                          vol_target=TARGET, vol_cap=1.0, diag=diag)
    bias = forward_bias(diag, openp)
    for k, v in arms.items():
        v.pop("_ser", None)

    b, c = arms["B_capped_1.0"], arms["C_capped_3.0"]
    v_b, v_c = b["windows"]["full"]["vol"], c["windows"]["full"]["vol"]
    gap = v_b - TARGET
    from_lag = max(0.0, v_c - TARGET)
    from_cap = max(0.0, gap - from_lag)
    out = {
        "schema": SCHEMA,
        "generated": None,
        "evidence_cutoff": str(close.index[-1].date()),
        "panel_flip_repairs": n_flip,
        "config": {"n_hold": N_HOLD, "rebal": REBAL, "cost_bp": COST * 1e4,
                   "target_vol": TARGET, "uncapped_cap": CAP_UNCAPPED},
        "arms": arms,
        "decomposition": {
            "delivered_capped": round(v_b, 4),
            "delivered_uncapped": round(v_c, 4),
            "gap_vs_label": round(gap, 4),
            "gap_from_estimator_lag": round(from_lag, 4),
            "gap_from_one_sided_cap": round(from_cap, 4),
            "share_at_cap_capped_arm": b["share_at_cap"],
            "headline": ("8%% label delivers %.1f%% capped, %.1f%% uncapped -> the one-sided cap is "
                         "worth %.1fpp of the %.1fpp gap; the 60d backward estimator reads "
                         "%.2f%% against %.2f%% realised over the same holds, and "
                         "mean(scale*hold vol)=%.2f%% leaves %.2fpp of intra-hold clustering"
                         % (v_b * 100, v_c * 100, from_cap * 100, gap * 100,
                            (bias["est_mean"] * 100) if bias else 0.0,
                            (bias["fwd_mean"] * 100) if bias else 0.0,
                            (bias["predicted_delivered_vol"] * 100) if bias else 0.0,
                            ((v_b - bias["predicted_delivered_vol"]) * 100) if bias else 0.0)),
        "residual_intra_hold": round(v_b - (bias["predicted_delivered_vol"] if bias else v_b), 4),
        },
        "implied_label": implied_label(b),
        "estimator_bias": bias,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1, sort_keys=True)
    print(out["decomposition"]["headline"])
    for k in ("full", "is", "oos"):
        print("  %-4s capped %.3f%% sr %.3f dd %.1f%% | uncapped %.3f%% sr %.3f dd %.1f%%"
              % (k, b["windows"][k]["vol"] * 100, b["windows"][k]["sharpe"],
                 b["windows"][k]["maxdd"] * 100, c["windows"][k]["vol"] * 100,
                 c["windows"][k]["sharpe"], c["windows"][k]["maxdd"] * 100))
    print("  implied label (full/is/oos ratios %.3f/%.3f/%.3f) -> %.3f%%"
          % (out["implied_label"]["ratio_full"], out["implied_label"]["ratio_is"],
             out["implied_label"]["ratio_oos"],
             (out["implied_label"]["implied_label_full"] or 0.0) * 100))
    print("wrote", OUT)
    return 0


def _fixture(n_sym=40, n_bar=1500, seed=7):
    """Small synthetic panel: the guards below are about a code path, not about the market.

    The earlier version called P.prep_panel() (1499 symbols x 1649 bars) and ran the full
    engine three times, so `--selftest` printed nothing for >10 minutes and blocked the S1
    smoke gate outright (r1298 and r1300 both lost the gate to it). A fixture keeps every
    leg meaningful and the whole file offline in seconds.
    """
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2020-01-01", periods=n_bar)
    cols = ["S%03d" % i for i in range(n_sym)]
    rets = rng.normal(0.0004, 0.013, size=(n_bar, n_sym))
    close = pd.DataFrame(1.0 * np.cumprod(1.0 + rets, axis=0), index=idx, columns=cols)
    openp = close * (1.0 + rng.normal(0.0, 0.002, size=(n_bar, n_sym)))
    amt = pd.DataFrame(5e7 * (1.0 + rng.random((n_bar, n_sym))), index=idx, columns=cols)
    score = pd.DataFrame(rng.normal(size=(n_bar, n_sym)), index=idx, columns=cols)
    return close, openp, amt, score


def selftest():
    ok = []

    def chk(name, cond, detail=""):
        ok.append((name, bool(cond), detail))

    close, openp, amt, score = _fixture()
    ser_legacy, turn_legacy = R.open_to_open_equity(close, openp, amt, score, REBAL, N_HOLD,
                                                    COST, vol_target=TARGET)
    diag = []
    ser_explicit, turn_explicit = R.open_to_open_equity(close, openp, amt, score, REBAL, N_HOLD,
                                                        COST, vol_target=TARGET, vol_cap=1.0,
                                                        diag=diag)
    chk("default vol_cap path is the same run as an explicit cap 1.0",
        float(np.max(np.abs((ser_legacy - ser_explicit).to_numpy()))) == 0.0
        and turn_legacy == turn_explicit,
        "maxabs=%.2e turn %.6f/%.6f" % (float(np.max(np.abs((ser_legacy - ser_explicit).to_numpy()))),
                                        turn_legacy, turn_explicit))

    ser_hi, turn_hi = R.open_to_open_equity(close, openp, amt, score, REBAL, N_HOLD, COST,
                                            vol_target=TARGET, vol_cap=CAP_UNCAPPED)
    diff = float(np.max(np.abs((ser_hi - ser_explicit).to_numpy())))
    chk("uncapped arm actually differs (activity leg, r1261 family)", diff > 1e-6,
        "maxabs vs capped=%.3e" % diff)

    scales = [d["scale"] for d in diag]
    chk("capped arm never exceeds scale 1.0 and diag counts every decision",
        scales and max(scales) <= 1.0 + 1e-12 and len(scales) > 50,
        "n=%d max=%.4f" % (len(scales), max(scales) if scales else -1))

    hot = float(A.stats2(ser_hi, "x")["vol"]) > float(A.stats2(ser_explicit, "x")["vol"])
    chk("early arm expected to be at least as volatile (diagnostic direction)", hot,
        "uncapped vol %.4f > capped vol %.4f"
        % (float(A.stats2(ser_hi, "x")["vol"]), float(A.stats2(ser_explicit, "x")["vol"])))

    passed = sum(1 for _, c, _ in ok if c)
    for name, cond, detail in ok:
        print(("[PASS] " if cond else "[FAIL] ") + name + (" | " + detail if detail else ""))
    print("selftest %d/%d" % (passed, len(ok)))
    return 0 if passed == len(ok) else 1


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "--selftest":
        sys.exit(selftest())
    sys.exit(run())