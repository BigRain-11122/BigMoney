"""BOND_CARRY_WAVE3A batch runner -- 交易所国债折价收敛袖 (clean-price face).

Prereg: research/BOND_CARRY_WAVE3A_PREREG.md (frozen R207, git-blob sha1
89973100924a3602786c27edf5c41047f89f703c; integrity asserted at run,
CRLF->LF normalized per R140 law; blob sha is content-addressed = rebase-safe).
Cells (prereg sec.0, N_eff=35, all in D1 correction burden):
  C1  judgment cell   = discount-convergence sleeve (top-20 ADV20, close<100)
  C2  attribution     = same sleeve, no discount gate (top-20 by ADV20)
  C3  attribution     = discount gate, no ranking (all ADV20>=500k discounts)
  K=32 random member-mask nulls (seed SEED_REGISTRY["bond_carry_w3a"]=66_000+k)
  +   2 passives (510300 buy-hold cross-asset anchor + in-domain cap-bounded
      EW monthly passive = the bond_w3a skill-line pool anchor, sec.4)

Mechanics (prereg sec.3, frozen): monthly rebalance (eval at month's last
panel-day close, execute next panel-day open), per-member position
min(10k, 1%*ADV20) with <2.5k deferral, convergence TP close>=100, face
termination at the member's last bar close, hard bounds (20d cum <= -8% /
HWM dd <= -10%: cut whole sleeve at next open, lock re-entry to the next
monthly eval; |r| >= 3% crisis log), V2 costs (knowledge/rules.py; judgment
face = fee x2 always on, CostPatch single-source semantics; x1/x3 = disclosure
columns), yuan-denominated deployed-capital return face (out-of-market days
= 0.0 return = the prereg sec.4 full-timeline Sharpe basis; idle-cash
convention disclosed in meta).

Subcommands:
  gates    G0 smoke / G1 prereg integrity / G2 panel complete (6/6 shards
           resolved + manifest coverage) / G3 per-member completeness +
           R178 12% breakpoint scan + window rule / G4 frozen evidence
           (capacity probe + CLEAN semantics verdict + seed registry)
  run      full batch (gates re-run inside; aborts exit 2 on any FAIL)
  status   panel/shard inventory read (monitoring face)
  selftest offline unit tests (synthetic panels; no data files needed)

Ledger: science_gates.append_ledger("BOND_CARRY_WAVE3A", 35,
          "results/bond_carry_w3a.json", evidence_cutoff="2026-09-24").
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "screening"))

import numpy as np
import pandas as pd

import science_gates as sg
from knowledge.rules import FeeSchedule, cost_v2_slippage
from pbo import cscv_pbo, align_returns

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREREG_PATH = os.path.join(ROOT, "research", "BOND_CARRY_WAVE3A_PREREG.md")
MANIFEST_JSON = os.path.join(ROOT, "results", "bond_w3a", "candidates.json")
REGISTRY_JSON = os.path.join(ROOT, "results", "bond_w3a", "member_registry.json")
SHARD_DIR = os.path.join(ROOT, "results", "bond_w3a")
DATA_DIR = os.path.join(ROOT, "data", "bond_w3a")
RESULTS_JSON = os.path.join(ROOT, "results", "bond_carry_w3a.json")
ATTRITION_JSON = os.path.join(ROOT, "results", "gate_attrition.json")
ETF_510300_CSV = os.path.join(ROOT, "data", "daily", "510300.csv")
CAPACITY_EVIDENCE = os.path.join(ROOT, "results", "bond_capacity_wave3a.json")
SEMANTICS_EVIDENCE = os.path.join(ROOT, "results", "bond_price_semantics_w3a.json")

CUTOFF = "2026-09-24"              # evidence_cutoff (2026-09-25 Mid-Autumn, no bar)
ERA_FLOOR = "2003-06-01"            # CLEAN semantics verified-era floor (prereg sec.2)
FROZEN_PREREG_BLOB_SHA = "89973100924a3602786c27edf5c41047f89f703c"
SEED_BASE = 66_000                  # SEED_REGISTRY["bond_carry_w3a"] (frozen pre-run R207)
K_NULLS = 32
BATCH_CELLS = 35                    # C1+C2+C3 + K32 (prereg sec.0)
TOP_N = 20
ADV_FLOOR_YUAN = 500_000.0          # candidate liquidity floor (r206 probe lower band)
POS_BASE_YUAN = 10_000.0            # per-member position base (prereg 200k/20 anchor)
DEFER_FLOOR_YUAN = 2_500.0          # 1%*ADV20 below this -> deferral (frozen residual guard)
CONVERGENCE_PAR = 100.0             # pull-to-par take-profit face
BOUND_20D_CUM = -0.08               # hard bound (a): 20d rolling cumulative
BOUND_HWM_DD = -0.10                # hard bound (b): HWM drawdown
CRISIS_DAY_ABS = 0.03               # crisis log threshold (bond scale)
BP_ABS = 0.12                       # R178 structural breakpoint scan threshold
K_NOTIONAL = 0.99998                # volume->notional calibration (r206 frozen)
MIN_BARS = 60
MIN_MEMBERS_START = 10              # window-start data-availability rule
START_CASH = 10_000_000.0           # uniform accounting headroom (disclosed; the
                                    # deployed-face returns are cash-independent)
COST_JUDGMENT_MULT = 2.0            # judgment face = fee x2 always on (prereg sec.3)
N_CSCV_BLOCKS = 8
FEES_PER_SIDE = (FeeSchedule().commission_rate
                 + FeeSchedule().handling_fee
                 + FeeSchedule().supervision_fee)   # single source, no hand-copy


def side_rate(adv20_yuan, mult: float) -> float:
    """V2 per-side rate: mult x fixed fees + ADV20-tier slippage (judgment mult=2)."""
    return float(mult) * FEES_PER_SIDE + cost_v2_slippage(adv20_yuan)


def prereg_blob_sha() -> str:
    b = open(PREREG_PATH, "rb").read().replace(b"\r\n", b"\n")
    return hashlib.sha1(b"blob %d\0" % len(b) + b).hexdigest()


def size_member(adv20_yuan: float):
    """Frozen sec.3 sizing: min(10k, 1%*ADV20); <2.5k -> (None, True) = deferred.
    Note: under the 500k candidacy floor 1%*ADV20 >= 5k > 2.5k, so deferrals
    are structurally unreachable for candidates -- the rule stays as the
    frozen residual guard and the batch discloses the count honestly."""
    yuan = min(POS_BASE_YUAN, 0.01 * float(adv20_yuan))
    if yuan < DEFER_FLOOR_YUAN:
        return None, True
    return yuan, False


# ---------------------------------------------------------------- panel

def prep_panel(raw: dict) -> dict:
    """Single code path for production panel and selftest fixtures (r157 law):
    raw per-member frames -> calendar + numpy faces + adv20/bars ffills."""
    codes = sorted(raw)
    calendar = sorted({d for df in raw.values() for d in df.index})
    cal = pd.DatetimeIndex(calendar)
    T, M = len(cal), len(codes)
    close = np.full((T, M), np.nan)
    open_ = np.full((T, M), np.nan)
    volume = np.full((T, M), np.nan)
    row_of = {d: i for i, d in enumerate(cal)}
    bar_rows: list[list[int]] = []
    for j, c in enumerate(codes):
        df = raw[c].sort_index()
        rows = [row_of[d] for d in df.index]
        bar_rows.append(rows)
        close[rows, j] = df["close"].to_numpy(dtype=float)
        open_[rows, j] = df["open"].to_numpy(dtype=float)
        volume[rows, j] = df["volume"].to_numpy(dtype=float)
    close_ff = np.full((T, M), np.nan)
    adv20_ff = np.full((T, M), np.nan)
    bars_cal = np.zeros((T, M), dtype=np.int64)
    last_bar_row = np.full(M, -1, dtype=np.int64)
    for j, rows in enumerate(bar_rows):
        if not rows:
            continue
        r = np.asarray(rows)
        cl = close[r, j]
        notional = volume[r, j] * cl * K_NOTIONAL
        a = np.full(len(r), np.nan)
        if len(r) >= 20:
            csum = np.cumsum(notional)
            a[19:] = (csum[19:] - np.concatenate(([0.0], csum[:-20]))) / 20.0
        last_bar_row[j] = int(r[-1])
        close_ff[:, j] = pd.Series(cl, index=cal[r]).reindex(cal).ffill().to_numpy()
        adv20_ff[:, j] = pd.Series(a, index=cal[r]).reindex(cal).ffill().to_numpy()
        bars_cal[:, j] = (pd.Series(np.arange(1, len(r) + 1), index=cal[r])
                          .reindex(cal).ffill().fillna(0).to_numpy())
    tradable = np.isfinite(volume) & (volume > 0)
    return {"codes": codes, "cal": cal, "close": close, "open": open_,
            "volume": volume, "tradable": tradable, "close_ff": close_ff,
            "adv20_ff": adv20_ff, "bars_cal": bars_cal,
            "bar_rows": bar_rows, "last_bar_row": last_bar_row}


def load_manifest() -> list[str]:
    with open(MANIFEST_JSON, encoding="utf-8") as fh:
        m = json.load(fh)
    if int(m.get("n_candidates", -1)) != len(m.get("candidates", [])):
        raise ValueError("manifest n_candidates != len(candidates) -- schema drift")
    return [c["code"] for c in m["candidates"]]


def load_panel(data_dir: str = DATA_DIR):
    manifest = load_manifest()
    raw, missing = {}, []
    for code in manifest:
        p = os.path.join(data_dir, f"{code}.csv")
        if os.path.exists(p):
            raw[code] = pd.read_csv(p, index_col=0, parse_dates=True)
        else:
            missing.append(code)
    return prep_panel(raw), missing


# ---------------------------------------------------------------- R178 scan + window

def scan_breakpoints(panel: dict, i0: int, i1: int) -> dict:
    """|overnight| > 12% breakpoint list + in-span hole enumeration (R178/r186:
    in-span full enumeration, pre-listing count-only). Both faces scanned:
    open_t/close_{t-1}-1 (literal overnight) and close_t/close_{t-1}-1 (the
    daily face contains the overnight); union list, formula disclosed."""
    events: list[dict] = []
    in_span_holes: list[tuple] = []
    pre_listing: dict[str, int] = {}
    cal = panel["cal"]
    for j, c in enumerate(panel["codes"]):
        rows = [r for r in panel["bar_rows"][j] if i0 <= r <= i1]
        if not rows:
            continue
        first = rows[0]
        pre_listing[c] = max(0, first - i0)
        own = set(rows)
        in_span_holes.extend((c, str(cal[r].date())) for r in range(first, i1 + 1) if r not in own)
        cl = panel["close"][rows, j]
        op = panel["open"][rows, j]
        for k in range(1, len(rows)):
            on = op[k] / cl[k - 1] - 1.0
            cc = cl[k] / cl[k - 1] - 1.0
            if abs(on) > BP_ABS or abs(cc) > BP_ABS:
                events.append({"code": c, "date": str(cal[rows[k]].date()),
                               "overnight_ret": round(on, 6), "daily_ret": round(cc, 6)})
    return {"threshold_abs": BP_ABS,
            "formula": "|open_t/close_{t-1}-1|>0.12 OR |close_t/close_{t-1}-1|>0.12",
            "events": events, "n_events": len(events),
            "in_span_holes": in_span_holes, "in_span_holes_n": len(in_span_holes),
            "pre_listing_absence_days": pre_listing}


def whitelist_firsts(scan: dict) -> dict:
    """First event date per member (12% = data-corruption tripwire per prereg
    sec.2; real market extremes sit far below and flow to the crisis-log face).
    In-batch local handling, corpus untouched: the member is excluded from
    every selection set at/after its first event; an open position force-exits
    at the event-day close (no lookahead: the event is visible at that close)."""
    firsts: dict[str, str] = {}
    for e in scan["events"]:
        c = e["code"]
        if c not in firsts or e["date"] < firsts[c]:
            firsts[c] = e["date"]
    return firsts


def determine_window(panel: dict) -> dict:
    """start = max(ERA_FLOOR, first panel day with >=10 manifest members each
    having >=60 own bars) -- deterministic availability rule (prereg sec.2);
    end = evidence_cutoff (the panel must end exactly there)."""
    cal = panel["cal"]
    i1 = int(np.searchsorted(cal, pd.Timestamp(CUTOFF), side="right")) - 1
    if i1 < 0 or str(cal[i1].date()) != CUTOFF:
        last = str(cal[-1].date()) if len(cal) else None
        raise ValueError(f"panel last bar {last} != evidence_cutoff {CUTOFF}")
    ready = (panel["bars_cal"] >= MIN_BARS).sum(axis=1)
    hit = ready >= MIN_MEMBERS_START
    if not hit.any():
        raise ValueError("no panel day with >=10 members x >=60 bars")
    i0_data = int(np.argmax(hit))
    i0_floor = int(np.searchsorted(cal, pd.Timestamp(ERA_FLOOR), side="left"))
    i0 = max(i0_floor, i0_data)
    return {"i0": i0, "i1": i1, "start": str(cal[i0].date()), "end": str(cal[i1].date()),
            "era_floor": ERA_FLOOR, "first_10x60_day": str(cal[i0_data].date()),
            "era_floor_binds": bool(i0_floor >= i0_data)}


def eval_rows(cal: pd.DatetimeIndex, i0: int, i1: int) -> list[int]:
    """Monthly eval rows = month-last panel rows STRICTLY BEFORE i1 (the
    rebalance executes at the next panel day's open; the final row's orders
    would be unfillable, so the last month's composition freezes -- disclosed)."""
    out = []
    for i in range(i0, min(i1, len(cal) - 1)):
        if (cal[i + 1].year, cal[i + 1].month) != (cal[i].year, cal[i].month):
            out.append(i)
    return out


# ---------------------------------------------------------------- eval plans (frozen sec.3)

def build_eval_plans(panel: dict, win: dict, firsts: dict) -> list[dict]:
    """Per monthly eval row: universe / candidates / C1 targets / null pool /
    C2-C3-passive faces. Ranking ties break by code (deterministic)."""
    cal, codes = panel["cal"], panel["codes"]
    adv, cl_ff, bars = panel["adv20_ff"], panel["close_ff"], panel["bars_cal"]
    eligible = np.ones(panel["close"].shape, dtype=bool)
    for j, c in enumerate(codes):
        if c in firsts:
            eligible[:, j] = cal < pd.Timestamp(firsts[c])
    plans = []
    for i in eval_rows(cal, win["i0"], win["i1"]):
        uni = []
        for j in range(len(codes)):
            a = adv[i, j]
            if (not eligible[i, j]) or not np.isfinite(a) or bars[i, j] < MIN_BARS:
                continue
            if a < ADV_FLOOR_YUAN or not np.isfinite(cl_ff[i, j]):
                continue
            uni.append((j, float(a)))
        cands = [(j, a) for (j, a) in uni if cl_ff[i, j] < CONVERGENCE_PAR]
        uni_rank = sorted(uni, key=lambda t: (-t[1], codes[t[0]]))
        cand_rank = sorted(cands, key=lambda t: (-t[1], codes[t[0]]))
        c1_targets, c1_defers = {}, 0
        for j, a in cand_rank[:TOP_N]:
            yuan, deferred = size_member(a)
            if deferred:
                c1_defers += 1
                continue
            c1_targets[codes[j]] = yuan
        adv_by_code = {codes[j]: a for (j, a) in uni}
        plans.append({
            "row": i, "date": str(cal[i].date()),
            "universe_n": len(uni), "candidates_n": len(cands),
            "c1_targets": c1_targets, "c1_n": len(c1_targets), "c1_defers": c1_defers,
            "noncand_pool": [codes[j] for (j, a) in uni if cl_ff[i, j] >= CONVERGENCE_PAR],
            "uni_rank": [(codes[j], a) for (j, a) in uni_rank],
            "cand_all": {codes[j]: size_member(a)[0] for (j, a) in cands
                         if not size_member(a)[1]},
            "adv_by_code": adv_by_code,
        })
    return plans


def targets_c2(plan: dict) -> dict:
    """C2: top-20 by ADV20, NO discount gate; same sizing/deferral."""
    out = {}
    for code, a in plan["uni_rank"][:TOP_N]:
        yuan, deferred = size_member(a)
        if not deferred:
            out[code] = yuan
    return out


def targets_c3(plan: dict) -> dict:
    """C3: discount gate, no ranking (all candidates, cap-bounded EW)."""
    return dict(plan["cand_all"])


def targets_domain_passive(plan: dict) -> dict:
    """In-domain passive: ALL universe members (no price gate, no top-20)."""
    out = {}
    for code, a in plan["uni_rank"]:
        yuan, deferred = size_member(a)
        if not deferred:
            out[code] = yuan
    return out


def make_null_selector(k: int):
    """Null k: at each monthly eval draw c1_n members from the non-candidate
    universe (ADV20>=500k, >=60 bars, close>=100 = universe minus candidates)
    -- numpy.default_rng(66_000+k), one Generator per null across the whole
    run (state carries month to month; the choice call is skipped when
    c1_n==0 -- frozen deterministic semantics)."""
    rng = np.random.default_rng(SEED_BASE + k)

    def selector(plan: dict) -> dict:
        n = plan["c1_n"]
        if n == 0:
            return {}
        pool = sorted(plan["noncand_pool"])
        if not pool:
            return {}
        draw_n = min(n, len(pool))
        picked = rng.choice(np.asarray(pool), size=draw_n, replace=False)
        out = {}
        for code in picked:
            yuan, deferred = size_member(plan["adv_by_code"][str(code)])
            if not deferred:
                out[str(code)] = yuan
        return out
    return selector


# ---------------------------------------------------------------- sleeve simulator

def run_sleeve(panel: dict, plans: list, selector, cost_mult: float, *,
               i0: int, i1: int, tp_convergence: bool, hard_bounds: bool,
               label: str, firsts: dict | None = None) -> dict:
    """Monthly-rebalance sleeve sim on the deployed-capital return face.

    r_i = NAV_diff_i / D_i: NAV_diff = (cash + sum marked val)_i - (..)_{i-1}
    (idle cash cancels: it equals the day's deployed P&L minus the day's
    costs, gaps included); D_i = capital at risk during day i (positions
    held over at their prior-close basis + same-day-open entries/resize
    deltas + open-exit bases). Flat days (D_i == 0) contribute 0.0 (prereg
    sec.4 full-timeline basis). No-bar / zero-volume days are non-tradable
    and non-markable: orders slip to the member's next tradable bar, marks
    carry. Face termination exits at the member's last bar close (prereg
    (iii), settlement uncertainty disclosed). Hard-bound cut sells the whole
    sleeve at next open and locks re-entry until the next monthly eval."""
    cal = panel["cal"]
    codes = panel["codes"]
    code_idx = {c: j for j, c in enumerate(codes)}
    close, open_, vol, trad = panel["close"], panel["open"], panel["volume"], panel["tradable"]
    adv_ff = panel["adv20_ff"]
    last_bar = panel["last_bar_row"]
    firsts = firsts or {}
    firsts_row = {code_idx[c]: int(np.searchsorted(cal, pd.Timestamp(d)))
                  for c, d in firsts.items() if c in code_idx}

    start_row = int(i0)
    end_row = int(i1)
    if plans and (plans[0]["row"] < start_row or plans[-1]["row"] > end_row):
        raise ValueError("eval plans outside the window")

    positions: dict[str, dict] = {}
    pending_set: dict[str, tuple] = {}   # code -> (target_yuan, adv_signal)
    pending_sells: dict[str, tuple] = {}  # code -> (adv_signal, reason)
    locked = False
    cash = float(START_CASH)
    nav_prev = cash
    rets: list[float] = []
    ret_dates: list[str] = []
    # hard-bound monitor runs on the post-cut segment (nav/hwm/20d window reset
    # at each cut): the prereg's cut->lock-to-next-monthly design only operates
    # under a segment-fresh monitor (a persistent HWM/window would re-cut every
    # re-entry forever); the RETURN SERIES stays continuous for all metrics.
    bound_rets: list[float] = []
    nav = 1.0
    hwm = 1.0
    n_entries = n_exits = n_resizes = wins = 0
    traded_gross = 0.0
    costs_by_month: dict[str, float] = {}
    deploy_by_month: dict[str, float] = {}
    cut_log: list[dict] = []
    crisis_log: list[dict] = []
    exit_log: list[dict] = []
    entry_log: list[dict] = []
    cancelled_orders = 0
    monthly_risk_days: dict[str, int] = {}
    plan_by_row = {p["row"]: p for p in plans}

    def _cost(val, adv_sig):
        c = val * side_rate(adv_sig, cost_mult)
        return c

    for i in range(start_row, end_row + 1):
        d = str(cal[i].date())
        mkey = f"{cal[i].year}-{cal[i].month:02d}"
        D = 0.0
        counted: set[str] = set()
        basis: dict[str, float] = {c: positions[c]["val"] for c in positions}
        # ---- open: pending sells (rotation/tp/cut) ----
        for code in list(pending_sells):
            j = code_idx[code]
            if code not in positions:
                pending_sells.pop(code)
                continue
            if not trad[i, j]:
                continue
            adv_sig, reason = pending_sells.pop(code)
            pos = positions.pop(code)
            px = open_[i, j]
            proceeds = pos["units"] * px
            cost = _cost(proceeds, adv_sig)
            cash += proceeds - cost
            traded_gross += proceeds
            costs_by_month[mkey] = costs_by_month.get(mkey, 0.0) + cost
            D += basis[code]
            n_exits += 1
            if proceeds - cost - basis[code] > 0:
                wins += 1
            exit_log.append({"code": code, "date": d, "reason": reason,
                             "price": round(float(px), 4), "basis": round(basis[code], 2)})
        # ---- open: pending entries / resizes ----
        for code in list(pending_set):
            j = code_idx[code]
            if not trad[i, j] or (j in firsts_row and i >= firsts_row[j]):
                if j in firsts_row and i >= firsts_row[j]:
                    pending_set.pop(code)
                continue
            target, adv_sig = pending_set.pop(code)
            px = open_[i, j]
            if code in positions:
                pos = positions[code]
                cur = pos["units"] * px
                delta = target - cur
                if abs(delta) < 1.0:
                    continue
                if delta > 0:
                    cost = _cost(delta, adv_sig)
                    cash -= delta + cost
                    pos["units"] += delta / px
                    traded_gross += delta
                    costs_by_month[mkey] = costs_by_month.get(mkey, 0.0) + cost
                else:
                    amt = -delta
                    cost = _cost(amt, adv_sig)
                    cash += amt - cost
                    pos["units"] -= amt / px
                    traded_gross += amt
                    costs_by_month[mkey] = costs_by_month.get(mkey, 0.0) + cost
                n_resizes += 1
                D += basis[code] + delta
                basis[code] = basis[code] + delta
                counted.add(code)
                pos["val"] = pos["units"] * px
            else:
                cost = _cost(target, adv_sig)
                cash -= target + cost
                positions[code] = {"units": target / px, "val": target}
                traded_gross += target
                costs_by_month[mkey] = costs_by_month.get(mkey, 0.0) + cost
                n_entries += 1
                D += target
                basis[code] = target
                counted.add(code)
                entry_log.append({"code": code, "date": d, "price": round(float(px), 4),
                                  "target_yuan": round(target, 2)})
        # ---- risk capital of untouched held-over positions ----
        for code, b in basis.items():
            if code in positions and code not in counted:
                D += b
        # ---- close: marks + forced exits + TP monitor ----
        for code in list(positions):
            j = code_idx[code]
            has_bar = np.isfinite(close[i, j])
            if has_bar and vol[i, j] > 0:
                positions[code]["val"] = positions[code]["units"] * close[i, j]
            if has_bar and i == last_bar[j]:
                px = close[i, j]                    # terminal settlement face (disclosed)
                adv_sig = adv_ff[i, j]
                pos = positions.pop(code)
                proceeds = pos["units"] * px
                cost = _cost(proceeds, adv_sig)
                cash += proceeds - cost
                traded_gross += proceeds
                costs_by_month[mkey] = costs_by_month.get(mkey, 0.0) + cost
                n_exits += 1
                if proceeds - cost - basis.get(code, pos["val"]) > 0:
                    wins += 1
                exit_log.append({"code": code, "date": d, "reason": "face_term",
                                 "price": round(float(px), 4),
                                 "basis": round(basis.get(code, 0.0), 2)})
                pending_sells.pop(code, None)
                pending_set.pop(code, None)
                continue
            if j in firsts_row and i >= firsts_row[j] and has_bar:
                px = close[i, j]                    # event visible at this close
                adv_sig = adv_ff[i, j]
                pos = positions.pop(code)
                proceeds = pos["units"] * px
                cost = _cost(proceeds, adv_sig)
                cash += proceeds - cost
                traded_gross += proceeds
                costs_by_month[mkey] = costs_by_month.get(mkey, 0.0) + cost
                n_exits += 1
                if proceeds - cost - basis.get(code, pos["val"]) > 0:
                    wins += 1
                exit_log.append({"code": code, "date": d, "reason": "whitelist",
                                 "price": round(float(px), 4),
                                 "basis": round(basis.get(code, 0.0), 2)})
                pending_sells.pop(code, None)
                pending_set.pop(code, None)
                continue
            if tp_convergence and has_bar and vol[i, j] > 0 \
                    and close[i, j] >= CONVERGENCE_PAR and code not in pending_sells:
                pending_sells[code] = (adv_ff[i, j], "tp")
        # ---- daily return on the deployed face ----
        nav_now = cash + sum(p["val"] for p in positions.values())
        diff = nav_now - nav_prev
        r = (diff / D) if D > 0 else 0.0
        rets.append(r)
        ret_dates.append(d)
        nav_prev = nav_now
        if D > 0:
            monthly_risk_days[mkey] = monthly_risk_days.get(mkey, 0) + 1
            deploy_by_month[mkey] = deploy_by_month.get(mkey, 0.0) + D
        # ---- hard bounds + crisis log (close-of-day monitoring) ----
        cut_today = False
        if hard_bounds:
            bound_rets.append(r)
            nav *= (1.0 + r)
            hwm = max(hwm, nav)
            dd = nav / hwm - 1.0
            tail = bound_rets[-20:] if len(bound_rets) >= 20 else bound_rets
            cum20 = 1.0
            for x in tail:
                cum20 *= (1.0 + x)
            cum20 -= 1.0
            trigger = None
            if cum20 <= BOUND_20D_CUM:
                trigger = "20d_cum"
            elif dd <= BOUND_HWM_DD:
                trigger = "hwm_dd"
            if trigger:
                cut_log.append({"date": d, "trigger": trigger,
                                "cum20": round(cum20, 6), "hwm_dd": round(dd, 6),
                                "positions_cut": len(positions)})
                for code in list(positions):
                    pending_sells[code] = (adv_ff[i, code_idx[code]], "cut")
                pending_set.clear()
                locked = True
                cut_today = True
                bound_rets = []       # segment-fresh monitor (see note above)
                nav = 1.0
                hwm = 1.0
            elif abs(r) >= CRISIS_DAY_ABS:
                crisis_log.append({"date": d, "r": round(r, 6)})
        elif abs(r) >= CRISIS_DAY_ABS:
            crisis_log.append({"date": d, "r": round(r, 6)})
        # ---- monthly eval (close i -> orders for i+1 open) ----
        # cut_today: a hard-bound cut firing on an eval row supersedes that
        # row's re-entry (the "next monthly rebalance" is the NEXT month's);
        # otherwise the lock lifts at the eval and re-selection proceeds.
        if i in plan_by_row and not cut_today:
            plan = plan_by_row[i]
            locked = False
            targets = selector(plan)
            for code in list(positions):
                if code not in targets and code not in pending_sells:
                    pending_sells[code] = (plan["adv_by_code"].get(code, float("nan")), "rotation")
                if code in targets and code in pending_sells:
                    pending_sells.pop(code)          # back in targets: rotation cancelled
            for code, yuan in targets.items():
                jj = code_idx.get(code)
                if jj is None or (jj in firsts_row and (i + 1) >= firsts_row[jj]):
                    continue                          # whitelist-dead: never (re-)enter
                pending_set[code] = (yuan, plan["adv_by_code"].get(code, float("nan")))
    cancelled_orders = len(pending_set) + len(pending_sells)

    # ---- metrics ----
    n_days = len(rets)
    years = n_days / 252.0 if n_days else 0.0
    arr = np.asarray(rets, dtype=float)
    sd = float(arr.std(ddof=1)) if n_days > 1 else 0.0
    sharpe = float(arr.mean() / sd * math.sqrt(252)) if sd > 0 else 0.0
    nav_path = np.cumprod(1.0 + arr)
    total_ret = float(nav_path[-1] - 1.0) if n_days else 0.0
    annual = float((1.0 + total_ret) ** (1.0 / years) - 1.0) if years > 0 else 0.0
    peak = np.maximum.accumulate(nav_path) if n_days else np.array([1.0])
    maxdd = float((nav_path / peak - 1.0).min()) if n_days else 0.0
    mid = n_days // 2
    def _seg(a):
        if len(a) < 20:
            return {"status": "insufficient_data", "bars": int(len(a))}
        s = float(a.std(ddof=1))
        return {"sharpe": round(float(a.mean() / s * math.sqrt(252)), 4) if s > 0 else 0.0,
                "annual_return": round(float((np.prod(1.0 + a)) ** (252.0 / len(a)) - 1.0), 4),
                "bars": int(len(a))}
    month_keys = sorted({f"{cal[i].year}-{cal[i].month:02d}"
                         for i in range(start_row, end_row + 1)})
    empty_months = [mk for mk in month_keys if monthly_risk_days.get(mk, 0) == 0]
    open_at_end = {c: round(float(positions[c]["val"]), 2) for c in positions}
    yearly_cost: dict[str, float] = {}
    for mk, cv in costs_by_month.items():
        yk = mk[:4]
        yearly_cost[yk] = round(yearly_cost.get(yk, 0.0) + float(cv), 2)
    return {
        "label": label,
        "full": {"sharpe": round(sharpe, 4), "annual_return": round(annual, 4),
                 "total_return": round(total_ret, 4), "max_drawdown": round(maxdd, 4),
                 "n_days": n_days, "n_entries": n_entries, "n_exits": n_exits,
                 "n_resizes": n_resizes,
                 "win_rate": round(wins / n_exits, 4) if n_exits else None,
                 "turnover_gross_yuan": round(float(traded_gross), 2),
                 "open_positions_at_end": open_at_end,
                 "cancelled_orders": cancelled_orders},
        "half_early": _seg(arr[:mid]), "half_late": _seg(arr[mid:]),
        "cuts": cut_log, "crisis_log": crisis_log,
        "exit_log_sample": exit_log[:50], "n_exits_logged": len(exit_log),
        "entry_log_sample": entry_log[:50], "n_entries_logged": len(entry_log),
        "empty_months": empty_months, "n_empty_months": len(empty_months),
        "monthly_costs": {k: round(float(v), 2) for k, v in sorted(costs_by_month.items())},
        "yearly_costs": yearly_cost,
        "avg_deployed_yuan": round(float(sum(deploy_by_month.values())
                                          / max(1, sum(monthly_risk_days.values()))), 2),
        "_rets": rets, "_dates": ret_dates,
    }


# ---------------------------------------------------------------- passives

def passive_510300(panel: dict, win: dict) -> dict:
    """510300 buy-and-hold, cross-asset disclosure anchor (NOT the skill-line
    pool). Window face = ETF data availability (2020-01-02+) intersected with
    the bond window -- honest sub-window disclosure."""
    out = {"label": "passive_510300_buyhold"}
    if not os.path.exists(ETF_510300_CSV):
        out["error"] = f"missing {ETF_510300_CSV}"
        return out
    df = pd.read_csv(ETF_510300_CSV, index_col=0, parse_dates=True).sort_index()
    cal = panel["cal"]
    seg = df.loc[(df.index >= cal[win["i0"]]) & (df.index <= cal[win["i1"]]), "close"]
    if len(seg) < 20:
        out["error"] = "insufficient overlap"
        return out
    rets = seg.pct_change().dropna().to_numpy(dtype=float)
    sd = float(rets.std(ddof=1))
    sharpe = float(rets.mean() / sd * math.sqrt(252)) if sd > 0 else 0.0
    navp = np.cumprod(1.0 + rets)
    peak = np.maximum.accumulate(navp)
    out["window"] = {"start": str(seg.index[0].date()), "end": str(seg.index[-1].date()),
                     "note": "ETF daily data face starts 2020-01-02; cross-asset anchor only"}
    out["full"] = {"sharpe": round(sharpe, 4),
                   "annual_return": round(float(seg.iloc[-1] / seg.iloc[0]) ** (252.0 / len(seg)) - 1.0, 4),
                   "max_drawdown": round(float((navp / peak - 1.0).min()), 4),
                   "bars": int(len(seg))}
    return out


# ---------------------------------------------------------------- gates

def shard_status(shard_dir: str = SHARD_DIR) -> dict:
    resolved = []
    for i in range(6):
        p = os.path.join(shard_dir, f"shard_{i}of6.json")
        ok = False
        if os.path.exists(p):
            try:
                with open(p, encoding="utf-8") as fh:
                    ok = bool(json.load(fh).get("resolved"))
            except (OSError, ValueError):
                ok = False
        resolved.append(ok)
    return {"resolved": resolved, "n_resolved": sum(resolved)}


def gate_g0_smoke() -> dict:
    p = subprocess.run([sys.executable, "-m", "smoke_test"], cwd=ROOT,
                       capture_output=True, text=True, timeout=900)
    tail = p.stdout.split("Summary:")[-1] if "Summary:" in p.stdout else ""
    return {"gate": "G0 smoke", "ok": bool(p.returncode == 0 and "0 FAIL" in tail),
            "exit": p.returncode, "summary": tail.strip()[:60]}


def gate_g1_prereg() -> dict:
    sha = prereg_blob_sha()
    return {"gate": "G1 prereg integrity", "ok": sha == FROZEN_PREREG_BLOB_SHA,
            "sha": sha, "frozen": FROZEN_PREREG_BLOB_SHA}


def gate_g2_panel_complete(panel: dict, missing: list) -> dict:
    """6/6 shards resolved + manifest coverage: every manifest member either
    has a CSV or is registered no-face/guard-reject (r179 zero-capacity law)."""
    problems = []
    sh = shard_status()
    if sh["n_resolved"] != 6:
        problems.append(f"shards resolved {sh['n_resolved']}/6")
    registered = set()
    if os.path.exists(REGISTRY_JSON):
        with open(REGISTRY_JSON, encoding="utf-8") as fh:
            reg = json.load(fh)
        for code in reg.get("no_face", []) or []:
            registered.add(code["code"] if isinstance(code, dict) else code)
        for code in reg.get("guard_rejects", []) or []:
            registered.add(code["code"] if isinstance(code, dict) else code)
    uncovered = [c for c in missing if c not in registered]
    if uncovered:
        problems.append(f"manifest members with neither CSV nor registry entry: {uncovered[:8]}"
                        f" (n={len(uncovered)})")
    return {"gate": "G2 panel complete", "ok": not problems, "problems": problems,
            "shards": sh, "panel_members": len(panel["codes"]),
            "manifest_missing_csv": len(missing), "registered_no_face": len(registered)}


def gate_g3_completeness(panel: dict, win: dict, scan: dict) -> dict:
    """Per-member monotonic dates + OHLCV NaN=0 + tail reconciliation (sample
    5 alive members re-read from the raw CSV files) + breakpoint scan freeze
    + window rule disclosure. Breakpoint hits are whitelist-handled in-batch
    (NOT a gate failure -- prereg sec.2 freezes the list into the batch)."""
    problems = []
    per_member = {}
    cal = panel["cal"]
    alive = [j for j in range(len(panel["codes"]))
             if panel["last_bar_row"][j] == win["i1"]]
    for j, c in enumerate(panel["codes"]):
        rows = panel["bar_rows"][j]
        cl = panel["close"][rows, j]
        if np.isnan(cl).any() or np.isnan(panel["open"][rows, j]).any() \
                or np.isnan(panel["volume"][rows, j]).any():
            problems.append(f"{c}: NaN in OHLCV")
        per_member[c] = {"bars": len(rows),
                         "first": str(cal[rows[0]].date()) if rows else None,
                         "last": str(cal[rows[-1]].date()) if rows else None}
    # tail reconciliation: raw-file re-read of 5 alive members (sec.2 gate 1)
    reconciled = []
    if len(alive) >= 5:
        for j in alive[:5]:
            c = panel["codes"][j]
            p = os.path.join(DATA_DIR, f"{c}.csv")
            with open(p, encoding="utf-8") as fh:
                lines = [ln for ln in fh.read().strip().splitlines() if ln.strip()]
            tail_date = lines[-1].split(",")[0]
            reconciled.append({"code": c, "tail_date": tail_date})
            if tail_date != CUTOFF:
                problems.append(f"{c}: raw tail {tail_date} != cutoff {CUTOFF}")
    else:
        problems.append(f"alive members at cutoff = {len(alive)} < 5 (tail reconcile needs 5)")
    return {"gate": "G3 completeness + R178 scan + window", "ok": not problems,
            "problems": problems, "per_member_head": dict(list(per_member.items())[:5]),
            "n_members": len(panel["codes"]), "n_alive_at_cutoff": len(alive),
            "tail_reconciliation": reconciled,
            "breakpoints": {"n_events": scan["n_events"],
                            "events": scan["events"][:20],
                            "in_span_holes_n": scan["in_span_holes_n"]},
            "window": win}


def gate_g4_frozen_evidence() -> dict:
    problems = []
    if not os.path.exists(CAPACITY_EVIDENCE):
        problems.append(f"missing {CAPACITY_EVIDENCE}")
    if not os.path.exists(SEMANTICS_EVIDENCE):
        problems.append(f"missing {SEMANTICS_EVIDENCE}")
    else:
        with open(SEMANTICS_EVIDENCE, encoding="utf-8") as fh:
            sem = json.load(fh)
        if sem.get("verdict") != "CLEAN":
            problems.append(f"price semantics verdict {sem.get('verdict')} != CLEAN")
    if sg.SEED_REGISTRY.get("bond_carry_w3a") != SEED_BASE:
        problems.append(f"SEED_REGISTRY bond_carry_w3a != {SEED_BASE}")
    return {"gate": "G4 frozen evidence", "ok": not problems, "problems": problems,
            "capacity_evidence": os.path.basename(CAPACITY_EVIDENCE),
            "semantics_evidence": os.path.basename(SEMANTICS_EVIDENCE)}


def run_gates(panel: dict, missing: list, win: dict, scan: dict, include_g0: bool = True) -> dict:
    out = {}
    if include_g0:
        out["G0"] = gate_g0_smoke()
    out["G1"] = gate_g1_prereg()
    out["G2"] = gate_g2_panel_complete(panel, missing)
    out["G3"] = gate_g3_completeness(panel, win, scan)
    out["G4"] = gate_g4_frozen_evidence()
    return out


# ---------------------------------------------------------------- orchestration

def _inregister_corr(c1s, *, member_run=None):
    """D6 in-register disclosure face: C1 daily sleeve returns vs registered member
    equity streams (prereg sec.1: the in-register roster; PROSPECT/FIRED are not
    in-register). r212 wiring fix: the previous whole-dir iteration fed schema-
    foreign files (firm/traders/_template.json -- level INTERN by example but no
    params.entry) straight into ew6 member_run, KeyErroring the ENTIRE face on
    every production run since delivery (hermetic selftest never mirrored the
    real directory form -- r157/r204 family). Filters below skip non-member and
    schema-foreign files honestly instead of all-or-nothing."""
    import ew6_portfolio as E
    from firm import hr as HR
    if member_run is None:
        E._init_worker()
        member_run = E.member_run
    member_rets, skipped, n_prospect, n_fired = {}, [], 0, 0
    for fn in sorted(os.listdir(HR.TRADERS_DIR)):
        if not fn.endswith(".json"):
            continue
        if fn.startswith("_"):
            skipped.append({"file": fn, "reason": "non-member '_' prefix"})
            continue
        tid = fn[:-5]
        t = HR.load_trader(tid)
        lvl = t.get("level")
        if lvl == "PROSPECT":
            n_prospect += 1          # observation lane, not in-register (prereg sec.1)
            continue
        if lvl == "FIRED" or t.get("status") == "FIRE":
            n_fired += 1
            continue
        if "entry" not in t.get("params", {}):
            skipped.append({"id": tid, "reason": "params.entry absent (schema-foreign)"})
            continue
        mr = member_run(tid)
        eq = pd.Series(mr["eq"], index=pd.to_datetime(mr["dates"]))
        member_rets[tid] = eq.pct_change().dropna()
    pairs = {}
    for tid, mret in member_rets.items():
        j = pd.concat([c1s, mret], axis=1, join="inner").dropna()
        if len(j) > 60 and j.iloc[:, 1].std() > 0:
            pairs[tid] = round(float(j.corr().iloc[0, 1]), 4)
    out = {"max_abs_corr": round(max((abs(v) for v in pairs.values()), default=0.0), 4),
           "pairs": pairs, "n_members": len(member_rets)}
    if n_prospect:
        out["skipped_prospect_n"] = n_prospect
    if n_fired:
        out["skipped_fired_n"] = n_fired
    if skipped:
        out["skipped"] = skipped
    return out


def do_run() -> int:
    t0 = time.time()
    print("[bond_carry_w3a] prereg integrity ...")
    g1 = gate_g1_prereg()
    if not g1["ok"]:
        print(f"[bond_carry_w3a] PREREG DRIFT: {g1['sha']} != {g1['frozen']} -- abort (exit 2)")
        return 2
    panel, missing = load_panel()
    try:
        win = determine_window(panel)
    except ValueError as exc:
        print(f"[bond_carry_w3a] window rule failed: {exc} -- abort (exit 2)")
        return 2
    scan = scan_breakpoints(panel, win["i0"], win["i1"])
    firsts = whitelist_firsts(scan)
    gates = run_gates(panel, missing, win, scan, include_g0=True)
    for name, g in gates.items():
        print(f"  {name}: {'PASS' if g.get('ok') else 'FAIL'}")
        if not g.get("ok"):
            print(f"    detail: {json.dumps(g, ensure_ascii=False, default=str)[:400]}")
    if not all(g.get("ok") for g in gates.values()):
        print("[bond_carry_w3a] GATES FAILED -- batch aborted (exit 2), no numbers produced")
        return 2
    plans = build_eval_plans(panel, win, firsts)
    print(f"[bond_carry_w3a] window {win['start']}..{win['end']} | members {len(panel['codes'])} "
          f"| eval months {len(plans)} | whitelist events {scan['n_events']}")

    # ---- cells at the judgment face (fee x2), x1/x3 disclosure faces ----
    cells = {}
    for name, selector, tp, hb in (
            ("C1", lambda p: dict(p["c1_targets"]), True, True),
            ("C2", targets_c2, True, True),
            ("C3", targets_c3, True, True)):
        cell = run_sleeve(panel, plans, selector, COST_JUDGMENT_MULT,
                          i0=win["i0"], i1=win["i1"],
                          tp_convergence=tp, hard_bounds=hb, label=name, firsts=firsts)
        for mult, key in ((1.0, "x1_full_sharpe"), (3.0, "x3_full_sharpe")):
            cell[key] = run_sleeve(panel, plans, selector, mult,
                                   i0=win["i0"], i1=win["i1"],
                                   tp_convergence=tp, hard_bounds=hb,
                                   label=f"{name}@x{int(mult)}", firsts=firsts)["full"]["sharpe"]
        cells[name] = cell
        print(f"  {name}: sharpe={cell['full']['sharpe']} ann={cell['full']['annual_return']} "
              f"dd={cell['full']['max_drawdown']} entries={cell['full']['n_entries']} "
              f"cuts={len(cell['cuts'])} empty_months={cell['n_empty_months']}")

    # ---- K=32 nulls (judgment face) ----
    null_cells, null_vals, null_rets_cache = {}, [], {}
    for k in range(K_NULLS):
        sel = make_null_selector(k)
        cell = run_sleeve(panel, plans, sel, COST_JUDGMENT_MULT,
                          i0=win["i0"], i1=win["i1"],
                          tp_convergence=False, hard_bounds=True,
                          label=f"null_{k}", firsts=firsts)
        null_cells[f"null_{k}"] = {kk: cell[kk] for kk in
                                   ("full", "n_empty_months", "cuts", "crisis_log")}
        null_vals.append(float(cell["full"]["sharpe"]))
        null_rets_cache[k] = (cell["_rets"], cell["_dates"])
    mu = sum(null_vals) / len(null_vals)
    sigma = math.sqrt(sum((x - mu) ** 2 for x in null_vals) / (len(null_vals) - 1))
    null_summary = {"n": len(null_vals), "mu": round(mu, 4), "sigma": round(sigma, 4),
                    "p95": round(float(np.percentile(null_vals, 95)), 4),
                    "max": round(max(null_vals), 4), "min": round(min(null_vals), 4)}
    print(f"[bond_carry_w3a] nulls: {null_summary}")

    # ---- passives ----
    dom = run_sleeve(panel, plans, targets_domain_passive, COST_JUDGMENT_MULT,
                     i0=win["i0"], i1=win["i1"],
                     tp_convergence=False, hard_bounds=False,
                     label="passive_domain_ew", firsts=firsts)
    p510 = passive_510300(panel, win)
    print(f"  passive_domain_ew: sharpe={dom['full']['sharpe']} | 510300: {p510.get('full', {}).get('sharpe')}")

    c1 = cells["C1"]
    meta = {
        "window": {"start": win["start"], "end": win["end"], "era_floor": ERA_FLOOR,
                   "first_10x60_day": win["first_10x60_day"],
                   "era_floor_binds": win["era_floor_binds"]},
        "n_members_panel": len(panel["codes"]),
        "eval_months": len(plans),
        "cost": {"basis": "V2 (ADV20 3-tier slippage + 1%-ADV cap), knowledge/rules.py",
                 "judgment_face": "fee x2 always on (CostPatch single-source semantics)",
                 "fees_per_side_x1": FEES_PER_SIDE,
                 "disclosure_faces": "x1/x3 full-window Sharpe columns"},
        "accounting": {
            "convention": "yuan-denominated deployed-capital return face; "
                          "out-of-market days contribute 0.0 (sec.4 full-timeline basis)",
            "start_cash_headroom": START_CASH,
            "note": "idle-cash headroom never enters r_t (NAV-diff denominator is "
                    "the same-day risk capital); no lot granularity on the bond face"},
        "whitelist": {"n_events": scan["n_events"], "events": scan["events"],
                      "handling": "in-batch: member excluded from selection at/after "
                                  "first event; open position force-exits at event-day "
                                  "close; corpus files untouched (R178 law)",
                      "in_span_holes_n": scan["in_span_holes_n"]},
        "monthly_faces": {"c1_entry_months_with_candidates":
                              sum(1 for p in plans if p["candidates_n"] > 0),
                          "c1_deferrals_total": sum(p["c1_defers"] for p in plans),
                          "deferral_note": "1%*ADV20 < 2.5k is structurally unreachable "
                                           "under the 500k candidacy floor (frozen residual "
                                           "guard, count disclosed per sec.5.1 honesty)"},
        "last_month_note": "final month composition freezes (eval rows need a next "
                           "panel day to execute; disclosed)",
        "prereg_blob_sha": FROZEN_PREREG_BLOB_SHA,
        "null_base_note": "null monthly draw count = C1 target count at the same eval "
                          "(post-deferral, deterministic target-count face)",
    }
    phase1 = {
        "batch": "BOND_CARRY_WAVE3A",
        **sg.cutoff_meta(CUTOFF),
        "meta": meta,
        "gates": gates,
        "cells": {k: {kk: v[kk] for kk in v if not kk.startswith("_")} for k, v in cells.items()},
        "nulls": {"summary": null_summary, "cells": null_cells},
        "passive": {"passive_domain_ew": {k: v for k, v in dom.items() if not k.startswith("_")},
                    "passive_510300_buyhold": p510},
    }
    with open(RESULTS_JSON, "w", encoding="utf-8") as fh:
        json.dump(phase1, fh, ensure_ascii=False, indent=1, default=str)
    print("[bond_carry_w3a] phase-1 JSON written (passive pool registered)")

    # ---- verdicts (skill line reads the phase-1 passive block; bond_w3a pool) ----
    null_pool = {"values": null_vals,
                 "coverage": {"n_values": len(null_vals), "mu": mu, "sigma": sigma,
                              "schemas_parsed": ["bond_carry_w3a:nulls.summary (K=32 in-batch)"],
                              "known_unparsed": []}}
    line = sg.skill_line_v2(batch_cells=BATCH_CELLS, pool="bond_w3a", null_pool=null_pool)
    print(f"[bond_carry_w3a] skill_line_v2 = {line['line']} "
          f"(passive_term={line['passive_term']} null_term={line['null_term']})")
    g1v = sg.g1_prime_v2(sharpe_full=c1["full"]["sharpe"], returns=c1["_rets"],
                         batch_cells=BATCH_CELLS, pool="bond_w3a", null_pool=null_pool,
                         n_trades=c1["full"]["n_exits"], n_entries=c1["full"]["n_entries"])
    g1v["descriptive"] = {
        "annual_positive": bool(c1["full"]["annual_return"] > 0),
        "dd_ok": bool(c1["full"]["max_drawdown"] >= -0.35),
        "half_early": c1["half_early"], "half_late": c1["half_late"],
        "x1_full_sharpe": c1["x1_full_sharpe"], "x3_full_sharpe": c1["x3_full_sharpe"],
        "n_empty_months": c1["n_empty_months"], "n_cuts": len(c1["cuts"]),
        "crisis_days": len(c1["crisis_log"]),
    }
    print(f"[bond_carry_w3a] C1 g1_prime_v2 pass = {g1v['pass_v2']}")

    # ---- family PBO {C1,C2,C3} (3-cell family, noise noted per sec.4) ----
    fam = align_returns({k: pd.Series(cells[k]["_rets"], index=pd.to_datetime(cells[k]["_dates"]))
                         for k in ("C1", "C2", "C3")})
    pbo = cscv_pbo(fam, N_CSCV_BLOCKS)
    dsr = sg.deflated_sharpe_ratio(c1["_rets"], n_trials=line["n_eff"],
                                   var_null_sr=sigma ** 2)
    g2v = sg.g2_registration_v2(g1_pass=bool(g1v["pass_v2"]), dsr=dsr, pbo=pbo["pbo"])
    print(f"[bond_carry_w3a] C1 g2 eligible = {g2v['eligible_v2']} (dsr={g2v['dsr']} pbo={g2v['family_pbo']})")

    # ---- D6: within-batch + in-register corr faces ----
    within = {}
    c1s = pd.Series(c1["_rets"], index=pd.to_datetime(c1["_dates"]))
    for k in ("C2", "C3"):
        j = pd.concat([c1s, pd.Series(cells[k]["_rets"], index=pd.to_datetime(cells[k]["_dates"]))],
                      axis=1, join="inner").dropna()
        within[k] = round(float(j.corr().iloc[0, 1]), 4) if len(j) > 60 and j.iloc[:, 1].std() > 0 else None
    d6_nulls = []
    for k in range(K_NULLS):
        rets_k, dates_k = null_rets_cache[k]
        s = pd.Series(rets_k, index=pd.to_datetime(dates_k))
        j = pd.concat([c1s, s], axis=1, join="inner").dropna()
        if len(j) > 60 and j.iloc[:, 1].std() > 0:
            d6_nulls.append(round(float(j.corr().iloc[0, 1]), 4))
    d6_within_null_max = max((abs(x) for x in d6_nulls), default=None)
    d6_inregister = {}
    try:
        d6_inregister = _inregister_corr(c1s)
    except Exception as exc:  # noqa: BLE001
        d6_inregister = {"error": f"in-register corr skipped: {exc}"}
    d6 = {"within_batch": within, "nulls_max_abs_corr": d6_within_null_max,
          "in_register": d6_inregister, "reject_line": 0.7,
          "verdict": "reject" if max([abs(x) for x in
                                      [v for v in list(within.values()) if v is not None]
                                      + d6_nulls] + [0.0]) >= 0.7 else "pass"}

    ledger = sg.append_ledger("BOND_CARRY_WAVE3A", BATCH_CELLS,
                              "results/bond_carry_w3a.json", evidence_cutoff=CUTOFF,
                              note=("C1 discount-convergence + C2/C3 attribution + K32 "
                                    "random-member nulls (seed 66_000+k) + 2 passives; "
                                    "window max(2003-06-01, 10x60 rule)..2026-09-24; "
                                    "clean-price face (coupon invisible, carry lower "
                                    "bound); judgment cost face = fee x2; prereg frozen "
                                    "R207 blob 8997310; pool bond_w3a own nulls + "
                                    "domain passive skill line"))
    audit_seg = {}
    try:
        subprocess.run([sys.executable, os.path.join("scripts", "compute_audit.py")],
                       cwd=ROOT, capture_output=True, text=True, timeout=120)
    except Exception as exc:  # noqa: BLE001
        print(f"[bond_carry_w3a] compute_audit in-batch run failed: {exc}")
    apath = os.path.join(ROOT, "results", "compute_audit.json")
    if os.path.exists(apath):
        with open(apath, encoding="utf-8") as fh:
            aj = json.load(fh)
        latest = aj.get("history", [{}])[-1] if aj.get("history") else aj
        audit_seg = {"source": "results/compute_audit.json (in-batch run, latest)",
                     "verdict": latest.get("verdict"), "ts": latest.get("ts"),
                     "cpu_pct": latest.get("cpu_pct"), "flags": latest.get("flags")}

    final = dict(phase1)
    final.update({
        "null_pool": null_pool, "skill_line": line,
        "verdicts_g1": {"C1": g1v}, "verdicts_g2": {"C1": g2v},
        "d6": d6, "family_pbo": {"family": "{C1,C2,C3}", "n_blocks": N_CSCV_BLOCKS,
                                 "pbo": pbo["pbo"], "verdict": pbo["verdict"],
                                 "noise_note": "3-cell family PBO is noisy (prereg sec.4)"},
        "trials_ledger": ledger, "audit": audit_seg,
    })
    with open(RESULTS_JSON, "w", encoding="utf-8") as fh:
        json.dump(final, fh, ensure_ascii=False, indent=1, default=str)

    try:
        with open(ATTRITION_JSON, encoding="utf-8") as fh:
            attr = json.load(fh)
        attr["entries"].append({
            "batch": "BOND_CARRY_WAVE3A",
            "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
            "kind": "search",
            "cells_ledger_delta": BATCH_CELLS,
            "ledger_total_after": ledger.get("total"),
            "gates": {"skill_line_v2": line["line"],
                      "g1_passers": 1 if g1v["pass_v2"] else 0,
                      "g2_eligible": 1 if g2v["eligible_v2"] else 0},
            "eliminated": 2 - (1 if g1v["pass_v2"] else 0),
            "refs": {"results": "results/bond_carry_w3a.json",
                     "prereg": "research/BOND_CARRY_WAVE3A_PREREG.md"},
        })
        with open(ATTRITION_JSON, "w", encoding="utf-8") as fh:
            json.dump(attr, fh, ensure_ascii=False, indent=1)
    except Exception as exc:  # noqa: BLE001
        print(f"[bond_carry_w3a] attrition append failed: {exc}")

    print(f"[bond_carry_w3a] DONE in {time.time() - t0:.1f}s -- "
          f"C1 pass={g1v['pass_v2']} eligible={g2v['eligible_v2']} d6={d6['verdict']}")
    return 0


def do_status() -> int:
    sh = shard_status()
    manifest = load_manifest()
    n_csv = sum(1 for c in manifest if os.path.exists(os.path.join(DATA_DIR, f"{c}.csv")))
    reg = {}
    if os.path.exists(REGISTRY_JSON):
        with open(REGISTRY_JSON, encoding="utf-8") as fh:
            reg = json.load(fh)
    print(f"shards resolved: {sh['n_resolved']}/6 ({sh['resolved']})")
    print(f"manifest: {len(manifest)} | csv on disk: {n_csv} "
          f"| no_face: {len(reg.get('no_face', []))} | guard_rejects: {len(reg.get('guard_rejects', []))}")
    try:
        panel, missing = load_panel()
        win = determine_window(panel)
        print(f"window (if complete): {win['start']}..{win['end']} "
              f"(first 10x60 day {win['first_10x60_day']}, era floor binds={win['era_floor_binds']})")
    except Exception as exc:  # noqa: BLE001
        print(f"window rule: not determinable yet ({exc})")
    return 0


# ---------------------------------------------------------------- selftest (offline, hermetic)

def _mk_frame(dates, close, open_=None, volume=None):
    idx = pd.DatetimeIndex(dates)
    return pd.DataFrame({"open": open_ if open_ is not None else list(close),
                         "high": list(close), "low": list(close),
                         "close": list(close),
                         "volume": volume if volume is not None else [1_000_000.0] * len(close)},
                        index=idx)


def _fixture_panel(n_members=3, start="2019-01-01", days=130, base_close=98.0,
                   gap=0.0):
    bdates = pd.bdate_range(start, periods=days)
    raw = {}
    for m in range(n_members):
        code = f"sh01990{m}"
        cl = [base_close + m * 0.5 + gap * i for i in range(days)]
        raw[code] = _mk_frame(bdates, cl)
    return raw, bdates


def _win(i0, i1):
    return {"i0": i0, "i1": i1}


def do_selftest() -> int:
    fails: list[str] = []

    # ---- S15 seed registry ----
    if sg.SEED_REGISTRY.get("bond_carry_w3a") != 66_000:
        fails.append(f"SEED_REGISTRY bond_carry_w3a = {sg.SEED_REGISTRY.get('bond_carry_w3a')} != 66000")

    # ---- S2 sizing + deferral + structural invariance ----
    if size_member(800_000.0) != (8_000.0, False):
        fails.append("size_member(800k) != (8000, False)")
    if size_member(2_000_000.0) != (10_000.0, False):
        fails.append("size_member(2M) != (10000, False) -- cap")
    if size_member(200_000.0)[1] is not True:
        fails.append("size_member(200k) not deferred")
    if size_member(ADV_FLOOR_YUAN)[0] < DEFER_FLOOR_YUAN:
        fails.append("deferral reachable at candidacy floor -- structural invariant broken")

    # ---- S17 eval rows exclude the final row ----
    cal = pd.DatetimeIndex(pd.bdate_range("2020-01-01", periods=70))
    rows = eval_rows(cal, 0, len(cal) - 1)
    if rows and rows[-1] >= len(cal) - 1:
        fails.append("eval_rows includes the final row (unfillable orders)")

    # ---- S1 candidate gates via build_eval_plans ----
    raw, bdates = _fixture_panel(n_members=3, days=70, base_close=98.0)
    raw["sh0199999"] = _mk_frame(bdates, [101.0] * 70)          # not discount
    raw["sh0199998"] = _mk_frame(bdates, [99.0] * 70, volume=[100.0] * 70)  # thin book
    panel = prep_panel(raw)
    plans = build_eval_plans(panel, _win(0, 69), {})
    if not plans:
        fails.append("no eval plans for 70-day fixture")
    else:
        p = plans[-1]
        if p["candidates_n"] != 3:
            fails.append(f"candidates_n {p['candidates_n']} != 3 (discount+adv gate)")
        if "sh0199999" in p["cand_all"]:
            fails.append("close>=100 member passed the discount gate")
        if "sh0199998" in p["cand_all"]:
            fails.append("thin-book member (adv20 ~10k yuan) passed the ADV floor")
        if p["universe_n"] != 4:
            fails.append(f"universe_n {p['universe_n']} != 4")
        # thin member: 99 * 100 * k = ~9.9k yuan adv20 < 500k -> excluded; but the
        # 3 fixtures have 1e6 volume: 98*1e6*k ~ 98M yuan -> in universe.

    # ---- S4 discount-gate empty window (flat sleeve, zero rets, empty months) ----
    raw2, _ = _fixture_panel(n_members=3, days=70, base_close=101.0)  # all >= 100
    panel2 = prep_panel(raw2)
    plans2 = build_eval_plans(panel2, _win(0, 69), {})
    cell = run_sleeve(panel2, plans2, lambda p: dict(p["c1_targets"]), COST_JUDGMENT_MULT,
                      i0=0, i1=69, tp_convergence=True, hard_bounds=True, label="C1-empty")
    if any(x != 0.0 for x in cell["_rets"]):
        fails.append("empty-window sleeve produced nonzero returns")
    if cell["n_empty_months"] < 2:
        fails.append(f"empty-window sleeve empty_months {cell['n_empty_months']} < 2")
    if cell["full"]["n_entries"] != 0:
        fails.append("empty-window sleeve entered positions")

    # ---- S3 monthly rotation + convergence TP (260d: entries need >=60 bars) ----
    bd3 = pd.bdate_range("2019-01-01", periods=260)
    cl0 = [98.0] * 150 + [100.5] * 110                # converges above par mid-window
    raw3 = {"sh019900": _mk_frame(bd3, cl0),
            "sh019901": _mk_frame(bd3, [98.5] * 260)}
    panel3 = prep_panel(raw3)
    plans3 = build_eval_plans(panel3, _win(0, 259), {})
    cell3 = run_sleeve(panel3, plans3, lambda p: dict(p["c1_targets"]), COST_JUDGMENT_MULT,
                       i0=0, i1=259, tp_convergence=True, hard_bounds=True, label="C1-tp")
    tp_exits = [e for e in cell3["exit_log_sample"] if e["reason"] == "tp"]
    if not tp_exits:
        fails.append("convergence TP never fired for close>=100 member")
    if tp_exits and pd.to_datetime(tp_exits[0]["date"]) <= pd.Timestamp(str(bd3[150].date())):
        fails.append("TP exit executed on/before the trigger close (lookahead)")

    # ---- S10 accounting exactness (hand-computed r on mini panel) ----
    bd = pd.DatetimeIndex(["2020-01-29", "2020-01-30", "2020-01-31",
                           "2020-02-03", "2020-02-04"])
    mini = {"A": _mk_frame(bd, [98.0, 98.0, 98.0, 98.0, 99.0])}
    # open on execution day differs from close to exercise the open fill
    mini["A"] = pd.DataFrame(
        {"open": [98.0, 98.0, 98.0, 98.5, 99.0], "high": [98, 98, 98, 99, 99],
         "low": [98, 98, 98, 98, 99], "close": [98.0, 98.0, 98.0, 99.0, 99.0],
         "volume": [1e6] * 5}, index=bd)
    pmini = prep_panel(mini)
    plans_mini = [{"row": 2, "date": "2020-01-31", "adv_by_code": {"A": float("nan")}}]
    cellm = run_sleeve(pmini, plans_mini, lambda p: {"A": 10_000.0}, COST_JUDGMENT_MULT,
                       i0=0, i1=4, tp_convergence=False, hard_bounds=False, label="mini")
    # expected: entry 2020-02-03 open 98.5 -> units=10000/98.5; close 99.0
    units = 10_000.0 / 98.5
    entry_cost = 10_000.0 * (2.0 * FEES_PER_SIDE + cost_v2_slippage(float("nan")))
    val_close = units * 99.0
    exp_r = (val_close - 10_000.0 - entry_cost) / 10_000.0
    got_r = cellm["_rets"][3]  # 2020-02-03 is cal index 3
    if abs(got_r - exp_r) > 1e-12:
        fails.append(f"accounting exactness: r={got_r} != hand-computed {exp_r}")
    if cellm["_rets"][0] != 0.0 or cellm["_rets"][2] != 0.0:
        fails.append("flat pre-entry days must be 0.0")

    # ---- S5 face termination (hand-built plan bypasses the 60-bar gate) ----
    bd5 = pd.bdate_range("2019-01-01", periods=40)
    raw5 = {"sh019905": _mk_frame(bd5, [98.0 + 0.1 * i for i in range(40)])}
    panel5 = prep_panel(raw5)
    plans5 = [{"row": 1, "date": str(bd5[1].date()), "adv_by_code": {"sh019905": float("nan")}}]
    cell5 = run_sleeve(panel5, plans5, lambda p: {"sh019905": 10_000.0}, COST_JUDGMENT_MULT,
                       i0=0, i1=39, tp_convergence=False, hard_bounds=False, label="faceterm")
    ft = [e for e in cell5["exit_log_sample"] if e["reason"] == "face_term"]
    if not ft:
        fails.append("face termination never fired for data-ending member")
    elif ft[0]["date"] != str(bd5[39].date()):
        fails.append(f"face term exit date {ft[0]['date']} != last bar close day")

    # ---- S6 12% breakpoint whitelist (single-face event: crash without rebound) ----
    bd6 = pd.bdate_range("2019-01-01", periods=70)
    cl = [98.0] * 30 + [69.0] * 40                      # -29.6% overnight at day 30, stays down
    raw6 = {"sh019906": _mk_frame(bd6, cl)}
    panel6 = prep_panel(raw6)
    scan6 = scan_breakpoints(panel6, 0, 69)
    if scan6["n_events"] != 1:
        fails.append(f"12% scan flagged {scan6['n_events']} events, expected 1")
    f6 = whitelist_firsts(scan6)
    if "sh019906" not in f6:
        fails.append("whitelist_firsts missing the corrupted member")
    plans6 = build_eval_plans(panel6, _win(0, 69), f6)
    if plans6 and plans6[-1]["universe_n"] != 0:
        fails.append("whitelist-dead member still in the post-event universe")
    # sleeve-level defense: force-exit at event close + no post-event entry
    plans6b = [{"row": 2, "date": "2019-01-03", "adv_by_code": {"sh019906": float("nan")}},
               {"row": 34, "date": "2019-02-07", "adv_by_code": {"sh019906": float("nan")}}]
    cell6 = run_sleeve(panel6, plans6b, lambda p: {"sh019906": 10_000.0}, COST_JUDGMENT_MULT,
                       i0=0, i1=69, tp_convergence=False, hard_bounds=False, label="wl",
                       firsts={"sh019906": str(bd6[30].date())})
    wl = [e for e in cell6["exit_log_sample"] if e["reason"] == "whitelist"]
    if not wl:
        fails.append("whitelist force-exit never fired")
    elif wl[0]["date"] != str(bd6[30].date()):
        fails.append(f"whitelist exit at {wl[0]['date']} != event day {bd6[30].date()}")
    if cell6["full"]["n_entries"] != 1:
        fails.append(f"whitelist-dead member re-entered (entries={cell6['full']['n_entries']})")

    # ---- S7 hard bounds: cut + lock + re-entry at the NEXT monthly eval ----
    bd7 = pd.bdate_range("2019-01-01", periods=260)
    crash = [98.0] * 70
    for i in range(70, 100):
        crash.append(98.0 * (0.985 ** (i - 69)))
    crash.extend([crash[-1]] * (260 - len(crash)))
    crash[72] = crash[71] * 0.95          # -5% single day INSIDE the held crash -> crisis log
    raw7 = {"sh019907": _mk_frame(bd7, crash)}
    panel7 = prep_panel(raw7)
    plans7 = build_eval_plans(panel7, _win(0, 259), {})
    cell7 = run_sleeve(panel7, plans7, lambda p: dict(p["c1_targets"]), COST_JUDGMENT_MULT,
                       i0=0, i1=259, tp_convergence=False, hard_bounds=True, label="C1-bounds")
    if not cell7["cuts"]:
        fails.append("hard-bound cut never fired on a -1.5%/day crash stretch")
    else:
        trig = cell7["cuts"][0]["trigger"]
        if trig not in ("20d_cum", "hwm_dd"):
            fails.append(f"cut trigger {trig} unknown")
    # lock semantics: after a cut, the next ENTRY must be at/after the next
    # monthly eval row's execution day (no intra-month re-entry)
    if cell7["cuts"]:
        cut_i = pd.to_datetime(cell7["cuts"][0]["date"])
        evals = sorted(pd.to_datetime(p["date"]) for p in plans7)
        next_eval = next((e for e in evals if e > cut_i), None)
        post_entries = [pd.to_datetime(e["date"]) for e in cell7["entry_log_sample"]
                        if pd.to_datetime(e["date"]) > cut_i]
        if not post_entries:
            fails.append("sleeve never re-entered after the cut (segment-fresh monitor "
                         "must allow the next-monthly re-entry)")
        elif next_eval is not None and min(post_entries) <= next_eval:
            fails.append(f"re-entry {min(post_entries).date()} at/before the next monthly "
                         f"eval {next_eval.date()} (intra-month lock broken)")

    # ---- S8 crisis log ----
    crisis = [e for e in cell7["crisis_log"]]
    # the crash stretch must log at least one |r|>=3% day (single-member sleeve)
    if not crisis:
        fails.append("crisis log empty on a -1.5%/day single-member crash (20d cum face)")

    # ---- S9 null determinism + c1_n coupling (pool 8 > draw 3) ----
    bd9 = pd.bdate_range("2019-01-01", periods=90)
    raw9 = {}
    for m in range(3):
        raw9[f"sh01990{m}"] = _mk_frame(bd9, [98.0] * 90)          # discount candidates
    for m in range(3, 11):
        raw9[f"sh0199{m:02d}"] = _mk_frame(bd9, [101.0] * 90)      # non-candidate pool (8)
    panel9 = prep_panel(raw9)
    plans9 = build_eval_plans(panel9, _win(0, 89), {})
    selA = make_null_selector(0)
    ra = run_sleeve(panel9, plans9, selA, COST_JUDGMENT_MULT, i0=0, i1=89,
                    tp_convergence=False, hard_bounds=True, label="n0a")
    rb = run_sleeve(panel9, plans9, make_null_selector(0), COST_JUDGMENT_MULT, i0=0, i1=89,
                    tp_convergence=False, hard_bounds=True, label="n0b")
    if ra["_rets"] != rb["_rets"]:
        fails.append("null k=0 double-run differs (determinism)")
    rc = run_sleeve(panel9, plans9, make_null_selector(1), COST_JUDGMENT_MULT, i0=0, i1=89,
                    tp_convergence=False, hard_bounds=True, label="n1")
    if ra["_rets"] == rc["_rets"]:
        fails.append("null k=0 and k=1 identical (seed not binding)")
    if ra["full"]["n_entries"] == 0:
        fails.append("null sleeve never entered (fixture degenerate)")
    # c1_n coupling: rebuild plans with a selector yielding empty C1 -> null flat
    plans9e = [dict(p, c1_targets={}, c1_n=0) for p in plans9]
    r9e = run_sleeve(panel9, plans9e, make_null_selector(3), COST_JUDGMENT_MULT, i0=0, i1=89,
                     tp_convergence=False, hard_bounds=True, label="n3-empty")
    if r9e["full"]["n_entries"] != 0:
        fails.append("null sleeve entered members while C1 count was 0 (coupling broken)")

    # ---- S12 cost mult monotonicity ----
    sh_x1 = run_sleeve(panel3, plans3, lambda p: dict(p["c1_targets"]), 1.0,
                       i0=0, i1=259, tp_convergence=True, hard_bounds=True, label="x1")["full"]["sharpe"]
    sh_x2 = cell3["full"]["sharpe"]
    sh_x3 = run_sleeve(panel3, plans3, lambda p: dict(p["c1_targets"]), 3.0,
                       i0=0, i1=259, tp_convergence=True, hard_bounds=True, label="x3")["full"]["sharpe"]
    if not (sh_x1 >= sh_x2 >= sh_x3):
        fails.append(f"cost faces not monotone: x1={sh_x1} x2={sh_x2} x3={sh_x3}")

    # ---- S13 zero-volume day: order slips to the next tradable bar ----
    bd13 = pd.bdate_range("2019-01-01", periods=70)
    vol13 = [1e6] * 70
    vol13[1] = 0.0    # execution day 1 (after eval at row 0) is untradable
    raw13 = {"sh019913": _mk_frame(bd13, [98.0] * 70, volume=vol13)}
    panel13 = prep_panel(raw13)
    plans13 = [{"row": 0, "date": "2019-01-01", "adv_by_code": {"sh019913": float("nan")}}]
    cell13 = run_sleeve(panel13, plans13, lambda p: {"sh019913": 10_000.0}, COST_JUDGMENT_MULT,
                        i0=0, i1=69, tp_convergence=False, hard_bounds=False, label="slip")
    if cell13["full"]["n_entries"] != 1:
        fails.append("slipped order never filled")
    if cell13["_rets"][1] != 0.0:
        fails.append("zero-volume day produced a nonzero return (mark/trade on a dead bar)")

    # ---- S11 window rule: era floor vs data rule ----
    bd11 = pd.bdate_range("2001-01-01", periods=500)
    raw11 = {f"sh0199{m}1": _mk_frame(bd11, [98.0] * 500) for m in range(12)}
    panel11 = prep_panel(raw11)
    ready = (panel11["bars_cal"] >= MIN_BARS).sum(axis=1)
    hit = ready >= MIN_MEMBERS_START
    i0_data = int(np.argmax(hit))
    i0_floor = int(np.searchsorted(panel11["cal"], pd.Timestamp(ERA_FLOOR), side="left"))
    if not (i0_floor > i0_data):
        fails.append("era-floor fixture: floor row should bind later than the data rule")
    # (determine_window itself needs a CUTOFF-terminated panel -- covered by G2/G3
    #  production gates; here the row math is asserted directly)

    # ---- S14 pool registration: honest KeyError + read ----
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        try:
            sg.passive_baseline("bond_w3a", results_dir=td)
            fails.append("passive_baseline(bond_w3a) missing-file KeyError not raised")
        except KeyError:
            pass
        with open(os.path.join(td, "bond_carry_w3a.json"), "w", encoding="utf-8") as fh:
            json.dump({"passive": {"passive_domain_ew": {"full": {"sharpe": 0.42}}}}, fh)
        v = sg.passive_baseline("bond_w3a", results_dir=td)
        if abs(v - 0.42) > 1e-12:
            fails.append(f"passive_baseline(bond_w3a) read {v} != 0.42")

    # ---- S18 whitelist excludes only at/after the event date (own 120d panel:
    #      a bars-eligible eval row must exist BEFORE the event) ----
    bd18 = pd.bdate_range("2019-01-01", periods=120)
    cl18 = [98.0] * 80 + [69.0] * 40          # event at row 80 (mid-April)
    panel18 = prep_panel({"sh019918": _mk_frame(bd18, cl18)})
    scan18 = scan_breakpoints(panel18, 0, 119)
    f18 = whitelist_firsts(scan18)
    plans18 = build_eval_plans(panel18, _win(0, 119), f18)
    pre = [p for p in plans18 if pd.Timestamp(p["date"]) < pd.Timestamp(str(bd18[80].date()))]
    post = [p for p in plans18 if pd.Timestamp(p["date"]) >= pd.Timestamp(str(bd18[80].date()))]
    pre_eligible = [p for p in pre if p["universe_n"] > 0]
    if not pre_eligible:
        fails.append("S18 fixture degenerate: no bars-eligible pre-event eval row")
    if pre_eligible and "sh019918" not in (pre_eligible[-1]["cand_all"] or {}):
        fails.append("whitelist excluded the member BEFORE its event date")
    if post and any("sh019918" in p["cand_all"] or "sh019918" in p["c1_targets"] for p in post):
        fails.append("whitelist-dead member still selectable after its event date")

    # ---- S16 panel-complete gate (tmp shards) ----
    with tempfile.TemporaryDirectory() as td:
        sh = shard_status(td)
        if sh["n_resolved"] != 0:
            fails.append("empty tmp shard dir counted as resolved")
        for i in range(6):
            with open(os.path.join(td, f"shard_{i}of6.json"), "w", encoding="utf-8") as fh:
                json.dump({"resolved": True}, fh)
        if shard_status(td)["n_resolved"] != 6:
            fails.append("6/6 resolved shards miscounted")

    # ---- S19 d6 in-register face: production directory form (r212 wiring-fix
    #      pairing leg -- the real TRADERS_DIR contains _template.json and 22
    #      PROSPECT files; hermetic fixtures must mirror that form or the whole
    #      face KeyErrors at the first schema-foreign file, as it did from
    #      delivery through r212 -- r157/r204 family) ----
    import tempfile as _tempfile
    from pathlib import Path as _Path
    from firm import hr as _HR
    with _tempfile.TemporaryDirectory() as td:
        bds = pd.bdate_range("2020-01-01", periods=120)
        eq_walk = list(1 + 0.001 * np.sin(np.arange(120) / 7.0))
        fake_member_run = lambda tid: {"eq": eq_walk, "dates": [str(d.date()) for d in bds]}  # noqa: E731
        files = {
            "_template.json": {"level": "INTERN", "params": {"entry_n": "x", "exit_n": "y"}},
            "PROS-FAKE-01.json": {"level": "PROSPECT", "params": {"entry": "e"}},
            "FIRED-OLD-01.json": {"level": "FIRED", "params": {"entry": "e"}},
            "INTERN-OK-01.json": {"level": "INTERN", "params": {"entry": "e"}},
            "INTERN-OK-02.json": {"level": "INTERN", "params": {"entry": "e"}},
            "NOTJSON.txt": {"ignored": True},
        }
        for fn, payload in files.items():
            with open(os.path.join(td, fn), "w", encoding="utf-8") as fh:
                json.dump(payload, fh)
        c1s_fx = pd.Series(0.5 * np.sin(np.arange(120) / 7.0), index=bds)
        old_traders_dir = _HR.TRADERS_DIR
        _HR.TRADERS_DIR = _Path(td)
        try:
            d6fx = _inregister_corr(c1s_fx, member_run=fake_member_run)
        finally:
            _HR.TRADERS_DIR = old_traders_dir
        if d6fx.get("n_members") != 2:
            fails.append(f"S19 n_members {d6fx.get('n_members')} != 2 (template/prospect/"
                         "fired must be excluded, valid kept)")
        if set(d6fx.get("pairs", {})) != {"INTERN-OK-01", "INTERN-OK-02"}:
            fails.append(f"S19 pairs keys wrong: {sorted(d6fx.get('pairs', {}))}")
        if d6fx.get("skipped_prospect_n") != 1 or d6fx.get("skipped_fired_n") != 1:
            fails.append(f"S19 prospect/fired skip counts wrong: {d6fx}")
        skip_files = [s.get("file") for s in d6fx.get("skipped", [])] + [s.get("id") for s in d6fx.get("skipped", [])]
        if "_template.json" not in skip_files:
            fails.append(f"S19 template file not honestly skipped: {d6fx.get('skipped')}")
        if "NOTJSON.txt" in str(d6fx):
            fails.append("S19 non-json file leaked into the face")

    print(f"[bond_carry_w3a selftest] {'ALL PASS' if not fails else 'FAIL: ' + str(fails)}")
    return 0 if not fails else 1


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "selftest"
    if cmd == "gates":
        g1 = gate_g1_prereg()
        if not g1["ok"]:
            print(json.dumps(g1, ensure_ascii=False))
            sys.exit(2)
        panel, missing = load_panel()
        try:
            win = determine_window(panel)
        except ValueError as exc:
            print(f"G-window FAIL (honest): {exc}")
            print(f"G2 shards: {json.dumps(shard_status())}")
            sys.exit(2)
        scan = scan_breakpoints(panel, win["i0"], win["i1"])
        gs = run_gates(panel, missing, win, scan, include_g0=True)
        for name, g in gs.items():
            print(f"{name}: {'PASS' if g.get('ok') else 'FAIL'}")
            if not g.get("ok"):
                print(json.dumps(g, ensure_ascii=False, default=str)[:600])
        sys.exit(0 if all(g.get("ok") for g in gs.values()) else 2)
    if cmd == "run":
        sys.exit(do_run())
    if cmd == "status":
        sys.exit(do_status())
    if cmd == "selftest":
        sys.exit(do_selftest())
    print("usage: bond_carry_w3a.py gates|run|status|selftest")
    sys.exit(1)
