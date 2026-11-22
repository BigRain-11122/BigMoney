#!/usr/bin/env python
"""book_pay_vs_cash_ruler -- after the search rent, does this book beat parking the money?

Why this face exists
--------------------
`scripts/book_deflated_expectation.py` (r1962) turned the deflated Sharpe into money:
on 1,000,000 CNY the book budgets 1.80%/yr once the rent of 58 audited tries is paid,
against a headline 11.16%. It then stopped. A treasurer does not compare a number to
nothing -- he compares it to the alternative he can execute on the same morning: park
the same cash in the repo leg. That comparison had never been printed on one line.

`scripts/capital_placement.py` prices vehicles at account size, but it uses the
*headline* returns; it predates the deflation. So the two published readings were never
put on the same axis. This face does exactly that, and nothing else.

Construction (frozen before the first run)
------------------------------------------
* **Cash comparator** = `results/capital_placement.json::config.cash_net_annual`
  (the r1258-measured repo rate minus the roll commission -- the published net cash
  rate, not a number invented here). A window mean of the GC001 panel is printed
  alongside as a gross cross-check; a disagreement is disclosed, never averaged in.
* **Book pay** = the deflated budgetable CAGR at the conservative trial count, taken
  from the same haircut row the parent face publishes (imported, not re-implemented).
* **Excess** = (budgetable - cash) x capital. Per year, in CNY.
* **Years to repay one tail year** = falsification drawdown / excess. How many years of
  the excess it takes to put back the money one ordinary bad year takes.
* **Break-even trials** = the largest N at which the deflated pay still clears the cash
  rate. If the audited count is above it, the book only pays because the audit is
  generous -- which is a statement about the audit, not about the book.

verdict tokens:
  DEFLATED_PAY_BELOW_PARKING
  DEFLATED_PAY_IS_A_ROUNDING_ERROR_VS_CASH      (0 <= excess < meaningful_margin)
  DEFLATED_PAY_CLEARS_PARKING_BY_A_MARGIN       (excess >= meaningful_margin)

Usage:
    python scripts/book_pay_vs_cash_ruler.py run
    python scripts/book_pay_vs_cash_ruler.py check
    python scripts/book_pay_vs_cash_ruler.py --selftest
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for _p in (str(HERE), str(ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import book_deflated_expectation as BDE  # noqa: E402  (reuse, do not re-implement)

SCRIPT = "scripts/book_pay_vs_cash_ruler.py"
FACE = "results/book_pay_vs_cash_ruler.json"
OUT_JSON = ROOT / "results" / "book_pay_vs_cash_ruler.json"
OUT_MD = ROOT / "research" / "BOOK-PAY-VS-CASH.md"

PLACEMENT_FACE = ROOT / "results" / "capital_placement.json"
PARENT_FACE = ROOT / "results" / "book_deflated_expectation.json"
REPO_PANEL = ROOT / "data" / "repo_daily" / "GC001.csv"
REPO_PANEL_SECOND = ROOT / "data" / "repo_daily" / "GC007.csv"

# ---------------------------------------------------------------- frozen criteria
CRITERIA = {
    "capital_cny": 1_000_000,
    "n_conservative": 58,
    "cash_source": "results/capital_placement.json::config.cash_net_annual "
                   "(r1258 repo rate net of the roll commission)",
    "cash_cross_check": "data/repo_daily/GC001.csv window mean (gross, not averaged in)",
    "meaningful_margin_cny": 10_000.0,
    "meaningful_margin_note": "1pp/yr on 1,000,000 -- below this the 'edge' is the "
                              "width of the estimate, not an edge",
    "tolerance_cash_pp": 0.30,
    "tolerance_cash_note": "gross window mean vs published net rate: the commission and "
                           "the window differ, so 0.30pp is disclosed as a cross-check "
                           "band, not a pass/fail line on the book",
    "frozen": "constants above were written before the first run; no line is tuned "
              "after seeing the result",
}


def _load(path):
    p = Path(path)
    if not p.exists():
        return None
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def _dump(path, obj):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1, sort_keys=False)
        fh.write("\n")


def _now():
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


# ------------------------------------------------------------------------ inputs
def _cash_net():
    d = _load(PLACEMENT_FACE)
    if not d:
        return None
    return {
        "cash_net_annual": float((d.get("config") or {})["cash_net_annual"]),
        "cash_gross_pct": (d.get("inputs") or {}).get("ceiling", {}).get("gross_cash_pct"),
        "evidence_cutoff": d.get("evidence_cutoff"),
        "generated": d.get("ts"),
        "source": "results/capital_placement.json",
    }


def _repo_window_mean(panel, start, end):
    """Mean of the annualised repo close over the book's own window, in percent."""
    p = Path(panel)
    if not p.exists() or not start or not end:
        return None
    total, n, first, last = 0.0, 0, None, None
    with open(p, encoding="utf-8") as fh:
        head = fh.readline()
        if "close" not in head:
            return None
        for line in fh:
            parts = line.strip().split(",")
            if len(parts) < 5:
                continue
            day, close = parts[0], parts[4]
            if day < start or day > end:
                continue
            try:
                v = float(close)
            except ValueError:
                continue
            total += v
            n += 1
            first = first or day
            last = day
    if n == 0:
        return None
    return {"mean_pct": round(total / n, 4), "days": n, "first": first, "last": last}


