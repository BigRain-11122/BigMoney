# -*- coding: utf-8 -*-
"""Swap the control arm: is `rankind` still better when the control is not noisy?

r1947 (scripts/astock_rankind_second_sample.py) moved `rankind - ind` onto two other
samples of the same panel and got HOLDS_ON_ONE_SAMPLE_ONLY. The diagnosis it printed
was specific: the differential did not collapse because within-industry rank got worse
(+3.76% -> +4.19%/yr), it collapsed because the industry-dummy control `ind` got
*better* (+0.51% -> +3.49%/yr). A difference of two noisy arms is the standard way to
manufacture a finding. Its own first prescription was:

    swap in a stabler control -- the beta+size residual arm (`resid`, r1862) -- and
    re-test whether within-industry rank adds anything on top of it.

That is the whole question on this face, asked on the same three samples with the
identical frozen criterion. Nothing else changes: every row still comes from
`astock_resid_industry_neutral.run` on the same loaded panel, same 8bp/side cost, same
quintiles, same liquidity gate, same point-in-time industry map, same sampling offsets
(0/10 with stride 20, and 0 with stride 40). This face does not touch the maths and
does not re-open r1945/r1946/r1947.

Frozen criterion (written here, before any run; identical to r1947, not tuned)
------------------------------------------------------------------------------
    holds(sample) := n >= 12 AND mean(differential) > 0 AND t(differential) >= 1.5

    RESID_CONTROL_HOLDS_ON_BOTH_ALTERNATE_SAMPLES   S1 holds and S2 holds
    RESID_CONTROL_HOLDS_ON_ONE_SAMPLE_ONLY          exactly one of them holds
    RESID_CONTROL_DOES_NOT_HOLD                     neither holds
    NOT_ENOUGH_REBALANCES                           any sample under 12 rebalances

`ind` is re-run beside it with the same machinery purely as a reproduction of r1947:
if the numbers this face prints for `rankind - ind` are not the ones r1947 published,
the run is an error, not a reading, and nothing is published.

Two readings that are printed but are NOT part of the verdict
-------------------------------------------------------------
* Which control is actually stable: each arm's own q1 excess per sample and the
  spread of that annual number across the three samples. Calling `resid` "stable"
  without measuring it would be the same mistake one level up.
* r1947's second prescription: whether `rankind`'s *own* long leg (absolute, not
  differenced) is positive on all three samples. Descriptive only.

Honest boundaries (printed with the result, not kept in a notebook)
-------------------------------------------------------------------
* Same panel, same calendar, different observation dates. The alternates are not a
  second dataset; phase-shifted rows share formation windows and market moves with
  S0, so no pooled t exists here and none is claimed.
* Sign-flip p is reported per sample and per pair; it is not part of the verdict.
* No candidate, no prereg, no adoption. Long-only excess at 8bp/side on an
  investable-domain quintile is not a tradable book (ST/limit/delisting unhandled).

Usage:
    python scripts/astock_rankind_control_swap.py run
    python scripts/astock_rankind_control_swap.py check
    python scripts/astock_rankind_control_swap.py selftest
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import astock_resid_reversal_probe as base  # noqa: E402  (panel loader + maths)
import astock_resid_industry_neutral as neut  # noqa: E402  (the row producer)
import astock_rankind_stability as stab  # noqa: E402  (series/t-stat/sign-flip)
import astock_rankind_second_sample as rs2  # noqa: E402  (sampling + criterion, reused)

UPSTREAM = rs2.UPSTREAM  # results/astock_resid_industry_neutral.json (the rows)
PRIOR = rs2.OUT  # results/astock_rankind_second_sample.json (r1947, the ind pair)
OUT = os.path.join(ROOT, "results", "astock_rankind_control_swap.json")

Q1_KEY = rs2.Q1_KEY
SAMPLES = rs2.SAMPLES
ALTERNATES = rs2.ALTERNATES
MIN_REBALANCES = rs2.MIN_REBALANCES
T_FLOOR = rs2.T_FLOOR
DRAWS = rs2.DRAWS
SEED = rs2.SEED
REPRO_TOL = rs2.REPRO_TOL

PRIMARY = ("rankind", "resid")
REPRODUCTION_PAIR = ("rankind", "ind")
ARMS = ("rankind", "resid", "ind")

CRITERIA = {
    "primary_pair": "%s-minus-%s" % PRIMARY,
    "reproduction_pair": "%s-minus-%s" % REPRODUCTION_PAIR,
    "read": "q1_excess per rebalance, the implementable long leg, identical maths and costs",
    "holds": "n >= %d AND mean > 0 AND t >= %.1f" % (MIN_REBALANCES, T_FLOOR),
    "verdict_order": ["NOT_ENOUGH_REBALANCES",
                      "RESID_CONTROL_HOLDS_ON_BOTH_ALTERNATE_SAMPLES",
                      "RESID_CONTROL_HOLDS_ON_ONE_SAMPLE_ONLY",
                      "RESID_CONTROL_DOES_NOT_HOLD"],
    "samples_frozen": [s["label"] for s in SAMPLES],
    "reproduction_role": ("rankind-minus-ind is re-run here only to reproduce r1947; "
                          "a mismatch against that face is an error, not a reading"),
    "not_in_verdict": ["which control is stable (descriptive spread)",
                       "rankind's own absolute long leg across samples (descriptive)",
                       "sign-flip p"],
    "signflip": "%d draws, seed %d, reported but not part of the verdict" % (DRAWS, SEED),
    "note": "frozen in this file before the first run; no threshold was touched afterwards",
}


def _rel(path: str) -> str:
    """Repo-relative when possible; an absolute path when the face lives on another drive."""
    try:
        return os.path.relpath(path, ROOT).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


# ------------------------------------------------------------------ differential
def differential(rows, a: str, b: str):
    """a minus b, one value per rebalance; a missing key is an error, never a skip."""
    control = dict(stab.series(rows, Q1_KEY % b))
    diff = []
    for date, value in stab.series(rows, Q1_KEY % a):
        if date not in control:
            raise KeyError("rebalance %s has no %r row" % (date, Q1_KEY % b))
        diff.append((date, value - control[date]))
    return diff


def arm_stats(rows, arm: str):
    """Own level of one arm: mean/t/hit of its q1 excess, on the same rows."""
    vals = [v for _, v in stab.series(rows, Q1_KEY % arm)]
    st = stab._stat(vals)
    return {"n": len(vals), "mean": st.get("mean"), "t": st.get("t"),
            "hit": st.get("hit"), "annual": base.compound(vals) if vals else None}


def pair_block(rows, sample_spec, pair):
    """One sample x one pair: the differential, its yearly table and both arms' levels."""
    diff = differential(rows, *pair)
    vals = [v for _, v in diff]
    st = stab._stat(vals)
    yearly = stab.group_years(diff)
    block = {
        "id": sample_spec["id"],
        "label": sample_spec["label"],
        "offset": sample_spec["offset"],
        "stride": sample_spec["stride"],
        "n": len(vals),
        "first": diff[0][0] if diff else None,
        "last": diff[-1][0] if diff else None,
        "differential": {
            "summary": st,
            "annual": base.compound(vals) if vals else None,
            "yearly": [{"year": y["year"], "n": y["n"], "mean": y["mean"], "t": y["t"]}
                       for y in yearly],
            "years_positive": sum(1 for y in yearly if (y["mean"] or 0.0) > 0),
            "years_total": len(yearly),
            "signflip_p": stab.signflip_p(vals, draws=DRAWS, seed=SEED),
        },
    }
    block["holds"] = rs2.holds(block)
    return block


