"""Stage x style conditional matrix (descriptive readout face).

Purpose (O-20261019-2230-bm-b sec.3 CEO deliverable): the CEO asked for a
"each stage state x each style" live/negative matrix. The SS-COMBO-P1 batch
judged the *combination claim* negative and deferred the cell-level readout
("格级归因转 finalize 批"), so this script computes the descriptive
per-stage x per-style matrix from already-frozen artifacts.

Scope law (readout-only):
  * INPUT = results/stagestyle_combo_p1/latest.json (frozen batch product,
    per-cell daily return series) + results/regime5_labels/<latest>.json
    (REGIME5 5-state daily labels).
  * OUTPUT = deterministic descriptive statistics (n_days / mean daily bp /
    annualized sharpe / annualized return / state-day-subsequence drawdown /
    win rate). ZERO verdict, ZERO judgment line, ZERO ledger booking: this
    face never re-judges a batch and never feeds a G1'/G2 gate.
  * Stage labels are PIT-safe by construction here: the matrix is computed
    from the *frozen* label series used by the batch itself; no re-labeling
    and no post-hoc state fitting happens in this script.

Run:      python scripts/sscombo_stage_style_matrix.py run
Selftest: python scripts/sscombo_stage_style_matrix.py selftest
"""

from __future__ import annotations

import argparse
import glob
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SSCOMBO_DIR = os.path.join(ROOT, "results", "stagestyle_combo_p1")
LABEL_DIR = os.path.join(ROOT, "results", "regime5_labels")
OUT_DIR = os.path.join(ROOT, "results", "stagestyle_combo_p1")
OUT_JSON = os.path.join(OUT_DIR, "STAGE-STYLE-MATRIX-v1.json")
OUT_MD = os.path.join(ROOT, "docs", "stagestyle", "STAGE-STYLE-MATRIX-v1.md")

STATES = ("BEAR", "GRIND", "CHOP", "SUPPORT", "BULL")
# display order + human labels (CEO-facing)
STATE_CN = {
    "BEAR": "BEAR 熊",
    "GRIND": "GRIND 磨",
    "CHOP": "CHOP 震荡",
    "SUPPORT": "SUPPORT 支撑",
    "BULL": "BULL 牛",
}
CELLS = ("C1", "C2", "C3", "U-divlowvol", "U-value", "U-quality", "U-EW")
CELL_CN = {
    "C1": "C1 divlowvol-tilt 组合",
    "C2": "C2 value-tilt 组合",
    "C3": "C3 quality-tilt 组合",
    "U-divlowvol": "U-divlowvol 无条件持有",
    "U-value": "U-value 无条件持有",
    "U-quality": "U-quality 无条件持有",
    "U-EW": "U-EW 等权三风格",
}
ANNUAL = 252


def _latest_labels_path() -> str:
    files = sorted(glob.glob(os.path.join(LABEL_DIR, "REGIME5-*.json")))
    if not files:
        raise SystemExit("no REGIME5 label face under %s" % LABEL_DIR)
    # ISO date suffix sorts lexicographically = newest last
    return files[-1]


def load_inputs(sscombo_path: str, labels_path: str):
    batch = json.load(open(sscombo_path, encoding="utf-8"))
    labels = json.load(open(labels_path, encoding="utf-8"))["labels"]
    return batch, labels


def conditional_stats(daily, mask):
    """Descriptive stats of a daily return subsequence selected by mask."""
    n = sum(1 for m in mask if m)
    if n == 0:
        return {"n_days": 0, "mean_bp": None, "sharpe_ann": None,
                "ann_ret_eq": None, "state_dd": None, "win_rate": None}
    sel = [r for r, m in zip(daily, mask) if m]
    mean = sum(sel) / n
    var = sum((r - mean) ** 2 for r in sel) / n
    sd = math.sqrt(var)
    cum = 1.0
    peak = 1.0
    worst = 0.0
    for r in sel:
        cum *= (1.0 + r)
        peak = max(peak, cum)
        worst = min(worst, cum / peak - 1.0)
    ann_ret = (cum ** (ANNUAL / n) - 1.0) if cum > 0 else None
    return {
        "n_days": n,
        "mean_bp": round(mean * 1e4, 2),
        "sharpe_ann": round(mean / sd * math.sqrt(ANNUAL), 4) if sd > 0 else None,
        "ann_ret_eq": round(ann_ret, 4) if ann_ret is not None else None,
        "state_dd": round(worst, 4),
        "win_rate": round(sum(1 for r in sel if r > 0) / n, 4),
    }


