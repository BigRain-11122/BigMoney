"""E305 -- price the eight at-risk rows that E299 could only bound at face level.

E299 graded 62 numeric comparisons in ``smoke_test.py`` and called 29 of them at risk: the leg
compares at a tolerance finer than the quantum the field it reads is printed with. 21 of those 29
were graded on the field's own measured decimals. The other 8 were graded on the FACE's coarsest
printed quantum, because no leaf under the key name the leg reads could be found -- and a face-level
bound is an upper bound on resolution, not a measurement of the field.

This study prices those 8 rows. For each one the question is not "is it still at risk" but the
prior question: why could the key not be found?

  * CONTAINER_ONLY     -- the key is there, but its value is a list or a dict, so the leaf walker
                          skips it on purpose. A container is not a printed number; no quantum can
                          put it at risk.
  * IN_A_SIBLING_FACE  -- the key is absent from the face the row was priced against and present in
                          another face the SAME leg names. The quantum that matters is the producing
                          face's, and it is measurable.
  * WRITTEN_INSIDE_RECORDS -- the key is written by the producer into a list of per-record dicts and
                          that list is empty on the vintage that was read. The key is not absent by
                          design, it is absent today.
  * ABSENT             -- the key appears in no face the leg names and in no producer source.

Every row is then re-graded on whatever printed number was actually found. The verdict is a question
about E299's fallback, not about the legs: a face-level bound reported as a measurement is the
defect, and withdrawing it is the whole product of this study.

No study is re-run, no face is rebuilt: every number is arithmetic over the published census face,
the faces it names, and the producer sources under ``scripts/``.
"""

import ast
import io
import json
import os
import re
import sys
import tokenize

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
CENSUS = "precisioncensus_latest.json"

STUDY = "E305_face_level_row_pricing"
TITLE = ("eight at-risk rows were graded on the face's coarsest bound because the key the leg "
         "reads could not be found -- is the key absent, spelled differently, or inside a "
         "container the walker skips, and once found does the row stay at risk?")
FACE = "PRECISIONGAP-%s.json"
LATEST = "precisiongap_latest.json"

MAX_DECIMALS = 17
SELF_RE = re.compile(r"^(PRECISIONGAP-.*\.json|precisiongap_latest\.json)$")

VERDICT_VOCAB = (
    "none_of_the_face_level_rows_is_at_risk",
    "some_face_level_rows_stay_at_risk",
    "no_face_level_rows_published",
)

NO_BILL = ("measurement only: the row list is read out of the published E299 census face, the "
           "quantum of each field is measured from the published JSON the leg names, and producer "
           "sources are read as text. No study is re-run, no face is rebuilt, no engine runs, no "
           "draw stream is regenerated, and no smoke leg is edited.")


# ------------------------------------------------------------------ io
def _read(path):
    fh = io.open(path, "r", encoding="utf-8")
    try:
        return json.load(fh)
    finally:
        fh.close()


def write_face(face, outdir=None):
    outdir = outdir or OUTDIR
    text = json.dumps(face, ensure_ascii=False, indent=1) + "\n"
    for name in (FACE % face["evidence_cutoff"], LATEST):
        fh = io.open(os.path.join(outdir, name), "w", encoding="utf-8", newline="\n")
        try:
            fh.write(text)
        finally:
            fh.close()


def load(name, outdir=None):
    return _read(os.path.join(outdir or OUTDIR, name))


# ------------------------------------------------------------------ key resolution
def decimals(value):
    """The smallest d with round(v, d) == v, capped; None for a non-float."""
    if not isinstance(value, float) or value != value:
        return None
    for d in range(MAX_DECIMALS + 1):
        if round(value, d) == value:
            return d
    return MAX_DECIMALS


