#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""可转债双低轮动线 -- 第二收益线（survivorship-free）

为什么单独一条线：ETF 复合书是跨资产动量，与转债的债性+期权性是两套驱动。
一个策略就是单点故障，所以第二条线必须先证明自己。

数据（东财 RPTA_WEB_KZZ_LS，一券一次请求）：
    DATE 收盘价 FCLOSE 转股价值 SWAPVALUE 纯债价值 PUREBONDVALUE
    转股溢价率 SWAPOR(%) 纯债溢价率 PUREBONDOR(%) 转股价 SWAPPRICE
含已退市/违约券（搜特 128100 末价 18.00、广汇 110072 末价 44.27 均可取到），
所以本线没有「只看得见活下来的基金」这个偏差。

口径（写死在代码里，改口径=改判据，必须单独说明）：
  * 信号在 t 收盘算，t+1 收盘成交 —— 1 根 bar 延迟，与 ETF 书的 next-open 同代口径
  * 持仓券从面板消失（强赎/退市/违约）= 按最后可得收盘价清仓，不允许「神奇逃脱」
  * 成本 10bp/边（转债免印花税），另跑 5/20/40bp 敏感性
  * 双低值 = 收盘价 + 转股溢价率（%），数值越低越便宜

用法：
    python scripts/cb_dual_low.py fetch          # 拉全历史，断点续跑
    python scripts/cb_dual_low.py build          # 拼面板
    python scripts/cb_dual_low.py run            # 回测 + 出报告
    python scripts/cb_dual_low.py run --quick    # 只跑主配置（出结论用）
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CB_DIR = os.path.join(ROOT, "data", "cb_daily")
LIST_PATH = os.path.join(ROOT, "data", "cb_bond_list.json")
PANEL_PATH = os.path.join(ROOT, "data", "cb_panel.csv.gz")
RESULT_JSON = os.path.join(ROOT, "results", "cb_dual_low.json")
RESULT_MD = os.path.join(ROOT, "results", "cb_dual_low.md")

EM_URL = "https://datacenter-web.eastmoney.com/api/data/get"
EM_TOKEN = "894050c76af8597a853f5b408b759f5d"
COLS = ["date", "code", "close", "conv_value", "pure_bond_value",
        "conv_premium", "pure_bond_premium", "swap_price", "name"]


# ---------------------------------------------------------------- fetch

def _em_get(code: str, retries: int = 4) -> list[dict]:
    # filter 里的引号必须原样发给东财：只走 requests 的 params 拼装，
    # urllib 的 urlencode 会把 `=` 转义成 %3D，服务端直接回 400。
    import requests
    params = {
        "sty": "ALL", "token": EM_TOKEN, "st": "date", "sr": "1", "source": "WEB",
        "type": "RPTA_WEB_KZZ_LS", "filter": f'(zcode="{code}")', "p": "1", "ps": "8000",
    }
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
               "Referer": "https://data.eastmoney.com/"}
    last = None
    for attempt in range(retries):
        try:
            r = requests.get(EM_URL, params=params, headers=headers, timeout=30)
            r.raise_for_status()
            j = r.json()
            res = j.get("result") or {}
            return res.get("data") or []
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(0.6 * (attempt + 1))
    raise RuntimeError(f"{code}: {type(last).__name__}: {last}")


def _bond_list() -> list[dict]:
    """转债清单：代码 + 上市时间 + 规模 + 评级。失败则退回从本地缓存。"""
    if os.path.exists(LIST_PATH):
        with open(LIST_PATH, "r", encoding="utf-8") as f:
            cached = json.load(f)
        if cached.get("bonds"):
            return cached["bonds"]
    import akshare as ak  # 只有拿清单时才需要，避免其余子命令依赖 akshare
    df = ak.bond_zh_cov()
    rename = {
        "债券代码": "code", "债券简称": "name", "上市时间": "list_date",
        "发行规模": "issue_size", "信用评级": "rating", "正股代码": "stock_code",
    }
    df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})
    bonds = []
    for _, row in df.iterrows():
        code = str(row.get("code") or "").strip()
        if not code or len(code) != 6:
            continue
        ld = row.get("list_date")
        bonds.append({
            "code": code,
            "name": str(row.get("name") or "").strip(),
            "list_date": None if ld is None or (hasattr(ld, "year") is False) else str(ld)[:10],
            "issue_size": _num(row.get("issue_size")),
            "rating": (str(row.get("rating")).strip() if row.get("rating") is not None else None),
            "stock_code": (str(row.get("stock_code")).strip() if row.get("stock_code") is not None else None),
        })
    os.makedirs(os.path.dirname(LIST_PATH), exist_ok=True)
    with open(LIST_PATH, "w", encoding="utf-8") as f:
        json.dump({"fetched_at": datetime.now().isoformat(timespec="seconds"), "bonds": bonds},
                  f, ensure_ascii=False, indent=1)
    return bonds


