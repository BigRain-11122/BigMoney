#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""the one book that clears the yearly gate does it by 0.09pp of top-2 share --
what does that margin cost, and how much of each book's money is one year?

WHY THIS FILE EXISTS
--------------------
r1921 priced the gate-passing arms against cost and found the pass belongs to the
10bp assumption, not to any lever. r1926/r1929 kept using the same sentence on
the reader faces: "passes by 0.09 / 0.32 pp". Nobody has yet said what a
percentage point of *annual return* is worth in money, so every reader still has
to multiply by hand -- and a reader who does not multiply reads "ADMIT by a
hair" as "a slightly thin pass" instead of "one year's rounding decision".

This face answers three questions the yearly gate refuses to answer for itself:

  1. how much of each book's lifetime money came from its single best year?
     (terminal value is a product, not a sum, so the answer is not the same as
     the published top-2 share, which is an arithmetic share of annual returns)
  2. what would the book have been worth without that year, in CNY?
  3. how far can the best year move before the verdict flips, in pp *and* in CNY?
     (closed form on the published rule, line imported from the gate itself)

Readings are honest by construction:
  * the gate line and the yearly metrics are imported from candidate_year_gate,
    never transcribed; the top-2 share this face re-computes is asserted equal
    to the one YEAR-GATE published, so a disagreement is reported, not hidden;
  * money only appears where a capital is stated (1,000,000 CNY, the same
    seed the live book uses) -- an unstated capital prints no total;
  * the best-year attribution is a decomposition of a product, so it does not
    add up across years and is not printed as if it did (top-3 gain shares are
    printed separately from the leave-one-out multiples);
  * a partial year (2026 here) is disclosed wherever its own number is used;
  * this face does not move any verdict: it re-reads one line of the gate and
    prices the distance to it.

self  python scripts/etf_book_year_concentration_money.py selftest    # synthetic, fast
run   python scripts/etf_book_year_concentration_money.py run         # reads published face
check python scripts/etf_book_year_concentration_money.py check       # re-derive from receipt
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import candidate_year_gate as G

SOURCE_FACE = os.path.join(ROOT, "results", "etf_book_year_gate", "YEAR-GATE.json")
OUT = os.path.join(ROOT, "results", "etf_book_year_concentration_money.json")
DOC = os.path.join(ROOT, "research", "ETF_BOOK_YEAR_CONCENTRATION_MONEY.md")
CAPITAL_CNY = 1_000_000.0
FACE = "etf_book_year_concentration_money"


# --------------------------------------------------------------------------- #
# arithmetic (pure, so the selftest can pin every leg)
# --------------------------------------------------------------------------- #
def multiple_of(rets):
    """terminal growth of a year-return series in percent."""
    m = 1.0
    for r in rets:
        m *= (1.0 + float(r) / 100.0)
    return m


def cagr_pct_of(multiple, years):
    if years <= 0 or multiple <= 0:
        return None
    return (multiple ** (1.0 / float(years)) - 1.0) * 100.0


def best_year_crossing(best, second, other_sum, line):
    """closed form for the best-year return that puts top-2 share *exactly* on line.

    share(r) = (r + second) / (r + other_sum), solved for r.  Returns None when
    the rule cannot cross (line == 1.0 has no finite solution).
    """
    den = 1.0 - float(line)
    if abs(den) < 1e-12:
        return None
    return (float(line) * float(other_sum) - float(second)) / den


