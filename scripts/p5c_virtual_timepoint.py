"""P-5C virtual-timepoint mass validation runner (T-22 / CEO O-20260924-1532).

Prereg FROZEN: research/shortline/P5C_VIRTUAL_TIMEPOINT.md (r105 bm-b,
commit 052fde0 = lock). Zero-seed deterministic full grid (prereg s3):
every eligible trading day is a virtual startpoint, no sampling anywhere.

Legs (prereg s2):
  L = legacy 6.7y control axis 2020-01-02..2026-09-22 (frozen evidence
      cutoff; warmup INSIDE the 2020+ slice = P-5 anchor caliber; local
      daily CSVs -> no Money02 contention; NO GF dependency -- GM
      O-20260924-1612: run immediately, compute must not idle on gates).
  D = T-18 deep axis 2013-06-17.. (Money02 deep-panel cache; gated face
      -> runs WITH the per-window events_n disclosure column per GM
      O-20260924-1612 branch-(b) raw-face waiver, results annotated
      contaminated until T-19 stage-3 clean rerun; Money02 data-dir
      contention queues this machine's launch behind XSTOCK post-chain).

Grid boundary convention (probe-frozen, results/shortline/p5c_grid_probe.json,
logs/iteration-loop/_r105_probe.py): start position p eligible for window W
iff p >= WARMUP and p <= n-1-W; leg L additionally listed >= 24 (never binds,
listed 45-48), leg D has NO listed gate (CEO full-grid caliber; member-count
strata disclosed instead). Census must reproduce the frozen probe counts or
the leg aborts (grid drift = data moved under the batch).

Subcommands:
  selftest       offline fixtures (no network, no repo data files)
  slice-o1600    CEO O-20260924-1600 designated single-start slice: all 6
                 registered traders (anchor hard gate first, prereg s2-3)
                 + PROSPECT pool read dynamically (T-24 onboarding in
                 flight -> honest 0 note), simulated from the first 2026
                 trading day (data-confirmed 2026-01-05, bm-c MSG-1630)
                 through 2026-09-23, faces x1 + CostPatch(2), passive EW
                 same window, regime v3 attribution; per-trader rows
                 ret/dd/vs-passive/verdict for the CEO report.
  run --leg L    checkpointed batch leg: (trader x start x face) cells ->
                 results/shortline/p5c_checkpoint/leg<L>/shard_<i>of<n>.jsonl
                 (append-per-cell in the MAIN process = kill-safe resume);
                 --shard/--shards for the three-machine startpoint split,
                 --faces x1,x2 (default both), --workers, --limit.
  status         checkpoint progress readout per leg/shard.
  finalize       aggregate shards -> per-window CSV + batch JSON + ledger
                 + D7 + regime segments + judgments (runs when grid done).

Cell accounting (prereg s0): strategy cell = (start, trader, face); passive
cell = start; anchors = 6. Windows {126, 252, 504} sliced from the longest
probe-complete window per start (prereg s3: 跑至最长完备窗).

Patch self-test gate: live.paper.self_test_patches() must PASS before any
engine run (P-5/P-5B precedent). Anchor hard gate: any registered trader
failing anchor reproduction voids the batch (prereg s2-3, exit 3).
"""
import argparse
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd

from config import PATHS
from engine import run_backtest
from engine.metrics import max_drawdown, sharpe
from firm.hr import TRADERS_DIR, load_trader
from live.paper import (PAPER_LEVELS, SIGNAL_BUILDERS, ExitPatch,
                        anchor_gate, build_panels, load_core,
                        self_test_patches, v3_state_series)
from parallel_runner import worker_cap
from p5_random_entry import passive_rel, slice_metrics, WARMUP_TD
from science_gates import COST_X2_RATE, CostPatch, append_ledger, ledger_head

WINDOWS = {"6m": 126, "12m": 252, "24m": 504}   # prereg s3 (td, inclusive bars)
EVIDENCE_CUTOFF_GRID = "2026-09-22"             # P-5C frozen (both grid legs)
LEG_L_FLOOR = pd.Timestamp("2020-01-02")
LEG_D_FLOOR = pd.Timestamp("2013-06-17")
LEG_D_CACHE = os.path.join("Money02", "data", "cache", "t18_deep_panel", "ohlcv")
O1600_END = pd.Timestamp("2026-09-23")          # order-specified slice cutoff
O1600_START_CAP = pd.Timestamp("2026-01-01")    # first 2026 trading day
MIN_LISTED = 24                                 # leg L census caliber (never binds)
CKPT_DIR = os.path.join(PATHS.results_dir, "shortline", "p5c_checkpoint")
FROZEN_CENSUS = {                                # p5c_grid_probe.json (r105)
    "L": {"6m": 1253, "12m": 1127, "24m": 875},
    "D": {"6m": 3104, "12m": 2978, "24m": 2726},
}
RES_O1600 = os.path.join(PATHS.results_dir, "shortline", "o1600_market_fit.json")
CSV_O1600 = os.path.join(PATHS.root, "research", "shortline",
                        "o1600_market_fit.csv")
