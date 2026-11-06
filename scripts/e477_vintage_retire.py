"""E477 -- if the unread vintage families were retired, what bytes would actually be lost?

E472 found 97 vintage families under results/ that no study opens (571 files, 27.2 MB), and r1504
concluded they cannot be attributed to a writer, so they have to be retired by publishing policy
rather than fixed at the source.  Before a policy retires them, the question that matters is
whether the bytes are still the only copy: a daily face that repeats an unchanged payload, or a
vintage that is an exact copy of the family's `*_latest.json` twin, costs nothing to delete.

Every member file of every family E472 published is hashed (sha256) against the whole results/
payload tree, and each file lands in exactly one class:

  repeat_of_another_member_in_the_same_family  same bytes as a sibling vintage (the payload did not
                                               change on that date)
  copy_of_a_latest_twin                        same bytes as a file whose name carries "latest"
  copy_of_a_file_outside_the_unread_families    same bytes as some other results/ file
  unique_bytes                                 no byte-identical partner in the tree

The verdict is computed from the class counts; the delivered number is `bytes_lost_if_retired`
(the unique bytes plus the bytes of copies that live only inside the unread set -- a copy of a
latest twin survives a retirement of the vintages, a repeat inside the family does not).

CLI: run | check | verify | selftest
"""

import argparse
import hashlib
import io
import json
import os
import shutil
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE_NAME = "vintageretire_latest.json"
DATED_PREFIX = "VINTAGERETIRE"
CARD = ("E477-IF-THE-UNREAD-VINTAGE-FAMILIES-WERE-RETIRED-HOW-MANY-BYTES-WOULD-ACTUALLY-BE-LOST")

PARENT_FACE = "vintageread_latest.json"   # E472: the 97 unread vintage families
CORPUS_SCOPE = "results"
PAYLOAD_EXTS = (".json", ".jsonl", ".csv", ".md")
SKIP_DIRS = ("__pycache__", "_quarantine", "node_modules")

C_FAMILY_REPEAT = "repeat_of_another_member_in_the_same_family"
C_LATEST_COPY = "copy_of_a_latest_twin"
C_OUTSIDE_COPY = "copy_of_a_file_outside_the_unread_families"
C_UNIQUE = "unique_bytes"
CLASSES = (C_FAMILY_REPEAT, C_LATEST_COPY, C_OUTSIDE_COPY, C_UNIQUE)

V_EMPTY = "the_unread_vintage_population_is_empty"
V_NONE = "no_unread_vintage_file_has_a_byte_identical_partner"
V_SOME = "some_unread_vintage_files_have_a_byte_identical_partner_but_the_majority_do_not"
V_MOST = "most_unread_vintage_files_have_a_byte_identical_partner"
VERDICT_VOCAB = (V_EMPTY, V_NONE, V_SOME, V_MOST)


# ----------------------------------------------------------------------------- helpers


def _rel(path, root=None):
    return os.path.relpath(path, root or ROOT).replace("\\", "/")


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _walk_payloads(scope):
    out = []
    for base, dirs, files in os.walk(scope):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in files:
            if name.endswith(PAYLOAD_EXTS):
                out.append(os.path.join(base, name))
    return out


def _is_latest_name(path):
    return "latest" in os.path.basename(path).lower()


