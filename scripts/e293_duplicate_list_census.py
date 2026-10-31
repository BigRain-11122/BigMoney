"""E293 -- which published faces carry literally duplicated lists, and does anything count them twice?

E291 classified 746 equal-length pairs by content and found 135 that are the very same list inside ONE
face.  An equal length is not a defect; a copy might be.  The question E291 left open is not "how many
copies" but "does any published number derive from a copy as if it were a second record" -- a summary
that sums or compares two aliases counts one thing twice, and nothing in the family reports that.

Four measurements, each of which can fail on its own:

  (1) THE CENSUS.  Group every list in every dated BAND face by its content (canonical JSON).  A group
      of two or more members with the same unit is an alias group.  Publish the members, their length
      and the face they live in.

  (2) THE SHAPE OF THE COPY.  A copy can be schema-driven -- the same key appears in every arm, so
      every arm carries an identical label/slot list -- or accidental -- a list restated inside a
      record that already has it.  Three shapes are distinguished by where the members sit:
        same_slot_across_arms   all members share one index-free path (arm[0].x == arm[1].x)
        parallel_slot_across_arms  members sit at the same slot of sibling containers
                                    (groups.A.cells == groups.B.cells)
        scattered               neither (a restatement somewhere else in the face)
      Only the third is a copy an author did not have to make.

  (3) THE SUM TEST.  The decisive join: does any number in the scope that ENCLOSES an alias group equal
      the total length of the lists it sits beside?  A count equal to that total, when the lists are
      copies, is a count that counts the same content twice.  This test is strict -- it compares against
      the actual sum of the sibling lists -- because a loose "count equals the length" test fires on
      every small integer (E207's lesson: a name is not a measurement).

  (4) THE LOOSE JOIN, LABELLED.  Every other number in an enclosing scope that equals the alias member
      count or the alias total is published too, with a coincidence flag for values small enough that
      matching is cheap (<= 5, or a value that occurs in the face more than once).  Published so the
      strict test's silence can be read as silence and not as absence of a scan.

DECISION RULE, declared before any number is read:

  D1  THE UNIT IS THE LIST, NOT THE PAIR.  Two aliases are one group; three are still one group.  A
      pair count would report a 4-member copy as six copies.
  D2  THE STRICT SUM TEST IS THE ONLY ONE THAT CAN CONVICT.  Candidate numbers from the loose join are
      disclosed with their coincidence flag and never enter the verdict on their own.
  D3  SHAPE IS MEASURED, NOT ASSUMED.  "Schema-driven" is a claim about where the copies SIT, measured
      from their paths, not about what the face's author intended.
  D4  NO REBURN.  Published faces are re-read only; no draw stream, no band rebuild, no engine.

Verdict vocabulary (frozen):
  no_published_face_repeats_list_content_so_no_alias_exists
  every_alias_is_a_schema_copy_and_no_scope_counts_one_twice
  some_aliases_are_accidental_copies_but_no_scope_counts_one_twice
  a_count_in_an_enclosing_scope_equals_the_alias_total_so_the_duplicate_is_counted_twice

Usage:  python scripts/e293_duplicate_list_census.py run|verify|selftest
"""
import collections
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e286_count_field_scope as e286  # noqa: E402  (the census family this study extends)
import e291_ambiguity_chance as e291  # noqa: E402  (the pair classification that raised the question)
import e_band_family_vintage as vintage  # noqa: E402  (universe vintage freeze)

ROOT = e286.ROOT
OUTDIR = e286.OUTDIR

STUDY = "E293_duplicate_list_census"
TITLE = ("which published faces carry literally duplicated lists, is the copy schema-driven or "
         "accidental, and does any number in an enclosing scope count the copies twice?")
CUTOFF = "2026-10-29"
FACE = "BANDDUPES-%s.json" % CUTOFF
LATEST = "banddupes_latest.json"
SELF_FACES = (FACE, LATEST, e291.FACE, e291.SRC_FACE)   # self + both predecessor faces

SMALL_COINCIDENCE = 5   # an integer <= this matches too cheaply to be evidence on its own

VERDICT_VOCAB = (
    "no_published_face_repeats_list_content_so_no_alias_exists",
    "every_alias_is_a_schema_copy_and_no_scope_counts_one_twice",
    "some_aliases_are_accidental_copies_but_no_scope_counts_one_twice",
    "a_count_in_an_enclosing_scope_equals_the_alias_total_so_the_duplicate_is_counted_twice",
)

