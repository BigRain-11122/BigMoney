#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""the year gate counts a partial year as a year -- for two checks that is protective, for two it is a gift

WHY THIS FILE EXISTS
--------------------
r1440 went looking for one answer and stumbled on a number: the arm the live ticket
actually accrues (plain book + beta overlay) passes Y4 at 67.52% top-2 share, and the
same arm reads 77.57% once partial 2020 is dropped -- i.e. the pass exists only because
a window that is not a year was counted as a year.  r1444 then showed all four year-axis
checks are blind forward, which moved the question from "does the check predict?" to
"what is the check even measuring?".

scripts/candidate_year_gate.py documents its partial-year treatment as deliberate: "Y3
and Y4 use raw calendar-year returns, including a partial year, because a loss booked in
the current year is a loss".  That sentence is sound for Y3 (*worst* year -- including a
partial year can only make the gate stricter) and it is exactly backwards for Y4
(*concentration share* -- a short window shrinks the numerator and the denominator, so
including it can only make the gate more permissive).  The same inclusion rule protects
on one check and gives on the other, and no receipt says which is which.

This file puts every published book through three calibers of the same frozen checks:

  A  as published          all calendar years, partial included (production caliber)
  B  full years only       every check ignores the partial year
  P  protection-consistent Y1/Y2/Y4 (typical / aggregate shape) = full years only
                           Y3 (worst booked loss)                = all years
                           C1 unchanged (capacity is not a calendar statistic)

The thresholds are NOT touched -- only which rows enter each statistic.  Nothing here
adopts anything: production stays on caliber A, and adopting P is a decision for the
2026-11-11 rebalance path with its own preregistration.

WHAT A READER SHOULD TAKE AWAY
------------------------------
For each book: the verdict under all three calibers, which checks move, and the reason
a check moved (the partial year entering or leaving *that* check).  Then the aggregate:
how many books are only on the ADMIT side of the line because a window shorter than a
year was counted as one.

self  python scripts/etf_book_partial_year_caliber.py selftest
run   python scripts/etf_book_partial_year_caliber.py run
check python scripts/etf_book_partial_year_caliber.py --check
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import candidate_year_gate as cyg  # single implementation of the frozen checks

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "results", "etf_book_partial_year_caliber")
OUT = os.path.join(OUT_DIR, "CALIBER.json")

SOURCES = [
    ("year_gate", "results/etf_book_year_gate/YEAR-GATE.json"),
    ("wrapper_gate", "results/etf_book_year_gate/WRAPPER-GATE.json"),
    ("admission", "results/admission/CANDIDATES.json"),
    ("gate_forward", "results/etf_book_gate_forward/GATE-FORWARD.json"),
]

YEAR_CHECKS = ("Y1_positive_years_share", "Y2_median_positive", "Y3_worst_year",
               "Y4_top2_share")
PROTECT_FULL_ONLY = ("Y1_positive_years_share", "Y2_median_positive", "Y4_top2_share")


# ---------------------------------------------------------------- collection
def _norm_rows(years) -> list[dict]:
    """accept both published shapes -> [{year, net_pct, cohorts, partial}] sorted by year."""
    rows = []
    if isinstance(years, dict):
        it = [dict(blk or {}, year=k) for k, blk in years.items()]
    elif isinstance(years, list):
        it = [dict(x) for x in years]
    else:
        return rows
    for blk in it:
        n, c = blk.get("net_pct"), blk.get("cohorts")
        if n is None:
            continue
        if c is None:
            # a bare {year: net_pct} face carries no cohort count; the caller that
            # knows the partial flag passes it in explicitly (see _entries gate_forward)
            c = 4
        rows.append({"year": str(blk.get("year")), "net_pct": float(n),
                     "cohorts": int(c),
                     "partial": bool(blk.get("partial", int(c) < 4))})
    rows.sort(key=lambda r: r["year"])
    return rows


def _entries() -> list[dict]:
    """every published book in the four receipts, with its published verdict."""
    out = []
    for face, rel in SOURCES:
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            out.append({"face": face, "missing": rel})
            continue
        d = json.load(open(path, encoding="utf-8"))
        if face == "gate_forward":
            # this receipt publishes {year: net_pct} plus a partial_years list, so the
            # flag comes from the receipt and only the cohort count is synthesised
            partial = {str(y) for y in (d.get("partial_years") or [])}
            for arm, blk in sorted((d.get("arms") or {}).items()):
                yrs = blk.get("years") or {}
                rows = []
                for y, n in sorted(yrs.items()):
                    y = str(y)
                    part = y in partial or y in {str(p) for p in (blk.get("partial_years") or [])}
                    rows.append({"year": y, "net_pct": float(n),
                                 "cohorts": 3 if part else 4, "partial": part})
                out.append({
                    "face": face, "source": rel, "name": arm,
                    "years": rows,
                    "published_verdict": None,  # this receipt publishes no verdict
                    "published_checks": None,
                    "capacity_cny": None,
                    "capacity_checked": False,
                })
            continue
        books = d.get("books") if isinstance(d.get("books"), list) else d.get("candidates")
        for blk in (books or []):
            name = blk.get("arm") or blk.get("book") or blk.get("candidate") or "?"
            checks = dict(blk.get("checks") or {})
            cap = blk.get("capacity_cny_1day_5pct")
            out.append({
                "face": face, "source": rel, "name": name,
                "years": _norm_rows(blk.get("years")),
                "published_verdict": blk.get("verdict"),
                "published_checks": checks,
                "capacity_cny": cap if checks.get("C1_capacity") is not None else None,
                "capacity_checked": bool(blk.get("capacity_checked")),
            })
    return out


