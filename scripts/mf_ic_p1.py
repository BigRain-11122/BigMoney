"""MF_IC_P1 — EM main-force moneyflow panel first factor-reference IC batch.

Prereg (frozen): research/shortline/MF_IC_P1.md — T-2026-09-25-46 (bm-b).
Claim lock commit 2c0958bd precedes the prereg freeze commit (THS_AGG_P1
two-commit pattern); NO batch-product-touching command before the freeze
(R99 law). Reuses pa_lhb_ic helpers verbatim (rank_rows / ic_from_ranks /
fwd_ret) and composite_ic.stats_block + science_gates ledger/cutoff — no
re-implementation (anti-duplication rule).

Zero engine runs: factor-reference batch; IC counts go to the factor ledger
via science_gates.append_ledger; the engine trials ledger N is untouched.

Subcommands:
  run      — gated on panel completeness (prereg S2 completeness gate);
             gate unmet -> honest exit 2 with status echo, nothing computed.
  selftest — hermetic synthetic-panel offline self-check (tmp sandbox, zero
             real-data dependency; r116 hermetic law).

Run gate (prereg S2, frozen): panel.complete=true AND n_symbols>=5,000 AND
eligible signal days>=150 (superset of IS>=100 / OOS>=30 at the 2/3 split).
Current live face (2026-09-25): panel source-blocked 53/5222 (bm-a T-39 lane,
30-min self-heal in flight) -> batch legally waits.
"""

import glob
import json
import os
import sys
import tempfile
import time

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from pa_lhb_ic import rank_rows, ic_from_ranks, fwd_ret  # noqa: E402
from composite_ic import stats_block  # noqa: E402
from science_gates import cutoff_meta, append_ledger  # noqa: E402

PER_DIR = os.path.join(ROOT, "data", "moneyflow", "per")
BARS_DIR = os.path.join(ROOT, "Money02", "data", "bars")
THS_DIR = os.path.join(ROOT, "data", "ths_ggzjl", "daily")
LHB_PATH = os.path.join(ROOT, "Money02", "data", "lhb", "lhb_detail.parquet")
STATUS_PATH = os.path.join(ROOT, "results", "moneyflow_update_status.json")
OUT_JSON = os.path.join(ROOT, "results", "shortline", "mf_ic_p1.json")
OUT_CSV = os.path.join(ROOT, "research", "shortline", "mf_ic_p1_results.csv")

# ---- frozen constants (prereg S3/S4; criteria zero-change law J18) ----
COL_MAIN = "主力净流入-净占比"
COL_XL = "超大单净流入-净占比"
FACTOR_SPECS = [  # (name, panel column, window) — prereg S3 table verbatim
    ("mf_main_net_pct_5", COL_MAIN, 5),
    ("mf_main_net_pct_10", COL_MAIN, 10),
    ("mf_main_net_pct_20", COL_MAIN, 20),
    ("mf_xl_net_pct_10", COL_XL, 10),
    ("mf_xl_net_pct_20", COL_XL, 20),
]
H_GATE = 10
H_REPORT = [5, 20]
N_NULLS = 50
SEED0 = 58_500                      # SEED_REGISTRY["mf_ic_p1"]
V1_FLOOR = 0.02
V2_IR = 0.30
V3_RETAIN = 0.5
MIN_PERIODS_IS = 100
MIN_PERIODS_OOS = 30
WIDTH_GATE = 1000                    # eligible-day cross-section floor (S2)
MIN_ELIG = 150                       # run-gate eligible-days floor (S2)
MIN_SYMBOLS = 5000                   # run-gate panel breadth floor (S2)
D6_MAX_CORR = 0.7
D6_MIN_DAYS = 30

PROD = dict(width_gate=WIDTH_GATE, min_elig=MIN_ELIG, min_symbols=MIN_SYMBOLS,
            min_is=MIN_PERIODS_IS, min_oos=MIN_PERIODS_OOS)


