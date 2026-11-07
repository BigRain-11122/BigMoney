"""E495 (r1527 bm-b) -- did the diagnostic become the publication?

E492 published 13 ``*_latest.json`` faces whose only visible composers are doctor harnesses,
and the natural reading of "no producer among the visible composers" is "a test wrote this
face".  This study prices that reading instead of repeating it.

Three arms per face, all static, no network, nothing mutated:

  A. harness discipline -- what the harness does with the name (write once / write twice so
     it can put the original back / restores inside a ``finally``);
  B. author -- does any source in the canonical scan write the name through a path that a
     *different* callee receives (``_write_json(join(OUTDIR, FACE_NAME), face)``)?  E491's
     composer scan looks at opener arguments, so a write that enters an opener as a
     parameter of a local helper is invisible to it;
  C. readers -- who opens the face, and what their block does with the payload (E499's
     prices: re-derive / pin / presence / existence / bytes / no field).

The verdict is computed by a gate from the summary counts, never written by hand.
"""

import ast
import hashlib
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e483_leg_debt as e483
import e491_latest_copier as e491
import e492_multi_composer_doctor as e492
import e499_helperprice as e499

ROOT = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(ROOT)
OUTDIR = os.path.join(ROOT, "results", "state_tilt")

FACE_NAME = "doctorpub_latest.json"
DATED_PREFIX = "DOCTORPUB"
DATE_STAMP = "2026-11-07"
CARD = "E495-WHEN-A-FACES-ONLY-VISIBLE-COMPOSERS-ARE-LEG-RUNNERS-DID-THE-DIAGNOSTIC-BECOME-THE-PUBLICATION"
STUDY = "E495_doctorpub"
PARENT_FACE = "latestdoctor_latest.json"          # E492

SELF_EXCLUDED = ("e495_", "run_e495", "_e495")

# --- axis A: what the harness leaves behind -------------------------------------------
A_RESTORES = "writes_twice_so_the_original_goes_back"
A_LEAVES = "writes_once_and_leaves_its_own_bytes_behind"
A_UNREADABLE = "the_composer_source_is_absent_or_does_not_parse"
RESTORE_VOCAB = (A_RESTORES, A_LEAVES, A_UNREADABLE)

# --- axis B: who writes the name ------------------------------------------------------
B_DIRECT = "a_source_opens_the_name_for_write_directly"
B_THROUGH_HELPER = "a_source_passes_the_name_into_a_local_helper_that_opens_for_write"
B_CONSTANT = ("a_source_names_the_file_with_a_module_constant_that_reaches_a_write_but_the_"
              "directory_half_of_the_composition_is_unresolvable")
B_OUTSIDE = "a_source_passes_the_name_to_a_function_this_scan_cannot_see"
B_COMPOSED = ("a_source_composes_the_name_into_a_path_and_carries_it_through_local_names_"
              "into_a_write_while_the_directory_half_is_unresolvable")
B_NONE = "no_source_in_the_scan_ever_names_the_file"
AUTHOR_VOCAB = (B_DIRECT, B_THROUGH_HELPER, B_CONSTANT, B_COMPOSED, B_OUTSIDE, B_NONE)

# --- axis C: who reads it --------------------------------------------------------------
C_ASSERTS = "a_reader_asserts_a_field_of_the_payload"
C_PRESENCE = "a_reader_only_requires_a_field_to_be_present"
C_EXISTS = "a_reader_only_requires_the_file_to_exist"
C_NO_FIELD = "a_reader_opens_the_payload_and_reads_no_field"
C_BYTES = "a_reader_compares_the_payload_with_a_copy_and_reads_no_field"
C_NONE = "nothing_in_the_scan_opens_the_file_for_read"
READER_VOCAB = (C_ASSERTS, C_PRESENCE, C_EXISTS, C_NO_FIELD, C_BYTES, C_NONE)

READER_PRICE_TO_READER_CLASS = {
    e483.D_REDERIVE: C_ASSERTS,
    e483.D_PIN: C_ASSERTS,
    e483.D_PRESENCE: C_PRESENCE,
    e483.D_EXISTS: C_EXISTS,
    e483.D_NO_FIELD: C_NO_FIELD,
    e483.D_BYTES: C_BYTES,
    e483.D_UNREADABLE: C_NONE,
}

# --- verdicts -------------------------------------------------------------------------
V_HARNESS = "a_harness_writes_a_no_producer_face_once_and_leaves_its_own_bytes_behind"
V_UNNAMED = ("a_no_producer_face_is_not_named_by_any_source_in_the_scan_while_every_harness_"
             "restores_the_original")
V_ARTIFACT = ("every_no_producer_face_is_written_by_a_source_other_than_the_harness_and_its_"
              "visible_composers_restore_the_original")
V_EMPTY = "no_face_has_harness_only_composers"
VERDICT_VOCAB = (V_HARNESS, V_UNNAMED, V_ARTIFACT, V_EMPTY)

OPENER_COPY_ATTRS = e492.COPY_ATTRS

# A path-composition primitive passing the basename is not an author: ``join`` only builds the
# string.  The first draft graded ``os.path.join(OUTDIR, "x_latest.json")`` as "passed to a
# function this scan cannot see", which made every direct writer look like an indirect one.
COMPOSE_ONLY = frozenset((
    "join", "Path", "PurePath", "str", "format", "abspath", "normpath", "expanduser",
    "fspath", "resolve", "absolute", "dirname", "basename", "with_suffix", "with_name",
    "as_posix", "lstrip", "rstrip", "strip", "encode", "decode",
))
C_COMPOSES = "composes_the_path_from_the_name"
C_COPIES = "copies_the_name_to_or_from_a_destination"


def _now():
    import datetime
    return datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()


def _load_json(path):
    with io.open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _sha16(path):
    h = hashlib.sha256()
    with io.open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def scan_sources(root=None):
    """E491's canonical scan, minus this study's own sources (E180/E207 family)."""
    root = root or ROOT
    out = []
    for rel, text in e491.scan_sources(root):
        base = os.path.basename(rel).lower()
        if base.startswith(SELF_EXCLUDED):
            continue
        out.append((rel, text))
    return out


# ------------------------------------------------------------------ call-site discovery
def _defs_at_module(tree):
    out = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out.setdefault(node.name, node)
    return out


def _param_names(func):
    args = func.args
    names = [a.arg for a in (args.posonlyargs or [])] + [a.arg for a in args.args]
    return names


