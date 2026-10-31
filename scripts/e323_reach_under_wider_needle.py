"""E323 -- re-price E321's five classes with E322's wider needle.

E321 read the producing side of all 196 unresolved-or-ambiguous gate leaves and reported that 21
of them (10.7 pct) are named by a constant that says what the gated quantity is a share *of*.
E322 then showed that the same lookup refuses four faces for purely mechanical reasons: it drops
the auditor's own file from the ownership corpus, it substitutes ISO dates only (this repo also
dates faces compactly, ``CASHLeg-20261027``), and it never tries a name composed from a format
string (``f"p1e_nulls_{cls}.json"``).  A needle that refuses faces also bounds every row it
classified, so the 10.7 pct is a lower bound of unknown tightness.

This study re-runs E321's census over the WHOLE population under the wider needle and publishes
every class that moves.  Nothing is re-implemented: the population, the classifier, the
publish-site reader and the "does this line write the face" test all come from E321; the corpus
and the needle vocabulary come from E322.

One step is deliberately NOT inherited from E322: E322 asked only whether a writer *names* a face
(a census of ownership), while a producer has to *write* it.  Every wider hit therefore passes
E321's ``writes_the_face`` gate, and the mentions that gate rejects are counted and published --
otherwise a composed prefix such as ``p1e`` would hand this study any script that assigns a
variable whose name starts the same way.

Usage:
    python scripts/e323_reach_under_wider_needle.py run|build|verify|selftest
"""
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import e312_gate_operand_identity as e312  # noqa: E402  (path set above)
import e321_quantity_name_reach as e321  # noqa: E402
import e322_residual_refusal_causes as e322  # noqa: E402

ROOT = e312.ROOT
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
INPUT = "QUANTITYNAME-2026-10-31.json"
TODAY = "2026-10-31"
FACE = "REACHWIDE-%s.json" % TODAY
LATEST = "reachwide_latest.json"
STUDY = "E323_reach_under_wider_needle"

ISO_DATE = e322.ISO_DATE
COMPACT_DATE = e322.COMPACT_DATE

# The steps, in the order they are attempted.  The order IS the taxonomy: first step that lands a
# writer is the one reported, so a face reached by the literal name is never credited to a prefix.
STEPS = ("literal", "basename", "iso", "compact", "stem", "composed")

# Attribution rule.  A needle that is the face's own path, its own filename or its own dated
# template can only land the script that names THAT face.  A compact-date template or a name
# prefix cannot: `etf_book_bakeoff.json` composes to `etf_book`, which 106 scripts contain, and a
# prefix hit is a family membership, not ownership.  So the narrow steps define a face's producer
# set when they reach anything at all, and the wide steps are only used for faces nothing narrow
# reaches -- which is exactly the population E322 measured.  The naively accumulated set is still
# built and published as ``class_naive`` so the contamination is a number, not an opinion.
NARROW_STEPS = ("literal", "basename", "iso", "stem")
WIDE_STEPS = ("compact", "composed")

VERDICT_MORE = "the_wider_needle_names_more_gates_so_the_published_share_was_a_lower_bound"
VERDICT_RELOCATES = "the_wider_needle_moves_rows_between_classes_without_naming_anything_new"
VERDICT_SAME = "the_wider_needle_changes_nothing_so_the_named_share_is_a_repository_fact"

VERDICTS = (VERDICT_MORE, VERDICT_RELOCATES, VERDICT_SAME)


# -------------------------------------------------------------------------------- corpus
_SRC = None


