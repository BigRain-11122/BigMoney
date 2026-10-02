"""PERPETUAL-N3-R1 runner (T-2026-09-30-133 s2, N3 face wave-1).

Neighborhood robustness grid on the REGISTERED members (t24_g2_pack
machinery generalized to the registration face per the frozen face table
in research/PERPETUAL_FACES.md v1.0 section 2). PRE-REGISTERED:
research/PERPETUAL_N3_R1_PREREG.md (frozen before any pool burn).

Per member: center anchor re-verify (recorded-cell replay, ledger +0)
+ cost-x3 cell + frozen OAT neighborhood cells (prereg sec.3 table).
Products = results/perpetual_faces/n3_r1/cells-<ID>.jsonl (append-only
per-member checkpoint = shard product; presence=done, deterministic rerun
byte-equal) + finalize merge JSON + per-member packs.

Judgment lines are machine-linked (science_gates recorded_lines /
bootstrap_ci_sharpe / deflated_sharpe_ratio / g2_registration_v2 /
skill_line_v2; zero hand-copied numbers). Measurement-deepening face:
three-state registration verdicts are N/A per prereg sec.4; anchor-fail
members contribute nothing beyond their center cell (t24 anchor gate
convention verbatim).

Pool handshake (r497 law): worker-side claim file closed at burn
completion and at idempotent no-op reruns; selftest never writes.

Usage (detached BelowNormal per O-1612 full-load pool):
  python scripts/perpetual_faces_n3.py run --member <ID>            # R1 shard
  python scripts/perpetual_faces_n3.py run --member <ID> --wave r2 # R2 shard
  python scripts/perpetual_faces_n3.py status
  python scripts/perpetual_faces_n3.py probe               # read-only anchor
  python scripts/perpetual_faces_n3.py probe --wave r2     # R2 4-leg probe
  python scripts/perpetual_faces_n3.py finalize [--wave r1|r2]
  python scripts/perpetual_faces_n3.py selftest
"""
import argparse
import json
import os
import sys
import time
from contextlib import nullcontext

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd

from config import PATHS
from science_gates import (SEED_REGISTRY, append_ledger, cutoff_meta,
                            bootstrap_ci_sharpe, deflated_sharpe_ratio,
                            g2_registration_v2, ledger_head,
                            recorded_lines, skill_line_v2)

EVIDENCE_CUT = "2026-09-22"          # prereg sec.2 hard cutoff
OOS_START = "2025-01-01"             # registered evidence segment split
ANCHOR_TOL = 0.002                   # J14/J15 project standard
WORST_YEAR_FLOOR = -0.35             # registration standard per-year floor
BATCH = "PERPETUAL-N3-R1"
BATCH_CELLS_NEW = 28                 # prereg sec.0: 22 nbhd + 6 x3 (all
                                     # new evidence; centers = replays +0)
N_MEMBERS = 6
SEED_BASE = 70_000                   # SEED_REGISTRY perpetual_n3_r1

WAVE_DIR = os.path.join(PATHS.results_dir, "perpetual_faces", "n3_r1")
BATCH_JSON = os.path.join(PATHS.results_dir, "perpetual_faces",
                          "n3_r1_results.json")

# --------------------------- R2 wave (time-start robustness grid) ---------
# prereg: research/PERPETUAL_N3_R2_PREREG.md (frozen before any pool burn;
# five-condition freeze gate in the prereg head). Stress axis = the
# time-interval START POINT (investor joins at a quarter close, holds to
# cutoff) -- orthogonal to R1's frozen-parameter neighborhood. Engine face
# = 6 center replays anchor-gated against the R1 checkpoint cells; the
# 144 window readouts are pure-math strict-tail slices of the center
# equity curves (zero extra engine runs). Ledger +144 (windows only;
# centers are replays +0). Zero new seed bands: slicing is
# calendar-deterministic and window-level bootstrap CI is deliberately
# not run (short-window CI face; full-history CI is R1's, prereg sec.3).
R2_BATCH = "PERPETUAL-N3-R2"
R2_CELLS_NEW = 144                 # 24 start-window readouts x 6 members
R2_WAVE_DIR = os.path.join(PATHS.results_dir, "perpetual_faces", "n3_r2")
R2_BATCH_JSON = os.path.join(PATHS.results_dir, "perpetual_faces",
                             "n3_r2_results.json")
R2_EXPECT_STARTS = 24              # frozen: 2020Q1..2025Q4 quarter-first bars
R2_REBASE_TOL = 1e-12             # standing rebase cross-path tolerance

RL = recorded_lines()
I_LINE = {"default": RL["i_line"], "ce": RL["ce_null_p4_batch1"]}
VI_BAR = RL["vi_bar"]


def _machine_id() -> str:
    try:
        with open(os.path.join(PATHS.root, "fleet", "machine.json"),
                  encoding="utf-8") as fh:
            return json.load(fh)["machine_id"]
    except Exception:
        return "unknown"


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S+08:00")


# ---------------------------------------------------------------- families
# spec: build(P, p) must reproduce SIGNAL_BUILDERS[member entry key](P)
# bit-exactly at CENTER (selftest S1 hard gate). oat = frozen prereg
# sec.3 table. k_control = (param_name, registered_total_exposure) for
# the top_k/top_n perturbation position convention (G2_DEEPENING sec.1
# experiment control: max_positions=k, size=round(exposure/k,4)).


def _apply_sym(fn, P, keys, **kw):
    syms = list(P["close"].columns)
    return pd.DataFrame({s: fn(*[P[k][s] for k in keys], **kw)
                         for s in syms}).fillna(0)


def _lowvol(P, p):
    import strategies.volatility as m
    return m.low_vol_long(P["close"], p["n"], top_k=p["top_k"])


def _rot(P, p):
    from strategies.composite_rotation import top_n_rotation
    return top_n_rotation(P["high"], P["low"], P["close"],
                           top_n=p["n"], rebal_days=p["rebal_days"])


def _drought(P, p):
    import strategies.patterns as m
    return _apply_sym(m.vol_drought_reversal, P,
                      ["open", "high", "low", "close", "volume"],
                      vol_floor=p["vol_floor"], drop_th=p["drop_th"])


def _engulf(P, p):
    import strategies.ta as m
    return _apply_sym(m.engulf_reversal, P, ["open", "close"],
                      drop_th=p["drop_th"])


def _needle(P, p):
    import strategies.patterns as m
    return _apply_sym(m.needle_probe, P,
                      ["open", "high", "low", "close"],
                      drop_th=p["drop_th"], shadow_pct=p["shadow_pct"])


FAMILIES = {
    "VOLATILITY-CE-01": {
        "build": _lowvol,
        "center": {"n": 60, "top_k": 5},
        "oat": [("n", 50, 70), ("top_k", 4, 6)],
        "k_control": ("top_k", 0.50),
    },
    "COMPOSITE-CE-01": {
        "build": _rot,
        "center": {"n": 5, "rebal_days": 20},
        "oat": [("n", 4, 6), ("rebal_days", 15, 25)],
        "k_control": ("n", 0.95),
    },
    "COMPOSITE-CE-02": {
        "build": _rot,
        "center": {"n": 8, "rebal_days": 20},
        "oat": [("n", 6, 10), ("rebal_days", 15, 25)],
        "k_control": ("n", 0.9496),
    },
    "DROUGHT-CE-01": {
        "build": _drought,
        "center": {"vol_floor": 0.55, "drop_th": -0.05},
        "oat": [("vol_floor", 0.50, 0.60), ("drop_th", -0.04, -0.06)],
        "k_control": None,
    },
    "ENGULF-CE-01": {
        "build": _engulf,
        "center": {"drop_th": -0.05},
        "oat": [("drop_th", -0.04, -0.06)],
        "k_control": None,
    },
    "NEEDLE-DE-01": {
        "build": _needle,
        "center": {"drop_th": -0.05, "shadow_pct": 0.02},
        "oat": [("drop_th", -0.04, -0.06), ("shadow_pct", 0.015, 0.025)],
        "k_control": None,
    },
}

MEMBER_ORDER = sorted(FAMILIES)          # seed index face (prereg sec.3)


def load_members() -> list:
    from firm.hr import TRADERS_DIR
    out = []
    for name in sorted(os.listdir(TRADERS_DIR)):
        if not (name.endswith(".json") and not name.startswith("PROS-")
               and not name.startswith("_")):
            continue
        with open(os.path.join(TRADERS_DIR, name), encoding="utf-8") as fh:
            m = json.load(fh)
        if m["id"] not in FAMILIES:
            raise KeyError(f"no family spec for member {m['id']}")
        if m.get("evidence_cutoff") != EVIDENCE_CUT:
            raise ValueError(f"{m['id']} cutoff drift: "
                             f"{m.get('evidence_cutoff')}")
        out.append(m)
    return out


def member_regime(m: dict) -> str:
    return "ce" if "time_decay_period" in m["params"] else "default"


def cell_id(mid: str, kind: str, p: dict) -> str:
    if kind in ("center", "x3"):
        return f"{mid}::{kind}"
    (pname, val), = p.items()
    return f"{mid}::nbhd::{pname}={val}"


def member_cells_path(mid: str) -> str:
    return os.path.join(WAVE_DIR, f"cells-{mid}.jsonl")


