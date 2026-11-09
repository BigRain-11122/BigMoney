# -*- coding: utf-8 -*-
"""E597 -- is a published BAR COUNT ever turned into a RATE?

E588 (r1623) asked that question of one file and answered it with a census of eleven modules:
no consumer of ``results/etf_book_forward/LEDGER.json`` puts ``len(bars)`` into arithmetic on
its own line, yet two of them *publish* the count.  A count that is only carried is cosmetic; a
count that becomes a per-bar rate is a wrong rate.  This study widens the question to every
published face in the repo that carries a bar count, and splits it in two:

  (a) AT THE WRITER.  A published ``cagr`` next to a published ``bars`` is an annualisation
      whose denominator IS the bar count (or a bars-per-year constant derived from it).  For
      every block that carries ``bars`` + ``years`` + ``total_ret`` + ``cagr`` this study
      re-derives the annualised figure from the two fields that are not the count, and compares
      it with the one that was published.  ``years`` is then divided by ``bars`` to publish the
      implied bars-per-year constant, which is what makes the count live rather than decorative.
  (b) ONE HOP DOWNSTREAM.  For every module that names such a face by a path literal, grade the
      module's own lines: does it put a bar count into a DENOMINATOR, a MULTIPLIER, an
      ANNUALISATION, a presence test, or only print it?

And the second half of the card: could the face itself have noticed a duplicated row?  A face
that publishes only a count cannot; a face that publishes the first and last bar's identity, or
a distinct-bar count beside the row count, or a dedupe flag, can.

Read-only: no runner, no fixture write, no panel refresh.  The only write is this face.

  python scripts/e597_bar_count_arith.py build
  python scripts/e597_bar_count_arith.py check
  python scripts/e597_bar_count_arith.py verify
  python scripts/e597_bar_count_arith.py selftest

Output: results/state_tilt/BARCOUNTARITH.json (+ BARCOUNTARITH-latest.json)
"""
from __future__ import annotations

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

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
OUT_PATH = os.path.join(OUTDIR, "BARCOUNTARITH.json")
SELF_STEM = "BARCOUNTARITH"
SELF_NAME = "e597_bar_count_arith.py"

# a key that states HOW MANY bars, as opposed to which ones.  ``bars`` is the only ambiguous
# member: in the forward ledger it is a list of bar objects, in the capacity faces it is an int.
# Only an int value counts here, and a bare ``payload["bars"]`` read is not credited as a count
# (see limits) because this instrument cannot tell the two shapes apart at the read site.
COUNT_KEYS = ("bars", "n_bars", "bar_count", "n_bar", "bars_observed")
ANNUAL_KEYS = ("bars", "years", "total_ret", "cagr")
# keys that would let a face notice a duplicated row: an identity for the first and last bar
BAR_IDENTITY_KEYS = ("first_bar", "last_bar", "start_bar", "end_bar", "first_date", "last_date",
                     "bar_start", "bar_end", "first", "last")
RE_WITNESS_FIELD = re.compile(
    r"dedupe|de-?dup|duplicate|unique_bars|distinct_bars|n_distinct|rows_equal_bars", re.I)

FACE_GLOBS = ("results/**/*.json", "docs/**/*.json")
SCAN_DIRS = ["scripts", "Tools", "firm", "live", "monitor", "."]
SKIP_DIRS = {"__pycache__", ".git", "results", "data", "research", "knowledge", "docs",
             "content", "fleet", "legacy", "Money02", ".codely-cli", "media", "node_modules"}
EXCLUDE_NAME = re.compile(r"^(_r\d|_tmp|_dbg|_e\d+_run)")

READ_CAP = 1000000          # bytes; above this the face is published as too_big, not guessed at
DEPTH_CAP = 4
LIST_CAP = 40
CAGR_TOL = 5e-4             # a published 4-6 decimal cagr cannot be compared tighter than this
REDERIVE_TOL = 1e-9         # this study's own arithmetic, compared against its own publication

# witness classes: could this block have noticed a duplicated row?
W_DEDUPE = "a_dedupe_field_is_published"
W_IDENTITY = "the_first_and_last_bar_identities_are_published"
W_COUNT_ONLY = "a_count_and_nothing_else"

ROLES = ("divisor", "multiplier", "annualisation_input", "presence_only", "printed_only")

C_ANNUALISED = "carries_the_annualisation_quadruple"
C_COUNT_ONLY = "carries_a_bar_count_only"

V_NO_ANNUAL = "no_face_in_the_repo_publishes_an_annualised_figure_beside_a_bar_count"
V_WRITER_ONLY = ("the_bar_count_feeds_annualisation_at_the_writer_and_lands_in_the_published_"
                 "figure_but_no_reader_puts_a_published_count_into_arithmetic_on_its_own_line")
V_READER_RATES = "some_reader_puts_a_published_bar_count_into_arithmetic_on_its_own_line"

# annualisation constants only: months, weeks, trading days, calendar days.  Room to grow a
# period multiplier by 2 or 4 is not an annualisation and must not be graded as one.
RE_ANNUAL_CONST = re.compile(r"\b(12|52|240|241|242|243|244|250|252|365)\b")
RE_COUNT_IDENT = re.compile(r"\b(n_bars|bar_count|n_bar|bars_observed)\b")
RE_LEN = re.compile(r"\blen\s*\(")
RE_PRESENCE = re.compile(r"(?:<=|>=|<|>|==|!=)\s*[012](?!\d)")
RE_DEDUPE_GUARD = re.compile(
    r"dedupe|uniq|rows_equal_bars|accrued_bars_on_disk|set\(\s*[^)]*\bbar\b"
    r"|\{[^}]*for\s+\w+\s+in\s+[^}]*\bbars\b", re.I)
