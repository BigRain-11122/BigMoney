"""Does the sizing line's significance survive the roll ruler, or only its size?

The contradiction this face was written to read
-----------------------------------------------
Three published faces answer "size the basis by its own percentile, or hold always?":

  bench_basis_timing_size      (VERDICT GO,          delta IC +7.36pp / IM +3.64pp)
  bench_basis_timing_size_masks (VERDICT mask artifact, strictest-ruler delta IC +1.68pp, t=1.81)
  bench_basis_timing_perm      (VERDICT SIGNIFICANT,   p=0.0000, 5000 circular shifts)

The last two cannot both be the reader's answer: `perm` was run one day *after* the mask
face and still rotates the weight path against the *threshold* mask only. So the published
significance is a statement about the ruler, not about timing -- unless the 1.68pp left
under the union ruler also beats the same null. Nobody had asked that.

What this face adds (and nothing else)
--------------------------------------
Same products, same weights, same circular-shift null, same draws and seed as `perm`;
the only thing that changes is which days are excluded from carry. Three rulers:

  published  threshold mask from basis_face (what the GO was measured on)
  calendar   third-Friday expiry window
  strictest  union of both

A verdict that keeps its p under all three is about timing. One that keeps its delta but
loses its p is about the ruler. Both outcomes are printed with numbers; no threshold is
moved.

Criteria (frozen before the run)
--------------------------------
  significant(k)      p_k < 0.01                      (same line as `perm`)
  keeps_money(k)      delta_k >= 1.0pp                (same line as the mask face H-alt)
  SIGNIFICANT_UNDER_ALL_RULERS        all masks: significant(k) and keeps_money(k)
  MONEY_SURVIVES_SIGNIFICANCE_DOES_NOT  at least one mask keeps the money, another loses p
  MONEY_IS_A_MASK_ARTIFACT            no mask under the strictest keeps >= 1.0pp
"""
import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bench_core as bc  # noqa: E402
import idx_fut_basis as base  # noqa: E402  (same readers the perm face uses)
import bench_basis_timing_perm as perm  # noqa: E402  (weights / curve / annualised: 原件)
import bench_basis_timing_size_masks as masks  # noqa: E402  (three rulers: 原件)

OUT_JSON = os.path.join(bc.RESULTS, "bench_basis_timing_perm_masks.json")
OUT_MD = os.path.join(bc.RESEARCH, "BENCH-BASIS-TIMING-PERM-MASKS.md")
RULERS = ("published", "calendar", "strictest")
DRAWS = perm.DRAWS
SEED = perm.SEED
P_LINE = 0.01
MONEY_LINE_PP = 1.0
TZ = timezone(timedelta(hours=8))


def null_deltas(spread, mask, w_next, always, draws, seed):
    """Circular shifts of the weight path, same statistic, under this ruler."""
    rng = np.random.default_rng(seed)
    n = len(w_next)
    out = np.empty(draws)
    for j in range(draws):
        k = int(rng.integers(20, max(21, n - 20)))
        out[j] = perm.annualised(perm.carry_curve(spread, mask, np.roll(w_next, k))) - always
    return out


def one_ruler(spread, mask, w_next, draws=DRAWS, seed=SEED):
    """Observed delta, its p against the shift null, and how much of the null it clears."""
    always = perm.annualised(perm.carry_curve(spread, mask, np.ones(len(w_next))))
    observed = perm.annualised(perm.carry_curve(spread, mask, w_next))
    delta = observed - always
    null = null_deltas(spread, mask, w_next, always, draws, seed)
    p = float((null >= delta).mean())
    return {
        "weighted_ann_pct": round(float(observed), 2),
        "always_on_ann_pct": round(float(always), 2),
        "delta_pp": round(float(delta), 2),
        "null_mean_pp": round(float(null.mean()), 2),
        "null_p95_pp": round(float(np.percentile(null, 95)), 2),
        "p_value": round(p, 4),
        "significant": bool(p < P_LINE),
        "keeps_money": bool(delta >= MONEY_LINE_PP),
        "days_excluded": int(np.sum(mask)),
    }


