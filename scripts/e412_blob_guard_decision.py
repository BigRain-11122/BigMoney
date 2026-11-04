"""E412 -- which leg should have failed when a blob reader's face moved?

E406 (r1430) published the population: 307 attributed git-object read sites over 126 modules,
58 face names a blob reader can name, 25 of them present both at HEAD and on disk, 5 differing
at the moment of the census, and 1 module out of 126 ever comparing the two arms. That bill
measured the gap. It did not answer the next question, and neither did any leg:

    when the file beside the blob has moved, what should have gone red?

This card is a decision, not another census. For each of the 25 measured faces it asks two
mechanical questions and lets the answers pick one of three guards:

  1. WHO READS IT, AND AT WHICH VINTAGE. Every site that names the face is classified by the
     revision its call passes: an explicit commit/sha/pin (the face's committed vintage is the
     point -- E368/E369 seam replays), or HEAD-at-call-time (the reader believes it is reading
     the current face), or an argument carrying neither token (unresolved: the helper may
     resolve HEAD inside itself, so it is not evidence of pinning). Sites inside the face's own
     writer are separated out -- a producer reading its own output is not a consumer.

  2. CAN THE FACE BE RE-DERIVED CHEAPLY? A writer module that names the face and dumps JSON,
     with no network marker, can be re-run by a leg (E387's shape: re-derive, then compare).
     A writer that needs a source or a session cannot, and the only honest guard is a refusal.

The choice per face:

  a  a leg re-derives the face and compares it to the published one   (net-free writer on hand)
  b  a leg refuses a HEAD blob read whose face file is newer than HEAD (no net-free writer)
  c  nothing                                                          (every consumer pins a
                                                                       commit, or the only reader
                                                                       is the producer itself)

The bill is the decision table with the evidence that decided each row and the count of sites
each choice covers. Nothing here edits a reader or a leg: the repair is a separate card, and a
study that rewrote the thing it measures would be measuring itself.

Subcommands: run | verify | selftest
"""
from __future__ import annotations

import ast
import io
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "results", "state_tilt")
SOURCE_FACE = os.path.join(OUT_DIR, "blobread_latest.json")
DELIVERY = os.path.join(OUT_DIR, "BLOBGUARD-2026-11-05.json")
LATEST = os.path.join(OUT_DIR, "blobguard_latest.json")
STUDY = "E412_blob_guard_decision"
CARD = "E412-WHICH-LEG-SHOULD-FAIL-WHEN-A-BLOB-READERS-FACE-MOVED"

CHOICES = {
    "a": "a suite leg re-derives the face and compares it to the published one (E387 shape)",
    "b": "a leg refuses a HEAD blob read whose face file is newer than HEAD",
    "c": "nothing -- no consumer can be blinded (every consumer pins a commit, or the only "
         "reader is the face's own producer)",
}

WHY = {
    "re_derivable_writer_on_hand": "a net-free in-repo writer names the face, so a leg can "
                                  "re-derive it and compare",
    "no_net_free_writer": "a consumer reads HEAD and no net-free writer exists, so the only "
                          "guard that costs nothing is a refusal",
    "every_reader_pins_a_commit": "every consumer passes an explicit commit, so the committed "
                                  "vintage is the intent",
    "only_its_own_writer_reads_it": "the only module that names the face is the module that "
                                    "writes it -- a producer reading its own output",
    "read_only_by_round_scoped_tools": "only a round-scoped tool reads it, and such a tool runs "
                                       "once by name -- it cannot be blinded by a later write",
    "no_call_carries_the_face": "no call passes this face to a git reader -- the module names it "
                                "in a constant, a comparison or a docstring, so the read E406 "
                                "attributed is not visible at any call site",
}

VERDICTS = (
    "no_consumer_can_be_blinded_so_no_guard_is_owed",
    "a_write_that_head_has_not_seen_moves_a_face_out_from_under_a_reader_and_no_leg_opens_it",
    "a_leg_opens_the_mover_but_it_reads_the_file_and_never_the_blob",
    "a_mover_is_covered_by_a_leg_that_could_be_extended_to_the_blob_arm",
    "every_measured_face_was_attributed_by_a_module_literal_and_no_call_hands_it_to_a_git_"
    "reader_so_the_gap_describes_no_consumer",
)

# A call that passes one of these tokens is naming a commit, not "whatever HEAD is now".
PIN_RE = re.compile(
    r"\b(commit|commits|sha|shas|sha_a|sha_b|pin|pinned|PIN_SHA|BASE|base_commit|parent|"
    r"target|vintage|replay|OURS_COMMIT|THEIRS_COMMIT|rev_)\b")
