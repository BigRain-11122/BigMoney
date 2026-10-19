"""FUND-STAGESTYLE-COMBO-P1 runner -- stage x style conditional combo
(stock domain), r1050 bm-b.

Prereg: research/FUND-STAGESTYLE-COMBO-P1.md (freeze window state:
DRAFT-NOT-FROZEN; sec.3 mapping v1 + sec.5 predictions are written down
run-before; judged thresholds live there and in scripts/science_gates.py --
this file implements them and never re-states a threshold).

Why this file exists
  The three P1 sleeve runners (value / quality / divlowvol) read the
  Money02 p1c_stock npy panel, which does NOT exist on bm-b. Prereg sec.2c
  names the local rebuild path (data/astock_daily per-symbol qfq CSVs,
  cutoff >= 2026-10-19) as the main road. This runner therefore owns:
    (a) a local panel materializer that produces the exact _G surface the
        frozen family kernels expect (idx/syms/OHLC/volume/amount/pct),
        cached as npy under data/cache/p1c_local (gitignored, outside
        Money02 -- the Money02 no-touch law is not bent);
    (b) single-source reuse: family selection kernels are IMPORTED from the
        frozen runners (scripts/fund_*_p1.py) -- zero re-implementation of
        ranking rules, universes or floors;
    (c) the only new science: the stage->style mapping composition and its
        readout matrix.

Composition (prereg sec.3 mapping v1, finite enumeration, frozen before run)
  states    = REGIME5 five states (BULL/CHOP/GRIND/BEAR/SUPPORT)
  judged    = C1 divlowvol-tilt / C2 value-tilt / C3 quality-tilt
              BEAR=cash, GRIND=cash, CHOP+SUPPORT=divlowvol, BULL=<tilt>
  controls  = U-value / U-quality / U-divlowvol / U-EW (non-judged)
  cash leg  = zero return, zero cost, declared (no alpha, only beta removal)
  labels    = read at the month's FIRST trading day from the PREVIOUS
              trading day's label (prereg sec.2a PIT law)

Honesty boundaries
  * status=READOUT_ONLY: this runner produces the conditional readout
    matrix + controls. G1'/G2/DSR/M1 adjudication and the same-mask null
    family are NOT run here (nulls="pending"); a judged verdict is only
    ever issued by finalize over the frozen gates, never by this file.
  * x2 (cost-doubled) face is computed for every candidate: the conditional
    mapping pays a rotation tax that x2 makes visible.
  * funding gate: tools are cheap; the full-window engine run is a long
    job (>5 min). Use `--pool` to hand the burn to the runnable pool.

Usage
    python scripts/stagestyle_combo_p1_backtest.py materialize [--force]
    python scripts/stagestyle_combo_p1_backtest.py picks [--families ...]
    python scripts/stagestyle_combo_p1_backtest.py run [--faces x1,x2]
        [--candidates C1,C2,C3] [--limit-months N] [--out PREFIX]
    python scripts/stagestyle_combo_p1_backtest.py selftest
    python scripts/stagestyle_combo_p1_backtest.py status

Exit codes: 0 normal, 2 mechanism fault (reported verbatim), 3 precondition
missing (panel/faces not materialized yet -- honest no-op, not a pass).
"""

from __future__ import annotations

import argparse
import csv
import glob
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

ASTOCK_DIR = os.path.join(ROOT, "data", "astock_daily", "per")
LOCAL_CACHE = os.path.join(ROOT, "data", "cache", "p1c_local")
OUT_DIR = os.path.join(ROOT, "results", "stagestyle_combo_p1")
LABEL_DIR = os.path.join(ROOT, "results", "regime5_labels")
BENCH = os.path.join(ROOT, "data", "daily", "sh510300.csv")

PANEL_FIELDS = ("open", "high", "low", "close", "volume", "amount")
META_NAME = "meta.json"
STATES = ("BULL", "CHOP", "GRIND", "BEAR", "SUPPORT")

