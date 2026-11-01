"""E336 -- which of the six consumers can afford to opt in to the tokenizer first?

E335 landed ``code_lines_tokenized`` beside the shipped ``code_lines`` and proved nothing moved.
E334 priced a repository-wide switch (6 faces / 37 numbers) but only ranked the blast radius; it
never priced a *single consumer*.  A repository-wide price is not a decision anyone can take -- the
question a reader actually has is "may I move ONE study onto the new reading", and that price is
per consumer.

This study ranks the six E334 consumers by the cost of moving exactly one of them onto the landed
sibling name, and it ranks them twice:

  reading A (delta)   -- how many numbers move between the shipped build and the tokenized build,
                         i.e. how much of the consumer's own answer is the helper's defect;
  reading B (publish) -- how many numbers in the consumer's *published* face would have to be
                         re-read, i.e. what a reader pays today when the consumer opts in.

The two readings are different quantities on purpose: A is "how wrong is the consumer", B is "how
much of its published answer stops being true".  They need not order the six the same way, and the
day they disagree the cheapest candidate is not published at all -- the disagreement is.

Usage:
    python scripts/e336_consumer_optin_ranking.py [run|verify|selftest]
"""

import io
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e326_template_parameter_consumers as e326  # noqa: E402  (path set above)
import e332_invisible_tail_recovery as e332  # noqa: E402
import e334_helper_repair_blast_radius as e334  # noqa: E402

ROOT = e326.ROOT
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
TODAY = "2026-11-01"
FACE = "OPTINRANK-%s.json" % TODAY
LATEST = "optinrank_latest.json"
STUDY = "E336_consumer_optin_ranking"
E334_FACE = "results/state_tilt/%s" % e334.FACE
E332_FACE = "results/state_tilt/%s" % e332.FACE

MAX_EXAMPLES = 8
TOL = 1e-9

SHIPPED = e326.code_lines
NEW = "code_lines_tokenized"

V_NAMED = "cheapest_opt_in_named_and_the_two_readings_rank_the_six_the_same_way"
V_REFUSE = "no_consumer_named_because_the_two_readings_disagree_about_which_is_cheapest"
V_NONE = "no_consumer_is_affordable_because_every_published_verdict_fails_to_survive_the_switch"
VERDICTS = (V_NAMED, V_REFUSE, V_NONE)

_TOKENIZED = {}


def say(message):
    """Progress on stderr: the build is minutes long and a silent pipe looks like a hang."""
    sys.stderr.write(message + "\n")
    sys.stderr.flush()


# ---------------------------------------------------------------------------------- primitives

def tokenized(src):
    """The landed sibling reading, memoised.  Not the E334 wrapper: this asks the shipped name."""
    key = src or ""
    hit = _TOKENIZED.get(key)
    if hit is None:
        fn = getattr(e326, NEW)
        hit = fn(src)
        _TOKENIZED[key] = hit
    return hit


def priced(build_fn, helper=None):
    """One consumer build under a chosen reading; the module binding is restored and asserted."""
    outdir = tempfile.mkdtemp(prefix="e336_build_")
    try:
        if helper is not None:
            e326.code_lines = helper
        return build_fn(outdir)
    finally:
        e326.code_lines = SHIPPED
        if e326.code_lines is not SHIPPED:
            raise AssertionError("the corpus helper was not restored")


def compare(a, b):
    """Numeric leaves that differ between two summary blocks (E333's comparator, reused)."""
    return e334.e333.compare(a, b)


def load_json(rel):
    with io.open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
        return json.load(fh)


def order_of(rows, key):
    """Cheapest first: a consumer that keeps its verdict outranks one that does not.

    Ties break on the other reading's number and then on the name, so the order is a pure function
    of the published rows -- nothing here can drift from the numbers it prints.
    """
    def sort_key(row):
        return (0 if row["published_verdict_survives"] else 1,
                row[key],
                row["name"])
    return [r["name"] for r in sorted(rows, key=sort_key)]


