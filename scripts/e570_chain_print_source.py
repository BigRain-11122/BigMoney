"""E570 (r1596 bm-b): where does the printed chain count come from?

E561 priced the receipt *field* (``legs_total`` in the bm-b envelope is ``len(rows)``; the other
two runners publish no such field at all).  E566/E567 then priced the prose and found sentences
that understate their round's table.  Neither asked the source-level question this card poses:

    the sentence ``chain: N/M rc0`` -- is M the length of the very object that was just written
    to the receipt, or a literal, or a counter that can drift away from the file?

If every printed number is read from the written object, then a sentence can never disagree with
its own receipt by arithmetic drift; the only way it can understate is a *population* choice
(``--only``, or a chain that stopped early), which is a different defect class and must be named
as such.  That is what makes this study worth a face: it removes a hypothesis and localises the
remaining one.

The trace is mechanical and re-derivable from what the face stores:

  * the population is the three runner sources at HEAD, pinned by sha16;
  * the print statement is found by SHApe (a statically readable text containing a chain word and
    a slash), then each placeholder is classified by the expression that fills it and by the
    binding of every name it reads (``len(out)`` where ``out`` is the json.dump argument;
    ``len(out)-len(bad)`` where ``bad`` is a comprehension over that same ``out``;
    ``payload["legs_rc0"]`` where ``payload`` is the dumped envelope);
  * two live arms beside the static one: recount every receipt on disk for the count field each
    runner writes (by payload, not by trust), and machine-read E567's claim face to say how the
    printed denominators in the prose actually compare with their receipts.

  python scripts/e570_chain_print_source.py build      # write the dated face + latest
  python scripts/e570_chain_print_source.py check      # re-derive from live sources, compare
  python scripts/e570_chain_print_source.py verify     # re-derive, print problems
  python scripts/e570_chain_print_source.py selftest   # fixtures only
"""
from __future__ import annotations

import ast
import glob
import hashlib
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
EVIDENCE_CUTOFF = "2026-11-08"
DATED_PREFIX = "CHAINPRINTSOURCE"
STATE_TILT = os.path.join(ROOT, "results", "state_tilt")
LATEST = os.path.join(STATE_TILT, "chainprintsource_latest.json")
DATED = os.path.join(STATE_TILT, "%s-%s.json" % (DATED_PREFIX, EVIDENCE_CUTOFF))
CLAIMS_FACE = os.path.join(STATE_TILT, "CHAINCLAIM-2026-11-08.json")

RUNNERS = [("a", "Tools/s6_chain_bma.py"),
           ("b", "Tools/s6_chain_bmb.py"),
           ("c", "Tools/s6_chain_bmc.py")]

# the receipt corpus this repo's chain runners write (E561's population, name-derived)
RECEIPT_GLOB = os.path.join(ROOT, "results", "_r*bm*_s6_chain.json")

# ---- the trace rule (echoed verbatim into the face so a reader can refute it) ----
PRINT_RULE = {
    "chain_words": ["s6", "chain"],
    "count_shape": ["/", "rc0", "rc=0"],
    "how_a_print_is_found": ("a call to print whose argument is statically readable "
                             "(constant, f-string, or %-format)"),
    "how_thedump_is_found": ("the nearest ast.Call to <json>.dump in the same function that "
                             "comes before the print and whose path names an s6_chain receipt"),
    "how_a_name_is_bound": ("the last assignment to that name above the print, in the same "
                            "function, at any nesting depth; a list-comprehension over the "
                            "dumped object is what makes a difference of lengths legitimate"),
}

# ---- origin classes -------------------------------------------------------------
READ_PAYLOAD = "read_from_the_payload_that_is_written"
LENGTH_WRITTEN = "the_length_of_the_rows_the_runner_writes"
DIFF_MINUS_NONZERO = "the_written_rows_minus_their_own_nonzero_rows"
THE_OBJECT = "the_written_object_itself"
LITERAL = "a_literal_in_the_source"
NOT_FROM_OBJECT = "an_expression_whose_value_is_not_read_from_the_written_object"
ORIGIN_CLASSES = (READ_PAYLOAD, LENGTH_WRITTEN, DIFF_MINUS_NONZERO, THE_OBJECT, LITERAL,
                  NOT_FROM_OBJECT)
FROM_PAYLOAD = (READ_PAYLOAD, LENGTH_WRITTEN, DIFF_MINUS_NONZERO)

V_ALL_FROM_PAYLOAD = ("every_printed_chain_count_is_read_from_the_object_its_runner_writes_so_"
                      "a_sentence_cannot_drift_from_its_own_receipt")
V_SOME_OUTSIDE = ("some_printed_chain_count_is_not_read_from_the_object_its_runner_writes")
V_NOTHING_PRINTED = "no_runner_prints_a_statically_readable_chain_count_so_nothing_is_concluded"


