"""T-18 deep-axis machinery -- infra leg (gates + build), frozen prereg
research/DEEP_AXIS_REVALIDATION.md s2/s6 (r97 freeze, sha256 5cdea03e...).

gates: GA twin/bare overlap parity 48/48 (|dclose| tol 0, spotcheck 3/3
      upgraded to full-population), GB per-member completeness (warmup=252,
      valid rows >=252, close NaN <0.5%, dates strictly monotonic, zero rows
      after evidence_cutoff), GC bars anchor Money02/data/bars ==10444 files,
      GD break-registry re-derive bit-match (t14 build_guard chain),
      GE manifest deterministic freeze (panel_start gate-computed from the
      >=5-valid-member rule -- 手写禁 per prereg), GF adjusted-view hard-gate
      STATE PROBE (record-only here; blocks nulls/reval/pbo runs per
      O-1310 s3; gates/build infra unblocked).
build: growing-membership panel cache -> Money02/data/cache/t18_deep_panel/
      (gitignored, regenerable). Twin sources truncated at evidence_cutoff;
      bare-code files are never touched (anchor-reproduction law).
nulls: K=50 deep-axis null regeneration (prereg SS3, GF-gated) -- p2
      family-A machinery reuse (random Bernoulli entry matrix x engine
      exits, seeds 54_000+k, p regimes {0.02, 0.05}) masked to warmup-valid
      members on the axis window (panel_start..cutoff); passive family-C
      reuse (EW48 monthly rebal + buy-hold on the twin panel). Checkpoint
      resume via t18_deep_nulls_runs.jsonl (manifest-sha keyed); finalize
      -> results/shortline/t18_deep_nulls.json + R53 live dual-pool probe.
      No ledger append (batch-level accounting at reval finalize, SS3).
reval/pbo: GF + XSTOCK data-dir mutex checked first; blocked = exit 2
      (implementation rounds pending).
status/selftest.

Exit codes: 0 = pass / no-op, 1 = gate fail / refused, 2 = stage blocked
(GF hard gate, XSTOCK mutex, or machinery pending implementation rounds).
"""
from __future__ import annotations

import glob
import hashlib
import json
import os
import sys
import time

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)   # engine/ + scripts.x imports under `python scripts/...` (p2 precedent)
DAILY = os.path.join(ROOT, "data", "daily")
MANIFEST_PATH = os.path.join(ROOT, "results", "shortline", "t18_deep_manifest.json")
CACHE_DIR = os.path.join(ROOT, "Money02", "data", "cache", "t18_deep_panel")
BARS_DIR = os.path.join(ROOT, "Money02", "data", "bars")
REGISTRY_PATH = os.path.join(ROOT, "data", "consolidation", "registry.json")
T19_TICKET_PATH = os.path.join(ROOT, "fleet", "tasks", "T-20260924-19-P1.json")
ORDERS_DIR = os.path.join(ROOT, "fleet", "orders")
ADJUST_DIR = os.path.join(ROOT, "data", "consolidation")  # T-19 stage-3 face

# Frozen prereg constants (research/DEEP_AXIS_REVALIDATION.md s2 -- do not tune).
WARMUP_BARS = 252          # covers high252 / mom_12_1 max lookback of all 6 traders
MIN_Z_NAMES = 5            # cross-section validity floor (MIN_Z_NAMES=5 precedent)
EVIDENCE_CUTOFF = "2026-09-22"   # twin-data measured end == registry anchor cutoff
BARS_ANCHOR = 10444        # Money02/data/bars total file count (T-01 chain)
NAN_RATE_MAX = 0.005       # per-member close NaN rate ceiling
VALID_ROWS_MIN = 252      # effective rows after warmup floor
PREREG_SHA = "5cdea03e48933d219aea7d666d8cc808b84c70d4b66fe062cee7dd35bbab309d"


def _twin_prefix(code: str) -> str:
    return "sz" if code.startswith(("0", "1", "3")) else "sh"


def _twin_path(code: str) -> str:
    return os.path.join(DAILY, _twin_prefix(code) + code + ".csv")


