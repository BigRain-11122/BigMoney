"""E661: how much of the published "files carrying a counted row key" volume is
archaeology rather than code that runs.

E652 counts a file as carrying a counted row key when a string literal equals a
key or a Subscript names one; E658 folded E657's unresolved-handle arm in and
published the volume under all three arms (3850 / 3864 / 3873 on its tree). E654
then found that all 16 scoped counted-key sites live in round scripts reading
their own diagnostic JSON -- i.e. the population that carries the key may be
dominated by one-shot probes, not by modules anybody calls again.

This face prices the same question across E658's whole volume: every carrying
file is split by where it sits (a round script's stem, results/ scratch, a live
module root, a test or smoke leg) and by stem shape, the counted-key histogram is
published per class, and the volume is reconciled against E658's published arm
totals rather than restated from them.

Rules carried from this family:
  * every input is machine-read (E658's face for the published baseline, the
    tree for the members); no count from a predecessor is typed into this file
    (E239).
  * the walk is one walk: the per-class members must re-add to the walk's own
    volume or the face refuses to publish (E366 -- name every member one way).
  * a class split on a file NAME is a name claim, so the priority order and every
    rule are published with the counts (E194/E206 family).
"""

import argparse
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE = "VOLUMEVINTAGE.json"
LATEST = "volumevintage_latest.json"
STUDY = "E661_volume_vintage"
E658_FACE = "results/state_tilt/VOLUMEFOLD.json"
E652_FACE = "results/state_tilt/STRINGARMCENSUS.json"
SELF_PARTS = ("e661_", "run_e661_")

sys.path.insert(0, HERE)
import e658_volume_fold as e658  # noqa: E402

ROUND_SCRIPT = re.compile(r"_r\d{3,}")
SMOKE_LEG = re.compile(r"(^run_.*_smoke_leg$|^smoke_test$|^_?test_)")
LIVE_ROOTS = ("scripts/", "Tools/", "firm/", "live/")

V_NO_POPULATION = "not_assessable_the_walk_carried_no_files"
V_ALL_ROUND = "every_carrying_file_is_a_round_script_or_scratch_artifact"
V_ALL_LIVE = "every_carrying_file_is_a_live_module"
V_MIXED = "the_volume_splits_between_archaeology_and_live_code"

PRIORITY = ["round_script", "results_scratch", "test_or_smoke_leg", "live_module", "other"]


def say(line):
    sys.stdout.write(str(line) + "\n")
    sys.stdout.flush()


def rel(path, root=ROOT):
    path = os.path.abspath(path)
    root = os.path.abspath(root)
    try:
        return os.path.relpath(path, root).replace("\\", "/")
    except ValueError:
        return path.replace("\\", "/")


def is_self(name):
    base = os.path.basename(name)
    return any(base.startswith(p) or p in base for p in SELF_PARTS)


def path_class(module):
    """Where the file sits, read off its repository-relative path."""
    p = module.replace("\\", "/")
    if p.startswith("results/") or p.startswith("state/"):
        return "results_scratch"
    if p.startswith(LIVE_ROOTS):
        return "live_module"
    return "other"


def stem_class(module):
    base = os.path.basename(module)
    stem = base[:-3] if base.endswith(".py") else base
    if ROUND_SCRIPT.search(stem) or stem.startswith("_probe"):
        return "round_script"
    if SMOKE_LEG.search(stem):
        return "test_or_smoke_leg"
    if stem.startswith("_"):
        return "underscore_temporary"
    return "plain_stem"


def resolve_class(module):
    """One class per file, in the published priority order.

    A round script under results/ is archaeology either way; the priority keeps
    the two overlapping dimensions from double-counting the same file.
    """
    sc = stem_class(module)
    pc = path_class(module)
    if sc == "round_script":
        return "round_script"
    if pc == "results_scratch":
        return "results_scratch"
    if sc == "test_or_smoke_leg":
        return "test_or_smoke_leg"
    if pc == "live_module":
        return "live_module"
    return "other"