def helper_opens_with(func, param, want):
    """Does this local helper open ``param`` in mode ``want``?

    ``want`` is 'write' or 'read'.  The helper may reach the opener with the parameter
    directly, or through one locally bound name (a ``p = os.path.join(base, param)`` line).
    """
    names_with_param = {param}
    for node in ast.walk(func):
        if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                and isinstance(node.targets[0], ast.Name):
            for sub in ast.walk(node.value):
                if isinstance(sub, ast.Name) and sub.id in names_with_param:
                    names_with_param.add(node.targets[0].id)
                    break
    for node in ast.walk(func):
        if not isinstance(node, ast.Call):
            continue
        mode = e492._mode_of_call(node)
        if mode != want:
            continue
        for arg in node.args:
            for sub in ast.walk(arg):
                if isinstance(sub, ast.Name) and sub.id in names_with_param:
                    return True
    return False


class SourceFacts(object):
    """Per-source cache: parsed tree, line index, module defs, call nodes."""

    def __init__(self, rel, text, root):
        self.rel = rel
        self.text = text
        self.root = root
        self.error = None
        self.tree = None
        self.folder = None
        self.index = None
        self.bom = text.startswith("\ufeff")
        if self.bom:
            # e429_two_hop_writer.py is UTF-8-with-BOM: ast.parse refuses U+FEFF with
            # "invalid non-printable character" and the source then looks like a file that
            # names nothing.  A leading BOM is an encoding artefact, not a syntax error.
            text = text[1:]
        try:
            self.tree, self.folder, self.index = e492._folder_for(rel, text, root)
        except SyntaxError as exc:
            self.error = "does_not_parse: %s" % exc
            return
        self.defs = _defs_at_module(self.tree)
        self.finally_ranges = self._finally_ranges()

    def _finally_ranges(self):
        out = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Try) and node.finalbody:
                start = getattr(node.finalbody[0], "lineno", 0)
                end = getattr(node.finalbody[-1], "end_lineno", start) or start
                out.append((start, end))
        return out

    def in_finally(self, line):
        return any(a <= line <= b for a, b in self.finally_ranges)

    def module_constants_equal_to(self, basename):
        """Module-level ``NAME = "<basename>"`` assignments (the literal that names a face)."""
        if self.tree is None:
            return []
        out = []
        for node in self.tree.body:
            if not isinstance(node, ast.Assign) or len(node.targets) != 1:
                continue
            target = node.targets[0]
            value = node.value
            if not isinstance(target, ast.Name):
                continue
            if isinstance(value, ast.Constant) and value.value == basename:
                out.append({"constant": target.id, "line": getattr(node, "lineno", 0)})
        return out

    def _pathish(self, node):
        """Expressions that can hold a path (a dict payload that quotes the name cannot)."""
        return isinstance(node, (ast.Constant, ast.JoinedStr, ast.Name, ast.Call,
                                 ast.Tuple, ast.List, ast.BinOp, ast.Attribute))

    def expr_mentions_the_name(self, expr, basename, line):
        """Does this path expression, or a call inside it, carry the basename?

        The outer composition often fails to fold (``join(OUTDIR, FACE_NAME)`` where OUTDIR is
        an alias of another module's constant) while the literal half folds perfectly.  Reading
        the *arguments* of a composition call is what makes ``f"FIXTUREWRITE-{day}"`` and
        ``join(OUTDIR, "x_latest.json")`` visible.  A dict payload that merely quotes the name
        is not a path, so it is excluded before folding (E207: a name in the text is not use).
        """
        if not self._pathish(expr):
            return False
        paths, _unfolded = self.fold(expr, line)
        if basename in [os.path.basename(p) for p in paths]:
            return True
        for sub in ast.walk(expr):
            if not isinstance(sub, ast.Call):
                continue
            for arg in sub.args:
                if not self._pathish(arg):
                    continue
                paths, _un = self.fold(arg, line)
                if basename in [os.path.basename(p) for p in paths]:
                    return True
        return False

    def carriers_into_a_write(self, basename):
        """Local names that carry the basename into a write-mode opener in this source.

        Seeded from path-shaped assignments and ``for`` targets whose expression mentions the
        name, then propagated two hops through further path-shaped assignments and loops.
        Returns ``(reached, carriers)``.
        """
        if self.tree is None or self.index is None:
            return False, []
        carrying = set()
        for node in ast.walk(self.tree):
            line = getattr(node, "lineno", 0)
            if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                    and isinstance(node.targets[0], ast.Name):
                if self.expr_mentions_the_name(node.value, basename, line):
                    carrying.add(node.targets[0].id)
            elif isinstance(node, ast.For):
                if self.expr_mentions_the_name(node.iter, basename, line):
                    if isinstance(node.target, ast.Name):
                        carrying.add(node.target.id)
                    elif isinstance(node.target, (ast.Tuple, ast.List)):
                        carrying.update(t.id for t in node.target.elts
                                        if isinstance(t, ast.Name))
        if not carrying:
            return False, []
        for _ in range(2):
            before = len(carrying)
            for node in ast.walk(self.tree):
                if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                        and isinstance(node.targets[0], ast.Name) \
                        and self._pathish(node.value):
                    if any(isinstance(sub, ast.Name) and sub.id in carrying
                           for sub in ast.walk(node.value)):
                        carrying.add(node.targets[0].id)
                elif isinstance(node, ast.For) and self._pathish(node.iter):
                    if any(isinstance(sub, ast.Name) and sub.id in carrying
                           for sub in ast.walk(node.iter)):
                        if isinstance(node.target, ast.Name):
                            carrying.add(node.target.id)
                        elif isinstance(node.target, (ast.Tuple, ast.List)):
                            carrying.update(t.id for t in node.target.elts
                                            if isinstance(t, ast.Name))
            if len(carrying) == before:
                break
        for node in self.index.calls:
            if not isinstance(node, ast.Call):
                continue
            if not any(isinstance(sub, ast.Name) and sub.id in carrying
                       for arg in node.args for sub in ast.walk(arg)):
                continue
            if e492._mode_of_call(node) == "write":
                return True, sorted(carrying)
            callee = (node.func.id if isinstance(node.func, ast.Name)
                      else (node.func.attr if isinstance(node.func, ast.Attribute) else None))
            func = self.defs.get(callee) if callee else None
            if func is None:
                continue
            names = _param_names(func)
            for pos, _arg in enumerate(node.args):
                if pos < len(names) and helper_opens_with(func, names[pos], "write"):
                    return True, sorted(carrying)
        return False, sorted(carrying)

    def names_carrying(self, constant):
        """Names that carry this constant inside one module, following local assignments.

        ``path = os.path.join(OUTDIR, FACE_NAME)`` then ``targets = [path, ...]`` then
        ``for target in targets`` then ``open(target, 'w')``: the constant reaches the opener
        through three locally bound names, so a one-hop check reports "the constant reaches no
        write" for a producer that plainly writes the face.  The propagation is inside one
        module only, so it cannot invent a writer.
        """
        if self.tree is None:
            return set()
        carrying = set([constant])
        for _ in range(6):
            before = len(carrying)
            for node in ast.walk(self.tree):
                if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                        and isinstance(node.targets[0], ast.Name):
                    if any(isinstance(sub, ast.Name) and sub.id in carrying
                           for sub in ast.walk(node.value)):
                        carrying.add(node.targets[0].id)
                elif isinstance(node, ast.For):
                    if any(isinstance(sub, ast.Name) and sub.id in carrying
                           for sub in ast.walk(node.iter)):
                        targets = []
                        if isinstance(node.target, ast.Name):
                            targets = [node.target.id]
                        elif isinstance(node.target, (ast.Tuple, ast.List)):
                            targets = [t.id for t in node.target.elts
                                       if isinstance(t, ast.Name)]
                        carrying.update(targets)
            if len(carrying) == before:
                break
        return carrying

    def constant_reaches_a_write(self, constant):
        """Is this constant carried into a write-mode opener, directly or via local names?"""
        if self.index is None:
            return False
        carrying = self.names_carrying(constant)
        for node in self.index.calls:
            if not isinstance(node, ast.Call):
                continue
            if not any(isinstance(sub, ast.Name) and sub.id in carrying
                       for arg in node.args for sub in ast.walk(arg)):
                continue
            if e492._mode_of_call(node) == "write":
                return True
            callee = (node.func.id if isinstance(node.func, ast.Name)
                      else (node.func.attr if isinstance(node.func, ast.Attribute) else None))
            func = self.defs.get(callee) if callee else None
            if func is None:
                continue
            names = _param_names(func)
            for pos, _arg in enumerate(node.args):
                if pos < len(names) and helper_opens_with(func, names[pos], "write"):
                    return True
        return False

    def fold(self, arg, line):
        if self.index is None:
            return [], True
        names = self.index.names_at(line)
        paths, unfolded = self.folder.fold(arg, names, 0)
        return [p for p in (e491._clean(x) for x in paths) if p], unfolded

    def sites_naming(self, basename):
        """Every call in this source with an argument that folds to ``basename``.

        Unlike E492's ``named_sites`` this keeps *all* calls, not only openers, because a
        write that reaches an opener through a helper parameter is exactly what E491's
        composer scan cannot see.
        """
        out = []
        if self.index is None:
            return out
        for node in self.index.calls:
            if not isinstance(node, ast.Call):
                continue
            line = getattr(node, "lineno", 0)
            mode = e492._mode_of_call(node)
            callee = (node.func.id if isinstance(node.func, ast.Name)
                      else (node.func.attr if isinstance(node.func, ast.Attribute) else None))
            copies = bool(isinstance(node.func, ast.Attribute)
                          and node.func.attr in OPENER_COPY_ATTRS)
            for pos, arg in enumerate(node.args):
                paths, unfolded = self.fold(arg, line)
                if basename not in [os.path.basename(p) for p in paths]:
                    continue
                out.append({"line": line, "callee": callee, "arg_position": pos,
                            "mode": ("copy" if copies else mode),
                            "paths": paths[:e491.MAX_PATHS],
                            "unfolded": bool(unfolded)})
        # a keyword argument can carry the composed path too (``write_json(path=..., face=...)``)
        for node in self.index.calls:
            if not isinstance(node, ast.Call):
                continue
            line = getattr(node, "lineno", 0)
            mode = e492._mode_of_call(node)
            callee = (node.func.id if isinstance(node.func, ast.Name)
                      else (node.func.attr if isinstance(node.func, ast.Attribute) else None))
            copies = bool(isinstance(node.func, ast.Attribute)
                          and node.func.attr in OPENER_COPY_ATTRS)
            for kw in node.keywords or []:
                paths, unfolded = self.fold(kw.value, line)
                if basename not in [os.path.basename(p) for p in paths]:
                    continue
                out.append({"line": line, "callee": callee, "arg_position": None,
                            "keyword": kw.arg, "mode": ("copy" if copies else mode),
                            "paths": paths[:e491.MAX_PATHS],
                            "unfolded": bool(unfolded)})
        out.sort(key=lambda s: (s["line"], str(s["callee"]), str(s["arg_position"])))
        return out

    def classify(self, site, basename):
        """Grade one call site by what it does with the name."""
        mode = site["mode"]
        if mode == "copy":
            return C_COPIES
        if mode in ("write", "read"):
            return ("a_source_opens_the_name_for_write_directly" if mode == "write"
                    else "a_source_opens_the_name_for_read_directly")
        callee = site["callee"]
        if callee in COMPOSE_ONLY:
            return C_COMPOSES
        func = self.defs.get(callee) if callee else None
        if func is None:
            return B_OUTSIDE
        param = None
        names = _param_names(func)
        if site.get("arg_position") is not None and site["arg_position"] < len(names):
            param = names[site["arg_position"]]
        elif site.get("keyword") in names:
            param = site["keyword"]
        if param is None:
            return "passes_the_name_to_a_local_helper_that_never_takes_it"
        if helper_opens_with(func, param, "write"):
            return B_THROUGH_HELPER
        if helper_opens_with(func, param, "read"):
            return "a_source_passes_the_name_into_a_local_helper_that_opens_for_read"
        return "passes_the_name_to_a_local_helper_that_never_opens_it"