# ---- physics: pure functions (fixtures drive the selftest) -----------------------
def derive_kind(expr_kind, reads, bindings, dump_target):
    """The origin class, re-derivable from the stored fields of a row."""
    if expr_kind == "constant_int":
        return LITERAL
    if expr_kind == "subscript_of":
        return READ_PAYLOAD if reads.split(".", 1)[0] == dump_target else NOT_FROM_OBJECT
    if expr_kind in ("len_of_name", "len_of_subscript"):
        root = reads.split(".", 1)[0]
        return LENGTH_WRITTEN if root == dump_target else NOT_FROM_OBJECT
    if expr_kind == "name":
        return THE_OBJECT if reads == dump_target else NOT_FROM_OBJECT
    if expr_kind == "difference_of_two_lengths":
        left, right = (reads.split("|") + ["", ""])[:2]
        if left == dump_target and (bindings or {}).get(right) == "comprehension_over:%s" % dump_target:
            return DIFF_MINUS_NONZERO
        return NOT_FROM_OBJECT
    return NOT_FROM_OBJECT


def classify_expr(node, bindings):
    """(expr_kind, reads) for one placeholder expression."""
    if isinstance(node, ast.Constant) and isinstance(node.value, int):
        return "constant_int", str(node.value)
    if isinstance(node, ast.Subscript):
        base = node.value.id if isinstance(node.value, ast.Name) else ast.unparse(node.value)
        key = node.slice
        key = key.value if isinstance(key, ast.Constant) else ast.unparse(key)
        return "subscript_of", "%s.%s" % (base, key)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "len":
        if len(node.args) == 1:
            arg = node.args[0]
            if isinstance(arg, ast.Name):
                return "len_of_name", arg.id
            if isinstance(arg, ast.Subscript):
                base = arg.value.id if isinstance(arg.value, ast.Name) else ast.unparse(arg.value)
                key = arg.slice
                key = key.value if isinstance(key, ast.Constant) else ast.unparse(key)
                return "len_of_subscript", "%s.%s" % (base, key)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Sub):
        left, right = node.left, node.right
        if (isinstance(left, ast.Call) and isinstance(right, ast.Call)
                and isinstance(left.func, ast.Name) and isinstance(right.func, ast.Name)
                and left.func.id == "len" and right.func.id == "len"
                and left.args and right.args
                and isinstance(left.args[0], ast.Name) and isinstance(right.args[0], ast.Name)):
            return "difference_of_two_lengths", "%s|%s" % (left.args[0].id, right.args[0].id)
    if isinstance(node, ast.Name):
        return "name", node.id
    return "unparsed", ast.unparse(node)[:80]