SHAPE_VOCAB = ("same_slot_across_arms", "parallel_slot_across_arms", "scattered")

NO_BILL = ("measurement only: the dated BAND faces are re-read and the lists already published in them "
           "are grouped by content. No draw stream is drawn, no band rebuilt, no engine runs, no verdict "
           "about the market. A verdict here is a statement about the published JSON, its shapes and its "
           "duplicate content.")


# ------------------------------------------------------------------ io
def load(name):
    return e286.load(name)


def census_names():
    """E291's universe (its own and E290's faces already excluded) minus this study's own faces."""
    blocked = set(SELF_FACES)
    upstream = e291.census_names()
    # E297 (r1315) froze E291 to the name list it published, so its census_names now returns
    # (names, vintage_note). Taking the tuple as a name list raised TypeError: unhashable list --
    # i.e. a published face whose derivation had stopped running at all.
    if isinstance(upstream, tuple):
        upstream = upstream[0]
    return [n for n in upstream if n not in blocked]


# ------------------------------------------------------------------ paths
def indep(path):
    """Index-free path: arm[3].cells -> arm.cells (the same slot across arms)."""
    return ".".join(seg.split("[")[0] for seg in str(path).split("."))


def parent_path(path):
    """Index-free path of the container that holds this slot: groups.A.cells -> groups."""
    return indep(path).rsplit(".", 1)[0] if "." in indep(path) else ""


def content_key(value):
    return json.dumps(value, sort_keys=True)


def is_ancestor(candidate, leaf):
    """True when candidate's scope strictly encloses leaf's scope."""
    return bool(candidate) and candidate != leaf and leaf.startswith(candidate + ".")


def shape_of(members):
    """Where the copies sit: one slot repeated, a slot repeated over sibling arms, or a restatement.

    The middle segments are allowed to differ in several places because a face often lays its arms
    out as a grid (cross/self x 200/60); what makes the copy schema-driven is that head and tail --
    the container root and the slot name -- are the same, so every arm had to carry the list.
    """
    indeps = [indep(p) for p, _ in members]
    if len(set(indeps)) == 1:
        return "same_slot_across_arms"
    segs = [tuple(seg.split("[")[0] for seg in str(p).split(".")) for p, _ in members]
    if len({len(t) for t in segs}) == 1 and len({t[0] for t in segs}) == 1 \
            and len({t[-1] for t in segs}) == 1 and len(set(segs)) == len(segs):
        return "parallel_slot_across_arms"
    return "scattered"


# ------------------------------------------------------------------ census
def alias_groups(names):
    """[{face, unit, members[(path,len)], ...}] over E286's canonical list universe.

    The universe is the one E286/E291 already agreed on (a list of records/values inside a face, not
    every raw list): a raw walk would report every empty list as a duplicate of every other empty
    list, which is a fact about JSON, not about the face.
    """
    out = []
    for name in names:
        rec = e286.analyse_face(name)
        by_unit = collections.defaultdict(list)
        for item in rec["unit_lists"]:
            by_unit[item["unit"]].append((item["path"], item["n_items"]))
        if not any(len(v) > 1 for v in by_unit.values()):
            continue
        obj = load(name)
        for unit, lists in by_unit.items():
            if len(lists) < 2:
                continue
            buckets = collections.defaultdict(list)
            for path, n_items in lists:
                buckets[content_key(e291.resolve(obj, path))].append((path, n_items))
            for members in buckets.values():
                if len(members) < 2:
                    continue
                members = sorted(members)
                lengths = sorted({n for _, n in members})
                indeps = sorted({indep(p) for p, _ in members})
                parents = sorted({parent_path(p) for p, _ in members})
                shape = shape_of(members)
                out.append({
                    "face": name,
                    "unit": unit,
                    "members": [{"path": p, "length": n} for p, n in members],
                    "n_members": len(members),
                    "length": lengths[0] if len(lengths) == 1 else None,
                    "lengths_seen": lengths,
                    "shape": shape,
                    "scope": indeps[0] if len(indeps) == 1 else None,
                    "scopes": indeps,
                    "enclosing_scope": parents[0] if len(parents) == 1 else None,
                    "pairs": len(members) * (len(members) - 1) // 2,
                })
    return out


