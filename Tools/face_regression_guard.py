#!/usr/bin/env python
"""face_regression_guard -- a derived face may not move its evidence backwards.

Why this exists (r1285, live case): bm-a regenerated the ETF book faces from the
scripts it has, and the machine's wide ETF panel ends 2026-11-06 while the
committed ticket was priced on 2026-11-10.  Nothing errored: every leg returned
rc0 and printed a coherent sheet.  The only trace was a number getting four days
older inside an otherwise healthy-looking artifact (`entry_gate.evidence_cutoff`
11-10 -> 11-06, and the gate's cagr 0.0878 -> 0.0859 with it).  Had that been
committed under a "round regenerated the faces" message, the published book
would have silently stepped back a week.

The law this encodes: a face that carries a cutoff may only move it forward, or
say why it moved back.  Regeneration is not automatically an advance.

Usage
  python Tools/face_regression_guard.py check            # worktree vs HEAD
  python Tools/face_regression_guard.py check --ref origin/main
  python Tools/face_regression_guard.py selftest

Exit codes
  0  no regression (or nothing to compare)
  1  at least one face moved its cutoff backwards
  2  mechanism failure (git unavailable / unreadable input)

The comparison itself is a pure function so the selftest can drive it with
fixtures instead of a repository.
"""

import argparse
import json
import os
import subprocess
import sys

# Keys that mean "as far as this face has data", most specific first.  `bar`
# and `asof` are last because plenty of faces carry a bar without claiming
# completeness; they are still better than nothing when they are all we have.
CUTOFF_KEYS = [
    "evidence_cutoff",
    "data_cutoff",
    "panel_last_bar",
    "cutoff",
    "asof",
    "bar",
]

# Only faces that publish numbers are interesting.  Configuration seeds and
# schema files never carry a moving cutoff.
SKIP_PREFIXES = (
    "results/_",
    "results/_quarantine/",
)

RC_OK, RC_REGRESSED, RC_BROKEN = 0, 1, 2


def _date_key(value):
    """Return a comparable (y, m, d) tuple, or None when the value is not a date.

    Accepts "2026-11-10" and "2026-11-10T12:34:56+08:00".  Anything else -- an
    integer bar index, a sentence, a null -- is not a cutoff and must not be
    compared: a guard that flags junk strings is a guard nobody keeps.
    """
    if not isinstance(value, str):
        return None
    s = value.strip()
    if len(s) < 10 or s[4] != "-" or s[7] != "-":
        return None
    try:
        return (int(s[0:4]), int(s[5:7]), int(s[8:10]))
    except ValueError:
        return None


def face_cutoffs(face, _prefix=""):
    """Collect every usable cutoff in a face as [(key, date_tuple, raw), ...].

    A face is only as fresh as its stalest block.  The live case proved it: the
    ticket's top-level cutoff stayed 2026-11-10 while the `entry_gate` block
    inside it dropped to 2026-11-06, and a guard that reads only the first key
    it finds reports the sheet as perfectly current.  So we take all of them and
    compare the oldest on each side.
    """
    out = []
    if not isinstance(face, dict):
        return out
    for key, value in face.items():
        name = ("%s.%s" % (_prefix, key)) if _prefix else key
        d = _date_key(value)
        if d is not None and key in CUTOFF_KEYS:
            out.append((name, d, value))
        elif isinstance(value, dict):
            out.extend(face_cutoffs(value, name))
    return out


def oldest_cutoff(face):
    """The stalest cutoff in a face, or None when it carries no date at all."""
    got = face_cutoffs(face)
    if not got:
        return None
    return min(got, key=lambda item: item[1])


def compare_faces(committed, worktree):
    """Pure comparison. `committed` and `worktree` map path -> parsed JSON.

    Compares cutoff *key by key*, never face by face.  A face normally carries
    a dozen stamps from different lanes, some of them legitimately old; judging
    the face by its oldest stamp hid the r1285 case completely (the ticket's
    `live_width_ruler` block was already at 2026-11-06, so `entry_gate` dropping
    from 11-10 to 11-06 still left the minimum unchanged).  The rule that
    actually holds is: no single stamp may move backwards.

    Returns a list of findings {path, key, was, now, direction}.  Faces that are
    new, unreadable, or carry no comparable stamp are not judged.
    """
    findings = []
    for path in sorted(worktree):
        if path not in committed:
            continue
        old = {k: d for k, d, _ in face_cutoffs(committed[path])}
        new = {k: d for k, d, _ in face_cutoffs(worktree[path])}
        raw_new = {k: r for k, _, r in face_cutoffs(worktree[path])}
        raw_old = {k: r for k, _, r in face_cutoffs(committed[path])}
        for key in sorted(new):
            if key not in old:
                continue
            direction = "flat"
            if new[key] < old[key]:
                direction = "backward"
            elif new[key] > old[key]:
                direction = "forward"
            findings.append({
                "path": path,
                "key": key,
                "was": raw_old[key],
                "now": raw_new[key],
                "direction": direction,
            })
    regressions = [f for f in findings if f["direction"] == "backward"]
    return findings, regressions