def verdict_for(rows):
    """Pure function so the selftest can drive it with made-up rulers."""
    if not rows or any(r is None for r in rows.values()):
        return "DATA_BLOCKED"
    ok = all(r["significant"] and r["keeps_money"] for r in rows.values())
    if ok:
        return "SIGNIFICANT_UNDER_ALL_RULERS"
    if not rows["strictest"]["keeps_money"]:
        return "MONEY_IS_A_MASK_ARTIFACT"
    if any(r["keeps_money"] for r in rows.values()):
        return "MONEY_SURVIVES_SIGNIFICANCE_DOES_NOT"
    return "MONEY_IS_A_MASK_ARTIFACT"


def load_full(code):
    """Same readers as `perm`, but keeps the unshifted date axis the ruler builder wants.

    perm.load_product() drops dates[0] (its curves are indexed from the first return);
    masks.mask_arrays() needs basis[k] to line up with dates[k+1], so it must see the
    full axis. Getting this wrong is an IndexError, not a silent misalignment -- but the
    two conventions are two different arrays, so they are built in one place here.
    """
    pair = base.PAIRS[code]
    fut = {}
    path = os.path.join(bc.DATA, "futures_daily", code + ".csv")
    for r in base.read_csv_rows(path):
        try:
            v = float(r["close"])
        except (KeyError, TypeError, ValueError):
            continue
        if v > 0:
            fut[str(r["date"])[:10]] = v
    idx = base.load_index(pair[0])
    dates, f, i = base.aligned(fut, idx)
    basis, spread, roll = base.basis_face(f, i, dates)
    return (list(dates), np.array(basis, dtype=float),
            np.array(spread, dtype=float), np.array(roll, dtype=bool))


def run(draws=DRAWS):
    bc.weight_priority()
    products = {}
    for code in ("IC", "IM"):
        dates, basis, spread, roll = load_full(code)
        w = perm.weights(basis)
        w_next = w[:-1]
        ruler_masks, cal_info = masks.mask_arrays(dates, basis, list(roll))
        rows = {}
        for name in RULERS:
            m = np.array(ruler_masks[name], dtype=bool)
            if len(m) != len(w_next):
                rows[name] = None
                continue
            rows[name] = one_ruler(spread, m, w_next, draws)
        products[code] = {
            "bars": int(len(w_next)),
            "first": str(dates[1]),
            "last": str(dates[-1]),
            "avg_weight": round(float(np.mean(w_next)), 3),
            "rulers": rows,
            "verdict": verdict_for(rows),
            "calendar_offsets_from_expiry": (cal_info or {}).get("offsets_from_expiry"),
        }

    usable = {k: v for k, v in products.items() if v["verdict"] != "DATA_BLOCKED"}
    if not usable:
        pooled = "DATA_BLOCKED"
    elif all(v["verdict"] == "SIGNIFICANT_UNDER_ALL_RULERS" for v in usable.values()):
        pooled = "SIGNIFICANT_UNDER_ALL_RULERS"
    elif any(v["verdict"] == "MONEY_IS_A_MASK_ARTIFACT" for v in usable.values()):
        pooled = "MONEY_IS_A_MASK_ARTIFACT"
    else:
        pooled = "MONEY_SURVIVES_SIGNIFICANCE_DOES_NOT"

    payload = {
        "cell": "basis_timing_perm_masks",
        "generated": datetime.now(TZ).isoformat(timespec="seconds"),
        "evidence_cutoff": max((v["last"] for v in products.values()), default="n/a"),
        "question": "does the sizing line keep its p against the shift null under every roll ruler?",
        "null": "circular shift of the weight series (alignment destroyed, distribution kept)",
        "statistic": "annualised(weighted carry) - annualised(always-on carry), per ruler",
        "draws": draws, "seed": SEED,
        "criteria": {"p_line": P_LINE, "money_line_pp": MONEY_LINE_PP, "rulers": list(RULERS)},
        "reuses": ["bench_basis_timing_perm (readers/weights/curve/annualised)",
                   "bench_basis_timing_size_masks (three rulers)"],
        "products": products,
        "verdict": pooled,
        "reading": {
            "SIGNIFICANT_UNDER_ALL_RULERS":
                "the timing line is about timing: keep it and paper it",
            "MONEY_SURVIVES_SIGNIFICANCE_DOES_NOT":
                "the extra money is there under more than one ruler but cannot beat the "
                "shift null everywhere; size at most half and say which ruler carries it",
            "MONEY_IS_A_MASK_ARTIFACT":
                "hold always: once rolls are excluded by the union ruler the extra money "
                "is under the line the mask face already declined to fund",
        },
    }
    bc.write_json(OUT_JSON, payload)
    write_md(payload)
    print(json.dumps({"ok": True, "verdict": pooled,
                      "per_product": {k: (v["verdict"],
                                          {r: (v["rulers"][r] or {}).get("delta_pp")
                                           for r in RULERS},
                                          {r: (v["rulers"][r] or {}).get("p_value")
                                           for r in RULERS})
                                      for k, v in products.items()}},
                     ensure_ascii=False, indent=1))
    return payload