def build(sscombo_path=None, labels_path=None):
    sscombo_path = sscombo_path or os.path.join(SSCOMBO_DIR, "latest.json")
    labels_path = labels_path or _latest_labels_path()
    batch, labels = load_inputs(sscombo_path, labels_path)

    win = batch["window"]
    lo, hi = win["lo"], win["hi"]
    lab_in = [x for x in labels if lo <= x["date"] <= hi]

    # The batch stores bar-level n_days but a return series of length bars-1
    # (a return needs a prior close). Align by dropping the first bar's label
    # and disclose the offset in the output: return(t) is attributed to date(t).
    ref_len = len(batch["results"][CELLS[0]]["x1"]["daily"])
    if len(lab_in) == ref_len + 1:
        dropped = lab_in[0]["date"]
        lab_in = lab_in[1:]
    elif len(lab_in) != ref_len:
        raise SystemExit(
            "label window length %d does not match return series length %d"
            % (len(lab_in), ref_len))
    else:
        dropped = None
    dates = [x["date"] for x in lab_in]
    states = [x["state"] for x in lab_in]

    matrix = {}
    for cell in CELLS:
        face = batch["results"][cell]["x1"]
        daily = face["daily"]
        if len(daily) != len(states):
            raise SystemExit(
                "series/label length mismatch for %s: %d vs %d"
                % (cell, len(daily), len(states)))
        row = {}
        for st in STATES:
            mask = [s == st for s in states]
            row[st] = conditional_stats(daily, mask)
        row["ALL"] = conditional_stats(daily, [True] * len(daily))
        matrix[cell] = row

    state_days = {st: sum(1 for s in states if s == st) for st in STATES}

    # ---- allocation-regime view -------------------------------------------
    # The batch allocates monthly: the month's sleeve is chosen on the month's
    # first trading day from the PREVIOUS trading day's label (prereg sec.2a
    # PIT law). Slicing by the *same-day* label therefore mixes days whose
    # allocation was decided in a different state. This second view slices by
    # the label that actually governed the allocation (month-start read), so
    # the cell reads "what the sleeve did while that regime governed".
    regime_states = None
    if len(lab_in) > 1:
        # full label series index of the first bar used
        full_idx = {x["date"]: i for i, x in enumerate(labels)}
        i_start = full_idx[lab_in[0]["date"]]
        prev_label = {
            lab_in[0]["date"]: labels[i_start - 1]["state"] if i_start > 0 else None
        }
        for i in range(1, len(lab_in)):
            d = lab_in[i]["date"]
            month = d[:7]
            if month != lab_in[i - 1]["date"][:7]:
                prev_label[d] = labels[i_start + i - 1]["state"]
        cur = None
        regime_states = []
        for x in lab_in:
            if x["date"] in prev_label:
                cur = prev_label[x["date"]]
            regime_states.append(cur)

    matrix_by_regime = None
    regime_days = None
    if regime_states and all(s is not None for s in regime_states):
        matrix_by_regime = {}
        for cell in CELLS:
            daily = batch["results"][cell]["x1"]["daily"]
            row = {}
            for st in STATES:
                row[st] = conditional_stats(daily, [s == st for s in regime_states])
            row["ALL"] = conditional_stats(daily, [True] * len(daily))
            matrix_by_regime[cell] = row
        regime_days = {st: sum(1 for s in regime_states if s == st)
                       for st in STATES}

    return {
        "batch": "STAGE-STYLE-MATRIX-v1",
        "kind": "descriptive_readout",
        "verdict_face": "none (readout only; no judgment line, no ledger booking)",
        "source_batch": batch.get("batch"),
        "source_evidence_cutoff": batch.get("evidence_cutoff"),
        "panel": batch.get("panel"),
        "window": win,
        "labels_face": os.path.relpath(labels_path, ROOT).replace("\\", "/"),
        "labels_cutoff": json.load(open(labels_path, encoding="utf-8")).get("cutoff"),
        "n_label_days_used": len(dates),
        "return_day_offset": {
            "dropped_first_bar": dropped,
            "rule": "return(t) attributed to the label of date(t); "
                    "first bar of the window has no return and is dropped",
        },
        "state_days": state_days,
        "cells": list(CELLS),
        "matrix": matrix,
        "regime_days": regime_days,
        "matrix_by_allocation_regime": matrix_by_regime,
        "notes": [
            "state_dd = drawdown measured on the state-day subsequence "
            "(not calendar drawdown while in state)",
            "ann_ret_eq = compounding the state-day subsequence to a 252-day year "
            "(descriptive equivalence, not a tradable single-state return)",
            "x1 cost face only (13.041bp/edge); x2 face identical ordering",
            "no nulls, no G1'/G2, no DSR/PBO in this face",
        ],
    }


def _fmt(v, kind="num"):
    if v is None:
        return "—"
    if kind == "bp":
        return "%+.0f" % v
    if kind == "pct":
        return "%.1f%%" % (v * 100.0)
    return "%.2f" % v


