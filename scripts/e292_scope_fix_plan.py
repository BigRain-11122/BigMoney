"""E292 -- is the "move the count into the scope that already publishes its unit" fix cheap?

E290 measured the shape of the 27 checkable counts and then priced the un-derivable half as WORK:
301 rows (over 299 distinct scopes) whose face already publishes a list of the unit the count's name
claims, and 566 rows whose face publishes no records of that unit at all.  The 301 were handed on as
"move the count, no new data needed".

That sentence is a plan, and a plan can be priced.  Nothing here draws or rebuilds: every number is
read off a published face.

  (1) VERIFY THE PREMISE.  For each of the 301 rows, is there really a list of exactly the claimed unit
      in that face, and does it resolve to a list?  A row whose unit is named but published nowhere is
      evidence against the premise and is published as such, never dropped.
  (2) NAME THE FIX SHAPE.  The shapes are not the same job:
        move_count        - the key is qualified (n_<unit> / <unit>_count) and exactly one list of that
                            unit exists: relocating the count beside it is a naming change;
        choice_required   - the unit is published as a list in more than one scope, so the author must
                            choose which collection the count counts -- a move is under-determined;
        needs_own_records - the key IS the unit name (bare), so no sibling list of that name can ever
                            exist in the same parent: the scope has to publish its own records;
        mirror_copy       - the target scope already carries this key with the same value (one move
                            carried twice, not two gains);
        collision         - the target scope already carries this key with a different value;
        premise_fails     - no list of the claimed unit resolves in this face.
  (3) MEASURE WHAT THE MOVE WOULD BUY -- AND WHERE IT LANDS.  A move buys auditability only if the
      count also agrees with the list it lands beside.  But agreement is not enough: the list must be
      the SAME COLLECTION.  So every single-target row publishes the relation between its own scope and
      the list's scope, and the two kinds of agreement are never added together:
        agreement in a related scope (same / ancestor / descendant) = a plausible move;
        agreement in a foreign scope (face root / unrelated subtree)  = coincidence-prone, and priced
        as such -- a one-element list agrees with every count that happens to be 1, which is what 126 of
        the 138 agreements turn out to be.
  (4) DEDUPE BEFORE RANKING.  A target scope may already hold the row's key: same key + same value is
      one move carried twice; same key + different value is a collision, published, not merged.
  (5) RANK BY GAIN PER MOVE.  Per face: related-scope clean counts / distinct target scopes, then the
      foreign agreements, then the convictions.  Raw row counts are never the ranking key.

DECISION RULE, declared before any number is read:

  D1  THE PLAN IS READ OFF THE PUBLISHED FACES AND THE CENSUS IS IMPORTED.  Which counts are
      un-derivable comes from E286 (never re-implemented); every scope, length and value comes from the
      published face object.  The face also joins E290's published pair (301 rows / 299 scopes) as an
      identity check, so this plan cannot quietly describe a different census.
  D2  THE PREMISE IS CHECKED, NOT ASSUMED.  A row is only priced as moveable when a list of exactly the
      claimed unit exists in the same face and resolves to a list.  Failures are published.
  D3  AGREEMENT IS MEASURED AND SO IS ITS SCOPE.  Every single-target row publishes its value against
      the candidate list's length AND the relation between the two scopes.  An agreement in a scope
      that has nothing to do with the count's own scope is published as its own bucket, with the share
      of those whose target list holds at most one item.
  D4  A MOVE MUST BE UNIQUE AND COLLISION-FREE.  More than one candidate scope = a choice, not a move.
      A target scope that already carries the row's key is a mirror (same value, one move) or a
      collision (different value), never silently absorbed.
  D5  RANKING IS GAIN PER MOVE.  Per face: related-scope clean counts / distinct target scopes, then
      foreign agreements, then convictions, then face name.
  D6  NO REBURN.  Published faces are re-read; no draw stream, no band rebuild, no engine, no verdict
      about the market.

Verdict vocabulary (frozen):
  the_cheap_naming_fix_is_cheap_and_every_moveable_count_would_agree_with_the_list_it_moves_beside
  the_naming_fix_is_mostly_clean_but_a_minority_would_publish_a_new_disagreement
  most_elsewhere_rows_need_a_choice_because_their_unit_is_published_in_more_than_one_scope
  most_elsewhere_rows_are_bare_unit_names_so_the_cheap_move_does_not_exist_for_them
  the_elsewhere_scope_premise_does_not_hold_no_move_lands_in_a_scope_related_to_the_count

V4 was added after the first build of this face, and the disclosure is deliberate: the first run
reported 126 clean moves and 75 convictions, all of them scored without asking where the candidate list
lives.  Adding the scope relation showed that those 126 agreements come from lists of one element in
unrelated subtrees and that no row at all lands beside a list in its own scope -- the vocabulary as
declared could not describe the data it met, so the missing case was named and the original counts are
reproduced in `frozen_spec.vocab_amendment` rather than dropped.

Usage:  python scripts/e292_scope_fix_plan.py run|verify|selftest
"""
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e286_count_field_scope as e286          # noqa: E402  (the census this plan is a plan OVER)
import e_band_family_vintage as vintage        # noqa: E402  (universe vintage freeze, E292)

