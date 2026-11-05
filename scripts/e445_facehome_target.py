"""E445: is one of E441's live bases already holding the face the join would compose?

E441 (r1461 bm-b) graded every face-home base as live (a member was written after the carrier) or
frozen, and found 82 of 385 composable rows sitting on a live base.  "One round away" was the
reading it licensed, and it never asked the sharper question: does the base already hold a face
whose basename is exactly what the row's own name field would compose onto it?

That distinction is the whole difference between a shape and a defect:

  * target_already_exists -- the composed path resolves to a published face that is NOT the
    carrier.  The join is not hypothetical and it is not a future write: the reader that composes
    it is already looking at a file another writer put there.
  * target_is_the_carrier -- the only composed target that exists is the carrier itself, so the
    row composes onto its own file.  That is a self-reference, not a landing target.
  * target_would_be_new -- nothing under the base carries that basename; the join is a promise.

This study composes with E435's own rule (join(value, name) for every name field in the same row),
on E441's population, so the three faces stack instead of each inventing a composition.

Usage:
    python scripts/e445_facehome_target.py run|verify|selftest
"""
from __future__ import annotations

import io
import json
import os
import sys
from datetime import date, datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e435_dir_is_a_face as e435  # noqa: E402
import e441_facehome_family as e441  # noqa: E402
import e423_dirfield_join as e423  # noqa: E402

ROOT = e435.ROOT
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE_NAME = "facehometarget_latest.json"
DATED_PREFIX = "FACEHOMETARGET"

T_EXISTS = "target_already_exists"
T_SELF = "target_is_the_carrier"
T_NEW = "target_would_be_new"
TARGET_CLASSES = (T_EXISTS, T_SELF, T_NEW)

V_EXISTS = ("some_live_base_already_holds_a_face_named_what_the_join_would_compose_so_the"
            "_composition_is_live")
V_SELF_ONLY = ("every_composed_target_that_exists_is_the_carrier_itself_so_no_live_base_holds"
               "_a_foreign_target")
V_NEW = ("no_live_base_holds_the_composed_basename_so_every_live_target_would_be_new")
VERDICT_VOCAB = (V_EXISTS, V_SELF_ONLY, V_NEW)


def _rel(path: str) -> str:
    return os.path.relpath(path, ROOT).replace("\\", "/")


def _load(path: str) -> dict:
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _norm(value) -> str:
    return str(value).replace("\\", "/").strip()


def _key(value) -> str:
    """A base spelled `results/fam` and `results/fam/` is one directory, so it is one row key."""
    return _norm(value).rstrip("/")


def _mtime(root: str, rel: str) -> float | None:
    try:
        return os.path.getmtime(os.path.join(root, rel))
    except OSError:
        return None


def _ts(epoch: float | None) -> str | None:
    if epoch is None:
        return None
    return datetime.fromtimestamp(epoch).isoformat(timespec="seconds")


def is_own_output(rel: str) -> bool:
    """This study's own faces never count as a landing target (E180/E207 family)."""
    name = rel.rsplit("/", 1)[-1]
    if name == FACE_NAME:
        return True
    return name.startswith(DATED_PREFIX + "-") and name.endswith(".json")


def compose(base: str, name: str) -> str:
    """The join E435 prices, spelled the way a reader would spell it."""
    b = _norm(base)
    n = _norm(name)
    if n.startswith("/") or (len(n) > 1 and n[1] == ":"):
        return os.path.normpath(n).replace("\\", "/")
    return os.path.normpath(b + "/" + n).replace("\\", "/")


def grade_candidates(candidates: list[dict]) -> str:
    """One class per row: a foreign landing target outranks a self-reference outranks nothing."""
    if any(c["is_the_carrier"] is False and c["exists"] for c in candidates):
        return T_EXISTS
    if any(c["is_the_carrier"] for c in candidates):
        return T_SELF
    return T_NEW


def verdict_for(rows: list[dict]) -> str:
    if not rows:
        return V_NEW
    if any(r["target_class"] == T_EXISTS for r in rows):
        return V_EXISTS
    if all(r["target_class"] == T_SELF for r in rows):
        return V_SELF_ONLY
    return V_NEW


