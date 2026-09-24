"""T-24 slice (a): PROSPECT per-member paper tracking lane (prospect-levels).

Ticket T-2026-09-24-24 remaining slice (a): per-member PROSPECT paper
tracking display -- a lane SEPARATE from live.paper.PAPER_LEVELS, so the
registered 6 composition stays byte-identical by construction (this
script never reads or writes results/paper/ and never enters the
registered paper loop).

Reuse map (zero new engine code):
  anchor replay    = p3_portfolio.member_run (base + cost_mult=2.0) x
                     t24_prospect_onboard._compare vs t["prospect"]
                     recorded_* fields (R84 recorded-cell replay gate,
                     ledger_trials_added=0 precedent)
  paper window     = live.paper.paper_run (T-20 fill_guard wired fresh
                     per run; T-21 regime_mask mirrors live.paper.main's
                     3-gate logic -- shadow default, date-gated enforce)
  monthly evidence = live.paper.monthly_aggregate (registered shape:
                     months_tracked / monthly_returns / current_dd)

Honesty contract (registered update_trader verbatim): anchor FAIL =
member file UNTOUCHED, drift disclosed, exit 2.

Usage (detached BelowNormal per O-1612 full-load pool):
  python scripts/t24_prospect_paper.py run       # all PROSPECT members
  python scripts/t24_prospect_paper.py status    # last summary + cells
  python scripts/t24_prospect_paper.py selftest   # offline gates
Exit contract: 0 = all members anchor-PASS (tracking written);
2 = any drift/FAIL or mechanism error (honest, never masked).
"""
import argparse
import copy
import json
import os
import sys
import tempfile
import time

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # p3 imports

from config import PATHS

PROSPECT_LEVELS = ("PROSPECT",)   # T-24 slice (a): observation lane --
# deliberately NOT added to live.paper.PAPER_LEVELS (composition-free).
OUT_DIR = os.path.join(PATHS.results_dir, "prospect_paper")
SUMMARY_PATH = os.path.join(OUT_DIR, "_summary.json")
CELLS_PATH = os.path.join(PATHS.results_dir, "t24_prospect_paper_cells.jsonl")
TICKET = "T-2026-09-24-24"


def _load_prospects(traders_dir) -> list:
    out = []
    for f in sorted(os.listdir(traders_dir)):
        if not f.endswith(".json") or f.startswith("_"):
            continue
        with open(os.path.join(traders_dir, f), encoding="utf-8") as fh:
            t = json.load(fh)
        if t.get("level") in PROSPECT_LEVELS:
            out.append(t)
    return out


def _save_member(t: dict, traders_dir) -> None:
    """hr.save_trader verbatim, parameterized for selftest isolation."""
    with open(os.path.join(traders_dir, f"{t['id']}.json"), "w",
              encoding="utf-8") as fh:
        json.dump(t, fh, indent=2, ensure_ascii=False)


