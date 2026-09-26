"""CN_SECTOR_LEADER_P1 runner -- A股「板块龙头非涨停面」judged 判决批
(T-87 s2 queue #4, sector-leader non-limit-up face).

Laws frozen in research/CN_SECTOR_LEADER_PREREG.md @commit b3d72924 (R99:
freeze precedes runner build precedes ANY run; seed
SEED_REGISTRY['cn_sector_leader_p1'] = 20277200 registered at the freeze
commit, band 20277200..20279200 clean; N bill 2004 = 4 judged cells x1
judged face + 2000 own-nulls; x1 = disclosure column not in N):

  panel   Money02 cache p1c_stock (T=8792 x N=5222 float32, open/close/
          volume/amount, read-only, cutoff 2026-09-22) + bars parquet for
          the universe re-derive (probe-verbatim per-file method) + SW
          official 2021 classification workbook (data/basic/
          sw_stock_classify_2021.xls, sha256 frozen, L2=industry_code[:4],
          point-in-time per start_date segments, retrofit disclosed).
          Cache gate stamps the ACTUAL asset meta value '2026-09-23 18:12:59'
          (r299 kenglu: gate constant must equal the asset meta 实值, not a
          remembered string -- wild_route_lab.py stale-stamp case) and the
          frozen cross-check results/_r299bma_cache_crosscheck.json (0
          mismatch) is gated in place. Survivorship faces disclosed
          (in-market snapshot panel, current-time masks, WILD-S1 same face).
  events  EF encoding probe-verbatim (results/_r299bma_sector_census.py =
          sole encoding authority): per day t, r20=c/c[-20]-1 over U_static
          members with a mapped sector; sector EW20>0 with >=5 members
          ranked top K=3 = hot; leader = argmax r20 within hot sector;
          trigger = (sector, day, leader) when leader close r1 < board
          floor - 0.002 (non-limit-up face; near/at-limit closes excluded
          and counted). Tie face: probe-verbatim first-argmax (float ties
          measure-zero; prereg-narrative amount20 tie-break subsumed by
          probe authority). Census gate refuses (exit 2) on any drift vs
          the frozen probe results/cn_sector_leader_probe.json (17,823
          events / 2,562 limit-excluded / universe 3106 / skip ledger /
          EF params).
  exec    signal close d -> entry open d+1; suspension rolls to the first
          tradable open (open & volume finite); near-limit-up open
          (open/prev_finite_close-1 >= floor-0.002) = unfillable, counted
          not discarded; exits T+1-open style; panel-end tail = mark to
          last finite close (honest, WILD-S1/KLINE same face).
  floors  main 0.0975 / chinext(30) 0.1975 from 2020-08-24 / star(68) 0.1975
          from 2019-07-22 (prereg s2 EF table; symbol-prefix face, probe-
          identical; BSE-prefix members face the main floor per the frozen
          table -- conservative rejection, disclosed).
  cells   LDR-FIX10 H=10 | LDR-FIX20 H=20 | LDR-SECT10 H=10 v sector ebb
          (hold-day sector outside hot_rank(t') -> next open out, folklore
          card#7 direction proxy) | LDR-STOP10 H=10 v close <= entry*0.92
          (engine -8% canonical face) -- first-to-fire wins.
  costs   V2 single source: alloc_backtest.side_cost_v2/side_cost_x2 with
          per-member leg notional N0=1e5 CNY; x2 judged face (every V2
          component doubled), x1 disclosure column; ADV20 = NaN-aware
          rolling-20 amount mean (min 10) on the member own index; NaN adv
          -> krules 10bp fallback inside the V2 call. x2 array = 2 x x1
          array (pointwise identity asserted in selftest, no hand-copy).
  bucket  WILD-S1/KLINE frozen reuse: day-t cohort (all triggers that day,
          <=3 members, equal-weight internal) deployed at t+1 open; net
          booked evenly across holding calendar days entry_cal+1..exit_cal;
          ebb/stop arms book at actual exit (per-trade spans).
  nulls   RANDOM_LARGE_SAMPLE_LAW s3: per cell K=2000 draws, each draw =
          N_cell uniform (name,day) pairs from universe x valid-days table
          (own-index t in [1, n-2], EF disclosed), same time-exit H /
          execution / cost(x2) / bucket accounting -> null cell Sharpe;
          own-null pool per cell (rng seed SEED+k); ebb/stop arms
          undefined on random events (EF disclosed, time-exit null face);
          8 shards x 250 draws npy checkpoints, idempotent resume. Block
          bootstrap 2000 (block=10) + sign-flip 2000 per cell, p double.
  starts  census virtual starts t0 in [200, T-126), 126d window vs the
          universe-EW passive proxy; 4 segment classes (bull/bear/
          deep-bear/chop, REV_OSC s2.1 frozen face); segment n<500 =
          insufficient-sample honest note; >=100 random train/val splits +
          walk-forward 5 folds (law s2.3).
  sobol   s2.2 space-filling descriptive leg: Sobol N=500 draws over
          (W in [10,60] x K in [1,5] x H in [5,20] integer grid), same
          encoding / same execution (time-exit H) / cost x1 face; scramble
          seed-sequence np.random.default_rng([20277200, 2000]); engine
          draws 512 (power-of-2 balance), first 500 consumed per prereg
          N=500; products = Sharpe/mean/maxDD distribution description
          columns; NO N_eff, NO gates, NO survivorship claims. 10 shards
          x 50 draws npy checkpoints.
  gates   G1'v2 per cell (batch_cells=2004, pool='stock_b_layer',
          null_pool=own, F6 dual trade gate) + DSR (deflated_sharpe_ratio
          on the raw x2 series) + family PBO (screening/pbo cscv_pbo CSCV-8
          over the 4-cell x2 matrix) + g2_registration_v2. NO hand-copied
          lines (O-2250). Judged face = x2 (prereg s3); batch disclosure:
          ann>0 AND OOS (>=2025-01-01) ann>0 AND maxDD >= -35%.
  ledger  science_gates.append_ledger single-count (prev_total redo
          guard, REV_OSC r259 face); gate_attrition measurement row
          (entries-list face per r248 law, own row replaced on redo).

Products (prereg s6): results/cn_sector_leader/p1_results.json (top
evidence_cutoff + cutoff_meta + panel/taxonomy/cache faces + cells both
faces + nulls + D6 + virtual starts + splits + walk-forward + robust +
gates + ledger + limit/reject disclosures + Sobol descriptive block) +
cells/<cell>_<face>.json|.npy + nulls/<cell>_shard<k>.npy +
sobol/shard<k>.npy + cells_summary.csv.

Usage: run | selftest   (exit 0 ok; 2 = fail-closed gate refusal; 3 = RAM
floor)
"""
import argparse
import glob
import hashlib
import json
import math
import os
import shutil
import sys
import tempfile
import time

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import science_gates as SG                      # shared gate library (O-2250)
from screening.pbo import cscv_pbo              # family PBO CSCV-8
from alloc_backtest import side_cost_v2, side_cost_x2   # V2 single source

BARS = os.path.join(ROOT, "Money02", "data", "bars")
CACHE = os.path.join(ROOT, "Money02", "data", "cache", "p1c_stock")
MASK = os.path.join(ROOT, "data", "fundamental", "b_layer_mask.csv")
XLS = os.path.join(ROOT, "data", "basic", "sw_stock_classify_2021.xls")
SSE = os.path.join(ROOT, "Money02", "data", "index", "sse.parquet")
PROBE_JSON = os.path.join(ROOT, "results", "cn_sector_leader_probe.json")
XCC_JSON = os.path.join(ROOT, "results", "_r299bma_cache_crosscheck.json")
OUT_DIR = os.path.join(ROOT, "results", "cn_sector_leader")
CELL_DIR = os.path.join(OUT_DIR, "cells")
NULL_DIR = os.path.join(OUT_DIR, "nulls")
SOBOL_DIR = os.path.join(OUT_DIR, "sobol")
OUT_JSON = os.path.join(OUT_DIR, "p1_results.json")
OUT_CSV = os.path.join(OUT_DIR, "cells_summary.csv")
ATT_JSON = os.path.join(ROOT, "results", "gate_attrition.json")

EVIDENCE_CUTOFF = "2026-09-22"
N_FILES_EXPECT = 5222
UNIVERSE_EXPECT = 3106
CENSUS_EXPECT = 17823                 # frozen probe trigger census
LIMIT_EXCL_EXPECT = 2562               # frozen probe limit-face exclusions
CACHE_STAMP_EXPECTED = "2026-09-23 18:12:59"   # ACTUAL asset meta (r299 kenglu)
XLS_SHA256_FROZEN = ("1111bceb420c510c90f0f794fd8ae0c3"
                     "9015c99768162374f90b782ce5d3a3c8")
BATCH_NAME = "CN_SECTOR_LEADER_P1"
BATCH_CELLS = 2004                    # 4 judged cells x1 + 2000 nulls
K_NULLS = 2000
NULL_SHARDS = 8
SOBOL_N = 500                        # prereg s3.2.2 descriptive leg
SOBOL_SHARDS = 10
SOBOL_DRAW_BALANCE = 512              # power-of-2 balance, first 500 used
PBP = 252
SEED = None                          # filled from SG.SEED_REGISTRY at run
MIN_ROWS = 500
MIN_AMT20 = 3e7
# EF params (prereg s2, probe authority)
W = 20
K_TOP = 3
MIN_SECT = 5
LIMIT_EXCL_TOL = 0.002
MAIN_FLOOR = 0.0975
WIDE_FLOOR = 0.1975
CN_20CM_FROM = np.datetime64("2020-08-24")
STAR_FROM = np.datetime64("2019-07-22")
N0 = 1.0e5                           # per-member leg notional CNY (EF)
H_FIX = 10
H_LONG = 20
STOP_PX = 0.92                       # engine -8% canonical face (s3.1)
WIN_DAYS = 126
STARTS_FROM = 200
SEG_MIN = 500
OOS_FROM = np.datetime64("2025-01-01")
D6_REJECT = 0.7
RAM_FLOOR_GB = 16.0

CELLS = [
    {"name": "LDR-FIX10",  "H": H_FIX,  "arm": "time"},
    {"name": "LDR-FIX20",  "H": H_LONG, "arm": "time"},
    {"name": "LDR-SECT10", "H": H_FIX,  "arm": "ebb"},
    {"name": "LDR-STOP10", "H": H_FIX,  "arm": "stop"},
]
CELL_NAMES = [c["name"] for c in CELLS]


def _free_ram_gb():
    try:
        import psutil
        return psutil.virtual_memory().available / 1e9
    except Exception:
        return RAM_FLOOR_GB + 1.0        # psutil absent -> guard off (disclosed)


def gate_refuse(msg):
    print(f"GATE-REFUSE(exit2): {msg}")
    return 2


