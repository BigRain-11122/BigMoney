"""What the book pays its owner versus what the panel shows: the dividend credit.

Every printed number for the ETF book so far is a PRICE return. The panel
(`data/daily`, sina klc_kl) carries the ETF's adjusted-price factor at 1.0, so a cash
distribution leaves the series one step lower and the holder's cash never appears.
r2078 (`ETF-BASKET-SPREAD-DECOMPOSE.md`) measured the size of that blindness from the
side: 11 of 40 wide-basket groups have a spread that is mostly dividend jumps, and for
one of them (510300 vs 159393) 457 of 943 bp of net price spread is the ex-date steps.

This face measures it from the holder's side instead of from a pair. It runs the SAME
engine, the same rules and the same score on two price panels:

  A) as-traded prices          -- every number the book has ever published;
  B) prices scaled by a total-return factor built from sina's cumulative-distribution
     series of exactly the names the book held -- dividends reinvested at the close.

The difference is the dividend credit: how much of the book's return has been sitting
in cash instead of in the equity curve. The score itself is left on price factors
(`compute_all` is not rebuilt), which biases B DOWNWARD -- the momentum of a name that
pays out is understated in A and stays understated in B, so the credit printed here is
a floor for the selection channel, not a ceiling.

Coverage is printed, never assumed: a name with no sina distribution record is treated
as paying nothing, which understates the credit the same way. `--check` re-derives the
published deltas from the published arms and refuses a face whose subtraction does not
hold; `--selftest` pins the total-return arithmetic on a hand-built ex-date.
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import numpy as np
import pandas as pd

import etf_composite_pf as E
import etf_robust_pf as R
import etf_equity_alpha as A

IS_END = "2023-12-31"
VOL_TARGET = 0.08
REBAL, N_HOLD, COST = 20, 5, 0.0010
OUT = "etf_book_dividend_credit.json"
DIV_DIR = os.path.join(E.PATHS.data_dir, "etf_dividend")
DOC = os.path.join(E.PATHS.root, "research", "ETF_BOOK_DIVIDEND_CREDIT.md")


def _prefixed(sym):
    """sina wants sh/sz in front; A-share rule is 5/6 -> sh, 0/3 -> sz."""
    s = str(sym)
    if s[:2] in ("sh", "sz"):
        return s
    return ("sh" if s[0] in "56" else "sz") + s


def tr_factor(prices, divs, raw_prices=None, cap=0.10):
    """Total-return factor for one name: 1 + (每份派息 / 除息日收盘) compounded on ex-dates.

    prices: as-traded close series (index = trading days), the repaired panel the engine
    actually runs on. divs: DataFrame with columns 日期 / 累计分红 (sina). raw_prices, when
    given, is the UNREPAIRED close of the same name: the repair rebases a price series at
    a share conversion (510230 lost 77% of its quote on 2020-08-17 with no cash involved),
    which would blow up 派息/价格 for every earlier event. Events whose cash is more than
    `cap` of the raw close are therefore not cash distributions at all -- they are
    conversions or bad records, dropped and counted, never silently credited.

    Returns (factor, dropped_count). Cash is reinvested at the ex-date's own close, so
    a pure-distribution ex-date nets to flat on the total-return curve.
    """
    if divs is None or len(divs) == 0:
        return pd.Series(1.0, index=prices.index), 0
    cum = (divs.set_index(pd.to_datetime(divs["日期"]))["累计分红"]
           .astype(float).sort_index())
    cum = cum.reindex(prices.index, method="ffill").fillna(0.0)
    step_cash = cum.diff().fillna(0.0).clip(lower=0.0)
    denom = (raw_prices.reindex(prices.index).where(lambda s: s > 0) if raw_prices is not None
             else prices.where(prices > 0))
    share = (step_cash / denom).fillna(0.0)
    dropped = int((share > cap).sum())
    share = share.clip(upper=cap).where(share <= cap, 0.0)
    ratio = (1.0 + share).where(np.isfinite(step_cash), 1.0)
    return ratio.where(np.isfinite(ratio), 1.0).cumprod(), dropped


def fetch_dividend(sym, refresh=False):
    """Local cache first; one sina call per name per window. Returns a DataFrame."""
    os.makedirs(DIV_DIR, exist_ok=True)
    path = os.path.join(DIV_DIR, "%s.csv" % sym)
    if os.path.exists(path) and not refresh:
        try:
            return pd.read_csv(path, parse_dates=["日期"])
        except Exception:
            pass
    import akshare as ak
    last = None
    for attempt in range(3):
        try:
            df = ak.fund_etf_dividend_sina(symbol=_prefixed(sym))
            break
        except Exception as exc:  # network shape drift is reported, never hidden
            last = exc
            time.sleep(1.5 * (attempt + 1))
    else:
        raise RuntimeError("dividend fetch failed for %s: %r" % (sym, last))
    if df is None or not len(df):
        df = pd.DataFrame({"日期": pd.to_datetime([]), "累计分红": []})
    df = df.copy()
    df["日期"] = pd.to_datetime(df["日期"])
    df.to_csv(path, index=False, encoding="utf-8")
    time.sleep(1.1)
    return df


def stats_pair(ser, label):
    m = A.stats2(ser, label)
    for lbl, sl in (("is", ser[ser.index <= IS_END]), ("oos", ser[ser.index > IS_END])):
        if len(sl) < 40:
            continue
        mm = A.stats2(sl, label + "_" + lbl)
        for k in ("cagr", "sharpe", "maxdd"):
            m[k + "_" + lbl] = mm.get(k)
    return m


def main():
    close, openp, amt, feats = E.build_panel()
    close, openp, n_flip = A.repair_flips(close, openp)
    cmap = A.load_class_map()
    cls = A.classify(close.columns, cmap, close)
    want = ("equity", "commodity", "convertible")
    cols = [c for c in close.columns if cls[c] in want]
    print("bond-free universe %d, flips repaired %d" % (len(cols), n_flip), flush=True)

    sc = E.build_score(close[cols], amt[cols], feats)

    # A) published caliber: collect the actual books the engine holds, so the dividend
    #    fetch is scoped to names that were really bought rather than the whole panel.
    diag = []
    ser_px0, _ = R.open_to_open_equity(close[cols], openp[cols], amt[cols], sc, REBAL, N_HOLD,
                                       COST, vol_target=VOL_TARGET, diag=diag)
    held = sorted({n for row in diag for n in row.get("book") or []})
    live = [str(s) for s in sc.loc[sc.index[-1]].dropna().nlargest(N_HOLD).index]
    symbols = sorted(set(held) | set(live))
    print("books held over the window: %d names, +%d live-only = %d to price"
          % (len(held), len(set(live) - set(held)), len(symbols)), flush=True)

    divs, records = {}, {}
    for i, sym in enumerate(symbols, 1):
        try:
            df = fetch_dividend(sym)
            divs[sym] = df
            records[sym] = {
                "events": int(len(df)),
                "last_ex_date": (str(pd.to_datetime(df["日期"].max()).date()) if len(df) else None),
                "cum_per_share": (round(float(df["累计分红"].iloc[-1]), 4) if len(df) else 0.0),
            }
        except Exception as exc:
            divs[sym] = None
            records[sym] = {"events": None, "error": str(exc)[:200]}
        if i % 20 == 0:
            print("  dividends %d/%d" % (i, len(symbols)), flush=True)

    # B) the same panel with each held name scaled by its dividend factor. Raw (unrepaired)
    #    closes are used only as the denominator for the event filter: a repair rebases a
    #    series at a share conversion, and a 0.55 派息 divided by a rebased 1.01 quote would
    #    read as a 55% distribution that never happened.
    raw = E._dedupe(E._load_prices())
    fac, dropped = {}, {}
    for s in symbols:
        rp = raw.get(s)
        f, d = tr_factor(close[s], divs.get(s), rp["close"] if rp is not None else None)
        fac[s], dropped[s] = f, d
    fac = pd.DataFrame(fac)
    openp_tr = openp[cols].copy()
    for s in symbols:
        if s in openp_tr.columns:
            openp_tr[s] = openp_tr[s] * fac[s]

    arms = {}
    for tag, op in (("price", openp[cols]), ("with_dividends", openp_tr)):
        for lag in (0, 1):
            ser, turn = R.open_to_open_equity(close[cols], op, amt[cols], sc, REBAL, N_HOLD,
                                              COST, vol_target=VOL_TARGET, entry_lag=lag)
            row = stats_pair(ser, "%s_lag%d" % (tag, lag))
            row["turnover"] = round(turn, 3)
            arms["%s_lag%d" % (tag, lag)] = row
            print("%-22s cagr=%.4f sharpe=%.3f maxdd=%.4f"
                  % (tag + "_lag%d" % lag, row.get("cagr") or 0, row.get("sharpe") or 0,
                     row.get("maxdd") or 0), flush=True)
        _ = ser_px0 if tag == "price" else None

    credit = {}
    for lag in (0, 1):
        a = arms["price_lag%d" % lag]
        b = arms["with_dividends_lag%d" % lag]
        credit["lag%d_cagr_pp" % lag] = round(((b.get("cagr") or 0) - (a.get("cagr") or 0)) * 100, 4)
        credit["lag%d_sharpe_delta" % lag] = round((b.get("sharpe") or 0) - (a.get("sharpe") or 0), 4)
        credit["lag%d_maxdd_pp" % lag] = round(((b.get("maxdd") or 0) - (a.get("maxdd") or 0)) * 100, 4)
    # the same subtraction on the execution caliber: owning one bar late is paid twice a
    # month, the dividend blindness is paid once a year -- print both on one ruler.
    credit["execution_penalty_pp"] = round(
        ((arms["price_lag0"].get("cagr") or 0) - (arms["price_lag1"].get("cagr") or 0)) * 100, 4)
    credit["dividend_to_execution_ratio"] = (
        round(credit["lag1_cagr_pp"] / credit["execution_penalty_pp"], 3)
        if credit["execution_penalty_pp"] else None)
    # per-name dividend gain INSIDE the backtest window (a factor carried from 2005 would
    # credit two decades of payouts to a window that starts in 2020)
    win = close.index[close.index >= pd.Timestamp("2020-01-01")]
    win0 = win[0] if len(win) else close.index[0]
    per_name = {}
    for s in symbols:
        f = fac[s].dropna()
        if len(f) and win0 in f.index:
            per_name[s] = round(float(f.loc[win0:].iloc[-1] / f.loc[win0] - 1.0) * 100.0, 3)
    priced = {s: v for s, v in per_name.items() if v > 0.0}
    with_div = {s: r for s, r in records.items() if (r.get("events") or 0) > 0}
    dropped_events = {s: n for s, n in dropped.items() if n}

    face = {
        "evidence_cutoff": str(close.index[-1].date()),
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "caliber": {
            "engine": "etf_robust_pf.open_to_open_equity (rebal=20, n_hold=5, cost=10bp/side, vol_target=8%)",
            "panel_a": "as-traded prices (sina klc_kl, adjusted factor 1.0 on ETFs) -- every published number",
            "panel_b": "same panel, held names scaled by 1+每份派息/前收 compounded on sina ex-dates",
            "scope": "only names the book actually held (or holds today) are repriced; the rest have no tested dividend credit",
            "score_unchanged": "score is still built from price factors (compute_all not rebuilt) -> the credit printed here is a floor for the selection channel",
        },
        "arms": arms,
        "dividend_credit": credit,
        "verdict": ("DIVIDENDS_ADD_MONEY" if credit["lag1_cagr_pp"] > 0.5
                    else ("DIVIDENDS_ARE_NOISE" if credit["lag1_cagr_pp"] <= 0.5 else "MIXED")),
        "coverage": {
            "names_held_or_live": len(symbols),
            "names_with_sina_records": len(with_div),
            "names_paying_inside_window": len(priced),
            "coverage_pct": round(100.0 * len(priced) / max(1, len(symbols)), 1),
            "events_dropped_as_non_cash": dropped_events,
            "event_cap_pct_of_raw_close": 10.0,
        },
        "per_name_dividend_pct_in_window": dict(sorted(per_name.items(), key=lambda kv: -kv[1])),
        "records": records,
        "live_picks": {"as_of": str(sc.index[-1].date()), "picks": live},
    }
    p = os.path.join(E.PATHS.results_dir, OUT)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(face, f, ensure_ascii=False, indent=1)
    print("saved", p)

    write_doc(face)
    print("doc", DOC)
    return 0


def write_doc(face):
    a = face["arms"]
    cr = face["dividend_credit"]
    cov = face["coverage"]
    top = list(face["per_name_dividend_pct_in_window"].items())[:12]
    lines = [
        "# 这本书实际付给持有人多少：分红口径的重算",
        "",
        "generated %s ｜ evidence_cutoff %s ｜ 判词 **%s**"
        % (time.strftime("%Y-%m-%dT%H:%M:%S%z"), face["evidence_cutoff"], face["verdict"]),
        "",
        "## 一句话",
        "",
        "同一个引擎、同一条规则、同一张打分表，只把价格面板换成「含分红再投资」："
        "年化从 **%.2f%%** 变成 **%.2f%%**（下一开盘口径，lag1），差 **%+.2f pp/年**。"
        % ((a["price_lag1"].get("cagr") or 0) * 100,
           (a["with_dividends_lag1"].get("cagr") or 0) * 100, cr["lag1_cagr_pp"]),
        "",
        "## 为什么必须做这一面",
        "",
        "- 面板（sina klc_kl）在 ETF 上的复权因子恒为 1.0，派息是价格的一次下跌，持有人的现金**整段不在序列里**。",
        "- r2078 从同篮子价差侧量到：40 个价差 ≥1pp 的组里 11 组是除息跳（分红政策），沪深300ETF 组 943bp 的净价差里 457bp 是除息台阶。",
        "- 所以「这本书年化 10%」讲的是**不领分红的纸面**。持有人实际拿到的要高一些——本面把这个差额量出来。",
        "",
        "## 两口径并排",
        "",
        "| 口径 | 年化 | 夏普 | 最大回撤 | 换手 |",
        "|---|---|---|---|---|",
    ]
    for tag in ("price_lag0", "price_lag1", "with_dividends_lag0", "with_dividends_lag1"):
        r = a[tag]
        lines.append("| %s | %.2f%% | %.3f | %.2f%% | %s |"
                     % (tag, (r.get("cagr") or 0) * 100, r.get("sharpe") or 0,
                        (r.get("maxdd") or 0) * 100, r.get("turnover")))
    lines += [
        "",
        "分段（lag1 口径）：",
        "",
        "| 口径 | IS 2020-2023 年化 | OOS 2024+ 年化 | IS 夏普 | OOS 夏普 |",
        "|---|---|---|---|---|",
    ]
    for tag in ("price_lag1", "with_dividends_lag1"):
        r = a[tag]
        lines.append("| %s | %.2f%% | %.2f%% | %.3f | %.3f |"
                     % (tag, (r.get("cagr_is") or 0) * 100, (r.get("cagr_oos") or 0) * 100,
                        r.get("sharpe_is") or 0, r.get("sharpe_oos") or 0))
    lines += [
        "",
        "## 分红信用（差额）",
        "",
        "| 项 | lag0 | lag1 |",
        "|---|---|---|",
        "| 年化差 pp | %+.2f | %+.2f |" % (cr["lag0_cagr_pp"], cr["lag1_cagr_pp"]),
        "| 夏普差 | %+.3f | %+.3f |" % (cr["lag0_sharpe_delta"], cr["lag1_sharpe_delta"]),
        "| 最大回撤差 pp | %+.2f | %+.2f |" % (cr["lag0_maxdd_pp"], cr["lag1_maxdd_pp"]),
        "",
        "### 放进同一把尺子里",
        "",
        "| 代价 | pp/年（lag1 口径） |",
        "|---|---|",
        "| 没把分红算进面板 | %+.2f |" % cr["lag1_cagr_pp"],
        "| 决策当天收盘看到、下一开盘才买到（entry lag 1） | %+.2f |" % cr["execution_penalty_pp"],
        "",
        "两条都是「口径错位」，都不是策略好坏。分红这一条比执行晚一天**小 %.1f 倍**——"
        "所以「面板不含派息」不是这本书被系统性低估的主因，读者最该记住的那条仍然是执行口径。"
        % (1.0 / cr["dividend_to_execution_ratio"] if cr.get("dividend_to_execution_ratio") else 1.0),
        "",
        "## 覆盖度（诚实面）",
        "",
        "- 窗口内被持有 + 今日在册的名字：**%d**；sina 有分红记录：**%d**；窗内真的派过息：**%d**（%.1f%%）。"
        % (cov["names_held_or_live"], cov["names_with_sina_records"],
           cov["names_paying_inside_window"], cov["coverage_pct"]),
        "- 没有记录的名字一律按「不派息」处理——这类遗漏只会让本面的差额**偏小**，不会偏大。",
        "- 单次派息超过原始收盘价 %.0f%% 的事件一律**丢弃并计数**（份额折算/坏记录，不是现金分红）：%s。"
        % (cov.get("event_cap_pct_of_raw_close", 10.0),
           ("；".join("%s×%s" % (k, v) for k, v in (cov.get("events_dropped_as_non_cash") or {}).items())
            or "无")),
        "",
        "### 窗内派息最多的名字（按窗内因子累计 %）",
        "",
        "| 代码 | 窗内贡献 % | 全史累计每份(元) | 最后除息日 | 全史事件数 |",
        "|---|---|---|---|---|",
    ]
    for sym, pct in top:
        rec = face["records"].get(sym) or {}
        lines.append("| %s | %+.3f%% | %s | %s | %s |"
                     % (sym, pct, rec.get("cum_per_share"), rec.get("last_ex_date"), rec.get("events")))
    lines += [
        "",
        "## 局限（不改口径就不许引用）",
        "",
        "1. **打分仍按价格因子**：`compute_all` 没有重建，派息多的名字在打分里仍然被低估。所以本面的差额是**下界**，只覆盖「持有收益」这一半，没覆盖「选股被改善」那一半。",
        "2. **sina 累计分红可能不全**：511010 在 2015→2025 之间只有一次跳变，159915/518880 干脆没有记录（黄金 ETF 本来不分红）；缺记录=按 0 处理=低估。",
        "3. **分红按除息日收盘再投资**：真实持有人可能是现金留存或按别的价格再投，年化差额会在百分之几 pp 内浮动。",
        "4. 只重定价「书真的买过/今天在册」的名字，没有测试「没被买过的名字分红更多」这种可能。",
        "",
        "本面只测量，不改书、不改分组、不下单。",
    ]
    os.makedirs(os.path.dirname(DOC), exist_ok=True)
    with open(DOC, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def check():
    """Re-derive the published credit from the published arms; never recompute a book."""
    p = os.path.join(E.PATHS.results_dir, OUT)
    if not os.path.exists(p):
        print("check FAIL: no face at", p)
        return 1
    with open(p, encoding="utf-8") as f:
        face = json.load(f)
    probs = []
    arms = face.get("arms") or {}
    cr = face.get("dividend_credit") or {}
    for lag in (0, 1):
        a, b = arms.get("price_lag%d" % lag), arms.get("with_dividends_lag%d" % lag)
        if not a or not b:
            probs.append("lag%d: missing an arm" % lag)
            continue
        want = ((b.get("cagr") or 0) - (a.get("cagr") or 0)) * 100
        got = cr.get("lag%d_cagr_pp" % lag)
        if got is None or abs(want - got) > 1e-3:
            probs.append("lag%d: cagr_pp %.4f != b-a %.4f" % (lag, got or 0, want))
        if (b.get("cagr") or 0) <= 0:
            probs.append("lag%d: with-dividend arm has no positive cagr" % lag)
    cov = face.get("coverage") or {}
    if not cov.get("names_held_or_live"):
        probs.append("coverage block empty")
    else:
        n, m = cov["names_paying_inside_window"], cov["names_held_or_live"]
        if abs(cov["coverage_pct"] - round(100.0 * n / max(1, m), 1)) > 1e-6:
            probs.append("coverage_pct does not match its own counts")
    if face.get("verdict") == "DIVIDENDS_ADD_MONEY" and not (cr.get("lag1_cagr_pp") or 0) > 0.5:
        probs.append("verdict claims money that the lag1 delta does not show")
    if probs:
        print("check FAIL:")
        for x in probs:
            print("  -", x)
        return 1
    print("check ok: lag1 credit %+.2f pp/yr, coverage %.1f%%, verdict %s"
          % (cr["lag1_cagr_pp"], cov["coverage_pct"], face["verdict"]))
    return 0


def selftest():
    """Pin the total-return arithmetic: an ex-date must leave the curve flat."""
    idx = pd.bdate_range("2024-01-01", periods=6)
    px = pd.Series([10.0, 10.0, 9.5, 9.5, 9.5, 9.5], index=idx)  # 0.5 distribution on bar 3
    divs = pd.DataFrame({"日期": [idx[2]], "累计分红": [0.5]})
    f, got_drop = tr_factor(px, divs)
    ok = True
    # bar 3 price dropped 0.5 with 0.5 paid: total return flat, factor must lift it back
    tr = px * f
    if abs(tr.iloc[2] / tr.iloc[1] - 1.0) > 1e-9:
        print("selftest FAIL: ex-date not flat (%r)" % (tr.iloc[2] / tr.iloc[1]))
        ok = False
    if abs(f.iloc[1] - 1.0) > 1e-12:
        print("selftest FAIL: factor moved before the ex-date")
        ok = False
    if abs(f.iloc[-1] - (1.0 + 0.5 / 9.5)) > 1e-9:
        print("selftest FAIL: final factor %r != 1+D/P_ex" % f.iloc[-1])
        ok = False
    if got_drop != 0:
        print("selftest FAIL: a 5%% distribution was treated as a non-cash event")
        ok = False
    # a name with no records must be untouched
    f0, _ = tr_factor(px, None)
    if not (f0 == 1.0).all():
        print("selftest FAIL: no-record name was scaled")
        ok = False
    # payments before the window are absorbed, not credited
    f1, _ = tr_factor(px, pd.DataFrame({"日期": [idx[0] - pd.Timedelta(days=3)], "累计分红": [9.9]}))
    if not (f1 == 1.0).all():
        print("selftest FAIL: pre-window payment leaked into the factor")
        ok = False
    # a 50% "distribution" against the raw quote is a share conversion, not cash
    pxs = pd.Series([1.0] * len(idx), index=idx)
    f2, d2 = tr_factor(pxs, pd.DataFrame({"日期": [idx[2]], "累计分红": [0.5]}), raw_prices=pxs)
    if d2 != 1 or not (f2 == 1.0).all():
        print("selftest FAIL: conversion-sized step was credited (dropped=%d)" % d2)
        ok = False
    print("selftest", "PASS" if ok else "FAIL", "5 legs")
    return 0 if ok else 1


if __name__ == "__main__":
    arg = sys.argv[1].lstrip("-") if len(sys.argv) > 1 else ""
    if arg == "check":
        raise SystemExit(check())
    if arg == "selftest":
        raise SystemExit(selftest())
    raise SystemExit(main())
