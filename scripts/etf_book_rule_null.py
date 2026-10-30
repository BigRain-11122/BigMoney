"""The labeler, run on data that cannot contain an effect.

r1352 priced the buffer family on the phase grid and the three arms came back
k=0.05 -0.030pp (REJECT) / k=0.10 +0.072pp (NOT-SEPARABLE) / k=0.20 +0.138pp
(NOT-SEPARABLE), with **0 of 36** cell-level deltas clearing their own band and a sign flip in
3 of 12 cells between the outermost arms. Two possible readings:

  (a) the family is a real but tiny effect, and the rule sorts the arms honestly;
  (b) the family is noise, and the rule's label is itself a coin toss at this ruler.

This module decides between them by asking the only question that separates them: **what does
the frozen rule say when the data provably has no effect?** Each cell's delta is replaced by a
draw from a zero-mean normal whose width is that cell's own band (p95-p05 = 3.2905 sigma), then
`judge()` -- imported from the arms module, never re-implemented -- is applied. The resulting
label frequencies are the rule's false-label rate on this grid.

If P(REJECT | no effect) is large, then a single-arm REJECT is not evidence, and the k=0.05
"REJECT" the previous window published was a property of the ruler, not of the buffer knob.

Usage:
  python scripts/etf_book_rule_null.py run
  python scripts/etf_book_rule_null.py --check
  python scripts/etf_book_rule_null.py --selftest
"""

from __future__ import annotations

import json
import hashlib
import os
import random
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

# single source of the rule AND of the staleness rule: r1373 dropped this file's own copy of the
# cutoff read, which could only drift away from the arms module's (the r1292 unit family again).
from etf_book_phase_atlas_arms import judge, CRITERIA, _source_advanced

RES = os.path.join(ROOT, "results")
ARMS_FACE = os.path.join(RES, "etf_book_phase_atlas_arms.json")
OUT_JSON = os.path.join(RES, "etf_book_rule_null.json")

# frozen before the first read
PARAMS = {
    "n_trials": 20000,
    "seed": 20261030,
    "band_sigma": 3.2905,       # p95-p05 of a normal in sigma units
    "materiality_p": 0.05,      # a label is informative only if it is rare under the null
    "frozen": ("n_trials / seed / band_sigma / materiality_p were fixed before any trial was "
               "drawn; the rule itself is imported from the arms module so the two cannot drift"),
}


def arms_face():
    with open(ARMS_FACE, encoding="utf-8") as f:
        return json.load(f)


def base_bands(payload):
    """Each cell's own baseline band, taken from the published rows (never recomputed here)."""
    any_arm = next(iter(payload["arms"].values()))
    return {(r["n_hold"], r["rebal"]): r["baseline_band_pp"] for r in any_arm["rows"]}


