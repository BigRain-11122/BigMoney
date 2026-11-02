"""E373 -- two studies in one replay were published from two different commits.

E369 measured that a pin taken at E350's publishing commit does not reproduce E350's published
numbers.  The queue card then asked the obvious next question, which is cheap because the machinery
already exists: E353's face records a *different* commit (e847e099, evidence_cutoff 11-02) than
E350's (daf9a897, 11-01), and both studies were replayed together on 11-02.  So:

  * build the corpus pin at EACH study's own publishing commit (members and bytes from that tree,
    never from today's disk),
  * replay BOTH studies over BOTH pins, which is a 2 x 2 matrix and costs one scan per cell,
  * publish per cell: published, pinned, delta, reproduced -- per key, never a folded verdict.

The question the card asks is answered as a measurement, not an assertion: if each study reproduces
only at its own commit, then the queue of pins is per-study and a single corpus pin cannot cover a
multi-study replay.  If both studies reproduce at one commit, one pin covers the couple and E369's
bill was a single-vintage artefact.

Bounds kept honest in the face:
  * the pin is the SOURCE population only.  E353's faces are read from disk today (build_index has
    no vintage parameter), so a cell proves the source population's vintage, not the faces'.
  * the published numbers are read from the upstream faces, never written into this file, so a
    re-publish cannot silently keep pointing at a stale commit.
  * this study writes its own pin files only when E369 has not already published one for that
    commit; E369's pin is reused verbatim rather than restamped with another study's name.

Usage:
  python scripts/e373_two_pins_one_replay.py run       # build both pins, replay 2x2, publish
  python scripts/e373_two_pins_one_replay.py verify    # re-derive every non-scan fact
  python scripts/e373_two_pins_one_replay.py selftest  # offline fixture legs
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e346_status_writer_unread as e346  # noqa: E402  (the corpus rule, imported not copied)
import e350_field_branch_census as e350  # noqa: E402
import e353_unwritten_guard_presence as e353  # noqa: E402
import e369_pin_at_publishing_commit as e369  # noqa: E402  (the pin/bill machinery, imported)

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
TODAY = "2026-11-02"
FACE = "TWOPINS-%s.json" % TODAY
LATEST = "twopins_latest.json"
STUDY = "E373_two_pins_one_replay"
SELF_REL = "scripts/e373_two_pins_one_replay.py"

DISK_PIN = os.path.join(OUTDIR, "CORPUSPIN-2026-11-02.json")   # E361's 11-02 disk pin
PIN_NAME = "CORPUSPIN-AT-COMMIT-%s.json"   # same naming as E369, so one commit has one pin file

CORPUS_DIRS = tuple(e346.CORPUS_DIRS)
CORPUS_FILES = tuple(e346.CORPUS_FILES)

STUDIES = ("E350", "E353")

V_PER_STUDY = ("each_study_reproduces_only_at_its_own_publishing_commit_so_the_pin_queue_is_"
               "per_study_and_one_corpus_pin_cannot_cover_a_multi_study_replay")
V_ONE_PIN = ("both_studies_reproduce_at_one_and_the_same_commit_so_one_pin_covers_the_couple_"
             "and_the_two_vintages_are_not_load_bearing")
V_MIXED = ("one_study_reproduces_at_a_commit_the_other_does_not_so_the_replay_mixes_two_"
           "provenances_and_neither_single_pin_is_honest_for_both")
V_NONE = ("neither_study_reproduces_at_either_publishing_commit_so_the_published_numbers_come_"
          "from_neither_tree_and_the_pin_alone_does_not_explain_them")


def say(message):
    print(message, flush=True)


def _sha256(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_json(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def tree_members(commit):
    """E369's walk, reused: names come from the tree, not from today's disk."""
    return e369.tree_members(commit)


def build_pin(commit):
    """The corpus pin at ``commit``, stamped with this study's identity when it must be written.

    If E369 already published a pin for this commit, that file is the pin: restamping it with
    another ``study`` name would make one vintage look like two.
    """
    path = os.path.join(OUTDIR, PIN_NAME % commit[:8])
    if os.path.exists(path):
        pin = load_json(path)
        if pin.get("git_commit") == commit:
            return pin, path, "reused"
    members = tree_members(commit)
    blobs = e369.read_blobs(commit, members)
    sources = [{"path": p, "sha256": _sha256(blobs[p]), "bytes": len(blobs[p].encode("utf-8"))}
               for p in members if p in blobs]
    digest = hashlib.sha256()
    for row in sources:
        digest.update(("%s\0%s\n" % (row["path"], row["sha256"])).encode("utf-8"))
    pin = {"study": STUDY,
           "rule": "e346.CORPUS_DIRS *.py + CORPUS_FILES, the study's own file excluded at walk time",
           "git_commit": commit,
           "count": len(sources),
           "pin_id": digest.hexdigest(),
           "evidence_cutoff": TODAY,
           "generated": datetime.now().astimezone().isoformat(timespec="seconds"),
           "sources": sources}
    return pin, path, "built"


def published_numbers(study):
    """E369's reader for both upstream faces (they are read, never rewritten)."""
    return e369.published_numbers(study)