def attribution(rows, capital=CAPITAL_CNY, line=None):
    """Decompose one book's yearly rows into money terms.

    rows = [{"year": "2020", "net_pct": x, "partial": bool}, ...] in year order.
    """
    if not rows or len(rows) < 2:
        return {"refused": "fewer than two years: concentration is undefined"}
    line = float(G.TOP2_SHARE_MAX if line is None else line)

    years = [str(r["year"]) for r in rows]
    rets = [float(r["net_pct"]) for r in rows]
    partial = {str(r["year"]): bool(r.get("partial")) for r in rows}

    full = multiple_of(rets)
    n = len(rets)
    cagr = cagr_pct_of(full, n)

    # ---- leave-one-year-out: money without that year -------------------------
    loo = {}
    for i, y in enumerate(years):
        rest = rets[:i] + rets[i + 1:]
        m_wo = multiple_of(rest)
        loo[y] = {
            "net_pct": round(rets[i], 6),
            "partial": partial[y],
            "multiple_without": round(m_wo, 12),
            "retained_fraction": round(m_wo / full, 12) if full else None,
            "cagr_without_pct": (round(cagr_pct_of(m_wo, n - 1), 6)
                                 if n > 1 else None),
            "value_without_cny": (round(capital * m_wo, 2)
                                  if capital is not None else None),
        }

    # ---- best year in money --------------------------------------------------
    order = sorted(range(n), key=lambda i: rets[i], reverse=True)
    bi = order[0]
    best_y, best_r = years[bi], rets[bi]
    second_r = rets[order[1]] if n > 1 else None
    other_sum = sum(rets) - best_r
    total_sum = sum(rets)

    # capital standing before the best year compounds -- that is what makes a pp
    # of the best year worth a different amount of money than a pp of 2021
    cap_before = capital
    if capital is not None:
        for i in range(bi):
            cap_before *= (1.0 + rets[i] / 100.0)

    m_wo_best = multiple_of(rets[:bi] + rets[bi + 1:])
    gain_cny = (capital * (full - m_wo_best)) if capital is not None else None
    gain_share_of_gain = ((full - m_wo_best) / (full - 1.0)
                          if full != 1.0 else None)

    # ---- top-3 gain shares (a separate reading, does not sum with the above) --
    per_year_gain_share = {}
    if full != 1.0:
        for i, y in enumerate(years):
            m_i = multiple_of(rets[:i] + rets[i + 1:])
            per_year_gain_share[y] = round((full - m_i) / (full - 1.0), 6)
    top3 = sorted(per_year_gain_share.items(), key=lambda kv: kv[1],
                  reverse=True)[:3]

    # ---- distance to the line, in pp and in money ----------------------------
    top2_share = (sorted(rets, reverse=True)[0] + sorted(rets, reverse=True)[1]) / total_sum \
        if total_sum > 0 else None
    r_star = best_year_crossing(best_r, second_r, other_sum, line)
    margin = {
        "line": line,
        "top2_share_recomputed": (round(top2_share, 6)
                                  if top2_share is not None else None),
        "on_pass_side": (bool(top2_share <= line)
                         if top2_share is not None else None),
        "best_year": best_y,
        "best_year_pct": round(best_r, 6),
        "best_year_pct_star": (round(r_star, 6) if r_star is not None else None),
        "delta_pp": (round(r_star - best_r, 6) if r_star is not None else None),
        "delta_cny": (round(cap_before * (r_star - best_r) / 100.0, 2)
                      if (r_star is not None and capital is not None) else None),
        "capital_before_best_cny": (round(cap_before, 2)
                                    if capital is not None else None),
        "best_year_partial": partial[best_y],
    }

    return {
        "years": years,
        "returns_pct": [round(r, 6) for r in rets],
        "partial_years": [y for y in years if partial[y]],
        "full_multiple": round(full, 12),
        "cagr_recomputed_pct": (round(cagr, 6) if cagr is not None else None),
        "value_cny": (round(capital * full, 2) if capital is not None else None),
        "middle_value_cny": (round(capital * (full + 1.0) / 2.0, 2)
                             if capital is not None else None),
        "best_year": {
            "year": best_y,
            "net_pct": round(best_r, 6),
            "partial": partial[best_y],
            "multiple_added": round(full / m_wo_best, 12) if m_wo_best else None,
            "gain_cny": (round(gain_cny, 2) if gain_cny is not None else None),
            "share_of_lifetime_gain": (round(gain_share_of_gain, 6)
                                       if gain_share_of_gain is not None else None),
        },
        "leave_one_year_out": loo,
        "gain_share_by_year": per_year_gain_share,
        "top3_gain_share": [{"year": y, "share": s} for y, s in top3],
        "margin": margin,
    }


