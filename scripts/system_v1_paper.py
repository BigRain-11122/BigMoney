"""SYSTEM-V1 live paper harness (T-91 s1/s2, O-20260926-2340, bm-a lane).

Two paper accounts, deterministic full replay from the frozen anchor grid
day 2026-09-24 (AGGR/grid_paper paradigm), consuming ONLY the git-tracked
small artifacts exported by the bm-b lane bridge (scripts/
rev_osc_signal_export.py; git = the transfer channel, fleet/TRANSFER.md
control-plane law). Fail-closed on absent lane data (no SIG = awaiting_
signal skip, counted; no BARS at all = armed, zero marks).

  SYSTEM-V1    ¥1,000,000 -- the LIVE face of the decision-chain system
               (research/SYSTEM_V1_PREREG.md): L1 market-clock state
               (harness-accumulated state_hist from results/market_clock/
               call_latest.json, append-when-advances never truncate;
               state_for_day = latest asof STRICTLY < day) -> L2 frozen
               route table v1.0 -> deployed sleeve = rev_osc only (trend/
               lowvol v1.0 stubs weight-bearing-0, residual cash 0%);
               w_eff glide law (weight changes take effect at the first
               entry day after the route change; no mid-hold forced
               liquidation) + |dw|*COST_X1 transition cost.
  REV-OSC-STD  ¥1,000,000 -- standalone sleeve face (same engine replay,
               ret = series, no route overlay).

Engine = per-name daily-mark-to-market MIRROR of the judged runner
(rev_osc_stock_p1.sim_stock, constants imported, zero re-implementation):
T+1 open conservative entry (O-1132 unfillable law), TP +8% / SL -10%
(same-day-both -> SL first, gap fills at open), time exit H=7 with
LD-open rolls, sealed-LD mark-at-close rolls, suspension frozen marks;
cost x1 13.041bp/side multiplicative decomposition -- daily path product
== sim_stock _net within 1e-9 (selftest leg-1 proves the mirror). Bars
exhausted while holding = status open, NO fake tail exit (live-ops law).

Idempotency: full deterministic replay every run; state files written
atomically; no-op = serialized content identical to disk (wall clock only
in the "updated" envelope). Lane guard: bm-a-only-writes (R31 family);
every other machine = stdout-only honest no-op. Marks are not trials:
ledger +0, SEED_REGISTRY +0.

Usage: python scripts/system_v1_paper.py run | selftest
Exit codes: 0 = ok/no-op; 2 = mechanism fault (honest, never masked).
"""
import json
import math
import os
import sys
import time

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from rev_osc_stock_p1 import (CN_20CM_FROM, COST_X1, GRID_STEP,     # noqa: F401
                              LIMIT_OPEN_TOL, MAIN_FLOOR, SL, STAR_FROM,
                              TP, WIDE_FLOOR)          # frozen-mirror imports

MACHINE_JSON = os.path.join(ROOT, "fleet", "machine.json")
ETF_CSV = os.path.join(ROOT, "data", "daily", "510300.csv")
CALL_LATEST = os.path.join(ROOT, "results", "market_clock", "call_latest.json")
SIG_DIR = os.path.join(ROOT, "results", "rev_osc_live")
OUT_DIR = os.path.join(ROOT, "results", "system_v1_paper")
V1_PATH = os.path.join(OUT_DIR, "SYSTEM-V1_paper.json")
STD_PATH = os.path.join(OUT_DIR, "REV-OSC-STD_paper.json")

LANE_OWNER = "bm-a"                     # T-91 harness lane (R31 family)
TICKET = "T-2026-09-27-91"
ORDER_REF = "O-20260926-2340"
ANCHOR = "2026-09-24"                   # frozen grid anchor = evidence cutoff
EVIDENCE_CUTOFF = "2026-09-24"          # C2 top-level key law
H = 7                                  # FY_BG_TP8 frozen cell (O-2335)
NAME_W = 0.10                           # equal weight 1/10 (frozen spec)
TOP_N = 10
INITIAL_CNY = 1_000_000.0              # AGGR paper precedent

# L2 route table v1.0 -- harness-frozen numeric instantiation of the
# SYSTEM_V1_PREREG L2 qualitative rows (amendment window until first mark
# 2026-09-28; disclose in every state file).
ROUTE_TABLE_V1 = {
    "GREEN":  {"rev_osc": 0.00, "trend": 0.60, "lowvol": 0.20, "cap": 0.80},
    "CHOP":   {"rev_osc": 0.00, "trend": 0.15, "lowvol": 0.15, "cap": 0.40},
    "ORANGE": {"rev_osc": 0.30, "trend": 0.10, "lowvol": 0.10, "cap": 0.50},
    "RED":    {"rev_osc": 0.05, "trend": 0.00, "lowvol": 0.15, "cap": 0.20},
}
STATE_TO_ROW = {"GREEN": "GREEN", "YELLOW": "CHOP", "CHOP": "CHOP",
                "ORANGE": "ORANGE", "RED": "RED"}
FAIL_CLOSED_ROW = {"rev_osc": 0.00, "trend": 0.00, "lowvol": 0.00, "cap": 0.00}