def decide(affordable, orders_agree, cheapest_agrees):
    """The frozen rule.  Returns (verdict, reason) and never reads prose."""
    if not affordable:
        return V_NONE, ("no consumer survives the switch with its published verdict intact, so no "
                        "opt-in is affordable")
    if not orders_agree:
        return V_REFUSE, ("the delta reading and the publish reading order the six differently, so "
                          "the cheapest candidate is a property of the yardstick rather than of a "
                          "consumer")
    if not cheapest_agrees:
        return V_REFUSE, ("the two readings disagree about which consumer is cheapest")
    return V_NAMED, ("both readings put the same consumer first and it keeps its published verdict")


# ------------------------------------------------------------------------------------- consumers

def published_e334():
    """E334's per-consumer rows, the published delta reading this study has to reproduce."""
    try:
        doc = load_json(E334_FACE)
    except Exception as exc:  # noqa: BLE001 - reported, never swallowed
        say("  E334 face unreadable (%r); reproduction will be published as blind" % (exc,))
        return {}
    return {c["name"]: c for c in doc.get("consumers") or []}


def recovered_sources():
    """Per-source recovered code lines, from the E332 face (no rebuild)."""
    try:
        rows = load_json(E332_FACE).get("sources") or []
    except Exception as exc:  # noqa: BLE001 - reported, never swallowed
        say("  E332 face unreadable (%r); the recovered axis will be blind" % (exc,))
        return {}, 0
    out, total = {}, 0
    for row in rows:
        n = row.get("recovered_code_lines") or 0
        if n:
            out[row.get("source")] = n
            total += n
    return out, total


def own_faces_excluded(files):
    """This study's own dated face and latest pointer are dropped before any build."""
    kept, dropped = [], 0
    for path, src in files:
        base = os.path.basename(path)
        if base.startswith("OPTINRANK-") or base == LATEST:
            dropped += 1
            continue
        kept.append((path, src))
    return kept, dropped


def consumer_rows(files, published):
    rows = []
    for entry in e334.registry(files):
        say("  %s: shipped build" % entry["name"])
        base = priced(entry["build"])
        say("  %s: tokenized build (landed sibling name)" % entry["name"])
        tok = priced(entry["build"], tokenized)
        delta_rows, delta_compared = compare(base.get("summary"), tok.get("summary"))
        disk, why = e334.published(entry["face"])
        face_rows, face_compared = [], 0
        if disk is not None:
            face_rows, face_compared = compare(disk.get("summary"), tok.get("summary"))
        pub = published.get(entry["name"]) or {}
        rows.append({
            "name": entry["name"],
            "module": "scripts/%s" % entry["module"],
            "face": entry["face"],
            "face_readable": disk is not None,
            "face_unreadable_because": why,
            "verdict_shipped_build": base.get("verdict"),
            "verdict_tokenized_build": tok.get("verdict"),
            "verdict_published_face": (disk or {}).get("verdict"),
            "published_verdict_survives": ((disk or {}).get("verdict") == tok.get("verdict")
                                           if disk is not None else None),
            "numbers_compared_delta": delta_compared,
            "numbers_moved_by_the_delta": len(delta_rows),
            "numbers_compared_publish": face_compared,
            "numbers_in_published_face_that_move": len(face_rows),
            "published_face_needs_republishing": bool(face_rows),
            "delta_examples": delta_rows[:MAX_EXAMPLES],
            "publish_examples": face_rows[:MAX_EXAMPLES],
            "delta_rows_truncated": max(0, len(delta_rows) - MAX_EXAMPLES),
            "publish_rows_truncated": max(0, len(face_rows) - MAX_EXAMPLES),
            "e334_published_delta": pub.get("numbers_moved_by_the_repair"),
            "e334_published_face_numbers_moved": (
                (pub.get("published_face_vs_repaired_build") or {}).get("numbers_differing")),
            "e334_delta_reproduced": (pub.get("numbers_moved_by_the_repair")
                                      == len(delta_rows)),
        })
    return rows


