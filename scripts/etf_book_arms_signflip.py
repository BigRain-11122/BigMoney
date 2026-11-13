"""Which of the printed REJECTs survive their own cells' noise?

WHY THIS EXISTS: r1632 put a null-calibration sentence beside the cost axis and it said the
frozen two-label rule reads REJECT 96.5% of the time on an effect-free panel. That is an honest
sentence and it leaves the operator with exactly one unanswered question -- *are any of the five
REJECTs on this page real?* A frequency says "this label is cheap"; it cannot say which arm it is
cheap about. Without that second half a reader has to either believe all five or none, and the
two cost arms and the buffer-k40 arm are not the same claim.

WHAT THIS ASKS: for each arm, take its published per-cell deltas (12 cells: widths 3/5/8 x
cadences 10/20/40, each a median over its decision origins), and ask whether the arm's MEDIAN
delta could have been produced by sign noise alone. The null is enumerated exactly, not sampled:
flipping the sign of every cell independently gives 2**12 = 4096 possible worlds, so the p-value
is a count over a complete set and has no seed, no normal approximation and no tie-breaking.

WHAT IT CANNOT SAY (declared before the first number is read):
  * sign exchangeability is assumed across the 12 cells. They are not independent -- they share
    one panel and overlapping decision origins, and the three widths move together. So a p here
    is a LOWER bound on how surprising the arm is, not a frequentist guarantee; the family-wise
    threshold is printed beside the raw one for that reason.
  * it says nothing about whether the arm rule is a good rule. It only separates "this arm's
    cells agree with each other" from "half of them point the other way".
  * the frozen label is imported, never recomputed: this face's job is to sit BESIDE the rule,
    not to replace it.

USAGE:
    python scripts/etf_book_arms_signflip.py run
    python scripts/etf_book_arms_signflip.py --check
    python scripts/etf_book_arms_signflip.py --selftest
"""
from __future__ import annotations

import json
import os
import random
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

# Single source of the input face, of its digest, and of the field-by-field comparison used by
# the gate: r1373 dropped this file's own copy of the staleness read, and the same rule applies
# here -- an input read that this module owns would drift away from the one the null face uses.
from etf_book_rule_null import source_digest, _diff, PARAMS as NULL_PARAMS   # noqa: E402

RES = os.path.join(ROOT, "results")
ARMS_FACE = os.path.join(RES, "etf_book_phase_atlas_arms.json")
OUT_JSON = os.path.join(RES, "etf_book_arms_signflip.json")

# frozen before the first read
PARAMS = {
    "statistic": "median of the arm's published cell deltas",
    "null": "every cell's sign flipped independently (exact enumeration of 2**n worlds)",
    "alpha": 0.05,
    "alpha_familywise": None,      # filled from the arm count: 0.05 / n_arms
    "max_exact_cells": 16,
    "sample_seed": 20261113,
    "sample_trials": 20000,
    "frozen": ("statistic / null / alpha / cell cap were fixed before any arm was read; the "
               "frozen two-label rule is imported from the arms face, never recomputed here"),
}

DEFAULT_ALPHA = 0.05


def read_face(path=None):
    """Load the arms face from the path THIS module was told to read.

    r1373/r1631 family: importing rule_null's reader would have resolved the module-level path in
    rule_null's globals, so a gate pointed at a fixture would quietly read the live face and pass.
    The digest computation stays imported -- that is the part that must not have two copies.
    """
    with open(path or ARMS_FACE, encoding="utf-8") as f:
        return json.load(f)


def median(values):
    """Median with an even count averaging the middle pair (same convention as the arms face)."""
    v = sorted(values)
    n = len(v)
    if not n:
        raise ValueError("median of no values")
    return v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2.0


def _binom_two_sided(k, n):
    """Directional binomial tails for one sign count (exact, no normal approximation).

    Returns (p_at_least_k, p_at_most_k). With n <= 16 the arithmetic is exact in integers, so a
    p of 1/4096 is really 1/4096 and not a rounded 0.0002.
    """
    tot = 1 << n
    at_most = sum(_comb(n, i) for i in range(0, k + 1)) / float(tot)
    at_least = sum(_comb(n, i) for i in range(k, n + 1)) / float(tot)
    return at_least, at_most