# A call that passes HEAD -- literal, or a helper whose whole job is to resolve it now.
HEAD_RE = re.compile(r"\bHEAD\b|\bhead_commit\s*\(|\bhead_sha\s*\(|\bhead_rev\s*\(|"
                     r"\bhead\b|origin/main|rev\s+or\b")
NET_RE = re.compile(r"requests\.|urllib|akshare|https?://|sina|eastmoney|tushare", re.I)
CHECK_NAMES = ("asks_the_clock", "dates_the_face_in_a_gate")


def say(message):
    sys.stdout.write(str(message) + "\n")
    sys.stdout.flush()


def git(args, binary=False):
    try:
        out = subprocess.run(["git"] + args, cwd=ROOT, capture_output=True, check=False)
        if out.returncode != 0:
            return None
        return out.stdout if binary else out.stdout.decode("utf-8", "replace")
    except Exception:  # noqa: BLE001
        return None


def head_rev():
    return (git(["rev-parse", "HEAD"]) or "").strip()


def _lines(rel):
    try:
        with io.open(os.path.join(ROOT, rel), encoding="utf-8", errors="replace") as fh:
            return fh.read().splitlines()
    except Exception:  # noqa: BLE001
        return []


def _leg_name_before(lines, lo):
    """The `_nameNNN = (...)` literal the suite prints for the leg starting at `lo`."""
    for i in range(lo - 2, max(-1, lo - 40), -1):
        m = re.match(r"^\s*_name\d+\s*=\s*(.*)$", lines[i])
        if not m:
            continue
        buf = [m.group(1)]
        j = i
        while j + 1 < len(lines) and "\n".join(buf).count("(") > "\n".join(buf).count(")"):
            j += 1
            buf.append(lines[j])
        text = "\n".join(buf)
        parts = re.findall(r'"([^"]*)"', text) or re.findall(r"'([^']*)'", text)
        if parts:
            return " ".join(parts)
    return None


def suite_legs():
    """Every `try:` block in smoke_test.py that reports through check(), with its own name.

    Named from the `_nameNNN = (...)` literal the suite prints -- not from a line number, which
    E409 lost three readers to.
    """
    rel = "smoke_test.py"
    lines = _lines(rel)
    if not lines:
        return []
    try:
        tree = ast.parse("\n".join(lines))
    except SyntaxError:
        return []
    legs = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Try):
            continue
        lo, hi = node.lineno, node.end_lineno
        if not (0 < lo <= hi <= len(lines)):
            continue
        # The suite reports a leg with `check(...)` *after* the try/except pair, and names it
        # with the `_nameNNN` assignment *before* it, so both sit outside the node's own span.
        text = "\n".join(lines[lo - 1:min(len(lines), hi + 6)])
        if "check(" not in text:
            continue
        name = _leg_name_before(lines, lo)
        legs.append({"leg": (name or "check@%d" % lo)[:120].replace("\n", " "),
                     "lo": lo, "hi": hi, "text": text})
    return legs


def _load_e409():
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    try:
        import e409_unfloored_faces as mod
        return mod
    except Exception:  # noqa: BLE001
        return None


def tier_of(leg, classifier):
    if classifier is None:
        return "unclassified"
    block = {"found": True, "lo": leg["lo"], "hi": leg["hi"],
             "lines": leg["text"].splitlines()}
    return classifier._classify(block).get("tier", "unclassified")


def _parse_cached(rel, cache):
    key = ("ast", rel)
    if key not in cache:
        try:
            cache[key] = ast.parse("\n".join(_lines(rel)))
        except SyntaxError:
            cache[key] = None
    return cache[key]


def read_sites(rel, base, callees, cache):
    """The call sites in this module that actually hand THIS face to a git-object reader.

    E406's reader rows are module-level: the module's whole face list is repeated on every site,
    so `e340:430 head_sha(root)` arrives carrying a face it never touches. A site is a site only
    if an argument carries the face -- as a literal, an alias, or a loop binding.
    """
    tree = _parse_cached(rel, cache)
    if tree is None:
        return []
    glob = _taint_names(list(ast.walk(tree)), base, {})
    scopes = [("module", list(ast.walk(tree)), glob)]
    for fn in ast.walk(tree):
        if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            scopes.append((fn.name, list(ast.walk(fn)), glob))
    out, seen = [], set()
    for scope, nodes, seed in scopes:
        tainted = _taint_names(nodes, base, seed)
        for node in nodes:
            if not isinstance(node, ast.Call):
                continue
            fname = getattr(node.func, "id", None) or getattr(node.func, "attr", None) or ""
            if fname not in callees:
                continue
            args = list(node.args) + [k.value for k in node.keywords]
            if not any(_mentions(a, base) or (_names(a) & set(tainted)) for a in args):
                continue
            if (node.lineno, fname) in seen:
                continue
            seen.add((node.lineno, fname))
            try:
                args_text = ", ".join(ast.unparse(a) for a in args)
            except Exception:  # noqa: BLE001
                args_text = ""
            out.append({"module": rel, "line": node.lineno, "callee": fname,
                        "scope": scope, "args": args_text[:160],
                        "rev_kind": rev_kind(args_text)})
    return sorted(out, key=lambda s: s["line"])


