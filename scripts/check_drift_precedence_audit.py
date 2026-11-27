"""Which probes test the numbers before they test the bytes?

Why this exists
---------------
The chain pays a writer only when a probe's text says STALE (r1850). A probe that
recomputes a face, compares it to the receipt value-by-value, and returns "CHECK
FAILED" *before* it ever asks whether the source bytes moved will therefore never pay
a writer: on any source restatement the receipt disagrees, the probe prints a defect,
and the face keeps yesterday's numbers while looking like a code problem (r1934,
r1935).

The order inside the probe is the mechanism:
  bytes first  -> source moved  => STALE (writer paid, face republished)
                  source still  => value mismatch is a real defect
  values first -> source moved  => CHECK FAILED (writer never paid, face frozen)

This audit reads probe sources, finds the branch that exits non-zero printing STALE
(the drift exit) and the branch that exits non-zero printing CHECK FAILED (the defect
exit), and records which runs first. It judges probes, not strategies, and never
rewrites one.

Verdicts per scope:
  BYTES_FIRST     drift exit precedes defect exit -- the r1934 contract holds
  VALUES_FIRST    defect exit precedes drift exit -- restatement reads as a defect
  NO_STALE_PATH   a check-like scope with a defect exit and no drift exit at all

Branches are identified by the word they print, not by what their condition is called:
a parser that happens to say "rows moved" is not a probe. Non-check scopes are skipped.

Measured 2026-11-27 on this tree: 204 probe scopes in 181 modules, 6 VALUES_FIRST,
21 with no STALE path, rest clean. One of the six (etf_book_year_concentration_money)
was fixed the same round and pinned by this selftest.

Outputs results/check_drift_precedence_audit.json (zero network, idempotent).

Usage:
  python scripts/check_drift_precedence_audit.py run
  python scripts/check_drift_precedence_audit.py check
  python scripts/check_drift_precedence_audit.py selftest
"""
import argparse
import ast
import glob
import hashlib
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "check_drift_precedence_audit.json")

SCAN_GLOBS = ("scripts/*.py", "Tools/*.py")
SELF = "check_drift_precedence_audit.py"


def sha16(path):
    h = hashlib.sha256()
    with io.open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def _test_text(node, src):
    try:
        return (ast.get_source_segment(src, node) or "").strip().lower()
    except Exception:
        return ""


def _returns_nonzero(body):
    for n in ast.walk(ast.Module(body=body, type_ignores=[])):
        if isinstance(n, ast.Return) and isinstance(n.value, ast.Constant):
            v = n.value.value
            if isinstance(v, int) and not isinstance(v, bool) and v != 0:
                return True
        if isinstance(n, ast.Raise):
            return True
    return False


def _has_word(body, src, word):
    for n in ast.walk(ast.Module(body=body, type_ignores=[])):
        if isinstance(n, ast.Constant) and isinstance(n.value, str) and word in n.value:
            return True
    return False


def _walk_stmts(body):
    """Yield every statement in a scope, descending into loops/with/try/if-else.

    Exits hide one level down: cash_shelf_total_return_audit prints STALE from inside
    `for ... in face["panels"].items()`, and reading only the top level then reported
    the probe as having no STALE path at all. Nested defs are not entered.
    """
    for n in body:
        yield n
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        for field in ("body", "orelse", "finalbody"):
            sub = getattr(n, field, None)
            if isinstance(sub, list):
                for s in _walk_stmts(sub):
                    yield s
        if isinstance(n, ast.Try):
            for h in n.handlers:
                for s in _walk_stmts(h.body):
                    yield s


def _exit_units(body, src):
    """Yield (lineno, body) for every non-zero exit branch in a scope."""
    for n in _walk_stmts(body):
        chunk = None
        if isinstance(n, ast.If) and _returns_nonzero(n.body):
            chunk = n.body
        elif isinstance(n, ast.ExceptHandler) and _returns_nonzero(n.body):
            chunk = n.body
        if chunk is not None:
            yield n.lineno, chunk


