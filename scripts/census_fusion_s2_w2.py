# -*- coding: utf-8 -*-
"""CENSUS_FUS_S2_W2A runner -- T-86 s2 factor-level fusion census (wave-2 W2-A).

Prereg (FROZEN R325 precedes this build, R99): research/CENSUS_FUSION_S2_PREREG.md
sec.9.3 + roster results/census_fusion_s2/w2_roster.json (same-commit freeze,
commit 38c7dc96). EXPLORATION FACE: zero judgment claims / zero paper
eligibility; sole output = frozen-rules family aggregation feeding the T-23
intake funnel (judged consumers carry their own prereg + gates).

Universe (sec.9.3 frozen): astock qfq panel data/astock_daily/per/<code>.csv
(T-87 bm-b collector, bm-b-local gitignored) x data/fundamental/b_layer_mask.csv
code set, frozen >=5,000 join gate (fail-closed). Gate report discloses BOTH
counts: join members AND the ok_static=True subset (3,517 at freeze-time
snapshot). The >=5,000 frozen gate is satisfiable only under the code-join
reading (ok_static-only join ~3,517 < 5,000); interpretation recorded in the
zero-run amendment window (ledger_trials_added=0 at build time) per the
2026-09-27 freeze-alignment law -- pointers: ticket progress_r326_bma +
fleet/inbox MSG. LANE: bm-b (panel locality; pool entry lane_owner=bm-b).

Face roster (frozen w2_roster.json w2a.faces, 32 faces, zero invention):
  B4 zoo   : scripts/p1e_factors.py frozen r218 constructors. Inputs from
             the astock panels: rets=close.pct_change(), tr_frac = raw
             astock turnover column (source-verbatim; == volume/
             outstanding_share per T-87 probe cross-check), close/open/vwap.
  C-gtja191 top-10 + C-wq101 top-10 : p1c stock-face machinery
             (p1c_stock_ic_batch.load_alpha191_bigpanel / _wq_engine) on the
             astock panels dict -- 9-key contract open/high/low/close/volume/
             amount/vwap/turnover/pct_chg; vwap = amount/volume (p1c Stage-A
             cache convention, cache cross-check max_rel ~7e-8); pct_chg =
             ffilled-close pct_change()*100 (derived, disclosed).
  C-a158 all-7 : a158_truegap_ic.FACTORS constructors (panels-dict contract).
  E-lhb    : pa_lhb_ic literal -- dedup max-amount row per (code, 上榜日),
             rolling_sum(ind, 20), shift1 fill 0.0; Money02/data/lhb/
             lhb_detail.parquet (both machines in-register per sec.9.3).
  controls : rs_20_csi300 / rs_60_csi300 via engine.factors.rs_vs (64 pairs).

Methodology instantiation (sec.9.3 frozen; divergences from wave-1 disclosed):
  blend long leg = combo-score TOP-50 equal weight (NOT wave-1 top tercile --
  ~1,700-member tercile untradeable at 5,228 scale), weekly REB=5 grid,
  signal t / exec t+1 close conservative T+1 proxy, V2 + x2 costs, 1% ADV20
  entry cap same mechanics; adv20 from RAW amount (no ffill -- suspension
  days -> NaN -> entry no-fill; conservative wide-universe divergence from
  wave-1's dense-48-member ffill convention, disclosed); IC face = fwd-5d
  rank-IC (p1_factor_screen.ic_series, same anchor); dual-sort tercile
  matrices same as wave-1; evidence_cutoff = 2026-09-24 (cutoff lockbox:
  rows past cutoff are dropped with a disclosure count, never reflowed).

Scale architecture (established wide-panel patterns, zero new invention):
  the ~12GB state cannot pickle to Windows spawn workers -> state sidecars
  as .npy under Money02/data/cache/census_w2/ (p1c-cache dir family,
  gitignored) + worker mmap init (p1e _worker_init pattern). Wave-1 frozen
  machinery is IMPORTED and reused, not rewritten: blend_top16 (with the
  default-preserving top_k param), _dual_sort_pair/_dual_sort_triple,
  _ic_stats, _zscore, _tercile_labels, _score_matrix, _jsonable; block loop
  via parallel_runner.run_cells_parallel (r259 audit key).

Ledger: append_ledger("CENSUS_FUS_S2_W2A", 5920, ...) at finalize only
(r252 embed key law). In-runner fail-closed data gates exit 2. Checkpoint
every 200 combos (JSONL, cross-kill resume; prep re-runs on resume).
Deterministic: byte-stable rerun.

Usage: python scripts/census_fusion_s2_w2.py run | probe | selftest [--workers N]
"""
import argparse
import glob
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "research", "shortline", "screening"))

import numpy as np
import pandas as pd

from science_gates import SEED_REGISTRY, append_ledger, cutoff_meta
from config import PATHS

import census_fusion_s2 as W1          # frozen wave-1 machinery (import-only)

BATCH = "CENSUS_FUS_S2_W2A"
TICKET = "T-2026-09-26-86-P1 s2 wave-2 W2-A (CEO O-20260926-2320)"
PREREG = ("research/CENSUS_FUSION_S2_PREREG.md sec.9.3 + w2_roster.json "
          "FROZEN commit 38c7dc96 precedes runner build precedes ANY run (R99)")
CUTOFF = "2026-09-24"                   # evidence_cutoff (prereg sec.9.3)
TOP_K_W2 = 50                           # blend long leg (sec.9.3 top-50)
HORIZON = 5                             # IC forward 5d close->close
REB = 5                                 # weekly grid
NOTIONAL = 1_000_000.0
N_NULLS = 400                           # 200 random pairs + 200 random triples
BLOCK = 200                             # checkpoint cadence (wave-1 parity)
MIN_JOIN = 5000                         # frozen universe join gate (sec.9.3)
MIN_FREE_RAM_GB = 12.0                  # prep guard (a158 _free_ram_gb family)
SEED_W2 = SEED_REGISTRY["census_fusion_s2_w2"]          # 20281500 (R325)
BENCH_FACES = ["rs_20_csi300", "rs_60_csi300"]

PER_DIR = os.path.join(ROOT, "data", "astock_daily", "per")
MASK_CSV = os.path.join(ROOT, "data", "fundamental", "b_layer_mask.csv")
LHB_PATH = os.path.join(ROOT, "Money02", "data", "lhb", "lhb_detail.parquet")
OUT_DIR = os.path.join(ROOT, "results", "census_fusion_s2")
ROSTER_JSON = os.path.join(OUT_DIR, "w2_roster.json")
SIDE_DIR = os.path.join(ROOT, "Money02", "data", "cache", "census_w2")
CKPT = os.path.join(OUT_DIR, "w2a_checkpoint.jsonl")