# ---- prereg sec.3 mapping v1 (frozen enumeration; never extended at run time)
MAP_TILT = {
    "C1": "DIVLOWVOL-YIELDVOL",
    "C2": "VALUE-PE",
    "C3": "QUALITY-ROE",
}
MAP_RULES = {
    "BEAR": "cash",
    "GRIND": "cash",
    "CHOP": "DIVLOWVOL-YIELDVOL",
    "SUPPORT": "DIVLOWVOL-YIELDVOL",
}
CONTROLS = {
    "U-value": "VALUE-PE",
    "U-quality": "QUALITY-ROE",
    "U-divlowvol": "DIVLOWVOL-YIELDVOL",
}
FAMILIES = ("value", "quality", "divlowvol")
TOPN = 20                      # family headline Top-N (prereg sec.3)


# --------------------------------------------------------------------- panel
def _symbol_files() -> list:
    return sorted(glob.glob(os.path.join(ASTOCK_DIR, "*.csv")))


def _scan_dates(files: list) -> list:
    days = set()
    for f in files:
        with open(f, "r", encoding="utf-8", errors="ignore") as fh:
            next(fh, None)
            for line in fh:
                if len(line) > 9:
                    days.add(line[:10])
    return sorted(days)


def _parse_file(path: str, didx: dict, out: dict, n_days: int) -> bool:
    """Fill out[field] (n_days,) for one symbol. Returns False when the
    symbol has no row inside the date axis."""
    rows = []
    with open(path, "r", encoding="utf-8", errors="ignore") as fh:
        rd = csv.reader(fh)
        next(rd, None)
        for rec in rd:
            if len(rec) < 7:
                continue
            p = didx.get(rec[0])
            if p is None:
                continue
            try:
                rows.append((p, float(rec[1]), float(rec[2]), float(rec[3]),
                             float(rec[4]), float(rec[5] or 0.0),
                             float(rec[6] or 0.0)))
            except (TypeError, ValueError):
                continue
    if not rows:
        return False
    arr = np.array(rows, dtype=np.float64)
    p = arr[:, 0].astype(int)
    for k, f in enumerate(PANEL_FIELDS):
        out[f][p] = arr[:, k + 1]
    return True


def cmd_materialize(args) -> int:
    files = _symbol_files()
    if not files:
        print(f"no symbol CSVs under {ASTOCK_DIR}")
        return 3
    if args.limit_symbols and args.limit_symbols > 0:
        files = files[: args.limit_symbols]
    os.makedirs(LOCAL_CACHE, exist_ok=True)
    meta_path = os.path.join(LOCAL_CACHE, META_NAME)
    if os.path.exists(meta_path) and not args.force:
        meta = json.load(open(meta_path, encoding="utf-8"))
        if meta.get("n_symbols") == len(files) and not args.limit_symbols:
            print(f"panel cache present: {meta['shape']} "
                  f"cutoff={meta['cutoff']} -> {LOCAL_CACHE} (use --force "
                  f"to rebuild)")
            return 0
    days = _scan_dates(files)
    if len(days) < 250:
        print(f"date axis too short ({len(days)})")
        return 2
    didx = {d: i for i, d in enumerate(days)}
    n_days = len(days)
    syms = []
    for path in files:
        sym = os.path.basename(path)[:-4]
        out = {f: np.full(n_days, np.nan, dtype=np.float32)
               for f in PANEL_FIELDS}
        if _parse_file(path, didx, out, n_days):
            syms.append((sym, out))
    if not syms:
        print("no parseable symbol")
        return 2
    codes = [s for s, _ in syms]
    n_sym = len(codes)
    # pct_chg is derived, not read (astock CSVs carry no pct column)
    arrays = {f: np.empty((n_days, n_sym), dtype=np.float32)
              for f in PANEL_FIELDS + ("pct_chg",)}
    for j, (_, out) in enumerate(syms):
        for f in PANEL_FIELDS:
            arrays[f][:, j] = out[f]
        close = out["close"].astype(np.float64)
        prev = np.concatenate(([np.nan], close[:-1]))
        with np.errstate(invalid="ignore", divide="ignore"):
            arrays["pct_chg"][:, j] = ((close / prev - 1.0) * 100.0)
    for f, arr in arrays.items():
        np.save(os.path.join(LOCAL_CACHE, f + ".npy"), arr)
    np.save(os.path.join(LOCAL_CACHE, "dates.npy"),
            pd.to_datetime(days).astype("int64").to_numpy())
    meta = {"shape": [n_days, n_sym], "n_symbols": len(files),
            "cutoff": days[-1], "start": days[0], "source": "data/astock_daily/per",
            "fields": list(arrays), "built_ts": pd.Timestamp.now().isoformat()}
    with open(meta_path, "w", encoding="utf-8") as fh:
        json.dump(meta, fh, ensure_ascii=False, indent=1)
    print(f"panel materialized: {n_days} days x {n_sym} syms "
          f"({days[0]}..{days[-1]}) -> {LOCAL_CACHE}")
    return 0


