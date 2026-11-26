"""Does repairing the donchian units change any verdict, and does it produce money?

Why this cell exists
--------------------
r2142 found the defect (the breakout compares an adjusted close index against raw
high/low prices, so the long side never triggers) and r2143 measured how wide it
is (8 of 11 signal families are unaffected; only donchian moves under a unit
perturbation). Neither answered the only question that changes a decision:

    if the units are fixed, does any card's verdict flip, and is there money?

This cell re-runs the affected cards twice on TODAY'S panel -- once with the
published behaviour (raw high/low) and once with each candidate repair -- so the
before/after difference is the units and nothing else. Published card numbers are
printed beside them only as a fidelity check (the panel has grown since those
cards were generated).

Units, stated once
------------------
bench_core.align_futures builds ``closes`` as a ROLL-ADJUSTED price series
(``adjusted_price``), while ``highs``/``lows`` are handed over raw. Two repairs
are possible and they are not the same answer:

  per_bar      high/low x (raw close / adjusted close) on the same bar
               -- exact mapping into the series the rule compares against; the
                  multiplier changes at every roll, so roll gaps stay excluded
  first_close  high/low / first raw close
               -- one constant per product; the roll gaps that adjusted_price
                  removed from ``closes`` come back into high/low

Output: results/bench_donchian_repair_rerun.json + research/BENCH-DONCHIAN-REPAIR-RERUN.md
Nothing here writes a shared face, changes bench_generic/bench_core, or re-ranks
a published card. The flip of a verdict is reported, not applied.
"""
import argparse
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bench_core as bc  # noqa: E402
import bench_generic as bg  # noqa: E402
import bench_fut_trend as ft  # noqa: E402

CELL = "donchian_repair_rerun"
OUT_JSON = os.path.join(bc.RESULTS, "bench_donchian_repair_rerun.json")
OUT_MD = os.path.join(bc.RESEARCH, "BENCH-DONCHIAN-REPAIR-RERUN.md")
CELLS = os.path.join(bc.RESEARCH, "cells")

METHODS = ["raw_panel", "per_bar", "first_close"]
METHOD_WHAT = {
    "raw_panel": "published behaviour: adjusted close compared against raw high/low",
    "per_bar": "high/low x (raw close / adjusted close) on the same bar",
    "first_close": "high/low / first raw close of that product",
}

# Fidelity tolerance: the panel has extended since the cards were generated, so
# a re-run on today's panel cannot reproduce them to the digit. Anything above
# this is a real disagreement and gets named.
FIDELITY_PP = 1.0


# --------------------------------------------------------------------------
# units
# --------------------------------------------------------------------------
def repaired_highs_lows(panel, closes, method):
    """Return (highs, lows) expressed in the same units as ``closes``."""
    if method == "raw_panel":
        return ({c: df["high"] for c, df in panel.items()},
                {c: df["low"] for c, df in panel.items()})
    highs, lows = {}, {}
    for c, df in panel.items():
        ref = closes[c]
        if method == "per_bar":
            raw = df["close"].ffill()
            adj = ref.ffill()
            # raw price -> adjusted-price units: multiply by adj/raw, never raw/adj
            factor = (adj / raw).replace([np.inf, -np.inf], np.nan)
        elif method == "first_close":
            first = df["close"].dropna()
            if not len(first) or not np.isfinite(first.iloc[0]) or first.iloc[0] <= 0:
                continue
            factor = pd.Series(1.0 / float(first.iloc[0]), index=df.index)
        else:
            raise ValueError(f"unknown method {method}")
        highs[c] = (df["high"] * factor).replace([np.inf, -np.inf], np.nan)
        lows[c] = (df["low"] * factor).replace([np.inf, -np.inf], np.nan)
    return highs, lows


def long_share(sub_cfg, closes, highs, lows):
    """Fraction of live bars on which the rule holds a long."""
    sigs = bg.build_signals(sub_cfg, closes, highs, lows)
    up = down = 0
    for s in sigs.values():
        v = s.dropna().values
        up += int((v > 0).sum())
        down += int((v < 0).sum())
    total = up + down
    return None if not total else round(up / total, 4)


# --------------------------------------------------------------------------
# cards
# --------------------------------------------------------------------------
def load_cell_config(cell_id):
    path = os.path.join(CELLS, f"{cell_id}.json")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def published_donchian_arms(cell_id, whole_card_donchian=False):
    payload = bc.read_json(os.path.join(bc.RESULTS, f"bench_{cell_id}.json"), {}) or {}
    out = {}
    for a in payload.get("arms") or []:
        tags = a.get("tags") or {}
        name = tags.get("variant") or tags.get("combo") or tags.get("name") or ""
        if whole_card_donchian or "donchian" in str(name).lower():
            out[str(name)] = {
                "ann_pct": (a.get("common_window") or {}).get("ann_pct"),
                "sharpe": (a.get("common_window") or {}).get("sharpe"),
                "mdd_pct": (a.get("common_window") or {}).get("mdd_pct"),
                "verdict": a.get("verdict"),
            }
    return payload, out


def robust_pooled_verdict(arms):
    """Verbatim copy of bench_generic.run_cell's robust branch."""
    if not arms:
        return "DATA_BLOCKED"
    anns = [a["common_window"]["ann_pct"] for a in arms]
    mdes = [a["mde_pp"] for a in arms if a["mde_pp"]]
    signs = {1 if x > 0 else -1 for x in anns}
    stable = len(signs) == 1 and mdes and min(abs(x) for x in anns) > max(mdes)
    return ("STABLE_POSITIVE" if stable and 1 in signs
            else ("STABLE_NEGATIVE" if stable else "UNSTABLE_ACROSS_PARAMS"))


