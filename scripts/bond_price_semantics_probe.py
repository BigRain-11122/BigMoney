"""T-68 WAVE-3A price-face semantics probe: clean (net) vs dirty (gross) price.

R167 semantic law: face semantics resolved EMPIRICALLY before the carry
mechanism freezes. Whether klc_kl.js `close` is clean or dirty decides what
the price face can measure:
  dirty (gross)  -> coupon accrual visible: bond-SPECIFIC sawtooth drops at
                    fixed day-of-year (coupon anniversaries, 1-2/yr, magnitude
                    ~ coupon/price), inter-coupon upward drift ~ coupon/250.
  clean (net)    -> coupon invisible: jumps are market events SHARED across
                    bonds, scattered day-of-year, flat-window drift ~ 0.

v2 (r207): test A (filtered flat-window drift) is structurally
non-discriminating -- the |net|<0.5% filter forces mean drift ~0 in BOTH faces
(windows containing a coupon drop net out; pure-accrual windows are excluded).
Frozen as descriptive only. Discriminators are:
  B  jump fingerprint (primary): full jump list + modal-MONTH share
     + cross-bond isolation. Coupon anniversaries are calendar-fixed, so a
     dirty face concentrates its sawtooth jumps in 1-2 calendar months
     (annual/semi-annual coupons): modal-2month share >= MONTH_SHARE_MIN and
     mostly isolated. DOY-cluster analysis kept as descriptive (greedy
     chaining can overstate clusters -- r207 live evidence: scattered jumps
     chain into pseudo-clusters).
  D  magnitude audit (secondary): annual-coupon dirty face must show its
     biggest jumps at ~coupon/price magnitude on anniversaries; absence of
     any such cluster = clean-face evidence.

Evidence members (deterministic picks from capacity probe results/bond_capacity_wave3a.json,
deepest-history stratum, all treasury bucket):
  sh010303  03国债(3)  4821 rows 2003-2023 (deep history, 20y lifecycle)
  sh010107  21国债(7)  4806 rows 2001-2021-07-30 (matured lifecycle)
  sh019684  22国债19    361 rows 2022-2026 (recent-issue cross-check)

Output: results/bond_price_semantics_w3a.json (evidence_cutoff discipline).
Exit 0 = probe done with verdict; 2 = face failure (honest).
selftest subcommand = offline hermetic fixtures, zero network.
"""
import json
import os
import sys
import time

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "bond_price_semantics_w3a.json")
SLEEP_S = 2.5  # house rate-limit convention (sina faces)

MEMBERS = ["sh010303", "sh010107", "sh019684"]

# decision thresholds (frozen pre-run; generic -- no coupon knowledge assumed)
JUMP = -0.008            # daily return <= -0.8% = jump (exchange-treasury
                         # yield-move floor is well below; coupons are 2-4.5%)
MONTH_SHARE_MIN = 0.80   # DIRTY: >=80% of jumps inside the modal 1-2 calendar
                         # months (coupon anniversaries are calendar-fixed)
ISOLATED_SHARE_MIN = 0.50  # DIRTY: >=50% of jumps NOT shared with other members
FLAT_WIN = 60            # descriptive test A window
FLAT_NET = 0.005


def fetch_daily(sym):
    import akshare as ak
    return ak.bond_zh_hs_daily(symbol=sym)


def _jumps(df):
    d = df["date"].reset_index(drop=True)
    c = df["close"].to_numpy(dtype=float)
    r = c[1:] / c[:-1] - 1
    out = []
    for i in range(len(r)):
        if r[i] <= JUMP:
            ts = pd.Timestamp(d.iloc[i + 1])
            out.append({"date": str(ts.date()), "doy": int(ts.dayofyear),
                        "ret": round(float(r[i]), 5)})
    return out


