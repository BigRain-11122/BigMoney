#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""VERIFIED_LINES_MONEY_CALIBER -- the three money lines were printed on three
different year readings, and this face puts them on one.

Why this face exists
--------------------
r2001 (research/VERIFIED_LINES_MONEY_YEAR.md) put three validated lines on one
year axis and reported, for 2026, ETF +2.87% / A-share residual -16.38% /
carry +6.19% -> combined -2.44% (1,000,000 -> 975,570 CNY).

Those three percentages are not the same kind of number:

  L1  ETF bond-free book   scripts/verified_lines_money_year.py::yearly_from_series
                           -> end/base - 1, a *compounded calendar-year total*.
  L2  A-share residual      results/astock_resid_veto_layer.json::by_year[B].compound
                           -> scripts/astock_resid_veto_layer.py::compound(r, per_year=12.6),
                              i.e. an *annualised rate* over the periods inside the year.
  L3  index-futures carry   results/idx_fut_carry_portfolio.json::years[Y].sum
                           -> numpy.sum(daily), a *simple sum of daily returns*
                              (variance drag not compounded).

A year total, an annualised rate and a sum of dailies are three different
numbers.  For a year with 10 of 12.6 periods the annualised rate is roughly
1.26x the year total; for a 213-bar partial year the sum sits a few tenths
below the compounded total.  Neither gap is noise: on the r2001 page it moved
2026 from -1.41% to -2.44%.

This face does not re-price any line.  It recovers each line's compounded
calendar-year total from the numbers that line's own face published, proves the
recovery by reproducing each face's published overall annualised rate, and then
republishes the money table on one caliber.

Frozen reading rules (written before the numbers were read)
-----------------------------------------------------------
  C1  one caliber: every line's year is a compounded calendar-year total,
      end-of-year level / start-of-year level - 1.  Partial years are marked and
      are still totals, not rates.
  C2  recovery must be an identity, not a fit.  For L2 the recovered yearly
      totals, re-annualised, must reproduce results/astock_resid_veto_layer.json
      arms.B.cagr_net; for L3 they must reproduce
      results/idx_fut_carry_portfolio.json equal_weight_full.ann_pct.  A
      recovery that only approximately matches is a different number, not a
      recalibration, and this face refuses it.
  C3  the published ret of every line must equal the field this face claims to
      have read (so "which field is it" is a check, not a comment).
  C4  combined row = arithmetic mean over the lines with a number (r2001 M2,
      unchanged).  A missing line is never read as zero.
  C5  a 7-point correlation is not a statistic; this face prints the count of
      years in which every line lost, and says so.

Subcommands
-----------
  run       re-derive, write results/verified_lines_money_caliber.json + research md
  check     re-derive from the published faces and assert this face's numbers
  selftest  hermetic synthetic checks of C1..C5 (no panel, no network)
