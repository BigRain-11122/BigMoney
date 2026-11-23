"""VERIFIED_LINES_MONEY_YEAR -- one page that puts the three validated money lines side by side.

Why this face exists
--------------------
Three lines in this repo have survived their own gates and each prints a *rate*:
the bond-free ETF book (7 names -> 5 names, 8% vol target, next-open fills),
the A-share residual veto (pool minus the top 20% residual names), and the
four-arm index-futures basis carry.  Every one of them prints an annualised
percentage over its own window.  A person deciding what to do with money does
not hold a percentage -- they hold a year that either made money or lost it.
Nobody has printed the three lines **year by year in CNY**, on the same page,
with each line's own execution caliber written beside it and the years in which
they lost together called out.  That is what this face is.

What it is not
--------------
- It is NOT a fourth strategy.  The three lines use different calibers (cost per
  side, fill timing, universe, rebalance grid) and their returns cannot be added
  into one engine.  "One third per line" here is arithmetic on three separate
  books of money, re-set every January, not a portfolio backtest.
- It does NOT re-price any line.  ETF is re-run because its published face keeps
  yearly totals as scalars only; astock and carry are read from their published
  years dicts.  If a line's own face disagrees with this page, that face wins.

Frozen reading rules (written before the numbers were read)
-----------------------------------------------------------
  M1  a year is the line's own year: first bar of the year (or the previous
      year's last level when available) to the last bar of that year.  2020 is
      therefore short for every line and is printed as `partial` where the bars
      are fewer than a full calendar year.
  M2  the combined row is the arithmetic mean of the lines that have a number
      for that year.  A missing line is NEVER read as zero (r98 family): the
      count of lines behind the number is printed beside it.
  M3  "lost together" means every line with a number that year was negative.  It
      is the reading a reader actually needs: diversification is judged in the
      bad year, not in the average.
  M4  a 7-point correlation is not a statistic.  This face does not print a
      correlation coefficient; it prints the sign-agreement count and says so.

Subcommands
-----------
  run       deterministic re-derivation (ETF engine ~70 s), writes results/ + research/
  check     re-derives every rate and every combined row from the published face
  selftest  hermetic synthetic checks of M1..M4 (no panel, no network)
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

OUT = os.path.join(ROOT, "results", "verified_lines_money_year.json")
MD = os.path.join(ROOT, "research", "VERIFIED_LINES_MONEY_YEAR.md")

CAPITAL = 1000000.0
YEAR_WINDOW = [str(y) for y in range(2020, 2027)]

LINES = [
    {
        "key": "L1_etf_book",
        "name": "ETF bond-free composite (production candidate)",
        "face": "results/etf_nobond_vt.json",
        "arm": "nobond_vt08",
        "caliber": {
            "cost_bp_per_side": 10.0,
            "execution": "decide at close t, own from open t+1 (entry_lag=1)",
            "universe": "equity + commodity + convertible ETFs (no bond/money)",
            "names": 5,
            "rebalance_bars": 20,
            "overlay": "8% vol target, de-lever only",
            "source": "scripts/etf_nobond_vt.py + scripts/etf_robust_pf.py::open_to_open_equity",
        },
    },
    {
        "key": "L2_astock_veto",
        "name": "A-share residual veto (arm B: pool minus top 20% residual)",
        "face": "results/astock_resid_veto_layer.json",
        "arm": "B",
        "caliber": {
            "cost_bp_per_side": 8.0,
            "execution": "equal weight on the rebalance date's eligible pool",
            "universe": "A-share panel, 5,181 symbols, liquidity >= 20m CNY 20d",
            "names": "whole eligible pool minus the top 20% residual names",
            "rebalance_bars": 20,
            "overlay": "none",
            "source": "scripts/astock_resid_veto_layer.py::run",
        },
    },
    {
        "key": "L3_idx_carry",
        "name": "Index-futures basis carry, four arms equal weight",
        "face": "results/idx_fut_carry_portfolio.json",
        "arm": "equal_weight_full",
        "caliber": {
            "cost_bp_per_side": 1.5,
            "execution": "close-to-close on the daily bar",
            "universe": "IC/IM/IF/IH long futures",
            "names": 4,
            "rebalance_bars": "weights change only when the book re-sizes",
            "overlay": "none (margin account, see idx_fut_leverage_washout)",
            "source": "scripts/idx_fut_carry_portfolio.py",
        },
    },
]


# ----------------------------------------------------------------------------- io
def _read_face(rel):
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def etf_yearly():
    """Re-run the published production candidate and cut it by calendar year (M1)."""
    import etf_composite_pf as E
    import etf_robust_pf as R
    import etf_equity_alpha as A

    close, openp, amt, feats = E.build_panel()
    close, openp, n_flip = A.repair_flips(close, openp)
    cmap = A.load_class_map()
    cls = A.classify(close.columns, cmap, close)
    cols = [c for c in close.columns if cls[c] in ("equity", "commodity", "convertible")]
    sc = E.build_score(close[cols], amt[cols], feats)
    ser, turn = R.open_to_open_equity(close[cols], openp[cols], amt[cols], sc, 20, 5, 0.0010,
                                      vol_target=0.08, entry_lag=1)
    years = yearly_from_series(ser)
    return {
        "years": years,
        "bars": int(len(ser)),
        "first": str(ser.index[0].date()),
        "last": str(ser.index[-1].date()),
        "turnover": round(float(turn), 2),
        "flips_repaired": int(n_flip),
        "universe": int(len(cols)),
        "end_level": round(float(ser.iloc[-1]), 6),
    }


def yearly_from_series(ser, full_year_bars=200):
    """M1: a year runs from the previous year's last level to this year's last level.

    The first year has no previous level, so it starts on its own first bar; that
    one bar's move is not booked, and the year is printed like any other.
    """
    out = {}
    prev = None
    for y in sorted({d.year for d in ser.index}):
        block = ser[[d.year == y for d in ser.index]]
        if len(block) == 0:
            continue
        base = prev if prev is not None else float(block.iloc[0])
        end = float(block.iloc[-1])
        out[str(y)] = {
            "ret": end / base - 1.0 if base else None,
            "bars": int(len(block)),
            "partial": bool(len(block) < full_year_bars),
            "base_level": round(base, 6),
            "end_level": round(end, 6),
        }
        prev = end
    return out


def astock_yearly(face):
    yr = ((face or {}).get("by_year") or {}).get("B") or {}
    out = {}
    for y, v in yr.items():
        out[str(y)] = {
            "ret": v.get("compound"),
            "bars": v.get("periods"),
            "partial": bool((v.get("periods") or 0) < 12),
            "base_level": None,
            "end_level": None,
        }
    return out


def carry_yearly(face):
    yrs = ((face or {}).get("equal_weight_full") or {}).get("years") or {}
    out = {}
    for y, v in yrs.items():
        out[str(y)] = {
            "ret": v.get("sum"),
            "bars": v.get("bars"),
            "partial": bool((v.get("bars") or 0) < 200),
            "base_level": None,
            "end_level": None,
        }
    return out


def mark_partial_in_cutoff_year(yearly, cutoff):
    """A year is partial if it is the cutoff year and the cutoff is not in December.

    The bar-count test alone cannot see this: the carry line holds 213 bars by
    2026-11-20, which is 'more than 200' yet still ten months of a year.  The
    cutoff month is the fact, the bar count is a proxy (M1).
    """
    if not cutoff or len(cutoff) < 7:
        return yearly
    cy, cm = cutoff[:4], int(cutoff[5:7])
    if cm < 12 and cy in yearly:
        yearly[cy]["partial"] = True
    return yearly


# ------------------------------------------------------------------------- maths
def combine_row(per_line, year):
    """M2: arithmetic mean over the lines that have a number; missing is not zero."""
    vals = [(k, v) for k, v in per_line.items() if v.get("ret") is not None]
    if not vals:
        return {"ret": None, "n_lines": 0, "lines": [], "missing": []}
    return {
        "ret": sum(v["ret"] for _k, v in vals) / len(vals),
        "n_lines": len(vals),
        "lines": [k for k, _v in vals],
        "missing": [k for k, v in per_line.items() if v.get("ret") is None],
    }


def money(ret):
    return None if ret is None else round(CAPITAL * (1.0 + ret), 2)


def sign_agreement(years, per_line):
    """M3/M4: how often the lines point the same way, and how often they all lost."""
    all_pos, all_neg, mixed = [], [], []
    for y in years:
        vals = [per_line[k][y]["ret"] for k in per_line
                if y in per_line[k] and per_line[k][y].get("ret") is not None]
        if not vals:
            continue
        if all(v > 0 for v in vals):
            all_pos.append(y)
        elif all(v < 0 for v in vals):
            all_neg.append(y)
        else:
            mixed.append(y)
    judged = len(all_pos) + len(all_neg) + len(mixed)
    return {
        "years_judged": judged,
        "years_all_positive": all_pos,
        "years_all_negative": all_neg,
        "years_mixed": mixed,
        "share_same_sign": round((len(all_pos) + len(all_neg)) / judged, 4) if judged else None,
        "note": ("%d 个年份点算不出相关系数（样本太短）；这一行只回答「它们有没有一起亏过」，"
                 "那才是把钱放进去的人真正感受到的事" % judged),
    }


def build():
    import datetime
    faces = {L["key"]: _read_face(L["face"]) for L in LINES}
    missing = [L["key"] for L in LINES if faces[L["key"]] is None]
    if missing:
        return {"state": "REFUSE", "state_why": "missing upstream face: %s" % ", ".join(missing)}

    etf = etf_yearly()
    cutoff_l2 = str((faces["L2_astock_veto"] or {}).get("evidence_cutoff") or "")
    cutoff_l3 = str((faces["L3_idx_carry"] or {}).get("evidence_cutoff") or "")
    per_line = {
        "L1_etf_book": mark_partial_in_cutoff_year(etf["years"], etf["last"]),
        "L2_astock_veto": mark_partial_in_cutoff_year(astock_yearly(faces["L2_astock_veto"]), cutoff_l2),
        "L3_idx_carry": mark_partial_in_cutoff_year(carry_yearly(faces["L3_idx_carry"]), cutoff_l3),
    }

    years = [y for y in YEAR_WINDOW if any(y in per_line[k] for k in per_line)]
    rows = []
    for y in years:
        row = {"year": y, "lines": {}, "combined": None}
        for k in per_line:
            v = per_line[k].get(y)
            row["lines"][k] = {
                "ret": None if not v or v.get("ret") is None else float(v["ret"]),
                "ret_pct": None if not v or v.get("ret") is None else round(100.0 * v["ret"], 4),
                "money_end_cny": money(v.get("ret")) if v else None,
                "bars": None if not v else v.get("bars"),
                "partial": None if not v else v.get("partial"),
            }
        comb = combine_row({k: (per_line[k].get(y) or {}) for k in per_line}, y)
        row["combined"] = {
            "ret": None if comb["ret"] is None else float(comb["ret"]),
            "ret_pct": None if comb["ret"] is None else round(100.0 * comb["ret"], 4),
            "money_end_cny": money(comb["ret"]),
            "n_lines": comb["n_lines"],
            "lines_present": comb["lines"],
            "missing": comb["missing"],
        }
        rows.append(row)

    signs = sign_agreement(years, per_line)
    worst = min((r for r in rows if r["combined"]["ret_pct"] is not None),
                key=lambda r: r["combined"]["ret_pct"], default=None)
    best = max((r for r in rows if r["combined"]["ret_pct"] is not None),
               key=lambda r: r["combined"]["ret_pct"], default=None)
    worst_line = {}
    for k in per_line:
        vals = [(y, per_line[k][y]["ret"]) for y in years
                if y in per_line[k] and per_line[k][y].get("ret") is not None]
        if vals:
            worst_line[k] = {"year": min(vals, key=lambda t: t[1])[0],
                             "ret_pct": round(100.0 * min(v for _y, v in vals), 4)}

    verdict = ("THREE_LINES_NEVER_LOST_TOGETHER" if not signs["years_all_negative"]
               else "THREE_LINES_LOST_TOGETHER_IN_%s" % "_".join(signs["years_all_negative"]))

    return {
        "generated": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "evidence_cutoff": max(str((faces["L2_astock_veto"] or {}).get("evidence_cutoff") or ""),
                               str((faces["L3_idx_carry"] or {}).get("evidence_cutoff") or ""),
                               etf["last"]),
        "kind": "verified_lines_money_year",
        "capital_cny": CAPITAL,
        "window": [years[0], years[-1]] if years else [],
        "rules": {
            "M1": "a year runs from the previous year's last level to this year's last level; short years are printed partial",
            "M2": "combined = arithmetic mean of the lines that have a number; a missing line is never zero",
            "M3": "lost together = every line with a number that year was negative",
            "M4": "7 points is not a statistic: no correlation coefficient is printed, only a sign count",
        },
        "lines": [{**L, "yearly": per_line[L["key"]]} for L in LINES],
        "rows": rows,
        "sign_agreement": signs,
        "worst_combined_year": None if not worst else {
            "year": worst["year"], "ret_pct": worst["combined"]["ret_pct"],
            "money_end_cny": worst["combined"]["money_end_cny"]},
        "best_combined_year": None if not best else {
            "year": best["year"], "ret_pct": best["combined"]["ret_pct"],
            "money_end_cny": best["combined"]["money_end_cny"]},
        "worst_year_per_line": worst_line,
        "verdict": verdict,
        "cannot_be_added": ("the three lines run different calibers (10/8/1.5 bp per side, "
                            "next-open vs same-day close vs rebalance-date fills, different "
                            "universes); one third per line is three separate books of money, "
                            "not one portfolio backtest"),
        "state": "ok",
        "state_why": None,
        "upstream": {
            "L1": {"face": "results/etf_nobond_vt.json", "bars": etf["bars"], "first": etf["first"],
                   "last": etf["last"], "turnover": etf["turnover"],
                   "flips_repaired": etf["flips_repaired"], "universe": etf["universe"],
                   "end_level": etf["end_level"]},
            "L2": {"face": "results/astock_resid_veto_layer.json",
                   "cutoff": (faces["L2_astock_veto"] or {}).get("evidence_cutoff"),
                   "generated": (faces["L2_astock_veto"] or {}).get("generated")},
            "L3": {"face": "results/idx_fut_carry_portfolio.json",
                   "cutoff": (faces["L3_idx_carry"] or {}).get("evidence_cutoff"),
                   "generated": (faces["L3_idx_carry"] or {}).get("generated")},
        },
    }


# -------------------------------------------------------------------------- check
def check():
    face = _read_face("results/verified_lines_money_year.json")
    if not face:
        print("check FAIL: no face at results/verified_lines_money_year.json")
        return 1
    probs = []
    rows = face.get("rows") or []
    if not rows:
        probs.append("no rows")
    per_line, line_year = {}, {}
    for L in face.get("lines") or []:
        k = L["key"]
        line_year[k] = L.get("yearly") or {}
        for y, v in line_year[k].items():
            per_line.setdefault(y, {})[k] = v
    for r in rows:
        y = r["year"]
        # M2 is re-derived on the face's own full-precision `ret`, not on the 4dp `ret_pct`
        # (r1935: a tolerance must name where it comes from; 4dp printing is not a rule)
        vals = [v["ret"] for v in r["lines"].values() if v.get("ret") is not None]
        if not vals:
            probs.append("%s: no priced line, yet a row was printed" % y)
            continue
        want = sum(vals) / len(vals)
        got = r["combined"]["ret"]
        if got is None or abs(want - got) > 1e-12:
            probs.append("%s: combined %s != mean of lines %.12f" % (y, got, want))
        if r["combined"]["n_lines"] != len(vals):
            probs.append("%s: n_lines %s != priced %d" % (y, r["combined"]["n_lines"], len(vals)))
        money_got = r["combined"]["money_end_cny"]
        money_want = round(face["capital_cny"] * (1.0 + want), 2)
        if money_got is None or abs(money_got - money_want) > 0.01:
            probs.append("%s: money %s != capital*(1+r) %s" % (y, money_got, money_want))
        if r["combined"]["ret_pct"] is not None and abs(r["combined"]["ret_pct"] - want * 100.0) > 5e-5:
            probs.append("%s: printed percent %.6f is not the rate it carries" % (y, r["combined"]["ret_pct"]))
    # M3 re-derivation
    all_neg = []
    for y in [r["year"] for r in rows]:
        vals = [v["ret"] for v in per_line.get(y, {}).values() if v.get("ret") is not None]
        if vals and all(v < 0 for v in vals):
            all_neg.append(y)
    if (face.get("sign_agreement") or {}).get("years_all_negative") != all_neg:
        probs.append("sign_agreement.years_all_negative does not match the rows")
    if bool(face.get("verdict", "").startswith("THREE_LINES_LOST_TOGETHER")) != bool(all_neg):
        probs.append("verdict contradicts the all-negative years")
    # calibers must be printed, otherwise the page cannot be read
    for L in face.get("lines") or []:
        c = L.get("caliber") or {}
        for f in ("cost_bp_per_side", "execution", "universe"):
            if f not in c:
                probs.append("%s: caliber missing %s" % (L["key"], f))
    if not face.get("cannot_be_added"):
        probs.append("the page does not say the lines cannot be added")
    if probs:
        print("check FAIL:")
        for p in probs:
            print("  -", p)
        return 1
    print("check ok: %d rows, %d all-negative year(s), verdict %s"
          % (len(rows), len(all_neg), face.get("verdict")))
    return 0


# ------------------------------------------------------------------------ report
def write_md(face):
    L = {x["key"]: x for x in face["lines"]}
    years = face["window"]
    out = []
    out.append("# VERIFIED_LINES_MONEY_YEAR\n")
    out.append("三本书、同一个年份轴、同一笔 100 万。生成 %s；证据截止 %s。\n"
               % (face["generated"], face["evidence_cutoff"]))
    out.append("这不是第四条策略，也不是组合回测。三条线的成本口径、成交时点、票池都不同"
               "（10 / 8 / 1.5 bp 每边；次日开盘 vs 当日收盘 vs 调仓日等权；票池分别是 ETF、"
               "全 A 股、股指期货）。「每样三分之一」是三笔钱、每年一月初重新分配，"
               "不是一台引擎跑出来的组合。\n")
    out.append("## 一、逐年钱表（100 万，年初进、年末出）\n")
    hdr = "| 年 | ETF复合书 | A股残差黑名单 | 期货carry | 三线等权（几条线在算） | 等权年末市值 |"
    out.append(hdr)
    out.append("|---|---|---|---|---|---|")
    for r in face["rows"]:
        def cell(k):
            v = r["lines"][k]
            if v["ret_pct"] is None:
                return "—"
            s = "%+.2f%%" % v["ret_pct"]
            if v.get("partial"):
                s += "（未满年）"
            return s
        c = r["combined"]
        out.append("| %s | %s | %s | %s | %+.2f%%（%d 条） | %s 元 |"
                   % (r["year"], cell("L1_etf_book"), cell("L2_astock_veto"), cell("L3_idx_carry"),
                      c["ret_pct"], c["n_lines"], "{:,.0f}".format(c["money_end_cny"])))
    out.append("")
    sa = face["sign_agreement"]
    out.append("## 二、它们有没有一起亏过\n")
    out.append("- 判过的年份：%d 年（%s..%s）" % (sa["years_judged"], years[0], years[-1]))
    out.append("- **三条线同时亏钱的年份：%s**" % ("、".join(sa["years_all_negative"]) or "0 个"))
    out.append("- 三条线同时赚钱的年份：%s" % ("、".join(sa["years_all_positive"]) or "0 个"))
    out.append("- 方向一致率：%.1f%%" % (100.0 * sa["share_same_sign"]) if sa["share_same_sign"] is not None else "- 方向一致率：—")
    out.append("- %s" % sa["note"])
    out.append("")
    out.append("## 三、每条线最差的一年（读者真正会在意的那一格）\n")
    for k, v in face["worst_year_per_line"].items():
        out.append("- %s：%s 年 %+.2f%%" % (L[k]["name"], v["year"], v["ret_pct"]))
    out.append("")
    wc, bc = face["worst_combined_year"], face["best_combined_year"]
    if wc:
        out.append("三线等权最差一年：**%s 年 %+.2f%%**（100 万变成 %s 元）" %
                   (wc["year"], wc["ret_pct"], "{:,.0f}".format(wc["money_end_cny"])))
    if bc:
        out.append("三线等权最好一年：**%s 年 %+.2f%%**（100 万变成 %s 元）" %
                   (bc["year"], bc["ret_pct"], "{:,.0f}".format(bc["money_end_cny"])))
    out.append("")
    out.append("## 四、每条线的口径（不可相加的原因写在这里）\n")
    for k, L_ in L.items():
        c = L_["caliber"]
        out.append("### %s\n" % L_["name"])
        out.append("- 成本：%.1f bp / 边" % c["cost_bp_per_side"])
        out.append("- 成交：%s" % c["execution"])
        out.append("- 票池：%s" % c["universe"])
        out.append("- 名数：%s" % c["names"])
        out.append("- 网格：%s；叠加：%s" % (c["rebalance_bars"], c["overlay"]))
        out.append("- 出处：%s\n" % c["source"])
    out.append("## 五、结论\n")
    out.append("**%s**\n" % face["verdict"])
    out.append("判读边界：①三条线窗口不同（ETF/A股 2020 起、carry 2017 起，本页只取 2020 起对齐）；"
               "②2026 年三条线都未满年（截止 %s）；③7 个年份点算不出相关系数，本页只报方向一致率；"
               "④A股残差线是 5,000+ 只等权，实盘要按流动性切；⑤carry 是保证金账户，"
               "单品种档位会爆仓（见 idx_fut_leverage_washout），本页的 carry 收益没有计追缴。\n"
               % face["evidence_cutoff"])
    with open(MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out))
    return MD


# ---------------------------------------------------------------------- selftest
def selftest():
    import datetime as dt
    import pandas as pd

    fails = []
    n_checked = [0]

    def ok(cond, name):
        n_checked[0] += 1
        print("%s %s" % ("PASS" if cond else "FAIL", name))
        if not cond:
            fails.append(name)

    # L1: M1 yearly slicing, previous-year-end base
    idx = pd.to_datetime(["2021-12-30", "2021-12-31", "2022-01-04", "2022-12-30"])
    ser = pd.Series([1.00, 1.10, 1.15, 1.32], index=idx)
    y = yearly_from_series(ser, full_year_bars=2)
    ok(abs(y["2022"]["ret"] - (1.32 / 1.10 - 1)) < 1e-12,
       "M1 the year starts from the PREVIOUS year's last level, not its own first bar")
    ok(y["2022"]["bars"] == 2 and y["2022"]["partial"] is False, "M1 bars counted, full year not partial")

    idx2 = pd.to_datetime(["2023-01-03", "2023-06-30"])
    y2 = yearly_from_series(pd.Series([2.0, 2.2], index=idx2), full_year_bars=200)
    ok(y2["2023"]["partial"] is True, "M1 a short year is marked partial")

    # L2: M2 combined is the mean over PRESENT lines only; missing is not zero
    row = combine_row({"a": {"ret": 0.10}, "b": {"ret": None}, "c": {"ret": 0.20}}, "2022")
    ok(abs(row["ret"] - 0.15) < 1e-12 and row["n_lines"] == 2,
       "M2 missing line is dropped, not read as 0 (mean of 2, not 3)")
    ok(row["missing"] == ["b"], "M2 the missing line is named")
    ok(combine_row({"a": {"ret": None}}, "2022")["ret"] is None,
       "M2 no priced line -> no number at all")

    # L3: M3 all-negative detection
    per = {"a": {"2020": {"ret": -0.1}, "2021": {"ret": 0.1}},
           "b": {"2020": {"ret": -0.2}, "2021": {"ret": 0.2}},
           "c": {"2020": {"ret": -0.3}, "2021": {"ret": -0.05}}}
    sa = sign_agreement(["2020", "2021"], per)
    ok(sa["years_all_negative"] == ["2020"], "M3 the all-negative year is found")
    ok(sa["years_mixed"] == ["2021"] and sa["share_same_sign"] == 0.5,
       "M3 a mixed year is not counted as agreement")

    # L4: M4 no correlation is invented
    ok("相关系数" in sa["note"] and "一起亏" in sa["note"],
       "M4 the note says a sign count is not a correlation")

    # L5: money conversion
    ok(money(0.10) == 1100000.0 and money(-0.25) == 750000.0, "money() converts a rate on 1,000,000")
    ok(money(None) is None, "money(None) is None, never 0")

    # L6: astock/carry adapters keep partial flags
    a = astock_yearly({"by_year": {"B": {"2020": {"periods": 7, "compound": -0.09},
                                         "2021": {"periods": 12, "compound": 0.27}}}})
    ok(a["2020"]["partial"] is True and a["2021"]["partial"] is False,
       "astock adapter: fewer than 12 periods in a year is partial")
    c = carry_yearly({"equal_weight_full": {"years": {"2026": {"bars": 213, "sum": 0.06}}}})
    ok(c["2026"]["ret"] == 0.06 and c["2026"]["partial"] is False,
       "carry adapter: 213 bars is not < 200, so 2026 is not marked partial (bars threshold is per face)")

    # L7: a line without a number cannot influence the verdict
    per2 = {"a": {"2020": {"ret": -0.1}}, "b": {"2020": {"ret": None}}}
    sa2 = sign_agreement(["2020"], per2)
    ok(sa2["years_all_negative"] == ["2020"] and sa2["years_judged"] == 1,
       "M3 a year is judged on the lines that have numbers")

    # L8: the cutoff month decides partial, not the bar count
    y3 = mark_partial_in_cutoff_year({"2025": {"ret": 0.1, "bars": 243, "partial": False},
                                      "2026": {"ret": 0.02, "bars": 213, "partial": False}},
                                     "2026-11-20")
    ok(y3["2026"]["partial"] is True and y3["2025"]["partial"] is False,
       "M1 a 213-bar year cut off in November is still partial; a finished year is not")
    y4 = mark_partial_in_cutoff_year({"2026": {"ret": 0.1, "bars": 243, "partial": False}},
                                     "2026-12-31")
    ok(y4["2026"]["partial"] is False,
       "M1 a December cutoff does not by itself make the year partial")
    ok(mark_partial_in_cutoff_year({"2019": {"ret": 0.1, "partial": False}}, "") ["2019"]["partial"] is False,
       "M1 no cutoff -> nothing is marked")

    total = n_checked[0]
    print("\nselftest %d/%d" % (total - len(fails), total))
    return 0 if not fails else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lstrip("-")
    if cmd == "selftest":
        return selftest()
    if cmd == "check":
        return check()
    face = build()
    if face.get("state") != "ok":
        print("REFUSE:", face.get("state_why"))
        return 2
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=1)
    write_md(face)
    print("rows %d  verdict %s" % (len(face["rows"]), face["verdict"]))
    for r in face["rows"]:
        c = r["combined"]
        print("  %s  L1 %+7.2f%%  L2 %+7.2f%%  L3 %+7.2f%%  combined %+7.2f%% (%d lines)  %s CNY"
              % (r["year"],
                 r["lines"]["L1_etf_book"]["ret_pct"],
                 r["lines"]["L2_astock_veto"]["ret_pct"],
                 r["lines"]["L3_idx_carry"]["ret_pct"],
                 c["ret_pct"], c["n_lines"], "{:,.0f}".format(c["money_end_cny"])))
    print("all-negative years:", face["sign_agreement"]["years_all_negative"])
    print("saved", OUT)
    print("saved", MD)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
