"""SINA_CONSTRUCT_P1 — sina 四档资金流因子族 IC 普查批 (factor-reference batch).

Prereg (frozen): research/SINA_CONSTRUCT_P1.md — sibling family of
scripts/mf_ic_p1.py (T-2026-09-25-46 lineage): §2 run gates and §4 V1/V2/V3
family constants are the MF_IC_P1 同门移植 face (A1 修正案 lineage).
Lane adjudication MSG-20260927-1615 (bm-a): option (a) data-host local census
burn on bm-a — the panel lives bm-a-local data/sina_mf/ (gitignored); this
script is the frozen science face shared in-repo (authored bm-b, R99 freeze
commit precedes any panel-touching run).

Helpers reused verbatim — no re-implementation (anti-duplication rule):
pa_lhb_ic rank_rows / ic_from_ranks / fwd_ret + composite_ic.stats_block +
science_gates cutoff_meta / append_ledger / SEED_REGISTRY + mf_ic_p1
load_bars_close / load_panel (EM D6 leg) / roll_mean / shift1 / d6_lhb_grid /
d6_ths_grids / d6_corr_days / d6_verdict / verdict_from_blocks.

Zero engine runs: factor-reference IC census; counts go to the factor ledger
via science_gates.append_ledger; the engine trials ledger N is untouched.

Constructs (prereg §3, frozen): TIER_rX = rX_net / turnover (X=0..3);
MAIN = (r0_net + r1_net) / turnover (official r0+r1 aggregate, R225).
Lag law (prereg §3): sina lscjfb row = day-T close face -> signal day T,
forward returns strictly from T+1: fwd_h[T] = close[T+1+h]/close[T+1] - 1
(= pa_lhb_ic.fwd_ret shifted back one row); the factor itself is NOT lagged.

Subcommands:
  run      — gated (prereg §2): sina_mf_accept verdict PASS AND panel status
             complete AND n_symbols>=5,000 AND eligible signal days>=150;
             any gate unmet -> honest exit 2, nothing computed or written.
  selftest — hermetic synthetic-panel offline self-check (tmp sandbox, zero
             real-data dependency; r116 hermetic law; R99-sanctioned
             pre-freeze escape, T-46 precedent).
"""

import glob
import json
import os
import socket
import sys
import tempfile
import time

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from pa_lhb_ic import rank_rows, ic_from_ranks, fwd_ret  # noqa: E402
from composite_ic import stats_block  # noqa: E402
from science_gates import cutoff_meta, append_ledger, SEED_REGISTRY  # noqa: E402
from mf_ic_p1 import (  # noqa: E402
    load_bars_close, load_panel as load_em_panel, roll_mean, shift1,
    d6_lhb_grid, d6_ths_grids, d6_corr_days, d6_verdict,
    verdict_from_blocks, FACTOR_SPECS as EM_FACTOR_SPECS,
    COL_MAIN as EM_COL_MAIN, COL_XL as EM_COL_XL, D6_MAX_CORR, D6_MIN_DAYS)

SINA_PER = os.path.join(ROOT, "data", "sina_mf", "per")
BARS_DIR = os.path.join(ROOT, "Money02", "data", "bars")
THS_DIR = os.path.join(ROOT, "data", "ths_ggzjl", "daily")
LHB_PATH = os.path.join(ROOT, "Money02", "data", "lhb", "lhb_detail.parquet")
EM_PER_DIR = os.path.join(ROOT, "data", "moneyflow", "per")
ELIG_PATH = os.path.join(ROOT, "data", "fundamental", "eligibility.csv")
MASK_PATH = os.path.join(ROOT, "data", "fundamental", "b_layer_mask.csv")
ACCEPT_PATH = os.path.join(ROOT, "results", "sina_mf_accept.json")
STATUS_PATH = os.path.join(ROOT, "results", "sina_mf_update_status.json")
OUT_JSON = os.path.join(ROOT, "results", "shortline", "sina_construct_p1.json")
OUT_CSV = os.path.join(ROOT, "research", "shortline", "sina_construct_p1_results.csv")

# ---- frozen constants (prereg §2/§3/§4; criteria zero-change law) ----
TIER_NETS = ["r0_net", "r1_net", "r2_net", "r3_net"]   # frozen schema order
CONSTRUCTS = ["TIER_r0", "TIER_r1", "TIER_r2", "TIER_r3", "MAIN"]
H_GATE = 10
H_REPORT = [1, 5]                    # h10 gates; h1/h5 report-only decay face
N_NULLS = 100                        # prereg §3 K=100 same-mask permutation
SEED_KEY = "sina_construct_p1"       # SEED_REGISTRY key (no hand-copy, F11)
V1_FLOOR = 0.02
V2_IR = 0.30                         # verdict arithmetic owned by the shared
V3_RETAIN = 0.5                      # mf_ic_p1.verdict_from_blocks import;
                                     # duplicated here only for the JSON face
