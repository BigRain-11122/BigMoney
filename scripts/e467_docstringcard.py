"""E467 -- is the card in a producer's docstring ever read, or is the identity human-only?

E460 read the 21 producers of the 12 identity-gap faces and found that every one of them restates
its own card twice: once in the module name (``eNNN_``) and again in the module docstring -- while
11 of the 12 payloads carry the identity only as a producer *stem*, never as a card.  That makes
the docstring the second of exactly three places an identity can live, and nobody had asked
whether any program in the tree ever recovers a card from it.

This study publishes three channels per producer and then one census over readers:

  (a) the module name -- mechanical, always available, needs no cooperation from the producer;
  (b) the docstring -- reachable only by a source that parses docstrings;
  (c) a machine channel -- the producer writing its own card as a literal outside the docstring,
      i.e. into a payload field, a module constant or a registry.

The reader census is deliberately built so that co-occurrence cannot pass for a join.  A source
that reads a docstring *and* contains a card regex somewhere is published as two separate facts
("reads a docstring", "looks for a card") and NOT as a reader that recovers a card; the join tier
requires a visible dataflow edge -- a regex search/findall/finditer/match applied to the very
expression (or the very variable) that a docstring read produced.

Patterns are validated by a positive probe and a negative control before they count: an empty
string, or an alternation with an empty branch, matches everything and would otherwise publish a
thousand "card-aware" sources that look for nothing in particular.

Usage:
    python scripts/e467_docstringcard.py run|check|verify|selftest
"""
from __future__ import annotations

import ast
import io
import json
import os
import re
import sys
import warnings
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "scripts")
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE_NAME = "docstringcard_latest.json"
DATED_PREFIX = "DOCSTRINGCARD"
CARD_ID = "E467-IS-THE-CARD-IN-A-PRODUCERS-DOCSTRING-EVER-READ-OR-IS-THE-IDENTITY-HUMAN-ONLY"

PRODUCER_RE = re.compile(r"^(e[0-9]{3,})_[a-z0-9_]*\.py$")
CARD_RE = re.compile(r"\bE[0-9]{3,}\b")
CARD_PROBE = "E460"
STEM_PROBE = "e460_facegap"
# A pattern only counts when it hits the probe and misses both a plain sentence and the other
# probe: `""` and `"a|"` match everything, which is how this census first reported 1,203 sources
# "looking for a card shape".
CARD_NEGATIVES = ("nothing of that shape here", STEM_PROBE, "271")
STEM_NEGATIVES = ("nothing of that shape here", CARD_PROBE)

IDENTITY_FIELDS = frozenset({
    "card", "card_id", "cards", "study", "study_id", "studies", "prereg", "prereg_path",
    "prereg_note", "pid", "source_card", "source_cards", "pin", "pinned_note",
})

C_LITERAL = "its_own_card_is_written_as_a_literal_outside_the_docstring"
C_FIELD = "it_writes_an_identity_named_field_but_never_its_own_card_as_a_literal"
C_DOCSTRING = "its_own_card_appears_only_in_its_docstring_and_its_module_name"
C_NOT_RESTATED = "its_docstring_and_its_constants_do_not_restate_its_own_card"
CLASSES = (C_LITERAL, C_FIELD, C_DOCSTRING, C_NOT_RESTATED)

T_JOIN = "a_card_shaped_pattern_is_applied_to_the_text_a_docstring_read_produced"
T_DOC_AND_CARD = "reads_a_docstring_and_looks_for_a_card_shape_but_no_static_join_is_visible"
T_CARD_NO_DOC = "looks_for_a_card_shape_without_reading_a_docstring"
T_DOC_ONLY = "reads_a_docstring_without_looking_for_a_card"
T_NONE = "neither_reads_a_docstring_nor_looks_for_a_card"
TIERS = (T_JOIN, T_DOC_AND_CARD, T_CARD_NO_DOC, T_DOC_ONLY, T_NONE)

V_EMPTY = "no_producer_script_is_in_the_corpus"
V_NO_DOC_READER = ("no_source_in_the_corpus_reads_a_docstring_so_the_card_a_producer_restates"
                   "_has_no_machine_reader")
V_DOC_READER_NO_CARD = "sources_read_docstrings_but_none_of_them_looks_for_a_card_shape_in_one"
V_DOC_AND_CARD = ("sources_read_a_docstring_and_look_for_a_card_shape_but_no_static_dataflow"
                  "_edge_joins_them")
V_JOIN = "at_least_one_source_applies_a_card_shaped_pattern_to_the_text_a_docstring_read_produced"
VERDICT_VOCAB = (V_EMPTY, V_NO_DOC_READER, V_DOC_READER_NO_CARD, V_DOC_AND_CARD, V_JOIN)

MAX_SOURCE_BYTES = 4 * 1024 * 1024
MAX_PATTERN_LEN = 200
MAX_CARDS_CITED = 6
MAX_READ_TARGETS = 4
REGEX_METHODS = ("findall", "search", "finditer", "match", "fullmatch", "sub")


def _rel(path: str) -> str:
    return os.path.relpath(path, ROOT).replace(os.sep, "/")


def _load(path: str) -> dict:
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def corpus() -> list:
    """The shared corpus, minus this study's own files (self-inclusion law, E180/E207)."""
    import e432_fixture_write as e432
    return [p for p in e432.corpus()
            if not os.path.basename(p).startswith(("e467", "_e467", "run_e467"))]


