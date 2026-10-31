"""E333 -- which E3xx conclusions survive the corpus the helper actually can read.

E332 measured the defect: ``e326.code_lines`` flips into doc mode on any line that *starts* with a
triple quote and carries an odd count of them, so real code leaves the corpus and docstring prose
enters it.  It re-priced exactly one consumer (E331).  Four other studies read the same helper --
E326 (template parameters), E328 (quoted-number staleness), E329 (two-vintage binding) and E330
(unpinned choice) -- and every count they published is a floor of the same shape.  This study runs
each of them twice over one file list, once with the shipped helper and once with the tokenizer,
diffs every numeric leaf of their summary blocks, and then ablates a single source at a time to
name the source and the line span that produced each difference.

    python scripts/e333_surviving_e3xx_conclusions.py run|verify|selftest
"""
import io
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import e326_template_parameter_consumers as e326  # noqa: E402  (path set above)
import e328_quoted_number_staleness as e328  # noqa: E402
import e329_two_vintage_binding as e329  # noqa: E402
import e330_unpinned_choice as e330  # noqa: E402
import e332_invisible_tail_recovery as e332  # noqa: E402

ROOT = e326.ROOT
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
TODAY = "2026-11-01"
FACE = "SURVIVINGCONCLUSIONS-%s.json" % TODAY
LATEST = "survivingconclusions_latest.json"
STUDY = "E333_surviving_e3xx_conclusions"

SOURCE_FACE = os.path.join(OUTDIR, e332.FACE)
MAX_MOVED_PUBLISHED = 60     # per consumer
MAX_ROWS = 40

V_FLIP = "at_least_one_published_verdict_flips_when_the_corpus_is_read"
V_FLOOR = "every_published_count_moves_but_no_verdict_flips"
V_SURVIVE = "no_published_number_moves_when_the_corpus_is_read"
VERDICTS = (V_FLIP, V_FLOOR, V_SURVIVE)

SHIPPED = e326.code_lines          # the helper every consumer reads, captured once
_TOKENIZED = {}                    # source text -> recovered code lines (content keyed)


def say(message):
    """Progress on stderr: the build is minutes long and a silent pipe looks like a hang."""
    sys.stderr.write(message + "\n")
    sys.stderr.flush()


# ---------------------------------------------------------------------------------- primitives

def true_lines(src):
    """The tokenizer reading, memoised: the consumers call the helper many times per source."""
    key = src or ""
    hit = _TOKENIZED.get(key)
    if hit is None:
        hit = e332.true_lines(src)
        _TOKENIZED[key] = hit
    return hit


def recovery_for(rel, src_to_rel):
    """A helper that recovers ONE source and leaves every other file on the shipped reading.

    ``SHIPPED`` is captured at import: inside a priced build ``e326.code_lines`` is this closure,
    so calling the module attribute here would recurse.
    """
    def recover(src):
        if src_to_rel.get(src or "") == rel:
            return true_lines(src)
        return SHIPPED(src)
    return recover


def numeric_leaves(node, prefix="", out=None):
    """Every number in a summary block, keyed by its dotted path."""
    out = {} if out is None else out
    if isinstance(node, dict):
        for key in sorted(node):
            numeric_leaves(node[key], "%s.%s" % (prefix, key) if prefix else str(key), out)
    elif isinstance(node, bool) or node is None:
        return out
    elif isinstance(node, (int, float)):
        out[prefix] = node
    return out


def compare(shipped, recovered):
    """Numeric leaves that differ, with the delta; booleans and strings only as presence."""
    a = numeric_leaves(shipped or {})
    b = numeric_leaves(recovered or {})
    moved = []
    for key in sorted(set(a) | set(b)):
        va, vb = a.get(key), b.get(key)
        if va == vb:
            continue
        delta = None
        if isinstance(va, (int, float)) and isinstance(vb, (int, float)):
            delta = vb - va
        moved.append({"key": key, "shipped": va, "recovered": vb, "delta": delta})
    return moved, len(set(a) | set(b))