def separation(books, key="share_of_lifetime_gain"):
    """Does the top-2 line separate books by how much ONE year is worth?

    The gate compares an arithmetic share of annual returns. Money compounds, so
    a book can clear the share line while a single year owns most of its gain.
    This reports which shape the published set has -- it does not judge the line.
    """
    rows = []
    for b in books:
        d = b.get("derived") or {}
        if d.get("refused"):
            continue
        sh = (d.get("best_year") or {}).get(key)
        on_pass = (d.get("margin") or {}).get("on_pass_side")
        if sh is None or on_pass is None:
            continue
        rows.append({"book": b["book"], key: sh, "on_pass_side": bool(on_pass)})
    passing = [r for r in rows if r["on_pass_side"]]
    failing = [r for r in rows if not r["on_pass_side"]]
    if not passing or not failing:
        return {"verdict": "ONE_SIDED",
                "note": "every published book lands on the same side of the line, "
                        "so this set cannot show whether the line separates them",
                "rows": rows}
    lo = min(r[key] for r in failing)
    hi = max(r[key] for r in failing)
    inside = [r for r in passing if lo <= r[key] <= hi]
    spread = (min(p[key] for p in passing) - hi) if not inside else 0.0
    verdict = ("THE_LINE_DOES_NOT_SEPARATE_ONE_YEAR_DEPENDENCE"
               if inside else "THE_LINE_SEPARATES_ONE_YEAR_DEPENDENCE")
    return {
        "verdict": verdict,
        "metric": key,
        "failing_range": [round(lo, 6), round(hi, 6)],
        "passing_inside_failing_range": [r["book"] for r in inside],
        "spread_pp": round(100.0 * spread, 4),
        "thin": bool(abs(spread) < 0.05),
        "one_year_books": [r["book"] for r in rows if r[key] >= 0.50],
        "rows": rows,
        "note": ("the book that clears the top-2 line is not the one whose money "
                 "depends least on a single year" if inside else
                 "the book that clears the top-2 line also depends least on a "
                 "single year, so the share line happens to sort the same way -- "
                 "by {sp:.2f}pp, and every book in the set still takes at least "
                 "half its lifetime gain from one year ({ob})".format(
                     sp=100.0 * spread,
                     ob=", ".join(r["book"] for r in rows if r[key] >= 0.50) or "none")),
    }


# --------------------------------------------------------------------------- #
# rendering
# --------------------------------------------------------------------------- #
def _cny(x):
    if x is None:
        return "—"
    return "{:,.0f}".format(x)


def sentence_for(book, a):
    b = a["best_year"]
    m = a["margin"]
    if m["delta_pp"] is None:
        return ("{}: the line cannot be crossed by moving one year".format(book))
    if m["on_pass_side"]:
        word = "flips to a fail"
    else:
        word = "flips to a pass"
    return ("{}: best year {} at {:.2f}% is worth {} of the lifetime gain ({:.1f}% of it); "
            "{:+.2f}pp on that one year ({} on the capital standing then) {} — "
            "top-2 share now {:.2f}% against the {:.2f}% line"
            ).format(book, b["year"], b["net_pct"], _cny(b["gain_cny"]),
                     100.0 * (b["share_of_lifetime_gain"] or 0.0),
                     m["delta_pp"], _cny(m["delta_cny"]), word,
                     100.0 * (m["top2_share_recomputed"] or 0.0), 100.0 * m["line"])