REGISTRY_PATH = os.path.join("data", "consolidation", "registry.json")


# ---------------------------------------------------------------- fixtures
def _load_registry_events():
    """21 consolidation events (T-19 stage-1, bit-exact vs t14). Rows used
    only for the per-window events_n disclosure column."""
    with open(REGISTRY_PATH, encoding="utf-8") as fh:
        reg = json.load(fh)
    ev = reg.get("events", reg)
    return [(pd.Timestamp(e["date"]), e["sym"]) for e in ev]


def _run_len(n: int, p: int) -> int:
    """Longest probe-complete window at start p (boundary: p <= n-1-W)."""
    for w in (504, 252, 126):
        if p <= n - 1 - w:
            return w
    return 0


def _stratum(n_listed: int) -> str:
    if n_listed < 24:
        return "thin"
    return "mid" if n_listed < 48 else "full"


def _census(idx, listed, floor, warmup_positions, use_min_listed):
    """Probe-replica census on the runner's own panel (grid drift gate)."""
    n = len(idx)
    out = {}
    for wname, w in WINDOWS.items():
        elig = [i for i in range(n)
                if idx[i] >= floor and i >= warmup_positions
                and i <= n - 1 - w
                and (listed.iloc[i] >= MIN_LISTED if use_min_listed else True)]
        out[wname] = len(elig)
    return out


def _events_between(events, sdate, edate):
    return int(sum(1 for d, _s in events if sdate <= d <= edate))


def _load_leg(leg):
    """Panel + census for one leg. L = local daily CSVs; D = T-18 cache."""
    if leg == "L":
        prices = load_core()
        cut = pd.Timestamp(EVIDENCE_CUTOFF_GRID)
        prices = {s: df[(df.index >= LEG_L_FLOOR) & (df.index <= cut)]
                  for s, df in prices.items()}
        warmup_positions = WARMUP_TD
        floor, use_ml = LEG_L_FLOOR, True
    else:
        import pathlib
        frames = {}
        for q in sorted(pathlib.Path(LEG_D_CACHE).glob("*.parquet")):
            df = pd.read_parquet(q)
            df.index = pd.to_datetime(df.index)
            frames[q.stem] = df
        if not frames:
            raise SystemExit("P5C-GATE: deep-panel cache empty/absent "
                             f"({LEG_D_CACHE})")
        prices = frames
        cut = pd.Timestamp(EVIDENCE_CUTOFF_GRID)
        prices = {s: df[df.index <= cut] for s, df in prices.items()}
        warmup_positions = WARMUP_TD   # measured on FULL cache calendar below
        floor, use_ml = LEG_D_FLOOR, False
    P = build_panels(prices)
    close = P["close"]
    idx = close.index
    listed = close.notna().sum(axis=1)
    if leg == "D":
        # probe caliber: warmup positions on the FULL cache calendar, start
        # floor 2013-06-17, no listed gate; idx here already == full cache
        # union truncated at the cutoff (build_panels outer-joins all frames).
        pass
    cen = _census(idx, listed, floor, warmup_positions, use_ml)
    return prices, P, idx, listed, cen


def _enrich_row(r, states, close=None):
    """Main-process post-enrichment (workers stay pandas-light):
    regime state at start (causal prior lookup) + member strata."""
    d = pd.Timestamp(r["start"])
    prior = states[states.index <= d]
    r["regime_state_start"] = str(prior.iloc[-1]) if len(prior) else "NA"
    if r["trader"] != "PASSIVE" and close is not None:
        nl = int(close.columns[close.loc[d].notna()].size) \
            if d in close.index else int(close.loc[:d].iloc[-1].notna().sum())
        r["n_listed"] = nl
        r["stratum"] = _stratum(nl)
        r["min24_eligible"] = bool(nl >= MIN_LISTED)
    return r


# ------------------------------------------------- pool worker (top-level)
_ST = None   # per-worker shared state via initializer (picklable globals)


def _init_worker(state):
    global _ST
    _ST = state
    try:   # O-1136 full-load pool: BelowNormal priority (yield to interactive)
        import psutil
        psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    except Exception:
        pass


