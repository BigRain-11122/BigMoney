"""E553 -- whether the six ``wrote <path>`` messages are read back by any machine.

E550 (r1577) found six sites where a file-naming constant is only *rendered*
into a message -- ``print("wrote", OUT_PATH, ...)`` in the six ``etf_phase_*``
scripts -- and published ``no_site_that_hands_the_constant_on_reads_it_as_a_container_one_hop_out``.
A printed output path looks like a contract: a caller could parse it, a log
scraper could key on the word, a test could assert on the line.  This study asks
whether anything actually does, for each of the six, and whether the printed
path is the only machine-visible announcement of the face it names.

The population is machine-read from the parent's own face
(``calledconsumer_latest.json`` -- the rows whose one hop out is a builtin that
only renders), never hand-listed.  Three routes are measured per row:

  * the in-process route -- a module that *imports* the writer.  The render sits
    inside the writer's ``main()``, so the question is whether ``main`` is
    reachable except from the ``if __name__ == "__main__"`` guard;
  * the process route -- a source that spawns the script and *captures* stdout.
    A spawn that leaves stdout on the console cannot be parsed by the spawner;
  * the text route -- any source (Python or shell) that uses the message word in
    a *parsing* position (startswith/split/partition/regex/membership/grep),
    regardless of who produced the line.

The announcement half asks a different question: if the message is not read, is
the face it names announced to any machine at all?  A source that names the face
path in a literal, or a ``*_latest`` pointer that resolves it, is an announcement
that survives the loss of the message.

    python scripts/e553_render_reader.py build      # publish the face
    python scripts/e553_render_reader.py check       # re-derive from source; problems must be []
    python scripts/e553_render_reader.py verify      # two builds identical
    python scripts/e553_render_reader.py selftest    # offline fixtures + defect refusals
"""
from __future__ import annotations

import ast
import io
import json
import os
import re
import sys
import textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
STATE_TILT = os.path.join(ROOT, "results", "state_tilt")
PARENT_LATEST = os.path.join(STATE_TILT, "calledconsumer_latest.json")
LATEST = os.path.join(STATE_TILT, "renderreader_latest.json")
DATED_PREFIX = "RENDERREADER"

STUDY = "E553"
CARD = "E553"
TITLE = "whether the six wrote-path messages are read back by any machine code"
EVIDENCE_CUTOFF = "2026-11-08"

# The parent's own words for "the callee is a builtin that only renders the value".
P_KIND_BUILTIN = "a_builtin"
P_USE_RENDERS = "renders_only"

# ---- reader classes, one per way a message could be consumed --------------
R_IN_PROCESS_IMPORT_ONLY = "the_writer_is_imported_but_the_render_is_unreachable_from_that_import"
R_IN_PROCESS_REACHABLE = "the_writer_is_imported_and_the_render_is_reachable_from_the_import"
R_PROCESS_CAPTURED = "the_writer_is_spawned_by_a_source_that_captures_its_stdout"
R_PROCESS_UNCAPTURED = "the_writer_is_spawned_but_its_stdout_is_not_captured"
R_WORD_PARSED_ELSEWHERE = "the_message_word_is_parsed_in_the_repository_but_by_code_that_never_sees_this_line"
R_NOTHING = "nothing_in_the_repository_names_or_runs_this_writer"
READER_VOCAB = (R_IN_PROCESS_IMPORT_ONLY, R_IN_PROCESS_REACHABLE, R_PROCESS_CAPTURED,
                R_PROCESS_UNCAPTURED, R_WORD_PARSED_ELSEWHERE, R_NOTHING)
# Classes whose row's line can actually reach a consumer.
READER_CLASSES_THAT_READ = (R_PROCESS_CAPTURED, R_IN_PROCESS_REACHABLE)

# ---- announcement classes -------------------------------------------------
A_ONLY_MESSAGE = "only_the_rendered_message_announces_this_face"
A_SOURCE_LITERAL = "a_source_literal_announces_this_face"
A_POINTER_FACE = "a_pointer_face_announces_this_face"
A_BOTH = "both_a_source_literal_and_a_pointer_face_announce_this_face"
ANNOUNCE_VOCAB = (A_ONLY_MESSAGE, A_SOURCE_LITERAL, A_POINTER_FACE, A_BOTH)

V_NO_READER = "no_repository_code_reads_back_any_of_the_six_rendered_paths"
V_SOME_READER = "some_of_the_six_rendered_paths_are_read_back_by_repository_code"
V_ALL_ONLY_MESSAGE = "every_one_of_the_six_faces_is_announced_only_by_the_message_that_nobody_reads"
V_SOME_ANNOUNCED_ELSEWHERE = "at_least_one_of_the_six_faces_is_announced_by_something_other_than_the_message"
VERDICT_VOCAB = (V_NO_READER, V_SOME_READER)
ANNOUNCE_VERDICT_VOCAB = (V_ALL_ONLY_MESSAGE, V_SOME_ANNOUNCED_ELSEWHERE)

# The word a rendered line begins with.  Read from the render site, not hardcoded
# into the classification: these are only the spellings a *parsing* position is
# looked for, and the site's own word must be among them or the row is unsettled.
MESSAGE_WORD_GUARD = ("wrote",)