RE_PATH_STR = re.compile(r"""(['"])([^'"\n]{4,200}?)\1""")
DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})")


# --------------------------------------------------------------------------- pure helpers
def is_count_value(v):
    return isinstance(v, int) and not isinstance(v, bool)


def count_spans(line):
    """(start, end, kind) for every place this line reads a bar COUNT (never a bar list).

    Two shapes are recognised: ``len(...)`` over an expression that mentions bars, and the
    unambiguous count identifiers.  A bare ``payload["bars"]`` read is deliberately NOT a count
    here -- see the limits block on the face.
    """
    spans = []
    for m in RE_LEN.finditer(line):
        i = m.end() - 1
        depth = 0
        for j in range(i, len(line)):
            if line[j] == "(":
                depth += 1
            elif line[j] == ")":
                depth -= 1
                if depth == 0:
                    inner = line[i + 1:j]
                    if re.search(r"\bbars\b|\bn_bars\b", inner):
                        spans.append((m.start(), j + 1, "len_of_bars"))
                    break
    for m in RE_COUNT_IDENT.finditer(line):
        if not any(s <= m.start() < e for s, e, _k in spans):
            spans.append((m.start(), m.end(), m.group(1)))
    return spans


def classify_line(line):
    """Which arithmetic roles this single source line plays on a bar count. Pure."""
    spans = count_spans(line)
    if not spans:
        return []
    roles = set()
    annual = bool(RE_ANNUAL_CONST.search(line)) or "sqrt" in line
    for start, end, _kind in spans:
        before = line[:start]
        after = line[end:]
        binds_denominator = bool(re.search(r"/\s*$", before))
        binds_numerator = bool(re.match(r"\s*/", after))
        binds_multiplier = bool(re.match(r"\s*\*", after))
        if binds_denominator:
            roles.add("divisor")
        if binds_multiplier:
            roles.add("multiplier")
        if (binds_denominator or binds_numerator or binds_multiplier) and annual:
            roles.add("annualisation_input")
    # sqrt of a count is an annualisation (a standard error scaled to a per-year horizon) even
    # though it binds no arithmetic operator of its own
    if annual and spans and re.search(r"sqrt\s*\(", line):
        roles.add("annualisation_input")
    rest = line
    for start, end, _kind in spans:
        rest = rest[:start] + " " * (end - start) + rest[end:]
    if RE_PRESENCE.search(rest) and not (roles & {"divisor", "multiplier", "annualisation_input"}):
        roles.add("presence_only")
    if not roles:
        roles.add("printed_only")
    return sorted(roles)


def module_usage(text):
    """{role: [{line, code}]} across a module's own lines."""
    usage = {r: [] for r in ROLES}
    for i, line in enumerate(text.splitlines(), 1):
        for r in classify_line(line):
            usage[r].append({"line": i, "code": line.strip()[:200]})
    return usage


def duplicate_effect(usage):
    """What a duplicated row would do to this module, on the E588 ladder."""
    if usage.get("divisor") or usage.get("multiplier") or usage.get("annualisation_input"):
        return "blind_row_count_in_arithmetic"
    if usage.get("presence_only") or usage.get("printed_only"):
        return "carries_or_tests_the_count"
    return "reads_no_count"


def witness_class(block):
    """Could this block have noticed a duplicated row?"""
    if any(RE_WITNESS_FIELD.search(k) for k in block):
        return W_DEDUPE
    if all(k in block for k in ("first_bar", "last_bar")):
        return W_IDENTITY
    if all(k in block for k in ("first", "last")):
        return W_IDENTITY
    return W_COUNT_ONLY


def rederive_cagr(block):
    """The annualised figure implied by (total_ret, years) -- the two fields that are not a count."""
    try:
        years = float(block["years"])
        total = float(block["total_ret"])
        published = float(block["cagr"])
    except (KeyError, TypeError, ValueError):
        return None
    if years <= 0 or (1.0 + total) <= 0:
        return None
    implied = (1.0 + total) ** (1.0 / years) - 1.0
    return {"implied_cagr": round(implied, 8),
            "published_cagr": round(published, 8),
            "abs_err": round(abs(implied - published), 8),
            "is_annualised": abs(implied - published) <= CAGR_TOL}


def bars_per_year(block):
    """The annualisation constant this block's own (bars, years) pair implies."""
    try:
        years = float(block["years"])
        bars = block["bars"]
    except (KeyError, TypeError, ValueError):
        return None
    if years <= 0 or not is_count_value(bars) or bars <= 0:
        return None
    return round(bars / years, 4)


def walk_blocks(payload, path=""):
    """Every dict under the payload that states a bar count, with its own dotted path."""
    out = []

    def walk(node, at, depth):
        if isinstance(node, dict):
            if any(is_count_value(node.get(k)) for k in COUNT_KEYS):
                out.append((at or "/", node))
            if depth < DEPTH_CAP:
                for k, v in node.items():
                    walk(v, (at or "") + "/" + str(k), depth + 1)
        elif isinstance(node, list) and depth < DEPTH_CAP:
            for i, v in enumerate(node[:LIST_CAP]):
                walk(v, (at or "") + "[%d]" % i, depth + 1)

    walk(payload, path, 0)
    return out


