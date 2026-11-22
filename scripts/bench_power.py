"""Was each negative capable of finding anything? Minimum detectable edge per cell.

Why this exists
---------------
A NO_EDGE verdict is only meaningful if the sample could have detected an edge
of the size we care about. With 10 years of data and 10% annualised vol, the
standard error on an annualised mean is about 1.96*vol/sqrt(years) -- ~3.2pp/yr
-- so a test that "fails to find 2pp" has not proven there is no 2pp edge; it
has proven there is no edge the size of its own noise. That distinction is the
difference between science and burning compute.

This script reads the published bench faces and prints, per arm:
  years, annualised vol, observed edge, the minimum detectable edge (MDE) at
  95% two-sided, and how many years would be needed to detect the target edge.
It also flags "UNPOWERED": the arm's absolute edge is below its own MDE, so the
negative is not evidence against an edge of the target size.

Target edges (what would change a decision at our scale):
  futures / bond / A-share lines: 5.0pp/yr (below that it cannot move a 1M book)
  re-validation / monitoring cells: not applicable
"""
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(ROOT, "results")
OUT_JSON = os.path.join(RESULTS, "bench_power.json")
OUT_MD = os.path.join(ROOT, "research", "BENCH-POWER.md")

T_CRIT = 1.96          # 95% two-sided
TARGET_EDGE_PP = 5.0   # the smallest edge worth a separate line at this scale
TRADING_DAYS = 244.0


def years_of(n):
    return max(n / TRADING_DAYS, 1e-9) if n else None


def mde(vol_pct, years):
    """Smallest annualised edge the sample can detect at 95% (single series)."""
    if not vol_pct or not years:
        return None
    return T_CRIT * vol_pct / math.sqrt(years)


def years_needed(vol_pct, edge_pp):
    if not vol_pct or not edge_pp:
        return None
    return (T_CRIT * vol_pct / edge_pp) ** 2


def collect():
    rows = []

    def add(cell, arm, ann, vol, n, verdict, note=""):
        yrs = years_of(n)
        m = mde(vol, yrs)
        rows.append({
            "cell": cell, "arm": arm,
            "years": None if yrs is None else round(yrs, 2),
            "ann_pct": ann, "vol_pct": vol,
            "mde_pp": None if m is None else round(m, 2),
            "years_needed_for_target": (None if years_needed(vol, TARGET_EDGE_PP) is None
                                        else round(years_needed(vol, TARGET_EDGE_PP), 1)),
            "verdict": verdict,
            "powered_for_target": (None if m is None else bool(m <= TARGET_EDGE_PP)),
            "note": note,
        })

    # futures trend
    p = os.path.join(RESULTS, "bench_fut_trend.json")
    if os.path.exists(p):
        d = json.load(open(p, encoding="utf-8"))
        hold = d.get("benchmark_buy_and_hold", {}).get("common_window", {})
        for a in d.get("arms", []):
            c = a.get("common_window") or {}
            add("fut_trend", a["style"], c.get("ann_pct"), c.get("vol_pct"),
                c.get("n"), a.get("verdict"),
                "excess vs hold: %s pp" % ((a.get("vs_hold") or {}).get(a["style"], {})
                                           .get("excess_ann_pp")))
        add("fut_trend", "buy_and_hold", hold.get("ann_pct"), hold.get("vol_pct"),
            hold.get("n"), "BENCHMARK")

    # bond curve
    p = os.path.join(RESULTS, "bench_bond_curve.json")
    if os.path.exists(p):
        d = json.load(open(p, encoding="utf-8"))
        for a in d.get("arms", []):
            c = a.get("common_window") or {}
            add("bond_curve", f"{a['pair']}:{a['style']}", c.get("ann_pct"),
                c.get("vol_pct"), c.get("n"), a.get("verdict"))
        ctl = d.get("long_duration_control", {}).get("common_window", {})
        add("bond_curve", "long_duration", ctl.get("ann_pct"), ctl.get("vol_pct"),
            ctl.get("n"), "BENCHMARK")

    # A-share low vol
    p = os.path.join(RESULTS, "bench_astock_lowvol.json")
    if os.path.exists(p):
        d = json.load(open(p, encoding="utf-8"))
        c = d.get("lowvol_book", {}).get("common_window", {})
        add("astock_lowvol", "lowvol", c.get("ann_pct"), c.get("vol_pct"), c.get("n"),
            d.get("verdict"))
        x = d.get("excess_vs_ew") or {}
        add("astock_lowvol", "excess_vs_equal_weight", x.get("ann_pct"), x.get("vol_pct"),
            x.get("n"), d.get("verdict"), "this is the decision series (paired)")

    # bond defensive
    p = os.path.join(RESULTS, "bench_bond_defensive.json")
    if os.path.exists(p):
        d = json.load(open(p, encoding="utf-8"))
        c = d.get("bond_arm", {}).get("reading", {})
        add("bond_defensive", "bond_leg", c.get("ann_pct"), c.get("vol_pct"), c.get("n"),
            d.get("verdict"))

    return rows