def static_text(node):
    """(text, [placeholder nodes]) for a statically readable print argument."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value, []
    if isinstance(node, ast.JoinedStr):
        parts, phs = [], []
        for v in node.values:
            if isinstance(v, ast.Constant):
                parts.append(str(v.value))
            elif isinstance(v, ast.FormattedValue):
                phs.append(v.value)
                parts.append("{?}")
            else:
                return None, []
        return "".join(parts), phs
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod):
        if isinstance(node.left, ast.Constant) and isinstance(node.left.value, str):
            right = node.right
            elts = list(right.elts) if isinstance(right, ast.Tuple) else [right]
            conv = re.compile(r"%(?!%)[-+ #0]*\d*(?:\.\d+)?[diouxXeEfFgGcrsa]")
            return conv.sub("{?}", node.left.value), elts
    return None, []


def is_chain_sentence(text):
    low = (text or "").lower()
    return (any(w in low for w in PRINT_RULE["chain_words"])
            and any(s in low for s in PRINT_RULE["count_shape"]))


def _last_assigns(func):
    """name -> the assignment statement that last binds it (list of (lineno, node))."""
    found = {}
    for node in ast.walk(func):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    found.setdefault(t.id, []).append((node.lineno, node.value))
    return found


def binding_kind(value, dump_target):
    if isinstance(value, ast.ListComp):
        iters = value.generators
        if iters and isinstance(iters[0].iter, ast.Name) and iters[0].iter.id == dump_target:
            return "comprehension_over:%s" % dump_target
        return "a_comprehension_over_something_else"
    if isinstance(value, ast.List):
        return "a_list_literal"
    if isinstance(value, ast.Dict):
        return "a_dict_literal"
    return "other"


def strip_bom(text):
    """ast.parse refuses a leading U+FEFF; one of the three runners opens with one."""
    return text[1:] if text.startswith("\ufeff") else text


def count_positions(body):
    """The two placeholder indices either side of the slash -- a numerator and a denominator.

    A chain sentence also prints a path and an elapsed time; those are not counts and are not
    part of this population.  The pair is found in the static text, not from the argument order,
    so a reordered print is still read the same way.
    """
    slots = [m.start() for m in re.finditer(r"\{\?\}", body)]
    if len(slots) < 2:
        return []
    slash = body.find("/", slots[0])
    if slash < 0:
        return []
    before = [i for i, pos in enumerate(slots) if pos < slash]
    after = [i for i, pos in enumerate(slots) if pos > slash]
    if not before or not after:
        return []
    return [before[-1], after[0]]


def trace_source(text, name):
    """Every printed chain count in one runner source, with its origin."""
    tree = ast.parse(strip_bom(text))
    rows = []
    prints_seen = 0
    dump_calls = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                and node.func.attr == "dump" and node.args:
            dump_calls.append((node.lineno, node))
    for func in [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]:
        assigns = _last_assigns(func)
        for node in ast.walk(func):
            if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                    and node.func.id == "print" and node.args):
                continue
            prints_seen += 1
            body, phs = static_text(node.args[0])
            if body is None or not is_chain_sentence(body):
                continue
            dump = None
            for lineno, call in sorted(dump_calls):
                if lineno < node.lineno:
                    dump = call
            dump_target = None
            dump_kind = None
            dump_keys = []
            if dump is not None and isinstance(dump.args[0], ast.Name):
                dump_target = dump.args[0].id
                cands = [v for ln, v in assigns.get(dump_target, []) if ln < node.lineno]
                if cands:
                    v = cands[-1]
                    dump_kind = "dict" if isinstance(v, ast.Dict) else (
                        "list" if isinstance(v, ast.List) else type(v).__name__)
                    if isinstance(v, ast.Dict):
                        dump_keys = [k.value for k in v.keys
                                     if isinstance(k, ast.Constant) and isinstance(k.value, str)]
            pair = count_positions(body)
            if not pair:
                continue
            for i in pair:
                if i >= len(phs):
                    continue
                ph = phs[i]
                expr_kind, reads = classify_expr(ph, assigns)
                bindings = {}
                for nm in reads.replace("|", ".").split("."):
                    if nm and nm != dump_target:
                        vals = [v for ln, v in assigns.get(nm, []) if ln < node.lineno]
                        if vals:
                            bindings[nm] = binding_kind(vals[-1], dump_target)
                rows.append({
                    "runner": name,
                    "line": node.lineno,
                    "sentence": body[:200],
                    "placeholder_index": i,
                    "expression": ast.unparse(ph)[:120],
                    "expr_kind": expr_kind,
                    "reads": reads,
                    "bindings": bindings,
                    "dump_target": dump_target,
                    "dump_kind": dump_kind,
                    "dump_keys": dump_keys,
                    "dump_line": (dump.lineno if dump is not None else None),
                    "origin_kind": derive_kind(expr_kind, reads, bindings, dump_target),
                })
    return rows, prints_seen


# ---- the three live arms --------------------------------------------------------
def read_receipts():
    """Recount every receipt on disk: does the file's own count match its own rows?"""
    out = []
    for path in sorted(glob.glob(RECEIPT_GLOB)):
        base = os.path.basename(path)
        m = re.match(r"^_r(.*?)bm([abc])_s6_chain\.json$", base)
        entry = {"file": base, "machine": (m.group(2) if m else None),
                 "rows": None, "count_fields": {}, "shape": None, "unparsed": None}
        try:
            data = json.load(io.open(path, encoding="utf-8-sig"))
        except Exception as exc:
            entry["unparsed"] = str(exc)[:80]
            out.append(entry)
            continue
        if isinstance(data, list):
            entry["shape"] = "a_bare_list_of_rows"
            rows, fields = data, {}
        elif isinstance(data, dict):
            rows = None
            for k in ("legs", "rows", "results"):
                if isinstance(data.get(k), list):
                    rows = data[k]
                    break
            entry["shape"] = "an_envelope_with_rows" if rows is not None else "an_envelope_without_rows"
            fields = {k: v for k, v in data.items()
                      if k in ("legs_total", "legs_rc0") and isinstance(v, int)}
            rows = rows or []
        else:
            entry["shape"] = "neither_a_list_nor_an_envelope"
            rows, fields = [], {}
        entry["rows"] = len(rows)
        entry["nonzero_rows"] = sum(1 for r in rows
                                    if isinstance(r, dict) and r.get("rc") not in (0, None))
        entry["count_fields"] = fields
        out.append(entry)
    return out