def run_generic_card(cell_id, cfg, panel, dates, closes, rets, vols, split):
    """Census and robust cells, each under every unit method."""
    result = {"cell": cell_id, "type": cfg.get("type"), "rule": cfg.get("rule"),
              "products": sorted(cfg.get("products") or bc.FUTURES),
              "methods": {}, "published": {}, "donchian": []}
    pub_payload, pub_arms = published_donchian_arms(
        cell_id, whole_card_donchian=(cfg.get("rule") == "donchian"))
    result["published"] = {
        "verdict": (pub_payload or {}).get("verdict"),
        "generated": (pub_payload or {}).get("generated"),
        "evidence_cutoff": (pub_payload or {}).get("evidence_cutoff"),
        "donchian_arms": pub_arms,
    }

    for method in METHODS:
        highs, lows = repaired_highs_lows(panel, closes, method)
        if cfg.get("type") == "census":
            cen = bg.run_census(cfg, panel, dates, closes, rets, vols, highs, lows, split)
            rows = cen.get("rows") or []
            result["methods"][method] = {
                "verdict": cen.get("verdict"),
                "n_combos": cen.get("n_combos"),
                "n_powered": cen.get("n_powered"),
                "median_ann_pct": cen.get("median_ann_pct"),
                "best_powered": cen.get("best_powered"),
                "worst_powered": cen.get("worst_powered"),
                "donchian_rows": [r for r in rows if str(r.get("combo", "")).startswith("donchian")],
            }
        elif cfg.get("type") == "robust":
            arms = []
            for v in cfg.get("variants") or []:
                sub = dict(cfg)
                sub["params"] = dict(cfg.get("params") or {}, **(v.get("params") or {}))
                if v.get("long_only") is not None:
                    sub["long_only"] = v["long_only"]
                arm = bg.run_arm(sub, panel, dates, closes, rets, vols, highs, lows, split,
                                 tags=v.get("tags") or {"variant": v.get("name")})
                if arm:
                    arms.append(arm)
            result["methods"][method] = {
                "verdict": robust_pooled_verdict(arms),
                "arms": [{"variant": (a["tags"].get("variant") or a["tags"].get("name")),
                          "ann_pct": a["common_window"]["ann_pct"],
                          "sharpe": a["common_window"]["sharpe"],
                          "mdd_pct": a["common_window"]["mdd_pct"],
                          "oos_ann_pct": a["oos_2024_after"]["ann_pct"],
                          "mde_pp": a["mde_pp"],
                          "powered": a["powered_for_target"],
                          "verdict": a["verdict"]} for a in arms],
            }
        else:
            raise ValueError(f"unsupported type {cfg.get('type')}")

    # per-arm before/after, plus the long share that names the defect
    if cfg.get("type") == "census":
        specs = [s for s in cfg.get("grid") or [] if s.get("rule") == "donchian"]
    else:
        specs = [{"rule": "donchian",
                  "params": dict(cfg.get("params") or {}, **(v.get("params") or {})),
                  "long_only": bool(v.get("long_only", cfg.get("long_only", False))),
                  "tags": v.get("tags") or {"variant": v.get("name")}}
                 for v in cfg.get("variants") or []]
    for spec in specs:
        sub = dict(cfg)
        sub["rule"] = "donchian"
        sub["params"] = spec.get("params") or {}
        sub["long_only"] = bool(spec.get("long_only", cfg.get("long_only", False)))
        label = (spec.get("tags") or {}).get("variant") or (
            "donchian|%s|%s" % (sub["params"], "long" if sub["long_only"] else "ls"))
        row = {"variant": label, "long_only": sub["long_only"],
               "params": sub["params"], "long_share": {}}
        for method in METHODS:
            highs, lows = repaired_highs_lows(panel, closes, method)
            arm = bg.run_arm(sub, panel, dates, closes, rets, vols, highs, lows, split,
                             tags={"variant": label})
            row["long_share"][method] = long_share(sub, closes, highs, lows)
            row[method] = None if not arm else {
                "ann_pct": arm["common_window"]["ann_pct"],
                "sharpe": arm["common_window"]["sharpe"],
                "mdd_pct": arm["common_window"]["mdd_pct"],
                "oos_ann_pct": arm["oos_2024_after"]["ann_pct"],
                "turnover": arm["turnover_per_year"],
                "mde_pp": arm["mde_pp"],
                "powered": arm["powered_for_target"],
                "verdict": arm["verdict"],
                "p_value": (arm.get("control") or {}).get("p_value"),
            }
        result["donchian"].append(row)

    # fidelity: does today's raw re-run agree with what the card printed?
    diffs = []
    for row in result["donchian"]:
        pub = result["published"]["donchian_arms"].get(row["variant"])
        today = row.get("raw_panel")
        if pub and today and pub.get("ann_pct") is not None and today.get("ann_pct") is not None:
            diffs.append({"variant": row["variant"], "published_ann_pct": pub["ann_pct"],
                          "today_raw_ann_pct": today["ann_pct"],
                          "diff_pp": round(today["ann_pct"] - pub["ann_pct"], 2)})
    result["fidelity"] = {
        "n_matched": len(diffs),
        "max_abs_diff_pp": round(max((abs(d["diff_pp"]) for d in diffs), default=0.0), 2),
        "over_tolerance": [d for d in diffs if abs(d["diff_pp"]) > FIDELITY_PP],
        "rows": diffs,
    }
    rolls = {}
    for c, df in panel.items():
        _, mask = bc.roll_adjusted_returns(df["close"].reindex(dates).values)
        rolls[c] = int(np.nansum(mask))
    result["roll_bars"] = {"per_product": rolls, "total": int(sum(rolls.values()))}
    return result


