"""E397 -- which names are ambiguous only outside the census walk?

E385 priced the merged-key split per PAIR and found that 2 of 7 guard pairs on an ambiguous key are
settled by naming the one member the census walk can see, while 5 stay ambiguous.  It also published
``merged_names_whose_ambiguity_is_only_outside_the_walk = 0``, which is a strong claim about the
instrument and was never tested per NAME over the whole key population.

So ask it per name:

  * the population is every key the census publishes -- the read half (``e350.measure``'s
    ``faces_named``) union the write half (``e383.keyed_sites``'s dump sinks);
  * a key is resolved by the same suffix index E383/E385 use, so one spelling is never two files;
  * every resolved file is tested against BOTH census walk rules in the tree as they stand:
    E350/E353/E377's corpus drops whole top-level trees (``Money02``, ``legacy``, ``media``,
    ``Money0923``) while E391's ``py_corpus`` drops path PARTS anywhere (``.git``, ``__pycache__``,
    ``_quarantine``, ``node_modules``, ``.codely-cli``, ``_smoke``);
  * a name whose file set collapses to fewer than two files under a rule is ambiguous only because
    the resolver is wider than that walk -- that is the repair list, and the repair is a rule, not
    an edit;
  * a name that keeps two or more files under every rule is ambiguous in the DATA; naming a member
    there is a decision (E385's 5-of-7), and it is published as such rather than repaired.

The bill is the per-name list plus the rule that would make the key set agree with the corpus, not a
count.  No published face is rewritten and no pointer is edited.

Usage:
  python scripts/e397_walk_ambiguity.py run       # build the face
  python scripts/e397_walk_ambiguity.py verify    # re-derive every row from the tree
  python scripts/e397_walk_ambiguity.py selftest  # offline fixture legs
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

import e347_published_number_gate_census as e347  # noqa: E402
import e350_field_branch_census as e350  # noqa: E402
import e383_shared_key_collision as e383  # noqa: E402

TODAY = "2026-11-03"
FACE = "WALKAMBIG-%s.json" % TODAY
LATEST = "walkambig_latest.json"
PUBLISHED_DIR = os.path.join(ROOT, "results", "state_tilt")
STUDY = "E397_walk_ambiguity"
SELF_REL = "scripts/e397_walk_ambiguity.py"
OWN_FILES = (FACE, LATEST)
SIBLING_FACE = "SPLITPRICE-%s.json" % TODAY

# The two walk rules the tree actually contains.  ``top`` drops whole trees; ``part`` drops any
# path component anywhere.  They are not the same corpus, and that is the point: a name near an
# excluded tree is classified differently depending on which instrument reads it.
WALKS = {
    "e350_e353_e377": ("top", ("Money02", "legacy", "media", "Money0923")),
    "e391_py_corpus": ("part", (".git", "__pycache__", "_quarantine", "node_modules",
                                ".codely-cli", "_smoke")),
}

STATE_NONE = "no_file_inside_the_walk"
STATE_ONE = "exactly_one_file_inside_the_walk"
STATE_MANY = "two_or_more_files_inside_the_walk"

CLASS_UNIQUE = "unique_or_unresolved"
CLASS_COLLAPSES = "ambiguity_collapses_under_every_walk"
CLASS_SURVIVES = "ambiguity_survives_every_walk"
CLASS_DEPENDENT = "ambiguity_depends_on_which_walk_you_use"

V_DATA = ("every_ambiguous_name_keeps_at_least_two_files_inside_every_walk_so_the_ambiguity_is_the_"
          "data_and_naming_a_member_is_a_decision_not_a_cleanup")
V_WALK = ("every_ambiguous_name_collapses_to_a_single_file_once_a_walk_rule_is_applied_so_the_"
          "ambiguity_is_the_resolvers_and_the_repair_is_a_skip_rule")
V_MIXED = ("some_names_collapse_under_a_walk_rule_and_some_keep_two_files_inside_it_so_the_repair_"
           "list_and_the_decision_list_must_be_published_separately")
V_EMPTY = "no_key_in_the_population_was_resolved_so_no_claim_is_made"


def say(message):
    print(message, flush=True)


# --------------------------------------------------------------------------- walk rules

def in_walk(path, walk):
    """Is ``path`` inside the corpus that walk reads?"""
    kind, exclusions = WALKS[walk]
    parts = [p for p in (path or "").replace("\\", "/").split("/") if p]
    if not parts:
        return False
    if kind == "top":
        return parts[0] not in exclusions
    return not any(p in exclusions for p in parts)


def walk_state(files, walk):
    inside = [f for f in files if in_walk(f, walk)]
    if not inside:
        return STATE_NONE, []
    if len(inside) == 1:
        return STATE_ONE, inside
    return STATE_MANY, inside


def classify(files, walks=None):
    """The joint class of one name's resolved file set, and the per-walk states behind it."""
    walks = walks or sorted(WALKS)
    states = {}
    inside = {}
    for walk in walks:
        state, members = walk_state(files, walk)
        states[walk] = state
        inside[walk] = members
    if len(files) <= 1:
        klass = CLASS_UNIQUE
    else:
        many = sum(1 for s in states.values() if s == STATE_MANY)
        if many == len(states):
            klass = CLASS_SURVIVES
        elif many == 0:
            klass = CLASS_COLLAPSES
        else:
            klass = CLASS_DEPENDENT
    return klass, states, inside


