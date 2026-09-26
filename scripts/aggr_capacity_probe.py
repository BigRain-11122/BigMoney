"""scripts/aggr_capacity_probe.py -- T-80 slice-4 capacity face
(AGGR-CAPACITY-FACE-P1; prereg research/AGGR_CAPACITY_FACE_P1.md FROZEN
pre-run; CEO order O-20260926-1332 six-face canon clause 1; R179 caliber).

DISCLOSURE face for the 20 frozen battery variants: ADV20 participation-cap
reading at the variant's own ¥1M scale. Zero re-judge, zero new judgment
cells (battery 400 cells already in the ledger), zero adoption wiring.
Battery product results/aggr_fullpool_battery.json stays byte-frozen.

Caliber (prereg s3, verbatim battery sleeve machinery + two new kwargs):
  per (variant, sleeve, w>0): initial_cash = w x 1,000,000 CNY, engine-native
  D5 cost_v2={"adv20": panel} -- entry demand > 1% x ADV(20d) caps (partial
  fill kept, capped_entries counter), zero/negative ADV drops the order,
  missing ADV -> conservative no-cap + counter; per-side slippage tiered
  2/5/10bp by ADV(20d). No CostPatch (V2 basis = fixed fees + tiered slip).
  Sleeve inputs pinned to results/t56_caliber_registry snapshot (A1 law),
  manifest sha256 gate (raw + LF-normalized double door, R253 law).
  ADV20 panel = per-member own-bar amount.rolling(20, min_periods=1).mean()
  (no cross-member ffill; engine owns shift(1) causality + missing paths).

Units are deduped by (tid, scale) across variants (267 distinct of 291
variant-sleeve pairs, census-gated fail-closed).

Subcommands:
  run       full probe -> results/aggr_capacity_face/p1_results.json
            + gate_attrition entries row (cells_ledger_delta 0)
  selftest  offline fixtures (no network): synthetic ADV known-refusal /
            zero-ADV drop / missing-ADV / tier classification / scale
            boundary / determinism / battery-consumption census / caliber
            manifest gate / core48 smoke integration leg
"""
import argparse
import hashlib
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd

from config import PATHS
from engine import run_backtest
from knowledge.rules import (ADV20_TIER_2BP_YUAN, ADV20_TIER_5BP_YUAN,
                              ADV_FILL_CAP_RATE)
from live.paper import SIGNAL_BUILDERS, ExitPatch, build_panels, load_core
from parallel_runner import run_cells_parallel, worker_cap
from science_gates import cutoff_meta, ledger_head
from t28_stable_profit import W_CUR_END

PREREG = os.path.join(PATHS.root, "research", "AGGR_CAPACITY_FACE_P1.md")
BATTERY_JSON = os.path.join(PATHS.results_dir, "aggr_fullpool_battery.json")
OUT_DIR = os.path.join(PATHS.results_dir, "aggr_capacity_face")
OUT_JSON = os.path.join(OUT_DIR, "p1_results.json")
GA_PATH = os.path.join(PATHS.results_dir, "gate_attrition.json")
T56_CALIBER_DIR = os.path.join(PATHS.results_dir, "t56_caliber_registry",
                               "firm", "traders")
T56_MANIFEST = os.path.join(PATHS.results_dir, "t56_caliber_registry",
                            "_manifest.json")
BATCH = "AGGR-CAPACITY-FACE-P1"
SLEEVE_CUTOFF = W_CUR_END             # battery caliber truncation (t28)
EVIDENCE_CUTOFF = "2026-09-24"        # prereg s2 (core48 panel face)
SCALE_CNY = 1_000_000.0               # AGGR account scale (T-56 paper face)
N_VARIANTS = 20                       # prereg s0 census gates (frozen
N_PAIRS = 291                         # battery product consumption, fail-
N_UNITS = 267                         # closed on any drift)
RAM_FLOOR_GB = 4.0                    # fleet line
ADV_MIN_PERIODS = 1                   # prereg s2 (own-bar window, raw face)


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def machine_id() -> str:
    try:
        with open(os.path.join(PATHS.root, "fleet", "machine.json"),
                  encoding="utf-8") as fh:
            return json.load(fh)["machine_id"]
    except Exception:
        return "unknown"


