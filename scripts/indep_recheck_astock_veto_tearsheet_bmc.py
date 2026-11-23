#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Independent re-check of astock_veto_tearsheet (R5 seat: another implementation).

Why this exists
---------------
The astock_veto family published 13 faces in r2008..r2015, every one of them
written by the same host with the same code.  R5 (independent audit) means the
*absolute numbers that get quoted* must be recomputed at least once by a second,
separate implementation.  This module recomputes the risk block straight from
the parent face's per-period tape (results/astock_veto_lot_drag.json :: rows[]),
NOT by importing scripts/astock_veto_tearsheet.py, and then checks the reader
page (research/ASTOCK_VETO_TEARSHEET.md) prints the same numbers.

What it does NOT do
-------------------
It does not re-run the ranking / veto selection.  The pick list is an INPUT of
the parent face; this check takes the tape as given and audits the arithmetic
and the quoting.  Claiming more than that would be dishonest.

Usage
-----
  python scripts/indep_recheck_astock_veto_tearsheet_bmc.py run
  python scripts/indep_recheck_astock_veto_tearsheet_bmc.py check
  python scripts/indep_recheck_astock_veto_tearsheet_bmc.py --selftest
  python scripts/indep_recheck_astock_veto_tearsheet_bmc.py --negative

exit 0 = PASS / rc3 = FAILED (numbers disagree) / rc3 = face missing
"""
from __future__ import annotations

import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PARENT = os.path.join(ROOT, "results", "astock_veto_lot_drag.json")
TARGET = os.path.join(ROOT, "results", "astock_veto_tearsheet.json")
PAGE = os.path.join(ROOT, "research", "ASTOCK_VETO_TEARSHEET.md")
OUT = os.path.join(ROOT, "results", "indep_recheck_astock_veto_tearsheet.json")

PPY = 12.6          # periods per year, taken from the parent spec (hold=20, stride=20)
TOL = 1e-9          # arithmetic identity tolerance; anything above is a real disagreement
LOT_KEY = "lot_10000000"


# ---------------------------------------------------------------- primitives
def mean(xs):
    return sum(xs) / len(xs)


def stdev(xs):
    """Sample stdev (ddof=1) - the convention the published face uses."""
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))


def compound(xs):
    g = 1.0
    for x in xs:
        g *= (1.0 + x)
    return g


def annualized_compound(xs, ppy=PPY):
    return compound(xs) ** (ppy / len(xs)) - 1.0


def max_drawdown(xs):
    """Peak-to-trough on the compounded equity curve, seeded at 1.0."""
    peak = 1.0
    cur = 1.0
    mdd = 0.0
    for x in xs:
        cur *= (1.0 + x)
        if cur > peak:
            peak = cur
        dd = cur / peak - 1.0
        if dd < mdd:
            mdd = dd
    return mdd


def underwater_share(xs):
    """Share of periods whose equity sits below its running peak."""
    peak = 1.0
    cur = 1.0
    n_uw = 0
    for x in xs:
        cur *= (1.0 + x)
        if cur > peak:
            peak = cur
        elif cur < peak:
            n_uw += 1
    return n_uw / len(xs)


def worst_rolling(xs, w):
    """Worst compounded w-period block (compounded, overlapping)."""
    if len(xs) < w:
        return None
    worst = None
    for i in range(len(xs) - w + 1):
        blk = compound(xs[i:i + w]) - 1.0
        if worst is None or blk < worst:
            worst = blk
    return worst


def paired_t(diff):
    m = mean(diff)
    sd = stdev(diff)
    if sd == 0:
        return None
    return m / (sd / math.sqrt(len(diff)))


def risk_block(xs, ppy=PPY):
    """Everything a reader quotes, derived only from the tape."""
    m = mean(xs)
    sd = stdev(xs)
    ann = annualized_compound(xs, ppy)
    vol = sd * math.sqrt(ppy)
    mdd = max_drawdown(xs)
    return {
        "periods": len(xs),
        "per_period_mean": m,
        "per_period_stdev": sd,
        "annualized_compound": ann,
        "annual_vol": vol,
        "sharpe_excess_0": (m / sd * math.sqrt(ppy)) if sd else None,
        "max_drawdown": mdd,
        "calmar": (ann / abs(mdd)) if mdd else None,
        "hit_rate": sum(1 for x in xs if x > 0) / len(xs),
        "worst_period": min(xs),
        "best_period": max(xs),
        "worst_6_periods": worst_rolling(xs, 6),
        "underwater_share": underwater_share(xs),
    }


# ---------------------------------------------------------------- tape load
def load_tape():
    with open(PARENT, "r", encoding="utf-8") as fh:
        parent = json.load(fh)
    rows = parent["rows"]
    tapes = {
        "A_fractional": [r["A"]["net_frac"] for r in rows],
        "B_fractional": [r["B"]["net_frac"] for r in rows],
        ("A_" + LOT_KEY): [r["A"]["by_capital"]["10000000"]["net"] for r in rows],
        ("B_" + LOT_KEY): [r["B"]["by_capital"]["10000000"]["net"] for r in rows],
    }
    aux = {
        "turnover_A": [r["A"]["turnover"] for r in rows],
        "turnover_B": [r["B"]["turnover"] for r in rows],
        "gross_A": [r["A"]["gross_frac"] for r in rows],
        "gross_B": [r["B"]["gross_frac"] for r in rows],
        "cost_A": [r["A"]["gross_frac"] - r["A"]["net_frac"] for r in rows],
        "cost_B": [r["B"]["gross_frac"] - r["B"]["net_frac"] for r in rows],
    }
    return parent, tapes, aux


# ---------------------------------------------------------------- comparing
def compare_block(name, mine, pub, diffs):
    """Record |mine - published| for every published key we can derive."""
    worst = 0.0
    for key, pv in pub.items():
        if key not in mine:
            diffs.append({"face": name, "metric": key, "status": "NOT_DERIVED"})
            continue
        mv = mine[key]
        if mv is None or pv is None:
            diffs.append({"face": name, "metric": key,
                          "status": "UNCOMPARABLE", "mine": mv, "published": pv})
            continue
        d = abs(mv - pv)
        worst = max(worst, d)
        diffs.append({"face": name, "metric": key, "abs_diff": d,
                      "status": "OK" if d <= TOL else "DISAGREE",
                      "mine": mv, "published": pv})
    return worst


# ---------------------------------------------------------------- page check
def page_numbers():
    """All numeric tokens printed on the reader page (percent style kept as text)."""
    with open(PAGE, "r", encoding="utf-8") as fh:
        text = fh.read()
    toks = set()
    for m in re.finditer(r"[+-]?\d+(?:\.\d+)?", text):
        s = m.group(0)
        toks.add(s)
        # the page signs numbers ("+0.8241%", "-29.71%"); compare on the bare digits too
        toks.add(s.lstrip("+-"))
    return text, toks


def expect_token(value, pct=True, ndigits=2):
    """Format a value the way the page prints it (e.g. 0.3761 -> '0.38' / '37.61')."""
    v = value * 100.0 if pct else value
    s = f"{v:.{ndigits}f}"
    return s


def page_quote_check(tear):
    """Every headline number the page prints must be derivable from the JSON."""
    text, toks = page_numbers()
    A = tear["summary"]["A"]["bookings"]["fractional"]
    B = tear["summary"]["B"]["bookings"]["fractional"]
    AL = tear["summary"]["A"]["bookings"][LOT_KEY]
    BL = tear["summary"]["B"]["bookings"][LOT_KEY]
    edge = tear["edges"]["by_booking"]["fractional"]
    tax = tear["edges"]["edge_tax"]
    checks = [
        # Sharpe is a dimensionless ratio: the page prints it as 0.38, not 38%
        ("A_sharpe", A["sharpe_excess_0"], False, 2),
        ("B_sharpe", B["sharpe_excess_0"], False, 2),
        ("A_lot_sharpe", AL["sharpe_excess_0"], False, 2),
        ("B_lot_sharpe", BL["sharpe_excess_0"], False, 2),
        ("A_vol", A["annual_vol"], True, 2),
        ("B_vol", B["annual_vol"], True, 2),
        ("A_mdd", A["max_drawdown"], True, 2),
        ("B_mdd", B["max_drawdown"], True, 2),
        ("A_hit", A["hit_rate"], True, 1),
        ("B_hit", B["hit_rate"], True, 1),
        ("A_uw", A["underwater_share"], True, 1),
        ("B_uw", B["underwater_share"], True, 1),
        ("A_mean", A["per_period_mean"], True, 4),
        ("B_mean", B["per_period_mean"], True, 4),
        ("A_ann", A["annualized_compound"], True, 2),
        ("B_ann", B["annualized_compound"], True, 2),
        ("A_lot_mdd", AL["max_drawdown"], True, 2),
        ("B_lot_mdd", BL["max_drawdown"], True, 2),
        ("A_turnover", tear["summary"]["A"]["turnover_mean"], True, 2),
        ("B_turnover", tear["summary"]["B"]["turnover_mean"], True, 2),
        ("gross_edge", tax["gross_edge_per_period"], True, 4),
        ("net_edge", tax["net_edge_per_period"], True, 4),
        ("tax_share", tax["tax_share_of_gross_edge"], True, 1),
    ]
    be = tax.get("breakeven") or {}
    be_val = be.get("one_side_bp") if isinstance(be, dict) else None
    if be_val is not None:
        checks.append(("breakeven_bp", be_val / 100.0, True, 1))
    out = []
    for label, val, pct, nd in checks:
        if val is None:
            out.append({"label": label, "status": "NO_VALUE"})
            continue
        tok = expect_token(val, pct, nd)
        out.append({"label": label, "expect": tok,
                    "status": "FOUND" if tok in toks else "NOT_FOUND_ON_PAGE"})
    return out


# ---------------------------------------------------------------- run / check
def build():
    parent, tapes, aux = load_tape()
    with open(TARGET, "r", encoding="utf-8") as fh:
        tear = json.load(fh)

    diffs = []
    worst_by_face = {}
    mapping = {
        "A_fractional": tear["summary"]["A"]["bookings"]["fractional"],
        "B_fractional": tear["summary"]["B"]["bookings"]["fractional"],
        ("A_" + LOT_KEY): tear["summary"]["A"]["bookings"][LOT_KEY],
        ("B_" + LOT_KEY): tear["summary"]["B"]["bookings"][LOT_KEY],
    }
    mine = {}
    for face, xs in tapes.items():
        blk = risk_block(xs)
        mine[face] = blk
        worst_by_face[face] = compare_block(face, blk, mapping[face], diffs)

    # derived edges: mean of the A/B difference, paired t, sharpe gap, mdd gap
    dfrac = [b - a for a, b in zip(tapes["A_fractional"], tapes["B_fractional"])]
    edge_mine = {
        "mean_per_period": mean(dfrac),
        "t": paired_t(dfrac),
        "sharpe_b_minus_a": mine["B_fractional"]["sharpe_excess_0"] - mine["A_fractional"]["sharpe_excess_0"],
        "mdd_b_minus_a": mine["B_fractional"]["max_drawdown"] - mine["A_fractional"]["max_drawdown"],
    }
    pub_edge = tear["edges"]["by_booking"]["fractional"]
    edge_diffs = []
    worst_edge = 0.0
    for k, mv in edge_mine.items():
        pv = pub_edge.get(k)
        if pv is None or mv is None:
            edge_diffs.append({"metric": k, "status": "UNCOMPARABLE", "mine": mv, "published": pv})
            continue
        d = abs(mv - pv)
        worst_edge = max(worst_edge, d)
        edge_diffs.append({"metric": k, "abs_diff": d,
                           "status": "OK" if d <= 1e-9 else "DISAGREE",
                           "mine": mv, "published": pv})

    # auxiliary: cost identity, turnover identity, gross mean identity
    aux_out = {
        "turnover_mean_A_mine": mean(aux["turnover_A"]),
        "turnover_mean_A_pub": tear["summary"]["A"]["turnover_mean"],
        "turnover_mean_B_mine": mean(aux["turnover_B"]),
        "turnover_mean_B_pub": tear["summary"]["B"]["turnover_mean"],
        "gross_mean_A_mine": mean(aux["gross_A"]),
        "gross_mean_A_pub": tear["summary"]["A"]["gross"]["gross_per_period_mean"],
        "gross_mean_B_mine": mean(aux["gross_B"]),
        "gross_mean_B_pub": tear["summary"]["B"]["gross"]["gross_per_period_mean"],
        "cost_mean_A_mine": mean(aux["cost_A"]),
        "cost_mean_A_pub": tear["summary"]["A"]["gross"]["cost_per_period_mean"],
        "cost_mean_B_mine": mean(aux["cost_B"]),
        "cost_mean_B_pub": tear["summary"]["B"]["gross"]["cost_per_period_mean"],
    }
    aux_ok = {}
    for name in ("turnover_mean_A", "turnover_mean_B", "gross_mean_A",
                 "gross_mean_B", "cost_mean_A", "cost_mean_B"):
        aux_ok[name] = abs(aux_out[name + "_mine"] - aux_out[name + "_pub"])

    page = page_quote_check(tear)
    worst_page = sum(1 for p in page if p.get("status") == "NOT_FOUND_ON_PAGE")

    overall = max([worst_by_face.values()] and list(worst_by_face.values()) + [worst_edge]) if worst_by_face else 0.0
    overall = max(list(worst_by_face.values()) + [worst_edge] + list(aux_ok.values()))
    disagree = [d for d in diffs if d.get("status") == "DISAGREE"] + \
               [d for d in edge_diffs if d.get("status") == "DISAGREE"] + \
               [{"metric": k, "status": "DISAGREE"} for k, v in aux_ok.items() if v > 1e-9]

    verdict = "INDEP_RECHECK_PASS" if (not disagree and worst_page == 0) else "INDEP_RECHECK_FAILED"
    return {
        "schema": "indep_recheck_astock_veto_tearsheet/v1",
        "generated": _now(),
        "machine": "bm-c",
        "auditor": "second implementation (no import of scripts/astock_veto_tearsheet.py)",
        "evidence_cutoff": parent.get("evidence_cutoff"),
        "parent_face": "results/astock_veto_lot_drag.json",
        "target_face": "results/astock_veto_tearsheet.json",
        "reader_page": "research/ASTOCK_VETO_TEARSHEET.md",
        "scope": "risk block + quoting; selection is an input, not re-run",
        "tolerance": TOL,
        "worst_abs_diff_by_face": worst_by_face,
        "worst_abs_diff_edges": worst_edge,
        "worst_abs_diff_overall": overall,
        "values_recomputed": mine,
        "edges_recomputed": edge_mine,
        "auxiliary_identities": {"values": aux_out, "abs_diff": aux_ok},
        "per_metric_diffs": diffs,
        "edge_diffs": edge_diffs,
        "page_quote_checks": page,
        "page_tokens_not_found": worst_page,
        "disagreements": disagree,
        "verdict": verdict,
    }


def _now():
    import datetime
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def cmd_run():
    if not os.path.exists(PARENT):
        print("STALE parent face missing: results/astock_veto_lot_drag.json", file=sys.stderr)
        return 2
    if not os.path.exists(TARGET):
        print("STALE target face missing: results/astock_veto_tearsheet.json", file=sys.stderr)
        return 2
    rep = build()
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(rep, fh, ensure_ascii=False, indent=2)
    print(f"verdict={rep['verdict']} worst_diff={rep['worst_abs_diff_overall']:.3e} "
          f"disagreements={len(rep['disagreements'])} page_miss={rep['page_tokens_not_found']}")
    for d in rep["disagreements"][:10]:
        print("  DISAGREE", d)
    for p in rep["page_quote_checks"]:
        if p.get("status") == "NOT_FOUND_ON_PAGE":
            print("  PAGE-MISS", p)
    print("evidence -> results/indep_recheck_astock_veto_tearsheet.json")
    return 0 if rep["verdict"] == "INDEP_RECHECK_PASS" else 3


def cmd_check():
    if not os.path.exists(OUT):
        print("STALE evidence missing: run first", file=sys.stderr)
        return 3
    with open(OUT, "r", encoding="utf-8") as fh:
        old = json.load(fh)
    fresh = build()
    diffs = []
    for k in ("verdict", "worst_abs_diff_overall", "page_tokens_not_found"):
        if old.get(k) != fresh.get(k):
            diffs.append({"key": k, "evidence": old.get(k), "recomputed": fresh.get(k)})
    if old.get("evidence_cutoff") != fresh.get("evidence_cutoff"):
        diffs.append({"key": "evidence_cutoff",
                      "evidence": old.get("evidence_cutoff"),
                      "recomputed": fresh.get("evidence_cutoff")})
    if diffs:
        print("CHECK FAILED (recomputation drifted from published evidence)")
        for d in diffs:
            print("  ", d)
        return 3
    print(f"check ok: verdict={fresh['verdict']} worst_diff={fresh['worst_abs_diff_overall']:.3e} "
          f"page_miss={fresh['page_tokens_not_found']}")
    return 0


# ---------------------------------------------------------------- negatives
def cmd_negative():
    """Behavioural test: a tampered published number must turn the verdict red."""
    ok = 0
    total = 0

    def check(name, cond):
        nonlocal ok, total
        total += 1
        if cond:
            ok += 1
            print(f"  PASS {name}")
        else:
            print(f"  FAIL {name}")

    rep = build()
    check("baseline is PASS", rep["verdict"] == "INDEP_RECHECK_PASS")
    check("baseline worst_diff tiny", rep["worst_abs_diff_overall"] <= 1e-9)

    # tamper one published metric in-memory and confirm the comparator flags it
    with open(TARGET, "r", encoding="utf-8") as fh:
        tear = json.load(fh)
    tear["summary"]["B"]["bookings"]["fractional"]["sharpe_excess_0"] += 0.01
    parent, tapes, aux = load_tape()
    mine = {f: risk_block(xs) for f, xs in tapes.items()}
    diffs = []
    worst = compare_block("B_fractional", mine["B_fractional"],
                          tear["summary"]["B"]["bookings"]["fractional"], diffs)
    check("tampered sharpe is caught", worst > 1e-9)
    check("tampered flagged DISAGREE",
          any(d.get("status") == "DISAGREE" for d in diffs))

    # a missing parent face must be a hard stale, never a silent pass
    saved = {}
    for p in (PARENT,):
        with open(p, "rb") as fh:
            saved[p] = fh.read()
    try:
        os.remove(PARENT)
        check("missing parent -> rc2", cmd_run() == 2)
    finally:
        with open(PARENT, "wb") as fh:
            fh.write(saved[PARENT])
    check("parent restored, run green again", cmd_run() == 0)

    print(f"{ok}/{total} PASS")
    return 0 if ok == total else 3


# ---------------------------------------------------------------- selftest
def cmd_selftest():
    ok = 0
    total = 0

    def check(name, cond):
        nonlocal ok, total
        total += 1
        if cond:
            ok += 1
            print(f"  PASS {name}")
        else:
            print(f"  FAIL {name}")

    # 1 mean of [1,2,3]
    check("mean 1,2,3 = 2", abs(mean([0.01, 0.02, 0.03]) - 0.02) < 1e-12)
    # 2 sample stdev of [1,2,3] = 1
    check("stdev ddof1 [1,2,3] = 1", abs(stdev([1.0, 2.0, 3.0]) - 1.0) < 1e-12)
    # 3 compound of +10%,-10% = 0.99
    check("compound +10/-10 = 0.99", abs(compound([0.10, -0.10]) - 0.99) < 1e-12)
    # 4 annualized: flat 1%/期 for 63 期 (=5y at 12.6) -> (1.01^63)^(12.6/63)-1
    xs = [0.01] * 63
    exp = 1.01 ** 12.6 - 1.0
    check("annualized flat 1% x63 == 1.01^12.6-1",
          abs(annualized_compound(xs) - exp) < 1e-12)
    # 5 max drawdown: +100% then -50% -> trough at 0% => mdd = -50%
    check("mdd +100/-50 = -0.5", abs(max_drawdown([1.0, -0.5]) - (-0.5)) < 1e-12)
    # 6 mdd monotone up is zero
    check("mdd all-up = 0", abs(max_drawdown([0.01, 0.02, 0.03])) < 1e-15)
    # 7 underwater: up, down, up(new high) -> 1 of 3
    check("underwater 1/3", abs(underwater_share([0.1, -0.05, 0.2]) - 1.0 / 3.0) < 1e-12)
    # 8 underwater never-below = 0
    check("underwater all-up = 0", abs(underwater_share([0.01, 0.02])) < 1e-15)
    # 9 paired t symmetric sign
    d1 = [0.01, 0.02, 0.03, 0.01]
    check("paired t sign flips with diff sign",
          abs(paired_t(d1) + paired_t([-x for x in d1])) < 1e-12)
    # 10 paired t of constant nonzero diff is None (sd=0) - must not divide by zero
    check("paired t constant -> None", paired_t([0.01] * 5) is None)
    # 11 worst rolling: blocks of 2 are -0.12 / -0.16 / -0.265 -> worst is -0.265
    check("worst_rolling w2 picks -0.265",
          abs(worst_rolling([0.1, -0.2, 0.05, -0.3], 2) - (1.05 * 0.7 - 1.0)) < 1e-12)
    # 12 sharpe of zero-variance is None (guarded)
    blk = risk_block([0.0] * 10)
    check("zero-variance sharpe/calmar guarded",
          blk["sharpe_excess_0"] is None and blk["calmar"] is None)
    # 13 hit rate counts strictly positive
    check("hit rate strict >0", abs(risk_block([0.01, 0.0, -0.01])["hit_rate"] - 1.0 / 3.0) < 1e-12)
    # 14 expect_token formats percent
    check("expect_token 0.3761 -> 37.61", expect_token(0.3761, True, 2) == "37.61")
    # 15 expect_token negative
    check("expect_token -0.2971 -> -29.71", expect_token(-0.2971, True, 2) == "-29.71")

    print(f"{ok}/{total} PASS")
    return 0 if ok == total else 3


def main(argv):
    if "--selftest" in argv:
        return cmd_selftest()
    if "--negative" in argv:
        return cmd_negative()
    if "check" in argv:
        return cmd_check()
    if "run" in argv or len(argv) == 1:
        return cmd_run()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