def _git(*args, binary=False):
    r = subprocess.run(["git"] + list(args), capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout if binary else r.stdout.decode("utf-8", "replace")


def _load_json(text):
    try:
        return json.loads(text)
    except Exception:
        return None


def tracked_faces(ref):
    """Paths under results/ that exist in both the worktree and `ref`."""
    listed = _git("ls-tree", "-r", "--name-only", ref, "results/")
    if listed is None:
        return None
    out = []
    for path in listed.splitlines():
        path = path.strip()
        if not path.endswith(".json"):
            continue
        if any(path.startswith(p) for p in SKIP_PREFIXES):
            continue
        if not os.path.exists(path):
            continue
        out.append(path)
    return out


def _batch_blobs(ref, paths):
    """Fetch many `ref:path` blobs in one `git cat-file --batch` pass.

    One `git show` per face is hundreds of process launches on a repository this
    size; the guard runs every round and must not become the slowest leg.
    """
    if not paths:
        return {}
    request = "".join("%s:%s\n" % (ref, p) for p in paths).encode("utf-8")
    proc = subprocess.Popen(["git", "cat-file", "--batch"],
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL)
    blob, _ = proc.communicate(request)
    out, pos, n = {}, 0, len(blob)
    order = list(paths)
    for path in order:
        eol = blob.find(b"\n", pos)
        if eol < 0:
            break
        header = blob[pos:eol].decode("utf-8", "replace")
        pos = eol + 1
        parts = header.split()
        if len(parts) < 3 or parts[-1] == "missing":
            continue
        try:
            size = int(parts[2])
        except ValueError:
            continue
        out[path] = blob[pos:pos + size].decode("utf-8", "replace")
        pos += size + 1
    return out


def run_check(ref, only=None):
    paths = tracked_faces(ref)
    if paths is None:
        print("face_regression_guard: cannot read %s (git failed)" % ref)
        return RC_BROKEN
    if only:
        paths = [p for p in paths if only in p]
        if not paths:
            print("face_regression_guard: --only %r matched no tracked face" % only)
            return RC_BROKEN

    committed, worktree = {}, {}
    base_blobs = _batch_blobs(ref, paths)
    for path in paths:
        raw = base_blobs.get(path)
        if raw is None:
            continue
        base = _load_json(raw)
        if base is None:
            continue
        with open(path, "rb") as fh:
            now = _load_json(fh.read().decode("utf-8", "replace"))
        if now is None:
            continue
        committed[path] = base
        worktree[path] = now

    findings, regressions = compare_faces(committed, worktree)

    payload = {
        "artifact": "face_regression_guard",
        "ref": ref,
        "compared": len(findings),
        "regressions": regressions,
        "verdict": "REGRESSED" if regressions else "CLEAN",
        "law": "a face that carries a cutoff may only move forward, or say why it moved back",
    }
    os.makedirs("results", exist_ok=True)
    with open("results/face_regression_guard.json", "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)

    if not regressions:
        print("face_regression_guard: CLEAN (%d faces carry a comparable cutoff vs %s)"
              % (len(findings), ref))
        return RC_OK

    print("face_regression_guard: %d face(s) moved their cutoff BACKWARD vs %s"
          % (len(regressions), ref))
    for r in regressions:
        print("  %s  %s: %s -> %s" % (r["path"], r["key"], r["was"], r["now"]))
    return RC_REGRESSED


def selftest():
    """Fixture legs: the guard must fire on a rollback and stay quiet otherwise."""
    legs = []

    def leg(name, ok, detail=""):
        legs.append((name, bool(ok), detail))

    # L1 rollback is caught
    f, r = compare_faces({"a.json": {"evidence_cutoff": "2026-11-10"}},
                         {"a.json": {"evidence_cutoff": "2026-11-06"}})
    leg("rollback flagged", len(r) == 1 and r[0]["was"] == "2026-11-10")

    # L2 forward move is not a regression
    f, r = compare_faces({"a.json": {"evidence_cutoff": "2026-11-06"}},
                         {"a.json": {"evidence_cutoff": "2026-11-10"}})
    leg("forward move ignored", len(r) == 0 and f[0]["direction"] == "forward")

    # L3 same day is flat
    f, r = compare_faces({"a.json": {"bar": "2026-11-10"}},
                         {"a.json": {"bar": "2026-11-10"}})
    leg("same day flat", len(r) == 0 and f[0]["direction"] == "flat")

    # L4 NEW face (no committed twin) is never a regression -- a brand new
    #    artifact cannot have moved backwards.
    f, r = compare_faces({}, {"n.json": {"evidence_cutoff": "2020-01-01"}})
    leg("new face ignored", len(r) == 0 and len(f) == 0)

    # L5 junk cutoff values are not judged, so the guard does not cry wolf on
    #    faces that store a bar index or a sentence.
    f, r = compare_faces({"a.json": {"bar": "2026-11-10"}},
                         {"a.json": {"bar": "not a date"}})
    leg("junk value skipped", len(r) == 0 and len(f) == 0)

    # L6 the specific live case: a nested block (entry_gate-style) is found and
    #    its rollback is caught, which is the shape that shipped the bug.
    f, r = compare_faces(
        {"t.json": {"entry_gate": {"evidence_cutoff": "2026-11-10"}}},
        {"t.json": {"entry_gate": {"evidence_cutoff": "2026-11-06"}}})
    leg("nested block caught", len(r) == 1 and r[0]["key"] == "entry_gate.evidence_cutoff")

    # L7 a renamed cutoff key cannot be compared to the old name, so the guard
    #    stays quiet instead of inventing a direction.  (Worth a future leg that
    #    reports renames as a separate note.)
    f, r = compare_faces({"a.json": {"evidence_cutoff": "2026-11-10"}},
                         {"a.json": {"data_cutoff": "2026-11-09"}})
    leg("renamed key not judged", len(r) == 0 and len(f) == 0)

    # L7b the masked case: a current top-level stamp over a stale block.  The
    #     first draft of this guard read only the first stamp it found and
    #     called it flat, which is why the live run had to be re-read.
    f, r = compare_faces(
        {"t.json": {"evidence_cutoff": "2026-11-10", "risk_tape": {"evidence_cutoff": "2026-11-10"}}},
        {"t.json": {"evidence_cutoff": "2026-11-10", "risk_tape": {"evidence_cutoff": "2026-11-06"}}})
    leg("stale block under a current stamp caught", len(r) == 1 and r[0]["now"] == "2026-11-06")

    # L7c the second masking, the one that actually shipped the bug: an already
    #     old sibling block makes the face minimum identical even though one
    #     stamp moved back four days.  Judging the minimum hides it; judging key
    #     by key does not.
    f, r = compare_faces(
        {"t.json": {"a": {"evidence_cutoff": "2026-11-06"}, "b": {"evidence_cutoff": "2026-11-10"}}},
        {"t.json": {"a": {"evidence_cutoff": "2026-11-06"}, "b": {"evidence_cutoff": "2026-11-06"}}})
    leg("min-identical rollback still caught", len(r) == 1 and r[0]["key"] == "b.evidence_cutoff")

    # L8 the same day under two different key names is not judged at all
    f, r = compare_faces({"a.json": {"evidence_cutoff": "2026-11-10"}},
                         {"a.json": {"bar": "2026-11-10"}})
    leg("rename without move not judged", len(r) == 0 and len(f) == 0)

    ok = all(v for _, v, _ in legs)
    for name, passed, detail in legs:
        print("%s %s%s" % ("ok  " if passed else "FAIL", name,
                           ("  " + detail) if detail else ""))
    print("selftest: %d/%d %s" % (sum(1 for _, v, _ in legs if v), len(legs),
                                  "PASS" if ok else "FAIL"))
    return RC_OK if ok else RC_BROKEN


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("command", choices=["check", "selftest"], nargs="?", default="check")
    ap.add_argument("--ref", default="HEAD", help="commit/ref to compare the worktree against")
    ap.add_argument("--only", default=None,
                    help="restrict to faces whose path contains this substring (fast demo)")
    args = ap.parse_args(argv)

    if args.command == "selftest":
        return selftest()
    return run_check(args.ref, args.only)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