def free_ram_gb() -> float:
    try:
        import psutil
        return psutil.virtual_memory().available / (1024 ** 3)
    except Exception:
        return 99.0


# ------------------------------------------------------------- worker layer
COST_BASIS_MISSING = "absent"        # cost_v2 block absent -> unit gate fail


def _cap_worker(args):
    """One (tid, scale) measurement unit. Trader spec served from the pinned
    caliber snapshot dir (A1 law); machinery mirrors t28._sleeve_worker
    verbatim plus the capacity kwargs (initial_cash, cost_v2) and the
    metrics-only report_num_entries flag (additive engine iron rule; the
    tier counters sum == num_entries identity is asserted in selftest)."""
    tid, scale_cny, trader_dir, prices = args
    try:
        import psutil
        psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    except Exception:
        pass
    P = build_panels(prices)
    with open(os.path.join(trader_dir, f"{tid}.json"),
              encoding="utf-8") as fh:
        t = json.load(fh)
    entry = SIGNAL_BUILDERS[t["params"]["entry"]](P)
    params = {k: v for k, v in t["params"].items() if k != "entry"}
    params["report_num_entries"] = True
    adv20 = pd.DataFrame(
        {s: prices[s]["amount"].rolling(20, min_periods=ADV_MIN_PERIODS)
            .mean() for s in prices}).sort_index()
    with ExitPatch(t.get("exit_overrides")):
        res = run_backtest(prices, params, initial_cash=float(scale_cny),
                           entry_signal=entry, exit_signal=(entry <= 0),
                           dd_control=t.get("dd_control"),
                           cost_v2={"adv20": adv20})
    cv = res.get("cost_v2") or {}
    m = res["metrics"]
    return {"tid": tid, "scale_cny": float(scale_cny),
            "cost_basis": cv.get("cost_basis", COST_BASIS_MISSING),
            "num_entries": int(m.get("num_entries", 0)),
            "n_trades": int(m.get("num_trades", 0)),
            "final_eq": round(float(res["equity_curve"][-1]), 2),
            "capped_entries": int(cv.get("capped_entries", 0)),
            "dropped_zero_adv": int(cv.get("dropped_zero_adv", 0)),
            "missing_adv_executions": int(cv.get("missing_adv_executions", 0)),
            "tier_entries_2bp": int(cv.get("tier_entries_2bp", 0)),
            "tier_entries_5bp": int(cv.get("tier_entries_5bp", 0)),
            "tier_entries_10bp": int(cv.get("tier_entries_10bp", 0))}


def _caliber_manifest_gate() -> int:
    """F11-style byte gate on the pinned snapshot, R253 double door:
    raw sha OR LF-normalized sha must match (git EOL transport face)."""
    with open(T56_MANIFEST, encoding="utf-8") as fh:
        man = json.load(fh)
    n = 0
    for rel, want in man.get("files", {}).items():
        p = os.path.join(T56_CALIBER_DIR, rel)   # manifest keys are bare
        if not os.path.exists(p):                # filenames under the
            p = os.path.join(os.path.dirname(T56_MANIFEST), rel)  # snapshot
        raw = open(p, "rb").read()
        sha_raw = hashlib.sha256(raw).hexdigest()
        sha_lf = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()
        if want not in (sha_raw, sha_lf):
            raise SystemExit(f"CALIBER GATE FAIL: {rel} sha drift "
                             f"(want {want[:12]}, got {sha_raw[:12]})")
        n += 1
    if n < 29:
        raise SystemExit(f"CALIBER GATE FAIL: manifest {n} < 29 files")
    return n


