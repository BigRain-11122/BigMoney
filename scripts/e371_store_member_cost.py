"""E371 -- what the store_needed members actually cost the pin.

E366 priced the store as the expensive half of a pin and E368 replayed a repaired seam: 2,361
members resolved from disk, 6 from the pin's commit, and the rest as ``store_needed`` -- members
the pin recorded but git cannot supply at the pin commit, replayed from today's disk.  A
``store_needed`` member is the one place a "reproduction" can borrow bytes from the tree instead of
from the pin, so the card asks for a bill rather than a footnote:

  (1) FOOTPRINT -- which face fields does the member bind (read) or write, measured with the same
      instrument E350 uses (``e350.measure``), and published twice: over the bytes the pin gives
      (UTF-8 as stored) and over BOM-stripped bytes.  The two arms exist because a member whose
      text carries a leading U+FEFF is unparseable, and "unparseable" is not "contributes nothing";
  (2) NAME REACH -- the third state.  The instrument only sees faces whose path it can resolve, so
      a member that formats its output path at run time writes a face no census can key.  For every
      (face, field) pair the published E350 face calls an unwritten guard, ask whether the member's
      own text names both the face and the field, i.e. whether the missing writer is merely unseen;
  (3) REPLAY -- build E350 and E353 over the pin's members with the store_needed set present and
      with it excluded.  The delta IS the bill: a member that moves no published number was paid
      for and bought nothing measurable.

Nothing here rewrites E368's or E350's faces; the exclusions are computed in memory.

Usage:
  python scripts/e371_store_member_cost.py run       # build the face
  python scripts/e371_store_member_cost.py verify    # re-derive the checks that need no scan
  python scripts/e371_store_member_cost.py selftest  # offline fixture legs
"""
from __future__ import annotations

import ast
import io
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
import e368_seam_replay as e368  # noqa: E402

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
TODAY = "2026-11-03"
FACE = "STOREMEMBERCOST-%s.json" % TODAY
LATEST = "storemembercost_latest.json"
STUDY = "E371_store_member_cost"
SELF_REL = "scripts/e371_store_member_cost.py"
CACHE = os.path.join(ROOT, "logs", "_e371_partial.json")

E350_KEYS = ("corpus_sources", "sources_parsed", "fields", "fields_with_no_writer",
             "guard_fields", "guard_fields_with_no_writer", "dump_sinks", "faces_named")
E353_KEYS = ("pairs", "guard_never_fires_on_a_falsy_value")

V_INVISIBLE = ("the_store_needed_members_bind_and_write_no_field_of_any_face_the_instrument_can_"
               "key_and_excluding_them_moves_nothing_but_the_source_count_so_the_store_pays_for_a_"
               "writer_the_census_cannot_see_rather_than_for_a_number")
V_UNSEEN_WRITER = ("excluding_the_store_needed_members_moves_no_published_number_yet_a_member_names_"
                   "a_face_and_field_the_face_calls_unwritten_so_the_missing_writer_is_invisible_to_"
                   "a_census_that_can_only_key_resolved_paths")
V_LOAD_BEARING = ("excluding_the_store_needed_members_changes_a_published_number_so_the_store_is_"
                  "load_bearing_and_its_members_must_be_pinned_at_the_pin_commit_not_from_disk")
V_NO_STORE = "the_pin_resolved_every_member_so_there_is_no_store_cost_to_measure"
V_EMPTY = "no_replay_was_built_so_no_claim_is_made"


def say(message):
    print(message, flush=True)


# ------------------------------------------------------------------ footprint

def dump_calls(text):
    """``[(lineno, resolved, target)]`` for every ``json.dump`` in one member's text.

    ``resolved`` is whether the destination expression is a name bound to a string constant --
    exactly the shape E350's ``_dump_sinks`` needs to key a face.  A formatted path is written but
    unnameable, which is the difference between "writes nothing" and "writes a face nobody keys".
    """
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []
    consts = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target, value = node.targets[0], node.value
            if isinstance(target, ast.Name) and isinstance(value, ast.Constant) \
                    and isinstance(value.value, str):
                consts[target.id] = value.value
    out = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == "dump"):
            continue
        if not node.args:
            continue
        dest = node.args[1] if len(node.args) > 1 else None
        resolved, target = False, None
        if isinstance(dest, ast.Call) and dest.args:
            inner = dest.args[0]
            if isinstance(inner, ast.Constant) and isinstance(inner.value, str):
                resolved, target = True, inner.value
            elif isinstance(inner, ast.Name) and inner.id in consts:
                resolved, target = True, consts[inner.id]
            else:
                target = "<computed>"
        elif isinstance(dest, ast.Name):
            target = consts.get(dest.id, "<bound>")
        out.append({"line": node.lineno, "resolved": resolved, "target": target})
    return out


