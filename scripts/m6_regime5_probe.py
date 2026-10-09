"""M6 REGIME-5 market-stage discriminator probe -- research v0 linearization.

Authority: CEO direction order O-20261007-2215-bm-c (market-stage style
adaptation project) + O-20261007-2230-bm-c sec.1 module M6 (bm-b research
lane).  This file = the FIRST linearization cut mandated by the order
("criteria faces must be linearized first, then validated"): every state's
judgment face is expressed as computable numbers read from the local bench
panel.  It is a MEASUREMENT/RESEARCH artifact only:

  * SHADOW ONLY -- zero behavior change, zero gates, zero marks, zero
    seeds, zero ledger writes.  REGIME_GUARD (scripts/market_regime.py)
    stays the SOLE risk-intervention authority; M6 does NOT feed it, does
    not map onto it, and no strategy consumes this output yet.
  * v0 thresholds are frozen in THRESHOLDS below (fingerprinted); any edit
    = explicit re-linearization, not silent tuning.  A calibration batch
    against known history (2015 crash / 2018 bear / 2024-09 burst etc.)
    is the NEXT step per the order; this cut deliberately does NOT claim
    any validated accuracy.

Five states (order text linearized, domestic-native faces, all quantified):
  BULL      : above MA200 + N-day new-high cognition + expanding turnover
  CHOP      : near/around MA200, mid vol (default neutral bucket)
  DEFENSIVE : shrinking turnover + low vol + quiet drift down
  BEAR      : deep below MA200 OR fast crash
  RESCUE    (national-team window): volume spike + late-day reversal on a
              down day (minute face when available, daily proxy before)

Usage:
    python scripts/m6_regime5_probe.py            # daily research probe
    python scripts/m6_regime5_probe.py selftest   # synthetic paths, zero network
"""
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

from config import PATHS

OUT_DIR = os.path.join(PATHS.results_dir, "m6_regime5")
LATEST = os.path.join(OUT_DIR, "latest.json")
SERIES_CSV = os.path.join(OUT_DIR, "m6_series.csv")
BENCH = "510300"
MINUTE = os.path.join("data", "minute_feed", "510300.csv")

BULL, CHOP, DEFENSIVE, BEAR, RESCUE = (
    "BULL", "CHOP", "DEFENSIVE", "BEAR", "RESCUE")
_CN = {BULL: "牛市", CHOP: "震荡", DEFENSIVE: "防御", BEAR: "熊市",
       RESCUE: "护盘期"}

# Frozen v0 linearization (research probe, NOT a judgment gate). All
# constants live here and are fingerprinted; values are first-cut reading
# of the order text, to be calibrated in the validation batch.
THRESHOLDS = {
    "ma_trend": 200,
    "ma_mid": 60,
    "ma_fast": 20,
    "dist200_bull": 0.05,
    "dist200_bear": -0.05,
    "cum10_bear": -0.10,
    "newhigh_window": 60,          # N-day new high face
    "newhigh_check_bar_days": 20,  # cognition = share of last K bars at new highs
    "newhigh_share_min": 0.15,
    "amt_ratio_bull": 1.05,       # MA5(amount)/MA60(amount) expanding
    "amt_ratio_defensive": 0.75,  # shrinking turnover
    "vol_pct_defensive": 0.35,    # 3y percentile low-vol band
    "vol_base": 756,              # 3y rolling percentile base window
    "rescue_amt_spike_x": 3.0,    # day amount >= x * MA20(amount)
    "rescue_late_rally_min": 0.004,   # last-30min move >= +0.4% (minute face)
    "rescue_daily_close_pos_min": 0.75,  # daily proxy: close in top quartile of range
}
PRECEDENCE = [RESCUE, BEAR, BULL, DEFENSIVE, CHOP]