# ------------------------------------------------------------------ helpers
def _adv20_own(amount):
    """NaN-aware rolling-20 amount mean (min 10), own-index, float64
    (KLINE-verbatim)."""
    fin = np.isfinite(amount)
    vals = np.where(fin, amount, 0.0)
    cs = np.concatenate([[0.0], np.cumsum(vals)])
    cc = np.concatenate([[0], np.cumsum(fin.astype(np.int64))])
    lo = np.maximum(np.arange(len(amount)) - 20, 0)
    hi = np.arange(len(amount)) + 1
    cnt = cc[hi] - cc[lo]
    out = np.full(len(amount), np.nan)
    ok = cnt >= 10
    out[ok] = (cs[hi] - cs[lo])[ok] / cnt[ok]
    return out


def _floor_own(dates_d, sym):
    """Board floor per own-day, symbol-prefix face (probe-verbatim)."""
    fl = np.full(len(dates_d), MAIN_FLOOR)
    if sym.startswith("30"):
        fl[dates_d >= CN_20CM_FROM] = WIDE_FLOOR
    elif sym.startswith("68"):
        fl[dates_d >= STAR_FROM] = WIDE_FLOOR
    return fl


# ------------------------------------------------------------------ panel
def load_taxonomy(idx, syms):
    """SW 2021 workbook -> sector matrix (probe-verbatim parse) with the
    workbook sha256 gated against the frozen value."""
    raw = open(XLS, "rb").read()
    sha = hashlib.sha256(raw).hexdigest()
    if sha != XLS_SHA256_FROZEN:
        return None, f"taxonomy sha256 drift: {sha}"
    clf = pd.read_excel(XLS, dtype={"股票代码": "str", "行业代码": "str"})
    clf.columns = ["symbol", "start_date", "industry_code", "update_time"]
    symset = set(syms)
    clf = clf[clf["symbol"].isin(symset)]
    covered = len(set(clf["symbol"]))
    if covered != len(syms):
        return None, f"taxonomy coverage {covered}/{len(syms)} != 100%"
    clf = clf.sort_values(["symbol", "start_date"])
    l2_codes = sorted(clf["industry_code"].str[:4].unique())
    l2_id = {c: i + 1 for i, c in enumerate(l2_codes)}
    n_l2 = len(l2_codes)
    T, N = len(idx), len(syms)
    col = {s: j for j, s in enumerate(syms)}
    sect = np.zeros((T, N), dtype=np.int16)
    for sym, g in clf.groupby("symbol"):
        j = col[sym]
        for sd, ic in zip(g["start_date"], g["industry_code"]):
            sd = pd.Timestamp(sd)
            p = int(np.searchsorted(idx, sd.to_pydatetime(), side="right") - 1)
            p = max(p, 0)
            sid = l2_id.get(ic[:4], 0)
            if sid != 0:
                sect[p:, j] = sid
    return {"sect": sect, "l2_codes": l2_codes, "n_l2": n_l2,
            "sha256": sha, "covered": covered}, None


def encode_events(cl, sect, in_u, syms, dates_d, n_l2, W_, K_TOP_,
                 hot_arr=None):
    """Probe-verbatim trigger encoding (sole authority: the frozen census).
    Returns (events [(t, col, sid)], limit_excluded, by_year dict).
    Hot-id scan vectorized with identical semantics (stable order == probe
    list order); leader = first-argmax (probe tie face)."""
    T, N = cl.shape
    events = []
    limit_excluded = 0
    by_year = {}
    for t in range(W_ + 1, T):
        c_now = cl[t]
        c_then = cl[t - W_]
        c_prev = cl[t - 1]
        with np.errstate(invalid="ignore"):
            r20 = c_now / c_then - 1.0
            r1 = c_now / c_prev - 1.0
        srow = sect[t]
        valid = (np.isfinite(r20) & np.isfinite(c_now) & np.isfinite(r1)
                 & in_u & (srow > 0))
        cols_v = np.flatnonzero(valid)
        if cols_v.size == 0:
            continue
        sids = srow[cols_v]
        r20v = r20[cols_v]
        counts = np.bincount(sids, minlength=n_l2 + 1)
        sums = np.bincount(sids, weights=r20v, minlength=n_l2 + 1)
        with np.errstate(invalid="ignore"):
            ew = np.where(counts > 0, sums / np.maximum(counts, 1), np.nan)
        hot_mask = (counts[1:] >= MIN_SECT) & (ew[1:] > 0)
        hot_ids = np.flatnonzero(hot_mask) + 1     # ascending, stable
        if hot_ids.size == 0:
            continue
        order = np.argsort(-ew[hot_ids], kind="stable")
        hot_rank = hot_ids[order][:K_TOP_]
        if hot_arr is not None:
            hot_arr[t, :len(hot_rank)] = hot_rank
        yy = str(dates_d[t])[:4]
        for s in hot_rank:
            m = sids == s
            cand = cols_v[m]
            rv = r20v[m]
            lead = int(cand[int(np.argmax(rv))])
            sym = syms[lead]
            if sym.startswith("30"):
                wide = dates_d[t] >= CN_20CM_FROM
            elif sym.startswith("68"):
                wide = dates_d[t] >= STAR_FROM
            else:
                wide = False
            board_floor = WIDE_FLOOR if wide else MAIN_FLOOR
            if float(r1[lead]) >= board_floor - LIMIT_EXCL_TOL:
                limit_excluded += 1
                continue
            events.append((t, lead, int(s)))
            by_year[yy] = by_year.get(yy, 0) + 1
    return events, limit_excluded, by_year