def pinned_members(pin):
    return [(row["path"], e369.read_blobs(pin["git_commit"], [row["path"]]).get(row["path"], ""))
            for row in pin["sources"]]


def replay(study, members):
    mod = e350 if study == "E350" else e353
    return mod.build(files=members)


def cell(study, members, commit):
    published = published_numbers(study)
    face = replay(study, members)
    replayed = e369._replayed_numbers(study, face)
    return {"commit": commit,
            "published_from": (published or {}).get("pin"),
            "pinned": {"population_source": face.get("population_source"),
                       "numbers": replayed},
            "compare": e369.compare(published, replayed),
            "same_commit_as_publication": (published or {}).get("pin") == commit}


def reproduced_anywhere(compare):
    flags = [row.get("reproduced") for row in (compare or {}).values()
             if row.get("reproduced") is not None]
    return bool(flags) and all(flags)


def decide(matrix):
    own = {}
    for study in STUDIES:
        cells = (matrix.get(study) or {}).get("cells") or {}
        own_commit = (matrix.get(study) or {}).get("published_from")
        own_cell = cells.get(own_commit) or {}
        others = [c for sha, c in cells.items() if sha != own_commit]
        at_own = reproduced_anywhere(own_cell.get("compare"))
        at_other = any(reproduced_anywhere(c.get("compare")) for c in others)
        own[study] = {"at_own_pin": at_own, "at_other_pin": at_other}
    flags = [own[s] for s in STUDIES]
    if all(f["at_own_pin"] and not f["at_other_pin"] for f in flags):
        return V_PER_STUDY, own
    if any(f["at_own_pin"] and f["at_other_pin"] for f in flags):
        return V_ONE_PIN, own
    if any(f["at_own_pin"] for f in flags) and not all(f["at_own_pin"] for f in flags):
        return V_MIXED, own
    if not any(f["at_own_pin"] or f["at_other_pin"] for f in flags):
        return V_NONE, own
    return V_MIXED, own


def build(write_face=True):
    pubs = {s: published_numbers(s) for s in STUDIES}
    commits = []
    for s in STUDIES:
        sha = (pubs.get(s) or {}).get("pin")
        if not sha:
            raise RuntimeError("%s's face does not record the commit it was published from" % s)
        if sha not in commits:
            commits.append(sha)
    say("publishing commits: %s" % ", ".join("%s=%s" % (s, (pubs[s] or {}).get("pin"))
                                              for s in STUDIES))
    pins, bills = {}, {}
    for sha in commits:
        pin, path, how = build_pin(sha)
        pins[sha] = pin
        bills[sha] = e369.store_bill(sha, DISK_PIN)
        say("pin @%s: %d members (%s), pin_id %s" % (sha[:8], pin["count"], how,
                                                     pin["pin_id"][:12]))
        if how == "built":
            os.makedirs(OUTDIR, exist_ok=True)
            with open(path, "w", encoding="utf-8", newline="\n") as fh:
                json.dump(pin, fh, ensure_ascii=False, indent=1, sort_keys=True)
                fh.write("\n")
    matrix = {}
    for study in STUDIES:
        own = (pubs.get(study) or {}).get("pin")
        cells = {}
        for sha in commits:
            say("%s @%s: replay over the pinned bytes" % (study, sha[:8]))
            cells[sha] = cell(study, pinned_members(pins[sha]), sha)
        matrix[study] = {"published_from": own,
                         "published": pubs.get(study),
                         "cells": cells}
    verdict, own = decide(matrix)
    populations = {}
    for sha in commits:
        populations[sha] = {"count": pins[sha]["count"], "pin_id": pins[sha]["pin_id"],
                            "members": sorted(r["path"] for r in pins[sha]["sources"])}
    shared = set()
    if len(commits) == 2:
        a, b = (set(populations[c]["members"]) for c in commits)
        shared = {"common": len(a & b), "only_a": len(a - b), "only_b": len(b - a),
                  "only_a_paths": sorted(a - b)[:40], "only_b_paths": sorted(b - a)[:40]}
    face = {"study": STUDY,
            "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
            "evidence_cutoff": TODAY,
            "source": SELF_REL,
            "pins": {sha: {"count": pins[sha]["count"], "pin_id": pins[sha]["pin_id"],
                           "file": os.path.relpath(os.path.join(OUTDIR, PIN_NAME % sha[:8]),
                                                   ROOT).replace("\\", "/")}
                     for sha in commits},
            "population_overlap": shared,
            "store_bills": bills,
            "matrix": matrix,
            "verdict": verdict,
            "reproduces_at_own_pin": own,
            "bound": ("the pin covers the SOURCE population only: E353 reads its faces with "
                      "build_index() on today's disk, so a cell proves the source vintage, not "
                      "the faces' one; a key that is not identical across the two studies (E350 "
                      "publishes corpus_sources/fields_*, E353 publishes pairs/by_class) is "
                      "compared within its own study only, never across; the store bill is "
                      "measured against E361's 11-02 disk pin, a population of the same family, "
                      "so it bounds the members a commit cannot supply rather than rebuilding "
                      "either face's exact input")}
    if write_face:
        for target in (os.path.join(OUTDIR, FACE), os.path.join(OUTDIR, LATEST)):
            with open(target, "w", encoding="utf-8", newline="\n") as fh:
                json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
                fh.write("\n")
    return face