def shift1(a, fill=np.nan):
    out = np.full_like(a, fill)
    out[1:] = a[:-1]
    return out


def roll_mean(a, w):
    """Trailing w-row mean, strict min_periods=w (NaN until warm; a gap day
    inside the window invalidates it — calendar-grid semantics, prereg S3)."""
    return pd.DataFrame(a).rolling(w, min_periods=w).mean().values


def cal_index(cal):
    """int64 us epoch array -> proper DatetimeIndex (raw-int64 DatetimeIndex
    would be read as ns epoch = wrong dates; pc_l2 cast law)."""
    return pd.DatetimeIndex(np.asarray(cal).astype("datetime64[us]"))


def load_status(status_path=STATUS_PATH):
    try:
        with open(status_path, encoding="utf-8-sig") as f:  # r131 BOM law
            return json.load(f).get("panel", {})
    except FileNotFoundError:
        return {}


def panel_gate(panel_status, n_syms, n_elig, cfg):
    """Prereg S2 completeness gate. Pure — selftest exercises it directly."""
    reasons = []
    if not panel_status.get("complete"):
        reasons.append(f"panel.complete={panel_status.get('complete')}")
    if n_syms < cfg["min_symbols"]:
        reasons.append(f"n_symbols={n_syms}<{cfg['min_symbols']}")
    if n_elig < cfg["min_elig"]:
        reasons.append(f"eligible_days={n_elig}<{cfg['min_elig']}")
    return (not reasons), reasons


def load_panel(per_dir, cal):
    """Per-symbol panel CSVs -> (codes, grids{col: (T,N) aligned to cal},
    dropped panel rows off the bars calendar counted honestly)."""
    cal_ts = cal_index(cal)
    frames = {}
    dropped = 0
    for fp in sorted(glob.glob(os.path.join(per_dir, "*.csv"))):
        code = os.path.basename(fp)[:-4]
        df = pd.read_csv(fp, dtype={"date": str})
        df["date"] = pd.to_datetime(df["date"])
        df = (df.drop_duplicates("date", keep="last")
                .set_index("date").sort_index())
        off = ~df.index.isin(cal_ts)
        dropped += int(off.sum())
        frames[code] = df[~off]
    codes = sorted(frames)
    grids = {c: np.full((len(cal_ts), len(codes)), np.nan)
             for c in (COL_MAIN, COL_XL)}
    pos = {d: i for i, d in enumerate(cal_ts)}
    for j, code in enumerate(codes):
        df = frames[code]
        idx = np.array([pos[d] for d in df.index], dtype=int)
        for c in (COL_MAIN, COL_XL):
            grids[c][idx, j] = pd.to_numeric(df[c], errors="coerce").values
    return codes, grids, dropped


def load_bars_close(bars_dir, codes, cal):
    """Money02 bars -> close grid (T,N) on cal, P-1c S2.1 caliber (bars are
    already forward-adjusted). Codes without a bars file counted honestly."""
    cal_ts = cal_index(cal)
    close = np.full((len(cal_ts), len(codes)), np.nan)
    missing = 0
    col_of = {c: j for j, c in enumerate(codes)}
    for code in codes:
        fp = os.path.join(bars_dir, f"{code}.parquet")
        if not os.path.exists(fp):
            missing += 1
            continue
        df = pd.read_parquet(fp, columns=["date", "close"])
        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date").sort_index()
        idx = df.index.get_indexer(cal_ts)  # exact match, -1 elsewhere
        take = idx >= 0
        vals = df["close"].values
        close[take, col_of[code]] = vals[idx[take]]
    return close, missing


def eligible_days(close, fwd, width_gate):
    """Prereg S2/S3 mask: A = close&fwd valid AND the day's cross-section is
    >= width_gate names (53-symbol legacy narrow phase excluded, count
    disclosed). Factor-independent by design. Returns (A_eff, elig_rows)."""
    A = np.isfinite(close) & np.isfinite(fwd)
    nA = A.sum(axis=1)
    ok_rows = nA >= width_gate
    A_eff = A & ok_rows[:, None]
    return A_eff, np.where(ok_rows)[0]


