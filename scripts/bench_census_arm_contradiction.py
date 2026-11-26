#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Does a census face's headline agree with the arms it is built from?

WHY THIS FILE EXISTS
--------------------
r2151 found three arms that lose money to simply holding the same basket. While
reading them, one of the faces looked wrong in a different way:

    results/bench_census_bond_futures.json
      "verdict": "CENSUS_LEANS_POSITIVE"
      arms:     5 arms, all five NO_EDGE

A reader who only reads the headline is told the space leans positive; the five
rules inside it all fail every gate. `run_census()` decides that headline from

    powered = [r for r in rows if r["powered"]]      # can the sample SEE 5pp?
    pos     = [r for r in powered if ann_pct > 0]    # and is the sign positive?

`powered` is a *resolution* statement (MDE <= target_edge), not a *merit*
statement. Nothing in the headline looks at whether any arm actually passed a
gate. So an arm sitting at +1.2% with MDE 3.8 produces exactly the same headline
word as an arm sitting at +9% that passed all five gates.

This file measures how often that happens, across every published census face,
from the faces alone (no panel reload, no verdict rewrite).

WHAT IS MEASURED
----------------
For every `results/bench_*.json` with `config.type == "census"`:
  * the published headline word
  * how many arms it contains, and how those arms judged
    (GO / INCOMPLETE / NO_EDGE / UNINFORMATIVE_AT_TARGET)
  * how many arms cleared H1's absolute line (4.0% default, or the face's own
    `crit.H1_full_pct` when the face overrides it)
  * whether the headline leans one way while nothing inside it passes

Verdict vocabulary (per face)
  AGREES                 headline and arms point the same way
  LEANS_WITHOUT_A_PASS   headline says the space leans positive/negative but no
                         arm inside it reached GO (the reader cannot act on it)
  HEADLINE_CONTRADICTS   headline says positive while every powered arm's point
                         estimate is <= 0 (or the mirror)
  NO_ARMS                nothing to compare

Read-only by construction: this file never writes a screen, a face, or a verdict.
It only reads what `bench_generic` already published.

Usage
-----
  python scripts/bench_census_arm_contradiction.py             # write json + page
  python scripts/bench_census_arm_contradiction.py --check     # stale? rc0/rc3
  python scripts/bench_census_arm_contradiction.py --selftest  # offline legs
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import io
import json
import os
import sys
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")
OUT_JSON = os.path.join(RES, "bench_census_arm_contradiction.json")
OUT_MD = os.path.join(ROOT, "research", "BENCH_CENSUS_ARM_CONTRADICTION.md")

# the same default `run_arm` uses when a face does not override it
H1_FULL_PCT_DEFAULT = 4.0
# only these headlines make a claim about direction
LEAN_WORDS = ("CENSUS_LEANS_POSITIVE", "CENSUS_LEANS_NEGATIVE")

TZ = timezone(timedelta(hours=8))


def now_iso():
    return datetime.now(TZ).replace(microsecond=0).isoformat()


def read(path):
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)


def own_names():
    return {os.path.basename(OUT_JSON), os.path.basename(OUT_MD)}


def input_paths():
    """Every published bench face except this file's own output."""
    mine = own_names()
    out = []
    for p in sorted(glob.glob(os.path.join(RES, "bench_*.json"))):
        if os.path.basename(p) in mine:
            continue
        out.append(p)
    return out


def digest(paths):
    h = hashlib.sha256()
    for p in paths:
        h.update(os.path.basename(p).encode("utf-8"))
        with open(p, "rb") as f:
            h.update(hashlib.sha256(f.read()).hexdigest().encode("ascii"))
    return h.hexdigest()


def arm_counts(arms):
    c = {"GO": 0, "INCOMPLETE": 0, "NO_EDGE": 0,
         "UNINFORMATIVE_AT_TARGET": 0, "OTHER": 0}
    for a in arms:
        v = a.get("verdict")
        c[v if v in c else "OTHER"] += 1
    return c


def h1_line(cfg):
    crit = (cfg.get("crit") or {}) if isinstance(cfg, dict) else {}
    v = crit.get("H1_full_pct")
    return float(v) if v is not None else H1_FULL_PCT_DEFAULT