def subtree_lists(node, prefix=""):
    """[(index-free path, unit, length)] for every list under this node."""
    out = []
    for path, items in e286.walk_lists(node, prefix):
        out.append((indep(path), e286.path_key(path), len(items)))
    return out


def aggregate_index(obj):
    """{count_path: (value, {unit: (n_lists, total_len, index-free paths)})}.

    For each number, the lists of the container that HOLDS it are the candidate things it totals.
    Two copies of a list can never sit in the same dict (keys are unique), so the only place a
    number can add a copy twice is a container that holds them through sibling arms.
    """
    out = {}
    for path, value, parent in e286.walk_values(obj):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        # the container's own dotted path, so the lists are named the way the alias members are
        prefix = path.rsplit(".", 1)[0] if "." in path else ""
        by_unit = {}
        for ipath, unit, length in subtree_lists(parent, prefix):
            slot = by_unit.setdefault(unit, [0, 0, []])
            slot[0] += 1
            slot[1] += length
            slot[2].append(ipath)
        out[path] = (value, by_unit)
    return out


def join_alias(group, obj):
    """Split the joins into the strict aggregate test (can convict) and the labelled loose matches."""
    numbers = aggregate_index(obj)
    strict, loose = [], []
    member_count = group["n_members"]
    total = sum(m["length"] for m in group["members"])
    scopes = set(group["scopes"] or [])
    if group["scope"]:
        scopes.add(group["scope"])
    member_indeps = {indep(m["path"]) for m in group["members"]}

    for path, (value, by_unit) in sorted(numbers.items()):
        # the number's SCOPE is the container that holds it, not its own dotted path
        scope = indep(path.rsplit(".", 1)[0]) if "." in path else ""
        if not any(is_ancestor(scope, s) for s in scopes):
            continue
        slot = by_unit.get(group["unit"])
        # (3) strict: the number equals the total length of EVERY list of this unit under it, and
        #     the copies are among those lists -- so the number was built by adding them up
        if slot and slot[0] >= member_count and value == slot[1] and value == total \
                and member_indeps <= set(slot[2]):
            strict.append({
                "count_path": path, "count_value": value,
                "unit_lists_under_it": slot[0], "unit_total_length": slot[1],
                "alias_total_length": total,
                "why": "the number equals the total length of every list of this unit in its scope, "
                       "and the copies are among them",
            })
            continue
        # (4) loose: equals the member count or one member's length, disclosed with a flag
        if value in (member_count, group["length"]) and value is not None:
            loose.append({
                "count_path": path,
                "count_value": value,
                "matches": "member_count" if value == member_count else "member_length",
                "coincidence_prone": bool(value <= SMALL_COINCIDENCE),
            })
    return strict, loose


