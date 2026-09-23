"""Reporting: OOS stitched performance, equity chart, yearly/fold tables,
regime view, and next-day signal files (self-contained for paper execution)."""
import json
import datetime as dt

import numpy as np
import pandas as pd

import config as C
import backtest as BT
import regime as RG

FAM_CN = {"breakout": "放量突破", "limitup": "首板接力", "meanrev": "超跌反弹",
          "pullback": "趋势回调", "smallmom": "小盘动量", "relstr": "RPS相对强度",
          "nrev": "N字反包", "volburst": "量价起爆",
          "vcp": "平台缩量突破", "gapup": "缺口跳空", "streak": "连阳动量",
          "newhigh250": "年线新高", "macd": "MACD水上金叉", "lowvol": "低波动量",
          "turnspike": "换手异动", "bollrev": "布林反转", "crashst": "急跌企稳",
          "diplimit": "开板反包",
          "kdjgold": "随机低位金叉", "ccirev": "CCI超卖回升", "wrrev": "威廉超卖",
          "mfidip": "资金流超卖", "atrbreak": "波动扩张突破", "adxstrong": "强趋势延续",
          "momspeed": "动量加速", "lotterylow": "低彩票稳态动量", "illiq": "非流动异象",
          "intraday": "日内强隔夜弱", "engulf": "阳包阴形态", "confluence": "多流派共振",
          "lhb": "龙虎榜聪明钱"}
REG_CN = {0: "多头", 1: "震荡", 2: "急跌", 3: "修复"}


def signals_path():
    return C.RESULTS_DIR / "signals.json"


def paper_path():
    return C.RESULTS_DIR / "paper.json"


def stitch(records, key="eq", drop_head=True):
    segs, scale = [], 1.0
    for k, r in enumerate(records):
        eq = np.asarray(r[key], dtype=np.float64)
        rel = eq / eq[0]
        seg = rel * scale
        segs.append(seg if (k == 0 or not drop_head) else seg[1:])
        scale *= rel[-1]
    return np.concatenate(segs) if segs else np.array([1.0])


def stitch_dates(records, drop_head=True):
    ds = []
    for k, r in enumerate(records):
        d = list(r["test_dates"])
        ds.extend(d if (k == 0 or not drop_head) else d[1:])
    return pd.to_datetime(ds)


def stitch_abs(records, key, drop_head=True):
    """Absolute (non-compounding) concatenation, e.g. daily invested value."""
    segs = []
    for k, r in enumerate(records):
        seg = np.asarray(r[key], dtype=np.float64)
        segs.append(seg if (k == 0 or not drop_head) else seg[1:])
    return np.concatenate(segs) if segs else np.array([0.0])


def bench_curve(cache, records, key, drop_head=True):
    """Stitch a benchmark over the same fold windows, scaled to 1.0 at start.
    Folds before the index was published (hs300: 2005, csi500: 2007) fall
    back to the SSE composite - a REAL benchmark for the whole 34y span,
    never a silently-shorter array (that crashed the 34y report 2026-09-21)."""
    b = np.asarray(cache[key], dtype=np.float64)
    sse = np.asarray(cache["bench_sse"], dtype=np.float64)
    segs, scale = [], 1.0
    for k, r in enumerate(records):
        i1, j1 = r["test"]
        rel = b[i1:j1]
        if len(rel) == 0 or not np.isfinite(rel[0]) or rel[0] <= 0:
            rel = sse[i1:j1]  # pre-publication folds: SSE composite fallback
        if len(rel) == 0 or not np.isfinite(rel[0]) or rel[0] <= 0:
            continue
        seg = rel / rel[0] * scale
        segs.append(seg if (k == 0 or not drop_head) else seg[1:])
        scale *= rel[-1] / rel[0]
    return np.concatenate(segs) if segs else np.array([1.0])


def yearly_returns(dates, vals):
    df = pd.DataFrame({"d": pd.to_datetime(dates), "v": np.asarray(vals, float)})
    df["y"] = df["d"].dt.year
    out = {}
    prev = df["v"].iloc[0]
    rows = df.groupby("y", sort=True)
    last_v = prev
    for y, g in rows:
        base = last_v if g["d"].iloc[0] > df["d"].iloc[0] else g["v"].iloc[0]
        out[int(y)] = float(g["v"].iloc[-1] / base - 1.0)
        last_v = float(g["v"].iloc[-1])
    return out


