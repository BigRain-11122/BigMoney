"""E374 -- the store pays 128 members and only a handful of them change a published number.

E372 published that the store (``research/corpus_store/PINSTORE-daf9a897.json``) brings E353's
unwritten-guard ``pairs`` from 129 to 131 and billed the corpus for 128 recovered members.  E371 had
already shown the same store binds no field in the E350 arm.  The queue card then asks the question a
reader of a 780 KB store is entitled to ask: *which* of those members carry the two pairs, and does
the rest of the store change anything at all?

The answer is built as measurement, not assertion.  Four arms over the same pin:

  A  pin only                        -> the number without the store
  B  pin + the whole store           -> the number E372 published
  D  pin + store minus the load-bearing members   (the ablation the card asks for)
  C  pin + the load-bearing members only          (the sufficiency the card implies)

The load-bearing set is not guessed from the pair diff: each member is parsed on its own and kept only
if it (a) carries an assert/exit guard on one of the fields whose pair the store moves, or (b) writes a
field whose pair the store *removes*.  Every kept member publishes the line that justifies it.

Two things the card's arithmetic hides and this face states plainly:

  * "129 -> 131" is a net of two, not two additions.  The store gains three pairs and pays one back,
    because one recovered member is a writer for a pair the pin counted as unwritten.
  * the three gained pairs are guards on the firm's own status faces (``bm-b.json`` heartbeat fields,
    ``state-bm-b.json`` round key), not on a research face.  What the store buys here is closeout
    bookkeeping that asserts on a heartbeat no corpus source writes -- a real pair, on a face the
    instrument's own operators maintain by hand.

Usage:
  python scripts/e374_store_load_bearing_members.py run       # four arms, publish
  python scripts/e374_store_load_bearing_members.py verify    # re-derive the non-scan facts
  python scripts/e374_store_load_bearing_members.py selftest  # offline fixture legs
"""
from __future__ import annotations

import ast
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
import e369_pin_at_publishing_commit as e369  # noqa: E402

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
TODAY = "2026-11-03"
FACE = "STORELOAD-%s.json" % TODAY
LATEST = "storeload_latest.json"
STUDY = "E374_store_load_bearing_members"
SELF_REL = "scripts/e374_store_load_bearing_members.py"

PIN_COMMIT = "daf9a897fda167987d85aa27ea17beadb48de24f"
PIN_FILE = os.path.join(OUTDIR, "CORPUSPIN-AT-COMMIT-daf9a897.json")
STORE_FILE = os.path.join("research", "corpus_store", "PINSTORE-daf9a897.json")

ARMS = ("pin_only", "pin_plus_store", "store_minus_load", "load_only")
GUARD_BRANCHES = ("assert_guard", "exit_guard")

V_ONE = ("a_handful_of_members_carries_the_two_pairs_the_rest_of_the_store_changes_no_published_"
         "pair")
V_MANY = ("no_small_load_bearing_set_exists_so_the_pairs_the_store_buys_are_not_attributable_to_a_"
          "few_members")
V_NONE = ("the_store_changes_no_pair_so_there_is_nothing_to_attribute_and_the_bill_is_paid_for_"
          "nothing")


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


def pairs_of(face):
    """The instrument's pair set: ``[(face, field)]`` of rows that read a field nobody writes."""
    return sorted({(r["face"], r["field"]) for r in face.get("rows") or []})


def store_members(store):
    """``[(path, text)]`` for the replay -- a member without text is not a member of the read."""
    return [(m["path"], m["text"]) for m in store.get("members") or [] if m.get("text")]


def pin_members(pin):
    paths = [row["path"] for row in pin.get("sources") or []]
    blobs = e369.read_blobs(pin["git_commit"], paths)
    return [(p, blobs.get(p, "")) for p in paths]


def arm_pairs(study_face):
    return {"pairs": (study_face.get("summary") or {}).get("pairs"),
            "by_class": (study_face.get("summary") or {}).get("by_class"),
            "population_source": study_face.get("population_source")}


