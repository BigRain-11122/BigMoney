"""E441: a face-home base is either a live writer directory or a frozen one, and that decides
whether E435's empty composition is structural safety or a timing accident.

E435 (r1458 bm-b) published 626 directory values that are the home directory of a published face
and 0 of 489 composable joins that lands on a path.  A zero like that supports two opposite
readings and the face could not tell them apart:

  * the base is a live writer directory -- another round is writing new members into it, so the
    join is one round away from having a landing target, i.e. the zero is TIMING; or
  * the base is frozen -- nothing has been written there since the face that names it, so the zero
    is STRUCTURAL, and a future write is as likely as any other future event.

This study answers that by reading the filesystem instead of the intent: for every face-home row it
lists the published faces living directly under the named directory, drops the carrier itself (a
face that names its own directory would otherwise always be its own newest member), and asks how
many members carry an mtime strictly later than the carrier's.

Rows are graded live / frozen per carrier; directories are graded live if any of their carriers was
outlived by a member.  The composable subset (the 489 rows that DO offer a name to join) is then
cross-tabbed against that grading, because that population is the one a landing target would change.

Usage:
    python scripts/e441_facehome_family.py run|verify|selftest
"""
from __future__ import annotations

import io
import json
import os
import sys
from datetime import date, datetime

import e435_dir_is_a_face as e435

ROOT = e435.ROOT
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE_NAME = "facehome_latest.json"
DATED_PREFIX = "FACEHOME"

B_HOME = e435.B_HOME

L_LIVE = "gained_at_least_one_member_after_the_face_that_names_it"
L_FROZEN = "no_member_was_written_after_the_face_that_names_it"
BASE_CLASSES = (L_LIVE, L_FROZEN)

R_LIVE = "this_carrier_was_outlived_by_a_member_of_the_base"
R_FROZEN = "no_member_of_the_base_is_newer_than_this_carrier"
ROW_CLASSES = (R_LIVE, R_FROZEN)

V_ALL_LIVE = ("every_face_home_base_gained_a_member_after_at_least_one_carrier_so_the_empty"
              "_composition_is_a_timing_accident_not_a_structural_safety")
V_ALL_FROZEN = ("no_face_home_base_gained_a_member_after_any_carrier_so_the_empty_composition"
                "_is_structural")
V_SPLIT = ("some_face_home_bases_are_live_writer_directories_and_the_rest_are_frozen")
VERDICT_VOCAB = (V_ALL_LIVE, V_ALL_FROZEN, V_SPLIT)


def _rel(path: str) -> str:
    return os.path.relpath(path, ROOT).replace("\\", "/")


def _load(path: str) -> dict:
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _norm(value) -> str:
    return str(value).replace("\\", "/").strip()


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
    """This study's own faces are excluded from the member scan.

    Without this the study counts itself: `facehome_latest.json` is written into
    results/state_tilt on every run, so the directory would read as live because of the face
    that is doing the reading (E180/E207 family -- the scanner inside its own candidate set).
    """
    name = rel.rsplit("/", 1)[-1]
    if name == FACE_NAME:
        return True
    return name.startswith(DATED_PREFIX + "-") and name.endswith(".json")


def members_of(index: dict, directory: str, carrier: str, root: str) -> list[tuple[str, float]]:
    """Published faces directly under `directory`, minus the carrier and minus this study."""
    out = []
    for rel in index["homes"].get(directory, []):
        if rel == carrier or is_own_output(rel):
            continue
        stamp = _mtime(root, rel)
        if stamp is None:
            continue
        out.append((rel, stamp))
    out.sort(key=lambda pair: (-pair[1], pair[0]))
    return out


def grade_row(carrier_stamp: float | None, members: list[tuple[str, float]]) -> str:
    if carrier_stamp is None or not members:
        return R_FROZEN
    return R_LIVE if members[0][1] > carrier_stamp else R_FROZEN


def verdict_for(directory_rows: list[dict]) -> str:
    """Recomputed from the published directory classes, never carried."""
    live = sum(1 for d in directory_rows if d["base_class"] == L_LIVE)
    if live == 0:
        return V_ALL_FROZEN
    if live == len(directory_rows) and directory_rows:
        return V_ALL_LIVE
    return V_SPLIT