def rev_kind(call_text):
    """What revision does this call site name?"""
    text = call_text or ""
    if HEAD_RE.search(text):
        return "head_now"
    if PIN_RE.search(text):
        return "pinned_commit"
    return "unresolved_argument"


def _module_texts():
    out = {}
    for base in ("scripts", "Tools"):
        for dirpath, dirnames, filenames in os.walk(os.path.join(ROOT, base)):
            dirnames[:] = [d for d in dirnames if d not in ("__pycache__",)]
            for name in filenames:
                if not name.endswith(".py"):
                    continue
                full = os.path.join(dirpath, name)
                rel = os.path.relpath(full, ROOT).replace(os.sep, "/")
                try:
                    with io.open(full, encoding="utf-8", errors="replace") as fh:
                        out[rel] = fh.read()
                except Exception:  # noqa: BLE001
                    continue
    return out


def _mentions(node, base):
    for sub in ast.walk(node):
        if isinstance(sub, ast.Constant) and isinstance(sub.value, str) and sub.value.endswith(base):
            return True
    return False


def _names(node):
    return {sub.id for sub in ast.walk(node) if isinstance(sub, ast.Name)}


def _targets(node):
    out = set()
    for sub in ast.walk(node):
        if isinstance(sub, ast.Name) and isinstance(sub.ctx, ast.Store):
            out.add(sub.id)
    return out


def _taint_names(nodes, base, seed):
    """Names that carry the face: a literal, an alias, or a loop binding."""
    tainted = dict(seed)
    changed = True
    while changed:
        changed = False
        for node in nodes:
            if isinstance(node, (ast.Assign, ast.AnnAssign)) and node.value is not None:
                if _mentions(node.value, base) or (_names(node.value) & set(tainted)):
                    for name in _targets(node):
                        if name not in tainted:
                            tainted[name] = node.lineno
                            changed = True
            if isinstance(node, ast.For) and (_mentions(node.iter, base)
                                              or (_names(node.iter) & set(tainted))):
                for sub in ast.walk(node.target):
                    if isinstance(sub, ast.Name) and sub.id not in tainted:
                        tainted[sub.id] = node.lineno
                        changed = True
    return tainted


def _writes_in_scope(nodes, base, seed):
    """Names that carry the face, and the write calls one of them reaches."""
    tainted = _taint_names(nodes, base, seed)
    hits = []
    for node in nodes:
        if not isinstance(node, ast.Call):
            continue
        fname = getattr(node.func, "id", None) or getattr(node.func, "attr", None) or ""
        args = list(node.args) + [k.value for k in node.keywords]
        receiver = None
        if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
            receiver = node.func.value.id
        if re.search(r"write|dump|save|publish", fname, re.I):
            if any(_mentions(a, base) or (_names(a) & set(tainted)) for a in args):
                hits.append(node.lineno)
                continue
        if receiver and receiver in tainted and fname in ("write_text", "write_bytes"):
            hits.append(node.lineno)
            continue
        if fname == "open" and args:
            mode = "r"
            if len(args) > 1 and isinstance(args[1], ast.Constant):
                mode = str(args[1].value or "r")
            if "w" in mode and (_mentions(args[0], base) or (_names(args[0]) & set(tainted))):
                hits.append(node.lineno)
    return tainted, hits


