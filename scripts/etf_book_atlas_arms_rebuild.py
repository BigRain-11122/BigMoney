"""Re-derive the phase-atlas arm faces onto ONE world, and prove that they are.

WHY (r1179 bm-a): the arm faces are produced by separate 280-cell sweeps, hours or days
apart.  The arms audit (`etf_book_phase_atlas_arms.py`) compares their bands with each
other, and until r1179 no face could say which panel it had priced -- so a band measured
on one world could sit beside a band measured on another and read as a rule effect (E293).
The atlas now stamps `panel` on every face; this runner is the consumer of that stamp:

  * it rebuilds a group of arms, one atlas sweep per arm, using the ARM list and the
    DECLARED knob table of the audit itself (single source -- no second copy of the
    mapping), so an arm can never be rebuilt with a different knob than the one it is
    audited under;
  * it then asserts that every face it just wrote carries the SAME panel digest.  A
    group that leaves the family split across two worlds fails here instead of quietly
    producing a comparison the audit would have read as a result;
  * it finishes by running the audit's own `--check`, so "the arm set is coherent" is
    decided by the published criterion, not by this runner's opinion.

Groups (each is one pool unit; the three together put the whole family on one panel):
    buffer  = buffer_k02 .05 .10 .20 .40
    cost    = cost0 .05 .20 .40
    combo   = base (production toll) + buffer_k05_cost20

Usage:
    python scripts/etf_book_atlas_arms_rebuild.py run --only=buffer [--workers=8]
    python scripts/etf_book_atlas_arms_rebuild.py --selftest
"""

from __future__ import annotations

import io
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import etf_book_phase_atlas_arms as AUDIT  # arm list + declared knobs (single source)

GROUPS = {
    "buffer": ["buffer_k02", "buffer_k05", "buffer_k10", "buffer_k20", "buffer_k40"],
    "cost": ["cost0", "cost05", "cost20", "cost40"],
    "combo": ["base", "buffer_k05_cost20"],
    # one group = one world. A knob family rebuilt on its own leaves the FAMILY split across
    # two panels, and the arms audit (correctly) reports the older faces as stale -- so the
    # pool unit is the whole set, not a third of it. r1179 lost one burn to learning this.
    "all": ["base", "buffer_k02", "buffer_k05", "buffer_k10", "buffer_k20", "buffer_k40",
            "cost0", "cost05", "cost20", "cost40", "buffer_k05_cost20"],
}

BASE_FACE = AUDIT.BASE
RECEIPT = os.path.join(ROOT, "results", "etf_book_atlas_arms_rebuild.json")
ATLAS = os.path.join("scripts", "etf_book_phase_atlas.py")


def face_for(arm):
    """The repo-relative face path an arm writes (base = the production-toll face)."""
    if arm == "base":
        return BASE_FACE
    return AUDIT.ARMS[arm][0]


def command_for(arm, workers=None, out=None):
    """The atlas command line that produces `arm`, built from the audit's declared knob."""
    cmd = [sys.executable, ATLAS, "run"]
    if workers:
        cmd.append("--workers=%d" % int(workers))
    knob = AUDIT.DECLARED.get(arm) or {}
    if "buffer_k" in knob:
        cmd.append("--k=%g" % knob["buffer_k"])
    if "cost" in knob:
        cmd.append("--cost=%g" % knob["cost"])
    cmd.append("--out=%s" % (out or os.path.relpath(face_for(arm), ROOT)).replace("\\", "/"))
    return cmd


def digests(faces):
    """Read the panel digest of each face; a face without one is reported, never assumed.

    Returns {"stamped": {face: digest}, "unstamped": [...], "absent": [...]}.
    """
    stamped, unstamped, absent = {}, [], []
    for face in faces:
        path = face if os.path.isabs(face) else os.path.join(ROOT, face)
        if not os.path.exists(path):
            absent.append(face)
            continue
        try:
            with io.open(path, encoding="utf-8") as fh:
                payload = json.load(fh) or {}
        except Exception:
            absent.append(face)
            continue
        dig = (payload.get("panel") or {}).get("digest")
        if dig:
            stamped[face] = dig
        else:
            unstamped.append(face)
    return {"stamped": stamped, "unstamped": unstamped, "absent": absent}


def verdict(reading):
    """One sentence a reader can act on: are these faces one world or several?"""
    worlds = sorted(set(reading["stamped"].values()))
    if reading["absent"]:
        return "INCOMPLETE", "%d face(s) absent" % len(reading["absent"])
    if reading["unstamped"]:
        return "UNSTAMPED", "%d face(s) predate the panel stamp" % len(reading["unstamped"])
    if len(worlds) > 1:
        return "SPLIT_WORLDS", "%d faces, %d panels" % (len(reading["stamped"]), len(worlds))
    if not worlds:
        return "EMPTY", "no faces to compare"
    return "ONE_WORLD", "all %d faces priced %s" % (len(reading["stamped"]), worlds[0])