def corpus():
    """Every python source under the producing packages, THIS scanner excluded.

    E312's ``sources()`` drops itself, which is why a face written by E312 can never find its
    producer (E322's first cause).  Here every auditor is kept -- E312, E321 and E322 included --
    and only this file is removed, because it spells the very filenames it searches for (the
    E204/r1232 self-inclusion trap: the first burn resolved two faces to "the writer spells the
    name" and the writer was the scanner).
    """
    global _SRC
    if _SRC is not None:
        return _SRC
    own = os.path.abspath(__file__)
    out = []
    for sub in ("scripts", "Tools", "live", "monitor", "firm"):
        base = os.path.join(ROOT, sub)
        for dirpath, _dirs, files in os.walk(base):
            for fn in sorted(files):
                if not fn.endswith(".py"):
                    continue
                path = os.path.join(dirpath, fn)
                if os.path.abspath(path) == own:
                    continue
                try:
                    with io.open(path, encoding="utf-8", errors="replace") as fh:
                        out.append((path, fh.read()))
                except OSError:
                    continue
    _SRC = out
    return _SRC


def install_corpus(corpus_files):
    """Hand the wider corpus to E312's classifier.

    ``e321.classify`` reads the constant's definition through ``e312.sources()``; if the producers
    it is given come from a corpus E312 does not know about, every widened producer would resolve
    to an empty source and be classed "names nothing" -- a silent re-refusal.  The globals are set
    here so the reused classifier reads the same corpus for producers and for definitions.
    """
    e312._SRC = corpus_files
    e312._OWN = None
    return len(e312.sources())


_TOKENS = {}
_ORIG_CODE_TOKENS = e312.code_tokens


def _memo_code_tokens(src):
    """Tokenise each source once (identity-keyed, holding the text so the key cannot be reused).

    Not an optimisation of convenience: a composed prefix reaches hundreds of scripts and the
    reused write gate re-tokenises a whole file per hit, which put this leg at 198s in the chain
    for a 51-face population. The cache changes nothing about the answer -- same function, same
    output, called once per text.
    """
    hit = _TOKENS.get(id(src))
    if hit is not None and hit[0] is src:
        return hit[1]
    got = _ORIG_CODE_TOKENS(src)
    _TOKENS[id(src)] = (src, got)
    return got


e312.code_tokens = _memo_code_tokens


# -------------------------------------------------------------------------------- needle
def _strip_markers(text):
    """Cut a name at its template marker, KEEPING the directory part.

    ``e322.strip_to_needle`` basenames on the way, which is right for a corpus that searches
    filenames and wrong here: it turned the literal step into the bare filename, and a bare
    filename shared by a whole family of scripts (``etf_book_voltarget_phase.json`` is named by
    106 of them) hands the classifier 106 producers, any one of which may publish a key with the
    same name for a DIFFERENT gate.  That first burn moved 7 rows to "named" through exactly such
    a cross-script site.  The literal step keeps its path; the basename step is separate.
    """
    out = text
    for marker in ("%s", "*", "{"):
        out = out.split(marker)[0]
    return out


def needles_for(face):
    """Ordered (step, needle) attempts for one face under the wider needle."""
    base = os.path.basename(face)
    out = []

    def add(step, needle):
        needle = _strip_markers(needle)
        if len(needle) < 3:
            return
        if (step, needle) not in out:
            out.append((step, needle))

    add("literal", face)
    add("basename", base)
    if ISO_DATE.search(base):
        add("iso", ISO_DATE.sub("%s", base))
    if COMPACT_DATE.search(base):
        add("compact", COMPACT_DATE.sub("%s", base))
    stem = re.sub(r"-?\d{4}-\d{2}-\d{2}.*$", "", base)
    if stem:
        add("stem", stem)
    for prefix in e322.name_prefixes(base):
        add("composed", prefix)
    return out


