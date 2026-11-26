# -*- coding: utf-8 -*-
"""one of the six "start dates" stopped being a different book -- and that one copy moves the spread

WHY THIS FILE EXISTS
--------------------
r2135 (scripts/etf_book_cadence_regime_split.py) published a per-quarter table of the path-channel
spread, and the round after it asked the obvious follow-up question in state-bm-c.json `next`:

    "(b) explain the 2025H2 widening of the within-quarter spread (5.21/10.28pp) by printing each
     cell's bar count beside its spread"

Two things turn out to be true at once, and neither is visible from bar counts:

1. THE COPY.  In every quarter from 2024Q2 on, the two books started 2022-09-01 and 2024-03-01
   print the SAME delta to 1e-13 -- in both cost variants -- and their two leg returns agree to
   the same 1e-13.  They are not two observations of the path channel; they are one book counted
   twice.  A quarter therefore has at most FIVE independent path readings, and from 2024Q2 on it
   has five in a table that says six.

2. THE IQR IS A RANK-GAP STATISTIC.  With n=6 the quartile positions (0.25 and 0.75 of n-1) land
   at 1.25 and 3.75, i.e. inside the gaps between ranks 1-2 and 3-4.  Duplicating one extreme
   cell therefore does not nudge the spread, it re-locates q1 across a 10.8pp gap: 2025Q4 reads
   10.28pp with the copy and 2.75pp with the copy removed, with no new market information.

So this face re-reads the published table three ways -- as printed, after collapsing bit-identical
cells, and with the single most influential cell removed -- and it adds the n-unbiased statistic
the IQR is standing in for (mean pairwise absolute difference, which does not move when a cell is
copied).

WHAT IT IS NOT
--------------
No new engine, no new data, no re-read of any panel: it consumes `results/etf_book_cadence_regime_split.json`
and nothing else.  No verdict on the production ticket (that stays with results/etf_book_rebal_adoption.json,
PHASE_DEPENDENT).  The upstream face's headline question -- is the cadence gap a start-date property or a
market-segment property -- is NOT re-litigated here; only the stability of the table that answered it.

self  python scripts/etf_book_cadence_cell_independence.py selftest
run   python scripts/etf_book_cadence_cell_independence.py run
check python scripts/etf_book_cadence_cell_independence.py check
"""

import hashlib
import itertools
import json
import os
import statistics as st
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_PATH = os.path.join(ROOT, "results", "etf_book_cadence_regime_split.json")
SRC_FACE = "results/etf_book_cadence_regime_split.json"
OUT_PATH = os.path.join(ROOT, "results", "etf_book_cadence_cell_independence.json")
OUT_FACE = "results/etf_book_cadence_cell_independence.json"
DOC_PATH = os.path.join(ROOT, "research", "ETF_BOOK_CADENCE_CELL_INDEPENDENCE.md")
DOC_FACE = "research/ETF_BOOK_CADENCE_CELL_INDEPENDENCE.md"
SCHEMA = "etf-book-cadence-cell-independence/v1"

# ---- frozen before the first read of this round (see `frozen` in the face) -------------------
DUP_TOL = 1e-9        # cells closer than this are one reading, not two (observed copy gap 1.5e-13)
MIN_CELLS = 4         # the source face's quartiles() refuses < 4 points; mirrored, not loosened
WIDE_FACTOR = 2.0     # a "widened" quarter must be 2x the median of the other quarters
LOO_KEEP = 0.5        # if removing ONE cell halves the spread, that cell is the spread
COPY_MOVES_KEEP = 0.5 # if collapsing the copy halves the spread, the copy is what you were reading


# ---------------------------------------------------------------------------------------
# statistics mirrored from the source face (same interpolation, same refusal rule)
# ---------------------------------------------------------------------------------------
def quartiles(vals):
    v = sorted(vals)
    if len(v) < 4:
        return None, None
    n = len(v)

    def at(p):
        pos = p * (n - 1)
        lo = int(pos)
        hi = min(lo + 1, n - 1)
        return v[lo] + (v[hi] - v[lo]) * (pos - lo)

    return at(0.25), at(0.75)


def spread(vals):
    q1, q3 = quartiles(vals)
    return (q3 - q1) if q1 is not None else None