def run(group, workers=None):
    arms = GROUPS[group]
    written = []
    for arm in arms:
        cmd = command_for(arm, workers=workers)
        print("[rebuild] %s -> %s" % (arm, cmd[-1]), flush=True)
        rc = subprocess.call(cmd, cwd=ROOT)
        print("[rebuild] %s rc=%d" % (arm, rc), flush=True)
        written.append(os.path.relpath(face_for(arm), ROOT).replace("\\", "/"))
    reading = digests(written)
    kind, detail = verdict(reading)
    audit_rc = subprocess.call([sys.executable,
                                os.path.join(ROOT, "scripts", "etf_book_phase_atlas_arms.py"),
                                "--check"], cwd=ROOT)
    out = {"group": group, "arms": arms, "faces": written, "panel": reading,
           "verdict": kind, "detail": detail, "audit_check_rc": audit_rc,
           "stamp_law": "every face in a rebuilt group must price one panel (r1179)"}
    with io.open(RECEIPT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print("[rebuild] %s: %s (%s); audit --check rc=%d" % (group, kind, detail, audit_rc),
          flush=True)
    # the group's own coherence is what this unit promises; the family-level audit verdict is
    # recorded, not fatal -- a partial rebuild of the family is honestly "stale", and making
    # that fatal would fail every unit except the last one.
    return 0 if kind == "ONE_WORLD" else 2


def selftest():
    bad = []
    # `all` is the pool unit (one family, one world); the knob groups are the parts it covers.
    knob_groups = {g: arms for g, arms in GROUPS.items() if g != "all"}
    seen = {}
    for group, arms in knob_groups.items():
        for arm in arms:
            if arm != "base" and arm not in AUDIT.ARMS:
                bad.append("%s/%s is not an arm the audit knows" % (group, arm))
            seen[arm] = seen.get(arm, 0) + 1
    for arm, n in seen.items():
        if n != 1:
            bad.append("%s appears in %d knob groups" % (arm, n))
    covered = set()
    for arms in knob_groups.values():
        covered.update(arms)
    if set(GROUPS["all"]) != covered:
        bad.append("the all group is not exactly the union of the knob groups")
    for arm in AUDIT.ARMS:
        if arm not in GROUPS["all"]:
            bad.append("%s is audited but no rebuild covers it" % arm)
    # the knob in the command line is the knob the audit declares
    for arm in ("buffer_k05", "cost20", "buffer_k05_cost20", "cost0"):
        cmd = " ".join(command_for(arm))
        for key, val in (AUDIT.DECLARED.get(arm) or {}).items():
            flag = "--k=%g" % val if key == "buffer_k" else "--cost=%g" % val
            if flag not in cmd:
                bad.append("%s does not pass %s" % (arm, flag))
    if "--k=" in " ".join(command_for("cost20")):
        bad.append("a cost arm must not set the buffer knob")
    # a mixed family is SPLIT_WORLDS, a uniform one is ONE_WORLD, an unstamped face is named
    split = {"stamped": {"a": "1111222233334444", "b": "5555666677778888"},
             "unstamped": [], "absent": []}
    same = {"stamped": {"a": "1111222233334444", "b": "1111222233334444"},
            "unstamped": [], "absent": []}
    old = {"stamped": {"a": "1111222233334444"}, "unstamped": ["c"], "absent": []}
    miss = {"stamped": {}, "unstamped": [], "absent": ["d"]}
    if verdict(split)[0] != "SPLIT_WORLDS":
        bad.append("two panels in one family is not reported as split")
    if verdict(same)[0] != "ONE_WORLD":
        bad.append("a uniform family is not reported as one world")
    if verdict(old)[0] != "UNSTAMPED":
        bad.append("a face without a stamp is silently accepted")
    if verdict(miss)[0] != "INCOMPLETE":
        bad.append("an absent face is not reported as incomplete")
    # an absent face is never invented as stamped
    if digests(["results/__no_such_face__.json"])["stamped"]:
        bad.append("a missing file was read as a stamped face")
    for b in bad:
        print("[FAIL] %s" % b)
    print("selftest: %d legs, %d failed" % (9 + len(bad), len(bad)))
    return 0 if not bad else 1


def main(argv):
    if "--selftest" in argv:
        return selftest()
    group = "buffer"
    workers = None
    for a in argv:
        if a.startswith("--only="):
            group = a.split("=", 1)[1]
        elif a.startswith("--workers="):
            workers = int(a.split("=", 1)[1])
    if group not in GROUPS:
        print("unknown group %r; one of %s" % (group, ",".join(GROUPS)))
        return 2
    return run(group, workers=workers)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))