def outside_tops(files, walk="e350_e353_e377"):
    """Which top-level trees hold the files this walk cannot see -- the candidate skip rule."""
    tops = {}
    for f in files:
        if in_walk(f, walk):
            continue
        top = f.split("/")[0]
        tops[top] = tops.get(top, 0) + 1
    return tops


# --------------------------------------------------------------------------- population

def population(sources=None):
    """Every key the census publishes: the read half union the write half.

    The read half must be E350's ``faces_named`` exactly, but its ``measure()`` also builds a parent
    map per source for the read rows, and that table is what a low-memory host runs out of room on
    (r1414 family).  The key set is a function of the two binding helpers alone, so they are called
    here directly and the row walk is skipped -- same set, one tree live at a time.
    """
    if sources is None:
        sources = e350._sources()
    named = set()
    keyed = {}
    parsed = 0
    write_rows = 0
    for relpath, text in sources:
        tree = e347.parse(text)
        if tree is None:
            continue
        parsed += 1
        consts = e347.constants(tree)
        bindings, _unresolved = e350._face_bindings(tree, consts)
        sinks = e350._dump_sinks(tree, consts)
        named |= {f for v in bindings.values() for f in v}
        named |= {f for v in sinks.values() for f in v}
        for row in e347.load_bindings(tree, consts):
            e383._add(keyed, relpath, row["line"], e383.ROLE_READ, row["values"])
        for line, values in e383._dump_rows(tree, consts):
            write_rows += 1
            e383._add(keyed, relpath, line, e383.ROLE_WRITE, values)
    write_keys = set(keyed)
    return {
        "keys": sorted(named | write_keys),
        "read_half": sorted(named),
        "write_only": sorted(write_keys - named),
        "sources": len(sources),
        "parsed": parsed,
        "write_rows": write_rows,
    }


def key_row(key):
    norm = e383._norm(key or "")
    files = e383._resolve(norm)
    klass, states, inside = classify(files)
    row = {
        "key": key,
        "n_files": len(files),
        "files": files[:8],
        "files_truncated": max(0, len(files) - 8),
        "states_by_walk": states,
        "class": klass,
    }
    if klass in (CLASS_COLLAPSES, CLASS_DEPENDENT):
        row["outside_the_stricter_walk"] = outside_tops(files)
        survivors = sorted({f for members in inside.values() for f in members})
        row["files_any_walk_keeps"] = survivors[:8]
    return row


# --------------------------------------------------------------------------- the rule

