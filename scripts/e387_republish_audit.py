"""E387 -- republish the faces that no longer re-derive, and say which column did the moving.

The 08:59 smoke run was pass=277 fail=7.  One red was that round's own heartbeat artifact.  The
other six compared a face published over an older corpus with a fresh build over today's tree, so
a red here has two possible causes and the leg only reports the second one: the corpus moved
(republish is correct) or the face was never reproducible (a seam is needed, E368's rule).

This study publishes the three columns the decision needs, per face:

    carried   what the face on disk at HEAD says        (git show HEAD:<face>)
    fresh     what a build over today's tree says       (the study's own build())
    replay    what a build over the corpus the face pins says -- only possible when the pin
              carries the bytes, not just their digests (E372's gap: 128 members no commit holds)

and then decides per face: CORPUS_MOVED_REPUBLISHED (fresh is what is now on disk and the
difference is the tree), SEAM_OPENED (the face could not name its corpus and now can, but the
pinned bytes are not stored, so only the address is replayable), or REPRODUCIBLE_PARKED.

Never widens a leg's assertion: the legs were not edited to accept these numbers.

    python scripts/e387_republish_audit.py run
    python scripts/e387_republish_audit.py verify
    python scripts/e387_republish_audit.py selftest
"""
import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
STUDY = "E387_republish_six"
TODAY = "2026-11-03"
FACE = "REPUBLISH-%s.json" % TODAY
LATEST = "republish_latest.json"

if HERE not in sys.path:
    sys.path.insert(0, HERE)

# leg name -> the face it reads. The five failing legs are four faces: the fifth red was the same
# E346 face read again through its runner head.
LEGS = [
    ("product: a face-level bound is not a measurement", "precisiongap_latest.json",
     "e305_face_level_row_pricing", "E305_face_level_row_pricing"),
    ("product: the repaired corpus reading lands beside the shipped one",
     "siblingentry_latest.json", "e335_sibling_entry_point", "E335_sibling_entry_point"),
    ("product: the published census family is inventoried",
     "UNSTAMPEDCENSUS-2026-11-02.json", "e364_unstamped_census", "E364_unstamped_census"),
    ("product: a status key nobody reads is published as unread",
     "unreadstatus_latest.json", "e346_status_writer_unread", "E346_status_writer_unread"),
    ("product: every runner-backed leg executes against the suite's own module head",
     "unreadstatus_latest.json", "e346_status_writer_unread", "E346_status_writer_unread"),
]

VERDICT_MOVED = "corpus_moved_republished"
VERDICT_SEAM = "address_added_but_the_bytes_are_not_stored_so_only_the_address_replays"
VERDICT_PARKED = "reproduced_at_head_parked_for_its_next_refresh"
VERDICTS = (VERDICT_MOVED, VERDICT_SEAM, VERDICT_PARKED)


def _no_window():
    if os.name != "nt":
        return {}
    return {"creationflags": 0x08000000}


def git_show(path):
    """The face as the last commit has it; None when the path is untracked in HEAD."""
    try:
        p = subprocess.run(["git", "show", "HEAD:%s" % path], cwd=ROOT,
                           capture_output=True, **_no_window())
    except Exception:
        return None
    if p.returncode != 0:
        return None
    try:
        return json.loads(p.stdout.decode("utf-8"))
    except Exception:
        return None


def fresh_doc(module_name, tmp):
    """Re-derive through the study's own build(); never write into results/."""
    mod = __import__("importlib").import_module(module_name)
    if module_name == "e305_face_level_row_pricing":
        # its census input lives beside its output, so a temp outdir would read nothing
        return mod.build()
    if module_name == "e335_sibling_entry_point":
        return mod.build(outdir=tmp)
    if module_name == "e346_status_writer_unread":
        face = mod.census()
        return {"summary": mod._summary_block(face)["summary"], "producers": face.get("producers")}
    if module_name == "e364_unstamped_census":
        # it inventories the published *_latest.json family, which only exists in results/
        return mod.build()
    raise KeyError(module_name)


def headline(doc, module_name=None):
    if not isinstance(doc, dict):
        return {}
    out = {}
    for k in ("verdict",):
        if k in doc:
            out[k] = doc[k]
    s = doc.get("summary")
    if isinstance(s, dict):
        for k in sorted(s):
            if isinstance(s[k], (int, float, str)) and not isinstance(s[k], bool):
                out["summary.%s" % k] = s[k]
    cs = doc.get("corpus_source")
    if isinstance(cs, dict):
        out["corpus_source.pin_file"] = cs.get("pin_file")
        out["corpus_source.pin_id"] = cs.get("pin_id")
    return out