def wider_producers(face, corpus_files=None):
    """(first_step, first_needle, writers_by_step, rejected_mentions) for one face.

    ``writers_by_step`` maps each step that landed at least one writer to its writer list.  It is
    kept per step rather than flattened because a flattened list is what let ``etf_book`` (106
    scripts) pass itself off as the producer of seven different book faces.
    """
    src = corpus_files if corpus_files is not None else corpus()
    rejected = []
    first_step, first_needle = None, None
    by_step = {}
    for step, needle in needles_for(face):
        hits = [(p, s) for p, s in src if needle in s]
        got = [(p, s) for p, s in hits if e321.writes_the_face(s, needle)]
        rejected.extend((step, e312.rel(p)) for p, _s in hits if (p, _s) not in got)
        if got:
            by_step[step] = _dedupe(got)
            if first_step is None:
                first_step, first_needle = step, needle
    return first_step, first_needle, by_step, rejected


def _dedupe(pairs):
    out, seen = [], set()
    for path, text in pairs:
        if path in seen:
            continue
        seen.add(path)
        out.append((path, text))
    return out


def attended_writers(by_step):
    """The producer set under the attribution rule: narrow steps win, wide steps only as fallback."""
    narrow = []
    for step in NARROW_STEPS:
        narrow.extend(by_step.get(step) or [])
    if narrow:
        return _dedupe(narrow), "narrow"
    wide = []
    for step in WIDE_STEPS:
        wide.extend(by_step.get(step) or [])
    return _dedupe(wide), "wide" if wide else "unreached"


def naive_writers(by_step):
    """Every writer every step reached -- the contaminated set, published for comparison."""
    out = []
    for step in STEPS:
        out.extend(by_step.get(step) or [])
    return _dedupe(out)


# -------------------------------------------------------------------------------- build
def _read(name):
    with io.open(os.path.join(OUTDIR, name), encoding="utf-8") as fh:
        return json.load(fh)


