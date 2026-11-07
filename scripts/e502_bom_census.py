"""E502 (r1530 bm-b) -- does the BOM source list change any published census row?

E495 disclosed nine sources in its scan that begin with a UTF-8 BOM and showed that one of
them (``scripts/e429_two_hop_writer.py``) makes ``ast.parse`` raise, so that source contributed
nothing to the census built on the same read.  E495 stripped the BOM for its own face and left
the rest of the corpus unpriced: every other E-series study that reuses the same reader still
reads those nine files as text that names nothing.

This study prices that.  Four arms, all static, no network:

  A. the BOM census -- which sources in the canonical scan (E491/E492/E495's shared corpus)
     begin with a BOM, and how many more exist in the full tree the per-study corpora walk;
  B. the reader census -- for every E-series module that defines ``build()``, does its reader
     remove the BOM before parsing, parse the text as it is, or never parse at all, and does
     its published payload name the sources it could not parse?
  C. exposure -- for the studies that expose a zero-argument ``corpus()``, is a BOM source
     inside that corpus?  (A study cannot be damaged by a file it never reads.)
  D. the replay -- for the exposed studies, run ``build()`` twice in a subprocess, once on the
     text as read and once with the leading BOM stripped, and diff the two payloads.  Every
     write the replay performs is backed up before it happens and restored afterwards, and the
     restoration is asserted per file.

The verdict is computed by a gate from the rows, never written by hand.

Method limits (also published in the face): a study whose ``build()`` needs an argument, or
whose payload is not a dict, is replayed as ``payload_unavailable`` rather than guessed; the
diff is structural (dotted key paths), so a re-ordered list of equal elements reads as a
change; and arm B classifies a reader by its source text, not by running it.
"""

import ast
import builtins
import glob
import hashlib
import io
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e491_latest_copier as e491

ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "results", "state_tilt")

FACE_NAME = "bomcensus_latest.json"
DATED_PREFIX = "BOMCENSUS"
DATE_STAMP = "2026-11-07"
CARD = "E502-DOES-THE-BOM-SOURCE-LIST-CHANGE-ANY-PUBLISHED-CENSUS"
STUDY = "E502_bom_census"
PARENT_CARD = "E495-WHEN-A-FACES-ONLY-VISIBLE-COMPOSERS-ARE-LEG-RUNNERS-DID-THE-DIAGNOSTIC-BECOME-THE-PUBLICATION"

SELF_EXCLUDED = ("e502_", "run_e502", "_e502")

BOM = "\ufeff"

# --- arm B: what the reader does with a leading BOM ------------------------------------
R_STRIPS = "the_reader_removes_the_bom_before_parsing"
R_RAW_PARSE = "the_reader_parses_the_text_as_it_is_read_so_a_bom_source_cannot_parse"
R_NO_PARSE = "the_study_never_parses_source_text"
R_SELF_UNPARSABLE = "the_studys_own_source_does_not_parse_even_with_the_bom_stripped"
READER_VOCAB = (R_STRIPS, R_RAW_PARSE, R_NO_PARSE, R_SELF_UNPARSABLE)

# --- arm B: does the published payload name what it could not parse --------------------
D_DISCLOSED = "the_payload_names_the_sources_it_could_not_parse"
D_SILENT = "the_payload_never_names_an_unparsed_source"
DISCLOSURE_VOCAB = (D_DISCLOSED, D_SILENT)

# --- arm C: exposure ------------------------------------------------------------------
X_IN_CORPUS = "a_bom_source_is_inside_this_studys_own_corpus"
X_OUTSIDE = "no_bom_source_is_inside_this_studys_own_corpus"
X_UNEXPOSED = "the_study_exposes_no_zero_arg_corpus_so_membership_is_unmeasured"
EXPOSURE_VOCAB = (X_IN_CORPUS, X_OUTSIDE, X_UNEXPOSED)

# --- arm D: replay outcome ------------------------------------------------------------
P_EQUAL = "stripping_the_bom_changes_nothing_in_the_payload"
P_CHANGED = "stripping_the_bom_changes_at_least_one_value_in_the_payload"
P_UNAVAILABLE = "the_payload_could_not_be_replayed"
P_UNEXPOSED = "not_replayed_because_no_bom_source_is_in_this_studys_corpus"
P_NO_PARSE = "not_replayed_because_the_study_never_parses_source_text"
REPLAY_VOCAB = (P_EQUAL, P_CHANGED, P_UNAVAILABLE, P_UNEXPOSED, P_NO_PARSE)

# --- verdicts -------------------------------------------------------------------------
V_EMPTY = "the_canonical_corpus_holds_no_bom_source"
V_UNPRICED = "no_exposed_study_could_be_replayed_so_the_census_body_stays_unpriced"
V_CHANGE = "at_least_one_published_payload_moves_when_the_bom_sources_parse"
V_NO_CHANGE = "stripping_the_bom_moves_no_published_payload_among_the_replayed_studies"
V_DISCLOSED_AT_RISK = ("the_replayed_payloads_do_not_move_but_a_study_that_parses_raw_and_"
                       "cannot_parse_a_bom_member_never_names_the_dropped_sources")