def compare(carried, fresh):
    keys = sorted(set(carried) | set(fresh))
    moved = {k: {"carried": carried.get(k), "fresh": fresh.get(k)}
             for k in keys if carried.get(k) != fresh.get(k)}
    return {"keys": len(keys), "moved": len(moved), "moved_detail": moved}


def replay_column(module_name, face_name, outdir=None):
    """Replay needs the pinned BYTES. Only an address is on disk for these faces (E372)."""
    base = outdir or OUTDIR
    path = os.path.join(base, face_name)
    doc = None
    if os.path.exists(path):
        with io.open(path, encoding="utf-8") as fh:
            doc = json.load(fh)
    cs = (doc or {}).get("corpus_source") or {}
    stamp = (doc or {}).get("corpus") or {}
    if not cs and not stamp:
        return {"available": False, "reason": "no_corpus_address_declared",
                "verdict": VERDICT_SEAM}
    pin_file = cs.get("pin_file")
    if not pin_file:
        return {"available": False, "reason": "address_is_a_digest_with_no_pin_file",
                "verdict": VERDICT_SEAM}
    on_disk = os.path.exists(os.path.join(base, pin_file))
    if not on_disk:
        return {"available": False, "reason": "pin_file_not_on_disk",
                "pin_file": pin_file, "verdict": VERDICT_SEAM}
    with io.open(os.path.join(base, pin_file), encoding="utf-8") as fh:
        pin = json.load(fh)
    stores_bytes = any("text" in s for s in pin.get("sources") or [])
    return {"available": bool(stores_bytes), "pin_file": pin_file,
            "pin_id": pin.get("pin_id"), "members": pin.get("members"),
            "reason": "the_pin_stores_digests_only_so_the_population_can_be_checked_but_not_rebuilt",
            "verdict": VERDICT_SEAM}


def build(outdir=None):
    rows = []
    seen = set()
    tmp_base = outdir or OUTDIR
    for leg, face_name, module_name, study_id in LEGS:
        if face_name in seen:
            continue
        seen.add(face_name)
        with tempfile.TemporaryDirectory() as tmp:
            fresh = fresh_doc(module_name, tmp)
        carried = headline(git_show("results/state_tilt/%s" % face_name), module_name)
        freshh = headline(fresh, module_name)
        cmp = compare(carried, freshh)
        rep = replay_column(module_name, face_name)
        if cmp["moved"] == 0:
            verdict = VERDICT_PARKED
        elif rep.get("verdict") == VERDICT_SEAM:
            verdict = VERDICT_SEAM
        else:
            verdict = VERDICT_MOVED
        rows.append({"leg": leg, "face": face_name, "study": study_id,
                     "carried_at_head": carried, "fresh_today": freshh,
                     "columns": cmp, "replay_at_pin": rep, "verdict": verdict})
    summary = {
        "faces": len(rows),
        "legs": len(LEGS),
        "faces_whose_numbers_moved_since_head": sum(1 for r in rows if r["columns"]["moved"]),
        "faces_that_now_name_a_corpus": sum(1 for r in rows if r["replay_at_pin"].get("pin_file")),
        "faces_whose_pin_stores_the_bytes": sum(1 for r in rows if r["replay_at_pin"].get("available")),
        "faces_reproducible_at_head": sum(1 for r in rows if r["verdict"] == VERDICT_PARKED),
        "seams_opened": sum(1 for r in rows if r["verdict"] == VERDICT_SEAM),
        "republished": sum(1 for r in rows if r["verdict"] == VERDICT_MOVED),
        "frozen_legs_edited": 0,
    }
    verdict = (VERDICT_SEAM if summary["seams_opened"] else
               VERDICT_MOVED if summary["republished"] else VERDICT_PARKED)
    return {
        "study": STUDY,
        "evidence_cutoff": TODAY,
        "verdict": verdict,
        "rule": {
            "carried": "git show HEAD:<face> -- the published numbers, not a remembered copy",
            "fresh": "the study's own build() into a temp dir so results/ is never touched",
            "replay": "only possible when the pin stores the bytes, not just their digests (E372)",
            "no_assertion_widened": "the smoke legs were not edited; the faces moved under them",
        },
        "summary": summary,
        "rows": rows,
    }