def build():
    doc = _read(INPUT)
    rows = population(doc)
    src = corpus()
    install_corpus(src)

    cache = {}
    out = []
    for row in rows:
        face = row.get("face")
        if face not in cache:
            step, needle, by_step, rejected = wider_producers(face, src)
            writers, basis = attended_writers(by_step)
            cache[face] = {"step": step, "needle": needle, "by_step": by_step,
                           "writers": writers, "basis": basis, "rejected": rejected,
                           "naive": naive_writers(by_step)}
        entry = cache[face]
        got = e321.classify(row, {face: entry["writers"]})
        naive = e321.classify(row, {face: entry["naive"]})
        out.append({
            "face": face,
            "leaf": row.get("leaf"),
            "block": row.get("block"),
            "class_before": row.get("class"),
            "class_after": got["class"],
            "class_naive": naive["class"],
            "moved": got["class"] != row.get("class"),
            "moved_naively": naive["class"] != row.get("class"),
            "producer_before": row.get("producer"),
            "producer_after": got["producer"],
            "producer_naive": naive["producer"],
            "attribution": entry["basis"],
            "step": entry["step"],
            "needle": entry["needle"],
            "writers": sorted(e312.rel(p) for p, _s in entry["writers"]),
            "writers_by_step": dict((k, sorted(e312.rel(p) for p, _s in v))
                                    for k, v in entry["by_step"].items()),
            "mentions_rejected": sorted(set(w for _st, w in entry["rejected"])),
            "quantity_words": got["quantity_words"],
            "quantity_words_naive": naive["quantity_words"],
            "name_publishable": got["name_publishable"],
        })

    before = _count(r["class_before"] for r in out)
    after = _count(r["class_after"] for r in out)
    naive_after = _count(r["class_naive"] for r in out)
    named_before = before.get(e321.CLASS_NAMED, 0)
    named_after = after.get(e321.CLASS_NAMED, 0)
    named_naive = naive_after.get(e321.CLASS_NAMED, 0)
    moves = [r for r in out if r["moved"]]
    transitions = {}
    for r in moves:
        key = "%s -> %s" % (r["class_before"], r["class_after"])
        transitions[key] = transitions.get(key, 0) + 1
    by_step = _count(r["step"] or "unreached" for r in out)
    by_basis = _count(r["attribution"] for r in out)
    gain = named_after - named_before

    # A name the naive set would award and the attribution rule refuses: this is the false-positive
    # volume of the wider needle, and every one of them has to be listed, not summarised away.
    rejected_gains = [r for r in out
                      if r["class_naive"] == e321.CLASS_NAMED and r["class_after"] != e321.CLASS_NAMED]

    if named_after > named_before:
        verdict = VERDICT_MORE
    elif moves:
        verdict = VERDICT_RELOCATES
    else:
        verdict = VERDICT_SAME

    worse = sum(1 for r in moves if _rank(r["class_after"]) > _rank(r["class_before"]))
    reason = (
        "%d rows re-classified under the wider needle (%d corpus files): %d rows move class, %d "
        "of them to a LESS named class, and the named count goes %d -> %d. The named share was "
        "%.1f pct with the literal needle and is %.1f pct now. A naively accumulated producer "
        "set would report %d named rows, but all %d of the extra names come from family needles "
        "(a composed prefix or a sibling filename) rather than from the face's own path, so "
        "attribution refuses them and the published figure is the attended one."
        % (len(out), len(src), len(moves), worse, named_before, named_after,
           100.0 * named_before / len(out) if out else 0.0,
           100.0 * named_after / len(out) if out else 0.0,
           named_naive, len(rejected_gains)))

    return {
        "study": STUDY,
        "title": ("E321's named share was measured with a needle that refuses four faces; re-run "
                  "the five-class census over the whole population with E322's wider needle"),
        "evidence_cutoff": TODAY,
        "upstream": INPUT,
        "verdict": verdict,
        "verdict_reason": reason,
        "population": {
            "source": "QUANTITYNAME-%s.json rows (all classes, not only the unowned ones)" % TODAY,
            "rows": len(out),
            "faces": len(set(r["face"] for r in out)),
            "faces_cache": len(cache),
        },
        "summary": {
            "rows": len(out),
            "by_class_before": before,
            "by_class_after": after,
            "by_class_naive": naive_after,
            "named_before": named_before,
            "named_after": named_after,
            "named_naive": named_naive,
            "name_gains_rejected": len(rejected_gains),
            "named_share_before_pct": round(100.0 * named_before / len(out), 1) if out else 0.0,
            "named_share_after_pct": round(100.0 * named_after / len(out), 1) if out else 0.0,
            "rows_moved": len(moves),
            "rows_moved_to_a_less_named_class": worse,
            "transitions": transitions,
            "by_step": by_step,
            "by_attribution": by_basis,
            "steps": list(STEPS),
            "narrow_steps": list(NARROW_STEPS),
            "wide_steps": list(WIDE_STEPS),
            "steps_that_reached_a_writer": sorted(k for k in by_step if k != "unreached"),
            "mentions_rejected": sum(len(r["mentions_rejected"]) for r in out),
            "max_writers_on_one_face": max(len(r["writers"]) for r in out) if out else 0,
            "max_naive_writers_on_one_face": max(
                len(r["writers_by_step"]) and sum(len(v) for v in r["writers_by_step"].values())
                for r in out) if out else 0,
            "corpus_files": len(src),
            "corpus_keeps_the_other_auditors": True,
            "corpus_self_excluded": os.path.basename(os.path.abspath(__file__)),
            "corpus_installed_into_upstream": True,
        },
        "held_fixed": ("every gate value, every row of the upstream face and every class of E320 is "
                       "read, never rewritten; only the producer needle moves"),
        "no_bill": ("published faces and in-repo sources only; no draws, no panel read, no engine, "
                    "no network"),
        "rejected_name_gains": [
            {"face": r["face"], "leaf": r["leaf"], "class_after": r["class_after"],
             "producer_naive": r["producer_naive"], "step": r["step"],
             "attribution": r["attribution"]}
            for r in rejected_gains],
        "rows": out,
    }


