"""E388 -- is the trial-labor schema an accretion or a break?

E386 measured that the two merged basenames in ``results/trial_labor_w*/`` do not share one
schema: 31 distinct top-level key sets sit under two file names.  That count does not tell a
reader which failure they face.  Accretion is harmless -- a later wave is a strict superset, so
anything written for an early wave still finds every field it asks for.  A break is not -- a field
stops being written and a reader that asks for it gets ``None`` with no error.

Four things are measured here, none asserted:

  * **the walls** -- for every consecutive pair of observed waves, the fields added and the fields
    removed, classified as accretion (added only) or break (anything removed);
  * **the runs** -- the presence of each field across the whole series as maximal intervals, so a
    field that appears, disappears and comes back is not read as one long presence;
  * **the value shape** -- the JSON type of each field in every wave it appears in, so a surviving
    name that changes from a scalar to a block is priced too;
  * **the scalar fate** -- for every numeric field dropped at a break, whether any quantity in the
    post-break schema carries the same value: a loss of a schema is not a loss of a number, and
    the two must not be published as one flag.

Usage:
  python scripts/e388_schema_accretion.py run       # build the face
  python scripts/e388_schema_accretion.py verify    # re-derive the published numbers from disk
  python scripts/e388_schema_accretion.py selftest  # offline fixture legs
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

TODAY = "2026-11-03"
FACE = "SCHEMAACCRETE-%s.json" % TODAY
LATEST = "schemaaccrete_latest.json"
OUT_DIR = os.path.join(ROOT, "results", "state_tilt")
FAMILY_GLOB = os.path.join(ROOT, "results", "trial_labor_w*")
BASENAMES = ("judge_state.json", "prep_state.json")
STUDY = "E388_schema_accretion_vs_break"
SELF_REL = "scripts/e388_schema_accretion.py"

KIND_ACCRETION = "accretion"
KIND_BREAK = "break"

V_EMPTY = "no_trial_labor_wave_holds_a_state_face_to_compare"
V_ACCRETION = ("the_key_sets_only_grow_across_the_family_so_a_later_wave_answers_every_field_an_"
               "earlier_wave_answered_and_the_merge_costs_only_a_shape")
V_BREAK = ("the_key_sets_grow_monotonically_until_one_wall_drops_fields_and_at_least_one_dropped_"
           "scalar_has_no_counterpart_in_the_post_break_schema_so_the_merge_hides_both_a_schema_"
           "and_a_number")
V_BREAK_RECOVERABLE = ("the_key_sets_grow_monotonically_until_one_wall_drops_fields_but_every_"
                       "dropped_scalar_is_recoverable_from_the_post_break_shape_so_the_merge_"
                       "costs_the_schema_and_not_the_numbers")
VOCAB = {V_EMPTY, V_ACCRETION, V_BREAK, V_BREAK_RECOVERABLE}

MYSTERY_THRESHOLD_KEYS = 8   # a dict wider than this is a map of names, not a block of scalars


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _write(obj, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")


def wave_no(path):
    m = re.search(r"trial_labor_w(\d+)", path)
    return int(m.group(1)) if m else None


def family_dirs(root=ROOT):
    """Wave directories that hold at least one state face, in numeric wave order."""
    out = []
    for d in glob.glob(os.path.join(root, "results", "trial_labor_w*")):
        if not os.path.isdir(d):
            continue
        if any(os.path.exists(os.path.join(d, b)) for b in BASENAMES):
            out.append(d)
    return sorted(out, key=wave_no)


def load_series(root=ROOT, basename="judge_state.json"):
    rows = []
    for d in family_dirs(root):
        p = os.path.join(d, basename)
        if not os.path.exists(p):
            continue
        doc = _read(p)
        rows.append({
            "wave": wave_no(d),
            "path": os.path.relpath(p, root).replace("\\", "/"),
            "keys": sorted(doc),
            "types": {k: type(v).__name__ for k, v in doc.items()},
            "doc": doc,
        })
    return rows


def runs_of(rows, field):
    """Maximal presence intervals [{'from': w, 'to': w, 'present': bool}, ...]."""
    runs = []
    for r in rows:
        present = field in r["types"]
        if runs and runs[-1]["present"] == present:
            runs[-1]["to"] = r["wave"]
        else:
            runs.append({"from": r["wave"], "to": r["wave"], "present": present})
    return runs


def walls_of(rows):
    walls = []
    for a, b in zip(rows, rows[1:]):
        removed = sorted(set(a["keys"]) - set(b["keys"]))
        added = sorted(set(b["keys"]) - set(a["keys"]))
        if not removed and not added:
            continue
        walls.append({
            "from_wave": a["wave"],
            "to_wave": b["wave"],
            "kind": KIND_BREAK if removed else KIND_ACCRETION,
            "fields_from": len(a["keys"]),
            "fields_to": len(b["keys"]),
            "added": added,
            "removed": removed,
            "waves_on_the_wrong_side": [r["wave"] for r in rows if r["wave"] > b["wave"]],
            "removed_remains_absent": all(f not in b["keys"] for f in removed),
        })
    return walls


def field_rows(rows):
    fields = sorted({f for r in rows for f in r["keys"]})
    out = []
    for f in fields:
        present = [r["wave"] for r in rows if f in r["types"]]
        absent = [r["wave"] for r in rows if f not in r["types"]]
        pattern = [x["present"] for x in runs_of(rows, f)]
        re_added = any(a and not b and any(c for c in pattern[i + 2:])
                       for i, (a, b) in enumerate(zip(pattern, pattern[1:])))
        edges = []
        for a, b in zip(rows, rows[1:]):
            if f in a["types"] and f not in b["types"]:
                edges.append({"from_wave": a["wave"], "to_wave": b["wave"]})
        types = []
        for r in rows:
            t = r["types"].get(f)
            if t and t not in [x["type"] for x in types]:
                types.append({"type": t, "waves": [r["wave"]]})
            elif t:
                for x in types:
                    if x["type"] == t:
                        x["waves"].append(r["wave"])
        out.append({
            "field": f,
            "runs": runs_of(rows, f),
            "first_seen": present[0] if present else None,
            "last_seen": present[-1] if present else None,
            "present_in": present,
            "absent_in": absent,
            "removal_edges": edges,
            "waves_after_last_seen": [r["wave"] for r in rows
                                      if present and r["wave"] > present[-1]],
            "value_types": types,
            "type_flips": len(types) > 1,
            "re_added": re_added,
        })
    return out


def inner_vocabulary_walls(rows):
    """For dict-valued fields, walls where the block's own key vocabulary changes."""
    out = []
    fields = sorted({f for r in rows for f in r["keys"] if isinstance(r["doc"].get(f), dict)})
    for f in fields:
        seq = [(r["wave"], frozenset(r["doc"][f].keys())) for r in rows if isinstance(r["doc"].get(f), dict)]
        walls = []
        for a, b in zip(seq, seq[1:]):
            if a[1] != b[1]:
                walls.append({
                    "from_wave": a[0], "to_wave": b[0],
                    "removed": sorted(a[1] - b[1]),
                    "added": sorted(b[1] - a[1]),
                })
        if walls:
            out.append({
                "field": f,
                "walls": len(walls),
                "blocks": walls,
                "first_vocabulary": sorted(seq[0][1]),
                "last_vocabulary": sorted(seq[-1][1]),
                "vocabulary_replaced": bool(walls) and any(
                    w["removed"] and w["added"] for w in walls),
            })
    return out


