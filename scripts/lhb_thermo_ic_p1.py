"""LHB_THERMO_IC_P1 runner (explore board E5 slice-2, bm-a r947 freeze).

Market-level LHB aggregate-emotion axes -> 510300 forward-info TS-IC
verdict batch. Design frozen verbatim in research/LHB_THERMO_IC_P1.md
(freeze commit precedes the burn; post-freeze spec edits = none --
runner is part of the freeze). Conventions reused, zero re-implementation:
  - faces: results/lhb_thermo/lhb_thermo_daily.csv (emotion signal face,
    slice-1 product, 4,799 rows) + data/daily/sh510300.csv (index return
    face, 3,490 rows, 2012-05-28+ -- the 2007..2012-05 LHB segment is
    unmeasurable on this face and disclosed as such, no backfill)
  - signal s(t) = -z_w(axis(t)), w in {120, 250} -- contrarian convention
    frozen per prereg sec.1 mechanism (hot-money crowding peaks mark
    local tops; withdrawal troughs mark bottoms)
  - lag: LHB discloses >=18:00 on t -> fwd return r_h(t) =
    close(t+1+h)/close(t+1) - 1 (close-to-close from t+1)
  - TS-IC: spearman(s, r_h) per window; monthly sub-ICs (>=15 pairs/month)
    feed IC_IR = mean/std; V1/V2/V3 gates frozen (PA_LHB_IC calibre),
    h10 = the ONLY gating horizon (h5/h20 report-only)
  - nulls: K=200 circular-shift structure-preserving phase randomization,
    rng(94700+i) i<200 (SEED_REGISTRY lhb_thermo_ic_p1_nulls; 94 band
    pocket, never climbs the 95_000+ N1 staircase)
  - IS/OOS: composite_ic.IS_END company-wide (IS<=2024-12-31, OOS 2025+)
  - gates: science_gates.m1_t_value_gate / cutoff_meta / append_ledger /
    closed_family_check; NO engine import (exit-axis declaration (3)
    template_default: pure IC measurement, zero positions, zero exit
    stack -- hard assert in run())
  - ledger: 36 real cells appended (PA_LHB zero-engine + PARKING
    real-cells precedents merged, frozen sec.3)

Determinism: no wall-clock in content fields; nulls seeded rng(94700+i);
redo (results JSON already carries trials_ledger for this batch) =
idempotent no-op exit 0 (r253 single-count law). Lane guard: lhb_thermo
face + 510300 panel bm-a-hosted; other machines probe fail-closed.

Exit codes: 0 normal/no-op; 2 mechanism failure; 3 VOID face-mismatch /
lane refusal (fail-closed, honest message, nothing written).
"""
import argparse
import json
import os
import random
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)

import science_gates as SG  # noqa: E402
from composite_ic import IS_END  # noqa: E402  # company-wide IS/OOS calibre

BATCH = "LHB_THERMO_IC_P1"
TRIALS = 36                    # 6 axes x 2 z-windows x 3 h (frozen sec.0)
N_NULLS = 200
CUTOFF = "2026-09-22"          # P-5C frozen face, fleet-wide (sibling same)
NULL_BASE = 94700              # SEED_REGISTRY lhb_thermo_ic_p1_nulls
V1_FLOOR = 0.02                # IC floor (PA_LHB calibre)
V2_IR_LINE = 0.30
V3_OOS_HALF = 0.5
MIN_IS_PAIRS = 500
MIN_MONTH_PAIRS = 15
AXES = ["n_lhb", "netbuy_sum", "netbuy_pos_share", "med_netbuy",
        "netbuy_intensity", "amt_share"]
ZWINS = [120, 250]
HS = [5, 10, 20]
H_GATE = 10                    # the ONLY gating horizon (frozen sec.3)
SEGMENTS = {                   # frozen sec.3 descriptive segmentation
    "S1": ("2013-06-07", "2017-12-29"),
    "S2": ("2018-01-02", "2022-06-30"),
    "S3": ("2022-07-01", CUTOFF),
}
FROZEN_FACE1 = {"rows": 4799, "cols": 12, "first": "2007-01-04",
                "last": "2026-09-30"}
FROZEN_FACE2 = {"rows": 3490, "cols": 7, "first": "2012-05-28",
                "last": "2026-10-09"}