def write_evidence(rel, base, cache=None):
    """Does this module put bytes on disk at a path that names the face?

    Layer 1 is E408's taint analysis; layer 2 covers the two write shapes it cannot see -- a
    module-local helper (`_write(os.path.join(outdir, "<face>"), doc)`) and a `Path` receiver
    (`p2.write_text(...)`).  A bare mention is never a write: the loose test ("names the
    basename and calls dump somewhere") made every reader look like its own writer.
    """
    cache = cache if cache is not None else {}
    if ("text", rel) not in cache:
        cache[("text", rel)] = _lines(rel)
    text = "\n".join(cache[("text", rel)])
    if base not in text:
        return {"writes": False, "how": "does_not_name_the_face"}
    import importlib
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    try:
        e408 = importlib.import_module("e408_writer_refresh_signal")
        ev = e408.write_evidence(os.path.join(ROOT, rel), base)
        if ev.get("writes"):
            return {"writes": True, "how": "taint: " + str(ev.get("how"))[:100],
                    "lines": ev.get("lines") or []}
    except Exception:  # noqa: BLE001
        pass
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return {"writes": False, "how": "unparseable"}
    globals_, _ = _writes_in_scope(list(ast.walk(tree)), base, {})
    scopes = [("module", list(tree.body), globals_)]
    for fn in ast.walk(tree):
        if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            scopes.append((fn.name, list(ast.walk(fn)), globals_))
    for scope, nodes, seed in scopes:
        _tainted, hits = _writes_in_scope(nodes, base, seed)
        if hits:
            return {"writes": True, "how": "a write call reaches the face in %s()" % scope,
                    "lines": sorted(set(hits))[:4]}
    return {"writes": False, "how": "mention_only"}


def _is_one_off(rel):
    stem = os.path.basename(rel)[:-3] if rel.endswith(".py") else os.path.basename(rel)
    return stem.startswith("_") or "_postscript" in stem or rel.startswith("results/")


def _family_latest(base):
    """`ALLOWANCE-2026-11-01.json` -> `allowance_latest.json` (the mirror its producer stamps)."""
    stem = base
    for suffix in (".json",):
        if stem.endswith(suffix):
            stem = stem[: -len(suffix)]
    stem = re.sub(r"[-_]\d{4}-\d{2}-\d{2}$", "", stem)
    stem = re.sub(r"[-_]\d{4}-\d{2}$", "", stem)
    stem = re.sub(r"_latest$", "", stem)
    return stem.lower() + "_latest.json"


def writers_for(basename, texts, cache=None):
    """Modules that actually put bytes on disk at a path naming the face."""
    cache = cache if cache is not None else {}
    writer, one_off, evidence = [], [], {}
    latest = _family_latest(basename)
    dated = latest != basename
    for rel, text in texts.items():
        if basename not in text and not (dated and latest in text):
            continue
        ev = {"writes": False, "how": "does_not_name_the_face"}
        if basename in text:
            ev = write_evidence(rel, basename, cache)
            if not ev.get("writes") and dated:
                # A dated face is written by the module that writes the family's latest mirror
                # and names this file -- E408's taint cannot see a name built from a cutoff.
                if latest in text and write_evidence(rel, latest, cache).get("writes"):
                    ev = {"writes": True, "how": "writes the family mirror and names this file"}
        if not ev.get("writes"):
            continue
        if _is_one_off(rel):
            one_off.append(rel)
        else:
            writer.append(rel)
            evidence[rel] = ev.get("how")
    return sorted(writer), sorted(one_off), evidence


def dirty_paths():
    out = set()
    raw = git(["status", "--porcelain"]) or ""
    for line in raw.splitlines():
        if len(line) > 3:
            out.add(os.path.normpath(line[3:].strip().strip('"')))
    return out


def source_rows(doc):
    """E406's measured faces, with the reader sites its own rows attribute to each."""
    rows_by_face = {}
    for row in doc.get("reader_rows") or []:
        for face in row.get("faces_read_from_a_blob") or []:
            rows_by_face.setdefault(face, []).append(row)
    return [f for f in doc.get("faces") or [] if f.get("state") == "compared"], rows_by_face


