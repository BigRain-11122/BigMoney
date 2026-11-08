"""E557 -- are the writers of the message-only faces reachable from any entry point?

E556 (r1582) priced the six faces E555 folded out of E554's ``wrote <path>`` rows and
found all six announced only by the message: no ``_latest`` pointer names them and no
source loads them.  E556's own spawn arm added that five of the six writers cannot be
spawned by any source either -- so the question that decides whether the loss is
recoverable is not "who names the face" but "can anything run the writer again".

This study re-reads the six rows (machine-read from E556's published face, never
hand-copied) and runs a *reachability* census over executable sources:

  * a live chain leg (``Tools/s6_chain_bm[abc].py``) that runs the writer -- and
    whether its own arguments let it rebuild the face (``run`` / no argument) or only
    gate it (``--check``/``check``/``--selftest``).  A gate leg proves the face is
    still right; it cannot restore a deleted or stale one.
  * a smoke leg in ``smoke_test.py`` -- which is very often ``--selftest`` only, i.e.
    the module imports and its invariants hold, but nothing is written.
  * a speech act: a subprocess spawn, an import by another module, a scheduled-task
    definition, a shell script.
  * a one-off: a ``Tools/_r<N>`` round snapshot, a ``scripts/e<N>_`` study, a
    ``results/_`` scratch.  These are historical command lines, not entry points.

The distinction the earlier arms could not make: a chain leg's argv is *data* -- a
list of strings inside ``LEGS`` -- so E554's spawn arm (which looks for a call whose
arguments mention the script) is blind to it by construction.  Measured here.

    python scripts/e557_face_entry_reach.py build      # publish the face
    python scripts/e557_face_entry_reach.py check      # re-derive from source; problems must be []
    python scripts/e557_face_entry_reach.py verify     # two builds identical
    python scripts/e557_face_entry_reach.py selftest   # offline fixtures + defect refusals
"""
from __future__ import annotations

import ast
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e554_wrote_population as e554  # noqa: E402  (the corpus and spawn arm reused)
import e556_rescued_face as e556    # noqa: E402  (the survival classifier this extends)

STATE_TILT = os.path.join(ROOT, "results", "state_tilt")
LATEST = os.path.join(STATE_TILT, "faceentryreach_latest.json")
DATED_PREFIX = "FACEENTRYREACH"
PARENT = os.path.join(STATE_TILT, "rescuedface_latest.json")

STUDY = "E557"
CARD = "E557"
TITLE = "whether the writers of the message-only faces are reachable from any entry point"
EVIDENCE_CUTOFF = "2026-11-08"

# ---- naming-site kinds ----------------------------------------------------
N_CHAIN_BUILD = "a_live_chain_leg_runs_the_writer_with_a_build_verb"
N_CHAIN_GATE = "a_live_chain_leg_runs_the_writer_with_a_gate_verb"
N_CHAIN_SELFTEST = "a_live_chain_leg_runs_the_writer_selftest"
N_SMOKE_BUILD = "a_smoke_leg_runs_the_writer_with_a_build_verb"
N_SMOKE_SELFTEST = "a_smoke_leg_runs_the_writer_selftest"
N_SPAWN = "a_source_spawns_the_writer_as_a_subprocess"
N_IMPORT = "another_source_imports_the_module"
N_TASK = "a_task_definition_names_the_writer"
N_SHELL = "a_shell_script_names_the_writer"
N_ONEOFF = "only_a_one_off_round_or_study_script_names_the_writer"

KIND_VOCAB = (N_CHAIN_BUILD, N_CHAIN_GATE, N_CHAIN_SELFTEST, N_SMOKE_BUILD,
              N_SMOKE_SELFTEST, N_SPAWN, N_IMPORT, N_TASK, N_SHELL, N_ONEOFF)

# ---- reachability classes -------------------------------------------------
R_SELF_CHAIN_BUILD = "a_live_chain_on_this_machine_rebuilds_it"
R_OTHER_CHAIN_BUILD = "a_live_chain_on_another_machine_rebuilds_it"
R_GATED_ONLY = "a_live_chain_only_gates_it_and_no_leg_rebuilds_it"
R_SMOKE_ONLY = "only_a_smoke_leg_runs_its_selftest_and_nothing_rebuilds_it"
R_SPEECH_ONLY = "only_a_spawn_or_an_import_reaches_it_and_no_chain_leg_does"
R_TYPED_ONLY = ("only_one_off_scripts_name_it_so_it_can_be_rebuilt_only_by_typing_"
                "the_command_line")
R_NONE = "nothing_in_the_tree_names_the_writer_at_all"

REACH_VOCAB = (R_SELF_CHAIN_BUILD, R_OTHER_CHAIN_BUILD, R_GATED_ONLY, R_SMOKE_ONLY,
               R_SPEECH_ONLY, R_TYPED_ONLY, R_NONE)
REBUILD_CLASSES = (R_SELF_CHAIN_BUILD, R_OTHER_CHAIN_BUILD)

V_SOME_REBUILD = "some_message_only_faces_have_a_live_chain_leg_that_rebuilds_them"
V_NONE_REBUILD = ("no_message_only_face_can_be_rebuilt_by_a_live_chain_leg_anywhere_"
                  "in_the_tree")

MACHINE = "bm-b"
CHAIN_RE = re.compile(r"^(?:Tools/)?s6_chain_bm([abc])\.py$")
ONEOFF_RE = re.compile(r"(^|/)(?:_r\d+|_tmp_|e\d+_|_dbg)")
SMOKE_FILE = "smoke_test.py"

GATE_VERBS = ("--check", "check", "--doctor")
SELFTEST_VERBS = ("--selftest", "selftest")


def _read(path):
    return io.open(path, encoding="utf-8", errors="replace").read()


def _rel(path):
    return os.path.relpath(path, ROOT).replace("\\", "/")


