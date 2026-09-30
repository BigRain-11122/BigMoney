# -*- coding: utf-8 -*-
"""_r259bmc_w9_crowding_probe.py -- INNOVATION-QUOTA-SLOT-9 berth probe (zoo #84
crowding_vote / CROWD-VOTE-P1 candidate family).

Berth-time probe faces (read-only, zero engine/admission touch):
  F1 G-ANCHOR face   : four-vote composite construction on core48 panel,
                       author-verbatim thresholds (zero calibration):
                       Score = annualized 20d OLS log-trend x R^2 per member;
                       votes 1-3 on 47 non-guard members (ETF-domain adaptation:
                       industries-vs-guard-object separation mirror), vote 4 =
                       guard object 510300 own score. Crowd day = >=3/4 votes.
                       Occupancy facts per vote + state-machine episode counts
                       (asymmetric confirm 2d-out/3d-in + 75pct hysteresis
                       recovery) -- construction facts, not results.
  F2 D6 signal face : pearson of width-leg face (weak share) and composite
                       vote-count vs REGIME_GUARD below-MA20 share (nearest
                       in-production narrative neighbor) + vs #87 nh_nl B20
                       face (in-book closed-family neighbor). Signal-level
                       only; cell-level merge clause stays freeze/judge face.
  F3 descriptive fwd : core48 equal-weight fwd 5d/20d returns conditional on
                       crowd day vs non-crowd day -- descriptive census only
                       (overlapping windows, no costs, NOT a strategy claim).

Data anchor four-tuple (G-ANCHOR-FACE, O-20260928-1712):
  data/daily/<code>.csv bare-code files / pd.read_csv raw direct read /
  full panel history (first bar 2020-01-02) / 20-bar score warmup.
  Runner verify subcommand must assert same face bit-exact.

Output: results/_r259bmc_w9_crowding_probe_facts.json (evidence_cutoff anchored).
Exit 0 normal / 2 mechanism fault (honest, no masking).
"""
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DAILY = os.path.join(ROOT, "data", "daily")
OUT = os.path.join(ROOT, "results", "_r259bmc_w9_crowding_probe_facts.json")
GUARD = "510300"
W = 20
ANNUAL = 252.0
# author-verbatim frozen thresholds (wzetf.cn 2026-08-22 card, zero calibration)
TH_TOP3 = 0.20      # vote 1: mean(Top3 score) > 0.20
TH_SPREAD = 0.25    # vote 2: mean(Top3) - median(cross-section) > 0.25
TH_WEAK = 0.55      # vote 3: weak share (score<0) > 55%
TH_GUARD = 0.0      # vote 4: guard score < 0
CONFIRM_OUT = 2     # crowd state 2 consecutive days -> defensive
CONFIRM_IN = 3      # recovery state 3 consecutive days -> re-enter
HYST = 0.75         # recovery diff threshold = 0.25 * 0.75 = 0.1875
TH_RANK = 0.40      # recovery: guard score percentile among all 48 > 40%


def load_core48() -> tuple[pd.DataFrame, list[str]]:
    """Bare-code core48 close panel (date x code), sorted, de-duplicated."""
    frames = {}
    for fn in os.listdir(DAILY):
        if not fn.endswith(".csv"):
            continue
        code = fn[:-4]
        if not code.isdigit() or len(code) != 6:
            continue  # skip prefixed/special files
        df = pd.read_csv(os.path.join(DAILY, fn), parse_dates=["date"])
        s = df.set_index("date")["close"].astype(float).sort_index()
        s = s[~s.index.duplicated(keep="last")]
        frames[code] = s
    panel = pd.DataFrame(frames).sort_index()
    return panel, list(frames.keys())


def trend_score(closes: pd.DataFrame, w: int = W) -> pd.DataFrame:
    """Score = annualized OLS slope of log close (x252) x R^2, rolling w window.
    Vectorized closed form on strided windows; NaN outside warmup."""
    logp = np.log(closes.values)                    # (T, N)
    n_dates, n_sym = logp.shape
    x = np.arange(w, dtype=float)
    xc = x - x.mean()
    sxx = float((xc * xc).sum())
    if n_dates < w:
        return pd.DataFrame(np.full_like(logp, np.nan),
                            index=closes.index, columns=closes.columns)
    win = np.lib.stride_tricks.sliding_window_view(logp, w, axis=0)  # (T-w+1, N, w)
    ymean = win.mean(axis=-1, keepdims=True)
    yc = win - ymean
    slope = (yc * xc).sum(-1) / sxx
    ss_tot = (yc * yc).sum(-1)
    r2 = np.where(ss_tot > 0, (slope * slope * sxx) / np.where(ss_tot > 0, ss_tot, 1.0), 0.0)
    score = slope * ANNUAL * r2
    out = np.full_like(logp, np.nan)
    out[w - 1:] = score
    return pd.DataFrame(out, index=closes.index, columns=closes.columns)


