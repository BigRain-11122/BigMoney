"""D-20260930-41 deliverable #1 -- cross-start + rolling-window robustness
adjudication (CROSS-START-ROBUSTNESS-P1, bm-c berth r284).

Adjudicates the ORDER's two standing retail conclusions across start points
and rolling windows ("majority of starts hold -> keep, else withdraw"):

  Face A (burned this batch): four-asset allocation conclusion
      (claim anchor 5.87%/-14.4%/71%, regime-adaptive external config).
      In-repo face = equal-weight 25x4 monthly rebalance (near-kin, no
      replication obligation per EXCLUSION_MARGINAL precedent) + 3 seeded
      random static-weight null cells. Engine = 100% imported from
      scripts/allocation_policy_scan (load_faces/simulate/_path_metrics),
      zero rewrite per anti-dup law.
  Face B (burn window OPEN since bm-b engine landing r476 / commit 25b13a8a5):
      low-volume stock-selection conclusion (14.80%/8-10y single-start defect
      named by the ORDER). Canonical baseline frozen in prereg sec.3-B; the
      engine is 100% imported from scripts/exclusion_marginal_scan (bm-b
      berth #3, MSG-20260930-1947 sec.2 anti-dup law, zero rewrite). Data
      locality: the astock per-code panel is physically bm-b-only
      (gitignored face), so this burn is pool-submitted with lane_owner=bm-b;
      run_face_b executes on the burn host and lands face_b.json in git.

Prereg (frozen pre-burn) = research/CROSS_START_ROBUSTNESS.md.
Laws carried: G-ANCHOR-FACE four-tuples (inherited via load_faces fail-closed),
R99 freeze-before-burn, CN-C7 cost import (no hand-copy), M1 informational t,
M3 closed-family gate, trial gate <=500/30d (RETAIL_QUANT_TRACK sec.4),
evidence_cutoff=2026-09-22 (same lockbox as ALLOC-POLICY-SCAN-P1).

Usage (module mode, cwd = repo root):
    python -m scripts.cross_start_robustness probe      # anchors + gates
    python -m scripts.cross_start_robustness run        # face A burn
    python -m scripts.cross_start_robustness run_face_b # face B burn (bm-b host)
    python -m scripts.cross_start_robustness selftest   # hermetic
Direct run also works (repo-root sys.path fix mirrors allocation_policy_scan).
"""
import json
import os
import sys

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)
_SCRIPTS_DIR = os.path.join(_REPO_ROOT, "scripts")
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

