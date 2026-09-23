"""P-4 batch 2 stock-pool screen -- R38 of research/shortline/P4_BATCH2.md s7.

R38 split per O-1820 CEO red-line gate (cleared round 42 -- see
research/shortline/R38_RUN_CLEARANCE.md):
  R38-a  `panel`   build-once float32 price panel + validation gates
                   (delivered; results/shortline_p4_batch2_panel.json).
  R38-b  `probe`   shared-state build + ONE limitup_mom@default run:
                   timing probe (spec s7: probe first, then fix null
                   capacity). Also unit-sanity prints (pct/amount scale).
         `run`     full pre-registered batch: 10 family points (first_board
                   is CE-only per spec s4) -> 19 gate cells + 9 x2-cost
                   info runs + 40 random nulls (20 seeds x 2 exit regimes,
                   paired) + 2 passive nulls. Checkpointed per-run to
                   results/p4_batch2_runs.jsonl (resume-safe, deterministic
                   per key); final verdict JSON+CSV written only when every
                   run key is on disk. Lock file guards against double-run.
         `status`  poll progress (jsonl count vs total, final JSON done?).

Red lines honored: engine/exit_rules.py untouched (fill_guard was the R37
additive, already gated); T+1 untouched; stock cost = 2x ETF FeeSchedule
via CostPatch(2) (= 0.0026082 roundtrip, G6-verified) on EVERY run
(costs-always-on); x2 stress = CostPatch(4).

R38-b builder constraints (clearance s3, frozen):
  688 volume=100x true shares -- this batch's builders consume volume only
  in per-stock RATIOS (vol_ratio = vol / roll5(vol)), which are
  scale-invariant -> pit not triggered; no turnover/osh use. Recorded.
  Limit detection = raw pct_chg + same-day price relations (never qfq
  close/preclose); board-truth table: main 10%, chinext 10%->20% on
  2020-08-24, star 20%; +-0.5pp band.
  ST-regime proxy (spec s2) is board-aware: the 5%-seal proxy is only
  meaningful where the board limit is 10% (main board + chinext pre-2020);
  20%-board segments are exempt (normal 20% stocks seal near 5% closes
  routinely -> literal cross-board read would false-flag; r36 scan's own
  rationale says "main-board normal stocks never seal 5%").

Universe/eligibility (spec s2, screen-time side-join per clearance s2):
  static b_layer_mask.csv ok_static (O-1820 item3b) + dynamic per-day:
  roll20 mean amount >= 5e7, close >= 1, listing >= 20 bars, last bar
  within 250 td, not in ST-regime segment. Liquidity is an ENTRY-day gate
  ("进入日计算，退出后不再依赖") -- positions may outlive eligibility.

G1' gate (spec s5, five clauses): full Sharpe > vi_format where
vi = max(in-batch random-null p95 of that exit format, passive monthly-EW
Sharpe + 0.10); annual > 0; max_dd >= -0.35; >= 30 trades; OOS double
positive. Core48 lines (0.4004/0.3521/0.4229) NOT reused (new domain).
Survivors = G1' candidates only; NO registration this batch (G2 deepening
requires its own pre-registration).

Trial ledger: prev total 2020 (shortline_p4_batch2a.json) + 68 engine runs
(19 gate cells + 9 x2 info + 40 nulls) + 2 passive = 2090.
"""
import hashlib
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

BARS_DIR = os.path.join(ROOT, "Money02", "data", "bars")
CACHE_DIR = os.path.join(ROOT, "Money02", "data", "cache", "p4_batch2_panel")
OUT_JSON = os.path.join(ROOT, "results", "shortline_p4_batch2_panel.json")
CLEARANCE = os.path.join(ROOT, "research", "shortline", "R38_RUN_CLEARANCE.md")
MASK_CSV = os.path.join(ROOT, "data", "fundamental", "b_layer_mask.csv")
LHB_PATH = os.path.join(ROOT, "Money02", "data", "lhb", "lhb_detail.parquet")
RUNS_JSONL = os.path.join(ROOT, "results", "p4_batch2_runs.jsonl")
FINAL_JSON = os.path.join(ROOT, "results", "shortline_p4_batch2.json")
FINAL_CSV = os.path.join(ROOT, "research", "shortline", "p4_batch2_results.csv")
LOCK = os.path.join(ROOT, "results", "p4_batch2_run.lock")
LOG_LEDGER = os.path.join(ROOT, "results", "shortline_p4_batch2a.json")

WINDOW_START = np.datetime64("2015-01-01")
CUTOFF = np.datetime64("2026-09-22")
MIN_BARS = 20
COLS = ["open", "high", "low", "close", "volume", "amount", "pct_chg"]
WORKERS_PANEL = 12      # panel build workers (O-1738: bm-b <= 12)
SPOT_SYMS = ["000001", "300750", "688981"]
DET_PICK_STRIDE = 97

# ---- R38-b constants (frozen P4_BATCH2.md s3/s4/s5) ----
CHINEXT_20_FROM = np.datetime64("2020-08-24")   # board-truth table
SEAL_BAND = 0.5         # +-0.5pp limit-detection band (s3.1)
SEAL_FAMILY_FRAC = 0.92 # limitup chg_th 0.092 of true board threshold (s4)
LIQ_YUAN = 5e7          # roll-20d mean amount >= 5000万 (s2)
STALE_TD = 250          # last bar within 250 trading days (s2)
ST_WIN = 250            # ST-regime proxy rolling window (s2)
ST_SEAL5_MIN = 2        # >=2 sealed-5% days, 0 sealed-10% days (s2)
CE_PARAMS = {"time_decay_period": 25, "time_decay_threshold": 0.05,
             "trailing_stop_activate": 0.10}
CE_OVERRIDES = {"loss_time_days": 16}
N_NULL = 20             # per exit format (spec n>=20; probe fixes capacity)
NULL_SEED_BASE = 20260936  # spec s5 seed base
POS_PCT = 0.10
STOCK_COST_MULT = 2.0   # 2x ETF fee = 26.082bp roundtrip (G6-verified)
X2_COST_MULT = 4.0      # stock x2 stress = 52bp
MIN_TRADES = 30
DD_FLOOR = -0.35
PASSIVE_PAD = 0.10
OOS_START = "2025-01-01"