# ------------------------------------------------------------------ calibers
def caliber_checks(rows: list[dict], capacity_cny: float | None) -> dict:
    """the three calibers, all through candidate_year_gate.year_checks (nothing copied)."""
    full = [r for r in rows if not r["partial"]]
    a = cyg.year_checks(rows, capacity_cny)
    b = cyg.year_checks(full, capacity_cny)
    p_checks = {}
    for k, v in a["checks"].items():
        p_checks[k] = b["checks"][k] if k in PROTECT_FULL_ONLY else v
    p = {"metrics": a["metrics"], "checks": p_checks}
    return {"A": a, "B": b, "P": p}


def _moved(a: dict, b: dict) -> list[str]:
    return [k for k in YEAR_CHECKS + ("C1_capacity",)
            if a["checks"].get(k) != b["checks"].get(k)]


# ----------------------------------------------------------------------- run
def build() -> dict:
    entries = _entries()
    rows_out, flips = [], []
    counts = {"A": {}, "B": {}, "P": {}}
    for e in entries:
        if e.get("missing"):
            rows_out.append({"face": e["face"], "status": "source_missing",
                             "source": e["missing"]})
            continue
        if not e["years"]:
            rows_out.append({"face": e["face"], "name": e["name"],
                             "status": "no_years_published"})
            continue
        cal = caliber_checks(e["years"], e["capacity_cny"])
        v = {c: cyg.verdict(cal[c]) for c in ("A", "B", "P")}
        for c in ("A", "B", "P"):
            counts[c][v[c]] = counts[c].get(v[c], 0) + 1
        partial = [r["year"] for r in e["years"] if r["partial"]]
        rec = {
            "face": e["face"], "name": e["name"], "source": e["source"],
            "years": len(e["years"]), "partial_years": partial,
            "calibers": {
                "A": {"verdict": v["A"], "checks": cal["A"]["checks"],
                      "metrics": cal["A"]["metrics"]},
                "B": {"verdict": v["B"], "checks": cal["B"]["checks"],
                      "metrics": cal["B"]["metrics"]},
                "P": {"verdict": v["P"], "checks": cal["P"]["checks"],
                      "metrics": cal["P"]["metrics"]},
            },
            "checks_moved_A_to_B": _moved(cal["A"], cal["B"]),
            "checks_moved_A_to_P": _moved(cal["A"], cal["P"]),
            "published_verdict": e["published_verdict"],
        }
        if e["published_verdict"] and v["A"] != e["published_verdict"]:
            rec["identity_break"] = {"published": e["published_verdict"], "A": v["A"]}
        rows_out.append(rec)
        if v["P"] != v["A"]:
            flips.append({"face": e["face"], "name": e["name"],
                          "A": v["A"], "P": v["P"],
                          "checks_moved": rec["checks_moved_A_to_P"],
                          "top2_share": cal["A"]["metrics"]["top2_share"],
                          "top2_share_full_only": cal["B"]["metrics"]["top2_share_full_only"]})

    identity_breaks = [r for r in rows_out if r.get("identity_break")]
    admit_gained = [f for f in flips if f["A"] != "ADMIT" and f["P"] == "ADMIT"]
    admit_lost = [f for f in flips if f["A"] == "ADMIT" and f["P"] != "ADMIT"]

    return {
        "face": "etf_book_partial_year_caliber",
        "generated": __import__("datetime").datetime.now().astimezone().isoformat(timespec="seconds"),
        "evidence_cutoff": "2026-11-06",
        "question": "the year gate counts a partial year as a year on every check -- where does that protect, where does it give?",
        "calibers": {
            "A": "as published: all calendar years, partial included (production caliber)",
            "B": "full calendar years only (every check)",
            "P": "protection-consistent: Y1/Y2/Y4 full years only, Y3 all years, C1 unchanged",
        },
        "why_P": "Y3 asks for a booked loss and a partial year can only make it stricter; "
                 "Y1/Y2/Y4 ask what a typical year looks like, and a 3-cohort window is not a year",
        "thresholds_touched": False,
        "production_caliber": "A",
        "adoption": "NOT ADOPTED -- P is evidence for the 2026-11-11 rebalance decision, needs its own prereg",
        "counts_by_caliber": counts,
        "identity_breaks": identity_breaks,
        "flips_A_to_P": flips,
        "admit_lost_under_P": admit_lost,
        "admit_gained_under_P": admit_gained,
        "rows": rows_out,
        "honest": [
            "no repricing and no engine call: every number is recomputed from the years block each receipt already published",
            "caliber P is a proposal; nothing in the chain reads it and production stays on A this round",
            "gate_forward arms publish no verdict and no capacity face, so their C1 column is unchecked (not passed)",
            "a flip here is a measurement statement about the same numbers, not a new backtest",
        ],
    }