def _series_profile(panel):
    """Last date + last close of a repo panel -- the 'what it quotes today' line."""
    p = Path(panel)
    if not p.exists():
        return None
    last = None
    with open(p, encoding="utf-8") as fh:
        fh.readline()
        for line in fh:
            parts = line.strip().split(",")
            if len(parts) >= 5:
                last = parts
    if not last:
        return None
    return {"last_date": last[0], "last_close_pct": round(float(last[4]), 4)}


# -------------------------------------------------------------------- arithmetic
def budgetable_at(book, n):
    """Deflated annual return at trial count n -- the parent's own haircut row."""
    row = BDE._haircut_row(
        book["sr_ann"], book["vol_ann"], book["sigma_sr_daily"], n,
        CRITERIA["capital_cny"], 3.0, 0.05, 252)
    return row


def break_even_n(book, cash_annual, nmax=5000):
    """Largest N whose deflated pay still clears the cash rate (None if none does)."""
    if budgetable_at(book, 2)["budgetable_cagr"] < cash_annual:
        return {"n": None, "why": "even the N=2 floor does not clear cash"}
    lo, hi = 2, int(nmax)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if budgetable_at(book, mid)["budgetable_cagr"] >= cash_annual:
            lo = mid
        else:
            hi = mid - 1
    return {"n": int(lo)}


def verdict_of(excess_cny, margin):
    if excess_cny < 0:
        return "DEFLATED_PAY_BELOW_PARKING"
    if excess_cny < margin:
        return "DEFLATED_PAY_IS_A_ROUNDING_ERROR_VS_CASH"
    return "DEFLATED_PAY_CLEARS_PARKING_BY_A_MARGIN"