def verdict_from_blocks(blk_is, blk_oos, v1_thr, cfg):
    """V1/V2/V3 + period gates from stats blocks (prereg S4 verbatim).
    Pure — selftest exercises designed cases directly."""
    rec = {"v1": False, "v2": False, "v3": False, "period_gate": False,
           "pass": False}
    if "ic_mean" not in blk_is or "ic_mean" not in blk_oos:
        return rec
    rec["v1"] = abs(blk_is["ic_mean"]) > v1_thr
    rec["v2"] = abs(blk_is["ic_ir"]) >= V2_IR
    rec["v3"] = ((blk_oos["ic_mean"] > 0) == (blk_is["ic_mean"] > 0)
                 and abs(blk_oos["ic_mean"]) >= V3_RETAIN * abs(blk_is["ic_mean"]))
    rec["period_gate"] = (blk_is.get("n_periods", 0) >= cfg["min_is"]
                          and blk_oos.get("n_periods", 0) >= cfg["min_oos"])
    rec["pass"] = bool(rec["v1"] and rec["v2"] and rec["v3"]
                       and rec["period_gate"])
    return rec


def null_threshold(A, R_fwd, cal, is_dates, n_nulls=N_NULLS, seed0=SEED0):
    """K same-mask white-noise nulls -> (v1_thr, p95|ir|, n) on IS segment
    (prereg S3). Deterministic by seed; selftest re-runs for identity."""
    abs_ic, abs_ir = [], []
    for k in range(n_nulls):
        rng = np.random.default_rng(seed0 + k)
        noise = rng.standard_normal((len(cal), A.shape[1]))
        s = ic_from_ranks(rank_rows(A, noise), R_fwd, cal)
        blk = stats_block(s[s.index.isin(is_dates)])
        if "ic_mean" in blk:
            abs_ic.append(abs(blk["ic_mean"]))
            abs_ir.append(abs(blk["ic_ir"]))
    if not abs_ic:
        return None, None, 0
    return (max(V1_FLOOR, round(float(np.quantile(abs_ic, 0.95)), 4)),
            round(float(np.quantile(abs_ir, 0.95)), 4), len(abs_ic))


def d6_lhb_grid(cal, codes, lhb_path):
    """lhb_count_20 on this universe — pc_l2_ic.py D6 leg verbatim (P-A
    dedup law, W=20, shift1(count, 0.0)). None on load failure (honest
    degradation, never silent pass)."""
    T = len(cal)
    try:
        lhb = pd.read_parquet(lhb_path)
    except Exception:
        return None
    lhb = lhb.sort_values(["龙虎榜成交额", "序号"], ascending=[True, False])
    ev = lhb.drop_duplicates(subset=["代码", "上榜日"], keep="last")
    ev_us = (pd.to_datetime(ev["上榜日"]).values.astype("datetime64[us]")
             .astype("int64"))
    pos = np.searchsorted(cal, ev_us)
    in_win = pos < T
    col_of = {c: j for j, c in enumerate(codes)}
    cc = ev["代码"].map(col_of)
    both = in_win & cc.notna().values
    r_idx, c_idx = pos[both], cc.values[both].astype(int)
    ind = np.zeros((T, len(codes)))
    ind[r_idx, c_idx] = 1.0
    cs = np.vstack([np.zeros((1, ind.shape[1])), np.cumsum(ind, axis=0)])
    cnt = np.empty_like(ind)
    cnt[:19] = cs[1:20]
    cnt[19:] = cs[20:] - cs[:-20]
    return shift1(cnt, 0.0)


