"""Census over the whole ETF universe: which styles survive a pooled, costed run?

Why this is not parameter fishing
---------------------------------
One rule x one window x one product group is a lottery ticket. A census runs the
whole grid on the same panel and reports how many combinations are powered, how
many keep the same sign, and what the median powered result is. One artefact
answers "is this space worth another cell", so the machine stops asking the same
question in different clothes.

Space (frozen): 3 rules x 2 rebalance frequencies on ~1,500 ETFs.
  ma_cross(50/200) · tsmom(250/21) · reversal(5)   x   rebalance 5 / 20 bars
  long-only (an ETF book cannot short), vol target 10%, cost 10bp/side,
  control = same-pool equal weight.
Criteria per combo: H1 full >= 4%, H2 OOS >= 3% and Sharpe >= 0.4, H3 both
halves positive, H4 drop-best >= 1.5%/yr, H5 control p < 0.05.
Pooled verdict:
  CENSUS_LEANS_POSITIVE   >= 50% of combos pass all five
  CENSUS_SIGN_MIXED       powered combos disagree on sign
  CENSUS_LEANS_NEGATIVE   powered combos are mostly negative
  CENSUS_UNPOWERED        no combo can resolve the target edge
"""
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bench_core as bc  # noqa: E402

OUT = os.path.join(bc.RESULTS, "bench_etf_census.json")
PAGE = os.path.join(bc.RESEARCH, "BENCH-ETF-CENSUS.md")
ETF_DIR = os.path.join(bc.DATA, "daily")
MIN_AMOUNT = 5_000_000.0
TARGET_VOL = 0.10
COST_BP = 10.0
SPLIT = "2024-01-01"
TARGET_EDGE = 5.0
MAX_NAMES = 300


def load_panel():
    files = [f for f in os.listdir(ETF_DIR) if f.endswith(".csv")]
    files.sort()
    closes, amounts = {}, {}
    for f in files:
        code = f[:-4]
        try:
            df = pd.read_csv(os.path.join(ETF_DIR, f), usecols=["date", "close", "amount"])
        except Exception:
            continue
        if len(df) < 600:
            continue
        df["date"] = pd.to_datetime(df["date"])
        df = df.drop_duplicates("date").set_index("date").sort_index()
        df = df[(df["close"] > 0) & df["close"].notna()]
        if len(df) < 600:
            continue
        closes[code] = df["close"]
        amounts[code] = df["amount"]
    close = pd.concat(closes, axis=1).sort_index()
    amount = pd.concat(amounts, axis=1).reindex(close.index)
    return close, amount


def signals(rule, close, params):
    if rule == "ma_cross":
        f, s = params["fast"], params["slow"]
        ma_f, ma_s = close.rolling(f).mean(), close.rolling(s).mean()
        sig = (ma_f > ma_s).astype(float).where(ma_s.notna())
    elif rule == "tsmom":
        lb, skip = params["lookback"], params["skip"]
        past = close.shift(lb + skip)
        sig = (close > past).astype(float).where(past.notna())
    elif rule == "reversal":
        w = params["window"]
        sig = (close < close.shift(w)).astype(float).where(close.shift(w).notna())
    else:
        raise ValueError(rule)
    return sig


def run_combo(rule, params, rebal, close, amount):
    rets = close.pct_change(fill_method=None)
    liq = amount.rolling(60, min_periods=20).median() >= MIN_AMOUNT
    sig = signals(rule, close, params) * liq.astype(float)
    sig = sig.where(sig > 0.5, np.nan)

    vol = rets.rolling(60, min_periods=30).std() * np.sqrt(bc.TRADING_DAYS)
    dates = close.index
    pos = pd.DataFrame(np.nan, index=dates, columns=close.columns)
    for i in range(len(dates)):
        if i % rebal:
            continue
        live = sig.iloc[i].dropna().index
        if len(live) == 0:
            pos.iloc[i] = np.nan
            continue
        live = live[:MAX_NAMES]
        v = vol.iloc[i][live].replace(0.0, np.nan)
        w = (TARGET_VOL / np.sqrt(len(live))) / v
        row = pd.Series(0.0, index=close.columns)
        row.loc[live] = w.values
        pos.iloc[i] = row.values
    pos = pos.ffill()
    gross = (pos.shift(1) * rets).sum(axis=1, min_count=1)
    turn = (pos - pos.shift(1)).abs().sum(axis=1).fillna(0.0)
    net = (gross - turn * COST_BP / 10000.0).fillna(0.0)
    net = net[net.index >= pd.Timestamp("2016-01-01")]
    if len(net) < 500:
        return None
    reading = bc.split_perf(net.values, net.index, split=SPLIT)
    mde = (1.96 * reading["full"]["vol_pct"] / (reading["full"]["n"] / bc.TRADING_DAYS) ** 0.5
           if reading["full"]["vol_pct"] and reading["full"]["n"] else None)
    ctrl = bc.random_sign_control(pos.loc[net.index], rets.reindex(net.index), draws=60)
    checks = {
        "H1": bool(reading["full"]["ann_pct"] is not None
                   and reading["full"]["ann_pct"] >= 4.0),
        "H2": bool(reading["oos"]["ann_pct"] is not None
                   and reading["oos"]["ann_pct"] >= 3.0
                   and (reading["oos"]["sharpe"] or -9) >= 0.4),
        "H3": bool((reading.get("first_half_ann_pct") or -9) > 0
                   and (reading.get("second_half_ann_pct") or -9) > 0),
        "H4": bool(reading["full"]["drop_best_year_ann_pct"] is not None
                   and reading["full"]["drop_best_year_ann_pct"] >= 1.5),
        "H5": bool(ctrl["p_value"] is not None and ctrl["p_value"] < 0.05),
    }
    return {
        "combo": f"{rule}|{params}|rebal{rebal}",
        "ann_pct": reading["full"]["ann_pct"], "sharpe": reading["full"]["sharpe"],
        "mdd_pct": reading["full"]["mdd_pct"], "oos_ann_pct": reading["oos"]["ann_pct"],
        "turnover": round(float(turn.sum()) * bc.TRADING_DAYS / max(len(turn), 1), 1),
        "mde_pp": None if mde is None else round(mde, 2),
        "powered": None if mde is None else bool(mde <= TARGET_EDGE),
        "verdict": bc.verdict_of(checks), "checks": checks,
        "control_p": ctrl["p_value"],
    }


