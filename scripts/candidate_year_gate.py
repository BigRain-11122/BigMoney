#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""does a candidate survive its own calendar, or is it two years wearing a headline?

WHY THIS FILE EXISTS
--------------------
r1414 adopted the 20-name small-cap book on four gates that all looked at one
number per width: x1 CAGR, phase spread, x3 CAGR, one-day capacity.  All four
passed.  Then its own by_year block printed +41.9/+35.7/+3.5/-7.6/+48.9/+75.9/
-18.7 -- i.e. the headline is carried by 2024+2025 and the book is losing money
in the current (partial) year.  Nothing in the machinery asked that question,
so a reader could quote 25.38%/yr as if it were a rate.

r1411 hit the mirror image: its gate rejected an equal-weight book on phase
spread 4.74pp while r1414's gate accepted a 17.20pp spread because the floor
never fell below zero.  Two frozen rules, legally opposite.  The fix is not to
pick a winner after seeing the numbers: it is to freeze a second stage that
looks at the calendar axis, emit BOTH verdicts side by side, and let the
conflict be a field rather than a choice.

This file is that second stage.  It does no new pricing: it re-reads published
candidate receipts (results/*/*.json) and re-issues a verdict on the year axis
plus the capacity floor already frozen in r1414.

VERDICT RULE (frozen before the numbers were read; re-emitted in the receipt)
-----------------------------------------------------------------------------
For one (candidate, width) with annual net returns y[year] in percent:
  Y1 positive years                     >= 70% of years            (>= 5/7 here)
  Y2 median annual net                  >  0
  Y3 worst annual net                   >= -15.0 pp
  Y4 top-2 years' share of the annual sum <= 70%      (only when sum > 0)
  C1 one-day 5%-participation capacity  >= 20,000,000 CNY  (frozen in r1414)

  capacity < C1                      -> CAPACITY_LIMITED
  Y1..Y4 all pass                    -> ADMIT
  exactly three of Y1..Y4 pass       -> CONDITIONAL
  two or fewer                       -> REFUSE

Y3 and Y4 use raw calendar-year returns, including a partial year, because a
loss booked in the current year is a loss.  The same numbers restricted to full
years are printed beside them (worst_year_full_only, top2_share_full_only) so a
reader can see how much of the verdict the partial year is carrying; the gate
itself never switches to the friendlier of the two.

The partial year is also annualised for disclosure only (net_pct x 12/cohorts,
cohorts >= 2) and never fed to a gate.

self  python scripts/candidate_year_gate.py selftest   # synthetic, seconds
run   python scripts/candidate_year_gate.py run        # re-reads receipts
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
OUT_DIR = os.path.join(ROOT, "results", "admission")
OUT = os.path.join(OUT_DIR, "CANDIDATES.json")

CANDIDATE_FACES = [
    ("smallcap_book", "results/smallcap_book/astock_smallcap_book.json"),
    ("breadth_book", "results/breadth_book/astock_breadth_book.json"),
]

CAPACITY_FLOOR_CNY = 20_000_000.0
POSITIVE_YEARS_SHARE = 0.70
WORST_YEAR_FLOOR_PP = -15.0
TOP2_SHARE_MAX = 0.70
# r1411's frozen phase-spread rule, carried verbatim so the two gates can be
# printed against each other instead of silently competing.
R1411_PHASE_SPREAD_MAX_PP = 4.74


def _year_rows(years: dict) -> list[dict]:
    """[{year, net_pct, cohorts, partial}] sorted by year, partial = cohorts < 4."""
    rows = []
    for y, blk in years.items():
        n = blk.get("net_pct")
        c = blk.get("cohorts")
        if n is None or c is None:
            continue
        rows.append({"year": str(y), "net_pct": float(n), "cohorts": int(c),
                     "partial": int(c) < 4})
    rows.sort(key=lambda r: r["year"])
    return rows


def year_metrics(rows: list[dict]) -> dict:
    if not rows:
        return {"years": 0, "positive_years": 0, "median": None, "worst": None,
                "best": None, "annual_sum": None, "top2_share": None,
                "worst_full_only": None, "top2_share_full_only": None}
    vals = [r["net_pct"] for r in rows]
    s = sorted(vals)
    n = len(s)
    median = s[n // 2] if n % 2 else 0.5 * (s[n // 2 - 1] + s[n // 2])
    total = sum(vals)
    top2 = sum(sorted(vals, reverse=True)[:2])
    full = [r["net_pct"] for r in rows if not r["partial"]]
    full_total = sum(full)
    return {
        "years": n,
        "positive_years": sum(1 for v in vals if v > 0),
        "median": round(median, 4),
        "worst": round(min(vals), 4),
        "best": round(max(vals), 4),
        "annual_sum": round(total, 4),
        "top2_share": round(top2 / total, 4) if total > 0 else None,
        "worst_full_only": round(min(full), 4) if full else None,
        "top2_share_full_only": (round(sum(sorted(full, reverse=True)[:2]) / full_total, 4)
                                 if full and full_total > 0 else None),
    }


def year_checks(rows: list[dict], capacity_cny: float | None) -> dict:
    m = year_metrics(rows)
    checks = {
        "Y1_positive_years_share": (m["years"] > 0
                                    and m["positive_years"] / m["years"] >= POSITIVE_YEARS_SHARE),
        "Y2_median_positive": m["median"] is not None and m["median"] > 0,
        "Y3_worst_year": m["worst"] is not None and m["worst"] >= WORST_YEAR_FLOOR_PP,
        "Y4_top2_share": m["top2_share"] is not None and m["top2_share"] <= TOP2_SHARE_MAX,
        # None = this receipt publishes no capacity face; that is not a pass
        # and not a fail, it is an unchecked column (see capacity_checked)
        "C1_capacity": (None if capacity_cny is None
                        else capacity_cny >= CAPACITY_FLOOR_CNY),
    }
    return {"metrics": m, "checks": checks}


def verdict(y: dict) -> str:
    c = y["checks"]
    if c["C1_capacity"] is False:
        return "CAPACITY_LIMITED"
    year_pass = sum(1 for k in ("Y1_positive_years_share", "Y2_median_positive",
                                "Y3_worst_year", "Y4_top2_share") if c[k])
    if year_pass == 4:
        return "ADMIT"
    if year_pass == 3:
        return "CONDITIONAL"
    return "REFUSE"


def admission_block(years: dict, capacity_cny: float | None, phase_spread_pp: float | None,
                    cagr: float | None) -> dict:
    rows = _year_rows(years)
    y = year_checks(rows, capacity_cny)
    v = verdict(y)
    partial = [r for r in rows if r["partial"]]
    conflict = None
    if phase_spread_pp is not None:
        conflict = {
            "r1411_phase_spread_max_pp": R1411_PHASE_SPREAD_MAX_PP,
            "this_candidate_phase_spread_pp": round(phase_spread_pp, 4),
            "passes_this_year_gate": v in ("ADMIT", "CONDITIONAL"),
            "passes_r1411_phase_rule": phase_spread_pp <= R1411_PHASE_SPREAD_MAX_PP,
            "note": "two frozen rules; both verdicts are reported, neither is retired",
        }
        conflict["rules_disagree"] = (
            conflict["passes_this_year_gate"] != conflict["passes_r1411_phase_rule"])
    return {
        "verdict": v,
        "capacity_checked": capacity_cny is not None,
        "cagr_pct": None if cagr is None else round(cagr * 100, 4),
        "capacity_cny_1day_5pct": None if capacity_cny is None else round(capacity_cny, 0),
        "year_metrics": y["metrics"],
        "checks": y["checks"],
        "years": rows,
        "partial_years": [
            {"year": r["year"], "net_pct": r["net_pct"], "cohorts": r["cohorts"],
             # a cohort is 60 bars ~= 2.9 months; the month count is printed so
             # nobody annualises two cohorts into a triple-digit number
             "approx_months_of_evidence": round(r["cohorts"] * 60.0 / 21.0, 1)}
            for r in partial],
        "gate_conflict": conflict,
    }


def _load(path: str) -> dict:
    with io.open(os.path.join(ROOT, path), encoding="utf-8") as f:
        return json.load(f)


def _sha16(path: str) -> str:
    h = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def _candidate_arms(d: dict) -> tuple[str, list[dict]]:
    """normalise the two published receipt schemas into one arm list.

    smallcap_book: by_year[arm] = {net_pct (percent), cohorts}, capacity_cny_5pct_1day[arm],
                   phases.summary[arm].spread, chained_x1[arm].cagr
    breadth_book:  per_year[year] = {ALL_net (fraction), cohorts}, arms.ALL.cagr, no capacity
    """
    by_year = d.get("by_year")
    if isinstance(by_year, dict):
        cap = d.get("capacity_cny_5pct_1day") or {}
        phases = d.get("phases") or {}
        ph = (phases.get("summary") if isinstance(phases, dict) else None) or {}
        chained = d.get("chained_x1") or {}
        arms = [{"arm": a, "years": by_year[a], "capacity": cap.get(a),
                 "spread": (ph.get(a) or {}).get("spread"),
                 "cagr": (chained.get(a) or {}).get("cagr")}
                for a in by_year if a in cap]
        return "by_year_percent", arms

    per_year = d.get("per_year")
    if isinstance(per_year, dict):
        years = {}
        for y, v in per_year.items():
            if isinstance(v, dict) and isinstance(v.get("ALL_net"), (int, float)):
                years[y] = {"net_pct": float(v["ALL_net"]) * 100.0,
                            "cohorts": int(v.get("cohorts") or 0)}
        allarm = (d.get("arms") or {}).get("ALL") or {}
        return "per_year_fraction", [{"arm": "ALL", "years": years, "capacity": None,
                                      "spread": None, "cagr": allarm.get("cagr")}]
    return "unrecognised", []


def run() -> dict:
    t0 = time.time()
    out = {"face": "candidate_year_gate", "asof": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
           "rule": {"positive_years_share": POSITIVE_YEARS_SHARE,
                    "worst_year_floor_pp": WORST_YEAR_FLOOR_PP,
                    "top2_share_max": TOP2_SHARE_MAX,
                    "capacity_floor_cny": CAPACITY_FLOOR_CNY,
                    "r1411_phase_spread_max_pp": R1411_PHASE_SPREAD_MAX_PP},
           "sources": {}, "candidates": [], "pool_ready": [], "honest": []}

    for face_name, rel in CANDIDATE_FACES:
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p):
            out["sources"][face_name] = {"path": rel, "status": "absent"}
            continue
        d = _load(rel)
        schema, arms = _candidate_arms(d)
        vb = d.get("verdict_block") or {}
        published = vb.get("verdict") or d.get("verdict")
        width = vb.get("candidate_width")
        for a in arms:
            blk = admission_block(a["years"], a["capacity"], a["spread"], a["cagr"])
            blk.update({"candidate": face_name, "arm": a["arm"],
                        "published_verdict": published,
                        "published_candidate_width": width})
            out["candidates"].append(blk)
        out["sources"][face_name] = {
            "path": rel, "status": "read", "schema": schema, "sha16": _sha16(rel),
            "evidence_cutoff": d.get("evidence_cutoff"),
            "arms_priced": [a["arm"] for a in arms],
            "published_verdict": published, "published_candidate_width": width,
        }

    out["pool_ready"] = [{"candidate": c["candidate"], "arm": c["arm"],
                          "cagr_pct": c["cagr_pct"],
                          "capacity_cny_1day_5pct": c["capacity_cny_1day_5pct"]}
                         for c in out["candidates"] if c["verdict"] == "ADMIT"]

    flips = []
    for c in out["candidates"]:
        if c["published_verdict"] == "ADOPT_AS_CANDIDATE" and c["verdict"] != "ADMIT":
            flips.append({"candidate": c["candidate"], "arm": c["arm"],
                          "published": c["published_verdict"], "year_gate": c["verdict"],
                          "failed_checks": [k for k, ok in c["checks"].items() if ok is False]})
    out["published_vs_year_gate"] = flips
    out["honest"] = [
        "annual returns are per-cohort sums inside a calendar year, not a compounded series",
        "a partial year is a real loss and stays in Y3/Y4; the full-year-only twins are printed beside it",
        "capacity is one-day entry at 5% of trailing turnover (r1414), not an exit number",
        "C1 null means the receipt publishes no capacity face: printed as unchecked, never as a pass",
        "no new pricing happens here: this file only re-reads published receipts",
    ]
    out["elapsed_sec"] = round(time.time() - t0, 1)
    os.makedirs(OUT_DIR, exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1, sort_keys=False)
        f.write("\n")
    return out


def _chk(ok: bool, msg: str, errs: list) -> None:
    if not ok:
        errs.append(msg)


def selftest() -> int:
    errs: list = []
    ok = tot = 0

    def chk(cond, msg):
        nonlocal ok, tot
        tot += 1
        if cond:
            ok += 1
        else:
            errs.append(msg)

    # L1 a clean seven-year book with real capacity is admitted
    good = {"2020": {"net_pct": 30.0, "cohorts": 4}, "2021": {"net_pct": 20.0, "cohorts": 4},
            "2022": {"net_pct": 12.0, "cohorts": 4}, "2023": {"net_pct": 6.0, "cohorts": 4},
            "2024": {"net_pct": 25.0, "cohorts": 4}, "2025": {"net_pct": 18.0, "cohorts": 4},
            "2026": {"net_pct": 9.0, "cohorts": 4}}
    b = admission_block(good, 5e7, 5.0, 0.15)
    chk(b["verdict"] == "ADMIT", "L1 clean book admitted (%s)" % b["verdict"])

    # L2 r1414's actual shape: headline carried by two years, current year red
    two_year = {"2020": {"net_pct": 41.862, "cohorts": 4}, "2021": {"net_pct": 35.722, "cohorts": 4},
                "2022": {"net_pct": 3.501, "cohorts": 4}, "2023": {"net_pct": -7.608, "cohorts": 4},
                "2024": {"net_pct": 48.927, "cohorts": 4}, "2025": {"net_pct": 75.939, "cohorts": 4},
                "2026": {"net_pct": -18.709, "cohorts": 2}}
    b2 = admission_block(two_year, 4.83e7, 17.2, 0.2538)
    chk(b2["verdict"] == "CONDITIONAL", "L2 two-year headline is conditional (%s)" % b2["verdict"])
    chk(b2["checks"]["Y3_worst_year"] is False, "L3 a -18.7%% year trips Y3")
    # the real 20-name book sits at 69.5% top-two share: it clears Y4 by 0.5pp.
    # That is a disclosed reading, not a reason to move the 70% line.
    chk(b2["year_metrics"]["top2_share"] == 0.6951,
        "L4 top-two share is 69.5%%, just inside the 70%% line")
    carried = {"2020": {"net_pct": 90.0, "cohorts": 4}, "2021": {"net_pct": 95.0, "cohorts": 4},
               "2022": {"net_pct": 2.0, "cohorts": 4}, "2023": {"net_pct": 2.0, "cohorts": 4},
               "2024": {"net_pct": 2.0, "cohorts": 4}, "2025": {"net_pct": 2.0, "cohorts": 4},
               "2026": {"net_pct": 2.0, "cohorts": 4}}
    chk(admission_block(carried, 5e7, 1.0, 0.3)["checks"]["Y4_top2_share"] is False,
        "L4b a genuinely two-year book trips Y4")
    chk(b2["checks"]["Y1_positive_years_share"] is True, "L5 five of seven positive still holds")
    chk(b2["gate_conflict"]["rules_disagree"] is True,
        "L6 the 17.2pp spread book disagrees with r1411's phase rule")
    chk(b2["partial_years"] and b2["partial_years"][0]["year"] == "2026",
        "L7 the partial year is named rather than annualised into the gate")
    chk(b2["year_metrics"]["worst_full_only"] == -7.608,
        "L8 the full-year-only twin is printed beside the gate number")

    # L9 capacity below the floor is not a candidate no matter how good the years are
    b3 = admission_block(good, 1e6, 1.0, 0.5)
    chk(b3["verdict"] == "CAPACITY_LIMITED", "L9 thin capacity reads %s" % b3["verdict"])

    # L10 all-negative tape is refused, not loud-but-admitted
    bad = {y: {"net_pct": -5.0, "cohorts": 4} for y in ("2020", "2021", "2022", "2023")}
    b4 = admission_block(bad, 5e7, 1.0, -0.05)
    chk(b4["verdict"] == "REFUSE", "L10 negative tape reads %s" % b4["verdict"])

    # L11 median exactly zero is not positive (strict >)
    flat = {y: {"net_pct": 0.0, "cohorts": 4} for y in ("2020", "2021", "2022")}
    m = year_metrics(_year_rows(flat))
    chk(m["median"] == 0.0, "L11 median of a flat book is 0")
    chk(year_checks(_year_rows(flat), 5e7)["checks"]["Y2_median_positive"] is False,
        "L12 median 0 does not pass Y2")

    # L13 a single-year book cannot reach ADMIT: nothing to compare, so Y4
    # reads 1.0 and the best it can be is CONDITIONAL
    one = {"2026": {"net_pct": 40.0, "cohorts": 4}}
    chk(verdict(year_checks(_year_rows(one), 5e7)) == "CONDITIONAL",
        "L13 one-year book stops at CONDITIONAL")
    m1 = year_metrics(_year_rows(one))
    chk(m1["years"] == 1 and m1["top2_share"] == 1.0,
        "L14 a one-year book reports top2_share 1.0 so the reader sees the thinness")

    print("selftest %d/%d PASS" % (ok, tot))
    for e in errs:
        print("  FAIL:", e)
    return 0 if ok == tot else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["run", "selftest"])
    a = ap.parse_args()
    if a.mode == "selftest":
        return selftest()
    r = run()
    print(json.dumps({
        "verdicts": {f'{c["candidate"]}:{c["arm"]}': c["verdict"] for c in r["candidates"]},
        "pool_ready": r["pool_ready"],
        "flips": r["published_vs_year_gate"],
        "elapsed_sec": r["elapsed_sec"],
    }, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())