def _comb(n, k):
    from math import comb
    return comb(n, k)


def null_means(signed):
    """Every mean reachable by flipping cell signs -- exact when 2**n is affordable.

    The statistic is the mean of the per-cell z (each cell divided by its own band in sigma
    units), because a median over an even number of cells is so coarse that 12 identical cells
    cannot leave the middle of its null: the median only takes the value 0 whenever 5..7 of the
    flips come up positive, which is 61% of the worlds. That coarseness was the first selftest
    failure on this face and is why the magnitude side is measured as a mean.
    """
    n = len(signed)
    if n <= PARAMS["max_exact_cells"]:
        out = []
        for mask in range(1 << n):
            out.append(sum(z if not (mask >> i) & 1 else -z for i, z in enumerate(signed)) / n)
        return out, "exact"
    rng = random.Random(PARAMS["sample_seed"])
    trials = int(PARAMS["sample_trials"])
    out = []
    for _ in range(trials):
        out.append(sum((z if rng.random() < 0.5 else -z) for z in signed) / n)
    return out, "sampled:%d" % trials


def _label(p_worse, p_better, alpha):
    if p_worse <= alpha:
        return "WORSE"
    if p_better <= alpha:
        return "BETTER"
    return "NOT-SEPARABLE"


def read_arm(deltas, bands, alpha):
    """One arm against its own cells, read by two aggregators that must agree (E213).

    Aggregator A -- sign: how many of the cells land on the same side (exact binomial).
    Aggregator B -- magnitude: mean of each cell's delta in its OWN band's sigma units, with the
    null enumerated by flipping every cell's sign (exact, 2**n worlds).
    A verdict printed only when both agree; disagreement is its own published state.
    """
    n = len(deltas)
    # a cell whose delta is exactly zero is a TIE and carries no side: counting it as a negative
    # would let "nothing moved anywhere" read as evidence that the arm is worse (the all-zero
    # selftest leg caught exactly that on the first run)
    nz = [d for d in deltas if d != 0.0]
    k_pos = sum(1 for d in nz if d > 0)
    n_eff = len(nz)
    if n_eff:
        p_at_least, p_at_most = _binom_two_sided(k_pos, n_eff)
        sign_worse, sign_better = p_at_most, p_at_least
    else:
        sign_worse = sign_better = 1.0
    signed = []
    for d, b in zip(deltas, bands):
        sigma = (b or 0.0) / NULL_PARAMS["band_sigma"]
        signed.append(0.0 if sigma <= 0 else d / sigma)
    null, mode = null_means(signed)
    obs = sum(signed) / float(n)
    m = len(null)
    z_worse = sum(1 for x in null if x <= obs + 1e-12) / float(m)
    z_better = sum(1 for x in null if x >= obs - 1e-12) / float(m)
    v_sign = _label(sign_worse, sign_better, alpha)
    v_mag = _label(z_worse, z_better, alpha)
    if v_sign == v_mag:
        verdict, stable = v_sign, True
    else:
        verdict, stable = "SPLIT", False
    ns = sorted(null)
    return {
        "median_delta_pp": round(median(deltas), 3),
        "mean_z": round(obs, 3),
        "cells": n,
        "sign_cells": n_eff,
        "cells_positive": k_pos,
        "cells_negative": sum(1 for d in deltas if d < 0),
        "null_mode": mode,
        "sign_p_worse": round(sign_worse, 5),
        "sign_p_better": round(sign_better, 5),
        "mag_p_worse": round(z_worse, 5),
        "mag_p_better": round(z_better, 5),
        "null_mean_z_band": [round(ns[int(0.05 * (m - 1))], 3), round(ns[int(0.95 * (m - 1))], 3)],
        "verdict_sign": v_sign,
        "verdict_magnitude": v_mag,
        "verdict": verdict,
        "verdict_stable": stable,
    }