VERDICT_VOCAB = (V_EMPTY, V_UNPRICED, V_CHANGE, V_NO_CHANGE, V_DISCLOSED_AT_RISK)

DISCLOSURE_WORDS = ("do_not_parse", "does_not_parse", "unparseable", "unparsed",
                    "cannot_be_parsed", "not_parseable", "parse_failed")
SKIP_DIRS = frozenset((".git", "__pycache__", "node_modules", "legacy", "Money02",
                       ".codely-cli", "media"))
MAX_READ_BYTES = 2 * 1024 * 1024
REPLAY_TIMEOUT = 900
# Why 900 and not 240: measured on 2026-11-07 r1531, the slowest arm is
# e429_two_hop_writer at 231.9s raw / 237.0s stripped -- 97% of the previous 240s
# budget.  A 240s build priced that study as "timeout after 240s" (unmeasured) while a
# build 40 minutes earlier, on a quieter box, priced it as changed; the budget was
# deciding the reading.  The budget is published in the face with that evidence.
REPLAY_BUDGET_NOTE = (
    "slowest arm observed 2026-11-07: e429_two_hop_writer raw 231.9s / stripped 237.0s, "
    "i.e. 99% of the previous 240s budget; the budget was raised to 900s so the reading "
    "is not set by it, and the earlier 240s reading is published beside this one"
)
MAX_DIFF_ROWS = 40


def _now():
    import datetime
    return datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()


def _load_json(path):
    with io.open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _rel(path, root=None):
    root = root or ROOT
    return os.path.relpath(path, root).replace(os.sep, "/")


def read_text(path):
    """The shared reader this corpus actually uses (E451): utf-8, BOM kept."""
    try:
        with io.open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return ""


def sha16_bytes(data):
    return hashlib.sha256(data).hexdigest()[:16]


# ------------------------------------------------------------------ arm A: the BOM census
def full_tree_sources(root=None):
    """Every .py a per-study corpus can walk: the tree minus the skip directories."""
    root = root or ROOT
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for name in sorted(filenames):
            if not name.endswith(".py"):
                continue
            full = os.path.join(dirpath, name)
            rel = _rel(full, root)
            if any(os.path.basename(rel).startswith(p) for p in SELF_EXCLUDED):
                continue
            out.append(rel)
    return sorted(out)


def canonical_scan(root=None):
    """E491's canonical scan (the corpus E492/E495 share), minus this study's own sources."""
    root = root or ROOT
    out = []
    for rel, text in e491.scan_sources(root):
        if any(os.path.basename(rel).startswith(p) for p in SELF_EXCLUDED):
            continue
        out.append((rel, text))
    return out


def bom_census(root=None):
    root = root or ROOT
    canonical = canonical_scan(root)
    canon_bom = [rel for rel, text in canonical if text.startswith(BOM)]
    tree = full_tree_sources(root)
    tree_bom = []
    for rel in tree:
        try:
            if os.path.getsize(os.path.join(root, rel)) > MAX_READ_BYTES:
                continue
        except OSError:
            continue
        if read_text(os.path.join(root, rel)).startswith(BOM):
            tree_bom.append(rel)
    return {
        "canonical_sources": len(canonical),
        "canonical_bom": canon_bom,
        "tree_sources": len(tree),
        "tree_bom": tree_bom,
        "bom_outside_the_canonical_scan": [r for r in tree_bom if r not in canon_bom],
    }


def bom_source_row(rel, root=None):
    root = root or ROOT
    path = os.path.join(root, rel)
    text = read_text(path)
    size = os.path.getsize(path)
    stripped = text[1:] if text.startswith(BOM) else text
    raw_ok = _parses(text)
    strip_ok = _parses(stripped)
    return {
        "source": rel,
        "bytes": size,
        "sha16": sha16_bytes(io.open(path, "rb").read()),
        "string_literals": _string_literals(stripped),
        "parses_as_read": raw_ok,
        "parses_without_the_bom": strip_ok,
    }


def _parses(text):
    try:
        ast.parse(text)
        return True
    except (SyntaxError, ValueError):
        return False


def _string_literals(text):
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError):
        return 0
    return sum(1 for n in ast.walk(tree) if isinstance(n, ast.Constant)
               and isinstance(n.value, str))


# ------------------------------------------------------------------ arm B: reader census
def study_modules(root=None):
    root = root or ROOT
    out = []
    for path in sorted(glob.glob(os.path.join(root, "scripts", "e*.py"))):
        base = os.path.basename(path)
        if len(base) < 4 or not base[1:2].isdigit():
            continue
        if any(base.startswith(p) for p in SELF_EXCLUDED):
            continue
        out.append(path)
    return out


def study_shape(path):
    text = read_text(path)
    stripped = text[1:] if text.startswith(BOM) else text
    try:
        tree = ast.parse(stripped)
    except (SyntaxError, ValueError):
        return None, text, R_SELF_UNPARSABLE
    funcs = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    if "build" not in funcs:
        return None, text, None
    return tree, text, None