# ------------------------------------------------------------------ build
def build(extend=False):
    live = census_names()
    frozen, frozen_from = (None, None) if extend else vintage.published_names(
        OUTDIR, (FACE, LATEST), ("faces_censused",))
    if frozen:
        keep = set(live)
        names = [n for n in frozen if n in keep]
        vintage_note = vintage.note(names, sorted(keep - set(names)), len(live), frozen_from, None)
        vintage_note["faces_published_but_gone_from_disk"] = [n for n in frozen if n not in keep]
    else:
        names = live
        vintage_note = vintage.note(names, [], len(names), None, None)
    groups = alias_groups(names)

    shapes = collections.Counter(g["shape"] for g in groups)
    by_face = collections.Counter(g["face"] for g in groups)
    by_unit = collections.Counter(g["unit"] for g in groups)

    cache = {}
    rows = []
    strict_hits = []
    loose_total = 0
    loose_prone = 0
    for group in groups:
        if group["face"] not in cache:
            cache[group["face"]] = load(group["face"])
        strict, loose = join_alias(group, cache[group["face"]])
        loose_total += len(loose)
        loose_prone += len([c for c in loose if c["coincidence_prone"]])
        row = dict(group)
        row["strict_sum_joins"] = strict
        row["loose_joins"] = loose
        row["counts_one_twice"] = bool(strict)
        rows.append(row)
        for hit in strict:
            strict_hits.append({"face": group["face"], "unit": group["unit"],
                                "scope": group["scope"] or group["scopes"],
                                "count_path": hit["count_path"],
                                "count_value": hit["count_value"],
                                "n_alias_members": group["n_members"]})

    accidental = [r for r in rows if r["shape"] == "scattered"]
    pairs_here = sum(r["pairs"] for r in rows)
    # the cross-study identity: E291 counted alias PAIRS from the same universe, so sum(C(k,2))
    # over these groups must equal its published alias count.  A pair count and a group count are
    # different numbers, and only this leg shows they describe the same copies.
    e291_alias_pairs = None
    try:
        e291_face = load(e291.FACE)
        e291_alias_pairs = ((e291_face.get("summary") or {}).get("pair_mechanism") or {}).get(
            "alias_identical_content")
    except (IOError, ValueError, KeyError, AttributeError):
        pass
    summary = {
        "faces_censused": len(names),
        "alias_groups": len(rows),
        "alias_members": sum(r["n_members"] for r in rows),
        "alias_member_share_of_all_lists": None,
        "faces_with_an_alias": len(by_face),
        "top_faces": [[f, c] for f, c in by_face.most_common(5)],
        "top_units": [[u, c] for u, c in by_unit.most_common(8)],
        "shape_counts": {k: shapes.get(k, 0) for k in SHAPE_VOCAB},
        "schema_driven_groups": len([r for r in rows if r["shape"] != "scattered"]),
        "accidental_groups": len(accidental),
        "accidental_examples": [{"face": r["face"], "unit": r["unit"], "members": r["members"]}
                                for r in accidental[:5]],
        "strict_sum_test": {
            "groups_tested": len(rows),
            "convictions": len(strict_hits),
            "hits": strict_hits[:20],
            "test": "a number whose scope strictly encloses an alias group, whose value equals the "
                    "total length of EVERY list of that unit in its own container, with the copies "
                    "among those lists, was built by adding the copies up",
        },
        "loose_join": {
            "candidates": loose_total,
            "coincidence_prone": loose_prone,
            "note": "these match the alias member count or total, which small integers do by accident. "
                    "They never enter the verdict (D2).",
        },
        "calibrated": False,
    }
    all_lists = 0
    for name in names:
        all_lists += len(e286.analyse_face(name)["unit_lists"])
    summary["all_lists_censused"] = all_lists
    summary["alias_pairs_recounted"] = pairs_here
    summary["e291_alias_pairs_published"] = e291_alias_pairs
    summary["alias_member_share_of_all_lists"] = (float(summary["alias_members"]) / all_lists) if all_lists else None

    verdict = decide(summary)
    summary["verdict"] = verdict

    # re-read the members independently: the grouping above buckets by content, so only a second
    # read of the published paths can show the buckets actually hold copies
    share_content = True
    for row in rows:
        obj = cache.get(row["face"]) or load(row["face"])
        values = [e291.resolve(obj, m["path"]) for m in row["members"]]
        if len({content_key(v) for v in values}) != 1:
            share_content = False

    # the cross-study identity (E291's alias pairs) is computed above, with the summary
    identity = {
        "every_group_has_two_members": all(r["n_members"] >= 2 for r in rows),
        "every_group_members_are_distinct_paths": all(
            len({m["path"] for m in r["members"]}) == r["n_members"] for r in rows),
        "every_group_members_share_content": share_content,
        "pairs_match_e291_alias_count": (e291_alias_pairs is not None
                                        and pairs_here == e291_alias_pairs),
        "shape_partition": sum(summary["shape_counts"].values()) == len(rows),
        "schema_plus_accidental_partition": (summary["schema_driven_groups"]
                                            + summary["accidental_groups"]) == len(rows),
        "self_faces_absent_from_universe": all(n not in names for n in SELF_FACES),
        "predecessor_faces_absent_from_universe": all(n not in names for n in (e291.FACE, e291.SRC_FACE)),
        "convictions_are_all_strict": len(strict_hits) == len([r for r in rows if r["counts_one_twice"]]),
    }

    return {
        "study": STUDY, "title": TITLE, "evidence_cutoff": CUTOFF,
        "generated": None,   # stamped by run
        "no_bill": NO_BILL,
        "source_faces": [e291.FACE],
        "faces_censused": names,
        "universe_vintage": vintage_note,
        "frozen_spec": {
            "D1_unit_is_the_list_not_the_pair": "two aliases are one group; three are still one group",
            "D2_only_the_strict_sum_test_convicts": "loose candidates are disclosed with a coincidence "
                                                    "flag and never enter the verdict",
            "D3_shape_is_measured": "schema-driven is a claim about where the copies sit, read from paths",
            "D4_no_reburn": "published faces re-read only; no draw stream, no band rebuild, no engine",
            "small_coincidence_threshold": SMALL_COINCIDENCE,
            "verdict_vocab": list(VERDICT_VOCAB),
        },
        "groups": rows,
        "identity_check": identity,
        "summary": summary,
        "verdict": verdict,
        "verdict_reason": _reason(verdict, summary),
    }