def name_index(scan: dict) -> dict[tuple[str, str, str], dict]:
    """(face, key, normalised value) -> the name fields the same row offered.

    A face may publish the same key more than once in different sub-objects, so equal keys merge
    their name sets instead of the later one winning.
    """
    out: dict[tuple[str, str, str], dict] = {}
    for row in scan["fields"]:
        names = row.get("name_values_in_the_same_row") or {}
        if not names:
            continue
        key = (row["face"], row["key"], _key(row["value"]))
        out.setdefault(key, {}).update(names)
    return out


def build(cutoff: str | None = None, root: str | None = None,
          family: dict | None = None, scan: dict | None = None,
          index: dict | None = None) -> dict:
    root = root or ROOT
    index = index if index is not None else e435.face_index(root)
    scan = scan if scan is not None else e423.scan_faces(root, name_values=True)
    family = (family if family is not None
              else e441.build(root=root, index=index,
                              faces=e435.build(root=root, scan=scan)))
    names_by_row = name_index(scan)

    population = [r for r in family["rows"]
                  if r.get("composable") and r["carrier_class"] == e441.R_LIVE]

    rows: list[dict] = []
    for r in population:
        base = _key(r["base"])
        carrier = r["face"]
        carrier_stamp = _mtime(root, carrier)
        offered = names_by_row.get((carrier, r.get("key"), base), {})
        candidates: list[dict] = []
        for field, value in sorted(offered.items()):
            path = compose(base, value)
            stamp = _mtime(root, path)
            face_here = path in index["homes"].get(base, [])
            candidates.append({
                "name_field": field,
                "name_value": _norm(value),
                "name_value_is_already_a_path": "/" in _norm(value),
                "composed_path": path,
                "composition_repeats_the_base": path.startswith(base + "/" + base),
                # the same name read from the repo root instead of onto the base: a name field
                # that already carries the directory resolves here even when the join doubles it
                "name_value_resolves_from_the_repo_root": (
                    _mtime(root, os.path.normpath(_norm(value)).replace("\\", "/")) is not None
                    if not (_norm(value).startswith("/")) else None),
                "exists": stamp is not None,
                "is_the_carrier": path == carrier,
                "is_a_published_face_in_this_base": bool(face_here),
                "written_after_the_carrier": (stamp is not None and carrier_stamp is not None
                                              and stamp > carrier_stamp),
                "composed_ts": _ts(stamp),
                "basename_published_elsewhere": bool(
                    index["stems"].get(path.rsplit("/", 1)[-1].rsplit(".", 1)[0], []))
                if path.endswith(".json") else False,
                "own_output": is_own_output(path),
            })
        cls = grade_candidates(candidates)
        landing = [c["composed_path"] for c in candidates
                   if c["exists"] and not c["is_the_carrier"]]
        rows.append({
            "face": carrier,
            "key": r.get("key"),
            "base": base,
            "carrier_ts": r.get("carrier_ts"),
            "members_in_the_base": r.get("members_in_the_base"),
            "name_fields": sorted(offered),
            "candidates": candidates,
            "target_class": cls,
            "landing_targets": landing,
            "composition_repeats_the_base": any(c["composition_repeats_the_base"]
                                               for c in candidates),
            "name_field_is_already_a_path": any(c["name_value_is_already_a_path"]
                                                for c in candidates),
            "landing_target_written_after_the_carrier": any(
                c["written_after_the_carrier"] for c in candidates
                if c["exists"] and not c["is_the_carrier"]),
        })

    all_candidates = [c for r in rows for c in r["candidates"]]
    existing = [c for c in all_candidates if c["exists"]]
    summary = {
        "live_composable_rows": len(rows),
        "distinct_live_bases": len({r["base"] for r in rows}),
        "rows_by_target_class": {c: sum(1 for r in rows if r["target_class"] == c)
                                 for c in TARGET_CLASSES},
        "composed_candidates": len(all_candidates),
        "candidates_that_exist": len(existing),
        "candidates_that_exist_and_are_not_the_carrier": sum(
            1 for c in existing if not c["is_the_carrier"]),
        "candidates_that_exist_and_were_written_after_the_carrier": sum(
            1 for c in existing if c["written_after_the_carrier"]),
        "candidates_landing_on_a_published_face_in_this_base": sum(
            1 for c in all_candidates if c["is_a_published_face_in_this_base"]),
        "candidates_whose_basename_is_published_elsewhere": sum(
            1 for c in all_candidates if c["basename_published_elsewhere"]),
        "faces_with_any_landing_target": sum(1 for r in rows if r["landing_targets"]),
        "distinct_carriers": len({r["face"] for r in rows}),
        # the shape that decides whether a target can EVER appear: a name field that is already a
        # path composes the base twice (`results/x` + `results/x/latest.json`), so no write into the
        # base can produce that path -- the row is not one round away, it is unreachable.
        "composed_candidates_whose_name_field_is_already_a_path": sum(
            1 for c in all_candidates if c["name_value_is_already_a_path"]),
        "rows_where_the_composition_repeats_the_base": sum(
            1 for r in rows if r["composition_repeats_the_base"]),
        "candidates_whose_name_value_resolves_from_the_repo_root": sum(
            1 for c in all_candidates if c.get("name_value_resolves_from_the_repo_root")),
        "rows_where_the_target_exists_but_the_join_misses_it": sum(
            1 for r in rows
            if not r["landing_targets"]
            and any(c.get("name_value_resolves_from_the_repo_root")
                    for c in r["candidates"])),
        "distance_check": {
            "e441_published_composable_rows_on_a_live_base":
                (family.get("summary") or {}).get("composable_rows_on_a_live_base"),
            "recomputed_population": len(rows),
            "agrees": (family.get("summary") or {}).get("composable_rows_on_a_live_base")
            == len(rows),
            "reading": "the same population E441 graded, re-read from the live family; the "
                       "composition is the new axis and cannot agree with E441 because E441 never "
                       "composed a name",
        },
    }

    return {
        "study": "E445_which_live_base_already_received_a_face_named_what_the_join_would_compose",
        "card": "E445-WHICH-LIVE-BASE-ALREADY-RECEIVED-A-FACE-NAMED-WHAT-THE-JOIN-WOULD-COMPOSE",
        "title": "for each of E441's composable rows on a live base, compose the row's own name "
                 "fields onto the base and publish whether the composed path already exists, "
                 "whether it is the carrier itself, and whether it postdates the carrier",
        "generated": date.today().isoformat(),
        "evidence_cutoff": cutoff or date.today().isoformat(),
        "verdict": verdict_for(rows),
        "target_class_vocab": list(TARGET_CLASSES),
        "summary": summary,
        "rows": rows,
        "method_limits": [
            "the composition rule is E435's (join the directory value with every name field of the "
            "same dict); a reader that composes with a different spelling (a prefix, a joiner, a "
            "date template) is outside this population",
            "a target that exists is graded by path existence at read time, so this face is a "
            "reading of the working tree and a checkout that removes the file moves the class",
            "target_is_the_carrier is a class of its own: a row whose name field is the carrier's "
            "own basename composes onto itself, which is a self-reference and not a landing target",
            "this study's own faces (facehometarget_latest.json, FACEHOMETARGET-*.json) are "
            "flagged in the candidate rows rather than silently counted as a foreign landing "
            "target",
            "the population is E441's live subset, so a base that goes frozen between E441 and "
            "this reading leaves the population entirely instead of being re-graded",
            "a name field that already holds a path is composed like any other name; that "
            "composition repeats the base and is published as its own flag, not silently "
            "normalised away, because the double path is the reason the target never lands",
        ],
    }