def membership(root=ROOT, workers=12, counted=None):
    m = e658.membership(root=root, counted=counted, workers=workers)
    carrying = sorted(r["module"] for r in m["rows"]
                      if r.get("literal_arm") or r.get("subscript_arm")
                      or r.get("handle_arm"))
    keys_of = {}
    for r in m["rows"]:
        if r.get("hole"):
            continue
        named = set(r.get("literal_keys") or []) | set(r.get("handle_keys") or [])
        if named:
            keys_of[r["module"]] = sorted(named)
    m["carrying"] = [c for c in carrying if not is_self(c)]
    m["keys_of"] = keys_of
    return m


def split_counts(m):
    by_class, by_path, by_stem = {}, {}, {}
    file_lists = {}
    key_hist = {}
    for module in m["carrying"]:
        cl = resolve_class(module)
        by_class[cl] = by_class.get(cl, 0) + 1
        file_lists.setdefault(cl, []).append(module)
        pc = path_class(module)
        by_path[pc] = by_path.get(pc, 0) + 1
        sc = stem_class(module)
        by_stem[sc] = by_stem.get(sc, 0) + 1
        n = len(m["keys_of"].get(module) or [])
        key_hist[n] = key_hist.get(n, 0) + 1
    return {
        "files_walked": m["files_seen"],
        "volume_this_walk": len(m["carrying"]),
        "volume_literal_only": len(m["lit"] - {x for x in m["lit"] if is_self(x)}),
        "volume_handle_arm": len(m["b"] - {x for x in m["b"] if is_self(x)}),
        "by_class": dict(sorted(by_class.items())),
        "by_path_class": dict(sorted(by_path.items())),
        "by_stem_class": dict(sorted(by_stem.items())),
        "counted_keys_named_per_file": dict(
            sorted((str(k), v) for k, v in key_hist.items())),
        "files_naming_no_counted_key": sum(
            1 for mod in m["carrying"] if not m["keys_of"].get(mod)),
        "holes": m["holes"],
        "counted_row_keys": len(m["keys"]),
        "_file_lists": file_lists,
    }


def load_published(path, root=ROOT):
    try:
        with io.open(os.path.join(root, path), encoding="utf-8") as fh:
            return json.load(fh), None
    except (OSError, ValueError) as exc:
        return None, str(exc)


def reconcile(c, e658_doc, e658_err, e652_doc, e652_err):
    out = {}
    if e658_doc:
        counts = e658_doc.get("counts") or {}
        for key in ("volume_literal_only", "volume_literal_plus_subscript",
                    "volume_all_three"):
            pub = counts.get(key)
            if pub is None:
                continue
            mine = {"volume_literal_only": c["volume_literal_only"],
                    "volume_literal_plus_subscript": c["volume_this_walk"],
                    "volume_all_three": c["volume_this_walk"]}[key]
            out["e658_" + key] = pub
            out["this_walk_" + key] = mine
    if e658_doc is None:
        out["e658_unreadable"] = e658_err or "absent"
    if e652_doc:
        pub = ((e652_doc.get("volume") or {}).get(
            "files_carrying_a_counted_row_key"))
        if pub is not None:
            out["e652_published_volume"] = pub
            out["this_walk_vs_e652"] = c["volume_this_walk"] - pub
    else:
        out["e652_unreadable"] = e652_err or "absent"
    return out


def decide(c):
    if not c.get("files_walked") or not c.get("volume_this_walk"):
        return V_NO_POPULATION
    cls = c["by_class"]
    archaeology = cls.get("round_script", 0) + cls.get("results_scratch", 0)
    live = cls.get("live_module", 0)
    if archaeology == c["volume_this_walk"]:
        return V_ALL_ROUND
    if live == c["volume_this_walk"]:
        return V_ALL_LIVE
    return V_MIXED