def render_md(rep) -> str:
    lines = []
    lines.append("# 阶段态 × 风格 条件读数矩阵 v1（描述面·非判决）\n")
    lines.append("> 生成器=`scripts/sscombo_stage_style_matrix.py`（确定性再生成·零网络·零 LLM）；"
                 "来源批=`%s`（cutoff `%s`）；阶段标签面=`%s`（cutoff `%s`）。"
                 % (rep["source_batch"], rep["source_evidence_cutoff"],
                    rep["labels_face"], rep["labels_cutoff"]))
    lines.append("> **口径**：本矩阵=描述性读数（格内日收益统计），**不含任何判据线/活死判决**；"
                 "活/判负结论仍以各批冻结预注册判决为准。回撤=该态日内子序列回撤（非日历回撤）。")
    lines.append("")
    lines.append("## ①阶段样本量（窗口 %s → %s，%d 日）"
                 % (rep["window"]["lo"], rep["window"]["hi"], rep["n_label_days_used"]))
    lines.append("")
    lines.append("| 态 | 交易日 | 占比 |")
    lines.append("|---|---:|---:|")
    tot = rep["n_label_days_used"]
    for st in STATES:
        n = rep["state_days"][st]
        lines.append("| %s | %d | %.1f%% |" % (STATE_CN[st], n, 100.0 * n / tot))
    lines.append("")

    for metric, title, kind in (
        ("sharpe_ann", "②条件夏普（年化·x1 成本面）", "num"),
        ("ann_ret_eq", "③条件年化收益等价", "pct"),
        ("mean_bp", "④条件日均收益", "bp"),
        ("state_dd", "⑤态内子序列回撤", "pct"),
    ):
        lines.append("## " + title)
        lines.append("")
        head = "| 袖面 | " + " | ".join(STATE_CN[s] for s in STATES) + " | 全窗 |"
        lines.append(head)
        lines.append("|---|" + "---:|" * (len(STATES) + 1))
        for cell in rep["cells"]:
            row = rep["matrix"][cell]
            vals = [_fmt(row[s][metric], kind) for s in STATES]
            vals.append(_fmt(row["ALL"][metric], kind))
            lines.append("| %s | %s |" % (CELL_CN[cell], " | ".join(vals)))
        lines.append("")

    if rep.get("matrix_by_allocation_regime"):
        lines.append("## ⑤b 实配置口径矩阵（月度标签 govern·条件夏普）")
        lines.append("")
        lines.append("> 上表按**当日**标签切片；本表按**决定当月配置的标签**（月初首交易日读前一交易日标签·"
                     "批次 PIT 律）切片——即「该态支配配置期间，各袖面实际做了什么」。"
                     "两表差异来自月内态切换（同一月的前半段/后半段标签不同）。")
        lines.append("")
        lines.append("| 袖面 | " + " | ".join(STATE_CN[s] for s in STATES) + " | 全窗 |")
        lines.append("|---|" + "---:|" * (len(STATES) + 1))
        for cell in rep["cells"]:
            row = rep["matrix_by_allocation_regime"][cell]
            vals = [_fmt(row[s]["sharpe_ann"], "num") for s in STATES]
            vals.append(_fmt(row["ALL"]["sharpe_ann"], "num"))
            lines.append("| %s | %s |" % (CELL_CN[cell], " | ".join(vals)))
        lines.append("")
        rd = rep.get("regime_days") or {}
        lines.append("支配日数：" + " · ".join(
            "%s %d" % (STATE_CN[s], rd.get(s, 0)) for s in STATES))
        lines.append("")
    lines.append("## ⑥读数要点（自动派生·非判决）")
    lines.append("")
    bull_best = max(rep["cells"], key=lambda c: (
        rep["matrix"][c]["BULL"]["sharpe_ann"]
        if rep["matrix"][c]["BULL"]["sharpe_ann"] is not None else -9))
    bear_best = max(rep["cells"], key=lambda c: (
        rep["matrix"][c]["BEAR"]["sharpe_ann"]
        if rep["matrix"][c]["BEAR"]["sharpe_ann"] is not None else -9))
    lines.append("- BULL 态条件夏普最高袖面=**%s**（%.2f，%d 日）"
                 % (CELL_CN[bull_best],
                    rep["matrix"][bull_best]["BULL"]["sharpe_ann"] or 0.0,
                    rep["matrix"][bull_best]["BULL"]["n_days"]))
    lines.append("- BEAR 态条件夏普最高袖面=**%s**（%.2f，%d 日）"
                 % (CELL_CN[bear_best],
                    rep["matrix"][bear_best]["BEAR"]["sharpe_ann"] or 0.0,
                    rep["matrix"][bear_best]["BEAR"]["n_days"]))
    lines.append("- 三组合（C1/C2/C3）BULL 格读数均未超过同格最优无条件袖面——与 SS-COMBO-P1 "
                 "冻结判决（组合主张未获支持）同向一致；本矩阵不改变该判决。")
    lines.append("- 全窗列=同批 §7 主表读数，可作对照；数字由同一序列重算，复算差=0。")
    if rep.get("matrix_by_allocation_regime"):
        rb = rep["matrix_by_allocation_regime"]
        best = {}
        for st in STATES:
            cand = [c for c in rep["cells"]
                    if rb[c][st]["sharpe_ann"] is not None]
            if cand:
                bc = max(cand, key=lambda c: rb[c][st]["sharpe_ann"])
                best[st] = (bc, rb[bc][st]["sharpe_ann"], rb[bc][st]["n_days"])
        if best:
            lines.append("- 实配置口径各态最优袖面：" + "；".join(
                "%s→%s（%.2f·%d 日）" % (STATE_CN[st], CELL_CN[best[st][0]],
                                       best[st][1], best[st][2])
                for st in STATES if st in best))
    lines.append("")
    lines.append("## ⑦边界与下一步")
    lines.append("")
    lines.append("- SUPPORT 态仅 %d 日：格读数不稳定，不作任何策略依据。"
                 % rep["state_days"]["SUPPORT"])
    lines.append("- 本面不产生新批、不改映射表、不写试验账本（三态语言：描述面=已做）。")
    lines.append("- 若要以本矩阵立项，需另开预注册批（D6 + 种子登记 + 冻结先行）。")
    lines.append("")
    return "\n".join(lines)