def _parse_wan_yi(s):
    """THS value parser: 万/亿 suffix strings -> yuan float (THS_AGG_P1 S6
    keeps raw strings; parsing belongs to the consumer side, this leg)."""
    if s is None or (isinstance(s, float) and np.isnan(s)):
        return np.nan
    t = str(s).strip()
    if t in ("", "-", "—", "None"):
        return np.nan
    try:
        if t.endswith("亿"):
            return float(t[:-1]) * 1e8
        if t.endswith("万"):
            return float(t[:-1]) * 1e4
        return float(t)
    except ValueError:
        return np.nan


def d6_ths_grids(cal, codes, ths_dir):
    """ths_net_ratio / ths_net_ratio_ma5 grids from the THS aggregate panel
    (THS_AGG_P1 S3 definitions verbatim, read-only). None when the panel is
    absent on this machine (weak-check declaration path)."""
    fps = sorted(glob.glob(os.path.join(ths_dir, "*.csv")))
    if not fps:
        return None
    T, N = len(cal), len(codes)
    col_of = {c: j for j, c in enumerate(codes)}
    ratio = np.full((T, N), np.nan)
    cal_ts = cal_index(cal)
    for fp in fps:
        day = os.path.basename(fp)[:-4]
        t = pd.Timestamp(day)
        if t not in cal_ts:
            continue
        i = cal_ts.get_loc(t)
        try:
            df = pd.read_csv(fp, dtype=str)
        except Exception:
            continue
        for _, r in df.iterrows():
            j = col_of.get(str(r.get("股票代码", "")).strip().zfill(6))
            if j is None:
                continue
            amt = _parse_wan_yi(r.get("成交额(元)"))
            net = _parse_wan_yi(r.get("净额(元)"))
            if np.isfinite(amt) and amt > 0:
                ratio[i, j] = net / amt
    ma5 = pd.DataFrame(ratio).rolling(5, min_periods=5).mean().values
    return {"ths_net_ratio": ratio, "ths_net_ratio_ma5": ma5}


def d6_corr_days(vals, other, eff):
    """Per-day cross-section spearman corr, both valid, n>=5 pairs
    (PC_L2 S5 / prereg S1 verbatim)."""
    bothm = eff & np.isfinite(vals) & np.isfinite(other)
    nboth = bothm.sum(axis=1)
    corrs = []
    for t in np.where(nboth >= 5)[0]:
        with np.errstate(invalid="ignore"):
            sl = pd.Series(vals[t, bothm[t]]).corr(
                pd.Series(other[t, bothm[t]]), method="spearman")
        if np.isfinite(sl):
            corrs.append(float(sl))
    return corrs


def d6_verdict(corrs):
    n = len(corrs)
    mx = round(float(np.max(np.abs(corrs))), 4) if corrs else ""
    if n < D6_MIN_DAYS:
        return mx, n, "weak_check_insufficient_coverage"
    return mx, n, ("reject" if mx >= D6_MAX_CORR else "ok")