# --------------------------------------------------------------------------- population
def _payload_self_report(path):
    if not os.path.exists(path):
        return {"exists": False}
    try:
        d = _load_json(path)
    except (OSError, ValueError, UnicodeError) as exc:
        return {"exists": True, "parses": False, "error": str(exc)[:120]}
    out = {"exists": True, "parses": True, "bytes": os.path.getsize(path),
           "sha16": _sha16(path), "keys": sorted(d.keys()) if isinstance(d, dict) else []}
    if isinstance(d, dict):
        for key in ("study", "card", "generated", "evidence_cutoff", "verdict"):
            if key in d:
                out[key] = d[key] if not isinstance(d[key], str) else d[key][:200]
    return out


def measure_face(row, sources, root):
    """Three arms for one harness-only face."""
    name = row["latest_basename"]
    harness = []
    for cand in row.get("composers") or []:
        src = cand["source"]
        text = sources.get(src)
        if text is None:
            harness.append({"source": src, "role": e492.role_of(src),
                            "discipline": A_UNREADABLE})
            continue
        facts = SourceFacts(src, text, root)
        if facts.error:
            harness.append({"source": src, "role": e492.role_of(src),
                            "discipline": A_UNREADABLE, "error": facts.error})
            continue
        sites = facts.sites_naming(name)
        writes = sorted({s["line"] for s in sites if s["mode"] == "write"})
        reads = sorted({s["line"] for s in sites if s["mode"] == "read"})
        restore_lines = [ln for ln in writes[1:] if ln not in writes[:1]]
        harness.append({
            "source": src,
            "role": e492.role_of(src),
            "write_lines": writes,
            "read_lines": reads,
            "reads_the_name_before_it_writes_it": bool(reads and writes and reads[0] < writes[0]),
            "restore_lines": restore_lines,
            "restore_happens_in_a_finally": bool(
                restore_lines and any(facts.in_finally(ln) for ln in restore_lines)),
            "discipline": A_RESTORES if len(writes) >= 2 else (
                A_LEAVES if writes else A_UNREADABLE),
        })

    authors = []
    readers = []
    compositions = []
    copies = []
    name_constants = []
    composed_writers = []
    for rel, text in sorted(sources.items()):
        facts = SourceFacts(rel, text, root)
        if facts.error:
            continue
        for holder in facts.module_constants_equal_to(name):
            role = e492.role_of(rel)
            reaches = facts.constant_reaches_a_write(holder["constant"]) if \
                role != e492.R_HARNESS else False
            name_constants.append({"source": rel, "line": holder["line"],
                                   "constant": holder["constant"], "role": role,
                                   "the_constant_reaches_a_write": reaches})
        composes_a_write, carriers = facts.carriers_into_a_write(name)
        if composes_a_write and e492.role_of(rel) != e492.R_HARNESS:
            composed_writers.append({"source": rel, "role": e492.role_of(rel),
                                     "carriers": carriers})
        for site in facts.sites_naming(name):
            klass = facts.classify(site, name)
            entry = {"source": rel, "line": site["line"], "callee": site["callee"],
                     "kind": klass, "role": e492.role_of(rel)}
            if klass == C_COMPOSES:
                compositions.append(entry)
            elif klass == C_COPIES:
                copies.append(entry)
            elif klass in (B_DIRECT, B_THROUGH_HELPER, B_OUTSIDE,
                           "passes_the_name_to_a_local_helper_that_never_opens_it",
                           "passes_the_name_to_a_local_helper_that_never_takes_it"):
                authors.append(entry)
            elif klass == "a_source_opens_the_name_for_read_directly":
                price = e499.price_site(rel, site["line"])
                readers.append(dict(entry, price=price.get("price"),
                                    reader_class=READER_PRICE_TO_READER_CLASS.get(
                                        price.get("price"), C_NO_FIELD)))
            elif klass == "a_source_passes_the_name_into_a_local_helper_that_opens_for_read":
                readers.append(dict(entry, price="through_a_helper_so_unpriced",
                                    reader_class=C_NO_FIELD))

    author_kinds = {}
    for a in authors:
        author_kinds[a["kind"]] = author_kinds.get(a["kind"], 0) + 1
    # A harness that opens the name for write is arm A's subject, not an author: e492 already
    # counts it as a composer, and grading it as a writer is what made 11 of 13 faces read
    # "opened for write directly" when the only writer was the harness restoring its own mutant.
    writers = [a for a in authors if a["role"] != e492.R_HARNESS]
    writer_kinds = {}
    for a in writers:
        writer_kinds[a["kind"]] = writer_kinds.get(a["kind"], 0) + 1
    constant_writers = [c for c in name_constants
                        if c["role"] != e492.R_HARNESS and c["the_constant_reaches_a_write"]]
    if B_DIRECT in writer_kinds:
        writer_class = B_DIRECT
    elif B_THROUGH_HELPER in writer_kinds:
        writer_class = B_THROUGH_HELPER
    elif constant_writers:
        writer_class = B_CONSTANT
    elif composed_writers:
        writer_class = B_COMPOSED
    elif writers:
        writer_class = B_OUTSIDE
    else:
        writer_class = B_NONE

    consumers = [r for r in readers if r["role"] != e492.R_HARNESS]
    harness_reads = [r for r in readers if r["role"] == e492.R_HARNESS]
    reader_classes = {}
    for r in consumers:
        reader_classes[r["reader_class"]] = reader_classes.get(r["reader_class"], 0) + 1
    if C_ASSERTS in reader_classes:
        reader_class = C_ASSERTS
    elif C_PRESENCE in reader_classes:
        reader_class = C_PRESENCE
    elif consumers and (C_BYTES in reader_classes or C_NO_FIELD in reader_classes):
        reader_class = C_NO_FIELD
    elif consumers:
        reader_class = C_EXISTS
    else:
        reader_class = C_NONE

    published = row.get("published_path") or ("results/state_tilt/" + name)
    payload = _payload_self_report(os.path.join(root, published))

    return {
        "latest_basename": name,
        "published_path": published,
        "composer_sources": row.get("composer_sources") or [],
        "harness": harness,
        "harness_leaves_its_bytes_behind": any(h.get("discipline") == A_LEAVES
                                               for h in harness),
        "harness_restores_the_original": bool(harness) and all(
            h.get("discipline") == A_RESTORES for h in harness),
        "authors": authors,
        "author_kinds": author_kinds,
        "writers_other_than_the_harness": writers,
        "writer_kinds": writer_kinds,
        "name_constants": name_constants,
        "constant_writers_other_than_the_harness": constant_writers,
        "composed_writers_other_than_the_harness": composed_writers,
        "author_class": writer_class,
        "has_a_producer_module_writer": bool(
            [a for a in writers if a["kind"] in (B_DIRECT, B_THROUGH_HELPER)]) or bool(
            constant_writers) or bool(composed_writers),
        "path_composition_sites": compositions,
        "copy_sites": copies,
        "readers": consumers,
        "reader_classes": reader_classes,
        "reader_class": reader_class,
        "harness_read_sites": harness_reads,
        "payload": payload,
    }