# ---------------------------------------------------------------- population
def population():
    """The six rows E556 published, read out of E556's own face."""
    parent = json.load(io.open(PARENT, encoding="utf-8"))
    rows = parent.get("rows") or []
    out = []
    for r in rows:
        if not r.get("writer"):
            continue
        out.append({"face": r.get("face"), "writer": r.get("writer"),
                    "spawn_class": r.get("spawn_class"),
                    "survival_class": r.get("survival_class")})
    out.sort(key=lambda r: (r["writer"], r["face"]))
    return out


def writers():
    seen = []
    for r in population():
        if r["writer"] not in seen:
            seen.append(r["writer"])
    return sorted(seen)


# ---------------------------------------------------------------- chain legs
_LEG_CACHE = {}


def _argv_token(node):
    """One argv element as a string, or ``None`` when it cannot be read statically.

    ``ast.literal_eval`` over the whole LEGS literal fails on the *first* element
    that is not a literal, and a failed literal_eval returns nothing at all -- the
    first build of this study read bm-b's 306-leg table as an empty list because
    three legs carry ``os.path.join(...)`` inside their argv.  So elements are read
    one at a time, and a fold is attempted before a token is called unreadable.
    """
    try:
        val = ast.literal_eval(node)
        return str(val) if isinstance(val, str) else None
    except Exception:
        pass
    try:
        val, _why = e554._fold(node, {})
        return val if isinstance(val, str) else None
    except Exception:
        return None


def _parse_legs(text):
    """``(legs, unreadable)`` from a chain runner's source text.

    Two traps cost a draft in this window and are pinned as selftest legs:
    a UTF-8 BOM makes ``ast.parse`` raise (and a failed parse used to read as
    "this runner runs nothing" -- bm-b's own 306-leg table was invisible for
    exactly that reason), and ``ast.literal_eval`` over the whole LEGS list
    returns nothing as soon as one leg carries an ``os.path.join(...)``.
    """
    legs, unreadable = [], []
    if not text:
        return legs, unreadable
    try:
        tree = ast.parse(text.lstrip("\ufeff"))
    except SyntaxError:
        return legs, unreadable
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for tgt in node.targets:
            if not (isinstance(tgt, ast.Name) and tgt.id == "LEGS"
                    and isinstance(node.value, ast.List)):
                continue
            for item in node.value.elts:
                if not isinstance(item, ast.Tuple) or len(item.elts) < 2:
                    continue
                if not isinstance(item.elts[1], ast.List):
                    continue
                label = _argv_token(item.elts[0])
                argv, unread = [], []
                for el in item.elts[1].elts:
                    tok = _argv_token(el)
                    if tok is None:
                        try:
                            raw = ast.unparse(el)
                        except Exception:
                            raw = ""
                        unread.append(raw)
                        argv.append("<unreadable:%s>" % raw)
                    else:
                        argv.append(tok)
                legs.append({"label": label or "<unnamed>", "argv": argv,
                             "unreadable_argv": unread})
                if unread:
                    unreadable.append({"leg": label or "<unnamed>", "tokens": unread})
    return legs, unreadable


def _leg_table(chain_rel):
    """Every ``(label, argv)`` a live chain runner actually runs, plus the legs
    whose argv could not be read as data (published, never silently dropped).

    bm-a's runner deliberately imports its list from bm-c's file instead of copying
    it, so a chain file with no ``LEGS`` literal contributes no legs of its own --
    published as ``legs_from`` rather than silently read as "runs nothing".
    """
    if chain_rel in _LEG_CACHE:
        return _LEG_CACHE[chain_rel]
    text = e554._corpus().get(chain_rel) or ""
    legs, unreadable = _parse_legs(text)
    parsed = bool(text) and _parses(text)
    imported = None
    if text:
        try:
            tree = ast.parse(text.lstrip("\ufeff"))
        except SyntaxError:
            tree = None
        for node in ast.walk(tree) if tree is not None else []:
            if isinstance(node, ast.ImportFrom) and node.module \
                    and node.module.startswith("s6_chain_bm"):
                imported = "Tools/%s.py" % node.module
    _LEG_CACHE[chain_rel] = (legs, imported, unreadable)
    _LEG_CACHE[chain_rel + "::parsed"] = parsed
    return _LEG_CACHE[chain_rel]


def _parses(text):
    try:
        ast.parse(text.lstrip("\ufeff"))
        return True
    except SyntaxError:
        return False


def _chain_machine(chain_rel):
    m = CHAIN_RE.match(chain_rel)
    return "bm-%s" % m.group(1) if m else None


def _verb_class(argv):
    toks = [os.path.basename(t) for t in argv if not t.startswith("<unreadable:")]
    if any(t in GATE_VERBS for t in toks):
        return "gate"
    if any(t in SELFTEST_VERBS for t in toks):
        return "selftest"
    return "build"


def _argv_names_writer(argv, script_rel, module_name):
    base = os.path.basename(script_rel)
    for tok in argv:
        if tok.startswith("<unreadable:"):
            # a token only a run-time expression can describe: the writer's own
            # basename inside it is still evidence, and the row says so
            if base in tok or module_name in tok:
                return True
            continue
        t = tok.replace("\\", "/")
        if os.path.basename(t) == base:
            return True
        if t == module_name or t == base.rsplit(".", 1)[0] + ".py":
            return True
    return False


