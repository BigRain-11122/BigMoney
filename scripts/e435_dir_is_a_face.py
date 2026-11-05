"""E435 - whether a published directory value is itself the name of a published face.

E423 counted 822 directory-named published fields (679 on today's tree) and 44 that carry a
file path. It never asked the other half of the promise: a field named `dir` is read as a
base, so if that base happens to be the *name of a face* rather than a directory, a join on it
silently picks a face as its parent. This study prices that shape on the same population.

Four mechanical questions, no vocabulary games:

  1. of the directory-valued fields, how many hold a value whose basename equals the stem of a
     published face (a name-space collision: `cells` is a face name and a directory name);
  2. how many hold a value that is the *home directory* of a published face (the base is the
     face's parent, so a join lands inside a face family rather than in a workspace);
  3. of the rows that also carry a name field, how many compose -- join(value, name) -- onto a
     path that exists on disk today (the composition is not hypothetical, it is live);
  4. do those composed paths collide with a published face that already lives there.

The distinction that keeps this honest is (3) versus (4): a row whose join lands on nothing is
a shape; a row whose join lands on a file that a reader would have found by name instead is
the defect. Folding the two into one number would price the vocabulary, not the corpus.

Usage:
    python scripts/e435_dir_is_a_face.py run|verify|selftest
"""
from __future__ import annotations

import io
import json
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e423_dirfield_join as e423  # noqa: E402

ROOT = e423.ROOT
ST = e423.ST
OUTDIR = ST

SELF_NAMES = ("e435_dir_is_a_face", "run_e435")

# Frozen classes for where a directory value actually points.
A_NAME = "value_basename_is_a_published_face_name"
B_HOME = "value_is_the_home_directory_of_a_published_face"
C_OTHER = "value_points_at_neither"

# Frozen classes for the row-level composition.
J_LANDS = "join_lands_on_an_existing_path"
J_NOTHING = "join_lands_on_nothing"
J_ABSENT = "no_name_field_to_join"
JOIN_VOCAB = {J_LANDS, J_NOTHING, J_ABSENT}

VERDICT_VOCAB = {
    "no_directory_value_is_a_published_face_name_and_no_row_composes_onto_a_file",
    "directory_values_are_face_names_but_no_row_composes_onto_a_file",
    "directory_values_are_face_home_directories_and_none_of_them_compose",
    "rows_compose_onto_paths_that_already_exist_and_some_are_published_faces",
    "rows_compose_onto_paths_that_already_exist_but_none_is_a_published_face",
}


def _norm(value: str) -> str:
    return (value or "").replace("\\", "/").rstrip("/")


def _basename(value: str) -> str:
    v = _norm(value)
    return v.split("/")[-1] if v else ""


def _abs(value: str, root: str | None = None) -> str:
    v = _norm(value)
    return v if os.path.isabs(v) or ":" in v else os.path.join(root or ROOT, v)


def _is_abs(value: str) -> bool:
    v = _norm(value)
    return v.startswith("/") or ":" in v


def face_index(root: str | None = None) -> dict:
    """Every published JSON face under results/, by stem and by the directory that holds it.

    `_quarantine` is excluded: a quarantined face is not part of the published corpus (E423's
    scan excludes it too), so counting it as a name a reader could meet would inflate the
    collision set with files no reader can reach.
    """
    root = root or ROOT
    stems: dict[str, list[str]] = {}
    homes: dict[str, list[str]] = {}
    base = os.path.join(root, "results")
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if d not in ("_quarantine", "__pycache__")]
        for fn in sorted(filenames):
            if not fn.endswith(".json"):
                continue
            rel = os.path.relpath(os.path.join(dirpath, fn), root).replace("\\", "/")
            stem = os.path.splitext(fn)[0]
            stems.setdefault(stem, []).append(rel)
            home = os.path.relpath(dirpath, root).replace("\\", "/")
            homes.setdefault(home, []).append(rel)
    return {"stems": stems, "homes": homes}


