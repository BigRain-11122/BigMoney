#!/usr/bin/env python3
"""E244 -- if the rest channel is not one channel, WHICH counterparties carry it?

E243 answered "does additivity survive out of sample" with NO, and its own per-pair rows carry
the next question: 9 of 20 ordered pairs in the headline cell exclude zero, in mixed signs. A
mixed-sign set is three different objects:

  * a few counterparties that genuinely pay differently (a NAMED carrier),
  * one cell's sampling noise seen through twenty windows,
  * two quantities wearing one name (the E239 family failure).

This face reads E243's published per-pair intervals (machine-read from addos_latest.json, never
transcribed -- the r1265 law) and asks where the heterogeneity lives: on the COUNTERPARTY
identity (`one_of`, the single name the difference is measured against), on the OWN identity
(`own_of`, whose return is being explained), or in pair idiosyncrasy that repeats nowhere.

Orientation, pinned by a selftest leg: diff = b_one - b_rest3, so a POSITIVE difference means the
sum of the remaining members pays more than the singled counterparty does.

NO BILL, NO ADOPTION, NO RE-PRICING. The face classifies where a published spread sits.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e222_tom_overlay as e222  # noqa: E402
import e243_additivity_out_of_sample as e243  # noqa: E402

ROOT = e222.ROOT
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
SOURCE_FACE = os.path.join("results", "state_tilt", "addos_latest.json")
STUDY = "E244"

COUNTED_KINDS = ("headline", "window", "era", "neighbour")
CARRIER_MIN_DECISIVE = 2      # frozen: one decisive cell is a false positive at 95%, not a pattern
CARRIER_MIN_SHARE = 0.50      # frozen: a carrier must be decisive in half of its cells
CARRIER_MIN_ABS_MEAN = 0.30   # frozen: half of E243's own 0.60 resolution scale

VERDICTS = ("one_member_pays_differently_the_others_are_its_mirror",
            "two_members_pay_differently",
            "several_members_pay_differently",
            "no_repeatable_counterparty_effect",
            "unresolved_pairs_too_few")
MIRROR_RATIO_MIN = 1.5   # frozen: the deviant's own reading must be 1.5x the mirror it casts


# ---------------------------------------------------------------- reading the previous face
def load_face(path=None):
    p = path if path is not None else os.path.join(ROOT, SOURCE_FACE)
    if not os.path.exists(p):
        return None, None
    with open(p, encoding="utf-8") as fh:
        raw = fh.read()
    return json.loads(raw), hashlib.sha256(raw.encode("utf-8")).hexdigest()


def pair_rows(face):
    """One row per (cell, own_of, one_of) that published an interval."""
    rows = []
    for cell in face.get("cells") or []:
        if not cell.get("decided") or cell.get("kind") not in COUNTED_KINDS:
            continue
        for p in cell.get("per_pair_diffs") or []:
            ci = p.get("ci")
            if p.get("diff") is None or not ci:
                continue
            decisive = not (ci[0] <= 0.0 <= ci[1])
            rows.append({"cell": cell.get("label"),
                         "kind": cell.get("kind"),
                         "own_of": p.get("own_of"),
                         "one_of": p.get("one_of"),
                         "diff": float(p["diff"]),
                         "ci": [float(ci[0]), float(ci[1])],
                         "halfwidth": (float(ci[1]) - float(ci[0])) / 2.0,
                         "decisive": decisive,
                         "sign": 1 if p["diff"] > 0 else -1})
    return rows


def _by(rows, key):
    out = {}
    for r in rows:
        out.setdefault(r[key], []).append(r)
    return out


def _stat_block(bucket, label):
    """Per-identity statistics.

    `decisive_share` is measured over the PAIRS that identity appears in, and `cell_share` over
    its CELLS -- the two differ because a leave-one-out cell holds fewer pairs, and quoting either
    alone would let one wide cell outvote nine narrow ones.
    """
    diffs = [r["diff"] for r in bucket]
    dec = [r for r in bucket if r["decisive"]]
    cells = sorted({r["cell"] for r in bucket})
    cells_with_decisive = sorted({r["cell"] for r in dec})
    signs = sorted({r["sign"] for r in dec})
    return {"name": label,
            "pairs": len(bucket),
            "cells": len(cells),
            "cells_with_decisive": len(cells_with_decisive),
            "decisive_pairs": len(dec),
            "decisive_share": (len(dec) / float(len(bucket))) if bucket else 0.0,
            "cell_share": (len(cells_with_decisive) / float(len(cells))) if cells else 0.0,
            "mean_diff": (sum(diffs) / len(diffs)) if diffs else None,
            "mean_diff_decisive": (sum(r["diff"] for r in dec) / len(dec)) if dec else None,
            "decisive_signs": signs,
            "sign_consistent": len(signs) == 1 and bool(dec),
            "cell_labels_with_decisive": cells_with_decisive}


def counterparty_stats(rows):
    return [_stat_block(b, k) for k, b in sorted(_by(rows, "one_of").items())]


def own_stats(rows):
    return [_stat_block(b, k) for k, b in sorted(_by(rows, "own_of").items())]


def variance_split(rows):
    """Descriptive two-way split of the published differences (unbalanced, so shares are eta^2).

    Exact for a balanced grid; published as DESCRIPTIVE for this unbalanced one, and the residual
    share is printed so a reader can see how much is pair idiosyncrasy rather than identity.
    """
    n = len(rows)
    if n == 0:
        return {"rows": 0}
    grand = sum(r["diff"] for r in rows) / n
    own = {k: sum(r["diff"] for r in b) / len(b) for k, b in _by(rows, "own_of").items()}
    one = {k: sum(r["diff"] for r in b) / len(b) for k, b in _by(rows, "one_of").items()}
    sst = sum((r["diff"] - grand) ** 2 for r in rows)
    ss_own = sum(len(b) * (own[k] - grand) ** 2 for k, b in _by(rows, "own_of").items())
    ss_one = sum(len(b) * (one[k] - grand) ** 2 for k, b in _by(rows, "one_of").items())
    ss_resid = sum((r["diff"] - own[r["own_of"]] - one[r["one_of"]] + grand) ** 2 for r in rows)
    return {"rows": n,
            "grand_mean": grand,
            "ss_total": sst,
            "ss_own": ss_own,
            "ss_counterparty": ss_one,
            "ss_residual": ss_resid,
            "share_own": (ss_own / sst) if sst else None,
            "share_counterparty": (ss_one / sst) if sst else None,
            "share_residual": (ss_resid / sst) if sst else None,
            "cell_means": {k: (sum(r["diff"] for r in b) / len(b))
                           for k, b in sorted(_by(rows, "cell").items())},
            "note": "unbalanced grid: eta^2-style shares, descriptive only; the two main effects "
                    "are not orthogonal here"}


def carriers(stats):
    """An identity carries the channel only if it repeats: decisive in half its cells, one sign,
    and a mean difference of at least half the resolution scale."""
    out = []
    for s in stats:
        if s["decisive_pairs"] < CARRIER_MIN_DECISIVE:
            continue
        if s["cell_share"] < CARRIER_MIN_SHARE or not s["sign_consistent"]:
            continue
        mean = s["mean_diff_decisive"]
        if mean is None or abs(mean) < CARRIER_MIN_ABS_MEAN:
            continue
        out.append({"name": s["name"], "sign": s["decisive_signs"][0],
                    "mean_diff_decisive": mean,
                    "decisive_pairs": s["decisive_pairs"],
                    "cell_share": s["cell_share"],
                    "cells": s["cell_labels_with_decisive"]})
    return sorted(out, key=lambda c: (-abs(c["mean_diff_decisive"]), c["name"]))


def classify(car, stats, rows):
    """Both signs are not automatically two channels.

    A member that pays more than the rest produces a POSITIVE difference when it is the singled
    counterparty and a NEGATIVE one for every ordinary member, because the deviant sits inside the
    sum that the ordinary member is priced against. That mirror is the signature of ONE deviant,
    so the sign count alone cannot tell one deviant from several -- the arithmetic leg below pins
    that on a fixture. A split is called only when BOTH sides carry more than one repeatable name.
    """
    if len(rows) < 6:
        return "unresolved_pairs_too_few"
    pos = [c for c in car if c["sign"] > 0]
    neg = [c for c in car if c["sign"] < 0]
    if not car:
        return ("no_repeatable_counterparty_effect"
                if any(s["decisive_pairs"] for s in stats) else "unresolved_pairs_too_few")
    if len(pos) == 1 and len(neg) >= 2:
        neg_mean = sum(abs(n["mean_diff_decisive"]) for n in neg) / len(neg)
        ratio = abs(pos[0]["mean_diff_decisive"]) / neg_mean if neg_mean else None
        if ratio is not None and ratio >= MIRROR_RATIO_MIN:
            return "one_member_pays_differently_the_others_are_its_mirror"
        return "several_members_pay_differently"
    if len(pos) >= 2 or len(neg) >= 2:
        return "several_members_pay_differently"
    return "two_members_pay_differently"


def mirror_ratio(car):
    pos = [c for c in car if c["sign"] > 0]
    neg = [c for c in car if c["sign"] < 0]
    if len(pos) != 1 or not neg:
        return None
    neg_mean = sum(abs(n["mean_diff_decisive"]) for n in neg) / len(neg)
    return (abs(pos[0]["mean_diff_decisive"]) / neg_mean) if neg_mean else None


def run(save=True, face=None, source_path=None, outdir=None):
    outdir = outdir or OUTDIR
    src, src_sha = (face, None) if face is not None else load_face(source_path)
    if not src:
        return {"study": STUDY,
                "error": "source face results/state_tilt/addos_latest.json is missing",
                "verdict": "unresolved_pairs_too_few"}
    rows = pair_rows(src)
    cstats = counterparty_stats(rows)
    ostats = own_stats(rows)
    vs = variance_split(rows)
    car = carriers(cstats)
    verdict = classify(car, cstats, rows)
    overlap = _overlap(src)

    out = {
        "study": STUDY,
        "title": "if the rest channel is not one channel, which counterparties carry it?",
        "generated": datetime.now().isoformat(timespec="seconds"),
        "evidence_cutoff": src.get("evidence_cutoff"),
        "source_face": {"path": SOURCE_FACE, "sha256": src_sha,
                        "verdict": (src.get("rollup") or {}).get("verdict"),
                        "note": "machine-read; this face writes its own file and never the source"},
        "frozen_spec": {
            "question": "E243 published 9 of 20 ordered pairs excluding zero with mixed signs on "
                        "its headline cell. Does the heterogeneity sit on the counterparty "
                        "identity, on the own identity, or on neither?",
            "input": "E243's published per-pair intervals (cells of kind headline/window/era/"
                     "neighbour; degenerate k=3 cells excluded)",
            "orientation": "diff = b_one - b_rest3; POSITIVE means the sum of the remaining "
                           "members pays more than the singled counterparty",
            "carrier_rule": {"min_decisive_pairs": CARRIER_MIN_DECISIVE,
                             "min_cell_share": CARRIER_MIN_SHARE,
                             "min_abs_mean_diff": CARRIER_MIN_ABS_MEAN,
                             "sign_consistency": "required -- a carrier that flips sign across "
                                                 "cells is not a carrier"},
            "verdict_vocabulary": list(VERDICTS),
            "independence": "the cells overlap in time; cross-cell counts are NOT independent "
                            "observations and are published as repeats, not as replications",
        },
        "rows": len(rows),
        "counterparty_stats": cstats,
        "own_stats": ostats,
        "variance_split": vs,
        "carriers": car,
        "mirror": {"ratio": mirror_ratio(car), "floor": MIRROR_RATIO_MIN,
                   "reading": "the positive member's own reading over the mean absolute reading "
                              "of the negative set; a member that pays more than the rest casts "
                              "a negative mirror on every ordinary member because it sits inside "
                              "the sum they are priced against"},
        "overlap": overlap,
        "verdict": verdict,
        "no_bill": {"permitted": False,
                    "reason": "classification of a published spread; any charge or configuration "
                              "change is a separate pre-registered act"},
    }
    out["summary"] = _summary(out)
    if save:
        _write(out, outdir)
    return out


def _overlap(src):
    """How much of the cross-cell count is the same sessions counted twice."""
    spans = []
    for c in src.get("cells") or []:
        if c.get("decided") and c.get("kind") in COUNTED_KINDS:
            spans.append((c.get("label"), c.get("first"), c.get("last"), c.get("sessions")))
    headline = next((s for s in spans if s[0] == "all_five"), None)
    contained = [s[0] for s in spans
                 if headline and s[1] and headline[1] and headline[1] <= s[1]
                 and headline[2] and s[2] and s[2] <= headline[2]]
    return {"cells": len(spans),
            "cell_spans": [{"cell": s[0], "first": s[1], "last": s[2], "sessions": s[3]}
                           for s in spans],
            "cells_inside_headline_window": contained,
            "independent_observations": False,
            "note": "era and leave-one-out cells are subsets of the headline window; the pair "
                    "counts measure REPEAT, not independent replication"}


def _summary(out):
    car = out["carriers"]
    return {"verdict": out["verdict"],
            "carriers": [{"name": c["name"], "sign": c["sign"],
                          "mean_diff_decisive": round(c["mean_diff_decisive"], 4),
                          "decisive_pairs": c["decisive_pairs"],
                          "cells": len(c["cells"])} for c in car],
            "positive_carriers": [c["name"] for c in car if c["sign"] > 0],
            "negative_carriers": [c["name"] for c in car if c["sign"] < 0],
            "mirror_ratio": out["mirror"]["ratio"],
            "rows": out["rows"],
            "share_counterparty": out["variance_split"].get("share_counterparty"),
            "share_own": out["variance_split"].get("share_own"),
            "share_residual": out["variance_split"].get("share_residual"),
            "one_line": _answer(out)}


def _answer(out):
    v = out["verdict"]
    car = out["carriers"]
    vs = out["variance_split"]
    pos = [c for c in car if c["sign"] > 0]
    neg = [c for c in car if c["sign"] < 0]
    share = ("counterparty identity %.0f%% / own identity %.0f%% / residual %.0f%%"
             % (100 * (vs.get("share_counterparty") or 0.0),
                100 * (vs.get("share_own") or 0.0),
                100 * (vs.get("share_residual") or 0.0)))
    if v == "one_member_pays_differently_the_others_are_its_mirror":
        return ("the spread is ONE member: %s reads %+.2f when it is the singled counterparty, "
                "and every ordinary member (n=%d) reads its mirror at %.2fx smaller magnitude -- "
                "because the deviant sits inside the sum they are priced against. There is no "
                "'rest channel' to be additive about; variance %s"
                % (pos[0]["name"], pos[0]["mean_diff_decisive"], len(neg),
                   out["mirror"]["ratio"] or 0.0, share))
    if v == "two_members_pay_differently":
        return ("two counterparties carry the spread (%s); variance %s"
                % (", ".join(c["name"] for c in car), share))
    if v == "several_members_pay_differently":
        return ("several counterparties carry the spread in both directions (positive %s / "
                "negative %s); variance %s"
                % (", ".join(c["name"] for c in pos), ", ".join(c["name"] for c in neg), share))
    if v == "no_repeatable_counterparty_effect":
        return ("no counterparty repeats: pairs exclude zero in different cells with no stable "
                "sign, variance %s -- the spread is pair idiosyncrasy, not a named channel"
                % share)
    return "too few decided pairs to classify where the spread sits"


def _write(out, outdir):
    os.makedirs(outdir, exist_ok=True)
    cutoff = out.get("evidence_cutoff") or "unknown"
    name = "PAIRHET-" + str(cutoff) + ".json"
    for fn in (name, "pairhet_latest.json"):
        with open(os.path.join(outdir, fn), "w", encoding="utf-8") as fh:
            json.dump(out, fh, ensure_ascii=False, indent=1)
    return name


# ---------------------------------------------------------------- selftest
def _synth(stars, own=0.5, base_rest=0.02, n=900, seed=7, noise=0.6):
    """Book where `stars` is a {member: coefficient} map for the singled-out channel.

    Every non-star member pays `base_rest` on the summed channel, so the diff for the pair
    (m, star) reads (stars[star] - base_rest) * (1 + eta) and the pairs among non-stars read ~0.
    """
    import random
    rnd = random.Random(seed)
    syms = ["syn%d" % i for i in range(5)]
    labels = e243._dates(n, "2019-01-01")
    lo = {s: 18.0 for s in syms}
    rows = {s: [] for s in syms}
    for t in range(n):
        dl = {s: rnd.gauss(0.0, 1.0) for s in syms}
        for s in syms:
            lo[s] += dl[s]
        for s in syms:
            others = [o for o in syms if o != s]
            y = own * dl[s]
            for o in others:
                y += stars.get(o, base_rest) * dl[o]
            rows[s].append((labels[t], y + rnd.gauss(0.0, noise), lo[s]))
    return {s: {r[0]: (r[1], r[2]) for r in rows[s]} for s in syms}


def _face_for(per):
    """Reuse E243's grid so the fixtures ride the same eleven cells the real face has."""
    return e243.run(save=False, per=per, basket=sorted(per))