def verify(write_face=False):
    """Re-derive every fact that needs no corpus scan; a scan-free check is a cheap tripwire."""
    dated = os.path.join(OUTDIR, FACE)
    if not os.path.exists(dated):
        say("no published face")
        return 2
    published = load_json(dated)
    problems = []
    for study in STUDIES:
        fresh = published_numbers(study)
        if fresh is None:
            problems.append("%s: upstream face missing" % study)
            continue
        block = (published.get("matrix") or {}).get(study) or {}
        if block.get("published_from") != (fresh or {}).get("pin"):
            problems.append("%s: published_from %r != upstream pin %r"
                            % (study, block.get("published_from"), (fresh or {}).get("pin")))
        if (block.get("published") or {}).get("numbers") != fresh.get("numbers"):
            problems.append("%s: published numbers drifted from the upstream face" % study)
        for sha, c in (block.get("cells") or {}).items():
            if c.get("same_commit_as_publication") != (sha == block.get("published_from")):
                problems.append("%s@%s: same_commit flag contradicts published_from" % (study, sha))
            if not (c.get("pinned") or {}).get("population_source"):
                problems.append("%s@%s: replay does not publish its population source"
                                % (study, sha))
            if (published.get("pins") or {}).get(sha, {}).get("count") is None:
                problems.append("%s@%s: cell has no pin behind it" % (study, sha))
            for key, row in (c.get("compare") or {}).items():
                want, got = row.get("published"), row.get("pinned")
                delta = (got - want) if isinstance(got, (int, float)) \
                    and isinstance(want, (int, float)) else None
                if delta != row.get("delta"):
                    problems.append("%s@%s/%s: delta %r does not re-derive from %r,%r"
                                    % (study, sha[:8], key, row.get("delta"), want, got))
                if row.get("reproduced") is not None and (delta == 0) != row.get("reproduced"):
                    problems.append("%s@%s/%s: reproduced contradicts its own delta"
                                    % (study, sha[:8], key))
    verdict, own = decide(published.get("matrix") or {})
    if verdict != published.get("verdict"):
        problems.append("verdict does not re-derive: %r != %r"
                        % (published.get("verdict"), verdict))
    if own != published.get("reproduces_at_own_pin"):
        problems.append("reproduces_at_own_pin does not re-derive")
    say("verify problems=%s" % problems)
    if problems:
        return 1
    if write_face:
        face = build(write_face=True)
        return 0 if face.get("verdict") == published.get("verdict") else 1
    return 0


def _fixture_cell(reproduced, key="k"):
    return {"compare": {key: {"published": 10, "pinned": 10 if reproduced else 11,
                              "delta": 0 if reproduced else 1, "reproduced": reproduced}}}


