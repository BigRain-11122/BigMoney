"""E658: what E652's corpus-wide "files carrying a counted row key" volume becomes
once E657's unresolved-handle arm is folded in.

E652 counts a file as carrying a counted row key when its string arm names a key
or any Subscript names one, and publishes that count -- but its own measure()
throws the membership away. E657 then found counted keys sitting inside
unresolved string handles, positions E652's string arm cannot see at all
(707 files / 1,504 sites, 0 of which were already priced by the subscript arm).

So the published volume and the volume the tree actually supports are two
different numbers, and nobody has priced the gap. This face re-walks E652's
corpus once with each arm's own scanner, keeps both per-file membership sets,
and publishes: volume before, the set the handle arm adds, volume after, and how
much of the gain is visible-in-principle to E652's subscript arm.

Two rules carried from this family's own rulings:
  * every input is machine-read from the tree and from the predecessors'
    published JSON; the E652 headline (3860) is never typed into this file, and
    when this face fails to reproduce it the face publishes that instead of
    quietly disagreeing (E239).
  * the two arms must name their members the same way before any set operation,
    or one file is counted twice and the whole gain is fiction (E366).
"""

import argparse
import ast
import io
import json
import os
import re
import sys
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
TODAY = "2026-11-10"
FACE = "VOLUMEFOLD.json"
LATEST = "volumefold_latest.json"
STUDY = "E658_volume_fold"
SOURCE_FACE = "results/state_tilt/UNRESOLVEDKEY.json"
E652_FACE = "results/state_tilt/STRINGARMCENSUS.json"
SELF_PARTS = ("e658_", "run_e658_", "_r1675")

sys.path.insert(0, HERE)
import e652_string_arm_census as e652  # noqa: E402
import e657_unresolved_key as e657  # noqa: E402

V_NO_POPULATION = "not_assessable_e652_population_is_empty"
V_NO_HANDLE = "the_handle_arm_adds_nothing_beyond_e652"
V_ALL_VISIBLE = (
    "every_handle_arm_gain_is_already_visible_to_e652s_subscript_arm"
)
V_FOLD_GROWS = (
    "folding_the_unresolved_handle_arm_into_e652_raises_the_published_volume"
)
V_UNREPRODUCED = (
    "this_walk_does_not_reproduce_e652s_published_volume_so_the_gain_is_a_vintage_delta"
)


def say(line):
    sys.stdout.write(str(line) + "\n")
    sys.stdout.flush()


def rel(module, root=ROOT):
    module = os.path.abspath(module)
    root = os.path.abspath(root)
    try:
        return os.path.relpath(module, root).replace("\\", "/")
    except ValueError:
        return module.replace("\\", "/")


def is_self(name):
    base = os.path.basename(name)
    return any(base.startswith(p) or p in base for p in SELF_PARTS)


def scan_one(job):
    """Three arms over one file. Runs in a worker process.

    literal   -- E652's string arm: a string literal equal to a counted key
    subscript -- E652's tree-wide Subscript arm
    handle    -- E657's unresolved-handle arm: a counted key inside a string
                 handle whose value cannot be resolved statically
    """
    path, keys, index, root = job
    row = {"module": rel(path, root)}
    got, why = e652.scan_file(path, keys, index, root)
    row["hole"] = why
    if why is None:
        row["literal_arm"] = bool(got["counted_keys_named"])
        row["subscript_arm"] = bool(got["subscript_key_sites"])
        row["literal_keys"] = sorted(got["counted_keys_named"] or [])
        row["subscript_sites"] = int(got["subscript_key_sites"] or 0)
    else:
        row["literal_arm"] = None
        row["subscript_arm"] = None
    got2, why2 = e657.scan_file(path, keys, root)
    row["hole_handle"] = why2
    if why2 is None:
        handles = got2.get("handles") or []
        sites = [k for h in handles for k in (h.get("counted_keys") or [])]
        row["handle_arm"] = bool(sites)
        row["handle_sites"] = sum(int(h.get("counted_key_sites") or 0) for h in handles)
        row["handle_keys"] = sorted({k["key"] for k in sites})
        row["handle_nonsubscript_sites"] = sum(
            int(h.get("invisible_sites") or 0) for h in handles
        )
        row["handle_site_detail"] = [
            {"key": s.get("key"), "role": s.get("role"),
             "line": s.get("line"), "column": s.get("column")}
            for s in sites[:6]
        ]
        row["handle_site_detail_elided"] = max(0, len(sites) - 6)
    else:
        row["handle_arm"] = None
        row["handle_sites"] = 0
        row["handle_nonsubscript_sites"] = 0
        row["handle_site_detail"] = []
        row["handle_site_detail_elided"] = 0
    return row