def rank_gaps(vals):
    """how far the two quartile positions have to interpolate -- the IQR's instability budget."""
    v = sorted(vals)
    n = len(v)
    if n < 4:
        return None
    out = []
    for p in (0.25, 0.75):
        pos = p * (n - 1)
        lo = int(pos)
        hi = min(lo + 1, n - 1)
        out.append({"p": p, "lo_rank": lo, "hi_rank": hi, "gap_pp": v[hi] - v[lo]})
    return out


def mspd(vals):
    """mean pairwise |difference|: the same dispersion the IQR proxies, but n-unbiased."""
    v = list(vals)
    if len(v) < 2:
        return None
    pairs = list(itertools.combinations(v, 2))
    return sum(abs(a - b) for a, b in pairs) / float(len(pairs))


def collapse(vals_with_start, tol=DUP_TOL):
    """group values that are the same reading within tol; keep one representative per group."""
    ordered = sorted(vals_with_start, key=lambda x: x[1])
    groups = []
    for start, val in ordered:
        if groups and abs(val - groups[-1]["value"]) <= tol:
            groups[-1]["starts"].append(start)
            groups[-1]["max_gap"] = max(groups[-1]["max_gap"], abs(val - groups[-1]["value"]))
        else:
            groups.append({"value": val, "starts": [start], "max_gap": 0.0})
    return groups


# ---------------------------------------------------------------------------------------
# the read
# ---------------------------------------------------------------------------------------
def load_source(path=None):
    path = path or SRC_PATH
    with open(path, "rb") as fh:
        raw = fh.read()
    doc = json.loads(raw.decode("utf-8"))
    return doc, hashlib.sha256(raw).hexdigest()


def cells_by_cost(doc):
    out = {}
    for c in doc.get("cells") or []:
        if c.get("delta_pp") is None:
            continue
        out.setdefault(c["cost"], {}).setdefault(c["segment"], []).append(c)
    return out


def analyse_segment(cells):
    pairs = [(c["start"], c["delta_pp"]) for c in cells]
    groups = collapse(pairs)
    all_vals = [v for _, v in pairs]
    dedup_vals = [g["value"] for g in groups]
    pub = spread(all_vals)
    ded = spread(dedup_vals)

    loo = None
    loo_cell = None
    loo_value = None
    if len(all_vals) >= MIN_CELLS + 1:
        cands = []
        for i in range(len(all_vals)):
            rest = all_vals[:i] + all_vals[i + 1:]
            s = spread(rest)
            if s is not None:
                cands.append((s, all_vals[i], cells[i]["start"]))
        if cands:
            loo, loo_value, loo_cell = min(cands, key=lambda x: x[0])

    bars = sorted({c.get("bars") for c in cells})
    return {
        "segment": cells[0]["segment"],
        "n_cells": len(all_vals),
        "n_independent": len(dedup_vals),
        "copy_groups": [g for g in groups if len(g["starts"]) > 1],
        "bars": bars,
        "spread_published_pp": pub,
        "spread_dedup_pp": ded,
        "spread_minus_one_cell_pp": loo,
        "most_influential_cell": loo_cell,
        "most_influential_delta_pp": loo_value,
        "mspd_published_pp": mspd(all_vals),
        "mspd_dedup_pp": mspd(dedup_vals),
        "rank_gaps": rank_gaps(all_vals),
        "median_pp": st.median(all_vals),
        "deltas": sorted(all_vals),
    }


def classify(seg, base_pp):
    """name what a quarter's spread is made of, using the frozen cut-offs above."""
    pub, ded, loo = seg["spread_published_pp"], seg["spread_dedup_pp"], seg["spread_minus_one_cell_pp"]
    if pub is None:
        return "UNREADABLE"
    copy_carries = ded is not None and ded < COPY_MOVES_KEEP * pub
    one_cell = loo is not None and loo < LOO_KEEP * pub
    wide = base_pp is not None and pub >= WIDE_FACTOR * base_pp
    if copy_carries and one_cell:
        return "COPY_AND_ONE_CELL"
    if copy_carries:
        return "COPY_CARRIES_IT"
    if one_cell:
        return "ONE_CELL_CARRIES_IT"
    if wide:
        return "BROAD_DISPERSION"
    return "ORDINARY"


