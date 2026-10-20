"""FUND-DIVLOWVOL-P2 burn-face adequacy leg: do we need a split (song-zhuan) event face?

Why this exists
---------------
P2 sec.2.1 residual risk: the local qfq-inversion sidecars model *cash dividends only*.
The signal kernel needs P_raw_close (yield_ttm = ttm_cash / raw_close). If a symbol had a
share split / bonus issue (song-zhuan), the cash-only factor under-corrects and the yield
is wrong on every signal date after that ex-date -- which would poison the whole burn.

The panel carries `amount` (currency) and `volume` (shares), so the day's VWAP
`amount/volume` is a **raw-price proxy**. The residual

    rho_t = close_qfq(t) / vwap_raw(t) / f_cash(t)

is flat by construction except at split events, where it steps by the split ratio.
Monthly-spaced medians of rho therefore expose split events without a split database.

Verdict
-------
ADEQUATE   : zero detected split steps in the judged window -> cash-only sidecar is enough,
             option (B) local-base burn is admissible.
INADEQUATE : split steps detected -> sidecar under-corrects; the detected ratios are emitted
             as a candidate split face (results/fund_divlowvol_p2/split_events_candidate.json)
             so the burn face can be corrected instead of silently wrong.

This is a read-only measurement leg. It never writes data panels and never burns a cell.
"""
from __future__ import annotations

import argparse
import bisect
import hashlib
import json
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PANEL = os.path.join(ROOT, "data", "cache", "p1c_local")
SIDECARS = os.path.join(ROOT, "data", "cache", "p1c_sidecars")
OUT_DIR = os.path.join(ROOT, "results", "fund_divlowvol_p2")
RECEIPT = os.path.join(OUT_DIR, "split_adequacy.json")

CUTOFF = "2026-09-22"          # prereg sec.2 D2 lockbox anchor
STEP_UP = 1.15                 # rho step up  >= +15%  -> split/bonus issue
STEP_DOWN = 1.0 / 1.15         # rho step down <= -13% -> consolidation
MIN_MONTHS = 24                # symbol needs this many monthly rho points to be judged
LEVEL_TOL = 0.05               # |median rho - 1| tolerated before the sidecar is deemed short


def _load_panel():
    fields = {}
    for f in ("close", "amount", "volume", "dates"):
        p = os.path.join(PANEL, f + ".npy")
        if not os.path.exists(p):
            raise SystemExit("panel field missing: " + p)
        fields[f] = np.load(p, mmap_mode="r")
    with open(os.path.join(PANEL, "symbols.json"), "r", encoding="utf-8") as fh:
        symbols = json.load(fh)
    return fields, symbols


def _load_factor(dates_yyyymmdd, sym):
    p = os.path.join(SIDECARS, sym + ".factor.json")
    if not os.path.exists(p):
        return None
    try:
        with open(p, "r", encoding="utf-8") as fh:
            obj = json.load(fh)
    except Exception:
        return None
    d = obj.get("d") or []
    f = obj.get("f") or []
    if not d or not f:
        return None
    return d, f


def _f_series(d, f, t_int):
    """Vectorised cash-only factor at each date (step lookup, same law as sidecar_f_at)."""
    if not d:
        return np.ones(len(t_int), dtype=np.float64)
    idx = np.searchsorted(np.asarray(d), t_int, side="right") - 1
    arr = np.asarray(f, dtype=np.float64)
    out = np.where(idx < 0, arr[0], arr[np.clip(idx, 0, len(arr) - 1)])
    return out


def _yyyymmdd(raw_dates):
    """Panel date axis is int64 epoch (this panel: microseconds) -> YYYYMMDD ints."""
    import pandas as pd
    raw = np.asarray(raw_dates).astype(np.int64)
    med = float(np.median(raw)) if len(raw) else 0.0
    unit = "ns" if med > 1e17 else ("us" if med > 1e13 else "ms")
    dt = pd.to_datetime(raw, unit=unit)
    return dt.strftime("%Y%m%d").astype(np.int64).values


def _level_ratio(rho, k, back=3, fwd=3):
    """Persistent level change across a detected step (smoothing-robust split ratio)."""
    lo = max(0, k - back + 1)
    hi = min(len(rho), k + 1 + fwd)
    before = float(np.median(rho[lo:k + 1]))
    after = float(np.median(rho[k + 1:hi]))
    if before <= 0 or after <= 0:
        return float("nan")
    return before / after


def _month_points(dates_int, cutoff_int):
    """Positions of the last bar in each calendar month, strictly <= cutoff."""
    pos = []
    seen = set()
    for i in range(len(dates_int) - 1, -1, -1):
        t = int(dates_int[i])
        if t > cutoff_int:
            continue
        key = t // 100
        if key in seen:
            continue
        seen.add(key)
        pos.append(i)
    pos.reverse()
    return np.asarray(pos, dtype=np.int64)