def holds(block) -> bool:
    """Same predicate as r1947, imported rather than retyped."""
    return rs2.holds(block)


def verdict_for(blocks, label: str) -> str:
    """Identical verdict machinery as r1947, namespaced by which control was swapped."""
    return "%s_%s" % (label, rs2.verdict_for(blocks))


def snapshot(blocks) -> dict:
    """The cells the prior face published, in a shape a mismatch detector can compare."""
    out = {}
    for sid, block in blocks.items():
        st = block["differential"]["summary"]
        out[sid] = {"n": block["n"], "mean": st.get("mean"), "t": st.get("t"),
                    "holds": block["holds"], "first": block["first"], "last": block["last"]}
    return out


def compare_snapshots(mine, theirs, label: str, tol: float = 1e-9):
    """Field-for-field comparison against a published face; returns a list of problems."""
    problems = []
    for sid in sorted(set(mine) | set(theirs)):
        if sid not in theirs:
            problems.append("%s %s missing from the prior face" % (label, sid))
            continue
        if sid not in mine:
            problems.append("%s %s missing from this run" % (label, sid))
            continue
        a, b = mine[sid], theirs[sid]
        if a.get("n") != b.get("n"):
            problems.append("%s %s n %r vs %r" % (label, sid, a.get("n"), b.get("n")))
        for key in ("mean", "t"):
            x, y = a.get(key), b.get(key)
            if x is None or y is None:
                if x is not y:
                    problems.append("%s %s %s %r vs %r" % (label, sid, key, x, y))
                continue
            if abs(float(x) - float(y)) > tol:
                problems.append("%s %s %s %.12g vs %.12g" % (label, sid, key, x, y))
        if bool(a.get("holds")) != bool(b.get("holds")):
            problems.append("%s %s holds %r vs %r" % (label, sid, a.get("holds"), b.get("holds")))
    return problems