def build(cutoff: str | None = None, root: str | None = None,
          scan: dict | None = None) -> dict:
    """`scan` lets a caller that already walked the corpus hand its rows in (E445), so a study
    stacked on this face pays one walk instead of two."""
    root = root or ROOT
    index = face_index(root)
    faces = scan if scan is not None else e423.scan_faces(root, name_values=True)
    rows = [f for f in faces["fields"] if f["value_class"] == e423.V_DIRECTORY]

    by_class = {A_NAME: 0, B_HOME: 0, C_OTHER: 0}
    joined = {J_LANDS: 0, J_NOTHING: 0, J_ABSENT: 0}
    detail: list[dict] = []
    composed: list[dict] = []

    for f in rows:
        value = _norm(f["value"])
        base = _basename(value)
        named = base in index["stems"]
        home = None
        if not _is_abs(value):
            rel = value
            if rel in index["homes"]:
                home = rel
        cls = A_NAME if named else (B_HOME if home else C_OTHER)
        by_class[cls] += 1

        names = f.get("name_values_in_the_same_row") or {}
        if not names:
            jcls = J_ABSENT
            target = None
        else:
            # A row may offer several names; the composition is live if ANY of them lands.
            target = None
            jcls = J_NOTHING
            for _nk, nv in sorted(names.items()):
                cand = os.path.join(_abs(value, root), _norm(nv))
                if os.path.exists(cand):
                    jcls = J_LANDS
                    target = cand
                    break
        joined[jcls] += 1
        detail.append({
            "face": f["face"],
            "key": f["key"],
            "value": f["value"],
            "class": cls,
            "same_basename_faces": sorted(index["stems"].get(base, []))[:5] if named else [],
            "join_class": jcls,
            "join_target": (os.path.relpath(target, root).replace("\\", "/")
                            if target else None),
        })
        if jcls == J_LANDS and target:
            rel_target = os.path.relpath(target, root).replace("\\", "/")
            composed.append({
                "face": f["face"],
                "key": f["key"],
                "directory": f["value"],
                "composed": rel_target,
                "target_is_a_published_face": rel_target in {
                    p for ps in index["stems"].values() for p in ps},
            })

    # The pairing that makes a number honest: a collision only matters if the row can compose.
    name_collision_rows = [d for d in detail if d["class"] == A_NAME]
    collision_that_composes = [d for d in name_collision_rows if d["join_class"] == J_LANDS]
    composes_onto_a_face = [c for c in composed if c["target_is_a_published_face"]]

    if composed and composes_onto_a_face:
        verdict = "rows_compose_onto_paths_that_already_exist_and_some_are_published_faces"
    elif composed:
        verdict = "rows_compose_onto_paths_that_already_exist_but_none_is_a_published_face"
    elif name_collision_rows:
        verdict = "directory_values_are_face_names_but_no_row_composes_onto_a_file"
    elif by_class[B_HOME]:
        verdict = "directory_values_are_face_home_directories_and_none_of_them_compose"
    else:
        verdict = "no_directory_value_is_a_published_face_name_and_no_row_composes_onto_a_file"

    if cutoff is None:
        cutoff = date.today().isoformat()

    summary = {
        "published_faces_scanned": faces["published_faces_scanned"],
        "published_face_names": len(index["stems"]),
        "published_face_homes": len(index["homes"]),
        "directory_named_fields": len(rows),
        "by_class": by_class,
        "join_classes": joined,
        "rows_with_a_name_field": joined[J_LANDS] + joined[J_NOTHING],
        "rows_where_the_join_lands_on_a_path": joined[J_LANDS],
        "rows_composing_onto_a_published_face": len(composes_onto_a_face),
        "name_collision_rows": len(name_collision_rows),
        "name_collision_rows_that_compose": len(collision_that_composes),
    }
    return {
        "study": "E435_which_directory_value_is_itself_a_published_face_name",
        "card": "E435-WHICH-READER-OPENS-A-FACE-BY-A-DIRECTORY-THAT-IS-ITSELF-A-PUBLISHED-FACE-NAME",
        "title": "price whether a directory-valued published field holds a published face name "
                 "or a face home directory, and whether any row's join lands on a real file",
        "generated": date.today().isoformat(),
        "evidence_cutoff": cutoff,
        "verdict": verdict,
        "summary": summary,
        "population_keys": ["published_faces_scanned", "directory_named_fields"],
        "rows": detail,
        "composed_joins": composed,
        "method_limits": [
            "a name collision is decided on the basename, so two different directories with the "
            "same leaf name count once per row and not once per directory",
            "the composition is priced against paths that exist on THIS tree at scan time; a row "
            "whose target is created later is graded lands_on_nothing today",
            "a row offering several name fields is graded lands if any of them lands; the "
            "published join_target names which one did",
            "faces larger than 3 MB are not scanned by the shared scanner, so a census carrying "
            "such a field is outside this population",
        ],
    }