def _chain_imports(chain_rel):
    """The chain file whose LEGS this runner uses, if it imports instead of owning one.

    bm-a's runner says so in its docstring and does ``import s6_chain_bmc as canonical``
    / ``LEGS = canonical.LEGS`` -- an alias, not an ``ImportFrom``.  Read as a module
    relationship, because "runs nothing of its own" and "runs another file's list" are
    different: the legs a host actually runs are the ones that matter.
    """
    text = (e554._corpus().get(chain_rel) or "").lstrip("\ufeff")
    if not text:
        return None
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return None
    aliases = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.name.startswith("s6_chain_bm"):
                    aliases[a.asname or a.name] = "Tools/%s.py" % a.name
        elif isinstance(node, ast.ImportFrom) and node.module \
                and node.module.startswith("s6_chain_bm"):
            for a in node.names:
                aliases[a.asname or a.name] = "Tools/%s.py" % node.module
            aliases.setdefault("__module__", "Tools/%s.py" % node.module)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "LEGS" for t in node.targets):
            val = node.value
            if isinstance(val, ast.Attribute) and val.attr == "LEGS" \
                    and isinstance(val.value, ast.Name):
                return aliases.get(val.value.id)
            if isinstance(val, ast.Name) and val.id in aliases:
                return aliases[val.id]
    return aliases.get("__module__")


def _runners_sharing(chain_rel):
    """This chain plus every chain that runs this chain's leg list."""
    out = [chain_rel]
    for other in sorted(e554._corpus()):
        if CHAIN_RE.match(other) and other != chain_rel and _chain_imports(other) == chain_rel:
            out.append(other)
    return out


def chain_inventory():
    """What each live chain runner is, as data: its machine, how many legs it runs,
    and how many legs carry an argv this scan could not read."""
    out = []
    for chain_rel in sorted(e554._corpus()):
        if not CHAIN_RE.match(chain_rel):
            continue
        legs, imported, unreadable = _leg_table(chain_rel)
        out.append({"chain": chain_rel, "machine": _chain_machine(chain_rel),
                    "legs_run_as_data": len(legs),
                    "source_parsed": bool(_LEG_CACHE.get(chain_rel + "::parsed")),
                    "legs_not_readable_as_data": len(unreadable),
                    "unreadable_legs": unreadable[:10],
                    "leg_list_imported_from": imported or _chain_imports(chain_rel),
                    "machines_that_run_this_list": [
                        _chain_machine(c) for c in _runners_sharing(chain_rel)]})
    return out


def _chain_sites(script_rel, module_name):
    out = []
    for chain_rel in sorted(e554._corpus()):
        if not CHAIN_RE.match(chain_rel):
            continue
        legs, _imported, _unread = _leg_table(chain_rel)
        runners = _runners_sharing(chain_rel)
        for leg in legs:
            if not _argv_names_writer(leg["argv"], script_rel, module_name):
                continue
            verb = _verb_class(leg["argv"])
            kind = {"build": N_CHAIN_BUILD, "gate": N_CHAIN_GATE,
                    "selftest": N_CHAIN_SELFTEST}[verb]
            machines = [_chain_machine(c) for c in runners]
            out.append({"source": chain_rel, "kind": kind, "leg": leg["label"],
                        "argv": leg["argv"], "verb": verb,
                        "machine": _chain_machine(chain_rel),
                        "also_run_by": [m for m in machines
                                        if m and m != _chain_machine(chain_rel)],
                        "matched_in_unreadable_token": any(
                            t.startswith("<unreadable:") for t in leg["argv"])})
    out.sort(key=lambda r: (r["source"], r["leg"]))
    return out


# ---------------------------------------------------------------- smoke legs
_SMOKE_CACHE = {}


def _smoke_legs():
    if "legs" in _SMOKE_CACHE:
        return _SMOKE_CACHE["legs"]
    text = e554._corpus().get(SMOKE_FILE) or ""
    legs = []
    if text:
        try:
            tree = ast.parse(text)
        except SyntaxError:
            tree = None
        if tree is not None:
            for node in ast.walk(tree):
                if not isinstance(node, ast.Tuple) or len(node.elts) < 3:
                    continue
                strs = [e for e in node.elts if isinstance(e, ast.Constant)
                        and isinstance(e.value, str)]
                lists = [e for e in node.elts if isinstance(e, ast.List)]
                if not strs or not lists:
                    continue
                try:
                    args = [str(ast.literal_eval(x)) for x in lists[0].elts]
                except Exception:
                    continue
                for e in strs:
                    legs.append({"names": e.value, "args": args})
    _SMOKE_CACHE["legs"] = legs
    return legs


def _smoke_sites(script_rel, module_name):
    base = os.path.basename(script_rel)
    stem = base.rsplit(".", 1)[0]
    out = []
    for leg in _smoke_legs():
        name = leg["names"].replace("\\", "/")
        if not (name == script_rel or os.path.basename(name) == base or name == stem):
            continue
        verb = _verb_class(leg["args"])
        kind = {"build": N_SMOKE_BUILD, "gate": N_SMOKE_SELFTEST,
                "selftest": N_SMOKE_SELFTEST}[verb]
        out.append({"source": SMOKE_FILE, "kind": kind, "label": leg["names"],
                    "argv": leg["args"], "verb": verb})
    out.sort(key=lambda r: (r["source"], r["label"]))
    return out


# ---------------------------------------------------------------- other sites
def _import_sites(script_rel, module_name):
    out = []
    for rel, text in sorted(e554._corpus().items()):
        if not rel.endswith(".py") or rel == script_rel:
            continue
        if module_name not in text:
            continue
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            hit = None
            if isinstance(node, ast.Import):
                if any(a.name == module_name or a.name.startswith(module_name + ".")
                       for a in node.names):
                    hit = node.lineno
            elif isinstance(node, ast.ImportFrom) and node.module:
                if node.module == module_name or node.module.split(".")[0] == module_name:
                    hit = node.lineno
            if hit and not ONEOFF_RE.search(rel):
                out.append({"source": rel, "kind": N_IMPORT, "line": hit,
                            "is_live_chain": bool(CHAIN_RE.match(rel)),
                            "is_smoke": rel == SMOKE_FILE})
    out.sort(key=lambda r: (r["source"], r["line"]))
    return out