def _num(x):
    try:
        v = float(x)
        return v if math.isfinite(v) else None
    except (TypeError, ValueError):
        return None


def cmd_fetch(args) -> int:
    os.makedirs(CB_DIR, exist_ok=True)
    bonds = _bond_list()
    codes = [b["code"] for b in bonds]
    todo = []
    for c in codes:
        p = os.path.join(CB_DIR, f"{c}.csv")
        if os.path.exists(p) and os.path.getsize(p) > 200 and not args.force:
            continue
        todo.append(c)
    print(f"[fetch] bonds={len(codes)} pending={len(todo)} workers={args.workers}", flush=True)

    done = fail = 0

    def work(code: str) -> tuple[str, int, str | None]:
        try:
            rows = _em_get(code)
        except Exception as e:  # noqa: BLE001
            return code, 0, f"{type(e).__name__}: {e}"
        if not rows:
            return code, 0, "empty"
        out = []
        for r in rows:
            d = (r.get("DATE") or "")[:10]
            if not d:
                continue
            out.append([
                d, code,
                _num(r.get("FCLOSE")), _num(r.get("SWAPVALUE")), _num(r.get("PUREBONDVALUE")),
                _num(r.get("SWAPOR")), _num(r.get("PUREBONDOR")), _num(r.get("SWAPPRICE")),
                (r.get("BOND_NAME_ABBR") or "").replace(",", " "),
            ])
        out.sort(key=lambda x: x[0])
        p = os.path.join(CB_DIR, f"{code}.csv")
        tmp = p + ".tmp"
        with open(tmp, "w", encoding="utf-8", newline="") as f:
            f.write(",".join(COLS) + "\n")
            for row in out:
                f.write(",".join("" if v is None else str(v) for v in row) + "\n")
        os.replace(tmp, p)
        return code, len(out), None

    started = time.time()
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(work, c): c for c in todo}
        for i, fut in enumerate(as_completed(futs), 1):
            code, n, err = fut.result()
            if err:
                fail += 1
                if fail <= 12:
                    print(f"  FAIL {code}: {err}", flush=True)
            else:
                done += 1
            if i % 100 == 0:
                print(f"  {i}/{len(todo)} ok={done} fail={fail} {time.time() - started:.0f}s", flush=True)
    print(f"[fetch] done ok={done} fail={fail} in {time.time() - started:.0f}s", flush=True)
    return 0


# ---------------------------------------------------------------- build

def cmd_build(args) -> int:
    import csv
    import gzip
    files = sorted(f for f in os.listdir(CB_DIR) if f.endswith(".csv"))
    if not files:
        print("[build] no per-bond files", flush=True)
        return 2
    n_rows = 0
    with gzip.open(PANEL_PATH, "wt", encoding="utf-8", newline="") as out:
        out.write(",".join(COLS) + "\n")
        for fn in files:
            with open(os.path.join(CB_DIR, fn), "r", encoding="utf-8", newline="") as f:
                r = csv.reader(f)
                next(r, None)
                for row in r:
                    if len(row) < 9 or not row[0]:
                        continue
                    out.write(",".join(row[:9]) + "\n")
                    n_rows += 1
    print(f"[build] files={len(files)} rows={n_rows} -> {PANEL_PATH}", flush=True)
    return 0


# ---------------------------------------------------------------- run

def _load_panel():
    import pandas as pd
    df = pd.read_csv(PANEL_PATH, dtype={"code": str}, parse_dates=["date"])
    for c in ("close", "conv_value", "pure_bond_value", "conv_premium", "pure_bond_premium"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["close"])
    df = df[df["close"] > 0]
    return df.sort_values(["date", "code"]).reset_index(drop=True)