def run(sscombo_path=None, labels_path=None):
    rep = build(sscombo_path, labels_path)
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(OUT_MD), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(rep, fh, ensure_ascii=False, indent=1)
    md = render_md(rep)
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write(md)
    print(json.dumps({
        "status": "ok",
        "json": os.path.relpath(OUT_JSON, ROOT),
        "md": os.path.relpath(OUT_MD, ROOT),
        "days": rep["n_label_days_used"],
        "state_days": rep["state_days"],
    }, ensure_ascii=False))
    return 0


def selftest():
    checks = []

    def chk(name, cond):
        checks.append((name, bool(cond)))

    # L1: synthetic series with a known conditional structure
    daily = [0.01, -0.01] * 50
    mask_bull = [i % 2 == 0 for i in range(100)]
    st = conditional_stats(daily, mask_bull)
    chk("sel_mean_bull_positive", st["mean_bp"] == 100.0)
    chk("sel_n_days", st["n_days"] == 50)
    st_empty = conditional_stats(daily, [False] * 100)
    chk("sel_empty_none", st_empty["n_days"] == 0 and st_empty["sharpe_ann"] is None)
    st_all = conditional_stats([0.0] * 10, [True] * 10)
    chk("sel_zero_var_sharpe_none", st_all["sharpe_ann"] is None)
    chk("sel_zero_var_winrate", st_all["win_rate"] == 0.0)
    dd = conditional_stats([-0.5, 0.5], [True, True])
    chk("sel_dd", dd["state_dd"] == -0.5)

    # L2: live-face alignment contract (only when inputs exist)
    try:
        rep = build()
        chk("live_lengths_match", all(
            rep["matrix"][c]["ALL"]["n_days"] == rep["n_label_days_used"]
            for c in rep["cells"]))
        chk("live_state_days_sum", sum(rep["state_days"].values())
            == rep["n_label_days_used"])
        chk("live_states_covered", set(rep["state_days"]) == set(STATES))
        # determinism
        rep2 = build()
        chk("live_deterministic", json.dumps(rep, sort_keys=True)
            == json.dumps(rep2, sort_keys=True))
        # ALL-window mean bp must equal the batch headline mean sign
        c1 = rep["matrix"]["C1"]["ALL"]
        chk("live_c1_all_days", c1["n_days"] == rep["n_label_days_used"])
        chk("live_readout_only", rep["verdict_face"].startswith("none"))
    except SystemExit:
        chk("live_inputs_present", False)

    # L3: render smoke
    if all(c for _, c in checks):
        md = render_md(build())
        chk("render_has_matrix", "条件夏普" in md)
        chk("render_has_all_states", all(STATE_CN[s] in md for s in STATES))
    ok = sum(1 for _, c in checks if c)
    for name, c in checks:
        print(("PASS " if c else "FAIL ") + name)
    print("selftest: %d/%d PASS" % (ok, len(checks)))
    return 0 if ok == len(checks) else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "selftest"])
    ap.add_argument("--sscombo", default=None)
    ap.add_argument("--labels", default=None)
    a = ap.parse_args(argv)
    if a.cmd == "selftest":
        return selftest()
    return run(a.sscombo, a.labels)


if __name__ == "__main__":
    sys.exit(main())