def rule_from(rows):
    """The skip rule that would make the key set agree with the corpus.

    Two things can be said with the data in hand and nothing more: which top-level trees carry the
    files only one walk can see, and whether adding them to the resolver would collapse any name.
    A tree that appears here but explains no collapse is a corpus question, not a key question.
    """
    tops = {}
    for row in rows:
        if row["class"] == CLASS_UNIQUE:
            continue
        for top, count in row.get("outside_the_stricter_walk", {}).items():
            tops[top] = tops.get(top, 0) + 1
    collapses = [r["key"] for r in rows if r["class"] == CLASS_COLLAPSES]
    dependent = [r["key"] for r in rows if r["class"] == CLASS_DEPENDENT]
    if collapses:
        sentence = ("the repair is a skip rule: %d name(s) collapse to one file once the walk's own "
                    "exclusion is applied, so the resolver must not see %s"
                    % (len(collapses), ", ".join(sorted(tops)) or "nothing"))
    elif dependent:
        sentence = ("the two walks disagree on %d name(s) but neither exclusion collapses them, so "
                    "the corpus must pick ONE skip set (the union) before any key count is compared "
                    "across instruments" % len(dependent))
    else:
        sentence = ("no exclusion explains any ambiguity: every ambiguous name keeps two or more "
                    "files inside both walks, so the key set and the corpus already agree and the "
                    "ambiguity is real")
    return {
        "tops_holding_files_only_one_walk_sees": tops,
        "names_the_rule_would_collapse": collapses[:20],
        "names_whose_class_depends_on_the_walk": dependent[:20],
        "walk_disagreement_count": len(dependent),
        "sentence": sentence,
    }


def decide(summary):
    """The verdict is recomputed from the summary, never written by hand."""
    if not summary.get("keys_total"):
        return V_EMPTY
    collapses = summary.get("names_ambiguous_only_because_the_resolver_is_wider") or 0
    survives = summary.get("names_ambiguous_inside_every_walk") or 0
    if collapses and survives:
        return V_MIXED
    if collapses:
        return V_WALK
    if survives:
        return V_DATA
    return V_EMPTY


def sibling_check(ambiguous_rows):
    """Compare the merged-name set with E385's published one on the same cutoff (r1225 family)."""
    path = os.path.join(PUBLISHED_DIR, SIBLING_FACE)
    if not os.path.exists(path):
        return {"available": False, "why": "sibling face %s is absent" % SIBLING_FACE}
    with open(path, "r", encoding="utf-8") as fh:
        sib = json.load(fh)
    published_rows = []
    for arm in sib.get("arms") or []:
        published_rows.extend(r for r in (arm.get("merged_rows") or []) if "key" in r)
    published = {r["key"] for r in published_rows}
    mine = {r["key"] for r in ambiguous_rows}
    return {
        "available": True,
        "sibling": SIBLING_FACE,
        "same_cutoff": sib.get("evidence_cutoff") == TODAY,
        "published_merged_names": len(published),
        "recomputed_merged_names": len(mine),
        "published_not_recomputed": sorted(published - mine)[:10],
        "recomputed_not_published": sorted(mine - published)[:10],
        "agree": published == mine,
    }


# --------------------------------------------------------------------------- build / verify