def answer_of(c):
    if decide(c) == V_NO_POPULATION:
        return "no carrying file in this walk, so there is no volume to split"
    cls = c["by_class"]
    vol = c["volume_this_walk"]
    parts = ", ".join("%s=%d" % (k, cls[k]) for k in PRIORITY if k in cls)
    live = cls.get("live_module", 0)
    arch = cls.get("round_script", 0) + cls.get("results_scratch", 0)
    text = (
        "of %d python files walked, %d carry a counted row key under E658's "
        "three arms; they split %s -- %.1f%% archaeology (round scripts plus "
        "results/ scratch) against %.1f%% live modules, so the published "
        "volume is %s"
        % (c["files_walked"], vol, parts,
           100.0 * arch / max(1, vol), 100.0 * live / max(1, vol),
           "dominated by one-shot round probes" if arch > live else
           "dominated by code that runs")
    )
    return text


def publish_rows(c, keep=40):
    rows = {}
    for cl in PRIORITY:
        names = c["_file_lists"].get(cl) or []
        rows[cl] = names[:keep]
    return rows


def face_from(m, e658_doc=None, e658_err=None, e652_doc=None, e652_err=None):
    c = split_counts(m)
    rec = reconcile(c, e658_doc, e658_err, e652_doc, e652_err)
    rows = publish_rows(c)
    pub = {
        "study": STUDY,
        "card": "E661",
        "title": ("how much of the counted-row-key volume is round-script "
                  "archaeology rather than live modules"),
        "evidence_cutoff": "2026-11-26",
        "deliverable": "results/state_tilt/" + FACE,
        "source_face": E658_FACE,
        "verdict": decide(c),
        "answer": answer_of(c),
        "class_rules": {
            "priority": PRIORITY,
            "round_script": "stem matches _r<3+ digits> or starts with _probe",
            "results_scratch": "repository path starts with results/ or state/",
            "test_or_smoke_leg": "stem starts with run_<x>_smoke_leg, smoke_test or _?test_",
            "live_module": "repository path starts with scripts/, Tools/, firm/ or live/",
            "other": "everything else",
        },
        "counts": {k: v for k, v in c.items() if not k.startswith("_")},
        "published_rows_by_class": rows,
        "published_rows_kept_per_class": 40,
        "reconciliation": rec,
        "limits": [
            "the class split is read off the file NAME and PATH, so a probe "
            "shipped under a plain name reads as a live module",
            "only the literal and handle arms name a concrete key; a file "
            "carried by the subscript arm alone names no key and lands in the "
            "keys=0 bucket",
            "one tree at one moment: the count moves with the tree (E658's and "
            "E652's published volumes were measured on their own trees and are "
            "compared, not restated)",
        ],
    }
    return pub


def face_problems(face):
    problems = []
    c = face.get("counts") or {}
    vol = c.get("volume_this_walk") or 0
    by_class = c.get("by_class") or {}
    if sum(by_class.values()) != vol:
        problems.append("class counts do not re-add to the volume (%d vs %d)"
                        % (sum(by_class.values()), vol))
    if sum((c.get("by_path_class") or {}).values()) != vol:
        problems.append("path-class counts do not re-add to the volume")
    if sum((c.get("by_stem_class") or {}).values()) != vol:
        problems.append("stem-class counts do not re-add to the volume")
    if sum((c.get("counted_keys_named_per_file") or {}).values()) != vol:
        problems.append("the key histogram does not re-add to the volume")
    if vol > (c.get("files_walked") or 0):
        problems.append("the volume exceeds the files walked")
    if c.get("volume_literal_only", 0) > vol:
        problems.append("the literal arm exceeds the union volume")
    for cl, key in (("round_script", "by_class"), ("live_module", "by_class")):
        if cl not in by_class and vol:
            problems.append("a required class %s is missing while files exist" % cl)
            break
    rec = face.get("reconciliation") or {}
    for key in rec:
        if key.startswith("this_walk_") and not key[len("this_walk_"):]:
            problems.append("an empty this_walk_ key leaked into the reconciliation")
    if face.get("verdict") == V_NO_POPULATION and vol:
        problems.append("empty-walk verdict published beside a non-zero volume")
    if not face.get("verdict") in (V_NO_POPULATION, V_ALL_ROUND, V_ALL_LIVE, V_MIXED):
        problems.append("unknown verdict")
    rows = face.get("published_rows_by_class") or {}
    for cl, names in rows.items():
        for name in names:
            if not str(name).strip():
                problems.append("a published row has no module")
                break
            if name.count("\\"):
                problems.append("a published row carries a backslash path")
                break
            if resolve_class(name) != cl:
                problems.append("a published row sits in a class its own name contradicts")
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


