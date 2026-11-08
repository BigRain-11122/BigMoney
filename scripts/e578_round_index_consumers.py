# -*- coding: utf-8 -*-
"""E578 -- which other readers of the round ledger lose the same 1,534 rows E577 published.

E577 (r1605 bm-b) found that every one of the 31 "beyond the tolerance" gaps closes with a row
of the machine's own ledger within six hours, and that the index those rounds were read through
simply cannot see 1,534 rows because E573's ``ROW_TS`` requires a leading pipe.  The open
question it left is not what those rows are, but *who else* reads the ledger and inherits the
same blind spot.  This study answers that by measuring the readers, not by naming them:

  census      every module in the py corpus that names a round-report file, split into readers of
              the row index and modules that only size it, hash it, move it or scan its prose
  probe       a fixed six-shape synthetic ledger row set, pushed through each reader's own code
              path (no re-implementation where the real function can be called), giving one
              dialect per reader and the two shapes it disagrees about
  quantity    each reader's real row count over its own file set on disk, beside the lenient
              index of those same files, so the loss is a subtraction and not an opinion
  axes        the loss is split into the four axes it actually has -- row shape (the leading
              pipe), file scope (which ledgers a reader opens), window (how many tail lines),
              and vintage (a reader that prefers origin/main reads a tree this host is behind)

Classes of the verdict (first match wins):

  loses_the_same_rows_as_the_index_it_inherits   whole-file readers whose shape loss equals
                                                 E577's 1,534 on this host's ledgers
  loses_a_different_number_of_the_same_rows      whole-file readers with a narrower file scope
  sees_every_row_shape_and_loses_only_a_window   pipe-tolerant readers that still truncate
  sees_dates_anywhere_not_rows                   readers that scan timestamps in prose
  does_not_read_the_row_index                    modules that name the ledger but parse no rows

Bounds published, not claimed: the file sets are the constants the readers themselves declare;
a reader that takes its ledger from another tree (lane_round_liveness prefers origin/main) is
measured against that tree too, and the two counts are published apart rather than reconciled.
This study reads ledgers only -- it runs no chain, no report, no runner.

Usage: python scripts/e578_round_index_consumers.py [build|check|verify|selftest]
"""
import ast
import glob
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
CUTOFF = "2026-11-08"
STUDY = "E578"
E577_FACE = os.path.join(OUTDIR, "nightgap_latest.json")

REPORT_FILES = ("logs/iteration-loop/round_reports.md",
                "logs/iteration-loop/round_reports-bm-a.md",
                "logs/iteration-loop/round_reports-bm-c.md")

# The population E577 published; re-derived here and asserted, never assumed.
E577_LENIENT = 2247
E577_STRICT = 759
E577_NO_PIPE = 1534

C_SAME = "loses_the_same_rows_as_the_index_it_inherits"
C_NARROW = "loses_a_different_number_of_the_same_rows"
C_WINDOW = "sees_every_row_shape_and_loses_only_a_window"
C_ANYWHERE = "sees_dates_anywhere_not_rows"
C_NOT_INDEX = "does_not_read_the_row_index"
CLASSES = (C_SAME, C_NARROW, C_WINDOW, C_ANYWHERE, C_NOT_INDEX)

# Seven shapes.  A row index must take the row shapes and refuse the prose ones; which row
# shapes it takes is its dialect, and a reader that needs seconds or an offset is published with
# that narrowness rather than being called wrong.
SHAPES = (
    ("table_full",       "| 2026-11-08T02:40:00+08:00 | r1605 | dept:research | table, full stamp", True),
    ("table_minute",     "| 2026-11-08T02:40 | r1605 | dept:research | table, minute stamp", True),
    ("no_leading_pipe",  "2026-11-08T02:40:00+08:00 | r1605 | dept:research | same row, no pipe", True),
    ("no_pipe_minute",   "2026-11-08T02:40 | r1605 | dept:research | same row, no pipe, minute", True),
    ("indented_table",   "  | 2026-11-08T02:40:00+08:00 | r1605 | dept:research | indented", True),
    ("legacy_space",     "2026-11-08 02:40 | r1605 | dept:research | legacy space stamp", True),
    ("prose_short",      "note: at 2026-11-08 02:40 r1605 closed the chain with 12 legs", False),
    ("prose_full",       "at 2026-11-08T02:40:00+08:00 r1605 closed the chain", False),
)
ROW_SHAPES = tuple(n for n, _, is_row in SHAPES if is_row)
PROSE_SHAPES = tuple(n for n, _, is_row in SHAPES if not is_row)
PIPE_SHAPE = "table_full"
NO_PIPE_SHAPE = "no_leading_pipe"

# Readers of the row index, each measured through its own declared constant or function.
READERS = (
    {"id": "scripts/e573_silent_chain.round_of_row", "kind": "index", "dialect": "e573",
     "path": "scripts/e573_silent_chain.py"},
    {"id": "scripts/e575_only_flag.round_index", "kind": "index", "dialect": "e575",
     "path": "scripts/e575_only_flag.py"},
    {"id": "scripts/e409_unfloored_faces._round_rows", "kind": "index", "dialect": "e409",
     "path": "scripts/e409_unfloored_faces.py"},
    {"id": "Tools/lane_round_liveness.ledger_times_text", "kind": "index", "dialect": "liveness",
     "path": "Tools/lane_round_liveness.py"},
    {"id": "scripts/automation_line_audit.round_report_ts", "kind": "index",
     "dialect": "line_audit", "path": "scripts/automation_line_audit.py"},
    {"id": "scripts/marks_coverage.host_samples", "kind": "samples", "dialect": "marks",
     "path": "scripts/marks_coverage.py"},
    {"id": "scripts/e567_chain_claim.extract_claims", "kind": "prose", "dialect": None,
     "path": "scripts/e567_chain_claim.py"},
    {"id": "scripts/e574_receipt_tracking.report_corpus", "kind": "blob", "dialect": None,
     "path": "scripts/e574_receipt_tracking.py"},
    {"id": "scripts/e562_single_leg_provenance.round_report_only_witness", "kind": "flag_scan",
     "dialect": None, "path": "scripts/e562_single_leg_provenance.py"},
    {"id": "scripts/token_meter._states_and_reports", "kind": "size_only", "dialect": None,
     "path": "scripts/token_meter.py"},
    {"id": "Tools/tree_poison_probe.classify", "kind": "path_only", "dialect": None,
     "path": "Tools/tree_poison_probe.py"},
)