def summarize_receipts(receipts):
    """Per runner: does the file's own count agree with a recount of its own rows?

    A field that is *absent* is not a field that disagrees -- the two are counted apart, because
    a missing rc0 in an older envelope is not evidence of arithmetic drift.
    """
    agg = {}
    for name, _rel in RUNNERS:
        mine = [r for r in receipts if r["machine"] == name]
        with_total = [r for r in mine if "legs_total" in (r["count_fields"] or {})]
        with_rc0 = [r for r in mine if "legs_rc0" in (r["count_fields"] or {})]
        agg[name] = {
            "receipts": len(mine),
            "bare_lists": sum(1 for r in mine if r["shape"] == "a_bare_list_of_rows"),
            "envelopes_without_a_count": sum(
                1 for r in mine if r["shape"] == "an_envelope_without_rows"),
            "envelopes_with_rows_and_no_count": (
                sum(1 for r in mine if r["shape"] == "an_envelope_with_rows")
                - len(with_total)),
            "carrying_legs_total": len(with_total),
            "carrying_legs_rc0": len(with_rc0),
            "legs_total_agrees_with_the_recount": sum(
                1 for r in with_total if r["count_fields"]["legs_total"] == r["rows"]),
            "legs_total_differs_from_the_recount": sum(
                1 for r in with_total if r["count_fields"]["legs_total"] != r["rows"]),
            "legs_rc0_agrees_with_the_recount": sum(
                1 for r in with_rc0
                if r["count_fields"]["legs_rc0"] == r["rows"] - r.get("nonzero_rows", 0)),
            "legs_rc0_differs_from_the_recount": sum(
                1 for r in with_rc0
                if r["count_fields"]["legs_rc0"] != r["rows"] - r.get("nonzero_rows", 0)),
            "unparsed": sum(1 for r in mine if r["unparsed"]),
        }
    return agg


def summarize_claims():
    """Machine-read E567's claim face: how the printed denominators compare with their receipts."""
    try:
        face = json.load(io.open(CLAIMS_FACE, encoding="utf-8"))
    except Exception as exc:
        return {"read": False, "error": str(exc)[:120]}
    claims = face.get("claims") or []
    agg = {}
    for name, _rel in RUNNERS:
        mine = [c for c in claims if c.get("machine") == name]
        judged = [c for c in mine if isinstance(c.get("denominator_equals_receipt_rows"), bool)]
        agg[name] = {
            "claims": len(mine),
            "judged_against_a_receipt": len(judged),
            "denominator_equals_its_receipt_rows": sum(
                1 for c in judged if c["denominator_equals_receipt_rows"]),
            "denominator_below_its_receipt_rows": sum(
                1 for c in judged if not c["denominator_equals_receipt_rows"]),
            "numerator_below_the_receipt_rc0_rows": sum(
                1 for c in judged if c.get("numerator_equals_receipt_rc0_rows") is False),
        }
    return {"read": True,
            "face": os.path.relpath(CLAIMS_FACE, ROOT).replace(os.sep, "/"),
            "face_sha16": _sha16(CLAIMS_FACE),
            "per_machine": agg}


# ---- face construction ----------------------------------------------------------
def _sha16(path):
    try:
        with io.open(path, "rb") as fh:
            return hashlib.sha256(fh.read()).hexdigest()[:16]
    except Exception:
        return ""


def _verdict(summary_rows, sources):
    if not summary_rows:
        return V_NOTHING_PRINTED
    outside = [k for k in ORIGIN_CLASSES
               if k not in FROM_PAYLOAD and summary_rows.get(k)]
    return V_SOME_OUTSIDE if outside else V_ALL_FROM_PAYLOAD


def _verdict_line(rows, summary_rows, runners, receipts, claims):
    det = summary_rows.get(LENGTH_WRITTEN, 0)
    dif = summary_rows.get(DIFF_MINUS_NONZERO, 0)
    pay = summary_rows.get(READ_PAYLOAD, 0)
    bare = sum(v["bare_lists"] for v in receipts.values())
    envless = sum(v["envelopes_without_a_count"]
                  + v["envelopes_with_rows_and_no_count"] for v in receipts.values())
    withf = sum(v["carrying_legs_total"] for v in receipts.values())
    bad = sum(v["legs_total_differs_from_the_recount"] + v["legs_rc0_differs_from_the_recount"]
              for v in receipts.values())
    judged = sum(v["judged_against_a_receipt"] for v in
                 (claims.get("per_machine") or {}).values())
    below = sum(v["denominator_below_its_receipt_rows"] for v in
                (claims.get("per_machine") or {}).values())
    return ("%d runners / %d printed chain numbers: %d read from the payload, %d the length of "
            "the written rows, %d rows-minus-nonzero, %d literal, %d outside the written object; "
            "%d receipts carry a count field and %d agree with a recount of their own rows (%d "
            "disagree); %d bare lists and %d envelopes carry no count; of %d sentences E567 could "
            "judge against their receipt, %d equal it and %d print less"
            % (len(runners), len(rows), pay, det, dif,
               summary_rows.get(LITERAL, 0), summary_rows.get(NOT_FROM_OBJECT, 0),
               withf, withf - bad, bad, bare, envless, judged, judged - below, below))


def _sources(texts):
    out = []
    for name, rel in RUNNERS:
        path = os.path.join(ROOT, rel)
        text = texts[name]
        rows, prints = trace_source(text, name)
        out.append({
            "runner": name,
            "path": rel,
            "sha16": _sha16(path),
            "has_bom": text.startswith("\ufeff"),
            "lines": len(text.splitlines()),
            "print_calls": prints,
            "chain_sentences": len({r["line"] for r in rows}),
            "printed_numbers": len(rows),
            "dump_target": rows[0]["dump_target"] if rows else None,
            "dump_kind": rows[0]["dump_kind"] if rows else None,
            "writes_count_fields": bool(rows and rows[0]["dump_keys"]
                                        and any(k in rows[0]["dump_keys"]
                                                for k in ("legs_total", "legs_rc0"))),
        })
    return out


