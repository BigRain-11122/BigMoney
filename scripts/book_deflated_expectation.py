#!/usr/bin/env python
"""book_deflated_expectation -- what does the book we would fund actually pay?

Why this face exists
--------------------
`scripts/etf_book_search_rent.py` (r1960) measured how many independent tries this book's
Sharpe survives: N* = 5, while the desk has audited counts of 58 / 123 / 450. It ended
with a sentence -- "do not treat 1.10 as a proven edge" -- and no number a treasurer can
act on. A Sharpe is not money. Three questions were still open:

  1. If the Sharpe is inflated by the search that found it, what annual return should be
     budgeted instead of the headline 11.16%?
  2. On a real position size, what is the ordinary bad year (not the worst ever seen)?
  3. What outcome would tell us the edge is gone -- and how long would "just keep running
     it" take to prove the edge instead?

This face answers exactly those three, on the book's own published statistics. It adds no
new estimate of the edge: every input is a number another face already published.

Construction (frozen before the first run)
------------------------------------------
* **Expected inflation under the null.** For each trial count N the shared gate
  (`science_gates.dsr_from_stats`, the stored-stats twin of the raw-returns DSR) gives
  SR*(N), the Sharpe you would *expect to see* if the strategy were pure noise and you had
  taken N independent tries. That is the search rent, in Sharpe units.
* **Credible Sharpe** = published Sharpe - SR*(N), floored at zero. It is a haircut, not a
  posterior: it says "what is left after paying the rent the search charged", never "this
  is the true Sharpe".
* **Budgetable return** = credible Sharpe x the book's published volatility. Cash and
  costs are already inside the published series (the face is net of 10bp/side), so nothing
  is added or subtracted here.
* **Falsification drawdown** = the one-year drawdown that would occur with probability
  `abandon_p` if the credible Sharpe were the truth (first-passage law for a drifted
  Brownian motion). Deeper than that in a year and the truth was not the credible Sharpe.
* **Years to prove by waiting** = (t_req / credible Sharpe)^2. Waiting is not a plan; this
  number is how the face proves that.

Usage:
    python scripts/book_deflated_expectation.py run
    python scripts/book_deflated_expectation.py check
    python scripts/book_deflated_expectation.py --selftest
"""
from __future__ import annotations

import argparse
import json
import math
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

OUT_JSON = ROOT / "results" / "book_deflated_expectation.json"
OUT_MD = ROOT / "research" / "BOOK-DEFLATED-EXPECTATION.md"
SCRIPT = "scripts/book_deflated_expectation.py"
FACE = "results/book_deflated_expectation.json"

SOURCE_BOOK = ROOT / "results" / "etf_book_search_rent.json"
SOURCE_CARRY = ROOT / "results" / "idx_fut_carry_search_rent.json"

