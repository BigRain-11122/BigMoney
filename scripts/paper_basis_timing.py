"""Daily paper marks for the one line that passed: basis timing-to-size.

Why this exists
---------------
`bench_basis_timing_size` is the only cell that cleared every criterion (IC
+10.09%/yr carry vs +2.73% always-on, permutation p=0.0000; IM +9.30% vs
+5.63%). A GO on historical bars is still a claim. The cheapest way to keep
honest is a paper book that marks itself every session: the rule is frozen
(250-day trailing percentile, weight = clamp((80-pct)/60, 0, 1)), so each new
bar either confirms the carry or starts eating into it.

What it writes
--------------
  results/paper_basis_timing/LEDGER.json   per-day marks (append-only)
  results/paper_basis_timing/STATE.json    current weight and cumulative carry
  research/PAPER-BASIS-TIMING.md           reader page

Idempotent: running twice on the same bar writes nothing new. It never invents a
bar; if the lane is stale it reports STALE and exits 0.
"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bench_core as bc  # noqa: E402
import idx_fut_basis as base  # noqa: E402

OUT_DIR = os.path.join(bc.RESULTS, "paper_basis_timing")
LEDGER = os.path.join(OUT_DIR, "LEDGER.json")
STATE = os.path.join(OUT_DIR, "STATE.json")
PAGE = os.path.join(bc.RESEARCH, "PAPER-BASIS-TIMING.md")
WINDOW = 250
MIN_OBS = 60
COST_BP_SIDE = 1.5
PRODUCTS = ("IC", "IM")
TZ = timezone(timedelta(hours=8))


def now():
    return datetime.now(TZ)


def read_json(path, default):
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


def series(code):
    pair = base.PAIRS[code]
    fut = {}
    for r in base.read_csv_rows(os.path.join(bc.DATA, "futures_daily", code + ".csv")):
        try:
            v = float(r["close"])
        except (KeyError, TypeError, ValueError):
            continue
        if v > 0:
            fut[str(r["date"])[:10]] = v
    idx = base.load_index(pair[0])
    dates, f, i = base.aligned(fut, idx)
    return dates, np.array(f, float), np.array(i, float)


def weight_for(basis):
    lo = max(0, len(basis) - WINDOW)
    win = basis[lo:]
    if len(win) < MIN_OBS:
        return 0.0
    x = basis[-1]
    p = 100.0 * (float(np.sum(win < x)) + 0.5 * float(np.sum(win == x))) / len(win)
    return max(0.0, min(1.0, (80.0 - p) / 60.0))


def run():
    ledger = read_json(LEDGER, {"marks": []})
    marks = {f"{m['product']}:{m['date']}": m for m in ledger.get("marks", [])}
    added = []
    for code in PRODUCTS:
        dates, f, i = series(code)
        if len(dates) < 300:
            continue
        basis = f / i - 1.0
        rets_f = np.diff(f) / f[:-1]
        rets_i = np.diff(i) / i[:-1]
        spread = rets_f - rets_i
        # roll mask, same rule as the published face
        db = np.abs(np.diff(basis))
        scale = max(float(np.median(db)), 0.001) if len(db) else 0.001
        roll = np.array([x > 8.0 * scale and x > 0.005 for x in db])

        prev_w = None
        for k in range(len(spread)):
            d = dates[k + 1]
            key = f"{code}:{d}"
            if key in marks:
                prev_w = marks[key]["weight"]
                continue
            w = weight_for(basis[:k + 2])
            carry = 0.0 if roll[k] else prev_w * spread[k] if prev_w is not None else 0.0
            cost = 0.0 if prev_w is None else abs(w - prev_w) * COST_BP_SIDE / 10000.0
            marks[key] = {"date": d, "product": code, "weight": round(w, 4),
                          "carry_pct": round((carry - cost) * 100, 6),
                          "basis_pct": round(float(basis[k + 1]) * 100, 4)}
            added.append(key)
            prev_w = w

    ordered = sorted(marks.values(), key=lambda m: (m["date"], m["product"]))
    per_product = {}
    for code in PRODUCTS:
        rows = [m for m in ordered if m["product"] == code]
        if not rows:
            continue
        cum = float(np.cumprod([1.0 + m["carry_pct"] / 100.0 for m in rows])[-1] - 1.0)
        per_product[code] = {
            "days": len(rows),
            "first": rows[0]["date"], "last": rows[-1]["date"],
            "current_weight": rows[-1]["weight"],
            "cumulative_carry_pct": round(cum * 100, 3),
            "annualised_pct": (round(((1 + cum) ** (bc.TRADING_DAYS / len(rows)) - 1) * 100, 2)
                               if len(rows) >= 20 else None),
            "best_day_pct": round(max(m["carry_pct"] for m in rows), 3),
            "worst_day_pct": round(min(m["carry_pct"] for m in rows), 3),
        }

    last_bar = max((m["date"] for m in ordered), default=None)
    write_json(LEDGER, {"updated": now().isoformat(timespec="seconds"), "marks": ordered})
    state = {
        "generated": now().isoformat(timespec="seconds"),
        "evidence_cutoff": last_bar,
        "last_bar": last_bar,
        "products": per_product,
        "rule": {"window": WINDOW, "min_obs": MIN_OBS,
                 "weight": "clamp((80-percentile)/60,0,1)",
                 "cost_bp_side": COST_BP_SIDE},
        "cost": {"basis": "per_side_bp", "side_bp": COST_BP_SIDE},
        "verdict": ("TRACKING" if per_product else "NO_DATA"),
        "new_marks": len(added),
    }
    write_json(STATE, state)

    lines = ["# 基差定仓位 · 纸盘跟踪", "",
             f"generated {state['generated']} | 最新 bar {last_bar} | 本次新增 {len(added)} 条", "",
             "规则（冻结）：过去 250 日分位 → 权重 = clamp((80−分位)/60, 0, 1)；"
             f"成本 {COST_BP_SIDE}bp/边；carry = 期货 − 指数。", "",
             "| 品种 | 天数 | 当前权重 | 累计 carry | 年化 | 最好日 | 最差日 |",
             "|---|---|---|---|---|---|---|"]
    for code, v in per_product.items():
        lines.append(f"| {code} | {v['days']} | {v['current_weight']:.2f} | "
                     f"{v['cumulative_carry_pct']}% | {bc.fmt_pct(v['annualised_pct'])} | "
                     f"{v['best_day_pct']}% | {v['worst_day_pct']}% |")
    lines += ["", "这份台账每天多一行；它不预测，只记账。若累计 carry 长期转负，"
                  "该 GO 自动失效（回到常驻持有）。"]
    with open(PAGE, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")

    print(json.dumps({"ok": True, "verdict": state["verdict"], "new_marks": len(added),
                      "last_bar": last_bar,
                      "weights": {k: v["current_weight"] for k, v in per_product.items()}},
                     ensure_ascii=False, indent=1))
    return state


if __name__ == "__main__":
    res = run()
    sys.exit(0 if isinstance(res, dict) and res.get("verdict") in ("TRACKING", "NO_DATA") else 1)
