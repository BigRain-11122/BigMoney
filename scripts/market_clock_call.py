# -*- coding: utf-8 -*-
"""Market-clock current call -- T-74 s1 (O-20260926-0932).

Generates the CURRENT market-clock one-pager per research/MARKET_CLOCK_COMBO.md (s0 v1.0):
  L1 = REGIME_GUARD v3 state (results/regime_state.json, produced by S6 chain) x heat composite
       (HOT if LHB last-day rows >= rolling-250d p80 of daily row counts AND net buy sum > 0);
  L2 = core48 ETF momentum board (r5/r20/r60) on files fresh at the daily panel cutoff;
  L3/L4/L5 = sleeve activation / selection faces / position ladder per the frozen table.

Deterministic, read-only on inputs, zero network. Output:
  results/market_clock/CALL-<asof>.md + results/market_clock/call_latest.json
Idempotent per asof (rerun same-day = byte-identical; no wall-clock fields).

Usage:
  python scripts/market_clock_call.py run        (normal; no-op-safe, regenerates current call)
  python scripts/market_clock_call.py selftest  (offline hermetic: synthetic regime+lhb+daily)

Exit codes: 0 = call written (or selftest pass); 2 = mechanism failure (honest, report as-is).
"""
import json
import os
import sys

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "results", "market_clock")
LHB_PATH = os.path.join(ROOT, "Money02", "data", "lhb", "lhb_detail.parquet")

# Sleeve activation table -- frozen verbatim from research/MARKET_CLOCK_COMBO.md s0 v1.0 (L3/L5).
SLEEVE_TABLE = {
    "GREEN_COOL": ["offense-corps trend/momentum sleeve (full)", "grid sleeve aux"],
    "GREEN_HOT": ["offense-corps momentum sleeve (full)", "wild-theme micro-satellite (<=5%, T-57 survivor gate)"],
    "YELLOW_COOL": ["chop-corps grid sleeve (half)", "mean-reversion range sleeve (half)"],
    "YELLOW_HOT": ["chop-corps grid sleeve (half)", "mean-reversion range sleeve (half)"],
    "ORANGE_COOL": ["chop-corps on duty (grid/mean-reversion half)", "dividend-lowvol base position"],
    "ORANGE_HOT": ["chop-corps on duty (half)", "wild-theme micro-satellite (<=5%, T-57 survivor gate)"],
    "RED_COOL": ["air-defense cash leg (>=80% cash/bond), no theme satellite"],
    "RED_HOT": ["air-defense cash leg (>=80% cash/bond), no theme satellite"],
}
POSITION_LADDER = {"RED": 0.20, "ORANGE": 0.50, "YELLOW": 0.65, "GREEN": 0.80}
HOT_LADDER_BONUS = 0.15  # GREEN x HOT -> 0.95 per canon L5


def _heat_face():
    """LHB heat composite. Returns dict with honest face-state labels on failure."""
    try:
        df = pd.read_parquet(LHB_PATH, columns=["上榜日", "龙虎榜净买额"])
    except Exception as e:
        return {"state": "FACE_ERROR", "error": repr(e)[:200]}
    df["上榜日"] = pd.to_datetime(df["上榜日"])
    daily_rows = df.groupby("上榜日").size()
    daily_net = df.groupby("上榜日")["龙虎榜净买额"].sum()
    asof = daily_rows.index.max()
    # rolling 250-trading-day p80 of daily row counts, evaluated strictly BEFORE asof (causality)
    hist = daily_rows[daily_rows.index < asof].tail(250)
    p80 = float(hist.quantile(0.80)) if len(hist) >= 60 else None
    rows_last = int(daily_rows.loc[asof])
    net_last = float(daily_net.loc[asof])
    if p80 is None:
        heat = "UNDETERMINED"
    else:
        heat = "HOT" if (rows_last >= p80 and net_last > 0) else "COOL"
    return {
        "asof": str(asof.date()),
        "rows_last_day": rows_last,
        "net_buy_sum_yuan": net_last,
        "rolling250_p80_rows": p80,
        "hist_days": int(len(hist)),
        "heat": heat,
    }