def population(root=None):
    root = root or ROOT
    parent = _load_json(os.path.join(root, "results", "state_tilt", PARENT_FACE))
    rows_all = parent.get("rows") or []
    picked = [r for r in rows_all if not r.get("has_a_producer_composer")]
    sources = {rel: text for rel, text in scan_sources(root)}
    bom = [rel for rel, text in sources.items() if text.startswith("\ufeff")]
    unparsed = []
    for rel, text in sources.items():
        facts = SourceFacts(rel, text, root)
        if facts.error:
            unparsed.append({"source": rel, "error": facts.error[:120]})
    rows = [measure_face(r, sources, root) for r in sorted(picked,
                                                          key=lambda x: x["latest_basename"])]
    meta = {
        "sources_scanned": len(sources),
        "sources_that_start_with_a_bom": bom,
        "sources_that_do_not_parse": unparsed,
        "parent_face": PARENT_FACE,
        "parent_rows": len(rows_all),
        "population_definition": ("E492's rows whose has_a_producer_composer is false: the "
                                 "faces whose only visible composers are leg runners"),
        "sources_scanned": len(sources),
        "scan_directories": list(e491.SCAN_DIRS),
        "excluded_source_prefixes": list(e491.SELF_EXCLUDED) + list(SELF_EXCLUDED),
        "arm_a": "per-composer discipline re-derived from that source's own call sites",
        "arm_b": ("every call in every scanned source whose argument folds to the basename, "
                  "graded by whether the callee is an opener or a local helper that reaches "
                  "an opener with that parameter"),
        "arm_c": "each direct read site priced by e499.price_site (E483's debt vocabulary)",
        "live_arm": "each published path is opened, parsed and hashed at build time",
    }
    return rows, meta


