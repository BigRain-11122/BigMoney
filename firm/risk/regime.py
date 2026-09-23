"""Major-bear regime detector + portfolio position cap (O-20260923-1820 R-配3).

Why: CEO red line "大熊市只能配 20% 仓位" is T0-effective immediately.
Definition (GM-drafted, T1 7-day veto window, verbatim in firm/risk/
iron_rules.md): major bear = 沪深300 收盘 < 250 日均线 且 自 250 日收盘
高点回撤 >= 20% (dual condition, BOTH required); either condition no
longer holding ends the regime. During major bear: total equity position
<= 20% (stocks+ETF combined), cash/reverse-repo >= 80%.

Scope guard (order item 5): backtest history is used ONLY to validate the
detector; registered trader evidence is never rewritten (evidence_cutoff
doctrine). Enforcement point = portfolio allocation layer; in paper domain
the regime state rides along each paper state so the cap is visible before
any live gate exists. Existing engine rules (iron rule 10, hs300 < MA200
no-new-positions) are untouched -- this module is additive.

Benchmark proxy: 510300 沪深300ETF close (core48 member, maintained by
scripts/update_daily; bare-code file preferred, prefix twin fallback --
J9a proved the twins byte-identical on overlap).

Usage:
    python -m firm.risk.regime            # print regime state (real data)
    python -m firm.risk.regime --selftest # synthetic edge cases + real data
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

import pandas as pd

from config import PATHS

MA_WINDOW = 250          # 250-day moving average
DD_LINE = -0.20          # drawdown from 250d close high >= 20% (negative)
CAP_MAJOR_BEAR = 0.20    # R-配3: total position <= 20% in major bear
CAP_NORMAL = 0.80        # existing global hard rule 2 (total <= 80%)
HS300_PROXY = "510300"   # core48 bare code; twin = sh510300


def load_benchmark_close() -> pd.Series:
    """510300 close series (bare-code file preferred, prefix twin fallback)."""
    daily = PATHS.daily_dir
    for name in (f"{HS300_PROXY}.csv", f"sh{HS300_PROXY}.csv"):
        path = os.path.join(daily, name)
        if os.path.exists(path):
            df = pd.read_csv(path)
            s = pd.Series(df["close"].astype(float).values,
                          index=pd.to_datetime(df["date"]))
            return s.sort_index()
    raise FileNotFoundError(f"no {HS300_PROXY} daily file under {daily}")


def major_bear_state(close: pd.Series) -> dict:
    """R-配3 dual-condition regime state at the latest closed bar.

    Returns dict with: as_of, close, ma250, dd_from_250d_high (negative
    convention), below_ma250, dd_triggered, is_major_bear, position_cap,
    status ('ok' | 'insufficient_history').
    """
    if len(close) < MA_WINDOW:
        last = float(close.iloc[-1]) if len(close) else None
        as_of = str(close.index[-1].date()) if len(close) else None
        return {"status": "insufficient_history", "as_of": as_of,
                "close": last, "ma250": None, "dd_from_250d_high": None,
                "below_ma250": None, "dd_triggered": None,
                "is_major_bear": False, "position_cap": CAP_NORMAL,
                "note": f"<{MA_WINDOW} bars; unknown regime is NOT major "
                        "bear but no new-position signals should be "
                        "trusted without history"}
    ma = float(close.rolling(MA_WINDOW).mean().iloc[-1])
    high = float(close.rolling(MA_WINDOW).max().iloc[-1])
    last = float(close.iloc[-1])
    below = bool(last < ma)
    dd = (last / high - 1.0) if high > 0 else 0.0
    triggered = bool(dd <= DD_LINE)
    bear = bool(below and triggered)
    return {"status": "ok",
            "as_of": str(close.index[-1].date()),
            "close": last, "ma250": round(ma, 4),
            "dd_from_250d_high": round(dd, 4),
            "below_ma250": below, "dd_triggered": triggered,
            "is_major_bear": bear,
            "position_cap": CAP_MAJOR_BEAR if bear else CAP_NORMAL,
            "cash_floor": 0.80 if bear else 0.20}


def regime_report() -> dict:
    """Real-data regime report for paper/portfolio wiring."""
    st = major_bear_state(load_benchmark_close())
    st["rule"] = "R-配3 (O-20260923-1820): major bear = hs300 close < MA250 " \
                 "AND dd from 250d high >= 20% -> total position cap 20%"
    st["benchmark"] = f"{HS300_PROXY} ETF close (proxy)"
    return st


def _selftest() -> bool:
    ok = True
    idx = pd.bdate_range("2024-01-01", periods=260)

    # A: below MA250 AND dd >= 20% -> major bear, cap 20%
    a = pd.Series([100.0] * 250 + [78.0] * 10, index=idx)
    sa = major_bear_state(a)
    ok &= sa["is_major_bear"] and sa["position_cap"] == CAP_MAJOR_BEAR

    # B: below MA250 but dd only ~-10% -> NOT bear (current real shape)
    b = pd.Series([100.0] * 250 + [89.5] * 10, index=idx)
    sb = major_bear_state(b)
    ok &= (not sb["is_major_bear"]) and sb["below_ma250"] \
        and (not sb["dd_triggered"])

    # C: dd >= 20% from a short spike but close ABOVE MA250 -> NOT bear
    c = pd.Series([80.0] * 125 + [120.0] * 124 + [160.0, 120.0] + [120.0] * 9,
                   index=idx)
    sc = major_bear_state(c)
    ok &= (not sc["is_major_bear"]) and sc["dd_triggered"] \
        and (not sc["below_ma250"])

    # D: warmup < 250 bars -> honest insufficient_history, not bear
    sd = major_bear_state(pd.Series([100.0] * 100,
                                    index=pd.bdate_range("2024-01-01",
                                                         periods=100)))
    ok &= sd["status"] == "insufficient_history" and not sd["is_major_bear"]

    # E: dual condition releases when close recovers above MA250
    e = pd.Series([100.0] * 250 + [78.0] * 5 + [102.0] * 5, index=idx)
    se = major_bear_state(e)
    ok &= (not se["is_major_bear"]) and se["position_cap"] == CAP_NORMAL
    return bool(ok)


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if "--selftest" in argv:
        ok = _selftest()
        print(f"  [regime] synthetic edge cases... {'PASS' if ok else 'FAIL'}")
        rep = regime_report()
        print(f"  [regime] real data: {rep['as_of']} close={rep['close']} "
              f"ma250={rep['ma250']} dd={rep['dd_from_250d_high']} "
              f"below_ma250={rep['below_ma250']} "
              f"major_bear={rep['is_major_bear']}")
        return 0 if ok else 1
    rep = regime_report()
    print(json.dumps(rep, indent=2, ensure_ascii=False, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