def load_panel():
    """Fail-closed gate battery (prereg s2) + panel assembly from cache."""
    files = sorted(glob.glob(os.path.join(BARS, "*.parquet")))
    if len(files) != N_FILES_EXPECT:
        return None, f"bars census drift: {len(files)} != {N_FILES_EXPECT}"
    if not os.path.exists(PROBE_JSON):
        return None, "frozen probe reference absent"
    probe = json.load(open(PROBE_JSON, encoding="utf-8"))
    if probe.get("panel", {}).get("cutoff") != EVIDENCE_CUTOFF:
        return None, "probe cutoff drift"
    if int(probe.get("universe_n", -1)) != UNIVERSE_EXPECT:
        return None, "probe universe_n drift"
    ef_p = probe.get("EF_params", {})
    if (ef_p.get("W") != W or ef_p.get("K_TOP") != K_TOP
            or ef_p.get("MIN_SECT") != MIN_SECT
            or ef_p.get("limit_excl_tol") != LIMIT_EXCL_TOL):
        return None, "probe EF params drift vs runner constants"
    if not os.path.exists(XCC_JSON):
        return None, "cache cross-check reference absent"
    xcc = json.load(open(XCC_JSON, encoding="utf-8"))
    if int(xcc.get("bars_files", -1)) != N_FILES_EXPECT:
        return None, "cross-check bars_files drift"
    if xcc.get("cache_last_date") != EVIDENCE_CUTOFF:
        return None, "cross-check cache_last_date drift"
    bad = [k for k, v in xcc.items()
           if isinstance(v, dict) and v.get("finite_mask_mismatches")]
    if bad:
        return None, f"cross-check mismatches: {bad}"
    meta = json.load(open(os.path.join(CACHE, "meta.json"), encoding="utf-8"))
    # r299 kenglu: the gate constant IS the actual asset meta stamp -- a
    # regenerated cache must refuse, a remembered wrong stamp must refuse.
    if meta.get("generated") != CACHE_STAMP_EXPECTED:
        return None, (f"cache meta stamp drift: {meta.get('generated')} "
                      f"!= {CACHE_STAMP_EXPECTED}")
    idx = pd.to_datetime(np.load(os.path.join(CACHE, "dates.npy")), unit="us")
    if str(idx[-1].date()) != EVIDENCE_CUTOFF:
        return None, "panel end != cutoff"
    close32 = np.load(os.path.join(CACHE, "close.npy"), mmap_mode="r")
    open32 = np.load(os.path.join(CACHE, "open.npy"), mmap_mode="r")
    vol32 = np.load(os.path.join(CACHE, "volume.npy"), mmap_mode="r")
    amt32 = np.load(os.path.join(CACHE, "amount.npy"), mmap_mode="r")
    T, N = len(idx), close32.shape[1]
    if meta.get("shape", {}).get("T") != T or meta.get("shape", {}).get("N") != N:
        return None, f"cache shape drift: ({T},{N}) vs meta {meta.get('shape')}"
    syms = [os.path.basename(p)[:-8] for p in files]
    if len(syms) != N or len(idx) != T:
        return None, "cache shape vs bars census drift"
    col = {s: j for j, s in enumerate(syms)}

    # ---- universe re-derive (probe-verbatim per-file method, str codes)
    mask = pd.read_csv(MASK, dtype={"code": str})
    ok = set(mask.loc[mask["ok_static"] == True, "code"])
    u_cols = []
    skip = {"not_ok": 0, "rows": 0, "last": 0, "liq": 0}
    for p in files:
        code = os.path.basename(p)[:-8]
        if code not in ok:
            skip["not_ok"] += 1
            continue
        df = pd.read_parquet(p, columns=["date", "amount"])
        if len(df) < MIN_ROWS:
            skip["rows"] += 1
            continue
        if str(df["date"].iloc[-1])[:10] != EVIDENCE_CUTOFF:
            skip["last"] += 1
            continue
        if float(np.median(df["amount"].values[-20:])) < MIN_AMT20:
            skip["liq"] += 1
            continue
        u_cols.append(col[code])
    u_cols = np.array(sorted(u_cols), dtype=np.int64)
    if len(u_cols) != int(probe["universe_n"]):
        return None, (f"universe re-derive drift: n={len(u_cols)} "
                      f"vs probe {probe['universe_n']}")
    if skip != probe.get("universe_skipped"):
        return None, (f"universe skip drift: {skip} "
                      f"vs {probe.get('universe_skipped')}")
    if len(u_cols) != UNIVERSE_EXPECT:
        return None, f"universe n={len(u_cols)} != {UNIVERSE_EXPECT}"
    in_u = np.zeros(N, dtype=bool)
    in_u[u_cols] = True

    # ---- taxonomy + sector matrix
    tax, err = load_taxonomy(idx, syms)
    if err:
        return None, err
    sect = tax["sect"]
    n_l2 = tax["n_l2"]

    # ---- trigger census re-derive (census-drift face, probe authority)
    # hot_arr filled in the same pass (SECT10 ebb arm consumes it)
    cl = np.asarray(close32, dtype=np.float64)
    dates_d = idx.values.astype("datetime64[D]")
    hot_arr = np.zeros((T, K_TOP), dtype=np.int16)
    events, limit_excluded, by_year = encode_events(
        cl, sect, in_u, syms, dates_d, n_l2, W, K_TOP, hot_arr=hot_arr)
    if len(events) != CENSUS_EXPECT:
        return None, (f"trigger census drift: {len(events)} "
                      f"!= frozen {CENSUS_EXPECT}")
    if limit_excluded != LIMIT_EXCL_EXPECT:
        return None, (f"limit-face drift: {limit_excluded} "
                      f"!= frozen {LIMIT_EXCL_EXPECT}")
    cens = probe.get("census", {})
    if cens.get("first") and str(dates_d[events[0][0]]) != cens["first"]:
        return None, "census first-day drift"
    if cens.get("last") and str(dates_d[events[-1][0]]) != cens["last"]:
        return None, "census last-day drift"

    # ---- members (own-index face from cache columns)
    members = {}
    for j in u_cols:
        sym = syms[j]
        o = np.asarray(open32[:, j], dtype=np.float64)
        c = np.asarray(close32[:, j], dtype=np.float64)
        v = np.asarray(vol32[:, j], dtype=np.float64)
        amt = np.asarray(amt32[:, j], dtype=np.float64)
        own = np.flatnonzero(np.isfinite(o))    # own index = finite-open days
        if own.size < 30:
            continue
        o, c, v, amt = o[own], c[own], v[own], amt[own]
        pcal = own.astype(np.int32)
        n = len(own)
        pc = np.full(n, np.nan)
        last = np.nan
        for i in range(n):
            pc[i] = last
            if np.isfinite(c[i]):
                last = c[i]
        trad = np.isfinite(o) & np.isfinite(v)
        nxt = np.full(n, -1, dtype=np.int64)
        last_t = -1
        for i in range(n - 1, -1, -1):
            last_t = i if trad[i] else last_t
            nxt[i] = last_t
        lastfc = -1
        for i in range(n - 1, -1, -1):
            if np.isfinite(c[i]):
                lastfc = i
                break
        adv = _adv20_own(amt)
        cf1 = np.array([side_cost_v2(N0, a) / N0 for a in adv])
        cf2 = 2.0 * cf1            # x2 == 2x V2 pointwise (selftest identity)
        members[int(j)] = {
            "col": int(j), "sym": sym, "o": o, "c": c, "v": v, "amt": amt,
            "n": n, "pcal": pcal, "pc": pc, "nxt": nxt, "trad": trad,
            "lastfc": lastfc, "fl": _floor_own(dates_d[pcal], sym),
            "adv": adv, "cf1": cf1, "cf2": cf2,
        }
    if len(members) != len(u_cols):
        return None, f"degenerate members: {len(members)}/{len(u_cols)}"

    # ---- sse onto calendar (ffill bridge, REV_OSC face)
    sse_df = pd.read_parquet(SSE)
    sse_df["date"] = pd.to_datetime(sse_df["date"])
    sse_close = sse_df.set_index("date")["close"].reindex(idx).ffill()
    sse_v = sse_close.to_numpy(dtype=np.float64)
    ma200 = pd.Series(sse_v).rolling(200, min_periods=200).mean().to_numpy()

    # ---- universe-EW passive proxy on the calendar
    ew_sum = np.zeros(T)
    ew_cnt = np.zeros(T)
    for j, m in members.items():
        c = m["c"]
        with np.errstate(invalid="ignore"):
            r = c[1:] / c[:-1] - 1.0
        okm = np.isfinite(r)
        np.add.at(ew_sum, m["pcal"][1:][okm], r[okm])
        np.add.at(ew_cnt, m["pcal"][1:][okm], 1.0)
    ew = np.where(ew_cnt > 0, ew_sum / np.maximum(ew_cnt, 1.0), 0.0)

    pref = {"chinext": 0, "star": 0, "main": 0}
    for j in u_cols:
        s = syms[j]
        k = "chinext" if s.startswith("30") else ("star" if s.startswith("68")
                                                 else "main")
        pref[k] += 1
    face = {
        "files": N_FILES_EXPECT, "universe_n": len(members), "skip": skip,
        "boards_prefix": pref, "T": T, "N": N,
        "cutoff": EVIDENCE_CUTOFF,
        "cache_stamp": CACHE_STAMP_EXPECTED,
        "cache_stamp_note": "gate constant = actual asset meta value "
                            "(r299 kenglu; wild_route_lab stale-stamp case)",
        "census": {"trigger_events_n": len(events),
                   "limit_face_excluded_events": limit_excluded,
                   "distinct_trigger_days": len({e[0] for e in events}),
                   "by_year": dict(sorted(by_year.items())),
                   "first": str(dates_d[events[0][0]]),
                   "last": str(dates_d[events[-1][0]])},
        "taxonomy": {"source": "official SW 2021 classification workbook",
                     "sha256": tax["sha256"], "granularity": "L2=[:4]",
                     "n_l2": n_l2, "coverage": f"{tax['covered']}/{N}",
                     "point_in_time": True,
                     "retrofit_disclosure":
                         "SW 2021 standard applied retroactively pre-2021 "
                         "(official published history); within-standard "
                         "changes honored via start_date; unmapped "
                         "pre-first-classification pairs excluded"},
        "tie_face": "probe-verbatim first-argmax (float r20 ties "
                    "measure-zero; prereg-narrative amount20 tie-break "
                    "subsumed by probe authority)",
        "bse_floor_note": "BSE-prefix members face the main floor per the "
                           "frozen prereg s2 EF table (conservative "
                           "rejection face, disclosed)",
    }
    P = {"idx": idx, "dates_d": dates_d, "calendar_d": dates_d, "T": T,
         "N": N, "syms": syms, "col": col, "cl": cl, "sect": sect,
         "n_l2": n_l2, "l2_codes": tax["l2_codes"], "in_u": in_u,
         "members": members, "u_cols": u_cols, "hot_arr": hot_arr,
         "events": events, "sse": sse_v, "ma200": ma200, "ew": ew,
         "face": face}
    return P, None


# ------------------------------------------------------------------ sim
def sim_trade(P, mi, sig_cal, sid, cell, face):
    """One event path -> (net, entry_cal, exit_cal, tag) or (None,*,*,tag).
    face in {'x1','x2'} selects the member cost array."""
    m = P["members"][mi]
    o, c = m["o"], m["c"]
    n = m["n"]
    cf = m["cf1"] if face == "x1" else m["cf2"]
    s0 = int(np.searchsorted(m["pcal"], sig_cal, side="right"))
    d = int(m["nxt"][s0]) if s0 < n else -1
    if d < 0:
        return None, None, None, "susp_end"
    pc = m["pc"][d]
    if np.isfinite(pc) and o[d] / pc - 1.0 >= m["fl"][d] - LIMIT_EXCL_TOL:
        return None, None, None, "limit_reject"
    et = d
    entry = float(o[et])
    x_target = et + cell["H"]
    u = et
    while u < n:
        if not m["trad"][u]:
            u += 1
            continue
        if u >= x_target:
            cin, cout = cf[et], cf[u]
            net = float(o[u]) / entry * (1.0 - cout) / (1.0 + cin) - 1.0
            return net, int(m["pcal"][et]), int(m["pcal"][u]), "time"
        trig = False
        if cell["arm"] == "ebb":
            row = P["hot_arr"][m["pcal"][u]]
            if sid not in row:
                trig = True
        if cell["arm"] == "stop" and np.isfinite(c[u]) \
                and c[u] <= entry * STOP_PX:
            trig = True
        if trig:
            w = u + 1
            while w < n and not m["trad"][w]:
                w += 1
            if w >= n:
                break
            cin, cout = cf[et], cf[w]
            net = float(o[w]) / entry * (1.0 - cout) / (1.0 + cin) - 1.0
            tag = "ebb" if cell["arm"] == "ebb" else "stop"
            return net, int(m["pcal"][et]), int(m["pcal"][w]), tag
        u += 1
    # panel-end tail: mark to last finite close (honest)
    j = m["lastfc"] if m["lastfc"] > et else et
    px = float(c[j]) if np.isfinite(c[j]) else entry
    cin, cout = cf[et], cf[j]
    net = px / entry * (1.0 - cout) / (1.0 + cin) - 1.0
    return net, int(m["pcal"][et]), int(m["pcal"][j]), "tail"


def run_cell(P, cell, face, T_cal):
    """Cell daily series + counters (prereg s3 bucket accounting)."""
    events = P["events"]
    ser = np.zeros(T_cal)
    n_events = len(events)
    n_filled = 0
    rejects = {"limit_reject": 0, "susp_end": 0}
    exits = {"time": 0, "ebb": 0, "stop": 0, "tail": 0}
    cohorts = empty_cohorts = 0
    max_cohort = 0
    i = 0
    while i < n_events:
        cal = events[i][0]
        j = i
        while j < n_events and events[j][0] == cal:
            j += 1
        cohort = events[i:j]
        i = j
        cohorts += 1
        max_cohort = max(max_cohort, len(cohort))
        filled = []
        for t, mi, sid in cohort:
            net, ecal, xcal, tag = sim_trade(P, mi, t, sid, cell, face)
            if net is None:
                rejects[tag] = rejects.get(tag, 0) + 1
                continue
            exits[tag] = exits.get(tag, 0) + 1
            filled.append((net, ecal, xcal))
            n_filled += 1
        if not filled:
            empty_cohorts += 1
            continue
        m_ = len(filled)
        for net, ecal, xcal in filled:
            span = max(1, xcal - ecal)
            share = net / m_ / span
            lo = min(ecal + 1, T_cal)
            hi = min(xcal + 1, T_cal)
            if hi > lo:
                ser[lo:hi] += share
    return {"series": ser, "n_events": n_events, "n_filled": n_filled,
            "rejects": rejects, "exits": exits, "cohorts": cohorts,
            "empty_cohorts": empty_cohorts, "max_cohort": max_cohort}


def cell_stats(series, calendar_d):
    r = np.asarray(series, dtype=np.float64)
    mu = float(r.mean())
    sd = float(r.std(ddof=1)) if len(r) > 1 else 0.0
    sharpe = mu / sd * math.sqrt(PBP) if sd > 0 else 0.0
    eq = np.cumprod(1.0 + r)
    peak = np.maximum.accumulate(eq)
    dd = float((eq / peak - 1.0).min())
    ann = float(eq[-1] ** (PBP / max(len(r), 1)) - 1.0)
    i_oos = int(np.searchsorted(calendar_d, OOS_FROM))
    oos = r[i_oos:]
    oos_ann = None
    oos_sh = 0.0
    if len(oos):
        oos_eq = np.cumprod(1.0 + oos)
        oos_ann = float(oos_eq[-1] ** (PBP / max(len(oos), 1)) - 1.0)
        oos_sd = float(oos.std(ddof=1)) if len(oos) > 1 else 0.0
        oos_sh = float(oos.mean() / oos_sd * math.sqrt(PBP)) \
            if oos_sd > 0 else 0.0
    return {"sharpe_full": round(sharpe, 4), "ann_ret": round(ann, 6),
            "max_dd": round(dd, 6), "n_days": int(len(r)),
            "oos_from": str(pd.Timestamp(OOS_FROM).date()),
            "oos_ann": round(oos_ann, 6) if oos_ann is not None else None,
            "oos_sharpe": round(oos_sh, 4),
            "median_abs_r": round(float(np.median(np.abs(r))), 6),
            "p999_abs_r": round(float(np.percentile(np.abs(r), 99.9)), 6)}