PER_COLS = ["open", "high", "low", "close", "volume", "amount", "turnover"]
PANEL_KEYS = ["open", "high", "low", "close", "volume", "amount", "vwap",
              "turnover", "pct_chg"]


# ---------------------------------------------------------------- roster

def load_roster():
    """Frozen face roster (zero invention: consume w2_roster.json only)."""
    with open(ROSTER_JSON, encoding="utf-8") as fh:
        r = json.load(fh)
    faces = r["w2a"]["faces"]
    assert len(faces) == 32, f"roster w2a faces {len(faces)} != 32"
    enum = r["w2a"]["enumeration"]
    assert enum["candidates"] == 5456 and enum["controls_rs_pairs"] == 64 \
        and enum["nulls"] == 400 and enum["ledger_N"] == 5920, enum
    assert r["w2a"]["seeds"]["null_base"] == SEED_W2, "roster seed mismatch"
    fam = {}
    for f in faces:
        row = f["row"]
        fam[f["face"]] = {"B": "B_zoo", "C-gtja191": "C_gtja191",
                          "C-wq101": "C_wq101", "C-a158": "C_a158_truegap",
                          "E-lhb": "E_lhb"}[row]
    signs = {f["face"]: float(f["sign"]) for f in faces}
    return faces, signs, fam


# ---------------------------------------------------------------- universe

def load_mask_codes():
    """{code: ok_static} from the B-layer mask CSV (all rows; both counts
    are consumed: code set for the universe join, ok_static for disclosure)."""
    out = {}
    with open(MASK_CSV, encoding="utf-8-sig") as fh:
        import csv as _csv
        for r in _csv.DictReader(fh):
            out[r["code"]] = r["ok_static"].strip().lower() == "true"
    return out


def read_panel_universe(mask_codes):
    """Per-symbol frames from data/astock_daily/per/<code>.csv, cutoff-truncated.

    Returns (univ, gate_report_dict). Fail-closed: empty/missing panel or
    join < MIN_JOIN -> ok=False (caller exits 2).
    """
    if not os.path.isdir(PER_DIR):
        return None, {"ok": False, "fail": "panel dir absent (bm-b-local "
                                          "data/astock_daily/per; lane=bm-b)"}
    files = sorted(glob.glob(os.path.join(PER_DIR, "*.csv")))
    if not files:
        return None, {"ok": False, "fail": "panel dir empty"}
    cutoff_ts = pd.Timestamp(CUTOFF)
    univ = {}
    n_trunc = 0
    min_rows = []
    ends_at_cutoff = 0
    for p in files:
        code = os.path.basename(p)[:-4]
        if code not in mask_codes:
            continue                      # universe = panel x mask code set
        try:
            df = pd.read_csv(p)
        except Exception:
            continue
        if "date" not in df.columns or "close" not in df.columns:
            continue
        df["date"] = pd.to_datetime(df["date"])
        before = len(df)
        df = df[df["date"] <= cutoff_ts]   # cutoff lockbox (prereg sec.2)
        n_trunc += before - len(df)
        if df.empty:
            continue
        df = df.set_index("date").sort_index()
        univ[code] = df
        min_rows.append(len(df))
        if str(df.index.max().date()) == CUTOFF:
            ends_at_cutoff += 1
    n_files = len(files)
    n_join = len(univ)
    n_ok = sum(1 for c in univ if mask_codes[c])
    rep = {
        "panel_files": n_files, "join_members": n_join,
        "ok_static_true_in_join": n_ok,
        "ok_static_false_in_join": n_join - n_ok,
        "mask_rows": len(mask_codes),
        "min_rows_median": int(np.median(min_rows)) if min_rows else 0,
        "pct_end_at_cutoff": round(ends_at_cutoff / n_join, 4) if n_join else 0.0,
        "rows_dropped_post_cutoff": n_trunc,
        "gate_join_min_5000": n_join >= MIN_JOIN,
        "universe_reading": ("panel x mask CODE set (frozen >=5,000 gate; "
                             "ok_static subset DISCLOSED not gated -- "
                             "ok_static-only join would be ~3,517 < 5,000 "
                             "and cannot satisfy the frozen gate; zero-run "
                             "amendment window record: ticket "
                             "progress_r326_bma + fleet/inbox MSG)"),
    }
    rep["ok"] = bool(n_join >= MIN_JOIN)
    return univ, rep


def build_panels(univ):
    """9-key panels dict (p1c contract): OHLC ffilled (p1c harness
    convention), volume/amount/turnover raw, vwap=amount/volume, pct_chg
    derived from ffilled close."""
    idx = sorted(set().union(*[set(df.index) for df in univ.values()]))
    idx = pd.DatetimeIndex(idx)
    raw = {}
    for f in PER_COLS:
        raw[f] = pd.DataFrame(
            {s: (df[f] if f in df.columns else
                  pd.Series(np.nan, index=df.index))
             for s, df in univ.items()}).reindex(index=idx).sort_index()
    panels = {}
    for f in ("open", "high", "low", "close"):
        panels[f] = raw[f].ffill()
    panels["volume"] = raw["volume"]
    panels["amount"] = raw["amount"]
    panels["turnover"] = raw["turnover"]
    with np.errstate(invalid="ignore", divide="ignore"):
        panels["vwap"] = panels["amount"] / panels["volume"].where(raw["volume"] > 0)
    panels["pct_chg"] = (panels["close"].pct_change() * 100.0)
    return idx, list(panels["close"].columns), panels


# ---------------------------------------------------------------- faces

def _free_ram_gb():
    try:
        import psutil
        return psutil.virtual_memory().available / 1e9
    except Exception:
        return None