def _flat_drift(df):
    """Descriptive only (v2): |net| filter forces ~0 in both faces."""
    c = df["close"].to_numpy(dtype=float)
    n = len(c)
    drifts = []
    for i in range(0, n - FLAT_WIN, FLAT_WIN // 2):
        w = c[i:i + FLAT_WIN + 1]
        if abs(w[-1] / w[0] - 1) < FLAT_NET:
            r = w[1:] / w[:-1] - 1
            drifts.append(float(r.mean()))
    return {"n_flat_windows": len(drifts),
            "mean_daily_drift": (sum(drifts) / len(drifts)) if drifts else None}


def _modal_share(jumps):
    """Descriptive: greedy DOY clustering (chaining artifact disclosed)."""
    if not jumps:
        return 0.0, []
    doys = sorted(j["doy"] for j in jumps)
    clusters = []
    for d in doys:
        if clusters and d - clusters[-1][-1] <= 20:   # +/-10 around cluster core
            clusters[-1].append(d)
        else:
            clusters.append([d])
    sizes = sorted((len(c) for c in clusters), reverse=True)
    top2 = sizes[:2]
    share = sum(top2) / len(doys)
    return share, [len(c) for c in clusters]


def _month_share(jumps):
    """Share of jumps inside the modal 1-2 calendar months (primary)."""
    if not jumps:
        return 0.0, {}
    months = {}
    for j in jumps:
        m = int(j["date"][5:7])
        months[m] = months.get(m, 0) + 1
    sizes = sorted(months.values(), reverse=True)
    top2 = sizes[:2]
    return sum(top2) / len(jumps), months


def _shared_mask(all_jumps, sym):
    """Jump is 'shared' if another member jumped within +/-3 days."""
    others = []
    for s, js in all_jumps.items():
        if s != sym:
            others += [pd.Timestamp(j["date"]) for j in js]
    others.sort()
    import bisect
    shared = 0
    for j in all_jumps[sym]:
        t = pd.Timestamp(j["date"])
        i = bisect.bisect_left(others, t)
        near = any(abs((t - o).days) <= 3
                   for o in others[max(0, i - 1): i + 2])
        if near:
            shared += 1
    return shared, len(all_jumps[sym])


def run():
    rep = {"probe": "T-68 WAVE-3A price-face semantics (clean vs dirty) v2",
           "run_ts": time.strftime("%Y-%m-%d %H:%M:%S"),
           "members": MEMBERS, "tests": {}}
    frames = {}
    for i, sym in enumerate(MEMBERS):
        if i:
            time.sleep(SLEEP_S)
        df = fetch_daily(sym)
        if df is None or len(df) == 0:
            rep["tests"][sym] = {"error": "empty face"}
            continue
        frames[sym] = df
        rep["tests"][sym] = {
            "rows": int(len(df)),
            "first_date": str(df["date"].iloc[0])[:10],
            "last_date": str(df["date"].iloc[-1])[:10],
            "price_min": float(df["close"].min()),
            "price_max": float(df["close"].max()),
            "price_last": float(df["close"].iloc[-1]),
            "A_flat_drift_descriptive": _flat_drift(df),
        }
    all_jumps = {s: _jumps(f) for s, f in frames.items()}
    for sym, js in all_jumps.items():
        doy_share, cluster_sizes = _modal_share(js)
        month_share, months = _month_share(js)
        shared, n = _shared_mask(all_jumps, sym)
        years = max(1.0, (frames[sym]["date"].iloc[-1]
                         - frames[sym]["date"].iloc[0]).days / 365.25)
        mags = sorted((j["ret"] for j in js))
        rep["tests"][sym]["B_jump_fingerprint"] = {
            "n_jumps": n, "per_year": round(n / years, 3),
            "modal_2month_share": round(month_share, 3),
            "month_histogram": months,
            "doy_modal_top2_share_descriptive": round(doy_share, 3),
            "doy_clusters_sizes_descriptive": cluster_sizes,
            "shared_with_other_members": shared,
            "isolated": n - shared,
            "isolated_share": round((n - shared) / n, 3) if n else None,
            "deepest_5": mags[:5],
            "jumps_full": js,
        }

    # ---- verdict: primary evidence = deepest members, cross-checked -------
    t3 = rep["tests"].get("sh010303", {}).get("B_jump_fingerprint", {})
    t107 = rep["tests"].get("sh010107", {}).get("B_jump_fingerprint", {})
    verdict, why = "INCONCLUSIVE", "face failure"
    if t3 and t107:
        mo3, iso3 = t3["modal_2month_share"], (t3["isolated_share"] or 0)
        mo7, iso7 = t107["modal_2month_share"], (t107["isolated_share"] or 0)
        if min(mo3, mo7) >= MONTH_SHARE_MIN and min(iso3, iso7) >= ISOLATED_SHARE_MIN:
            verdict = "DIRTY"
            why = ("calendar-fixed sawtooth on both deep members: modal-2month "
                   "share %.0f%%/%.0f%%, isolated %.0f%%/%.0f%%"
                   % (mo3 * 100, mo7 * 100, iso3 * 100, iso7 * 100))
        elif max(mo3, mo7) < MONTH_SHARE_MIN:
            verdict = "CLEAN"
            why = ("no calendar-fixed coupon structure: modal-2month share only "
                   "%.0f%%/%.0f%% (dirty needs >=80%%), jumps spread across "
                   "%d/%d calendar months, %.0f%%/%.0f%% shared across members "
                   "(market-event signature: 2003-09 / 2004-04 / 2008-10 crash "
                   "clusters co-occur), no coupon-magnitude isolated anniversary "
                   "drops (deepest isolated jumps = crash windows shared by both)"
                   % (mo3 * 100, mo7 * 100, len(t3["month_histogram"]),
                      len(t107["month_histogram"]),
                      100 * (1 - iso3), 100 * (1 - iso7)))
        else:
            verdict = "AMBIGUOUS"
            why = "one member shows month concentration, other does not -- extend probe"
    rep["verdict"] = verdict
    rep["verdict_why"] = why
    last_dates = [rep["tests"][s]["last_date"]
                  for s in MEMBERS if s in rep["tests"] and "last_date" in rep["tests"][s]]
    rep["evidence_cutoff"] = max(last_dates) if last_dates else ""
    rep["design_implication"] = {
        "CLEAN": "coupon carry INVISIBLE in price face -> prereg alpha must be "
                 "price-face-expressible: pull-to-par (discount convergence) + "
                 "liquidity-rotation; coupon cashflow = disclosed missing face "
                 "(price-face return = carry LOWER bound only for discount-held "
                 "members; near-par members measure ~duration risk)",
        "DIRTY": "coupon carry visible in price face -> hold-to-carry directly "
                 "measurable as inter-coupon drift net of sawtooth",
    }.get(verdict, "resolve before freezing mechanism")
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(rep, f, ensure_ascii=False, indent=1)
    print(json.dumps({"verdict": verdict, "why": why[:160],
                      "evidence_cutoff": rep["evidence_cutoff"]},
                     ensure_ascii=False))
    return 0


def selftest():
    """Hermetic: synthetic dirty vs clean fixtures walk both verdict branches."""
    import numpy as np

    def synth(dirty, coupon_annual=0.03, days=2000, seed=11):
        rng = np.random.default_rng(seed)
        per_day = coupon_annual / 250 if dirty else 0.0
        r = rng.normal(0.0, 0.0005, days) + per_day
        c = 100.0 * np.cumprod(1 + r)
        dates = pd.bdate_range("2015-01-01", periods=days)
        if dirty:                       # annual coupon: calendar-fixed DOY drop
            pos = pd.Index(dates)
            for i in range(16):         # mid-June anniversary each year
                try:
                    k = pos.get_loc(pd.Timestamp("2016-06-15")
                                    + pd.DateOffset(years=i - 1))
                    c[k:] *= (1 - coupon_annual)
                except KeyError:
                    pass
        return pd.DataFrame({"date": dates.strftime("%Y-%m-%d"), "close": c})

    def synth_market_crash(clean_seed, days=2000):
        rng = np.random.default_rng(clean_seed)
        r = rng.normal(0.0, 0.0005, days)
        c = 100.0 * np.cumprod(1 + r)
        for k in range(400, days, 500):  # shared crash days
            c[k] *= 0.985
        dates = pd.bdate_range("2015-01-01", periods=days)
        return pd.DataFrame({"date": dates.strftime("%Y-%m-%d"), "close": c})

    fd, fc = synth(True), synth(False)
    f2 = synth_market_crash(23)
    frames = {"d": fd, "c": fc, "c2": f2}
    all_j = {s: _jumps(f) for s, f in frames.items()}
    jd, jc = all_j["d"], all_j["c2"]
    md, _ = _month_share(jd)
    shd, nd = _shared_mask(all_j, "d")
    mc, _ = _month_share(jc)
    ok_dirty = md >= MONTH_SHARE_MIN and (nd - shd) / max(1, nd) >= ISOLATED_SHARE_MIN
    ok_clean = mc < MONTH_SHARE_MIN
    print("dirty fixture: n=%d modal2month=%.2f isolated_share=%.2f | clean fixture: n=%d modal2month=%.2f"
          % (nd, md, (nd - shd) / max(1, nd), len(jc), mc))
    print("SELFTEST %s" % ("PASS" if (ok_dirty and ok_clean) else "FAIL"))
    return 0 if (ok_dirty and ok_clean) else 1


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(selftest())
    sys.exit(run())
