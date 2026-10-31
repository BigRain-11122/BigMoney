"""E331 -- who reads a face through a `_latest` pointer and nothing else, and what a missing
pointer does to them.

E330 closed with a hedge: the tree's only two-reference decision is e242's `_face_file`, and its
fallback is a *pinned date*.  E327 measured the other half of the pointer layer -- readers that
resolve a family through a `_latest` pointer and never see a date in a file name -- but it stopped
at "does the cutoff survive".  Neither asked the question a pointer makes unavoidable:

    a reader with no fallback gets NOTHING when the pointer is absent, or when the pointer names a
    cut that is not on disk.  What happens then: an explicit branch, a raise at the file, or a
    failure that surfaces far from its cause?

This study measures exactly that, on the python corpus, statically, with no file moved and no face
rewritten.  A (source, family) pair is in population when the source names `<stem>_latest.json`
anywhere outside its selftest region and names no dated cut `<stem>-<date>.json` and no
`<stem>-%s.json` template of the same stem.  Those pairs are then split three ways, and only the
third is measured for handling:

  writer_only                 every occurrence writes the pointer -- a producer is not a reader
  chain_with_a_variable_first the pointer sits in an ordered container beside a variable, or is
                              handed to a resolver helper whose body loops over candidates: that is
                              E329's chain, not a pointer-only reader
  pointer_only_reader         the pointer is the sole resolution route the source has

For each pointer-only reader the load site is resolved (a direct `open`/`json.load`, or a call to a
helper whose own body loads), and the missing-file handling is classified in this order:

  guarded_by_an_existence_test   os.path.isfile/exists/is_file on the path, in the same source
  guarded_by_try_except          a `try:` in the loading function with its `except` after the load
  defaults_to_an_empty_payload   `X or {}` / `or []` on the loaded value
  narrowed_after_the_load        `if X is None` / `if not X` / `if X:` in the lines after the load
  a_helper_returns_none_and_nothing_checks_it
                                 the helper turns a missing file into None (often after its own
                                 existence test) and the caller never branches on it: the failure
                                 surfaces at the first subscript, far from the file
  the_load_raises_at_the_file    a direct `open`/`json.load` or a propagating helper: the
                                 FileNotFoundError names the path, which is loud at the cause
  unresolved                     no load site could be resolved from the source -- published as
                                 such rather than counted as safe

The disk half answers "gets nothing today": for every family a pointer-only reader names, whether
the pointer file exists and whether the cut it states is itself on disk.

Usage:
    python scripts/e331_pointer_only_readers.py run|verify|selftest
"""
import io
import json
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import e326_template_parameter_consumers as e326  # noqa: E402  (path set above)
import e329_two_vintage_binding as e329  # noqa: E402
import e330_unpinned_choice as e330  # noqa: E402

ROOT = e326.ROOT
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
TODAY = "2026-11-01"
FACE = "POINTERONLY-%s.json" % TODAY
LATEST = "pointeronly_latest.json"
STUDY = "E331_pointer_only_readers"

WRITE_DUMP = re.compile(r"json\.dump\b|\.write\s*\(")
OPEN_CALL = re.compile(r"\b(?:io\.)?open\s*\(")
OPEN_W = re.compile(r"\b(?:io\.)?open\s*\(.*[\"']w")
LOAD_INLINE = re.compile(r"json\.load\s*\(|\.read_text\s*\(")
EXIST = re.compile(r"(isfile|is_file|exists)\s*\(")
OR_EMPTY = re.compile(r"\bor\s*(\{\s*\}|\[\s*\]|''|\"\")\s*(?:[,):]|$)")
NONE_TEST = re.compile(r"\bis\s+None\b|\bnot\s+[A-Za-z_][A-Za-z0-9_]*\b|"
                       r"\bif\s+[A-Za-z_][A-Za-z0-9_]*\s*:\s*$")