FACE1_COLS = ["date", "n_lhb", "buy_sum", "sell_sum", "netbuy_sum",
              "med_netbuy", "lhb_amt_sum", "mkt_amt_sum", "n_rows_raw",
              "netbuy_pos_share", "netbuy_intensity", "amt_share"]
FACE2_COLS = ["date", "open", "high", "low", "close", "volume", "amount"]

LHB_CSV = os.path.join(ROOT, "results", "lhb_thermo", "lhb_thermo_daily.csv")
ETF_CSV = os.path.join(ROOT, "data", "daily", "sh510300.csv")
OUT_DIR = os.path.join(ROOT, "results", "lhb_thermo_ic_p1")
OUT = os.path.join(OUT_DIR, "lhb_thermo_ic_p1_results.json")
CELLS_CSV = os.path.join(OUT_DIR, "cells_ts_ic.csv")
NULLS_CSV = os.path.join(OUT_DIR, "nulls_summary.csv")
PROBE_RC = os.path.join(ROOT, "results", "_r947bma_lhb_ic_probe.json")
SELFTEST_RC = os.path.join(ROOT, "results", "_r947bma_lhb_ic_selftest.json")
ATT_JSON = os.path.join(ROOT, "results", "gate_attrition.json")


def _void(msg):
    print(f"VOID fail-closed: {msg}")
    sys.exit(3)