# ---------------------------------------------------------------------------- summary
def summary_of(rows, meta):
    harness_rows = [h for r in rows for h in (r.get("harness") or [])]
    reader_sites = [s for r in rows for s in (r.get("readers") or [])]
    prices = {}
    for r in rows:
        for s in r.get("readers") or []:
            if s.get("price"):
                prices[s["price"]] = prices.get(s["price"], 0) + 1
    retirable_n, retirable_bytes = _summary_retirable(rows)
    unread = [r for r in rows
              if r.get("reader_class") == C_NONE
              and (r.get("has_a_producer_module_writer") or
                   r.get("constant_writers_other_than_the_harness") or
                   r.get("composed_writers_other_than_the_harness"))]
    unread_n = len(unread)
    unread_bytes = sum(int((r.get("payload") or {}).get("bytes") or 0) for r in unread)
    return {
        "no_producer_faces": len(rows),
        "harness_composer_sites": len(harness_rows),
        "harness_composers_that_leave_their_bytes_behind": sum(
            1 for h in harness_rows if h.get("discipline") == A_LEAVES),
        "harness_composers_that_restore": sum(
            1 for h in harness_rows if h.get("discipline") == A_RESTORES),
        "harness_restores_inside_a_finally": sum(
            1 for h in harness_rows if h.get("restore_happens_in_a_finally")),
        "faces_whose_harness_leaves_its_bytes_behind": sum(
            1 for r in rows if r.get("harness_leaves_its_bytes_behind")),
        "faces_whose_composers_all_restore": sum(
            1 for r in rows if r.get("harness_restores_the_original")),
        "faces_with_a_writer_other_than_the_harness": sum(
            1 for r in rows if r.get("has_a_producer_module_writer")),
        "faces_whose_only_other_writer_is_a_helper_parameter": sum(
            1 for r in rows if r.get("author_class") == B_THROUGH_HELPER),
        "faces_whose_other_writer_opens_them_directly": sum(
            1 for r in rows if r.get("author_class") == B_DIRECT),
        "faces_whose_writer_is_named_only_by_a_module_constant": sum(
            1 for r in rows if r.get("author_class") == B_CONSTANT),
        "faces_whose_writer_carries_the_name_through_local_names": sum(
            1 for r in rows if r.get("author_class") == B_COMPOSED),
        "module_name_constants_that_reach_a_write": sum(
            len([c for c in (r.get("constant_writers_other_than_the_harness") or [])])
            for r in rows),
        "faces_passed_to_a_function_outside_the_scan": sum(
            1 for r in rows if r.get("author_class") == B_OUTSIDE),
        "faces_no_source_other_than_the_harness_names": sum(
            1 for r in rows if r.get("author_class") == B_NONE),
        "path_composition_sites": sum(len(r.get("path_composition_sites") or []) for r in rows),
        "copy_sites": sum(len(r.get("copy_sites") or []) for r in rows),
        "consumer_read_sites": len(reader_sites),
        "harness_read_sites": sum(len(r.get("harness_read_sites") or []) for r in rows),
        "faces_with_no_consumer_reader": sum(
            1 for r in rows if r.get("reader_class") == C_NONE),
        "faces_whose_readers_assert_a_field": sum(
            1 for r in rows if r.get("reader_class") == C_ASSERTS),
        "faces_whose_readers_only_check_presence_or_existence": sum(
            1 for r in rows if r.get("reader_class") in (C_PRESENCE, C_EXISTS)),
        "reader_prices": prices,
        "payloads_that_parse": sum(1 for r in rows if (r.get("payload") or {}).get("parses")),
        "payloads_that_state_their_own_study": sum(
            1 for r in rows if (r.get("payload") or {}).get("study")),
        "faces_retirable_under_the_narrowest_rule": retirable_n,
        "bytes_retirable_under_the_narrowest_rule": retirable_bytes,
        "faces_written_but_read_by_no_consumer": unread_n,
        "bytes_written_but_read_by_no_consumer": unread_bytes,
    }


def _verdict(summary):
    if not summary.get("no_producer_faces"):
        return V_EMPTY
    if summary.get("faces_whose_harness_leaves_its_bytes_behind"):
        return V_HARNESS
    if summary.get("faces_no_source_other_than_the_harness_names"):
        return V_UNNAMED
    return V_ARTIFACT


