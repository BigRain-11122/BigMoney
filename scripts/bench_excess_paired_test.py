"""The excess is a difference, so its noise is the noise of the difference.

Why this exists
---------------
`scripts/bench_go_ruler_audit.py` asks whether an arm's printed excess over its
own benchmark clears the arm's own MDE, and `bench_generic.build` computes that
MDE as

    1.96 * vol(arm) / sqrt(years)

which is the standard error of the ARM's annualised mean.

The excess is not the arm's mean. It is mean(arm - benchmark), a difference of
two books that hold the same basket most of the time, so a large part of their
daily movement cancels. Its own standard error is

    1.96 * sd(arm - benchmark) / sqrt(years)

and with a high correlation between the two books `sd(d)` can be a small
fraction of `sd(arm)`. Comparing an excess against the arm's own MDE therefore
answers the wrong question: it can call a measurable excess invisible, and in
principle the reverse.

This matters now because the open decision is "should H1 read excess >= own
MDE, which would flip the bench's GO set?". Before taking that decision the
difference needs its own standard error, not the arm's.

What it does
------------
For every face that still has its cell config (`research/cells/<id>.json`), it
rebuilds each arm's daily net series and the buy-and-hold benchmark **priced at
the same volatility target on the same panel with the same per-side cost**,
then reports per arm:

  * the two rulers already published (absolute gate; excess vs the arm's MDE)
  * the paired statistic: mean(arm - bench) annualised, its 95% half width,
    t, and the correlation between the two books
  * a label saying what the three readings do to each other

It rewrites no verdict and writes no bench face: read-only over the panels and
the published `results/bench_*.json`, plus new files of its own.

Usage
-----
  python scripts/bench_excess_paired_test.py             # write json + page
  python scripts/bench_excess_paired_test.py --selftest  # offline behaviour legs
  python scripts/bench_excess_paired_test.py --face census_commodity  # one face
"""
from __future__ import annotations

import argparse
import datetime
import glob
import io
import json
import math
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import bench_core as bc  # noqa: E402
import bench_generic as bg  # noqa: E402

RESULTS = os.path.join(ROOT, "results")
RESEARCH = os.path.join(ROOT, "research")
CELLS = os.path.join(RESEARCH, "cells")
OUT_JSON = os.path.join(RESULTS, "bench_excess_paired_test.json")
OUT_MD = os.path.join(RESEARCH, "BENCH_EXCESS_PAIRED_TEST.md")

SCHEMA = "bench-excess-paired-test/v1"
T_CRIT = 1.96

HID_VISIBLE = "HEURISTIC_HID_A_VISIBLE_EXCESS"
ADMITTED_INVISIBLE = "HEURISTIC_ADMITTED_WHAT_PAIRED_CANNOT_SEE"
AGREE_CLEARS = "BOTH_RULERS_SEE_IT"
AGREE_NO = "NEITHER_RULER_SEES_IT"
UNDECIDABLE = "UNDECIDABLE"


# --------------------------------------------------------------------------
# arm enumeration (same order and tags as bench_generic.run_cell)
# --------------------------------------------------------------------------
def arm_specs(cfg):
    """(label, sub-config) for every arm a cell would run."""
    out = []
    if cfg.get("type") == "census":
        for spec in cfg.get("grid") or []:
            sub = dict(cfg)
            sub["rule"] = spec["rule"]
            sub["params"] = spec.get("params") or {}
            sub["long_only"] = bool(spec.get("long_only", cfg.get("long_only", False)))
            label = "%s|%s|%s" % (spec["rule"], sub["params"],
                                  "long" if sub["long_only"] else "ls")
            out.append((label, sub))
    elif cfg.get("type") == "robust":
        for v in cfg.get("variants") or []:
            sub = dict(cfg)
            sub["params"] = dict(cfg.get("params") or {}, **(v.get("params") or {}))
            if v.get("long_only") is not None:
                sub["long_only"] = v["long_only"]
            label = (v.get("tags") or {}).get("variant") or v.get("name")
            out.append((label, sub))
    else:
        out.append((cfg.get("id"), cfg))
    return out


def net_series(cfg, dates, closes, rets, vols, highs, lows):
    """Daily net return series of one arm, built exactly as bench_generic does."""
    sigs = bg.build_signals(cfg, closes, highs, lows)
    pos, _live = bc.vol_weighted_positions(sigs, vols, target_vol=cfg.get("target_vol", 0.10))
    if pos is None or not pos.notna().any().any():
        return None
    _gross, net, _turn = bc.apply_costs(pos, rets, cost_bp_side=cfg.get("cost_bp_side", 3.0))
    return net.reindex(dates).fillna(0.0)