MIN_PERIODS_IS = 100                 # A1/MF family lineage (positional 2/3)
MIN_PERIODS_OOS = 30
MIN_ELIG = 150                       # run-gate eligible-signal-days floor (§2)
MIN_SYMBOLS = 5000                   # run-gate panel breadth floor (§2)
MIN_PANEL_ROWS = 50                  # per-symbol panel N>=50 rows (§2)
MIN_DAY_NAMES = 5                    # mechanical IC-helper floor (n>=5); NO
                                     # invented width gate — prereg §2 froze
                                     # none; coverage distribution disclosed
COLLAPSE_TOL = 1e-3                  # self-collapse law (SINA_MF_PREREG §1)
D6_MAX_CORR_REJECT = D6_MAX_CORR     # 0.7 admission, cross-family pairs only
INTRA_BATCH_NOTE = (
    "family_by_construction sleeve-tag (prereg §1 sleeve-tag precedent): "
    "intra-batch pairs are by-construction correlated family members "
    "(MAIN is the official r0+r1 aggregate of its own components, R225) — "
    "disclosure face, NOT an admission reject; cross-family D6 pairs "
    "(EM/ths/lhb) carry the >=0.7 admission verdicts. Correlation-source "
    "argument pre-declared: four-tier decomposition vs single-column "
    "aggregation = dimension dis-parity (R118) + official aggregate (R225).")

PROD = dict(min_elig=MIN_ELIG, min_symbols=MIN_SYMBOLS,
            min_is=MIN_PERIODS_IS, min_oos=MIN_PERIODS_OOS)


def cal_index(cal):
    """int64 us epoch array -> DatetimeIndex (pc_l2 cast law, mf mirror)."""
    return pd.DatetimeIndex(np.asarray(cal).astype("datetime64[us]"))


def load_status(status_path=STATUS_PATH):
    try:
        with open(status_path, encoding="utf-8-sig") as f:  # r131 BOM law
            return json.load(f).get("panel", {})
    except FileNotFoundError:
        return {}


def load_accept_verdict(accept_path=ACCEPT_PATH):
    """Prereg §2 completeness gate face: latest in-repo accept run verdict."""
    try:
        with open(accept_path, encoding="utf-8-sig") as f:
            d = json.load(f)
        return d.get("verdict"), d.get("ts"), d.get("latent_repull_defect_note")
    except FileNotFoundError:
        return None, None, None


def load_universe_filters(elig_path=ELIG_PATH, mask_path=MASK_PATH):
    """Prereg §2 universe faces: eligibility snapshot + B-layer static mask.
    6-digit code sets; absent file -> None (caller gates honestly)."""
    def _codes(path, col, flag_col):
        if not os.path.exists(path):
            return None
        df = pd.read_csv(path, dtype=str)
        keep = df[df[flag_col].str.strip() == "True"]
        return set(keep[col].str.strip())
    return _codes(elig_path, "code", "eligible"), _codes(mask_path, "code",
                                                          "ok_static")


def panel_gate(panel_status, accept_verdict, n_syms, n_elig, cfg):
    """Prereg §2 completeness gate (accept PASS + status + breadth + days).
    Pure — selftest exercises it directly."""
    reasons = []
    if accept_verdict != "PASS":
        reasons.append(f"sina_mf_accept.verdict={accept_verdict}")
    if not panel_status.get("complete"):
        reasons.append(f"panel.complete={panel_status.get('complete')}")
    if n_syms < cfg["min_symbols"]:
        reasons.append(f"n_symbols={n_syms}<{cfg['min_symbols']}")
    if n_elig < cfg["min_elig"]:
        reasons.append(f"eligible_days={n_elig}<{cfg['min_elig']}")
    return (not reasons), reasons


