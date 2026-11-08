"""E566 (r1594 bm-b): does anyone who READS a chain receipt need to know how much of the chain it covers?

E562 settled that a killed run cannot leave a short receipt (every runner writes after the leg loop)
and E563 settled that 138 of the 159 short receipts are arbitrary subsets, so a reader holding one
cannot recover which legs it covers.  Before proposing a selection field, price the blindness:

  * how many in-repo sources NAME a receipt, how many WRITE one, and how many actually OPEN one;
  * of the openers, which ones compare the row count with the legs table (coverage-aware) and which
    ones reduce the rows they find to an rc verdict (blind: a 1-leg receipt reads as a green chain);
  * of the receipts each opener actually reads, how many were short against their own round's table
    (E561's join) -- i.e. the blindness is not hypothetical, it has already been printed.

Naming is not reading (E207/E470 family): 158 sources carry a receipt path and most of them are
report prose or a `git add` payload.  This study separates the three populations instead of folding
them into one "consumer" word.

Classes per source:
  * ``writes_a_receipt``      -- json.dump / open(...,'w') on a receipt path.
  * ``reads_the_payload``     -- json.load / open(read) / glob on a receipt path.
  * ``names_it_without_opening_it`` -- the path is a string in prose, a git payload list, a docstring.

Classes per reader (ordered, first match wins):
  * ``coverage_aware``        -- reads a row count AND joins it to a legs table (E561's own shape).
  * ``literal_denominator``   -- prints "N/<literal> rc0": the denominator is a constant in the source.
  * ``rc_only_summary``       -- filters rows on rc != 0 and prints what is left, no count check.
  * ``other_read``            -- opens the payload for something else (a round field, a total).

  python scripts/e566_receipt_coverage_consumer.py build      # write the dated face + latest
  python scripts/e566_receipt_coverage_consumer.py check      # re-derive from live sources, compare
  python scripts/e566_receipt_coverage_consumer.py verify     # re-derive, print problems
  python scripts/e566_receipt_coverage_consumer.py selftest   # fixtures only
"""
from __future__ import annotations

import ast
import hashlib
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
EVIDENCE_CUTOFF = "2026-11-08"
DATED_PREFIX = "RECEIPTCOVERAGE"
STATE_TILT = os.path.join(ROOT, "results", "state_tilt")
LATEST = os.path.join(STATE_TILT, "receiptcoverage_latest.json")
E561_FACE = os.path.join(STATE_TILT, "RECEIPTTABLE-2026-11-08.json")

RECEIPT_LITERAL = re.compile(r"_r[0-9-]+bm[abc]_s6_chain\.json")
RECEIPT_ANY = re.compile(r"s6_chain\.json")
RECEIPT_GLOB = re.compile(r"s6_chain")

SKIP_DIRS = {".git", ".codely-cli", "_quarantine", "__pycache__", "node_modules", "media"}

C_WRITES = "writes_a_receipt"
C_READS = "reads_the_payload"
C_NAMES = "names_it_without_opening_it"
C_UNPARSED = "the_source_cannot_be_parsed"
SOURCE_CLASSES = (C_WRITES, C_READS, C_NAMES, C_UNPARSED)

R_COVERAGE = "coverage_aware"
R_LITERAL = "literal_denominator"
R_RC_ONLY = "rc_only_summary"
R_OTHER = "other_read"
READER_CLASSES = (R_COVERAGE, R_LITERAL, R_RC_ONLY, R_OTHER)

V_READERS_ARE_AWARE = ("every_source_that_opens_a_receipt_also_reads_its_coverage_so_no_selection_field_is_owed")
V_SHORT_ALREADY_PRINTED = ("a_short_receipt_has_already_been_printed_as_the_whole_chain_so_coverage_blindness_has_a_price")
V_LATENT = ("the_operational_readers_hold_complete_receipts_so_the_gap_is_latent_not_absent")
V_NOBODY_READS = ("no_source_in_the_repo_opens_a_chain_receipt_so_coverage_costs_nothing_today")
V_BLIND = "the_population_could_not_be_measured_so_nothing_is_concluded"