ROOT = e286.ROOT
OUTDIR = e286.OUTDIR

STUDY = "E292_scope_fix_plan"
TITLE = ("the 301 un-derivable counts whose face already publishes their unit were handed on as "
         "'move the count' -- how many of those moves exist, where they would land, and how many would "
         "agree with the list they land beside")
CUTOFF = "2026-10-29"
SRC_FACE = "BANDCOUNTSCOPE-%s.json" % CUTOFF      # E286: the census being planned over
PROFILE_FACE = "BANDSELFAUDIT-%s.json" % CUTOFF    # E290: publishes the 301 / 299 headline
FACE = "BANDSCOPEFIX-%s.json" % CUTOFF
LATEST = "bandscopefix_latest.json"
SELF_FACES = (FACE, LATEST)

SHAPE_CLEAN = "move_count_clean"
SHAPE_FOREIGN = "move_count_clean_foreign_scope"
SHAPE_CONVICT = "move_count_would_convict"
SHAPE_CHOICE = "choice_required"
SHAPE_OWN = "needs_own_records"
SHAPE_MIRROR = "mirror_copy"
SHAPE_COLLIDE = "collision"
SHAPE_PREMISE = "premise_fails"
SHAPES = (SHAPE_CLEAN, SHAPE_FOREIGN, SHAPE_CONVICT, SHAPE_CHOICE, SHAPE_OWN, SHAPE_MIRROR,
          SHAPE_COLLIDE, SHAPE_PREMISE)
MOVE_SHAPES = (SHAPE_CLEAN, SHAPE_FOREIGN, SHAPE_CONVICT)
RELATED_SCOPES = ("same_scope", "ancestor_scope", "descendant_scope")

VERDICT_VOCAB = (
    "the_cheap_naming_fix_is_cheap_and_every_moveable_count_would_agree_with_the_list_it_moves_beside",
    "the_naming_fix_is_mostly_clean_but_a_minority_would_publish_a_new_disagreement",
    "most_elsewhere_rows_need_a_choice_because_their_unit_is_published_in_more_than_one_scope",
    "most_elsewhere_rows_are_bare_unit_names_so_the_cheap_move_does_not_exist_for_them",
    "the_elsewhere_scope_premise_does_not_hold_no_move_lands_in_a_scope_related_to_the_count",
)

NO_BILL = ("measurement only: the dated BAND faces are re-read and their own published counts, lists "
           "and scopes are compared. No draw stream is drawn, no band rebuilt, no engine runs, no "
           "verdict about the market. A verdict here is a statement about a proposed edit to a "
           "published face.")


# ------------------------------------------------------------------ io / paths
def load(name, outdir=None):
    return e286.load(name, outdir)


def resolve(obj, path):
    """Resolve a dotted path with [i] indices to its object; raises on any miss."""
    node = obj
    for chunk in str(path).split("."):
        while True:
            head, _, rest = chunk.partition("[")
            if head:
                node = node[head]
            if not rest:
                break
            idx, _, chunk = rest.partition("]")
            node = node[int(idx)]
            chunk = chunk.lstrip(".")
            if not chunk:
                break
    return node


def parent_path(path):
    return str(path).rsplit(".", 1)[0] if "." in str(path) else ""


def scope_relation(row_parent, target_scope):
    """How the candidate list's own scope sits relative to the count's own scope."""
    rp, tp = str(row_parent), str(target_scope)
    if rp == tp:
        return "same_scope"
    if tp and rp.startswith(tp + "."):
        return "ancestor_scope"
    if tp.startswith(rp + ".") and rp:
        return "descendant_scope"
    if not tp:
        return "face_root"
    return "unrelated_scope"


def lists_by_unit(rec):
    out = {}
    for item in rec.get("unit_lists") or []:
        out.setdefault(item["unit"], []).append(item["path"])
    return out