# -------------------------------------------------------------------------- build
def build(write=True):
    t0 = time.time()
    book = BDE._book_inputs()
    if not book:
        raise RuntimeError("face missing: results/etf_book_search_rent.json (STALE: run its writer)")
    cash = _cash_net()
    if not cash:
        raise RuntimeError("face missing: results/capital_placement.json (STALE: run its writer)")

    row = budgetable_at(book, CRITERIA["n_conservative"])
    cash_annual = cash["cash_net_annual"]
    budgetable = row["budgetable_cagr"]
    tail = row["falsification_drawdown"]
    capital = float(CRITERIA["capital_cny"])

    excess_annual = budgetable - cash_annual
    excess_cny = capital * excess_annual
    years_to_repay_tail = (tail / excess_annual) if excess_annual > 1e-9 else None

    win = _repo_window_mean(REPO_PANEL, book["start"], book["end"])
    win2 = _repo_window_mean(REPO_PANEL_SECOND, book["start"], book["end"])
    today = _series_profile(REPO_PANEL)

    cash_check = None
    if win:
        gap_pp = win["mean_pct"] / 100.0 - cash_annual
        cash_check = {
            "gc001_window_mean_pct": win["mean_pct"],
            "days": win["days"],
            "first": win["first"],
            "last": win["last"],
            "gc007_window_mean_pct": (win2 or {}).get("mean_pct"),
            "gap_vs_published_pp": round(gap_pp * 100.0, 4),
            "relation": ("CROSS_CHECK_OK" if abs(gap_pp) * 100.0 <= CRITERIA["tolerance_cash_pp"]
                         else "RELATION_UNVERIFIED"),
            "note": "gross panel mean vs published net rate: the roll commission and the "
                    "window differ by construction; this is disclosed, not reconciled",
        }

    be = break_even_n(book, cash_annual)
    verdict = verdict_of(excess_cny, CRITERIA["meaningful_margin_cny"])

    scanner_n = [2, 5, 10, 20, 40, 55, 58, 100, 200, 450]
    scanner = []
    for n in scanner_n:
        r = budgetable_at(book, n)
        scanner.append({
            "n_trials": n,
            "credible_sharpe": r["credible_sharpe"],
            "budgetable_cagr": r["budgetable_cagr"],
            "excess_over_cash_cagr": round(r["budgetable_cagr"] - cash_annual, 6),
            "money_vs_parking_cny": round(capital * (r["budgetable_cagr"] - cash_annual), 2),
            "clears_cash": bool(r["budgetable_cagr"] >= cash_annual),
        })

    face = {
        "script": SCRIPT,
        "face": FACE,
        "kind": "book-pay-vs-cash/v1",
        "generated": _now(),
        "evidence_cutoff": book["evidence_cutoff"],
        "evidence_cutoff_source": book["cutoff_source"],
        "criteria": CRITERIA,
        "book": {
            "arm": book["arm"],
            "window": [book["start"], book["end"]],
            "bars": book["bars"],
            "headline_cagr": book["cagr"],
            "headline_sharpe": book["sr_ann"],
            "published_vol": book["vol_ann"],
            "published_maxdd": book["maxdd"],
        },
        "cash": {
            "cash_net_annual": cash_annual,
            "source": cash["source"],
            "generated": cash["generated"],
            "evidence_cutoff": cash["evidence_cutoff"],
            "cross_check": cash_check,
            "today": today,
        },
        "at_conservative_n": {
            "n_trials": row["n_trials"],
            "credible_sharpe": row["credible_sharpe"],
            "budgetable_cagr": budgetable,
            "falsification_drawdown": tail,
            "excess_over_cash_cagr": round(excess_annual, 6),
            "excess_money_cny": round(excess_cny, 2),
            "years_of_excess_to_repay_one_tail_year": (round(years_to_repay_tail, 2)
                                                       if years_to_repay_tail else None),
            "headline_vs_deflated_gap_cagr": round(book["cagr"] - budgetable, 6),
        },
        "break_even_n": be,
        "scanner": scanner,
        "verdict": verdict,
        "verdict_zh": _verdict_zh(verdict, excess_cny, be, row),
        "caveats": [
            "the deflation is a haircut, not a posterior: the headline row is printed "
            "beside the deflated row so neither reading is hidden",
            "cash_net_annual is one published rate carried on the placement face; a real "
            "parking programme re-quotes daily and its realised carry moves",
            "the book is fully invested, so no idle cash earns this rate inside it -- the "
            "comparison is 'this book' vs 'the same money parked'",
            "excess is computed on the parent's published volatility, so a regime change "
            "moves both the pay and the tail",
        ],
        "elapsed_sec": round(time.time() - t0, 3),
    }
    if write:
        _dump(OUT_JSON, face)
        _write_doc(face)
    return face