# ---- git-free scanning ------------------------------------------------------------
def _parse(src):
    try:
        return ast.parse(src)
    except Exception:
        try:
            return ast.parse(src.lstrip("\ufeff"))
        except Exception:
            return None


_WRITE_MODES = ("w", "a", "wb", "ab", "x", "xb", "w+", "a+")


def _refs(tree):
    """Every string constant that names a receipt, with the call chain it sits in.

    The mode is decided from the *enclosing calls*, not from a word in the line: a path passed to
    ``git add`` is a name, a path passed to ``json.load`` is a read, and a path handed to
    ``open`` is read or written depending on its own mode argument.
    """
    out = []

    class V(ast.NodeVisitor):
        def __init__(self):
            self.stack = []

        def visit_Call(self, node):
            self.stack.append(node)
            self.generic_visit(node)
            self.stack.pop()

        def visit_Constant(self, node):
            v = node.value
            if isinstance(v, str) and RECEIPT_ANY.search(v):
                calls = [ast.unparse(c.func) for c in self.stack]
                joined = " ".join(calls)
                mode = C_NAMES
                if "dump" in joined or "write_text" in joined:
                    mode = C_WRITES
                elif any(("load" in c) or ("glob" in c) or ("listdir" in c) or ("iterdir" in c)
                         or ("scandir" in c) or ("read_text" in c) for c in calls):
                    mode = C_READS
                elif calls and calls[-1].endswith("open"):
                    args = [a for c in self.stack for a in c.args[1:]]
                    lit = [a.value for a in args if isinstance(a, ast.Constant)
                           and isinstance(a.value, str)]
                    mode = C_WRITES if any(m in _WRITE_MODES for m in lit) else C_READS
                out.append({"literal": v[:120], "line": node.lineno, "mode": mode,
                            "calls": calls[-3:]})
            self.generic_visit(node)

    V().visit(tree)
    return out


_DENOM = re.compile(r"(?:%d|\}|\d)\s*/\s*(\d{1,4})\s*(?:rc0|rc=|legs)")
_RC_ZERO = re.compile(r"!=\s*0\b|==\s*0\b")
_TABLE_JOIN = re.compile(r"table_at_its_round|s6_chain_bm[abc]|LEGS")
_ROW_COUNT = re.compile(r"len\(\s*(?:chain|rows|legs)\s*\)|len\([A-Za-z_]*chain[A-Za-z_]*\)")


def classify_reader(src):
    """Reader class from the source text alone.  Pure function: fixtures drive the selftest."""
    lines = src.splitlines()
    join_lines = [i + 1 for i, ln in enumerate(lines) if _TABLE_JOIN.search(ln)]
    count_lines = [i + 1 for i, ln in enumerate(lines) if _ROW_COUNT.search(ln)]
    denom_lines, denoms = [], []
    for i, ln in enumerate(lines):
        if not re.search(r"rc\b|chain|rows", ln):
            continue
        m = _DENOM.search(ln)
        if m:
            denom_lines.append(i + 1)
            denoms.append(int(m.group(1)))
    rc_lines = [i + 1 for i, ln in enumerate(lines)
                if _RC_ZERO.search(ln) and re.search(r"\brc\b|\[1\]|chain|legs", ln)]
    if join_lines and count_lines:
        cls = R_COVERAGE
    elif denom_lines:
        cls = R_LITERAL
    elif rc_lines:
        cls = R_RC_ONLY
    else:
        cls = R_OTHER
    return {
        "class": cls,
        "reads_a_row_count": bool(count_lines),
        "joins_a_legs_table": bool(join_lines),
        "literal_denominators": denoms,
        "evidence_lines": {
            "table_join": join_lines[:4],
            "row_count": count_lines[:4],
            "literal_denominator": denom_lines[:4],
            "rc_filter": rc_lines[:4],
        },
    }


def _named_literals(refs, mode=None):
    names = []
    for r in refs:
        if mode and r["mode"] != mode:
            continue
        for m in RECEIPT_LITERAL.findall(r["literal"]):
            if m not in names:
                names.append(m)
    return names