FAMILIES = {
    # name: (builder_key, top_k, hold_days, note)
    "limitup_mom":        ("limitup_mom", 5, 5, "zoo#1 seal+vol_ratio, hold5"),
    "limitup_mom_first_board": ("first_board", 5, 5, "zoo#1b first board in 20d, CE-only per spec"),
    "limitup_mom_mood":   ("limitup_mom", 5, 5, "zoo#1 + mood z>0 gate"),
    "dragon_head":        ("dragon_head", 3, 5, "zoo#2 count5>=2, streak-ranked tk3, break=exit"),
    "dragon_head_mood":   ("dragon_head", 3, 5, "zoo#2 + mood z>0 gate"),
    "ban_open":           ("ban_open", 5, 4, "zoo#3 yesterday failed seal + today +3%"),
    "limit_down_buy":     ("limit_down_buy", 5, 4, "zoo#4 near limit-down then no-crash confirm"),
    "sub_new":            ("sub_new", 5, None, "zoo#7 listing 20-250 bars, mom10 top5 frozen 5d"),
    "lhb_follow_tk5":     ("lhb_follow", 5, 5, "zoo#6 netbuy>0 & netbuy/mkt>=3%, lag1, tk5"),
    "lhb_follow_tk8":     ("lhb_follow", 8, 5, "zoo#6 same, tk8"),
}

_BARS_DIR = None


# ================= R38-a panel (delivered round 38, unchanged) =================

def _init_worker(bars_dir):
    global _BARS_DIR
    _BARS_DIR = bars_dir


def _load_one(args):
    sym, = args
    import pandas as pd
    try:
        df = pd.read_parquet(os.path.join(_BARS_DIR, sym + ".parquet"))
    except Exception:
        return (sym, None, None)
    d = df["date"].to_numpy().astype("datetime64[D]")
    m = (d >= WINDOW_START) & (d <= CUTOFF)
    if int(m.sum()) < MIN_BARS:
        return (sym, None, None)
    arr = df.loc[m, COLS].to_numpy(dtype=np.float32)
    return (sym, d[m], np.ascontiguousarray(arr))


def _jsonable(x):
    if isinstance(x, dict):
        return {k: _jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_jsonable(v) for v in x]
    if isinstance(x, np.bool_):
        return bool(x)
    if isinstance(x, (np.floating, np.integer)):
        return x.item()
    if isinstance(x, np.ndarray):
        return [_jsonable(v) for v in x.tolist()]
    return x


def build_panel():
    t0 = time.time()
    syms = sorted(f[:-8] for f in os.listdir(BARS_DIR) if f.endswith(".parquet"))
    kept, excluded_short = {}, 0
    with ProcessPoolExecutor(max_workers=WORKERS_PANEL, initializer=_init_worker,
                             initargs=(BARS_DIR,)) as ex:
        for sym, d, arr in ex.map(_load_one, [(s,) for s in syms], chunksize=32):
            if d is None:
                excluded_short += 1
            else:
                kept[sym] = (d, arr)
    codes = sorted(kept)
    dates = np.unique(np.concatenate([kept[c][0] for c in codes]))
    T, N = len(dates), len(codes)
    panel = np.full((T, N, 7), np.nan, dtype=np.float32)
    for j, c in enumerate(codes):
        d, arr = kept[c]
        panel[np.searchsorted(dates, d), j, :] = arr
    return dates, np.array(codes), panel, time.time() - t0, excluded_short, len(syms)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def validate(dates, codes, panel):
    global _BARS_DIR
    _BARS_DIR = BARS_DIR
    gates, detail = {}, {}
    gates["P1_window"] = bool(dates[0] >= WINDOW_START and dates[-1] == CUTOFF)
    pref = {p: int(sum(1 for c in codes if c.startswith(p)))
            for p in ("60", "00", "30", "68")}
    gates["P2_counts"] = bool(all(pref[p] > 0 for p in pref)
                              and sum(pref.values()) == len(codes)
                              and not any(c.startswith(("51", "15", "58"))
                                          for c in codes))
    nan_frac = {col: float(np.isnan(panel[:, :, k]).mean())
                for k, col in enumerate(COLS)}
    gates["P3_dtype_nan"] = bool(panel.dtype == np.float32
                                  and all(v < 0.9 for v in nan_frac.values()))
    code_idx = {c: j for j, c in enumerate(codes)}
    p4_ok, p4_detail = True, {}
    for s in SPOT_SYMS:
        if s not in code_idx:
            p4_detail[s] = "missing_from_panel"
            p4_ok = False
            continue
        _, sym_d, sym_arr = _load_one((s,))
        got = panel[np.isin(dates, sym_d), code_idx[s], :]
        ok = bool(np.array_equal(got, sym_arr, equal_nan=True))
        p4_detail[s] = ok
        p4_ok = p4_ok and ok
    gates["P4_spot_bitwise"] = p4_ok
    picks = codes[::DET_PICK_STRIDE][:50]
    p5_fail = 0
    for s in picks:
        _, sym_d, sym_arr = _load_one((s,))
        if sym_d is None:
            continue
        got = panel[np.isin(dates, sym_d), code_idx[s], :]
        if not np.array_equal(got, sym_arr, equal_nan=True):
            p5_fail += 1
    gates["P5_determinism_50"] = bool(p5_fail == 0)
    detail["nan_frac_by_col"] = nan_frac
    detail["p4_detail"] = p4_detail
    detail["det_picks"] = len(picks)
    detail["board_mix"] = pref
    return gates, detail


