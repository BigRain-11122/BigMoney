"""E385 -- does splitting a merged key move any published number?

E383 published eight keys that each name two or more files on disk (``prep_state.json`` names 20,
``judge_state.json`` 18, ``_summary.json`` 2) and found seven of them quoted from a published
face's key list.  A reader's next question is the only one that can authorise a republish:
*would splitting those keys change any published NUMBER?*

So the study is a projection, not a recount.  Four published headlines are functions of the key
set, and each is re-derived twice from the same population:

  * E350 ``faces_named``          -- the set of keys the field census binds a face to;
  * E353 ``pairs`` / ``by_class`` -- guards on a field no source writes, classified per key;
  * E377 ``faces_no_census_keys`` -- faces a sink writes that no census key names;
  * E381 ``joined_only_faces``    -- faces only the joined keying names.

Rules this study holds itself to:

  * a key is a NAME and a file is a DOCUMENT; ``faces_named`` counts names, so the split number is
    published beside the name count and never instead of it (a name count is not a document count,
    and a document count is not a name count);
  * a key whose files cannot all be identified is priced as a floor (``>=n``) and never as a count;
  * a class that only exists because the key is ambiguous is not the same as a class that holds for
    every member -- the 7 ambiguous E353 pairs are re-classified per member file, because "the
    instrument cannot name the file" and "every member says the same thing" are different claims;
  * the two list arms (E377/E381) publish FACES, not keys, so equality with a merged basename is a
    different predicate and is measured as its own column;
  * no published face is rewritten: E350/E353/E377/E381 are read as published, and a split that
    would move a headline is reported as a republish decision (E382's rule), not applied here.

Usage:
  python scripts/e385_merged_key_split.py run       # build the face
  python scripts/e385_merged_key_split.py verify    # re-derive the arithmetic from the face
  python scripts/e385_merged_key_split.py selftest  # offline fixture legs
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e350_field_branch_census as e350  # noqa: E402
import e353_unwritten_guard_presence as e353  # noqa: E402
import e383_shared_key_collision as e383  # noqa: E402

TODAY = "2026-11-03"
FACE = "SPLITPRICE-%s.json" % TODAY
LATEST = "splitprice_latest.json"
PUBLISHED_DIR = os.path.join(ROOT, "results", "state_tilt")
STUDY = "E385_merged_key_split_projection"
SELF_REL = "scripts/e385_merged_key_split.py"
OWN_FILES = (FACE, LATEST)

E350_FACE = "FIELDBRANCH-2026-11-01.json"
E353_FACE = "GUARDPRESENCE-2026-11-02.json"
E377_FACE = "UNRESOLVEDDEST-2026-11-03.json"
E381_FACE = "COMPONENTKEY-2026-11-03.json"

V_MOVES = ("splitting_the_merged_keys_moves_a_published_headline_so_the_republish_is_a_decision_"
           "not_a_cleanup")
V_MIXED = ("splitting_moves_the_guard_headline_and_only_the_pairs_whose_ambiguity_comes_from_outside_"
           "the_census_walk_are_settled_by_naming_a_member_while_the_rest_stay_undecidable_inside_it")
V_NAMES = ("splitting_the_merged_keys_leaves_every_published_headline_where_it_is_because_the_"
           "counts_are_names_and_the_split_only_adds_documents_behind_those_names")
V_STABLE = ("no_key_in_the_population_names_two_files_so_a_split_has_nothing_to_move")
V_EMPTY = "the_population_was_empty_so_no_claim_is_made"


def say(message):
    print(message, flush=True)


# --------------------------------------------------------------------------- identification

def identify(key):
    """``(files, complete)`` -- every repo-relative file a key can name, and whether that is all.

    A key is a folded value here: ``prep_state.json`` is resolved the way E383 resolves a value, by
    suffix against one index of the tree, so one spelling can never be two files and a key with two
    hits is never silently taken as one.
    """
    raw = (key or "").strip()
    if not raw:
        return [], False
    norm = e383._norm(raw)
    if (len(norm) > 1 and norm[1] == ":") or norm.startswith("/"):
        files = e383._resolve(norm)
        return files, bool(files)
    files = e383._resolve(norm)
    if not files:
        return [], False
    return files, True


def key_table(keys):
    """One row per distinct key: its identified files and whether it merges more than one."""
    rows = []
    for key in sorted(keys):
        files, complete = identify(key)
        inside = [f for f in files if _in_census(f)]
        rows.append({
            "key": key,
            "files": files,
            "n_files": len(files),
            "files_inside_the_census_walk": inside,
            "n_files_inside_the_census_walk": len(inside),
            "identified_complete": complete,
            "merged": len(files) > 1,
            "merge_survives_the_walk": len(inside) > 1,
        })
    return rows


# The census walks the repo minus the trees E383 named (``Money02``, ``legacy``, ``media``) and
# E353's index walks everything but ``.git``/caches.  So a name can be "ambiguous" only because two
# documents outside the census corpus share it -- that ambiguity is the instrument's, not the data's,
# and it has to be priced separately or the split inflates a count the census never read.
CENSUS_EXCLUDED_TOPS = frozenset(("Money02", "legacy", "media", "Money0923"))


def _in_census(path):
    return path.split("/")[0] not in CENSUS_EXCLUDED_TOPS


# --------------------------------------------------------------------------- arm 1: E350 faces_named

def arm_faces_named(named_keys):
    """``faces_named`` counts NAMES; the split number is the documents behind those names."""
    rows = key_table(named_keys)
    names = len(rows)
    documents = 0
    documents_unbounded = 0
    merged = [r for r in rows if r["merged"]]
    for row in rows:
        if row["n_files"]:
            documents += row["n_files"]
        else:
            # a name the tree cannot resolve is still one name, and it hides an unknown number of
            # documents: counted once and flagged, never priced as zero.
            documents += 1
            documents_unbounded += 1
    return {
        "headline": "e350.faces_named",
        "published_unit": "keys",
        "published": names,
        "split": documents,
        "delta": documents - names,
        "delta_is_exact": documents_unbounded == 0,
        "names_that_merge_two_or_more_files": len(merged),
        "merges_that_survive_dropping_files_outside_the_census_walk": sum(
            1 for r in merged if r["merge_survives_the_walk"]),
        "merged_names_whose_ambiguity_is_only_outside_the_walk": sum(
            1 for r in merged if not r["merge_survives_the_walk"]),
        "largest_merge": max([r["n_files"] for r in merged], default=0),
        "unresolved_names": documents_unbounded,
        "verdict_moves": False,
        "why": ("the headline is a count of keys and every consumer of it names a key, so adding "
                "documents behind a name changes what the number means, not what it says"),
        "merged_rows": [{"key": r["key"], "n_files": r["n_files"],
                         "n_inside": r["n_files_inside_the_census_walk"],
                         "merge_survives": r["merge_survives_the_walk"],
                         "files": r["files"][:6]} for r in merged[:20]],
    }


# --------------------------------------------------------------------------- arm 2: E353 pairs

def arm_guard_pairs(published):
    """The published pairs, then the same pairs re-classified per member of each ambiguous key."""
    rows = published.get("rows") or []
    index = e353.build_index()
    expanded = []
    ambiguous_pairs = 0
    reachable_members = 0
    divergent = []
    for row in rows:
        face, field = row.get("face"), row.get("field")
        res = e353.resolve(face, index)
        if res["kind"] != "ambiguous":
            expanded.append({"face": face, "field": field, "class": row.get("class"),
                             "from": "published"})
            continue
        ambiguous_pairs += 1
        inside = [a for a in res["alternatives"] if _in_census(a)]
        member_classes = []
        for alt in res["alternatives"]:
            member = e353.classify(alt, field, index)
            member_classes.append({"file": alt, "class": member["class"], "state": member["state"],
                                   "in_census_walk": _in_census(alt)})
            if member["class"] != e353.CLASS_UNREACHABLE:
                reachable_members += 1
        classes = sorted({m["class"] for m in member_classes})
        if len(classes) > 1 or row.get("class") not in classes:
            tops = sorted({m["file"].split("/")[0] for m in member_classes if "/" in m["file"]})
            in_census_classes = sorted({m["class"] for m in member_classes
                                        if m["in_census_walk"]})
            divergent.append({"face": face, "field": field,
                              "published_class": row.get("class"),
                              "member_classes": classes,
                              "member_classes_inside_the_census_walk": in_census_classes,
                              "n_members_inside_the_census_walk": len(inside),
                              "member_top_segments": tops,
                              "spans_unrelated_subtrees": len(tops) > 1,
                              "members": member_classes[:8],
                              "n_members": len(member_classes)})
        for member in member_classes:
            expanded.append({"face": member["file"], "field": field, "class": member["class"],
                             "from": "split"})
    unpriced = 0
    for row in rows:
        res = e353.resolve(row.get("face"), index)
        if res["kind"] in ("missing", "path_moved") and not res["alternatives"]:
            unpriced += 1
    split_pairs = len(expanded)
    by_class = {}
    for row in expanded:
        by_class[row["class"]] = by_class.get(row["class"], 0) + 1
    unreachable_members = ambiguous_pairs * 0
    for row in expanded:
        if row["from"] == "split" and row["class"] == e353.CLASS_UNREACHABLE:
            unreachable_members += 1
    return {
        "headline": "e353.pairs",
        "published_unit": "pairs_on_one_key",
        "published": len(rows),
        "split": split_pairs,
        "delta": split_pairs - len(rows),
        "delta_is_exact": unpriced == 0,
        "pairs_on_an_ambiguous_key": ambiguous_pairs,
        "split_members": split_pairs - len(rows) + ambiguous_pairs,
        "members_that_are_reachable_when_named": reachable_members,
        "pairs_whose_members_disagree_with_the_published_class": len(divergent),
        "divergent_pairs_spanning_unrelated_subtrees": sum(
            1 for row in divergent if row["spans_unrelated_subtrees"]),
        "divergent_pairs_with_members_of_two_classes": sum(
            1 for row in divergent if len(row["member_classes"]) > 1),
        "divergent_pairs_decided_by_one_in_census_member": sum(
            1 for row in divergent if row["n_members_inside_the_census_walk"] == 1),
        "divergent_pairs_ambiguous_even_inside_the_census_walk": sum(
            1 for row in divergent if row["n_members_inside_the_census_walk"] > 1),
        "divergent_pairs_with_no_in_census_member": sum(
            1 for row in divergent if row["n_members_inside_the_census_walk"] == 0),
        "by_class_published": published.get("summary", {}).get("by_class"),
        "by_class_split": by_class,
        "verdict_moves": bool(divergent),
        "why": ("an ambiguous key is published as unreachable because the instrument cannot name the "
                "file, so the published class says nothing about the guard; naming each member shows "
                "the class it would get -- and the member list also shows whether those members were "
                "ever versions of one face or unrelated documents sharing a basename"),
        "divergent": divergent[:20],
    }


# --------------------------------------------------------------------------- arms 3/4: face lists

def arm_face_list(name, faces, key_field="face"):
    """A list arm publishes FACES; the split question is whether a face's own basename merges."""
    rows = []
    merged = []
    index = e353.build_index()
    for item in faces:
        path = item.get(key_field) if isinstance(item, dict) else item
        if not path:
            continue
        base = e383._norm(path).rsplit("/", 1)[-1]
        same_name = index.get(base, [])
        row = {"face": path, "basename": base, "files_with_that_name": len(same_name),
               "shares_its_name": len(same_name) > 1}
        rows.append(row)
        if row["shares_its_name"]:
            merged.append(row)
    return {
        "headline": name,
        "published_unit": "faces",
        "published": len(rows),
        "split": len(rows),
        "delta": 0,
        "delta_is_exact": True,
        "faces_sharing_a_basename": len(merged),
        "verdict_moves": False,
        "why": ("the unit is a face path, and a face path names one file whatever its basename is "
                "shared with; the merge cannot add or remove a member here"),
        "merged_rows": merged[:12],
    }


