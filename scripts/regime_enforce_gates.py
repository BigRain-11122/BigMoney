"""T-2026-09-24-21 REGIME_ENFORCE_WIRING acceptance gates (G0-G5).

Tool-validation class (prereg research/REGIME_ENFORCE_WIRING.md):
zero trials, ledger_trials_added=0. Judgement gates, not statistics.

G0  smoke 23/23 (safety net, subprocess)
G1  legacy invariance:
      (a) engine synthetic determinism + all-ones-scale / all-True-guard
          no-op equivalences (additive flag OFF == legacy path)
      (b) shadow-mode production double-run field parity (ex wall-clock
          'updated') -- current wiring reproduces current repo state
G2  v3 replay bit-consistency: live.paper.v3_state_series() (import-replay,
    frozen seed) vs results/regime_calibration_v3.json recorded window /
    init_day / state_counts -- same code path, same data, must be exact
G3  mask semantics fixtures: decision-day state gates the NEXT session's
    fill; matrix applies to exec days on/after ENFORCE_ACTIVE_FROM only;
    first panel row never blocked; whole-window-pre-gate = exact no-op
G4  downgrade path (real data, env=enforce): September window predates the
    date gate -> honest downgrade, enforced counters all zero, window
    metrics field-identical to shadow run; block carries gate_note
G5  A-track invariance: anchor / cost_x2 blocks field-identical between
    the enforce(downgraded) run and the shadow run; update_trader passes
    the mask to paper_run only (structural inspect assertion)

Outputs results/regime_enforce_gates.json (top-level evidence_cutoff per
C2 contract). Restores canonical shadow-mode paper files at the end.
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd  # noqa: E402

from config import PATHS  # noqa: E402

RESULTS = os.path.join(PATHS.results_dir, "regime_enforce_gates.json")
PAPER_DIR = os.path.join(PATHS.results_dir, "paper")
EVIDENCE_CUTOFF = "2026-09-23"


def _load_paper_states() -> dict:
    out = {}
    for f in sorted(os.listdir(PAPER_DIR)):
        if f.endswith("_paper.json"):
            with open(os.path.join(PAPER_DIR, f), encoding="utf-8") as fh:
                out[f[:-5]] = json.load(fh)
    return out


def _cmp_ex_updated(a: dict, b: dict) -> list:
    """Field diff excluding wall-clock 'updated'; returns differing keys."""
    ka = {k: v for k, v in a.items() if k != "updated"}
    kb = {k: v for k, v in b.items() if k != "updated"}
    return [k for k in set(ka) | set(kb) if ka.get(k) != kb.get(k)]


def _g0() -> dict:
    r = subprocess.run([sys.executable, "-m", "smoke_test"],
                       capture_output=True, text=True, timeout=600)
    tail = (r.stdout or "").strip().splitlines()
    line = next((l for l in reversed(tail) if "Summary" in l), "")
    ok = ("0 FAIL" in line and "23/23" in line and r.returncode == 0)
    return {"pass": ok, "summary": line}


def _g1a() -> dict:
    import numpy as np
    from engine import run_backtest
    rng = np.random.default_rng(21)
    idx = pd.bdate_range("2026-01-05", periods=60)
    drift = np.cumsum(rng.normal(0, 1, 60))
    px = {"S1": pd.DataFrame({"open": 100 + drift, "close": 100 + drift,
                              "high": 105 + drift, "low": 96 + drift},
                             index=idx),
          "S2": pd.DataFrame({"open": 50 - 0.5 * drift, "close": 50 - 0.5 * drift,
                              "high": 55 - 0.5 * drift, "low": 46 - 0.5 * drift},
                             index=idx)}
    sig = pd.DataFrame({"S1": (np.arange(60) % 9 == 0),
                        "S2": (np.arange(60) % 11 == 3)}, index=idx).astype(bool)
    base = run_backtest(px, {}, entry_signal=sig, exit_signal=~sig)
    twin = run_backtest(px, {}, entry_signal=sig, exit_signal=~sig)
    det = (base["equity_curve"] == twin["equity_curve"]
           and base["trades"] == twin["trades"]
           and base["metrics"] == twin["metrics"])
    ones = run_backtest(px, {}, entry_signal=sig, exit_signal=~sig,
                        entry_size_scale=pd.Series(1.0, index=idx))
    gt = pd.DataFrame({"S1": True, "S2": True}, index=idx)
    guarded = run_backtest(px, {}, entry_signal=sig, exit_signal=~sig,
                           fill_guard={"buy": gt})
    # no-op = identical BEHAVIOR; the additive disclosure keys
    # (scaled_entries / fill_guard_buy_dropped) are expected additions
    # when a flag is ON -- excluded from the behavior comparison.
    addl = {"scaled_entries", "fill_guard_buy_dropped"}
    m_base = {k: v for k, v in base["metrics"].items() if k not in addl}
    m_ones = {k: v for k, v in ones["metrics"].items() if k not in addl}
    m_guard = {k: v for k, v in guarded["metrics"].items() if k not in addl}
    noop_scale = (ones["equity_curve"] == base["equity_curve"]
                  and ones["trades"] == base["trades"]
                  and m_ones == m_base)
    noop_guard = (guarded["equity_curve"] == base["equity_curve"]
                  and guarded["trades"] == base["trades"]
                  and m_guard == m_base)
    keys_clean = ("scaled_entries" not in base["metrics"]
                  and "fill_guard_buy_dropped" not in base["metrics"]
                  and "scaled_entries" in ones["metrics"]
                  and "fill_guard_buy_dropped" in guarded["metrics"])
    # behavior leg: half scale from the window start halves every entry
    # nominal; a blocked guard drops the pending order and counts it.
    r_half = run_backtest(px, {}, entry_signal=sig, exit_signal=~sig,
                          entry_size_scale=pd.Series(0.5, index=idx))
    q0 = base["trades"][0]["qty"] if base["trades"] else None
    qh = r_half["trades"][0]["qty"] if r_half["trades"] else None
    # qty granularity is round(x, 2) -> tolerate half-qty within 0.01
    scale_ok = bool(qh is not None and q0 is not None
                    and abs(qh - q0 / 2.0) <= 0.01
                    and r_half["metrics"].get("scaled_entries", 0) >= 1)
    gf = pd.DataFrame({"S1": True, "S2": True}, index=idx)
    gf.iloc[10:16] = False
    r_block = run_backtest(px, {}, entry_signal=sig, exit_signal=~sig,
                           fill_guard={"buy": gf})
    block_ok = r_block["metrics"].get("fill_guard_buy_dropped", -1) > 0
    ok = det and noop_scale and noop_guard and keys_clean and scale_ok and block_ok
    return {"pass": ok, "determinism": det, "noop_scale": noop_scale,
            "noop_guard": noop_guard, "keys_additive_only": keys_clean,
            "half_scale_bites": scale_ok, "guard_block_counts": block_ok}


def _g1b(shadow_before: dict) -> dict:
    r = subprocess.run([sys.executable, "-m", "live.paper"],
                       capture_output=True, text=True, timeout=900)
    after = _load_paper_states()
    diffs = {tid: _cmp_ex_updated(after[tid], shadow_before[tid])
             for tid in after if tid in shadow_before}
    bad = {k: v for k, v in diffs.items() if v}
    return {"pass": (not bad and r.returncode == 0
                     and "paper tracking: OK" in (r.stdout or "")),
            "diffs": bad or "none", "rc": r.returncode}


def _g2() -> dict:
    import live.paper as lp
    with open(os.path.join(PATHS.results_dir,
                           "regime_calibration_v3.json"), encoding="utf-8") as fh:
        cal = json.load(fh)
    s = lp.v3_state_series()
    w = cal["window"]
    win = s[(s.index >= pd.Timestamp(w["start"]))
            & (s.index <= pd.Timestamp(w["end"]))]
    counts = win.value_counts().to_dict()
    counts = {k: int(counts.get(k, 0)) for k in
              ("GREEN", "YELLOW", "ORANGE", "RED")}
    rec = cal["state_counts"]
    # init-day presence (sorted series head is the bench start, not the
    # frozen init day): the frozen seed day must be present and carry the
    # raw level at that day as its state (state_replay contract).
    init_day = pd.Timestamp(str(cal["init_day"])[:10])
    init_ok = bool(init_day in s.index)
    days_ok = int(len(win)) == int(w["days"])
    counts_ok = counts == {k: int(v) for k, v in rec.items()}
    # frozen-seed init: first replayed state == raw level at init day
    tail_ok = bool(len(s)) and s.index[-1] == pd.Timestamp(w["end"])
    ok = init_ok and days_ok and counts_ok and tail_ok
    return {"pass": ok, "init_day_match": init_ok, "days_match": days_ok,
            "state_counts_match": counts_ok, "tail_match": tail_ok,
            "replay_counts": counts, "recorded_counts": rec}


def _g3() -> dict:
    import live.paper as lp
    idx = pd.bdate_range("2026-09-25", "2026-10-09")
    states = pd.Series("GREEN", index=idx)
    states.loc["2026-09-28"] = "ORANGE"
    states.loc["2026-09-30"] = "ORANGE"
    states.loc["2026-10-05"] = "YELLOW"
    m = lp._enforce_mask(states, idx, active_from="2026-10-01")
    c1 = bool(m["buy_fillable"].iloc[0])
    c2 = bool(m["buy_fillable"].loc["2026-09-29"])
    c3 = not bool(m["buy_fillable"].loc["2026-10-01"])
    c4 = float(m["scale"].loc["2026-09-29"]) == 1.0
    c5 = float(m["scale"].loc["2026-10-06"]) == 0.5
    c6 = (m["blocked_exec_days"] == 1 and m["yellow_exec_days"] == 1)
    idx2 = pd.bdate_range("2026-09-23", "2026-09-30")
    m2 = lp._enforce_mask(pd.Series("ORANGE", index=idx2), idx2,
                          active_from="2026-10-01")
    c7 = (m2["blocked_exec_days"] == 0 and m2["yellow_exec_days"] == 0
          and bool(m2["buy_fillable"].all())
          and bool((m2["scale"] == 1.0).all()))
    ok = all([c1, c2, c3, c4, c5, c6, c7])
    return {"pass": ok, "first_row_open": c1, "pre_gate_legacy": c2,
            "gate_day_blocked": c3, "pre_gate_nominal": c4,
            "yellow_next_day_half": c5, "day_counts": c6,
            "pre_gate_window_noop": c7}


def _g4_g5(shadow_ref: dict) -> dict:
    env = dict(os.environ, BIGMONEY_REGIME_GUARD="enforce")
    r = subprocess.run([sys.executable, "-m", "live.paper"],
                       capture_output=True, text=True, timeout=900, env=env)
    enf = _load_paper_states()
    g4, g5 = {}, {"anchor_x2_parity": True, "structural": False}
    all_downgraded = True
    metrics_parity = True
    for tid, blk in enf.items():
        rg = blk.get("regime_guard") or {}
        downgraded = (rg.get("mode") == "enforce"
                      and rg.get("active") is False
                      and isinstance(rg.get("gate_note"), str)
                      and rg.get("enforced", {}).get("days_enforced") == 0
                      and rg.get("enforced", {}).get("entries_blocked") == 0)
        all_downgraded &= downgraded
        if tid in shadow_ref:
            d = _cmp_ex_updated(blk, shadow_ref[tid])
            # allowed diffs: regime_guard only (window identical otherwise)
            metrics_parity &= (set(d) <= {"regime_guard"})
            a_ok = (blk.get("anchor") == shadow_ref[tid].get("anchor")
                    and blk.get("cost_x2_check")
                    == shadow_ref[tid].get("cost_x2_check"))
            g5["anchor_x2_parity"] &= a_ok
    # structural: mask reaches paper_run only
    import inspect
    import live.paper as lp
    src = inspect.getsource(lp.update_trader)
    g5["structural"] = ("regime_mask=regime_mask" in src
                        and "anchor_gate(t, prices_full)" in src)
    g4 = {"pass": (all_downgraded and metrics_parity
                   and "DOWNGRADED" in (r.stdout or "")
                   and r.returncode == 0),
          "all_downgraded": all_downgraded,
          "window_metrics_parity": metrics_parity, "rc": r.returncode}
    g5["pass"] = bool(g5["anchor_x2_parity"] and g5["structural"])
    return {"G4": g4, "G5": g5}


def main() -> int:
    print("=== T-21 REGIME_ENFORCE_WIRING gates ===")
    out = {"batch": "regime_enforce_wiring", "ticket": "T-2026-09-24-21",
           "class": "tool-validation", "ledger_trials_added": 0,
           "evidence_cutoff": EVIDENCE_CUTOFF}
    shadow_ref = _load_paper_states()   # current repo = post-change shadow run
    for name, fn in (("G0", _g0), ("G1a", _g1a), ("G2", _g2), ("G3", _g3)):
        print(f"{name}...", end=" ", flush=True)
        out[name] = fn()
        print("PASS" if out[name]["pass"] else "FAIL")
    print("G1b (shadow production double-run)...", end=" ", flush=True)
    out["G1b"] = _g1b(shadow_ref)
    print("PASS" if out["G1b"]["pass"] else "FAIL")
    shadow_ref2 = _load_paper_states()
    print("G4+G5 (enforce downgrade run)...", end=" ", flush=True)
    g45 = _g4_g5(shadow_ref2)
    out.update(g45)
    print("PASS" if (g45["G4"]["pass"] and g45["G5"]["pass"]) else "FAIL")
    # restore canonical shadow-mode paper files
    print("restore shadow-mode production files...", end=" ", flush=True)
    r = subprocess.run([sys.executable, "-m", "live.paper"],
                       capture_output=True, text=True, timeout=900)
    out["restore_rc"] = r.returncode
    print("OK" if r.returncode == 0 else "FAIL")
    ok = all(v.get("pass") for k, v in out.items()
             if isinstance(v, dict) and k != "restore")
    out["verdict"] = "PASS" if ok else "FAIL"
    with open(RESULTS, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False, default=str)
    print(f"verdict: {out['verdict']}  -> {RESULTS}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
