"""E598 -- does any reader ask a ``latest.json`` pointer face for a bar at all?

E595 (r1624) priced an alias on ONE pointer face, ``results/etf_book_order/latest.json``, and found
that no reader that actually addresses it asks it for a bar the alias would add.  That is one face.
This study asks the repo-wide question the pool card posed: for every face named ``latest.json``,
WHO opens it and WHICH keys do they ask of it -- and is any of those keys a bar the face does not
carry?  Two outcomes matter and they mean opposite things:

  nothing asked   the missing bar is a repo-wide convention (nobody sources a bar from a pointer
                  face), so E594's "silent readers" have no repair target on this class of face;
  asked+missing   that face IS a silent join -- a reader asks it for a bar it never publishes --
                  and E594's repair finally has a concrete target.

Attribution is by DIRECTORY, not by basename.  E594 resolved targets by basename, so with 27 faces
sharing ``latest.json`` a reader of ``results/etf_book_production/latest.json`` was graded against
``results/etf_book_order/latest.json``.  Here each reader's own literals are folded (``os.path.join``
parts kept) and matched to a face by path suffix; a literal that spells only the basename is
published as ``basename_only`` rather than attributed to a face it never named.

Read-only: opens no runner, writes no fixture, refreshes no panel.  The only write is the face.

  python scripts/e598_pointer_bar_demand.py build
  python scripts/e598_pointer_bar_demand.py check
  python scripts/e598_pointer_bar_demand.py verify
  python scripts/e598_pointer_bar_demand.py selftest

Output: results/state_tilt/POINTERBARDEMAND.json (+ POINTERBARDEMAND-latest.json)
"""
from __future__ import annotations

import ast
import glob
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e594_bar_dialect_join as e594                                     # noqa: E402
import e595_pointer_alias_blast as e595                                  # noqa: E402

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
OUT_PATH = os.path.join(OUTDIR, "POINTERBARDEMAND.json")
SELF_NAME = "e598_pointer_bar_demand.py"
BASENAME = "latest.json"

A_THIS = "names_this_face"
A_AMBIG = "names_the_basename_alone"
A_OTHER = "names_another_face_only"

# the bar vocabulary is E594's speller families, not a hand-written list: a spelling that E594
# already grades is a spelling this study must also grade, or the two faces disagree by construction
BAR_NAMES = sorted({n for names in e594.SPELLINGS.values() for n in names})

V_NO_FACES = "no_latest_json_face_exists_in_the_repo"
V_NO_BAR_ASKED = "no_pointer_face_in_the_repo_is_asked_for_a_bar_at_all"
V_ALL_ASKED = "every_bar_asked_of_a_pointer_face_is_carried_by_that_face"
V_SOME_MISSING = "a_pointer_face_is_asked_for_a_bar_it_does_not_carry"
V_MISSING_SHARED_BINDING = ("the_only_asked_and_missing_bars_sit_on_a_payload_name_shared_by_two"
                            "_faces_so_they_are_unattributable")
V_MISSING_BASENAME_ONLY = ("the_only_asked_and_missing_bars_belong_to_readers_that_spell_the"
                           "_basename_alone")

SCAN_DIRS = ("scripts", "Tools", "firm", "live", "monitor", "content")
SKIP_DIRS = {".git", ".codely-cli", "__pycache__", "results", "research", "docs", "data",
             "legacy", "Money02", ".venv", "node_modules", "media"}
# pointer faces live under results/ and docs/ by construction, so the face scan must not inherit
# the module scan's skip list -- that mistake published "0 faces exist" on the first build
FACE_SKIP_DIRS = {".git", ".codely-cli", "__pycache__", "media", "node_modules", ".venv",
                  "legacy", "Money02"}


# --------------------------------------------------------------------------- pure helpers
def normalise(literal):
    """A literal as a posix path with the leading repo-relative noise trimmed."""
    if not isinstance(literal, str):
        return ""
    s = literal.replace("\\", "/").strip()
    while s.startswith("./"):
        s = s[2:]
    return s


def fold_join(node):
    """Constant parts of an ``os.path.join``/``Path`` call; bare names dropped, None if unreadable."""
    args = list(getattr(node, "args", []) or [])
    parts = []
    for a in args:
        if isinstance(a, ast.Constant) and isinstance(a.value, str):
            parts.append(normalise(a.value))
        elif isinstance(a, (ast.Name, ast.Attribute)):
            continue
        else:
            return None
    return "/".join(p for p in parts if p)


def spelled_paths(src):
    """Every string a module spells whose basename is ``latest.json``, joins folded."""
    out = []
    try:
        tree = ast.parse(src or "")
    except SyntaxError:
        tree = None
    if tree is not None:
        inside_join = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                    and node.func.attr == "join":
                joined = fold_join(node)
                if joined and joined.rstrip("/").split("/")[-1] == BASENAME:
                    out.append(joined)
                    for a in node.args:
                        if isinstance(a, ast.Constant) and isinstance(a.value, str):
                            inside_join.add(id(a))
        # a bare constant that is an element of a folded join is already accounted for by the
        # joined path; reporting it again as ``latest.json`` would turn every join into an
        # ambiguity and undo the directory attribution this study exists to make
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str) \
                    and id(node) not in inside_join:
                lit = normalise(node.value)
                if lit.rstrip("/").split("/")[-1] == BASENAME:
                    out.append(lit)
    return sorted(set(out))