def build(write=True):
    texts = {}
    for name, rel in RUNNERS:
        with io.open(os.path.join(ROOT, rel), encoding="utf-8", errors="replace") as fh:
            texts[name] = fh.read()
    rows = []
    for name, _rel in RUNNERS:
        r, _prints = trace_source(texts[name], name)
        rows.extend(r)
    receipts = read_receipts()
    rsum = summarize_receipts(receipts)
    claims = summarize_claims()
    sources = _sources(texts)

    summary = {"printed_numbers": len(rows),
               "runners": len(sources),
               "runners_printing_a_chain_count": len({r["runner"] for r in rows}),
               "sentences": len({(r["runner"], r["line"]) for r in rows}),
               "runners_whose_receipt_carries_a_count_field": sum(
                   1 for s in sources if s["writes_count_fields"]),
               "receipts_on_disk": len(receipts),
               "receipts_carrying_legs_total": sum(v["carrying_legs_total"]
                                                   for v in rsum.values()),
               "receipts_carrying_legs_rc0": sum(v["carrying_legs_rc0"]
                                                 for v in rsum.values()),
               "receipts_with_no_count_field": sum(
                   v["bare_lists"] + v["envelopes_without_a_count"]
                   + v["envelopes_with_rows_and_no_count"] for v in rsum.values()),
               "receipts_whose_total_disagrees_with_their_rows": sum(
                   v["legs_total_differs_from_the_recount"] for v in rsum.values()),
               "receipts_whose_rc0_disagrees_with_their_rows": sum(
                   v["legs_rc0_differs_from_the_recount"] for v in rsum.values()),
               "receipts_unparsed": sum(v["unparsed"] for v in rsum.values())}
    for cls in ORIGIN_CLASSES:
        summary[cls] = sum(1 for r in rows if r["origin_kind"] == cls)
    summary["printed_numbers_read_from_the_written_object"] = sum(
        summary.get(k, 0) for k in FROM_PAYLOAD)

    face = {
        "card": "E570",
        "study": "E570",
        "dept": "research+engineering",
        "machine": "bm-b",
        "round": "r1596",
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "population_source": {"runners": [rel for _n, rel in RUNNERS],
                              "sha16": {rel: _sha16(os.path.join(ROOT, rel)) for _n, rel in RUNNERS},
                              "receipts": "results/_r<round>bm<a|b|c>_s6_chain.json",
                              "claims_face": claims.get("face")},
        "print_rule": PRINT_RULE,
        "sources": sources,
        "rows": rows,
        "receipt_arm": rsum,
        "claims_arm": claims,
        "control_arms": control_arms(),
        "summary": summary,
        "verdict": _verdict(summary, sources),
        "verdict_line": "",
        "producers": {"script": "scripts/e570_chain_print_source.py",
                      "selftest": "python scripts/e570_chain_print_source.py selftest",
                      "card": "knowledge/METHODOLOGY_ASSETS.md E570"},
        "note": ("the origin class is decided by the expression and by the binding of every name "
                 "it reads, both stored per row, so `check` can re-derive it without re-parsing"),
    }
    face["verdict_line"] = _verdict_line(rows, summary, sources, rsum, claims)
    if write:
        _write(DATED, face)
        _write(LATEST, face)
    return face


def _write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")


# ---- control arms ---------------------------------------------------------------
def _fixture(text, dump_target, dump_kind="list", dump_keys=None):
    src = ("import json\n"
           "def main():\n"
           "    dump = object()\n"
           "    payload = {'legs': dump, 'legs_total': 1, 'legs_rc0': 1}\n"
           "    out = [1, 2]\n"
           "    bad = [o for o in out if o]\n"
           "    ok, total = 1, 2\n"
           "    json.dump(%s, open('results/_r0bmx_s6_chain.json', 'w'))\n"
           "    %s\n" % (dump_target, "\n    ".join(text.split("\n"))))
    rows, _prints = trace_source(src, "x")
    return [r["origin_kind"] for r in rows]


