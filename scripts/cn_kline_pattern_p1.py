"""CN_KLINE_PATTERN_P1 runner -- A股 K 线形态面 judged 判决批 (T-87 s2 queue #3).

Laws frozen in research/CN_KLINE_PATTERN_PREREG.md @commit cbf6c93c (R99: freeze
precedes runner build precedes ANY run; seed SEED_REGISTRY['cn_kline_pattern_p1']
= 20275100 registered at the freeze commit, band 20275100..20277100 clean):

  panel   Money02/data/bars/*.parquet direct read (D2-truncate every file to
          evidence cutoff 2026-09-22), file census == 5222; universe = b_layer
          ok_static & rows>=500 & last==cutoff & med(amount[-20:])>=3e7 CNY ->
          3106 members, re-derived mechanically and gated vs the frozen probe
          results/cn_kline_probe.json (universe n, skip ledger, boards, and
          the four pattern censuses -- probe = the sole encoding authority).
          Survivorship faces disclosed: in-market snapshot panel, current-time
          ok_static/liquidity masks (WILD-S1 same source same face).
  events  MS / TWS / DCC / TBC encodings are the probe code verbatim
          (results/cn_kline_probe_run.py); census gate refuses (exit 2) on
          any count drift vs the frozen probe (MS 1342 / TWS 21518 /
          DCC 35270 / TBC 14; TBC = dead-face honest, advisory member of the
          bear union, insufficient-sample flag in the product).
  exec    signal close d -> entry open d+1; suspension at entry rolls to the
          first tradable open (open & volume finite); near-limit-up open
          (open/prev_finite_close-1 >= floor-0.002) = unfillable, counted not
          discarded; exits T+1-open style: FIX/STOP H=10td, BEAR/COMBO
          H=20td cap; stop arms: MS stop = doji-day low l[e], TWS stop =
          first-soldier low l[d-2], trigger close<stop -> next open; bear
          arms: held name DCC|TBC -> next open out (long-only, zero short);
          exit-day suspension rolls forward (WILD face); panel-end tail =
          mark-to-last-finite-close (honest).
  floors  main 0.0975 / chinext 0.1975 from 2020-08-24 / star 0.1975 from
          2019-07-22 / other(BSE) 0.2975 (EF: 30cm band has no in-repo engine
          precedent, disclosed; 2 members); LIMIT_OPEN_TOL = 0.002 (WILD-S1).
  costs   V2 single source: alloc_backtest.side_cost_v2(gross, adv20) with the
          per-member leg notional N0=1e5 CNY (EF -- commission floor inactive
          at 100k, proportional face), x2 judged face via side_cost_x2 (every
          V2 component doubled), x1 = disclosure column; ADV20 = NaN-aware
          rolling-20 amount mean (min 10) per leg day; NaN adv -> krules 10bp
          fallback (a data gap can never cheapen costs); net = exit/entry *
          (1-c_out)/(1+c_in) - 1, both legs on their own notionals.
  bucket  WILD-S1 frozen reuse: cohort of day t equal-weight internal over
          FILLED members, per-trade net booked evenly across its holding
          calendar days entry_cal+1 .. exit_cal (span = exit_cal-entry_cal);
          stop/bear arms book at actual exit (per-trade spans, prereg s3).
  nulls   RANDOM_LARGE_SAMPLE_LAW s3: per cell K=2000 draws, each draw =
          N_cell uniform (name,day) pairs from universe x valid-days mask
          (own-index t in [1, n-2], EF disclosed), same H / execution /
          cost(x2) / bucket accounting -> null cell Sharpe; own-null pool per
          cell (rng seed SEED+k, k<2000); null face = time-exit H (FIX/STOP
          10, BEAR/COMBO 20) -- pattern-extremum stops are undefined on
          random events (EF disclosed); 8 shards x 250 draws, npy
          checkpoints, idempotent resume. Block bootstrap 2000 (block=10) +
          sign-flip 2000 per cell, p values double-reported.
  starts  census virtual starts t0 in [200, T-126), 126d window vs the
          universe-EW passive proxy; 4 segment classes (bull/bear/deep-bear/
          chop by sse level / MA200 / 60d return, REV_OSC s2.1 frozen face);
          segment n<500 = insufficient-sample honest note; >=100 random
          train/val splits + walk-forward 5 folds (law s2.3).
  gates   G1'v2 per cell (batch_cells=2007, pool='stock_b_layer',
          null_pool=own, F6 dual trade gate) + DSR (deflated_sharpe_ratio on
          the raw x2 series) + family PBO (screening/pbo cscv_pbo CSCV-8 over
          the 7-cell x2 matrix) + g2_registration_v2. NO hand-copied lines
          (O-2250). Judged face = x2 (prereg s3); batch disclosure: ann>0
          AND OOS (>=2025-01-01) ann>0 AND maxDD >= -35%.
  ledger  science_gates.append_ledger single-count (prev_total redo guard,
          REV_OSC r259 face); gate_attrition measurement row (entries list
          face per r248 law, own row replaced in place on redo).

Products (prereg s6): results/cn_kline_pattern/p1_results.json (top
evidence_cutoff + cutoff_meta + panel + cells both faces + nulls + D6 +
virtual starts + splits + walk-forward + robust + gates + ledger + TBC
advisory + flood disclosure) + cells/<cell>_<face>.json|.npy checkpoints +
nulls/<cell>_shard<k>.npy + cells_summary.csv.

Usage: run | selftest   (exit 0 ok; 2 = fail-closed gate refusal; 3 = RAM floor)
"""
import argparse
import glob
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
MASK = os.path.join(ROOT, "data", "fundamental", "b_layer_mask.csv")
SSE = os.path.join(ROOT, "Money02", "data", "index", "sse.parquet")
PROBE_JSON = os.path.join(ROOT, "results", "cn_kline_probe.json")
OUT_DIR = os.path.join(ROOT, "results", "cn_kline_pattern")
CELL_DIR = os.path.join(OUT_DIR, "cells")
NULL_DIR = os.path.join(OUT_DIR, "nulls")
OUT_JSON = os.path.join(OUT_DIR, "p1_results.json")
OUT_CSV = os.path.join(OUT_DIR, "cells_summary.csv")
ATT_JSON = os.path.join(ROOT, "results", "gate_attrition.json")