def run_fut_trend_card(panel, dates, closes, rets, vols, csi):
    """bench_fut_trend is a standalone runner; only its donchian arm is re-run.

    Its own thresholds (H1 6%, H2 4%/0.5, H4 2%, H5 0.05) and its own
    repackaged-beta addendum are applied by its own ``run_arm`` -- nothing here
    re-implements a rule.
    """
    vol_frame = pd.DataFrame(vols)
    live_count = vol_frame.notna().sum(axis=1)
    eligible = live_count[live_count >= 5].index
    common_start = eligible.min() if len(eligible) else dates[0]
    bh = ft.buy_and_hold(dates, closes, rets, vols, common_start)
    hold_ann = (bh or {}).get("common_window", {}).get("ann_pct")
    out = {"cell": "fut_trend", "type": "style_sheet", "products": sorted(panel),
           "published": {}, "methods": {}, "common_start": str(pd.Timestamp(common_start).date()),
           "hold_ann_pct": hold_ann, "long_only": False}
    pub = bc.read_json(os.path.join(bc.RESULTS, "bench_fut_trend.json"), {}) or {}
    out["published"] = {
        "verdict": (pub.get("verdict") or {}).get("donchian"),
        "generated": pub.get("generated"),
        "vs_hold": (pub.get("vs_hold") or {}).get("donchian"),
        "arm_ann_pct": next((a.get("common_window", {}).get("ann_pct")
                             for a in pub.get("arms") or []
                             if a.get("style") == "donchian"), None),
    }
    for method in METHODS:
        highs, lows = repaired_highs_lows(panel, closes, method)
        sigs = ft.sig_donchian(closes, highs, lows)
        arm = ft.run_arm("donchian", sigs, dates, closes, rets, vols, csi, common_start)
        if not arm:
            out["methods"][method] = None
            continue
        excess = None if hold_ann is None else round(arm["common_window"]["ann_pct"] - hold_ann, 2)
        verdict = arm["verdict"]
        if verdict == "GO" and excess is not None and excess < 2.0:
            verdict = "NO_EDGE_REPACKAGES_BETA"
        up = sum(int((s.dropna().values > 0).sum()) for s in sigs.values())
        dn = sum(int((s.dropna().values < 0).sum()) for s in sigs.values())
        out["methods"][method] = {
            "ann_pct": arm["common_window"]["ann_pct"],
            "sharpe": arm["common_window"]["sharpe"],
            "mdd_pct": arm["common_window"]["mdd_pct"],
            "oos_ann_pct": (arm.get("oos_2024_after") or {}).get("ann_pct"),
            "turnover": arm.get("turnover_per_year"),
            "p_value": (arm.get("control") or {}).get("p_value"),
            "checks": arm.get("checks"),
            "excess_vs_hold_pp": excess,
            "verdict": verdict,
            "long_share": None if not (up + dn) else round(up / (up + dn), 4),
        }
    rolls = {}
    for c, df in panel.items():
        _, mask = bc.roll_adjusted_returns(df["close"].reindex(dates).values)
        rolls[c] = int(np.nansum(mask))
    out["roll_bars"] = {"per_product": rolls, "total": int(sum(rolls.values()))}
    raw_arm = (out["methods"] or {}).get("raw_panel") or {}
    out["fidelity"] = {
        "n_matched": 1 if out["published"].get("arm_ann_pct") is not None else 0,
        "max_abs_diff_pp": (None if out["published"].get("arm_ann_pct") is None
                            or raw_arm.get("ann_pct") is None
                            else round(raw_arm["ann_pct"] - out["published"]["arm_ann_pct"], 2)),
    }
    return out


# --------------------------------------------------------------------------
# readings
# --------------------------------------------------------------------------
def verdict_flips(cards):
    flips = []
    for name, card in cards.items():
        methods = card.get("methods") or {}
        base = (methods.get("raw_panel") or {}).get("verdict")
        after = (methods.get("per_bar") or {}).get("verdict")
        first = (methods.get("first_close") or {}).get("verdict")
        if base is None or after is None:
            continue
        flips.append({"card": name, "raw_panel": base, "per_bar": after,
                      "first_close": first,
                      "flips": bool(after != base),
                      "published": (card.get("published") or {}).get("verdict")})
    return flips


def repair_fork(cards):
    """The widest gap between the two candidate repairs, arm by arm.

    If the choice of repair decides the answer, that has to be printed as a
    reading of its own -- a reader who only sees "the best arm" would take
    whichever repair flatters the book.
    """
    widest = None
    for name, card in cards.items():
        if card.get("type") == "style_sheet":
            pb = (card.get("methods") or {}).get("per_bar") or {}
            fc = (card.get("methods") or {}).get("first_close") or {}
            pairs = [("donchian", pb, fc)]
        else:
            pairs = [(row["variant"], row.get("per_bar") or {}, row.get("first_close") or {})
                     for row in card.get("donchian") or []]
        for variant, a, b in pairs:
            if a.get("ann_pct") is None or b.get("ann_pct") is None:
                continue
            gap = round(b["ann_pct"] - a["ann_pct"], 2)
            if widest is None or abs(gap) > abs(widest["gap_pp"]):
                widest = {"card": name, "variant": variant, "gap_pp": gap,
                          "per_bar": a, "first_close": b}
    return widest