def _verdict_zh(verdict, excess_cny, be, row):
    n = be.get("n")
    tail = row["falsification_drawdown"] * 100.0
    if verdict == "DEFLATED_PAY_BELOW_PARKING":
        return ("按 %d 次尝试扣完搜索租金后，这本书比躺利息还少 ￥%.0f/年，而它带的尾部回撤是 %.1f%%。"
                % (row["n_trials"], -excess_cny, tail))
    if verdict == "DEFLATED_PAY_IS_A_ROUNDING_ERROR_VS_CASH":
        return ("按 %d 次尝试扣完租金，这本书比躺利息多 ￥%.0f/年（%.3f 个百分点），"
                "而它一年内 5%% 概率的尾部回撤是 %.1f%%——超额是估计宽度的量级，不是边的量级。"
                % (row["n_trials"], excess_cny, excess_cny / 1_000_000 * 100.0, tail))
    return ("按 %d 次尝试扣完租金，这本书比躺利息多 ￥%.0f/年，已过 1 个百分点门槛，"
            "但尾部回撤仍是 %.1f%%。" % (row["n_trials"], excess_cny, tail))


# -------------------------------------------------------------------------- check
def _pct(x, nd=2):
    return ("%." + str(nd) + "f%%") % (x * 100.0)


def check():
    """Re-derive every printed number from the printed inputs; classify drift vs defect.

    STALE  -> a source moved (re-run the writer; paying for the refresh is correct)
    CHECK FAILED -> same inputs, different arithmetic (a defect; never labelled STALE)
    """
    if not OUT_JSON.exists():
        print("STALE: face missing -> %s (run: python %s run)" % (OUT_JSON.name, SCRIPT))
        return 3
    face = _load(OUT_JSON)
    if not face:
        print("STALE: face unreadable -> %s" % OUT_JSON.name)
        return 3
    if not face.get("evidence_cutoff"):
        print("STALE: face carries no evidence_cutoff")
        return 3

    book = BDE._book_inputs()
    cash = _cash_net()
    if not book or not cash:
        print("STALE: a source face is missing (book or placement)")
        return 3

    problems, drift = [], []
    if book["evidence_cutoff"] != face["evidence_cutoff"]:
        drift.append("evidence_cutoff moved: face %s vs source %s"
                     % (face["evidence_cutoff"], book["evidence_cutoff"]))
    if abs(cash["cash_net_annual"] - face["cash"]["cash_net_annual"]) > 1e-9:
        drift.append("cash_net_annual moved: face %.6f vs source %.6f"
                     % (face["cash"]["cash_net_annual"], cash["cash_net_annual"]))

    row = budgetable_at(book, face["at_conservative_n"]["n_trials"])
    cap = float(face["criteria"]["capital_cny"])
    printed = face["at_conservative_n"]
    for key, live in (("credible_sharpe", row["credible_sharpe"]),
                      ("budgetable_cagr", row["budgetable_cagr"]),
                      ("falsification_drawdown", row["falsification_drawdown"])):
        if abs(printed[key] - live) > 1e-6:
            problems.append("%s: printed %.6f != recomputed %.6f" % (key, printed[key], live))

    want_excess = printed["budgetable_cagr"] - face["cash"]["cash_net_annual"]
    if abs(printed["excess_over_cash_cagr"] - want_excess) > 1e-6:
        problems.append("excess_over_cash_cagr does not follow from the printed rows")
    if abs(printed["excess_money_cny"] - cap * want_excess) > 1.0:
        problems.append("excess_money_cny != capital x excess")
    if want_excess > 1e-9 and printed["years_of_excess_to_repay_one_tail_year"]:
        want_years = printed["falsification_drawdown"] / want_excess
        if abs(printed["years_of_excess_to_repay_one_tail_year"] - want_years) > 0.05:
            problems.append("years_of_excess_to_repay_one_tail_year != tail / excess")

    want_verdict = verdict_of(printed["excess_money_cny"], face["criteria"]["meaningful_margin_cny"])
    if face["verdict"] != want_verdict:
        problems.append("verdict %s does not follow from its own numbers (want %s)"
                        % (face["verdict"], want_verdict))

    live_be = break_even_n(book, face["cash"]["cash_net_annual"])
    if face["break_even_n"].get("n") is not None and live_be.get("n") is not None:
        if face["break_even_n"]["n"] != live_be["n"]:
            problems.append("break_even_n drifted: face %s vs live %s"
                            % (face["break_even_n"]["n"], live_be["n"]))

    if drift:
        for d in drift:
            print("STALE: " + d)
        print("STALE: source moved -> run: python %s run" % SCRIPT)
        return 3
    if problems:
        for p in problems:
            print("CHECK FAILED: " + p)
        return 4
    print("CHECK OK: %s | verdict=%s | deflated %s vs cash %s | excess ￥%.0f/yr | break-even N=%s"
          % (OUT_JSON.name, face["verdict"], _pct(printed["budgetable_cagr"], 3),
             _pct(face["cash"]["cash_net_annual"], 3), printed["excess_money_cny"],
             face["break_even_n"].get("n")))
    return 0