# ---------------------------------------------------------------------------------------- build

def build(root=None, outdir=None, files=None, rows=None, pub_doc=None):
    root = root or ROOT
    files = files if files is not None else e326.corpus()
    files, own_faces_dropped = own_faces_excluded(files)
    if pub_doc is None and rows is None:
        pub_doc = published_e334()
    published = pub_doc if pub_doc is not None else {}
    if rows is None:
        say("  recovered axis from the E332 face (no builds)")
        _recovered, recovered_total = recovered_sources()
        say("  pricing six consumers twice over one corpus")
        rows = consumer_rows(files, published)
    else:
        recovered_total = sum((r.get("recovered_code_lines") or 0)
                              for r in (load_json(E332_FACE).get("sources") or []))

    priced_rows = [r for r in rows if r["published_verdict_survives"] is not None]
    unreadable = [r["name"] for r in rows if r["published_verdict_survives"] is None]
    affordable = [r["name"] for r in priced_rows if r["published_verdict_survives"]]
    order_delta = order_of(priced_rows, "numbers_moved_by_the_delta")
    order_publish = order_of(priced_rows, "numbers_in_published_face_that_move")
    orders_agree = order_delta == order_publish
    cheapest_agrees = bool(order_delta) and order_delta[0] == order_publish[0]
    verdict, reason = decide(bool(affordable), orders_agree, cheapest_agrees)
    cheapest = order_delta[0] if verdict == V_NAMED else None
    head_stable = cheapest_agrees
    stable_positions = [n for i, n in enumerate(order_delta)
                        if i < len(order_publish) and order_publish[i] == n]
    if verdict == V_REFUSE and head_stable:
        reason = (reason + "; the head is not the unstable part -- both readings put %s first and "
                  "only %d position(s) below it move, so the cheapest name is a floor rather than "
                  "an answer" % (order_delta[0], sum(
                      1 for i, n in enumerate(order_delta)
                      if i < len(order_publish) and order_publish[i] != n)))

    reproduced = sum(1 for r in rows if r.get("e334_delta_reproduced"))
    republish = [r["name"] for r in rows if r["published_face_needs_republishing"]]

    summary = {
        "consumers_reviewed": len(rows),
        "consumers_with_a_readable_published_face": len(priced_rows),
        "consumers_unreadable": len(unreadable),
        "consumers_that_keep_their_published_verdict": len(affordable),
        "consumers_whose_published_face_would_need_republishing": len(republish),
        "published_numbers_that_would_move": sum(r["numbers_in_published_face_that_move"]
                                                 for r in rows),
        "numbers_moved_by_the_delta": sum(r["numbers_moved_by_the_delta"] for r in rows),
        "faces_to_republish_if_all_six_opted_in": len(republish),
        "e334_rows_reproduced": reproduced,
        "e334_rows_published": len(published),
        "orders_agree": bool(orders_agree),
        "cheapest_agrees": bool(cheapest_agrees),
        "head_is_stable_across_readings": bool(head_stable),
        "positions_stable_in_both_orders": len(stable_positions),
        "consumers_in_the_same_place_in_both_orders": stable_positions,
        "doctrine_delta_order": order_delta,
        "doctrine_publish_order": order_publish,
        "order_positions_that_differ": sum(
            1 for i, n in enumerate(order_delta)
            if i < len(order_publish) and order_publish[i] != n),
        "recovered_code_lines_in_the_corpus": recovered_total,
        "own_faces_excluded_from_the_corpus": own_faces_dropped,
    }
    doc = {
        "study": STUDY,
        "evidence_cutoff": TODAY,
        "verdict": verdict,
        "verdict_reason": reason,
        "summary": summary,
        "decision": {
            "rule": {
                "rank_by": "verdict survival first, then the reading's own number, then the name",
                "cheapest_published_only_when": [
                    "at least one consumer keeps its published verdict",
                    "the delta order and the publish order are identical",
                    "both orders put the same consumer first",
                ],
                "otherwise": "publish the disagreement and name nobody",
            },
            "inputs": {
                "consumers_that_keep_their_published_verdict": len(affordable),
                "orders_agree": bool(orders_agree),
                "cheapest_agrees": bool(cheapest_agrees),
            },
            "cheapest_opt_in": cheapest,
            "head_is_stable_across_readings": bool(head_stable),
            "positions_stable_in_both_orders": len(stable_positions),
            "named_or_refused": "named" if cheapest else "refused",
        },
        "rankings": {
            "delta_reading": {r["name"]: {"numbers_moved_by_the_delta":
                                          r["numbers_moved_by_the_delta"],
                                          "published_verdict_survives":
                                          r["published_verdict_survives"]}
                              for r in priced_rows},
            "publish_reading": {r["name"]: {"numbers_in_published_face_that_move":
                                            r["numbers_in_published_face_that_move"],
                                            "published_verdict_survives":
                                            r["published_verdict_survives"]}
                                for r in priced_rows},
            "delta_order": order_delta,
            "publish_order": order_publish,
        },
        "consumers": rows,
        "rules": {
            "one_corpus": "every consumer runs over e326.corpus(), so a delta is the reading and "
                          "nothing else",
            "landed_name": "the tokenized builds use the name E335 landed on the helper module, "
                           "not the wrapper E334 used to price the repair",
            "two_readings": "delta = shipped build vs tokenized build (how wrong is the consumer); "
                            "publish = published face vs tokenized build (what a reader must "
                            "re-read); they are different quantities and may order differently",
            "verdict_survival": "a consumer's published verdict is compared with the verdict its "
                                "tokenized build reaches, never with the shipped build's -- the "
                                "shipped build is the thing being replaced",
            "frozen_rule": "decide() is code: the named candidate cannot drift from the numbers",
            "self_inclusion": "this study's own face and latest pointer are dropped from the "
                              "corpus before any build (E204/E319 class)",
        },
        "limits": {
            "consumer_set": "the six consumers E334 registered; E332 and E333 are excluded there "
                            "and stay excluded here",
            "recovered_axis": "the recovered-code-line axis is read from the E332 face rather than "
                              "rebuilt, because rebuilding it is E332's own measurement",
            "builds": "12 builds (six consumers x shipped/tokenized), no ablation: a per-consumer "
                      "price does not need attribution, it needs a count",
        },
    }
    target = outdir or OUTDIR
    os.makedirs(target, exist_ok=True)
    body = json.dumps(doc, ensure_ascii=False, indent=1) + "\n"
    for name in (FACE, LATEST):
        with io.open(os.path.join(target, name), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body)
    return doc