def run(basis_notice: str = "") -> int:
    fields, symbols = _load_panel()
    close = fields["close"]
    amount = fields["amount"]
    volume = fields["volume"]
    dates_int = _yyyymmdd(fields["dates"])

    cutoff_int = int(CUTOFF.replace("-", ""))
    mpos = _month_points(dates_int, cutoff_int)
    if len(mpos) < MIN_MONTHS:
        raise SystemExit("not enough monthly points: %d" % len(mpos))

    n_syms = len(symbols)
    n_months = len(mpos)
    events = []
    judged = 0
    skipped_no_sidecar = 0
    skipped_thin = 0
    sym_levels = []

    for j in range(n_syms):
        sym = symbols[j]
        sc = _load_factor(dates_int, sym)
        if sc is None:
            skipped_no_sidecar += 1
            continue
        c = np.asarray(close[mpos, j], dtype=np.float64)
        am = np.asarray(amount[mpos, j], dtype=np.float64)
        vo = np.asarray(volume[mpos, j], dtype=np.float64)
        t_int = dates_int[mpos]
        ok = (c > 0) & (am > 0) & (vo > 0) & np.isfinite(c) & np.isfinite(am) & np.isfinite(vo)
        if int(ok.sum()) < MIN_MONTHS:
            skipped_thin += 1
            continue
        vwap = am[ok] / vo[ok]
        f = _f_series(sc[0], sc[1], t_int[ok])
        # close is qfq (older prices scaled by 1/F) while amount/volume is raw:
        #   close_q / vwap_raw == 1/F  ->  rho = (close_q / vwap_raw) * f_cash
        # is 1.0 everywhere the cash-only factor f_cash explains the whole adjustment F.
        # Any step in rho is an adjustment event the cash sidecar does not model (song-zhuan).
        rho = c[ok] / vwap * f
        tt = t_int[ok]

        # median-of-3 smoothing on rho kills single-day VWAP/close noise.
        if len(rho) >= 3:
            kern = np.array([0.5, 1.0, 0.5])
            rs = np.convolve(rho, kern / kern.sum(), mode="same")
            rs[0], rs[-1] = rho[0], rho[-1]
        else:
            rs = rho
        judged += 1
        sym_levels.append(float(np.median(rs)))
        step = rs[:-1] / np.where(rs[1:] == 0, np.nan, rs[1:])
        hit = np.where((step >= STEP_UP) | (step <= STEP_DOWN))[0]
        for k in hit:
            lr = _level_ratio(rho, int(k))
            events.append({
                "sym": sym,
                "from_date": str(int(tt[k])),
                "to_date": str(int(tt[k + 1])),
                "rho_prev": round(float(rs[k]), 6),
                "rho_next": round(float(rs[k + 1]), 6),
                "step_sample": round(float(step[k]), 6),
                "implied_ratio": (round(lr, 6) if np.isfinite(lr) else None),
            })

    n_ev = len(events)
    affected = len({e["sym"] for e in events})
    share = (affected / judged) if judged else 0.0
    levels = np.asarray(sym_levels, dtype=np.float64)
    levels = levels[np.isfinite(levels) & (levels > 0)]
    level_median = float(np.median(levels)) if len(levels) else float("nan")
    off_level = int((np.abs(levels - 1.0) > LEVEL_TOL).sum()) if len(levels) else 0
    off_share = (off_level / len(levels)) if len(levels) else 0.0

    # The level test is the decisive one: rho == 1.0 everywhere iff the cash-only factor
    # explains the entire qfq adjustment. Levels far from 1 mean the panel's qfq was
    # reversed with a *larger* factor than cash dividends alone (song-zhuan present).
    sidecar_ok = (level_median is not None and np.isfinite(level_median)
                  and abs(level_median - 1.0) <= LEVEL_TOL and share <= LEVEL_TOL)
    adequate = bool(sidecar_ok and n_ev == 0)

    os.makedirs(OUT_DIR, exist_ok=True)
    cand_path = os.path.join(OUT_DIR, "split_events_candidate.json")
    if n_ev:
        with open(cand_path, "w", encoding="utf-8") as fh:
            json.dump({"cutoff": CUTOFF, "n_events": n_ev, "events": events}, fh,
                      ensure_ascii=False, indent=1)

    receipt = {
        "leg": "split_adequacy",
        "batch": "FUND-DIVLOWVOL-P2",
        "evidence_cutoff": CUTOFF,
        "method": "rho = close_qfq / (amount/volume) / f_cash; monthly medians; step test",
        "basis_notice": basis_notice,
        "thresholds": {"step_up": STEP_UP, "step_down": round(STEP_DOWN, 6),
                       "min_months": MIN_MONTHS},
        "panel": {"symbols": n_syms, "months": n_months,
                  "first_month": str(int(dates_int[mpos[0]])),
                  "last_month": str(int(dates_int[mpos[-1]]))},
        "judged_symbols": judged,
        "skipped_no_sidecar": skipped_no_sidecar,
        "skipped_thin": skipped_thin,
        "split_events": n_ev,
        "affected_symbols": affected,
        "affected_share": round(share, 6),
        "level_test": {
            "rho_median": (round(level_median, 6) if np.isfinite(level_median) else None),
            "tolerance": LEVEL_TOL,
            "symbols_off_level": off_level,
            "off_level_share": round(off_share, 6),
        },
        "candidate_face": (os.path.relpath(cand_path, ROOT) if n_ev else None),
        "verdict": "ADEQUATE" if adequate else "INADEQUATE_FOR_CASH_ONLY_SIDECAR",
        "recommended_route": ("qm_raw_from_sidecar" if adequate else "vwap_raw_proxy"),
        "reading": (
            "rho == 1 across the judged universe: cash-only sidecar reconstructs raw close, "
            "so the burn may use P_raw = qfq * f_cash"
            if adequate else
            "rho level far from 1.0 and/or split steps present: the panel qfq was reversed "
            "with a larger factor than cash dividends (song-zhuan missing). Do NOT reconstruct "
            "P_raw as qfq*f_cash. Use the raw-price proxy P_raw = amount/volume on signal dates "
            "(option B with vwap route), or take option A (p1c re-delivery) which carries the "
            "provider's full adjustment factor."
        ),
        "machine": "bm-b",
    }
    with open(RECEIPT, "w", encoding="utf-8") as fh:
        json.dump(receipt, fh, ensure_ascii=False, indent=1)
    print(json.dumps({k: receipt[k] for k in
                      ("verdict", "split_events", "affected_symbols", "affected_share",
                       "judged_symbols", "split_events", "basis_notice")},
                     ensure_ascii=False))
    print("receipt=" + os.path.relpath(RECEIPT, ROOT))
    return 0