def identity_problems(samples: dict):
    """mean(a - b) must equal mean(a) - mean(b); a drifted face is caught here."""
    problems = []
    for sid, block in samples.items():
        arms = block.get("arms") or {}
        for arm, pair in (("primary", PRIMARY), ("reproduction", REPRODUCTION_PAIR)):
            d = ((block.get("pairs") or {}).get(arm) or {}).get("differential", {})
            mean = (d.get("summary") or {}).get("mean")
            a = ((arms.get(pair[0]) or {}).get("mean"))
            b = ((arms.get(pair[1]) or {}).get("mean"))
            if mean is None or a is None or b is None:
                continue
            if abs(float(mean) - (float(a) - float(b))) > 1e-9:
                problems.append("%s %s mean %.12g != %.12g - %.12g"
                                % (sid, arm, mean, a, b))
    return problems


# ------------------------------------------------------------------ build
def build_report(upstream, upstream_path: str = UPSTREAM, prior_path: str = PRIOR,
                 panel=None, keep_rows: bool = False):
    hist = neut.load_industry()
    if panel is None:
        panel = base.load_panel()
    dates, symbols, close, amount, shares = panel

    samples, raw = {}, {}
    for spec in SAMPLES:
        rows = rs2.run_sample(dates, symbols, close, amount, shares, hist,
                              offset=spec["offset"], stride=spec["stride"])
        if not rows:
            raise SystemExit("sample %s produced no rows" % spec["id"])
        raw[spec["id"]] = rows
        samples[spec["id"]] = {
            "arms": {arm: arm_stats(rows, arm) for arm in ARMS},
            "pairs": {
                "primary": pair_block(rows, spec, PRIMARY),
                "reproduction": pair_block(rows, spec, REPRODUCTION_PAIR),
            },
        }

    # r1947's cells must come back unchanged, or this is an error rather than a reading
    prior = json.load(open(prior_path, encoding="utf-8"))
    prior_blocks = {sid: b for sid, b in (prior.get("samples") or {}).items()}
    mine = {sid: s["pairs"]["reproduction"] for sid, s in samples.items()}
    prior_repro = compare_snapshots(snapshot(mine), snapshot(prior_blocks),
                                    "rankind-minus-ind")
    prior_verdict = prior.get("verdict")
    mine_verdict = rs2.verdict_for(mine)
    if mine_verdict != prior_verdict:
        prior_repro.append("verdict %r vs published %r" % (mine_verdict, prior_verdict))
    if prior_repro:
        print("ERROR republication check failed: %s" % json.dumps(prior_repro[:6],
                                                                  ensure_ascii=False))
        raise SystemExit("rankind-minus-ind does not reproduce r1947; refusing to publish")

    up_rows = upstream.get("rows") or []
    repro = rs2.reproduction_delta(raw["S0"], up_rows)
    if not repro["rows_match"]:
        print("ERROR reproduction failed: %s" % json.dumps(repro, ensure_ascii=False))
        raise SystemExit("S0 does not reproduce the upstream rows; refusing to publish a reading")

    primary = {sid: s["pairs"]["primary"] for sid, s in samples.items()}
    verdict = verdict_for(primary, "RESID_CONTROL")
    ind_verdict = verdict_for(mine, "IND_CONTROL")

    # descriptive: which control arm is actually stable across the samples?
    stability = {}
    for arm in ("resid", "ind"):
        annual = {sid: samples[sid]["arms"][arm]["annual"] for sid in samples}
        vals = [v for v in annual.values() if v is not None]
        stability[arm] = {
            "annual_by_sample": annual,
            "range_pp": (max(vals) - min(vals)) * 100.0 if len(vals) >= 2 else None,
            "own_t_by_sample": {sid: samples[sid]["arms"][arm]["t"] for sid in samples},
        }

    # descriptive: r1947's second prescription -- rankind's own absolute leg
    own_annual = {sid: samples[sid]["arms"]["rankind"]["annual"] for sid in samples}
    own_vals = [v for v in own_annual.values() if v is not None]
    own_level = {
        "annual_by_sample": own_annual,
        "positive_on_all_samples": bool(own_vals) and all(v > 0 for v in own_vals),
        "range_pp": (max(own_vals) - min(own_vals)) * 100.0 if len(own_vals) >= 2 else None,
        "role": "descriptive; r1947's option 2, not part of the verdict",
    }

    def _line(pair_blocks):
        return " | ".join(
            "%s %+.5f (t=%.2f, n=%d)" % (
                sid, pair_blocks[sid]["differential"]["summary"]["mean"] or 0.0,
                pair_blocks[sid]["differential"]["summary"]["t"] or 0.0,
                pair_blocks[sid]["n"])
            for sid in ("S0", "S1", "S2"))

    one_line = ("rankind-minus-resid across samples: %s -> %s; the ind control reproduces "
                "r1947 (%s) and its own stability spread is %.2fpp vs resid %.2fpp"
                % (_line(primary), verdict, prior_verdict,
                   stability["ind"]["range_pp"] or 0.0,
                   stability["resid"]["range_pp"] or 0.0))

    report = {
        "generated": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "evidence_cutoff": upstream.get("evidence_cutoff"),
        "machine": "bm-c",
        "kind": "census-derived",
        "prereg": None,
        "adoption": None,
        "question": ("does within-industry rank still add anything once the control is the "
                     "beta+size residual arm instead of the noisy industry-dummy arm?"),
        "row_producer": "scripts/astock_resid_industry_neutral.py::run (imported, not re-implemented)",
        "sampling": "scripts/astock_rankind_second_sample.py::run_sample (imported, not re-implemented)",
        "upstream": {
            "path": _rel(upstream_path),
            "sha256": stab.sha256_of(upstream_path),
            "generated": upstream.get("generated"),
            "kind": upstream.get("kind"),
            "rebalances": len(up_rows),
            "verdict": upstream.get("verdict"),
        },
        "prior": {
            "path": _rel(prior_path),
            "sha256": stab.sha256_of(prior_path),
            "generated": prior.get("generated"),
            "verdict": prior_verdict,
            "reproduction_problems": prior_repro,
        },
        "criteria": CRITERIA,
        "window": {
            "panel_symbols": len(symbols),
            "panel_dates": len(dates),
            "panel_first": dates[0] if len(dates) else None,
            "panel_last": dates[-1] if len(dates) else None,
            "hold_days": base.HOLD,
            "cost_one_side": base.COST_ONE_SIDE,
            "min_amount_20d": base.MIN_AMOUNT_20D,
        },
        "reproduction": repro,
        "samples": samples,
        "control_stability": stability,
        "rankind_own_level": own_level,
        "verdict": verdict,
        "ind_control_verdict": ind_verdict,
        "headline": {"verdict": verdict, "one_line": one_line},
        "boundaries": [
            "one panel, one calendar: alternates are different observation dates, not a second dataset",
            "S1 formation windows overlap S0; rows are not independent and no pooled t is claimed",
            "the control swap changes which arm is subtracted, never the rank arm or the maths",
            "control stability spread is descriptive; it is not a criterion and cannot flip the verdict",
            "unchanged upstream limits: ST/limit-up/limit-down and delisting unhandled, book is not tradable",
        ],
    }
    problems = identity_problems(samples)
    report["identity_check"] = {"problems": problems,
                               "rule": "mean(a-b) == mean(a) - mean(b) within 1e-9"}
    if problems:
        print("ERROR pair identity failed: %s" % json.dumps(problems[:6], ensure_ascii=False))
        raise SystemExit("a pair's mean does not equal its arms' mean difference")
    if keep_rows:
        report["rows"] = raw
    return report