def render_md(face):
    L = []
    L.append("# 判决里的钱：三本候选的一年集中度（{face}）".format(face=face["face"]))
    L.append("")
    L.append("证据截止 **{c}**；源面 `{p}`（asof {a}）；本金 **{k} 元**；"
             "年集中线 **{line:.0f}%** 从 `candidate_year_gate.TOP2_SHARE_MAX` 导入。"
             .format(c=face["evidence_cutoff"], p=face["source_face"]["path"],
                     a=face["source_face"]["asof"],
                     k=_cny(face["capital_cny"]), line=100.0 * face["line"]["top2_share_max"]))
    L.append("")
    L.append("## 一句话")
    L.append("")
    for s in face["sentences"]:
        L.append("- " + s)
    L.append("")
    L.append("## 逐本读数")
    L.append("")
    L.append("| 书 | 已发布判词 | 全期倍数 | 年化(年桶重算/在印) | 百万本金到 {cut} | 最好一年 | 该年值多少钱 | 占全期总赚 | 到线的距离 | 该距离值多少钱 |".format(cut=face["evidence_cutoff"]))
    L.append("|---|---|---|---|---|---|---|---|---|---|")
    for b in face["books"]:
        a = b["derived"]
        if a.get("refused"):
            L.append("| {b} | {v} | 拒算 | {r} | — | — | — | — | — | — |".format(
                b=b["book"], v=b["published_verdict"], r=a["refused"]))
            continue
        m = a["margin"]
        L.append("| {b} | {v} | {fm:.4f}× | {cg:.2f}% / {pg} | {val} | {by} {bp:.2f}% | {gc} | {gs:.1f}% | {dd:+.3f}pp | {dc} |".format(
            b=b["book"], v=b["published_verdict"], fm=a["full_multiple"],
            cg=a["cagr_recomputed_pct"] or 0.0,
            pg=(("{:.2f}%".format(b["published_cagr_pct"]))
                if b.get("published_cagr_pct") is not None else "—"),
            val=_cny(a["value_cny"]),
            by=a["best_year"]["year"], bp=a["best_year"]["net_pct"],
            gc=_cny(a["best_year"]["gain_cny"]),
            gs=100.0 * (a["best_year"]["share_of_lifetime_gain"] or 0.0),
            dd=(m["delta_pp"] or 0.0), dc=_cny(m["delta_cny"])))
    L.append("")
    L.append("## 去掉最好那一年还剩什么（leave-one-out·百万本金）")
    L.append("")
    for b in face["books"]:
        a = b["derived"]
        if a.get("refused"):
            continue
        L.append("**{b}**（已发布判词 {v}）".format(b=b["book"], v=b["published_verdict"]))
        L.append("")
        L.append("| 去掉哪一年 | 保留比例 | 年化(其余年) | 百万本金剩 | 该年部分年 |")
        L.append("|---|---|---|---|---|")
        best = a["best_year"]["year"]
        for y in a["years"]:
            row = a["leave_one_year_out"][y]
            mark = " **（最好的一年）**" if y == best else ""
            L.append("| {y}{mk} | {rf:.4f} | {cg} | {v} | {p} |".format(
                y=y, mk=mark,
                rf=row["retained_fraction"] or 0.0,
                cg=(("{:.2f}%".format(row["cagr_without_pct"]))
                    if row["cagr_without_pct"] is not None else "—"),
                v=_cny(row["value_without_cny"]),
                p="是" if row["partial"] else "否"))
        L.append("")
    L.append("")
    L.append("## 这条线分不分得开「一年书」")
    L.append("")
    sep = face["separation"]
    L.append("判词 **{v}**".format(v=sep["verdict"]))
    L.append("")
    if sep.get("metric"):
        L.append("口径：{m}（最好一年占全期总赚的比例）对比 top-2 份额是否过线。"
                 .format(m=sep["metric"]))
        L.append("")
        L.append("| 书 | 最好一年占总赚 | top-2 过线 |")
        L.append("|---|---|---|")
        for r in sep["rows"]:
            L.append("| {b} | {s:.1f}% | {p} |".format(
                b=r["book"], s=100.0 * r[sep["metric"]],
                p="是" if r["on_pass_side"] else "否"))
        L.append("")
    L.append(sep.get("note") or "")
    L.append("")
    L.append("## 三条诚实话")
    for h in face["honest"]:
        L.append("- " + h)
    L.append("")
    return "\n".join(L)