# --------------------------------------------------------------------------- build

def _load(name):
    with open(os.path.join(PUBLISHED_DIR, name), "r", encoding="utf-8") as fh:
        return json.load(fh)


def build(write_face=True, sources=None):
    say("reading the published upstream faces")
    published353 = _load(E353_FACE)
    published377 = _load(E377_FACE)
    published381 = _load(E381_FACE)

    say("re-deriving E350's faces_named from the corpus (the artifact publishes only its top rows)")
    if sources is None:
        sources = e350._sources()
    reads, writes, stats = e350.measure(sources)
    named = stats["faces_named"]

    say("arm 1/4 faces_named over %d names" % len(named))
    a1 = arm_faces_named(named)
    say("arm 2/4 guard pairs over %d published pairs" % len(published353.get("rows") or []))
    a2 = arm_guard_pairs(published353)
    say("arm 3/4 unresolved destinations")
    a3 = arm_face_list("e377.faces_no_census_keys", published377.get("faces_no_census_keys") or [])
    say("arm 4/4 joined-only faces")
    a4 = arm_face_list("e381.joined_only_faces", published381.get("joined_only_faces") or [])

    arms = [a1, a2, a3, a4]
    summary = {
        "arms": len(arms),
        "headlines_that_move": sum(1 for a in arms if a["verdict_moves"]),
        "documents_added_by_the_split": a1["delta"],
        "names_that_merge_two_or_more_files": a1["names_that_merge_two_or_more_files"],
        "largest_merge": a1["largest_merge"],
        "pairs_added_by_the_split": a2["delta"],
        "pairs_on_an_ambiguous_key": a2["pairs_on_an_ambiguous_key"],
        "split_members_that_are_reachable_when_named": a2["members_that_are_reachable_when_named"],
        "pairs_whose_members_disagree": a2["pairs_whose_members_disagree_with_the_published_class"],
        "divergent_pairs_spanning_unrelated_subtrees":
            a2["divergent_pairs_spanning_unrelated_subtrees"],
        "divergent_pairs_decided_by_one_in_census_member":
            a2["divergent_pairs_decided_by_one_in_census_member"],
        "divergent_pairs_ambiguous_even_inside_the_census_walk":
            a2["divergent_pairs_ambiguous_even_inside_the_census_walk"],
        "merged_names_whose_ambiguity_is_only_outside_the_walk":
            a1["merged_names_whose_ambiguity_is_only_outside_the_walk"],
        "faces_sharing_a_basename_in_a_face_list": a3["faces_sharing_a_basename"]
        + a4["faces_sharing_a_basename"],
        "split_is_exact_everywhere": a1["delta_is_exact"] and a2["delta_is_exact"],
        "e350_faces_named_republished": a1["published"],
        "corpus_sources": stats.get("sources"),
        "corpus_parsed": stats.get("parsed"),
    }
    summary["verdict"] = decide(summary)
    face = {
        "study": STUDY,
        "evidence_cutoff": TODAY,
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "source": SELF_REL,
        "published_faces": [E350_FACE, E353_FACE, E377_FACE, E381_FACE],
        "summary": summary,
        "arms": arms,
        "verdict": summary["verdict"],
        "bound": {
            "measured": ("the four published headlines re-derived from the same population under "
                         "two keyings, plus a per-member re-classification of every guard pair "
                         "that sits on an ambiguous key"),
            "not_measured": ("whether a consumer of a merged key reads the right member (that is "
                             "E383's consumer table); a document count for a name the tree cannot "
                             "resolve (published as a floor)"),
            "no_rewrites": "E350/E353/E377/E381 are read as published and none is touched here",
        },
    }
    say("verdict: %s" % summary["verdict"])
    if write_face:
        _write(face)
    return face