def run():
    bc.weight_priority()
    close, amount = load_panel()
    grid = []
    for rebal in (5, 20):
        grid.append(("ma_cross", {"fast": 50, "slow": 200}, rebal))
        grid.append(("tsmom", {"lookback": 250, "skip": 21}, rebal))
        grid.append(("reversal", {"window": 5}, rebal))
    rows = []
    for rule, params, rebal in grid:
        r = run_combo(rule, params, rebal, close, amount)
        if r:
            rows.append(r)
    powered = [r for r in rows if r["powered"]]
    pos = [r for r in powered if (r["ann_pct"] or 0) > 0]
    neg = [r for r in powered if (r["ann_pct"] or 0) < 0]
    go = [r for r in rows if r["verdict"] == "GO"]
    if not powered:
        verdict = "CENSUS_UNPOWERED"
    elif len(pos) and len(neg):
        verdict = "CENSUS_SIGN_MIXED"
    elif len(go) >= max(1, len(rows) // 2):
        verdict = "CENSUS_LEANS_POSITIVE"
    elif pos:
        verdict = "CENSUS_LEANS_POSITIVE"
    else:
        verdict = "CENSUS_LEANS_NEGATIVE"
    payload = {
        "cell": "etf_census",
        "generated": pd.Timestamp.now(tz="Asia/Shanghai").isoformat(timespec="seconds"),
        "evidence_cutoff": str(close.index[-1].date()),
        "universe": {"etfs": int(close.shape[1]), "bars": int(close.shape[0]),
                     "start": str(close.index[0].date()), "end": str(close.index[-1].date())},
        "criteria": {"cost_bp_side": COST_BP, "target_vol": TARGET_VOL,
                     "split": SPLIT, "target_edge_pp": TARGET_EDGE,
                     "min_amount": MIN_AMOUNT, "max_names": MAX_NAMES},
        "combos": rows, "n_combos": len(rows), "n_powered": len(powered),
        "n_positive_powered": len(pos), "n_negative_powered": len(neg),
        "verdict": verdict,
        "reading": ("整片地形：功效够的组合里正负分布如上；GO 数 = " + str(len(go))),
    }
    bc.write_json(OUT, payload)
    lines = ["# ETF 全池风格普查", "",
             f"generated {payload['generated']} | 标的 {payload['universe']['etfs']} 只 · "
             f"bar {payload['universe']['bars']} | **{verdict}**", "",
             "| 组合 | 年化 | 夏普 | 回撤 | 样本外 | 换手 | MDE | 可分辨 | 判决 | 对照p |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['combo']} | {bc.fmt_pct(r['ann_pct'])} | {bc.fmt_num(r['sharpe'])} | "
                     f"{bc.fmt_pct(r['mdd_pct'])} | {bc.fmt_pct(r['oos_ann_pct'])} | "
                     f"{r['turnover']} | {r['mde_pp']} | {r['powered']} | **{r['verdict']}** | "
                     f"{r['control_p']} |")
    lines += ["", "## 读数", "",
              f"- 组合 {len(rows)} 个，功效够 {len(powered)} 个：正 {len(pos)} / 负 {len(neg)}，"
              f"GO {len(go)} 个。",
              "- 一个组合判 GO 只代表它自己；整片地形要不要再投入看上面的正负分布。"]
    with open(PAGE, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    print(json.dumps({"ok": True, "verdict": verdict, "combos": len(rows),
                      "powered": len(powered), "go": len(go),
                      "etfs": payload["universe"]["etfs"]}, ensure_ascii=False, indent=1))
    return payload


if __name__ == "__main__":
    res = run()
    sys.exit(0 if isinstance(res, dict) and res.get("ok", True) else 1)