def gather(source_doc, rev, texts=None, legs=None, dirty=None, module_cache=None):
    """One row per measured face, every field traceable to a file or a call site."""
    import importlib
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    e406 = importlib.import_module("e406_blob_vs_tree_readers")
    texts = texts if texts is not None else _module_texts()
    legs = legs if legs is not None else suite_legs()
    dirty = dirty if dirty is not None else dirty_paths()
    classifier = _load_e409()
    cache = module_cache if module_cache is not None else {}
    faces, by_face = source_rows(source_doc)
    callees = {r.get("callee") for r in source_doc.get("reader_rows") or [] if r.get("callee")}

    rows = []
    for face in faces:
        rel = face["face"]
        base = os.path.basename(rel)
        gap = e406.gap_for(rel, rev)
        sites = []
        mods = sorted({row.get("module") for row in
                       (by_face.get(base) or by_face.get(face.get("face_name")) or [])
                       if row.get("module")})
        for mod in mods:
            for site in read_sites(mod, base, callees, cache):
                site["self_read"] = False
                site["round_scoped_reader"] = _is_one_off(mod)
                sites.append(site)
        writers, one_off, writer_evidence = writers_for(base, texts, cache)
        net_free = [w for w in writers if not NET_RE.search(texts.get(w, ""))]
        for site in sites:
            site["self_read"] = site["module"] in writers
        opening = [lg for lg in legs if base in lg["text"]]
        legs_open = [{"leg": lg["leg"], "tier": tier_of(lg, classifier)} for lg in opening]
        external = [s for s in sites if not s["self_read"] and not s["round_scoped_reader"]]
        rows.append({
            "face": rel,
            "face_name": face.get("face_name"),
            "differ": bool(gap.get("bytes_differ") or gap.get("keys_moved")
                           or gap.get("headline_moved")),
            "keys_moved": gap.get("keys_moved"),
            "verdict_disk": gap.get("verdict_disk"),
            "verdict_blob": gap.get("verdict_blob"),
            "face_newer_than_head": os.path.normpath(rel) in dirty,
            "sites": len(sites),
            "sites_self_read": sum(1 for s in sites if s["self_read"]),
            "sites_read_by_round_scoped_tools": sum(
                1 for s in sites if s["round_scoped_reader"] and not s["self_read"]),
            "sites_external": len(external),
            "source_basis": face.get("basis"),
            "sites_head_now": sum(1 for s in external if s["rev_kind"] == "head_now"),
            "sites_unresolved_argument": sum(1 for s in external
                                             if s["rev_kind"] == "unresolved_argument"),
            "sites_pinned": sum(1 for s in external if s["rev_kind"] == "pinned_commit"),
            "writers": writers,
            "writers_excluded_as_one_off": one_off,
            "writer_evidence": writer_evidence,
            "net_free_writers": net_free,
            "legs_opening_the_face": legs_open,
            "reader_sites": sites,
        })
    return rows


def decide(row):
    """Frozen rule: the vintage a consumer names decides whether anything is owed."""
    if row["sites_external"] == 0:
        if row.get("sites_self_read"):
            return "c", "only_its_own_writer_reads_it"
        if row.get("sites_read_by_round_scoped_tools"):
            return "c", "read_only_by_round_scoped_tools"
        return "c", "no_call_carries_the_face"
    if row["sites_head_now"] + row["sites_unresolved_argument"] == 0:
        return "c", "every_reader_pins_a_commit"
    if row["net_free_writers"]:
        return "a", "re_derivable_writer_on_hand"
    return "b", "no_net_free_writer"


def _expected_verdict(rows):
    owed = [r for r in rows if r["choice"] in ("a", "b")]
    if not owed:
        if rows and all(r.get("source_basis") == "module_face_literal" for r in rows):
            return VERDICTS[4]
        return VERDICTS[0]
    movers = [r for r in owed if r["face_newer_than_head"] or r["differ"]]
    opened = [r for r in movers if r["legs_opening_the_face"]]
    unopened = [r for r in movers if not r["legs_opening_the_face"]]
    if unopened:
        return VERDICTS[1]
    if opened:
        return VERDICTS[2]
    return VERDICTS[3]