def priced(build_fn, recover=None):
    """Run one consumer build in a scratch directory under a chosen corpus helper."""
    outdir = tempfile.mkdtemp(prefix="e333_build_")
    try:
        if recover is not None:
            e326.code_lines = recover
        return build_fn(outdir)
    finally:
        e326.code_lines = SHIPPED
        if e326.code_lines is not SHIPPED:
            raise AssertionError("the corpus helper was not restored")


def attribute(build_fn, shipped_summary, moved_keys, candidates, src_to_rel, budget):
    """Single-source ablation: which source, alone, reproduces which moved number."""
    tried = []
    per_key = {k: [] for k in moved_keys}
    for rel in candidates[:budget]:
        tried.append(rel)
        doc = priced(build_fn, recovery_for(rel, src_to_rel))
        rows, _n = compare(shipped_summary, doc.get("summary") or {})
        by_key = {r["key"]: r for r in rows}
        for key in moved_keys:
            hit = by_key.get(key)
            if hit:
                per_key[key].append({"source": rel, "shipped": hit["shipped"],
                                     "recovered_with_only_this_source": hit["recovered"],
                                     "delta": hit["delta"]})
    return per_key, tried


def consumer_signal(kind, path, src, rel, src_to_rel):
    """How much the helper changes what THIS consumer can read in one source.

    The generic event count is a proxy; a consumer that reads through its own index (E328) or its
    own handle collector (E329) can be measured directly on a single file, which is what decides
    where the ablation budget should go.
    """
    if kind == "e326":
        pop = e326.population(e326.read_json(e326.INPUT))

        def read(helper):
            e326.code_lines = helper
            try:
                return sum(len(e326.face_record(rec, [(path, src)])["consumers"]) for rec in pop)
            finally:
                e326.code_lines = SHIPPED
        shipped, recovered = read(SHIPPED), read(recovery_for(rel, src_to_rel))
        return {"consumer_side": "consumers_named_in_one_source",
                "with_shipped_helper": shipped, "with_recovered_corpus": recovered,
                "delta": recovered - shipped}
    if kind == "e328":
        def read(helper):
            e326.code_lines = helper
            try:
                index = e328.reader_index([(path, src)])
            finally:
                e326.code_lines = SHIPPED
            return sum(len([r for r in rows if not r["writer"]]) for rows in index.values())
        shipped, recovered = read(SHIPPED), read(recovery_for(rel, src_to_rel))
        return {"consumer_side": "non_writer_reader_entries",
                "with_shipped_helper": shipped, "with_recovered_corpus": recovered,
                "delta": recovered - shipped}
    if kind == "e329":
        def read(helper):
            e326.code_lines = helper
            try:
                rows = e329.collect([(path, src)])
            finally:
                e326.code_lines = SHIPPED
            return sum(len(row["handles"]) for row in rows.values())
        shipped, recovered = read(SHIPPED), read(recovery_for(rel, src_to_rel))
        return {"consumer_side": "handle_candidates",
                "with_shipped_helper": shipped, "with_recovered_corpus": recovered,
                "delta": recovered - shipped}
    return None


def events_of(lines):
    """How many line events a scanner would read from a code-line list."""
    n = 0
    for _lineno, text in lines:
        kinds = e332.classify(text)
        if e332.K_FACE in kinds or e332.K_LOAD in kinds:
            n += 1
    return n


def candidate_rows(rows, texts):
    """Blind sources ordered by how much the helper changed what a scanner can read.

    Ranking on the recovered volume alone is not enough: the shipped helper also *adds* prose as
    code, so a source can score high on recovered lines and still lose events.  The score is the
    absolute change in face-handle/load-site lines between the two readings.
    """
    out = []
    for row in rows:
        src = texts.get(row["source"])
        if src is None:
            continue
        shown = events_of(SHIPPED(src))
        recovered = events_of(true_lines(src))
        out.append({"source": row["source"], "events_with_shipped_helper": shown,
                    "events_with_recovered_corpus": recovered,
                    "event_delta": recovered - shown,
                    "recovered_code_lines": row.get("recovered_code_lines"),
                    "spans": row.get("spans") or [],
                    "span_count": row.get("span_count")})
    out.sort(key=lambda r: (-abs(r["event_delta"]), -max(r["events_with_recovered_corpus"],
                                                        r["events_with_shipped_helper"]),
                            -(r["recovered_code_lines"] or 0)))
    return out


