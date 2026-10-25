"""ETF composite -- forward paper book (the only honest out-of-sample that exists).

The backtest in `etf_composite_pf.py` is a historical fit. This script starts a
*forward* ledger at a chosen inception bar and accrues it one trading bar at a time
from then on, using exactly the same decision grid and the same leg accounting as
the `next_open` engine there (so the accrued path is comparable to the backtest):

  close of a decision bar  -> target top-N picks
  open of the next bar     -> fill, cost 8bp/side on |weight change|
  fill bar                 -> new book earns open->close only
  other bars               -> book earns close->close

State is idempotent by bar: re-running on the same panel adds nothing, it only
appends rows for bars that appeared since the last run. Nothing here is a claim of
edge -- the ledger's job is to let the forward record either confirm or kill the
backtest.

  python scripts/etf_composite_live.py run [--inception=YYYY-MM-DD]
  python scripts/etf_composite_live.py --selftest        # offline invariants

Outputs:
  results/etf_composite_live/state.json      book state (holdings, pending order)
  results/etf_composite_live/ledger.jsonl    one row per bar after inception
  results/etf_composite_live/LIVE-<asof>.json  latest snapshot + pending order sheet
  results/etf_composite_live/CARD.md         one-page CEO face (regen every run)
"""
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import pandas as pd

import scripts.etf_composite_pf as base
from config import PATHS

OUT_DIR = os.path.join(PATHS.results_dir, "etf_composite_live")
REBAL = 20
COST = base.COST
N_HOLD = base.N_HOLD
DEFAULT_INCEPTION = "2026-10-23"


# ---------------------------------------------------------------- book mechanics
def new_state(inception):
    return {"inception": str(inception), "last_bar": None, "equity": 1.0,
            "holdings": {}, "pending": None, "bars_since_decision": 0,
            "fills": 0, "turnover_sum": 0.0, "open_gapfill": 0, "rows": 0}


def _picks(score_row, n_hold):
    s = score_row.dropna()
    if len(s) < n_hold:
        return None
    return {str(k): 1.0 / n_hold for k in s.nlargest(n_hold).index}


def accrue(state, dates, close, openp, score, rebal=REBAL, cost=COST, n_hold=N_HOLD):
    """Advance `state` over `dates` (sorted, all >= inception). Appends ledger rows.

    Returns (state, rows). Pure function of (state, panel) -- no wall clock inside.
    """
    px = close.reindex(columns=close.columns).ffill()
    op = openp.reindex(columns=close.columns)
    state = json.loads(json.dumps(state))  # deep copy, keep caller's state intact
    rows = []
    last = state.get("last_bar")
    prev_bar = pd.Timestamp(last) if last else None

    for d in dates:
        if last is not None and d <= pd.Timestamp(last):
            continue
        held = state["holdings"]
        pending = state.get("pending")
        turn = 0.0
        filled = False
        gap = 0

        if pending:
            target = pending["target"]
            turn = sum(abs(target.get(k, 0.0) - held.get(k, 0.0))
                       for k in set(target) | set(held))
            if turn > 0:
                state["equity"] *= (1.0 - cost * turn)
            state["turnover_sum"] += turn
            state["fills"] += 1
            held = dict(target)
            state["holdings"] = held
            state["pending"] = None
            filled = True
            rets = []
            for p, w in held.items():
                o = op.at[d, p] if p in op.columns else np.nan
                c = px.at[d, p] if p in px.columns else np.nan
                if not np.isfinite(o) or not np.isfinite(c) or o <= 0:
                    gap += 1
                    continue
                rets.append(w * (c / o - 1.0))
            ret = float(np.sum(rets)) if rets else 0.0
        elif held and prev_bar is not None:
            rets = []
            for p, w in held.items():
                a = px.at[prev_bar, p] if p in px.columns else np.nan
                b = px.at[d, p] if p in px.columns else np.nan
                if not np.isfinite(a) or not np.isfinite(b) or a <= 0:
                    gap += 1
                    continue
                rets.append(w * (b / a - 1.0))
            ret = float(np.sum(rets)) if rets else 0.0
        else:
            ret = 0.0

        state["equity"] *= (1.0 + ret)
        state["open_gapfill"] += gap
        state["bars_since_decision"] += (1 if state["rows"] > 0 else 0)

        # decision at this bar's close (grid: every `rebal` bars from inception)
        decided = None
        if state["rows"] % rebal == 0:
            target = _picks(score.loc[d], n_hold) if d in score.index else None
            if target:
                state["pending"] = {"decided_on": str(d.date()), "target": target}
                decided = str(d.date())

        rows.append({"date": str(d.date()), "equity": round(state["equity"], 8),
                     "ret": round(ret, 8), "filled": filled, "turnover": round(turn, 4),
                     "cost": round(cost * turn, 8), "open_gapfill": gap,
                     "decided": decided,
                     "holdings": {k: round(v, 4) for k, v in state["holdings"].items()}})
        state["rows"] += 1
        state["last_bar"] = str(d.date())
        prev_bar = d
    return state, rows