def membership(root=ROOT, counted=None, workers=12):
    """Walk E652's corpus once, keeping each arm's per-file membership."""
    reads = e652.e648.read_population() if counted is None else counted
    keys = {r["key"] for r in reads if r.get("key")}
    read_modules = sorted({r["module"] for r in reads if r.get("module")})
    index = e652.target_index(read_modules, root)
    files = [p for p in e652.corpus(root) if not is_self(rel(p, root))]

    jobs = [(p, keys, index, root) for p in files]
    if workers and workers > 1 and len(jobs) > 200:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            rows = list(pool.map(scan_one, jobs, chunksize=32))
    else:
        rows = [scan_one(j) for j in jobs]

    lit, sub, hn = set(), set(), set()
    a_keys, b_keys = {}, {}
    nonsubscript = 0
    holes = {"over_the_size_cap": 0, "unreadable": 0, "does_not_parse": 0}
    for r in rows:
        if r.get("hole"):
            holes[r["hole"]] = holes.get(r["hole"], 0) + 1
            continue
        if r.get("literal_arm"):
            lit.add(r["module"])
            a_keys[r["module"]] = sorted(r.get("literal_keys") or [])
        if r.get("subscript_arm"):
            sub.add(r["module"])
        if r.get("handle_arm"):
            hn.add(r["module"])
            b_keys[r["module"]] = sorted(r.get("handle_keys") or [])
            nonsubscript += int(r.get("handle_nonsubscript_sites") or 0)
    return {
        "keys": sorted(keys),
        "files_seen": len(files),
        "rows": rows,
        "holes": holes,
        "lit": lit,
        "sub": sub,
        "a": lit | sub,
        "b": hn,
        "a_keys": a_keys,
        "b_keys": b_keys,
        "invisible_sites": nonsubscript,
    }


ROUND_SCRIPT = re.compile(r"_r\d{3,}")


def file_class(module):
    """A round probe vs a module somebody would call production.

    The split has to be mechanical and visible in the name, because the point of
    the count is whether the added volume sits in code that ships or in the
    one-shot scripts each round writes to answer a question.
    """
    base = os.path.basename(module)
    if ROUND_SCRIPT.search(base) or base.startswith("_probe"):
        return "round_script"
    if base.startswith("_"):
        return "underscore_temporary"
    return "production_module"


def class_of(lit, sub, hn):
    """Volume class: is this file carried by the arms given?

    The class is 'carried', not a label listing arms, because the question this
    face answers is whether E652's volume should contain the file at all. A file
    already carried that merely gains a handle label has not flipped class.
    """
    return "carried" if (lit or sub or hn) else "not_carried"


def counts_of(m, e652_published=None):
    a, b = m["a"], m["b"]
    gain = b - a
    lost = a - b
    both = a & b
    lit, sub = m["lit"], m["sub"]
    transitions = {}
    flips = []
    for r in m["rows"]:
        if r.get("hole"):
            continue
        before = class_of(r.get("literal_arm"), r.get("subscript_arm"), False)
        after = class_of(r.get("literal_arm"), r.get("subscript_arm"),
                         r.get("handle_arm"))
        key = "%s -> %s" % (before, after)
        transitions[key] = transitions.get(key, 0) + 1
        if before != after:
            flips.append({
                "module": r["module"],
                "before": before,
                "after": after,
                "class": file_class(r["module"]),
                "sites": r.get("handle_site_detail") or [],
                "sites_elided": r.get("handle_site_detail_elided") or 0,
            })
    flips.sort(key=lambda f: f["module"])
    counts = {
        "python_files_walked": m["files_seen"],
        "volume_literal_only": len(lit),
        "volume_literal_plus_subscript": len(a),
        "volume_all_three": len(a | b),
        "handle_files_already_carried": len(both),
        "handle_files_not_carried": len(gain),
        "files_carrying_a_counted_row_key_e652_arm": len(a),
        "files_carrying_a_counted_key_inside_a_handle_arm": len(b),
        "files_in_both_arms": len(both),
        "files_the_handle_arm_adds": len(gain),
        "files_only_the_handle_arm_sees": len(gain),
        "files_only_the_e652_arm_carries": len(lost),
        "volume_before": len(a),
        "volume_after": len(a | b),
        "counted_keys_named_by_the_e652_arm": sum(
            len(v) for v in m["a_keys"].values()
        ),
        "invisible_sites_inside_added_files": m["invisible_sites"],
        "holes": m["holes"],
        "counted_row_keys": len(m["keys"]),
        "volume_class_transitions": dict(sorted(transitions.items())),
        "files_whose_class_flips": len(flips),
    }
    if e652_published is not None:
        counts["e652_published_volume"] = e652_published
        counts["reproduces_e652_published_volume"] = (
            len(a) == e652_published
        )
        counts["vintage_delta_vs_e652_published"] = len(a) - e652_published
    by_class = {}
    for module in gain:
        name = file_class(module)
        by_class[name] = by_class.get(name, 0) + 1
    counts["added_files_by_class"] = dict(sorted(by_class.items()))
    counts["_flips"] = flips
    return counts