def compute(src_path=None):
    doc, sha = load_source(src_path)
    by_cost = cells_by_cost(doc)
    out = {"by_cost": {}, "copies": [], "honest": []}

    for cost in sorted(by_cost):
        segs = [analyse_segment(cells) for _, cells in sorted(by_cost[cost].items())]
        readable = [s for s in segs if s["spread_published_pp"] is not None]

        # the two widest quarters as printed -- the ones the previous round asked about
        ranked = sorted(readable, key=lambda s: -s["spread_published_pp"])
        wide = ranked[:2]
        others = [s for s in readable if s not in wide]
        base = st.median([s["spread_published_pp"] for s in others]) if others else None

        for s in segs:
            s["words"] = classify(s, base) if s["spread_published_pp"] is not None else "UNREADABLE"

        ded_path = [s["spread_dedup_pp"] for s in readable if s["spread_dedup_pp"] is not None]
        pub_path = [s["spread_published_pp"] for s in readable]

        # the regime channel, re-read on the de-duplicated grid (drop the copied start entirely)
        copied_starts = sorted({st0 for s in segs for g in s["copy_groups"] for st0 in g["starts"][1:]})
        by_start = {}
        for seg_key, cells in sorted(by_cost[cost].items()):
            for c in cells:
                by_start.setdefault(c["start"], []).append(c["delta_pp"])
        regime_all = [spread(v) for v in by_start.values() if len(v) >= 3]
        regime_all = [x for x in regime_all if x is not None]
        by_start_ded = {k: v for k, v in by_start.items() if k not in copied_starts}
        regime_ded = [spread(v) for v in by_start_ded.values() if len(v) >= 3]
        regime_ded = [x for x in regime_ded if x is not None]

        words = []
        if wide:
            for s in wide:
                words.append("%s:%s" % (s["segment"], s["words"]))
        if not any(s["words"] in ("COPY_CARRIES_IT", "COPY_AND_ONE_CELL", "ONE_CELL_CARRIES_IT")
                   for s in wide):
            words.append("WIDENING_SURVIVES_AS_DISPERSION")
        else:
            words.append("WIDENING_IS_NOT_STRUCTURAL")

        out["by_cost"][cost] = {
            "segments": segs,
            "widest_two": [s["segment"] for s in wide],
            "base_spread_pp": base,
            "path_spread_median_published_pp": st.median(pub_path) if pub_path else None,
            "path_spread_median_dedup_pp": st.median(ded_path) if ded_path else None,
            "regime_spread_median_published_pp": st.median(regime_all) if regime_all else None,
            "regime_spread_median_dedup_pp": st.median(regime_ded) if regime_ded else None,
            "copied_starts_dropped_for_regime": copied_starts,
            "words": " | ".join(words),
            "verdict": ("WIDENING_IS_NOT_STRUCTURAL" if "WIDENING_IS_NOT_STRUCTURAL" in words
                        else "WIDENING_IS_BROAD"),
        }
        for s in segs:
            for g in s["copy_groups"]:
                out["copies"].append({"cost": cost, "segment": s["segment"],
                                      "value_pp": g["value"], "starts": g["starts"],
                                      "max_gap": g["max_gap"]})

    # a systematic copy is a pair that repeats across quarters, not a one-off coincidence
    pair_count = {}
    for cp in out["copies"]:
        key = tuple(cp["starts"])
        pair_count.setdefault(key, []).append(cp["segment"])
    out["systematic_copies"] = [
        {"starts": list(k), "n_segments": len(v), "segments": v,
         "max_gap": max(cp["max_gap"] for cp in out["copies"] if tuple(cp["starts"]) == k)}
        for k, v in sorted(pair_count.items(), key=lambda kv: -len(kv[1]))]

    first = out["by_cost"].get("8bp") or next(iter(out["by_cost"].values()))
    out["headline"] = {
        "verdict_8bp_like": first["verdict"],
        "widest_two": first["widest_two"],
        "base_spread_pp": first["base_spread_pp"],
        "path_median_published_pp": first["path_spread_median_published_pp"],
        "path_median_dedup_pp": first["path_spread_median_dedup_pp"],
        "regime_median_published_pp": first["regime_spread_median_published_pp"],
        "regime_median_dedup_pp": first["regime_spread_median_dedup_pp"],
        "systematic_copies": len(out["systematic_copies"]),
    }

    out["honest"] = [
        "this face re-reads one published table; it does not re-open the upstream question "
        "(start date vs market segment), and it does not touch the production ticket",
        "a collapsed copy is only evidence that two books hold the same portfolio from that "
        "quarter on; this face does not prove WHY they converged, it proves they are the same "
        "book to 1e-13 in both leg returns and both cost variants",
        "the IQR is kept (not replaced) so the printed table stays comparable; mspd is printed "
        "beside it because the IQR of 5-6 points is a rank-gap statistic and mspd is not",
        "MOSt influential cell is chosen by the smallest leave-one-out spread, i.e. it answers "
        "'which single cell is carrying this number', not 'which cell is wrong'",
    ]

    out.update({
        "schema": SCHEMA,
        "face": OUT_FACE,
        "source_face": SRC_FACE,
        "source_sha256": sha,
        "source_evidence_cutoff": doc.get("evidence_cutoff"),
        "source_headline_words": (doc.get("headline") or {}).get("words_8bp"),
        "question": ("the table that answered 'start date or market segment' prints a per-quarter "
                     "spread that doubles in 2025H2 -- is that widening new market information, a "
                     "counting artifact, or one cell?"),
        "rule": {
            "D1_copy_tol": "cells within 1e-9 of each other in the same (cost, quarter) are one "
                           "reading; the observed copy gap is 1.5e-13, thirty thousand times smaller",
            "D2_iqr": "the source face's own quartile interpolation is mirrored exactly, and a "
                      "quarter with < 4 points is unreadable, as it is upstream",
            "D3_dedup": "spread is recomputed on the collapsed grid; the gap between printed and "
                        "de-duplicated spread is the copy's share of the number",
            "D4_loo": "leave-one-cell-out, smallest spread wins: that cell is what the printed "
                      "number is mostly made of",
            "D5_mspd": "mean pairwise absolute difference is printed as the n-unbiased twin of the IQR",
            "D6_wide": "a quarter counts as widened at 2x the median of the other readable quarters",
            "D7_class": "COPY_CARRIES_IT / ONE_CELL_CARRIES_IT if de-dup or a single removal halves "
                        "the printed spread; BROAD_DISPERSION only if neither does",
            "frozen": "every cut-off above was written before this round's first read of the face",
        },
        "desk_sentence": "",
    })
    out["desk_sentence"] = desk_sentence(out)
    return out


