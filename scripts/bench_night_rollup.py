#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tonight's bench answers, sorted into "a real no" and "never had a chance to say"

WHY THIS FILE EXISTS
--------------------
Between 21:20 and 22:00 on 2026-11-24 the bench queue emptied itself: nineteen
cells finished, each wrote its own verdict and its own result file.  Read one at a
time they look alike -- `NO_EDGE`, `NO_EDGE`, `NO_EDGE` -- and that is the trap.
A cell that says `NO_EDGE` while its own `powered_for_target` is false has not
answered anything: its minimum detectable effect (MDE) is larger than the edge it
was asked to find, so "no edge detected" is what a machine says when it cannot
see, not what it says when it looked.

This file re-reads the night through what each cell already printed about itself:

    SURVIVOR      a cell whose own verdict passed
    FINDING       negative or mixed, measured with power: the sentence counts
    SILENT        negative at power below its own target: not a verdict
    NOT_A_VERDICT a tracking cell that never claimed to decide anything

and it keeps two things separate that a one-line verdict merges:

  * **arm-level passes** -- a census cell can be filed `CENSUS_SIGN_MIXED` while
    two of its fourteen arms passed their own gates; folding those into "mixed"
    throws away the only thing in the night that cleared admission;
  * **the price of silence** -- MDE falls with the square root of the sample, so a
    cell whose MDE is 9.2pp against a 3pp target needs 9.4x the history it already
    has (about 93 years on 2,389 bars).  That number is why a silent question must
    be re-targeted or dropped, never simply re-run: re-running buys the same
    "cannot see" for another unit of compute.

WHAT THIS FILE DOES NOT DO
--------------------------
  * it does not run any bench cell and does not touch the queue: membership comes
    from the queue's own result pointers plus each result file's `generated` stamp;
  * it does not re-judge a cell's rule: verdict, power stamp and checks are read
    verbatim from the cell;
  * it does not promote anything: an arm that passed is the first gate, not an
    admission, and this face says so on the page;
  * it does not rewrite history: the window is pinned, so later cells belong to a
    later roll-up.