def card_answer(rows, summary):
    if not rows:
        return "no face in E492's population is composed only by harnesses"
    through = [r["latest_basename"] for r in rows if r["author_class"] == B_THROUGH_HELPER]
    return ("%d faces have no producer among their visible composers. No harness leaves its "
            "bytes behind: %d of %d composer sites write the name twice so the original goes "
            "back (%d of those inside a finally). Counting only sources other than the harness, "
            "%d faces are written through a helper that receives the composed path, %d are "
            "named by a module constant that reaches a write while the directory half of its "
            "composition cannot be resolved, %d carry the name through local names into a write, "
            "%d are opened for write directly, %d are passed to a function this scan cannot see "
            "and %d are named by nothing. On the consumer side, "
            "%d faces have a reader that is not the harness (%d states no reader at all) and %d "
            "of those readers assert a field. Retirable under the narrowest rule (no writer, no "
            "reader, no name constant): %d faces / %d bytes; written by a producer yet read by "
            "no consumer: %d faces / %d bytes. The helper-parameter class: %s"
            % (summary["no_producer_faces"], summary["harness_composers_that_restore"],
               summary["harness_composer_sites"], summary["harness_restores_inside_a_finally"],
               summary["faces_whose_only_other_writer_is_a_helper_parameter"],
               summary["faces_whose_writer_is_named_only_by_a_module_constant"],
               summary["faces_whose_writer_carries_the_name_through_local_names"],
               summary["faces_whose_other_writer_opens_them_directly"],
               summary["faces_passed_to_a_function_outside_the_scan"],
               summary["faces_no_source_other_than_the_harness_names"],
               summary["no_producer_faces"] - summary["faces_with_no_consumer_reader"],
               summary["faces_with_no_consumer_reader"],
               summary["faces_whose_readers_assert_a_field"],
               summary["faces_retirable_under_the_narrowest_rule"],
               summary["bytes_retirable_under_the_narrowest_rule"],
               summary["faces_written_but_read_by_no_consumer"],
               summary["bytes_written_but_read_by_no_consumer"],
               ", ".join(through[:3]) or "none"))


def _retirable(row):
    return (row.get("author_class") == B_NONE
            and row.get("reader_class") == C_NONE
            and not (row.get("constant_writers_other_than_the_harness") or [])
            and not (row.get("composed_writers_other_than_the_harness") or []))


def _summary_retirable(rows):
    picked = [r for r in rows if _retirable(r)]
    return (len(picked),
            sum(int((r.get("payload") or {}).get("bytes") or 0) for r in picked))


# ------------------------------------------------------------------------------- build
def build(root=None, write=True):
    root = root or ROOT
    rows, meta = population(root)
    summary = summary_of(rows, meta)
    face = {
        "card": CARD,
        "study": STUDY,
        "title": ("for every face whose only visible composer is a leg runner: what the "
                  "harness does with the name, who else writes it, and who reads it"),
        "evidence_cutoff": DATE_STAMP,
        "generated": _now(),
        "population_source": {"face": PARENT_FACE,
                              "rule": "has_a_producer_composer == false"},
        "sources": {"scanned": meta.get("sources_scanned"),
                    "start_with_a_bom": meta.get("sources_that_start_with_a_bom"),
                    "do_not_parse": meta.get("sources_that_do_not_parse"),
                    "note": ("a leading UTF-8 BOM is stripped before parsing; without that, "
                             "e429_two_hop_writer.py reads as a source that names nothing "
                             "because ast.parse refuses U+FEFF")},
        "restore_vocab": list(RESTORE_VOCAB),
        "author_vocab": list(AUTHOR_VOCAB),
        "reader_vocab": list(READER_VOCAB),
        "verdict_vocab": list(VERDICT_VOCAB),
        "summary": summary,
        "verdict": _verdict(summary),
        "card_answer": card_answer(rows, summary),
        "rows": rows,
        "method_limits": [
            "author attribution follows direct call sites and one local helper hop; a path "
            "composed inside a helper from a module constant and never passed in is still "
            "invisible, so B_NONE means 'no source names it', not 'no source writes it'",
            "a reader that goes through a helper is counted as a reader but its block is not "
            "priced (e499.price_site needs an opener on the line)",
            "role grading reuses E492's basename regexes; a harness named outside that "
            "vocabulary would be graded as a producer",
            "the population is E492's published row set, not a fresh composer scan, so a "
            "source added after E492 does not enter this population",
        ],
    }
    if write:
        _write(face, root)
    return face


def _write(face, root=None):
    root = root or ROOT
    outdir = os.path.join(root, "results", "state_tilt")
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    payload = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
    for name in ("%s-%s.json" % (DATED_PREFIX, DATE_STAMP), FACE_NAME):
        path = os.path.join(outdir, name)
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(payload + "\n")


# ----------------------------------------------------------------------------- gates
def row_problems(face):
    problems = []
    rows = face.get("rows") or []
    if face.get("verdict") not in VERDICT_VOCAB:
        problems.append("the verdict is outside the frozen vocabulary")
    for r in rows:
        name = r.get("latest_basename")
        if not name:
            problems.append("a row has no basename")
            continue
        harness = r.get("harness") or []
        if harness and all(h.get("discipline") == A_RESTORES for h in harness):
            if not r.get("harness_restores_the_original"):
                problems.append("%s: every harness restores but the row says otherwise" % name)
        if any(h.get("discipline") == A_LEAVES for h in harness):
            if not r.get("harness_leaves_its_bytes_behind"):
                problems.append("%s: a harness leaves its bytes but the row hides it" % name)
        klass = r.get("author_class")
        if klass not in AUTHOR_VOCAB:
            problems.append("%s: author_class outside the vocabulary" % name)
        if klass == B_THROUGH_HELPER and B_THROUGH_HELPER not in (r.get("author_kinds") or {}):
            problems.append("%s: author_class promises a helper that author_kinds lacks" % name)
        if klass == B_NONE and (r.get("writers_other_than_the_harness") or []):
            problems.append("%s: B_NONE but non-harness writers are listed" % name)
        if klass == B_CONSTANT and not (r.get("constant_writers_other_than_the_harness") or []):
            problems.append("%s: B_CONSTANT but no constant writer is listed" % name)
        if klass == B_NONE and (r.get("constant_writers_other_than_the_harness") or []):
            problems.append("%s: B_NONE but a name constant reaches a write" % name)
        if klass == B_NONE and (r.get("composed_writers_other_than_the_harness") or []):
            problems.append("%s: B_NONE but a source carries the name into a write" % name)
        if klass == B_COMPOSED and not (r.get("composed_writers_other_than_the_harness") or []):
            problems.append("%s: B_COMPOSED without a carrier source" % name)
        rk = r.get("reader_class")
        if rk not in READER_VOCAB:
            problems.append("%s: reader_class outside the vocabulary" % name)
        if rk == C_NONE and (r.get("readers") or []):
            problems.append("%s: C_NONE but readers are listed" % name)
        payload = r.get("payload") or {}
        if payload.get("exists") and not payload.get("sha16"):
            problems.append("%s: the payload is on disk but no hash was published" % name)
    # the summary must re-derive from the rows, never be carried
    rederived = summary_of(rows, {})
    for key, value in (face.get("summary") or {}).items():
        if key == "reader_prices":
            continue
        if rederived.get(key) != value:
            problems.append("summary.%s does not re-derive from the rows (%r vs %r)"
                            % (key, value, rederived.get(key)))
    if _verdict(face.get("summary") or {}) != face.get("verdict"):
        problems.append("the verdict does not re-derive from the summary")
    return problems