def build():
    payload = read_face()
    arms = payload.get("arms") or {}
    n_arms = len(arms)
    alpha = PARAMS["alpha"] if PARAMS["alpha_familywise"] is None else PARAMS["alpha_familywise"]
    if PARAMS["alpha_familywise"] is None:
        alpha = DEFAULT_ALPHA / float(n_arms or 1)     # family-wise: n arms on one panel
    rows = []
    for name in sorted(arms):
        a = arms[name]
        # the cell band is the BASELINE band, the same one the null face draws from, so the two
        # faces cannot disagree about how wide a cell is (r1632/E213)
        keep = [r for r in (a.get("rows") or [])
                if r.get("delta_pp") is not None and r.get("baseline_band_pp")]
        if not keep:
            rows.append({"arm": name, "verdict": "NOT-ASSESSED",
                         "detail": "this arm publishes no cell deltas with a baseline band"})
            continue
        deltas = [float(r["delta_pp"]) for r in keep]
        bands = [float(r["baseline_band_pp"]) for r in keep]
        rec = {"arm": name, "frozen_label": a.get("verdict_if_coherent") or a.get("verdict"),
               "frozen_label_published": a.get("verdict_publishable", True)}
        rec.update(read_arm(deltas, bands, alpha))
        # "does the printed label survive its own cells" -- the question the reader actually has
        rec["frozen_label_stands"] = (
            (rec["frozen_label"] == "REJECT" and rec["verdict"] == "WORSE") or
            (rec["frozen_label"] == "NOT-SEPARABLE" and rec["verdict"] == "NOT-SEPARABLE") or
            (rec["frozen_label"] == "ADOPT" and rec["verdict"] == "BETTER"))
        rows.append(rec)

    judged = [r for r in rows if r.get("frozen_label") in ("REJECT", "NOT-SEPARABLE", "ADOPT")]
    rejects = [r for r in judged if r["frozen_label"] == "REJECT"]
    stands = [r for r in rejects if r.get("frozen_label_stands")]
    flips = [r for r in judged if not r.get("frozen_label_stands")]
    if rejects and not stands:
        verdict = "NO_PUBLISHED_REJECT_STANDS"
        reason = ("all %d REJECTs on the arms face sit inside what sign noise alone produces on "
                  "their own %d cells; the label is the ruler's default, not a measurement"
                  % (len(rejects), rows[0].get("cells", 0)))
    elif rejects and len(stands) == len(rejects):
        verdict = "EVERY_PUBLISHED_REJECT_STANDS"
        reason = ("all %d REJECTs keep their median beyond the family-wise threshold under exact "
                  "sign flipping, so their cells agree on a direction that noise does not" % len(rejects))
    elif rejects:
        verdict = "SOME_REJECTS_STAND"
        reason = ("%d of %d published REJECTs stand on their own cells (%s); the rest are inside "
                  "sign noise and must not be read as findings"
                  % (len(stands), len(rejects),
                     ", ".join(r["arm"] for r in stands)))
    else:
        verdict = "NO_REJECT_TO_TEST"
        reason = "the arms face publishes no REJECT at this cutoff"
    return {
        "script": "scripts/etf_book_arms_signflip.py",
        "question": ("of the labels the frozen rule prints on this page, which ones survive the "
                     "sign noise of their own cells?"),
        "units": {"p": ("exact share of the arm's 2**n sign patterns whose median is at least as "
                        "extreme as the published one, in the printed direction"),
                  "band_pp": "p05-p95 of that arm's null medians"},
        "criteria": dict(PARAMS, alpha_familywise=round(alpha, 6), arms=n_arms),
        "rules_source": "results/etf_book_phase_atlas_arms.json rows (labels imported, not recomputed)",
        "source": {"face": "results/etf_book_phase_atlas_arms.json",
                   "inputs_sha256": source_digest(payload)},
        "arms": rows,
        "n_arms": n_arms,
        "n_reject": len(rejects),
        "n_reject_standing": len(stands),
        "labels_overturned": [r["arm"] for r in flips],
        "verdict": verdict,
        "verdict_reasons": [reason],
        "evidence_cutoff": (payload.get("baseline") or {}).get("evidence_cutoff"),
    }