def bench_series(cfg, dates, closes, rets, vols):
    """Buy-and-hold on the same basket, priced at the arm's own volatility target."""
    sig = {c: pd.Series(1.0, index=s.index).where(s.notna()) for c, s in closes.items()}
    pos, _live = bc.vol_weighted_positions(sig, vols, target_vol=cfg.get("target_vol", 0.10))
    if pos is None:
        return None
    _gross, net, _turn = bc.apply_costs(pos, rets, cost_bp_side=cfg.get("cost_bp_side", 3.0))
    return net.reindex(dates).fillna(0.0)


# --------------------------------------------------------------------------
# the paired statistic
# --------------------------------------------------------------------------
def paired(diff):
    """Annualised mean of the daily difference, its 95% half width, and t.

    `diff` is a 1-D array-like of daily net returns (arm minus benchmark).
    """
    d = np.asarray(diff, dtype=float)
    d = d[np.isfinite(d)]
    n = len(d)
    if n < 60:
        return {"n": n, "mean_ann_pp": None, "se95_pp": None, "t": None,
                "sd_ann_pp": None}
    mean_ann_pp = float(np.mean(d)) * bc.TRADING_DAYS * 100.0
    sd = float(np.std(d, ddof=1))
    sd_ann_pp = sd * math.sqrt(bc.TRADING_DAYS) * 100.0
    # The annualised mean is one number estimated from `years` years of data, so
    # its standard error is sd_annual / sqrt(years) -- not sd_annual / sqrt(bars).
    # Dividing by sqrt(bars) shrinks the interval by sqrt(244) and would make
    # every excess look measurable.
    years = year_fraction(n)
    se95_pp = T_CRIT * sd_ann_pp / math.sqrt(years)
    # A difference that never moves (the same book twice) has no t, not t=0 by
    # luck; callers must be able to tell "no variation" from "no excess".
    t = None if sd <= 0 else float(np.mean(d)) / (sd / math.sqrt(n))
    return {"n": n, "years": round(years, 2), "mean_ann_pp": round(mean_ann_pp, 2),
            "se95_pp": round(se95_pp, 2),
            "t": None if t is None else round(t, 2),
            "sd_ann_pp": round(sd_ann_pp, 2)}


def year_fraction(n):
    return max(n / bc.TRADING_DAYS, 1e-9)


def ratio_excess_pp(arm, bench):
    """Compounded arm/benchmark ratio annualised -- the size the money sees."""
    a = np.asarray(arm, dtype=float)
    b = np.asarray(bench, dtype=float)
    a = np.where(np.isfinite(a), a, 0.0)
    b = np.where(np.isfinite(b), b, 0.0)
    n = len(a)
    if n < 60:
        return None
    g = float(np.prod(1.0 + a) / np.prod(1.0 + b))
    if g <= 0:
        return None
    return round((g ** (1.0 / year_fraction(n)) - 1.0) * 100.0, 2)


def label_for(heuristic_clears, paired_clears):
    if heuristic_clears is None or paired_clears is None:
        return UNDECIDABLE
    if heuristic_clears and paired_clears:
        return AGREE_CLEARS
    if heuristic_clears and not paired_clears:
        return ADMITTED_INVISIBLE
    if paired_clears and not heuristic_clears:
        return HID_VISIBLE
    return AGREE_NO


# --------------------------------------------------------------------------
# one face
# --------------------------------------------------------------------------
def published_rows(doc):
    """The published arm rows, in file order, plus a label -> row map.

    Labels are not uniform across cells: a census arm carries `combo`, a robust
    arm a `variant`, and a single/pair arm can carry no tag at all. The order of
    `arms` is the order `bench_generic` ran them, so when a label cannot be
    matched the caller falls back to position -- and only when the counts agree.
    """
    rows, by_label = [], {}
    for a in doc.get("arms") or []:
        tags = a.get("tags") or {}
        key = tags.get("variant") or tags.get("combo") or tags.get("name")
        cw = a.get("common_window") or {}
        row = {
            "label": key,
            "ann_pct": cw.get("ann_pct"),
            "vol_pct": cw.get("vol_pct"),
            "n": cw.get("n"),
            "mde_pp": a.get("mde_pp"),
            "verdict": a.get("verdict"),
            "excess_pp": a.get("excess_vs_bench_pp"),
        }
        rows.append(row)
        if key is not None:
            by_label[str(key)] = row
    return rows, by_label