def _momentum_board(asof):
    """core48 ETF momentum board on files whose last bar == asof (fresh only, honest)."""
    import glob

    recs = []
    for f in glob.glob(os.path.join(ROOT, "data", "daily", "*.csv")):
        sym = os.path.splitext(os.path.basename(f))[0]
        try:
            px = pd.read_csv(f, usecols=[0, 4])
        except Exception:
            continue
        px.columns = ["date", "close"]
        px["date"] = pd.to_datetime(px["date"])
        px = px.sort_values("date").dropna()
        if str(px["date"].iloc[-1].date()) != asof or len(px) < 61:
            continue
        c = px["close"].values
        recs.append({
            "symbol": sym,
            "r5": round(float(c[-1] / c[-6] - 1), 4),
            "r20": round(float(c[-1] / c[-21] - 1), 4),
            "r60": round(float(c[-1] / c[-61] - 1), 4),
        })
    recs.sort(key=lambda r: r["r20"], reverse=True)
    return recs


def _regime_face():
    try:
        d = json.load(open(os.path.join(ROOT, "results", "regime_state.json"), encoding="utf-8"))
        return {"state": d.get("state"), "asof": d.get("asof"), "days_in_state": d.get("days_in_state"),
                "triggers": d.get("triggers", [])}
    except Exception as e:
        return {"state": "FACE_ERROR", "error": repr(e)[:200]}


def build_call():
    regime = _regime_face()
    heat = _heat_face()
    asof = heat.get("asof") if heat.get("asof") else regime.get("asof")
    board = _momentum_board(asof) if asof else []
    state = regime.get("state", "UNDETERMINED")
    heatv = heat.get("heat", "UNDETERMINED")
    cell = f"{state}_{heatv}" if (state and heatv) else "UNDETERMINED"
    sleeves = SLEEVE_TABLE.get(cell, ["UNDETERMINED -- face error, no instruction issued (honest)"])
    ladder = POSITION_LADDER.get(state)
    if ladder is not None and cell == "GREEN_HOT":
        ladder = round(ladder + HOT_LADDER_BONUS, 2)
    breadth = round(sum(1 for r in board if r["r20"] > 0) / len(board), 3) if board else None
    call = {
        "asof": asof,
        "clock_cell": cell,
        "regime_v3": regime,
        "heat_composite": {k: heat.get(k) for k in
                           ("rows_last_day", "net_buy_sum_yuan", "rolling250_p80_rows", "heat")},
        "sector_board_top8": board[:8],
        "sector_board_bottom5": board[-5:],
        "fresh_universe_n": len(board),
        "breadth_r20_pos": breadth,
        "active_sleeves": sleeves,
        "position_cap_ladder": ladder,
        "canon": "research/MARKET_CLOCK_COMBO.md s0 v1.0",
    }
    return call


def render_md(call):
    h = call["heat_composite"]
    L = []
    L.append(f"# 市场时钟 · 当日系统指令 — {call['asof']}")
    L.append("")
    L.append(f"- **时钟格**：`{call['clock_cell']}`（v3 政体 × 热度复合，正典=MARKET_CLOCK_COMBO.md s0 v1.0）")
    r = call["regime_v3"]
    L.append(f"- **L1 政体（v3）**：{r.get('state')} · 在态 {r.get('days_in_state')} 日 · 触发：{'；'.join(r.get('triggers', []) or [])}")
    net_yi = h.get("net_buy_sum_yuan")
    rows_lh, p80 = h.get("rows_last_day"), h.get("rolling250_p80_rows")
    cmp_rows = ">=" if (rows_lh is not None and p80 is not None and rows_lh >= p80) else "<"
    cmp_net = ">" if (net_yi or 0) > 0 else "<="
    L.append(f"- **L1 热度复合**：{h.get('heat')}（LHB 当日 {rows_lh} 行 {cmp_rows} 滚动250日p80 {p80} 且 净买 "
             f"{round(net_yi / 1e8, 2) if net_yi is not None else 'N/A'} 亿 {cmp_net} 0）")
    L.append(f"- **L2 板块面**（core48 新鲜 {call['fresh_universe_n']} 件，r20 强势榜）：")
    for r0 in call["sector_board_top8"][:8]:
        L.append(f"  - {r0['symbol']}: r5 {r0['r5']:+.1%} · r20 {r0['r20']:+.1%} · r60 {r0['r60']:+.1%}")
    bottom = "；".join("{} r20 {:+.1%}".format(r0["symbol"], r0["r20"]) for r0 in call["sector_board_bottom5"])
    L.append(f"  - 弱势榜尾：{bottom}")
    L.append(f"  - 宽度（r20>0 占比）：{call['breadth_r20_pos']}")
    L.append("- **L3/L4 激活袖与选股面**：")
    for s in call["active_sleeves"]:
        L.append(f"  - {s}")
    L.append(f"- **L5 仓位阶梯帽**：{call['position_cap_ladder'] if call['position_cap_ladder'] is not None else 'N/A'}"
             f"（RED 20% → ORANGE 50% → GREEN 80% → GREEN×HOT 95%；T0 刹车不破）")
    L.append("")
    L.append("> 面态只读判定（收盘因果），零未来数据；缺面与代理披露见正典 §1/§2。")
    return "\n".join(L)