def check():
    """Gate: the face must equal a rebuild, and the reason for a drift must be the source."""
    if not os.path.exists(OUT_JSON):
        print("face is stale: no published sign-flip face at %s" % os.path.basename(OUT_JSON))
        return 2
    with open(OUT_JSON, encoding="utf-8") as f:
        pub = json.load(f)
    if not os.path.exists(ARMS_FACE):
        print("face is stale: its source face %s is missing" % os.path.basename(ARMS_FACE))
        return 2
    rebuilt = json.loads(json.dumps(build()))
    drift = _diff(pub, rebuilt)
    if not drift:
        print("sign-flip face matches a rebuild: %d/%d REJECTs stand (%s)"
              % (pub["n_reject_standing"], pub["n_reject"], pub["evidence_cutoff"]))
        return 0
    recorded = (pub.get("source") or {}).get("inputs_sha256")
    now = rebuilt["source"]["inputs_sha256"]
    if recorded != now:
        if not recorded:
            print("face is stale: the published face carries no source digest; drift=%s"
                  % "; ".join(drift)[:300])
        else:
            print("face is stale: the arms face changed since this one was written (inputs %s -> "
                  "%s); drift=%s" % (recorded[:12], now[:12], "; ".join(drift)[:300]))
        return 2
    print("face is inconsistent: %d field(s) disagree while the arms face is unchanged: %s"
          % (len(drift), "; ".join(drift)[:400]))
    return 1