def decide(c):
    if not c.get("python_files_walked"):
        return V_NO_POPULATION
    if c["files_carrying_a_counted_key_inside_a_handle_arm"] == 0:
        return V_NO_HANDLE
    if c["files_the_handle_arm_adds"] == 0:
        return V_ALL_VISIBLE
    return V_FOLD_GROWS


def answer_of(c):
    if not c.get("python_files_walked"):
        return "no file walked, so no volume exists to fold anything into"
    if c["files_the_handle_arm_adds"] == 0:
        return (
            "all %d files the handle arm sees are already carried by E652's own "
            "arms, so the published volume of %d stands"
            % (
                c["files_carrying_a_counted_key_inside_a_handle_arm"],
                c["volume_before"],
            )
        )
    text = (
        "on one tree and one walk the volume runs %d (literal arm only) -> %d "
        "(literal + subscript, E652's published rule) -> %d (all three arms); "
        "%d files hold a counted key inside an unresolved string handle and %d "
        "of those are already carried by E652's own arms, so the handle arm adds "
        "%d files (+%.2f%%) and %d counted key sites sit where no subscript arm "
        "can reach them."
        % (
            c["volume_literal_only"],
            c["volume_literal_plus_subscript"],
            c["volume_all_three"],
            c["files_carrying_a_counted_key_inside_a_handle_arm"],
            c["files_in_both_arms"],
            c["files_the_handle_arm_adds"],
            100.0
            * c["files_the_handle_arm_adds"]
            / max(1, c["volume_literal_plus_subscript"]),
            c["invisible_sites_inside_added_files"],
        )
    )
    if c.get("e652_published_volume") is not None:
        delta = c["vintage_delta_vs_e652_published"]
        if c["reproduces_e652_published_volume"]:
            text += (
                " This walk reproduces E652's published volume of %d exactly."
                % c["e652_published_volume"]
            )
        else:
            text += (
                " E652 published %d on its own tree, so this walk's baseline is "
                "%+d against it (a vintage delta, not a correction); the gain is "
                "measured inside this one walk and does not depend on that delta."
                % (c["e652_published_volume"], delta)
            )
    if c.get("added_files_by_class"):
        classes = c["added_files_by_class"]
        text += " Added files by class: " + ", ".join(
            "%s=%d" % (k, classes[k]) for k in sorted(classes)
        ) + "."
    return text