def money_line(cards):
    """Best corrected donchian arm across the re-run cards, and what it beats."""
    best = None
    for name, card in cards.items():
        for row in card.get("donchian") or []:
            after = row.get("per_bar")
            if not after or after.get("ann_pct") is None or not after.get("powered"):
                continue
            if best is None or after["ann_pct"] > best["ann_pct"]:
                best = {"card": name, "variant": row["variant"],
                        "ann_pct": after["ann_pct"], "sharpe": after["sharpe"],
                        "mdd_pct": after["mdd_pct"], "oos_ann_pct": after["oos_ann_pct"],
                        "mde_pp": after["mde_pp"], "verdict": after["verdict"]}
    go = []
    for name, card in cards.items():
        for row in card.get("donchian") or []:
            after = row.get("per_bar")
            if after and after.get("verdict") == "GO":
                go.append({"card": name, "variant": row["variant"], **after})
        if card.get("type") == "style_sheet":
            after = (card.get("methods") or {}).get("per_bar")
            if after and after.get("verdict") == "GO":
                go.append({"card": name, "variant": "donchian", **after})
    return {"best_powered_corrected_arm": best, "go_after_repair": go}


# --------------------------------------------------------------------------
# page
# --------------------------------------------------------------------------
def fmt_pct(v):
    return "—" if v is None else f"{v:+.2f}%"