def faces_on_disk(root):
    """Every face named ``latest.json`` in the repo, as repo-relative posix paths."""
    hits = glob.glob(os.path.join(root, "**", BASENAME), recursive=True)
    out = []
    for p in hits:
        rel = os.path.relpath(p, root).replace("\\", "/")
        if any(seg in FACE_SKIP_DIRS for seg in rel.split("/")[:-1]):
            continue
        out.append(rel)
    return sorted(out)


def resolve_literal(literal, faces):
    """Which face(s) a reader's literal names.

    ``results/etf_book_order/latest.json`` names one face; ``etf_book_order/latest.json`` names the
    same face by suffix; a bare ``latest.json`` names all of them and is therefore published as an
    ambiguity rather than attributed to any one of them (E595's collision, restated per reader).
    """
    lit = normalise(literal)
    if not lit or lit.rstrip("/").split("/")[-1] != BASENAME:
        return A_OTHER, []
    if lit == BASENAME:
        return A_AMBIG, list(faces)
    hit = [f for f in faces if lit == f or f.endswith("/" + lit) or lit.endswith("/" + f)]
    return (A_THIS, hit) if hit else (A_OTHER, [])


def addressing(src, faces):
    """(class, faces named) for one module -- A_THIS wins over A_AMBIG over A_OTHER."""
    named, ambiguous = set(), False
    for lit in spelled_paths(src):
        cls, hits = resolve_literal(lit, faces)
        if cls == A_THIS:
            named.update(hits)
        elif cls == A_AMBIG:
            ambiguous = True
    if named:
        return A_THIS, sorted(named)
    if ambiguous:
        return A_AMBIG, []
    return A_OTHER, []


def is_path_to_face(node, face_rel, faces):
    """Is this expression itself a PATH to ``face_rel`` (a literal or a folded join)?

    Deliberately narrow: a module that merely writes the face's path into a published dict
    (``page = {"card": "results/etf_book_production/latest.json"}``) is NAMING the face, not
    loading it, and must not become a payload binding -- the first version walked every constant
    in the assigned value and turned the page dict into a second reader of the card.
    """
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        cls, hits = resolve_literal(node.value, faces)
        return cls == A_THIS and face_rel in hits
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
            and node.func.attr == "join":
        joined = fold_join(node)
        if joined:
            cls, hits = resolve_literal(joined, faces)
            return cls == A_THIS and face_rel in hits
    if isinstance(node, ast.JoinedStr):
        text = "".join(v.value for v in node.values
                       if isinstance(v, ast.Constant) and isinstance(v.value, str))
        if text:
            cls, hits = resolve_literal(text, faces)
            return cls == A_THIS and face_rel in hits
    return False


def _spells_face(node, face_rel, faces):
    """Does this expression, or anything a loader call inside it is given, spell the face?"""
    if is_path_to_face(node, face_rel, faces):
        return True
    if _is_loader_call(node):
        return any(is_path_to_face(sub, face_rel, faces)
                   or (isinstance(sub, ast.Constant) and isinstance(sub.value, str)
                       and is_path_to_face(sub, face_rel, faces))
                   for sub in ast.walk(node))
    return False


LOADER_ATTRS = {"load", "loads", "read_text"}
LOADER_NAMES = {"open", "load_json", "read_json", "_read", "_load", "_read_json", "_load_json",
                "_read_text"}


def _is_loader_call(node):
    """Is this call reading a file into a payload, or building a derived object?

    The distinction decides the study.  ``card = _load(CARD)`` binds the payload; ``page =
    build_page(card)`` and ``info = _series_tail_delta(series)`` bind DERIVED objects, and a key
    read off a derived object is not a key asked of the face.  A first version propagated through
    any call carrying a payload name, and published two "silent joins" that were really
    ``page.get("priced_bar")`` and ``info.get("asof")`` on locally built dicts.
    """
    if not isinstance(node, ast.Call):
        return False
    f = node.func
    if isinstance(f, ast.Attribute) and f.attr in LOADER_ATTRS:
        return True
    return isinstance(f, ast.Name) and f.id in LOADER_NAMES