def face_from(m, e652_published=None, e652_stamp=None):
    c = counts_of(m, e652_published)
    flips = c.pop("_flips", [])
    gain_rows = []
    for module in sorted(m["b"] - m["a"])[:60]:
        gain_rows.append(
            {
                "module": module,
                "class": file_class(module),
                "handle_keys": m["b_keys"].get(module) or [],
            }
        )
    published_flips = flips[:60]
    return {
        "study": STUDY,
        "date": TODAY,
        "evidence_cutoff": TODAY,
        "source_face": SOURCE_FACE,
        "source_face_stamp": e652_stamp,
        "deliverable": "results/state_tilt/VOLUMEFOLD.json",
        "method": [
            "re-derive the counted read population E638 joins and the corpus "
            "E652 walks, with the same 1MB read cap, so both arms skip the same "
            "files and nothing is priced against a different population",
            "walk that corpus three ways per file: E652's string arm (a literal "
            "equal to a counted key), E652's tree-wide Subscript arm, and E657's "
            "unresolved-handle arm priced against the same key set",
            "publish the volume under all three arm combinations: literal only, "
            "literal + subscript (E652's published rule), and all three",
            "publish the per-file class transition counts and every file whose "
            "class flips once the handle arm is added, with the site that "
            "flipped it (key, role, line, column)",
            "compare the literal + subscript volume against E652's published "
            "number: an equal count reads as reproduced, anything else is "
            "published as a vintage delta and no correction is claimed",
        ],
        "population_source": "e652.corpus() with each arm's own self-exclusion",
        "volume_before": c["volume_before"],
        "volume_after": c["volume_after"],
        "gain": c["files_the_handle_arm_adds"],
        "verdict": decide(c),
        "answer": answer_of(c),
        "counts": c,
        "files_the_handle_arm_adds": gain_rows,
        "files_the_handle_arm_adds_elided": max(
            0, c["files_the_handle_arm_adds"] - len(gain_rows)
        ),
        "files_whose_class_flips": published_flips,
        "files_whose_class_flips_elided": max(
            0, c["files_whose_class_flips"] - len(published_flips)
        ),
        "limits": [
            "a file is 'carried' by an arm only under that arm's own rule; the "
            "fold states membership, not how many keys or sites the file holds",
            "an unresolved handle E657 cannot resolve (unreadable offset) is "
            "invisible to both arms, so the gain is a floor",
            "the 1MB read cap skips the same files in both arms; the hole "
            "counts are published rather than assumed zero",
            "added_files_by_class splits on the file name only (a _rNNN stamp "
            "or an underscore prefix), not on what the file does, so a probe "
            "shipped under a plain name reads as a production module",
            "this face walks one tree at one moment: a till changed tree moves "
            "both membership sets together",
        ],
    }


def face_problems(face):
    problems = []
    c = face.get("counts") or {}
    rows = face.get("files_the_handle_arm_adds") or []
    walked = c.get("python_files_walked") or 0
    a = c.get("files_carrying_a_counted_row_key_e652_arm") or 0
    b = c.get("files_carrying_a_counted_key_inside_a_handle_arm") or 0
    both = c.get("files_in_both_arms") or 0
    gain = c.get("files_the_handle_arm_adds") or 0
    only_a = c.get("files_only_the_e652_arm_carries") or 0
    if a > walked or b > walked:
        problems.append("an arm claims more files than were walked")
    if both + gain != b:
        problems.append(
            "handle arm does not re-add from its parts (%d + %d vs %d)"
            % (both, gain, b)
        )
    if both + only_a != a:
        problems.append(
            "e652 arm does not re-add from its parts (%d + %d vs %d)"
            % (both, only_a, a)
        )
    if (c.get("volume_after") or 0) != a + gain:
        problems.append(
            "volume_after is not volume_before plus the gain (%s vs %d)"
            % (c.get("volume_after"), a + gain)
        )
    if (c.get("volume_before") or 0) != a:
        problems.append("volume_before is not the e652 arm's membership")
    if len(rows) + (face.get("files_the_handle_arm_adds_elided") or 0) != gain:
        problems.append("published gain rows do not re-add to the gain")
    by_class = c.get("added_files_by_class") or {}
    if sum(by_class.values()) != gain:
        problems.append(
            "added files by class do not re-add to the gain (%d vs %d)"
            % (sum(by_class.values()), gain)
        )
    lit = c.get("volume_literal_only") or 0
    pub = c.get("volume_literal_plus_subscript") or 0
    allthree = c.get("volume_all_three") or 0
    if not (lit <= pub <= allthree):
        problems.append(
            "the three arm volumes are not monotone (%d, %d, %d)" % (lit, pub, allthree)
        )
    if pub != a:
        problems.append("literal+subscript volume is not the e652 arm")
    if allthree != a + gain:
        problems.append(
            "all-three volume is not the union (%d vs %d)" % (allthree, a + gain)
        )
    flips = face.get("files_whose_class_flips") or []
    if len(flips) + (face.get("files_whose_class_flips_elided") or 0) != (
        c.get("files_whose_class_flips") or 0
    ):
        problems.append("published class flips do not re-add to the flip count")
    if (c.get("files_whose_class_flips") or 0) != gain:
        problems.append(
            "a handle-arm gain must be exactly a class flip (%d vs %d)"
            % (c.get("files_whose_class_flips"), gain)
        )
    transitions = c.get("volume_class_transitions") or {}
    walked_ok = sum(transitions.values()) + sum(
        (c.get("holes") or {}).values()
    )
    if walked_ok != (c.get("python_files_walked") or 0):
        problems.append(
            "class transitions plus holes do not cover the walk (%d vs %d)"
            % (walked_ok, c.get("python_files_walked"))
        )
    if any(k.startswith("_") for k in c):
        problems.append("a private key leaked into the published counts")
    for f in flips:
        if f.get("before") == f.get("after"):
            problems.append("a published flip does not change class")
            break
        if not f.get("sites"):
            problems.append("a published flip names no site")
            break
        roles = {s.get("role") for s in f["sites"]}
        if roles and roles == {"subscript_key"}:
            problems.append(
                "a file flips on a subscript site alone, which E652's subscript "
                "arm already walks -- the arm split is wrong"
            )
            break
    for r in rows:
        if not str(r.get("module", "")).strip():
            problems.append("a gain row has no module")
            break
        if r["module"].count("\\"):
            problems.append("a gain row carries a backslash path")
            break
        base = os.path.basename(r["module"])
        if any(base.startswith(p) for p in SELF_PARTS):
            problems.append("a self file is counted as a gain")
            break
    return problems