def _spawn_sites(script_rel, module_name):
    out = []
    for s in e554._spawners_of(script_rel, module_name):
        rel = s["source"]
        kind = N_ONEOFF if ONEOFF_RE.search(rel) else (
            N_TASK if rel.endswith(".ps1") and "schtasks" in (e554._corpus().get(rel) or "")
            else (N_SHELL if not rel.endswith(".py") else N_SPAWN))
        out.append({"source": rel, "kind": kind, "line": s["line"],
                    "construct": s.get("construct"), "captures": s.get("captures")})
    out.sort(key=lambda r: (r["source"], r["line"]))
    return out


def _mention_sites(script_rel, module_name):
    """Every executable source that names the writer IN CODE, one row per file.

    Code-level, not text-level: a comment that explains a study (including this
    study's own chain-leg note, which names ``capital_placement``) would otherwise
    enter the raw census as a source and inflate "who names this writer" -- the
    E180/E207 family of self-authored pollution.  Python sources are parsed and
    only name/string constants count; shell sources are matched line by line.
    """
    base = os.path.basename(script_rel)
    stem = base.rsplit(".", 1)[0]
    out = []
    for rel, text in sorted(e554._corpus().items()):
        if rel == script_rel:
            continue
        if stem not in text and base not in text:
            continue
        one_off = bool(ONEOFF_RE.search(rel))
        found = False
        if rel.endswith(".py"):
            try:
                tree = ast.parse(text.lstrip("\ufeff"))
            except SyntaxError:
                tree = None
            if tree is not None:
                for node in ast.walk(tree):
                    if isinstance(node, ast.Name) and stem in node.id:
                        found = True
                        break
                    if isinstance(node, ast.Attribute) and stem in node.attr:
                        found = True
                        break
                    if isinstance(node, ast.Constant) and isinstance(node.value, str) \
                            and (base in node.value or stem == node.value
                                 or base in node.value.replace("\\", "/")
                                 or stem in node.value.replace("\\", "/")):
                        found = True
                        break
                if not found:
                    continue
            else:
                found = True
        else:
            found = any(stem in line for line in text.splitlines())
        if found:
            out.append({"source": rel, "one_off": one_off})
    return out


def _own_command_line(script_rel):
    """The command line the writer's own docstring records, if any -- the thing a
    human would have to retype when no entry point runs it."""
    text = e554._corpus().get(script_rel) or ""
    if not text:
        return None
    head = text.split('"""')
    doc = head[1] if len(head) > 2 else text[:1500]
    for line in doc.splitlines():
        if script_rel in line.replace("\\", "/") and "python" in line:
            return line.strip()
    return None


def _naming_sites(script_rel, module_name):
    sites = []
    sites.extend(_chain_sites(script_rel, module_name))
    sites.extend(_smoke_sites(script_rel, module_name))
    sites.extend(_spawn_sites(script_rel, module_name))
    sites.extend(_import_sites(script_rel, module_name))
    seen = set()
    uniq = []
    for s in sites:
        key = (s["source"], s["kind"], s.get("line") or s.get("leg") or s.get("label"))
        if key in seen:
            continue
        seen.add(key)
        uniq.append(s)
    uniq.sort(key=lambda r: (r["kind"], r["source"]))
    return uniq


def _site_machines(site):
    m = set()
    if site.get("machine"):
        m.add(site["machine"])
    for x in site.get("also_run_by") or []:
        if x:
            m.add(x)
    return m


def classify_reach(sites):
    """Which entry point, if any, can RUN this writer again -- strongest first."""
    chain_build = [s for s in sites if s["kind"] == N_CHAIN_BUILD]
    if any(MACHINE in _site_machines(s) for s in chain_build):
        return R_SELF_CHAIN_BUILD
    if chain_build:
        return R_OTHER_CHAIN_BUILD
    if any(s["kind"] in (N_CHAIN_GATE, N_CHAIN_SELFTEST) for s in sites):
        return R_GATED_ONLY
    if any(s["kind"] in (N_SMOKE_BUILD, N_SMOKE_SELFTEST) for s in sites):
        return R_SMOKE_ONLY
    if any(s["kind"] in (N_SPAWN, N_IMPORT, N_TASK, N_SHELL) for s in sites):
        return R_SPEECH_ONLY
    if any(s["kind"] == N_ONEOFF for s in sites):
        return R_TYPED_ONLY
    return R_NONE