def corpus_facts(doc):
    s = doc.get("summary") or {}
    return {
        "study": doc.get("study"),
        "evidence_cutoff": doc.get("evidence_cutoff"),
        "sources_scanned": s.get("sources_scanned"),
        "sources_the_helper_blinds": s.get("sources_the_helper_blinds"),
        "recovered_code_lines": s.get("recovered_code_lines"),
        "recovered_by_kind": s.get("recovered_by_kind"),
        "source_face": os.path.relpath(SOURCE_FACE, ROOT).replace(os.sep, "/"),
    }


# ------------------------------------------------------------------------------------- consumer

def reproduction(face_rel, shipped_doc):
    """Control: the shipped half must reproduce the face as published, or the delta is not the helper."""
    path = os.path.join(ROOT, face_rel)
    try:
        with io.open(path, encoding="utf-8") as fh:
            published = json.load(fh)
    except Exception as exc:  # noqa: BLE001 - reported, never swallowed
        return {"published_face": face_rel, "readable": False, "why": repr(exc)}
    rows, compared = compare(published.get("summary"), shipped_doc.get("summary"))
    return {"published_face": face_rel, "readable": True,
            "numbers_compared": compared, "numbers_differing": len(rows),
            "differences": rows[:12],
            "reproduces_published": not rows,
            "verdict_same": published.get("verdict") == shipped_doc.get("verdict")}


def consumer_rows(files, src_to_rel, candidates):
    """One row per consumer study: shipped numbers, recovered numbers, delta, ablation."""
    registry = [
        {"name": "E326_template_parameters", "module": "e326_template_parameter_consumers.py",
         "face": "results/state_tilt/%s" % e326.FACE, "budget": 3, "signal": "e326",
         "build": lambda outdir: e326.build(outdir=outdir)},
        {"name": "E328_quoted_number_staleness", "module": "e328_quoted_number_staleness.py",
         "face": "results/state_tilt/%s" % e328.FACE, "budget": 8, "signal": "e328",
         "build": lambda outdir: e328.build(outdir=outdir, files=files)},
        {"name": "E329_two_vintage_binding", "module": "e329_two_vintage_binding.py",
         "face": "results/state_tilt/%s" % e329.FACE, "budget": 6, "signal": "e329",
         "build": lambda outdir: e329.build(outdir=outdir, files=files)},
        {"name": "E330_unpinned_choice", "module": "e330_unpinned_choice.py",
         "face": "results/state_tilt/%s" % e330.FACE, "budget": 4, "signal": None,
         "build": lambda outdir: e330.build(outdir=outdir, files=files)},
    ]
    names = [c["source"] for c in candidates]
    spans = {c["source"]: c["spans"] for c in candidates}
    by_rel = {}
    for path, src in files:
        by_rel.setdefault(e326.relp(path), (path, src))
    out = []
    for entry in registry:
        say("  %s: shipped build" % entry["name"])
        base = priced(entry["build"])
        say("  %s: recovered build" % entry["name"])
        fixed = priced(entry["build"], true_lines)
        moved, compared = compare(base.get("summary"), fixed.get("summary"))
        reproduced = reproduction(entry["face"], base)
        keys = [m["key"] for m in moved]
        per_key, tried, signals = ({}, [], [])
        if keys:
            order = names
            if entry.get("signal"):
                scored = []
                for rel in names:
                    path, src = by_rel[rel]
                    sig = consumer_signal(entry["signal"], path, src, rel, src_to_rel)
                    scored.append((abs(sig["delta"]), rel, sig))
                scored.sort(key=lambda t: -t[0])
                order = [rel for _a, rel, _s in scored]
                signals = [{"source": rel, "signal": sig} for _a, rel, sig in scored[:6]]
            say("  %s: %d numbers moved, ablating %d sources"
                % (entry["name"], len(keys), min(entry["budget"], len(order))))
            per_key, tried = attribute(entry["build"], base.get("summary") or {}, keys,
                                       order, src_to_rel, entry["budget"])
        for row in moved:
            matched = per_key.get(row["key"]) or []
            row["attributed_sources"] = [dict(m, spans=spans.get(m["source"]) or [])
                                         for m in matched]
            row["attributed"] = bool(matched)
            row["explained_by_one_source"] = bool(
                matched and abs((matched[0]["delta"] or 0) - (row["delta"] or 0)) < 1e-9)
            row["largest_single_source_share_pct"] = (
                round(100.0 * max(abs(m["delta"] or 0) for m in matched) / abs(row["delta"]), 1)
                if matched and row["delta"] else None)
        verdict_moved = base.get("verdict") != fixed.get("verdict")
        out.append({
            "name": entry["name"],
            "module": "scripts/%s" % entry["module"],
            "face": entry["face"],
            "verdict_with_shipped_helper": base.get("verdict"),
            "verdict_with_recovered_corpus": fixed.get("verdict"),
            "verdict_moved": verdict_moved,
            "numbers_compared": compared,
            "numbers_moved": len(moved),
            "numbers_unchanged": compared - len(moved),
            "moved": moved[:MAX_MOVED_PUBLISHED],
            "moved_truncated": max(0, len(moved) - MAX_MOVED_PUBLISHED),
            "numbers_attributed_to_one_source": sum(1 for r in moved if r["attributed"]),
            "numbers_explained_exactly_by_one_source": sum(
                1 for r in moved if r["explained_by_one_source"]),
            "ablation_sources_tried": tried,
            "ablation_signals": signals,
            "shipped_helper_reproduces_published_face": reproduced,
            "conclusion": ("the verdict changes" if verdict_moved else
                           ("the verdict holds, the counts do not" if moved else
                            "the reading is unchanged")),
        })
    return out