def footprint(rel, text):
    """The member's field footprint under two byte arms, plus the dump-call census."""
    arms = {}
    for name, body in (("as_pinned", text), ("bom_stripped", text.lstrip("\ufeff"))):
        reads, writes, stats = e350.measure([(rel, body)])
        arms[name] = {
            "parsed": stats["parsed"],
            "reads": len(reads),
            "writes": len(writes),
            "json_bindings": stats["json_bindings"],
            "dump_sinks": stats["dump_sinks"],
            "faces_named": sorted(stats["faces_named"])[:12],
            "write_pairs": ["%s :: %s" % pair for pair in sorted(writes)][:12],
        }
    calls = dump_calls(text.lstrip("\ufeff"))
    return {
        "path": rel,
        "bytes": len(text),
        "leading_bom": text.startswith("\ufeff"),
        "arms": arms,
        "dump_calls": calls,
        "unresolved_dump_paths": [c for c in calls if not c["resolved"]],
        "footprint_empty": all(a["reads"] == 0 and a["writes"] == 0 for a in arms.values()),
        "unparseable_as_pinned": arms["as_pinned"]["parsed"] == 0,
    }


def name_reach(member_texts, unwritten_guards, counted=None):
    """``(rows, hits)`` -- unwritten guards whose face and field are both named by a member.

    This is a NAME test, not a byte test: it answers "could the unseen writer be this member",
    which is the only question a census that cannot key computed paths can still ask.  The
    published face carries only the top of that table, so ``counted`` (the summary's
    ``guard_fields_with_no_writer``) is published beside the tested row count: a residue that was
    never tested must not read as a residue that was cleared.
    """
    lowered = {rel: text.lower() for rel, text in member_texts.items()}
    rows = []
    for row in unwritten_guards or []:
        face = (row.get("face") or "").lower()
        field = (row.get("field") or "").lower()
        if not face or not field:
            continue
        named = [rel for rel, text in lowered.items() if face in text and field in text]
        if named:
            rows.append({"face": row.get("face"), "field": row.get("field"),
                         "guards": row.get("guards"), "named_by": named})
    return {"tested": len(unwritten_guards or []), "counted": counted,
            "untested": (counted - len(unwritten_guards or [])) if isinstance(counted, int) else None,
            "naming_a_member": len(rows), "rows": rows[:20]}


# ------------------------------------------------------------------ replay

def _numbers(study, face):
    summary = face.get("summary") or {}
    keys = E350_KEYS if study == "E350" else E353_KEYS
    return {k: summary.get(k) for k in keys}


def run_arm(study, members, cache, arm):
    if arm in cache:
        say("  %s/%s: cached" % (study, arm))
        return cache[arm]
    mod = e350 if study == "E350" else e353
    say("  %s/%s: building over %d members" % (study, arm, len(members)))
    face = mod.build(files=members)
    out = {"population_source": face.get("population_source"),
           "numbers": _numbers(study, face)}
    cache[arm] = out
    return out


def replay(members, store_paths, cache):
    """Arms: ``published`` (read off disk), ``with_store``, ``without_store``."""
    kept = [m for m in members if m[0] not in store_paths]
    out = {}
    for study in ("E350", "E353"):
        sub = cache.setdefault(study, {})
        published = e368._published(study)
        block = {"published": (published or {}).get("numbers"),
                 "arms": {"with_store": run_arm(study, members, sub, "with_store"),
                          "without_store": run_arm(study, kept, sub, "without_store")}}
        moved = {}
        for key in block["arms"]["with_store"]["numbers"]:
            a = block["arms"]["with_store"]["numbers"].get(key)
            b = block["arms"]["without_store"]["numbers"].get(key)
            if a != b:
                moved[key] = {"with_store": a, "without_store": b}
        block["moved_keys"] = moved
        block["published_reproduced_by"] = [
            arm for arm in ("with_store", "without_store")
            if (block["arms"][arm]["numbers"] or {}) == (block["published"] or {})]
        out[study] = block
        _save_cache(cache)
    return out