# ------------------------------------------------------------------ price one row (D2/D3/D4)
def plan_row(rec, obj, field, cands):
    """One of the 301 rows, priced: what fix shape it has, where a move would land, what it buys."""
    unit = field["claimed_unit"]
    key = field["key"]
    value = field["published_value"]
    row_parent = parent_path(field["path"])
    toks = e286.tokens(key)
    bare = toks == [unit]
    row = {
        "face": rec["face"],
        "path": field["path"],
        "key": key,
        "claimed_unit": unit,
        "published_value": value,
        "bare_unit_key": bare,
        "n_candidate_scopes": len(cands),
        "candidate_paths": list(cands[:4]),
        "target_path": None,
        "target_scope": None,
        "target_list_length": None,
        "target_is_degenerate": None,
        "target_records_are_dicts": None,
        "target_matches_value": None,
        "scope_relation": None,
        "target_holds_this_key": None,
        "target_key_value": None,
        "fix_shape": None,
    }

    if bare:
        # D2/D4: a bare `<unit>` int cannot have a sibling list of the same name in the same parent,
        # so no relocation exists -- the scope must publish records of its own.
        row["fix_shape"] = SHAPE_OWN
        if cands:
            row["target_path"] = cands[0]
            row["target_scope"] = parent_path(cands[0])
            row["scope_relation"] = scope_relation(row_parent, row["target_scope"])
            try:
                lst = resolve(obj, cands[0])
            except (KeyError, IndexError, TypeError, ValueError):
                lst = None
            if isinstance(lst, list):
                row["target_list_length"] = len(lst)
                row["target_is_degenerate"] = len(lst) <= 1
                row["target_matches_value"] = bool(value == len(lst))
        return row

    if not cands:
        row["fix_shape"] = SHAPE_PREMISE
        return row
    if len(cands) > 1:
        row["fix_shape"] = SHAPE_CHOICE
        return row

    target = cands[0]
    row["target_path"] = target
    row["target_scope"] = parent_path(target)
    row["scope_relation"] = scope_relation(row_parent, row["target_scope"])
    try:
        lst = resolve(obj, target)
    except (KeyError, IndexError, TypeError, ValueError):
        row["fix_shape"] = SHAPE_PREMISE
        return row
    if not isinstance(lst, list):
        row["fix_shape"] = SHAPE_PREMISE
        return row
    row["target_list_length"] = len(lst)
    row["target_is_degenerate"] = len(lst) <= 1
    row["target_matches_value"] = bool(value == len(lst))
    row["target_records_are_dicts"] = bool(lst) and all(isinstance(x, dict) for x in lst)

    try:
        holder = resolve(obj, row["target_scope"]) if row["target_scope"] else obj
    except (KeyError, IndexError, TypeError, ValueError):
        holder = None
    if isinstance(holder, dict) and key in holder:
        row["target_holds_this_key"] = True
        row["target_key_value"] = holder[key]
        # D4: same key + same value = the move is already carried there; different = a real clash.
        row["fix_shape"] = (SHAPE_MIRROR if holder[key] == value else SHAPE_COLLIDE)
        return row
    row["target_holds_this_key"] = False

    if not row["target_matches_value"]:
        row["fix_shape"] = SHAPE_CONVICT
    elif row["scope_relation"] in RELATED_SCOPES:
        row["fix_shape"] = SHAPE_CLEAN
    else:
        row["fix_shape"] = SHAPE_FOREIGN
    return row


# ------------------------------------------------------------------ universe (a face is a vintage)
def _universe():
    """The faces E286's own census was published over (E292: a face is a vintage)."""
    live = [n for n in e286.face_universe() if n not in SELF_FACES]
    stored, stored_from = vintage.published_names(OUTDIR, (SRC_FACE,), ("faces_censused",))
    if not stored:
        return live, vintage.note(live, [], len(live), None, None)
    keep = set(live)
    used = [n for n in stored if n in keep and n not in SELF_FACES]
    note = vintage.note(used, sorted(set(live) - set(used)), len(live), stored_from, None)
    note["faces_published_but_gone_from_disk"] = [n for n in stored if n not in keep]
    return used, note