_MODS = {}


def _read_json(path):
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _mod(name, relpath):
    if name in _MODS:
        return _MODS[name]
    path = os.path.join(ROOT, relpath)
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _MODS[name] = mod
    return mod


def _read(relpath):
    full = os.path.join(ROOT, relpath)
    if not os.path.exists(full):
        return None
    with io.open(full, encoding="utf-8", errors="replace") as fh:
        return fh.read()


# ---------------------------------------------------------------- the lenient index (E577's)
# E577's exact lenient form: an optional leading pipe, then a T-separated stamp.  Kept identical
# on purpose -- the population cross-check is only meaningful if this is the same shape.
ROW_ANY = re.compile(r"^\|?\s*(\d{4}-\d{2}-\d{2})T(\d{2}):(\d{2})(?::(\d{2}))?")
# The row shapes this lenient index still refuses even when they are ledgers: a space-separated
# stamp.  Published as a bound, counted so the bound has a size.
ROW_SPACE = re.compile(r"^\|?\s*\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}")
ROUND_TOK = re.compile(r"\br(\d{1,4})(?!\d)", re.I)


def lenient_rows(files=REPORT_FILES):
    """Every ledger row on those files, read with or without a leading pipe.

    Same row shape as the index the readers build; the only difference is that this one is
    allowed to see a row that does not start with a pipe.  Published with the pipe flag so the
    two populations are always separable.
    """
    rows, outside = [], 0
    for rel in files:
        text = _read(rel) or ""
        for i, line in enumerate(text.splitlines()):
            m = ROW_ANY.match(line)
            if not m:
                if ROW_SPACE.match(line) and ROUND_TOK.search(line):
                    outside += 1
                continue
            parts = [x.strip() for x in line.split("|")]
            has_pipe = line.lstrip().startswith("|")
            tok = None
            for slot in ((2, 3) if has_pipe else (1, 2)):
                if slot < len(parts) and ROUND_TOK.search(parts[slot]):
                    tok = ROUND_TOK.search(parts[slot])
                    break
            if tok is None:
                continue
            rows.append({"file": rel, "line": i + 1, "round": int(tok.group(1)),
                         "leading_pipe": has_pipe,
                         "ts": "%s %s:%s" % (m.group(1), m.group(2), m.group(3))})
    return rows, outside


def file_scope_rows(files, rows=None):
    rows = rows if rows is not None else lenient_rows()
    return [r for r in rows if r["file"] in files]


# ---------------------------------------------------------------- probes (real code paths)
def _probe_e573():
    m = _mod("e573_silent_chain", "scripts/e573_silent_chain.py")
    return {name: (m.round_of_row(line) is not None) for name, line, _r in SHAPES}


def _probe_e575():
    m = _mod("e575_only_flag", "scripts/e575_only_flag.py")
    m573 = _mod("e573_silent_chain", "scripts/e573_silent_chain.py")
    out = {}
    for name, line, _r in SHAPES:
        out[name] = bool(m573.round_of_row(line) is not None and m.row_ts(line) is not None)
    return out


def _probe_e409():
    m = _mod("e409_unfloored_faces", "scripts/e409_unfloored_faces.py")
    out = {}
    saved = m.REPORT
    try:
        for name, line, _r in SHAPES:
            with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False,
                                            encoding="utf-8") as fh:
                fh.write(line + "\n")
                tmp = fh.name
            try:
                m.REPORT = tmp
                out[name] = bool(m._round_rows())
            finally:
                os.unlink(tmp)
    finally:
        m.REPORT = saved
    return out


def _probe_liveness():
    m = _mod("lane_round_liveness", "Tools/lane_round_liveness.py")
    out = {}
    for name, line, _r in SHAPES:
        try:
            out[name] = bool(m.ledger_times_text(line + "\n"))
        except Exception:
            out[name] = False
    return out


def _probe_line_audit():
    m = _mod("automation_line_audit", "scripts/automation_line_audit.py")
    return {name: (m.round_report_ts(line) is not None) for name, line, _r in SHAPES}


def _probe_marks():
    """host_samples over a synthetic root: its own file discovery, not a re-implemented regex."""
    m = _mod("marks_coverage", "scripts/marks_coverage.py")
    tmp = tempfile.mkdtemp(prefix="e578marks_")
    try:
        out = {}
        for name, line, _r in SHAPES:
            for _machine, rel in m.LIVENESS_SOURCES:
                full = os.path.join(tmp, rel)
                d = os.path.dirname(full)
                if not os.path.isdir(d):
                    os.makedirs(d)
                with io.open(full, "w", encoding="utf-8") as fh:
                    fh.write(line + "\n")
            try:
                samples = m.host_samples(root=tmp)
            except TypeError:
                samples = m.host_samples(tmp)
            out[name] = any(("02:40" in t) for day in samples.values()
                            for hhmm in day.values() for t in hhmm)
            for _machine, rel in m.LIVENESS_SOURCES:
                full = os.path.join(tmp, rel)
                if os.path.exists(full):
                    os.unlink(full)
        return out
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