def below_ma20_share(closes: pd.DataFrame) -> pd.Series:
    """REGIME_GUARD breadth leg semantics, full-series reconstruction
    (mirrors scripts/market_regime.py breadth_dims): share of members with
    full 20-bar MA history whose close is below own MA20."""
    below = pd.DataFrame(index=closes.index)
    valid = pd.DataFrame(index=closes.index)
    for code, s in closes.items():
        ma = s.rolling(20).mean()
        ok = s.rolling(20).count() >= 20
        below[code] = (s < ma) & ok
        valid[code] = ok
    v = valid.sum(axis=1)
    return (below.sum(axis=1) / v.replace(0, np.nan)).where(v >= 10)


def nhnl_b20(closes: pd.DataFrame, w: int = 20) -> pd.Series:
    """#87 nh_nl_breadth B_t face (W7 probe construction, closed family)."""
    nh = pd.DataFrame(index=closes.index)
    nl = pd.DataFrame(index=closes.index)
    valid = pd.DataFrame(index=closes.index)
    for code, s in closes.items():
        roll_max = s.rolling(w).max()
        roll_min = s.rolling(w).min()
        ok = s.rolling(w).count() >= w
        nh[code] = (s == roll_max) & ok
        nl[code] = (s == roll_min) & ok
        valid[code] = ok
    v = valid.sum(axis=1)
    return ((nh.sum(axis=1) - nl.sum(axis=1)) / v.replace(0, np.nan)).where(v >= 30)


def build_faces(closes: pd.DataFrame):
    """Vote faces on 47 non-guard members + guard self-momentum vote."""
    scores = trend_score(closes)
    members = [c for c in closes.columns if c != GUARD]
    xs = scores[members]                       # (T, 47)
    guard_s = scores[GUARD]                     # (T,)
    top3 = xs.apply(lambda r: r.nlargest(3).mean(), axis=1)
    med = xs.median(axis=1)
    weak_share = (xs < 0).sum(axis=1) / xs.notna().sum(axis=1).replace(0, np.nan)
    decidable = xs.notna().sum(axis=1) >= 30
    v1 = (top3 > TH_TOP3) & decidable
    v2 = ((top3 - med) > TH_SPREAD) & decidable
    v3 = (weak_share > TH_WEAK) & decidable
    v4 = (guard_s < TH_GUARD) & decidable
    votes = pd.DataFrame({"v1": v1, "v2": v2, "v3": v3, "v4": v4})
    vote_count = votes.sum(axis=1).where(decidable)
    crowd = (vote_count >= 3) & decidable
    # recovery faces (independent four-dimension, same >=3/4, 75pct hysteresis)
    rank_pct = closes.columns.size and scores.rank(axis=1, pct=True)[GUARD]
    r1 = (guard_s > 0) & decidable
    r2 = (rank_pct > TH_RANK) & decidable
    r3 = ((top3 - med) < TH_SPREAD * HYST) & decidable
    r4 = (weak_share < TH_WEAK) & decidable
    rec_votes = pd.DataFrame({"r1": r1, "r2": r2, "r3": r3, "r4": r4})
    rec_count = rec_votes.sum(axis=1).where(decidable)
    recover = (rec_count >= 3) & decidable
    faces = pd.DataFrame({
        "top3": top3, "med": med, "spread": top3 - med, "weak_share": weak_share,
        "guard_score": guard_s, "guard_rank": rank_pct,
        "vote_count": vote_count, "crowd": crowd, "recover": recover,
    })
    return faces, votes, rec_votes, decidable