def _first_word(chunk, src, word):
    for n in ast.walk(ast.Module(body=chunk, type_ignores=[])):
        if isinstance(n, ast.Constant) and isinstance(n.value, str) and word in n.value:
            return n.value.strip().replace("\n", " ")[:70]
    return word


def classify_scope(body, src):
    """Return the drift exits and defect exits of one probe scope.

    A "face missing" exit is neither: the chain repairs it on its own wording
    (Tools/s6_chain_bmc.py run_leg pays on "face missing" as well as "stale", r1581),
    so counting it as a defect exit would report a healthy probe as inverted.
    """
    drift, value = [], []
    repairable_words = ("face missing", "not found", "missing at", "no face",
                        "cannot read", "unreadable", "cannot parse")
    for lineno, chunk in _exit_units(body, src):
        says_stale = _has_word(chunk, src, "STALE")
        says_failed = _has_word(chunk, src, "CHECK FAILED")
        says_repairable = any(_has_word(chunk, src, w) for w in repairable_words)
        if says_stale and not says_failed:
            drift.append((lineno, _first_word(chunk, src, "STALE")))
        elif says_failed and not says_stale and not says_repairable:
            value.append((lineno, _first_word(chunk, src, "CHECK FAILED")))
    return drift, value


def _check_like(scope):
    s = scope.lower()
    return any(t in s for t in ("check", "probe", "guard", "gate"))


def audit_source(src):
    """Classify every probe scope in one module's source text."""
    try:
        tree = ast.parse(src)
    except SyntaxError as exc:
        return [{"scope": "module", "verdict": "UNPARSEABLE", "why": str(exc)[:120]}]

    scopes = [("module", tree.body)]
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            scopes.append((node.name, node.body))

    rows = []
    for scope, body in scopes:
        drift, value = classify_scope(body, src)
        if drift and value:
            first_drift = min(d[0] for d in drift)
            first_value = min(v[0] for v in value)
            rows.append({
                "scope": scope,
                "verdict": "BYTES_FIRST" if first_drift < first_value else "VALUES_FIRST",
                "drift_line": first_drift, "value_line": first_value,
                "drift_test": min(drift)[1], "value_test": min(value)[1]})
        elif drift:
            rows.append({"scope": scope, "verdict": "BYTES_FIRST",
                         "drift_line": drift[0][0], "drift_test": drift[0][1]})
        elif value and _check_like(scope):
            rows.append({"scope": scope, "verdict": "NO_STALE_PATH",
                         "value_line": value[0][0], "value_test": value[0][1]})
    return rows


def scan():
    hazards = {"VALUES_FIRST": [], "NO_STALE_PATH": [], "UNPARSEABLE": []}
    clean, scanned = [], []
    for pattern in SCAN_GLOBS:
        for path in sorted(glob.glob(os.path.join(ROOT, pattern))):
            rel = os.path.relpath(path, ROOT).replace("\\", "/")
            if os.path.basename(path) == SELF:
                continue
            src = io.open(path, encoding="utf-8", errors="replace").read()
            if "STALE" not in src:
                continue
            rows = audit_source(src)
            if not rows:
                continue
            scanned.append({"path": rel, "sha16": sha16(path), "rows": rows})
            for row in rows:
                v = row["verdict"]
                if v in hazards:
                    hazards[v].append({
                        "path": rel, "scope": row["scope"],
                        "line": row.get("drift_line") or row.get("value_line"),
                        "test": (row.get("value_test") or row.get("drift_test") or "")[:90]})
                else:
                    clean.append({"path": rel, "scope": row["scope"]})
    return scanned, hazards, clean


def build():
    scanned, hazards, clean = scan()
    return {
        "face": "check_drift_precedence_audit",
        "contract": "a probe must ask whether the bytes moved before it compares values (r1934)",
        "scanned_modules": len(scanned),
        "scanned_scopes": sum(len(s["rows"]) for s in scanned),
        "clean_scopes": len(clean),
        "verdict_counts": {k: len(v) for k, v in hazards.items()},
        "values_first": hazards["VALUES_FIRST"],
        "no_stale_path": hazards["NO_STALE_PATH"],
        "unparseable": hazards["UNPARSEABLE"],
        "modules": scanned,
    }