# ------------------------------------------------------------------ nulls
def build_null_table(P, H, cost_key="cf2"):
    """Flat (pair) arrays over universe x valid own days for one null H face
    (KLINE-verbatim construction on the cache own-index members)."""
    sig, okflag, gross, entcal, span, cin_a, cout_a = \
        [], [], [], [], [], [], []
    for j in sorted(P["members"]):
        m = P["members"][j]
        n = m["n"]
        if n < 4:
            continue
        o, v, pc, fl, nxt, pcal = m["o"], m["v"], m["pc"], m["fl"], \
            m["nxt"], m["pcal"]
        cf = m[cost_key]
        t_arr = np.arange(1, n - 1)                  # own t in [1, n-2]
        ent = nxt[t_arr + 1]                          # -1 if none
        valid = ent >= 0
        ent = np.where(valid, ent, 0)
        pc_e = pc[ent]
        with np.errstate(invalid="ignore"):
            rej = np.isfinite(pc_e) & \
                (o[ent] / pc_e - 1.0 >= fl[ent] - LIMIT_EXCL_TOL)
        ok = valid & ~rej & np.isfinite(o[ent])
        xu = np.where(ent + H < n, nxt[np.minimum(ent + H, n - 1)], -1)
        ok = ok & (xu >= 0)
        xu = np.where(ok, xu, 0)
        gr = np.where(ok, o[xu] / np.where(ok, o[ent], 1.0) - 1.0, np.nan)
        ecal = pcal[ent]
        xcal = pcal[xu]
        sp = np.where(ok, np.maximum(xcal - ecal, 1), 1)
        sig.append(pcal[t_arr])
        okflag.append(ok)
        gross.append(gr.astype(np.float64))
        entcal.append(ecal.astype(np.int64))
        span.append(sp.astype(np.int64))
        cin_a.append(cf[ent])
        cout_a.append(cf[xu])
    cat = lambda xs: np.concatenate(xs) if xs else np.array([])
    return {"sig": cat(sig), "ok": cat(okflag), "gross": cat(gross),
            "entcal": cat(entcal), "span": cat(span), "cin": cat(cin_a),
            "cout": cat(cout_a)}


def null_draw(tbl, rng, N, T_cal):
    """One null cell draw -> Sharpe (prereg s3 own-null face,
    KLINE-verbatim)."""
    total = len(tbl["ok"])
    if total == 0 or N <= 0:
        return 0.0
    sel = rng.integers(0, total, size=N)
    ok = tbl["ok"][sel]
    if not ok.any():
        return 0.0
    gross = tbl["gross"][sel[ok]]
    nets = (1.0 + gross) * (1.0 - tbl["cout"][sel[ok]]) / \
        (1.0 + tbl["cin"][sel[ok]]) - 1.0
    sc = tbl["sig"][sel[ok]]
    ent = tbl["entcal"][sel[ok]]
    span = tbl["span"][sel[ok]]
    cnt = np.bincount(sc, minlength=T_cal)
    share = nets / (cnt[sc] * span)
    maxspan = int(span.max())
    offs = np.arange(maxspan)
    idxmat = ent[:, None] + 1 + offs[None, :]
    keep = offs[None, :] < span[:, None]
    flat_idx = idxmat[keep]
    flat_w = np.repeat(share, span.astype(np.int64))
    m2 = flat_idx < T_cal
    ser = np.bincount(flat_idx[m2], weights=flat_w[m2], minlength=T_cal)
    sd = ser.std(ddof=1)
    return float(ser.mean() / sd * math.sqrt(PBP)) if sd > 0 else 0.0


def run_cell_nulls(P, cell, tables, n_events):
    """K=2000 own-null pool, sharded npy checkpoints (idempotent)."""
    H = cell["H"]                    # null face = time-exit at cell H (EF)
    tbl = tables[H]
    per = K_NULLS // NULL_SHARDS
    vals = np.empty(K_NULLS)
    for s in range(NULL_SHARDS):
        path = os.path.join(NULL_DIR, f"{cell['name']}_shard{s}.npy")
        if os.path.exists(path):
            vals[s * per:(s + 1) * per] = np.load(path)
            continue
        chunk = np.empty(per)
        for i in range(per):
            k = s * per + i
            rng = np.random.default_rng(SEED + k)
            chunk[i] = null_draw(tbl, rng, n_events, P["T"])
        np.save(path, chunk)
        vals[s * per:(s + 1) * per] = chunk
    cov = {"mu": round(float(vals.mean()), 4),
           "sigma": round(float(vals.std(ddof=1)), 4),
           "n_values": int(len(vals))}
    return {"values": [round(float(v), 4) for v in vals], "coverage": cov,
            "null_face": f"time-exit H={H} (EF: ebb/stop arms undefined "
                         "on random events)",
            "n_drawn_pairs_per_draw": n_events}


# ------------------------------------------------- vectorized time-exit paths
def vector_time_paths(P, events, H, face="x1"):
    """Vectorized T+1-open entry + time-exit-H paths for arbitrary event
    lists (Sobol leg; identical math to sim_trade's time arm incl. the
    panel-end tail mark). Returns (series, counters)."""
    T_cal = P["T"]
    ser = np.zeros(T_cal)
    if not events:
        return ser, {"n_events": 0, "n_filled": 0,
                     "rejects": {"limit_reject": 0, "susp_end": 0},
                     "exits": {"time": 0, "tail": 0}}
    ev_t = np.array([e[0] for e in events], dtype=np.int64)
    ev_m = np.array([e[1] for e in events], dtype=np.int64)
    order = np.argsort(ev_m, kind="stable")
    ev_t, ev_m = ev_t[order], ev_m[order]
    bounds = np.flatnonzero(np.concatenate(([True], ev_m[1:] != ev_m[:-1],
                                            [True])))
    n_rej = n_susp = n_time = n_tail = 0
    sig_a, net_a, ecal_a, xcal_a = [], [], [], []
    for b0, b1 in zip(bounds[:-1], bounds[1:]):
        m = P["members"][int(ev_m[b0])]
        ts = ev_t[b0:b1]
        n = m["n"]
        s0 = np.searchsorted(m["pcal"], ts, side="right")
        ent = np.where(s0 < n, m["nxt"][np.minimum(s0, n - 1)], -1)
        has = ent >= 0
        n_susp += int((~has).sum())
        ent_c = np.where(has, ent, 0)
        pc_e = m["pc"][ent_c]
        with np.errstate(invalid="ignore"):
            rej = has & np.isfinite(pc_e) & \
                (m["o"][ent_c] / pc_e - 1.0
                 >= m["fl"][ent_c] - LIMIT_EXCL_TOL)
        n_rej += int(rej.sum())
        ok = has & ~rej & np.isfinite(m["o"][ent_c])
        pos = ent_c + H
        complete = ok & (pos < n)
        xu = np.where(complete, m["nxt"][np.minimum(pos, n - 1)], -1)
        xu_ok = complete & (xu >= 0)
        tail = ok & ~xu_ok
        n_time += int(xu_ok.sum())
        n_tail += int(tail.sum())
        ent_ok = np.flatnonzero(ok)
        if ent_ok.size == 0:
            continue
        nets = np.full(ent_ok.size, np.nan)
        ecal = np.full(ent_ok.size, -1, dtype=np.int64)
        xcal = np.full(ent_ok.size, -1, dtype=np.int64)
        eo = ent_c[ent_ok]
        entry = m["o"][eo]
        cf = m["cf1"] if face == "x1" else m["cf2"]
        ix = np.flatnonzero(xu_ok[ent_ok])
        if ix.size:
            xx = xu[ent_ok[ix]]
            cin, cout = cf[eo[ix]], cf[xx]
            nets[ix] = m["o"][xx] / entry[ix] * (1.0 - cout) \
                / (1.0 + cin) - 1.0
            ecal[ix] = m["pcal"][eo[ix]]
            xcal[ix] = m["pcal"][xx]
        it = np.flatnonzero(tail[ent_ok])
        if it.size:
            jj = np.where(m["lastfc"] > eo[it], m["lastfc"], eo[it])
            px = np.where(np.isfinite(m["c"][jj]), m["c"][jj], entry[it])
            cin, cout = cf[eo[it]], cf[jj]
            nets[it] = px / entry[it] * (1.0 - cout) / (1.0 + cin) - 1.0
            ecal[it] = m["pcal"][eo[it]]
            xcal[it] = m["pcal"][jj]
        good = np.isfinite(nets)
        sig_a.append(ts[ent_ok][good])
        net_a.append(nets[good])
        ecal_a.append(ecal[good])
        xcal_a.append(xcal[good])
    if not net_a:
        return ser, {"n_events": len(events), "n_filled": 0,
                     "rejects": {"limit_reject": n_rej, "susp_end": n_susp},
                     "exits": {"time": n_time, "tail": n_tail}}
    sc = np.concatenate(sig_a)
    nets = np.concatenate(net_a)
    ecal = np.concatenate(ecal_a)
    xcal = np.concatenate(xcal_a)
    cnt = np.bincount(sc, minlength=T_cal)
    span = np.maximum(xcal - ecal, 1)
    share = nets / (cnt[sc] * span)
    maxspan = int(span.max())
    offs = np.arange(maxspan)
    idxmat = ecal[:, None] + 1 + offs[None, :]
    keep = offs[None, :] < span[:, None]
    flat_idx = idxmat[keep]
    flat_w = np.repeat(share, span)
    m2 = flat_idx < T_cal
    ser = np.bincount(flat_idx[m2], weights=flat_w[m2], minlength=T_cal)
    return ser, {"n_events": len(events),
                 "n_filled": int(len(nets)),
                 "rejects": {"limit_reject": n_rej, "susp_end": n_susp},
                 "exits": {"time": n_time, "tail": n_tail}}


# ------------------------------------------------- virtual starts & robust
def seg_class(P, t0):
    s, m = P["sse"][t0], P["ma200"][t0]
    if not (np.isfinite(s) and np.isfinite(m)):
        return "na"
    s60 = P["sse"][max(t0 - 60, 0)]
    if not np.isfinite(s60):
        return "na"
    r60 = s / s60 - 1.0
    if s > m:
        return "bull" if r60 > 0.05 else "chop"
    return "deep_bear" if r60 < -0.15 else "bear"