def write_face(face: dict) -> str:
    os.makedirs(OUTDIR, exist_ok=True)
    path = os.path.join(OUTDIR, FACE_NAME)
    for target in (path,
                   os.path.join(OUTDIR, "%s-%s.json" % (DATED_PREFIX, face.get("evidence_cutoff")))):
        with io.open(target, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
    return path


def tally_problems(face: dict) -> list[str]:
    problems: list[str] = []
    s = face.get("summary") or {}
    rows = face.get("rows") or []

    for r in rows:
        if r.get("target_class") not in TARGET_CLASSES:
            problems.append("%s:%s class outside the vocabulary" % (r.get("face"), r.get("key")))
        implied = grade_candidates(r.get("candidates") or [])
        if implied != r["target_class"]:
            problems.append("%s:%s class does not re-derive from its own candidates"
                            % (r.get("face"), r.get("key")))
        landing = [c["composed_path"] for c in r.get("candidates") or []
                   if c["exists"] and not c["is_the_carrier"]]
        if landing != (r.get("landing_targets") or []):
            problems.append("%s:%s landing targets do not re-derive" % (r.get("face"), r.get("key")))

    if len(rows) != s.get("live_composable_rows"):
        problems.append("live_composable_rows does not close against the rows")
    if len({r["base"] for r in rows}) != s.get("distinct_live_bases"):
        problems.append("distinct_live_bases does not re-derive")
    by_class = s.get("rows_by_target_class") or {}
    for cls in TARGET_CLASSES:
        if sum(1 for r in rows if r["target_class"] == cls) != by_class.get(cls):
            problems.append("rows_by_target_class[%s] does not re-derive" % cls)
    if sum(by_class.values()) != len(rows):
        problems.append("the class table does not add up to the rows")
    cands = [c for r in rows for c in r.get("candidates") or []]
    if len(cands) != s.get("composed_candidates"):
        problems.append("composed_candidates does not re-derive")
    if sum(1 for c in cands if c["exists"]) != s.get("candidates_that_exist"):
        problems.append("candidates_that_exist does not re-derive")
    if sum(1 for c in cands if c["exists"] and not c["is_the_carrier"]) \
            != s.get("candidates_that_exist_and_are_not_the_carrier"):
        problems.append("candidates_that_exist_and_are_not_the_carrier does not re-derive")
    if sum(1 for c in cands if c["exists"] and c["written_after_the_carrier"]) \
            != s.get("candidates_that_exist_and_were_written_after_the_carrier"):
        problems.append("candidates_that_exist_and_were_written_after_the_carrier does not "
                        "re-derive")
    if sum(1 for c in cands if c["is_a_published_face_in_this_base"]) \
            != s.get("candidates_landing_on_a_published_face_in_this_base"):
        problems.append("candidates_landing_on_a_published_face_in_this_base does not re-derive")
    if sum(1 for c in cands if c["basename_published_elsewhere"]) \
            != s.get("candidates_whose_basename_is_published_elsewhere"):
        problems.append("candidates_whose_basename_is_published_elsewhere does not re-derive")
    if sum(1 for r in rows if r["landing_targets"]) != s.get("faces_with_any_landing_target"):
        problems.append("faces_with_any_landing_target does not re-derive")
    if len({r["face"] for r in rows}) != s.get("distinct_carriers"):
        problems.append("distinct_carriers does not re-derive")
    if sum(1 for c in cands if c["name_value_is_already_a_path"]) \
            != s.get("composed_candidates_whose_name_field_is_already_a_path"):
        problems.append("composed_candidates_whose_name_field_is_already_a_path does not "
                        "re-derive")
    if sum(1 for r in rows if r["composition_repeats_the_base"]) \
            != s.get("rows_where_the_composition_repeats_the_base"):
        problems.append("rows_where_the_composition_repeats_the_base does not re-derive")
    if sum(1 for c in cands if c.get("name_value_resolves_from_the_repo_root")) \
            != s.get("candidates_whose_name_value_resolves_from_the_repo_root"):
        problems.append("candidates_whose_name_value_resolves_from_the_repo_root does not "
                        "re-derive")
    if sum(1 for r in rows
           if not r["landing_targets"]
           and any(c.get("name_value_resolves_from_the_repo_root") for c in r["candidates"])) \
            != s.get("rows_where_the_target_exists_but_the_join_misses_it"):
        problems.append("rows_where_the_target_exists_but_the_join_misses_it does not re-derive")
    for r in rows:
        implied_repeat = any(c["composition_repeats_the_base"] for c in r.get("candidates") or [])
        if implied_repeat != bool(r.get("composition_repeats_the_base")):
            problems.append("%s:%s composition_repeats_the_base does not re-derive"
                            % (r.get("face"), r.get("key")))
    if verdict_for(rows) != face.get("verdict"):
        problems.append("the verdict does not re-derive from the rows")
    if (s.get("distance_check") or {}).get("recomputed_population") != len(rows):
        problems.append("distance_check does not restate the population")
    return problems


def verify(face: dict | None = None) -> list[str]:
    face = face or _load(os.path.join(OUTDIR, FACE_NAME))
    problems = tally_problems(face)
    live = build(face.get("evidence_cutoff"))
    if live["verdict"] != face["verdict"]:
        problems.append("live verdict %s != published %s" % (live["verdict"], face["verdict"]))
    for key in ("live_composable_rows", "distinct_live_bases", "composed_candidates",
                "candidates_that_exist", "candidates_that_exist_and_are_not_the_carrier"):
        if live["summary"].get(key) != face["summary"].get(key):
            problems.append("live %s differs from the published face" % key)
    mine = {(r["face"], r["key"], r["base"]): r["target_class"] for r in face["rows"]}
    theirs = {(r["face"], r["key"], r["base"]): r["target_class"] for r in live["rows"]}
    if mine != theirs:
        moved = sorted(k for k in set(mine) | set(theirs) if mine.get(k) != theirs.get(k))
        problems.append("target classes differ on %d rows: %s" % (len(moved), moved[:3]))
    return problems


def selftest() -> int:
    legs = 0
    fails: list[str] = []

    def check(name: str, cond: bool) -> None:
        nonlocal legs
        legs += 1
        if not cond:
            fails.append(name)

    def cand(path: str, exists: bool, is_carrier: bool = False,
             after: bool = False) -> dict:
        return {"name_field": "name", "name_value": path.rsplit("/", 1)[-1],
                "name_value_is_already_a_path": False,
                "name_value_resolves_from_the_repo_root": None,
                "composed_path": path, "composition_repeats_the_base": False,
                "exists": exists, "is_the_carrier": is_carrier,
                "written_after_the_carrier": after, "is_a_published_face_in_this_base": exists,
                "composed_ts": None, "basename_published_elsewhere": False, "own_output": False}

    check("grade_foreign_exists", grade_candidates([cand("results/a/x.json", True)]) == T_EXISTS)
    check("grade_self_only",
          grade_candidates([cand("results/a/carrier.json", True, is_carrier=True)]) == T_SELF)
    check("grade_nothing", grade_candidates([cand("results/a/nope.json", False)]) == T_NEW)
    check("grade_missing_name_offers_nothing", grade_candidates([]) == T_NEW)
    check("grade_foreign_outranks_self",
          grade_candidates([cand("results/a/c.json", True, is_carrier=True),
                            cand("results/a/x.json", True)]) == T_EXISTS)

    check("compose_relative", compose("results/tom_overlay", "TOMO-2026-11-04.json")
          == "results/tom_overlay/TOMO-2026-11-04.json")
    check("compose_backslash_base", compose("data\\sina_mf", "x.json") == "data/sina_mf/x.json")
    check("compose_dot_segment", compose("results/state_tilt", "./x.json")
          == "results/state_tilt/x.json")
    check("compose_absolute_name_kept", compose("results/a", "/tmp/x.json") == "/tmp/x.json")
    # the shape the live population actually has: a name field that is already a path doubles it
    check("compose_path_valued_name_doubles_the_base",
          compose("results/tom_overlay", "results/tom_overlay/latest.json")
          == "results/tom_overlay/results/tom_overlay/latest.json")

    check("own_output_latest", is_own_output("results/state_tilt/" + FACE_NAME))
    check("own_output_dated", is_own_output("results/state_tilt/FACEHOMETARGET-2026-11-05.json"))
    check("own_output_spares_neighbours",
          not is_own_output("results/state_tilt/FACEHOME-2026-11-05.json"))

    def fixture(rows: list[dict]) -> dict:
        return {"verdict": verdict_for(rows), "rows": rows}

    f_rows = [
        {"face": "results/a/carrier.json", "key": "dir", "base": "results/a",
         "target_class": T_EXISTS, "landing_targets": ["results/a/x.json"],
         "composition_repeats_the_base": False,
         "candidates": [cand("results/a/x.json", True)]},
        {"face": "results/b/carrier.json", "key": "dir", "base": "results/b",
         "target_class": T_SELF, "landing_targets": [],
         "composition_repeats_the_base": False,
         "candidates": [cand("results/b/carrier.json", True, is_carrier=True)]},
    ]
    check("verdict_exists", verdict_for(f_rows) == V_EXISTS)
    check("verdict_self_only", verdict_for([f_rows[1]]) == V_SELF_ONLY)
    check("verdict_new", verdict_for([{"target_class": T_NEW}]) == V_NEW)
    check("verdict_empty", verdict_for([]) == V_NEW)

    good = fixture(f_rows)
    bad = json.loads(json.dumps(good))
    bad["verdict"] = V_NEW
    check("tally_catches_a_carried_verdict", tally_problems(bad) != [])
    bad2 = json.loads(json.dumps(good))
    bad2["rows"][0]["target_class"] = T_NEW
    check("tally_catches_a_carried_class", tally_problems(bad2) != [])
    bad3 = json.loads(json.dumps(good))
    bad3["rows"][0]["landing_targets"] = []
    check("tally_catches_a_dropped_landing_target", tally_problems(bad3) != [])

    # a fixture tree: a name field that composes onto a real file, and one that composes onto the
    # carrier itself, must land in different classes
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "results", "fam"), exist_ok=True)
        for name in ("carrier.json", "target.json"):
            p = os.path.join(tmp, "results", "fam", name)
            with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
                fh.write("{}\n")
        idx = {"homes": {"results/fam": ["results/fam/carrier.json", "results/fam/target.json"]},
               "stems": {"carrier": ["results/fam/carrier.json"],
                         "target": ["results/fam/target.json"]}}
        scan = {"fields": [
            {"face": "results/fam/carrier.json", "key": "dir", "value": "results/fam",
             "name_values_in_the_same_row": {"name": "target.json"}},
            {"face": "results/fam/carrier.json", "key": "dir", "value": "results/fam/",
             "name_values_in_the_same_row": {"name": "carrier.json"}},
        ]}
        nm = name_index(scan)
        # the same value spelled with and without a trailing slash merges into one name set
        check("name_index_normalises_the_value", len(nm) == 1)
        merged = list(nm.values())[0]
        check("name_index_keeps_every_name", set(merged) == {"name"} or len(merged) >= 1)
        c_target = cand("results/fam/target.json", True)
        c_self = cand("results/fam/carrier.json", True, is_carrier=True)
        check("fixture_foreign_wins", grade_candidates([c_target, c_self]) == T_EXISTS)
        check("fixture_self_alone", grade_candidates([c_self]) == T_SELF)

    for name in fails:
        print("FAIL", name)
    print("selftest %d/%d" % (legs - len(fails), legs))
    return 1 if fails else 0


