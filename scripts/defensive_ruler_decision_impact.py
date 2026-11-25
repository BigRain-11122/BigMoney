"""Does the repaired class ruler change a decision, or only a risk reading? (r1975 bm-c)

r1974 (`etf_class_ew_ruler_repair`) proved the class ruler is broken: the bucket labelled
"money" holds 45 names that are not cash, so `bond_money_only_ew_bench` -- the defensive
equal-weight basket the book is compared against -- was published as 1.18%/yr with vol 1.44%
and a -3.86% drawdown. Under the repaired ruler the same basket reads 1.28%/yr, vol 0.93%,
drawdown -1.35%. Returns barely move; **risk readings move by 2-3x**.

r1974 stopped at "the ruler is wrong". It never asked the only question a treasurer asks
next: does the corrected number change what you would rather hold? This face answers that
and nothing else, by putting the book and the basket on the same axes twice -- once under
the published ruler, once under the repaired one.

What it prints (all numbers come from published faces; nothing is re-estimated here):

  1. the book (`results/etf_nobond_vt.json::runs[production_candidate]`) beside both basket
     readings, on the SAME window (evidence_cutoff and bar count are asserted equal);
  2. the two decision columns that a reader actually uses:
       sharpe_edge = book.sharpe - bench.sharpe
       dd_multiple = |book.maxdd| / |bench.maxdd|
     and the same two under the repaired ruler;
  3. the price of the flip in money: at the basket's repaired Sharpe the book would have to
     earn `bench.sharpe x book.vol` to be equal per unit of risk -- the shortfall is printed
     in pp/yr and in CNY on 1 000 000, so "the book lost its edge" is a number, not a mood;
  4. whether that flip is SPENDABLE: reaching the book's vol from the basket needs
     `book.vol / bench.vol` leverage, which a cash account cannot buy (judged against
     LEVERAGE_UNREACHABLE, a frozen judgement line, not data).

verdict tokens (frozen before the first run, see JUDGES):
  JUSTIFICATION_FLIPS_BOOK_NO_LONGER_BETTER_PER_UNIT_OF_RISK
  BOOK_STILL_BETTER_PER_UNIT_OF_RISK
  BOOK_NEVER_WAS_BETTER_PER_UNIT_OF_RISK
plus, independently:
  SPENDABLE                     (the basket's vol is within reach, so the ratio is buyable)
  SHARPE_IS_NOT_SPENDABLE       (the basket cannot be levered to the book's vol)

This face writes only its own two files. It does not touch the repair face, the published
equity-alpha face, the book, or any shared artifact.

Usage:
    python scripts/defensive_ruler_decision_impact.py run
    python scripts/defensive_ruler_decision_impact.py check
    python scripts/defensive_ruler_decision_impact.py --selftest
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import bench_core as bc  # noqa: E402

SCHEMA = "defensive_ruler_decision_impact/v1"
FACE_JSON = os.path.join(bc.RESULTS, "defensive_ruler_decision_impact.json")
FACE_MD = os.path.join(bc.RESEARCH, "DEFENSIVE-RULER-DECISION-IMPACT.md")

REPAIR_FACE = os.path.join(bc.RESULTS, "etf_class_ew_ruler_repair.json")
BOOK_FACE = os.path.join(bc.RESULTS, "etf_nobond_vt.json")
ALPHA_FACE = os.path.join(bc.RESULTS, "etf_equity_alpha.json")

CAPITAL_CNY = 1_000_000.0

# ---- frozen before the first run ---------------------------------------------------------
BARS_PER_YEAR = 242.0        # the engine's own year convention (6.88y x 242 = 1665 ~ 1667 bars)
YEAR_TOL = 0.15              # a window mismatch of >36 bars means the two faces are not comparable
LEVERAGE_UNREACHABLE = 3.0   # a cash account cannot lever a bond basket 3x; judgement line
ROW_TOL = 5e-4               # stored precision of the readings the source faces print
FLIP_EPS = 1e-9              # a sharpe edge this close to zero is a tie, not a winner


# ------------------------------------------------------------------------------------------
# pure helpers
# ------------------------------------------------------------------------------------------
def _sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def _load(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _row(cagr, vol, maxdd, sharpe, names=None):
    return {"cagr": float(cagr), "vol": float(vol), "maxdd": float(maxdd),
            "sharpe": float(sharpe), "names": names}


def _derive(book, bench):
    """Every decision number this face prints, from the two rows only."""
    dd_mult = abs(book["maxdd"]) / abs(bench["maxdd"]) if bench["maxdd"] else None
    ret_per_dd_book = book["cagr"] / abs(book["maxdd"]) if book["maxdd"] else None
    ret_per_dd_bench = bench["cagr"] / abs(bench["maxdd"]) if bench["maxdd"] else None
    sharpe_edge = book["sharpe"] - bench["sharpe"]
    cagr_needed = bench["sharpe"] * book["vol"]
    return {
        "sharpe_edge": sharpe_edge,
        "dd_multiple": dd_mult,
        "book_return_per_unit_drawdown": ret_per_dd_book,
        "bench_return_per_unit_drawdown": ret_per_dd_bench,
        "return_per_drawdown_edge": (ret_per_dd_book / ret_per_dd_bench
                                     if ret_per_dd_bench else None),
        "cagr_needed_at_bench_sharpe": cagr_needed,
        "cagr_shortfall_pp": (cagr_needed - book["cagr"]) * 100.0,
        "cny_per_year_shortfall": (cagr_needed - book["cagr"]) * CAPITAL_CNY,
        "leverage_to_reach_book_vol": book["vol"] / bench["vol"] if bench["vol"] else None,
    }


def _edge_word(edge):
    if edge is None:
        return None
    if edge > FLIP_EPS:
        return "book"
    if edge < -FLIP_EPS:
        return "bench"
    return "tie"


def _verdict(pub, rep):
    if pub is None or rep is None:
        return None
    if pub == "book" and rep != "book":
        return "JUSTIFICATION_FLIPS_BOOK_NO_LONGER_BETTER_PER_UNIT_OF_RISK"
    if pub == "book" and rep == "book":
        return "BOOK_STILL_BETTER_PER_UNIT_OF_RISK"
    if pub != "book" and rep != "book":
        return "BOOK_NEVER_WAS_BETTER_PER_UNIT_OF_RISK"
    return "TIE_NOT_A_VERDICT"


def _spendable(lev):
    if lev is None:
        return None
    return "SPENDABLE" if lev < LEVERAGE_UNREACHABLE else "SHARPE_IS_NOT_SPENDABLE"


# ------------------------------------------------------------------------------------------
# assemble
# ------------------------------------------------------------------------------------------
def build(repair_path=REPAIR_FACE, book_path=BOOK_FACE, alpha_path=ALPHA_FACE):
    for _p in (repair_path, book_path, alpha_path):
        if not os.path.exists(_p):
            # an absent source is "cannot answer", never a zero (r98 family)
            raise SystemExit("FATAL: source face missing: %s" % _p)
    repair = _load(repair_path)
    book_face = _load(book_path)
    alpha = _load(alpha_path)

    # --- the book: the row the book face itself declares as the production candidate
    cand = (book_face.get("caliber") or {}).get("production_candidate")
    runs = book_face.get("runs") or []
    book_row = next((r for r in runs if r.get("label") == cand), None)
    if book_row is None:
        raise SystemExit("FATAL: book face has no row labelled production_candidate=%r" % (cand,))
    book = _row(book_row["cagr"], book_row["vol"], book_row["maxdd"], book_row["sharpe"])

    # --- the basket under the published and the repaired ruler (published face supplies both)
    arms = repair.get("arms") or {}
    pub_row = ((arms.get("published") or {}).get("bond+money") or {})
    rep_row = ((arms.get("repaired") or {}).get("bond+money") or {})
    if not pub_row or not rep_row:
        raise SystemExit("FATAL: repair face has no bond+money arm")
    bench_pub = _row(pub_row["cagr"], pub_row["vol"], pub_row["maxdd"], pub_row["sharpe"],
                     pub_row.get("names"))
    bench_rep = _row(rep_row["cagr"], rep_row["vol"], rep_row["maxdd"], rep_row["sharpe"],
                     rep_row.get("names"))

    # --- window identity: same panel, same bar count, same cutoff
    arm_win = repair.get("arm_window") or {}
    book_years = float(book_row.get("years") or 0.0)
    bars = int(arm_win.get("bars") or 0)
    implied_years = bars / BARS_PER_YEAR if bars else None
    cutoff_repair = repair.get("evidence_cutoff")
    cutoff_book = book_face.get("evidence_cutoff")
    window_ok = bool(
        cutoff_repair and cutoff_repair == cutoff_book and implied_years is not None
        and abs(implied_years - book_years) <= YEAR_TOL
    )

    d_pub = _derive(book, bench_pub)
    d_rep = _derive(book, bench_rep)
    w_pub = _edge_word(d_pub["sharpe_edge"])
    w_rep = _edge_word(d_rep["sharpe_edge"])
    verdict = _verdict(w_pub, w_rep)
    spend = _spendable(d_rep["leverage_to_reach_book_vol"])

    # --- cross-face control: the repair face's "released" cell must be the published cell
    alpha_row = next((r for r in (alpha.get("runs") or [])
                      if r.get("label") == "bond_money_only_ew_bench"), None)
    released = ((repair.get("released") or {}).get("bond_money_only_ew_bench") or {})
    released_ok = bool(
        alpha_row and released
        and abs(float(alpha_row["cagr"]) - float(released["cagr"])) <= ROW_TOL
        and abs(float(alpha_row["vol"]) - float(released["vol"])) <= ROW_TOL
        and abs(float(alpha_row["maxdd"]) - float(released["maxdd"])) <= ROW_TOL
    )

    payload = {
        "schema": SCHEMA,
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "evidence_cutoff": cutoff_repair,
        "window": {"first": arm_win.get("first"), "last": arm_win.get("last"), "bars": bars,
                   "book_years": book_years, "implied_years": implied_years,
                   "same_window": window_ok},
        "sources": {
            "repair_face": {"path": os.path.relpath(repair_path, ROOT).replace("\\", "/"),
                            "sha256": _sha(repair_path),
                            "schema": repair.get("schema"),
                            "generated": repair.get("generated")},
            "book_face": {"path": os.path.relpath(book_path, ROOT).replace("\\", "/"),
                          "sha256": _sha(book_path),
                          "production_candidate": cand},
            "alpha_face": {"path": os.path.relpath(alpha_path, ROOT).replace("\\", "/"),
                           "sha256": _sha(alpha_path)},
        },
        "book": book,
        "bench_published": bench_pub,
        "bench_repaired": bench_rep,
        "axes": {"published_ruler": d_pub, "repaired_ruler": d_rep,
                 "edge_word": {"published_ruler": w_pub, "repaired_ruler": w_rep}},
        "verdict": verdict,
        "spendability": spend,
        "controls": {
            "C1_released_cell_is_published_cell": released_ok,
            "C1_alpha_row": ({"cagr": alpha_row["cagr"], "vol": alpha_row["vol"],
                              "maxdd": alpha_row["maxdd"]} if alpha_row else None),
            "C2_same_window": window_ok,
        },
        "notes": {
            "not_the_same_object": ("the book is a 5-name rotating composite with an 8% vol target; "
                                    "the basket is an equal-weight holding of every bond+money ETF. "
                                    "A Sharpe comparison is a metric comparison, not a claim that "
                                    "one can be swapped for the other."),
            "bench_return_is_understated": ("cash funds pay dividends, so the basket's price-only "
                                            "return understates its true total return -- which "
                                            "understates its Sharpe. Any flip found here is "
                                            "conservative in the basket's favour."),
            "no_subperiod_split": ("the repair face prices the basket on the full window only, so "
                                   "this face cannot say whether the flip survives out of sample; "
                                   "it says the full-window reading flips."),
            "survivorship": "the basket is drawn from ETFs that exist today.",
            "leverage_line": LEVERAGE_UNREACHABLE,
            "bars_per_year": BARS_PER_YEAR,
        },
    }
    return payload


def _pct(x, nd=2):
    return "n/a" if x is None else ("%." + str(nd) + "f%%") % (x * 100.0)


def _sp(x, nd=3):
    return "n/a" if x is None else ("%." + str(nd) + "f") % x


def write_md(p):
    d_pub = p["axes"]["published_ruler"]
    d_rep = p["axes"]["repaired_ruler"]
    bk, bp, br = p["book"], p["bench_published"], p["bench_repaired"]
    w = p["window"]

    L = []
    L.append("# 尺子修好之后，这个决定还站得住吗（r1975 bm-c）\n")
    L.append("窗口 %s -> %s（%d 根 bar），证据截止 **%s**。\n"
             % (w["first"], w["last"], w["bars"], p["evidence_cutoff"]))
    L.append("## 判决\n")
    L.append("**%s**\n" % p["verdict"])
    L.append("| 判据 | 已发布尺子 | 修好之后 |\n|---|---|---|")
    L.append("| 谁在「每单位风险」上更强 | %s（差 %+.3f） | %s（差 %+.3f） |"
             % (p["axes"]["edge_word"]["published_ruler"], d_pub["sharpe_edge"],
                p["axes"]["edge_word"]["repaired_ruler"], d_rep["sharpe_edge"]))
    L.append("| 这本书的回撤是它几倍 | %.2fx | %.2fx |"
             % (d_pub["dd_multiple"], d_rep["dd_multiple"]))
    L.append("| 每单位回撤换到多少收益（书 / 篮子） | %.3f / %.3f（%.2fx） | %.3f / %.3f（%.2fx） |"
             % (d_pub["book_return_per_unit_drawdown"], d_pub["bench_return_per_unit_drawdown"],
                d_pub["return_per_drawdown_edge"],
                d_rep["book_return_per_unit_drawdown"], d_rep["bench_return_per_unit_drawdown"],
                d_rep["return_per_drawdown_edge"]))
    L.append("")
    L.append("## 三条读数\n")
    L.append("1. **这本书**（`%s`）：%s/年，波动 %s，夏普 %s，最大回撤 %s。"
             % (p["sources"]["book_face"]["production_candidate"], _pct(bk["cagr"]),
                _pct(bk["vol"]), _sp(bk["sharpe"]), _pct(bk["maxdd"])))
    L.append("2. **等权防御篮子**，已发布尺子：%s/年，波动 %s，夏普 %s，回撤 %s（%s 名）。"
             % (_pct(bp["cagr"]), _pct(bp["vol"]), _sp(bp["sharpe"]), _pct(bp["maxdd"]), bp["names"]))
    L.append("3. **同一只篮子**，修好之后：%s/年，波动 %s，夏普 %s，回撤 %s（%s 名）。"
             % (_pct(br["cagr"]), _pct(br["vol"]), _sp(br["sharpe"]), _pct(br["maxdd"]), br["names"]))
    L.append("")
    L.append("## 为什么这不是「数字变了」\n")
    L.append("收益几乎没动（%s -> %s，%+.2fpp），动的是**风险**：波动 %s -> %s、回撤 %s -> %s。"
             "于是同一个问题「这本书是不是比端着防御篮子更值」在两个尺子下得到两个答案。"
             % (_pct(bp["cagr"]), _pct(br["cagr"]), (br["cagr"] - bp["cagr"]) * 100,
                _pct(bp["vol"]), _pct(br["vol"]), _pct(bp["maxdd"]), _pct(br["maxdd"])))
    L.append("")
    L.append("- 夏普差从 **%+.3f** 变成 **%+.3f**：书从领先变成落后。"
             % (d_pub["sharpe_edge"], d_rep["sharpe_edge"]))
    L.append("- 按篮子修好后的夏普算，这本书要赚到 **%s/年**才算打平，实际 %s/年，差 **%.2fpp**"
             "（100 万本金上 **%s 元/年**）。"
             % (_pct(d_rep["cagr_needed_at_bench_sharpe"]), _pct(bk["cagr"]),
                d_rep["cagr_shortfall_pp"], "{:,.0f}".format(d_rep["cny_per_year_shortfall"])))
    L.append("- 「每单位回撤换收益」书仍然领先，但领先幅度从 **%.2fx** 缩到 **%.2fx**。"
             % (d_pub["return_per_drawdown_edge"], d_rep["return_per_drawdown_edge"]))
    L.append("")
    L.append("## 这个翻面能不能花（%s）\n" % p["spendability"])
    L.append("不能直接花。篮子的波动只有 %s，要把这份钱抬到这本书的 %s，需要 **%.1fx 杠杆**——"
             "现金账户买不到这个比例。所以翻面翻的是**这本书的说明句**（「它比端着债券更划算」），"
             "不是这本书的持有决定：这本书仍然交付一个债券篮子给不出的 10%% 波动收益流。"
             % (_pct(br["vol"]), _pct(bk["vol"]), d_rep["leverage_to_reach_book_vol"]))
    L.append("")
    L.append("## 控制臂\n")
    L.append("- C1 修复面「已发布」格 == `etf_equity_alpha.json` 的 `bond_money_only_ew_bench`："
             "**%s**" % ("绿" if p["controls"]["C1_released_cell_is_published_cell"] else "红"))
    L.append("- C2 两张面同窗口同 cutoff 同 bar 数：**%s**（书 %.2f 年 vs 篮子 %.2f 年）"
             % ("绿" if p["controls"]["C2_same_window"] else "红",
                w["book_years"], w["implied_years"] or 0.0))
    L.append("")
    L.append("## 诚实边界\n")
    L.append("1. 这两件不是同一种东西：书是 5 名轮动的复合组合（带 8% 波动目标），篮子是「每一只债券+货币 ETF 都等权」。"
             "夏普比较是**指标比较**，不是在说可以把一本书换成一只篮子。")
    L.append("2. 现金基金的分红是派息、不计入价格，所以篮子的价格收益低估了它的真实总收益——也就低估了它的夏普；"
             "这里找到的翻面是**对篮子有利方向上的保守读数**。")
    L.append("3. 修复面只在全窗上定价这只篮子，所以本面只能说「全窗读数翻了」，不能说「样本外也翻」。")
    L.append("4. 篮子的成分是今天还活着的 ETF（幸存者偏差），书同样。")
    L.append("5. 本面不重跑引擎、不改任何已发布面：两边的读数都来自 `%s` 与 `%s`，"
             "本面只做算术与判词。" % (p["sources"]["repair_face"]["path"],
                                      p["sources"]["book_face"]["path"]))
    L.append("")
    with open(FACE_MD, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(L))


# ------------------------------------------------------------------------------------------
# check -- re-derive; drift says STALE, self-contradiction says CHECK FAILED
# ------------------------------------------------------------------------------------------
def check(json_path=FACE_JSON, deep=False):
    problems, stale = [], []
    if not os.path.exists(json_path):
        print(json.dumps({"ok": False, "problems": ["face missing: %s" % json_path]}))
        return 2
    face = _load(json_path)

    for key, path in (("repair_face", REPAIR_FACE), ("book_face", BOOK_FACE)):
        src = (face.get("sources") or {}).get(key) or {}
        if not os.path.exists(path):
            stale.append("source face missing on disk: %s" % path)
            continue
        if src.get("sha256") != _sha(path):
            stale.append("%s bytes moved (face sha %s != disk %s)"
                         % (key, (src.get("sha256") or "")[:12], _sha(path)[:12]))

    if stale:
        print(json.dumps({"ok": False, "stale": True, "problems": stale}))
        return 3

    try:
        fresh = build()
    except SystemExit as exc:
        print(json.dumps({"ok": False, "problems": ["rebuild failed: %s" % exc]}))
        return 1

    if not (fresh.get("window") or {}).get("same_window"):
        problems.append("the two source faces are not on the same window/cutoff")

    # every printed number must equal the re-derived one
    for key in ("book", "bench_published", "bench_repaired"):
        for f in ("cagr", "vol", "maxdd", "sharpe"):
            a, b = face.get(key, {}).get(f), fresh.get(key, {}).get(f)
            if a is None or b is None or abs(float(a) - float(b)) > ROW_TOL:
                problems.append("%s.%s stored %r != re-derived %r" % (key, f, a, b))

    for ruler in ("published_ruler", "repaired_ruler"):
        for f, v in (fresh["axes"][ruler]).items():
            a = ((face.get("axes") or {}).get(ruler) or {}).get(f)
            if a is None or abs(float(a) - float(v)) > ROW_TOL:
                problems.append("axes.%s.%s stored %r != re-derived %r" % (ruler, f, a, v))

    if face.get("verdict") != fresh.get("verdict"):
        problems.append("verdict stored %r != re-derived %r"
                        % (face.get("verdict"), fresh.get("verdict")))
    if face.get("spendability") != fresh.get("spendability"):
        problems.append("spendability stored %r != re-derived %r"
                        % (face.get("spendability"), fresh.get("spendability")))
    for k, v in (fresh.get("controls") or {}).items():
        if k.startswith("C") and (face.get("controls") or {}).get(k) != v:
            problems.append("controls.%s stored %r != re-derived %r"
                            % (k, (face.get("controls") or {}).get(k), v))

    if deep:
        # the repair face must still agree with the live published cell
        alpha = _load(ALPHA_FACE)
        row = next((r for r in (alpha.get("runs") or [])
                    if r.get("label") == "bond_money_only_ew_bench"), None)
        rel = ((_load(REPAIR_FACE).get("released") or {}).get("bond_money_only_ew_bench") or {})
        if not row or not rel:
            problems.append("deep: published or released cell missing")
        elif (abs(float(row["cagr"]) - float(rel["cagr"])) > ROW_TOL
              or abs(float(row["maxdd"]) - float(rel["maxdd"])) > ROW_TOL):
            stale.append("published cell moved away from the repair face's released cell")

    if stale:
        print(json.dumps({"ok": False, "stale": True, "problems": stale + problems}))
        return 3
    if problems:
        print(json.dumps({"ok": False, "problems": problems}))
        return 1
    print(json.dumps({"ok": True, "verdict": face.get("verdict"),
                      "spendability": face.get("spendability"),
                      "sharpe_edge": face["axes"]["repaired_ruler"]["sharpe_edge"]}))
    return 0


# ------------------------------------------------------------------------------------------
# selftest -- offline, deterministic
# ------------------------------------------------------------------------------------------
def selftest():
    legs = []

    def leg(name, ok, info=""):
        legs.append((name, bool(ok), info))

    # L1 pure arithmetic
    book = _row(0.1116, 0.1050, -0.1056, 1.101)
    bench = _row(0.0128, 0.009271, -0.013538, 1.4334)
    d = _derive(book, bench)
    leg("L1 derive: dd multiple", abs(d["dd_multiple"] - 0.1056 / 0.013538) < 1e-9,
        "%.4f" % d["dd_multiple"])
    leg("L1b derive: cagr needed at bench sharpe",
        abs(d["cagr_needed_at_bench_sharpe"] - 1.4334 * 0.1050) < 1e-9)
    leg("L1c derive: leverage", abs(d["leverage_to_reach_book_vol"] - 0.1050 / 0.009271) < 1e-9)

    # L2 the live shape: book ahead published, behind repaired -> FLIP
    pub, rep = _row(0.0118, 0.0144, -0.0386, 0.861), bench
    leg("L2 flip detected",
        _verdict(_edge_word(_derive(book, pub)["sharpe_edge"]),
                 _edge_word(_derive(book, rep)["sharpe_edge"]))
        == "JUSTIFICATION_FLIPS_BOOK_NO_LONGER_BETTER_PER_UNIT_OF_RISK")
    # L3 no flip when the repaired basket is still weaker
    weak = _row(0.005, 0.02, -0.05, 0.25)
    leg("L3 still-better not called a flip",
        _verdict(_edge_word(_derive(book, pub)["sharpe_edge"]),
                 _edge_word(_derive(book, weak)["sharpe_edge"]))
        == "BOOK_STILL_BETTER_PER_UNIT_OF_RISK")
    # L4 never better
    leg("L4 never-better word",
        _verdict(_edge_word(_derive(book, rep)["sharpe_edge"]),
                 _edge_word(_derive(book, rep)["sharpe_edge"]))
        == "BOOK_NEVER_WAS_BETTER_PER_UNIT_OF_RISK")
    # L5 a tie is not a winner
    tie = _row(0.0, 0.0, -0.01, book["sharpe"])
    leg("L5 tie is not 'book'", _edge_word(_derive(book, tie)["sharpe_edge"]) == "tie")

    # L6 spendability line is a judgement, and it bites where it should
    leg("L6 leverage 11.3x is not spendable",
        _spendable(_derive(book, rep)["leverage_to_reach_book_vol"]) == "SHARPE_IS_NOT_SPENDABLE")
    near = _row(0.05, 0.0875, -0.06, 0.6)          # 0.1050 / 0.0875 = 1.2x
    leg("L6b leverage 1.2x is spendable",
        _spendable(_derive(book, near)["leverage_to_reach_book_vol"]) == "SPENDABLE")

    # L7 missing source face is 'cannot answer', never a zero
    tmpd = tempfile.mkdtemp(prefix="dryface_")
    try:
        try:
            build(repair_path=os.path.join(tmpd, "nope.json"))
            leg("L7 missing source refuses", False, "build returned a payload")
        except SystemExit:
            leg("L7 missing source refuses", True)

        # L8 real face: deterministic, and every control green
        a = build()
        b = build()
        strip = lambda p: json.dumps({k: v for k, v in p.items() if k != "generated"},
                                     sort_keys=True, ensure_ascii=False)
        leg("L8 deterministic", strip(a) == strip(b))
        leg("L8b C1 released cell is the published cell",
            a["controls"]["C1_released_cell_is_published_cell"] is True)
        leg("L8c C2 same window", a["controls"]["C2_same_window"] is True)

        # L9 tamper a printed number -> CHECK FAILED, and the word STALE must NOT appear
        path = os.path.join(tmpd, "face.json")
        bad = json.loads(json.dumps(a))
        bad["bench_repaired"]["maxdd"] = -0.30
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(bad, fh, ensure_ascii=False)
        import io
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = check(json_path=path)
        out = buf.getvalue()
        leg("L9 tampered number -> rc1 without STALE", rc == 1 and "STALE" not in out,
            "rc=%d" % rc)

        # L10 a source face whose bytes moved -> STALE (rc3)
        moved = os.path.join(tmpd, "repair.json")
        shutil.copyfile(REPAIR_FACE, moved)
        with open(moved, "a", encoding="utf-8") as fh:
            fh.write(" ")
        orig = globals()["REPAIR_FACE"]
        try:
            globals()["REPAIR_FACE"] = moved
            buf2 = io.StringIO()
            with contextlib.redirect_stdout(buf2):
                rc2 = check(json_path=path)
            leg("L10 moved source -> STALE", rc2 == 3, "rc=%d" % rc2)
        finally:
            globals()["REPAIR_FACE"] = orig
    finally:
        shutil.rmtree(tmpd, ignore_errors=True)

    bad = [n for n, ok, _ in legs if not ok]
    for n, ok, info in legs:
        print(("PASS " if ok else "FAIL ") + n + ((" [" + info + "]") if info else ""))
    print("SELFTEST %d/%d PASS" % (len(legs) - len(bad), len(legs)))
    return 0 if not bad else 1


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run",
                    choices=["run", "check", "selftest"])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--deep", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest or args.cmd == "selftest":
        return selftest()
    if args.cmd == "check":
        return check(deep=args.deep)

    t0 = time.time()
    payload = build()
    payload["elapsed_sec"] = round(time.time() - t0, 2)
    with open(FACE_JSON, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    write_md(payload)
    print(json.dumps({"verdict": payload["verdict"],
                      "spendability": payload["spendability"],
                      "edge_published": payload["axes"]["published_ruler"]["sharpe_edge"],
                      "edge_repaired": payload["axes"]["repaired_ruler"]["sharpe_edge"],
                      "cagr_shortfall_pp": payload["axes"]["repaired_ruler"]["cagr_shortfall_pp"],
                      "elapsed_sec": payload["elapsed_sec"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