def virtual_starts(P, series_by_cell):
    T = P["T"]
    starts = list(range(STARTS_FROM, T - WIN_DAYS))
    segs = np.array([seg_class(P, t0) for t0 in starts])
    sa = np.array(starts)
    ew = np.asarray(P["ew"], dtype=np.float64)
    ew_cs = np.cumsum(np.log1p(ew))
    out = {"n_starts": len(starts), "segments": {}}
    for cls in ("bull", "bear", "deep_bear", "chop", "na"):
        n = int((segs == cls).sum())
        out["segments"][cls] = {"n_starts": n,
                                "sufficient_sample": bool(n >= SEG_MIN)}
    rng = np.random.default_rng(SEED)
    cells = {}
    for name, series in series_by_cell.items():
        r = np.asarray(series, dtype=np.float64)
        cs = np.cumsum(np.log1p(r))
        wret = cs[sa + WIN_DAYS - 1] - cs[sa - 1]
        pw = ew_cs[sa + WIN_DAYS - 1] - ew_cs[sa - 1]
        beat = wret > pw
        seg_tab = {}
        for cls in ("bull", "bear", "deep_bear", "chop", "na"):
            m = segs == cls
            seg_tab[cls] = {"n": int(m.sum()),
                            "mean_win_ret": round(float(wret[m].mean()), 6)
                            if m.any() else None,
                            "beat_rate": round(float(beat[m].mean()), 4)
                            if m.any() else None}
        half = len(starts) // 2
        oos = {"first_half_mean": round(float(wret[:half].mean()), 6),
               "second_half_mean": round(float(wret[half:].mean()), 6)}
        fw = np.array_split(r, 5)
        wf = [round(float(x.mean() / x.std(ddof=1) * math.sqrt(PBP)), 4)
              if x.std(ddof=1) > 0 else 0.0 for x in fw]
        agree = valid = 0
        for _ in range(100):
            m = rng.random(len(starts)) < 0.5
            if not m.any() or m.all():
                continue
            valid += 1
            a, b_ = float(wret[m].mean()), float(wret[~m].mean())
            agree += int((a > 0) == (b_ > 0))
        cells[name] = {"mean_win_ret": round(float(wret.mean()), 6),
                       "beat_rate_6m": round(float(beat.mean()), 4),
                       "segments": seg_tab, "oos_halves": oos,
                       "walk_forward_sharpe": wf,
                       "split_sign_agreement_pct":
                           round(100.0 * agree / valid, 1) if valid else None}
    out["cells"] = cells
    return out


def robust_stats(series):
    """Block bootstrap (block=10) + sign-flip, 2000 each (law s3)."""
    r = np.asarray(series, dtype=np.float64)
    n = len(r)
    sd0 = r.std(ddof=1)
    obs = r.mean() / sd0 * math.sqrt(PBP) if sd0 > 0 else 0.0
    rng = np.random.default_rng(SEED)
    block = 10
    n_blocks = int(math.ceil(n / block))
    bb = np.empty(2000)
    offs = np.arange(block)
    for i in range(2000):
        pos = rng.integers(0, n_blocks, size=n_blocks)
        idx = (pos[:, None] * block + offs[None, :]).ravel()
        idx = idx[idx < n]
        bb[i] = r[idx].mean()
    sf = np.empty(2000)
    for i in range(2000):
        sgn = rng.integers(0, 2, size=n) * 2.0 - 1.0
        x = r * sgn
        sx = x.std(ddof=1)
        sf[i] = x.mean() / sx * math.sqrt(PBP) if sx > 0 else 0.0
    return {"obs_sharpe": round(obs, 4),
            "block_bootstrap_p95_mean": round(float(np.percentile(bb, 95)), 6),
            "block_bootstrap_p05_mean": round(float(np.percentile(bb, 5)), 6),
            "block_bootstrap_p_le_0": round(float((bb <= 0).mean()), 4),
            "sign_flip_p": round(float(
                (np.abs(sf) >= abs(obs)).mean()), 4)}


def d6_block(P, series_by_cell):
    """s1 reject face vs REGISTERED members (cn_rev_tilt_p1 ew6 canon)."""
    from cn_rev_tilt_p1 import REG6, load_member_rets, _corr
    member_rets, _member_cutoffs = load_member_rets()
    cal = pd.DatetimeIndex(P["idx"])
    out = {"reject_line": D6_REJECT, "members": list(REG6), "cells": {}}
    mat = {}
    for name, series in series_by_cell.items():
        s = pd.Series(np.asarray(series, dtype=np.float64), index=cal)
        per = {}
        for tid, mr in member_rets.items():
            v, ov = _corr(s, mr)
            per[tid] = {"corr": v, "overlap_days": ov}
        fin = {t: v["corr"] for t, v in per.items() if v["corr"] is not None}
        amax = max(fin, key=lambda k: abs(fin[k])) if fin else None
        out["cells"][name] = {"per_member": per,
                              "max_abs_corr": round(abs(fin[amax]), 4)
                              if amax else None,
                              "reject": bool(amax and
                                             abs(fin[amax]) >= D6_REJECT)}
        mat[name] = np.asarray(series, dtype=np.float64)
    names = list(mat)
    cross = {}
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b_ = mat[names[i]], mat[names[j]]
            m = np.isfinite(a) & np.isfinite(b_)
            if m.sum() > 20 and a[m].std() > 0 and b_[m].std() > 0:
                cross[f"{names[i]}|{names[j]}"] = round(float(
                    np.corrcoef(a[m], b_[m])[0, 1]), 4)
    out["same_batch_cross"] = cross
    return out


# ------------------------------------------------------------------ sobol
def sobol_params():
    """Sobol(3) scrambled, seed-sequence [SEED, 2000] (prereg s3.2.2);
    512 drawn (power-of-2 balance), first SOBOL_N consumed."""
    from scipy.stats import qmc
    eng = qmc.Sobol(d=3, scramble=True,
                    seed=np.random.default_rng([int(SEED), 2000]))
    pts = eng.random(SOBOL_DRAW_BALANCE)[:SOBOL_N]
    Ws = 10 + np.floor(pts[:, 0] * (60 - 10 + 1)).astype(int)
    Ks = 1 + np.floor(pts[:, 1] * (5 - 1 + 1)).astype(int)
    Hs = 5 + np.floor(pts[:, 2] * (20 - 5 + 1)).astype(int)
    return np.stack([Ws, Ks, Hs], axis=1)      # (SOBOL_N, 3)


def run_sobol(P):
    """Space-filling descriptive leg: per-draw re-encode (W,K) + vectorized
    time-exit x1 paths + bucket accounting. Sharded npy checkpoints."""
    os.makedirs(SOBOL_DIR, exist_ok=True)
    params = sobol_params()
    per = SOBOL_N // SOBOL_SHARDS
    rows_all = np.empty((SOBOL_N, 8))
    for s in range(SOBOL_SHARDS):
        path = os.path.join(SOBOL_DIR, f"shard{s}.npy")
        if os.path.exists(path):
            rows_all[s * per:(s + 1) * per] = np.load(path)
            continue
        chunk = np.empty((per, 8))
        for i in range(per):
            k = s * per + i
            W_, K_, H_ = (int(params[k, 0]), int(params[k, 1]),
                          int(params[k, 2]))
            ev, _le, _by = encode_events(P["cl"], P["sect"], P["in_u"],
                                         P["syms"], P["dates_d"], P["n_l2"],
                                         W_, K_)
            ser, cnt = vector_time_paths(P, ev, H_, face="x1")
            st = cell_stats(ser, P["dates_d"])
            chunk[i] = (W_, K_, H_, st["sharpe_full"], float(ser.mean()),
                        st["max_dd"], cnt["n_events"], cnt["n_filled"])
        np.save(path, chunk)
        rows_all[s * per:(s + 1) * per] = chunk
        print(f"  sobol shard {s + 1}/{SOBOL_SHARDS} done", flush=True)
    desc = {}
    for nm, arr in (("sharpe", rows_all[:, 3]), ("mean_daily", rows_all[:, 4]),
                    ("max_dd", rows_all[:, 5]), ("n_events", rows_all[:, 6]),
                    ("n_filled", rows_all[:, 7])):
        desc[nm] = {"p05": round(float(np.percentile(arr, 5)), 6),
                    "p25": round(float(np.percentile(arr, 25)), 6),
                    "p50": round(float(np.percentile(arr, 50)), 6),
                    "p75": round(float(np.percentile(arr, 75)), 6),
                    "p95": round(float(np.percentile(arr, 95)), 6),
                    "mean": round(float(arr.mean()), 6),
                    "min": round(float(arr.min()), 6),
                    "max": round(float(arr.max()), 6)}
    return {
        "n_draws": int(SOBOL_N),
        "space": {"W": [10, 60], "K_TOP": [1, 5], "H": [5, 20],
                  "grid": "integer"},
        "seed_sequence": f"[{int(SEED)}, 2000]",
        "engine_note": f"scipy qmc.Sobol(3) scrambled; {SOBOL_DRAW_BALANCE} "
                       "drawn (power-of-2 balance), first "
                       f"{SOBOL_N} consumed per prereg",
        "cost_face": "x1 (side_cost_v2)",
        "exit_face": "time-exit H (prereg s3.2.2 same-execution face)",
        "rows": [[int(r[0]), int(r[1]), int(r[2]), round(float(r[3]), 4),
                  round(float(r[4]), 8), round(float(r[5]), 6),
                  int(r[6]), int(r[7])] for r in rows_all],
        "description": desc,
        "claims_note": "descriptive only: NO N_eff, NO gates, NO "
                       "survivorship claims (prereg s3.2.2)",
    }


# ------------------------------------------------------------------ finalize
def _attr_row(batch, delta, total, gates, entries):
    d = json.load(open(ATT_JSON, encoding="utf-8"))
    row = {"batch": batch,
           "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
           "kind": "measurement", "cells_ledger_delta": delta,
           "ledger_total_after": total, "gates": gates,
           "entries": entries}            # r248 entries-list face
    own = [i for i, e in enumerate(d["entries"])
           if e.get("batch") == batch and e.get("kind") == "measurement"]
    if own:
        d["entries"][own[-1]] = row
    else:
        d["entries"].append(row)
    with open(ATT_JSON + ".tmp", "w", encoding="utf-8") as fh:
        json.dump(d, fh, ensure_ascii=False, indent=1)
    os.replace(ATT_JSON + ".tmp", ATT_JSON)