def cmd_run(args):
    face = build()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(face, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("scanned {} probes in {} modules: {} clean, {} VALUES_FIRST, {} NO_STALE_PATH".format(
        face["scanned_scopes"], face["scanned_modules"], face["clean_scopes"],
        face["verdict_counts"]["VALUES_FIRST"], face["verdict_counts"]["NO_STALE_PATH"]))
    for row in face["values_first"]:
        print("  VALUES_FIRST {path}:{scope} drift@{line} <- {test}".format(**row))
    print("wrote", os.path.relpath(OUT, ROOT))
    return 0


def cmd_check(args):
    if not os.path.exists(OUT):
        print("STALE: audit face missing:", OUT)
        return 3
    with io.open(OUT, encoding="utf-8") as f:
        had = json.load(f)
    now = build()
    moved = []
    before = {m["path"]: m["sha16"] for m in had.get("modules") or []}
    after = {m["path"]: m["sha16"] for m in now["modules"]}
    for path, digest in after.items():
        if path not in before:
            moved.append("new probe module: " + path)
        elif before[path] != digest:
            moved.append("probe bytes moved: {p} {a} -> {b}".format(
                p=path, a=before[path], b=digest))
    for path in before:
        if path not in after:
            moved.append("probe module gone: " + path)
    if moved:
        print("STALE: {} probe module(s) moved since this face was written; rescan to "
              "republish ({} hazards held back)".format(
                  len(moved), len(had.get("values_first") or []) + len(had.get("no_stale_path") or [])))
        for m in moved[:5]:
            print("  -", m)
        return 3
    problems = []
    for key in ("values_first", "no_stale_path"):
        if (had.get(key) or []) != (now.get(key) or []):
            problems.append("{k}: receipt {a} rows vs recomputed {b}".format(
                k=key, a=len(had.get(key) or []), b=len(now.get(key) or [])))
    if problems:
        print("CHECK FAILED ({} problems)".format(len(problems)))
        for p in problems:
            print(" -", p)
        return 3
    print("CHECK OK: {} probes scanned, {} VALUES_FIRST hazards".format(
        now["scanned_scopes"], len(now["values_first"])))
    return 0


# --------------------------------------------------------------------------- #
# selftest
# --------------------------------------------------------------------------- #
_SRC_BYTES_FIRST = '''
import json
def cmd_check(args):
    now = build()
    if had["sha"] != now["sha"]:
        moved.append("source moved")
    problems = []
    if had["value"] != now["value"]:
        problems.append("value")
    if moved:
        print("STALE face behind its source")
        return 3
    if problems:
        print("CHECK FAILED")
        return 3
    return 0
'''

_SRC_VALUES_FIRST = '''
import json
def cmd_check(args):
    now = build()
    if had["sha"] != now["sha"]:
        moved.append("source moved")
    problems = []
    if had["value"] != now["value"]:
        problems.append("value")
    if problems:
        print("CHECK FAILED")
        return 3
    if moved:
        print("STALE face behind its source")
        return 3
    return 0
'''

_SRC_NO_STALE_PATH = '''
import json
def cmd_check(args):
    now = build()
    if now["problems"]:
        print("CHECK FAILED")
        return 3
    return 0
'''

_SRC_NOT_A_PROBE = '''
import json
def parse_rows(text):
    if "bad" in text:
        print("CHECK FAILED to parse")
        return 3
    return 0
'''


def selftest():
    legs = []

    def chk(cond, msg):
        legs.append((bool(cond), msg))

    rows = audit_source(_SRC_BYTES_FIRST)
    chk([r["verdict"] for r in rows] == ["BYTES_FIRST"],
        "L1 a drift exit before the defect exit reads BYTES_FIRST")

    rows = audit_source(_SRC_VALUES_FIRST)
    chk([r["verdict"] for r in rows] == ["VALUES_FIRST"],
        "L2 the same two branches swapped read VALUES_FIRST (the shape that freezes a face)")

    rows = audit_source(_SRC_NO_STALE_PATH)
    chk([r["verdict"] for r in rows] == ["NO_STALE_PATH"],
        "L3 a check probe with no STALE exit at all is a hazard on its own -- the chain "
        "cannot hear it and will never pay a writer")

    rows = audit_source(_SRC_NOT_A_PROBE)
    chk(rows == [],
        "L4 a parser that prints CHECK FAILED is not a probe and is not reported")

    # L5 -- the live module this audit was written for must stay fixed.
    path = os.path.join(ROOT, "scripts", "etf_book_year_concentration_money.py")
    src = io.open(path, encoding="utf-8").read()
    verdicts = {r["scope"]: r["verdict"] for r in audit_source(src)}
    chk(verdicts.get("cmd_check") == "BYTES_FIRST",
        "L5 scripts/etf_book_year_concentration_money.py:cmd_check is BYTES_FIRST")

    # L6..L8 -- behavioural, through the real probe rather than through its source.
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    import importlib
    m = importlib.import_module("etf_book_year_concentration_money")
    real_out = m.OUT

    def _probe(mutate):
        """Doctor a receipt that has first been synced to the live source.

        Probing whatever is on disk makes the legs depend on the live face being
        fresh -- under a running chain that face is rewritten between probes and a
        leg reads STALE for a reason unrelated to branch order (r1861 family).
        Syncing first isolates the one field each leg is about.
        """
        with io.open(real_out, encoding="utf-8") as f:
            base = json.load(f)
        fresh = m.build()
        doc = json.loads(json.dumps(base))
        doc["source_face"]["sha16"] = fresh["source_face"]["sha16"]
        doc["source_face"]["asof"] = fresh["source_face"]["asof"]
        doc["evidence_cutoff"] = fresh["evidence_cutoff"]
        mutate(doc)
        tmp = os.path.join(os.path.dirname(real_out), "_drift_precedence_probe.json")
        with io.open(tmp, "w", encoding="utf-8") as f:
            f.write(json.dumps(doc, ensure_ascii=False, indent=1))
        m.OUT = tmp
        buf = io.StringIO()
        old = sys.stdout
        sys.stdout = buf
        try:
            rc = m.cmd_check(None)
        finally:
            sys.stdout = old
            m.OUT = real_out
            os.remove(tmp)
        return rc, buf.getvalue()

    rc, txt = _probe(lambda d: d["source_face"].__setitem__("sha16", "0" * 16))
    chk(rc == 3 and "STALE" in txt and "CHECK FAILED" not in txt,
        "L6 a receipt priced on moved source bytes reads STALE, never CHECK FAILED")

    def _moved_and_bent(d):
        d["source_face"]["sha16"] = "0" * 16
        d["books"][0]["derived"]["value_cny"] = 1

    rc, txt = _probe(_moved_and_bent)
    chk(rc == 3 and "STALE" in txt and "held back" in txt and "CHECK FAILED" not in txt,
        "L7 when the source moved and a number disagrees too, the STALE line names how many "
        "mismatches were held back (the republish is not blind)")

    rc, txt = _probe(lambda d: d["books"][0]["derived"].__setitem__("value_cny", 1))
    chk(rc == 3 and "CHECK FAILED" in txt and "STALE" not in txt,
        "L8 with the source holding still a bent number stays a defect and prints no STALE")

    ok = sum(1 for c, _ in legs if c)
    for c, msg in legs:
        print(("PASS " if c else "FAIL ") + msg)
    print("\nselftest {}/{} PASS".format(ok, len(legs)))
    return 0 if ok == len(legs) else 1


def main(argv=None):
    p = argparse.ArgumentParser(description="check_drift_precedence_audit")
    p.add_argument("mode", nargs="?", default="run", choices=["run", "check", "selftest"])
    args = p.parse_args(argv)
    if args.mode == "selftest":
        return selftest()
    if args.mode == "check":
        return cmd_check(args)
    return cmd_run(args)


if __name__ == "__main__":
    raise SystemExit(main())
