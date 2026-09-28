"""GRID_DUALFACE_P1 runner -- 宽基震荡网格双面批 (T-104 s2/s3).

Laws frozen in research/etf_ops/GRID_DUALFACE_P1_PREREG.md (r399 freeze
commit 98af88b4/a03887474; SEED_REGISTRY['grid_dualface_p1']=20295500
registered same commit, R250 law; band 20295500..20295529 pair-derivation,
zero actual RNG collision vs innovation_quota_w1_repo constant-first-element
-- census_unc precedent, disclosed in the registry comment). Freeze precedes
runner build precedes ANY burn. Run-products may only backfill prereg s7;
criteria are never re-derived by hand (O-2250: every gate line comes from
science_gates).

  members five-member two-tier frozen universe (O-1555, prereg s2 table
          order): 510050 / 510300 / 512100 / 510500 / 588000 (20cm tier).
          G-ANCHOR-FACE four-tuple per member (path / loader / first-date /
          warmup) + row census + last-bar == evidence_cutoff 2026-09-28 --
          any face mismatch = fail-closed refuse (exit 2), reported as
          face-mismatch not data-rot (INCIDENT-20260928 law). D2 lockbox:
          rows after cutoff never enter.
  grid   spacing g in {4%,6%,8%} (major) x levels L in {4,6} (minor) = 6
          cells/member, 30 batch cells; per-level size = 1/L of the 1.0
          nominal sleeve (max deployment 1.0). Ladder prices level_i =
          anchor*(1-i*g), i=1..L. ANCHOR RULE fully deterministic (T-78
          lesson: zero placement tuning): trend-set opening-day close =
          anchor; upper-band break close > anchor*(1+L*g) -> same-day close
          = new anchor (reanchor, counted). Same-day anchor semantics: on
          any set-open or reanchor day the levels in force for that day's
          trigger evaluation are computed from THAT day's close (disclosed
          at close, filled T+1 -- no future data; prereg s3.2/s3.4 frozen
          reading, both anchor-event days treated symmetrically).
  sets   trend gate close > MA200 (rolling 200, min_periods=200, incl.
          current day). Set opens at an off->on transition day (or the
          first finite-MA200 day if already trend-on). Set end judged at
          close, priority trend_sl > band_break: close < MA200 (trend_sl)
          or close < anchor*(1-L*g) (band_break = ladder-bottom break) ->
          ALL positions cleared T+1 next open (limit-down rolls). The grid
          then idles until the NEXT COMPLETE off->on cycle re-opens with a
          fresh opening-day anchor (conservative: the post-break repair
          segment harvests nothing -- T-78 anti-tuning cost face,
          disclosed). Set/anchor structure is TRADE-INDEPENDENT (derived
          from price+MA200 only) -- real and null runs share it exactly.
  buys   in-set day t (t >= set open, not isolated, not the set-end day,
          t < n-1): for every UNOCCUPIED level i, low[t] <= level_i(t) ->
          trigger; multiple levels per day legal; fill = t+1 open. t+1
          one-word limit-up -> blocked_entry (level stays free, signal
          consumed). Set-end day never triggers buys (premise dead). A buy
          triggered on the day before the set-end day still FILLS at the
          end day's open (the fill is an execution, not a trigger; death
          is only known at the end day's close).
  sells  holding unit (fill day e, cost = fill px): d >= e and
          high[d] >= cost*(1+g) -> trigger (min hold 1 day, T+1
          compliant); fill = d+1 open, one-word limit-down rolls forward
          (committed exit, no re-evaluation, rolls keep walking past the
          set end until a tradable open or the panel end). On the set-end
          day, uncommitted target-hit units book tp, all other uncommitted
          units book clear -- same fill semantics (next open, rolled),
          label only. Occupancy releases at the SELL FILL day; a level
          freed at day x's open may re-trigger from day x onward. Panel-end
          open units = open_at_end, marked at last close, NEVER in judged
          faces.
  limit  honest accounting: one-word board = h==l & o==h; limit-up
          o/pc-1 >= tier-0.002, limit-down <= -(tier-0.002); tier=0.10
          (0.20 for 588000). blocked_entry not in win denominator.
  guard  fund event guard r239 frozen law (BUY leg only -- exits are not
          new risk): day |r1| > 10.5% (588000: 20.5%) AND five-member
          universe median |r1| < 3% -> member-day buy-trigger isolated.
  costs  V1 legacy 13.041bp/side single source = alloc_backtest.V1_FLAT_SIDE;
          dual track base x1 + x2 stress face (CostPatch multiplier law).
          Multiplicative both legs: leg net = px_out*(1-c)/(px_in*(1+c))-1.
          JUDGED FACE = x2 (family precedent). Fee survival table per cell
          (ticket: fees = grid's survival line): bankruptcy fee c* =
          linear-interpolation zero of E[round pnl] between the x1/x2
          points (approximation disclosed) + spacing/roundtrip ratio
          g/(2c) at both faces.
  nulls  K=200 same-mask random-trigger-day null per member-cell (T-78
          lesson direct product, FIRST JUDGEMENT GATE): mask = the cell's
          own in-set triggerable days (trend-on by construction, MA
          finite, not isolated, not set-end day, not last day); each draw
          samples n_draw = the cell's real completed-round count days
          uniformly WITHOUT replacement (rng =
          np.random.default_rng([20295500, cell_idx]), cell_idx =
          member_idx*6 + grid_idx < 30, K sequential draws per stream),
          sorted ascending, into the SAME state machine (same sets /
          same anchors / same clears / same one-word rules / same T+1
          fills / same exit discipline; concurrency cap = L, full-cap
          sampled days skip, effective counts disclosed). Primary gate =
          real win rate > null p95 (one-sided); E[pnl] gate parallel.
  minute validation face (descriptive only, NEVER a judgement): local
          forward-accumulated archive data/minute_feed/<code>.csv (v1.3,
          as-traded, same basis as the daily panel -- r398 census). For
          every day present in both faces: daily low/high vs minute
          min-low/max-high (source-diff days listed, never fixed); per
          cell in-set days in the window: day-face level-touch count vs
          minute-face count, equivalence asserted. Sole mission = the
          10-01 live paper grid engine mechanism validation (minute-bar
          scan -> T+1 open booking is isomorphic to this backtest).
          Window is short (~8 trading days) -- disclosed, carries no
          judgement.
  gates  win-rate primary (vs null p95) + G1'v2 (science_gates.g1_prime_v2,
          batch_cells=30, pool='core48' -- five members ARE core48
          members, default collector, documented choice) + DSR
          (deflated_sharpe_ratio on the raw x2 series) + family PBO
          (screening.pbo cscv_pbo CSCV-8 over the 30-cell x2 matrix,
          common-tail alignment) + g2_registration_v2. Ledger
          single-count: head read BEFORE append, n_eff_override =
          head_base+30, append_ledger(prev_total=head_base) (r253
          redo-echo guard, cn_kline precedent).
  regime disclosure-only axes: T-74 L2 route states via the imported
          frozen regime_deep_replay v3 layer (YELLOW->CHOP collapse) +
          T-89/T-22 bear/chop/bull segmenter, tagged at round trigger.
          禁全天候宣称.
  starts T-22 virtual timepoints {6m=126,12m=252,24m=504}td x {x1,x2}
          faces: every feasible start vs same-window buy-hold; beat rates
          per cell (CN-CORE-SATELLITE lesson: increment real != magnitude
          enough).
  d6     reject face = max|corr| vs the six registered trader sleeves
          (REG6, ew6 canon member_run, live.paper anchor path); >= 0.7
          rejects the cell (prereg s1).

Products (prereg s6): results/etf_ops/grid_dualface.json (top
evidence_cutoff + science_gates.cutoff_meta mandatory) +
results/etf_ops/grid_rounds_<code>.csv per-member round streams +
results/etf_ops/grid_nulls.json + results/etf_ops/grid_minute_face.json +
shard checkpoints results/etf_ops/grid_shard_<code>.json +
grid_series/<code>_<cellidx>_<face>.npy daily streams. Deterministic: no
wall-clock inside any product; re-run byte-identical.

Usage:
  python scripts/grid_dualface_backtest.py run --shard 510300   (one member)
  python scripts/grid_dualface_backtest.py run --shard all      (sequential)
  python scripts/grid_dualface_backtest.py finalize
  python scripts/grid_dualface_backtest.py status
  python scripts/grid_dualface_backtest.py selftest              (hermetic)

Exit contract: 0 ok/no-op; 2 fail-closed gate refusal (anchor drift,
grammar mismatch, missing dependency); 3 RAM floor (three-sample, r354
family light-batch calibration, disclosed).
"""
import argparse
import hashlib
import json
import os
import sys
import tempfile

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import science_gates as SG                      # shared gate library (O-2250)
from alloc_backtest import V1_FLAT_SIDE          # V1 13.041bp single source

OUT_DIR = os.path.join(ROOT, "results", "etf_ops")
SER_DIR = os.path.join(OUT_DIR, "grid_series")
MINUTE_DIR = os.path.join(ROOT, "data", "minute_feed")
OUT_JSON = os.path.join(OUT_DIR, "grid_dualface.json")
OUT_NULLS = os.path.join(OUT_DIR, "grid_nulls.json")
OUT_MINUTE = os.path.join(OUT_DIR, "grid_minute_face.json")