# ------------------------------------------------------------------ check
VOLATILE = {"generated", "upstream", "prior", "samples", "identity_check"}


def _flat(obj, prefix=""):
    out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            if not prefix and k in VOLATILE:
                continue
            out.update(_flat(v, "%s.%s" % (prefix, k) if prefix else str(k)))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out.update(_flat(v, "%s[%d]" % (prefix, i), ))
    else:
        out[prefix] = obj
    return out


def check(out_path: str = OUT, upstream_path: str = UPSTREAM,
          prior_path: str = PRIOR) -> int:
    """Cheap external anchors only: a check leg must not pay for three panel passes.

    Verified here: the two upstream faces are byte-identical (else this face is one
    generation old), the prior pair's published cells are the ones this face printed,
    every holds flag agrees with its own mean/t, and the top verdict re-derives.
    S1/S2 rows are not re-derived -- that is stated in the output, not hidden.
    """
    if not os.path.exists(out_path):
        print("STALE face missing: %s" % _rel(out_path))
        return 3
    published = json.load(open(out_path, encoding="utf-8"))

    for which, path, key in (("upstream", upstream_path, "upstream"),
                             ("prior", prior_path, "prior")):
        if not os.path.exists(path):
            print("STALE %s face missing: %s" % (which, _rel(path)))
            return 3
        recorded = (published.get(key) or {}).get("sha256")
        live = stab.sha256_of(path)
        if recorded != live:
            print("STALE %s bytes changed (%s... -> %s...): re-run"
                  % (which, str(recorded)[:12], live[:12]))
            return 3

    upstream = json.load(open(upstream_path, encoding="utf-8"))
    if (published.get("reproduction") or {}).get("row_count") != len(upstream.get("rows") or []):
        print("STALE upstream rebalance count moved: re-run")
        return 3

    prior = json.load(open(prior_path, encoding="utf-8"))
    mine = {sid: (s.get("pairs") or {}).get("reproduction") or {}
            for sid, s in (published.get("samples") or {}).items()}
    prior_blocks = prior.get("samples") or {}
    problems = compare_snapshots(snapshot(mine), snapshot(prior_blocks), "rankind-minus-ind")
    want_ind = rs2.verdict_for(mine)
    if want_ind != (prior.get("verdict") or prior.get("headline", {}).get("verdict")):
        problems.append("published ind-pair verdict %r disagrees with the prior face"
                        % want_ind)

    for sid, block in (published.get("samples") or {}).items():
        for arm, pair in (("primary", PRIMARY), ("reproduction", REPRODUCTION_PAIR)):
            d = ((block.get("pairs") or {}).get(arm) or {})
            st = d.get("differential", {}).get("summary") or {}
            if d.get("n", 0) >= MIN_REBALANCES and d.get("holds") != (
                    (st.get("mean") or 0.0) > 0 and (st.get("t") or -9e9) >= T_FLOOR):
                problems.append("%s %s holds flag disagrees with its own mean/t" % (sid, arm))
            if (d.get("differential", {}).get("years_positive") or 0) > \
                    (d.get("differential", {}).get("years_total") or 0):
                problems.append("%s %s more positive years than years" % (sid, arm))
            p = d.get("differential", {}).get("signflip_p")
            if p is not None and not 0.0 <= p <= 1.0:
                problems.append("%s %s sign-flip p outside [0,1]" % (sid, arm))
    problems.extend(identity_problems(published.get("samples") or {}))

    primary = {sid: (s.get("pairs") or {}).get("primary") or {}
               for sid, s in (published.get("samples") or {}).items()}
    want = verdict_for(primary, "RESID_CONTROL")
    if published.get("verdict") != want:
        problems.append("verdict published=%r recomputed=%r" % (published.get("verdict"), want))
    if (published.get("headline") or {}).get("verdict") != want:
        problems.append("headline verdict disagrees with the recomputed verdict")

    flat = _flat(published)
    for key in ("criteria.holds", "criteria.primary_pair", "question",
                "control_stability.resid.annual_by_sample.S0",
                "rankind_own_level.positive_on_all_samples"):
        if key not in flat:
            problems.append("%s missing from the face" % key)
    if not (published.get("reproduction") or {}).get("rows_match"):
        problems.append("published face records a failed reproduction")

    if problems:
        print("CHECK FAILED: %d field(s) drift" % len(problems))
        for p in problems[:10]:
            print("  " + p)
        return 3
    print("CHECK OK %s | %d fields | upstream sha %s... | prior sha %s... | "
          "S1/S2 rows not re-derived here (three panel passes)" % (
              published["verdict"], len(flat),
              str(published["upstream"]["sha256"])[:12],
              str(published["prior"]["sha256"])[:12]))
    return 0