def classify(members_by_family, corpus_paths, hash_of, size_of, scope_prefix=None):
    """Assign every member file to exactly one class.

    members_by_family: {family_key: [member path, ...]} -- the population under test
    corpus_paths:      every payload path whose bytes can count as a partner
    hash_of / size_of: injectable readers (the selftest feeds fixtures through them)
    """
    # Path form must be normalised before any set membership test: the population is built by
    # os.path.join(ROOT, "results/...") and mixes separators, while os.walk returns backslashes,
    # so an unnormalised `p in members` never matches and every sibling reads as an outside copy
    # (the E366 lesson: one population, one address form).
    members = set()
    for paths in members_by_family.values():
        members.update(os.path.normpath(p) for p in paths)

    by_hash = {}
    for p in corpus_paths:
        try:
            by_hash.setdefault(hash_of(p), []).append(p)
        except OSError:
            continue

    rows = []
    class_counts = {c: 0 for c in CLASSES}
    class_bytes = {c: 0 for c in CLASSES}
    families = []

    for fam_key in sorted(members_by_family):
        paths = sorted(members_by_family[fam_key])
        fam_counts = {c: 0 for c in CLASSES}
        fam_unique_bytes = 0
        for p in paths:
            try:
                digest = hash_of(p)
                size = size_of(p)
            except OSError:
                continue
            norm = os.path.normpath(p)
            partners = [q for q in by_hash.get(digest, []) if os.path.normpath(q) != norm]
            family = {os.path.normpath(q) for q in paths}
            siblings = [q for q in partners if os.path.normpath(q) in family]
            latest = [q for q in partners if _is_latest_name(q)]
            outside = [q for q in partners if os.path.normpath(q) not in members]
            if siblings:
                cls = C_FAMILY_REPEAT
            elif latest:
                cls = C_LATEST_COPY
            elif outside:
                cls = C_OUTSIDE_COPY
            else:
                cls = C_UNIQUE
            class_counts[cls] += 1
            class_bytes[cls] += size
            fam_counts[cls] += 1
            if cls == C_UNIQUE:
                fam_unique_bytes += size
            rows.append({
                "path": _rel(p) if not scope_prefix else p,
                "family": fam_key,
                "bytes": size,
                "class": cls,
                "partners": sorted(_rel(q) if not scope_prefix else q for q in partners)[:5],
            })
        families.append({
            "family": fam_key,
            "members": len(paths),
            "counts": fam_counts,
            "unique_bytes": fam_unique_bytes,
            "bytes": sum(r["bytes"] for r in rows if r["family"] == fam_key),
        })

    return rows, families, class_counts, class_bytes


def build(pop_path=None, corpus_root=None, corpus_prefix=None):
    pop = json.load(io.open(pop_path or os.path.join(OUTDIR, PARENT_FACE), "r", encoding="utf-8"))
    fam_rows = pop.get("rows") or []
    members_by_family = {}
    missing = []
    for r in fam_rows:
        key = "%s/%s" % (r.get("dir", "?"), r.get("family", "?"))
        keep = []
        for m in r.get("members", []):
            path = m if os.path.isabs(m) else os.path.join(corpus_root or ROOT, m)
            if os.path.exists(path):
                keep.append(path)
            else:
                missing.append(m)
        if keep:
            members_by_family[key] = keep

    corpus = _walk_payloads(corpus_root or os.path.join(ROOT, CORPUS_SCOPE))
    rows, families, class_counts, class_bytes = classify(
        members_by_family, corpus, _sha256, os.path.getsize, scope_prefix=corpus_prefix)

    measured = sum(class_counts.values())
    duplicated = measured - class_counts[C_UNIQUE]
    # Bytes that a retirement of the vintages would destroy: everything that has no copy outside
    # the unread membership.  A copy of a latest twin survives; a family repeat does not.
    lost = class_bytes[C_UNIQUE] + class_bytes[C_FAMILY_REPEAT] + class_bytes[C_OUTSIDE_COPY]

    if measured == 0:
        verdict = V_EMPTY
    elif duplicated == 0:
        verdict = V_NONE
    elif duplicated * 2 > measured:
        verdict = V_MOST
    else:
        verdict = V_SOME

    summary = {
        "families": len(families),
        "member_files": measured,
        "class_counts": class_counts,
        "class_bytes": class_bytes,
        "duplicated_files": duplicated,
        "duplicated_share": round(duplicated / measured, 6) if measured else None,
        "total_bytes": sum(class_bytes.values()),
        "bytes_lost_if_retired": lost,
        "bytes_reclaimed_if_deduped": class_bytes[C_LATEST_COPY] + class_bytes[C_OUTSIDE_COPY],
        "members_missing_on_disk": len(missing),
        "corpus_files_hashed": len(corpus),
    }
    face = {
        "card": CARD,
        "study": "E477_if_the_unread_vintage_families_were_retired_how_many_bytes_would_actually_be_lost",
        "title": "if the unread vintage families were retired, how many bytes would actually be lost?",
        "evidence_cutoff": time.strftime("%Y-%m-%d"),
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "population_source": {
            "face": PARENT_FACE,
            "face_evidence_cutoff": pop.get("evidence_cutoff"),
            "face_verdict": pop.get("verdict"),
            "scope": CORPUS_SCOPE,
            "payload_extensions": list(PAYLOAD_EXTS),
        },
        "class_definition": {
            C_FAMILY_REPEAT: "same sha256 as another member of the same family",
            C_LATEST_COPY: "same sha256 as a file whose name carries 'latest' (survives a vintage retirement)",
            C_OUTSIDE_COPY: "same sha256 as a results/ payload outside the unread membership",
            C_UNIQUE: "no byte-identical partner anywhere in the results/ payload tree",
        },
        "summary": summary,
        "verdict": verdict,
        "verdict_vocab": list(VERDICT_VOCAB),
        "families": families,
        "rows": rows,
        "method_limits": [
            "byte identity is the only witness: a vintage that differs by one timestamp field counts as unique even when it carries no new measurement",
            "the corpus is results/ payload extensions only; a partner in docs/ or in a non-payload extension is not seen, so the duplicate count is a lower bound",
            "the population is E472's rows as published; a family that gained or lost members since then is reported through members_missing_on_disk, never silently rescanned",
            "bytes_lost_if_retired counts family repeats as lost even when the whole family is retired together (the bytes are identical to each other, not to anything that survives)",
        ],
    }
    return face


