"""P-1c Stage A: stock-pool consolidated cache build (P1C_STOCK_IC.md SS5).

One-time I/O leg: MONEY02 bars parquet (5222, raw prices) + factor.json
sidecars (cumulative adjustment, f(latest)=1.0) -> float32 memmap cache at
Money02/data/cache/p1c_stock/ (gitignored, regenerable from bars).

Adj convention: bars parquet prices are ALREADY qfq-adjusted (verified by the
event-day gate: bar close day-over-day return == pct_chg on adjustment dates);
factor.json sidecar is reference metadata only and is NOT applied (first
build attempt divided again = double-adjustment, caught by the pre-run gate).
Built-in pre-run gates (SS2): event-day bar return vs pct_chg (<=0.5%),
random re-read equivalence (rel 1e-5), STAR/CDR sanity gate (688xxx/689xxx
bars store volume AND amount both at 100x real units -- turnover anchor
volume/100/osh == stored turnover, vwap anchor amount/volume == close on all
years; build normalizes both to real units, vwap invariant).
Cache is pure data engineering: zero statistical trials, ledger N unchanged.
"""
import glob
import json
import os
import sys
import time

import numpy as np
import pandas as pd
from concurrent.futures import ProcessPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BARS_DIR = os.path.join(ROOT, "Money02", "data", "bars")
CACHE_DIR = os.path.join(ROOT, "Money02", "data", "cache", "p1c_stock")
ADJ_FIELDS = ["open", "high", "low", "close", "vwap"]     # divided by f(t)
RAW_FIELDS = ["volume", "amount", "turnover", "pct_chg"]  # scale-free / official
FIELDS = ADJ_FIELDS + RAW_FIELDS
MIN_ROWS = 250
# O-1738/O-2345 compute policy: workers = min(25, floor(cores*0.8))
WORKERS = min(25, max(1, os.cpu_count() * 4 // 5))
BATCHES = 50  # symbol batches per worker task (memmaps opened once per batch)


def _dates_only(path):
    df = pd.read_parquet(path, columns=["date"])
    return df["date"].values.astype("int64"), len(df)


def _build_batch(args):
    """Open 9 memmaps once, write all symbols of this batch at their columns."""
    items, calendar_int64 = args
    maps = {n: np.load(os.path.join(CACHE_DIR, n + ".npy"), mmap_mode="r+")
            for n in FIELDS}
    out = []
    for path, sym_idx in items:
        sym = os.path.basename(path)[:-8]
        try:
            df = pd.read_parquet(path)
        except Exception as ex:
            out.append((sym, "read_error", f"{type(ex).__name__}"))
            continue
        if len(df) < MIN_ROWS:
            out.append((sym, "short_history", str(len(df))))
            continue
        df = df.sort_values("date").reset_index(drop=True)
        side = os.path.splitext(path)[0] + ".factor.json"
        try:
            with open(side, "r", encoding="utf-8") as f:
                sj = json.load(f)
            ev = np.array([np.datetime64(x, "us").astype("int64") for x in sj["d"]])
            fv = np.array(sj["f"], dtype="float64")
        except Exception as ex:
            out.append((sym, "sidecar_error", f"{type(ex).__name__}"))
            continue
        dates = df["date"].values.astype("int64")
        pos = np.searchsorted(calendar_int64, dates)
        vol = df["volume"].to_numpy(float)
        amt = df["amount"].to_numpy(float)
        if sym.startswith("688") or sym.startswith("689"):
            # STAR-board/CDR bars store volume AND amount both at 100x real
            # units (anchors, verified per-year on 688001/688008/688981/689009:
            # volume/100/osh == stored turnover  AND  amount/volume == close,
            # so amount is co-inflated and vwap=amount/volume is invariant).
            # Normalize both to real units AT BUILD so downstream consumers
            # are cross-sectionally comparable; vwap unchanged by construction.
            vol = vol / 100.0
            amt = amt / 100.0
        with np.errstate(invalid="ignore", divide="ignore"):
            vwap = np.where(vol > 0, amt / vol, np.nan)
        # bars are already qfq-adjusted (event-day gate proves it): cache as-is
        cols = {
            "open": df["open"].to_numpy(float),
            "high": df["high"].to_numpy(float),
            "low": df["low"].to_numpy(float),
            "close": df["close"].to_numpy(float),
            "vwap": vwap,
            "volume": vol,
            "amount": amt,
            "turnover": df["turnover"].to_numpy(float),
            "pct_chg": df["pct_chg"].to_numpy(float),
        }
        for name in FIELDS:
            maps[name][pos, sym_idx] = cols[name].astype(np.float32)
        out.append((sym, "ok", str(len(df))))
    for m in maps.values():
        m.flush()
    return out


def _validate(ok_syms, all_files, calendar_int64):
    """Pre-run gates: event-day bar return vs pct_chg + random re-read."""
    rng = np.random.default_rng(20260923)
    ev_report, max_dev = [], 0.0
    picks = [ok_syms[0], ok_syms[len(ok_syms) // 2], ok_syms[-1]]
    for sym in picks:
        path = os.path.join(BARS_DIR, sym + ".parquet")
        df = pd.read_parquet(path).sort_values("date").reset_index(drop=True)
        with open(os.path.splitext(path)[0] + ".factor.json",
                  encoding="utf-8") as f:
            sj = json.load(f)
        ev = np.array([np.datetime64(x, "us").astype("int64") for x in sj["d"]])
        dates = df["date"].values.astype("int64")
        close = df["close"].to_numpy(float)
        pct = df["pct_chg"].to_numpy(float)
        evd = np.searchsorted(dates, ev[1:], side="right") - 1
        cand = [(e, i) for e, i in zip(ev[1:], evd)
                if 0 < i < len(df) and dates[i] == e][-5:]
        checked = 0
        for _e, i in cand:
            dev = abs((close[i] / close[i - 1] - 1.0) * 100.0 - pct[i])
            max_dev = max(max_dev, dev)
            checked += 1
        ev_report.append({"sym": sym, "events_checked": checked})
    close_cache = np.load(os.path.join(CACHE_DIR, "close.npy"), mmap_mode="r")
    sym_pos = {os.path.basename(p)[:-8]: i for i, p in enumerate(all_files)}
    recheck = []
    for sym in rng.choice(ok_syms, size=3, replace=False):
        path = os.path.join(BARS_DIR, sym + ".parquet")
        df = pd.read_parquet(path).sort_values("date").reset_index(drop=True)
        dates = df["date"].values.astype("int64")
        ref = df["close"].to_numpy(float)
        pos = np.searchsorted(calendar_int64, dates)
        got = np.asarray(close_cache[pos, sym_pos[sym]], dtype=float)
        m = np.isfinite(ref) & np.isfinite(got)
        rel = np.nanmax(np.abs(got[m] - ref[m]) / np.maximum(np.abs(ref[m]), 1e-9))
        recheck.append({"sym": sym, "max_rel_err": float(rel)})
    # STAR/CDR gate: vwap near price level AND volume/amount normalized to
    # real units (raw bars store both at 100x for 688xxx/689xxx)
    vwap_cache = np.load(os.path.join(CACHE_DIR, "vwap.npy"), mmap_mode="r")
    vol_cache = np.load(os.path.join(CACHE_DIR, "volume.npy"), mmap_mode="r")
    amt_cache = np.load(os.path.join(CACHE_DIR, "amount.npy"), mmap_mode="r")
    v688 = [s for s in ok_syms
            if s.startswith("688") or s.startswith("689")][:3]
    v688_details = []
    for sym in v688:
        j = sym_pos[sym]
        vw = np.asarray(vwap_cache[:, j], dtype=float)
        cl = np.asarray(close_cache[:, j], dtype=float)
        m = np.isfinite(vw) & np.isfinite(cl) & (cl > 0)
        idx = np.where(m)[0][-252:]
        if len(idx) == 0:
            v688_details.append({"sym": sym, "rows": 0, "gate": False})
            continue
        med = float(np.median(np.abs(vw[idx] / cl[idx] - 1.0)))
        rdf = pd.read_parquet(os.path.join(BARS_DIR, sym + ".parquet")
                              ).sort_values("date").reset_index(drop=True)
        rpos = np.searchsorted(calendar_int64,
                               rdf["date"].values.astype("int64"))
        raw_v = rdf["volume"].to_numpy(float) / 100.0
        raw_a = rdf["amount"].to_numpy(float) / 100.0
        gv = np.asarray(vol_cache[rpos, j], dtype=float)
        ga = np.asarray(amt_cache[rpos, j], dtype=float)
        ok_v = np.isfinite(raw_v) & np.isfinite(gv)
        ok_a = np.isfinite(raw_a) & np.isfinite(ga)
        rel_v = float(np.max(np.abs(gv[ok_v] - raw_v[ok_v])
                             / np.maximum(np.abs(raw_v[ok_v]), 1e-9)))
        rel_a = float(np.max(np.abs(ga[ok_a] - raw_a[ok_a])
                             / np.maximum(np.abs(raw_a[ok_a]), 1e-9)))
        v688_details.append({"sym": sym, "rows": int(len(idx)),
                              "median_abs_vwap_dev": round(med, 4),
                              "volume_vs_raw_div100_rel_err": round(rel_v, 7),
                              "amount_vs_raw_div100_rel_err": round(rel_a, 7),
                              "gate": bool(med <= 0.05 and rel_v <= 1e-5
                                           and rel_a <= 1e-5)})
    del close_cache, vwap_cache, vol_cache, amt_cache
    return {"event_day_check": {"samples": ev_report,
                                "events_total": sum(r["events_checked"]
                                                    for r in ev_report),
                                "max_abs_dev_pct": round(max_dev, 4),
                                "gate": bool(max_dev <= 0.5 and sum(
                                    r["events_checked"] for r in ev_report)
                                    >= 5)},
            "re_read_check": {"details": recheck,
                              "gate": bool(all(r["max_rel_err"] <= 1e-5
                                          for r in recheck))},
            "vwap_688_check": {"details": v688_details,
                               "gate": bool(len(v688_details) > 0 and all(
                                   r["gate"] for r in v688_details))}}


def main():
    t0 = time.time()
    os.makedirs(CACHE_DIR, exist_ok=True)
    files = sorted(glob.glob(os.path.join(BARS_DIR, "*.parquet")))
    print(f"universe files: {len(files)}", flush=True)

    # pass 1: master calendar (union of all bar dates, int64 us)
    cal = np.array([], dtype="int64")
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        for dates, _n in ex.map(_dates_only, files, chunksize=16):
            cal = np.union1d(cal, dates)
    T, N = len(cal), len(files)
    print(f"calendar T={T} syms N={N} ({time.time()-t0:.0f}s)", flush=True)
    np.save(os.path.join(CACHE_DIR, "dates.npy"), cal)

    # create NaN-filled float32 memmaps
    for name in FIELDS:
        p = os.path.join(CACHE_DIR, name + ".npy")
        arr = np.lib.format.open_memmap(p, mode="w+", dtype=np.float32,
                                        shape=(T, N))
        arr[:] = np.nan
        arr.flush()
        del arr

    # pass 2: write symbols in batches (memmap opened once per batch)
    items = [(p, i) for i, p in enumerate(files)]
    step = max(1, (N + BATCHES - 1) // BATCHES)
    batches = [(items[i:i + step], cal) for i in range(0, N, step)]
    status = {}
    sym_status = {}
    short_list = []
    sidecar_bad = []
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        for res in ex.map(_build_batch, batches):
            for sym, st, info in res:
                status[st] = status.get(st, 0) + 1
                sym_status[sym] = st
                if st == "short_history":
                    short_list.append(sym)
                if st == "sidecar_error":
                    sidecar_bad.append({"sym": sym, "reason": info})
    print(f"per-symbol pass done ({time.time()-t0:.0f}s) | {status}", flush=True)

    short_set = set(short_list)
    ok_syms = [os.path.basename(p)[:-8] for p in files
               if sym_status.get(os.path.basename(p)[:-8]) == "ok"]

    val = _validate(ok_syms, files, cal)

    nan_cov = {}
    for name in FIELDS:
        arr = np.load(os.path.join(CACHE_DIR, name + ".npy"), mmap_mode="r")
        nan_cov[name] = round(float(np.isnan(np.asarray(arr[::50, ::50],
                                        dtype=np.float32)).mean()), 4)
        del arr

    meta = {
        "batch": "P1C-StageA-stock-cache",
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "shape": {"T": int(T), "N": int(N), "dtype": "float32"},
        "fields": FIELDS,
        "adj_convention": "bars already qfq (event-day gate proves it); "
                          "sidecar = reference metadata, not applied",
        "volume_688_fix": "688xxx/689xxx volume AND amount stored at real "
                          "units (raw/100; both co-inflated at 100x in bars, "
                          "vwap=amount/volume invariant); enforced by "
                          "vwap_688_check gate",
        "universe_status": status,
        "sidecar_error_syms": sidecar_bad,
        "ok_universe": len(ok_syms),
        "nan_coverage_sampled": nan_cov,
        "validation": val,
        "audit": {"elapsed_sec": round(time.time() - t0, 1),
                  "workers": WORKERS, "cpu_cap_policy": "O-20260923-1738"},
        "ledger_note": "data engineering only, trials N unchanged",
    }
    with open(os.path.join(CACHE_DIR, "meta.json"), "w",
              encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    ok = (val["event_day_check"]["gate"] and val["re_read_check"]["gate"]
          and val["vwap_688_check"]["gate"]
          and status.get("read_error", 0) == 0
          and status.get("sidecar_error", 0) == 0)
    print(json.dumps(meta, indent=2, ensure_ascii=False), flush=True)
    print(f"STAGE-A {'PASS' if ok else 'FAIL'}", flush=True)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