# ------------------------------------------------------------------ selftest
def selftest() -> int:
    legs = []

    rows = [
        {"date": "2021-01-04", Q1_KEY % "rankind": 0.020, Q1_KEY % "resid": 0.005,
         Q1_KEY % "ind": 0.010},
        {"date": "2021-02-01", Q1_KEY % "rankind": -0.010, Q1_KEY % "resid": -0.004,
         Q1_KEY % "ind": 0.000},
        {"date": "2021-03-01", Q1_KEY % "rankind": 0.030, Q1_KEY % "resid": 0.010,
         Q1_KEY % "ind": 0.010},
    ]
    pr = differential(rows, *PRIMARY)
    legs.append(("primary differential subtracts resid, date for date",
                 [round(v, 12) for _, v in pr] == [0.015, -0.006, 0.020]))
    rp = differential(rows, *REPRODUCTION_PAIR)
    legs.append(("reproduction differential subtracts ind, date for date",
                 [round(v, 12) for _, v in rp] == [0.010, -0.010, 0.020]))

    missing = False
    try:
        differential([{"date": "2021-01-04", Q1_KEY % "rankind": 0.02}], *PRIMARY)
    except KeyError:
        missing = True
    legs.append(("a rebalance without the control leg is an error, not a skip", missing))

    a = arm_stats(rows, "rankind")
    b = arm_stats(rows, "resid")
    diff_mean = sum(v for _, v in pr) / len(pr)
    legs.append(("pair mean equals arms' mean difference",
                 abs(diff_mean - (a["mean"] - b["mean"])) < 1e-12))
    legs.append(("arm_stats reports the own-level annual, not the differential",
                 abs(a["annual"] - base.compound([0.02, -0.01, 0.03])) < 1e-12))

    good = {"n": 40, "differential": {"summary": {"mean": 0.004, "t": 1.6}}}
    weak = {"n": 40, "differential": {"summary": {"mean": 0.004, "t": 1.4}}}
    wrong = {"n": 40, "differential": {"summary": {"mean": -0.004, "t": -1.6}}}
    short = {"n": 8, "differential": {"summary": {"mean": 0.01, "t": 3.0}}}
    legs.append(("holds needs sign, t floor and enough rows",
                 holds(good) and not holds(weak) and not holds(wrong) and not holds(short)))

    three = {"id": "x", "offset": 0, "stride": 20,
             "differential": {"summary": {"mean": 0.004, "t": 1.6}}}
    legs.append(("holds accepts a short-n block only when n is the only fault",
                 not holds(dict(three, n=11))))

    def blocks(s1, s2):
        return {"S1": dict(s1, id="S1"), "S2": dict(s2, id="S2")}

    legs.append(("verdict names the swapped control: both hold",
                 verdict_for(blocks(good, good), "RESID_CONTROL")
                 == "RESID_CONTROL_HOLDS_ON_BOTH_ALTERNATE_SAMPLES"))
    legs.append(("verdict names the swapped control: one holds",
                 verdict_for(blocks(good, weak), "RESID_CONTROL")
                 == "RESID_CONTROL_HOLDS_ON_ONE_SAMPLE_ONLY"))
    legs.append(("verdict names the swapped control: neither holds",
                 verdict_for(blocks(weak, wrong), "RESID_CONTROL")
                 == "RESID_CONTROL_DOES_NOT_HOLD"))
    legs.append(("verdict: short sample outranks the rest",
                 verdict_for(blocks(good, good) | {"S1": dict(good, id="S1", n=5)},
                             "RESID_CONTROL") == "RESID_CONTROL_NOT_ENOUGH_REBALANCES"))

    mine = {"S0": {"n": 77, "mean": 0.003, "t": 1.9, "holds": True}}
    same = {"S0": {"n": 77, "mean": 0.003, "t": 1.9, "holds": True}}
    moved = {"S0": {"n": 77, "mean": 0.003, "t": 1.9 - 1e-6, "holds": True}}
    flipped = {"S0": {"n": 77, "mean": 0.003, "t": 1.9, "holds": False}}
    legs.append(("snapshot comparison accepts identical cells",
                 compare_snapshots(mine, same, "p") == []))
    legs.append(("snapshot comparison catches a one-in-a-million t drift",
                 compare_snapshots(mine, moved, "p") != []))
    legs.append(("snapshot comparison catches a flipped holds flag",
                 compare_snapshots(mine, flipped, "p") != []))
    legs.append(("snapshot comparison catches a missing sample",
                 compare_snapshots(mine, {}, "p") != []))

    ok_samples = {"S0": {"arms": {"rankind": {"mean": 0.03}, "resid": {"mean": 0.01}},
                         "pairs": {"primary": {"differential": {"summary": {"mean": 0.02}}}}}}
    bad_samples = {"S0": {"arms": {"rankind": {"mean": 0.03}, "resid": {"mean": 0.01}},
                          "pairs": {"primary": {"differential": {"summary": {"mean": 0.03}}}}}}
    legs.append(("identity check accepts a consistent pair", identity_problems(ok_samples) == []))
    legs.append(("identity check catches a differential that is not its arms' difference",
                 identity_problems(bad_samples) != []))

    # check must be shown failing, or it is only a promise
    import contextlib
    import io as _io
    import shutil
    import tempfile

    tmpdir = tempfile.mkdtemp(prefix="_r1950bmc_swap_")
    out = os.path.join(tmpdir, "out.json")
    up = os.path.join(tmpdir, "up.json")
    pr_path = os.path.join(tmpdir, "prior.json")
    shutil.copyfile(UPSTREAM, up)
    shutil.copyfile(PRIOR, pr_path)
    face = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else None
    rc_missing = rc_clean = rc_stale_up = rc_stale_prior = rc_fail = rc_identity = None
    text_stale = text_fail = text_identity = ""
    try:
        with contextlib.redirect_stdout(_io.StringIO()):
            rc_missing = check(out, up, pr_path)

        if face is not None:
            with open(out, "w", encoding="utf-8") as fh:
                json.dump(face, fh)
            with contextlib.redirect_stdout(_io.StringIO()):
                rc_clean = check(out, up, pr_path)

            with open(up, "ab") as fh:
                fh.write(b"\n")
            buf = _io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc_stale_up = check(out, up, pr_path)
            text_stale = buf.getvalue()
            shutil.copyfile(UPSTREAM, up)

            with open(pr_path, "ab") as fh:
                fh.write(b"\n")
            with contextlib.redirect_stdout(_io.StringIO()):
                rc_stale_prior = check(out, up, pr_path)
            shutil.copyfile(PRIOR, pr_path)

            broken = json.loads(json.dumps(face))
            broken["verdict"] = ("RESID_CONTROL_DOES_NOT_HOLD"
                                 if face["verdict"] != "RESID_CONTROL_DOES_NOT_HOLD"
                                 else "RESID_CONTROL_HOLDS_ON_BOTH_ALTERNATE_SAMPLES")
            with open(out, "w", encoding="utf-8") as fh:
                json.dump(broken, fh)
            buf = _io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc_fail = check(out, up, pr_path)
            text_fail = buf.getvalue()

            bad = json.loads(json.dumps(face))
            sid = sorted(bad["samples"])[0]
            arm = (bad["samples"][sid]["arms"] or {}).get("resid")
            if arm is not None and arm.get("mean") is not None:
                arm["mean"] = arm["mean"] + 0.001
            with open(out, "w", encoding="utf-8") as fh:
                json.dump(bad, fh)
            buf = _io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc_identity = check(out, up, pr_path)
            text_identity = buf.getvalue()
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

    legs.append(("a missing face reads STALE, not clean", rc_missing == 3))
    if face is not None:
        legs.append(("identical bytes re-derive clean", rc_clean == 0))
        legs.append(("one byte of upstream drift reads STALE, not clean",
                     rc_stale_up == 3 and "STALE" in text_stale))
        legs.append(("one byte of prior-face drift reads STALE, not clean",
                     rc_stale_prior == 3))
        legs.append(("a flipped verdict reads CHECK FAILED without STALE",
                     rc_fail == 3 and "CHECK FAILED" in text_fail and "STALE" not in text_fail))
        legs.append(("a drifted arm mean reads CHECK FAILED without STALE",
                     rc_identity == 3 and "CHECK FAILED" in text_identity
                     and "STALE" not in text_identity))

    ok = sum(1 for _, good_leg in legs if good_leg)
    for name, good_leg in legs:
        print("%s %s" % ("PASS" if good_leg else "FAIL", name))
    print("selftest %d/%d %s" % (ok, len(legs), "PASS" if ok == len(legs) else "FAIL"))
    return 0 if ok == len(legs) else 3