# ----------------------------------------------------------------------------- commands


def check(face=None):
    problems = []
    face = face or json.load(io.open(os.path.join(OUTDIR, FACE_NAME), "r", encoding="utf-8"))
    s = face.get("summary") or {}
    counts = s.get("class_counts") or {}
    if set(counts) != set(CLASSES):
        problems.append("class_counts keys are not the published class set: %r" % sorted(counts))
    if sum(counts.values()) != s.get("member_files"):
        problems.append("class counts do not sum to member_files")
    if face.get("verdict") not in VERDICT_VOCAB:
        problems.append("verdict is outside the vocabulary: %r" % face.get("verdict"))
    rows = face.get("rows") or []
    if len(rows) != s.get("member_files"):
        problems.append("row count %d != member_files %r" % (len(rows), s.get("member_files")))
    bad = [r for r in rows if r.get("class") not in CLASSES]
    if bad:
        problems.append("%d rows carry a class outside the set" % len(bad))
    if sum(r.get("bytes", 0) for r in rows) != s.get("total_bytes"):
        problems.append("row bytes do not sum to total_bytes")
    if sum((s.get("class_bytes") or {}).values()) != s.get("total_bytes"):
        problems.append("class bytes do not sum to total_bytes")
    # the verdict must be recomputable from the counts, never restated
    measured = s.get("member_files") or 0
    dup = measured - counts.get(C_UNIQUE, 0)
    expect = (V_EMPTY if measured == 0 else
              V_NONE if dup == 0 else
              V_MOST if dup * 2 > measured else V_SOME)
    if face.get("verdict") != expect:
        problems.append("verdict %r is not the one the counts imply (%r)" % (face.get("verdict"), expect))
    if s.get("duplicated_files") != dup:
        problems.append("duplicated_files does not match the counts")
    # a "unique" row must not carry partners
    for r in rows:
        if r.get("class") == C_UNIQUE and r.get("partners"):
            problems.append("row %s is classed unique but names partners" % r.get("path"))
            break
        if r.get("class") != C_UNIQUE and not r.get("partners"):
            problems.append("row %s is classed %s without a partner" % (r.get("path"), r.get("class")))
            break
    fam_sum = sum(f.get("members", 0) for f in face.get("families") or [])
    if fam_sum != s.get("member_files"):
        problems.append("family member counts do not sum to member_files")
    return problems


def verify():
    """Rebuild from the live tree and compare against the published face."""
    published = json.load(io.open(os.path.join(OUTDIR, FACE_NAME), "r", encoding="utf-8"))
    fresh = build()
    problems = []
    ps, fs = published.get("summary") or {}, fresh.get("summary") or {}
    for key in ("families", "member_files", "class_counts", "class_bytes", "total_bytes",
                "duplicated_files", "bytes_lost_if_retired"):
        if ps.get(key) != fs.get(key):
            problems.append("%s: published %r != fresh %r" % (key, ps.get(key), fs.get(key)))
    if published.get("verdict") != fresh.get("verdict"):
        problems.append("verdict: published %r != fresh %r" % (published.get("verdict"), fresh.get("verdict")))
    return problems


def run(face=None):
    face = face or build()
    os.makedirs(OUTDIR, exist_ok=True)
    dated = os.path.join(OUTDIR, "%s-%s.json" % (DATED_PREFIX, face["evidence_cutoff"]))
    latest = os.path.join(OUTDIR, FACE_NAME)
    compact = json.dumps(face, ensure_ascii=False, sort_keys=True)
    for path in (dated, latest):
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(compact + "\n")
    problems = check(face)
    print(json.dumps({"face": _rel(latest), "dated": _rel(dated),
                      "summary": face["summary"], "verdict": face["verdict"],
                      "problems": problems}, ensure_ascii=False, sort_keys=True))
    return 0 if not problems else 1