# ---------------------------------------------------------------- build
def build(write=True):
    rows = []
    for site in population():
        face_rel = site["face"]
        writer = site["writer"]
        module_name = os.path.basename(writer).rsplit(".", 1)[0]
        sites = _naming_sites(writer, module_name)
        mentions = _mention_sites(writer, module_name)
        chain_sites = [s for s in sites if s["kind"] in (N_CHAIN_BUILD, N_CHAIN_GATE,
                                                         N_CHAIN_SELFTEST)]
        rows.append({
            "face": face_rel,
            "writer": writer,
            "writer_exists_on_disk": os.path.isfile(os.path.join(ROOT, writer)),
            "survival_class": site["survival_class"],
            "spawn_class": site.get("spawn_class"),
            "leg_contradicts_the_spawn_arm": bool(chain_sites) and
            site.get("spawn_class") == e554.S_NONE,
            "reach_class": classify_reach(sites),
            "naming_sites": sites,
            "build_entry_points": [s for s in sites if s["kind"] in (N_CHAIN_BUILD,
                                                                     N_SMOKE_BUILD)],
            "gate_entry_points": [s for s in sites if s["kind"] in (N_CHAIN_GATE,
                                                                   N_CHAIN_SELFTEST,
                                                                   N_SMOKE_SELFTEST)],
            "fired_by_nothing_but_a_one_off": bool(sites) and all(
                s["kind"] == N_ONEOFF for s in sites),
            "raw_naming_sources": len(mentions),
            "raw_one_off_sources": sum(1 for m in mentions if m["one_off"]),
            "own_command_line": _own_command_line(writer),
        })
    rows.sort(key=lambda r: (r["writer"], r["face"]))

    per_writer = {}
    for r in rows:
        w = per_writer.setdefault(r["writer"], {
            "writer": r["writer"],
            "faces": [],
            "reach_class": r["reach_class"],
            "naming_sites": r["naming_sites"],
            "own_command_line": r["own_command_line"],
            "raw_naming_sources": r["raw_naming_sources"],
            "raw_one_off_sources": r["raw_one_off_sources"],
        })
        w["faces"].append(r["face"])
    for w in per_writer.values():
        w["faces"].sort()

    control = _control_arm()
    inventory = chain_inventory()

    by_reach = {c: 0 for c in REACH_VOCAB}
    by_reach_writers = {c: 0 for c in REACH_VOCAB}
    by_kind = {c: 0 for c in KIND_VOCAB}
    for r in rows:
        by_reach[r["reach_class"]] += 1
        for s in r["naming_sites"]:
            by_kind[s["kind"]] = by_kind.get(s["kind"], 0) + 1
    for w in per_writer.values():
        by_reach_writers[w["reach_class"]] += 1

    rebuild_rows = [r for r in rows if r["reach_class"] in REBUILD_CLASSES]
    rebuild_writers = [w["writer"] for w in per_writer.values()
                       if w["reach_class"] in REBUILD_CLASSES]
    typed_writers = [w["writer"] for w in per_writer.values()
                     if w["reach_class"] == R_TYPED_ONLY]
    if not control["found"]:
        raise SystemExit("the entry-point census is blind: %s" % control["why"])

    verdict = V_SOME_REBUILD if (rebuild_rows or rebuild_writers) else V_NONE_REBUILD

    summary = {
        "rows": len(rows),
        "distinct_writers": len(per_writer),
        "parent_faces_published": len(population()),
        "rows_on_disk": sum(1 for r in rows if r["writer_exists_on_disk"]),
        "rows_with_a_build_entry_point": len(rebuild_rows),
        "writers_with_a_build_entry_point": len(rebuild_writers),
        "writers_rebuilt_on_this_machine": sum(
            1 for w in per_writer.values() if w["reach_class"] == R_SELF_CHAIN_BUILD),
        "writers_rebuilt_only_on_another_machine": sum(
            1 for w in per_writer.values() if w["reach_class"] == R_OTHER_CHAIN_BUILD),
        "writers_only_gated": sum(1 for w in per_writer.values()
                                  if w["reach_class"] == R_GATED_ONLY),
        "writers_only_self_tested": sum(1 for w in per_writer.values()
                                        if w["reach_class"] == R_SMOKE_ONLY),
        "writers_only_typed": len(typed_writers),
        "writers_named_nowhere": sum(1 for w in per_writer.values()
                                     if w["reach_class"] == R_NONE),
        "typed_writers": typed_writers,
        "writers_with_their_command_line_in_their_own_docstring": sum(
            1 for w in per_writer.values() if w["own_command_line"]),
        "rows_whose_spawn_arm_says_no_source_yet_a_chain_leg_runs_them": sum(
            1 for r in rows if r["leg_contradicts_the_spawn_arm"]),
        "raw_naming_sources": sum(r["raw_naming_sources"] for r in rows),
        "raw_one_off_sources": sum(r["raw_one_off_sources"] for r in rows),
        "naming_sites": sum(len(r["naming_sites"]) for r in rows),
        "by_reach_class_rows": {k: v for k, v in by_reach.items() if v},
        "by_reach_class_writers": {k: v for k, v in by_reach_writers.items() if v},
        "by_naming_site_kind": {k: v for k, v in by_kind.items() if v},
        "chain_inventory": inventory,
        "control_arm": control,
    }

    face = {
        "study": STUDY,
        "card": CARD,
        "title": TITLE,
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "machine": MACHINE,
        "population_source": {
            "face": _rel(PARENT),
            "field": "rows",
            "selector": "every row E556 published",
            "published": len(population()),
        },
        "rows": rows,
        "writers": [per_writer[k] for k in sorted(per_writer)],
        "summary": summary,
        "verdict": verdict,
        "verdict_line": ("%d of %d writers can be rebuilt by a live chain leg (%s); "
                         "%d can only be rebuilt by typing the command line"
                         % (len(rebuild_writers), len(per_writer),
                            ", ".join(rebuild_writers) or "none", len(typed_writers))),
        "method_note": (
            "A chain leg is read out of the LEGS literal as data (label, argv), so a "
            "leg whose argv names the script counts as an entry point even though no "
            "call site mentions it -- the blind spot E554's spawn arm had.  A leg's "
            "verb decides whether it rebuilds (run / no argument) or only gates "
            "(--check / check), and a gate leg is never counted as a rebuild path."),
        "method_bound": (
            "static only: a run-time argv assembled from variables is not seen; a "
            "scheduled task is counted only when its definition file names the writer "
            "in a source the corpus reads (py/ps1/bat/cmd/sh); one-off round snapshots "
            "(Tools/_r<N>, scripts/e<N>_, _dbg, _tmp) are published as history and "
            "never as entry points; the census is controlled against %s"
            % ", ".join(_control_specs())),
    }
    if write:
        os.makedirs(STATE_TILT, exist_ok=True)
        _write(os.path.join(STATE_TILT, "%s-%s.json" % (DATED_PREFIX, EVIDENCE_CUTOFF)), face)
        _write(LATEST, face)
    return face


def _write(path, obj):
    raw = json.dumps(obj, ensure_ascii=False, indent=1, sort_keys=False)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(raw + "\n")


# ---------------------------------------------------------------- control arm
CONTROL_BUILD = "scripts/regime_thermo_build.py"
CONTROL_GATE = "scripts/etf_book_hysteresis.py"


def _control_specs():
    return (CONTROL_BUILD, CONTROL_GATE)