# B7b consumer contract: harness-consumed key faces (subset tripwire).
SIG_KEYS = {"date", "gate", "picks", "thin_market"}
GATE_KEYS = {"open"}
PICK_KEYS = {"code", "board"}
BARS_KEYS = {"rows"}


# ---------------------------------------------------------------- helpers
def _read_json(path):
    with open(path, encoding="utf-8-sig") as fh:
        return json.load(fh)


def _atomic_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def _fin(x):
    return isinstance(x, (int, float)) and math.isfinite(x)


def floor_for(board, date_str):
    """Per-day limit floor (judged frozen face: board x era switches)."""
    d = pd.Timestamp(date_str)
    if board == "chinext":
        return WIDE_FLOOR if d >= CN_20CM_FROM else MAIN_FLOOR
    if board == "star":
        return WIDE_FLOOR if d >= STAR_FROM else MAIN_FLOOR
    return MAIN_FLOOR


def route_for_state(state):
    """L2 route row for an L1 state (YELLOW -> CHOP); None/unknown state
    = fail-closed zero row, disclosed."""
    if state is None:
        return dict(FAIL_CLOSED_ROW), "fail_closed_no_state"
    row = STATE_TO_ROW.get(state)
    if row is None:
        return dict(FAIL_CLOSED_ROW), f"fail_closed_unknown_state:{state}"
    return dict(ROUTE_TABLE_V1[row]), None


# ------------------------------------------------------------------- L1
def update_state_hist(hist, call_latest):
    """Append-when-advances, never truncate (frozen L1 law)."""
    hist = [dict(e) for e in (hist or [])]
    if not call_latest:
        return hist
    asof = call_latest.get("asof")
    st = (call_latest.get("regime_v3") or {}).get("state")
    if not asof or not st:
        return hist
    if hist and asof <= hist[-1]["asof"]:
        return hist
    hist.append({"asof": asof, "state": st,
                 "clock_cell": call_latest.get("clock_cell"),
                 "cap_ladder": call_latest.get("position_cap_ladder")})
    return hist


def state_for_day(hist, date_str):
    """Latest hist entry with asof STRICTLY < date (T-close decision ->
    T+1 open causality law)."""
    best = None
    for e in hist or []:
        if e["asof"] < date_str:
            best = e
    return best["state"] if best else None


# ------------------------------------------------------------- data faces
def load_etf_calendar():
    df = pd.read_csv(ETF_CSV, parse_dates=["date"])
    return sorted({str(pd.Timestamp(d).date()) for d in df["date"]})


def load_sigs_bars():
    """SIG/BARS artifacts from the bm-b lane bridge; BARS merge =
    latest-wins per (code, bar date) across files (qfq truth)."""
    sigs, bars = {}, {}
    sig_files, bars_files = [], []
    if os.path.isdir(SIG_DIR):
        for fn in os.listdir(SIG_DIR):
            if fn.startswith("SIG-") and fn.endswith(".json"):
                sig_files.append(fn)
            elif fn.startswith("BARS-") and fn.endswith(".json"):
                bars_files.append(fn)
    for fn in sorted(sig_files):
        try:
            sigs[fn[4:-5]] = _read_json(os.path.join(SIG_DIR, fn))
        except Exception:                                       # noqa: BLE001
            continue                     # torn/foreign file -> skip honest
    bars_cutoff = None
    for fn in sorted(bars_files):        # ascending -> last parse wins (max)
        try:
            blob = _read_json(os.path.join(SIG_DIR, fn))
        except Exception:                                       # noqa: BLE001
            continue
        bars_cutoff = fn[5:-5]
        for code, rows in (blob.get("rows") or {}).items():
            slot = bars.setdefault(code, {})
            for row in rows:
                # producer row = [date, open, high, low, close]
                slot[row[0]] = (row[1], row[2], row[3], row[4])
    return sigs, bars, bars_cutoff, len(sig_files), len(bars_files)


# ---------------------------------------------------------------- engine
def prep_name(bars_code, pos_of, T):
    """rows {pos: (o,h,l,c)} + prev_close array (mirror _prev_finite)."""
    rows = {}
    for dstr, row in (bars_code or {}).items():
        p = pos_of.get(dstr)
        if p is not None:
            rows[p] = row
    prev_c = [None] * T
    run = None
    for i in range(T):
        prev_c[i] = run
        r = rows.get(i)
        if r is not None and _fin(r[3]):
            run = float(r[3])
    return rows, prev_c