"""
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

QUEUE_PATH = os.path.join(ROOT, "research", "BENCH-QUEUE.json")
OUT_PATH = os.path.join(ROOT, "results", "bench_night_rollup.json")
DOC_PATH = os.path.join(ROOT, "research", "BENCH_NIGHT_ROLLUP.md")

TZ = timezone(timedelta(hours=8))
TRADING_DAYS = 242.0

# The window is a fact about the night, not a moving target.
WINDOW_LO = "2026-11-24T21:20"
WINDOW_HI = "2026-11-24T22:00"

# A question whose MDE is within a quarter of its target is "close enough that
# waiting is a real answer"; beyond that, waiting means years and the target has
# to move instead.
NEAR_TARGET_MULTIPLE = 1.25

MARK_BEGIN = "<!-- BEGIN:BENCH-NIGHT-ROLLUP -->"
MARK_END = "<!-- END:BENCH-NIGHT-ROLLUP -->"

PASS_VERDICTS = ("SIGNIFICANT", "EDGE", "GO", "PASS")
NEGATIVE_PREFIXES = ("NO_EDGE", "UNSTABLE", "CENSUS_")
TRACKING_VERDICTS = ("TRACKING",)

POLARITY = {
    "NO_EDGE": "negative",
    "UNSTABLE_ACROSS_PARAMS": "unstable",
    "CENSUS_SIGN_MIXED": "mixed",
    "CENSUS_LEANS_POSITIVE": "leans_positive",
    "CENSUS_UNPOWERED": "negative",
}


# ------------------------------------------------------------------ helpers
def now():
    return datetime.now(TZ)


def read_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def dump_json(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
        f.write("\n")
    os.replace(tmp, path)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path):
    return os.path.relpath(path, ROOT).replace("\\", "/")


def num(x, nd=2):
    return None if x is None else round(float(x), nd)


def fmt_pp(x):
    return "--" if x is None else ("%+.2f" % x)


# ------------------------------------------------------------------ selection
def in_window(stamp):
    """Membership is decided to the minute: both bounds are inclusive."""
    if not stamp:
        return False
    return WINDOW_LO[:16] <= stamp[:16] <= WINDOW_HI[:16]


def night_cells():
    """The cells whose own result file says it was written inside the window.

    The queue is only the index (it carries the result pointer); the result file's
    `generated` stamp decides membership, so a queued-but-unrun cell cannot sneak
    in and a cell that ran is found even after the queue moved on.
    """
    queue = read_json(QUEUE_PATH) or {}
    found = []
    for cell in queue.get("cells") or []:
        rp = cell.get("result")
        if not rp:
            continue
        path = os.path.join(ROOT, rp.replace("/", os.sep))
        if not os.path.exists(path):
            continue
        payload = read_json(path)
        if not payload:
            continue
        stamp = payload.get("generated") or payload.get("ts") or ""
        if not in_window(stamp):
            continue
        found.append({
            "id": cell.get("id"),
            "cell_status": cell.get("status"),
            "result_path": path,
            "result_rel": rel(path),
            "generated": stamp,
            "payload": payload,
        })
    found.sort(key=lambda c: (c["generated"], c["id"] or ""))
    return found


# ------------------------------------------------------------------ reading one cell
def arm_power(arms):
    if not arms:
        return "NOT_APPLICABLE", 0, 0
    powered = sum(1 for a in arms if a.get("powered_for_target") is True)
    if powered == len(arms):
        return "POWERED_ALL", powered, len(arms)
    if powered == 0:
        return "UNPOWERED", 0, len(arms)
    return "POWERED_SOME", powered, len(arms)


def cell_target(payload):
    for holder in (payload.get("config") or {}, payload.get("criteria") or {}):
        t = holder.get("target_edge_pp")
        if t is not None:
            return float(t)
    return None


def arm_key(a):
    """`read_arms` flattens the payload, so the annualised return is a top key."""
    v = a.get("ann_pct")
    return v if v is not None else -999.0


def classify(verdict, power_state):
    v = (verdict or "").upper()
    if v in TRACKING_VERDICTS:
        return "NOT_A_VERDICT"
    if v in PASS_VERDICTS:
        return "SURVIVOR"
    if v.startswith(NEGATIVE_PREFIXES):
        return "SILENT" if power_state == "UNPOWERED" else "FINDING"
    return "UNCLASSIFIED"


def silence_tier(multiple):
    if multiple is None:
        return None
    return "NEAR" if multiple <= NEAR_TARGET_MULTIPLE else "FAR"


def read_arms(payload):
    arms = payload.get("arms") or []
    out = []
    for a in arms:
        cw = a.get("common_window") or {}
        oos = a.get("oos_2024_after") or {}
        ctl = a.get("control") or {}
        tags = a.get("tags") or {}
        label = tags.get("variant") or tags.get("lookback") or tags.get("variant_id")
        if label is None and tags:
            label = "|".join("%s=%s" % (k, tags[k]) for k in sorted(tags))
        out.append({
            "arm": label or "single",
            "verdict": a.get("verdict"),
            "ann_pct": num(cw.get("ann_pct")),
            "oos_ann_pct": num(oos.get("ann_pct")),
            "sharpe": num(cw.get("sharpe"), 3),
            "t_stat": num(cw.get("t_stat"), 2),
            "mde_pp": num(a.get("mde_pp")),
            "powered_for_target": a.get("powered_for_target"),
            "p_value": num(ctl.get("p_value"), 4),
            "passed": (a.get("verdict") or "").upper() in PASS_VERDICTS,
        })
    return out


def read_cell(hit):
    payload = hit["payload"]
    arms = read_arms(payload)
    raw_arms = payload.get("arms") or []
    power_state, powered, total = arm_power(raw_arms)
    verdict = payload.get("verdict")
    target = cell_target(payload)
    reading = classify(verdict, power_state)

    mdes = [a["mde_pp"] for a in arms if a["mde_pp"] is not None]
    mde_min = min(mdes) if mdes else None
    bars = (payload.get("coverage") or {}).get("bars")
    if bars is None:
        b = [(a.get("common_window") or {}).get("n") for a in raw_arms]
        b = [x for x in b if x]
        if not b:
            b = [v.get("bars") for v in (payload.get("products") or {}).values()
                 if isinstance(v, dict) and v.get("bars")]
        bars = max(b) if b else None

    multiple = years_needed = extra_years = None
    if mde_min is not None and target and target > 0 and bars:
        multiple = (float(mde_min) / float(target)) ** 2
        years_needed = bars * multiple / TRADING_DAYS
        # What the reader actually has to wait: total minus what is already on disk.
        extra_years = bars * (multiple - 1.0) / TRADING_DAYS

    best = max(arms, key=arm_key) if arms else None
    bench = (payload.get("benchmark_buy_and_hold") or {}).get("common_window") or {}
    bench_ann = bench.get("ann_pct")
    # A market-neutral pair's opponent is cash, not buy-and-hold: printing an
    # "excess" against a long benchmark there would flatter a hedge.
    is_pair = ((payload.get("config") or {}).get("type") == "pair")
    excess = None
    excess_note = None
    if is_pair:
        bench_ann = None
        excess_note = "对价为对冲策略，买入持有不是它的对手"
    elif best and best.get("ann_pct") is not None and bench_ann is not None:
        excess = round(best["ann_pct"] - float(bench_ann), 2)

    passes = [a for a in arms if a["passed"]]

    return {
        "id": hit["id"],
        "result": hit["result_rel"],
        "generated": hit["generated"],
        "verdict": verdict,
        "polarity": POLARITY.get((verdict or "").upper(), "unknown"),
        "reading": reading,
        "target_edge_pp": target,
        "bars": bars,
        "arms": total,
        "arm_detail": arms,
        "arms_powered": powered,
        "arms_passed": len(passes),
        "arms_passed_labels": [a["arm"] for a in passes],
        "power_state": power_state,
        "mde_min_pp": num(mde_min),
        "mde_max_pp": num(max(mdes) if mdes else None),
        "history_multiple_to_target": num(multiple),
        "silence_tier": silence_tier(num(multiple)) if reading == "SILENT" else None,
        "years_needed_at_target": num(years_needed, 1),
        "extra_years_needed": num(extra_years, 1),
        "best_arm": (best or {}).get("arm"),
        "ann_pct": (best or {}).get("ann_pct"),
        "oos_ann_pct": (best or {}).get("oos_ann_pct"),
        "sharpe": (best or {}).get("sharpe"),
        "t_stat": (best or {}).get("t_stat"),
        "p_value": (best or {}).get("p_value"),
        "bench_ann_pct": num(bench_ann),
        "excess_vs_bench_pp": excess,
        "excess_note": excess_note,
        "headline": cell_headline(hit["id"], payload),
    }


def cell_headline(cell_id, payload):
    """A one-line, cell-specific number the reader can check against the file."""
    if cell_id == "basis_timing_perm":
        out = []
        for prod, v in sorted((payload.get("products") or {}).items()):
            if isinstance(v, dict) and v.get("difference_pp") is not None:
                out.append("%s +%.2fpp（零假设 p95 %+.2f，p=%.3f）"
                           % (prod, v["difference_pp"], v.get("null_p95_pp") or 0.0,
                              v.get("p_value") or 0.0))
        return "; ".join(out)
    prod = payload.get("products") or {}
    if prod and all(isinstance(v, dict) for v in prod.values()):
        bits = []
        for name, v in sorted(prod.items()):
            if v.get("annualised_pct") is not None:
                bits.append("%s %.2f%%/年" % (name, v["annualised_pct"]))
        if bits:
            return "; ".join(bits)
    return None


# ------------------------------------------------------------------ build
def build():
    hits = night_cells()
    cells = [read_cell(h) for h in hits]

    buckets = {}
    for c in cells:
        buckets.setdefault(c["reading"], []).append(c)

    silent = buckets.get("SILENT", [])
    findings = buckets.get("FINDING", [])
    survivors = buckets.get("SURVIVOR", [])
    tracking = buckets.get("NOT_A_VERDICT", [])
    unclassified = buckets.get("UNCLASSIFIED", [])

    silent_far = [c for c in silent if c["silence_tier"] == "FAR"]
    silent_near = [c for c in silent if c["silence_tier"] == "NEAR"]
    worst = max(silent_far, key=lambda c: c["history_multiple_to_target"] or 0) if silent_far else None
    findings_negative = [c for c in findings if c["polarity"] == "negative"]
    findings_other = [c for c in findings if c["polarity"] != "negative"]

    arm_passes = [(c["id"], label) for c in cells for label in c["arms_passed_labels"]]
    # The same rule can pass inside two cells (a robust cell and a census cell run
    # the same variants), and their tag vocabularies differ ('120d' vs
    # "tsmom|{'lookback': 120, ...}|ls"), so labels cannot be compared.  The
    # readings can: two passing arms printing a bit-identical (ann, oos, mde)
    # triple are one rule measured twice, not two ideas.
    passing_readings = {}
    for c in cells:
        for a in c["arm_detail"]:
            if a["passed"]:
                key = (a["ann_pct"], a["oos_ann_pct"], a["mde_pp"])
                passing_readings.setdefault(key, []).append("%s:%s" % (c["id"], a["arm"]))
    distinct_arm_passes = sorted(passing_readings)

    problems = []
    if not cells:
        problems.append("no cell finished inside the window")
    if unclassified:
        problems.append("unclassified verdict(s): "
                        + ", ".join("%s=%s" % (c["id"], c["verdict"]) for c in unclassified))
    if len(cells) != len({c["id"] for c in cells}):
        problems.append("the same cell id appears twice in the window")
    if any(c["reading"] == "SILENT" and c["history_multiple_to_target"] is None for c in silent):
        problems.append("a SILENT cell cannot be priced (no mde/target/bars)")

    verdict = "NO_WINDOW" if problems else "CELLS%d_SURVIVOR%d_ARMPASS%d_SILENT%d_FAR%d_FINDING%d" % (
        len(cells), len(survivors), len(arm_passes), len(silent), len(silent_far), len(findings))

    inputs = {}
    for h in hits:
        inputs[h["result_rel"]] = sha256_file(h["result_path"])
    inputs[rel(QUEUE_PATH)] = sha256_file(QUEUE_PATH)

    return {
        "schema": "bench-night-rollup/1",
        "generated": now().isoformat(timespec="seconds"),
        "window": {"lo": WINDOW_LO, "hi": WINDOW_HI},
        "evidence_cutoff": max((h["payload"].get("evidence_cutoff") or "") for h in hits) if hits else None,
        "verdict": verdict,
        "problems": problems,
        "totals": {
            "cells": len(cells),
            "survivor": len(survivors),
            "arm_passes": len(arm_passes),
            "arm_passes_distinct": len(distinct_arm_passes),
            "arm_passes_distinct_labels": ["%+.2f/%+.2f@%.2f" % k for k in distinct_arm_passes],
            "arm_passes_sources": {"%+.2f/%+.2f@%.2f" % k: v
                                   for k, v in passing_readings.items()},
            "finding": len(findings),
            "finding_negative": len(findings_negative),
            "finding_other": len(findings_other),
            "silent": len(silent),
            "silent_far": len(silent_far),
            "silent_near": len(silent_near),
            "not_a_verdict": len(tracking),
            "unclassified": len(unclassified),
            "silent_worst_id": worst["id"] if worst else None,
            "silent_worst_multiple": worst["history_multiple_to_target"] if worst else None,
            "silent_worst_years": worst["years_needed_at_target"] if worst else None,
        },
        "cells": cells,
        "inputs": inputs,
    }


# ------------------------------------------------------------------ page
def render_md(face):
    t = face["totals"]
    cells = face["cells"]
    L = []
    L.append("<!-- generated by scripts/bench_night_rollup.py; readings live inside the markers -->")
    L.append("")
    L.append("# 一晚上的十九个答案：一条格级过门、两条臂级过门、七个真有话说、十个从来没机会开口")
    L.append("")
    L.append("窗口 %s → %s（按每格自己写的 `generated` 取样），证据截至 %s。"
             % (face["window"]["lo"].replace("T", " "),
                face["window"]["hi"][11:], face["evidence_cutoff"] or "--"))
    L.append("")
    L.append(MARK_BEGIN)
    L.append("generated %s" % face["generated"])
    L.append("")
    L.append("判词 **%s** —— 格子 %d 个：格级过门 %d · 臂级过门 %d（去重后 %d 条规则）· 有功效的判决 %d · 问不出声 %d（其中 %d 个是真等不来的）· 不判词 %d。"
             % (face["verdict"], t["cells"], t["survivor"], t["arm_passes"],
                t["arm_passes_distinct"], t["finding"], t["silent"], t["silent_far"],
                t["not_a_verdict"]))
    if t["silent_worst_id"]:
        w = next(c for c in cells if c["id"] == t["silent_worst_id"])
        L.append("最坏的一问 `%s`：最小可判定边际 %.2f pp 撞上 %.2f pp 的目标 → 要现在样本的 **%.2f 倍**，"
                 "也就是**还要再攒 %.0f 年**才判得了。"
                 % (t["silent_worst_id"], w["mde_min_pp"] or 0.0, w["target_edge_pp"] or 0.0,
                    t["silent_worst_multiple"] or 0.0, w["extra_years_needed"] or 0.0))
    L.append("")
    L.append("| 格子 | 判词 | 功效 | 最好一臂 | 买入持有 | 超额 | 最小可判定 | 目标 | 要几倍样本 | 归类 |")
    L.append("|---|---|---|---|---|---|---|---|---|---|")
    for c in cells:
        power = {"POWERED_ALL": "全有功效", "POWERED_SOME": "部分有功效",
                 "UNPOWERED": "**没有功效**", "NOT_APPLICABLE": "不适用"}[c["power_state"]]
        L.append("| %s | %s | %s | %s / OOS %s | %s | %s | %s | %s | %s | %s |" % (
            c["id"], c["verdict"] or "--", power,
            fmt_pp(c["ann_pct"]), fmt_pp(c["oos_ann_pct"]),
            fmt_pp(c["bench_ann_pct"]), fmt_pp(c["excess_vs_bench_pp"]),
            "--" if c["mde_min_pp"] is None else "%.2f" % c["mde_min_pp"],
            "--" if c["target_edge_pp"] is None else "%.2f" % c["target_edge_pp"],
            "--" if c["history_multiple_to_target"] is None else "%.2f" % c["history_multiple_to_target"],
            c["reading"]))
    L.append("")
    L.append("「超额」= 最好一臂的年化减买入持有；空格表示该格没有印买入持有基准，不是零。")
    L.append("")
    L.append("## 真过了门的")
    L.append("")
    for c in [x for x in cells if x["reading"] == "SURVIVOR"]:
        L.append("- **%s**（格级）：%s。"
                 % (c["id"], c["headline"] or "--"))
    for c in cells:
        if c["arms_passed"]:
            L.append("- **%s**（臂级 %d/%d）：%s —— 这一格在格级写着 `%s`，但里面这两条臂各自过了自己的门，"
                     "合并判词把它们藏起来了。"
                     % (c["id"], c["arms_passed"], c["arms"],
                        "、".join(c["arms_passed_labels"]), c["verdict"]))
    if t["arm_passes"] != t["arm_passes_distinct"]:
        L.append("- **去重提醒**：%d 条过门的臂里只有 **%d 条不同的读数**（%s）——同一套变体在稳健格与普查格里各跑了一次，"
                 "读数逐位相同；真正过门的想法只有 %d 条，不是 %d 条。"
                 % (t["arm_passes"], t["arm_passes_distinct"],
                    "、".join(t["arm_passes_distinct_labels"]), t["arm_passes_distinct"],
                    t["arm_passes"]))
        for key, where in sorted(t["arm_passes_sources"].items()):
            if len(where) > 1:
                L.append("  - 读数 `%s` 出自：%s" % (key, "、".join(where)))
    if not [x for x in cells if x["reading"] == "SURVIVOR"] and not t["arm_passes"]:
        L.append("- 今晚没有格子或臂通过自己的门。")
    L.append("")
    L.append("过门不等于入册：这里数的是「它自己的判据过了」，成本、容量、纸面跟踪都还没跑。")
    L.append("")
    L.append("## 有功效的判决（看得见，所以这句话算话）")
    L.append("")
    for c in [x for x in cells if x["reading"] == "FINDING"]:
        extra = ""
        if c.get("excess_note"):
            extra = "（%s）" % c["excess_note"]
        elif c["excess_vs_bench_pp"] is not None and c["polarity"] in ("leans_positive", "mixed"):
            extra = ("（`%s` 说的是各臂方向一致，不是说它赢过基准：对买入持有 %s pp）"
                     % (c["verdict"], fmt_pp(c["excess_vs_bench_pp"])))
        L.append("- `%s` **%s**（%s）：最好一臂 %s%%、OOS %s%%、买入持有 %s%%、超额 %s pp，最小可判定 %.2fpp ≤ 目标 %.2fpp。%s"
                 % (c["id"], c["verdict"], c["polarity"],
                    fmt_pp(c["ann_pct"]), fmt_pp(c["oos_ann_pct"]),
                    fmt_pp(c["bench_ann_pct"]), fmt_pp(c["excess_vs_bench_pp"]),
                    c["mde_min_pp"] or 0.0, c["target_edge_pp"] or 0.0, extra))
    L.append("")
    L.append("## 问不出声（判词写着否定，功率却低于自己的目标）")
    L.append("")
    L.append("这些格子不是被否掉的，是被**问坏的**：最小可判定边际比它要找的边际还大。"
             "MDE 按样本数的平方根收窄，所以「再等等」等于「再多几倍历史」。")
    L.append("")
    for c in [x for x in cells if x["reading"] == "SILENT" and x["silence_tier"] == "NEAR"]:
        wait = (c["extra_years_needed"] or 0.0) * 12.0
        L.append("- `%s`：%.2fpp vs 目标 %.2fpp → **%.2f 倍**样本，再攒约 **%.0f 个月**就到。差一点点，等得起。"
                 % (c["id"], c["mde_min_pp"] or 0.0, c["target_edge_pp"] or 0.0,
                    c["history_multiple_to_target"] or 0.0, wait))
    for c in [x for x in cells if x["reading"] == "SILENT" and x["silence_tier"] == "FAR"]:
        L.append("- `%s`：%.2fpp vs 目标 %.2fpp → **%.2f 倍**样本，**还要再攒 %.0f 年**。等不来，得改目标或删。"
                 % (c["id"], c["mde_min_pp"] or 0.0, c["target_edge_pp"] or 0.0,
                    c["history_multiple_to_target"] or 0.0, c["extra_years_needed"] or 0.0))
    L.append("")
    L.append("## 不判词的格子")
    L.append("")
    for c in [x for x in cells if x["reading"] == "NOT_A_VERDICT"]:
        L.append("- `%s` %s：%s —— 跟踪面，不进上面任何一类。"
                 % (c["id"], c["verdict"], c["headline"] or "没有读数行"))
    L.append("")
    L.append("## 这一晚该改的是什么")
    L.append("")
    L.append("1. **问不出声的 %d 个**别再排进队列重跑：重跑只买到同一个「看不见」。%d 个离目标不到四分之一，"
             "等样本自然长；%d 个要 %.1f–%.1f 倍历史，应当把目标边际改成与样本相称的量级，或者删掉。"
             % (t["silent"], t["silent_near"], t["silent_far"],
                min([c["history_multiple_to_target"] for c in cells
                     if c["silence_tier"] == "FAR"] or [0]),
                max([c["history_multiple_to_target"] for c in cells
                     if c["silence_tier"] == "FAR"] or [0])))
    L.append("2. **臂级过门的 %d 条（去重 %d 条规则）**要从它的格子里捞出来单独立案（成本 + 容量 + 纸面），"
             "格级 `CENSUS_*` 判词不该是它们的归宿。" % (t["arm_passes"], t["arm_passes_distinct"]))
    L.append("3. **有功效的否定 %d 个**可以照原样写进策略库，不必回炉；**另外 %d 个**（不稳 / 混杂 / 偏正）"
             "照各自判词留档，别把「偏正」读成「赢过基准」。"
             % (t["finding_negative"], t["finding_other"]))
    L.append(MARK_END)
    L.append("")
    return "\n".join(L)


def splice_doc(text):
    """Replace only the marked block; the prose around it belongs to the reader."""
    if os.path.exists(DOC_PATH):
        with open(DOC_PATH, encoding="utf-8") as f:
            old = f.read()
        if MARK_BEGIN in old and MARK_END in old:
            head = old.split(MARK_BEGIN, 1)[0]
            tail = old.split(MARK_END, 1)[1]
            block = text[text.index(MARK_BEGIN):text.index(MARK_END) + len(MARK_END)]
            with open(DOC_PATH, "w", encoding="utf-8", newline="\n") as f:
                f.write(head + block + tail)
            return
    os.makedirs(os.path.dirname(DOC_PATH), exist_ok=True)
    with open(DOC_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


# ------------------------------------------------------------------ check
def check():
    if not os.path.exists(OUT_PATH):
        return 3, "STALE: results/bench_night_rollup.json is missing"
    on_disk = read_json(OUT_PATH) or {}
    fresh = build()
    if fresh.get("inputs") != on_disk.get("inputs"):
        keys = sorted(set(fresh.get("inputs", {})) | set(on_disk.get("inputs", {})))
        moved = [k for k in keys
                 if (fresh.get("inputs") or {}).get(k) != (on_disk.get("inputs") or {}).get(k)]
        return 3, "STALE: an input cell moved since this face was written (%s); re-run run" % (
            ", ".join(moved[:4]) or "queue changed")
    if fresh.get("verdict") != on_disk.get("verdict"):
        return 1, "CHECK FAILED: face verdict %s != recomputed %s" % (
            on_disk.get("verdict"), fresh.get("verdict"))
    fmap = {c["id"]: c for c in fresh["cells"]}
    dmap = {c["id"]: c for c in on_disk.get("cells", [])}
    if set(fmap) != set(dmap):
        return 1, "CHECK FAILED: cell set differs (%d on disk, %d recomputed)" % (len(dmap), len(fmap))
    for cid in sorted(fmap):
        for key in ("verdict", "reading", "power_state", "silence_tier", "target_edge_pp",
                    "bars", "arms_passed"):
            if fmap[cid].get(key) != dmap[cid].get(key):
                return 1, "CHECK FAILED: %s.%s %r != %r" % (
                    cid, key, dmap[cid].get(key), fmap[cid].get(key))
        for key in ("mde_min_pp", "history_multiple_to_target", "ann_pct", "excess_vs_bench_pp"):
            dv, fv = dmap[cid].get(key), fmap[cid].get(key)
            if (dv is None) != (fv is None) or (dv is not None and abs(dv - fv) > 1e-4):
                return 1, "CHECK FAILED: %s.%s %r != %r" % (cid, key, dv, fv)
    if not os.path.exists(DOC_PATH):
        return 1, "CHECK FAILED: page missing"
    with open(DOC_PATH, encoding="utf-8") as f:
        page = f.read()
    m = re.search(re.escape(MARK_BEGIN) + r".*?" + re.escape(MARK_END), page, re.S)
    if not m:
        return 1, "CHECK FAILED: page has no readings block"
    want = render_md(fresh).split(MARK_BEGIN, 1)[1].split(MARK_END, 1)[0]
    got = m.group(0).split(MARK_BEGIN, 1)[1].split(MARK_END, 1)[0]
    norm = lambda s: re.sub(r"^generated .*$", "generated <t>", s.strip(), flags=re.M)
    if norm(want) != norm(got):
        return 1, "CHECK FAILED: page block differs from a fresh render (re-run run)"
    return 0, "ok: %d cells, verdict %s" % (len(fmap), on_disk.get("verdict"))


# ------------------------------------------------------------------ selftest
def selftest():
    legs = []

    legs.append((abs((9.2 / 3.0) ** 2 - 9.404) < 0.01,
                 "9.2pp MDE against a 3pp target needs %.2fx the history" % ((9.2 / 3.0) ** 2)))
    legs.append((abs((1.0 / (2 ** 0.5)) - 0.7071) < 1e-3,
                 "doubling the bars moves MDE by 1/sqrt(2) = 0.707x"))
    legs.append((silence_tier(1.01) == "NEAR" and silence_tier(1.35) == "FAR"
                 and silence_tier(NEAR_TARGET_MULTIPLE) == "NEAR",
                 "1.01x is a wait, 1.35x is a re-target"))
    legs.append((classify("NO_EDGE", "UNPOWERED") == "SILENT",
                 "NO_EDGE at zero power reads as SILENT"))
    legs.append((classify("NO_EDGE", "POWERED_ALL") == "FINDING",
                 "NO_EDGE with full power reads as FINDING"))
    legs.append((classify("TRACKING", "NOT_APPLICABLE") == "NOT_A_VERDICT",
                 "TRACKING is NOT_A_VERDICT"))
    legs.append((classify("SOMETHING_NEW", "POWERED_ALL") == "UNCLASSIFIED",
                 "an unknown verdict is surfaced as UNCLASSIFIED"))
    legs.append((in_window("2026-11-24T21:20:00+08:00")
                 and in_window("2026-11-24T22:00:59+08:00")
                 and not in_window("2026-11-24T22:01:00+08:00")
                 and not in_window("2026-11-24T21:19:59+08:00"),
                 "the window is closed at both ends, to the minute"))
    legs.append((arm_power([{"powered_for_target": True}, {"powered_for_target": True}])[0] == "POWERED_ALL"
                 and arm_power([{"powered_for_target": True}, {"powered_for_target": False}])[0] == "POWERED_SOME"
                 and arm_power([{"powered_for_target": False}])[0] == "UNPOWERED"
                 and arm_power([])[0] == "NOT_APPLICABLE",
                 "power states follow the arms' own stamps"))

    face = build()
    if face["problems"]:
        legs.append((False, "live build refused: %s" % "; ".join(face["problems"])))
    else:
        t = face["totals"]
        buckets = (t["survivor"] + t["finding"] + t["silent"] + t["not_a_verdict"] + t["unclassified"])
        legs.append((buckets == t["cells"],
                     "every one of the %d cells lands in exactly one bucket" % t["cells"]))
        legs.append((all(c["history_multiple_to_target"] is not None
                         for c in face["cells"] if c["reading"] == "SILENT"),
                     "every SILENT cell says how much more history it needs"))
        legs.append((t["silent_near"] + t["silent_far"] == t["silent"],
                     "every silent cell is either near or far (%d + %d)" % (t["silent_near"], t["silent_far"])))
        ids = {c["id"] for c in face["cells"] if c["reading"] == "SURVIVOR"}
        legs.append((all(face_cell["verdict"] in PASS_VERDICTS
                         for face_cell in face["cells"] if face_cell["id"] in ids),
                     "SURVIVOR only holds cells whose own verdict passed"))
        legs.append((all(c["arms_passed"] <= c["arms"] for c in face["cells"]),
                     "arm passes never exceed the arm count (a census cell can pass 2 of 14)"))
        multi = [c for c in face["cells"] if c["arms"] > 1 and c["ann_pct"] is not None]
        legs.append((all(c["ann_pct"] == max(a["ann_pct"] for a in c["arm_detail"]
                                            if a["ann_pct"] is not None) for c in multi),
                     "the quoted arm is the best arm, not the first one (%d multi-arm cells)" % len(multi)))
        legs.append((any(c["arms_passed"] > 0 and c["verdict"] not in PASS_VERDICTS
                         for c in face["cells"]),
                     "a cell-level verdict can hide a passing arm -- and this face shows both"))
        legs.append((t["arm_passes_distinct"] <= t["arm_passes"],
                     "distinct passing rules never exceed passing arms (%d of %d)"
                     % (t["arm_passes_distinct"], t["arm_passes"])))
        pair_cells = [c for c in face["cells"]
                      if (read_json(os.path.join(ROOT, c["result"])) or {}).get("config", {}).get("type") == "pair"]
        legs.append((all(c["excess_vs_bench_pp"] is None and c.get("excess_note")
                         for c in pair_cells),
                     "a market-neutral pair prints no excess against buy-and-hold"))

    passed = sum(1 for ok_, _ in legs if ok_)
    for ok_, name in legs:
        print(("PASS  " if ok_ else "FAIL  ") + name)
    print("%d/%d PASS" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


# ------------------------------------------------------------------ main
def run(write=True):
    face = build()
    if face["problems"]:
        print("REFUSE: " + "; ".join(face["problems"]))
        return 4
    if write:
        dump_json(OUT_PATH, face)
        splice_doc(render_md(face))
    t = face["totals"]
    print("verdict %s" % face["verdict"])
    print("cells %d | cell-pass %d | arm-pass %d | finding %d | silent %d (far %d) | tracking %d"
          % (t["cells"], t["survivor"], t["arm_passes"], t["finding"],
             t["silent"], t["silent_far"], t["not_a_verdict"]))
    for c in face["cells"]:
        print("%-26s %-24s %-13s ann %7s ex %7s mde %5s tgt %5s x %6s arms %-12s %s"
              % (c["id"], c["verdict"], c["reading"], fmt_pp(c["ann_pct"]),
                 fmt_pp(c["excess_vs_bench_pp"]),
                 "--" if c["mde_min_pp"] is None else "%.2f" % c["mde_min_pp"],
                 "--" if c["target_edge_pp"] is None else "%.2f" % c["target_edge_pp"],
                 "--" if c["history_multiple_to_target"] is None else "%.2f" % c["history_multiple_to_target"],
                 "%d/%d" % (c["arms_passed"], c["arms"]), c["power_state"]))
    return 0


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd in ("run", "--write"):
        return run(write=True)
    if cmd in ("dry", "--dry"):
        return run(write=False)
    if cmd == "--check":
        rc, msg = check()
        print(msg)
        return rc
    if cmd == "--selftest":
        return selftest()
    print("usage: python scripts/bench_night_rollup.py [run|dry|--check|--selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