# ------------------------------------------------------------------ main
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cmd", choices=["run", "check", "selftest"], nargs="?", default="run")
    ap.add_argument("--out", default=OUT)
    args = ap.parse_args(argv)

    if args.cmd == "selftest":
        return selftest()
    if args.cmd == "check":
        return check(args.out)

    upstream = json.load(open(UPSTREAM, encoding="utf-8"))
    report = build_report(upstream)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    print(report["headline"]["one_line"])
    for sid in ("S0", "S1", "S2"):
        s = report["samples"][sid]
        for arm in ("primary", "reproduction"):
            b = s["pairs"][arm]
            d = b["differential"]
            print("%s %-12s n=%3d %s..%s mean %+.5f t=%5.2f p=%.3f years %d/%d holds=%s"
                  % (sid, arm, b["n"], b["first"], b["last"], d["summary"]["mean"],
                     d["summary"]["t"] or 0.0,
                     d["signflip_p"] if d["signflip_p"] is not None else float("nan"),
                     d["years_positive"], d["years_total"], b["holds"]))
        print("   arms annual: rankind %+.4f resid %+.4f ind %+.4f"
              % (s["arms"]["rankind"]["annual"], s["arms"]["resid"]["annual"],
                 s["arms"]["ind"]["annual"]))
    print("reproduction max|delta| = %s over %d rows; prior-face cells match"
          % (report["reproduction"]["max_abs_delta"], report["reproduction"]["row_count"]))
    print("-> %s" % _rel(args.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
