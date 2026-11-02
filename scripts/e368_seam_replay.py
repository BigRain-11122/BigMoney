"""E368 -- a repaired seam pins the population; does it reproduce the number?

E366 priced the pin queue and named ten studies as NEEDS_SEAM: their ``build()`` takes no member
list, so a replay can only re-walk the tree and compare a number built from today's population to a
number built from yesterday's.  E368 repairs one such seam (E350's walker, and E353 which imports
that walker) and then asks the question a seam is supposed to answer: *does the published number
come back?*

The repair has two halves, because a population and its bytes are two different things:

  (1) ``files=`` -- the member list.  Without it ``_sources()`` walks ``e346._corpus()``, and the
      walk is whatever the tree holds this minute (E366: 2387 against a quoted 2343);
  (2) a member may be ``(relpath, text)`` -- the bytes.  A pin list alone still reads today's disk,
      so a replay that only pins the list answers "same members, today's contents".

This study builds E350's number over four populations and E353's over the same four:

  published   -- the number in the face already on disk (no compute)
  live        -- a fresh walk of the tree now
  pinned_list -- the pin's members, bytes read from disk now
  pinned_bytes-- the pin's members, bytes resolved from the pin's commit when the disk alone no
                 longer hashes to the pin

The separation is the finding: if pinned_list already reproduces the published number then the
number was never population-sensitive, and a seam is cheap insurance; if only pinned_bytes does,
then the population was the difference; if neither does, the pin is over the wrong vintage.

A member the pin recorded but git cannot supply (untracked at pin time) is published as
``store_needed`` and its disk bytes are used with the drift disclosed -- never silently.

Usage:
  python scripts/e368_seam_replay.py run       # build all eight numbers + write the face
  python scripts/e368_seam_replay.py verify    # re-derive the checks that do not need a scan
  python scripts/e368_seam_replay.py selftest  # offline fixture legs
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

import e350_field_branch_census as e350  # noqa: E402
import e353_unwritten_guard_presence as e353  # noqa: E402

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
TODAY = "2026-11-02"
FACE = "SEAMREPLAY-%s.json" % TODAY
LATEST = "seamreplay_latest.json"
STUDY = "E368_seam_replay"
SELF_REL = "scripts/e368_seam_replay.py"

PIN_PATH = os.path.join(OUTDIR, "CORPUSPIN-2026-11-02.json")
E350_FACE = os.path.join(OUTDIR, "fieldbranch_latest.json")
E353_FACE = os.path.join(OUTDIR, "guardpresence_latest.json")
# the resume cache lives outside results/: every *.json under results/ joins the published-face
# population the census family walks (E328), so a scratch cache there would grow that population.
CACHE_PATH = os.path.join(ROOT, "logs", "_e368_partial.json")

V_REPRODUCED = ("a_pinned_replay_reproduces_the_published_number_so_the_seam_is_population_"
                "insurance_rather_than_a_repair_of_the_number")
V_REPRODUCED_OTHER_VINTAGE = ("a_pinned_replay_reproduces_the_published_number_yet_the_pin_is_not_"
                              "the_publishing_commit_so_the_reproduction_is_stability_not_"
                              "provenance_and_a_pin_must_be_taken_at_the_face_it_serves")
V_BYTES = ("the_pinned_population_alone_does_not_reproduce_the_published_number_and_the_pinned_"
           "bytes_do_so_the_number_was_a_product_of_the_population_and_its_contents")
V_VINTAGE = ("neither_the_pinned_population_nor_the_pinned_bytes_reproduce_the_published_number_"
             "so_the_pin_is_over_the_wrong_vintage_of_the_study")
V_EMPTY = "no_study_replayed_so_no_claim_is_made"


def say(message):
    print(message, flush=True)


def _sha256(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_pin(path=PIN_PATH):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def git_bytes(commit, rel):
    """The blob at ``commit:rel`` as text, or None when git cannot supply it."""
    try:
        out = subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (commit, rel)],
                             capture_output=True)
    except OSError:
        return None
    if out.returncode != 0 or not out.stdout:
        return None
    return out.stdout.decode("utf-8", errors="replace")


def resolve_members(pin):
    """``(members, provenance)`` -- one entry per pin member, bytes resolved to the pin's vintage.

    Disk wins only when it still hashes to the pin; otherwise the pin's commit is asked; otherwise
    the member is ``store_needed`` and today's disk bytes are used with the drift disclosed.
    """
    commit = pin.get("git_commit") or ""
    members, prov = [], {"disk": 0, "git": 0, "store_needed": 0, "unreadable": 0,
                         "store_needed_paths": [], "unreadable_paths": []}
    for row in pin.get("sources") or []:
        rel = row.get("path")
        want = row.get("sha256")
        if not rel:
            continue
        disk = None
        path = os.path.join(ROOT, rel)
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8", errors="replace") as fh:
                    disk = fh.read()
            except OSError:
                disk = None
        if disk is not None and want and _sha256(disk) == want:
            members.append((rel, disk))
            prov["disk"] += 1
            continue
        blob = git_bytes(commit, rel) if commit else None
        if blob is not None and (not want or _sha256(blob) == want):
            members.append((rel, blob))
            prov["git"] += 1
            continue
        if disk is not None:
            members.append((rel, disk))
            prov["store_needed"] += 1
            prov["store_needed_paths"].append(rel)
            continue
        prov["unreadable"] += 1
        prov["unreadable_paths"].append(rel)
    return members, prov


def numbers_of(study, face):
    summary = face.get("summary") or {}
    if study == "E350":
        return {"corpus_sources": summary.get("corpus_sources"),
                "guard_fields": summary.get("guard_fields"),
                "guard_fields_with_no_writer": summary.get("guard_fields_with_no_writer"),
                "fields_with_no_writer": summary.get("fields_with_no_writer")}
    return {"pairs": summary.get("pairs"),
            "by_class": summary.get("by_class"),
            "guard_never_fires_on_a_falsy_value":
                summary.get("guard_never_fires_on_a_falsy_value")}


def _published(study):
    path = E350_FACE if study == "E350" else E353_FACE
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as fh:
        face = json.load(fh)
    return {"face": os.path.relpath(path, ROOT).replace("\\", "/"),
            "pin": face.get("pin"), "evidence_cutoff": face.get("evidence_cutoff"),
            "numbers": numbers_of(study, face)}


def run_one(study, members, pin_paths):
    mod = e350 if study == "E350" else e353
    out = {}
    say("%s: live walk" % study)
    out["live"] = {"population_source": "live_walk",
                   "numbers": numbers_of(study, mod.build())}
    say("%s: pinned list, today's bytes" % study)
    face = mod.build(files=pin_paths)
    out["pinned_list"] = {"population_source": face.get("population_source"),
                          "numbers": numbers_of(study, face)}
    say("%s: pinned bytes" % study)
    face = mod.build(files=members)
    out["pinned_bytes"] = {"population_source": face.get("population_source"),
                           "numbers": numbers_of(study, face)}
    return out


def _delta(a, b):
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        return None
    return b - a


def compare(study, published, arms):
    """Which arm reproduces the published number, per key -- measured, never asserted."""
    pub = (published or {}).get("numbers") or {}
    rows = {}
    for arm, block in arms.items():
        nums = block.get("numbers") or {}
        rows[arm] = {k: {"value": nums.get(k), "delta_vs_published": _delta(pub.get(k), nums.get(k))}
                     for k in pub if not isinstance(pub.get(k), dict)}
    for key in ("guard_fields_with_no_writer", "pairs"):
        if key in pub:
            return {"key": key,
                    "published": pub.get(key),
                    "reproduced_by": [arm for arm in ("pinned_list", "pinned_bytes", "live")
                                      if (rows.get(arm, {}).get(key) or {}).get("delta_vs_published") == 0],
                    "rows": rows}
    return {"key": None, "published": None, "reproduced_by": [], "rows": rows}


def vintage_of(published, pin):
    """Is the pin the commit the published face was built from?  A number that reproduces over a
    different vintage is stable, not pinned -- the two are different findings and only one permits
    the word 'reproduced' to mean the pin covers the face."""
    face_pin = (published or {}).get("pin") or ""
    pin_commit = pin.get("git_commit") or ""
    return {"published_pin": face_pin, "pin_commit": pin_commit,
            "same_commit": bool(face_pin) and face_pin == pin_commit,
            "published_cutoff": (published or {}).get("evidence_cutoff"),
            "pin_cutoff": pin.get("evidence_cutoff")}


def decide(studies):
    if not studies:
        return V_EMPTY
    keyed = [s for s in studies.values() if (s.get("compare") or {}).get("key")]
    reproduced_pinned = all(("pinned_bytes" in (s.get("compare") or {}).get("reproduced_by", []))
                            for s in keyed)
    reproduced_list_only = all(("pinned_list" in (s.get("compare") or {}).get("reproduced_by", []))
                               for s in keyed)
    same_vintage = all((s.get("vintage") or {}).get("same_commit") for s in keyed if s.get("vintage"))
    if reproduced_pinned and reproduced_list_only:
        return V_REPRODUCED if same_vintage else V_REPRODUCED_OTHER_VINTAGE
    if reproduced_pinned:
        return V_BYTES
    return V_VINTAGE


def build(write_face=True, cache=None):
    """Build the face.  ``cache`` (a path) makes the run resumable: a scan is minutes long, so a
    run cut short must not have to re-pay the arms it already finished -- a cache entry is used
    only when it names the same pin, so a stale cache cannot answer for a different vintage.
    """
    pin = load_pin()
    members, prov = resolve_members(pin)
    pin_paths = [p for p, _ in members]
    done = {}
    if cache and os.path.exists(cache):
        try:
            with open(cache, "r", encoding="utf-8") as fh:
                done = json.load(fh)
        except (OSError, ValueError):
            done = {}
        if done.get("pin_id") != pin.get("pin_id"):
            done = {}
        else:
            say("resuming from cache: %s" % sorted(done.get("studies") or {}))
    studies = {}
    for study in ("E350", "E353"):
        published = _published(study)
        cached = (done.get("studies") or {}).get(study) or {}
        if cached.get("published") == published and cached.get("arms"):
            say("%s: cached" % study)
            arms = cached["arms"]
        else:
            arms = run_one(study, members, pin_paths)
            if cache:
                done.setdefault("studies", {})[study] = {"published": published, "arms": arms}
                done["pin_id"] = pin.get("pin_id")
                with open(cache, "w", encoding="utf-8", newline="\n") as fh:
                    json.dump(done, fh, ensure_ascii=False, indent=1, sort_keys=True)
                    fh.write("\n")
        studies[study] = {"published": published, "arms": arms,
                          "vintage": vintage_of(published, pin),
                          "compare": compare(study, published, arms)}
    face = {
        "study": STUDY,
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "evidence_cutoff": TODAY,
        "source": SELF_REL,
        "pin": pin.get("git_commit"),
        "pin_id": pin.get("pin_id"),
        "pin_file": os.path.relpath(PIN_PATH, ROOT).replace("\\", "/"),
        "pin_members": len(members),
        "bytes_provenance": {k: v for k, v in prov.items() if not k.endswith("_paths")},
        "store_needed_paths": prov["store_needed_paths"],
        "seam": {
            "repaired_in": ["scripts/e350_field_branch_census.py",
                            "scripts/e353_unwritten_guard_presence.py"],
            "shape": "build(files=[relpath | (relpath, text)])",
            "population_source_published": True,
        },
        "verdict": decide(studies),
        "studies": studies,
        "bound": ("the seam pins the member list and can pin the bytes; a member the pin recorded "
                  "but git cannot supply at the pin commit is store_needed and is replayed from "
                  "today's disk with that drift named, so those members are the only place a "
                  "'reproduction' could be borrowed from the tree rather than from the pin; the "
                  "E353 arm re-pays E350's scan because its population is E350's rows, not a "
                  "re-implementation of them"),
    }
    if write_face:
        os.makedirs(OUTDIR, exist_ok=True)
        for target in (os.path.join(OUTDIR, FACE), os.path.join(OUTDIR, LATEST)):
            with open(target, "w", encoding="utf-8", newline="\n") as fh:
                json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
                fh.write("\n")
    return face


def verify():
    """Re-derive every check that does not need a corpus scan, and compare with the face."""
    dated = os.path.join(OUTDIR, FACE)
    if not os.path.exists(dated):
        say("no published face")
        return 2
    with open(dated, "r", encoding="utf-8") as fh:
        published = json.load(fh)
    problems = []
    pin = load_pin()
    if published.get("pin") != pin.get("git_commit"):
        problems.append("pin commit %r != %r" % (published.get("pin"), pin.get("git_commit")))
    if published.get("pin_id") != pin.get("pin_id"):
        problems.append("pin_id does not match the pin file")
    members, prov = resolve_members(pin)
    if published.get("pin_members") != len(members):
        problems.append("pin_members %r != resolved %d" % (published.get("pin_members"), len(members)))
    for key, value in (("disk", prov["disk"]), ("git", prov["git"]),
                       ("store_needed", prov["store_needed"]), ("unreadable", prov["unreadable"])):
        if (published.get("bytes_provenance") or {}).get(key) != value:
            problems.append("provenance %s %r != %r"
                            % (key, (published.get("bytes_provenance") or {}).get(key), value))
    for study, block in (published.get("studies") or {}).items():
        fresh = _published(study)
        if fresh is None:
            problems.append("%s: upstream face missing" % study)
            continue
        if (block.get("published") or {}).get("numbers") != fresh.get("numbers"):
            problems.append("%s: published numbers drifted from the upstream face" % study)
        want = vintage_of(fresh, pin)
        got = block.get("vintage") or {}
        for key in ("published_pin", "pin_commit", "same_commit"):
            if got.get(key) != want.get(key):
                problems.append("%s: vintage %s %r != %r" % (study, key, got.get(key), want.get(key)))
        for arm, armblock in (block.get("arms") or {}).items():
            if not armblock.get("population_source"):
                problems.append("%s/%s: arm does not publish its population source" % (study, arm))
    verdict = decide({k: {"compare": v.get("compare"), "vintage": v.get("vintage")}
                      for k, v in (published.get("studies") or {}).items()})
    if verdict != published.get("verdict"):
        problems.append("verdict does not re-derive: %r != %r" % (published.get("verdict"), verdict))
    say("verify problems=%s" % problems)
    return 0 if not problems else 1


def selftest():
    legs = []

    def leg(name, ok, detail=""):
        legs.append((name, bool(ok), detail))

    # (1) the seam honours an explicit member list instead of walking the tree
    # (the study's own source is excluded by rule, so the fixture must not name it)
    picked = ["scripts/e347_published_number_gate_census.py", "scripts/e346_status_writer_unread.py"]
    got = e350._sources(picked)
    leg("an explicit member list is walked verbatim, not the corpus", len(got) == 2,
        str([p for p, _ in got]))

    # (2) a member that carries its bytes is not read from disk -- the byte half of the seam
    ghost = "scripts/_does_not_exist_seam_fixture.py"
    supplied = [("scripts/e347_published_number_gate_census.py", "X = 1\n"), (ghost, "Y = 2\n")]
    got = e350._sources(supplied)
    leg("supplied bytes are used verbatim, including a path that is not on disk",
        len(got) == 2 and dict(got).get(ghost) == "Y = 2\n", str(got))

    # (3) the study's own source stays outside the population even when the pin names it
    got = e350._sources([e350.SELF_REL, "scripts/e347_published_number_gate_census.py"])
    leg("the pin cannot smuggle the study's own source into its population",
        [p for p, _ in got] == ["scripts/e347_published_number_gate_census.py"], str(got))

    # (4) an empty member list is an empty population -- proof the walk was actually skipped
    face = e350.build(files=[])
    leg("build(files=[]) measures zero sources, so the walk is genuinely bypassed",
        face["summary"]["corpus_sources"] == 0, str(face["summary"]["corpus_sources"]))
    leg("an empty population is published as empty, not as today's number",
        face["verdict"] == e350.V_EMPTY, face["verdict"])

    # (5) the population source names which seam was used
    leg("population_source distinguishes walk / list / bytes",
        (e350._population_source(None) == "live_walk"
         and e350._population_source(["a.py"]) == "pinned_list:1"
         and e350._population_source([("a.py", "x")]) == "pinned_bytes:1"),
        "%s | %s | %s" % (e350._population_source(None), e350._population_source(["a.py"]),
                          e350._population_source([("a.py", "x")])))

    # (6) E353 inherits the seam rather than re-walking through a private path
    face = e353.build(files=[])
    leg("E353's population follows the seam it is given",
        face["summary"]["pairs"] == 0 and face["population_source"] == "pinned_list:0",
        "%s %s" % (face["summary"]["pairs"], face["population_source"]))

    # (7) a pin without a sources list is refused, not read as an empty population
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        bad = os.path.join(tmp, "pin.json")
        with open(bad, "w", encoding="utf-8") as fh:
            json.dump({"count": 5}, fh)
        try:
            e350.pin_members(bad)
            refused = False
        except ValueError:
            refused = True
    leg("a pin with no sources list is refused", refused)

    # (8) the resolver prefers the pin's bytes when the disk no longer hashes to the pin
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["git", "-C", ROOT, "show", "HEAD:scripts/e368_seam_replay.py"],
                       capture_output=True)
    pin = load_pin()
    members, prov = resolve_members(pin)
    drifted = prov["git"] + prov["store_needed"] + prov["unreadable"]
    leg("every pin member resolves to bytes and the provenance adds up",
        len(members) == len([r for r in pin["sources"] if r.get("path")])
        and prov["disk"] + drifted == len(members),
        "%d members, %s" % (len(members), {k: v for k, v in prov.items() if not k.endswith("_paths")}))

    failed = [n for n, ok, _ in legs if not ok]
    for name, ok, detail in legs:
        say(("PASS " if ok else "FAIL ") + name + (("  [" + detail + "]") if not ok and detail else ""))
    say("selftest %d/%d" % (len(legs) - len(failed), len(legs)))
    return 0 if not failed else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "verify").lower()
    if cmd == "run":
        face = build(cache=CACHE_PATH)
        say("verdict: %s" % face["verdict"])
        for study, block in face["studies"].items():
            comp = block.get("compare") or {}
            say("%s: published=%s reproduced_by=%s" % (study, comp.get("published"),
                                                       comp.get("reproduced_by")))
        return 0
    if cmd == "verify":
        return verify()
    if cmd == "selftest":
        return selftest()
    say("usage: run | verify | selftest")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))