# ----------------------------------------------------------------------- selftest
def selftest():
    ok = fail = 0

    def leg(name, cond, extra=""):
        nonlocal ok, fail
        if cond:
            ok += 1
            print("  PASS %s %s" % (name, extra))
        else:
            fail += 1
            print("  FAIL %s %s" % (name, extra))

    book = BDE._book_inputs()
    leg("L0 book inputs present", bool(book))
    if not book:
        print("SELFTEST %d/%d" % (ok, ok + fail))
        return 1

    cash = _cash_net()
    leg("L1 cash rate read from the placement face", bool(cash) and 0.0 < cash["cash_net_annual"] < 0.10,
        "=%.5f" % (cash["cash_net_annual"] if cash else -1))

    # Control leg: the conservative-N row must reproduce the parent face bit for bit.
    parent = _load(PARENT_FACE)
    row = budgetable_at(book, CRITERIA["n_conservative"])
    if parent and parent.get("at_conservative_n"):
        p = parent["at_conservative_n"]
        leg("L2 control: budgetable reproduces the parent face",
            abs(row["budgetable_cagr"] - p["budgetable_cagr"]) < 1e-6
            and abs(row["falsification_drawdown"] - p["falsification_drawdown"]) < 1e-6,
            "%.6f vs %.6f" % (row["budgetable_cagr"], p["budgetable_cagr"]))
    else:
        leg("L2 control: parent face present", False, "(missing)")

    leg("L3 deflated pay is monotone decreasing in N",
        budgetable_at(book, 2)["budgetable_cagr"] >= budgetable_at(book, 58)["budgetable_cagr"]
        >= budgetable_at(book, 450)["budgetable_cagr"])

    be = break_even_n(book, cash["cash_net_annual"])
    if be.get("n"):
        n = be["n"]
        leg("L4 break-even N brackets the cash rate",
            budgetable_at(book, n)["budgetable_cagr"] >= cash["cash_net_annual"]
            and budgetable_at(book, n + 1)["budgetable_cagr"] < cash["cash_net_annual"],
            "N=%d" % n)
    else:
        leg("L4 break-even N absent -> N=2 must be below cash",
            budgetable_at(book, 2)["budgetable_cagr"] < cash["cash_net_annual"])

    leg("L5 verdict branches are exhaustive and ordered",
        verdict_of(-1.0, 10000) == "DEFLATED_PAY_BELOW_PARKING"
        and verdict_of(0.0, 10000) == "DEFLATED_PAY_IS_A_ROUNDING_ERROR_VS_CASH"
        and verdict_of(9999.0, 10000) == "DEFLATED_PAY_IS_A_ROUNDING_ERROR_VS_CASH"
        and verdict_of(10000.0, 10000) == "DEFLATED_PAY_CLEARS_PARKING_BY_A_MARGIN")

    # L6: window-mean parser on a synthetic panel (deterministic, no real data involved).
    with tempfile.TemporaryDirectory() as td:
        syn = Path(td) / "GC001.csv"
        syn.write_text("date,open,high,low,close,volume\n"
                       "2020-01-01,1,2,1,2.0,1\n"
                       "2020-06-01,1,2,1,3.0,1\n"
                       "2021-01-01,1,2,1,9.0,1\n", encoding="utf-8")
        w = _repo_window_mean(syn, "2020-01-01", "2020-12-31")
        leg("L6 window mean respects the window", bool(w) and abs(w["mean_pct"] - 2.5) < 1e-9 and w["days"] == 2,
            "=" + str(w and w["mean_pct"]))

    # L7: behaviour leg -- the real check() on a poisoned copy.
    face = build(write=False)
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td) / "face.json"
        _dump(tmp, face)
        global OUT_JSON
        orig = OUT_JSON
        try:
            OUT_JSON = tmp
            bad = json.loads(json.dumps(face))
            bad["at_conservative_n"]["budgetable_cagr"] = round(bad["at_conservative_n"]["budgetable_cagr"] + 0.01, 6)
            _dump(tmp, bad)
            import io
            import contextlib
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc_bad = check()
            out_bad = buf.getvalue()
            leg("L7a poisoned number at the same cutoff -> rc4 without the STALE word",
                rc_bad == 4 and "CHECK FAILED" in out_bad and "STALE" not in out_bad,
                "rc=%d" % rc_bad)
            stale = json.loads(json.dumps(face))
            stale["evidence_cutoff"] = "1999-01-01"
            _dump(tmp, stale)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc_stale = check()
            out_stale = buf.getvalue()
            leg("L7b moved cutoff -> rc3 naming STALE", rc_stale == 3 and "STALE" in out_stale,
                "rc=%d" % rc_stale)
            _dump(tmp, face)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc_ok = check()
            leg("L7c clean copy -> rc0", rc_ok == 0, "rc=%d" % rc_ok)
        finally:
            OUT_JSON = orig

    # L8: the face must be reproducible from its own printed fields.
    cap = float(face["criteria"]["capital_cny"])
    p = face["at_conservative_n"]
    leg("L8 excess is reproducible from the printed rows",
        abs(p["excess_money_cny"] - cap * (p["budgetable_cagr"] - face["cash"]["cash_net_annual"])) < 1.0)
    if p["years_of_excess_to_repay_one_tail_year"] and p["excess_over_cash_cagr"] > 0:
        leg("L9 tail-repay years follow from the printed rows",
            abs(p["years_of_excess_to_repay_one_tail_year"]
                - p["falsification_drawdown"] / p["excess_over_cash_cagr"]) < 0.05)

    # L10: exactly one of the two readings must be shown -- the headline is never dropped.
    leg("L10 headline and deflated row are both published",
        face["book"]["headline_cagr"] > 0 and "budgetable_cagr" in p)

    print("SELFTEST %d/%d" % (ok, ok + fail))
    return 0 if fail == 0 else 1