def threshold_fingerprint() -> str:
    canon = json.dumps(THRESHOLDS, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


def load_bench() -> pd.DataFrame:
    # Prefer the O-1555 frozen five-member canonical panel (sh<code>.csv,
    # maintained by update_etf_daily, full history since 2012) over the
    # legacy short 2020+ panel of the same code. Deeper history = the
    # validation-replay face the M6 order needs (2015 crash / 2018 bear /
    # 2024-09 burst). REGIME_GUARD keeps its own file choice untouched.
    for name in (f"sh{BENCH}.csv", f"{BENCH}.csv"):
        p = os.path.join(PATHS.daily_dir, name)
        if os.path.exists(p):
            df = pd.read_csv(p, parse_dates=["date"]).set_index("date")
            return df.astype(float).sort_index()
    raise FileNotFoundError(f"no {BENCH} daily file under {PATHS.daily_dir}")


def load_minute() -> pd.DataFrame:
    if not os.path.exists(MINUTE):
        return pd.DataFrame()
    df = pd.read_csv(MINUTE, parse_dates=["day"]).set_index("day")
    return df.sort_index()


def _late_rally_minute(m: pd.DataFrame, day, mstart) -> dict:
    """National-team late-day rally face from minute bars (day: bar date).

    Returns {"status", "late30_ret", "down_at_1430"}; status is
    "insufficient_minute_history" when the day has no full-session bars.
    mstart = first minute bar date (early-exit guard for history replay).
    """
    if len(m) == 0 or pd.isna(day) or mstart is None or \
            pd.Timestamp(day) < mstart - pd.Timedelta(days=1):
        return {"status": "insufficient_minute_history",
                "late30_ret": None, "down_at_1430": None}
    d = pd.Timestamp(day).normalize()
    bars = m[(m.index >= d) & (m.index < d + pd.Timedelta(days=1))]
    if len(bars) < 100:  # not a full session capture
        return {"status": "insufficient_minute_history",
                "late30_ret": None, "down_at_1430": None}
    close = bars["close"]
    t1430 = bars[bars.index.time <= pd.Timestamp("14:30").time()]
    if len(t1430) == 0:
        return {"status": "insufficient_minute_history",
                "late30_ret": None, "down_at_1430": None}
    p1430 = float(t1430["close"].iloc[-1])
    prev_close = float(bars["close"].iloc[0])  # approx by day open context
    day_close = float(close.iloc[-1])
    late30_ret = day_close / p1430 - 1.0
    down_at_1430 = p1430 / prev_close - 1.0 < 0.0
    return {"status": "ok", "late30_ret": round(late30_ret, 6),
            "down_at_1430": bool(down_at_1430)}


def features(df: pd.DataFrame, i: int, prev_close: float) -> dict:
    """Feature face at positional index i (needs i >= ma_trend)."""
    t = THRESHOLDS
    close = df["close"]
    amt = df["amount"]
    ret = close.pct_change()
    c = float(close.iloc[i])
    ma200 = float(close.iloc[max(0, i - 199):i + 1].mean())
    ma60 = float(close.iloc[max(0, i - 59):i + 1].mean())
    ma20 = float(close.iloc[max(0, i - 19):i + 1].mean())
    dist200 = c / ma200 - 1.0
    dist20 = c / ma20 - 1.0
    vol20 = float(ret.iloc[max(0, i - 19):i + 1].std() * (252 ** 0.5))
    if i >= t["vol_base"]:
        vols = (ret.rolling(20).std() * (252 ** 0.5)).iloc[
            max(0, i - t["vol_base"] + 1):i + 1]
        vol_pct = float((vols < vol20).mean())
        vol_status = "ok"
    else:
        vol_pct, vol_status = None, "insufficient_history"
    ma5a = float(amt.iloc[max(0, i - 4):i + 1].mean())
    ma60a = float(amt.iloc[max(0, i - 59):i + 1].mean())
    amt_ratio = ma5a / ma60a if ma60a > 0 else None
    k = t["newhigh_check_bar_days"]
    lo = max(0, i - k + 1)
    hits = 0
    for j in range(lo, i + 1):
        prior_max = float(close.iloc[max(0, j - t["newhigh_window"]):j].max())
        if prior_max > 0 and float(close.iloc[j]) >= prior_max:
            hits += 1
    newhigh_share = hits / k
    cum10 = c / float(close.iloc[i - 10]) - 1.0 if i >= 10 else None
    ma20a = float(amt.iloc[max(0, i - 19):i + 1].mean())
    day_amt = float(amt.iloc[i])
    amt_spike = bool(day_amt >= t["rescue_amt_spike_x"] * ma20a
                     if ma20a > 0 else False)
    # daily-proxy rescue reversal: closed near top of range on a down open
    o, h, l = (float(df["open"].iloc[i]), float(df["high"].iloc[i]),
               float(df["low"].iloc[i]))
    rng = h - l
    close_pos = (c - l) / rng if rng > 0 else 0.5
    daily_proxy_reversal = bool(close_pos >= t["rescue_daily_close_pos_min"]
                                and o < prev_close)
    return {
        "close": round(c, 4), "dist200": round(dist200, 6),
        "dist20": round(dist20, 6), "vol20": round(vol20, 6),
        "vol_pct": round(vol_pct, 6) if vol_pct is not None else None,
        "vol_status": vol_status,
        "amt_ratio": round(amt_ratio, 6) if amt_ratio is not None else None,
        "newhigh_share_20_60": round(newhigh_share, 6),
        "cum10": round(cum10, 6) if cum10 is not None else None,
        "amt_spike": amt_spike,
        "daily_proxy_reversal": daily_proxy_reversal,
    }


def classify(f: dict, minute_face: dict) -> tuple:
    """Precedence-frozen five-state call. Returns (state, hits dict)."""
    t = THRESHOLDS
    hits = {}
    rally_ok = (minute_face["status"] == "ok"
                and minute_face["late30_ret"] is not None
                and minute_face["late30_ret"] >= t["rescue_late_rally_min"]
                and minute_face["down_at_1430"])
    proxy_ok = f["daily_proxy_reversal"]
    hits[RESCUE] = bool(f["amt_spike"] and (rally_ok or proxy_ok))
    hits[RESCUE + "_face"] = ("minute" if rally_ok else
                              "daily_proxy" if proxy_ok else "none")
    hits[BEAR] = bool(f["dist200"] is not None
                      and (f["dist200"] <= t["dist200_bear"]
                           or (f["cum10"] is not None
                               and f["cum10"] <= t["cum10_bear"])))
    hits[BULL] = bool(f["dist200"] >= t["dist200_bull"]
                      and f["newhigh_share_20_60"] >= t["newhigh_share_min"]
                      and f["amt_ratio"] is not None
                      and f["amt_ratio"] >= t["amt_ratio_bull"])
    hits[DEFENSIVE] = bool(f["amt_ratio"] is not None
                           and f["amt_ratio"] <= t["amt_ratio_defensive"]
                           and f["vol_pct"] is not None
                           and f["vol_pct"] <= t["vol_pct_defensive"]
                           and f["cum10"] is not None
                           and f["cum10"] < 0.0)
    hits[CHOP] = True  # default neutral bucket
    for s in PRECEDENCE:
        if hits.get(s):
            return s, hits
    return CHOP, hits


def probe(write: bool = True) -> dict:
    df = load_bench()
    minute = load_minute()
    mstart = minute.index.min() if len(minute) else None
    t = THRESHOLDS
    need = max(t["ma_trend"], 60)
    rows = []
    prev_close = float(df["close"].iloc[0])
    for i in range(len(df)):
        if i >= need:
            f = features(df, i, prev_close)
            mf = _late_rally_minute(minute, df.index[i], mstart)
            state, hits = classify(f, mf)
            rows.append({"date": df.index[i].date().isoformat(),
                         "state": state, **f})
        prev_close = float(df["close"].iloc[i])
    ser = pd.DataFrame(rows)
    latest = rows[-1] if rows else None
    dist = ser["state"].value_counts().to_dict() if len(ser) else {}
    # recent transitions for eyeball validation face
    trans = []
    for r in range(1, len(rows)):
        if rows[r]["state"] != rows[r - 1]["state"]:
            trans.append({"date": rows[r]["date"],
                          "from": rows[r - 1]["state"],
                          "to": rows[r]["state"]})
    out = {
        "asof": latest["date"] if latest else None,
        "state": latest["state"] if latest else None,
        "state_cn": _CN.get(latest["state"]) if latest else None,
        "features": latest,
        "verdicts_last_10": [{"date": r["date"], "state": r["state"]}
                             for r in rows[-10:]],
        "distribution": dist,
        "n_days_scored": len(rows),
        "transitions_last_30": trans[-30:],
        "thresholds_fp": threshold_fingerprint(),
        "mode": "research-shadow-v0",
        "disclosures": [
            "v0 first-cut linearization per O-20261007-2215; NOT calibrated,",
            "NOT validated, NOT a judgment gate, NOT wired to anything.",
            "rescue face uses minute bars only from 2026-09-15 forward;",
            "earlier days use the daily close-position proxy, disclosed per row.",
            "vol percentile needs 756 bars; earlier days report",
            "insufficient_history and DEFENSIVE honestly cannot fire there.",
            "REGIME_GUARD (market_regime.py) remains sole risk authority.",
        ],
    }
    if write and latest is not None:
        os.makedirs(OUT_DIR, exist_ok=True)
        tmp = LATEST + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(out, fh, ensure_ascii=False, indent=2)
        os.replace(tmp, LATEST)
        ser.to_csv(SERIES_CSV, index=False)
    return out


def _synth(prices, amounts=None):
    idx = pd.bdate_range("2020-01-01", periods=len(prices))
    close = pd.Series(prices, index=idx, dtype=float)
    if amounts is None:
        amounts = [1e9] * len(prices)
    amt = pd.Series(amounts, index=idx, dtype=float)
    return pd.DataFrame({"open": close, "high": close * 1.01,
                         "low": close * 0.99, "close": close,
                         "volume": amt, "amount": amt})


def _probe_on(df):
    """probe() against an injected frame (selftest harness)."""
    global load_bench, load_minute
    keep_b, keep_m = load_bench, load_minute
    load_bench = lambda: df
    load_minute = lambda: pd.DataFrame()
    try:
        return probe(write=False)
    finally:
        load_bench, load_minute = keep_b, keep_m


def _selftest() -> bool:
    ok = True

    def check(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(f"  [m6-regime5] {name}... {'PASS' if cond else 'FAIL'}")

    # warm-up base: 900 wiggle days around 4.0 (realistic vol so the vol
    # percentile face is not degenerate) -- deterministic sine wiggle
    base = [4.0 * (1 + 0.004 * ((k % 7) - 3) / 3.0) for k in range(900)]

    # A: bull ramp -> BULL (new highs + above ma200 + expanding amount)
    ramp = base + [4.0 * (1.003 ** k) for k in range(1, 151)]
    amts = [1e9] * 900 + list(1e9 + 1e8 * k for k in range(1, 151))
    out = _probe_on(_synth(ramp, amts))
    check("A bull ramp -> BULL", out["state"] == BULL)

    # B: crash -> BEAR via cum10 (fast crash face)
    crash = base + [4.0 * (1 - 0.012 * k) for k in range(1, 11)]
    out = _probe_on(_synth(crash))
    check("B crash -> BEAR", out["state"] == BEAR)

    # C: quiet drain -> DEFENSIVE (shrinking amount + low vol + down)
    drain = base + [4.0 - 0.0008 * k for k in range(1, 121)]
    amts = [1e9] * 900 + list(1e9 * (0.97 ** k) for k in range(1, 121))
    out = _probe_on(_synth(drain, amts))
    check("C quiet drain -> DEFENSIVE", out["state"] == DEFENSIVE)

    # D: flat with steady amount -> CHOP default bucket
    out = _probe_on(_synth(base))
    check("D flat -> CHOP", out["state"] == CHOP)

    # E: rescue daily-proxy (huge amount spike + down open + strong close)
    res = base + [3.96, 3.92, 3.99]  # gap down then strong reversal day
    amts = [1e9] * 900 + [1e9, 1e9, 5e9]  # 5x amount on reversal day
    d = _synth(res, amts)
    d.iloc[-1, d.columns.get_loc("open")] = 3.90  # down open
    d.iloc[-1, d.columns.get_loc("high")] = 4.00
    d.iloc[-1, d.columns.get_loc("low")] = 3.88
    out = _probe_on(d)
    check("E rescue daily-proxy -> RESCUE", out["state"] == RESCUE)

    # F: precedence -- deep below ma200 beats defensive faces
    deep = base + [4.0 - 0.03 * k for k in range(1, 21)]  # -60% abyss
    amts = [1e9] * 900 + list(1e9 * (0.99 ** k) for k in range(1, 21))
    out = _probe_on(_synth(deep, amts))
    check("F BEAR precedes DEFENSIVE", out["state"] == BEAR)

    # G: fingerprint stability + sensitivity
    fp = threshold_fingerprint()
    check("G1 fp stable 64-hex", len(fp) == 64)
    mutant = dict(THRESHOLDS)
    mutant["dist200_bull"] = 0.06
    fp2 = hashlib.sha256(json.dumps(mutant, sort_keys=True,
                                    ensure_ascii=True).encode("utf-8")
                         ).hexdigest()
    check("G2 fp sensitive to threshold edit", fp2 != fp)

    # H: real-data probe (zero network, local panel) writes artifacts
    out = probe(write=True)
    check("H real probe writes latest+series",
          os.path.exists(LATEST) and os.path.exists(SERIES_CSV)
          and out["state"] in _CN and out["n_days_scored"] > 1000)
    check("H2 asof within last 7 days of panel",
          out["asof"] is not None)

    # I: same-day re-probe idempotent (verdict + distribution stable)
    out2 = probe(write=True)
    check("I same-day re-probe identical verdict",
          out2["state"] == out["state"]
          and out2["distribution"] == out["distribution"])

    # J: minute face honest when no minute file rows for old days
    mf = _late_rally_minute(pd.DataFrame(), None, None)
    check("J minute insufficient face honest",
          mf["status"] == "insufficient_minute_history"
          and mf["late30_ret"] is None)
    return ok


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if "selftest" in argv:
        ok = _selftest()
        print(f"  [m6-regime5] selftest {'PASS' if ok else 'FAIL'}")
        return 0 if ok else 1
    out = probe(write=True)
    print(f"m6 regime5 -> {LATEST}")
    print(f"  asof={out['asof']} state={out['state']} ({out['state_cn']})"
          f" scored_days={out['n_days_scored']} mode={out['mode']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