def load_sina_panel(per_dir, cal, elig_set, mask_set, min_rows=MIN_PANEL_ROWS):
    """Per-symbol panel CSVs -> (codes, grids, counts). Frozen schema read by
    header name (opendate + 13 raw-ASCII value cols); per-row self-collapse
    law |netamount - sum(r0_net..r3_net)| > COLLAPSE_TOL -> rejected +
    counted; netamount present with any missing tier -> conservative
    unverifiable rejection (collector booking law mirrored). Universe law
    (prereg §2): eligibility ∩ b_layer_mask ∩ per-symbol N>=50 on-calendar
    rows; every exclusion bucket counted honestly."""
    cal_ts = cal_index(cal)
    pos = {d: i for i, d in enumerate(cal_ts)}
    T = len(cal_ts)
    cols = ["netamount"] + TIER_NETS + ["turnover"]
    frames, counts = {}, dict(files=0, off_eligibility=0, off_mask=0,
                              short_history=0, schema_foreign=0, kept=0,
                              rows=0, rows_off_cal=0, collapse_rejected=0,
                              unverifiable_rows=0)
    for fp in sorted(glob.glob(os.path.join(per_dir, "*.csv"))):
        code = os.path.basename(fp)[:-4]
        counts["files"] += 1
        if elig_set is not None and code not in elig_set:
            counts["off_eligibility"] += 1
            continue
        if mask_set is not None and code not in mask_set:
            counts["off_mask"] += 1
            continue
        df = pd.read_csv(fp, dtype=str)
        if "opendate" not in df.columns:
            counts["schema_foreign"] += 1
            continue
        df["__d"] = pd.to_datetime(df["opendate"], errors="coerce")
        df = df.dropna(subset=["__d"])
        df = (df.drop_duplicates("__d", keep="last")
                .set_index("__d").sort_index())
        on = df.index.isin(cal_ts)
        counts["rows"] += len(df)
        counts["rows_off_cal"] += int((~on).sum())
        df = df[on]
        if len(df) < min_rows:
            counts["short_history"] += 1
            continue
        num = df[cols].apply(pd.to_numeric, errors="coerce")
        net = num["netamount"].values
        tiers = num[TIER_NETS].values
        ok_net = np.isfinite(net)
        tier_missing = (~np.isfinite(tiers)).any(axis=1)
        bad = ok_net & (np.abs(net - np.nansum(tiers, axis=1)) > COLLAPSE_TOL)
        unver = ok_net & tier_missing
        keep_row = ~(bad | unver)
        counts["collapse_rejected"] += int(bad.sum())
        counts["unverifiable_rows"] += int(unver.sum())
        frames[code] = num[keep_row]
        counts["kept"] += 1
    codes = sorted(frames)
    grids = {c: np.full((T, len(codes)), np.nan) for c in cols}
    for j, code in enumerate(codes):
        idx = np.array([pos[d] for d in frames[code].index], dtype=int)
        for c in cols:
            grids[c][idx, j] = frames[code][c].values
    return codes, grids, counts


def build_constructs(grids):
    """Prereg §3 frozen definitions (vectorized, turnover>0 guarded)."""
    tvr = grids["turnover"]
    safe = np.where(np.isfinite(tvr) & (tvr > 0), tvr, np.nan)
    fac = {f"TIER_r{k}": grids[t] / safe for k, t in enumerate(TIER_NETS)}
    fac["MAIN"] = (grids["r0_net"] + grids["r1_net"]) / safe
    return fac


def fwd_sina(close, h):
    """Prereg §3 lag law: signal day T = panel row T (day-T close face);
    forward returns strictly from T+1 — fwd_h[T] = close[T+1+h]/close[T+1]-1
    (raw helper shifted BACK one row, unlike the EM shift1-on-factor face)."""
    out = np.full_like(close, np.nan, dtype=float)
    raw = fwd_ret(close, h)
    out[:-1] = raw[1:]
    return out


def eligible_days(close, fwd, min_names=MIN_DAY_NAMES):
    """Factor-independent day mask: close&fwd valid AND the day's cross-section
    >= the IC helper's own n>=5 floor (no invented width gate; coverage
    distribution is disclosed per prereg §4(a))."""
    A = np.isfinite(close) & np.isfinite(fwd)
    ok_rows = A.sum(axis=1) >= min_names
    return A & ok_rows[:, None], np.where(ok_rows)[0]


def null_threshold_per_construct(F0, R_fwd, cal, is_dates, eff, elig_rows,
                                 n_nulls=N_NULLS, seed0=None):
    """K same-mask within-day factor-rank permutation nulls (prereg §3:
    因子日内随机置换·同 universe 同日历), stats on the IS segment; per-construct
    independent. Deterministic by registered seed base."""
    if seed0 is None:
        seed0 = SEED_REGISTRY[SEED_KEY]   # no hand-copy (F11 law)
    abs_ic, abs_ir = [], []
    for k in range(n_nulls):
        rng = np.random.default_rng(seed0 + k)
        Fk = F0.copy()
        for t in elig_rows:
            idx = np.flatnonzero(eff[t])
            if idx.size >= 5:
                Fk[t, idx] = rng.permutation(Fk[t, idx])
        s = ic_from_ranks(Fk, R_fwd, cal)
        blk = stats_block(s[s.index.isin(is_dates)])
        if "ic_mean" in blk:
            abs_ic.append(abs(blk["ic_mean"]))
            abs_ir.append(abs(blk["ic_ir"]))
    if not abs_ic:
        return None, None, 0
    return (max(V1_FLOOR, round(float(np.quantile(abs_ic, 0.95)), 4)),
            round(float(np.quantile(abs_ir, 0.95)), 4), len(abs_ic))