def keys_asked_of_face(src, face_rel, faces):
    """Which keys a module asks OF this specific face, resolving the payload name up to 4 hops.

    Naming is not opening and opening is not fetching (E470/E595).  The binding being resolved is
    the payload object LOADED FROM this face; a name is bound when its value spells the face, when
    it is another payload name, or when it is a loader call fed by either.  Derived objects built
    from the payload are deliberately not followed (see ``_is_loader_call``): a key read off a
    derived object is not a key asked of the face.  A module whose binding does not resolve is
    published as unresolved rather than as asking for nothing.
    """
    try:
        tree = ast.parse(src or "")
    except SyntaxError:
        return {"keys": [], "resolved": False, "payload_names": []}
    paths, payloads = set(), set()
    follows = False
    for _ in range(4):
        before = (len(paths), len(payloads))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Assign):
                continue
            value = node.value
            tgts = [t.id for t in node.targets if isinstance(t, ast.Name)]
            if not tgts:
                continue
            if is_path_to_face(value, face_rel, faces) or \
                    (isinstance(value, ast.Name) and value.id in paths):
                paths.update(tgts)
                continue
            if isinstance(value, ast.Name) and value.id in payloads:
                payloads.update(tgts)
                continue
            if _is_loader_call(value):
                fed_by_path = any(
                    is_path_to_face(sub, face_rel, faces) or
                    (isinstance(sub, ast.Name) and sub.id in paths) for sub in ast.walk(value))
                fed_by_payload = any(isinstance(sub, ast.Name) and sub.id in payloads
                                     for sub in ast.walk(value))
                if fed_by_path:
                    payloads.update(tgts)
                elif fed_by_payload:
                    # the loader is fed BY the payload we already hold, so what it returns is the
                    # target this face points at, one hop away -- not this face's own payload
                    follows = True
        if (len(paths), len(payloads)) == before:
            break
    names = payloads
    keys = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name) \
                and node.value.id in names:
            sl = node.slice
            if isinstance(sl, ast.Constant) and isinstance(sl.value, str):
                keys.add(sl.value)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                and node.func.attr in ("get", "pop", "setdefault") \
                and isinstance(node.func.value, ast.Name) and node.func.value.id in names \
                and node.args and isinstance(node.args[0], ast.Constant) \
                and isinstance(node.args[0].value, str):
            keys.add(node.args[0].value)
        if isinstance(node, ast.Compare) and isinstance(node.left, ast.Constant) \
                and isinstance(node.left.value, str) and len(node.comparators) == 1 \
                and isinstance(node.comparators[0], ast.Name) \
                and node.comparators[0].id in names:
            keys.add(node.left.value)
    return {"keys": sorted(keys), "resolved": bool(names), "payload_names": sorted(names),
            "path_names": sorted(paths), "follows_a_pointer_redirect": follows}


def open_witnesses(src, face_rel, faces):
    """Line-local lower bound on 'this module opens this face' (E595's witness, per face)."""
    lines = (src or "").splitlines()
    hits = []
    for i, ln in enumerate(lines):
        if BASENAME not in ln:
            continue
        cls, named = A_OTHER, []
        for m in re.finditer(r"""["']([^"'\n]{0,300}latest\.json)["']""", ln):
            cls, named = resolve_literal(m.group(1), faces)
            if cls == A_THIS and face_rel in named:
                break
        if not (cls == A_THIS and face_rel in named):
            continue
        lo, hi = max(0, i - 6), min(len(lines), i + 7)
        for j in range(lo, hi):
            if re.search(r"\b(open|read_text|json\.load|loads)\s*\(", lines[j]):
                hits.append({"literal_line": i + 1, "open_line": j + 1,
                             "snippet": lines[j].strip()[:120]})
                break
    return hits


def bar_split(asked_keys, face_key_set):
    """(bar names asked, of those carried, of those not carried) against one face's payload."""
    asked_bars = sorted(set(asked_keys) & set(BAR_NAMES))
    carried = sorted(n for n in asked_bars if n in face_key_set)
    missing = sorted(n for n in asked_bars if n not in face_key_set)
    return asked_bars, carried, missing


def summarise(rows, n_faces):
    """Counts that must re-derive from the published rows (the guard recomputes this).

    The missing-bar class is published three ways on purpose: every pair, the pairs that are
    actually attributed to the face they name, and the pairs whose payload name is bound to two
    faces in the same module (a name-based resolver cannot separate those).
    """
    asked = [r for r in rows if r.get("bar_keys_asked")]
    missing = [r for r in rows if r.get("bar_keys_missing")]
    attr_missing = [r for r in missing if r["addressing"] == A_THIS]
    clean_missing = [r for r in attr_missing if not r.get("binding_is_shared")]
    return {
        "faces_total": n_faces,
        "faces_with_a_reader": len({r["face"] for r in rows}),
        "faces_with_no_reader": n_faces - len({r["face"] for r in rows}),
        "pairs": len(rows),
        "readers": len({r["reader"] for r in rows}),
        "pairs_names_this_face": sum(1 for r in rows if r["addressing"] == A_THIS),
        "pairs_names_the_basename_alone": sum(1 for r in rows
                                              if r["addressing"] == A_AMBIG),
        "readers_with_resolved_binding": len({r["reader"] for r in rows
                                              if r["payload_binding_resolved"]}),
        "pairs_with_shared_binding": sum(1 for r in rows if r.get("binding_is_shared")),
        "readers_following_a_pointer_redirect": len(
            {r["reader"] for r in rows if r.get("follows_a_pointer_redirect")}),
        "pairs_asking_a_bar": len(asked),
        "readers_asking_a_bar": len({r["reader"] for r in asked}),
        "pairs_asking_a_bar_carried": sum(1 for r in rows if r.get("bar_keys_carried")),
        "pairs_asking_a_bar_missing": len(missing),
        "pairs_asking_a_bar_missing_attributed": len(attr_missing),
        "pairs_asking_a_bar_missing_shared_binding": sum(1 for r in missing
                                                         if r.get("binding_is_shared")),
        "pairs_asking_a_bar_missing_clean": len(clean_missing),
        "faces_asked_a_bar_missing": sorted({r["face"] for r in missing}),
        "readers_asking_a_bar_missing": sorted({r["reader"] for r in missing}),
        "readers_asking_a_bar_missing_clean": sorted({r["reader"] for r in clean_missing}),
        "faces_asked_a_bar_missing_clean": sorted({r["face"] for r in clean_missing}),
        "faces_carrying_no_bar_at_all": [],   # filled by build from the per-face block
    }