def decide(summary):
    """The verdict is recomputed from the summary, never written by hand."""
    if not summary.get("arms"):
        return V_EMPTY
    if summary["names_that_merge_two_or_more_files"] == 0 and summary["pairs_on_an_ambiguous_key"] == 0:
        return V_STABLE
    if summary["headlines_that_move"]:
        settled = summary.get("divergent_pairs_decided_by_one_in_census_member") or 0
        still = summary.get("divergent_pairs_ambiguous_even_inside_the_census_walk") or 0
        if settled and still:
            return V_MIXED
        return V_MOVES
    return V_NAMES


def _write(face):
    os.makedirs(PUBLISHED_DIR, exist_ok=True)
    for name in (FACE, LATEST):
        path = os.path.join(PUBLISHED_DIR, name)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
    say("wrote %s and %s" % (FACE, LATEST))


# --------------------------------------------------------------------------- verify

def verify():
    """Re-derive the arithmetic from the published face and the tree as it stands."""
    problems = []
    path = os.path.join(PUBLISHED_DIR, FACE)
    with open(path, "r", encoding="utf-8") as fh:
        face = json.load(fh)
    summary, arms = face["summary"], face["arms"]
    if face.get("evidence_cutoff") != TODAY:
        problems.append("evidence_cutoff moved")
    if len(arms) != summary["arms"]:
        problems.append("arm count does not match the summary")
    a1, a2, a3, a4 = arms
    if a1["split"] - a1["published"] != a1["delta"]:
        problems.append("faces_named delta does not re-derive from its own two numbers")
    if sum(1 for r in a1["merged_rows"] if r["n_files"] > 1) != len(a1["merged_rows"]):
        problems.append("a row in merged_rows names fewer than two files")
    for row in a1["merged_rows"]:
        files, _ = identify(row["key"])
        if row["n_files"] != len(files):
            problems.append("merged row %s: n_files %d but the tree resolves %d"
                            % (row["key"], row["n_files"], len(files)))
    if a2["split"] - a2["published"] != a2["delta"]:
        problems.append("pairs delta does not re-derive")
    if a2["by_class_split"] and sum(a2["by_class_split"].values()) != a2["split"]:
        problems.append("split classes do not sum to the split pair count")
    for row in a2["divergent"]:
        if len({m["class"] for m in row["members"]}) < 2 and row["published_class"] in {
                m["class"] for m in row["members"]}:
            problems.append("a divergent pair does not actually diverge: %s" % row["face"])
    if summary["headlines_that_move"] != sum(1 for a in arms if a["verdict_moves"]):
        problems.append("headline count does not re-derive")
    if decide(summary) != face["verdict"]:
        problems.append("decision gate does not re-derive the published verdict")
    for arm in (a3, a4):
        if arm["split"] != arm["published"] or arm["delta"] != 0:
            problems.append("%s: a face list cannot move without a member changing" % arm["headline"])
    say("verify problems=%s" % (problems or "[]"))
    return problems