def attribute(store, gained, lost):
    """Members that carry one of the moved pairs, each with the line that says why.

    A member is load-bearing when it *guards* a gained field (that is what creates a pair) or
    *writes* a lost field (that is what removes one).  An unbranched read of the same field is
    recorded on the row but does not earn membership: a read that is not a guard adds no pair.
    """
    want_gain = {(f, k) for f, k in gained}
    want_lost = {(f, k) for f, k in lost}
    kept, scanned = [], 0
    for path, text in store_members(store):
        scanned += 1
        try:
            reads, writes, _stats = e350.measure(e350._sources([(path, text)]))
        except (SyntaxError, ValueError) as exc:
            kept.append({"path": path, "unparseable": "%s: %s" % (type(exc).__name__, exc)})
            continue
        guards = [r for r in reads
                  if (r["face"], r["field"]) in want_gain and r["branch"] in GUARD_BRANCHES]
        written = sorted({(w[0], w[1]) for w in writes if (w[0], w[1]) in want_lost})
        if not guards and not written:
            continue
        evidence = []
        for r in guards:
            evidence.append({"kind": "guard", "face": r["face"], "field": r["field"],
                             "branch": r["branch"], "line": r.get("branch_line") or r.get("line"),
                             "form": r.get("form")})
        for face, field in written:
            evidence.append({"kind": "writer", "face": face, "field": field, "line": None})
        kept.append({"path": path, "evidence": evidence})
    return kept, scanned


def diff_pairs(a, b):
    """``(gained, lost)`` between two pair sets, both as sorted lists of pairs."""
    sa, sb = {(x[0], x[1]) for x in a}, {(x[0], x[1]) for x in b}
    return [list(x) for x in sorted(sb - sa)], [list(x) for x in sorted(sa - sb)]


def decide(arms, moved, kept, dropped):
    gained, lost = moved["gained"], moved["lost"]
    if not gained and not lost:
        return V_NONE
    if not kept:
        return V_MANY
    a = {tuple(x) for x in arms["pin_only"]["pair_set"]}
    b = {tuple(x) for x in arms["pin_plus_store"]["pair_set"]}
    d = {tuple(x) for x in arms["store_minus_load"]["pair_set"]}
    c = {tuple(x) for x in arms["load_only"]["pair_set"]}
    small = len(kept) <= max(3, len(dropped) // 10)
    if d == a and c == b and small:
        return V_ONE
    return V_MANY


def build(write_face=True):
    pin = load_json(PIN_FILE)
    store = load_json(os.path.join(ROOT, STORE_FILE))
    base = pin_members(pin)
    allm = store_members(store)

    say("pin %d members, store %d members" % (len(base), len(allm)))
    first = e353.build(files=base)
    arms = {"pin_only": dict(arm_pairs(first), pair_set=pairs_of(first))}
    say("A pin_only pairs=%s" % arms["pin_only"]["pairs"])

    full = e353.build(files=base + allm)
    arms["pin_plus_store"] = dict(arm_pairs(full), pair_set=pairs_of(full))
    say("B pin_plus_store pairs=%s" % arms["pin_plus_store"]["pairs"])

    gained, lost = diff_pairs(arms["pin_only"]["pair_set"], arms["pin_plus_store"]["pair_set"])
    say("moved: gained %d lost %d" % (len(gained), len(lost)))

    kept, scanned = attribute(store, gained, lost)
    keep_paths = {row["path"] for row in kept}
    dropped = [p for p, _t in allm if p not in keep_paths]
    say("load-bearing %d of %d scanned" % (len(kept), scanned))

    minus = e353.build(files=base + [(p, t) for p, t in allm if p not in keep_paths])
    arms["store_minus_load"] = dict(arm_pairs(minus), pair_set=pairs_of(minus))
    say("D store_minus_load pairs=%s" % arms["store_minus_load"]["pairs"])

    only = e353.build(files=base + [(p, t) for p, t in allm if p in keep_paths])
    arms["load_only"] = dict(arm_pairs(only), pair_set=pairs_of(only))
    say("C load_only pairs=%s" % arms["load_only"]["pairs"])

    a = {tuple(x) for x in arms["pin_only"]["pair_set"]}
    b = {tuple(x) for x in arms["pin_plus_store"]["pair_set"]}
    d = {tuple(x) for x in arms["store_minus_load"]["pair_set"]}
    c = {tuple(x) for x in arms["load_only"]["pair_set"]}

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
        "arms": {name: {"pairs": arms[name]["pairs"],
                        "by_class": arms[name]["by_class"],
                        "population_source": arms[name]["population_source"],
                        "pair_set": [[x[0], x[1]] for x in arms[name]["pair_set"]]}
                 for name in ARMS},
        "moved": {"gained": gained, "lost": lost,
                  "net": len(gained) - len(lost)},
        "load_bearing": kept,
        "ablation": {
            "dropped": len(dropped),
            "kept": sorted(keep_paths),
            "pairs_full_store": arms["pin_plus_store"]["pairs"],
            "pairs_after_drop": arms["store_minus_load"]["pairs"],
            "pair_set_equals_pin_only": d == a,
            "moved_by_the_drop": [list(x) for x in sorted(a - d)],
        },
        "sufficiency": {
            "kept": len(keep_paths),
            "pairs_load_only": arms["load_only"]["pairs"],
            "pair_set_equals_full_store": c == b,
            "missing_vs_full_store": [list(x) for x in sorted(b - c)],
        },
        "verdict": decide(arms, {"gained": gained, "lost": lost}, kept, dropped),
        "bound": (
            "load-bearing is measured for THIS instrument (E353's unwritten-guard pairs) only: E371 "
            "already published that the same two store_needed members bind and write no field of the "
            "E350 arm, so 'nothing else matters' is not a property of the store, it is a property of "
            "this yardstick; membership is earned by a guard on a moved field or by being a writer "
            "for a pair the store removes, so a member that feeds a pair through a helper two calls "
            "deep would be missed -- the ablation is what settles that, not the static walk; the pin "
            "is E369's pinned bytes, not today's disk, so a member that today's tree has changed is "
            "judged on the bytes the pin says it had"),
    }
    if write_face:
        write_json(os.path.join(OUTDIR, FACE), face)
        write_json(os.path.join(OUTDIR, LATEST), face)
        say("published %s verdict=%s" % (FACE, face["verdict"]))
    return face