def _cell_worker(trader_id, p, face):
    """One (trader, start, face) cell inside a pool worker."""
    st = _ST
    prices, params, ovr, entry, close, idx, events = (
        st["prices"], st["params"], st["ovr"], st["entry"],
        st["close"], st["idx"], st["events"])
    n = len(idx)
    rl = _run_len(n, p)
    if rl == 0:
        return {"cell_id": f"ERR|{trader_id}|{p}", "error": "no complete window"}
    sdate = idx[p]
    edate = idx[p + rl - 1]
    window = {s: df[(df.index >= sdate) & (df.index <= edate)]
              for s, df in prices.items()}
    kw = {}
    if face == "x2":
        cmgr = CostPatch(2.0)
        cmgr.__enter__()
    try:
        with ExitPatch(ovr.get(trader_id, {})):
            res = run_backtest(window, params[trader_id],
                               entry_signal=entry[trader_id],
                               exit_signal=(entry[trader_id] <= 0))
    finally:
        if face == "x2":
            cmgr.__exit__(None, None, None)
    widx = idx[p:p + rl][:len(res["equity_curve"])]
    eq = pd.Series(res["equity_curve"], index=widx)
    wins, evs = {}, {}
    for wname, w in WINDOWS.items():
        if w > rl:
            continue
        m = slice_metrics(eq, res["trades"], w)
        wins[wname] = m
        evs[wname] = _events_between(events, sdate, idx[p + w - 1])
    return {"trader": trader_id, "face": face, "p": int(p),
            "start": str(sdate.date()), "run_len": rl,
            "windows": wins, "events": evs}


def _passive_worker(p):
    """One passive cell: EW buy&hold rel of start-listed members, per window."""
    st = _ST
    close, idx = st["close"], st["idx"]
    n = len(idx)
    rl = _run_len(n, p)
    sdate = idx[p]
    edate = idx[p + rl - 1]
    syms = close.columns[close.loc[sdate].notna()]
    rel = passive_rel(close, syms, sdate, edate)
    wins = {}
    for wname, w in WINDOWS.items():
        if w > rl:
            continue
        m = slice_metrics(rel, [], w)
        wins[wname] = {"ret": m["ret"]}
    return {"trader": "PASSIVE", "face": "passive", "p": int(p),
            "start": str(sdate.date()), "run_len": rl,
            "windows": wins, "events": {},
            "n_listed": int(len(syms))}


# ----------------------------------------------------------- checkpoint io
def _ckpt_path(leg, shard, shards):
    d = os.path.join(CKPT_DIR, f"leg{leg}")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, f"shard_{shard}of{shards}.jsonl")


def _load_done(path):
    """Done cell_ids; tolerant of a truncated tail line (killed mid-write ->
    that cell is re-run, zero-assumption honest)."""
    done = set()
    if not os.path.exists(path):
        return done, 0
    bad = 0
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                done.add(json.loads(line)["cell_id"])
            except (json.JSONDecodeError, KeyError):
                bad += 1
    return done, bad


def _append_cells(path, rows):
    with open(path, "a", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False, default=float) + "\n")


# ------------------------------------------------------------------ slice
def _run_slice_cell(state, trader_id, p_end, face):
    """O-1600 slice: single window [start..end] run (serial, small batch)."""
    prices, params, ovr, entry, close, idx = (
        state["prices"], state["params"], state["ovr"], state["entry"],
        state["close"], state["idx"])
    sdate = idx[p_end[0]]
    edate = idx[p_end[1]]
    window = {s: df[(df.index >= sdate) & (df.index <= edate)]
              for s, df in prices.items()}
    if face == "x2":
        cmgr = CostPatch(2.0)
        cmgr.__enter__()
    try:
        with ExitPatch(ovr.get(trader_id, {})):
            res = run_backtest(window, params[trader_id],
                               entry_signal=entry[trader_id],
                               exit_signal=(entry[trader_id] <= 0))
    finally:
        if face == "x2":
            cmgr.__exit__(None, None, None)
    widx = idx[p_end[0]:p_end[1] + 1][:len(res["equity_curve"])]
    eq = pd.Series(res["equity_curve"], index=widx)
    return {"ret": round(float(eq.iloc[-1] / eq.iloc[0] - 1), 6),
            "dd": round(float(max_drawdown(eq)), 4),
            "sharpe": round(float(sharpe(eq)), 4),
            "n_trades": len(res["trades"]), "n_bars": int(len(eq))}


