"""E328 -- which quoted numbers sit on a stated cutoff that its own family has already outgrown.

E326 asked whether a consumer carries the parameter of a face it names.  E327 asked whether a
pointer republishes that parameter.  Both of them measured faces.  This study measures *numbers*.

The question a reader actually has is narrower than "is the cutoff stated".  A face can state
`evidence_cutoff: 2026-10-27` honestly and still be the wrong face: if the same family on disk
already holds a newer cut, then every number a code path pulls out of the older file is a number
read at a vintage its own producer has moved past.  A stated cutoff is not a fresh cutoff.

Population:
  faces   = files under results/ named <STEM>-<YYYY-MM-DD>.json or <STEM>-<YYYYMMDD>.json
  family  = (directory, STEM) -- same stem in a different directory is a different family
  cutoff  = the first ISO date inside evidence_cutoff / cutoff / as_of / asof, else the name token
  stale   = cutoff < the newest cutoff of the same family

Quote:
  a *non-writer* python source names the face's literal basename and, within a small window after
  that line, subscripts a quoted key (or `.get("...")`).  A source that binds the basename to a
  name and then dumps that name is the producer, not a reader, and is excluded -- otherwise every
  face is "quoted" by the module that writes it (E204/r1232 self-inclusion family).

For every stale face that is actually quoted, the numbers are diffed against the newest sibling on
the same key path: `changed`, `equal` and `absent_from_the_newest_cut`.  A changed number is what a
reader loses by opening the old file; an absent one has no fresh counterpart at all.

Static tree analysis only: no panel, no engine, no network, no draws.

Usage:
    python scripts/e328_quoted_number_staleness.py run|verify|selftest
"""
import datetime
import io
import json
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import e326_template_parameter_consumers as e326  # noqa: E402  (path set above)

ROOT = e326.ROOT
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
TODAY = "2026-11-01"
FACE = "STALECUTOFF-%s.json" % TODAY
LATEST = "stalecutoff_latest.json"
STUDY = "E328_quoted_number_staleness"

DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
FACE_ISO = re.compile(r"^(?P<stem>[A-Za-z0-9_+\-]+?)-(?P<date>\d{4}-\d{2}-\d{2})\.json$")
FACE_CMP = re.compile(r"^(?P<stem>[A-Za-z0-9_+\-]+?)-(?P<date>\d{8})\.json$")
CUTOFF_KEYS = ("evidence_cutoff", "cutoff", "as_of", "asof")
NUMERIC_READ = re.compile(r"\[\s*[\"'][A-Za-z_][A-Za-z0-9_.]*[\"']\s*\]|"
                          r"\.get\(\s*[\"'][A-Za-z_][A-Za-z0-9_.]*[\"']")
FACE_TOKEN = re.compile(r"([A-Za-z0-9_+\-]+-\d{4}-?\d{2}-?\d{2}\.json)")
WRITE_CALL = re.compile(r"(json\.dump|\.write\(|[\"']w[\"'])")

V_STALE_CHANGED = ("quoted_numbers_are_read_from_vintages_and_move_when_the_newest_cut_is_opened")
V_STALE_SAME = "quoted_vintages_are_stale_but_their_numbers_do_not_move"
V_NO_STALE_QUOTE = "no_quoted_face_is_older_than_its_family_s_newest_cut"
VERDICTS = (V_STALE_CHANGED, V_STALE_SAME, V_NO_STALE_QUOTE)

WINDOW = 8            # lines after a naming line searched for the numeric subscript
MAX_BYTES = 4 << 20   # a face larger than this is skipped, and counted as skipped
OWN_FACES = (FACE, LATEST)


# ---------------------------------------------------------------------------------- primitives

def face_name(name):
    """(stem, token date) for a dated face filename, else None.  Compact dates included."""
    match = FACE_ISO.match(name)
    if match:
        try:
            return match.group("stem"), datetime.date.fromisoformat(match.group("date"))
        except ValueError:
            return None
    match = FACE_CMP.match(name)
    if match:
        try:
            raw = match.group("date")
            return match.group("stem"), datetime.date(int(raw[:4]), int(raw[4:6]), int(raw[6:]))
        except ValueError:
            return None
    return None