def control_arms():
    arms = {}
    arms["a_payload_field_is_read_from_the_payload"] = _fixture(
        "print('S6 %d/%d rc=0' % (payload['legs_rc0'], payload['legs_total']))", "payload")
    arms["an_f_string_payload_field_is_read_from_the_payload"] = _fixture(
        "print(f'chain: {payload[\"legs_rc0\"]}/{payload[\"legs_total\"]} rc0')", "payload")
    arms["the_length_of_the_dumped_list_is_the_written_rows"] = _fixture(
        "print(f'chain: {len(out)}/{len(out)} rc0')", "out")
    arms["the_length_of_the_dumped_envelopes_rows_is_the_written_rows"] = _fixture(
        "print(f'chain: {len(payload[\"legs\"])}/{len(payload[\"legs\"])} rc0')", "payload")
    arms["the_written_rows_minus_a_comprehension_over_them_is_still_the_payload"] = _fixture(
        "print(f'chain: {len(out)-len(bad)}/{len(out)} rc0')", "out")
    arms["a_literal_denominator_is_a_literal"] = _fixture(
        "print(f'chain: {ok}/{312} rc0')", "out")
    arms["a_separate_counter_is_not_the_written_object"] = _fixture(
        "print(f'chain: {ok}/{total} rc0')", "out")
    arms["the_length_of_another_list_is_not_the_written_object"] = _fixture(
        "print(f'chain: {len(bad)}/{len(out)} rc0')", "out")
    arms["a_comprehension_over_something_else_is_not_the_written_rows"] = _fixture(
        "other = [1, 2]\nprint(f'chain: {len(out)-len(other)}/{len(out)} rc0')", "out")
    return arms


def _check_arms():
    got = control_arms()
    want = {
        "a_payload_field_is_read_from_the_payload": [READ_PAYLOAD, READ_PAYLOAD],
        "an_f_string_payload_field_is_read_from_the_payload": [READ_PAYLOAD, READ_PAYLOAD],
        "the_length_of_the_dumped_list_is_the_written_rows": [LENGTH_WRITTEN, LENGTH_WRITTEN],
        "the_length_of_the_dumped_envelopes_rows_is_the_written_rows": [LENGTH_WRITTEN,
                                                                        LENGTH_WRITTEN],
        "the_written_rows_minus_a_comprehension_over_them_is_still_the_payload": [
            DIFF_MINUS_NONZERO, LENGTH_WRITTEN],
        "a_literal_denominator_is_a_literal": [NOT_FROM_OBJECT, LITERAL],
        "a_separate_counter_is_not_the_written_object": [NOT_FROM_OBJECT, NOT_FROM_OBJECT],
        "the_length_of_another_list_is_not_the_written_object": [NOT_FROM_OBJECT, LENGTH_WRITTEN],
        "a_comprehension_over_something_else_is_not_the_written_rows": [
            NOT_FROM_OBJECT, LENGTH_WRITTEN],
    }
    return ["%s -> %r (want %r)" % (k, got.get(k), v) for k, v in want.items()
            if got.get(k) != v]


def doctored_arm():
    """Copy the bm-b runner with its denominator replaced by a literal number.

    A classifier that cannot see this edit is not reading the source.  The edit is applied to a
    string copy; the file on disk is never touched.
    """
    rel = "Tools/s6_chain_bmb.py"
    with io.open(os.path.join(ROOT, rel), encoding="utf-8", errors="replace") as fh:
        text = fh.read()
    needle = 'payload["legs_total"]'
    if needle not in text:
        return {"applied": False,
                "why": "the denominator expression this study traced is no longer in the source"}
    doc = text.replace(needle, "312", 1)
    rows, _p = trace_source(doc, "b")
    live, _p2 = trace_source(text, "b")
    return {"applied": True,
            "denominator_kind_live": [r["origin_kind"] for r in live],
            "denominator_kind_doctored": [r["origin_kind"] for r in rows],
            "detected": [r["origin_kind"] for r in rows] != [r["origin_kind"] for r in live]}