# ---------------------------------------------------------------------------------------- build

def build(root=None, outdir=None, files=None, consumers=None, facts=None, facts_rows=None):
    root = root or ROOT
    files = files if files is not None else e326.corpus()
    candidates = []
    if facts is None or facts_rows is None:
        with io.open(SOURCE_FACE, encoding="utf-8") as fh:
            src_doc = json.load(fh)
        facts = facts or corpus_facts(src_doc)
        facts_rows = facts_rows if facts_rows is not None else (src_doc.get("sources") or [])
    if consumers is None:
        src_to_rel = {}
        texts = {}
        for path, src in files:
            rel = e326.relp(path)
            src_to_rel.setdefault(src or "", rel)
            texts[rel] = src
        candidates = candidate_rows(facts_rows, texts)
        consumers = consumer_rows(files, src_to_rel, candidates)

    flips = [c["name"] for c in consumers if c["verdict_moved"]]
    movers = [c["name"] for c in consumers if c["numbers_moved"]]
    compared = sum(c["numbers_compared"] for c in consumers)
    moved = sum(c["numbers_moved"] for c in consumers)
    attributed = sum(c["numbers_attributed_to_one_source"] for c in consumers)
    exact = sum(c["numbers_explained_exactly_by_one_source"] for c in consumers)

    if flips:
        verdict = V_FLIP
        reason = ("%d of %d studies publish a different verdict once the tokenizer reads the "
                  "corpus (%s); %d of %d published numbers move"
                  % (len(flips), len(consumers), ", ".join(flips), moved, compared))
    elif moved:
        verdict = V_FLOOR
        reason = ("%d of %d studies keep their verdict while %d of %d published numbers move; "
                  "%d of the moved numbers are reproduced by a single source and %d of those are "
                  "explained exactly by it"
                  % (len(movers), len(consumers), moved, compared, attributed, exact))
    else:
        verdict = V_SURVIVE
        reason = ("none of the %d published numbers the %d studies summarise moves when the corpus "
                  "is read with the tokenizer" % (compared, len(consumers)))

    summary = {
        "consumers_reviewed": len(consumers),
        "consumers_whose_counts_move": len(movers),
        "consumers_whose_verdict_flips": len(flips),
        "published_numbers_compared": compared,
        "published_numbers_moved": moved,
        "published_numbers_unchanged": compared - moved,
        "numbers_attributed_to_a_single_source": attributed,
        "numbers_explained_exactly_by_a_single_source": exact,
        "numbers_with_no_single_source_explanation": moved - attributed,
        "consumers_whose_shipped_half_reproduces_the_published_face": sum(
            1 for c in consumers
            if (c.get("shipped_helper_reproduces_published_face") or {}).get(
                "reproduces_published")),
        "corpus_sources_scanned": facts.get("sources_scanned"),
        "corpus_sources_the_helper_blinds": facts.get("sources_the_helper_blinds"),
        "corpus_recovered_code_lines": facts.get("recovered_code_lines"),
        "ablation_candidates_ranked": len(candidates),
        "ablation_builds": sum(len(c["ablation_sources_tried"]) for c in consumers),
        "rows_published": len(consumers),
    }
    doc = {
        "study": STUDY,
        "evidence_cutoff": TODAY,
        "verdict": verdict,
        "verdict_reason": reason,
        "summary": summary,
        "source_study": facts,
        "rules": {
            "one_corpus": "every consumer runs over the same file list (e326.corpus()), so a delta "
                          "is the helper and nothing else",
            "priced": "each consumer's own build() is run twice into scratch directories; the "
                      "patched helper is restored in a finally block and the restore is asserted",
            "numbers": "every numeric leaf of the summary block is compared, dotted paths "
                       "included; booleans and strings are not counted as published numbers",
            "attribution": "a moved number is attributed when re-running the same build with ONE "
                           "source recovered reproduces it; 'explained exactly' additionally "
                           "requires that single source to produce the whole delta",
            "bounded": "each consumer ablates a fixed number of sources (3/8/6/4 for E326/E328/"
                       "E329/E330), ranked by the absolute change in face-handle and load-site "
                       "lines between the two readings; an unattributed number is published as "
                       "unattributed, never guessed",
            "no_silent_repair": "no consumer's face is rewritten by this study; the delta is "
                                "published beside the shipped numbers",
        },
        "limits": {
            "verdict_text": "a verdict token that does not move can still overstate: the counts "
                            "behind it are published here so a reader can check that for itself",
            "single_source": "ablation names one source at a time; a moved number that needs two "
                             "sources together reads as unattributed",
            "line_span": "the span published for an attributed number is the source's E332 span "
                         "list, not a per-delta line slice",
            "corpus_drift": "the delta is the helper alone: both halves run over today's file "
                            "list and today's faces.  The published-vs-shipped difference is a "
                            "SECOND axis (the corpus has grown since each face was written) and is "
                            "published as a control, not folded into this delta",
        },
        "consumers": consumers,
    }
    if candidates:
        doc["attribution_candidates"] = candidates[:MAX_ROWS]
        doc["attribution_candidates_truncated"] = max(0, len(candidates) - MAX_ROWS)
    target = outdir or OUTDIR
    os.makedirs(target, exist_ok=True)
    body = json.dumps(doc, ensure_ascii=False, indent=1) + "\n"
    for name in (FACE, LATEST):
        with io.open(os.path.join(target, name), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body)
    return doc