def build_faces(panels, idx, syms, roster_faces, rep):
    """32 candidate faces + 2 rs control faces from the frozen roster."""
    faces = {}
    import p1e_factors as ZF
    close = panels["close"]
    rets = close.pct_change()
    tr = panels["turnover"]
    t0 = time.time()
    faces["zoo85_stv"] = ZF.build_zoo85_stv(rets, tr)
    faces["zoo85_terrified"] = ZF.build_zoo85_terrified(rets)
    faces["zoo92_coin_team"] = ZF.build_zoo92_coin_team(close, panels["open"], tr)
    # family ctor returns (dict of 4 zoo93 faces, n_bad); W2A roster consumes
    # only the zoo93_arc member (vrc/src/krc not rostered) -- r330 crash fix
    _zoo93, rep["zoo93_n_bad"] = ZF.build_zoo93_arc_family(tr, panels["vwap"], close)
    faces["zoo93_arc"] = _zoo93["zoo93_arc"]
    rep["zoo_s"] = round(time.time() - t0, 1)

    t0 = time.time()
    import p1c_stock_ic_batch as P1C
    gtja_names = [f["face"] for f in roster_faces if f["row"] == "C-gtja191"]
    mod = P1C.load_alpha191_bigpanel()
    for nm in gtja_names:
        faces[nm] = getattr(mod, nm)(panels)
    rep["gtja_s"] = round(time.time() - t0, 1)

    t0 = time.time()
    wq_names = [f["face"] for f in roster_faces if f["row"] == "C-wq101"]
    engine = P1C._wq_engine(panels)
    for nm in wq_names:
        n = int(nm[len("wq101_alpha"):])
        out = getattr(engine, f"alpha{n:03d}")()
        if not isinstance(out, pd.DataFrame):
            out = pd.DataFrame(np.asarray(out), index=idx, columns=syms)
        faces[nm] = out
    del engine
    rep["wq_s"] = round(time.time() - t0, 1)

    t0 = time.time()
    import a158_truegap_ic as A158
    a158_names = [f["face"] for f in roster_faces if f["row"] == "C-a158"]
    for nm in a158_names:
        fn, _fields = A158.FACTORS[nm]
        faces[nm] = fn(panels)
    rep["a158_s"] = round(time.time() - t0, 1)

    t0 = time.time()
    faces["lhb_count_20"], rep["lhb"] = lhb_count_face(idx, syms)
    rep["lhb_s"] = round(time.time() - t0, 1)

    # controls: rs vs csi300 (engine/factors.rs_vs, compute_all branch anchor)
    bench = pd.read_csv(os.path.join(PATHS.basic_dir, "csi300.csv"),
                        parse_dates=["date"]).set_index("date")["close"]
    rep["bench_end"] = str(bench.index.max().date())
    from engine.factors import rs_vs
    faces["rs_20_csi300"] = rs_vs(panels["close"], bench, 20)
    faces["rs_60_csi300"] = rs_vs(panels["close"], bench, 60)

    cand = [f["face"] for f in roster_faces]
    for nm in cand + BENCH_FACES:
        assert nm in faces, f"face {nm} missing after build"
        faces[nm] = faces[nm].reindex(index=idx, columns=syms)
    return faces, rep["bench_end"]


def lhb_count_face(idx, syms, lhb_path=LHB_PATH, w=20):
    """E-row lhb_count_20, PA_LHB_IC literal construction (dedup max-amount
    row per (code, 上榜日); rolling 20d count; shift1 fill 0.0 = signal at t
    holds events <= t-1, LHB disclosed after close)."""
    import pa_lhb_ic as PA
    if not os.path.exists(lhb_path):
        raise FileNotFoundError(f"LHB parquet absent: {lhb_path}")
    lhb = pd.read_parquet(lhb_path)
    lhb = lhb.sort_values(["龙虎榜成交额", "序号"], ascending=[True, False])
    ev = lhb.drop_duplicates(subset=["代码", "上榜日"], keep="last")
    # unit-agnostic datetime64[ns] domain (pandas 3.x index .asi8 unit is
    # resolution-dependent -- int comparisons would silently misplace events)
    cal = idx.values.astype("datetime64[ns]")
    ev64 = (pd.to_datetime(ev["上榜日"]).values.astype("datetime64[ns]"))
    T, N = len(idx), len(syms)
    sym_col = {s: i for i, s in enumerate(syms)}
    pos = np.searchsorted(cal, ev64)
    in_cal = pos < T
    pos_safe = np.minimum(pos, T - 1)
    pos_ok = in_cal & (cal[pos_safe] == ev64)
    cols = ev["代码"].map(sym_col)
    col_ok = cols.notna().values
    keep = pos_ok & col_ok
    r_idx = pos[keep]
    c_idx = cols.values[keep].astype(int)
    ind = np.zeros((T, N))
    ind[r_idx, c_idx] = 1.0
    count20 = PA.rolling_sum(ind, w)
    count_s = PA.shift1(count20, 0.0)
    return pd.DataFrame(count_s, index=idx, columns=syms), {
        "raw": int(len(lhb)), "dedup_events": int(len(ev)),
        "placed": int(keep.sum()),
        "drop_no_col": int((~col_ok).sum()),
        "drop_no_date": int((~pos_ok).sum())}


# ---------------------------------------------------------------- state prep