def load_local_panel():
    meta_path = os.path.join(LOCAL_CACHE, META_NAME)
    if not os.path.exists(meta_path):
        return None
    meta = json.load(open(meta_path, encoding="utf-8"))
    dates = np.load(os.path.join(LOCAL_CACHE, "dates.npy"))
    idx = pd.to_datetime(dates.astype("datetime64[us]"))
    arrays = {f: np.load(os.path.join(LOCAL_CACHE, f + ".npy"), mmap_mode="r")
              for f in PANEL_FIELDS + ("pct_chg",)}
    syms = sorted(os.path.basename(p)[:-4]
                  for p in glob.glob(os.path.join(ASTOCK_DIR, "*.csv")))
    syms = syms[: arrays["close"].shape[1]]
    return idx, syms, arrays, meta


# ------------------------------------------------------------------- families
def _import_family(name: str):
    import importlib
    return importlib.import_module(f"fund_{name}_p1")


def _family_faces(mod) -> dict:
    for fn in ("_load_value_faces", "_load_quality_faces",
               "_load_div_events"):
        if hasattr(mod, fn):
            return getattr(mod, fn)()
    raise RuntimeError(f"{mod.__name__}: no face loader")


def wire_family(name: str, panel):
    """Populate a frozen family module's _G with the local panel + its own
    parquet faces. Every kernel downstream stays the frozen one."""
    idx, syms, arrays, meta = panel
    mod = _import_family(name)
    close = np.asarray(arrays["close"])
    first_valid = np.argmax(np.isfinite(close), axis=0)
    codes_arr = np.array(syms)
    g = {
        "idx": idx, "syms": syms, "codes_arr": codes_arr,
        "first_valid": first_valid,
        "static_thr": np.where(np.array([s.startswith("68") for s in syms]),
                               0.20, 0.10).astype(np.float32),
        "is_cx": np.array([s.startswith("30") for s in syms]),
        "close_np": arrays["close"], "open_np": arrays["open"],
        "high_np": arrays["high"], "low_np": arrays["low"],
        "volume_np": arrays["volume"], "amount_np": arrays["amount"],
        "pct_np": arrays["pct_chg"],
        "by_sym": _family_faces(mod),
        "month_pos": mod.enumerate_starts_monthly(idx, arrays["close"]),
    }
    if name == "divlowvol":
        sidecars = getattr(mod, "_load_sidecars", None)
        if sidecars:
            g["sidecars"] = sidecars(g["by_sym"].keys())
    elif name == "quality":
        # quality family keeps its statement faces beside by_sym
        extra = getattr(mod, "_load_quality_faces", None)
        if extra:
            g["by_sym"] = extra()
    mod._G.clear()
    mod._G.update(g)
    mod._G.pop("_firing", None)
    if getattr(mod, "ETF_510300_CSV", None) and os.path.exists(BENCH):
        try:
            mod._G["regime"] = mod._regime_series(idx)
        except Exception:
            mod._G["regime"] = None
    else:
        mod._G["regime"] = None
    return mod


def family_picks(name: str, panel) -> list:
    mod = wire_family(name, panel)
    rule = {"value": "pe", "quality": "roe", "divlowvol": None}[name]
    if name == "divlowvol":
        return mod._cell_picks(None, TOPN)
    return mod._cell_picks(rule, TOPN)


# ---------------------------------------------------------------- stage labels
def load_stage_labels() -> dict:
    files = sorted(glob.glob(os.path.join(LABEL_DIR, "REGIME5-*.json")))
    if not files:
        raise FileNotFoundError("no REGIME5 label face")
    doc = json.load(open(files[-1], encoding="utf-8"))
    out = {}
    for row in doc.get("labels") or []:
        out[str(row["date"])[:10]] = row["state"]
    if not out:
        raise ValueError("empty stage label face")
    return out