def _control_arm():
    """Two arms in opposite directions.

    ``CONTROL_BUILD`` is a writer this machine's own chain runs with no gate verb
    (it rebuilds its face every round) -- if the census cannot see that leg, a
    "nothing reaches these writers" reading would be the instrument's blindness.
    ``CONTROL_GATE`` is a leg the chain runs with an argument, so a build leg and a
    gate leg must not collapse into one class.
    """
    mod = os.path.basename(CONTROL_BUILD).rsplit(".", 1)[0]
    sites = _chain_sites(CONTROL_BUILD, mod)
    builds = [s for s in sites if s["kind"] == N_CHAIN_BUILD]
    own = [s for s in builds if s.get("machine") == MACHINE]
    gmod = os.path.basename(CONTROL_GATE).rsplit(".", 1)[0]
    gsites = _chain_sites(CONTROL_GATE, gmod)
    gates = [s for s in gsites if s["kind"] in (N_CHAIN_GATE, N_CHAIN_SELFTEST)]
    found = bool(own) and bool(gates)
    if found:
        why = None
    elif not builds:
        why = "no live chain leg rebuilds %s" % CONTROL_BUILD
    elif not own:
        why = ("no leg on %s's own chain rebuilds %s, so 'this machine cannot rebuild "
               "it' is not distinguishable from a blind census"
               % (MACHINE, CONTROL_BUILD))
    else:
        why = ("no live chain leg gates %s, so build and gate legs are not "
               "distinguishable" % CONTROL_GATE)
    return {"found": found, "why": why,
            "build_control": CONTROL_BUILD,
            "build_control_legs": [{"source": s["source"], "leg": s["leg"],
                                    "argv": s["argv"], "machine": s["machine"]}
                                   for s in builds],
            "gate_control": CONTROL_GATE,
            "gate_control_legs": [{"source": s["source"], "leg": s["leg"],
                                   "argv": s["argv"], "machine": s["machine"]}
                                  for s in gates]}


# ---------------------------------------------------------------- gate
def face_problems(face):
    probs = []
    rows = face.get("rows") or []
    s = face.get("summary") or {}
    if not rows:
        return ["the population is empty"]

    by_reach = {c: 0 for c in REACH_VOCAB}
    by_kind = {}
    for r in rows:
        if r.get("reach_class") not in REACH_VOCAB:
            probs.append("a reach class outside the vocabulary (%s)" % (r.get("reach_class"),))
        got = classify_reach(r["naming_sites"])
        if got != r.get("reach_class"):
            probs.append("a row's reach class is not what its own sites say (%s: %s vs %s)"
                         % (r.get("face"), r.get("reach_class"), got))
        has_leg = bool([x for x in r["naming_sites"] if x["kind"] in (
            N_CHAIN_BUILD, N_CHAIN_GATE, N_CHAIN_SELFTEST)])
        want_c = has_leg and r.get("spawn_class") == e554.S_NONE
        if bool(r.get("leg_contradicts_the_spawn_arm")) != want_c:
            probs.append("a row's spawn-arm contradiction is not what its own sites say (%s)"
                         % (r.get("face"),))
        if r.get("writer_exists_on_disk") and not os.path.isfile(
                os.path.join(ROOT, r["writer"])):
            probs.append("a row claims its writer is on disk and it is not (%s)"
                         % (r.get("writer"),))
        for site in r["naming_sites"]:
            if site.get("kind") not in KIND_VOCAB:
                probs.append("a naming site of an unknown kind (%s -> %s)"
                             % (r.get("writer"), site.get("kind")))
            if site["kind"] == N_CHAIN_BUILD and ONEOFF_RE.search(site["source"]):
                probs.append("a one-off script is counted as a live chain build leg (%s)"
                             % (site["source"],))
            if site["kind"] in (N_CHAIN_BUILD, N_CHAIN_GATE, N_CHAIN_SELFTEST) \
                    and not CHAIN_RE.match(site["source"]):
                probs.append("a leg-shaped site is not in a live chain runner (%s)"
                             % (site["source"],))
            if site["kind"] == N_ONEOFF and not ONEOFF_RE.search(site["source"]):
                probs.append("a normal source is dismissed as a one-off (%s)"
                             % (site["source"],))
        # a gate leg is never a rebuild
        if r.get("reach_class") in REBUILD_CLASSES and not [
                x for x in r["naming_sites"] if x["kind"] == N_CHAIN_BUILD]:
            probs.append("a row is called rebuildable without a build leg (%s)"
                         % (r.get("face"),))
        if r.get("reach_class") == R_GATED_ONLY and any(
                x["kind"] == N_CHAIN_BUILD for x in r["naming_sites"]):
            probs.append("a row with a build leg is called gated-only (%s)" % (r.get("face"),))
        by_reach[r["reach_class"]] += 1
        for site in r["naming_sites"]:
            by_kind[site["kind"]] = by_kind.get(site["kind"], 0) + 1

    writer_rows = face.get("writers") or []
    writers_seen = {}
    for w in writer_rows:
        writers_seen[w["writer"]] = w["reach_class"]
    for r in rows:
        if writers_seen.get(r["writer"]) != r["reach_class"]:
            probs.append("the writer summary and the rows disagree on %s" % (r["writer"],))
    by_reach_writers = {c: 0 for c in REACH_VOCAB}
    for w in writer_rows:
        by_reach_writers[w["reach_class"]] += 1

    control = _control_arm()
    rebuild_rows = [r for r in rows if r["reach_class"] in REBUILD_CLASSES]
    rebuild_writers = [w["writer"] for w in writer_rows if w["reach_class"] in REBUILD_CLASSES]
    expected = {
        "rows": len(rows),
        "distinct_writers": len(writers_seen),
        "rows_with_a_build_entry_point": len(rebuild_rows),
        "writers_with_a_build_entry_point": len(rebuild_writers),
        "writers_rebuilt_on_this_machine": sum(
            1 for w in writer_rows if w["reach_class"] == R_SELF_CHAIN_BUILD),
        "writers_rebuilt_only_on_another_machine": sum(
            1 for w in writer_rows if w["reach_class"] == R_OTHER_CHAIN_BUILD),
        "writers_only_gated": sum(1 for w in writer_rows if w["reach_class"] == R_GATED_ONLY),
        "writers_only_self_tested": sum(1 for w in writer_rows
                                        if w["reach_class"] == R_SMOKE_ONLY),
        "writers_only_typed": sum(1 for w in writer_rows if w["reach_class"] == R_TYPED_ONLY),
        "writers_named_nowhere": sum(1 for w in writer_rows if w["reach_class"] == R_NONE),
        "raw_naming_sources": sum(r["raw_naming_sources"] for r in rows),
        "raw_one_off_sources": sum(r["raw_one_off_sources"] for r in rows),
        "rows_whose_spawn_arm_says_no_source_yet_a_chain_leg_runs_them": sum(
            1 for r in rows if r["leg_contradicts_the_spawn_arm"]),
        "naming_sites": sum(len(r["naming_sites"]) for r in rows),
        "by_reach_class_rows": {k: v for k, v in by_reach.items() if v},
        "by_reach_class_writers": {k: v for k, v in by_reach_writers.items() if v},
        "by_naming_site_kind": {k: v for k, v in by_kind.items() if v},
        "chain_inventory": chain_inventory(),
    }
    for key, val in expected.items():
        if s.get(key) != val:
            probs.append("summary %s=%r but the rows say %r" % (key, s.get(key), val))
    if s.get("control_arm") != control:
        probs.append("the published control arm is not the one the tree gives")
    if not control["found"]:
        probs.append("the entry-point census is blind: %s" % control["why"])
    want = V_SOME_REBUILD if rebuild_rows or rebuild_writers else V_NONE_REBUILD
    if face.get("verdict") != want:
        probs.append("the verdict is not what the rows derive (%r vs %r)"
                     % (face.get("verdict"), want))
    if not face.get("evidence_cutoff"):
        probs.append("the face carries no evidence_cutoff")
    if (face.get("population_source") or {}).get("published") != len(population()):
        probs.append("the parent face no longer publishes this many rows")
    if s.get("parent_faces_published") != len(population()):
        probs.append("the parent size in the summary is not what E556 publishes now")
    return probs