def finalize(P, cells_out, nulls, d6, vstarts, robust, sobol):
    series_by_cell = {n: cells_out[n]["x2"]["series"] for n in cells_out}
    # r259 prev-echo guard (re-finalize single-count law)
    prev_total = None
    if os.path.exists(OUT_JSON):
        try:
            with open(OUT_JSON, encoding="utf-8") as fh:
                prev_total = int(
                    json.load(fh)["trials_ledger"]["prev_total"])
        except Exception:
            prev_total = None
    head_base = (prev_total if prev_total is not None
                 else int(SG.ledger_head()["total"]))
    gates = {}
    for name, ser in series_by_cell.items():
        st = cells_out[name]["x2"]["stats"]
        g1 = SG.g1_prime_v2(st["sharpe_full"], ser, batch_cells=BATCH_CELLS,
                            pool="stock_b_layer",
                            null_pool={"values": nulls[name]["values"],
                                       "coverage": nulls[name]["coverage"]},
                            n_trades=cells_out[name]["x2"]["n_filled"],
                            n_entries=cells_out[name]["x2"]["n_filled"],
                            n_eff_override=head_base + BATCH_CELLS)
        dsr = SG.deflated_sharpe_ratio(ser, n_trials=g1["skill_line"]["n_eff"])
        gates[name] = {"g1_prime_v2": g1, "dsr": dsr}
    mat = pd.DataFrame({n: np.asarray(s, dtype=np.float64)
                        for n, s in series_by_cell.items()})
    pbo = cscv_pbo(mat)
    for name in gates:
        gates[name]["g2"] = SG.g2_registration_v2(
            gates[name]["g1_prime_v2"]["pass_v2"],
            gates[name]["dsr"], float(pbo["pbo"]))
        gates[name]["d6_reject"] = bool(d6["cells"][name]["reject"])

    ledger = SG.append_ledger(BATCH_NAME, BATCH_CELLS,
                              file_name="cn_sector_leader_p1",
                              evidence_cutoff=EVIDENCE_CUTOFF,
                              prev_total=prev_total)
    _attr_row(BATCH_NAME, BATCH_CELLS, int(ledger["total"]),
              {"g1_pass": {n: gates[n]["g1_prime_v2"]["pass_v2"]
                          for n in gates},
               "g2_eligible": {n: gates[n]["g2"]["eligible_v2"]
                               for n in gates},
               "d6_reject": {n: gates[n]["d6_reject"] for n in gates},
               "family_pbo": pbo},
              {"entries_x2": {n: cells_out[n]["x2"]["n_filled"]
                              for n in cells_out},
               "events": {n: cells_out[n]["x2"]["n_events"]
                          for n in cells_out},
               "limit_face_excluded": int(
                   P["face"]["census"]["limit_face_excluded_events"]),
               "rejects_x2": {n: cells_out[n]["x2"]["rejects"]
                              for n in cells_out}})

    result = {
        "batch": BATCH_NAME,
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "cutoff_meta": SG.cutoff_meta(EVIDENCE_CUTOFF),
        "prereg": "research/CN_SECTOR_LEADER_PREREG.md (@b3d72924 freeze)",
        "seed": {"base": SEED, "k": K_NULLS,
                 "sobol_seedseq": f"[{int(SEED)}, 2000]"},
        "panel": P["face"],
        "cost": {"face_judged": "x2 (side_cost_x2, V2 components doubled; "
                                "array face 2x V2, identity selftested)",
                 "x1": "side_cost_v2 disclosure column",
                 "leg_notional_cny": N0,
                 "adv20": "NaN-aware rolling-20 amount mean on the member "
                          "own index; NaN -> krules 10bp fallback (V2 call)"},
        "cells": {n: {f: {"stats": cells_out[n][f]["stats"],
                          "n_events": cells_out[n][f]["n_events"],
                          "n_filled": cells_out[n][f]["n_filled"],
                          "rejects": cells_out[n][f]["rejects"],
                          "exits": cells_out[n][f]["exits"],
                          "cohorts": cells_out[n][f]["cohorts"],
                          "empty_cohorts": cells_out[n][f]["empty_cohorts"],
                          "max_cohort": cells_out[n][f]["max_cohort"]}
                      for f in ("x1", "x2")} for n in cells_out},
        "nulls": nulls, "d6": d6, "virtual_starts": vstarts,
        "robust": robust, "family_pbo": pbo, "sobol": sobol,
        "gates": gates, "trials_ledger": ledger,
        "batch_disclosure": {
            "rule": "ann>0 AND OOS(>=2025-01-01) ann>0 AND maxDD>=-35% "
                    "(prereg s4 disclosure columns)",
            "cells_ok": {n: bool(
                cells_out[n]["x2"]["stats"]["ann_ret"] > 0 and
                (cells_out[n]["x2"]["stats"]["oos_ann"] or -1) > 0 and
                cells_out[n]["x2"]["stats"]["max_dd"] >= -0.35)
                for n in cells_out}},
        "verdict_line": ("judged per prereg s4 on x2 faces; judged-negative "
                         "= slot closed + new-evidence reopen note "
                         "(claim != verify, boundary disclosure c)"),
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_JSON + ".tmp", "w", encoding="utf-8") as fh:
        json.dump(result, fh, ensure_ascii=False, indent=1)
    os.replace(OUT_JSON + ".tmp", OUT_JSON)
    rows = []
    for n in cells_out:
        for f in ("x1", "x2"):
            rows.append({"cell": n, "face": f,
                         **cells_out[n][f]["stats"]})
    pd.DataFrame(rows).to_csv(OUT_CSV, index=False)
    return result


# ------------------------------------------------------------------ driver
def cmd_run():
    global SEED
    SEED = SG.SEED_REGISTRY["cn_sector_leader_p1"]
    if _free_ram_gb() < RAM_FLOOR_GB:
        print("free-RAM floor refused")
        return 3
    t0 = time.time()
    P, err = load_panel()
    if err:
        return gate_refuse(err)
    print(f"panel ok: universe={P['face']['universe_n']} "
          f"events={P['face']['census']['trigger_events_n']} "
          f"({time.time() - t0:.0f}s)", flush=True)
    os.makedirs(CELL_DIR, exist_ok=True)
    os.makedirs(NULL_DIR, exist_ok=True)

    cells_out = {}
    for cell in CELLS:
        name = cell["name"]
        cells_out[name] = {}
        for face in ("x1", "x2"):
            ck = os.path.join(CELL_DIR, f"{name}_{face}.json")
            if os.path.exists(ck):
                blob = json.load(open(ck, encoding="utf-8"))
                blob["series"] = np.load(ck.replace(".json", ".npy"))
            else:
                r = run_cell(P, cell, face, P["T"])
                np.save(ck.replace(".json", ".npy"), r["series"])
                blob = {"series": r["series"],
                        "stats": cell_stats(r["series"], P["dates_d"]),
                        "n_events": r["n_events"], "n_filled": r["n_filled"],
                        "rejects": r["rejects"], "exits": r["exits"],
                        "cohorts": r["cohorts"],
                        "empty_cohorts": r["empty_cohorts"],
                        "max_cohort": r["max_cohort"]}
                dump = {k: v for k, v in blob.items() if k != "series"}
                with open(ck + ".tmp", "w", encoding="utf-8") as fh:
                    json.dump(dump, fh, ensure_ascii=False, indent=1)
                os.replace(ck + ".tmp", ck)
                print(f"  cell {name}/{face}: events={r['n_events']} "
                      f"filled={r['n_filled']} "
                      f"({time.time() - t0:.0f}s)", flush=True)
            cells_out[name][face] = blob

    tables = {}
    nulls = {}
    for H in (H_FIX, H_LONG):
        tables[H] = build_null_table(P, H, "cf2")
        print(f"null table H={H} built ({time.time() - t0:.0f}s)", flush=True)
    for cell in CELLS:
        nulls[cell["name"]] = run_cell_nulls(
            P, cell, tables, cells_out[cell["name"]]["x2"]["n_events"])
        print(f"  nulls {cell['name']}: mu="
              f"{nulls[cell['name']]['coverage']['mu']} "
              f"({time.time() - t0:.0f}s)", flush=True)

    series_by_cell = {n: cells_out[n]["x2"]["series"] for n in cells_out}
    d6 = d6_block(P, series_by_cell)
    vstarts = virtual_starts(P, series_by_cell)
    robust = {n: robust_stats(s) for n, s in series_by_cell.items()}
    print(f"d6/vstarts/robust done ({time.time() - t0:.0f}s)", flush=True)
    sobol = run_sobol(P)
    print(f"sobol done ({time.time() - t0:.0f}s)", flush=True)
    res = finalize(P, cells_out, nulls, d6, vstarts, robust, sobol)
    print(f"finalize ok: cells={len(res['cells'])} "
          f"ledger={res['trials_ledger']['total']} "
          f"elapsed={time.time() - t0:.0f}s")
    return 0


