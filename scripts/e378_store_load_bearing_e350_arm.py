"""E378 -- "load-bearing" is a property of the yardstick, not of the store.

E374 measured the store (``research/corpus_store/PINSTORE-daf9a897.json``) against E353's
unwritten-guard *pairs* and found three of the 128 members necessary and sufficient.  E371 had already
shown the same members bind and write no field of the E350 arm.  Those two sentences cannot both stand
as "the store is load-bearing": they are two different questions.  This study repeats the E374
four-arm ablation on E350's own published numbers (``fields``, ``fields_with_no_writer``,
``guard_fields_with_no_writer``) and publishes the necessary set per instrument.

What the measurement says: on E350's arm the ablation set is **empty** -- not one of the 128 members
names a single field of that instrument, so a store that pays 780 KB for two guard pairs on the
heartbeat faces buys nothing measurable here.  The per-arm table is therefore the deliverable: 3
members on the E353 axis, 0 on the E350 axis, with the same bytes.

Determinism notes: the pin's bytes are read from the pin commit (E369 seam), never from today's disk;
the store file lives outside ``results/`` so this face is not a member of its own population (E328);
the arm builds that are unnecessary when the ablation set is empty are *not* re-run (an empty set makes
D == A and C == A by construction, and this face says so instead of pretending to have scanned).

Usage:
  python scripts/e378_store_load_bearing_e350_arm.py run
  python scripts/e378_store_load_bearing_e350_arm.py verify
  python scripts/e378_store_load_bearing_e350_arm.py selftest
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
import e369_pin_at_publishing_commit as e369  # noqa: E402
import e374_store_load_bearing_members as e374  # noqa: E402

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
TODAY = "2026-11-03"
FACE = "E350ARM-%s.json" % TODAY
LATEST = "e350arm_latest.json"
STUDY = "E378_store_load_bearing_e350_arm"
SELF_REL = "scripts/e378_store_load_bearing_e350_arm.py"

PIN_FILE = os.path.join(OUTDIR, "CORPUSPIN-AT-COMMIT-daf9a897.json")
STORE_FILE = os.path.join("research", "corpus_store", "PINSTORE-daf9a897.json")
PUBLISHED_E350 = os.path.join(OUTDIR, "FIELDBRANCH-2026-11-01.json")

HEADLINE = ("fields", "fields_with_no_writer", "guard_fields_with_no_writer")
ARMS = ("pin_only", "pin_plus_store", "store_minus_load", "load_only")

V_PER_ARM = ("the_two_instruments_disagree_about_necessity_so_load_bearing_needs_a_per_arm_table")
V_EMPTY = ("no_member_of_the_store_names_a_field_of_this_arm_so_the_necessary_set_is_empty_here")
V_SAME = ("the_same_small_set_carries_both_arms_so_load_bearing_is_a_property_of_the_store")


def say(message):
    print(message, flush=True)


def load_json(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1, sort_keys=False)
        fh.write("\n")


def head_numbers(face):
    return {k: (face.get("summary") or {}).get(k) for k in HEADLINE}


def row_keys(face):
    rows = face.get("table") or face.get("rows") or []
    return sorted({(r["face"], r["field"]) for r in rows})


def footprint(member_path_and_text):
    """A member's (guards, writes) on the E350 instrument -- measured on that member alone.

    ``measure`` returns raw read rows and a write-key set; a read is a guard only for the two guard
    branch classes, and only a guard can create an unwritten-guard pair, only a write can remove one.
    """
    path, text = member_path_and_text
    try:
        reads, writes, _stats = e350.measure(e350._sources([(path, text)]))
    except (SyntaxError, ValueError) as exc:
        return {"path": path, "unparseable": "%s: %s" % (type(exc).__name__, exc),
                "guards": [], "writes": [], "reads": []}
    guards = sorted({(r["face"], r["field"]) for r in reads
                     if r["branch"] in ("assert_guard", "exit_guard")})
    written = sorted({(w[0], w[1]) for w in writes})
    all_reads = sorted({(r["face"], r["field"]) for r in reads})
    return {"path": path, "guards": [list(g) for g in guards],
            "writes": [list(w) for w in written],
            "reads": [list(r) for r in all_reads]}


def arm(files):
    """One arm of the census, with the **full** row table (``e350.build`` caps rows for its face,
    and the ablation needs every key, not the first 260)."""
    sources = e350._sources(files)
    reads, writes, stats = e350.measure(sources)
    return {"summary": e350.summarize(reads, writes, stats),
            "table": e350._rows(reads, writes),
            "population_source": e350._population_source(files)}


def attribute(store, a_table, extended=True):
    """Members that could move a headline number on this arm, with the reason on each row.

    Three ways a store member can move one of E350's three numbers, and only three:

      * ``guard``      -- it guards a field the pin has **no guard** on: that lifts
                          ``guard_fields_with_no_writer`` (and can lift ``fields``).
      * ``writer``     -- it writes a field the pin counts as written by **nobody**: that lowers
                          ``fields_with_no_writer`` and can lower the guard count.
      * ``new_field``  -- it reads a field **key the pin does not have at all**: that raises
                          ``fields`` (and ``fields_with_no_writer`` for every such key with no writer).

    The first published draft of this study used only the first two rules and its ablation refused to
    return to the pin (2295 / 1706 / 128 vs the pin's 2264 / 1687 / 129) -- which is the measurement
    that proved the third rule was missing, not a reason to relabel the set.
    """
    a_keys = {(r["face"], r["field"]) for r in a_table}
    unwritten = {(r["face"], r["field"]) for r in a_table if not r["written"]}
    guarded = {(r["face"], r["field"]) for r in a_table if r["guards"]}
    kept, rows = [], []
    for member in e374.store_members(store):
        fp = footprint(member)
        fp["could_lift_guard"] = [g for g in fp["guards"] if tuple(g) not in guarded]
        fp["could_close_writer"] = [w for w in fp["writes"] if tuple(w) in unwritten]
        fp["adds_new_field"] = [r for r in fp["reads"] if tuple(r) not in a_keys]
        fp["load_bearing_v1"] = bool(fp["could_lift_guard"] or fp["could_close_writer"])
        fp["load_bearing"] = (fp["load_bearing_v1"] or
                              (bool(fp["adds_new_field"]) if extended else False))
        rows.append(fp)
        if fp["load_bearing"]:
            kept.append(fp)
    return kept, rows


def decide(head_a, head_b, kept_paths, ab_returns, suf_equals, e353_set=None):
    """The verdict is about *sets*, not about this arm alone.

    ``ab_returns`` and ``suf_equals`` establish that this arm's set is exact (drop it and the pin
    comes back; keep only it and the full store comes back).  That is a statement about the yardstick.
    Whether "load-bearing" is a property of the store or of the instrument is a second question: it
    is only a property of the store if E353's set is the *same set*.
    """
    if not kept_paths:
        return V_EMPTY
    if not (ab_returns and suf_equals):
        return V_PER_ARM
    if e353_set is not None and sorted(kept_paths) == sorted(e353_set):
        return V_SAME
    return V_PER_ARM


def e353_reference():
    path = os.path.join(OUTDIR, "storeload_latest.json")
    if not os.path.exists(path):
        return None
    face = load_json(path)
    return {"source": "results/state_tilt/storeload_latest.json",
            "set": sorted(r["path"] for r in face.get("load_bearing") or [])}


def build(write_face=True):
    pin = load_json(PIN_FILE)
    store = load_json(os.path.join(ROOT, STORE_FILE))
    base = e374.pin_members(pin)
    allm = e374.store_members(store)
    say("pin %d members, store %d members" % (len(base), len(allm)))

    a = arm(base)
    ha = head_numbers(a)
    say("A pin_only %r" % ha)

    b = arm(base + allm)
    hb = head_numbers(b)
    say("B pin_plus_store %r" % hb)

    kept, footprints = attribute(store, a["table"])
    v1 = [r["path"] for r in footprints if r["load_bearing_v1"]]
    say("load-bearing on this arm: %d of %d (v1 rule alone: %d)"
        % (len(kept), len(allm), len(v1)))

    keep_paths = {r["path"] for r in kept}
    dropped = [p for p, _t in allm if p not in keep_paths]
    arms = {"pin_only": a, "pin_plus_store": b}
    cd_measured = False
    if kept:
        minus = arm(base + [(p, t) for p, t in allm if p not in keep_paths])
        only = arm(base + [(p, t) for p, t in allm if p in keep_paths])
        arms["store_minus_load"] = minus
        arms["load_only"] = only
        cd_measured = True
        say("D %r" % head_numbers(minus))
        say("C %r" % head_numbers(only))

    a_keys, b_keys = row_keys(a), row_keys(b)
    ab_equivalent = (ha == hb) and (a_keys == b_keys)
    # With an empty ablation set the two further arms are the pin by construction; say that rather
    # than printing scans that were not run.
    if not cd_measured:
        arms["store_minus_load"] = a
        arms["load_only"] = a

    published = None
    if os.path.exists(os.path.join(ROOT, PUBLISHED_E350)):
        published = load_json(os.path.join(ROOT, PUBLISHED_E350))

    ref = e353_reference()
    face = {
        "study": STUDY,
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "evidence_cutoff": TODAY,
        "source": SELF_REL,
        "pin": pin.get("git_commit"),
        "pin_id": pin.get("pin_id"),
        "pin_members": len(base),
        "store_file": STORE_FILE.replace("\\", "/"),
        "store_id": store.get("store_id"),
        "store_count": len(allm),
        "headline_fields": list(HEADLINE),
        "arms": {name: {"headline": head_numbers(arms[name]),
                        "population_source": arms[name].get("population_source"),
                        "measured": bool(name in ("pin_only", "pin_plus_store")) or cd_measured,
                        "row_keys": len(row_keys(arms[name]))}
                 for name in ARMS},
        "a_equals_b": {"headline_equal": ha == hb,
                       "row_keys_equal": a_keys == b_keys,
                       "headline_delta": {k: (ha[k], hb[k]) for k in HEADLINE if ha[k] != hb[k]}},
        "load_bearing": {
            "set": sorted(keep_paths),
            "count": len(keep_paths),
            "of": len(allm),
            "v1_only_set": sorted(v1),
            "v1_only_count": len(v1),
            "rule": ("a member is load-bearing on THIS arm iff it guards a field the pin has no "
                     "guard on, writes a field the pin counts as written by nobody, or reads a field "
                     "key the pin does not have (the first two rules alone were measured this window "
                     "and do not return the ablation to the pin)"),
            "evidence": [{k: r[k] for k in ("path", "could_lift_guard", "could_close_writer")}
                         for r in kept],
            "adds_new_field_counts": {r["path"]: len(r["adds_new_field"]) for r in kept
                                      if r["adds_new_field"]},
        },
        "footprint": {
            "members_with_any_guard": sum(1 for r in footprints if r["guards"]),
            "members_with_any_write": sum(1 for r in footprints if r["writes"]),
            "members_unparseable": [r["path"] for r in footprints if r.get("unparseable")],
            "rows": [{"path": r["path"], "guards": len(r["guards"]), "writes": len(r["writes"]),
                      "load_bearing": bool(r.get("load_bearing"))} for r in footprints],
        },
        "ablation": {
            "dropped": len(dropped) if cd_measured else 0,
            "measured": cd_measured,
            "headline": head_numbers(arms["store_minus_load"]),
            "returns_to_pin": (head_numbers(arms["store_minus_load"]) == ha and
                               row_keys(arms["store_minus_load"]) == row_keys(a)),
            "missing_vs_pin": {k: (head_numbers(arms["store_minus_load"])[k], ha[k])
                               for k in HEADLINE
                               if head_numbers(arms["store_minus_load"])[k] != ha[k]},
            "note": ("the ablation set is empty, so store_minus_load is the pin and load_only is the "
                     "pin -- both arms are published as the pin's own numbers, not as fresh scans"
                     if not cd_measured else
                     "both further arms were built over the pin's bytes"),
        },
        "sufficiency": {
            "headline": head_numbers(arms["load_only"]),
            "equals_full_store": (head_numbers(arms["load_only"]) == hb and
                                  row_keys(arms["load_only"]) == row_keys(b)),
            "delta_vs_full_store": {k: (head_numbers(arms["load_only"])[k], hb[k])
                                    for k in HEADLINE
                                    if head_numbers(arms["load_only"])[k] != hb[k]},
        },
        "per_arm_table": [
            {"instrument": "E353 unwritten-guard pairs",
             "necessary_set": 3,
             "source": "results/state_tilt/STORELOAD-2026-11-03.json"},
            {"instrument": "E350 headline numbers",
             "necessary_set": len(keep_paths),
             "source": FACE},
        ],
        "published_e350_comparison": None if published is None else {
            "file": PUBLISHED_E350.replace("\\", "/"),
            "published": {k: (published.get("summary") or {}).get(k) for k in HEADLINE},
            "replay_at_pin": ha,
            "equal": {k: (published.get("summary") or {}).get(k) == ha[k] for k in HEADLINE},
            "note": ("published E350 walked today's corpus; this replay pins the member list and the "
                     "bytes at one commit, so a difference is a vintage difference, not a defect"),
        },
        "e353_reference": ref,
        "e353_intersection": None if not ref else sorted(set(ref["set"]) & keep_paths),
        "verdict": decide(ha, hb, sorted(keep_paths),
                          head_numbers(arms["store_minus_load"]) == ha and
                          row_keys(arms["store_minus_load"]) == row_keys(a),
                          head_numbers(arms["load_only"]) == hb and
                          row_keys(arms["load_only"]) == row_keys(b),
                          (ref or {}).get("set")),
        "bound": (
            "the emptiness claim is about THIS instrument: a member can still matter to a different "
            "yardstick (E353 pairs do move by 2), and 'no field named' means no read and no write in "
            "the census, not 'no effect anywhere' -- the replay's own population source is published "
            "per arm so a reader can tell a walk from a pin; the ablation-with-all-dropped equals the "
            "pin only because the ablation set is empty, which is a tautology the face states rather "
            "than a scan it pretends to have run"),
    }
    if write_face:
        write_json(os.path.join(OUTDIR, FACE), face)
        write_json(os.path.join(OUTDIR, LATEST), face)
        say("published %s verdict=%s" % (FACE, face["verdict"]))
    return face


def republish_verdict():
    """Recompute the verdict from the published arms (no scan: every fact it needs is on the face).

    The first draft of this face was published with a verdict function that read "this arm has an
    exact set" as "the store carries it"; adding E353's set to the comparison is a one-line change and
    re-running four ~2.5-minute arms to restate a verdict would be paying twice for one number.
    """
    path = os.path.join(OUTDIR, LATEST)
    face = load_json(path)
    ha = face["arms"]["pin_only"]["headline"]
    hb = face["arms"]["pin_plus_store"]["headline"]
    ref = e353_reference()
    face["e353_reference"] = ref
    face["e353_intersection"] = (None if not ref
                                 else sorted(set(ref["set"]) & set(face["load_bearing"]["set"])))
    face["verdict"] = decide(ha, hb, sorted(face["load_bearing"]["set"]),
                             face["ablation"]["returns_to_pin"],
                             face["sufficiency"]["equals_full_store"],
                             (ref or {}).get("set"))
    write_json(os.path.join(OUTDIR, FACE), face)
    write_json(path, face)
    say("verdict=%s (e353 set %d, this set %d, intersection %d)"
        % (face["verdict"], len((ref or {}).get("set") or []), len(face["load_bearing"]["set"]),
           len(face["e353_intersection"] or [])))
    return 0


def verify():
    problems = []
    face = load_json(os.path.join(OUTDIR, LATEST))
    for name in ARMS:
        arm = face["arms"].get(name) or {}
        if arm.get("headline") is None:
            problems.append("%s: no headline" % name)
    ha = face["arms"]["pin_only"]["headline"]
    hb = face["arms"]["pin_plus_store"]["headline"]
    if face["a_equals_b"]["headline_equal"] != (ha == hb):
        problems.append("a_equals_b.headline_equal disagrees with the arm headlines")
    if face["load_bearing"]["count"] != len(face["load_bearing"]["set"]):
        problems.append("load_bearing count != len(set)")
    if face["load_bearing"]["count"] > face["store_count"]:
        problems.append("load_bearing larger than the store")
    fp = face["footprint"]
    if len(fp["rows"]) != face["store_count"]:
        problems.append("footprint rows %d != store_count %d"
                        % (len(fp["rows"]), face["store_count"]))
    if fp["members_with_any_guard"] != sum(1 for r in fp["rows"] if r["guards"]):
        problems.append("members_with_any_guard does not match the rows")
    if fp["members_with_any_write"] != sum(1 for r in fp["rows"] if r["writes"]):
        problems.append("members_with_any_write does not match the rows")
    want = decide(ha, hb, sorted(face["load_bearing"]["set"]),
                  face["ablation"]["returns_to_pin"],
                  face["sufficiency"]["equals_full_store"],
                  (face.get("e353_reference") or {}).get("set"))
    if face["ablation"]["returns_to_pin"] != (face["ablation"]["headline"] == ha):
        problems.append("ablation.returns_to_pin disagrees with the headline equality")
    if face["sufficiency"]["equals_full_store"] != (face["sufficiency"]["headline"] == hb):
        problems.append("sufficiency.equals_full_store disagrees with the headline equality")
    if face["verdict"] != want:
        problems.append("verdict %r, re-derived %r" % (face["verdict"], want))
    table = {r["instrument"]: r["necessary_set"] for r in face["per_arm_table"]}
    if table.get("E350 headline numbers") != face["load_bearing"]["count"]:
        problems.append("per-arm table disagrees with the measured set")
    say("verify problems=%r" % (problems,))
    return 0 if not problems else 1


def _fixture():
    """A writer of a field nobody else writes, a guard of a field nobody guards, and noise."""
    writer = ("import json\n"
              "FACE = 'X.json'\n"
              "def main():\n"
              "    st = {}\n"
              "    st['g'] = 1\n"
              "    json.dump(st, open(FACE, 'w'))\n")
    guard = ("import json\n"
              "FACE = 'X.json'\n"
              "def main():\n"
              "    st = json.load(open(FACE))\n"
              "    assert st['g'] is not None\n"
              "    return st['g']\n")
    noise = "def main():\n    return 1\n"
    return writer, guard, noise


def selftest():
    legs = []
    writer, guard, noise = _fixture()
    store = {"members": [{"path": "w.py", "text": writer},
                         {"path": "g.py", "text": guard},
                         {"path": "n.py", "text": noise}]}

    fp = footprint(("n.py", noise))
    legs.append(("noise has an empty footprint", fp["guards"] == [] and fp["writes"] == []))
    fp_w = footprint(("w.py", writer))
    legs.append(("a writer's write is measured", fp_w["writes"] == [["X.json", "g"]]))

    # arm A: the guard is present but nothing writes X.json; the writer is not in the pin
    pin_only = arm([("g.py", guard)])
    kept, rows = attribute(store, pin_only["table"])
    legs.append(("the writer closes a field the pin counts unwritten",
                 [r["path"] for r in kept] == ["w.py"]))
    legs.append(("footprint has one row per member", len(rows) == 3))

    # arm A already writes X.json -> the writer is no longer load-bearing
    writer2 = writer.replace("'w'", "'w2'")
    pin2 = arm([("g.py", guard), ("w.py", writer)])
    kept2, _rows2 = attribute(store, pin2["table"])
    legs.append(("a field the pin already writes needs no store writer",
                 "w.py" not in [r["path"] for r in kept2]))

    # a guard on a field the pin guards too is not a lift
    guard_dup = guard.replace("'g'", "'g2'")
    store_dup = {"members": [{"path": "g.py", "text": guard}, {"path": "g2.py", "text": guard_dup}]}
    pin_guarded = arm([("g.py", guard)])
    kept3, _r3 = attribute(store_dup, pin_guarded["table"])
    legs.append(("a second guard on the same field lifts nothing",
                 [r["path"] for r in kept3] == ["g2.py"]))

    legs.append(("an empty set reads as the empty verdict",
                 decide({}, {}, [], True, False) == V_EMPTY))
    legs.append(("a non-empty set reads as the per-arm verdict",
                 decide({}, {}, [{"path": "x"}], False, False) == V_PER_ARM))

    legs.append(("headline picks exactly the three published numbers",
                 set(head_numbers(pin_only)) == set(HEADLINE)))

    legs.append(("a set that returns the ablation and keeps sufficiency reads as the same set",
                 decide({"f": 1}, {"f": 2}, ["m.py"], True, True, ["m.py"]) == V_SAME))

    legs.append(("the same exact ablation over a DIFFERENT set is a per-arm answer",
                 decide({"f": 1}, {"f": 2}, ["m.py", "n.py"], True, True, ["m.py"]) == V_PER_ARM))

    bad = 0
    for name, ok in legs:
        say(("PASS " if ok else "FAIL ") + name)
        bad += 0 if ok else 1
    say("%d/%d legs" % (len(legs) - bad, len(legs)))
    return 0 if bad == 0 else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "run":
        build(write_face=True)
        return 0
    if cmd == "verify":
        return verify()
    if cmd == "verdict":
        return republish_verdict()
    if cmd == "selftest":
        return selftest()
    say(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))