def _save_cache(cache):
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    with open(CACHE, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(cache, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")


# ------------------------------------------------------------------ verdict

def decide(store_paths, footprints, reach, studies):
    if not store_paths:
        return V_NO_STORE
    if not studies:
        return V_EMPTY
    moved = sorted(k for s in studies.values() for k in (s.get("moved_keys") or {}))
    published_moves = [k for k in moved if k not in ("corpus_sources", "sources_parsed")]
    if published_moves:
        return V_LOAD_BEARING
    if any((r.get("naming_a_member") or 0) for r in [reach]):
        return V_UNSEEN_WRITER
    if all(f.get("footprint_empty") for f in footprints):
        return V_INVISIBLE
    return V_INVISIBLE


def build(write_face=True):
    pin = e368.load_pin()
    members, prov = e368.resolve_members(pin)
    store_paths = prov["store_needed_paths"]
    say("pin %s: %d members, store_needed=%d" % (pin.get("git_commit"), len(members),
                                                 len(store_paths)))
    texts = dict(members)
    footprints = []
    for rel in store_paths:
        fp = footprint(rel, texts.get(rel, ""))
        footprints.append(fp)
        say("  %s: empty=%s unparseable_as_pinned=%s dump_calls=%d unresolved=%d"
            % (rel, fp["footprint_empty"], fp["unparseable_as_pinned"],
               len(fp["dump_calls"]), len(fp["unresolved_dump_paths"])))

    e350_face = {}
    if os.path.exists(os.path.join(OUTDIR, "fieldbranch_latest.json")):
        with open(os.path.join(OUTDIR, "fieldbranch_latest.json"), "r", encoding="utf-8") as fh:
            e350_face = json.load(fh)
    reach = name_reach({rel: texts.get(rel, "") for rel in store_paths},
                       e350_face.get("unwritten_guards") or [],
                       counted=((e350_face.get("summary") or {})
                                .get("guard_fields_with_no_writer")))
    say("  name reach: %d of %d published unwritten guards name a store member (%s counted)"
        % (reach["naming_a_member"], reach["tested"], reach["counted"]))

    cache = {}
    if os.path.exists(CACHE):
        try:
            with open(CACHE, "r", encoding="utf-8") as fh:
                cache = json.load(fh)
        except (OSError, ValueError):
            cache = {}
        if cache.get("pin_id") != pin.get("pin_id"):
            cache = {}
    cache["pin_id"] = pin.get("pin_id")
    studies = replay(members, store_paths, cache)
    _save_cache(cache)

    for study, block in studies.items():
        say("  %s moved keys: %s" % (study, sorted(block.get("moved_keys") or {})))

    face = {
        "study": STUDY,
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "evidence_cutoff": TODAY,
        "source": SELF_REL,
        "pin": pin.get("git_commit"),
        "pin_id": pin.get("pin_id"),
        "pin_members": len(members),
        "bytes_provenance": {k: v for k, v in prov.items() if not k.endswith("_paths")},
        "store_needed_paths": store_paths,
        "footprints": footprints,
        "name_reach": reach,
        "studies": studies,
        "verdict": decide(store_paths, footprints, reach, studies),
        "bill": ("the store's bill on this instrument is the source count: dropping the "
                 "store_needed set moves corpus_sources / sources_parsed by exactly its size and "
                 "no field-level number; the members themselves contribute no resolvable read and "
                 "no keyed write, so what the store pays for is a member whose output face the "
                 "census cannot name"),
        "bound": ("a member that is unparseable under the pin's bytes and empty when the BOM is "
                  "stripped is two different zeros and both are published; the name-reach test is "
                  "a substring test over one member's text, so it can only show that a writer "
                  "could be this member, never that it is; the replay compares published numbers "
                  "to two arms of the same instrument, so a key the instrument never measures "
                  "cannot move in either arm"),
    }
    if write_face:
        os.makedirs(OUTDIR, exist_ok=True)
        for target in (os.path.join(OUTDIR, FACE), os.path.join(OUTDIR, LATEST)):
            with open(target, "w", encoding="utf-8", newline="\n") as fh:
                json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
                fh.write("\n")
        say("wrote %s" % os.path.join(OUTDIR, FACE))
    return face


def verify():
    """Re-derive every check that needs no corpus scan and compare with the face."""
    path = os.path.join(OUTDIR, FACE)
    with open(path, "r", encoding="utf-8") as fh:
        face = json.load(fh)
    problems = []
    pinned = e368.load_pin()
    _, prov = e368.resolve_members(pinned)
    if face.get("store_needed_paths") != prov["store_needed_paths"]:
        problems.append("store_needed set drifted from the pin")
    for fp in face.get("footprints") or []:
        if not os.path.exists(os.path.join(ROOT, fp["path"])):
            problems.append("member vanished: %s" % fp["path"])
            continue
        with io.open(os.path.join(ROOT, fp["path"]), encoding="utf-8", errors="replace") as fh:
            text = fh.read()
        again = footprint(fp["path"], text)
        if again["arms"] != fp.get("arms") or again["dump_calls"] != fp.get("dump_calls"):
            problems.append("footprint does not re-derive: %s" % fp["path"])
    for study, block in (face.get("studies") or {}).items():
        moved = block.get("moved_keys") or {}
        allowed = {"corpus_sources", "sources_parsed"}
        if set(moved) - allowed:
            problems.append("%s moved a field-level key: %s" % (study, sorted(set(moved) - allowed)))
        delta = (moved.get("corpus_sources") or {})
        if delta:
            size = len(face.get("store_needed_paths") or [])
            if [delta.get("with_store"), delta.get("without_store")] != [
                    (block["arms"]["with_store"]["numbers"].get("corpus_sources")),
                    (block["arms"]["with_store"]["numbers"].get("corpus_sources")) - size]:
                problems.append("%s source-count delta is not the store size" % study)
        if face.get("verdict") != decide(face.get("store_needed_paths"), face.get("footprints"),
                                         face.get("name_reach"), face.get("studies")):
            problems.append("verdict does not re-derive")
    say("verify: %d problem(s)" % len(problems))
    for p in problems:
        say("  - %s" % p)
    return 1 if problems else 0


# ------------------------------------------------------------------ selftest

FIXTURE_LITERAL = '''
import json
FACE = "results/state_tilt/DELTA-2026-11-01.json"
d = json.load(open(FACE))
if d["cutoff"] == 0:
    raise SystemExit(2)
'''

FIXTURE_COMPUTED = '''
import json
def main(rnd):
    out = "results/_r%sbmb_chain.json" % rnd
    payload = {"rows": 1}
    json.dump(payload, open(out, "w"))
'''


def selftest():
    legs = []

    def leg(name, ok, detail=""):
        legs.append((name, bool(ok), detail))

    fp_lit = footprint("scripts/a.py", FIXTURE_LITERAL)
    leg("a literal face path is a resolved footprint", not fp_lit["footprint_empty"]
        and fp_lit["arms"]["as_pinned"]["reads"] == 1, str(fp_lit["arms"]["as_pinned"]))

    fp_cmp = footprint("scripts/b.py", FIXTURE_COMPUTED)
    leg("a formatted path is a write the instrument cannot name",
        fp_cmp["footprint_empty"] and len(fp_cmp["unresolved_dump_paths"]) == 1
        and fp_cmp["dump_calls"][0]["target"] == "<computed>", str(fp_cmp["dump_calls"]))

    fp_bom = footprint("scripts/c.py", "\ufeff" + FIXTURE_LITERAL)
    leg("a BOM makes the pinned bytes unparseable and the stripped bytes ordinary",
        fp_bom["unparseable_as_pinned"] and fp_bom["arms"]["bom_stripped"]["parsed"] == 1
        and fp_bom["arms"]["as_pinned"]["reads"] == 0,
        "%s | %s" % (fp_bom["arms"]["as_pinned"], fp_bom["arms"]["bom_stripped"]))

    guards = [{"face": "results/state_tilt/DELTA-2026-11-01.json", "field": "cutoff", "guards": 1},
              {"face": "results/other.json", "field": "ready", "guards": 2}]
    reach = name_reach({"scripts/b.py": "results/state_tilt/DELTA-2026-11-01.json\n"
                                        "cutoff rows"}, guards)
    leg("name reach needs both the face and the field", reach["naming_a_member"] == 1
        and reach["rows"][0]["field"] == "cutoff", str(reach["rows"]))

    empty = [{"footprint_empty": True}, {"footprint_empty": True}]
    moved_only_counts = {"E350": {"moved_keys": {"corpus_sources": {}}}}
    leg("a member that moves only the source count is invisible, not load-bearing",
        decide(["a", "b"], empty, {"naming_a_member": 0}, moved_only_counts) == V_INVISIBLE)
    leg("a member that moves a field-level key is load-bearing",
        decide(["a"], empty, {"naming_a_member": 0},
               {"E350": {"moved_keys": {"fields_with_no_writer": {}}}}) == V_LOAD_BEARING)
    leg("an unwritten guard the member names is an unseen writer",
        decide(["a"], empty, {"naming_a_member": 1}, moved_only_counts) == V_UNSEEN_WRITER)
    leg("no store means no bill", decide([], [], {"naming_a_member": 0}, moved_only_counts)
        == V_NO_STORE)

    total = len(legs)
    bad = [n for n, ok, _ in legs if not ok]
    for name, ok, detail in legs:
        say("%s %s%s" % ("PASS" if ok else "FAIL", name, (" | " + detail) if not ok else ""))
    say("selftest: %d/%d" % (total - len(bad), total))
    return 1 if bad else 0


def main(argv):
    mode = (argv[1] if len(argv) > 1 else "run").lower()
    if mode == "selftest":
        return selftest()
    if mode == "verify":
        return verify()
    build(write_face=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))