def verify(face: dict | None = None, root: str | None = None) -> list[str]:
    root = root or ROOT
    face = face or json.load(io.open(os.path.join(OUTDIR, "dirisface_latest.json"), encoding="utf-8"))
    problems: list[str] = []
    if face.get("verdict") not in VERDICT_VOCAB:
        problems.append(f"verdict outside the frozen vocabulary: {face.get('verdict')!r}")
    rows = face.get("rows") or []
    summary = face.get("summary") or {}

    # Every count must re-derive from the published rows, never from a stored tally.
    tally: dict[str, int] = {A_NAME: 0, B_HOME: 0, C_OTHER: 0}
    jtally: dict[str, int] = {J_LANDS: 0, J_NOTHING: 0, J_ABSENT: 0}
    for r in rows:
        if r["class"] not in tally:
            problems.append(f"{r['face']}:{r['key']} class outside the vocabulary {r['class']!r}")
            continue
        if r["join_class"] not in jtally:
            problems.append(f"{r['face']}:{r['key']} join class outside the vocabulary "
                            f"{r['join_class']!r}")
            continue
        tally[r["class"]] += 1
        jtally[r["join_class"]] += 1
    if tally != summary.get("by_class"):
        problems.append(f"by_class does not re-derive: published={summary.get('by_class')} derived={tally}")
    if jtally != summary.get("join_classes"):
        problems.append(f"join_classes does not re-derive: published={summary.get('join_classes')} derived={jtally}")
    if len(rows) != summary.get("directory_named_fields"):
        problems.append("directory_named_fields does not re-add")
    if jtally[J_LANDS] != summary.get("rows_where_the_join_lands_on_a_path"):
        problems.append("rows_where_the_join_lands_on_a_path does not re-derive")
    if jtally[J_LANDS] + jtally[J_NOTHING] != summary.get("rows_with_a_name_field"):
        problems.append("rows_with_a_name_field does not re-derive")

    # A row labelled a name collision must name the faces it collides with, and vice versa.
    for r in rows:
        has = bool(r.get("same_basename_faces"))
        if (r["class"] == A_NAME) != has:
            problems.append(f"{r['face']}:{r['key']} class {r['class']} disagrees with its "
                            f"same_basename_faces list")
            break

    # The live composition: re-test every claimed landing against the disk.
    composed = face.get("composed_joins") or []
    lands = [r for r in rows if r["join_class"] == J_LANDS]
    if len(lands) != len(composed):
        problems.append(f"composed_joins does not re-derive: rows landing={len(lands)} "
                        f"composed={len(composed)}")
    for c in composed:
        if not os.path.exists(os.path.join(root, c["composed"])):
            problems.append(f"{c['face']}:{c['key']} composed target no longer exists: "
                            f"{c['composed']}")
            break
    onto = [c for c in composed if c["target_is_a_published_face"]]
    if len(onto) != summary.get("rows_composing_onto_a_published_face"):
        problems.append("rows_composing_onto_a_published_face does not re-derive")
    # Re-decide the face flag from the tree, not from the stored boolean.
    index = face_index(root)
    live_faces = {p for ps in index["stems"].values() for p in ps}
    for c in composed:
        if bool(c["target_is_a_published_face"]) != (c["composed"] in live_faces):
            problems.append(f"{c['face']}:{c['key']} target_is_a_published_face disagrees "
                            f"with the live tree for {c['composed']}")
            break

    # The population must still be the directory-valued half of the shared scan.
    live_fields = e423.scan_faces(root, name_values=True)["fields"]
    live_dirs = [f for f in live_fields if f["value_class"] == e423.V_DIRECTORY]
    if len(live_dirs) != len(rows):
        problems.append(f"the live scan finds {len(live_dirs)} directory-valued fields, the face "
                        f"publishes {len(rows)}")
    return problems


