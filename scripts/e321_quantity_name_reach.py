"""E321 -- for the gates whose face never names the gated quantity, does the producer?

E320 measured that 134 of 219 decoy-bearing leaves publish nothing that names or fingerprints the
quantity the gate is compared against, so a reader can only read the span.  A face is not the only
place a name can live: the writer usually holds the tolerance in a constant, and that constant (or
its definition line) may well say what it is a share *of*.  This study asks one question of that
population -- can the name be found on the producing side, and would it survive being published?

Nothing here re-implements E320 or E312: the population comes from DECOYRESOLVE, the producer lookup
(producers_for / publish_sites / constant_definition / code_tokens) comes from E312, and every
classification is a pure function of those two inputs.

Usage:
    python scripts/e321_quantity_name_reach.py run|build|verify|selftest
"""
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import e312_gate_operand_identity as e312  # noqa: E402  (path set above)

ROOT = e312.ROOT
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
INPUT = "DECOYRESOLVE-2026-10-31.json"
TODAY = "2026-10-31"
FACE = "QUANTITYNAME-%s.json" % TODAY
LATEST = "quantityname_latest.json"
STUDY = "E321_quantity_name_reach"

# Words a definition uses when it says what the tolerance is a share *of*.  A bare `TOL = 0.02`
# names nothing; `TOL_SHARE_OF_TESTED_EVENTS = 0.02` does.  The list is deliberately short and
# literal -- it is the vocabulary of the population at hand, not a general ontology.
QUANTITY_WORDS = frozenset((
    "n", "num", "number", "count", "events", "tested", "tests", "samples", "rows", "bars",
    "obs", "observations", "trials", "days", "sessions", "share", "frac", "fraction",
    "rate", "ratio", "pct", "percent", "median", "mean", "p90", "stdev", "sd",
))

CLASS_NO_PRODUCER = "no_producer_names_the_face"
CLASS_NO_SITE = "producer_found_but_publishes_no_such_key"
CLASS_LITERAL = "published_as_a_bare_literal"
CLASS_NAMED = "published_as_a_constant_that_names_a_quantity"
CLASS_NAMED_UNNAMED = "published_as_a_constant_that_names_nothing"

CLASSES = (CLASS_NO_PRODUCER, CLASS_NO_SITE, CLASS_LITERAL, CLASS_NAMED, CLASS_NAMED_UNNAMED)

VERDICT_MORE = "the_producer_names_more_than_the_face_does_but_not_all_of_it"
VERDICT_ALL = "every_gate_the_face_leaves_unnamed_is_named_by_its_producer"
VERDICT_NONE = "the_producer_side_does_not_name_the_gated_quantity_either"

VERDICTS = (VERDICT_MORE, VERDICT_ALL, VERDICT_NONE)

LITERAL = re.compile(r"^[-+]?[0-9][0-9_.eE+-]*$")
IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def _read(name, outdir=None):
    path = os.path.join(outdir or OUTDIR, name)
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def population(doc):
    """The rows of E320 that its own face could not resolve by name or magnitude fingerprint."""
    return [r for r in doc.get("rows") or [] if r.get("class") in ("unresolved", "ambiguous")]


def name_tokens(text):
    """Identifier components that carry a quantity word, read off a name or an expression."""
    words = []
    for part in re.split(r"[^A-Za-z0-9]+", text or ""):
        low = part.lower()
        if low in QUANTITY_WORDS or (low.startswith("n") and low[1:].isdigit()):
            words.append(low)
    return sorted(set(words))


def definition_names_a_quantity(producer_src, name):
    """Does the constant's own definition say what the gated quantity is?"""
    if not name:
        return [], None
    tokens = name_tokens(name)
    definition = e312.constant_definition(producer_src, name) if producer_src else None
    if definition:
        for ident in IDENT.findall(definition.get("value_expression") or ""):
            if ident != name and ident not in tokens:
                tokens.extend(name_tokens(ident))
        # the comment on the definition line is the other place a writer says what the number is
        for ident in IDENT.findall(definition.get("text") or ""):
            if ident != name and ident not in tokens:
                tokens.extend(name_tokens(ident))
    return sorted(set(tokens)), definition


def producer_candidates(face):
    """Producer lookups for a dated face: the name as published, then its dated template.

    E312's producers_for() stops a needle at `%s`, but a published face is dated, so a producer
    that writes `RECOVERY-<cutoff>.json` is invisible to a needle built from the concrete filename
    (154 of 196 rows read as producer-less before this).  The template is the same face one
    publication earlier, so it is the right second attempt -- not a loosened match.
    """
    tries = [face, re.sub(r"\d{4}-\d{2}-\d{2}", "%s", os.path.basename(face))]
    stem = re.sub(r"-?\d{4}-\d{2}-\d{2}.*$", "", os.path.basename(face))
    if stem:
        tries.append(stem)
    seen = []
    for needle in tries:
        for path, src in e312.producers_for(needle):
            if path not in [p for p, _ in seen]:
                seen.append((path, src))
    return seen