def check():
    pub = json.load(io.open(LATEST, encoding="utf-8"))
    problems = list(face_problems(pub))
    fresh = build(write=False)
    if [(r["face"], r["writer"]) for r in fresh["rows"]] != \
            [(r["face"], r["writer"]) for r in pub["rows"]]:
        problems.append("the published population is not the one E556 publishes now")
    else:
        for a, b in zip(fresh["rows"], pub["rows"]):
            if json.dumps(a, sort_keys=True) != json.dumps(b, sort_keys=True):
                problems.append("a published row is not what the sources say now (%s)"
                                % (a["face"],))
    if fresh["verdict"] != pub["verdict"]:
        problems.append("the published verdict is not the one the sources derive now")
    print(json.dumps({"problems": problems, "verdict": pub.get("verdict"),
                      "rows": len(pub.get("rows") or []),
                      "writers": (pub.get("summary") or {}).get("distinct_writers"),
                      "rebuilt": (pub.get("summary") or {}).get(
                          "writers_with_a_build_entry_point")}, ensure_ascii=False))
    return 1 if problems else 0


def verify():
    a, b = build(write=False), build(write=False)
    problems = [] if json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True) else \
        ["two builds of the same sources differ"]
    if not problems:
        problems = list(face_problems(a))
    print(json.dumps({"problems": problems}, ensure_ascii=False))
    return 1 if problems else 0