def verify():
    """Re-derive every fact that does not need a corpus scan.

    The four arms are scans (~2 min each); re-running them inside ``verify`` would double the wall
    cost of a round for no new information, so the arms are checked for internal consistency and the
    attribution is recomputed from the store -- that is the part a code change can move.
    """
    problems = []
    face = load_json(os.path.join(OUTDIR, LATEST))
    store = load_json(os.path.join(ROOT, STORE_FILE))

    for name in ARMS:
        arm = face["arms"].get(name) or {}
        pairs = arm.get("pairs")
        pair_set = arm.get("pair_set") or []
        if pairs is None or pairs != len(pair_set):
            problems.append("%s: pairs=%r but pair_set has %d rows" % (name, pairs, len(pair_set)))
        if len({tuple(x) for x in pair_set}) != len(pair_set):
            problems.append("%s: pair_set has duplicates" % name)

    gained, lost = diff_pairs(face["arms"]["pin_only"]["pair_set"],
                              face["arms"]["pin_plus_store"]["pair_set"])
    if gained != face["moved"]["gained"] or lost != face["moved"]["lost"]:
        problems.append("moved: published %r/%r, re-derived %r/%r"
                        % (face["moved"]["gained"], face["moved"]["lost"], gained, lost))
    if face["moved"]["net"] != len(gained) - len(lost):
        problems.append("moved.net is not gained-lost")

    kept, scanned = attribute(store, gained, lost)
    if [r["path"] for r in kept] != [r["path"] for r in face["load_bearing"]]:
        problems.append("load_bearing: re-derived %r, published %r"
                        % ([r["path"] for r in kept], [r["path"] for r in face["load_bearing"]]))
    if face["ablation"]["dropped"] != scanned - len(kept):
        problems.append("ablation.dropped=%d but %d - %d"
                        % (face["ablation"]["dropped"], scanned, len(kept)))
    a = {tuple(x) for x in face["arms"]["pin_only"]["pair_set"]}
    d = {tuple(x) for x in face["arms"]["store_minus_load"]["pair_set"]}
    b = {tuple(x) for x in face["arms"]["pin_plus_store"]["pair_set"]}
    c = {tuple(x) for x in face["arms"]["load_only"]["pair_set"]}
    if face["ablation"]["pair_set_equals_pin_only"] != (d == a):
        problems.append("ablation: equality flag disagrees with the arm pair sets")
    if face["sufficiency"]["pair_set_equals_full_store"] != (c == b):
        problems.append("sufficiency: equality flag disagrees with the arm pair sets")
    want = decide({name: {"pair_set": face["arms"][name]["pair_set"]} for name in ARMS},
                  {"gained": gained, "lost": lost}, kept, ["x"] * (scanned - len(kept)))
    if face["verdict"] != want:
        problems.append("verdict: published %r, re-derived %r" % (face["verdict"], want))

    say("verify problems=%r" % (problems,))
    return 0 if not problems else 1