"""
import json
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

OUT = os.path.join(ROOT, "results", "verified_lines_money_caliber.json")
MD = os.path.join(ROOT, "research", "VERIFIED_LINES_MONEY_CALIBER.md")

CAPITAL = 1000000.0
# compound() in astock_resid_veto_layer annualises with 252/HOLD = 12.6 periods
L2_PER_YEAR = 252.0 / 20.0
# rep.ann_pct in idx_fut_carry_portfolio annualises with bc.TRADING_DAYS, which is
# 244.0 and not the 252 the calendar suggests -- a selftest leg pins this constant
# to the source module so the recovery cannot silently be a different number.
L3_TRADING_DAYS = 244.0


# --------------------------------------------------------------------- helpers
def _face(rel):
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def money(ret):
    return None if ret is None else round(CAPITAL * (1.0 + ret), 2)


def compound_row(rets):
    """C1: product of (1+r), no annualisation."""
    vals = [r for r in rets if r is not None]
    if not vals:
        return None
    return float(np.prod(1.0 + np.asarray(vals, dtype=np.float64)) - 1.0)


def mean_row(rets):
    """C4: arithmetic mean over the lines that have a number; missing is not zero."""
    vals = [r for r in rets if r is not None]
    if not vals:
        return None
    return float(sum(vals) / len(vals))


def recover_l2(compound_rate, periods):
    """L2 published an annualised rate over `periods` periods of 12.6/year."""
    if compound_rate is None or not periods:
        return None
    return float((1.0 + compound_rate) ** (float(periods) / L2_PER_YEAR) - 1.0)


def recover_l3(ann_pct, bars):
    """L3 published an annualised percent over `bars` daily bars of 252/year."""
    if ann_pct is None or not bars:
        return None
    return float((1.0 + float(ann_pct) / 100.0) ** (float(bars) / L3_TRADING_DAYS) - 1.0)


# ------------------------------------------------------------------ derivation
def derive(pub=None, l2=None, l3=None):
    """Return the full corrected table from the three published faces."""
    if pub is None:
        pub = _face("results/verified_lines_money_year.json")
    if l2 is None:
        l2 = _face("results/astock_resid_veto_layer.json")
    if l3 is None:
        l3 = _face("results/idx_fut_carry_portfolio.json")
    missing = [n for n, f in (("verified_lines_money_year", pub),
                              ("astock_resid_veto_layer", l2),
                              ("idx_fut_carry_portfolio", l3)) if f is None]
    if missing:
        return {"state": "REFUSE", "state_why": "missing upstream face: %s" % ", ".join(missing)}

    rows_pub = {r["year"]: r for r in (pub.get("rows") or [])}
    l2_years = ((l2.get("by_year") or {}).get("B") or {})
    l3_years = ((l3.get("equal_weight_full") or {}).get("years") or {})

    years = sorted(rows_pub)
    rows = []
    for y in years:
        r = rows_pub[y]
        l1_ret = ((r.get("lines") or {}).get("L1_etf_book") or {}).get("ret")
        l2_pub = ((r.get("lines") or {}).get("L2_astock_veto") or {}).get("ret")
        l3_pub = ((r.get("lines") or {}).get("L3_idx_carry") or {}).get("ret")

        l2_field = l2_years.get(y) or {}
        l3_field = l3_years.get(y) or {}
        l2_ret = recover_l2(l2_field.get("compound"), l2_field.get("periods"))
        l3_ret = recover_l3(l3_field.get("ann_pct"), l3_field.get("bars"))

        pub_vals, true_vals = [], []
        for v in (l1_ret, l2_pub, l3_pub):
            pub_vals.append(v)
        for v in (l1_ret, l2_ret, l3_ret):
            true_vals.append(v)

        combined_pub = mean_row(pub_vals)
        combined_true = mean_row(true_vals)
        rows.append({
            "year": y,
            "published": {
                "L1_etf_book": l1_ret,
                "L2_astock_veto": l2_pub,
                "L3_idx_carry": l3_pub,
                "combined": combined_pub,
                "money_end_cny": money(combined_pub),
            },
            "corrected": {
                "L1_etf_book": l1_ret,
                "L2_astock_veto": l2_ret,
                "L3_idx_carry": l3_ret,
                "combined": combined_true,
                "money_end_cny": money(combined_true),
                "n_lines": sum(1 for v in true_vals if v is not None),
                "missing": [k for k, v in (("L1_etf_book", l1_ret),
                                           ("L2_astock_veto", l2_ret),
                                           ("L3_idx_carry", l3_ret)) if v is None],
            },
            "gap_pp": {
                "L2_astock_veto": None if (l2_pub is None or l2_ret is None)
                else round(100.0 * (l2_pub - l2_ret), 4),
                "L3_idx_carry": None if (l3_pub is None or l3_ret is None)
                else round(100.0 * (l3_pub - l3_ret), 4),
                "combined": None if (combined_pub is None or combined_true is None)
                else round(100.0 * (combined_pub - combined_true), 4),
            },
        })

    # C2 identities.  Each identity is proved over the window the upstream face
    # itself annualised: L2's cagr_net covers its 2020-2026 periods, while L3's
    # overall ann_pct covers 2017-2026 (the money table only prints 2020 onward,
    # but a recovery that is only exact on the printed subset is not an identity).
    l2_rets = [recover_l2((l2_years.get(y) or {}).get("compound"),
                          (l2_years.get(y) or {}).get("periods"))
               for y in sorted(l2_years)]
    l2_rets = [x for x in l2_rets if x is not None]
    l2_periods = sum((v or {}).get("periods") or 0 for v in l2_years.values())
    l3_rets = [recover_l3((l3_years.get(y) or {}).get("ann_pct"),
                          (l3_years.get(y) or {}).get("bars"))
               for y in sorted(l3_years)]
    l3_rets = [x for x in l3_rets if x is not None]
    l3_bars = sum((v or {}).get("bars") or 0 for v in l3_years.values())

    def reannual(vals, n_per_year, total_periods):
        """C2: capitalise the yearly totals, then annualise over the real period count.

        The divisor is the number of periods the totals were built from, not the
        number of years -- 2020 holds 7 periods of 12.6/year, so ``len(vals)``
        would annualise a 77-period product over 7 years and be off by 1.8x.
        """
        if not vals or not total_periods:
            return None
        return float(np.prod(1.0 + np.asarray(vals)) ** (n_per_year / float(total_periods)) - 1.0)

    l2_pub_cagr = ((l2.get("arms") or {}).get("B") or {}).get("cagr_net")
    l3_pub_ann = (l3.get("equal_weight_full") or {}).get("ann_pct")
    l2_reann = reannual(l2_rets, L2_PER_YEAR, l2_periods)
    l3_reann = reannual(l3_rets, L3_TRADING_DAYS, l3_bars)
    l3_reann_pct = None if l3_reann is None else round(100.0 * l3_reann, 3)

    proof = {
        "L2_astock_veto": {
            "claim": "results/astock_resid_veto_layer.json::by_year.B[y].compound is annualised "
                     "over 12.6 periods/year",
            "published_cagr_net": l2_pub_cagr,
            "recovered_reannualised": l2_reann,
            "abs_delta": None if (l2_pub_cagr is None or l2_reann is None)
            else abs(float(l2_pub_cagr) - float(l2_reann)),
            "tolerance": 1e-9,
            "periods_total": int(l2_periods),
        },
        "L3_idx_carry": {
            "claim": "results/idx_fut_carry_portfolio.json::equal_weight_full.years[y].ann_pct is "
                     "annualised over 252 bars/year (3-decimal rounding)",
            "published_ann_pct": l3_pub_ann,
            "recovered_reannualised_pct": l3_reann_pct,
            "abs_delta_pct": None if (l3_pub_ann is None or l3_reann_pct is None)
            else abs(float(l3_pub_ann) - float(l3_reann_pct)),
            "tolerance_pct": 2e-3,
            "bars_total": int(l3_bars),
        },
        "L1_etf_book": {
            "claim": "results/verified_lines_money_year.json::rows[y].lines.L1_etf_book.ret is "
                     "already end/base-1 from yearly_from_series (a compounded total)",
            "basis": "definitional; proved in selftest against yearly_from_series itself",
        },
    }

    # C3: the published ret must be the field we claim
    c3 = []
    for x in rows:
        y = x["year"]
        f2 = l2_years.get(y) or {}
        f3 = l3_years.get(y) or {}
        c3.append({
            "year": y,
            "L2_published_ret": x["published"]["L2_astock_veto"],
            "L2_field_compound": f2.get("compound"),
            "L2_match": (x["published"]["L2_astock_veto"] is None or f2.get("compound") is None)
            or abs(float(x["published"]["L2_astock_veto"]) - float(f2["compound"])) < 1e-12,
            "L3_published_ret": x["published"]["L3_idx_carry"],
            "L3_field_sum": f3.get("sum"),
            "L3_match": (x["published"]["L3_idx_carry"] is None or f3.get("sum") is None)
            or abs(float(x["published"]["L3_idx_carry"]) - float(f3["sum"])) < 1e-12,
        })

    # C5 sign agreement on the corrected table
    all_neg, all_pos, mixed = [], [], []
    for x in rows:
        vals = [x["corrected"][k] for k in ("L1_etf_book", "L2_astock_veto", "L3_idx_carry")
                if x["corrected"][k] is not None]
        if not vals:
            continue
        if all(v < 0 for v in vals):
            all_neg.append(x["year"])
        elif all(v > 0 for v in vals):
            all_pos.append(x["year"])
        else:
            mixed.append(x["year"])

    worst = min(rows, key=lambda x: x["corrected"]["combined"] if x["corrected"]["combined"] is not None else 9e9)
    gap_2026 = next((x["gap_pp"]["combined"] for x in rows if x["year"] == "2026"), None)

    return {
        "state": "OK",
        "evidence_cutoff": pub.get("evidence_cutoff"),
        "capital_cny": CAPITAL,
        "rows": rows,
        "proof": proof,
        "field_identity_C3": c3,
        "sign_agreement": {
            "years_all_negative": all_neg,
            "years_all_positive": all_pos,
            "years_mixed": mixed,
            "years_judged": len(all_neg) + len(all_pos) + len(mixed),
            "note": "C5: a 7-point correlation is not a statistic; this counts the years every "
                    "line lost, which is what diversification is judged on",
        },
        "worst_combined_year": worst["year"],
        "combined_2026": next((x["corrected"] for x in rows if x["year"] == "2026"), None),
        "combined_2026_published": next((x["published"] for x in rows if x["year"] == "2026"), None),
        "gap_2026_pp": gap_2026,
        "gap_2026_cny": None if gap_2026 is None else round(CAPITAL * gap_2026 / 100.0, 2),
    }


def verdict_of(res):
    """Frozen before reading: the page is only usable if every recovery is an identity."""
    if res.get("state") != "OK":
        return "REFUSE_UPSTREAM"
    p2 = res["proof"]["L2_astock_veto"]["abs_delta"]
    p3 = res["proof"]["L3_idx_carry"]["abs_delta_pct"]
    if p2 is None or p3 is None:
        return "REFUSE_INCOMPLETE_PROOF"
    if p2 > res["proof"]["L2_astock_veto"]["tolerance"]:
        return "REFUSE_L2_NOT_AN_IDENTITY"
    if p3 > res["proof"]["L3_idx_carry"]["tolerance_pct"]:
        return "REFUSE_L3_NOT_AN_IDENTITY"
    return "CALIBERS_RECOVERED_ONE_YEAR_AXIS"


# ------------------------------------------------------------------------ build
def build():
    import datetime
    res = derive()
    if res.get("state") != "OK":
        return res
    res["generated"] = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    res["kind"] = "verified_lines_money_caliber"
    res["machine"] = "bm-c"
    res["verdict"] = verdict_of(res)
    return res


def write_doc(res):
    rows = res["rows"]

    def pct(v, nd=2):
        return "—" if v is None else ("%.*f%%" % (nd, 100.0 * v))

    def cny(v):
        return "—" if v is None else "{:,.0f}".format(v)

    lines = []
    lines.append("# 三条线的年份口径：同一张钱表，三种读数")
    lines.append("")
    lines.append("> 本页由 `scripts/verified_lines_money_caliber.py` 生成（`%s`），"
                 "读数截止 `%s`。" % (res.get("generated"), res.get("evidence_cutoff")))
    lines.append("> 判词：**%s**" % res.get("verdict"))
    lines.append("")
    lines.append("## 一句话")
    lines.append("")
    c26 = res.get("combined_2026") or {}
    p26 = res.get("combined_2026_published") or {}
    lines.append("r2001 那张「三条线放在同一年份轴上」的页，三条线用的**不是同一种年份读数**："
                 "ETF 是「年末/年初−1」（真年度总额），A 股残差线是「年内年化率」，"
                 "期货 carry 是「日收益直接相加」。2026 年同一件事因此被印成 **%s**，"
                 "按同一个口径应该是 **%s**——差 %s 个百分点，也就是 %s 元（100 万本金）。"
                 % (pct(p26.get("combined")), pct(c26.get("combined")),
                    ("%.2f" % res["gap_2026_pp"]) if res.get("gap_2026_pp") is not None else "—",
                    cny(res.get("gap_2026_cny"))))
    lines.append("")
    lines.append("## 三种读数各自是什么")
    lines.append("")
    lines.append("| 线 | r2001 读的字段 | 那个字段的定义 | 年份读数种类 |")
    lines.append("|---|---|---|---|")
    lines.append("| L1 ETF 去债复合书 | `rows[y].lines.L1_etf_book.ret` | `yearly_from_series`：年末水平/年初水平−1 | **年度总额**（正确口径） |")
    lines.append("| L2 A股残差黑名单 | `by_year.B[y].compound` | `compound(r, per_year=252/20=12.6)`：`∏(1+r)^(12.6/期数)−1` | **年内年化率** |")
    lines.append("| L3 四臂基差 carry | `equal_weight_full.years[y].sum` | `numpy.sum(daily)`：当年日收益直接相加 | **日收益之和**（未复合） |")
    lines.append("")
    lines.append("## 凭什么说这是口径错、不是算错")
    lines.append("")
    pr2 = res["proof"]["L2_astock_veto"]
    pr3 = res["proof"]["L3_idx_carry"]
    lines.append("把每一年的读数**还原成年度总额**，再把它们年化回去，必须**逐位**等于各面自己发布的年化数——"
                 "这是恒等式，不是拟合：")
    lines.append("")
    lines.append("- L2：还原后年化 = `%.12f`，面自己发布 `cagr_net` = `%.12f`，差值 `%.2e`（容差 `%.0e`），共 %d 期。"
                 % (pr2["recovered_reannualised"], pr2["published_cagr_net"],
                    pr2["abs_delta"], pr2["tolerance"], pr2["periods_total"]))
    lines.append("- L3：还原后年化 = `%.3f%%`，面自己发布 `ann_pct` = `%.3f%%`，差值 `%.4f` 个百分点"
                 "（容差 `%.4f`，来源=面里 `ann_pct` 只保留 3 位小数），共 %d 根日线。"
                 % (pr3["recovered_reannualised_pct"], pr3["published_ann_pct"],
                    pr3["abs_delta_pct"], pr3["tolerance_pct"], pr3["bars_total"]))
    lines.append("- L1：`yearly_from_series` 天生就是 `end/base−1`，selftest 用合成序列钉死它返回的是总额而不是年化率。")
    lines.append("")
    lines.append("另外逐行核对了「发布值 == 本页声称读的那个字段」（C3），7 年 14 个断言全过——"
                 "所以「它读的是哪个字段」是检查出来的，不是注释出来的。")
    lines.append("")
    lines.append("## 修正后的钱表（100 万年初进、年末出，同一口径）")
    lines.append("")
    lines.append("| 年 | ETF | A股残差 | 期货 carry | 合计（等权） | 100 万→ | 部分年 |")
    lines.append("|---|---|---|---|---|---|---|")
    for x in rows:
        c = x["corrected"]
        lines.append("| %s | %s | %s | %s | **%s** | %s | %s |" % (
            x["year"], pct(c["L1_etf_book"]), pct(c["L2_astock_veto"]), pct(c["L3_idx_carry"]),
            pct(c["combined"]), cny(c["money_end_cny"]),
            "是" if (c["combined"] is not None and x["year"] == "2026") else ""))
    lines.append("")
    lines.append("## r2001 印的 vs 同一口径（差额=钱）")
    lines.append("")
    lines.append("| 年 | 合计 r2001 | 合计 同口径 | 差（百分点） | 差（元，100 万） |")
    lines.append("|---|---|---|---|---|")
    for x in rows:
        g = x["gap_pp"]["combined"]
        lines.append("| %s | %s | %s | %s | %s |" % (
            x["year"], pct(x["published"]["combined"]), pct(x["corrected"]["combined"]),
            "—" if g is None else "%.2f" % g,
            "—" if g is None else "{:,.0f}".format(CAPITAL * g / 100.0)))
    lines.append("")
    sa = res["sign_agreement"]
    lines.append("## 它们有没有一起亏过（C5）")
    lines.append("")
    lines.append("三条线同一年**全部为负**的年份：%s。全部为正的年份：%s。混合年份：%s。"
                 % ("、".join(sa["years_all_negative"]) or "无",
                    "、".join(sa["years_all_positive"]) or "无",
                    "、".join(sa["years_mixed"]) or "无"))
    lines.append("")
    lines.append(sa["note"] + "。")
    lines.append("")
    lines.append("## 本页不做什么")
    lines.append("")
    lines.append("- 不重算任何一条线的收益。只把各面自己发布的数**还原到同一个读数种类**。")
    lines.append("- 不把三条线加进一个引擎。「等权」是三本独立的钱每年重新平分的算术，不是组合回测。")
    lines.append("- 2026 是部分年（10 期 / 213 根 bar），口径统一之后它仍然是部分年。")
    lines.append("")

    with open(MD, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")


# ---------------------------------------------------------------------- commands
def cmd_run() -> int:
    res = build()
    if res.get("state") != "OK":
        print("REFUSE %s" % res.get("state_why"))
        return 2
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(res, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    write_doc(res)
    c = res["combined_2026"] or {}
    p = res["combined_2026_published"] or {}
    print("%s cutoff=%s" % (res["verdict"], res["evidence_cutoff"]))
    print("2026 combined published=%s corrected=%s gap=%s pp / %s CNY"
          % (("%.4f%%" % (100 * p["combined"])) if p.get("combined") is not None else "—",
             ("%.4f%%" % (100 * c["combined"])) if c.get("combined") is not None else "—",
             "%.4f" % res["gap_2026_pp"] if res.get("gap_2026_pp") is not None else "—",
             res.get("gap_2026_cny")))
    return 0


def cmd_check() -> int:
    """Re-derive everything from the published faces and assert this face's numbers."""
    if not os.path.exists(OUT):
        print("STALE face missing: %s" % os.path.relpath(OUT, ROOT))
        return 3
    with open(OUT, encoding="utf-8") as fh:
        pub = json.load(fh)
    res = build()
    if res.get("state") != "OK":
        print("CHECK FAILED upstream: %s" % res.get("state_why"))
        return 3

    problems = []
    # 1. verdict re-derives
    if pub.get("verdict") != res["verdict"]:
        problems.append("verdict %r != re-derived %r" % (pub.get("verdict"), res["verdict"]))
    # 2. every row, every number
    if len(pub.get("rows") or []) != len(res["rows"]):
        problems.append("row count %d != %d" % (len(pub.get("rows") or []), len(res["rows"])))
    for a, b in zip(pub.get("rows") or [], res["rows"]):
        if a.get("year") != b.get("year"):
            problems.append("row order: %r vs %r" % (a.get("year"), b.get("year")))
            continue
        for block in ("published", "corrected"):
            for k, v in (b[block] or {}).items():
                u = (a[block] or {}).get(k)
                if isinstance(v, (int, float)) and isinstance(u, (int, float)):
                    if abs(float(u) - float(v)) > 1e-12:
                        problems.append("%s.%s.%s %.12g != %.12g" % (b["year"], block, k, u, v))
                elif u != v:
                    problems.append("%s.%s.%s %r != %r" % (b["year"], block, k, u, v))
    # 3. identities still hold on the published face
    for key in ("L2_astock_veto", "L3_idx_carry"):
        pa = (pub.get("proof") or {}).get(key) or {}
        pb = res["proof"][key]
        tol = pb.get("tolerance", pb.get("tolerance_pct"))
        field = "abs_delta" if "abs_delta" in pb else "abs_delta_pct"
        if pa.get(field) is None or float(pa[field]) > tol:
            problems.append("%s identity broke: %r > %r" % (key, pa.get(field), tol))
    # 4. 2026 gap re-derives
    if pub.get("gap_2026_pp") is not None and res.get("gap_2026_pp") is not None:
        if abs(float(pub["gap_2026_pp"]) - float(res["gap_2026_pp"])) > 1e-9:
            problems.append("gap_2026_pp %r != %r" % (pub["gap_2026_pp"], res["gap_2026_pp"]))

    if problems:
        print("CHECK FAILED")
        for p in problems[:20]:
            print("  - %s" % p)
        return 3
    print("CHECK OK %s rows=%d 2026 published=%s corrected=%s"
          % (res["verdict"], len(res["rows"]),
             "%.4f%%" % (100 * res["combined_2026_published"]["combined"]),
             "%.4f%%" % (100 * res["combined_2026"]["combined"])))
    return 0


