"""Anti-cheat audit (user order 2026-09-21: 务必建好机制防止有AI作弊).

"Cheating" for an evolving trading AI = earning money it could NOT earn in
real trading. Four mechanical detectors, all replayable:

  T1 成交重放审计  - re-derive every closed trade from the panel: entry/exit
                    price == day open x slippage, T+1 (exit>entry), no buy on
                    limit-up-open, no sell on limit-down-open, integer lots,
                    order size <= 5% of that day's turnover.
  T2 指标因果性    - recompute ma10/ma20/ma60/mom20/rh20/vol_ratio5 at random
                    (stock, day) from PAST bars only; must equal panel values.
  T3 复权真值      - panel price RATIO between two dates must equal Sina's
                    independently-fetched qfq ratio (ratio is invariant to
                    factor re-anchoring) - validates the TX x factor pipeline.
  T4 幸存者披露    - universe = currently listed stocks only; count delisted
                    A-shares and disclose the survivorship bias honestly.

Writes results/latest/anti_cheat.md. Exit code 0 only if T1-T3 all pass.
"""
import json
import random
import sys
import time

import numpy as np

import backtest as BT
import config as C
import data as D
import regime as RG
import strategies as S

OUT = C.RESULTS_DIR / "latest" / "anti_cheat.md"


def _t1_trade_replay(cache, report):
    """Simulate the LIVE genome over the last 120 days and re-verify every
    closed trade from raw panel data."""
    live_p = C.RESULTS_DIR / "live_genome.json"
    if not live_p.exists():
        report.append("- T1 SKIP: 无 live_genome")
        return True
    live = json.loads(live_p.read_text(encoding="utf-8"))
    gp = {"params": {f: dict(live["params"][f]) for f in S.FAMILIES},
          "w": np.asarray(live["w"]), "exposure": np.asarray(live["exposure"]),
          "K": live["K"], "stop": live["stop"], "trail": live["trail"],
          "hold": live["hold"]}
    T = int(len(cache["dates"]))
    reg = RG.compute(cache["bench_sse"], cache["breadth"])
    i1, j1 = T - 120, T
    fams = S.family_signals(D.window(cache, i1 - 1, j1 - 1), gp["params"])
    res = BT.simulate(D.window(cache, i1, j1), fams, gp, reg, i1)
    tr = res["trades"]
    o = np.asarray(cache["open"]); amt = np.asarray(cache["amount"])
    ban = np.asarray(cache["open_ban"]); bust = np.asarray(cache["open_bust"])
    bad = []
    for t in tr:
        i = int(t["i"]); ea = i1 + int(t["entry_day"]); xa = i1 + int(t["exit_day"])
        if int(t["exit_day"]) <= int(t["entry_day"]):
            bad.append(f"{t['fam']}#i{i}: T+1违规(同日进出)")
            continue
        if ban[ea, i]:
            bad.append(f"i{i}@d{ea}: 涨跌停开盘日买入")
        if bust[xa, i]:
            bad.append(f"i{i}@d{xa}: 跌停开盘日卖出")
        px_out = float(o[xa, i]) * (1 - C.SLIPPAGE)
        if not np.isfinite(px_out) or px_out <= 0:
            bad.append(f"i{i}: 开盘价无效")
            continue
        shares = float(t["gross"]) / px_out
        if abs(shares - round(shares)) > 0.01 or round(shares) % C.LOT:
            bad.append(f"i{i}: 非整手 {shares:.2f}")
            continue
        px_in = float(o[ea, i]) * (1 + C.SLIPPAGE)
        cost_expect = round(shares) * px_in
        fee_expect = max(C.COMMISSION * cost_expect, C.MIN_COMMISSION)
        if abs(float(t["cost"]) - (cost_expect + fee_expect)) > 0.02 * max(1.0, cost_expect):
            bad.append(f"i{i}: 入账成本≠开盘×滑点+费用")
        if not np.isfinite(amt[ea, i]) or float(t["cost"]) > C.AMOUNT_PART_CAP * float(amt[ea, i]) + 1.0:
            bad.append(f"i{i}: 超当日成交额5%容量")
    report.append(f"- T1 成交重放: {len(tr)}笔闭合交易全部对照面板重放，"
                  f"违规 {len(bad)} 项" + (f"：{bad[:3]}" if bad else " ✓"))
    return not bad


def _t2_indicator_causality(cache, report, n=40, seed=7):
    """Recompute indicators at random points from past bars only."""
    rng = random.Random(seed)
    close = np.asarray(cache["close"]); ma10 = np.asarray(cache["ma10"])
    ma20 = np.asarray(cache["ma20"]); ma60 = np.asarray(cache["ma60"])
    mom20 = np.asarray(cache["mom20"]); rh20 = np.asarray(cache["roll_high20"])
    T, N = close.shape
    checked = bad = 0
    for _ in range(n):
        t = rng.randint(80, T - 2); i = rng.randrange(N)
        w = close[max(0, t - 80):t + 1, i]
        if not np.isfinite(w).all() or len(w) < 61:
            continue
        pairs = [(ma10, float(np.nanmean(w[-10:]))),
                 (ma20, float(np.nanmean(w[-20:]))),
                 (ma60, float(np.nanmean(w[-60:]))),  # rolling(60): rows t-59..t
                 (mom20, float(w[-1] / w[-21] - 1)),
                 (rh20, float(w[-20:].max()))]
        for arr, expect in pairs:
            got = float(arr[t, i])
            if not np.isfinite(got) or not np.isfinite(expect) or expect == 0:
                continue
            checked += 1
            if abs(got - expect) > max(1e-3, abs(expect) * 1e-3):
                bad += 1
                if bad <= 3:
                    report.append(f"  偏差点: t={t} i={i} got={got:.4f} expect={expect:.4f}")
    report.append(f"- T2 指标因果性: {checked}个(股,日)对照点用过去bar重算，"
                  f"偏差 {bad} 项" + (" ✓" if bad == 0 else " ✗"))
    return bad == 0 and checked >= n // 2