def _done_ids(cells_path: str, cutoff: str) -> set:
    """Checkpoint resume (t22 convention): members already anchor-PASSed
    at the SAME data cutoff are skipped on re-invocation; new data cutoff
    re-runs everyone (anchor must re-verify every fresh data state)."""
    done = set()
    if not os.path.exists(cells_path):
        return done
    with open(cells_path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                c = json.loads(line)
            except json.JSONDecodeError:
                continue   # corrupt tail tolerated
            if c.get("cutoff") == cutoff and c.get("pass"):
                done.add(c["id"])
    return done


def _append_cell(cells_path: str, rec: dict):
    with open(cells_path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def _update_member(t: dict, prices_full: dict, P: dict, data_cutoff: str,
                   regime_mask, fill_guard, rg: dict,
                   member_run, _compare, lp) -> dict:
    """Pure compute for ONE PROSPECT member (no member-file IO here; the
    caller writes only on anchor pass). Never mutates t on drift."""
    r1 = member_run(t, prices_full)
    r2 = member_run(t, prices_full, cost_mult=2.0)
    verdict = _compare(r1, r2, t["prospect"])
    state = {"trader": t["id"], "anchor_ok": bool(verdict["pass"]),
             "anchor": verdict, "evidence_cutoff": r1["cutoff"],
             "cutoff": data_cutoff,
             "updated": time.strftime("%Y-%m-%d %H:%M:%S")}
    if not verdict["pass"]:
        return state   # drift: member JSON untouched (registered contract)
    run = lp.paper_run(t, prices_full, P, regime_mask=regime_mask,
                       fill_guard=fill_guard)
    agg = lp.monthly_aggregate(run["equity"], lp.INITIAL_CASH, t["created"])
    m = run["metrics"] or {}
    state.update({
        "paper_start": t["created"], "bars": agg["bars"],
        "months_tracked": agg["months_tracked"],
        "monthly_returns": agg["monthly_returns"],
        "current_dd": agg["current_dd"], "months_detail": agg["months_detail"],
        "window_metrics": run["metrics"],
        "recorded_evidence": {k: t["prospect"][k] for k in (
            "recorded_full_sharpe", "recorded_oos_sharpe",
            "recorded_x2_full_sharpe", "recorded_n_trades",
            "recorded_oos_trades", "recorded_max_dd")},
        "regime_guard": rg,
        "forward_guard": {
            "enabled": fill_guard is not None,
            "guard_source": lp.GUARD_SOURCE_LABEL
            if fill_guard is not None else None,
            "buy_rejected_n": int(m.get("fill_guard_buy_dropped", 0) or 0),
            "sell_deferred_events_n":
                int(m.get("fill_guard_sell_deferred_events", 0) or 0),
            "window_semantics": "guarded" if fill_guard is not None
                                else "legacy",
        },
        "allocation_pct": 0,   # observation tier: allocation permanently 0
        "no_future_data": "closed bars only; signal T close -> T+1 open "
                          "(engine contract)",
    })
    # same member-file paper shape the registered update_trader writes
    state["member_paper"] = {
        "months_tracked": agg["months_tracked"],
        "monthly_returns": agg["monthly_returns"],
        "current_dd": agg["current_dd"],
        "as_of": time.strftime("%Y-%m-%d"),
        "cutoff": data_cutoff,
    }
    return state


def _run_lane(members: list, prices_full: dict, traders_dir, out_dir: str,
              cells_path: str, rg: dict, regime_mask, fill_guard,
              member_run, _compare, lp) -> tuple:
    """Process every PROSPECT member; write per-member JSONs + summary.
    Returns (summary_dict, rc)."""
    os.makedirs(out_dir, exist_ok=True)
    P = lp.build_panels(prices_full)
    data_cutoff = str(P["close"].index[-1].date())
    done = _done_ids(cells_path, data_cutoff)
    n_pass = n_drift = n_skip = 0
    months_total = 0
    engine_runs = 0
    drift_ids = []
    for t in members:
        if t["id"] in done:
            n_skip += 1
            months_total += (t.get("paper") or {}).get("months_tracked", 0)
            n_pass += 1   # already verified at this cutoff (checkpoint)
            continue
        try:
            st = _update_member(t, prices_full, P, data_cutoff,
                                regime_mask, fill_guard, rg,
                                member_run, _compare, lp)
        except Exception as exc:   # mechanism error: honest, never masked
            st = {"trader": t["id"], "anchor_ok": False,
                  "error": f"{type(exc).__name__}: {exc}"}
        engine_runs += 2   # base + x2 anchor replays (gates, not trials)
        _append_cell(cells_path, {"id": t["id"], "cutoff": data_cutoff,
                                  "pass": bool(st.get("anchor_ok")),
                                  "ts": time.strftime(
                                      "%Y-%m-%d %H:%M:%S")})
        if not st.get("anchor_ok"):
            n_drift += 1
            drift_ids.append(t["id"])
            print(f"{t['id']}: ANCHOR DRIFT -- member JSON untouched"
                  + (f" ({st.get('error')})" if st.get("error")
                     else f" checks: {st['anchor'].get('checks')}"))
            continue
        t["paper"] = st.pop("member_paper")
        _save_member(t, traders_dir)
        sp = os.path.join(out_dir, f"{t['id']}.json")
        with open(sp, "w", encoding="utf-8") as fh:
            json.dump(st, fh, indent=2, ensure_ascii=False, default=str)
        if (st.get("bars") or 0) > 0:
            engine_runs += 1   # non-empty paper window ran the engine
        n_pass += 1
        months_total += st["months_tracked"]
        print(f"{t['id']}: prospect anchor OK (cutoff {st['evidence_cutoff']})"
              f" | paper {st['bars']} bars since {st['paper_start']} | "
              f"months_tracked={st['months_tracked']} "
              f"dd={st['current_dd']} | saved {sp}")
    summary = {
        "batch": "t24-prospect-paper-tracking",
        "ticket": TICKET,
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "data_cutoff": data_cutoff,
        "n_members": len(members), "n_pass": n_pass, "n_drift": n_drift,
        "n_checkpoint_skip": n_skip, "drift_ids": drift_ids,
        "months_total": months_total,
        "lane": "PROSPECT_LEVELS separate from PAPER_LEVELS "
                "(composition-free; results/paper/ never touched)",
        "regime_guard_mode": rg.get("mode"),
        "window_semantics": "guarded" if fill_guard is not None else "legacy",
        "audit": {
            "ledger_trials_added": 0,
            "engine_runs": engine_runs,
            "note": "anchor replays = reproducibility gates (R84 "
                    "recorded-cell replay precedent, p4 cells already "
                    "counted in source-batch ledgers); paper window runs "
                    "= tracking state, not trials",
        },
        "verdict": "PROSPECT observation tracking written for the "
                   "anchor-PASS set; drift members untouched + exit 2",
    }
    with open(os.path.join(out_dir, "_summary.json"), "w",
              encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, ensure_ascii=False)
    print(f"prospect tracking: {'OK' if n_drift == 0 else 'DRIFT'} "
          f"pass={n_pass}/{len(members)} drift={n_drift} "
          f"months_total={months_total} cutoff={data_cutoff}")
    return summary, (2 if n_drift else 0)


def _lane_context(lp, prices_full: dict):
    """Mirror live.paper.main's regime-guard + fill-guard wiring (T-05
    shadow default / T-21 enforce 3-gate / T-20 B-rail fresh build)."""
    rg = lp.regime_guard_context()
    regime_mask = None
    if rg.get("mode") == "enforce":
        af = pd.Timestamp(lp.ENFORCE_ACTIVE_FROM)
        last_bar = max(df.index[-1] for df in prices_full.values())
        if last_bar < af:
            rg = dict(rg, active=False,
                      enforced={"active_from": lp.ENFORCE_ACTIVE_FROM,
                                "days_enforced": 0, "entries_blocked": 0,
                                "entries_halved": 0},
                      gate_note=f"date gate not yet open "
                                f"(active_from={lp.ENFORCE_ACTIVE_FROM}) "
                                "-- downgrade to shadow semantics")
            print(f"prospect lane: enforce requested, DOWNGRADED to shadow "
                  f"semantics (date gate {lp.ENFORCE_ACTIVE_FROM})")
        else:
            v3 = lp.v3_state_series()
            P_idx = lp.build_panels(prices_full)["close"].index
            regime_mask = lp._enforce_mask(v3, P_idx)
            print(f"prospect lane: regime_guard ENFORCE active from "
                  f"{lp.ENFORCE_ACTIVE_FROM}")
    from scripts.t14_rules_fidelity import build_guard   # lazy: t14
    # imports live.paper (keep import order live.paper -> t14)
    fill_guard, gdiag = build_guard(prices_full)
    print(f"prospect lane: forward_guard {lp.GUARD_SOURCE_LABEL} wired "
          f"(up={gdiag['totals']['buy_blocked']} "
          f"dn={gdiag['totals']['sell_blocked']})")
    return rg, regime_mask, fill_guard


def cmd_run() -> int:
    try:
        import psutil
        pri = getattr(psutil, "BELOW_NORMAL_PRIORITY_CLASS", None)
        if pri is not None:
            psutil.Process().nice(pri)   # O-1136 full-load low-priority pool
    except Exception:
        pass
    import live.paper as lp
    from p3_portfolio import member_run
    from t24_prospect_onboard import _compare
    from firm.hr import TRADERS_DIR
    prices_full = lp.load_core()
    rg, regime_mask, fill_guard = _lane_context(lp, prices_full)
    members = _load_prospects(TRADERS_DIR)
    if not members:
        print("prospect lane: 0 PROSPECT members (no-op, rc 0)")
        return 0
    summary, rc = _run_lane(members, prices_full, TRADERS_DIR, OUT_DIR,
                            CELLS_PATH, rg, regime_mask, fill_guard,
                            member_run, _compare, lp)
    return rc


def cmd_status() -> int:
    if os.path.exists(SUMMARY_PATH):
        with open(SUMMARY_PATH, encoding="utf-8") as fh:
            s = json.load(fh)
        print(json.dumps({k: s[k] for k in ("generated", "data_cutoff",
                                            "n_members", "n_pass", "n_drift",
                                            "months_total",
                                            "window_semantics")},
                         ensure_ascii=False))
    else:
        print("no summary yet (lane never ran)")
    return 0


def _fixture_prices(n=700):
    import numpy as np
    import pandas as pd
    rng = np.random.default_rng(20260924)
    idx = pd.bdate_range("2022-09-01", periods=n)
    close = pd.DataFrame(
        {"AAA": 1 + np.cumsum(rng.normal(0.0003, 0.012, n)),
         "BBB": 1 + np.cumsum(rng.normal(-0.0001, 0.015, n))},
        index=idx)
    high = close * (1 + np.abs(rng.normal(0, 0.006, (n, 2))))
    low = close * (1 - np.abs(rng.normal(0, 0.006, (n, 2))))
    open_ = close.shift(1).fillna(1.0)
    vol = pd.DataFrame(rng.lognormal(12, .4, (n, 2)), index=idx,
                       columns=close.columns)
    prices = {}
    for s in close.columns:
        prices[s] = pd.DataFrame(
            {"open": open_[s], "high": high[s], "low": low[s],
             "close": close[s], "volume": vol[s],
             "amount": vol[s] * close[s]}).dropna()
    return prices


def cmd_selftest() -> int:
    import live.paper as lp
    from p3_portfolio import member_run
    from t24_prospect_onboard import _compare
    from firm.hr import ALLOCATION
    ok = True

    # S1: composition-free invariants (PAPER_LEVELS untouched + alloc 0)
    s1 = ("PROSPECT" not in lp.PAPER_LEVELS
          and lp.PAPER_LEVELS == ("INTERN", "TRAINEE")
          and PROSPECT_LEVELS == ("PROSPECT",)
          and ALLOCATION["PROSPECT"] == 0)
    print(f"S1 composition-free invariants: "
          f"{'PASS' if s1 else 'FAIL'} "
          f"(PAPER_LEVELS={lp.PAPER_LEVELS})")
    ok &= s1

    with tempfile.TemporaryDirectory() as td:
        prices = _fixture_prices()
        last = list(prices.values())[0].index[-1]
        created = str((last - pd.Timedelta(days=90)).date())
        ec = str(last.date())

        def _member(created_, ec_):
            return {"id": "PROS-ZZTEST-01", "name": "fixture",
                    "level": "PROSPECT", "created": created_,
                    "evidence_cutoff": ec_,
                    "params": {"entry": "doji_at_low()"},
                    "prospect": {}, "paper": {"months_tracked": 0,
                                              "monthly_returns": [],
                                              "current_dd": 0.0}}

        # S2: self-consistent recorded evidence -> anchor PASS + tracking
        t = _member(created, ec)
        r1 = member_run(t, prices)
        r2 = member_run(t, prices, cost_mult=2.0)
        t["prospect"] = {
            "recorded_full_sharpe": r1["full"]["sharpe"],
            "recorded_oos_sharpe": r1["oos"]["sharpe"],
            "recorded_x2_full_sharpe": r2["full"]["sharpe"],
            "recorded_n_trades": r1["n_trades"],
            "recorded_oos_trades": r1["oos_trades"],
            "recorded_max_dd": r1["full"]["max_drawdown"],
        }
        P = lp.build_panels(prices)
        dc = str(P["close"].index[-1].date())
        st = _update_member(t, prices, P, dc, None, None,
                            {"mode": "shadow", "state": "ORANGE"},
                            member_run, _compare, lp)
        s2 = (st["anchor_ok"] and st["bars"] > 0
              and st["member_paper"]["months_tracked"] >= 1
              and st["allocation_pct"] == 0
              and t["paper"]["months_tracked"] == 0)   # t NOT mutated here
        print(f"S2 pass-path compute: {'PASS' if s2 else 'FAIL'} "
              f"(anchor={st['anchor_ok']} bars={st['bars']} "
              f"months={st['months_tracked']})")
        ok &= s2

        # S3: drift contract -- corrupted recorded evidence -> anchor FAIL
        # and the member dict stays untouched (no paper write path)
        t3 = _member(created, ec)
        t3["prospect"] = dict(t["prospect"],
                              recorded_full_sharpe=(
                                  t["prospect"]["recorded_full_sharpe"]
                                  + 0.5))
        before = json.dumps(t3, sort_keys=True)
        st3 = _update_member(t3, prices, P, dc, None, None,
                             {"mode": "shadow"}, member_run, _compare, lp)
        s3 = (not st3["anchor_ok"] and "member_paper" not in st3
              and before == json.dumps(t3, sort_keys=True))
        print(f"S3 drift-untouched: {'PASS' if s3 else 'FAIL'} "
              f"(checks={st3['anchor'].get('checks')})")
        ok &= s3

        # S4: zero-bar window honesty (created after last bar)
        t4 = _member(str((last + pd.Timedelta(days=3)).date()), ec)
        t4["prospect"] = dict(t["prospect"])
        st4 = _update_member(t4, prices, P, dc, None, None,
                             {"mode": "shadow"}, member_run, _compare, lp)
        s4 = (st4["anchor_ok"] and st4["bars"] == 0
              and st4["months_tracked"] == 0
              and st4["current_dd"] == 0.0
              and st4["monthly_returns"] == [])
        print(f"S4 zero-bar honesty: {'PASS' if s4 else 'FAIL'} "
              f"(bars={st4['bars']} months={st4['months_tracked']})")
        ok &= s4

        # S5: lane run end-to-end on tempdir -- checkpoint + summary + rc
        tA = copy.deepcopy(t)
        tB = copy.deepcopy(t3)   # one drifting member
        tB["id"] = "PROS-ZZTEST-02"
        cells = os.path.join(td, "cells.jsonl")
        summ, rc = _run_lane([tA, tB], prices, td, os.path.join(td, "out"),
                             cells, {"mode": "shadow"}, None, None,
                             member_run, _compare, lp)
        s5 = (summ["n_members"] == 2 and summ["n_pass"] == 1
              and summ["n_drift"] == 1 and rc == 2
              and os.path.exists(os.path.join(td, "PROS-ZZTEST-01.json"))
              and not os.path.exists(os.path.join(td, "PROS-ZZTEST-02.json"))
              and summ["months_total"] == st["months_tracked"]
              and summ["audit"]["ledger_trials_added"] == 0)
        # checkpoint resume: same cutoff -> pass members skipped
        summ2, rc2 = _run_lane([tA, tB], prices, td,
                               os.path.join(td, "out"), cells,
                               {"mode": "shadow"}, None, None,
                               member_run, _compare, lp)
        s5 &= (summ2["n_checkpoint_skip"] == 1 and rc2 == 2)
        print(f"S5 lane end-to-end + checkpoint: "
              f"{'PASS' if s5 else 'FAIL'} (rc={rc}/{rc2} "
              f"skip={summ2['n_checkpoint_skip']})")
        ok &= s5

    print(f"selftest: {'ALL PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", choices=["run", "status", "selftest"])
    args = ap.parse_args()
    return {"run": cmd_run, "status": cmd_status,
            "selftest": cmd_selftest}[args.cmd]()


if __name__ == "__main__":
    sys.exit(main())