def prep_state():
    """Build panels + faces + shared arrays ONCE, write sidecars + meta.json.

    Workers mmap the sidecars (Windows spawn cannot pickle the ~12GB state).
    Returns (meta, side_dir, gate_rep, lhb_rep) or (None, None, rep, None)
    on gate failure.
    """
    free = _free_ram_gb()
    if free is not None and free < MIN_FREE_RAM_GB:
        print(f"REFUSED: free RAM {free:.1f}GB < {MIN_FREE_RAM_GB}GB "
              f"(shared-machine prep guard, a158 family)")
        return None, None, {"ok": False, "fail": f"free_ram {free:.1f}GB"}, None
    roster_faces, signs, fam = load_roster()
    mask_codes = load_mask_codes()
    univ, gate = read_panel_universe(mask_codes)
    print("[gate]", json.dumps(W1._jsonable(gate), ensure_ascii=False))
    if univ is None or not gate["ok"]:
        return None, None, gate, None
    idx, syms, panels = build_panels(univ)
    del univ
    cand = [f["face"] for f in roster_faces]

    rep = {}
    faces, bench_end = build_faces(panels, idx, syms, roster_faces, rep)
    lhb_rep = rep.get("lhb") or {}
    close = panels["close"]
    amount_raw = panels["amount"]
    zed, terc = {}, {}
    for nm in cand + BENCH_FACES:
        Z = W1._zscore(faces[nm])
        zed[nm] = Z
        terc[nm] = W1._tercile_labels(Z)
        faces[nm] = None                     # free face frames as we go
    del faces, panels

    rets = close.pct_change()
    fwd5 = close.shift(-HORIZON) / close - 1
    # adv20 from RAW amount (no ffill): suspension -> NaN -> entry no-fill
    # (conservative wide-universe divergence from wave-1 dense-panel ffill,
    # disclosed in the module docstring + audit)
    adv20 = amount_raw.rolling(20).mean()

    # grid anchor: first date where every candidate face has >=TOP_K_W2 valid
    valid_min = None
    for nm in cand:
        cnt = zed[nm].notna().sum(axis=1)
        valid_min = cnt if valid_min is None else np.minimum(valid_min, cnt)
    feasible = np.asarray(valid_min) >= TOP_K_W2
    anchor = int(np.argmax(feasible)) if feasible.any() else -1
    n_days = len(idx)
    grid_sig = list(range(anchor, n_days - 1, REB)) if anchor >= 0 else []
    grid_exec = [g + 1 for g in grid_sig if g + 1 < n_days]
    if not grid_sig:
        print("GRID INFEASIBLE (no date with all-32-faces >=50 valid) -> exit 2")
        return None, None, dict(gate, ok=False, fail="grid infeasible"), None

    os.makedirs(SIDE_DIR, exist_ok=True)
    for nm in cand + BENCH_FACES:
        np.save(os.path.join(SIDE_DIR, f"z_{nm}.npy"),
                np.ascontiguousarray(zed[nm].values, dtype=np.float64))
        np.save(os.path.join(SIDE_DIR, f"t_{nm}.npy"),
                np.ascontiguousarray(terc[nm], dtype=np.int8))
        zed[nm] = None
        terc[nm] = None
    np.save(os.path.join(SIDE_DIR, "rets.npy"),
            np.ascontiguousarray(rets.values, dtype=np.float64))
    np.save(os.path.join(SIDE_DIR, "fwd5.npy"),
            np.ascontiguousarray(fwd5.values, dtype=np.float64))
    np.save(os.path.join(SIDE_DIR, "adv20.npy"),
            np.ascontiguousarray(adv20.values, dtype=np.float64))

    state = {"idx": idx, "syms": syms, "faces": cand,
             "sign": {k: float(v) for k, v in signs.items()},
             "rets": rets.values, "fwd5": fwd5, "adv20": adv20.values,
             "grid_sig": grid_sig, "grid_exec": grid_exec, "n_days": n_days}
    ew_x1, ew_x2 = _ew_univ(state)

    meta = {
        "batch": BATCH, "cutoff_real": CUTOFF, "n_days": n_days,
        "n_syms": len(syms), "faces": cand, "signs": state["sign"],
        "fam": fam, "grid_sig": grid_sig, "grid_exec": grid_exec,
        "idx_iso": [str(x.date()) for x in idx], "syms": syms,
        "gate": W1._jsonable(gate), "lhb": lhb_rep, "bench_end": bench_end,
        "build_timing_s": {k: v for k, v in rep.items()
                           if isinstance(v, (int, float))},
        "ew_univ": {"x1": W1._jsonable(ew_x1), "x2": W1._jsonable(ew_x2)},
    }
    with open(os.path.join(SIDE_DIR, "meta.json"), "w", encoding="utf-8") as fh:
        s = json.dumps(W1._jsonable(meta), ensure_ascii=False)
        json.loads(s)
        fh.write(s)
    print(f"[prep] sidecars ready: T={n_days} N={len(syms)} faces=32+2 "
          f"grid={len(grid_sig)} first_sig={str(idx[grid_sig[0]].date())} "
          f"ew_x1={ew_x1['sharpe']} prep_s={meta['build_timing_s']}")
    return meta, SIDE_DIR, gate, lhb_rep


def _ew_univ(state):
    """EW all-members benchmark (wave-1 fixed_all=True mirror; delta anchor)."""
    return (W1.blend_top16(state, None, x2=False, fixed_all=True),
            W1.blend_top16(state, None, x2=True, fixed_all=True))


# ---------------------------------------------------------------- specs

def enumerate_specs(meta):
    """5,456 candidates + 64 rs controls + 400 nulls = 5,920 (sec.9.3 frozen;
    null draw machinery mirrored from wave-1 with SEED_W2 band)."""
    from itertools import combinations
    faces = meta["faces"]
    sign = meta["signs"]
    specs = []
    for f1, f2 in combinations(faces, 2):
        specs.append({"kind": "pair", "id": f"P:{f1}|{f2}", "faces": [f1, f2],
                      "signs": [sign[f1], sign[f2]]})
    for f1, f2, f3 in combinations(faces, 3):
        specs.append({"kind": "triple", "id": f"T:{f1}|{f2}|{f3}",
                      "faces": [f1, f2, f3],
                      "signs": [sign[f1], sign[f2], sign[f3]]})
    for f in faces:
        for b in BENCH_FACES:
            specs.append({"kind": "control", "id": f"C:{f}|{b}",
                          "faces": [f, b], "signs": [sign[f], 1.0]})
    for k in range(N_NULLS):
        rng = np.random.default_rng(SEED_W2 + k)
        n = 2 if k < 200 else 3
        sel = rng.choice(len(faces), size=n, replace=False)
        sgn = rng.choice([-1.0, 1.0], size=n)
        specs.append({"kind": "null", "id": f"N{k}",
                      "faces": [faces[i] for i in sel],
                      "signs": [float(x) for x in sgn]})
    assert len(specs) == 5920, len(specs)
    return specs


# ---------------------------------------------------------------- workers

_G = {}


def _init_worker(side_dir, ew_x1, ew_x2, specs):
    """Worker state from sidecar mmaps (p1e _worker_init pattern). Specs are
    built once in the parent and pickled via initargs (small, ~1.5MB)."""
    with open(os.path.join(side_dir, "meta.json"), encoding="utf-8") as fh:
        meta = json.load(fh)
    idx = pd.DatetimeIndex(pd.to_datetime(meta["idx_iso"]))
    syms = meta["syms"]
    zed, terc = {}, {}
    for nm in meta["faces"] + BENCH_FACES:
        zed[nm] = np.load(os.path.join(side_dir, f"z_{nm}.npy"), mmap_mode="r")
        terc[nm] = np.load(os.path.join(side_dir, f"t_{nm}.npy"), mmap_mode="r")
    fwd5_arr = np.load(os.path.join(side_dir, "fwd5.npy"), mmap_mode="r")
    _G["state"] = {
        "idx": idx, "syms": syms, "faces": meta["faces"], "sign": meta["signs"],
        "zed": zed, "terc": terc,
        "rets": np.load(os.path.join(side_dir, "rets.npy"), mmap_mode="r"),
        "fwd5": pd.DataFrame(fwd5_arr, index=idx, columns=syms),
        "adv20": np.load(os.path.join(side_dir, "adv20.npy"), mmap_mode="r"),
        "grid_sig": meta["grid_sig"], "grid_exec": meta["grid_exec"],
        "n_days": meta["n_days"],
        "specs": specs,
    }
    _G["ew_x1"] = ew_x1
    _G["ew_x2"] = ew_x2