# ------------------------------------------------------------------- persistence
def _load_state(inception):
    p = os.path.join(OUT_DIR, "state.json")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    return new_state(inception)


def _append_rows(rows):
    if not rows:
        return
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "ledger.jsonl"), "a", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def _write_json(name, obj):
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, name), "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)


def _read_ledger():
    p = os.path.join(OUT_DIR, "ledger.jsonl")
    if not os.path.exists(p):
        return []
    out = []
    with open(p, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def _hist_row(backtest_json, rebal=20):
    p = os.path.join(PATHS.results_dir, backtest_json)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        d = json.load(f)
    for r in d.get("runs", []):
        if r.get("label") == "nextopen_rebal%d_full" % rebal:
            return r
    return None


def _classes(symbols):
    """symbol -> asset class (bond/cash, commodity, crossborder, convertible, equity).

    Prefix-only tagging is wrong here: 159395/159396 and 551900/551510 are bond or
    money-market, so the name-keyword map comes first (scripts/etf_asset_class.py).
    """
    try:
        from scripts.etf_asset_class import classify
        return classify(list(symbols))
    except Exception as e:  # tagging is decoration, never block the ledger
        print("class tagging unavailable:", e)
        return {}


def card(state, rows, asof):
    hist = _hist_row("etf_composite_pf_open.json")
    led = _read_ledger()
    eq = state["equity"]
    pend = state.get("pending") or {}
    lines = ["# ETF 复合因子书 · 前向纸面账（%s）" % asof, "",
             "当前活：前向纸面账自 %s 起逐 bar 累计，已记 %d bar。"
             % (state["inception"], len(led)),
             "最近实物：results/etf_composite_live/ledger.jsonl（末行 %s）"
             % (led[-1]["date"] if led else "—"),
             "下个里程碑：下一交易日开盘按下方下单表成交并追加一行（≤1 交易日）", ""]
    if hist:
        lines += ["## 历史回测（next-open 口径，仅供对照，不是前向成绩）",
                  "| 区间 | 年化 | 夏普 | 最大回撤 |", "|---|---|---|---|"]
        p2 = os.path.join(PATHS.results_dir, "etf_composite_pf_open.json")
        with open(p2, encoding="utf-8") as f:
            dj = json.load(f)
        names = {"full": "2020-2026", "is_2020_2023": "2020-2023", "oos_2024_plus": "2024-2026"}
        for lbl, zh in names.items():
            r = next((x for x in dj["runs"]
                      if x.get("label") == "nextopen_rebal20_%s" % lbl), None)
            if r:
                lines.append("| %s | %.1f%% | %.2f | %.1f%% |"
                             % (zh, r["cagr"] * 100, r["sharpe"], r["maxdd"] * 100))
        lines.append("")
    lines += ["## 前向纸面账", "| 起始 | 净值 | 已成交次数 | 累计换手 |",
              "|---|---|---|---|",
              "| %s | %.4f | %d | %.3f |" % (state["inception"], eq, state["fills"],
                                             state["turnover_sum"]), ""]
    if pend.get("target"):
        lines += ["## 下单表（%s 收盘信号 → 次一交易日开盘执行）" % pend.get("decided_on"),
                  "| 代码 | 权重 | 类别 |", "|---|---|---|"]
        cls = _classes(list(pend["target"]))
        for s, w in sorted(pend["target"].items(), key=lambda kv: -kv[1]):
            lines.append("| %s | %.0f%% | %s |" % (s, w * 100, cls.get(s, "?")))
        est = sum(abs(pend["target"].get(k, 0.0) - state["holdings"].get(k, 0.0))
                  for k in set(pend["target"]) | set(state["holdings"]))
        lines += ["", "预计换手 %.2f，按 8bp/边 计成本约 %.2f%%"
                  % (est, est * COST * 100)]
        if cls and all(v == "bond" for v in cls.values()):
            lines += ["", "**当前档位=全债防御**：五个席位全是债券/货币类 —— "
                          "信号把股票腿全部关掉了，这套书在避险档只吃票息。"]
    else:
        lines += ["## 下单表", "无待执行信号（下一决策点未到）。"]
    lines += ["", "## 诚实标注", "",
              "- 这是纸面账，不是实盘；实盘开闸是 CEO 独有的物理动作。",
              "- 票池=盘上现存 ETF，含幸存者偏差；无涨跌停/申赎折溢价建模。",
              "- 历史回测列仅作对照，前向净值才是唯一的样本外证据。"]
    with open(os.path.join(OUT_DIR, "CARD.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return "\n".join(lines)


# ------------------------------------------------------------------------- runner
def run(inception=None):
    close, openp, amt, feats = base.build_panel()
    score = base.build_score(close, amt, feats)
    inception = inception or DEFAULT_INCEPTION
    state = _load_state(inception)
    dates = [d for d in close.index if d >= pd.Timestamp(state["inception"])]
    state, rows = accrue(state, dates, close, openp, score)
    _append_rows(rows)
    _write_json("state.json", state)
    asof = str(close.index[-1].date())
    pend = state.get("pending")
    snap = {"as_of": asof, "inception": state["inception"], "equity": round(state["equity"], 8),
            "basis": "next_open fill + 8bp/side", "rebal": REBAL, "n_hold": N_HOLD,
            "bars_accrued": state["rows"], "fills": state["fills"],
            "turnover_sum": round(state["turnover_sum"], 4),
            "open_gapfill": state["open_gapfill"],
            "new_rows_this_run": len(rows),
            "holdings": state["holdings"],
            "pending_order": pend,
            "pending_classes": _classes(list(pend["target"])) if pend else {},
            "note": "forward paper book; not a backtest, not investment advice"}
    _write_json("LIVE-%s.json" % asof, snap)
    print("as_of=%s inception=%s equity=%.4f new_rows=%d fills=%d"
          % (asof, state["inception"], state["equity"], len(rows), state["fills"]))
    if pend:
        print("pending order (fill next open):",
              ", ".join("%s %.0f%%" % (k, v * 100) for k, v in pend["target"].items()))
    card(state, rows, asof)
    print("card: results/etf_composite_live/CARD.md")
    return 0


# ---------------------------------------------------------------------- selftest
def selftest():
    """Offline: the accrued path must equal the engine's hand-computed leg chain."""
    ok = True
    idx = pd.to_datetime(["2021-01-04", "2021-01-05", "2021-01-06"])
    close = pd.DataFrame({"AAA": [100.0, 110.0, 100.0]}, index=idx)
    openp = pd.DataFrame({"AAA": [100.0, 105.0, 99.0]}, index=idx)
    score = pd.DataFrame({"AAA": [1.0, 1.0, 1.0]}, index=idx)
    cost = base.COST

    st = new_state("2021-01-04")
    st, rows = accrue(st, list(idx), close, openp, score, rebal=2, n_hold=1)
    expect1 = (1.0 - cost * 1.0) * (110.0 / 105.0)
    expect2 = expect1 * (100.0 / 110.0)
    got1, got2 = rows[1]["equity"], rows[2]["equity"]
    print("leg1 fill-bar  got %.10f want %.10f" % (got1, expect1))
    print("leg1 next-bar  got %.10f want %.10f" % (got2, expect2))
    if not (abs(got1 - expect1) < 1e-7 and abs(got2 - expect2) < 1e-7):
        ok = False
        print("  FAIL: accrued path != engine leg chain")

    # leg2: idempotent re-run adds nothing
    st2, rows2 = accrue(st, list(idx), close, openp, score, rebal=2, n_hold=1)
    print("leg2 rerun rows added = %d (want 0)" % len(rows2))
    if rows2:
        ok = False
        print("  FAIL: accrual is not idempotent by bar")

    # leg3: a new bar after the end accrues exactly one row
    idx3 = idx.append(pd.DatetimeIndex(["2021-01-07"]))
    c3 = close.reindex(idx3).ffill()
    o3 = openp.reindex(idx3).ffill()
    s3 = score.reindex(idx3).ffill()
    st3, rows3 = accrue(st2, list(idx3), c3, o3, s3, rebal=2, n_hold=1)
    print("leg3 new bar rows = %d (want 1)" % len(rows3))
    if len(rows3) != 1:
        ok = False
        print("  FAIL: new bar not accrued")

    # leg4: empty universe at a decision bar must not fabricate a trade
    sc_nan = score.copy()
    sc_nan.iloc[:, :] = np.nan
    st4 = new_state("2021-01-04")
    st4, rows4 = accrue(st4, list(idx), close, openp, sc_nan, rebal=2, n_hold=1)
    print("leg4 no-signal fills = %d (want 0)" % st4["fills"])
    if st4["fills"] != 0:
        ok = False
        print("  FAIL: traded without a signal")

    print("selftest:", "PASS 4/4" if ok else "FAIL")
    return 0 if ok else 1


def main():
    if "--selftest" in sys.argv:
        return selftest()
    inception = None
    for a in sys.argv:
        if a.startswith("--inception="):
            inception = a.split("=", 1)[1]
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        return run(inception)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())