def _read(rel: str):
    path = os.path.join(ROOT, rel)
    if os.path.getsize(path) > MAX_SOURCE_BYTES:
        return None, "larger than the read cap"
    with io.open(path, encoding="utf-8-sig", errors="replace") as fh:
        return fh.read(), None


def _parse(source: str):
    try:
        return ast.parse(source), None
    except SyntaxError as exc:
        return None, "%s (line %s)" % (exc.msg, exc.lineno)


def _compile(text: str):
    if not text or len(text) > MAX_PATTERN_LEN:
        return None
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", FutureWarning)
        try:
            return re.compile(text)
        except re.error:
            return None


def pattern_is_for(rx, positive: str, negatives) -> bool:
    """A pattern answers a probe only when it hits it and misses the controls."""
    if rx is None:
        return False
    try:
        if not rx.search(positive):
            return False
        return not any(rx.search(neg) for neg in negatives)
    except (re.error, RecursionError):
        return False


def docstring_node(tree):
    """The module docstring's Constant node, if the module has one."""
    if tree.body and isinstance(tree.body[0], ast.Expr):
        value = tree.body[0].value
        if isinstance(value, ast.Constant) and isinstance(value.value, str):
            return value
    return None


def string_constants(tree) -> list:
    doc = docstring_node(tree)
    doc_id = id(doc) if doc is not None else None
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) != doc_id:
            out.append(node.value)
    return out


def _is_docstring_read(node) -> bool:
    if not isinstance(node, ast.Call):
        return False
    func = node.func
    if isinstance(func, ast.Attribute) and func.attr in ("get_docstring", "getdoc"):
        return True
    return isinstance(func, ast.Name) and func.id == "getdoc"


def _unparse(node) -> str:
    try:
        return ast.unparse(node)
    except Exception:  # very old/odd nodes; a missing spelling is published as empty
        return ""


def docstring_reads(tree) -> dict:
    """Sites where a source parses somebody's docstring, and the expressions it parses."""
    calls = attr_reads = 0
    targets = []
    for node in ast.walk(tree):
        if _is_docstring_read(node):
            calls += 1
            targets.append(_unparse(node)[:80])
        elif isinstance(node, ast.Attribute) and node.attr == "__doc__":
            attr_reads += 1
            targets.append(_unparse(node)[:80])
    return {"docstring_call_sites": calls, "dunder_doc_reads": attr_reads,
            "docstring_read_sites": calls + attr_reads,
            "docstring_read_targets": targets[:MAX_READ_TARGETS]}


def docstring_variables(tree) -> list:
    """Names that hold the text a docstring read produced (``doc = ast.get_docstring(tree)``)."""
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and all(isinstance(t, ast.Name) for t in node.targets):
            value = node.value
            if _is_docstring_read(value):
                names.add(node.targets[0].id)
            elif (isinstance(value, ast.BoolOp) and not isinstance(value, ast.Compare)
                  and any(_is_docstring_read(v) for v in value.values)):
                names.add(node.targets[0].id)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            if _is_docstring_read(node.value):
                names.add(node.target.id)
    return sorted(names)


def card_signals(tree) -> dict:
    """Does a source carry a pattern that actually answers the card probe, or spell one?"""
    literals, card_patterns, stem_patterns = [], [], []
    for value in string_constants(tree):
        text = value.strip()
        if text and CARD_RE.fullmatch(text):
            literals.append(text)
            continue
        rx = _compile(text)
        if pattern_is_for(rx, CARD_PROBE, CARD_NEGATIVES):
            card_patterns.append(text)
        if pattern_is_for(rx, STEM_PROBE, STEM_NEGATIVES):
            stem_patterns.append(text)
    return {"card_literals": sorted(set(literals))[:MAX_CARDS_CITED],
            "card_patterns": sorted(set(card_patterns))[:MAX_CARDS_CITED],
            "stem_patterns": sorted(set(stem_patterns))[:MAX_CARDS_CITED]}


def compiled_patterns(tree) -> dict:
    """Module-level ``NAME = re.compile(<literal>)``: the spelling every study in this tree uses."""
    out = {}
    for node in tree.body:
        if not (isinstance(node, ast.Assign) and all(isinstance(t, ast.Name) for t in node.targets)):
            continue
        value = node.value
        if (isinstance(value, ast.Call) and isinstance(value.func, ast.Attribute)
                and value.func.attr == "compile" and value.args
                and isinstance(value.args[0], ast.Constant)
                and isinstance(value.args[0].value, str)):
            out[node.targets[0].id] = value.args[0].value
    return out


def join_pattern_kind(pattern_text: str) -> str:
    """What a regex looks for: a card, a producer stem, or something else."""
    rx = _compile(pattern_text or "")
    if pattern_is_for(rx, CARD_PROBE, CARD_NEGATIVES):
        return "card"
    if pattern_is_for(rx, STEM_PROBE, STEM_NEGATIVES):
        return "stem"
    return "other"