def state_machine(faces: pd.DataFrame, confirm_out: int, confirm_in: int,
                  hysteresis: bool) -> dict:
    """Descriptive state-machine episode counts (construction facts).
    State ON at first decidable day (W7 initial-state convention).
    OFF entry: `crowd` True CONFIRM_OUT consecutive days.
    ON  re-entry: `recover` True CONFIRM_IN consecutive days (asymmetric face
    uses hysteresis-carrying recovery votes; symmetric ablation uses
    no-hysteresis recovery votes -- computed by caller)."""
    state = "ON"
    run = 0
    flips = []
    first = None
    for dt, row in faces.iterrows():
        if first is None:
            if bool(row["crowd"]) or bool(row["recover"]):
                first = dt
            else:
                continue
        trig = row["crowd"] if state == "ON" else row["recover"]
        run = run + 1 if bool(trig) else 0
        need = confirm_out if state == "ON" else confirm_in
        if run >= need:
            state = "OFF" if state == "ON" else "ON"
            flips.append(dt)
            run = 0
    return {"n_flips": len(flips), "first_flip_dates": [str(d.date()) for d in flips[:6]]}


def main() -> int:
    try:
        closes, codes = load_core48()
        if GUARD not in closes.columns:
            print(f"PROBE FAULT: guard object {GUARD} not in panel", file=sys.stderr)
            return 2
        cutoff = str(closes.index[-1].date())
        ew_ret = closes.pct_change().mean(axis=1)
        ew = (1.0 + ew_ret.fillna(0.0)).cumprod()

        faces, votes, rec_votes, decidable = build_faces(closes)
        dec_days = faces[decidable]
        n_dec = int(len(dec_days))

        facts = {
            "probe": "INNOVATION-QUOTA-SLOT-9 berth probe (zoo #84 crowding_vote)",
            "machine": "bm-c",
            "round": "r259",
            "evidence_cutoff": cutoff,
            "thresholds_frozen": {
                "score": f"annualized {W}d OLS log-trend x R^2 (x{ANNUAL:.0f})",
                "v1_top3_gt": TH_TOP3, "v2_spread_gt": TH_SPREAD,
                "v3_weak_share_gt": TH_WEAK, "v4_guard_score_lt": TH_GUARD,
                "crowd_rule": ">=3/4 votes", "confirm_out_days": CONFIRM_OUT,
                "confirm_in_days": CONFIRM_IN, "hysteresis_pct": HYST,
                "recovery_diff_lt": round(TH_SPREAD * HYST, 4),
                "recovery_rank_gt": TH_RANK,
                "note": "author-verbatim wzetf 2026-08-22 card, zero calibration",
            },
            "panel": {
                "n_symbols": len(codes),
                "n_members_non_guard": len(codes) - 1,
                "guard": GUARD,
                "first_date": str(closes.index[0].date()),
                "last_date": cutoff,
                "n_dates_total": int(len(closes)),
            },
            "g_anchor_face": {
                "anchor_four_tuple": (
                    "data/daily/<code>.csv bare-code 48 files / "
                    "pd.read_csv raw direct read / full panel history / "
                    f"{W}-bar score warmup"),
                "n_decidable_days": n_dec,
                "first_decidable_date": str(dec_days.index[0].date()),
                "vote_occupancy": {
                    "v1_days": int(dec_days["v1"].sum()) if "v1" in dec_days else int(votes["v1"].sum()),
                    "v2_days": int(votes["v2"].sum()),
                    "v3_days": int(votes["v3"].sum()),
                    "v4_days": int(votes["v4"].sum()),
                },
                "crowd_days_ge3": int(dec_days["crowd"].sum()),
                "crowd_days_eq4": int((dec_days["vote_count"] == 4).sum()),
                "recover_days_ge3": int(dec_days["recover"].sum()),
                "vote_count_mean": round(float(dec_days["vote_count"].mean()), 4),
                "weak_share_q10": round(float(dec_days["weak_share"].quantile(0.10)), 4),
                "weak_share_q90": round(float(dec_days["weak_share"].quantile(0.90)), 4),
                "top3_mean_q10": round(float(dec_days["top3"].quantile(0.10)), 4),
                "top3_mean_q90": round(float(dec_days["top3"].quantile(0.90)), 4),
                "spread_q10": round(float(dec_days["spread"].quantile(0.10)), 4),
                "spread_q90": round(float(dec_days["spread"].quantile(0.90)), 4),
                "guard_score_neg_days": int((dec_days["guard_score"] < 0).sum()),
                "extreme_day_sample": [],
            },
            "state_machine_face": {},
            "d6_signal_face": {},
            "descriptive_fwd_face": {"note": ("descriptive census only; overlapping "
                                              "windows inflate t; no costs; NOT a "
                                              "strategy claim")},
        }

        # extreme-day sample: top crowd windows (contiguous clusters)
        vc = dec_days["vote_count"]
        for dt in vc.nlargest(8).index:
            facts["g_anchor_face"]["extreme_day_sample"].append({
                "date": str(dt.date()), "votes": int(vc.loc[dt]),
                "weak_share": round(float(dec_days.loc[dt, "weak_share"]), 4),
                "spread": round(float(dec_days.loc[dt, "spread"]), 4),
                "guard_score": round(float(dec_days.loc[dt, "guard_score"]), 4),
            })

        # state machine: asymmetric author-verbatim face (2d out / 3d in)
        facts["state_machine_face"]["asym_verbatim"] = state_machine(
            dec_days, CONFIRM_OUT, CONFIRM_IN, True)
        # symmetric ablation face (2d out / 2d in, no hysteresis):
        # recovery without hysteresis = r3 uses TH_SPREAD itself
        sp = faces["spread"]
        r3_sym = (sp < TH_SPREAD) & decidable
        rec_sym_count = (rec_votes["r1"].astype(int) + rec_votes["r2"].astype(int)
                         + r3_sym.astype(int) + rec_votes["r4"].astype(int))
        faces_sym = faces.copy()
        faces_sym["recover"] = (rec_sym_count >= 3) & decidable
        facts["state_machine_face"]["sym_ablation_2d2d"] = state_machine(
            faces_sym[decidable], CONFIRM_OUT, CONFIRM_OUT, False)

        # F2 D6 signal faces
        below = below_ma20_share(closes)
        b20 = nhnl_b20(closes)
        for label, series in (
            ("weak_share_vs_below_ma20", dec_days["weak_share"]),
            ("vote_count_vs_below_ma20", dec_days["vote_count"]),
            ("weak_share_vs_nhnl_b20", dec_days["weak_share"]),
            ("vote_count_vs_nhnl_b20", dec_days["vote_count"]),
        ):
            ref = below if "below_ma20" in label else b20
            common = series.dropna().index.intersection(ref.dropna().index)
            if len(common) > 100:
                corr = float(np.corrcoef(series.loc[common], ref.loc[common])[0, 1])
            else:
                corr = None
            facts["d6_signal_face"][label] = {
                "n_common_days": int(len(common)),
                "pearson": None if corr is None else round(corr, 4),
                "verdict_note": ("signal-level only; cell-level merge clause "
                                  "remains freeze/judge face per prereg sec.1"),
            }

        # F3 descriptive forward face: crowd day vs non-crowd day
        for h in (5, 20):
            fwd = (ew.shift(-h) / ew - 1.0)
            common = dec_days.index.intersection(fwd.dropna().index)
            on_crowd = fwd.loc[common][dec_days.loc[common, "crowd"]]
            off_crowd = fwd.loc[common][~dec_days.loc[common, "crowd"]]

            def _st(x: pd.Series) -> dict:
                return {"n": int(len(x)), "mean": round(float(x.mean()), 5),
                        "std": round(float(x.std()), 5)}
            facts["descriptive_fwd_face"][f"fwd_{h}d"] = {
                "crowd_day": _st(on_crowd), "non_crowd_day": _st(off_crowd),
                "spread_noncrowd_minus_crowd_mean":
                    round(float(off_crowd.mean() - on_crowd.mean()), 5),
            }

        # F3b guard-object (510300) conditional forward face: the exposure
        # gate's actual bet face -- descriptive census, same honest labels.
        guard_px = closes[GUARD]
        for h in (5, 20):
            g_fwd = (guard_px.shift(-h) / guard_px - 1.0)
            common = dec_days.index.intersection(g_fwd.dropna().index)
            g_on = g_fwd.loc[common][dec_days.loc[common, "crowd"]]
            g_off = g_fwd.loc[common][~dec_days.loc[common, "crowd"]]

            def _stg(x: pd.Series) -> dict:
                return {"n": int(len(x)), "mean": round(float(x.mean()), 5),
                        "std": round(float(x.std()), 5)}
            facts["descriptive_fwd_face"][f"guard_fwd_{h}d"] = {
                "crowd_day": _stg(g_on), "non_crowd_day": _stg(g_off),
                "spread_noncrowd_minus_crowd_mean":
                    round(float(g_off.mean() - g_on.mean()), 5),
            }

        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(facts, f, ensure_ascii=False, indent=1)
        print(json.dumps(facts, ensure_ascii=False, indent=1))
        return 0
    except Exception as exc:  # honest fault, no masking
        import traceback
        traceback.print_exc()
        print(f"PROBE FAULT: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