def cmd_panel():
    os.makedirs(CACHE_DIR, exist_ok=True)
    dates, codes, panel, elapsed, excluded_short, scanned = build_panel()
    gates, detail = validate(dates, codes, panel)
    p_path = os.path.join(CACHE_DIR, "panel_prices.npy")
    np.save(p_path, panel)
    np.save(os.path.join(CACHE_DIR, "panel_dates.npy"), dates)
    np.save(os.path.join(CACHE_DIR, "panel_symbols.npy"), codes)
    T, N = panel.shape[0], panel.shape[1]
    payload = {
        "stage": "R38-a panel build (data engineering only, zero engine runs)",
        "gate_context": ("batch runs deferred per O-1820/MSG-1845: bars lack "
                         "fundamentals -> R-pei1 unverifiable pool-wide -> "
                         "conservative literal execution = zero output; run "
                         "subcommand gated on research/shortline/"
                         "R38_RUN_CLEARANCE.md"),
        "window": {"start": "2015-01-01", "end": "2026-09-22", "days": int(T)},
        "symbols": {"included": int(N),
                    "excluded_under_20_bars": int(excluded_short),
                    "scanned_parquet": int(scanned),
                    "board_mix": pref_detail(detail)},
        "dtype": "float32", "layout": "(T,N,7)", "columns": COLS,
        "workers": WORKERS_PANEL, "build_seconds": round(elapsed, 2),
        "cache": {"dir": os.path.relpath(CACHE_DIR, ROOT),
                  "panel_prices_sha256": sha256_file(p_path),
                  "panel_bytes": int(os.path.getsize(p_path))},
        "nan_frac_by_col": detail["nan_frac_by_col"],
        "gates": gates, "all_pass": all(gates.values()),
        "trials_n_delta": 0, "engine_runs": 0,
        "meta_note": ("prices already forward-adjusted in bars parquet "
                      "(P-1c lesson: sidecar factors never applied); pct_chg "
                      "= official raw daily change, sole limit-detection "
                      "input per spec s3.1"),
    }
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(_jsonable(payload), f, ensure_ascii=False, indent=2)
    print(_jsonable({"T": T, "N": N, "workers": WORKERS_PANEL,
                     "build_seconds": payload["build_seconds"],
                     "gates": gates, "all_pass": payload["all_pass"]}))
    return 0 if payload["all_pass"] else 1


def pref_detail(detail):
    return detail["board_mix"]


# ================= R38-b shared state (per process, lazy) =================

_S = {}


def _roll_sum(x, w):
    """Rolling sum over axis 0 of a NaN-free float array (full windows)."""
    cs = np.cumsum(x, axis=0, dtype=np.float64)
    out = np.full(x.shape, np.nan, dtype=np.float64)
    if len(out) > w:
        out[w:] = cs[w:] - cs[:-w]
        out[w - 1] = cs[w - 1]
    return out


def _roll_mean(x, w):
    s = _roll_sum(x, w)
    with np.errstate(invalid="ignore"):
        s /= w
    return s


def _last_pos(mask):
    idx = np.arange(mask.shape[0])[:, None]
    return np.maximum.accumulate(np.where(mask, idx, -1), axis=0)


def _days_since(mask):
    last = _last_pos(mask)
    ds = np.arange(mask.shape[0])[:, None] - last
    ds[last < 0] = 1 << 20
    return ds