def _battery_units():
    """Consume the frozen battery product verbatim (single source, zero
    re-derivation): per variant weights_representative -> (tid, scale)
    units. Census gates = prereg s0 fail-closed."""
    b = json.load(open(BATTERY_JSON, encoding="utf-8-sig"))
    variants = b.get("variants", {})
    if len(variants) != N_VARIANTS:
        raise SystemExit(f"BATTERY GATE FAIL: {len(variants)} != 20 variants")
    pairs, units = [], {}
    vmap = {}
    for name, v in variants.items():
        wr = v.get("weights_representative")
        if not wr:
            raise SystemExit(f"BATTERY GATE FAIL: {name} no weights")
        gws = float(v.get("grid_weight_sum", 0.0))
        if abs(sum(wr.values()) - gws) > 1e-9:
            raise SystemExit(f"BATTERY GATE FAIL: {name} weight sum drift "
                             f"{sum(wr.values())} vs grid_weight_sum {gws}")
        vmap[name] = dict(wr)
        for tid, w in wr.items():
            pairs.append((name, tid))
            scale = round(float(w) * SCALE_CNY, 2)
            units.setdefault((tid, scale), []).append(name)
    if len(pairs) != N_PAIRS:
        raise SystemExit(f"BATTERY GATE FAIL: pairs {len(pairs)} != {N_PAIRS}")
    if len(units) != N_UNITS:
        raise SystemExit(f"BATTERY GATE FAIL: units {len(units)} != {N_UNITS}")
    return b, vmap, units


def _adv_yearly_table(prices) -> dict:
    """Per member per year ADV20 distribution (prereg s3 disclosure face,
    r206 _r206_cap_view shape). Panel values over the year's own bars."""
    adv = pd.DataFrame(
        {s: prices[s]["amount"].rolling(20, min_periods=ADV_MIN_PERIODS)
            .mean() for s in prices}).sort_index()
    out = {}
    for s in prices:
        a = adv[s].dropna()
        if a.empty:
            out[s] = {}
            continue
        for y, g in a.groupby(a.index.year):
            out.setdefault(s, {})[str(y)] = {
                "n": int(len(g)),
                "median": round(float(g.median()), 0),
                "p25": round(float(g.quantile(0.25)), 0),
                "p75": round(float(g.quantile(0.75)), 0),
                "cap1pct_median": round(ADV_FILL_CAP_RATE * float(g.median()), 0),
            }
    return out