def render_md(payload):
    lines = []
    flips = payload["verdict_flips"]
    moved = [f for f in flips if f["flips"]]
    money = payload["money"]
    best = money["best_powered_corrected_arm"]
    lines += [f"# 把高低价换回收盘的单位之后，这些卡翻不翻", "",
              f"cell `{CELL}` · cutoff **{payload['evidence_cutoff']}** · "
              f"生成 {payload['generated']}", "",
              "r2142 找出毛病（突破规则拿“调整后的收盘指数”跟“原始价位高低价”比），"
              "r2143 量出它只坏了一条规则。这一件回答后面那个真正会改决策的问题："
              "**单位修好之后，有哪张卡的判词会翻？钱会不会冒出来？**", "",
              "做法：同一份今天的面板，只换高低价的单位，其余（成本 3bp/边、波动目标、"
              "样本外切点 2024-01-01、判据、随机对照 100 次同种子）全部不动。"
              "发布的卡片数字并列印出，只作忠实度核对——面板比那些卡生成时已经长了两天。", "",
              "## 一句话", "",
              f"- 修好单位之后**判词翻面的卡：{len(moved)}/{len(flips)}**"
              + ("（" + "、".join(f"{m['card']}: {m['raw_panel']} → {m['per_bar']}" for m in moved) + "）"
                 if moved else "——没有一张卡因为修单位而变成新的结论"),
              f"- 修好之后最好的可分辨臂："
              + (f"**{fmt_pct(best['ann_pct'])} / 夏普 {best['sharpe']} / 回撤 {fmt_pct(best['mdd_pct'])}**"
                 f"（`{best['card']}` · `{best['variant']}` · MDE {best['mde_pp']}pp）"
                 if best else "**没有一条可分辨**"),
              f"- 够格上钱（判词 GO）的臂：**{len(money['go_after_repair'])} 条**"
              + ("（" + "、".join(f"{g['card']}/{g['variant']}" for g in money["go_after_repair"]) + "）"
                 if money["go_after_repair"] else "——修好单位只是让它能往两边做，并没有把噪声变成边际"),
              ""]
    fork = payload.get("repair_fork") or {}
    if fork:
        pb, fc = fork["per_bar"], fork["first_close"]
        lines += ["## 两种修法给出相反的答案（本轮最重要的一条）", "",
                  f"同一条规则、同一份面板、同一套成本，只因为“把换月跳空怎么处理”不同，"
                  f"`{fork['card']}` 的 `{fork['variant']}` 相差 **{fork['gap_pp']:+.2f}pp/年**：", "",
                  "| 修法 | 做多占比 | 年化 | 夏普 | 回撤 | 样本外 | 随机对照 p | 判词 |",
                  "|---|---|---|---|---|---|---|---|",
                  f"| `per_bar` | {pb.get('long_share')} | {fmt_pct(pb.get('ann_pct'))} | {pb.get('sharpe')} | "
                  f"{fmt_pct(pb.get('mdd_pct'))} | {fmt_pct(pb.get('oos_ann_pct'))} | {pb.get('p_value')} | "
                  f"**{pb.get('verdict')}** |",
                  f"| `first_close` | {fc.get('long_share')} | {fmt_pct(fc.get('ann_pct'))} | {fc.get('sharpe')} | "
                  f"{fmt_pct(fc.get('mdd_pct'))} | {fmt_pct(fc.get('oos_ann_pct'))} | {fc.get('p_value')} | "
                  f"**{fc.get('verdict')}** |",
                  "",
                  "**不能按哪个数好看选哪个修法。** 定这次口径的不是收益，是收益面本来怎么算的："
                  "`bench_core.roll_adjusted_returns` 已经把换月跳空从收益里剔掉（跳空那根 bar 的收益记 0），"
                  "所以任何“能拿到的收益”都不包含跳空。若通道里仍保留跳空（`first_close`），"
                  "规则就会对着一个**在收益里不存在**的价格跳空做决定——这类信号天然不可实现。"
                  "因此本件采 `per_bar`（乘子 = 同 bar 调整价/原始价，逐 bar 变化，正好抵消跳空），"
                  "`first_close` 只作敏感性并列，不推荐。", ""]
    lines += ["## 方法：三种单位，同一个面板", "",
              "| 方法 | 怎么算 | 意思 |", "|---|---|---|"]
    for m in METHODS:
        lines.append(f"| `{m}` | {METHOD_WHAT[m]} | "
                     + ("发布口径（有缺陷）" if m == "raw_panel" else "候选修法") + " |")
    lines += ["", "两种修法不是同一个答案：`per_bar` 的乘子随换月变化，"
              "把“已在收盘序列里剔除的换月跳空”同样从高低价里剔掉；`first_close` 一个品种一个常数，"
              "高低价里仍带着换月跳空。表格里两列并列，读者自己看差多大。", "",
              "## 逐卡读数", "",
              "### 判词", "",
              "| 卡 | 发布判词 | 今天·原始高低价 | `per_bar` | `first_close` | 翻面? |",
              "|---|---|---|---|---|---|"]
    for f in flips:
        lines.append(f"| `{f['card']}` | {f['published']} | {f['raw_panel']} | {f['per_bar']} | "
                     f"{f['first_close']} | **{'翻' if f['flips'] else '不翻'}** |")
    lines += ["", "### 每条 donchian 臂：做多占比（缺陷的指纹）", "",
              "| 卡 | 臂 | 原始做多占比 | `per_bar` | 原始年化 | `per_bar` 年化 | `first_close` 年化 | 可分辨? | 判词(`per_bar`) |",
              "|---|---|---|---|---|---|---|---|---|"]
    for name, card in payload["cards"].items():
        for row in card.get("donchian") or []:
            raw = row.get("raw_panel") or {}
            pb = row.get("per_bar") or {}
            fc = row.get("first_close") or {}
            lines.append(
                f"| `{name}` | {row['variant']} | {row['long_share'].get('raw_panel')} | "
                f"{row['long_share'].get('per_bar')} | {fmt_pct(raw.get('ann_pct'))} | "
                f"{fmt_pct(pb.get('ann_pct'))} | {fmt_pct(fc.get('ann_pct'))} | "
                f"{pb.get('powered')} | **{pb.get('verdict')}** |")
    if payload.get("fut_trend"):
        ftc = payload["fut_trend"]
        lines += ["", "### `bench_fut_trend` 的第五条风格（同一个毛病，另一份脚本）", "",
                  f"它自己那套判据（H1 6% / H2 4%+0.5 / H4 2% / H5 0.05）和"
                  f"“必须赢过同篮子持有 2pp”的追加条款原样沿用，"
                  f"同篮子持有年化 {fmt_pct(ftc.get('hold_ann_pct'))}。", "",
                  "| 方法 | 做多占比 | 年化 | 夏普 | 回撤 | 样本外 | 相对持有 | 判词 |",
                  "|---|---|---|---|---|---|---|---|"]
        for m in METHODS:
            a = (ftc.get("methods") or {}).get(m)
            if not a:
                lines.append(f"| `{m}` | — | — | — | — | — | — | 无臂 |")
                continue
            lines.append(f"| `{m}` | {a['long_share']} | {fmt_pct(a['ann_pct'])} | {a['sharpe']} | "
                         f"{fmt_pct(a['mdd_pct'])} | {fmt_pct(a['oos_ann_pct'])} | "
                         f"{fmt_pct(a['excess_vs_hold_pp'])} | **{a['verdict']}** |")
    lines += ["", "## 忠实度（我们能不能重跑出发布过的数）", ""]
    for name, card in payload["cards"].items():
        fid = card.get("fidelity") or {}
        over = fid.get("over_tolerance") or []
        diff = fid.get("max_abs_diff_pp")
        lines.append(f"- `{name}`：对上 {fid.get('n_matched')} 条，最大差 "
                     + ("—" if diff is None else f"{diff}pp")
                     + ("；超差：" + "、".join(f"{o['variant']}={o['diff_pp']}pp" for o in over)
                        if over else "；无一条超 1pp"))
    lines += ["", "面板延伸到今天，所以差几个零点几本来就是预期的；真差到 pp 级才是分歧。", "",
              "## 换月面：两种修法分歧的来源", ""]
    for name, card in payload["cards"].items():
        rb = card.get("roll_bars") or {}
        if not rb:
            continue
        per = rb.get("per_product") or {}
        lines.append(f"- `{name}`：共 **{rb.get('total')}** 根 bar 被 `bench_core` 判为换月"
                     f"（判据 8× 中位绝对变动且 >0.5%），逐品种 "
                     + "、".join(f"{k}={v}" for k, v in sorted(per.items(), key=lambda kv: -kv[1]))
                     + "。这些 bar 就是 `first_close` 把跳空留回通道、`per_bar` 把它抵消掉的地方。")
    lines += ["", "## 射程与未验证（如实）", "",
              "1. 本件**不改** `bench_generic.sig_donchian`、不改任何已发布卡片，也不应用判词翻面——"
              "修共享代码面需要无竞争窗（本轮同宿主在写共享面，只落新增文件）。",
              "2. 单位修好只解决“能不能做多”。`per_bar` 里乘子来自同一根 bar 的收盘，"
              "而每根 bar 的 high/low 是真实成交区间，滚动窗口跨换月时窗口内仍然是不同合约的价位；"
              "更严格的修法是回测层面用后复权连续合约，属数据面工程，不在本件射程。",
              "3. 随机对照是同一组权重换符号（`bench_core.random_sign_control`，100 次、同种子），"
              "它检验的是“方向是否比乱摆强”，不检验入场时点。",
              "4. 修正后的 MDE 与可分辨性沿用卡片自己的目标边际（5pp / fut_trend 自带 6pp 档），"
              "本件没有重新标定门槛。",
              "5. 口径选定 `per_bar` 的理由是“收益面已剔除换月跳空，信号面不能对着跳空决策”，"
              "这是口径论证，不是收益论证；`first_close` 的数字并列印出正是为了让读者看到"
              "“按钱选口径”会把一条死风格抬成 4/5 门候选。",
              "6. 判词翻面只报不应用：`census_commodity` 从 MIXED 翻到 LEANS_POSITIVE 的意思是"
              "“这个空间里可分辨的臂全是正的”，**不等于**有一本书可以上钱——最好的可分辨臂 "
              "年化 3.41%、回撤 -35.21%，自己那五道门一条都没全过。",
              "", "## 下一手", "",
              "- 无竞争窗时：把 `sig_donchian` 的输入改到同一套单位（推荐 `per_bar`），"
              "重跑 `census_commodity` / `census_index_futures` / `robust_donchian_index` / `bench_fut_trend` 四张卡，"
              "并把 r2140 答卷册与 r2141 去重面重 derive（它们把 14 行缺陷臂算成 EXHAUSTED 证据）。",
              "- 把「新信号族必须过单位扰动」做成冒烟腿（r2143 已给判据，本件给的是它翻不了判词的证据）。",
              ""]
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------
# checks
# --------------------------------------------------------------------------
def check(payload):
    fails = []
    cards = payload.get("cards") or {}
    if not cards:
        fails.append("no cards re-run")
    for name, card in cards.items():
        methods = card.get("methods") or {}
        for m in METHODS:
            if m not in methods:
                fails.append(f"{name}: missing method {m}")
        if card.get("type") == "style_sheet":
            # bench_fut_trend carries one donchian arm across the whole sheet
            for m, a in methods.items():
                if a is not None and a.get("ann_pct") is None:
                    fails.append(f"{name}/{m}: arm has no annualised reading")
            continue
        rows = card.get("donchian") or []
        if not rows:
            fails.append(f"{name}: no donchian arm")
        for row in rows:
            for m in METHODS:
                if row.get(m) is None and row["long_share"].get(m) is None:
                    fails.append(f"{name}/{row['variant']}: no reading under {m}")
            if row["long_share"].get("raw_panel") not in (0.0, 0, None):
                fails.append(f"{name}/{row['variant']}: raw panel is not all-short "
                             f"(long_share={row['long_share'].get('raw_panel')}) -- the defect "
                             f"signature changed, re-read r2142 before trusting this page")
        fid = card.get("fidelity") or {}
        if (fid.get("max_abs_diff_pp") or 0) > 3.0:
            fails.append(f"{name}: faithful re-run differs from the published card by "
                         f"{fid['max_abs_diff_pp']}pp -- not the same pipeline any more")
    flips = payload.get("verdict_flips") or []
    for f in flips:
        card = cards.get(f["card"]) or {}
        base = ((card.get("methods") or {}).get("raw_panel") or {}).get("verdict")
        after = ((card.get("methods") or {}).get("per_bar") or {}).get("verdict")
        if (f["raw_panel"], f["per_bar"]) != (base, after):
            fails.append(f"{f['card']}: flip table disagrees with the card")
    best = (payload.get("money") or {}).get("best_powered_corrected_arm")
    pool = [row["per_bar"]["ann_pct"] for card in cards.values()
            for row in (card.get("donchian") or [])
            if row.get("per_bar") and row["per_bar"].get("powered")
            and row["per_bar"].get("ann_pct") is not None]
    if best and pool and abs(best["ann_pct"] - max(pool)) > 1e-9:
        fails.append("money line did not pick the best powered corrected arm")
    fork = payload.get("repair_fork") or {}
    if fork:
        pb = (fork.get("per_bar") or {}).get("ann_pct")
        fc = (fork.get("first_close") or {}).get("ann_pct")
        if pb is None or fc is None:
            fails.append("repair fork is missing one of its two legs")
        elif abs(round(fc - pb, 2) - fork["gap_pp"]) > 1e-9:
            fails.append(f"repair fork gap {fork['gap_pp']} does not equal the two printed legs")
    return fails