def scalar_candidates(doc):
    """Every numeric quantity the post-break schema exposes, by name."""
    out = {}
    for k, v in doc.items():
        if isinstance(v, bool):
            out[k] = int(v)
        elif isinstance(v, (int, float)):
            out[k] = v
        elif isinstance(v, list):
            out[k + ".len"] = len(v)
        elif isinstance(v, dict):
            out[k + ".len"] = len(v)
            if len(v) <= MYSTERY_THRESHOLD_KEYS:
                for k2, v2 in v.items():
                    if isinstance(v2, (int, float)) and not isinstance(v2, bool):
                        out[k + "." + k2] = v2
    return out


def _tokens(name):
    """Name parts that can pair a dropped field with the quantity that replaced it."""
    parts = {p for p in re.split(r"[^0-9a-z]+", str(name).lower()) if p}
    parts.discard("n")
    parts.discard("len")
    return parts


def scalar_fate(rows, walls):
    """For every numeric field dropped at a break, is its value still carried under some name?

    Value equality alone is not evidence: one field's last value routinely equals an unrelated
    field's value in the next wave, so a counterpart must also share a name token with the field
    it would replace.  A value-only match is published as a coincidence, never as recovery.
    """
    out = []
    by_wave = {r["wave"]: r for r in rows}
    for w in walls:
        if w["kind"] != KIND_BREAK:
            continue
        after = by_wave[w["to_wave"]]
        cands = scalar_candidates(after["doc"])
        for f in w["removed"]:
            prev = by_wave[w["from_wave"]]
            val = prev["doc"].get(f)
            if isinstance(val, bool) or not isinstance(val, (int, float)):
                out.append({"field": f, "kind": "non_numeric", "last_value": None,
                            "from_wave": w["from_wave"], "to_wave": w["to_wave"],
                            "recoverable": None, "counterparts": [],
                            "value_coincidences": [],
                            "candidates_checked": sorted(cands)})
                continue
            hits = sorted(k for k, v in cands.items() if k != f and v == val)
            named = [k for k in hits if _tokens(f) & _tokens(k)]
            out.append({
                "field": f, "kind": "numeric", "last_value": val,
                "from_wave": w["from_wave"], "to_wave": w["to_wave"],
                "recoverable": bool(named),
                "counterparts": named,
                "value_coincidences": [k for k in hits if k not in named],
                "candidates_checked": sorted(cands),
            })
    return out