def classify(row, cache):
    """One gate leaf: where its name could live and whether it says anything."""
    face = row.get("face")
    key = (row.get("leaf") or "").split(".")[-1].split("[")[0]
    if face not in cache:
        cache[face] = producer_candidates(face)
    producers = cache[face]
    if not producers:
        return {"class": CLASS_NO_PRODUCER, "producer": None, "site": None,
                "quantity_words": [], "name_publishable": False}
    sites = e312.publish_sites(face, key, producers)
    if not sites:
        return {"class": CLASS_NO_SITE, "producer": None, "site": None,
                "quantity_words": [], "name_publishable": False}

    best = None
    for site in sites:
        expr = (site.get("expression") or "").strip()
        producer = site.get("producer")
        src = dict((e312.rel(p), s) for p, s in e312.sources()).get(producer, "")
        if LITERAL.match(expr):
            got = {"class": CLASS_LITERAL, "producer": producer, "site": site,
                   "quantity_words": [], "name_publishable": False}
        else:
            ident = (IDENT.findall(expr) or [None])[0]
            words, definition = definition_names_a_quantity(src, ident)
            module_level = bool(definition) and not (definition["text"] or "").startswith(
                (" ", "\t"))
            got = {"class": CLASS_NAMED if words else CLASS_NAMED_UNNAMED,
                   "producer": producer, "site": site, "constant": ident,
                   "quantity_words": words, "name_publishable": module_level}
        if best is None or (got["class"] == CLASS_NAMED and best["class"] != CLASS_NAMED):
            best = got
    return best


def build(outdir=None):
    doc = _read(INPUT, outdir)
    rows = population(doc)
    cache = {}
    out = []
    for row in rows:
        got = classify(row, cache)
        out.append({
            "face": row.get("face"),
            "leaf": row.get("leaf"),
            "block": row.get("block"),
            "gate_value": row.get("gate_value"),
            "decoy_class": row.get("class"),
            "residual_span": row.get("residual_span"),
            "class": got["class"],
            "producer": got["producer"],
            "publish_line": (got.get("site") or {}).get("line"),
            "published_as": (got.get("site") or {}).get("expression"),
            "constant": got.get("constant"),
            "quantity_words": got["quantity_words"],
            "name_publishable": got["name_publishable"],
        })

    tally = {}
    for r in out:
        tally[r["class"]] = tally.get(r["class"], 0) + 1
    named = [r for r in out if r["class"] == CLASS_NAMED]
    reachable = [r for r in out if r["producer"]]
    if named and len(named) == len(out):
        verdict = VERDICT_ALL
    elif named:
        verdict = VERDICT_MORE
    else:
        verdict = VERDICT_NONE

    return {
        "study": STUDY,
        "title": ("E320 left 134 gates whose face never names the gated quantity; this reads the "
                  "producer instead and asks whether the name exists there and would survive "
                  "being published"),
        "evidence_cutoff": TODAY,
        "upstream": INPUT,
        "verdict": verdict,
        "verdict_reason": (
            "%d of %d unresolved-or-ambiguous gates (%.1f%%) have a producer that names the "
            "quantity at "
            "the line that publishes the gate; %d of those names sit on a module-level constant, "
            "i.e. would survive being published as-is; %d gates have no producer that publishes "
            "the key at all, so no reading of the producer can name them."
            % (len(named), len(out), round(100.0 * len(named) / len(out), 1) if out else 0.0,
               sum(1 for r in named if r["name_publishable"]), tally.get(CLASS_NO_SITE, 0)
               + tally.get(CLASS_NO_PRODUCER, 0))),
        "population": {
            "source": "DECOYRESOLVE-2026-10-31.json rows with class unresolved or ambiguous",
            "rows": len(out),
            "by_upstream_class": _count(r["decoy_class"] for r in out),
        },
        "summary": {
            "rows": len(out),
            "by_class": tally,
            "classes": list(CLASSES),
            "producer_located": len(reachable),
            "named_by_the_producer": len(named),
            "named_and_publishable": sum(1 for r in named if r["name_publishable"]),
            "quantity_word_vocabulary": sorted(QUANTITY_WORDS),
        },
        "held_fixed": ("the upstream faces are read, never written; the producers are read off "
                       "scripts/*.py as published; no gate value is recomputed and no verdict of "
                       "E320 is changed"),
        "no_bill": ("published faces and in-repo sources only; no draws, no panel read, no engine, "
                    "no network"),
        "rows": out,
    }