def verdict_from(counts):
    """Decided by the intersection: an ATTRIBUTED, unshared bar name a face does not carry."""
    if not counts.get("faces_total"):
        return V_NO_FACES
    if not counts.get("pairs_asking_a_bar"):
        return V_NO_BAR_ASKED
    if counts.get("pairs_asking_a_bar_missing_clean"):
        return V_SOME_MISSING
    if counts.get("pairs_asking_a_bar_missing_attributed"):
        return V_MISSING_SHARED_BINDING
    if counts.get("pairs_asking_a_bar_missing"):
        return V_MISSING_BASENAME_ONLY
    return V_ALL_ASKED


def answer_sentence(counts, faces_block):
    clean = counts.get("readers_asking_a_bar_missing_clean") or []
    barless = counts.get("faces_carrying_no_bar_at_all") or []
    return (
        "%d face(s) named latest.json exist in the repo; %d of them are named by at least one "
        "in-repo module and %d are named by none. Resolving each reader's own literals by "
        "directory (not by basename), %d (face, reader) pair(s) survive; %d spell the full path "
        "and %d spell only the basename (an unattributable literal). %d pair(s) ask a pointer face "
        "for a bar name from the E594 vocabulary, %d of those are carried and %d are not; of the "
        "un-carried ones %d are attributed to the face they name, %d of those survive a shared "
        "payload name, leaving %d clean pair(s) read by %s. %d of the %d faces carry no bar name "
        "at all, so a pointer payload is the normal shape for this class of face. A missing bar is "
        "a repo-wide convention; an asked-and-missing bar on an attributed, unshared binding is a "
        "silent join and a repair target."
        % (counts.get("faces_total", 0), counts.get("faces_with_a_reader", 0),
           counts.get("faces_with_no_reader", 0), counts.get("pairs", 0),
           counts.get("pairs_names_this_face", 0), counts.get("pairs_names_the_basename_alone", 0),
           counts.get("pairs_asking_a_bar", 0), counts.get("pairs_asking_a_bar_carried", 0),
           counts.get("pairs_asking_a_bar_missing", 0),
           counts.get("pairs_asking_a_bar_missing_attributed", 0),
           counts.get("pairs_asking_a_bar_missing_shared_binding", 0),
           counts.get("pairs_asking_a_bar_missing_clean", 0),
           ", ".join(clean) or "nobody", len(barless), counts.get("faces_total", 0)))


# --------------------------------------------------------------------------- repo scan
def modules_on_disk(root):
    """Every python module a reader could live in (bounded, excludes data/results trees)."""
    out = []
    for d in SCAN_DIRS:
        base = os.path.join(root, d)
        if not os.path.isdir(base):
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [x for x in dirnames if x not in SKIP_DIRS]
            for fn in filenames:
                if fn.endswith(".py"):
                    out.append(os.path.relpath(os.path.join(dirpath, fn), root)
                               .replace("\\", "/"))
    for fn in glob.glob(os.path.join(root, "*.py")):
        out.append(os.path.basename(fn))
    return sorted(set(m for m in out if not m.endswith(SELF_NAME)))


def read_src(root, mod):
    try:
        return io.open(os.path.join(root, mod), encoding="utf-8", errors="replace").read()
    except OSError:
        return ""


