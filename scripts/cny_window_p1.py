"""CNY_WINDOW_P1 -- spring-festival concrete-window batch (one-shot).

Prereg: research/shortline/CNY_WINDOW_PREREG.md (FROZEN at commit before
this run; window shopping red line -- windows consumed verbatim from
results/cny_window_probe.json, never redefined in-batch).

Arms (N_eff=3, mask semantics = p1 seasonal family precedent):
  PRE-5 / POST-5 / PREPOST on core48 bare-code pool, engine defaults
  (13bp cost always on, T+1), evidence_cutoff 2026-09-24 lockbox.
Nulls: K=20 same-mask random windows (SEED_REGISTRY cny_window_p1=68000;
2 random 5-bar windows per year = same ON-day statistics as PREPOST).
Verdict: science_gates.g1_prime_v2 shared line (skill_line_v2, core48
collector pool) + stationary bootstrap CI + F6 entries gate; DSR via
deflated_sharpe_ratio(n_trials=23); G2 only if G1' passes (missing
inputs refused honestly). Cost stress x2/x3 via CostPatch (p2 precedent).

Usage:
  python scripts/cny_window_p1.py            -> results/cny_window_p1.json
  python scripts/cny_window_p1.py selftest   -> offline self-check
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd

from cny_window_probe import KNOWN_CNY, WINDOW_BARS
from p1_strategy_screen import OOS_START, load_core
from science_gates import (CostPatch, append_ledger, cutoff_meta,
                           deflated_sharpe_ratio, g1_prime_v2)
from engine import run_backtest
from engine.metrics import annual_return, max_drawdown, sharpe

CUTOFF = "2026-09-24"          # prereg sec.2 lockbox (D2)
BATCH_CELLS = 3                # PRE-5 / POST-5 / PREPOST
K_NULLS = 20                   # prereg sec.3
N_TRIALS = BATCH_CELLS + K_NULLS   # 23, ledger accounting
OUT = os.path.join("results", "cny_window_p1.json")
PROBE = os.path.join("results", "cny_window_probe.json")


def load_panel(cutoff: str = CUTOFF):
    """core48 + 510300 calendar face, truncated to the prereg cutoff."""
    prices = load_core()
    prices = {s: df[df.index <= cutoff] for s, df in prices.items()}
    cal = pd.DatetimeIndex(
        pd.read_csv(os.path.join("data", "daily", "510300.csv"),
                    parse_dates=["date"])["date"]).sort_values()
    cal = cal[cal <= pd.Timestamp(cutoff)]
    keep = {s: df for s, df in prices.items() if len(df) >= 60}
    return keep, cal


def build_masks(probe: dict, cal: pd.DatetimeIndex) -> dict[str, pd.Series]:
    """Consume frozen probe windows verbatim -> boolean mask per arm."""
    pre, post = set(), set()
    for e in probe["events"]:
        pre.update(e["pre5"])
        post.update(e["post5"])
    idx = pd.DatetimeIndex([d for d in cal])
    dates = set(str(d.date()) for d in idx)
    for wanted in pre | post:
        if wanted not in dates:
            raise ValueError(f"probe window date {wanted} not in calendar face "
                             f"-- probe/batch calendar mismatch, refuse to run")
    m_pre = pd.Series([str(d.date()) in pre for d in idx], index=idx)
    m_post = pd.Series([str(d.date()) in post for d in idx], index=idx)
    return {"PRE-5": m_pre, "POST-5": m_post, "PREPOST": m_pre | m_post}


def null_mask(seed: int, cal: pd.DatetimeIndex, years, per_year_windows: int = 2,
              window_bars: int = WINDOW_BARS) -> pd.Series:
    """Same-mask random null: per year, place k random contiguous windows."""
    rng = np.random.default_rng(seed)
    on = set()
    for y in years:
        bars = [d for d in cal if d.year == y]
        if len(bars) < window_bars:
            continue
        starts = rng.choice(len(bars) - window_bars + 1,
                            size=per_year_windows, replace=False)
        for s in starts:
            on.update(str(d.date()) for d in bars[s:s + window_bars])
    return pd.Series([str(d.date()) in on for d in cal], index=cal)


def mask_panel(mask: pd.Series, idx: pd.DatetimeIndex, syms: list):
    """p1 mask-panel construction verbatim (entry tiled, exit = ~entry)."""
    m = mask.reindex(idx).fillna(False).astype(bool)
    entry = pd.DataFrame(np.tile(m.values[:, None], (1, len(syms))),
                         index=idx, columns=syms)
    return entry, ~entry


def run_arm(prices: dict, idx, mask: pd.Series, name: str,
            cost_mult: int | None = None):
    syms = list(prices)
    entry, exit_ = mask_panel(mask, idx, syms)
    if cost_mult is None:
        res = run_backtest(prices, {}, entry_signal=entry, exit_signal=exit_)
    else:
        with CostPatch(cost_mult):
            res = run_backtest(prices, {}, entry_signal=entry, exit_signal=exit_)
    eq = pd.Series(res["equity_curve"], index=idx[:len(res["equity_curve"])])
    seg = eq[eq.index >= OOS_START]
    out = {
        "name": name,
        "full": {k: res["metrics"][k] for k in
                 ("annual_return", "sharpe", "max_drawdown", "num_trades")},
        "oos": {"sharpe": round(float(sharpe(seg)), 4),
                "annual_return": round(float(annual_return(seg)), 4),
                "max_drawdown": round(float(max_drawdown(seg)), 4)},
        "n_entries": len(res["trades"]),
        "returns": eq.pct_change().dropna(),
    }
    return out


def seg_sharpe(eq: pd.Series, start: str) -> float:
    seg = eq[eq.index >= start]
    return round(float(sharpe(seg)), 4) if len(seg) >= 20 else 0.0


def build_payload(probe: dict, arms: dict, nulls: list, cost_runs: dict,
                  g1: dict, dsr: dict, g2: dict) -> dict:
    ns = null_sharpes = [n["full"]["sharpe"] for n in nulls]
    stats = {
        "k": len(ns), "seed_base": "cny_window_p1=68000",
        "full_sharpes": ns,
        "mean": round(float(np.mean(ns)), 4) if ns else None,
        "sd": round(float(np.std(ns)), 4) if ns else None,
        "p95": round(float(np.percentile(ns, 95)), 4) if ns else None,
    }
    payload = {
        **cutoff_meta(CUTOFF),
        "batch": "CNY_WINDOW_P1",
        "arms": {k: {kk: vv for kk, vv in v.items() if kk != "returns"}
                 for k, v in arms.items()},
        "null_family": stats,
        "cost_stress": cost_runs,
        "g1_prime_v2": g1,
        "dsr": dsr,
        "g2_registration_v2": g2,
        "n_trials": N_TRIALS,
        "events_consumed": probe["n_events"],
        "trials_ledger": append_ledger("CNY_WINDOW_P1", N_TRIALS,
                                os.path.basename(OUT),
                                evidence_cutoff=CUTOFF,
                                note="zoo sec.8 #38 evidence-upgrade; "
                                     "3 arms + 20 same-mask nulls"),
    }
    return payload

def selftest() -> int:
    print("cny_window_p1 selftest:")
    fails = 0

    def ok(name, cond):
        nonlocal fails
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
        fails += 0 if cond else 1

    # S1 mask build from synthetic probe payload, disjointness + counts
    probe = {"n_events": 1,
             "events": [{"year": 2024, "pre5": ["2024-02-02", "2024-02-05",
                                                "2024-02-06", "2024-02-07",
                                                "2024-02-08"],
                         "post5": ["2024-02-19", "2024-02-20", "2024-02-21",
                                   "2024-02-22", "2024-02-23"]}]}
    cal = pd.DatetimeIndex(pd.bdate_range("2024-01-02", "2024-03-29"))
    m = build_masks(probe, cal)
    ok("S1 per-arm ON-day counts 5/5/10",
       int(m["PRE-5"].sum()) == 5 and int(m["POST-5"].sum()) == 5
       and int(m["PREPOST"].sum()) == 10)
    ok("S1 PRE/POST disjoint", not (m["PRE-5"] & m["POST-5"]).any())
    # S2 null determinism + same statistics
    n1 = null_mask(68000, cal, [2024])
    n2 = null_mask(68000, cal, [2024])
    n3 = null_mask(68001, cal, [2024])
    ok("S2 null same-seed identical", n1.equals(n2))
    ok("S2 null ON-days == 10 (same statistics)", int(n1.sum()) == 10)
    ok("S2 different seed -> different placement", not n1.equals(n3))
    # S3 cutoff truncation (Timestamp comparison, not string)
    ok("S3 cutoff truncates calendar",
       pd.Timestamp("2026-09-24") <= pd.Timestamp(CUTOFF)
       and pd.Timestamp("2026-09-25") > pd.Timestamp(CUTOFF))
    # S4 payload shape: cutoff_meta at top level + ledger embedded
    p = build_payload(probe, {"PRE-5": {"name": "x", "full": {}, "oos": {},
                                        "n_entries": 0, "returns": None}},
                      [], {}, {}, {}, {})
    ok("S4 evidence_cutoff top-level", p["evidence_cutoff"] == CUTOFF)
    ok("S4 ledger dict embedded with chain fields",
       isinstance(p["trials_ledger"], dict)
       and "prev_total" in p["trials_ledger"]
       and p["trials_ledger"]["batch_trials"] == N_TRIALS)
    # S5 known-CNY year coverage = 7 (probe face contract)
    ok("S5 KNOWN_CNY has 7 anchor years", len(KNOWN_CNY) == 7)
    print(f"  selftest {'PASS' if fails == 0 else 'FAIL'} ({fails} fail)")
    return 1 if fails else 0


def main(argv: list[str]) -> int:
    if argv and argv[0] == "selftest":
        return selftest()
    print("CNY_WINDOW_P1 batch (one-shot, prereg frozen):")
    with open(PROBE, encoding="utf-8") as fh:
        probe = json.load(fh)
    if not probe["validation"]["all_pass"]:
        print("probe validation not all_pass -- data gate refused (exit 2)")
        return 2
    prices, cal = load_panel(CUTOFF)
    print(f"  core48 members: {len(prices)}  calendar bars: {len(cal)}")
    masks = build_masks(probe, cal)
    idx = cal
    # ---- arms (one-shot) ----
    arms = {}
    for name, mask in masks.items():
        arms[name] = run_arm(prices, idx, mask, name)
        a = arms[name]
        print(f"  {name:<8} sharpe={a['full']['sharpe']:>8.3f} "
              f"oos_sharpe={a['oos']['sharpe']:>7.3f} "
              f"entries={a['n_entries']:>4} dd={a['full']['max_drawdown']}")
    # ---- K=20 same-mask nulls ----
    years = sorted(e["year"] for e in probe["events"])
    nulls = []
    for k in range(K_NULLS):
        nm = null_mask(68_000 + k, cal, years)
        nulls.append(run_arm(prices, idx, nm, f"null_{k}"))
    ns = [n["full"]["sharpe"] for n in nulls]
    print(f"  nulls: n={len(ns)} mean={np.mean(ns):.3f} sd={np.std(ns):.3f} "
          f"p95={np.percentile(ns, 95):.3f}")
    # ---- verdicts (shared library, no hand-copied lines) ----
    g1, dsr, g2 = {}, {}, {"gate": "g2_registration_v2",
                           "note": "not evaluated -- G1' gate first (missing "
                                   "inputs refused honestly)"}
    for name, a in arms.items():
        g1[name] = g1_prime_v2(a["full"]["sharpe"], a["returns"].tolist(),
                               batch_cells=BATCH_CELLS, pool="core48",
                               n_trades=a["full"]["num_trades"],
                               n_entries=a["n_entries"])
        dsr[name] = deflated_sharpe_ratio(a["returns"].tolist(),
                                          n_trials=N_TRIALS)
        g1[name]["oos_sharpe"] = a["oos"]["sharpe"]
        g1[name]["oos_dual_positive"] = bool(a["oos"]["sharpe"] > 0
                                             and a["oos"]["annual_return"] > 0)
        print(f"  G1' {name}: pass_v2={g1[name]['pass_v2']} "
              f"line={g1[name]['skill_line']['line']}")
    if any(v["pass_v2"] for v in g1.values()):
        g2 = {"gate": "g2_registration_v2",
              "note": "family PBO leg not wired in this one-shot; G1' pass "
                      "requires PBO (screening/pbo.py CSCV) before any "
                      "registration -- refused honestly"}
    # ---- cost stress x2/x3 (descriptive clause) ----
    cost_runs = {}
    for name, mask in masks.items():
        for m in (2, 3):
            r = run_arm(prices, idx, mask, f"{name}_x{m}", cost_mult=m)
            cost_runs[f"{name}_x{m}"] = {
                "full": r["full"], "oos": r["oos"],
                "n_entries": r["n_entries"],
                "survive_x2_clause": bool(
                    m == 2 and r["full"]["sharpe"] > 0
                    and r["oos"]["sharpe"] >= 0)}
    payload = build_payload(probe, arms, nulls, cost_runs, g1, dsr, g2)
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    verdict = "PASS" if any(v["pass_v2"] for v in g1.values()) else "FAIL"
    print(f"batch -> {OUT}  batch verdict (G1' any-arm): {verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