def scan():
    """Every *.py in the repo that carries a receipt path, classified.  Deterministic."""
    rows = []
    self_path = os.path.abspath(__file__)
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for fn in sorted(filenames):
            if not fn.endswith(".py"):
                continue
            path = os.path.join(dirpath, fn)
            if os.path.abspath(path) == self_path:
                continue
            try:
                with io.open(path, encoding="utf-8-sig", errors="replace") as fh:
                    src = fh.read()
            except Exception:
                continue
            if "s6_chain.json" not in src and not re.search(r"s6_chain\.json", src):
                continue
            rel = os.path.relpath(path, ROOT).replace("\\", "/")
            tree = _parse(src)
            if tree is None:
                rows.append({"file": rel, "source_class": C_UNPARSED, "refs": [],
                             "receipts_it_names": RECEIPT_LITERAL.findall(src)})
                continue
            refs = _refs(tree)
            if not refs:
                rows.append({"file": rel, "source_class": C_NAMES, "refs": [],
                             "receipts_it_names": RECEIPT_LITERAL.findall(src)})
                continue
            modes = {r["mode"] for r in refs}
            if C_READS in modes:
                cls = C_READS
            elif C_WRITES in modes:
                cls = C_WRITES
            else:
                cls = C_NAMES
            row = {"file": rel, "source_class": cls, "refs": refs,
                   "receipts_it_names": _named_literals(refs)}
            if cls == C_READS:
                row.update(classify_reader(src))
                row["receipts_it_reads"] = _named_literals(refs, C_READS)
                row["patterns_it_reads"] = [r["literal"] for r in refs
                                            if r["mode"] == C_READS
                                            and not RECEIPT_LITERAL.search(r["literal"])]
            if cls == C_WRITES:
                row["receipts_it_writes"] = _named_literals(refs, C_WRITES)
            rows.append(row)
    rows.sort(key=lambda r: r["file"])
    return rows


# ---- pricing against E561's join --------------------------------------------------
def read_join():
    """{file: {rows, table_at_its_round, class}} from E561's published face."""
    with io.open(E561_FACE, encoding="utf-8") as fh:
        face = json.load(fh)
    out = {}
    for r in face.get("rows") or []:
        if not isinstance(r, dict) or r.get("unparsed"):
            continue
        out[r.get("file")] = {"rows": r.get("rows"),
                              "table": r.get("table_at_its_round"),
                              "class": r.get("class")}
    return out, face


def price(rows):
    """For each reader, join the receipts it reads to their row count and their era table size."""
    join, _face = read_join()
    priced, unpriced, short_pairs, blind_short = [], [], [], []
    for r in rows:
        if r.get("source_class") != C_READS:
            continue
        for name in r.get("receipts_it_reads") or []:
            j = join.get(name)
            if not j:
                unpriced.append({"reader": r["file"], "receipt": name,
                                 "why": "not in E561's join (absent or unparsed)"})
                continue
            rec = {"reader": r["file"], "receipt": name, "rows": j["rows"],
                   "table_at_its_round": j["table"],
                   "join_class": j["class"]}
            priced.append(rec)
            if isinstance(j["rows"], int) and isinstance(j["table"], int) and j["rows"] < j["table"]:
                short_pairs.append(rec)
                if r.get("class") in (R_RC_ONLY, R_LITERAL):
                    blind_short.append(rec)
    return priced, unpriced, short_pairs, blind_short