def main():
    rows = collect()
    for r in rows:
        if r["ann_pct"] is None:
            continue
        if r["mde_pp"] is not None and abs(r["ann_pct"]) < r["mde_pp"]:
            r["reading"] = "UNPOWERED_AT_OWN_NOISE"
        elif r["powered_for_target"] is False:
            r["reading"] = "UNDERPOWERED_FOR_5PP"
        else:
            r["reading"] = "POWERED"

    unpowered = [r for r in rows if r.get("reading") == "UNPOWERED_AT_OWN_NOISE"]
    payload = {
        "cell": "power",
        "generated": __import__("datetime").datetime.now(
            __import__("datetime").timezone(__import__("datetime").timedelta(hours=8))
        ).isoformat(timespec="seconds"),
        "target_edge_pp": TARGET_EDGE_PP,
        "t_crit": T_CRIT,
        "rule": ("an |edge| below the arm's own MDE means the sample cannot tell 'no edge' "
                 "from 'edge smaller than the noise'; such a negative is not evidence"),
        "n_unpowered": len(unpowered),
        "rows": rows,
    }
    os.makedirs(RESULTS, exist_ok=True)
    with open(OUT_JSON + ".tmp", "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
        f.write("\n")
    os.replace(OUT_JSON + ".tmp", OUT_JSON)

    lines = ["# 这些「负结论」到底有多硬（统计功效）", "",
             f"目标可下注边际：{TARGET_EDGE_PP}pp/年 · 95% 双侧 · generated {payload['generated']}",
             "",
             "| 格子 | 臂 | 年数 | 年化波动 | 观测年化 | 可检出下限(MDE) | 检出 5pp 需要年数 | 读数 |",
             "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['cell']} | {r['arm']} | {r['years']} | {r['vol_pct']} | "
                     f"{r['ann_pct']} | {r['mde_pp']} | {r['years_needed_for_target']} | "
                     f"{r.get('reading', '')} |")
    lines += ["", "## 怎么读这张表", "",
              "- **MDE** = 1.96 × 年化波动 ÷ √年数。它是这个样本能分辨的最小年化差。",
              "- 若观测值落在 ±MDE 内（UNPOWERED_AT_OWN_NOISE），只能说「没看见」，不能说「不存在」。",
              "- 若 MDE > 5pp（UNDERPOWERED_FOR_5PP），这条线要么换更长样本，要么这个样本永远回答不了。",
              "- 这一条是本轮最重要的产出：它决定了下一格该不该排队，而不是「跑得多不多」。"]
    with open(OUT_MD, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")

    print(json.dumps({"ok": True, "rows": len(rows), "unpowered": len(unpowered),
                      "target_edge_pp": TARGET_EDGE_PP,
                      "unpowered_arms": [f"{r['cell']}:{r['arm']}" for r in unpowered]},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