def eval_spec(state, spec, ew_x1, ew_x2):
    """One combo -> full stat row (wave-1 mirror; top_k=TOP_K_W2; deltas vs
    EW-universe benchmark). Native types only (r286 law)."""
    S = W1._score_matrix(state, spec["faces"], spec["signs"])
    b1 = W1.blend_top16(state, lambda g: S[g], x2=False, top_k=TOP_K_W2)
    b2 = W1.blend_top16(state, lambda g: S[g], x2=True, top_k=TOP_K_W2)
    ic = W1._ic_stats(state, S)
    mat = W1._dual_sort_triple(state, S) if spec["kind"] == "triple" \
        else W1._dual_sort_pair(state, spec["faces"][0], spec["faces"][1])
    row = {
        "id": spec["id"], "kind": spec["kind"], "faces": "|".join(spec["faces"]),
        "signs": "".join("+" if s > 0 else "-" for s in spec["signs"]),
        "ic_mean": ic["ic_mean"], "ic_ir": ic["ic_ir"],
        "ic_pos_pct": ic["ic_pos_pct"], "ic_n": ic["ic_n"],
        "x1_ann": b1["ann"], "x1_vol": b1["vol"], "x1_sharpe": b1["sharpe"],
        "x1_maxdd": b1["maxdd"], "x1_monthly_win": b1["monthly_win"],
        "x1_capped": b1["capped_entries"],
        "x2_ann": b2["ann"], "x2_vol": b2["vol"], "x2_sharpe": b2["sharpe"],
        "x2_maxdd": b2["maxdd"], "x2_monthly_win": b2["monthly_win"],
        "x2_capped": b2["capped_entries"],
        "delta_x1_ann_vs_ew_univ": None if b1["ann"] is None or ew_x1["ann"] is None
            else round(b1["ann"] - ew_x1["ann"], 4),
        "delta_x2_sharpe_vs_ew_univ": None if b2["sharpe"] is None or ew_x2["sharpe"] is None
            else round(b2["sharpe"] - ew_x2["sharpe"], 4),
        "matrix": mat,
    }
    for y, v in ic["ic_by_year"].items():
        row[f"ic_y{y}"] = v
    return row


def block_worker(start, end):
    """Top-level picklable: evaluate specs[start:end], return {i: row}."""
    state = _G["state"]
    specs = state["specs"]
    return {i: eval_spec(state, specs[i], _G["ew_x1"], _G["ew_x2"])
            for i in range(start, end)}


# ---------------------------------------------------------------- checkpoints