def card_join_sites(tree, doc_names) -> dict:
    """Regex calls applied to the exact text (or variable) a docstring read produced.

    This is the only tier that is a join rather than a co-occurrence: the *subject* of the
    search/findall must be the docstring text, either spelled inline or through the name the
    assignment gave it.  The subject is argument 0 for a compiled pattern (``CARD_RE.findall(doc)``)
    and argument 1 for the module-level spelling (``re.findall(pat, doc)``).

    A join is only published as a CARD join when the pattern it applies answers the card probe;
    a study-id or prereg regex applied to the same text is a join to a different question.
    """
    constants = {c["name"]: c["value"] for c in module_constants(tree)}
    # a receiver is usually `CARD_RE = re.compile(r"\bE[0-9]{3,}\b")`, not a bare string constant
    constants.update(compiled_patterns(tree))
    sites = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not (isinstance(func, ast.Attribute) and func.attr in REGEX_METHODS):
            continue
        if not node.args:
            continue
        if isinstance(func.value, ast.Name) and func.value.id == "re" and len(node.args) >= 2:
            pattern_arg, subject = node.args[0], node.args[1]
        else:
            pattern_arg, subject = None, node.args[0]
        inline = _is_docstring_read(subject)
        named = isinstance(subject, ast.Name) and subject.id in doc_names
        if not (inline or named):
            continue
        if pattern_arg is None:
            receiver = _unparse(func.value)
            pattern_text = constants.get(receiver, "")
        elif isinstance(pattern_arg, ast.Constant) and isinstance(pattern_arg.value, str):
            # unparse() renders a string constant back as a quoted literal, which would be
            # compiled together with its quotes and match nothing
            pattern_text = pattern_arg.value
        elif isinstance(pattern_arg, ast.Name):
            pattern_text = constants.get(pattern_arg.id, "")
        else:
            pattern_text = ""
        kind = join_pattern_kind(pattern_text)
        sites.append({"receiver": _unparse(func.value)[:60], "method": func.attr,
                      "pattern_kind": kind, "pattern": (pattern_text or "")[:60],
                      "argument": _unparse(subject)[:60],
                      "via": "inline" if inline else "variable"})
    card = [s for s in sites if s["pattern_kind"] == "card"]
    return {"regex_join_sites": len(sites), "card_join_sites": len(card),
            "card_join_detail": card[:4],
            "other_join_detail": [s for s in sites if s["pattern_kind"] != "card"][:4]}


def identity_field_reads(tree) -> dict:
    """Reads of an identity-named payload field: ``x["study"]`` or ``x.get("study")``."""
    keys = {}
    for node in ast.walk(tree):
        key = None
        if isinstance(node, ast.Subscript):
            sl = node.slice
            if isinstance(sl, ast.Constant) and isinstance(sl.value, str):
                key = sl.value
        elif (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
              and node.func.attr == "get" and node.args
              and isinstance(node.args[0], ast.Constant)
              and isinstance(node.args[0].value, str)):
            key = node.args[0].value
        if key in IDENTITY_FIELDS:
            keys[key] = keys.get(key, 0) + 1
    return {"identity_read_sites": sum(keys.values()), "identity_keys_read": sorted(keys)}


def identity_keys_written(tree) -> list:
    keys = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            for k in node.keys:
                if isinstance(k, ast.Constant) and isinstance(k.value, str):
                    if k.value in IDENTITY_FIELDS:
                        keys.add(k.value)
    return sorted(keys)


def module_constants(tree) -> list:
    out = []
    for node in tree.body:
        if isinstance(node, ast.Assign) and all(isinstance(t, ast.Name) for t in node.targets):
            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                out.append({"name": node.targets[0].id, "value": node.value.value})
    return out


def own_card_literal_sites(tree, own: str) -> int:
    """How many places the producer writes its own card where a program (not a human) reads it."""
    return sum(1 for value in string_constants(tree) if value.strip() == own)


def _own_card(rel: str):
    m = PRODUCER_RE.match(os.path.basename(rel))
    return m.group(1).upper() if m else None


def producer_class(restated: bool, literal_sites: int, identity_keys) -> str:
    """Where the producer's own card can be recovered from, cheapest channel first."""
    if literal_sites > 0:
        return C_LITERAL
    if identity_keys:
        return C_FIELD
    if restated:
        return C_DOCSTRING
    return C_NOT_RESTATED


def producer_row(rel: str, tree) -> dict:
    own = _own_card(rel)
    doc = ast.get_docstring(tree) or ""
    doc_cards = sorted(set(CARD_RE.findall(doc)))[:MAX_CARDS_CITED]
    const_cards = sorted({c["value"].strip() for c in module_constants(tree)
                          if CARD_RE.fullmatch(c["value"].strip())})[:MAX_CARDS_CITED]
    literal = own_card_literal_sites(tree, own)
    keys = identity_keys_written(tree)
    restated = bool(own and (own in doc_cards or own in const_cards))
    return {
        "source": rel,
        "own_card": own,
        "docstring_head": doc.strip().splitlines()[0][:120] if doc.strip() else "",
        "docstring_cards": doc_cards,
        "docstring_restates_its_own_card": restated,
        "constant_cards": const_cards,
        "own_card_literal_sites_outside_the_docstring": literal,
        "writes_its_own_card_as_a_literal": literal > 0,
        "identity_keys_it_writes": keys,
        "writes_an_identity_named_payload_key": bool(keys),
        "class": producer_class(restated, literal, keys),
    }


def reader_tier(reads: int, has_card: bool, joins: int) -> str:
    if joins > 0:
        return T_JOIN
    if reads and has_card:
        return T_DOC_AND_CARD
    if reads:
        return T_DOC_ONLY
    if has_card:
        return T_CARD_NO_DOC
    return T_NONE