def cutoff_of(doc, token):
    """(date, where it came from).  A stated cutoff wins over the name token."""
    if isinstance(doc, dict):
        for key in CUTOFF_KEYS:
            value = doc.get(key)
            if isinstance(value, str):
                match = DATE.search(value)
                if match:
                    return datetime.date.fromisoformat(match.group(0)), key
    return token, "name_token"


def numeric_leaves(node, prefix="", out=None, depth=0):
    """Every numeric leaf with its key path.  Bools are not numbers (E207 family)."""
    out = [] if out is None else out
    if depth > 14:
        return out
    if isinstance(node, dict):
        for key, value in node.items():
            path = ("%s.%s" % (prefix, key)) if prefix else str(key)
            if isinstance(value, bool):
                continue
            if isinstance(value, (int, float)):
                out.append((path, float(value)))
            elif isinstance(value, (dict, list)):
                numeric_leaves(value, path, out, depth + 1)
    elif isinstance(node, list):
        for index, value in enumerate(node):
            path = "%s[%d]" % (prefix, index)
            if isinstance(value, bool):
                continue
            if isinstance(value, (int, float)):
                out.append((path, float(value)))
            elif isinstance(value, (dict, list)):
                numeric_leaves(value, path, out, depth + 1)
    return out


def diff_numbers(old, new):
    """changed / equal / absent_from_newest, comparing on the key path."""
    fresh = dict(new)
    changed, absent, equal = [], [], 0
    for path, value in old:
        if path not in fresh:
            absent.append((path, value))
            continue
        other = fresh[path]
        if abs(other - value) > 1e-12 * max(1.0, abs(value)):
            changed.append((path, value, other))
        else:
            equal += 1
    return {"changed": changed, "absent_from_newest": absent, "equal": equal}


def scan_faces(root):
    base = os.path.join(root, "results")
    own = set(OWN_FACES)
    out = []
    for dirpath, _dirnames, filenames in os.walk(base):
        for name in filenames:
            if name in own:
                continue
            parsed = face_name(name)
            if not parsed:
                continue
            stem, token = parsed
            rel = os.path.relpath(os.path.join(dirpath, name), root).replace("\\", "/")
            out.append({"rel": rel, "name": name, "stem": stem, "token": token,
                        "family": "%s/%s" % (os.path.dirname(rel), stem)})
    return sorted(out, key=lambda r: r["rel"])


def load(root, rel):
    path = os.path.join(root, rel)
    try:
        if os.path.getsize(path) > MAX_BYTES:
            return None
    except OSError:
        return None
    try:
        with io.open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return None


# ------------------------------------------------------------------------------------ readers

def _code_lines(src):
    return e326.code_lines(src)


def reader_index(files):
    """basename -> [{source, line, text, writer, numeric_read}] built in one pass over the corpus.

    The window test is precomputed per line: an inner `any(... for _n, t in lines ...)` over every
    naming line is quadratic and turned a 4-second corpus into a 5-minute hang on the first run.
    """
    index = {}
    for path, src in files:
        lines = _code_lines(src)
        numeric_flags = [bool(NUMERIC_READ.search(text)) for _n, text in lines]
        naming = []
        for position, (lineno, text) in enumerate(lines):
            bases = [b for b in FACE_TOKEN.findall(text) if face_name(b)]
            if bases:
                naming.append((position, lineno, text, bases))
        if not naming:
            continue
        rel = e326.relp(path)
        for position, lineno, text, bases in naming:
            numeric = numeric_flags[position] or any(
                numeric_flags[position + 1:position + 1 + WINDOW])
            writer = bool(WRITE_CALL.search(text))
            if not writer:
                # a producer binds the basename to a name and dumps that name later; resolving the
                # binding per naming line keeps this linear (the first draft re-scanned every line
                # against every variable in the file and never finished on the 2.3k-file corpus).
                match = re.match(r"([A-Za-z_][A-Za-z0-9_]*)\s*=", text)
                if match:
                    var = re.compile(r"\b%s\b" % re.escape(match.group(1)))
                    writer = any(var.search(t) and WRITE_CALL.search(t)
                                 for n, t in lines if n != lineno)
            for base in bases:
                record = {"source": rel, "line": lineno, "text": text[:150], "writer": writer,
                          "numeric_read": numeric}
                bucket = index.setdefault(base, [])
                if record not in bucket:
                    bucket.append(record)
    return index