EVIDENCE_CUTOFF = "2026-09-22"
N_FILES_EXPECT = 5222
UNIVERSE_EXPECT = 3106
BATCH_NAME = "CN_KLINE_PATTERN_P1"
BATCH_CELLS = 2007            # 7 judged cells x1 + 2000 nulls (prereg s0)
K_NULLS = 2000
NULL_SHARDS = 8
PBP = 252
SEED = None                   # filled from SG.SEED_REGISTRY at run
MIN_ROWS = 500
MIN_AMT20 = 3e7
# EF params (prereg s2, probe authority)
HEAD_TOP = 0.3
BODY_RATIO = 2.0
RISE_5D = 1.05
CROW_TOP = 0.3
YANG_BODY_FRAC = 0.5
# execution faces (WILD-S1 frozen)
MAIN_FLOOR = 0.0975
WIDE_FLOOR = 0.1975
BSE_FLOOR = 0.2975            # EF: 'other' board 30cm band, no engine precedent
LIMIT_OPEN_TOL = 0.002
CN_20CM_FROM = np.datetime64("2020-08-24")
STAR_FROM = np.datetime64("2019-07-22")
N0 = 1.0e5                    # per-member leg notional CNY (EF, cost basis)
H_FIX = 10
H_BEAR = 20
WIN_DAYS = 126
STARTS_FROM = 200
SEG_MIN = 500
OOS_FROM = np.datetime64("2025-01-01")
D6_REJECT = 0.7
RAM_FLOOR_GB = 16.0
TBC_SAMPLE_MIN = 100           # TBC advisory insufficient-sample line (EF)