# --------------------------------------------------------------------------
# selftest
# --------------------------------------------------------------------------
def _toy_panel(n=160, base=3000.0, roll_at=80, jump=1.08):
    """Raw price space with one roll, plus the adjusted index bench_core builds.

    ``bench_core.align_futures`` hands the rule the adjusted series and the raw
    high/low, so the toy has to hold both: a price series that jumps at the roll
    and an index that does not.
    """
    idx = pd.bdate_range("2020-01-02", periods=n)
    t = np.arange(n)
    rets = 0.002 + 0.01 * np.sin(t / 9.0)
    rets[roll_at] = 0.0                      # the contract changed; no return
    price = base * np.cumprod(np.concatenate([[1.0], 1.0 + rets[1:]]))
    price[roll_at:] *= jump                  # the raw quote jumps, the index does not
    adj = np.cumprod(np.concatenate([[1.0], 1.0 + rets[1:]]))
    return idx, price, adj


def selftest():
    legs, fails = [], []

    def leg(name, ok, detail=""):
        legs.append({"leg": name, "ok": bool(ok), "detail": detail})
        if not ok:
            fails.append(f"{name}: {detail}")

    idx, price, adj = _toy_panel()
    df = pd.DataFrame({"close": price, "high": price * 1.01, "low": price * 0.99}, index=idx)
    closes = {"X": pd.Series(adj, index=idx)}
    panel = {"X": df}
    cfg = {"rule": "donchian", "params": {"entry": 20, "exit": 10}, "long_only": False}

    hi_raw, lo_raw = repaired_highs_lows(panel, closes, "raw_panel")
    share_raw = long_share(cfg, closes, hi_raw, lo_raw)
    hi_pb, lo_pb = repaired_highs_lows(panel, closes, "per_bar")
    share_pb = long_share(cfg, closes, hi_pb, lo_pb)
    leg("raw units never go long (the defect's signature)", share_raw == 0.0, f"long_share={share_raw}")
    leg("per-bar repair trades both ways", (share_pb or 0) > 0.0, f"long_share={share_pb}")

    # alignment: the repair may not shift the bar it prices off
    ratio_pb = (hi_pb["X"] / closes["X"]).dropna()
    ratio_true = (df["high"] / df["close"]).dropna()
    worst = float((ratio_pb - ratio_true).abs().max())
    leg("per-bar repair keeps high/close on the same bar", worst < 1e-9, f"max abs diff {worst:.3e}")

    # the two repairs are NOT the same answer: first_close carries the roll jump
    hi_fc, lo_fc = repaired_highs_lows(panel, closes, "first_close")
    r_fc = (hi_fc["X"] / closes["X"]).dropna()
    before = float(r_fc.iloc[70]) if len(r_fc) > 71 else None
    after = float(r_fc.iloc[-1])
    leg("first-close repair leaves the roll jump in the channel",
        before is not None and after / before > 1.05, f"{before:.4f} -> {after:.4f}")

    scaled_panel = {"X": df.assign(close=df["close"] * 2.0,
                                   high=df["high"] * 2.0, low=df["low"] * 2.0)}
    scaled_closes = {"X": closes["X"] * 2.0}
    hi_s, lo_s = repaired_highs_lows(scaled_panel, scaled_closes, "per_bar")
    sig_a = bg.sig_donchian(closes, hi_pb, lo_pb, 20, 10)
    sig_b = bg.sig_donchian(scaled_closes, hi_s, lo_s, 20, 10)
    same = bool(sig_a["X"].fillna(0).equals(sig_b["X"].fillna(0)))
    leg("scaling the whole price space leaves the signal unchanged", same)

    leg("robust pooled rule: one sign and clear of MDE -> stable",
        robust_pooled_verdict([{"common_window": {"ann_pct": 6.0}, "mde_pp": 3.0},
                               {"common_window": {"ann_pct": 4.0}, "mde_pp": 3.0}]) == "STABLE_POSITIVE")
    leg("robust pooled rule: signs disagree -> unstable",
        robust_pooled_verdict([{"common_window": {"ann_pct": 6.0}, "mde_pp": 3.0},
                               {"common_window": {"ann_pct": -4.0}, "mde_pp": 3.0}]) == "UNSTABLE_ACROSS_PARAMS")
    leg("robust pooled rule: inside MDE -> unstable, not a win",
        robust_pooled_verdict([{"common_window": {"ann_pct": 1.0}, "mde_pp": 5.0}]) == "UNSTABLE_ACROSS_PARAMS")

    s = bg.sig_donchian({"X": pd.Series([100.0, 110.0, 105.0, 90.0, 100.0])},
                        {"X": pd.Series([101.0, 101.0, 111.0, 106.0, 95.0])},
                        {"X": pd.Series([99.0, 99.0, 104.0, 95.0, 89.0])}, 2, 2)
    # 105 breaks the 2-bar high -> long; 90 breaks the low -> short; 100 sits
    # inside both channels and holds the short. 0 (no position) is dropped.
    leg("donchian semantics pinned (1 = long, -1 = short, 0 dropped)",
        list(s["X"].fillna(0.0).values) == [0.0, 0.0, 1.0, -1.0, -1.0],
        str(list(s["X"].values)))

    bad = check({"cards": {"c": {"methods": {m: {} for m in METHODS},
                                "donchian": [{"variant": "v", "long_share": {"raw_panel": 0.42},
                                              "raw_panel": {}, "per_bar": {}, "first_close": {}}]}},
                 "verdict_flips": [], "money": {}})
    leg("check() reports a broken defect signature instead of passing",
        any("defect signature" in f for f in bad), str(bad[:1]))

    return {"legs": legs, "passed": sum(1 for x in legs if x["ok"]), "total": len(legs),
            "fails": fails}