def _ensure_shared():
    """Build shared arrays once per process (memmap views -> shared pages)."""
    if _S:
        return
    t0 = time.time()
    panel = np.load(os.path.join(CACHE_DIR, "panel_prices.npy"), mmap_mode="r")
    dates = np.load(os.path.join(CACHE_DIR, "panel_dates.npy"))
    codes = np.load(os.path.join(CACHE_DIR, "panel_symbols.npy"))
    T, N = panel.shape[0], panel.shape[1]
    op = panel[:, :, 0]; hi = panel[:, :, 1]; lo = panel[:, :, 2]
    cl = panel[:, :, 3]; vol = panel[:, :, 4]; amt = panel[:, :, 5]
    pct = panel[:, :, 6]

    # board-truth threshold matrix (fraction; pct stays in percent units)
    is_main = np.zeros((T, N), dtype=bool)
    is_cx = np.zeros((T, N), dtype=bool)
    is_star = np.zeros((T, N), dtype=bool)
    for j, c in enumerate(codes):
        if c.startswith(("60", "00")):
            is_main[:, j] = True
        elif c.startswith("30"):
            is_cx[:, j] = True
        elif c.startswith("68"):
            is_star[:, j] = True
    cx20 = (dates >= CHINEXT_20_FROM)[:, None]
    thr = np.full((T, N), np.nan, dtype=np.float32)
    thr[is_main] = 0.10
    thr[is_star] = 0.20
    thr[is_cx & ~cx20] = 0.10
    thr[is_cx & cx20] = 0.20

    finite_cl = np.isfinite(cl)
    # true seal (limit-UP within +-0.5pp band, close==high)
    sealed_true = finite_cl & (cl == hi) & (pct >= thr * 100 - SEAL_BAND)
    # family seal (chg_th = 0.92 x true threshold, s4)
    sealed_family = finite_cl & (cl == hi) & (pct >= SEAL_FAMILY_FRAC * thr * 100)

    # dynamic eligibility
    mask = pd.read_csv(MASK_CSV)
    code_str = mask["code"].astype(int).map(lambda v: f"{v:06d}")
    static_ok = np.isin(codes, code_str[mask["ok_static"] == True].values)

    amt0 = np.where(finite_cl, amt, 0.0)
    liq20 = _roll_mean(amt0, 20) >= LIQ_YUAN
    liq20[~finite_cl] = False
    price_ok = finite_cl & (cl >= 1.0)
    bars_so_far = np.cumsum(finite_cl, axis=0) >= MIN_BARS
    last_valid = _last_pos(finite_cl)
    stale = ((np.arange(T)[:, None] - last_valid) > STALE_TD) | (last_valid < 0)

    # ST-regime proxy, board-aware (10%-board segments only)
    s5 = (finite_cl & (cl == hi) & (pct >= 4.6) & (pct <= 5.4)).astype(np.float64)
    s10 = (finite_cl & (cl == hi) & (pct >= 9.4) & (pct <= 10.6)).astype(np.float64)
    r5 = _roll_sum(s5, ST_WIN); r10 = _roll_sum(s10, ST_WIN)
    with np.errstate(invalid="ignore"):
        st_seg = (r5 >= ST_SEAL5_MIN) & (r10 == 0) & (thr == 0.10)
    st_seg = np.where(np.isnan(r5), False, st_seg)

    elig = (static_ok[None, :] & liq20 & price_ok & bars_so_far & ~stale
            & ~st_seg)

    # fill guards (s3.1): buy blocked on sealed limit-up OPEN; sell blocked
    # on sealed limit-DOWN close. NaN rows stay unrestricted (False==False).
    buy_ok = ~((op == hi) & np.isfinite(op) & (pct >= thr * 100 - SEAL_BAND))
    sell_ok = ~((cl == lo) & finite_cl & (pct <= -(thr * 100 - SEAL_BAND)))

    # mood: market-wide limit-up seal count, 60d z-score (pandas rolling =
    # NaN-safe; numpy _roll_sum is NaN-free-only, dev array has NaN head)
    seal_count = np.array([np.count_nonzero(sealed_true[t]) for t in range(T)],
                          dtype=np.float64)
    sc_s = pd.Series(seal_count)
    mc_s = sc_s.rolling(60, min_periods=60).mean()
    ms_s = sc_s.rolling(60, min_periods=60).std()
    with np.errstate(invalid="ignore", divide="ignore"):
        mood_z = ((sc_s - mc_s) / ms_s).to_numpy()

    # LHB events (P-A dedup convention: per (code, day) keep max lhb amount)
    lhb = pd.read_parquet(LHB_PATH)
    lhb = lhb.sort_values(["龙虎榜成交额", "序号"], ascending=[True, False])
    ev = lhb.drop_duplicates(subset=["代码", "上榜日"], keep="last")
    ev_day = pd.to_datetime(ev["上榜日"]).values.astype("datetime64[D]")
    pos = np.searchsorted(dates, ev_day)
    sym_col = {s: i for i, s in enumerate(codes)}
    cols = ev["代码"].astype(str).str.zfill(6).map(sym_col)
    keep = (pos < T) & cols.notna().values
    # signal at the NEXT trading day after disclosure (lag 1, P-A/P-B)
    sig_pos = pos[keep] + 1
    sig_ok = sig_pos < T
    lhb_net = pd.to_numeric(ev["龙虎榜净买额"], errors="coerce").values[keep]
    lhb_mkt = pd.to_numeric(ev["市场总成交额"], errors="coerce").values[keep]
    lhb_r, lhb_c = sig_pos[sig_ok], cols.values[keep][sig_ok].astype(int)
    lhb_nb, lhb_mk = lhb_net[sig_ok], lhb_mkt[sig_ok]
    with np.errstate(invalid="ignore", divide="ignore"):
        lhb_ok = (lhb_nb > 0) & (lhb_mk > 0) & (lhb_nb / lhb_mk >= 0.03)
    lhb_sig = np.zeros((T, N), dtype=bool)
    lhb_sig[lhb_r[lhb_ok], lhb_c[lhb_ok]] = True

    dt = pd.DatetimeIndex(dates.astype("datetime64[ns]"))
    _S.update(dict(panel=panel, dates=dates, codes=codes, T=T, N=N,
                   open=op, high=hi, low=lo, close=cl, vol=vol, amt=amt,
                   pct=pct, thr=thr, sealed_true=sealed_true,
                   sealed_family=sealed_family, elig=elig,
                   buy_ok=buy_ok, sell_ok=sell_ok, mood_z=mood_z,
                   lhb_sig=lhb_sig, dt=dt, static_ok=static_ok,
                   build_s=round(time.time() - t0, 1)))
    _S["_prices_full"] = None


def _prices_dict(syms_idx):
    """dict[sym] -> DataFrame(open, close) for the given column indices."""
    if _S["_prices_full"] is None:
        cl = np.asarray(_S["close"], dtype=np.float32)
        op = np.asarray(_S["open"], dtype=np.float32)
        dt = _S["dt"]
        d = {}
        for j, c in enumerate(_S["codes"]):
            d[str(c)] = pd.DataFrame({"open": op[:, j], "close": cl[:, j]},
                                     index=dt)
        _S["_prices_full"] = d
    syms = [str(_S["codes"][j]) for j in syms_idx]
    return {s: _S["_prices_full"][s] for s in syms}


# ---------------- family builders (pure, deterministic) ----------------