CELLS = [
    {"name": "MS-FIX10",   "pat": ("MS",),  "H": H_FIX,  "stop": False, "bear": False},
    {"name": "MS-STOP10",  "pat": ("MS",),  "H": H_FIX,  "stop": True,  "bear": False},
    {"name": "TWS-FIX10",  "pat": ("TWS",), "H": H_FIX,  "stop": False, "bear": False},
    {"name": "TWS-STOP10", "pat": ("TWS",), "H": H_FIX,  "stop": True,  "bear": False},
    {"name": "MS-BEAR",    "pat": ("MS",),  "H": H_BEAR, "stop": False, "bear": True},
    {"name": "TWS-BEAR",   "pat": ("TWS",), "H": H_BEAR, "stop": False, "bear": True},
    {"name": "COMBO",      "pat": ("MS", "TWS"), "H": H_BEAR, "stop": False, "bear": True},
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


# ------------------------------------------------------------------ panel
def _adv20_own(amount):
    """NaN-aware rolling-20 amount mean (min 10), own-index, float64."""
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


def _floor_own(dates, board):
    fl = np.full(len(dates), MAIN_FLOOR)
    if board == "chinext":
        fl[dates >= CN_20CM_FROM] = WIDE_FLOOR
    elif board == "star":
        fl[dates >= STAR_FROM] = WIDE_FLOOR
    elif board == "other":
        fl[:] = BSE_FLOOR
    return fl


def _encodings(o, h, l, c):
    """Probe-verbatim pattern encodings. Returns dict of bool arrays plus
    per-event stop levels for MS (l[e]) and TWS (l[d-2])."""
    n = len(c)
    body = np.abs(c - o)
    rng = h - l
    eps = 1e-12
    with np.errstate(divide="ignore", invalid="ignore"):
        small = (body / np.maximum(np.abs(o), eps)) < 0.005
        long_shadow = (rng / np.maximum(body, eps)) > 2.0
        a1 = small & long_shadow
        head_ok = (h - c) <= HEAD_TOP * np.maximum(rng, eps)
        crow_ok = (c - l) <= CROW_TOP * np.maximum(rng, eps)
    yang = c > o
    yin = c < o
    l13 = pd.Series(l).rolling(13).min().values
    c13 = pd.Series(c).rolling(13).min().values
    h30 = pd.Series(h).rolling(30).max().values
    c6ago = np.concatenate([np.full(6, np.nan), c[:-6]])   # c6ago[t] = c[t-6]
    c1 = np.concatenate([np.full(1, np.nan), c[:-1]])      # c1[t]  = c[t-1]
    body_frac_ok = body >= YANG_BODY_FRAC * np.maximum(rng, eps)

    ms = np.zeros(n, dtype=bool)
    ms_stop = np.full(n, np.nan)
    for d in range(14, n - 1):
        e = d - 1
        if not (yang[d] and body_frac_ok[d] and c[d] > c[e - 1]):
            continue
        if not (yin[e - 1] and a1[e] and (int(bool(a1[e - 1])) + int(bool(a1[e]))) == 1):
            continue
        if not (o[e] < c[e - 1]):
            continue
        if not (np.isfinite(l13[e]) and l[e - 1] == l13[e] and c1[e] == c13[e]):
            continue
        ms[d] = True
        ms_stop[d] = l[e]

    tws = np.zeros(n, dtype=bool)
    tws_stop = np.full(n, np.nan)
    for d in range(4, n):
        i, j, k = d - 2, d - 1, d
        if not (yin[i - 1] and yang[i] and yang[j] and yang[k]):
            continue
        if not (o[i] < o[j] < o[k] and c[i] < c[j] < c[k]):
            continue
        if not (head_ok[i] and head_ok[j] and head_ok[k]):
            continue
        b3 = [body[i], body[j], body[k]]
        if min(b3) <= 0 or max(b3) / min(b3) > BODY_RATIO:
            continue
        tws[d] = True
        tws_stop[d] = l[i]

    dcc = np.zeros(n, dtype=bool)
    for d in range(7, n):
        if not (yang[d - 1] and yin[d]):
            continue
        if not (o[d] > h[d - 1]):
            continue
        if not (c[d] < (o[d - 1] + c[d - 1]) / 2.0):
            continue
        if not (np.isfinite(c6ago[d - 1]) and c[d - 1] >= RISE_5D * c6ago[d - 1]):
            continue
        dcc[d] = True

    tbc = np.zeros(n, dtype=bool)
    for d in range(33, n):
        if not (yin[d - 2] and yin[d - 1] and yin[d]):
            continue
        if not (h[d - 2] == h30[d]):
            continue
        if not (c[d - 2] < l[d - 3] and c[d - 1] < l[d - 2] and c[d] < l[d - 1]):
            continue
        okb = all(min(o[i - 1], c[i - 1]) < o[i] < max(o[i - 1], c[i - 1])
                  for i in (d - 2, d - 1, d) if i - 1 >= 0)
        if not okb:
            continue
        if not (crow_ok[d - 2] and crow_ok[d - 1] and crow_ok[d]):
            continue
        tbc[d] = True

    return {"MS": ms, "MS_stop": ms_stop, "TWS": tws, "TWS_stop": tws_stop,
            "DCC": dcc, "TBC": tbc}


def load_panel():
    """Fail-closed gate battery (prereg s2) + panel assembly from bars."""
    files = sorted(glob.glob(os.path.join(BARS, "*.parquet")))
    if len(files) != N_FILES_EXPECT:
        return None, f"bars census drift: {len(files)} != {N_FILES_EXPECT}"
    if not os.path.exists(PROBE_JSON):
        return None, "frozen probe reference absent"
    probe = json.load(open(PROBE_JSON, encoding="utf-8"))
    if probe.get("panel", {}).get("cutoff") != EVIDENCE_CUTOFF:
        return None, "probe cutoff drift"

    mask = pd.read_csv(MASK)
    ok_codes = set(int(x) for x in mask.loc[mask["ok_static"] == True, "code"])
    board_of = {int(r.code): str(r.board) for r in mask.itertuples()}

    cut = np.datetime64(EVIDENCE_CUTOFF)
    cal_chunks = []
    skip = {"not_ok": 0, "rows": 0, "last": 0, "liq": 0}
    uni_files = []
    for p in files:
        code = int(os.path.basename(p)[:-8])
        df = pd.read_parquet(p, columns=["date", "amount"])
        dts = df["date"].values
        keep = dts <= cut
        cal_chunks.append(dts[keep])
        if code not in ok_codes:
            skip["not_ok"] += 1
            continue
        if int(keep.sum()) < MIN_ROWS:
            skip["rows"] += 1
            continue
        if str(dts[keep][-1])[:10] != EVIDENCE_CUTOFF:
            skip["last"] += 1
            continue
        amt = df["amount"].values[keep][-20:]
        if float(np.median(amt[np.isfinite(amt)])) < MIN_AMT20:
            skip["liq"] += 1
            continue
        uni_files.append((p, code, keep))
    calendar = np.unique(np.concatenate(cal_chunks))
    T_cal = len(calendar)

    p_face = probe.get("universe", {})
    if p_face.get("n") != len(uni_files) or p_face.get("skipped") != skip:
        return None, (f"universe re-derive drift: n={len(uni_files)}/{p_face.get('n')} "
                      f"skip={skip}/{p_face.get('skipped')}")
    if len(uni_files) != UNIVERSE_EXPECT:
        return None, f"universe n={len(uni_files)} != {UNIVERSE_EXPECT}"

    members = []
    census = {"MS": 0, "TWS": 0, "DCC": 0, "TBC": 0}
    boards_n = {}
    for p, code, keep in uni_files:
        df = pd.read_parquet(p)
        df = df.loc[keep]
        dts = df["date"].values
        o = df["open"].values.astype(float)
        h = df["high"].values.astype(float)
        l = df["low"].values.astype(float)
        c = df["close"].values.astype(float)
        v = df["volume"].values.astype(float)
        amt = df["amount"].values.astype(float)
        enc = _encodings(o, h, l, c)
        for k in census:
            census[k] += int(enc[k].sum())
        board = board_of.get(code, "main")
        boards_n[board] = boards_n.get(board, 0) + 1
        pcal = np.searchsorted(calendar, dts).astype(np.int32)
        # previous finite close per own index (昨收 face, suspension-aware)
        pc = np.full(len(c), np.nan)
        last = np.nan
        for i in range(len(c)):
            pc[i] = last
            if np.isfinite(c[i]):
                last = c[i]
        members.append({
            "code": code, "board": board, "o": o, "h": h, "l": l, "c": c,
            "v": v, "amt": amt, "n": len(c), "pcal": pcal, "pc": pc,
            "fl": _floor_own(dts.astype("datetime64[D]"), board),
            "adv": _adv20_own(amt),
            "enc": enc,
        })
    exp_census = {k: int(probe["census"][k]["n"]) for k in census}
    if census != exp_census:
        return None, f"pattern census drift: {census} vs probe {exp_census}"
    if boards_n != probe["universe"]["boards"]:
        return None, f"board census drift: {boards_n}"

    # sse onto calendar (ffill bridge, REV_OSC face)
    sse_df = pd.read_parquet(SSE)
    sse_df["date"] = pd.to_datetime(sse_df["date"])
    sse_close = sse_df.set_index("date")["close"].reindex(
        pd.DatetimeIndex(calendar)).ffill()
    cover = float(sse_close.notna().mean())
    sse_v = sse_close.to_numpy(dtype=np.float64)
    ma200 = pd.Series(sse_v).rolling(200, min_periods=200).mean().to_numpy()

    # universe-EW passive proxy on the calendar
    ew_sum = np.zeros(T_cal)
    ew_cnt = np.zeros(T_cal)
    for m in members:
        c = m["c"]
        with np.errstate(invalid="ignore"):
            r = c[1:] / c[:-1] - 1.0
        ok = np.isfinite(r)
        np.add.at(ew_sum, m["pcal"][1:][ok], r[ok])
        np.add.at(ew_cnt, m["pcal"][1:][ok], 1.0)
    ew = np.where(ew_cnt > 0, ew_sum / np.maximum(ew_cnt, 1.0), 0.0)

    face = {"files": N_FILES_EXPECT, "universe_n": len(members),
            "boards": boards_n, "skip": skip, "census": census,
            "T_cal": T_cal, "first": str(pd.Timestamp(calendar[0]).date()),
            "last": str(pd.Timestamp(calendar[-1]).date()),
            "sse_cover": round(cover, 4)}
    P = {"calendar": calendar, "calendar_d": calendar.astype("datetime64[D]"),
         "T_cal": T_cal, "members": members,
         "sse": sse_v, "ma200": ma200, "ew": ew, "face": face}
    return P, None


# ------------------------------------------------------------------ events
def build_event_tables(P):
    """Per pattern: flat arrays over (member_i, own sig day)."""
    tabs = {}
    for pname in ("MS", "TWS"):
        rows = {"mi": [], "t": [], "cal": [], "stop": []}
        for mi, m in enumerate(P["members"]):
            sig = np.flatnonzero(m["enc"][pname])
            rows["mi"].append(np.full(len(sig), mi, dtype=np.int32))
            rows["t"].append(sig.astype(np.int32))
            rows["cal"].append(m["pcal"][sig])
            rows["stop"].append(m["enc"][pname + "_stop"][sig])
        tabs[pname] = {k: (np.concatenate(v) if v else np.array([]))
                       for k, v in rows.items()}
    bear = {"mi": [], "t": [], "cal": []}
    for mi, m in enumerate(P["members"]):
        sig = np.flatnonzero(m["enc"]["DCC"] | m["enc"]["TBC"])
        bear["mi"].append(np.full(len(sig), mi, dtype=np.int32))
        bear["t"].append(sig.astype(np.int32))
        bear["cal"].append(m["pcal"][sig])
    tabs["BEAR"] = {k: (np.concatenate(v) if v else np.array([]))
                    for k, v in bear.items()}
    return tabs


def cell_events(cell, tabs):
    """Event list for a cell: [(cal, mi, t, stop_px)] deduped for COMBO."""
    seen = set()
    out = []
    for pname in cell["pat"]:
        tab = tabs[pname]
        for cal, mi, t, sp in zip(tab["cal"], tab["mi"], tab["t"], tab["stop"]):
            key = (int(mi), int(t))
            if cell["name"] == "COMBO" and key in seen:
                continue
            seen.add(key)
            out.append((int(cal), int(mi), int(t), float(sp)))
    out.sort(key=lambda x: (x[0], x[1]))
    return out


# ------------------------------------------------------------------ sim
def _cost_frac(cost_fn, adv):
    return cost_fn(N0, adv) / N0


def sim_trade(P, mi, sig_t, cell, cost_fn):
    """One event path -> (net, entry_cal, exit_cal, tag) or (None, tag)."""
    m = P["members"][mi]
    o, h, l, c, v = m["o"], m["h"], m["l"], m["c"], m["v"]
    n = m["n"]
    d = sig_t + 1
    while d < n and not (np.isfinite(o[d]) and np.isfinite(v[d])):
        d += 1
    if d >= n:
        return None, None, None, "susp_end"
    pc = m["pc"][d]
    if np.isfinite(pc) and o[d] / pc - 1.0 >= m["fl"][d] - LIMIT_OPEN_TOL:
        return None, None, None, "limit_reject"
    et = d
    entry = float(o[et])
    stop_px = None
    if cell["stop"]:
        sp = m["enc"]["MS_stop"][sig_t] if cell["pat"] == ("MS",) \
            else m["enc"]["TWS_stop"][sig_t]
        stop_px = float(sp) if np.isfinite(sp) else None
    x_target = et + cell["H"]
    u = et
    while u < n:
        if not (np.isfinite(o[u]) and np.isfinite(v[u])):
            u += 1
            continue
        if u >= x_target:
            cin = _cost_frac(cost_fn, m["adv"][et])
            cout = _cost_frac(cost_fn, m["adv"][u])
            net = float(o[u]) / entry * (1.0 - cout) / (1.0 + cin) - 1.0
            return net, int(m["pcal"][et]), int(m["pcal"][u]), "time"
        trig = False
        if stop_px is not None and np.isfinite(c[u]) and c[u] < stop_px:
            trig = True
        if cell["bear"] and (m["enc"]["DCC"][u] or m["enc"]["TBC"][u]):
            trig = True
        if trig:
            w = u + 1
            while w < n and not (np.isfinite(o[w]) and np.isfinite(v[w])):
                w += 1
            if w >= n:
                break
            cin = _cost_frac(cost_fn, m["adv"][et])
            cout = _cost_frac(cost_fn, m["adv"][w])
            net = float(o[w]) / entry * (1.0 - cout) / (1.0 + cin) - 1.0
            return net, int(m["pcal"][et]), int(m["pcal"][w]), \
                ("stop" if stop_px is not None and np.isfinite(c[u])
                 and c[u] < stop_px else "bear")
        u += 1
    # panel-end tail: mark to last finite close (honest)
    j = n - 1
    while j > et and not np.isfinite(c[j]):
        j -= 1
    px = float(c[j]) if np.isfinite(c[j]) else entry
    cin = _cost_frac(cost_fn, m["adv"][et])
    cout = _cost_frac(cost_fn, m["adv"][j])
    net = px / entry * (1.0 - cout) / (1.0 + cin) - 1.0
    return net, int(m["pcal"][et]), int(m["pcal"][j]), "tail"


def run_cell(P, cell, cost_fn, T_cal):
    """Cell daily series + counters (prereg s3 bucket accounting)."""
    events = cell_events(cell, P["tabs"])
    ser = np.zeros(T_cal)
    n_events = len(events)
    n_filled = 0
    rejects = {"limit_reject": 0, "susp_end": 0}
    exits = {"time": 0, "stop": 0, "bear": 0, "tail": 0}
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
        for _, mi, t, _sp in cohort:
            net, ecal, xcal, tag = sim_trade(P, mi, t, cell, cost_fn)
            if net is None:
                rejects[tag] = rejects.get(tag, 0) + 1
                continue
            exits[tag] = exits.get(tag, 0) + 1
            filled.append((net, ecal, xcal))
            n_filled += 1
        if not filled:
            empty_cohorts += 1
            continue
        m = len(filled)
        for net, ecal, xcal in filled:
            span = max(1, xcal - ecal)
            share = net / m / span
            lo = min(ecal + 1, T_cal)
            hi = min(xcal + 1, T_cal)
            if hi > lo:
                ser[lo:hi] += share
    return {"series": ser, "n_events": n_events, "n_filled": n_filled,
            "rejects": rejects, "exits": exits, "cohorts": cohorts,
            "empty_cohorts": empty_cohorts, "max_cohort": max_cohort,
            "cohort_members_total": n_events}


def cell_stats(series, calendar_d):
    r = np.asarray(series, dtype=np.float64)
    mu, sd = float(r.mean()), float(r.std(ddof=1)) if len(r) > 1 else 0.0
    sharpe = mu / sd * math.sqrt(PBP) if sd > 0 else 0.0
    eq = np.cumprod(1.0 + r)
    peak = np.maximum.accumulate(eq)
    dd = float((eq / peak - 1.0).min())
    ann = float(eq[-1] ** (PBP / max(len(r), 1)) - 1.0)
    i_oos = int(np.searchsorted(calendar_d, OOS_FROM))
    oos = r[i_oos:]
    oos_eq = np.cumprod(1.0 + oos)
    oos_ann = float(oos_eq[-1] ** (PBP / max(len(oos), 1)) - 1.0) \
        if len(oos) else None
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
def build_null_table(P, H, cost_fn):
    """Flat (pair) arrays over universe x valid days for one null H face.
    Per-member leg-cost array computed once (single-source V2 call per day,
    no hand-copied tiers) and cached on the member for both H tables."""
    sig, okflag, gross, entcal, span, cin_a, cout_a = [], [], [], [], [], [], []
    for mi, m in enumerate(P["members"]):
        n = m["n"]
        if n < 4:
            continue
        if cost_fn is side_cost_x2 and "cost2" not in m:
            m["cost2"] = np.array([_cost_frac(cost_fn, a) for a in m["adv"]])
        cost_arr = m.get("cost2")
        o, v = m["o"], m["v"]
        t_arr = np.arange(1, n - 1)                      # t in [1, n-2]
        trad = np.isfinite(o) & np.isfinite(v)
        # first tradable >= i (backward pass)
        nxt = np.full(n, -1, dtype=np.int64)
        last = -1
        for i in range(n - 1, -1, -1):
            last = i if trad[i] else last
            nxt[i] = last
        ent = nxt[t_arr + 1]                              # -1 if none
        valid = ent >= 0
        ent = np.where(valid, ent, 0)
        pc_e = m["pc"][ent]
        with np.errstate(invalid="ignore"):
            rej = np.isfinite(pc_e) & \
                (o[ent] / pc_e - 1.0 >= m["fl"][ent] - LIMIT_OPEN_TOL)
        ok = valid & ~rej & np.isfinite(o[ent])
        xu = np.where(ent + H < n, nxt[np.minimum(ent + H, n - 1)], -1)
        ok = ok & (xu >= 0)
        xu = np.where(ok, xu, 0)
        gr = np.where(ok, o[xu] / np.where(ok, o[ent], 1.0) - 1.0, np.nan)
        ecal = m["pcal"][ent]
        xcal = m["pcal"][xu]
        sp = np.where(ok, np.maximum(xcal - ecal, 1), 1)
        if cost_arr is not None:
            cin = cost_arr[ent]
            cout = cost_arr[xu]
        else:
            cin = np.zeros(len(t_arr))
            cout = np.zeros(len(t_arr))
        sig.append(m["pcal"][t_arr])
        okflag.append(ok)
        gross.append(gr.astype(np.float64))
        entcal.append(ecal.astype(np.int64))
        span.append(sp.astype(np.int64))
        cin_a.append(cin)
        cout_a.append(cout)
    cat = lambda xs: np.concatenate(xs) if xs else np.array([])
    return {"sig": cat(sig), "ok": cat(okflag), "gross": cat(gross),
            "entcal": cat(entcal), "span": cat(span), "cin": cat(cin_a),
            "cout": cat(cout_a)}


def null_draw(tbl, rng, N, T_cal):
    """One null cell draw -> Sharpe (prereg s3 own-null face)."""
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
    H = cell["H"]                   # null face = time-exit at cell H (EF)
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
            chunk[i] = null_draw(tbl, rng, n_events, P["T_cal"])
        np.save(path, chunk)
        vals[s * per:(s + 1) * per] = chunk
    cov = {"mu": round(float(vals.mean()), 4),
           "sigma": round(float(vals.std(ddof=1)), 4),
           "n_values": int(len(vals))}
    return {"values": [round(float(v), 4) for v in vals], "coverage": cov,
            "null_face": f"time-exit H={H} (EF: pattern stops undefined "
                         "on random events)",
            "n_drawn_pairs_per_draw": n_events}


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
    T = P["T_cal"]
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
    cal = pd.DatetimeIndex(P["calendar"])
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


def finalize(P, cells_out, nulls, d6, vstarts, robust):
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
                              file_name="cn_kline_pattern_p1",
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
               "events": {n: cells_out[n]["x2"]["n_events"] for n in cells_out}})

    tbc_n = int(P["face"]["census"]["TBC"])
    result = {
        "batch": BATCH_NAME,
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "cutoff_meta": SG.cutoff_meta(EVIDENCE_CUTOFF),
        "prereg": "research/CN_KLINE_PATTERN_PREREG.md (@cbf6c93c freeze)",
        "seed": {"base": SEED, "k": K_NULLS},
        "panel": P["face"],
        "cost": {"face_judged": "x2 (side_cost_x2, V2 components doubled)",
                 "x1": "side_cost_v2 disclosure column",
                 "leg_notional_cny": N0,
                 "adv20": "NaN-aware rolling-20 amount mean per leg day; "
                          "NaN -> krules 10bp fallback"},
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
        "robust": robust, "family_pbo": pbo, "gates": gates,
        "trials_ledger": ledger,
        "tbc_advisory": {
            "n_tbc": tbc_n,
            "insufficient_sample": bool(tbc_n < TBC_SAMPLE_MIN),
            "note": "TBC dead-face honest (prereg s2); DCC = main bear "
                    "operating face, TBC = advisory union member only"},
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
    SEED = SG.SEED_REGISTRY["cn_kline_pattern_p1"]
    if _free_ram_gb() < RAM_FLOOR_GB:
        print("free-RAM floor refused")
        return 3
    t0 = time.time()
    P, err = load_panel()
    if err:
        return gate_refuse(err)
    print(f"panel ok: {P['face']}", flush=True)
    os.makedirs(CELL_DIR, exist_ok=True)
    os.makedirs(NULL_DIR, exist_ok=True)
    P["tabs"] = build_event_tables(P)

    cells_out = {}
    for cell in CELLS:
        name = cell["name"]
        cells_out[name] = {}
        for face, fn in (("x1", side_cost_v2), ("x2", side_cost_x2)):
            ck = os.path.join(CELL_DIR, f"{name}_{face}.json")
            if os.path.exists(ck):
                blob = json.load(open(ck, encoding="utf-8"))
                blob["series"] = np.load(ck.replace(".json", ".npy"))
            else:
                r = run_cell(P, cell, fn, P["T_cal"])
                np.save(ck.replace(".json", ".npy"), r["series"])
                blob = {"series": r["series"],
                        "stats": cell_stats(r["series"], P["calendar_d"]),
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
    for H in (H_FIX, H_BEAR):
        tables[H] = build_null_table(P, H, side_cost_x2)
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
    res = finalize(P, cells_out, nulls, d6, vstarts, robust)
    print(f"finalize ok: cells={len(res['cells'])} "
          f"ledger={res['trials_ledger']['total']} "
          f"elapsed={time.time() - t0:.0f}s")
    return 0


# ------------------------------------------------------------------ selftest
def _mk_fixture(tmp, T=460, N=12):
    """Hermetic synthetic bars: planted MS/TWS/DCC/TBC + negative control."""
    bars = os.path.join(tmp, "bars")
    os.makedirs(bars)
    cal = pd.date_range(end=EVIDENCE_CUTOFF, periods=T,
                        freq="B").as_unit("us")
    codes = [600001 + i for i in range(8)] + [300001, 688001, 600091, 600092]
    boards = ["main"] * 8 + ["chinext", "star", "main", "main"]
    ok = [True] * 10 + [False, True]          # 600091 not_ok

    def bg(df, i):
        # alternating tiny yang/yin -- no pattern can fire on the background
        o, c = (10.0, 10.02) if i % 2 == 0 else (10.02, 10.0)
        df.loc[i, ["open", "close"]] = o, c
        df.loc[i, "high"] = max(o, c) + 0.01
        df.loc[i, "low"] = min(o, c) - 0.01

    def candle(df, i, o, c, h=None, l=None):
        df.loc[i, "open"] = o
        df.loc[i, "close"] = c
        df.loc[i, "high"] = h if h is not None else max(o, c) + 0.01
        df.loc[i, "low"] = l if l is not None else min(o, c) - 0.01

    frames = []
    for k, code in enumerate(codes):
        df = pd.DataFrame(index=range(T))
        df["date"] = cal
        for col in ("open", "close", "high", "low", "volume", "amount"):
            df[col] = np.nan
        for i in range(T):
            bg(df, i)
        df["volume"] = 1e6
        df["amount"] = 5e7

        if code == 600001:                    # MS + near-limit entry reject
            t0 = 100
            for j, cc in enumerate(np.linspace(9.5, 7.6, 12)):
                candle(df, t0 + j, cc + 0.3, cc, cc + 0.35, cc - 0.05)
            candle(df, t0 + 12, 7.5, 7.0, 7.55, 6.95)      # big yin e-1
            candle(df, t0 + 13, 6.98, 7.01, 7.12, 6.96)    # doji e
            candle(df, t0 + 14, 7.0, 7.8, 7.9, 6.95)       # recovery d
            candle(df, t0 + 15, 8.58, 7.2, 8.6, 7.1)       # +10% open: reject
        if code == 600002:                    # MS + suspension roll at entry
            t0 = 150
            for j, cc in enumerate(np.linspace(9.5, 7.6, 12)):
                candle(df, t0 + j, cc + 0.3, cc, cc + 0.35, cc - 0.05)
            candle(df, t0 + 12, 7.5, 7.0, 7.55, 6.95)
            candle(df, t0 + 13, 6.98, 7.01, 7.12, 6.96)
            candle(df, t0 + 14, 7.0, 7.8, 7.9, 6.95)
            df.loc[t0 + 15, ["open", "close", "high", "low", "volume",
                             "amount"]] = np.nan            # susp entry day
            candle(df, t0 + 16, 8.0, 8.1)
        if code == 600003:                    # MS + stop trigger in hold
            t0 = 200
            for j, cc in enumerate(np.linspace(9.5, 7.6, 12)):
                candle(df, t0 + j, cc + 0.3, cc, cc + 0.35, cc - 0.05)
            candle(df, t0 + 12, 7.5, 7.0, 7.55, 6.95)
            candle(df, t0 + 13, 6.98, 7.01, 7.12, 6.96)
            candle(df, t0 + 14, 7.0, 7.8, 7.9, 6.95)
            candle(df, t0 + 15, 7.85, 6.9, 7.9, 6.85)   # close < stop 6.96
        if code == 600004:                    # TWS + DCC-in-hold (bear test)
            candle(df, 199, 10.2, 10.0, 10.25, 9.95)     # yin i-1
            candle(df, 200, 10.0, 10.3, 10.35, 9.98)     # soldier i
            candle(df, 201, 10.4, 10.7, 10.75, 10.38)    # soldier j
            candle(df, 202, 10.8, 11.1, 11.15, 10.78)    # soldier k (signal)
            candle(df, 203, 11.1, 11.2)
            candle(df, 204, 11.2, 11.4)
            candle(df, 205, 11.4, 11.5, 11.55, 11.35)
            candle(df, 206, 11.6, 11.0, 11.65, 10.9)     # DCC signal day
            candle(df, 207, 11.0, 10.9)
        if code == 600005:                    # plain TWS
            candle(df, 299, 10.2, 10.0, 10.25, 9.95)
            candle(df, 300, 10.0, 10.3, 10.35, 9.98)
            candle(df, 301, 10.4, 10.7, 10.75, 10.38)
            candle(df, 302, 10.8, 11.1, 11.15, 10.78)
        if code == 600006:                    # DCC (rise context)
            for j, cc in enumerate(np.linspace(10.0, 10.6, 6)):
                candle(df, 294 + j, cc - 0.1, cc)
            candle(df, 299, 10.6, 10.8, 10.85, 10.55)
            candle(df, 300, 10.9, 10.2, 10.95, 10.1)
        if code == 600007:                    # TBC
            candle(df, 397, 11.5, 11.4, 11.6, 11.3)
            candle(df, 398, 11.45, 11.0, 12.0, 10.9)      # AA: HHV30 high
            candle(df, 399, 11.05, 10.4, 11.1, 10.3)
            candle(df, 400, 10.45, 9.8, 10.5, 9.7)
        if code == 600008:                    # negative control: no gap-down
            t0 = 350
            for j, cc in enumerate(np.linspace(9.5, 7.6, 12)):
                candle(df, t0 + j, cc + 0.3, cc, cc + 0.35, cc - 0.05)
            candle(df, t0 + 12, 7.5, 7.0, 7.55, 6.95)
            candle(df, t0 + 13, 7.05, 7.06, 7.15, 7.0)    # doji, NO gap-down
            candle(df, t0 + 14, 7.0, 7.8, 7.9, 6.95)
        df = df[["date", "open", "close", "high", "low", "volume", "amount"]]
        df.to_parquet(os.path.join(bars, f"{code}.parquet"))
        frames.append(code)

    pd.DataFrame({"code": codes, "board": boards,
                  "ok_static": ok}).to_csv(
        os.path.join(tmp, "mask.csv"), index=False)
    pd.DataFrame({"date": cal,
                  "close": np.linspace(3000, 2500, T)}).to_parquet(
        os.path.join(tmp, "sse.parquet"))
    return bars, codes, cal


def cmd_selftest():
    global BARS, MASK, SSE, PROBE_JSON, OUT_DIR, CELL_DIR, NULL_DIR, \
        OUT_JSON, OUT_CSV, ATT_JSON, SEED, K_NULLS, NULL_SHARDS, \
        N_FILES_EXPECT, UNIVERSE_EXPECT, MIN_ROWS, MIN_AMT20, N0
    tmp = tempfile.mkdtemp(prefix="cn_kline_selftest_")
    K_NULLS, NULL_SHARDS = 30, 2      # skill_line_v2 thin-line floor = 30
    SEED = 20275100
    N0 = 1.0e5
    bars, codes, cal = _mk_fixture(tmp)
    BARS = bars
    MASK = os.path.join(tmp, "mask.csv")
    SSE = os.path.join(tmp, "sse.parquet")
    OUT_DIR = os.path.join(tmp, "out")
    CELL_DIR = os.path.join(OUT_DIR, "cells")
    NULL_DIR = os.path.join(OUT_DIR, "nulls")
    OUT_JSON = os.path.join(OUT_DIR, "p1_results.json")
    OUT_CSV = os.path.join(OUT_DIR, "cells_summary.csv")
    ATT_JSON = os.path.join(tmp, "attr.json")
    os.makedirs(CELL_DIR, exist_ok=True)
    os.makedirs(NULL_DIR, exist_ok=True)
    json.dump({"entries": []}, open(ATT_JSON, "w"))
    N_FILES_EXPECT = len(codes)
    MIN_ROWS = 100
    MIN_AMT20 = 1.0
    ok = []

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

    # fixture probe: derive census on the synthetic panel, freeze as gate ref
    probe_counts = {"MS": 0, "TWS": 0, "DCC": 0, "TBC": 0}
    for code in codes:
        df = pd.read_parquet(os.path.join(bars, f"{code}.parquet"))
        enc = _encodings(df["open"].values.astype(float),
                         df["high"].values.astype(float),
                         df["low"].values.astype(float),
                         df["close"].values.astype(float))
        for kk in probe_counts:
            probe_counts[kk] += int(enc[kk].sum())
    # planted expectations: MS 3 (600001/2/3) -- 600008 negative control must
    # NOT fire; TWS 3 (600004, 600005 + one honest extra on the 600006 DCC
    # rise ladder); DCC 2 (600006 + 600004 in-hold); TBC 1
    exp = {"MS": 3, "TWS": 3, "DCC": 2, "TBC": 1}
    ok.append(("planted census == expected", probe_counts == exp))
    PROBE_JSON = os.path.join(tmp, "probe.json")
    json.dump({"panel": {"cutoff": EVIDENCE_CUTOFF},
               "universe": {"n": 11, "boards": {"main": 9, "chinext": 1,
                                                 "star": 1},
                            "skipped": {"not_ok": 1, "rows": 0, "last": 0,
                                        "liq": 0}},
               "census": {k: {"n": v} for k, v in probe_counts.items()}},
              open(PROBE_JSON, "w"))
    UNIVERSE_EXPECT = 11

    try:
        P, err = load_panel()
        ok.append(("panel gate pass", err is None))
        if err:
            raise RuntimeError(err)
        ok.append(("universe n", P["face"]["universe_n"] == 11))
        ok.append(("census gate", P["face"]["census"] == probe_counts))
        ok.append(("sse coverage", P["face"]["sse_cover"] >= 0.99))

        P["tabs"] = build_event_tables(P)
        ms_cal = P["tabs"]["MS"]["cal"]
        ok.append(("MS events 3", len(P["tabs"]["MS"]["mi"]) == 3))
        ok.append(("negative control absent (600008)",
                   600008 not in [P["members"][i]["code"]
                                  for i in P["tabs"]["MS"]["mi"]]))

        # [5] near-limit entry reject counted (member 0 = 600001)
        cell = CELLS[0]
        r0 = run_cell(P, cell, side_cost_x2, P["T_cal"])
        ok.append(("near-limit reject", r0["rejects"]["limit_reject"] >= 1))

        # [6] suspension roll at entry + time-exit booking math (600002)
        m1 = [i for i, m in enumerate(P["members"])
              if m["code"] == 600002][0]
        net, ecal, xcal, tag = sim_trade(P, m1, 150 + 14, cell, side_cost_x2)
        m = P["members"][m1]
        ok.append(("susp roll entry", tag == "time" and
                   m["pcal"][150 + 16] == ecal and xcal == ecal + 10))
        ser = r0["series"]
        share_days = np.flatnonzero(ser)
        ok.append(("booking span face (2 trades x 10d, disjoint)",
                   len(share_days) == 20))

        # [7] stop arm: close < doji low -> exit next open (600003)
        cell_stop = CELLS[1]
        m2 = [i for i, m in enumerate(P["members"])
              if m["code"] == 600003][0]
        net, ecal, xcal, tag = sim_trade(P, m2, 200 + 14, cell_stop,
                                         side_cost_x2)
        ok.append(("stop trigger next-open exit", tag == "stop" and
                   xcal == P["members"][m2]["pcal"][200 + 16]))

        # [8] bear arm: DCC in hold -> next-open out (600004)
        cell_bear = CELLS[5]
        m3 = [i for i, m in enumerate(P["members"])
              if m["code"] == 600004][0]
        net, ecal, xcal, tag = sim_trade(P, m3, 202, cell_bear, side_cost_x2)
        ok.append(("bear exit next-open", tag == "bear" and
                   xcal == P["members"][m3]["pcal"][207]))

        # [9] cost math: V2 x2 on both legs (600002 time exit)
        cin = side_cost_x2(N0, P["members"][m1]["adv"][150 + 16]) / N0
        cout = side_cost_x2(N0, P["members"][m1]["adv"][150 + 26]) / N0
        exp_net = (P["members"][m1]["o"][150 + 26] /
                   P["members"][m1]["o"][150 + 16] *
                   (1 - cout) / (1 + cin) - 1)
        net1, ecal1, xcal1, tag1 = sim_trade(P, m1, 150 + 14, cell,
                                             side_cost_x2)
        ok.append(("x2 cost math", tag1 == "time" and
                   abs(net1 - exp_net) < 1e-12))

        # [10] full cell run both faces + stats
        cells_out = {}
        for c in CELLS:
            rr = run_cell(P, c, side_cost_x2, P["T_cal"])
            cells_out[c["name"]] = {"x2": {
                "series": rr["series"],
                "stats": cell_stats(rr["series"], P["calendar_d"]),
                "n_events": rr["n_events"], "n_filled": rr["n_filled"],
                "rejects": rr["rejects"], "exits": rr["exits"],
                "cohorts": rr["cohorts"],
                "empty_cohorts": rr["empty_cohorts"],
                "max_cohort": rr["max_cohort"]}}
            rr1 = run_cell(P, c, side_cost_v2, P["T_cal"])
            cells_out[c["name"]]["x1"] = {
                "series": rr1["series"],
                "stats": cell_stats(rr1["series"], P["calendar_d"]),
                "n_events": rr1["n_events"], "n_filled": rr1["n_filled"],
                "rejects": rr1["rejects"], "exits": rr1["exits"],
                "cohorts": rr1["cohorts"],
                "empty_cohorts": rr1["empty_cohorts"],
                "max_cohort": rr1["max_cohort"]}
        ok.append(("cells 7x2", len(cells_out) == 7 and all(
            len(v) == 2 for v in cells_out.values())))

        # [11] null tables + own pools, deterministic
        tbl10 = build_null_table(P, H_FIX, side_cost_x2)
        ok.append(("null table nonempty", int(tbl10["ok"].sum()) > 100))
        v1 = null_draw(tbl10, np.random.default_rng(SEED), 3, P["T_cal"])
        v2 = null_draw(tbl10, np.random.default_rng(SEED), 3, P["T_cal"])
        ok.append(("null draw deterministic", v1 == v2 and
                   np.isfinite(v1)))
        tbl_by_H = {H_FIX: tbl10, H_BEAR: build_null_table(
            P, H_BEAR, side_cost_x2)}
        nulls = {}
        for c in CELLS:
            nulls[c["name"]] = run_cell_nulls(
                P, c, tbl_by_H, cells_out[c["name"]]["x2"]["n_events"])
        ok.append(("null pools 7 x 30 finite", len(nulls) == 7 and all(
            len(v["values"]) == 30 and np.isfinite(v["values"]).all()
            for v in nulls.values())))

        # [12] virtual starts / segments / walk-forward
        sbc = {n: cells_out[n]["x2"]["series"] for n in cells_out}
        vs = virtual_starts(P, sbc)
        ok.append(("vstarts census",
                   vs["n_starts"] == P["T_cal"] - WIN_DAYS - STARTS_FROM))
        rb = robust_stats(sbc["MS-FIX10"])
        ok.append(("robust finite", np.isfinite(rb["obs_sharpe"]) and
                   0.0 <= rb["sign_flip_p"] <= 1.0))

        # [13] D6 face: real member files read repo paths (hermetic tmp has
        # none) -> stub dict is passed straight into finalize (arg face)
        d6 = {"cells": {n: {"reject": False} for n in sbc}}

        # [14] finalize product (stubbed SG faces) + TBC advisory flag
        res = finalize(P, cells_out, nulls, d6, vs, {"MS-FIX10": rb})
        ok.append(("finalize product", os.path.exists(OUT_JSON) and
                   res["trials_ledger"]["total"] == 100))
        ok.append(("TBC insufficient-sample flag",
                   res["tbc_advisory"]["insufficient_sample"] is True and
                   res["tbc_advisory"]["n_tbc"] == 1))
        ok.append(("cutoff_meta key",
                   "cutoff_meta" in res and
                   res["evidence_cutoff"] == EVIDENCE_CUTOFF))
        att = json.load(open(ATT_JSON, encoding="utf-8"))
        ok.append(("attrition row entries face",
                   att["entries"][-1]["batch"] == BATCH_NAME and
                   "entries" in att["entries"][-1]))
    finally:
        SG.n_eff, SG.passive_baseline, SG.append_ledger = _ne, _pb, _al
        SG.ledger_head = _lh
        globals()["cscv_pbo"] = _real_cscv
        shutil.rmtree(tmp, ignore_errors=True)

    n_ok = sum(1 for _, v in ok if v)
    print(f"cn_kline_pattern_p1 selftest: {n_ok}/{len(ok)} PASS")
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
            os.environ.get("CN_KLINE_PATTERN_P1_REFINALIZE") != "1":
        print("idempotent no-op: p1_results.json exists "
              "(CN_KLINE_PATTERN_P1_REFINALIZE=1 = only redo)")
        return 0
    return cmd_run()


if __name__ == "__main__":
    sys.exit(main())