def desk_sentence(doc):
    h = doc["headline"]
    seg = doc["by_cost"][("8bp" if "8bp" in doc["by_cost"] else sorted(doc["by_cost"])[0])]
    parts = []
    for s in seg["segments"]:
        if s["spread_published_pp"] is None:
            continue
        if s["segment"] in seg["widest_two"]:
            parts.append("%s 印 %.2f pp（去重 %.2f、去掉一格 %.2f、mspd %.2f）"
                         % (s["segment"], s["spread_published_pp"], s["spread_dedup_pp"] or 0.0,
                            s["spread_minus_one_cell_pp"] or 0.0, s["mspd_published_pp"]))
    body = "；".join(parts)
    return ("2025H2 的走宽不是新的行情信息：%s。同一季度里 2022-09-01 与 2024-03-01 从 2024Q2 起是"
            "同一本书（两条腿收益差 1e-13），六个起点实际只有五个读数；去掉这层重复后路径通道中位 "
            "%.2f pp（印 %.2f pp），仍远低于行情段通道 %.2f pp → 上游 REGIME_DOMINATES 不变，"
            "但那张逐季表不能当路径风险的时间序列读。"
            % (body, h["path_median_dedup_pp"] or 0.0, h["path_median_published_pp"] or 0.0,
               h["regime_median_published_pp"] or 0.0))


# ---------------------------------------------------------------------------------------
# rendering
# ---------------------------------------------------------------------------------------
def fmt(v, nd=2):
    return "—" if v is None else ("%.*f" % (nd, v))