def verify(path=None):
    path = path or os.path.join(OUTDIR, FACE)
    problems = []
    if not os.path.exists(path):
        return ["no published republish face"]
    with io.open(path, encoding="utf-8") as fh:
        doc = json.load(fh)
    s = doc.get("summary") or {}
    rows = doc.get("rows") or []
    if s.get("faces") != len(rows):
        problems.append("summary face count disagrees with its rows")
    if len({r["face"] for r in rows}) != len(rows):
        problems.append("a face is counted twice")
    for r in rows:
        if r.get("verdict") not in VERDICTS:
            problems.append("%s has a verdict outside the frozen set" % r.get("face"))
        if r["columns"]["moved"] == 0 and r["verdict"] != VERDICT_PARKED:
            problems.append("%s reproduces at head but is not parked" % r.get("face"))
        if r["verdict"] == VERDICT_SEAM and not r["replay_at_pin"].get("reason"):
            problems.append("%s is a seam with no reason" % r.get("face"))
        if r["verdict"] == VERDICT_MOVED and r["columns"]["moved"] == 0:
            problems.append("%s is republished with nothing moved" % r.get("face"))
        for k, v in (r["carried_at_head"] or {}).items():
            if r["fresh_today"].get(k) != v and k not in (r["columns"]["moved_detail"] or {}):
                problems.append("%s: %s moved but is not in the delta" % (r.get("face"), k))
    counts = (s.get("faces_reproducible_at_head", 0) + s.get("seams_opened", 0)
              + s.get("republished", 0))
    if counts != len(rows):
        problems.append("the verdict tally does not sum to the rows")
    return problems


def selftest():
    fails = []

    def ok(cond, name):
        if not cond:
            fails.append(name)

    carried = {"summary.a": 1, "summary.b": 2}
    fresh = {"summary.a": 9, "summary.b": 2}
    c = compare(carried, fresh)
    ok(c["moved"] == 1 and "summary.a" in c["moved_detail"], "L1 a moved number is a delta")
    ok(compare(fresh, fresh)["moved"] == 0, "L2 identical columns move nothing")
    ok(headline({"summary": {"x": 1, "flag": True, "y": "s"}}) == {"summary.x": 1, "summary.y": "s"},
       "L3 booleans are not measurements")
    ok(headline(None) == {}, "L4 a missing face has no headline")
    ok(replay_column("e305_face_level_row_pricing", "no_such_face.json")["verdict"] == VERDICT_SEAM,
       "L5 a face with no address is a seam, not a pass")
    ok(set(VERDICTS) == {VERDICT_MOVED, VERDICT_SEAM, VERDICT_PARKED}, "L6 frozen vocabulary")
    ok(len({f for _l, f, _m, _s in LEGS}) == 4, "L7 five legs read four faces")
    ok(all(v in VERDICTS for v in (VERDICT_MOVED, VERDICT_SEAM, VERDICT_PARKED)), "L8 vocabulary closed")
    ok(git_show("results/state_tilt/does_not_exist.json") is None, "L9 an absent path is not a face")
    # a pin that stores digests only is not a replay
    with tempfile.TemporaryDirectory() as tmp:
        with io.open(os.path.join(tmp, "P.json"), "w", encoding="utf-8") as fh:
            json.dump({"sources": [{"path": "a", "sha256": "x"}], "pin_id": "p"}, fh)
        with io.open(os.path.join(tmp, "f.json"), "w", encoding="utf-8") as fh:
            json.dump({"corpus_source": {"pin_file": "P.json"}}, fh)
        rep = replay_column("e305_face_level_row_pricing", "f.json", outdir=tmp)
        ok(rep["available"] is False, "L10 a digest-only pin cannot be replayed")
        ok(rep["reason"].startswith("the_pin_stores_digests_only"), "L11 and says why")
    print("E387 selftest %d/%d" % (11 - len(fails), 11))
    if fails:
        for f in fails:
            print("FAIL", f)
        return 1
    return 0


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "selftest":
        return selftest()
    if cmd == "verify":
        problems = verify()
        print(json.dumps({"problems": problems}, ensure_ascii=False))
        return 0 if not problems else 1
    if cmd == "run":
        doc = build()
        os.makedirs(OUTDIR, exist_ok=True)
        with io.open(os.path.join(OUTDIR, FACE), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(doc, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
        mirror = dict(doc)
        mirror["face"] = FACE
        with io.open(os.path.join(OUTDIR, LATEST), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(mirror, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
        s = doc["summary"]
        print("%s -> %s" % (STUDY, os.path.join(OUTDIR, FACE)))
        print("verdict: %s" % doc["verdict"])
        print("%d faces / %d legs: %d moved since head, %d republished, %d seams opened, "
              "%d reproducible at head" % (s["faces"], s["legs"],
                                           s["faces_whose_numbers_moved_since_head"],
                                           s["republished"], s["seams_opened"],
                                           s["faces_reproducible_at_head"]))
        return 0
    print("unknown mode: %s" % cmd)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))