def reader_class(text):
    if "ast.parse" not in text:
        return R_NO_PARSE
    if "ufeff" in text or "utf-8-sig" in text or BOM in text:
        return R_STRIPS
    return R_RAW_PARSE


def has_zero_arg_corpus(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "corpus":
            if not node.args.args and not node.args.kwonlyargs:
                return True
    return False


def disclosure_of(payload):
    """Does this payload name an unparsed source anywhere?"""
    hits = []

    def walk(node, path):
        if isinstance(node, dict):
            for key, value in node.items():
                key_l = str(key).lower()
                if any(word in key_l for word in DISCLOSURE_WORDS):
                    hits.append("%s.%s" % (path, key) if path else str(key))
                walk(value, "%s.%s" % (path, key) if path else str(key))
        elif isinstance(node, list):
            for i, value in enumerate(node):
                walk(value, "%s[%d]" % (path, i))
        elif isinstance(node, str):
            low = node.lower()
            if any(word in low for word in DISCLOSURE_WORDS):
                hits.append(path)

    walk(payload, "")
    return sorted(set(hits))


def face_of_module(module_name, root=None):
    """The published face a study writes, by its own FACE_NAME constant then by search."""
    root = root or ROOT
    try:
        mod = __import__(module_name)
    except Exception:
        return None
    name = getattr(mod, "FACE_NAME", None)
    if isinstance(name, str) and name.endswith(".json"):
        for path in glob.glob(os.path.join(root, "results", "**", name), recursive=True):
            return _rel(path, root)
    return None


# ------------------------------------------------------------------ arm C: exposure
def corpus_of(module_name):
    """The study's own corpus, or None when it exposes no zero-argument corpus()."""
    try:
        mod = __import__(module_name)
    except Exception:
        return None
    fn = getattr(mod, "corpus", None)
    if not callable(fn):
        return None
    try:
        members = fn()
    except Exception:
        return None
    out = []
    for member in members or []:
        out.append(str(member).replace(os.sep, "/"))
    return sorted(set(out))


# ------------------------------------------------------------------ arm D: the replay
def _strip_open(real_open, path):
    text = real_open(path, "r", encoding="utf-8", errors="replace").read()
    return text[1:] if text.startswith(BOM) else text


def replay_worker(module_name, strip, out_path):
    """Run one study's build() once, restore every file it wrote, and dump the payload."""
    backups = {}
    touched = []
    guard = {"inside": False}
    real_open = builtins.open

    def hook(event, args):
        if guard["inside"] or event != "open":
            return
        try:
            path, mode = args[0], args[1]
        except (IndexError, TypeError):
            return
        if not isinstance(path, str) or not isinstance(mode, str):
            return
        if not any(ch in mode for ch in "wax+"):
            return
        if path in backups:
            return
        guard["inside"] = True
        try:
            if os.path.isfile(path):
                with real_open(path, "rb") as fh:
                    backups[path] = fh.read()
            else:
                backups[path] = None
            touched.append(path)
        except OSError:
            pass
        finally:
            guard["inside"] = False

    sys.addaudithook(hook)

    if strip:
        import io as _io
        _real = builtins.open

        def patched(file, mode="r", *a, **kw):
            if (isinstance(file, str) and file.endswith(".py")
                    and "b" not in mode and all(c not in mode for c in "wax+")):
                return io.StringIO(_strip_open(_real, file))
            return _real(file, mode, *a, **kw)

        builtins.open = patched
        _io.open = patched

    payload = None
    error = None
    try:
        mod = __import__(module_name)
        build = getattr(mod, "build")
        try:
            payload = build()
        except TypeError as exc:
            error = "build_needs_arguments: %s" % exc
    except Exception as exc:                      # noqa: BLE001 - reported, not swallowed
        error = "%s: %s" % (type(exc).__name__, exc)
    finally:
        builtins.open = real_open
        try:
            import io as _io2
            _io2.open = real_open
        except Exception:
            pass
        restored = []
        for path, body in backups.items():
            try:
                now = None
                if os.path.isfile(path):
                    with real_open(path, "rb") as fh:
                        now = fh.read()
                if body is None:
                    if os.path.isfile(path):
                        os.remove(path)
                    restored.append({"path": path, "action": "removed"})
                elif now != body:
                    with real_open(path, "wb") as fh:
                        fh.write(body)
                    restored.append({"path": path, "action": "rewritten"})
                else:
                    restored.append({"path": path, "action": "unchanged"})
            except OSError as exc:
                restored.append({"path": path, "action": "restore_failed: %s" % exc})

    if not isinstance(payload, dict):
        error = error or ("the_payload_is_%s_not_a_dict" % type(payload).__name__)
        payload = None
    body = {"payload": payload, "error": error,
            "writes": [_rel(p) for p in touched], "restored": restored}
    with io.open(out_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(body, fh, ensure_ascii=False, sort_keys=True)
    return 0


def diff_payloads(left, right, path="", out=None):
    """Structural diff: every dotted path whose value differs between two payloads."""
    out = out if out is not None else []
    if len(out) >= MAX_DIFF_ROWS:
        return out
    if type(left) is not type(right):
        out.append({"path": path or "<root>", "left": _short(left), "right": _short(right),
                    "kind": "type"})
        return out
    if isinstance(left, dict):
        for key in sorted(set(left) | set(right), key=str):
            sub = "%s.%s" % (path, key) if path else str(key)
            if key not in left:
                out.append({"path": sub, "left": None, "right": _short(right[key]),
                            "kind": "added"})
            elif key not in right:
                out.append({"path": sub, "left": _short(left[key]), "right": None,
                            "kind": "removed"})
            else:
                diff_payloads(left[key], right[key], sub, out)
            if len(out) >= MAX_DIFF_ROWS:
                break
        return out
    if isinstance(left, list):
        if len(left) != len(right):
            out.append({"path": path or "<root>", "left": "len=%d" % len(left),
                        "right": "len=%d" % len(right), "kind": "length"})
        for i, (a, b) in enumerate(zip(left, right)):
            diff_payloads(a, b, "%s[%d]" % (path, i), out)
            if len(out) >= MAX_DIFF_ROWS:
                break
        return out
    if left != right:
        out.append({"path": path or "<root>", "left": _short(left), "right": _short(right),
                    "kind": "value"})
    return out


def _short(value):
    text = json.dumps(value, ensure_ascii=False, sort_keys=True) if not isinstance(
        value, str) else value
    return text[:120]


def run_replay(module_name):
    """Replay a study twice in a subprocess: as read, and with the leading BOM stripped."""
    results = {}
    for strip in (0, 1):
        out = os.path.join(OUTDIR, "_e502_replay_%s_%d.json" % (module_name, strip))
        cmd = [sys.executable, os.path.abspath(__file__), "_replay", module_name,
               str(strip), out]
        try:
            proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, timeout=REPLAY_TIMEOUT)
        except subprocess.TimeoutExpired:
            results[strip] = {"payload": None, "error": "timeout after %ds" % REPLAY_TIMEOUT,
                              "writes": [], "restored": []}
            continue
        if not os.path.isfile(out):
            results[strip] = {"payload": None,
                              "error": "worker wrote no payload (rc=%d) %s"
                                       % (proc.returncode,
                                          (proc.stderr or b"")[-300:].decode("utf-8", "replace")),
                              "writes": [], "restored": []}
            continue
        try:
            results[strip] = _load_json(out)
        finally:
            try:
                os.remove(out)
            except OSError:
                pass
    return results


# ------------------------------------------------------------------ the population
def measure_study(path, boms, root=None):
    root = root or ROOT
    base = os.path.basename(path)
    module = base[:-3]
    tree, text, self_error = study_shape(path)
    if tree is None and self_error is None:
        return None       # the module defines no build(): outside this population
    if self_error:
        return {"module": module, "source": _rel(path, root),
                "reader_class": self_error, "disclosure_class": None,
                "exposure": X_UNEXPOSED, "replay": P_UNAVAILABLE,
                "corpus_members": None, "corpus_exposed": False,
                "bom_members_in_corpus": [], "payload": None,
                "rows_changed": None, "changed_keys": [], "replay_error": self_error,
                "writes_during_replay": [], "restore_actions": []}
    reader = reader_class(text)
    face_rel = face_of_module(module, root)
    payload = None
    if face_rel:
        try:
            payload = _load_json(os.path.join(root, face_rel))
        except (OSError, ValueError):
            payload = None
    disc_hits = disclosure_of(payload) if payload is not None else []
    if payload is None:
        disclosure = D_SILENT
        disc_note = "the_study_publishes_no_readable_face_so_this_arm_is_unmeasured"
    else:
        disclosure = D_DISCLOSED if disc_hits else D_SILENT
        disc_note = None

    members = corpus_of(module) if has_zero_arg_corpus(tree) else None
    if members is None:
        exposure = X_UNEXPOSED
        hits = []
    else:
        hits = [b for b in boms if b in members]
        exposure = X_IN_CORPUS if hits else X_OUTSIDE

    row = {"module": module, "source": _rel(path, root), "face": face_rel,
           "reader_class": reader, "disclosure_class": disclosure,
           "disclosure_note": disc_note, "disclosure_fields": disc_hits[:12],
           "exposure": exposure, "corpus_exposed": members is not None,
           "corpus_members": len(members) if members is not None else None,
           "bom_members_in_corpus": hits}

    if reader == R_NO_PARSE:
        row.update({"replay": P_NO_PARSE, "rows_changed": None, "changed_keys": [],
                    "replay_error": None, "writes_during_replay": [],
                    "restore_actions": []})
        return row
    if exposure != X_IN_CORPUS:
        row.update({"replay": P_UNEXPOSED, "rows_changed": None, "changed_keys": [],
                    "replay_error": None, "writes_during_replay": [],
                    "restore_actions": []})
        return row

    runs = run_replay(module)
    raw, strip = runs.get(0) or {}, runs.get(1) or {}
    if not raw.get("payload") or not strip.get("payload"):
        row.update({"replay": P_UNAVAILABLE, "rows_changed": None, "changed_keys": [],
                    "replay_error": raw.get("error") or strip.get("error"),
                    "writes_during_replay": sorted(set(raw.get("writes") or [])
                                                   | set(strip.get("writes") or [])),
                    "restore_actions": (raw.get("restored") or []),
                    "restore_actions_strip": (strip.get("restored") or [])})
        return row
    changes = diff_payloads(raw["payload"], strip["payload"])
    row.update({"replay": P_CHANGED if changes else P_EQUAL,
                "rows_changed": len(changes), "changed_keys": changes,
                "replay_error": None,
                "writes_during_replay": sorted(set(raw.get("writes") or [])
                                               | set(strip.get("writes") or [])),
                "restore_actions": (raw.get("restored") or []),
                "restore_actions_strip": (strip.get("restored") or [])})
    return row


def population(root=None):
    root = root or ROOT
    census = bom_census(root)
    boms = census["canonical_bom"]
    tris = census["tree_bom"]
    rows = []
    for path in study_modules(root):
        row = measure_study(path, tris, root)
        if row is not None:
            rows.append(row)
    return census, rows


def summary_of(rows, census):
    reader_counts = {}
    replay_counts = {}
    exposure_counts = {}
    for row in rows:
        reader_counts[row.get("reader_class")] = reader_counts.get(row.get("reader_class"), 0) + 1
        replay_counts[row.get("replay")] = replay_counts.get(row.get("replay"), 0) + 1
        exposure_counts[row.get("exposure")] = exposure_counts.get(row.get("exposure"), 0) + 1
    replayed = [r for r in rows if r.get("replay") in (P_EQUAL, P_CHANGED)]
    changed = [r for r in replayed if r.get("replay") == P_CHANGED]
    at_risk = [r for r in rows
               if r.get("reader_class") == R_RAW_PARSE
               and r.get("exposure") == X_IN_CORPUS
               and r.get("disclosure_class") == D_SILENT]
    return {
        "canonical_sources": census.get("canonical_sources", 0),
        "canonical_bom_sources": len(census.get("canonical_bom") or ()),
        "tree_bom_sources": len(census.get("tree_bom") or ()),
        "bom_outside_the_canonical_scan": len(census.get("bom_outside_the_canonical_scan") or ()),
        "studies_with_build": len(rows),
        "reader_class_counts": reader_counts,
        "exposure_counts": exposure_counts,
        "replay_counts": replay_counts,
        "studies_replayed": len(replayed),
        "studies_whose_payload_changed": len(changed),
        "rows_changed_total": sum(r.get("rows_changed") or 0 for r in changed),
        "studies_that_parse_raw_with_a_bom_member_and_name_nothing": len(at_risk),
        "at_risk_modules": sorted(r["module"] for r in at_risk),
        "replays_that_wrote_a_file": sum(1 for r in rows
                                         if r.get("writes_during_replay")),
        "restores_that_failed": sum(1 for r in rows
                                    for a in (r.get("restore_actions") or [])
                                    if str(a.get("action", "")).startswith("restore_failed")),
        "evidence_cutoff": DATE_STAMP,
    }


def _verdict(summary):
    if not summary["canonical_bom_sources"] and not summary["tree_bom_sources"]:
        return V_EMPTY
    if summary["studies_whose_payload_changed"]:
        return V_CHANGE
    if not summary["studies_replayed"]:
        return V_UNPRICED
    if summary["studies_that_parse_raw_with_a_bom_member_and_name_nothing"]:
        return V_DISCLOSED_AT_RISK
    return V_NO_CHANGE


def build(root=None, write=True):
    root = root or ROOT
    census, rows = population(root)
    summary = summary_of(rows, census)
    face = {
        "study": STUDY,
        "card": CARD,
        "parent_card": PARENT_CARD,
        "title": ("Which published census rows change when the 9 BOM-prefixed sources are "
                  "parsed with the BOM stripped?"),
        "evidence_cutoff": DATE_STAMP,
        "generated": _now(),
        "reader_vocab": list(READER_VOCAB),
        "disclosure_vocab": list(DISCLOSURE_VOCAB),
        "exposure_vocab": list(EXPOSURE_VOCAB),
        "replay_vocab": list(REPLAY_VOCAB),
        "verdict_vocab": list(VERDICT_VOCAB),
        "method_limits": [
            "arm B classifies a reader by its source text (ufeff / utf-8-sig / ast.parse), "
            "not by running it",
            "exposure is measurable only for a study that exposes a zero-argument corpus(); "
            "a study whose corpus needs arguments is published as unexposed, never as safe",
            "the replay runs the study's own build() once per arm in a subprocess with "
            "REPLAY_TIMEOUT=%ds; a timeout or a non-dict payload is payload_unavailable"
            % REPLAY_TIMEOUT,
            "every write during a replay is backed up before the open and restored after, and "
            "each restoration is published per file (E493 family)",
            "the structural diff reports dotted paths, so a re-ordered list of equal elements "
            "reads as a change; the diff is capped at %d rows" % MAX_DIFF_ROWS,
            "arm A publishes both the canonical scan (E491/E492/E495) and the full tree, "
            "because a per-study corpus walks more files than the canonical scan",
        ],
        "bom_census": census,
        "replay_budget": {
            "timeout_seconds": REPLAY_TIMEOUT,
            "note": REPLAY_BUDGET_NOTE,
            "superseded_budget_seconds": 240,
            "superseded_budget_reading": {
                "generated": "2026-11-07T17:34:10+08:00",
                "studies_replayed": 6,
                "studies_whose_payload_changed": 2,
                "rows_changed_total": 41,
                "unmeasured_for_timeout": ["e429_two_hop_writer"],
            },
            "evidence_cutoff": DATE_STAMP,
        },
        "population_source": {
            "arm_a_canonical": {
                "rule": "the shared canonical source scan of E491/E492/E495 over this repo, "
                        "minus this study's own sources",
                "sources": summary["canonical_sources"],
                "bom_sources": summary["canonical_bom_sources"],
            },
            "arm_a_full_tree": {
                "rule": "every source the tree scan walks, so a per-study corpus is not "
                        "under-counted by the canonical filters",
                "bom_sources": summary["tree_bom_sources"],
                "bom_sources_outside_the_canonical_scan":
                    summary["bom_outside_the_canonical_scan"],
            },
            "arm_b_study_population": {
                "rule": "every in-repo module under scripts/ that defines build(); a module "
                        "without build() is outside the population and is never counted as safe",
                "studies_with_build": summary["studies_with_build"],
                "studies_replayed": summary["studies_replayed"],
            },
            "evidence_cutoff": DATE_STAMP,
        },
        "summary": summary,
        "verdict": _verdict(summary),
        "rows": rows,
    }
    if write:
        _write(face, root)
    return face


def _write(face, root=None):
    root = root or ROOT
    outdir = os.path.join(root, "results", "state_tilt")
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    body = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
    for name in (FACE_NAME, "%s-%s.json" % (DATED_PREFIX, DATE_STAMP)):
        with io.open(os.path.join(outdir, name), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body + "\n")


def row_problems(face):
    """Gate: the verdict and the summary must re-derive from the rows."""
    problems = []
    rows = face.get("rows") or []
    summary = face.get("summary") or {}
    census = face.get("bom_census") or {}
    fresh = summary_of(rows, {
        "canonical_sources": summary.get("canonical_sources"),
        "canonical_bom": [None] * (summary.get("canonical_bom_sources") or 0),
        "tree_bom": [None] * (summary.get("tree_bom_sources") or 0),
        "bom_outside_the_canonical_scan": [None] * (summary.get("bom_outside_the_canonical_scan") or 0),
    })
    for key, value in fresh.items():
        if key in ("canonical_sources", "canonical_bom_sources", "tree_bom_sources"):
            continue
        if summary.get(key) != value:
            problems.append("summary.%s=%r does not re-derive from the rows (%r)"
                            % (key, summary.get(key), value))
    if face.get("verdict") != _verdict(fresh):
        problems.append("verdict=%r does not re-derive from the rows (%r)"
                        % (face.get("verdict"), _verdict(fresh)))
    if census.get("canonical_bom") is not None:
        if len(census.get("canonical_bom") or []) != summary.get("canonical_bom_sources"):
            problems.append("bom_census.canonical_bom does not match summary.canonical_bom_sources")
    pop = face.get("population_source") or {}
    for block, key, skey in (
            ("arm_a_canonical", "sources", "canonical_sources"),
            ("arm_a_canonical", "bom_sources", "canonical_bom_sources"),
            ("arm_a_full_tree", "bom_sources", "tree_bom_sources"),
            ("arm_a_full_tree", "bom_sources_outside_the_canonical_scan",
             "bom_outside_the_canonical_scan"),
            ("arm_b_study_population", "studies_with_build", "studies_with_build"),
            ("arm_b_study_population", "studies_replayed", "studies_replayed")):
        have = (pop.get(block) or {}).get(key)
        if have != summary.get(skey):
            problems.append(
                "population_source.%s.%s=%r does not re-derive from summary.%s (%r)"
                % (block, key, have, skey, summary.get(skey)))
    for row in rows:
        module = row.get("module")
        if row.get("reader_class") not in READER_VOCAB:
            problems.append("%s: reader_class %r outside the vocabulary"
                            % (module, row.get("reader_class")))
        if row.get("replay") not in REPLAY_VOCAB:
            problems.append("%s: replay %r outside the vocabulary" % (module, row.get("replay")))
        if row.get("exposure") not in EXPOSURE_VOCAB:
            problems.append("%s: exposure %r outside the vocabulary"
                            % (module, row.get("exposure")))
        if row.get("replay") == P_CHANGED and not row.get("changed_keys"):
            problems.append("%s: claimed changed with no changed key" % module)
        if row.get("replay") == P_EQUAL and row.get("rows_changed") not in (0, None):
            problems.append("%s: claimed equal with rows_changed=%r"
                            % (module, row.get("rows_changed")))
        if row.get("reader_class") == R_STRIPS and row.get("exposure") == X_IN_CORPUS:
            parsed = [b for b in (row.get("bom_members_in_corpus") or [])]
            if parsed and row.get("replay") == P_UNAVAILABLE:
                problems.append("%s: strips the BOM yet the replay is unavailable" % module)
        for action in (row.get("restore_actions") or []):
            if str(action.get("action", "")).startswith("restore_failed"):
                problems.append("%s: %s was not restored" % (module, action.get("path")))
    return problems


def check(face=None, root=None):
    root = root or ROOT
    face = face or _load_json(os.path.join(root, "results", "state_tilt", FACE_NAME))
    problems = row_problems(face)
    print("check problems=%r" % (problems,))
    return 0 if not problems else 1


def verify(root=None):
    root = root or ROOT
    face = build(root, write=False)
    problems = row_problems(face)
    print("verify problems=%r" % (problems,))
    print("verdict=%s" % face["verdict"])
    return 0 if not problems else 1


# ---------------------------------------------------------------- selftest

RAW_FIXTURE = '''import ast, io
def build():
    return {}
def corpus():
    return []
tree = ast.parse(io.open("x.py").read())
'''

STRIP_FIXTURE = '''import ast, io
def build():
    return {}
text = io.open("x.py").read()
if text.startswith("\\ufeff"):
    text = text[1:]
tree = ast.parse(text)
'''

NO_PARSE_FIXTURE = '''import io
def build():
    return {"n": 1}
'''


def selftest():
    legs = []

    def leg(name, fn):
        try:
            ok, note = fn()
        except Exception as exc:                   # noqa: BLE001
            ok, note = False, "%s: %s" % (type(exc).__name__, exc)
        legs.append((name, ok, note))

    def leg_reader_raw():
        return reader_class(RAW_FIXTURE) == R_RAW_PARSE, reader_class(RAW_FIXTURE)

    def leg_reader_strips():
        return reader_class(STRIP_FIXTURE) == R_STRIPS, reader_class(STRIP_FIXTURE)

    def leg_reader_no_parse():
        return reader_class(NO_PARSE_FIXTURE) == R_NO_PARSE, reader_class(NO_PARSE_FIXTURE)

    def leg_parses_with_and_without():
        body = "def build():\n    return {}\n"
        return (_parses(BOM + body) is False and _parses(body) is True,
                "raw=%r stripped=%r" % (_parses(BOM + body), _parses(body)))

    def leg_disclosure_found():
        hits = disclosure_of({"sources": {"do_not_parse": [{"source": "a.py"}]}})
        return bool(hits), hits

    def leg_disclosure_silent():
        return disclosure_of({"rows": [{"n": 1}]}) == [], "no field"

    def leg_diff_value():
        d = diff_payloads({"a": 1}, {"a": 2})
        return len(d) == 1 and d[0]["path"] == "a" and d[0]["kind"] == "value", d

    def leg_diff_added_removed():
        d = diff_payloads({"a": 1}, {"b": 1})
        kinds = sorted(x["kind"] for x in d)
        return kinds == ["added", "removed"], d

    def leg_diff_equal():
        return diff_payloads({"a": [1, 2]}, {"a": [1, 2]}) == [], "equal"

    def leg_diff_nested():
        d = diff_payloads({"a": {"b": {"c": 1}}}, {"a": {"b": {"c": 2}}})
        return len(d) == 1 and d[0]["path"] == "a.b.c", d

    def leg_diff_length():
        d = diff_payloads({"a": [1]}, {"a": [1, 2]})
        return any(x["kind"] == "length" for x in d), d

    def leg_verdict_empty():
        census = {"canonical_bom": [], "tree_bom": []}
        return _verdict(summary_of([], census)) == V_EMPTY, V_EMPTY

    def leg_verdict_unpriced():
        census = {"canonical_bom": ["a.py", "b.py"], "tree_bom": ["a.py", "b.py"]}
        rows = [{"reader_class": R_RAW_PARSE, "exposure": X_OUTSIDE,
                 "replay": P_UNEXPOSED, "disclosure_class": D_SILENT}]
        return _verdict(summary_of(rows, census)) == V_UNPRICED, "unpriced"

    def leg_verdict_change():
        census = {"canonical_bom": ["a.py", "b.py"], "tree_bom": ["a.py", "b.py"]}
        rows = [{"reader_class": R_RAW_PARSE, "exposure": X_IN_CORPUS,
                 "replay": P_CHANGED, "rows_changed": 3, "changed_keys": [{"path": "a"}],
                 "disclosure_class": D_SILENT, "module": "e999"}]
        return _verdict(summary_of(rows, census)) == V_CHANGE, "change"

    def leg_verdict_no_change_but_unnamed():
        census = {"canonical_bom": ["a.py", "b.py"], "tree_bom": ["a.py", "b.py"]}
        rows = [{"reader_class": R_RAW_PARSE, "exposure": X_IN_CORPUS,
                 "replay": P_EQUAL, "rows_changed": 0, "changed_keys": [],
                 "disclosure_class": D_SILENT, "module": "e999"}]
        return _verdict(summary_of(rows, census)) == V_DISCLOSED_AT_RISK, "at risk"

    def leg_verdict_no_change_disclosed():
        census = {"canonical_bom": ["a.py", "b.py"], "tree_bom": ["a.py", "b.py"]}
        rows = [{"reader_class": R_RAW_PARSE, "exposure": X_IN_CORPUS,
                 "replay": P_EQUAL, "rows_changed": 0, "changed_keys": [],
                 "disclosure_class": D_DISCLOSED, "module": "e999"}]
        return _verdict(summary_of(rows, census)) == V_NO_CHANGE, "no change"

    def leg_gate_catches_carried_summary():
        face = {"rows": [], "summary": {"studies_with_build": 5},
                "verdict": V_EMPTY, "bom_census": {}}
        return bool(row_problems(face)), row_problems(face)[:2]

    def leg_gate_catches_changed_without_keys():
        face = {"rows": [{"module": "e999", "reader_class": R_RAW_PARSE,
                          "exposure": X_IN_CORPUS, "replay": P_CHANGED,
                          "changed_keys": []}],
                "summary": {}, "verdict": V_CHANGE, "bom_census": {}}
        return any("no changed key" in p for p in row_problems(face)), "caught"

    def leg_gate_catches_failed_restore():
        face = {"rows": [{"module": "e999", "reader_class": R_NO_PARSE,
                          "exposure": X_OUTSIDE, "replay": P_NO_PARSE,
                          "restore_actions": [{"path": "x", "action": "restore_failed: x"}]}],
                "summary": {}, "verdict": V_EMPTY, "bom_census": {}}
        return any("was not restored" in p for p in row_problems(face)), "caught"

    def leg_gate_catches_carried_population():
        face = {"rows": [],
                "summary": {"canonical_sources": 3, "canonical_bom_sources": 0,
                            "tree_bom_sources": 0, "bom_outside_the_canonical_scan": 0,
                            "studies_with_build": 0, "studies_replayed": 0},
                "verdict": V_EMPTY, "bom_census": {},
                "population_source": {
                    "arm_a_canonical": {"sources": 4, "bom_sources": 0},
                    "arm_a_full_tree": {"bom_sources": 0,
                                        "bom_sources_outside_the_canonical_scan": 0},
                    "arm_b_study_population": {"studies_with_build": 0,
                                               "studies_replayed": 0}}}
        return any("population_source" in p for p in row_problems(face)), "caught"

    def leg_strip_shim():
        import tempfile
        tmp = tempfile.mkdtemp()
        path = os.path.join(tmp, "bom_source.py")
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(BOM + "x = 1\n")
        text = _strip_open(builtins.open, path)
        return text == "x = 1\n", repr(text)

    def leg_self_excluded():
        names = [os.path.basename(p) for p in study_modules(ROOT)]
        return not any(n.startswith("e502_") for n in names), "self excluded"

    def leg_module_without_build_is_outside():
        import tempfile
        tmp = tempfile.mkdtemp()
        path = os.path.join(tmp, "e999_nobuild.py")
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("def other():\n    return 1\n")
        tree, _text, err = study_shape(path)
        return (tree is None and err is None), "no build() -> outside the population"

    def leg_bom_constant():
        return BOM == "\ufeff" and BOM.encode("utf-8") == b"\xef\xbb\xbf", "utf-8 bom"

    leg("reader: parses raw", leg_reader_raw)
    leg("reader: strips the bom", leg_reader_strips)
    leg("reader: never parses", leg_reader_no_parse)
    leg("bom makes ast.parse raise and stripping fixes it", leg_parses_with_and_without)
    leg("disclosure: a field names an unparsed source", leg_disclosure_found)
    leg("disclosure: a payload without the field is silent", leg_disclosure_silent)
    leg("diff: a changed value", leg_diff_value)
    leg("diff: added and removed keys", leg_diff_added_removed)
    leg("diff: equal payloads", leg_diff_equal)
    leg("diff: a nested path", leg_diff_nested)
    leg("diff: a length change", leg_diff_length)
    leg("verdict: no bom source", leg_verdict_empty)
    leg("verdict: nothing replayed", leg_verdict_unpriced)
    leg("verdict: a payload moves", leg_verdict_change)
    leg("verdict: equal but the drop is unnamed", leg_verdict_no_change_but_unnamed)
    leg("verdict: equal and disclosed", leg_verdict_no_change_disclosed)
    leg("gate: a carried summary is caught", leg_gate_catches_carried_summary)
    leg("gate: changed with no key is caught", leg_gate_catches_changed_without_keys)
    leg("gate: a failed restore is caught", leg_gate_catches_failed_restore)
    leg("gate: a carried population_source is caught", leg_gate_catches_carried_population)
    leg("replay: the strip shim removes one leading bom", leg_strip_shim)
    leg("scan excludes this study", leg_self_excluded)
    leg("a module without build() is outside the population", leg_module_without_build_is_outside)
    leg("the bom constant is the utf-8 bom", leg_bom_constant)

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
                          "verdict": face["verdict"], "summary": face["summary"]},
                         ensure_ascii=False, indent=1))
        return 0
    if cmd == "check":
        return check()
    if cmd == "verify":
        return verify()
    if cmd == "selftest":
        return selftest()
    if cmd == "_replay" and len(argv) >= 4:
        return replay_worker(argv[1], argv[2] == "1", argv[3])
    print("usage: e502_bom_census.py [run|check|verify|selftest]", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())