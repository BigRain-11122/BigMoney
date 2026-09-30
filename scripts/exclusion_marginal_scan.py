"""EXCLUSION-MARGINAL-P1 runner (D-20260930-41 deliverable #3, bm-b berth).

Scan the marginal value of each stock-exclusion rule on a FROZEN classical
low-amount ("低量") monthly-rebalance selection base, over the bm-b astock
daily panel. Three-command identity (W14 lineage):

  probe     real-read data anchors -> results/exclusion_marginal_scan/probe_facts.json
  selftest  hermetic offline checks (rule masks, cell enumeration, cost spec,
            engine fixtures incl. hand-value cost leg per r474 law)
  run       full burn -- engine landed r476 bm-b; FAIL-CLOSED burn gates
            (probe face assertions / panel-complete / eligibility fresh /
             closed-family / seed-registry law) with honest rc=2 refusal;
            idempotent: existing scan.json = no-op exit 0 unless
            EXCLUSION_MARGINAL_REBURN=1 (double-count guard).

Laws carried: G-ANCHOR-FACE four-tuples + same-face assertions (O-20260928-1712),
R99 freeze-before-burn, D-20260930-40 CN-C7 roundtrip via knowledge/cost_spec,
D-20260930-41 retail-quant track #3, trial gate <=500/30d (RETAIL_QUANT_TRACK
sec.4), evidence_cutoff=2026-09-22 (P-5C binding, ALLOC-POLICY-SCAN-P1 precedent),
trials_ledger appended BEFORE json.dump embed (r474 law), cost primitives
imported never rewritten (knowledge/rules.py fee_schedule_for + cost_v2 tiers).

Engine faces frozen in prereg sec.3 (do not reinterpret at burn time):
  monthly last-trading-day signal -> amt20(own 20 bars, min_periods=20) ASC rank
  -> cell rule mask -> top N=10 equal-weight (1e6 initial, sleeve=signal-day-close
  equity/10, 100-share lots, ADV20 1% fill cap, min-commission 5 CNY)
  -> next trading day open execution (T+1 conservative proxy, O-1132)
  -> hold 1 month; entry-suspended = skipped (honest miss), exit-suspended =
  first resume-day open; overlap names held without trade (classical monthly
  equal-weight rotation, turnover only on entering/exiting names).
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES_DIR = os.path.join(ROOT, "results", "exclusion_marginal_scan")
PROBE_FILE = os.path.join(RES_DIR, "probe_facts.json")
SCAN_FILE = os.path.join(RES_DIR, "scan.json")
CELLS_FILE = os.path.join(RES_DIR, "scan_cells.csv")
ASTOCK_STATUS = os.path.join(ROOT, "results", "astock_daily_update_status.json")
ATTR_FILE = os.path.join(ROOT, "results", "gate_attrition.bm-b.json")
CAL_CSV = os.path.join(ROOT, "data", "daily", "sh510050.csv")  # market calendar face (2005-02-23+, covers 2007 signals)

EVIDENCE_CUTOFF = "2026-09-22"          # P-5C binding, frozen pre-burn
PANEL_DIR = os.path.join(ROOT, "data", "astock_daily", "per")
ELIG_CSV = os.path.join(ROOT, "data", "fundamental", "eligibility.csv")
MASK_CSV = os.path.join(ROOT, "data", "fundamental", "b_layer_mask.csv")

FIRST_SIGNAL = "2007-01"                # frozen base window_first_signal
START_YEARS = list(range(2007, 2023))   # 16 all-starts (2007..2022 Jan first td)
SEED_KEY = "exclusion_marginal_rand"    # registered r476, band 20329500..20329750 (renumbered from 20329000: same-window collision with bm-c cross_start_robustness_p1, ours unburned = yields; science_gates comment carries the ruling)
N_HOLDINGS = 10
INITIAL_CASH = 1_000_000.0

# frozen rule set (prereg sec.3; ids are contract -- do not renumber)
RULES = ["r1_loss", "r2_st", "l1_liq5000w", "l2_price1y", "l3_age250", "l4_active10td"]

# frozen base params (prereg sec.3)
BASE_PARAMS = {
    "rank_face": "amt20_mean asc (low-amount first)",
    "n_holdings": 10,
    "weighting": "equal",
    "rebalance": "monthly (month-end signal, next trading day open execution, T+1)",
    "initial_capital_cny": 1_000_000,
    "window_first_signal": "2007-01",
    "allstart_jan_firsts": "2007..2022 (16 starts)",
    "cost_face": "V2 stock: knowledge/rules.py fee_schedule_for + ADV20 3-layer slippage",
}

CELLS = (
    [{"cell": "FULL", "off": []}, {"cell": "NONE", "off": RULES}]
    + [{"cell": f"LOO-{r}", "off": [r]} for r in RULES]
    + [{"cell": f"AOI-{r}", "off": [x for x in RULES if x != r]} for r in RULES]
    + [{"cell": "RAND-FULL", "off": [], "base": "random"},
       {"cell": "RAND-NONE", "off": RULES, "base": "random"}]
)

if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
_SCRIPTS_DIR = os.path.join(ROOT, "scripts")
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)


def _sha16(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def _load_codes() -> list[str]:
    """Universe = eligibility 6-digit codes with sh/sz prefixes only
    (0/3 -> sz, 6 -> sh; B-share 2/9 + BSE 4/8/92x skipped per collector law,
    mirrors update_astock_daily universe_n=5228 face)."""
    df = pd.read_csv(ELIG_CSV, dtype={"code": str})
    return [c for c in df["code"].astype(str).tolist()
            if len(c) == 6 and c[0] in ("0", "3", "6")]


# --------------------------------------------------------------------------
# shared loader faces (probe + burn use the SAME loaders -- face assertion law)
# --------------------------------------------------------------------------
def _load_calendar() -> tuple[list[str], dict[str, int]]:
    """Market trading calendar from the frozen five-member face sh510050
    (full history 2005-02-23+, longest core48 member). Returns date list
    (UNtruncated -- signal month-ends must come from the true calendar) and
    date->position dict."""
    df = pd.read_csv(CAL_CSV, usecols=["date"])
    dates = df["date"].astype(str).tolist()
    return dates, {d: i for i, d in enumerate(dates)}


def _signal_schedule(cal: list[str]) -> tuple[list[str], list[int]]:
    """Month-end trading days (true calendar) from FIRST_SIGNAL whose
    next-trading-day execution falls <= evidence cutoff. Returns
    (signal_dates, exec_positions)."""
    cal_pos_of = {d: i for i, d in enumerate(cal)}
    month_last: dict[str, int] = {}
    for i, d in enumerate(cal):
        month_last[d[:7]] = i
    sig_pos, dates = [], []
    cutoff_pos = max(i for i, d in enumerate(cal) if d <= EVIDENCE_CUTOFF)
    for ym in sorted(month_last):
        if ym < FIRST_SIGNAL:
            continue
        p = month_last[ym]
        if p + 1 < len(cal) and p + 1 <= cutoff_pos:
            sig_pos.append(p)
            dates.append(cal[p])
    return dates, sig_pos


# --------------------------------------------------------------------------
# probe (frozen r475 face -- do not modify semantics)
# --------------------------------------------------------------------------
def probe() -> int:
    """Real-read anchors, frozen into facts file (G-ANCHOR-FACE four-tuples)."""
    os.makedirs(RES_DIR, exist_ok=True)
    codes = _load_codes()
    files = sorted(os.listdir(PANEL_DIR))
    facts = {
        "probe": "EXCLUSION-MARGINAL-P1 data anchors",
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "anchor_faces": {
            "panel": {
                "path": "data/astock_daily/per/<code>.csv",
                "loader": "pandas.read_csv",
                "start": "per-file first date (1991-04-03 oldest实证)",
                "warmup": "amt20_mean min_periods=20; age250 rule needs 250 bars",
            },
            "eligibility": {
                "path": "data/fundamental/eligibility.csv",
                "loader": "firm.risk.b_layer_filter.load_eligibility",
                "start": "snapshot (24h refresh, update_fundamental.py)",
                "warmup": "static mask, none",
            },
            "b_layer_mask": {
                "path": "data/fundamental/b_layer_mask.csv",
                "loader": "firm.risk.b_layer_filter.load_mask",
                "start": "snapshot (regenerated per eligibility refresh)",
                "warmup": "static mask, none",
            },
        },
        "panel_files": len(files),
        "eligibility_codes": len(codes),
        "cells": [c["cell"] for c in CELLS],
        "n_cells": len(CELLS),
        "rules": RULES,
        "base_params": BASE_PARAMS,
    }
    # real-read three sample anchors (first/middle/last by code order)
    sample = {}
    for code in [files[0].split(".")[0], files[len(files) // 2].split(".")[0], files[-1].split(".")[0]]:
        df = pd.read_csv(os.path.join(PANEL_DIR, f"{code}.csv"))
        amt20 = df["amount"].rolling(20).mean()
        cutoff_rows = int((df["date"] <= EVIDENCE_CUTOFF).sum())
        sample[code] = {
            "rows_total": int(len(df)),
            "rows_to_cutoff": cutoff_rows,
            "first": str(df["date"].iloc[0]),
            "last": str(df["date"].iloc[-1]),
            "amt20_first_valid_idx": int(amt20.first_valid_index() or -1),
            "sha16": _sha16(os.path.join(PANEL_DIR, f"{code}.csv")),
        }
    facts["sample_anchors"] = sample
    # static mask reason counts (b_layer_filter output, same-face)
    try:
        mask = pd.read_csv(MASK_CSV, dtype={"code": str})
        ex = mask[~mask["ok_static"].astype(bool)] if "ok_static" in mask.columns else pd.DataFrame()
        facts["mask_reason_counts"] = {k: int(v) for k, v in
                                       ex["exclude_reason"].value_counts().items()} if len(ex) else {}
        facts["mask_total"] = int(len(mask))
    except Exception as e:  # noqa: BLE001
        facts["mask_error"] = str(e)[:120]
    # CN-C7 roundtrip derivation face (real-read, no hand-copy)
    try:
        sys.path.insert(0, ROOT)
        from knowledge import cost_spec  # noqa: PLC0415
        facts["cost_spec_face"] = getattr(cost_spec, "FACE_A_ETF_RT_BP", None) or "see knowledge/cost_spec.py"
    except Exception as e:  # noqa: BLE001
        facts["cost_spec_face"] = f"import-fail: {str(e)[:80]}"
    with open(PROBE_FILE, "w", encoding="utf-8") as f:
        json.dump(facts, f, ensure_ascii=False, indent=1)
    print(json.dumps({k: facts[k] for k in
                      ("panel_files", "eligibility_codes", "n_cells",
                       "mask_total", "mask_reason_counts")},
                     ensure_ascii=False, indent=1))
    print(f"probe facts -> {PROBE_FILE}")
    return 0


# --------------------------------------------------------------------------
# engine core (pure functions -- selftest injects synthetic fixtures)
# --------------------------------------------------------------------------
def _side_cost(notional: float, fee, slip_rate: float, is_sell: bool) -> float:
    """V2 stock side cost in CNY. Fixed fees + tiered slippage via rate
    primitives; commission min-floor discrete; stamp sell-only (CN-C1/2/3).
    Slippage rate passed in (tier already resolved from no-lookahead ADV)."""
    fixed = notional * (fee.handling_fee + fee.supervision_fee + fee.transfer_fee
                        + slip_rate)
    comm = max(fee.commission_min, notional * fee.commission_rate)
    return fixed + comm + (notional * fee.stamp_tax if is_sell else 0.0)


def _sim_cell(sel_by_month, mkt, sig_pos, n_cal, start_month: int,
              fee, slip_of) -> dict:
    """Replay one cell from start_month. sel_by_month = list (len n_sig) of
    selection lists [(code, adv20_signal)] (empty = no candidates).
    mkt = lazy cache dict code -> (mpos, open, close, ffclose len n_cal).
    slip_of(code, m) = no-lookahead slippage tier rate for month m trade.
    Event-walk: exec days and resume days are events; a suspended exit keeps
    marking at ffclose until its actual resume day, where the sale realizes
    (no liquidity look-ahead -- cash lands on the resume day, never before)."""
    cash = INITIAL_CASH
    pos: dict[str, float] = {}           # code -> shares (live)
    pending: dict[str, float] = {}       # code -> shares awaiting resume open
    resume_at: dict[str, int] = {}       # code -> first bar pos >= exit intent
    eq = np.full(n_cal, np.nan)
    buy_notional = sell_notional = cost_paid = 0.0
    n_buys = n_sells = n_skip_entry = 0

    def holdings_value(a: int, b: int) -> float:
        val = 0.0
        for c, sh in pos.items():
            val += sh * mkt[c][3][a:b]
        for c, sh in pending.items():
            val += sh * mkt[c][3][a:b]
        return val

    def mark(a: int, b: int):
        if b > a:
            eq[a:b] = cash + holdings_value(a, b)

    def realize(c: str, sh: float, r: int, m_slip_month: int):
        nonlocal cash, sell_notional, cost_paid, n_sells
        px = float(mkt[c][1][int(np.searchsorted(mkt[c][0], r))])
        notional = px * sh
        slip = slip_of(c, m_slip_month)
        cost = _side_cost(notional, fee, slip, True)
        cash += notional - cost
        sell_notional += notional
        cost_paid += cost
        n_sells += 1

    def walk_pending(upto: int, m_slip_month: int):
        """Realize pendings whose resume day falls in (day, upto], marking
        segments in order so the curve jumps exactly on the resume day."""
        nonlocal day
        for c in sorted(pending, key=lambda k: (resume_at[k] is None,
                                                resume_at[k] if resume_at[k] is not None else 0)):
            r = resume_at.get(c)
            if r is None or r > upto:
                continue
            mark(day, r)
            day = r
            realize(c, pending.pop(c), r, m_slip_month)
            resume_at.pop(c, None)

    cur = start_month
    day = sig_pos[start_month]           # curve starts at first signal day
    while cur < len(sel_by_month):
        p_sig = sig_pos[cur]
        p_exec = p_sig + 1
        if p_exec >= n_cal:
            break
        # 1) pending exits resumed before this exec: realize (cash funds buys)
        walk_pending(p_exec, cur)
        # 2) mark to exec day
        mark(day, p_exec)
        day = p_exec
        # 3) sleeve target from signal-day-close equity
        sleeve = eq[p_sig] / N_HOLDINGS if not np.isnan(eq[p_sig]) \
            else INITIAL_CASH / N_HOLDINGS
        new_names = [c for c, _ in sel_by_month[cur]]
        new_set = set(new_names)
        # 4) sells: live names leaving the new cohort
        for c in list(pos.keys()):
            if c in new_set:
                continue
            mpos = mkt[c][0]
            j = int(np.searchsorted(mpos, p_exec, side="left"))
            if j < len(mpos) and mpos[j] == p_exec:
                realize(c, pos.pop(c), p_exec, cur)
            else:
                pending[c] = pos.pop(c)          # suspended -> resume-day exit
                resume_at[c] = int(mpos[j]) if j < len(mpos) else None
        # 5) pendings re-selected by the new cohort: cancel the exit (wanted)
        for c in list(pending.keys()):
            if c in new_set:
                pos[c] = pending.pop(c)
                resume_at.pop(c, None)
        # 6) buys: new names not already held
        for c, adv in sel_by_month[cur]:
            if c in pos or c in pending:
                continue
            mpos, opens, _, _ = mkt[c]
            j = int(np.searchsorted(mpos, p_exec, side="left"))
            if j >= len(mpos) or mpos[j] != p_exec:
                n_skip_entry += 1                # suspended on exec day -> skip
                continue
            px = float(opens[j])
            slip = slip_of(c, cur)
            cap_shares = int((K_ADV_CAP * adv) / px) if adv and adv > 0 else 0
            cap_shares = (cap_shares // 100) * 100
            demand = int(sleeve / px / 100) * 100
            shares = min(demand, cap_shares)
            while shares > 0:
                notional = shares * px
                cost = _side_cost(notional, fee, slip, False)
                if cash >= notional + cost:
                    break
                shares -= 100
            if shares <= 0:
                n_skip_entry += 1                # cash/ADV-capped honest miss
                continue
            notional = shares * px
            cost = _side_cost(notional, fee, slip, False)
            cash -= notional + cost
            pos[c] = float(shares)
            buy_notional += notional
            cost_paid += cost
            n_buys += 1
        cur += 1
    # final leg: pendings resuming before the cutoff realize on their day
    walk_pending(n_cal - 1, max(cur - 1, start_month))
    mark(day, n_cal)
    open_at_end = {c: sh for c, sh in list(pos.items()) + list(pending.items())}
    return {
        "eq": eq, "cash": cash, "open_at_end": open_at_end,
        "buy_notional": buy_notional, "sell_notional": sell_notional,
        "cost_paid": cost_paid, "n_buys": n_buys, "n_sells": n_sells,
        "n_skip_entry": n_skip_entry,
    }


def _metrics(replay: dict, cal: list[str], day0: int) -> dict:
    eq = replay["eq"]
    days = (len(eq) - day0)
    years = days / 244.0                     # A-share ~244 trading days/yr
    final = float(eq[-1])
    ann = (final / INITIAL_CASH) ** (1.0 / years) - 1.0
    window = eq[day0:]
    cummax = np.maximum.accumulate(window)
    maxdd = float((window / cummax - 1.0).min())
    rets = np.diff(window) / window[:-1]
    sd = float(np.std(rets, ddof=1))
    sharpe = float(np.mean(rets) / sd * np.sqrt(244.0)) if sd > 0 else 0.0
    # rolling worst annualized (3/5/10y in trading days)
    roll = {}
    for yy, td in ((3, 732), (5, 1220), (10, 2440)):
        if len(window) > td + 1:
            seg = window[:len(window) - td]
            r = (window[td:] / seg) ** (1.0 / yy) - 1.0
            roll[f"worst_{yy}y"] = float(r.min())
        else:
            roll[f"worst_{yy}y"] = None
    mean_eq = float(np.nanmean(window))
    yrs_held = years
    return {
        "ann_ret_net": ann, "maxdd": maxdd, "sharpe": sharpe,
        "t_from_sharpe": sharpe * np.sqrt(years),
        "final_equity": final, "years": years,
        "turnover_ann": (replay["buy_notional"] + replay["sell_notional"]) / 2.0
                        / mean_eq / yrs_held if mean_eq > 0 else None,
        "cost_drag_ann": replay["cost_paid"] / mean_eq / yrs_held if mean_eq > 0 else None,
        "n_buys": replay["n_buys"], "n_sells": replay["n_sells"],
        "n_skip_entry": replay["n_skip_entry"],
        "open_positions_at_end": len(replay["open_at_end"]),
        **roll,
    }


# engine needs the ADV cap constant from knowledge/rules -- imported lazily so
# the hermetic selftest can monkeypatch fixtures without repo data
K_ADV_CAP = 0.01


def _build_selection(amt, close, barcnt, stale, r1, r2, cell: dict,
                     seed_base: int | None) -> list:
    """Per-signal selection. Matrices are (n_codes, n_sig). Returns list over
    months of list[(code_idx, adv20)] (None when no valid candidates)."""
    n_sig = amt.shape[1]
    off = set(cell.get("off", []))
    is_rand = cell.get("base") == "random"
    out = []
    for m in range(n_sig):
        valid = ~np.isnan(amt[:, m])
        keep = valid.copy()
        if "r1_loss" not in off:
            keep &= ~r1
        if "r2_st" not in off:
            keep &= ~r2
        if "l1_liq5000w" not in off:
            keep &= amt[:, m] >= 5e7
        if "l2_price1y" not in off:
            keep &= close[:, m] >= 1.0
        if "l3_age250" not in off:
            keep &= barcnt[:, m] >= 250
        if "l4_active10td" not in off:
            keep &= stale[:, m] <= 10
        idx = np.where(keep)[0]
        if len(idx) == 0:
            out.append(None)
            continue
        if is_rand:
            rng = np.random.default_rng([seed_base + m, 7919])
            k = min(N_HOLDINGS, len(idx))
            pick = rng.choice(idx, size=k, replace=False)
            out.append([(int(i), float(amt[i, m])) for i in pick])
        else:
            order = idx[np.lexsort((idx, amt[idx, m]))]
            pick = order[:N_HOLDINGS]
            out.append([(int(i), float(amt[i, m])) for i in pick])
    return out


# --------------------------------------------------------------------------
# selftest (hermetic; r475 S1-S5 + r476 engine legs S6-S16)
# --------------------------------------------------------------------------
def selftest() -> int:
    ok = 0
    # S1: cell enumeration is exactly 16, ids unique, LOO/AOI complement
    cells = [c["cell"] for c in CELLS]
    assert len(cells) == 16 and len(set(cells)) == 16, "cell count/id contract"
    assert sum(1 for c in CELLS if c["cell"].startswith("LOO-")) == len(RULES)
    assert sum(1 for c in CELLS if c["cell"].startswith("AOI-")) == len(RULES)
    for r in RULES:
        loo = next(c for c in CELLS if c["cell"] == f"LOO-{r}")
        aoi = next(c for c in CELLS if c["cell"] == f"AOI-{r}")
        assert r in loo["off"] and r not in aoi["off"], "LOO/AOI complement"
        assert set(aoi["off"]) == set(RULES) - {r}, "AOI keeps exactly one rule"
    ok += 1
    # S2: rank face determinism on synthetic panel (amt20 asc -> pick order)
    df = pd.DataFrame({"amount": [10.0] * 25 + [5.0] * 25 + [1.0] * 25})
    amt20 = df["amount"].rolling(20).mean()
    assert abs(amt20.iloc[24] - 10.0) < 1e-12 and amt20.first_valid_index() == 19
    ok += 1
    # S3: trading month-end signal grid = last TRADING day per (year, month)
    d = pd.Series(pd.to_datetime(["2026-01-28", "2026-01-29", "2026-02-27",
                                  "2026-02-28", "2026-03-31"]))
    ym = d.dt.strftime("%Y-%m")
    last_per_ym = d.groupby(ym).transform("max") == d
    assert list(last_per_ym) == [False, True, False, True, True]
    ok += 1
    # S4: evidence cutoff truncation is monotone (no post-cutoff leakage)
    dates = pd.Series(["2026-09-21", "2026-09-22", "2026-09-23"])
    kept = dates[dates <= EVIDENCE_CUTOFF]
    assert len(kept) == 2 and kept.iloc[-1] == EVIDENCE_CUTOFF
    ok += 1
    # S5: trial accounting contract (16 cells -> 16 trials at burn)
    assert len(cells) == 16
    ok += 1
    # S6: selection builder -- ranking + all six rule masks on synthetic faces
    # fixture: 0 fails l1 only / 1 fails l2 only / 2 fails l3 only /
    # 3 fails l4 only / 4 fails r1 only (loss-maker) / 5 fails r2 only (ST) /
    # 6,7 fully clean (amt 8e7 / 2e8)
    n_codes, n_sig = 8, 1
    amt = np.full((n_codes, n_sig), np.nan)
    close = np.full((n_codes, n_sig), np.nan)
    barcnt = np.full((n_codes, n_sig), np.nan)
    stale = np.full((n_codes, n_sig), np.nan)
    rows = [(3e7, 5.0, 300, 0), (6e7, 0.5, 300, 0), (6e7, 5.0, 100, 0),
            (6e7, 5.0, 300, 20), (6e7, 5.0, 300, 0), (6e7, 5.0, 300, 0),
            (8e7, 5.0, 300, 0), (2e8, 5.0, 300, 0)]
    for i, (a, c, b, s) in enumerate(rows):
        amt[i, 0], close[i, 0], barcnt[i, 0], stale[i, 0] = a, c, b, s
    r1 = np.array([False, False, False, False, True, False, False, False])
    r2 = np.array([False, False, False, False, False, True, False, False])
    pick = lambda sel: [i for i, _ in sel[0]]  # noqa: E731
    full = _build_selection(amt, close, barcnt, stale, r1, r2,
                            {"cell": "FULL", "off": []}, None)
    assert pick(full) == [6, 7], "FULL keeps clean names, amt asc"
    assert pick(_build_selection(amt, close, barcnt, stale, r1, r2,
                                 {"cell": "NONE", "off": RULES}, None)) == \
        list(range(8)), "NONE keeps all amt-valid names, amt asc"
    assert pick(_build_selection(amt, close, barcnt, stale, r1, r2,
                                 {"cell": "LOO-r1_loss", "off": ["r1_loss"]}, None)) == \
        [4, 6, 7], "LOO-r1 re-admits ONLY the loss-maker (others still filtered)"
    assert pick(_build_selection(amt, close, barcnt, stale, r1, r2,
                                 {"cell": "LOO-l1_liq5000w", "off": ["l1_liq5000w"]}, None)) == \
        [0, 6, 7], "LOO-l1 re-admits ONLY the sub-floor name"
    assert pick(_build_selection(amt, close, barcnt, stale, r1, r2,
                                 {"cell": "AOI-r1_loss", "off": [r for r in RULES if r != "r1_loss"]}, None)) == \
        [0, 1, 2, 3, 5, 6, 7], "AOI-r1 applies ONLY r1 (drops the loss-maker)"
    assert pick(_build_selection(amt, close, barcnt, stale, r1, r2,
                                 {"cell": "AOI-l1_liq5000w", "off": [r for r in RULES if r != "l1_liq5000w"]}, None)) == \
        [1, 2, 3, 4, 5, 6, 7], "AOI-l1 applies ONLY the liquidity floor"
    ok += 1
    # S7: RAND determinism -- same seed twice = identical draws; differs by month
    rc = {"cell": "RAND-NONE", "off": RULES, "base": "random"}
    a1 = _build_selection(amt, close, barcnt, stale, r1, r2, rc, 20329500)
    a2 = _build_selection(amt, close, barcnt, stale, r1, r2, rc, 20329500)
    assert a1 == a2, "RAND seed determinism"
    ok += 1
    # S8: hand-value cost leg (r474 law: every rate/multiplier gets a literal leg)
    from knowledge import rules as kr
    stock_fee = kr.fee_schedule_for("600000")
    slip2 = kr.cost_v2_slippage(6e8)      # 2bp tier
    assert abs(slip2 - 0.0002) < 1e-15, "2bp tier"
    # buy 100k CNY @ 2bp tier: fixed 0.641bp=6.41 + comm max(5, 25)=25 + slip 2bp=20
    buy_cost = _side_cost(100_000.0, stock_fee, slip2, False)
    assert abs(buy_cost - 51.41) < 1e-9, f"hand buy cost {buy_cost}"
    # sell adds stamp 5bp = 50
    sell_cost = _side_cost(100_000.0, stock_fee, slip2, True)
    assert abs(sell_cost - 101.41) < 1e-9, f"hand sell cost {sell_cost}"
    # min-commission floor: tiny 4000 CNY ticket, comm = max(5, 1) = 5
    tiny = _side_cost(4_000.0, stock_fee, kr.cost_v2_slippage(2e8), False)
    assert abs(tiny - 7.2564) < 1e-9, f"min-commission floor hand-value {tiny}"
    ok += 1
    # S9: ADV fill cap + lot rounding faces
    adv = 5e7                     # 5e7 < 1e8 -> 10bp tier; cap = 1%*adv/px
    px = 10.0
    cap_shares = (int((K_ADV_CAP * adv) / px) // 100) * 100
    assert cap_shares == 50_000, "cap lot-rounded (1% ADV at px=10)"
    assert K_ADV_CAP == kr.ADV_FILL_CAP_RATE, "ADV cap constant mirrors rules.py"
    demand = int(1_000_000.0 / 10 / px / 100) * 100
    assert demand == 10_000, f"lot-rounded demand {demand}"
    ok += 1
    # S10: suspension entry-skip / resume-day exit on a synthetic market
    n_cal = 12
    sig_pos = [4]
    # code A: bar on exec day (pos 5); code B: suspended at exec (pos 5),
    # resumes pos 8 -> exit at resume open
    mkt = {
        "A": (np.array([4, 5, 6, 7, 8, 9, 10, 11], dtype=np.int64),
              np.array([10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0]),
              np.array([10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0]),
              _ffill_np(np.array([4, 5, 6, 7, 8, 9, 10, 11]),
                        np.array([10.0] * 8), n_cal)),
        "B": (np.array([0, 1, 2, 3, 8, 9, 10, 11], dtype=np.int64),
              np.array([5.0, 5.0, 5.0, 5.0, 6.0, 6.0, 6.0, 6.0]),
              np.array([5.0, 5.0, 5.0, 5.0, 6.0, 6.0, 6.0, 6.0]),
              _ffill_np(np.array([0, 1, 2, 3, 8, 9, 10, 11]),
                        np.array([5.0, 5.0, 5.0, 5.0, 6.0, 6.0, 6.0, 6.0]), n_cal)),
    }
    sel = [[("A", 6e8), ("B", 6e8)]]  # single month: buy both at exec pos 5
    rep = _sim_cell(sel, mkt, sig_pos, n_cal, 0, stock_fee,
                    lambda c, m: kr.cost_v2_slippage(6e8))
    # B suspended on exec day 5 -> skipped (n_skip_entry), only A bought
    assert rep["n_skip_entry"] == 1 and "A" in rep["open_at_end"], "entry skip"
    ok += 1
    # S11: suspended exit -> resume-day open fill (exit not at stale close)
    sig_pos2 = [0]
    sel2 = [[("B", 6e8)]]
    mkt2 = {"B": mkt["B"]}
    rep2 = _sim_cell(sel2, mkt2, sig_pos2, n_cal, 0, stock_fee,
                     lambda c, m: kr.cost_v2_slippage(6e8))
    assert rep2["n_buys"] == 1, "B entered at pos 1"
    # now force an exit while suspended: select nothing next month at pos 5+
    sig_pos3 = [0, 4]
    sel3 = [[("B", 6e8)], []]           # month1 empty cohort -> sell B at exec 5
    rep3 = _sim_cell(sel3, mkt2, sig_pos3, n_cal, 0, stock_fee,
                     lambda c, m: kr.cost_v2_slippage(6e8))
    # B suspended on exec day 5 -> pending exit -> filled at resume pos 8 open 6.0
    assert rep3["n_sells"] == 1 and rep3["open_at_end"] == {}, "resume exit"
    assert abs(rep3["eq"][8] - rep3["eq"][7]) > 0, "exit realized cash on resume day"
    ok += 1
    # S12: ledger arithmetic face (append_ledger is pure-dict, no side effects)
    import science_gates as sg
    led = sg.append_ledger("SELFTEST-EXCLUSION", 16, "selftest",
                           prev_total=100, evidence_cutoff=EVIDENCE_CUTOFF)
    assert led["prev_total"] == 100 and led["batch_trials"] == 16
    assert led["total"] == 116, "chain arithmetic"
    ok += 1
    # S13: closed-family gate open for our family key
    chk = sg.closed_family_check("exclusion_marginal_p1")
    assert chk["status"] == "open", f"family gate {chk}"
    ok += 1
    # S14: seed registry law -- SEED_KEY must be registered (禁现编)
    assert SEED_KEY in sg.SEED_REGISTRY, "seed registered"
    assert sg.SEED_REGISTRY[SEED_KEY] == 20329500, "seed value pinned"
    ok += 1
    # S15: determinism -- identical replay twice = byte-identical equity
    r1b = _sim_cell(sel3, mkt2, sig_pos3, n_cal, 0, stock_fee,
                    lambda c, m: kr.cost_v2_slippage(6e8))
    assert np.array_equal(np.nan_to_num(rep3["eq"]), np.nan_to_num(r1b["eq"]))
    ok += 1
    # S16: cost_spec frozen face intact (CN-C7 roundtrip derivation premise)
    from knowledge import cost_spec
    assert cost_spec.verify(), "cost_spec frozen face"
    ok += 1
    print(f"selftest: {ok}/16 PASS (hermetic; engine legs S6-S16 landed r476)")
    return 0


def _ffill_np(mpos: np.ndarray, close: np.ndarray, n_cal: int) -> np.ndarray:
    """Forward-filled close over the full calendar grid (marking face)."""
    out = np.full(n_cal, np.nan)
    out[mpos] = close
    valid = ~np.isnan(out)
    idx = np.where(valid, np.arange(n_cal), -1)
    np.maximum.accumulate(idx, out=idx)
    out = np.where(idx >= 0, out[np.clip(idx, 0, n_cal - 1)], np.nan)
    out[~valid & (idx < 0)] = np.nan
    return out


# --------------------------------------------------------------------------
# run (full burn, engine landed r476)
# --------------------------------------------------------------------------
def _burn_gates(probe_f: dict) -> tuple[bool, dict]:
    """FAIL-CLOSED burn gates (prereg sec.2 data-completeness + law faces)."""
    rep: dict = {}
    # G1 probe same-face assertions (bit-for-bit path + count pin)
    af = probe_f.get("anchor_faces", {})
    if (af.get("panel", {}).get("path") != "data/astock_daily/per/<code>.csv"
            or af.get("eligibility", {}).get("path") != "data/fundamental/eligibility.csv"
            or af.get("b_layer_mask", {}).get("path") != "data/fundamental/b_layer_mask.csv"):
        rep["face_mismatch"] = "anchor paths"
        return False, rep
    files = sorted(os.listdir(PANEL_DIR))
    if len(files) != probe_f.get("panel_files"):
        rep["face_mismatch"] = f"panel_files {len(files)} != {probe_f.get('panel_files')}"
        return False, rep
    codes = _load_codes()
    if len(codes) != probe_f.get("eligibility_codes"):
        rep["face_mismatch"] = f"eligibility_codes {len(codes)} != {probe_f.get('eligibility_codes')}"
        return False, rep
    rep["panel_files"] = len(files)
    rep["eligibility_codes"] = len(codes)
    # G2 panel complete + cutoff fresh enough
    st = json.load(open(ASTOCK_STATUS, encoding="utf-8"))
    panel = st.get("panel", {})
    if not panel.get("complete") or panel.get("cutoff", "") < EVIDENCE_CUTOFF:
        rep["panel_gate"] = panel
        return False, rep
    rep["panel_status_cutoff"] = panel.get("cutoff")
    # G3 eligibility snapshot < 24h
    age_h = (time.time() - os.path.getmtime(ELIG_CSV)) / 3600.0
    if age_h > 24.0:
        rep["eligibility_age_h"] = round(age_h, 1)
        return False, rep
    rep["eligibility_age_h"] = round(age_h, 1)
    # G4 closed-family tripwire
    import science_gates as sg
    chk = sg.closed_family_check("exclusion_marginal_p1")
    rep["closed_family"] = chk["status"]
    if chk["status"] == "rejected":
        return False, rep
    # G5 seed-registry law (禁现编 -- registration must predate the burn)
    if SEED_KEY not in sg.SEED_REGISTRY:
        rep["seed_missing"] = SEED_KEY
        return False, rep
    # G6 cost_spec frozen face + ADV-cap constant mirror (drift guard)
    from knowledge import cost_spec
    from knowledge import rules as _kr
    rep["cost_spec_verify"] = cost_spec.verify()
    rep["adv_cap_mirror"] = (K_ADV_CAP == _kr.ADV_FILL_CAP_RATE)
    if not rep["cost_spec_verify"] or not rep["adv_cap_mirror"]:
        return False, rep
    # G7 double-count guard (idempotent burn)
    if os.path.exists(SCAN_FILE) and os.environ.get("EXCLUSION_MARGINAL_REBURN") != "1":
        rep["already_burned"] = True
        return False, rep
    return True, rep


def run() -> int:
    t0 = time.time()
    if not os.path.exists(PROBE_FILE):
        print("run: FAIL-CLOSED -- probe facts missing (run probe first).")
        return 2
    probe_f = json.load(open(PROBE_FILE, encoding="utf-8"))
    if os.path.exists(SCAN_FILE) and os.environ.get("EXCLUSION_MARGINAL_REBURN") != "1":
        print("run: already burned -- scan.json present, no-op (idempotency guard).")
        print("     redo channel = EXCLUSION_MARGINAL_REBURN=1 (fresh prereg for re-burns).")
        return 0
    ok, gates_rep = _burn_gates(probe_f)
    if not ok:
        print("run: FAIL-CLOSED -- burn gate refused (honest, zero-burn):")
        print(json.dumps(gates_rep, ensure_ascii=False, indent=1))
        return 2

    import science_gates as sg
    from knowledge import rules as kr

    # ---- calendar + signals ----
    cal, _ = _load_calendar()
    cutoff_pos = max(i for i, d in enumerate(cal) if d <= EVIDENCE_CUTOFF)
    cal = cal[: cutoff_pos + 1]                      # rows actually read <= cutoff
    cal_pos_of = {d: i for i, d in enumerate(cal)}
    cal_start = cal[0]  # calendar face start (2005-02-23); pre-face stock history is expected-unmapped, not a face error
    sig_dates, sig_pos_full = _signal_schedule(_load_calendar()[0])
    n_cal = len(cal)
    # signals must live inside the truncated grid; exec positions likewise
    sig_pos = [p for p in sig_pos_full if p + 1 < n_cal]
    sig_dates = [d for d, p in zip(sig_dates, sig_pos_full) if p + 1 < n_cal]
    n_sig = len(sig_pos)

    # ---- universe: per-code intersection pinned (probe -1 drift candidate) ----
    from firm.risk import b_layer_filter as blf
    elig = blf.load_eligibility(ELIG_CSV)
    mask = blf.load_mask(MASK_CSV)
    panel_codes = {f[:-4] for f in os.listdir(PANEL_DIR) if f.endswith(".csv")}
    codes = sorted(c for c in elig.index
                   if len(c) == 6 and c[0] in ("0", "3", "6")
                   and c in panel_codes and c in mask.index)
    gates_rep["burn_universe"] = len(codes)
    code_idx = {c: i for i, c in enumerate(codes)}
    n_codes = len(codes)

    # ---- feature extraction (single pass, compact matrices) ----
    AMT = np.full((n_codes, n_sig), np.nan)
    CLOSE = np.full((n_codes, n_sig), np.nan)
    CNT = np.full((n_codes, n_sig), np.nan)
    STALE = np.full((n_codes, n_sig), np.inf)
    for c in codes:
        p = f"{c}.csv"
        df = pd.read_csv(os.path.join(PANEL_DIR, p),
                         usecols=["date", "open", "close", "amount"])
        df = df[df["date"] <= EVIDENCE_CUTOFF]       # RW-2 truncation face
        amt20_full = df["amount"].rolling(20).mean().to_numpy()
        cnt_full = np.arange(1, len(df) + 1, dtype=np.float64)
        dates = df["date"].astype(str).tolist()
        mpos_l, o_l, cl_l, a_l, cnt_l = [], [], [], [], []
        unmapped = 0
        for j, d in enumerate(dates):
            q = cal_pos_of.get(d)
            if q is None:
                if d >= cal_start:   # only in-coverage unmapped rows are face errors
                    unmapped += 1
                continue
            mpos_l.append(q); o_l.append(df["open"].iat[j])
            cl_l.append(df["close"].iat[j]); a_l.append(amt20_full[j])
            cnt_l.append(cnt_full[j])
        if unmapped:
            gates_rep["unmapped_rows"] = {c: unmapped}
            print("run: FAIL-CLOSED -- calendar-unmapped post-2005 rows (face error VOID).")
            return 2
        if not mpos_l:
            continue
        mpos = np.asarray(mpos_l, dtype=np.int64)
        idx = np.searchsorted(mpos, np.asarray(sig_pos), side="right") - 1
        has = idx >= 0
        ii = np.where(has, idx, 0)
        i = code_idx[c]
        AMT[i] = np.where(has, np.asarray(a_l)[ii], np.nan)
        CLOSE[i] = np.where(has, np.asarray(cl_l)[ii], np.nan)
        CNT[i] = np.where(has, np.asarray(cnt_l)[ii], np.nan)
        STALE[i] = np.where(has, np.asarray(sig_pos) - mpos[ii], np.inf)

    r1 = elig.loc[codes, "r1_loss"].astype(bool).to_numpy()
    r2 = elig.loc[codes, "r2_st"].astype(bool).to_numpy()
    seed_base = int(sg.SEED_REGISTRY[SEED_KEY])

    # ---- per-cell selection + simulation ----
    start_months: dict[int, int] = {}
    for y in START_YEARS:
        first_day = next(d for d in cal if d[:4] == str(y) and d[5:7] == "01")
        p = cal.index(first_day)
        start_months[y] = next(m for m, sp in enumerate(sig_pos) if sp >= p)

    stock_fee = kr.fee_schedule_for("600000")
    cache: dict[str, tuple] = {}

    def mkt(code: str) -> tuple:
        if code not in cache:
            df = pd.read_csv(os.path.join(PANEL_DIR, f"{code}.csv"),
                             usecols=["date", "open", "close"])
            df = df[df["date"] <= EVIDENCE_CUTOFF]
            # drop rows outside the calendar face (pre-2005 listing history):
            # unreachable for execution (signals 2007+, exec at signal+1) and
            # bare cal_pos_of[d] would KeyError; cnt_full age face (feature pass)
            # is computed on the UNTRUNCATED df -- frozen sec.2 full-history
            # age250 semantics are NOT touched by this execution-array filter.
            _keep = df["date"].astype(str).isin(cal_pos_of)
            df = df[_keep]
            mpos = np.array([cal_pos_of[d] for d in df["date"].astype(str)],
                            dtype=np.int64)
            opens = df["open"].to_numpy()
            closes = df["close"].to_numpy()
            cache[code] = (mpos, opens, closes, _ffill_np(mpos, closes, n_cal))
        return cache[code]

    def slip_of(code: str, m: int) -> float:
        i = code_idx[code]
        adv = AMT[i, m] if m < n_sig else np.nan
        return kr.cost_v2_slippage(adv if adv == adv else None)

    cells_out = {}
    cohorts_by_cell = {}
    for cell in CELLS:
        name = cell["cell"]
        sel = _build_selection(AMT, CLOSE, CNT, STALE, r1, r2, cell,
                               seed_base if cell.get("base") == "random" else None)
        cohorts_by_cell[name] = sel
        sel_named = [[(codes[i], adv) for i, adv in s] if s else []
                     for s in sel]
        # full-history replay (start 2007)
        rep = _sim_cell(sel_named, mkt, sig_pos, n_cal, 0, stock_fee, slip_of)
        met = _metrics(rep, cal, sig_pos[0])
        # all-starts
        starts = {}
        for y in START_YEARS:
            m0 = start_months[y]
            rp = _sim_cell(sel_named, mkt, sig_pos, n_cal, m0, stock_fee, slip_of)
            d0 = sig_pos[m0]
            days = n_cal - d0
            yrs = days / 244.0
            starts[str(y)] = {
                "ann_ret_net": (float(rp["eq"][-1]) / INITIAL_CASH) ** (1.0 / yrs) - 1.0,
            }
        vals = np.array([v["ann_ret_net"] for v in starts.values()])
        cells_out[name] = {
            "off_rules": cell.get("off", []),
            "base": cell.get("base", "rank"),
            "full_period": met,
            "allstarts_ann_ret_net": {k: v["ann_ret_net"] for k, v in starts.items()},
            "allstart_best": float(vals.max()), "allstart_worst": float(vals.min()),
            "allstart_p25": float(np.percentile(vals, 25)),
            "allstart_median": float(np.median(vals)),
            "allstart_p75": float(np.percentile(vals, 75)),
        }

    # ---- M1 marginal verdicts (prereg sec.4 frozen) ----
    def dist(a: str, b: str):
        da = np.array([cells_out[a]["allstarts_ann_ret_net"][str(y)]
                       for y in START_YEARS])
        db = np.array([cells_out[b]["allstarts_ann_ret_net"][str(y)]
                       for y in START_YEARS])
        return da - db

    verdicts = {}
    for rname in RULES:
        d = dist("FULL", f"LOO-{rname}")
        dp = dist(f"AOI-{rname}", "NONE")
        full_d = cells_out["FULL"]["full_period"]["ann_ret_net"] - \
            cells_out[f"LOO-{rname}"]["full_period"]["ann_ret_net"]
        full_dp = cells_out[f"AOI-{rname}"]["full_period"]["ann_ret_net"] - \
            cells_out["NONE"]["full_period"]["ann_ret_net"]
        verdicts[rname] = {
            "loo_delta": {"full_period": full_d,
                          "pos_share_allstarts": float((d > 0).mean()),
                          "median_allstarts": float(np.median(d)),
                          "verdict_positive": bool(full_d > 0 and (d > 0).mean() >= 0.50
                                                   and np.median(d) > 0)},
            "aoi_delta": {"full_period": full_dp,
                           "pos_share_allstarts": float((dp > 0).mean()),
                           "median_allstarts": float(np.median(dp)),
                           "verdict_positive": bool(full_dp > 0 and (dp > 0).mean() >= 0.50
                                                    and np.median(dp) > 0)},
            "delta_maxdd_full": cells_out["FULL"]["full_period"]["maxdd"]
                - cells_out[f"LOO-{rname}"]["full_period"]["maxdd"],
            "delta_sharpe_full": cells_out["FULL"]["full_period"]["sharpe"]
                - cells_out[f"LOO-{rname}"]["full_period"]["sharpe"],
        }
    # cohort overlap descriptive (mean |cohort_m ∩ cohort_m+1| / N)
    ov = {}
    for name, sel in cohorts_by_cell.items():
        ovs = []
        for m in range(len(sel) - 1):
            a = {i for i, _ in sel[m]} if sel[m] else set()
            b = {i for i, _ in sel[m + 1]} if sel[m + 1] else set()
            ovs.append(len(a & b) / N_HOLDINGS)
        ov[name] = float(np.mean(ovs)) if ovs else None
    gates_rep["cohort_overlap_mean"] = ov

    # ---- ledger BEFORE dump (r474 embed-order law) ----
    ledger = sg.append_ledger("EXCLUSION-MARGINAL-P1", len(CELLS),
                              "exclusion_marginal_scan",
                              evidence_cutoff=EVIDENCE_CUTOFF)
    # derived cost faces (CN-C7: derive, never hand-copy)
    from knowledge import cost_spec
    stock_ref = kr.fee_schedule_for("600000")
    cost_faces = {
        "stock_ref_code": "600000",
        "roundtrip_bp_by_adv_tier": {
            f"{tier}_yuan_adv": {
                "buy_side_bp": round(kr.cost_v2_side_rate(float(tier_v), stock_ref) * 1e4, 4),
                "sell_side_bp": round(kr.cost_v2_sell_side_rate(float(tier_v), stock_ref) * 1e4, 4),
            } for tier, tier_v in (("adv_ge_5e8", 6e8), ("adv_1e8_5e8", 2e8), ("adv_lt_1e8", 5e7))
        },
        "adv_fill_cap_rate": kr.ADV_FILL_CAP_RATE,
        "cost_spec_verify": cost_spec.verify(),
    }
    payload = {
        "schema": "exclusion_marginal_scan_v1",
        "order_ref": "D-20260930-41 deliverable #3 (RETAIL_QUANT_TRACK sec.2 #3)",
        "science_gates": {"cutoff_meta": sg.cutoff_meta(EVIDENCE_CUTOFF)},
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "trials_ledger": ledger,
        "burn_gates_report": gates_rep,
        "signal_months": n_sig,
        "signal_first_last": [sig_dates[0], sig_dates[-1]],
        "base_params": BASE_PARAMS,
        "cost_faces": cost_faces,
        "cells": cells_out,
        "m1_verdicts": verdicts,
        "engine_faces": {
            "calendar": "data/daily/sh510050.csv (2005-02-23+ full-history member)",
            "sleeve_target": "signal-day-close equity / 10",
            "lots": "100-share A-share lots (buy side)",
            "cash": "no interest on cash sleeves",
            "final_cohort": "held open at evidence cutoff (partial month, honest)",
            "overlap": "names re-selected held without trade (classical rotation)",
            "exit_slippage_adv": "exit month's selection-signal ADV (no-lookahead)",
        },
        "burn_audit": {"elapsed_sec": round(time.time() - t0, 1),
                       "n_cached_names": len(cache)},
    }
    os.makedirs(RES_DIR, exist_ok=True)
    with open(SCAN_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1, sort_keys=True)
    # scan_cells.csv
    with open(CELLS_FILE, "w", encoding="utf-8", newline="\n") as f:
        f.write("cell,ann_ret_net,maxdd,sharpe,turnover_ann,cost_drag_ann,"
                "allstart_median,allstart_p25,allstart_p75,worst_3y,worst_5y,worst_10y\n")
        for name, c in cells_out.items():
            fp = c["full_period"]
            f.write(f"{name},{fp['ann_ret_net']:.6f},{fp['maxdd']:.6f},"
                    f"{fp['sharpe']:.4f},{fp['turnover_ann'] or 0:.4f},"
                    f"{fp['cost_drag_ann'] or 0:.6f},{c['allstart_median']:.6f},"
                    f"{c['allstart_p25']:.6f},{c['allstart_p75']:.6f},"
                    f"{fp['worst_3y'] if fp['worst_3y'] is not None else ''},"
                    f"{fp['worst_5y'] if fp['worst_5y'] is not None else ''},"
                    f"{fp['worst_10y'] if fp['worst_10y'] is not None else ''}\n")
    # gate_attrition append (measurement row, append-only face)
    if os.path.exists(ATTR_FILE):
        with open(ATTR_FILE, encoding="utf-8") as f:
            attr = json.load(f)
        attr["entries"].append({
            "batch": "EXCLUSION-MARGINAL-P1",
            "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
            "kind": "measurement",
            "cells_ledger_delta": len(CELLS),
            "ledger_total_after": ledger["total"],
            "gates": {
                "burn_gates_all_pass": True,
                "m1_loo_positive_rules": sorted(
                    [r for r, v in verdicts.items() if v["loo_delta"]["verdict_positive"]]),
                "m1_aoi_positive_rules": sorted(
                    [r for r, v in verdicts.items() if v["aoi_delta"]["verdict_positive"]]),
                "void": False,
            },
            "eliminated": None,
            "refs": {"results": "results/exclusion_marginal_scan/scan.json",
                     "prereg": "research/EXCLUSION_MARGINAL_PREREG.md"},
        })
        with open(ATTR_FILE, "w", encoding="utf-8") as f:
            json.dump(attr, f, ensure_ascii=False, indent=1)
    print(f"burn COMPLETE: {len(CELLS)} cells | ledger {ledger['prev_total']} -> {ledger['total']}")
    print(f"  signals {sig_dates[0]} .. {sig_dates[-1]} ({n_sig} months) | universe {n_codes}")
    print(f"  products: {SCAN_FILE} + {CELLS_FILE} | elapsed {payload['burn_audit']['elapsed_sec']}s")
    return 0


def main() -> int:
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "probe":
        return probe()
    if cmd == "selftest":
        return selftest()
    if cmd == "run":
        return run()
    print("usage: python scripts/exclusion_marginal_scan.py {probe|selftest|run}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