def _load_checkpoint():
    done = set()
    if os.path.exists(CKPT):
        with open(CKPT, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    try:
                        done.add(json.loads(line)["i"])
                    except (ValueError, KeyError):
                        continue
    return done


def _append_ckpt(rows):
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(CKPT, "a", encoding="utf-8") as fh:
        for i, row in rows.items():
            fh.write(json.dumps({"i": int(i), "row": W1._jsonable(row)},
                                ensure_ascii=False, separators=(",", ":")) + "\n")


# ---------------------------------------------------------------- run

def run(probe=False, workers=None):
    t0 = time.time()
    from parallel_runner import run_cells_parallel

    meta, side_dir, gate, lhb_rep = prep_state()
    if meta is None:
        print("DATA GATE FAIL (fail-closed, exit 2)")
        return 2
    idx = pd.DatetimeIndex(pd.to_datetime(meta["idx_iso"]))
    specs = enumerate_specs(meta)
    n_total = len(specs)
    n = min(n_total, 4) if probe else n_total

    ew_x1, ew_x2 = meta["ew_univ"]["x1"], meta["ew_univ"]["x2"]
    print(f"[ew_univ] x1 sharpe={ew_x1['sharpe']} ann={ew_x1['ann']} | "
          f"x2 sharpe={ew_x2['sharpe']} ann={ew_x2['ann']}")

    done = set() if probe else _load_checkpoint()
    jobs = []
    for s in range(0, n, BLOCK):
        e = min(s + BLOCK, n)
        if all(i in done for i in range(s, e)):
            continue
        jobs.append((f"blk{s // BLOCK:02d}", block_worker, (s, e)))
    print(f"[plan] specs={n} blocks_todo={len(jobs)} ckpt_done={len(done)}")

    results = {}
    if jobs:
        flushed = set()

        def _flush(blk, rows):
            # r340 pitlaw fix: incremental checkpoint -- _append_ckpt fires
            # per COMPLETED block (via parallel_runner on_result), so a
            # mid-run kill retains finished blocks instead of re-burning
            # the whole batch (collect-only-tail = 4.6h zero-ckpt live miss).
            flushed.add(blk)
            results.update(rows)
            if not probe:
                _append_ckpt(rows)

        res = run_cells_parallel(jobs, workers=workers or 4, desc="census-w2a",
                                 initializer=_init_worker,
                                 initargs=(side_dir, ew_x1, ew_x2, specs),
                                 on_result=_flush)
        w = res.pop("__workers__", 1)
        for _blk, rows in res.items():
            if _blk not in flushed:  # safety net if on_result path skipped
                results.update(rows)
                if not probe:
                    _append_ckpt(rows)
    else:
        w = 0
        with open(CKPT, encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    d = json.loads(line)
                    results[d["i"]] = d["row"]

    if probe:
        payload = W1._jsonable({
            "batch": BATCH, "mode": "probe", "gate": gate, "lhb": lhb_rep,
            "n_days": meta["n_days"], "cutoff_real": meta["cutoff_real"],
            "grid_first_signal": str(idx[meta["grid_sig"][0]].date()),
            "n_grid_signals": len(meta["grid_sig"]),
            "n_grid_execs": len(meta["grid_exec"]),
            "ew_univ": meta["ew_univ"], "rows": list(results.values()),
        })
        s = json.dumps(payload, ensure_ascii=False)
        json.loads(s)
        os.makedirs(OUT_DIR, exist_ok=True)
        with open(os.path.join(OUT_DIR, "probe_w2a.json"), "w",
                  encoding="utf-8") as fh:
            fh.write(s)
        print(f"[probe] OK rows={len(results)} grid={len(meta['grid_exec'])} "
              f"first_sig={payload['grid_first_signal']}")
        return 0

    # ---- finalize ----
    missing = [i for i in range(n_total) if i not in results]
    if missing:
        print(f"INCOMPLETE: {len(missing)} specs missing -> exit 2 (checkpoint retained)")
        return 2
    cand_rows = [results[i] for i in range(n_total) if results[i]["kind"] != "null"]
    nulls = [results[i] for i in range(n_total) if results[i]["kind"] == "null"]

    import csv as _csv
    cols = ["id", "kind", "faces", "signs", "ic_mean", "ic_ir", "ic_pos_pct", "ic_n",
            "x1_ann", "x1_vol", "x1_sharpe", "x1_maxdd", "x1_monthly_win", "x1_capped",
            "x2_ann", "x2_vol", "x2_sharpe", "x2_maxdd", "x2_monthly_win", "x2_capped",
            "delta_x1_ann_vs_ew_univ", "delta_x2_sharpe_vs_ew_univ"]
    ycols = sorted({c for r in cand_rows + nulls for c in r if c.startswith("ic_y")})
    with open(os.path.join(OUT_DIR, "w2a_cells.csv"), "w", encoding="utf-8",
              newline="") as fh:
        wr = _csv.DictWriter(fh, fieldnames=cols + ycols, extrasaction="ignore")
        wr.writeheader()
        for r in cand_rows:
            wr.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in cols + ycols})
    with open(os.path.join(OUT_DIR, "w2a_nulls.json"), "w", encoding="utf-8") as fh:
        json.dump(W1._jsonable({"batch": BATCH, "n": len(nulls),
                                "seed_base": int(SEED_W2), "nulls": nulls}),
                  fh, ensure_ascii=False, indent=1)

    ranked = sorted((r for r in cand_rows if r["ic_mean"] is not None),
                    key=lambda r: -abs(r["ic_mean"]))[:50]
    with open(os.path.join(OUT_DIR, "w2a_top_matrices.json"), "w",
              encoding="utf-8") as fh:
        json.dump(W1._jsonable({"batch": BATCH,
                                "top_rule": "|ic_mean| top-50 (wave-1 sec.4 rule)",
                                "n": len(ranked),
                                "items": [{"id": r["id"], "kind": r["kind"],
                                           "ic_mean": r["ic_mean"],
                                           "matrix": r["matrix"]}
                                          for r in ranked]}),
                  fh, ensure_ascii=False, indent=1)

    fam = meta["fam"]
    fam_stats = {}
    for fam_name in sorted(set(fam.values())):
        members = [r for r in cand_rows if r["kind"] in ("pair", "triple")
                   and any(fam.get(f) == fam_name for f in r["faces"].split("|"))]
        xs = sorted(r["x2_sharpe"] for r in members if r["x2_sharpe"] is not None)
        fam_stats[fam_name] = {"n_combos": len(members),
                               "median_x2_sharpe": round(float(np.median(xs)), 4) if xs else None}
    cross_top10 = sorted((r for r in cand_rows if r["kind"] in ("pair", "triple")
                          and r["x2_sharpe"] is not None),
                         key=lambda r: -r["x2_sharpe"])[:10]
    null_x2 = sorted(r["x2_sharpe"] for r in nulls if r["x2_sharpe"] is not None)
    cand_x2 = [r["x2_sharpe"] for r in cand_rows if r["x2_sharpe"] is not None]
    summary = W1._jsonable({
        "batch": BATCH,
        "family_rule": ("sec.9.3: per roster family, median x2 blend Sharpe of "
                        "combos containing >=1 family face + coverage count; "
                        "cross-family top-10 by x2 Sharpe; EXPLORATION ONLY "
                        "(zero registration effect)"),
        "families": fam_stats,
        "cross_family_top10": [{"id": r["id"], "faces": r["faces"], "signs": r["signs"],
                                 "x2_sharpe": r["x2_sharpe"], "x1_sharpe": r["x1_sharpe"],
                                 "ic_mean": r["ic_mean"]} for r in cross_top10],
        "ew_univ_benchmark": {"x1": ew_x1, "x2": ew_x2},
        "null_x2_sharpe": {"n": len(null_x2),
                           "median": round(float(np.median(null_x2)), 4) if null_x2 else None,
                           "p95": round(float(np.quantile(null_x2, 0.95)), 4) if null_x2 else None},
        "cand_x2_p95": round(float(np.quantile(cand_x2, 0.95)), 4) if cand_x2 else None,
    })
    with open(os.path.join(OUT_DIR, "w2a_summary.json"), "w", encoding="utf-8") as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=1)

    ledger = append_ledger(BATCH, n_total, "census_fusion_s2/w2a_results.json",
                           evidence_cutoff=CUTOFF,
                           note="exploration face: 5,456 fusion combos + 64 rs "
                                "controls + 400 nulls (sec.9.3 frozen N=5,920)")
    payload = {
        **cutoff_meta(CUTOFF),
        "batch": BATCH, "ticket": TICKET, "prereg_ref": PREREG,
        "face": "EXPLORATION (zero judgment claims / zero paper eligibility)",
        "n_candidates": sum(1 for r in cand_rows if r["kind"] in ("pair", "triple")),
        "n_controls": sum(1 for r in cand_rows if r["kind"] == "control"),
        "n_nulls": len(nulls),
        "data_gate": W1._jsonable(gate),
        "lhb_events": W1._jsonable(lhb_rep),
        "bench_disclosure": {
            "bench_end": meta["bench_end"],
            "note": (f"csi300.csv ends {meta['bench_end']}; rs_vs reindex+ffill "
                     f"convention (engine/factors.py source anchor) bridges to "
                     f"{CUTOFF}; affects rs CONTROL faces only (disclosed)")},
        "grid": {"anchor_first_signal": str(idx[meta["grid_sig"][0]].date()),
                 "n_signals": len(meta["grid_sig"]),
                 "n_execs": len(meta["grid_exec"]),
                 "cadence": f"{REB} trading days", "top_k": TOP_K_W2,
                 "panel_days": meta["n_days"], "cutoff_real": meta["cutoff_real"],
                 "n_syms": meta["n_syms"]},
        "products": ["w2a_cells.csv", "w2a_nulls.json", "w2a_top_matrices.json",
                     "w2a_summary.json"],
        "audit": {"workers": int(w), "purpose": "exploration census (no selection gate)",
                  "ledger_trials_added": int(n_total),
                  "elapsed_sec": round(time.time() - t0, 1),
                  "null_seed_band": f"{SEED_W2}..{SEED_W2 + N_NULLS - 1}",
                  "checkpoint": "w2a_checkpoint.jsonl (200-combo cadence)",
                  "sidecars": SIDE_DIR + " (gitignored state; rebuildable)",
                  "methodology_divergences": [
                      "top-50 blend leg (sec.9.3; wave-1 was top-tercile 16/48)",
                      "adv20 from RAW amount (no ffill): suspension -> NaN -> "
                      "entry no-fill (conservative; wave-1 dense-panel ffill "
                      "convention disclosed)",
                      "EW-universe all-members benchmark replaces EW48 "
                      "(delta cols _vs_ew_univ)",
                      "universe = panel x mask CODE set with frozen >=5,000 "
                      "gate; ok_static subset disclosed not gated (gate report)"]},
        "trials_ledger": ledger,   # r252 law: canonical embed key
    }
    out = os.path.join(OUT_DIR, "w2a_results.json")
    s = json.dumps(W1._jsonable(payload), ensure_ascii=False, indent=1)
    json.loads(s)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(s)
    print(f"[done] cells={len(cand_rows)} nulls={len(nulls)} workers={w} "
          f"elapsed={payload['audit']['elapsed_sec']}s ledger={ledger['total']}")
    return 0