# ---------------------------------------------------------------- frozen criteria
CRITERIA = {
    "capital_cny": 1_000_000,
    "n_ladder": [2, 58, 123, 450],
    "n_ladder_definitions": {
        "2": "the floor of the null-max formula (a single bet is not expressible in it)",
        "58": "queue rows marked done in state/queue/{tech,explore}.md",
        "123": "batches a gate killed (results/gate_attrition.bm-c.json)",
        "450": "research/**/*PREREG*.md written by this desk",
    },
    "n_conservative": 58,
    "t_req": 3.0,
    "abandon_p": 0.05,
    "dsr_line": 0.95,
    "periods_per_year": 252,
    "haircut": "SR*(N) from science_gates.dsr_from_stats at the book's own sigma_sr; "
               "credible = max(0, published - SR*(N))",
    "budgetable_return": "credible_sharpe * published volatility (the series is already net of cost)",
    "falsification_drawdown": "one-year first-passage drawdown at probability abandon_p",
    "sources": {
        "book": "results/etf_book_search_rent.json",
        "carry": "results/idx_fut_carry_search_rent.json (frontier cross-check only)",
    },
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


def _z95():
    return 1.6448536269514722


# ------------------------------------------------------------------ the arithmetic
def _sr_star_ann(sr_ann, sigma_sr_daily, n, ppy=252):
    """Expected max Sharpe under the null, annualised, from the shared stored-stats gate."""
    import science_gates as SG

    d = SG.dsr_from_stats(sr_ann, sigma_sr_daily, n)
    return d["sr_star"] * math.sqrt(ppy), d["dsr"]


def _haircut_row(sr_ann, vol_ann, sigma_sr_daily, n, capital, t_req, abandon_p, ppy=252):
    sr_star_ann, dsr = _sr_star_ann(sr_ann, sigma_sr_daily, n, ppy)
    # Everything downstream is computed from the PRINTED credible Sharpe so a reader can
    # reproduce every cell from the table without knowing our rounding path.
    credible = round(max(0.0, sr_ann - sr_star_ann), 4)
    budgetable = credible * vol_ann
    years = (t_req / credible) ** 2 if credible > 0 else None
    dd = _falsification_drawdown(credible * vol_ann, vol_ann, abandon_p)
    return {
        "n_trials": int(n),
        "sr_star_ann": round(sr_star_ann, 4),
        "credible_sharpe": credible,
        "dsr": round(dsr, 6),
        "budgetable_cagr": round(budgetable, 6),
        "money_on_capital": round(capital * budgetable, 2),
        "p_edge_is_noise": round(1.0 - dsr, 4),
        "years_to_t_req": (round(years, 2) if years is not None else None),
        "falsification_drawdown": round(dd, 6),
        "money_at_that_drawdown": round(-capital * dd, 2),
    }


def _falsification_drawdown(mu, sigma, p, t=1.0):
    """One-year drawdown D with P(min over t < -D) = p for a drifted Brownian motion.

    Reflection-principle first passage:
        P = Phi((-D - mu t)/(sigma sqrt t))
            + exp(-2 mu D / sigma^2) * Phi((-D + mu t)/(sigma sqrt t))
    """
    if sigma <= 0:
        return 0.0

    def hit(d):
        a = _norm_cdf((-d - mu * t) / (sigma * math.sqrt(t)))
        b = math.exp(min(0.0, -2.0 * mu * d / (sigma * sigma))) * _norm_cdf(
            (-d + mu * t) / (sigma * math.sqrt(t)))
        return a + b

    lo, hi = 0.0, 10.0 * sigma * math.sqrt(t) + 4.0 * abs(mu) * t
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if hit(mid) > p:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def _norm_cdf(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


# ------------------------------------------------------------------------ inputs
def _book_inputs():
    d = _load(SOURCE_BOOK)
    if not d:
        return None
    cents = (d.get("book") or {}).get("cents") or {}
    curve = d.get("dsr_curve") or []
    sigmas = sorted({round(float(r["sigma_sr"]), 9) for r in curve if "sigma_sr" in r})
    if len(sigmas) != 1:
        raise RuntimeError("sigma_sr is not constant across the published grid: %s" % sigmas)
    return {
        "sr_ann": float(cents["sharpe"]),
        "vol_ann": float(cents["vol"]),
        "cagr": float(cents["cagr"]),
        "maxdd": float(cents["maxdd"]),
        "bars": int((d.get("book") or {}).get("bars") or 0),
        "start": (d.get("book") or {}).get("start"),
        "end": (d.get("book") or {}).get("end"),
        "skew": (d.get("book") or {}).get("skew"),
        "arm": (d.get("book") or {}).get("arm"),
        "sigma_sr_daily": sigmas[0],
        "published_curve": curve,
        "evidence_cutoff": d.get("evidence_cutoff"),
    }


def _carry_frontier():
    d = _load(SOURCE_CARRY)
    if not d:
        return None
    out = []
    for key, cell in sorted((d.get("cells") or {}).items()):
        out.append({
            "cell": key,
            "sharpe_ann": cell.get("sharpe_ann"),
            "n_star": cell.get("n_star"),
            "sharpe_needed_at_audited_n": cell.get("sharpe_needed_at_audited_n"),
            "gap_at_audited_n": cell.get("gap_at_audited_n"),
            "verdict": cell.get("verdict"),
        })
    return {
        "audited_n_used": d.get("audited_n_used"),
        "audited_counts": d.get("audit_counts"),
        "cells": out,
        "evidence_cutoff": d.get("evidence_cutoff"),
    }


def _verdict(rows, n_conservative, line):
    row = next((r for r in rows if r["n_trials"] == int(n_conservative)), None)
    if row is None:
        return "LADDER_MISSING_CONSERVATIVE_N"
    if row["budgetable_cagr"] <= 0:
        return "SEARCH_RENT_EATS_THE_BOOK"
    if row["dsr"] < line:
        return "PAYS_BUT_UNPROVEN"
    return "PAYS_AFTER_RENT"


# -------------------------------------------------------------------------- build
def build(write=True):
    book = _book_inputs()
    if not book:
        raise RuntimeError("source face missing: %s" % SOURCE_BOOK)
    carry = _carry_frontier()

    rows = []
    for n in CRITERIA["n_ladder"]:
        rows.append(_haircut_row(
            book["sr_ann"], book["vol_ann"], book["sigma_sr_daily"], n,
            CRITERIA["capital_cny"], CRITERIA["t_req"], CRITERIA["abandon_p"],
            CRITERIA["periods_per_year"]))

    verdict = _verdict(rows, CRITERIA["n_conservative"], CRITERIA["dsr_line"])
    head = next(r for r in rows if r["n_trials"] == int(CRITERIA["n_conservative"]))

    face = {
        "script": SCRIPT,
        "face": FACE,
        "kind": "deflated-expectation/v1",
        "generated": _now(),
        "evidence_cutoff": book["evidence_cutoff"],
        "criteria": CRITERIA,
        "book": {
            "arm": book["arm"],
            "bars": book["bars"],
            "window": [book["start"], book["end"]],
            "headline": {
                "cagr": book["cagr"],
                "sharpe": book["sr_ann"],
                "vol": book["vol_ann"],
                "maxdd": book["maxdd"],
                "skew": book["skew"],
            },
            "sigma_sr_daily": book["sigma_sr_daily"],
            "source": "results/etf_book_search_rent.json",
        },
        "rows": rows,
        "at_conservative_n": head,
        "verdict": verdict,
        "verdict_zh": _verdict_zh(verdict, head, book, CRITERIA["capital_cny"]),
        "carry_frontier": carry,
        "caveats": [
            "credible_sharpe is a haircut, not an estimate of the truth: it subtracts the "
            "Sharpe a pure-noise strategy would be expected to show after N tries.",
            "N is not derivable from the repo; the ladder prints three mechanical counts and "
            "the verdict is taken at the smallest of them (58), so the reading errs high.",
            "the falsification drawdown assumes a stable vol; a regime change moves it.",
            "the carry family is printed for comparison only -- its face does not publish "
            "sigma_sr per grid point, so no haircut is computed for it here.",
        ],
    }

    if write:
        _dump(OUT_JSON, face)
        _write_doc(face)
    return face


def _verdict_zh(verdict, row, book, capital):
    if verdict == "SEARCH_RENT_EATS_THE_BOOK":
        return ("按本司自己的记账（N=%d 次尝试）扣掉搜索租金后，这本书可预算的年化是 %.2f%%，"
                "不是标题的 %.2f%%——等于不付钱。" % (
                    row["n_trials"], 100 * row["budgetable_cagr"], 100 * book["cagr"]))
    if verdict == "PAYS_BUT_UNPROVEN":
        return ("扣掉 N=%d 的搜索租金后仍值 %.2f%%/年，但 DSR=%.3f 未过 %.2f 线："
                "可以小额跑，不能按已证边满仓。" % (
                    row["n_trials"], 100 * row["budgetable_cagr"], row["dsr"],
                    CRITERIA["dsr_line"]))
    return ("扣掉 N=%d 的搜索租金后仍值 %.2f%%/年且 DSR=%.3f 过线。" % (
        row["n_trials"], 100 * row["budgetable_cagr"], row["dsr"]))


# ---------------------------------------------------------------------- rendering
def _pct(x, nd=2):
    return "n/a" if x is None else "%.*f%%" % (nd, 100.0 * x)


def _render(face):
    b = face["book"]
    h = b["headline"]
    lines = []
    lines.append("Book: `%s` -- %d bars, %s -> %s, published CAGR %s / Sharpe %.3f / vol %s / maxDD %s."
                 % (b["arm"], b["bars"], b["window"][0], b["window"][1],
                    _pct(h["cagr"]), h["sharpe"], _pct(h["vol"]), _pct(h["maxdd"])))
    lines.append("")
    lines.append("| tries (N) | what N counts | SR* under the null | credible Sharpe | budgetable CAGR | on %s | P(edge is noise) | falsification drawdown in 1y | years to prove by waiting |"
                 % _money(face["criteria"]["capital_cny"]))
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for r in face["rows"]:
        lines.append("| %d | %s | %.3f | %.3f | %s | %s | %s | %s | %s |" % (
            r["n_trials"],
            face["criteria"]["n_ladder_definitions"].get(str(r["n_trials"]), ""),
            r["sr_star_ann"], r["credible_sharpe"], _pct(r["budgetable_cagr"]),
            _money(r["money_on_capital"]), _pct(r["p_edge_is_noise"], 1),
            _pct(r["falsification_drawdown"]),
            ("%.1f" % r["years_to_t_req"]) if r["years_to_t_req"] is not None else "never"))
    lines.append("")
    row = face["at_conservative_n"]
    lines.append("**Verdict at N=%d (the smallest audited count): %s.** %s"
                 % (row["n_trials"], face["verdict"], face["verdict_zh"]))
    lines.append("")
    lines.append("Reading the three questions:")
    lines.append("")
    lines.append("1. **What to budget.** %s per year, not %s. The difference is the search rent: "
                 "at N=%d a pure-noise strategy would be expected to show Sharpe %.3f."
                 % (_pct(row["budgetable_cagr"]), _pct(h["cagr"]), row["n_trials"], row["sr_star_ann"]))
    lines.append("2. **What an ordinary bad year looks like.** If the credible Sharpe is the truth, "
                 "a one-year drawdown of %s happens with %.0f%% probability, i.e. %s on %s. "
                 "The published maxDD of %s was the worst in 6.9 years, not the ordinary tail."
                 % (_pct(row["falsification_drawdown"]), 100 * face["criteria"]["abandon_p"],
                    _money(row["money_at_that_drawdown"]), _money(face["criteria"]["capital_cny"]),
                    _pct(h["maxdd"])))
    lines.append("3. **What would falsify it, and why waiting is not a plan.** Deeper than %s in a "
                 "year and the credible Sharpe was not the truth -- that is the abandon line. "
                 "The line is relative to the edge you believe: believing a bigger edge makes a small "
                 "decline surprising, believing only what survived the rent buys a loose stop. "
                 "Waiting for t=%.1f would take %s years at the credible Sharpe, which is why the "
                 "answer has to be a position size, not more patience."
                 % (_pct(row["falsification_drawdown"]), face["criteria"]["t_req"],
                    ("%.1f" % row["years_to_t_req"]) if row["years_to_t_req"] is not None else "unbounded"))
    carry = face.get("carry_frontier")
    if carry:
        lines.append("")
        lines.append("Frontier cross-check -- the carry family as its own face published it "
                     "(no haircut computed here; that face does not publish `sigma_sr` per grid point):")
        lines.append("")
        lines.append("| cell | Sharpe | tries it survives (N*) | Sharpe needed at audited N=%s | gap | verdict |"
                     % carry.get("audited_n_used"))
        lines.append("|---|---|---|---|---|---|")
        for c in carry["cells"]:
            lines.append("| %s | %.3f | %s | %s | %s | %s |" % (
                c["cell"], c["sharpe_ann"], c["n_star"],
                ("%.3f" % c["sharpe_needed_at_audited_n"]) if c["sharpe_needed_at_audited_n"] is not None else "n/a",
                ("%.3f" % c["gap_at_audited_n"]) if c["gap_at_audited_n"] is not None else "n/a",
                c["verdict"]))
    lines.append("")
    lines.append("Caveats, printed so they cannot be read past:")
    lines.append("")
    for c in face["caveats"]:
        lines.append("- " + c)
    return "\n".join(lines)


def _money(x):
    if x is None:
        return "n/a"
    sign = "-" if x < 0 else ""
    return "%s¥%s" % (sign, format(abs(round(x)), ","))


def _write_doc(face):
    body = _render(face)
    head = (
        "# What this book pays after the search rent\n\n"
        "Generated by `%s` -- do not edit the block below by hand; `check` compares it\n"
        "byte-for-byte with what the face would render today.\n\n"
        "<!-- BEGIN GENERATED -->\n" % SCRIPT
    )
    tail = "\n<!-- END GENERATED -->\n"
    Path(OUT_MD).parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_MD, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(head + body + tail)


def _doc_block(text):
    a = text.find("<!-- BEGIN GENERATED -->")
    b = text.find("<!-- END GENERATED -->")
    if a < 0 or b < 0:
        return None
    return text[a + len("<!-- BEGIN GENERATED -->"):b]


# -------------------------------------------------------------------------- check
def check():
    """Anchored to what moves: the parent faces' cutoff and their published numbers."""
    face = _load(OUT_JSON)
    if not face:
        print("STALE face missing: %s" % FACE)
        return 3
    if (face.get("criteria") or {}) != CRITERIA:
        print("CHECK FAILED criteria differ from the frozen constants (face is not this code)")
        return 4
    book = _book_inputs()
    if not book:
        print("STALE source face missing: results/etf_book_search_rent.json")
        return 3
    if face.get("evidence_cutoff") != book["evidence_cutoff"]:
        print("STALE source advanced: face cutoff %s, source now %s"
              % (face.get("evidence_cutoff"), book["evidence_cutoff"]))
        return 3
    fresh = build(write=False)
    bad = []
    for key in ("verdict", "at_conservative_n", "rows"):
        if (face.get(key) or None) != (fresh.get(key) or None):
            bad.append(key)
    if (face.get("carry_frontier") or None) != (fresh.get("carry_frontier") or None):
        bad.append("carry_frontier")
    if bad:
        print("CHECK FAILED same inputs, different numbers: %s (not a freshness issue)"
              % ", ".join(bad))
        return 4
    md = (ROOT / "research" / "BOOK-DEFLATED-EXPECTATION.md")
    if not md.exists():
        print("STALE doc missing: research/BOOK-DEFLATED-EXPECTATION.md")
        return 3
    block = _doc_block(md.read_text(encoding="utf-8"))
    if block is None or block.strip() != _render(face).strip():
        print("CHECK FAILED doc block differs from what the face renders today")
        return 4
    print("CHECK OK -- %s at N=%d, rows=%d, carry cells=%d"
          % (face["verdict"], face["at_conservative_n"]["n_trials"], len(face["rows"]),
             len((face.get("carry_frontier") or {}).get("cells") or [])))
    return 0


# ----------------------------------------------------------------------- selftest
def selftest():
    legs = []

    def leg(name, ok):
        legs.append((name, bool(ok)))

    book = _book_inputs()
    leg("L1 source face present", book is not None)

    # L2 control: this face must quote the parent's published numbers, not recompute them.
    d_src = _load(SOURCE_BOOK)
    c = (d_src.get("book") or {}).get("cents") or {}
    leg("L2 control parent headline", abs(float(c["sharpe"]) - book["sr_ann"]) < 1e-12
        and abs(float(c["vol"]) - book["vol_ann"]) < 1e-12)

    # L3 the stored-stats twin reproduces the published curve (single source of the formula)
    worst = 0.0
    for r in book["published_curve"]:
        _, dsr = _sr_star_ann(book["sr_ann"], r["sigma_sr"], r["n_trials"])
        worst = max(worst, abs(dsr - float(r["dsr"])))
    leg("L3 curve reproduced (worst |dDSR|=%.5f)" % worst, worst < 5e-4)

    face = build(write=False)
    rows = face["rows"]
    leg("L4 ladder covers the conservative N", any(r["n_trials"] == CRITERIA["n_conservative"] for r in rows))
    leg("L5 credible Sharpe never rises with N",
        all(rows[i]["credible_sharpe"] >= rows[i + 1]["credible_sharpe"] for i in range(len(rows) - 1)))
    leg("L6 P(edge is noise) never falls with N",
        all(rows[i]["p_edge_is_noise"] <= rows[i + 1]["p_edge_is_noise"] for i in range(len(rows) - 1)))
    # tolerance = the storage precision of budgetable_cagr itself (6dp), not a fudge factor
    leg("L7 budgetable return is credible Sharpe x vol",
        all(abs(r["budgetable_cagr"] - r["credible_sharpe"] * book["vol_ann"]) <= 1e-6 for r in rows))

    # L8 waiting-time inverse
    r = rows[-1]
    ok = True
    if r["years_to_t_req"] is not None and r["credible_sharpe"] > 0:
        ok = abs(r["credible_sharpe"] * math.sqrt(r["years_to_t_req"]) - CRITERIA["t_req"]) < 0.02
    leg("L8 years-to-prove inverts the t-stat", ok)

    # L9 exact first-passage case: zero drift -> D = 1.96 sigma for p=0.05
    dd0 = _falsification_drawdown(0.0, 0.20, 0.05)
    leg("L9 zero-drift falsification drawdown = 1.96 sigma (%.4f)" % dd0, abs(dd0 - 1.959964 * 0.20) < 5e-3)

    # L10 the 5% drawdown gets SHALLOWER as the believed edge gets stronger: believing more
    # means a smaller decline is already a 5%-tail event. (First draft asserted the reverse
    # and this leg caught it.)
    weak = _falsification_drawdown(0.02, 0.10, 0.05)
    strong = _falsification_drawdown(0.12, 0.10, 0.05)
    leg("L10 falsification drawdown shallows as the edge strengthens (%.3f -> %.3f)" % (weak, strong),
        strong < weak)

    # L11 verdict branches are all reachable and driven by the printed rows
    fake = [dict(rows[0], n_trials=CRITERIA["n_conservative"], budgetable_cagr=0.0, dsr=0.99)]
    leg("L11a verdict EATS when nothing is left",
        _verdict(fake, CRITERIA["n_conservative"], CRITERIA["dsr_line"]) == "SEARCH_RENT_EATS_THE_BOOK")
    fake2 = [dict(fake[0], budgetable_cagr=0.03, dsr=0.50)]
    leg("L11b verdict unproven below the DSR line",
        _verdict(fake2, CRITERIA["n_conservative"], CRITERIA["dsr_line"]) == "PAYS_BUT_UNPROVEN")
    fake3 = [dict(fake[0], budgetable_cagr=0.03, dsr=0.96)]
    leg("L11c verdict pays above the line",
        _verdict(fake3, CRITERIA["n_conservative"], CRITERIA["dsr_line"]) == "PAYS_AFTER_RENT")

    # L12/L13 behaviour legs: drive the real check() on a poisoned copy of the face
    global OUT_JSON
    saved = OUT_JSON
    tmpdir = Path(tempfile.mkdtemp(prefix="bde_selftest_"))
    try:
        _dump(OUT_JSON, face)
        print("  (selftest writes the real face first so check() has something to read)")
        OUT_JSON = tmpdir / "face.json"

        poisoned = json.loads(json.dumps(face))
        poisoned["at_conservative_n"]["budgetable_cagr"] = 0.99
        _dump(OUT_JSON, poisoned)
        import io as _io
        from contextlib import redirect_stdout
        buf = _io.StringIO()
        with redirect_stdout(buf):
            rc = check()
        txt = buf.getvalue()
        leg("L12 same-cutoff wrong number -> rc4 without the STALE word",
            rc == 4 and "CHECK FAILED" in txt and "STALE" not in txt)

        moved = json.loads(json.dumps(face))
        moved["evidence_cutoff"] = "1999-01-01"
        _dump(OUT_JSON, moved)
        buf = _io.StringIO()
        with redirect_stdout(buf):
            rc = check()
        txt = buf.getvalue()
        leg("L13 moved cutoff -> rc3 naming STALE", rc == 3 and "STALE" in txt)
    finally:
        OUT_JSON = saved
        shutil.rmtree(tmpdir, ignore_errors=True)

    passed = sum(1 for _, ok in legs if ok)
    for name, ok in legs:
        print("%s %s" % ("PASS" if ok else "FAIL", name))
    print("selftest %d/%d" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


def show():
    face = _load(OUT_JSON)
    if not face:
        print("no face yet: run `run` first")
        return 1
    print(_render(face))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", nargs="?", default="run",
                    choices=["run", "check", "show", "--selftest"])
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest or args.cmd == "--selftest":
        return selftest()
    if args.cmd == "check":
        return check()
    if args.cmd == "show":
        return show()
    face = build(write=True)
    print("%s at N=%d: budgetable %s/yr on %s -- %s"
          % (face["verdict"], face["at_conservative_n"]["n_trials"],
             _pct(face["at_conservative_n"]["budgetable_cagr"]),
             _money(face["criteria"]["capital_cny"]), face["face"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