def label_at_month_start(idx, month_pos: list, labels: dict) -> list:
    """prereg sec.2a PIT law: the month's allocation reads the label of the
    PREVIOUS trading day (never the month's own close)."""
    out = []
    for m in month_pos:
        if m <= 0:
            out.append(None)
            continue
        d = str(idx[m - 1].date())
        out.append(labels.get(d))
    return out


# ------------------------------------------------------------------ compose
def compose_picks(family_pick: dict, mapping: dict, month_pos: list,
                  states: list) -> list:
    """Map each month to the picked symbols of the mapped sleeve. Cash months
    contribute no symbols (position closed at that month's signal day).
    family_pick: {sleeve_cell: [(m, end, top, w), ...]}."""
    by_month = {}
    for sleeve, picks in family_pick.items():
        by_month[sleeve] = {m: (end, top, w) for (m, end, top, w) in picks}
    out = []
    for m, state in zip(month_pos, states):
        if state is None:
            continue
        sleeve = mapping.get(state)
        if not sleeve or sleeve == "cash":
            continue
        rec = by_month.get(sleeve, {}).get(m)
        if not rec:
            continue
        end, top, w = rec
        out.append((m, end, top, w))
    return out


def pick_stats(picks: list) -> dict:
    months = sorted({m for (m, _e, _t, _w) in picks})
    return {"n_months_with_position": len(months),
            "n_symbol_holds": int(sum(len(t) for (_m, _e, t, _w) in picks)),
            "first_month_pos": months[0] if months else None}


# --------------------------------------------------------------------- metrics
def nav_metrics(nav: pd.Series) -> dict:
    from engine.metrics import max_drawdown, sharpe
    rets = nav.pct_change().dropna()
    return {"sharpe": round(float(sharpe(nav)), 6),
            "ret": round(float(nav.iloc[-1] / nav.iloc[0] - 1), 6),
            "max_dd": round(float(max_drawdown(nav)), 6),
            "n_days": int(len(nav)),
            "vol_ann": round(float(rets.std() * np.sqrt(252)), 6),
            "daily": [round(float(v), 8) for v in rets.to_numpy()]}


def run_spans(mod, spans, face: str, lo: int, hi: int) -> dict:
    run = mod.run_cell_portfolio(spans, face, lo, hi, keep_trades=False)
    if run is None:
        return {"empty": True}
    nav = mod._nav_from_run(run, lo, hi)
    out = nav_metrics(nav)
    out.update({"n_trades": run["n_trades"], "n_entries": run["n_entries"],
                "empty": False})
    return out


def _corr(a: list, b: list) -> float:
    n = min(len(a), len(b))
    if n < 20:
        return 0.0
    x = np.asarray(a[-n:], dtype=float)
    y = np.asarray(b[-n:], dtype=float)
    if x.std() == 0 or y.std() == 0:
        return 0.0
    return round(float(np.corrcoef(x, y)[0, 1]), 4)


def cmd_picks(args) -> int:
    panel = load_local_panel()
    if panel is None:
        print("panel cache missing -- run `materialize` first")
        return 3
    out = {}
    for name in args.families:
        picks = family_picks(name, panel)
        out[name] = pick_stats(picks)
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0