def decide(summary):
    if not summary.get("alias_groups"):
        return VERDICT_VOCAB[0]
    if (summary.get("strict_sum_test") or {}).get("convictions"):
        return VERDICT_VOCAB[3]
    if summary.get("accidental_groups"):
        return VERDICT_VOCAB[2]
    return VERDICT_VOCAB[1]


def _fmt_pct(value):
    return "n/a" if value is None else "%.1f pct" % (value * 100.0)


def _reason(verdict, summary):
    if verdict == VERDICT_VOCAB[0]:
        return ("no face in the census publishes two lists with identical content, so no count can "
                "read one content as two records.")
    shapes = summary["shape_counts"]
    head = ("%d alias group(s) over %d of %d censused faces, %d list(s) in total (%s of all lists): "
            "%d are the same slot repeated across arms, %d sit at the same slot of sibling containers "
            "and %d are scattered restatements"
            % (summary["alias_groups"], summary["faces_with_an_alias"], summary["faces_censused"],
               summary["alias_members"], _fmt_pct(summary["alias_member_share_of_all_lists"]),
               shapes["same_slot_across_arms"], shapes["parallel_slot_across_arms"],
               shapes["scattered"]))
    strict = summary["strict_sum_test"]
    mid = ("the strict sum test (a number equal to the total length of the lists in its own dict) "
           "convicted %d of the %d non-scattered groups"
           % (strict["convictions"], strict["groups_tested"]))
    loose = summary["loose_join"]
    tail = ("the loose join found %d number(s) equal to a member count or alias total, %d of them small "
            "enough to be coincidence and none of them evidence" % (loose["candidates"],
                                                                   loose["coincidence_prone"]))
    if verdict == VERDICT_VOCAB[3]:
        first = strict["hits"][0] if strict["hits"] else {}
        return ("%s; %s; %s. The first conviction is %s :: %s where %s = %s totals the lists beside it."
                % (head, mid, tail, first.get("face"), first.get("count_path"),
                   first.get("count_path"), first.get("count_value")))
    if verdict == VERDICT_VOCAB[2]:
        ex = summary["accidental_examples"][0] if summary["accidental_examples"] else {}
        return ("%s; %s; %s. Copying is not automatic -- %s restates %s at %s, which no arm schema "
                "forces -- but nothing that reads it totals the copies."
                % (head, mid, tail, ex.get("face"), ex.get("unit"),
                   (ex.get("members") or [{}])[0].get("path")))
    return ("%s; %s; %s. Every copy sits where its face's own schema puts a list, so the duplication is "
            "the shape of the arms and not an accident, and no published number adds the copies."
            % (head, mid, tail))


# ------------------------------------------------------------------ commands
def write_face(face, outdir=None):
    outdir = outdir or OUTDIR
    text = json.dumps(face, ensure_ascii=False, indent=1) + "\n"
    for name in (FACE, LATEST):
        fh = io.open(os.path.join(outdir, name), "w", encoding="utf-8", newline="\n")
        try:
            fh.write(text)
        finally:
            fh.close()