def analyse(rows, basename):
    walls = walls_of(rows)
    frows = field_rows(rows)
    fate = scalar_fate(rows, walls)
    numeric = [x for x in fate if x["kind"] == "numeric"]
    missing_pairs = []
    seen = [r["wave"] for r in rows]
    if seen:
        missing_pairs = [w for w in range(seen[0], seen[-1] + 1) if w not in seen]
    return {
        "basename": basename,
        "members": len(rows),
        "waves": seen,
        "waves_missing_inside_the_series": missing_pairs,
        "schema_sizes": [len(r["keys"]) for r in rows],
        "fields": len(frows),
        "walls": walls,
        "accretion_walls": sum(1 for w in walls if w["kind"] == KIND_ACCRETION),
        "break_walls": sum(1 for w in walls if w["kind"] == KIND_BREAK),
        "fields_with_removal_edge": sum(1 for f in frows if f["removal_edges"]),
        "fields_re_added_after_removal": sum(1 for f in frows if f["re_added"]),
        "fields_with_type_flip": sum(1 for f in frows if f["type_flips"]),
        "field_rows": frows,
        "inner_vocabulary_walls": inner_vocabulary_walls(rows),
        "scalar_fate": fate,
        "dropped_numeric": len(numeric),
        "dropped_numeric_lost": sum(1 for x in numeric if not x["recoverable"]),
        "dropped_numeric_recovered": sum(1 for x in numeric if x["recoverable"]),
    }


def decide(summary):
    if not summary.get("members"):
        return V_EMPTY
    if not summary.get("break_walls"):
        return V_ACCRETION
    if summary.get("dropped_numeric_lost"):
        return V_BREAK
    return V_BREAK_RECOVERABLE