def check(face=None, root=None):
    root = root or ROOT
    face = face or _load_json(os.path.join(root, "results", "state_tilt", FACE_NAME))
    problems = row_problems(face)
    print(json.dumps({"face": FACE_NAME, "rows": len(face.get("rows") or []),
                      "verdict": face.get("verdict"),
                      "problems": problems}, ensure_ascii=False, indent=1))
    return 0 if not problems else 1


def _strip(face):
    out = dict(face)
    out.pop("generated", None)
    return out


def verify(root=None):
    root = root or ROOT
    disk = _load_json(os.path.join(root, "results", "state_tilt", FACE_NAME))
    live = build(root, write=False)
    problems = []
    if _strip(disk) != _strip(live):
        problems.append("the published face does not re-derive from the live tree")
        d_rows = {r["latest_basename"]: r for r in disk.get("rows") or []}
        l_rows = {r["latest_basename"]: r for r in live.get("rows") or []}
        for name in sorted(set(d_rows) | set(l_rows)):
            if d_rows.get(name) != l_rows.get(name):
                problems.append("row differs: %s" % name)
    print(json.dumps({"verify": "rebuild", "problems": problems[:20],
                      "problem_count": len(problems)}, ensure_ascii=False, indent=1))
    return 0 if not problems else 1


# --------------------------------------------------------------------------- selftest
FIXTURE_DEP_WRITER = '''import io, json, os
OUTDIR = os.path.join("results", "state_tilt")
FACE_NAME = "alpha_latest.json"
def _write_json(path, payload):
    with io.open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh)
def main():
    face = {"study": "E900_alpha"}
    _write_json(os.path.join(OUTDIR, FACE_NAME), face)
'''

FIXTURE_DIRECT_WRITER = '''import io, json, os
OUTDIR = os.path.join("results", "state_tilt")
def main():
    with io.open(os.path.join(OUTDIR, "beta_latest.json"), "w", encoding="utf-8") as fh:
        json.dump({"study": "E901_beta"}, fh)
'''

FIXTURE_RESTORING_HARNESS = '''import io, json, os
P = os.path.join("results", "state_tilt", "alpha_latest.json")
def main():
    original = io.open(P, encoding="utf-8").read()
    with io.open(P, "w", encoding="utf-8") as fh:
        fh.write("{}")
    try:
        pass
    finally:
        with io.open(P, "w", encoding="utf-8") as fh:
            fh.write(original)
'''

FIXTURE_LEAVING_HARNESS = '''import io, json, os
P = os.path.join("results", "state_tilt", "gamma_latest.json")
def main():
    with io.open(P, "w", encoding="utf-8") as fh:
        fh.write("{}")
'''

FIXTURE_READER = '''import io, json, os
P = os.path.join("results", "state_tilt", "alpha_latest.json")
def main():
    d = json.load(io.open(P, encoding="utf-8"))
    assert d["study"].startswith("E900")
'''