def reader_row(rel: str, tree) -> dict:
    reads = docstring_reads(tree)
    signals = card_signals(tree)
    doc_names = docstring_variables(tree)
    join = card_join_sites(tree, doc_names)
    fields = identity_field_reads(tree)
    has_card = bool(signals["card_patterns"] or signals["card_literals"])
    return {
        "source": rel,
        "docstring_read_sites": reads["docstring_read_sites"],
        "docstring_call_sites": reads["docstring_call_sites"],
        "dunder_doc_reads": reads["dunder_doc_reads"],
        "docstring_read_targets": reads["docstring_read_targets"],
        "docstring_variables": doc_names[:MAX_READ_TARGETS],
        "card_literals": signals["card_literals"],
        "card_pattern_count": len(signals["card_patterns"]),
        "stem_pattern_count": len(signals["stem_patterns"]),
        "card_join_sites": join["card_join_sites"],
        "regex_join_sites": join["regex_join_sites"],
        "card_join_detail": join["card_join_detail"],
        "other_join_detail": join["other_join_detail"],
        "identity_read_sites": fields["identity_read_sites"],
        "identity_keys_read": fields["identity_keys_read"],
        "tier": reader_tier(reads["docstring_read_sites"], has_card, join["card_join_sites"]),
    }


def is_candidate_reader(row: dict) -> bool:
    """Only sources with a signal are published row by row; the rest are counted, not listed."""
    return bool(row["docstring_read_sites"] or row["card_literals"]
                or row["card_pattern_count"] or row["identity_read_sites"]
                or row["regex_join_sites"])


# ----------------------------------------------------------------------------- build


def build(write: bool = True) -> dict:
    sources = [s for s in corpus() if s.endswith(".py")]
    producers, readers, failures, bom = [], [], [], 0
    for rel in sources:
        try:
            source, err = _read(rel)
        except OSError as exc:
            failures.append({"source": rel, "reason": str(exc)[:120]})
            continue
        if source is None:
            failures.append({"source": rel, "reason": err})
            continue
        if source.startswith("\ufeff"):
            bom += 1
        tree, err = _parse(source)
        if tree is None:
            failures.append({"source": rel, "reason": err})
            continue
        row = reader_row(rel, tree)
        if is_candidate_reader(row):
            readers.append(row)
        if rel.startswith("scripts/") and _own_card(rel):
            producers.append(producer_row(rel, tree))

    by_class = {c: sum(1 for p in producers if p["class"] == c) for c in CLASSES}
    by_tier = {t: sum(1 for r in readers if r["tier"] == t) for t in TIERS}
    silent = len(sources) - len(readers)
    # the silent majority is a reading, not an omission: it is counted in the same tally
    by_tier[T_NONE] = by_tier.get(T_NONE, 0) + silent
    joins = [r for r in readers if r["tier"] == T_JOIN]
    summary = {
        "sources_scanned": len(sources),
        "sources_with_a_signal": len(readers),
        "sources_with_no_signal_at_all": silent,
        "parse_or_read_failures": len(failures),
        "sources_starting_with_a_utf8_bom": bom,
        "producers_read": len(producers),
        "producers_restating_their_own_card": sum(
            1 for p in producers if p["docstring_restates_its_own_card"]),
        "producers_writing_their_own_card_as_a_literal": by_class[C_LITERAL],
        "producers_writing_an_identity_key_but_no_card_literal": by_class[C_FIELD],
        "producers_whose_card_lives_only_in_the_docstring_and_the_module_name": by_class[C_DOCSTRING],
        "producers_that_never_restate_their_own_card": by_class[C_NOT_RESTATED],
        "sources_reading_a_docstring": sum(
            1 for r in readers if r["docstring_read_sites"]),
        "sources_reading_a_docstring_by_call": sum(
            1 for r in readers if r["docstring_call_sites"]),
        "sources_reading_dunder_doc": sum(1 for r in readers if r["dunder_doc_reads"]),
        "sources_looking_for_a_card_shape": sum(
            1 for r in readers if (r["card_pattern_count"] or r["card_literals"])),
        "sources_keying_on_an_identity_payload_field": sum(
            1 for r in readers if r["identity_read_sites"]),
        "sources_applying_a_card_pattern_to_docstring_text": len(joins),
        "sources_applying_any_regex_to_docstring_text": sum(
            1 for r in readers if r["regex_join_sites"]),
        "regex_joins_to_a_non_card_question": sum(
            1 for r in readers if r["regex_join_sites"] and not r["card_join_sites"]),
        "card_join_readers": [r["source"] for r in joins],
        "card_join_detail": [{"source": r["source"], "sites": r["card_join_detail"]}
                             for r in joins],
        "non_card_join_detail": [{"source": r["source"], "sites": r["other_join_detail"]}
                                 for r in readers if r["other_join_detail"]],
        "sources_reading_a_docstring_and_looking_for_a_card_without_a_join": by_tier[T_DOC_AND_CARD],
        "tier_tally": by_tier,
        "class_tally": by_class,
    }
    verdict = verdict_for(len(producers), by_tier)
    payload = {
        "card": CARD_ID,
        "study": "E467",
        "title": "is the card in a producer's docstring ever read, or is the identity human-only",
        "evidence_cutoff": date.today().isoformat(),
        "population_source": ("every scripts/eNNN_*.py producer plus every .py source in the shared "
                              "corpus (e432.corpus, self-excluded); producers are read for the "
                              "three identity channels, all sources for docstring and card reads"),
        "class_vocab": list(CLASSES),
        "tier_vocab": list(TIERS),
        "verdict_vocab": list(VERDICT_VOCAB),
        "identity_field_vocabulary": sorted(IDENTITY_FIELDS),
        "probe": {"card": CARD_PROBE, "stem": STEM_PROBE,
                  "card_negatives": list(CARD_NEGATIVES),
                  "stem_negatives": list(STEM_NEGATIVES),
                  "why": ("a pattern counts only when it hits its probe and misses both controls; "
                          "an empty string or an empty alternation hits everything and is how the "
                          "first cut published 1,203 'card-aware' sources")},
        "corpus": {"source": "e432.corpus (self-excluded)", "files": len(sources),
                   "failures": failures[:20], "failures_total": len(failures),
                   "files_starting_with_a_utf8_bom": bom},
        "producers": producers,
        "producer_class_tally": by_class,
        "reader_tier_tally": by_tier,
        "readers": readers,
        "summary": summary,
        "verdict": verdict,
        "method_limits": [
            "the module name is a channel this study cannot close: any program can recover the "
            "card from the path without the producer's cooperation, so 'human-only' means "
            "'human-only apart from the file name'",
            "a docstring read is counted from three spellings only (ast.get_docstring, "
            "inspect/pydoc getdoc calls, and attribute reads of __doc__); a reader that shells out "
            "to a tool that prints docstrings is invisible here",
            "the join tier requires a regex call whose argument is the docstring text or the "
            "variable it was assigned to; a join through a helper function or a two-step copy is "
            "not seen, so a zero join count is an upper bound on invisibility, not a proof of "
            "absence",
            "sources with no signal are counted but not published row by row, so the tier tally "
            "and the row list do not have the same length (sources_scanned == rows + silent)",
            "the docstring itself is never counted as a card literal site -- the study is about "
            "escaping it",
        ],
    }
    if write:
        os.makedirs(OUTDIR, exist_ok=True)
        for name in ("%s-%s.json" % (DATED_PREFIX, payload["evidence_cutoff"]), FACE_NAME):
            with io.open(os.path.join(OUTDIR, name), "w", encoding="utf-8", newline="\n") as fh:
                json.dump(payload, fh, ensure_ascii=False, indent=1, sort_keys=True)
                fh.write("\n")
        print("wrote results/state_tilt/%s-%s.json" % (DATED_PREFIX, payload["evidence_cutoff"]))
    return payload