def quotes_of(face_rel, index):
    readers = index.get(os.path.basename(face_rel)) or []
    live = [r for r in readers if not r["writer"]]
    return {"readers": readers, "non_writer_readers": live,
            "numeric_non_writer_readers": [r for r in live if r["numeric_read"]]}


# --------------------------------------------------------------------------------------- build

def build(root=None, outdir=None, files=None):
    root = root or ROOT
    faces = scan_faces(root)
    by_family = {}
    for rec in faces:
        doc = load(root, rec["rel"])
        cut, source = cutoff_of(doc, rec["token"])
        rec["cutoff"] = cut
        rec["cutoff_source"] = source
        rec["loaded"] = doc is not None
        rec["doc"] = doc if doc is not None else {}
        by_family.setdefault(rec["family"], []).append(rec)

    index = reader_index(files if files is not None else e326.corpus())
    own = set(OWN_FACES)

    rows = []
    families = 0
    faces_with_cutoff = 0
    stale_faces = 0
    skipped_large = 0
    for family in sorted(by_family):
        members = sorted(by_family[family], key=lambda r: (r["cutoff"], r["rel"]))
        families += 1
        newest = members[-1]
        for rec in members:
            if rec["cutoff_source"] != "name_token":
                faces_with_cutoff += 1
            if rec["cutoff"] >= newest["cutoff"]:
                continue
            stale_faces += 1
            if os.path.basename(rec["rel"]) in own:
                continue
            quotes = quotes_of(rec["rel"], index)
            if not quotes["numeric_non_writer_readers"]:
                continue
            if not rec["loaded"]:
                skipped_large += 1
                rec["unparsed"] = True
                continue
            fresh = load(root, newest["rel"]) if newest["loaded"] else None
            if fresh is None:
                continue
            stale_numbers = numeric_leaves(rec["doc"])
            diff = diff_numbers(stale_numbers, numeric_leaves(fresh))
            rows.append({
                "face": rec["rel"],
                "family": family,
                "cutoff": rec["cutoff"].isoformat(),
                "cutoff_source": rec["cutoff_source"],
                "family_newest_face": newest["rel"],
                "family_newest_cutoff": newest["cutoff"].isoformat(),
                "days_behind": (newest["cutoff"] - rec["cutoff"]).days,
                "readers": len(quotes["numeric_non_writer_readers"]),
                "reader_sources": sorted({r["source"] for r in quotes["numeric_non_writer_readers"]}),
                "reader_lines": [{"source": r["source"], "line": r["line"], "text": r["text"]}
                                 for r in quotes["numeric_non_writer_readers"][:3]],
                "numbers": len(stale_numbers),
                "changed": len(diff["changed"]),
                "equal": diff["equal"],
                "absent_from_newest_cut": len(diff["absent_from_newest"]),
                "examples": [{"path": p, "stale": v, "newest": n}
                             for p, v, n in diff["changed"][:5]],
            })

    moved = sum(r["changed"] for r in rows)
    absent = sum(r["absent_from_newest_cut"] for r in rows)
    if rows and moved:
        verdict = V_STALE_CHANGED
    elif rows:
        verdict = V_STALE_SAME
    else:
        verdict = V_NO_STALE_QUOTE

    summary = {
        "faces_scanned": len(faces),
        "families": families,
        "families_with_more_than_one_cut": sum(1 for m in by_family.values() if len(m) > 1),
        "faces_with_stated_cutoff": faces_with_cutoff,
        "stale_faces": stale_faces,
        "stale_faces_quoted": len(rows),
        "stale_faces_unquoted": stale_faces - len(rows),
        "stale_faces_quoted_and_parsed": sum(1 for r in rows),
        "quoted_numbers": sum(r["numbers"] for r in rows),
        "numbers_that_move": moved,
        "numbers_absent_from_newest_cut": absent,
        "numbers_equal": sum(r["equal"] for r in rows),
        "unparsed_stale_quoted": skipped_large,
    }
    doc = {
        "study": STUDY,
        "evidence_cutoff": TODAY,
        "verdict": verdict,
        "summary": summary,
        "rules": {
            "family": "(directory, stem) -- the same stem in another directory is another family",
            "cutoff": "first ISO date in " + "/".join(CUTOFF_KEYS) + ", else the name token",
            "stale": "cutoff < the newest cutoff of the same family on disk",
            "quote": "a non-writer python source names the literal basename and subscripts a "
                     "quoted key within %d lines of that line" % WINDOW,
            "producer_excluded": "a source that binds the basename and dumps the binding is the "
                                 "face's writer, not a reader",
        },
        "limits": {
            "numeric_read_is_line_local": "a reader that names the face in one function and reads "
                                          "the numbers elsewhere is measured by the %d-line window "
                                          "only" % WINDOW,
            "no_reach_into_the_newest_cut": "a changed number is what the stale file prints; it is "
                                            "not proof the reader would have used the newest cut "
                                            "if it had opened that file",
            "family_by_name": "two faces with different stems that carry the same series are two "
                              "families here",
        },
        "rows": rows,
    }
    target = outdir or OUTDIR
    os.makedirs(target, exist_ok=True)
    for name, payload in ((FACE, doc), (LATEST, doc)):
        with io.open(os.path.join(target, name), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(payload, fh, indent=1, sort_keys=False)
            fh.write("\n")
    return doc


def verify(root=None, files=None):
    """Re-derive the face and report every number that does not reproduce."""
    fresh = build(root=root, outdir=tempfile.mkdtemp(prefix="e328_verify_"), files=files)
    disk_path = os.path.join(root or ROOT, os.path.join("results", "state_tilt", FACE))
    problems = []
    try:
        with io.open(disk_path, encoding="utf-8") as fh:
            disk = json.load(fh)
    except Exception as exc:
        return ["the face does not read: %r" % (exc,)]
    if disk.get("verdict") != fresh.get("verdict"):
        problems.append("the verdict does not re-derive")
    if disk.get("verdict") not in VERDICTS:
        problems.append("verdict %r is outside the frozen set" % (disk.get("verdict"),))
    for key, value in (fresh.get("summary") or {}).items():
        if (disk.get("summary") or {}).get(key) != value:
            problems.append("summary.%s does not re-derive" % key)
    on_disk = {(r["face"], r["family"]): (r["cutoff"], r["changed"])
               for r in disk.get("rows") or []}
    computed = {(r["face"], r["family"]): (r["cutoff"], r["changed"]) for r in fresh["rows"]}
    if on_disk != computed:
        problems.append("a quoted stale face does not re-derive")
    for row in disk.get("rows") or []:
        if row["changed"] + row["absent_from_newest_cut"] + row["equal"] != row["numbers"]:
            problems.append("a row's number split does not sum")
            break
    return problems


# ------------------------------------------------------------------------------------ selftest

def _write(root, rel, payload):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh)