def read_cells(mid: str) -> list:
    cells = []
    fp = member_cells_path(mid)
    if os.path.exists(fp):
        with open(fp, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    cells.append(json.loads(line))
                except json.JSONDecodeError:
                    continue        # corrupt tail tolerated (t22 convention)
    return cells


def _append_cell(mid: str, rec: dict):
    os.makedirs(WAVE_DIR, exist_ok=True)
    with open(member_cells_path(mid), "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def _cells_done(cells: list) -> set:
    return {c["id"] for c in cells if "id" in c}


def _anchor_fail_ids(cells: list) -> set:
    out = set()
    for c in cells:
        if c.get("kind") == "center" and c.get("anchor") \
                and not c["anchor"].get("pass"):
            out.add(c["member"])
    return out


def cells_todo(m: dict, cells: list, anchor_fail: set) -> list:
    """Center first (anchor gate), then x3 + OAT points; anchor-FAIL
    members contribute nothing beyond their center cell (t24 verbatim)."""
    mid = m["id"]
    spec = FAMILIES[mid]
    done = _cells_done(cells)
    plan = []
    if f"{mid}::center" not in done:
        plan.append(("center", {}))
    if mid in anchor_fail:
        return plan
    if f"{mid}::x3" not in done:
        plan.append(("x3", {}))
    for pname, lo, hi in spec["oat"]:
        for v in (lo, hi):
            if cell_id(mid, "nbhd", {pname: v}) not in done:
                plan.append(("nbhd", {pname: v}))
    return plan


def _member_params(m: dict, point: dict) -> dict:
    """Registered-member engine params (paper_run convention verbatim:
    params minus entry) with the G2_DEEPENING position-control override
    on the k-param perturbation cells."""
    params = {k: v for k, v in m["params"].items() if k != "entry"}
    spec = FAMILIES[m["id"]]
    kc = spec["k_control"]
    if point and kc and kc[0] in point:
        k = point[kc[0]]
        params["max_positions"] = k
        params["position_size_pct"] = round(kc[1] / k, 4)
    return params


def _sharpe(series: pd.Series) -> float:
    ret = series.pct_change().dropna()
    if len(ret) < 2 or ret.std() == 0:
        return 0.0
    return float(ret.mean() / ret.std() * (252 ** 0.5))


def _run_cell(prices, P, state, m: dict, point: dict,
              cost_mult: float | None = None) -> dict:
    """Registered-member run convention (paper_run engine call verbatim:
    params minus entry + ExitPatch + dd_control passthrough)."""
    from live.paper import CostPatch, ExitPatch
    from engine import run_backtest
    params = _member_params(m, point)
    cctx = CostPatch(cost_mult) if cost_mult else nullcontext()
    with cctx, ExitPatch(m.get("exit_overrides")):
        res = run_backtest(prices, params, entry_signal=state,
                           exit_signal=(state <= 0),
                           dd_control=m.get("dd_control"))
    idx = P["close"].index
    eq = pd.Series(res["equity_curve"], index=idx[:len(res["equity_curve"])])
    trades = res["trades"]
    n_in = sum(1 for t in trades if str(t["date"]) < OOS_START)
    n_oos = int(res["metrics"]["num_trades"]) - n_in
    rets = eq.pct_change().dropna().tolist()
    return {"eq": eq, "rets": rets,
            "full": res["metrics"], "in_s": _sharpe(eq[eq.index < OOS_START]),
            "oos_s": _sharpe(eq[eq.index >= OOS_START]),
            "n_trades": int(res["metrics"]["num_trades"]),
            "n_in": n_in, "n_oos": n_oos}


def _panel():
    from live.paper import build_panels, load_core
    prices = load_core()
    cut = pd.Timestamp(EVIDENCE_CUT)
    prices = {s: df[df.index <= cut] for s, df in prices.items()}
    P = build_panels(prices)
    if str(P["close"].index[-1].date()) != EVIDENCE_CUT:
        print(f"HONEST ABORT: panel tail {P['close'].index[-1].date()} "
              f"!= cutoff {EVIDENCE_CUT}")
        return None, None
    if len(P["close"].columns) != 48:
        print(f"HONEST ABORT: universe {len(P['close'].columns)} != 48")
        return None, None
    return prices, P


def _compute_cell(m: dict, kind: str, point: dict, seed: int,
                  prices, P) -> dict:
    """Single-body cell computation (serial and pooled drivers share this
    exact code path -- O-2026-09-30-2355 s2 single-body law)."""
    mid = m["id"]
    spec = FAMILIES[mid]
    regime = member_regime(m)
    bp = dict(spec["center"])
    bp.update(point)
    state = spec["build"](P, bp)
    r = _run_cell(prices, P, state, m, point,
                  cost_mult=3.0 if kind == "x3" else None)
    rec = {"id": cell_id(mid, kind, point), "member": mid,
           "kind": kind, "point": point or None, "regime": regime,
           "full_sharpe": round(_sharpe(r["eq"]), 4),
           "in_sharpe": round(float(r["in_s"]), 4),
           "oos_sharpe": round(float(r["oos_s"]), 4),
           "n_trades": r["n_trades"], "n_in": r["n_in"],
           "n_oos": r["n_oos"],
           "max_dd": round(float(r["full"]["max_drawdown"]), 4),
           "annual_return": round(float(r["full"]["annual_return"]), 4),
           "bootstrap_ci": bootstrap_ci_sharpe(r["rets"], seed=seed)}
    # no wall-clock fields in checkpoint rows: determinism law (rerun
    # byte-equal); burn-time provenance lives in the pool claim file and
    # the member pack's generated face
    if kind == "center":
        from p3_portfolio import yearly_returns
        rec_in = m["backtest"]["in_sample"]
        rec_oos = m["backtest"]["out_sample"]
        rec["yearly"] = {str(k): round(v, 4)
                         for k, v in yearly_returns(r["eq"]).items()}
        rec["anchor"] = {
            "d_in": round(abs(r["in_s"] - rec_in["sharpe"]), 6),
            "d_oos": round(abs(r["oos_s"] - rec_oos["sharpe"]), 6),
            "trades_in_exact": bool(r["n_in"] == rec_in["trades"]),
            "trades_oos_exact": bool(r["n_oos"] == rec_oos["trades"]),
            "pass": bool(abs(r["in_s"] - rec_in["sharpe"]) < ANCHOR_TOL
                         and abs(r["oos_s"] - rec_oos["sharpe"])
                         < ANCHOR_TOL
                         and r["n_in"] == rec_in["trades"]
                         and r["n_oos"] == rec_oos["trades"]),
        }
        # n_trials = live ledger head at burn time (a fact of the run; a
        # re-burned crashed cell carries the then-current head -- t22
        # resume semantics, disclosed)
        rec["dsr"] = deflated_sharpe_ratio(
            r["rets"], n_trials=int(ledger_head()["total"]))
    return rec


# --- O-2026-09-30-2355 multicore law: single body, two drivers -------------
# pooled face: initializer ships the assembled panel context (spawn-safe
# module-global, grid_p1_screen r304 canon); per-cell exceptions propagate
# and kill the run (fail-closed; buffered plan-order flush below keeps
# rerun byte-equal -- completion order never reaches the checkpoint).
from parallel_runner import run_cells_parallel, worker_cap  # noqa: E402

_POOL_CTX = {}      # per-process assembled context (spawn-safe global)


def _init_pool_ctx(prices, P):
    _POOL_CTX.clear()
    _POOL_CTX.update(prices=prices, P=P)


def _cell_task(m, kind, point, seed):
    return _compute_cell(m, kind, point, seed,
                         _POOL_CTX["prices"], _POOL_CTX["P"])


def _burn_member(m: dict, prices, P, write: bool = True,
                 use_pool: bool = True) -> list:
    """Burn all remaining cells for one member; returns new cell records.
    write=False = probe face (in-memory only, checkpoint untouched).
    Pooled driver = default (law-1: single-thread runners may not serve
    pool entries); serial driver kept for parity/hermetic legs."""
    mid = m["id"]
    seed = SEED_BASE + MEMBER_ORDER.index(mid)
    cells = read_cells(mid) if write else []
    anchor_fail = _anchor_fail_ids(cells) if write else set()
    todo = cells_todo(m, cells, anchor_fail)
    if not todo:
        return []
    new_recs = []
    if use_pool:
        specs = [(cell_id(mid, kind, point), _cell_task,
                  (m, kind, point, seed)) for kind, point in todo]
        by_key = {}

        def _on_cell(key, payload):
            by_key[key] = payload

        run_cells_parallel(specs, workers=min(worker_cap(), len(specs)),
                           desc=f"n3r1-{mid}", initializer=_init_pool_ctx,
                           initargs=(prices, P), on_result=_on_cell)
        # buffered plan-order flush: determinism law (rerun byte-equal)
        for kind, point in todo:
            rec = by_key[cell_id(mid, kind, point)]
            new_recs.append(rec)
            if write:
                _append_cell(mid, rec)
                _log_cell(mid, rec)
        return new_recs
    for kind, point in todo:
        rec = _compute_cell(m, kind, point, seed, prices, P)
        new_recs.append(rec)
        if write:
            _append_cell(mid, rec)
            _log_cell(mid, rec)
    return new_recs


def _log_cell(mid: str, rec: dict):
    print(f"[{mid}] {rec['id']}: full_s={rec['full_sharpe']} "
          f"in_s={rec['in_sharpe']} oos_s={rec['oos_sharpe']} "
          f"trades={rec['n_trades']}"
          + (f" anchor={'OK' if rec['anchor']['pass'] else 'FAIL'}"
             if rec["kind"] == "center" else ""), flush=True)


# ------------------------------------------------------- pool handshake (r497)
def _pool_claim(mid: str, detail: str, write: bool = True,
                wave: str = "r1") -> None:
    if not write:
        return
    entry_id = pool_entry_id(mid, wave=wave)
    d = os.path.join(PATHS.results_dir, "pool_claims",
                     entry_id.replace("/", "_"))
    os.makedirs(d, exist_ok=True)
    fp = os.path.join(d, f"{mid}.{_machine_id()}.json")
    now = _now_iso()
    with open(fp, "w", encoding="utf-8") as f:
        json.dump({"machine_id": _machine_id(), "state": "closed",
                   "pid": os.getpid(), "heartbeat": now, "outcome": "ok",
                   "exit_code": 0, "closed_at": now, "result_ref": detail},
                  f, ensure_ascii=False, indent=1)
    print(f"pool claim closed: {os.path.basename(fp)}", flush=True)


def pool_entry_id(mid: str, wave: str = "r1") -> str:
    """Single-source entry-id face: the generator imports this so the
    pool entries and the runner handshake can never drift apart. The
    wave param keeps the R1 face byte-stable for existing callers."""
    batch = BATCH if wave == "r1" else R2_BATCH
    return f"{batch}-{mid}"


def cmd_run(member_id: str, use_pool: bool = True,
            wave: str = "r1") -> int:
    if wave == "r2":
        return cmd_run_r2(member_id)
    try:
        import psutil
        pri = getattr(psutil, "BELOW_NORMAL_PRIORITY_CLASS", None)
        if pri is not None:
            psutil.Process().nice(pri)   # O-1612 full-load low-priority pool
    except Exception:
        pass
    members = {m["id"]: m for m in load_members()}
    if member_id not in members:
        print(f"HONEST ABORT: unknown member {member_id}")
        return 2
    m = members[member_id]
    cells = read_cells(member_id)
    todo = cells_todo(m, cells, _anchor_fail_ids(cells))
    print(f"member={member_id} cells_done={len(_cells_done(cells))} "
          f"cells_todo={len(todo)} cutoff={EVIDENCE_CUT} "
          f"driver={'pool' if use_pool else 'serial'}")
    if todo:
        prices, P = _panel()
        if prices is None:
            return 2
        _burn_member(m, prices, P, write=True, use_pool=use_pool)
        cells = read_cells(member_id)
    anchor_ok = next((c["anchor"]["pass"] for c in cells
                      if c["kind"] == "center"), None)
    _pool_claim(member_id,
                f"cells={len(cells)} anchor={anchor_ok} "
                f"{'idempotent-no-op' if not todo else 'burn-complete'}")
    return cmd_finalize_one(member_id)


def cmd_probe(wave: str = "r1") -> int:
    """Read-only anchor probe. wave=r1: CENTER-ONLY anchor probe (prereg
    sec.2 evidence face; zero checkpoint writes, zero ledger) reproducing
    the r509 pre-freeze probe facts. wave=r2: the standing R2 4-leg
    probe (r392 receipt absorbed per prereg sec.6)."""
    if wave == "r2":
        return cmd_probe_r2()
    prices, P = _panel()
    if prices is None:
        return 2
    members = load_members()
    out_rows = []
    ok = True
    for m in members:
        spec = FAMILIES[m["id"]]
        state = spec["build"](P, dict(spec["center"]))
        r = _run_cell(prices, P, state, m, {})
        anchor_pass = bool(
            abs(r["in_s"] - m["backtest"]["in_sample"]["sharpe"])
            < ANCHOR_TOL
            and abs(r["oos_s"] - m["backtest"]["out_sample"]["sharpe"])
            < ANCHOR_TOL
            and r["n_in"] == m["backtest"]["in_sample"]["trades"]
            and r["n_oos"] == m["backtest"]["out_sample"]["trades"])
        ok &= anchor_pass
        out_rows.append({"member": m["id"], "anchor_pass": anchor_pass,
                         "full_sharpe": round(_sharpe(r["eq"]), 4)})
        print(f"[{m['id']}] anchor="
              f"{'PASS' if anchor_pass else 'FAIL'}")
    fp = os.path.join(PATHS.results_dir, "_n3r1_probe_latest.json")
    with open(fp, "w", encoding="utf-8") as fh:
        json.dump({"probe": "n3r1-anchor", "ts": _now_iso(),
                   "rows": out_rows, "all_pass": ok}, fh, indent=1)
    print(f"probe: {'ALL PASS' if ok else 'FAIL'} ({len(out_rows)})")
    return 0 if ok else 1


# ==================== R2 wave: time-start robustness grid =================
# prereg research/PERPETUAL_N3_R2_PREREG.md (frozen before any pool burn;
# DRAFT state refuses burns -- materialization law sec.1). R2 stress axis
# = the time-interval START POINT; the 144 window readouts are pure-math
# slices of the center equity curves, so the wave has zero new seed bands.


def r2_derive_starts(idx: pd.DatetimeIndex) -> dict:
    """Frozen start family (prereg sec.2): first trading bar of every
    quarter, panel-first-year .. year before the evidence cutoff. Panel
    head mid-quarter duplicates keep the first claiming key (probe leg S
    law). The 2020-01-02..2026-09-22 panel face -> 2020Q1..2025Q4 = 24."""
    first_year = int(idx[0].year)
    last_year = int(EVIDENCE_CUT[:4]) - 1
    starts, used = {}, set()
    for y in range(first_year, last_year + 1):
        for m in (1, 4, 7, 10):
            hits = idx[idx >= pd.Timestamp(f"{y}-{m:02d}-01")]
            if not len(hits):
                continue
            d = str(hits[0].date())
            if d in used:
                continue
            starts[f"{y}Q{(m - 1) // 3 + 1}"] = d
            used.add(d)
    return starts


def r2_window_rows(eq: pd.Series, starts: dict, mid: str,
                   line: float) -> list:
    """Join-at-start-close semantics (prereg sec.2): the window series is
    the STRICT tail slice (index > s) of the full-history daily returns
    -- the s-1 -> s move belongs to the previous day's investor, not the
    joiner. The rebase cross-path identity (slice path vs rebased path,
    r392 probe leg X) is a standing per-window assertion, not a one-off:
    a slice-math drift fails the shard closed."""
    full_rets = eq.pct_change().dropna()
    rows = []
    for k in sorted(starts):
        s = pd.Timestamp(starts[k])
        rets_sub = full_rets[full_rets.index > s]
        n_days = int(len(rets_sub))
        if n_days < 2:
            raise ValueError(f"window {k} degenerate (n_days={n_days})")
        std = float(rets_sub.std())
        w_s = float(rets_sub.mean() / std * (252 ** 0.5)) if std > 0 else 0.0
        cum = (1.0 + rets_sub).cumprod()
        maxdd = float((cum / cum.cummax() - 1).min())
        rebased = eq[eq.index >= s]
        alt = (rebased / rebased.iloc[0]).pct_change().dropna()
        if not (len(alt) == n_days
                and float(abs(alt.values - rets_sub.values).max())
                < R2_REBASE_TOL):
            raise AssertionError(f"slice-math identity broken at start {k}")
        rows.append({
            "id": f"{mid}::w::{k}", "kind": "window", "member": mid,
            "start": k, "start_date": starts[k], "n_days": n_days,
            "window_sharpe": round(w_s, 4),
            "annual_return": round(float(
                cum.iloc[-1] ** (252 / n_days) - 1), 4),
            "max_dd": round(maxdd, 4),
            "red": bool(w_s <= line),
        })
    return rows


def r2_cells_path(mid: str) -> str:
    return os.path.join(R2_WAVE_DIR, f"cells-{mid}.jsonl")


def r2_read_cells(mid: str) -> list:
    cells = []
    fp = r2_cells_path(mid)
    if os.path.exists(fp):
        with open(fp, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    cells.append(json.loads(line))
                except json.JSONDecodeError:
                    continue      # corrupt tail tolerated (t22 convention)
    return cells


def r2_append_cell(mid: str, rec: dict):
    os.makedirs(R2_WAVE_DIR, exist_ok=True)
    with open(r2_cells_path(mid), "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


_R2_ANCHOR_FIELDS = ("full_sharpe", "in_sharpe", "oos_sharpe",
                     "n_trades", "n_in", "n_oos", "max_dd",
                     "annual_return")


def _r2_center_read(r: dict) -> dict:
    return {"full_sharpe": round(_sharpe(r["eq"]), 4),
            "in_sharpe": round(float(r["in_s"]), 4),
            "oos_sharpe": round(float(r["oos_s"]), 4),
            "n_trades": r["n_trades"], "n_in": r["n_in"],
            "n_oos": r["n_oos"],
            "max_dd": round(float(r["full"]["max_drawdown"]), 4),
            "annual_return": round(float(r["full"]["annual_return"]), 4)}


def _r1_center_cell(mid: str) -> dict:
    """R1 checkpoint center cell = the anchor oracle (R2 replays must be
    bitwise-identical on the frozen anchor fields; prereg sec.3)."""
    fp = os.path.join(WAVE_DIR, f"cells-{mid}.jsonl")
    if not os.path.exists(fp):
        raise FileNotFoundError(f"R1 checkpoint absent for {mid}")
    with open(fp, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            c = json.loads(line)
            if c.get("kind") == "center":
                return c
    raise KeyError(f"R1 center cell not found for {mid}")


def _r2_anchor(read: dict, r1c: dict) -> dict:
    ok = all(read[k] == r1c[k] for k in _R2_ANCHOR_FIELDS)
    return {"pass": bool(ok), "fields": list(_R2_ANCHOR_FIELDS),
            "r1_checkpoint": {k: r1c[k] for k in _R2_ANCHOR_FIELDS}}


def cmd_run_r2(member_id: str) -> int:
    try:
        import psutil
        pri = getattr(psutil, "BELOW_NORMAL_PRIORITY_CLASS", None)
        if pri is not None:
            psutil.Process().nice(pri)   # O-1612 full-load low-priority pool
    except Exception:
        pass
    members = {m["id"]: m for m in load_members()}
    if member_id not in members:
        print(f"HONEST ABORT: unknown member {member_id}")
        return 2
    m = members[member_id]
    mid = m["id"]
    cells = r2_read_cells(mid)
    done = _cells_done(cells)
    have_center = f"{mid}::center" in done
    n_win = sum(1 for c in cells if c.get("kind") == "window")
    if have_center and n_win >= R2_EXPECT_STARTS:
        anchor_ok = next(c for c in cells
                         if c["id"] == f"{mid}::center").get(
                             "anchor", {}).get("pass")
        _pool_claim(mid, f"cells={len(cells)} anchor={anchor_ok} "
                    "idempotent-no-op", wave="r2")
        return cmd_finalize_one(mid, wave="r2")
    prices, P = _panel()
    if prices is None:
        return 2
    starts = r2_derive_starts(P["close"].index)
    if len(starts) != R2_EXPECT_STARTS:
        print(f"HONEST ABORT: start table {len(starts)} != "
              f"{R2_EXPECT_STARTS} (frozen family 2020Q1..2025Q4)")
        return 2
    spec = FAMILIES[mid]
    state = spec["build"](P, dict(spec["center"]))
    r = _run_cell(prices, P, state, m, {})
    read = _r2_center_read(r)
    try:
        r1c = _r1_center_cell(mid)
    except (FileNotFoundError, KeyError) as exc:
        print(f"HONEST ABORT: anchor oracle unavailable: {exc}")
        return 2
    anchor = _r2_anchor(read, r1c)
    if have_center:
        prev = next(c for c in cells if c["id"] == f"{mid}::center")
        if any(prev.get(k) != read[k] for k in read):
            print("HONEST ABORT: stored center row != fresh deterministic "
                  "replay (determinism law)")
            return 2
    else:
        r2_append_cell(mid, {"id": f"{mid}::center", "kind": "center",
                             "member": mid, **read, "anchor": anchor,
                             "starts": starts})
        print(f"[{mid}] center replay anchor="
              f"{'OK' if anchor['pass'] else 'FAIL'}", flush=True)
    n_new = 0
    if anchor["pass"]:
        rows = r2_window_rows(r["eq"], starts, mid,
                              I_LINE[member_regime(m)])
        for row in rows:
            if row["id"] in done:
                prev = next(c for c in cells if c["id"] == row["id"])
                if any(prev.get(k) != row[k] for k in
                       ("start", "start_date", "n_days", "window_sharpe",
                        "annual_return", "max_dd", "red")):
                    print(f"HONEST ABORT: stored window {row['id']} != "
                          "fresh deterministic row")
                    return 2
                continue
            r2_append_cell(mid, row)
            n_new += 1
            print(f"[{mid}] {row['id']}: w_s={row['window_sharpe']} "
                  f"red={row['red']}", flush=True)
    else:
        print(f"[{mid}] ANCHOR FAIL -- all {R2_EXPECT_STARTS} windows "
              "refused (prereg sec.3)", flush=True)
    cells = r2_read_cells(mid)
    _pool_claim(mid, f"cells={len(cells)} anchor={anchor['pass']} "
                + ("burn-complete" if (n_new or not have_center)
                   else "idempotent-no-op"), wave="r2")
    return cmd_finalize_one(mid, wave="r2")


def cmd_probe_r2() -> int:
    """Standing R2 probe (prereg sec.6: the r392 pre-freeze probe receipt
    absorbed as the permanent wave-r2 probe). Legs: P panel face /
    S start table / R center-replay bit-identity / W window readouts with
    the standing rebase cross-path identity. Read-only: zero checkpoint
    writes, zero ledger."""
    rec = {"probe": "PERPETUAL-N3-R2", "machine": _machine_id(),
           "evidence_cutoff": EVIDENCE_CUT,
           "start_family": "quarter-first-bar 2020Q1..2025Q4", "legs": {}}
    prices, P = _panel()
    if P is None:
        rec["legs"]["P"] = {"ok": False, "err": "panel drift (FAIL-CLOSED)"}
        rec["verdict"] = "FAIL"
        fp = os.path.join(PATHS.results_dir, "_n3r2_probe_latest.json")
        with open(fp, "w", encoding="utf-8") as fh:
            json.dump(rec, fh, ensure_ascii=False, indent=1)
        return 1
    idx = P["close"].index
    rec["legs"]["P"] = {
        "ok": True,
        "quadruple": {
            "data_face": "data/daily/sh*.csv (core48 bare codes via "
                        "load_core)",
            "loader": "live.paper.load_core -> build_panels",
            "window_start": str(idx[0].date()),
            "warmup": "vol20/med500 min_periods 20/500 (in-panel)",
        },
        "n_members_panel": int(len(P["close"].columns)),
        "tail": str(idx[-1].date()),
        "n_bars": int(len(idx)),
    }
    starts = r2_derive_starts(idx)
    rec["legs"]["S"] = {"ok": len(starts) == R2_EXPECT_STARTS,
                        "n_starts": len(starts), "starts": starts}
    members = {m["id"]: m for m in load_members()}
    mid = "VOLATILITY-CE-01"
    m = members[mid]
    spec = FAMILIES[mid]
    state = spec["build"](P, dict(spec["center"]))
    r = _run_cell(prices, P, state, m, {})
    read = _r2_center_read(r)
    r1c = _r1_center_cell(mid)
    replay_ok = all(read[k] == r1c[k] for k in _R2_ANCHOR_FIELDS)
    rec["legs"]["R"] = {"ok": bool(replay_ok), "replay": read,
                        "r1_checkpoint": {k: r1c[k]
                                          for k in _R2_ANCHOR_FIELDS}}
    line = I_LINE[member_regime(m)]
    try:
        rows = r2_window_rows(r["eq"], starts, mid, line)
        w_err = None
    except (ValueError, AssertionError) as exc:
        rows, w_err = [], str(exc)
    w_ok = len(rows) == R2_EXPECT_STARTS and w_err is None
    leg_w = {"ok": bool(w_ok), "member": mid, "line": line, "windows": rows,
             "slice_math_identity": "standing assertion in r2_window_rows"}
    if w_err is not None:
        leg_w["err"] = w_err
    if rows:
        sharpes = [w["window_sharpe"] for w in rows]
        q = pd.Series(sharpes).quantile([0.25, 0.5, 0.75])
        leg_w["start_distribution"] = {
            "best": max(sharpes), "worst": min(sharpes),
            "p25": round(float(q[0.25]), 4),
            "median": round(float(q[0.5]), 4),
            "p75": round(float(q[0.75]), 4),
            "worst_start": rows[sharpes.index(min(sharpes))]["start"],
        }
        leg_w["red_rate"] = round(
            sum(w["red"] for w in rows) / len(rows), 4)
    rec["legs"]["W"] = leg_w
    all_ok = all(rec["legs"][k].get("ok") for k in ("P", "S", "R", "W"))
    rec["verdict"] = "PASS" if all_ok else "FAIL"
    fp = os.path.join(PATHS.results_dir, "_n3r2_probe_latest.json")
    with open(fp, "w", encoding="utf-8") as fh:
        json.dump(rec, fh, ensure_ascii=False, indent=1)
    print(f"N3-R2 PROBE {rec['verdict']}: P={rec['legs']['P']['ok']} "
          f"S={rec['legs']['S']['ok']} R={rec['legs']['R']['ok']} "
          f"W={rec['legs']['W']['ok']}")
    if all_ok:
        d = rec["legs"]["W"]["start_distribution"]
        print(f"  starts={rec['legs']['S']['n_starts']} "
              f"red_rate={rec['legs']['W']['red_rate']} "
              f"worst={d['worst']}@{d['worst_start']}")
    return 0 if all_ok else 1


def _r2_member_pack(m: dict, cells: list) -> dict:
    mid = m["id"]
    regime = member_regime(m)
    mc = {c["id"]: c for c in cells}
    center = mc.get(f"{mid}::center")
    pack = {
        "member": mid, "regime": regime,
        "entry": m["params"]["entry"],
        "gate": "perpetual-n3-r2 (prereg research/PERPETUAL_N3_R2_PREREG.md)",
        "lines": {"window_line": I_LINE[regime],
                  "source": "science_gates.recorded_lines() live read"},
        "red_point_pass": False,
    }
    if center is None:
        pack["status"] = "incomplete"
        return pack
    pack["anchor_reverify"] = center.get("anchor")
    if not center.get("anchor", {}).get("pass"):
        pack["status"] = "anchor_broken"
        pack["windows_refused"] = ("anchor_broken -- all 24 windows "
                                   "refused (prereg sec.3)")
        pack["windows"] = []
        return pack
    wins = sorted((c for c in mc.values() if c.get("kind") == "window"),
                  key=lambda c: c["start"])
    pack["windows"] = wins
    pack["n_windows"] = len(wins)
    if wins:
        sharpes = [w["window_sharpe"] for w in wins]
        n_red = sum(1 for w in wins if w["red"])
        worst = min(wins, key=lambda w: w["window_sharpe"])
        q = pd.Series(sharpes).quantile([0.25, 0.5, 0.75])
        pack["start_distribution"] = {
            "best": max(sharpes), "worst": min(sharpes),
            "p25": round(float(q[0.25]), 4),
            "median": round(float(q[0.5]), 4),
            "p75": round(float(q[0.75]), 4),
            "worst_start": worst["start"],
        }
        pack["red_point"] = {
            "windows": len(wins), "red": n_red,
            "clause": "red*2 <= 24 (prereg sec.4 verbatim)",
            "pass": bool(n_red * 2 <= len(wins)),
        }
        pack["red_point_pass"] = pack["red_point"]["pass"]
        pack["worst_start"] = {
            "start": worst["start"], "start_date": worst["start_date"],
            "window_sharpe": worst["window_sharpe"],
            "n_days": worst["n_days"], "max_dd": worst["max_dd"],
        }
    pack["status"] = ("judged" if len(wins) == R2_EXPECT_STARTS
                      else "incomplete")
    return pack


def cmd_finalize_r2(member_id: str | None = None) -> int:
    members = load_members()
    if member_id is not None:
        members = [m for m in members if m["id"] == member_id]
    packs, n_rows, complete = [], 0, True
    for m in members:
        mid = m["id"]
        cells = r2_read_cells(mid)
        n_rows += len(cells)
        pack = _r2_member_pack(m, cells)
        packs.append(pack)
        done = _cells_done(cells)
        center = next((c for c in cells if c["id"] == f"{mid}::center"),
                      None)
        if center is None:
            complete = False
        elif center.get("anchor", {}).get("pass"):
            want = {f"{mid}::w::{k}" for k in center.get("starts", {})}
            complete &= want <= done
        # anchor-broken member: center present = complete face (all 24
        # windows refused per prereg sec.3 -- nothing further to wait for)
        os.makedirs(R2_WAVE_DIR, exist_ok=True)
        with open(os.path.join(R2_WAVE_DIR, f"{mid}.json"), "w",
                  encoding="utf-8") as fh:
            json.dump({**pack, **cutoff_meta(EVIDENCE_CUT),
                       "generated": _now_iso()}, fh, ensure_ascii=False,
                      indent=1)
    if member_id is not None:
        print(f"single-member finalize: {member_id} "
              "(R2 wave finalize deferred)")
        return 0
    if not complete:
        print("HONEST REFUSAL: R2 wave incomplete -- finalize deferred")
        return 2
    batch_ledger = None
    if os.path.exists(R2_BATCH_JSON):
        try:
            with open(R2_BATCH_JSON, encoding="utf-8") as fh:
                prev = json.load(fh)
            if prev.get("complete"):
                batch_ledger = prev.get("trials_ledger")   # idempotent
        except (OSError, ValueError):
            batch_ledger = None
    if batch_ledger is None:
        batch_ledger = append_ledger(
            R2_BATCH, R2_CELLS_NEW,
            file_name="perpetual_faces/n3_r2_results.json",
            note=("N3-R2 time-start robustness grid on 6 registered "
                  "members: 144 quarter-start window readouts all new "
                  "evidence (pure-math strict-tail slices of the center "
                  "equity curves; derived-face nature disclosed per "
                  "prereg sec.0); 6 centers = R1 checkpoint replays "
                  "(+0); zero new seed bands; measurement-deepening "
                  "face, no registration claim"),
            evidence_cutoff=EVIDENCE_CUT)
    n_red_total = sum(p.get("red_point", {}).get("red", 0) for p in packs
                     if p.get("status") != "anchor_broken")
    out = {
        "batch": R2_BATCH,
        "ticket": ("O-20261002-2155 seat split (bm-c N3-R2 seat via "
                   "MSG-2026-10-03-0115; response to the bm-b "
                   "MSG-2026-10-03-0016 seat invite)"),
        "prereg": "research/PERPETUAL_N3_R2_PREREG.md",
        "generated": _now_iso(),
        "members": len(members),
        "complete": True,
        "engine_cells": n_rows,
        "window_cells": R2_CELLS_NEW,
        "packs": [{"member": p["member"], "status": p.get("status"),
                   "anchor_pass": bool(p.get("anchor_reverify", {})
                                      .get("pass")),
                   "n_windows": p.get("n_windows"),
                   "red_windows": p.get("red_point", {}).get("red"),
                   "red_point_pass": p["red_point_pass"],
                   "start_distribution": p.get("start_distribution"),
                   "worst_start": p.get("worst_start")}
                  for p in packs],
        "subleg_counts": {
            "anchor_pass": sum(1 for p in packs
                               if p.get("anchor_reverify", {}).get("pass")),
            "red_point_pass": sum(1 for p in packs if p["red_point_pass"]),
            "windows_total": sum(p.get("n_windows", 0) for p in packs),
            "windows_red": n_red_total,
        },
        "trials_ledger": batch_ledger,
        "audit": {
            "ledger_trials_added": batch_ledger["batch_trials"],
            "ledger_head_after": ledger_head()["total"],
            "note": ("N3 measurement-deepening wave-2 (time-interval "
                     "start-point stress); three-state registration "
                     "verdicts N/A per prereg sec.4; window readouts "
                     "never change member status (month-boundary "
                     "registration pipeline owns that face)"),
        },
    }
    out.update(cutoff_meta(EVIDENCE_CUT))
    os.makedirs(os.path.dirname(R2_BATCH_JSON), exist_ok=True)
    with open(R2_BATCH_JSON, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print(f"packs={len(packs)} engine_rows={n_rows} "
          f"sublegs={out['subleg_counts']} "
          f"ledger+{batch_ledger['batch_trials']} "
          f"head={ledger_head()['total']}")
    print(f"saved: {R2_BATCH_JSON} + {R2_WAVE_DIR} packs")
    return 0


def _member_pack(m: dict, cells: list, line_info: dict) -> dict:
    mid = m["id"]
    regime = member_regime(m)
    mc = {c["id"]: c for c in cells}
    center = mc.get(f"{mid}::center")
    x3 = mc.get(f"{mid}::x3")
    pack = {
        "member": mid, "regime": regime,
        "entry": m["params"]["entry"],
        "gate": "perpetual-n3-r1 (prereg research/PERPETUAL_N3_R1_PREREG.md)",
        "lines": {"nbhd_line": I_LINE[regime], "vi_bar": VI_BAR,
                  "worst_year_floor": WORST_YEAR_FLOOR,
                  "source": "science_gates.recorded_lines() live read"},
        "neighborhood_pass": False, "cost_x3_pass": False,
        "per_year_pass": False,
    }
    if center is None:
        pack["status"] = "incomplete"
        return pack
    anchor = center.get("anchor", {})
    pack["anchor_reverify"] = anchor
    # per-year face from the center cell's stored yearly (burn-time fact;
    # equity curves are not persisted in the checkpoint)
    yearly = center.get("yearly")
    pack["yearly"] = yearly
    worst = min(yearly.values()) if yearly else None
    pack["worst_year"] = worst
    nb_cells = sorted((c for c in mc.values() if c["kind"] == "nbhd"),
                      key=lambda c: str(c["point"]))
    pts = len(nb_cells)
    red_ids = {c["id"] for c in nb_cells
               if float(c["full_sharpe"]) <= I_LINE[regime]}
    if pts == 0:
        pack["neighborhood"] = {"points": 0, "red": 0, "refused": "grid_empty"}
    else:
        pack["neighborhood"] = {
            "points": pts, "red": len(red_ids),
            "clause": "red*2 <= points (G2_FOLK clause 2 verbatim)",
            "cells": [{"point": c["point"], "full_sharpe": c["full_sharpe"],
                       "red": bool(c["id"] in red_ids),
                       "bootstrap_ci_low": c["bootstrap_ci"]["ci95_low"]}
                      for c in nb_cells]}
        pack["neighborhood_pass"] = bool(len(red_ids) * 2 <= pts)
    if x3 is not None:
        pack["x3"] = {"full_sharpe": x3["full_sharpe"],
                      "oos_sharpe": x3["oos_sharpe"],
                      "n_trades": x3["n_trades"]}
    x3_ok = bool(x3 is not None and float(x3["full_sharpe"]) > 0
                 and float(x3["oos_sharpe"]) > 0)
    x2_ok = bool(float(m["backtest"]["cost_x2"]["sharpe"]) > VI_BAR)
    pack["cost_x3_pass"] = bool(x3_ok and x2_ok)
    pack["cost_clause"] = {
        "x3_positive": x3_ok, "recorded_x2_beats_vi": x2_ok,
        "recorded_x2_full_sharpe": m["backtest"]["cost_x2"]["sharpe"],
        "note": "x2>vi on recorded evidence; x3 survival = this wave's cell"}
    pack["per_year_pass"] = bool(worst is not None
                                 and float(worst) > WORST_YEAR_FLOOR)
    pack["center_bootstrap_ci"] = center.get("bootstrap_ci")
    pack["center_dsr"] = center.get("dsr")
    # current-line recheck (prereg sec.3: stress readout, not a gate)
    pack["line_recheck"] = {
        "line": line_info["line"], "n_eff": line_info["n_eff"],
        "center_full_sharpe": center["full_sharpe"],
        "line_ok": bool(float(center["full_sharpe"]) > line_info["line"])}
    pack["g2_registration_v2"] = g2_registration_v2(
        g1_pass=pack["line_recheck"]["line_ok"],
        dsr=center.get("dsr") or {"dsr": 0.0}, pbo=None)
    pack["status"] = ("judged" if anchor.get("pass") else "anchor_broken")
    if pack["status"] == "anchor_broken":
        pack["neighborhood_pass"] = False
        pack["cost_x3_pass"] = False
        pack["per_year_pass"] = False
    return pack


def cmd_finalize_one(member_id: str | None = None,
                    wave: str = "r1") -> int:
    if wave == "r2":
        return cmd_finalize_r2(member_id)
    members = load_members()
    if member_id is not None:
        members = [m for m in members if m["id"] == member_id]
    line_info = skill_line_v2(batch_cells=BATCH_CELLS_NEW)
    packs, n_cells, complete = [], 0, True
    for m in members:
        cells = read_cells(m["id"])
        n_cells += len(cells)
        pack = _member_pack(m, cells, line_info)
        packs.append(pack)
        need = _cells_done(cells)
        spec = FAMILIES[m["id"]]
        want = {f"{m['id']}::center", f"{m['id']}::x3"} \
            | {cell_id(m["id"], "nbhd", {p: v})
               for p, lo, hi in spec["oat"] for v in (lo, hi)}
        complete &= want <= need
        os.makedirs(WAVE_DIR, exist_ok=True)
        with open(os.path.join(WAVE_DIR, f"{m['id']}.json"), "w",
                  encoding="utf-8") as fh:
            json.dump({**pack, **cutoff_meta(EVIDENCE_CUT),
                       "generated": _now_iso()}, fh, ensure_ascii=False,
                      indent=1)
    if member_id is not None:
        print(f"single-member finalize: {member_id} "
              f"complete={complete} (wave finalize deferred)")
        return 0
    if not complete:
        print("HONEST REFUSAL: wave incomplete -- finalize deferred")
        return 2

    batch_ledger = None
    if os.path.exists(BATCH_JSON):
        try:
            with open(BATCH_JSON, encoding="utf-8") as fh:
                prev = json.load(fh)
            if prev.get("complete"):
                batch_ledger = prev.get("trials_ledger")   # idempotent
        except (OSError, ValueError):
            batch_ledger = None
    if batch_ledger is None:
        batch_ledger = append_ledger(
            BATCH, BATCH_CELLS_NEW, file_name="perpetual_faces/n3_r1_results.json",
            note="N3-R1 neighborhood stress grid on 6 registered members: "
                 "22 OAT nbhd + 6 x3 cells all new evidence (x3 provenance "
                 "unverified/batch-era constructions per prereg sec.0 -- "
                 "NEEDLE smoke-verified non-replay 0.3729 vs recorded "
                 "0.4833); 6 centers = recorded-cell replays (+0, t24 "
                 "precedent); measurement-deepening face, no registration "
                 "claim",
            evidence_cutoff=EVIDENCE_CUT)
    out = {
        "batch": BATCH,
        "ticket": "T-2026-09-30-133",
        "prereg": "research/PERPETUAL_N3_R1_PREREG.md",
        "generated": _now_iso(),
        "members": len(members),
        "complete": True,
        "engine_cells": n_cells,
        "packs": [{"member": p["member"], "status": p.get("status"),
                   "neighborhood_pass": p["neighborhood_pass"],
                   "cost_x3_pass": p["cost_x3_pass"],
                   "per_year_pass": p["per_year_pass"],
                   "line_recheck": p.get("line_recheck"),
                   "g2_v2_eligible": p.get("g2_registration_v2",
                                           {}).get("eligible_v2")}
                  for p in packs],
        "subleg_counts": {
            "neighborhood_pass": sum(1 for p in packs
                                     if p["neighborhood_pass"]),
            "cost_x3_pass": sum(1 for p in packs if p["cost_x3_pass"]),
            "per_year_pass": sum(1 for p in packs if p["per_year_pass"]),
            "line_recheck_pass": sum(1 for p in packs
                                     if p.get("line_recheck",
                                              {}).get("line_ok")),
        },
        "trials_ledger": batch_ledger,
        "audit": {
            "ledger_trials_added": batch_ledger["batch_trials"],
            "ledger_head_after": ledger_head()["total"],
            "note": "G2 evidence-supply deepening face (PERPETUAL_FACES "
                    "sec.2 N3); three-state registration verdicts N/A; "
                    "member files read-only; g2_registration_v2 pbo=None "
                    "refused honestly (single-member families = no legal "
                    "CSCV sample, missing_inputs disclosed)",
        },
    }
    out.update(cutoff_meta(EVIDENCE_CUT))
    os.makedirs(os.path.dirname(BATCH_JSON), exist_ok=True)
    with open(BATCH_JSON, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print(f"packs={len(packs)} engine_cells={n_cells} "
          f"sublegs={out['subleg_counts']} "
          f"ledger+{batch_ledger['batch_trials']} "
          f"head={ledger_head()['total']}")
    print(f"saved: {BATCH_JSON} + {WAVE_DIR} packs")
    return 0


def cmd_status() -> int:
    members = load_members()
    total_done = 0
    total_plan = 0
    for m in members:
        spec = FAMILIES[m["id"]]
        cells = read_cells(m["id"])
        done = _cells_done(cells)
        n_plan = 2 + 2 * len(spec["oat"])
        total_done += len(done)
        total_plan += n_plan
        print(f"{m['id']}: {len(done)}/{n_plan} cells "
              f"(anchor_fail={len(_anchor_fail_ids(cells))})")
    print(f"wave R1: {total_done}/{total_plan} cells")
    r2_done = 0
    for m in members:
        cells = r2_read_cells(m["id"])
        n_win = sum(1 for c in cells if c.get("kind") == "window")
        anchor = next((c.get("anchor", {}).get("pass")
                       for c in cells if c["id"] == f"{m['id']}::center"),
                      None)
        print(f"R2 {m['id']}: 1 center + {n_win}/{R2_EXPECT_STARTS} "
              f"windows (anchor={anchor})")
        r2_done += 1 + n_win
    print(f"wave R2: {r2_done}/{len(members) * (1 + R2_EXPECT_STARTS)} "
          f"rows (centers + window readouts)")
    return 0


def _synth_panel(n=900, seed=20260924):
    import numpy as np
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2023-01-02", periods=n)
    close = pd.DataFrame(
        {"AAA": 1 + np.cumsum(rng.normal(0.0002, 0.01, n)),
         "BBB": 1 + np.cumsum(rng.normal(-0.0001, 0.015, n))},
        index=idx)
    high = close * (1 + np.abs(rng.normal(0, 0.006, (n, 2))))
    low = close * (1 - np.abs(rng.normal(0, 0.006, (n, 2))))
    open_ = close.shift(1).fillna(1.0)
    vol = pd.DataFrame(rng.lognormal(12, .4, (n, 2)), index=idx,
                       columns=close.columns)
    return {"open": open_, "high": high, "low": low, "close": close,
            "volume": vol, "amount": vol * close}


def cmd_selftest() -> int:
    ok = True
    from live.paper import SIGNAL_BUILDERS

    # S1: parametrized builder == frozen SIGNAL_BUILDERS at center
    P = _synth_panel()
    s1 = True
    for mid, spec in FAMILIES.items():
        mine = spec["build"](P, dict(spec["center"]))
        # member entry key comes from the registry files (real-data leg
        # below); synth leg uses the builder directly vs the frozen keys
        # via the member file in S3 -- here assert determinism + causality
        half = P["close"].shape[0] // 2
        shorth = spec["build"]({k: d.iloc[:half] for k, d in P.items()},
                               dict(spec["center"]))
        if not bool((mine.iloc[:half].values == shorth.values).all()):
            print(f"FAIL S1: {mid} center build not causal")
            s1 = False
        if bool(mine.isna().any().any()):
            print(f"FAIL S1: {mid} center build has NaN")
            s1 = False
    members = load_members()
    for m in members:
        spec = FAMILIES[m["id"]]
        mine = spec["build"](P, dict(spec["center"]))
        frozen = SIGNAL_BUILDERS[m["params"]["entry"]](P)
        if not mine.equals(frozen):
            print(f"FAIL S1: {m['id']} center != frozen key")
            s1 = False
    print(f"S1 center-equivalence: {'PASS' if s1 else 'FAIL'} "
          f"({len(FAMILIES)} families)")
    ok &= s1

    # S2: OAT coupling -- steps ordered around center, constructors
    # accept perturbations, causal, no NaN.
    s2 = True
    half = P["close"].shape[0] // 2
    for mid, spec in FAMILIES.items():
        ctr_map = spec["center"]
        for pname, lo, hi in spec["oat"]:
            ctr = ctr_map[pname]
            if not (min(lo, hi) < ctr < max(lo, hi) and lo != hi):
                print(f"FAIL S2: {mid} {pname} steps not ordered")
                s2 = False
            for v in (lo, hi):
                pp = dict(ctr_map)
                pp[pname] = v
                try:
                    got = spec["build"](P, pp)
                except (TypeError, KeyError) as exc:
                    print(f"FAIL S2: {mid} {pname}={v} rejected: {exc}")
                    s2 = False
                    continue
                shorth = spec["build"]({k: d.iloc[:half] for k, d in P.items()}, pp)
                if not (bool((got.iloc[:half].values == shorth.values).all())
                        and not bool(got.isna().any().any())):
                    print(f"FAIL S2: {mid} {pname}={v} causal/NaN")
                    s2 = False
    print(f"S2 oat-coupling: {'PASS' if s2 else 'FAIL'}")
    ok &= s2

    # S3: member registry -- 6 members, spec coverage, cutoff intact.
    s3 = bool(len(members) == N_MEMBERS
              and all(m["id"] in FAMILIES for m in members)
              and all(m.get("evidence_cutoff") == EVIDENCE_CUT
                      for m in members)
              and all(m["backtest"]["cost_x2"].get("sharpe") is not None
                      for m in members))
    print(f"S3 member-registry: {'PASS' if s3 else 'FAIL'} "
          f"({len(members)} members)")
    ok &= s3

    # S4: judgment arithmetic (frozen clauses on synthetic values).
    s4 = True

    def _nb(pts, red):
        return bool(pts > 0 and red * 2 <= pts)

    if not (_nb(6, 3) and not _nb(6, 4) and _nb(2, 1)
            and not _nb(2, 2) and not _nb(0, 0)):
        print("FAIL S4: neighborhood clause arithmetic")
        s4 = False

    def _cx(x3f, x3o, x2):
        return bool(x3f > 0 and x3o > 0 and x2 > VI_BAR)

    if not (_cx(0.1, 0.05, VI_BAR + 0.01)
            and not _cx(0.1, 0.05, VI_BAR - 0.01)
            and not _cx(0.1, -0.05, VI_BAR + 0.01)):
        print("FAIL S4: cost_x3 clause arithmetic")
        s4 = False
    if not ((WORST_YEAR_FLOOR + 0.01 > WORST_YEAR_FLOOR)
            and not (WORST_YEAR_FLOOR - 0.01 > WORST_YEAR_FLOOR)):
        print("FAIL S4: per-year floor strictness")
        s4 = False
    g2 = g2_registration_v2(g1_pass=True, dsr={"dsr": 0.97}, pbo=None)
    if not (g2["eligible_v2"] is False
            and g2["missing_inputs"] == ["family_pbo"]):
        print("FAIL S4: g2_registration_v2 honest-missing refusal")
        s4 = False
    print(f"S4 judgment-arithmetic: {'PASS' if s4 else 'FAIL'}")
    ok &= s4

    # S5: checkpoint idempotence on a fixture JSONL (tmp dir).
    s5 = True
    import tempfile
    global WAVE_DIR
    with tempfile.TemporaryDirectory() as td:
        old = WAVE_DIR
        try:
            WAVE_DIR = td
            m0 = members[0]
            _append_cell(m0["id"], {"id": f"{m0['id']}::center",
                                    "member": m0["id"], "kind": "center",
                                    "anchor": {"pass": True}})
            _append_cell(m0["id"], {"id": f"{m0['id']}::x3",
                                     "member": m0["id"], "kind": "x3"})
            cells = read_cells(m0["id"])
            plan = cells_todo(m0, cells, set())
            ids = [cell_id(m0["id"], k, p) for (k, p) in plan]
            spec = FAMILIES[m0["id"]]
            expect = {cell_id(m0["id"], "nbhd", {pn: v})
                      for pn, lo, hi in spec["oat"] for v in (lo, hi)}
            if set(ids) != expect or len(ids) != len(set(ids)):
                print(f"FAIL S5: idempotence ids={ids}")
                s5 = False
        finally:
            WAVE_DIR = old
    print(f"S5 checkpoint-idempotence: {'PASS' if s5 else 'FAIL'}")
    ok &= s5

    # S6: machine-linked lines + seed-band disjoint (registry law).
    s6 = bool(I_LINE["default"] == RL["i_line"]
              and I_LINE["ce"] == RL["ce_null_p4_batch1"]
              and VI_BAR == RL["vi_bar"]
              and abs(VI_BAR - 0.4004) < 1e-9
              and abs(I_LINE["default"] - 0.3521) < 1e-9
              and abs(I_LINE["ce"] - 0.4474) < 1e-9
              and SEED_REGISTRY.get("perpetual_n3_r1") == SEED_BASE
              and all(abs(v - SEED_BASE) >= 500
                      for v in SEED_REGISTRY.values()
                      if isinstance(v, int) and v != SEED_BASE)
              and MEMBER_ORDER == sorted(FAMILIES)
              and [SEED_BASE + i for i in range(N_MEMBERS)]
              == [SEED_BASE + i for i, _ in enumerate(MEMBER_ORDER)])
    # position-control arithmetic (prereg sec.3 frozen convention)
    s6 &= bool(round(0.95 / 6, 4) == 0.1583 and round(0.95 / 4, 4) == 0.2375
               and round(0.9496 / 10, 4) == 0.095 and round(0.5 / 6, 4) == 0.0833)
    print(f"S6 machine-linked-lines+seeds: {'PASS' if s6 else 'FAIL'}")
    ok &= s6

    # S6b: R1 seed values vs the N1 law-mirror bands -- adjudicated
    # two-state leg (r529 bm-a, canon sec.4 amendment row). The W13 A band
    # (70_001..72_000, frozen bm-b r512) overlaps the R1 CI seeds
    # 70_001..70_005: root cause = R1 registered only its base point
    # 70_000 in SEED_REGISTRY while the runner consumes base+member-index
    # values, and the W13 freeze-time scan face was registry-points-only
    # (evidence results/_r529bma_n3r1_w13_overlap_scan.py). Ruling: no
    # re-burn (different mechanisms -- bootstrap resample indices vs N1
    # entry matrices; no ledger double-count; R250 frozen bands; holiday
    # meaning gate). This leg pins the adjudicated overlap set exactly;
    # any OTHER N1 band value landing inside the R1 seed set is a fresh
    # violation and fails fail-closed.
    s6b = True
    try:
        import perpetual_faces as pf
        r1_seeds = {SEED_BASE + i for i in range(N_MEMBERS)}
        hit = set()
        for _w, cfg in pf.N1_BANDS.items():
            a_lo, a_hi = cfg["a"]
            b_lo, b_hi = cfg["b_exit"]
            hit |= {v for v in r1_seeds if a_lo <= v <= a_hi}
            hit |= {v for v in r1_seeds if b_lo <= v <= b_hi}
        expected = {70_001, 70_002, 70_003, 70_004, 70_005}
        s6b = hit == expected
        if not s6b:
            print(f"FAIL S6b: N1-band x R1-seed overlap {sorted(hit)} "
                  f"!= adjudicated {sorted(expected)}")
    except Exception as exc:  # fail-closed (law-mirror import/scan)
        s6b = False
        print(f"FAIL S6b: law-mirror scan error: {exc}")
    print(f"S6b N1-band x R1-seed adjudicated-overlap pin: "
          f"{'PASS' if s6b else 'FAIL'}")
    ok &= s6b

    # S7: pool-entry single-source face (generator contract).
    s7 = bool(pool_entry_id("VOLATILITY-CE-01")
               == "PERPETUAL-N3-R1-VOLATILITY-CE-01")
    print(f"S7 pool-entry-id: {'PASS' if s7 else 'FAIL'}")
    ok &= s7

    # S8: S-mp parity legs (O-2026-09-30-2355 s2; ems S18 idiom): inline
    # task == spawn+pickle+initializer pool path (bit-identical canonical
    # payloads), double-run determinism, worker-count face -- synthetic
    # fixtures, zero real-data burn, zero writes.
    s8 = True
    try:
        Ps = _synth_panel(n=320)
        syms = list(Ps["close"].columns)
        prices_s = {s: pd.DataFrame({"open": Ps["open"][s],
                                     "high": Ps["high"][s],
                                     "low": Ps["low"][s],
                                     "close": Ps["close"][s]})
                    for s in syms}
        m_vol = next(m for m in members if m["id"] == "VOLATILITY-CE-01")
        seed_v = SEED_BASE + MEMBER_ORDER.index("VOLATILITY-CE-01")
        # low_vol rotation binds on any panel (ranking fires continuously;
        # rare-event families like needle bind only on real crash days --
        # t24 S2 WARN precedent -- so the parity fixture uses VOLATILITY)
        inline_c = _compute_cell(m_vol, "center", {}, seed_v,
                                 prices_s, Ps)
        inline_n = _compute_cell(m_vol, "nbhd", {"n": 50}, seed_v,
                                 prices_s, Ps)

        def _canon(x):
            return json.dumps(x, sort_keys=True, default=float)

        def _collect(key, payload):
            _collect.out[key] = payload
        _collect.out = {}
        res_p = run_cells_parallel(
            [("c", _cell_task, (m_vol, "center", {}, seed_v)),
             ("n", _cell_task, (m_vol, "nbhd", {"n": 50}, seed_v))],
            workers=2, desc="n3r1-s-mp", initializer=_init_pool_ctx,
            initargs=(prices_s, Ps), on_result=_collect)
        w_face = res_p.pop("__workers__", None)
        if w_face != 2:
            print(f"FAIL S8: worker count face {w_face} != 2")
            s8 = False
        if _canon(_collect.out.get("c")) != _canon(inline_c) \
                or _canon(_collect.out.get("n")) != _canon(inline_n):
            print("FAIL S8: pool task != inline task (parity drift)")
            s8 = False
        _collect.out = {}
        run_cells_parallel(
            [("c", _cell_task, (m_vol, "center", {}, seed_v)),
             ("n", _cell_task, (m_vol, "nbhd", {"n": 50}, seed_v))],
            workers=2, desc="n3r1-s-mp2", initializer=_init_pool_ctx,
            initargs=(prices_s, Ps), on_result=_collect)
        _collect.out.pop("__workers__", None)
        if _canon(_collect.out.get("c")) != _canon(inline_c):
            print("FAIL S8: double-run determinism drift")
            s8 = False
    except Exception as ex:
        print(f"FAIL S8: S-mp leg exception {type(ex).__name__}: {ex}")
        s8 = False
    print(f"S8 s-mp-parity: {'PASS' if s8 else 'FAIL'}")
    ok &= s8

    # S9: R2 wave machinery (synthetic fixtures; zero real-data burns,
    # zero writes outside the tmp-dir fixture).
    s9 = True
    try:
        # S9a: frozen start family -- 24 quarter-first bars, label order,
        # and the panel-head mid-quarter dedup face.
        idx = pd.date_range("2020-01-03", "2025-12-30", freq="B")
        starts = r2_derive_starts(idx)
        keys = list(starts)
        if not (len(starts) == R2_EXPECT_STARTS
                and keys[0] == "2020Q1" and keys[-1] == "2025Q4"
                and keys == sorted(keys)):
            print(f"FAIL S9a: start family {len(starts)} {keys[:3]}...")
            s9 = False
        head_mid = pd.date_range("2020-02-17", "2025-12-30", freq="B")
        s2m = r2_derive_starts(head_mid)
        if not (len(s2m) == R2_EXPECT_STARTS
                and len(set(s2m.values())) == R2_EXPECT_STARTS
                and s2m["2020Q1"] == "2020-02-17"):
            print("FAIL S9a: mid-quarter head dedup")
            s9 = False

        # S9b: join-at-start-close semantics + window readout math. eq
        # jumps +100% INTO the start bar; the joiner must NOT earn it.
        dts = pd.date_range("2020-01-02", periods=6, freq="D")
        eq = pd.Series([100.0, 200.0, 200.0, 210.0, 220.0, 198.0],
                       index=dts)
        st = {"T0": str(dts[1].date())}      # join at bar-1 close
        rows = r2_window_rows(eq, st, "TEST-01", line=1.0)
        full_rets = eq.pct_change().dropna()
        tail = full_rets[full_rets.index > dts[1]]
        if not (len(rows) == 1 and rows[0]["n_days"] == 4
                and rows[0]["start_date"] == str(dts[1].date())
                and abs(rows[0]["window_sharpe"]
                        - float(tail.mean() / tail.std()
                                * (252 ** 0.5))) < 5e-5):
            print(f"FAIL S9b: window row {rows}")
            s9 = False
        cum = (1.0 + tail).cumprod()
        if not (abs(rows[0]["annual_return"]
                    - float(cum.iloc[-1] ** (252 / 4) - 1)) < 5e-5
                and abs(rows[0]["max_dd"]
                        - float((cum / cum.cummax() - 1).min())) < 5e-5):
            print("FAIL S9b: annual/maxdd arithmetic")
            s9 = False
        if not (float(tail.iloc[0]) == 0.0
                and float(abs(tail.values).max()) < 1.0):
            print("FAIL S9b: strict-tail slice leaked the join-day move")
            s9 = False

        # S9c: red clause arithmetic (frozen clause red*2 <= 24) + the
        # window red flag vs the member line.
        if not (bool(12 * 2 <= 24) and not bool(13 * 2 <= 24)):
            print("FAIL S9c: red-point clause boundary")
            s9 = False
        red_hi = r2_window_rows(eq, st, "TEST-01", line=100.0)[0]["red"]
        red_lo = r2_window_rows(eq, st, "TEST-01", line=-100.0)[0]["red"]
        if not (red_hi is True and red_lo is False):
            print("FAIL S9c: window red flag vs line")
            s9 = False

        # S9d: zero-new-seed-band pin (prereg sec.3: R2 has NO random
        # face; SEED_REGISTRY must not carry a perpetual_n3_r2 key).
        if "perpetual_n3_r2" in SEED_REGISTRY:
            print("FAIL S9d: SEED_REGISTRY carries an R2 key "
                  "(zero-new-seeds law)")
            s9 = False

        # S9e: wave-scoped pool entry ids (single-source face; the R1
        # form must stay byte-stable for the generator import).
        if not (pool_entry_id("VOLATILITY-CE-01")
                == "PERPETUAL-N3-R1-VOLATILITY-CE-01"
                and pool_entry_id("VOLATILITY-CE-01", wave="r2")
                == "PERPETUAL-N3-R2-VOLATILITY-CE-01"):
            print("FAIL S9e: wave-scoped pool entry id")
            s9 = False

        # S9f: R2 checkpoint idempotence on a fixture JSONL (tmp dir);
        # the center row carries the start table so finalize needs no
        # panel reload.
        import tempfile
        global R2_WAVE_DIR
        with tempfile.TemporaryDirectory() as td:
            old_r2 = R2_WAVE_DIR
            try:
                R2_WAVE_DIR = td
                mid0 = members[0]["id"]
                r2_append_cell(mid0, {"id": f"{mid0}::center",
                                       "kind": "center", "member": mid0,
                                       "anchor": {"pass": True},
                                       "starts": {"2020Q1": "2020-01-03",
                                                  "2020Q2": "2020-04-01"}})
                r2_append_cell(mid0, {"id": f"{mid0}::w::2020Q1",
                                      "kind": "window", "member": mid0,
                                      "start": "2020Q1"})
                cells_fx = r2_read_cells(mid0)
                if not (len(cells_fx) == 2
                        and sum(1 for c in cells_fx
                                if c.get("kind") == "window") == 1):
                    print("FAIL S9f: R2 fixture readback")
                    s9 = False
                done_fx = _cells_done(cells_fx)
                missing = {f"{mid0}::w::{k}"
                           for k in ("2020Q1", "2020Q2")} - done_fx
                if missing != {f"{mid0}::w::2020Q2"}:
                    print(f"FAIL S9f: idempotence missing={missing}")
                    s9 = False
            finally:
                R2_WAVE_DIR = old_r2

        # S9g: anchor gate on synthetic dicts (bitwise field compare).
        base = dict.fromkeys(_R2_ANCHOR_FIELDS, 1)
        if not (_r2_anchor(base, base)["pass"]
                and not _r2_anchor(base,
                                   {**base, "max_dd": 0.999})["pass"]):
            print("FAIL S9g: anchor gate arithmetic")
            s9 = False
    except Exception as ex:
        print(f"FAIL S9: exception {type(ex).__name__}: {ex}")
        s9 = False
    print(f"S9 r2-machinery: {'PASS' if s9 else 'FAIL'}")
    ok &= s9

    print(f"selftest: {'ALL PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--member", required=True)
    r.add_argument("--wave", choices=("r1", "r2"), default="r1")
    r.add_argument("--serial", action="store_true",
                   help="serial driver (parity/hermetic leg; pool entries "
                        "are served by the pooled driver per law-1)")
    sub.add_parser("status")
    p = sub.add_parser("probe")
    p.add_argument("--wave", choices=("r1", "r2"), default="r1")
    f = sub.add_parser("finalize")
    f.add_argument("--member", default=None)
    f.add_argument("--wave", choices=("r1", "r2"), default="r1")
    sub.add_parser("selftest")
    args = ap.parse_args()
    if args.cmd == "run":
        return cmd_run(args.member, use_pool=not args.serial,
                       wave=args.wave)
    if args.cmd == "status":
        return cmd_status()
    if args.cmd == "probe":
        return cmd_probe(wave=args.wave)
    if args.cmd == "finalize":
        return cmd_finalize_one(args.member, wave=args.wave)
    return cmd_selftest()


if __name__ == "__main__":
    sys.exit(main())