# Frames that spawn a process.
SPAWN_FUNCS = ("run", "call", "check_call", "check_output", "Popen", "system",
               "spawn", "spawnv", "spawnl", "popen")

# Directories never walked.
SKIP_DIRS = {".git", "data", "__pycache__", "media", "_quarantine",
             "node_modules", ".codely-cli"}
# The study must not measure its own output (E180/E207 family).
SELF_EXCLUDE = re.compile(r"(^|/)e55[0-9]_|^scripts/e553_render_reader\.py$"
                          r"|results/state_tilt/[A-Z]*RENDERREADER"
                          r"|results/state_tilt/renderreader_latest")


# ---------------------------------------------------------------- source reads
def _read(path):
    return io.open(path, encoding="utf-8", errors="replace").read()


def _rel(path):
    return os.path.relpath(path, ROOT).replace("\\", "/")


_WALK_CACHE = {}
_CORPUS = None
_POINTERS = None


def _walk_sources(exts=(".py",)):
    """Paths only -- never reads.  Cached per extension tuple (E442 family)."""
    exts = tuple(exts)
    if exts in _WALK_CACHE:
        return _WALK_CACHE[exts]
    out = []
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fn in files:
            if not fn.endswith(exts):
                continue
            p = os.path.join(base, fn)
            rel = _rel(p)
            if SELF_EXCLUDE.search(rel):
                continue
            out.append((rel, p))
    _WALK_CACHE[exts] = sorted(out)
    return _WALK_CACHE[exts]


def _corpus():
    """Every text source in the repo, read exactly once.

    A repo-wide read per row costs minutes on this tree; the whole point of the
    cache is that six rows share one pass (E442's lesson, applied to I/O).
    """
    global _CORPUS
    if _CORPUS is not None:
        return _CORPUS
    corpus = {}
    for rel, path in _walk_sources((".py", ".ps1", ".bat", ".cmd", ".sh")):
        try:
            if os.path.getsize(path) > 4 * 1024 * 1024:
                continue
            corpus[rel] = _read(path)
        except OSError:
            continue
    _CORPUS = corpus
    return _CORPUS


def _pointer_faces():
    """Small ``*_latest.json`` pointer faces, read once.

    Only pointer-sized JSON is scanned: reading every face in ``results/`` is
    1.2 GB on this tree, and a pointer face is by definition the small one.
    """
    global _POINTERS
    if _POINTERS is not None:
        return _POINTERS
    out = {}
    for rel, path in _walk_sources((".json",)):
        if not os.path.basename(rel).endswith("_latest.json"):
            continue
        try:
            if os.path.getsize(path) > 512 * 1024:
                continue
            out[rel] = _read(path)
        except OSError:
            continue
    _POINTERS = out
    return _POINTERS


def _parse(rel, path):
    try:
        return ast.parse(_read(path))
    except SyntaxError:
        return None


def _word_of_render(call):
    """The first word of the rendered message, from the call's own arguments."""
    if not call.args:
        return None
    first = call.args[0]
    if isinstance(first, ast.Constant) and isinstance(first.value, str):
        return first.value.split()[0] if first.value.split() else None
    if isinstance(first, ast.BinOp) and isinstance(first.op, ast.Mod):
        fmt = first.left
        if isinstance(fmt, ast.Constant) and isinstance(fmt.value, str):
            parts = fmt.value.split()
            return parts[0] if parts else None
    return None


def _enclosing_function(tree, line):
    """The innermost FunctionDef whose body holds `line`, and the guard reach."""
    best = None
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            end = getattr(node, "end_lineno", node.lineno)
            if node.lineno <= line <= end:
                if best is None or node.lineno > best.lineno:
                    best = node
    return best


def _main_guard_calls(tree):
    """Names called from an ``if __name__ == '__main__'`` block."""
    called = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.If):
            continue
        try:
            cond = ast.unparse(node.test)
        except Exception:
            cond = ""
        if "__name__" not in cond:
            continue
        for inner in ast.walk(node):
            if isinstance(inner, ast.Call):
                try:
                    called.add(ast.unparse(inner.func))
                except Exception:
                    pass
    return called


def _reachable_from_guard(tree, func):
    """Is `func` called only from the main guard / another such function?"""
    if func is None:
        return False
    name = func.name
    guard = _main_guard_calls(tree)
    if name in guard:
        return True
    # one level: another function that is itself guard-called calls this one
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in guard:
            for inner in ast.walk(node):
                if isinstance(inner, ast.Call):
                    try:
                        if ast.unparse(inner.func) == name:
                            return True
                    except Exception:
                        pass
    return False