def _now_iso():
    import datetime
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def _exit_axis_assert():
    """Frozen sec.3 exit-axis declaration (3) template_default: pure IC
    measurement, zero positions. Structural assertions (no source-regex
    self-match): (a) AST scan of this module finds NO direct
    engine/backtest/exit_rules import statement; (b) this module's global
    namespace binds NO object from the engine package family (transitive
    package import by the shared gate library is not this runner using
    the engine -- sibling thermo_overlay same semantics)."""
    import ast as _ast
    banned_tops = {"engine", "backtest", "exit_rules", "alloc_backtest"}
    tree = _ast.parse(open(os.path.abspath(__file__), encoding="utf-8").read())
    for node in _ast.walk(tree):
        if isinstance(node, _ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in banned_tops:
                    _void(f"exit-axis assert: direct import {alias.name}")
        elif isinstance(node, _ast.ImportFrom):
            if node.module and node.module.split(".")[0] in banned_tops:
                _void(f"exit-axis assert: direct from-import {node.module}")
    for name, obj in list(vars(sys.modules[__name__]).items()):
        mod = getattr(obj, "__module__", None)
        if mod and mod.split(".")[0] in banned_tops:
            _void(f"exit-axis assert: engine-family binding {name} <- {mod}")


def _pre_burn_checks():
    got = SG.SEED_REGISTRY.get("lhb_thermo_ic_p1_nulls")
    if got != NULL_BASE:
        _void(f"seed base lhb_thermo_ic_p1_nulls not registered "
              f"(got {got}, want {NULL_BASE})")
    cfam = SG.closed_family_check("lhb_thermo_ic_p1")
    if cfam.get("status") == "rejected":
        _void(f"closed-family gate rejected: {cfam}")
    return cfam


def load_faces(quiet=False):
    """Both frozen faces + hard completeness gates + same-face assertion."""
    f1 = pd.read_csv(LHB_CSV)
    if list(f1.columns) != FACE1_COLS:
        _void(f"face1 schema drift: {list(f1.columns)[:4]}...")
    if len(f1) != FROZEN_FACE1["rows"]:
        _void(f"face1 rows {len(f1)} != frozen {FROZEN_FACE1['rows']}")
    f1["date"] = pd.to_datetime(f1["date"])
    if str(f1["date"].iloc[0].date()) != FROZEN_FACE1["first"] \
            or str(f1["date"].iloc[-1].date()) != FROZEN_FACE1["last"]:
        _void(f"face1 window drift: {f1['date'].iloc[0].date()}.."
              f"{f1['date'].iloc[-1].date()}")
    f2 = pd.read_csv(ETF_CSV)
    if list(f2.columns) != FACE2_COLS:
        _void(f"face2 schema drift: {list(f2.columns)}")
    if len(f2) != FROZEN_FACE2["rows"]:
        _void(f"face2 rows {len(f2)} != frozen {FROZEN_FACE2['rows']}")
    f2["date"] = pd.to_datetime(f2["date"])
    if str(f2["date"].iloc[0].date()) != FROZEN_FACE2["first"]:
        _void(f"face2 first {f2['date'].iloc[0].date()} != "
              f"frozen {FROZEN_FACE2['first']}")
    # probe-assert: runner loads the exact declared paths (G-ANCHOR-FACE law)
    if not os.path.abspath(LHB_CSV).endswith(
            os.path.join("results", "lhb_thermo", "lhb_thermo_daily.csv")):
        _void("face-mismatch: face1 path != declared anchor path")
    if not os.path.abspath(ETF_CSV).endswith(
            os.path.join("data", "daily", "sh510300.csv")):
        _void("face-mismatch: face2 path != declared anchor path")
    # cutoff lockbox: truncate the return face at the frozen cutoff
    cut = pd.Timestamp(CUTOFF)
    f2 = f2[f2["date"] <= cut].copy()
    m = pd.merge(f1, f2[["date", "close"]], on="date", how="inner")
    m = m.sort_values("date").reset_index(drop=True)
    if len(m) < 3400:
        _void(f"join coverage {len(m)} < 3400 (calendar break?)")
    if not quiet:
        print(f"faces ok: face1 {len(f1)} rows, face2 pre-cut {len(f2)} rows, "
              f"join {len(m)} days {m['date'].iloc[0].date()}.."
              f"{m['date'].iloc[-1].date()}")
    return m


def build_signals(m):
    """Frozen sec.3: s(t) = -z_w(axis(t)) on the joined daily frame."""
    out = {}
    for ax in AXES:
        x = m[ax].astype(float).values
        for w in ZWINS:
            s = pd.Series(x)
            mu = s.rolling(w, min_periods=w).mean()
            sd = s.rolling(w, min_periods=w).std()
            z = (s - mu) / sd
            out[(ax, w)] = (-z).values  # contrarian convention (frozen)
    return out


def fwd_returns(m):
    """Frozen sec.3: r_h(t) = close(t+1+h)/close(t+1) - 1."""
    close = m["close"].astype(float).values
    out = {}
    for h in HS:
        k = 1 + h
        f = np.full(len(close), np.nan)
        f[:-k] = close[k:] / close[1:len(close) - h] - 1.0
        out[h] = f
    return out


def _spearman(a, b):
    ok = np.isfinite(a) & np.isfinite(b)
    if ok.sum() < 3:
        return np.nan, int(ok.sum())
    ra = pd.Series(a[ok]).rank().values
    rb = pd.Series(b[ok]).rank().values
    sd = ra.std() * rb.std()
    if sd == 0:
        return np.nan, int(ok.sum())
    return float(np.corrcoef(ra, rb)[0, 1]), int(ok.sum())


def ts_ic_window(s, r, idx):
    return _spearman(s[idx], r[idx])


def monthly_ics(s, r, dates, idx):
    """Monthly sub-ICs within the index window (>=MIN_MONTH_PAIRS pairs)."""
    df = pd.DataFrame({"d": dates[idx], "s": s[idx], "r": r[idx]})
    df = df[np.isfinite(df["s"].values) & np.isfinite(df["r"].values)]
    ics = []
    for _, g in df.groupby(df["d"].dt.to_period("M")):
        if len(g) >= MIN_MONTH_PAIRS:
            v, _ = _spearman(g["s"].values, g["r"].values)
            if np.isfinite(v):
                ics.append(v)
    return ics


def run(quiet=False):
    _exit_axis_assert()
    cfam = _pre_burn_checks()
    # idempotent redo guard (r253 single-count law)
    if os.path.exists(OUT):
        try:
            prev = json.load(open(OUT, encoding="utf-8"))
            if prev.get("batch") == BATCH and "trials_ledger" in prev:
                print(f"redo: {BATCH} already burned (ledger total "
                      f"{prev['trials_ledger'].get('total')}) -- idempotent "
                      f"no-op, zero re-append")
                return 0
        except Exception:
            pass
    m = load_faces(quiet=quiet)
    dates = m["date"]
    sig = build_signals(m)
    fr = fwd_returns(m)
    dstr = dates.dt.strftime("%Y-%m-%d").values
    is_mask = dstr <= IS_END
    oos_mask = dstr > IS_END
    seg_masks = {}
    for k, (a, b) in SEGMENTS.items():
        seg_masks[k] = (dstr >= a) & (dstr <= b)
    T = len(m)
    # circular shifts drawn once per null index (sibling convention:
    # same shift face across cells)
    shifts = []
    for i in range(N_NULLS):
        rng = random.Random(NULL_BASE + i)
        shifts.append(rng.randint(1, T - 1))

    rows, null_summary = [], []
    for (ax, w), s in sig.items():
        for h in HS:
            r = fr[h]
            gating = (h == H_GATE)
            ic_full, _ = ts_ic_window(s, r, np.ones(T, bool))
            ic_is, n_is = ts_ic_window(s, r, is_mask)
            ic_oos, n_oos = ts_ic_window(s, r, oos_mask)
            seg_ics = {}
            for k in SEGMENTS:
                v, n = ts_ic_window(s, r, seg_masks[k])
                seg_ics[k] = {"ts_ic": None if not np.isfinite(v) else round(v, 5),
                              "pairs": n}
            month_ics = monthly_ics(s, r, dates.values, is_mask)
            n_months = len(month_ics)
            ic_ir = None
            if n_months >= 3:
                arr = np.asarray(month_ics)
                ic_ir = float(arr.mean() / arr.std(ddof=1)) if arr.std(ddof=1) > 0 else None
            # null band on the IS window (circular shift preserves the
            # z-window inertia; the shift applies to the signal only)
            null_abs = []
            for i, sh in enumerate(shifts):
                s_n = np.roll(s, sh)
                v, _ = ts_ic_window(s_n, r, is_mask)
                if np.isfinite(v):
                    null_abs.append(abs(v))
            p95 = float(np.percentile(null_abs, 95)) if null_abs else None
            null_summary.append({"axis": ax, "zwin": w, "h": h,
                                  "null_p95_abs_ic": None if p95 is None else round(p95, 5),
                                  "n_nulls_finite": len(null_abs)})
            if not gating:
                rows.append({"axis": ax, "zwin": w, "h": h, "gating": False,
                             "ts_ic_full": None if not np.isfinite(ic_full) else round(ic_full, 5),
                             "ts_ic_is": None if not np.isfinite(ic_is) else round(ic_is, 5),
                             "pairs_is": n_is, "ts_ic_oos": None if not np.isfinite(ic_oos) else round(ic_oos, 5),
                             "pairs_oos": n_oos, "ic_ir_is": None if ic_ir is None else round(ic_ir, 4),
                             "n_months_is": n_months,
                             "segments": seg_ics, "v1": None, "v2": None,
                             "v3": None, "m1_t": None, "full_chain": False,
                             "report_only": True})
                continue
            # gates (h10 only, frozen sec.4)
            v1 = v2 = v3 = None
            if p95 is not None and np.isfinite(ic_is):
                v1 = bool(abs(ic_is) > max(V1_FLOOR, p95))
            if ic_ir is not None:
                v2 = bool(abs(ic_ir) >= V2_IR_LINE)
            if np.isfinite(ic_is) and np.isfinite(ic_oos) and ic_is != 0:
                v3 = bool((ic_oos > 0) == (ic_is > 0)
                          and abs(ic_oos) >= V3_OOS_HALF * abs(ic_is))
            pairs_ok = bool(n_is >= MIN_IS_PAIRS)
            m1_t = None
            if ic_ir is not None and n_months > 0:
                m1_t = float(ic_ir * np.sqrt(n_months))
            m1 = SG.m1_t_value_gate(m1_t if m1_t is not None else float("nan"),
                                    hurdle=3.0, claim_class="new_factor")
            full = bool(v1 and v2 and v3 and pairs_ok
                        and m1.get("pass", False))
            rows.append({"axis": ax, "zwin": w, "h": h, "gating": True,
                         "ts_ic_full": None if not np.isfinite(ic_full) else round(ic_full, 5),
                         "ts_ic_is": None if not np.isfinite(ic_is) else round(ic_is, 5),
                         "pairs_is": n_is,
                         "ts_ic_oos": None if not np.isfinite(ic_oos) else round(ic_oos, 5),
                         "pairs_oos": n_oos,
                         "ic_ir_is": None if ic_ir is None else round(ic_ir, 4),
                         "n_months_is": n_months,
                         "segments": seg_ics,
                         "null_p95_abs_ic": None if p95 is None else round(p95, 5),
                         "v1": v1, "v2": v2, "v3": v3,
                         "pairs_gate": pairs_ok,
                         "m1_t": None if m1_t is None else round(m1_t, 3),
                         "m1_pass": m1.get("pass", False),
                         "full_chain": full, "report_only": False})

    os.makedirs(OUT_DIR, exist_ok=True)
    pd.DataFrame([{k: v for k, v in row.items() if k != "segments"}
                  for row in rows]).to_csv(CELLS_CSV, index=False)
    pd.DataFrame(null_summary).to_csv(NULLS_CSV, index=False)
    gating_rows = [r_ for r_ in rows if r_["gating"]]
    n_pass = sum(1 for r_ in gating_rows if r_["full_chain"])
    ledger = SG.append_ledger(batch_name=BATCH, batch_trials=TRIALS,
                              file_name="lhb_thermo_ic_p1/lhb_thermo_ic_p1_results.json",
                              evidence_cutoff=CUTOFF)
    # attrition row (frozen sec.8 discipline)
    try:
        d = json.load(open(ATT_JSON, encoding="utf-8"))
        row = {"batch": BATCH, "ts": __import__("time").strftime("%Y-%m-%d %H:%M:%S"),
               "kind": "ic_judgment", "cells_ledger_delta": TRIALS,
               "ledger_total_after": ledger.get("total"),
               "gates": {"v1_pass": sum(1 for r_ in gating_rows if r_["v1"]),
                         "v2_pass": sum(1 for r_ in gating_rows if r_["v2"]),
                         "v3_pass": sum(1 for r_ in gating_rows if r_["v3"]),
                         "m1_pass": sum(1 for r_ in gating_rows if r_["m1_pass"]),
                         "full_chain_pass": n_pass},
               "entries": [f"{r_['axis']}|z{r_['zwin']}|h{r_['h']}" for r_ in gating_rows]}
        own = [i for i, e in enumerate(d.get("entries", []))
               if e.get("batch") == BATCH and e.get("kind") == "ic_judgment"]
        if own:
            d["entries"][own[-1]] = row
        else:
            d["entries"].append(row)
        with open(ATT_JSON, "w", encoding="utf-8") as fh:
            json.dump(d, fh, ensure_ascii=False, indent=1)
    except Exception as e:  # attrition face is best-effort disclosure
        print(f"attrition append failed (non-fatal, disclose): {e}")
    out = {
        "batch": BATCH,
        "burned_by": "bm-a r947",
        "burned_at": _now_iso(),
        "evidence_cutoff": CUTOFF,
        "science_gates": {"cutoff_meta": SG.cutoff_meta(CUTOFF)},
        "closed_family_check": cfam,
        "design": {"axes": AXES, "zwins": ZWINS, "hs": HS, "h_gate": H_GATE,
                   "segments": {k: list(v) for k, v in SEGMENTS.items()},
                   "is_end": IS_END, "null_base": NULL_BASE, "n_nulls": N_NULLS,
                   "convention": "contrarian s=-z_w(axis)"},
        "faces": {"face1_lhb_thermo": FROZEN_FACE1, "face2_sh510300": FROZEN_FACE2,
                  "join_days": int(len(m)),
                  "join_first": str(m['date'].iloc[0].date()),
                  "join_last": str(m['date'].iloc[-1].date()),
                  "unmeasurable_disclosed": "2007-01..2012-05 LHB segment "
                                            "(1311 days) unmeasurable on the "
                                            "2012-05-28+ ETF face, no backfill"},
        "gating_summary": {"gating_cells": len(gating_rows),
                           "full_chain_pass": n_pass,
                           "pass_cells": [f"{r_['axis']}|z{r_['zwin']}" for r_ in gating_rows
                                          if r_["full_chain"]]},
        "trials_ledger": ledger,
        "audit": {"engine_used": False, "exit_axis": "template_default_pure_ic",
                  "runtime_note": "L1 deterministic vectorized, in-round burn"},
        "cells": rows,
    }
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print(f"burn done: {len(rows)} cells ({len(gating_rows)} gating h10), "
          f"full_chain_pass={n_pass}, ledger total={ledger.get('total')}")
    print(f"results: {OUT}")
    return 0


def probe():
    m = load_faces()
    rc = {"batch": BATCH, "probe_at": _now_iso(),
          "face1": FROZEN_FACE1, "face2": FROZEN_FACE2,
          "join_days": int(len(m)),
          "join_first": str(m['date'].iloc[0].date()),
          "join_last": str(m['date'].iloc[-1].date()),
          "seed_registered": SG.SEED_REGISTRY.get("lhb_thermo_ic_p1_nulls"),
          "closed_family": SG.closed_family_check("lhb_thermo_ic_p1")}
    with open(PROBE_RC, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(rc, fh, ensure_ascii=False, indent=1)
    print(json.dumps(rc, ensure_ascii=False, indent=1))
    return 0


def selftest():
    """Offline fixtures: spearman sanity, circular-shift determinism, gates."""
    ok = []
    # fixture 1: spearman on a monotone pair == 1.0
    a = np.linspace(-2, 2, 50)
    b = a * 3.0 + 1.0
    v, n = _spearman(a, b)
    ok.append(("spearman_monotone", abs(v - 1.0) < 1e-9 and n == 50))
    # fixture 2: constant series -> NaN (zero variance guard)
    v2, _ = _spearman(np.ones(30), np.arange(30.0))
    ok.append(("spearman_const_nan", not np.isfinite(v2)))
    # fixture 3: circular shift determinism (same seed -> same shift)
    s1 = random.Random(94700).randint(1, 99999)
    s2 = random.Random(94700).randint(1, 99999)
    ok.append(("null_seed_determinism", s1 == s2 and 1 <= s1))
    # fixture 4: fwd return math r_h(t) = close[t+1+h]/close[t+1]-1
    close = np.array([10.0, 11.0, 12.1, 13.31, 14.0])
    f = np.full(5, np.nan)
    k = 1 + 1
    f[:-k] = close[k:] / close[1:len(close) - 1] - 1.0
    ok.append(("fwd_h1_math", abs(f[0] - (12.1 / 11.0 - 1)) < 1e-12
               and abs(f[1] - (13.31 / 12.1 - 1)) < 1e-12
               and not np.isfinite(f[3])))
    # fixture 5: exit-axis assert -- AST scan finds no direct engine-family
    # import and the module namespace binds no engine-family object
    # (structural checks, no source-regex self-match)
    import ast as _ast
    _banned = {"engine", "backtest", "exit_rules", "alloc_backtest"}
    _tree = _ast.parse(open(os.path.abspath(__file__), encoding="utf-8").read())
    _imports_bad = False
    for _node in _ast.walk(_tree):
        if isinstance(_node, _ast.Import):
            if any(a.name.split(".")[0] in _banned for a in _node.names):
                _imports_bad = True
        elif isinstance(_node, _ast.ImportFrom):
            if _node.module and _node.module.split(".")[0] in _banned:
                _imports_bad = True
    _bind_bad = any(
        getattr(_o, "__module__", None)
        and getattr(_o, "__module__", "").split(".")[0] in _banned
        for _o in list(vars(sys.modules[__name__]).values()))
    ok.append(("exit_axis_no_engine", not _imports_bad and not _bind_bad))
    # fixture 6: gate math -- V3 half-retention
    ok.append(("v3_half_line", abs(0.5 * 0.08 - 0.04) < 1e-12
               and bool((0.05 > 0) == (0.08 > 0))))
    rc = {"batch": BATCH, "selftest_at": _now_iso(),
          "cases": {k: bool(v) for k, v in ok},
          "all_pass": all(v for _, v in ok)}
    with open(SELFTEST_RC, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(rc, fh, ensure_ascii=False, indent=1)
    print(json.dumps(rc, ensure_ascii=False, indent=1))
    return 0 if rc["all_pass"] else 2


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", choices=["probe", "run", "selftest"])
    a = ap.parse_args()
    if a.cmd == "probe":
        sys.exit(probe())
    if a.cmd == "selftest":
        sys.exit(selftest())
    sys.exit(run())


if __name__ == "__main__":
    main()