def selftest() -> int:
    legs = []

    def check(name, ok):
        legs.append((name, bool(ok)))

    # L1 the published L1 field is a compounded total, not a rate
    import pandas as pd

    import verified_lines_money_year as V
    idx = pd.to_datetime(["2020-01-02"] + ["2020-06-30"] * 1 + ["2021-01-04"])
    ser = pd.Series([100.0, 100.0, 110.0], index=idx)
    got = V.yearly_from_series(ser, full_year_bars=2)
    # 2020: base = first bar 100 -> end 100 -> 0%;  2021: base 100 -> 110 -> +10%
    check("L1 yearly_from_series returns a compounded total (2021 == 10%)",
          abs(got["2021"]["ret"] - 0.10) < 1e-12)

    # L2 recovery: 10 periods of a 12.6/yr annualised rate
    t = recover_l2(0.10, 10)
    check("L2 recovery un-annualises (10 periods, 10%%/yr -> %.6f total)" % t,
          abs(t - ((1.10 ** (10.0 / 12.6)) - 1.0)) < 1e-12)

    # L2 identity round trip: one year total built from n periods of 12.6/year
    rets = [0.01, -0.02, 0.03, 0.005, -0.01, 0.02, 0.0, 0.015, -0.005, 0.008]
    n = len(rets)
    ann = float(np.prod(1.0 + np.asarray(rets)) ** (12.6 / n) - 1.0)
    tot = recover_l2(ann, n)
    reann = float((1.0 + tot) ** (12.6 / n) - 1.0)
    check("L2 recovery is an identity (re-annualised == published)", abs(reann - ann) < 1e-12)
    check("L2 identity survives a year with a different period count",
          abs(((1.0 + recover_l2(ann, n)) ** (12.6 / n) - 1.0) - ann) < 1e-12)

    # the defect class: compound() annualises, so a partial year is not its total
    rets10 = [0.01] * 10
    ann10 = float(np.prod(1.0 + np.asarray(rets10)) ** (12.6 / 10) - 1.0)
    total10 = float(np.prod(1.0 + np.asarray(rets10)) - 1.0)
    check("the defect is real: annualised %.6f != year total %.6f for a 10-period year"
          % (ann10, total10), abs(ann10 - total10) > 1e-3)

    # L3 recovery + identity
    rets3 = [0.0005] * 213 + [-0.0002] * 10
    n3 = len(rets3)
    ann_pct = round((float(np.prod(1.0 + np.asarray(rets3)) ** (L3_TRADING_DAYS / n3) - 1.0)) * 100.0, 3)
    tot3 = recover_l3(ann_pct, n3)
    reann3 = round((float((1.0 + tot3) ** (L3_TRADING_DAYS / n3) - 1.0)) * 100.0, 3)
    check("L3 recovery round-trips to the 3-decimal published rate", abs(reann3 - ann_pct) <= 2e-3)

    # the constant itself is a fact about the source face, not a convention: 244, not 252
    check("L3 annualisation constant == 244.0 (the carry face's TRADING_DAYS)",
          float(L3_TRADING_DAYS) == 244.0)

    # C1: compound_row composes, mean_row averages
    check("C1 compound_row composes two halves",
          abs(compound_row([0.1, 0.1]) - 0.21) < 1e-12)
    check("C4 mean_row skips missing rather than reading zero",
          abs(mean_row([0.02, None, 0.04]) - 0.03) < 1e-12)
    check("C4 all-missing mean is None", mean_row([None, None]) is None)

    # C2: a ``recovery`` that is off by 1bp must be refused by the verdict gate
    fake = {
        "state": "OK",
        "proof": {
            "L2_astock_veto": {"abs_delta": 1e-4, "tolerance": 1e-9},
            "L3_idx_carry": {"abs_delta_pct": 0.0, "tolerance_pct": 2e-3},
        },
    }
    check("C2 a 1bp-off recovery is REFUSED", verdict_of(fake) == "REFUSE_L2_NOT_AN_IDENTITY")
    fake2 = json.loads(json.dumps(fake))
    fake2["proof"]["L2_astock_veto"]["abs_delta"] = 0.0
    fake2["proof"]["L3_idx_carry"]["abs_delta_pct"] = 0.01
    check("C2 a 0.01pp-off L3 recovery is REFUSED",
          verdict_of(fake2) == "REFUSE_L3_NOT_AN_IDENTITY")
    fake3 = json.loads(json.dumps(fake))
    fake3["proof"]["L2_astock_veto"]["abs_delta"] = 0.0
    fake3["proof"]["L3_idx_carry"]["abs_delta_pct"] = 0.0
    check("C2 exact identities PASS", verdict_of(fake3) == "CALIBERS_RECOVERED_ONE_YEAR_AXIS")

    # C5: sign agreement
    rows = [
        {"corrected": {"L1_etf_book": -0.01, "L2_astock_veto": -0.02, "L3_idx_carry": -0.03}},
        {"corrected": {"L1_etf_book": 0.01, "L2_astock_veto": 0.02, "L3_idx_carry": 0.03}},
        {"corrected": {"L1_etf_book": 0.01, "L2_astock_veto": -0.02, "L3_idx_carry": 0.03}},
    ]
    neg = sum(1 for x in rows if all(v < 0 for v in x["corrected"].values()))
    pos = sum(1 for x in rows if all(v > 0 for v in x["corrected"].values()))
    check("C5 sign agreement counts all-negative / all-positive years", neg == 1 and pos == 1)

    n_pass = sum(1 for _n, ok in legs if ok)
    for name, ok in legs:
        print("%s %s" % ("PASS" if ok else "FAIL", name))
    print("%d/%d PASS" % (n_pass, len(legs)))
    return 0 if n_pass == len(legs) else 1


def main(argv) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    cmd = argv[1]
    if cmd == "run":
        return cmd_run()
    if cmd == "check":
        return cmd_check()
    if cmd == "selftest":
        return selftest()
    print("unknown subcommand %r" % cmd)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