def build(write_face=True, sources=None):
    say("resolving the published key population")
    pop = population(sources)
    keys = pop["keys"]
    say("keys=%d (read half %d, write-only %d)"
        % (len(keys), len(pop["read_half"]), len(pop["write_only"])))

    rows = [key_row(k) for k in keys]
    ambiguous = [r for r in rows if r["n_files"] > 1]
    say("ambiguous_in_resolver=%d" % len(ambiguous))

    by_class = {}
    for row in rows:
        by_class[row["class"]] = by_class.get(row["class"], 0) + 1

    per_walk = {}
    for walk in sorted(WALKS):
        per_walk[walk] = {
            "names_with_two_or_more_files_inside": sum(
                1 for r in rows if r["states_by_walk"][walk] == STATE_MANY),
            "names_with_exactly_one_file_inside": sum(
                1 for r in rows if r["states_by_walk"][walk] == STATE_ONE),
            "names_with_no_file_inside": sum(
                1 for r in rows if r["states_by_walk"][walk] == STATE_NONE),
        }

    rule = rule_from(rows)
    collapses = [r for r in rows if r["class"] == CLASS_COLLAPSES]
    survives = [r for r in rows if r["class"] == CLASS_SURVIVES]
    dependent = [r for r in rows if r["class"] == CLASS_DEPENDENT]

    summary = {
        "keys_total": len(rows),
        "keys_read_half": len(pop["read_half"]),
        "keys_write_only": len(pop["write_only"]),
        "names_resolved_to_no_file": sum(1 for r in rows if r["n_files"] == 0),
        "names_unique": sum(1 for r in rows if r["n_files"] == 1),
        "names_ambiguous_in_the_resolver": len(ambiguous),
        "names_ambiguous_only_because_the_resolver_is_wider": len(collapses),
        "names_ambiguous_inside_every_walk": len(survives),
        "names_whose_class_depends_on_the_walk": len(dependent),
        "by_class": by_class,
        "per_walk": per_walk,
        "classes_sum_to_the_population": sum(by_class.values()) == len(rows),
        "corpus_sources": pop.get("sources"),
        "corpus_parsed": pop.get("parsed"),
    }
    summary["verdict"] = decide(summary)
    face = {
        "study": STUDY,
        "evidence_cutoff": TODAY,
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "source": SELF_REL,
        "walks": {k: {"kind": v[0], "exclusions": list(v[1])} for k, v in WALKS.items()},
        "summary": summary,
        "verdict": summary["verdict"],
        "rule": rule,
        "repair_list": [{"key": r["key"], "n_files": r["n_files"], "files": r["files"],
                         "files_any_walk_keeps": r.get("files_any_walk_keeps", [])}
                        for r in collapses[:60]],
        "undecided_inside_every_walk": [{"key": r["key"], "n_files": r["n_files"],
                                         "files": r["files"][:6],
                                         "files_inside": r["states_by_walk"]}
                                        for r in survives[:60]],
        "walk_dependent": [{"key": r["key"], "n_files": r["n_files"],
                            "states_by_walk": r["states_by_walk"]}
                           for r in dependent[:60]],
        "sibling_check": sibling_check(ambiguous),
        "bounds": {
            "measured": ("each published key resolved to files and tested against both walk rules "
                         "in the tree; the classes are functions of the resolved sets"),
            "not_measured": ("whether a consumer of an ambiguous name reads the member it meant "
                             "(E383's consumer table); the corpus content of the excluded trees"),
            "no_rewrites": "no published face and no pointer is edited here",
        },
    }
    say("verdict: %s" % summary["verdict"])
    if write_face:
        _write(face)
    return face


def _write(face):
    os.makedirs(PUBLISHED_DIR, exist_ok=True)
    for name in (FACE, LATEST):
        path = os.path.join(PUBLISHED_DIR, name)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
    say("wrote %s and %s" % (FACE, LATEST))


def verify():
    """Re-derive every published row from the tree as it stands."""
    problems = []
    path = os.path.join(PUBLISHED_DIR, FACE)
    if not os.path.exists(path):
        say("verify problems=['face is absent']")
        return ["face is absent"]
    with open(path, "r", encoding="utf-8") as fh:
        face = json.load(fh)
    summary, rule = face["summary"], face["rule"]
    if face.get("evidence_cutoff") != TODAY:
        problems.append("evidence_cutoff moved")
    by_class = summary.get("by_class") or {}
    total = sum(by_class.values())
    if total != summary.get("keys_total"):
        problems.append("classes sum to %d but the population is %d"
                        % (total, summary.get("keys_total")))
    if sum(v for k, v in by_class.items() if k != CLASS_UNIQUE) != (
            summary.get("names_ambiguous_only_because_the_resolver_is_wider")
            + summary.get("names_ambiguous_inside_every_walk")
            + summary.get("names_whose_class_depends_on_the_walk")):
        problems.append("the three ambiguity classes do not sum to the published counts")
    for group in ("repair_list", "undecided_inside_every_walk", "walk_dependent"):
        for row in face.get(group) or []:
            files = e383._resolve(e383._norm(row["key"]))
            if len(files) != row["n_files"]:
                problems.append("%s/%s: n_files %d but the tree resolves %d"
                                % (group, row["key"], row["n_files"], len(files)))
            klass, states, _inside = classify(files)
            expected = {"repair_list": CLASS_COLLAPSES,
                        "undecided_inside_every_walk": CLASS_SURVIVES,
                        "walk_dependent": CLASS_DEPENDENT}[group]
            if klass != expected:
                problems.append("%s/%s: class is %s, not %s"
                                % (group, row["key"], klass, expected))
            if "states_by_walk" in row and row["states_by_walk"] != states:
                problems.append("%s/%s: per-walk states do not re-derive" % (group, row["key"]))
    if rule.get("walk_disagreement_count") != summary.get("names_whose_class_depends_on_the_walk"):
        problems.append("the rule's disagreement count is not the summary's")
    if decide(summary) != face.get("verdict"):
        problems.append("the decision gate does not re-derive the published verdict")
    say("verify problems=%s" % (problems or "[]"))
    return problems