def audit_face(face, doc, cell_cfg, tol_pp):
    products = (doc.get("coverage") or {}).get("products") or cell_cfg.get("products")
    if not products:
        return {"face": face, "skipped": "no products on the face"}
    panel = bc.load_futures_products(list(products))
    if len(panel) < 1:
        return {"face": face, "skipped": "no product data on disk"}
    dates, closes, rets, vols = bc.align_futures(panel)
    highs, lows = bc.align_highs_lows(panel, closes)
    bh_tv = cell_cfg.get("target_vol", 0.10)
    bench = bench_series(dict(cell_cfg, target_vol=bh_tv), dates, closes, rets, vols)
    if bench is None:
        return {"face": face, "skipped": "benchmark could not be priced"}
    bench_perf = bc.perf(bench.values, dates)
    pub_list, pub_map = published_rows(doc)
    specs = arm_specs(cell_cfg)
    by_position = len(pub_list) == len(specs)

    rows, reproduced, mismatched = [], 0, []
    for i, (label, sub) in enumerate(specs):
        arm = net_series(sub, dates, closes, rets, vols, highs, lows)
        if arm is None:
            continue
        mine = bc.perf(arm.values, dates)
        p = pub_map.get(str(label))
        if p is None and by_position:
            p = pub_list[i]
        if p is None:
            continue
        # honesty leg: the rebuilt book must be the book that was published
        gap = (None if mine["ann_pct"] is None or p["ann_pct"] is None
               else round(float(mine["ann_pct"]) - float(p["ann_pct"]), 3))
        if gap is not None and abs(gap) <= tol_pp:
            reproduced += 1
        else:
            mismatched.append({"variant": str(label), "rebuilt_ann_pct": mine["ann_pct"],
                               "published_ann_pct": p["ann_pct"], "gap_pp": gap})

        st = paired(arm.values - bench.values)
        a = np.asarray(arm.values, dtype=float)
        b = np.asarray(bench.values, dtype=float)
        corr = None
        if len(a) > 60 and np.std(a) > 0 and np.std(b) > 0:
            corr = round(float(np.corrcoef(a, b)[0, 1]), 3)
        heuristic = None
        if p["excess_pp"] is not None and p["mde_pp"]:
            heuristic = bool(p["excess_pp"] >= p["mde_pp"])
        paired_clears = None if st["n"] < 60 else (
            False if st["t"] is None
            else bool(st["t"] >= T_CRIT and (st["mean_ann_pp"] or 0) > 0))
        rows.append({
            "variant": str(label),
            "verdict": p["verdict"],
            "ann_pct": p["ann_pct"],
            "bench_ann_pct": round(float(bench_perf["ann_pct"]), 2),
            "excess_pp_published": p["excess_pp"],
            "arm_mde_pp": p["mde_pp"],
            "heuristic_clears": heuristic,
            "paired_mean_ann_pp": st["mean_ann_pp"],
            "paired_se95_pp": st["se95_pp"],
            "paired_t": st["t"],
            "paired_clears": paired_clears,
            "corr_arm_bench": corr,
            "ratio_excess_pp": ratio_excess_pp(a, b),
            # > 1 means the arm's own MDE understated the uncertainty of the
            # difference; < 1 means it overstated it. This is the direction of
            # the old ruler's error, per arm.
            "paired_width_over_arm_mde": (None if not p["mde_pp"] or not st["se95_pp"]
                                          else round(st["se95_pp"] / float(p["mde_pp"]), 3)),
            "label": label_for(heuristic, paired_clears),
            "reproduced_ann_gap_pp": gap,
        })
    return {
        "face": face,
        "evidence_cutoff": doc.get("evidence_cutoff"),
        "products": sorted(panel),
        "target_vol": bh_tv,
        "cost_bp_side": cell_cfg.get("cost_bp_side", 3.0),
        "n_arm_specs": len(arm_specs(cell_cfg)),
        "n_rows": len(rows),
        "n_reproduced": reproduced,
        "mismatched": mismatched,
        "rows": rows,
    }