# --------------------------------------------------------------------------- #
# run / check
# --------------------------------------------------------------------------- #
def sha16(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


def build(face_path=SOURCE_FACE, capital=CAPITAL_CNY):
    if not os.path.exists(face_path):
        raise SystemExit("REFUSED: source face missing: " + face_path)
    with io.open(face_path, "r", encoding="utf-8") as f:
        src = json.load(f)

    asof = str(src.get("asof") or "")
    cutoff = asof[:10] if asof else None
    if not cutoff:
        raise SystemExit("REFUSED: source face carries no asof; money readings need a date")

    line = float(G.TOP2_SHARE_MAX)
    books = []
    for row in src.get("books") or []:
        name = row.get("book")
        years = row.get("years") or []
        derived = attribution(years, capital=capital, line=line)
        rec = {
            "book": name,
            "published_verdict": row.get("verdict"),
            "published_cagr_pct": row.get("cagr_pct"),
            "published_top2_share": (row.get("year_metrics") or {}).get("top2_share"),
            "derived": derived,
        }
        # cross-check: our top-2 share must equal the gate's own arithmetic
        if not derived.get("refused"):
            mine = derived["margin"]["top2_share_recomputed"]
            theirs = rec["published_top2_share"]
            rec["top2_share_crosscheck"] = {
                "recomputed": mine,
                "published": theirs,
                "delta": (round(mine - theirs, 6)
                          if (mine is not None and theirs is not None) else None),
                "agrees": (abs(mine - theirs) <= 5e-4
                           if (mine is not None and theirs is not None) else None),
            }
            # cross-check: our CAGR must reproduce the published one
            if rec["published_cagr_pct"] is not None and derived["cagr_recomputed_pct"] is not None:
                gap = round(derived["cagr_recomputed_pct"]
                            - float(rec["published_cagr_pct"]), 6)
                rec["cagr_caliber"] = {
                    "published_pct": rec["published_cagr_pct"],
                    "year_bucket_pct": derived["cagr_recomputed_pct"],
                    "gap_pp": gap,
                    "note": ("the published CAGR divides the equity curve by its bar count; "
                             "this face compounds the calendar-year buckets and takes the "
                             "N-th root, so a partial final year and unequal year lengths "
                             "land here as a visible gap rather than a silent one"),
                }
        books.append(rec)

    sentences = [sentence_for(b["book"], b["derived"])
                 for b in books if not b["derived"].get("refused")]
    sep = separation(books)
    # the thinnest distance is the one the reader must be able to read as money
    near = [(b["book"], b["derived"]["margin"]) for b in books
            if not b["derived"].get("refused")
            and (b["derived"]["margin"].get("delta_pp") is not None)]
    closest = None
    if near:
        name, mm = min(near, key=lambda kv: abs(kv[1]["delta_pp"]))
        closest = {
            "book": name,
            "delta_pp": mm["delta_pp"],
            "delta_cny": mm["delta_cny"],
            "best_year": mm["best_year"],
            "best_year_pct": mm["best_year_pct"],
            "capital_before_best_cny": mm["capital_before_best_cny"],
            "top2_share": mm["top2_share_recomputed"],
            "line": mm["line"],
            "on_pass_side": mm["on_pass_side"],
        }
        sentences.append(
            "最薄的那一本是 {b}：top-2 份额 {s:.2f}% 对 {l:.2f}% 的线，只差 "
            "{g:.2f}pp；换成钱，就是 {y} 年那一年只要多印（或少印）{d:.2f}pp、"
            "当时本金上 {c} 元，判词就翻面。这不是能力测量，是一次舍入测量。"
            .format(b=name, s=100.0 * (mm["top2_share_recomputed"] or 0.0),
                    l=100.0 * mm["line"], g=abs(100.0 * (mm["top2_share_recomputed"] or 0.0)
                                                - 100.0 * mm["line"]),
                    y=mm["best_year"], d=abs(mm["delta_pp"]),
                    c=_cny(abs(mm["delta_cny"]) if mm["delta_cny"] is not None else None)))
    if sep["verdict"] == "THE_LINE_DOES_NOT_SEPARATE_ONE_YEAR_DEPENDENCE":
        sentences.append(
            "年集中线（top-2 份额 ≤ {l:.0f}%）在年账上是分得开的，但在钱上是分不开的："
            "过线的那本（{p}）最好一年占全期总赚 {ps:.1f}%，落在未过线三本的区间 "
            "{lo:.1f}%–{hi:.1f}% 之内，而三本加起来最好一年都占到近六成。"
            .format(l=100.0 * line, p="、".join(sep["passing_inside_failing_range"]),
                    ps=100.0 * next(r["share_of_lifetime_gain"] for r in sep["rows"]
                                    if r["book"] in sep["passing_inside_failing_range"]),
                    lo=100.0 * sep["failing_range"][0],
                    hi=100.0 * sep["failing_range"][1]))

    honest = [
        "货币读数只在写明本金时出现（本面 1,000,000 元，与在册书同种子）；"
        "换个本金，全部金额按比例缩放，pp 与倍数不变。",
        "最好一年的归因是**乘积的分解**，不与其它年份相加；同一年在 "
        "leave-one-out 里的保留比例才是可加的口径，两者不可混读。",
        "2026 是部分年（{p} 个年度行里标 partial），它出现在最好一年或 "
        "leave-one-out 时会改变倍数——表里逐行标了「部分年」。".format(
            p=len([1 for b in books
                   for y in (b["derived"].get("partial_years") or [])])),
        "本面不动任何判词：它只重读年门的 top-2 这一行，并把到线的距离换成钱；"
        "判词以 YEAR-GATE 为正身。",
    ]
    gaps = [(b["book"], b["cagr_caliber"]["gap_pp"])
            for b in books if b.get("cagr_caliber")]
    if gaps:
        honest.append("年化有两把尺：在印的是「净值曲线 ÷ bar 数」，本表重算的是"
                      "「日历年的乘积开 N 次方」，2026 是部分年，所以两者有可见差："
                      + "；".join("{} {:+.2f}pp".format(k, v) for k, v in gaps)
                      + "。倍数与金额用的是年桶这把尺，判词与在印年化以源面为准。")
    if any(not b.get("top2_share_crosscheck", {}).get("agrees", True) for b in books):
        honest.append("**对账不一致**：重算的 top-2 份额与源面不一致（见 "
                      "top2_share_crosscheck），本面的距离读数因此不可信，先修源面。")

    face = {
        "face": FACE,
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "evidence_cutoff": cutoff,
        "capital_cny": capital,
        "line": {
            "top2_share_max": line,
            "source": "candidate_year_gate.TOP2_SHARE_MAX (imported)",
        },
        "source_face": {
            "path": os.path.relpath(face_path, ROOT).replace("\\", "/"),
            "asof": asof,
            "sha16": sha16(face_path),
        },
        "books": books,
        "separation": sep,
        "closest_to_line": closest,
        "sentences": sentences,
        "honest": honest,
    }
    return face


def cmd_run(args):
    t0 = time.time()
    face = build()
    face["elapsed_sec"] = round(time.time() - t0, 3)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(face, f, ensure_ascii=False, indent=1)
        f.write("\n")
    with io.open(DOC, "w", encoding="utf-8", newline="\n") as f:
        f.write(render_md(face))
        f.write("\n")
    for s in face["sentences"]:
        print(s)
    print("wrote", os.path.relpath(OUT, ROOT), os.path.relpath(DOC, ROOT))
    return 0


def cmd_check(args):
    if not os.path.exists(OUT):
        print("STALE: receipt face missing:", OUT)
        return 3
    with io.open(OUT, "r", encoding="utf-8") as f:
        had = json.load(f)
    now = build()
    problems = []
    if had.get("evidence_cutoff") != now["evidence_cutoff"]:
        problems.append("evidence_cutoff moved: {a} -> {b}".format(
            a=had.get("evidence_cutoff"), b=now["evidence_cutoff"]))
    if had.get("source_face", {}).get("sha16") != now["source_face"]["sha16"]:
        problems.append("source face bytes moved: {a} -> {b}".format(
            a=had.get("source_face", {}).get("sha16"), b=now["source_face"]["sha16"]))
    hb = {b["book"]: b for b in had.get("books") or []}
    for b in now["books"]:
        prev = hb.get(b["book"])
        if prev is None:
            problems.append("book missing from receipt: " + str(b["book"]))
            continue
        a, p = b["derived"], prev.get("derived") or {}
        for key in ("full_multiple", "value_cny", "cagr_recomputed_pct"):
            if a.get(key) != p.get(key):
                problems.append("{b}.{k}: receipt {p} vs recomputed {q}".format(
                    b=b["book"], k=key, p=p.get(key), q=a.get(key)))
        mm = (p.get("margin") or {}).get("delta_pp")
        nn = (a.get("margin") or {}).get("delta_pp")
        if mm != nn:
            problems.append("{b}.margin.delta_pp: receipt {p} vs recomputed {q}".format(
                b=b["book"], p=mm, q=nn))
        cc = b.get("top2_share_crosscheck") or {}
        if cc and cc.get("agrees") is False:
            problems.append("{b}: recomputed top-2 share disagrees with the gate "
                            "({p} vs {q})".format(b=b["book"], p=cc.get("recomputed"),
                                                  q=cc.get("published")))
    if problems:
        print("CHECK FAILED ({} problems)".format(len(problems)))
        for p in problems:
            print(" -", p)
        return 3
    print("CHECK OK: {n} books re-derived, line {l:.2f}%, capital {c:,.0f}".format(
        n=len(now["books"]), l=100.0 * now["line"]["top2_share_max"],
        c=now["capital_cny"]))
    for s in now["sentences"]:
        print(" ", s)
    return 0


# --------------------------------------------------------------------------- #
# selftest
# --------------------------------------------------------------------------- #
def selftest():
    legs = []

    def chk(cond, msg):
        legs.append((bool(cond), msg))

    # L1 -- a single year cannot be decomposed
    a = attribution([{"year": "2020", "net_pct": 10.0}])
    chk(a.get("refused"), "L1 one year is refused, not guessed")

    # L2 -- two years: the best year carries the whole concentration
    rows = [{"year": "2020", "net_pct": 10.0}, {"year": "2021", "net_pct": 20.0}]
    a = attribution(rows, capital=100.0, line=0.70)
    chk(a["full_multiple"] == 1.1 * 1.2 - 0.0 or abs(a["full_multiple"] - 1.32) < 1e-12,
        "L2a product of yearly growth, not the sum (1.10*1.20=1.32)")
    chk(abs(a["value_cny"] - 132.0) < 1e-9,
        "L2b money is capital * product (132 on 100)")
    chk(abs(a["margin"]["top2_share_recomputed"] - (10.0 + 20.0) / 30.0) < 1e-9,
        "L2c top-2 share is the gate's own arithmetic share")

    # L3 -- best-year gain share on the extreme: one year does all the work
    a = attribution([{"year": "2020", "net_pct": 100.0},
                     {"year": "2021", "net_pct": 0.0}], capital=100.0, line=0.70)
    chk(abs(a["best_year"]["share_of_lifetime_gain"] - 1.0) < 1e-9,
        "L3 gain share 1.0 when 2020 is the only year that grows")
    chk(abs(a["best_year"]["gain_cny"] - 100.0) < 1e-9,
        "L3b gain in money = 200 - 100")
    chk(abs(a["leave_one_year_out"]["2020"]["value_without_cny"] - 100.0) < 1e-9,
        "L3c without the best year the 100 is untouched")

    # L4 -- the crossing solve reproduces the line when re-evaluated
    rows = [{"year": "2019", "net_pct": 3.0}, {"year": "2020", "net_pct": 4.0},
            {"year": "2021", "net_pct": 6.0}, {"year": "2022", "net_pct": 30.0},
            {"year": "2023", "net_pct": 5.0}]
    a = attribution(rows, capital=1e6, line=0.70)
    m = a["margin"]
    rets = [r["net_pct"] for r in rows]
    star = m["best_year_pct_star"]
    patched = [star if abs(r - m["best_year_pct"]) < 1e-12 else r for r in rets]
    share_at_star = (sorted(patched, reverse=True)[0] + sorted(patched, reverse=True)[1]) / sum(patched)
    chk(abs(share_at_star - 0.70) < 1e-9,
        "L4 the closed form lands exactly on the line when re-evaluated")

    # L5 -- distance is signed: a passing book needs the best year to move UP
    a_pass = attribution([{"year": "2020", "net_pct": 10.0},
                          {"year": "2021", "net_pct": 10.0},
                          {"year": "2022", "net_pct": 10.0}], capital=1e6, line=0.70)
    chk(a_pass["margin"]["on_pass_side"] is True,
        "L5a a flat book is on the pass side (top-2 66.7% vs 70%)")
    chk((a_pass["margin"]["delta_pp"] or 0) > 0,
        "L5b the line sits ABOVE a passing best year (delta positive)")

    # L6 -- and on a failing book the delta is negative, so the money is a price of repair
    a_fail = attribution([{"year": "2020", "net_pct": 5.0},
                          {"year": "2021", "net_pct": 5.0},
                          {"year": "2022", "net_pct": 60.0}], capital=1e6, line=0.70)
    chk(a_fail["margin"]["on_pass_side"] is False,
        "L6a a top-heavy book is on the fail side")
    chk((a_fail["margin"]["delta_pp"] or 0) < 0,
        "L6b its delta is negative (the line sits below the printed best year)")

    # L7 -- the money of a pp is measured on the capital standing THEN
    rows = [{"year": "2020", "net_pct": 100.0}, {"year": "2021", "net_pct": 10.0},
            {"year": "2022", "net_pct": 1.0}]
    a = attribution(rows, capital=100.0, line=0.70)
    chk(abs(a["margin"]["capital_before_best_cny"] - 100.0) < 1e-9,
        "L7a best year is 2020, so the standing capital is the seed")
    rows = [{"year": "2020", "net_pct": 1.0}, {"year": "2021", "net_pct": 10.0},
            {"year": "2022", "net_pct": 100.0}]
    a = attribution(rows, capital=100.0, line=0.70)
    chk(abs(a["margin"]["capital_before_best_cny"] - 111.1) < 1e-6,
        "L7b a late best year is priced on compounded capital (100*1.01*1.10)")

    # L8 -- partial years travel into the output
    a = attribution([{"year": "2020", "net_pct": 8.0},
                     {"year": "2021", "net_pct": 6.0, "partial": True}],
                    capital=1e6, line=0.70)
    chk(a["partial_years"] == ["2021"], "L8 partial year is disclosed, not silently used")
    chk(a["best_year"]["partial"] is False,
        "L8b the best year here is the complete one, so its flag is False")

    # L9 -- no capital, no money
    a = attribution([{"year": "2020", "net_pct": 5.0},
                     {"year": "2021", "net_pct": 6.0}], capital=None, line=0.70)
    chk(a["value_cny"] is None and a["best_year"]["gain_cny"] is None,
        "L9 an unstated capital prints no money")
    chk(a["margin"]["delta_cny"] is None, "L9b and no money on the distance either")

    # L10 -- line at 1.0 has no crossing (refuse rather than emit inf)
    chk(best_year_crossing(10.0, 5.0, 20.0, 1.0) is None,
        "L10 a 100% line cannot be crossed by moving one year")

    # L11 -- crosscheck arithmetic: recomputed share equal to the gate's metric
    rows = [{"year": "2020", "net_pct": 5.607211539627288},
            {"year": "2021", "net_pct": 7.628116174581789},
            {"year": "2022", "net_pct": 2.8392743924003705},
            {"year": "2023", "net_pct": 5.47301156733262},
            {"year": "2024", "net_pct": 14.549563099483386},
            {"year": "2025", "net_pct": 43.062681571816476},
            {"year": "2026", "net_pct": 0.4380586942911213, "partial": True}]
    gm = G.year_metrics([dict(r, partial=bool(r.get("partial"))) for r in rows])
    a = attribution(rows, capital=1e6, line=float(G.TOP2_SHARE_MAX))
    chk(abs(a["margin"]["top2_share_recomputed"] - gm["top2_share"]) <= 5e-4,
        "L11 our share reproduces candidate_year_gate.year_metrics on the published rows")

    # L12 -- the calendar-year reading is disclosed as a different caliber, not asserted equal
    if rows and a["cagr_recomputed_pct"] is not None:
        gap = abs(a["cagr_recomputed_pct"] - 11.16)
        chk(gap < 1.0,
            "L12 the year-bucket CAGR stays within 1pp of the published bar-count CAGR "
            "(gap {:.2f}pp here) and the gap is printed, not asserted away".format(gap))

    # L13 -- top3 gain share is sorted and does not exceed 1.0
    a = attribution([{"year": "2020", "net_pct": 5}, {"year": "2021", "net_pct": 40},
                     {"year": "2022", "net_pct": 1}, {"year": "2023", "net_pct": 2}],
                    capital=1e6, line=0.70)
    t3 = a["top3_gain_share"]
    chk(all(t3[i]["share"] >= t3[i + 1]["share"] for i in range(len(t3) - 1)),
        "L13 top-3 gain shares are sorted descending")
    chk(max(v for v in a["gain_share_by_year"].values()) <= 1.0 + 1e-9,
        "L13b no single year can own more than the whole gain")

    # L14 -- separation is a reading of the set, and a passing book inside the
    #        failing range must be named, not smoothed over
    def _fake(name, share, on_pass):
        return {"book": name,
                "derived": {"best_year": {"share_of_lifetime_gain": share},
                            "margin": {"on_pass_side": on_pass}}}

    s = separation([_fake("a", 0.55, False), _fake("b", 0.565, True),
                    _fake("c", 0.58, False)])
    chk(s["verdict"] == "THE_LINE_DOES_NOT_SEPARATE_ONE_YEAR_DEPENDENCE",
        "L14a a passing book inside the failing range is reported as not separated")
    chk(s["passing_inside_failing_range"] == ["b"],
        "L14b and it is named by book, not summarised away")
    s = separation([_fake("a", 0.70, False), _fake("b", 0.50, True),
                    _fake("c", 0.65, False)])
    chk(s["verdict"] == "THE_LINE_SEPARATES_ONE_YEAR_DEPENDENCE",
        "L14c when the passing book is outside the failing range the reverse holds")
    s = separation([_fake("a", 0.70, False), _fake("b", 0.65, False)])
    chk(s["verdict"] == "ONE_SIDED",
        "L14d a one-sided set refuses to claim separation either way")

    # L15 -- a refused book is skipped, not treated as zero dependence
    s = separation([_fake("a", 0.70, False), _fake("b", 0.60, True),
                    {"book": "c", "derived": {"refused": "one year"}}])
    chk(all(r["book"] != "c" for r in s["rows"]),
        "L15 a refused book does not enter the separation rows")

    ok = sum(1 for c, _ in legs if c)
    for c, msg in legs:
        print(("PASS " if c else "FAIL ") + msg)
    print("\nselftest {}/{} PASS".format(ok, len(legs)))
    return 0 if ok == len(legs) else 1


def main(argv=None):
    p = argparse.ArgumentParser(description=FACE)
    p.add_argument("mode", nargs="?", default="run",
                   choices=["run", "check", "selftest"])
    args = p.parse_args(argv)
    if args.mode == "selftest":
        return selftest()
    if args.mode == "check":
        return cmd_check(args)
    return cmd_run(args)


if __name__ == "__main__":
    sys.exit(main())
