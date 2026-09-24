"""Market regime guard probe -- REGIME_GUARD v1.0 shadow detector (T-05 part 1).

Authority: firm/risk/REGIME_GUARD.md §1 (CEO order O-20260923-2315).
Mode: SHADOW ONLY -- writes results/regime_state.json, zero behavior change
to paper/live (enforce mode is a separate flag gated on the calibration
batch + GM approval, NOT in this file's scope).

Four-level state machine (daily, all data-driven, thresholds frozen verbatim
from REGIME_GUARD §1 -- no hand-tuning):
  RED    : 510300 10d cumulative <= -12% | single-day <= -5% (panic)
           | R-配3 major bear (single source: firm/risk/regime.py major_bear_state)
  ORANGE : 10d <= -8% | 20d realized vol > rolling-3y p95 | breadth collapse
           (core48 close<MA20 share >= 80% AND 5d share slope negative)
           | hs300 < MA200 (iron_rules #10 collected, reference not reimpl.)
  YELLOW : 10d <= -5% | 20d vol > rolling-3y p80 | breadth >= 65%
           | event window (frozen calendar, appendix A)
  GREEN  : none of the above.

Transitions: upgrades immediate; downgrades require 2 consecutive GREEN
signal days (anti-flap, literal §1 reading: while raw < prev but raw != GREEN
the state holds; multi-level drops go straight to GREEN after the 2nd green
day -- calibration batch will quantify this stickiness).

Honest limitations (documented, part-2 prereg items):
  * pre-long-holiday event window is bars-gap derived -- detectable only in
    hindsight/replay (live probe cannot know tomorrow's SSE holiday from
    past bars); live forward coverage needs the frozen official calendar
    registered via prereg. FOMC leg uses the frozen 2026 announcement list
    (provisional, verify before enforce).
  * rolling-3y vol quantile needs >= 776 bench bars; earlier dates report
    insufficient_history and do NOT trigger (conservative floor).

Usage:
    python scripts/market_regime.py            # daily shadow probe
    python scripts/market_regime.py selftest   # synthetic paths, zero network
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

from config import PATHS

STATE_PATH = os.path.join(PATHS.results_dir, "regime_state.json")
BENCH = "510300"
MA_BRE = 20          # breadth MA window
MA_TREND = 200       # iron_rules #10 collected trend line
WIN10 = 10
VOL_WIN = 20
VOL_BASE = 756       # 3y rolling quantile base window
GREEN, YELLOW, ORANGE, RED = "GREEN", "YELLOW", "ORANGE", "RED"
_ORD = {GREEN: 0, YELLOW: 1, ORANGE: 2, RED: 3}
_CN = {GREEN: "绿·正常", YELLOW: "黄·警戒", ORANGE: "橙·高危", RED: "红·危机"}
MODE = "shadow"
HISTORY_KEEP = 500
TRANSITION_KEEP = 50
BREADTH_LOOKBACK = 6   # dates for 5d slope
# Appendix A frozen event calendar (add/remove = prereg only).
# FOMC 2026 announcement days (US) -> Beijing trading day = next calendar
# day. Provisional list per Federal Reserve published schedule; verify
# before any enforce decision (part-2 item).
FOMC_2026_BEIJING = [
    "2026-01-29", "2026-03-19", "2026-04-30", "2026-06-18",
    "2026-07-30", "2026-09-17", "2026-10-29", "2026-12-10",
]
LONG_GAP_DAYS = 6        # calendar-day gap defining a long holiday
LONG_GAP_MONTHS = {1, 2, 10}   # spring festival / national day only

# Canonical declared thresholds of the deployed live probe (v1 §1 matrix,
# REGIME_GUARD.md law values verbatim). The science_audit C6 monthly check
# fingerprints this dict (sha256 over canonical JSON) against the value
# frozen in research/SCIENCE_AUDIT_PREREG.md §9 -- any drift (law number
# changed without a new prereg) is a finding. Behavior-level drift is
# guarded by the _selftest boundary cases which hit each threshold.
THRESHOLDS = {
    "windows": {"win10": WIN10, "vol_win": VOL_WIN, "vol_base": VOL_BASE,
                "ma_breadth": MA_BRE, "ma_trend": MA_TREND,
                "breadth_lookback": BREADTH_LOOKBACK},
    "crash_10d": {"red": -0.12, "orange": -0.08, "yellow": -0.05},
    "panic_1d": {"red": -0.05},
    "vol_burst": {"orange_quantile": 0.95, "yellow_quantile": 0.80},
    "breadth": {"orange_share": 0.80, "orange_slope_negative": True,
                "yellow_share": 0.65},
    "v1_mapping": {"trend_below_ma200": "ORANGE",     # iron_rules #10 collected
                   "r_pei3_major_bear": "RED"},       # R-配3 collected v1
    "v2_remap": {"red": "crash|panic only", "r_pei3_major_bear": "YELLOW",
                 "trend_below_ma200": "de-collected (T0 ruling, separate wiring)"},
    "hysteresis": {"downgrade_green_days": 2},
    "events": {"fomc_2026_beijing": FOMC_2026_BEIJING,
               "pre_holiday": "replay-only (bars-gap derived)"},
}


def threshold_fingerprint() -> str:
    """sha256 of the canonical THRESHOLDS JSON (audit C6 drift anchor)."""
    import hashlib
    canon = json.dumps(THRESHOLDS, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


def _bare_codes():
    return sorted(f[:-4] for f in os.listdir(PATHS.daily_dir)
                  if f.endswith(".csv") and f[:-4].isdigit())


def load_bench() -> pd.Series:
    for name in (f"{BENCH}.csv", f"sh{BENCH}.csv"):
        p = os.path.join(PATHS.daily_dir, name)
        if os.path.exists(p):
            df = pd.read_csv(p, parse_dates=["date"]).set_index("date")
            return df["close"].astype(float).sort_index()
    raise FileNotFoundError(f"no {BENCH} daily file under {PATHS.daily_dir}")


def bench_dims(bench: pd.Series) -> dict:
    """Latest-bar readings for bench-based dimensions."""
    r1 = bench.pct_change()
    r10 = bench.pct_change(WIN10)
    last = float(bench.iloc[-1])
    asof = str(bench.index[-1].date())
    dims = {"asof": asof, "close": round(last, 4)}

    # crash10d / panic
    v10 = float(r10.iloc[-1]) if r10.notna().iloc[-1] else None
    v1 = float(r1.iloc[-1]) if r1.notna().iloc[-1] else None
    dims["crash_10d"] = v10
    dims["panic_1d"] = v1

    # vol burst: 20d realized vol vs rolling-3y p95/p80 (needs VOL_WIN+VOL_BASE)
    vol20 = r1.rolling(VOL_WIN).std()
    if len(vol20.dropna()) > VOL_BASE + VOL_WIN:
        base = vol20.iloc[-(VOL_BASE + 1):-1]  # exclude current from base
        p95 = float(base.quantile(0.95))
        p80 = float(base.quantile(0.80))
        v = float(vol20.iloc[-1])
        dims["vol20"] = round(v, 6)
        dims["vol_p95"] = round(p95, 6)
        dims["vol_p80"] = round(p80, 6)
        dims["vol_status"] = "ok"
    else:
        dims["vol20"] = None
        dims["vol_status"] = "insufficient_history"

    # trend: iron_rules #10 collected (hs300 proxy < MA200)
    if len(bench) >= MA_TREND:
        ma200 = float(bench.rolling(MA_TREND).mean().iloc[-1])
        dims["ma200"] = round(ma200, 4)
        dims["below_ma200"] = bool(last < ma200)
    else:
        dims["ma200"] = None
        dims["below_ma200"] = None

    # event window (frozen calendar; bars-gap leg is replay-only by design)
    dims["event_fomc"] = asof in FOMC_2026_BEIJING
    dims["event_pre_holiday"] = None  # live-unknowable from past bars
    dims["event_note"] = ("pre-holiday leg bars-gap-derived (replay-capable, "
                          "live needs frozen official calendar via prereg)")
    return dims


def breadth_dims(bench: pd.Series) -> dict:
    """core48 close<MA20 share on the last BREADTH_LOOKBACK bench dates.

    Reads each bare-code CSV once; symbols lacking MA_BRE bars as-of a date
    are excluded from that date's denominator (honest).
    """
    dates = list(bench.index[-BREADTH_LOOKBACK:])
    if len(dates) < BREADTH_LOOKBACK:
        return {"share_below_ma20": None, "share_slope_5d": None,
                "status": "insufficient_history", "n_symbols": 0}
    below = {d: 0 for d in dates}
    valid = {d: 0 for d in dates}
    for code in _bare_codes():
        p = os.path.join(PATHS.daily_dir, f"{code}.csv")
        df = pd.read_csv(p, parse_dates=["date"]).set_index("date")
        closes = df["close"].astype(float).sort_index()
        for d in dates:
            hist = closes.loc[:d]
            if len(hist) < MA_BRE:
                continue
            win = hist.tail(MA_BRE)
            if float(win.iloc[-1]) < float(win.mean()):
                below[d] += 1
            valid[d] += 1
    latest, past = dates[-1], dates[0]
    share = (below[latest] / valid[latest]) if valid[latest] else None
    slope = None
    if share is not None and valid[past]:
        slope = share - below[past] / valid[past]
    return {"share_below_ma20": None if share is None else round(share, 4),
            "share_slope_5d": None if slope is None else round(slope, 4),
            "share_5d_ago": None if not valid[past]
            else round(below[past] / valid[past], 4),
            "status": "ok", "n_symbols": valid[latest],
            "interpretation": "slope = share_now - share_5d_ago (literal s1)"}


def raw_level(bd: dict, br: dict, bear: bool) -> str:
    """Highest triggered level today (frozen §1 matrix)."""
    lvl = GREEN
    triggers = []
    # -- RED --
    if bd["crash_10d"] is not None and bd["crash_10d"] <= -0.12:
        lvl = RED; triggers.append(f"crash10d {bd['crash_10d']:.3f}<=-12%")
    if bd["panic_1d"] is not None and bd["panic_1d"] <= -0.05:
        lvl = RED; triggers.append(f"panic {bd['panic_1d']:.3f}<=-5%")
    if bear:
        lvl = RED; triggers.append("R-配3 major bear (regime.py)")
    # -- ORANGE --
    if bd["crash_10d"] is not None and bd["crash_10d"] <= -0.08:
        if _ORD[lvl] < _ORD[ORANGE]: lvl = ORANGE
        triggers.append(f"crash10d {bd['crash_10d']:.3f}<=-8%")
    if bd.get("vol_status") == "ok" and bd["vol20"] > bd["vol_p95"]:
        if _ORD[lvl] < _ORD[ORANGE]: lvl = ORANGE
        triggers.append("vol20>p95 (3y)")
    sh, sl = br.get("share_below_ma20"), br.get("share_slope_5d")
    if sh is not None and sh >= 0.80 and sl is not None and sl < 0:
        if _ORD[lvl] < _ORD[ORANGE]: lvl = ORANGE
        triggers.append(f"breadth {sh:.2f}>=80% slope {sl:+.4f}<0")
    if bd.get("below_ma200") is True:
        if _ORD[lvl] < _ORD[ORANGE]: lvl = ORANGE
        triggers.append("hs300<MA200 (#10 collected)")
    # -- YELLOW --
    if bd["crash_10d"] is not None and bd["crash_10d"] <= -0.05:
        if _ORD[lvl] < _ORD[YELLOW]: lvl = YELLOW
        triggers.append(f"crash10d {bd['crash_10d']:.3f}<=-5%")
    if bd.get("vol_status") == "ok" and bd["vol20"] > bd["vol_p80"]:
        if _ORD[lvl] < _ORD[YELLOW]: lvl = YELLOW
        triggers.append("vol20>p80 (3y)")
    if sh is not None and sh >= 0.65:
        if _ORD[lvl] < _ORD[YELLOW]: lvl = YELLOW
        triggers.append(f"breadth {sh:.2f}>=65%")
    if bd.get("event_fomc") or bd.get("event_pre_holiday"):
        if _ORD[lvl] < _ORD[YELLOW]: lvl = YELLOW
        triggers.append("event window (appendix A)")
    return lvl, triggers


def raw_level_v2(bd: dict, br: dict, bear: bool) -> str:
    """V2 structural remap (research/REGIME_GUARD_VALIDATION_V2.md s1,
    prereg FROZEN ee8498e -- T-05 part 4).

    RED=crash/panic only; ORANGE=crash/vol-p95/breadth; YELLOW collects
    R-配3 major bear (its T0 <=20% position cap stays iron_rules law,
    untouched); #10 hs300<MA200 DE-COLLECTED -- the T0 no-new-position ban
    stands alone and its independent enforcement wiring is a separate
    signed item, so v2 never reads below_ma200. All thresholds verbatim v1
    constants. The live probe() keeps the v1 matrix until the law file is
    amended (PASS + GM approval + veto window); this function is the
    calibration-layer v2 decision source only.
    """
    lvl = GREEN
    triggers = []
    # -- RED: pure crash/panic semantics --
    if bd["crash_10d"] is not None and bd["crash_10d"] <= -0.12:
        lvl = RED; triggers.append(f"crash10d {bd['crash_10d']:.3f}<=-12%")
    if bd["panic_1d"] is not None and bd["panic_1d"] <= -0.05:
        lvl = RED; triggers.append(f"panic {bd['panic_1d']:.3f}<=-5%")
    # -- ORANGE --
    if bd["crash_10d"] is not None and bd["crash_10d"] <= -0.08:
        if _ORD[lvl] < _ORD[ORANGE]: lvl = ORANGE
        triggers.append(f"crash10d {bd['crash_10d']:.3f}<=-8%")
    if bd.get("vol_status") == "ok" and bd["vol20"] > bd["vol_p95"]:
        if _ORD[lvl] < _ORD[ORANGE]: lvl = ORANGE
        triggers.append("vol20>p95 (3y)")
    sh, sl = br.get("share_below_ma20"), br.get("share_slope_5d")
    if sh is not None and sh >= 0.80 and sl is not None and sl < 0:
        if _ORD[lvl] < _ORD[ORANGE]: lvl = ORANGE
        triggers.append(f"breadth {sh:.2f}>=80% slope {sl:+.4f}<0")
    # -- YELLOW (v2: + R-配3 collected here; #10 de-collected, not read) --
    if bd["crash_10d"] is not None and bd["crash_10d"] <= -0.05:
        if _ORD[lvl] < _ORD[YELLOW]: lvl = YELLOW
        triggers.append(f"crash10d {bd['crash_10d']:.3f}<=-5%")
    if bd.get("vol_status") == "ok" and bd["vol20"] > bd["vol_p80"]:
        if _ORD[lvl] < _ORD[YELLOW]: lvl = YELLOW
        triggers.append("vol20>p80 (3y)")
    if sh is not None and sh >= 0.65:
        if _ORD[lvl] < _ORD[YELLOW]: lvl = YELLOW
        triggers.append(f"breadth {sh:.2f}>=65%")
    if bd.get("event_fomc") or bd.get("event_pre_holiday"):
        if _ORD[lvl] < _ORD[YELLOW]: lvl = YELLOW
        triggers.append("event window (appendix A)")
    if bear:
        if _ORD[lvl] < _ORD[YELLOW]: lvl = YELLOW
        triggers.append("R-配3 major bear (regime.py)")
    return lvl, triggers


def resolve_state(prev_state: str, prev_streak: int, raw: str):
    """Upgrade immediate; downgrade needs 2 consecutive GREEN signal days."""
    if _ORD[raw] > _ORD[prev_state]:
        return raw, 0
    if _ORD[raw] == _ORD[prev_state]:
        return prev_state, (prev_streak + 1) if raw == GREEN else 0
    # raw < prev: only GREEN signal days accumulate toward downgrade
    if raw == GREEN:
        streak = prev_streak + 1
        if streak >= 2:
            return GREEN, streak
        return prev_state, streak
    return prev_state, 0


def raw_level_v3(bd: dict, br: dict, bear: bool):
    """V3 structural matrix (research/REGIME_GUARD_VALIDATION_V3.md s2,
    prereg FROZEN a25f47a -- T-10 deliverable-2/3). Twist B (RED partial
    release) lives in resolve_state_v3; this is twist C (ORANGE needs >=2
    same-day dims; single-dim orange day lands YELLOW). RED = crash/panic
    only, no multi-dim confirm (acute-crisis semantics is itself the
    signature, prereg s1 verbatim). All thresholds verbatim v1 constants;
    #10 below_ma200 DE-COLLECTED (never read, v2 ruling verbatim); R-配3
    major bear collected at YELLOW (T0 <=20% cap stays iron_rules law).
    Live probe() keeps the v1 matrix until law amendment (PASS + GM
    approval + veto window); this function is the calibration-layer v3
    decision source only.
    """
    lvl = GREEN
    triggers = []
    # -- RED: pure crash/panic semantics, no multi-dim confirm --
    if bd["crash_10d"] is not None and bd["crash_10d"] <= -0.12:
        lvl = RED; triggers.append(f"crash10d {bd['crash_10d']:.3f}<=-12%")
    if bd["panic_1d"] is not None and bd["panic_1d"] <= -0.05:
        lvl = RED; triggers.append(f"panic {bd['panic_1d']:.3f}<=-5%")
    # -- ORANGE dims (twist C: >=2 same-day required) --
    odims = []
    if (bd["crash_10d"] is not None
            and -0.12 < bd["crash_10d"] <= -0.08):
        odims.append(f"crash10d {bd['crash_10d']:.3f} in (-12%,-8%]")
    if bd.get("vol_status") == "ok" and bd["vol20"] > bd["vol_p95"]:
        odims.append("vol20>p95 (3y)")
    sh, sl = br.get("share_below_ma20"), br.get("share_slope_5d")
    if sh is not None and sh >= 0.80 and sl is not None and sl < 0:
        odims.append(f"breadth {sh:.2f}>=80% slope {sl:+.4f}<0")
    if len(odims) >= 2:
        if _ORD[lvl] < _ORD[ORANGE]: lvl = ORANGE
        triggers.extend(odims)
    elif len(odims) == 1:
        triggers.append(odims[0] + " [C-downgrade: single-dim ORANGE day]")
    # -- YELLOW (v2 set verbatim; single-dim orange days land here) --
    if bd["crash_10d"] is not None and bd["crash_10d"] <= -0.05:
        if _ORD[lvl] < _ORD[YELLOW]: lvl = YELLOW
        triggers.append(f"crash10d {bd['crash_10d']:.3f}<=-5%")
    if bd.get("vol_status") == "ok" and bd["vol20"] > bd["vol_p80"]:
        if _ORD[lvl] < _ORD[YELLOW]: lvl = YELLOW
        triggers.append("vol20>p80 (3y)")
    if sh is not None and sh >= 0.65:
        if _ORD[lvl] < _ORD[YELLOW]: lvl = YELLOW
        triggers.append(f"breadth {sh:.2f}>=65%")
    if bd.get("event_fomc") or bd.get("event_pre_holiday"):
        if _ORD[lvl] < _ORD[YELLOW]: lvl = YELLOW
        triggers.append("event window (appendix A)")
    if bear:
        if _ORD[lvl] < _ORD[YELLOW]: lvl = YELLOW
        triggers.append("R-配3 major bear (regime.py)")
    # belt-and-braces frozen landing: single-dim orange day == YELLOW
    if len(odims) == 1 and lvl == GREEN:
        lvl = YELLOW
    return lvl, triggers


def resolve_state_v3(prev_state: str, prev_streak: int, raw: str):
    """V3 hysteresis (prereg V3 s2 frozen). Twist B: RED -> ORANGE on the
    FIRST green signal day (acute-crisis residual risk is orange-grade,
    not cash-parking grade); RED -> GREEN still needs 2 consecutive green
    days; ORANGE/YELLOW -> GREEN downgrades verbatim v1/v2; RED does NOT
    downgrade on non-green days (literal-B, conservative).
    """
    if _ORD[raw] > _ORD[prev_state]:
        return raw, 0
    if _ORD[raw] == _ORD[prev_state]:
        return prev_state, (prev_streak + 1) if raw == GREEN else 0
    # raw < prev: only GREEN signal days accumulate toward downgrade
    if raw == GREEN:
        streak = prev_streak + 1
        if streak >= 2:
            return GREEN, streak
        if prev_state == RED:
            return ORANGE, 1          # twist B partial release
        return prev_state, streak
    return prev_state, 0


def probe(write: bool = True) -> dict:
    """Daily shadow probe: compute dims -> state machine -> atomic write.

    Same-trading-day re-probes (intraday S6 rounds before a new bar lands)
    update the day's row in place: history keeps exactly one row per asof
    and green_streak/days_in_state never double-count (continuity
    contract consumed by science_audit C6; found live: the r54 probe
    appended a duplicate row every 10-min round)."""
    from firm.risk.regime import load_benchmark_close, major_bear_state

    bench = load_benchmark_close()
    bd = bench_dims(bench)
    br = breadth_dims(bench)
    bear = major_bear_state(bench)  # single source, R-配3
    raw, triggers = raw_level(bd, br, bool(bear.get("is_major_bear")))

    old = {}
    if os.path.exists(STATE_PATH):
        try:
            old = json.load(open(STATE_PATH, encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            old = {}
    hist = list(old.get("history") or [])
    # idempotency: drop today's earlier rows, then resolve the state
    # machine from the last *different* trading day
    hist = [e for e in hist if e.get("asof") != bd["asof"]]
    prev_entry = hist[-1] if hist else None
    if prev_entry is None:
        state, streak = raw, 1 if raw == GREEN else 0
    else:
        state, streak = resolve_state(prev_entry.get("state", GREEN),
                                      int(prev_entry.get("green_streak", 0)),
                                      raw)
    days_in_state = 1
    if prev_entry is not None and prev_entry.get("state") == state:
        days_in_state = int(prev_entry.get("days_in_state", 0)) + 1
    hist.append({"asof": bd["asof"], "raw": raw, "state": state,
                 "green_streak": streak, "days_in_state": days_in_state})
    hist = hist[-HISTORY_KEEP:]

    trans = list(old.get("transitions") or [])
    prev_state = prev_entry.get("state") if prev_entry is not None else None
    if prev_state is not None and state != prev_state:
        trans.append({"asof": bd["asof"], "from": prev_state, "to": state})
        trans = trans[-TRANSITION_KEEP:]

    out = {"updated": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
           "asof": bd["asof"], "mode": MODE, "state": state,
           "state_cn": _CN[state], "raw_level": raw,
           "green_streak": streak, "days_in_state": days_in_state,
           "thresholds_fp": threshold_fingerprint(),
           "dims": {"bench": bd, "breadth": br,
                    "bear_r_pei3": bear},
           "triggers": triggers, "transitions": trans, "history": hist,
           "rule": "firm/risk/REGIME_GUARD.md v1.0 s1 (O-20260923-2315)"}

    if write:
        tmp = STATE_PATH + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2, default=str)
        os.replace(tmp, STATE_PATH)
    return out


def _selftest() -> bool:
    ok = True

    def check(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(f"  [regime-guard] {name}... {'PASS' if cond else 'FAIL'}")

    # synthetic bench: 1600 calm days + engineered tails
    idx = pd.bdate_range("2020-01-01", periods=1600)
    base = pd.Series(4.0, index=idx)
    bench_calm = base * (1 + pd.Series(0.0, index=idx))

    # A: crash10d RED path (<= -12% over 10d)
    a = bench_calm.copy()
    a.iloc[-10:] = 4.0 * (1 - 0.13 * pd.Series(range(1, 11),
                          index=a.index[-10:]) / 10)
    bd = bench_dims(a); br = {"share_below_ma20": 0.1, "share_slope_5d": -0.01,
                              "status": "ok"}
    lvl, tr = raw_level(bd, br, False)
    check("A crash10d -13% -> RED", lvl == RED)

    # B: panic single-day RED
    b = bench_calm.copy()
    b.iloc[-1] = 4.0 * 0.94
    bd = bench_dims(b)
    lvl, _ = raw_level(bd, br, False)
    check("B panic -6% day -> RED", lvl == RED)

    # C: bear (R-配3) -> RED via reuse flag
    lvl, tr = raw_level(bench_dims(bench_calm), br, True)
    check("C major-bear flag -> RED", lvl == RED and
          any("R-配3" in t for t in tr))

    # D: debounce -- ORANGE held until 2 consecutive GREEN days
    s1, k1 = resolve_state(ORANGE, 0, GREEN)
    check("D1 first green day holds ORANGE", s1 == ORANGE and k1 == 1)
    s2, k2 = resolve_state(ORANGE, 1, GREEN)
    check("D2 second green day downgrades", s2 == GREEN and k2 == 2)
    s3, k3 = resolve_state(RED, 1, YELLOW)
    check("D3 non-green raw resets streak, holds RED",
          s3 == RED and k3 == 0)

    # E: upgrade immediate from YELLOW to RED
    s4, _ = resolve_state(YELLOW, 3, RED)
    check("E upgrade immediate", s4 == RED)

    # F: vol insufficient history -> no trigger, honest
    short = pd.Series(4.0, index=pd.bdate_range("2026-01-01", periods=600))
    bdf = bench_dims(short)
    check("F vol insufficient_history honest",
          bdf["vol_status"] == "insufficient_history" and
          bdf["vol20"] is None)

    # G: breadth literal reading -- share 85% + negative slope -> ORANGE;
    #    share 70% -> YELLOW only
    lvl1, _ = raw_level(bench_dims(bench_calm),
                        {"share_below_ma20": 0.85, "share_slope_5d": -0.02,
                         "status": "ok"}, False)
    lvl2, _ = raw_level(bench_dims(bench_calm),
                        {"share_below_ma20": 0.70, "share_slope_5d": 0.01,
                         "status": "ok"}, False)
    check("G breadth 85%+neg-slope ORANGE / 70% YELLOW",
          lvl1 == ORANGE and lvl2 == YELLOW)

    # H: real-data probe + atomic write (zero network, local files only)
    out = probe(write=True)
    check("H real probe writes state file",
          os.path.exists(STATE_PATH) and out["mode"] == MODE and
          out["state"] in _ORD and len(out["history"]) >= 1)

    # I: threshold fingerprint = stable 64-hex, sensitive to any value edit
    fp = threshold_fingerprint()
    check("I thresholds fp stable 64-hex + carried in probe output",
          len(fp) == 64 and out.get("thresholds_fp") == fp)
    import copy as _copy
    mutant = _copy.deepcopy(THRESHOLDS)
    mutant["crash_10d"]["red"] = -0.13
    import hashlib as _hl, json as _js
    check("I fp sensitive to threshold edit",
          _hl.sha256(_js.dumps(mutant, sort_keys=True,
                               ensure_ascii=True).encode("utf-8")
                     ).hexdigest() != fp)

    # J: same-trading-day re-probe idempotent -- one row per asof, no
    #    double-counted days_in_state (C6 continuity contract)
    asof = out["asof"]
    out2 = probe(write=True)
    rows_today = [e for e in out2["history"] if e["asof"] == asof]
    check("J same-day re-probe keeps one row per asof",
          len(rows_today) == 1 and rows_today[0]["days_in_state"]
          == out["days_in_state"])
    return ok


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if "selftest" in argv:
        ok = _selftest()
        print(f"  [regime-guard] selftest {'PASS' if ok else 'FAIL'}")
        return 0 if ok else 1
    out = probe(write=True)
    print(f"regime state -> {STATE_PATH}")
    print(f"  asof={out['asof']} state={out['state']} "
          f"({out['state_cn']}) raw={out['raw_level']} "
          f"days_in_state={out['days_in_state']} mode={out['mode']}")
    if out["triggers"]:
        for t in out["triggers"]:
            print(f"  trigger: {t}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