def run() -> int:
    res = build()
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(res, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")
    print(f"[caliber] {len(res['rows'])} books  A={res['counts_by_caliber']['A']} "
          f"P={res['counts_by_caliber']['P']}")
    print(f"[caliber] flips A->P {len(res['flips_A_to_P'])}  admit_lost {len(res['admit_lost_under_P'])}  "
          f"identity_breaks {len(res['identity_breaks'])}")
    for f in res["admit_lost_under_P"]:
        print(f"  ADMIT GONE  {f['face']}/{f['name']}  A=ADMIT P={f['P']}  "
              f"top2 {f['top2_share']} -> full-only {f['top2_share_full_only']}")
    for b in res["identity_breaks"]:
        print(f"  IDENTITY BREAK {b['face']}/{b['name']}  published={b['identity_break']}")
    print(f"[caliber] wrote {os.path.relpath(OUT, ROOT)}")
    return 0 if not res["identity_breaks"] else 2


def check() -> int:
    path = OUT
    if not os.path.exists(path):
        print("[caliber] check: receipt missing, run first")
        return 2
    raw = open(path, encoding="utf-8").read()
    d = json.loads(raw)
    errs = []
    recomputed = build()
    for key in ("counts_by_caliber", "flips_A_to_P", "identity_breaks", "rows"):
        if json.dumps(d.get(key), sort_keys=True, ensure_ascii=False) != \
                json.dumps(recomputed.get(key), sort_keys=True, ensure_ascii=False):
            errs.append(f"receipt {key} does not re-derive from the same sources")
    if d.get("thresholds_touched") is not False:
        errs.append("receipt claims thresholds were touched")
    if d.get("production_caliber") != "A":
        errs.append("receipt claims a non-production caliber")
    if errs:
        for e in errs:
            print(f"[caliber] CHECK FAIL {e}")
        return 1
    print(f"[caliber] CHECK OK {len(d['rows'])} books re-derived, zero identity breaks")
    return 0


# ------------------------------------------------------------------ selftest
def _rows(spec: dict) -> list[dict]:
    return _norm_rows(spec)


def selftest() -> int:
    ok = 0
    legs = []

    def leg(name, cond, detail=""):
        nonlocal ok
        if cond:
            ok += 1
        legs.append((name, bool(cond), detail))

    # L1 a book with no partial year reads identically under all three calibers
    full = {"2021": {"net_pct": 6.0, "cohorts": 4}, "2022": {"net_pct": 5.0, "cohorts": 4},
            "2023": {"net_pct": 4.0, "cohorts": 4}, "2024": {"net_pct": 3.0, "cohorts": 4}}
    cal = caliber_checks(_rows(full), 5e7)
    vs = {c: cyg.verdict(cal[c]) for c in ("A", "B", "P")}
    leg("L1 no partial year -> A == B == P", len(set(vs.values())) == 1, str(vs))

    # L2 a short window can DILUTE the top-2 share and buy a Y4 pass (lenient direction)
    gift = {"2021": {"net_pct": 30.0, "cohorts": 4}, "2022": {"net_pct": 2.0, "cohorts": 4},
            "2023": {"net_pct": 3.0, "cohorts": 4}, "2024": {"net_pct": 2.0, "cohorts": 4},
            "2025": {"net_pct": 29.0, "cohorts": 4}, "2026": {"net_pct": 25.0, "cohorts": 3}}
    cal = caliber_checks(_rows(gift), 5e7)
    leg("L2 partial year can make Y4 pass (lenient direction exists)",
        cal["A"]["checks"]["Y4_top2_share"] and not cal["B"]["checks"]["Y4_top2_share"],
        f"A={cal['A']['metrics']['top2_share']} B={cal['B']['metrics']['top2_share_full_only']}")

    # L3 a partial loss can fail Y3 that passes without it (protective direction exists)
    loss = {"2021": {"net_pct": 10.0, "cohorts": 4}, "2022": {"net_pct": 8.0, "cohorts": 4},
            "2023": {"net_pct": 9.0, "cohorts": 4}, "2024": {"net_pct": 7.0, "cohorts": 4},
            "2025": {"net_pct": 8.0, "cohorts": 4}, "2026": {"net_pct": -20.0, "cohorts": 2}}
    cal = caliber_checks(_rows(loss), 5e7)
    leg("L3 partial loss fails Y3 that would pass without it (protective direction exists)",
        (not cal["A"]["checks"]["Y3_worst_year"]) and cal["B"]["checks"]["Y3_worst_year"],
        f"A worst={cal['A']['metrics']['worst']} B worst={cal['B']['metrics']['worst_full_only']}")

    # L4 caliber P keeps the protective half of L3's loss and ignores the lenient half
    cal = caliber_checks(_rows(loss), 5e7)
    leg("L4 P keeps Y3 from all-years and Y4 from full-years",
        cal["P"]["checks"]["Y3_worst_year"] == cal["A"]["checks"]["Y3_worst_year"]
        and cal["P"]["checks"]["Y4_top2_share"] == cal["B"]["checks"]["Y4_top2_share"])

    # L5 P is not a free pass: on the gift book P must NOT inherit A's lenient Y4
    cal = caliber_checks(_rows(gift), 5e7)
    leg("L5 P drops the gift: Y4 reads full-only under P",
        not cal["P"]["checks"]["Y4_top2_share"], str(cal["P"]["checks"]["Y4_top2_share"]))

    # L6 an unchecked capacity column is not a pass and not a fail
    cal = caliber_checks(_rows(gift), None)
    leg("L6 capacity None stays None under every caliber",
        all(cal[c]["checks"]["C1_capacity"] is None for c in ("A", "B", "P")))

    # L7 verdict() maps exactly-three to CONDITIONAL and two to REFUSE (imported, pinned here)
    c3 = {"checks": {"Y1_positive_years_share": True, "Y2_median_positive": True,
                     "Y3_worst_year": True, "Y4_top2_share": False, "C1_capacity": True}}
    c2 = {"checks": {"Y1_positive_years_share": True, "Y2_median_positive": False,
                     "Y3_worst_year": False, "Y4_top2_share": False, "C1_capacity": True}}
    leg("L7 verdict mapping pinned (3 pass -> CONDITIONAL, 2 -> REFUSE)",
        cyg.verdict(c3) == "CONDITIONAL" and cyg.verdict(c2) == "REFUSE")

    # L8 _norm_rows reads both published shapes and sorts
    a = _norm_rows({"2026": {"net_pct": 1.0, "cohorts": 3}, "2025": {"net_pct": 2.0, "cohorts": 4}})
    b = _norm_rows([{"year": "2025", "net_pct": 2.0, "cohorts": 4},
                    {"year": "2026", "net_pct": 1.0, "cohorts": 3}])
    leg("L8 both published year shapes normalise to the same rows and sort by year",
        [r["year"] for r in a] == ["2025", "2026"] and
        [(r["year"], r["net_pct"], r["partial"]) for r in a] ==
        [(r["year"], r["net_pct"], r["partial"]) for r in b])

    # L9 a partial year is detected from cohorts even when the flag is absent
    r = _norm_rows([{"year": "2026", "net_pct": 1.0, "cohorts": 2}])
    leg("L9 partial detected from cohorts<4 when the flag is missing", r[0]["partial"] is True)

    # L10 build() is deterministic twice and keeps a flip list consistent with rows
    b1, b2 = build(), build()
    key = lambda d: json.dumps({k: d[k] for k in ("counts_by_caliber", "flips_A_to_P", "rows")},
                               sort_keys=True, ensure_ascii=False)
    leg("L10 build is deterministic on the same receipts", key(b1) == key(b2))
    leg("L11 every flip names a check that actually moved",
        all(f["checks_moved"] for f in b1["flips_A_to_P"]))
    leg("L12 no flip is claimed when P == A on that row",
        all(any(r.get("name") == f["name"] and r["face"] == f["face"]
                and r["calibers"]["A"]["verdict"] == r["calibers"]["P"]["verdict"]
                for r in b1["rows"] if r.get("calibers")) is False
            for f in b1["flips_A_to_P"]))

    for name, good, detail in legs:
        print(f"  {'PASS' if good else 'FAIL'}  {name}" + (f"  [{detail}]" if detail and not good else ""))
    print(f"[caliber] selftest {ok}/{len(legs)}")
    return 0 if ok == len(legs) else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run",
                    choices=["run", "selftest", "check"])
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    if a.check or a.cmd == "check":
        return check()
    if a.cmd == "selftest":
        return selftest()
    return run()


if __name__ == "__main__":
    raise SystemExit(main())