# ------------------------------------------------------------------ selftest
def _mk_fixture(tmp, T=460):
    """Hermetic synthetic panel: bars parquets + p1c-style cache + SW xlsx
    taxonomy + mask + sse, with planted sector-leader windows (all prices
    flat-10 background; rallies snap back to base when the window ends):
      w0 100-130  600010 rallies BEFORE its classification start (day 300)
                  -> zero events (point-in-time unmapped control)
      w1 150-165  600001 rally; gap-up +10% open at day 153 -> limit_reject
      w2 200-215  600002 rally; all-NaN day 201 -> suspension roll
      w3 250-265  600003 rally then -25% close crash at 262 -> stop arm
      w4 300-325  600004 rally then -1%/day decay -> hot death -> ebb arm
      w6 350-365  300001 (chinext) rally, +20% close day 354 -> WIDE-floor
                  limit exclusion (no event that day)
      w7 370-385  688001 (star) rally, +20% close day 374 -> ditto
      w8 395-410  600001 + 300001 simultaneous rallies -> 2-sector cohorts
      w5 445-459  600005 rally through panel end -> tail marks + susp_end
      600006 reclassified 3403 -> 2102 at day 420 (segment point-in-time)
      600091 not_ok / 600092 60-row file / 600093 thin amount / 600094
      early-last file -> skip ledger {not_ok,rows,last,liq} = 1 each
    """
    bars = os.path.join(tmp, "bars")
    os.makedirs(bars)
    cal = pd.date_range(end=EVIDENCE_CUTOFF, periods=T,
                        freq="B").as_unit("us")
    cal_arr = cal.values

    a_syms = ["600001", "600002", "600003", "600004", "600005", "600010"]
    b_syms = ["600006", "600007", "600008", "600009"]
    c_syms = ["300001", "300002", "300003", "300004", "688001"]
    ctrl = ["600091", "600092", "600093", "600094"]
    all_syms = a_syms + b_syms + c_syms + ctrl
    N = len(all_syms)

    def base_frame(sym):
        df = pd.DataFrame(index=range(T))
        df["date"] = cal
        for name in ("open", "close", "high", "low", "volume", "amount"):
            df[name] = np.nan
        df["close"] = 10.0
        df["open"] = 10.0
        df["high"] = 10.01
        df["low"] = 9.99
        df["volume"] = 1e6
        df["amount"] = 5e7
        if sym == "600093":
            df["amount"] = 0.5                      # liq skip
        return df

    def _set_path(df, c):
        df["close"] = c
        df["open"] = np.concatenate([[c[0]], c[:-1]])   # open = prev close
        df["high"] = np.maximum(df["open"].values, c) + 0.01
        df["low"] = np.minimum(df["open"].values, c) - 0.01

    def rally(df, start, days, rate, wide_day=None, gapup_day=None):
        c = df["close"].values.copy()
        for i in range(1, days + 1):
            c[start + i] = c[start + i - 1] * (1.0 + rate)
        if wide_day is not None:
            c[wide_day] = c[wide_day - 1] * 1.20    # +20% close day
        _set_path(df, c)
        if gapup_day is not None:
            o = df["open"].values.copy()
            o[gapup_day] = c[gapup_day - 1] * 1.10  # +10% gap-up open
            df["open"] = o
            df.loc[gapup_day, "high"] = max(o[gapup_day], c[gapup_day]) + 0.01
            df.loc[gapup_day, "low"] = min(o[gapup_day], c[gapup_day]) - 0.01

    frames = {s: base_frame(s) for s in all_syms}
    rally(frames["600010"], 100, 10, 0.015)                 # w0 unmapped
    rally(frames["600001"], 150, 10, 0.015)                 # w1 rally
    rally(frames["600002"], 200, 10, 0.015)                 # w2
    frames["600002"].loc[201, ["open", "close", "high", "low",
                               "volume", "amount"]] = np.nan  # susp day
    rally(frames["600003"], 250, 10, 0.015)                 # w3 rally
    c3 = frames["600003"]["close"].values.copy()
    c3[262] = c3[261] * 0.75                                # -25% crash
    _set_path(frames["600003"], c3)
    rally(frames["600004"], 300, 10, 0.015)                 # w4 rally
    c4 = frames["600004"]["close"].values.copy()
    c4[310] = c4[309]                                       # flat pivot
    for i in range(1, 16):
        c4[310 + i] = c4[309 + i] * 0.99                    # decay 311-325
    _set_path(frames["600004"], c4)
    rally(frames["300001"], 350, 8, 0.05, wide_day=354)      # w6 chinext
    rally(frames["688001"], 370, 8, 0.05, wide_day=374)     # w7 star
    rally(frames["600001"], 395, 8, 0.015)                   # w8 dual A
    rally(frames["300001"], 395, 8, 0.05)                    # w8 dual C
    rally(frames["600005"], 445, 14, 0.015)                  # w5 tail
    # w1 gap-up entry-reject day applied LAST: _set_path recomputes the
    # whole open column, so any later rally on the same frame would erase
    # a gap-up set earlier (w8 shares 600001 with w1)
    rally(frames["600001"], 150, 0, 0.0, gapup_day=153)      # gap-up only
    frames["600092"] = frames["600092"].iloc[T - 60:].reset_index(drop=True)
    frames["600094"] = frames["600094"].iloc[:T - 10].reset_index(drop=True)
    for sym, df in frames.items():
        df.to_parquet(os.path.join(bars, f"{sym}.parquet"))

    pd.DataFrame({"code": all_syms,
                  "ok_static": [s != "600091" for s in all_syms]}).to_csv(
        os.path.join(tmp, "mask.csv"), index=False)
    pd.DataFrame({"date": cal,
                  "close": np.linspace(3000, 3400, T)}).to_parquet(
        os.path.join(tmp, "sse.parquet"))

    # taxonomy xlsx: all 19 symbols covered (100% coverage gate); 600010
    # classified from day 300; 600006 reclassified 3403 -> 2102 at day 420
    d300 = str(cal[300].date())
    d420 = str(cal[420].date())
    rows = []
    for s in a_syms:
        rows.append([s, d300 if s == "600010" else "1990-01-01",
                     "210200", "1990-01-01"])
    for s in b_syms:
        rows.append([s, "1990-01-01", "340300", "1990-01-01"])
        if s == "600006":
            rows.append([s, d420, "210200", d420])
    for s in c_syms:
        rows.append([s, "1990-01-01", "430100", "1990-01-01"])
    for s in ctrl:
        rows.append([s, "1990-01-01", "340300", "1990-01-01"])
    xlsx = os.path.join(tmp, "sw.xlsx")
    pd.DataFrame(rows, columns=["股票代码", "开始日期", "行业代码",
                                "更新时间"]).to_excel(xlsx, index=False)

    # cache npy: aligned calendar x N, float32, NaN elsewhere, date-mapped
    syms_sorted = sorted(all_syms)
    colmap = {s: i for i, s in enumerate(syms_sorted)}
    cache = os.path.join(tmp, "cache")
    os.makedirs(cache)
    for fld in ("open", "high", "low", "close", "volume", "amount"):
        arr = np.full((T, N), np.nan, dtype=np.float32)
        for s in all_syms:
            df = frames[s]
            pos = np.searchsorted(cal_arr, df["date"].values)
            vals = df[fld].values
            fin = np.isfinite(vals)
            arr[pos[fin], colmap[s]] = vals[fin].astype(np.float32)
        np.save(os.path.join(cache, f"{fld}.npy"), arr)
    np.save(os.path.join(cache, "dates.npy"), cal.values)
    json.dump({"batch": "fixture", "generated": "FIXTURE-CACHE-STAMP",
               "shape": {"T": T, "N": N}},
              open(os.path.join(cache, "meta.json"), "w"))
    return {"bars": bars, "cache": cache, "syms": syms_sorted,
            "all_syms": all_syms, "N": N, "T": T, "xlsx": xlsx}


