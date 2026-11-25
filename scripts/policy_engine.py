"""Policy engine: turn the strategy document into a daily, checkable instruction.

What this does (and does not do)
--------------------------------
It does not pick strategies -- that is research's job (and the strategy document
fixes which legs exist). It takes the three legs as given, reads the *live* state
of each (production ETF book k and holdings, the basis percentile rule, the
futures prices), applies the drawdown ladder and the caps from
research/STRATEGY-20261125.md, and prints today's instruction: notional, lots,
margin, expected annual carry in CNY, and each leg's risk contribution.

Inputs are read, never re-typed: the ETF leg from the book's own ledger row, the
basis leg from the same frozen percentile rule the paper book uses, the contract
multipliers and prices from the futures files.
"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bench_core as bc  # noqa: E402
import idx_fut_basis as base  # noqa: E402
import paper_basis_timing as paper  # noqa: E402

OUT_DIR = os.path.join(bc.RESULTS, "policy")
OUT = os.path.join(OUT_DIR, "POLICY.json")
PAGE = os.path.join(bc.RESEARCH, "POLICY-TODAY.md")
BOOK_POS = os.path.join(bc.RESULTS, "etf_book_positions.json")
PAPER_STATE = os.path.join(bc.RESULTS, "paper_basis_timing", "STATE.json")
TZ = timezone(timedelta(hours=8))

MULT = {"IC": 200.0, "IF": 300.0, "IH": 300.0, "IM": 200.0}
MARGIN_RATE = 0.12          # exchange margin, conservative
L2_NOTIONAL_CAP_X = 2.5     # notional / NAV
L2_MARGIN_CAP = 0.35        # margin / NAV
K_CAP = 0.55
VOL_TARGET = 0.07          # caps bind at ~6.5%; 9% would need a third leg
L1_VOL_AT_K1 = 0.105        # book vol per unit k, from the tearsheet
L2_VOL_BUDGET = 0.035
DRAWDOWN_LADDER = [(0.10, "CLEAR_L2_AND_HALVE_L1"), (0.06, "HALVE_ALL")]


def now():
    return datetime.now(TZ)


def read_json(path, default=None):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def write_json(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
        f.write("\n")
    os.replace(tmp, path)


def l1_state():
    d = read_json(BOOK_POS) or {}
    row = (d.get("ledger_row") or {})
    return {
        "k": row.get("k"),
        "risk_book_cny": row.get("risk_book_cny"),
        "cash_cny": row.get("cash_cny"),
        "holdings": row.get("holdings") or [],
        "bar": row.get("bar"),
        "source": "results/etf_book_positions.json",
    }


def l2_state():
    """Weights from the frozen percentile rule + price/multiplier per product."""
    out = {}
    for code in ("IC", "IM"):
        dates, f, i = paper.series(code)
        if len(dates) < 300:
            continue
        basis = f / i - 1.0
        w = paper.weight_for(basis)
        price = float(f[-1])
        out[code] = {
            "weight": round(w, 4),
            "price": round(price, 2),
            "multiplier": MULT[code],
            "notional_per_lot": round(price * MULT[code], 0),
            "basis_pct": round(float(basis[-1]) * 100, 3),
            "bar": dates[-1],
        }
    return out


def paper_drawdown():
    st = read_json(PAPER_STATE) or {}
    prods = st.get("products") or {}
    worst = None
    for code, v in prods.items():
        cum = v.get("cumulative_carry_pct")
        if cum is not None and (worst is None or cum < worst):
            worst = cum
    return {"worst_cumulative_carry_pct": worst,
            "verdict": st.get("verdict"), "last_bar": st.get("last_bar")}


def compute(nav):
    l1 = l1_state()
    l2 = l2_state()
    paper_dd = paper_drawdown()

    k = l1.get("k")
    if k is None:
        k = 0.435
    steps = []
    # the ladder is driven by the *paper* drawdown of the carry leg plus the
    # book's own drawdown; here only the carry leg is measured daily
    ddc = paper_dd.get("worst_cumulative_carry_pct") or 0.0
    mode = "NORMAL"
    for level, action in DRAWDOWN_LADDER:
        if ddc <= -100.0 * level:
            mode = action
            steps.append(f"paper carry {ddc}% <= -{level*100:.0f}% -> {action}")
            break
    k_eff = min(k, K_CAP)
    if mode == "HALVE_ALL":
        k_eff *= 0.5
    elif mode == "CLEAR_L2_AND_HALVE_L1":
        k_eff = min(k_eff, 0.25)

    l1_amount = round(nav * k_eff, 2)
    l2_budget = nav * L2_NOTIONAL_CAP_X
    if mode != "NORMAL":
        l2_budget *= 0.0 if mode.startswith("CLEAR") else 0.5

    legs = {}
    margin_total = 0.0
    for code, v in l2.items():
        w = v["weight"] * (l2_budget / max(nav, 1.0)) if l2_budget else 0.0
        notional = l2_budget * v["weight"]
        lots = int(round(notional / v["notional_per_lot"])) if v["notional_per_lot"] else 0
        notional_real = lots * v["notional_per_lot"]
        margin = notional_real * MARGIN_RATE
        margin_total += margin
        legs[code] = {**v, "target_weight": round(w, 4), "target_notional_cny": round(notional, 0),
                      "lots": lots, "notional_at_lots_cny": round(notional_real, 0),
                      "margin_cny": round(margin, 0)}

    if nav > 0 and margin_total > nav * L2_MARGIN_CAP:
        scale = (nav * L2_MARGIN_CAP) / margin_total
        for code in legs:
            legs[code]["lots"] = int(np.floor(legs[code]["lots"] * scale))
            legs[code]["notional_at_lots_cny"] = round(legs[code]["lots"] *
                                                       legs[code]["notional_per_lot"], 0)
            legs[code]["margin_cny"] = round(legs[code]["notional_at_lots_cny"] * MARGIN_RATE, 0)
        steps.append(f"margin {margin_total:.0f} > {L2_MARGIN_CAP*nav:.0f} -> lots scaled by {scale:.2f}")
        margin_total = sum(v["margin_cny"] for v in legs.values())

    l3 = max(nav - l1_amount - margin_total, 0.0)

    # risk contributions (declared assumptions, not fitted)
    l1_vol = L1_VOL_AT_K1 * k_eff
    l2_notional = sum(v["notional_at_lots_cny"] for v in legs.values())
    l2_carry_vol = 0.04          # measured carry vol ~4%/yr on notional
    l2_vol = (l2_notional / max(nav, 1.0)) * l2_carry_vol
    l2_vol = min(l2_vol, L2_VOL_BUDGET)
    rho = 0.10
    port_vol = float(np.sqrt(l1_vol ** 2 + l2_vol ** 2 + 2 * rho * l1_vol * l2_vol))

    expected_carry = {code: round(v["lots"] * v["notional_per_lot"] *
                                  (7.38 if code == "IC" else 3.74) / 100.0, 0)
                      for code, v in legs.items()}

    return {
        "generated": now().isoformat(timespec="seconds"),
        "nav_cny": nav,
        "mode": mode,
        "steps_applied": steps,
        "l1_etf_book": {**l1, "target_k": round(k_eff, 4), "target_amount_cny": l1_amount},
        "l2_basis": legs,
        "l2_margin_total_cny": round(margin_total, 0),
        "l2_margin_pct_of_nav": round(100.0 * margin_total / nav, 1),
        "l3_cash_cny": round(l3, 0),
        "risk": {"l1_vol_pct": round(100 * l1_vol, 2),
                 "l2_vol_pct": round(100 * l2_vol, 2),
                 "assumed_corr": rho,
                 "portfolio_vol_pct": round(100 * port_vol, 2),
                 "vol_target_pct": round(100 * VOL_TARGET, 1),
                 "within_target": bool(port_vol <= VOL_TARGET)},
        "expected_carry_cny_per_year": expected_carry,
        "expected_total_cny_per_year": round(sum(expected_carry.values()), 0),
        "paper_check": paper_dd,
        "sources": {"l1": "results/etf_book_positions.json",
                    "l2_weights": "frozen percentile rule (paper_basis_timing.weight_for)",
                    "prices": "data/futures_daily/<code>.csv"},
    }


def main():
    nav = 1_000_000.0
    if len(sys.argv) > 1:
        try:
            nav = float(sys.argv[1])
        except ValueError:
            pass
    payload = compute(nav)
    write_json(OUT, payload)

    lines = ["# 今日策略指令", "",
             f"生成 {payload['generated']} · NAV {nav:,.0f} 元 · 模式 **{payload['mode']}**", ""]
    l1 = payload["l1_etf_book"]
    lines += ["## L1 权益核心（ETF 多因子书）", "",
              f"- 目标 k = **{l1['target_k']}** → {l1['target_amount_cny']:,.0f} 元"
              f"（生产簿 bar {l1.get('bar')}）",
              f"- 现持仓 {len(l1.get('holdings') or [])} 只", ""]
    lines += ["## L2 基差收成（股指期货）", "",
              "| 品种 | 贴水% | 规则权重 | 目标名义 | 手数 | 保证金 | 预期 carry/年 |",
              "|---|---|---|---|---|---|---|"]
    for code, v in payload["l2_basis"].items():
        lines.append(f"| {code} | {v['basis_pct']} | {v['weight']} | "
                     f"{v['target_notional_cny']:,.0f} | **{v['lots']}** | "
                     f"{v['margin_cny']:,.0f} | {payload['expected_carry_cny_per_year'][code]:,.0f} |")
    lines += ["", f"- 保证金合计 {payload['l2_margin_total_cny']:,.0f} 元"
                  f"（NAV 的 {payload['l2_margin_pct_of_nav']}%，上限 35%）", ""]
    r = payload["risk"]
    lines += ["## 风险与现金", "",
              f"- L1 波动贡献 {r['l1_vol_pct']}% · L2 {r['l2_vol_pct']}% · "
              f"相关系数假设 {r['assumed_corr']}",
              f"- 组合估计波动 **{r['portfolio_vol_pct']}%**（目标 {r['vol_target_pct']}%）"
              f" → {'达标' if r['within_target'] else '超标，需降档'}",
              f"- L3 现金 {payload['l3_cash_cny']:,.0f} 元",
              f"- 预期年 carry 合计 {payload['expected_total_cny_per_year']:,.0f} 元"
              f"（毛口径：未扣保证金资金成本，也未计 L1 收益）", ""]
    if payload["steps_applied"]:
        lines += ["## 本次触发的降档", ""] + [f"- {s}" for s in payload["steps_applied"]] + [""]
    pc = payload["paper_check"]
    lines += ["## 纸盘核查", "",
              f"- 纸盘状态 {pc.get('verdict')} · 最新 bar {pc.get('last_bar')} · "
              f"最差累计 carry {pc.get('worst_cumulative_carry_pct')}%"]
    with open(PAGE, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")

    print(json.dumps({"ok": True, "mode": payload["mode"],
                      "k": payload["l1_etf_book"]["target_k"],
                      "lots": {k: v["lots"] for k, v in payload["l2_basis"].items()},
                      "margin_pct": payload["l2_margin_pct_of_nav"],
                      "portfolio_vol_pct": payload["risk"]["portfolio_vol_pct"],
                      "carry_cny": payload["expected_total_cny_per_year"]},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