def build(root=ROOT, out_dir=None, workers=12, counted=None):
    e658_doc, e658_err = load_published(E658_FACE, root)
    e652_doc, e652_err = load_published(E652_FACE, root)
    m = membership(root=root, workers=workers, counted=counted)
    doc = face_from(m, e658_doc, e658_err, e652_doc, e652_err)
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


def verify(path=None, root=ROOT, workers=12):
    """Re-walk the corpus and compare the published readings field by field.

    Only readings this walk re-derives are compared: the tree-vintage fields
    (files_walked, volume, holes) are published beside the comparison, never
    used as a gate, or a tree that grows by one probe would redden the leg.
    """
    path = path or os.path.join(root, OUTDIR, FACE)
    with io.open(path, encoding="utf-8") as fh:
        published = json.load(fh)
    e658_doc, e658_err = load_published(E658_FACE, root)
    e652_doc, e652_err = load_published(E652_FACE, root)
    again = face_from(membership(root=root, workers=workers),
                      e658_doc, e658_err, e652_doc, e652_err)
    problems = face_problems(again)
    for key in ("verdict", "class_rules"):
        if published.get(key) != again.get(key):
            problems.append("published %s does not re-derive" % key)
    pub_c = published.get("counts") or {}
    new_c = again.get("counts") or {}
    for key in ("by_class", "by_path_class", "by_stem_class",
                "counted_keys_named_per_file"):
        if pub_c.get(key) != new_c.get(key):
            problems.append(
                "published %s differs (%s vs %s)"
                % (key, json.dumps(pub_c.get(key), sort_keys=True)[:160],
                   json.dumps(new_c.get(key), sort_keys=True)[:160]))
    say("verify problems=%s" % json.dumps(problems, ensure_ascii=False))
    say("vintage this walk: files_walked=%s volume=%s"
        % (new_c.get("files_walked"), new_c.get("volume_this_walk")))
    return 0 if not problems else 3