def cmd_selftest():
    global BARS, CACHE, MASK, XLS, SSE, PROBE_JSON, XCC_JSON, OUT_DIR, \
        CELL_DIR, NULL_DIR, SOBOL_DIR, OUT_JSON, OUT_CSV, ATT_JSON, SEED, \
        K_NULLS, NULL_SHARDS, SOBOL_N, SOBOL_SHARDS, SOBOL_DRAW_BALANCE, \
        N_FILES_EXPECT, UNIVERSE_EXPECT, CENSUS_EXPECT, LIMIT_EXCL_EXPECT, \
        CACHE_STAMP_EXPECTED, XLS_SHA256_FROZEN, MIN_ROWS, MIN_AMT20, N0
    tmp = tempfile.mkdtemp(prefix="cn_sector_leader_selftest_")
    K_NULLS, NULL_SHARDS = 30, 2       # skill_line_v2 thin-line floor = 30
    SOBOL_N, SOBOL_SHARDS, SOBOL_DRAW_BALANCE = 6, 2, 8
    SEED = 20277200
    N0 = 1.0e5
    fx = _mk_fixture(tmp)
    BARS = fx["bars"]
    CACHE = fx["cache"]
    MASK = os.path.join(tmp, "mask.csv")
    SSE = os.path.join(tmp, "sse.parquet")
    XLS = fx["xlsx"]
    XLS_SHA256_FROZEN = hashlib.sha256(open(XLS, "rb").read()).hexdigest()
    CACHE_STAMP_EXPECTED = "FIXTURE-CACHE-STAMP"
    XCC_JSON = os.path.join(tmp, "xcc.json")
    json.dump({"bars_files": len(fx["all_syms"]),
               "cache_last_date": EVIDENCE_CUTOFF,
               "600001": {"finite_mask_mismatches": 0}},
              open(XCC_JSON, "w"))
    OUT_DIR = os.path.join(tmp, "out")
    CELL_DIR = os.path.join(OUT_DIR, "cells")
    NULL_DIR = os.path.join(OUT_DIR, "nulls")
    SOBOL_DIR = os.path.join(OUT_DIR, "sobol")
    OUT_JSON = os.path.join(OUT_DIR, "p1_results.json")
    OUT_CSV = os.path.join(OUT_DIR, "cells_summary.csv")
    ATT_JSON = os.path.join(tmp, "attr.json")
    os.makedirs(CELL_DIR, exist_ok=True)
    os.makedirs(NULL_DIR, exist_ok=True)
    os.makedirs(SOBOL_DIR, exist_ok=True)
    json.dump({"entries": []}, open(ATT_JSON, "w"))
    N_FILES_EXPECT = len(fx["all_syms"])
    MIN_ROWS = 100
    MIN_AMT20 = 1.0
    ok = []

    def check(name, cond):
        ok.append((name, bool(cond)))

    # fixture probe: derive the census on the synthetic panel with the SAME
    # encode path (planted universe = 19 minus 4 control skips), freeze as
    # the gate reference (KLINE selftest face)
    idx = pd.to_datetime(np.load(os.path.join(CACHE, "dates.npy")),
                         unit="us")
    dates_d = idx.values.astype("datetime64[D]")
    cl = np.load(os.path.join(CACHE, "close.npy")).astype(np.float64)
    syms = fx["syms"]
    N = fx["N"]
    planted = [s for s in syms
               if s not in ("600091", "600092", "600093", "600094")]
    in_u = np.zeros(N, dtype=bool)
    in_u[[syms.index(s) for s in planted]] = True
    tax, terr = load_taxonomy(idx, syms)
    check("taxonomy parse + coverage 100%", terr is None)
    ev0, le0, _by = encode_events(cl, tax["sect"], in_u, syms, dates_d,
                                  tax["n_l2"], W, K_TOP)
    PROBE_JSON = os.path.join(tmp, "probe.json")
    json.dump({"panel": {"cutoff": EVIDENCE_CUTOFF},
               "universe_n": len(planted),
               "universe_skipped": {"not_ok": 1, "rows": 1, "last": 1,
                                    "liq": 1},
               "EF_params": {"W": W, "K_TOP": K_TOP, "MIN_SECT": MIN_SECT,
                             "limit_excl_tol": LIMIT_EXCL_TOL},
               "census": {"trigger_events_n": len(ev0),
                          "limit_face_excluded_events": le0,
                          "first": str(dates_d[ev0[0][0]]),
                          "last": str(dates_d[ev0[-1][0]])}},
              open(PROBE_JSON, "w"))
    UNIVERSE_EXPECT = len(planted)
    CENSUS_EXPECT = len(ev0)
    LIMIT_EXCL_EXPECT = le0

    # structural expectations
    leaders = {syms[e[1]] for e in ev0}
    check("leader set == planted 7 (no 600010: unmapped pre-300)",
          leaders == {"600001", "600002", "600003", "600004", "600005",
                      "300001", "688001"})
    check("limit-face exclusions == 2 (w6+w7 +20% days)", le0 == 2)
    a_id = tax["l2_codes"].index("2102") + 1
    c_id = tax["l2_codes"].index("4301") + 1
    b_id = tax["l2_codes"].index("3403") + 1
    check("all events in sectors A/C, none in B (MIN_SECT+EW controls)",
          all(e[2] in (a_id, c_id) for e in ev0)
          and not any(e[2] == b_id for e in ev0))
    check("no event on the +20% wide-floor days (354/374)",
          not any(e[0] in (354, 374) for e in ev0))
    col600006 = syms.index("600006")
    check("point-in-time reclass: 600006 in B at 419, in A at 420",
          tax["sect"][419, col600006] == b_id
          and tax["sect"][420, col600006] == a_id)

    # hermetic stubs: shared-library state faces isolated from the real repo
    _ne, _pb, _al, _lh = SG.n_eff, SG.passive_baseline, SG.append_ledger, \
        SG.ledger_head
    SG.n_eff = lambda bc, rd=None: int(bc)
    SG.passive_baseline = lambda pool, rd=None: 0.4606
    SG.append_ledger = lambda *a, **k: {"prev_total": 0, "total": 100,
                                        "batch": BATCH_NAME}
    SG.ledger_head = lambda rd=None: {"total": 500, "file": None,
                                      "note": None}
    _real_cscv = globals()["cscv_pbo"]
    globals()["cscv_pbo"] = lambda mat: {"pbo": 0.1}

    try:
        P, err = load_panel()
        check("panel gate battery pass", err is None)
        if err:
            raise RuntimeError(err)
        check("universe n == planted 15", P["face"]["universe_n"] == 15)
        check("skip ledger == planted",
              P["face"]["skip"] == {"not_ok": 1, "rows": 1, "last": 1,
                                    "liq": 1})
        check("census gate re-derive == frozen probe",
              P["face"]["census"]["trigger_events_n"] == CENSUS_EXPECT
              and P["face"]["census"]["limit_face_excluded_events"]
              == LIMIT_EXCL_EXPECT)

        # [arms] per-event sim faces (FIX10 = time arm)
        cell_fix = CELLS[0]
        r0 = run_cell(P, cell_fix, "x2", P["T"])
        check("near-limit entry reject counted (w1 gap-up)",
              r0["rejects"]["limit_reject"] >= 1)
        check("susp_end rejects (w5 last-day signal)",
              r0["rejects"]["susp_end"] >= 1)
        check("tail marks (w5 panel-end holds)", r0["exits"]["tail"] >= 1)
        check("time exits present", r0["exits"]["time"] >= 1)
        check("cohort of 2 on the w8 dual-sector day",
              r0["max_cohort"] == 2)

        # suspension roll: signal day 201, NaN day 201, entry at 202
        mi2 = [j for j, m in P["members"].items()
               if m["sym"] == "600002"][0]
        m2 = P["members"][mi2]
        net2, ec2, xc2, tag2 = sim_trade(P, mi2, 201, a_id, cell_fix, "x2")
        check("suspension roll entry at first tradable after NaN",
              tag2 == "time" and ec2 == 202)

        # x2 cost math: hand formula on the rolled trade
        eo2 = int(np.searchsorted(m2["pcal"], 202))
        cin = side_cost_x2(N0, m2["adv"][eo2]) / N0
        xo2 = eo2 + H_FIX
        cout = side_cost_x2(N0, m2["adv"][xo2]) / N0
        exp_net = m2["o"][xo2] / m2["o"][eo2] * (1 - cout) / (1 + cin) - 1
        check("x2 cost math exact", tag2 == "time" and
              abs(net2 - exp_net) < 1e-12)
        samp = np.arange(0, m2["n"], max(1, m2["n"] // 40))
        check("cf1 array == direct side_cost_v2 calls",
              np.allclose(m2["cf1"][samp],
                          np.array([side_cost_v2(N0, m2["adv"][i]) / N0
                                    for i in samp]), equal_nan=True))
        check("cf2 array == 2x cf1 (x2 pointwise identity)",
              np.allclose(2.0 * m2["cf1"][samp], m2["cf2"][samp],
                          equal_nan=True))
        check("side_cost_x2 == 2x side_cost_v2 (spot, incl NaN adv)",
              all(side_cost_x2(N0, m2["adv"][i]) ==
                  2.0 * side_cost_v2(N0, m2["adv"][i]) for i in samp))

        # stop arm: -25% close crash at 262 -> exit next open
        r_stop = run_cell(P, CELLS[3], "x2", P["T"])
        check("stop arm fires on the -25% crash",
              r_stop["exits"]["stop"] >= 1)
        # ebb arm: w4 hot death -> ebb exits; FIX cell has none
        r_ebb = run_cell(P, CELLS[2], "x2", P["T"])
        check("ebb arm fires (w4 hot death) and FIX10 has zero ebb",
              r_ebb["exits"]["ebb"] >= 1 and r0["exits"]["ebb"] == 0)

        # vector_time_paths == per-event sim_trade on the time-exit face
        ev_w1 = [e for e in P["events"] if 150 <= e[0] <= 160]
        ser_v, cnt_v = vector_time_paths(P, ev_w1, H_FIX, face="x2")
        by_day = {}
        for t, mi, sid in ev_w1:
            net, ecal, xcal, tag = sim_trade(P, mi, t, sid, cell_fix, "x2")
            if net is not None:
                by_day.setdefault(t, []).append((net, ecal, xcal))
        ser_l = np.zeros(P["T"])
        for t, fl_ in by_day.items():
            for net, ecal, xcal in fl_:
                span = max(1, xcal - ecal)
                ser_l[min(ecal + 1, P["T"]):min(xcal + 1, P["T"])] += \
                    net / len(fl_) / span
        check("vector time-exit == per-event loop (w1 window)",
              cnt_v["n_filled"] == sum(len(v) for v in by_day.values())
              and np.allclose(ser_v, ser_l, atol=1e-12))

        # null tables + own pools, deterministic
        tbl10 = build_null_table(P, H_FIX, "cf2")
        check("null table nonempty", int(tbl10["ok"].sum()) > 100)
        v1 = null_draw(tbl10, np.random.default_rng(SEED), 5, P["T"])
        v2 = null_draw(tbl10, np.random.default_rng(SEED), 5, P["T"])
        check("null draw deterministic", v1 == v2 and np.isfinite(v1))
        tbl_by_H = {H_FIX: tbl10,
                    H_LONG: build_null_table(P, H_LONG, "cf2")}
        nulls = {}
        for c in CELLS:
            nulls[c["name"]] = run_cell_nulls(
                P, c, tbl_by_H, len(P["events"]))
        check("null pools 4 x 30 finite", len(nulls) == 4 and all(
            len(v["values"]) == 30 and np.isfinite(v["values"]).all()
            for v in nulls.values()))

        # cells both faces + stats
        cells_out = {}
        for c in CELLS:
            for face in ("x1", "x2"):
                rr = run_cell(P, c, face, P["T"])
                cells_out.setdefault(c["name"], {})[face] = {
                    "series": rr["series"],
                    "stats": cell_stats(rr["series"], P["dates_d"]),
                    "n_events": rr["n_events"], "n_filled": rr["n_filled"],
                    "rejects": rr["rejects"], "exits": rr["exits"],
                    "cohorts": rr["cohorts"],
                    "empty_cohorts": rr["empty_cohorts"],
                    "max_cohort": rr["max_cohort"]}
        check("cells 4x2", len(cells_out) == 4 and all(
            len(v) == 2 for v in cells_out.values()))

        # B7b contract leg (r297 kenglu): every st[...] key subscripted
        # downstream by finalize/gates/disclosure must exist in cell_stats
        stc = cell_stats(cells_out["LDR-FIX10"]["x2"]["series"],
                         P["dates_d"])
        check("B7b cell_stats downstream key contract (sharpe_full et al)",
              {"sharpe_full", "ann_ret", "max_dd", "oos_ann"}
              <= set(stc) and stc["sharpe_full"] is not None
              and stc["oos_ann"] is not None)

        # virtual starts / robust
        sbc = {n: cells_out[n]["x2"]["series"] for n in cells_out}
        vs = virtual_starts(P, sbc)
        check("vstarts census",
              vs["n_starts"] == P["T"] - WIN_DAYS - STARTS_FROM)
        rb = robust_stats(sbc["LDR-FIX10"])
        check("robust finite", np.isfinite(rb["obs_sharpe"]) and
              0.0 <= rb["sign_flip_p"] <= 1.0)

        # sobol mini: deterministic, in-grid, finite
        sb1 = run_sobol(P)
        rows1 = [tuple(r) for r in sb1["rows"]]
        for f in os.listdir(SOBOL_DIR):
            os.remove(os.path.join(SOBOL_DIR, f))
        sb2 = run_sobol(P)
        rows2 = [tuple(r) for r in sb2["rows"]]
        check("sobol deterministic + in-grid + finite",
              rows1 == rows2 and len(rows1) == 6 and all(
                  10 <= r[0] <= 60 and 1 <= r[1] <= 5 and 5 <= r[2] <= 20
                  and np.isfinite(r[3]) and np.isfinite(r[4])
                  and np.isfinite(r[5]) for r in rows1))

        # D6 face: real member files read repo paths (hermetic tmp has
        # none) -> stub dict passed into finalize (arg face, KLINE face)
        d6 = {"cells": {n: {"reject": False} for n in sbc}}

        # finalize product (stubbed SG faces)
        res = finalize(P, cells_out, nulls, d6, vs,
                       {"LDR-FIX10": rb}, sb1)
        check("finalize product", os.path.exists(OUT_JSON) and
              res["trials_ledger"]["total"] == 100)
        check("cutoff_meta key",
              "cutoff_meta" in res and
              res["evidence_cutoff"] == EVIDENCE_CUTOFF)
        att = json.load(open(ATT_JSON, encoding="utf-8"))
        check("attrition row entries face",
              att["entries"][-1]["batch"] == BATCH_NAME and
              "entries" in att["entries"][-1] and
              "limit_face_excluded" in att["entries"][-1]["entries"])
    finally:
        SG.n_eff, SG.passive_baseline, SG.append_ledger = _ne, _pb, _al
        SG.ledger_head = _lh
        globals()["cscv_pbo"] = _real_cscv
        shutil.rmtree(tmp, ignore_errors=True)

    n_ok = sum(1 for _, v in ok if v)
    print(f"cn_sector_leader_p1 selftest: {n_ok}/{len(ok)} PASS")
    for name, v in ok:
        if not v:
            print(f"  FAIL: {name}")
    return 0 if n_ok == len(ok) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "selftest"])
    a = ap.parse_args()
    if a.cmd == "selftest":
        return cmd_selftest()
    if os.path.exists(OUT_JSON) and \
            os.environ.get("CN_SECTOR_LEADER_P1_REFINALIZE") != "1":
        print("idempotent no-op: p1_results.json exists "
              "(CN_SECTOR_LEADER_P1_REFINALIZE=1 = only redo)")
        return 0
    return cmd_run()


if __name__ == "__main__":
    sys.exit(main())