def path_engine(rows, prev_c, fl_arr, entry_pos, end_pos, tpsl=True,
                hold=None):
    """Per-name daily-mark-to-market path, mirror of rev_osc_stock_p1.
    sim_stock rule order verbatim: suspension roll -> sealed-LD
    mark-at-close roll -> TP/SL (same-day-both -> SL first, gap fills at
    open) -> time exit at open with LD-open queue-unsold roll. Cost
    split: entry day close/(entry*(1+cost))-1, mid days close/prev_mark,
    exit day px*(1-cost)/prev_mark -> telescopes to sim_stock _net.
    Bars exhausted while holding = status open (no fake tail exit).
    hold = H days (frozen live cell H=7; parameterized for the mirror
    proof). Returns (rets[(pos, ret)], exit_pos, tag, entry_px) or None
    (= unfillable, same rule as sim_stock)."""
    hold = H if hold is None else hold
    d = entry_pos
    b0 = rows.get(d)
    if b0 is None or not _fin(b0[0]):
        return None
    pc0 = prev_c[d]
    if pc0 is None or b0[0] / pc0 - 1.0 >= fl_arr[d] - LIMIT_OPEN_TOL:
        return None                       # near-limit-up open, un-captured
    entry = float(b0[0])
    tp_px, sl_px = entry * TP, entry * SL
    target = entry_pos + hold
    rets = []
    prev_mark = None
    while d <= end_pos:
        b = rows.get(d)
        if b is None or not (_fin(b[0]) and _fin(b[3])):
            if prev_mark is not None:
                rets.append((d, 0.0))     # suspension day: mark frozen
            d += 1
            continue
        o, h, l, c = b
        fl = fl_arr[d]
        pcv = prev_c[d]
        # sealed limit-down day -> no fills, mark at close, roll forward
        if _fin(h) and _fin(l) and h == l == c and pcv is not None \
                and c / pcv - 1.0 <= -fl:
            base = entry * (1 + COST_X1) if prev_mark is None else prev_mark
            rets.append((d, c / base - 1.0))
            prev_mark = float(c)
            d += 1
            continue
        # TP/SL intraday (frozen live cell three-piece tp8)
        exit_px, tag = None, None
        if tpsl and _fin(h) and _fin(l):
            lo_gap = pcv is not None and o / pcv - 1.0 <= -(fl - LIMIT_OPEN_TOL)
            sl_hit = lo_gap or (l <= sl_px)
            tp_hit = o >= tp_px or h >= tp_px
            if sl_hit:
                exit_px, tag = (o if lo_gap else sl_px), "sl"
            elif tp_hit:
                exit_px = o if o >= tp_px else tp_px
                tag = "tp_gap" if o >= tp_px else "tp"
        # time exit at open (LD-open queue-unsold rolls)
        if exit_px is None and d >= target:
            if not (pcv is not None and o / pcv - 1.0 <= -(fl - LIMIT_OPEN_TOL)):
                exit_px, tag = o, "time"
        if exit_px is not None:
            base = entry * (1 + COST_X1) if prev_mark is None else prev_mark
            rets.append((d, exit_px * (1 - COST_X1) / base - 1.0))
            return rets, d, tag, entry
        # mid-day mark at close
        base = entry * (1 + COST_X1) if prev_mark is None else prev_mark
        rets.append((d, c / base - 1.0))
        prev_mark = float(c)
        d += 1
    return rets, None, "open", entry      # bars exhausted / data end


def replay(cal, pos_of, sigs, bars, end_pos, tpsl=True):
    """Full deterministic REV-OSC replay from the anchor grid over the
    SIG/BARS lane faces -> daily series + counters + open positions."""
    T = len(cal)
    anchor_pos = pos_of[ANCHOR]
    first_mark_pos = anchor_pos + 1
    domain = (list(range(first_mark_pos, end_pos + 1))
              if end_pos >= first_mark_pos else [])
    grid_positions = list(range(anchor_pos, end_pos + 1, GRID_STEP))
    b = {0: {}, 1: {}}
    counters = {"grid_days": len(grid_positions), "live_cohorts": 0,
                "pending_cohorts": 0,
                "skips": {"awaiting_signal": 0, "gate_closed": 0,
                          "thin_market": 0, "empty_fill": 0},
                "entries": 0, "unfillable": 0,
                "exits": {"time": 0, "tp": 0, "tp_gap": 0, "sl": 0},
                "cohort_buckets": []}
    entry_events = set()
    open_positions = []
    boards = {"main"}
    for gp in grid_positions:
        sig = sigs.get(cal[gp])
        if sig:
            for p in sig.get("picks", []):
                boards.add(p.get("board", "main"))
    fl_by_board = {bd: [floor_for(bd, cal[p]) for p in range(T)]
                   for bd in boards}
    name_cache = {}
    for k, gp in enumerate(grid_positions):
        sig = sigs.get(cal[gp])
        if sig is None:
            counters["skips"]["awaiting_signal"] += 1
            continue
        if not (sig.get("gate") or {}).get("open"):
            counters["skips"]["gate_closed"] += 1
            continue
        if sig.get("thin_market"):
            counters["skips"]["thin_market"] += 1
            continue
        entry_pos = gp + 1
        if entry_pos > end_pos:
            counters["pending_cohorts"] += 1
            continue
        counters["live_cohorts"] += 1
        counters["cohort_buckets"].append(k % 2)   # judged mirror: k over
        bucket = k % 2                            # the full grid sequence
        entry_events.add(entry_pos)
        filled = 0
        for pick in sig.get("picks", []):
            code = pick["code"]
            board = pick.get("board", "main")
            if code not in name_cache:
                name_cache[code] = prep_name(bars.get(code), pos_of, T)
            rows, prev_c = name_cache[code]
            res = path_engine(rows, prev_c, fl_by_board[board], entry_pos,
                              end_pos, tpsl)
            if res is None:
                counters["unfillable"] += 1
                continue
            rets, exit_pos, tag, entry_px = res
            filled += 1
            counters["entries"] += 1
            if tag == "open":
                open_positions.append({
                    "code": code, "board": board, "bucket": bucket,
                    "grid_date": cal[gp], "entry_date": cal[entry_pos],
                    "entry_px": round(entry_px, 4),
                    "last_activity_date": (cal[rets[-1][0]]
                                           if rets else cal[entry_pos]),
                    "status": "open (bars exhausted or data end; "
                              "no fake tail exit -- live-ops law)"})
            else:
                counters["exits"][tag] += 1
            for p, r in rets:
                b[bucket][p] = b[bucket].get(p, 0.0) + NAME_W * r
        if filled == 0:
            counters["skips"]["empty_fill"] += 1
    series = {p: 0.5 * (b[0].get(p, 0.0) + b[1].get(p, 0.0)) for p in domain}
    return {"series": series, "counters": counters,
            "entry_events": sorted(entry_events),
            "open_positions": open_positions}