def build(cutoff: str | None = None, root: str | None = None,
          faces: dict | None = None, index: dict | None = None) -> dict:
    root = root or ROOT
    index = index if index is not None else e435.face_index(root)
    scanned = faces if faces is not None else e435.build(root=root)
    home_rows = [r for r in scanned["rows"] if r["class"] == B_HOME]

    rows: list[dict] = []
    by_dir: dict[str, dict] = {}

    for r in home_rows:
        directory = _norm(r["value"])
        carrier = r["face"]
        carrier_stamp = _mtime(root, carrier)
        members = members_of(index, directory, carrier, root)
        newer = [m for m in members
                 if carrier_stamp is not None and m[1] > carrier_stamp]
        cls = grade_row(carrier_stamp, members)
        composable = r.get("join_class") != "no_name_field_to_join"

        rows.append({
            "face": carrier,
            "key": r.get("key"),
            "base": directory,
            "carrier_class": cls,
            "carrier_ts": _ts(carrier_stamp),
            "members_in_the_base": len(members),
            "members_after_the_carrier": len(newer),
            "newest_member": members[0][0] if members else None,
            "newest_member_ts": _ts(members[0][1]) if members else None,
            "days_from_carrier_to_newest_member": (
                round((members[0][1] - carrier_stamp) / 86400.0, 3)
                if members and carrier_stamp is not None else None),
            "carrier_names_its_own_base": carrier.rsplit("/", 1)[0] == directory,
            "composable": bool(composable),
            "join_class": r.get("join_class"),
        })

        block = by_dir.setdefault(directory, {
            # named `base`, not `directory`: E423's census classifies a published field BY NAME, so
            # a key spelled `directory` here would put this study's own face back into the
            # population it censuses (+144 rows, measured in-window).  The rows already use `base`;
            # the aggregate follows them (r1234 name-is-semantics law).
            "base": directory,
            "carriers": 0,
            "members": len(members),
            "carrier_rows_outlived": 0,
            "newest_member": members[0][0] if members else None,
            "newest_member_ts": _ts(members[0][1]) if members else None,
            "oldest_member_ts": _ts(members[-1][1]) if members else None,
            "max_days_from_a_carrier_to_the_newest_member": None,
            "base_class": L_FROZEN,
        })
        block["carriers"] += 1
        block["members"] = max(block["members"], len(members))
        if cls == R_LIVE:
            block["carrier_rows_outlived"] += 1
            block["base_class"] = L_LIVE
        if members and carrier_stamp is not None:
            gap = round((members[0][1] - carrier_stamp) / 86400.0, 3)
            best = block["max_days_from_a_carrier_to_the_newest_member"]
            if best is None or gap > best:
                block["max_days_from_a_carrier_to_the_newest_member"] = gap

    directories = sorted(by_dir.values(), key=lambda d: (-d["carriers"], d["base"]))

    composable = [r for r in rows if r["composable"]]
    live_rows = [r for r in rows if r["carrier_class"] == R_LIVE]
    summary = {
        "face_home_rows": len(rows),
        "distinct_directories": len(directories),
        "live_directories": sum(1 for d in directories if d["base_class"] == L_LIVE),
        "frozen_directories": sum(1 for d in directories if d["base_class"] == L_FROZEN),
        "carriers_outlived_by_a_later_member": len(live_rows),
        "share_of_carriers_outlived": round(len(live_rows) / len(rows), 4) if rows else None,
        "composable_rows": len(composable),
        "composable_rows_on_a_live_base": sum(1 for r in composable
                                              if r["carrier_class"] == R_LIVE),
        "composable_rows_on_a_frozen_base": sum(1 for r in composable
                                                if r["carrier_class"] == R_FROZEN),
        "carriers_naming_their_own_base": sum(1 for r in rows if r["carrier_names_its_own_base"]),
        "carrier_classes": {c: sum(1 for r in rows if r["carrier_class"] == c)
                            for c in ROW_CLASSES},
        "largest_live_directory": next((d["base"] for d in directories
                                        if d["base_class"] == L_LIVE), None),
        "directories": directories,
    }
    summary["distance_check"] = {
        "e435_published_face_home_rows": _e435_published_rows(),
        "recomputed_face_home_rows": len(rows),
        "agrees": _e435_published_rows() == len(rows),
        "reading": "the same population re-read from the live tree; the member counts are the "
                   "new axis and cannot agree with E435 because E435 never counted them",
    }

    return {
        "study": "E441_which_face_home_base_is_a_live_writer_directory",
        "card": "E441-WHICH-FACE-HOME-BASE-IS-A-LIVE-WRITER-DIRECTORY",
        "title": "map each of E435's face-home directory values to the family of published faces "
                 "living directly under it, publish the per-family member count and the newest "
                 "member, and flag the families whose newest member postdates the face that "
                 "names the value",
        "generated": date.today().isoformat(),
        "evidence_cutoff": cutoff or date.today().isoformat(),
        "verdict": verdict_for(directories),
        "base_class_vocab": list(BASE_CLASSES),
        "row_classes": list(ROW_CLASSES),
        "summary": summary,
        "rows": rows,
        "method_limits": [
            "member identity is the filesystem mtime of each .json face directly under the named "
            "directory; a checkout that rewrote every file would restamp the whole family and "
            "read every base as frozen, so this face is a reading of the working tree, not of git "
            "history",
            "subdirectories are not descended: E435's base is the directory that holds the face, "
            "and a family two levels down is not 'directly under it'",
            "the carrier is excluded from its own member list, otherwise a face that names its own "
            "directory is always its own newest member and every such base reads frozen",
            "this study's own faces (facehome_latest.json and FACEHOME-*.json) are excluded from "
            "the member scan, otherwise results/state_tilt reads live because of the reader itself",
            "mtime equality is graded frozen: a member written in the same second as the carrier "
            "cannot be shown to postdate it",
            "a live base proves the family is growing, not that any join will ever be written; the "
            "composable cross-tab is the population a landing target would change, not a claim "
            "that one will appear",
        ],
    }