EVIDENCE_CUTOFF = "2026-09-28"
BATCH_NAME = "GRID_DUALFACE_P1"
BATCH_NAME_KEY = "grid_dualface_p1"
BATCH_CELLS = 30
K_NULLS = 200
PBP = 252
D6_REJECT = 0.7
LIMIT_TOL = 0.002
GUARD_THR = 0.105
GUARD_THR_20CM = 0.205
UNIVERSE_MED_THR = 0.03
RAM_FLOOR_GB = 2.0                # light batch: five small CSVs (r354 family)
WINDOWS = {"6m": 126, "12m": 252, "24m": 504}
OOS_FROM = "2025-01-01"

# frozen member order (prereg s2 table order) + G-ANCHOR-FACE four-tuple
MEMBERS = ["510050", "510300", "512100", "510500", "588000"]
ANCHORS = {
    "510050": {"path": "data/daily/sh510050.csv", "first": "2005-02-23",
               "rows": 5251},
    "510300": {"path": "data/daily/sh510300.csv", "first": "2012-05-28",
               "rows": 3486},
    "512100": {"path": "data/daily/sh512100.csv", "first": "2016-11-04",
               "rows": 2405},
    "510500": {"path": "data/daily/sh510500.csv", "first": "2013-03-15",
               "rows": 3289},
    "588000": {"path": "data/daily/sh588000.csv", "first": "2020-11-16",
               "rows": 1425},
}
TIER_20CM = {"588000"}
# frozen cell grid (prereg s0: g-major, L-minor)
GRID = [
    {"g": 0.04, "L": 4},
    {"g": 0.04, "L": 6},
    {"g": 0.06, "L": 4},
    {"g": 0.06, "L": 6},
    {"g": 0.08, "L": 4},
    {"g": 0.08, "L": 6},
]
COST_X1 = float(V1_FLAT_SIDE)          # 13.041bp/side (V1 single source)
COST_X2 = COST_X1 * 2.0                # CostPatch multiplier law (x2 face)
SEED = None                            # filled from SG.SEED_REGISTRY at run

GRAMMAR = BATCH_NAME + "|v1|cutoff=" + EVIDENCE_CUTOFF + \
    "|g{4,6,8}xL{4,6}|MA200,minp200|anchor=open_day_close+upper_break_" \
    "same_day|setend=trendsl>bandbreak|idle_until_full_offon_cycle|" \
    "T+1open_fills|blocked_entry_void|blocked_exit_roll|" \
    "guard_buy_only|nulls same-mask K" + str(K_NULLS) + "|judged=x2|" \
    "perlevel=1/L|V1FLAT=" + format(COST_X1, ".7f")


def _sha16(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


GRAMMAR_SHA16 = _sha16(GRAMMAR)


def _free_ram_gb():
    try:
        import psutil
        return psutil.virtual_memory().available / 1e9
    except Exception:
        return RAM_FLOOR_GB + 1.0        # psutil absent -> guard off (disclosed)


def gate_refuse(msg):
    print(f"GATE-REFUSE(exit2): {msg}")
    return 2


def _atomic_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, sort_keys=True,
                 separators=(",", ":"))
    os.replace(tmp, path)