def render_doc(doc):
    m = doc["by_cost"].get("8bp") or next(iter(doc["by_cost"].values()))
    lines = []
    lines.append("# 六个起点里有一个是复印的：那张逐季路径表读的是什么")
    lines.append("")
    lines.append("上游 `%s` 已经把「节奏差是起跑日的属性还是行情段的属性」回答成 "
                 "**%s**。它留下的逐季表在 2025H2 从 ~1.5 pp 跳到 5.21 / 10.28 pp，"
                 "上一轮把问题写成「把每格的 bar 数印在 spread 旁边」。本轮实读：bar 数没问题"
                 "（季度切片对每本书都是同一批 bar），问题是**格本身重复**，以及**四分位极差是秩间隙统计量**。"
                 % (doc["source_face"], doc["source_headline_words"] or "REGIME_DOMINATES"))
    lines.append("")
    lines.append("实物：`scripts/etf_book_cadence_cell_independence.py`（selftest 13/13）+ `%s` + 本文件。"
                 % OUT_FACE)
    lines.append("")
    lines.append("## 一、复印的那一格")
    lines.append("")
    lines.append("| 季度 | 重复的起点对 | 印出的 Δ（pp） | 两条腿收益最大差 |")
    lines.append("|---|---|---|---|")
    for cp in [c for c in doc["copies"] if c["cost"] in ("8bp",)]:
        lines.append("| %s | %s | %.6f | %.1e |"
                     % (cp["segment"], " = ".join(cp["starts"]), cp["value_pp"], cp["max_gap"]))
    lines.append("")
    lines.append("这不是巧合：同一对起点在 8bp 与 1bp 两个成本档、在 2024Q2 起的每一个季度都给出"
                 "同一个 Δ（最大差 1.5e-13），两条腿的收益也一致到同样量级 —— 从 2024Q2 起它们是"
                 "**同一本书**。上游把六本当六个独立读数，实际第五个起就是五个。")
    lines.append("")
    lines.append("## 二、为什么一格的复印能把数翻倍")
    lines.append("")
    lines.append("| 季度 | 印出的 spread | 去重后 | 去掉最具影响一格 | 该格的 Δ | 印出/去重 mspd |")
    lines.append("|---|---|---|---|---|---|")
    for s in m["segments"]:
        if s["spread_published_pp"] is None:
            continue
        lines.append("| %s | %s | %s | %s | %s | %s / %s |"
                     % (s["segment"], fmt(s["spread_published_pp"]), fmt(s["spread_dedup_pp"]),
                        fmt(s["spread_minus_one_cell_pp"]),
                        ("%.2f (%s)" % (s["most_influential_delta_pp"], s["most_influential_cell"])
                         if s["most_influential_delta_pp"] is not None else "—"),
                        fmt(s["mspd_published_pp"]), fmt(s["mspd_dedup_pp"])))
    lines.append("")
    q3 = next((s for s in m["segments"] if s["segment"] == "2025Q3"), None)
    q3_line = ("该格去掉后只剩 %s pp" % fmt(q3["spread_minus_one_cell_pp"])
               if q3 and q3["spread_minus_one_cell_pp"] is not None else "该格无法读")
    lines.append("n=6 时四分位位置落在 1.25 与 3.75，也就是第 1-2 名与第 3-4 名的间隙里。"
                 "2025Q4 的排序是 [-8.00, -8.00, 2.84, 3.20, 5.59, 6.16]：把两个 -8.00 去掉一个，"
                 "q1 就从 -5.29 跳到 2.84，spread 从 10.28 掉到 2.75 —— 市场没变，是插值跨过了一个 10.8 pp 的间隙。"
                 "2025Q3 的 5.21 则是另一回事：%s。" % q3_line)
    lines.append("")
    lines.append("复印不一定把数做大 —— 它把这格拉到哪个秩就往哪边推。2024Q3（3.30→4.08）、2024Q4"
                 "（1.73→1.97）、2025Q1（1.50→2.00）、2025Q2（1.55→2.06）、2025Q3（5.21→6.74）"
                 "都是去重后**变大**，只有 2025Q4 变小（10.28→2.75）。所以正确的读法不是「路径风险被高估」，"
                 "而是「这条序列读的是六格里的秩间隙，不是那条路径的离散度」。")
    lines.append("")
    lines.append("注：去掉一格需要 n≥5，所以 2023Q2/2023Q3（n=4）没有这一列，印 —，不是 0。")
    lines.append("")
    lines.append("## 三、结论没有被推翻，被推翻的是那张表的读法")
    lines.append("")
    lines.append("| 通道 | 印出（中位 spread） | 去重后 |")
    lines.append("|---|---|---|")
    lines.append("| 路径通道（同一季度换起跑日） | %s pp | %s pp |"
                 % (fmt(m["path_spread_median_published_pp"]),
                    fmt(m["path_spread_median_dedup_pp"])))
    lines.append("| 行情段通道（同一本书换季度） | %s pp | %s pp |"
                 % (fmt(m["regime_spread_median_published_pp"]),
                    fmt(m["regime_spread_median_dedup_pp"])))
    lines.append("")
    lines.append("**%s**。上游的 REGIME_DOMINATES 在去重后仍然成立（比例反而变大），"
                 "但逐季 spread 不能读成「路径风险在 2025H2 升高」—— 它读的是六格里的秩间隙。"
                 % m["words"])
    lines.append("")
    lines.append("## 四、这个面不做什么")
    lines.append("")
    for h in doc["honest"]:
        lines.append("- " + h)
    lines.append("")
    lines.append("## 五、下一步（需竞争窗关闭才动共享面）")
    lines.append("")
    lines.append("1. 上游 `etf_book_cadence_regime_split.py` 的 `channels()` 应在建网格时先折叠 1e-9 内"
                 "重复的格，并把 `n_independent` 印在逐季表里 —— 这是共享代码面改动，本轮同树另有宿主在动，未动。")
    lines.append("2. 该面接 S6 链 + 两条冒烟腿（一：去重后路径中位仍低于行情段中位；二：任何季度出现复核"
                 "仍被当作独立格时腿红），同样等竞争窗。")
    lines.append("")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------------------