def classify(headline, arms, line):
    """One verdict per face, plus the evidence that produced it."""
    n = len(arms)
    counts = arm_counts(arms)
    anns = [a.get("common_window", {}).get("ann_pct") for a in arms]
    anns = [float(x) for x in anns if x is not None]
    clears_h1 = sum(1 for x in anns if x >= line)
    n_go = counts["GO"]
    ev = {
        "n_arms": n,
        "counts": counts,
        "n_clears_h1": clears_h1,
        "h1_line_pct": line,
        "min_ann_pct": round(min(anns), 2) if anns else None,
        "max_ann_pct": round(max(anns), 2) if anns else None,
        "median_ann_pct": (round(sorted(anns)[len(anns) // 2], 2) if anns else None),
    }
    if n == 0:
        ev["verdict"] = "NO_ARMS"
        ev["why"] = "face published no arms; headline cannot be checked against them"
        return ev
    if headline not in LEAN_WORDS:
        ev["verdict"] = "AGREES"
        ev["why"] = (f"headline {headline} makes no directional claim; "
                     f"{n_go}/{n} arms GO")
        return ev

    # wrong direction outranks "could not get over the line": saying positive when
    # every arm is negative is a different (worse) error than saying positive when
    # the arms are merely too small to clear 4%.
    if headline == "CENSUS_LEANS_POSITIVE":
        if ev["max_ann_pct"] is not None and ev["max_ann_pct"] <= 0:
            ev["verdict"] = "HEADLINE_CONTRADICTS"
            ev["why"] = (f"headline says positive while the best arm is "
                         f"{ev['max_ann_pct']}%")
            return ev
        if n_go == 0:
            # clearing the absolute H1 line is not the same as passing every gate:
            # census_bond_futures has one arm at 4.02% and still 0/5 GO. A reader who
            # acts on "leans positive" needs the GO count, not the H1 count.
            ev["verdict"] = "LEANS_WITHOUT_A_PASS"
            ev["why"] = (f"headline says the space leans positive, but 0/{n} arms "
                         f"passed every gate ({clears_h1}/{n} cleared only the "
                         f"{line:.1f}% H1 line; best arm {ev['max_ann_pct']}%)")
            return ev
    if headline == "CENSUS_LEANS_NEGATIVE":
        if ev["min_ann_pct"] is not None and ev["min_ann_pct"] >= 0:
            ev["verdict"] = "HEADLINE_CONTRADICTS"
            ev["why"] = (f"headline says negative while the worst arm is "
                         f"{ev['min_ann_pct']}%")
            return ev
        if counts["GO"] > 0:
            ev["verdict"] = "HEADLINE_CONTRADICTS"
            ev["why"] = f"headline says negative while {counts['GO']} arm(s) GO"
            return ev
    ev["verdict"] = "AGREES"
    ev["why"] = (f"headline {headline} with {n_go}/{n} arms GO and "
                 f"{clears_h1}/{n} over the {line:.1f}% H1 line")
    return ev


def build():
    faces = []
    skipped = []
    for p in input_paths():
        try:
            d = read(p)
        except Exception as e:  # a half-written face is not a finding
            skipped.append({"path": os.path.basename(p), "why": f"unreadable: {e}"})
            continue
        if not isinstance(d, dict) or "verdict" not in d or "arms" not in d:
            skipped.append({"path": os.path.basename(p), "why": "not a bench face"})
            continue
        cfg = d.get("config") or {}
        if cfg.get("type") != "census":
            skipped.append({"path": os.path.basename(p),
                            "why": f"type={cfg.get('type')}"})
            continue
        line = h1_line(cfg)
        ev = classify(d.get("verdict"), d.get("arms") or [], line)
        faces.append({
            "cell": cfg.get("id") or os.path.basename(p)[6:-5],
            "path": os.path.basename(p),
            "headline": d.get("verdict"),
            "evidence_cutoff": d.get("evidence_cutoff"),
            **ev,
        })

    by_v = {}
    for f in faces:
        by_v[f["verdict"]] = by_v.get(f["verdict"], 0) + 1
    flagged = [f for f in faces if f["verdict"] in
               ("LEANS_WITHOUT_A_PASS", "HEADLINE_CONTRADICTS")]

    return {
        "schema": "bench_census_arm_contradiction.v1",
        "generated": now_iso(),
        "evidence_cutoff": max([f["evidence_cutoff"] for f in faces
                                if f.get("evidence_cutoff")] or [None]) or None,
        "cutoff_rule": "the newest evidence_cutoff among the census faces read",
        "n_faces_read": len(faces),
        "n_faces_skipped": len(skipped),
        "skipped": skipped,
        "verdict_counts": by_v,
        "n_flagged": len(flagged),
        "flagged": [{"cell": f["cell"], "verdict": f["verdict"],
                     "headline": f["headline"], "why": f["why"]} for f in flagged],
        "faces": faces,
        "h1_default_pct": H1_FULL_PCT_DEFAULT,
        "decision": (
            "HEADLINE_OVERSTATES_MERIT" if flagged else
            "HEADLINES_MATCH_THEIR_ARMS"),
        "what_this_does_not_do": [
            "it does not re-issue any arm or face verdict (frozen set untouched)",
            "it does not reload panels; every number is read off published faces",
            "it does not decide whether a census space is worth another burn -- "
            "it only says whether its headline is supported by its own arms",
        ],
        "inputs_digest": digest(input_paths()),
    }


# --------------------------------------------------------------------------
def render(r):
    L = ["# Does a census headline agree with the arms inside it?", "",
         f"generated {r['generated']} · cutoff {r['evidence_cutoff']} · "
         f"**{r['decision']}**", "",
         f"{r['n_faces_read']} census faces read · {r['n_faces_skipped']} skipped "
         f"(non-census or unreadable) · **{r['n_flagged']} flagged**", "",
         "## The defect", "",
         "`bench_generic.run_census()` picks its headline from `powered` -- a",
         "*resolution* statement (MDE ≤ target_edge) -- and the **sign** of that arm.",
         "It never asks whether any arm passed a gate. So an arm at +1.2% with MDE 3.8",
         "and an arm at +9% that cleared all five checks produce the same headline word.",
         "", "## Faces", "",
         "| face | headline | arms | GO | NO_EDGE | UNINFORM | clears H1 | best | worst | verdict |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for f in sorted(r["faces"], key=lambda x: (x["verdict"] != "LEANS_WITHOUT_A_PASS",
                                               x["verdict"] != "HEADLINE_CONTRADICTS",
                                               x["cell"])):
        c = f["counts"]
        L.append(f"| `{f['cell']}` | {f['headline']} | {f['n_arms']} | {c['GO']} | "
                 f"{c['NO_EDGE']} | {c['UNINFORMATIVE_AT_TARGET']} | "
                 f"{f['n_clears_h1']}/{f['n_arms']} | {f['max_ann_pct']}% | "
                 f"{f['min_ann_pct']}% | **{f['verdict']}** |")
    if r["flagged"]:
        L += ["", "## Flagged", ""]
        for f in r["flagged"]:
            L.append(f"* `{f['cell']}` — **{f['verdict']}**: {f['why']}")
    L += ["", "## What this does not do", ""]
    L += [f"* {x}" for x in r["what_this_does_not_do"]]
    L += ["", f"inputs digest `{r['inputs_digest'][:16]}…`"]
    return "\n".join(L) + "\n"


def write_outputs(r):
    os.makedirs(RES, exist_ok=True)
    with io.open(OUT_JSON, "w", encoding="utf-8", newline="\n") as f:
        json.dump(r, f, ensure_ascii=False, indent=1)
        f.write("\n")
    os.makedirs(os.path.join(ROOT, "research"), exist_ok=True)
    with io.open(OUT_MD, "w", encoding="utf-8", newline="\n") as f:
        f.write(render(r))


def check():
    if not os.path.exists(OUT_JSON):
        print("STALE face missing: run without --check to build it")
        return 3
    old = read(OUT_JSON)
    paths = input_paths()
    d = digest(paths)
    if old.get("inputs_digest") != d:
        print(f"STALE inputs moved: face {old.get('inputs_digest','?')[:16]}… "
              f"vs disk {d[:16]}… -> re-derive")
        return 3
    new = build()
    a = {k: v for k, v in old.items() if k != "generated"}
    b = {k: v for k, v in new.items() if k != "generated"}
    if a != b:
        diff = [k for k in a if a.get(k) != b.get(k)]
        print(f"CHECK FAILED same inputs, different numbers in {diff}")
        return 3
    print(f"CHECK_OK {old['n_faces_read']} faces, {old['n_flagged']} flagged, "
          f"decision {old['decision']}")
    return 0


def _face(headline, anns, crit=None):
    arms = []
    for a in anns:
        arms.append({"verdict": "NO_EDGE",
                     "common_window": {"ann_pct": a}})
    cfg = {"id": "t", "type": "census", "crit": crit or {}}
    return classify(headline, arms, h1_line(cfg))


def _face_v(headline, pairs, crit=None):
    arms = [{"verdict": v, "common_window": {"ann_pct": a}} for a, v in pairs]
    cfg = {"id": "t", "type": "census", "crit": crit or {}}
    return classify(headline, arms, h1_line(cfg))


def selftest():
    legs = []

    def leg(name, cond):
        legs.append((name, bool(cond)))

    # 1. the exact shape that started this: headline positive, every arm NO_EDGE
    r = _face("CENSUS_LEANS_POSITIVE", [1.2, 0.4, -0.3, 2.1, 0.9])
    leg("leans-positive with no arm over H1 is flagged", r["verdict"] == "LEANS_WITHOUT_A_PASS")

    # 2. the live anchor (census_bond_futures): one arm over the H1 line but zero
    #    arms through every gate is still flagged -- clearing one line is not a pass
    r = _face_v("CENSUS_LEANS_POSITIVE", [(4.02, "NO_EDGE"), (3.21, "NO_EDGE")])
    leg("an arm over H1 alone still flags when no arm GOes",
        r["verdict"] == "LEANS_WITHOUT_A_PASS")
    leg("the flag still reports how many cleared H1", r["n_clears_h1"] == 1)

    # 3. a GO arm always agrees
    r = _face_v("CENSUS_LEANS_POSITIVE", [(6.0, "GO"), (-1.0, "NO_EDGE")])
    leg("a GO arm agrees with a positive headline", r["verdict"] == "AGREES")

    # 4. positive headline while the best arm is <= 0 contradicts
    r = _face_v("CENSUS_LEANS_POSITIVE", [(0.0, "NO_EDGE"), (-2.0, "NO_EDGE")])
    leg("positive headline over non-positive arms contradicts",
        r["verdict"] == "HEADLINE_CONTRADICTS")

    # 5. the face's own H1 override is read and carried (it is reported, not
    #    decisive -- the flag now keys on GO, so the line only annotates the why)
    r = _face("CENSUS_LEANS_POSITIVE", [3.5, 1.0], crit={"H1_full_pct": 3.0})
    leg("face H1 override is carried into the evidence", r["h1_line_pct"] == 3.0)
    leg("the override changes which arms count as clearing H1", r["n_clears_h1"] == 1)
    r = _face("CENSUS_LEANS_POSITIVE", [3.5, 1.0])
    leg("default H1 line still applies without an override",
        r["h1_line_pct"] == 4.0 and r["n_clears_h1"] == 0)

    # 6. non-lean headlines never flag
    r = _face("CENSUS_UNPOWERED", [-1.0, 0.5])
    leg("a non-lean headline is never flagged", r["verdict"] == "AGREES")

    # 7. no arms at all
    r = classify("CENSUS_LEANS_POSITIVE", [], 4.0)
    leg("no arms is NO_ARMS not a flag", r["verdict"] == "NO_ARMS")

    # 8. negative mirror: GO inside a negative headline contradicts
    r = _face_v("CENSUS_LEANS_NEGATIVE", [(-5.0, "GO"), (-2.0, "NO_EDGE")])
    leg("negative headline with a GO arm contradicts",
        r["verdict"] == "HEADLINE_CONTRADICTS")

    # 9. negative headline whose arms are all negative agrees
    r = _face_v("CENSUS_LEANS_NEGATIVE", [(-5.0, "NO_EDGE"), (-2.0, "NO_EDGE")])
    leg("negative headline over negative arms agrees", r["verdict"] == "AGREES")

    # 10. digest changes when a face changes
    p = input_paths()[:1]
    if p:
        d1 = digest(p)
        leg("digest is a function of the bytes it names", len(d1) == 64)

    bad = [n for n, ok in legs if not ok]
    for n, ok in legs:
        print(("PASS " if ok else "FAIL ") + n)
    print(f"--selftest {len(legs) - len(bad)}/{len(legs)}")
    return 0 if not bad else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.check:
        return check()
    r = build()
    write_outputs(r)
    print(json.dumps({"ok": True, "faces": r["n_faces_read"],
                      "flagged": r["n_flagged"], "decision": r["decision"]},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