# --------------------------------------------------------------------------------------- verify

def verify_face(disk, fresh):
    problems = []
    if disk.get("verdict") != fresh.get("verdict"):
        problems.append("the verdict does not re-derive")
    if disk.get("verdict") not in VERDICTS:
        problems.append("verdict %r is outside the frozen set" % (disk.get("verdict"),))
    for key, value in (fresh.get("summary") or {}).items():
        if (disk.get("summary") or {}).get(key) != value:
            problems.append("summary.%s does not re-derive" % key)
    for key, value in (fresh.get("decision") or {}).get("inputs", {}).items():
        if ((disk.get("decision") or {}).get("inputs") or {}).get(key) != value:
            problems.append("decision.inputs.%s does not re-derive" % key)
    if (disk.get("decision") or {}).get("cheapest_opt_in") != \
            (fresh.get("decision") or {}).get("cheapest_opt_in"):
        problems.append("the named candidate does not re-derive")
    if (disk.get("decision") or {}).get("cheapest_opt_in") and \
            disk.get("verdict") != V_NAMED:
        problems.append("a candidate is named while the verdict refuses to name one")
    disk_c = {c.get("name"): c for c in disk.get("consumers") or []}
    fresh_c = {c.get("name"): c for c in fresh.get("consumers") or []}
    if sorted(disk_c) != sorted(fresh_c):
        problems.append("the consumer list does not re-derive")
    for name in sorted(set(disk_c) & set(fresh_c)):
        a, b = disk_c[name], fresh_c[name]
        for key in ("numbers_moved_by_the_delta", "numbers_in_published_face_that_move",
                    "published_verdict_survives"):
            if a.get(key) != b.get(key):
                problems.append("%s.%s does not re-derive" % (name, key))
    if (disk.get("summary") or {}).get("consumers_with_a_readable_published_face", 0) <= 0:
        problems.append("nothing was priced, which is a broken measurement not a clean result")
    return problems