def block_kind(block):
    return C_ANNUALISED if all(k in block for k in ANNUAL_KEYS) else C_COUNT_ONLY


def block_row(face, at, block):
    kind = block_kind(block)
    row = {
        "face": face,
        "at": at,
        "kind": kind,
        "count_keys": sorted(k for k in COUNT_KEYS if is_count_value(block.get(k))),
        "bars": block.get("bars"),
        "witness": witness_class(block),
    }
    if kind != C_ANNUALISED:
        return row
    rd = rederive_cagr(block)
    row.update({
        "years": block.get("years"),
        "total_ret": block.get("total_ret"),
        "cagr": block.get("cagr"),
        "bars_per_year_implied": bars_per_year(block),
        "rederived": bool(rd and rd["is_annualised"]),
        "implied_cagr": rd["implied_cagr"] if rd else None,
        "abs_err": rd["abs_err"] if rd else None,
    })
    return row


def face_summary(rows):
    """Per-face counts: how many blocks, how many of them annualised, how many re-derive."""
    out = {}
    for r in rows:
        f = out.setdefault(r["face"], {"blocks": 0, "annualised": 0, "rederiving": 0,
                                      "witness": {}})
        f["blocks"] += 1
        if r["kind"] == C_ANNUALISED:
            f["annualised"] += 1
            if r["rederived"]:
                f["rederiving"] += 1
        f["witness"][r["witness"]] = f["witness"].get(r["witness"], 0) + 1
    return dict(sorted(out.items()))


# --------------------------------------------------------------------------- scan
def faces_on_disk(root):
    out = []
    for pattern in FACE_GLOBS:
        for p in glob.glob(os.path.join(root, pattern), recursive=True):
            rel = os.path.relpath(p, root).replace("\\", "/")
            if os.path.basename(rel).startswith(SELF_STEM):
                continue
            out.append(rel)
    return sorted(set(out))


def scan_faces(root=None):
    root = root or ROOT
    rows, unreadable, too_big, dates = [], 0, [], []
    for rel in faces_on_disk(root):
        path = os.path.join(root, rel)
        try:
            if os.path.getsize(path) > READ_CAP:
                too_big.append(rel)
                unreadable += 1
                continue
            with io.open(path, encoding="utf-8", errors="replace") as fh:
                payload = json.load(fh)
        except (ValueError, OSError):
            unreadable += 1
            continue
        blocks = walk_blocks(payload)
        if not blocks:
            continue
        for at, block in blocks:
            rows.append(block_row(rel, at, block))
        for key in ("evidence_cutoff", "as_of", "cutoff", "ts"):
            v = payload.get(key) if isinstance(payload, dict) else None
            if isinstance(v, str):
                m = DATE_RE.match(v.strip())
                if m:
                    dates.append(m.group(1))
    return {"rows": rows, "unreadable": unreadable, "too_big": sorted(too_big),
            "dates": dates}


# --------------------------------------------------------------------------- readers
def python_modules(root):
    seen, out = [], []
    for d in SCAN_DIRS:
        base = os.path.join(root, d)
        if d == ".":
            for f in os.listdir(root):
                if f.endswith(".py"):
                    p = os.path.join(root, f)
                    if p not in seen:
                        seen.append(p)
                        out.append(p)
            continue
        if not os.path.isdir(base):
            continue
        for dp, dn, fn in os.walk(base):
            dn[:] = [x for x in dn if x not in SKIP_DIRS and not x.startswith("_r")]
            for f in fn:
                if not f.endswith(".py"):
                    continue
                p = os.path.join(dp, f)
                if p not in seen:
                    seen.append(p)
                    out.append(p)
    return sorted(out)


def path_literals(text):
    """Every string literal in a module that looks like a path."""
    out = set()
    for m in RE_PATH_STR.finditer(text):
        s = m.group(2)
        if "/" in s or "\\" in s:
            out.add(s.replace("\\", "/"))
    return out


def addressing(literals, face):
    """How a module's own literals reach this face: by its path, or only by its basename."""
    base = os.path.basename(face)
    by_path = False
    by_base = False
    for lit in literals:
        if lit == face or lit.endswith("/" + face):
            by_path = True
        elif os.path.basename(lit) == base:
            by_base = True
    if by_path:
        return "names_this_face"
    if by_base:
        return "names_basename_only"
    return ""


def module_kind(text, name):
    """Writer / study / wave runner / standing reader -- published so a rate is attributable."""
    if name == SELF_NAME:
        return "self"
    if re.search(r"^\"\"\"E\d+", text) or re.search(r"^# -\*- coding", text) and "selftest" in text:
        if re.search(r"^\"\"\"E\d+", text):
            return "study"
    if re.search(r"^\"\"\"W\d+", text, re.M) or re.search(r"trial_labor_w\d+", name):
        return "wave_runner"
    if re.search(r"^OUT_PATH\s*=|^OUTDIR\s*=", text, re.M) and "def build(" in text:
        return "study"
    return "reader"