def _eligible(day_df, min_price, max_price, max_premium, itm_price, itm_premium) -> "object":
    """单日可投池。itm_* 用来剔除深度实值（强赎高危）券。"""
    d = day_df
    m = (d["close"] >= min_price) & (d["close"] <= max_price)
    if max_premium is not None:
        m &= d["conv_premium"].isna() | (d["conv_premium"] <= max_premium)
    if itm_price is not None:
        itm = (d["close"] >= itm_price) & (d["conv_premium"].notna()) & (d["conv_premium"] <= itm_premium)
        m &= ~itm
    return d[m]


def _metrics(equity, dates, rf=0.0):
    import numpy as np
    eq = np.asarray(equity, dtype=float)
    if len(eq) < 3 or eq[0] <= 0:
        return {}
    r = eq[1:] / eq[:-1] - 1.0
    years = (dates[-1] - dates[0]).days / 365.25
    cagr = (eq[-1] / eq[0]) ** (1 / years) - 1 if years > 0.2 else float("nan")
    sd = r.std(ddof=1) if len(r) > 2 else 0.0
    sharpe = ((r.mean() - rf / 244) / sd * math.sqrt(244)) if sd > 0 else float("nan")
    peak = np.maximum.accumulate(eq)
    dd = eq / peak - 1.0
    return {
        "cagr": cagr, "sharpe": sharpe, "maxdd": float(dd.min()),
        "vol": float(sd * math.sqrt(244)),
        "bars": int(len(eq)), "years": years,
    }


def _yearly(equity, dates):
    out = {}
    for i in range(1, len(equity)):
        y = dates[i].year
        if y not in out:
            out[y] = [equity[i - 1], equity[i]]
        out[y][1] = equity[i]
    return {y: (v[1] / v[0] - 1) for y, v in out.items() if v[0] > 0}


def _backtest(panel, *, n_hold=20, rebal=20, phase=0, cost_bp=10.0,
              min_price=80.0, max_price=200.0, max_premium=None,
              itm_price=130.0, itm_premium=1.0, bench=False):
    """日频 mark-to-market + 周期性调仓。

    trade day d：目标权重由 d-1 的截面算出，按 d 的收盘成交（1 bar 延迟）。
    """
    import numpy as np
    dates = list(panel["date"].drop_duplicates().sort_values())
    by_date = {d: g for d, g in panel.groupby("date")}
    idx_of_date = {d: i for i, d in enumerate(dates)}
    price = {d: dict(zip(g["code"], g["close"])) for d, g in by_date.items()}

    # 每只券最后可得日期（用于「消失即清仓」）
    last_seen = panel.groupby("code")["date"].max().to_dict()

    cash = 1.0
    holdings: dict[str, float] = {}   # code -> 市值
    equity = []
    turnover_sum = 0.0
    n_rebal = 0
    holds_hist = []
    for i, d in enumerate(dates):
        px = price.get(d, {})
        # 1) 估值：给了价就按价，没给价沿用上一格（停牌）；序列终结则清仓
        new_h = {}
        for code, val in holdings.items():
            if code in px:
                prev = holdings.get(code, val)
                # 用上一格价格推算股数再乘今日价
                new_h[code] = val  # 下面统一按日收益处理
            else:
                if last_seen.get(code) == dates[max(0, i - 1)]:
                    cash += val            # 序列终结：按最后可得价变现
                else:
                    new_h[code] = val      # 停牌：沿用
        holdings = new_h
        # 按价格日收益更新持仓市值
        if i > 0:
            prev_px = price.get(dates[i - 1], {})
            for code in list(holdings.keys()):
                if code in px and code in prev_px and prev_px[code] > 0:
                    holdings[code] *= px[code] / prev_px[code]
        total = cash + sum(holdings.values())
        equity.append(total)

        # 2) 是否调仓：i 属于网格（含 1 bar 延迟 -> 用 i-1 的信号）
        if i == 0 or ((i - 1 - phase) % rebal != 0) or (i - 1) >= len(dates):
            continue
        sig_date = dates[i - 1]
        day_df = by_date.get(sig_date)
        if day_df is None or day_df.empty:
            continue
        pool = _eligible(day_df, min_price, max_price, max_premium, itm_price, itm_premium)
        if len(pool) < n_hold:
            continue
        if bench:
            picks = list(pool["code"])
            w = 1.0 / len(picks)
        else:
            pool = pool.assign(score=pool["close"] + pool["conv_premium"].fillna(50.0))
            picks = list(pool.nsmallest(n_hold, "score")["code"])
            w = 1.0 / len(picks)

        # 目标市值（按今日收盘价买卖）
        target = {}
        for code in picks:
            if code in px and px[code] > 0:
                target[code] = total * w
        if not target:
            continue
        cur = dict(holdings)
        # 只在今天有价的券上交易；没有价的不动
        codes = set(target) | set(cur)
        delta = 0.0
        for code in codes:
            if code not in px:
                continue
            cur_v = cur.get(code, 0.0)
            tgt_v = target.get(code, 0.0)
            delta += abs(tgt_v - cur_v)
        cost = delta * cost_bp / 10000.0
        turnover_sum += delta / max(total, 1e-9)
        n_rebal += 1
        # 执行：把不在目标里的持仓变现，把目标权重买回
        new_hold = {}
        for code, v in cur.items():
            if code not in target and code in px:
                cash += v
            else:
                new_hold[code] = v
        for code, tgt in target.items():
            have = new_hold.get(code, 0.0)
            diff = tgt - have
            if diff > 0:
                cash -= diff
                new_hold[code] = tgt
            else:
                cash += -diff
                new_hold[code] = tgt
        cash -= cost
        holdings = new_hold
        holds_hist.append(len(picks))

    m = _metrics(equity, dates)
    m.update({
        "n_hold": n_hold, "rebal": rebal, "phase": phase, "cost_bp": cost_bp,
        "min_price": min_price, "max_price": max_price, "max_premium": max_premium,
        "itm_price": itm_price, "itm_premium": itm_premium, "bench": bench,
        "avg_turnover_per_rebal": (turnover_sum / n_rebal) if n_rebal else None,
        "rebalances": n_rebal,
        "annual_turnover": (turnover_sum / max(m.get("years", 1), 1e-9)) if n_rebal else None,
        "avg_holds": float(np.mean(holds_hist)) if holds_hist else None,
        "first_bar": str(dates[0].date()), "last_bar": str(dates[-1].date()),
        "yearly": _yearly(equity, dates),
    })
    return m, equity, dates