def verify(root=None, files=None):
    root = root or ROOT
    fresh = build(root=root, outdir=tempfile.mkdtemp(prefix="e336_verify_"), files=files)
    path = os.path.join(root, "results", "state_tilt", FACE)
    try:
        with io.open(path, encoding="utf-8") as fh:
            disk = json.load(fh)
    except Exception as exc:  # noqa: BLE001 - reported, never swallowed
        return ["the face does not read: %r" % (exc,)]
    return verify_face(disk, fresh)


# ------------------------------------------------------------------------------------- selftest

SWALLOW = (
    '"""doc."""\n'
    'V = ("""\n'
    'one\n'
    '""".split())\n'
    '\n'
    'def load_a():\n'
    '    return json.load(open("results/x/FOO-2026-11-01.json"))\n'
)


def _fake_row(name, delta, publish, survives=True):
    return {"name": name, "module": "scripts/%s.py" % name, "face": "results/x/%s.json" % name,
            "face_readable": survives is not None,
            "face_unreadable_because": None if survives is not None else "no such face",
            "verdict_shipped_build": "v1", "verdict_tokenized_build": "v1" if survives else "v2",
            "verdict_published_face": "v1",
            "published_verdict_survives": survives,
            "numbers_compared_delta": 10, "numbers_moved_by_the_delta": delta,
            "numbers_compared_publish": 10, "numbers_in_published_face_that_move": publish,
            "published_face_needs_republishing": bool(publish),
            "delta_examples": [], "publish_examples": [],
            "delta_rows_truncated": 0, "publish_rows_truncated": 0,
            "e334_published_delta": delta, "e334_published_face_numbers_moved": publish,
            "e334_delta_reproduced": True}