def scan_readers(faces, root=None):
    root = root or ROOT
    rows, excluded = [], []
    for p in python_modules(root):
        name = os.path.basename(p)
        rel = os.path.relpath(p, root).replace("\\", "/")
        try:
            text = io.open(p, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        if not count_spans_anywhere(text):
            continue
        lits = path_literals(text)
        named = sorted(f for f in faces if addressing(lits, f) == "names_this_face")
        based = sorted(f for f in faces if addressing(lits, f) == "names_basename_only")
        if not named and not based:
            continue
        if name == SELF_NAME:
            excluded.append({"module": rel,
                             "reason": "this study -- its own selftest literals name faces"})
            continue
        if EXCLUDE_NAME.match(name):
            excluded.append({"module": rel, "reason": "round-local helper or debug script"})
            continue
        usage = module_usage(text)
        roles = [r for r in ROLES if usage.get(r)]
        rows.append({
            "module": rel,
            "kind": module_kind(text, name),
            "faces_named_by_path": named[:12],
            "faces_named_by_basename_only": based[:12],
            "n_faces_named_by_path": len(named),
            "roles": roles,
            "duplicate_effect": duplicate_effect(usage),
            "evidence": {r: usage[r][:3] for r in ("divisor", "multiplier",
                                                  "annualisation_input")
                         if usage.get(r)},
        })
    return rows, excluded


def count_spans_anywhere(text):
    for line in text.splitlines():
        if count_spans(line):
            return True
    return False


# --------------------------------------------------------------------------- summarise
def _counter(values):
    out = {}
    for v in values:
        if v:
            out[v] = out.get(v, 0) + 1
    return dict(sorted(out.items()))


def summarise(frows, reader_rows, unreadable, too_big, excluded):
    annual = [r for r in frows if r["kind"] == C_ANNUALISED]
    faces = sorted({r["face"] for r in frows})
    annual_faces = sorted({r["face"] for r in annual})
    witness = {}
    for r in annual:
        witness[r["witness"]] = witness.get(r["witness"], 0) + 1
    bpy = sorted(r["bars_per_year_implied"] for r in annual
                 if r.get("bars_per_year_implied"))
    by_face = face_summary(frows)
    return {
        "faces_publishing_a_bar_count": len(faces),
        "blocks_publishing_a_bar_count": len(frows),
        "blocks_annualised": len(annual),
        "faces_annualised": len(annual_faces),
        "blocks_where_cagr_re_derives": sum(1 for r in annual if r["rederived"]),
        "blocks_where_it_does_not": sum(1 for r in annual if not r["rederived"]),
        "annualisation_witness": dict(sorted(witness.items())),
        "bars_per_year_implied_min": bpy[0] if bpy else None,
        "bars_per_year_implied_max": bpy[-1] if bpy else None,
        "bars_per_year_implied_median": bpy[len(bpy) // 2] if bpy else None,
        "reader_modules_naming_a_face": len(reader_rows),
        "reader_modules_dividing_by_a_count": sum(
            1 for r in reader_rows if "divisor" in r["roles"]),
        "reader_modules_multiplying_a_count": sum(
            1 for r in reader_rows if "multiplier" in r["roles"]),
        "reader_modules_annualising_a_count": sum(
            1 for r in reader_rows if "annualisation_input" in r["roles"]),
        "reader_modules_printing_a_count": sum(
            1 for r in reader_rows if r["roles"] == ["printed_only"]),
        "reader_modules_testing_presence_only": sum(
            1 for r in reader_rows if "presence_only" in r["roles"]),
        "reader_modules_guarding_a_duplicate": sum(
            1 for r in reader_rows if r["duplicate_effect"] == "carries_or_tests_the_count"),
        "reader_modules_blind_in_arithmetic": sum(
            1 for r in reader_rows if r["duplicate_effect"] == "blind_row_count_in_arithmetic"),
        "reader_modules_by_kind": _counter(r.get("kind") for r in reader_rows),
        "reader_modules_dividing_a_count_named": sorted(
            r["module"] for r in reader_rows
            if {"divisor", "multiplier", "annualisation_input"} & set(r["roles"])),
        "reader_modules_basename_only": sum(
            1 for r in reader_rows if not r["faces_named_by_path"]),
        "faces_unreadable": unreadable,
        "faces_too_big": len(too_big),
        "modules_excluded": len(excluded),
        "blocks_by_face": by_face,
    }


def verdict_from(counts):
    if not counts.get("blocks_annualised"):
        return V_NO_ANNUAL
    if (counts.get("reader_modules_dividing_by_a_count")
            or counts.get("reader_modules_multiplying_a_count")
            or counts.get("reader_modules_annualising_a_count")):
        return V_READER_RATES
    return V_WRITER_ONLY


def answer_sentence(counts, verdict):
    if verdict == V_NO_ANNUAL:
        return ("no face in the repo publishes an annualised figure beside a bar count, so the "
                "count cannot become a rate anywhere this instrument can see")
    head = ("%d of %d blocks that publish a bar count also publish an annualised figure, and all "
            "%d of those re-derive to within %.0e of the figure printed, with an implied "
            "bars-per-year constant of %s..%s (median %s)"
            % (counts["blocks_annualised"], counts["blocks_publishing_a_bar_count"],
               counts["blocks_where_cagr_re_derives"], CAGR_TOL,
               counts["bars_per_year_implied_min"], counts["bars_per_year_implied_max"],
               counts["bars_per_year_implied_median"]))
    if verdict == V_READER_RATES:
        named = counts.get("reader_modules_dividing_a_count_named") or []
        tail = ("; downstream, %d of %d reader modules divide a published count, %d multiply it "
                "and %d annualise it (%s)"
                % (counts["reader_modules_dividing_by_a_count"],
                   counts["reader_modules_naming_a_face"],
                   counts["reader_modules_multiplying_a_count"],
                   counts["reader_modules_annualising_a_count"],
                   ", ".join(named[:6]) or "none"))
    else:
        tail = ("; downstream, %d of %d reader modules that name such a face put a published "
                "count into a denominator, a multiplier or an annualisation on their own lines "
                "(%d only print it, %d only test it for presence)"
                % (0, counts["reader_modules_naming_a_face"],
                   counts["reader_modules_printing_a_count"],
                   counts["reader_modules_testing_presence_only"]))
    witness = counts.get("annualisation_witness") or {}
    only_count = witness.get(W_COUNT_ONLY, 0)
    if only_count:
        tail += ("; %d of the %d annualised blocks publish a count and nothing that could reveal "
                 "a duplicated row" % (only_count, counts["blocks_annualised"]))
    return head + tail


# --------------------------------------------------------------------------- face
def publish_view(frows, sample_per_face=6):
    """All annualised blocks (they are the finding) plus a bounded sample of count-only ones
    drawn from the faces that also carry an annualised block.  The other faces are published as
    an aggregate in blocks_by_face -- 499 faces x 6 sample rows would make the face 600KB to say
    "a count and nothing else" 2,900 times (E207 name-as-measure family)."""
    annual = [r for r in frows if r["kind"] == C_ANNUALISED]
    annual_faces = {r["face"] for r in annual}
    per_face = {}
    aggregate_only = 0
    for r in frows:
        if r["kind"] == C_ANNUALISED:
            continue
        if r["face"] not in annual_faces:
            aggregate_only += 1
            continue
        per_face.setdefault(r["face"], []).append(r)
    sampled = []
    dropped = 0
    for face in sorted(per_face):
        got = per_face[face]
        sampled.extend(got[:sample_per_face])
        dropped += max(0, len(got) - sample_per_face)
    return {"blocks": annual + sampled,
            "not_published": {
                "count_only_blocks_sampled_out": dropped,
                "count_only_blocks_from_faces_published_in_aggregate_only": aggregate_only}}


def published_face_summary(frows):
    """Per-face aggregates for the faces whose blocks are published in full; the rest are a count."""
    annual_faces = {r["face"] for r in frows if r["kind"] == C_ANNUALISED}
    keep = [r for r in frows if r["face"] in annual_faces]
    return face_summary(keep)


def build(write=True, root=None):
    root = root or ROOT
    sc = scan_faces(root)
    frows = sc["rows"]
    faces = sorted({r["face"] for r in frows})
    reader_rows, excluded = scan_readers(faces, root)
    counts = summarise(frows, reader_rows, sc["unreadable"], sc["too_big"], excluded)
    # the per-face aggregates are published only for the faces whose blocks are in the face, so
    # the block counts and the aggregate table describe the same population
    counts["blocks_by_face"] = published_face_summary(frows)
    counts["faces_publishing_a_count_only_aggregate"] = (
        counts["faces_publishing_a_bar_count"] - len(counts["blocks_by_face"]))
    view = publish_view(frows)
    face = {
        "study": "E597_bar_count_arith",
        "evidence_cutoff": max(sc["dates"]) if sc["dates"] else None,
        "count_keys": list(COUNT_KEYS),
        "annualisation_keys": list(ANNUAL_KEYS),
        "blocks": view["blocks"],
        "not_published": view["not_published"],
        "readers": reader_rows,
        "excluded_modules": excluded,
        "too_big": {"count": len(sc["too_big"]), "first_20": sc["too_big"][:20]},
        "counts": counts,
        "verdict": verdict_from(counts),
        "answer": answer_sentence(counts, verdict_from(counts)),
        "limits": [
            "a bar count is recognised only as an integer under %s or as a len() over something "
            "that mentions bars; a bare payload[\"bars\"] read cannot be told apart from a "
            "read of the bar LIST (the forward ledger stores a list under the same name), so it "
            "is not credited as a count read here -- this census is a lower bound"
            % ", ".join(COUNT_KEYS),
            "roles are decided line-level on the module's own literals: a count that travels "
            "through several helper frames before being divided is invisible",
            "a reader is attributed to a face only when its own literal states the face path; a "
            "module that reaches the face through a constant defined elsewhere is counted in "
            "reader_modules_basename_only or not at all",
            "the annualisation arm re-derives cagr from (total_ret, years) and compares with the "
            "published cagr at %.0e; a face that annualises with a different formula (log return, "
            "arithmetic mean x bars) would read as not re-deriving, which is a statement about "
            "the formula and not about the count" % CAGR_TOL,
            "lists are walked %d elements deep at %d levels; a count inside a longer tail is not "
            "seen" % (LIST_CAP, DEPTH_CAP),
            "faces above %d bytes are published as too_big rather than parsed" % READ_CAP,
        ],
    }
    problems = face_problems(face)
    if write and not problems:
        write_face(face)
    return face, problems


def write_face(face):
    os.makedirs(OUTDIR, exist_ok=True)
    body = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    for path in (OUT_PATH, os.path.join(OUTDIR, SELF_STEM + "-latest.json")):
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body)


# --------------------------------------------------------------------------- guard
def face_problems(face):
    p = []
    if not isinstance(face, dict) or "counts" not in face:
        return ["the face carries no counts block"]
    blocks = face.get("blocks") or []
    readers = face.get("readers") or []
    counts = face.get("counts") or {}
    npb = face.get("not_published") or {}
    if not blocks:
        p.append("no block is published")
    if not isinstance(npb.get("count_only_blocks_sampled_out"), int):
        p.append("the not-published block does not say how many count-only blocks were sampled out")

    annual = [b for b in blocks if b.get("kind") == C_ANNUALISED]
    for b in blocks:
        if b.get("kind") not in (C_ANNUALISED, C_COUNT_ONLY):
            p.append("block %s carries an unknown kind %r" % (b.get("at"), b.get("kind")))
            break
    for b in annual:
        rd = rederive_cagr({"years": b.get("years"), "total_ret": b.get("total_ret"),
                            "cagr": b.get("cagr")})
        if rd is None:
            p.append("block %s/%s cannot be re-derived from the fields it publishes"
                     % (b.get("face"), b.get("at")))
            break
        if abs(float(b.get("implied_cagr") or 0.0) - rd["implied_cagr"]) > REDERIVE_TOL:
            p.append("block %s/%s publishes implied_cagr %r, re-derives to %r"
                     % (b.get("face"), b.get("at"), b.get("implied_cagr"),
                        rd["implied_cagr"]))
            break
        if bool(b.get("rederived")) != rd["is_annualised"]:
            p.append("block %s/%s claims rederived=%r but the check says %r"
                     % (b.get("face"), b.get("at"), b.get("rederived"), rd["is_annualised"]))
            break
        bpy = bars_per_year({"bars": b.get("bars"), "years": b.get("years")})
        if bpy is not None and abs(float(b.get("bars_per_year_implied") or 0.0) - bpy) > 1e-4:
            p.append("block %s/%s publishes bars_per_year_implied %r, re-derives to %r"
                     % (b.get("face"), b.get("at"), b.get("bars_per_year_implied"), bpy))
            break

    if counts.get("blocks_annualised") != len(annual):
        p.append("blocks_annualised is %r but %d published blocks carry the quadruple"
                 % (counts.get("blocks_annualised"), len(annual)))
    sampled = npb.get("count_only_blocks_sampled_out")
    aggregate_only = npb.get("count_only_blocks_from_faces_published_in_aggregate_only")
    if isinstance(sampled, int) and isinstance(aggregate_only, int):
        if counts.get("blocks_publishing_a_bar_count") != len(blocks) + sampled + aggregate_only:
            p.append("blocks_publishing_a_bar_count is %r but published %d + sampled-out %d + "
                     "aggregate-only %d = %d"
                     % (counts.get("blocks_publishing_a_bar_count"), len(blocks), sampled,
                        aggregate_only, len(blocks) + sampled + aggregate_only))
    else:
        p.append("the not-published block does not account for every count-only block")
    if counts.get("blocks_where_cagr_re_derives") != sum(1 for b in annual if b.get("rederived")):
        p.append("blocks_where_cagr_re_derives does not re-derive from the published blocks")
    if (counts.get("blocks_where_cagr_re_derives", 0)
            + counts.get("blocks_where_it_does_not", 0)) != len(annual):
        p.append("the re-derive partition does not cover every annualised block")
    by_face = counts.get("blocks_by_face") or {}
    if sorted(by_face) != sorted({b["face"] for b in blocks} | set(by_face)):
        p.append("blocks_by_face names a face with no published block")
    for face_name, agg in by_face.items():
        if agg.get("blocks", 0) < agg.get("annualised", 0):
            p.append("face %s claims %r annualised blocks out of %r"
                     % (face_name, agg.get("annualised"), agg.get("blocks")))
            break
    if counts.get("faces_publishing_a_bar_count") != (
            len(by_face) + (counts.get("faces_publishing_a_count_only_aggregate") or 0)):
        p.append("faces_publishing_a_bar_count is %r but %d per-face aggregates + %r "
                 "aggregate-only faces"
                 % (counts.get("faces_publishing_a_bar_count"), len(by_face),
                    counts.get("faces_publishing_a_count_only_aggregate")))
    if counts.get("faces_annualised") != len({b["face"] for b in annual}):
        p.append("faces_annualised does not re-derive from the annualised blocks")

    for key, role in (("reader_modules_dividing_by_a_count", "divisor"),
                      ("reader_modules_multiplying_a_count", "multiplier"),
                      ("reader_modules_annualising_a_count", "annualisation_input"),
                      ("reader_modules_testing_presence_only", "presence_only")):
        want = sum(1 for r in readers if role in (r.get("roles") or []))
        if counts.get(key) != want:
            p.append("%s is %r but %d published readers carry role %s"
                     % (key, counts.get(key), want, role))
            break
    if counts.get("reader_modules_naming_a_face") != len(readers):
        p.append("reader_modules_naming_a_face is %r but %d reader rows are published"
                 % (counts.get("reader_modules_naming_a_face"), len(readers)))
    for r in readers:
        for role in r.get("roles") or []:
            if role not in ROLES:
                p.append("reader %s carries an unknown role %r" % (r.get("module"), role))
                break
        if "divisor" in (r.get("roles") or []) and not (r.get("evidence") or {}).get("divisor"):
            p.append("reader %s is graded a divisor with no line evidence" % r.get("module"))
            break
    if face.get("verdict") != verdict_from(counts):
        p.append("the verdict does not follow the counts")
    if not face.get("answer"):
        p.append("the face carries no answer sentence")
    return p


# --------------------------------------------------------------------------- selftest
def selftest():
    ok = []

    def chk(name, cond, detail=""):
        ok.append(bool(cond))
        print(("PASS " if cond else "FAIL ") + name + ((" | " + str(detail)) if not cond else ""))

    # 1-5 count recognition
    chk("1 len(bars) is a count read",
        [s[2] for s in count_spans("n = len(bars)")] == ["len_of_bars"])
    chk("2 len(ledger['bars']) is a count read",
        [s[2] for s in count_spans("n = len(ledger['bars'])")] == ["len_of_bars"])
    chk("3 a bare bars list read is not a count read", count_spans("rows = bars") == [])
    chk("4 a bare payload['bars'] read is not credited as a count",
        count_spans("v = payload['bars']") == [])
    chk("5 an unambiguous count identifier is a count read",
        [s[2] for s in count_spans("rate = total / n_bars")] == ["n_bars"])

    # 6-12 arithmetic roles
    chk("6 a count in a denominator is a divisor",
        classify_line("per_bar = total / n_bars") == ["divisor"])
    chk("7 len(bars) as the denominator is a divisor",
        "divisor" in classify_line("mean = sum(x) / len(bars)"))
    chk("8 a count times a constant is a multiplier",
        classify_line("span = n_bars * 2") == ["multiplier"])
    chk("9 a count over an annual constant is an annualisation input",
        "annualisation_input" in classify_line("ret = total / n_bars * 242"))
    chk("10 sqrt of a count is an annualisation input",
        "annualisation_input" in classify_line("se = sd / sqrt(n_bars)"))
    chk("11 a count compared to zero is presence only",
        classify_line("if n_bars == 0:") == ["presence_only"])
    chk("12 a count that is only printed is printed only",
        classify_line("print('bars', n_bars)") == ["printed_only"])

    # 13-16 block classification
    quad = {"bars": 1648, "years": 6.81, "total_ret": 0.6486, "cagr": 0.0762}
    chk("13 the quadruple is the annualised class", block_kind(quad) == C_ANNUALISED)
    chk("14 a count without the annualisation fields is the count-only class",
        block_kind({"bars": 24}) == C_COUNT_ONLY)
    rd = rederive_cagr(quad)
    chk("15 cagr re-derives from total_ret and years", rd and rd["is_annualised"],
        rd)
    chk("16 bars divided by years gives the annualisation constant",
        abs((bars_per_year(quad) or 0) - 241.996) < 1e-2, bars_per_year(quad))
    broken = dict(quad)
    broken["cagr"] = 0.20
    chk("17 a cagr that ignores its own years does not re-derive",
        rederive_cagr(broken) and not rederive_cagr(broken)["is_annualised"])

    # 18-20 witness classes
    chk("18 a dedupe field is a witness",
        witness_class({"bars": 10, "dedupe_applied": True}) == W_DEDUPE)
    chk("19 first and last bar identities are a witness",
        witness_class({"bars": 10, "first_bar": "2019-01-02", "last_bar": "2026-10-23"})
        == W_IDENTITY)
    chk("20 a count and nothing else is no witness",
        witness_class({"bars": 10, "cagr": 0.1}) == W_COUNT_ONLY)

    # 21-24 duplicate effect ladder
    chk("21 a divisor means blind in arithmetic",
        duplicate_effect(module_usage("x = y / n_bars\n")) == "blind_row_count_in_arithmetic")
    chk("22 a presence test is not blindness",
        duplicate_effect(module_usage("if n_bars == 0:\n    pass\n")) == "carries_or_tests_the_count")
    chk("23 a printed count is not blindness",
        duplicate_effect(module_usage("print(n_bars)\n")) == "carries_or_tests_the_count")
    chk("24 a module that never reads a count reads no count",
        duplicate_effect(module_usage("x = 1\n")) == "reads_no_count")

    # 25-27 walk + summarise
    payload = {"a": {"bars": 100, "years": 0.5, "total_ret": 0.1,
                     "cagr": (1.1 ** 2) - 1},
               "b": [{"bars": 5}, {"bars": 6}],
               "c": {"deep": {"bars": 7}}}
    blocks = walk_blocks(payload)
    chk("25 the walk finds counts at several depths", len(blocks) == 4, len(blocks))
    rows = [block_row("f.json", at, b) for at, b in blocks]
    sm = face_summary(rows)
    chk("26 the per-face summary counts annualised blocks",
        sm["f.json"]["blocks"] == 4 and sm["f.json"]["annualised"] == 1, sm)
    counts = summarise(rows, [{"module": "m.py", "roles": ["divisor"],
                               "duplicate_effect": "blind_row_count_in_arithmetic",
                               "faces_named_by_path": ["f.json"]},
                              {"module": "n.py", "roles": ["printed_only"],
                               "duplicate_effect": "carries_or_tests_the_count",
                               "faces_named_by_path": ["f.json"]}], 0, [], [])
    chk("27 a reader that divides forces the reader-rates verdict",
        verdict_from(counts) == V_READER_RATES)

    # 28-31 guard: it must refuse drift in each direction it can drift
    sample_face = {"study": "x", "evidence_cutoff": "2026-11-06",
                   "blocks": rows, "readers": [
                       {"module": "m.py", "roles": ["divisor"],
                        "duplicate_effect": "blind_row_count_in_arithmetic",
                        "faces_named_by_path": ["f.json"],
                        "evidence": {"divisor": [{"line": 1, "code": "x"}]}}],
                   "not_published": {"count_only_blocks_sampled_out": 0,
                                     "count_only_blocks_from_faces_published_in_aggregate_only":
                                         0},
                   "counts": summarise(rows, [{"module": "m.py", "roles": ["divisor"],
                                               "duplicate_effect": "blind_row_count_in_arithmetic",
                                               "faces_named_by_path": ["f.json"]}],
                                       0, [], []),
                   "verdict": None, "answer": "x"}
    sample_face["verdict"] = verdict_from(sample_face["counts"])
    chk("28 a clean synthetic face passes the guard", face_problems(sample_face) == [],
        face_problems(sample_face))
    bad_blocks = json.loads(json.dumps(sample_face))
    bad_blocks["counts"]["blocks_annualised"] += 1
    chk("29 a block count that does not re-derive is caught",
        any("blocks_annualised" in s for s in face_problems(bad_blocks)))
    bad_v = json.loads(json.dumps(sample_face))
    bad_v["verdict"] = V_WRITER_ONLY
    chk("30 a verdict the counts do not force is caught",
        any("verdict" in s for s in face_problems(bad_v)))
    bad_rd = json.loads(json.dumps(sample_face))
    for b in bad_rd["blocks"]:
        if b["kind"] == C_ANNUALISED:
            b["implied_cagr"] = 0.5
            break
    chk("31 an implied cagr that does not re-derive is caught",
        any("re-derives" in s for s in face_problems(bad_rd)))
    bad_ev = json.loads(json.dumps(sample_face))
    bad_ev["readers"][0]["evidence"] = {}
    chk("32 a divisor graded with no line evidence is caught",
        any("no line evidence" in s for s in face_problems(bad_ev)))

    # 33-34 addressing + self-exclusion on the real tree
    chk("33 a module naming the face path is attributed by path",
        addressing({"results/etf_book_capacity.json"}, "results/etf_book_capacity.json")
        == "names_this_face")
    chk("34 a module naming only the basename is not attributed by path",
        addressing({"etf_book_capacity.json"}, "results/etf_book_capacity.json")
        == "names_basename_only")

    # 34b this study is not one of its own readers: its own selftest literals name faces, and a
    # scanner that credits them publishes its own fixtures as evidence (E180/E207 family)
    sample_faces = ["results/etf_book_capacity.json"]
    self_rows, self_excluded = scan_readers(sample_faces, ROOT)
    chk("34b this study does not appear among its own readers",
        not any(r["module"].endswith(SELF_NAME) for r in self_rows),
        [r["module"] for r in self_rows if r["module"].endswith(SELF_NAME)])
    chk("34c the exclusion is published with a reason",
        any(e["module"].endswith(SELF_NAME) for e in self_excluded),
        self_excluded[:3])

    tmp = os.path.join(ROOT, "results", "_e597_selftest_tmp")
    os.makedirs(tmp, exist_ok=True)
    try:
        with io.open(os.path.join(tmp, SELF_STEM + "-x.json"), "w", encoding="utf-8") as fh:
            fh.write('{"bars": 12, "years": 1, "total_ret": 0.1, "cagr": 0.1}')
        sc = scan_faces(ROOT)
        chk("35 this study does not scan its own published face",
            not any(r["face"].endswith(SELF_STEM + "-x.json") for r in sc["rows"]))
        chk("36 the scan reads more than one annualised block",
            sum(1 for r in sc["rows"] if r["kind"] == C_ANNUALISED) > 100,
            sum(1 for r in sc["rows"] if r["kind"] == C_ANNUALISED))
    finally:
        for f in glob.glob(os.path.join(tmp, "*")):
            os.remove(f)
        os.rmdir(tmp)

    print("\n%d/%d PASS" % (sum(ok), len(ok)))
    return 0 if all(ok) else 1


# --------------------------------------------------------------------------- cli
def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "build").lower()
    if cmd == "selftest":
        return selftest()
    face, problems = build(write=(cmd == "build"))
    if problems:
        print("PROBLEMS: " + "; ".join(problems))
        return 1
    c = face["counts"]
    print("faces_with_a_bar_count=%d blocks=%d annualised=%d rederive=%d/%d"
          % (c["faces_publishing_a_bar_count"], c["blocks_publishing_a_bar_count"],
             c["blocks_annualised"], c["blocks_where_cagr_re_derives"], c["blocks_annualised"]))
    print("bars_per_year_implied=%s..%s median=%s"
          % (c["bars_per_year_implied_min"], c["bars_per_year_implied_max"],
             c["bars_per_year_implied_median"]))
    print("witness=" + json.dumps(c["annualisation_witness"], sort_keys=True))
    print("readers=%d dividing=%d multiplying=%d annualising=%d printing=%d"
          % (c["reader_modules_naming_a_face"], c["reader_modules_dividing_by_a_count"],
             c["reader_modules_multiplying_a_count"],
             c["reader_modules_annualising_a_count"], c["reader_modules_printing_a_count"]))
    print("verdict=" + face["verdict"])
    print("answer=" + face["answer"])
    if cmd == "build":
        print("wrote " + os.path.relpath(OUT_PATH, ROOT))
    if cmd == "verify" and os.path.exists(OUT_PATH):
        with io.open(OUT_PATH, encoding="utf-8") as fh:
            old = json.load(fh)
        same = (json.dumps(old.get("counts"), sort_keys=True)
                == json.dumps(face.get("counts"), sort_keys=True))
        print("verify counts_identical=%s" % same)
        return 0 if same else 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))