# --------------------------------------------------------------------------- selftest

def _fixture_tree(root):
    """A tiny tree: one name shared by two files, one name unique, one face list."""
    def put(rel, obj):
        full = os.path.join(root, rel.replace("/", os.sep))
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(obj, fh)

    put("results/trial_labor_w1/prep_state.json", {"nshards": 3})
    put("results/trial_labor_w2/prep_state.json", {"nshards": 0})
    put("results/solo.json", {"flag": 1})


def selftest():
    import tempfile

    legs = []

    def leg(name, ok, note=""):
        legs.append((name, bool(ok), note))

    # 1. identification: a bare shared name resolves to every file, a unique one to itself
    files, complete = identify("scripts/e350_field_branch_census.py")
    leg("identify_unique", len(files) == 1 and complete)
    shared = identify("prep_state.json")
    leg("identify_shared", shared[1] is True and len(shared[0]) >= 2,
        "prep_state.json -> %d files" % len(shared[0]))
    leg("identify_missing", identify("definitely_not_a_file_zzz.json") == ([], False))

    # 2. a name the tree cannot resolve is still ONE name and is published as a floor
    a1 = arm_faces_named({"scripts/e350_field_branch_census.py", "nowhere_zzz.json"})
    leg("unresolved_name_is_one_not_zero", a1["split"] == 2)
    leg("unresolved_name_is_flagged", a1["unresolved_names"] == 1 and a1["delta_is_exact"] is False)

    # 3. a merged name adds documents without moving the headline
    a1b = arm_faces_named({"prep_state.json", "scripts/e350_field_branch_census.py"})
    leg("names_do_not_move", a1b["published"] == 2 and a1b["split"] > 2)
    leg("merge_counted", a1b["names_that_merge_two_or_more_files"] == 1)
    leg("largest_merge_matches_rows", a1b["largest_merge"] == max(
        r["n_files"] for r in a1b["merged_rows"]))

    # 4. a face list cannot move: its unit is a path
    a3 = arm_face_list("x", [{"face": "results/trial_labor_w1/prep_state.json"}, "results/solo.json"])
    leg("face_list_is_a_path_unit", a3["published"] == 2 and a3["delta"] == 0)
    leg("face_list_reports_the_shared_name", a3["faces_sharing_a_basename"] == 1)

    # 5. the decision gate is a function of the summary, not of the prose
    base = {"arms": 4, "headlines_that_move": 0, "names_that_merge_two_or_more_files": 3,
            "pairs_on_an_ambiguous_key": 1}
    leg("decide_names", decide(base) == V_NAMES)
    leg("decide_moves", decide(dict(base, headlines_that_move=1)) == V_MOVES)
    leg("decide_mixed", decide(dict(base, headlines_that_move=1,
                                    divergent_pairs_decided_by_one_in_census_member=2,
                                    divergent_pairs_ambiguous_even_inside_the_census_walk=5))
        == V_MIXED)
    leg("decide_stable", decide(dict(base, names_that_merge_two_or_more_files=0,
                                     pairs_on_an_ambiguous_key=0)) == V_STABLE)
    leg("decide_empty", decide({}) == V_EMPTY)

    # 6. an ambiguous guard pair is re-classified per member, not assumed
    with tempfile.TemporaryDirectory() as tmp:
        _fixture_tree(tmp)
        index = e353.build_index(tmp)
        res = e353.resolve("prep_state.json", index, tmp)
        leg("fixture_key_is_ambiguous", res["kind"] == "ambiguous" and res["n_alternatives"] == 2)
        per = [e353.classify(alt, "nshards", index, tmp) for alt in res["alternatives"]]
        leg("members_are_classified_separately",
            len({(m["class"], m["state"]) for m in per}) >= 2,
            "states=%s" % sorted({m["state"] for m in per}))
        leg("published_class_is_the_ambiguity", e353.classify("prep_state.json", "nshards", index,
                                                              tmp)["class"] == e353.CLASS_UNREACHABLE)

    # 7. own files are named so the published-face scan cannot read its own output back in
    leg("own_files_named", FACE in OWN_FILES and LATEST in OWN_FILES)

    passed = sum(1 for _, ok, _ in legs if ok)
    for name, ok, note in legs:
        say("  %-42s %s%s" % (name, "PASS" if ok else "FAIL", ("  " + note) if note and not ok else ""))
    say("selftest %d/%d" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "run":
        face = build()
        say("split of %d names adds %d documents; %d headline(s) move"
            % (face["summary"]["e350_faces_named_republished"],
               face["summary"]["documents_added_by_the_split"],
               face["summary"]["headlines_that_move"]))
        return 0
    if cmd == "verify":
        return 0 if not verify() else 1
    if cmd == "selftest":
        return selftest()
    say("usage: e385_merged_key_split.py [run|verify|selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))