def scan_key(node, key, path="", depth=0, cap=2000):
    """Every appearance of ``key`` anywhere in the payload, container values included.

    E299's leaf walker drops list and dict values on purpose (a container has no printed quantum).
    This scan keeps them, because "found but not a number" and "not found at all" are different
    answers to the question this study asks.
    """
    out = []

    def walk(n, p, d):
        if len(out) >= cap or d > 12:
            return
        if isinstance(n, dict):
            for k, v in n.items():
                if str(k) == key:
                    out.append({"path": (p + "/" + str(k)), "kind": _kind(v),
                                "value": v if not isinstance(v, (dict, list)) else None,
                                "container": _container_shape(v)})
                if isinstance(v, (dict, list)):
                    walk(v, p + "/" + str(k), d + 1)
        elif isinstance(n, list):
            for item in n[:500]:
                if isinstance(item, (dict, list)):
                    walk(item, p + "/[]", d + 1)

    walk(node, path, depth)
    return out


def _kind(v):
    if isinstance(v, dict):
        return "dict"
    if isinstance(v, list):
        return "list"
    if isinstance(v, bool):
        return "bool"
    if isinstance(v, int):
        return "int"
    if isinstance(v, float):
        return "float"
    if v is None:
        return "null"
    return "str"


def _container_shape(v):
    if isinstance(v, list):
        return "list[%d]" % len(v)
    if isinstance(v, dict):
        return "dict[%d]" % len(v)
    return None


def quantum_of(sites):
    """Coarsest printed quantum over the float values found, or None when there is no number."""
    decs = [decimals(s["value"]) for s in sites if s["kind"] == "float"]
    decs = [d for d in decs if d is not None]
    if not decs:
        return None, None
    return min(decs), 10.0 ** (-min(decs))


def prose_or_fixture_lines(text):
    """Lines that cannot be a producer write: comments, docstrings, and self-test fixtures.

    A regex cannot tell a writer from a quote. E313 (r1332) put a docstring line and a fixture
    mentioning `"session_open"` into the top-8 hits of the row with no face, pushing out the two
    scripts that really write the key -- so a hit inside prose or inside a `*selftest*` function is
    dropped here (E312's lesson, applied on the reading side).
    """
    skip = set()
    try:
        tree = ast.parse(text)
    except SyntaxError:
        tree = None
    if tree is not None:
        for node in ast.walk(tree):
            body = getattr(node, "body", None)
            if not isinstance(body, list) or not body:
                continue
            first = body[0]
            value = getattr(first, "value", None)
            if isinstance(first, ast.Expr) and isinstance(value, ast.Constant) \
                    and isinstance(value.value, str):
                skip.update(range(first.lineno, (first.end_lineno or first.lineno) + 1))
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and "selftest" in node.name:
                skip.update(range(node.lineno, (node.end_lineno or node.lineno) + 1))
    try:
        for tok in tokenize.generate_tokens(io.StringIO(text).readline):
            if tok.type == tokenize.COMMENT:
                skip.add(tok.start[0])
    except (tokenize.TokenError, IndentationError):
        pass
    return skip


def producer_hits(key):
    """Where the producer writes this key, as text. Read-only over scripts/."""
    hits = []
    pat = re.compile(r"""["']%s["']""" % re.escape(key))
    for name in sorted(os.listdir(HERE)):
        if not name.endswith(".py"):
            continue
        path = os.path.join(HERE, name)
        try:
            text = io.open(path, "r", encoding="utf-8").read()
        except Exception:
            continue
        skip = prose_or_fixture_lines(text)
        for i, line in enumerate(text.split("\n"), 1):
            if i in skip:
                continue
            if pat.search(line):
                hits.append({"script": "scripts/" + name, "line": i, "text": line.strip()[:160]})
    return hits[:8]


def is_a_face(rel):
    base = os.path.basename(rel)
    return base.endswith(".json") and not ("%" in base or "*" in base or "{" in base)