def assemble(rows, rev, source_doc):
    for row in rows:
        choice, why = decide(row)
        row["choice"] = choice
        row["why"] = why
        row["choice_rule"] = CHOICES[choice]
        capable = [lg["leg"] for lg in row["legs_opening_the_face"] if lg["tier"] in CHECK_NAMES]
        row["legs_that_could_notice_age"] = capable
        row["leg_that_should_have_been_red"] = None
        if row["differ"] or row["face_newer_than_head"]:
            if capable:
                # Only an age-pricing leg could have failed on this drift, and drift is not age:
                # the named leg would have to be extended to the blob arm to see it. Recorded as
                # a candidate, never as an existing guard.
                row["leg_that_should_have_been_red"] = capable[0]
                row["candidate_needs_the_blob_arm"] = True
    by_choice = {}
    sites_by_choice = {}
    for row in rows:
        by_choice[row["choice"]] = by_choice.get(row["choice"], 0) + 1
        sites_by_choice[row["choice"]] = (sites_by_choice.get(row["choice"], 0)
                                          + row["sites_external"])
    summary = {
        "faces_measured": len(rows),
        "faces_whose_blob_and_file_differ": sum(1 for r in rows if r["differ"]),
        "faces_newer_than_head_right_now": sum(1 for r in rows if r["face_newer_than_head"]),
        "faces_by_choice": by_choice,
        "external_sites_by_choice": sites_by_choice,
        "faces_all_consumers_pin_a_commit": sum(
            1 for r in rows if r["why"] == "every_reader_pins_a_commit"),
        "faces_read_only_by_their_own_writer": sum(
            1 for r in rows if r["why"] == "only_its_own_writer_reads_it"),
        "faces_read_only_by_round_scoped_tools": sum(
            1 for r in rows if r["why"] == "read_only_by_round_scoped_tools"),
        "faces_no_call_carries": sum(
            1 for r in rows if r["why"] == "no_call_carries_the_face"),
        "faces_owed_a_guard": sum(1 for r in rows if r["choice"] in ("a", "b")),
        "owed_faces_whose_file_is_newer_than_head": sum(
            1 for r in rows if r["choice"] in ("a", "b") and r["face_newer_than_head"]),
        "owed_faces_whose_blob_and_file_differ": sum(
            1 for r in rows if r["choice"] in ("a", "b") and r["differ"]),
        "faces_opened_by_a_suite_leg": sum(1 for r in rows if r["legs_opening_the_face"]),
        "moving_faces_no_leg_opens": sum(
            1 for r in rows if r["choice"] in ("a", "b")
            and (r["differ"] or r["face_newer_than_head"]) and not r["legs_opening_the_face"]),
        "legs_that_should_have_been_red": sum(
            1 for r in rows if r["leg_that_should_have_been_red"]),
        "consumer_sites_total": sum(r["sites_external"] for r in rows),
        "reader_rows_consumed": len(source_doc.get("reader_rows") or []),
        "faces_attributed_by_a_module_literal": sum(
            1 for r in rows if r.get("source_basis") == "module_face_literal"),
        "source_faces_by_basis": source_doc.get("faces_by_basis"),
        "source_study": source_doc.get("study"),
        "source_rev": source_doc.get("rev"),
    }
    return {
        "study": STUDY,
        "card": CARD,
        "evidence_cutoff": source_doc.get("evidence_cutoff"),
        "census_rev": rev,
        "source_face": "results/state_tilt/blobread_latest.json",
        "rule": {
            "population": "every face E406 measured both at HEAD and on disk (state=compared)",
            "rev_kind": {
                "pinned_commit": "the call passes a commit/sha/pin token -- the vintage is the point",
                "head_now": "the call passes HEAD or a helper that resolves it at call time",
                "unresolved_argument": "no revision token on the call line; not evidence of pinning",
            },
            "choice": {"a": CHOICES["a"], "b": CHOICES["b"], "c": CHOICES["c"]},
            "self_read": "a site inside a module that also writes this face is not a consumer",
            "no_rewrite": "no reader and no leg is edited; the repair stays a separate card",
        },
        "summary": summary,
        "rows": sorted(rows, key=lambda r: (r["choice"], -r["sites_external"], r["face"])),
        "verdict": _expected_verdict(rows),
    }


def build(write_face=True):
    if not os.path.exists(SOURCE_FACE):
        raise SystemExit("E406's face is missing: %s" % SOURCE_FACE)
    with io.open(SOURCE_FACE, encoding="utf-8") as fh:
        source_doc = json.load(fh)
    if source_doc.get("study") != "E406_blob_vs_tree_readers":
        raise SystemExit("the population face is not E406's: %r" % source_doc.get("study"))
    rev = head_rev()
    rows = gather(source_doc, rev)
    doc = assemble(rows, rev, source_doc)
    if write_face:
        _write(doc)
    return doc


def _write(doc):
    os.makedirs(OUT_DIR, exist_ok=True)
    body = json.dumps(doc, ensure_ascii=False, indent=1, sort_keys=False) + "\n"
    for path in (DELIVERY, LATEST):
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body)
    say("wrote %s" % os.path.relpath(DELIVERY, ROOT).replace(os.sep, "/"))
    say("wrote %s" % os.path.relpath(LATEST, ROOT).replace(os.sep, "/"))