# ------------------------------------------------------- accounts/marks
def build_marks(cal, series, hist, entry_events, account):
    """Attribution rows + equity. SYSTEM-V1: w_eff glide law + |dw|*COST_X1
    transition cost; REV-OSC-STD: ret = series (pure sleeve face)."""
    marks = []
    eq = INITIAL_CNY
    w_prev = 0.0
    fail_closed_days = 0
    ee = set(entry_events)
    for p in sorted(series):
        d = cal[p]
        state = state_for_day(hist, d)
        route, fc = route_for_state(state)
        if fc:
            fail_closed_days += 1
        if account == "SYSTEM-V1":
            w_eff = route["rev_osc"] if p in ee else w_prev
            dw = w_eff - w_prev
            ret = w_eff * series[p] - abs(dw) * COST_X1
            w_prev = w_eff
        else:
            w_eff = 1.0
            ret = series[p]
        eq *= 1.0 + ret
        marks.append({"date": d, "state": state, "route": route,
                      "w_eff": round(w_eff, 4),
                      "series": round(series[p], 8),
                      "ret": round(ret, 8),
                      "equity_cny": round(eq, 2)})
    return marks, eq, fail_closed_days


def marks_dd(marks, initial):
    """Peak-to-trough dd over the marked equity path (initial included)."""
    peak, dd = initial, 0.0
    for m in marks:
        peak = max(peak, m["equity_cny"])
        dd = min(dd, m["equity_cny"] / peak - 1.0)
    return round(dd, 6)


def _marks_summary(marks, eq, fail_closed_days):
    return {"bars": len(marks),
            "first_date": marks[0]["date"] if marks else None,
            "last_date": marks[-1]["date"] if marks else None,
            "cumulative_ret": round(eq / INITIAL_CNY - 1.0, 8),
            "current_dd": marks_dd(marks, INITIAL_CNY),
            "active_days": sum(1 for m in marks if abs(m["ret"]) > 1e-12),
            "fail_closed_route_days": fail_closed_days}