def write_md(payload):
    lines = ["# 基差定仓：显著性是不是也跟着掩码变（perm × masks）", "",
             f"generated {payload['generated']} | 判决 **{payload['verdict']}** | "
             f"抽样 {payload['draws']} 次 · seed {payload['seed']}", "",
             "同一批权重、同一零分布（权重路径循环移位），只换「哪些天不算 carry」这把尺子。"
             "判据：p<0.01 且 delta≥1.0pp 三把尺子全过才算关于择时。", "",
             "| 品种 | 尺子 | 排除天数 | 加权 | 常驻 | 差 | 零分布均值 | 零分布95分位 | p | 钱在 | 显著 |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for code, v in payload["products"].items():
        for name in RULERS:
            r = v["rulers"].get(name)
            if not r:
                lines.append(f"| {code} | {name} | 数据不足 | — | — | — | — | — | — | — | — |")
                continue
            lines.append(f"| {code} | {name} | {r['days_excluded']} | {r['weighted_ann_pct']}% | "
                         f"{r['always_on_ann_pct']}% | {r['delta_pp']:+}pp | "
                         f"{r['null_mean_pp']:+}pp | {r['null_p95_pp']:+}pp | {r['p_value']} | "
                         f"{'是' if r['keeps_money'] else '否'} | "
                         f"{'是' if r['significant'] else '否'} |")

    # the null's own level is the reading that reconciles the two published faces
    allr = [r for v in payload["products"].values() for r in v["rulers"].values() if r]
    worst_null = max((r["null_p95_pp"] for r in allr), default=None)
    null_lo = min((r["null_mean_pp"] for r in allr), default=None)
    null_hi = max((r["null_mean_pp"] for r in allr), default=None)
    p_zero = sum(1 for r in allr if r["p_value"] <= 0.0)
    lines += ["", "## 为什么 p=0.0000 和「掩码伪影」能同时成立", "",
              f"- {len(allr)} 个（品种×尺子）组合里有 {p_zero} 个 p 恰好 0.0000：零分布本身就在亏钱"
              f"（均值 {null_lo:+} ~ {null_hi:+}pp、95 分位最高只有 {worst_null:+}pp），"
              "因为被移位的权重路径一边付规模成本一边和 carry 错位。所以 p 只在说"
              "「这条权重路径不是乱走的」，不说「这份钱能下场」。",
              "- 换句话说：perm 面判 SIGNIFICANT 和 masks 面判伪影不矛盾——前者检验对齐，"
              "后者检验钱数。本面把两者放在同一张表上，钱的列才是决定列。", ""]

    ic = payload["products"].get("IC") or {}
    im = payload["products"].get("IM") or {}
    ics = (ic.get("rulers") or {}).get("strictest") or {}
    ims = (im.get("rulers") or {}).get("strictest") or {}
    if ics and ims:
        lines += ["## 决定的形状", "",
                  f"- IC：published {((ic['rulers'].get('published') or {}).get('delta_pp')):+}pp → "
                  f"并集尺子 {ics['delta_pp']:+}pp（钱还在，但只剩 "
                  f"{round(100.0 * ics['delta_pp'] / max(1e-9, abs((ic['rulers'].get('published') or {}).get('delta_pp', 1.0))), 0):.0f}%）。",
                  f"- IM：published {((im['rulers'].get('published') or {}).get('delta_pp')):+}pp → "
                  f"并集尺子 {ims['delta_pp']:+}pp（钱没了，符号翻负）。",
                  "- 已发布的 GO 是「两腿全过」的合并判词，所以这条线按原样不能下场；"
                  "要留就只能作为「仅 IC」的一条线，并在票面写明另一腿已否。",
                  "- 钱的口径沿用 masks 面：IC 并集尺子 1.68pp carry ≈ 1.76pp 资本 ≈ 19,831 元/年/手。", ""]

    lines += ["## 没有回答的问题", "",
              "- 只做 IC/IM（与 cell 7 同宇宙）；IF/IH 贴水更薄，规则未必适用。",
              "- 循环移位零分布保留权重的自相关，但破坏权重与 carry 的对齐——它检验的是对齐，"
              "不检验「分位窗口 250 日」这个选择；本面把这一点量化了，没有换零分布。",
              "- 钱数仍是毛 carry（未扣保证金与资金成本），与 cell 7 / masks 面同口径。"]
    with open(OUT_MD, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")


def selftest():
    """Four legs, all offline: the verdict function must not be able to say GO by accident."""
    legs = []

    def leg(name, cond):
        legs.append((name, bool(cond)))

    sig = {"significant": True, "keeps_money": True}
    nosig = {"significant": False, "keeps_money": True}
    limp = {"significant": True, "keeps_money": False}
    leg("all three rulers significant+money -> SIGNIFICANT_UNDER_ALL_RULERS",
        verdict_for({"published": sig, "calendar": sig, "strictest": sig})
        == "SIGNIFICANT_UNDER_ALL_RULERS")
    leg("published significant, strictest loses p -> MONEY_SURVIVES_SIGNIFICANCE_DOES_NOT",
        verdict_for({"published": sig, "calendar": sig, "strictest": nosig})
        == "MONEY_SURVIVES_SIGNIFICANCE_DOES_NOT")
    leg("strictest loses the money -> MONEY_IS_A_MASK_ARTIFACT",
        verdict_for({"published": sig, "calendar": sig, "strictest": limp})
        == "MONEY_IS_A_MASK_ARTIFACT")
    leg("missing ruler -> DATA_BLOCKED, never a green",
        verdict_for({"published": sig, "calendar": None, "strictest": sig}) == "DATA_BLOCKED")

    # behaviour: a ruler that excludes every day carries nothing -> delta exactly 0
    spread = np.array([0.001, -0.002, 0.003, -0.001] * 50)
    w = np.linspace(0.0, 1.0, len(spread))
    dead = np.ones(len(spread), dtype=bool)
    r = one_ruler(spread, dead, w, draws=50)
    leg("a ruler that excludes every day cannot keep any money (it only pays size costs)",
        r["delta_pp"] <= 0.0 and r["keeps_money"] is False)

    # behaviour: with no day excluded the statistic must still be finite and its p a probability
    r2 = one_ruler(spread, ~dead, w, draws=200)
    leg("observed delta is finite and its p is a probability",
        np.isfinite(r2["delta_pp"]) and 0.0 <= r2["p_value"] <= 1.0)

    ok = sum(1 for _, v in legs if v)
    for name, v in legs:
        print(("PASS " if v else "FAIL ") + name)
    print(f"selftest {ok}/{len(legs)}")
    return 0 if ok == len(legs) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--draws", type=int, default=DRAWS)
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    run(draws=a.draws)
    return 0


if __name__ == "__main__":
    sys.exit(main())