def selftest() -> int:
    """Offline leg: synthetic rho with one split must be detected; flat rho must not."""
    legs = []

    def check(name, cond):
        legs.append((name, bool(cond)))

    # synthetic panel: 30 months, one split at t=15 (rho steps 2x)
    rho = np.ones(30)
    rho[15:] *= 2.0
    kern = np.array([0.5, 1.0, 0.5])
    rs = np.convolve(rho, kern / kern.sum(), mode="same")
    rs[0], rs[-1] = rho[0], rho[-1]
    step = rs[:-1] / rs[1:]
    hit = np.where((step >= STEP_UP) | (step <= STEP_DOWN))[0]
    check("sel1 split detected", len(hit) >= 1)
    # implied_ratio = raw-price divisor: a 2-for-1 split gives 0.5 (1 share -> 2 shares)
    check("sel2 split ratio approx 0.5", abs(_level_ratio(rho, int(hit[0])) - 0.5) < 0.05)

    flat = np.ones(30) * 1.0003
    rs2 = np.convolve(flat, kern / kern.sum(), mode="same")
    rs2[0], rs2[-1] = flat[0], flat[-1]
    step2 = rs2[:-1] / rs2[1:]
    hit2 = np.where((step2 >= STEP_UP) | (step2 <= STEP_DOWN))[0]
    check("sel3 flat rho no event", len(hit2) == 0)

    # consolidation (reverse split) direction
    rho3 = np.ones(30)
    rho3[15:] *= 0.4
    rs3 = np.convolve(rho3, kern / kern.sum(), mode="same")
    rs3[0], rs3[-1] = rho3[0], rho3[-1]
    step3 = rs3[:-1] / rs3[1:]
    hit3 = np.where((step3 >= STEP_UP) | (step3 <= STEP_DOWN))[0]
    check("sel4 consolidation detected", len(hit3) >= 1)

    # step lookup kernel
    d = [20000101, 20100101, 20200101]
    f = [1.0, 1.1, 1.25]
    got = _f_series(d, f, np.array([19991231, 20000101, 20150101, 20200101]))
    check("sel5 f_series step law",
          abs(got[0] - 1.0) < 1e-12 and abs(got[1] - 1.0) < 1e-12
          and abs(got[2] - 1.1) < 1e-12 and abs(got[3] - 1.25) < 1e-12)
    check("sel6 empty sidecar = 1.0", abs(_f_series([], [], np.array([20200101]))[0] - 1.0) < 1e-12)

    # month point picker: last bar per month, nothing after cutoff
    dates = np.array([20200102, 20200131, 20200203, 20200228, 20200330, 20200401])
    mp = _month_points(dates, 20200331)
    check("sel7 month points <= cutoff", int(dates[mp][-1]) == 20200330)
    check("sel8 one point per month", len(mp) == 3)

    bad = [n for n, ok in legs if not ok]
    print(json.dumps({"legs": len(legs), "pass": len(legs) - len(bad), "fail": bad}))
    return 0 if not bad else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="P2 split adequacy leg")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--basis-notice", default="")
    sub.add_parser("selftest")
    args = ap.parse_args(argv)
    if args.cmd == "selftest":
        return selftest()
    return run(args.basis_notice)


if __name__ == "__main__":
    sys.exit(main())