def _sha16(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()[:16]


def build(write=True):
    rows = scan()
    priced, unpriced, short_pairs, blind_short = price(rows)
    _join, e561 = read_join()

    s = {"sources_scanned": len(rows)}
    for cls in SOURCE_CLASSES:
        s[cls] = sum(1 for r in rows if r.get("source_class") == cls)
    for cls in READER_CLASSES:
        s["readers_" + cls] = sum(1 for r in rows
                                  if r.get("source_class") == C_READS and r.get("class") == cls)
    s["reader_receipt_pairs_priced"] = len(priced)
    s["reader_receipt_pairs_unpriced"] = len(unpriced)
    s["pairs_where_the_receipt_was_short"] = len(short_pairs)
    s["pairs_where_the_receipt_had_zero_rows"] = sum(
        1 for p in priced if p.get("rows") == 0)
    s["pairs_where_a_blind_reader_read_a_short_receipt"] = len(blind_short)
    s["receipts_on_disk_in_e561"] = (e561.get("summary") or {}).get("receipts_on_disk")
    s["short_receipts_in_e561"] = (e561.get("summary") or {}).get("partial")
    s["blind_short_example"] = (sorted(blind_short, key=lambda p: (p["reader"], p["receipt"]))[0]
                                if blind_short else None)
    s["_source_class_sum"] = sum(s[c] for c in SOURCE_CLASSES)

    verdict, line = _verdict(s)
    face = {
        "card": "E566",
        "study": "E566",
        "dept": "research+engineering",
        "machine": "bm-b",
        "round": "r1594",
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "population_source": {
            "face": os.path.relpath(E561_FACE, ROOT).replace("\\", "/"),
            "sha16": _sha16(E561_FACE),
            "note": "E561's join supplies each receipt's row count and the legs table of its own "
                    "round; naming is separated from reading by AST ancestry, not by a word in "
                    "the line",
        },
        "summary": s,
        "rows": rows,
        "priced_pairs": priced,
        "unpriced_pairs": unpriced,
        "control_arms": _control_arms(),
        "verdict": verdict,
        "verdict_line": line,
        "note": "static only: no receipt is opened for its content beyond the scan of sources, no "
                "runner is executed, no receipt is rewritten; each reader row carries the evidence "
                "line numbers its class was derived from",
        "producers": {
            "script": "scripts/e566_receipt_coverage_consumer.py",
            "selftest": "python scripts/e566_receipt_coverage_consumer.py selftest",
            "card": "knowledge/METHODOLOGY_ASSETS.md E566",
        },
    }
    if write:
        _write(LATEST, face)
        _write(os.path.join(STATE_TILT, "%s-%s.json" % (DATED_PREFIX, EVIDENCE_CUTOFF)), face)
    return face


def _verdict(s):
    s = {"sources_scanned": 0, C_WRITES: 0, C_READS: 0, C_NAMES: 0, C_UNPARSED: 0,
         "reader_receipt_pairs_priced": 0,
         "pairs_where_a_blind_reader_read_a_short_receipt": 0,
         **s}
    head = ("%d sources carry a receipt path: %d write one, %d open one, %d only name it, %d do "
            "not parse."
            % (s["sources_scanned"], s[C_WRITES], s[C_READS], s[C_NAMES], s[C_UNPARSED]))
    if not s[C_READS]:
        return V_NOBODY_READS, head + " No source opens a receipt, so coverage cannot mislead a reader."
    readers = ", ".join("%s=%d" % (c, s["readers_" + c]) for c in READER_CLASSES)
    body = (" Of the %d readers: %s. %d (reader, receipt) pairs could be priced against E561's join; "
            "%d of those receipts were short against their own round's table (%d carried no rows at "
            "all) and %d short ones were read by a reader that prints an rc verdict without a count."
            % (s[C_READS], readers, s["reader_receipt_pairs_priced"],
               s["pairs_where_the_receipt_was_short"],
               s.get("pairs_where_the_receipt_had_zero_rows") or 0,
               s["pairs_where_a_blind_reader_read_a_short_receipt"]))
    if s["pairs_where_a_blind_reader_read_a_short_receipt"]:
        ex = s.get("blind_short_example") or {}
        tail = ""
        if ex.get("reader"):
            tail = (" For example %s printed %s, a %d-row receipt against the %d-leg table of its own "
                    "round." % (ex["reader"], ex["receipt"], ex.get("rows") or 0,
                                ex.get("table_at_its_round") or 0))
        return V_SHORT_ALREADY_PRINTED, head + body + tail
    blind = s["readers_" + R_RC_ONLY] + s["readers_" + R_LITERAL]
    if blind:
        return V_LATENT, head + body
    return V_READERS_ARE_AWARE, head + body


# ---- control arms (pure fixtures) --------------------------------------------------
FIX_COVERAGE = '''\
import json
face = json.load(open("results/state_tilt/RECEIPTTABLE-2026-11-08.json"))
rows = json.load(open("results/_r1bmb_s6_chain.json"))
n, table = len(rows), face["rows"][0]["table_at_its_round"]
print(n == table)
'''

FIX_LITERAL = '''\
import json
chain = json.load(open("results/_r1210bmc_s6_chain.json"))
bad = [x for x in chain if x["rc"] != 0]
print("S6 chain %d/39 rc0" % len(chain))
'''

FIX_RC_ONLY = '''\
import json
chain = json.load(open("results/_r2bmb_s6_chain.json"))
chain_rc = [(x.get("leg"), x.get("rc")) for x in chain]
nonzero = [x for x in chain_rc if x[1] != 0]
print("chain_nonzero", nonzero)
'''

FIX_OTHER = '''\
import json
face = json.load(open("results/_r3bmb_s6_chain.json"))
print(face["round"], face["total"])
'''

FIX_WRITE = '''\
import json
json.dump(out, open("results/_r4bmb_s6_chain.json", "w"))
'''

FIX_NAME = '''\
PAYLOAD = ["results/_r5bmb_s6_chain.json", "results/other.json"]
'''

FIX_GLOB_READ = '''\
import glob, json
for p in sorted(glob.glob("results/_r*bm*_s6_chain.json")):
    rows = json.load(open(p))
'''


def _mode_of(src):
    tree = _parse(src)
    if tree is None:
        return C_UNPARSED
    refs = _refs(tree)
    modes = {r["mode"] for r in refs}
    if C_READS in modes:
        return C_READS
    if C_WRITES in modes:
        return C_WRITES
    return C_NAMES


def _control_arms():
    return {
        "a_payload_read_is_a_read": _mode_of(FIX_RC_ONLY),
        "a_dump_is_a_write": _mode_of(FIX_WRITE),
        "a_path_in_a_payload_list_is_only_a_name": _mode_of(FIX_NAME),
        "a_glob_inside_json_load_is_a_read": _mode_of(FIX_GLOB_READ),
        "a_count_joined_to_a_table_is_coverage_aware": classify_reader(FIX_COVERAGE)["class"],
        "a_literal_denominator_is_not_coverage_aware": classify_reader(FIX_LITERAL)["class"],
        "an_rc_filter_without_a_count_is_blind": classify_reader(FIX_RC_ONLY)["class"],
        "an_unrelated_read_is_its_own_class": classify_reader(FIX_OTHER)["class"],
        "literal_denominators_are_carried_not_dropped":
            classify_reader(FIX_LITERAL)["literal_denominators"],
        "a_coverage_reader_carries_no_literal_denominator":
            classify_reader(FIX_COVERAGE)["literal_denominators"],
    }


def _check_arms():
    arms = _control_arms()
    want = {
        "a_payload_read_is_a_read": C_READS,
        "a_dump_is_a_write": C_WRITES,
        "a_path_in_a_payload_list_is_only_a_name": C_NAMES,
        "a_glob_inside_json_load_is_a_read": C_READS,
        "a_count_joined_to_a_table_is_coverage_aware": R_COVERAGE,
        "a_literal_denominator_is_not_coverage_aware": R_LITERAL,
        "an_rc_filter_without_a_count_is_blind": R_RC_ONLY,
        "an_unrelated_read_is_its_own_class": R_OTHER,
        "literal_denominators_are_carried_not_dropped": [39],
        "a_coverage_reader_carries_no_literal_denominator": [],
    }
    return ["%s -> %r (want %r)" % (k, arms.get(k), v) for k, v in want.items() if arms.get(k) != v]


# ---- face validation -------------------------------------------------------------
def _write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")


def face_problems(face):
    problems = []
    rows = face.get("rows") or []
    s = face.get("summary") or {}
    if s.get("sources_scanned") != len(rows):
        problems.append("summary.sources_scanned %r != %d rows" % (s.get("sources_scanned"), len(rows)))
    for cls in SOURCE_CLASSES:
        got = sum(1 for r in rows if r.get("source_class") == cls)
        if s.get(cls) != got:
            problems.append("summary.%s %r != %d in rows" % (cls, s.get(cls), got))
    if sum(s.get(c, 0) for c in SOURCE_CLASSES) != len(rows):
        problems.append("a row is in no source class or in two")
    for cls in READER_CLASSES:
        got = sum(1 for r in rows if r.get("source_class") == C_READS and r.get("class") == cls)
        if s.get("readers_" + cls) != got:
            problems.append("summary.readers_%s %r != %d" % (cls, s.get("readers_" + cls), got))
    for r in rows:
        if r.get("source_class") == C_READS and r.get("class") not in READER_CLASSES:
            problems.append("%s: a reader carries class %r" % (r.get("file"), r.get("class")))
        if r.get("source_class") != C_READS and "class" in r:
            problems.append("%s: a non-reader carries a reader class" % r.get("file"))
        for ref in r.get("refs") or []:
            if ref.get("mode") not in (C_WRITES, C_READS, C_NAMES):
                problems.append("%s: a reference has mode %r" % (r.get("file"), ref.get("mode")))
            if not isinstance(ref.get("line"), int):
                problems.append("%s: a reference carries no line" % r.get("file"))
    priced = face.get("priced_pairs") or []
    short = [p for p in priced if isinstance(p.get("rows"), int)
             and isinstance(p.get("table_at_its_round"), int)
             and p["rows"] < p["table_at_its_round"]]
    if s.get("reader_receipt_pairs_priced") != len(priced):
        problems.append("priced pair counter does not re-derive")
    if s.get("pairs_where_the_receipt_was_short") != len(short):
        problems.append("short pair counter does not re-derive")
    blind = {r["file"] for r in rows if r.get("source_class") == C_READS
             and r.get("class") in (R_RC_ONLY, R_LITERAL)}
    blind_short = [p for p in short if p.get("reader") in blind]
    if s.get("pairs_where_a_blind_reader_read_a_short_receipt") != len(blind_short):
        problems.append("blind-short pair counter does not re-derive")
    if s.get("pairs_where_the_receipt_had_zero_rows") != sum(
            1 for p in priced if p.get("rows") == 0):
        problems.append("zero-row pair counter does not re-derive")
    want_ex = sorted(blind_short, key=lambda p: (p["reader"], p["receipt"]))[0] if blind_short else None
    if s.get("blind_short_example") != want_ex:
        problems.append("the published example does not re-derive from the pair lists")
    if s.get("reader_receipt_pairs_priced") != len(priced) or \
            s.get("reader_receipt_pairs_unpriced") != len(face.get("unpriced_pairs") or []):
        problems.append("pair counters disagree with the pair lists")
    exp_verdict, exp_line = _verdict(s)
    if face.get("verdict") != exp_verdict:
        problems.append("verdict %r != re-derived %r" % (face.get("verdict"), exp_verdict))
    if face.get("verdict_line") != exp_line:
        problems.append("verdict_line does not re-derive")
    if not (face.get("population_source") or {}).get("sha16"):
        problems.append("the population is not pinned to a vintage")
    if face.get("control_arms") != _control_arms():
        problems.append("control arms do not re-derive")
    for r in rows:
        if r.get("source_class") == C_READS:
            if not r.get("receipts_it_reads") and not r.get("patterns_it_reads"):
                problems.append("%s: a reader names no receipt it reads" % r.get("file"))
            if r.get("class") != R_OTHER and \
                    not (r.get("evidence_lines") or {}).get("rc_filter") and \
                    not (r.get("evidence_lines") or {}).get("row_count") and \
                    not (r.get("evidence_lines") or {}).get("table_join") and \
                    not (r.get("evidence_lines") or {}).get("literal_denominator"):
                problems.append("%s: a reader class has no evidence line" % r.get("file"))
    return problems


def selftest():
    bad = list(_check_arms())
    face = build(write=False)
    bad.extend(face_problems(face))
    doc = json.loads(json.dumps(face))
    for r in doc.get("rows") or []:
        if r.get("source_class") == C_READS:
            r["class"] = R_OTHER
            break
    if not face_problems(doc):
        bad.append("a hand-written reader class was accepted")
    doc = json.loads(json.dumps(face))
    doc["verdict"] = "a_verdict_this_study_never_publishes"
    if not face_problems(doc):
        bad.append("a hand-written verdict was accepted")
    doc = json.loads(json.dumps(face))
    if doc.get("priced_pairs"):
        doc["priced_pairs"][0]["rows"] = 0
        doc["priced_pairs"][0]["table_at_its_round"] = 0
        if not face_problems(doc):
            bad.append("a doctored pair was accepted")
    if bad:
        print("SELFTEST FAIL: " + "; ".join(bad)[:600])
        return 1
    s = face["summary"]
    print("SELFTEST PASS: %d arms + %d sources; writes=%d reads=%d names=%d unparsed=%d; "
          "readers: aware=%d literal=%d rc_only=%d other=%d; priced=%d short=%d blind_short=%d"
          % (len(_control_arms()), len(face["rows"]), s[C_WRITES], s[C_READS], s[C_NAMES],
             s[C_UNPARSED], s["readers_" + R_COVERAGE], s["readers_" + R_LITERAL],
             s["readers_" + R_RC_ONLY], s["readers_" + R_OTHER],
             s["reader_receipt_pairs_priced"], s["pairs_where_the_receipt_was_short"],
             s["pairs_where_a_blind_reader_read_a_short_receipt"]))
    return 0


def check():
    """Re-derive from live sources and compare with the published face.

    Line numbers are published as evidence but are NOT gated: a comment added above a string
    moves every number below it in a 2,000-line file, and a gate that goes red on an unrelated
    edit to the runner would be red every round (it is edited every round).  What is gated is the
    classification: which sources read, which only name, and how the readers were classed.
    """
    fresh = build(write=False)
    try:
        with io.open(LATEST, encoding="utf-8") as fh:
            published = json.load(fh)
    except Exception as exc:
        print("CHECK FAIL: the face cannot be read: %s" % exc)
        return 1
    problems = face_problems(published)
    for key in ("verdict", "verdict_line", "summary", "card"):
        if fresh.get(key) != published.get(key):
            problems.append("live %s disagrees with the published face" % key)
    fp = {r["file"]: r for r in fresh.get("rows") or []}
    pp = {r["file"]: r for r in published.get("rows") or []}
    for f in sorted(set(fp) - set(pp)):
        problems.append("%s names a receipt now but is not in the face" % f)
    for f in sorted(set(pp) - set(fp)):
        problems.append("%s is in the face but no longer names a receipt" % f)
    for f in sorted(set(fp) & set(pp)):
        a, b = fp[f], pp[f]
        for key in ("source_class", "class", "receipts_it_reads", "receipts_it_names"):
            if a.get(key) != b.get(key):
                problems.append("%s: live %s %r != published %r"
                                % (f, key, a.get(key), b.get(key)))
    if fresh.get("priced_pairs") != published.get("priced_pairs"):
        problems.append("the priced pairs do not re-derive")
    if problems:
        print("CHECK FAIL: %d problems; first=%s" % (len(problems), problems[0][:300]))
        return 1
    print("CHECK PASS: %d sources re-derive, verdict=%s"
          % (len(published.get("rows") or []), published.get("verdict")))
    return 0


def verify():
    problems = face_problems(build(write=False))
    print(json.dumps({"problems": problems[:10], "n": len(problems)}, ensure_ascii=False))
    return 0 if not problems else 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    action = argv[0] if argv else "build"
    if action == "build":
        face = build(write=True)
        s = face["summary"]
        print("BUILT %s: %d sources | writes=%d reads=%d names=%d unparsed=%d"
              % (os.path.relpath(LATEST, ROOT), len(face["rows"]), s[C_WRITES], s[C_READS],
                 s[C_NAMES], s[C_UNPARSED]))
        print("READERS: aware=%d literal=%d rc_only=%d other=%d | pairs priced=%d short=%d "
              "blind_short=%d"
              % (s["readers_" + R_COVERAGE], s["readers_" + R_LITERAL],
                 s["readers_" + R_RC_ONLY], s["readers_" + R_OTHER],
                 s["reader_receipt_pairs_priced"], s["pairs_where_the_receipt_was_short"],
                 s["pairs_where_a_blind_reader_read_a_short_receipt"]))
        print("VERDICT: %s" % face["verdict"])
        return 0
    if action == "check":
        return check()
    if action == "verify":
        return verify()
    if action == "selftest":
        return selftest()
    print("unknown action %r (build|check|verify|selftest)" % action)
    return 2


if __name__ == "__main__":
    sys.exit(main())