def verify(path=None):
    path = path or LATEST
    problems = []
    if not os.path.exists(path):
        return ["face missing: %s" % path]
    with io.open(path, encoding="utf-8") as fh:
        doc = json.load(fh)
    if doc.get("verdict") not in VERDICTS:
        problems.append("verdict %r is outside the frozen set" % doc.get("verdict"))
    rows = doc.get("rows") or []
    summary = doc.get("summary") or {}
    if summary.get("faces_measured") != len(rows):
        problems.append("the face headline is not its own table")
    by_choice = {}
    for row in rows:
        by_choice[row.get("choice")] = by_choice.get(row.get("choice"), 0) + 1
        if row.get("choice") not in CHOICES:
            problems.append("%s: unknown choice %r" % (row.get("face"), row.get("choice")))
        if row.get("why") not in WHY:
            problems.append("%s: unknown why %r" % (row.get("face"), row.get("why")))
        want_choice, want_why = decide(row)
        if (row.get("choice"), row.get("why")) != (want_choice, want_why):
            problems.append("%s: the decision does not re-derive from its own row"
                            % row.get("face"))
        sites = row.get("sites") or 0
        ext = row.get("sites_external") or 0
        self_read = row.get("sites_self_read") or 0
        round_scoped = row.get("sites_read_by_round_scoped_tools") or 0
        heads = (row.get("sites_head_now") or 0) + (row.get("sites_unresolved_argument") or 0)
        pinned = row.get("sites_pinned") or 0
        if ext + self_read + round_scoped != sites:
            problems.append("%s: the site columns do not re-add" % row.get("face"))
        if heads + pinned != ext:
            problems.append("%s: the vintage columns do not re-add" % row.get("face"))
        if len(row.get("reader_sites") or []) != sites:
            problems.append("%s: the site list is not its own count" % row.get("face"))
    if summary.get("faces_by_choice") != by_choice:
        problems.append("the choice histogram does not re-derive from the rows")
    if summary.get("faces_whose_blob_and_file_differ") != sum(
            1 for r in rows if r.get("differ")):
        problems.append("the disagreement headline does not re-derive")
    if summary.get("faces_newer_than_head_right_now") != sum(
            1 for r in rows if r.get("face_newer_than_head")):
        problems.append("the newer-than-HEAD headline does not re-derive")
    if summary.get("faces_owed_a_guard") != sum(
            1 for r in rows if r.get("choice") in ("a", "b")):
        problems.append("the owed-guard headline does not re-derive")
    if summary.get("consumer_sites_total") != sum(r.get("sites_external") or 0 for r in rows):
        problems.append("the consumer-site total does not re-derive")
    if doc.get("verdict") != _expected_verdict(rows):
        problems.append("the verdict does not re-derive from the rows")
    if not doc.get("census_rev"):
        problems.append("a decision table was published with no revision")
    # A face published as needing no guard must say which of the two reasons applies.
    for row in rows:
        if row.get("choice") == "c" and row.get("sites_external"):
            if row.get("sites_head_now") or row.get("sites_unresolved_argument"):
                problems.append("%s: called guard-free with a non-pinned consumer"
                                % row.get("face"))
        if row.get("choice") == "a" and not row.get("net_free_writers"):
            problems.append("%s: a re-derive leg is claimed with no writer on hand"
                            % row.get("face"))
        if row.get("choice") == "b" and row.get("net_free_writers"):
            problems.append("%s: a refusal is claimed while a writer is on hand"
                            % row.get("face"))
        if row.get("choice") in ("a", "b") and not (
                row.get("sites_head_now") or row.get("sites_unresolved_argument")):
            problems.append("%s: a guard is owed with no non-pinned consumer"
                            % row.get("face"))
    return problems