# GBK console reconfigure entry law (r236 family)
if hasattr(sys.stdout, "encoding") and sys.stdout.encoding \
        and sys.stdout.encoding.lower().replace("-", "") not in ("utf8", "utf8mb4"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import numpy as np  # noqa: E402

try:
    from scripts import science_gates as sg
    from scripts import allocation_policy_scan as aps
    from scripts.parallel_runner import run_cells_parallel, worker_cap
except ImportError:
    import science_gates as sg
    import allocation_policy_scan as aps
    from parallel_runner import run_cells_parallel, worker_cap

BATCH = "CROSS-START-ROBUSTNESS-P1"
EVIDENCE_CUTOFF = "2026-09-22"        # same lockbox as ALLOC-POLICY-SCAN-P1
OUT_DIR = os.path.join(_REPO_ROOT, "results", "cross_start_robustness")
FAMILY_KEY = "cross-start-robustness"
SEED_KEY = "cross_start_robustness_p1"
N_RAND_CELLS = 3
N_TRIALS = 1 + N_RAND_CELLS          # A-EQW + A-RAND x3 (face B staged +2 later)

# ---- Face B (low-volume stock-selection cross-start adjudication) ---------
# Burn window opened r285: bm-b #3 EXCLUSION-MARGINAL engine landed (r476,
# commit 25b13a8a5, selftest 16/16) -> per MSG-1947 sec.2 / prereg sec.3-B the
# Face B burn imports that engine wholesale (anti-dup: zero engine rewrite).
B_RAND_SEED_OFFSET = 100             # band 20329000+100; A-RAND used +0..2
FACE_B_N_TRIALS = 2                  # B-FULL + B-RAND (prereg sec.3-B)
FACE_B_FILE = os.path.join(OUT_DIR, "face_b.json")
CLAIM_B = {"cagr": 0.1480, "win_band": "8-10y",
           "source": "ORDER conclusion B: low-volume selection "
                     "(single-start defect named by the ORDER, 须补验)"}
KIN_FILE = os.path.join(_REPO_ROOT, "results", "allocation_policy_scan",
                        "scan.json")
KIN_CELL_IDS = ["0.30|0.50|0.20|monthly", "0.20|0.50|0.20|monthly"]
WIN_1Y_WINDOW = 252

# ORDER conclusion A claim anchors (external regime-adaptive config) --
# reference-only comparison anchors, never gates (prereg sec.4).
CLAIM_A = {"cagr": 0.0587, "maxdd": -0.144, "win_rate": 0.71,
           "source": "ORDER conclusion A: regime-adaptive four-asset, "
                     "external config not in repo"}


def _rand_targets():
    """Seeded random static weights (prereg sec.3-A): default_rng(base+k)
    .dirichlet(ones(4)), k=0..N_RAND_CELLS-1. Deterministic, sum=1."""
    base = int(sg.SEED_REGISTRY[SEED_KEY])
    rows = []
    for k in range(N_RAND_CELLS):
        rng = np.random.default_rng(base + k)
        w = rng.dirichlet(np.ones(4))
        assert abs(float(w.sum()) - 1.0) < 1e-12 and (w > 0).all()
        rows.append(w)
    return np.array(rows)


def _targets():
    eqw = np.array([[0.25, 0.25, 0.25, 0.25]])
    rand = _rand_targets()
    return np.vstack([eqw, rand]), ["A-EQW"] + \
        [f"A-RAND-{k+1}" for k in range(N_RAND_CELLS)]


def _win_metrics(path, starts):
    """Frozen win-rate readouts (prereg sec.3-A):
    win_1y_pos_share = share of rolling 252td windows with positive total
    return (daily step, log-diff); win_month_pos_share = share of positive
    complete month slices between consecutive month-first boundaries (tail
    partial month excluded; first slice starts at window head, disclosed)."""
    v = np.asarray(path, dtype=float)
    out = {"win_1y_pos_share": None, "win_month_pos_share": None,
           "n_1y_windows": 0, "n_month_slices": 0}
    if len(v) > WIN_1Y_WINDOW:
        logv = np.log(v)
        d = logv[WIN_1Y_WINDOW:] - logv[:-WIN_1Y_WINDOW]
        out["win_1y_pos_share"] = float((d > 0).mean())
        out["n_1y_windows"] = int(len(d))
    starts = np.asarray(starts)
    if len(starts) >= 2:
        seg = v[starts[1:]] / v[starts[:-1]] - 1.0
        out["win_month_pos_share"] = float((seg > 0).mean())
        out["n_month_slices"] = int(len(seg))
    return out


# ---- T-134 s2 multicore conversion (CEO order O-2026-09-30-2355) --------
# All-start grid = per-start independent jobs through the house
# scripts/parallel_runner ProcessPool (worker_cap x0.8 + RAM guard,
# BelowNormal workers per O-1136). Outputs are byte-identical to the
# retired serial loop: each start simulates the same sliced window and
# results are keyed by start index (scheduler-independent determinism).
_AS_G: dict = {}


def _as_init(dates, rets, targets, rule):
    """Pool worker initializer: BelowNormal priority (O-1136) + shared
    sliced-input globals (panels passed once via initargs, never via
    closures -- picklable-worker law)."""
    try:
        import psutil
        pri = getattr(psutil, "BELOW_NORMAL_PRIORITY_CLASS", None)
        if pri is not None:
            psutil.Process().nice(pri)
    except Exception:
        pass
    aps._cost_check()   # worker-side lazy global init (COST_PER_SIDE=None
                        # until _cost_check imports cost_spec.X1_RATE)
    _AS_G.update(dates=dates, rets=rets, targets=targets, rule=rule)


def _allstart_one(payload):
    """One all-start grid job: simulate the sliced window for ALL target
    rows; returns (start_index, V-vector-or-None). Top-level picklable."""
    j, s = payload["j"], payload["s"]
    if payload["horizon"] <= 0:
        return j, None
    sim = aps.simulate_with_dates(
        _AS_G["dates"][s:], _AS_G["rets"][s:], _AS_G["targets"],
        np.zeros(_AS_G["targets"].shape[0], dtype=int), _AS_G["rule"],
        store_path=False)
    return j, sim["V"]


def _allstart_stats(dates, rets, targets, rule="monthly"):
    """Fresh-entry all-start grid (prereg sec.3-A). Start grid = monthly
    first trading days (same grid/horizon gate as #2); ENTRY SEMANTICS =
    clean sliced entry: each start enters at slice t=0 (engine sliced state
    is twin-verified vs the aps naive reference at 1e-12), because the
    engine's in-window fresh-entry leg drifts weights on the entry day
    without crediting V (measured perturbation = entry-day portfolio
    return, ~1e-3 relative; disclosed in prereg changelog + summary).
    Headline stats over starts with horizon >= aps.MIN_START_HORIZON."""
    starts = aps._monthly_start_idx(dates)
    n = rets.shape[0]
    horizon_days = (n - 1) - starts
    valid = horizon_days >= aps.MIN_START_HORIZON
    n_valid, n_short = int(valid.sum()), int((~valid).sum())
    R = targets.shape[0]
    finals = np.empty((len(starts), R), dtype=float)
    jobs = [(j, _allstart_one,
             ({"j": j, "s": int(s), "horizon": int(horizon_days[j])},))
            for j, s in enumerate(starts)]
    pool_out = run_cells_parallel(
        jobs, workers=worker_cap(), desc="allstart grid",
        initializer=_as_init, initargs=(dates, rets, targets, rule))
    as_workers = pool_out.pop("__workers__", 1)
    for j in range(len(starts)):
        _, v = pool_out[j]
        finals[j] = v if v is not None else np.nan
    per_row = []
    for i in range(R):
        with np.errstate(divide="ignore", invalid="ignore"):
            cagrs = finals[:, i] ** (252.0 / horizon_days) - 1.0
        head = cagrs[valid & (horizon_days > 0)]
        per_row.append({
            "allstart_n_valid": n_valid, "allstart_short": n_short,
            "allstart_best": float(head.max()),
            "allstart_worst": float(head.min()),
            "allstart_p25": float(np.percentile(head, 25)),
            "allstart_median": float(np.percentile(head, 50)),
            "allstart_p75": float(np.percentile(head, 75)),
            "allstart_pos_share": float((head > 0).mean()),
        })
    return per_row, n_valid, n_short, int(len(starts)), as_workers


def _adjudicate(cell):
    """Frozen PASS criteria (prereg sec.4, three-way conjunction):
    allstart_pos_share >= 0.50 AND allstart_median_cagr > 0 AND worst5y > 0."""
    ok_pos = cell["allstart_pos_share"] is not None \
        and cell["allstart_pos_share"] >= 0.50
    ok_med = cell["allstart_median"] is not None and cell["allstart_median"] > 0
    ok_w5 = cell["worst5y"] is not None and cell["worst5y"] > 0
    return {"pos_share_ok": bool(ok_pos), "median_ok": bool(ok_med),
            "worst5y_ok": bool(ok_w5), "pass": bool(ok_pos and ok_med and ok_w5)}


def _kin_context():
    """Read-only context from the burned #2 scan (zero new trials):
    pure-stock/pure-cash baselines + nearest-kin monthly cells."""
    with open(KIN_FILE, encoding="utf-8") as fh:
        scan = json.load(fh)
    kin = {"baselines": {}, "nearest_kin_cells": {}}
    for c in scan["cells"]:
        if c.get("baseline"):
            kin["baselines"][c["baseline"]] = {
                k: c.get(k) for k in ("cagr", "maxdd", "worst5y")}
        elif c["cell_id"] in KIN_CELL_IDS:
            kin["nearest_kin_cells"][c["cell_id"]] = {
                k: c.get(k) for k in ("w", "cagr", "maxdd", "worst5y",
                                      "allstart_median", "allstart_pos_share",
                                      "allstart_best", "allstart_worst")}
    kin["source"] = "results/allocation_policy_scan/scan.json (bm-b r474, +0 trials)"
    kin["nearest_kin_note"] = ("0.30|0.50|0.20|monthly = closest grid cell to "
                               "equal-weight in weight space (L1 dist 0.12)")
    return kin


# ==========================================================================
# Face B -- low-volume stock-selection conclusion, cross-start adjudication
# ==========================================================================
def _ems():
    """Lazy engine import (bm-b #3 EXCLUSION-MARGINAL, landed r476; single
    import face -- anti-dup law MSG-20260930-1947 sec.2)."""
    try:
        from scripts import exclusion_marginal_scan as ems
    except ImportError:
        import exclusion_marginal_scan as ems
    return ems


def _face_b_cells():
    """Frozen Face B cells (prereg sec.3-B): B-FULL = raw baseline (ALL
    exclusion rules OFF -> pure amt20-asc top-10) and B-RAND = seeded
    random-cohort null on the same valid-candidate face."""
    ems = _ems()
    off = list(ems.RULES)
    return ({"cell": "B-FULL", "off": off},
            {"cell": "B-RAND", "off": off, "base": "random"})


def _face_b_gates():
    """FAIL-CLOSED Face B burn gates (mirror ems._burn_gates fact sources;
    Face B idempotency + BOTH seed keys + BOTH families + panel host face)."""
    import time as _t
    ems = _ems()
    rep = {}
    if not os.path.exists(ems.PROBE_FILE):
        rep["fail"] = "engine probe facts missing (bm-b probe not run)"
        return False, rep
    with open(ems.PROBE_FILE, encoding="utf-8") as fh:
        probe_f = json.load(fh)
    af = probe_f.get("anchor_faces", {})
    if (af.get("panel", {}).get("path") != "data/astock_daily/per/<code>.csv"
            or af.get("eligibility", {}).get("path")
            != "data/fundamental/eligibility.csv"):
        rep["fail"] = "anchor face paths mismatch"
        return False, rep
    if not os.path.isdir(ems.PANEL_DIR):
        rep["fail"] = f"panel host gate: {ems.PANEL_DIR} absent (bm-b lane)"
        return False, rep
    files = sorted(os.listdir(ems.PANEL_DIR))
    if len(files) != probe_f.get("panel_files"):
        rep["fail"] = f"panel_files {len(files)} != {probe_f.get('panel_files')}"
        return False, rep
    n_elig = len(ems._load_codes())
    if n_elig != probe_f.get("eligibility_codes"):
        rep["fail"] = (f"eligibility_codes {n_elig} != "
                       f"{probe_f.get('eligibility_codes')}")
        return False, rep
    with open(ems.ASTOCK_STATUS, encoding="utf-8") as fh:
        st = json.load(fh)
    panel = st.get("panel", {})
    if not panel.get("complete") or panel.get("cutoff", "") < ems.EVIDENCE_CUTOFF:
        rep["fail"] = f"panel gate: {panel}"
        return False, rep
    age_h = (_t.time() - os.path.getmtime(ems.ELIG_CSV)) / 3600.0
    if age_h > 24.0:
        rep["fail"] = f"eligibility age {age_h:.1f}h > 24h"
        return False, rep
    fam_b = sg.closed_family_check(FAMILY_KEY)
    fam_e = sg.closed_family_check("exclusion_marginal_p1")
    if fam_b["status"] == "rejected" or fam_e["status"] == "rejected":
        rep["fail"] = f"closed family: {fam_b['status']}/{fam_e['status']}"
        return False, rep
    if SEED_KEY not in sg.SEED_REGISTRY:
        rep["fail"] = f"seed key missing: {SEED_KEY}"
        return False, rep
    if ems.SEED_KEY not in sg.SEED_REGISTRY:
        rep["fail"] = f"engine seed key missing: {ems.SEED_KEY}"
        return False, rep
    from knowledge import cost_spec
    from knowledge import rules as kr
    rep["cost_spec_verify"] = cost_spec.verify()
    rep["adv_cap_mirror"] = (ems.K_ADV_CAP == kr.ADV_FILL_CAP_RATE)
    if not rep["cost_spec_verify"] or not rep["adv_cap_mirror"]:
        return False, rep
    if os.path.exists(FACE_B_FILE) and os.environ.get("FACE_B_REBURN") != "1":
        rep["fail"] = ("already burned -- face_b.json present "
                       "(FACE_B_REBURN=1 redo channel)")
        return False, rep
    rep.update({"panel_files": len(files), "eligibility_codes": n_elig,
                "panel_status_cutoff": panel.get("cutoff"),
                "eligibility_age_h": round(age_h, 1),
                "family_face_b": fam_b["status"],
                "family_engine": fam_e["status"],
                "rand_seed_base": int(sg.SEED_REGISTRY[SEED_KEY])
                                  + B_RAND_SEED_OFFSET})
    return True, rep


# --------------------------------------------------------------------------
# multicore faces (O-2026-09-30-2355 hard law; T-134 s2 conversion, bm-b).
# Face B sims run as per-(cell, start) ProcessPool tasks through the shared
# parallel_runner; engine faces stay 100% imported from ems. This also FIXES
# the r478-class contract bug: the old closure `def mkt(code)->tuple` was a
# CALLABLE, while ems._sim_cell subscripts (mkt[c]) -- it would have died
# TypeError at the first marked position, after the multi-minute feature
# pass. The engine's ems._Mkt class (subscriptable) is the contract face.
# --------------------------------------------------------------------------
def _fb_init_ctx(ctx: dict) -> None:
    """ProcessPool initializer: ships the compact shared context once per
    worker; the engine module global pair (ems._POOL_CTX/_MKT_CACHE) is the
    only state the tasks consume (spawn-safe, no closures cross the wire)."""
    global _FB_CTX
    _FB_CTX = ctx
    ems = _ems()
    ems._POOL_CTX = ctx
    ems._MKT_CACHE = ems._Mkt()


def _fb_task(sel_named, m0):
    """One face-B sim task: full-period replay (m0 None) or one Jan-first
    start replay (prereg sec.3-B frozen faces, engine imported)."""
    ems = _ems()
    ctx = ems._POOL_CTX
    mkt = ems._MKT_CACHE
    from knowledge import rules as _kr
    stock_fee = _kr.fee_schedule_for("600000")
    sig_pos, n_cal, cal = ctx["sig_pos"], ctx["n_cal"], ctx["cal"]
    n_sig, code_idx, AMT = ctx["n_sig"], ctx["code_idx"], ctx["AMT"]

    def slip_of(code: str, m: int) -> float:
        i = code_idx[code]
        adv = AMT[i, m] if m < n_sig else np.nan
        return _kr.cost_v2_slippage(adv if adv == adv else None)

    start_month = 0 if m0 is None else m0
    day0 = sig_pos[0] if m0 is None else sig_pos[m0]
    rp = ems._sim_cell(sel_named, mkt, sig_pos, n_cal, start_month,
                       stock_fee, slip_of)
    met = ems._metrics(rp, cal, day0)
    if m0 is None:
        return {"full_met": met}
    yrs = (n_cal - day0) / 244.0
    return {"start": {
        "ann_ret_net": (float(rp["eq"][-1]) / ems.INITIAL_CASH)
                       ** (1.0 / yrs) - 1.0,
        "final_equity": float(rp["eq"][-1]),
        "worst_5y": met["worst_5y"],
        "maxdd": met["maxdd"],
    }}


def run_face_b(write=True):
    """Burn Face B (prereg sec.3-B, frozen): raw low-amount baseline
    (amt20-asc top-10, monthly, T+1 open exec, V2 stock costs) across the
    16 Jan-first starts 2007..2022 + seeded random-cohort null. Engine faces
    are 100% imported from bm-b's exclusion_marginal_scan; the data assembly
    mirrors ems.run() with ONE disclosed deviation: panel rows dated before
    the calendar face (sh510050 starts 2005-02-23) are filtered BEFORE the
    calendar mapping. Sensitivity: both Face B cells run with ALL exclusion
    rules OFF, so barcnt/age and stale faces are not consumed; amt20 at
    signal dates >= 2007-01 is identical under the filter (20-bar rolling
    window fully post-2005); the filter is required because pre-2005 rows
    are legitimately outside the calendar face (they map as unmapped -> the
    ems.run() assembly FAIL-CLOSEDs on any pre-2005 listing -- engineering
    fact disclosed to bm-b, MSG-20260930-2115-bmc-bmb)."""
    import time as _t
    t0 = _t.time()
    ems = _ems()
    # CPU headroom law (O-20260929-1029): self-apply BELOW_NORMAL priority
    # (harmless no-op off-Windows; belt-and-suspenders beside workers_plan).
    try:
        import ctypes
        ctypes.windll.kernel32.SetPriorityClass(
            ctypes.windll.kernel32.GetCurrentProcess(), 0x00004000)
    except Exception:
        pass
    ok, gates = _face_b_gates()
    if not ok:
        print(json.dumps({"face_b": "FAIL-CLOSED (zero-burn)", "gates": gates},
                         ensure_ascii=False, indent=1))
        return 2
    from firm.risk import b_layer_filter as blf

    # ---- calendar + signals (engine faces, imported) ----
    cal, _ = ems._load_calendar()
    cutoff_pos = max(i for i, d in enumerate(cal) if d <= ems.EVIDENCE_CUTOFF)
    cal = cal[: cutoff_pos + 1]                     # rows actually read <= cutoff
    cal_pos_of = {d: i for i, d in enumerate(cal)}
    sig_dates, sig_pos_full = ems._signal_schedule(ems._load_calendar()[0])
    n_cal = len(cal)
    sig_pos = [p for p in sig_pos_full if p + 1 < n_cal]
    sig_dates = [d for d, p in zip(sig_dates, sig_pos_full) if p + 1 < n_cal]
    n_sig = len(sig_pos)

    # ---- universe: engine canonical assembly (elig ∩ mask ∩ panel files) ----
    elig = blf.load_eligibility(ems.ELIG_CSV)
    mask = blf.load_mask(ems.MASK_CSV)
    panel_codes = {f[:-4] for f in os.listdir(ems.PANEL_DIR)
                   if f.endswith(".csv")}
    codes = sorted(c for c in elig.index
                   if len(c) == 6 and c[0] in ("0", "3", "6")
                   and c in panel_codes and c in mask.index)
    gates["burn_universe"] = len(codes)
    code_idx = {c: i for i, c in enumerate(codes)}
    n_codes = len(codes)

    # ---- feature matrices (phase-1 ProcessPool via the engine's shared
    # _feature_task; lo_bound keeps the disclosed face-B calendar filter;
    # T-134 s2 / O-2026-09-30-2355) ----
    from parallel_runner import run_cells_parallel, worker_cap
    _wo = os.environ.get("CROSS_START_FACEB_WORKERS")
    workers = int(_wo) if _wo else int(min(worker_cap(), 8))
    cal_first = cal[0]
    ctx_f = {"panel_dir": ems.PANEL_DIR, "cal_pos_of": cal_pos_of,
             "cal_start": cal_first, "sig_pos": sig_pos,
             "code_idx": code_idx}
    AMT = np.full((n_codes, n_sig), np.nan)
    CLOSE = np.full((n_codes, n_sig), np.nan)
    CNT = np.full((n_codes, n_sig), np.nan)
    STALE = np.full((n_codes, n_sig), np.inf)
    feats = run_cells_parallel(
        [(c, ems._feature_task, (c, cal_first)) for c in codes],
        workers=workers, desc="face_b_features",
        initializer=_fb_init_ctx, initargs=(ctx_f,))
    feats.pop("__workers__")
    for c in codes:                    # fixed assembly order (determinism)
        r = feats[c]
        if r["unmapped"]:
            gates["fail"] = f"calendar-unmapped in-calendar rows: {c} x{r['unmapped']}"
            print(json.dumps({"face_b": "FAIL-CLOSED (zero-burn)",
                              "gates": gates}, ensure_ascii=False, indent=1))
            return 2
        if r["empty"]:
            continue
        i = r["i"]
        AMT[i] = r["amt"]
        CLOSE[i] = r["close"]
        CNT[i] = r["cnt"]
        STALE[i] = r["stale"]
    r1 = elig.loc[codes, "r1_loss"].astype(bool).to_numpy()
    r2 = elig.loc[codes, "r2_st"].astype(bool).to_numpy()
    seed_base_rand = int(sg.SEED_REGISTRY[SEED_KEY]) + B_RAND_SEED_OFFSET

    start_months: dict[int, int] = {}
    for y in ems.START_YEARS:
        first_day = next(d for d in cal
                          if d[:4] == str(y) and d[5:7] == "01")
        p = cal.index(first_day)
        start_months[y] = next(m for m, sp in enumerate(sig_pos) if sp >= p)

    # ---- phase-2: per-(cell, start) sim pool (T-134 s2 /
    # O-2026-09-30-2355); mkt contract = ems._Mkt (subscriptable; the old
    # closure callable was the r478-class TypeError bug, fixed here) ----
    ctx_c = {"panel_dir": ems.PANEL_DIR, "cal_pos_of": cal_pos_of,
             "cal_start": cal_first, "sig_pos": sig_pos, "n_cal": n_cal,
             "cal": cal, "n_sig": n_sig, "code_idx": code_idx, "AMT": AMT,
             "codes": codes}
    ems._POOL_CTX = ctx_c
    ems._MKT_CACHE = ems._Mkt()
    sel_by_cell: dict[str, list] = {}
    sel_named_by_cell: dict[str, list] = {}
    jobs = []
    for cell in _face_b_cells():
        name = cell["cell"]
        sel = ems._build_selection(
            AMT, CLOSE, CNT, STALE, r1, r2, cell,
            seed_base_rand if cell.get("base") == "random" else None)
        sel_named = [[(codes[i], adv) for i, adv in s] if s else []
                     for s in sel]
        sel_by_cell[name] = sel
        sel_named_by_cell[name] = sel_named
        jobs.append((f"{name}|full", _fb_task, (sel_named, None)))
        for y in ems.START_YEARS:
            jobs.append((f"{name}|start{y}", _fb_task,
                         (sel_named, start_months[y])))
    # r478-class fast-fail gate (parent side, seconds): exercise the exact
    # production consumption face (subscript -> tuple) BEFORE the pool burn.
    _probe_code = next((nm for s in sel_named_by_cell["B-FULL"] if s
                        for nm, _ in s), None)
    if _probe_code:
        _t_probe = ems._MKT_CACHE[_probe_code]
        assert len(_t_probe) == 4 and _t_probe[0].dtype == np.int64, \
            "mkt tuple contract (mpos, opens, closes, ffill)"
    res = run_cells_parallel(jobs, workers=workers, desc="face_b",
                             initializer=_fb_init_ctx, initargs=(ctx_c,))
    n_workers = res.pop("__workers__")

    union_codes = set()
    for cell in _face_b_cells():
        for m in sel_by_cell[cell["cell"]]:
            if m:
                union_codes.update(i for i, _ in m)

    cells_out = {}
    for cell in _face_b_cells():
        name = cell["cell"]
        sel = sel_by_cell[name]
        full_met = res[f"{name}|full"]["full_met"]
        starts = {}
        for y in ems.START_YEARS:
            starts[str(y)] = res[f"{name}|start{y}"]["start"]
        vals = np.array([v["ann_ret_net"] for v in starts.values()])
        row = {
            "off_rules": cell.get("off", []),
            "base": cell.get("base", "rank"),
            "seed_base": seed_base_rand if cell.get("base") == "random" else None,
            "full_period": full_met,
            "allstarts_ann_ret_net": {k: v["ann_ret_net"]
                                      for k, v in starts.items()},
            "allstarts_worst_5y": {k: v["worst_5y"]
                                   for k, v in starts.items()},
            "allstart_best": float(vals.max()),
            "allstart_worst": float(vals.min()),
            "allstart_p25": float(np.percentile(vals, 25)),
            "allstart_median": float(np.median(vals)),
            "allstart_p75": float(np.percentile(vals, 75)),
            "allstart_pos_share": float((vals > 0).mean()),
        }
        # cohort overlap descriptive (engine burn parity)
        ovs = []
        for m in range(len(sel) - 1):
            a = {i for i, _ in sel[m]} if sel[m] else set()
            b = {i for i, _ in sel[m + 1]} if sel[m + 1] else set()
            ovs.append(len(a & b) / ems.N_HOLDINGS)
        row["cohort_overlap_mean"] = float(np.mean(ovs)) if ovs else None
        # adjudication mapping (frozen sec.3-B/4 criteria == Face A family)
        row["allstart_median_cagr"] = row["allstart_median"]
        row["worst5y"] = full_met["worst_5y"]
        row.update(_adjudicate(row))
        cells_out[name] = row

    bfull = cells_out["B-FULL"]
    verdict_b = {
        "claim_anchor": dict(CLAIM_B),
        "inrepo_face": "engine-canonical raw baseline: amt20_mean asc top-10 "
                       "monthly equal-weight T+1, ALL exclusion rules OFF, "
                       "universe = eligibility ∩ b_layer_mask ∩ panel files",
        "verdict_cell": "B-FULL",
        "criteria": "allstart_pos_share>=0.50 AND allstart_median_cagr>0 "
                    "AND worst5y_cagr>0 (prereg sec.3-B/sec.4, frozen "
                    "pre-burn, Face A criteria family)",
        "criteria_reads": {k: bfull[k] for k in
                           ("allstart_pos_share", "allstart_median",
                            "worst5y", "pos_share_ok", "median_ok",
                            "worst5y_ok", "pass")},
        "verdict": "retained" if bfull["pass"] else "withdrawn",
        "note": "ORDER wording: majority of starts hold -> keep, else "
                "withdraw (low-volume conclusion's single-start defect was "
                "named by the ORDER as 须补验).",
    }
    rand_pass = 1 if cells_out["B-RAND"]["pass"] else 0

    # ledger BEFORE dump (r474 embed-order law); pure data-driven chain head
    ledger = sg.append_ledger(
        batch_name=BATCH, batch_trials=FACE_B_N_TRIALS,
        file_name="results/cross_start_robustness/face_b.json",
        evidence_cutoff=EVIDENCE_CUTOFF,
        note="D-41 deliverable #1 FACE B: low-volume selection cross-start "
             "adjudication +2 (B-FULL/B-RAND); engine = bm-b "
             "EXCLUSION-MARGINAL import (r476) per MSG-1947 sec.2 anti-dup; "
             "burn host = bm-b (astock panel locality)")
    payload = {
        "schema": "cross_start_face_b_v1",
        "order_ref": "D-20260930-41 deliverable #1 face B "
                     "(RETAIL_QUANT_TRACK sec.2 #1, bm-c berth)",
        "science_gates": {"cutoff_meta": sg.cutoff_meta(EVIDENCE_CUTOFF)},
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "trials_ledger": ledger,
        "burn_gates_report": gates,
        "engine_provenance": {
            "imported_from": "scripts/exclusion_marginal_scan.py (bm-b r476 "
                             "engine + T-134 s2 multicore conversion r484: "
                             "selftest 19/19 hermetic incl pool legs)",
            "anti_dup_law": "MSG-20260930-1947 sec.2 + prereg sec.3-B: burn "
                            "window opens on engine landing; import reuse, "
                            "zero engine rewrite",
            "imported_faces": [
                "_load_calendar", "_signal_schedule", "_build_selection",
                "_sim_cell", "_metrics", "_side_cost", "_ffill_np",
                "_feature_task", "_Mkt", "RULES", "START_YEARS",
                "N_HOLDINGS", "INITIAL_CASH",
                "BASE_PARAMS", "EVIDENCE_CUTOFF"],
            "assembly_deviation": "panel rows dated < calendar face start "
                                  "(2005-02-23) filtered pre-mapping; both "
                                  "cells run all-rules-OFF so barcnt/stale "
                                  "faces are unconsumed and signal-date "
                                  "amt20 is identical under the filter "
                                  "(disclosed; ems.run() assembly fails-"
                                  "closed on pre-2005 rows instead -- "
                                  "engineering fact, bm-b berth to resolve)",
        },
        "universe": {"n_codes": n_codes,
                     "face": "engine canonical: eligibility ∩ b_layer_mask "
                             "presence ∩ panel files (mirrors bm-b run())"},
        "signal_months": n_sig,
        "signal_first_last": [sig_dates[0], sig_dates[-1]],
        "base_params": dict(ems.BASE_PARAMS),
        "face_b_params": {
            "off_rules": "ALL (raw baseline face; B-FULL == bm-b NONE-cell "
                         "semantics by frozen definition)",
            "b_rand_seed": f"default_rng([base+{B_RAND_SEED_OFFSET}+m, 7919]) "
                           "per-month streams (engine random procedure, "
                           "seed band cross_start_robustness_p1+100)",
            "rand_seed_base": seed_base_rand,
            "starts": "2007..2022 Jan first signal month (16)",
        },
        "cells": cells_out,
        "conclusion_B": verdict_b,
        "rand_null_pass_count": rand_pass,
        "burn_audit": {"elapsed_sec": round(_t.time() - t0, 1),
                       "n_cached_names": len(union_codes),
                       "workers": n_workers,
                       "parallel_face": "parallel_runner.run_cells_parallel "
                                        "phase-1 features + phase-2 "
                                        "per-(cell,start) sims "
                                        "(T-134 s2, O-2026-09-30-2355)"},
    }
    if not write:
        return payload
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(FACE_B_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1, sort_keys=True)
    with open(os.path.join(OUT_DIR, "face_b_cells.csv"), "w",
              encoding="utf-8", newline="\n") as f:
        f.write("cell,allstart_pos_share,allstart_median,allstart_best,"
                "allstart_worst,allstart_p25,allstart_p75,worst5y_full,"
                "ann_ret_net_full,maxdd_full,sharpe_full,turnover_ann_full,"
                "cost_drag_ann_full,cohort_overlap_mean,pass\n")
        for name, c in cells_out.items():
            fp = c["full_period"]
            f.write(f"{name},{c['allstart_pos_share']:.6f},"
                    f"{c['allstart_median']:.6f},{c['allstart_best']:.6f},"
                    f"{c['allstart_worst']:.6f},{c['allstart_p25']:.6f},"
                    f"{c['allstart_p75']:.6f},{c['worst5y'] if c['worst5y'] is not None else ''},"
                    f"{fp['ann_ret_net']:.6f},{fp['maxdd']:.6f},"
                    f"{fp['sharpe']:.4f},{fp['turnover_ann'] or 0:.4f},"
                    f"{fp['cost_drag_ann'] or 0:.6f},"
                    f"{c['cohort_overlap_mean'] if c['cohort_overlap_mean'] is not None else ''},"
                    f"{int(c['pass'])}\n")
    print(json.dumps({
        "face_b": "burn COMPLETE",
        "conclusion_B_verdict": verdict_b["verdict"],
        "bfull": {k: bfull[k] for k in ("allstart_pos_share",
                                        "allstart_median", "worst5y",
                                        "pass")},
        "rand_null_pass": rand_pass,
        "ledger_total_after": ledger["total"],
        "elapsed_sec": payload["burn_audit"]["elapsed_sec"],
    }, ensure_ascii=False))
    return payload


def run(write=True):
    aps._cost_check()
    if aps.EVIDENCE_CUTOFF != EVIDENCE_CUTOFF:
        raise RuntimeError("cutoff drift vs #2 face (same-lockbox law)")
    fam = sg.closed_family_check(FAMILY_KEY)
    if fam.get("status") != "open":
        raise RuntimeError(f"closed-family gate: {fam}")
    dates, rets, facts = aps.load_faces()
    if SEED_KEY not in sg.SEED_REGISTRY:
        raise RuntimeError("seed base not registered (prereg sec.3-A law)")
    targets, cell_ids = _targets()
    R = targets.shape[0]

    # pass A: headline rows with full paths
    simA = aps.simulate_with_dates(dates, rets, targets,
                                  np.zeros(R, dtype=int), "monthly",
                                  store_path=True)
    # pass B: all-start fresh-entry grid (T-134 s2: per-start ProcessPool)
    allstart_rows, n_valid, n_short, n_starts, as_workers = _allstart_stats(
        dates, rets, targets, "monthly")
    starts = aps._monthly_start_idx(dates)
    n = rets.shape[0]

    cells = []
    for i, cid in enumerate(cell_ids):
        m = aps._path_metrics(simA["path"][i])
        c = {"cell_id": cid, "rule": "monthly",
             "w": [round(float(x), 6) for x in targets[i]],
             "n_rebalances": int(simA["n_reb"][i]),
             "cost_drag_annual": float(simA["tot_cost"][i] * 252.0 / (n - 1)),
             "t_face": "informational t_from_sharpe (M1 declared non-gating)",
             }
        if cid == "A-EQW":
            c["seed"] = None
        else:
            c["seed"] = int(sg.SEED_REGISTRY[SEED_KEY]) + int(cid[-1]) - 1
        c.update(m)
        c.update(_win_metrics(simA["path"][i], starts))
        c.update(allstart_rows[i])
        c.update(_adjudicate(c))
        cells.append(c)

    eqw = cells[0]
    verdict_a = {
        "claim_anchor": dict(CLAIM_A),
        "inrepo_face": "equal-weight 25x4 monthly four-asset (near-kin; "
                       "no replication obligation per prereg sec.1.2)",
        "verdict_cell": "A-EQW",
        "criteria": "allstart_pos_share>=0.50 AND allstart_median_cagr>0 "
                    "AND worst5y_cagr>0 (prereg sec.4, frozen pre-burn)",
        "criteria_reads": eqw,
        "verdict": "retained" if eqw["pass"] else "withdrawn",
        "note": "ORDER wording: majority of starts hold -> keep, else "
                "withdraw. Claimed numbers are external-config reads, "
                "compared not gated.",
    }
    rand_pass = sum(1 for c in cells if c["cell_id"] != "A-EQW" and c["pass"])

    result = {
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "science_gates": {"cutoff_meta": sg.cutoff_meta(EVIDENCE_CUTOFF)},
        "batch": BATCH,
        "prereg": "research/CROSS_START_ROBUSTNESS.md",
        "n_trials": N_TRIALS,
        "family": {"key": FAMILY_KEY, "status": fam["status"]},
        "faces": facts,
        "cost": {"face": "A", "per_side_bp": 13.041, "rt_bp": 26.082,
                 "source": "knowledge/cost_spec.py X1_RATE (imported)"},
        "audit": {"workers": int(as_workers),
                  "face": "T-134 s2 ProcessPool conversion (O-2026-09-30-2355): "
                          "pass B all-start grid = per-start jobs via "
                          "scripts/parallel_runner (worker_cap x0.8 + RAM guard, "
                          "BelowNormal workers); pass A headline = unchanged "
                          "single vectorized call; outputs byte-identical to "
                          "retired serial loop (S9 determinism law)"},
        "grid": {"cells": cell_ids, "rule": "monthly",
                 "n_starts": n_starts, "n_valid_starts": n_valid,
                 "n_short_starts": n_short,
                 "min_start_horizon_td": aps.MIN_START_HORIZON,
                 "rand_seed_base": int(sg.SEED_REGISTRY[SEED_KEY]),
                 "rand_procedure": "default_rng(base+k).dirichlet(ones(4))"},
        "face_B_staged": {
            "status": "STAGED zero burns this batch",
            "baseline": "amt20_mean asc top-10 monthly equal-weight T+1, "
                        "16 Jan-firsts 2007..2022, V2 stock costs",
            "engine_plan": "import bm-b EXCLUSION-MARGINAL engine when it "
                           "lands (anti-dup; MSG-1947 sec.2)",
            "planned_trials": 2,
        },
        "conclusion_A": verdict_a,
        "rand_null_pass_count": rand_pass,
        "kin_context": _kin_context(),
        "cells": cells,
    }
    if not write:
        return result

    os.makedirs(OUT_DIR, exist_ok=True)
    scan_path = os.path.join(OUT_DIR, "scan.json")
    existing_tl = None
    if os.path.exists(scan_path):
        try:
            with open(scan_path, encoding="utf-8") as fh:
                old = json.load(fh)
            tl = old.get("trials_ledger") or {}
            if tl.get("batch") == BATCH:
                existing_tl = tl
        except Exception:
            existing_tl = None
    if existing_tl is not None:
        led = dict(existing_tl)
        led["reexec_single_count"] = True
        led["reexec_note"] = ("deterministic-engine legal re-execution; "
                              "ledger +0 per r259 single-count law")
    else:
        led = sg.append_ledger(
            batch_name=BATCH, batch_trials=N_TRIALS,
            file_name="results/cross_start_robustness/scan.json",
            evidence_cutoff=EVIDENCE_CUTOFF,
            note="D-41 deliverable #1 cross-start robustness adjudication "
                 "face A: equal-weight 25x4 monthly + 3 seeded random "
                 "static-weight nulls; conclusion adjudication not a "
                 "selection search")
    result["trials_ledger"] = led
    with open(scan_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    cols = ["cell_id", "rule", "w", "seed", "n_rebalances", "cost_drag_annual",
            "cagr", "vol", "sharpe", "t_info", "maxdd", "worst3y", "worst5y",
            "worst10y", "p_dd20_1y", "win_1y_pos_share", "win_month_pos_share",
            "n_1y_windows", "n_month_slices", "allstart_n_valid",
            "allstart_best", "allstart_worst", "allstart_p25",
            "allstart_median", "allstart_p75", "allstart_pos_share",
            "allstart_short", "pos_share_ok", "median_ok", "worst5y_ok",
            "pass"]
    import pandas as pd
    pd.DataFrame([{k: c.get(k) for k in cols} for c in cells]) \
        .to_csv(os.path.join(OUT_DIR, "cells.csv"), index=False)
    _write_summary(result)
    print(json.dumps({
        "batch": BATCH, "cutoff": EVIDENCE_CUTOFF,
        "conclusion_A_verdict": verdict_a["verdict"],
        "eqw": {k: eqw[k] for k in ("cagr", "maxdd", "win_1y_pos_share",
                                    "allstart_pos_share",
                                    "allstart_median", "worst5y", "pass")},
        "rand_null_pass": f"{rand_pass}/{N_RAND_CELLS}",
        "ledger_total_after": led.get("total"),
    }, ensure_ascii=False))
    return result


def _write_summary(result):
    va, f, kin = result["conclusion_A"], result["faces"], result["kin_context"]
    eqw = next(c for c in result["cells"] if c["cell_id"] == "A-EQW")
    bl = kin["baselines"]
    lines = [
        f"# CROSS-START-ROBUSTNESS-P1 裁定摘要（D-41 交付件#1·Face A）",
        "",
        f"- **结论A裁定：{('保留' if va['verdict'] == 'retained' else '撤回')}"
        f"**（判据：多数起点正份额≥50% ∩ 起点中位>0 ∩ 滚动5年最差>0——跑前冻结）",
        f"- evidence_cutoff = **{result['evidence_cutoff']}**（与 #2 同锁盒；"
        f"债/金孪生末行=cutoff 日，6td 尾差披露）·联合窗 {f['joint_start']}"
        f" → {f['joint_end']}（{f['n_days']} 交易日）",
        f"- 本仓面=等权 25×4 月频（政体自适应版=外部配置不在仓，无复现义务——"
        f"近亲面裁定，读数对照不裁断）",
        "",
        "## A-EQW vs 令文锚（对照不裁断）",
        "",
        "| 面 | 年化 | 最大回撤 | 胜率类读数 |",
        "|---|---|---|---|",
        f"| 令文结论A（外部政体自适应） | 5.87% | −14.4% | 71%（原口径未注） |",
        f"| 本仓面 A-EQW 等权月频 | {eqw['cagr']:+.2%} | {eqw['maxdd']:.1%} "
        f"| 1年滚动窗正占比 {eqw['win_1y_pos_share']:.1%} / 月切片正占比 "
        f"{eqw['win_month_pos_share']:.1%} |",
        "",
        "## 全起点分布（§1.3 必填面·新鲜入场独立模拟）",
        "",
        f"- 月度起点 {result['grid']['n_starts']} 个（≥3 年 horizon 入 "
        f"headline {result['grid']['n_valid_starts']} 个，短 horizon "
        f"{result['grid']['n_short_starts']} 个如实披露）",
        f"- A-EQW：最好 {eqw['allstart_best']:+.2%} / p75 "
        f"{eqw['allstart_p75']:+.2%} / 中位 {eqw['allstart_median']:+.2%} / "
        f"p25 {eqw['allstart_p25']:+.2%} / 最坏 {eqw['allstart_worst']:+.2%}"
        f" / 正份额 {eqw['allstart_pos_share']:.1%}",
        f"- 滚动窗最差：3年 {eqw['worst3y']:+.2%} / 5年 {eqw['worst5y']:+.2%}"
        f" / 10年 {eqw['worst10y']:+.2%}（10y 窗起点跨度薄样本如实注记）",
        f"- 一年内见 −20% 概率：{eqw['p_dd20_1y']:.1%}"
        f"（#2 纯股基线 38.5% 对照）",
        "",
        "## 随机静态权重 null 族（seeded·公布不设线）",
        "",
        "| 格 | 权重 | 年化 | 起点中位 | 正份额 | PASS |",
        "|---|---|---|---|---|---|",
    ]
    for c in result["cells"]:
        if c["cell_id"] == "A-EQW":
            continue
        lines.append(f"| {c['cell_id']} | {c['w']} | {c['cagr']:+.2%} "
                      f"| {c['allstart_median']:+.2%} "
                      f"| {c['allstart_pos_share']:.1%} "
                      f"| {'PASS' if c['pass'] else 'FAIL'} |")
    lines += [
        f"| （A-EQW 等权） | [0.25, 0.25, 0.25, 0.25] | {eqw['cagr']:+.2%} "
        f"| {eqw['allstart_median']:+.2%} | {eqw['allstart_pos_share']:.1%} "
        f"| {'PASS' if eqw['pass'] else 'FAIL'} |",
        "",
        f"随机 null 通过 {result['rand_null_pass_count']}/{N_RAND_CELLS}"
        f"——若随机混合亦多数通过=配置稳健性主体由分散承载的证据面"
        f"（等权无特权主张，如实对照）。",
        "",
        "## kin-context（#2 已烧面只读引用·+0 试验）",
        "",
        f"- 纯股 B&H：CAGR {bl['stock_bh']['cagr']:+.2%} / maxdd "
        f"{bl['stock_bh']['maxdd']:.1%}；纯现金：{bl['cash_only']['cagr']:+.2%}",
        f"- 最近邻格 {KIN_CELL_IDS[0]}：起点中位 "
        f"{kin['nearest_kin_cells'][KIN_CELL_IDS[0]]['allstart_median']:+.2%}"
        f" / 正份额 "
        f"{kin['nearest_kin_cells'][KIN_CELL_IDS[0]]['allstart_pos_share']:.1%}",
        "",
        "## Face B（低量选股结论）分级暂缓",
        "",
        "- 基线定义已冻结共享（20 日均额升序 10 只月频等权 T+1·2007..2022 "
        "16 起点·V2 成本）——烧批待 bm-b #3 排除引擎落地后 import 复用"
        "（防双引擎）；届时 +2 试验另行归因。",
        "",
        "## 诚实免责",
        "",
        "- as-traded 价格基（非全收益：股/债腿分红未计→实际回报被低估；"
        "金腿无分红）；再平衡=同日收盘理想化执行近似（日历规则历法先验）；",
        "- GC001 现金腿=前收年化利率/365 单利近似；首月切片自窗首 2013-07-29 "
        "起为残月（计入并披露）；",
        "- 本裁定=研究产出非投资建议；令文数字为外部配置读数（窗巧合与口径差"
        "异如实披露）；任何格晋升注册须另开预注册过全门（D6/M1/DSR/PBO）。",
        "",
        f"产物：results/cross_start_robustness/scan.json + cells.csv"
        f"（{len(result['cells'])} 行全指标）· 预注册："
        f"research/CROSS_START_ROBUSTNESS.md",
    ]
    with open(os.path.join(OUT_DIR, "SUMMARY_20260930.md"), "w",
              encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def probe():
    aps._cost_check()
    if SEED_KEY not in sg.SEED_REGISTRY:
        raise RuntimeError("seed base not registered")
    dates, rets, facts = aps.load_faces()
    fam = sg.closed_family_check(FAMILY_KEY)
    led = sg.ledger_head()
    kin_ok = os.path.exists(KIN_FILE)
    targets, cell_ids = _targets()
    print(json.dumps({
        "batch": BATCH, "evidence_cutoff": EVIDENCE_CUTOFF,
        "faces": {k: {"path": aps.FACES[k]["path"],
                      "first": facts[k]["first"], "last": facts[k]["last"],
                      "rows": facts[k]["rows"]} for k in aps.LEG_ORDER},
        "joint": {"start": facts["joint_start"], "end": facts["joint_end"],
                  "n_days": facts["n_days"],
                  "ffill_counts": facts["ffill_counts"]},
        "cost_per_side": aps.COST_PER_SIDE,
        "closed_family": fam["status"],
        "seed_base": int(sg.SEED_REGISTRY[SEED_KEY]),
        "rand_cells": [f"{cid}: w={[round(float(x), 6) for x in targets[i]]}"
                       for i, cid in enumerate(cell_ids)],
        "kin_file_present": kin_ok,
        "ledger_head_total": led["total"],
        "n_trials_planned": N_TRIALS,
        "face_B_staged": True,
    }, ensure_ascii=False, indent=1))
    return 0


# ---------------------------------------------------------------- selftest --
def selftest():
    ok = 0

    def chk(name, cond):
        nonlocal ok
        if not cond:
            raise AssertionError(f"selftest FAIL: {name}")
        ok += 1
        print(f"  [ok] {name}")

    # S1: cost anchor import (CN-C7, no hand-copy)
    aps._cost_check()
    chk("S1 cost anchor X1_RATE==0.0013041 (import chain)",
        abs(aps.COST_PER_SIDE - 0.0013041) < 1e-12)
    # S2: EQW target exact + RAND determinism/sum/positivity/distinctness
    targets, cell_ids = _targets()
    chk("S2a EQW target == [0.25]*4",
        np.allclose(targets[0], [0.25] * 4) and cell_ids[0] == "A-EQW")
    t2 = _rand_targets()
    chk("S2b RAND determinism (double-derive identical)",
        np.array_equal(targets[1:], t2))
    chk("S2c RAND rows sum=1, positive, pairwise distinct",
        np.allclose(t2.sum(axis=1), 1.0) and (t2 > 0).all()
        and not np.allclose(t2[0], t2[1]) and not np.allclose(t2[0], t2[2]))
    # S3: win_1y_pos_share on constructed paths (monotone up -> 1.0, down -> 0.0)
    starts_3 = np.array([0, 21, 42, 63])
    up = 1.0 + 0.001 * np.arange(600)
    down = 1.0 - 0.0004 * np.arange(600)
    m_up = _win_metrics(up, starts_3)
    m_dn = _win_metrics(down, starts_3)
    chk("S3 win_1y_pos_share monotone up==1.0 / down==0.0 "
        f"(windows {m_up['n_1y_windows']})",
        m_up["win_1y_pos_share"] == 1.0 and m_dn["win_1y_pos_share"] == 0.0
        and m_up["n_1y_windows"] == 600 - WIN_1Y_WINDOW)
    # S4: win_month_pos_share hand-check (rise/rise/fall -> 2/3)
    p = np.ones(64)
    p[21:42] = np.linspace(1.0, 1.10, 21)      # month 2 up
    p[42:63] = np.linspace(1.10, 1.05, 21)    # month 3 down
    m4 = _win_metrics(p, starts_3)
    # slices: [0,21) flat=0 -> not positive; [21,42) up -> positive;
    # [42,63) down -> negative => 1/3 positive
    chk("S4 win_month_pos_share hand-check == 1/3",
        abs(m4["win_month_pos_share"] - 1.0 / 3.0) < 1e-12
        and m4["n_month_slices"] == 3)
    # S5: fresh-entry engine math at a mid-window start (twin-check vs the
    # validated aps naive reference on the sliced window, rule="none")
    import pandas as pd
    rng = np.random.default_rng(7)
    dts = [d.strftime("%Y-%m-%d") for d in
           pd.bdate_range("2020-01-01", periods=700)]
    rets5 = rng.normal(0.0005, 0.01, size=(700, 4))
    tg = np.array([[0.25] * 4])
    s = 250
    sim5s = aps.simulate_with_dates(dts[s:], rets5[s:], tg,
                                    np.zeros(1, dtype=int), "none",
                                    store_path=True)
    entry = 0.75 * aps.COST_PER_SIDE
    chk("S5a fresh-entry V[0]==1-entry_cost(ETF legs)",
        abs(sim5s["path"][0, 0] - (1.0 - entry)) < 1e-12)
    v_naive, n_reb = aps._naive_sim(rets5[s:], dts[s:], tg[0], "none")
    chk("S5b sliced clean entry == aps naive reference (rule none)",
        abs(sim5s["V"][0] - v_naive) < 1e-10 and sim5s["n_reb"][0] == 0)
    sim5f = aps.simulate_with_dates(dts, rets5, tg, np.array([s]), "none",
                                    store_path=False)
    chk("S5c engine in-window fresh-entry perturbation documented "
        "(entry-day weight drift; clean sliced entry adopted for all-starts)",
        abs(sim5f["V"][0] - sim5s["V"][0]) > 1e-9)
    # S6: adjudication truth table
    base = {"allstart_pos_share": None, "allstart_median": None,
            "worst5y": None}
    c1 = dict(base, allstart_pos_share=0.60, allstart_median=0.03,
              worst5y=0.01)
    c2 = dict(base, allstart_pos_share=0.49, allstart_median=0.03,
              worst5y=0.01)
    c3 = dict(base, allstart_pos_share=0.60, allstart_median=-0.01,
              worst5y=0.01)
    c4 = dict(base, allstart_pos_share=0.60, allstart_median=0.03,
              worst5y=-0.005)
    c5 = dict(base, allstart_pos_share=0.60, allstart_median=0.03,
              worst5y=None)
    chk("S6 adjudication truth table (3-way conjunction, None fails)",
        _adjudicate(c1)["pass"] and not _adjudicate(c2)["pass"]
        and not _adjudicate(c3)["pass"] and not _adjudicate(c4)["pass"]
        and not _adjudicate(c5)["pass"])
    # S7: t_from_sharpe consistency with _path_metrics informational t
    v = np.cumprod(1.0 + rng.normal(0.0004, 0.008, size=1000))
    m7 = aps._path_metrics(v)
    chk("S7 t_info == t_from_sharpe (M1 informational face)",
        abs(m7["t_info"] - sg.t_from_sharpe(m7["sharpe"], 999)) < 1e-9)
    # S8: kin-context extraction from committed #2 fixture
    kin = _kin_context()
    chk("S8 kin-context baselines + nearest-kin cells extracted",
        "stock_bh" in kin["baselines"] and "cash_only" in kin["baselines"]
        and KIN_CELL_IDS[0] in kin["nearest_kin_cells"])
    # S9: determinism double-run (write=False) on real faces, byte-identical
    r1_ = run(write=False)
    r2_ = run(write=False)
    chk("S9 determinism double-run identical",
        json.dumps(r1_, sort_keys=True) == json.dumps(r2_, sort_keys=True))
    # BS1: Face B cell enumeration + trial count (frozen sec.3-B)
    bcells = _face_b_cells()
    ems = _ems()
    chk("BS1 face B cells = B-FULL(all rules OFF raw baseline) + "
        "B-RAND(seeded random), trials=2",
        len(bcells) == 2 and bcells[0]["cell"] == "B-FULL"
        and bcells[0]["off"] == list(ems.RULES) and "base" not in bcells[0]
        and bcells[1]["cell"] == "B-RAND" and bcells[1]["base"] == "random"
        and FACE_B_N_TRIALS == 2)
    # BS2: B-RAND seed hygiene (own band +100, clear of A-RAND 0..2 and of
    # the engine's renumbered exclusion_marginal_rand band)
    base = int(sg.SEED_REGISTRY[SEED_KEY])
    chk("BS2 B-RAND seed = own band base+100, clear of A-RAND and engine band",
        base + B_RAND_SEED_OFFSET == base + 100 and B_RAND_SEED_OFFSET > 2
        and base + B_RAND_SEED_OFFSET
        != int(sg.SEED_REGISTRY[ems.SEED_KEY]))
    # BS3: engine selection faces on synthetic matrices -- B-FULL ranks amt
    # ascending (raw baseline), B-RAND seeded reproducible + distinct cohort
    n_cs, n_ss = 14, 4
    amt_s = np.full((n_cs, n_ss), np.nan)
    close_s = np.full((n_cs, n_ss), np.nan)
    cnt_s = np.full((n_cs, n_ss), np.nan)
    stale_s = np.full((n_cs, n_ss), np.inf)
    rng_syn = np.random.default_rng(11)
    amt_s[:, 1:] = rng_syn.uniform(1e7, 1e9, (n_cs, n_ss - 1))
    close_s[:, 1:] = rng_syn.uniform(1, 50, (n_cs, n_ss - 1))
    cnt_s[:, 1:] = 300.0
    stale_s[:, 1:] = 0.0
    r1z = np.zeros(n_cs, dtype=bool)
    r2z = np.zeros(n_cs, dtype=bool)
    sb = base + B_RAND_SEED_OFFSET
    sA = ems._build_selection(amt_s, close_s, cnt_s, stale_s, r1z, r2z,
                              bcells[0], None)
    sA2 = ems._build_selection(amt_s, close_s, cnt_s, stale_s, r1z, r2z,
                               bcells[0], None)
    sR = ems._build_selection(amt_s, close_s, cnt_s, stale_s, r1z, r2z,
                              bcells[1], sb)
    sR2 = ems._build_selection(amt_s, close_s, cnt_s, stale_s, r1z, r2z,
                               bcells[1], sb)
    m = 2  # a signal month with full synthetic candidates
    exp_order = [i for i, _ in sA[m]]
    amt_col = amt_s[:, m]
    valid_sorted = sorted([i for i in range(n_cs)
                           if not np.isnan(amt_col[i])],
                          key=lambda i: (amt_col[i], i))
    chk("BS3a B-FULL rank face = amt asc top-N, deterministic",
        sA == sA2 and exp_order == valid_sorted[:ems.N_HOLDINGS])
    chk("BS3b B-RAND seeded reproducible and cohort != B-FULL",
        sR == sR2 and sR is not None and sR[m] is not None
        and {i for i, _ in sR[m]} != {i for i, _ in sA[m]})
    # BS4: adjudication mapping (worst5y from full-period metrics face)
    synth_b = {"allstart_pos_share": 0.625, "allstart_median": 0.02,
               "worst5y": 0.01}
    chk("BS4 face B criteria reuse frozen _adjudicate family "
        "(>=0.50 / median>0 / worst5y>0)",
        _adjudicate(synth_b)["pass"]
        and not _adjudicate(dict(synth_b, worst5y=-0.01))["pass"]
        and not _adjudicate(dict(synth_b, allstart_pos_share=0.49))["pass"])
    # BS5: pre-2005 calendar-bounds filter face (synthetic): rows outside
    # the calendar face are dropped pre-mapping; in-calendar rows unaffected
    cal_syn = ["2005-02-23", "2005-02-24", "2005-02-27"]
    pos_syn = {d: i for i, d in enumerate(cal_syn)}
    dates_syn = ["1991-04-03", "2005-02-23", "2005-02-24", "2005-02-28"]
    kept = [d for d in dates_syn if d >= cal_syn[0]]
    unmapped = [d for d in kept if d not in pos_syn]
    chk("BS5 calendar lower-bound filter drops pre-face rows, in-calendar "
        "unmapped still counted honest",
        kept == ["2005-02-23", "2005-02-24", "2005-02-28"]
        and unmapped == ["2005-02-28"])
    # BS6: T-134 s2 multicore conversion faces -- (a) the mkt contract FIX:
    # the object handed to ems._sim_cell must be SUBSCRIPTABLE and not a
    # bare callable (the old closure `def mkt(code)` was callable-only and
    # would die TypeError at the first marked position, r478 class);
    # (b) _fb_task inline == ProcessPool payload + double-run determinism.
    import shutil
    import tempfile
    from parallel_runner import run_cells_parallel
    tmp_b = tempfile.mkdtemp(prefix="faceb_s17_")
    cal_b: list[str] = []
    for mm in range(1, 13):
        cal_b += [f"2020-{mm:02d}-10", f"2020-{mm:02d}-25"]
    n_cal_b = len(cal_b)
    cal_pos_b = {d: i for i, d in enumerate(cal_b)}
    sig_pos_b = [1 + 2 * k for k in range(12)]
    for c, px in (("600001", 10.0), ("600002", 5.0)):
        with open(os.path.join(tmp_b, f"{c}.csv"), "w", encoding="ascii") as f:
            f.write("date,open,close,amount\n"
                    + "\n".join(f"{d},{px},{px},6000000.0" for d in cal_b)
                    + "\n")
    AMT_b = np.full((2, 12), 6e8)
    ctx_b = {"panel_dir": tmp_b, "cal_pos_of": cal_pos_b, "n_cal": n_cal_b,
             "sig_pos": sig_pos_b, "cal": cal_b, "n_sig": 12,
             "code_idx": {"600001": 0, "600002": 1}, "AMT": AMT_b,
             "codes": ["600001", "600002"]}
    _fb_init_ctx(ctx_b)
    chk("BS6a mkt contract = subscriptable ems._Mkt (non-callable; old "
        "closure was the r478-class TypeError bug)",
        hasattr(ems._MKT_CACHE, "__getitem__") and not callable(ems._MKT_CACHE))
    sel_b = [[("600001", 6e8)], []]        # buy month0, exit month1
    r_full_i = _fb_task(sel_b, None)
    r_start_i = _fb_task(sel_b, 0)
    chk("BS6b inline full-period sim trades (n_buys>0)",
        r_full_i["full_met"]["n_buys"] == 1)
    res_b = run_cells_parallel(
        [("full", _fb_task, (sel_b, None)), ("start", _fb_task, (sel_b, 0))],
        workers=2, desc="bs6", initializer=_fb_init_ctx, initargs=(ctx_b,))
    res_b.pop("__workers__")
    res_b2 = run_cells_parallel(
        [("full", _fb_task, (sel_b, None)), ("start", _fb_task, (sel_b, 0))],
        workers=2, desc="bs6b", initializer=_fb_init_ctx, initargs=(ctx_b,))
    res_b2.pop("__workers__")
    chk("BS6c face-B pool==inline identity + double-run determinism",
        json.dumps(res_b["full"], sort_keys=True)
        == json.dumps(r_full_i, sort_keys=True)
        and json.dumps(res_b["start"], sort_keys=True)
        == json.dumps(r_start_i, sort_keys=True)
        and json.dumps(res_b2["full"], sort_keys=True)
        == json.dumps(res_b["full"], sort_keys=True))
    shutil.rmtree(tmp_b, ignore_errors=True)
    print(f"selftest: {ok}/{ok} PASS")
    return 0


def main(argv):
    cmd = argv[1] if len(argv) > 1 else ""
    if cmd == "probe":
        return probe()
    if cmd == "run":
        run()
        return 0
    if cmd == "run_face_b":
        rc = run_face_b()
        return 0 if isinstance(rc, dict) else int(rc)
    if cmd == "selftest":
        return selftest()
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