def selftest():
    legs = []

    def leg(name, ok, detail=""):
        legs.append((name, bool(ok), detail))

    pubs = {s: published_numbers(s) for s in STUDIES}
    pins = {s: (pubs.get(s) or {}).get("pin") for s in STUDIES}
    leg("both upstream faces record a publishing commit", all(pins.values()), str(pins))
    leg("the two studies were published from different commits (the card's premise)",
        pins["E350"] != pins["E353"], "%s vs %s" % (pins["E350"], pins["E353"]))
    leg("their evidence cutoffs differ, which is what a two-vintage replay looks like",
        (pubs["E350"] or {}).get("evidence_cutoff") != (pubs["E353"] or {}).get("evidence_cutoff"),
        "%s vs %s" % ((pubs["E350"] or {}).get("evidence_cutoff"),
                      (pubs["E353"] or {}).get("evidence_cutoff")))
    k350 = set(((pubs["E350"] or {}).get("numbers") or {}).keys())
    k353 = set(((pubs["E353"] or {}).get("numbers") or {}).keys())
    leg("the two studies publish disjoint key sets, so no key may be compared across studies",
        not (k350 & k353), "shared=%s" % sorted(k350 & k353))

    head = e369._git(["rev-parse", "HEAD"]).stdout.decode().strip()
    members = tree_members(head)
    leg("the walk still names corpus members from a tree and every one is python under a corpus dir",
        bool(members) and all(m.endswith(".py") for m in members), str(len(members)))
    leg("a path the commit does not hold reads back as nothing, not as empty text",
        e369.read_blobs(head, ["scripts/_e373_absent_fixture.py"]) == {})

    # the decision rule, on fixtures: three shapes must give three verdicts
    both_own = {"E350": {"published_from": "a", "cells": {"a": _fixture_cell(True),
                                                          "b": _fixture_cell(False)}},
                "E353": {"published_from": "b", "cells": {"a": _fixture_cell(False),
                                                          "b": _fixture_cell(True)}}}
    one_pin = {"E350": {"published_from": "a", "cells": {"a": _fixture_cell(True),
                                                         "b": _fixture_cell(True)}},
               "E353": {"published_from": "a", "cells": {"a": _fixture_cell(True),
                                                         "b": _fixture_cell(True)}}}
    none = {"E350": {"published_from": "a", "cells": {"a": _fixture_cell(False),
                                                      "b": _fixture_cell(False)}},
            "E353": {"published_from": "b", "cells": {"a": _fixture_cell(False),
                                                      "b": _fixture_cell(False)}}}
    leg("each study reproducing only at its own pin yields the per-study verdict",
        decide(both_own)[0] == V_PER_STUDY)
    leg("both studies reproducing at one commit yields the one-pin verdict",
        decide(one_pin)[0] == V_ONE_PIN)
    leg("nothing reproducing anywhere yields the empty verdict, never a silent pass",
        decide(none)[0] == V_NONE)
    partial = {"E350": {"published_from": "a", "cells": {"a": _fixture_cell(True),
                                                         "b": _fixture_cell(False)}},
               "E353": {"published_from": "b", "cells": {"a": _fixture_cell(False),
                                                         "b": _fixture_cell(False)}}}
    leg("one study reproducing and the other not yields mixed, not the tidier per-study claim",
        decide(partial)[0] == V_MIXED)

    leg("an empty flag set never reads as reproduced (a fold over nothing must not say yes)",
        reproduced_anywhere({"k": {"reproduced": None}}) is False)
    leg("the pin reader reuses a same-commit pin file instead of restamping its study name",
        _pin_reuse_holds(), "")

    passed = sum(1 for _, ok, _ in legs if ok)
    for name, ok, detail in legs:
        say("%s %s%s" % ("PASS" if ok else "FAIL", name, ("-- " + detail) if detail else ""))
    say("selftest %d/%d" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


def _pin_reuse_holds():
    """A pin already on disk for the same commit must be returned verbatim, not restamped."""
    pubs = published_numbers("E350")
    sha = (pubs or {}).get("pin")
    if not sha:
        return False
    path = os.path.join(OUTDIR, PIN_NAME % sha[:8])
    if not os.path.exists(path):
        return True  # nothing on disk to reuse: the rule is vacuously satisfied
    before = _sha256(open(path, "r", encoding="utf-8").read())
    pin, got_path, how = build_pin(sha)
    after = _sha256(open(path, "r", encoding="utf-8").read())
    return how == "reused" and before == after and pin.get("git_commit") == sha


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "run":
        face = build(write_face=True)
        say("verdict: %s" % face["verdict"])
        for study in STUDIES:
            block = (face["matrix"] or {}).get(study) or {}
            for sha, c in (block.get("cells") or {}).items():
                moved = [k for k, r in (c.get("compare") or {}).items() if r.get("reproduced") is False]
                say("  %s @%s: %d/%d keys reproduced%s"
                    % (study, sha[:8], sum(1 for r in (c.get("compare") or {}).values()
                                           if r.get("reproduced")), len(c.get("compare") or {}),
                       (" moved=" + ",".join(sorted(moved))) if moved else ""))
        for sha, bill in (face["store_bills"] or {}).items():
            say("  bill @%s: disk pin %s -> absent %s, bytes_differ %s"
                % (sha[:8], bill.get("disk_pin_members"), bill.get("absent"),
                   bill.get("bytes_differ")))
        return 0
    if cmd == "verify":
        return verify()
    if cmd == "selftest":
        return selftest()
    say(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))