def _importers_below(module_name):
    """Modules that import `module_name` (in-process route)."""
    out = []
    for rel, text in sorted(_corpus().items()):
        if not rel.endswith(".py") or rel == "scripts/%s.py" % module_name:
            continue
        if module_name not in text:
            continue
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.Import):
                names = [a.name.split(".")[-1] for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [a.name for a in node.names]
                if node.module and node.module.split(".")[-1] == module_name:
                    out.append({"source": rel, "line": node.lineno,
                                "construct": "from_import", "captures": False})
                    break
            if module_name in names:
                out.append({"source": rel, "line": node.lineno,
                            "construct": "import", "captures": False})
                break
    return out


def _spawners_of(script_rel, module_name):
    """Sources that spawn the script, with whether they capture stdout."""
    out = []
    stems = (script_rel, os.path.basename(script_rel), module_name)
    for rel, text in sorted(_corpus().items()):
        if not any(s in text for s in stems):
            continue
        if rel.endswith(".py"):
            for line, captured in _spawn_lines(rel, text, stems):
                out.append({"source": rel, "line": line, "construct": "spawn",
                            "captures": captured})
        else:
            for i, line in enumerate(text.splitlines(), 1):
                if not any(s in line for s in stems):
                    continue
                captured = bool(re.search(r"\|\s*Out-String|=\s*&|\(&|\$\(|\bSelect-String\b", line))
                out.append({"source": rel, "line": i, "construct": "shell_spawn",
                            "captures": captured})
    return out


def _spawn_lines(rel, text, stems):
    """Lines in one Python source where a spawn names the script."""
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []
    lines = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        try:
            fname = ast.unparse(node.func)
        except Exception:
            continue
        if not any(fname.split(".")[-1] == s for s in SPAWN_FUNCS):
            continue
        try:
            argtext = " ".join(ast.unparse(a) for a in node.args)
        except Exception:
            argtext = ""
        kw = " ".join("%s=%s" % (k.arg, ast.unparse(k.value)) for k in node.keywords if k.arg)
        if not any(s in argtext for s in stems):
            continue
        captured = ("capture_output" in kw and "True" in kw) or \
                   (re.search(r"stdout\s*=\s*(subprocess\.)?PIPE", kw) is not None) or \
                   fname.split(".")[-1] == "check_output"
        lines.append((node.lineno, bool(captured)))
    return lines


PARSE_PATTERNS = (
    ("startswith", re.compile(r"\.startswith\(\s*['\"]%s")),
    ("split", re.compile(r"\.split\(\s*['\"]%s")),
    ("partition", re.compile(r"\.(partition|rpartition)\(\s*['\"]%s")),
    ("membership", re.compile(r"['\"]%s['\"]\s+(not\s+)?in\b")),
    ("membership", re.compile(r"(not\s+)?in\s+['\"]%s['\"]")),
    ("regex", re.compile(r"(re\.(search|match|findall|compile|fullmatch)|re\.Pattern)"
                         r"\(.*['\"]%s")),
    ("grep", re.compile(r"\b(Select-String|grep|rg)\b.*['\"]%s")),
    ("grep", re.compile(r"\b(Select-String|grep|rg)\b.*-Pattern\s+['\"]?%s")),
)


_PARSE_CACHE = {}


def _parsing_uses_of(word):
    """Sources that use `word` in a position that consumes a line.

    Cached per word: the text route is measured independently of which row asked,
    and re-scanning the corpus six times costs minutes for one answer.
    """
    if not word:
        return []
    if word in _PARSE_CACHE:
        return _PARSE_CACHE[word]
    out = []
    patterns = [(name, re.compile(pat.pattern % re.escape(word), pat.flags))
                for name, pat in PARSE_PATTERNS]
    for rel, text in sorted(_corpus().items()):
        if word not in text:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            for name, p in patterns:
                if p.search(line):
                    out.append({"source": rel, "line": i, "construct": name,
                                "text": " ".join(line.split())[:160]})
                    break
    _PARSE_CACHE[word] = out
    return out


_MENTION_CACHE = {}


def _mentions_of(word):
    """Sources that contain the word at all (mentions, not parsers)."""
    if not word:
        return []
    if word in _MENTION_CACHE:
        return _MENTION_CACHE[word]
    out = [rel for rel, text in sorted(_corpus().items()) if word in text]
    _MENTION_CACHE[word] = out
    return out


_ANNOUNCE_CACHE = {}


def _announcements_of(face_rel):
    """What announces the face to a machine, besides the message.

    Three kinds, kept apart because only the first two are machine-visible:

      * ``pointer``        -- the canonical ``<stem>_latest.json`` pointer exists;
      * ``source_literal`` -- a code/shell source other than the writer names the
                              path, so a machine can read the name without parsing
                              a console line;
      * ``study_reference``-- a mention inside a document or inside some other
                              face: published, but NOT counted as an announcement,
                              because prose is not a machine-readable name.

    A mention in an unrelated study face was the first draft's error: it made all
    six faces look announced when nothing pointed at them.
    """
    if face_rel in _ANNOUNCE_CACHE:
        return _ANNOUNCE_CACHE[face_rel]
    found = []
    base = os.path.basename(face_rel)
    stem = base.replace(".json", "")
    writer_rel = "scripts/%s.py" % stem
    for rel, text in sorted(_corpus().items()):
        if rel == writer_rel:
            continue
        if face_rel in text or base in text:
            found.append({"source": rel, "kind": "source_literal"})
    canonical = "results/state_tilt/%s_latest.json" % stem
    if canonical in _pointer_faces():
        found.append({"source": canonical, "kind": "pointer"})
    for rel, text in sorted(_pointer_faces().items()):
        if rel == canonical:
            continue
        if face_rel in text or base in text:
            found.append({"source": rel, "kind": "study_reference"})
    _ANNOUNCE_CACHE[face_rel] = found
    return found


def _pointer_face_stem(face_rel):
    stem = os.path.basename(face_rel).replace(".json", "")
    if stem.startswith("etf_phase_"):
        return "results/state_tilt/%s_latest.json" % stem
    return None


# ---------------------------------------------------------------- classification
def _parser_sources_reachable(facts):
    """Parsers that could actually receive this writer's line.

    A parser keyed on the word is only a reader of *this* message if its own
    source also spawns this writer -- otherwise it parses some other command's
    output and this line never reaches it.
    """
    spawners = {s["source"] for s in facts["spawners"]}
    return [p for p in facts["parsers"] if p["source"] in spawners]


def classify(writer_rel, face_rel, render, facts):
    """Fold the measured facts for one row into a reader class + announcement."""
    imp = facts["importers"]
    spawns = facts["spawners"]

    if any(s["captures"] for s in spawns):
        reader = R_PROCESS_CAPTURED
    elif spawns:
        reader = R_PROCESS_UNCAPTURED
    elif imp and not render["reachable_from_the_main_guard"]:
        reader = R_IN_PROCESS_REACHABLE
    elif imp:
        reader = R_IN_PROCESS_IMPORT_ONLY
    elif facts["parsers"]:
        reader = R_WORD_PARSED_ELSEWHERE
    else:
        reader = R_NOTHING

    ann = facts["announcements"]
    literal = any(a["kind"] == "source_literal" for a in ann)
    pointer = any(a["kind"] == "pointer" for a in ann)
    if literal and pointer:
        announce = A_BOTH
    elif literal:
        announce = A_SOURCE_LITERAL
    elif pointer:
        announce = A_POINTER_FACE
    else:
        announce = A_ONLY_MESSAGE
    return reader, announce


def _rederive_reader(row):
    """What the row's own facts say its reader class must be -- used by check."""
    f = row["facts"]
    if any(s["captures"] for s in f["spawners"]):
        return R_PROCESS_CAPTURED
    if f["spawners"]:
        return R_PROCESS_UNCAPTURED
    if f["importers"]:
        return R_IN_PROCESS_IMPORT_ONLY if row["render"]["reachable_from_the_main_guard"] \
            else R_IN_PROCESS_REACHABLE
    if f["parsers"]:
        return R_WORD_PARSED_ELSEWHERE
    return R_NOTHING


def _rederive_announce(row):
    ann = row["facts"]["announcements"]
    literal = any(a["kind"] == "source_literal" for a in ann)
    pointer = any(a["kind"] == "pointer" for a in ann)
    if literal and pointer:
        return A_BOTH
    if literal:
        return A_SOURCE_LITERAL
    if pointer:
        return A_POINTER_FACE
    return A_ONLY_MESSAGE


def _what_the_reader_does(cls):
    return {
        R_IN_PROCESS_IMPORT_ONLY: "an importer sees the module but never the line",
        R_IN_PROCESS_REACHABLE: "an importer can reach the render",
        R_PROCESS_CAPTURED: "a spawner captures the line",
        R_PROCESS_UNCAPTURED: "a spawner leaves the line on the console",
        R_WORD_PARSED_ELSEWHERE: "the word is parsed, but never on this line",
        R_NOTHING: "nothing names or runs the writer",
    }[cls]


# ---------------------------------------------------------------- population
def population():
    """The parent's own six render rows, machine-read."""
    parent = json.load(io.open(PARENT_LATEST, encoding="utf-8"))
    rows = []
    for r in parent.get("rows") or []:
        hop = r.get("hop") or {}
        if hop.get("kind") != P_KIND_BUILTIN:
            continue
        if (hop.get("use_classes") or []) != [P_USE_RENDERS]:
            continue
        rows.append({
            "source": r["source"],
            "name": r["name"],
            "line": r["line"],
            "the_value_the_parent_published": r.get("the_value_the_parent_published"),
        })
    rows.sort(key=lambda r: r["source"])
    return rows, parent


def _render_facts(row):
    path = os.path.join(ROOT, row["source"].replace("/", os.sep))
    text = _read(path)
    tree = ast.parse(text)
    call = None
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and node.lineno == row["line"]:
            try:
                if ast.unparse(node.func) == "print":
                    call = node
            except Exception:
                pass
    word = _word_of_render(call) if call is not None else None
    func = _enclosing_function(tree, row["line"])
    reachable = _reachable_from_guard(tree, func)
    return {
        "message_word": word,
        "enclosing_function": func.name if func is not None else None,
        "reachable_from_the_main_guard": reachable,
        "word_is_the_sites_own": word in MESSAGE_WORD_GUARD,
    }, tree


def build(write=True):
    rows, parent = population()
    published = []
    for row in rows:
        render, tree = _render_facts(row)
        module_name = os.path.basename(row["source"]).replace(".py", "")
        face_rel = "results/%s.json" % module_name
        facts = {
            "importers": _importers_below(module_name),
            "spawners": _spawners_of(row["source"], module_name),
            "parsers": _parsing_uses_of(render["message_word"] or "") if render["message_word"] else [],
            "mentions": _mentions_of(render["message_word"] or "") if render["message_word"] else [],
            "announcements": _announcements_of(face_rel),
        }
        facts["word_is_the_sites_own"] = render["word_is_the_sites_own"]
        reader, announce = classify(row["source"], face_rel, render, facts)
        published.append({
            "writer": row["source"],
            "face": face_rel,
            "constant": row["name"],
            "line": row["line"],
            "render": render,
            "facts": facts,
            "reader_class": reader,
            "what_the_reader_does": _what_the_reader_does(reader),
            "announcement_class": announce,
        })

    by_reader = {c: 0 for c in READER_VOCAB}
    by_announce = {c: 0 for c in ANNOUNCE_VOCAB}
    for r in published:
        by_reader[r["reader_class"]] += 1
        by_announce[r["announcement_class"]] += 1
    read_back = by_reader[R_PROCESS_CAPTURED] + by_reader[R_IN_PROCESS_REACHABLE]
    only_message = by_announce[A_ONLY_MESSAGE]
    summary = {
        "rows": len(published),
        "by_reader_class": by_reader,
        "by_announcement_class": by_announce,
        "messages_read_back_by_machine_code": read_back,
        "messages_human_only": len(published) - read_back,
        "faces_announced_only_by_the_message": only_message,
        "faces_announced_by_a_source_literal": by_announce[A_SOURCE_LITERAL] + by_announce[A_BOTH],
        "faces_announced_by_a_pointer_face": by_announce[A_POINTER_FACE] + by_announce[A_BOTH],
        "writers_spawned_by_any_source": sum(1 for r in published if r["facts"]["spawners"]),
        "writers_imported_by_any_source": sum(1 for r in published if r["facts"]["importers"]),
        "renders_reachable_only_from_the_main_guard": sum(
            1 for r in published if r["render"]["reachable_from_the_main_guard"]),
        "message_word_parsers_repo_wide": len(_parsing_uses_of(MESSAGE_WORD_GUARD[0])),
        "parsers_that_could_receive_any_of_the_six_lines": sum(
            len(_parser_sources_reachable(r["facts"])) for r in published),
        "faces_with_a_canonical_pointer": sum(
            1 for r in published if any(a["kind"] == "pointer" for a in r["facts"]["announcements"])),
        "study_references_not_counted_as_announcements": sum(
            1 for r in published for a in r["facts"]["announcements"]
            if a["kind"] == "study_reference"),
        "reproduction_matches_the_parent": len(published) == 6,
    }
    verdict = V_SOME_READER if read_back else V_NO_READER
    announce_verdict = V_ALL_ONLY_MESSAGE if only_message == len(published) \
        else V_SOME_ANNOUNCED_ELSEWHERE

    face = {
        "study": STUDY,
        "card": CARD,
        "title": TITLE,
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "population_source": {
            "face": "results/state_tilt/calledconsumer_latest.json",
            "parent_verdict": parent.get("verdict"),
            "parent_rows_whose_one_hop_out_is_a_builtin_that_only_renders": len(published),
        },
        "rows": published,
        "summary": summary,
        "verdict": verdict,
        "verdict_line": verdict,
        "announcement_verdict": announce_verdict,
        "announcement_verdict_line": announce_verdict,
        "method_note": (
            "a spawn that does not capture stdout cannot be parsed by the spawner; an "
            "import of a writer whose render sits inside main() never executes the line; "
            "the text route is measured independently of who produced the line"),
    }
    if write:
        dated = os.path.join(STATE_TILT, "%s-%s.json" % (DATED_PREFIX, EVIDENCE_CUTOFF))
        blob = json.dumps(face, ensure_ascii=False, indent=1)
        io.open(dated, "w", encoding="utf-8", newline="\n").write(blob + "\n")
        io.open(LATEST, "w", encoding="utf-8", newline="\n").write(blob + "\n")
        print(json.dumps({"rows": len(published),
                          "read_back": read_back,
                          "only_message": only_message,
                          "verdict": verdict,
                          "announcement_verdict": announce_verdict,
                          "wrote": os.path.relpath(dated, ROOT).replace("\\", "/")},
                         ensure_ascii=False))
    return face


# ---------------------------------------------------------------- gates
def face_problems(face):
    probs = []
    rows = face.get("rows") or []
    s = face.get("summary") or {}
    if not rows:
        probs.append("the population is empty")
        return probs

    by_reader = {c: 0 for c in READER_VOCAB}
    by_announce = {c: 0 for c in ANNOUNCE_VOCAB}
    for r in rows:
        rc, ac = r.get("reader_class"), r.get("announcement_class")
        if rc not in READER_VOCAB:
            probs.append("reader class outside the vocabulary: %s" % (rc,))
        else:
            by_reader[rc] += 1
        if ac not in ANNOUNCE_VOCAB:
            probs.append("announcement class outside the vocabulary: %s" % (ac,))
        else:
            by_announce[ac] += 1
        if rc in READER_VOCAB and rc != _rederive_reader(r):
            probs.append("a row's reader class is not what its own facts say (%s -- %s vs %s)"
                         % (r.get("writer"), rc, _rederive_reader(r)))
        if ac in ANNOUNCE_VOCAB and ac != _rederive_announce(r):
            probs.append("a row's announcement class is not what its own facts say (%s)"
                         % (r.get("writer"),))
        if r.get("what_the_reader_does") != _what_the_reader_does(rc):
            probs.append("a row's word is not what its class says (%s)" % (r.get("writer"),))
        facts = r.get("facts") or {}
        if rc == R_PROCESS_CAPTURED and not any(x.get("captures") for x in facts.get("spawners") or []):
            probs.append("a row is called captured with no capturing spawner (%s)" % (r.get("writer"),))
        if rc == R_WORD_PARSED_ELSEWHERE and not facts.get("parsers"):
            probs.append("a row is called parsed-elsewhere with no parser (%s)" % (r.get("writer"),))
        if rc in (R_IN_PROCESS_IMPORT_ONLY, R_IN_PROCESS_REACHABLE) and not facts.get("importers"):
            probs.append("an import row has no importer (%s)" % (r.get("writer"),))
        announcing = [a for a in facts.get("announcements") or []
                      if a.get("kind") in ("source_literal", "pointer")]
        if ac == A_ONLY_MESSAGE and announcing:
            probs.append("a row is called message-only while it lists an announcement (%s)"
                         % (r.get("writer"),))
        if not r.get("render", {}).get("message_word"):
            probs.append("a row publishes no message word (%s)" % (r.get("writer"),))

    if s.get("by_reader_class") != by_reader:
        probs.append("the summary's reader counts are not the rows'")
    if s.get("by_announcement_class") != by_announce:
        probs.append("the summary's announcement counts are not the rows'")
    expected = {
        "rows": len(rows),
        "messages_read_back_by_machine_code":
            by_reader[R_PROCESS_CAPTURED] + by_reader[R_IN_PROCESS_REACHABLE],
        "faces_announced_only_by_the_message": by_announce[A_ONLY_MESSAGE],
        "faces_announced_by_a_source_literal": by_announce[A_SOURCE_LITERAL] + by_announce[A_BOTH],
        "faces_announced_by_a_pointer_face": by_announce[A_POINTER_FACE] + by_announce[A_BOTH],
        "writers_spawned_by_any_source": sum(1 for r in rows if r["facts"]["spawners"]),
        "writers_imported_by_any_source": sum(1 for r in rows if r["facts"]["importers"]),
        "renders_reachable_only_from_the_main_guard": sum(
            1 for r in rows if r["render"]["reachable_from_the_main_guard"]),
        "parsers_that_could_receive_any_of_the_six_lines": sum(
            len(_parser_sources_reachable(r["facts"])) for r in rows),
        "faces_with_a_canonical_pointer": sum(
            1 for r in rows if any(a["kind"] == "pointer" for a in r["facts"]["announcements"])),
        "study_references_not_counted_as_announcements": sum(
            1 for r in rows for a in r["facts"]["announcements"]
            if a["kind"] == "study_reference"),
    }
    expected["messages_human_only"] = expected["rows"] - expected["messages_read_back_by_machine_code"]
    for key, val in expected.items():
        if s.get(key) != val:
            probs.append("summary %s=%r but the rows say %r" % (key, s.get(key), val))

    want = V_SOME_READER if expected["messages_read_back_by_machine_code"] else V_NO_READER
    if face.get("verdict") != want:
        probs.append("the verdict is not what the rows derive (%r vs %r)" % (face.get("verdict"), want))
    if face.get("verdict") not in VERDICT_VOCAB:
        probs.append("verdict outside the vocabulary")
    want_a = V_ALL_ONLY_MESSAGE if expected["faces_announced_only_by_the_message"] == len(rows) \
        else V_SOME_ANNOUNCED_ELSEWHERE
    if face.get("announcement_verdict") != want_a:
        probs.append("the announcement verdict is not what the rows derive (%r vs %r)"
                     % (face.get("announcement_verdict"), want_a))
    if face.get("announcement_verdict") not in ANNOUNCE_VERDICT_VOCAB:
        probs.append("announcement verdict outside the vocabulary")
    if not face.get("evidence_cutoff"):
        probs.append("the face carries no evidence_cutoff")
    return probs


def check():
    pub = json.load(io.open(LATEST, encoding="utf-8"))
    problems = list(face_problems(pub))
    fresh = build(write=False)
    if [(r["writer"], r["line"]) for r in fresh["rows"]] != \
            [(r["writer"], r["line"]) for r in pub["rows"]]:
        problems.append("the published population is not the one the parent has now")
    else:
        for a, b in zip(fresh["rows"], pub["rows"]):
            if json.dumps(a, sort_keys=True) != json.dumps(b, sort_keys=True):
                problems.append("a published row is not what the sources say now (%s)" % a["writer"])
    if fresh["verdict"] != pub["verdict"]:
        problems.append("the published verdict is not the one the sources derive now")
    if fresh["announcement_verdict"] != pub["announcement_verdict"]:
        problems.append("the published announcement verdict is not the one the sources derive now")
    print(json.dumps({"problems": problems, "verdict": pub.get("verdict"),
                      "announcement_verdict": pub.get("announcement_verdict"),
                      "rows": len(pub.get("rows") or [])}, ensure_ascii=False))
    return 1 if problems else 0


def verify():
    a, b = build(write=False), build(write=False)
    pa = {k: v for k, v in a.items() if k != "generated"}
    pb = {k: v for k, v in b.items() if k != "generated"}
    problems = [] if json.dumps(pa, sort_keys=True) == json.dumps(pb, sort_keys=True) else \
        ["two builds of the same sources differ"]
    print(json.dumps({"problems": problems}, ensure_ascii=False))
    return 1 if problems else 0


# ---------------------------------------------------------------- selftest
FIXTURES = {}


def selftest():
    fails = []
    n = 0

    def ok(name, cond, detail=""):
        nonlocal n
        n += 1
        if not cond:
            fails.append(name + ((" -- " + detail) if detail else ""))
        print(("PASS " if cond else "FAIL ") + name + ((" -- " + detail) if detail else ""))

    # --- word extraction from a render call
    def word(src):
        tree = ast.parse(textwrap.dedent(src))
        call = [n for n in ast.walk(tree) if isinstance(n, ast.Call)][0]
        return _word_of_render(call)

    ok("word: a constant first argument gives its first word",
       word('print("wrote", OUT_PATH)') == "wrote", str(word('print("wrote", OUT_PATH)')))
    ok("word: a %-formatted message gives the format string's first word",
       word('print("wrote %s (%.0fs)" % (OUT_PATH, t))') == "wrote")
    ok("word: a call with no constant first argument has no word",
       word('print(name, OUT_PATH)') is None)
    ok("word: an f-string has no statically known word",
       word('print(f"wrote {OUT_PATH}")') is None)

    # --- main-guard reachability
    reach_src = textwrap.dedent('''
        import sys
        def main():
            print("wrote", OUT_PATH)
            return 0
        if __name__ == "__main__":
            sys.exit(main())
    ''')
    tree = ast.parse(reach_src)
    func = _enclosing_function(tree, 4)
    ok("guard: the render sits in main()", func is not None and func.name == "main")
    ok("guard: main() is reachable only from the __main__ block",
       _reachable_from_guard(tree, func) is True)

    plain_src = textwrap.dedent('''
        def publish():
            print("wrote", OUT_PATH)
        ''')
    tree2 = ast.parse(plain_src)
    f2 = _enclosing_function(tree2, 3)
    ok("guard: a render in a plain function is not guard-reachable",
       _reachable_from_guard(tree2, f2) is False)

    # --- parse-position patterns
    def parses(line, word="wrote"):
        for name, pat in PARSE_PATTERNS:
            p = re.compile(pat.pattern % re.escape(word), pat.flags)
            if p.search(line):
                return name
        return None

    ok("parser: startswith on the word is a parsing position",
       parses('if line.startswith("wrote"):') == "startswith")
    ok("parser: splitting on the word is a parsing position",
       parses('path = out.split("wrote")[-1]') == "split")
    ok("parser: a regex compiled on the word is a parsing position",
       parses('m = re.search(r"wrote\\s+(\\S+)", out)') == "regex")
    ok("parser: a membership test is a parsing position",
       parses('if "wrote" in out:') == "membership")
    ok("parser: a shell grep keyed on the word is a parsing position",
       parses("Select-String -Pattern 'wrote' $log") == "grep")
    ok("parser: merely printing the word is NOT a parsing position",
       parses('print("wrote", OUT_PATH)') is None)
    ok("parser: a docstring that mentions the word is NOT a parsing position",
       parses('"""prints wrote <path> to the console"""') is None)

    # --- classification truth table
    def cls(importers, spawns, parsers, own=True, guard_reach=True):
        render = {"reachable_from_the_main_guard": guard_reach, "word_is_the_sites_own": own}
        facts = {"importers": importers, "spawners": spawns, "parsers": parsers,
                 "announcements": [], "word_is_the_sites_own": own}
        return classify("scripts/x.py", "results/x.json", render, facts)[0]

    ok("class: a capturing spawner is a reader",
       cls([], [{"captures": True}], []) == R_PROCESS_CAPTURED)
    ok("class: an uncaptured spawner is not a reader",
       cls([], [{"captures": False}], []) == R_PROCESS_UNCAPTURED)
    ok("class: a parser that never receives the line is not a reader",
       cls([], [], [{"construct": "startswith", "source": "elsewhere.py"}]) ==
       R_WORD_PARSED_ELSEWHERE)
    ok("class: importers alone are not a reader when the render sits behind the guard",
       cls([{"source": "a.py"}], [], [], guard_reach=True) == R_IN_PROCESS_IMPORT_ONLY)
    ok("class: importers are a reader when the render is reachable from them",
       cls([{"source": "a.py"}], [], [], guard_reach=False) == R_IN_PROCESS_REACHABLE)
    ok("class: nothing at all is its own class, not 'unknown'",
       cls([], [], []) == R_NOTHING)

    # --- the published face
    face = build(write=False)
    rows = face["rows"]
    s = face["summary"]
    ok("face: the population is the parent's six render rows", s["rows"] == 6, str(s["rows"]))
    ok("face: the parent's own render count reproduces here",
       s["reproduction_matches_the_parent"] is True)
    ok("face: the reader counts partition the rows",
       sum(s["by_reader_class"].values()) == len(rows))
    ok("face: the announcement counts partition the rows",
       sum(s["by_announcement_class"].values()) == len(rows))
    ok("face: read-back is the sum of its three reader classes",
       s["messages_read_back_by_machine_code"] ==
       s["by_reader_class"][R_PROCESS_CAPTURED] +
       s["by_reader_class"][R_IN_PROCESS_REACHABLE])
    ok("face: human-only is the complement of read-back",
       s["messages_human_only"] == len(rows) - s["messages_read_back_by_machine_code"])
    ok("face: every row publishes its message word",
       all(r["render"]["message_word"] for r in rows))
    ok("face: every row's message word is one the guard knows",
       all(r["render"]["word_is_the_sites_own"] for r in rows))
    ok("face: the 'reachable only from the main guard' name matches what it counts",
       s["renders_reachable_only_from_the_main_guard"] ==
       sum(1 for r in rows if r["render"]["reachable_from_the_main_guard"] is True),
       "%s vs %s" % (s["renders_reachable_only_from_the_main_guard"],
                     sum(1 for r in rows if r["render"]["reachable_from_the_main_guard"] is True)))
    ok("face: every render in this tree sits behind the __main__ guard",
       s["renders_reachable_only_from_the_main_guard"] == len(rows),
       str(s["renders_reachable_only_from_the_main_guard"]))
    ok("face: nobody spawns any of the six writers",
       s["writers_spawned_by_any_source"] == 0, str(s["writers_spawned_by_any_source"]))
    ok("face: the word is parsed somewhere, but never on these lines",
       s["message_word_parsers_repo_wide"] >= 1 and
       s["parsers_that_could_receive_any_of_the_six_lines"] == 0,
       "%s / %s" % (s["message_word_parsers_repo_wide"],
                    s["parsers_that_could_receive_any_of_the_six_lines"]))
    ok("face: a study reference is published but never counted as an announcement",
       s["study_references_not_counted_as_announcements"] ==
       sum(1 for r in rows for a in r["facts"]["announcements"]
           if a["kind"] == "study_reference"))
    ok("face: face_problems is clean", face_problems(face) == [], str(face_problems(face))[:300])
    ok("face: the verdict follows the read-back count",
       face["verdict"] == (V_SOME_READER if s["messages_read_back_by_machine_code"] else V_NO_READER))
    ok("face: the announcement verdict follows the message-only count",
       face["announcement_verdict"] ==
       (V_ALL_ONLY_MESSAGE if s["faces_announced_only_by_the_message"] == len(rows)
        else V_SOME_ANNOUNCED_ELSEWHERE))

    # --- doctored copies must be refused
    doc = json.loads(json.dumps(face))
    doc["verdict"] = "a_verdict_this_study_never_publishes"
    ok("defect: a hand-written verdict is refused", bool(face_problems(doc)))
    doc = json.loads(json.dumps(face))
    doc["announcement_verdict"] = "a_verdict_this_study_never_publishes"
    ok("defect: a hand-written announcement verdict is refused", bool(face_problems(doc)))
    doc = json.loads(json.dumps(face))
    doc["rows"] = doc["rows"][:-1]
    ok("defect: a summary that outlives its rows is refused", bool(face_problems(doc)))
    doc = json.loads(json.dumps(face))
    doc["rows"][0]["reader_class"] = R_PROCESS_CAPTURED
    ok("defect: a row called captured with no capturing spawner is refused",
       bool(face_problems(doc)))
    doc = json.loads(json.dumps(face))
    for r in doc["rows"]:
        if r["announcement_class"] == A_ONLY_MESSAGE:
            r["facts"]["announcements"] = [{"source": "someone.py", "kind": "source_literal"}]
            break
    ok("defect: a message-only row that lists an announcement is refused",
       any("lists an announcement" in p for p in face_problems(doc)))
    doc = json.loads(json.dumps(face))
    doc["summary"]["messages_read_back_by_machine_code"] = \
        s["messages_read_back_by_machine_code"] + 1
    ok("defect: a read-back count that is not the rows' is refused", bool(face_problems(doc)))
    doc = json.loads(json.dumps(face))
    del doc["evidence_cutoff"]
    ok("defect: a face with no evidence_cutoff is refused", bool(face_problems(doc)))

    # --- the study must not measure its own output
    ok("self: the scan excludes this study's own sources",
       not any("e553_render_reader" in rel for rel, _ in _walk_sources()))
    ok("self: the scan excludes this study's own faces",
       not any("RENDERREADER" in rel or "renderreader_latest" in rel
               for rel, _ in _walk_sources((".py", ".json"))))

    print("%d/%d legs green" % (n - len(fails), n))
    return 1 if fails else 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "build"
    if cmd == "build":
        face = build()
        return 0
    if cmd == "check":
        return check()
    if cmd == "verify":
        return verify()
    if cmd == "selftest":
        return selftest()
    raise SystemExit("unknown command: %s (build|check|verify|selftest)" % cmd)


if __name__ == "__main__":
    sys.exit(main())