CLASS_ORDER = (e321.CLASS_NO_PRODUCER, e321.CLASS_NO_SITE, e321.CLASS_LITERAL,
               e321.CLASS_NAMED_UNNAMED, e321.CLASS_NAMED)


def _rank(cls):
    """How named a class is: 0 = no producer at all, 4 = a constant that names the quantity."""
    try:
        return CLASS_ORDER.index(cls)
    except ValueError:
        return -1


def population(doc):
    return list(doc.get("rows") or [])


def _count(values):
    out = {}
    for v in values:
        out[v] = out.get(v, 0) + 1
    return out


# -------------------------------------------------------------------------------- io / verify
def save(payload, name=None):
    os.makedirs(OUTDIR, exist_ok=True)
    text = json.dumps(payload, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    path = os.path.join(OUTDIR, name or FACE)
    for target in (path, os.path.join(OUTDIR, LATEST)):
        with io.open(target, "w", encoding="utf-8") as fh:
            fh.write(text)
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
    rows = face.get("rows") or []
    if len(rows) != (face.get("summary") or {}).get("rows"):
        problems.append("the rows do not match the summary count")
    upstream = _read(INPUT)
    before = dict(((r.get("face"), r.get("leaf")), r.get("class"))
                  for r in upstream.get("rows") or [])
    for r in rows:
        if r.get("class_after") not in e321.CLASSES:
            problems.append("row class %r is outside the frozen set" % (r.get("class_after"),))
            break
        if before.get((r.get("face"), r.get("leaf"))) != r.get("class_before"):
            problems.append("a row's before-class is not the upstream face's class")
            break
        if r.get("moved") != (r.get("class_before") != r.get("class_after")):
            problems.append("a row's moved flag disagrees with its two classes")
            break
    named = sum(1 for r in rows if r.get("class_after") == e321.CLASS_NAMED)
    if named != (face.get("summary") or {}).get("named_after"):
        problems.append("the named count disagrees with the rows")
    if (face.get("summary") or {}).get("named_before") != (upstream.get("summary") or {}).get(
            "named_by_the_producer"):
        problems.append("named_before is not the upstream face's own named count")
    return problems


def selftest():
    legs = []

    def leg(name, ok, detail=""):
        legs.append((bool(ok), name, detail))

    leg("L1 a compact-dated face offers a compact step",
        "compact" in [s for s, _n in needles_for("results/state_tilt/CASHLeg-20261027.json")])
    leg("L2 an ISO-dated face offers an iso step",
        "iso" in [s for s, _n in needles_for("results/state_tilt/REPRO-2026-10-31.json")])
    leg("L3 the step order runs literal before stem before composed",
        [s for s, _n in needles_for("results/state_tilt/p1e_nulls_M_arc-2026-10-31.json")][:6]
        == ["literal", "basename", "iso", "stem", "composed", "composed"],
        repr([s for s, _n in needles_for("results/state_tilt/p1e_nulls_M_arc-2026-10-31.json")]))
    leg("L4 a template marker is stripped before the search",
        e322.strip_to_needle("GATEOPERANDS-%s.json") == "GATEOPERANDS-")
    leg("L5 a too-short needle is refused",
        all(len(n) >= 3 for _s, n in needles_for("a_b.json")))
    src = [("scripts/fake_writer.py", 'FACE = "CASHLeg-%s.json" % d\n')]
    step, needle, by_step, _rej = wider_producers("results/state_tilt/CASHLeg-20261027.json", src)
    leg("L6 the compact step reaches a format-string writer",
        step == "compact" and len(by_step.get("compact") or []) == 1,
        "%r %r %r" % (step, needle, sorted(by_step)))
    mention = [("scripts/fake_quoter.py",
                '"""We resolved CASHLeg-20261027 above."""\nSOMETHING = 1\n')]
    step2, _n2, by_step2, rej2 = wider_producers(
        "results/state_tilt/CASHLeg-20261027.json", mention)
    leg("L7 a source that only MENTIONS the face is rejected (E321's write gate is inherited)",
        not by_step2 and rej2, "%r %r" % (by_step2, rej2))
    corpus_files = corpus()
    leg("L8 this scanner is not in its own corpus (r1232 self-inclusion trap)",
        not any(os.path.abspath(p) == os.path.abspath(__file__) for p, _s in corpus_files))
    leg("L9 the other auditors ARE in the corpus (E312's self-exclusion is the defect under test)",
        any(os.path.basename(p).startswith("e312_") for p, _s in corpus_files)
        and any(os.path.basename(p).startswith("e322_") for p, _s in corpus_files))
    leg("L10 the corpus is installed into E312 so definitions resolve",
        install_corpus(corpus_files) == len(corpus_files) and len(e312.sources()) == len(corpus_files))
    doc = _read(INPUT)
    leg("L11 the population is every row, not only the unowned ones",
        len(population(doc)) == len(doc.get("rows") or [])
        and len(population(doc)) > sum(1 for r in doc.get("rows") or []
                                       if r.get("class") == e321.CLASS_NO_PRODUCER))
    leg("L12 the class ranking puts the unowned class below the named one",
        _rank(e321.CLASS_NO_PRODUCER) < _rank(e321.CLASS_NAMED)
        and _rank(e321.CLASS_NAMED_UNNAMED) < _rank(e321.CLASS_NAMED))
    face = _read(LATEST)
    rows = face.get("rows") or []
    summ = face.get("summary") or {}
    leg("L13 the published rows partition into the before and after tallies",
        _count(r.get("class_after") for r in rows) == summ.get("by_class_after")
        and _count(r.get("class_before") for r in rows) == summ.get("by_class_before"))
    leg("L14 the transitions tally equals the moved rows",
        sum((summ.get("transitions") or {}).values()) == summ.get("rows_moved"))
    leg("L15 the verdict is inside the frozen set", face.get("verdict") in VERDICTS)
    leg("L16 a row whose producer set came from the NARROW steps keeps the upstream producer "
        "(the wide steps may add a face, never re-attribute one)",
        not [r for r in rows if not r.get("moved") and r.get("attribution") == "narrow"
             and r.get("producer_after") != r.get("producer_before")],
        repr([r.get("face") for r in rows if not r.get("moved")
              and r.get("attribution") == "narrow"
              and r.get("producer_after") != r.get("producer_before")][:3]))
    leg("L17 the rejected name gains are exactly the naive-minus-attended difference",
        len(face.get("rejected_name_gains") or []) == max(
            0, summ.get("named_naive", 0) - summ.get("named_after", 0)),
        "%r vs %r" % (len(face.get("rejected_name_gains") or []),
                      summ.get("named_naive", 0) - summ.get("named_after", 0)))
    leg("L18 the attribution rule can only shrink a producer set",
        all(set(r.get("writers") or []) <= set(
            w for v in (r.get("writers_by_step") or {}).values() for w in v) for r in rows))
    return legs


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "run"
    if cmd == "run":
        face = run()
        print(json.dumps({"face": FACE, "verdict": face["verdict"],
                          "rows": face["summary"]["rows"],
                          "named_before": face["summary"]["named_before"],
                          "named_after": face["summary"]["named_after"],
                          "rows_moved": face["summary"]["rows_moved"],
                          "transitions": face["summary"]["transitions"],
                          "by_step": face["summary"]["by_step"]},
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
        passed = sum(1 for ok, _n, _d in legs if ok)
        for ok, name, detail in legs:
            print("%s %s%s" % ("PASS" if ok else "FAIL", name,
                               "" if ok else "  <- %r" % (detail,)))
        print("%d/%d" % (passed, len(legs)))
        return 0 if passed == len(legs) else 1
    print("usage: e323_reach_under_wider_needle.py [run|build|verify|selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main())