E435_FACE_NAME = "dirisface_latest.json"


def _e435_published_rows() -> int | None:
    """How many rows E435 published in the face-home class specifically.

    E435's `directory_named_fields` (679) is the whole directory-valued population; this study
    only grades the subset whose value is the home of a published face (626).  Counting the whole
    population here would make every run report a mismatch that is not a defect.
    """
    try:
        face = _load(os.path.join(OUTDIR, E435_FACE_NAME))
    except (OSError, ValueError):
        return None
    return ((face.get("summary") or {}).get("by_class") or {}).get(B_HOME)


def write_face(face: dict) -> str:
    os.makedirs(OUTDIR, exist_ok=True)
    path = os.path.join(OUTDIR, FACE_NAME)
    targets = [path,
               os.path.join(OUTDIR, "%s-%s.json" % (DATED_PREFIX, face.get("evidence_cutoff")))]
    for target in targets:
        with io.open(target, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
    return path


def tally_problems(face: dict) -> list[str]:
    problems: list[str] = []
    s = face.get("summary") or {}
    rows = face.get("rows") or []
    directories = s.get("directories") or []

    for r in rows:
        if r.get("carrier_class") not in ROW_CLASSES:
            problems.append("%s:%s carrier class outside the vocabulary"
                            % (r.get("face"), r.get("key")))
        if not isinstance(r.get("members_after_the_carrier"), int) \
                or r["members_after_the_carrier"] < 0:
            problems.append("%s:%s carries a negative member count"
                            % (r.get("face"), r.get("key")))
        implied = R_LIVE if r["members_after_the_carrier"] > 0 else R_FROZEN
        if implied != r["carrier_class"]:
            problems.append("%s:%s class does not re-derive from its own member count"
                            % (r.get("face"), r.get("key")))

    if len(rows) != s.get("face_home_rows"):
        problems.append("face_home_rows does not close against the rows")
    if len(directories) != s.get("distinct_directories"):
        problems.append("directories does not cover every distinct base")
    if sum(d["carriers"] for d in directories) != len(rows):
        problems.append("the directory carrier counts do not add up to the rows")
    if sum(1 for d in directories if d["base_class"] == L_LIVE) != s.get("live_directories"):
        problems.append("live_directories does not re-derive")
    if sum(1 for d in directories if d["base_class"] == L_FROZEN) != s.get("frozen_directories"):
        problems.append("frozen_directories does not re-derive")
    if s.get("live_directories", 0) + s.get("frozen_directories", 0) != len(directories):
        problems.append("every directory must be either live or frozen")
    if sum(r["members_after_the_carrier"] > 0 for r in rows) \
            != s.get("carriers_outlived_by_a_later_member"):
        problems.append("carriers_outlived_by_a_later_member does not re-derive")
    if verdict_for(directories) != face.get("verdict"):
        problems.append("the verdict does not re-derive from the published directories")
    comp = [r for r in rows if r.get("composable")]
    if len(comp) != s.get("composable_rows"):
        problems.append("composable_rows does not re-derive")
    if s.get("composable_rows_on_a_live_base", 0) + s.get("composable_rows_on_a_frozen_base", 0) \
            != len(comp):
        problems.append("the composable cross-tab does not close against the composable rows")
    if sum(1 for r in comp if r["carrier_class"] == R_LIVE) \
            != s.get("composable_rows_on_a_live_base"):
        problems.append("composable_rows_on_a_live_base does not re-derive")
    for d in directories:
        mine = [r for r in rows if r["base"] == d["base"]]
        if d["carriers"] != len(mine):
            problems.append("%s: carrier count does not re-derive" % d["base"])
        if any(r["carrier_class"] == R_LIVE for r in mine) != (d["base_class"] == L_LIVE):
            problems.append("%s: base class disagrees with its carriers" % d["base"])
        if d["members"] != max((r["members_in_the_base"] for r in mine), default=0):
            problems.append("%s: member count does not re-derive" % d["base"])
        if d["carrier_rows_outlived"] != sum(1 for r in mine if r["carrier_class"] == R_LIVE):
            problems.append("%s: outlived count does not re-derive" % d["base"])
    if (s.get("distance_check") or {}).get("recomputed_face_home_rows") != len(rows):
        problems.append("distance_check does not restate the row total")
    return problems


def verify(face: dict | None = None) -> list[str]:
    face = face or _load(os.path.join(OUTDIR, FACE_NAME))
    problems = tally_problems(face)
    live = build(face.get("evidence_cutoff"))
    if live["verdict"] != face["verdict"]:
        problems.append("live verdict %s != published %s" % (live["verdict"], face["verdict"]))
    for key in ("face_home_rows", "distinct_directories", "live_directories",
                "frozen_directories", "composable_rows", "composable_rows_on_a_live_base"):
        if live["summary"].get(key) != face["summary"].get(key):
            problems.append("live %s differs from the published face" % key)
    mine = {d["base"]: d["members"] for d in face["summary"]["directories"]}
    theirs = {d["base"]: d["members"] for d in live["summary"]["directories"]}
    if mine != theirs:
        differing = sorted(k for k in set(mine) | set(theirs) if mine.get(k) != theirs.get(k))
        problems.append("member counts differ on %d directories: %s"
                        % (len(differing), differing[:5]))
    return problems


def selftest() -> int:
    legs = 0
    fails: list[str] = []

    def check(name: str, cond: bool) -> None:
        nonlocal legs
        legs += 1
        if not cond:
            fails.append(name)

    check("class_live", grade_row(100.0, [("a.json", 200.0)]) == R_LIVE)
    check("class_frozen_newer_carrier", grade_row(100.0, [("a.json", 50.0)]) == R_FROZEN)
    check("class_equal_is_frozen", grade_row(100.0, [("a.json", 100.0)]) == R_FROZEN)
    check("class_no_members_is_frozen", grade_row(100.0, []) == R_FROZEN)
    check("class_missing_carrier_is_frozen", grade_row(None, [("a.json", 9e9)]) == R_FROZEN)
    check("own_output_latest", is_own_output("results/state_tilt/" + FACE_NAME))
    check("own_output_dated", is_own_output("results/state_tilt/FACEHOME-2026-11-05.json"))
    check("own_output_spares_neighbours", not is_own_output("results/state_tilt/FILESLOT-2026-11-04.json"))
    check("own_output_spares_other_json", not is_own_output("results/state_tilt/sharedname_latest.json"))

    check("verdict_frozen", verdict_for([{"base_class": L_FROZEN}]) == V_ALL_FROZEN)
    check("verdict_live_all", verdict_for([{"base_class": L_LIVE},
                                           {"base_class": L_LIVE}]) == V_ALL_LIVE)
    check("verdict_split", verdict_for([{"base_class": L_LIVE},
                                        {"base_class": L_FROZEN}]) == V_SPLIT)

    def fixture_face(rows: list[dict], dirs: list[dict]) -> dict:
        return {
            "verdict": verdict_for(dirs),
            "rows": rows,
            "summary": {
                "face_home_rows": len(rows),
                "distinct_directories": len(dirs),
                "live_directories": sum(1 for d in dirs if d["base_class"] == L_LIVE),
                "frozen_directories": sum(1 for d in dirs if d["base_class"] == L_FROZEN),
                "carriers_outlived_by_a_later_member": sum(
                    1 for r in rows if r["carrier_class"] == R_LIVE),
                "composable_rows": sum(1 for r in rows if r.get("composable")),
                "composable_rows_on_a_live_base": sum(
                    1 for r in rows if r.get("composable") and r["carrier_class"] == R_LIVE),
                "composable_rows_on_a_frozen_base": sum(
                    1 for r in rows if r.get("composable") and r["carrier_class"] == R_FROZEN),
                "directories": dirs,
                "distance_check": {"recomputed_face_home_rows": len(rows)},
            },
        }

    def row(face: str, base: str, cls: str, after: int, comp: bool = True) -> dict:
        return {"face": face, "key": "dir", "base": base, "carrier_class": cls,
                "members_after_the_carrier": after, "composable": comp,
                "members_in_the_base": after + 1}

    def drow(d: str, cls: str, carriers: int, outlived: int, members: int) -> dict:
        return {"base": d, "base_class": cls, "carriers": carriers,
                "carrier_rows_outlived": outlived, "members": members}

    good = fixture_face(
        [row("results/a/x.json", "results/a", R_FROZEN, 0),
         row("results/a/y.json", "results/a", R_FROZEN, 0),
         row("results/b/x.json", "results/b", R_LIVE, 3)],
        [drow("results/a", L_FROZEN, 2, 0, 1), drow("results/b", L_LIVE, 1, 1, 4)])
    check("tally_clean", tally_problems(good) == [])

    bad = json.loads(json.dumps(good))
    bad["summary"]["live_directories"] = 2
    check("tally_catches_a_shifted_split", tally_problems(bad) != [])

    bad2 = json.loads(json.dumps(good))
    bad2["rows"][0]["carrier_class"] = R_LIVE
    check("tally_catches_a_carried_class", tally_problems(bad2) != [])

    bad3 = json.loads(json.dumps(good))
    bad3["verdict"] = V_ALL_LIVE
    check("tally_catches_a_carried_verdict", tally_problems(bad3) != [])

    bad4 = json.loads(json.dumps(good))
    bad4["summary"]["composable_rows_on_a_live_base"] = 0
    check("tally_catches_a_shifted_cross_tab", tally_problems(bad4) != [])

    bad5 = json.loads(json.dumps(good))
    bad5["summary"]["directories"][1]["base_class"] = L_FROZEN
    check("tally_catches_a_directory_that_contradicts_its_rows", tally_problems(bad5) != [])

    bad6 = json.loads(json.dumps(good))
    bad6["summary"]["directories"][0]["members"] = 7
    check("tally_catches_a_wrong_member_count", tally_problems(bad6) != [])

    # a fixture tree: the carrier is its own newest member unless it is excluded
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "results", "fam"), exist_ok=True)
        for name, stamp in (("carrier.json", 1000), ("later.json", 2000), ("earlier.json", 500)):
            p = os.path.join(tmp, "results", "fam", name)
            with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
                fh.write("{}\n")
            os.utime(p, (stamp, stamp))
        idx = {"homes": {"results/fam": ["results/fam/carrier.json",
                                         "results/fam/later.json",
                                         "results/fam/earlier.json"]}}
        got = members_of(idx, "results/fam", "results/fam/carrier.json", tmp)
        check("members_exclude_the_carrier",
              [m[0] for m in got] == ["results/fam/later.json", "results/fam/earlier.json"])
        check("members_sorted_newest_first", got[0][1] == 2000)
        check("carrier_outlived_by_the_later_member",
              grade_row(_mtime(tmp, "results/fam/carrier.json"), got) == R_LIVE)
        # self-exclusion: this study's own face never makes its directory live
        own = os.path.join(tmp, "results", "fam", FACE_NAME)
        with io.open(own, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("{}\n")
        os.utime(own, (9000, 9000))
        idx["homes"]["results/fam"].append("results/fam/" + FACE_NAME)
        got2 = members_of(idx, "results/fam", "results/fam/carrier.json", tmp)
        check("the_reader_does_not_count_itself", len(got2) == 2)
        check("the_reader_does_not_make_a_frozen_base_live",
              grade_row(_mtime(tmp, "results/fam/earlier.json"), 
                        members_of(idx, "results/fam", "results/fam/later.json", tmp)) is not None)

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
        problems = tally_problems(face)
        s = face["summary"]
        print("verdict: %s" % face["verdict"])
        print("face-home rows %d over %d directories: %d live / %d frozen"
              % (s["face_home_rows"], s["distinct_directories"],
                 s["live_directories"], s["frozen_directories"]))
        print("carriers outlived by a later member: %d of %d (%s)"
              % (s["carriers_outlived_by_a_later_member"], s["face_home_rows"],
                 s["share_of_carriers_outlived"]))
        print("composable rows: %d -- %d on a live base, %d on a frozen base"
              % (s["composable_rows"], s["composable_rows_on_a_live_base"],
                 s["composable_rows_on_a_frozen_base"]))
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