def make_report(res):
    records, live, cache, reg = res["records"], res["live"], res["cache"], res["regime"]
    out_dir = res["out_dir"]
    eq = stitch(records) * C.CAPITAL
    dates = stitch_dates(records)
    inv = stitch_abs(records, "invested")
    trades = [t for r in records for t in r["trades"]]
    buy_cost = float(sum(t["cost"] for t in trades))
    m = BT.metrics(eq, inv, trades, buy_cost, len(eq))
    b300 = bench_curve(cache, records, "bench_hs300")
    b500 = bench_curve(cache, records, "bench_csi500")

    def curve_m(v):
        v = np.asarray(v, float)
        ret = v[1:] / v[:-1] - 1
        peak = np.maximum.accumulate(v)
        dd = (v / peak - 1).min()
        return {"total": v[-1] / v[0] - 1,
                "cagr": (v[-1] / v[0]) ** (252 / max(len(v) - 1, 1)) - 1,
                "sharpe": float(ret.mean() / (ret.std() + 1e-12) * np.sqrt(252)),
                "maxdd": float(dd)}

    m3, m5 = curve_m(b300), curve_m(b500)
    yr_p = yearly_returns(dates, eq)
    yr3 = yearly_returns(dates, b300)
    yr5 = yearly_returns(dates, b500)

    # chart
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "sans-serif"]
    plt.rcParams["axes.unicode_minus"] = False
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(dates, eq, label="策略组合(样本外)", lw=1.6, color="#d62728")
    ax.plot(dates, b300 * C.CAPITAL, label="沪深300", lw=1.0, color="#7f7f7f")
    ax.plot(dates, b500 * C.CAPITAL, label="中证500", lw=1.0, color="#1f77b4", alpha=0.7)
    ax.set_title(f"A股短线系统·滚动样本外验证（{C.CAPITAL / 1e4:.0f}万虚拟本金）")
    ax.legend(); ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_dir / "equity.png", dpi=110)
    plt.close(fig)

    w = np.asarray(live["w"]); expo = np.asarray(live["exposure"])
    fam_cols = list(FAM_CN[f] for f in ["breakout", "limitup", "meanrev",
                    "pullback", "smallmom", "relstr", "nrev", "volburst"])
    last_reg = int(reg[-1])
    lines = []
    lines.append(f"# A股短线系统·样本外验证报告（{C.CAPITAL / 1e4:.0f}万虚拟本金）\n")
    lines.append(f"- 生成: {dt.datetime.now().strftime('%Y-%m-%d %H:%M')} ｜ "
                 f"样本外区间: {dates[0].date()} ~ {dates[-1].date()}（{len(records)}折滚动，"
                 f"每折训练{C.TRAIN_DAYS}日→盲测{C.TEST_DAYS}日）\n")
    lines.append("- 基准注：沪深300(始于2005)/中证500(始于2007)发布前的折叠段以上证综指接续"
                 "（真实基准，非空段拼接）\n")
    lines.append("## 核心指标（样本外拼接，全部含手续费/印花税/滑点/涨跌停约束/T+1）\n")
    lines.append("| 指标 | 策略组合 | 沪深300 | 中证500 |")
    lines.append("|---|---|---|---|")
    lines.append(f"| 总收益 | {m['total'] * 100:.1f}% | {m3['total'] * 100:.1f}% | {m5['total'] * 100:.1f}% |")
    lines.append(f"| 年化收益 | {m['cagr'] * 100:.1f}% | {m3['cagr'] * 100:.1f}% | {m5['cagr'] * 100:.1f}% |")
    lines.append(f"| 夏普比率 | {m['sharpe']:.2f} | {m3['sharpe']:.2f} | {m5['sharpe']:.2f} |")
    lines.append(f"| 最大回撤 | {m['maxdd'] * 100:.1f}% | {m3['maxdd'] * 100:.1f}% | {m5['maxdd'] * 100:.1f}% |")
    lines.append(f"| Calmar | {m['calmar']:.2f} | - | - |")
    lines.append(f"| 交易次数 / 胜率 | {m['n_trades']} / {m['win_rate'] * 100:.1f}% | - | - |")
    lines.append(f"| 平均持仓(日) / 年换手 | {m['avg_hold']:.1f} / {m['turnover_ann']:.1f}倍 | - | - |")
    lines.append(f"| 平均仓位暴露 | {m['exposure'] * 100:.0f}% | - | - |\n")
    lines.append("## 分年表现（样本外）\n")
    lines.append("| 年份 | 组合 | 沪深300 | 中证500 |")
    lines.append("|---|---|---|---|")
    for y in sorted(set(list(yr_p) + list(yr3) + list(yr5))):
        lines.append(f"| {y} | {yr_p.get(y, 0) * 100:6.1f}% | {yr3.get(y, 0) * 100:6.1f}% | {yr5.get(y, 0) * 100:6.1f}% |")
    lines.append("\n## 逐折明细（每折=完全未见过的60个交易日）\n")
    lines.append("| 折 | 区间 | 收益 | 回撤 | 交易 |")
    lines.append("|---|---|---|---|---|")
    for r in records:
        mm = r["metrics"]
        lines.append(f"| {r['fold']} | {r['start']}~{r['end']} | {mm['total'] * 100:6.2f}% "
                     f"| {mm['maxdd'] * 100:6.2f}% | {mm['n_trades']} |")
    lines.append("\n## 风格自适应状态（当前）\n")
    lines.append(f"- 当前市场状态: **{REG_CN[last_reg]}** ｜ 各状态目标仓位: " +
                 " / ".join(f"{REG_CN[i]}={expo[i] * 100:.0f}%" for i in range(4)) + "\n")
    lines.append("| 状态 | " + " | ".join(fam_cols) + " |")
    lines.append("|---|" + "---|" * len(fam_cols))
    for i in range(4):
        lines.append(f"| {REG_CN[i]} | " + " | ".join(f"{w[i, j] * 100:.0f}%" for j in range(len(w[i]))) + " |")
    lines.append("\n## 诚实声明（已知局限）\n")
    lines.append("- 股票池=当前在市名单（免费数据源无退市股历史），存在幸存者偏差；ST历史状态用当前名单近似\n"
                 "- 前复权价格口径；现金分红不单独入账\n"
                 "- 滑点固定0.1%；单票下单≤当日成交额5%；日线粒度（收盘出信号→次日开盘成交）\n"
                 "- 每折基因组只在其训练窗口内进化，盲测段零参数调整——以上业绩为真实样本外\n")
    report_md = "\n".join(lines)
    (out_dir / "report.md").write_text(report_md, encoding="utf-8")
    latest = C.RESULTS_DIR / "latest"
    latest.mkdir(exist_ok=True)
    (latest / "report.md").write_text(report_md, encoding="utf-8")
    import shutil
    shutil.copyfile(out_dir / "equity.png", latest / "equity.png")
    with open(out_dir / "oos_metrics.json", "w", encoding="utf-8") as f:
        json.dump({"portfolio": m, "hs300": m3, "csi500": m5,
                   "yearly": {"port": yr_p, "hs300": yr3, "csi500": yr5},
                   "live": live}, f, ensure_ascii=False, indent=2)
    return m