# ------------------------------------------------------------------ build
def build():
    names, universe_note = _universe()
    recs = [e286.analyse_face(n) for n in names]
    objs = {rec["face"]: load(rec["face"]) for rec in recs}

    rows = []
    for rec in recs:
        cands_by_unit = lists_by_unit(rec)
        for field in rec["fields"]:
            if field.get("why") != "unit_list_exists_elsewhere":
                continue
            rows.append(plan_row(rec, objs[rec["face"]], field,
                                 cands_by_unit.get(field["claimed_unit"], [])))

    by_shape = {s: [r for r in rows if r["fix_shape"] == s] for s in SHAPES}
    clean = by_shape[SHAPE_CLEAN]
    foreign = by_shape[SHAPE_FOREIGN]
    convict = by_shape[SHAPE_CONVICT]
    choice = by_shape[SHAPE_CHOICE]
    own = by_shape[SHAPE_OWN]
    mirror = by_shape[SHAPE_MIRROR]
    collide = by_shape[SHAPE_COLLIDE]
    premise = by_shape[SHAPE_PREMISE]
    single_target = clean + foreign + convict + mirror + collide

    # D5: per-face ranking by gain per move
    per_face = []
    for rec in recs:
        mine = [r for r in rows if r["face"] == rec["face"]]
        if not mine:
            continue
        mine_clean = [r for r in mine if r["fix_shape"] == SHAPE_CLEAN]
        scopes = sorted({r["target_scope"] for r in mine_clean})
        per_scope = {}
        for r in mine_clean:
            per_scope[r["target_scope"]] = per_scope.get(r["target_scope"], 0) + 1
        per_face.append({
            "face": rec["face"],
            "elsewhere_rows": len(mine),
            "related_clean_moves": len(mine_clean),
            "foreign_agreements": len([r for r in mine if r["fix_shape"] == SHAPE_FOREIGN]),
            "moves_would_convict": len([r for r in mine if r["fix_shape"] == SHAPE_CONVICT]),
            "choice_required": len([r for r in mine if r["fix_shape"] == SHAPE_CHOICE]),
            "needs_own_records": len([r for r in mine if r["fix_shape"] == SHAPE_OWN]),
            "mirror_copies": len([r for r in mine if r["fix_shape"] == SHAPE_MIRROR]),
            "collisions": len([r for r in mine if r["fix_shape"] == SHAPE_COLLIDE]),
            "premise_failures": len([r for r in mine if r["fix_shape"] == SHAPE_PREMISE]),
            "distinct_target_scopes": len(scopes),
            "clean_per_scope": (float(len(mine_clean)) / len(scopes)) if scopes else None,
            "best_scope": (max(per_scope, key=lambda k: (per_scope[k], k)) if per_scope else None),
            "best_scope_clean_counts": (max(per_scope.values()) if per_scope else 0),
        })
    per_face.sort(key=lambda b: (-(b["clean_per_scope"] or 0.0), -b["foreign_agreements"],
                                 -b["moves_would_convict"], b["face"]))

    def relation_mix(bucket):
        mix = {}
        for r in bucket:
            mix[r["scope_relation"]] = mix.get(r["scope_relation"], 0) + 1
        return mix

    scopes = sorted({"%s :: %s" % (r["face"], parent_path(r["path"])) for r in rows})
    agreeing = clean + foreign
    degenerate = [r for r in agreeing if r["target_is_degenerate"]]

    summary = {
        "faces_censused": len(recs),
        "elsewhere_rows": len(rows),
        "distinct_row_scopes": len(scopes),
        "single_target_rows": len(single_target),
        "related_clean_moves": len(clean),
        "foreign_scope_agreements": len(foreign),
        "agreeing_single_target_rows": len(agreeing),
        "moves_that_would_convict": len(convict),
        "choice_required": len(choice),
        "needs_own_records": len(own),
        "mirror_copies": len(mirror),
        "collisions": len(collide),
        "premise_failures": len(premise),
        "gradable_rows": len(single_target) + len(choice) + len(own),
        "agreeing_rows_whose_target_holds_at_most_one_item": len(degenerate),
        "agreeing_share_that_is_degenerate": (float(len(degenerate)) / len(agreeing)) if agreeing else None,
        "agreeing_relation_mix": relation_mix(agreeing),
        "convict_relation_mix": relation_mix(convict),
        "rows_landing_in_a_related_scope": len([r for r in single_target
                                                if r["scope_relation"] in RELATED_SCOPES]),
        "faces_with_a_related_clean_move": len([b for b in per_face if b["related_clean_moves"]]),
        "top_faces": [
            {"face": b["face"], "related_clean_moves": b["related_clean_moves"],
             "foreign_agreements": b["foreign_agreements"],
             "moves_would_convict": b["moves_would_convict"],
             "distinct_target_scopes": b["distinct_target_scopes"],
             "clean_per_scope": b["clean_per_scope"], "best_scope": b["best_scope"]}
            for b in per_face[:5]],
        "shape_statement": ("move_count = qualified key + exactly one list of that unit; move_count is "
                            "only 'clean' when the list lives in the count's own scope or a scope that "
                            "contains / sits under it -- an agreement in a foreign scope is published "
                            "as coincidence-prone; choice_required = the unit is published in more than "
                            "one scope; needs_own_records = the key IS the unit name, so no sibling "
                            "list of that name can exist; mirror_copy / collision = the target scope "
                            "already holds this key with the same / a different value; premise_fails = "
                            "no list of the claimed unit resolves in this face"),
        "calibrated": False,
    }
    verdict = decide(summary)
    summary["verdict"] = verdict

    identity = {
        "rows_join_e286_census": None,        # filled from the source faces below
        "distinct_scopes_join_e290": None,
        "shape_partition_sums_to_rows": sum(len(v) for v in by_shape.values()) == len(rows),
        "every_clean_move_equals_its_target_length": all(
            r["published_value"] == r["target_list_length"] for r in clean),
        "every_clean_move_lands_in_a_related_scope": all(
            r["scope_relation"] in RELATED_SCOPES for r in clean),
        "every_foreign_agreement_lands_outside_a_related_scope": all(
            r["scope_relation"] not in RELATED_SCOPES for r in foreign),
        "every_convicting_move_differs_from_its_target_length": all(
            r["published_value"] != r["target_list_length"] for r in convict),
        "every_mirror_copy_carries_the_same_value": all(
            r["target_key_value"] == r["published_value"] for r in mirror),
        "every_collision_carries_a_different_value": all(
            r["target_key_value"] != r["published_value"] for r in collide),
        "every_bare_unit_row_is_a_needs_own_records_row": all(
            r["fix_shape"] == SHAPE_OWN for r in rows if r["bare_unit_key"]),
        "choice_rows_have_at_least_two_scopes": all(r["n_candidate_scopes"] >= 2 for r in choice),
        "self_faces_absent_from_universe": all(n not in names for n in SELF_FACES),
        "source_face_present": SRC_FACE in names,
        "profile_face_present": PROFILE_FACE in names,
    }
    try:
        src = load(SRC_FACE)
        identity["rows_join_e286_census"] = (
            ((src.get("summary") or {}).get("of_which_unit_list_exists_elsewhere")) == len(rows))
        identity["e286_elsewhere_rows"] = (src.get("summary") or {}).get("of_which_unit_list_exists_elsewhere")
    except (OSError, ValueError, KeyError):
        identity["e286_join_note"] = "source face unreadable; the census join was not run"
    try:
        prof = load(PROFILE_FACE)
        block = ((prof.get("summary") or {}).get("un_derivable_elsewhere_scope") or {})
        identity["distinct_scopes_join_e290"] = (block.get("distinct_scopes") == len(scopes)
                                                 and block.get("n_rows") == len(rows))
        identity["e290_distinct_scopes"] = block.get("distinct_scopes")
        identity["e290_n_rows"] = block.get("n_rows")
    except (OSError, ValueError, KeyError):
        identity["e290_join_note"] = "profile face unreadable; the E290 join was not run"

    return {
        "study": STUDY, "title": TITLE, "evidence_cutoff": CUTOFF,
        "generated": None,   # stamped by run
        "no_bill": NO_BILL,
        "source_faces": [SRC_FACE, PROFILE_FACE],
        "faces_censused": names,
        "universe_vintage": universe_note,
        "frozen_spec": {
            "D1_plan_from_faces_census_from_e286": "which counts are un-derivable is imported from the "
                                                  "census; scopes, lengths and values are read off the "
                                                  "published face; the plan also joins E290's "
                                                  "301-row / 299-scope headline",
            "D2_premise_checked": "a row is moveable only when a list of exactly the claimed unit "
                                  "exists in the same face and resolves to a list; failures published",
            "D3_agreement_measured_with_its_scope": "the published value is compared to the candidate "
                                                    "list's length AND the scope relation is published, "
                                                    "so an agreement in an unrelated subtree is its own "
                                                    "bucket with its degenerate-target share",
            "D4_unique_and_collision_free": "more than one candidate scope is a choice; a target scope "
                                            "already holding the key is a mirror (same value) or a "
                                            "collision (different value)",
            "D5_rank_by_gain_per_move": "per-face ranking key is related-scope clean counts / distinct "
                                        "target scopes, then foreign agreements, then convictions, "
                                        "then face name",
            "D6_no_reburn": "published faces re-read only; no draw stream, no band rebuild, no engine",
            "verdict_vocab": list(VERDICT_VOCAB),
            "vocab_amendment": {
                "when": "after the first build of this face, before the face was published or wired",
                "why": "the first build scored agreement without asking where the candidate list lives "
                       "and reported 126 clean moves / 75 convictions; a relation-aware recount showed "
                       "all 126 agreements sit in unrelated subtrees against lists of at most one "
                       "item, and no row lands beside a list in its own scope, which the four declared "
                       "verdicts could not express",
                "first_build_counts": {"clean_moves": 126, "moves_that_would_convict": 75,
                                       "choice_required": 76, "needs_own_records": 24},
                "kept": "the four original verdicts are unchanged and remain reachable; V4 names the "
                        "case the declaration missed rather than reinterpreting a clean result",
            },
        },
        "rows": rows,
        "per_face": per_face,
        "identity_check": identity,
        "summary": summary,
        "verdict": verdict,
        "verdict_reason": _reason(verdict, summary),
    }