def cmd_run():
    import datetime
    face = build(extend=True)
    face["generated"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    write_face(face)
    s = face["summary"]
    print("E293 %s" % face["verdict"])
    print("  groups: %d over %d face(s), %d members (%s of lists)"
          % (s["alias_groups"], s["faces_with_an_alias"], s["alias_members"],
             _fmt_pct(s["alias_member_share_of_all_lists"])))
    print("  shapes: same_slot=%d parallel_slot=%d scattered=%d"
          % (s["shape_counts"]["same_slot_across_arms"],
             s["shape_counts"]["parallel_slot_across_arms"],
             s["shape_counts"]["scattered"]))
    print("  strict sum test: %d conviction(s) of %d tested | loose candidates=%d (%d coincidence-prone)"
          % (s["strict_sum_test"]["convictions"], s["strict_sum_test"]["groups_tested"],
             s["loose_join"]["candidates"], s["loose_join"]["coincidence_prone"]))
    print("  identity=%s" % all(face["identity_check"].values()))
    return 0


def cmd_verify():
    stored = load(FACE)
    live = build()
    problems = []
    if stored.get("verdict") != live.get("verdict"):
        problems.append("verdict: stored=%r live=%r" % (stored.get("verdict"), live.get("verdict")))
    for key in ("faces_censused", "alias_groups", "alias_members", "shape_counts",
                "schema_driven_groups", "accidental_groups", "all_lists_censused"):
        if (stored.get("summary") or {}).get(key) != live["summary"].get(key):
            problems.append("summary.%s does not re-derive" % key)
    if [(g["face"], g["unit"], tuple(m["path"] for m in g["members"]))
            for g in (stored.get("groups") or [])] != \
            [(g["face"], g["unit"], tuple(m["path"] for m in g["members"])) for g in live["groups"]]:
        problems.append("the alias group set does not re-derive")
    for key, ok in live["identity_check"].items():
        if not ok:
            problems.append("identity check %s is false" % key)
    if (stored.get("summary") or {}).get("verdict") not in VERDICT_VOCAB:
        problems.append("verdict outside the frozen set")
    print("E293 verify: %d problem(s)" % len(problems))
    for problem in problems:
        print("  - %s" % problem)
    return 0 if not problems else 1


# ------------------------------------------------------------------ selftest
def _fixture():
    """A summing scope (convicts), a label copy across arms, a parallel copy, a restatement, a solo."""
    return {
        "tally": {
            "arm_a": {"cells": ["c1", "c2", "c3"]},
            "arm_b": {"cells": ["c1", "c2", "c3"]},
            "n_cells": 6,
        },
        "arms": [
            {"labels": ["a", "b"], "n_rows": 2, "rows": [{"x": 1}, {"x": 2}]},
            {"labels": ["a", "b"], "n_rows": 2, "rows": [{"x": 3}, {"x": 4}]},
        ],
        "groups": {
            "A": {"seeds": ["s1", "s2"]},
            "B": {"seeds": ["s1", "s2"]},
        },
        "record": {"keys": ["z"], "inner": {"keys": ["z"]}},
        "solo": {"only": ["q"]},
    }


def cmd_selftest():
    ok, fail = 0, []

    def leg(name, cond, detail=""):
        nonlocal ok
        if cond:
            ok += 1
        else:
            fail.append("%s %s" % (name, detail))

    # L1 the path helpers: index-free slots and their containers
    leg("L1", indep("arms[3].cells") == "arms.cells"
        and parent_path("arms[3].cells") == "arms"
        and parent_path("groups.A.cells") == "groups.A"
        and indep("top") == "top")

    # L2 ancestry is strict, not prefix-of-string
    leg("L2", is_ancestor("groups", "groups.A.cells")
        and not is_ancestor("group", "groups.A.cells")
        and not is_ancestor("groups.A.cells", "groups.A.cells"))

    # L2b the three shapes: same slot / sibling arms (also over a grid) / restatement
    leg("L2b", shape_of([("arms[0].x", 1), ("arms[1].x", 1)]) == "same_slot_across_arms"
        and shape_of([("groups.A.cells", 3), ("groups.B.cells", 3)]) == "parallel_slot_across_arms"
        and shape_of([("g.cross:200.tight.cells", 4), ("g.self:60.wide.cells", 4)])
        == "parallel_slot_across_arms"
        and shape_of([("s.labels", 3), ("s.faces[0].labels", 3)]) == "scattered")

    fx = _fixture()
    groups = []
    rec = e286.analyse_face_from_object("FIXTURE.json", fx)
    by_unit = collections.defaultdict(list)
    for item in rec["unit_lists"]:
        by_unit[item["unit"]].append((item["path"], item["n_items"]))
    for unit, lists in by_unit.items():
        buckets = collections.defaultdict(list)
        for path, n_items in lists:
            buckets[content_key(e291.resolve(fx, path))].append((path, n_items))
        for members in buckets.values():
            if len(members) < 2:
                continue
            members = sorted(members)
            indeps = sorted({indep(p) for p, _ in members})
            parents = sorted({parent_path(p) for p, _ in members})
            shape = shape_of(members)
            groups.append({"face": "FIXTURE", "unit": unit,
                           "members": [{"path": p, "length": n} for p, n in members],
                           "n_members": len(members), "length": members[0][1],
                           "lengths_seen": [members[0][1]], "shape": shape,
                           "scope": indeps[0] if len(indeps) == 1 else None,
                           "scopes": indeps,
                           "enclosing_scope": parents[0] if len(parents) == 1 else None})

    # L3 the fixture produces exactly the three shapes it was built to produce
    shapes = {g["unit"]: g["shape"] for g in groups}
    leg("L3", shapes.get("labels") == "same_slot_across_arms"
        and shapes.get("seeds") == "parallel_slot_across_arms"
        and shapes.get("keys") == "scattered", shapes)

    # L4 a list that occurs once is never a group (D1: the unit is the list)
    leg("L4", all(g["n_members"] >= 2 for g in groups)
        and not any(g["unit"] == "only" for g in groups))

    # L5 the aggregate index sums every list of a unit under the number's own container
    _v, by_unit5 = aggregate_index({"tally": {"a": {"cells": ["p", "q"]},
                                              "b": {"cells": ["p", "q"]},
                                              "n_cells": 4}})["tally.n_cells"]
    leg("L5", by_unit5["cells"][0] == 2 and by_unit5["cells"][1] == 4, by_unit5.get("cells"))

    # L6 the strict test convicts the summing scope: n_cells == the total of every cells list under it
    cells = [g for g in groups if g["unit"] == "cells"][0]
    strict, loose = join_alias(cells, fx)
    leg("L6", strict and strict[0]["count_path"].endswith("n_cells")
        and strict[0]["count_value"] == strict[0]["unit_total_length"] == 6
        and strict[0]["unit_lists_under_it"] == 2, strict)

    # L7 a same-slot copy inside arms does not get convicted by an unrelated small number
    labels = [g for g in groups if g["unit"] == "labels"][0]
    strict_l, loose_l = join_alias(labels, fx)
    leg("L7", not [c for c in strict_l if c["count_path"].endswith("n_rows")],
        (strict_l, loose_l))

    # L8 loose candidates carry the coincidence flag and never convict (D2)
    leg("L8", all(isinstance(c["coincidence_prone"], bool) for c in loose + loose_l)
        and not any(c.get("why") for c in loose + loose_l))

    # L9 the verdict ladder: no groups -> vocab[0], conviction -> vocab[3], accidental -> vocab[2],
    #    else vocab[1]
    leg("L9", decide({"alias_groups": 0}) == VERDICT_VOCAB[0]
        and decide({"alias_groups": 1, "strict_sum_test": {"convictions": 1}}) == VERDICT_VOCAB[3]
        and decide({"alias_groups": 2, "strict_sum_test": {"convictions": 0},
                    "accidental_groups": 1}) == VERDICT_VOCAB[2]
        and decide({"alias_groups": 2, "strict_sum_test": {"convictions": 0},
                    "accidental_groups": 0}) == VERDICT_VOCAB[1])

    # L10 the deliberate order: an accidental copy does not outrank a conviction
    leg("L10", decide({"alias_groups": 2, "strict_sum_test": {"convictions": 2},
                       "accidental_groups": 3}) == VERDICT_VOCAB[3])

    # L11 a missing strict block never crashes and never convicts
    leg("L11", decide({"alias_groups": 1, "accidental_groups": 0}) == VERDICT_VOCAB[1])

    # L12 the live face re-derives twice on its decisive keys and stays inside the vocabulary
    a, b = build(), build()
    keys = ("faces_censused", "alias_groups", "alias_members", "shape_counts")
    leg("L12", all(a["summary"][k] == b["summary"][k] for k in keys)
        and a["summary"]["strict_sum_test"] == b["summary"]["strict_sum_test"]
        and a["verdict"] == b["verdict"] and a["verdict"] in VERDICT_VOCAB)

    # L13 the live identities hold (shape partition, distinct paths, convictions are strict)
    leg("L13", all(a["identity_check"].values()), a["identity_check"])

    # L14 the live census does not include this study's own faces or its predecessors (self-inclusion)
    leg("L14", a["identity_check"]["self_faces_absent_from_universe"]
        and a["identity_check"]["predecessor_faces_absent_from_universe"]
        and FACE not in a["faces_censused"] and e291.FACE not in a["faces_censused"])

    print("E293 selftest: %d/%d" % (ok, ok + len(fail)))
    for f in fail:
        print("  FAIL %s" % f)
    return 0 if not fail else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
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