def evaluate(cal, codes, grids, close, panel_status, cfg, out_json, out_csv,
             ledger=True, lhb_path=LHB_PATH, ths_dir=THS_DIR):
    """Full gated evaluation. Returns exit code (0 ok / 2 gate unmet).
    D6 material paths are parameters so the selftest stays hermetic."""
    t0 = time.time()
    fwd10 = fwd_ret(close, H_GATE)
    A, elig = eligible_days(close, fwd10, cfg["width_gate"])
    n_elig = len(elig)
    n_syms = int(panel_status.get("n_symbols") or len(codes))
    ok, reasons = panel_gate(panel_status, n_syms, n_elig, cfg)
    print(f"gate: complete={panel_status.get('complete')} n_symbols={n_syms} "
          f"eligible_days={n_elig} -> "
          f"{'PASS' if ok else 'FAIL: ' + '; '.join(reasons)}", flush=True)
    if not ok:
        return 2
    cal_ts = cal_index(cal)
    is_dates = cal_ts[elig[: n_elig * 2 // 3]]
    oos_dates = cal_ts[elig[n_elig * 2 // 3:]]
    panel_cutoff = str(cal_ts.max().date())

    # ---- factors on the calendar grid, then shift1 (T+1 strict lag, S3)
    fac = {name: shift1(roll_mean(grids[col], w))
           for name, col, w in FACTOR_SPECS}

    # ---- nulls: K=50 same-mask white noise, IS-segment stats (S3)
    R_fwd = rank_rows(A, fwd10)
    v1_thr, null_p95_ir, n_null_ok = null_threshold(A, R_fwd, cal, is_dates)
    if v1_thr is None:
        print("run: null calibration empty (no IS-segment null IC) -> "
              "honest exit 2", flush=True)
        return 2
    print(f"null: p95|ic|={v1_thr} p95|ir|={null_p95_ir} n={n_null_ok} "
          f"split IS={len(is_dates)} OOS={len(oos_dates)}", flush=True)

    # ---- D6 reference grids (material-presence honest degradation)
    d6_refs = {}
    lhb_grid = d6_lhb_grid(cal, codes, lhb_path)
    if lhb_grid is None:
        print("d6: lhb face not loadable on this machine -> weak-check "
              "declared", flush=True)
    else:
        d6_refs["lhb_count_20"] = lhb_grid
    ths = d6_ths_grids(cal, codes, ths_dir)
    if ths:
        d6_refs.update(ths)
    else:
        print("d6: ths aggregate panel absent on this machine -> "
              "weak-check declared", flush=True)

    rows = []
    for name in fac:
        vals = fac[name]
        eff = A & np.isfinite(vals)
        s = ic_from_ranks(rank_rows(eff, vals), rank_rows(eff, fwd10), cal)
        s_is = s[s.index.isin(is_dates)]
        s_oos = s[s.index.isin(oos_dates)]
        blk_is, blk_oos = stats_block(s_is), stats_block(s_oos)
        rec = {"factor": name, "is_n_periods": blk_is.get("n_periods", 0),
               "oos_n_periods": blk_oos.get("n_periods", 0)}
        for seg, blk in (("is", blk_is), ("oos", blk_oos)):
            for k in ("ic_mean", "ic_ir", "n_periods"):
                rec[f"h{H_GATE}_{seg}_{k}"] = blk.get(k, "")
        rec.update(verdict_from_blocks(blk_is, blk_oos, v1_thr, cfg))
        ic5 = (np.nanpercentile(s.values, [0, 25, 50, 75, 100])
               if len(s) else [])
        rec["ic_five_num"] = [round(float(x), 4) for x in ic5]
        if rec["pass"]:  # report horizons for passers only (S4)
            for h in H_REPORT:
                fw = fwd_ret(close, h)
                eff_h = A & np.isfinite(vals) & np.isfinite(fw)
                sh_ = ic_from_ranks(rank_rows(eff_h, vals),
                                    rank_rows(eff_h, fw), cal)
                rec[f"h{h}_is_ic"] = stats_block(
                    sh_[sh_.index.isin(is_dates)]).get("ic_mean", "")
                rec[f"h{h}_oos_ic"] = stats_block(
                    sh_[sh_.index.isin(oos_dates)]).get("ic_mean", "")
        pair_verdicts = []
        for ref_name, ref_grid in d6_refs.items():
            mx, n, v = d6_verdict(d6_corr_days(vals, ref_grid, eff))
            rec[f"d6_{ref_name}"] = {"max_abs_corr": mx, "days": n,
                                     "verdict": v}
            pair_verdicts.append(v)
        if not d6_refs:
            rec["d6_all_pairs"] = "weak_check_no_material_on_machine"
            rec["d6_verdict"] = "weak_check_insufficient_coverage"
        elif "reject" in pair_verdicts:
            rec["d6_verdict"] = "reject"
        elif "ok" in pair_verdicts:
            rec["d6_verdict"] = "ok"
        else:
            rec["d6_verdict"] = "weak_check_insufficient_coverage"
        rows.append(rec)
        print(f"  {name}: IS ic={rec[f'h{H_GATE}_is_ic_mean']} "
              f"IR={rec[f'h{H_GATE}_is_ic_ir']} pass={rec['pass']} "
              f"d6={rec['d6_verdict']} ({time.time()-t0:.0f}s)", flush=True)

    out = {
        "batch": "mf_ic_p1",
        "lane": "bm-b T-2026-09-25-46, bandit event-attention candidate "
                "(MSG-20260925-0810)",
        **cutoff_meta(panel_cutoff),
        "window": {"n_days": len(cal), "start": str(cal_ts[0].date()),
                   "end": str(cal_ts[-1].date()),
                   "is_oos_split": "positional 2/3 of eligible days "
                                   "(prereg S2, THS trigger-frozen pattern)",
                   "is_end_date": str(is_dates[-1].date()),
                   "regime_note": "window inside the 2026 regime; IS/OOS is "
                                  "a sub-split, NOT regime OOS (120d source-"
                                  "window disclosure clause applies)"},
        "universe": {"n_panel_codes": len(codes), "n_eligible_days": n_elig,
                     "width_gate": cfg["width_gate"],
                     "median_cross_section": int(np.median(
                         A.sum(axis=1)[elig]))},
        "gates": {"h_gate": H_GATE, "v1_thr": v1_thr, "v1_floor": V1_FLOOR,
                  "null_p95_abs_ir": null_p95_ir, "v2_ir_min": V2_IR,
                  "v3_retain_min": V3_RETAIN, "min_periods_is": cfg["min_is"],
                  "min_periods_oos": cfg["min_oos"], "null_n": N_NULLS,
                  "seed_base": SEED0},
        "rows": rows,
        "ledger_note": "factor-reference batch: append_ledger(batch_trials="
                       f"{len(FACTOR_SPECS)}) at run time; IC counts "
                       f"{len(FACTOR_SPECS)}+{N_NULLS} in factor audit; "
                       "engine trials ledger N untouched",
        "prereg": "research/shortline/MF_IC_P1.md (freeze commit precedes "
                  "run, R99 law)",
        "runtime_s": round(time.time() - t0, 1),
    }
    if ledger:
        led = append_ledger(batch_name="mf_ic_p1",
                            batch_trials=len(FACTOR_SPECS),
                            file_name=os.path.relpath(out_json, ROOT),
                            evidence_cutoff=panel_cutoff)
        out["trials_ledger"] = led
    os.makedirs(os.path.dirname(out_json), exist_ok=True)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    pd.DataFrame(rows).to_csv(out_csv, index=False)
    print(f"written {out_json} + {out_csv} ({time.time()-t0:.0f}s)", flush=True)
    return 0


def _toy(tmp, n_days=90, n_codes=12, narrow_days=10, status_complete=True):
    """Hermetic synthetic fixture: panel CSVs + bars parquets + status json
    in a tmp sandbox. Values built at construction time (pandas-3 CoW law:
    no chained assignment). Stocks 3..11 start at day `narrow_days` in BOTH
    the panel and bars faces -> the width gate excludes the narrow head."""
    cal = pd.bdate_range("2026-01-05", periods=n_days)
    per = os.path.join(tmp, "per")
    bars = os.path.join(tmp, "bars")
    os.makedirs(per)
    os.makedirs(bars)
    codes = [f"{600000 + i:06d}" for i in range(n_codes)]
    rng = np.random.default_rng(7)
    base = rng.uniform(-5, 5, n_codes)  # per-stock constant flow pct
    for i, code in enumerate(codes):
        main = np.full(n_days, base[i])
        main[40] = base[i] + 20.0  # designed single-day spike (lag fixture)
        if i >= 3:
            main[:narrow_days] = np.nan
        xl = main * 0.6
        pd.DataFrame({"date": [str(d.date()) for d in cal], COL_MAIN: main,
                      COL_XL: xl}).to_csv(os.path.join(per, f"{code}.csv"),
                                          index=False)
        close = 100.0 + np.cumsum(rng.standard_normal(n_days) * 0.01)
        if i >= 3:
            dcal, cvals = cal[narrow_days:], close[narrow_days:]
        else:
            dcal, cvals = cal, close
        pd.DataFrame({"date": dcal, "close": cvals}).to_parquet(
            os.path.join(bars, f"{code}.parquet"), index=False)
    status = {"panel": {"complete": status_complete, "n_symbols": n_codes}}
    sp = os.path.join(tmp, "status.json")
    with open(sp, "w", encoding="utf-8") as f:
        json.dump(status, f)
    return per, bars, sp, cal, codes


def selftest():
    """Hermetic offline checks: warmup/strict-window semantics / shift1 lag /
    width gate / positional split / V-gate arithmetic / run-gate exit 2 /
    full pipeline with D6 weak-check path / null determinism."""
    with tempfile.TemporaryDirectory() as tmp:
        per, bars, sp, cal, _ = _toy(tmp, status_complete=False)
        cal_us = cal.values.astype("datetime64[us]").astype("int64")
        panel_status = load_status(sp)
        assert panel_status["complete"] is False
        codes, grids, dropped = load_panel(per, cal_us)
        assert len(codes) == 12 and dropped == 0
        close, missing = load_bars_close(bars, codes, cal_us)
        assert missing == 0
        assert np.isfinite(close[:10, :3]).all()      # narrow-head stocks
        assert np.isfinite(close[10:, :]).all()
        # (a) strict-window warmup: 5d rolling mean valid only from row 4
        f5 = roll_mean(grids[COL_MAIN], 5)
        assert np.isnan(f5[:4, 0]).all() and np.isfinite(f5[4:, 0]).all()
        # (b) shift1 lag: panel value at day 40 lands at signal position 41
        g = shift1(grids[COL_MAIN])
        assert g[41, 0] == grids[COL_MAIN][40, 0] and np.isnan(g[0, 0])
        # (c) width gate: first 10 days only 3 stocks -> excluded
        fwd10 = fwd_ret(close, 10)
        A, elig = eligible_days(close, fwd10, width_gate=5)
        assert elig[0] == 10 and A[:10].sum() == 0 and A.sum(axis=1)[10] == 12
        # (d) positional 2/3 split boundary is well-formed (IS>=30 so the
        # toy null calibration clears stats_block's own 30-period floor)
        n = len(elig)
        assert n == 70 and n * 2 // 3 == 46
        # (e) V-gate arithmetic on designed blocks (pure function)
        blk = {"ic_mean": 0.05, "ic_ir": 0.4, "n_periods": 120}
        blk_oos = {"ic_mean": 0.03, "ic_ir": 0.3, "n_periods": 40}
        assert verdict_from_blocks(blk, blk_oos, 0.02, PROD)["pass"]
        r2 = verdict_from_blocks(blk, {**blk_oos, "ic_mean": -0.03}, 0.02,
                                 PROD)
        assert not r2["v3"] and not r2["pass"]
        r3 = verdict_from_blocks({**blk, "n_periods": 99}, blk_oos, 0.02,
                                 PROD)
        assert not r3["period_gate"] and not r3["pass"]
        # (f) run gate honest exit 2, nothing computed (incomplete panel)
        rc = evaluate(cal_us, codes, grids, close, panel_status,
                      dict(PROD, min_symbols=10, min_elig=5, width_gate=5),
                      out_json=os.path.join(tmp, "o.json"),
                      out_csv=os.path.join(tmp, "o.csv"), ledger=False,
                      lhb_path=os.path.join(tmp, "absent.parquet"),
                      ths_dir=os.path.join(tmp, "no_ths"))
        assert rc == 2 and not os.path.exists(os.path.join(tmp, "o.json"))
        # (g) full pipeline pass with toy gates + hermetic-absent D6 ->
        #     weak-check declared on every factor, no crash, C2 key present
        tmp2 = os.path.join(tmp, "ok")
        per2, bars2, sp2, _, _ = _toy(tmp2, status_complete=True)
        pc2, grids2, _ = load_panel(per2, cal_us)
        close2, _ = load_bars_close(bars2, pc2, cal_us)
        rc2 = evaluate(cal_us, pc2, grids2, close2, load_status(sp2),
                       dict(PROD, min_symbols=10, min_elig=5, width_gate=5,
                            min_is=5, min_oos=2),
                       out_json=os.path.join(tmp, "o2.json"),
                       out_csv=os.path.join(tmp, "o2.csv"), ledger=False,
                       lhb_path=os.path.join(tmp, "absent.parquet"),
                       ths_dir=os.path.join(tmp, "no_ths"))
        assert rc2 == 0
        with open(os.path.join(tmp, "o2.json"), encoding="utf-8") as f:
            out2 = json.load(f)
        assert "evidence_cutoff" in out2
        assert len(out2["rows"]) == len(FACTOR_SPECS)
        for row in out2["rows"]:
            assert row["d6_verdict"] == "weak_check_insufficient_coverage"
            assert row["d6_all_pairs"] == "weak_check_no_material_on_machine"
        # (h) null determinism: same seeds -> identical threshold (twice)
        A2, elig2 = eligible_days(close2, fwd_ret(close2, 10), width_gate=5)
        cal_ts = cal_index(cal_us)
        isd = cal_ts[elig2[: len(elig2) * 2 // 3]]
        R_fwd2 = rank_rows(A2, fwd_ret(close2, 10))
        t1 = null_threshold(A2, R_fwd2, cal_us, isd, n_nulls=8)
        t2 = null_threshold(A2, R_fwd2, cal_us, isd, n_nulls=8)
        assert t1 == t2 and t1[0] >= V1_FLOOR and t1[2] == 8
    print("selftest: 8/8 PASS")
    return 0


def main():
    assert len(sys.argv) >= 2 and sys.argv[1] in ("run", "selftest"), \
        "usage: mf_ic_p1.py run|selftest"
    if sys.argv[1] == "selftest":
        return selftest()
    panel_status = load_status()
    if not panel_status:
        print("run: moneyflow panel status absent on this machine "
              "(collector lane bm-a) -> honest exit 2", flush=True)
        return 2
    panel_dates = set()
    for fp in sorted(glob.glob(os.path.join(PER_DIR, "*.csv")))[:20000]:
        with open(fp, encoding="utf-8-sig") as f:
            f.readline()
            for line in f:
                panel_dates.add(line.split(",", 1)[0])
    if not panel_dates:
        print("run: moneyflow panel empty on this machine -> honest exit 2",
              flush=True)
        return 2
    dmin = pd.Timestamp(min(panel_dates)) - pd.Timedelta(days=10)
    dmax = pd.Timestamp(max(panel_dates)) + pd.Timedelta(days=30)
    cal = set()
    for fp in sorted(glob.glob(os.path.join(BARS_DIR, "*.parquet"))):
        d = pd.to_datetime(pd.read_parquet(fp, columns=["date"])["date"])
        cal |= set(d[(d >= dmin) & (d <= dmax)])
    cal_us = np.array(sorted(cal)).astype("datetime64[us]").astype("int64")
    codes, grids, dropped = load_panel(PER_DIR, cal_us)
    print(f"panel: {len(codes)} codes, {len(cal_us)} calendar days, "
          f"{dropped} panel rows off-calendar dropped", flush=True)
    close, missing = load_bars_close(BARS_DIR, codes, cal_us)
    print(f"bars: {missing} panel codes without bars file", flush=True)
    return evaluate(cal_us, codes, grids, close, panel_status, PROD,
                    OUT_JSON, OUT_CSV, ledger=True)


if __name__ == "__main__":
    sys.exit(main())