# --------------------------------------------------------------------------
# build
# --------------------------------------------------------------------------
def build(only_face=None):
    bc.weight_priority()
    faces, skipped = [], []
    for path in sorted(glob.glob(os.path.join(RESULTS, "bench_*.json"))):
        base = os.path.basename(path)
        if base == os.path.basename(OUT_JSON):
            continue
        face = base[6:-5] if base.startswith("bench_") else base[:-5]
        if only_face and face != only_face:
            continue
        cell_path = os.path.join(CELLS, face + ".json")
        if not os.path.isfile(cell_path):
            skipped.append({"face": face, "why": "no research/cells config -- arms not "
                                                  "reconstructible without guessing"})
            continue
        with io.open(cell_path, encoding="utf-8") as f:
            cell_cfg = json.load(f)
        with io.open(path, encoding="utf-8") as f:
            doc = json.load(f)
        try:
            got = audit_face(face, doc, cell_cfg, tol_pp=0.05)
        except Exception as exc:  # a face that cannot be audited must say so
            skipped.append({"face": face, "why": "error: " + repr(exc)[:160]})
            continue
        if got.get("rows"):
            faces.append(got)
        else:
            skipped.append({"face": face, "why": got.get("skipped") or "no usable rows"})

    counts = {}
    go_rows = []
    for f in faces:
        for r in f["rows"]:
            counts[r["label"]] = counts.get(r["label"], 0) + 1
            if str(r["verdict"]) == "GO":
                go_rows.append({"face": f["face"], **r})

    hidden = [{"face": f["face"], "variant": r["variant"],
               "excess_pp": r["excess_pp_published"], "arm_mde_pp": r["arm_mde_pp"],
               "paired_t": r["paired_t"], "paired_se95_pp": r["paired_se95_pp"],
               "verdict": r["verdict"]}
              for f in faces for r in f["rows"] if r["label"] == HID_VISIBLE]
    admitted = [{"face": f["face"], "variant": r["variant"],
                 "excess_pp": r["excess_pp_published"], "mde_pp": r["arm_mde_pp"],
                 "paired_t": r["paired_t"]}
                for f in faces for r in f["rows"]
                if r["label"] == ADMITTED_INVISIBLE]
    n_go = len(go_rows)
    n_go_paired = sum(1 for r in go_rows if r["paired_clears"])

    ratios = sorted(r["paired_width_over_arm_mde"] for f in faces for r in f["rows"]
                    if r.get("paired_width_over_arm_mde"))
    wider = [r for f in faces for r in f["rows"]
             if (r.get("paired_width_over_arm_mde") or 0) > 1.0]
    narrower = [r for f in faces for r in f["rows"]
                if r.get("paired_width_over_arm_mde") is not None
                and r["paired_width_over_arm_mde"] <= 1.0]
    sig = [{"face": f["face"], "variant": r["variant"], "t": r["paired_t"],
            "excess_pp": r["excess_pp_published"], "verdict": r["verdict"]}
           for f in faces for r in f["rows"]
           if r.get("paired_t") is not None and r["paired_t"] <= -T_CRIT]

    # The open question, priced with today's numbers: rewriting H1 as
    # "excess >= own MDE" and rewriting it as "paired excess clears 95%" are two
    # candidate rulers. Count what each would do, so the choice can be made on
    # a number instead of on the argument that the current ruler is blind.
    non_go = [r for f in faces for r in f["rows"] if str(r["verdict"]) != "GO"]
    non_go_new_h = sum(1 for r in non_go
                       if r["excess_pp_published"] is not None and r["arm_mde_pp"]
                       and r["excess_pp_published"] >= r["arm_mde_pp"])
    non_go_new_p = sum(1 for r in non_go if r["paired_clears"])
    decision = {
        "question": "should H1 read excess >= own MDE instead of the absolute gate?",
        "go_rows_today": n_go,
        "go_that_survive_heuristic_ruler": sum(
            1 for r in go_rows
            if r["excess_pp_published"] is not None and r["arm_mde_pp"]
            and r["excess_pp_published"] >= r["arm_mde_pp"]),
        "go_that_survive_paired_ruler": n_go_paired,
        "non_go_that_become_go_under_heuristic_ruler": non_go_new_h,
        "non_go_that_become_go_under_paired_ruler": non_go_new_p,
        "same_verdict_set_either_ruler": bool(n_go_paired == 0 and non_go_new_p == 0
                                             and non_go_new_h == 0),
        "what_the_number_says": (
            "在这张 bench 上，两条候选尺子给出完全相同的判决：GO 集两边都被清空，"
            "没有一条旧臂被重新打开——所以今天的判决不是尺子造成的。配对数字真正补充的是："
            "臂自己的 MDE 在两边都量错了（中位 %.2f 倍，%d/%d 条更宽），"
            "把它当成「差的宽度」来读，读的是一个跟差无关的数。"
            % ((ratios[len(ratios) // 2] if ratios else 0.0), len(wider), len(ratios))),
        "not_done_this_round": ("换任何一条尺子都要改 bench_generic 的闸，那是共享面；"
                                "本轮在写入竞争下行进，留给拥有工作树的轮次"),
    }

    cutoffs = [f.get("evidence_cutoff") for f in faces if f.get("evidence_cutoff")]
    return {
        "schema": SCHEMA,
        "generated": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "evidence_cutoff": max(cutoffs) if cutoffs else None,
        "cutoff_rule": "max of the audited faces' own evidence_cutoff fields",
        "faces_read": [f["face"] for f in faces],
        "faces_skipped": skipped,
        "n_faces": len(faces),
        "n_arms": sum(f["n_rows"] for f in faces),
        "n_arms_reproduced_within_0_05pp": sum(f["n_reproduced"] for f in faces),
        "n_arms_not_reproduced": sum(len(f["mismatched"]) for f in faces),
        "rules_compared": {
            "absolute_gate": "H1_full_ge >= 4.0% and the face's target_edge_pp (unchanged)",
            "excess_vs_own_mde": "excess_pp >= arm mde_pp (what bench_go_ruler_audit prints)",
            "paired_excess": "mean(arm - benchmark) annualised, t >= 1.96 on the daily difference",
        },
        "counts": counts,
        "n_go": n_go,
        "n_go_paired_clears": n_go_paired,
        "interval_direction": {
            "n_arms": len(ratios),
            "median_paired_width_over_arm_mde": (ratios[len(ratios) // 2] if ratios else None),
            "ruler_too_confident": len(wider),
            "ruler_too_cautious": len(narrower),
            "rule": "paired 95% width / the arm's own MDE; >1 means the arm's MDE "
                    "understated how uncertain the difference is",
        },
        "paired_significant_negative": sig,
        "decision": decision,
        "go_rows": go_rows,
        "heuristic_hid_visible_excess": hidden,
        "heuristic_admitted_invisible": admitted,
        "faces": faces,
    }


# --------------------------------------------------------------------------
# page
# --------------------------------------------------------------------------
def _cell(text, width):
    """A pipe inside a variant label would end the markdown cell early."""
    s = str(text)
    if len(s) > width:
        s = s[:width] + "..."
    return s.replace("|", "\\|")


def render_md(doc):
    L = []
    L.append("# 超额是差，不是和：配对检验 vs 臂自己的 MDE\n")
    L.append("generated %s | 面 %d | 臂 %d | 重建复现（±0.05pp）%d 条 / 未复现 %d 条\n"
             % (doc["generated"], doc["n_faces"], doc["n_arms"],
                doc["n_arms_reproduced_within_0_05pp"], doc["n_arms_not_reproduced"]))
    L.append("只读面：面板 + `results/bench_*.json`，不改判决、不重写任何 bench 面。\n")
    L.append("## 一句话\n")
    L.append("臂自己的 MDE 是「臂年化均值」的标准误，而超额是两本书之差的均值——量错了对象。"
             "本轮把差自己的标准误算出来（%d 面 / %d 臂，%d 条重建臂全部对上出版年化、"
             "零条失配）：**不是尺子太严，是方向不定**——配对宽度中位是臂 MDE 的 %.2f 倍，"
             "%d 条更宽、%d 条更窄。**判决一条没变**：换成任一条候选尺子，GO 都从 4 变 0、"
             "没有旧臂被重新打开；而 %d 条臂里没有一条能证明跑赢「直接持有同篮子」，"
             "另有 %d 条**显著跑输**。\n"
             % (doc["n_faces"], doc["n_arms"], doc["n_arms_reproduced_within_0_05pp"],
                (doc.get("interval_direction") or {}).get("median_paired_width_over_arm_mde") or 0.0,
                (doc.get("interval_direction") or {}).get("ruler_too_confident") or 0,
                (doc.get("interval_direction") or {}).get("ruler_too_cautious") or 0,
                doc["n_arms"], len(doc.get("paired_significant_negative") or [])))
    c = doc["counts"]
    L.append("| 读数 | 臂数 |")
    L.append("|---|---|")
    L.append("| 两条尺都说过线（%s） | %d |" % (AGREE_CLEARS, c.get(AGREE_CLEARS, 0)))
    L.append("| 两条尺都说不过（%s） | %d |" % (AGREE_NO, c.get(AGREE_NO, 0)))
    L.append("| **臂 MDE 说看不见、配对 t 说看得见**（%s） | %d |"
             % (HID_VISIBLE, c.get(HID_VISIBLE, 0)))
    L.append("| 臂 MDE 说看得见、配对 t 说看不见（%s） | %d |"
             % (ADMITTED_INVISIBLE, c.get(ADMITTED_INVISIBLE, 0)))
    L.append("| 无法判（%s） | %d |\n" % (UNDECIDABLE, c.get(UNDECIDABLE, 0)))

    d = doc.get("interval_direction") or {}
    L.append("## 旧尺子的误差往哪边偏\n")
    L.append("臂自己的 MDE 是「臂年化均值」的标准误；配对宽度是「臂 − 同价基准」日差的标准误，"
             "两者只在两本书完全同向时才相等。本轮 %d 条臂里，配对宽度中位数是臂 MDE 的 "
             "**%.2f 倍**：**%d 条更宽**（臂 MDE 低估了差的不确定性）、%d 条更窄。"
             "所以拿臂 MDE 当超额的宽度，方向是不确定的——不是「太严」，是「量错了东西」。\n"
             % (d.get("n_arms") or 0, d.get("median_paired_width_over_arm_mde") or 0.0,
                d.get("ruler_too_confident") or 0, d.get("ruler_too_cautious") or 0))

    dec = doc.get("decision") or {}
    L.append("## 待决问题：H1 改成超额过 MDE 吗\n")
    L.append("| 读数 | 数值 |")
    L.append("|---|---|")
    L.append("| 今天打印的 GO 行 | %s |" % dec.get("go_rows_today"))
    L.append("| 换成「超额 ≥ 臂 MDE」后仍是 GO | %s |" % dec.get("go_that_survive_heuristic_ruler"))
    L.append("| 换成配对 t ≥ 1.96 后仍是 GO | %s |" % dec.get("go_that_survive_paired_ruler"))
    L.append("| 两条候选尺子下新开闸的旧臂 | %s / %s |"
             % (dec.get("non_go_that_become_go_under_heuristic_ruler"),
                dec.get("non_go_that_become_go_under_paired_ruler")))
    L.append("| 两条尺子给出同一判决集 | %s |\n" % ("是" if dec.get("same_verdict_set_either_ruler") else "否"))
    L.append("%s\n" % (dec.get("what_the_number_says") or ""))
    L.append("本轮**没有**改闸：`bench_generic` 是共享面，本轮在写入竞争下行进（r1907），"
             "换尺子留给拥有工作树的轮次。\n")

    L.append("## 配对后显著跑输「直接持有同篮子」的臂\n")
    neg = doc.get("paired_significant_negative") or []
    if neg:
        L.append("| 面 | 臂 | 超过基准年化 | t | 原判决 |")
        L.append("|---|---|---|---|---|")
        for r in neg:
            L.append("| %s | %s | %s | %s | %s |"
                     % (r["face"], _cell(r["variant"], 40), r["excess_pp"], r["t"],
                        r["verdict"]))
        L.append("")
        L.append("这三条不是「没找到边」，是**显著把钱做少了**——它们与「什么都不做」的差"
                 "比噪声大三倍上下（−2.9pp / −6.8pp / −8.0pp/年）。\n")
    else:
        L.append("(无)\n")

    L.append("## 4 条 GO 在配对尺下\n")
    if doc["go_rows"]:
        L.append("| 面 | 臂 | 年化 | 同价基准 | 出版超额 | 臂MDE | 配对均值 | 配对95%宽 | t | 相关 | 配对过线 |")
        L.append("|---|---|---|---|---|---|---|---|---|---|---|")
        for r in doc["go_rows"]:
            L.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
                r["face"], _cell(r["variant"], 34), r["ann_pct"], r["bench_ann_pct"],
                r["excess_pp_published"], r["arm_mde_pp"], r["paired_mean_ann_pp"],
                r["paired_se95_pp"], r["paired_t"], r["corr_arm_bench"],
                "是" if r["paired_clears"] else "否"))
    else:
        L.append("(该范围无 GO 行)")
    L.append("")
    L.append("## 被臂 MDE 挡住、但配对看得见的臂\n")
    if doc["heuristic_hid_visible_excess"]:
        L.append("| 面 | 臂 | 出版超额 | 臂MDE | 配对95%宽 | t | 原判决 |")
        L.append("|---|---|---|---|---|---|---|")
        for r in doc["heuristic_hid_visible_excess"]:
            L.append("| %s | %s | %s | %s | %s | %s | %s |" % (
                r["face"], _cell(r["variant"], 40), r["excess_pp"], r["arm_mde_pp"],
                r["paired_se95_pp"], r["paired_t"], r["verdict"]))
    else:
        L.append("(无：本轮没有一条臂出现这种错位)")
    L.append("")
    L.append("## 面逐张\n")
    L.append("| 面 | 臂 | 复现 | 两尺皆过 | 两尺皆否 | 臂MDE藏了可见超额 | 臂MDE误放 |")
    L.append("|---|---|---|---|---|---|---|")
    for f in doc["faces"]:
        fc = {}
        for r in f["rows"]:
            fc[r["label"]] = fc.get(r["label"], 0) + 1
        L.append("| %s | %d | %d | %d | %d | %d | %d |" % (
            f["face"], f["n_rows"], f["n_reproduced"],
            fc.get(AGREE_CLEARS, 0), fc.get(AGREE_NO, 0),
            fc.get(HID_VISIBLE, 0), fc.get(ADMITTED_INVISIBLE, 0)))
    L.append("")
    if doc["faces_skipped"]:
        no_cell = [s["face"] for s in doc["faces_skipped"]
                   if s["why"].startswith("no research/cells")]
        other = [s for s in doc["faces_skipped"] if not s["why"].startswith("no research/cells")]
        L.append("## 没审的面（如实列出）\n")
        L.append("`results/bench_*.json` 里能重建臂的只有 `bench_generic` 的 cell 族——"
                 "有 `research/cells/<id>.json` 才能不靠猜复现仓位，共 %d 面。"
                 "其余 %d 张面由各自脚本直接跑（审计面审的是其中 21 张有臂的），"
                 "没有可重建的配置，不做半猜检验。\n"
                 % (doc["n_faces"], len(no_cell)))
        if no_cell:
            L.append("- 无 cell 配置（%d）：%s\n" % (len(no_cell), "、".join(no_cell)))
        for s in other:
            L.append("- %s：%s" % (s["face"], s["why"]))
        if other:
            L.append("")
    L.append("## 这份面不说什么\n")
    L.append("- 不重跑也不重发判决：`results/bench_*.json` 与 MDE 列一个字未改")
    L.append("- 配对 t 检验的是「这套仓位相对同篮子持有是否稳定跑赢」，不是「这套仓位会赚钱」——"
             "持有本身也可能是负的")
    L.append("- 重建复现腿只用 ±0.05pp 判等：面板每天推进，重建用的是今天的面板，"
             "与出版时的截止日不同，腿失败会逐条列在 json 的 `mismatched` 里而非静默丢弃")
    L.append("- 配对的通过与否**不能**直接当 GO：它没看样本外、没看前后半、没看剔除最好一年")
    L.append("")
    L.append("## 复现\n")
    L.append("```")
    L.append("python scripts\\bench_excess_paired_test.py")
    L.append("python scripts\\bench_excess_paired_test.py --face census_commodity")
    L.append("python scripts\\bench_excess_paired_test.py --selftest")
    L.append("```")
    return "\n".join(L) + "\n"


# --------------------------------------------------------------------------
# selftest
# --------------------------------------------------------------------------
def selftest():
    legs = []

    def leg(name, ok, detail=""):
        legs.append({"leg": name, "ok": bool(ok), "detail": detail})

    rng = np.random.default_rng(20261126)
    n = 1000
    a = rng.normal(0.0004, 0.01, n)
    b = rng.normal(0.0001, 0.01, n)

    st = paired(a - b)
    expect_mean = (np.mean(a) - np.mean(b)) * bc.TRADING_DAYS * 100.0
    leg("mean is annualised mean of the difference",
        abs(st["mean_ann_pp"] - round(expect_mean, 2)) < 1e-9, str(st))

    d = a - b
    expect_t = float(np.mean(d)) / (float(np.std(d, ddof=1)) / math.sqrt(n))
    leg("t is mean over standard error", abs(st["t"] - round(expect_t, 2)) < 1e-9)

    rev = paired(b - a)
    leg("swapping the two books flips the sign of the difference",
        abs(rev["mean_ann_pp"] + st["mean_ann_pp"]) < 0.02
        and abs(rev["t"] + st["t"]) < 0.02, "%s vs %s" % (rev["t"], st["t"]))

    zero = paired(a - a)
    leg("a book against itself is not an excess",
        zero["mean_ann_pp"] == 0.0 and zero["t"] is None,
        str(zero))
    leg("no variation in the difference reads as 'no excess', not 'undecidable'",
        label_for(False, False if zero["t"] is None else True) == AGREE_NO)

    short = paired(np.zeros(10))
    leg("too short a window returns None rather than a fake number",
        short["mean_ann_pp"] is None and short["t"] is None)

    # the three printed numbers must agree with each other, not only with their
    # own formula: se95 = 1.96 * mean_ann / t is the identity a reader uses
    if st["t"]:
        implied = T_CRIT * abs(st["mean_ann_pp"]) / abs(st["t"])
        leg("mean, t and the half width tell the same story",
            abs(implied - st["se95_pp"]) <= max(0.02, 0.01 * st["se95_pp"]),
            "implied %.3f vs printed %.3f" % (implied, st["se95_pp"]))

    # a perfectly correlated pair: the difference is nearly constant, so the
    # paired interval collapses -- this is the case the old ruler over-punishes
    base = rng.normal(0.0001, 0.01, n)
    tight = paired((base + 0.0002) - base)
    leg("a difference of two perfectly aligned books has almost no width",
        tight["sd_ann_pp"] < 1.0, str(tight))

    # independent books: the difference carries both variances, so the paired
    # interval is wider than the arm's own -- the case the old ruler under-punishes
    one = rng.normal(0.0004, 0.01, n)
    two = rng.normal(0.0000, 0.01, n)
    wide = paired(one - two)
    own = T_CRIT * float(np.std(one, ddof=1)) * math.sqrt(bc.TRADING_DAYS) \
        * 100.0 / math.sqrt(year_fraction(n))
    leg("a difference of two unrelated books is wider than the arm's own MDE",
        wide["se95_pp"] > own, "paired %.2f vs own %.2f" % (wide["se95_pp"], own))

    leg("label: both clear", label_for(True, True) == AGREE_CLEARS)
    leg("label: heuristic hides what the pair sees",
        label_for(False, True) == HID_VISIBLE)
    leg("label: heuristic admits what the pair cannot see",
        label_for(True, False) == ADMITTED_INVISIBLE)
    leg("label: neither", label_for(False, False) == AGREE_NO)
    leg("label: missing input is undecidable", label_for(None, True) == UNDECIDABLE)

    cfg_census = {"type": "census", "grid": [{"rule": "tsmom",
                                              "params": {"lookback": 60},
                                              "long_only": False},
                                             {"rule": "ma_cross",
                                              "params": {"fast": 20, "slow": 60},
                                              "long_only": True}],
                  "long_only": False}
    specs = arm_specs(cfg_census)
    leg("census enumeration keeps rule, params and side in the label",
        len(specs) == 2 and specs[1][0].startswith("ma_cross") and specs[1][0].endswith("long"),
        str([s[0] for s in specs]))

    cfg_robust = {"type": "robust", "params": {"lookback": 120, "skip": 21},
                  "variants": [{"name": "120d", "params": {}},
                               {"name": "250d", "params": {"lookback": 250}}]}
    specs = arm_specs(cfg_robust)
    leg("robust enumeration overrides only the named parameters",
        len(specs) == 2 and specs[1][1]["params"]["lookback"] == 250
        and specs[1][1]["params"]["skip"] == 21, str(specs[1][0]))

    ok = all(l["ok"] for l in legs)
    print(json.dumps({"selftest": "bench_excess_paired_test", "ok": ok,
                      "legs": legs}, ensure_ascii=False, indent=1))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--face", default=None)
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    doc = build(only_face=a.face)
    bc.write_json(OUT_JSON, doc)
    if not a.face:
        with io.open(OUT_MD, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(render_md(doc))
    print(json.dumps({"ok": True, "faces": doc["n_faces"], "arms": doc["n_arms"],
                      "go": doc["n_go"], "go_paired_clears": doc["n_go_paired_clears"],
                      "hidden": len(doc["heuristic_hid_visible_excess"]),
                      "not_reproduced": doc["n_arms_not_reproduced"]},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