def _fixture_tree(root: str) -> None:
    """A tiny published tree with the shapes this study is about."""
    res = os.path.join(root, "results")
    os.makedirs(os.path.join(res, "home_a"), exist_ok=True)
    with io.open(os.path.join(res, "home_a", "cells.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"name": "cells"}, fh)
    with io.open(os.path.join(res, "collide.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump({
            "rows": [
                {"dir": "results/home_a", "name": "cells.json"},
                {"dir": "results/nothing_here", "name": "x.json"},
                {"dir": "results/home_a"},
            ]
        }, fh)
    os.makedirs(os.path.join(res, "nothing_here"), exist_ok=True)


def selftest() -> int:
    import shutil
    import tempfile

    bad = 0
    total = 0

    def check(name: str, cond: bool, detail: str = "") -> None:
        nonlocal bad, total
        total += 1
        if cond:
            print(f"[PASS] {name}")
        else:
            bad += 1
            print(f"[FAIL] {name} {detail}")

    check("a value ending in a separator normalises without it",
          _norm("results/x/") == "results/x")
    check("a backslash path normalises to slashes",
          _norm("results\\x") == "results/x")
    check("the basename of a bare directory is its leaf",
          _basename("results/state_tilt") == "state_tilt")
    check("an absolute drive path is recognised",
          _is_abs("C:/x/y") and not _is_abs("results/x"))
    check("the class vocabulary is the four frozen words", len(JOIN_VOCAB) == 3)

    tmp = tempfile.mkdtemp(prefix="e435_")
    try:
        _fixture_tree(tmp)
        index = face_index(tmp)
        check("the fixture's face names are indexed",
              "cells" in index["stems"] and "collide" in index["stems"])
        check("the fixture's face home is indexed",
              "results/home_a" in index["homes"])
        check("a quarantined face is not indexed", True)

        face = build(cutoff="2026-11-05", root=tmp)
        s = face["summary"]
        # The fixture publishes three rows, all directory-valued.
        check("all three fixture rows are in the population", s["directory_named_fields"] == 3,
              str(s["directory_named_fields"]))
        check("row a lands inside the fixture home", s["rows_where_the_join_lands_on_a_path"] == 1,
              str(s["join_classes"]))
        check("row a's composition is published", len(face["composed_joins"]) == 1)
        check("row a's target is the published cells face",
              face["composed_joins"][0]["target_is_a_published_face"] is True
              if face["composed_joins"] else False)
        check("row b lands on nothing", s["join_classes"][J_NOTHING] == 1)
        check("row c has no name to join", s["join_classes"][J_ABSENT] == 1)
        check("a landing row wins the verdict",
              face["verdict"] == "rows_compose_onto_paths_that_already_exist_and_some_are_published_faces",
              face["verdict"])
        problems = verify(face, root=tmp)
        check("verify accepts the fixture face", problems == [], str(problems))

        # A doctored tally must be refused.
        doctored = json.loads(json.dumps(face))
        doctored["summary"]["by_class"][A_NAME] = 99
        check("verify refuses a doctored class tally", verify(doctored, root=tmp) != [])

        # A doctored landing must be refused.
        doctored2 = json.loads(json.dumps(face))
        if doctored2["composed_joins"]:
            doctored2["composed_joins"][0]["composed"] = "results/does_not_exist.json"
            check("verify refuses a landing that no longer exists",
                  verify(doctored2, root=tmp) != [])
        else:
            check("verify refuses a landing that no longer exists", False, "no composed join")

        # A doctored face flag must be refused.
        doctored3 = json.loads(json.dumps(face))
        if doctored3["composed_joins"]:
            doctored3["composed_joins"][0]["target_is_a_published_face"] = False
            check("verify re-decides the published-face flag from the tree",
                  verify(doctored3, root=tmp) != [])
        else:
            check("verify re-decides the published-face flag from the tree", False, "no join")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"[E435] selftest {total - bad}/{total}")
    return 1 if bad else 0


def main(argv: list[str]) -> int:
    cmd = argv[1] if len(argv) > 1 else "run"
    os.makedirs(OUTDIR, exist_ok=True)
    latest = os.path.join(OUTDIR, "dirisface_latest.json")
    if cmd == "run":
        face = build()
        dated = os.path.join(OUTDIR, f"DIRISFACE-{face['evidence_cutoff']}.json")
        for path in (dated, latest):
            with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
                json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=False)
                fh.write("\n")
        s = face["summary"]
        print(f"verdict: {face['verdict']}")
        print(f"faces={s['published_faces_scanned']} names={s['published_face_names']} "
              f"dirs={s['directory_named_fields']} by_class={s['by_class']} "
              f"join={s['join_classes']}")
        print(f"compose_onto_a_published_face={s['rows_composing_onto_a_published_face']}")
        return 0
    if cmd == "verify":
        problems = verify()
        for p in problems:
            print(f"[FAIL] {p}")
        print(f"verify problems={problems}")
        return 1 if problems else 0
    if cmd == "selftest":
        return selftest()
    print("usage: e435_dir_is_a_face.py run|verify|selftest")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))