def build(root=ROOT):
    tables = []
    for b in BASENAMES:
        rows = load_series(root, b)
        if rows:
            tables.append(analyse(rows, b))
    breaks = [(t, w) for t in tables for w in t["walls"] if w["kind"] == KIND_BREAK]
    biggest = None
    if breaks:
        t, w = max(breaks, key=lambda p: len(p[1]["removed"]))
        biggest = {
            "basename": t["basename"], "from_wave": w["from_wave"], "to_wave": w["to_wave"],
            "removed": len(w["removed"]), "added": len(w["added"]),
            "waves_on_the_wrong_side": w["waves_on_the_wrong_side"],
        }
    cutoffs = []
    for b in BASENAMES:
        for r in load_series(root, b):
            c = r["doc"].get("evidence_cutoff")
            if isinstance(c, str):
                cutoffs.append(c)
    summary = {
        "basenames": len(tables),
        "members": sum(t["members"] for t in tables),
        "waves_union": sorted({w for t in tables for w in t["waves"]}),
        "fields_union": len({f["field"] for t in tables for f in t["field_rows"]}),
        "fields_in_both_basenames": len(
            set.intersection(*[{f["field"] for f in t["field_rows"]} for t in tables])
            if tables else set()),
        "walls": sum(len(t["walls"]) for t in tables),
        "accretion_walls": sum(t["accretion_walls"] for t in tables),
        "break_walls": sum(t["break_walls"] for t in tables),
        "removal_edges": sum(t["fields_with_removal_edge"] for t in tables),
        "fields_re_added_after_removal": sum(t["fields_re_added_after_removal"] for t in tables),
        "fields_with_type_flip": sum(t["fields_with_type_flip"] for t in tables),
        "dropped_numeric": sum(t["dropped_numeric"] for t in tables),
        "dropped_numeric_lost": sum(t["dropped_numeric_lost"] for t in tables),
        "dropped_numeric_recovered": sum(t["dropped_numeric_recovered"] for t in tables),
        "fields_replaced_inside_a_dict": sum(
            1 for t in tables for v in t["inner_vocabulary_walls"] if v["vocabulary_replaced"]),
        "biggest_break": biggest,
        "schema_sizes_span": [min([min(t["schema_sizes"]) for t in tables] or [0]),
                              max([max(t["schema_sizes"]) for t in tables] or [0])],
    }
    face = {
        "study": STUDY,
        "script": SELF_REL,
        "evidence_cutoff": max(cutoffs) if cutoffs else TODAY,
        "generated": None,
        "method": ("consecutive observed waves only; a wall is a break iff any field is removed; "
                   "a dropped numeric field is recoverable iff its last value equals some numeric "
                   "quantity in the post-break schema, compared by value and never by name"),
        "summary": summary,
        "basename_table": tables,
        "verdict": decide(summary),
    }
    face["verdict"] = decide(summary)
    return face


def write_face(face, root=ROOT):
    import datetime
    face = dict(face)
    face["generated"] = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    path = os.path.join(root, "results", "state_tilt", FACE)
    _write(face, path)
    _write(face, os.path.join(root, "results", "state_tilt", LATEST))
    return path