def scan(root=None):
    root = root or ROOT
    faces = faces_on_disk(root)
    mods = modules_on_disk(root)
    face_block = {}
    for f in faces:
        path = os.path.join(root, f)
        keys, kind = e594.face_keys(path)
        face_block[f] = {"path": f, "kind": kind,
                         "keys": sorted(keys) if kind == "json" else [],
                         "bar_names_carried": sorted(keys & set(BAR_NAMES))
                         if kind == "json" else [],
                         "readers": [], "open_witnesses": {}}
    rows = []
    for mod in mods:
        src = read_src(root, mod)
        if BASENAME not in src:
            continue
        cls, named = addressing(src, faces)
        if cls == A_OTHER:
            continue
        targets = named if cls == A_THIS else faces
        asked_by_face = {f: keys_asked_of_face(src, f, faces) for f in targets}
        # a payload name bound to more than one face in the same module makes the key request
        # unattributable: the resolver is name-based, so `d` reused for two faces would give the
        # union of both key sets to each.  Published per row instead of silently trusted.
        name_faces = {}
        for f, asked in asked_by_face.items():
            for n in asked.get("payload_names") or []:
                name_faces.setdefault(n, set()).add(f)
        for f in targets:
            asked = asked_by_face[f]
            opens = open_witnesses(src, f, faces)
            face_keys = set(face_block[f]["keys"])
            asked_bars, carried, missing = bar_split(asked.get("keys") or [], face_keys)
            shared = sorted(n for n in (asked.get("payload_names") or [])
                            if len(name_faces.get(n) or ()) > 1)
            row = {"face": f, "reader": mod, "addressing": cls,
                   "payload_binding_resolved": bool(asked.get("resolved")),
                   "payload_names": asked.get("payload_names") or [],
                   "binding_names_shared_across_faces": shared,
                   "binding_is_shared": bool(shared),
                   "follows_a_pointer_redirect": bool(
                       asked.get("follows_a_pointer_redirect")),
                   "keys_asked": solved_keys(asked),
                   "bar_keys_asked": asked_bars,
                   "bar_keys_carried": carried,
                   "bar_keys_missing": missing,
                   "opens_this_face": bool(opens),
                   "open_witnesses": opens[:2]}
            rows.append(row)
            face_block[f]["readers"].append(mod)
            if opens:
                face_block[f]["open_witnesses"][mod] = opens[:2]
    for f in face_block:
        face_block[f]["readers"] = sorted(set(face_block[f]["readers"]))
    counts = summarise(rows, len(faces))
    counts["faces_carrying_no_bar_at_all"] = sorted(
        f for f, b in face_block.items() if not b["bar_names_carried"])
    return {"faces": face_block, "rows": rows, "counts": counts}


def solved_keys(asked):
    """The key list, but only for a resolved binding (an unresolved binding asks for nothing we
    can name -- publishing its empty list as 'asks nothing' would be the E595 leg5f mistake)."""
    return list(asked.get("keys") or []) if asked.get("resolved") else []


# --------------------------------------------------------------------------- face
def build(write=True, root=None):
    root = root or ROOT
    sc = scan(root)
    faces_block, rows, counts = sc["faces"], sc["rows"], sc["counts"]
    payload_bar = {}
    for f, b in faces_block.items():
        payload_bar[f] = b["bar_names_carried"]
    face = {
        "study": "E598_pointer_bar_demand",
        "evidence_cutoff": _cutoff(faces_block, root),
        "basename": BASENAME,
        "bar_vocabulary": {"source": "e594.SPELLINGS families (E586 field lists)",
                           "names": BAR_NAMES},
        "addressing_vocab": [A_THIS, A_AMBIG, A_OTHER],
        "faces": faces_block,
        "pairs": rows,
        "counts": counts,
        "verdict": verdict_from(counts),
        "answer": answer_sentence(counts, faces_block),
        "limits": [
            "addressing is decided from the reader's own string literals with os.path.join parts "
            "folded; a path composed at runtime is visible only through the parts it spells",
            "a key request is a resolved payload binding plus a fetch on that name; a module whose "
            "binding does not resolve is published as unresolved, not as asking for nothing",
            "an asked-and-missing bar is a static join failure, not proof the reader runs it",
        ],
    }
    pr = face_problems(face)
    if write and not pr:
        write_face(face)
    return face, pr


def _cutoff(faces_block, root):
    """Newest bar any pointer face carries, used as the study's cutoff (never today's date)."""
    best = None
    for f, b in faces_block.items():
        path = os.path.join(root, f)
        if not path.lower().endswith(".json"):
            continue
        try:
            with io.open(path, encoding="utf-8", errors="replace") as fh:
                payload = json.load(fh)
        except (ValueError, OSError):
            continue
        for k in ("as_of", "evidence_cutoff", "pricing_bar", "ticket_bar", "cutoff"):
            v = payload.get(k) if isinstance(payload, dict) else None
            if isinstance(v, str) and re.match(r"^\d{4}-\d{2}-\d{2}$", v[:10]):
                best = max(best or "", v[:10])
    return best


def write_face(face):
    os.makedirs(OUTDIR, exist_ok=True)
    body = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    for path in (OUT_PATH, os.path.join(OUTDIR, "POINTERBARDEMAND-latest.json")):
        with io.open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(body)


# --------------------------------------------------------------------------- guard
REQUIRED_ROW_KEYS = ("face", "reader", "addressing", "payload_binding_resolved",
                     "payload_names", "binding_is_shared", "follows_a_pointer_redirect",
                     "keys_asked", "bar_keys_asked",
                     "bar_keys_carried", "bar_keys_missing", "opens_this_face")
REQUIRED_FACE_KEYS = ("path", "kind", "keys", "bar_names_carried", "readers")


