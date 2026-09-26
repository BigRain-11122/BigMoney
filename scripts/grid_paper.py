"""T-78 s5c: GRID-* grid-engine paper observation accounts (unlock-4).

Wiring decision (s5c sole discretion per GRID_SLEEVE_P1.md sec.8 后续 +
CEO O-20260926-0958 "GRID accounts paper-wired"): the FULL 5-cell live
family (510300/159915/512880/518880/511010) wires as experimental
observation accounts. The s5b batch verdict is an honest 0/5 science
FAIL with ZERO promotion candidates -- the CEO order wires paper
REGARDLESS (AGGR-MOM revival precedent), honesty carried per account by
frozen batch labels loaded from results/grid_sleeve_p1.json (single
truth source, zero hand-copied numbers).

Marks paradigm = AGGR slice-2 (aggressive_lab.py cmd_paper): deterministic
full-window engine replay per advancing bar; daily returns accrued from
the first bar STRICTLY AFTER the frozen judgment-domain evidence_cutoff
(2026-09-24) at INITIAL_CNY 1,000,000; idempotent no-op when the panel
cutoff is already marked. Lane = results/grid_paper/ (PROS-* whitelist
paradigm: NOT consumed by t35 paper_export / daily_scorecard CEO faces).
Marks are not trials -> trials ledger +0, SEED_REGISTRY +0.

Forward fund-event guard (r239 law family, honest freeze): a live cell
flagged by guard_event_days on a day AFTER evidence_cutoff freezes its
account TERMINALLY -- marks truncate strictly before the first forward
event day (no fake-event marks accrue), disclosure carries the event
dates, and the frozen state file stays byte-stable.

Usage: python scripts/grid_paper.py run | selftest
Products: results/grid_paper/GRID-<code>_paper.json (5 accounts)
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd

from config import PATHS
from engine.grid_sleeve import (_selftest as engine_selftest,
                                guard_event_days, run_grid_sleeve)

TICKET = "T-2026-09-26-78"
BATCH_JSON = os.path.join("results", "grid_sleeve_p1.json")
PAPER_DIR = os.path.join(PATHS.results_dir, "grid_paper")
LIVE = ("510300", "159915", "512880", "518880", "511010")
GUARD_LIMITS = {"510300": 0.105, "159915": 0.205, "512880": 0.105,
                "518880": 0.105, "511010": 0.105}
UNI_THRESH = 0.03                 # r239 calm-universe threshold (frozen)
GRID_KW = {"n_grids": 10, "band_win": 250, "nav0": 1_000_000.0}
COST_BP_X1 = 13.0                 # V1 legacy (batch x1 face, smoke-verified)
INITIAL_CNY = 1_000_000.0         # AGGR paper precedent


def _sha16(obj) -> str:
    import hashlib
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, default=str)
        .encode("utf-8")).hexdigest()[:16]


def _state_path(code: str) -> str:
    return os.path.join(PAPER_DIR, f"GRID-{code}_paper.json")


def _load_instrument(code: str, cutoff: pd.Timestamp):
    """data/daily single-instrument OHLCV at cutoff (s5b loader mirror)."""
    df = pd.read_csv(os.path.join(PATHS.daily_dir, f"{code}.csv"),
                     parse_dates=["date"]).set_index("date").sort_index()
    df = df[df.index <= cutoff]
    for col in ("open", "close"):
        if col not in df.columns or df[col].isna().any():
            raise ValueError(f"{code}: {col} face missing/NaN")
    if len(df) < GRID_KW["band_win"] + 2:
        raise ValueError(f"{code}: {len(df)} bars < band_win+2")
    return df


def load_batch_faces():
    """Frozen s5b batch = the single truth source for evidence_cutoff and
    per-cell honest labels (fail-closed: missing/void batch = exit 2)."""
    with open(BATCH_JSON, encoding="utf-8") as fh:
        b = json.load(fh)
    if b.get("void") or not b.get("evidence_cutoff"):
        raise ValueError("batch product void / no evidence_cutoff")
    labels, codes = {}, set()
    for c in b.get("candidates", []):
        code = c["code"]
        codes.add(code)
        nul = b["null_summary"]["by_code"][code]
        labels[code] = {
            "batch_sharpe_full": round(c["sharpe_full"], 4),
            "g1_prime_v2": {
                "pass": c["g1_pass"],
                "line": c["g1_prime_v2"]["skill_line"]["line"],
                "line_ok": c["g1_prime_v2"]["line_ok"],
                "ci_lower_bound_positive":
                    c["g1_prime_v2"]["ci_lower_bound_positive"],
            },
            "gate_a_chop_specialist": c["gate_a"],
            "chop_face": c["chop_face"],
            "null_face": {
                "mu": nul["mu"], "max": nul["max"],
                "cell_beats_null_max": nul["cell_beats_null_max"],
            },
            "x2_stress": {
                "sharpe": round(c["x2_stress"]["sharpe"], 4),
                "x2_flip_negative": bool(
                    c["sharpe_full"] > 0.0 and c["x2_stress"]["sharpe"] < 0.0),
            },
            "descriptive": {
                "trend_up_opportunity_gap":
                    c["descriptive"]["trend_up_opportunity_gap"],
                "trend_down_whipsaw_cost":
                    c["descriptive"]["trend_down_whipsaw_cost"],
            },
            "promotion_candidate": c["paper_candidate"],
        }
    if codes != set(LIVE):
        raise ValueError(f"batch live cells {sorted(codes)} != frozen "
                         f"{sorted(LIVE)}")
    verdict = {
        "science_survivors": b.get("survivors_science", []),
        "paper_candidates": b.get("paper_candidates", []),
        "prereg_sha256_16": b.get("prereg_sha256_16"),
        "note": ("s5b frozen verdict: honest negative -- observation "
                 "wiring per CEO O-20260926-0958 regardless, labels "
                 "above"),
    }
    return b["evidence_cutoff"], labels, verdict


# ---------------- marks helpers (AGGR slice-2 mirror, pure) ----------------

def accrue_marks(rets: pd.Series, cutoff_ts: pd.Timestamp,
                 initial: float):
    """Deterministic daily accrual over bars STRICTLY AFTER cutoff_ts
    (judgment-domain bar excluded; AGGR _accrue_marks mirror). Internal
    equity unrounded; outputs round for display only (r163 law)."""
    seg = rets[rets.index > cutoff_ts]
    eq, marks = initial, []
    for d, r in seg.items():
        eq *= 1.0 + float(r)
        marks.append({"date": str(pd.Timestamp(d).date()),
                      "daily_ret": round(float(r), 8),
                      "equity_cny": round(eq, 2)})
    return marks, eq


def marks_dd(marks: list, initial: float) -> float:
    """Peak-to-trough dd over the marked equity path (initial included)."""
    peak, eq, dd = initial, initial, 0.0
    for m in marks:
        eq = m["equity_cny"]
        peak = max(peak, eq)
        dd = min(dd, eq / peak - 1.0)
    return round(dd, 6)


def truncate_marks(marks: list, first_event_date: str):
    """Forward fund-event freeze: drop marks ON/after the first forward
    event day (fake-event marks must not accrue; r239 law family)."""
    out = [m for m in marks if m["date"] < first_event_date]
    return out


def needs_recompute(state: dict | None, panel_cutoff: str) -> bool:
    """Idempotency predicate: missing state / stale panel_cutoff /
    not-yet-frozen -> recompute; marked-through or terminally frozen
    -> no-op."""
    if state is None:
        return True
    if state.get("forward_fund_event", {}).get("frozen"):
        return False                      # terminal freeze, byte-stable
    return state.get("panel_cutoff") != panel_cutoff


# ------------------------------ the lane ----------------------------------

def run() -> int:
    t0 = time.time()
    try:
        ev_cutoff, labels, verdict = load_batch_faces()
        cutoff_ts = pd.Timestamp(ev_cutoff)

        raw_end = {}
        for code in LIVE:
            df = pd.read_csv(os.path.join(PATHS.daily_dir, f"{code}.csv"),
                             parse_dates=["date"]).set_index("date")
            raw_end[code] = str(df.index[-1].date())
        panel_cutoff = min(raw_end.values())
        ps = pd.Timestamp(panel_cutoff)
        if ps <= cutoff_ts:
            print(f"grid paper: no markable bar yet (panel cutoff "
                  f"{panel_cutoff} <= evidence_cutoff {ev_cutoff}) -- no-op")
            return 0

        stale = []
        for code in LIVE:
            sp = _state_path(code)
            state = None
            if os.path.exists(sp):
                with open(sp, encoding="utf-8-sig") as fh:
                    state = json.load(fh)
            if needs_recompute(state, panel_cutoff):
                stale.append(code)
        if not stale:
            print(f"grid paper: marks already at panel cutoff "
                  f"{panel_cutoff} -- no-op (idempotent)")
            return 0

        # calm-universe reference for the forward fund-event guard
        # (s5b runner face mirror: core48 close panel median |r1|)
        from live.paper import build_panels, load_core
        core_close = build_panels(load_core())["close"]
        uni_med = core_close.pct_change().abs().median(axis=1)

        os.makedirs(PAPER_DIR, exist_ok=True)
        n_runs, written = 0, []
        for code in stale:
            df = _load_instrument(code, ps)
            r = run_grid_sleeve(df["open"], df["close"], df.index,
                               cost_bp=COST_BP_X1, **GRID_KW)
            n_runs += 1
            rets = r["nav"].pct_change().dropna()
            marks, eq = accrue_marks(rets, cutoff_ts, INITIAL_CNY)

            ev_days = [str(d.date()) for d in guard_event_days(
                df["close"], GUARD_LIMITS[code], uni_med, UNI_THRESH)
                if pd.Timestamp(d) > cutoff_ts]
            ffe = {"frozen": bool(ev_days), "event_days": ev_days,
                   "law": "r239 fund-event guard, forward face "
                          "(GRID_SLEEVE_P1 sec.2 guard, applied to "
                          "post-cutoff bars)"}
            if ev_days:
                marks = truncate_marks(marks, min(ev_days))
                eq = (marks[-1]["equity_cny"] if marks else INITIAL_CNY)
                ffe["frozen_note"] = (
                    "terminal freeze: forward fund event detected "
                    f"{ev_days[0]} -- marks truncated strictly before the "
                    "event day, account stops accruing (no fake-event "
                    "marks)")
            ms = {
                "bars": len(marks),
                "first_date": marks[0]["date"] if marks else None,
                "last_date": marks[-1]["date"] if marks else None,
                "cumulative_ret": round(eq / INITIAL_CNY - 1.0, 8),
                "current_dd": marks_dd(marks, INITIAL_CNY),
            }
            lab = labels[code]
            st = {
                "schema": "grid_paper_v1",
                "account": f"GRID-{code}",
                "instrument": code,
                "lane": "experimental-grid (T-78 s5c, ticket "
                        f"{TICKET}, order O-20260926-0958 unlock-4)",
                "whitelist_paradigm": "PROS-* precedent: own lane dir; "
                    "excluded from t35 paper_export and daily_scorecard "
                    "CEO faces by construction",
                "guard": "shadow (record-only; zero interference; zero "
                         "canon/production-account touch)",
                "experimental": True,
                "initial_cash_cny": INITIAL_CNY,
                "denomination": "CNY",
                "paper_start_rationale": "first bar strictly after the "
                    f"frozen judgment-domain evidence_cutoff "
                    f"{ev_cutoff} (blind forward; GRID_SLEEVE_P1 sec.4/8 "
                    "+ CEO O-0958 wiring order)",
                "evidence_cutoff": ev_cutoff,
                "machinery": {
                    "engine": "engine/grid_sleeve.py v1 (additive "
                              "independent module, house backtester "
                              "zero-touch)",
                    "params": dict(GRID_KW, cost_bp=COST_BP_X1),
                    "params_sha16": _sha16(
                        dict(GRID_KW, cost_bp=COST_BP_X1)),
                },
                "batch_honest_labels": lab,
                "batch_verdict": verdict,
                "risk_budget": {
                    "position_cap": 1.0,
                    "position_cap_note": "structural grid face: n_grids x "
                        "unit_cash = NAV_0 fully deployed at band bottom "
                        "(engine v1 design); declared budget parameter, "
                        "not a modeled cap",
                    "cash_parking_leg": "intrinsic to machinery: "
                        "between-grids idle cash + band-eject full-cash "
                        "leg inside the engine",
                    "experimental": True,
                    "execution_layer_note": "marks are the deterministic "
                        "machinery-replay measurement; budget fields are "
                        "declared parameters, not modeled in marks",
                },
                "cost_face": "x1 (V1 legacy 13bp production-aligned; batch "
                    "x2 stress face disclosed in labels -- "
                    + ("cell x2 FLIPS NEGATIVE: cost-sensitive "
                       "observation" if lab["x2_stress"]["x2_flip_negative"]
                       else "x2 degrades but stays same-sign"),
                "forward_fund_event": ffe,
                "marks": marks,
                "marks_summary": ms,
                "equity_cny": round(eq, 2),
                "panel_cutoff": panel_cutoff,
                "updated": time.strftime("%Y-%m-%d %H:%M:%S"),
                "audit": {"network": "zero", "ledger_trials_added": 0,
                          "seed_registry_added": 0,
                          "engine_runs": 1,
                          "adoption": "ZERO (observation lane)"},
            }
            tmp = _state_path(code) + ".tmp"
            with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
                json.dump(st, fh, ensure_ascii=False, indent=1)
            os.replace(tmp, _state_path(code))
            written.append(st["account"])
            print(f"grid paper {st['account']}: bars={ms['bars']} "
                  f"last={ms['last_date']} cum={ms['cumulative_ret']} "
                  f"dd={ms['current_dd']} equity={st['equity_cny']}"
                  + (" [FROZEN: forward fund event]" if ffe["frozen"]
                     else ""))
        print(f"grid paper: {len(written)}/{len(stale)} accounts marked "
              f"through {panel_cutoff} -> {PAPER_DIR} "
              f"({round(time.time() - t0, 1)}s, {n_runs} engine runs)")
        return 0
    except SystemExit as e:
        print(f"grid paper mechanism fault (gate): {e}")
        return 2
    except Exception as e:                       # noqa: BLE001
        print(f"grid paper mechanism fault: {e}")
        return 2


# ------------------------------ selftest -----------------------------------

def selftest() -> int:
    ok_all = True

    def ok(name, cond):
        nonlocal ok_all
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
        ok_all &= bool(cond)
        return cond

    # [1/6] engine machinery selftest (production form, mirror law)
    ok("engine grid_sleeve 8/8 (production engine)", engine_selftest())

    # [2/6] marks accrual math: unrounded compounding + r163 display round
    idx = pd.bdate_range("2026-09-24", periods=4)
    rets = pd.Series([0.01, -0.02, 0.03], index=idx[1:])
    marks, eq = accrue_marks(rets, pd.Timestamp("2026-09-24"),
                             1_000_000.0)
    want_eq = 1_000_000.0 * 1.01 * 0.98 * 1.03
    ok("marks: compounded equity + rounded display (r163 law)",
       len(marks) == 3
       and marks[0]["equity_cny"] == round(1_000_000.0 * 1.01, 2)
       and abs(marks[-1]["equity_cny"] - round(want_eq, 2)) < 0.01
       and marks[-1]["daily_ret"] == 0.03)

    # [3/6] paper-start boundary: judgment-domain bar strictly excluded
    idx2 = pd.bdate_range("2026-09-23", periods=3)   # 09-23,24,25
    r2 = pd.Series([0.05, 0.01, 0.02], index=idx2)
    m2, _ = accrue_marks(r2, pd.Timestamp("2026-09-24"), 100.0)
    ok("boundary: bar ON evidence_cutoff excluded, first mark after",
       [m["date"] for m in m2] == ["2026-09-25"]
       and m2[0]["daily_ret"] == 0.02)

    # [4/6] dd formula: peak-to-trough incl. initial point; honest 0.0
    m3 = [{"date": "2026-09-25", "daily_ret": 0.01, "equity_cny": 1010.0},
          {"date": "2026-09-26", "daily_ret": -0.05,
           "equity_cny": 959.5},
          {"date": "2026-09-27", "daily_ret": 0.02,
           "equity_cny": 978.69}]
    ok("dd: peak 1010 -> trough 959.5 = -0.05; no marks = 0.0",
       abs(marks_dd(m3, 1000.0) - (959.5 / 1010.0 - 1.0)) < 1e-6
       and marks_dd([], 1000.0) == 0.0)

    # [5/6] forward freeze: truncation strictly before event; terminal
    #       predicate; stale/idempotency faces
    mk = [{"date": "2026-09-25", "daily_ret": 0.01, "equity_cny": 1010.0},
          {"date": "2026-09-28", "daily_ret": -0.6, "equity_cny": 404.0},
          {"date": "2026-09-29", "daily_ret": 0.61, "equity_cny": 650.44}]
    tk = truncate_marks(mk, "2026-09-28")
    ok("freeze: marks drop ON/after first forward event day",
       [m["date"] for m in tk] == ["2026-09-25"])
    st_frozen = {"panel_cutoff": "2026-09-28",
                 "forward_fund_event": {"frozen": True}}
    st_fresh = {"panel_cutoff": "2026-09-29"}
    ok("recompute predicate: missing->True, stale->True, "
       "marked-through->False, frozen->False",
       needs_recompute(None, "2026-09-29") is True
       and needs_recompute({"panel_cutoff": "2026-09-28"},
                           "2026-09-29") is True
       and needs_recompute(st_fresh, "2026-09-29") is False
       and needs_recompute(st_frozen, "2026-09-29") is False)

    # [6/6] frozen batch label face: single truth source loadable, 5/5
    #       cells, honest s5b verdict intact (fail-closed on tamper)
    try:
        ev, labels, verdict = load_batch_faces()
        lab_ok = (ev == "2026-09-24" and set(labels) == set(LIVE)
                  and verdict["science_survivors"] == []
                  and verdict["paper_candidates"] == []
                  and all(not v["g1_prime_v2"]["pass"]
                          and not v["promotion_candidate"]
                          and "batch_sharpe_full" in v
                          for v in labels.values())
                  and {c for c, v in labels.items()
                       if v["x2_stress"]["x2_flip_negative"]}
                  == {"510300", "511010"})
    except Exception as ex:                          # noqa: BLE001
        print(f"    (load_batch_faces fault: {ex})")
        lab_ok = False
    ok("batch labels: evidence_cutoff + 5/5 honest faces + 0/5 verdict "
       "load intact (no hand-copied numbers)", lab_ok)

    if not ok_all:
        print("SELFTEST FAILED")
        return 2
    print("selftest: ALL LEGS PASS")
    return 0


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "selftest":
        return selftest()
    if mode == "run":
        return run()
    # fail-closed argv (r232 law): unknown/missing arg -> usage, exit 2,
    # NEVER a silent production path
    print(f"usage: {sys.argv[0]} [run|selftest] (got {mode!r})")
    return 2


if __name__ == "__main__":
    sys.exit(main())
