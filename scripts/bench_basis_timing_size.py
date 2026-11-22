"""Bench cell 7: does sizing the basis by its own percentile beat holding it always?

The question (four-gate test (b): how much, and when)
-----------------------------------------------------
`idx_fut_basis` says the discount pays (IC +4.15pp/yr, IM +5.89pp). `idx_fut_basis_timing`
says the widest-quintile discount is followed by a bigger forward carry. Neither answers
the only question left before sizing money: **should the position be smaller when the
discount is narrow?** This cell turns the percentile into a weight and compares it with
holding the contract always.

Rule (frozen before the run)
----------------------------
  weight(k) = clamp((80 - pct_k) / 60, 0, 1)
  pct_k     = percentile of basis[k] inside basis[k-250 .. k] (trailing only, causal)
  so the widest 20% of the trailing year gets 100% and the narrowest 20% gets 0%.
Both arms hold the same futures contract long; the difference is only size. Cost is
1.5bp per side on |Δweight|. Carry = futures return minus index return, which is the
part the basis actually pays; beta is printed separately and never credited as carry.

Criteria:
  H1  weighted carry/yr >= always-on carry/yr + 1.0pp
  H2  both halves of the sample positive on weighted carry
  H3  weighted carry drawdown not worse than always-on by more than 5pp
  H4  out-of-sample (2024+) weighted carry >= always-on out-of-sample carry
  GO only if all four pass. Otherwise: keep the always-on book and say so.
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bench_core as bc  # noqa: E402
import idx_fut_basis as base  # noqa: E402  (same readers, same roll rule)

OUT_JSON = os.path.join(bc.RESULTS, "bench_basis_timing_size.json")
OUT_MD = os.path.join(bc.RESEARCH, "BENCH-BASIS-TIMING-SIZE.md")
WINDOW = 250
MIN_OBS = 60
LOW_Q, HIGH_Q = 20.0, 80.0
COST_BP_SIDE = 1.5
SPLIT = "2024-01-01"
H1_MARGIN_PP = 1.0
H3_TOLERANCE_PP = 5.0


def percentile(win, x):
    below = sum(1 for v in win if v < x)
    equal = sum(1 for v in win if v == x)
    return 100.0 * (below + 0.5 * equal) / len(win)


def weights(basis):
    w = [0.0] * len(basis)
    for k in range(len(basis)):
        lo = max(0, k - WINDOW + 1)
        win = basis[lo:k + 1]
        if len(win) < MIN_OBS:
            w[k] = 0.0
            continue
        p = percentile(win, basis[k])
        w[k] = max(0.0, min(1.0, (HIGH_Q - p) / (HIGH_Q - LOW_Q)))
    return w


def curve(spread, roll, w):
    """Daily returns: carry = w_prev * spread (roll days excluded), minus size costs."""
    n = len(spread)
    net = []
    carry = []
    turn = 0.0
    prev = 0.0
    for k in range(n):
        wk = w[k] if k < len(w) else 0.0
        carry_k = 0.0 if roll[k] else wk * spread[k]
        cost = abs(wk - prev) * COST_BP_SIDE / 10000.0
        carry.append(carry_k - cost)
        net.append(carry_k - cost)
        turn += abs(wk - prev)
        prev = wk
    return carry, net, turn


def annualise(vals):
    if not vals:
        return None
    eq = float(np.cumprod(1.0 + np.array(vals))[-1])
    years = len(vals) / bc.TRADING_DAYS
    return round((eq ** (1.0 / years) - 1.0) * 100, 2) if years > 0 else None


def mdd(vals):
    if not vals:
        return None
    eq = np.cumprod(1.0 + np.array(vals))
    return round(float(np.min(eq / np.maximum.accumulate(eq) - 1.0)) * 100, 2)


def halves(vals):
    mid = len(vals) // 2
    return annualise(vals[:mid]), annualise(vals[mid:])


def run():
    bc.weight_priority()
    products = {}
    for code in ("IC", "IM"):
        pair = base.PAIRS.get(code)
        if not pair:
            continue
        idx_code = pair[0]
        fut = {}
        path = os.path.join(bc.DATA, "futures_daily", code + ".csv")
        for r in base.read_csv_rows(path):
            try:
                v = float(r["close"])
            except (KeyError, TypeError, ValueError):
                continue
            if v > 0:
                fut[str(r["date"])[:10]] = v
        idx = base.load_index(idx_code)
        dates, f, i = base.aligned(fut, idx)
        if len(dates) < 400:
            products[code] = {"state": "NOT_ENOUGH_BARS", "bars": len(dates)}
            continue
        basis, spread, roll = base.basis_face(f, i, dates)
        d1 = dates[1:]
        w = weights(basis)
        w_next = w[:-1]                      # weight known at k drives day k+1
        w_always = [1.0] * len(spread)

        carry_w, net_w, turn_w = curve(spread, roll, w_next)
        carry_a, net_a, turn_a = curve(spread, roll, w_always)

        halves_w = halves(carry_w)
        split_i = next((k for k, d in enumerate(d1) if d >= SPLIT), len(d1))
        oos_w = annualise(carry_w[split_i:])
        oos_a = annualise(carry_a[split_i:])

        checks = {
            "H1_margin_over_always_on": bool(
                annualise(carry_w) is not None and annualise(carry_a) is not None
                and annualise(carry_w) >= annualise(carry_a) + H1_MARGIN_PP),
            "H2_both_halves_positive": bool(
                halves_w[0] is not None and halves_w[1] is not None
                and halves_w[0] > 0 and halves_w[1] > 0),
            "H3_drawdown_not_worse": bool(
                mdd(carry_w) is not None and mdd(carry_a) is not None
                and mdd(carry_w) >= mdd(carry_a) - H3_TOLERANCE_PP),
            "H4_oos_not_worse": bool(oos_w is not None and oos_a is not None and oos_w >= oos_a),
        }
        products[code] = {
            "bars": len(dates),
            "first": d1[0], "last": d1[-1],
            "full_years": round(len(d1) / bc.TRADING_DAYS, 2),
            "weighted": {"carry_ann_pct": annualise(carry_w), "net_ann_pct": annualise(net_w),
                         "carry_mdd_pct": mdd(carry_w),
                         "halves_pct": [round(x, 2) if x is not None else None for x in halves_w],
                         "oos_carry_ann_pct": oos_w,
                         "turnover_per_year": round(turn_w * bc.TRADING_DAYS / max(len(d1), 1), 2),
                         "avg_weight": round(float(np.mean(w_next)), 3),
                         "days_flat_pct": round(100.0 * float(np.mean([1.0 if x <= 0.001 else 0.0
                                                                       for x in w_next])), 1)},
            "always_on": {"carry_ann_pct": annualise(carry_a), "net_ann_pct": annualise(net_a),
                          "carry_mdd_pct": mdd(carry_a),
                          "halves_pct": [round(x, 2) if x is not None else None
                                         for x in halves(carry_a)],
                          "oos_carry_ann_pct": oos_a},
            "checks": checks,
            "verdict": bc.verdict_of(checks),
        }

    usable = {k: v for k, v in products.items() if "checks" in v}
    pooled = ("GO" if usable and all(v["verdict"] == "GO" for v in usable.values())
              else ("NO_EDGE" if usable else "DATA_BLOCKED"))
    payload = {
        "cell": "basis_timing_size",
        "generated": __import__("datetime").datetime.now(
            __import__("datetime").timezone(__import__("datetime").timedelta(hours=8))
        ).isoformat(timespec="seconds"),
        "evidence_cutoff": max((v.get("last") for v in products.values() if v.get("last")),
                               default="n/a"),
        "rule": {"weight": "clamp((80-pct)/60,0,1)", "window": WINDOW,
                 "min_obs": MIN_OBS, "cost_bp_side": COST_BP_SIDE, "split": SPLIT},
        "criteria": {"cost_bp_side": COST_BP_SIDE, "H1_margin_pp": H1_MARGIN_PP,
                     "H3_tolerance_pp": H3_TOLERANCE_PP, "split": SPLIT,
                     "window": WINDOW, "weight_rule": "clamp((80-pct)/60,0,1)"},
        "products": products,
        "verdict": pooled,
        "note": ("carry = futures minus index, rolls excluded; beta is not counted as carry. "
                 "This cell only answers 'size by percentile or hold always'."),
    }
    os.makedirs(bc.BENCH_OUT, exist_ok=True)
    bc.write_json(OUT_JSON, payload)

    lines = ["# 基差按分位定仓位 vs 常驻持有（bench cell 7）", "",
             f"generated {payload['generated']} | 判决 **{pooled}**", "",
             "规则：权重 = clamp((80−分位)/60, 0, 1)；分位只用过去 250 日（因果）；"
             f"成本 {COST_BP_SIDE}bp/边；carry=期货−指数，移仓日剔除。", "",
             "| 品种 | 加权 carry/年 | 常驻 carry/年 | 差 | 加权回撤 | 常驻回撤 | 前后半 | 样本外加权/常驻 | 判决 |",
             "|---|---|---|---|---|---|---|---|---|"]
    for code, v in products.items():
        if "checks" not in v:
            lines.append(f"| {code} | 数据不足 | — | — | — | — | — | — | {v['state']} |")
            continue
        w, a = v["weighted"], v["always_on"]
        diff = (round(w["carry_ann_pct"] - a["carry_ann_pct"], 2)
                if w["carry_ann_pct"] is not None and a["carry_ann_pct"] is not None else None)
        lines.append(f"| {code} | {bc.fmt_pct(w['carry_ann_pct'])} | {bc.fmt_pct(a['carry_ann_pct'])} | "
                     f"{diff:+}pp | {bc.fmt_pct(w['carry_mdd_pct'])} | {bc.fmt_pct(a['carry_mdd_pct'])} | "
                     f"{w['halves_pct']} | {bc.fmt_pct(w['oos_carry_ann_pct'])} / "
                     f"{bc.fmt_pct(a['oos_carry_ann_pct'])} | **{v['verdict']}** |")
    lines += ["", "## 读数", ""]
    for code, v in products.items():
        if "checks" in v:
            lines.append(f"- {code}：平均权重 {v['weighted']['avg_weight']}、"
                         f"空仓日占 {v['weighted']['days_flat_pct']}%、"
                         f"年换手 {v['weighted']['turnover_per_year']}、"
                         f"判据 {json.dumps(v['checks'], ensure_ascii=False)}")
    lines += ["", "## 没有回答的问题", "",
              "- 只做了 IC/IM 两个品种；IF/IH 的贴水更薄，规则可能不适用。",
              "- 没有建模保证金占用与资金成本：carry 是毛口径。",
              "- 分位窗口 250 日是冻结值，未做敏感性扫描（换窗口属于新格）。"]
    with open(OUT_MD, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")

    print(json.dumps({"ok": True, "verdict": pooled,
                      "per_product": {k: (v.get("weighted", {}).get("carry_ann_pct"),
                                          v.get("always_on", {}).get("carry_ann_pct"),
                                          v.get("verdict")) for k, v in products.items()}},
                     ensure_ascii=False, indent=1))
    return payload


if __name__ == "__main__":
    res = run()
    sys.exit(0 if isinstance(res, dict) and res.get("ok", True) else 1)