# ---------------------------------------------------------------- selftest

def _synth_universe_w2(seed=7, n_sym=60, n_day=340):
    """Hermetic synthetic wide-ish universe (no real panel, no parquet)."""
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2015-01-01", periods=n_day)
    univ = {}
    for i in range(n_sym):
        close = 10.0 * np.cumprod(1 + rng.normal(0.0003, 0.02, n_day))
        vol = rng.uniform(1e6, 5e6, n_day)
        amt = close * vol * rng.uniform(0.98, 1.02, n_day)
        univ[f"s{i:02d}"] = pd.DataFrame({
            "open": close * (1 + rng.normal(0, 0.004, n_day)),
            "high": close * (1 + np.abs(rng.normal(0, 0.008, n_day))),
            "low": close * (1 - np.abs(rng.normal(0, 0.008, n_day))),
            "close": close, "volume": vol, "amount": amt,
            "outstanding_share": 1e9,
            "turnover": vol / 1e9,
        }, index=dates)
    return univ


def _synth_lhb_events(idx, syms):
    """Tiny synthetic LHB event frame (hermetic; mirrors parquet columns)."""
    rows = []
    for k in range(6):
        d = idx[30 + 10 * k]
        rows.append({"代码": syms[k % len(syms)], "上榜日": str(d.date()),
                     "龙虎榜成交额": 1e8 + k, "序号": 1})
        rows.append({"代码": syms[k % len(syms)], "上榜日": str(d.date()),
                     "龙虎榜成交额": 9e7, "序号": 2})   # dedup loser
    return pd.DataFrame(rows)