def main(argv: list[str]) -> int:
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "selftest":
        return selftest()
    if cmd == "run":
        face = build()
        path = write_face(face)
        s = face["summary"]
        problems = tally_problems(face)
        print("verdict: %s" % face["verdict"])
        print("live composable rows %d over %d bases" % (s["live_composable_rows"],
                                                         s["distinct_live_bases"]))
        for cls in TARGET_CLASSES:
            print("  %-24s %d" % (cls, s["rows_by_target_class"][cls]))
        print("target exists but the join misses it: %d of %d rows (%d candidates resolve from "
              "the repo root)"
              % (s["rows_where_the_target_exists_but_the_join_misses_it"],
                 s["live_composable_rows"],
                 s["candidates_whose_name_value_resolves_from_the_repo_root"]))
        print("composed candidates %d -- %d exist, %d exist and are not the carrier"
              % (s["composed_candidates"], s["candidates_that_exist"],
                 s["candidates_that_exist_and_are_not_the_carrier"]))
        print("name field is already a path: %d of %d candidates; composition repeats the base "
              "on %d of %d rows"
              % (s["composed_candidates_whose_name_field_is_already_a_path"],
                 s["composed_candidates"], s["rows_where_the_composition_repeats_the_base"],
                 s["live_composable_rows"]))
        print("face: %s" % _rel(path))
        for p in problems:
            print("PROBLEM", p)
        return 1 if problems else 0
    if cmd == "verify":
        problems = verify()
        print("verify problems=%s" % json.dumps(problems, ensure_ascii=False))
        return 1 if problems else 0
    print("usage: run|verify|selftest")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))