def verify(root=ROOT):
    """Re-derive every published number from disk and from the face's own rows."""
    problems = []
    p = os.path.join(root, "results", "state_tilt", LATEST)
    if not os.path.exists(p):
        return 1
    face = _read(p)
    s = face.get("summary") or {}
    tables = face.get("basename_table") or []
    fresh = build(root)
    if face.get("verdict") != decide(s):
        problems.append("verdict does not re-derive from the summary")
    if len(tables) != s.get("basenames"):
        problems.append("basename_table does not hold one row per basename")
    if sum(t.get("members") or 0 for t in tables) != s.get("members"):
        problems.append("member total does not re-add")
    if sum(len(t.get("walls") or []) for t in tables) != s.get("walls"):
        problems.append("wall total does not re-add")
    if sum(t.get("accretion_walls") or 0 for t in tables) != s.get("accretion_walls"):
        problems.append("accretion wall count does not re-add")
    if sum(t.get("break_walls") or 0 for t in tables) != s.get("break_walls"):
        problems.append("break wall count does not re-add")
    if sum(t.get("dropped_numeric_lost") or 0 for t in tables) != s.get("dropped_numeric_lost"):
        problems.append("lost scalar count does not re-add")
    if (s.get("dropped_numeric_recovered") or 0) + (s.get("dropped_numeric_lost") or 0) \
            != s.get("dropped_numeric"):
        problems.append("dropped scalar classes do not partition the dropped scalars")
    for t in tables:
        if len(t.get("field_rows") or []) != t.get("fields"):
            problems.append("field_rows does not hold one row per field in %s" % t.get("basename"))
        if t.get("accretion_walls", 0) + t.get("break_walls", 0) != len(t.get("walls") or []):
            problems.append("wall classes do not partition the walls of %s" % t.get("basename"))
        for w in t.get("walls") or []:
            if w.get("kind") == KIND_ACCRETION and w.get("removed"):
                problems.append("an accretion wall carries a removed field in %s" % t.get("basename"))
                break
            if w.get("kind") == KIND_BREAK and not w.get("removed"):
                problems.append("a break wall removes nothing in %s" % t.get("basename"))
                break
            if w.get("fields_to", 0) - w.get("fields_from", 0) \
                    != len(w.get("added") or []) - len(w.get("removed") or []):
                problems.append("a wall's size delta disagrees with its own lists in %s"
                                % t.get("basename"))
                break
        for f in t.get("field_rows") or []:
            prob = [x["present"] for x in f.get("runs") or []]
            if len(prob) == 1 and f.get("re_added"):
                problems.append("a one-run field claims to be re-added: %s" % f.get("field"))
                break
            if any(a == b for a, b in zip(prob, prob[1:])):
                problems.append("two adjacent runs share a presence bit: %s" % f.get("field"))
                break
            if f.get("removal_edges") and not f.get("waves_after_last_seen"):
                problems.append("a field with a removal edge has no wave after its last sighting: %s"
                                % f.get("field"))
                break
    # the re-derivation must agree with the published tables, number by number
    fresh_by = {t["basename"]: t for t in fresh["basename_table"]}
    for t in tables:
        ft = fresh_by.get(t.get("basename"))
        if ft is None:
            problems.append("a published basename is no longer on disk: %s" % t.get("basename"))
            continue
        for key in ("members", "walls", "accretion_walls", "break_walls",
                    "dropped_numeric", "dropped_numeric_lost", "fields_with_type_flip"):
            if t.get(key) != ft.get(key):
                problems.append("%s does not re-derive for %s (%r != %r)"
                                % (key, t.get("basename"), t.get(key), ft.get(key)))
    for key in ("members", "walls", "accretion_walls", "break_walls", "dropped_numeric",
                "dropped_numeric_lost", "fields_with_type_flip"):
        if s.get(key) != fresh["summary"].get(key):
            problems.append("summary %s does not re-derive" % key)
    if face.get("verdict") != fresh.get("verdict"):
        problems.append("published verdict disagrees with a fresh build")
    if problems:
        print("VERIFY FAIL")
        for x in problems[:20]:
            print("  -", x)
        return 1
    print("VERIFY OK  members=%d walls=%d breaks=%d lost_scalars=%d verdict=%s"
          % (s.get("members") or 0, s.get("walls") or 0, s.get("break_walls") or 0,
             s.get("dropped_numeric_lost") or 0, str(face.get("verdict"))[:60]))
    return 0


def _fixture(root, waves, basename="prep_state.json"):
    for w, doc in waves:
        d = os.path.join(root, "results", "trial_labor_w%d" % w)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, basename), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(doc, fh)