def selftest():
    fails = []

    def leg(name, ok, detail=""):
        if not ok:
            fails.append("%s: %s" % (name, detail))

    # 1. the revision classifier reads the call, not the module
    cases = [
        ('blob, reason = git_show_text(rev or "HEAD", rel)', "head_now"),
        ('blobs = read_blobs(head, members)  # HEAD at call time', "head_now"),
        ("blob = git_bytes(commit, rel) if commit else None", "pinned_commit"),
        ("pinned_read = read_pinned(earliest[\"sha\"], pinned)", "pinned_commit"),
        ('"rd": _rd_face(now),', "unresolved_argument"),
    ]
    for text, want in cases:
        leg("rev_kind(%r)" % text[:40], rev_kind(text) == want,
            "wanted %s got %s" % (want, rev_kind(text)))

    # 2. the decision rule, all four branches
    base = {"sites": 2, "sites_external": 2, "sites_self_read": 0, "sites_pinned": 2,
            "sites_head_now": 0, "sites_unresolved_argument": 0, "net_free_writers": []}
    leg("decide pinned", decide(dict(base)) == ("c", "every_reader_pins_a_commit"),
        decide(dict(base)))
    leg("decide own writer",
        decide(dict(base, sites_external=0, sites_self_read=2, sites_pinned=0)) ==
        ("c", "only_its_own_writer_reads_it"))
    leg("decide head with a writer",
        decide(dict(base, sites_pinned=0, sites_head_now=2,
                    net_free_writers=["scripts/x.py"])) == ("a", "re_derivable_writer_on_hand"))
    leg("decide head without a writer",
        decide(dict(base, sites_pinned=0, sites_unresolved_argument=1)) ==
        ("b", "no_net_free_writer"))

    # 3. each verdict branch is reachable from rows
    def row(choice="b", differ=True, dirty=False, legs=None, face="results/x.json"):
        return {"face": face, "choice": choice, "why": WHY["no_net_free_writer"],
                "differ": differ, "face_newer_than_head": dirty,
                "legs_opening_the_face": legs or []}
    leg("verdict all pinned", _expected_verdict([row(choice="c", differ=False)]) == VERDICTS[0])
    leg("verdict weak basis only",
        _expected_verdict([dict(row(choice="c", differ=False),
                               source_basis="module_face_literal")]) == VERDICTS[4])
    leg("verdict no leg", _expected_verdict([row()]) == VERDICTS[1])
    leg("verdict leg reads the file",
        _expected_verdict([row(legs=[{"leg": "x", "tier": "no_freshness_test"}])]) == VERDICTS[2])
    leg("verdict no mover",
        _expected_verdict([row(differ=False,
                               legs=[{"leg": "x", "tier": "no_freshness_test"}])]) == VERDICTS[3])

    # 4. the suite is parsed, not line-indexed
    legs = suite_legs()
    leg("suite legs found", len(legs) > 50, "found %d" % len(legs))
    leg("every leg has a name", all(lg["leg"] for lg in legs))
    lines = len(_lines("smoke_test.py"))
    leg("every leg span is inside the file", all(0 < lg["lo"] <= lg["hi"] <= lines for lg in legs))

    # 5. a face the suite opens resolves to a leg, and its tier is from the frozen set
    fixture = [lg for lg in legs if "blobread_latest.json" in lg["text"]]
    leg("the E406 face is opened by a leg", bool(fixture))
    classifier = _load_e409()
    if classifier is not None and fixture:
        tier = tier_of(fixture[0], classifier)
        leg("the E406 leg has a tier", isinstance(tier, str) and tier != "unclassified", tier)

    # 6. a fixture table assembles and verifies, and a tampered one is refused
    doc = {"study": "E406_blob_vs_tree_readers", "evidence_cutoff": "2026-11-05",
           "rev": "0" * 40, "reader_rows": [{}] * 3}
    rows = [dict(base, face="results/a.json", differ=True, face_newer_than_head=True,
                 sites_pinned=1, sites_head_now=1,
                 sites_self_read=0, sites=2, reader_sites=[{}, {}],
                 legs_opening_the_face=[], writers=[], face_name="a.json",
                 keys_moved=1, verdict_disk=None, verdict_blob=None),
            dict(base, face="results/b.json", differ=False, face_newer_than_head=False,
                 sites=0, sites_external=0, sites_pinned=0, reader_sites=[],
                 legs_opening_the_face=[], writers=["scripts/w.py"], face_name="b.json",
                 keys_moved=0, verdict_disk=None, verdict_blob=None)]
    made = assemble(rows, "0" * 40, doc)
    leg("fixture assembles two rows", len(made["rows"]) == 2)
    leg("fixture verdict is reachable", made["verdict"] in VERDICTS, made["verdict"])
    leg("fixture histogram re-adds",
        made["summary"]["faces_by_choice"] == {"b": 1, "c": 1},
        made["summary"]["faces_by_choice"])

    total = 4 + 4 + 5 + 2 + 1 + 3
    say("selftest %d/%d" % (total - len(fails), total))
    for f in fails:
        say("  FAIL " + f)
    return 0 if not fails else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "run":
        doc = build(write_face=True)
        s = doc["summary"]
        say("faces=%s differ=%s owed=%s by_choice=%s sites_by_choice=%s verdict=%s"
            % (s["faces_measured"], s["faces_whose_blob_and_file_differ"],
               s["faces_owed_a_guard"], s["faces_by_choice"], s["external_sites_by_choice"],
               doc["verdict"]))
        problems = verify(LATEST)
        say("verify problems=%s" % problems)
        return 0 if not problems else 1
    if cmd == "verify":
        problems = verify(argv[2] if len(argv) > 2 else None)
        say("verify problems=%s" % problems)
        return 0 if not problems else 1
    if cmd == "selftest":
        return selftest()
    say("usage: e412_blob_guard_decision.py run|verify|selftest")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))