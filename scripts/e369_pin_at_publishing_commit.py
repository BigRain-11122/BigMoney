"""E369 -- take the pin at the commit the face was published from, and see if the number comes back.

E368 replayed E350 and E353 over a corpus pin taken on 11-02, the day AFTER E350's face was
published, and every arm reproduced the verdict number.  A number that reproduces over a different
vintage is *stable*, not *pinned*; the two findings permit different sentences and only one of them
lets a reader say "the pin covers the face".

So this study takes the pin where a pin is supposed to be taken: at the commit the face itself
records as its ``pin``.  The vintage is machine-read from E350's published face, never written into
this file, so a re-publish cannot silently keep pointing at a stale commit.  The population and the
bytes are both read from that tree -- ``git ls-tree`` names the members, ``git cat-file --batch``
supplies their text -- so nothing in this replay is borrowed from today's disk.

It then answers the three questions the queue card asked, as measurements:

  corpus_sources        -- does E350 come back at the 2343 its face published?
  fields_with_no_writer -- does it come back at 1698?
  the bill              -- how many members of the publish-day population a pin at that commit
                           cannot supply, i.e. how many must be STORED rather than fetched

The bill is measured against the disk pin the census family recorded on 11-02 (E361's
``CORPUSPIN-2026-11-02.json``).  That pin is not the face's own population -- it holds 2368 members
while the face counted 2343 sources -- so the bill is published as a bound on the same population
family, never as the face's exact member list.

Usage:
  python scripts/e369_pin_at_publishing_commit.py run       # walk the commit, replay, publish
  python scripts/e369_pin_at_publishing_commit.py verify    # re-derive what needs no scan
  python scripts/e369_pin_at_publishing_commit.py selftest  # offline fixture legs
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e346_status_writer_unread as e346  # noqa: E402  (the corpus rule, imported not copied)
import e350_field_branch_census as e350  # noqa: E402
import e353_unwritten_guard_presence as e353  # noqa: E402

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
TODAY = "2026-11-02"
FACE = "PUBLISHPIN-%s.json" % TODAY
LATEST = "publishpin_latest.json"
STUDY = "E369_pin_at_publishing_commit"
SELF_REL = "scripts/e369_pin_at_publishing_commit.py"

E350_FACE = os.path.join(OUTDIR, "fieldbranch_latest.json")
E353_FACE = os.path.join(OUTDIR, "guardpresence_latest.json")
DISK_PIN = os.path.join(OUTDIR, "CORPUSPIN-2026-11-02.json")

# The pin file this study writes is named after the commit it holds, so two vintages cannot be
# mistaken for one another the way a date-stamped pin can (E366's whole complaint).
PIN_NAME = "CORPUSPIN-AT-COMMIT-%s.json"

# The corpus rule is E346's, imported rather than copied -- a pin that described a different
# population than the study counts would be a second, private definition of the corpus.
CORPUS_DIRS = tuple(e346.CORPUS_DIRS)
CORPUS_FILES = tuple(e346.CORPUS_FILES)

V_REPRODUCED = ("a_pin_taken_at_the_publishing_commit_reproduces_the_published_numbers_so_"
                "stability_and_provenance_coincide_and_the_bill_is_one_pin_per_vintage")
V_MOVED = ("a_pin_taken_at_the_publishing_commit_does_not_reproduce_the_published_corpus_size_"
           "%d_against_%d_so_the_face_was_built_from_a_tree_no_commit_holds_and_the_bill_is_a_pin_"
           "plus_a_store_per_vintage")
V_BYTES_ONLY = ("a_pin_taken_at_the_publishing_commit_reproduces_the_population_but_not_the_"
                "published_numbers_so_the_difference_lives_in_the_bytes_not_in_the_member_list")
V_EMPTY = "no_corpus_at_the_publishing_commit_so_no_claim_is_made"


def say(message):
    print(message, flush=True)


def _sha256(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _norm(text):
    """The bytes a census reads: text mode folds CRLF and a lone CR to LF before anyone hashes it."""
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _git(args, **kwargs):
    return subprocess.run(["git", "-C", ROOT] + args, capture_output=True, **kwargs)


def tree_members(commit):
    """Every corpus member at ``commit`` -- names from the tree, not from today's disk."""
    out = _git(["ls-tree", "-r", "--name-only", "-z", commit])
    if out.returncode != 0:
        raise RuntimeError("git ls-tree %s failed: %s"
                           % (commit, out.stderr.decode("utf-8", errors="replace")[:300]))
    names = [n for n in out.stdout.decode("utf-8", errors="replace").split("\0") if n]
    under = tuple(d + "/" for d in CORPUS_DIRS)
    members = [n for n in names if n.endswith(".py") and n.startswith(under)]
    members += [n for n in CORPUS_FILES if n in names]
    return sorted(set(members))