def decide(summary):
    gradable = summary.get("gradable_rows") or 0
    if not gradable:
        return VERDICT_VOCAB[4]
    moves = (summary.get("related_clean_moves", 0) + summary.get("moves_that_would_convict", 0))
    if not summary.get("rows_landing_in_a_related_scope"):
        # D3: nothing lands beside a list in a scope that has anything to do with the count.
        return VERDICT_VOCAB[4]
    if summary.get("needs_own_records", 0) * 2 > gradable:
        return VERDICT_VOCAB[3]
    if summary.get("choice_required", 0) * 2 > gradable:
        return VERDICT_VOCAB[2]
    if summary.get("moves_that_would_convict", 0):
        return VERDICT_VOCAB[1]
    if moves:
        return VERDICT_VOCAB[0]
    return VERDICT_VOCAB[4]


def _fmt_pct(value):
    return "n/a" if value is None else "%.1f pct" % (value * 100.0)


def _reason(verdict, summary):
    head = ("of %d un-derivable 'elsewhere scope' counts in %d face(s): %d are bare unit-name rows with "
            "no relocation at all, %d need a choice between scopes, %d have a single target, %d mirror or "
            "collide with a key already in the target scope, and %d have no resolvable list of their unit"
            % (summary["elsewhere_rows"], summary["faces_censused"], summary["needs_own_records"],
               summary["choice_required"], summary["single_target_rows"],
               summary["mirror_copies"] + summary["collisions"], summary["premise_failures"]))
    if verdict == VERDICT_VOCAB[4]:
        tail = ("; among the %d single-target rows %d agree with their candidate list and %d do not, but "
                "only %d of those rows land beside a list in their own scope or a scope that contains / "
                "sits under it -- %d of the %d agreements are against a list holding at most one item in "
                "an unrelated subtree, so the premise 'the face already publishes this unit where the "
                "count needs it' fails and the counts measure a collection the face never enumerates"
                % (summary["single_target_rows"], summary["agreeing_single_target_rows"],
                   summary["moves_that_would_convict"], summary["rows_landing_in_a_related_scope"],
                   summary["agreeing_rows_whose_target_holds_at_most_one_item"],
                   summary["agreeing_single_target_rows"]))
    elif verdict == VERDICT_VOCAB[0]:
        tail = ("; every one of the %d related-scope moves would agree with the list it lands beside, so "
                "the naming change is checkable the day it ships" % summary["related_clean_moves"])
    elif verdict == VERDICT_VOCAB[1]:
        tail = ("; %d moves would agree and %d would immediately publish a disagreement the face does not "
                "carry today, so 'move the count' is not free -- it is auditability bought by convicting "
                "the face" % (summary["related_clean_moves"], summary["moves_that_would_convict"]))
    elif verdict == VERDICT_VOCAB[2]:
        tail = ("; the majority of gradable rows have more than one scope publishing their unit, so the "
                "author must choose the collection the count counts before any move is checkable")
    else:
        tail = ("; the majority of these rows name their unit as the key itself, so no sibling list of "
                "that name can exist in the same parent -- they need their own records, not a move")
    return head + tail


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
    face = build()
    face["generated"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    write_face(face)
    s = face["summary"]
    print("E292 %s" % face["verdict"])
    print("  elsewhere rows=%d over %d scope(s) in %d face(s)"
          % (s["elsewhere_rows"], s["distinct_row_scopes"], s["faces_censused"]))
    print("  shapes: related_clean=%d foreign_agree=%d convict=%d choice=%d own_records=%d mirror=%d "
          "collision=%d premise_fail=%d"
          % (s["related_clean_moves"], s["foreign_scope_agreements"], s["moves_that_would_convict"],
             s["choice_required"], s["needs_own_records"], s["mirror_copies"], s["collisions"],
             s["premise_failures"]))
    print("  rows landing in a related scope=%d ; agreeing rows with a <=1-item target=%d of %d (%s)"
          % (s["rows_landing_in_a_related_scope"],
             s["agreeing_rows_whose_target_holds_at_most_one_item"],
             s["agreeing_single_target_rows"], _fmt_pct(s["agreeing_share_that_is_degenerate"])))
    print("  agreeing relation mix=%s ; convict relation mix=%s"
          % (s["agreeing_relation_mix"], s["convict_relation_mix"]))
    ic = face["identity_check"]
    print("  identity: census=%s e290=%s partition=%s"
          % (ic["rows_join_e286_census"], ic["distinct_scopes_join_e290"],
             ic["shape_partition_sums_to_rows"]))
    return 0


def cmd_verify():
    stored = load(FACE)
    live = build()
    problems = []
    if stored.get("verdict") != live.get("verdict"):
        problems.append("verdict: stored=%r live=%r" % (stored.get("verdict"), live.get("verdict")))
    s_stored, s_live = stored.get("summary") or {}, live.get("summary") or {}
    for key in ("elsewhere_rows", "distinct_row_scopes", "related_clean_moves",
                "foreign_scope_agreements", "agreeing_single_target_rows", "moves_that_would_convict",
                "choice_required", "needs_own_records", "mirror_copies", "collisions",
                "premise_failures", "single_target_rows", "rows_landing_in_a_related_scope",
                "agreeing_rows_whose_target_holds_at_most_one_item"):
        if s_stored.get(key) != s_live.get(key):
            problems.append("summary.%s does not re-derive" % key)
    if ["%s :: %s" % (r["face"], r["path"]) for r in (stored.get("rows") or [])] != \
            ["%s :: %s" % (r["face"], r["path"]) for r in live["rows"]]:
        problems.append("the priced row set does not re-derive")
    if [r["fix_shape"] for r in (stored.get("rows") or [])] != [r["fix_shape"] for r in live["rows"]]:
        problems.append("the fix-shape assignment does not re-derive")
    if [r["scope_relation"] for r in (stored.get("rows") or [])] != \
            [r["scope_relation"] for r in live["rows"]]:
        problems.append("the scope relation does not re-derive")
    ic = live["identity_check"]
    for key in ("shape_partition_sums_to_rows", "every_clean_move_equals_its_target_length",
                "every_clean_move_lands_in_a_related_scope",
                "every_foreign_agreement_lands_outside_a_related_scope",
                "every_convicting_move_differs_from_its_target_length",
                "every_mirror_copy_carries_the_same_value",
                "every_collision_carries_a_different_value",
                "every_bare_unit_row_is_a_needs_own_records_row",
                "choice_rows_have_at_least_two_scopes", "self_faces_absent_from_universe"):
        if not ic.get(key):
            problems.append("identity check %s is false" % key)
    if not ic.get("rows_join_e286_census"):
        problems.append("this plan's rows do not join the census")
    if ic.get("distinct_scopes_join_e290") is False:
        problems.append("this plan's row/scope pair does not join E290's published 301/299")
    if s_stored.get("verdict") not in VERDICT_VOCAB:
        problems.append("verdict outside the frozen set")
    print("E292 verify: %d problem(s)" % len(problems))
    for problem in problems:
        print("  - %s" % problem)
    return 0 if not problems else 1


# ------------------------------------------------------------------ selftest
def _fixture():
    """One face carrying every fix shape the plan can report."""
    return {
        # related (ancestor) clean: the list sits in a scope that CONTAINS the count's scope
        "rel": {"arms": [{"id": 1}, {"id": 2}], "deeper": {"n_arms": 2}},
        # foreign agreement: list at a sibling subtree, agreeing only because it holds one item
        "seeds": [7],
        "far": {"bucket": {"n_seeds": 1}},
        # conviction: single target, value disagrees with the list length
        "cells": [1, 2],
        "dis": {"holder": {"n_cells": 5}},
        # choice required: the same unit published in two scopes
        "rows": [{"a": 1}],
        "sub": {"rows": [{"a": 1}, {"b": 2}]},
        "pik": {"n_rows": 2},
        # needs own records: the key IS the unit name (the unit is published, but elsewhere)
        "legpool": {"legs": [{"id": 1}]},
        "own": {"legs": 7},
        # mirror: the target scope already carries n_labels with the same value
        "mir": {"labels": ["a", "b"], "n_labels": 2},
        "mir2": {"n_labels": 2},
        # collision: the target scope already carries n_keys with a different value
        "col": {"keys": ["a"], "n_keys": 9},
        "col2": {"n_keys": 4},
    }


def cmd_selftest():
    ok, fail = 0, []

    def leg(name, cond, detail=""):
        nonlocal ok
        if cond:
            ok += 1
        else:
            fail.append("%s %s" % (name, detail))

    fx = _fixture()
    rec = e286.analyse_face_from_object("FIXTURE.json", fx)
    cands = lists_by_unit(rec)
    fields = {f["path"]: f for f in rec["fields"]}
    priced = {}
    for path, field in fields.items():
        if field.get("why") != "unit_list_exists_elsewhere":
            continue
        priced[path] = plan_row(rec, fx, field, cands.get(field["claimed_unit"], []))

    # L1 D2: the census supplies which rows are un-derivable; every priced row came from that set
    leg("L1", all(fields[p].get("why") == "unit_list_exists_elsewhere" for p in priced) and len(priced) >= 7,
        sorted(priced))

    # L2 D3: a single target in a scope that CONTAINS the count's scope, with a matching length, is clean
    leg("L2", priced.get("rel.deeper.n_arms", {}).get("fix_shape") == SHAPE_CLEAN
        and priced["rel.deeper.n_arms"]["scope_relation"] == "ancestor_scope"
        and priced["rel.deeper.n_arms"]["target_list_length"] == 2, priced.get("rel.deeper.n_arms"))

    # L3 D3: the same agreement in a foreign scope is NOT clean -- and a one-item target is disclosed
    leg("L3", priced.get("far.bucket.n_seeds", {}).get("fix_shape") == SHAPE_FOREIGN
        and priced["far.bucket.n_seeds"]["target_is_degenerate"] is True, priced.get("far.bucket.n_seeds"))

    # L4 D3: a disagreeing single target is a conviction, never gain
    leg("L4", priced.get("dis.holder.n_cells", {}).get("fix_shape") == SHAPE_CONVICT
        and priced["dis.holder.n_cells"]["target_matches_value"] is False, priced.get("dis.holder.n_cells"))

    # L5 D4: a unit published in two scopes is a choice, not a move
    leg("L5", priced.get("pik.n_rows", {}).get("fix_shape") == SHAPE_CHOICE
        and priced["pik.n_rows"]["n_candidate_scopes"] >= 2, priced.get("pik.n_rows"))

    # L6 D2: a bare unit key can never have a sibling list of the same name -> needs own records
    leg("L6", priced.get("own.legs", {}).get("fix_shape") == SHAPE_OWN
        and priced["own.legs"]["bare_unit_key"] is True, priced.get("own.legs"))

    # L7 D4: same key + same value in the target scope is one move carried twice, not a gain
    leg("L7", priced.get("mir2.n_labels", {}).get("fix_shape") == SHAPE_MIRROR,
        priced.get("mir2.n_labels"))

    # L8 D4: same key + different value in the target scope is a collision, published separately
    leg("L8", priced.get("col2.n_keys", {}).get("fix_shape") == SHAPE_COLLIDE,
        priced.get("col2.n_keys"))

    # L9 scope_relation is computed on the list's OWN scope and reads ancestry, not string prefixes
    leg("L9", scope_relation("rel.deeper", "rel") == "ancestor_scope"
        and scope_relation("rel", "rel.deeper") == "descendant_scope"
        and scope_relation("a.b", "a.bc") == "unrelated_scope"
        and scope_relation("a.b", "") == "face_root"
        and scope_relation("a.b", "a.b") == "same_scope")

    # L10 resolve() walks dotted paths with indices and raises on a miss
    leg("L10", resolve(fx, "rel.arms") == fx["rel"]["arms"]
        and resolve(fx, "sub.rows") == [{"a": 1}, {"b": 2}]
        and _raises(lambda: resolve(fx, "nope.deeper")))

    # L11 parent_path() never returns a trailing dot
    leg("L11", parent_path("summary.n_arms") == "summary" and parent_path("n_arms") == ""
        and parent_path("a[0].n_rows") == "a[0]")

    # L12 every frozen verdict is reachable through decide()
    leg("L12", decide({"gradable_rows": 10, "rows_landing_in_a_related_scope": 0}) == VERDICT_VOCAB[4]
        and decide({"gradable_rows": 10, "rows_landing_in_a_related_scope": 4,
                    "needs_own_records": 6}) == VERDICT_VOCAB[3]
        and decide({"gradable_rows": 10, "rows_landing_in_a_related_scope": 4,
                    "needs_own_records": 2, "choice_required": 6}) == VERDICT_VOCAB[2]
        and decide({"gradable_rows": 10, "rows_landing_in_a_related_scope": 4,
                    "needs_own_records": 2, "choice_required": 2, "related_clean_moves": 4,
                    "moves_that_would_convict": 2}) == VERDICT_VOCAB[1]
        and decide({"gradable_rows": 10, "rows_landing_in_a_related_scope": 6,
                    "needs_own_records": 2, "choice_required": 2, "related_clean_moves": 6,
                    "moves_that_would_convict": 0}) == VERDICT_VOCAB[0])

    # L13 the live face re-derives twice on its decisive keys and stays inside the vocabulary
    a, b = build(), build()
    keys = ("elsewhere_rows", "related_clean_moves", "foreign_scope_agreements",
            "moves_that_would_convict", "choice_required", "needs_own_records", "mirror_copies",
            "collisions", "premise_failures", "rows_landing_in_a_related_scope")
    leg("L13", all(a["summary"][k] == b["summary"][k] for k in keys)
        and a["verdict"] == b["verdict"] and a["verdict"] in VERDICT_VOCAB)

    # L14 the live identity checks hold (census join, partition, and each shape's own invariant)
    ic = a["identity_check"]
    leg("L14", ic["rows_join_e286_census"] and ic["shape_partition_sums_to_rows"]
        and ic["every_clean_move_equals_its_target_length"]
        and ic["every_clean_move_lands_in_a_related_scope"]
        and ic["every_foreign_agreement_lands_outside_a_related_scope"]
        and ic["every_convicting_move_differs_from_its_target_length"]
        and ic["self_faces_absent_from_universe"], ic)

    # L15 D5: the ranking is by gain per move -- related clean counts over scopes, never raw rows
    faces = a["per_face"]
    leg("L15", all(faces[i]["clean_per_scope"] >= faces[i + 1]["clean_per_scope"]
                   for i in range(len(faces) - 1)
                   if faces[i]["clean_per_scope"] is not None
                   and faces[i + 1]["clean_per_scope"] is not None))

    # L16 D3 disclosure: the mix by scope relation sums to each bucket's own count
    s = a["summary"]
    leg("L16", sum(s["agreeing_relation_mix"].values()) == s["agreeing_single_target_rows"]
        and sum(s["convict_relation_mix"].values()) == s["moves_that_would_convict"])

    print("E292 selftest: %d/%d" % (ok, ok + len(fail)))
    for f in fail:
        print("  FAIL %s" % f)
    return 0 if not fail else 1


def _raises(fn):
    try:
        fn()
    except Exception:
        return True
    return False


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