# --------------------------------------------------------------------------
# run
# --------------------------------------------------------------------------
def run():
    bc.weight_priority()
    out = {}
    cards = {}
    generic = ["census_commodity", "census_index_futures", "robust_donchian_index"]
    panels = {}
    align = {}
    for cell_id in generic:
        cfg = load_cell_config(cell_id)
        if not cfg:
            continue
        key = tuple(sorted(cfg.get("products") or bc.FUTURES))
        if key not in panels:
            panels[key] = bc.load_futures_products(list(key))
            align[key] = bc.align_futures(panels[key])
        panel = panels[key]
        dates, closes, rets, vols = align[key]
        cards[cell_id] = run_generic_card(cell_id, cfg, panel, dates, closes, rets, vols,
                                          cfg.get("split", "2024-01-01"))

    ft_panel = bc.load_futures_products()
    ft_dates, ft_closes, ft_rets, ft_vols = bc.align_futures(ft_panel)
    fut_trend = run_fut_trend_card(ft_panel, ft_dates, ft_closes, ft_rets, ft_vols,
                                   bc.load_index_close("sh000300"))
    cards["fut_trend"] = fut_trend

    cutoff = str(pd.Timestamp(ft_dates[-1]).date())
    payload = {
        "cell": CELL,
        "generated": pd.Timestamp.now(tz="Asia/Shanghai").isoformat(timespec="seconds"),
        "evidence_cutoff": cutoff,
        "question": "把 donchian 的高低价换到收盘的同一套单位之后，哪些卡的判词会翻？钱会不会出现？",
        "defect": {
            "what": "sig_donchian compares an adjusted-close index against raw high/low prices",
            "found_by": "r2142 (scripts/bench_donchian_unit_audit.py)",
            "how_wide": "r2143 (scripts/bench_signal_scale_invariance.py): 8 of 11 families unchanged",
            "signature": "the long side never triggers, because raw prices are 96x-6980x the index",
        },
        "methods": {m: METHOD_WHAT[m] for m in METHODS},
        "cards": cards,
        "fut_trend": fut_trend,
        "verdict_flips": verdict_flips(cards),
        "repair_fork": repair_fork(cards),
        "money": money_line(cards),
    }
    payload["repair_effect"] = {
        "cards_with_flip": [f["card"] for f in payload["verdict_flips"] if f["flips"]],
        "cards_unchanged": [f["card"] for f in payload["verdict_flips"] if not f["flips"]],
        "any_go_after_repair": bool(payload["money"]["go_after_repair"]),
    }
    payload["checks"] = check(payload)
    payload["selftest"] = selftest()
    bc.write_json(OUT_JSON, payload)
    with open(OUT_MD, "w", encoding="utf-8", newline="\n") as f:
        f.write(render_md(payload))
    print(json.dumps({"ok": not payload["checks"] and not payload["selftest"]["fails"],
                      "card_flips": payload["repair_effect"]["cards_with_flip"],
                      "any_go": payload["repair_effect"]["any_go_after_repair"],
                      "selftest": f"{payload['selftest']['passed']}/{payload['selftest']['total']}",
                      "checks": payload["checks"],
                      "json": os.path.relpath(OUT_JSON, bc.ROOT),
                      "md": os.path.relpath(OUT_MD, bc.ROOT)}, ensure_ascii=False, indent=1))
    return payload


