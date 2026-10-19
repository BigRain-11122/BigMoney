"""Suspension / resume event census (exploratory, zero judged claims).

Product purpose: A-share folklore treats "停牌复牌" (suspension then resumption)
as a tradable event ("复牌首日一字板" / "重组复牌暴涨"). Nothing in this repo has
ever measured the *resumption* face on the local panel with a cost-bearing,
market-adjusted read. This census produces that measured prior so the next trial
batch (supply-floor leg) can be registered against numbers instead of a slogan.

Face discipline:
  * panel = data/cache/p1c_local (qfq, cutoff 2026-10-19). A "missing bar" on an
    already-listed symbol is read as a suspension/suspension-like halt; the panel
    has no official halt flag, so this is a proxy and is disclosed as such.
  * event = first valid bar after >= MIN_SPELL consecutive missing sessions.
  * measures, all market-adjusted by the same-day cross-sectional median:
      gap      = open(resume) / close(last bar before the spell) - 1
      ret1     = close(resume) / open(resume) - 1        (intraday, tradable)
      ret5     = close(resume+4) / close(resume) - 1
      ret20    = close(resume+19) / close(resume) - 1
    net measures subtract round-trip cost (2 sides x ce_transfer.COST_X1_RATE).
  * survival bias is structural and stated: symbols that never resumed are simply
    absent from the panel axis. Long halts mostly end in either a reorganisation
    pump or a delisting, and only the former stays tradeable here -> the long-spell
    numbers are an UPPER bound, not an expectation.
  * zero judged lines, zero prereg gates, zero pool writes.

Usage:
  python scripts/susp_resume_census.py            # run census -> results/susp_resume_census/
  python scripts/susp_resume_census.py --selftest # offline math self-test
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from div_event_census import window_stats  # single source: same stats kernel

PANEL = os.path.join(ROOT, "data", "cache", "p1c_local")
OUT_DIR = os.path.join(ROOT, "results", "susp_resume_census")

MIN_SPELL = 20                      # trading sessions of missing bars
SPELL_BUCKETS = [(20, 59), (60, 119), (120, 10 ** 6)]
ERAS = [(1990, 2009), (2010, 2015), (2016, 2020), (2021, 2099)]
RET_HORIZONS = (1, 5, 20)


# ------------------------------------------------------------------ panel math
def missing_runs(valid: np.ndarray) -> np.ndarray:
    """For every row i, count consecutive missing bars ending at i (0 if valid)."""
    cum_missing = np.cumsum(~valid, axis=0).astype(np.int64)
    last_valid_cum = np.maximum.accumulate(np.where(valid, cum_missing, -1), axis=0)
    run = cum_missing - last_valid_cum
    run[~np.isfinite(run)] = 0
    return np.maximum(run, 0)


def ffill_valid_close(close: np.ndarray, valid: np.ndarray) -> np.ndarray:
    """Last valid close at or before each row (NaN before the first valid bar)."""
    idx = np.where(valid, np.arange(close.shape[0])[:, None], -1)
    idx = np.maximum.accumulate(idx, axis=0)
    safe = np.maximum(idx, 0)
    out = np.take_along_axis(close, safe, axis=0)
    out[idx < 0] = np.nan
    return out


def detect_events(close: np.ndarray, min_spell: int = MIN_SPELL):
    """Return (rows, cols) of resume bars: valid bar after >= min_spell missing."""
    valid = np.isfinite(close) & (close > 0)
    run = missing_runs(valid)
    prev_run = np.zeros_like(run)
    prev_run[1:] = run[:-1]
    first_valid = np.where(valid.any(axis=0), valid.argmax(axis=0), -1)
    rows, cols = np.nonzero(valid & (prev_run >= min_spell))
    keep = rows > first_valid[cols]
    return rows[keep], cols[keep], valid


def market_median(x: np.ndarray) -> np.ndarray:
    """Per-row cross-sectional median (all-NaN rows -> NaN)."""
    with np.errstate(all="ignore"):
        return np.nanmedian(x, axis=1)


def cost_roundtrip() -> float:
    try:
        from ce_transfer import COST_X1_RATE
        return 2.0 * float(COST_X1_RATE)
    except Exception:                                  # pragma: no cover
        return 2.0 * 0.0013041


def build_measures(open_, close, valid, rows, cols):
    """Event-level measures, each net of the same-day market median."""
    ffclose = ffill_valid_close(close, valid)
    prev_close = np.full(close.shape, np.nan)
    prev_close[1:] = ffclose[:-1]

    gap_raw = open_ / prev_close - 1.0
    ret1_raw = close / open_ - 1.0
    gap_mkt = market_median(gap_raw)
    ret1_mkt = market_median(ret1_raw)

    out = {
        "gap": gap_raw[rows, cols] - gap_mkt[rows],
        "ret1": ret1_raw[rows, cols] - ret1_mkt[rows],
    }
    for h in RET_HORIZONS[1:]:
        raw = np.full(close.shape, np.nan)
        if h < close.shape[0]:
            raw[:-h] = close[h:] / close[:-h] - 1.0
        raw[~np.isfinite(raw)] = np.nan
        raw[np.abs(raw) > 5.0] = np.nan
        out[f"ret{h}"] = raw[rows, cols] - market_median(raw)[rows]
    return out


def bucketize(rows, cols, dates, spells):
    years = np.array([int(str(d)[:4]) for d in dates], dtype=np.int64)[rows]
    spell_b = np.select(
        [spells < SPELL_BUCKETS[1][0], spells < SPELL_BUCKETS[2][0]],
        ["20-59", "60-119"], default="120+")
    era = np.select(
        [years <= ERAS[1][1], years <= ERAS[2][1], years <= ERAS[3][1]],
        ["<=2015", "2016-2020", "2021+"], default="?").astype(object)
    return years, spell_b, era


# ------------------------------------------------------------------ selftest
def selftest() -> int:
    cases = []

    # 1. missing-run counter on a hand-built mask
    valid = np.array([[1], [1], [0], [0], [0], [1], [1], [0], [1]], dtype=bool)
    run = missing_runs(valid)[:, 0]
    cases.append(("run_counts", list(run) == [0, 0, 1, 2, 3, 0, 0, 1, 0]))

    # 2. resume detection respects min_spell
    close = np.array([[10.0], [10.5], [np.nan], [np.nan], [np.nan],
                      [12.0], [12.5], [np.nan], [13.0]])
    rows, cols, v = detect_events(close, min_spell=2)
    cases.append(("detect_2plus", list(rows) == [5] and list(cols) == [0]))
    rows3, _, _ = detect_events(close, min_spell=3)
    cases.append(("detect_3plus", list(rows3) == [5]))
    rows4, _, _ = detect_events(close, min_spell=4)
    cases.append(("detect_4plus_none", len(rows4) == 0))

    # 3. first-bar-after-listing is not a resume event
    close2 = np.array([[np.nan], [np.nan], [9.0], [9.2]])
    r2, _, _ = detect_events(close2, min_spell=1)
    cases.append(("no_listing_event", len(r2) == 0))

    # 4. forward-filled close = last valid bar at or before the row
    ff = ffill_valid_close(close, np.isfinite(close) & (close > 0))
    cases.append(("ffill", ff[4, 0] == 10.5 and ff[3, 0] == 10.5 and ff[8, 0] == 13.0))

    # 5/6. single-symbol panel self-neutralises the market median, so the
    #      adjusted measures must collapse to zero while the raw legs are non-zero
    open_ = np.where(np.isfinite(close), close, np.nan).copy()
    open_[5, 0] = 11.55
    m = build_measures(open_, close, np.isfinite(close) & (close > 0), rows, cols)
    cases.append(("self_neutral", abs(float(m["gap"][0])) < 1e-12
                  and abs(float(m["ret1"][0])) < 1e-12
                  and abs(11.55 / 10.5 - 1.0) > 1e-3
                  and abs(12.0 / 11.55 - 1.0) > 1e-2))

    # 7. two-symbol panel keeps the residual against the cross-sectional median
    close2s = np.array([[10.0, 10.0], [np.nan, 10.2], [11.0, 10.15]])
    open2s = np.array([[10.0, 10.0], [np.nan, 10.2], [11.0, 10.15]])
    v2 = np.isfinite(close2s) & (close2s > 0)
    r2s, c2s, _ = detect_events(close2s, min_spell=1)
    m2 = build_measures(open2s, close2s, v2, r2s, c2s)
    cases.append(("market_residual", len(r2s) == 1 and float(r2s[0]) == 2
                  and abs(float(m2["gap"][0]) - (11.0 / 10.0 - 1.0 -
                          np.median([11.0 / 10.0 - 1.0, 10.15 / 10.2 - 1.0]))) < 1e-9))

    # 7. market median subtracts the same-day cross-sectional median
    x = np.array([[1.0, 3.0], [2.0, np.nan]])
    med = market_median(x)
    cases.append(("median", med[0] == 2.0 and med[1] == 2.0))

    # 8. window_stats stays the div census kernel (shared source, not a copy)
    st = window_stats(np.array([1.0, 2.0, 3.0]))
    cases.append(("stats_kernel", st["n"] == 3 and st["mean"] == 2.0))

    # 9. cost is two sides of one frozen constant
    cr = cost_roundtrip()
    cases.append(("cost_roundtrip", abs(cr - 2 * 0.0013041) < 1e-9))

    # 10. bucket edges line up (20/59 | 60/119 | 120+)
    _, sb, _ = bucketize(np.array([0, 0, 0]), np.array([0, 0, 0]),
                         ["2020-01-01"], np.array([20, 60, 120]))
    cases.append(("spell_buckets", list(sb) == ["20-59", "60-119", "120+"]))

    fails = [n for n, ok in cases if not ok]
    for n, ok in cases:
        print(f"  [{'PASS' if ok else 'FAIL'}] {n}")
    print(f"selftest: {len(cases) - len(fails)}/{len(cases)} PASS")
    return 0 if not fails else 1


# ------------------------------------------------------------------ run
def run() -> int:
    t0 = time.time()
    meta = json.load(open(os.path.join(PANEL, "meta.json"), encoding="utf-8"))
    close = np.load(os.path.join(PANEL, "close.npy"))
    open_ = np.load(os.path.join(PANEL, "open.npy"))
    raw_dates = np.load(os.path.join(PANEL, "dates.npy"), allow_pickle=True)
    # axis is int64 microseconds since epoch -> normalise to YYYY-MM-DD
    dates = [str(np.datetime_as_string(np.datetime64(int(d), "us"), unit="D"))
             for d in raw_dates]

    rows, cols, valid = detect_events(close)
    if rows.size == 0:
        print("no resume events found")
        return 1

    run_len = missing_runs(valid)
    spells = run_len[rows - 1, cols]
    years, spell_b, era = bucketize(rows, cols, dates, spells)
    meas = build_measures(open_, close, valid, rows, cols)
    cost = cost_roundtrip()

    def face(slice_mask):
        d = {"n": int(slice_mask.sum())}
        for k, arr in meas.items():
            sub = arr[slice_mask]
            if k in ("ret1", "ret5", "ret20"):
                sub = sub - cost
            d[k] = window_stats(sub)
        return d

    all_mask = np.ones(rows.size, dtype=bool)
    face_all = face(all_mask)

    by_cell = []
    for e in ["<=2015", "2016-2020", "2021+"]:
        for b in ["20-59", "60-119", "120+"]:
            m = (era == e) & (spell_b == b)
            if int(m.sum()) == 0:
                continue
            f = face(m)
            by_cell.append({"era": e, "spell": b, "n": f["n"],
                            "gap_mean": f["gap"]["mean"], "gap_win": f["gap"]["win_rate"],
                            "gap_t": f["gap"]["t"],
                            "ret1_net_mean": f["ret1"]["mean"], "ret1_win": f["ret1"]["win_rate"],
                            "ret5_net_mean": f["ret5"]["mean"], "ret5_win": f["ret5"]["win_rate"],
                            "ret20_net_mean": f["ret20"]["mean"], "ret20_win": f["ret20"]["win_rate"]})

    by_spell = []
    for b in ["20-59", "60-119", "120+"]:
        m = spell_b == b
        if int(m.sum()) == 0:
            continue
        f = face(m)
        by_spell.append({"spell": b, "n": f["n"],
                         "gap_mean": f["gap"]["mean"], "gap_win": f["gap"]["win_rate"],
                         "ret1_net_mean": f["ret1"]["mean"], "ret1_win": f["ret1"]["win_rate"],
                         "ret5_net_mean": f["ret5"]["mean"], "ret5_win": f["ret5"]["win_rate"],
                         "ret20_net_mean": f["ret20"]["mean"], "ret20_win": f["ret20"]["win_rate"]})

    # second pass: 5-19 session halts. Post-2018 CSRC rules cap most halts well
    # under 20 sessions, so the >=20 face is nearly extinct in the current era and
    # would otherwise report "no data" for the era that matters.
    srows, scols, _ = detect_events(close, min_spell=5)
    srun = missing_runs(valid)[srows - 1, scols]
    short_mask = (srun >= 5) & (srun < MIN_SPELL)
    srows, scols = srows[short_mask], scols[short_mask]
    short_face = []
    if srows.size:
        smeas = build_measures(open_, close, valid, srows, scols)
        syears = np.array([int(dates[int(r)][:4]) for r in srows])
        s_era = np.select([syears <= 2015, syears <= 2020],
                          ["<=2015", "2016-2020"], default="2021+").astype(object)
        for e in ["<=2015", "2016-2020", "2021+"]:
            m = s_era == e
            if int(m.sum()) == 0:
                continue
            d = {"era": e, "spell": "5-19", "n": int(m.sum())}
            for k, arr in smeas.items():
                sub = arr[m] - (cost if k != "gap" else 0.0)
                st = window_stats(sub)
                d[f"{k}_mean" if k == "gap" else f"{k}_net_mean"] = st["mean"]
                d[f"{k}_win"] = st["win_rate"]
            short_face.append(d)

    os.makedirs(OUT_DIR, exist_ok=True)
    face_obj = {
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "evidence_cutoff": meta.get("cutoff"),
        "panel": "data/cache/p1c_local",
        "panel_shape": meta.get("shape"),
        "min_spell_sessions": MIN_SPELL,
        "cost_roundtrip_rate": round(cost, 8),
        "market_adjust": "same-day cross-sectional median (equal-weight proxy)",
        "n_events": int(rows.size),
        "n_symbols": int(len(set(cols.tolist()))),
        "n_dates": len(set(dates[int(r)] for r in rows[:200000])),
        "face_all": face_all,
        "by_spell": by_spell,
        "by_era_spell": by_cell,
        "short_halt_5_19_by_era": short_face,
        "disclosures": [
            "missing bar is a proxy for halt: the panel carries no official suspension flag",
            "survival bias: symbols that never resumed are absent from the axis; long-spell rows are an upper bound",
            "qfq back-adjustment makes old-era absolute levels not directly comparable across corporate-action regimes",
            "ret1 is tradable only if the resume bar is not sealed at the limit (unmeasurable here, disclosed)",
        ],
    }
    with open(os.path.join(OUT_DIR, f"CENSUS-{meta.get('cutoff')}.json"), "w", encoding="utf-8") as fh:
        json.dump(face_obj, fh, ensure_ascii=False, indent=1)

    csv_path = os.path.join(OUT_DIR, f"by-era-spell-{meta.get('cutoff')}.csv")
    with open(csv_path, "w", encoding="utf-8") as fh:
        fh.write("era,spell,n,gap_mean,gap_win,gap_t,ret1_net_mean,ret1_win,"
                 "ret5_net_mean,ret5_win,ret20_net_mean,ret20_win\n")
        for r in by_cell:
            fh.write(f"{r['era']},{r['spell']},{r['n']},{r['gap_mean']},{r['gap_win']},"
                     f"{r['gap_t']},{r['ret1_net_mean']},{r['ret1_win']},"
                     f"{r['ret5_net_mean']},{r['ret5_win']},"
                     f"{r['ret20_net_mean']},{r['ret20_win']}\n")

    print(json.dumps({"n_events": int(rows.size),
                      "n_symbols": face_obj["n_symbols"],
                      "face_all_gap": face_all["gap"],
                      "face_all_ret1_net": face_all["ret1"],
                      "face_all_ret5_net": face_all["ret5"],
                      "face_all_ret20_net": face_all["ret20"],
                      "elapsed_s": round(time.time() - t0, 1),
                      "out": os.path.join(OUT_DIR, f"CENSUS-{meta.get('cutoff')}.json")},
                     ensure_ascii=False))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    return run()


if __name__ == "__main__":
    sys.exit(main())