def cmd_run(args) -> int:
    panel = load_local_panel()
    if panel is None:
        print("panel cache missing -- run `materialize` first")
        return 3
    idx, syms, arrays, meta = panel
    labels = load_stage_labels()
    faces = [f.strip() for f in args.faces.split(",") if f.strip()]
    cands = [c.strip() for c in args.candidates.split(",") if c.strip()]

    pick_faces = {}
    gaps = {}
    month_pos = None
    host = None
    for name in FAMILIES:
        try:
            mod = wire_family(name, panel)
            pick_faces[name] = mod._cell_picks(
                {"value": "pe", "quality": "roe"}.get(name), TOPN)
        except Exception as exc:            # noqa: BLE001 - honest gap face
            gaps[name] = f"{type(exc).__name__}: {exc}"
            print(f"[GAP] family {name} unavailable: {gaps[name]}")
            continue
        if name == "value":
            month_pos = list(mod._G["month_pos"])
            host = mod
    if host is None or month_pos is None:
        print("family wiring failed (value sleeve is the calendar host)")
        return 2

    states = label_at_month_start(idx, month_pos, labels)
    unlabeled = sum(1 for s in states if s is None)
    sleeve_cells = {"value": "VALUE-PE", "quality": "QUALITY-ROE",
                    "divlowvol": "DIVLOWVOL-YIELDVOL"}
    sleeve_picks = {sleeve_cells[k]: v for k, v in pick_faces.items()}

    lo_candidates = [picks[0][0] for picks in sleeve_picks.values() if picks]
    if not lo_candidates:
        print("no sleeve picks -- family faces unavailable")
        return 3
    lo = max(lo_candidates)
    # A conditional mapping cannot allocate before the stage-label face
    # starts: the shared evaluation window therefore begins at the first
    # month that actually carries a PIT label (disclosed in the receipt).
    first_labeled = next((m for m, s in zip(month_pos, states)
                          if s is not None), None)
    if first_labeled is None:
        print("no PIT-labeled month -- stage face does not cover the panel")
        return 3
    lo = max(lo, int(first_labeled))
    hi = len(idx) - 1
    if args.limit_months and args.limit_months > 0:
        hi = min(hi, lo + args.limit_months * 21)
    print(f"window {idx[lo].date()}..{idx[hi].date()} "
          f"({hi - lo + 1} bars) unlabeled_months={unlabeled} gaps={list(gaps)}")

    jobs = {}
    blocked = {}
    for cand in cands:
        tilt = MAP_TILT.get(cand)
        if not tilt:
            print(f"unknown candidate {cand}")
            return 2
        mapping = dict(MAP_RULES)
        mapping["BULL"] = tilt
        used = {v for v in mapping.values() if v != "cash"}
        missing = sorted(used - set(sleeve_picks))
        if missing:
            # A candidate whose mapping needs an uncomputable sleeve is NOT
            # run at all: substituting cash/another sleeve would silently
            # re-design the frozen mapping v1.
            blocked[cand] = {"missing_sleeves": missing}
            print(f"[BLOCKED] {cand}: sleeve(s) unavailable {missing}")
            continue
        picks = compose_picks(sleeve_picks, mapping, month_pos, states)
        jobs[cand] = compose_spans(host, picks, idx, lo, hi)
    for label, cell in CONTROLS.items():
        if cell not in sleeve_picks:
            blocked[label] = {"missing_sleeves": [cell]}
            continue
        jobs[label] = host._spans_from_picks(
            [p for p in sleeve_picks[cell] if lo <= p[0] <= hi])
    # equal-weight control over the AVAILABLE sleeves (declared coverage)
    jobs["U-EW"] = _ew_spans(sleeve_picks, lo, hi)
    if not jobs:
        print("no runnable candidate: every mapping needs a missing sleeve")
        return 3

    results = {}
    for name, spans in jobs.items():
        rec = {}
        for face in faces:
            rec[face] = run_spans(host, spans, face, lo, hi)
        results[name] = rec
        print(f"  {name}: " + " | ".join(
            f"{f} sharpe={rec[f].get('sharpe')}" for f in faces))

    # D6 structural disclosure: conditional combos are allocators over the
    # very sleeves they compare against -- correlation is reported, not used
    # as a rejection face (prereg sec.1 D6 disclosure clause).
    disclosure = {}
    runnable = [c for c in cands if c in jobs]
    base = results[runnable[0]][faces[0]] if runnable else {}
    for name in list(CONTROLS) + ["U-EW"]:
        if name in results and base.get("daily") and \
                results[name][faces[0]].get("daily"):
            disclosure[name] = _corr(base["daily"],
                                     results[name][faces[0]]["daily"])

    p4 = None
    if runnable and "U-divlowvol" in results:
        uc = results["U-divlowvol"][faces[0]].get("sharpe")
        best = max((results[c][faces[0]].get("sharpe") or -9e9)
                   for c in runnable)
        if uc is not None:
            p4 = {"gate": "combo_sharpe >= U-divlowvol + 0.10",
                  "best_combo_sharpe": best, "u_divlowvol_sharpe": uc,
                  "passes": bool(best >= uc + 0.10),
                  "label": "PREDICTIVE_CHECK_ONLY (not a judged verdict)"}

    os.makedirs(OUT_DIR, exist_ok=True)
    cutoff = str(idx[hi].date())
    doc = {
        "batch": "FUND-STAGESTYLE-COMBO-P1",
        "status": ("PARTIAL_DISCLOSED" if (gaps or blocked)
                   else "READOUT_ONLY"),
        "prereg": "research/FUND-STAGESTYLE-COMBO-P1.md",
        "prereg_state": "DRAFT-NOT-FROZEN",
        "machine": "bm-b",
        "panel": {"source": meta["source"], "shape": meta["shape"],
                  "cutoff": meta["cutoff"],
                  "panel_cutoff_used": cutoff},
        "evidence_cutoff": cutoff,
        "cutoff_meta": {"cutoff": cutoff, "face": "astock_daily_local"},
        "stage_labels": {"face": sorted(glob.glob(
            os.path.join(LABEL_DIR, "REGIME5-*.json")))[-1],
            "states": list(STATES), "unlabeled_months": unlabeled},
        "mapping_v1": {c: dict(MAP_RULES, BULL=MAP_TILT[c]) for c in cands},
        "window": {"lo": str(idx[lo].date()), "hi": cutoff,
                   "bars": int(hi - lo + 1)},
        "results": results,
        "data_gaps": gaps,
        "blocked_candidates": blocked,
        "single_source": ("family selection kernels imported from "
                          "scripts/fund_*_p1.py (zero re-implementation); "
                          "local panel = data/astock_daily per-symbol qfq"),
        "d6_disclosure": disclosure,
        "p4_predictive_check": p4,
        "nulls": "pending (same-mask shuffle family not run here)",
        "gates": "UNJUDGED -- G1'/G2/DSR/M1 belong to finalize",
    }
    out = os.path.join(OUT_DIR, f"SSCOMBO-P1-{cutoff}.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    with open(os.path.join(OUT_DIR, "latest.json"), "w",
              encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    print(f"wrote {out}")
    return 0


def _ew_spans(sleeve_picks: dict, lo: int, hi: int):
    """Equal-weight-three control: union of the three sleeves' monthly picks
    with each sleeve contributing 1/3 of the book (weights carried as the
    per-month scale, split across that sleeve's names)."""
    from collections import defaultdict
    spans = defaultdict(list)
    by_month = defaultdict(list)
    for cell, picks in sleeve_picks.items():
        for (m, end, top, w) in picks:
            if lo <= m <= hi:
                by_month[m].append((end, top, w))
    for m, recs in by_month.items():
        n_sleeves = len(recs)
        for (end, top, w) in recs:
            for j in top:
                spans[int(j)].append((m, end, float(w) / n_sleeves))
    return {k: sorted(v) for k, v in spans.items()}


def compose_spans(mod, picks, idx, lo: int, hi: int):
    picked = [p for p in picks if lo <= p[0] <= hi]
    return mod._spans_from_picks(picked)


# ------------------------------------------------------------------- selftest
def cmd_selftest(args) -> int:
    legs = []

    def leg(name, fn):
        try:
            fn()
            legs.append((name, True, ""))
        except Exception as exc:            # noqa: BLE001 - report verbatim
            legs.append((name, False, f"{type(exc).__name__}: {exc}"))

    def l1():
        idx = pd.date_range("2024-01-01", periods=30, freq="D")
        labels = {str(d.date()): "BULL" for d in idx}
        states = label_at_month_start(idx, [0, 29], labels)
        assert states[0] is None, "month 0 must have no previous bar"
        assert states[1] == "BULL"

    def l2():
        # PIT: label read at month start must come from day m-1, never m
        idx = pd.date_range("2024-01-01", periods=5, freq="D")
        labels = {str(idx[0].date()): "BEAR", str(idx[1].date()): "BULL"}
        states = label_at_month_start(idx, [1], labels)
        assert states == ["BEAR"], states

    def l3():
        picks = [(10, 20, np.array([1, 2]), 0.5), (20, 30, np.array([3]), 1.0)]
        fp = {"DIVLOWVOL-YIELDVOL": picks}
        mp = [10, 20, 30]
        states = ["BULL", "CHOP", "BEAR"]
        out = compose_picks(fp, dict(MAP_RULES, BULL="DIVLOWVOL-YIELDVOL"),
                            mp, states)
        assert [p[0] for p in out] == [10, 20], out     # BEAR=cash dropped

    def l4():
        picks = [(10, 20, np.array([1]), 1.0)]
        fp = {"VALUE-PE": picks}
        out = compose_picks(fp, dict(MAP_RULES, BULL="VALUE-PE"),
                            [10], ["BULL"])
        assert len(out) == 1
        out2 = compose_picks(fp, dict(MAP_RULES, BULL="QUALITY-ROE"),
                             [10], ["BULL"])
        assert out2 == [], "mapped sleeve with no picks contributes nothing"

    def l5():
        class M:
            @staticmethod
            def _spans_from_picks(picks):
                from collections import defaultdict
                sp = defaultdict(list)
                for (m, e, t, w) in picks:
                    for j in t:
                        sp[int(j)].append((m, e, w))
                return dict(sp)
        sp = compose_spans(M, [(5, 9, np.array([1]), 1.0),
                               (40, 45, np.array([2]), 1.0)], None, 0, 20)
        assert list(sp) == [1], sp

    def l6():
        sp = _ew_spans({"A": [(5, 9, np.array([1]), 1.0)],
                        "B": [(5, 9, np.array([2]), 1.0)]}, 0, 20)
        assert sp[1][0][2] == 0.5 and sp[2][0][2] == 0.5, sp

    def l7():
        # mapping table integers are frozen: cash on BEAR/GRIND is mandatory
        assert MAP_RULES["BEAR"] == "cash" and MAP_RULES["GRIND"] == "cash"
        assert MAP_RULES["CHOP"] == MAP_RULES["SUPPORT"]

    def l8():
        s = pd.Series(np.linspace(1.0, 1.2, 100))
        m = nav_metrics(s)
        assert m["sharpe"] > 0 and abs(m["ret"] - 0.2) < 1e-9, m

    for n, fnn in [("label_pit_prev_bar", l1), ("label_pit_exact", l2),
                   ("compose_cash_months", l3), ("compose_sleeve_miss", l4),
                   ("compose_window_clip", l5), ("ew_weight_split", l6),
                   ("mapping_frozen", l7), ("metrics_known_answer", l8)]:
        leg(n, fnn)
    ok = sum(1 for _n, p, _e in legs if p)
    for n, p, e in legs:
        print(("[PASS] " if p else "[FAIL] ") + n + (" " + e if e else ""))
    print(f"selftest: {ok}/{len(legs)} PASS")
    return 0 if ok == len(legs) else 2


def cmd_status(args) -> int:
    panel = load_local_panel()
    doc = {"panel": None, "labels": None, "outputs": []}
    if panel:
        _idx, _syms, _arrays, meta = panel
        doc["panel"] = {"shape": meta["shape"], "cutoff": meta["cutoff"],
                        "start": meta["start"], "cache": LOCAL_CACHE}
    files = sorted(glob.glob(os.path.join(LABEL_DIR, "REGIME5-*.json")))
    doc["labels"] = files[-1] if files else None
    doc["outputs"] = sorted(glob.glob(os.path.join(OUT_DIR, "SSCOMBO-*.json")))
    print(json.dumps(doc, ensure_ascii=False, indent=1))
    return 0 if panel else 3


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    m = sub.add_parser("materialize")
    m.add_argument("--force", action="store_true")
    m.add_argument("--limit-symbols", type=int, default=0)
    m.set_defaults(fn=cmd_materialize)

    p = sub.add_parser("picks")
    p.add_argument("--families", default=",".join(FAMILIES))
    p.set_defaults(fn=cmd_picks)

    r = sub.add_parser("run")
    r.add_argument("--faces", default="x1")
    r.add_argument("--candidates", default=",".join(MAP_TILT))
    r.add_argument("--limit-months", type=int, default=0)
    r.set_defaults(fn=cmd_run)

    sub.add_parser("selftest").set_defaults(fn=cmd_selftest)
    sub.add_parser("status").set_defaults(fn=cmd_status)

    args = ap.parse_args(argv)
    if args.cmd == "picks":
        args.families = [f.strip() for f in args.families.split(",") if f.strip()]
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())