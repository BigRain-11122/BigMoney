# -*- coding: utf-8 -*-
"""CTA_P1 paper-trial harness (O-20261007-2215 deliverable (2)-bm-c, bar-gated).

Purpose: forward paper-trial observation lane for the CTA_P1 trend line
(vol_target_tsmom_60 @daily, the best cell of the frozen judgment batch
research/CTA_P1.md SS7: Sharpe 0.7408 vs skill_line_v2 1.1463, G1' v2
0/16 honest loss) released into a paper trial by GM signature per
O-20261007-2215 (bull-market offense gap, CEO direction order). This is
NOT a G2 registration and NOT a judgment batch: science ledger +0,
SEED_REGISTRY +0, marks are observation-only.

Bar gate (O-2215 no-blind-wiring law): the harness refuses to produce
marks before the first reopen bar exists. Panel cutoff < paper_start
(2026-10-08 reopen) => honest no-op exit 0. First wiring + first marks
verification happen at the first-bar round (r703 ack face).

Construction: VERBATIM imports from the frozen batch carrier -- no
re-implementation. Signal + weights from scripts/cta_p1_screen.py
(sig_vol_target_tsmom, build_weights, daily regime), engine semantics from
engine/futures_runner.py (run/load_panel). ETF engine untouched
(O-2250 additive-iron). Universe pinned to the frozen CTA_P1 nine
varieties (TS belongs to the CTA_WAVE1 lane, added to FUT_META after the
CTA_P1 freeze -- importing VARIETIES live would silently widen the
universe, so the nine are pinned here).

Account: CTA-P1, experimental account #28 (first slot beyond the
27-account experimental pool, number registered at wiring per O-2215).
Lane: results/cta_paper/ (PROS-* whitelist paradigm -- own directory, by
construction NOT consumed by t35/paper_export/scorecard/daily_report CEO
faces). Shadow guard: record-only, zero interference, zero canon touch,
live.paper registration face untouched (separate lane).

Sizing: initial 10,000,000 CNY = batch-parity (results/shortline_cta_p1.json
meta: 10M keeps whole-lot granularity from dominating small margin shares,
so marks are comparable with the judged construction).

Determinism: full-window recompute on every accrual; same panel bytes =>
same marks bytes (double-run bit-exact assert embedded in selftest and in
run). Wall-clock appears only in the envelope "updated" field.

Disclosures carried in the state file (honest-history law): V0 roll-gap
caveat (main-continuous raw prices, roll jumps marked as-is), AU-gold-beta
suspicion (batch SS7 mechanism 3: trend alpha was ~AU beta on the judgment
window -- forward observation is the test), margin semantics (batch
margin_usage_max ~= 1.0 = embedded 7-10x leverage profile marked honestly),
exit axis = signal-following weights (no engine default exit stack in
futures_runner), REGIME-5 bull-state promotion face pending bm-a judge
(O-2215 ss1; not wired yet).

Subcommands:
  run       bar-gated marks accrual (no-op before first bar; idempotent after)
  status    read-only state summary
  selftest  offline unit tests (synthetic panel; no data files needed)
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd

from engine import futures_runner as fr
from cta_p1_screen import sig_vol_target_tsmom, build_weights  # frozen batch carrier (verbatim)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANE_DIR = os.path.join(ROOT, "results", "cta_paper")
STATE_PATH = os.path.join(LANE_DIR, "CTA-P1_paper.json")

SCHEMA = "cta_p1_paper_v1"
ACCOUNT = "CTA-P1"
SLOT_NOTE = ("experimental account #28: first slot beyond the 27-account "
             "experimental pool, number registered at wiring per "
             "O-20261007-2215 ss4")
INITIAL_CNY = 10_000_000.0        # batch-parity sizing (disclosed above)
WINDOW_START = "2017-01-17"       # CTA_P1 frozen window start (panel warmup)
PAPER_START = pd.Timestamp("2026-10-08")   # reopen day, first trial bar
COST_MULT = 1.0                   # x1 production-aligned per-lot fee + 1 tick
# Frozen CTA_P1 nine-variety universe, pinned (TS = CTA_WAVE1 lane, excluded).
NINE = ["IF", "IC", "IH", "IM", "T", "TF", "RB", "AU", "SC"]


def _panel_cutoff() -> pd.Timestamp:
    last = None
    for v in NINE:
        path = os.path.join(fr.FUT_DIR, f"{v}.csv")
        if not os.path.exists(path):
            raise FileNotFoundError(f"futures csv missing: {path}")
        df = pd.read_csv(path, index_col=0, parse_dates=True).sort_index()
        t = df.index[-1]
        last = t if last is None else max(last, t)
    return last


def _load_state() -> dict | None:
    if not os.path.exists(STATE_PATH):
        return None
    with open(STATE_PATH, encoding="utf-8-sig") as fh:
        return json.load(fh)


def _accrue_marks(equity: pd.Series, paper_start: pd.Timestamp,
                  initial: float) -> list[dict]:
    """Marks = compounded daily returns of the standing system from the
    first bar >= paper_start (AGGR accrual paradigm). Daily ret on the
    first mark date is vs the previous trading day -- positions carry
    across the boundary because the signal is a standing construction."""
    rets = equity.pct_change()
    tail = rets[rets.index >= paper_start]
    marks = []
    eq = initial
    for d, r in tail.items():
        if not np.isfinite(r):
            continue
        eq = eq * (1.0 + float(r))
        marks.append({"date": str(d.date()),
                      "daily_ret": round(float(r), 8),
                      "equity_cny": round(eq, 2)})
    return marks


def cmd_status() -> int:
    st = _load_state()
    if st is None:
        print(f"cta paper: no state file yet (wiring pending first bar "
              f">= {PAPER_START.date()})")
        return 0
    ms = st.get("marks_summary", {})
    print(f"cta paper: account={st.get('account')} panel_cutoff="
          f"{st.get('panel_cutoff')} marks={ms.get('n_marks')} "
          f"equity_cny={st.get('equity_cny')} status={st.get('status')}")
    return 0


def cmd_run() -> int:
    # bar gate: no marks before the reopen bar exists (no-blind-wiring law)
    cutoff = _panel_cutoff()
    if cutoff < PAPER_START:
        print(f"cta paper: no markable bar yet (panel cutoff "
              f"{cutoff.date()} < paper_start {PAPER_START.date()}) -- no-op")
        return 0

    prev = _load_state()
    if prev is not None and prev.get("panel_cutoff") == str(cutoff.date()):
        print(f"cta paper: marks already at panel cutoff "
              f"{cutoff.date()} -- no-op (idempotent)")
        return 0

    # full-window deterministic recompute, frozen construction verbatim
    panel = fr.load_panel(WINDOW_START, str(cutoff.date()), varieties=NINE)
    state = sig_vol_target_tsmom(panel["close"], 60)
    weights = build_weights(state, panel["close"], None)
    r1 = fr.run(panel, weights, start_cash=INITIAL_CNY, cost_mult=COST_MULT)
    r2 = fr.run(panel, weights, start_cash=INITIAL_CNY, cost_mult=COST_MULT)
    if not np.array_equal(r1.equity.to_numpy(), r2.equity.to_numpy()) \
            or r1.trades != r2.trades:
        print("cta paper: determinism check FAILED (double-run differ)")
        return 2

    marks = _accrue_marks(r1.equity, PAPER_START, INITIAL_CNY)
    if not marks:
        print(f"cta paper: no accruable bar >= {PAPER_START.date()} -- no-op")
        return 0
    total_ret = marks[-1]["equity_cny"] / INITIAL_CNY - 1.0

    os.makedirs(LANE_DIR, exist_ok=True)
    out = {
        "schema": SCHEMA,
        "account": ACCOUNT,
        "slot_registration": SLOT_NOTE,
        "lane": "cta-p1 paper trial (O-20261007-2215 deliverable (2)-bm-c, "
                "engineering lane bm-c)",
        "whitelist_paradigm": "PROS-* precedent: own lane dir; excluded "
            "from t35 paper_export, daily_scorecard and CEO faces by "
            "construction",
        "guard": "shadow (record-only; zero interference; zero canon / "
                 "production-account touch; live.paper registration face "
                 "untouched - separate lane)",
        "experimental": True,
        "initial_cash_cny": INITIAL_CNY,
        "denomination": "CNY",
        "sizing_rationale": "batch-parity with results/shortline_cta_p1.json "
            "meta (10M keeps whole-lot granularity from dominating small "
            "margin shares; marks comparable with the judged construction)",
        "paper_start": str(PAPER_START.date()),
        "paper_start_rationale": "O-20261007-2215: GM-signed release into "
            "paper trial wired at the 10-08 reopen (first-bar round per "
            "r703 ack); zero hindsight backfill - marks begin at the first "
            "reopen bar",
        "evidence_cutoff_judgment_domain": "2026-09-23",
        "construction": {
            "signal": "vol_target_tsmom_60 @daily regime (frozen CTA_P1 "
                      "SS3 construction)",
            "carrier": "scripts/cta_p1_screen.py sig_vol_target_tsmom + "
                       "build_weights (verbatim import, zero "
                       "re-implementation)",
            "engine": "engine/futures_runner.py run/load_panel (O-2250: "
                      "ETF engine untouched)",
            "universe": NINE,
            "universe_note": "frozen CTA_P1 nine varieties pinned; TS "
                             "(CTA_WAVE1 lane, post-freeze FUT_META "
                             "addition) excluded",
            "execution": "T signal -> T+1 open; T+0 two-way; per-lot fee "
                         "+ 1 tick slippage x1; per-variety margin cap "
                         "0.20; limit-touch blocks new exposure",
            "exit_axis": "signal-following weights (futures_runner has no "
                         "engine default exit stack; positions follow the "
                         "frozen construction)",
            "cost_face": "x1 (production-aligned)",
        },
        "honest_history": {
            "g1_verdict": "CTA_P1 batch G1' v2 0/16 honest loss (frozen "
                          "research/CTA_P1.md SS7): best cell = this "
                          "construction, Sharpe 0.7408 vs skill_line_v2 "
                          "1.1463; zero G2 registration, ledger +0",
            "release_basis": "GM signature O-20261007-2215 ss2 (P1 face, "
                             "bull-market offense gap): paper trial "
                             "observation, NOT a registration; science "
                             "gates not lowered and not re-claimed",
            "v0_rollgap_caveat": "main-continuous V0 raw prices, roll-gap "
                                 "jumps marked as-is (symmetric with the "
                                 "judgment batch; G2 roll-smoothing debt "
                                 "clause not triggered - no registration)",
            "au_beta_suspicion": "batch SS7 mechanism 3: trend alpha ~= AU "
                                 "gold beta on the judgment window "
                                 "(AU leg +121.5M of +116.7M commodity "
                                 "pnl); forward observation is the test",
            "margin_profile": "batch margin_usage_max ~= 1.0 = embedded "
                              "7-10x leverage; paper marks carry this "
                              "risk profile honestly (deep-drawdown "
                              "capable)",
            "regime_promotion_pending": "O-2215 ss1: weight promotion when "
                                        "REGIME-5 judges bull state - "
                                        "pending bm-a REGIME-5 judge "
                                        "(<=10-14); not wired in this lane",
        },
        "risk_budget": {
            "per_variety_margin_cap": 0.20,
            "global_margin_budget": 1.0,
            "experimental": True,
        },
        "marks": marks,
        "marks_summary": {
            "n_marks": len(marks),
            "first_mark": marks[0]["date"],
            "last_mark": marks[-1]["date"],
            "total_ret": round(total_ret, 8),
        },
        "equity_cny": marks[-1]["equity_cny"],
        "panel_cutoff": str(cutoff.date()),
        "status": "trial-live",
        "audit": {
            "determinism": "double-run bit-exact (equity + trades), "
                           "checked in-run",
            "recompute": "full-window deterministic recompute per accrual",
            "ledger": "science_gates +0 (observation lane, not a batch)",
        },
        "updated": pd.Timestamp.now().strftime("%Y-%m-%dT%H:%M:%S%z"),
    }
    tmp = STATE_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=True, indent=1)
    os.replace(tmp, STATE_PATH)
    print(f"cta paper: {ACCOUNT} marks accrued to {cutoff.date()} "
          f"({len(marks)} bar(s), equity {out['equity_cny']:,} CNY, "
          f"total_ret {total_ret:+.6f})")
    return 0


def _synthetic_panel() -> dict:
    dates = pd.bdate_range("2026-09-01", periods=40)
    rng = np.random.default_rng(20261008)
    base = pd.DataFrame(
        {"AU": 780.0 + np.cumsum(rng.normal(0, 2.0, 40)),
         "RB": 3500.0 + np.cumsum(rng.normal(0, 15.0, 40)),
         "T": 105.0 + np.cumsum(rng.normal(0, 0.2, 40))},
        index=dates)
    panel = {"dates": dates}
    for fld in ("open", "high", "low", "volume"):
        panel[fld] = base * (1.0 + rng.normal(0, 0.002, base.shape)) \
            if fld != "volume" \
            else pd.DataFrame(np.full(base.shape, 1000.0), index=dates,
                              columns=base.columns)
    panel["close"] = base
    return panel


def cmd_selftest() -> int:
    fails = []

    def check(name, cond):
        print(f"[{'PASS' if cond else 'FAIL'}] {name}")
        if not cond:
            fails.append(name)

    # 1) universe pin: nine varieties, TS excluded (post-freeze FUT_META
    #    addition must not silently widen the trial universe)
    check("universe pin = frozen nine, TS excluded",
          len(NINE) == 9 and "TS" not in NINE
          and set(NINE) == {"IF", "IC", "IH", "IM", "T", "TF", "RB", "AU", "SC"})

    # 2) signal unit: vol_target formula = direction x min(1, 0.01/realized)
    close = pd.DataFrame(
        {"A": list(np.linspace(100.0, 110.0, 80)) + list(np.linspace(110.0, 90.0, 20))},
        index=pd.bdate_range("2026-01-01", periods=100))
    sig = sig_vol_target_tsmom(close, 60)
    realized = close.pct_change().rolling(60).std()
    expect_dir = np.sign(close / close.shift(60) - 1.0)
    expect_mult = (0.01 / realized).clip(upper=1.0)
    tail_ok = np.allclose(sig.iloc[65:].to_numpy(),
                          (expect_dir * expect_mult).iloc[65:].to_numpy(),
                          equal_nan=True)
    check("vol_target signal formula (direction x vol multiplier)", tail_ok)
    warmup_nan = bool(sig.iloc[:60].to_numpy().flatten()[
        ~np.isnan(sig.iloc[:60].to_numpy().flatten())].size == 0)
    check("signal warmup 60d = flat/NaN", warmup_nan)

    # 3) weights: daily regime => NaN flattened, row sums = |state|/n_alive
    panel = _synthetic_panel()
    state = sig_vol_target_tsmom(panel["close"], 20)
    w = build_weights(state, panel["close"], None)
    check("build_weights daily regime zero-fills NaN (no carry gap)",
          not np.isnan(w.to_numpy()).any())
    n_alive = panel["close"].notna().sum(axis=1)
    exp = state.div(n_alive, axis=0).fillna(0.0)
    check("build_weights row math = state/n_alive",
          np.allclose(w.to_numpy(), exp.to_numpy(), equal_nan=True))

    # 4) engine determinism: same panel+weights double-run bit-exact
    r1 = fr.run(panel, w, start_cash=1_000_000.0)
    r2 = fr.run(panel, w, start_cash=1_000_000.0)
    check("futures_runner double-run equity bit-exact",
          np.array_equal(r1.equity.to_numpy(), r2.equity.to_numpy()))
    check("futures_runner double-run trades bit-exact", r1.trades == r2.trades)

    # 5) marks accrual unit: known rets compound from initial (series has a
    #    pre-start bar so the paper_start-day return is defined, as in
    #    production where the panel history anchors the first trial day)
    eq = pd.Series([100.0, 101.0, 100.9, 101.9, 102.9, 103.9],
                   index=pd.bdate_range("2026-10-07", periods=6))
    marks = _accrue_marks(eq, pd.Timestamp("2026-10-08"), 10_000_000.0)
    expect_first = 10_000_000.0 * (1.0 + 0.01)
    check("accrue: first mark = paper_start day ret off initial",
          abs(marks[0]["equity_cny"] - expect_first) < 0.01
          and marks[0]["date"] == "2026-10-08"
          and abs(marks[0]["daily_ret"] - 0.01) < 1e-12)
    check("accrue: n_marks = bars >= paper_start (pre-start bar excluded)",
          len(marks) == 5)
    comp = 10_000_000.0
    for m in marks:
        comp *= (1.0 + m["daily_ret"])
    check("accrue: compounding identity equity_cny == prod(1+r)*initial",
          abs(comp - marks[-1]["equity_cny"]) < 0.5)

    # 6) bar gate: pre-start cutoff must yield zero marks (no-op face)
    early = _accrue_marks(eq, pd.Timestamp("2026-10-15"), 1_000.0)
    check("bar gate: accrue after paper_start only (empty before)",
          early == [])

    # 7) state schema fields present on a synthetic write round-trip
    st = {"schema": SCHEMA, "account": ACCOUNT,
          "panel_cutoff": "2026-10-08", "status": "trial-live"}
    check("state schema constants pinned",
          st["schema"] == "cta_p1_paper_v1" and st["account"] == "CTA-P1")

    print(f"selftest: {'ALL PASS' if not fails else 'FAIL ' + str(fails)}")
    return 0 if not fails else 2


def main() -> int:
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "run":
        return cmd_run()
    if cmd == "status":
        return cmd_status()
    if cmd == "selftest":
        return cmd_selftest()
    print("usage: cta_p1_paper.py run|status|selftest")
    return 1


if __name__ == "__main__":
    sys.exit(main())