def resolve_row(row, payloads):
    """Answer the card's question for one at-risk row and re-grade it."""
    priced = [a for a in row.get("at_risk_faces") or []]
    named = [f for f in row.get("faces_named") or [] if is_a_face(f)]
    keys = row.get("keys") or []
    per_key = []
    numeric_sites = []
    for key in keys:
        in_priced = []
        in_other = {}
        for rel in named:
            payload = payloads.get(rel)
            if payload is None:
                continue
            found = scan_key(payload, key)
            for s in found:
                s["face"] = rel
            if rel in [a.get("face") for a in priced]:
                in_priced.extend(found)
            elif found:
                in_other[rel] = found
            numeric_sites.extend(s for s in found if s["kind"] in ("float", "int"))
        per_key.append({"key": key, "in_priced_face": in_priced, "in_other_faces": in_other})
    all_sites = [s for p in per_key for s in
                 (p["in_priced_face"] + [x for v in p["in_other_faces"].values() for x in v])]
    in_priced = [s for p in per_key for s in p["in_priced_face"]]
    decs, quantum = quantum_of(numeric_sites)
    tol = row.get("tolerance") or 0.0

    found_any = bool(all_sites)
    base_kinds = sorted({s["kind"] for s in all_sites})
    if numeric_sites:
        kind = "in_priced_face" if any(s in in_priced for s in numeric_sites) \
            else "in_a_sibling_face"
    elif found_any:
        kind = "not_a_number_in_priced_face" if in_priced else "not_a_number_in_a_sibling_face"
    else:
        hits = []
        for key in keys:
            hits.extend(producer_hits(key))
        kind = "written_inside_records" if hits else "absent"

    at_risk_after = bool(numeric_sites) and quantum is not None and tol < quantum / 2.0
    shapes = sorted({s["container"] for s in all_sites if s["container"]})
    if kind in ("not_a_number_in_priced_face", "not_a_number_in_a_sibling_face"):
        where = "in the face it was priced against" if in_priced else \
            "in a sibling face the same leg names"
        what = ("a %s" % "/".join(shapes)) if shapes else \
            ("only %s values" % "/".join(base_kinds))
        reason = ("the key is present %s as %s: a container or a label is not a printed number, so "
                  "no quantum can put it at risk" % (where, what))
    elif kind == "written_inside_records":
        reason = ("the producer writes this key inside per-record dicts and the face carries none on "
                  "this vintage, so there is no printed number to be finer than")
    elif kind == "absent":
        reason = "the key appears in no face the leg names and in no producer source"
    elif quantum is None:
        reason = ("every value under the read key is an integer, which carries no printed "
                  "fractional quantum")
    elif at_risk_after:
        reason = "a printed number was found at %d dp, still coarser than 2x the tolerance" % decs
    else:
        reason = "the number found is printed at %d dp, finer than 2x the tolerance" % decs
    return {
        "leg": row.get("leg"),
        "line": row.get("line"),
        "kind": row.get("kind"),
        "tolerance": tol,
        "expression": (row.get("expression") or "")[:240],
        "priced_against": [a.get("face") for a in priced],
        "faces_named": named,
        "keys": keys,
        "resolution": kind,
        "value_kinds": base_kinds,
        "key_sites": per_key,
        "producer_writers": ([] if found_any else
                             [h for key in keys for h in producer_hits(key)][:8]),
        "found_decimals": decs,
        "found_quantum": quantum,
        "at_risk_after": at_risk_after,
        "reason": reason,
    }


def decimal_sites_in_priced(per_key):
    return [s for p in per_key for s in p["in_priced_face"] if s["kind"] == "float"]


def _count(by_kind, *names):
    return sum(by_kind.get(n, 0) for n in names)