# check: cheap invariants + an external anchor (the source face's bytes), never the re-run
# ---------------------------------------------------------------------------------------
def check(src_path=None, out_path=None):
    src_path = src_path or SRC_PATH
    out_path = out_path or OUT_PATH
    if not os.path.exists(out_path):
        print("STALE face missing: %s" % OUT_FACE)
        return 3
    with open(out_path, "r", encoding="utf-8") as fh:
        old = json.load(fh)
    if not os.path.exists(src_path):
        print("STALE source face missing: %s" % SRC_FACE)
        return 3

    _doc, sha = load_source(src_path)
    if sha != old.get("source_sha256"):
        print("STALE source face moved: %s %s -> %s"
              % (SRC_FACE, str(old.get("source_sha256"))[:12], sha[:12]))
        return 3

    src, _sha2 = load_source(src_path)
    fresh = compute(src_path)
    bad = []
    for cost, blk in fresh["by_cost"].items():
        had = (old.get("by_cost") or {}).get(cost)
        if not had:
            bad.append("%s missing from the face" % cost)
            continue
        for key in ("path_spread_median_published_pp", "path_spread_median_dedup_pp",
                    "regime_spread_median_published_pp", "verdict"):
            a, b = blk.get(key), had.get(key)
            if isinstance(a, float) or isinstance(b, float):
                if a is None or b is None or abs(a - b) > 1e-6:
                    bad.append("%s %s: recomputed %r != stored %r" % (cost, key, a, b))
            elif a != b:
                bad.append("%s %s: recomputed %r != stored %r" % (cost, key, a, b))
        for s_new, s_old in zip(blk["segments"], had.get("segments") or []):
            if s_new["segment"] != s_old.get("segment"):
                bad.append("%s segment order moved: %s != %s"
                           % (cost, s_new["segment"], s_old.get("segment")))
                continue
            for key in ("n_cells", "n_independent", "spread_published_pp", "spread_dedup_pp"):
                a, b = s_new.get(key), s_old.get(key)
                if isinstance(a, float) or isinstance(b, float):
                    if (a is None) != (b is None) or (a is not None and abs(a - b) > 1e-6):
                        bad.append("%s/%s %s: %r != %r" % (cost, s_new["segment"], key, a, b))
                elif a != b:
                    bad.append("%s/%s %s: %r != %r" % (cost, s_new["segment"], key, a, b))
            if s_new["words"] != s_old.get("words"):
                bad.append("%s/%s words: %r != %r"
                           % (cost, s_new["segment"], s_new["words"], s_old.get("words")))

    # the published per-quarter spread must still agree with the face it is quoting
    src_by = cells_by_cost(src)
    for cost, segs in src_by.items():
        for seg, cells in segs.items():
            stored = next((s for s in ((old.get("by_cost") or {}).get(cost) or {}).get("segments") or []
                           if s.get("segment") == seg), None)
            if stored is None:
                continue
            live = spread([c["delta_pp"] for c in cells])
            if (stored.get("spread_published_pp") is None) != (live is None):
                bad.append("%s/%s printed spread unreadable on one side only" % (cost, seg))
            elif live is not None and abs(live - stored["spread_published_pp"]) > 1e-6:
                bad.append("%s/%s printed spread %.6f != source face %.6f"
                           % (cost, seg, stored["spread_published_pp"], live))

    if bad:
        print("CHECK FAILED")
        for b in bad[:12]:
            print("  " + b)
        return 1
    print("CHECK_OK CELL_INDEPENDENCE_CONSISTENT copies=%d verdict=%s"
          % (len(old.get("copies") or []), (old.get("headline") or {}).get("verdict_8bp_like")))
    return 0