# ------------------------------------------------------------------- run
def cmd_run() -> int:
    t0 = time.time()
    if os.path.exists(OUT_JSON) and not os.environ.get("AGGR_CAP_REFINALIZE"):
        log(f"single-shot guard: {OUT_JSON} exists -> no-op exit 0 "
            "(AGGR_CAP_REFINALIZE=1 = only redo, never re-ledgers)")
        return 0
    if free_ram_gb() < RAM_FLOOR_GB:
        raise SystemExit(f"RAM GATE FAIL: free {free_ram_gb():.1f}GB < "
                         f"{RAM_FLOOR_GB}GB (fleet line, honest exit)")
    log(f"=== {BATCH} (prereg frozen pre-run, disclosure face) ===")
    b, vmap, units = _battery_units()
    log(f"battery consumed: 20 variants, {N_PAIRS} pairs -> "
        f"{N_UNITS} distinct (tid, scale) units")

    n_man = _caliber_manifest_gate()
    log(f"caliber snapshot manifest gate PASS ({n_man} files)")

    prices_full = load_core()
    cutoff = max(df.index.max() for df in prices_full.values())
    if cutoff < SLEEVE_CUTOFF:
        raise SystemExit(f"PANEL GATE FAIL: cutoff {cutoff.date()} < "
                         f"{SLEEVE_CUTOFF.date()}")
    prices = {s: df[df.index <= SLEEVE_CUTOFF]
              for s, df in prices_full.items()}
    log(f"panel: {len(prices)} members, window -> {SLEEVE_CUTOFF.date()} "
        f"(file cutoff {cutoff.date()})")

    jobs = [(f"{tid}|{scale:.2f}", _cap_worker,
             (tid, scale, T56_CALIBER_DIR, prices))
            for (tid, scale) in sorted(units)]
    res = run_cells_parallel(jobs, workers=min(worker_cap(), 25),
                             desc="aggrcap-units")
    missing = [k for k, _, _ in jobs if k not in res]
    if missing:
        raise SystemExit(f"UNIT GATE FAIL: {len(missing)} units missing "
                         f"(e.g. {missing[:3]}) -- fail-closed, no product")
    log(f"units: {len(res)}/{len(jobs)} returned ({time.time()-t0:.0f}s)")

    urows = {}
    for k, r in res.items():
        urows[k] = r
        if r["cost_basis"] == COST_BASIS_MISSING:
            raise SystemExit(f"UNIT GATE FAIL: {k} cost_v2 block absent "
                             "-- engine D5 face not engaged, abort")

    variants_out = {}
    for name in sorted(vmap):
        wr = vmap[name]
        tot = {"num_entries": 0, "capped_entries": 0, "dropped_zero_adv": 0,
               "missing_adv_executions": 0, "tier_entries_2bp": 0,
               "tier_entries_5bp": 0, "tier_entries_10bp": 0, "n_trades": 0}
        constrained = []
        for tid, w in sorted(wr.items()):
            scale = round(float(w) * SCALE_CNY, 2)
            u = urows[f"{tid}|{scale:.2f}"]
            for f in tot:
                tot[f] += u[f]
            if u["capped_entries"] or u["dropped_zero_adv"]:
                constrained.append({"tid": tid, "scale_cny": scale,
                                    "capped_entries": u["capped_entries"],
                                    "dropped_zero_adv": u["dropped_zero_adv"],
                                    "num_entries": u["num_entries"]})
        label = "constrained" if constrained else "unconstrained"
        variants_out[name] = {
            "sleeves": {tid: urows[f"{tid}|{round(float(w)*SCALE_CNY, 2):.2f}"]
                        for tid, w in sorted(wr.items())},
            "totals": tot,
            "capacity_label": label,
            "constrained_detail": constrained,
            "capped_rate": (round(tot["capped_entries"]
                                   / tot["num_entries"], 6)
                            if tot["num_entries"] else None)}

    n_unc = sum(1 for v in variants_out.values()
                if v["capacity_label"] == "unconstrained")
    log(f"labels: {n_unc} unconstrained / {N_VARIANTS - n_unc} constrained")

    adv_yearly = _adv_yearly_table(prices)
    out = {
        **cutoff_meta(EVIDENCE_CUTOFF),
        "batch": BATCH,
        "prereg": PREREG,
        "prereg_sha256_lf": hashlib.sha256(
            open(PREREG, "rb").read().replace(b"\r\n", b"\n")).hexdigest(),
        "battery_consumed": os.path.basename(BATTERY_JSON),
        "battery_sha256": hashlib.sha256(
            open(BATTERY_JSON, "rb").read()).hexdigest(),
        "order": "O-20260926-1332 six-face canon clause 1 (capacity face)",
        "ticket": "T-2026-09-26-80-P1 slice-4",
        "caliber_snapshot": {"dir": os.path.relpath(T56_CALIBER_DIR,
                                                    PATHS.root),
                             "manifest_files": n_man},
        "units": urows,
        "units_census": {"variant_sleeve_pairs": N_PAIRS,
                         "distinct_units": N_UNITS},
        "variants": variants_out,
        "label_summary": {"unconstrained": n_unc,
                           "constrained": N_VARIANTS - n_unc},
        "six_face_capacity": {
            "covered": True,
            "probe": BATCH,
            "note": "capacity face of the six-face canon for the 20 frozen "
                    "battery variants measured at representative-weight "
                    "scale; battery product stays byte-frozen -- this block "
                    "is the authoritative successor face (prereg s4)"},
        "adv_yearly": adv_yearly,
        "ledger": {"cells_ledger_delta": 0,
                   "note": "disclosure leg, zero judgment cells (canon "
                           "re-anchor precedent); battery 400 cells "
                           "already in ledger",
                   "ledger_total_after": ledger_head()["total"]},
        "audit": {"runtime_sec": round(time.time() - t0, 1),
                  "machine": machine_id(),
                  "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
                  "sleeve_cutoff": str(SLEEVE_CUTOFF.date()),
                  "panel_file_cutoff": str(cutoff.date()),
                  "workers": min(worker_cap(), 25),
                  "n_units": len(res),
                  "ram_free_gb": round(free_ram_gb(), 1),
                  "adv_min_periods": ADV_MIN_PERIODS,
                  "refinalize": bool(os.environ.get("AGGR_CAP_REFINALIZE"))},
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1, default=float)
    log(f"outputs: {OUT_JSON}")

    try:
        ga = json.load(open(GA_PATH, encoding="utf-8"))
        ga["entries"].append({
            "batch": BATCH,
            "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
            "kind": "capacity-disclosure (T-80 slice-4, zero re-judge)",
            "cells_ledger_delta": 0,
            "ledger_total_after": ledger_head()["total"],
            "gates": {v: variants_out[v]["capacity_label"]
                      for v in sorted(variants_out)},
            "refs": {"results": OUT_JSON, "prereg": PREREG}})
        with open(GA_PATH, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(ga, fh, ensure_ascii=False, indent=1)
    except (OSError, KeyError, json.JSONDecodeError) as exc:
        log(f"gate_attrition append skipped: {exc}")
    return 0


# --------------------------------------------------------------- selftest
def _fixture_panel(tmp, n_bars=80):
    """5-member synthetic panel (prereg-style caliber faces):
    THIN  amount 1e4  -> ADV20 1e4  -> 1% cap 100 (capped partial fill, 10bp)
    ZERO  amount 0    -> ADV20 0    -> order dropped
    MISS  amount NaN  -> ADV20 NaN  -> missing path (no cap, 10bp)
    MID   amount 2e8  -> 5bp tier
    HUGE  amount 1e9  -> 2bp tier
    Gently varying closes so low_vol_long ranking is non-degenerate."""
    idx = pd.bdate_range("2020-01-01", periods=n_bars)
    specs = {"THIN": 1e4, "ZERO": 0.0, "MISS": float("nan"),
             "MID": 2e8, "HUGE": 1e9}
    prices = {}
    for i, (s, amt) in enumerate(specs.items()):
        base = 10.0 + i
        close = pd.Series(
            [base + 0.3 * ((j % 9) - 4) + 0.01 * j for j in range(n_bars)],
            index=idx, dtype=float)
        prices[s] = pd.DataFrame({
            "open": close.shift(1).fillna(close.iloc[0]),
            "high": close + 0.2, "low": close - 0.2, "close": close,
            "volume": 1e6, "amount": amt}, index=idx)
    tdir = os.path.join(tmp, "traders")
    os.makedirs(tdir, exist_ok=True)
    with open(os.path.join(tdir, "FX.json"), "w", encoding="utf-8",
              newline="\n") as fh:
        json.dump({"id": "FX", "params": {
            "entry": "low_vol_long(n=60, top_k=5, daily)",
            "max_positions": 5, "position_size_pct": 0.10}}, fh)
    return prices, tdir


def cmd_selftest() -> int:
    import tempfile
    ok = []

    def ck(name, fn):
        try:
            fn()
            ok.append(name)
            print(f"[selftest] {name}: PASS", flush=True)
        except Exception as exc:
            print(f"[selftest] {name}: FAIL ({exc})", flush=True)
            raise

    with tempfile.TemporaryDirectory() as tmp:
        prices, tdir = _fixture_panel(tmp)

        def f1():
            """known-refusal matrix: every D5 face exercised at least once
            + the engine-contract identity sum(tiers) == num_entries
            (structural invariants, not magic numbers -- r242 gate law)."""
            r = _cap_worker(("FX", 1e6, tdir, prices))
            assert r["capped_entries"] >= 1, f"capped: {r}"
            assert r["dropped_zero_adv"] >= 1, f"zero-adv drop: {r}"
            assert r["missing_adv_executions"] >= 1, f"missing adv: {r}"
            assert r["tier_entries_2bp"] >= 1, f"2bp tier: {r}"
            assert r["tier_entries_5bp"] >= 1, f"5bp tier: {r}"
            assert r["tier_entries_10bp"] >= 2, f"10bp tiers: {r}"
            tiers = (r["tier_entries_2bp"] + r["tier_entries_5bp"]
                     + r["tier_entries_10bp"])
            assert tiers == r["num_entries"] >= 1, \
                f"tier-sum identity: {tiers} vs {r['num_entries']}"
            assert r["cost_basis"] == "v2-adv20-tiered", r["cost_basis"]

        def f2():
            """isolated zero-ADV drop: nothing opens, eq == initial."""
            pz = {s: prices[s] for s in ("ZERO",)}
            with open(os.path.join(tdir, "FZ.json"), "w", encoding="utf-8",
                      newline="\n") as fh:
                json.dump({"id": "FZ", "params": {
                    "entry": "low_vol_long(n=60, top_k=5, daily)",
                    "max_positions": 1, "position_size_pct": 1.0}}, fh)
            r = _cap_worker(("FZ", 1e6, tdir, pz))
            assert r["dropped_zero_adv"] >= 1 and r["num_entries"] == 0, r
            assert abs(r["final_eq"] - 1e6) < 1e-9, r["final_eq"]

        def f3():
            """determinism: same unit twice -> identical payload."""
            a = _cap_worker(("FX", 1e6, tdir, prices))
            b = _cap_worker(("FX", 1e6, tdir, prices))
            assert json.dumps(a, sort_keys=True) == json.dumps(b,
                                                               sort_keys=True)

        def f4():
            """scale boundary: demand 100 (scale 1000, pct .10) vs cap 100
            -> uncapped; scale 1e6 -> capped (demand 1e5 >> 100)."""
            pt = {"THIN": prices["THIN"]}
            r_small = _cap_worker(("FX", 1000.0, tdir, pt))
            r_big = _cap_worker(("FX", 1e6, tdir, pt))
            assert r_small["capped_entries"] == 0, r_small
            assert r_big["capped_entries"] >= 1, r_big

        def f5():
            """battery consumption census (real frozen product, read-only):
            20 variants / 291 pairs / 267 units / weight-sum mirror."""
            b, vmap, units = _battery_units()
            assert len(vmap) == N_VARIANTS and len(units) == N_UNITS
            assert sum(len(v) for v in vmap.values()) == N_PAIRS

        def f6():
            """caliber manifest gate on the real snapshot (read-only)."""
            n = _caliber_manifest_gate()
            assert n >= 29, n

        def f7():
            """core48 integration smoke: 1 real sleeve at w=0.5 scale on the
            real truncated panel; V2 basis engaged; deterministic counters
            are NOT asserted beyond structural faces (reading is the run's
            face, not selftest's)."""
            prices_full = load_core()
            pc = {s: df[df.index <= SLEEVE_CUTOFF]
                  for s, df in prices_full.items()}
            r = _cap_worker(("COMPOSITE-CE-01", 0.5 * SCALE_CNY,
                             T56_CALIBER_DIR, pc))
            assert r["cost_basis"] == "v2-adv20-tiered", r
            assert r["num_entries"] > 0, r
            assert r["scale_cny"] == 0.5 * SCALE_CNY, r

        def f8():
            """ADV yearly table on synthetic panel: 2020 medians per face."""
            t = _adv_yearly_table(prices)
            assert t["HUGE"]["2020"]["median"] >= ADV20_TIER_2BP_YUAN, t
            assert t["MID"]["2020"]["median"] >= ADV20_TIER_5BP_YUAN, t
            assert t["THIN"]["2020"]["cap1pct_median"] == 100.0, t
            assert "MISS" not in t or not t.get("MISS", {}), t

        ck("F1 known-refusal matrix", f1)
        ck("F2 zero-ADV drop isolation", f2)
        ck("F3 determinism", f3)
        ck("F4 scale boundary", f4)
        ck("F5 battery consumption census", f5)
        ck("F6 caliber manifest gate", f6)
        ck("F7 core48 integration smoke", f7)
        ck("F8 ADV yearly table", f8)
    print(f"selftest: {len(ok)}/{len(ok)} PASS", flush=True)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("run", "selftest"))
    ns = ap.parse_args()
    return cmd_selftest() if ns.cmd == "selftest" else cmd_run()


if __name__ == "__main__":
    sys.exit(main())