def build_account_states(cal, rep, hist, bars_cutoff, lane_files):
    """Pure state builders for both accounts (no wall clock, no disk)."""
    counters = rep["counters"]
    common = {
        "schema": "system_v1_paper_v1",
        "ticket": TICKET, "order": ORDER_REF,
        "lane": "system-v1 live paper (results/system_v1_paper/, "
                "independent lane)",
        "lane_guard": f"{LANE_OWNER}-only-writes (R31 family); every other "
                      "machine = stdout-only honest no-op",
        "guard": "shadow record-only (zero interference, zero canon/"
                 "production-account touch)",
        "experimental": True,
        "initial_cash_cny": INITIAL_CNY,
        "denomination": "CNY",
        "anchor_grid": ANCHOR,
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "paper_start": "first mark day = first trading day strictly after "
                       f"the anchor grid {ANCHOR} (out-of-sample by "
                       "construction; O-2045 daily-marks semantics)",
        "machinery": {
            "engine": "per-name daily-mark-to-market MIRROR of "
                      "rev_osc_stock_p1.sim_stock (constants imported, "
                      "zero re-implementation; selftest leg-1 path product "
                      "== _net within 1e-9)",
            "cell": "FY_BG_TP8 live face (O-2335 three-piece): "
                    "first-bullish + bear-gate (SIG gate.open, 510300<MA200 "
                    "proxy per SIG disclosure) + TP +8%, hold H=7",
            "grid": f"every {GRID_STEP}th td from anchor {ANCHOR} on the "
                    "510300 ETF calendar (frozen)",
            "buckets": "2 capital buckets, cohort k%2 over the FULL grid "
                       "sequence (skips included, judged mirror); max "
                       "concurrent 2 (H=7 < 2*grid step)",
            "name_weight": NAME_W,
            "name_weight_note": "frozen equal weight 1/10 per name (idle "
                                "slots = cash); judged eq face = 1/min(10, "
                                "qualified) -- picks<10 divergence disclosed",
            "cost_face": f"x1 {COST_X1}/side (13.041bp, V1 stock schedule, "
                         "P4_BATCH2 s3.2 anchor, COST_X1 import)",
            "entry_law": "T+1 open conservative proxy (O-1132): unfillable "
                        "= open NaN or near-limit-up open "
                        "(open/prev_close-1 >= floor-0.002)",
            "bars_exhausted_law": "status open, no fake tail exit "
                                  "(live-ops law; judged tail face not "
                                  "applicable forward)",
            "signal_face": "results/rev_osc_live SIG-<date>/BARS-<date> "
                           "consumed; missing SIG = awaiting_signal skip "
                           "(counted); BARS merge = latest-wins (qfq truth); "
                           "git = transfer channel (fleet/TRANSFER.md)",
        },
        "engine_counters": counters,
        "open_positions": rep["open_positions"],
        "lane_files": lane_files,
        "panel_cutoff": bars_cutoff,
        "etf_calendar_last": cal[-1] if cal else None,
        "awaiting_lane_data": bars_cutoff is None,
        "audit": {"network": "zero", "ledger_trials_added": 0,
                  "seed_registry_added": 0,
                  "adoption": "ZERO (live paper observation lane)"},
    }
    v1_marks, v1_eq, v1_fc = build_marks(cal, rep["series"], hist,
                                         rep["entry_events"], "SYSTEM-V1")
    std_marks, std_eq, _ = build_marks(cal, rep["series"], hist,
                                       rep["entry_events"], "REV-OSC-STD")
    v1 = dict(common)
    v1.update({
        "account": "SYSTEM-V1",
        "account_face": "decision-chain LIVE face: L1 clock state -> L2 "
                        "route -> deployed sleeve = rev_osc only (v1.0 "
                        "stubs); allocation semantics (w_eff x series; no "
                        "mid-hold forced liquidation; glide law + "
                        "transition cost)",
        "l1_source": "harness-accumulated state_hist from "
                     "results/market_clock/call_latest.json (append-when-"
                     "advances, never truncate; state_for_day = latest "
                     "asof STRICTLY < day)",
        "route_table_v1_0": {
            "rows": ROUTE_TABLE_V1,
            "yellow_maps_to": "CHOP",
            "instantiation": "harness-frozen numeric instantiation of "
                             "SYSTEM_V1_PREREG L2 qualitative rows",
            "amendment_window": "until first mark 2026-09-28 (frozen spec "
                                "R308; after that = law)",
            "l5_note": "call_latest position_cap_ladder carried in "
                       "state_hist entries (informational; route caps are "
                       "the frozen table rows)",
        },
        "stubs_v1_0": {
            "trend_sleeve": "weight-bearing-0 (member classification + "
                             "T-86 lowamp pending)",
            "lowvol_sleeve": "weight-bearing-0 (same)",
            "cash_leg": "residual idles in cash at 0% accrual (repo "
                        "ladder pending T-88 s3 collectors)",
            "fail_closed": True,
        },
        "report_wiring": "s4 WIRED (R310 bm-a): daily_scorecard SYSTEM-V1 + "
                         "REV-OSC lines with sleeve attribution + town "
                         "GM-office rows + 2026-10-31 bench rows (SPM J1-J4 "
                         "caliber, three-lines-three-judgments); consumers "
                         "read this lane read-only, zero handwriting",
        "state_hist": hist,
        "marks": v1_marks,
        "marks_summary": _marks_summary(v1_marks, v1_eq, v1_fc),
        "equity_cny": round(v1_eq, 2),
    })
    std = dict(common)
    std.update({
        "account": "REV-OSC-STD",
        "account_face": "standalone sleeve face (same engine replay, no "
                        "route overlay): ret = series",
        "marks": std_marks,
        "marks_summary": _marks_summary(std_marks, std_eq, 0),
        "equity_cny": round(std_eq, 2),
    })
    return v1, std