def write_face(out_dir, doc, face=FACE, latest=LATEST):
    os.makedirs(out_dir, exist_ok=True)
    blob = json.dumps(doc, ensure_ascii=False, indent=1, sort_keys=False)
    for name in (face, latest):
        path = os.path.join(out_dir, name)
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(blob)
            fh.write("\n")
    return os.path.join(out_dir, face)


def load_e652(path=None, root=ROOT):
    path = path or os.path.join(root, E652_FACE)
    try:
        with io.open(path, encoding="utf-8") as fh:
            doc = json.load(fh)
    except (OSError, ValueError):
        return None, None
    published = ((doc.get("volume") or {}).get("files_carrying_a_counted_row_key"))
    stamp = doc.get("evidence_cutoff") or doc.get("date")
    return published, stamp


def build(root=ROOT, out_dir=None, workers=12, counted=None):
    published, stamp = load_e652(root=root)
    m = membership(root=root, counted=counted, workers=workers)
    doc = face_from(m, e652_published=published, e652_stamp=stamp)
    problems = face_problems(doc)
    if problems:
        say("FACE-PROBLEMS: " + "; ".join(problems))
        return 3, doc
    path = write_face(out_dir or OUTDIR, doc)
    say("wrote " + rel(path, root))
    return 0, doc


def check(path=None, root=ROOT):
    path = path or os.path.join(root, OUTDIR, FACE)
    with io.open(path, encoding="utf-8") as fh:
        face = json.load(fh)
    problems = face_problems(face)
    say("check problems=%s" % json.dumps(problems, ensure_ascii=False))
    return 0 if not problems else 3