def selftest():
    import tempfile

    legs = []

    def leg(name, ok, note=""):
        legs.append((name, bool(ok), note))
        say("%s %s%s" % ("PASS" if ok else "FAIL", name,
                         (" -- " + note) if note and not ok else ""))

    leg("round_script_wins_over_path", resolve_class("results/state_tilt/_r1675_scan.py")
        == "round_script", resolve_class("results/state_tilt/_r1675_scan.py"))
    leg("results_scratch_reads_scratch",
        resolve_class("results/state_tilt/_tmp_scan.py") == "results_scratch")
    leg("live_module_reads_live", resolve_class("scripts/update_daily.py") == "live_module")
    leg("tools_live_module", resolve_class("Tools/idle_trigger.py") == "live_module")
    leg("smoke_leg_class", resolve_class("scripts/run_e640_smoke_leg.py")
        == "test_or_smoke_leg")
    leg("other_class", resolve_class("vendor/lib.py") == "other")

    tmp = tempfile.mkdtemp(prefix="e661_")
    mods = {
        "scripts/live_mod.py": "def f(d):\n    return d['rows']\n",
        "results/_r1600_probe.py": "def f(d):\n    return d['rows']\n",
        "scripts/run_zz_smoke_leg.py": "def f(d):\n    return d.get('rows')\n",
        "vendor/other.py": "def f(d):\n    return d['value']\n",
    }
    for name, body in mods.items():
        p = os.path.join(tmp, name)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body)

    m = {"files_seen": 4, "keys": ["rows"],
         "rows": [
             {"module": "scripts/live_mod.py", "literal_arm": True,
              "subscript_arm": True, "handle_arm": False, "literal_keys": ["rows"]},
             {"module": "results/_r1600_probe.py", "literal_arm": True,
              "subscript_arm": True, "handle_arm": False, "literal_keys": ["rows"]},
             {"module": "scripts/run_zz_smoke_leg.py", "literal_arm": False,
              "subscript_arm": True, "handle_arm": False, "literal_keys": []},
             {"module": "vendor/other.py", "literal_arm": False,
              "subscript_arm": False, "handle_arm": False, "literal_keys": []},
         ],
         "lit": {"scripts/live_mod.py", "results/_r1600_probe.py"},
         "sub": {"scripts/live_mod.py", "results/_r1600_probe.py",
                 "scripts/run_zz_smoke_leg.py"},
         "b": set(), "holes": {"over_the_size_cap": 0, "unreadable": 0,
                               "does_not_parse": 0},
         "keys_of": {"scripts/live_mod.py": ["rows"],
                     "results/_r1600_probe.py": ["rows"]}}
    m["carrying"] = sorted(["scripts/live_mod.py", "results/_r1600_probe.py",
                            "scripts/run_zz_smoke_leg.py"])
    doc = face_from(m)
    c = doc["counts"]
    leg("fixture_volume_is_three", c["volume_this_walk"] == 3)
    leg("fixture_classes_readd", sum(c["by_class"].values()) == 3,
        json.dumps(c["by_class"]))
    leg("fixture_split_is_mixed", doc["verdict"] == V_MIXED, doc["verdict"])
    leg("fixture_archaeology_one", c["by_class"].get("round_script") == 1)
    leg("fixture_live_one", c["by_class"].get("live_module") == 1)
    leg("fixture_face_clean", face_problems(doc) == [], str(face_problems(doc)))
    leg("fixture_key_histogram_readds",
        sum(c["counted_keys_named_per_file"].values()) == 3)

    empty = {"files_seen": 0, "keys": [], "rows": [], "lit": set(), "sub": set(),
             "b": set(), "holes": {"over_the_size_cap": 0, "unreadable": 0,
                                   "does_not_parse": 0},
             "keys_of": {}, "carrying": []}
    doc0 = face_from(empty)
    leg("empty_walk_is_not_assessed", doc0["verdict"] == V_NO_POPULATION)

    allround = dict(m)
    allround["carrying"] = ["results/_r1600_probe.py"]
    leg("all_archaeology_verdict", face_from(allround)["verdict"] == V_ALL_ROUND)

    alllive = dict(m)
    alllive["carrying"] = ["scripts/live_mod.py"]
    leg("all_live_verdict", face_from(alllive)["verdict"] == V_ALL_LIVE)

    leg("self_exclusion_predicate",
        is_self("scripts/e661_volume_vintage.py")
        and not is_self("scripts/e658_volume_fold.py"))

    bad = json.loads(json.dumps(doc))
    bad["counts"]["by_class"]["round_script"] = 99
    leg("readd_gate_catches_a_broken_split", face_problems(bad) != [])

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
    v = sub.add_parser("verify")
    v.add_argument("--face", default=None)
    v.add_argument("--workers", type=int, default=12)
    args = parser.parse_args(argv)

    if args.cmd == "selftest":
        return selftest()
    if args.cmd == "check":
        return check(args.face)
    if args.cmd == "verify":
        return verify(args.face, workers=args.workers)
    if args.cmd == "build":
        rc, doc = build(workers=args.workers)
        say("verdict=%s" % doc.get("verdict"))
        say(doc.get("answer"))
        return rc
    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