def write_if_changed(path, state):
    """Atomic write; no-op when content (sans the wall-clock envelope) is
    identical on disk. Returns True when the file was written."""
    if os.path.exists(path):
        try:
            old = _read_json(path)
            old_core = {k: v for k, v in old.items() if k != "updated"}
            new_core = {k: v for k, v in state.items() if k != "updated"}
            if json.dumps(old_core, sort_keys=True) == \
                    json.dumps(new_core, sort_keys=True):
                return False
        except Exception:                                       # noqa: BLE001
            pass                        # torn file -> full rewrite
    new = dict(state)
    new["updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
    _atomic_json(path, new)
    return True


# ------------------------------------------------------------------ run
def run() -> int:
    try:
        with open(MACHINE_JSON, encoding="utf-8-sig") as fh:
            mid = json.load(fh).get("machine_id", "")
        if mid != LANE_OWNER:
            print(f"system_v1_paper: lane guard (owner={LANE_OWNER}, "
                  f"this={mid}) -- stdout-only honest no-op")
            return 0

        cal = load_etf_calendar()
        pos_of = {d: i for i, d in enumerate(cal)}
        if ANCHOR not in pos_of:
            print(f"system_v1_paper mechanism fault: anchor {ANCHOR} "
                  "missing from the 510300 calendar face")
            return 2
        sigs, bars, bars_cutoff, n_sig, n_bars = load_sigs_bars()
        call_latest = _read_json(CALL_LATEST) if os.path.exists(CALL_LATEST) \
            else None
        hist = []
        if os.path.exists(V1_PATH):
            try:
                hist = _read_json(V1_PATH).get("state_hist") or []
            except Exception:                                   # noqa: BLE001
                hist = []
        hist = update_state_hist(hist, call_latest)

        anchor_pos = pos_of[ANCHOR]
        if bars_cutoff is None:
            end_pos = anchor_pos - 1           # armed, empty marks domain
        elif bars_cutoff in pos_of:
            end_pos = min(len(cal) - 1, pos_of[bars_cutoff])
        else:
            # bars lane ahead of the ETF calendar face (e.g. bm-b export
            # landed before this machine's update_daily refresh): clamp
            # honestly to the calendar; the ahead-bars days stay pending.
            end_pos = len(cal) - 1

        rep = replay(cal, pos_of, sigs, bars, end_pos)
        v1_state, std_state = build_account_states(
            cal, rep, hist, bars_cutoff, {"sig": n_sig, "bars": n_bars})
        w1 = write_if_changed(V1_PATH, v1_state)
        w2 = write_if_changed(STD_PATH, std_state)
        if not (w1 or w2):
            print(f"system_v1_paper: marks already at lane cutoff "
                  f"{bars_cutoff} -- no-op (idempotent)")
            return 0
        c = rep["counters"]
        print(f"system_v1_paper: SYSTEM-V1 {'written' if w1 else 'no-op'} | "
              f"REV-OSC-STD {'written' if w2 else 'no-op'} | cutoff="
              f"{bars_cutoff} marks={len(v1_state['marks'])} "
              f"entries={c['entries']} skips={c['skips']} "
              f"pending={c['pending_cohorts']} "
              f"open_pos={len(rep['open_positions'])} -> {OUT_DIR}")
        return 0
    except SystemExit as e:
        print(f"system_v1_paper mechanism fault (gate): {e}")
        return 2
    except Exception as e:                                      # noqa: BLE001
        print(f"system_v1_paper mechanism fault: {e}")
        return 2


# -------------------------------------------------------------- selftest
def selftest() -> int:
    ok_all = True

    def ok(name, cond):
        nonlocal ok_all
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
        ok_all &= bool(cond)
        return cond

    import shutil
    import tempfile

    tmp = tempfile.mkdtemp(prefix="sysv1_selftest_")
    try:
        # [1/10] constants tripwire (frozen mirror, zero re-derivation)
        ok("constants imported from judged runner "
           "(TP/SL/COST_X1/GRID_STEP/TOL/floors)",
           (TP, SL, COST_X1, GRID_STEP, LIMIT_OPEN_TOL, MAIN_FLOOR,
            WIDE_FLOOR)
           == (1.08, 0.90, 0.0013041, 5, 0.002, 0.0975, 0.1975))

        # [2/10] floor era switches (board x era, judged face)
        ok("floor: main 0.0975; chinext 20cm from 2020-08-24; "
           "star from 2019-07-22",
           floor_for("main", "2026-09-24") == 0.0975
           and floor_for("chinext", "2020-08-21") == 0.0975
           and floor_for("chinext", "2020-08-24") == 0.1975
           and floor_for("star", "2019-07-19") == 0.0975
           and floor_for("star", "2019-07-22") == 0.1975)

        # [3/10] route integrity + YELLOW->CHOP + fail-closed rows
        rows_ok = all(r["rev_osc"] <= r["cap"] and r["rev_osc"] / TOP_N <= 0.15
                      for r in ROUTE_TABLE_V1.values())
        fc_none, tag1 = route_for_state(None)
        fc_bad, tag2 = route_for_state("PURPLE")
        ok("route table v1.0: deployed<=cap, single-name<=15%, ORANGE row "
           "verbatim, YELLOW->CHOP, unknown/None fail-closed zero",
           rows_ok
           and ROUTE_TABLE_V1["ORANGE"] == {"rev_osc": 0.30, "trend": 0.10,
                                            "lowvol": 0.10, "cap": 0.50}
           and route_for_state("YELLOW")[0] == ROUTE_TABLE_V1["CHOP"]
           and fc_none == dict(FAIL_CLOSED_ROW)
           and tag1 == "fail_closed_no_state"
           and fc_bad == dict(FAIL_CLOSED_ROW))

        # [4/10] L1: append-when-advances only, never truncate;
        #         state_for_day strict-< boundary
        call_a = {"asof": "2026-09-24", "regime_v3": {"state": "ORANGE"},
                  "clock_cell": "ORANGE_COOL", "position_cap_ladder": 0.5}
        call_b = {"asof": "2026-09-25", "regime_v3": {"state": "GREEN"},
                  "clock_cell": "GREEN_COOL", "position_cap_ladder": 0.8}
        h1 = update_state_hist([], call_a)
        h2 = update_state_hist(h1, call_a)          # same asof -> no dup
        h3 = update_state_hist(h2, call_b)           # advance -> append
        h4 = update_state_hist(h3, call_a)          # older -> no-op
        multi = [{"asof": "2026-09-22", "state": "GREEN"},
                 {"asof": "2026-09-24", "state": "ORANGE"}]
        ok("L1: append-when-advances only, never truncate; "
           "state_for_day asof STRICTLY < day",
           len(h1) == 1 and len(h2) == 1 and len(h3) == 2 and len(h4) == 2
           and h3[-1]["state"] == "GREEN"
           and state_for_day(multi, "2026-09-22") is None
           and state_for_day(multi, "2026-09-23") == "GREEN"
           and state_for_day(multi, "2026-09-24") == "GREEN"
           and state_for_day(multi, "2026-09-25") == "ORANGE")

        # [5/10] MIRROR-PRODUCT x50 vs imported sim_stock
        import rev_osc_stock_p1 as R
        t_saved = R.T_EXPECT
        T = 96
        R.T_EXPECT = T
        try:
            cal = [str(dd.date())
                   for dd in pd.bdate_range("2026-04-01", periods=T)]
            pos_of = {d: i for i, d in enumerate(cal)}
            rng = np.random.default_rng(20260927)
            n_cmp = n_unfill = 0
            parity = True
            for case in range(50):
                entry_t = int(rng.integers(5, 46))
                Hc = int(rng.choice([2, 5, 7, 10]))
                tpsl = bool(rng.random() < 0.8)
                op = np.full(T, np.nan)
                hi = np.full(T, np.nan)
                lo = np.full(T, np.nan)
                cl = np.full(T, np.nan)
                run = 8.0 + rng.random() * 12.0
                for i in range(T):
                    prev = run
                    if i >= T - 15:                 # clean tail: exits land
                        o = prev * (1 + rng.normal(0, 0.005))
                        c = o * (1 + rng.normal(0, 0.02))
                    else:
                        u = rng.random()
                        if u < 0.10:                # suspension day (all NaN)
                            continue
                        if u < 0.20:                # sealed limit-down day
                            c = prev * 0.90
                            op[i] = hi[i] = lo[i] = cl[i] = c
                            run = c
                            continue
                        if u < 0.30:                # gap day (limit faces)
                            o = prev * (1 + rng.choice(
                                [-0.09, -0.05, 0.05, 0.09]))
                            c = o * (1 + rng.normal(0, 0.02))
                        else:                       # normal day
                            o = prev * (1 + rng.normal(0, 0.006))
                            c = o * (1 + rng.normal(0, 0.025))
                    h_ = max(o, c) * (1 + abs(rng.normal(0, 0.006)))
                    l_ = min(o, c) * (1 - abs(rng.normal(0, 0.006)))
                    op[i], hi[i], lo[i], cl[i] = o, h_, l_, c
                    run = c
                fl2d = np.full((1, T), MAIN_FLOOR, dtype=np.float64)
                P = {"col": {"open": np.ascontiguousarray(op[None, :]),
                             "high": np.ascontiguousarray(hi[None, :]),
                             "low": np.ascontiguousarray(lo[None, :]),
                             "close": np.ascontiguousarray(cl[None, :])},
                     "fl": fl2d}
                net, ed, tag = R.sim_stock(P, 0, entry_t, Hc, tpsl, COST_X1)
                nbars = {cal[i]: (float(op[i]), float(hi[i]), float(lo[i]),
                                  float(cl[i]))
                         for i in range(T)
                         if np.isfinite(op[i]) and np.isfinite(cl[i])}
                rows, prev_c = prep_name(nbars, pos_of, T)
                fl_arr = [MAIN_FLOOR] * T
                res = path_engine(rows, prev_c, fl_arr, entry_t + 1, T - 1,
                                  tpsl, hold=Hc)
                if net is None:
                    n_unfill += 1
                    if res is not None:
                        parity = False
                    continue
                if res is None:
                    parity = False
                    continue
                rets, xpos, xtag, _ = res
                prod = 1.0
                for _p, _r in rets:
                    prod *= 1.0 + _r
                n_cmp += 1
                if not (abs(prod - 1.0 - net) < 1e-9 and xtag == tag
                        and xpos == ed):
                    parity = False
            ok("mirror-product x50: daily path product == sim_stock _net "
               "(<1e-9) + tag/exit/unfillable parity",
               parity and n_cmp >= 25 and n_cmp + n_unfill == 50)
        finally:
            R.T_EXPECT = t_saved

        # [6-8] synthetic lane faces: engine taxonomy + accounting + open law
        T2 = 36
        cal2 = [str(dd.date())
                for dd in pd.bdate_range("2026-09-24", periods=T2)]
        pos_of2 = {d: i for i, d in enumerate(cal2)}
        codes = [f"60000{i}" for i in range(10)]

        def sig_live(date):
            return {"date": date, "gate": {"open": True},
                    "thin_market": False,
                    "picks": [{"code": c, "board": "main", "rank": i}
                              for i, c in enumerate(codes)]}

        sigs2 = {cal2[gp]: sig_live(cal2[gp])
                 for gp in range(0, T2, GRID_STEP)}
        sigs2[cal2[5]]["gate"]["open"] = False            # gate_closed
        sigs2[cal2[10]] = {"gate": {"open": True},         # thin
                           "thin_market": True, "picks": []}
        del sigs2[cal2[15]]                                 # awaiting_signal
        bars2 = {c: {d: (10.0, 10.1, 9.9, 10.0) for d in cal2}
                 for c in codes}
        rep2 = replay(cal2, pos_of2, sigs2, bars2, T2 - 1)
        c2 = rep2["counters"]
        ok("engine: skip taxonomy (gate_closed/thin/awaiting_signal) + "
           "pending cohort + bucket alternation k%2 over full grid seq",
           c2["skips"]["gate_closed"] == 1
           and c2["skips"]["thin_market"] == 1
           and c2["skips"]["awaiting_signal"] == 1
           and c2["live_cohorts"] == 4
           and c2["pending_cohorts"] == 1
           and c2["cohort_buckets"] == [0, 0, 1, 0]
           and c2["entries"] == 40
           and c2["exits"]["time"] == 30)

        r1 = 10.0 / (10.0 * (1 + COST_X1)) - 1.0
        s1 = 0.5 * (10 * NAME_W) * r1
        ok("marks accounting: series = 0.5*(b0+b1), name w=0.1, "
           "entry-day cost split + exit-day cost split",
           abs(rep2["series"][1] - s1) < 1e-12
           and abs(rep2["series"][2] - 0.0) < 1e-12
           and abs(rep2["series"][8] - 0.5 * (-COST_X1)) < 1e-12)

        hist2 = [{"asof": cal2[0], "state": "ORANGE"}]
        m1, _, _ = build_marks(cal2, rep2["series"], hist2,
                               rep2["entry_events"], "SYSTEM-V1")
        exp1 = 0.30 * s1 - 0.30 * COST_X1
        ok("SYSTEM-V1 overlay: ORANGE 0.30 deploy at first entry day + "
           "|dw|*COST_X1 transition cost; hold days no new cost",
           m1[0]["w_eff"] == 0.30 and abs(m1[0]["ret"] - exp1) < 1e-9
           and m1[1]["w_eff"] == 0.30 and abs(m1[1]["ret"]) < 1e-12)

        hist3 = [{"asof": cal2[0], "state": "ORANGE"},
                 {"asof": cal2[20], "state": "GREEN"}]
        m2, _, fc2 = build_marks(cal2, rep2["series"], hist3,
                                 rep2["entry_events"], "SYSTEM-V1")
        exp21 = 0.00 * rep2["series"][21] - 0.30 * COST_X1
        ok("w_eff glide law: route change takes effect at the first entry "
           "day after the change (no mid-hold forced liquidation) + "
           "fail-closed route-day counter",
           m2[20]["w_eff"] == 0.0
           and abs(m2[20]["ret"] - exp21) < 1e-9 and fc2 == 0
           and all(m2[i]["w_eff"] == 0.30 for i in range(20)))

        ok("bars exhausted = status open, NO fake tail exit "
           "(cohort entered pos 31, H=7 target 38 > domain 35)",
           len(rep2["open_positions"]) == 10
           and all(p["entry_date"] == cal2[31]
                   and p["status"].startswith("open")
                   for p in rep2["open_positions"]))

        # [9/10] no-op predicate (content-hash compare, wall ts envelope)
        st = {"schema": "x", "marks": [{"date": "2026-09-28", "ret": 0.01}],
              "equity_cny": 1010000.0}
        p9 = os.path.join(tmp, "st.json")
        w_a = write_if_changed(p9, st)
        w_b = write_if_changed(p9, st)
        st2 = dict(st)
        st2["equity_cny"] = 1020000.0
        w_c = write_if_changed(p9, st2)
        ok("no-op predicate: identical content -> no rewrite; change -> "
           "write; wall clock only in envelope",
           w_a and not w_b and w_c
           and _read_json(p9).get("updated") is not None)

        # [10/10] B7b consumer contract + stub/state disclosure fields
        v1, std = build_account_states(
            cal2, rep2, hist2, cal2[T2 - 1], {"sig": 8, "bars": 1})
        prod_sig_keys = {"schema", "date", "gate", "universe", "thin_market",
                         "picks", "params", "cost_ref", "panel_cutoff",
                         "updated"}
        prod_gate_keys = {"face", "signal_date", "close", "ma200", "open",
                          "disclosure"}
        prod_pick_keys = {"code", "board", "drop20", "drop60", "close",
                          "open", "amount20", "rank"}
        prod_bars_keys = {"schema", "date", "rows", "updated"}
        ok("B7b contract: consumed keys subset of producer schema; "
           "stub/route/lane disclosure fields present",
           SIG_KEYS <= prod_sig_keys and GATE_KEYS <= prod_gate_keys
           and PICK_KEYS <= prod_pick_keys and BARS_KEYS <= prod_bars_keys
           and "route_table_v1_0" in v1 and "stubs_v1_0" in v1
           and "weight-bearing-0" in v1["stubs_v1_0"]["trend_sleeve"]
           and "0% accrual" in v1["stubs_v1_0"]["cash_leg"]
           and v1["evidence_cutoff"] == EVIDENCE_CUTOFF
           and v1["account"] == "SYSTEM-V1" and std["account"] == "REV-OSC-STD"
           and v1["marks_summary"]["bars"] == len(v1["marks"]))

        if not ok_all:
            print("SELFTEST FAILED")
            return 2
        print("selftest: ALL LEGS PASS")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "selftest":
        return selftest()
    if mode == "run":
        return run()
    # fail-closed argv (r232 law): unknown/missing arg -> usage, exit 2
    print(f"usage: {sys.argv[0]} [run|selftest] (got {mode!r})")
    return 2


if __name__ == "__main__":
    sys.exit(main())