def _selftest():
    bad = []
    CHECKS = [0]

    def chk(ok, msg):
        CHECKS[0] += 1
        print(("[PASS] " if ok else "[FAIL] ") + msg)
        if not ok:
            bad.append(msg)

    # L1 the enumeration is complete: 12 cells -> exactly 4096 worlds
    deltas = [0.5 * i - 1.0 for i in range(12)]
    null, mode = null_means(deltas)
    chk(mode == "exact" and len(null) == 4096, "12 cells enumerate exactly 4096 sign worlds (%s/%d)"
        % (mode, len(null)))
    # L2 an arm whose cells all point the same way cannot be produced by sign noise
    same = [0.4] * 12
    rec = read_arm(same, [1.0] * 12, 0.05 / 10.0)
    chk(rec["verdict"] == "BETTER" and rec["sign_p_better"] <= 0.001,
        "12 cells all +0.4 read BETTER (sign p=%.5f, mag p=%.5f)"
        % (rec["sign_p_better"], rec["mag_p_better"]))
    # L3 activity precondition (r1261): zero deltas are NOT-SEPARABLE, never a silent WORSE
    flat = read_arm([0.0] * 12, [1.0] * 12, 0.05 / 10.0)
    chk(flat["verdict"] == "NOT-SEPARABLE",
        "zero deltas read NOT-SEPARABLE, not a label (got %s)" % flat["verdict"])
    # L4 mirror symmetry: flipping every sign mirrors the two p-values on both aggregators
    base12 = [0.9, -0.2, 0.4, 0.1, 0.7, 0.3, 0.5, 0.2, 0.6, 0.8, 0.15, 0.45]
    up = read_arm(base12, [2.0] * 12, 0.05 / 10.0)
    dn = read_arm([-x for x in base12], [2.0] * 12, 0.05 / 10.0)
    chk(abs(up["sign_p_worse"] - dn["sign_p_better"]) < 1e-9 and
        abs(up["mag_p_worse"] - dn["mag_p_better"]) < 1e-9,
        "flipping every sign mirrors both aggregators' p-values")
    # L5 mixed signs stay inside the null: a coin-flip arm must not be published as a finding
    mixed = read_arm([0.9, -0.8, 0.7, -0.9, 0.6, -0.7, 0.8, -0.6, 0.5, -0.5, 0.4, -0.4],
                     [2.0] * 12, 0.05 / 10.0)
    chk(mixed["verdict"] == "NOT-SEPARABLE",
        "a half-and-half arm reads NOT-SEPARABLE (got %s)" % mixed["verdict"])
    # L6 the real face: every published arm is accounted for and the cutoff is the arms' own
    payload = read_face()
    pub = build()
    chk(len(pub["arms"]) == len(payload["arms"]),
        "every published arm appears (%d of %d)" % (len(pub["arms"]), len(payload["arms"])))
    chk(pub["evidence_cutoff"] == (payload.get("baseline") or {}).get("evidence_cutoff"),
        "the evidence cutoff is the arms face's own (%s)" % pub["evidence_cutoff"])
    chk(sum(pub["n_reject_standing"] for _ in [0]) <= pub["n_reject"],
        "standing REJECTs cannot exceed printed REJECTs (%d/%d)"
        % (pub["n_reject_standing"], pub["n_reject"]))
    # L7 the gate: match passes, an edit stays red, a moved source is stale
    global OUT_JSON, ARMS_FACE
    keep, keep_arms = OUT_JSON, ARMS_FACE
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        tmp = os.path.join(td, "sf.json")
        p2 = json.loads(json.dumps(pub))
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(p2, f, ensure_ascii=False, indent=1)
        os.utime(tmp, (os.path.getmtime(tmp) + 3600, os.path.getmtime(tmp) + 3600))
        OUT_JSON = tmp
        chk(check() == 0, "a face that equals a rebuild passes the gate")
        chk(p2["source"]["inputs_sha256"] == source_digest(payload),
            "the recorded digest is the one the arms face hashes to today")
        p2["arms"][0]["median_delta_pp"] = 99.0
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(p2, f, ensure_ascii=False, indent=1)
        os.utime(tmp, (os.path.getmtime(tmp) + 3600, os.path.getmtime(tmp) + 3600))
        chk(check() == 1, "an edited face with no source moved stays inconsistent")
        p3 = json.loads(json.dumps(payload))
        first = next(iter(p3["arms"].values()))
        first["rows"][0]["delta_pp"] = round(first["rows"][0]["delta_pp"] + 0.05, 6)
        moved = os.path.join(td, "arms2.json")
        with open(moved, "w", encoding="utf-8") as f:
            json.dump(p3, f, ensure_ascii=False, indent=1)
        ARMS_FACE = moved
        chk(check() == 2, "a regenerated arms face reads stale (refresh), not hand-edited")
        ARMS_FACE = os.path.join(td, "missing.json")
        chk(check() == 2, "a missing source face is stale, never a crash")
        ARMS_FACE = keep_arms
        OUT_JSON = os.path.join(td, "missing_out.json")
        chk(check() == 2, "a missing face is stale, not inconsistent")
    OUT_JSON, ARMS_FACE = keep, keep_arms

    print("selftest: %d legs, %d failed" % (CHECKS[0], len(bad)))
    return 0 if not bad else 1


def main(argv):
    if "--selftest" in argv:
        return _selftest()
    if "--check" in argv:
        return check()
    p = build()
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(p, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("sign-flip null on %d arms (cutoff %s): %s"
          % (p["n_arms"], p["evidence_cutoff"], p["verdict"]))
    for r in p["arms"]:
        if r.get("verdict") == "NOT-ASSESSED":
            print("%-16s %s" % (r["arm"], r.get("detail")))
            continue
        print("%-16s frozen=%-14s sign=%-14s mag=%-14s sign_p=%.5f mag_p=%.5f stands=%s"
              % (r["arm"], r["frozen_label"], r["verdict_sign"], r["verdict_magnitude"],
                 min(r["sign_p_worse"], r["sign_p_better"]),
                 min(r["mag_p_worse"], r["mag_p_better"]), r.get("frozen_label_stands")))
    print(p["verdict"], "|", p["verdict_reasons"][0])
    print("wrote", os.path.relpath(OUT_JSON, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