def read_blobs(commit, paths):
    """``{path: text}`` straight from the object store, one ``cat-file --batch`` pass."""
    if not paths:
        return {}
    payload = b"".join(("%s:%s\n" % (commit, p)).encode("utf-8") for p in paths)
    proc = subprocess.run(["git", "-C", ROOT, "cat-file", "--batch"], input=payload,
                          capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError("git cat-file --batch failed: %s"
                           % proc.stderr.decode("utf-8", errors="replace")[:300])
    stream, out, index = proc.stdout, {}, 0
    for path in paths:
        nl = stream.find(b"\n", index)
        if nl < 0:
            break
        header = stream[index:nl].decode("utf-8", errors="replace")
        index = nl + 1
        parts = header.split()
        if len(parts) < 3 or parts[-1] in ("missing", "ambiguous"):
            continue
        size = int(parts[2])
        body = stream[index:index + size]
        index += size + 1  # the trailing newline git writes after each object
        out[path] = _norm(body.decode("utf-8", errors="replace"))
    return out


def build_pin(commit):
    """The corpus pin at ``commit``: members and bytes from that tree, digest over the pairs."""
    paths = tree_members(commit)
    blobs = read_blobs(commit, paths)
    sources = [{"path": p, "sha256": _sha256(blobs[p]), "bytes": len(blobs[p].encode("utf-8"))}
               for p in paths if p in blobs]
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
    return pin


def load_json(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def published_numbers(study):
    path = E350_FACE if study == "E350" else E353_FACE
    if not os.path.exists(path):
        return None
    face = load_json(path)
    summary = face.get("summary") or {}
    if study == "E350":
        keys = ("corpus_sources", "fields_with_no_writer", "guard_fields_with_no_writer",
                "fields", "guard_fields")
    else:
        keys = ("pairs", "guard_never_fires_on_a_falsy_value", "by_class", "by_state")
    return {"face": os.path.relpath(path, ROOT).replace("\\", "/"),
            "pin": face.get("pin"),
            "evidence_cutoff": face.get("evidence_cutoff"),
            "numbers": {k: summary.get(k) for k in keys}}


def _replayed_numbers(study, face):
    summary = face.get("summary") or {}
    if study == "E350":
        keys = ("corpus_sources", "fields_with_no_writer", "guard_fields_with_no_writer",
                "fields", "guard_fields")
    else:
        keys = ("pairs", "guard_never_fires_on_a_falsy_value", "by_class", "by_state")
    return {k: summary.get(k) for k in keys}


def compare(published, replayed):
    """Per key: the published number, the pinned number, and the delta -- measured, never asserted."""
    rows = {}
    for key, want in (published or {}).get("numbers", {}).items():
        got = (replayed or {}).get(key)
        delta = (got - want) if isinstance(got, (int, float)) and isinstance(want, (int, float)) \
            else None
        rows[key] = {"published": want, "pinned": got, "delta": delta,
                     "reproduced": delta == 0 if delta is not None else None}
    return rows


def store_bill(commit, disk_pin_path=DISK_PIN):
    """How much of the publish-day population a pin at ``commit`` cannot fetch.

    ``absent``     -- the path does not exist at that commit, so its bytes only exist in a store;
    ``bytes_differ``-- the path exists but the commit's bytes are not the bytes the pin recorded.
    Both are populations with paths, never a bare count.
    """
    if not os.path.exists(disk_pin_path):
        return {"measured": False, "reason": "no disk pin at %s"
                % os.path.relpath(disk_pin_path, ROOT).replace("\\", "/")}
    pin = load_json(disk_pin_path)
    rows = pin.get("sources") or []
    paths = [r.get("path") for r in rows if r.get("path")]
    blobs = read_blobs(commit, paths)
    absent, differ = [], []
    for row in rows:
        path = row.get("path")
        if not path:
            continue
        if path not in blobs:
            absent.append(path)
        elif _sha256(blobs[path]) != row.get("sha256"):
            differ.append(path)
    return {"measured": True,
            "commit": commit,
            "disk_pin": os.path.relpath(disk_pin_path, ROOT).replace("\\", "/"),
            "disk_pin_members": len(paths),
            "fetched_from_commit": len(paths) - len(absent),
            "absent": len(absent),
            "bytes_differ": len(differ),
            "must_be_stored": len(absent),
            "absent_paths": absent,
            "bytes_differ_paths": differ}


def decide(studies, bill, pin):
    if not pin.get("count"):
        return V_EMPTY
    e350_cmp = ((studies.get("E350") or {}).get("compare") or {})
    corpus = e350_cmp.get("corpus_sources") or {}
    fields = e350_cmp.get("fields_with_no_writer") or {}
    if corpus.get("reproduced") is False:
        return V_MOVED % (corpus.get("pinned") or 0, corpus.get("published") or 0)
    if corpus.get("reproduced") and fields.get("reproduced") is False:
        return V_BYTES_ONLY
    return V_REPRODUCED


def build(write_face=True):
    published_350 = published_numbers("E350")
    target = (published_350 or {}).get("pin")
    if not target:
        raise RuntimeError("E350's face does not record the commit it was published from")
    say("publishing commit: %s" % target)
    pin = build_pin(target)
    say("corpus at that commit: %d members, pin_id %s" % (pin["count"], pin["pin_id"]))
    pin_path = os.path.join(OUTDIR, PIN_NAME % target[:8])
    os.makedirs(OUTDIR, exist_ok=True)
    with open(pin_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(pin, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    members = [(row["path"], read_blobs(target, [row["path"]])[row["path"]])
               for row in pin["sources"]]
    studies = {}
    for study in ("E350", "E353"):
        mod = e350 if study == "E350" else e353
        say("%s: replay over the pinned bytes" % study)
        face = mod.build(files=members)
        published = published_numbers(study)
        replayed = _replayed_numbers(study, face)
        studies[study] = {"published": published,
                          "pinned": {"population_source": face.get("population_source"),
                                     "numbers": replayed},
                          "compare": compare(published, replayed),
                          "same_commit": bool((published or {}).get("pin")) and
                                         (published or {}).get("pin") == target}
    bill = store_bill(target)
    face = {"study": STUDY,
            "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
            "evidence_cutoff": TODAY,
            "source": SELF_REL,
            "pin": target,
            "pin_id": pin["pin_id"],
            "pin_file": os.path.relpath(pin_path, ROOT).replace("\\", "/"),
            "pin_members": pin["count"],
            "population_source": "pinned_bytes:%d@%s" % (pin["count"], target[:8]),
            "verdict": decide(studies, bill, pin),
            "studies": studies,
            "store_bill": bill,
            "bound": ("the pin is taken at the commit E350's own face records, so provenance is "
                      "whatever that field says; the corpus rule is E346's walk but the members "
                      "come from the tree, which means a file untracked at publish time is not in "
                      "the pin at all and shows up only in the bill -- and the bill is measured "
                      "against E361's disk pin (a population of the same family, not the face's "
                      "own member list), so 'must be stored' is a bound on that population, not a "
                      "reconstruction of the face's exact input")}
    if write_face:
        for target_path in (os.path.join(OUTDIR, FACE), os.path.join(OUTDIR, LATEST)):
            with open(target_path, "w", encoding="utf-8", newline="\n") as fh:
                json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
                fh.write("\n")
    return face


def verify():
    """Re-derive every check that does not need a corpus scan."""
    dated = os.path.join(OUTDIR, FACE)
    if not os.path.exists(dated):
        say("no published face")
        return 2
    published = load_json(dated)
    problems = []
    target = (published_numbers("E350") or {}).get("pin")
    if published.get("pin") != target:
        problems.append("pin %r != E350 face pin %r" % (published.get("pin"), target))
    if not target:
        problems.append("E350's face no longer records a pin")
    else:
        pin = build_pin(target)
        if published.get("pin_members") != pin["count"]:
            problems.append("pin_members %r != walked %d"
                            % (published.get("pin_members"), pin["count"]))
        if published.get("pin_id") != pin["pin_id"]:
            problems.append("pin_id does not re-derive from the tree")
        bill = store_bill(target)
        for key in ("disk_pin_members", "absent", "bytes_differ", "must_be_stored"):
            if (published.get("store_bill") or {}).get(key) != bill.get(key):
                problems.append("store_bill %s %r != %r"
                                % (key, (published.get("store_bill") or {}).get(key), bill.get(key)))
        verdict = decide(published.get("studies") or {}, bill, pin)
        if verdict != published.get("verdict"):
            problems.append("verdict does not re-derive: %r != %r"
                            % (published.get("verdict"), verdict))
    for study, block in (published.get("studies") or {}).items():
        fresh = published_numbers(study)
        if fresh is None:
            problems.append("%s: upstream face missing" % study)
            continue
        if (block.get("published") or {}).get("numbers") != fresh.get("numbers"):
            problems.append("%s: published numbers drifted from the upstream face" % study)
        if not (block.get("pinned") or {}).get("population_source"):
            problems.append("%s: replay does not publish its population source" % study)
        for key, row in (block.get("compare") or {}).items():
            want, got = row.get("published"), row.get("pinned")
            delta = (got - want) if isinstance(got, (int, float)) and isinstance(want, (int, float)) \
                else None
            if delta != row.get("delta"):
                problems.append("%s/%s: delta %r does not re-derive from %r,%r"
                                % (study, key, row.get("delta"), want, got))
            if row.get("reproduced") is not None and (delta == 0) != row.get("reproduced"):
                problems.append("%s/%s: reproduced flag contradicts its own delta" % (study, key))
    say("verify problems=%s" % problems)
    return 0 if not problems else 1


def selftest():
    legs = []

    def leg(name, ok, detail=""):
        legs.append((name, bool(ok), detail))

    head = _git(["rev-parse", "HEAD"]).stdout.decode().strip()
    members = tree_members(head)
    leg("the walk names members from a tree, and every one of them is python under a corpus dir",
        bool(members) and all(m.endswith(".py") for m in members), str(len(members)))
    # the study under test is tracked, so it is in the tree; the exclusion still holds at walk time
    studies_self = e350.SELF_REL
    leg("the study's own source is in the pin, and the study excludes it at walk time",
        studies_self in members and studies_self not in [p for p, _ in e350._sources(members)],
        "%s -> %d sources" % (studies_self, len(e350._sources(members))))

    blobs = read_blobs(head, members[:3])
    leg("bytes come back for every path the tree named", len(blobs) == 3, str(sorted(blobs)))
    leg("batch reads fold CRLF, so a pin digest cannot drift with the checkout's line endings",
        all("\r" not in text for text in blobs.values()))
    leg("a path the commit does not hold reads back as nothing rather than as empty text",
        read_blobs(head, ["scripts/_no_such_member_fixture.py"]) == {})

    pin = build_pin(head)
    leg("the pin digest is over the sorted (path, sha256) pairs and is stable across two builds",
        pin["pin_id"] == build_pin(head)["pin_id"] and pin["count"] == len(pin["sources"]))
    all_blobs = read_blobs(head, members)
    leg("the pin counts what the walk named",
        pin["count"] == len([m for m in members if m in all_blobs]),
        "%d vs %d" % (pin["count"], len(all_blobs)))

    # a bill against a fixture pin: one member absent, one present with other bytes, one exact
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        fixture = os.path.join(tmp, "pin.json")
        sample = members[0]
        text = blobs.get(sample)
        rows = [{"path": sample, "sha256": _sha256(text)} if text else None,
                {"path": "scripts/_absent_bill_fixture.py", "sha256": "0" * 64}]
        with open(fixture, "w", encoding="utf-8") as fh:
            json.dump({"sources": [r for r in rows if r]}, fh)
        bill = store_bill(head, fixture)
    leg("the bill charges every member a commit cannot fetch, and nothing a commit can",
        bill["must_be_stored"] == 1 and bill["absent"] == 1 and bill["bytes_differ"] == 0,
        str({k: bill[k] for k in ("disk_pin_members", "fetched_from_commit", "absent",
                                  "bytes_differ")}))

    # the verdict must be driven by the measured delta, not by which study happens to have run
    moved = {"E350": {"compare": {"corpus_sources": {"published": 2343, "pinned": 2251,
                                                     "delta": -92, "reproduced": False}}}}
    same = {"E350": {"compare": {"corpus_sources": {"published": 2343, "pinned": 2343,
                                                    "delta": 0, "reproduced": True}}}}
    leg("a moved population chooses the moved verdict",
        decide(moved, {"measured": True}, {"count": 5}).startswith(
            "a_pin_taken_at_the_publishing_commit_does_not_reproduce"))
    leg("a reproduced population chooses the provenance verdict",
        decide(same, {"measured": True}, {"count": 5}) == V_REPRODUCED)
    leg("an empty pin claims nothing", decide({}, {}, {"count": 0}) == V_EMPTY)

    published = published_numbers("E350") or {}
    face_pin = published.get("pin") or ""
    leg("the target commit is read from the face, not hardcoded in this file",
        "%s" % ("daf9a897" not in open(os.path.join(ROOT, SELF_REL), encoding="utf-8").read()),
        str(face_pin))

    failed = [n for n, ok, _ in legs if not ok]
    for name, ok, detail in legs:
        say(("PASS " if ok else "FAIL ") + name + (("  [" + detail + "]") if not ok and detail else ""))
    say("selftest %d/%d" % (len(legs) - len(failed), len(legs)))
    return 0 if not failed else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "verify").lower()
    if cmd == "run":
        face = build()
        say("verdict: %s" % face["verdict"])
        for study, block in face["studies"].items():
            say("%s: %s" % (study, {k: (v.get("published"), v.get("pinned"))
                                    for k, v in (block.get("compare") or {}).items()
                                    if v.get("delta") is not None}))
        bill = face["store_bill"]
        say("bill: %s" % {k: bill.get(k) for k in ("disk_pin_members", "absent",
                                                   "bytes_differ", "must_be_stored")})
        return 0
    if cmd == "verify":
        return verify()
    if cmd == "selftest":
        return selftest()
    say("usage: run | verify | selftest")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))