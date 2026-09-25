"""OPTIONS_WAVE2 batch runner — 波-2 期权备兑族 pilot批: 18 candidates + 50
nulls + 2 passives (70 cells).

Prereg: research/OPTIONS_WAVE2_PREREG.md (frozen R191, git-blob LF sha256
a6998921371ef4f867a448dd07f047e9288fdd47254f6c8a61fda4444396d0e6;
integrity asserted at run). Domain: SSE ETF option retention-window panel
(510050 + 510300, 200 contracts, s0 census results/options_s0_panel_probe.json
+ data/options/), evidence_cutoff 2026-09-24. Retention-window data debt is
a frozen disclosure (s3 retention_boundary): sina codes face keeps only
recent expiry months; this is the backfill pilot, wave-2b forward collector
is the definitive-batch path.

Cells (prereg §0/§3):
  covered_call / protective_put / cash_secured_put  x  m {3,5,10}%  x
  {weekly judgement regime, monthly descriptive regime}  -> 18
  + K=50 random nulls (seed SEED_REGISTRY options_wave2 = 63_000 + k,
    weekly 3-state {CC,PP,off} + m draw, both underlyings synchronized)
  + 2 passives (buy_hold_510050 / buy_hold_510300)      -> 70

Subcommands:
  gates    G0 smoke / G1 engine selftest / G2 exchange-verified constants
           (frozen evidence file) / G3 panel completeness (prereg §2 five
           conditions + hard-bound distribution face) / G4 determinism
  run      full batch (gates re-run inside; aborts exit 2 on any FAIL)
  selftest offline unit tests (synthetic panels; no data files needed)

Ledger: science_gates.append_ledger("options_wave2", 70,
          "results/options_wave2.json", evidence_cutoff="2026-09-24").
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "screening"))

import numpy as np
import pandas as pd

from engine import options_runner as opr
import science_gates as sg

PREREG_PATH = os.path.join(ROOT, "research", "OPTIONS_WAVE2_PREREG.md")
RESULTS_JSON = os.path.join(ROOT, "results", "options_wave2.json")
RESULTS_CSV = os.path.join(ROOT, "research", "options_wave2_results.csv")
ATTRITION_JSON = os.path.join(ROOT, "results", "gate_attrition.json")
CONTRACTS_JSON = os.path.join(ROOT, "data", "options", "contracts.json")
G2_EVIDENCE_PATH = os.path.join(ROOT, "results", "options_wave2_g2_check.json")

CUTOFF = "2026-09-24"          # evidence_cutoff (09-25 Mid-Autumn, no bar)
FROZEN_PREREG_SHA = "a6998921371ef4f867a448dd07f047e9288fdd47254f6c8a61fda4444396d0e6"
SEED_BASE = 63_000             # SEED_REGISTRY["options_wave2"] (frozen R191)
K_NULLS = 50
BATCH_CELLS = 70               # 18 candidates + 50 nulls + 2 passives
START_CASH = 1_000_000.0       # per cell (prereg §3)
SPAN_DEGRADE_MIN = 90          # prereg §2 span-adaptive clause
CRISIS_R1 = 0.50                # hard-bound max face (三件套(b) crisis sensing)
POOL = "options_wave2"


def _sha256_lf_normalized(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read().replace(b"\r\n", b"\n")).hexdigest()


# ---------------------------------------------------------------- panel build (P0, local files only)

def build_panels() -> tuple[dict, pd.DatetimeIndex, dict]:
    """P0 panel build (embedded, zero network): contracts registry + ETF
    underlying window slice -> UndPanel per underlying. Window = [min contract
    first_date, cutoff] on the shared SSE calendar."""
    with open(CONTRACTS_JSON, encoding="utf-8") as fh:
        meta = json.load(fh)
    expiry_map = opr.build_expiry_map(meta)
    first = min(pd.Timestamp(c["first_date"]) for c in meta["contracts"])
    panels = {}
    dates = None
    for code in opr.UNDERLYINGS:
        df = pd.read_csv(os.path.join(ROOT, "data", "daily", f"{code}.csv"),
                         index_col=0, parse_dates=True).sort_index()
        seg = df.loc[(df.index >= first) & (df.index <= pd.Timestamp(CUTOFF))]
        panels[code] = opr.UndPanel(code, seg, meta["contracts"], expiry_map, seg.index)
        if dates is None:
            dates = seg.index
        elif list(dates) != list(seg.index):
            raise ValueError(f"calendar mismatch: {code} vs first underlying")
    return panels, dates, meta


# ---------------------------------------------------------------- G1 engine selftest (synthetic, offline)

def _synth_panel(n_days: int = 40, put_premium: float = 0.04,
                 limit_exec: int | None = None) -> tuple[opr.UndPanel, pd.DatetimeIndex]:
    """Synthetic single-underlying panel: flat ETF 3.0, one call + one put
    month family (strikes 2.7..3.3 step 0.1), one late-listed contract."""
    dates = pd.bdate_range("2026-01-05", periods=n_days)
    n = len(dates)
    close = np.full(n, 3.0)
    open_ = np.full(n, 3.0)
    if limit_exec is not None and limit_exec < n:
        open_[limit_exec] = 3.0 * (1.0 + opr.ETF_LIMIT + 0.01)  # limit-up open
    close[34] = 3.25 if n > 34 else 3.0     # expiry-day ITM jump (settlement test)
    amount = np.full(n, 1e9)
    by_dir = {"call": [], "put": []}
    expiry_ts = dates[min(34, n - 2)]
    for i, k in enumerate(np.arange(2.7, 3.35, 0.1)):
        k = round(float(k), 2)
        cprem = np.maximum(3.0 - k, 0.0) + 0.05 * np.linspace(1, 0, n)
        pprem = np.maximum(k - 3.0, 0.0) + put_premium * np.ones(n)
        if n > 34:
            cprem[34] = max(3.25 - k, 0.0)     # expiry-day intrinsic
            cprem[35:] = np.nan                # no rows after expiry (real panels)
            pprem[34] = max(k - 3.25, 0.0)
            pprem[35:] = np.nan
        by_dir["call"].append({"code": f"C{i}", "month": "202602", "direction": "call",
                               "strike": k, "open": cprem.copy(), "close": cprem.copy(),
                               "first_idx": 0, "expiry": (expiry_ts, False)})
        by_dir["put"].append({"code": f"P{i}", "month": "202602", "direction": "put",
                              "strike": k, "open": pprem.copy(), "close": pprem.copy(),
                              "first_idx": 0, "expiry": (expiry_ts, False)})
    pnl = opr.UndPanel.from_components("TEST", dates, open_, close, amount, by_dir)
    return pnl, dates


def options_engine_selftest() -> dict:
    """G1: synthetic-panel unit assertions — determinism, look-ahead,
    lots/budget math, expiry settlement, limit guard, selection availability,
    roll schedule, null determinism, off-flatten."""
    failures = []

    # (1) roll schedule: weekly = first day of each ISO week; monthly = last
    #     trading day of each calendar month
    dates = pd.bdate_range("2026-01-05", periods=40)
    wk = opr.roll_schedule(dates, "weekly")
    if [s for s, e in wk][:3] != [0, 5, 10]:
        failures.append(f"weekly schedule drift: {[s for s, e in wk][:3]}")
    mo = opr.roll_schedule(dates, "monthly")
    if not any(dates[s].month != dates[s + 1].month for s, e in mo):
        failures.append("monthly schedule lacks month boundary")

    pnl, _ = _synth_panel()
    wk = opr.roll_schedule(pnl.dates, "weekly")

    # (2) strike selection: m=0.03, S=3.0 -> target K=3.09 -> argmin band 3.1
    sel = pnl.select(5, "call", 0.03)
    if sel is None or abs(sel["strike"] - 3.1) > 1e-9:
        failures.append(f"select m=0.03 strike {sel and sel['strike']} != 3.1")
    # availability: a month family whose only contract lists at idx=10 must be
    # unselectable at t=5 (first_idx gate), selectable at t=12
    late = {"call": [{"code": "CLATE", "month": "202603", "direction": "call",
                      "strike": 3.05, "open": np.full(len(pnl.dates), 0.02),
                      "close": np.full(len(pnl.dates), 0.02), "first_idx": 10,
                      "expiry": (pnl.dates[-1], False)}], "put": []}
    pnl_late = opr.UndPanel.from_components("TEST", pnl.dates, pnl.open, pnl.close,
                                            np.full(len(pnl.dates), 1e9), late)
    if pnl_late.select(5, "call", 0.03) is not None:
        failures.append("availability: late-listed-only family selectable before first_idx")
    if pnl_late.select(12, "call", 0.03) is None:
        failures.append("availability: late-listed family unselectable after first_idx")

    # (3) CC lots math: sig_eq=1M, S_T=3.0 -> lots=floor(1M/30000)=33
    plan = opr.build_plan({"TEST": pnl}, wk, "covered_call", 0.03)
    res = opr.run_und_sleeve(pnl, [(s, e, f, per["TEST"]) for (s, e, f, mm, per) in plan],
                             1_000_000.0)
    first_opt = [t for t in res["trades"] if t["reason"] == "open"
                 and t["date"] == str(pnl.dates[1].date()) and t["leg"] == "opt_sell"]
    if not first_opt or first_opt[0]["lots"] != 33:
        failures.append(f"CC lots: first open lots {first_opt and first_opt[0]['lots']} != 33")
    if res["shares_end"] != 33 * opr.OPT_UNIT:
        failures.append(f"CC shares_end {res['shares_end']} != {33 * opr.OPT_UNIT}")
    if float(res["equity"].min()) <= 0:
        failures.append(f"CC solvency: equity min {res['equity'].min()} <= 0")

    # (4) PP budget guard: constant put premium 0.5 -> naive lots 33 overshoots
    #     cash; guard decrements to lots*(3.0+0.6)*1e4 <= 1M -> 27
    pnl2, _ = _synth_panel(put_premium=0.5)
    plan2 = opr.build_plan({"TEST": pnl2}, wk, "protective_put", 0.03)
    res2 = opr.run_und_sleeve(pnl2, [(s, e, f, per["TEST"]) for (s, e, f, mm, per) in plan2],
                              1_000_000.0)
    first_buy = [t for t in res2["trades"] if t["reason"] == "open" and t["leg"] == "opt_buy"
                 and t["date"] == str(pnl2.dates[1].date())]
    if not first_buy or first_buy[0]["lots"] != 27:
        failures.append(f"PP budget guard: first buy lots {first_buy and first_buy[0]['lots']} != 27")
    if float(res2["equity"].min()) <= 0:
        failures.append(f"PP solvency: equity min {res2['equity'].min()} <= 0")

    # (5) CSP lots: floor(cash/(K*unit)); K selected ~3.1 -> floor(1M/31000)=32
    plan3 = opr.build_plan({"TEST": pnl}, wk, "cash_secured_put", 0.03)
    res3 = opr.run_und_sleeve(pnl, [(s, e, f, per["TEST"]) for (s, e, f, mm, per) in plan3],
                              1_000_000.0)
    first_sell = [t for t in res3["trades"] if t["reason"] == "open" and t["leg"] == "opt_sell"
                  and t["date"] == str(pnl.dates[1].date())]
    if not first_sell or first_sell[0]["lots"] != 32:
        failures.append(f"CSP lots: first sell lots {first_sell and first_sell[0]['lots']} != 32")
    if res3["shares_end"] != 0:
        failures.append(f"CSP shares_end {res3['shares_end']} != 0")

    # (6) expiry settlement: ITM call at 3.25 close vs K=3.1 -> intrinsic 0.15
    settles = [t for t in res["trades"] if t["reason"] == "expiry_settle"]
    if not settles:
        failures.append("expiry settlement missing")
    else:
        exp_day = str(pnl.dates[34].date())
        s = settles[-1]
        expect = -round(max(3.25 - 3.1, 0.0) * opr.OPT_UNIT * s["lots"], 6)
        if s["date"] != exp_day or abs(s["value"] - expect) > 1e-6:
            failures.append(f"settlement {s['date']} value {s['value']} != {expect}")

    # (7) limit guard: limit-up open at exec day -> no new open, close allowed
    pnl3, _ = _synth_panel(limit_exec=6)
    wk3 = opr.roll_schedule(pnl3.dates, "weekly")
    plan4 = opr.build_plan({"TEST": pnl3}, wk3, "covered_call", 0.03)
    res4 = opr.run_und_sleeve(pnl3, [(s, e, f, per["TEST"]) for (s, e, f, mm, per) in plan4],
                              1_000_000.0)
    day6 = str(pnl3.dates[6].date())
    opens_day6 = [t for t in res4["trades"] if t["reason"] == "open" and t["date"] == day6]
    closes_day6 = [t for t in res4["trades"] if t["reason"] == "roll_close" and t["date"] == day6]
    if opens_day6:
        failures.append("limit guard: new open on limit-up day")
    if not closes_day6:
        failures.append("limit guard: closing on limit-up day must be allowed")

    # (8) look-ahead: truncated panel run == full-panel run prefix (bit-exact);
    #     expiry kept beyond truncation so no settlement fires inside prefix
    k = 20
    pnl_t, _ = _synth_panel()
    dates_t = pnl_t.dates[:k]
    pnl_tr = opr.UndPanel.from_components(
        "TEST", dates_t, pnl_t.open[:k], pnl_t.close[:k], pnl_t.adv20[:k],
        {d: [{**c, "open": c["open"][:k], "close": c["close"][:k]}
             for c in cs] for d, cs in pnl_t.by_dir.items()})
    wk_full = opr.roll_schedule(pnl_t.dates, "weekly")
    wk_tr = opr.roll_schedule(dates_t, "weekly")
    plan_f = opr.build_plan({"TEST": pnl_t}, wk_full, "covered_call", 0.05)
    plan_t = opr.build_plan({"TEST": pnl_tr}, wk_tr, "covered_call", 0.05)
    r_f = opr.run_und_sleeve(pnl_t, [(s, e, f, per["TEST"]) for (s, e, f, mm, per) in plan_f],
                             1_000_000.0)
    r_t = opr.run_und_sleeve(pnl_tr, [(s, e, f, per["TEST"]) for (s, e, f, mm, per) in plan_t],
                             1_000_000.0)
    if not np.array_equal(r_f["equity"].to_numpy()[:k], r_t["equity"].to_numpy(), equal_nan=True):
        failures.append("look-ahead: truncated run equity prefix differs")

    # (9) determinism: double run bit-exact (equity + trades)
    r_f2 = opr.run_und_sleeve(pnl_t, [(s, e, f, per["TEST"]) for (s, e, f, mm, per) in plan_f],
                              1_000_000.0)
    if not (np.array_equal(r_f["equity"].to_numpy(), r_f2["equity"].to_numpy())
            and json.dumps(r_f["trades"], default=str) == json.dumps(r_f2["trades"], default=str)):
        failures.append("determinism: double run differs")

    # (10) null plan determinism (same seed) + off-flatten
    panels_s = {"A": pnl, "B": pnl2}
    rng1 = np.random.default_rng(SEED_BASE)
    rng2 = np.random.default_rng(SEED_BASE)
    np1 = opr.build_null_plan(panels_s, wk, rng1)
    np2 = opr.build_null_plan(panels_s, wk, rng2)
    if json.dumps(np1, default=str) != json.dumps(np2, default=str):
        failures.append("null plan: same-seed rebuild differs")
    cell = opr.run_cell(panels_s, wk, None, 0.05, START_CASH, plan=np1)
    cell2 = opr.run_cell(panels_s, wk, None, 0.05, START_CASH, plan=np1)
    if not np.array_equal(cell["_equity"].to_numpy(), cell2["_equity"].to_numpy()):
        failures.append("null cell: double run equity differs")
    # (11) off-flatten: CC -> off roll must flatten ETF shares (no naked hold)
    manual = [(wk[0][0], wk[0][1], "covered_call", 0.03,
               {"TEST": pnl.select(wk[0][0], "call", 0.03)}),
              (wk[1][0], wk[1][1], None, 0.03, {"TEST": None})]
    r_off = opr.run_und_sleeve(pnl, [(s, e, f, per["TEST"]) for (s, e, f, mm, per) in manual],
                               1_000_000.0)
    if r_off["shares_end"] != 0:
        failures.append(f"off-flatten: shares_end {r_off['shares_end']} != 0")
    return {"gate": "G1 options engine selftest", "ok": len(failures) == 0,
            "failures": failures}


# ---------------------------------------------------------------- gates

def gate_g0() -> dict:
    p = subprocess.run([sys.executable, "-m", "smoke_test"], cwd=ROOT,
                       capture_output=True, text=True, timeout=900)
    tail = p.stdout.split("Summary:")[-1] if "Summary:" in p.stdout else ""
    return {"gate": "G0 smoke", "ok": bool(p.returncode == 0 and "0 FAIL" in tail),
            "exit": p.returncode, "summary": tail.strip()[:60]}


def gate_g2() -> dict:
    """Instrument constants exchange-verification gate (prereg §3 G2, R169
    no-blind-guess law). Component-wise: unit/tick/SSE 经手费 must be verified
    vs official literals with <=30% deviation; CSDC 结算费 must reach
    status=verified (JS-shell fee-list face pending); broker commission is a
    declared non-exchange assumption (exempt). Evidence file frozen at
    results/options_wave2_g2_check.json."""
    problems = []
    statuses: dict[str, str] = {}
    if not os.path.exists(G2_EVIDENCE_PATH):
        problems.append(f"G2 evidence file missing: {G2_EVIDENCE_PATH} "
                        "(exchange verification web leg pending)")
    else:
        with open(G2_EVIDENCE_PATH, encoding="utf-8") as fh:
            ev = json.load(fh)
        comps = {c["item"]: c for c in ev.get("components", [])}
        statuses = {c["item"]: str(c.get("status")) for c in ev.get("components", [])}

        def _check(item: str, module_val: float) -> None:
            c = comps.get(item)
            if not c:
                problems.append(f"G2 evidence missing component: {item}")
                return
            if c.get("status") == "verified":
                v = float(c["value"])
                dev = abs(float(module_val) - v) / v
                if dev > 0.30:
                    problems.append(f"{item}: module {module_val} deviates {dev:.0%} "
                                    f">30% from verified {v} (freeze-verified required)")
            else:
                problems.append(f"{item}: status={c.get('status')} "
                                f"(official face not yet verified)")

        _check("unit", opr.OPT_UNIT)
        _check("tick", opr.OPT_TICK)
        _check("sse_jingshou_etf_yuan_per_contract", 1.3)
        if statuses.get("csdc_settlement_yuan_per_contract") != "verified":
            problems.append("csdc_settlement: not verified — CSDC fee-doc list = "
                            "JS shell; continuation leg required (evidence next_leg)")
        fee_parts = sum(float(comps[k]["value"]) for k in
                        ("sse_jingshou_etf_yuan_per_contract",
                         "csdc_settlement_yuan_per_contract",
                         "broker_commission_yuan_per_contract")
                        if k in comps and isinstance(comps[k].get("value"), (int, float)))
        if abs(fee_parts - opr.OPT_FEE_LOT) > 1e-9:
            problems.append(f"fee_lot decomposition {fee_parts} != module {opr.OPT_FEE_LOT}")
    unit_ok = 5_000 <= opr.OPT_UNIT <= 50_000
    fee_ok = 1.0 <= opr.OPT_FEE_LOT <= 50.0
    tick_ok = 1e-5 <= opr.OPT_TICK <= 1e-2
    if not (unit_ok and fee_ok and tick_ok):
        problems.append(f"plausibility fail: unit_ok={unit_ok} fee_ok={fee_ok} tick_ok={tick_ok}")
    fee_bp_at_ref = opr.OPT_FEE_LOT / (0.05 * opr.OPT_UNIT) * 1e4
    return {"gate": "G2 exchange-verified constants", "ok": len(problems) == 0,
            "problems": problems,
            "module_constants": {"unit": opr.OPT_UNIT, "fee_lot": opr.OPT_FEE_LOT,
                                 "tick": opr.OPT_TICK,
                                 "slip": "max(2 ticks, 5% premium)/side (frozen)"},
            "component_statuses": statuses,
            "fee_bp_at_ref_premium_0.05": round(fee_bp_at_ref, 4),
            "evidence_path": "results/options_wave2_g2_check.json"}


def gate_g3(panels: dict, dates: pd.DatetimeIndex, meta: dict) -> dict:
    """P0 data completeness (prereg §2 five conditions + 三件套(a)(b) hard-bound
    distribution face). Local files only, zero network."""
    problems = []
    n_days = len(dates)
    cal = set(dates)
    # (1) contract files + rows
    files_ok = 0
    for c in meta["contracts"]:
        path = os.path.join(ROOT, c["daily_csv"])
        if not os.path.exists(path):
            problems.append(f"{c['code']}: csv missing")
            continue
        frame = pd.read_csv(path, index_col=0, parse_dates=True).sort_index()
        if len(frame) < 1:
            problems.append(f"{c['code']}: zero rows")
        if len(frame) != c["rows"]:
            problems.append(f"{c['code']}: rows {len(frame)} != registry {c['rows']}")
        # (3) calendar alignment, zero tolerance
        extra = [d for d in frame.index if d not in cal]
        if extra:
            problems.append(f"{c['code']}: {len(extra)} dates off shared calendar")
        # (4) close>0 hygiene
        if (frame["close"].to_numpy(dtype=float) <= 0).any():
            problems.append(f"{c['code']}: non-positive close")
        files_ok += 1
    # (2) underlying faces
    for code, pnl in panels.items():
        if (pnl.close <= 0).any():
            problems.append(f"{code}: non-positive underlying close")
    # (5) strike ladder face: exchange ladders legitimately mix steps by
    #     moneyness band (50ETF 0.05/0.10, 300ETF 0.10/0.25) — s0 G5 "0 缺 0
    #     跳档" means the SELECTION band has no holes, not a single uniform
    #     step. Hard reds: duplicate strikes; selection-band hole at cutoff
    #     (nearest strike farther than the family's max step from target).
    ladder_report = []
    fams: dict[tuple, list] = {}
    for c in meta["contracts"]:
        fams.setdefault((c["underlying"], c["month"], c["direction"]), []).append(c["strike"])
    fam_steps: dict[tuple, float] = {}
    for (und, month, direction), strikes in sorted(fams.items()):
        ks = sorted(set(strikes))
        if len(ks) != len(strikes):
            problems.append(f"ladder {und}/{month}/{direction}: duplicate strikes")
        diffs = [round(b - a, 6) for a, b in zip(ks, ks[1:])]
        steps = sorted(set(diffs))
        fam_steps[(und, month, direction)] = max(steps) if steps else 0.0
        ladder_report.append({"und": und, "month": month, "direction": direction,
                              "n": len(ks), "steps": steps,
                              "note": "mixed-step exchange ladder, disclosure only"})
    last = n_days - 1
    for code, pnl in panels.items():
        for direction in ("call", "put"):
            for m in opr.MONEYNESS:
                sel = pnl.select(last, direction, m)
                if sel is None:
                    problems.append(f"selection hole: {code} {direction} m={m} "
                                    "no alive family at cutoff")
                    continue
                s = pnl.close[last]
                strike_dist = abs(sel["strike"] - (1.0 + m) * s)
                max_step = max(fam_steps.get((code, sel["month"], direction), 0.0),
                               fam_steps.get((code, sel["month"],
                                              "call" if direction == "put" else "put"), 0.0))
                if strike_dist > max_step + 1e-9:
                    problems.append(f"selection hole: {code} {direction} m={m} "
                                    f"nearest K {sel['strike']} strike-distance "
                                    f"{strike_dist:.4f} > family max step {max_step}")
    # 三件套(a) distribution face: per-contract |r1| median/p99.9 + close>0
    # 三件套(b) max hard bound with crisis sensing (single-point disclosure,
    # never auto-fail)
    r1_all, crisis_log = [], []
    for c in meta["contracts"]:
        frame = pd.read_csv(os.path.join(ROOT, c["daily_csv"]), index_col=0,
                            parse_dates=True).sort_index()
        r1 = frame["close"].pct_change().dropna().abs()
        r1_all.extend(r1.to_numpy().tolist())
        hits = [(str(t.date()), round(float(v), 4)) for t, v in r1.items() if v > CRISIS_R1]
        if hits:
            crisis_log.append({"code": c["code"], "hits": hits,
                                "prior": "prereg §5.8 extreme-day prior (premium jumps)"})
    arr = np.asarray(r1_all, dtype=float)
    dist_face = {"n_obs": int(len(arr)),
                 "median": round(float(np.median(arr)), 6) if len(arr) else None,
                 "p999": round(float(np.percentile(arr, 99.9)), 6) if len(arr) else None,
                 "max": round(float(arr.max()), 6) if len(arr) else None}
    # put legs alive (prereg §2: PP/CSP cells honest FAIL otherwise)
    put_alive = {}
    for code, pnl in panels.items():
        put_alive[code] = sum(1 for c in pnl.by_dir["put"] if not math.isnan(c["close"][n_days - 1])) \
            if n_days else 0
        if put_alive[code] == 0:
            problems.append(f"{code}: zero put contracts alive at cutoff")
    # span adaptive verdict (frozen §2)
    span_ok = n_days >= SPAN_DEGRADE_MIN
    return {"gate": "G3 panel completeness", "ok": len(problems) == 0,
            "problems": problems,
            "n_days": n_days, "span_registration_eligible": bool(span_ok),
            "contracts_checked": files_ok,
            "first_dates": {"min": str(min(pd.Timestamp(c["first_date"])
                                          for c in meta["contracts"]).date()),
                            "max_last": str(max(pd.Timestamp(c["last_date"])
                                                for c in meta["contracts"]).date())},
            "strike_ladder": ladder_report,
            "distribution_face_r1": dist_face,
            "crisis_log_over_50pct": crisis_log,
            "put_alive_at_cutoff": put_alive,
            "semantics": "prereg §2 five conditions; hard-bound max face is "
                         "crisis-logged single-point disclosure (三件套(b)), never auto-fail"}


def gate_g4(panels: dict, dates: pd.DatetimeIndex) -> dict:
    """Null + passive determinism on the real panel: same-seed plan rebuild
    + double run bit-exact (prereg gate list G4)."""
    wk = opr.roll_schedule(dates, "weekly")
    rng1 = np.random.default_rng(SEED_BASE)
    rng2 = np.random.default_rng(SEED_BASE)
    p1 = opr.build_null_plan(panels, wk, rng1)
    p2 = opr.build_null_plan(panels, wk, rng2)
    if json.dumps(p1, default=str) != json.dumps(p2, default=str):
        return {"gate": "G4 determinism", "ok": False, "stage": "null plan rebuild differ"}
    c1 = opr.run_cell(panels, wk, None, 0.05, START_CASH, plan=p1)
    c2 = opr.run_cell(panels, wk, None, 0.05, START_CASH, plan=p1)
    eq_ok = np.array_equal(c1["_equity"].to_numpy(), c2["_equity"].to_numpy())
    pa1 = opr.run_passive(panels[opr.UNDERLYINGS[0]], START_CASH)
    pa2 = opr.run_passive(panels[opr.UNDERLYINGS[0]], START_CASH)
    pa_ok = np.array_equal(pa1["_equity"].to_numpy(), pa2["_equity"].to_numpy())
    return {"gate": "G4 determinism", "ok": bool(eq_ok and pa_ok),
            "null_cell_bitexact": bool(eq_ok), "passive_bitexact": bool(pa_ok)}


def run_gates(include_g0: bool = True) -> dict:
    panels, dates, meta = build_panels()
    out = {"panel_days": len(dates)}
    if include_g0:
        out["G0"] = gate_g0()
    out["G1"] = options_engine_selftest()
    out["G2"] = gate_g2()
    out["G3"] = gate_g3(panels, dates, meta)
    out["G4"] = gate_g4(panels, dates)
    return out


# ---------------------------------------------------------------- batch run

def do_run() -> int:
    t0 = time.time()
    print("[options_wave2] prereg integrity + gates ...")
    sha = _sha256_lf_normalized(PREREG_PATH)
    if sha != FROZEN_PREREG_SHA:
        print(f"[options_wave2] PREREG DRIFT: {sha} != {FROZEN_PREREG_SHA} — abort (exit 2)")
        return 2
    gates = run_gates(include_g0=True)
    gates_ok = all(g.get("ok") for name, g in gates.items() if isinstance(g, dict))
    for name, g in gates.items():
        if isinstance(g, dict):
            print(f"  {name}: {'PASS' if g.get('ok') else 'FAIL'}")
            if not g.get("ok"):
                print(f"    detail: {json.dumps(g, ensure_ascii=False, default=str)[:400]}")
    if not gates_ok:
        print("[options_wave2] GATES FAILED — batch aborted (exit 2), no numbers produced")
        return 2

    panels, dates, meta = build_panels()
    wk = opr.roll_schedule(dates, "weekly")
    mo = opr.roll_schedule(dates, "monthly")

    cells: dict[str, dict] = {}
    for fam in opr.FAMILIES:
        for m in opr.MONEYNESS:
            for style, sched in (("weekly", wk), ("monthly", mo)):
                name = f"{fam}_m{int(m * 100)}@{style}"
                plan = opr.build_plan(panels, sched, fam, m)
                cell = opr.run_cell(panels, sched, fam, m, START_CASH, plan=plan)
                cell["x2_full_sharpe"] = opr.run_cell(panels, sched, fam, m, START_CASH,
                                                      cost_mult=2.0, plan=plan)["full"]["sharpe"]
                cell["x3_full_sharpe"] = opr.run_cell(panels, sched, fam, m, START_CASH,
                                                      cost_mult=3.0, plan=plan)["full"]["sharpe"]
                cells[name] = cell
                print(f"  {name}: sharpe={cell['full']['sharpe']} dd={cell['full']['max_drawdown']} "
                      f"entries={cell['full']['n_entries']} x2={cell['x2_full_sharpe']}")

    null_sharpes, null_cells = [], {}
    for k in range(K_NULLS):
        plan = opr.build_null_plan(panels, wk, np.random.default_rng(SEED_BASE + k))
        cell = opr.run_cell(panels, wk, None, 0.05, START_CASH, plan=plan)
        public = {k2: cell[k2] for k2 in ("full", "per_und")}
        null_cells[f"null_{k}"] = public
        null_sharpes.append(cell["full"]["sharpe"])
    vals = [float(x) for x in null_sharpes]
    mu = sum(vals) / len(vals)
    sigma = math.sqrt(sum((x - mu) ** 2 for x in vals) / (len(vals) - 1))
    null_summary = {"n": len(vals), "mu": round(mu, 4), "sigma": round(sigma, 4),
                    "p95": round(float(np.percentile(vals, 95)), 4),
                    "max": round(max(vals), 4), "min": round(min(vals), 4)}

    passive_cells, passive_sharpes = {}, {}
    for code in opr.UNDERLYINGS:
        cell = opr.run_passive(panels[code], START_CASH)
        pname = f"passive_buy_hold_{code}"
        passive_cells[pname] = {"full": cell["full"]}
        passive_sharpes[pname] = cell["full"]["sharpe"]
        print(f"  {pname}: sharpe={cell['full']['sharpe']}")
    naked_blend = (passive_cells["passive_buy_hold_510050"]["full"]["max_drawdown"]
                   + passive_cells["passive_buy_hold_510300"]["full"]["max_drawdown"]) / 2.0

    m = {
        "batch": POOL,
        "meta": {
            "window": {"start": str(dates[0].date()), "end": str(dates[-1].date()),
                       "n_days": int(len(dates)),
                       "retention_window_disclosure":
                           "sina codes face keeps recent expiry months only (s3 "
                           "retention_boundary); pilot backfill batch, wave-2b forward "
                           "collector is the definitive path"},
            "underlyings": list(opr.UNDERLYINGS),
            "cell_composition": "18 candidates (3 families x 3 moneyness x "
                                "{weekly judgement, monthly descriptive}) + 50 nulls "
                                "(seed 63000+k) + 2 passives",
            "blend_disclosure": "18-cell reading: each candidate = 50/50 blend across "
                                "both underlyings (¥500k/sleeve), prereg §0 cell count "
                                "70 with no per-underlying axis",
            "start_cash": START_CASH,
            "roll_semantics": "signal at T close (selection+sizing), T+1 open fills, "
                              "roll-always; monthly regime = last panel day of month; "
                              "expiry = intrinsic cash settle at underlying close "
                              "(physical-delivery proxy, settle fee 0; ITM settle pays "
                              "cash while shares persist -> transient negative cash "
                              "possible, covered by shares, equity-solvency invariant "
                              "asserted in selftest)",
            "constants": {"unit": opr.OPT_UNIT, "fee_lot": opr.OPT_FEE_LOT,
                          "tick": opr.OPT_TICK,
                          "slip": "max(2 ticks, 5% premium)/side",
                          "etf_leg": "knowledge.rules cost_v2_side_rate (ADV20 tiered) "
                                     "+ 1% ADV fill cap"},
            "prereg_sha_frozen": FROZEN_PREREG_SHA,
            "prereg_sha_at_run": sha,
            "schedule": {"weekly_rolls": len(wk), "monthly_rolls": len(mo)},
        },
        **sg.cutoff_meta(CUTOFF),
        "gates": gates,
        "nulls": {"summary": null_summary, "cells": null_cells},
        "passive": passive_cells,
    }
    with open(RESULTS_JSON, "w", encoding="utf-8") as fh:
        json.dump(m, fh, ensure_ascii=False, indent=1, default=str)
    print("[options_wave2] phase-1 JSON written (passive pool registered)")

    null_pool = {"values": vals,
                 "coverage": {"n_values": len(vals), "mu": mu, "sigma": sigma,
                              "schemas_parsed": ["options_wave2:nulls.summary (K=50 in-batch)"],
                              "known_unparsed": []}}
    line = sg.skill_line_v2(batch_cells=BATCH_CELLS, pool=POOL, null_pool=null_pool)
    print(f"[options_wave2] skill_line_v2 = {line['line']} "
          f"(passive={line['passive_term']} null={line['null_term']})")

    verdicts, passers = {}, []
    for name, cell in cells.items():
        v = sg.g1_prime_v2(sharpe_full=cell["full"]["sharpe"], returns=cell["_returns"],
                           batch_cells=BATCH_CELLS, pool=POOL, null_pool=null_pool,
                           n_trades=cell["full"]["n_trades"],
                           n_entries=cell["full"]["n_entries"])
        yearly = opr.yearly_returns(cell["_equity"])
        worst = min(yearly.values()) if yearly else 0.0
        cell["_worst_year"] = worst
        premium_paid_pct = cell["_premium_paid"] / START_CASH
        desc = {
            "annual_positive": bool(cell["full"]["annual_return"] > 0),
            "dd_ok": bool(cell["full"]["max_drawdown"] >= -0.35),
            "no_crash_year": bool(worst >= -0.35),
            "x2_info_sharpe": cell["x2_full_sharpe"],
            "x3_info_sharpe": cell["x3_full_sharpe"],
            "worst_year": round(worst, 4),
        }
        fam = name.split("_")[0] if not name.startswith("cash") else "cash_secured_put"
        fam = name.rsplit("_m", 1)[0]
        if fam == "protective_put":
            desc["insurance_face"] = {
                "premium_paid": round(cell["_premium_paid"], 2),
                "premium_pct_of_start": round(premium_paid_pct, 4),
                "dd_vs_naked_blend_delta": round(cell["full"]["max_drawdown"] - naked_blend, 4),
                "dd_reduction_bps_per_premium_pct": (
                    round((naked_blend - cell["full"]["max_drawdown"]) * 1e4
                          / premium_paid_pct, 2) if premium_paid_pct > 0 else None),
            }
        if fam == "cash_secured_put":
            lots_seen = [t["lots"] for t in cell["_trades"] if t["reason"] == "open"]
            desc["cash_leg"] = {"max_open_lots": max(lots_seen) if lots_seen else 0,
                                "note": "collateral = strike*unit*lots frozen cash"}
        v["descriptive"] = desc
        verdicts[name] = v
        if v["pass_v2"]:
            passers.append(name)
            print(f"  >> {name} PASSES g1_prime_v2")

    # D6: within-batch pairwise corr (all 18) + in-register corr for passers
    rets_df = pd.DataFrame({k: cells[k]["_returns"] for k in cells})
    corr = rets_df.corr()
    within_max = {name: (round(float(corr[name].drop(name).abs().max()), 4)
                          if len(corr) > 1 else None) for name in cells}
    family_pbo = {}
    from pbo import cscv_pbo, align_returns
    for fam in opr.FAMILIES:
        grid = {name: cells[name]["_returns"] for name in cells
                if name.rsplit("_m", 1)[0] == fam}
        family_pbo[fam] = cscv_pbo(align_returns(grid))
    d6_inregister = {}
    verdicts_g2 = {}
    if passers:
        try:
            import ew6_portfolio as E
            E._init_worker()
            from firm.hr import TRADERS_DIR, load_trader
            member_rets = {}
            for fn in sorted(os.listdir(TRADERS_DIR)):
                if not fn.endswith(".json"):
                    continue
                tid = fn[:-5]
                t = load_trader(tid)
                if t.get("status") == "FIRE":
                    continue
                mr = E.member_run(tid)
                eq = pd.Series(mr["eq"], index=pd.to_datetime(mr["dates"]))
                member_rets[tid] = eq.pct_change().dropna()
            for name in passers:
                cr = cells[name]["_returns"]
                pairs = {}
                for tid, mret in member_rets.items():
                    j = pd.concat([cr, mret], axis=1, join="inner").dropna()
                    if len(j) > 60 and j.iloc[:, 1].std() > 0:
                        pairs[tid] = round(float(j.corr().iloc[0, 1]), 4)
                d6_inregister[name] = {
                    "max_abs_corr": round(max((abs(v) for v in pairs.values()), default=0.0), 4),
                    "pairs": pairs}
        except Exception as exc:  # noqa: BLE001
            d6_inregister = {"error": f"in-register corr skipped: {exc}"}
        for name in passers:
            fam = name.rsplit("_m", 1)[0]
            dsr = sg.deflated_sharpe_ratio(cells[name]["_returns"],
                                           n_trials=line["n_eff"], var_null_sr=sigma ** 2)
            verdicts_g2[name] = sg.g2_registration_v2(
                g1_pass=True, dsr=dsr, pbo=family_pbo[fam]["pbo"])

    ledger = sg.append_ledger(
        POOL, BATCH_CELLS, "results/options_wave2.json", evidence_cutoff=CUTOFF,
        note=("18 candidates (CC/PP/CSP x m{3,5,10}% x weekly/monthly) + 50 nulls "
              "(seed 63_000+k) + 2 passives; retention-window pilot 2026-01-29..2026-09-24, "
              "blend 50/50 across 510050/510300; pool options_wave2 own nulls+passives; "
              "prereg research/OPTIONS_WAVE2_PREREG.md sha a6998921"))

    audit_seg = {}
    try:
        subprocess.run([sys.executable, "scripts/compute_audit.py"], cwd=ROOT,
                       capture_output=True, text=True, timeout=120)
    except Exception as exc:  # noqa: BLE001
        print(f"[options_wave2] compute_audit in-batch run failed: {exc}")
    apath = os.path.join(ROOT, "results", "compute_audit.json")
    if os.path.exists(apath):
        with open(apath, encoding="utf-8") as fh:
            aj = json.load(fh)
        latest = aj.get("history", [{}])[-1] if aj.get("history") else aj
        audit_seg = {"source": "results/compute_audit.json (in-batch run, latest)",
                     "verdict": latest.get("verdict"), "ts": latest.get("ts"),
                     "cpu_pct": latest.get("cpu_pct"), "flags": latest.get("flags")}

    final = dict(m)
    final.update({
        "null_pool": null_pool, "skill_line": line, "verdicts_g1": verdicts,
        "g1_passers": passers, "verdicts_g2": verdicts_g2,
        "d6": {"within_batch_max_abs_corr": within_max, "in_register": d6_inregister,
               "reject_line": 0.7, "preannotation": "CC<->CSP twin corr >=0.7 band "
                                                  "expected by design (prereg §1)"},
        "family_pbo": family_pbo, "trials_ledger": ledger, "audit": audit_seg,
        "passive_sharpes": passive_sharpes,
        "candidates": {k: {k2: cell[k2] for k2 in
                           ("full", "per_und", "x2_full_sharpe", "x3_full_sharpe")}
                       for k, cell in cells.items()},
    })
    with open(RESULTS_JSON, "w", encoding="utf-8") as fh:
        json.dump(final, fh, ensure_ascii=False, indent=1, default=str)

    with open(RESULTS_CSV, "w", newline="", encoding="utf-8") as fh:
        wr = csv.writer(fh)
        wr.writerow(["cell", "family", "moneyness", "style", "kind", "sharpe_full",
                     "annual_return", "max_drawdown", "worst_year", "x2_full_sharpe",
                     "x3_full_sharpe", "n_trades", "n_entries", "turnover", "win_rate",
                     "premium_paid", "line", "line_ok", "ci_ok", "pass_v2"])
        for name, cell in cells.items():
            v = verdicts[name]
            fam, rest = name.rsplit("_m", 1)
            mm, style = rest.split("@")
            wr.writerow([name, fam, int(mm) / 100, style, "candidate",
                         cell["full"]["sharpe"], cell["full"]["annual_return"],
                         cell["full"]["max_drawdown"], cell["_worst_year"],
                         cell["x2_full_sharpe"], cell["x3_full_sharpe"],
                         cell["full"]["n_trades"], cell["full"]["n_entries"],
                         cell["full"]["turnover"], cell["full"]["win_rate"],
                         round(cell["_premium_paid"], 2), v["skill_line"]["line"],
                         v["line_ok"], v["ci_lower_bound_positive"], v["pass_v2"]])
        for k in range(K_NULLS):
            c = null_cells[f"null_{k}"]
            wr.writerow([f"null_{k}", "random", "", "weekly", "null", c["full"]["sharpe"],
                         c["full"]["annual_return"], c["full"]["max_drawdown"], "", "", "",
                         c["full"]["n_trades"], c["full"]["n_entries"],
                         c["full"]["turnover"], c["full"]["win_rate"], "",
                         "", "", "", ""])
        for pname, c in passive_cells.items():
            wr.writerow([pname, "passive_buy_hold", "", "", "passive", c["full"]["sharpe"],
                         c["full"]["annual_return"], c["full"]["max_drawdown"], "", "", "",
                         c["full"]["n_trades"], c["full"]["n_entries"], "", "", "",
                         "", "", "", ""])

    try:
        with open(ATTRITION_JSON, encoding="utf-8") as fh:
            attr = json.load(fh)
        attr["entries"].append({
            "batch": "OPTIONS_WAVE2",
            "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
            "kind": "search",
            "cells_ledger_delta": BATCH_CELLS,
            "ledger_total_after": ledger.get("total"),
            "gates": {"skill_line_v2": line["line"], "g1_passers": len(passers)},
            "eliminated": 18 - len(passers),
            "refs": {"results": "results/options_wave2.json",
                     "prereg": "research/OPTIONS_WAVE2_PREREG.md"},
        })
        with open(ATTRITION_JSON, "w", encoding="utf-8") as fh:
            json.dump(attr, fh, ensure_ascii=False, indent=1)
    except Exception as exc:  # noqa: BLE001
        print(f"[options_wave2] attrition append failed: {exc}")

    print(f"[options_wave2] DONE in {time.time() - t0:.1f}s — passers: {passers}")
    print(f"[options_wave2] null summary: {null_summary}")
    print(f"[options_wave2] skill line: {line['line']}")
    return 0


# ---------------------------------------------------------------- selftest (offline)

def do_selftest() -> int:
    g = options_engine_selftest()
    fails = list(g["failures"])
    if sg.SEED_REGISTRY.get(POOL) != SEED_BASE:
        fails.append(f"SEED_REGISTRY {POOL} != {SEED_BASE}")
    print(f"[options_wave2 selftest] {'ALL PASS' if not fails else 'FAIL: ' + str(fails)}")
    return 0 if not fails else 1


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "selftest"
    if cmd == "gates":
        gs = run_gates()
        ok = True
        for name, g in gs.items():
            if isinstance(g, dict):
                print(f"{name}: {'PASS' if g.get('ok') else 'FAIL'}")
                if not g.get("ok"):
                    ok = False
                    print(json.dumps(g, ensure_ascii=False, default=str)[:600])
        sys.exit(0 if ok else 2)
    if cmd == "run":
        sys.exit(do_run())
    if cmd == "selftest":
        sys.exit(do_selftest())
    print("usage: options_wave2.py gates|run|selftest")
    sys.exit(1)