def _t3_adjustment_truth(cache, report):
    """Panel close ratio between two dates == Sina's independent qfq ratio."""
    import akshare as ak
    dates = [str(x) for x in np.asarray(cache["dates"])]
    close = np.asarray(cache["close"])
    ok = bad = 0
    for sym, col in (("sz000001", "close"), ("sh600519", "close")):
        code = sym[2:]
        try:
            df = ak.stock_zh_a_daily(symbol=sym, start_date="20260820",
                                     end_date="20260918", adjust="qfq")
        except Exception as e:  # noqa: BLE001
            report.append(f"  {sym}: 新浪拉取失败 {type(e).__name__}（网络层，非作弊信号）")
            continue
        sdf = df.set_index(df["date"].astype(str).str.slice(0, 10))[col]
        codes = [str(x) for x in np.asarray(cache["codes"])]
        if code not in codes:
            continue
        ci = codes.index(code)
        pairs = [("2026-08-24", "2026-09-18"), ("2026-08-31", "2026-09-17"),
                 ("2026-09-07", "2026-09-16")]
        for d1, d2 in pairs:
            if d1 not in dates or d2 not in dates or d1 not in sdf.index or d2 not in sdf.index:
                continue
            panel_r = float(close[dates.index(d2), ci] / close[dates.index(d1), ci])
            sina_r = float(sdf[d2] / sdf[d1])
            checked = abs(panel_r - sina_r) <= 1e-3
            ok += checked
            bad += (not checked)
            if not checked:
                report.append(f"  {sym} {d1}->{d2}: panel比 {panel_r:.5f} vs 新浪 {sina_r:.5f}")
    report.append(f"- T3 复权真值: {ok + bad}组两日价格比 vs 新浪独立qfq，"
                  f"不符 {bad} 组" + (" ✓" if bad == 0 else " ✗"))
    return bad == 0 and ok >= 2


def _t4_survivorship(cache, report):
    """Universe = currently listed only; disclose the survivorship bias."""
    T, N = np.asarray(cache["close"]).shape
    dates = np.asarray(cache["dates"])
    per_year = {}
    close = np.asarray(cache["close"])
    for yr in (2005, 2010, 2015, 2020, 2025):
        try:
            k = next(idx for idx in range(T) if str(dates[idx]).startswith(str(yr)))
        except StopIteration:
            continue
        per_year[yr] = int(np.isfinite(close[k]).sum())
    delist_total = None
    try:
        import akshare as ak
        a = ak.stock_info_sh_delist()
        b = ak.stock_info_sz_delist(symbol="终止上市公司")
        delist_total = int(len(a) + len(b))
    except Exception:  # noqa: BLE001
        delist_total = None
    yrs = "，".join(f"{y}年面板内有效 {n} 只" for y, n in per_year.items())
    report.append(f"- T4 幸存者偏差(披露): 面板宇宙=当前上市 {N} 只，"
                  f"已退市股不在面板内（{yrs}）。"
                  f"{'akshare退市名录共 ' + str(delist_total) + ' 只未纳入——历史回测收益系统性偏乐观，实盘须打折看待' if delist_total else '退市名录拉取失败，按未纳入口径披露'}")
    return True  # disclosure-only, never blocks


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    t0 = time.time()
    cache = D.load_cache(mmap=True)  # views only: the machine runs WF workers
    report = ["# 反作弊审计（anti_cheat.py）\n",
              f"生成: {time.strftime('%Y-%m-%d %H:%M')} | 面板 "
              f"{np.asarray(cache['close']).shape[0]}日 × "
              f"{np.asarray(cache['close']).shape[1]}股\n"]
    p1 = _t1_trade_replay(cache, report)
    p2 = _t2_indicator_causality(cache, report)
    p3 = _t3_adjustment_truth(cache, report)
    p4 = _t4_survivorship(cache, report)
    report.append("\n## 执行模型声明")
    report.append("- 信号=日T收盘生成 → T+1开盘执行（2026-09-21修复：此前引擎为T+2，"
                  "首日不可买；修复前历史档案按T+2口径，偏保守无泄露）")
    report.append("- 卖出信号=日T收盘生成→T+1开盘执行；跌停开盘顺延；T+1结构性满足")
    report.append("- 涨跌停开盘禁买卖；订单≤当日成交额5%；整手；佣金+印花税+0.1%滑点")
    report.append("- 席位资格赛: 挑战者须在随机窗上也胜过现役才可夺权（防最新窗专才）")
    report.append("- 指标仅用过去数据（T2机检）；复权时点无未来因子（T3对新浪独立源）")
    verdict = "🟢 PASS" if (p1 and p2 and p3) else "🔴 FAIL"
    report.append(f"\n**总判定: {verdict}** (T1成交重放={'P' if p1 else 'F'} "
                  f"T2指标因果={'P' if p2 else 'F'} T3复权真值={'P' if p3 else 'F'} "
                  f"T4幸存者=已披露) {time.time() - t0:.0f}s")
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text("\n".join(report), encoding="utf-8")
    print("\n".join(report))
    return 0 if (p1 and p2 and p3) else 1


if __name__ == "__main__":
    sys.exit(main())