def selftest():
    legs = []

    def leg(name, fn):
        try:
            fn()
            legs.append((name, True, ""))
        except AssertionError as exc:
            legs.append((name, False, str(exc)))

    def one_carrier_is_named():
        face = _face_for(_synth({"syn0": 0.9}))
        out = run(save=False, face=face)
        if out["verdict"] != "one_member_pays_differently_the_others_are_its_mirror":
            raise AssertionError("single-star fixture read as %s" % out["verdict"])
        pos = [c["name"] for c in out["carriers"] if c["sign"] > 0]
        if pos != ["syn0"]:
            raise AssertionError("positive carrier set %s (expected ['syn0'])" % pos)
        if len([c for c in out["carriers"] if c["sign"] < 0]) < 2:
            raise AssertionError("no mirror cast on the ordinary members")

    def mirror_arithmetic_is_pinned():
        """The mirror is arithmetic, not a second channel: make it explicit on the fixture."""
        face = _face_for(_synth({"syn0": 0.9}))
        out = run(save=False, face=face)
        r = out["mirror"]["ratio"]
        if r is None or r < MIRROR_RATIO_MIN:
            raise AssertionError("mirror ratio %s is under the frozen floor %.2f"
                                 % (r, MIRROR_RATIO_MIN))
        rows = pair_rows(face)
        # The deviant can only sit in ONE of three roles: own, counterparty, or inside the SUM.
        # The mirror is the third role, so the positive-decisive mass must be overwhelmingly on
        # pairs where the deviant IS the counterparty. Small-sample stragglers elsewhere are
        # possible (a 4-member cell's sum arithmetic differs) and are counted, not denied.
        on_dev = [r_ for r_ in rows if r_["decisive"] and r_["diff"] > 0
                  and r_["one_of"] == "syn0"]
        elsewhere = [r_ for r_ in rows if r_["decisive"] and r_["diff"] > 0
                     and r_["one_of"] != "syn0"]
        if len(on_dev) < 5:
            raise AssertionError("only %d positive-decisive pairs on the deviant" % len(on_dev))
        if len(elsewhere) * 5 > len(on_dev):
            raise AssertionError("%d positive-decisive pairs off the deviant against %d on it -- "
                                 "the spread is not carried by one member"
                                 % (len(elsewhere), len(on_dev)))
        if any(c["sign"] > 0 and c["name"] != "syn0" for c in out["carriers"]):
            raise AssertionError("a non-deviant was named a positive carrier")

    def orientation_is_pinned():
        """A star that pays MORE than the rest must read NEGATIVE (diff = one - rest)."""
        face = _face_for(_synth({"syn0": 0.02}, base_rest=0.6))
        out = run(save=False, face=face)
        if not out["carriers"]:
            raise AssertionError("a 0.58 truth gap produced no carrier")
        if out["carriers"][0]["sign"] >= 0:
            raise AssertionError("orientation inverted: a star paying less than the rest read "
                                 "with a positive difference")

    def symmetric_book_has_no_carrier():
        face = _face_for(_synth({}, base_rest=0.3))
        out = run(save=False, face=face)
        if out["verdict"] != "no_repeatable_counterparty_effect":
            raise AssertionError("symmetric book read as %s" % out["verdict"])
        if out["carriers"]:
            raise AssertionError("named carriers on a symmetric book: %s"
                                 % [c["name"] for c in out["carriers"]])

    def two_deviants_are_not_a_mirror():
        face = _face_for(_synth({"syn0": 0.9, "syn1": 0.8}))
        out = run(save=False, face=face)
        if out["verdict"] != "several_members_pay_differently":
            raise AssertionError("two deviants read as %s" % out["verdict"])
        pos = [c["name"] for c in out["carriers"] if c["sign"] > 0]
        if len(pos) < 2:
            raise AssertionError("only %s named on the positive side" % pos)

    def counterparty_dimension_dominates():
        """On a one-carrier book the counterparty identity must own the variance, not own_of."""
        face = _face_for(_synth({"syn0": 0.9}))
        out = run(save=False, face=face)
        vs = out["variance_split"]
        if (vs.get("share_counterparty") or 0.0) <= (vs.get("share_own") or 0.0):
            raise AssertionError("counterparty share %.3f <= own share %.3f on a one-carrier book"
                                 % (vs.get("share_counterparty") or 0.0,
                                    vs.get("share_own") or 0.0))

    def carrier_repeats_across_cells():
        face = _face_for(_synth({"syn0": 0.9}))
        out = run(save=False, face=face)
        for c in out["carriers"]:
            if len(c["cells"]) < 2:
                raise AssertionError("carrier %s stands on %d cell(s) -- not a repeat"
                                     % (c["name"], len(c["cells"])))
            if c["cell_share"] < CARRIER_MIN_SHARE:
                raise AssertionError("carrier %s has cell share %.2f under the frozen floor"
                                     % (c["name"], c["cell_share"]))

    def degenerate_cells_are_excluded():
        face = _face_for(_synth({"syn0": 0.9}))
        out = run(save=False, face=face)
        kinds = {r["kind"] for r in pair_rows(face)}
        if "degenerate" in kinds:
            raise AssertionError("a degenerate k=3 cell entered the row set")
        deg = [c for c in face["cells"] if c.get("kind") == "degenerate"]
        if not deg:
            raise AssertionError("fixture has no degenerate cell to exclude -- gate untested")

    def rows_are_unique():
        face = _face_for(_synth({"syn0": 0.9}))
        rows = pair_rows(face)
        keys = [(r["cell"], r["own_of"], r["one_of"]) for r in rows]
        if len(keys) != len(set(keys)):
            raise AssertionError("duplicate (cell, own, counterparty) rows")

    def empty_face_does_not_crash():
        out = run(save=False, face={"cells": []})
        if out["verdict"] != "unresolved_pairs_too_few":
            raise AssertionError("an empty face read as %s" % out["verdict"])

    def missing_source_is_reported():
        out = run(save=False, source_path=os.path.join(ROOT, "results", "_no_such_face.json"))
        if not out.get("error"):
            raise AssertionError("a missing source face was not reported")

    def no_bill_is_denied():
        out = run(save=False, face=_face_for(_synth({"syn0": 0.9})))
        if (out.get("no_bill") or {}).get("permitted") is not False:
            raise AssertionError("the classification granted a charge")

    def verdict_outside_vocabulary_never_prints():
        out = run(save=False, face=_face_for(_synth({"syn0": 0.9, "syn1": -0.6})))
        if out["verdict"] not in VERDICTS:
            raise AssertionError("verdict %s outside the frozen vocabulary" % out["verdict"])

    def overlap_is_published():
        out = run(save=False, face=_face_for(_synth({"syn0": 0.9})))
        ov = out["overlap"]
        if ov["cells"] < 3 or not ov["cells_inside_headline_window"]:
            raise AssertionError("overlap block did not name the contained cells")
        if ov["independent_observations"] is not False:
            raise AssertionError("overlapping cells were published as independent observations")

    def sign_flip_is_not_a_carrier():
        """A counterparty that pays more in one era and less in another must NOT be named."""
        import random
        rnd = random.Random(5)
        n = 1400
        syms = ["syn%d" % i for i in range(5)]
        labels = e243._dates(n, "2019-01-01")
        cut = n // 2
        lo = {s: 18.0 for s in syms}
        rows = {s: [] for s in syms}
        for t in range(n):
            dl = {s: rnd.gauss(0.0, 1.0) for s in syms}
            for s in syms:
                lo[s] += dl[s]
            star = 0.9 if t < cut else -0.6
            for s in syms:
                others = [o for o in syms if o != s]
                y = 0.5 * dl[s]
                for o in others:
                    y += (star if o == "syn0" else 0.02) * dl[o]
                rows[s].append((labels[t], y + rnd.gauss(0.0, 0.6), lo[s]))
        per = {s: {r[0]: (r[1], r[2]) for r in rows[s]} for s in syms}
        out = run(save=False, face=_face_for(per))
        if any(c["name"] == "syn0" and c["cell_share"] >= CARRIER_MIN_SHARE
               for c in out["carriers"]):
            raise AssertionError("a counterparty whose sign flips across eras was named a carrier")

    for name, fn in (("one counterparty is named", one_carrier_is_named),
                     ("mirror is arithmetic, not a channel", mirror_arithmetic_is_pinned),
                     ("orientation diff = one - rest", orientation_is_pinned),
                     ("symmetric book names no carrier", symmetric_book_has_no_carrier),
                     ("two deviants are not a mirror", two_deviants_are_not_a_mirror),
                     ("counterparty dimension dominates", counterparty_dimension_dominates),
                     ("carrier repeats across cells", carrier_repeats_across_cells),
                     ("degenerate cells excluded", degenerate_cells_are_excluded),
                     ("rows are unique", rows_are_unique),
                     ("empty face does not crash", empty_face_does_not_crash),
                     ("missing source is reported", missing_source_is_reported),
                     ("no bill is denied", no_bill_is_denied),
                     ("verdict stays in the vocabulary", verdict_outside_vocabulary_never_prints),
                     ("overlap is published", overlap_is_published),
                     ("a sign flip is not a carrier", sign_flip_is_not_a_carrier)):
        leg(name, fn)

    passed = sum(1 for _, ok, _ in legs if ok)
    print("E244 pair-heterogeneity selftest")
    for name, ok, why in legs:
        print("  %-44s %s%s" % (name, "PASS" if ok else "FAIL",
                                "" if ok else "  <- " + why))
    print("Summary: %d/%d" % (passed, len(legs)))
    return passed == len(legs)


def main(argv=None):
    ap = argparse.ArgumentParser(description="E244 which counterparties carry the rest channel")
    ap.add_argument("cmd", nargs="?", default="run", choices=("run", "selftest"))
    ap.add_argument("--outdir", default=None)
    args = ap.parse_args(argv)
    if args.cmd == "selftest":
        return 0 if selftest() else 1
    out = run(outdir=args.outdir)
    if out.get("error"):
        print(out["error"])
        return 2
    print(out["summary"]["one_line"])
    return 0


if __name__ == "__main__":
    sys.exit(main())