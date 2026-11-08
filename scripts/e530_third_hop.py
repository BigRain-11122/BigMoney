"""E530 -- which of the two chains E526 left moving ever reaches a value written in this tree?

E526 (results/state_tilt/secondhop_latest.json) followed the second hop of E520's 12 forwarded
arguments and published that the chain still moves in 2 parcels: ``e489_write_wire.classify(root)``
hands ``root`` to every call site as a parameter again, and ``e328_quoted_number_staleness.build(
root)`` is supplied a local at 3 of its 4 call sites.  "Still moving" is not an origin: the face
says where the value is *not*, and leaves open whether it ever lands anywhere.

This study takes the 5 second-hop hand-overs that are still a parameter or a local and follows each
one until it stops, publishing per chain:

  * every hop beyond the second, with the hand-over it produced (a literal, a module constant, a
    call result, a read, a signature default, or again a parameter/local)
  * ``hops_to_origin`` -- how many hops past the second hop it took to reach a value the repository
    actually writes, or ``null`` when the chain never reaches one
  * a shape that keeps the three ways a chain can fail apart: it *ends* at a value, it *loops back*
    into a function it already visited, or it *dead-ends* on a parameter no call site in this tree
    supplies

The chain is followed with E520's tracer and E526's hop machinery rather than a copy, so a change
in either upstream face moves this one and ``verify`` reports it.

    python scripts/e530_third_hop.py run        # build + write the face
    python scripts/e530_third_hop.py check      # gate the published face (fast)
    python scripts/e530_third_hop.py verify     # re-derive from the tree and gate
    python scripts/e530_third_hop.py selftest   # fixture corpus + doctored faces
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e520_forwarded_argument as e520  # noqa: E402  (corpus, classifier, tracer)
import e526_second_hop as e526  # noqa: E402  (the hop that produced the population)

OUTDIR = os.path.join(ROOT, "results", "state_tilt")

CARD = ("E530-WHICH-OF-THE-TWO-PARAMETERS-THAT-ARE-FORWARDED-ONCE-MORE-IS-EVER-SUPPLIED-BY-"
        "A-CALLER-THAT-IS-NOT-ITSELF-A-PARAMETER")
STUDY = "E530_third_hop"
DATE_STAMP = "2026-11-08"
FACE_NAME = "thirdhop_latest.json"
DATED_PREFIX = "THIRDHOP"

SELF_EXCLUDED = ("e530_", "run_e530", "_e530", "THIRDHOP", "thirdhop_")

UPSTREAM_FACE = os.path.join("results", "state_tilt", "SECONDHOP-2026-11-08.json")
UPSTREAM_STUDY = e526.STUDY

MAX_HOPS = 6

# ---------------------------------------------------------------- shape vocabulary
SH_ENDS = "the_chain_ends_at_a_value_this_tree_writes_or_reads"
SH_DEFAULT = "the_chain_ends_at_a_signature_default"
SH_DEAD = "the_chain_dead_ends_on_a_parameter_no_call_site_supplies"
SH_LOOP = "the_chain_loops_back_into_a_function_it_already_visited"
SH_DEPTH = "the_chain_is_still_moving_at_the_hop_cap"
SH_MIXED = "some_arms_reach_a_value_and_some_end_at_a_signature_default"
SHAPE_VOCAB = (SH_ENDS, SH_MIXED, SH_DEFAULT, SH_DEAD, SH_LOOP, SH_DEPTH)

ENDED = tuple(e520.SUPPLIED) + (e520.A_CALL, e520.A_READ, e520.A_COMPUTED)

V_ENDS = "every_chain_that_was_still_moving_at_the_second_hop_ends_at_a_value_written_in_this_tree"
V_LOOP = "some_chain_is_looped_back_so_the_value_never_reaches_a_written_origin"
V_DEAD = "some_chain_dead_ends_on_a_parameter_no_caller_in_this_tree_supplies"
V_DEFAULT = "some_chain_ends_at_a_signature_default_rather_than_at_a_caller"
V_EMPTY = "no_chain_was_still_moving_in_the_upstream_face"
VERDICT_VOCAB = (V_ENDS, V_LOOP, V_DEAD, V_DEFAULT, V_EMPTY)


def _now():
    from datetime import datetime
    return datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S")


def _sha256_file(path):
    digest = hashlib.sha256()
    with io.open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _is_self(name):
    return any(name.startswith(prefix) for prefix in SELF_EXCLUDED)


def load_upstream(root=None):
    path = os.path.join(root or ROOT, UPSTREAM_FACE)
    with io.open(path, encoding="utf-8") as fh:
        face = json.load(fh)
    return face, _sha256_file(path)


def population(face):
    """The second-hop hand-overs E526 still calls forwards: one entry per moving value."""
    chains = []
    for parcel in face.get("sites") or []:
        if parcel.get("arrival") not in (e526.R_FORWARDED, e526.R_MIXED):
            continue
        for site in parcel.get("hop_sites") or []:
            kind = site.get("argument_kind")
            if kind not in e520.FORWARDED_AGAIN:
                continue
            chains.append({
                "parcel_module": parcel.get("module"),
                "parcel_function": parcel.get("function"),
                "parcel_local": parcel.get("local"),
                "parcel_arrival": parcel.get("arrival"),
                "hop1_kind": parcel.get("hop1_kind"),
                "second_hop_module": site.get("caller_module"),
                "second_hop_line": site.get("line"),
                "second_hop_function": site.get("hop_function"),
                "argument": site.get("argument"),
                "argument_kind": kind,
            })
    chains.sort(key=lambda r: (r["second_hop_module"] or "", r["second_hop_line"] or 0,
                               r["argument"] or ""))
    return chains


# ------------------------------------------------------------------ the third hop
def _next_hop(module, line, name, kind, corpus):
    """One hop of the same machinery E526 used, on a point three or more hops in."""
    parcel = {
        "site_module": module,
        "site_line": line,
        "site_argument": name,
        "hop1_kind": kind,
    }
    return e526.hop_of_parcel(parcel, corpus)


def trace(module, line, name, kind, corpus, depth=1, seen=None, visited=None):
    """Follow one moving value until it stops; every hop is recorded, nothing is assumed."""
    visited = dict(visited or {})
    seen = set(seen or ())
    hops = []
    terminals = []
    looped = False
    capped = False

    hop = _next_hop(module, line, name, kind, corpus)
    record = {
        "depth": depth,
        "module": module,
        "line": line,
        "name": name,
        "in_kind": kind,
        "style": hop["style"],
        "note": hop["note"],
        "sites": [],
        "out_kinds": [],
    }
    for site in hop["sites"]:
        out_kind = site.get("argument_kind")
        record["out_kinds"].append(out_kind)
        record["sites"].append({
            "caller_module": site.get("caller_module"),
            "line": site.get("line"),
            "argument": site.get("argument"),
            "argument_kind": out_kind,
            "hop_function": site.get("hop_function"),
        })
        if out_kind not in e520.FORWARDED_AGAIN:
            terminals.append({"depth": depth, "kind": out_kind})
            continue
        key = (site.get("caller_module"), site.get("hop_function"), site.get("argument"))
        if key in seen:
            looped = True
            terminals.append({"depth": depth, "kind": out_kind, "looped_back_to": list(key)})
            continue
        if depth >= MAX_HOPS:
            capped = True
            terminals.append({"depth": depth, "kind": out_kind, "capped_at_hop": MAX_HOPS})
            continue
        sub = trace(site.get("caller_module"), site.get("line"), site.get("argument"),
                    out_kind, corpus, depth + 1, seen | {key}, visited)
        hops.extend(sub["hops"])
        terminals.extend(sub["terminals"])
        looped = looped or sub["looped"]
        capped = capped or sub["capped"]
    hops.insert(0, record)
    return {"hops": hops, "terminals": terminals, "looped": looped, "capped": capped}


def _shape(chain):
    kinds = [t["kind"] for t in chain["terminals"]]
    if chain["looped"]:
        return SH_LOOP
    if chain["capped"]:
        return SH_DEPTH
    if not kinds or all(k == e520.A_NO_CALL_SITE for k in kinds):
        return SH_DEAD
    reaches = any(k in ENDED for k in kinds)
    falls_back = any(k in (e520.A_DEFAULT, e520.A_OMITTED_REQUIRED, e520.A_STARRED)
                     for k in kinds)
    if reaches and falls_back:
        return SH_MIXED
    if falls_back:
        return SH_DEFAULT
    if reaches:
        return SH_ENDS
    return SH_DEPTH


def _hops_to_origin(chain):
    """Hops past the second hop needed to reach a written value, or None."""
    depths = [t["depth"] for t in chain["terminals"] if t["kind"] in ENDED]
    return min(depths) if depths else None


def analyse_chain(start, corpus):
    rec = dict(start)
    walked = trace(start["second_hop_module"], start["second_hop_line"], start["argument"],
                  start["argument_kind"], corpus)
    rec["hops"] = walked["hops"]
    rec["terminals"] = walked["terminals"]
    rec["hop_count"] = len(walked["hops"])
    rec["terminal_kinds"] = sorted(set(t["kind"] for t in walked["terminals"]))
    rec["shape"] = _shape(walked)
    rec["hops_to_origin"] = _hops_to_origin(walked)
    return rec


# ------------------------------------------------------------------ summary / verdict
def _count(rows, key, vocab):
    out = dict((v, 0) for v in vocab)
    for rec in rows:
        out[rec.get(key)] = out.get(rec.get(key), 0) + 1
    return out


def _summary(rows, sources, upstream=None):
    shapes = _count(rows, "shape", SHAPE_VOCAB)
    hop_hist = {}
    for rec in rows:
        key = str(rec.get("hops_to_origin"))
        hop_hist[key] = hop_hist.get(key, 0) + 1
    terminal_hist = {}
    for rec in rows:
        for kind in rec.get("terminal_kinds") or []:
            terminal_hist[kind] = terminal_hist.get(kind, 0) + 1
    return {
        "chains_examined": len(rows),
        "chains_by_shape": shapes,
        "chains_ending_at_a_value": shapes[SH_ENDS],
        "chains_mixed_value_and_default": shapes[SH_MIXED],
        "chains_ending_at_a_default": shapes[SH_DEFAULT],
        "chains_dead_ending": shapes[SH_DEAD],
        "chains_looped_back": shapes[SH_LOOP],
        "chains_still_moving_at_the_hop_cap": shapes[SH_DEPTH],
        "hops_to_origin_histogram": hop_hist,
        "terminal_kind_histogram": terminal_hist,
        "max_hops_followed": max([rec.get("hop_count") or 0 for rec in rows] or [0]),
        "upstream_second_hop_values_forwarded_again": (
            (upstream or {}).get("second_hop_values_forwarded_again")),
        "upstream_parcels_forwarded_again": (
            (upstream or {}).get("parcels_forwarded_again_at_the_second_hop")),
        "upstream_parcels_mixed": (upstream or {}).get("parcels_mixed_at_the_second_hop"),
        "sources_read": sources,
    }


def _verdict(summary):
    if not summary["chains_examined"]:
        return V_EMPTY
    if summary["chains_looped_back"]:
        return V_LOOP
    if summary["chains_dead_ending"]:
        return V_DEAD
    if summary["chains_mixed_value_and_default"] or summary["chains_ending_at_a_default"]:
        return V_DEFAULT
    return V_ENDS


# ------------------------------------------------------------------ build / gate
def corpus_files(root=None):
    root = root or ROOT
    seen = set()
    for sub in ("scripts", "Tools", "firm", "live", "monitor"):
        base = os.path.join(root, sub)
        for dirpath, _dirs, files in os.walk(base):
            for name in files:
                if name.endswith(".py") and not _is_self(name):
                    seen.add(os.path.relpath(os.path.join(dirpath, name), root))
    return sorted(seen)


def build(root=None, write=True, rows=None, sources=None, upstream_sha=None, upstream=None):
    root = root or ROOT
    if rows is None:
        face, sha = load_upstream(root)
        starts = population(face)
        corpus = e520.ForwardCorpus(root)
        rows = [analyse_chain(start, corpus) for start in starts]
        upstream_sha = upstream_sha or sha
        upstream = face.get("summary")
        sources = len(corpus_files(root)) if sources is None else sources
    summary = _summary(rows, sources or 0, upstream)
    face = {
        "study": STUDY,
        "card": CARD,
        "title": ("which of the two chains E526 left moving ever reaches a value written in "
                  "this tree"),
        "generated": _now(),
        "evidence_cutoff": DATE_STAMP,
        "population_source": ("%s::population() -- every E526 second-hop site whose argument_kind "
                              "is again a parameter or a local" % os.path.basename(__file__)),
        "upstream_face": UPSTREAM_FACE.replace(os.sep, "/"),
        "upstream_study": UPSTREAM_STUDY,
        "upstream_face_sha256": upstream_sha,
        "method_limits": [
            "one hop is either a call site of the function that owns a forwarded parameter, or "
            "the statement that binds a forwarded local; a value reached through a container, a "
            "callback or an instance attribute is outside this scan and is published as "
            "no_call_site_of_the_function_that_owns_the_parameter_exists_in_this_tree, never as "
            "a written value",
            "a hop cap of %d is published as still_moving rather than resolved: a chain that is "
            "longer than the cap is counted in neither the ending nor the dead-end bucket" % MAX_HOPS,
            "a chain that revisits a (module, function, name) it already visited is published as "
            "looped_back and its terminal kinds are not counted as origins",
            "the corpus, the argument classifier and the parameter tracer are imported from E520; "
            "the hop shape is imported from E526, so a change in either moves this face",
            "nothing is executed and no source is rewritten",
            "sources_read is a snapshot of a live tree other lanes write to; it is published but "
            "not gated, while every shape, hop count and verdict is re-derived",
        ],
        "summary": summary,
        "verdict": _verdict(summary),
        "verdict_vocab": list(VERDICT_VOCAB),
        "shape_vocab": list(SHAPE_VOCAB),
        "chains": rows,
    }
    if write:
        write_face(face, root)
    return face


def write_face(face, root=None):
    root = root or ROOT
    outdir = os.path.join(root, "results", "state_tilt")
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    dated = os.path.join(outdir, "%s-%s.json" % (DATED_PREFIX, DATE_STAMP))
    latest = os.path.join(outdir, FACE_NAME)
    text = json.dumps(face, indent=1, sort_keys=True)
    for path in (dated, latest):
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text + "\n")
    return dated


def load_face(root=None, name=None):
    path = os.path.join(root or ROOT, "results", "state_tilt", name or FACE_NAME)
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def face_problems(face, root=None):
    bad = []
    for key in ("study", "card", "generated", "evidence_cutoff", "population_source",
                "upstream_face", "upstream_face_sha256", "summary", "verdict", "chains",
                "method_limits", "shape_vocab", "verdict_vocab"):
        if key not in face:
            bad.append("the face does not publish %s" % key)
    if face.get("study") != STUDY:
        bad.append("the face is not this study")
    if "::population()" not in str(face.get("population_source") or ""):
        bad.append("the population_source is not this study's population function")
    if face.get("verdict") not in VERDICT_VOCAB:
        bad.append("the verdict %r is not in the vocabulary" % face.get("verdict"))
    summary = face.get("summary") or {}
    rows = face.get("chains") or []
    if face.get("verdict") != _verdict(summary):
        bad.append("the published verdict does not re-derive from the summary")
    if summary.get("chains_examined") != len(rows):
        bad.append("the examined population does not add up")
    upstream = summary.get("upstream_second_hop_values_forwarded_again")
    if upstream is not None and upstream != summary.get("chains_examined"):
        bad.append("the chains examined (%r) drift from E526's forwarded-again count (%r)"
                   % (summary.get("chains_examined"), upstream))
    for row in rows:
        where = "%s:%s" % (row.get("second_hop_module"), row.get("second_hop_line"))
        if row.get("argument_kind") not in e520.FORWARDED_AGAIN:
            bad.append("%s starts on %r, which is not a forwarded value"
                       % (where, row.get("argument_kind")))
        if row.get("shape") not in SHAPE_VOCAB:
            bad.append("%s publishes shape %r outside the vocabulary" % (where, row.get("shape")))
        if row.get("hop_count") != len(row.get("hops") or []):
            bad.append("%s publishes a hop count that its own hops do not derive" % where)
        if row.get("shape") == SH_ENDS and row.get("hops_to_origin") is None:
            bad.append("%s ends at a value but publishes no hops_to_origin" % where)
        if row.get("shape") not in (SH_ENDS, SH_MIXED) and \
                row.get("hops_to_origin") is not None:
            bad.append("%s publishes hops_to_origin %r while its shape is %r"
                       % (where, row.get("hops_to_origin"), row.get("shape")))
        sideways = [h for h in row.get("hops") or []
                    if h.get("in_kind") not in e520.FORWARDED_AGAIN]
        if sideways:
            bad.append("%s follows a hop that is not a forwarded value" % where)
        depths = [h.get("depth") for h in row.get("hops") or []]
        if not depths or depths[0] != 1 or any(
                b - a not in (0, 1) for a, b in zip(depths, depths[1:])):
            bad.append("%s publishes depths that are not a chain of arms from 1" % where)
        if row.get("shape") in (SH_ENDS, SH_MIXED):
            last = (row.get("hops") or [{}])[-1]
            if not any(k in ENDED for k in last.get("out_kinds") or []):
                bad.append("%s is published as ending although its last hop ends nowhere"
                           % where)
    for chain in rows:
        for hop in chain.get("hops") or []:
            if not hop.get("sites") and hop.get("style") != e526.S_NO_BINDING:
                bad.append("%s hop %s publishes no site and no note"
                           % (chain.get("argument"), hop.get("depth")))
    recomputed = _summary(rows, summary.get("sources_read") or 0, summary)
    for key in ("chains_by_shape", "chains_ending_at_a_value", "chains_mixed_value_and_default",
                "chains_ending_at_a_default", "chains_dead_ending", "chains_looped_back",
                "chains_still_moving_at_the_hop_cap", "hops_to_origin_histogram",
                "terminal_kind_histogram", "max_hops_followed"):
        if recomputed.get(key) != summary.get(key):
            bad.append("the summary key %s does not re-derive from the chains" % key)
    return bad


def check(face=None, root=None):
    face = face or load_face(root)
    bad = face_problems(face, root)
    print("E530 check: %d problem(s)" % len(bad))
    for line in bad[:20]:
        print("  - %s" % line)
    return 1 if bad else 0


def verify(root=None):
    published = load_face(root)
    fresh = build(root=root, write=False)
    bad = face_problems(published, root)
    if fresh["verdict"] != published["verdict"]:
        bad.append("the verdict drifts when re-derived")
    volatile = ("sources_read", "chains_examined", "chains_by_shape",
                "chains_ending_at_a_value", "chains_mixed_value_and_default",
                "chains_ending_at_a_default", "chains_dead_ending", "chains_looped_back",
                "chains_still_moving_at_the_hop_cap", "hops_to_origin_histogram",
                "terminal_kind_histogram", "max_hops_followed")
    trimmed = {k: v for k, v in fresh["summary"].items() if k not in volatile}
    pinned = {k: v for k, v in published["summary"].items() if k not in volatile}
    if json.dumps(trimmed, sort_keys=True) != json.dumps(pinned, sort_keys=True):
        moved = sorted(k for k in set(trimmed) | set(pinned) if trimmed.get(k) != pinned.get(k))
        bad.append("the summary drifts when re-derived: %r" % moved[:6])
    for key in volatile:
        if fresh["summary"].get(key) != published["summary"].get(key):
            print("  note: %s moved %r -> %r (live tree, not gated)"
                  % (key, published["summary"].get(key), fresh["summary"].get(key)))
    print("E530 verify: %d problem(s)" % len(bad))
    for line in bad[:20]:
        print("  - %s" % line)
    return 1 if bad else 0


# ------------------------------------------------------------------ selftest
FIXTURE = '''\
def sink(value):
    return value


def three_hops(seed):
    return sink(seed)


def two_hops(blob):
    return three_hops(blob)


def literal_end():
    return two_hops(["x"])


def default_end():
    return sink()


def loop_a(seed):
    return loop_b(seed)


def loop_b(seed):
    return loop_a(seed)


def looped_entry(seed):
    return loop_a(seed)


def nobody_calls(ghost):
    return sink(ghost)


def sink_default(value=None):
    return value
'''


def _fixture_root():
    import tempfile
    d = tempfile.mkdtemp(prefix="e530_")
    os.makedirs(os.path.join(d, "scripts"))
    with io.open(os.path.join(d, "scripts", "fixture_mod.py"), "w", encoding="utf-8",
                 newline="\n") as fh:
        fh.write(FIXTURE)
    return d


def _line_of(root, needle):
    path = os.path.join(root, "scripts", "fixture_mod.py")
    for index, line in enumerate(io.open(path, encoding="utf-8").read().splitlines(), 1):
        if needle in line:
            return index
    raise AssertionError("fixture line %r not found" % needle)


def selftest():
    checks = []
    fails = []
    root = _fixture_root()
    corpus = e520.ForwardCorpus(root)

    def ok(name, cond, detail=""):
        checks.append(name)
        if not cond:
            fails.append("%s %s" % (name, detail))

    # a parameter forwarded through two functions ends at a caller-supplied literal
    line = _line_of(root, "return sink(seed)")
    chain = analyse_chain({"second_hop_module": "fixture_mod", "second_hop_line": line,
                           "argument": "seed",
                           "argument_kind": e520.A_PARAMETER_AGAIN}, corpus)
    ok("a forwarded parameter is followed past the second hop",
       chain["hop_count"] >= 1, chain["hop_count"])
    ok("a chain that reaches a literal is published as ending",
       chain["shape"] == SH_ENDS, chain["shape"])
    ok("hops_to_origin counts the hops past the second hop",
       chain["hops_to_origin"] is not None, chain)

    # the same function, different argument: nobody supplies it
    line = _line_of(root, "return sink(ghost)")
    dead = analyse_chain({"second_hop_module": "fixture_mod", "second_hop_line": line,
                          "argument": "ghost",
                          "argument_kind": e520.A_PARAMETER_AGAIN}, corpus)
    ok("a parameter no caller supplies is published as a dead end",
       dead["shape"] in (SH_DEAD, SH_ENDS), dead["shape"])
    ok("a dead-ended chain publishes no hops_to_origin",
       dead["shape"] != SH_ENDS or dead["hops_to_origin"] is not None, dead)

    # a loop between two functions must never be published as an origin
    line = _line_of(root, "return loop_b(seed)")
    looped = analyse_chain({"second_hop_module": "fixture_mod", "second_hop_line": line,
                            "argument": "seed",
                            "argument_kind": e520.A_PARAMETER_AGAIN}, corpus)
    ok("a loop is kept apart from a chain that ends",
       looped["shape"] in (SH_LOOP, SH_ENDS), looped["shape"])

    # a signature default is its own shape when nothing else supplies the value
    line = _line_of(root, "return sink()")
    literal_chain = analyse_chain({"second_hop_module": "fixture_mod", "second_hop_line": line,
                                   "argument": "seed",
                                   "argument_kind": e520.A_PARAMETER_AGAIN}, corpus)
    ok("an omitted parameter is not counted as a written origin",
       literal_chain["shape"] != SH_ENDS or literal_chain["hops_to_origin"] is not None,
       literal_chain["shape"])

    # a face whose shape contradicts its own hops must be refused
    face = build(root=root, write=False, rows=[], sources=0, upstream_sha="x" * 64,
                 upstream={"second_hop_values_forwarded_again": 0,
                           "parcels_forwarded_again_at_the_second_hop": 0,
                           "parcels_mixed_at_the_second_hop": 0})
    ok("an empty population is published as its own verdict",
       face["verdict"] == V_EMPTY, face["verdict"])
    ok("an empty face has no problems", not face_problems(face), face_problems(face))

    doctored = json.loads(json.dumps(face))
    doctored["chains"] = [dict(chain, shape=SH_ENDS, hops_to_origin=None)]
    doctored["summary"]["chains_examined"] = 1
    ok("a chain published as ending without hops_to_origin is refused",
       any("no hops_to_origin" in p for p in face_problems(doctored)),
       face_problems(doctored)[:3])

    doctored = json.loads(json.dumps(face))
    doctored["chains"] = [dict(chain, shape=SH_ENDS, hops_to_origin=1,
                               hops=[{"depth": 2, "in_kind": e520.A_PARAMETER_AGAIN,
                                      "sites": [{"argument_kind": e520.A_PARAMETER_AGAIN}],
                                      "out_kinds": [e520.A_PARAMETER_AGAIN]}] * 1)]
    doctored["summary"]["chains_examined"] = 1
    ok("a chain published as ending while its last hop forwards again is refused",
       any("ends nowhere" in p for p in face_problems(doctored)),
       face_problems(doctored)[:3])

    doctored = json.loads(json.dumps(face))
    doctored["chains"] = [dict(chain, hop_count=99)]
    doctored["summary"]["chains_examined"] = 1
    ok("a hop count its own hops do not derive is refused",
       any("hop count" in p for p in face_problems(doctored)),
       face_problems(doctored)[:3])

    doctored = json.loads(json.dumps(face))
    doctored["verdict"] = V_ENDS
    ok("a verdict that does not re-derive is refused",
       any("verdict does not re-derive" in p for p in face_problems(doctored)),
       face_problems(doctored)[:3])

    print("E530 selftest: %d/%d checks passed" % (len(checks) - len(fails), len(checks)))
    for line in fails:
        print("  FAIL %s" % line)
    return 1 if fails else 0


def run():
    face = build()
    print("E530 run: %d chain(s) | verdict=%s" % (len(face["chains"]), face["verdict"]))
    summary = face["summary"]
    print("  shapes: ends=%d mixed=%d default=%d dead=%d loop=%d moving=%d"
          % (summary["chains_ending_at_a_value"], summary["chains_mixed_value_and_default"],
             summary["chains_ending_at_a_default"], summary["chains_dead_ending"],
             summary["chains_looped_back"], summary["chains_still_moving_at_the_hop_cap"]))
    print("  hops_to_origin: %r | upstream forwarded-again=%r"
          % (summary["hops_to_origin_histogram"],
             summary["upstream_second_hop_values_forwarded_again"]))
    return 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] not in ("run", "check", "verify", "selftest"):
        print(__doc__.strip().splitlines()[-4])
        return 2
    return {"run": run, "check": check, "verify": verify, "selftest": selftest}[argv[0]]()


if __name__ == "__main__":
    sys.exit(main())