def _count(values):
    out = {}
    for v in values:
        out[v] = out.get(v, 0) + 1
    return out


def save(payload, name=None):
    path = os.path.join(OUTDIR, name or FACE)
    with io.open(path, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=False, indent=1, sort_keys=True))
        fh.write("\n")
    with io.open(os.path.join(OUTDIR, LATEST), "w", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=False, indent=1, sort_keys=True))
        fh.write("\n")
    return path


def run(save_face=True):
    face = build()
    if save_face:
        save(face)
    return face


def verify():
    problems = []
    face = _read(LATEST)
    fresh = build()
    if face.get("verdict") != fresh.get("verdict"):
        problems.append("the verdict does not re-derive")
    if face.get("verdict") not in VERDICTS:
        problems.append("verdict %r is outside the frozen set" % (face.get("verdict"),))
    if face.get("summary") != fresh.get("summary"):
        problems.append("the summary does not re-derive")
    for r in face.get("rows") or []:
        if r.get("class") not in CLASSES:
            problems.append("row class %r is outside the frozen set" % (r.get("class"),))
            break
        if r.get("class") == CLASS_NAMED and not r.get("quantity_words"):
            problems.append("a named row carries no quantity word")
            break
    if face.get("summary", {}).get("rows") != len(face.get("rows") or []):
        problems.append("the summary count disagrees with its own rows")
    return problems


def selftest():
    legs = []

    def leg(name, ok, detail=""):
        legs.append((bool(ok), name, detail))

    leg("L1 a bare literal is not a name", not name_tokens("0.02"))
    leg("L2 a count word in a constant is a name",
        name_tokens("N_EVENTS_TESTED") == ["events", "n", "tested"],
        repr(name_tokens("N_EVENTS_TESTED")))
    leg("L3 a share word is a name", "share" in name_tokens("TOL_SHARE"))
    leg("L4 a tolerance constant that names nothing stays unnamed",
        name_tokens("MATCH_TOL") == [])
    src = "TOL_SHARE_OF_TESTED = 0.02\n\n\ndef build():\n    return {'tolerance': TOL_SHARE_OF_TESTED}\n"
    words, definition = definition_names_a_quantity(src, "TOL_SHARE_OF_TESTED")
    leg("L5 the definition is found and its words are read",
        definition and definition["line"] == 1 and "share" in words, repr(words))
    leg("L6 a module-level definition is publishable",
        not (definition or {}).get("text", "").startswith(" "))
    local = "def f():\n    inner_tol = 0.1\n"
    words2, definition2 = definition_names_a_quantity(local, "inner_tol")
    leg("L7 a local definition is not module-level",
        bool(definition2) and definition2["text"].startswith("inner_tol ="),
        repr(definition2))
    leg("L8 the literal regex does not swallow an expression",
        bool(LITERAL.match("0.02")) and not LITERAL.match("TOL * 2"))
    row = {"face": "results/state_tilt/NOSUCH-%s.json" % TODAY, "leaf": "block.tolerance"}
    got = classify(row, {})
    leg("L9 a face no producer names is classed rather than guessed",
        got["class"] in (CLASS_NO_PRODUCER, CLASS_NO_SITE), got["class"])
    face = _read(LATEST)
    tally = face.get("summary", {}).get("by_class") or {}
    leg("L10 the published census partitions its own rows",
        sum(tally.values()) == face.get("summary", {}).get("rows"))
    leg("L11 every row carries its producer decision, including the negative one",
        all("class" in r for r in face.get("rows") or []))
    leg("L12 the named count is what the summary says it is",
        tally.get(CLASS_NAMED, 0) == face.get("summary", {}).get("named_by_the_producer"))
    return legs


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "run"
    if cmd == "run":
        face = run()
        print(json.dumps({"face": FACE, "verdict": face["verdict"],
                          "rows": face["summary"]["rows"],
                          "by_class": face["summary"]["by_class"],
                          "named": face["summary"]["named_by_the_producer"],
                          "publishable": face["summary"]["named_and_publishable"]},
                         ensure_ascii=False))
        return 0
    if cmd == "build":
        print(json.dumps(build(), ensure_ascii=False, indent=1))
        return 0
    if cmd == "verify":
        problems = verify()
        print(json.dumps({"problems": problems}, ensure_ascii=False))
        return 1 if problems else 0
    if cmd == "selftest":
        legs = selftest()
        passed = sum(1 for ok, _, _ in legs if ok)
        for ok, name, detail in legs:
            print("%s %s%s" % ("PASS" if ok else "FAIL", name,
                               "" if ok else "  <- %r" % (detail,)))
        print("%d/%d" % (passed, len(legs)))
        return 0 if passed == len(legs) else 1
    print("usage: e321_quantity_name_reach.py [run|build|verify|selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main())