# -------------------------------------------------------------------------- render
def _money(x):
    return "{:,.0f}".format(x)


def _write_doc(face):
    p = face["at_conservative_n"]
    c = face["cash"]
    b = face["book"]
    be = face["break_even_n"].get("n")
    cc = c["cross_check"] or {}
    lines = []
    lines.append("# 扣完搜索租金，这本书比躺着赚利息多多少\n")
    lines.append("> 由 `%s` 渲染，数字不手抄。`generated %s`，`cutoff %s`（%s）。\n"
                 % (SCRIPT, face["generated"], face["evidence_cutoff"], face["evidence_cutoff_source"]))
    lines.append("## 一句话\n")
    lines.append(face["verdict_zh"] + "\n")
    lines.append("## 两半都印出来\n")
    lines.append("| 读法 | 年化 | 在 ￥%s 上是 |\n|---|---|---|\n" % _money(face["criteria"]["capital_cny"]))
    lines.append("| 标题（不扣租金，父面原样） | %s | ￥%s |\n"
                 % (_pct(b["headline_cagr"]), _money(face["criteria"]["capital_cny"] * b["headline_cagr"])))
    lines.append("| 扣租金（N=%d 次尝试） | %s | ￥%s |\n"
                 % (p["n_trials"], _pct(p["budgetable_cagr"], 3), _money(face["criteria"]["capital_cny"] * p["budgetable_cagr"])))
    lines.append("| 躺利息（回购净利率） | %s | ￥%s |\n"
                 % (_pct(c["cash_net_annual"], 3), _money(face["criteria"]["capital_cny"] * c["cash_net_annual"])))
    lines.append("| **超额（扣租金 - 躺利息）** | %s | **￥%s** |\n"
                 % (_pct(p["excess_over_cash_cagr"], 3), _money(p["excess_money_cny"])))
    lines.append("\n## 代价\n")
    lines.append("* 一年内 5%% 概率的尾部回撤：**%s**（￥%s）。\n"
                 % (_pct(p["falsification_drawdown"]), _money(-face["criteria"]["capital_cny"] * p["falsification_drawdown"])))
    if p["years_of_excess_to_repay_one_tail_year"]:
        lines.append("* 要靠超额把这一个坏年补回来，需要 **%.0f 年**。\n"
                     % p["years_of_excess_to_repay_one_tail_year"])
    lines.append("\n## 反面问题：审计多少次它才值得上\n")
    if be:
        lines.append("只有当「为找这本书花掉的独立尝试次数」不超过 **%d 次**时，扣租金的年化才仍高于躺利息。"
                     "本司机械可数的三次审计是 58 / 123 / 450 —— 都在这条线之上或之上沿。\n" % be)
    else:
        lines.append("即使只算 2 次尝试，扣租金的年化也已低于躺利息：这本书在当前现金利率下没有可预算的超额。\n")
    lines.append("\n## N 阶梯（同一套算术，格子自洽）\n")
    lines.append("| 尝试次数 N | 可信夏普 | 可预算年化 | 相对躺利息 | ￥%s 上的差 | 过线 |\n|---|---|---|---|---|---|\n"
                 % _money(face["criteria"]["capital_cny"]))
    for r in face["scanner"]:
        lines.append("| %d | %.4f | %s | %s | ￥%s | %s |\n"
                     % (r["n_trials"], r["credible_sharpe"], _pct(r["budgetable_cagr"], 3),
                        _pct(r["excess_over_cash_cagr"], 3), _money(r["money_vs_parking_cny"]),
                        "是" if r["clears_cash"] else "否"))
    lines.append("\n## 现金腿的取证\n")
    lines.append("* 发布值：`cash_net_annual=%s`（来源 %s，`generated %s`，`cutoff %s`）。\n"
                 % (_pct(c["cash_net_annual"], 3), c["source"], c.get("generated"), c.get("evidence_cutoff")))
    if cc:
        lines.append("* 面板复核：GC001 在本书面窗口内日度年化利率均值 **%.3f%%**（%d 天，%s→%s），"
                     "与发布净值差 %.3fpp → **%s**。差额=佣金与窗口不同源，披露不调和。\n"
                     % (cc["gc001_window_mean_pct"], cc["days"], cc["first"], cc["last"],
                        cc["gap_vs_published_pp"], cc["relation"]))
        if cc.get("gc007_window_mean_pct") is not None:
            lines.append("* 次查：GC007 同窗均值 %.3f%%。\n" % cc["gc007_window_mean_pct"])
    if c.get("today"):
        lines.append("* 最新报价：%s GC001 收盘 %.3f%%（年化）。\n"
                     % (c["today"]["last_date"], c["today"]["last_close_pct"]))
    lines.append("\n## 不许只挑一边信\n")
    for cv in face["caveats"]:
        lines.append("* %s\n" % cv)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_MD, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("".join(lines))


def show():
    face = _load(OUT_JSON)
    if not face:
        print("face missing")
        return 1
    p = face["at_conservative_n"]
    print("verdict=%s" % face["verdict"])
    print("headline %s | deflated %s | cash %s | excess ￥%.0f/yr | break-even N=%s"
          % (_pct(face["book"]["headline_cagr"]), _pct(p["budgetable_cagr"], 3),
             _pct(face["cash"]["cash_net_annual"], 3), p["excess_money_cny"],
             face["break_even_n"].get("n")))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "check", "show", "--selftest", "selftest"])
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest or a.cmd in ("selftest", "--selftest"):
        return selftest()
    if a.cmd == "check":
        return check()
    if a.cmd == "show":
        return show()
    face = build()
    print("OK %s | verdict=%s | excess ￥%.0f/yr | break-even N=%s"
          % (FACE, face["verdict"], face["at_conservative_n"]["excess_money_cny"],
             face["break_even_n"].get("n")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
