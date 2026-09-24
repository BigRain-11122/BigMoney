"""T-2026-09-24-20 PAPER_GUARD_DUAL_RAIL acceptance gates (G0-G6).

Prereg (frozen R71, BEFORE implementation): research/PAPER_GUARD_DUAL_RAIL.md
Family: cost_v2_gates / cash_leg_gates / regime_enforce_gates (tool-validation,
zero registration claims, ledger_trials_added=0).

Subcommands:
  baseline  capture the PRE-change paper_run / cost_x2_check / monthly outputs
            on the frozen face (cutoff 2026-09-23). MUST run before the wiring
            commit (prereg s4 G2: 改前基线=实现 commit 前先行落盘).
  run       G0-G6 acceptance -> results/paper_guard_dual_rail.json
            (G6 executes the post-commit production cutover run).
  selftest  offline G3 fixture cases + shape helpers (no data loads).
"""
from __future__ import annotations

import datetime as dt
import json
import os
import subprocess
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import pandas as pd  # noqa: E402

import live.paper as lp  # noqa: E402

FROZEN_CUTOFF = "2026-09-23"          # prereg s3 evidence face
BASELINE_PATH = os.path.join(_REPO, "results", "paper_guard_baseline.json")
OUT_PATH = os.path.join(_REPO, "results", "paper_guard_dual_rail.json")
PAPER_DIR = os.path.join(_REPO, "results", "paper")
X2_LOG = os.path.join(_REPO, "results", "x2_watch_log.jsonl")
GUARD_SOURCE = "t14_rules_fidelity.build_guard"
# additive disclosure keys present whenever a guard is supplied (T-21 G1a
# precedent: noop equality strips additive keys, behavior keys stay)
ADDITIVE_KEYS = {"fill_guard_buy_dropped", "fill_guard_sell_deferred_events",
                 "fill_guard_deferred_days_total", "fill_guard_first_deferred_date"}


def _traders() -> list[dict]:
    out = []
    for path in sorted(lp.TRADERS_DIR.glob("*.json")):
        if path.name.startswith("_"):
            continue
        t = lp.load_trader(path.stem)
        if t.get("level") in lp.PAPER_LEVELS:
            out.append(t)
    return out


def _frozen_face() -> tuple[dict, dict]:
    prices_full = lp.load_core()
    ps = pd.Timestamp(FROZEN_CUTOFF)
    prices = {s: df[df.index <= ps] for s, df in prices_full.items()}
    return prices, lp.build_panels(prices)


def _ser_run(run: dict) -> dict:
    eq = run["equity"]
    return {"bars": run["bars"], "metrics": run["metrics"],
            "trades": run["trades"],
            "equity": ({"dates": [str(d.date()) for d in eq.index],
                        "values": [float(v) for v in eq.values]}
                       if eq is not None else None)}


def _deser_run(s: dict) -> dict:
    eq = (pd.Series(s["equity"]["values"],
                    index=pd.to_datetime(s["equity"]["dates"]))
          if s["equity"] is not None else None)
    return {"bars": s["bars"], "metrics": s["metrics"], "trades": s["trades"],
            "equity": eq}


def _all_true_guard(P: dict) -> dict:
    idx = P["close"].index
    cols = list(P["close"].columns)
    return {"buy": pd.DataFrame(True, index=idx, columns=cols),
            "sell": pd.DataFrame(True, index=idx, columns=cols)}


def _clean(metrics: dict) -> dict:
    return {k: v for k, v in metrics.items() if k not in ADDITIVE_KEYS}


def _x_clean(x2: dict) -> dict:
    return x2


# ---------------------------------------------------------------- baseline