# --------------------------------------------------------------------------- selftest

def selftest():
    legs = []

    def leg(name, ok, note=""):
        legs.append((name, bool(ok), note))

    inside_a = "results/trial_labor_w1/judge_state.json"
    inside_b = "results/trial_labor_w2/judge_state.json"
    outside_top = "Money0923/results/judge_state.json"
    quarantine = "results/_quarantine/judge_state.json"

    # 1. the two rules are not the same corpus
    leg("top_rule_drops_the_tree", not in_walk(outside_top, "e350_e353_e377"))
    leg("top_rule_keeps_a_quarantined_file", in_walk(quarantine, "e350_e353_e377"))
    leg("part_rule_drops_the_quarantine", not in_walk(quarantine, "e391_py_corpus"))
    leg("part_rule_keeps_the_money_tree", in_walk(outside_top, "e391_py_corpus"))

    # 2. the joint class is a function of the resolved set, not of the key name
    k, states, _ = classify([inside_a])
    leg("one_file_is_unique", k == CLASS_UNIQUE and states["e350_e353_e377"] == STATE_ONE)
    k, states, _ = classify([inside_a, inside_b])
    leg("two_inside_files_survive", k == CLASS_SURVIVES
        and all(s == STATE_MANY for s in states.values()))
    k, states, _ = classify([inside_a, outside_top])
    leg("a_walk_dependent_name_is_not_a_collapse", k == CLASS_DEPENDENT
        and states["e350_e353_e377"] == STATE_ONE
        and states["e391_py_corpus"] == STATE_MANY)
    k, states, _ = classify([outside_top, quarantine])
    leg("a_name_both_walks_drop_collapses", k == CLASS_COLLAPSES
        and states["e350_e353_e377"] == STATE_ONE and states["e391_py_corpus"] == STATE_ONE)
    k, _states, _ = classify([inside_a, quarantine])
    leg("a_walk_dependent_name_flips", k == CLASS_DEPENDENT)

    # 3. an empty walk is its own state, never folded into "one"
    state, members = walk_state([outside_top, "Money0923/other/x.json"], "e350_e353_e377")
    leg("nothing_inside_is_its_own_state", state == STATE_NONE and members == [])

    # 4. the skip rule names the trees that hold the files a walk cannot see
    tops = outside_tops([inside_a, outside_top, "legacy/x.json"])
    leg("outside_tops_counts_the_trees", tops.get("Money0923") == 1 and tops.get("legacy") == 1
        and "results" not in tops)

    # 5. the decision gate is a function of the summary
    leg("decide_data", decide({"keys_total": 10, "names_ambiguous_inside_every_walk": 3}) == V_DATA)
    leg("decide_walk", decide({"keys_total": 10,
                               "names_ambiguous_only_because_the_resolver_is_wider": 2}) == V_WALK)
    leg("decide_mixed", decide({"keys_total": 10,
                                "names_ambiguous_only_because_the_resolver_is_wider": 1,
                                "names_ambiguous_inside_every_walk": 1}) == V_MIXED)
    leg("decide_empty", decide({}) == V_EMPTY)

    # 6. the tree today really carries a shared name, so the apparatus is not answering a vacuum
    files = e383._resolve("judge_state.json")
    leg("the_tree_has_a_shared_name", len(files) >= 2, "judge_state.json -> %d" % len(files))

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
        summary = face["summary"]
        say("of %d keys, %d are ambiguous: %d collapse under a walk rule, %d survive every walk, "
            "%d depend on which walk you use"
            % (summary["keys_total"], summary["names_ambiguous_in_the_resolver"],
               summary["names_ambiguous_only_because_the_resolver_is_wider"],
               summary["names_ambiguous_inside_every_walk"],
               summary["names_whose_class_depends_on_the_walk"]))
        return 0
    if cmd == "verify":
        return 0 if not verify() else 1
    if cmd == "selftest":
        return selftest()
    say("usage: e397_walk_ambiguity.py [run|verify|selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))