# --------------------------------------------------------------------------------------- verify

def verify_face(disk, fresh):
    """The publish check, split out so it can be pinned hermetically."""
    problems = []
    if disk.get("verdict") != fresh.get("verdict"):
        problems.append("the verdict does not re-derive")
    if disk.get("verdict") not in VERDICTS:
        problems.append("verdict %r is outside the frozen set" % (disk.get("verdict"),))
    for key, value in (fresh.get("summary") or {}).items():
        if (disk.get("summary") or {}).get(key) != value:
            problems.append("summary.%s does not re-derive" % key)
    disk_c = {c.get("name"): c for c in disk.get("consumers") or []}
    fresh_c = {c.get("name"): c for c in fresh.get("consumers") or []}
    if sorted(disk_c) != sorted(fresh_c):
        problems.append("the consumer list does not re-derive")
    for name in sorted(set(disk_c) & set(fresh_c)):
        a, b = disk_c[name], fresh_c[name]
        for key in ("verdict_with_shipped_helper", "verdict_with_recovered_corpus",
                    "verdict_moved", "numbers_compared", "numbers_moved"):
            if a.get(key) != b.get(key):
                problems.append("%s.%s does not re-derive" % (name, key))
        if [(r["key"], r["shipped"], r["recovered"]) for r in a.get("moved") or []] != \
                [(r["key"], r["shipped"], r["recovered"]) for r in b.get("moved") or []]:
            problems.append("%s moved list does not re-derive" % name)
    if (disk.get("summary") or {}).get("published_numbers_compared", 0) <= 0:
        problems.append("nothing was compared, which is a broken measurement not a clean result")
    return problems