def source_digest(payload):
    """Identity of the INPUT this face consumes, so the gate can tell 'source regenerated' from
    'face hand-edited' without asking a clock (r1371/r1372 family).

    Everything below is read off the arms face: the band of every cell, each arm's own delta and
    band rows, its verdict, and the bar the whole thing is priced on. If these bytes are the same
    as when this face was written, no source moved -- so a drifting null face is somebody's edit.
    If they differ, the arms face was regenerated and the honest answer is 'stale, refresh me'
    (rc=2), not 'inconsistent' (rc=1), which would leave a green chain permanently red.
    """
    inputs = {
        "cutoff": payload.get("baseline", {}).get("evidence_cutoff"),
        "bands": [[k[0], k[1], v] for k, v in sorted(base_bands(payload).items())],
        "arms": [[name,
                  [[r["n_hold"], r["rebal"], round(float(r["delta_pp"]), 9),
                    round(float(r["band_pp"]), 9)] for r in a["rows"]],
                  label_of(a)]
                 for name, a in sorted(payload["arms"].items())],
    }
    blob = json.dumps(inputs, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def label_of(a):
    """The label an arm reads as a RULE OUTPUT, whether or not the arms face publishes it.

    r1180: the arms audit withholds a verdict whose comparison spans two panels and keeps the
    reading in `verdict_if_coherent`. This face asks 'what does this rule say under a null',
    which is a question about the rule, so it must keep reading the rule's own answer --
    otherwise every arm silently scores 0.0 against the null and the null looks decisive.
    Publication status travels with the row instead.
    """
    return a.get("verdict_if_coherent") or a.get("verdict")


def median_sigma(bands):
    """One sigma implied by the median cell band (p95-p05 = 3.2905 sigma)."""
    v = sorted(bands.values())
    mid = len(v) // 2
    band = v[mid] if len(v) % 2 else (v[mid - 1] + v[mid]) / 2.0
    return band / PARAMS["band_sigma"]


def simulate(bands, shift_pp=0.0, n_trials=None, seed=None):
    """Label frequencies when every cell's delta is zero-mean noise of its own band's width."""
    n = int(n_trials if n_trials is not None else PARAMS["n_trials"])
    rng = random.Random(int(seed if seed is not None else PARAMS["seed"]))
    cells = sorted(bands)
    counts = {}
    for _ in range(n):
        rows = []
        for k in cells:
            band = bands[k]
            sigma = band / PARAMS["band_sigma"]
            rows.append({"delta_pp": rng.gauss(shift_pp, sigma), "band_pp": band})
        label, _ = judge(rows)
        counts[label] = counts.get(label, 0) + 1
    return {lab: round(c / float(n), 4) for lab, c in sorted(counts.items())}, n


def build():
    payload = arms_face()
    bands = base_bands(payload)
    labels, n = simulate(bands)
    # the observed arms, for the comparison that makes the number readable
    observed = []
    for name, a in payload["arms"].items():
        resolvable = sum(1 for r in a["rows"] if abs(r["delta_pp"]) > r["band_pp"])
        deltas = sorted(r["delta_pp"] for r in a["rows"])
        med = (deltas[len(deltas) // 2] if len(deltas) % 2 else
               (deltas[len(deltas) // 2 - 1] + deltas[len(deltas) // 2]) / 2.0)
        observed.append({
            "arm": name,
            "median_delta_pp": round(med, 3),
            "cells_beyond_own_band": resolvable,
            "verdict": label_of(a),
            "verdict_published_on_arms_face": a.get("verdict_publishable", True),
            "null_p_same_or_worse": labels.get(label_of(a), 0.0),
        })
    p_reject = labels.get("REJECT", 0.0)
    p_sep = labels.get("NOT-SEPARABLE", 0.0)
    p_adopt = labels.get("ADOPT", 0.0)
    p_none = labels.get("NOT-ASSESSED", 0.0)
    mat = PARAMS["materiality_p"]
    if p_reject > mat and p_sep > mat:
        verdict = "LABELS_ARE_NOISE_ON_THIS_RULER"
        reason = ("under a provably effect-free panel the rule reports REJECT %.1f%% and "
                  "NOT-SEPARABLE %.1f%% of the time; neither label can carry a single-arm "
                  "conclusion at this band width" % (100 * p_reject, 100 * p_sep))
    elif p_reject > mat:
        verdict = "REJECT_IS_THE_DEFAULT"
        floor = CRITERIA["cagr_floor_pp"]
        sig = median_sigma(bands)
        reason = ("an effect-free panel reads REJECT %.1f%% of the time, so a published REJECT "
                  "transmits almost nothing; the rule's informative branch is the rare one "
                  "(NOT-SEPARABLE %.1f%%, ADOPT %.1f%%, NOT-ASSESSED %.1f%%). Mechanism: the "
                  "cell floor %.2fpp is %.1fx smaller than one sigma (%.2fpp) of these cells, so "
                  "about half of them land under it by chance and the not-worse share "
                  "(floor %.2f) fails by construction"
                  % (100 * p_reject, 100 * p_sep, 100 * p_adopt, 100 * p_none, floor,
                     sig / abs(floor), sig, CRITERIA["cagr_share_min"]))
    elif p_sep > mat:
        verdict = "SEPARABILITY_IS_NOT"
        reason = ("NOT-SEPARABLE is what this ruler says %.1f%% of the time by default; only "
                  "its REJECT branch (%.2f%%) discriminates" % (100 * p_sep, 100 * p_reject))
    else:
        verdict = "LABELS_ARE_INFORMATIVE"
        reason = ("no label appears more than %.0f%% of the time under the null"
                  % (100 * mat))
    return {
        "script": "scripts/etf_book_rule_null.py",
        "question": ("what does the frozen two-label rule say when the panel has no effect at "
                     "all, so that a published REJECT cannot be mistaken for a measurement?"),
        "units": {"p": "share of simulated no-effect panels receiving the label",
                  "band_pp": "p95-p05 of a cell's median CAGR over its decision origins"},
        "criteria": PARAMS,
        "rules_source": "scripts/etf_book_phase_atlas_arms.py::judge (imported, not copied)",
        "source": {"face": "results/etf_book_phase_atlas_arms.json",
                   "inputs_sha256": source_digest(payload)},
        "null": {"trials": n, "label_frequency": labels,
                 "shift_pp": 0.0, "band_source": "results/etf_book_phase_atlas_arms.json rows"},
        "observed": observed,
        "verdict": verdict,
        "verdict_reasons": [reason],
        "evidence_cutoff": payload["baseline"]["evidence_cutoff"],
    }


def _diff(a, b, path="", out=None, limit=6):
    if out is None:
        out = []
    if len(out) >= limit:
        return out
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b), key=str):
            if len(out) >= limit:
                break
            if k not in a or k not in b:
                out.append("%s.%s (only on one side)" % (path, k))
            else:
                _diff(a[k], b[k], "%s.%s" % (path, k), out, limit)
        return out
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append("%s (len %d vs %d)" % (path, len(a), len(b)))
            return out
        for i, (x, y) in enumerate(zip(a, b)):
            if len(out) >= limit:
                break
            _diff(x, y, "%s[%d]" % (path, i), out, limit)
        return out
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool):
        if abs(a - b) > 1e-9:
            out.append("%s (%r vs %r)" % (path, a, b))
    elif a != b:
        out.append("%s (%r vs %r)" % (path, a, b))
    return out


def check():
    """Gate: this face must equal a re-simulation from the arms face.

    Two red states, and the difference is the whole point (r1346): a face whose SOURCE has moved
    is 'stale' and the chain pays the declared refresh; a face that disagrees with its own source
    while the source has not moved is 'inconsistent' and stays red, because re-deriving it would
    launder a hand edit.

    r1373: this gate used to answer that question by looking for a LATER bar on the arms face
    alone, which cannot see the common case -- a regenerated arms face whose cutoff did not move
    (the same 2026-10-29 bar re-derived with different cells). That drift was reported as a hand
    edit (rc=1) and would have sat permanently red in the chain while the truth was 'refresh me'.
    Now the ONLY question asked is whether the inputs this face consumed still hash the same; the
    cutoff comparison imports the arms module's own implementation rather than keeping a second
    copy of it.
    """
    if not os.path.exists(OUT_JSON):
        print("face is stale: no published null face at %s" % os.path.basename(OUT_JSON))
        return 2
    with open(OUT_JSON, encoding="utf-8") as f:
        pub = json.load(f)
    if not os.path.exists(ARMS_FACE):
        print("face is stale: its source face %s is missing, so no re-simulation is possible"
              % os.path.basename(ARMS_FACE))
        return 2
    rebuilt = json.loads(json.dumps(build()))
    drift = _diff(pub, rebuilt)
    if not drift:
        print("null face matches a re-simulation (seed %d, %d trials): %s"
              % (PARAMS["seed"], pub["null"]["trials"], pub["verdict"]))
        return 0
    recorded = (pub.get("source") or {}).get("inputs_sha256")
    now = rebuilt["source"]["inputs_sha256"]
    if recorded != now:
        if not recorded:
            print("face is stale: the published face carries no source-input digest, so it "
                  "predates this gate; drift=%s" % "; ".join(drift)[:300])
        else:
            print("face is stale: the arms face's inputs changed since this one was written "
                  "(inputs %s -> %s); drift=%s" % (recorded[:12], now[:12], "; ".join(drift)[:300]))
        return 2
    adv = _source_advanced(pub, [ARMS_FACE])
    if adv:
        print("face is stale: a source face is priced later than this one (%s); drift=%s"
              % (",".join(adv), "; ".join(drift)[:300]))
        return 2
    print("face is inconsistent: %d field(s) disagree while the arms face's inputs are unchanged: %s"
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

    payload = arms_face()
    bands = base_bands(payload)
    chk(len(bands) == 12, "the bands come from all 12 published cells (got %d)" % len(bands))

    # L1 deterministic: same seed, same labels
    a, n = simulate(bands, n_trials=500, seed=7)
    b, _ = simulate(bands, n_trials=500, seed=7)
    chk(a == b, "the null is seeded and reproducible")
    # L2 activity precondition (r1261): a zero-width ruler with zero delta is NOT-SEPARABLE, not
    # a silent ADOPT -- the rule really ran and saw 12 cells
    flat_bands = {k: 1e-9 for k in bands}
    lab, _ = simulate(flat_bands, n_trials=50, seed=1)
    chk(lab == {"NOT-SEPARABLE": 1.0}, "zero noise reads NOT-SEPARABLE, 100%% (got %r)" % (lab,))
    # L3 a shift large against the band is always ADOPT: the labeler is not stuck
    wide = {k: 1.0 for k in bands}
    lab, _ = simulate(wide, shift_pp=50.0, n_trials=50, seed=1)
    chk(lab == {"ADOPT": 1.0}, "a 50pp shift on a 1pp band reads ADOPT, 100%% (got %r)" % (lab,))
    # L4 the published face's null frequencies are what a fresh simulation of the same size says
    pub = build()
    tot = sum(pub["null"]["label_frequency"].values())
    chk(abs(tot - 1.0) < 1e-6, "the label frequencies sum to 1 (got %.6f)" % tot)
    chk(sum(1 for x in pub["observed"]) == len(payload["arms"]),
        "every published arm is compared against the null")
    # L5 the verdict follows from its own published frequencies, not from a hand-written string
    freq = pub["null"]["label_frequency"]
    if pub["verdict"] == "LABELS_ARE_NOISE_ON_THIS_RULER":
        chk(freq.get("REJECT", 0) > PARAMS["materiality_p"] and
            freq.get("NOT-SEPARABLE", 0) > PARAMS["materiality_p"],
            "LABELS_ARE_NOISE_ON_THIS_RULER requires both labels to be common under the null")
    elif pub["verdict"] == "REJECT_IS_THE_DEFAULT":
        chk(freq.get("REJECT", 0) > PARAMS["materiality_p"] and
            max(freq.get("NOT-SEPARABLE", 0), freq.get("ADOPT", 0)) <= PARAMS["materiality_p"],
            "REJECT_IS_THE_DEFAULT requires REJECT to be common and every other label rare")
    elif pub["verdict"] == "SEPARABILITY_IS_NOT":
        chk(freq.get("NOT-SEPARABLE", 0) > PARAMS["materiality_p"],
            "SEPARABILITY_IS_NOT requires NOT-SEPARABLE to be common under the null")
    # L6 the gate: an edited face with no source moved stays red; a missing face is stale
    global OUT_JSON, ARMS_FACE
    keep = OUT_JSON
    keep_arms = ARMS_FACE
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        tmp = os.path.join(td, "null.json")
        p2 = json.loads(json.dumps(build()))
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(p2, f, ensure_ascii=False, indent=1)
        os.utime(tmp, (os.path.getmtime(tmp) + 3600, os.path.getmtime(tmp) + 3600))
        OUT_JSON = tmp
        chk(check() == 0, "a face that equals a re-simulation passes the gate")
        chk(p2["source"]["inputs_sha256"] == source_digest(arms_face()),
            "the recorded source-input digest is the one the arms face hashes to today")
        p2["null"]["label_frequency"]["REJECT"] = 0.999
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(p2, f, ensure_ascii=False, indent=1)
        os.utime(tmp, (os.path.getmtime(tmp) + 3600, os.path.getmtime(tmp) + 3600))
        chk(check() == 1, "an edited face with no source moved stays inconsistent")
        # r1373: the case the old gate could not see -- the arms face regenerated on the SAME
        # bar (same cutoff, different cells). That is 'refresh me', not 'somebody edited me'.
        p3 = json.loads(json.dumps(arms_face()))
        first = next(iter(p3["arms"].values()))
        first["rows"][0]["baseline_band_pp"] = round(first["rows"][0]["baseline_band_pp"] + 0.05, 6)
        arms2 = os.path.join(td, "arms.json")
        with open(arms2, "w", encoding="utf-8") as f:
            json.dump(p3, f, ensure_ascii=False, indent=1)
        ARMS_FACE = arms2
        old_face = os.path.join(td, "null_same_bar.json")
        with open(old_face, "w", encoding="utf-8") as f:
            json.dump(build(), f, ensure_ascii=False, indent=1)
        ARMS_FACE = keep_arms
        OUT_JSON = old_face
        chk(check() == 2,
            "a regenerated arms face on the same bar reads stale (refresh), not hand-edited")
        p4 = json.loads(json.dumps(build()))
        p4.pop("source", None)
        nodigest = os.path.join(td, "null_nodigest.json")
        with open(nodigest, "w", encoding="utf-8") as f:
            json.dump(p4, f, ensure_ascii=False, indent=1)
        OUT_JSON = nodigest
        chk(check() == 2, "a face published before the digest existed is stale, not inconsistent")
        ARMS_FACE = os.path.join(td, "no_arms.json")
        OUT_JSON = tmp
        chk(check() == 2, "a missing source face is stale, never a crash")
        ARMS_FACE = keep_arms
        OUT_JSON = os.path.join(td, "missing.json")
        chk(check() == 2, "a missing face is stale, not inconsistent")
    OUT_JSON = keep
    ARMS_FACE = keep_arms

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
    print("null label frequencies (%d trials): %s" % (p["null"]["trials"], p["null"]["label_frequency"]))
    for o in p["observed"]:
        print("%-11s %-14s null_p_same_or_worse %.4f" % (
            o["arm"], o["verdict"], o["null_p_same_or_worse"]))
    print(p["verdict"], "|", p["verdict_reasons"][0])
    print("wrote", os.path.relpath(OUT_JSON, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))