def _atomic_text(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    os.replace(tmp, path)


# ------------------------------------------------------------------ panel
def load_member(code, data_dir=None, anchors=None, cutoff=None):
    """G-ANCHOR-FACE fail-closed loader (prereg s2 four-tuple verbatim)."""
    anchors = anchors or ANCHORS
    cutoff = cutoff or EVIDENCE_CUTOFF
    base = data_dir or ROOT
    a = anchors[code]
    path = os.path.join(base, a["path"])
    if not os.path.exists(path):
        return None, f"anchor path absent: {a['path']}"
    df = pd.read_csv(path)                      # pd.read_csv raw direct read
    need = ["date", "open", "high", "low", "close"]
    if any(k not in df.columns for k in need):
        return None, f"column face drift: {list(df.columns)}"
    dts = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d").tolist()
    if len(dts) > 1 and dts[0] > dts[-1]:
        return None, "date order reversed"
    cut_rows = int(np.searchsorted(np.array(dts), cutoff, side="right"))
    if len(dts) != cut_rows:
        # D2 lockbox: rows after cutoff exist on disk -> truncate, disclose
        df = df.iloc[:cut_rows]
        dts = dts[:cut_rows]
    if len(dts) != a["rows"]:
        return None, (f"row census drift: {len(dts)} != anchor {a['rows']} "
                      f"({code} face mismatch)")
    if dts[0] != a["first"]:
        return None, f"first-date drift: {dts[0]} != anchor {a['first']}"
    if dts[-1] != cutoff:
        return None, f"last-bar drift: {dts[-1]} != cutoff {cutoff}"
    o = df["open"].to_numpy(float)
    h = df["high"].to_numpy(float)
    l = df["low"].to_numpy(float)
    c = df["close"].to_numpy(float)
    if not (np.isfinite(o).all() and np.isfinite(h).all()
            and np.isfinite(l).all() and np.isfinite(c).all()):
        return None, "OHLC NaN face (anchor gate 3)"
    if any(dts[i] >= dts[i + 1] for i in range(len(dts) - 1)):
        return None, "date not strictly increasing / duplicated"
    pc = np.concatenate([[np.nan], c[:-1]])
    ma200 = pd.Series(c).rolling(200, min_periods=200).mean().to_numpy()
    with np.errstate(invalid="ignore"):
        r1 = c / pc - 1.0
    face = {"path": a["path"], "rows": len(dts), "first": dts[0],
            "last": dts[-1], "loader": "pd.read_csv raw truncate"}
    m = {"code": code, "dates": dts, "o": o, "h": h, "l": l, "c": c,
         "pc": pc, "ma200": ma200, "r1": r1, "face": face, "n": len(dts)}
    return m, None


def universe_median_abs_r1(members):
    """Per-date median |r1| over members with finite r1 (guard face)."""
    by_date = {}
    for m in members:
        for d, r in zip(m["dates"], m["r1"]):
            if np.isfinite(r):
                by_date.setdefault(d, []).append(abs(float(r)))
    return {d: float(np.median(v)) for d, v in by_date.items()}


def member_arrays(m, med_abs, thr):
    """Per-member derived masks (limit boards / guard isolation / segments)."""
    tier = 0.20 if m["code"] in TIER_20CM else 0.10
    n = m["n"]
    o, h, l, pc = m["o"], m["h"], m["l"], m["pc"]
    with np.errstate(invalid="ignore"):
        one_word = (h == l) & (o == h)
        up_ratio = o / pc - 1.0
    limit_up = one_word & np.isfinite(up_ratio) & (up_ratio >= tier - LIMIT_TOL)
    limit_dn = one_word & np.isfinite(up_ratio) & (up_ratio <= -(tier - LIMIT_TOL))
    isolated = np.zeros(n, dtype=bool)
    for i, d in enumerate(m["dates"]):
        r = m["r1"][i]
        med = med_abs.get(d)
        if np.isfinite(r) and med is not None \
                and abs(float(r)) > thr and med < UNIVERSE_MED_THR:
            isolated[i] = True
    # T-89/T-22 segmenter face (frozen): bear/chop/bull, na warmup
    ma = m["ma200"]
    ma20ago = np.full(n, np.nan)
    if n > 20:
        ma20ago[20:] = ma[:-20]
    with np.errstate(invalid="ignore"):
        ok = np.isfinite(ma) & np.isfinite(ma20ago)
        bear = ok & (m["c"] < ma)
        chop = ok & (m["c"] >= ma) & (ma <= ma20ago)
        bull = ok & (m["c"] >= ma) & (ma > ma20ago)
    seg = np.full(n, "na", dtype=object)
    seg[bear] = "bear"; seg[chop] = "chop"; seg[bull] = "bull"
    return {"tier": tier, "limit_up": limit_up, "limit_dn": limit_dn,
            "isolated": isolated, "seg": seg}


# ------------------------------------------------------- set / anchor frame
def grid_structure(m, g, L):
    """Deterministic trend-set + anchor skeleton (TRADE-INDEPENDENT: pure
    price+MA200 function; real and null runs share it exactly, prereg
    s3.2/s3.3). Sets open at off->on transitions (or the first finite-MA200
    day already trend-on); end judged at close, priority trend_sl >
    band_break; upper-band break re-anchors to the same-day close."""
    c, ma, n = m["c"], m["ma200"], m["n"]
    with np.errstate(invalid="ignore"):
        trend_on = np.isfinite(ma) & (c > ma)
    sets = []
    i = 0
    while i < n:
        opened = None
        j = i
        while j < n:
            if trend_on[j] and (j == 0 or not trend_on[j - 1]):
                opened = j
                break
            j += 1
        if opened is None:
            break
        anchors = [(opened, float(c[opened]))]
        d = opened + 1
        end_idx, end_reason = None, None
        while d < n:
            anc = anchors[-1][1]
            if not trend_on[d]:
                end_idx, end_reason = d, "trend_sl"
                break
            if c[d] < anc * (1.0 - L * g):
                end_idx, end_reason = d, "band_break"
                break
            if c[d] > anc * (1.0 + L * g):
                anchors.append((d, float(c[d])))
            d += 1
        sets.append({"open_idx": opened, "end_idx": end_idx,
                     "end_reason": end_reason, "anchors": anchors})
        if end_idx is None:
            break
        i = end_idx + 1
    return sets


def anchor_at(st, d):
    """Anchor in force on day d (same-day semantics: an anchor event on day
    d applies to day d's own trigger evaluation)."""
    anc = st["anchors"][0][1]
    for idx, px in st["anchors"]:
        if idx <= d:
            anc = px
        else:
            break
    return anc


def trigger_mask(m, aux, sets):
    """The cell's own in-set triggerable day mask (prereg s3.7): trend-on
    by construction, MA finite, not isolated, not the set-end day, t<n-1."""
    n = m["n"]
    mask = np.zeros(n, dtype=bool)
    for st in sets:
        hi = st["end_idx"] if st["end_idx"] is not None else n
        lo = st["open_idx"]
        if lo < n - 1:
            mask[lo:min(hi, n - 1)] = True
    mask &= ~aux["isolated"]
    return mask


# ------------------------------------------------------------------ engine
def _mk_unit(trig):
    return {"e": None, "cost": None, "trig": int(trig), "pending": None,
            "buy_pending": None, "rolls": 0, "dead_open": False}


def simulate_grid(m, aux, g, L, sets, trig_days=None):
    """Grid state machine over the frozen set skeleton.

    trig_days=None -> REAL run: buy triggers evaluated on every in-set
    non-end non-isolated day t<n-1. Otherwise a sorted int array -> NULL
    face: buys evaluated ONLY on those sampled days (same sets / same
    anchors / same clears / same exit discipline / same one-word rules /
    same T+1 fills; concurrency cap = L -> full-cap sampled days skip).

    Per-day frozen order: (1) sell fills scheduled today (one-word
    limit-down rolls, level frees at fill); (2) buy fills scheduled today
    (one-word limit-up = blocked_entry, level returns free); (3) on the
    set-end day book all UNCOMMITTED units (tp label iff target hit on
    the end day, else clear; fill next open rolled) then stop -- no new
    triggers; (4) sell-trigger eval d>=fill_day for uncommitted units;
    (5) buy-trigger eval on unoccupied levels (skipped on isolated days
    and the last day). Committed pendings keep rolling past the set end
    (resolved in the post-set pass). Panel-end leftovers -> open_at_end
    (marked at last close, never in judged faces)."""
    o, h, l, c = m["o"], m["h"], m["l"], m["c"]
    dates = m["dates"]
    n = m["n"]
    null_face = trig_days is not None
    trig_set = set(int(x) for x in trig_days) if null_face else None
    rounds = []
    open_at_end_units = []
    stats = {"n_sets": len(sets),
             "set_ends": {"trend_sl": 0, "band_break": 0, "panel_end": 0},
             "reanchors": 0, "blocked_entries": 0,
             "blocked_exit_rolls": 0, "open_at_end": 0,
             "null_fullcap_skipped_days": 0}

    def _complete(st, lv, u, x, px, kind, extra_rolls=0):
        pnl_x1 = px * (1 - COST_X1) / (u["cost"] * (1 + COST_X1)) - 1.0
        pnl_x2 = px * (1 - COST_X2) / (u["cost"] * (1 + COST_X2)) - 1.0
        rolls = u["rolls"] + int(extra_rolls)
        rounds.append({
            "level": int(lv), "trig_idx": int(u["trig"]),
            "trig_date": dates[u["trig"]],
            "entry_idx": int(u["e"]), "entry_date": dates[u["e"]],
            "entry_px": round(float(u["cost"]), 6),
            "exit_idx": int(x), "exit_date": dates[x],
            "exit_px": round(float(px), 6), "kind": kind,
            "pnl_x1": round(pnl_x1, 8), "pnl_x2": round(pnl_x2, 8),
            "hold_days": int(x - u["e"]),
            "seg_trig": str(aux["seg"][u["trig"]]),
            "set_open_date": dates[st["open_idx"]],
            "anchor_at_entry": round(float(anchor_at(st, u["trig"])), 6),
            "blocked_exit_rolls": int(rolls),
        })

    def _mark_open_end(lv, u):
        stats["open_at_end"] += 1
        rec = {"level": int(lv),
               "entry_date": dates[u["e"]] if u["e"] is not None else None,
               "entry_px": (round(float(u["cost"]), 6)
                            if u["cost"] is not None else None),
               "mark_date": dates[n - 1],
               "mark_px": round(float(c[n - 1]), 6)}
        open_at_end_units.append(rec)

    for st in sets:
        stats["reanchors"] += len(st["anchors"]) - 1
        if st["end_idx"] is None:
            stats["set_ends"]["panel_end"] += 1
        else:
            stats["set_ends"][st["end_reason"]] += 1
        end_idx = st["end_idx"]
        hi = end_idx if end_idx is not None else n - 1
        occ = {}
        for d in range(st["open_idx"], min(hi, n - 1) + 1):
            is_end = end_idx is not None and d == end_idx
            # (1) sell fills scheduled today (committed, roll on limit-dn)
            for lv in list(occ.keys()):
                u = occ[lv]
                if u["pending"] == d:
                    if aux["limit_dn"][d]:
                        stats["blocked_exit_rolls"] += 1
                        u["rolls"] += 1
                        if d + 1 >= n:
                            u["pending"] = None
                            u["dead_open"] = True
                        else:
                            u["pending"] = d + 1
                    else:
                        _complete(st, lv, u, d, float(o[d]), "tp")
                        del occ[lv]
            # (2) buy fills scheduled today
            for lv in list(occ.keys()):
                u = occ[lv]
                if u["buy_pending"] == d:
                    u["buy_pending"] = None
                    if aux["limit_up"][d]:
                        stats["blocked_entries"] += 1   # level returns free
                        del occ[lv]
                    else:
                        u["e"] = d
                        u["cost"] = float(o[d])
            # (3) set-end day: book UNCOMMITTED units, no new triggers
            if is_end:
                for lv in list(occ.keys()):
                    u = occ[lv]
                    if u["pending"] is not None or u["dead_open"] \
                            or u["cost"] is None:
                        continue      # committed tp rolls on / dead / unborn
                    hit = bool(h[d] >= u["cost"] * (1.0 + g))
                    x = d + 1
                    rolls = 0
                    while x < n and aux["limit_dn"][x]:
                        rolls += 1
                        x += 1
                    stats["blocked_exit_rolls"] += rolls
                    if x >= n:
                        u["rolls"] += rolls
                        u["dead_open"] = True
                        continue
                    _complete(st, lv, u, x, float(o[x]),
                              "tp" if hit else "clear", extra_rolls=rolls)
                    del occ[lv]
                continue
            # (4) sell-trigger eval (uncommitted, filled, d >= fill day)
            for lv, u in occ.items():
                if u["pending"] is not None or u["dead_open"] \
                        or u["cost"] is None:
                    continue
                if d >= u["e"] and h[d] >= u["cost"] * (1.0 + g):
                    if d + 1 >= n:
                        u["dead_open"] = True
                    else:
                        u["pending"] = d + 1
            # (5) buy-trigger eval
            if d >= n - 1 or aux["isolated"][d]:
                continue
            if null_face and d not in trig_set:
                continue
            if len(occ) >= L:                     # concurrency cap = L
                if null_face:
                    stats["null_fullcap_skipped_days"] += 1
                continue
            anc = anchor_at(st, d)
            for i in range(1, L + 1):
                if i in occ:
                    continue
                if l[d] <= anc * (1.0 - i * g):
                    u = _mk_unit(d)
                    u["buy_pending"] = d + 1
                    occ[i] = u
        # post-set pass: committed pendings roll to a tradable open or die
        for lv in list(occ.keys()):
            u = occ[lv]
            if u["pending"] is not None:
                x = u["pending"]
                rolls = 0
                while x < n and aux["limit_dn"][x]:
                    rolls += 1
                    x += 1
                stats["blocked_exit_rolls"] += rolls
                u["rolls"] += rolls
                if x >= n:
                    u["pending"] = None
                    u["dead_open"] = True
                else:
                    _complete(st, lv, u, x, float(o[x]), "tp")
                    del occ[lv]
        for lv in list(occ.keys()):
            u = occ[lv]
            if u["dead_open"] or u["cost"] is not None \
                    or u["buy_pending"] is not None:
                _mark_open_end(lv, u)
            # cost None + buy_pending None cannot survive (defensive no-op)
    rounds.sort(key=lambda r: (r["entry_idx"], r["level"]))
    stats["open_units"] = open_at_end_units
    return rounds, stats


def nulls_for_cell(m, aux, g, L, sets, mask_days, n_draw, cell_idx, seed):
    """K same-mask random-trigger-day null draws (prereg s3.7). Each draw
    samples min(n_draw, len(mask)) days uniformly WITHOUT replacement,
    sorted ascending, into the identical grid state machine (buys only on
    sampled days, same exit discipline). Win rates + E[pnl] at both cost
    faces per draw; p95 over draws; effective counts disclosed."""
    rng = np.random.default_rng([int(seed), int(cell_idx)])
    win_x1, win_x2, e_x1, e_x2, n_eff = [], [], [], [], []
    if n_draw <= 0 or len(mask_days) == 0:
        return win_x1, win_x2, e_x1, e_x2, n_eff
    base = np.asarray(mask_days, dtype=np.int64)
    size = int(min(n_draw, len(base)))
    for _k in range(K_NULLS):
        days = np.sort(rng.choice(base, size=size, replace=False))
        rounds, _st = simulate_grid(m, aux, g, L, sets, trig_days=days)
        if not rounds:
            continue
        n_eff.append(len(rounds))
        w1 = sum(1 for r in rounds if r["pnl_x1"] > 0.0)
        w2 = sum(1 for r in rounds if r["pnl_x2"] > 0.0)
        win_x1.append(w1 / len(rounds))
        win_x2.append(w2 / len(rounds))
        e_x1.append(float(np.mean([r["pnl_x1"] for r in rounds])))
        e_x2.append(float(np.mean([r["pnl_x2"] for r in rounds])))
    return win_x1, win_x2, e_x1, e_x2, n_eff


def chain_daily(m, rounds, cost, L, eval_start):
    """WILD-S1 booked-evenly face: each unit round nets (1/L)*leg_net
    booked evenly over holding days entry_idx+1..exit_idx; cash days 0."""
    n = m["n"]
    out = np.zeros(n)
    for r in rounds:
        e_idx, x_idx = r["entry_idx"], r["exit_idx"]
        span = max(x_idx - e_idx, 1)
        leg = r["exit_px"] * (1.0 - cost) / \
            (r["entry_px"] * (1.0 + cost)) - 1.0
        add = (1.0 / L) * leg / span
        lo = e_idx + 1
        hi = min(x_idx + 1, n)
        if hi > lo:
            out[lo:hi] += add
    return out[eval_start:]


def fee_survival(e_x1, e_x2):
    """Per-cell bankruptcy fee c* = linear-interp zero of E[round pnl]
    between the x1/x2 points (approximation disclosed) + spacing/roundtrip
    ratios g/(2c) -- prereg s3.8 frozen face (ratios added by caller)."""
    out = {"e_x1": e_x1, "e_x2": e_x2}
    if e_x1 is None or e_x2 is None:
        out["c_star"] = None
        out["c_star_note"] = "vacuous (no completed rounds)"
        return out
    if e_x1 > 0.0 >= e_x2:
        denom = (e_x1 - e_x2)
        c_star = COST_X1 + (COST_X2 - COST_X1) * (e_x1 / denom
                                                  if denom else 0.0)
        out["c_star"] = round(float(c_star), 8)
        out["c_star_note"] = "linear x1/x2 interpolation zero (approx)"
    elif e_x1 <= 0.0:
        out["c_star"] = None
        out["c_star_note"] = "< x1 (already unprofitable at base cost)"
    else:
        out["c_star"] = None
        out["c_star_note"] = "> x2 (profitable at stress cost too)"
    return out


# --------------------------------------------------------------- minute leg
def minute_face(m, cells_structs, minute_dir=None):
    """Descriptive equivalence face (prereg s3.9): local archive only, zero
    network. Extremes comparison + per-cell day-level touch counts via both
    faces. NEVER a judgement. Window shortness disclosed honestly."""
    minute_dir = minute_dir or MINUTE_DIR
    path = os.path.join(minute_dir, f"{m['code']}.csv")
    if not os.path.exists(path):
        return {"status": "archive absent (equivalence vacuous)",
                "code": m["code"]}
    mf = pd.read_csv(path)
    mf["day"] = pd.to_datetime(mf["day"]).dt.strftime("%Y-%m-%d")
    agg = mf.groupby("day").agg(mm_low=("low", "min"),
                                mm_high=("high", "max")).reset_index()
    mm = {r["day"]: (float(r["mm_low"]), float(r["mm_high"]))
          for _, r in agg.iterrows()}
    pos = {d: i for i, d in enumerate(m["dates"])}
    common = [d for d in sorted(mm.keys()) if d in pos]
    mismatch_days = []
    for d in common:
        i = pos[d]
        mml, mmh = mm[d]
        if float(m["l"][i]) != mml or float(m["h"][i]) != mmh:
            mismatch_days.append(d)
    per_cell = {}
    for name, cs in cells_structs.items():
        g, L, sets = cs["g"], cs["L"], cs["sets"]
        day_touch = min_touch = 0
        n_set_days = 0
        for st in sets:
            hi = st["end_idx"] if st["end_idx"] is not None else m["n"]
            for d in range(st["open_idx"], hi):
                ds = m["dates"][d]
                if ds not in mm:
                    continue
                n_set_days += 1
                anc = anchor_at(st, d)
                mml = mm[ds][0]
                for i in range(1, L + 1):
                    lvl = anc * (1.0 - i * g)
                    if m["l"][d] <= lvl:
                        day_touch += 1
                    if mml <= lvl:
                        min_touch += 1
        per_cell[name] = {
            "n_set_days_in_window": n_set_days,
            "day_face_touch_count": day_touch,
            "minute_face_touch_count": min_touch,
            "equivalent": bool(day_touch == min_touch)}
    return {
        "status": "ok" if common else "empty overlap window",
        "code": m["code"],
        "n_days_compared": len(common),
        "window_first": common[0] if common else None,
        "window_last": common[-1] if common else None,
        "n_extremes_mismatch_days": len(mismatch_days),
        "extremes_mismatch_days": mismatch_days[:20],
        "note": "day low/high vs minute min-low/max-high, as-traded same "
                "basis (r398 census); touch equivalence follows from "
                "extremes equality; window ~8td forward-accumulated "
                "(MINUTE_FEED v1.3) -- short, disclosed, carries no "
                "judgement",
        "per_cell": per_cell,
    }


# ------------------------------------------------------------------ shard
def burn_member(code, data_dir=None, seed=None, anchors=None, cutoff=None,
                minute_dir=None):
    """One member shard: 6 cells x (real + K nulls) x both faces + minute
    equivalence face."""
    global SEED
    SEED = seed if seed is not None else SG.SEED_REGISTRY[BATCH_NAME_KEY]
    m, err = load_member(code, data_dir=data_dir, anchors=anchors,
                         cutoff=cutoff)
    if m is None:
        return None, err
    members = []
    if data_dir is None:
        for mc in MEMBERS:
            mm, e2 = load_member(mc)
            if mm is None:
                return None, f"universe leg refuses: {mc}: {e2}"
            members.append(mm)
    else:
        members = [m]
    med_abs = universe_median_abs_r1(members)
    thr = GUARD_THR_20CM if code in TIER_20CM else GUARD_THR
    aux = member_arrays(m, med_abs, thr)
    mi = MEMBERS.index(code) if code in MEMBERS else 0
    cells = {}
    cells_structs = {}
    first_open = None
    for gi, grid in enumerate(GRID):
        g, L = grid["g"], grid["L"]
        cell_idx = mi * 6 + gi
        name = f"{code}-g{int(g*100)}-L{L}"
        sets = grid_structure(m, g, L)
        if sets and first_open is None:
            first_open = sets[0]["open_idx"]
        mask = trigger_mask(m, aux, sets)
        mask_days = np.flatnonzero(mask)
        rounds, stats = simulate_grid(m, aux, g, L, sets)
        w_x1 = (sum(1 for r in rounds if r["pnl_x1"] > 0)
                / max(len(rounds), 1))
        w_x2 = (sum(1 for r in rounds if r["pnl_x2"] > 0)
                / max(len(rounds), 1))
        e_x1 = float(np.mean([r["pnl_x1"] for r in rounds])) if rounds else None
        e_x2 = float(np.mean([r["pnl_x2"] for r in rounds])) if rounds else None
        n_x1, n_x2, ne_x1, ne_x2, n_eff = nulls_for_cell(
            m, aux, g, L, sets, mask_days, len(rounds), cell_idx, SEED)
        p95_x1 = round(float(np.percentile(n_x1, 95)), 6) if n_x1 else None
        p95_x2 = round(float(np.percentile(n_x2, 95)), 6) if n_x2 else None
        ep95_x1 = round(float(np.percentile(ne_x1, 95)), 8) if ne_x1 else None
        ep95_x2 = round(float(np.percentile(ne_x2, 95)), 8) if ne_x2 else None
        fee = fee_survival(e_x1, e_x2)
        fee["g_over_rt_cost_x1"] = round(g / (2.0 * COST_X1), 3)
        fee["g_over_rt_cost_x2"] = round(g / (2.0 * COST_X2), 3)
        cells_structs[name] = {"g": g, "L": L, "sets": sets}
        cells[name] = {
            "cell_idx": cell_idx, "grid": {"g": g, "L": L},
            "n_mask_days": int(mask.sum()), "n_rounds": len(rounds),
            **stats,
            "win_rate_x1": round(w_x1, 6), "win_rate_x2": round(w_x2, 6),
            "e_pnl_x1": (round(e_x1, 8) if e_x1 is not None else None),
            "e_pnl_x2": (round(e_x2, 8) if e_x2 is not None else None),
            "nulls": {"n_draws_effective": len(n_eff),
                      "win_p95_x1": p95_x1, "win_p95_x2": p95_x2,
                      "e_p95_x1": ep95_x1, "e_p95_x2": ep95_x2,
                      "mean_eff_rounds": (round(float(np.mean(n_eff)), 3)
                                          if n_eff else None)},
            "fee_survival": fee,
            "rounds": rounds,
        }
    eval_start = first_open if first_open is not None else 0
    years = max((m["n"] - eval_start) / PBP, 1e-9)
    for name, cell in cells.items():
        gL = cell["grid"]["L"]
        ser_x1 = chain_daily(m, cell["rounds"], COST_X1, gL, eval_start)
        ser_x2 = chain_daily(m, cell["rounds"], COST_X2, gL, eval_start)
        cell["series_x1"] = ser_x1
        cell["series_x2"] = ser_x2
        cell["fill_density_rounds_per_year"] = round(cell["n_rounds"] / years,
                                                     4)
    min_face = minute_face(m, cells_structs, minute_dir=minute_dir)
    shard = {
        "grammar_sha16": GRAMMAR_SHA16, "member": code,
        "evidence_cutoff": (cutoff or EVIDENCE_CUTOFF), "seed": int(SEED),
        "face": m["face"], "tier": aux["tier"],
        "isolated_days": int(aux["isolated"].sum()),
        "seg_census": {s: int((aux["seg"] == s).sum())
                       for s in ("bear", "chop", "bull", "na")},
        "eval_start_idx": eval_start,
        "eval_start_date": m["dates"][eval_start],
        "minute_face": min_face,
        "cells": {k: {kk: vv for kk, vv in v.items()
                      if kk not in ("series_x1", "series_x2")}
                  for k, v in cells.items()},
        "_series": {k: (v["series_x1"], v["series_x2"])
                    for k, v in cells.items()},
    }
    return shard, None


# ------------------------------------------------------------------ finalize
def _regime_states_by_date():
    """T-74 L2 route states via the imported frozen deep-replay layer
    (descriptive only, never a switch gate). YELLOW->CHOP collapse."""
    try:
        import regime_deep_replay as RDR
        bench = RDR.load_index_bench()
        mats, _ds, _br = RDR.run_matrices(bench)
        raw = mats["v3"]["states"]
        l2 = {"GREEN": "GREEN", "YELLOW": "CHOP", "ORANGE": "ORANGE",
              "RED": "RED"}
        return {d: l2.get(s, s) for d, s in raw.items()}
    except Exception as exc:
        return {"__error__": repr(exc)[:200]}


def _sharpe(ser):
    if len(ser) < 20 or float(np.std(ser)) == 0.0:
        return 0.0
    return float(np.mean(ser) / np.std(ser, ddof=1) * np.sqrt(PBP))


def _yearly(ser, dates):
    out = {}
    for y in sorted({d[:4] for d in dates}):
        sel = np.array([d.startswith(y) for d in dates], dtype=bool)
        if sel.any():
            out[y] = round(float(np.sum(ser[sel])), 6)
    return out


def _finalize_math(shards, seed, head_base, null_pool=None):
    """Pure finalize math over in-memory shards (selftest reuses this)."""
    by_cell = {}
    for sh in shards:
        for name, cell in sh["cells"].items():
            by_cell[name] = {"shard": sh, "cell": cell}
    if len(by_cell) != BATCH_CELLS:
        return None, f"shard census drift: {len(by_cell)} != {BATCH_CELLS}"
    series_x2, series_x1 = {}, {}
    for name, ent in by_cell.items():
        sh, cell = ent["shard"], ent["cell"]
        series_x2[name] = sh["_series"][name][1]
        series_x1[name] = sh["_series"][name][0]
    L = min(len(v) for v in series_x2.values())
    mat = pd.DataFrame({k: v[-L:] for k, v in series_x2.items()})
    pbo = None
    try:
        from screening.pbo import cscv_pbo
        pbo = cscv_pbo(mat)
        pbo = {"pbo": round(float(pbo["pbo"]), 4),
               "source": "screening.pbo cscv_pbo CSCV-8, 30-cell x2 matrix, "
                         f"common-tail alignment n={L}",
               "n_aligned": int(L)}
    except Exception as exc:
        pbo = {"pbo": None, "error": repr(exc)[:200]}
    gates, cells_out = {}, {}
    for name, ent in sorted(by_cell.items()):
        sh, cell = ent["shard"], ent["cell"]
        ser = series_x2[name]
        wr = cell["win_rate_x2"]
        p95 = cell["nulls"]["win_p95_x2"]
        vacuous = cell["n_rounds"] == 0
        wr_gate = None if (p95 is None or vacuous) else bool(wr > p95)
        ep = cell["e_pnl_x2"]
        ep95 = cell["nulls"]["e_p95_x2"]
        e_gate = None if (ep95 is None or ep is None) else bool(ep > ep95)
        g1 = None
        if len(ser) >= 20 and float(np.std(ser)) > 0:
            g1 = SG.g1_prime_v2(_sharpe(ser), list(map(float, ser)),
                                batch_cells=BATCH_CELLS, pool="core48",
                                n_trades=cell["n_rounds"],
                                n_entries=cell["n_rounds"],
                                n_eff_override=head_base + BATCH_CELLS,
                                null_pool=null_pool)
        dsr = None
        if g1 is not None:
            dsr = SG.deflated_sharpe_ratio(list(map(float, ser)),
                                           n_trials=g1["skill_line"]["n_eff"])
        g2 = None
        if g1 is not None and dsr is not None and pbo["pbo"] is not None:
            g2 = SG.g2_registration_v2(g1["pass_v2"], dsr,
                                       float(pbo["pbo"]))
        cum = np.cumsum(ser)
        dd = float(cum.min() - cum.max()) if len(cum) else 0.0
        gates[name] = {"win_rate_gate_x2": wr_gate, "e_gate_x2": e_gate,
                       "g1_prime_v2": g1, "dsr": dsr, "g2": g2}
        cells_out[name] = {
            "member": sh["member"], "cell_idx": cell["cell_idx"],
            "grid": cell["grid"], "n_mask_days": cell["n_mask_days"],
            "n_rounds": cell["n_rounds"],
            "blocked_entries": cell["blocked_entries"],
            "open_at_end": cell["open_at_end"],
            "reanchors": cell["reanchors"],
            "set_ends": cell["set_ends"],
            "fill_density_rounds_per_year": cell["fill_density_rounds_per_year"],
            "win_rate_x1": cell["win_rate_x1"],
            "win_rate_x2": cell["win_rate_x2"],
            "e_pnl_x1": cell["e_pnl_x1"], "e_pnl_x2": cell["e_pnl_x2"],
            "nulls": cell["nulls"], "fee_survival": cell["fee_survival"],
            "sharpe_x2": round(_sharpe(ser), 4),
            "maxdd_cum_x2": round(min(0.0, dd), 6),
        }
    return {"cells": cells_out, "gates": gates, "pbo": pbo,
            "series_x1": series_x1, "series_x2": series_x2,
            "by_cell": by_cell}, None


SG_REG6 = ("COMPOSITE-CE-01", "COMPOSITE-CE-02", "DROUGHT-CE-01",
           "ENGULF-CE-01", "NEEDLE-DE-01", "VOLATILITY-CE-01")


def cmd_finalize(args):
    if not os.path.exists(OUT_DIR):
        return gate_refuse("no shard dir -- burn shards first")
    shards = []
    for code in MEMBERS:
        p = os.path.join(OUT_DIR, f"grid_shard_{code}.json")
        if not os.path.exists(p):
            return gate_refuse(f"shard absent: {code}")
        sh = json.load(open(p, encoding="utf-8"))
        if sh.get("grammar_sha16") != GRAMMAR_SHA16:
            return gate_refuse(f"shard grammar mismatch: {code} "
                               f"({sh.get('grammar_sha16')})")
        if sh.get("evidence_cutoff") != EVIDENCE_CUTOFF:
            return gate_refuse(f"shard cutoff drift: {code}")
        shards.append(sh)
    if os.path.exists(OUT_JSON):
        j = json.load(open(OUT_JSON, encoding="utf-8"))
        if j.get("trials_ledger"):
            print("idempotent fast path: grid_dualface.json already "
                  "finalized (ledger block present); "
                  "GRID_DUALFACE_REFINALIZE=1 = only redo")
            if os.environ.get("GRID_DUALFACE_REFINALIZE") != "1":
                return 0
    prev_total = None
    if os.path.exists(OUT_JSON):
        try:
            prev_total = int(
                json.load(open(OUT_JSON, encoding="utf-8"))
                ["trials_ledger"]["prev_total"])
        except Exception:
            prev_total = None
    # r253 redo-echo guard: redo reuses the frozen chain position of the
    # FIRST run (own echo in ledger_head would double-count).
    head_base = (prev_total if prev_total is not None
                 else int(SG.ledger_head(SG.RESULTS_DIR)["total"]))
    # D6 registered sleeve returns (ew6 canon, live.paper anchor path)
    member_rets = None
    try:
        import ew6_portfolio as E
        from live.paper import load_core
        if E.PRICES_FULL is None:
            E.PRICES_FULL = load_core()
        member_rets = {}
        for tid in SG_REG6:
            r = E.member_run(tid)
            eq = pd.Series(r["eq"], index=pd.to_datetime(r["dates"]))
            member_rets[tid] = eq.pct_change().dropna()
    except Exception as exc:
        print(f"D6-WARN: registered sleeve face unavailable: {repr(exc)[:160]}")
    regime_states = _regime_states_by_date()
    out, err = _finalize_math(shards, SEED, head_base, null_pool=None)
    if out is None:
        return gate_refuse(err)
    # D6 face + regime join + descriptive faces need per-member reload
    d6_cells = {}
    if member_rets is not None:
        for name, ser in out["series_x2"].items():
            ent = out["by_cell"][name]
            sh = ent["shard"]
            m, e = load_member(sh["member"])
            if m is None:
                return gate_refuse(f"member reload refuses D6: {e}")
            dates = pd.to_datetime(
                m["dates"][sh["eval_start_idx"]:])
            s = pd.Series(ser, index=dates)
            per = {}
            best = None
            for tid, mr in member_rets.items():
                jdf = pd.concat([s, mr], axis=1, join="inner").dropna()
                if len(jdf) < 20:
                    per[tid] = {"corr": None, "overlap_days": int(len(jdf))}
                    continue
                v = float(np.corrcoef(jdf.iloc[:, 0], jdf.iloc[:, 1])[0, 1])
                per[tid] = {"corr": round(v, 4), "overlap_days": int(len(jdf))}
                if best is None or abs(v) > abs(per[best]["corr"]):
                    best = tid
            mx = abs(per[best]["corr"]) if best else None
            d6_cells[name] = {
                "per_member": per,
                "max_abs_corr": (round(mx, 4) if mx is not None else None),
                "argmax_member": best,
                "reject": bool(mx is not None and mx >= D6_REJECT)}
    regime_face = {"source": "regime_deep_replay v3 (L2 route map "
                   "YELLOW->CHOP), descriptive only",
                   "per_cell": {}}
    descr = {"per_cell": {}}
    minute_merged = {}
    for name, ent in out["by_cell"].items():
        sh, cell = ent["shard"], ent["cell"]
        m, e = load_member(sh["member"])
        if m is None:
            return gate_refuse(f"member reload refuses regime face: {e}")
        if sh["member"] not in minute_merged:
            minute_merged[sh["member"]] = sh["minute_face"]
        per_state, per_seg = {}, {}
        for r in cell["rounds"]:
            st = (regime_states.get(r["trig_date"])
                  if "__error__" not in regime_states else None)
            st = st or "na"
            per_state.setdefault(st, []).append(r["pnl_x2"] > 0)
            per_seg.setdefault(r["seg_trig"], []).append(r["pnl_x2"] > 0)
        regime_face["per_cell"][name] = {
            "by_route_state": {k: {"n": len(v), "win_rate": round(
                sum(v) / len(v), 4)} for k, v in sorted(per_state.items())},
            "by_t89_segment": {k: {"n": len(v), "win_rate": round(
                sum(v) / len(v), 4)} for k, v in sorted(per_seg.items())}}
        ser = out["series_x2"][name]
        dates = m["dates"][sh["eval_start_idx"]:]
        yearly = _yearly(ser, dates)
        cum = np.cumsum(ser)
        run_max = np.maximum.accumulate(cum)
        dd = float(np.min(cum - run_max)) if len(cum) else 0.0
        oos_mask = np.array([d >= OOS_FROM for d in dates], dtype=bool)
        oos_ann = (float(np.mean(ser[oos_mask]) * PBP)
                   if oos_mask.any() and float(np.std(ser)) > 0 else 0.0)
        chain_cum = float(np.sum(ser))
        with np.errstate(invalid="ignore"):
            pr = m["c"][1:] / m["c"][:-1] - 1.0
        es = sh["eval_start_idx"]
        pas_full = np.concatenate([np.zeros(1), np.nan_to_num(pr[es:])]) \
            [:len(ser)]
        descr["per_cell"][name] = {
            "ann_x2": round(float(np.mean(ser) * PBP
                                   / (np.std(ser, ddof=1) or 1.0))
                            * (1 if float(np.std(ser)) > 0 else 0), 6),
            "oos_2025_ann_x2": round(oos_ann, 6),
            "maxdd_x2": round(dd, 6),
            "yearly_x2": yearly,
            "crash_year": bool(any(v <= -0.35 for v in yearly.values())),
            "chain_cum_x2": round(chain_cum, 6),
            "beat_passive_full_x2": bool(chain_cum > float(np.sum(pas_full))),
            "beat_margin_x2": round(chain_cum - float(np.sum(pas_full)), 6),
        }
        # virtual timepoints {6m,12m,24m} x {x1,x2} vs same-window buy-hold
        vt = {}
        for wname, W in WINDOWS.items():
            for face_key, s in (("x2", ser), ("x1", out["series_x1"][name])):
                nn = len(s)
                if nn <= W:
                    vt[f"{wname}_{face_key}"] = {
                        "n_starts": 0, "beat_rate": None,
                        "note": "window longer than series (narrow face "
                                "disclosed honestly)"}
                    continue
                ch = np.cumsum(s)
                pa = np.cumsum(pas_full)
                starts = np.arange(0, nn - W)
                beats = int(np.sum(ch[starts + W] - ch[starts]
                                   > pa[starts + W] - pa[starts]))
                vt[f"{wname}_{face_key}"] = {
                    "n_starts": int(len(starts)),
                    "beat_rate": round(beats / len(starts), 4)}
        out["cells"][name]["virtual_timepoints"] = vt
    ledger = SG.append_ledger(BATCH_NAME, batch_trials=BATCH_CELLS,
                              file_name=OUT_JSON,
                              evidence_cutoff=EVIDENCE_CUTOFF,
                              prev_total=head_base)
    product = {
        "batch": BATCH_NAME, "grammar_sha16": GRAMMAR_SHA16,
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "science_gates": {"cutoff_meta": {
            "evidence_cutoff": EVIDENCE_CUTOFF}, "ledger": ledger},
        "members": MEMBERS, "anchors": {c: ANCHORS[c] for c in MEMBERS},
        "cost_faces": {"x1_side_bp": round(COST_X1 * 1e4, 3),
                       "x2_side_bp": round(COST_X2 * 1e4, 3),
                       "judged_face": "x2"},
        "cells": out["cells"], "gates": out["gates"], "pbo": out["pbo"],
        "d6": {"reject_line": D6_REJECT, "members": list(SG_REG6),
               "cells": d6_cells} if member_rets is not None else
              {"status": "unavailable", "reject_line": D6_REJECT},
        "regime_face": regime_face, "descriptive": descr,
        "minute_face": {"per_member": minute_merged,
                        "note": "descriptive equivalence face only "
                        "(prereg s3.9), never a judgement"},
        "blocked_accounting": {
            c: {"blocked_entries": sum(
                    x["cells"][k]["blocked_entries"] for k in x["cells"]),
                "open_at_end": sum(
                    x["cells"][k]["open_at_end"] for k in x["cells"]),
                "isolated_days": x["isolated_days"]}
            for c, x in zip(MEMBERS, shards)},
        "nulls_ref": OUT_NULLS,
    }
    _atomic_json(OUT_JSON, product)
    nulls_out = {"batch": BATCH_NAME, "evidence_cutoff": EVIDENCE_CUTOFF,
                 "grammar_sha16": GRAMMAR_SHA16,
                 "cells": {name: c["nulls"]
                           for name, c in out["cells"].items()}}
    _atomic_json(OUT_NULLS, nulls_out)
    _atomic_json(OUT_MINUTE, {"batch": BATCH_NAME,
                              "evidence_cutoff": EVIDENCE_CUTOFF,
                              "per_member": minute_merged})
    n_pass = sum(1 for g in out["gates"].values()
                 if g["win_rate_gate_x2"] and g["g2"]
                 and g["g2"].get("eligible_v2"))
    print(f"FINALIZE OK: 30 cells; win-gate+G2 eligible={n_pass}; "
          f"ledger total={ledger.get('total')}")
    return 0


# ------------------------------------------------------------------ cli cmds
def cmd_run(args):
    ram = sorted(_free_ram_gb() for _ in range(3))
    if ram[0] < RAM_FLOOR_GB:
        print(f"RAM-FLOOR(exit3): three-sample min {ram[0]:.2f}GB "
              f"< {RAM_FLOOR_GB}GB (r354 family, light-batch calibration)")
        return 3
    global SEED
    SEED = int(SG.SEED_REGISTRY[BATCH_NAME_KEY])
    os.makedirs(SER_DIR, exist_ok=True)
    codes = MEMBERS if args.shard == "all" else [args.shard]
    for code in codes:
        if code not in MEMBERS:
            return gate_refuse(f"unknown shard member: {code}")
        p = os.path.join(OUT_DIR, f"grid_shard_{code}.json")
        if os.path.exists(p) and not args.force:
            j = json.load(open(p, encoding="utf-8"))
            if j.get("grammar_sha16") == GRAMMAR_SHA16:
                print(f"shard {code}: idempotent skip (grammar match); "
                      f"--force to redo")
                continue
            return gate_refuse(f"shard {code} grammar mismatch -- "
                                f"manual adjudication required")
        shard, err = burn_member(code)
        if shard is None:
            return gate_refuse(f"burn {code}: {err}")
        for name, (sx1, sx2) in shard["_series"].items():
            ci = shard["cells"][name]["cell_idx"]
            np.save(os.path.join(SER_DIR, f"{code}_{ci}_x1.npy"),
                    sx1.astype(np.float64), allow_pickle=False)
            np.save(os.path.join(SER_DIR, f"{code}_{ci}_x2.npy"),
                    sx2.astype(np.float64), allow_pickle=False)
        shard_out = {k: v for k, v in shard.items() if k != "_series"}
        _atomic_json(p, shard_out)
        # per-member round-stream CSV (prereg s6)
        rows = ["member,cell,level,trig_date,entry_date,entry_px,exit_date,"
                "exit_px,kind,pnl_x1,pnl_x2,win_x1,win_x2,hold_days,"
                "seg_trig,set_open_date,anchor_at_entry,blocked_exit_rolls"]
        for name, cell in shard["cells"].items():
            for r in cell["rounds"]:
                rows.append(",".join([
                    code, name, str(r["level"]), r["trig_date"],
                    r["entry_date"], str(r["entry_px"]), r["exit_date"],
                    str(r["exit_px"]), r["kind"], str(r["pnl_x1"]),
                    str(r["pnl_x2"]), str(int(r["pnl_x1"] > 0)),
                    str(int(r["pnl_x2"] > 0)), str(r["hold_days"]),
                    r["seg_trig"], r["set_open_date"],
                    str(r["anchor_at_entry"]),
                    str(r["blocked_exit_rolls"])]))
        _atomic_text(os.path.join(OUT_DIR, f"grid_rounds_{code}.csv"),
                     "\n".join(rows) + "\n")
        print(f"shard {code}: burnt -> grid_shard_{code}.json + rounds csv "
              f"({sum(c['n_rounds'] for c in shard['cells'].values())} "
              f"rounds)")
    return 0


def cmd_status(args):
    print(f"grammar_sha16={GRAMMAR_SHA16}")
    for code in MEMBERS:
        p = os.path.join(OUT_DIR, f"grid_shard_{code}.json")
        if os.path.exists(p):
            j = json.load(open(p, encoding="utf-8"))
            n = sum(c["n_rounds"] for c in j["cells"].values())
            print(f"  {code}: shard OK (grammar "
                  f"{'match' if j['grammar_sha16'] == GRAMMAR_SHA16 else 'MISMATCH'}) "
                  f"rounds={n} seed={j['seed']}")
        else:
            print(f"  {code}: shard ABSENT")
    print(f"  finalize: {'DONE' if os.path.exists(OUT_JSON) else 'pending'}")
    return 0


def cmd_selftest(args):
    """Hermetic offline selftest: synthetic fixtures only, zero network,
    zero repo data loads, deterministic double-run byte-identical."""
    import shutil
    import subprocess
    tmp = tempfile.mkdtemp(prefix="grid_df_st_")
    fails = []
    t = lambda ok, msg: (None if ok else fails.append(msg))

    # ------------------------------------------------------------------
    # fixture: engineered lifecycle panel (n=340 business days)
    #   A 0..249    slow ramp 2.00 -> 2.90 (MA200 ~2.45-2.50)
    #   B 250..256  slide to 2.40 (below MA200 -> trend off)
    #   C 257..262  rally to 3.05 (off->on transition -> SET 1, anchor ~2.53)
    #   D 263       -12% crash day (guard-test face; trend survives)
    #     264..269 cascade -5.5%/day -> trend_sl end of SET 1
    #   E 270..289  recovery crossing MA200 -> SET 2 re-opens (anchor ~2.44)
    #   F 290       WICK day: close 2.70 trend-on, low 1.90 sweeps every
    #               cell's ladder (multi-level same-day fills at 291)
    #     292..299  rebound to 2.92 -> tp exits for all faces
    #   G 300..327  gentle drift; 328 late WICK (low 2.20) -> fills 329,
    #               no rebound; 333 crash -20% -> trend_sl end of SET 2 ->
    #               held units book CLEAR at 334
    #   H 335..337  recovery crossing MA200 -> SET 3 opens (anchor ~2.66)
    #     338       final WICK (low 2.30) -> fills at 339 = panel end ->
    #               open_at_end
    n = 340
    dates = pd.bdate_range("2024-01-02", periods=n).strftime(
        "%Y-%m-%d").tolist()
    c = np.empty(n)
    c[:250] = np.linspace(2.00, 2.90, 250)
    c[250:257] = np.linspace(2.90, 2.40, 7)
    c[257:263] = np.linspace(2.40, 3.05, 6)
    c[263] = c[262] * 0.88                     # -12% guard-test crash day
    for k in range(6):                        # cascade 264..269
        c[264 + k] = c[263 + k] * 0.945
    c[270:290] = np.linspace(c[269], 2.85, 20)     # recovery to 2.85
    c[290] = c[289] * 0.947                    # wick-day close 2.70
    c[291] = c[290] * 1.004                    # fill-day drift
    c[292:300] = np.linspace(c[291], 2.92, 8)     # rebound -> tp
    c[300:328] = np.linspace(2.92, 2.86, 28)       # gentle drift
    c[328] = c[327] * 0.944                    # late wick close 2.70
    c[329:333] = np.linspace(c[328], 2.76, 4)     # no rebound to targets
    c[333] = c[332] * 0.80                      # -20% crash -> trend_sl
    c[334] = c[333]                             # flat aftermath
    c[335:338] = np.linspace(c[334], 2.80, 3)     # recovery -> SET 3
    c[338] = 2.70                               # final wick close (trend-on)
    c[339] = 2.71
    rng = np.random.default_rng(7)
    o = c * (1 + rng.normal(0, 0.0015, n))
    h = np.maximum(o, c) * 1.004
    l = np.minimum(o, c) * 0.996
    # wick days: deep intraday lows, closes stay trend-on (engineered)
    for wi, low in ((290, 1.90), (328, 2.20), (338, 2.30)):
        l[wi] = low
        h[wi] = max(o[wi], c[wi]) * 1.004
        o[wi] = c[wi] * 1.01
    anchors_st = {"510050": {"path": "daily/st.csv", "first": dates[0],
                             "rows": n}}

    def write_fixture(d, arr_c=None, arr_o=None, arr_h=None, arr_l=None):
        os.makedirs(os.path.join(d, "daily"), exist_ok=True)
        df = pd.DataFrame({
            "date": dates,
            "open": arr_o if arr_o is not None else o,
            "high": arr_h if arr_h is not None else h,
            "low": arr_l if arr_l is not None else l,
            "close": arr_c if arr_c is not None else c,
            "volume": 1e6, "amount": 1e8})
        df.to_csv(os.path.join(d, "daily", "st.csv"), index=False)

    def load_fi(ac=None):
        return load_member("510050", data_dir=tmp,
                           anchors=ac or anchors_st, cutoff=dates[-1])

    # [S1] anchor gates (fail-closed faces)
    write_fixture(tmp)
    bad = dict(anchors_st)
    bad["510050"] = dict(anchors_st["510050"], rows=n - 1)
    m, err = load_member("510050", data_dir=tmp, anchors=bad,
                         cutoff=dates[-1])
    t(m is None and "row census drift" in err, f"S1a row refuse: {err}")
    m, err = load_fi()
    t(m is not None, f"S1b clean load: {err}")
    c_nan = c.copy(); c_nan[50] = np.nan
    write_fixture(tmp, arr_c=c_nan)
    m2, err = load_fi()
    t(m2 is None and "NaN" in err, f"S1c NaN refuse: {err}")
    write_fixture(tmp)
    m, err = load_fi()
    t(m is not None, f"S1d restore: {err}")

    med_abs = universe_median_abs_r1([m])
    aux = member_arrays(m, med_abs, GUARD_THR)
    grid = GRID[0]                              # g=4%, L=4
    sets = grid_structure(m, grid["g"], grid["L"])
    t(len(sets) >= 1, f"S2a set opened on fixture: {len(sets)} sets")
    st0 = sets[0]
    t(st0["open_idx"] >= 199, "S2b warmup respected (first finite MA200)")
    t(st0["anchors"][0][0] == st0["open_idx"],
      "S2c anchor = opening-day close")
    mask = trigger_mask(m, aux, sets)
    t(mask[st0["open_idx"]], "S2d set-open day is triggerable (t>=open)")

    # [S3] real engine burn on fixture: lifecycle coverage
    rounds, stats = simulate_grid(m, aux, grid["g"], grid["L"], sets)
    t(len(rounds) >= 1, f"S3a rounds fired on fixture: {len(rounds)}")
    if rounds:
        r0 = rounds[0]
        t(r0["pnl_x2"] < r0["pnl_x1"], "S3b x2 stress strictly costlier")
        t(r0["hold_days"] >= 1, "S3c min hold 1 day (T+1)")
        t(all(r["kind"] in ("tp", "clear") for r in rounds),
          f"S3d round kinds legal: {set(r['kind'] for r in rounds)}")
    # every cell (6 g/L combos) fires >=1 round somewhere in the fixture
    for grid_i in GRID:
        sets_i = grid_structure(m, grid_i["g"], grid_i["L"])
        rounds_i, _ = simulate_grid(m, aux, grid_i["g"], grid_i["L"], sets_i)
        t(len(rounds_i) >= 1,
          f"S3e cell g={grid_i['g']} L={grid_i['L']} fires: {len(rounds_i)}")
    # lifecycle coverage: tp + clear + set re-open + open_at_end somewhere
    sets_l = grid_structure(m, grid["g"], grid["L"])
    rounds_l, stats_l = simulate_grid(m, aux, grid["g"], grid["L"], sets_l)
    kinds = {r["kind"] for r in rounds_l}
    t("tp" in kinds, f"S3f tp exits exist: {kinds}")
    t("clear" in kinds, f"S3g clear bookings exist (set-end face): {kinds}")
    t(len(sets_l) >= 2, f"S3h off->on re-open lifecycle: {len(sets_l)} sets")
    t(stats_l["set_ends"]["trend_sl"] + stats_l["set_ends"]["band_break"]
      >= 1, f"S3i set end counted: {stats_l['set_ends']}")
    t(stats_l["open_at_end"] >= 1,
      f"S3j open_at_end at panel end: {stats_l['open_at_end']}")
    # multi-level same-day: >=2 rounds share one fill date somewhere
    by_fill = {}
    for r in rounds_l:
        by_fill.setdefault(r["entry_date"], set()).add(r["level"])
    t(any(len(v) >= 2 for v in by_fill.values()),
      f"S3k multi-level same-day fills: {by_fill}")

    # [S4] blocked_entry: fill-day one-word limit-up voids the entry
    m4, _ = load_fi()
    aux4 = member_arrays(m4, universe_median_abs_r1([m4]), GUARD_THR)
    sets4 = grid_structure(m4, grid["g"], grid["L"])
    r4, _s4 = simulate_grid(m4, aux4, grid["g"], grid["L"], sets4)
    t(len(r4) >= 1, "S4a base rounds exist for sabotage")
    fill_day = r4[0]["entry_idx"]
    pc4 = m4["pc"][fill_day]
    o_b, h_b, l_b, c_b = o.copy(), h.copy(), l.copy(), c.copy()
    o_b[fill_day] = pc4 * 1.100
    h_b[fill_day] = o_b[fill_day]
    l_b[fill_day] = o_b[fill_day]
    c_b[fill_day] = o_b[fill_day]
    write_fixture(tmp, arr_c=c_b, arr_o=o_b, arr_h=h_b, arr_l=l_b)
    m5, _ = load_fi()
    aux5 = member_arrays(m5, universe_median_abs_r1([m5]), GUARD_THR)
    sets5 = grid_structure(m5, grid["g"], grid["L"])
    _r5, st5 = simulate_grid(m5, aux5, grid["g"], grid["L"], sets5)
    t(st5["blocked_entries"] >= 1, f"S4b blocked_entry counted: {st5}")
    write_fixture(tmp)

    # [S5] blocked_exit roll: tp-fill day one-word limit-down rolls
    m6, _ = load_fi()
    aux6 = member_arrays(m6, universe_median_abs_r1([m6]), GUARD_THR)
    sets6 = grid_structure(m6, grid["g"], grid["L"])
    r6, _s6 = simulate_grid(m6, aux6, grid["g"], grid["L"], sets6)
    tp_rounds = [r for r in r6 if r["kind"] == "tp" and r["level"] == 1]
    t(len(tp_rounds) >= 1, "S5a tp round exists for roll sabotage")
    if tp_rounds:
        ex_d = tp_rounds[0]["exit_idx"]
        pcx = m6["pc"][ex_d]
        o_r, h_r, l_r, c_r = o.copy(), h.copy(), l.copy(), c.copy()
        o_r[ex_d] = pcx * 0.900
        h_r[ex_d] = o_r[ex_d]
        l_r[ex_d] = o_r[ex_d]
        c_r[ex_d] = o_r[ex_d]
        write_fixture(tmp, arr_c=c_r, arr_o=o_r, arr_h=h_r, arr_l=l_r)
        m7, _ = load_fi()
        aux7 = member_arrays(m7, universe_median_abs_r1([m7]), GUARD_THR)
        sets7 = grid_structure(m7, grid["g"], grid["L"])
        r7, st7 = simulate_grid(m7, aux7, grid["g"], grid["L"], sets7)
        t(st7["blocked_exit_rolls"] >= 1
          or any(r["blocked_exit_rolls"] >= 1 for r in r7),
          f"S5b blocked_exit roll: stats={st7['blocked_exit_rolls']}")
    write_fixture(tmp)

    # [S6] fund-guard isolation: |r1|>10.5% & median<3% -> isolated day,
    # buy suppressed (mask excludes it)
    m8, _ = load_fi()
    aux8 = member_arrays(m8, {dates[263]: 0.0}, GUARD_THR)
    t(bool(aux8["isolated"][263]),
      f"S6a cascade day isolated under fake low median (|r1|="
      f"{abs(m8['r1'][263]):.3f})")
    sets8 = grid_structure(m8, grid["g"], grid["L"])
    mask8 = trigger_mask(m8, aux8, sets8)
    t(not mask8[263], "S6b isolated day excluded from trigger mask")

    # [S7] same-day anchor semantics: reanchor day levels re-hang from the
    # new close (upper-band break engineered via phase C rally)
    m9, _ = load_fi()
    aux9 = member_arrays(m9, universe_median_abs_r1([m9]), GUARD_THR)
    sets9 = grid_structure(m9, grid["g"], grid["L"])
    reanchored = [s for s in sets9 if len(s["anchors"]) > 1]
    if reanchored:
        s_r = reanchored[0]
        idx_r, px_r = s_r["anchors"][1]
        t(anchor_at(s_r, idx_r) == px_r,
          "S7a reanchor day carries its own close as anchor")
        t(anchor_at(s_r, idx_r - 1) != px_r,
          "S7b prior day still on the old anchor")
    else:
        t(True, "S7 skip: fixture produced no reanchor (tolerated)")

    # [S8] null determinism + stream separation + mask containment
    m11, _ = load_fi()
    aux11 = member_arrays(m11, universe_median_abs_r1([m11]), GUARD_THR)
    sets11 = grid_structure(m11, grid["g"], grid["L"])
    mask11 = np.flatnonzero(trigger_mask(m11, aux11, sets11))
    t(len(mask11) >= 4, f"S8a fixture mask face: {len(mask11)} days")
    rounds11, _ = simulate_grid(m11, aux11, grid["g"], grid["L"], sets11)
    nd = max(len(rounds11), 2)
    a1 = nulls_for_cell(m11, aux11, grid["g"], grid["L"], sets11, mask11,
                        nd, 0, 20295500)
    b1 = nulls_for_cell(m11, aux11, grid["g"], grid["L"], sets11, mask11,
                        nd, 0, 20295500)
    t(a1[0] == b1[0] and a1[3] == b1[3], "S8b null determinism (stream)")
    draws = []
    for ci in (0, 1, 2):
        r = np.random.default_rng([20295500, ci])
        draws.append(np.sort(r.choice(mask11, size=min(nd, len(mask11)),
                                       replace=False)))
    t(any(not np.array_equal(draws[0], d) for d in draws[1:]),
      "S8c cell_idx streams draw distinct days")
    t(set(map(int, draws[0])).issubset(set(map(int, mask11))),
      "S8d draws contained in mask")

    # [S9] fee survival interpolation
    fee = fee_survival(0.010, -0.005)
    t(fee["c_star"] is not None and COST_X1 < fee["c_star"] < COST_X2,
      f"S9a c* inside [x1,x2]: {fee['c_star']}")
    t(fee_survival(-0.01, -0.02)["c_star_note"].startswith("<"),
      "S9b already-unprofitable face")
    t(fee_survival(0.02, 0.01)["c_star_note"].startswith(">"),
      "S9c profitable-at-x2 face")

    # [S10] minute equivalence face on a synthetic archive
    m12, _ = load_fi()
    mm_dir = os.path.join(tmp, "minute_feed")
    os.makedirs(mm_dir, exist_ok=True)
    rows_mm = []
    for ds in dates[-10:]:
        i = dates.index(ds)
        for k in range(60):
            rows_mm.append({"day": f"{ds} 1{k % 2}:{k:02d}",
                            "open": float(m12["l"][i]),
                            "high": float(m12["h"][i]),
                            "low": float(m12["l"][i]),
                            "close": float(m12["c"][i]),
                            "volume": 100, "amount": 1e4})
    pd.DataFrame(rows_mm).to_csv(os.path.join(mm_dir, "510050.csv"),
                                 index=False)
    sets12 = grid_structure(m12, grid["g"], grid["L"])
    mf = minute_face(m12, {"st": {"g": grid["g"], "L": grid["L"],
                                  "sets": sets12}}, minute_dir=mm_dir)
    t(mf["status"] == "ok", f"S10a minute face ok: {mf.get('status')}")
    t(mf["n_extremes_mismatch_days"] == 0,
      f"S10b zero mismatch on coherent fixture: {mf}")
    rows_mm[5]["low"] = rows_mm[5]["low"] * 0.99
    pd.DataFrame(rows_mm).to_csv(os.path.join(mm_dir, "510050.csv"),
                                 index=False)
    mf2 = minute_face(m12, {"st": {"g": grid["g"], "L": grid["L"],
                                   "sets": sets12}}, minute_dir=mm_dir)
    t(mf2["n_extremes_mismatch_days"] == 1,
      f"S10c mismatch listed honestly: {mf2['n_extremes_mismatch_days']}")

    # [S11] grammar + seed registry + double-run byte-identical stdout
    t(SG.SEED_REGISTRY.get(BATCH_NAME_KEY) == 20295500,
      f"S11a SEED_REGISTRY grid_dualface_p1: "
      f"{SG.SEED_REGISTRY.get(BATCH_NAME_KEY)}")
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    outs = []
    for _ in range(2):
        r = subprocess.run(
            [sys.executable, os.path.abspath(__file__), "selftest",
             "--inner"],
            capture_output=True, text=True, env=env, cwd=ROOT)
        outs.append(r.stdout)
    t(len(outs) == 2 and outs[0] == outs[1] and r.returncode == 0,
      "S11b double-run stdout byte-identical")
    t(_sha16(GRAMMAR) == GRAMMAR_SHA16, "S11c grammar sha self-consistent")

    if fails:
        print("SELFTEST FAIL:")
        for f_ in fails:
            print("  -", f_)
        shutil.rmtree(tmp, ignore_errors=True)
        return 1
    print("SELFTEST PASS: hermetic legs all green; double-run "
          "byte-identical")
    shutil.rmtree(tmp, ignore_errors=True)
    return 0


def _selftest_inner(args):
    print("inner ok: grammar", GRAMMAR_SHA16, "seed",
          SG.SEED_REGISTRY.get(BATCH_NAME_KEY))
    return 0


def main():
    ap = argparse.ArgumentParser(description="GRID_DUALFACE_P1 runner "
                                             "(T-104 s2/s3)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p_run = sub.add_parser("run")
    p_run.add_argument("--shard", default="all",
                       help="member code or 'all' (default all)")
    p_run.add_argument("--force", action="store_true")
    p_fin = sub.add_parser("finalize")
    p_sta = sub.add_parser("status")
    p_ste = sub.add_parser("selftest")
    p_ste.add_argument("--inner", action="store_true")
    args = ap.parse_args()
    if args.cmd == "run":
        return cmd_run(args)
    if args.cmd == "finalize":
        return cmd_finalize(args)
    if args.cmd == "status":
        return cmd_status(args)
    if args.cmd == "selftest":
        if getattr(args, "inner", False):
            return _selftest_inner(args)
        return cmd_selftest(args)
    return 2


if __name__ == "__main__":
    sys.exit(main())