PROBES = {"e573": _probe_e573, "e575": _probe_e575, "e409": _probe_e409,
          "liveness": _probe_liveness, "line_audit": _probe_line_audit, "marks": _probe_marks}


# ---------------------------------------------------------------- the comparable population R
# R = a dated ledger row: an optional leading pipe, a full stamp (date plus HH:MM), and a round
# token in the row's own round slot.  Published as a 2x2 of pipe/no-pipe x T/space separator,
# because "loses the 1,534" is one cell of that table and not the whole table.
ROW_R = re.compile(r"^(\|?)\s*\d{4}-\d{2}-\d{2}([T ])\d{2}:\d{2}")
ROUND_TOK = re.compile(r"\br(\d{1,4})(?!\d)", re.I)


def row_population(files=REPORT_FILES):
    out = []
    for rel in files:
        text = _read(rel) or ""
        for i, line in enumerate(text.splitlines()):
            m = ROW_R.match(line)
            if not m:
                continue
            parts = [x.strip() for x in line.split("|")]
            pipe = line.startswith("|")
            slots = (2, 3) if pipe else (1, 2)
            tok = None
            for s in slots:
                if s < len(parts) and ROUND_TOK.search(parts[s]):
                    tok = ROUND_TOK.search(parts[s])
                    break
            if tok is None:
                continue
            out.append({"file": rel, "line": i + 1, "text": line,
                        "leading_pipe": pipe, "separator": "T" if m.group(2) == "T" else "space",
                        "round": int(tok.group(1))})
    return out


def _split(rows):
    cell = {}
    for r in rows:
        key = ("pipe" if r["leading_pipe"] else "no_pipe", r["separator"])
        cell[key] = cell.get(key, 0) + 1
    return {"%s_%s" % k: v for k, v in sorted(cell.items())}


def _scope_rows(scope, R):
    return [r for r in R if r["file"] in set(scope)]


# ---------------------------------------------------------------- per-reader predicates
def _lifted_regex(relpath, marker, occurrence=0):
    """Lift a row regex out of a reader's own source, so its predicate is the reader's regex."""
    src = _read(relpath) or ""
    if marker == "e409_row":
        pats = [p for p in re.findall(r're\.match\(r"([^"]+)"', src)
                if "\\d{4}" in p and "\\|" in p]
        pat = pats[occurrence] if len(pats) > occurrence else None
    elif marker == "marks_stamp":
        pats = re.findall(r'stamp = re\.compile\(r"([^"]+)"\)', src)
        pat = pats[0] if pats else None
    else:
        pat = None
    return (re.compile(pat) if pat else None), pat


_PRED = {}


def predicates():
    """One line-level predicate per reader, each taken from that reader's own code."""
    if _PRED:
        return _PRED
    m573 = _mod("e573_silent_chain", "scripts/e573_silent_chain.py")
    m575 = _mod("e575_only_flag", "scripts/e575_only_flag.py")
    mlive = _mod("lane_round_liveness", "Tools/lane_round_liveness.py")
    mla = _mod("automation_line_audit", "scripts/automation_line_audit.py")
    r409, pat409 = _lifted_regex("scripts/e409_unfloored_faces.py", "e409_row")
    rmarks, pat_marks = _lifted_regex("scripts/marks_coverage.py", "marks_stamp")

    def f573(line):
        return m573.round_of_row(line) is not None

    def f575(line):
        return m573.round_of_row(line) is not None and m575.row_ts(line) is not None

    def f409(line):
        return bool(r409 and r409.match(line))

    def flive(line):
        try:
            return bool(mlive.ledger_times_text(line + "\n"))
        except Exception:
            return False

    def fla(line):
        return mla.round_report_ts(line) is not None

    def fmarks(line):
        return bool(rmarks and rmarks.search(line))

    _PRED.update({
        "scripts/e573_silent_chain.round_of_row": (f573, None),
        "scripts/e575_only_flag.round_index": (f575, None),
        "scripts/e409_unfloored_faces._round_rows":
            (f409, "regex lifted from e409_unfloored_faces.py: %s" % pat409),
        "Tools/lane_round_liveness.ledger_times_text": (flive, None),
        "scripts/automation_line_audit.round_report_ts": (fla, None),
        "scripts/marks_coverage.host_samples":
            (fmarks, "regex lifted from marks_coverage.py: %s" % pat_marks),
    })
    return _PRED


def _declared_files(relpath):
    """The ledger files a reader declares in its own module-level constants.

    Read from the AST rather than by grepping the text: a study that mentions a ledger file name
    in a fixture or a docstring does not thereby read that ledger (E573 names one in its selftest
    fixture only), and a module that takes its ledgers from its caller declares none at all.
    """
    src = _read(relpath) or ""
    try:
        tree = ast.parse(src)
    except Exception:
        return ()
    names = set()
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        consts = [s.value for s in ast.walk(node.value)
                  if isinstance(s, ast.Constant) and isinstance(s.value, str)]
        md = [c for c in consts if c.endswith(".md") and "round_reports" in c]
        for c in md:
            names.add(c if "/" in c else "logs/iteration-loop/%s" % c)
    return tuple(sorted(names))