# ---- face validation ------------------------------------------------------------
def face_problems(face):
    problems = []
    rows = face.get("rows") or []
    s = face.get("summary") or {}
    sources = face.get("sources") or []
    if s.get("printed_numbers") != len(rows):
        problems.append("summary.printed_numbers %r != %d rows" % (s.get("printed_numbers"),
                                                                   len(rows)))
    for cls in ORIGIN_CLASSES:
        got = sum(1 for r in rows if r.get("origin_kind") == cls)
        if s.get(cls) != got:
            problems.append("summary.%s %r != %d in rows" % (cls, s.get(cls), got))
    if sum(s.get(c, 0) for c in ORIGIN_CLASSES) != len(rows):
        problems.append("a printed number is in no class or in two")
    if s.get("printed_numbers_read_from_the_written_object") != sum(
            s.get(k, 0) for k in FROM_PAYLOAD):
        problems.append("summary.printed_numbers_read_from_the_written_object does not re-derive")
    if s.get("runners") != len(sources):
        problems.append("summary.runners %r != %d sources" % (s.get("runners"), len(sources)))
    if s.get("sentences") != len({(r.get("runner"), r.get("line")) for r in rows}):
        problems.append("summary.sentences does not re-derive")
    if s.get("runners_printing_a_chain_count") != len({r.get("runner") for r in rows}):
        problems.append("summary.runners_printing_a_chain_count does not re-derive")
    if s.get("runners_whose_receipt_carries_a_count_field") != sum(
            1 for x in sources if x.get("writes_count_fields")):
        problems.append("summary.runners_whose_receipt_carries_a_count_field does not re-derive")
    receipts = face.get("receipt_arm") or {}
    if receipts:
        if s.get("receipts_carrying_legs_total") != sum(
                v.get("carrying_legs_total", 0) for v in receipts.values()):
            problems.append("summary.receipts_carrying_legs_total does not re-derive")
        if s.get("receipts_carrying_legs_rc0") != sum(
                v.get("carrying_legs_rc0", 0) for v in receipts.values()):
            problems.append("summary.receipts_carrying_legs_rc0 does not re-derive")
        if s.get("receipts_with_no_count_field") != sum(
                v.get("bare_lists", 0) + v.get("envelopes_without_a_count", 0)
                + v.get("envelopes_with_rows_and_no_count", 0)
                for v in receipts.values()):
            problems.append("summary.receipts_with_no_count_field does not re-derive")
        if s.get("receipts_whose_total_disagrees_with_their_rows") != sum(
                v.get("legs_total_differs_from_the_recount", 0) for v in receipts.values()):
            problems.append("summary.receipts_whose_total_disagrees_with_their_rows does not "
                            "re-derive")
        if s.get("receipts_whose_rc0_disagrees_with_their_rows") != sum(
                v.get("legs_rc0_differs_from_the_recount", 0) for v in receipts.values()):
            problems.append("summary.receipts_whose_rc0_disagrees_with_their_rows does not "
                            "re-derive")
        for name, v in receipts.items():
            if v.get("carrying_legs_total") is not None:
                if v.get("legs_total_agrees_with_the_recount", 0) + \
                        v.get("legs_total_differs_from_the_recount", 0) != \
                        v.get("carrying_legs_total"):
                    problems.append("%s: the receipt arm does not add up" % name)
            if v.get("carrying_legs_rc0", 0) > v.get("carrying_legs_total", 0):
                problems.append("%s: more files carry an rc0 than carry a total" % name)
    for r in rows:
        for key in ("runner", "line", "expression", "expr_kind", "reads", "origin_kind",
                    "dump_target"):
            if key not in r:
                problems.append("a row is missing %s" % key)
        want = derive_kind(r.get("expr_kind"), r.get("reads") or "", r.get("bindings") or {},
                           r.get("dump_target"))
        if r.get("origin_kind") != want:
            problems.append("%s:%r: origin %r != re-derived %r"
                            % (r.get("runner"), r.get("line"), r.get("origin_kind"), want))
        if r.get("origin_kind") == LITERAL and r.get("expr_kind") != "constant_int":
            problems.append("%s:%r: a literal with a non-literal expression"
                            % (r.get("runner"), r.get("line")))
    exp_verdict = _verdict(s, sources)
    if face.get("verdict") != exp_verdict:
        problems.append("verdict %r != re-derived %r" % (face.get("verdict"), exp_verdict))
    if face.get("control_arms") != control_arms():
        problems.append("control arms do not re-derive")
    pin = (face.get("population_source") or {}).get("sha16") or {}
    for _n, rel in RUNNERS:
        if not pin.get(rel):
            problems.append("the population is not pinned: %s" % rel)
    if (face.get("print_rule") or {}).get("chain_words") != PRINT_RULE["chain_words"]:
        problems.append("the echoed print rule is not the rule this module runs")
    if not face.get("verdict_line"):
        problems.append("the face carries no verdict_line")
    return problems


# ---- modes ----------------------------------------------------------------------
def selftest():
    bad = list(_check_arms())
    doc_arm = doctored_arm()
    if not doc_arm.get("applied"):
        bad.append("the doctored-copy arm could not be applied: %s" % doc_arm.get("why"))
    elif not doc_arm.get("detected"):
        bad.append("a doctored denominator was not detected")
    face = build(write=False)
    bad.extend(face_problems(face))
    s = face["summary"]
    if doc_arm.get("applied") and doc_arm.get("detected"):
        if LITERAL not in doc_arm.get("denominator_kind_doctored", []):
            bad.append("the doctored denominator was not classed a literal")
    d = json.loads(json.dumps(face))
    d["verdict"] = "a_verdict_this_study_never_publishes"
    if not face_problems(d):
        bad.append("a hand-written verdict was accepted")
    d = json.loads(json.dumps(face))
    if d["rows"]:
        d["rows"][0]["origin_kind"] = LITERAL if d["rows"][0]["origin_kind"] != LITERAL \
            else READ_PAYLOAD
        if not face_problems(d):
            bad.append("a relabelled origin was accepted")
    d = json.loads(json.dumps(face))
    d["summary"]["printed_numbers"] = d["summary"]["printed_numbers"] + 1
    if not face_problems(d):
        bad.append("an inflated printed-number count was accepted")
    d = json.loads(json.dumps(face))
    d["population_source"]["sha16"]["Tools/s6_chain_bma.py"] = ""
    if not face_problems(d):
        bad.append("an unpinned runner was accepted")
    if bad:
        print("SELFTEST FAIL %d problems" % len(bad))
        for x in bad[:10]:
            print("  -", x[:220])
        return 1
    print("SELFTEST PASS: %d control arms + %d printed numbers (from_payload=%d literal=%d "
          "outside=%d) + doctored copy detected"
          % (len(control_arms()), s["printed_numbers"],
             s["printed_numbers_read_from_the_written_object"], s[LITERAL], s[NOT_FROM_OBJECT]))
    return 0