def _fixture():
    """A tree where one family is exact, one is stale and quoted, one is stale and unread."""
    root = tempfile.mkdtemp(prefix="e328_fx_")
    results = os.path.join(root, "results", "fam")
    os.makedirs(results, exist_ok=True)
    _write(root, "results/fam/A-2026-10-01.json",
           {"evidence_cutoff": "2026-10-01", "cells": {"x": 1.0, "y": 2.0, "gone": 9.0}})
    _write(root, "results/fam/A-2026-10-05.json",
           {"evidence_cutoff": "2026-10-05", "cells": {"x": 1.5, "y": 2.0}})
    # stale but newer-looking token: the stated cutoff is what counts
    _write(root, "results/fam/B-2026-10-09.json",
           {"evidence_cutoff": "panel 2026-09-30 (bars due 15:30)", "cells": {"v": 3.0}})
    _write(root, "results/fam/B-2026-10-02.json",
           {"evidence_cutoff": "2026-10-02", "cells": {"v": 3.5}})
    # compact date token, quoted all the same
    _write(root, "results/fam/C-20260928.json",
           {"evidence_cutoff": "2026-09-28", "cells": {"w": 4.0}})
    _write(root, "results/fam/C-20261003.json",
           {"evidence_cutoff": "2026-10-03", "cells": {"w": 4.25}})
    # a lone face: it is its own family's newest cut, so never stale
    _write(root, "results/fam/D-2026-09-01.json",
           {"evidence_cutoff": "2026-09-01", "cells": {"z": 1.0}})
    src = os.path.join(root, "scripts")
    os.makedirs(src, exist_ok=True)
    with io.open(os.path.join(src, "reader.py"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write('import json\n'
                 'p = "results/fam/A-2026-10-01.json"\n'
                 'doc = json.load(open(p))\n'
                 'v = doc["cells"]["x"]\n')
    with io.open(os.path.join(src, "namer_only.py"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write('LABEL = "results/fam/C-20260928.json"\nprint(LABEL)\n')
    with io.open(os.path.join(src, "producer.py"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write('import json\n'
                 'out = {}\n'
                 'f = "results/fam/B-2026-10-09.json"\n'
                 'json.dump(out, open(f, "w"))\n')
    files = []
    for name in sorted(os.listdir(src)):
        path = os.path.join(src, name)
        with io.open(path, encoding="utf-8") as fh:
            files.append((path, fh.read()))
    return root, files


def cmd_selftest():
    checks = []

    def check(name, ok, detail=""):
        checks.append((name, bool(ok), detail))
        print("%-6s %s%s" % ("PASS" if ok else "FAIL", name, "" if ok else "  <- " + detail))
        sys.stdout.flush()

    check("L1 iso face names parse", face_name("BANDFLOOR-2026-10-29.json")
          == ("BANDFLOOR", datetime.date(2026, 10, 29)))
    check("L2 compact face names parse", face_name("CASHLeg-20261027.json")
          == ("CASHLeg", datetime.date(2026, 10, 27)))
    check("L3 a non-face name is not a face", face_name("latest.json") is None)
    check("L4 a name with trailing text is not a dated face",
          face_name("X-2026-10-29-extra.json") is None
          and face_name("X-2026-10.json") is None)
    doc = {"evidence_cutoff": "panel 2026-10-14 (bars due 15:30)", "cells": {"a": 1}}
    got, where = cutoff_of(doc, datetime.date(2026, 10, 20))
    check("L5 a stated cutoff wins over the name token",
          got == datetime.date(2026, 10, 14) and where == "evidence_cutoff")
    got, where = cutoff_of({"cells": {}}, datetime.date(2026, 10, 20))
    check("L6 a face with no cutoff falls back to its token",
          got == datetime.date(2026, 10, 20) and where == "name_token")
    leaves = dict(numeric_leaves({"a": 1, "b": True, "c": {"d": 2.5}, "e": [3, False]}))
    check("L7 numeric leaves skip bools", leaves == {"a": 1.0, "c.d": 2.5, "e[0]": 3.0})
    diff = diff_numbers([("x", 1.0), ("y", 2.0), ("gone", 9.0)],
                        [("x", 1.5), ("y", 2.0)])
    check("L8 the diff separates changed / equal / absent",
          len(diff["changed"]) == 1 and diff["equal"] == 1
          and len(diff["absent_from_newest"]) == 1)

    root, files = _fixture()
    index = reader_index(files)
    reader = quotes_of("results/fam/A-2026-10-01.json", index)
    check("L9 a non-writer source that subscripts a key is a quote",
          len(reader["numeric_non_writer_readers"]) == 1)
    producer = quotes_of("results/fam/B-2026-10-09.json", index)
    check("L10 the face's own writer is not a reader",
          producer["readers"] and not producer["non_writer_readers"])
    namer = quotes_of("results/fam/C-20260928.json", index)
    check("L11 a source that only names the file in a label is not a numeric quote",
          namer["non_writer_readers"] and not namer["numeric_non_writer_readers"])

    out = tempfile.mkdtemp(prefix="e328_fx_out_")
    doc = build(root=root, outdir=out, files=files)
    summary = doc["summary"]
    check("L12 only the quoted stale face is a row",
          [r["face"] for r in doc["rows"]] == ["results/fam/A-2026-10-01.json"],
          str([r["face"] for r in doc["rows"]]))
    check("L13 the stated cutoff, not the token, sets staleness",
          doc["rows"][0]["cutoff"] == "2026-10-01"
          and doc["rows"][0]["family_newest_cutoff"] == "2026-10-05")
    check("L14 the changed and absent numbers are both counted",
          doc["rows"][0]["changed"] == 1 and doc["rows"][0]["absent_from_newest_cut"] == 1)
    check("L15 a lone face is never stale", summary["stale_faces"] == 3,
          "stale=%r" % (summary["stale_faces"],))
    check("L16 a stale unread face is not a row", summary["stale_faces_quoted"] == 1)
    check("L17 the verdict names moving numbers", doc["verdict"] == V_STALE_CHANGED)

    # verify() must accept the face it just wrote and refuse a doctored one
    import shutil
    shutil.copytree(out, os.path.join(root, "results", "state_tilt"))
    check("L18 verify reproduces the face it wrote", verify(root=root, files=files) == [],
          "; ".join(verify(root=root, files=files))[:120])
    disk = os.path.join(root, "results", "state_tilt", FACE)
    fresh = json.load(io.open(disk, encoding="utf-8"))
    fresh["summary"]["numbers_that_move"] = 99
    with io.open(disk, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(fresh, fh)
    problems = verify(root=root, files=files)
    check("L19 verify refuses a doctored summary", any("numbers_that_move" in p for p in problems),
          "; ".join(problems)[:120])
    check("L20 the frozen vocabulary is closed", set(VERDICTS) == {
        V_STALE_CHANGED, V_STALE_SAME, V_NO_STALE_QUOTE})

    bad = [c for c in checks if not c[1]]
    print("\n%d/%d passed" % (len(checks) - len(bad), len(checks)))
    return 0 if not bad else 1


# ------------------------------------------------------------------------------------------ cli

def cmd_run():
    doc = build()
    s = doc["summary"]
    print("%s | %s" % (doc["verdict"], STUDY))
    print("faces %(faces_scanned)s / families %(families)s / multi-cut families "
          "%(families_with_more_than_one_cut)s / stated cutoffs %(faces_with_stated_cutoff)s"
          % s)
    print("stale faces %(stale_faces)s, of which quoted and parsed %(stale_faces_quoted)s"
          % s)
    print("numbers quoted at a stale vintage %(quoted_numbers)s: %(numbers_that_move)s move, "
          "%(numbers_absent_from_newest_cut)s have no fresh counterpart, %(numbers_equal)s agree"
          % s)
    return 0


def cmd_verify():
    problems = verify()
    if problems:
        print("PROBLEMS: " + "; ".join(problems[:8]))
        return 1
    print("verify: 0 problems")
    return 0


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "run":
        return cmd_run()
    if cmd == "verify":
        return cmd_verify()
    if cmd == "selftest":
        return cmd_selftest()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))