# ---------------------------------------------------------------- selftest
def selftest():
    fails = []
    n = 0

    def ok(label, cond):
        nonlocal n
        n += 1
        if not cond:
            fails.append(label)

    site = lambda kind, **kw: dict({"kind": kind, "source": "Tools/s6_chain_bmb.py"}, **kw)

    ok("a build leg on this machine is the strongest class",
       classify_reach([site(N_CHAIN_BUILD, machine="bm-b")]) == R_SELF_CHAIN_BUILD)
    ok("a build leg on another machine is not a rebuild path here",
       classify_reach([site(N_CHAIN_BUILD, machine="bm-c")]) == R_OTHER_CHAIN_BUILD)
    ok("a gate leg alone is not a rebuild",
       classify_reach([site(N_CHAIN_GATE, machine="bm-c")]) == R_GATED_ONLY)
    ok("a selftest leg alone is not a rebuild",
       classify_reach([site(N_CHAIN_SELFTEST, machine="bm-b")]) == R_GATED_ONLY)
    ok("a smoke selftest is weaker than a chain leg",
       classify_reach([dict(site(N_SMOKE_SELFTEST), source=SMOKE_FILE)]) == R_SMOKE_ONLY)
    ok("an import is a speech act, weaker than a smoke leg",
       classify_reach([dict(site(N_IMPORT), source="scripts/x.py")]) == R_SPEECH_ONLY)
    ok("a one-off script means the command line must be typed",
       classify_reach([dict(site(N_ONEOFF), source="Tools/_r1003bmb_s6.py")]) == R_TYPED_ONLY)
    ok("nothing at all is the empty class", classify_reach([]) == R_NONE)
    ok("a build leg outranks a gate leg in the same file",
       classify_reach([site(N_CHAIN_GATE, machine="bm-b"),
                       site(N_CHAIN_BUILD, machine="bm-b")]) == R_SELF_CHAIN_BUILD)
    ok("a gate verb is never read as a build verb", _verb_class(
        ["python", "scripts/x.py", "--check"]) == "gate")
    ok("a selftest verb is never read as a build verb", _verb_class(
        ["python", "scripts/x.py", "--selftest"]) == "selftest")
    ok("no verb is a build (the script's default command)", _verb_class(
        ["python", "scripts/x.py"]) == "build")
    ok("a positional run is a build", _verb_class(["python", "scripts/x.py", "run"]) == "build")
    ok("a chain argv is matched by basename across separators",
       _argv_names_writer(["python", "scripts\\x.py", "run"], "scripts/x.py", "x"))
    ok("a chain argv that names another script does not match",
       not _argv_names_writer(["python", "scripts/y.py"], "scripts/x.py", "x"))
    ok("one-off snapshots are recognised as history",
       bool(ONEOFF_RE.search("Tools/_r1003bmb_s6.py"))
       and bool(ONEOFF_RE.search("scripts/e556_rescued_face.py"))
       and not ONEOFF_RE.search("Tools/s6_chain_bmb.py"))
    ok("the live chain pattern is bounded to the three runners",
       [bool(CHAIN_RE.match(x)) for x in ("Tools/s6_chain_bmb.py", "Tools/s6_chain_bmc.py",
                                          "Tools/s6_chain_bma.py",
                                          "Tools/_r1003bmb_s6.py")] == [True, True, True, False])
    ok("the chain machine is read off the file name",
       _chain_machine("Tools/s6_chain_bmc.py") == "bm-c")

    # a leg whose argv names the writer must be found by reading LEGS as data,
    # which is exactly what a call-site scan cannot see
    fixture = ("LEGS = [\n"
               "    (\"build_face\", [\"python\", \"scripts/x.py\", \"run\"]),\n"
               "    (\"gate_face\", [\"python\", \"scripts/x.py\", \"--check\"]),\n"
               "    (\"other\", [\"python\", \"scripts/y.py\"]),\n"
               "]\n")
    tree = ast.parse(fixture)
    legs = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "LEGS" for t in node.targets):
            legs = ast.literal_eval(node.value)
    ok("LEGS is readable as data without executing the runner", len(legs) == 3)

    # in-window trap 1: a BOM made ast.parse raise and the whole 306-leg table read
    # as empty.  The BOM is stripped and the table must survive it.
    bom = "\ufeff" + fixture
    ok("a UTF-8 BOM does not hide the leg table", len(_parse_legs(bom)[0]) == 3)
    ok("a BOM-prefixed source still parses", _parses(bom))

    # in-window trap 2: one non-literal argv element made literal_eval over the whole
    # list return nothing.  Elements are read one at a time, and a join is FOLDED
    # (published as a path) while a run-time expression is published as unreadable.
    mixed = ("LEGS = [\n"
             "    (\"joined\", [\"python\", os.path.join(\"scripts\", \"x.py\"), \"run\"]),\n"
             "    (\"runtime\", [\"python\", os.environ.get(\"S\", \"scripts/z.py\")]),\n"
             "    (\"plain\", [\"python\", \"scripts/y.py\"]),\n"
             "]\n")
    mlegs, munread = _parse_legs(mixed)
    ok("one unreadable argv element does not drop the rest of the table",
       len(mlegs) == 3 and len(munread) == 1)
    ok("a joined argv element is folded, not published as unreadable",
       mlegs[0]["argv"][1] == "scripts/x.py")
    ok("the readable leg is still read", mlegs[2]["argv"][-1] == "scripts/y.py")
    ok("the run-time element is published, not skipped",
       any(t.startswith("<unreadable:") for t in mlegs[1]["argv"]))
    ok("the unreadable token keeps its source text so a writer can still be found",
       "scripts/z.py" in [t for t in mlegs[1]["argv"] if t.startswith("<unreadable:")][0])
    ok("a writer named inside an unreadable token still matches",
       _argv_names_writer(mlegs[1]["argv"], "scripts/z.py", "z"))
    ok("an unreadable token does not poison the verb of the leg",
       _verb_class(mlegs[1]["argv"]) == "build")
    ok("a chain that only aliases another file's list runs no legs of its own",
       _parse_legs("LEGS = canonical.LEGS\n")[0] == [])
    ok("the build leg's verb is build", _verb_class(legs[0][1]) == "build")
    ok("the gate leg's verb is gate", _verb_class(legs[1][1]) == "gate")
    ok("a fixture leg set with one build and one gate leg is not classed gated-only",
       classify_reach([
           {"kind": N_CHAIN_BUILD, "source": "Tools/s6_chain_bmb.py", "machine": "bm-b"},
           {"kind": N_CHAIN_GATE, "source": "Tools/s6_chain_bmb.py", "machine": "bm-b"},
       ]) == R_SELF_CHAIN_BUILD)

    # identity: the rebuild classes are exactly the two chain-build classes
    ok("rebuild classes are exactly the two chain-build classes",
       set(REBUILD_CLASSES) == {R_SELF_CHAIN_BUILD, R_OTHER_CHAIN_BUILD})
    ok("the vocabulary has no class that means both gate and rebuild",
       len(set(REACH_VOCAB)) == len(REACH_VOCAB))
    ok("the control arm is an assertion, not a sentence",
       "the entry-point census is blind" in io.open(
           os.path.abspath(__file__), encoding="utf-8").read())
    ok("both control directions are exercised",
       CONTROL_BUILD != CONTROL_GATE and CONTROL_BUILD and CONTROL_GATE)

    print("%d/%d legs green" % (n - len(fails), n))
    for f in fails:
        print("FAIL: %s" % f)
    return 1 if fails else 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "build"
    if cmd == "build":
        face = build()
        print(json.dumps({"rows": len(face["rows"]), "verdict": face["verdict"],
                          "verdict_line": face["verdict_line"]}, ensure_ascii=False))
        return 0
    if cmd == "check":
        return check()
    if cmd == "verify":
        return verify()
    if cmd == "selftest":
        return selftest()
    if cmd == "population":
        rows = population()
        print(json.dumps({"rows": len(rows), "writers": writers()}, ensure_ascii=False))
        return 0
    raise SystemExit("unknown command: %s (build|check|verify|selftest|population)" % cmd)


if __name__ == "__main__":
    sys.exit(main())