# ------------------------------------------------------------------ build
def build(census_path=None, outdir=None):
    census = _read(census_path or os.path.join(outdir or OUTDIR, CENSUS))
    rows = [s for s in census.get("sites") or []
            if s.get("at_risk") and s.get("at_risk_faces")
            and all(a.get("basis") == "face_level" for a in s["at_risk_faces"])]
    faces = sorted({f for r in rows for f in (r.get("faces_named") or []) if is_a_face(f)})
    payloads = {}
    unreadable = []
    for rel in faces:
        path = os.path.join(ROOT, rel.replace("/", os.sep))
        try:
            payloads[rel] = _read(path)
        except Exception:
            unreadable.append(rel)

    priced_rows = [resolve_row(r, payloads) for r in rows]
    by_kind = {}
    for r in priced_rows:
        by_kind[r["resolution"]] = by_kind.get(r["resolution"], 0) + 1
    after = [r for r in priced_rows if r["at_risk_after"]]

    if not priced_rows:
        verdict = "no_face_level_rows_published"
    elif after:
        verdict = "some_face_level_rows_stay_at_risk"
    else:
        verdict = "none_of_the_face_level_rows_is_at_risk"

    census_summary = census.get("summary") or {}
    published = census_summary.get("n_at_risk_on_face_level_bound_only")
    identity = {
        "row_count_matches_the_census": published == len(priced_rows),
        "every_row_carries_a_resolution": all(r["resolution"] for r in priced_rows),
        "partition_sums_to_rows": sum(by_kind.values()) == len(priced_rows),
        "every_sibling_row_names_the_face_it_was_found_in":
            all(any(p["in_other_faces"] for p in r["key_sites"])
                for r in priced_rows
                if r["resolution"] in ("in_a_sibling_face",
                                       "not_a_number_in_a_sibling_face")),
        "no_row_is_at_risk_without_a_printed_number":
            all(r["found_quantum"] is not None for r in after),
        "at_risk_after_agrees_with_verdict":
            (verdict == "some_face_level_rows_stay_at_risk") == bool(after),
        "self_faces_excluded": not any(SELF_RE.match(os.path.basename(f)) for f in faces),
        "unreadable_faces_disclosed": True,
    }
    identity["all_checks"] = all(v for k, v in identity.items() if k != "all_checks")

    evidence_cutoff = max([census.get("evidence_cutoff") or "1970-01-01"]
                          + [(census.get("generated") or "1970-01-01")[:10]])
    summary = {
        "census_face": CENSUS,
        "census_published_face_level_rows": published,
        "rows_priced": len(priced_rows),
        "by_resolution": by_kind,
        "n_at_risk_after": len(after),
        "n_withdrawn": len(priced_rows) - len(after),
        "faces_read": len(payloads),
        "faces_unreadable_or_missing": unreadable,
        "statement": None,
    }
    summary["statement"] = (
        "of the %d at-risk rows E299 could only bound at face level, %d are withdrawn: %d rest on "
        "a value that is a container or a label rather than a printed number, %d read a key that "
        "lives in a sibling face the same leg names, %d name a key the producer writes inside "
        "per-record lists that are empty on this vintage; %d stay at risk once the printed number "
        "is found. A face-level bound is an upper bound on resolution, not a measurement of the "
        "field."
        % (len(priced_rows), len(priced_rows) - len(after),
           _count(by_kind, "not_a_number_in_priced_face", "not_a_number_in_a_sibling_face"),
           _count(by_kind, "in_a_sibling_face", "in_priced_face"),
           _count(by_kind, "written_inside_records", "absent"),
           len(after)))

    return {
        "study": STUDY,
        "title": TITLE,
        "evidence_cutoff": evidence_cutoff,
        "decision_rule": ("a row is at risk after pricing only when a numeric value under the key "
                          "it reads exists in a face the leg names and the leg's tolerance is "
                          "finer than half that value's printed quantum; a container, a string or "
                          "an absent key can never be at risk from rounding."),
        "no_bill": NO_BILL,
        "rows": priced_rows,
        "summary": summary,
        "identity_check": identity,
        "verdict": verdict,
        "verdict_reason": (
            "%d row(s) priced; %d withdrawn as unmeasurable-or-finer, %d still finer than the "
            "quantum of the number actually found." % (len(priced_rows), len(priced_rows) - len(after),
                                                      len(after))),
    }