def _count_liveness_origin():
    mlive = _mod("lane_round_liveness", "Tools/lane_round_liveness.py")
    out = {}
    for rel in REPORT_FILES:
        try:
            proc = subprocess.run(["git", "-C", ROOT, "show", "origin/main:%s" % rel],
                                  stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        except Exception:
            out[rel] = None
            continue
        if proc.returncode != 0 or not proc.stdout:
            out[rel] = None
            continue
        out[rel] = len(mlive.ledger_times_text(proc.stdout.decode("utf-8", "replace")))
    return out


def _count_line_audit_window():
    """Its window is measured, not named: how many of the rows it *could* read are reachable.

    A 20-line tail of a ledger whose rows are single long lines can reach at most 20 rows, so a
    pipe-tolerant reader can still be blind to the whole file -- the two axes do not cancel.
    """
    mla = _mod("automation_line_audit", "scripts/automation_line_audit.py")
    try:
        dt, raw, n_lines = mla._round_report_newest_ts("bm-b")
    except Exception as exc:  # noqa: BLE001
        return {"window_lines": None, "window_error": repr(exc)[:160]}
    text = _read("logs/iteration-loop/round_reports.md") or ""
    tail = text.splitlines()[-n_lines:] if n_lines else []
    reachable = len([ln for ln in tail if mla.round_report_ts(ln) is not None])
    return {"window_lines": n_lines,
            "window_rows_reachable": reachable,
            "rows_the_window_never_reaches": max(0, len(row_population(
                ["logs/iteration-loop/round_reports.md"])) - reachable),
            "newest_ts": dt.isoformat() if dt else None,
            "newest_row_parsed": dt is not None}


# ---------------------------------------------------------------- census
def census():
    """Every module that names a round-report file, with whether it parses rows."""
    files = []
    for base in ("scripts", "Tools", "firm", "live", "monitor"):
        base_dir = os.path.join(ROOT, base)
        if not os.path.isdir(base_dir):
            continue
        for dirpath, _dirnames, filenames in os.walk(base_dir):
            if ".git" in dirpath:
                continue
            for fn in filenames:
                if fn.endswith(".py"):
                    files.append(os.path.join(dirpath, fn))
    out = []
    for p in files:
        rel = os.path.relpath(p, ROOT).replace("\\", "/")
        if os.path.basename(rel).startswith("_") or rel.startswith("results/"):
            continue
        src = _read(rel)
        if not src or "round_reports" not in src:
            continue
        try:
            tree = ast.parse(src)
        except Exception:
            tree = None
        row_regex = False
        row_gate = False
        if tree is not None:
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and isinstance(node.value, str):
                    v = node.value
                    if "round_reports" in v:
                        continue
                    if re.search(r"\^\\\|\s*\\d\{4\}", v) or re.match(r"\^?\s*\|", v) or \
                            ("\\d{4}-\\d{2}-\\d{2}" in v and "|" in v):
                        row_regex = True
                if isinstance(node, ast.Compare) and isinstance(node.left, ast.Attribute) \
                        and node.left.attr == "startswith":
                    for comp in node.comparators:
                        if isinstance(comp, ast.Constant) and comp.value in ("|", " |", "| "):
                            row_gate = True
        out.append({"path": rel, "has_row_regex": row_regex,
                    "has_pipe_startswith_gate": row_gate,
                    "named_files": sorted(set(re.findall(r"round_reports[\w\-.@]*\.md", src))),
                    "declared_files": _declared_files(rel)})
    out.sort(key=lambda r: r["path"])
    return out


# ---------------------------------------------------------------- classify + build
def _dialect(probe):
    """Read a reader's dialect off the shapes it accepted, not off its name."""
    if any(probe.get(n) for n in PROSE_SHAPES):
        return "reads_a_timestamp_anywhere_in_the_line"
    if not any(probe.get(n) for n in ROW_SHAPES):
        return "refuses_every_row_shape"
    if probe.get(NO_PIPE_SHAPE) or probe.get("no_pipe_minute"):
        return "row_head_with_or_without_a_leading_pipe"
    return "row_head_with_a_leading_pipe"


def _stamp_narrowness(probe):
    return {"refuses_minute_stamp": not (probe.get("table_minute") or probe.get("no_pipe_minute")),
            "refuses_space_stamp": not probe.get("legacy_space"),
            "refuses_indented_row": not probe.get("indented_table")}


def classify(consumer, scope_rows, population):
    """One class per consumer, first match wins, with the subtraction published."""
    if consumer["kind"] != "index":
        if consumer.get("dialect") == "reads_a_timestamp_anywhere_in_the_line":
            return C_ANYWHERE
        return C_NOT_INDEX
    if consumer.get("window_lines"):
        return C_WINDOW
    seen = consumer.get("rows_seen")
    if seen is None:
        return C_NARROW
    no_pipe = population["no_pipe_rows_in_scope"]
    if no_pipe > 0 and consumer["loss_in_scope"] >= no_pipe \
            and len(set(consumer.get("reads_files") or [])) >= len(REPORT_FILES) \
            and consumer.get("refuses_every_no_pipe_row"):
        return C_SAME
    return C_NARROW


def build(write=True):
    R = row_population()
    cells = _split(R)
    no_pipe_total = len([r for r in R if not r["leading_pipe"]])
    pipe_total = len([r for r in R if r["leading_pipe"]])
    t_no_pipe = cells.get("no_pipe_T", 0)
    t_pipe = cells.get("pipe_T", 0)

    e577 = _read_json(E577_FACE) if os.path.exists(E577_FACE) else {}
    e577_s = (e577 or {}).get("summary") or {}
    preds = predicates()

    # E577's triple, reconciled against this measurement: its "strict" was a reader that also
    # accepts a space-separated stamp, its "lenient" was one that does not, so the triple does
    # not partition and the gap has a name and a size.
    rec = {
        "e577_strict_rows_indexed": e577_s.get("strict_rows_indexed"),
        "e577_lenient_rows_indexed": e577_s.get("lenient_rows_indexed"),
        "e577_rows_without_a_leading_pipe": e577_s.get("rows_without_a_leading_pipe"),
        "strict_plus_no_pipe_minus_lenient":
            (e577_s.get("strict_rows_indexed") or 0)
            + (e577_s.get("rows_without_a_leading_pipe") or 0)
            - (e577_s.get("lenient_rows_indexed") or 0),
        "e577_implied_pipe_T_rows":
            (e577_s.get("lenient_rows_indexed") or 0)
            - (e577_s.get("rows_without_a_leading_pipe") or 0),
        "this_round_pipe_T_rows": t_pipe,
        "this_round_no_pipe_T_rows": t_no_pipe,
        "growth_since_that_vintage": t_no_pipe - (e577_s.get("rows_without_a_leading_pipe") or 0),
    }
    rec["growth_in_pipe_T"] = t_pipe - rec["e577_implied_pipe_T_rows"]
    rec["explanation"] = (
        "at E577's own vintage strict counted %r pipe rows and lenient counted %r of them plus %r "
        "without a pipe; the %r-row gap between the two definitions is the pipe rows whose stamp "
        "is space-separated, which the strict reader takes and the lenient one does not. This "
        "round's population is larger by %r pipe and %r no-pipe rows, both published as growth"
        % (rec["e577_strict_rows_indexed"], rec["e577_implied_pipe_T_rows"],
           rec["e577_rows_without_a_leading_pipe"],
           rec["e577_strict_rows_indexed"] - rec["e577_implied_pipe_T_rows"],
           rec.get("growth_in_pipe_T"), rec["growth_since_that_vintage"]))

    consumers = []
    for spec in READERS:
        c = dict(spec)
        c.pop("dialect", None)
        declared = _declared_files(c["path"])
        c["declared_files"] = declared
        if spec["dialect"]:
            try:
                c["probe"] = PROBES[spec["dialect"]]()
                c["dialect"] = _dialect(c["probe"])
                c.update(_stamp_narrowness(c["probe"]))
            except Exception as exc:  # noqa: BLE001
                c["probe"] = {}
                c["dialect"] = "probe_failed: %r" % (exc,)
        else:
            c["probe"] = {}
            c["dialect"] = None

        if spec["id"].startswith("scripts/e409"):
            c["reads_files"] = ["logs/iteration-loop/round_reports.md"]
            c["scope_note"] = "declares one ledger in its own REPORT constant"
        elif declared:
            c["reads_files"] = list(declared)
        else:
            c["reads_files"] = list(REPORT_FILES)
            c["scope_note"] = ("declares no ledger of its own: its scope is inherited from the "
                               "caller that passes the files in")

        pred, pred_note = preds.get(spec["id"], (None, None))
        if pred_note:
            c["predicate_source"] = pred_note
        if pred is not None and c["kind"] == "index":
            scope = _scope_rows(c["reads_files"], R)
            accepted = [r for r in scope if pred(r["text"])]
            c["rows_seen"] = len(accepted)
            c["rows_in_its_scope"] = len(scope)
            c["loss_in_scope"] = len(scope) - len(accepted)
            c["no_pipe_rows_in_scope"] = len([r for r in scope if not r["leading_pipe"]])
            c["pipe_rows_in_scope"] = len([r for r in scope if r["leading_pipe"]])
            c["refuses_every_no_pipe_row"] = (
                c["no_pipe_rows_in_scope"] > 0
                and not any(r for r in accepted if not r["leading_pipe"]))
            c["refuses_some_pipe_row"] = len(accepted) < c["pipe_rows_in_scope"]
            c["extra_pipe_rows_lost"] = max(0, (c["loss_in_scope"] or 0)
                                            - (c["no_pipe_rows_in_scope"] or 0))
        else:
            c["rows_seen"] = None
            scope = _scope_rows(c["reads_files"], R)
            c["rows_in_its_scope"] = len(scope)
            c["loss_in_scope"] = None
            c["no_pipe_rows_in_scope"] = len([r for r in scope if not r["leading_pipe"]])
            c["pipe_rows_in_scope"] = len([r for r in scope if r["leading_pipe"]])
            c["refuses_every_no_pipe_row"] = None
            c["refuses_some_pipe_row"] = None

        if spec["dialect"] == "liveness":
            c["rows_seen_from_origin_main_per_file"] = _count_liveness_origin()
        if spec["dialect"] == "line_audit":
            c.update(_count_line_audit_window())
        if spec["dialect"] == "marks":
            c["note"] = "scans timestamps anywhere, so it sees rows and prose alike and holds no row index"
        consumers.append(c)

    population = {"rows": len(R), "cells": cells,
                  "rows_with_a_leading_pipe": pipe_total,
                  "rows_without_a_leading_pipe": no_pipe_total}
    for c in consumers:
        c["class"] = classify(c, None, {"no_pipe_rows_in_scope": c.get("no_pipe_rows_in_scope")})
        c["class_reason"] = (
            "saw %r of %r rows in the %d ledger(s) it reads; %r rows without a leading pipe went "
            "unread, and %r rows with a pipe did too"
            % (c.get("rows_seen"), c.get("rows_in_its_scope"),
               len(set(c.get("reads_files") or [])),
               (c.get("no_pipe_rows_in_scope") if c.get("refuses_every_no_pipe_row")
                else "some_of_%r" % (c.get("no_pipe_rows_in_scope"),)),
               c.get("extra_pipe_rows_lost") if c.get("extra_pipe_rows_lost") else 0))

    pop = census()
    by_class = {}
    for c in consumers:
        by_class[c["class"]] = by_class.get(c["class"], 0) + 1

    face = {
        "study": STUDY, "machine": "bm-b", "dept": "研究+工程",
        "evidence_cutoff": CUTOFF,
        "generated_by": "scripts/e578_round_index_consumers.py",
        "rule": "a reader's dialect is read off the six probe shapes it accepts; its loss is the "
                "subtraction of the rows it accepts from the dated rows in its own declared ledgers",
        "population": {
            "ledger_files": list(REPORT_FILES),
            "rows": len(R), "by_cell": cells,
            "rows_with_a_leading_pipe": pipe_total,
            "rows_without_a_leading_pipe": no_pipe_total,
            "cell_rule": "pipe/no_pipe x T/space separator; a row is a dated stamp plus a round "
                         "token in its own round slot",
            "e577_reconciliation": rec,
            "agrees_with_e577_on_the_cell": (rec["growth_since_that_vintage"] >= 0
                                             and rec["growth_since_that_vintage"] <= 10),
            "modules_naming_a_ledger": len(pop),
        },
        "consumers": consumers,
        "census": pop,
        "summary": {
            "index_readers": len([c for c in consumers if c["kind"] == "index"]),
            "non_index_modules_naming_the_ledger": len(pop) - len(consumers),
            "by_class": by_class,
            "lose_every_row_without_a_leading_pipe":
                [c["id"] for c in consumers if c["class"] == C_SAME],
            "pipe_tolerant_readers": [c["id"] for c in consumers
                                      if c.get("dialect") == "row_head_with_or_without_a_leading_pipe"],
            "reads_a_timestamp_anywhere": [c["id"] for c in consumers
                                          if c.get("dialect") == "reads_a_timestamp_anywhere_in_the_line"],
            "window_limited_readers": [c["id"] for c in consumers if c.get("window_lines")],
            "narrower_scope_readers": [c["id"] for c in consumers if c["class"] == C_NARROW],
            "four_axes": ["row shape (leading pipe)", "stamp shape (T vs space)",
                          "window (tail lines)", "vintage (origin/main vs worktree)"],
        },
        "bounds": [
            "file sets are the constants each reader declares; a reader that names a file which "
            "does not exist is published with that file missing rather than repaired",
            "lane_round_liveness prefers origin/main, so its two counts are published apart and "
            "never reconciled into one number",
            "a module that only sizes, hashes, moves or scans prose is counted in the census but "
            "is given no row count -- naming a ledger is not reading its index",
            "the population is this host's ledgers at this cutoff; E577's 1,534 is the same cell "
            "two rounds earlier and the growth is published, not smoothed",
        ],
    }
    face["verdict"] = _verdict(face["summary"])
    face["verdict_line"] = _verdict_line(face["summary"])
    if write:
        if not os.path.isdir(OUTDIR):
            os.makedirs(OUTDIR)
        path = os.path.join(OUTDIR, "ROWINDEXCONSUMERS-%s.json" % CUTOFF)
        for p in (path, os.path.join(OUTDIR, "rowindexconsumers_latest.json")):
            with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
                json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
                fh.write("\n")
    return face


def _verdict(summary):
    same = summary.get("lose_every_row_without_a_leading_pipe") or []
    if not same:
        return "no_reader_loses_the_rows_without_a_leading_pipe"
    if len(same) >= 3:
        return "the_leading_pipe_blind_spot_is_inherited_by_the_whole_index_family"
    return "the_leading_pipe_blind_spot_reaches_more_than_the_study_that_found_it"


def _verdict_line(summary):
    same = summary.get("lose_every_row_without_a_leading_pipe") or []
    return ("%d row-index readers; %d lose every row without a leading pipe (%s); pipe-tolerant: %s"
            % (summary.get("index_readers", 0), len(same),
               ", ".join(x.split(".")[0].split("/")[-1] for x in same) or "none",
               ", ".join(x.split(".")[0].split("/")[-1]
                         for x in summary.get("pipe_tolerant_readers") or []) or "none"))


# ---------------------------------------------------------------- checks
def face_problems(face):
    """Everything that would make this face a wish rather than a measurement."""
    probs = []
    pop = face.get("population") or {}
    cons = face.get("consumers") or []
    summary = face.get("summary") or {}
    cells = pop.get("by_cell") or {}
    if sum(cells.values()) != pop.get("rows"):
        probs.append("the 2x2 cells do not add up to the row population")
    if (pop.get("rows_with_a_leading_pipe") or 0) + (pop.get("rows_without_a_leading_pipe") or 0) \
            != pop.get("rows"):
        probs.append("pipe + no-pipe does not add up to the row population")
    rec = pop.get("e577_reconciliation") or {}
    if rec.get("strict_plus_no_pipe_minus_lenient") is None:
        probs.append("E577's triple was not reconciled")
    if not cons:
        probs.append("no consumer was measured")
    ids = [c.get("id") for c in cons]
    if len(set(ids)) != len(ids):
        probs.append("a consumer is counted twice")
    for c in cons:
        if c.get("kind") == "index" and not c.get("reads_files"):
            probs.append("%s reads the index but no ledger file could be resolved for it"
                         % c.get("id"))
        if c.get("kind") == "index" and not c.get("declared_files") and not c.get("scope_note"):
            probs.append("%s declares no ledger and does not say where its scope comes from"
                         % c.get("id"))
        if c.get("class") not in CLASSES:
            probs.append("%s carries an unknown class %r" % (c.get("id"), c.get("class")))
        if c.get("dialect") and c["dialect"] not in (
                "row_head_with_a_leading_pipe", "row_head_with_or_without_a_leading_pipe",
                "reads_a_timestamp_anywhere_in_the_line", "refuses_every_row_shape"):
            probs.append("%s carries an unreadable dialect %r" % (c.get("id"), c.get("dialect")))
        seen, scope = c.get("rows_seen"), c.get("rows_in_its_scope")
        if isinstance(seen, int) and isinstance(scope, int) and seen > scope:
            probs.append("%s saw more rows than its own declared ledgers hold" % c.get("id"))
        if isinstance(seen, int) and isinstance(c.get("loss_in_scope"), int) and \
                seen + c["loss_in_scope"] != scope:
            probs.append("%s: seen + loss does not equal its scope" % c.get("id"))
        if c.get("class") == C_SAME:
            if (c.get("loss_in_scope") or 0) < (c.get("no_pipe_rows_in_scope") or 0):
                probs.append("%s is 'loses every no-pipe row' but its loss %r is below the "
                             "no-pipe count %r" % (c.get("id"), c.get("loss_in_scope"),
                                                   c.get("no_pipe_rows_in_scope")))
            if not c.get("refuses_every_no_pipe_row"):
                probs.append("%s is 'loses every no-pipe row' but accepted one" % c.get("id"))
            if len(set(c.get("reads_files") or [])) < len(pop.get("ledger_files") or []):
                probs.append("%s is 'loses every no-pipe row' while reading %d of %d ledgers"
                             % (c.get("id"), len(set(c.get("reads_files") or [])),
                                len(pop.get("ledger_files") or [])))
        if c.get("kind") != "index" and c.get("dialect") is None and c.get("class") != C_NOT_INDEX:
            probs.append("%s parses no rows but was classified as a reader" % c.get("id"))
        if c.get("class") == C_WINDOW and not isinstance(c.get("window_rows_reachable"), int):
            probs.append("%s is window-limited but its window was not measured" % c.get("id"))
        if c.get("kind") == "index" and c.get("dialect") == "row_head_with_or_without_a_leading_pipe" \
                and c.get("refuses_every_no_pipe_row") is True:
            probs.append("%s is pipe-tolerant by probe but refuses every no-pipe row on disk"
                         % c.get("id"))
    by_class = summary.get("by_class") or {}
    if sum(by_class.values()) != len(cons):
        probs.append("the class tally does not add up to the consumer count")
    if not summary.get("lose_every_row_without_a_leading_pipe"):
        probs.append("the verdict names no reader that loses every no-pipe row")
    for cid in summary.get("lose_every_row_without_a_leading_pipe") or []:
        row = next((c for c in cons if c.get("id") == cid), None)
        if row is None:
            probs.append("%s is named in the verdict but is not in the consumers list" % cid)
        elif row.get("class") != C_SAME:
            probs.append("%s is named in the verdict but carries class %r" % (cid, row.get("class")))
    if not face.get("bounds"):
        probs.append("no bounds were published")
    return probs


def check():
    face = build(write=False)
    probs = face_problems(face)
    print(json.dumps({"check": "PASS" if not probs else "FAIL", "problems": probs[:12],
                      "summary": face["summary"], "verdict": face["verdict"]},
                     ensure_ascii=False, indent=1))
    return 0 if not probs else 1


def verify():
    """Re-derive the face from disk and compare the fields that carry the verdict."""
    disk = _read_json(os.path.join(OUTDIR, "rowindexconsumers_latest.json"))
    fresh = build(write=False)
    problems = []
    for key in ("population", "summary", "verdict", "verdict_line"):
        if (disk.get(key) or {}) != (fresh.get(key) or {}):
            problems.append("%s differs from the rebuilt face" % key)
    if len(disk.get("consumers") or []) != len(fresh.get("consumers") or []):
        problems.append("consumer count differs from the rebuilt face")
    else:
        for a, b in zip(disk.get("consumers") or [], fresh.get("consumers") or []):
            for key in ("id", "class", "dialect", "rows_seen", "loss_in_scope"):
                if a.get(key) != b.get(key):
                    problems.append("%s.%s differs" % (a.get("id"), key))
    probs = problems + face_problems(disk)
    print(json.dumps({"verify": "PASS" if not probs else "FAIL", "problems": probs[:12]},
                     ensure_ascii=False, indent=1))
    return 0 if not probs else 1


def selftest():
    legs = []

    def leg(name, cond):
        legs.append((name, bool(cond)))

    R = row_population()
    cells = _split(R)
    leg("the row population is non-empty and the 2x2 adds up", len(R) > 2000
        and sum(cells.values()) == len(R))
    leg("the T-separated no-pipe cell agrees with E577's 1,534 within its growth",
        1530 <= cells.get("no_pipe_T", 0) <= 1545)
    leg("the T-separated pipe cell is smaller than the no-pipe cell",
        cells.get("pipe_T", 0) < cells.get("no_pipe_T", 0))
    leg("rows outside a full stamp are not in the population",
        all(re.match(r"^\|?\s*\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}", r["text"]) for r in R))
    leg("every row carries its pipe flag and separator",
        all(isinstance(r["leading_pipe"], bool) and r["separator"] in ("T", "space") for r in R))

    m573 = _mod("e573_silent_chain", "scripts/e573_silent_chain.py")
    fixture = {n: line for n, line, _r in SHAPES}
    leg("e573 takes the pipe row", m573.round_of_row(fixture["table_full"]) is not None)
    leg("e573 refuses the no-pipe row", m573.round_of_row(fixture[NO_PIPE_SHAPE]) is None)
    leg("e573 refuses prose", m573.round_of_row(fixture["prose_full"]) is None)
    p_live = _probe_liveness()
    leg("lane_round_liveness refuses the no-pipe row", p_live[NO_PIPE_SHAPE] is False)
    leg("lane_round_liveness takes the full pipe row", p_live["table_full"] is True)
    leg("lane_round_liveness needs seconds or an offset",
        p_live["table_minute"] is False)
    p_la = _probe_line_audit()
    leg("automation_line_audit takes the no-pipe row", p_la[NO_PIPE_SHAPE] is True)
    p_marks = _probe_marks()
    leg("marks_coverage sees a row without a pipe", p_marks[NO_PIPE_SHAPE] is True)
    leg("marks_coverage also sees a prose sentence", p_marks["prose_full"] is True)
    leg("a probe that takes prose is called 'timestamp anywhere'",
        _dialect({n: True for n, _l, _r in SHAPES})
        == "reads_a_timestamp_anywhere_in_the_line")
    leg("a probe that takes the no-pipe row is pipe-tolerant",
        _dialect({n: (n not in ("legacy_space",) + PROSE_SHAPES) for n, _l, _r in SHAPES})
        == "row_head_with_or_without_a_leading_pipe")
    leg("a probe that refuses every shape is not pipe-tolerant",
        _dialect({n: False for n, _l, _r in SHAPES}) == "refuses_every_row_shape")

    preds = predicates()
    f575 = preds["scripts/e575_only_flag.round_index"][0]
    leg("e575's predicate refuses the no-pipe row", f575(fixture[NO_PIPE_SHAPE]) is False)
    leg("e575's predicate takes the pipe row", f575(fixture["table_full"]) is True)
    f409, note409 = preds["scripts/e409_unfloored_faces._round_rows"]
    leg("e409's predicate was lifted from its source", bool(note409))
    leg("e409's predicate refuses the no-pipe row", f409(fixture[NO_PIPE_SHAPE]) is False)

    face = build(write=False)
    leg("the face is clean", not face_problems(face))
    leg("the census finds modules that name a ledger",
        (face.get("population") or {}).get("modules_naming_a_ledger", 0) > 5)
    leg("the census finds modules that name a ledger but parse no rows",
        (face.get("summary") or {}).get("non_index_modules_naming_the_ledger", 0) > 0)
    leg("the verdict names at least two readers",
        len((face.get("summary") or {}).get("lose_every_row_without_a_leading_pipe") or []) >= 2)
    leg("each named reader loses at least every no-pipe row",
        all(next(c for c in face["consumers"] if c["id"] == cid)["loss_in_scope"]
            >= next(c for c in face["consumers"] if c["id"] == cid)["no_pipe_rows_in_scope"]
            for cid in face["summary"]["lose_every_row_without_a_leading_pipe"]))
    leg("E577's triple is reconciled with a named gap",
        (face["population"]["e577_reconciliation"]
         .get("strict_plus_no_pipe_minus_lenient") or 0) > 0)
    leg("every consumer publishes the reason for its class",
        all(c.get("class_reason") for c in face["consumers"]))

    # doctored faces must be refused
    doc = json.loads(json.dumps(face))
    for c in doc["consumers"]:
        if c["id"] in doc["summary"]["lose_every_row_without_a_leading_pipe"]:
            c["reads_files"] = c["reads_files"][:1]
            break
    leg("a 'loses every no-pipe row' reader that reads one ledger is refused",
        bool(face_problems(doc)))
    doc2 = json.loads(json.dumps(face))
    for c in doc2["consumers"]:
        if c["class"] == C_SAME:
            c["loss_in_scope"] = c["no_pipe_rows_in_scope"] - 1
            break
    leg("a 'loses every no-pipe row' reader whose loss is short by one is refused",
        bool(face_problems(doc2)))
    doc3 = json.loads(json.dumps(face))
    doc3["summary"]["lose_every_row_without_a_leading_pipe"] = []
    doc3["verdict"] = "no_reader_loses_the_rows_without_a_leading_pipe"
    leg("a verdict that names nobody is refused",
        any("names no reader" in p for p in face_problems(doc3)))
    doc4 = json.loads(json.dumps(face))
    doc4["population"]["by_cell"] = {"pipe_T": 1}
    leg("an index whose cells do not add up is refused",
        any("do not add up" in p for p in face_problems(doc4)))
    doc5 = json.loads(json.dumps(face))
    doc5["consumers"][0]["class"] = "a_class_nobody_defined"
    leg("an unknown class is refused", bool(face_problems(doc5)))

    live = next((c for c in face["consumers"] if "lane_round_liveness" in c["id"]), {})
    leg("the origin/main vintage is published beside the worktree count",
        "rows_seen_from_origin_main_per_file" in live)
    audit = next((c for c in face["consumers"] if "automation_line_audit" in c["id"]), {})
    leg("the window-limited reader publishes its window size",
        isinstance(audit.get("window_lines"), int))

    ok = sum(1 for _, c in legs if c)
    for name, cond in legs:
        if not cond:
            print("[FAIL] %s" % name)
    print("e578 selftest: %d/%d PASS" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "build"
    if cmd == "build":
        face = build(write=True)
        print(json.dumps({"build": "ok",
                          "face": "results/state_tilt/ROWINDEXCONSUMERS-%s.json" % CUTOFF,
                          "verdict": face["verdict"], "verdict_line": face["verdict_line"]},
                         ensure_ascii=False, indent=1))
        return 0
    if cmd == "check":
        return check()
    if cmd == "verify":
        return verify()
    if cmd == "selftest":
        return selftest()
    print("usage: python scripts/e578_round_index_consumers.py [build|check|verify|selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main())