def _fixture():
    """A three-source fixture: a reader that guards X.y, a writer for X.y, and noise."""
    reader = ("import json\n"
              "FACE = 'X.json'\n"
              "def main():\n"
              "    st = json.load(open(FACE))\n"
              "    assert st['y'] is not None\n"
              "    return st['y']\n")
    writer = ("import json\n"
              "FACE = 'X.json'\n"
              "def main():\n"
              "    st = {}\n"
              "    st['y'] = 1\n"
              "    json.dump(st, open(FACE, 'w'))\n")
    noise = "def main():\n    return 1\n"
    return reader, writer, noise


def selftest():
    legs = []
    reader, writer, noise = _fixture()
    files = [("a.py", reader), ("b.py", writer), ("c.py", noise)]

    only_reader = e350._rows(*e350.measure(e350._sources(files[:1]))[:2])
    legs.append(("reader-only leaves the pair unwritten",
                 [(r["face"], r["field"]) for r in only_reader
                  if r["guards"] and not r["written"]] == [("X.json", "y")]))

    with_writer = e350._rows(*e350.measure(e350._sources(files))[:2])
    legs.append(("a writer in the population removes the pair",
                 [(r["face"], r["field"]) for r in with_writer
                  if r["guards"] and not r["written"]] == []))

    fake_store = {"members": [{"path": p, "text": t} for p, t in files]}
    gained = [["X.json", "y"]]
    kept, scanned = attribute(fake_store, gained, [])
    legs.append(("the guarding reader is load-bearing, the noise is not",
                 [r["path"] for r in kept] == ["a.py"] and scanned == 3))

    kept_w, _ = attribute(fake_store, [], [["X.json", "y"]])
    legs.append(("a writer for a removed pair is load-bearing",
                 [r["path"] for r in kept_w] == ["b.py"]))

    legs.append(("diff_pairs reports both directions",
                 diff_pairs([("X.json", "y"), ("Z.json", "w")], [("X.json", "z")])
                 == ([["X.json", "z"]], [["X.json", "y"], ["Z.json", "w"]])))

    legs.append(("a no-op store has nothing to attribute",
                 decide({n: {"pair_set": [["X.json", "y"]]} for n in ARMS},
                        {"gained": [], "lost": []}, [], []) == V_NONE))
    arms_fixture = {"pin_only": {"pair_set": [["A", "b"]]},
                    "pin_plus_store": {"pair_set": [["A", "b"], ["C", "d"]]},
                    "store_minus_load": {"pair_set": [["A", "b"]]},
                    "load_only": {"pair_set": [["A", "b"], ["C", "d"]]}}
    legs.append(("ablation and sufficiency both holding reads as one small set",
                 decide(arms_fixture, {"gained": [["C", "d"]], "lost": []},
                        [{"path": "m.py"}], ["n.py"] * 20) == V_ONE))
    broke = dict(arms_fixture)
    broke["store_minus_load"] = {"pair_set": [["A", "b"], ["E", "f"]]}
    legs.append(("an ablation that does not return to the pin contradicts the set",
                 decide(broke, {"gained": [["C", "d"]], "lost": []},
                        [{"path": "m.py"}], ["n.py"] * 20) == V_MANY))

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
    if cmd == "selftest":
        return selftest()
    say(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))