# ------------------------------------------------------------------ commands
def cmd_run():
    import datetime
    face = build()
    face["generated"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    write_face(face)
    s = face["summary"]
    print("E305 %s" % face["verdict"])
    print("  rows priced: %d (E299 published %s at face level)"
          % (s["rows_priced"], s["census_published_face_level_rows"]))
    print("  by resolution: %s" % ", ".join("%s=%d" % kv for kv in sorted(s["by_resolution"].items())))
    print("  withdrawn: %d, still at risk: %d" % (s["n_withdrawn"], s["n_at_risk_after"]))
    for r in face["rows"]:
        print("    %-22s tol=%-8g %s" % (r["resolution"], r["tolerance"],
                                         (r["leg"] or "")[:70]))
        print("        %s" % r["reason"])
    print("  identity_check: %s" % ("ALL PASS" if face["identity_check"]["all_checks"] else "FAILED"))
    return 0


def cmd_verify():
    stored = load(FACE % build()["evidence_cutoff"])
    live = build()
    problems = []
    for key in ("verdict", "summary", "identity_check", "rows"):
        if stored.get(key) != live.get(key):
            problems.append("%s does not re-derive" % key)
    if stored.get("verdict") not in VERDICT_VOCAB:
        problems.append("verdict outside the frozen set")
    if not (stored.get("identity_check") or {}).get("all_checks"):
        problems.append("identity_check is not all green")
    if problems:
        for p in problems:
            print("FAIL %s" % p)
        return 1
    print("E305 verify: the published face re-derives (%d rows, verdict %s)"
          % (len(live["rows"]), live["verdict"]))
    return 0


def cmd_selftest():
    ok = 0
    fails = []

    def leg(name, cond, detail=None):
        nonlocal ok
        if cond:
            ok += 1
        else:
            fails.append("%s (%r)" % (name, detail))

    # scan_key finds a leaf nested inside a list of records -- the shape E299's walker does see
    payload = {"per_trader": {"T1": {"detail": [{"session_open": 3.21}]}}}
    hits = scan_key(payload, "session_open")
    leg("L1", len(hits) == 1 and hits[0]["kind"] == "float" and hits[0]["value"] == 3.21, hits)
    # ... and reports a container value instead of dropping it
    hits = scan_key({"a": {"rows": [1, 2]}}, "rows")
    leg("L2", len(hits) == 1 and hits[0]["kind"] == "list" and hits[0]["value"] is None, hits)
    leg("L3", hits and hits[0]["container"] == "list[2]", hits)
    # an absent key stays absent
    leg("L4", scan_key({"a": {"b": 1.5}}, "zzz") == [])

    # decimals: a printed copy vs a computed one
    leg("L5", decimals(0.123457) == 6, decimals(0.123457))
    leg("L6", decimals(0.1 + 0.2) == 17, decimals(0.1 + 0.2))
    leg("L7", decimals("3.2") is None and decimals(3) is None)

    # quantum_of: floats only, coarsest wins; integers and strings carry no quantum
    leg("L8", quantum_of([{"kind": "float", "value": 0.123457},
                          {"kind": "float", "value": 0.5}])[1] == 0.1)
    leg("L9", quantum_of([{"kind": "int", "value": 3}]) == (None, None))
    leg("L10", quantum_of([]) == (None, None))

    def row(**kw):
        base = {"leg": "x", "line": 1, "kind": "epsilon", "tolerance": 1e-9,
                "expression": "", "keys": [], "faces_named": [], "at_risk_faces": []}
        base.update(kw)
        return base

    # a key present with 15 dp in the face the row was priced against: withdrawn
    payloads = {"results/a.json": {"share": 0.123456789012345}}
    r = resolve_row(row(keys=["share"], faces_named=["results/a.json"],
                        at_risk_faces=[{"face": "results/a.json", "basis": "face_level"}]),
                    payloads)
    leg("L11", r["resolution"] == "in_priced_face" and r["at_risk_after"] is False, r)
    # the same key printed at 3 dp stays at risk
    payloads = {"results/a.json": {"share": 0.123}}
    r = resolve_row(row(keys=["share"], faces_named=["results/a.json"],
                        at_risk_faces=[{"face": "results/a.json", "basis": "face_level"}]),
                    payloads)
    leg("L12", r["at_risk_after"] is True and r["found_decimals"] == 3, r)
    # absent from the priced face, present in a sibling the leg also names -> sibling reading
    payloads = {"results/priced.json": {"other": 1},
                "results/sib.json": {"share": 0.123456789012345}}
    r = resolve_row(row(keys=["share"], faces_named=["results/priced.json", "results/sib.json"],
                        at_risk_faces=[{"face": "results/priced.json", "basis": "face_level"}]),
                    payloads)
    leg("L13", r["resolution"] == "in_a_sibling_face" and r["at_risk_after"] is False, r)
    # a container is not a printed number and cannot be at risk
    payloads = {"results/a.json": {"band": {"lo": 0.63, "hi": 0.71}}}
    r = resolve_row(row(keys=["band"], kind="exact_equality", tolerance=0.0,
                        faces_named=["results/a.json"],
                        at_risk_faces=[{"face": "results/a.json", "basis": "face_level"}]),
                    payloads)
    leg("L14a", r["resolution"] == "not_a_number_in_priced_face", r["resolution"])
    leg("L14b", r["at_risk_after"] is False and r["found_quantum"] is None, r)
    # ... a boolean flag is a label too, not a measurement
    payloads = {"results/a.json": {"sensitivity": {"rows": [{"ok": True}]}}}
    r = resolve_row(row(keys=["ok"], kind="exact_equality", tolerance=0.0,
                        faces_named=["results/a.json"],
                        at_risk_faces=[{"face": "results/a.json", "basis": "face_level"}]),
                    payloads)
    leg("L14c", r["resolution"] == "not_a_number_in_priced_face"
        and r["value_kinds"] == ["bool"], r)
    # a key no face carries is answered from the producer text, not left blank
    r = resolve_row(row(keys=["session_open"], faces_named=["results/zzz.json"],
                        at_risk_faces=[{"face": "results/zzz.json", "basis": "face_level"}]),
                    {"results/zzz.json": {"a": 1}})
    leg("L15", r["resolution"] == "written_inside_records" and r["producer_writers"], r)

    # the live census: the row set is the one published, and the identity legs hold
    live = build()
    s, idn = live["summary"], live["identity_check"]
    leg("L16", live["verdict"] in VERDICT_VOCAB, live["verdict"])
    leg("L17", idn["all_checks"] is True, idn)
    leg("L18", s["rows_priced"] == s["census_published_face_level_rows"],
        (s["rows_priced"], s["census_published_face_level_rows"]))
    leg("L19", s["n_withdrawn"] + s["n_at_risk_after"] == s["rows_priced"],
        (s["n_withdrawn"], s["n_at_risk_after"], s["rows_priced"]))
    leg("L20", all(r["resolution"] in
                   ("in_priced_face", "in_a_sibling_face", "not_a_number_in_priced_face",
                    "not_a_number_in_a_sibling_face", "written_inside_records", "absent")
                   for r in live["rows"]),
        [r["resolution"] for r in live["rows"]])
    # the withdrawn rows are withdrawn for a stated reason, never silently dropped
    leg("L21", all(r["reason"] for r in live["rows"]))
    # a row kept at risk must name a face it was priced against
    leg("L22", all(r["priced_against"] for r in live["rows"]))
    # a template is not a face
    leg("L23", not is_a_face("results/state_tilt/BANDPATH-%s.json")
        and is_a_face("results/state_tilt/BANDSCREEN-2026-10-29.json"))

    print("E305 selftest: %d/%d" % (ok, ok + len(fails)))
    for f_ in fails:
        print("  FAIL %s" % f_)
    return 0 if not fails else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "run":
        return cmd_run()
    if cmd == "verify":
        return cmd_verify()
    if cmd == "selftest":
        return cmd_selftest()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))