# ----------------------------------------------------------------------------- selftest


def selftest():
    tmp = tempfile.mkdtemp(prefix="e477_")
    fails = []

    def want(name, got, expect):
        if got != expect:
            fails.append("%s: got %r want %r" % (name, got, expect))

    try:
        fam = os.path.join(tmp, "results", "fam")
        other = os.path.join(tmp, "results", "other")
        os.makedirs(fam)
        os.makedirs(other)
        files = {
            "a.json": '{"x":1}',          # repeated on two dates -> family repeat
            "b.json": '{"x":1}',          # same bytes as a.json
            "c.json": '{"y":2}',          # unique
            "fam_latest.json": '{"z":3}',  # twin of d.json
            "d.json": '{"z":3}',
            "e.json": '{"w":4}',          # copy of a file outside the families
        }
        for name, text in files.items():
            with io.open(os.path.join(fam, name), "w", encoding="utf-8", newline="\n") as fh:
                fh.write(text)
        with io.open(os.path.join(other, "outside.json"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write('{"w":4}')

        # the latest twin is part of the corpus but NOT part of the population
        corpus = sorted(os.path.join(fam, n) for n in ("a.json", "b.json", "c.json", "d.json", "e.json"))
        corpus.append(os.path.join(fam, "fam_latest.json"))
        corpus.append(os.path.join(other, "outside.json"))
        population = {"fam": [os.path.join(fam, n) for n in ("a.json", "b.json", "c.json", "d.json", "e.json")]}

        rows, families, counts, byte_counts = classify(
            population, corpus, _sha256, os.path.getsize, scope_prefix=True)
        want("member rows", len(rows), 5)
        want("family repeats", counts[C_FAMILY_REPEAT], 2)
        want("latest copies", counts[C_LATEST_COPY], 1)
        want("outside copies", counts[C_OUTSIDE_COPY], 1)
        want("unique", counts[C_UNIQUE], 1)
        want("class sum", sum(counts.values()), 5)
        want("repeat bytes", byte_counts[C_FAMILY_REPEAT], 2 * len('{"x":1}'))
        want("family rows", len(families), 1)
        want("family unique bytes", families[0]["unique_bytes"], len('{"y":2}'))
        # a same-bytes sibling must win over a latest twin: class order is by closest surviving copy
        by_path = {os.path.basename(r["path"]): r["class"] for r in rows}
        want("a is a family repeat", by_path["a.json"], C_FAMILY_REPEAT)
        want("c is unique", by_path["c.json"], C_UNIQUE)

        # an empty population is a verdict, not a crash
        rows2, fam2, counts2, bytes2 = classify({}, corpus, _sha256, os.path.getsize, scope_prefix=True)
        want("empty rows", rows2, [])
        want("empty counts", sum(counts2.values()), 0)

        # check() must refuse a doctored tally (verdict restated instead of recomputed)
        good = {
            "summary": {"families": 1, "member_files": 2, "class_counts": {c: 0 for c in CLASSES},
                        "class_bytes": {c: 0 for c in CLASSES}, "total_bytes": 0,
                        "duplicated_files": 0},
            "families": [{"members": 2}],
            "rows": [{"path": "p", "class": C_UNIQUE, "bytes": 0, "partners": []},
                     {"path": "q", "class": C_UNIQUE, "bytes": 0, "partners": []}],
            "verdict": V_NONE,
        }
        good["summary"]["class_counts"][C_UNIQUE] = 2
        want("clean fixture checks", check(good), [])
        doctored = json.loads(json.dumps(good))
        doctored["verdict"] = V_MOST
        if not check(doctored):
            fails.append("check() accepted a verdict the counts do not imply")
        doctored2 = json.loads(json.dumps(good))
        doctored2["rows"][0]["partners"] = ["z"]
        if not check(doctored2):
            fails.append("check() accepted a unique row that names a partner")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    if fails:
        for f in fails:
            print("FAIL %s" % f)
        return 1
    print("selftest 5/5 classes + empty population + doctored tally + doctored unique row: OK")
    return 0


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("run", "check", "verify", "selftest"))
    args = ap.parse_args(argv)
    if args.cmd == "run":
        return run()
    if args.cmd == "check":
        problems = check()
    elif args.cmd == "verify":
        problems = verify()
    else:
        return selftest()
    print(json.dumps({"problems": problems}, ensure_ascii=False))
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))