def _read_daily(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    return df.rename(columns={c: c.strip() for c in df.columns})


def _universe() -> list[str]:
    """core48 caliber: bare 6-digit CSVs with >=60 rows (live.paper listing floor)."""
    out = []
    for f in sorted(os.listdir(DAILY)):
        if not (f.endswith(".csv") and f[:-4].isdigit()):
            continue
        n = sum(1 for _ in open(os.path.join(DAILY, f), encoding="utf-8")) - 1
        if n >= 60:
            out.append(f[:-4])
    return out


def _gate_ga(codes: list[str]) -> tuple[bool, dict]:
    rows, worst = [], 0.0
    for code in codes:
        bare = _read_daily(os.path.join(DAILY, code + ".csv")).set_index("date")["close"]
        twin = _read_daily(_twin_path(code)).set_index("date")["close"]
        common = bare.index.intersection(twin.index)
        if len(common) == 0:
            rows.append({"code": code, "common_rows": 0, "max_abs_close_diff": None, "pass": False})
            continue
        diff = float((bare.loc[common] - twin.loc[common]).abs().max())
        worst = max(worst, diff)
        rows.append({"code": code, "common_rows": int(len(common)),
                     "max_abs_close_diff": diff, "pass": diff == 0.0})
    ok = bool(rows) and all(r["pass"] for r in rows)
    return ok, {"pass": ok, "n_checked": len(rows), "tolerance": 0.0,
                "max_abs_close_diff_worst": worst, "per_member": rows}


def _gate_gb(codes: list[str]) -> tuple[bool, dict]:
    members, ok = {}, True
    for code in codes:
        twin = _read_daily(_twin_path(code))
        dates = twin["date"].astype(str).tolist()
        rows = len(twin)
        mono = all(dates[i] < dates[i + 1] for i in range(len(dates) - 1))
        nan_rate = float(twin["close"].isna().mean())
        after_cut = sum(1 for d in dates if d > EVIDENCE_CUTOFF)
        valid_from = dates[WARMUP_BARS] if rows > WARMUP_BARS else None
        valid_rows = rows - WARMUP_BARS if rows > WARMUP_BARS else 0
        member_ok = (mono and nan_rate < NAN_RATE_MAX and after_cut == 0
                     and valid_rows >= VALID_ROWS_MIN)
        ok = ok and member_ok
        members[code] = {
            "twin_start": dates[0], "twin_end": dates[-1], "rows": rows,
            "valid_from": valid_from, "valid_rows": valid_rows,
            "nan_rate": nan_rate, "dates_mono": mono,
            "rows_after_cutoff": after_cut, "pass": member_ok,
        }
    return ok, {"pass": ok, "members": members}


def _gate_gc() -> tuple[bool, dict]:
    if not os.path.isdir(BARS_DIR):
        return False, {"pass": False, "bars_files": None, "error": "bars dir absent"}
    files = [f for f in os.listdir(BARS_DIR) if os.path.isfile(os.path.join(BARS_DIR, f))]
    n_pq = sum(1 for f in files if f.endswith(".parquet"))
    info = {"pass": len(files) == BARS_ANCHOR, "bars_files": len(files),
            "parquet_files": n_pq, "anchor": BARS_ANCHOR}
    return info["pass"], info


def _gd_compare(registry_path: str, derived_canon: list) -> dict:
    """Pure comparison leg of GD (registry file vs re-derived canon)."""
    reg = json.load(open(registry_path, encoding="utf-8-sig"))
    events = reg.get("events", [])
    # registry face stores the detector 4dp value (pct_detector_4dp); the
    # t14-derived face uses "pct" -- both canon to pct@4dp (t19 build law)
    reg_canon = sorted((e["sym"], e["date"],
                        round(float(e.get("pct", e.get("pct_detector_4dp"))), 4))
                       for e in events)
    n_pre = sum(1 for _, d, _ in reg_canon if d[:4] < "2020")
    return {
        "registry_events": len(events),
        "derived_events": len(derived_canon),
        "bit_match": reg_canon == list(derived_canon),
        "n_pre_2020": n_pre,
        "first_event": min((d for _, d, _ in reg_canon), default=None),
        "last_event": max((d for _, d, _ in reg_canon), default=None),
    }


def _gate_gd() -> tuple[bool, dict]:
    _repo = ROOT
    if _repo not in sys.path:
        sys.path.insert(0, _repo)
    import live.paper as LP
    from scripts.t14_rules_fidelity import build_guard
    from scripts.t19_consolidation_registry import _canon

    prices = LP.load_core()
    _, diag = build_guard(prices)
    tot = diag["totals"]
    derived = _canon(diag["break_days"])
    cmp_ = _gd_compare(REGISTRY_PATH, derived)
    ok = (cmp_["bit_match"] and tot["break_days"] == 21
          and tot["break_days_distinct_syms"] == 19 and cmp_["n_pre_2020"] == 0)
    info = {"pass": ok, "detector": "t14 build_guard re-derive -> _canon bit-match",
            "totals": {"break_days": tot["break_days"],
                       "break_days_distinct_syms": tot["break_days_distinct_syms"]},
            **cmp_}
    return ok, info


def _panel_start(members: dict) -> str | None:
    """First trading day with >= MIN_Z_NAMES warmup-valid members (gate-computed)."""
    starts = sorted(m["valid_from"] for m in members.values() if m["valid_from"])
    for d in starts:
        n = sum(1 for m in members.values() if m["valid_from"] and m["valid_from"] <= d)
        if n >= MIN_Z_NAMES:
            return d
    return None


def _gf_state() -> dict:
    """O-1310 s3 literal: T-19 adjusted view delivered (files on disk + ticket
    note delivery marker) OR GM waiver in an O-file -- else nulls/reval/pbo exit 2."""
    basis: dict = {}
    adj_files = sorted(glob.glob(os.path.join(ADJUST_DIR, "adjust*")))
    basis["adjusted_files_on_disk"] = [os.path.basename(f) for f in adj_files]
    note = ""
    try:
        note = json.load(open(T19_TICKET_PATH, encoding="utf-8-sig")).get("note", "")
    except Exception as e:  # honest: unreadable ticket recorded, not fatal for probe
        basis["t19_note_error"] = str(e)[:120]
    low = note.lower()
    basis["t19_note_stage3_delivered_marker"] = (
        "stage-3 delivered" in low or "stage-3 adjusted panel delivered" in low)
    waiver_lines = []
    for f in sorted(glob.glob(os.path.join(ORDERS_DIR, "O-*.md"))):
        try:
            txt = open(f, encoding="utf-8-sig").read()
        except Exception:
            continue
        for ln in txt.splitlines():
            l = ln.lower()
            if ("豁免" in ln or "waiver" in l) and any(
                    k in l for k in ("t-18", "t18", "deep axis", "deep-axis",
                                     "deep_axis", "deep reval", "deep_reval")):
                waiver_lines.append(os.path.basename(f) + ": " + ln.strip()[:160])
    basis["gm_waiver_lines"] = waiver_lines
    delivered = bool(adj_files) and basis["t19_note_stage3_delivered_marker"]
    waiver = bool(waiver_lines)
    return {
        "satisfied": delivered or waiver,
        "delivered": delivered,
        "gm_waiver": waiver,
        "basis": basis,
        "contract": "nulls/reval/pbo stages exit 2 until satisfied (O-1310 s3); "
                    "gates/build infra unblocked",
    }


def _xstock_mutex() -> tuple[bool, str]:
    """s0 compute-budget law: heavy stages must not ignite while the XSTOCK
    build/post chain holds the shared data dirs (Money02 cache contention)."""
    try:
        import psutil
    except ImportError:
        return True, "psutil unavailable (fail-safe block)"
    for p in psutil.process_iter(["pid", "cmdline"]):
        try:
            cl = " ".join(p.info.get("cmdline") or [])
        except Exception:
            continue
        if "xstock_synth.py" in cl and " run" in cl:
            return True, f"xstock_synth run in flight (PID {p.info['pid']})"
    return False, ""


def _compute_gates() -> tuple[bool, dict]:
    codes = _universe()
    ga_ok, ga = _gate_ga(codes)
    gb_ok, gb = _gate_gb(codes)
    gc_ok, gc = _gate_gc()
    gd_ok, gd = _gate_gd()
    panel_start = _panel_start(gb["members"])
    gf = _gf_state()
    payload = {
        "batch": "t18_deep_reval",
        "stage": "gates",
        "prereg": f"research/DEEP_AXIS_REVALIDATION.md (frozen sha256 {PREREG_SHA})",
        "universe_n": len(codes),
        "warmup_bars": WARMUP_BARS,
        "min_z_names": MIN_Z_NAMES,
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "panel_start": panel_start,
        "members": gb["members"],
        "gates": {"GA": ga, "GB": {"pass": gb_ok}, "GC": gc, "GD": gd, "GF": gf},
        "verdict": "PASS" if (ga_ok and gb_ok and gc_ok and gd_ok
                              and panel_start and len(codes) == 48) else "FAIL",
    }
    ok = payload["verdict"] == "PASS"
    # GE determinism: recompute the whole payload and demand byte-equality.
    ga2_ok, ga2 = _gate_ga(codes)
    gb2_ok, gb2 = _gate_gb(codes)
    gc2_ok, gc2 = _gate_gc()
    ps2 = _panel_start(gb2["members"])
    payload2 = dict(payload)
    payload2["gates"] = {"GA": ga2, "GB": {"pass": gb2_ok}, "GC": gc2,
                         "GD": gd, "GF": _gf_state()}
    payload2["members"] = gb2["members"]
    payload2["panel_start"] = ps2
    same = json.dumps(payload, sort_keys=True) == json.dumps(payload2, sort_keys=True)
    payload["ge_determinism_double_run"] = same
    if not same:
        payload["verdict"] = "FAIL"
        ok = False
    return ok, payload


def cmd_gates() -> int:
    ok, payload = _compute_gates()
    os.makedirs(os.path.dirname(MANIFEST_PATH), exist_ok=True)
    with open(MANIFEST_PATH, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    print(json.dumps({k: payload[k] for k in
                      ("universe_n", "panel_start", "evidence_cutoff", "verdict",
                       "ge_determinism_double_run")}, ensure_ascii=False))
    for g in ("GA", "GB", "GC", "GD", "GF"):
        info = payload["gates"][g]
        print(f"[gate {g}] pass={info.get('pass', info.get('satisfied'))}")
    print("manifest written:", MANIFEST_PATH)
    return 0 if ok else 1


def _manifest_sha() -> str:
    return hashlib.sha256(open(MANIFEST_PATH, "rb").read()).hexdigest()


def cmd_build() -> int:
    if not os.path.exists(MANIFEST_PATH):
        print("[build] manifest absent -- running gates first")
        rc = cmd_gates()
        if rc != 0:
            return rc
    man = json.load(open(MANIFEST_PATH, encoding="utf-8"))
    if man.get("verdict") != "PASS":
        print("[build] manifest verdict != PASS; rebuild refused")
        return 1
    msha = _manifest_sha()
    meta_path = os.path.join(CACHE_DIR, "meta.json")
    ohlcv_dir = os.path.join(CACHE_DIR, "ohlcv")
    if os.path.exists(meta_path):
        try:
            meta = json.load(open(meta_path, encoding="utf-8-sig"))
            done = (meta.get("manifest_sha256") == msha
                    and all(os.path.exists(os.path.join(ohlcv_dir, c + ".parquet"))
                            for c in man["members"]))
            if done:
                print(f"[build] no-op: cache fresh for manifest {msha[:12]} "
                      f"({len(man['members'])} members)")
                return 0
        except Exception as e:
            print("[build] stale meta read:", str(e)[:120])
    os.makedirs(ohlcv_dir, exist_ok=True)
    n_rows = 0
    for code, m in sorted(man["members"].items()):
        df = _read_daily(_twin_path(code))
        df = df.set_index("date").sort_index()
        df = df.loc[df.index <= EVIDENCE_CUTOFF]  # cutoff 后新 bar 锁定不回流
        df[["open", "high", "low", "close", "volume"]].to_parquet(
            os.path.join(ohlcv_dir, code + ".parquet"))
        n_rows += len(df)
    meta = {
        "manifest_sha256": msha,
        "warmup_bars": WARMUP_BARS,
        "min_z_names": MIN_Z_NAMES,
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "members": len(man["members"]),
        "rows_total": n_rows,
        "panel_start": man["panel_start"],
        "source": "twin files (bare-code files untouched; anchor-reproduction law)",
    }
    with open(meta_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(meta, fh, ensure_ascii=False, indent=1)
    print(f"[build] panel cache written: {ohlcv_dir} ({len(man['members'])} members, "
          f"{n_rows} rows, panel_start {man['panel_start']})")
    return 0


# ------------------------------------------------------- nulls stage (prereg SS3)

NULLS_K = 50                 # K=50 frozen (prereg SS3)
NULLS_P = (0.02, 0.05)       # p2 family-A entry-frequency regimes (machinery reuse)
NULLS_SEED_BASE = 54_000     # SEED_REGISTRY["t18_deep_axis"] (54_000+i, i=0..49)
NULLS_RUNS_PATH = os.path.join(ROOT, "results", "shortline",
                               "t18_deep_nulls_runs.jsonl")
NULLS_OUT_PATH = os.path.join(ROOT, "results", "shortline",
                              "t18_deep_nulls.json")

_NW: dict = {}   # per-worker initialized state (spawn fresh import on Windows)


def _panel_inputs(man: dict):
    """prices dict + union calendar + warmup-valid mask, from the frozen panel
    cache (full twin history, cutoff-truncated; bare-code files untouched).
    DatetimeIndex faces mirror p2 load_core so the reused machinery is
    byte-faithful (p2 ran bare CSVs with parse_dates)."""
    ohlcv_dir = os.path.join(CACHE_DIR, "ohlcv")
    prices = {}
    for f in sorted(os.listdir(ohlcv_dir)):
        if not f.endswith(".parquet"):
            continue
        df = pd.read_parquet(os.path.join(ohlcv_dir, f))
        if "date" in df.columns:
            df = df.set_index("date")
        df = df.sort_index()
        df.index = pd.to_datetime(df.index.astype(str))
        prices[f[:-len(".parquet")]] = df[
            ["open", "high", "low", "close", "volume"]].assign(
            amount=df["volume"] * df["close"])  # p2 load_core convention
    closes = pd.DataFrame({s: d["close"] for s, d in prices.items()}).sort_index()
    idx, syms = closes.index, list(closes.columns)
    valid = pd.DataFrame(False, index=idx, columns=syms)
    for code, m in man["members"].items():
        if code in syms and m.get("valid_from"):
            valid[code] = valid.index >= m["valid_from"]
    axis_ok = pd.Series(idx >= pd.Timestamp(man["panel_start"]), index=idx)
    mask = valid.where(axis_ok, other=False)  # entries only on-axis + valid
    return prices, idx, syms, mask


def _nulls_worker_init():
    import psutil
    pri = getattr(psutil, "BELOW_NORMAL_PRIORITY_CLASS", None)
    if pri is not None:
        try:
            psutil.Process().nice(pri)   # O-1136 full-load low-priority pool
        except Exception:
            pass
    man = json.load(open(MANIFEST_PATH, encoding="utf-8"))
    prices, idx, syms, mask = _panel_inputs(man)
    _NW.update(prices=prices, idx=idx, syms=syms, mask=mask,
               panel_start=man["panel_start"])


def _nulls_run_one(k: int) -> dict:
    """One deep-axis null: random Bernoulli entry matrix (seed 54_000+k,
    p regime alternating per p2 family-A) masked to warmup-valid members on
    the axis window; exits = engine rules only (params={} registered defaults).
    Full-axis reading = Sharpe over the equity segment from panel_start."""
    import time as _t
    from engine import run_backtest
    from engine.metrics import sharpe, annual_return, max_drawdown

    prices, idx, syms = _NW["prices"], _NW["idx"], _NW["syms"]
    mask, panel_start = _NW["mask"], _NW["panel_start"]
    p = NULLS_P[k % 2]
    rng = np.random.default_rng(NULLS_SEED_BASE + k)
    entry = pd.DataFrame(
        ((rng.random((len(idx), len(syms))) < p) & mask.to_numpy()).astype(int),
        index=idx, columns=syms)
    exit_ = pd.DataFrame(False, index=idx, columns=syms)
    t0 = _t.time()
    res = run_backtest(prices, {}, entry_signal=entry, exit_signal=exit_)
    eq = pd.Series(res["equity_curve"], index=idx[:len(res["equity_curve"])])
    seg = eq[eq.index >= panel_start]           # deep-axis window reading
    if len(seg) < 20:
        full_axis = {"sharpe": 0.0, "annual_return": 0.0, "max_drawdown": 0.0}
    else:
        full_axis = {"sharpe": round(float(sharpe(seg)), 4),
                     "annual_return": round(float(annual_return(seg)), 4),
                     "max_drawdown": round(float(max_drawdown(seg)), 4)}
    return {"k": k, "p": p, "seed": NULLS_SEED_BASE + k,
            "sharpe_full_axis": full_axis["sharpe"],
            "full_axis": full_axis,
            "n_trades": int(res["metrics"].get("num_trades", 0)),
            "n_days_axis": int(len(seg)),
            "elapsed_sec": round(_t.time() - t0, 1)}


def _nulls_resume(msha: str) -> dict:
    """Done-set from the checkpoint jsonl; manifest-sha keyed so a panel
    rebuild invalidates stale rows (census-drift law, r105)."""
    done: dict = {}
    if not os.path.exists(NULLS_RUNS_PATH):
        return done
    with open(NULLS_RUNS_PATH, encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if not ln:
                continue
            try:
                rec = json.loads(ln)
            except ValueError:
                continue
            if (isinstance(rec, dict) and rec.get("ok")
                    and rec.get("manifest_sha") == msha
                    and isinstance(rec.get("k"), int)
                    and 0 <= rec["k"] < NULLS_K):
                done[rec["k"]] = rec
    return done


def _seg_metrics_axis(eq: pd.Series, panel_start: str) -> dict:
    seg = eq[eq.index >= panel_start]
    if len(seg) < 20:
        return {"sharpe": 0.0, "annual_return": 0.0, "max_drawdown": 0.0}
    from engine.metrics import sharpe, annual_return, max_drawdown
    return {"sharpe": round(float(sharpe(seg)), 4),
            "annual_return": round(float(annual_return(seg)), 4),
            "max_drawdown": round(float(max_drawdown(seg)), 4)}


def _dual_pool_probe(payload: dict, batch_cells: int) -> dict:
    """R53 law: the science_gates t18_deep_axis additive branch is accepted by
    a LIVE dual-pool comparison recorded in the product file -- deep line must
    read the deep file's mu/sigma/passive; core48 line must stay on the
    pre-existing p2_calibration collector face (zero cross-contamination)."""
    from scripts.science_gates import skill_line_v2, null_sharpes
    deep = skill_line_v2(batch_cells=batch_cells, pool="t18_deep_axis",
                          null_pool=payload["null_pool"])
    core = skill_line_v2(batch_cells=batch_cells, pool="core48")
    cov = payload["null_pool"]["coverage"]
    pas_deep = max(payload["passive"]["ew48_buyhold"]["full_axis"]["sharpe"],
                   payload["passive"]["ew48_monthly_rebal"]["full_axis"]["sharpe"])
    core_cov = null_sharpes()["coverage"]
    deep_ok = (deep["pool"] == "t18_deep_axis"
               and abs(deep["mu_null"] - cov["mu"]) < 5e-4
               and abs(deep["sigma_null"] - cov["sigma"]) < 5e-4
               and abs(deep["passive_term"] - round(pas_deep + 0.10, 4)) < 5e-4)
    core_ok = (core["pool"] == "core48"
               and abs(core["mu_null"] - core_cov["mu"]) < 5e-4
               and abs(core["sigma_null"] - core_cov["sigma"]) < 5e-4)
    return {"law": "R53 live dual-pool probe (branch acceptance, not selftest)",
            "deep_line": deep, "core48_line": core,
            "deep_inputs_match_file": bool(deep_ok),
            "core48_face_untouched": bool(core_ok),
            "pass": bool(deep_ok and core_ok),
            "probe_n_eff_basis": f"batch_cells={batch_cells} (nulls+passive "
                                  f"probe basis; reval finalize re-derives the "
                                  f"line with the full batch cell count, SS3)"}


def _nulls_finalize(man: dict, msha: str, done: dict, workers: int,
                    elapsed: float) -> int:
    from scripts.p2_null_calibration import (passive_buyhold,
                                             passive_monthly_rebal)
    from knowledge.rules import FeeSchedule

    prices, idx, syms, mask = _panel_inputs(man)
    closes = pd.DataFrame({s: d["close"] for s, d in prices.items()}
                          ).sort_index().ffill()   # p2 passive convention
    fee = FeeSchedule()
    cost_rate = (fee.commission_rate + fee.handling_fee +
                 fee.supervision_fee + fee.slippage_a)
    ps = man["panel_start"]
    bh = passive_buyhold(closes, cost_rate)
    mr = passive_monthly_rebal(closes, cost_rate)
    passive_block = {
        "ew48_buyhold": {"full_axis": _seg_metrics_axis(bh, ps), "n_trades": 0},
        "ew48_monthly_rebal": {"full_axis": _seg_metrics_axis(mr, ps),
                               "n_trades": 0},
        "note": "p2 family-C reuse on the deep twin panel (cash before "
                "listing); strict-max defines the pool passive; window "
                f"{ps}..{EVIDENCE_CUTOFF}",
    }
    values = [done[k]["sharpe_full_axis"] for k in range(NULLS_K)]
    mu = sum(values) / len(values)
    var = sum((v - mu) ** 2 for v in values) / (len(values) - 1)
    sigma = var ** 0.5
    srt = sorted(values)
    trades = [done[k]["n_trades"] for k in range(NULLS_K)]
    st = sorted(trades)
    n_med = st[len(st) // 2]
    axis_days = int(done[0].get("n_days_axis") or 0)
    payload = {
        "batch": "t18_deep_reval",
        "stage": "nulls",
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "prereg": f"research/DEEP_AXIS_REVALIDATION.md (frozen sha256 {PREREG_SHA})",
        "evidence_cutoff": EVIDENCE_CUTOFF,   # top-level C2 key (science_audit)
        "manifest_sha256": msha,
        "panel": {"panel_start": ps, "evidence_cutoff": EVIDENCE_CUTOFF,
                  "members": len(man["members"]),
                  "axis_days": axis_days,
                  "axis_years": round(axis_days / 252, 2),
                  "source": "twin cache Money02/data/cache/t18_deep_panel "
                            "(bare-code files untouched; anchor law)"},
        "null_pool": {"values": values,
                      "coverage": {"n_values": len(values),
                                   "mu": round(mu, 6), "sigma": round(sigma, 6),
                                   "schemas_parsed": [
                                       "t18_deep_nulls_runs.jsonl: seeds "
                                       "54_000+k random-entry x engine-exit "
                                       "nulls (deep-axis window Sharpe)"],
                                   "known_unparsed": []}},
        "passive": passive_block,
        "seeds": {"base": NULLS_SEED_BASE, "k": NULLS_K,
                  "p_regimes": list(NULLS_P),
                  "registry": "SEED_REGISTRY['t18_deep_axis'] (54_000+i, i=0..49)"},
        "machinery": "p2_null_calibration family-A reuse (Bernoulli entry "
                     "matrix x engine exits, params={} registered defaults) "
                     "masked to warmup-valid members on-axis; passive "
                     "family-C reuse on the twin panel",
        "four_mandatory_fields": {
            "null_median_trades": n_med,
            "covered_years": round(axis_days / 252, 2),
            "independent_regime_windows": axis_days // 63,
            "ci_width_empirical_p95_null_sharpes": round(
                srt[int(0.975 * (len(srt) - 1))]
                - srt[int(0.025 * (len(srt) - 1))], 4),
            "note": "null-family disclosure face (empirical p2.5-p97.5 "
                    "spread, not a bootstrap CI); per-trader faces (IS2 "
                    "trades, bootstrap CI width) land at the reval stage "
                    "per prereg SS4",
        },
        "audit": {"workers": workers, "elapsed_sec": round(elapsed, 1),
                  "n_backtests": NULLS_K, "n_passive": 2,
                  "ledger_appended": False,
                  "note": "batch-level ledger accounting happens once at the "
                          "reval finalize (prereg SS3); nulls stage product "
                          "is an intermediate face of T18_DEEP_REVAL"},
    }
    os.makedirs(os.path.dirname(NULLS_OUT_PATH), exist_ok=True)
    with open(NULLS_OUT_PATH, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    probe = _dual_pool_probe(payload, NULLS_K + 2)
    payload["r53_dual_pool_probe"] = probe
    with open(NULLS_OUT_PATH, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    print(f"[nulls] finalize: mu={round(mu, 4)} sigma={round(sigma, 4)} "
          f"K={NULLS_K} passive_bh={passive_block['ew48_buyhold']['full_axis']['sharpe']} "
          f"passive_mr={passive_block['ew48_monthly_rebal']['full_axis']['sharpe']}")
    print(f"[nulls] R53 dual-pool probe: pass={probe['pass']} "
          f"deep_line={probe['deep_line']['line']} core48_line={probe['core48_line']['line']}")
    print("saved:", NULLS_OUT_PATH)
    return 0 if probe["pass"] else 1


def cmd_nulls() -> int:
    gf = _gf_state()
    if not gf["satisfied"]:
        print(f"[nulls] BLOCKED by GF adjusted-view hard gate (O-1310 s3): "
              f"delivered={gf['delivered']} waiver={gf['gm_waiver']}")
        return 2
    busy, why = _xstock_mutex()
    if busy:
        print(f"[nulls] BLOCKED by XSTOCK data-dir mutex (s0): {why}")
        return 2
    if not os.path.exists(MANIFEST_PATH):
        print("[nulls] manifest absent -- run gates first")
        return 2
    man = json.load(open(MANIFEST_PATH, encoding="utf-8"))
    if man.get("verdict") != "PASS":
        print("[nulls] manifest verdict != PASS; refused")
        return 2
    msha = _manifest_sha()
    meta_path = os.path.join(CACHE_DIR, "meta.json")
    if not os.path.exists(meta_path):
        print("[nulls] panel cache absent -- run build first")
        return 2
    meta = json.load(open(meta_path, encoding="utf-8-sig"))
    if meta.get("manifest_sha256") != msha:
        print("[nulls] panel cache stale for manifest -- run build first")
        return 2
    try:
        import psutil
    except ImportError:
        print("[nulls] psutil unavailable (fail-safe block, s0 budget law)")
        return 2
    cores = psutil.cpu_count() or 4
    free_gb = psutil.virtual_memory().available / (1024 ** 3)
    workers = max(1, min(int(cores * 0.8), int(free_gb / 0.5), NULLS_K))  # SS0
    done = _nulls_resume(msha)
    pending = [k for k in range(NULLS_K) if k not in done]
    print(f"[nulls] seeds {NULLS_SEED_BASE}+k K={NULLS_K} p={NULLS_P} axis "
          f"{man['panel_start']}..{EVIDENCE_CUTOFF}; done={len(done)} "
          f"pending={len(pending)} workers={workers} "
          f"(cores={cores} free_gb={round(free_gb, 1)})")
    t0 = time.time()
    if pending:
        from concurrent.futures import ProcessPoolExecutor, as_completed
        with ProcessPoolExecutor(max_workers=workers,
                                 initializer=_nulls_worker_init) as ex:
            futs = {ex.submit(_nulls_run_one, k): k for k in pending}
            for fut in as_completed(futs):
                rec = fut.result()  # engine crash = honest abort, checkpoint kept
                with open(NULLS_RUNS_PATH, "a", encoding="utf-8",
                          newline="\n") as fh:
                    fh.write(json.dumps({**rec, "manifest_sha": msha,
                                         "ok": True},
                                        ensure_ascii=False) + "\n")
                done[rec["k"]] = rec
                print(f"[nulls {len(done)}/{NULLS_K}] k={rec['k']} "
                      f"p={rec['p']} sharpe={rec['sharpe_full_axis']} "
                      f"n_trades={rec['n_trades']} ({rec['elapsed_sec']}s)",
                      flush=True)
    if len(done) < NULLS_K:
        print(f"[nulls] incomplete: {len(done)}/{NULLS_K} -- checkpoint "
              f"preserved for resume; honest partial, no finalize")
        return 1
    return _nulls_finalize(man, msha, done, workers, time.time() - t0)


def _blocked_stage(name: str) -> int:
    gf = _gf_state()
    if not gf["satisfied"]:
        print(f"[{name}] BLOCKED by GF adjusted-view hard gate (O-1310 s3): "
              "T-19 stage-3 not delivered and no GM waiver on file")
        print(f"[{name}] gf basis: files={gf['basis']['adjusted_files_on_disk']} "
              f"note_marker={gf['basis']['t19_note_stage3_delivered_marker']} "
              f"waiver_lines={gf['basis']['gm_waiver_lines']}")
        return 2
    busy, why = _xstock_mutex()
    if busy:
        print(f"[{name}] BLOCKED by XSTOCK data-dir mutex (s0): {why}")
        return 2
    print(f"[{name}] GF satisfied and mutex clear, but stage machinery is pending "
          "implementation rounds (r101 delivered gates/build only); refusing to fake a run")
    return 2


def cmd_status() -> int:
    if os.path.exists(MANIFEST_PATH):
        man = json.load(open(MANIFEST_PATH, encoding="utf-8"))
        print(json.dumps({k: man.get(k) for k in
                          ("verdict", "universe_n", "panel_start", "evidence_cutoff",
                           "ge_determinism_double_run")}, ensure_ascii=False))
    else:
        print("manifest absent (run: python scripts/t18_deep_axis.py gates)")
    gf = _gf_state()
    print("GF:", json.dumps({"satisfied": gf["satisfied"], "delivered": gf["delivered"],
                             "gm_waiver": gf["gm_waiver"]}, ensure_ascii=False))
    meta_path = os.path.join(CACHE_DIR, "meta.json")
    if os.path.exists(meta_path):
        meta = json.load(open(meta_path, encoding="utf-8-sig"))
        fresh = meta.get("manifest_sha256") == (_manifest_sha()
                                                if os.path.exists(MANIFEST_PATH) else None)
        print("cache:", json.dumps({**meta, "fresh_for_manifest": fresh},
                                   ensure_ascii=False))
    else:
        print("cache: absent")
    return 0


def _selftest() -> int:
    import tempfile
    tmp = tempfile.mkdtemp(prefix="t18gates_")
    fake = os.path.join(tmp, "daily")
    os.makedirs(fake)
    # 7 synthetic members, staggered twin starts, constant close=1.0
    starts = ["2010-01-0" + str(i + 1) for i in range(7)]
    for i, s in enumerate(starts):
        code = f"51000{i}"
        idx = pd.bdate_range(s, "2020-01-01")
        pd.DataFrame({"date": idx.strftime("%Y-%m-%d"), "open": 1.0, "high": 1.0,
                      "low": 1.0, "close": 1.0, "volume": 1.0,
                      }).to_csv(os.path.join(fake, code + ".csv"), index=False)
        pd.DataFrame({"date": idx.strftime("%Y-%m-%d"), "open": 1.0, "high": 1.0,
                      "low": 1.0, "close": 1.0, "volume": 1.0,
                      }).to_csv(os.path.join(fake, "sh" + code + ".csv"), index=False)
    import t18_deep_axis as mod
    mod.DAILY = fake

    def chk(name, cond):
        assert cond, f"selftest FAIL: {name}"
        print(f"  [ok] {name}")

    codes = [f"51000{i}" for i in range(7)]
    ga_ok, ga = mod._gate_ga(codes)
    chk("GA parity all-zero on synthetic", ga_ok and ga["n_checked"] == 7
        and ga["max_abs_close_diff_worst"] == 0.0)
    # GA violation case: corrupt one twin close
    bad = pd.read_csv(os.path.join(fake, "sh510000.csv"))
    bad.loc[3, "close"] = 9.9
    bad.to_csv(os.path.join(fake, "sh510000.csv"), index=False)
    ga2_ok, ga2 = mod._gate_ga(codes)
    chk("GA catches corrupted twin", not ga2_ok
        and ga2["per_member"][0]["pass"] is False)
    pd.read_csv(os.path.join(fake, "sh510000.csv")).assign(
        close=1.0).to_csv(os.path.join(fake, "sh510000.csv"), index=False)

    gb_ok, gb = mod._gate_gb(codes)
    chk("GB pass on synthetic long twins", gb_ok
        and all(m["valid_rows"] >= mod.VALID_ROWS_MIN for m in gb["members"].values()))
    m0 = gb["members"]["510000"]
    chk("GB valid_from = twin_start + 252 bars",
        m0["valid_from"] == pd.bdate_range(starts[0], periods=253)[-1].strftime("%Y-%m-%d"))
    # GB violation: rows-after-cutoff on one twin
    bad = pd.read_csv(os.path.join(fake, "sh510001.csv"))
    bad.loc[len(bad)] = ["2026-09-23", 1.0, 1.0, 1.0, 1.0, 1.0]
    bad.to_csv(os.path.join(fake, "sh510001.csv"), index=False)
    gb2_ok, gb2 = mod._gate_gb(codes)
    chk("GB catches rows after evidence_cutoff", not gb2_ok
        and gb2["members"]["510001"]["rows_after_cutoff"] == 1)
    # restore the corrupted twin so later recomputes stay deterministic
    idx = pd.bdate_range(starts[1], "2020-01-01")
    pd.DataFrame({"date": idx.strftime("%Y-%m-%d"), "open": 1.0, "high": 1.0,
                  "low": 1.0, "close": 1.0, "volume": 1.0,
                  }).to_csv(os.path.join(fake, "sh510001.csv"), index=False)

    ps = mod._panel_start(gb["members"])
    # staggered starts -> the 5th member's valid_from is the first day the
    # >=5-member cross-section exists (members 0..4 by start order)
    chk("panel_start = first day with >=5 valid members",
        ps == gb["members"]["510004"]["valid_from"])
    # thin-universe case: only 3 valid -> None
    thin = {k: gb["members"][k] for k in list(gb["members"])[:3]}
    chk("panel_start None when <5 members ever valid", mod._panel_start(thin) is None)

    reg = os.path.join(tmp, "registry.json")
    json.dump({"events": [{"sym": "159901", "date": "2021-04-12", "pct": -0.5103},
                          {"sym": "512100", "date": "2022-05-20", "pct": 1.7627}]},
              open(reg, "w"))
    cmp_ = mod._gd_compare(reg, sorted([("159901", "2021-04-12", -0.5103),
                                        ("512100", "2022-05-20", 1.7627)]))
    chk("GD compare bit-match true", cmp_["bit_match"] and cmp_["n_pre_2020"] == 0)
    cmp2 = mod._gd_compare(reg, [("159901", "2021-04-12", -0.5103)])
    chk("GD compare catches drift", not cmp2["bit_match"])

    # GF probe on synthetic ticket/orders (hermetic: ADJUST_DIR pinned to an
    # empty tmp dir -- the r116 lesson: real stage-3 files on disk broke the
    # "files empty" fixture premise of this leg on delivery machines)
    mod.T19_TICKET_PATH = os.path.join(tmp, "t19.json")
    mod.ADJUST_DIR = os.path.join(tmp, "consolidation")
    os.makedirs(mod.ADJUST_DIR)
    json.dump({"note": "stage-1 delivered; Remaining: ... stage-3 adjusted panel"},
              open(mod.T19_TICKET_PATH, "w"))
    mod.ORDERS_DIR = os.path.join(tmp, "orders")
    os.makedirs(mod.ORDERS_DIR)
    gf = mod._gf_state()
    chk("GF unsatisfied when neither files nor marker", gf["satisfied"] is False)
    open(os.path.join(mod.ORDERS_DIR, "O-x.md"), "w", encoding="utf-8").write(
        "GM waiver: T-18 deep reval adjusted-view 豁免 effective now")
    gf2 = mod._gf_state()
    chk("GF satisfied via GM waiver line", gf2["satisfied"] and gf2["gm_waiver"])
    json.dump({"note": "... stage-3 adjusted panel delivered by bm-c ..."},
              open(mod.T19_TICKET_PATH, "w"))
    open(os.path.join(mod.ORDERS_DIR, "O-x.md"), "w", encoding="utf-8").write("no waiver")
    gf3 = mod._gf_state()
    chk("GF delivered requires files too (files empty -> false)",
        gf3["satisfied"] is False and gf3["delivered"] is False)

    # determinism on synthetic members payload
    p1 = json.dumps({"m": gb["members"], "ps": ps}, sort_keys=True)
    p2 = json.dumps({"m": mod._gate_gb(codes)[1]["members"],
                     "ps": mod._panel_start(mod._gate_gb(codes)[1]["members"])},
                    sort_keys=True)
    chk("GE payload deterministic across recomputes", p1 == p2)

    # ---- nulls-stage offline legs (no engine runs) ----
    a1 = np.random.default_rng(54_000 + 7).random(5)
    a2 = np.random.default_rng(54_000 + 7).random(5)
    a3 = np.random.default_rng(54_000 + 8).random(5)
    chk("nulls seeds: 54_000+k reproducible and k-distinct",
        bool((a1 == a2).all()) and not bool((a1 == a3).all()))
    chk("nulls p-regime alternation (p2 family-A reuse)",
        NULLS_P[0] == 0.02 and NULLS_P[1] == 0.05
        and [NULLS_P[k % 2] for k in range(4)] == [0.02, 0.05, 0.02, 0.05])

    rl = os.path.join(tmp, "nulls_runs.jsonl")
    mod.NULLS_RUNS_PATH = rl
    with open(rl, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps({"k": 0, "ok": True, "manifest_sha": "S1"}) + "\n")
        fh.write(json.dumps({"k": 1, "ok": True, "manifest_sha": "S2"}) + "\n")
        fh.write("{broken json\n")
        fh.write(json.dumps({"k": 99, "ok": True, "manifest_sha": "S1"}) + "\n")
        fh.write(json.dumps({"k": 2, "ok": False, "manifest_sha": "S1"}) + "\n")
    r = mod._nulls_resume("S1")
    chk("nulls resume: manifest-sha keyed done-set filters stale/bad/range",
        set(r.keys()) == {0})

    mod.CACHE_DIR = os.path.join(tmp, "panelcache")
    ohl = os.path.join(mod.CACHE_DIR, "ohlcv")
    os.makedirs(ohl)
    dts = pd.bdate_range("2015-01-01", "2017-01-06")
    for code in ("510001", "510002", "510003"):
        pd.DataFrame({"date": dts.strftime("%Y-%m-%d"), "open": 1.0,
                     "high": 1.0, "low": 1.0, "close": 1.0,
                     "volume": 1.0}).set_index("date").to_parquet(
            os.path.join(ohl, code + ".parquet"))
    man3 = {"panel_start": "2016-01-04",
            "members": {"510001": {"valid_from": "2015-06-01"},
                        "510002": {"valid_from": "2015-09-01"},
                        "510003": {"valid_from": "2016-01-04"}}}
    prices3, idx3, syms3, mask3 = mod._panel_inputs(man3)
    chk("nulls panel inputs: 3 members loaded, datetime union index",
        len(prices3) == 3 and len(idx3) == len(dts)
        and str(idx3[0].date()) == "2015-01-01")
    chk("nulls mask: pre-panel_start axis gate blocks even valid members",
        not mask3.loc["2015-12-31", "510001"])
    chk("nulls mask: valid member True only on-axis",
        mask3.loc["2016-01-05", "510001"]
        and mask3.loc["2016-01-05", "510002"]
        and mask3.loc["2016-01-05", "510003"]
        and not mask3.loc["2015-06-02", "510001"]
        and not mask3.loc["2015-06-02", "510003"])

    print("selftest: all PASS")
    return 0


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    cmd = argv[0] if argv else "status"
    if cmd == "gates":
        return cmd_gates()
    if cmd == "build":
        return cmd_build()
    if cmd == "nulls":
        return cmd_nulls()
    if cmd in ("reval", "pbo"):
        return _blocked_stage(cmd)
    if cmd == "status":
        return cmd_status()
    if cmd == "selftest":
        return _selftest()
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())