def cmd_run(args) -> int:
    import pandas as pd  # noqa: F401
    panel = _load_panel()
    n_codes = panel["code"].nunique()
    print(f"[run] panel rows={len(panel)} codes={n_codes} "
          f"{panel['date'].min().date()} -> {panel['date'].max().date()}", flush=True)

    # 主配置网格：持有数 × 调仓周期 × 成本
    grid = []
    if args.quick:
        cells = [(20, 20, 10.0)]
    else:
        cells = [(n, r, c) for n in (10, 20, 30) for r in (10, 20) for c in (10.0,)]
        cells += [(20, 20, c) for c in (5.0, 20.0, 40.0)]
    for n, r, c in cells:
        m, eq, dt = _backtest(panel, n_hold=n, rebal=r, cost_bp=c)
        grid.append(m)
        print(f"  n={n} r={r} cost={c}bp -> CAGR {m['cagr']*100:.2f}% "
              f"SR {m['sharpe']:.3f} MDD {m['maxdd']*100:.1f}% "
              f"turn {m['annual_turnover']:.2f}/yr", flush=True)

    # 主配置：4 个调仓相位（稳健性）
    phases = []
    for ph in range(args.phases):
        m, _, _ = _backtest(panel, n_hold=20, rebal=20, phase=ph)
        phases.append({"phase": ph, "cagr": m["cagr"], "sharpe": m["sharpe"],
                       "maxdd": m["maxdd"], "yearly": m["yearly"]})
        print(f"  phase={ph} CAGR {m['cagr']*100:.2f}% SR {m['sharpe']:.3f} "
              f"MDD {m['maxdd']*100:.1f}%", flush=True)

    # 对照：全池等权（同一调仓网格）
    bench, _, _ = _backtest(panel, bench=True, rebal=20)
    print(f"  bench(全池等权 r20) CAGR {bench['cagr']*100:.2f}% SR {bench['sharpe']:.3f} "
          f"MDD {bench['maxdd']*100:.1f}% turn {bench['annual_turnover']:.2f}/yr", flush=True)

    # 无 ITM 过滤（看强赎剔除值不值）
    noitm, _, _ = _backtest(panel, itm_price=None, itm_premium=None)
    print(f"  no-ITM-filter CAGR {noitm['cagr']*100:.2f}% SR {noitm['sharpe']:.3f} "
          f"MDD {noitm['maxdd']*100:.1f}%", flush=True)

    out = {
        "face": "cb_dual_low",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "data": {"rows": int(len(panel)), "codes": int(n_codes),
                 "first_bar": str(panel["date"].min().date()),
                 "last_bar": str(panel["date"].max().date())},
        "rules": {
            "signal": "双低 = 收盘价 + 转股溢价率(%)",
            "execution": "t 收盘出信号，t+1 收盘成交",
            "delisting": "面板消失按最后可得收盘价清仓（不允许逃脱）",
            "cost_bp_per_side": 10.0,
            "filters": "价格 80~200；深度实值（价≥130 且溢价≤1%）剔除",
        },
        "grid": grid, "phases": phases, "bench": bench, "no_itm_filter": noitm,
    }
    os.makedirs(os.path.dirname(RESULT_JSON), exist_ok=True)
    with open(RESULT_JSON, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1, default=str)
    _write_md(out)
    print(f"[run] -> {RESULT_JSON}\n[run] -> {RESULT_MD}", flush=True)
    return 0