def selftest():
    import shutil
    import tempfile

    legs = []

    def leg(name, cond, note=""):
        legs.append((name, bool(cond), note))

    base = [
        (1, {"a": 1, "b": {"x": 1}, "n": 7}),
        (2, {"a": 2, "b": {"x": 1}, "n": 7, "c": 3}),
        (3, {"a": 3, "b": {"x": 1, "y": 2}, "n": 7, "c": 3, "d": 4}),
        (4, {"a": 4, "c": 5, "starts": [1, 2, 3, 4, 5]}),
        (5, {"a": 6, "c": 7, "starts": [1, 2, 3, 4, 5]}),
    ]
    with tempfile.TemporaryDirectory() as tmp:
        _fixture(tmp, base)
        dirs = family_dirs(tmp)
        leg("five wave dirs found", len(dirs) == 5, str(len(dirs)))
        rows = load_series(tmp, "prep_state.json")
        leg("five members read", len(rows) == 5, str(len(rows)))
        face = build(tmp)
        s = face["summary"]
        t = face["basename_table"][0]
        leg("one basename", s["basenames"] == 1, str(s["basenames"]))
        leg("three walls", s["walls"] == 3, str(s["walls"]))
        leg("two accretion walls", s["accretion_walls"] == 2, str(s["accretion_walls"]))
        leg("one break wall", s["break_walls"] == 1, str(s["break_walls"]))
        br = [w for w in t["walls"] if w["kind"] == KIND_BREAK][0]
        leg("break drops b, d and n", br["removed"] == ["b", "d", "n"], str(br["removed"]))
        leg("break adds starts", br["added"] == ["starts"], str(br["added"]))
        leg("one wave on the wrong side", br["waves_on_the_wrong_side"] == [5],
            str(br["waves_on_the_wrong_side"]))
        leg("wall size delta re-adds", br["fields_to"] - br["fields_from"]
            == len(br["added"]) - len(br["removed"]), "")
        fr = {f["field"]: f for f in t["field_rows"]}
        leg("b has two runs", len(fr["b"]["runs"]) == 2, str(fr["b"]["runs"]))
        leg("b keeps its dict shape", fr["b"]["type_flips"] is False, "")
        leg("c has no removal edge", fr["c"]["removal_edges"] == [], str(fr["c"]["removal_edges"]))
        leg("n removal edge is 3->4",
            fr["n"]["removal_edges"] == [{"from_wave": 3, "to_wave": 4}],
            str(fr["n"]["removal_edges"]))
        leg("nothing is re-added", s["fields_re_added_after_removal"] == 0,
            str(s["fields_re_added_after_removal"]))
        leg("no type flips", s["fields_with_type_flip"] == 0, str(s["fields_with_type_flip"]))
        fate = {x["field"]: x for x in t["scalar_fate"] if x["kind"] == "numeric"}
        leg("n is lost", fate["n"]["recoverable"] is False, str(fate["n"]["counterparts"]))
        # a scalar replaced by the length of the list that took its place
        leg("dropped numeric counted", s["dropped_numeric"] == 2, str(s["dropped_numeric"]))
        leg("a value match without a shared name token is a coincidence, not recovery",
            any(x["field"] == "d" and x["recoverable"] is False
                and x["value_coincidences"] == ["a"] for x in t["scalar_fate"]),
            str([x for x in t["scalar_fate"] if x["field"] == "d"]))
        leg("verdict is a break with a lost number", face["verdict"] == V_BREAK,
            str(face["verdict"]))
        write_face(face, tmp)
        leg("verify clean on fixture", verify(tmp) == 0, "verify")
        again = build(tmp)
        leg("build is idempotent on the numbers",
            again["summary"] == face["summary"], "summary")

    # a scalar whose value survives as a list length under another name
    recov = [
        (1, {"a": 1, "n_starts": 6}),
        (2, {"a": 2, "starts": [1, 2, 3, 4, 5, 6]}),
    ]
    with tempfile.TemporaryDirectory() as tmp:
        _fixture(tmp, recov)
        face = build(tmp)
        fate = [x for x in face["basename_table"][0]["scalar_fate"] if x["field"] == "n_starts"]
        leg("a dropped scalar can be recovered from a list length",
            bool(fate) and fate[0]["recoverable"] is True
            and fate[0]["counterparts"] == ["starts.len"], str(fate))
        leg("all-recoverable break gets its own verdict",
            face["verdict"] == V_BREAK_RECOVERABLE, str(face["verdict"]))

    # accretion only: no break wall
    acc = [(1, {"a": 1}), (2, {"a": 1, "b": 2}), (3, {"a": 1, "b": 2, "c": 3})]
    with tempfile.TemporaryDirectory() as tmp:
        _fixture(tmp, acc)
        face = build(tmp)
        leg("accretion-only series has no break wall",
            face["summary"]["break_walls"] == 0, str(face["summary"]["break_walls"]))
        leg("accretion verdict", face["verdict"] == V_ACCRETION, str(face["verdict"]))

    # a surviving name that changes its value shape
    flip = [(1, {"a": 1, "m": 5}), (2, {"a": 1, "m": {"x": 1}})]
    with tempfile.TemporaryDirectory() as tmp:
        _fixture(tmp, flip)
        face = build(tmp)
        leg("type flip is counted", face["summary"]["fields_with_type_flip"] == 1,
            str(face["summary"]["fields_with_type_flip"]))
        leg("a type flip alone is not a break wall",
            face["summary"]["break_walls"] == 0, str(face["summary"]["break_walls"]))

    # inner vocabulary replacement is priced apart from top-level removal
    voc = [(1, {"gates": {"G-A": 1, "G-B": 2}}), (2, {"gates": {"G-C": 1, "G-D": 2}})]
    with tempfile.TemporaryDirectory() as tmp:
        _fixture(tmp, voc)
        face = build(tmp)
        leg("inner vocabulary replacement is detected",
            face["summary"]["fields_replaced_inside_a_dict"] == 1,
            str(face["summary"]["fields_replaced_inside_a_dict"]))

    # empty family
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "results"))
        face = build(tmp)
        leg("empty family has no members", face["summary"]["members"] == 0, "")
        leg("empty verdict", face["verdict"] == V_EMPTY, str(face["verdict"]))

    # a series with a missing wave inside must not read as a removal
    gap = [(1, {"a": 1, "b": 2}), (3, {"a": 1, "b": 2})]
    with tempfile.TemporaryDirectory() as tmp:
        _fixture(tmp, gap)
        face = build(tmp)
        leg("a gap is reported, not treated as a removal",
            face["summary"]["walls"] == 0, str(face["summary"]["walls"]))
        leg("the missing wave is named",
            face["basename_table"][0]["waves_missing_inside_the_series"] == [2],
            str(face["basename_table"][0]["waves_missing_inside_the_series"]))

    failed = [x for x in legs if not x[1]]
    for name, ok, note in legs:
        if not ok:
            print("FAIL %s  [%s]" % (name, note))
    print("selftest %d/%d" % (len(legs) - len(failed), len(legs)))
    return 0 if not failed else 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "run"
    if cmd == "run":
        face = build()
        path = write_face(face)
        s = face["summary"]
        print("face %s" % os.path.relpath(path, ROOT).replace("\\", "/"))
        print("members=%d walls=%d breaks=%d lost=%d verdict=%s"
              % (s["members"], s["walls"], s["break_walls"], s["dropped_numeric_lost"],
                 str(face["verdict"])[:70]))
        return 0
    if cmd == "verify":
        return verify()
    if cmd == "selftest":
        return selftest()
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())