def extreme_day_face(s, A, elig, cal):
    """Prereg §4 hard-bounds 三件套 (a)/(b): median/p99.9 distribution bounds
    carry the main judging duty (no naive max as主判); per-day |IC| outliers
    listed separately (structural limit-tide days = exemption path, single-day
    disclosure preferred over batch rejection)."""
    if not len(s):
        return {"n_days": 0}
    a = s.abs()
    cov_all = A.sum(axis=1)
    cov = cov_all[elig]
    pos = {d: i for i, d in enumerate(cal_index(cal))}
    top = s.reindex(a.sort_values(ascending=False).index)[:5]
    return {
        "n_days": int(len(s)),
        "abs_ic_median": round(float(a.median()), 4),
        "abs_ic_p99_9": round(float(a.quantile(0.999)), 4),
        "abs_ic_max": round(float(a.max()), 4),
        "coverage_median": int(np.median(cov)),
        "coverage_min": int(cov.min()),
        "top_days": [{"date": str(d.date()), "ic": round(float(v), 4),
                      "n": int(cov_all[pos[d]])} for d, v in top.items()],
    }


def d6_em_grids(cal, codes, em_per_dir):
    """EM moneyflow panel constructs (MF_IC_P1 family specs) mapped onto the
    sina universe axis for overlap-day correlation. None when the EM panel is
    absent/empty on this machine (MSG-1105 dual-face death -> honest
    UNAVAILABLE/weak-check row)."""
    if not em_per_dir or not glob.glob(os.path.join(em_per_dir, "*.csv")):
        return None, 0
    em_codes, em_grids, _dropped = load_em_panel(em_per_dir, cal)
    if not em_codes:
        return None, 0
    T, N = len(cal), len(codes)
    col_of = {c: j for j, c in enumerate(codes)}
    mapped = {EM_COL_MAIN: np.full((T, N), np.nan),
              EM_COL_XL: np.full((T, N), np.nan)}
    kept = 0
    for i, c in enumerate(em_codes):
        j = col_of.get(c)
        if j is None:
            continue
        kept += 1
        for col in (EM_COL_MAIN, EM_COL_XL):
            mapped[col][:, j] = em_grids[col][:, i]
    if kept == 0:
        return None, 0
    out = {}
    for name, col, w in EM_FACTOR_SPECS:
        out[name] = shift1(roll_mean(mapped[col], w))
    return out, kept