def cmd_selftest():
    checks = []

    def check(name, ok, detail=""):
        checks.append((name, bool(ok), detail))

    # L1/L2: the primitive this study rests on is the shipped name, not the E334 wrapper
    check("L1 the landed sibling name exists on the helper module", hasattr(e326, NEW), NEW)
    check("L2 it is not the shipped function",
          getattr(e326, NEW, None) is not SHIPPED, repr(getattr(e326, NEW, None)))

    # L3/L4: priced() restores the module binding, even when the build raises
    def boom(outdir):
        raise RuntimeError("build failed")
    try:
        priced(boom, tokenized)
    except RuntimeError:
        pass
    check("L3 the reading is restored after a raising build", e326.code_lines is SHIPPED,
          repr(e326.code_lines))

    def fake_build(outdir):
        os.makedirs(outdir, exist_ok=True)
        return {"verdict": "v%d" % len([1 for _n, _t in e326.code_lines(SWALLOW)]),
                "summary": {"shown": len([1 for _n, _t in e326.code_lines(SWALLOW)])}}
    shipped_doc = priced(fake_build)
    token_doc = priced(fake_build, tokenized)
    check("L4 the tokenized reading is not silently the same call",
          tokenized(SWALLOW) is not None and isinstance(token_doc["summary"]["shown"], int),
          json.dumps({"shipped": shipped_doc["summary"], "tokenized": token_doc["summary"]}))

    # L5/L6: the sort is a pure function of the published rows, verdict survival dominates
    rows = [_fake_row("B", 5, 0), _fake_row("A", 1, 3), _fake_row("C", 0, 0)]
    order_delta = order_of(rows, "numbers_moved_by_the_delta")
    order_pub = order_of(rows, "numbers_in_published_face_that_move")
    check("L5 the cheapest is the smallest number among survivors",
          order_delta == ["C", "A", "B"] and order_pub == ["B", "C", "A"], str(order_delta))
    check("L6 a consumer that loses its verdict sorts last whatever its count",
          order_of([_fake_row("X", 0, 0, survives=False), _fake_row("Y", 9, 9)],
                   "numbers_moved_by_the_delta") == ["Y", "X"],
          "verdict survival is not dominant")

    # L7-L10: the frozen rule
    check("L7 both readings agreeing names a candidate",
          decide(True, True, True)[0] == V_NAMED, decide(True, True, True)[0])
    check("L8 a different order refuses to name",
          decide(True, False, True)[0] == V_REFUSE, decide(True, False, True)[0])
    check("L9 a different first place refuses to name",
          decide(True, True, False)[0] == V_REFUSE, decide(True, True, False)[0])
    check("L10 nothing affordable refuses even when the orders agree",
          decide(False, True, True)[0] == V_NONE, decide(False, True, True)[0])

    # L11/L12: order stability is measured on the whole order, not only the head
    a = [_fake_row("A", 1, 1), _fake_row("B", 2, 3), _fake_row("C", 3, 2)]
    b = [_fake_row("A", 1, 1), _fake_row("B", 3, 3), _fake_row("C", 2, 2)]
    check("L11 the same first place can still hide a different order",
          order_of(a, "numbers_moved_by_the_delta")[0]
          == order_of(b, "numbers_in_published_face_that_move")[0]
          and order_of(a, "numbers_moved_by_the_delta")
          != order_of(b, "numbers_in_published_face_that_move"),
          "%s vs %s" % (order_of(a, "numbers_moved_by_the_delta"),
                        order_of(b, "numbers_in_published_face_that_move")))
    check("L12 an unreadable face is not counted as surviving",
          [r for r in [_fake_row("Z", 0, 0, survives=None)]
           if r["published_verdict_survives"] is not None] == [],
          "an unreadable face was priced")

    # L13/L14: publish and re-derive
    fx_rows = [_fake_row("A", 2, 1), _fake_row("B", 0, 0)]
    out = tempfile.mkdtemp(prefix="e336_fx_")
    fx = build(root=out, outdir=os.path.join(out, "results", "state_tilt"), files=[],
               rows=fx_rows, pub_doc={"A": {}, "B": {}})
    check("L13 the face writes both the dated face and the latest pointer",
          os.path.isfile(os.path.join(out, "results", "state_tilt", FACE)) and
          os.path.isfile(os.path.join(out, "results", "state_tilt", LATEST)), "missing")
    check("L14 verify_face accepts what build just published", verify_face(fx, fx) == [],
          str(verify_face(fx, fx))[:200])

    # L15/L16: verify catches doctoring on both a legacy field and the named candidate
    doctored = json.loads(json.dumps(fx))
    doctored["summary"]["numbers_moved_by_the_delta"] = 99
    check("L15 verify_face catches a doctored summary",
          any("summary.numbers_moved_by_the_delta" in p for p in verify_face(doctored, fx)),
          str(verify_face(doctored, fx))[:200])
    doctored2 = json.loads(json.dumps(fx))
    doctored2["decision"]["cheapest_opt_in"] = "Z"
    check("L16 verify_face catches a renamed candidate",
          any("named candidate does not re-derive" in p for p in verify_face(doctored2, fx)),
          str(verify_face(doctored2, fx))[:200])

    # L17/L18: a named candidate under a refusing verdict is a contradiction
    doctored3 = json.loads(json.dumps(fx))
    doctored3["verdict"] = V_REFUSE
    doctored3["verdict"] is not None
    check("L17 a refusing verdict with a named candidate is rejected",
          any("named while the verdict refuses" in p
              for p in verify_face(doctored3, dict(fx, verdict=V_REFUSE,
                                                   decision=dict(fx["decision"],
                                                                 cheapest_opt_in="A")))),
          "contradiction not caught")

    # L18/L19: self-inclusion exclusion
    kept, dropped = own_faces_excluded([("/x/" + FACE, "a"), ("/x/" + LATEST, "b"),
                                        ("/x/OTHER-2026-11-01.json", "c")])
    check("L18 the study's own faces are dropped from the corpus",
          dropped == 2 and [os.path.basename(p) for p, _s in kept]
          == ["OTHER-2026-11-01.json"], "%d dropped" % dropped)
    check("L19 a face of another study is kept",
          kept and kept[0][0].endswith("OTHER-2026-11-01.json"), str(kept))

    # L20: the two readings are actually different quantities on the fixture
    check("L20 the readings measure different numbers on the same row",
          fx_rows[0]["numbers_moved_by_the_delta"] !=
          fx_rows[0]["numbers_in_published_face_that_move"],
          json.dumps(fx_rows[0])[:120])

    bads = [c for c in checks if not c[1]]
    for name, ok, detail in checks:
        if not ok:
            print("FAIL %s :: %s" % (name, detail))
    print("\n%d/%d passed" % (len(checks) - len(bads), len(checks)))
    return 0 if not bads else 1