def face_problems(face):
    p = []
    if not isinstance(face, dict) or "counts" not in face:
        return ["the face carries no counts block"]
    rows = face.get("pairs") or []
    counts = face.get("counts") or {}
    faces_block = face.get("faces") or {}
    if not faces_block:
        p.append("no pointer face is published")
    for f, b in faces_block.items():
        missing = [k for k in REQUIRED_FACE_KEYS if k not in b]
        if missing:
            p.append("face %s lacks %s" % (f, ",".join(missing)))
            break
        if b.get("bar_names_carried") and not set(b["bar_names_carried"]) <= set(face.get(
                "bar_vocabulary", {}).get("names") or []):
            p.append("face %s carries a 'bar' name outside the published vocabulary" % f)
            break
    for r in rows:
        missing = [k for k in REQUIRED_ROW_KEYS if k not in r]
        if missing:
            p.append("row %s/%s lacks %s" % (r.get("face"), r.get("reader"),
                                             ",".join(missing)))
            break
        if r["addressing"] not in (A_THIS, A_AMBIG, A_OTHER):
            p.append("row %s carries an unknown addressing %r" % (r["reader"], r["addressing"]))
            break
        if set(r["bar_keys_carried"]) & set(r["bar_keys_missing"]):
            p.append("row %s carries and misses the same bar name" % r["reader"])
            break
        if set(r["bar_keys_asked"]) != set(r["bar_keys_carried"]) | set(r["bar_keys_missing"]):
            p.append("row %s: asked bars do not split into carried + missing" % r["reader"])
            break
        if r["addressing"] == A_THIS and r["face"] not in faces_block:
            p.append("row %s names a face that is not published" % r["reader"])
            break
    # counts re-derive through the same summariser that built them
    want = summarise(rows, len(faces_block))
    want["faces_carrying_no_bar_at_all"] = sorted(
        f for f, b in faces_block.items() if not b.get("bar_names_carried"))
    for k, v in want.items():
        if counts.get(k) != v:
            p.append("count %s is %r but re-derives to %r" % (k, counts.get(k), v))
    if face.get("verdict") != verdict_from(counts):
        p.append("the verdict does not follow the counts")
    if not face.get("answer"):
        p.append("the face carries no answer sentence")
    if not face.get("bar_vocabulary", {}).get("names"):
        p.append("the bar vocabulary is not published")
    return p