def verify(root=None, files=None):
    root = root or ROOT
    fresh = build(root=root, outdir=tempfile.mkdtemp(prefix="e333_verify_"), files=files)
    path = os.path.join(root, "results", "state_tilt", FACE)
    try:
        with io.open(path, encoding="utf-8") as fh:
            disk = json.load(fh)
    except Exception as exc:  # noqa: BLE001 - reported, never swallowed
        return ["the face does not read: %r" % (exc,)]
    return verify_face(disk, fresh)


# ------------------------------------------------------------------------------------- selftest

A = (
    '"""doc."""\n'
    'V = ("""\n'
    'one\n'
    '""".split())\n'
    '\n'
    'def load_a():\n'
    '    return json.load(open("results/x/FOO-2026-11-01.json"))\n'
)
B = (
    'def load_b():\n'
    '    return json.load(open("results/x/BAR-2026-11-01.json"))\n'
)


def _fake_build(depends, outdir):
    """A consumer whose published number counts the defs one source shows it."""
    shown = len([1 for _n, t in e326.code_lines(depends)])
    doc = {"verdict": "v%d" % shown, "summary": {"defs": shown, "class_": {"nested": shown}}}
    os.makedirs(outdir, exist_ok=True)
    return doc


def cmd_selftest():
    checks = []

    def check(name, ok, detail=""):
        checks.append((name, bool(ok), detail))

    # L1/L2: the memoised tokenizer reading is the real one, and it is cached
    check("L1 the memoised reading equals the tokenizer reading",
          true_lines(A) == e332.true_lines(A), "mismatch")
    check("L2 a second call is served from the cache",
          true_lines(A) is true_lines(A), "not cached")

    # L3/L4: a partial recovery touches only its source
    src_map = {A: "a.py", B: "b.py"}
    rec_a = recovery_for("a.py", src_map)
    check("L3 the targeted source switches to the tokenizer reading",
          len(rec_a(A)) > len(SHIPPED(A)), "%d vs %d" % (len(rec_a(A)), len(SHIPPED(A))))
    check("L4 every other source keeps the shipped reading", rec_a(B) == SHIPPED(B), "moved")

    # L5: priced() restores the helper even when the build raises
    def boom(outdir):
        raise RuntimeError("build failed")
    try:
        priced(boom, true_lines)
    except RuntimeError:
        pass
    check("L5 the helper is restored after a raising build", e326.code_lines is SHIPPED,
          repr(e326.code_lines))

    # L6-L8: leaf walking and diffing
    moved, compared = compare({"a": 1, "b": {"c": 2}, "flag": True, "text": "x"},
                              {"a": 3, "b": {"c": 4}, "flag": False, "text": "y"})
    check("L6 a nested number is compared by its dotted path",
          [m["key"] for m in moved] == ["a", "b.c"], json.dumps(moved))
    check("L7 booleans and strings are not published numbers", compared == 2, str(compared))
    check("L8 the delta carries its sign", [m["delta"] for m in moved] == [2, 2],
          json.dumps([m["delta"] for m in moved]))

    # L9/L10: attribution names one source and stays silent for a source with no effect
    build_a = lambda d: _fake_build(A, d)  # noqa: E731
    base = priced(build_a)
    fixed = priced(build_a, true_lines)
    keys = [m["key"] for m in compare(base["summary"], fixed["summary"])[0]]
    per_key, tried = attribute(build_a, base["summary"], keys, ["a.py", "b.py"], src_map, 2)
    check("L9 the single-source ablation reproduces the moved number",
          all(per_key[k] and per_key[k][0]["source"] == "a.py" for k in keys),
          json.dumps(per_key))
    per_key_b, _t = attribute(build_a, base["summary"], keys, ["b.py"], src_map, 1)
    check("L10 a source that feeds nothing attributes nothing",
          all(per_key_b[k] == [] for k in keys), json.dumps(per_key_b))

    # L11: the ablation ranking prefers a source whose readable events actually changed
    loud = ('"""doc."""\n'
            'T = ("""\n'
            'x\n'
            '""".split())\n'
            'def load_loud():\n'
            '    return json.load(open("results/x/LOUD-2026-11-01.json"))\n')
    quiet = ('def load_quiet():\n'
             '    return json.load(open("results/x/QUIET-2026-11-01.json"))\n')
    cand = candidate_rows([{"source": "quiet.py", "recovered_code_lines": 90},
                           {"source": "loud.py", "recovered_code_lines": 4}],
                          {"loud.py": loud, "quiet.py": quiet})
    check("L11 the ablation ranking prefers a changed event count over recovered volume",
          cand[0]["source"] == "loud.py" and cand[0]["event_delta"] > 0 and
          cand[1]["event_delta"] == 0, json.dumps(cand))

    # L12-L14: the publish check
    fake_consumers = [{"name": "fake", "verdict_with_shipped_helper": "a",
                       "verdict_with_recovered_corpus": "b", "verdict_moved": True,
                       "numbers_compared": 2, "numbers_moved": 1,
                       "numbers_attributed_to_one_source": 1,
                       "numbers_explained_exactly_by_one_source": 1,
                       "ablation_sources_tried": ["a.py"],
                       "conclusion": "the verdict changes",
                       "moved": [{"key": "k", "shipped": 1, "recovered": 2, "delta": 1}]}]
    facts = {"sources_scanned": 2, "sources_the_helper_blinds": 1, "recovered_code_lines": 3}
    out = tempfile.mkdtemp(prefix="e333_fx_")
    doc = build(root=out, outdir=os.path.join(out, "results", "state_tilt"),
                files=[], consumers=fake_consumers, facts=facts, facts_rows=[])
    check("L12 the face writes both the dated face and the latest pointer",
          os.path.isfile(os.path.join(out, "results", "state_tilt", FACE)) and
          os.path.isfile(os.path.join(out, "results", "state_tilt", LATEST)), "missing")
    check("L13 a flipped verdict outranks a mere count move", doc["verdict"] == V_FLIP,
          doc["verdict"])
    check("L14 verify_face accepts what build just published", verify_face(doc, doc) == [],
          str(verify_face(doc, doc))[:200])

    doctored = json.loads(json.dumps(doc))
    doctored["consumers"][0]["numbers_moved"] = 0
    check("L15 verify_face catches a doctored moved count",
          any("numbers_moved" in p for p in verify_face(doctored, doc)),
          str(verify_face(doctored, doc))[:200])

    doctored2 = json.loads(json.dumps(doc))
    doctored2["summary"]["published_numbers_moved"] = 0
    check("L16 verify_face catches a doctored summary", verify_face(doctored2, doc) != [],
          str(verify_face(doctored2, doc))[:200])

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
    print("consumers %(consumers_reviewed)s / counts move %(consumers_whose_counts_move)s / "
          "verdict flips %(consumers_whose_verdict_flips)s" % s)
    print("numbers: %(published_numbers_moved)s of %(published_numbers_compared)s moved, "
          "%(numbers_explained_exactly_by_a_single_source)s explained exactly by one source, "
          "%(numbers_with_no_single_source_explanation)s unattributed" % s)
    for c in doc["consumers"]:
        print("   - %-34s moved %2d/%-3d verdict_moved=%s  %s"
              % (c["name"], c["numbers_moved"], c["numbers_compared"], c["verdict_moved"],
                 c["conclusion"]))
        for m in c["moved"][:6]:
            src = m["attributed_sources"][0]["source"] if m["attributed_sources"] else "-"
            print("       %-44s %s -> %s (%+g) via %s"
                  % (m["key"], m["shipped"], m["recovered"],
                     m["delta"] if m["delta"] is not None else 0, src))
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