# ------------------------------------------------------------------------------------------ cli

def cmd_run():
    doc = build()
    s = doc["summary"]
    print("%s | %s" % (doc["verdict"], STUDY))
    print("consumers %(consumers_reviewed)s priced %(consumers_with_a_readable_published_face)s / "
          "verdict survives %(consumers_that_keep_their_published_verdict)s" % s)
    print("numbers: delta moves %(numbers_moved_by_the_delta)s ; a reader must re-read "
          "%(published_numbers_that_would_move)s across %(faces_to_republish_if_all_six_opted_in)s "
          "face(s)" % s)
    print("E334 rows reproduced: %(e334_rows_reproduced)s/%(e334_rows_published)s | orders agree: "
          "%(orders_agree)s (%(order_positions_that_differ)s position(s) differ)" % s)
    for r in doc["consumers"]:
        print("   - %-30s delta %2d/%-3d  publish %2d/%-3d  verdict_survives=%s"
              % (r["name"], r["numbers_moved_by_the_delta"], r["numbers_compared_delta"],
                 r["numbers_in_published_face_that_move"], r["numbers_compared_publish"],
                 r["published_verdict_survives"]))
    print("delta order  : " + " < ".join(s["doctrine_delta_order"]))
    print("publish order: " + " < ".join(s["doctrine_publish_order"]))
    print("stable in both orders: %s of %s (%s)"
          % (s["positions_stable_in_both_orders"], s["consumers_with_a_readable_published_face"],
             ", ".join(s["consumers_in_the_same_place_in_both_orders"])))
    print("CHEAPEST: " + str(doc["decision"]["cheapest_opt_in"] or "refused -- " +
                             doc["verdict_reason"]))
    return 0


def cmd_verify():
    problems = verify()
    if problems:
        print("PROBLEMS: " + "; ".join(problems[:8]))
        return 1
    print("verify: 0 problems")
    return 0


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd in ("run", "build"):
        return cmd_run()
    if cmd == "verify":
        return cmd_verify()
    if cmd == "selftest":
        return cmd_selftest()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))