# --------------------------------------------------------------------------- selftest
def selftest():
    ok = []

    def chk(name, cond, detail=""):
        ok.append(bool(cond))
        print(("PASS " if cond else "FAIL ") + name + ((" | " + str(detail)) if not cond else ""))

    faces = ["results/etf_book_order/latest.json", "results/paper_export/latest.json",
             "results/other/latest.json"]

    # leg1 attribution is by directory, not by basename
    chk("leg1 a full path names exactly one face",
        resolve_literal("results/paper_export/latest.json", faces)
        == (A_THIS, ["results/paper_export/latest.json"]),
        resolve_literal("results/paper_export/latest.json", faces))
    chk("leg1b a suffixed literal names the same face",
        resolve_literal("paper_export/latest.json", faces)[0] == A_THIS,
        resolve_literal("paper_export/latest.json", faces))
    chk("leg1c a bare basename is published as an ambiguity, not attributed",
        resolve_literal("latest.json", faces)[0] == A_AMBIG,
        resolve_literal("latest.json", faces))
    chk("leg1d an unrelated literal names no face",
        resolve_literal("results/etf_book_order/TICKET-1.json", faces)[0] == A_OTHER)
    chk("leg1e backslashes resolve like slashes",
        resolve_literal(r"results\etf_book_order\latest.json", faces)[0] == A_THIS)

    # leg2 joins are folded so the directory survives
    src2 = 'p = os.path.join("results", "paper_export", "latest.json")\n'
    chk("leg2 an os.path.join literal keeps its directory",
        spelled_paths(src2) == ["results/paper_export/latest.json"], spelled_paths(src2))
    chk("leg2b and that module addresses that face",
        addressing(src2, faces) == (A_THIS, ["results/paper_export/latest.json"]),
        addressing(src2, faces))
    chk("leg2c a module with no latest.json literal addresses nothing",
        addressing("x = 1", faces)[0] == A_OTHER)

    # leg3 key requests must come off the payload bound to that face
    src3 = ('import json\n'
            'p = os.path.join("results", "paper_export", "latest.json")\n'
            'd = json.load(open(p))\n'
            'bar = d["as_of"]\n'
            'n = d.get("nav")\n')
    asked3 = keys_asked_of_face(src3, "results/paper_export/latest.json", faces)
    chk("leg3 the payload binding resolves", asked3["resolved"] is True, asked3)
    chk("leg3b both fetched keys are collected",
        set(asked3["keys"]) == {"as_of", "nav"}, asked3["keys"])
    other = keys_asked_of_face(src3, "results/etf_book_order/latest.json", faces)
    chk("leg3c the same source asks the OTHER face for nothing",
        other["resolved"] is False and other["keys"] == [], other)

    # leg3d naming a face in a payload is not loading it (the first build's page-dict false positive)
    src3d = ('page = {"card": "results/paper_export/latest.json", "n": 1}\n'
             'bar = page.get("as_of")\n')
    asked3d = keys_asked_of_face(src3d, "results/paper_export/latest.json", faces)
    chk("leg3d a dict literal that NAMES the face is not a payload binding",
        asked3d["resolved"] is False and asked3d["keys"] == [], asked3d)

    # leg3e a loader fed by the payload is the pointer's TARGET (one hop), not the pointer
    faces4 = faces + ["docs/x/latest.json"]
    src3e = ('import json\n'
             'ptr = json.load(open("docs/x/latest.json", encoding="utf-8"))\n'
             'page = json.load(open(ptr.get("json"), encoding="utf-8"))\n'
             'b = page.get("priced_bar")\n')
    asked3e = keys_asked_of_face(src3e, "docs/x/latest.json", faces4)
    chk("leg3e the pointer itself is asked only for its redirect key",
        asked3e["keys"] == ["json"], asked3e["keys"])
    chk("leg3e2 and the bar read off the target is published as a hop",
        asked3e["follows_a_pointer_redirect"] is True, asked3e)

    # leg3f an alias of the payload is still the payload
    src3f = src3 + "e = d\nbar2 = e[\"as_of\"]\n"
    asked3f = keys_asked_of_face(src3f, "results/paper_export/latest.json", faces)
    chk("leg3f an alias of the payload stays a payload name",
        "e" in asked3f["payload_names"] and "as_of" in asked3f["keys"], asked3f)

    # leg4 bar split against one face's payload
    a, c, m = bar_split(["as_of", "nav", "evidence_cutoff"], {"as_of", "nav"})
    chk("leg4 a bar carried by the face lands in carried", c == ["as_of"], (a, c, m))
    chk("leg4b a non-bar key is not graded as a bar", "nav" not in a, a)
    chk("leg4c a bar the face lacks lands in missing", m == ["evidence_cutoff"], m)
    chk("leg4c2 asked bars split exactly into carried + missing",
        sorted(c + m) == sorted(a), (a, c, m))
    a2, c2, m2 = bar_split(["as_of", "evidence_cutoff"], {"nav"})
    chk("leg4d a bar the face lacks is published as missing",
        m2 == ["as_of", "evidence_cutoff"] and c2 == [], (a2, c2, m2))

    # leg5 the counts re-derive, and the verdict is decided by the missing class only
    rows_none = [{"face": faces[0], "reader": "a.py", "addressing": A_THIS,
                  "payload_binding_resolved": True, "payload_names": ["d"],
                  "binding_names_shared_across_faces": [], "binding_is_shared": False,
                  "follows_a_pointer_redirect": False,
                  "keys_asked": ["nav"], "bar_keys_asked": [], "bar_keys_carried": [],
                  "bar_keys_missing": [], "opens_this_face": True, "open_witnesses": []}]
    cnt_none = summarise(rows_none, len(faces))
    chk("leg5 no bar asked -> NO_BAR_ASKED", verdict_from(cnt_none) == V_NO_BAR_ASKED,
        verdict_from(cnt_none))
    rows_all = [dict(rows_none[0], bar_keys_asked=["as_of"], bar_keys_carried=["as_of"],
                     keys_asked=["as_of"])]
    cnt_all = summarise(rows_all, len(faces))
    chk("leg5b every asked bar carried -> ALL_ASKED", verdict_from(cnt_all) == V_ALL_ASKED,
        verdict_from(cnt_all))
    rows_miss = [dict(rows_none[0], bar_keys_asked=["as_of"], bar_keys_missing=["as_of"],
                      keys_asked=["as_of"])]
    cnt_miss = summarise(rows_miss, len(faces))
    chk("leg5c an attributed, unshared asked-and-missing bar -> SOME_MISSING",
        verdict_from(cnt_miss) == V_SOME_MISSING, verdict_from(cnt_miss))
    chk("leg5d the missing reader is published by name",
        cnt_miss["readers_asking_a_bar_missing_clean"] == ["a.py"], cnt_miss)
    chk("leg5e faces with no reader are counted, not dropped",
        cnt_none["faces_with_no_reader"] == len(faces) - 1, cnt_none)
    # the three attribution arms must not collapse into each other
    rows_ambig = [dict(rows_miss[0], addressing=A_AMBIG)]
    cnt_ambig = summarise(rows_ambig, len(faces))
    chk("leg5f a missing bar on a basename-only reader is NOT called a silent join",
        verdict_from(cnt_ambig) == V_MISSING_BASENAME_ONLY
        and cnt_ambig["pairs_asking_a_bar_missing_clean"] == 0, cnt_ambig)
    rows_shared = [dict(rows_miss[0], binding_is_shared=True,
                        binding_names_shared_across_faces=["d"])]
    cnt_shared = summarise(rows_shared, len(faces))
    chk("leg5g a missing bar on a payload name shared by two faces is published as unattributable",
        verdict_from(cnt_shared) == V_MISSING_SHARED_BINDING, cnt_shared)

    # leg6 the guard refuses hand-written counts and a verdict that contradicts them
    base_face = {
        "bar_vocabulary": {"names": BAR_NAMES},
        "faces": {faces[0]: {"path": faces[0], "kind": "json", "keys": ["nav"],
                             "bar_names_carried": [], "readers": ["a.py"]},
                  faces[1]: {"path": faces[1], "kind": "json", "keys": ["as_of"],
                             "bar_names_carried": ["as_of"], "readers": []},
                  faces[2]: {"path": faces[2], "kind": "text", "keys": [],
                             "bar_names_carried": [], "readers": []}},
        "pairs": rows_miss,
        "counts": dict(cnt_miss, faces_carrying_no_bar_at_all=sorted(
            [faces[0], faces[2]])),
        "verdict": verdict_from(cnt_miss),
        "answer": "x",
    }
    chk("leg6 the guard accepts a face whose counts re-derive",
        face_problems(base_face) == [], face_problems(base_face))
    bad = json.loads(json.dumps(base_face))
    bad["counts"]["pairs_asking_a_bar_missing"] = 0
    chk("leg6b the guard refuses a missing-pair count that does not re-derive",
        any("pairs_asking_a_bar_missing" in s for s in face_problems(bad)), face_problems(bad))
    bad2 = json.loads(json.dumps(base_face))
    bad2["verdict"] = V_ALL_ASKED
    chk("leg6c the guard refuses a verdict that contradicts the rows",
        any("verdict does not follow" in s for s in face_problems(bad2)), face_problems(bad2))
    bad3 = json.loads(json.dumps(base_face))
    bad3["pairs"][0]["bar_keys_carried"] = ["as_of"]
    chk("leg6d the guard refuses a row that both carries and misses the same bar",
        any("same bar name" in s or "split into" in s for s in face_problems(bad3)),
        face_problems(bad3))
    bad4 = json.loads(json.dumps(base_face))
    bad4["faces"]["results/other/latest.json"]["bar_names_carried"] = ["not_a_bar_field"]
    chk("leg6e the guard refuses a bar name outside the published vocabulary",
        any("outside the published vocabulary" in s for s in face_problems(bad4)),
        face_problems(bad4))

    # leg7 the face scan must not inherit the module scan's skip list (this bug shipped once:
    #      "0 faces exist" because results/ was skipped for modules and then for faces too)
    chk("leg7 the face scan does not skip results/ or docs/",
        "results" not in FACE_SKIP_DIRS and "docs" not in FACE_SKIP_DIRS, sorted(FACE_SKIP_DIRS))
    chk("leg7b while the module scan does skip them",
        "results" in SKIP_DIRS and "docs" in SKIP_DIRS)
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        for rel in ("results/a/latest.json", "results/b/latest.json", "docs/live_usage/latest.json",
                    ".codely-cli/x/latest.json"):
            full = os.path.join(td, rel.replace("/", os.sep))
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with io.open(full, "w", encoding="utf-8") as f:
                f.write('{"as_of": "2026-11-06"}\n')
        found = faces_on_disk(td)
        chk("leg7c faces under results/ and docs/ are found, .codely-cli is not",
            found == ["docs/live_usage/latest.json", "results/a/latest.json",
                      "results/b/latest.json"], found)

    # leg8 the answer sentence carries the numbers it counted
    ans = answer_sentence(cnt_miss, base_face["faces"])
    chk("leg8 the answer names the reader class and the counts",
        "a.py" in ans and str(len(faces)) in ans, ans[:200])

    n_ok = sum(1 for x in ok if x)
    print("\nselftest %d/%d" % (n_ok, len(ok)))
    return 0 if n_ok == len(ok) else 1


# --------------------------------------------------------------------------- cli
def main(argv):
    mode = (argv[1] if len(argv) > 1 else "build").lower()
    if mode == "selftest":
        return selftest()
    if mode == "build":
        face, pr = build(write=True)
        print("built %s | verdict=%s" % (os.path.relpath(OUT_PATH, ROOT), face.get("verdict")))
        print("answer:", face.get("answer"))
        if pr:
            print("problems:", pr)
            return 2
        return 0
    if mode == "check":
        _face, pr = build(write=False)
        print("problems=%s" % pr)
        return 0 if not pr else 2
    if mode == "verify":
        if not os.path.exists(OUT_PATH):
            print("no face on disk")
            return 2
        with io.open(OUT_PATH, encoding="utf-8") as f:
            on_disk = json.load(f)
        fresh, _pr = build(write=False)
        keys = ("faces", "pairs", "counts", "verdict", "bar_vocabulary", "basename")
        diff = [k for k in keys if on_disk.get(k) != fresh.get(k)]
        print("problems=%s" % (["field does not re-derive: %s" % k for k in diff] or []))
        return 0 if not diff else 2
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))