def verify():
    """Re-derive and compare with the published face, ignoring only `generated`."""
    published = bc.read_json(OUT_JSON, None)
    if not published:
        print(json.dumps({"ok": False, "error": "no published face"}, ensure_ascii=False))
        return 2
    fresh = run()
    a = dict(published)
    b = dict(fresh)
    for d in (a, b):
        d.pop("generated", None)
    same = json.dumps(a, sort_keys=True, ensure_ascii=False, default=str) == \
        json.dumps(b, sort_keys=True, ensure_ascii=False, default=str)
    print(json.dumps({"ok": same, "verdict": "MATCH" if same else "MISMATCH"}, ensure_ascii=False))
    return 0 if same else 3


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run")
    a, unknown = ap.parse_known_args()
    a.cmd = (a.cmd or "run").lstrip("-")   # accept both `--selftest` and `selftest`
    for u in unknown:                      # `--selftest` arrives here, not in cmd
        cand = u.lstrip("-")
        if cand in ("run", "check", "selftest", "verify"):
            a.cmd = cand
    if a.cmd not in ("run", "check", "selftest", "verify"):
        print(json.dumps({"ok": False, "error": f"unknown command {a.cmd}"}, ensure_ascii=False))
        return 2
    if a.cmd == "run":
        payload = run()
        return 0 if not payload["checks"] and not payload["selftest"]["fails"] else 1
    if a.cmd == "selftest":
        st = selftest()
        for l in st["legs"]:
            print(f"[{'PASS' if l['ok'] else 'FAIL'}] {l['leg']}"
                  + (f" | {l['detail']}" if l["detail"] else ""))
        print(json.dumps({"passed": st["passed"], "total": st["total"]}, ensure_ascii=False))
        return 0 if not st["fails"] else 1
    if a.cmd == "check":
        payload = bc.read_json(OUT_JSON, None)
        if not payload:
            print(json.dumps({"ok": False, "error": "no face"}, ensure_ascii=False))
            return 2
        fails = check(payload)
        st = payload.get("selftest") or {}
        print(json.dumps({"ok": not fails, "failures": fails,
                          "selftest": f"{st.get('passed')}/{st.get('total')}"},
                         ensure_ascii=False, indent=1))
        return 0 if not fails else 3
    return verify()


if __name__ == "__main__":
    sys.exit(main())