def write_signals(cache, live, reg, out_dir):
    """Generate next-trading-day order list from the live genome (signal = last bar)."""
    import strategies as S
    import data as D
    T = int(len(cache["dates"]))
    sig_day = T - 1
    fams = S.family_signals(D.window(cache, sig_day, T), live["params"])
    r = int(reg[sig_day])
    fam_names = sorted(fams.keys())
    w = np.asarray(live["w"])[r]
    masks = np.stack([np.asarray(fams[f][0])[0] for f in fam_names])  # [F, N] last day
    scores = np.stack([np.asarray(fams[f][1])[0] for f in fam_names])
    cand = masks.any(axis=0)
    blended = (scores * w[:, None]).sum(axis=0)
    idx = np.where(cand)[0]
    order = idx[np.argsort(-blended[idx])][:30]
    codes = cache["codes"]; names = cache["names"]
    buys = []
    for i in order:
        fam_row = masks[:, i]
        ws = np.where(fam_row, w * scores[:, i], -1.0)
        fidx = int(np.argmax(ws))
        buys.append({"code": str(codes[i]), "name": str(names[i]),
                     "fam": fam_names[fidx], "fam_cn": FAM_CN[fam_names[fidx]],
                     "score": round(float(blended[i]), 4)})
    sig = {
        "signal_date": str(np.asarray(cache["dates"])[sig_day]),
        "regime": REG_CN[r],
        "K": int(live.get("K", 6)),
        "exposure": float(np.asarray(live["exposure"])[r]),
        "stop": live.get("stop"), "trail": live.get("trail"), "hold": live.get("hold"),
        "buys": buys,
    }
    with open(signals_path(), "w", encoding="utf-8") as f:
        json.dump(sig, f, ensure_ascii=False, indent=2)
    md = [f"# 次日交易信号（信号日 {sig['signal_date']}，市场状态：{sig['regime']}，目标仓位 {sig['exposure'] * 100:.0f}%）\n"]
    md.append("| 排名 | 代码 | 名称 | 策略 | 得分 |")
    md.append("|---|---|---|---|---|")
    for k, b in enumerate(buys[:20]):
        md.append(f"| {k + 1} | {b['code']} | {b['name']} | {b['fam_cn']} | {b['score']:.3f} |")
    (out_dir / "signals.md").write_text("\n".join(md), encoding="utf-8")
    (C.RESULTS_DIR / "latest" / "signals.md").write_text("\n".join(md), encoding="utf-8")
    return sig