CALL = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\s*\(")
DEF = re.compile(r"^def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(")
ASSIGN = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=")
ORDERED = re.compile(r"for\s+[A-Za-z_][A-Za-z0-9_]*\s+in\s*\(")
TRY = re.compile(r"^\s*try\s*:")
INDENT = re.compile(r"^(\s*)")

K_WRITER = "writer_only"
K_CHAIN = "chain_with_a_variable_first"
K_READER = "pointer_only_reader"
K_REFERENCE = "reference_without_a_reader"
PAIR_CLASSES = (K_WRITER, K_CHAIN, K_REFERENCE, K_READER)

H_EXIST = "guarded_by_an_existence_test"
H_TRY = "guarded_by_try_except"
H_EMPTY = "defaults_to_an_empty_payload"
H_NONE = "narrowed_after_the_load"
H_SOFT = "a_helper_returns_none_and_nothing_checks_it"
H_CALLEE = "the_callee_absorbs_the_None"
H_LOUD = "the_load_raises_at_the_file"
HANDLING = (H_SOFT, H_CALLEE, H_LOUD, H_EMPTY, H_NONE, H_TRY, H_EXIST)
# order matters: the first class that applies is the one published
PRECEDENCE = (H_EXIST, H_TRY, H_EMPTY, H_NONE)

C_SOFT_NONE = "turns_a_missing_file_into_None"
C_RAISE = "raises_at_the_file"
C_PROPAGATES = "propagates_the_open_error"
C_UNKNOWN = "not_defined_in_the_corpus"

V_SILENT = ("a_pointer_only_reader_turns_a_missing_pointer_into_a_failure_far_from_its_cause")
V_EXPOSED = ("every_pointer_only_reader_is_guarded_but_a_pointer_some_of_them_name_resolves_to_"
             "nothing_today")
V_SAFE = ("every_pointer_only_reader_raises_at_the_file_or_guards_it_and_every_pointer_it_names_"
          "resolves_today")
VERDICTS = (V_SILENT, V_EXPOSED, V_SAFE)

R_ABSENT = "pointer_absent"
R_CUT_MISSING = "stated_cut_not_on_disk"
R_NO_CUT_STATED = "pointer_states_no_cutoff"
R_ONLY_FORMAT = "the_pointer_is_the_familys_only_published_form"
R_RESOLVES = "stated_cut_on_disk"
RESOLUTIONS = (R_ABSENT, R_CUT_MISSING, R_NO_CUT_STATED, R_ONLY_FORMAT, R_RESOLVES)

GLOBAL_SOURCES = ("Tools/s6_chain_bmb.py", "smoke_test.py")
OWN_FACES = (FACE, LATEST)
OWN_SOURCES = (os.path.basename(__file__),)
MAX_ROWS = 300
MAX_SITES = 3


# ---------------------------------------------------------------------------------- primitives

def _clean(text):
    return e329._clean(text)


def is_write_line(text):
    """A line that produces the pointer rather than consumes it."""
    body = _clean(text)
    if WRITE_DUMP.search(body):
        return True
    return bool(OPEN_W.search(body))


def is_prose(text):
    """A line that is nothing but text (a docstring, a fixture string, a prose row)."""
    return not e330.code_mask(_clean(text)).strip()


def helper_index(files):
    """(global, per_source) name -> {contract, loads, writes, ordered}.

    A name is not unique in a 2,284-file corpus (``_read``, ``_dump``, ``_face`` are redefined in
    dozens of studies), so a source's own definition wins and the corpus-wide table is only a
    fallback: resolving a load through another file's helper is how a writer gets read as a reader.
    """
    index = {}
    per_source = {}
    for path, src in files:
        local = per_source.setdefault(e326.relp(path), {})
        lines = e329._code_lines(src)
        for i, (_n, text) in enumerate(lines):
            match = DEF.match(text)
            if not match:
                continue
            body = []
            for j in range(i + 1, len(lines)):
                nxt = lines[j][1]
                if DEF.match(nxt) and not nxt[:1].isspace():
                    break
                body.append(nxt)
            joined = "\n".join(body)
            param = ""
            sig = text[text.find("(") + 1:]
            first = sig.split(")")[0].split(",")[0].split("=")[0].strip()
            if first and first.isidentifier():
                param = first
            absorbs = bool(param) and bool(
                re.search(r"if\s+not\s+%s\b" % re.escape(param), joined)
                or re.search(r"\b%s\s+is\s+None\b" % re.escape(param), joined)
                or re.search(r"if\s+%s\s*:" % re.escape(param), joined))
            writes = bool(WRITE_DUMP.search(joined) or OPEN_W.search(joined))
            reads = bool(LOAD_INLINE.search(joined) or (OPEN_CALL.search(joined) and not writes))
            loads = reads
            missing_to_none = (re.search(r"return\s+None", joined)
                               and (re.search(r"except", joined) or EXIST.search(joined)))
            if missing_to_none:
                contract = C_SOFT_NONE
            elif re.search(r"^\s*raise\b", joined, re.M):
                contract = C_RAISE
            elif loads:
                contract = C_PROPAGATES
            else:
                contract = C_UNKNOWN
            entry = {"contract": contract, "loads": loads, "writes": writes,
                     "ordered": bool(ORDERED.search(joined)), "absorbs_none": absorbs}
            local.setdefault(match.group(1), entry)
            index.setdefault(match.group(1), entry)
    return index, per_source


def norm_stem(name):
    """A family stem without the punctuation that differs between a pointer and its dated cut.

    This disk publishes ``per_member_gamma_latest.json`` beside ``PER-MEMBER-GAMMA-2026-10-30.json``
    and ``call_latest.json`` beside ``CALL-2026-10-27.md``: comparing raw stems reported five
    families as unresolvable when every one of them resolves (first draft's headline).
    """
    return re.sub(r"[^a-z0-9]", "", (name or "").lower())


DATED_ANY = re.compile(r"(?P<stem>[A-Za-z0-9_.+\-]*?)-(?P<date>\d{4}-\d{2}-\d{2})\."
                       r"(?:json|md|csv)$")


def disk_cuts(root):
    """Normalized stem -> set of dated vintages, across the extensions a face is published in."""
    cuts = {}
    base = os.path.join(root, "results")
    for dirpath, _dirnames, filenames in os.walk(base):
        for name in filenames:
            match = DATED_ANY.match(name)
            if not match:
                continue
            cuts.setdefault(norm_stem(match.group("stem")), set()).add(match.group("date"))
    return cuts


def tail_is_invisible(src, lines):
    """Lines the corpus helper dropped from the END of the file (an unclosed triple quote)."""
    raw = src.splitlines()
    if not raw or not lines:
        return 0
    last_raw = len(raw)
    while last_raw > 0 and not raw[last_raw - 1].strip():
        last_raw -= 1
    last_seen = lines[-1][0]
    return max(0, last_raw - last_seen)


def quoted_span_at(text, pos):
    """The (start, end) of the quoted literal containing ``pos``, or None when it is not quoted."""
    quote = None
    start = 0
    escape = False
    for index, ch in enumerate(text):
        if quote:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == quote:
                if start <= pos <= index:
                    return start, index + 1
                quote = None
        elif ch in "\"'":
            quote = ch
            start = index
    return None


def is_path_literal(text, pos):
    """A pointer inside a prose sentence is a note; only a path-shaped literal is a reference.

    ``"see results/x/foo_latest.json for the receipt"`` is a doc row.  whitespace inside the
    literal is the discriminator, and it is published rather than folded away (r1281 shape).
    """
    span = quoted_span_at(text, pos)
    if span is None:
        return True
    return not re.search(r"\s", text[span[0] + 1:span[1] - 1])


def family_occurrences(lines, stop):
    """Line-level handles per family: stem -> list of occurrences (idx, lineno, text, written)."""
    latest, dated = {}, set()
    stats = {"prose_literals_rejected": 0}
    for idx, (lineno, text) in enumerate(lines):
        if idx >= stop or is_prose(text):
            continue
        for handle in e329.handles_in_line(text, lineno):
            stem = (handle["stem"] or "").lower()
            if not stem:
                continue
            if not is_path_literal(text, handle["pos"]):
                stats["prose_literals_rejected"] += 1
                continue
            if handle["kind"] == e329.K_LATEST:
                latest.setdefault(stem, []).append({
                    "idx": idx, "line": lineno, "text": text, "written": is_write_line(text)})
            elif handle["kind"] in (e329.K_DATED, e329.K_TEMPLATE):
                dated.add(stem)
    return latest, dated, stats


def bound_names(occurrences):
    names = set()
    for occ in occurrences:
        match = ASSIGN.match(e330.code_mask(_clean(occ["text"])))
        if match:
            names.add(match.group(1))
    return names


def mentioned(text, name, stem):
    """Does this line mention the bound path name, or spell the family's pointer literal?"""
    if name and re.search(r"\b%s\b" % re.escape(name), text):
        return True
    for handle in e329.handles_in_line(text, 0):
        if handle["kind"] == e329.K_LATEST and (handle["stem"] or "").lower() == stem:
            return True
    return False


def load_sites(lines, stop, name, stem, helpers):
    """Every line that loads the pointer: a direct open/json.load, or a call to a loading helper.

    A line that writes the pointer is not a load site: ``with io.open(latest, "w") as fh`` names
    the pointer in a produce step, and counting it would publish a producer's own output as the
    place its reader would fail (this study's first draft did exactly that for four studies).
    """
    out = []
    for idx, (lineno, text) in enumerate(lines):
        if idx >= stop or not mentioned(text, name, stem) or is_write_line(text):
            continue
        body = _clean(text)
        mask = e330.code_mask(body)
        if OPEN_CALL.search(mask) or LOAD_INLINE.search(mask):
            out.append({"idx": idx, "line": lineno, "text": text, "helper": None})
            continue
        called = [c for c in CALL.findall(mask) if c in helpers and helpers[c]["loads"]]
        if called:
            out.append({"idx": idx, "line": lineno, "text": text, "helper": called[-1]})
    return out


def raw_indents(src):
    """line number -> leading-space count, from the raw source.

    ``code_lines`` strips indentation, so the block structure a guard is read from has to come from
    the raw file; the line numbers are the same because ``code_lines`` keeps the original numbering.
    """
    out = {}
    for lineno, line in enumerate((src or "").splitlines(), 1):
        out[lineno] = len(line) - len(line.lstrip())
    return out


def _function_span(lines, index, indents=None):
    """(start, end) of the function enclosing ``index``, or the module span."""
    indents = indents or {}
    start = 0
    for back in range(index, -1, -1):
        if DEF.match(lines[back][1]):
            start = back
            break
    base = indents.get(lines[start][0], 0)
    end = len(lines)
    for ahead in range(start + 1, len(lines)):
        text = lines[ahead][1]
        indent = indents.get(lines[ahead][0], 0)
        if DEF.match(text) and indent <= base:
            end = ahead
            break
        if indent == 0 and not text.startswith(("#", "@")) and not DEF.match(text):
            end = ahead
            break
    return start, end


def expression_span(lines, idx):
    """The load expression as one string: the line plus its continuation lines only.

    ``or {}`` counts as a guard when it sits on the loaded value, not when a later statement
    happens to contain one.  This study's second draft read a neighbouring ``s = face.get(...)
    or {}`` as a guard for the load above it and missed the real finding twice.
    """
    parts = [lines[idx][1]]
    depth = _paren_balance(lines[idx][1])
    cursor = idx
    while (depth > 0 or parts[-1].rstrip().endswith("\\")) and cursor + 1 < len(lines) \
            and cursor - idx < 5:
        cursor += 1
        parts.append(lines[cursor][1])
        depth += _paren_balance(lines[cursor][1])
    return "\n".join(parts)


def _paren_balance(text):
    mask = e330.code_mask(_clean(text))
    return mask.count("(") - mask.count(")")


def handling_of(lines, site, name, stem, helpers, indents=None):
    """How a missing pointer surfaces at this load site."""
    idx = site["idx"]
    start, end = _function_span(lines, idx, indents)
    before = lines[start:idx]
    body_indent = (indents or {}).get(lines[idx][0], 0)
    for _n, text in before:
        mask = e330.code_mask(_clean(text))
        if EXIST.search(mask) and mentioned(text, name, stem):
            return H_EXIST, "an existence test names this path before the load"
    for _n, text in before:
        match = TRY.match(text)
        if match and (indents.get(_n, 0) if indents else 0) <= body_indent:
            return H_TRY, "a try: block encloses the load"
    expression = _clean(expression_span(lines, idx))
    if OR_EMPTY.search(expression):
        return H_EMPTY, "the loaded value falls back to an empty payload"
    target = None
    match = ASSIGN.match(e330.code_mask(_clean(lines[idx][1])))
    if match:
        target = match.group(1)
    for _n, text in lines[idx + 1:min(end, idx + 6)]:
        mask = e330.code_mask(_clean(text))
        if target and re.search(r"\b%s\b" % re.escape(target), mask) and NONE_TEST.search(mask):
            return H_NONE, "the loaded value is branched on before it is used"
    loader = site["helper"]
    if loader and helpers[loader]["contract"] == C_SOFT_NONE:
        absorbers = [c for c in CALL.findall(e330.code_mask(expression))
                     if c != loader and (helpers.get(c) or {}).get("absorbs_none")]
        if absorbers:
            return H_CALLEE, "%s returns None and %s branches on it" % (loader, absorbers[-1])
        return H_SOFT, "%s turns a missing file into None and nothing checks it" % (loader,)
    if loader:
        return H_LOUD, "%s lets the open error out, naming the path" % (loader,)
    return H_LOUD, "the source opens the file directly, so a miss names the path"


def pair_class(occurrences, helpers, sites):
    """chain / writer_only / reference_without_a_reader / reader.

    A pointer that sits inside an ordered container beside another candidate is a chain (E329's
    subject) whether or not this file also loads it: the pointer is not the only route.  Otherwise
    the class follows the load site, not the wording -- a path that is only bound and later written
    is a producer, and a path published in a census dict is a reference.
    """
    for occ in occurrences:
        mask = e330.code_mask(_clean(occ["text"]))
        if ORDERED.search(mask):
            return K_CHAIN, "the pointer is a candidate in an ordered container"
        for name in CALL.findall(mask):
            entry = helpers.get(name)
            if entry and entry["ordered"]:
                return K_CHAIN, "%s loops over candidates" % (name,)
    if sites:
        return K_READER, "the pointer is loaded here and the source has no dated cut of the family"
    if any(occ["written"] for occ in occurrences):
        return K_WRITER, "every use of the pointer in this source produces it"
    return K_REFERENCE, "the pointer is named but neither loaded nor written"


# ------------------------------------------------------------------------------------ census

def build(root=None, outdir=None, files=None):
    root = root or ROOT
    files = files if files is not None else e326.corpus()
    hindex, hper = helper_index(files)
    cuts, pointers, paths, _spellings = e329.disk_index(root)
    cuts_any = disk_cuts(root)
    payloads = {}
    rows = []
    stats = {"sources": 0, "families_seen": 0, "pairs": 0}
    blind = []
    seen_sources = set()
    for path, src in files:
        rel = e326.relp(path)
        if os.path.basename(rel) in OWN_SOURCES:
            continue
        seen_sources.add(rel)
        lines = e329._code_lines(src)
        stop = e329.selftest_start(lines)
        indents = raw_indents(src)
        helpers = dict(hindex)
        helpers.update(hper.get(rel, {}))
        raw_lines = len(src.splitlines())
        lost = tail_is_invisible(src, lines)
        if lost > 10:
            blind.append({"source": rel, "raw_lines": raw_lines, "last_visible_line": lines[-1][0],
                          "dropped_tail_lines": lost})
        latest, dated, occ_stats = family_occurrences(lines, stop)
        stats["prose_literals_rejected"] = stats.get("prose_literals_rejected", 0) + \
            occ_stats["prose_literals_rejected"]
        for stem, occurrences in sorted(latest.items()):
            stats["families_seen"] += 1
            if stem in dated:
                continue  # the source also names a dated cut of this family: that is E329's chain
            names = sorted(bound_names(occurrences))
            sites, name = [], None
            for candidate in names:
                found = load_sites(lines, stop, candidate, stem, helpers)
                if found:
                    sites, name = found, candidate
                    break
            if not sites:
                sites = load_sites(lines, stop, None, stem, helpers)
            klass, why = pair_class(occurrences, helpers, sites)
            row = {"source": rel, "family": stem, "class": klass, "class_why": why,
                   "occurrences": len(occurrences),
                   "first_line": occurrences[0]["line"],
                   "first_text": occurrences[0]["text"].strip()[:120],
                   "bound_names": names}
            if klass == K_READER:
                row["load_sites"] = sites[:MAX_SITES]
                row["load_site_count"] = len(sites)
                verdicts = []
                for site in sites:
                    handling, why2 = handling_of(lines, site, name, stem, helpers, indents)
                    verdicts.append((handling, why2, site))
                pick = None
                for wanted in PRECEDENCE + (H_SOFT, H_LOUD):
                    pick = next((v for v in verdicts if v[0] == wanted), None)
                    if pick:
                        break
                if pick is None:
                    pick = verdicts[0]
                row["handling"] = pick[0]
                row["handling_why"] = pick[1]
                row["load_line"] = pick[2]["line"]
                row["load_text"] = pick[2]["text"].strip()[:140]
                row["load_helper"] = pick[2]["helper"]
                row["helper_contract"] = (helpers.get(pick[2]["helper"]) or {}).get("contract")
                # disk half: does this family's pointer resolve today?
                pointer_path = paths.get(stem)
                cut = e329.pointer_cut(pointer_path, payloads) if pointer_path else None
                dated_vintages = cuts_any.get(norm_stem(stem)) or set()
                row["pointer_on_disk"] = bool(pointer_path)
                row["pointer_stated_cut"] = cut
                row["dated_vintages_on_disk"] = len(dated_vintages)
                if not pointer_path:
                    resolution = R_ABSENT
                elif not cut:
                    resolution = R_NO_CUT_STATED
                elif not dated_vintages:
                    # the family publishes no dated face at all, so the pointer is its only form
                    # and the cutoff it states refers to data, not to a sibling file name
                    resolution = R_ONLY_FORMAT
                elif cut in dated_vintages or cut in (cuts.get(stem) or set()):
                    resolution = R_RESOLVES
                else:
                    resolution = R_CUT_MISSING
                row["resolution"] = resolution
                row["resolves_today"] = resolution == R_RESOLVES
            rows.append(row)
    stats["sources"] = len(seen_sources)
    stats["pairs"] = len(rows)

    readers = [r for r in rows if r["class"] == K_READER]
    by_handling = {h: [r for r in readers if r.get("handling") == h] for h in HANDLING}
    soft = by_handling[H_SOFT]
    missing = [r for r in readers if r.get("resolution") == R_ABSENT]
    cut_missing = [r for r in readers if r.get("resolution") == R_CUT_MISSING]
    guarded = [r for r in readers if r.get("handling") in (H_EXIST, H_TRY, H_EMPTY, H_NONE, H_CALLEE)]

    if soft:
        verdict = V_SILENT
        reason = ("%d of %d pointer-only readers load through a helper that turns a missing file "
                  "into None and neither the caller nor its callee branches on it"
                  % (len(soft), len(readers)))
    elif missing or cut_missing:
        verdict = V_EXPOSED
        reason = ("every pointer-only reader guards the value or raises at the file, but %d name a "
                  "pointer that is absent and %d a pointer whose stated cut has no dated sibling on "
                  "disk" % (len(missing), len(cut_missing)))
    else:
        verdict = V_SAFE
        reason = ("all %d pointer-only readers either branch before using the value or let the open "
                  "error name the path, and no pointer they name is absent; %d families cannot be "
                  "judged because the pointer is their only published form"
                  % (len(readers), sum(1 for r in readers
                                       if r.get("resolution") == R_ONLY_FORMAT)))

    summary = {
        "sources_scanned": stats["sources"],
        "families_referenced_only_through_a_pointer": stats["families_seen"],
        "pairs": len(rows),
        "pairs_by_class": {k: sum(1 for r in rows if r["class"] == k) for k in PAIR_CLASSES},
        "pointer_only_readers": len(readers),
        "distinct_families_read": len({r["family"] for r in readers}),
        "distinct_pointer_files_named": len({r["family"] for r in readers}),
        "handling_by_class": {h: len(by_handling[h]) for h in HANDLING},
        "readers_guarded_before_they_use_the_value": len(guarded),
        "readers_whose_helper_turns_a_miss_into_None": len(soft),
        "readers_whose_None_is_absorbed_by_the_callee": len(by_handling[H_CALLEE]),
        "readers_that_raise_at_the_file": len(by_handling[H_LOUD]),
        "pointer_files_missing_on_disk_today": len(missing),
        "pointers_whose_stated_cut_is_not_on_disk_today": len(cut_missing),
        "pointers_that_state_no_cutoff": sum(
            1 for r in readers if r.get("resolution") == R_NO_CUT_STATED),
        "families_that_resolve_today": len({r["family"] for r in readers if r["resolves_today"]}),
        "families_read_but_unresolvable_today": len({r["family"] for r in readers
                                                     if not r["resolves_today"]}),
        "prose_literals_rejected_as_notes": stats.get("prose_literals_rejected", 0),
        "sources_whose_tail_the_scanner_cannot_see": len(blind),
        "rows_published": min(len(rows), MAX_ROWS),
        "rows_truncated": max(0, len(rows) - MAX_ROWS),
    }
    doc = {
        "study": STUDY,
        "evidence_cutoff": TODAY,
        "verdict": verdict,
        "verdict_reason": reason,
        "summary": summary,
        "rules": {
            "population": "a source names <stem>_latest.json outside its selftest region and names "
                          "no dated cut or template of the same stem",
            "reader": "not every occurrence writes the pointer",
            "pointer_only": "the pointer is not a candidate in an ordered container and not handed "
                            "to a helper that loops over candidates",
            "load_site": "a line that opens the pointer directly or calls a helper whose own body "
                         "opens a file",
            "handling precedence": "existence test, then try/except, then `or {}`, then a None "
                                   "branch after the load, then the helper's contract",
        },
        "limits": {
            "static": "a reader that resolves a pointer through a computed name is not seen, which "
                      "under-counts the population rather than over-counting a finding",
            "helper_scope": "a helper defined outside scripts/Tools/live/monitor/firm is not in the "
                            "corpus, so its contract is reported as unknown and its caller as loud",
            "single_line": "a try: block is detected at the indent of the loading line; a load "
                           "inside a one-line `try: ... except ...` is out of population for this "
                           "measurement",
            "presence_not_behaviour": "the tool never deletes a pointer to watch a reader fire; "
                                      "the disk half reports what would be missing if it did",
            "fixture_strings": "a pointer name inside a quoted string that forms no code (a doc "
                               "row, a fixture) is not an occurrence",
            "invisible_tail": "the corpus helper drops a triple-quoted block to its end, so a "
                              "source whose docstring logic continues past a point loses the rest "
                              "of its lines; the count of such sources is published because a load "
                              "site in that tail cannot be seen (e312 is one)",
        },
        "rows": rows[:MAX_ROWS],
        "sources_with_an_invisible_tail": blind[:24],
    }
    target = outdir or OUTDIR
    os.makedirs(target, exist_ok=True)
    body = json.dumps(doc, ensure_ascii=False, indent=1) + "\n"
    for name in (FACE, LATEST):
        with io.open(os.path.join(target, name), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body)
    return doc


# ------------------------------------------------------------------------------------ verify

def verify(root=None, files=None):
    root = root or ROOT
    fresh = build(root=root, outdir=tempfile.mkdtemp(prefix="e331_verify_"), files=files)
    path = os.path.join(root, "results", "state_tilt", FACE)
    try:
        with io.open(path, encoding="utf-8") as fh:
            disk = json.load(fh)
    except Exception as exc:
        return ["the face does not read: %r" % (exc,)]
    problems = []
    if disk.get("verdict") != fresh["verdict"]:
        problems.append("the verdict does not re-derive")
    if disk.get("verdict") not in VERDICTS:
        problems.append("verdict %r is outside the frozen set" % (disk.get("verdict"),))
    for key, value in fresh["summary"].items():
        if (disk.get("summary") or {}).get(key) != value:
            problems.append("summary.%s does not re-derive" % key)
    published = [(r["source"], r["family"], r["class"], r.get("handling")) for r in
                 disk.get("rows") or []]
    recomputed = [(r["source"], r["family"], r["class"], r.get("handling")) for r in fresh["rows"]]
    if published != recomputed:
        problems.append("a published pair does not re-derive")
    for row in disk.get("rows") or []:
        if row["class"] == K_READER and not row.get("handling"):
            problems.append("a pointer-only reader carries no handling class")
            break
        if row["class"] != K_READER and row.get("handling"):
            problems.append("a %s row carries a handling class" % (row["class"],))
            break
    return problems


# ------------------------------------------------------------------------------------ selftest

def _fixture():
    """A tree with one pointer-only reader per handling class, plus a writer and a chain."""
    root = tempfile.mkdtemp(prefix="e331_fx_")
    st = os.path.join(root, "results", "state_tilt")
    os.makedirs(st, exist_ok=True)

    def write(name, payload):
        with io.open(os.path.join(st, name), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(payload, fh, indent=1)

    write("AAA-2026-10-01.json", {"evidence_cutoff": "2026-10-01"})
    write("AAA_latest.json", {"evidence_cutoff": "2026-10-01"})
    # BBB: the pointer exists and states a cut that is NOT on disk
    write("BBB_latest.json", {"evidence_cutoff": "2026-09-30"})
    write("BBB-2026-09-29.json", {"evidence_cutoff": "2026-09-29"})
    # CCC: no pointer on disk at all
    write("CCC-2026-09-29.json", {"evidence_cutoff": "2026-09-29"})
    # DDD/E32x families used by guarded readers
    for stem, cut in (("DDD", "2026-10-01"), ("EEE", "2026-10-01"), ("FFF", "2026-10-01"),
                      ("GGG", "2026-10-01"), ("MMM", "2026-10-01")):
        write("%s-%s.json" % (stem, cut), {"evidence_cutoff": cut})
        write("%s_latest.json" % stem, {"evidence_cutoff": cut})

    src = os.path.join(root, "scripts")
    os.makedirs(src, exist_ok=True)
    bodies = {
        # soft helper: existence test inside, returns None, caller never checks
        "soft.py": (
            'import io, json, os\n'
            'OUT = "results/state_tilt"\n'
            'def _face(name):\n'
            '    p = os.path.join(OUT, name)\n'
            '    if not os.path.exists(p):\n'
            '        return None\n'
            '    with io.open(p, encoding="utf-8") as fh:\n'
            '        return json.load(fh)\n'
            'def run():\n'
            '    face = _face("AAA_latest.json")\n'
            '    return face["verdict"]\n'
            'def selftest():\n'
            '    return True\n'),
        # guarded by an existence test on the path before the open
        "exist_guard.py": (
            'import io, json, os\n'
            'OUT = "results/state_tilt"\n'
            'def run():\n'
            '    p = os.path.join(OUT, "BBB_latest.json")\n'
            '    if not os.path.exists(p):\n'
            '        return {}\n'
            '    with io.open(p, encoding="utf-8") as fh:\n'
            '        return json.load(fh)\n'
            'def selftest():\n'
            '    return True\n'),
        # try / except around the load
        "try_guard.py": (
            'import io, json, os\n'
            'OUT = "results/state_tilt"\n'
            'def run():\n'
            '    p = os.path.join(OUT, "EEE_latest.json")\n'
            '    try:\n'
            '        with io.open(p, encoding="utf-8") as fh:\n'
            '            return json.load(fh)\n'
            '    except OSError:\n'
            '        return {}\n'
            'def selftest():\n'
            '    return True\n'),
        # or {} on the loaded value
        "empty_guard.py": (
            'import io, json, os\n'
            'OUT = "results/state_tilt"\n'
            'def _read(path):\n'
            '    with io.open(path, encoding="utf-8") as fh:\n'
            '        return json.load(fh)\n'
            'def run():\n'
            '    face = _read(os.path.join(OUT, "FFF_latest.json")) or {}\n'
            '    return face.get("x")\n'
            'def selftest():\n'
            '    return True\n'),
        # None branch after the load
        "none_guard.py": (
            'import io, json, os\n'
            'OUT = "results/state_tilt"\n'
            'def _face(name):\n'
            '    p = os.path.join(OUT, name)\n'
            '    if not os.path.exists(p):\n'
            '        return None\n'
            '    with io.open(p, encoding="utf-8") as fh:\n'
            '        return json.load(fh)\n'
            'def run():\n'
            '    face = _face("CCC_latest.json")\n'
            '    if face is None:\n'
            '        return {}\n'
            '    return face.get("x")\n'
            'def selftest():\n'
            '    return True\n'),
        # writer only
        "writer.py": (
            'import io, json, os\n'
            'OUT = "results/state_tilt"\n'
            'def run(payload):\n'
            '    with io.open(os.path.join(OUT, "HHH_latest.json"), "w", encoding="utf-8") as fh:\n'
            '        json.dump(payload, fh)\n'
            'def selftest():\n'
            '    return True\n'),
        # a chain over a variable first: not a pointer-only reader
        "chain.py": (
            'import os\n'
            'OUT = "results/state_tilt"\n'
            'def run(name):\n'
            '    for fn in (name, "III_latest.json"):\n'
            '        p = os.path.join(OUT, fn)\n'
            '        if os.path.isfile(p):\n'
            '            return p\n'
            '    return None\n'
            'def selftest():\n'
            '    return True\n'),
        # prose: a pointer name inside a doc row and a fixture string is not an occurrence
        "prose.py": (
            'NOTE = "see results/state_tilt/JJJ_latest.json for the receipt"\n'
            'def selftest():\n'
            '    return True\n'),
        # a soft loader whose None is absorbed by the callee one level out
        "callee.py": (
            'import io, json, os\n'
            'OUT = "results/state_tilt"\n'
            'def _read_face(path):\n'
            '    if not os.path.exists(path):\n'
            '        return None\n'
            '    with io.open(path, encoding="utf-8") as fh:\n'
            '        return json.load(fh)\n'
            'def _pair(face):\n'
            '    if not face:\n'
            '        return None\n'
            '    return face.get("x")\n'
            'def run():\n'
            '    return _pair(_read_face(os.path.join(OUT, "MMM_latest.json")))\n'
            'def selftest():\n'
            '    return True\n'),
    }
    files = []
    for name, body in bodies.items():
        path = os.path.join(src, name)
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body)
        files.append((path, body))
    tools = os.path.join(root, "Tools")
    os.makedirs(tools, exist_ok=True)
    with io.open(os.path.join(tools, "s6_chain_bmb.py"), "w", encoding="utf-8",
                 newline="\n") as fh:
        fh.write('LEGS = [("x", ["python", "scripts/x.py", "verify"])]\n')
    return root, files


def cmd_selftest():
    checks = []

    def check(name, ok, detail=""):
        checks.append((name, bool(ok), detail))
        print("%-6s %s%s" % ("PASS" if ok else "FAIL", name, "" if ok else "  <- " + detail))
        sys.stdout.flush()

    root, files = _fixture()
    doc = build(root=root, outdir=tempfile.mkdtemp(prefix="e331_fx_out_"), files=files)
    rows = doc["rows"]
    by_source = {}
    for row in rows:
        by_source.setdefault(row["source"], []).append(row)

    def row_for(name):
        hits = [r for src, rows_ in by_source.items() for r in rows_
                if src.endswith("/" + name) or src.endswith(name)]
        return hits[0] if hits else None

    soft = row_for("soft.py")
    check("L1 a soft helper whose caller never branches is flagged",
          soft is not None and soft["class"] == K_READER and soft["handling"] == H_SOFT,
          str(soft and (soft["class"], soft.get("handling"))))
    check("L2 the helper's contract is published beside the row",
          soft is not None and soft.get("helper_contract") == C_SOFT_NONE,
          str(soft and soft.get("helper_contract")))
    check("L3 the fixture verdict is the silent one", doc["verdict"] == V_SILENT, doc["verdict"])

    check("L4 an existence test before the load is its own class",
          row_for("exist_guard.py")["handling"] == H_EXIST,
          str(row_for("exist_guard.py")["handling"]))
    check("L5 a try block around the load is its own class",
          row_for("try_guard.py")["handling"] == H_TRY, str(row_for("try_guard.py")["handling"]))
    check("L6 `or {}` on the loaded value is its own class",
          row_for("empty_guard.py")["handling"] == H_EMPTY,
          str(row_for("empty_guard.py")["handling"]))
    check("L7 a None branch after the load is its own class",
          row_for("none_guard.py")["handling"] == H_NONE,
          str(row_for("none_guard.py")["handling"]))

    writer = row_for("writer.py")
    check("L8 a source that only writes the pointer is a writer, not a reader",
          writer is not None and writer["class"] == K_WRITER, str(writer and writer["class"]))
    chain = row_for("chain.py")
    check("L9 a pointer beside a variable in an ordered container is a chain",
          chain is not None and chain["class"] == K_CHAIN, str(chain and chain["class"]))
    check("L10 a pointer name inside a quoted prose row is not an occurrence",
          row_for("prose.py") is None, str(row_for("prose.py")))
    check("L11 every row carries a class in the frozen set",
          all(r["class"] in PAIR_CLASSES for r in rows), str({r["class"] for r in rows}))
    check("L12 only pointer-only readers carry a handling class",
          all((r.get("handling") is None) == (r["class"] != K_READER) for r in rows))

    check("L13 a pointer whose stated cut is not on disk is counted as exposing its readers",
          doc["summary"]["pointers_whose_stated_cut_is_not_on_disk_today"] >= 1,
          str(doc["summary"]["pointers_whose_stated_cut_is_not_on_disk_today"]))
    check("L14 summary counts equal the rows they summarize",
          doc["summary"]["pointer_only_readers"] == sum(
              1 for r in rows if r["class"] == K_READER)
          and sum(doc["summary"]["handling_by_class"].values()) ==
          doc["summary"]["pointer_only_readers"],
          str(doc["summary"]["handling_by_class"]))

    out = tempfile.mkdtemp(prefix="e331_fx_pub_")
    build(root=root, outdir=out, files=files)
    import shutil
    for name in os.listdir(out):
        shutil.copy(os.path.join(out, name), os.path.join(root, "results", "state_tilt", name))
    check("L15 verify reproduces the face it wrote", verify(root=root, files=files) == [],
          "; ".join(verify(root=root, files=files))[:140])
    disk_path = os.path.join(root, "results", "state_tilt", FACE)
    fresh = json.load(io.open(disk_path, encoding="utf-8"))
    fresh["summary"]["pointer_only_readers"] = 999
    with io.open(disk_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(fresh, fh)
    problems = verify(root=root, files=files)
    check("L16 verify refuses a doctored summary",
          any("pointer_only_readers" in p for p in problems), "; ".join(problems)[:140])

    # L17: with the soft reader removed the verdict must move on to the disk half
    keep = [f for f in files if not f[0].endswith("soft.py")]
    nosoft = build(root=root, outdir=tempfile.mkdtemp(prefix="e331_fx_ns_"), files=keep)
    check("L17 without the soft reader the verdict falls to the disk exposure",
          nosoft["verdict"] == V_EXPOSED, nosoft["verdict"])

    # L18: a pointer named in a source that never loads and never writes it is a reference
    src = os.path.join(root, "scripts")
    lonely = os.path.join(src, "lonely.py")
    body = ('PATH = "results/state_tilt/KKK_latest.json"\n'
            'def selftest():\n'
            '    return True\n')
    with io.open(lonely, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(body)
    lonely_doc = build(root=root, outdir=tempfile.mkdtemp(prefix="e331_fx_lo_"),
                       files=[(lonely, body)])
    row = lonely_doc["rows"][0]
    check("L18 a pointer that is neither loaded nor written is a reference, not a reader",
          row["class"] == K_REFERENCE and not row.get("handling"),
          str((row["class"], row.get("handling"))))
    os.remove(lonely)

    # L19: the corpus helper's docstring rule hides a tail, and that bound is published
    blind_body = ('"""A study.\n'
                  'More prose.\n'
                  '"""\n'
                  'PATH = "results/state_tilt/LLL_latest.json"\n'
                  '"""a stray opener that never closes\n'
                  + ''.join('X%d = %d\n' % (i, i) for i in range(20)))
    blind_path = os.path.join(src, "blindtail.py")
    with io.open(blind_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(blind_body)
    blind_doc = build(root=root, outdir=tempfile.mkdtemp(prefix="e331_fx_bl_"),
                      files=[(blind_path, blind_body)])
    check("L19 a source whose tail the scanner cannot see is counted",
          blind_doc["summary"]["sources_whose_tail_the_scanner_cannot_see"] == 1
          and blind_doc["sources_with_an_invisible_tail"],
          str(blind_doc["summary"]["sources_whose_tail_the_scanner_cannot_see"]))
    os.remove(blind_path)

    check("L20 the frozen vocabulary is closed", set(VERDICTS) == {V_SILENT, V_EXPOSED, V_SAFE})
    check("L21 the limits state the population bound and the presence-only rule",
          all(k in doc["limits"] for k in ("static", "helper_scope", "presence_not_behaviour",
                                           "fixture_strings", "invisible_tail")))
    check("L22 two builds agree on summary and verdict",
          build(root=root, outdir=tempfile.mkdtemp(prefix="e331_fx_d_"), files=files)["summary"]
          == build(root=root, outdir=tempfile.mkdtemp(prefix="e331_fx_d2_"),
                   files=files)["summary"])

    callee = row_for("callee.py")
    check("L23 a None absorbed by the callee is not called a silent reader",
          callee is not None and callee["handling"] == H_CALLEE,
          str(callee and callee.get("handling")))

    # L24: a long but CLOSED docstring must not be counted as an invisible tail
    normal_body = ('"""A study.\n' + ''.join('prose %d\n' % i for i in range(30)) + '"""\n'
                   + 'X = 1\n' + ''.join('Y%d = %d\n' % (i, i) for i in range(5)))
    normal_path = os.path.join(src, "closeddoc.py")
    with io.open(normal_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(normal_body)
    normal_doc = build(root=root, outdir=tempfile.mkdtemp(prefix="e331_fx_cd_"),
                       files=[(normal_path, normal_body)])
    check("L24 a closed docstring is not an invisible tail",
          normal_doc["summary"]["sources_whose_tail_the_scanner_cannot_see"] == 0,
          str(normal_doc["sources_with_an_invisible_tail"]))
    os.remove(normal_path)

    bad = [c for c in checks if not c[1]]
    print("\n%d/%d passed" % (len(checks) - len(bad), len(checks)))
    return 0 if not bad else 1


# --------------------------------------------------------------------------------------- cli

def cmd_run():
    doc = build()
    s = doc["summary"]
    print("%s | %s" % (doc["verdict"], STUDY))
    print("sources %(sources_scanned)s / families reached only through a pointer "
          "%(families_referenced_only_through_a_pointer)s / pairs %(pairs)s" % s)
    print("pairs by class:", json.dumps(s["pairs_by_class"], ensure_ascii=False))
    print("pointer-only readers %(pointer_only_readers)s over %(distinct_families_read)s families"
          % s)
    print("handling:", json.dumps(s["handling_by_class"], ensure_ascii=False))
    print("disk today: pointer missing for %(pointer_files_missing_on_disk_today)s readers / "
          "stated cut not on disk for %(pointers_whose_stated_cut_is_not_on_disk_today)s / "
          "unresolvable families %(families_read_but_unresolvable_today)s" % s)
    for row in doc["rows"]:
        if row["class"] == K_READER:
            print("   - %-44s %-18s %-46s %s"
                  % (row["source"], row["family"], row.get("handling"),
                     row.get("load_text", "")[:48]))
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