def _write_md(out):
    L = []
    a = L.append
    d = out["data"]
    a("# 可转债双低轮动线 —— 第二条收益线（无生存者偏差）\n")
    a(f"生成 {out['generated_at']}　面板 {d['codes']} 只券 / {d['rows']} 行 / "
      f"{d['first_bar']} → {d['last_bar']}\n")
    a("## 口径（写死在脚本里）\n")
    for k, v in out["rules"].items():
        a(f"- **{k}**：{v}")
    a("\n## 主网格（成本 10bp/边）\n")
    a("| 持仓 | 调仓 | 年化 | 夏普 | 最大回撤 | 年换手 | 调仓次数 |")
    a("|---|---|---|---|---|---|---|")
    for m in out["grid"]:
        a(f"| {m['n_hold']} | {m['rebal']}日 | {m['cagr']*100:.2f}% | {m['sharpe']:.3f} | "
          f"{m['maxdd']*100:.1f}% | {m['annual_turnover']:.2f} | {m['rebalances']} |")
    b = out["bench"]
    a(f"\n**对照（全池等权，同调仓网格）**：年化 {b['cagr']*100:.2f}%、夏普 {b['sharpe']:.3f}、"
      f"最大回撤 {b['maxdd']*100:.1f}%、年换手 {b['annual_turnover']:.2f}")
    n = out["no_itm_filter"]
    a(f"\n**不剔深度实值（强赎高危）**：年化 {n['cagr']*100:.2f}%、夏普 {n['sharpe']:.3f}、"
      f"最大回撤 {n['maxdd']*100:.1f}%")
    a("\n## 调仓相位稳健性（持有 20 / 20 日）\n")
    a("| 相位 | 年化 | 夏普 | 最大回撤 |")
    a("|---|---|---|---|")
    for p in out["phases"]:
        a(f"| {p['phase']} | {p['cagr']*100:.2f}% | {p['sharpe']:.3f} | {p['maxdd']*100:.1f}% |")
    a("\n## 分年\n")
    yrs = sorted({y for m in out["grid"] for y in m["yearly"]})
    a("| 年 | " + " | ".join(f"{m['n_hold']}/{m['rebal']}" for m in out["grid"]) + " | 等权 |")
    a("|---|" + "---|" * (len(out["grid"]) + 1))
    for y in yrs:
        cells = []
        for m in out["grid"]:
            v = m["yearly"].get(str(y), m["yearly"].get(y))
            cells.append(f"{v*100:.1f}%" if isinstance(v, (int, float)) else "—")
        bv = b["yearly"].get(str(y), b["yearly"].get(y))
        a(f"| {y} | " + " | ".join(cells) + " | " +
          (f"{bv*100:.1f}%" if isinstance(bv, (int, float)) else "—") + " |")
    a("\n> 这是测量面：不改任何生产书、不下单。判负就关线。")
    with open(RESULT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="可转债双低轮动线")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p1 = sub.add_parser("fetch")
    p1.add_argument("--workers", type=int, default=4)
    p1.add_argument("--force", action="store_true")
    p2 = sub.add_parser("build")
    p3 = sub.add_parser("run")
    p3.add_argument("--quick", action="store_true")
    p3.add_argument("--phases", type=int, default=4)
    args = ap.parse_args(argv)
    return {"fetch": cmd_fetch, "build": cmd_build, "run": cmd_run}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