def verdict_for(producers: int, by_tier: dict) -> str:
    """The strongest channel a reader actually exercises, recomputed from the tier tally."""
    if producers == 0:
        return V_EMPTY
    if by_tier.get(T_JOIN, 0) > 0:
        return V_JOIN
    if by_tier.get(T_DOC_AND_CARD, 0) > 0:
        return V_DOC_AND_CARD
    if by_tier.get(T_DOC_ONLY, 0) > 0:
        return V_DOC_READER_NO_CARD
    return V_NO_DOC_READER


# ----------------------------------------------------------------------------- check


def tally_problems(published: dict) -> list:
    """Every way the published face fails to re-derive from its own rows."""
    bad = []
    producers = published.get("producers") or []
    readers = published.get("readers") or []
    summary = published.get("summary") or {}
    corpus_block = published.get("corpus") or {}

    by_class = {c: sum(1 for p in producers if p["class"] == c) for c in CLASSES}
    if published.get("producer_class_tally") != by_class:
        bad.append("producer_class_tally does not re-derive from the producer rows")
    by_tier = published.get("reader_tier_tally") or {}
    for tier in TIERS[:-1]:
        if by_tier.get(tier) != sum(1 for r in readers if r["tier"] == tier):
            bad.append("reader_tier_tally[%s] does not re-derive from the reader rows" % tier)
    silent = summary.get("sources_with_no_signal_at_all") or 0
    if by_tier.get(T_NONE) != sum(1 for r in readers if r["tier"] == T_NONE) + silent:
        bad.append("reader_tier_tally[none] does not re-derive from rows + silent sources")
    if summary.get("sources_scanned") != len(readers) + silent:
        bad.append("sources_scanned != published rows + silent sources")
    if summary.get("sources_scanned") != corpus_block.get("files"):
        bad.append("sources_scanned does not match the published corpus size")
    if summary.get("sources_with_a_signal") != len(readers):
        bad.append("sources_with_a_signal does not re-derive")
    if summary.get("producers_read") != len(producers):
        bad.append("producers_read does not re-derive")
    for key, cls in (("producers_writing_their_own_card_as_a_literal", C_LITERAL),
                     ("producers_writing_an_identity_key_but_no_card_literal", C_FIELD),
                     ("producers_whose_card_lives_only_in_the_docstring_and_the_module_name",
                      C_DOCSTRING),
                     ("producers_that_never_restate_their_own_card", C_NOT_RESTATED)):
        if summary.get(key) != by_class[cls]:
            bad.append("%s does not re-derive from the producer rows" % key)
    if summary.get("producers_restating_their_own_card") != sum(
            1 for p in producers if p["docstring_restates_its_own_card"]):
        bad.append("producers_restating_their_own_card does not re-derive")
    if summary.get("sources_reading_a_docstring") != sum(
            1 for r in readers if r["docstring_read_sites"]):
        bad.append("sources_reading_a_docstring does not re-derive")
    if summary.get("sources_reading_dunder_doc") != sum(
            1 for r in readers if r["dunder_doc_reads"]):
        bad.append("sources_reading_dunder_doc does not re-derive")
    if summary.get("sources_keying_on_an_identity_payload_field") != sum(
            1 for r in readers if r["identity_read_sites"]):
        bad.append("sources_keying_on_an_identity_payload_field does not re-derive")
    if summary.get("sources_looking_for_a_card_shape") != sum(
            1 for r in readers if (r["card_pattern_count"] or r["card_literals"])):
        bad.append("sources_looking_for_a_card_shape does not re-derive")
    want_join = sorted(r["source"] for r in readers if r["tier"] == T_JOIN)
    if sorted(summary.get("card_join_readers") or []) != want_join:
        bad.append("card_join_readers does not re-derive from the reader rows")
    if summary.get("sources_applying_a_card_pattern_to_docstring_text") != len(want_join):
        bad.append("sources_applying_a_card_pattern_to_docstring_text does not re-derive")
    if summary.get("sources_applying_any_regex_to_docstring_text") != sum(
            1 for r in readers if r["regex_join_sites"]):
        bad.append("sources_applying_any_regex_to_docstring_text does not re-derive")
    if summary.get("regex_joins_to_a_non_card_question") != sum(
            1 for r in readers if r["regex_join_sites"] and not r["card_join_sites"]):
        bad.append("regex_joins_to_a_non_card_question does not re-derive")
    if any(r["card_join_sites"] > r["regex_join_sites"] for r in readers):
        bad.append("a reader publishes more card joins than joins")
    if summary.get("sources_reading_a_docstring_and_looking_for_a_card_without_a_join") != (
            by_tier.get(T_DOC_AND_CARD, 0)):
        bad.append("the reads-but-no-join count does not re-derive")
    for p in producers:
        want = producer_class(p["docstring_restates_its_own_card"],
                              p["own_card_literal_sites_outside_the_docstring"],
                              p["identity_keys_it_writes"])
        if p["class"] != want:
            bad.append("%s: class does not re-derive from its own channels" % p["source"])
        if p["class"] not in CLASSES:
            bad.append("%s: class outside the vocabulary" % p["source"])
    for r in readers:
        want = reader_tier(r["docstring_read_sites"],
                           bool(r["card_pattern_count"] or r["card_literals"]),
                           r["card_join_sites"])
        if r["tier"] != want:
            bad.append("%s: tier does not re-derive from its own counts" % r["source"])
        if r["tier"] not in TIERS:
            bad.append("%s: tier outside the vocabulary" % r["source"])
        if r["tier"] == T_JOIN and not r["card_join_detail"]:
            bad.append("%s: a join tier with no published join site" % r["source"])
        if r["tier"] != T_JOIN and r["card_join_sites"]:
            bad.append("%s: join sites outside the join tier" % r["source"])
    want_verdict = verdict_for(len(producers), by_tier)
    if published.get("verdict") != want_verdict:
        bad.append("the verdict does not re-derive: %r != %r"
                   % (published.get("verdict"), want_verdict))
    if published.get("verdict") not in VERDICT_VOCAB:
        bad.append("the verdict is outside the frozen vocabulary")
    return bad


