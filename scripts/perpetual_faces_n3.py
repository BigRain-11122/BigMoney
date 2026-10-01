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
  python scripts/perpetual_faces_n3.py run --member <ID>   # one shard
  python scripts/perpetual_faces_n3.py status
  python scripts/perpetual_faces_n3.py probe               # read-only anchor
  python scripts/perpetual_faces_n3.py finalize
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


def _burn_member(m: dict, prices, P, write: bool = True) -> list:
    """Burn all remaining cells for one member; returns new cell records.
    write=False = probe face (in-memory only, checkpoint untouched)."""
    mid = m["id"]
    spec = FAMILIES[mid]
    seed = SEED_BASE + MEMBER_ORDER.index(mid)
    regime = member_regime(m)
    cells = read_cells(mid) if write else []
    anchor_fail = _anchor_fail_ids(cells) if write else set()
    todo = cells_todo(m, cells, anchor_fail)
    new_recs = []
    for kind, point in todo:
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
               "bootstrap_ci": bootstrap_ci_sharpe(r["rets"], seed=seed),
               "ts": time.strftime("%Y-%m-%d %H:%M:%S")}
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
            rec["dsr"] = deflated_sharpe_ratio(
                r["rets"], n_trials=int(ledger_head()["total"]))
        new_recs.append(rec)
        if write:
            _append_cell(mid, rec)
            print(f"[{mid}] {rec['id']}: full_s={rec['full_sharpe']} "
                  f"in_s={rec['in_sharpe']} oos_s={rec['oos_sharpe']} "
                  f"trades={rec['n_trades']}"
                  + (f" anchor={'OK' if rec['anchor']['pass'] else 'FAIL'}"
                     if kind == "center" else ""), flush=True)
    return new_recs


# ------------------------------------------------------- pool handshake (r497)
def _pool_claim(mid: str, detail: str, write: bool = True) -> None:
    if not write:
        return
    entry_id = pool_entry_id(mid)
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


def pool_entry_id(mid: str) -> str:
    """Single-source entry-id face: the generator imports this so the
    pool entries and the runner handshake can never drift apart."""
    return f"{BATCH}-{mid}"


def cmd_run(member_id: str) -> int:
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
          f"cells_todo={len(todo)} cutoff={EVIDENCE_CUT}")
    if todo:
        prices, P = _panel()
        if prices is None:
            return 2
        _burn_member(m, prices, P, write=True)
        cells = read_cells(member_id)
    anchor_ok = next((c["anchor"]["pass"] for c in cells
                      if c["kind"] == "center"), None)
    _pool_claim(member_id,
                f"cells={len(cells)} anchor={anchor_ok} "
                f"{'idempotent-no-op' if not todo else 'burn-complete'}")
    return cmd_finalize_one(member_id)


def cmd_probe() -> int:
    """Read-only CENTER-ONLY anchor probe (prereg sec.2 evidence face;
    zero checkpoint writes, zero ledger). Reproduces the r509 pre-freeze
    probe facts and doubles as the real-data smoke of the assembly/config
    segment (r506 law: selftest green != burnable)."""
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


def cmd_finalize_one(member_id: str | None = None) -> int:
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
    print(f"wave: {total_done}/{total_plan} cells")
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

    # S7: pool-entry single-source face (generator contract).
    s7 = bool(pool_entry_id("VOLATILITY-CE-01")
               == "PERPETUAL-N3-R1-VOLATILITY-CE-01")
    print(f"S7 pool-entry-id: {'PASS' if s7 else 'FAIL'}")
    ok &= s7

    print(f"selftest: {'ALL PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--member", required=True)
    sub.add_parser("status")
    sub.add_parser("probe")
    f = sub.add_parser("finalize")
    f.add_argument("--member", default=None)
    sub.add_parser("selftest")
    args = ap.parse_args()
    if args.cmd == "run":
        return cmd_run(args.member)
    if args.cmd == "status":
        return cmd_status()
    if args.cmd == "probe":
        return cmd_probe()
    if args.cmd == "finalize":
        return cmd_finalize_one(args.member)
    return cmd_selftest()


if __name__ == "__main__":
    sys.exit(main())