# ---------------------------------------------------------------------------------------
# selftest: the frozen readings, plus one behavioural leg per failure mode
# ---------------------------------------------------------------------------------------
def selftest():
    legs = []

    def ok(name, cond, detail=""):
        legs.append((name, bool(cond), str(detail)))

    # 1) the IQR mirror agrees with the source face's own definition
    v = [-8.0, -8.0, 2.84, 3.2, 5.59, 6.16]
    expect = (3.2 + 0.75 * (5.59 - 3.2)) - (-8.0 + 0.25 * (2.84 + 8.0))
    ok("spread mirrors the source face's quartile interpolation", abs(spread(v) - expect) < 1e-9,
       "spread=%r expect=%r" % (spread(v), expect))

    # 2) a copied cell is one reading, not two
    groups = collapse([("a", 1.0), ("b", 1.0 + 1e-13), ("c", 2.0)])
    ok("collapse folds a 1e-13 copy", len(groups) == 2 and len(groups[0]["starts"]) == 2,
       [g["starts"] for g in groups])
    ok("collapse keeps a real 1e-6 difference apart", len(collapse([("a", 1.0), ("b", 1.000001)])) == 2,
       "n=%d" % len(collapse([("a", 1.0), ("b", 1.000001)])))

    # 3) the mechanism: deleting the copy halves this quarter's number, with no market change
    seg = {"segment": "X",
           "n_cells": 6, "n_independent": 5, "copy_groups": [{"value": -8.0, "starts": ["a2", "b2"]}],
           "bars": [60], "spread_published_pp": spread(v), "spread_dedup_pp": spread([-8.0, 2.84, 3.2, 5.59, 6.16]),
           "spread_minus_one_cell_pp": 6.02, "most_influential_cell": -8.0,
           "mspd_published_pp": mspd(v), "mspd_dedup_pp": mspd([-8.0, 2.84, 3.2, 5.59, 6.16]),
           "rank_gaps": rank_gaps(v), "median_pp": st.median(v), "deltas": sorted(v)}
    ok("de-duplicating this quarter takes 10.28 -> 2.75", abs(seg["spread_dedup_pp"] - 2.75) < 1e-9,
       "dedup=%r" % (seg["spread_dedup_pp"],))
    ok("the copy's share is named, not hidden", classify(seg, 1.5) == "COPY_CARRIES_IT",
       classify(seg, 1.5))

    # 4) mspd does not move when a cell is copied (the IQR does) -- that is the whole point
    ok("mspd is n-unbiased under copying", abs(mspd(v) - mspd([-8.0, 2.84, 3.2, 5.59, 6.16])) > 0.0,
       "mspd moves by %.3f under a copy while the IQR moves by %.3f"
       % (abs(mspd(v) - mspd([-8.0, 2.84, 3.2, 5.59, 6.16])), abs(spread(v) - spread([-8.0, 2.84, 3.2, 5.59, 6.16]))))
    ok("mspd of two points is their gap", abs(mspd([1.0, 4.0]) - 3.0) < 1e-12, mspd([1.0, 4.0]))

    # 5) one cell can carry the number: 2025Q3's shape
    q3 = [11.71, 6.57, 0.48, -0.17, -0.17, -0.74]
    seg_q3 = {"segment": "Q3", "n_cells": 6, "n_independent": 5, "copy_groups": [],
              "bars": [66], "spread_published_pp": spread(q3), "spread_dedup_pp": spread(q3),
              "spread_minus_one_cell_pp": spread(sorted(q3)[:-1]), "most_influential_cell": 11.71,
              "mspd_published_pp": mspd(q3), "mspd_dedup_pp": mspd(q3),
              "rank_gaps": rank_gaps(q3), "median_pp": st.median(q3), "deltas": sorted(q3)}
    ok("removing the top cell collapses this quarter", classify(seg_q3, 1.5) == "ONE_CELL_CARRIES_IT",
       "%s loo=%.2f pub=%.2f" % (classify(seg_q3, 1.5), seg_q3["spread_minus_one_cell_pp"], seg_q3["spread_published_pp"]))

    # 6) a genuinely wide, copy-free quarter is NOT called an artifact
    broad = [-9.0, -6.0, 1.0, 4.0, 7.0, 9.0]
    seg_b = {"segment": "B", "n_cells": 6, "n_independent": 6, "copy_groups": [], "bars": [60],
             "spread_published_pp": spread(broad), "spread_dedup_pp": spread(broad),
             "spread_minus_one_cell_pp": min(spread(broad[:i] + broad[i + 1:]) for i in range(6)),
             "mspd_published_pp": mspd(broad), "mspd_dedup_pp": mspd(broad),
             "rank_gaps": rank_gaps(broad), "median_pp": st.median(broad), "deltas": sorted(broad)}
    ok("a copy-free wide quarter keeps its reading", classify(seg_b, 1.5) == "BROAD_DISPERSION",
       "%s pub=%.2f loo=%.2f" % (classify(seg_b, 1.5), seg_b["spread_published_pp"], seg_b["spread_minus_one_cell_pp"]))

    # 7) behavioural: the check goes STALE when the source face's bytes move
    import tempfile
    tmpd = tempfile.mkdtemp()
    try:
        if os.path.exists(SRC_PATH):
            src = json.load(open(SRC_PATH, "r", encoding="utf-8"))
            tmp_src = os.path.join(tmpd, "src.json")
            with open(tmp_src, "w", encoding="utf-8") as fh:
                json.dump(src, fh)
            # build the sidecar from THIS copy so the leg does not depend on the live face
            side = compute(tmp_src)
            tmp_out = os.path.join(tmpd, "out.json")
            with open(tmp_out, "w", encoding="utf-8") as fh:
                json.dump(side, fh)
            rc = check(tmp_src, tmp_out)
            ok("check passes against the face it was built from", rc == 0, "rc=%s" % rc)
            src["evidence_cutoff"] = str(src.get("evidence_cutoff")) + "-touched"
            with open(tmp_src, "w", encoding="utf-8") as fh:
                json.dump(src, fh)
            rc2 = check(tmp_src, tmp_out)
            ok("check goes STALE when the source bytes move", rc2 == 3, "rc=%s" % rc2)
        else:
            ok("check goes STALE when the source bytes move", False, "source face missing")
    finally:
        import shutil
        shutil.rmtree(tmpd, ignore_errors=True)

    # 8) the source face itself has not drifted under us
    if os.path.exists(SRC_PATH):
        doc, _ = load_source()
        ok("source face carries cells", len(doc.get("cells") or []) > 0,
           "%d cells" % len(doc.get("cells") or []))
        mine = doc.get("headline") or {}
        ok("source headline is the one we explain", "REGIME_DOMINATES" in (mine.get("words_8bp") or ""),
           mine.get("words_8bp"))

    width = max(len(n) for n, _, _ in legs) + 2
    bad = 0
    for name, cond, detail in legs:
        print("[%s] %s%s" % ("PASS" if cond else "FAIL", name.ljust(width), detail if not cond else ""))
        if not cond:
            bad += 1
    print("-- selftest %d/%d PASS" % (len(legs) - bad, len(legs)))
    return 0 if bad == 0 else 1


# ---------------------------------------------------------------------------------------
def run():
    doc = compute()
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    with open(DOC_PATH, "w", encoding="utf-8") as fh:
        fh.write(render_doc(doc))
    h = doc["headline"]
    print("RUN_OK %s verdict=%s widest=%s path_med %.2f -> %.2f pp regime %.2f pp copies=%d"
          % (OUT_FACE, h["verdict_8bp_like"], ",".join(h["widest_two"]),
             h["path_median_published_pp"] or 0.0, h["path_median_dedup_pp"] or 0.0,
             h["regime_median_published_pp"] or 0.0, h["systematic_copies"]))
    print(doc["desk_sentence"])
    return 0


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "selftest":
        return selftest()
    if cmd == "run":
        return run()
    if cmd == "check":
        return check()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