def check() -> int:
    published = _load(os.path.join(OUTDIR, FACE_NAME))
    bad = tally_problems(published)
    for b in bad:
        print("BAD %s" % b)
    print("check %s" % ("clean" if not bad else "%d problem(s)" % len(bad)))
    return 0 if not bad else 1


def verify() -> int:
    """Rebuild live and require identical rows: the corpus walk is the expensive part."""
    published = _load(os.path.join(OUTDIR, FACE_NAME))
    fresh = build(write=False)
    bad = tally_problems(published)
    for key in ("producers", "readers", "producer_class_tally", "reader_tier_tally"):
        if (fresh.get(key) or []) != (published.get(key) or []):
            bad.append("a live rebuild reads different %s" % key)
    if fresh.get("verdict") != published.get("verdict"):
        bad.append("a live rebuild reads a different verdict: %r != %r"
                   % (fresh.get("verdict"), published.get("verdict")))
    for b in bad:
        print("BAD %s" % b)
    print("verify %s" % ("clean" if not bad else "%d problem(s)" % len(bad)))
    return 0 if not bad else 1


# ----------------------------------------------------------------------------- selftest


def selftest() -> int:
    ok = total = 0

    def leg(name, cond):
        nonlocal ok, total
        total += 1
        if cond:
            ok += 1
        else:
            print("FAIL %s" % name)

    tree = ast.parse('"""E271 -- a study.\n\nE262 proved something else.\n"""\nX = 1\n')
    leg("the module docstring node is found", docstring_node(tree) is not None)
    leg("a module without a docstring has no docstring node",
        docstring_node(ast.parse("X = 1\n")) is None)
    leg("the docstring is not a string constant site", string_constants(tree) == [])

    reads = docstring_reads(ast.parse("import ast\nast.get_docstring(m)\n"))
    leg("ast.get_docstring is a docstring read", reads["docstring_call_sites"] == 1)
    leg("inspect.getdoc is a docstring read",
        docstring_reads(ast.parse("import inspect\ninspect.getdoc(f)\n"))["docstring_call_sites"] == 1)
    leg("a callee named getdoc is a docstring read",
        docstring_reads(ast.parse("getdoc(f)\n"))["docstring_call_sites"] == 1)
    leg("a dunder doc read is counted apart",
        docstring_reads(ast.parse("d = f.__doc__\n"))["dunder_doc_reads"] == 1)
    leg("the two spellings add into one site count",
        docstring_reads(ast.parse("a = f.__doc__\nimport ast\nast.get_docstring(m)\n"))
        ["docstring_read_sites"] == 2)
    leg("no docstring read is zero, not None",
        docstring_reads(ast.parse("x = 1\n"))["docstring_read_sites"] == 0)
    leg("the parsed expression is published",
        docstring_reads(ast.parse("import ast\nast.get_docstring(tree)\n"))
        ["docstring_read_targets"] == ["ast.get_docstring(tree)"])

    leg("an empty pattern is not a card pattern", _compile("") is None)
    leg("an empty alternation does not count as a card pattern",
        not pattern_is_for(_compile(""), CARD_PROBE, CARD_NEGATIVES))
    leg("a bare alternation that matches everything is rejected",
        not pattern_is_for(_compile("x|"), CARD_PROBE, CARD_NEGATIVES))
    leg("a card regex passes the probe and the controls",
        pattern_is_for(_compile(r"\bE[0-9]{3,}\b"), CARD_PROBE, CARD_NEGATIVES))
    leg("a stem regex fails the card probe",
        not pattern_is_for(_compile(r"e[0-9]{3,}_[a-z0-9_]+"), CARD_PROBE, CARD_NEGATIVES))
    leg("a stem regex passes its own probe",
        pattern_is_for(_compile(r"e[0-9]{3,}_[a-z0-9_]+"), STEM_PROBE, STEM_NEGATIVES))
    leg("prose is neither", _compile("see the card for details") is not None
        and not pattern_is_for(_compile("see the card for details"), CARD_PROBE, CARD_NEGATIVES))

    sig = card_signals(ast.parse('P = r"\\bE[0-9]{3,}\\b"\n'))
    leg("a card regex is published as a card pattern", len(sig["card_patterns"]) == 1)
    leg("a card regex is not a stem pattern", sig["stem_patterns"] == [])
    leg("a literal card is published as a literal",
        card_signals(ast.parse('C = "E271"\n'))["card_literals"] == ["E271"])
    leg("a prose string is not a card pattern",
        card_signals(ast.parse('S = "see the card for details"\n'))["card_patterns"] == [])
    leg("an invalid regex is skipped, not raised",
        card_signals(ast.parse('S = "(unclosed"\n'))["card_patterns"] == [])

    leg("a docstring assigned to a name is a docstring variable",
        docstring_variables(ast.parse("import ast\ndoc = ast.get_docstring(t)\n")) == ["doc"])
    leg("a docstring defaulted with or is still a docstring variable",
        docstring_variables(ast.parse("import ast\ndoc = ast.get_docstring(t) or ''\n")) == ["doc"])
    leg("an unrelated assignment is not a docstring variable",
        docstring_variables(ast.parse("x = 1\n")) == [])
    join = card_join_sites(ast.parse('import ast\ndoc = ast.get_docstring(t)\n'
                                     'import re\nCARD_RE = re.compile(r"\\bE[0-9]{3,}\\b")\n'
                                     'hits = CARD_RE.findall(doc)\n'),
                           ["doc"])
    leg("a regex applied to the docstring variable is a join", join["regex_join_sites"] == 1)
    leg("the join publishes its argument", join["card_join_detail"][0]["argument"] == "doc")
    leg("a join through the variable is labelled as such",
        join["card_join_detail"][0]["via"] == "variable")
    leg("a compiled pattern resolves to the constant it was built from",
        join["card_join_detail"][0]["pattern_kind"] == "card")
    inline = card_join_sites(ast.parse('import ast, re\n'
                                       're.findall(r"\\bE[0-9]{3,}\\b", ast.get_docstring(t))\n'),
                             [])
    leg("a regex applied to an inline docstring read is a join", inline["regex_join_sites"] == 1)
    leg("the inline join is labelled", inline["card_join_detail"][0]["via"] == "inline")
    leg("the module-level spelling takes its subject from the second argument",
        inline["card_join_detail"][0]["argument"] == "ast.get_docstring(t)")
    noncard = card_join_sites(ast.parse('import ast\nSTUDY_RE = 1\n'
                                        'import re\nSTUDY_RE = re.compile(r"[A-Z]+-P[0-9]+")\n'
                                        'doc = ast.get_docstring(t)\nSTUDY_RE.findall(doc)\n'),
                              ["doc"])
    leg("a study-id regex on the docstring text is a join", noncard["regex_join_sites"] == 1)
    leg("a study-id regex is not a card join", noncard["card_join_sites"] == 0)
    leg("a non-card join is published apart", noncard["other_join_detail"][0]["pattern_kind"]
        == "other")
    leg("a regex on something else is not a join",
        card_join_sites(ast.parse('import re\nre.findall(r"x", payload)\n'), [])["regex_join_sites"] == 0)
    leg("a non-regex call on the docstring is not a join",
        card_join_sites(ast.parse('doc.strip()\n'), ["doc"])["regex_join_sites"] == 0)
    leg("a card pattern probe is its own kind", join_pattern_kind(r"\bE[0-9]{3,}\b") == "card")
    leg("a compiled module pattern is resolved to its literal",
        compiled_patterns(ast.parse('import re\nCARD_RE = re.compile(r"\\bE[0-9]{3,}\\b")\n'))
        == {"CARD_RE": "\\bE[0-9]{3,}\\b"})
    leg("a non-compiled module assignment is not a pattern",
        compiled_patterns(ast.parse('X = 1\n')) == {})
    leg("a stem pattern probe is its own kind", join_pattern_kind(r"e[0-9]{3,}_[a-z0-9_]+")
        == "stem")
    leg("prose is another question", join_pattern_kind("nothing in particular") == "other")

    fr = identity_field_reads(ast.parse('v = d["study"]\n'))
    leg("a subscript identity read is counted", fr["identity_read_sites"] == 1)
    leg("an identity key read is published", fr["identity_keys_read"] == ["study"])
    leg("a get() identity read is counted",
        identity_field_reads(ast.parse('v = d.get("card")\n'))["identity_read_sites"] == 1)
    leg("a non-identity subscript is not counted",
        identity_field_reads(ast.parse('v = d["rows"]\n'))["identity_read_sites"] == 0)

    d = ast.parse('"""E271 -- a study."""\nX = {"study": s, "rows": r, "card": "E1"}\n')
    leg("an identity-named dict key is found", identity_keys_written(d) == ["card", "study"])
    leg("a non-identity dict key is not counted",
        identity_keys_written(ast.parse('X = {"title": t}\n')) == [])
    leg("a module string constant is found",
        module_constants(ast.parse('CARD = "E271"\nN = 3\n')) == [{"name": "CARD", "value": "E271"}])
    leg("a module non-string constant is not counted",
        module_constants(ast.parse("N = 3\n")) == [])
    leg("the producer's own card comes from its file name",
        _own_card("scripts/e271_donor_choice_sensitivity.py") == "E271")
    leg("a non-study script has no filename card", _own_card("scripts/smoke_test.py") is None)
    leg("the docstring does not count as a card literal site",
        own_card_literal_sites(ast.parse('"""E271 -- a study."""\n'), "E271") == 0)
    leg("a card literal outside the docstring is a site",
        own_card_literal_sites(ast.parse('"""E271."""\nC = "E271"\n'), "E271") == 1)

    leg("a literal site wins the cheapest channel", producer_class(True, 2, ["card"]) == C_LITERAL)
    leg("an identity key without a literal is its own channel",
        producer_class(False, 0, ["card"]) == C_FIELD)
    leg("a docstring-only card is its own channel", producer_class(True, 0, []) == C_DOCSTRING)
    leg("a producer that never restates is its own channel",
        producer_class(False, 0, []) == C_NOT_RESTATED)

    leg("a join is the strongest tier", reader_tier(1, True, 1) == T_JOIN)
    leg("a join counts even when the card signal is only the pattern in the same call",
        reader_tier(1, True, 2) == T_JOIN)
    leg("a docstring reader with a card but no join is one tier down",
        reader_tier(1, True, 0) == T_DOC_AND_CARD)
    leg("a docstring reader with no card is the plain tier",
        reader_tier(1, False, 0) == T_DOC_ONLY)
    leg("a card reader with no docstring is counted apart",
        reader_tier(0, True, 0) == T_CARD_NO_DOC)
    leg("silence is its own tier", reader_tier(0, False, 0) == T_NONE)

    leg("no producer is its own verdict", verdict_for(0, {}) == V_EMPTY)
    leg("no docstring reader is its own verdict", verdict_for(3, {T_NONE: 5}) == V_NO_DOC_READER)
    leg("docstring readers with no card is its own verdict",
        verdict_for(3, {T_DOC_ONLY: 2}) == V_DOC_READER_NO_CARD)
    leg("a docstring reader with a card is its own verdict",
        verdict_for(3, {T_DOC_AND_CARD: 1}) == V_DOC_AND_CARD)
    leg("a real join is the strongest verdict", verdict_for(3, {T_JOIN: 1}) == V_JOIN)
    leg("the class vocabulary is closed",
        set(CLASSES) == {C_LITERAL, C_FIELD, C_DOCSTRING, C_NOT_RESTATED})
    leg("the tier vocabulary is closed",
        set(TIERS) == {T_JOIN, T_DOC_AND_CARD, T_CARD_NO_DOC, T_DOC_ONLY, T_NONE})
    leg("the verdict vocabulary is closed", set(VERDICT_VOCAB) == {
        V_EMPTY, V_NO_DOC_READER, V_DOC_READER_NO_CARD, V_DOC_AND_CARD, V_JOIN})
    leg("this study's own files are not in its own corpus",
        not any(os.path.basename(s).startswith(("e467", "_e467", "run_e467")) for s in corpus()))
    print("%d/%d" % (ok, total))
    return 0 if ok == total else 1


def main(argv) -> int:
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "run":
        payload = build(write=True)
        print(json.dumps(payload["summary"], ensure_ascii=False, sort_keys=True)[:1400])
        print(payload["verdict"])
        return 0
    if cmd == "check":
        return check()
    if cmd == "verify":
        return verify()
    if cmd == "selftest":
        return selftest()
    print("usage: python scripts/e467_docstringcard.py run|check|verify|selftest")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))