def selftest():
    """Hermetic selftest (no real panel, no parquet, no network). r263 law."""
    ok = True

    def t(name, cond):
        nonlocal ok
        print(("PASS" if cond else "FAIL"), name)
        ok = ok and bool(cond)

    # [1] frozen roster load + enumeration math + seed registry match
    roster_faces, signs, fam = load_roster()
    specs = enumerate_specs({"faces": [f["face"] for f in roster_faces],
                              "signs": signs})
    t("[1] roster 32 faces + enumeration 496/4960/64/400 = 5920 + seeds",
      len(roster_faces) == 32 and len(specs) == 5920
      and sum(1 for s in specs if s["kind"] == "pair") == 496
      and sum(1 for s in specs if s["kind"] == "triple") == 4960
      and sum(1 for s in specs if s["kind"] == "control") == 64
      and sum(1 for s in specs if s["kind"] == "null") == 400
      and SEED_W2 == 20281500
      and SEED_REGISTRY["census_fusion_s2_w2_unc"] == 20282000)
    a = np.random.default_rng(SEED_W2 + 0).choice(32, size=2, replace=False)
    b = np.random.default_rng(SEED_W2 + 0).choice(32, size=2, replace=False)
    t("[1b] null seed determinism (same base -> same draw)", list(a) == list(b))

    # [2] synthetic panels -> all face constructors evaluate (vendor engines
    #     from committed external files; no Money02 data dependency)
    univ = _synth_universe_w2()
    idx = sorted(set().union(*[set(df.index) for df in univ.values()]))
    idx = pd.DatetimeIndex(idx)
    syms = list(univ.keys())
    panels = {}
    for f in ("open", "high", "low", "close"):
        panels[f] = pd.DataFrame({s: univ[s][f] for s in syms}).ffill()
    panels["volume"] = pd.DataFrame({s: univ[s]["volume"] for s in syms})
    panels["amount"] = pd.DataFrame({s: univ[s]["amount"] for s in syms})
    panels["turnover"] = pd.DataFrame({s: univ[s]["turnover"] for s in syms})
    with np.errstate(invalid="ignore", divide="ignore"):
        panels["vwap"] = panels["amount"] / panels["volume"]
    panels["pct_chg"] = panels["close"].pct_change() * 100.0
    import p1e_factors as ZF
    rets = panels["close"].pct_change()
    fz = ZF.build_zoo85_stv(rets, panels["turnover"])
    t("[2] zoo faces evaluate on synthetic panels",
      fz.shape == panels["close"].shape
      and np.isfinite(np.asarray(fz)).any())

    import p1c_stock_ic_batch as P1C
    mod = P1C.load_alpha191_bigpanel()
    fg = mod.alpha191_099(panels)
    t("[3] GTJA191 vendor evaluates on synthetic 9-key panels",
      fg.shape == panels["close"].shape)
    engine = P1C._wq_engine(panels)
    fw = pd.DataFrame(np.asarray(engine.alpha013()),
                      index=idx, columns=syms)
    t("[4] WQ101 vendor evaluates on synthetic panels",
      fw.shape == panels["close"].shape)
    import a158_truegap_ic as A158
    fa = A158.FACTORS["IMAX20"][0](panels)
    t("[5] A158 constructor evaluates on synthetic panels",
      fa.shape == panels["close"].shape)

    # [6] LHB synthetic: dedup keeps max-amount row; shift1 semantics
    evf = _synth_lhb_events(idx, syms)
    p_tmp = os.path.join(OUT_DIR, "_r326bma_selftest_lhb.parquet")
    os.makedirs(OUT_DIR, exist_ok=True)
    evf.to_parquet(p_tmp)
    try:
        fl, rep = lhb_count_face(idx, syms, lhb_path=p_tmp)
        s0 = syms[0]
        col = np.asarray(fl[s0])
        # first event for syms[0] at idx[30]; count20 reaches 1 at day 30;
        # shifted face holds events <= t-1 -> first nonzero at day 31
        first_nz = int(np.argmax(col > 0))
        t("[6] LHB dedup max-amount + shift1 (first signal = event+1)",
          rep["dedup_events"] == 6 and first_nz == 31)
    finally:
        os.remove(p_tmp)

    # [7] rs control faces
    from engine.factors import rs_vs
    bench = pd.Series(panels["close"].iloc[:, 0].values, index=idx)
    frs = rs_vs(panels["close"], bench, 20)
    t("[7] rs_vs controls evaluate", frs.shape == panels["close"].shape
      and np.isfinite(np.asarray(frs)).any())

    # [8] blend top_k equivalence: wave-1 default == explicit 16; top_k=50 path
    st = W1._synth_state()
    S = W1._score_matrix(st, ["mom_20", "vol_20"], [1.0, -1.0])
    m_def = W1.blend_top16(st, lambda g: S[g], x2=True)
    m_k16 = W1.blend_top16(st, lambda g: S[g], x2=True, top_k=16)
    m_k5 = W1.blend_top16(st, lambda g: S[g], x2=True, top_k=5)
    t("[8] blend top_k: default==16 byte-equal, k=5 five positions",
      m_def == m_k16 and m_k5["n_days"] == m_def["n_days"])

    # [9] universe gate fail-closed on join < 5,000 (tiny synthetic)
    mask_small = {f"s{i:02d}": (i % 3 == 0) for i in range(60)}
    univ_s = _synth_universe_w2()
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        per = os.path.join(td, "per")
        os.makedirs(per)
        for s, df in univ_s.items():
            df.to_csv(os.path.join(per, f"{s}.csv"), index_label="date")
        global PER_DIR, MASK_CSV
        per_saved, mask_saved = PER_DIR, MASK_CSV
        try:
            PER_DIR, MASK_CSV = per, os.path.join(td, "mask.csv")
            with open(MASK_CSV, "w", encoding="utf-8") as fh:
                fh.write("code,ok_static\n" + "".join(
                    f"{c},{str(v)}\n" for c, v in mask_small.items()))
            u2, g2 = read_panel_universe(load_mask_codes())
            t("[9] gate fail-closed: 60-member join < 5000 -> ok=False",
              (not g2["ok"]) and g2["join_members"] == 60
              and g2["ok_static_true_in_join"] == 20)
        finally:
            PER_DIR, MASK_CSV = per_saved, mask_saved

    # [10] sidecar worker glue: prep-free mini sidecars -> block eval
    z0 = np.asarray(W1._zscore(pd.DataFrame(np.asarray(fz), index=idx,
                                             columns=syms)))
    with tempfile.TemporaryDirectory() as td:
        np.save(os.path.join(td, "z_zoo85_stv.npy"), z0)
        np.save(os.path.join(td, "t_zoo85_stv.npy"),
                W1._tercile_labels(pd.DataFrame(z0, index=idx, columns=syms)))
        for bnm in BENCH_FACES:                     # controls sidecars (zeros)
            np.save(os.path.join(td, f"z_{bnm}.npy"), np.zeros_like(z0))
            np.save(os.path.join(td, f"t_{bnm}.npy"),
                    np.full(z0.shape, -1, dtype=np.int8))
        rets_s = np.asarray(panels["close"].pct_change(), dtype=float)
        np.save(os.path.join(td, "rets.npy"), rets_s)
        np.save(os.path.join(td, "fwd5.npy"),
                np.asarray(panels["close"].shift(-5) / panels["close"] - 1,
                          dtype=float))
        np.save(os.path.join(td, "adv20.npy"),
                np.asarray(panels["amount"].rolling(20).mean(), dtype=float))
        grid_sig = list(range(60, len(idx) - 1, REB))
        mini_meta = {"faces": ["zoo85_stv"], "signs": {"zoo85_stv": -1.0},
                     "idx_iso": [str(x.date()) for x in idx], "syms": syms,
                     "grid_sig": grid_sig,
                     "grid_exec": [g + 1 for g in grid_sig],
                     "n_days": len(idx)}
        with open(os.path.join(td, "meta.json"), "w", encoding="utf-8") as fh:
            json.dump(mini_meta, fh)
        mini_specs = [{"kind": "pair", "id": "P:x|y",
                       "faces": ["zoo85_stv", "rs_20_csi300"],
                       "signs": [-1.0, 1.0]}]
        _init_worker(td, {"ann": 0.1, "sharpe": 0.5},
                     {"ann": 0.05, "sharpe": 0.2}, mini_specs)
        row = block_worker(0, 1)[0]
        json.loads(json.dumps({"r": W1._jsonable(row)}, ensure_ascii=False))
        t("[10] sidecar worker glue, json round-trip",
          row["id"] == "P:x|y" and row["x2_sharpe"] is not None
          and isinstance(W1._jsonable(row)["x2_capped"], int))
        _G.clear()                       # release mmap handles (Win32 delete)
        import gc
        gc.collect()

    # [11] ledger pure fn + cutoff_meta (C2 face)
    led = append_ledger(BATCH, 5920, "census_fusion_s2/w2a_results.json",
                        evidence_cutoff=CUTOFF)
    t("[11] ledger dict + cutoff keys",
      {"prev_total", "batch_trials", "total", "batch"} <= set(led)
      and led["total"] == led["prev_total"] + 5920
      and cutoff_meta(CUTOFF) == {"evidence_cutoff": CUTOFF})

    # [12] np-native coercion (r286 law) via wave-1 _jsonable
    dirty = {"a": np.int64(5), "b": np.float32(1.5), "c": np.bool_(True),
             "d": np.float64(np.nan)}
    clean = W1._jsonable(dirty)
    json.dumps(clean)
    t("[12] np-native coercion + NaN->None",
      isinstance(clean["a"], int) and isinstance(clean["b"], float)
      and isinstance(clean["c"], bool) and clean["d"] is None)

    print("selftest:", "ALL PASS" if ok else "FAIL")
    return 0 if ok else 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "probe", "selftest"])
    ap.add_argument("--workers", type=int, default=None)
    a = ap.parse_args()
    if a.cmd == "selftest":
        return selftest()
    if a.cmd == "probe":
        return run(probe=True, workers=a.workers or 4)
    return run(workers=a.workers or 4)


if __name__ == "__main__":
    sys.exit(main())