def capture_baseline() -> int:
    print(f"[t20] capturing PRE-change baseline on frozen face "
          f"(cutoff {FROZEN_CUTOFF})...")
    prices, P = _frozen_face()
    vi_bar = lp.load_vi_bar()
    out = {"batch": "paper_guard_dual_rail_baseline", "ticket": "T-2026-09-24-20",
           "class": "tool-validation", "evidence_cutoff": FROZEN_CUTOFF,
           "frozen_face_last_bar": str(P["close"].index[-1].date()),
           "traders": {}}
    for t in _traders():
        anchor = lp.anchor_gate(t, prices)
        assert anchor["ok"], f"anchor FAIL {t['id']}: {anchor.get('error')}"
        run = lp.paper_run(t, prices, P)
        x2 = lp.cost_x2_check(t, prices, P, vi_bar)
        agg = lp.monthly_aggregate(run["equity"], lp.INITIAL_CASH, t["created"])
        out["traders"][t["id"]] = {
            "anchor_got": anchor["got"], "anchor_cutoff": anchor["cutoff"],
            "paper_run": _ser_run(run), "cost_x2": x2, "monthly": agg,
        }
        print(f"[t20]   {t['id']}: bars={run['bars']} "
              f"trades={len(run['trades'])} x2={x2.get('status')}")
    with open(BASELINE_PATH, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print(f"[t20] baseline written: {BASELINE_PATH} "
          f"({len(out['traders'])} traders)")
    return 0


# ---------------------------------------------------------------- G3 fixture

def _fixture_panel() -> tuple[dict, dict, str, str, str]:
    """3-symbol synthetic window, 80 bdays. Signal = low_vol_long(n=60,
    top_k=5, daily): all 3 members enter from bar 61 (exec day d61 open).

    Case legs (hand-crafted guard cells, engine P4-B2 consumption):
      S1: sell-blocked on its hard-stop day -> deferred one close (case 1)
      S2: buy-blocked on first exec day -> order dropped, re-enters next
          open from a FRESH signal; hard stop later + sell-block (case 2+1)
      S3: suspension double-block 3 days -> drops accumulate, enters late
    """
    idx = pd.bdate_range("2026-01-05", periods=80)
    d = {i: str(idx[i].date()) for i in range(len(idx))}


    def frame(opens, closes):
        n = len(opens)
        return pd.DataFrame(
            {"open": opens, "high": [max(o, c) + 0.01 for o, c in zip(opens, closes)],
             "low": [min(o, c) - 0.01 for o, c in zip(opens, closes)],
             "close": closes, "volume": [1_000_000.0] * n,
             "amount": [c * 1_000_000.0 for c in closes]}, index=idx[:n])


    s1 = frame([100.0] * 64 + [91.9] * 16, [100.0] * 64 + [91.9] * 16)
    s2 = frame([50.0] * 69 + [45.9] * 11, [50.0] * 69 + [45.9] * 11)
    s3 = frame([100.0] * 68 + [91.9] * 12, [100.0] * 68 + [91.9] * 12)
    prices = {"S1": s1, "S2": s2, "S3": s3}
    t = {"id": "FIXTURE-T20", "created": "2026-01-05", "level": "INTERN",
         "params": {"entry": "low_vol_long(n=60, top_k=5, daily)",
                    "max_positions": 5, "position_size_pct": 0.10,
                    "initial_stop": -0.08, "report_num_entries": True},
         "exit_overrides": {"loss_time_days": 40}}
    # signal first fires at bar 60 (rolling-60 vol), so the first exec
    # OPEN is bar 61; stop days: S1 closes -8.1% at idx[64], S2 at
    # idx[69], S3 at idx[68]
    guard = {"buy": pd.DataFrame(True, index=idx, columns=["S1", "S2", "S3"]),
             "sell": pd.DataFrame(True, index=idx, columns=["S1", "S2", "S3"])}
    guard["sell"].at[idx[64], "S1"] = False          # S1 limit-down stop day
    guard["buy"].at[idx[61], "S2"] = False           # S2 sealed limit-up exec day
    guard["sell"].at[idx[69], "S2"] = False          # S2 limit-down stop day
    for i in (61, 62):                               # S3 suspension double-block
        guard["buy"].at[idx[i], "S3"] = False
        guard["sell"].at[idx[i], "S3"] = False
    return prices, t, guard, d[64], d[69]


def _fixture_asserts(detail: dict) -> bool:
    prices, t, guard, s1_stop, s2_stop = _fixture_panel()
    P = lp.build_panels(prices)
    control = lp.paper_run(t, prices, P)
    cg = lp.paper_run(t, prices, P, fill_guard=guard)
    ok = True

    def chk(name, cond):
        nonlocal ok
        detail[name] = bool(cond)
        ok = ok and bool(cond)

    m = cg["metrics"]
    chk("g3_buy_dropped_n", m.get("fill_guard_buy_dropped") == 3)  # S2x1 + S3x2
    chk("g3_sell_deferred_events", m.get("fill_guard_sell_deferred_events") == 2)
    chk("g3_deferred_days_total", m.get("fill_guard_deferred_days_total") == 2)
    chk("g3_first_deferred_date", m.get("fill_guard_first_deferred_date") == s1_stop)

    def first_exit(run, sym):
        tr = next(t2 for t2 in run["trades"] if t2["symbol"] == sym)
        return tr

    def bday_after(iso):
        ts = pd.Timestamp(iso) + pd.tseries.offsets.BDay(1)
        return str(ts.date())

    for sym, stop_iso in (("S1", s1_stop), ("S2", s2_stop)):
        c_tr, g_tr = first_exit(control, sym), first_exit(cg, sym)
        # case 1: deferral shifts the exit exactly one business day late
        chk(f"g3_{sym}_exit_deferred_one_bd",
            g_tr["date"] == bday_after(c_tr["date"]))
        # case 1: ORIGINAL exit reason preserved through the deferral
        chk(f"g3_{sym}_reason_preserved", g_tr["reason"] == c_tr["reason"])
        chk(f"g3_{sym}_control_stopped_at_stop_day", c_tr["date"] == stop_iso)
    # case 1: blocked-day mark-to-market visible (equity steps down at the
    # S1 stop day, position carried at the sealed close)
    eq = cg["equity"]
    i_stop = eq.index.get_indexer([pd.Timestamp(s1_stop)])[0]
    chk("g3_blocked_day_mark_visible", eq.iloc[i_stop] < eq.iloc[i_stop - 1])
    # case 2/3: S2 first entry dropped then refilled from a FRESH signal
    # (one day later) and S3 enters after the suspension window -> all
    # three positions open (entries are late, not lost)
    chk("g3_all_syms_entered", m.get("num_entries", 0) >= 3)
    s2_c, s2_g = first_exit(control, "S2"), first_exit(cg, "S2")
    # entry shift (-1 trading day) cancels the deferral shift (+1) on S2
    chk("g3_s2_hold_net_zero", s2_g["hold_days"] == s2_c["hold_days"])
    # case 4: double-run determinism
    cg2 = lp.paper_run(t, prices, P, fill_guard=guard)
    chk("g3_determinism",
        _clean(cg2["metrics"]) == _clean(cg["metrics"])
        and cg2["trades"] == cg["trades"]
        and list(cg2["equity"].values) == list(cg["equity"].values))
    # noop face: all-True guard == no guard (behavior keys, ex-additive)
    at = lp.paper_run(t, prices, P, fill_guard=_all_true_guard(P))
    chk("g3_all_true_noop",
        _clean(at["metrics"]) == _clean(control["metrics"])
        and at["trades"] == control["trades"]
        and list(at["equity"].values) == list(control["equity"].values))
    return ok


# ---------------------------------------------------------------- gates

def _g0(detail: dict) -> bool:
    r = subprocess.run([sys.executable, "-m", "smoke_test"],
                      capture_output=True, text=True, timeout=600, cwd=_REPO)
    line = next((l for l in reversed((r.stdout or "").splitlines())
                if "Summary" in l), "")
    detail["summary"] = line
    return "0 FAIL" in line and r.returncode == 0


def _g1(detail: dict, prices: dict, base: dict) -> bool:
    ok = True
    detail["anchor_ok"] = {}
    for t in _traders():
        a = lp.anchor_gate(t, prices)
        b = base["traders"][t["id"]]
        same = a["ok"] and a["got"] == b["anchor_got"] \
            and a["cutoff"] == b["anchor_cutoff"]
        detail["anchor_ok"][t["id"]] = bool(same)
        ok = ok and bool(same)
    # structural: A-rail never receives or builds a guard
    import inspect
    asrc = inspect.getsource(lp.anchor_gate)
    usrc = inspect.getsource(lp.update_trader)
    detail["anchor_source_clean"] = ("fill_guard" not in asrc
                                     and "build_guard" not in asrc)
    detail["structural"] = ("regime_mask=regime_mask" in usrc      # T-21 law
                            and "anchor_gate(t, prices_full)" in usrc  # T-21 law
                            and "fill_guard=fill_guard" in usrc)
    ok = ok and detail["anchor_source_clean"] and detail["structural"]
    return ok


def _g2(detail: dict, prices: dict, P: dict, base: dict) -> bool:
    vi_bar = lp.load_vi_bar()
    guard_true = _all_true_guard(P)
    ok = True
    for t in _traders():
        tid = t["id"]
        b = base["traders"][tid]
        dflt = lp.paper_run(t, prices, P)
        gt = lp.paper_run(t, prices, P, fill_guard=guard_true)
        x_dflt = lp.cost_x2_check(t, prices, P, vi_bar)
        x_gt = lp.cost_x2_check(t, prices, P, vi_bar, fill_guard=guard_true)
        b_run = _deser_run(b["paper_run"])
        row = {"default_run": True, "alltrue_run": True,
               "default_x2": True, "alltrue_x2": True, "monthly": True}
        # default path: byte-identical, NO additive keys present
        row["default_run"] = (dflt["metrics"] == b_run["metrics"]
                              and dflt["trades"] == b_run["trades"]
                              and list(dflt["equity"].values)
                              == list(b_run["equity"].values)
                              and not (set(dflt["metrics"]) & ADDITIVE_KEYS))
        # all-True guard: behavior-identical ex additive keys (zeros)
        row["alltrue_run"] = (_clean(gt["metrics"]) == b_run["metrics"]
                              and gt["trades"] == b_run["trades"]
                              and list(gt["equity"].values)
                              == list(b_run["equity"].values)
                              and gt["metrics"].get("fill_guard_buy_dropped") == 0
                              and gt["metrics"].get(
                                  "fill_guard_sell_deferred_events") == 0)
        row["default_x2"] = _x_clean(x_dflt) == b["cost_x2"]
        row["alltrue_x2"] = _x_clean(x_gt) == b["cost_x2"]
        agg = lp.monthly_aggregate(dflt["equity"], lp.INITIAL_CASH, t["created"])
        row["monthly"] = agg == b["monthly"]
        detail[tid] = row
        ok = ok and all(row.values())
    return ok


def _evidence_snapshot() -> dict:
    """G4 face: registered evidence blocks in firm/traders/*.json
    (level/params/backtest incl. the x2 registration seed)."""
    snap = {}
    for path in sorted(lp.TRADERS_DIR.glob("*.json")):
        if path.name.startswith("_"):
            continue
        with open(path, encoding="utf-8-sig") as fh:
            t = json.load(fh)
        snap[t["id"]] = json.dumps(
            {"level": t.get("level"), "params": t.get("params"),
             "backtest": t.get("backtest"),
             "exit_overrides": t.get("exit_overrides"),
             "created": t.get("created"),
             "evidence_cutoff": t.get("evidence_cutoff")},
            sort_keys=True, default=str)
    return snap


def _g4_g5_g6(detail: dict, pre_state: dict) -> bool:
    """G6 production cutover (post-commit first run) + G4 zero-touch +
    G5 disclosure-block presence; snapshot/verify around the production run."""
    pre_ev = _evidence_snapshot()
    pre_months = {tid: blk.get("months_tracked")
                  for tid, blk in pre_state.items()}
    r = subprocess.run([sys.executable, "-m", "live.paper"],
                       capture_output=True, text=True, timeout=900, cwd=_REPO)
    detail["prod_rc"] = r.returncode
    ok = r.returncode == 0
    # G5: disclosure blocks on the production face
    g5 = True
    post_state = {}
    for f in sorted(os.listdir(PAPER_DIR)):
        if not f.endswith("_paper.json"):
            continue
        with open(os.path.join(PAPER_DIR, f), encoding="utf-8") as fh:
            blk = json.load(fh)
        post_state[f[:-5]] = blk
        fg = blk.get("forward_guard") or {}
        want_keys = {"enabled", "guard_source", "buy_rejected_n",
                     "sell_deferred_events_n", "deferred_days_total",
                     "first_deferred_date", "window_semantics", "as_of"}
        good = (set(fg) == want_keys and fg.get("enabled") is True
                and fg.get("guard_source") == GUARD_SOURCE
                and fg.get("window_semantics") == "guarded")
        g5 = g5 and good
    detail["g5_forward_guard_blocks"] = g5
    ok = ok and g5
    # G4: registered evidence blocks byte-identical through the cutover
    g4 = _evidence_snapshot() == pre_ev
    # G4: hr.py / briefing judgment files untouched (git face, tracked only)
    r_gd = subprocess.run(["git", "status", "--porcelain",
                           "firm/hr.py", "scripts/monthly_briefing.py"],
                          capture_output=True, text=True, cwd=_REPO)
    detail["g4_judgment_files_clean"] = (r_gd.stdout or "").strip() == ""
    detail["g4_evidence_untouched"] = g4
    ok = ok and g4 and detail["g4_judgment_files_clean"]
    # G6: months_tracked semantics unchanged + x2 ledger lineage field
    g6 = all(post_state.get(tid, {}).get("months_tracked") == pre_months.get(tid)
             for tid in pre_months)
    tail_ok, n_tail = True, 0
    if os.path.exists(X2_LOG):
        with open(X2_LOG, encoding="utf-8") as fh:
            lines = [l for l in fh.read().splitlines() if l.strip()]
        for l in lines[-6:]:
            n_tail += 1
            tail_ok = tail_ok and "window_semantics" in json.loads(l)
    detail["g6_months_unchanged"] = g6
    detail["g6_x2_ledger_lineage"] = {"checked_tail": n_tail, "ok": tail_ok}
    ok = ok and g4 and g6 and tail_ok
    # G6 guard-event snapshot on the production face (prereg s5.3: ~0)
    detail["g6_guard_events"] = {
        tid: {k: (blk.get("forward_guard") or {}).get(k)
              for k in ("buy_rejected_n", "sell_deferred_events_n",
                        "deferred_days_total", "first_deferred_date")}
        for tid, blk in post_state.items()}
    return ok


def run_gates() -> int:
    print("=== T-20 PAPER_GUARD_DUAL_RAIL gates ===")
    if not os.path.exists(BASELINE_PATH):
        print("baseline absent -- run `baseline` BEFORE the wiring commit "
              "(prereg s4 G2)")
        return 2
    with open(BASELINE_PATH, encoding="utf-8") as fh:
        base = json.load(fh)
    out = {"batch": "paper_guard_dual_rail", "ticket": "T-2026-09-24-20",
           "class": "tool-validation", "ledger_trials_added": 0,
           "evidence_cutoff": FROZEN_CUTOFF, "prereg":
           "research/PAPER_GUARD_DUAL_RAIL.md", "guard_source": GUARD_SOURCE}
    prices, P = _frozen_face()
    out["frozen_face_last_bar"] = str(P["close"].index[-1].date())

    for name, fn in (("G0", _g0), ("G1", _g1), ("G2", _g2)):
        print(f"{name}...", end=" ", flush=True)
        d = {}
        ok = (fn(d, prices, base) if name in ("G1", "G2") else fn(d))
        out[name] = {"pass": ok, **d}
        print("PASS" if ok else "FAIL")

    print("G3 (synthetic forward cases)...", end=" ", flush=True)
    d3 = {}
    ok3 = _fixture_asserts(d3)
    out["G3"] = {"pass": ok3, **d3}
    print("PASS" if ok3 else "FAIL")

    print("G4+G5+G6 (production cutover run)...", end=" ", flush=True)
    pre_state = {}
    for f in sorted(os.listdir(PAPER_DIR)):
        if f.endswith("_paper.json"):
            with open(os.path.join(PAPER_DIR, f), encoding="utf-8") as fh:
                pre_state[f[:-5]] = json.load(fh)
    d456 = {}
    ok456 = _g4_g5_g6(d456, pre_state)
    out["G4"] = {"pass": d456.get("g4_evidence_untouched", False),
                 "evidence_untouched": d456.get("g4_evidence_untouched")}
    out["G5"] = {"pass": d456.get("g5_forward_guard_blocks", False),
                 "forward_guard_blocks": d456.get("g5_forward_guard_blocks")}
    out["G6"] = {"pass": bool(d456.get("g6_months_unchanged")
                              and d456.get("g6_x2_ledger_lineage", {}).get("ok")
                              and d456.get("prod_rc") == 0),
                 **{k: v for k, v in d456.items() if k != "g4_evidence_untouched"}}
    print("PASS" if ok456 else "FAIL")

    ok_all = all(v.get("pass") for k, v in out.items()
                 if isinstance(v, dict) and k.startswith("G"))
    out["verdict"] = "PASS" if ok_all else "FAIL"
    with open(OUT_PATH, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1, default=str)
    print(f"verdict: {out['verdict']}  ->  {OUT_PATH}")
    return 0 if ok_all else 1


def selftest() -> int:
    print("=== T-20 paper_guard_gates selftest (offline) ===")
    d = {}
    ok = _fixture_asserts(d)
    for k, v in d.items():
        print(f"  {k}: {'PASS' if v else 'FAIL'}")
    print("selftest:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == "baseline":
        return capture_baseline()
    if argv and argv[0] == "run":
        return run_gates()
    if argv and argv[0] == "selftest":
        return selftest()
    print("usage: paper_guard_gates.py [baseline|run|selftest]")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