def _build_family(key, top_k, hold):
    """Return (entry bool(T,N), exit bool(T,N), note)."""
    S = _S
    T, N = S["T"], S["N"]
    cl, pct, vol = S["close"], S["pct"], S["vol"]
    thr, elig = S["thr"], S["elig"]
    sealed = S["sealed_family"]
    zgate = None

    if key in ("limitup_mom", "first_board"):
        vol0 = np.where(np.isfinite(vol), vol, 0.0)
        v5 = _roll_mean(vol0, 5)
        with np.errstate(invalid="ignore"):
            vr = vol / v5
        trig = sealed & (vr >= 1.2) & np.isfinite(vr)
        if key == "first_board":
            c20 = _roll_sum(sealed.astype(np.float64), 20)
            prior = np.zeros((T, N), dtype=bool)
            prior[1:] = (c20[:-1] == 0)
            trig = trig & prior
        note = ("seal close==high & pct>=0.92*thr & vol>=1.2*roll5(vol)"
                + ("; first board: no seal in prior 20d" if key == "first_board" else ""))
    elif key == "dragon_head":
        c5 = _roll_sum(sealed.astype(np.float64), 5)
        idx = np.arange(T)[:, None]
        last_non = _last_pos(~sealed)
        streak = idx - last_non
        streak[~sealed] = 0
        trig = sealed & (c5 >= 2)
        # per-day top-k by streak height (ties -> lower code first)
        cand = trig & elig
        entry = np.zeros((T, N), dtype=bool)
        st_f = np.where(cand, streak, -np.inf).astype(np.float32)
        k = min(top_k, N)
        for t in range(T):
            row = st_f[t]
            if not np.isfinite(row).any():
                continue
            order = np.argsort(-row, kind="stable")[:k]
            order = order[np.isfinite(row[order])]
            entry[t, order] = True
        run_age = np.where(sealed, idx - (idx - streak), -1)
        ds = _days_since(sealed)
        ever = np.maximum.accumulate(entry, axis=0)
        exit_ = ((ds >= 2) | (run_age > 5)) & ever
        return entry, exit_, ("count5>=2 seal streak, tk=top3 by streak; "
                              "exit: streak break (ds>=2) or run age>5")
    elif key == "ban_open":
        with np.errstate(invalid="ignore", divide="ignore"):
            preclose = cl / (1.0 + pct / 100.0)
            hi_ret = S["high"] / preclose - 1.0
            drop = (S["high"] - cl) / S["high"]
        attempt = np.isfinite(hi_ret) & (hi_ret >= thr) & (drop >= 0.02)
        trig = np.zeros((T, N), dtype=bool)
        trig[1:] = attempt[:-1] & (pct[1:] >= 3.0)
        note = ("yesterday high_ret>=thr & high->close drop>=2%; "
                "today pct>=+3% confirm")
    elif key == "limit_down_buy":
        near_dn = np.isfinite(pct) & (pct <= -(thr * 100 - SEAL_BAND))
        trig = np.zeros((T, N), dtype=bool)
        trig[1:] = near_dn[:-1] & (pct[1:] > -2.0)
        note = ("yesterday pct<=-(thr-0.5pp); today pct>-2 no-crash confirm")
    elif key == "sub_new":
        finite_cl = np.isfinite(cl)
        age = np.cumsum(finite_cl, axis=0)
        sub_ok = (age >= 20) & (age <= 250) & elig
        mom = np.full((T, N), np.nan, dtype=np.float32)
        with np.errstate(invalid="ignore", divide="ignore"):
            mom[10:] = cl[10:] / cl[:-10] - 1.0
        sel = np.zeros((T, N), dtype=bool)
        st_f = np.where(sub_ok & np.isfinite(mom), mom, -np.inf).astype(np.float32)
        k = top_k
        for t in range(0, T, 5):
            row = st_f[t]
            if not np.isfinite(row).any():
                continue
            order = np.argsort(-row, kind="stable")[:k]
            order = order[np.isfinite(row[order])]
            sel[t, order] = True
        r_idx = (np.arange(T) // 5) * 5
        held = sel[r_idx]
        ever = np.maximum.accumulate(held, axis=0)
        # frozen membership: eligibility is an entry-day gate (spec s2
        # "进入日计算，退出后不再依赖") -> no re-AND on held members
        entry = held.astype(bool)
        exit_ = ~held & ever
        return entry, exit_, \
            ("listing age 20-250 bars, mom10 top5 frozen 5d membership")
    elif key == "lhb_follow":
        trig = S["lhb_sig"].copy()
        note = ("LHB dedup'd event, netbuy>0 & netbuy/mkt>=3%, signal at "
                "E+1 (disclosure lag 1 trading day)")
    else:
        raise KeyError(key)

    entry = trig & elig
    ds = _days_since(trig)
    ever = np.maximum.accumulate(trig, axis=0)
    exit_ = (ds > hold) & ever
    return entry, exit_, note


def _mood_gate():
    return _S["mood_z"] > 0


# ---------------- engine execution ----------------

def _exec_run(entry, exit_, syms_idx, params, ce, cost_mult, tag):
    from engine import run_backtest
    from live.paper import CostPatch, ExitPatch, seg_metrics
    S = _S
    codes = S["codes"]
    syms = [str(codes[j]) for j in syms_idx]
    dt = S["dt"]
    sel = np.array(syms_idx)
    e_df = pd.DataFrame(entry[:, sel], index=dt, columns=syms)
    x_df = pd.DataFrame(exit_[:, sel], index=dt, columns=syms)
    guard = {"buy": pd.DataFrame(S["buy_ok"][:, sel], index=dt, columns=syms),
             "sell": pd.DataFrame(S["sell_ok"][:, sel], index=dt, columns=syms)}
    pp = dict(params)
    if ce:
        pp.update(CE_PARAMS)
    prices = _prices_dict(sel)
    t0 = time.time()
    from contextlib import nullcontext
    with CostPatch(cost_mult):
        with ExitPatch(CE_OVERRIDES) if ce else nullcontext():
            res = run_backtest(prices, pp, entry_signal=e_df,
                               exit_signal=x_df, fill_guard=guard)
    elapsed = time.time() - t0
    eq = pd.Series(res["equity_curve"], index=dt[:len(res["equity_curve"])])
    oos_tr = sum(1 for tr in res["trades"] if tr["date"] >= OOS_START)
    ea = res["equity_curve"]
    diag = {"eq_q1": round(ea[len(ea) // 4], 0), "eq_mid": round(ea[len(ea) // 2], 0),
            "eq_tail": round(ea[-1], 0),
            "first_trade": res["trades"][0]["date"] if res["trades"] else None,
            "last_trade": res["trades"][-1]["date"] if res["trades"] else None}
    return {"tag": tag, "full": res["metrics"], "oos": seg_metrics(eq, OOS_START),
            "n_trades": res["metrics"]["num_trades"], "oos_trades": oos_tr,
            "run_seconds": round(elapsed, 1), **diag}


def _fired_syms(entry):
    return np.flatnonzero(entry.any(axis=0))


def _family_task(args):
    fam, variants = args
    _ensure_shared()
    S = _S
    bkey, top_k, hold, _note = FAMILIES[fam]
    entry, exit_, note = _build_family(bkey, top_k, hold)
    if fam.endswith("_mood"):
        entry = entry & _mood_gate()[:, None]   # gates OPENING only (spec s1)
    fired = _fired_syms(entry)
    params = {"max_positions": top_k, "position_size_pct": POS_PCT}
    out = []
    for run_name, ce, cost_mult in variants:
        out.append({"key": f"{fam}@{'ce' if ce else 'default'}@x{int(cost_mult)}",
                    "kind": "family", "family": fam, "note": note,
                    "exit_regime": "ce" if ce else "default",
                    "cost_mult": cost_mult, "n_syms": int(len(fired)),
                    "n_entry_days": int(entry.any(axis=1).sum()),
                    **_exec_run(entry, exit_, fired, params, ce, cost_mult,
                                run_name)})
    return out


def _null_task(args):
    seed, ce = args
    _ensure_shared()
    S = _S
    T = S["T"]
    elig = S["elig"]
    rng = np.random.default_rng(seed)
    entry = np.zeros((T, S["N"]), dtype=bool)
    # per-day uniform pick of k=5 among eligible (spec s5 literal k-pick)
    for t in range(T):
        idx = np.flatnonzero(elig[t])
        if len(idx) == 0:
            continue
        k = min(5, len(idx))
        entry[t, rng.choice(idx, size=k, replace=False)] = True
    exit_ = np.zeros_like(entry)
    fired = _fired_syms(entry)
    params = {"max_positions": 5, "position_size_pct": POS_PCT}
    return [{"key": f"null_{'ce' if ce else 'default'}_s{seed}",
             "kind": "random_null", "seed": seed,
             "exit_regime": "ce" if ce else "default",
             "cost_mult": STOCK_COST_MULT, "n_syms": int(len(fired)),
             **_exec_run(entry, exit_, fired, params, ce, STOCK_COST_MULT,
                         "null")}]


# ---------------- probe / run / status ----------------

def _all_keys():
    keys = []
    for fam, (bkey, top_k, hold, _n) in FAMILIES.items():
        if fam == "limitup_mom_first_board":
            # spec: first-board variant is CE-only
            keys.append(f"{fam}@ce@x{int(STOCK_COST_MULT)}")
        else:
            keys.append(f"{fam}@default@x{int(STOCK_COST_MULT)}")
            keys.append(f"{fam}@ce@x{int(STOCK_COST_MULT)}")
        if fam != "limitup_mom_first_board":
            keys.append(f"{fam}@default@x{int(X2_COST_MULT)}")
    for k in range(N_NULL):
        seed = NULL_SEED_BASE + k
        keys.append(f"null_default_s{seed}")
        keys.append(f"null_ce_s{seed}")
    return keys


def cmd_probe():
    t0 = time.time()
    _ensure_shared()
    S = _S
    print(f"shared build: {S['build_s']}s | T={S['T']} N={S['N']}")
    cl, pct, amt = S["close"], S["pct"], S["amt"]
    i = np.argmax(np.isfinite(cl[:, 0]))
    print(f"unit check 000001 row {i}: close={cl[i,0]} pct={pct[i,0]} "
          f"amt={amt[i,0]} (pct in percent, amt in yuan expected)")
    print(f"elig days x syms nonzero: {int(S['elig'].sum())} | "
          f"syms ever eligible: {int(S['elig'].any(axis=0).sum())} | "
          f"static ok: {int(S['static_ok'].sum())}")
    print(f"mood z finite: {np.isfinite(S['mood_z']).sum()}/{S['T']} | "
          f"lhb sig days: {int(S['lhb_sig'].any(axis=1).sum())}")
    t1 = time.time()
    entry, exit_, note = _build_family("limitup_mom", 5, 5)
    fired = _fired_syms(entry)
    print(f"limitup_mom build: {time.time()-t1:.1f}s | fired syms={len(fired)} "
          f"| entry days={int(entry.any(axis=1).sum())} | note: {note}")
    t2 = time.time()
    r = _exec_run(entry, exit_, fired,
                  {"max_positions": 5, "position_size_pct": POS_PCT},
                  False, STOCK_COST_MULT, "probe")
    print(f"diag: eq_q1={r['eq_q1']:.0f} eq_mid={r['eq_mid']:.0f} "
          f"eq_tail={r['eq_tail']:.0f} | trades {r['first_trade']}.."
          f"{r['last_trade']} | oos_trades={r['oos_trades']}")
    print(f"PROBE limitup_mom@default: full_s={r['full']['sharpe']} "
          f"oos_s={r['oos']['sharpe']} trades={r['n_trades']} "
          f"run={r['run_seconds']}s")
    print(f"probe total: {time.time()-t0:.1f}s | "
          f"est. cells(30)={30*r['run_seconds']:.0f}s "
          f"nulls(40)~est 40*{max(r['run_seconds']*0.4, 5):.0f}s "
          f"-> divide by workers for wall time")
    return 0


def _load_done():
    done = {}
    if os.path.exists(RUNS_JSONL):
        with open(RUNS_JSONL, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                    done[rec["key"]] = rec
                except Exception:
                    continue
    return done


def _lock_alive():
    if not os.path.exists(LOCK):
        return False
    try:
        with open(LOCK) as fh:
            pid = int(fh.read().strip())
        ps = os.popen(f"tasklist /FI \"PID eq {pid}\"").read()
        return str(pid) in ps
    except Exception:
        return False


def cmd_run():
    if not os.path.exists(CLEARANCE):
        print("EXIT 2: batch runs deferred per O-1820 (MSG-1845) -- "
              "create research/shortline/R38_RUN_CLEARANCE.md to unlock.")
        return 2
    if _lock_alive():
        print("LOCK ALIVE: another run process holds results/p4_batch2_run.lock "
              "-- this invocation exits without touching state (poll with "
              "`status`).")
        return 0
    if not self_test_gate():
        return 2
    t0 = time.time()
    with open(LOCK, "w") as fh:
        fh.write(str(os.getpid()))
    try:
        _ensure_shared()
        done = _load_done()
        keys = _all_keys()
        todo = [k for k in keys if k not in done]
        print(f"resume: {len(done)} done, {len(todo)} todo of {len(keys)} runs",
              flush=True)

        tasks = []
        for fam, (bkey, top_k, hold, _n) in FAMILIES.items():
            variants = []
            if fam == "limitup_mom_first_board":
                variants.append((fam, True, STOCK_COST_MULT))
            else:
                variants.append((fam, False, STOCK_COST_MULT))
                variants.append((fam, True, STOCK_COST_MULT))
                variants.append((fam, False, X2_COST_MULT))
            need = [f"{fam}@{'ce' if ce else 'default'}@x{int(cm)}"
                    for _, ce, cm in variants]
            if any(k in todo for k in need):
                tasks.append(("family", (fam, variants)))
        for k in range(N_NULL):
            seed = NULL_SEED_BASE + k
            if f"null_default_s{seed}" in todo:
                tasks.append(("null", (seed, False)))
            if f"null_ce_s{seed}" in todo:
                tasks.append(("null", (seed, True)))

        n_workers = min(6, max(1, len(tasks)))
        if tasks:
            with ProcessPoolExecutor(max_workers=n_workers) as ex:
                futs = []
                for kind, arg in tasks:
                    fn = _family_task if kind == "family" else _null_task
                    futs.append(ex.submit(fn, arg))
                for fut in futs:
                    for rec in fut.result():
                        with open(RUNS_JSONL, "a", encoding="utf-8") as fh:
                            fh.write(json.dumps(_jsonable(rec),
                                                ensure_ascii=False) + "\n")
                        done[rec["key"]] = rec
                        print(f"  done {rec['key']} "
                              f"full_s={rec['full']['sharpe']} "
                              f"trades={rec['n_trades']} "
                              f"({rec['run_seconds']}s)", flush=True)

        if any(k not in done for k in keys):
            print("INCOMPLETE: some runs missing (killed mid-flight?) -- "
                  "re-invoke `run` to resume.", flush=True)
            return 3
        ok = _finalize(done, t0)
        return 0 if ok else 1
    finally:
        if os.path.exists(LOCK):
            os.remove(LOCK)


def self_test_gate():
    from live.paper import self_test_patches, COST_X1_RATE, COST_X2_RATE
    ok = self_test_patches()
    print(f"patch self-test: {'PASS' if ok else 'FAIL'} "
          f"(x1={COST_X1_RATE} stock_base=x2={COST_X2_RATE})")
    return ok


def _passive_rows():
    """Passive nulls over the eligible universe (spec s5: monthly EW is the
    named passive; buyhold recorded as info). Sleeve enters at first
    eligible day (pre-mask closes to NaN before it)."""
    from p2_null_calibration import passive_buyhold, passive_monthly_rebal
    from live.paper import COST_X2_RATE
    S = _S
    elig = S["elig"]
    ever = elig.any(axis=0)
    sel = np.flatnonzero(ever)
    first_ok = np.argmax(elig[:, sel], axis=0)
    any_ok = elig[:, sel].any(axis=0)
    cl = np.asarray(S["close"][:, sel], dtype=np.float64)
    rows = np.arange(S["T"])[:, None]
    cl_m = cl.copy()
    cl_m[rows < first_ok[None, :]] = np.nan
    cl_m[:, ~any_ok] = np.nan
    closes = pd.DataFrame(cl_m, index=S["dt"],
                          columns=[str(c) for c in S["codes"][sel]])
    out = {}
    for name, fn in (("stock_ew_buyhold", passive_buyhold),
                     ("stock_ew_monthly", passive_monthly_rebal)):
        eq = fn(closes, COST_X2_RATE)
        from live.paper import seg_metrics
        out[name] = {"full": seg_metrics(eq), "oos": seg_metrics(eq, OOS_START)}
    out["_universe"] = {"n_sleeves": int(len(sel)),
                        "n_panel": int(S["N"])}
    return out


def _finalize(done, t0):
    import csv as _csv
    from live.paper import seg_metrics
    keys = _all_keys()
    cells = [done[k] for k in keys if "@x" in k and not k.startswith("null")]
    nulls = [done[k] for k in keys if k.startswith("null")]
    if len(cells) + len(nulls) != len(keys):
        print("finalize refused: run set incomplete")
        return False

    p95 = {}
    for fmt in ("default", "ce"):
        vals = [r["full"]["sharpe"] for r in nulls
                if r["exit_regime"] == fmt]
        p95[fmt] = round(float(np.percentile(vals, 95)), 4)
    passive = _passive_rows()
    passive_monthly_s = passive["stock_ew_monthly"]["full"]["sharpe"]
    vi = {fmt: round(max(p95[fmt], passive_monthly_s + PASSIVE_PAD), 4)
          for fmt in ("default", "ce")}

    rows_out, survivors = [], []
    x2_map = {}
    for c in cells:
        if c["cost_mult"] == X2_COST_MULT:
            x2_map[(c["family"], "default")] = c
    for c in cells:
        if c["cost_mult"] == X2_COST_MULT:
            continue
        fmt = c["exit_regime"]
        full, oos = c["full"], c["oos"]
        clauses = {
            "i_sharpe_gt_vi": full["sharpe"] > vi[fmt],
            "ii_ann_pos": full["annual_return"] > 0,
            "iii_dd_ok": full["max_drawdown"] >= DD_FLOOR,
            "iv_trades_ok": c["n_trades"] >= MIN_TRADES,
            "v_oos_double_pos": oos["sharpe"] > 0 and oos["annual_return"] > 0,
        }
        g1 = all(clauses.values())
        if g1:
            survivors.append(f"{c['family']}@{fmt}")
        x2 = x2_map.get((c["family"], "default"))
        rows_out.append({
            "name": f"{c['family']}@{fmt}", "family": c["family"],
            "exit_regime": fmt, "status": "ok",
            "n_trades": c["n_trades"], "oos_trades": c["oos_trades"],
            "annual_return": full["annual_return"], "sharpe": full["sharpe"],
            "max_drawdown": full["max_drawdown"],
            "win_rate": full.get("win_rate", ""),
            "oos_sharpe": oos["sharpe"],
            "oos_annual_return": oos["annual_return"],
            "oos_max_drawdown": oos["max_drawdown"],
            "vi_bar": vi[fmt], "i_p95_format": p95[fmt],
            "g1_pass": g1, "clauses": clauses,
            "n_syms": c["n_syms"], "n_entry_days": c["n_entry_days"],
            "x2_full_sharpe": x2["full"]["sharpe"] if x2 else "",
            "x2_oos_sharpe": x2["oos"]["sharpe"] if x2 else "",
            "note": c["note"],
        })

    with open(LOG_LEDGER, encoding="utf-8") as fh:
        prev = json.load(fh)["trials_ledger"]
    prev_total = int(prev["total"]) if isinstance(prev, dict) else 0
    n_gate_cells = sum(1 for c in cells if c["cost_mult"] == STOCK_COST_MULT)
    n_x2_info = sum(1 for c in cells if c["cost_mult"] == X2_COST_MULT)
    n_runs = len(cells) + len(nulls) + 2   # +2 passive accounting-only
    ledger = {"prev_total": prev_total, "batch_trials": n_runs,
              "note": (f"{n_gate_cells} gate cells (10 points; first_board "
                       f"CE-only per spec s4) + {n_x2_info} x2-cost info + "
                       f"{len(nulls)} random nulls (20 seeds x 2 regimes, "
                       "paired) + 2 passive; pre-registered P4_BATCH2.md "
                       "s4/s5"),
              "total": prev_total + n_runs}

    cols = ["name", "family", "exit_regime", "status", "n_trades",
            "oos_trades", "annual_return", "sharpe", "max_drawdown",
            "win_rate", "oos_sharpe", "oos_annual_return",
            "oos_max_drawdown", "vi_bar", "i_p95_format", "g1_pass",
            "n_syms", "n_entry_days", "x2_full_sharpe", "x2_oos_sharpe",
            "note"]
    with open(FINAL_CSV, "w", encoding="utf-8", newline="") as fh:
        w = _csv.writer(fh)
        w.writerow(cols)
        for r in rows_out:
            w.writerow([r[c] for c in cols])
        for r in nulls:
            w.writerow([r["key"], "random_null", r["exit_regime"], "ok",
                        r["n_trades"], r["oos_trades"],
                        r["full"]["annual_return"], r["full"]["sharpe"],
                        r["full"]["max_drawdown"], "", r["oos"]["sharpe"],
                        r["oos"]["annual_return"], r["oos"]["max_drawdown"],
                        "", "", "", r["n_syms"], "", "", "",
                        f"seed={r['seed']}"])
        for name, d in passive.items():
            if name.startswith("_"):
                continue
            w.writerow([name, "passive_null", "none", "ok", 0, 0,
                        d["full"]["annual_return"], d["full"]["sharpe"],
                        d["full"]["max_drawdown"], "", d["oos"]["sharpe"],
                        d["oos"]["annual_return"], d["oos"]["max_drawdown"],
                        "", "", "", "", "", "", "",
                        "elig-universe EW, sleeve enters first-eligible day"])

    out = {
        "batch": "shortline-p4-batch2-stock-B-layer",
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "preregistered_doc": "research/shortline/P4_BATCH2.md",
        "clearance": "research/shortline/R38_RUN_CLEARANCE.md (round 42)",
        "universe": {"panel": "Money02/data/cache/p4_batch2_panel",
                     "T": int(_S["T"]), "N": int(_S["N"]),
                     "static_ok": int(_S["static_ok"].sum()),
                     "syms_ever_eligible": int(_S["elig"].any(axis=0).sum()),
                     "elig_cell_days": int(_S["elig"].sum()),
                     "evidence_cutoff": "2026-09-22", "oos_start": OOS_START},
        "gate": {
            "clauses": "G1' five (spec s5): full_s>vi_format; ann>0; "
                       "dd>=-0.35; trades>=30; OOS double positive",
            "vi_rule": "max(in-batch random p95 of that exit format, "
                       "passive monthly-EW full sharpe + 0.10)",
            "random_p95": p95,
            "passive_monthly_full_sharpe": passive_monthly_s,
            "vi_used": vi,
            "core48_lines_NOT_reused": ["0.4004", "0.3521", "0.4229"],
        },
        "passive": passive,
        "cells": rows_out,
        "nulls": [{k: v for k, v in r.items() if k != "eq"} for r in nulls],
        "survivors_g1_prime": survivors,
        "survivors_are": "G1' CANDIDATES ONLY -- no registration this batch; "
                         "G2 deepening requires its own pre-registration",
        "engineering_notes": {
            "688_volume": "volume consumed only in per-stock ratios "
                          "(scale-invariant); no turnover/osh use",
            "st_proxy": "board-aware 5%-seal proxy (10%-board segments only); "
                        "20%-board segments exempt (see module docstring)",
            "stale_ffill": "delisted/suspended marks ride ffilled close; "
                           "equal treatment across cells and nulls",
            "dragon_exit": "state exit approximation: streak-break (ds>=2) "
                           "or seal-run age>5; re-seal while holding extends "
                           "limitup hold (state semantics, honest)",
            "cost": "stock base = CostPatch(2) = 0.0026082 roundtrip on every "
                    "run; x2 stress = CostPatch(4)",
        },
        "trials_ledger": ledger,
        "audit": {"elapsed_sec": round(time.time() - t0, 1),
                  "engine_runs": len(cells) + len(nulls),
                  "passive_accounting": 2,
                  "workers": "process pool (<=6)"},
    }
    with open(FINAL_JSON, "w", encoding="utf-8") as fh:
        json.dump(_jsonable(out), fh, ensure_ascii=False, indent=2)
    print(f"FINAL: survivors={survivors}")
    print(f"vi: default={vi['default']} ce={vi['ce']} | p95={p95} | "
          f"passive_monthly_s={passive_monthly_s}")
    print(f"saved {FINAL_JSON} + {FINAL_CSV}")
    print(f"ledger N={ledger['total']} (+{n_runs})")
    return True


def cmd_status():
    done = _load_done()
    keys = _all_keys()
    print(f"progress: {len(done)}/{len(keys)} runs on disk "
          f"({'FINAL JSON EXISTS' if os.path.exists(FINAL_JSON) else 'final pending'})")
    todo = [k for k in keys if k not in done]
    if todo:
        print(f"todo ({len(todo)}): {todo[:8]}{' ...' if len(todo) > 8 else ''}")
    print(f"lock alive: {_lock_alive()}")
    return 0


def main(argv):
    if len(argv) != 2 or argv[1] not in ("panel", "run", "probe", "status"):
        print(__doc__)
        return 1
    return {"panel": cmd_panel, "run": cmd_run, "probe": cmd_probe,
            "status": cmd_status}[argv[1]]()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