def run():
    os.makedirs(OUT_DIR, exist_ok=True)
    call = build_call()
    asof = call.get("asof") or "undetermined"
    md_path = os.path.join(OUT_DIR, f"CALL-{asof}.md")
    with open(md_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(render_md(call))
    latest = os.path.join(OUT_DIR, "call_latest.json")
    with open(latest, "w", encoding="utf-8", newline="\n") as f:
        json.dump(call, f, ensure_ascii=False, indent=1, default=str)
    print(f"call written: {md_path} cell={call['clock_cell']} sleeves={len(call['active_sleeves'])}")
    return 0


def selftest():
    """Hermetic: monkeypatch face readers with synthetic minimal data, assert clock logic."""
    global _heat_face, _momentum_board, _regime_face
    heat = {"asof": "2026-09-24", "rows_last_day": 90, "net_buy_sum_yuan": 1.0e9, "rolling250_p80_rows": 70.0, "heat": "HOT"}
    board = [{"symbol": "X1", "r5": 0.01, "r20": 0.02, "r60": 0.03}, {"symbol": "X2", "r5": -0.01, "r20": -0.02, "r60": -0.03}]
    regime = {"state": "ORANGE", "asof": "2026-09-24", "days_in_state": 2, "triggers": ["t1"]}
    _heat_face, _momentum_board, _regime_face = (lambda: heat), (lambda a: board), (lambda: regime)
    c = build_call()
    assert c["clock_cell"] == "ORANGE_HOT", c["clock_cell"]
    assert any("micro-satellite" in s for s in c["active_sleeves"]), c["active_sleeves"]
    assert c["position_cap_ladder"] == 0.50, c["position_cap_ladder"]
    assert c["breadth_r20_pos"] == 0.5
    regime2 = dict(regime, state="GREEN")
    _regime_face = lambda: regime2
    c2 = build_call()
    assert c2["clock_cell"] == "GREEN_HOT" and c2["position_cap_ladder"] == 0.95, (c2["clock_cell"], c2["position_cap_ladder"])
    heat2 = dict(heat, heat="COOL", rows_last_day=10, net_buy_sum_yuan=-1.0e8)
    _heat_face = lambda: heat2
    c3 = build_call()
    assert c3["clock_cell"] == "GREEN_COOL" and "trend/momentum sleeve (full)" in c3["active_sleeves"][0]
    md = render_md(c3)
    assert "GREEN_COOL" in md and "L5 仓位阶梯帽" in md
    regime3 = dict(regime, state="RED")
    _regime_face = lambda: regime3
    c4 = build_call()
    assert c4["position_cap_ladder"] == 0.20 and "air-defense" in c4["active_sleeves"][0]
    print("market_clock_call selftest: PASS (4 cell-logic cases + render)")
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "selftest":
        sys.exit(selftest())
    if cmd == "run":
        sys.exit(run())
    print("usage: run | selftest", file=sys.stderr)
    sys.exit(2)