def _key(r):
    return (r.get("runner") or "", r.get("line") or 0, r.get("placeholder_index") or 0,
            r.get("origin_kind") or "")


def check():
    fresh = build(write=False)
    try:
        with io.open(LATEST, encoding="utf-8") as fh:
            published = json.load(fh)
    except Exception as exc:
        print("CHECK FAIL: the face cannot be read: %s" % exc)
        return 1
    problems = face_problems(published)

    def _norm_sources(face):
        # the sha16 pin and the line count are the vintage, not the finding: an edit anywhere in a
        # runner moves them.  What must not move unrecorded is the traced population.
        return [{k: v for k, v in x.items() if k not in ("sha16", "lines")}
                for x in (face.get("sources") or [])]

    # The receipt corpus is live: every chain run, including this one, appends a file.  Those
    # counters may only grow, so they are compared as growth rather than as identity.
    live_keys = ("receipts_on_disk", "receipts_carrying_legs_total",
                 "receipts_carrying_legs_rc0", "receipts_with_no_count_field")
    for key in ("verdict", "card", "print_rule", "control_arms"):
        if fresh.get(key) != published.get(key):
            problems.append("live %s disagrees with the published face" % key)
    fs, ps = fresh.get("summary") or {}, published.get("summary") or {}
    for key in sorted(set(fs) | set(ps)):
        if key in live_keys:
            if (fs.get(key) or 0) < (ps.get(key) or 0):
                problems.append("summary.%s fell from %r to %r" % (key, ps.get(key), fs.get(key)))
        elif key in ("receipts_whose_total_disagrees_with_their_rows",
                     "receipts_whose_rc0_disagrees_with_their_rows"):
            if fs.get(key) != ps.get(key):
                problems.append("summary.%s moved: %r -> %r (a new disagreement is a finding, "
                                "not drift)" % (key, ps.get(key), fs.get(key)))
        elif fs.get(key) != ps.get(key):
            problems.append("live summary.%s %r != published %r" % (key, fs.get(key), ps.get(key)))
    if _norm_sources(fresh) != _norm_sources(published):
        problems.append("the traced population moved (rebuild the face if the runner did)")
    fresh_keys = sorted(_key(r) for r in fresh.get("rows") or [])
    pub_keys = sorted(_key(r) for r in published.get("rows") or [])
    if fresh_keys != pub_keys:
        problems.append("the traced-number multiset moved (live-only=%r published-only=%r)"
                        % ([k for k in fresh_keys if k not in pub_keys][:3],
                           [k for k in pub_keys if k not in fresh_keys][:3]))
    if problems:
        print("CHECK FAIL: %d problems; first=%s" % (len(problems), str(problems[0])[:300]))
        return 1
    print("CHECK PASS: %d printed numbers re-derive over %d runners, verdict=%s"
          % (len(pub_keys), len(published.get("sources") or []), published.get("verdict")))
    return 0


def verify():
    problems = face_problems(build(write=False))
    print(json.dumps({"problems": problems[:10], "n": len(problems)}, ensure_ascii=False))
    return 0 if not problems else 1


def main(argv=None):
    action = (list(sys.argv[1:] if argv is None else argv) or ["build"])[0]
    if action == "build":
        face = build(write=True)
        s = face["summary"]
        print("BUILT %s: %d printed numbers over %d runners | payload=%d literal=%d outside=%d"
              % (os.path.relpath(LATEST, ROOT), s["printed_numbers"], s["runners"],
                 s["printed_numbers_read_from_the_written_object"], s[LITERAL],
                 s[NOT_FROM_OBJECT]))
        print("RECEIPTS: %d on disk, %d carry legs_total, %d carry legs_rc0, %d carry no count, "
              "%d disagree with their own rows, %d unparsed"
              % (s["receipts_on_disk"], s["receipts_carrying_legs_total"],
                 s["receipts_carrying_legs_rc0"], s["receipts_with_no_count_field"],
                 s["receipts_whose_total_disagrees_with_their_rows"]
                 + s["receipts_whose_rc0_disagrees_with_their_rows"],
                 s["receipts_unparsed"]))
        print("VERDICT: %s" % face["verdict"])
        print("LINE: %s" % face["verdict_line"])
        return 0
    if action == "check":
        return check()
    if action == "verify":
        return verify()
    if action == "selftest":
        return selftest()
    if action == "doctor":
        print(json.dumps(doctored_arm(), ensure_ascii=False, indent=1))
        return 0
    print("usage: e570_chain_print_source.py build|check|verify|selftest|doctor")
    return 2


if __name__ == "__main__":
    sys.exit(main())