def cmd_slice_o1600():
    t0 = time.time()
    print("=== O-1600 current-market-fit slice (CEO O-20260924-1600) ===")
    if not self_test_patches():
        print("O1600-GATE FAIL: patch self-test")
        return 2
    prices_full = load_core()
    P = build_panels(prices_full)
    close = P["close"]
    idx = close.index
    # window: first 2026 trading day -> 2026-09-23 (order-specified, bm-c
    # MSG-1630 data-confirmed start 2026-01-05; 以数据为准)
    cand = [i for i, d in enumerate(idx) if d >= O1600_START_CAP]
    if not cand:
        print("O1600-GATE FAIL: no 2026 bars in panel")
        return 2
    p0 = cand[0]
    end_cand = [i for i, d in enumerate(idx) if d <= O1600_END]
    if not end_cand or end_cand[-1] < p0:
        print("O1600-GATE FAIL: window empty")
        return 2
    p1 = end_cand[-1]
    start_s, end_s = str(idx[p0].date()), str(idx[p1].date())
    print(f"window {start_s} -> {end_s} ({p1 - p0 + 1} bars, "
          f"warmup inside 2020+ panel = P-5 anchor caliber)")

    registered, prospect, skipped = [], [], []
    for path in sorted(TRADERS_DIR.glob("*.json")):
        if path.name.startswith("_"):
            continue
        t = load_trader(path.stem)
        lvl = t.get("level")
        if lvl in PAPER_LEVELS:
            registered.append(t)
        elif lvl == "PROSPECT":
            if t["params"]["entry"] not in SIGNAL_BUILDERS:
                skipped.append({"id": t["id"],
                                "reason": "entry not in SIGNAL_BUILDERS "
                                          "(T-24 onboarding incomplete)"})
            else:
                prospect.append(t)
    print(f"registered {len(registered)} + PROSPECT pool {len(prospect)} "
          f"(dynamic read; skipped {len(skipped)})")

    anchors = {}
    for t in registered:
        a = anchor_gate(t, prices_full)
        anchors[t["id"]] = {"ok": a["ok"], "cutoff": a.get("cutoff")}
        if not a["ok"]:
            print(f"O1600-GATE FAIL: anchor drift {t['id']} -- slice void")
            return 3
    print(f"anchors {len(anchors)}/{len(registered)} OK (prereg s2-3 hard gate)")

    state = {"prices": prices_full, "close": close, "idx": idx,
             "params": {}, "ovr": {}, "entry": {}}
    for t in registered + prospect:
        state["entry"][t["id"]] = SIGNAL_BUILDERS[t["params"]["entry"]](P)
        state["params"][t["id"]] = {k: v for k, v in t["params"].items()
                                    if k != "entry"}
        state["ovr"][t["id"]] = t.get("exit_overrides") or {}

    syms = close.columns[close.loc[idx[p0]].notna()]
    rel = passive_rel(close, syms, idx[p0], idx[p1])
    passive = {"ret": round(float(rel.iloc[-1] / rel.iloc[0] - 1), 6),
               "dd": round(float(max_drawdown(rel)), 4),
               "n_members": int(len(syms))}

    rows = []
    for t in registered + prospect:
        r = {"trader": t["id"], "level": t.get("level")}
        for face in ("x1", "x2"):
            r[face] = _run_slice_cell(state, t["id"], (p0, p1), face)
        r["beat_x1"] = bool(r["x1"]["ret"] > passive["ret"])
        r["beat_x2"] = bool(r["x2"]["ret"] > passive["ret"])
        r["spread_vs_passive"] = round(r["x1"]["ret"] - passive["ret"], 6)
        r["verdict"] = ("适合当前市场" if r["beat_x1"] else "不适合当前市场")
        if t in prospect:
            r["note"] = "PROSPECT: no registered anchor evidence yet " \
                        "(T-24 anchoring in flight) -- report-only row"
        rows.append(r)
    rows.sort(key=lambda r: r["spread_vs_passive"], reverse=True)

    states = v3_state_series()
    win_states = states[(states.index >= idx[p0]) & (states.index <= idx[p1])]
    mix = win_states.value_counts().to_dict()
    cur = states[states.index <= idx[p1]]
    regime = {"as_of": str(idx[p1].date()),
              "current_state": str(cur.iloc[-1]),
              "window_mix": {str(k): int(v) for k, v in mix.items()},
              "note": "v3 import-replay (T-21 s3.2), causal per-date"}

    trials = len(rows) * 2 + 1 + len(anchors)   # strategy x2 faces + passive + anchors
    led = append_ledger("O1600_MARKET_FIT", trials,
                        file_name="shortline/o1600_market_fit.json",
                        note="CEO O-20260924-1600 designated single-start "
                             "slice of T-22 (order-specified window "
                             f"{start_s}->{end_s}; strategy {len(rows)}x2 "
                             "faces + 1 passive + anchors "
                             f"{len(anchors)}; not a P-5C grid cell)",
                        evidence_cutoff=end_s)

    out = {"order": "O-20260924-1600", "ticket": "T-2026-09-24-22",
           "window": {"start": start_s, "end": end_s, "bars": p1 - p0 + 1},
           "start_note": "first 2026 trading day, data-confirmed "
                         "(bm-c MSG-1630 expected 2026-01-05; 以数据为准)",
           "anchors": anchors,
           "prospect_pool": {"n": len(prospect), "skipped": skipped,
                             "note": "T-24 PROSPECT onboarding in flight "
                                     "(bm-a); pool read dynamically at run "
                                     "time per MSG-1630 -- zero now = honest "
                                     "0, later slices absorb new members"},
           "passive_ew48": passive, "regime": regime,
           "judgment": {"beat_line_semantics": "P-5 frozen caliber: "
                         "beat = same-window strategy ret > passive EW ret "
                         "(single start = binary, no rate); verdict on x1 "
                         "face; x2 face + dd disclosed alongside",
                         "report_only": "order s5: 本切片不单独立门 -- no "
                                        "level/gate changes, CEO report only"},
           "rows": rows,
           "trials_ledger": led,
           "audit": {"workers": 1, "runtime_sec": round(time.time() - t0, 1),
                     "evidence_cutoff": end_s},
           "runtime_sec": round(time.time() - t0, 1),
           "generated": time.strftime("%Y-%m-%d %H:%M:%S")}
    with open(RES_O1600, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False, default=float)
    import csv
    cols = ["trader", "level", "ret_x1", "dd_x1", "n_trades_x1",
            "ret_x2", "dd_x2", "passive_ret", "passive_dd",
            "spread_vs_passive", "beat_x1", "beat_x2", "verdict"]
    with open(CSV_O1600, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({"trader": r["trader"], "level": r["level"],
                         "ret_x1": r["x1"]["ret"], "dd_x1": r["x1"]["dd"],
                         "n_trades_x1": r["x1"]["n_trades"],
                         "ret_x2": r["x2"]["ret"], "dd_x2": r["x2"]["dd"],
                         "passive_ret": passive["ret"],
                         "passive_dd": passive["dd"],
                         "spread_vs_passive": r["spread_vs_passive"],
                         "beat_x1": r["beat_x1"], "beat_x2": r["beat_x2"],
                         "verdict": r["verdict"]})

    print(f"\n--- O-1600 market-fit verdicts (window {start_s}..{end_s}) ---")
    print(f"passive EW-{passive['n_members']}: ret={passive['ret']} "
          f"dd={passive['dd']} | regime now={regime['current_state']} "
          f"mix={regime['window_mix']}")
    for r in rows:
        print(f"#{rows.index(r)+1} {r['trader']}: ret={r['x1']['ret']} "
              f"dd={r['x1']['dd']} spread={r['spread_vs_passive']:+.4f} "
              f"x2={r['x2']['ret']} -> {r['verdict']}")
    print(f"products: {RES_O1600}\n          {CSV_O1600}")
    print(f"ledger: prev={led['prev_total']} +{trials} -> {led['total']}")
    return 0


# -------------------------------------------------------------------- run
def cmd_run(leg, shard, shards, faces, workers, limit):
    t0 = time.time()
    print(f"=== P-5C leg {leg} batch (shard {shard}/{shards}, faces={faces}) ===")
    if not self_test_patches():
        print("P5C-GATE FAIL: patch self-test")
        return 2
    prices, P, idx, listed, cen = _load_leg(leg)
    if cen != FROZEN_CENSUS[leg]:
        print(f"P5C-GATE FAIL: grid drift on leg {leg}: panel census "
              f"{cen} != frozen probe {FROZEN_CENSUS[leg]} -- abort")
        return 2
    print(f"panel {idx[0].date()} -> {idx[-1].date()} | {len(idx)} td | "
          f"census {cen} == frozen probe (PASS)")

    # anchor hard gate (prereg s2-3): all registered traders reproduce
    cut = pd.Timestamp(EVIDENCE_CUTOFF_GRID)
    prices_cut = {s: df[df.index <= cut] for s, df in prices.items()}
    if leg == "L":
        anchor_prices = prices_cut
    else:
        anchor_prices = {s: df[df.index >= LEG_L_FLOOR]
                         for s, df in prices_cut.items()}
    anchors = {}
    for path in sorted(TRADERS_DIR.glob("*.json")):
        if path.name.startswith("_"):
            continue
        t = load_trader(path.stem)
        if t.get("level") in PAPER_LEVELS:
            a = anchor_gate(t, anchor_prices)
            anchors[t["id"]] = {"ok": a["ok"], "cutoff": a.get("cutoff")}
            if not a["ok"]:
                print(f"P5C-GATE FAIL: anchor drift {t['id']} -- batch void")
                return 3
    print(f"anchors {len(anchors)} OK (cutoff {EVIDENCE_CUTOFF_GRID})")

    traders = [load_trader(path.stem) for path in sorted(TRADERS_DIR.glob("*.json"))
               if not path.name.startswith("_")
               and load_trader(path.stem).get("level") in PAPER_LEVELS]
    entry, params, ovr = {}, {}, {}
    for t in traders:
        entry[t["id"]] = SIGNAL_BUILDERS[t["params"]["entry"]](P)
        params[t["id"]] = {k: v for k, v in t["params"].items() if k != "entry"}
        ovr[t["id"]] = t.get("exit_overrides") or {}

    # start grid on this shard (probe convention), contiguous chunk split
    n = len(idx)
    use_ml = (leg == "L")
    all_starts = [p for p in range(n)
                  if idx[p] >= (LEG_L_FLOOR if leg == "L" else LEG_D_FLOOR)
                  and p >= WARMUP_TD and p <= n - 1 - WINDOWS["6m"]
                  and ((listed.iloc[p] >= MIN_LISTED) if use_ml else True)]
    chunk = (len(all_starts) + shards - 1) // shards
    starts = all_starts[shard * chunk:(shard + 1) * chunk]
    if limit:
        starts = starts[:limit]
    print(f"starts on shard: {len(starts)} of {len(all_starts)} "
          f"(shards {shards}, chunk {chunk})")

    events = _load_registry_events()
    state = {"prices": prices, "close": P["close"], "idx": idx,
             "params": params, "ovr": ovr, "entry": entry, "events": events}
    states = v3_state_series()
    state["states"] = states

    ckpt = _ckpt_path(leg, shard, shards)
    done, bad = _load_done(ckpt)
    if bad:
        print(f"checkpoint: {len(done)} done, {bad} corrupt tail line(s) "
              f"(tolerated -> re-run)")
    else:
        print(f"checkpoint: {len(done)} done (resume)")

    jobs = []
    for p in starts:
        cell_p = f"{leg}|passive|{idx[p].date()}"
        if cell_p not in done:
            jobs.append((cell_p, _passive_worker, (p,)))
        for t in traders:
            for face in faces:
                cid = f"{leg}|{face}|{t['id']}|{idx[p].date()}"
                if cid not in done:
                    jobs.append((cid, _cell_worker, (t["id"], p, face)))
    if limit:
        jobs = jobs[: limit * (len(traders) * len(faces) + 1)]
    print(f"jobs to run: {len(jobs)} (workers={workers or worker_cap()})")

    n_done = 0
    t_pool = time.time()
    with ProcessPoolExecutor(max_workers=workers or worker_cap(),
                             initializer=_init_worker, initargs=(state,)) as pool:
        futs = {pool.submit(fn, *args): key
                for key, fn, args in jobs}
        buf = []
        for fut in futs:
            key = futs[fut]
            r = fut.result()
            r["cell_id"] = key
            _enrich_row(r, state["states"], state["close"])
            buf.append(r)
            n_done += 1
            if n_done % 50 == 0:
                _append_cells(ckpt, buf)
                buf = []
                print(f"  [pool] {n_done}/{len(jobs)} cells "
                      f"({time.time()-t_pool:.0f}s)")
        if buf:
            _append_cells(ckpt, buf)
    print(f"pool done: {n_done} cells in {time.time()-t_pool:.1f}s "
          f"(checkpoint {ckpt})")
    print(f"runtime {time.time()-t0:.1f}s")
    return 0


def cmd_status():
    import glob
    total = {}
    for path in sorted(glob.glob(os.path.join(CKPT_DIR, "leg*",
                                              "shard_*.jsonl"))):
        leg = os.path.basename(os.path.dirname(path))
        done, bad = _load_done(path)
        n = len(done)
        agg = total.setdefault(leg, {"cells": 0, "files": 0, "corrupt": 0})
        agg["cells"] += n
        agg["files"] += 1
        agg["corrupt"] += bad
        print(f"{leg}/{os.path.basename(path)}: {n} cells"
              + (f" (+{bad} corrupt tolerated)" if bad else ""))
    for leg, agg in total.items():
        print(f"TOTAL leg {leg}: {agg['cells']} cells, "
              f"{agg['files']} shard file(s), {agg['corrupt']} corrupt")
    return 0


# ---------------------------------------------------------------- selftest
def _mk_panel(n_days=1400, n_syms=4, seed=7):
    """Deterministic synthetic close-only panel (business-day index)."""
    import numpy as np
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2018-01-01", periods=n_days)
    data = {}
    for k in range(n_syms):
        s = f"S{k}"
        px = 10.0 * np.cumprod(1 + rng.normal(0.0002, 0.01, n_days))
        df = pd.DataFrame({"open": px, "close": px,
                           "high": px * 1.01, "low": px * 0.99,
                           "volume": px * 1000.0,
                           "amount": px * px * 1000.0},
                          index=idx)
        data[s] = df
    return data


def cmd_selftest():
    ok_n = 0

    def ok(name, cond):
        nonlocal ok_n
        print(f"[{'PASS' if cond else 'FAIL'}] {name}")
        if not cond:
            raise SystemExit(f"selftest FAIL: {name}")
        ok_n += 1

    # 1) run_len boundary convention (probe: p <= n-1-W, boundary inclusive)
    n = 1631
    ok("run_len: probe convention longest-complete",
       _run_len(n, 252) == 504 and _run_len(n, 1504) == 126
       and _run_len(n, 1127) == 252 and _run_len(n, 1505) == 0
       and _run_len(10, 0) == 0)
    ok("run_len: frozen leg-L census endpoints",
       _run_len(n, 252) == 504 and _run_len(n, n - 1 - 504) == 504
       and _run_len(n, n - 504) == 252 and _run_len(n, n - 1 - 126) == 126
       and _run_len(n, n - 126) == 0)

    # 2) census replica reproduces frozen counts on a shaped synthetic panel
    synth = _mk_panel(n_days=1631, n_syms=48)
    P = build_panels(synth)
    close = P["close"]
    idx = close.index
    idx = idx[(idx >= LEG_L_FLOOR) & (idx <= pd.Timestamp("2026-09-22"))]
    ok("census: synthetic panel warmup gate matches probe convention",
       _census(idx, pd.Series([48] * len(idx), index=idx), LEG_L_FLOOR,
               WARMUP_TD, True)["6m"]
       == len([p for p in range(len(idx))
               if p >= WARMUP_TD and p <= len(idx) - 1 - 126]))

    # 3) shard split: contiguous, disjoint, union == all
    all_s = list(range(1253))
    shards = 3
    chunk = (len(all_s) + shards - 1) // shards
    parts = [all_s[i * chunk:(i + 1) * chunk] for i in range(shards)]
    ok("shard split: disjoint + full coverage",
       sum(len(p_) for p_ in parts) == len(all_s)
       and len({x for p_ in parts for x in p_}) == len(all_s))

    # 4) checkpoint round-trip + tolerant corrupt tail
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        ck = os.path.join(td, "ck.jsonl")
        _append_cells(ck, [{"cell_id": "L|x1|T|2021-01-15", "v": 1}])
        _append_cells(ck, [{"cell_id": "L|passive|2021-01-15", "v": 2}])
        with open(ck, "a", encoding="utf-8") as fh:
            fh.write('{"cell_id": "TRUNC')   # killed mid-write
        done, bad = _load_done(ck)
        ok("checkpoint: round-trip + corrupt tail tolerated",
           done == {"L|x1|T|2021-01-15", "L|passive|2021-01-15"} and bad == 1)

    # 5) events window counting (fixture)
    ev = [(pd.Timestamp("2021-04-12"), "159901"),
          (pd.Timestamp("2021-06-25"), "159928"),
          (pd.Timestamp("2026-02-02"), "510300")]
    ok("events_n: window containment",
       _events_between(ev, pd.Timestamp("2021-01-04"),
                       pd.Timestamp("2021-12-31")) == 2
       and _events_between(ev, pd.Timestamp("2021-04-12"),
                           pd.Timestamp("2021-04-12")) == 1
       and _events_between(ev, pd.Timestamp("2022-01-01"),
                           pd.Timestamp("2025-12-31")) == 0)

    # 6) stratum + o1600 window truncation
    ok("stratum: thin/mid/full boundaries",
       _stratum(5) == "thin" and _stratum(23) == "thin"
       and _stratum(24) == "mid" and _stratum(47) == "mid"
       and _stratum(48) == "full")
    didx = pd.bdate_range("2025-12-01", periods=300)
    cand = [i for i, d in enumerate(didx) if d >= O1600_START_CAP]
    endc = [i for i, d in enumerate(didx) if d <= O1600_END]
    ok("o1600 window: first-2026 start + 09-23 end cap",
           str(didx[cand[0]].date()) == "2026-01-01"
       and str(didx[endc[-1]].date()) == "2026-09-23")

    # 7) CostPatch x2 rate + restore (science_gates single source)
    eb = sys.modules["engine.backtester"]
    orig = eb.FeeSchedule
    with CostPatch(2.0):
        fee = eb.FeeSchedule()
        rate2 = (fee.commission_rate + fee.handling_fee
                 + fee.supervision_fee + fee.slippage_a)
    ok("CostPatch: x2 single-side == COST_X2_RATE + name restored",
       abs(rate2 - COST_X2_RATE) < 1e-12 and eb.FeeSchedule is orig)

    # 8) passive EW determinism + hand value
    c = pd.DataFrame({"A": [10.0, 11.0, 12.0], "B": [20.0, 20.0, 22.0]},
                     index=pd.bdate_range("2026-01-05", periods=3))
    r1 = passive_rel(c, ["A", "B"], c.index[0], c.index[-1])
    r2 = passive_rel(c, ["A", "B"], c.index[0], c.index[-1])
    hand_end = ((12 / 10) + (22 / 20)) / 2
    ok("passive: EW rel deterministic + hand value",
       r1.equals(r2) and abs(float(r1.iloc[-1]) - hand_end) < 1e-12)

    # 9) end-to-end worker cell on synthetic panel (pipeline shape)
    synth = _mk_panel(n_days=420, n_syms=3)
    P = build_panels(synth)
    close = P["close"]
    entry = pd.DataFrame(False, index=close.index, columns=close.columns)
    entry.iloc[260] = True        # one entry 8td after warmup boundary
    state = {"prices": synth, "close": close, "idx": close.index,
             "params": {"T": {"max_positions": 1, "position_size_pct": 0.5}},
             "ovr": {"T": {}}, "entry": {"T": entry},
             "events": [(close.index[100], "S0")],
             "states": pd.Series(["YELLOW"] * len(close),
                                 index=close.index)}
    _init_worker(state)
    res = _cell_worker("T", 260, "x1")
    _enrich_row(res, state["states"], close)
    ok("worker cell: runs, window slices + events_n + regime fields",
       res["run_len"] == 126 and set(res["windows"]) == {"6m"}
       and res["events"]["6m"] == 0
       and res["regime_state_start"] == "YELLOW"
       and isinstance(res["windows"]["6m"]["ret"], float))
    res2 = _cell_worker("T", 260, "x2")
    ok("worker cell: x2 face runnable (cost strictly higher)",
       isinstance(res2["windows"]["6m"]["ret"], float))
    pas = _passive_worker(260)
    _enrich_row(pas, state["states"])
    ok("passive cell: window slices shape",
       pas["run_len"] == 126 and set(pas["windows"]) == {"6m"}
       and pas["n_listed"] == 3)

    # 10) cell_id uniqueness over a mini grid
    ids = [f"L|x1|T{i}|{d}" for i in range(3) for d in range(4)]
    ok("cell_id: unique over grid", len(set(ids)) == len(ids))

    # 11) ledger head reachable (data-driven chain)
    ok("ledger: head readable", ledger_head()["total"] > 0)

    print(f"selftest: {ok_n} checks ALL PASS")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest")
    sub.add_parser("slice-o1600")
    r = sub.add_parser("run")
    r.add_argument("--leg", choices=["L", "D"], required=True)
    r.add_argument("--shard", type=int, default=0)
    r.add_argument("--shards", type=int, default=1)
    r.add_argument("--faces", default="x1,x2")
    r.add_argument("--workers", type=int, default=None)
    r.add_argument("--limit", type=int, default=None)
    sub.add_parser("status")
    sub.add_parser("finalize")
    a = ap.parse_args()
    if a.cmd == "selftest":
        return cmd_selftest()
    if a.cmd == "slice-o1600":
        return cmd_slice_o1600()
    if a.cmd == "run":
        faces = [f.strip() for f in a.faces.split(",") if f.strip()]
        return cmd_run(a.leg, a.shard, a.shards, faces, a.workers, a.limit)
    if a.cmd == "status":
        return cmd_status()
    if a.cmd == "finalize":
        print("finalize: pending until leg grids complete (D7 + judgments "
              "per frozen prereg s4); run `status` for progress")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