def evaluate(cal, codes, grids, close, panel_status, accept_verdict, cfg,
             out_json, out_csv, ledger=True, lhb_path=LHB_PATH,
             ths_dir=THS_DIR, em_dir=EM_PER_DIR, seed0=None, counts=None,
             accept_ts=None, latent_note=None, machine=None):
    """Full gated evaluation. Returns exit code (0 ok / 2 gate unmet).
    D6 material paths are parameters so the selftest stays hermetic."""
    t0 = time.time()
    fwd10 = fwd_sina(close, H_GATE)
    A, elig = eligible_days(close, fwd10)
    n_elig = len(elig)
    n_syms = int(panel_status.get("n_symbols") or len(codes))
    ok, reasons = panel_gate(panel_status, accept_verdict, n_syms, n_elig, cfg)
    print(f"gate: accept={accept_verdict} complete={panel_status.get('complete')} "
          f"n_symbols={n_syms} eligible_days={n_elig} -> "
          f"{'PASS' if ok else 'FAIL: ' + '; '.join(reasons)}", flush=True)
    if not ok:
        return 2
    cal_ts = cal_index(cal)
    is_dates = cal_ts[elig[: n_elig * 2 // 3]]
    oos_dates = cal_ts[elig[n_elig * 2 // 3:]]
    panel_cutoff = str(panel_status.get("cutoff") or cal_ts.max().date())

    fac = build_constructs(grids)

    # ---- cross-family D6 reference grids (material-presence honest faces)
    d6_refs = {}
    lhb_grid = d6_lhb_grid(cal, codes, lhb_path)
    if lhb_grid is None:
        print("d6: lhb face not loadable on this machine -> weak-check declared",
              flush=True)
    else:
        d6_refs["lhb_count_20"] = lhb_grid
    ths = d6_ths_grids(cal, codes, ths_dir)
    if ths:
        d6_refs.update(ths)
    else:
        print("d6: ths aggregate panel absent on this machine -> weak-check "
              "declared", flush=True)
    em_grids, em_overlap = d6_em_grids(cal, codes, em_dir)
    if em_grids:
        d6_refs.update(em_grids)
        print(f"d6: em moneyflow panel mapped, overlap symbols={em_overlap}",
              flush=True)
    else:
        print("d6: em moneyflow panel absent on this machine -> UNAVAILABLE "
              "honest (MSG-1105 dual-face death)", flush=True)

    rows = []
    for name in CONSTRUCTS:
        vals = fac[name]
        eff = A & np.isfinite(vals)
        F0 = rank_rows(eff, vals)
        R_fwd = rank_rows(eff, fwd10)
        v1_thr, null_p95_ir, n_null_ok = null_threshold_per_construct(
            F0, R_fwd, cal, is_dates, eff, elig, seed0=seed0)
        if v1_thr is None:
            print(f"run: null calibration empty for {name} -> honest exit 2",
                  flush=True)
            return 2
        s = ic_from_ranks(F0, R_fwd, cal)
        s_is = s[s.index.isin(is_dates)]
        s_oos = s[s.index.isin(oos_dates)]
        blk_is, blk_oos = stats_block(s_is), stats_block(s_oos)
        rec = {"factor": name, "is_n_periods": blk_is.get("n_periods", 0),
               "oos_n_periods": blk_oos.get("n_periods", 0)}
        for seg, blk in (("is", blk_is), ("oos", blk_oos)):
            for k in ("ic_mean", "ic_ir", "n_periods"):
                rec[f"h{H_GATE}_{seg}_{k}"] = blk.get(k, "")
        rec.update(verdict_from_blocks(blk_is, blk_oos, v1_thr, cfg))
        rec["nulls"] = {"k": N_NULLS, "v1_thr": v1_thr,
                        "p95_abs_ir": null_p95_ir, "n_ok": n_null_ok,
                        "seed_base": SEED_REGISTRY[SEED_KEY],
                        "design": "within-day same-mask factor-rank permutation"}
        ic5 = (np.nanpercentile(s.values, [0, 25, 50, 75, 100])
               if len(s) else [])
        rec["ic_five_num"] = [round(float(x), 4) for x in ic5]
        rec["extreme_day_face"] = extreme_day_face(s, A, elig, cal)
        if rec["pass"]:  # report horizons for passers only (§4)
            for h in H_REPORT:
                fw = fwd_sina(close, h)
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
        rec["d6_em_overlap_symbols"] = em_overlap
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

    # ---- intra-batch pairwise disclosure (sleeve-tag face, §1)
    intra = []
    for i, a_ in enumerate(CONSTRUCTS):
        for b_ in CONSTRUCTS[i + 1:]:
            mx, n, _v = d6_verdict(d6_corr_days(fac[a_], fac[b_], A))
            intra.append({"pair": f"{a_}|{b_}", "max_abs_corr": mx, "days": n,
                          "tag": "family_by_construction"})
    for rec in rows:
        rec["intra_batch"] = [p for p in intra
                              if rec["factor"] in p["pair"].split("|")]

    out = {
        "batch": "sina_construct_p1",
        "lane": "bm-a data-host local census burn (MSG-20260927-1615 pick (a)); "
                "science script authored bm-b, prereg research/SINA_CONSTRUCT_P1.md",
        **cutoff_meta(panel_cutoff),
        "window": {"n_days": len(cal), "start": str(cal_ts[0].date()),
                   "end": str(cal_ts[-1].date()),
                   "is_oos_split": "positional 2/3 of eligible signal days "
                                   "(prereg §2, A1 修正案 lineage)",
                   "is_end_date": str(is_dates[-1].date()),
                   "h_lag_law": "signal day T = panel row T (sina lscjfb "
                                "day-T close face); forward strictly T+1 "
                                "(fwd_h[T]=close[T+1+h]/close[T+1]-1)"},
        "universe": {"n_status_symbols": n_syms,
                     "day_eligibility": f"helper floor n>={MIN_DAY_NAMES} "
                                        "(no width gate; coverage disclosed)",
                     "min_panel_rows": MIN_PANEL_ROWS,
                     "panel_counts": counts or {},
                     "median_cross_section": int(np.median(
                         A.sum(axis=1)[elig]))},
        "gates": {"h_gate": H_GATE, "v1_floor": V1_FLOOR, "v2_ir_min": V2_IR,
                  "v3_retain_min": V3_RETAIN, "min_periods_is": cfg["min_is"],
                  "min_periods_oos": cfg["min_oos"], "null_n": N_NULLS,
                  "seed_key": SEED_KEY},
        "d6_law": {"max_abs_corr_reject": D6_MAX_CORR_REJECT,
                   "min_overlap_days": D6_MIN_DAYS,
                   "intra_batch": "sleeve-tag disclosure, not admission"},
        "intra_batch_pairs": intra,
        "intra_batch_note": INTRA_BATCH_NOTE,
        "rows": rows,
        "audit": {"runtime_s": round(time.time() - t0, 1),
                  "machine": machine or socket.gethostname(),
                  "process_model": "single-process deterministic L1 "
                                   "(pool-supervised; C8 preemption -> "
                                   "whole-run restart, no intra-run state "
                                   "face — prereg §6 engineering note)",
                  "n_rows_scanned": (counts or {}).get("rows"),
                  "accept_ts": accept_ts,
                  "latent_repull_defect_note": latent_note},
        "ledger_note": "factor-reference batch: append_ledger(batch_trials="
                       f"{len(CONSTRUCTS)}) at run time; IC counts "
                       f"{len(CONSTRUCTS)}+{N_NULLS} per construct in factor "
                       "audit; engine trials ledger N untouched",
        "prereg": "research/SINA_CONSTRUCT_P1.md (freeze commit precedes "
                  "run, R99 law)",
        "runtime_s": round(time.time() - t0, 1),
    }
    if ledger:
        led = append_ledger(batch_name="sina_construct_p1",
                            batch_trials=len(CONSTRUCTS),
                            file_name=os.path.relpath(out_json, ROOT),
                            evidence_cutoff=panel_cutoff)
        out["trials_ledger"] = led
    os.makedirs(os.path.dirname(out_json), exist_ok=True)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    pd.DataFrame(rows).to_csv(out_csv, index=False)
    print(f"written {out_json} + {out_csv} ({time.time()-t0:.0f}s)", flush=True)
    return 0


def _toy(tmp, n_days=120, n_codes=12, narrow_days=10, status_complete=True,
         accept_verdict="PASS"):
    """Hermetic synthetic fixture: sina panel CSVs (frozen 14-col header) +
    bars parquets + eligibility/mask CSVs + status/accept JSONs in a tmp
    sandbox. Designed cross-section: factor base_i spans [-5,5]; close paths
    grow at 0.1%*base_i per day -> TIER_r0 carries a designed positive IC with
    non-zero daily variance. Codes 8 (mask-false), 9 (ineligible), 10
    (short-history 30 rows) exercise the §2 exclusion buckets; a collapse-
    violating row (code 0, day 40) and an unverifiable row (code 1, day 50)
    exercise the booking-law mirror."""
    cal = pd.bdate_range("2026-01-05", periods=n_days)
    per = os.path.join(tmp, "per")
    bars = os.path.join(tmp, "bars")
    os.makedirs(per)
    os.makedirs(bars)
    codes = [f"{600000 + i:06d}" for i in range(n_codes)]
    rng = np.random.default_rng(7)
    base = np.linspace(-5.0, 5.0, n_codes)
    noise = rng.standard_normal((n_codes, n_days)) * 0.5
    for i, code in enumerate(codes):
        rows = []
        for t, d in enumerate(cal):
            if i >= 3 and t < narrow_days:
                continue  # narrow-head stocks start day 10
            if i == 10 and t >= 30:
                continue  # short-history bucket: only 20 rows (< 50)
            r0 = base[i] * 1e6 + noise[i, t] * 1e5
            r1, r2, r3 = r0 * 0.5, r0 * 0.2, r0 * 0.05
            net = r0 + r1 + r2 + r3
            if i == 0 and t == 40:
                net = 123.456  # collapse violation (> 1e-3 drift)
            if i == 1 and t == 50:
                r2 = ""       # unverifiable: net present, tier missing
                net = r0 + r1 + r3
            rows.append({"opendate": str(d.date()), "trade": "1000",
                         "changeratio": "0.0", "turnover": "100000000",
                         "netamount": f"{net:.10g}", "ratioamount": "0.5",
                         "r0": "30", "r1": "20", "r2": "10", "r3": "5",
                         "r0_net": f"{r0:.10g}", "r1_net": f"{r1:.10g}",
                         "r2_net": f"{r2}", "r3_net": f"{r3:.10g}"})
        pd.DataFrame(rows).to_csv(os.path.join(per, f"{code}.csv"),
                                  index=False)
        if i == 10:
            dcal, cvals = cal[:30], 100.0 * (1 + 0.001 * base[i]) ** np.arange(30)
        elif i >= 3:
            dcal = cal[narrow_days:]
            cvals = 100.0 * (1 + 0.001 * base[i]) ** np.arange(narrow_days, n_days)
        else:
            dcal = cal
            cvals = 100.0 * (1 + 0.001 * base[i]) ** np.arange(n_days)
        pd.DataFrame({"date": dcal, "close": cvals}).to_parquet(
            os.path.join(bars, f"{code}.parquet"), index=False)
    with open(os.path.join(tmp, "elig.csv"), "w", encoding="utf-8") as f:
        f.write("code,name,eligible\n")
        for i, c in enumerate(codes):
            f.write(f"{c},n{i},{'False' if i == 9 else 'True'}\n")
    with open(os.path.join(tmp, "mask.csv"), "w", encoding="utf-8") as f:
        f.write("code,board,ok_static\n")
        for i, c in enumerate(codes):
            f.write(f"{c},main,{'False' if i == 8 else 'True'}\n")
    status = {"panel": {"complete": status_complete, "n_symbols": n_codes,
                       "cutoff": str(cal[-1].date())}}
    with open(os.path.join(tmp, "status.json"), "w", encoding="utf-8") as f:
        json.dump(status, f)
    with open(os.path.join(tmp, "accept.json"), "w", encoding="utf-8") as f:
        json.dump({"verdict": accept_verdict, "ts": "2026-09-27T00:00:00"}, f)
    return per, bars, os.path.join(tmp, "status.json"), \
        os.path.join(tmp, "accept.json"), cal, codes


def selftest():
    """Hermetic offline checks: construct arithmetic / T+1 lag law / same-day
    factor availability / booking-law row filters / §2 universe buckets /
    run-gate honest exit 2 / full pipeline with D6 weak-check + intra-batch
    sleeve-tag + extreme-day face / per-construct null determinism."""
    seed0 = SEED_REGISTRY[SEED_KEY]
    with tempfile.TemporaryDirectory() as tmp:
        per, bars, sp, ap, cal, codes = _toy(tmp)
        cal_us = cal.values.astype("datetime64[us]").astype("int64")
        elig_set, mask_set = load_universe_filters(
            os.path.join(tmp, "elig.csv"), os.path.join(tmp, "mask.csv"))
        assert len(elig_set) == 11 and len(mask_set) == 11
        codes2, grids, counts = load_sina_panel(per, cal_us, elig_set, mask_set)
        # (e) §2 universe buckets: 12 files - 1 ineligible - 1 mask-false
        #     - 1 short-history = 9 kept
        assert counts["files"] == 12 and counts["off_eligibility"] == 1 \
            and counts["off_mask"] == 1 and counts["short_history"] == 1 \
            and counts["kept"] == 9, counts
        # (d) booking-law rows: collapse violation + unverifiable rejected
        assert counts["collapse_rejected"] == 1 \
            and counts["unverifiable_rows"] == 1, counts
        c0 = codes2.index("600000")
        assert np.isnan(grids["r0_net"][40, c0])   # collapse row never booked
        c1 = codes2.index("600001")
        assert np.isnan(grids["r2_net"][50, c1])  # unverifiable row dropped
        close, missing = load_bars_close(bars, codes2, cal_us)
        assert missing == 0
        # (c) factor same-day availability (NO shift): construct at row t is
        #     built from the panel row t face
        fac = build_constructs(grids)
        assert abs(fac["TIER_r0"][20, c0]
                   - grids["r0_net"][20, c0] / 1e8) < 1e-12
        # (a) construct arithmetic: MAIN = (r0_net+r1_net)/turnover
        fin = np.isfinite(fac["MAIN"])
        assert np.allclose(fac["MAIN"][fin],
                           ((grids["r0_net"] + grids["r1_net"]) / 1e8)[fin])
        # (b) T+1 lag law: fwd_h[T] = close[T+1+h]/close[T+1] - 1 exactly
        f1 = fwd_sina(close, 1)
        assert abs(f1[30, c0] - (close[32, c0] / close[31, c0] - 1)) < 1e-12 \
            and np.isnan(f1[-1, c0])
        f10 = fwd_sina(close, 10)
        assert abs(f10[30, c0] - (close[41, c0] / close[31, c0] - 1)) < 1e-12
        # day eligibility: helper floor n>=5 excludes the 3-name narrow head
        A, elig = eligible_days(close, f10)
        assert A[:10].sum() == 0 and len(elig) > 50
        # (f) run gate honest exit 2 on accept FAIL, nothing written
        rc = evaluate(cal_us, codes2, grids, close,
                      {"complete": True, "n_symbols": 12,
                       "cutoff": "2026-06-01"},
                      "FAIL", dict(PROD, min_symbols=8, min_elig=5,
                                   min_is=5, min_oos=2),
                      out_json=os.path.join(tmp, "o.json"),
                      out_csv=os.path.join(tmp, "o.csv"), ledger=False,
                      lhb_path=os.path.join(tmp, "absent.parquet"),
                      ths_dir=os.path.join(tmp, "no_ths"),
                      em_dir=os.path.join(tmp, "no_em"))
        assert rc == 2 and not os.path.exists(os.path.join(tmp, "o.json"))
        # (g) full pipeline pass with toy gates + hermetic-absent D6 faces ->
        #     weak-check declared, intra-batch sleeve-tag present, extreme-day
        #     face present, C2 key present, designed construct clears V-gates
        oj = os.path.join(tmp, "o2.json")
        rc2 = evaluate(cal_us, codes2, grids, close,
                       {"complete": True, "n_symbols": 12,
                        "cutoff": str(cal[-1].date())},
                       "PASS", dict(PROD, min_symbols=8, min_elig=5,
                                    min_is=5, min_oos=2),
                       out_json=oj, out_csv=os.path.join(tmp, "o2.csv"),
                       ledger=False, counts=counts,
                       lhb_path=os.path.join(tmp, "absent.parquet"),
                       ths_dir=os.path.join(tmp, "no_ths"),
                       em_dir=os.path.join(tmp, "no_em"), seed0=seed0)
        assert rc2 == 0
        with open(oj, encoding="utf-8") as f:
            out2 = json.load(f)
        assert out2["evidence_cutoff"] == str(cal[-1].date())
        assert out2["universe"]["panel_counts"]["kept"] == 9
        assert "audit" in out2 and out2["audit"]["machine"]
        assert len(out2["rows"]) == 5
        for row in out2["rows"]:
            assert row["d6_verdict"] == "weak_check_insufficient_coverage"
            assert len(row["intra_batch"]) == 4
            assert "top_days" in row["extreme_day_face"]
            assert row["nulls"]["seed_base"] == seed0
        r0row = next(r for r in out2["rows"] if r["factor"] == "TIER_r0")
        assert r0row["pass"] and "h1_is_ic" in r0row  # passer decay face
        # (h) per-construct null determinism: identical on re-run
        eff = A & np.isfinite(fac["TIER_r0"])
        F0 = rank_rows(eff, fac["TIER_r0"])
        R = rank_rows(eff, f10)
        isd = cal_index(cal_us)[elig[: len(elig) * 2 // 3]]
        t1 = null_threshold_per_construct(F0, R, cal_us, isd, eff, elig,
                                          n_nulls=8, seed0=seed0)
        t2 = null_threshold_per_construct(F0, R, cal_us, isd, eff, elig,
                                          n_nulls=8, seed0=seed0)
        assert t1 == t2 and t1[0] >= V1_FLOOR and t1[2] == 8
    print("selftest: 9/9 PASS")
    return 0


def main():
    assert len(sys.argv) >= 2 and sys.argv[1] in ("run", "selftest"), \
        "usage: sina_construct_ic.py run|selftest"
    if sys.argv[1] == "selftest":
        return selftest()
    panel_status = load_status()
    if not panel_status:
        print("run: sina_mf panel status absent on this machine "
              "(collector lane bm-a, R31) -> honest exit 2", flush=True)
        return 2
    accept_verdict, accept_ts, latent_note = load_accept_verdict()
    if accept_verdict != "PASS":
        print(f"run: sina_mf_accept latest run verdict={accept_verdict} "
              f"(ts={accept_ts}) — prereg §2 completeness gate RED -> honest "
              "exit 2, 禁跑", flush=True)
        return 2
    if latent_note:
        print(f"note: accept latent_repull_defect_note present (collector "
              f"face, first monthly re-pull window): {latent_note}", flush=True)
    elig_set, mask_set = load_universe_filters()
    if elig_set is None or mask_set is None:
        print("run: eligibility/mask universe faces absent on this machine "
              "-> honest exit 2", flush=True)
        return 2
    fps = sorted(glob.glob(os.path.join(SINA_PER, "*.csv")))
    if not fps:
        print("run: sina_mf panel empty on this machine (data-host lane "
              "bm-a per MSG-20260927-1615 pick (a)) -> honest exit 2",
              flush=True)
        return 2
    panel_dates = set()
    for fp in fps[:20000]:
        with open(fp, encoding="utf-8-sig") as f:
            f.readline()
            for line in f:
                panel_dates.add(line.split(",", 1)[0][:10])
    if not panel_dates:
        print("run: sina_mf panel rows unreadable -> honest exit 2", flush=True)
        return 2
    dmin = pd.Timestamp(min(panel_dates)) - pd.Timedelta(days=10)
    dmax = pd.Timestamp(max(panel_dates)) + pd.Timedelta(days=30)
    cal = set()
    for fp in sorted(glob.glob(os.path.join(BARS_DIR, "*.parquet"))):
        d = pd.to_datetime(pd.read_parquet(fp, columns=["date"])["date"])
        cal |= set(d[(d >= dmin) & (d <= dmax)])
    if not cal:
        print("run: bars calendar empty on this machine -> honest exit 2",
              flush=True)
        return 2
    cal_us = np.array(sorted(cal)).astype("datetime64[us]").astype("int64")
    codes, grids, counts = load_sina_panel(SINA_PER, cal_us, elig_set, mask_set)
    print(f"panel: {counts['files']} files -> {counts['kept']} kept codes, "
          f"{len(cal_us)} calendar days, buckets={counts}", flush=True)
    close, missing = load_bars_close(BARS_DIR, codes, cal_us)
    print(f"bars: {missing} panel codes without bars file", flush=True)
    return evaluate(cal_us, codes, grids, close, panel_status, accept_verdict,
                    PROD, OUT_JSON, OUT_CSV, ledger=True, counts=counts,
                    accept_ts=accept_ts, latent_note=latent_note)


if __name__ == "__main__":
    sys.exit(main())
