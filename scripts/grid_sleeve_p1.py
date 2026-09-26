"""T-78 s5b: GRID-SLEEVE-P1 CN grid-engine sleeve batch (5 instruments).

PRE-REGISTERED before running: research/GRID_SLEEVE_P1.md (r243 frozen
commit bd42a609; run-backfill of sec.7/8 only, no criterion edits, no
re-runs). Unlock-4 machinery face: engine/grid_sleeve.py v1 (s5a, additive
independent module) judged on its own sleeve -- house backtester /
exit_rules / frozen exit priority ZERO-TOUCH per O-0958 (c).

Faces (prereg sec.0/3 frozen, NO search -- single-point):
  5 instrument cells (fund-event-guarded live set: 510300/159915/512880/
    518880/511010; 510500 quarantined by the r239-law guard per frozen
    sec.2 probe facts) x engine v1 params (n_grids=10, band_win=250,
    nav0=1_000_000, V1 legacy 13bp x1)
  + 50 layout-sensitivity nulls (5 instruments x 10 band-phase offsets
    uniform(-1,+1) grids, seed 62500+i per SEED_REGISTRY['grid_sleeve_p1'],
    r244 registration) -- "does band placement itself carry information"
  + 5 single-ETF buy-hold passive faces (consistency info)
  = 60 N_eff trials (x2 stress faces excluded, EXIT_OVERLAY precedent).

Gates (prereg sec.4): per-cell G1' v2 via science_gates.g1_prime_v2
(data-driven skill line, zero hand-copied constants; F6 dual trade gate
on entries, n_trades face = n_round_trips = completed harvest rounds) AND
GATE-A (chop-window cumulative grid return > same-window passive return --
the grid's money claim; x2 re-eval = descriptive stability face). Survivor
(both) = science survivor; paper candidacy additionally needs D6 admission.
Judgment FAIL != machinery discard: GRID paper family wires as experimental
observation accounts regardless (CEO O-0958), science claim judged by data.

D6 wording resolution (pre-run, zero cells, r71 protocol -- GRID_P1
docstring precedent adopted verbatim): sec.1 "registered 6 + same-batch
cells" -- the REGISTERED face REJECTS (max|corr| >= 0.70 vs named six,
member_run own-cutoff equity, r69 inner-join law); the same-batch face is
disclosed per-pair and resolved at REGISTRATION time (s5c) by the
registration pipeline's existing pairwise gate, not here.

Hard gates (any FAIL = batch VOID, exit 2, no ledger): patch self-test
(live.paper.self_test_patches), 5/5 live-cell OHLCV readable at cutoff,
guard face reproduces the frozen quarantine set {510500}. Single-shot
finalize guard: OUT_JSON exists -> refuse (freeze law, no re-runs).

Usage: python scripts/grid_sleeve_p1.py run | selftest
Products: results/grid_sleeve_p1.json + research/grid_sleeve_p1_results.csv
+ gate_attrition row + trials-ledger append (finalize).
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd

from config import PATHS
from engine.grid_sleeve import (
    _selftest as engine_selftest,
    guard_event_days,
    run_grid_sleeve,
    segment_faces,
    segment_windows,
)
from engine.metrics import sharpe as _sharpe
from science_gates import SEED_REGISTRY, append_ledger, cutoff_meta, g1_prime_v2

TICKET = "T-2026-09-26-78"
PREREG_PATH = os.path.join("research", "GRID_SLEEVE_P1.md")
BATCH_CELLS = 60                 # prereg sec.0 N_eff (frozen)
N_NULL_PER = 10                  # per live instrument (prereg sec.3)
SEED_BASE = 62_500               # SEED_REGISTRY['grid_sleeve_p1'] (r244)
D6_LINE = 0.70                   # prereg sec.1 registered-face rejection
UNI_THRESH = 0.03                # guard calm-universe threshold (r239 law)
GUARD_LIMITS = {"510300": 0.105, "510500": 0.105, "512880": 0.105,
                "159915": 0.205, "518880": 0.105, "511010": 0.105}
LIVE_ORDER = ("510300", "159915", "512880", "518880", "511010")
EXPECT_QUARANTINE = {"510500"}   # frozen sec.2 probe facts (hard-gate face)
GRID_KW = {"n_grids": 10, "band_win": 250, "nav0": 1_000_000.0}
COST_BP_X1 = 13.0                # V1 legacy (smoke-verified face)
COST_BP_X2 = 26.0                # CostPatch(2) convention, engine-native
PASSIVE_COST = 13.0 / 1e4        # one-time entry cost, J8 formula precedent
SEG_LEN, CHOP_THRESH = 60, 0.10   # frozen segmenter (engine defaults)
NAMED_SIX = ("COMPOSITE-CE-01", "COMPOSITE-CE-02", "DROUGHT-CE-01",
             "ENGULF-CE-01", "NEEDLE-DE-01", "VOLATILITY-CE-01")
OUT_JSON = os.path.join("results", "grid_sleeve_p1.json")
OUT_CSV = os.path.join("research", "grid_sleeve_p1_results.csv")
ATT_JSON = os.path.join("results", "gate_attrition.json")
LOG_PATH = os.path.join("results", "grid_sleeve_p1.log")


def _log(msg):
    with open(LOG_PATH, "a", encoding="utf-8") as fh:
        fh.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}\n")
    print(f"  {msg}")


def _sha256_file(path):
    import hashlib
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def _single_shot_ok(out_path: str) -> bool:
    """Freeze law: a second product write for this batch is refused."""
    return not os.path.exists(out_path)


def _pearson(a: pd.Series, b: pd.Series) -> float:
    """Inner-join by date (members run at their own cutoffs; the tail
    short drops honestly, r69 date-alignment law, min 20 overlap)."""
    j = pd.concat([a, b], axis=1, join="inner").dropna()
    if len(j) < 20:
        return float("nan")
    c = np.corrcoef(j.iloc[:, 0], j.iloc[:, 1])[0, 1]
    return float(c) if np.isfinite(c) else float("nan")


def null_offset(seed: int) -> float:
    """Prereg sec.3 null recipe: band-phase offset uniform(-1,+1) grids."""
    return float(np.random.default_rng(seed).uniform(-1.0, 1.0))


def gate_a_of(face: dict) -> bool:
    """GATE-A (prereg sec.4): chop-window cumulative grid return strictly
    greater than the same-window passive return. No chop windows = honest
    False (zero > zero is not a grid win)."""
    cum = face["chop"]["cum"]
    return bool(cum["n"] > 0 and cum["grid_cum"] > cum["passive_cum"])


def seg_capture(sells: list, segs: list, nav0: float) -> dict:
    """Per-segment lot-PnL capture rate (prereg sec.4 descriptive:
    capture rate = sum(lot pnl) / NAV_0 per segment window)."""
    by_label = {"chop": 0.0, "trend_up": 0.0, "trend_down": 0.0}
    n_by_label = {"chop": 0, "trend_up": 0, "trend_down": 0}
    for seg in segs:
        s, e = seg["start"], seg["end"]
        tot = sum(s2["pnl"] for s2 in sells
                  if s2.get("_pos") is not None and s <= s2["_pos"] <= e)
        by_label[seg["label"]] += tot
        n_by_label[seg["label"]] += 1
    return {k: {"capture": round(v / nav0, 6), "n_windows": n_by_label[k]}
            for k, v in by_label.items()}


# ---------------- selftest (hermetic: synthetic panels, zero repo data) --

def selftest() -> int:
    ok_all = True

    def ok(name, cond):
        nonlocal ok_all
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
        ok_all &= bool(cond)
        return cond

    # [1/8] engine machinery selftest (production form, mirror law)
    ok("engine grid_sleeve 8/8 (production engine)", engine_selftest())

    # [2/8] guard wiring: idio jump flagged, 20cm limit honored, market-wide
    #       extreme not flagged (runner face construction, mirror law)
    idx = pd.bdate_range("2020-01-02", periods=300)
    uni_calm = pd.Series(0.005, index=idx)     # calm universe median |r1|
    uni_mkt = pd.Series(0.05, index=idx)       # market-wide extreme day
    c10 = pd.Series(np.full(300, 100.0), index=idx)
    c10.iloc[250:] = c10.iloc[250] * 0.85      # one -15% level shift
    c20 = pd.Series(np.full(300, 100.0), index=idx)
    c20.iloc[250:] = c20.iloc[250] * 0.82      # fresh base: day-250 close
    # (r1 = 82/100 - 1 = -18%, inside the 20cm 0.205 limit; building c20
    # off the already-shifted c10 would make day-250 r1 = 69.7/100 = -30.3%
    # -- fixture must derive from the UNshifted prev close)
    ok("guard: 10cm idio jump flagged",
       len(guard_event_days(c10, 0.105, uni_calm, UNI_THRESH)) == 1)
    ok("guard: 20cm limit not flagged at -18%",
       len(guard_event_days(c20, 0.205, uni_calm, UNI_THRESH)) == 0)
    ok("guard: market-wide extreme not flagged",
       len(guard_event_days(c10, 0.105, uni_mkt, UNI_THRESH)) == 0)

    # [3/8] null recipe: deterministic, in-band, 50 distinct seeds, registry
    seeds = [SEED_BASE + j * N_NULL_PER + k for j in range(5)
             for k in range(N_NULL_PER)]
    offs = [null_offset(s) for s in seeds]
    ok("nulls: 50 distinct seeds in band, offsets bounded+reproducible",
       len(set(seeds)) == 50 and min(seeds) == 62_500
       and max(seeds) == 62_549
       and all(-1.0 <= o <= 1.0 for o in offs)
       and offs == [null_offset(s) for s in seeds])
    reg_vals = [v for v in SEED_REGISTRY.values() if isinstance(v, int)]
    ok("registry: grid_sleeve_p1 registered, base not double-booked",
       SEED_REGISTRY.get("grid_sleeve_p1") == 62_500
       and sum(1 for v in reg_vals if v == 62_500) == 1)
    # (full-registry value uniqueness is NOT asserted: documented same-base
    # disclosures exist on purpose, p1d_gdhs_quarterly == p4_pairs 48_000)

    # [4/8] D6 pearson: inner-join min-20 law (r69)
    a = pd.Series(np.random.default_rng(1).normal(0, 0.01, 60),
                  index=pd.bdate_range("2024-01-01", periods=60))
    b = pd.Series(np.random.default_rng(2).normal(0, 0.01, 60),
                  index=pd.bdate_range("2024-01-01", periods=60))
    b_short = b.iloc[50:]                      # only 10 overlapping days
    ok("pearson: 60-day overlap finite, <20 overlap honest nan",
       np.isfinite(_pearson(a, b)) and np.isnan(_pearson(a, b_short)))

    # [5/8] GATE-A math: chop win and chop loss faces (engine segmenter)
    nav_win = pd.Series(np.linspace(1.0, 1.20, 120),
                        index=pd.bdate_range("2024-01-01", periods=120))
    close_flat = pd.Series(np.full(120, 100.0),
                           index=nav_win.index)  # |r|~0 < 0.10 -> chop
    f_win = segment_faces(nav_win, close_flat, SEG_LEN, CHOP_THRESH)
    nav_lose = pd.Series(np.linspace(1.0, 0.95, 120), index=nav_win.index)
    f_lose = segment_faces(nav_lose, close_flat, SEG_LEN, CHOP_THRESH)
    ok("gate-a: chop grid>passive True / grid<passive False",
       gate_a_of(f_win) is True and gate_a_of(f_lose) is False
       and gate_a_of({"chop": {"cum": {"n": 0, "grid_cum": 0.0,
                                       "passive_cum": 0.0}}}) is False)

    # [6/8] passive formula: one-time entry cost buy-hold (J8 precedent)
    px = pd.Series(np.array([100.0, 102.0, 99.0, 101.0, 105.0]),
                   index=pd.bdate_range("2024-01-01", periods=5))
    nav_p = (px / px.iloc[0]) * (1 - PASSIVE_COST)
    ok("passive: entry-cost buy-hold nav formula",
       abs(nav_p.iloc[0] - (1 - PASSIVE_COST)) < 1e-12
       and abs(nav_p.iloc[-1] - 1.05 * (1 - PASSIVE_COST)) < 1e-12)

    # [7/8] per-segment capture: sells attribution == totals (self-consistency)
    sells = [{"pnl": 10.0, "_pos": 5}, {"pnl": -4.0, "_pos": 65},
             {"pnl": 6.0, "_pos": 61}]
    segs = segment_windows(pd.Series(np.full(130, 100.0)), SEG_LEN,
                           CHOP_THRESH)
    cap = seg_capture(sells, segs, 1_000.0)
    tot = (10.0 - 4.0 + 6.0) / 1_000.0
    ok("capture: per-segment sums == total lot pnl",
       abs(sum(v["capture"] for v in cap.values()) - tot) < 1e-9)

    # [8/8] single-shot freeze guard bites (real path probe, hermetic)
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        probe = os.path.join(td, "probe.json")
        ok("single-shot guard: nonexistent -> ok, existing -> refuse",
           _single_shot_ok(probe) is True)
        with open(probe, "w", encoding="utf-8") as fh:
            fh.write("{}")
        ok("single-shot guard: existing product -> refuse (freeze law)",
           _single_shot_ok(probe) is False)

    if not ok_all:
        print("SELFTEST FAILED -- batch refused (fake-evidence guard)")
        return 2
    print("selftest: ALL LEGS PASS")
    return 0


# ------------------------------ the batch --------------------------------

def _load_instrument(code: str, cutoff: pd.Timestamp):
    """data/daily single-instrument OHLCV at cutoff (prereg sec.2: repo
    data only, zero new sources)."""
    path = os.path.join(PATHS.daily_dir, f"{code}.csv")
    df = pd.read_csv(path, parse_dates=["date"]).set_index("date").sort_index()
    df = df[df.index <= cutoff]
    for col in ("open", "close"):
        if col not in df.columns or df[col].isna().any():
            raise ValueError(f"{code}: {col} face missing/NaN")
    if len(df) < GRID_KW["band_win"] + 2:
        raise ValueError(f"{code}: {len(df)} bars < band_win+2")
    return df


def _finalize(out: dict, void: bool) -> int:
    """Single-shot product write + attrition row (freeze law). The ledger
    is appended by the CALLER (pure function, dict must be embedded --
    r217 law) before this is invoked on the non-void path."""
    if not _single_shot_ok(OUT_JSON):
        print("finalize refused: OUT_JSON exists (single-shot guard, "
              "freeze law -- no re-runs)")
        return 2
    attrition_row = out.pop("_attrition_row", None)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2, default=str)
    print(f"saved: {OUT_JSON} (void={void})")
    if void:
        return 2
    with open(ATT_JSON, encoding="utf-8") as fh:
        att = json.load(fh)
    att["entries"].append(attrition_row)
    with open(ATT_JSON, "w", encoding="utf-8") as fh:
        json.dump(att, fh, ensure_ascii=False, indent=2)
    total = (out.get("trials_ledger") or {}).get("total")
    print(f"gate_attrition appended (ledger total -> {total})")
    return 0


def _void_product(cutoff, guard_face, reason, t0, prereg_sha):
    return _finalize({
        "batch": "GRID-SLEEVE-P1", "ticket": TICKET,
        "prereg": PREREG_PATH, "prereg_sha256_16": prereg_sha,
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        **cutoff_meta(cutoff),
        "guard_face": guard_face,
        "void": True, "void_reason": reason,
        "audit": {"elapsed_sec": round(time.time() - t0, 1)},
    }, void=True)


def main() -> int:
    t0 = time.time()
    n_runs = 0
    prereg_sha = _sha256_file(PREREG_PATH)[:16]

    # ---- hard gate 1: patch self-test (fake-evidence guard) ----
    from live.paper import build_panels, load_core, self_test_patches
    if not self_test_patches():
        _log("patch self-test FAILED -- batch void (exit 2, no product)")
        return 2
    _log("patch self-tests: PASS")

    # ---- panel: 6 frozen instruments, cutoff = latest complete bar ----
    raw_end, panels = {}, {}
    for code in GUARD_LIMITS:
        df = pd.read_csv(os.path.join(PATHS.daily_dir, f"{code}.csv"),
                         parse_dates=["date"]).set_index("date").sort_index()
        raw_end[code] = str(df.index[-1].date())
    cutoff = min(raw_end.values())            # latest COMPLETE bar (sec.2)
    ps = pd.Timestamp(cutoff)
    for code in GUARD_LIMITS:
        df = pd.read_csv(os.path.join(PATHS.daily_dir, f"{code}.csv"),
                         parse_dates=["date"]).set_index("date").sort_index()
        panels[code] = df[df.index <= ps]
    _log(f"panel: 6 frozen ETFs, cutoff={cutoff} "
         f"(raw ends {sorted(set(raw_end.values()))})")

    # ---- hard gate 2: guard face reproduces frozen quarantine set ----
    prices_core = load_core()
    core_close = build_panels(prices_core)["close"]
    uni_med = core_close.pct_change().abs().median(axis=1)
    guard_face, quarantined = {}, set()
    for code, limit in GUARD_LIMITS.items():
        days = guard_event_days(panels[code]["close"], limit, uni_med,
                                UNI_THRESH)
        guard_face[code] = {
            "limit": limit,
            "event_days": [str(d.date()) for d in days],
            "quarantined": bool(days),
        }
        if days:
            quarantined.add(code)
    _log(f"guard: quarantined={sorted(quarantined)} "
         f"(frozen expectation {sorted(EXPECT_QUARANTINE)})")
    live = tuple(c for c in LIVE_ORDER if c not in quarantined)
    if quarantined != EXPECT_QUARANTINE or len(live) != 5:
        return _void_product(
            cutoff, guard_face,
            f"guard face mismatch: quarantined={sorted(quarantined)} != "
            f"frozen {sorted(EXPECT_QUARANTINE)} (sec.2 hard gate)", t0,
            prereg_sha)
    # ---- hard gate 3: live cells 5/5 readable at cutoff ----
    try:
        for code in live:
            _load_instrument(code, ps)
    except (OSError, ValueError) as ex:
        return _void_product(
            cutoff, guard_face,
            f"live-cell OHLCV unreadable at cutoff: {ex}", t0, prereg_sha)
    _log("hard gates: patch PASS, live 5/5 readable, guard reproduced")

    # ---- cells: 5 live instruments x engine v1 (x1 primary) ----
    cells = {}
    for code in live:
        df = _load_instrument(code, ps)
        r = run_grid_sleeve(df["open"], df["close"], df.index,
                            cost_bp=COST_BP_X1, **GRID_KW)
        n_runs += 1
        rets = r["nav"].pct_change().dropna()
        face = segment_faces(r["nav"], df["close"], SEG_LEN, CHOP_THRESH)
        segs = segment_windows(df["close"], SEG_LEN, CHOP_THRESH)
        pos_map = {d: i for i, d in enumerate(df.index)}
        sells = [{**s, "_pos": pos_map[s["date"]]} for s in r["sells"]]
        capture = seg_capture(sells, segs, GRID_KW["nav0"])
        cells[code] = {
            "params": r["params"], "sharpe": r["sharpe"], "mdd": r["mdd"],
            "ann": r["ann"], "n_round_trips": r["n_round_trips"],
            "n_entries": r["n_entries"], "n_trades": r["n_trades"],
            "skipped_buys": r["skipped_buys"],
            "harvest_pnl": r["harvest_pnl"],
            "whipsaw_pnl": r["whipsaw_pnl"],
            "capture_rate_total": round(
                (r["harvest_pnl"] + r["whipsaw_pnl"]) / GRID_KW["nav0"], 6),
            "segment_capture": capture,
            "segment_faces": face,
            "gate_a": gate_a_of(face),
            "_rets": rets,
            "_sells_log": [{"date": str(s["date"].date()), "kind": s["kind"],
                            "pnl": round(s["pnl"], 2)} for s in r["sells"]],
        }
        _log(f"cell {code}: s={r['sharpe']:.4f} ann={r['ann']:.4f} "
             f"rt={r['n_round_trips']} entries={r['n_entries']} "
             f"gate_a={cells[code]['gate_a']}")

    # ---- x2 stress faces (descriptive stability, never a gate) ----
    x2 = {}
    for code in live:
        df = _load_instrument(code, ps)
        r2 = run_grid_sleeve(df["open"], df["close"], df.index,
                             cost_bp=COST_BP_X2, **GRID_KW)
        n_runs += 1
        f2 = segment_faces(r2["nav"], df["close"], SEG_LEN, CHOP_THRESH)
        x2[code] = {"sharpe": r2["sharpe"], "ann": r2["ann"],
                    "gate_a": gate_a_of(f2),
                    "chop_cum": f2["chop"]["cum"]}
        _log(f"stress {code} x2: s={r2['sharpe']:.4f} "
             f"gate_a={x2[code]['gate_a']}")

    # ---- nulls: 50 layout-sensitivity offsets (prereg sec.3) ----
    nulls = []
    for j, code in enumerate(live):
        df = _load_instrument(code, ps)
        for k in range(N_NULL_PER):
            seed = SEED_BASE + j * N_NULL_PER + k
            off = null_offset(seed)
            r = run_grid_sleeve(df["open"], df["close"], df.index,
                                cost_bp=COST_BP_X1,
                                band_offset_grids=off, **GRID_KW)
            n_runs += 1
            nulls.append({"code": code, "seed": seed,
                          "offset": round(off, 6),
                          "sharpe": r["sharpe"], "ann": r["ann"],
                          "n_round_trips": r["n_round_trips"]})
        vals = [n["sharpe"] for n in nulls if n["code"] == code]
        _log(f"nulls {code}: n={N_NULL_PER} mu={np.mean(vals):.4f} "
             f"max={max(vals):.4f}")

    # ---- passive: 5 single-ETF buy-hold faces (consistency info) ----
    passive = {}
    for code in live:
        df = _load_instrument(code, ps)
        nav = (df["close"] / df["close"].iloc[0]) * (1 - PASSIVE_COST)
        passive[f"passive_bh_{code}"] = {
            "sharpe": float(_sharpe(nav)),
            "total_return": float(nav.iloc[-1] - 1.0),
            "note": "buy-hold, one-time 13bp entry cost (J8 precedent)"}
    _log("passive: 5 buy-hold faces computed")

    # ---- D6 reference: registered six, member_run own cutoffs ----
    from firm.hr import load_trader
    from p3_portfolio import member_run
    member_rets, member_meta = {}, {}
    for tid in NAMED_SIX:
        r1 = member_run(load_trader(tid), prices_core, None)
        n_runs += 1
        member_rets[tid] = r1["eq"].pct_change().dropna()
        member_meta[tid] = {"cutoff": r1["cutoff"],
                            "full_sharpe": round(r1["full"]["sharpe"], 4)}
        _log(f"member {tid}: s={r1['full']['sharpe']:.4f} "
             f"cutoff={r1['cutoff']}")

    # ---- verdict faces: G1'v2 + GATE-A per cell; D6 admission ----
    cand, d6_rejects = [], []
    for code in live:
        c = cells[code]
        g1 = g1_prime_v2(c["sharpe"], c["_rets"], BATCH_CELLS,
                         n_trades=c["n_round_trips"],
                         n_entries=c["n_entries"])
        reg_max, reg_arg = 0.0, None
        for tid, rseries in member_rets.items():
            cc = abs(_pearson(c["_rets"], rseries))
            if np.isfinite(cc) and cc > reg_max:
                reg_max, reg_arg = cc, tid
        same_batch = {oc: round(abs(_pearson(c["_rets"],
                                             cells[oc]["_rets"])), 4)
                      for oc in live if oc != code}
        reg_ok = bool(reg_max < D6_LINE)
        if not reg_ok:
            d6_rejects.append(code)
        chop_cum = c["segment_faces"]["chop"]["cum"]
        trend_up = c["segment_faces"]["trend_up"]["cum"]
        trend_down = c["segment_faces"]["trend_down"]["cum"]
        cand.append({
            "code": code,
            "sharpe_full": c["sharpe"], "ann": c["ann"], "mdd": c["mdd"],
            "n_round_trips": c["n_round_trips"],
            "n_entries": c["n_entries"],
            "harvest_pnl": c["harvest_pnl"],
            "whipsaw_pnl": c["whipsaw_pnl"],
            "capture_rate_total": c["capture_rate_total"],
            "segment_capture": c["segment_capture"],
            "g1_prime_v2": g1, "g1_pass": bool(g1["pass_v2"]),
            "gate_a": c["gate_a"],
            "chop_face": {"grid_cum": chop_cum["grid_cum"],
                          "passive_cum": chop_cum["passive_cum"],
                          "n": chop_cum["n"]},
            "descriptive": {
                "ann_positive": bool(c["ann"] > 0),
                "dd_ok": bool(c["mdd"] >= -0.35),
                "trend_up_opportunity_gap": round(
                    trend_up["passive_cum"] - trend_up["grid_cum"], 6),
                "trend_down_whipsaw_cost": round(
                    trend_down["grid_cum"] - trend_down["passive_cum"], 6),
                "skipped_buys": c["skipped_buys"],
            },
            "d6": {"max_corr_vs_registered": round(reg_max, 4),
                   "vs_registered_argmax": reg_arg,
                   "registered_ok": reg_ok,
                   "same_batch_pairwise": same_batch},
            "x2_stress": x2[code],
        })
    survivors_science = [r["code"] for r in cand
                         if r["g1_pass"] and r["gate_a"]]
    paper_candidates = [r["code"] for r in cand
                        if r["g1_pass"] and r["gate_a"]
                        and r["d6"]["registered_ok"]]
    for r in cand:
        r["survivor_science"] = r["code"] in survivors_science
        r["paper_candidate"] = r["code"] in paper_candidates
        _log(f"verdict {r['code']}: g1={r['g1_pass']} "
             f"line_ok={r['g1_prime_v2']['line_ok']} "
             f"ci_ok={r['g1_prime_v2']['ci_lower_bound_positive']} "
             f"gate_a={r['gate_a']} d6={r['d6']['registered_ok']} "
             f"-> {'CANDIDATE' if r['paper_candidate'] else 'no'}")

    # ---- products: ledger (caller-embedded) + JSON + attrition + CSV ----
    null_summary = {
        "n": len(nulls),
        "mu": round(float(np.mean([n["sharpe"] for n in nulls])), 4),
        "sigma": round(float(np.std([n["sharpe"] for n in nulls],
                                    ddof=1)), 4),
        "by_code": {code: {
            "mu": round(float(np.mean([n["sharpe"] for n in nulls
                                       if n["code"] == code])), 4),
            "sigma": round(float(np.std([n["sharpe"] for n in nulls
                                         if n["code"] == code], ddof=1)), 4),
            "max": round(max(n["sharpe"] for n in nulls
                             if n["code"] == code), 4),
            "cell_beats_null_max": bool(
                cells[code]["sharpe"] > max(n["sharpe"] for n in nulls
                                            if n["code"] == code)),
        } for code in live},
        "question": "band-placement information: random phase offsets "
                    "uniform(-1,+1) grids; cell<=null band => placement "
                    "carries no gain (descriptive, not a gate)",
    }
    led = append_ledger(
        "GRID-SLEEVE-P1", BATCH_CELLS, "results/grid_sleeve_p1.json",
        note="5 cells + 50 layout nulls + 5 passive (N_eff=60 frozen "
             "sec.0); x2 stress faces + 6 member_run D6 references "
             "disclosed in audit only (EXIT_OVERLAY precedent)",
        evidence_cutoff=cutoff)
    line_val = cand[0]["g1_prime_v2"]["skill_line"]["line"] if cand else None
    attrition_row = {
        "batch": "GRID-SLEEVE-P1",
        "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
        "kind": "measurement", "retro_fill": False,
        "cells_ledger_delta": BATCH_CELLS,
        "ledger_total_after": led["total"],
        "gates": {
            "skill_line_v2": line_val,
            "g1_prime_v2_pass": len([r for r in cand if r["g1_pass"]]),
            "gate_a_pass": len([r for r in cand if r["gate_a"]]),
            "survivors_science": len(survivors_science),
            "paper_candidates": len(paper_candidates),
            "d6_registered_rejects": d6_rejects,
            "void": False,
        },
        "eliminated": (len(cand) - len(survivors_science)) if cand else 0,
        "refs": {"results": "results/grid_sleeve_p1.json",
                 "prereg": PREREG_PATH,
                 "csv": "research/grid_sleeve_p1_results.csv",
                 "ticket": f"fleet/tasks/{TICKET}-P1.json"},
    }

    def _public(code):
        c = cells[code]
        return {k: v for k, v in c.items()
                if k not in ("_rets", "_sells_log")}

    out = {
        "batch": "GRID-SLEEVE-P1", "ticket": TICKET,
        "prereg": PREREG_PATH, "prereg_sha256_16": prereg_sha,
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        **cutoff_meta(cutoff),
        "void": False,
        "universe": {"frozen_six": list(GUARD_LIMITS), "live": list(live),
                     "quarantined": sorted(quarantined),
                     "raw_ends": raw_end,
                     "history": (f"{min(panels[c].index[0] for c in live).date()} "
                                 f".. {cutoff} (sec.2 lockbox)")},
        "hard_gates": {"patch_selftest": True, "live_5of5_readable": True,
                       "guard_face_reproduced": True},
        "guard_face": guard_face,
        "grid_params": GRID_KW,
        "segmenter": {"seg_len": SEG_LEN, "chop_thresh": CHOP_THRESH},
        "cost": "V1 legacy 13bp x1 primary + engine-native 26bp x2 stress",
        "d6_wording_resolution": ("registered face REJECTS (>=0.70); "
                                 "same-batch pairwise disclosed, resolved "
                                 "at registration (s5c) -- GRID_P1 r71 "
                                 "protocol, frozen in runner docstring "
                                 "pre-run"),
        "candidates": cand,
        "cells_public": {code: _public(code) for code in live},
        "cells_sells_log": {code: cells[code]["_sells_log"]
                            for code in live},
        "nulls": nulls, "null_summary": null_summary,
        "passive": passive,
        "registered_members_d6_ref": member_meta,
        "survivors_science": survivors_science,
        "paper_candidates": paper_candidates,
        "verdict_note": ("science survivor = G1'v2 AND GATE-A (sec.4); "
                         "paper candidacy additionally requires D6 < 0.70 "
                         "registered-face; FAIL != machinery discard -- "
                         "GRID paper family wires as experimental "
                         "observation accounts regardless (CEO O-0958)"),
        "_attrition_row": attrition_row,
        "trials_ledger": led,
        "audit": {"elapsed_sec": round(time.time() - t0, 1),
                  "n_backtests": n_runs,
                  "workers": 1, "cpu_parallel": "serial (single-process)",
                  "ledger_n_eff": BATCH_CELLS,
                  "audit_note": (f"{n_runs} engine sims (5 cells x1 + 5 x2 "
                                 f"+ 50 nulls + 6 member_run D6 refs) + 5 "
                                 f"passive formulas; ledger counts N_eff=60 "
                                 f"only, x2/member faces audit-only")},
    }
    rc = _finalize(out, void=False)
    if rc == 0:
        _csv(cand, nulls, passive)
    return rc


def _csv(cand, nulls, passive):
    import csv
    base_cols = ["code", "face", "sharpe", "ann", "mdd", "n_round_trips",
                 "n_entries", "skill_line", "line_ok", "ci_ok",
                 "trade_entries_ok", "g1_pass", "gate_a", "chop_grid_cum",
                 "chop_passive_cum", "capture_rate_total", "harvest_pnl",
                 "whipsaw_pnl", "max_corr_vs_registered",
                 "vs_registered_argmax", "registered_ok",
                 "survivor_science", "paper_candidate", "x2_sharpe",
                 "x2_gate_a", "note"]
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=base_cols)
        w.writeheader()
        for r in cand:
            w.writerow({
                "code": r["code"], "face": "cell_x1",
                "sharpe": r["sharpe_full"], "ann": r["ann"],
                "mdd": r["mdd"], "n_round_trips": r["n_round_trips"],
                "n_entries": r["n_entries"],
                "skill_line": r["g1_prime_v2"]["skill_line"]["line"],
                "line_ok": r["g1_prime_v2"]["line_ok"],
                "ci_ok": r["g1_prime_v2"]["ci_lower_bound_positive"],
                "trade_entries_ok": r["g1_prime_v2"]["trade_gate"]["entries_ok"],
                "g1_pass": r["g1_pass"], "gate_a": r["gate_a"],
                "chop_grid_cum": r["chop_face"]["grid_cum"],
                "chop_passive_cum": r["chop_face"]["passive_cum"],
                "capture_rate_total": r["capture_rate_total"],
                "harvest_pnl": r["harvest_pnl"],
                "whipsaw_pnl": r["whipsaw_pnl"],
                "max_corr_vs_registered": r["d6"]["max_corr_vs_registered"],
                "vs_registered_argmax": r["d6"]["vs_registered_argmax"],
                "registered_ok": r["d6"]["registered_ok"],
                "survivor_science": r["survivor_science"],
                "paper_candidate": r["paper_candidate"],
                "x2_sharpe": r["x2_stress"]["sharpe"],
                "x2_gate_a": r["x2_stress"]["gate_a"]})
        for n in nulls:
            w.writerow({"code": n["code"], "face": "null_layout",
                        "sharpe": n["sharpe"], "ann": n["ann"],
                        "n_round_trips": n["n_round_trips"],
                        "note": f"seed={n['seed']} offset={n['offset']}"})
        for name, p in passive.items():
            w.writerow({"code": name, "face": "passive_bh",
                        "sharpe": p["sharpe"],
                        "note": p["note"]})
    print(f"saved: {OUT_CSV}")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "selftest":
        sys.exit(selftest())
    if mode != "run":
        # fail-closed argv (r232 law): unknown/missing arg -> usage, exit 2,
        # NEVER a silent production path
        print(f"usage: {sys.argv[0]} [run|selftest] (got {mode!r})")
        sys.exit(2)
    sys.exit(main())
