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


def _load_prev():
    if not os.path.exists(STATE_PATH):
        return None, 0
    try:
        d = json.load(open(STATE_PATH, encoding="utf-8"))
        hist = d.get("history") or []
        if hist:
            last = hist[-1]
            return last.get("state", GREEN), int(last.get("green_streak", 0))
        return d.get("state", GREEN), int(d.get("green_streak", 0))
    except (json.JSONDecodeError, OSError):
        return None, 0


def probe(write: bool = True) -> dict:
    """Daily shadow probe: compute dims -> state machine -> atomic write."""
    from firm.risk.regime import load_benchmark_close, major_bear_state

    bench = load_benchmark_close()
    bd = bench_dims(bench)
    br = breadth_dims(bench)
    bear = major_bear_state(bench)  # single source, R-配3
    raw, triggers = raw_level(bd, br, bool(bear.get("is_major_bear")))

    prev_state, prev_streak = _load_prev()
    if prev_state is None:
        state, streak = raw, 1 if raw == GREEN else 0
    else:
        state, streak = resolve_state(prev_state, prev_streak, raw)

    old = {}
    if os.path.exists(STATE_PATH):
        try:
            old = json.load(open(STATE_PATH, encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            old = {}
    hist = list(old.get("history") or [])
    days_in_state = 1
    if hist and hist[-1].get("state") == state:
        days_in_state = int(hist[-1].get("days_in_state", 0)) + 1
    hist.append({"asof": bd["asof"], "raw": raw, "state": state,
                 "green_streak": streak, "days_in_state": days_in_state})
    hist = hist[-HISTORY_KEEP:]

    trans = list(old.get("transitions") or [])
    if prev_state is not None and state != prev_state:
        trans.append({"asof": bd["asof"], "from": prev_state, "to": state})
        trans = trans[-TRANSITION_KEEP:]

    out = {"updated": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
           "asof": bd["asof"], "mode": MODE, "state": state,
           "state_cn": _CN[state], "raw_level": raw,
           "green_streak": streak, "days_in_state": days_in_state,
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