def _fixture_tree():
    base = os.path.join(ROOT, "results", "_e500_fixture")
    if os.path.isdir(base):
        import shutil
        shutil.rmtree(base)
    os.makedirs(os.path.join(base, "scripts"))
    os.makedirs(os.path.join(base, "results", "state_tilt"))
    files = {
        "scripts/e900_alpha.py": FIXTURE_DEP_WRITER,
        "scripts/e901_beta.py": FIXTURE_DIRECT_WRITER,
        "scripts/run_e900_smoke_leg.py": FIXTURE_RESTORING_HARNESS,
        "scripts/run_e901_smoke_leg.py": FIXTURE_LEAVING_HARNESS,
        "scripts/check_alpha.py": FIXTURE_READER,
    }
    for rel, text in files.items():
        path = os.path.join(base, rel.replace("/", os.sep))
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
    payload = {"study": "E900_alpha", "rows": [], "verdict": "x"}
    with io.open(os.path.join(base, "results", "state_tilt", "alpha_latest.json"),
                 "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh)
    return base


def selftest():
    legs = []

    def leg(name, fn):
        try:
            ok, note = fn()
        except Exception as exc:                       # noqa: BLE001 - selftest reports
            ok, note = False, "raised %s: %s" % (type(exc).__name__, exc)
        legs.append((name, ok, note))

    base = _fixture_tree()
    facts_w = SourceFacts("scripts/e900_alpha.py", FIXTURE_DEP_WRITER, base)
    facts_h = SourceFacts("scripts/run_e900_smoke_leg.py", FIXTURE_RESTORING_HARNESS, base)
    facts_l = SourceFacts("scripts/run_e901_smoke_leg.py", FIXTURE_LEAVING_HARNESS, base)
    facts_r = SourceFacts("scripts/check_alpha.py", FIXTURE_READER, base)

    def leg_helper_write_seen():
        sites = facts_w.sites_naming("alpha_latest.json")
        kinds = [facts_w.classify(s, "alpha_latest.json") for s in sites]
        return (B_THROUGH_HELPER in kinds,
                "alpha write sites %r -> %r" % ([s["line"] for s in sites], kinds))

    def leg_direct_write_seen():
        facts = SourceFacts("scripts/e901_beta.py", FIXTURE_DIRECT_WRITER, base)
        kinds = [facts.classify(s, "beta_latest.json")
                 for s in facts.sites_naming("beta_latest.json")]
        authors = [k for k in kinds if k != C_COMPOSES]
        return (authors == [B_DIRECT] and C_COMPOSES in kinds,
                "beta kinds %r" % (kinds,))

    def leg_restoring_harness():
        sites = facts_h.sites_naming("alpha_latest.json")
        writes = sorted({s["line"] for s in sites if s["mode"] == "write"})
        return (len(writes) >= 2 and facts_h.in_finally(writes[-1]),
                "writes %r in_finally %r" % (writes, [facts_h.in_finally(w) for w in writes]))

    def leg_leaving_harness():
        sites = facts_l.sites_naming("gamma_latest.json")
        writes = [s for s in sites if s["mode"] == "write"]
        return (len(writes) == 1, "gamma writes %r" % [s["line"] for s in writes])

    def leg_reader_priced():
        sites = facts_r.sites_naming("alpha_latest.json")
        reads = [s for s in sites if s["mode"] == "read"]
        return (bool(reads), "alpha read lines %r" % [s["line"] for s in reads])

    def leg_verdict_harness_first():
        return (_verdict({"no_producer_faces": 1,
                          "faces_whose_harness_leaves_its_bytes_behind": 1,
                          "faces_with_no_consumer_reader": 1}) == V_HARNESS,
                "harness arm wins over the orphan arm")

    def leg_verdict_orphan():
        return (_verdict({"no_producer_faces": 1,
                          "faces_whose_harness_leaves_its_bytes_behind": 0,
                          "faces_with_no_consumer_reader": 0,
                          "faces_no_source_other_than_the_harness_names": 1}) == V_UNNAMED,
                "an unnamed face reads as unnamed")

    def leg_verdict_artifact():
        return (_verdict({"no_producer_faces": 2,
                          "faces_whose_harness_leaves_its_bytes_behind": 0,
                          "faces_with_no_consumer_reader": 0,
                          "faces_no_source_other_than_the_harness_names": 0}) == V_ARTIFACT,
                "restore + writer reads as the scan artifact")

    def leg_verdict_empty():
        return (_verdict({"no_producer_faces": 0}) == V_EMPTY, "empty population has a word")

    def leg_summary_rederives():
        rows = [{"latest_basename": "a", "harness": [{"discipline": A_RESTORES}],
                 "harness_restores_the_original": True,
                 "harness_leaves_its_bytes_behind": False,
                 "authors": [], "author_kinds": {}, "author_class": B_NONE,
                 "has_a_producer_module_writer": False,
                 "readers": [], "reader_classes": {}, "reader_class": C_NONE,
                 "payload": {"exists": True, "parses": True, "bytes": 10, "sha16": "x",
                             "study": "E1"}}]
        s = summary_of(rows, {})
        return (s["faces_retirable_under_the_narrowest_rule"] == 1
                and s["bytes_retirable_under_the_narrowest_rule"] == 10,
                "retirable %r bytes %r" % (s["faces_retirable_under_the_narrowest_rule"],
                                           s["bytes_retirable_under_the_narrowest_rule"]))

    def leg_row_gate_catches_a_lie():
        rows = [{"latest_basename": "a", "harness": [{"discipline": A_LEAVES}],
                 "harness_leaves_its_bytes_behind": False,
                 "harness_restores_the_original": False,
                 "authors": [], "author_kinds": {}, "author_class": B_NONE,
                 "has_a_producer_module_writer": False,
                 "readers": [], "reader_classes": {}, "reader_class": C_NONE,
                 "payload": {"exists": False}}]
        face = {"rows": rows, "summary": summary_of(rows, {}),
                "verdict": _verdict(summary_of(rows, {})), "verdict_vocab": list(VERDICT_VOCAB)}
        problems = row_problems(face)
        return (any("hides it" in p for p in problems),
                "problems %r" % (problems,))

    def leg_row_gate_catches_a_carried_summary():
        rows = [{"latest_basename": "a", "harness": [], "authors": [], "author_kinds": {},
                 "author_class": B_NONE, "has_a_producer_module_writer": False,
                 "readers": [], "reader_classes": {}, "reader_class": C_NONE,
                 "payload": {"exists": False}}]
        face = {"rows": rows, "summary": {"no_producer_faces": 99},
                "verdict": V_EMPTY, "verdict_vocab": list(VERDICT_VOCAB)}
        problems = row_problems(face)
        return (any("does not re-derive" in p for p in problems), "problems %r" % (problems,))

    def leg_self_excluded():
        names = [os.path.basename(rel).lower() for rel, _ in scan_sources(ROOT)]
        return (not any(n.startswith(SELF_EXCLUDED) for n in names),
                "sources %d, none of them this study" % len(names))

    leg("helper-parameter write is visible", leg_helper_write_seen)
    leg("direct write is graded direct", leg_direct_write_seen)
    leg("restoring harness is seen and located in finally", leg_restoring_harness)
    leg("leaving harness is seen as one write", leg_leaving_harness)
    leg("reader site is found", leg_reader_priced)
    leg("verdict: harness arm outranks the orphan arm", leg_verdict_harness_first)
    leg("verdict: an unnamed face is orphaned", leg_verdict_orphan)
    leg("verdict: restore plus writer is the artifact", leg_verdict_artifact)
    leg("verdict: empty population", leg_verdict_empty)
    leg("summary re-derives the retirement price", leg_summary_rederives)
    leg("row gate catches a hidden harness write", leg_row_gate_catches_a_lie)
    leg("row gate catches a carried summary", leg_row_gate_catches_a_carried_summary)
    leg("the scan excludes this study", leg_self_excluded)

    passed = sum(1 for _, ok, _ in legs if ok)
    for name, ok, note in legs:
        print("%s %s -- %s" % ("PASS" if ok else "FAIL", name, note))
    print("%d/%d" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "run"
    if cmd == "run":
        face = build()
        print(json.dumps({"face": FACE_NAME, "rows": len(face["rows"]),
                          "verdict": face["verdict"],
                          "summary": face["summary"]}, ensure_ascii=False, indent=1))
        return 0
    if cmd == "check":
        return check()
    if cmd == "verify":
        return verify()
    if cmd == "selftest":
        return selftest()
    print("usage: e495_doctorpub.py [run|check|verify|selftest]", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())