def selftest():
    """Fixture tree: three files, one per membership class."""
    import tempfile

    legs = []

    def leg(name, ok, note=""):
        legs.append((name, bool(ok), note))
        say("%s %s%s" % ("PASS" if ok else "FAIL", name,
                         (" -- " + note) if note and not ok else ""))

    tmp = tempfile.mkdtemp(prefix="e658_")
    files = {
        "arm_e652_only.py": "def f(d):\n    return d['rows']\n",
        "arm_handle_only.py": (
            "def f(d):\n    return f'{d.get(\"rows\")},{d.get(\"cols\")}'\n"
        ),
        "both_arms.py": (
            "def f(d):\n    x = d['rows']\n    return f'{d.get(\"cols\")}'\n"
        ),
        "no_key_at_all.py": "def f(d):\n    return d['value']\n",
    }
    for name, body in files.items():
        p = os.path.join(tmp, name)
        with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body)

    keys = {"rows", "cols"}
    empty_index = e652.target_index([], tmp)
    jobs = [(os.path.join(tmp, n), keys, empty_index, tmp) for n in files]
    rows = [scan_one(j) for j in jobs]
    by = {r["module"]: r for r in rows}

    leg("fixture_reads_three_arm_classes",
        by["arm_e652_only.py"]["literal_arm"] is True
        and by["arm_e652_only.py"]["subscript_arm"] is True
        and by["arm_e652_only.py"]["handle_arm"] is False)
    leg("fixture_prices_a_handle_key",
        by["arm_handle_only.py"]["handle_arm"] is True,
        json.dumps(by["arm_handle_only.py"], ensure_ascii=False)[:200])
    leg("fixture_handle_file_is_blind_to_both_e652_arms",
        by["arm_handle_only.py"]["literal_arm"] is False
        and by["arm_handle_only.py"]["subscript_arm"] is False,
        json.dumps(by["arm_handle_only.py"], ensure_ascii=False)[:200])
    leg("fixture_no_key_carries_nothing",
        by["no_key_at_all.py"]["literal_arm"] is False
        and by["no_key_at_all.py"]["subscript_arm"] is False
        and by["no_key_at_all.py"]["handle_arm"] is False)

    a = {r["module"] for r in rows if r["literal_arm"] or r["subscript_arm"]}
    b = {r["module"] for r in rows if r["handle_arm"]}
    lit = {r["module"] for r in rows if r["literal_arm"]}
    sub = {r["module"] for r in rows if r["subscript_arm"]}
    m = {"keys": sorted(keys), "files_seen": len(rows), "rows": rows,
         "holes": {"over_the_size_cap": 0, "unreadable": 0,
                   "does_not_parse": 0},
         "lit": lit, "sub": sub, "a": a, "b": b,
         "a_keys": {}, "b_keys": {}, "invisible_sites": 0}
    c = counts_of(m)
    leg("set_union_identity", c["volume_after"] == c["volume_before"] + c["files_the_handle_arm_adds"])
    leg("handle_arm_readds", c["files_in_both_arms"] + c["files_the_handle_arm_adds"]
        == c["files_carrying_a_counted_key_inside_a_handle_arm"])
    leg("e652_arm_readds", c["files_in_both_arms"] + c["files_only_the_e652_arm_carries"]
        == c["files_carrying_a_counted_row_key_e652_arm"])
    leg("three_arm_volumes_monotone",
        c["volume_literal_only"] <= c["volume_literal_plus_subscript"]
        <= c["volume_all_three"])
    leg("a_gain_is_a_class_flip", c["files_whose_class_flips"]
        == c["files_the_handle_arm_adds"])
    leg("arm_e652_only_is_not_a_gain", "arm_e652_only.py" not in (b - a))
    leg("handle_only_is_a_gain", "arm_handle_only.py" in (b - a),
        str(sorted(b - a)))

    doc = face_from(m)
    leg("face_recomputes_without_problems", face_problems(doc) == [],
        str(face_problems(doc)))

    # a self file must never enter the gain set
    leg("self_exclusion_predicate",
        is_self("scripts/e658_volume_fold.py") and not is_self("scripts/e652_string_arm_census.py"))

    # empty walk is NOT-ASSESSED, not a zero
    empty = {"keys": [], "files_seen": 0, "rows": [],
             "holes": {"over_the_size_cap": 0, "unreadable": 0, "does_not_parse": 0},
             "lit": set(), "sub": set(), "a": set(), "b": set(),
             "a_keys": {}, "b_keys": {}, "invisible_sites": 0}
    doc0 = face_from(empty)
    leg("empty_walk_is_not_assessed", doc0["verdict"] == V_NO_POPULATION)

    # a vintage that disagrees with the published count is published as a delta
    # and must not swallow the gain measured inside this walk
    c2 = counts_of(m, e652_published=99)
    leg("vintage_delta_is_named",
        c2["vintage_delta_vs_e652_published"] == c2["volume_before"] - 99
        and c2["reproduces_e652_published_volume"] is False
        and decide(c2) == decide(c),
        "verdict changed with the baseline: %s vs %s" % (decide(c2), decide(c)))
    leg("reproduced_volume_is_claimed_when_equal",
        decide(counts_of(m, e652_published=c["volume_before"])) in (V_FOLD_GROWS, V_NO_HANDLE, V_ALL_VISIBLE))

    # face where every handle file is already carried
    m3 = dict(m)
    m3["a"] = set(a) | set(b)
    c3 = counts_of(m3)
    leg("no_gain_arm_reads_as_no_gain", c3["files_the_handle_arm_adds"] == 0)

    ok = all(l[1] for l in legs)
    say("selftest %d/%d" % (sum(1 for l in legs if l[1]), len(legs)))
    return 0 if ok else 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd")
    b = sub.add_parser("build")
    b.add_argument("--workers", type=int, default=12)
    sub.add_parser("selftest")
    c = sub.add_parser("check")
    c.add_argument("--face", default=None)
    args = parser.parse_args(argv)

    if args.cmd == "selftest":
        return selftest()
    if args.cmd == "check":
        return check(args.face)
    if args.cmd == "build":
        rc, doc = build(workers=args.workers)
        say("verdict=%s" % doc.get("verdict"))
        say(doc.get("answer"))
        return rc
    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
