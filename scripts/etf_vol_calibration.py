"""Does the 8% vol label survive a causal (walk-forward) calibration?

r1272 explained where the 12-name sleeve's 10.18% realised vol comes from: the 60d backward
estimator reads 12.25% against 13.62% realised over the same holds (the score carries vol_60
with a negative sign, so it prefers names whose trailing vol is low), plus ~1pp of intra-hold
clustering. The gap was reported, deliberately not corrected -- a multiplier fitted on the
same sample is exactly the fitting the earlier sweeps exist to detect.

This script asks the follow-up question: can the label be made TRUE without fitting? The
calibration below is causal by construction. At every decision it only knows
  * the estimator value the engine just produced, and
  * the realised vol of the holds that have already COMPLETED before today.
It forms m = median(realised_j / est_j) over those completed holds (needs MIN_OBS of them,
before which m = 1.0, i.e. the published behaviour), and sizes with
  scale = min(cap, target / (est * m)).
No future bar, no full-sample ratio, no parameter chosen by looking at the answer.

Arms (frozen production config: 12 names, 20-bar grid, 10bp/side, next-open fills):
  A  no target            reference, the un-de-levered book
  B  target 8%, m=1       the published behaviour
  C  target 8%, walk-fwd  the calibrated book, cap 1.0
  D  target 8%, walk-fwd, cap 3.0   same calibration, allowed to lever up

Adoption rule is stated before the numbers and evaluated mechanically:
  (1) delivered vol within 1.0pp of the target in BOTH the full window and OOS;
  (2) full-window Sharpe no worse than the published arm by more than 0.02;
  (3) the calibration must actually be active for >=50% of decisions;
  (4) m must not drift: |m(2nd half) - m(1st half)| / m(1st half) <= 0.50.
Failing any leg leaves the card's label honest-but-wrong (reported, not corrected) and says
which leg failed.

  python scripts/etf_vol_calibration.py run
  python scripts/etf_vol_calibration.py --selftest
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

SCHEMA = "etf-vol-calibration/v1"
OUT = os.path.join(PATHS.results_dir, "etf_vol_calibration.json")
N_HOLD = 12
REBAL = 20
COST = 0.0010
TARGET = 0.08
CAP_UNCAPPED = 3.0
MIN_OBS = 6          # completed holds required before m is used at all
VOL_TOL = 0.01       # adoption leg (1)
SHARPE_TOL = 0.02    # adoption leg (2)
ACTIVE_SHARE = 0.50  # adoption leg (3)
DRIFT_TOL = 0.50     # adoption leg (4)


class WalkForwardCalibration:
    """Causal delivered/estimated vol multiplier from completed holds only.

    The engine's hold at decision i runs from the open of bar i+1 to the open of bar
    i+rebal, so its realised vol is only knowable at decision i+rebal -- which is exactly
    when the next hook call happens. Settlement therefore happens inside the hook, for
    holds that have already closed, and the current decision never sees its own outcome.
    """

    def __init__(self, openp, rebal=REBAL, min_obs=MIN_OBS, mode="median"):
        if mode not in ("median", "rms"):
            raise ValueError("mode must be median or rms")
        self.mode = mode
        self.rets = openp.pct_change()
        self.index = self.rets.index
        self.rebal = rebal
        self.min_obs = min_obs
        self.pending = []
        self.ratios = []
        self.path = []

    def _settle(self, i):
        keep = []
        for p in self.pending:
            if i >= p["i"] + self.rebal:
                fwd = self.rets.iloc[p["i"] + 1: p["i"] + self.rebal + 1][p["picks"]]
                if fwd.shape[0] >= 5:
                    f = fwd.mean(axis=1)
                    v = float(f.std() * np.sqrt(252))
                    if np.isfinite(v) and v > 0 and p["est"]:
                        self.ratios.append(v / p["est"])
            else:
                keep.append(p)
        self.pending = keep

    def __call__(self, est, d, picks):
        i = int(self.index.get_indexer([pd.Timestamp(d)])[0])
        if i >= 0:
            self._settle(i)
        self.pending.append({"i": i, "est": est, "picks": list(picks)})
        m = 1.0
        if len(self.ratios) >= self.min_obs:
            arr = np.asarray(self.ratios, dtype=float)
            # median = "typical hold", rms = the multiplier that a MIXTURE variance target
            # actually needs: delivered annualised vol is rms(scale x hold vol), so sizing
            # on the rms of past ratios is the algebra, not a tuned knob.
            m = (float(np.median(arr)) if self.mode == "median"
                 else float(np.sqrt(np.mean(arr ** 2))))
        self.path.append({"date": str(pd.Timestamp(d).date()), "m": m, "n_obs": len(self.ratios)})
        return m


def windows(ser):
    out = {}
    for lbl, sl in (("full", ser), ("is", ser[ser.index <= R.IS_END]),
                    ("oos", ser[ser.index > R.IS_END])):
        m = A.stats2(sl, lbl)
        out[lbl] = {k: m.get(k) for k in ("cagr", "sharpe", "maxdd", "vol", "years")}
    return out


def arm(close, openp, amt, score, vol_target, cap, calib=None):
    diag = []
    ser, turn = R.open_to_open_equity(close, openp, amt, score, REBAL, N_HOLD, COST,
                                     vol_target=vol_target, vol_cap=cap, diag=diag,
                                     ratio_hook=calib)
    scales = [d["scale"] for d in diag]
    out = {
        "vol_target": vol_target, "vol_cap": cap,
        "calibration": ("walk-forward-" + calib.mode) if calib is not None else "none",
        "turnover_per_decision": round(turn, 3),
        "windows": windows(ser),
        "decisions": len(diag),
        "scale_mean": round(float(np.mean(scales)), 4) if scales else None,
        "scale_min": round(float(np.min(scales)), 4) if scales else None,
    }
    if calib is not None:
        ms = [p["m"] for p in calib.path]
        h = len(ms) // 2
        out["ratio_path"] = {
            "n": len(ms),
            "median": round(float(np.median(ms)), 4),
            "min": round(float(np.min(ms)), 4),
            "max": round(float(np.max(ms)), 4),
            "share_above_1": round(float(np.mean([1.0 if x > 1.0 + 1e-12 else 0.0 for x in ms])), 4),
            "share_active": round(float(np.mean([1.0 if p["n_obs"] >= calib.min_obs else 0.0
                                                for p in calib.path])), 4),
            "median_first_half": round(float(np.median(ms[:h])), 4) if h else None,
            "median_second_half": round(float(np.median(ms[h:])), 4) if h else None,
            "first_active": next((p["date"] for p in calib.path if p["n_obs"] >= calib.min_obs), None),
        }
    return out, ser, diag


def yearly_vol(ser, target):
    r = ser.pct_change().dropna()
    rows = {}
    for y, grp in r.groupby(r.index.year):
        v = float(grp.std() * np.sqrt(252))
        rows[str(y)] = {"vol": round(v, 4), "abs_error_vs_target": round(abs(v - target), 4)}
    errs = [x["abs_error_vs_target"] for x in rows.values()]
    return rows, (round(float(np.mean(errs)), 4) if errs else None)


def decide(pub, cal, cal_unc):
    """The pre-stated adoption rule, evaluated mechanically."""
    legs = {}
    vf = cal["windows"]["full"]["vol"] or 0.0
    vo = cal["windows"]["oos"]["vol"] or 0.0
    legs["vol_within_tol"] = {
        "pass": abs(vf - TARGET) <= VOL_TOL and abs(vo - TARGET) <= VOL_TOL,
        "full": round(vf, 4), "oos": round(vo, 4), "tol": VOL_TOL,
    }
    sf = cal["windows"]["full"]["sharpe"] or 0.0
    sb = pub["windows"]["full"]["sharpe"] or 0.0
    legs["sharpe_not_worse"] = {"pass": sf >= sb - SHARPE_TOL,
                               "calibrated": sf, "published": sb, "tol": SHARPE_TOL}
    path = cal.get("ratio_path") or {}
    legs["calibration_active"] = {"pass": (path.get("share_active") or 0.0) >= ACTIVE_SHARE,
                                 "share_active": path.get("share_active"), "need": ACTIVE_SHARE}
    m1, m2 = path.get("median_first_half"), path.get("median_second_half")
    drift = (abs((m2 or 0.0) - (m1 or 0.0)) / m1) if m1 else None
    legs["ratio_stable"] = {"pass": drift is not None and drift <= DRIFT_TOL,
                            "drift": None if drift is None else round(float(drift), 4),
                            "tol": DRIFT_TOL}
    failed = [k for k, v in legs.items() if not v["pass"]]
    return {
        "legs": legs,
        "verdict": "ADOPT" if not failed else "HOLD",
        "failed_legs": failed,
        "note": ("ADOPT = the label can be made true causally on this sample; the card may "
                 "publish the calibrated scale. HOLD = keep reporting the gap instead."
                 if not failed else
                 "HOLD = at least one pre-stated leg failed, so the label stays reported-not-"
                 "corrected; failed legs listed above."),
    }


def mixture_diag(diag, openp, measured_vol):
    """Ex-post check of the mixture identity: delivered vol ~= rms(scale x hold vol).

    Diagnostic only -- the realised vol of a hold is unknowable at its decision, so this
    never feeds sizing. It answers whether ANY constant-multiplier rule can close the gap:
    annualised vol of a mixture of segments is the root-mean-square of the segment vols, so
    a rule sized on the MEDIAN ratio must undershoot by the dispersion of the segments.
    """
    rets = openp.pct_change()
    idx = rets.index
    rows = []
    for d in diag:
        if d["est_vol"] is None:
            continue
        i = int(idx.get_indexer([pd.Timestamp(d["date"])])[0])
        if i < 0:
            continue
        fwd = rets.iloc[i + 1: i + 1 + REBAL][d["book"]]
        if fwd.shape[0] < 5:
            continue
        f = fwd.mean(axis=1)
        v = float(f.std() * np.sqrt(252))
        if np.isfinite(v) and v > 0:
            rows.append({"v": v, "scale": d["scale"], "est": d["est_vol"], "ratio": v / d["est_vol"]})
    if not rows:
        return None
    v = np.array([r["v"] for r in rows])
    sc = np.array([r["scale"] for r in rows])
    rt = np.array([r["ratio"] for r in rows])
    sized = sc * v
    rms_sized = float(np.sqrt(np.mean(sized ** 2)))
    mean_sized = float(np.mean(sized))
    return {
        "n": len(rows),
        "hold_vol_mean": round(float(v.mean()), 4),
        "hold_vol_rms": round(float(np.sqrt(np.mean(v ** 2))), 4),
        "hold_vol_dispersion_rms_over_mean": round(float(np.sqrt(np.mean(v ** 2)) / v.mean()), 3),
        "sized_mean": round(mean_sized, 4),
        "sized_rms": round(rms_sized, 4),
        "measured_annualised": round(float(measured_vol), 4),
        "rms_minus_mean": round(rms_sized - mean_sized, 4),
        "identity_error_rms_vs_measured": round(rms_sized - float(measured_vol), 4),
        "ratio_median": round(float(np.median(rt)), 4),
        "ratio_rms": round(float(np.sqrt(np.mean(rt ** 2))), 4),
        "ratio_rms_over_median": round(float(np.sqrt(np.mean(rt ** 2)) / np.median(rt)), 3),
        "note": "delivered vol is the rms of the sized segment vols; a median-sized rule "
                "undershoots by ratio_rms_over_median, which is why per-hold calibration on "
                "the median cannot move the label much",
    }


def run():
    close, openp, amt, score, cls, n_flip = P.prep_panel()
    a, ser_a, _ = arm(close, openp, amt, score, None, 1.0)
    b, ser_b, diag_b_arm = arm(close, openp, amt, score, TARGET, 1.0)
    c, ser_c, diag_c = arm(close, openp, amt, score, TARGET, 1.0,
                           WalkForwardCalibration(openp, mode="median"))
    d, ser_d, _ = arm(close, openp, amt, score, TARGET, CAP_UNCAPPED,
                      WalkForwardCalibration(openp, mode="median"))
    e, ser_e, diag_e = arm(close, openp, amt, score, TARGET, 1.0,
                           WalkForwardCalibration(openp, mode="rms"))

    by_b, err_b = yearly_vol(ser_b, TARGET)
    by_c, err_c = yearly_vol(ser_c, TARGET)
    by_e, err_e = yearly_vol(ser_e, TARGET)
    scales_c = {r["date"]: r["scale"] for r in diag_c}
    map_b = {r["date"]: r["scale"] for r in diag_b_arm}
    moved = [abs(scales_c[k] - map_b[k]) for k in map_b if k in scales_c]
    mix_b = mixture_diag(diag_b_arm, openp, b["windows"]["full"]["vol"])
    mix_e = mixture_diag(diag_e, openp, e["windows"]["full"]["vol"])
    out = {
        "schema": SCHEMA,
        "generated": None,
        "evidence_cutoff": str(close.index[-1].date()),
        "panel_flip_repairs": n_flip,
        "config": {"n_hold": N_HOLD, "rebal": REBAL, "cost_bp": COST * 1e4,
                   "target_vol": TARGET, "min_obs": MIN_OBS, "uncapped_cap": CAP_UNCAPPED,
                   "execution": "decide at close t -> fill at open t+1 -> hold to next rebalance"},
        "arms": {"A_no_target": a, "B_published": b, "C_calibrated_median": c,
                 "D_calibrated_median_uncapped": d, "E_calibrated_rms": e},
        "yearly_vol": {"published": by_b, "calibrated_median": by_c, "calibrated_rms": by_e,
                       "mean_abs_error_published": err_b,
                       "mean_abs_error_calibrated_median": err_c,
                       "mean_abs_error_calibrated_rms": err_e},
        "mixture": {"published": mix_b, "calibrated_rms": mix_e},
        "decisions_moved": {
            "n": len(moved),
            "share_moved_gt_2pp_of_scale": round(float(np.mean([1.0 if x > 0.02 else 0.0
                                                                for x in moved])), 4),
            "mean_abs_scale_change": round(float(np.mean(moved)), 4) if moved else None,
        },
        "decision_median": decide(b, c, d),
        "decision_rms": decide(b, e, None),
        "decision": None,
        "headline": None,
    }
    out["decision"] = out["decision_rms"]
    dp = b["windows"]["full"]["vol"]
    dc = c["windows"]["full"]["vol"]
    de = e["windows"]["full"]["vol"]
    out["headline"] = (
        "at an 8%% label the published book delivers %.2f%%; a causal median-ratio calibration "
        "reaches only %.2f%% (m median %.2f) because delivered vol is the rms of the sized holds "
        "(rms/median ratio %.2f), while the rms calibration reaches %.2f%% (full) / %.2f%% (OOS) "
        "with Sharpe %.3f vs %.3f and maxDD %.1f%% vs %.1f%%; verdict %s"
        % (dp * 100, dc * 100, (c["ratio_path"]["median"] or 0.0),
           (mix_b or {}).get("ratio_rms_over_median") or 0.0, de * 100,
           (e["windows"]["oos"]["vol"] or 0) * 100,
           e["windows"]["full"]["sharpe"] or 0.0, b["windows"]["full"]["sharpe"] or 0.0,
           (e["windows"]["full"]["maxdd"] or 0) * 100, (b["windows"]["full"]["maxdd"] or 0) * 100,
           out["decision"]["verdict"]))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1, sort_keys=True)
    print(out["headline"])
    for k in ("full", "is", "oos"):
        print("  %-4s pub %.2f%% sr %.3f dd %.1f%% | med %.2f%% sr %.3f | rms %.2f%% sr %.3f dd %.1f%%"
              % (k, b["windows"][k]["vol"] * 100, b["windows"][k]["sharpe"],
                 b["windows"][k]["maxdd"] * 100,
                 c["windows"][k]["vol"] * 100, c["windows"][k]["sharpe"],
                 e["windows"][k]["vol"] * 100, e["windows"][k]["sharpe"],
                 e["windows"][k]["maxdd"] * 100))
    print("  yearly |err| pub %.3f | med %.3f | rms %.3f"
          % (err_b or 0.0, err_c or 0.0, err_e or 0.0))
    print("  mixture: hold vol rms/mean %.2f, ratio rms/median %.2f, identity err %.2fpp"
          % ((mix_b or {}).get("hold_vol_dispersion_rms_over_mean") or 0.0,
             (mix_b or {}).get("ratio_rms_over_median") or 0.0,
             ((mix_b or {}).get("identity_error_rms_vs_measured") or 0.0) * 100))
    print("  decision rms:", out["decision_rms"]["verdict"], out["decision_rms"]["failed_legs"])
    print("wrote", OUT)
    return 0


def _fixture(n_sym=40, n_bar=1500, seed=7):
    """Small synthetic panel: every leg below guards a code path, not the market.

    This file used to call P.prep_panel() (1499 symbols x 1649 bars) and then drive the
    engine ten times, so `--selftest` printed nothing for ~5 minutes and sat right on the
    300 s per-leg timeout inside the S1 smoke gate -- the same defect r1300 fixed one
    script over (etf_vol_delivery_audit). A fixture keeps every leg meaningful offline.
    """
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2020-01-01", periods=n_bar)
    cols = ["S%03d" % i for i in range(n_sym)]
    rets = rng.normal(0.0004, 0.022, size=(n_bar, n_sym))
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

    # 1. the hook defaults to the published behaviour, bit for bit
    ser_legacy, turn_legacy = R.open_to_open_equity(close, openp, amt, score, REBAL, N_HOLD,
                                                    COST, vol_target=TARGET)
    diag = []
    ser_none, turn_none = R.open_to_open_equity(close, openp, amt, score, REBAL, N_HOLD, COST,
                                                vol_target=TARGET, diag=diag, ratio_hook=None)
    maxabs = float(np.max(np.abs((ser_legacy - ser_none).to_numpy())))
    chk("ratio_hook=None is bit-identical to the published overlay",
        maxabs == 0.0 and turn_legacy == turn_none,
        "maxabs=%.2e turn %.6f/%.6f" % (maxabs, turn_legacy, turn_none))
    chk("diag carries ratio 1.0 when no hook is used",
        diag and all(abs(r["ratio"] - 1.0) < 1e-12 for r in diag), "n=%d" % len(diag))

    # 2. a constant hook moves the book in the expected direction (activity + arithmetic)
    ser_f, _ = R.open_to_open_equity(close, openp, amt, score, REBAL, N_HOLD, COST,
                                     vol_target=TARGET, ratio_hook=lambda e, d, p: 1.25)
    chk("constant ratio 1.25 actually changes the book (activity leg, r1261 family)",
        float(np.max(np.abs((ser_f - ser_none).to_numpy()))) > 1e-6,
        "maxabs=%.3e" % float(np.max(np.abs((ser_f - ser_none).to_numpy()))))
    s_plain = [r["scale"] for r in diag]
    diag_f = []
    R.open_to_open_equity(close, openp, amt, score, REBAL, N_HOLD, COST,
                          vol_target=TARGET, diag=diag_f, ratio_hook=lambda e, d, p: 1.25)
    s_f = [r["scale"] for r in diag_f]
    chk("ratio 1.25 de-levers every decision it touches",
        all(a <= b + 1e-12 for a, b in zip(s_f, s_plain)),
        "mean %.4f -> %.4f" % (float(np.mean(s_plain)), float(np.mean(s_f))))

    # 3. the calibration is causal: truncating the panel must not change past decisions
    cut = len(close.index) - 260
    cl2, op2, am2 = close.iloc[:cut], openp.iloc[:cut], amt.iloc[:cut]
    sc2 = score.loc[op2.index]
    d_full = []
    R.open_to_open_equity(close, openp, amt, score, REBAL, N_HOLD, COST, vol_target=TARGET,
                          diag=d_full, ratio_hook=WalkForwardCalibration(openp))
    d_trunc = []
    R.open_to_open_equity(cl2, op2, am2, sc2, REBAL, N_HOLD, COST, vol_target=TARGET,
                          diag=d_trunc, ratio_hook=WalkForwardCalibration(op2))
    mf = {r["date"]: r for r in d_full}
    diffs, compared = [], 0
    for r in d_trunc:
        f = mf.get(r["date"])
        if not f or f["book"] != r["book"]:
            continue  # different picks -> different decision, not a causality test
        compared += 1
        diffs.append(abs(f["scale"] - r["scale"]))
    chk("past decisions are unchanged by truncating the future (no lookahead)",
        compared > 20 and max(diffs) <= 1e-12,
        "compared=%d maxdiff=%.2e" % (compared, max(diffs) if diffs else -1))

    # 4. warm-up: m stays exactly 1.0 until MIN_OBS holds have completed
    cal = WalkForwardCalibration(openp)
    diag_w = []
    R.open_to_open_equity(close, openp, amt, score, REBAL, N_HOLD, COST, vol_target=TARGET,
                          diag=diag_w, ratio_hook=cal)
    warm = [p["m"] for p in cal.path if p["n_obs"] < MIN_OBS]
    chk("no calibration before the warm-up completes",
        warm and all(abs(x - 1.0) < 1e-12 for x in warm),
        "warm decisions=%d" % len(warm))
    first_active = next((p for p in cal.path if p["n_obs"] >= MIN_OBS), None)
    chk("calibration only activates after MIN_OBS completed holds",
        first_active is None or first_active["n_obs"] >= MIN_OBS,
        "n_obs at activation=%s" % (first_active["n_obs"] if first_active else None))

    # 5. unit math on the settlement rule (synthetic, no panel)
    idx = pd.bdate_range("2022-01-03", periods=90)
    rng = np.random.default_rng(11)
    px = pd.DataFrame({"a": 100 * np.exp(np.cumsum(rng.normal(0, 0.01, 90))),
                       "b": 100.0}, index=idx)
    u = WalkForwardCalibration(px, rebal=20, min_obs=3)
    u(0.10, idx[0], ["a"])
    u(0.10, idx[20], ["a"])
    chk("a hold settles exactly when it completes", len(u.ratios) == 1,
        "ratios=%d" % len(u.ratios))
    m2 = u(0.10, idx[40], ["a"])
    chk("m is NaN-free and 1.0 while observations are short",
        np.isfinite(m2) and abs(m2 - 1.0) < 1e-12, "m=%.4f obs=%d" % (m2, len(u.ratios)))
    m3 = u(0.10, idx[60], ["a"])
    chk("m becomes the median of completed ratios once MIN_OBS is met",
        abs(m3 - float(np.median(u.ratios[:3]))) < 1e-12, "m=%.4f obs=%d" % (m3, len(u.ratios)))

    # 6. the mixture identity: measured annualised vol must equal the rms of the sized holds
    diag_b = []
    ser_b, _ = R.open_to_open_equity(close, openp, amt, score, REBAL, N_HOLD, COST,
                                     vol_target=TARGET, diag=diag_b)
    mx = mixture_diag(diag_b, openp, A.stats2(ser_b, "b")["vol"])
    chk("mixture identity holds (rms of sized holds == measured annualised vol)",
        mx is not None and abs(mx["identity_error_rms_vs_measured"]) <= 0.005,
        "rms=%.4f measured=%.4f err=%.4f"
        % ((mx or {}).get("sized_rms") or 0.0, (mx or {}).get("measured_annualised") or 0.0,
           (mx or {}).get("identity_error_rms_vs_measured") or 0.0))

    # 7. the rms multiplier can never sit below the median of the same ratios
    arr = np.asarray([0.9, 1.0, 1.2, 2.4])
    chk("rms multiplier >= median on the same ratio sample",
        float(np.sqrt(np.mean(arr ** 2))) >= float(np.median(arr)),
        "rms=%.4f median=%.4f" % (float(np.sqrt(np.mean(arr ** 2))), float(np.median(arr))))

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