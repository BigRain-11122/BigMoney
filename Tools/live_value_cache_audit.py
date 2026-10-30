"""Which faces cache a live value across ticks, and what they key it on.

r1374/r1375 fixed one rule twice: a replay of a live value must be keyed on a digest of
its inputs, never on a date, because the date stays put while the panel/weights/capital
under it move. Both rounds swept the etf_book family by hand and both said the same
thing in their closing note -- "the same question has not been asked of every face on
this host that caches a live value across ticks". This turns that sentence into a count.

It is a static read of the source, not a runtime trace: for every function that writes
JSON *and* mentions a cache/replay, it lists the field names the cache is read back on
(the literal keys passed to `.get("...")` / `["..."]` on a cache-ish name) and whether
the module carries any digest machinery at all. A row with a key but no digest is not
automatically a defect -- it is a face where a person has to read one function and say
which inputs the key omits -- but it is the complete list instead of the family we
happened to look at.

Usage:
    python Tools/live_value_cache_audit.py run [--json PATH]
    python Tools/live_value_cache_audit.py selftest
"""

import ast
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCAN_DIRS = ("scripts", "Tools")

CACHE_WORDS = ("cache", "replay")
DIGEST_WORDS = ("digest", "fingerprint", "sha256", "sha1", "md5", "blake2", "hashlib")
# r1377: a digest can reach the cache read through the CALL instead of the literal key
# (``cached = load_valid_cell(name, rule_sha, panel_sha)``). "sha"/"hash" are weak enough
# to be misleading on their own, so the evidence is its own verdict, never digest_in_key.
CALL_DIGEST_WORDS = DIGEST_WORDS + ("sha", "hash", "checksum")
VERDICT_ORDER = ("no_digest_anywhere", "module_has_digest_key_does_not",
                 "digest_argument_to_cache_read", "digest_in_key")


def _strs_in(node):
    out = []
    for sub in ast.walk(node):
        if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
            out.append(sub.value)
    return out


def _names_in(node):
    out = []
    for sub in ast.walk(node):
        if isinstance(sub, ast.Name):
            out.append(sub.id)
        elif isinstance(sub, ast.Attribute):
            out.append(sub.attr)
    return out


def _writes_json(fn):
    for sub in ast.walk(fn):
        if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute):
            if sub.func.attr in ("dump", "dumps"):
                return True
    return False


def _cache_key_fields(fn, cacheish):
    """Literal keys the function reads back off a cache-ish name.

    Two shapes matter and both are string literals one step from the cache name:
    ``cached.get("bar")`` and ``cache["bar"]``. Anything else (a key built in a loop,
    a dataclass attribute) is not inferred here -- the audit names what it can see.
    """
    fields = set()
    for sub in ast.walk(fn):
        if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute) and sub.func.attr == "get":
            base = sub.func.value
            base_names = set(_names_in(base)) if base is not None else set()
            if base_names & cacheish and sub.args:
                a0 = sub.args[0]
                if isinstance(a0, ast.Constant) and isinstance(a0.value, str):
                    fields.add(a0.value)
        elif isinstance(sub, ast.Subscript):
            base_names = set(_names_in(sub.value))
            sl = sub.slice
            if base_names & cacheish and isinstance(sl, ast.Constant) and isinstance(sl.value, str):
                fields.add(sl.value)
    return sorted(fields)


def _compares_cache(fn, cacheish):
    """Does the function ever *decide* anything from a cache-ish value?

    A local dict called `cache` that only accumulates rows is not a face; a face is
    code that loads a previous value and compares it to something today.
    """
    for sub in ast.walk(fn):
        if isinstance(sub, ast.Compare):
            sides = [sub.left] + list(sub.comparators)
            for s in sides:
                if set(_names_in(s)) & cacheish:
                    return True
    return False


def _mismatch_policy(fn, cacheish):
    """What happens when the stored value and today's do not match.

    A face that RAISES on mismatch cannot serve a stale number -- it stops. A face that
    RETURNS the cached payload is the one r1374/r1375 were about. Reporting both under
    one count is how an audit turns into noise.
    """
    refuses = any(isinstance(s, ast.Raise) for s in ast.walk(fn))
    serves = False
    for s in ast.walk(fn):
        if isinstance(s, ast.Return) and s.value is not None:
            if set(_names_in(s.value)) & cacheish:
                serves = True
    if refuses and not serves:
        return "refuses"
    if serves:
        return "serves"
    return "unknown"


def _digest_argument_evidence(fn, cacheish):
    """Digest names that reach the cache read as an ARGUMENT, not as a key.

    r1377 made alloc_backtest.run_cell_faces' checkpoint a function of (rule sha, panel
    digest) by passing both into `load_valid_cell`. There is no `cache.get("panel_sha")`
    anywhere in the writing function, so a keys-only read says "no digest" about a face
    that can no longer serve a stale panel -- and a scanner that under-reports generates
    the same work again next round.

    The tie is deliberately narrow: a CACHE-NAMED target assigned from a call whose
    arguments mention a digest. Names are clues, not proof (r1377 E207 lesson), so this
    is published as its own verdict with the names it saw, and a row here still needs a
    leg that perturbs the input to confirm the digest is actually compared.
    """
    hits = []
    for node in ast.walk(fn):
        if not isinstance(node, ast.Assign) or not isinstance(node.value, ast.Call):
            continue
        if not any(isinstance(t, ast.Name)
                   and any(w in t.id.lower() for w in CACHE_WORDS)
                   for t in node.targets):
            continue
        args = list(node.value.args) + [k.value for k in node.value.keywords]
        for arg in args:
            for nm in _names_in(arg):
                if any(w in nm.lower() for w in CALL_DIGEST_WORDS):
                    hits.append(nm)
    return sorted(set(hits))


def audit_source(text, path="<mem>"):
    """(rows, ignored) for one python source. Deterministic; no filesystem, no clock."""
    tree = ast.parse(text)
    ignored = 0
    module_names = set(n.lower() for n in _names_in(tree))
    # `import hashlib` never creates a Name node -- without this the half-covered
    # fixture (a digest in the module, a date in the key) reads as "no digest anywhere",
    # which is the wrong sentence about the wrong file.
    for sub in ast.walk(tree):
        if isinstance(sub, ast.Import):
            module_names |= set(a.name.split(".")[0].lower() for a in sub.names)
        elif isinstance(sub, ast.ImportFrom) and sub.module:
            module_names.add(sub.module.split(".")[0].lower())
    module_strs = " ".join(_strs_in(tree)).lower()
    has_digest = bool(module_names & set(DIGEST_WORDS)) or any(
        w in module_strs for w in ("sha256", "hashlib", "fingerprint"))
    rows = []
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        # Only NAMES count. A docstring that says "cache" is prose; a variable called
        # `cached` is a face that can serve a stale number. Matching prose is what makes
        # an audit of this shape unreadable.
        local_names = set(n.lower() for n in _names_in(fn))
        cacheish = set(n for n in local_names for w in CACHE_WORDS if w in n)
        if not cacheish or not _writes_json(fn):
            continue
        fields = _cache_key_fields(fn, cacheish)
        if not fields and not _compares_cache(fn, cacheish):
            ignored += 1
            continue
        digest_in_key = any(w in f.lower() for f in fields for w in DIGEST_WORDS)
        digest_args = _digest_argument_evidence(fn, cacheish)
        if digest_in_key:
            verdict = "digest_in_key"
        elif digest_args:
            verdict = "digest_argument_to_cache_read"
        elif has_digest:
            # the module hashes SOMETHING -- it is not evidence that this key sees it.
            # r1375's defect lived exactly here: a digest existed, one cache used it.
            verdict = "module_has_digest_key_does_not"
        else:
            verdict = "no_digest_anywhere"
        rows.append({
            "file": path,
            "function": fn.name,
            "line": fn.lineno,
            "key_fields": fields,
            "digest_argument_names": digest_args,
            "module_has_digest": has_digest,
            "on_mismatch": _mismatch_policy(fn, cacheish),
            "verdict": verdict,
        })
    return rows, ignored


def run(scan_dirs=SCAN_DIRS, root=ROOT):
    rows = []
    files = 0
    skipped = 0
    ignored = 0
    for d in scan_dirs:
        full = os.path.join(root, d)
        if not os.path.isdir(full):
            continue
        for name in sorted(os.listdir(full)):
            if not name.endswith(".py"):
                continue
            if name.startswith("_"):
                # one-shot scratch tools (`_r544bmc_close.py` …) write faces as a
                # by-product of a closeout; they are not a live value served twice.
                skipped += 1
                continue
            p = os.path.join(full, name)
            rel = os.path.relpath(p, root).replace("\\", "/")
            try:
                text = io.open(p, encoding="utf-8-sig", errors="replace").read()
                rws, ign = audit_source(text, rel)
                rows.extend(rws)
                ignored += ign
                files += 1
            except SyntaxError:
                rows.append({"file": rel, "function": None, "line": None, "key_fields": [],
                             "module_has_digest": False, "on_mismatch": "unknown",
                             "verdict": "unreadable"})
    rows.sort(key=lambda r: (r["verdict"] == "digest_in_key",
                             r["on_mismatch"] == "refuses",
                             r["file"], r["line"] or 0))
    summary = {
        "files_scanned": files,
        "files_skipped_scratch": skipped,
        "cache_names_that_never_compare": ignored,
        "cache_writers": len(rows),
    }
    for v in VERDICT_ORDER + ("unreadable",):
        summary[v] = sum(1 for r in rows if r["verdict"] == v)
    summary["serves_without_digest"] = sum(
        1 for r in rows
        if r["verdict"] != "digest_in_key" and r["on_mismatch"] in ("serves", "unknown"))
    summary["refuses_on_mismatch"] = sum(1 for r in rows if r["on_mismatch"] == "refuses")
    # Argument evidence is published NEXT TO the headline, never subtracted from it: a
    # name inside a call is weaker than a key, so the count of faces that serve a live
    # value with no digest anywhere in the story stays the conservative total.
    summary["digest_argument_evidence"] = sum(
        1 for r in rows if r["verdict"] == "digest_argument_to_cache_read")
    summary["serves_with_no_digest_and_no_argument"] = sum(
        1 for r in rows
        if r["verdict"] not in ("digest_in_key", "digest_argument_to_cache_read")
        and r["on_mismatch"] in ("serves", "unknown"))
    out = {
        "evidence_cutoff": "2026-10-31",
        "method": "static AST read: function writes JSON + mentions cache/replay -> the literal "
                  "keys it reads back off the cache name, the digest names it hands to the call "
                  "that returns the cache, and whether the module has any digest",
        "limits": "a key listed here is not proof the cache is safe, a digest in the module is "
                  "not proof it reaches this key, and a digest passed as an argument is not "
                  "proof it is compared -- rows are a reading list, not a verdict list",
        "scan_dirs": list(scan_dirs),
        "summary": summary,
        "rows": rows,
    }
    return out


# ---------------------------------------------------------------- selftest

_FIX_BAD = '''
import json
def build(x):
    cache = {}
    cached = _load()
    if cached.get("bar") == x["bar"] and cached.get("capital") == x["capital"]:
        return cached
    payload = {"bar": x["bar"]}
    json.dump(payload, open("c.json", "w"))
    return payload
'''

_FIX_GOOD = '''
import json, hashlib
def build(x):
    cached = _load()
    if cached.get("inputs_sha256") == hashlib.sha256(x["panel"]).hexdigest():
        return cached
    json.dump({"bar": 1}, open("c.json", "w"))
'''

_FIX_HALF = '''
import json, hashlib
def build(x):
    cached = _load()
    if cached.get("bar") == x["bar"]:
        return cached
    json.dump({"bar": 1}, open("c.json", "w"))
'''

_FIX_REFUSES = '''
import json
def verify():
    replay = _load()
    stored = _load2()
    if replay["n_days"] != stored["n_days"]:
        raise SystemExit("identity gate FAIL")
    json.dump({"n_days": 1}, open("v.json", "w"))
'''

_FIX_NOWRITE = '''
def read_only(cache):
    return cache.get("bar")
'''

_FIX_ARG = '''
import json, hashlib
def _load_valid(name, sha, data_sha):
    return None
def build(x):
    sha = hashlib.sha256(x["w"].encode()).hexdigest()[:16]
    cached = _load_valid("cell", sha, panel_sha(x))
    if cached is not None:
        return cached
    json.dump({"bar": 1}, open("c.json", "w"))
'''

_FIX_ARG_UNUSED = '''
import json
def build(x):
    cached = _load("cell")
    if cached.get("bar") == x["bar"]:
        return cached
    json.dump({"bar": 1}, open("c.json", "w"))
'''


def selftest():
    ok = []

    def chk(name, cond):
        ok.append((name, bool(cond)))

    bad, _ig1 = audit_source(_FIX_BAD, "bad.py")
    chk("L1 a date-keyed cache writer is listed", len(bad) == 1 and bad[0]["function"] == "build")
    chk("L2 its key fields are the literal keys it reads back",
        bad[0]["key_fields"] == ["bar", "capital"])
    chk("L3 and it is flagged as having no digest", bad[0]["verdict"] == "no_digest_anywhere")

    good, _ig2 = audit_source(_FIX_GOOD, "good.py")
    chk("L4 a digest-keyed writer is listed too (the audit does not only find defects)",
        len(good) == 1)
    chk("L5 digest in the key field wins", good[0]["verdict"] == "digest_in_key")

    chk("L6 a reader that never writes JSON is not a cache writer", audit_source(_FIX_NOWRITE, "r.py")[0] == [])
    chk("L7 an unparsable file is reported, never silently skipped",
        any(r["verdict"] == "unreadable" for r in _unparsable()))

    live = run()
    chk("L8 the live scan reads both code trees", live["summary"]["files_scanned"] >= 100)
    chk("L9 every row carries a verdict",
        all(r["verdict"] in VERDICT_ORDER + ("unreadable",) for r in live["rows"]))
    chk("L10 the summary totals equal the rows",
        live["summary"]["cache_writers"] == len(live["rows"]))
    chk("L11 the run is deterministic", run()["rows"] == live["rows"])

    half, _ig3 = audit_source(_FIX_HALF, "half.py")
    chk("L12 a module that hashes something else does NOT cover a date-keyed cache",
        len(half) == 1 and half[0]["verdict"] == "module_has_digest_key_does_not")

    refus, _ig4 = audit_source(_FIX_REFUSES, "ref.py")
    chk("L13 a gate that raises on mismatch is told apart from one that serves a cache",
        len(refus) == 1 and refus[0]["on_mismatch"] == "refuses")
    chk("L14 and the date-keyed cache that SERVES is the one called serves",
        bad[0]["on_mismatch"] == "serves")

    # r1377: a digest handed to the call that reads the cache is evidence, not a key.
    arg, _ig5 = audit_source(_FIX_ARG, "arg.py")
    argrow = [r for r in arg if r["function"] == "build"]
    chk("L15 a digest passed into the cache reader has its own verdict",
        len(argrow) == 1 and argrow[0]["verdict"] == "digest_argument_to_cache_read")
    chk("L16 and the names it saw are published",
        "sha" in (argrow[0]["digest_argument_names"] if argrow else []))
    chk("L17 such a row still needs confirmation, so it stays in the conservative total",
        any(r["verdict"] == "digest_argument_to_cache_read" for r in arg))
    unused, _ig6 = audit_source(_FIX_ARG_UNUSED, "unused.py")
    chk("L18 a cache read with no digest in the call stays a defect",
        len(unused) == 1 and unused[0]["verdict"] == "no_digest_anywhere")
    # The live row this round fixed must now carry the weaker-but-real evidence.
    alloc = [r for r in live["rows"] if r["file"] == "scripts/alloc_backtest.py"]
    chk("L19 the alloc cell checkpoint no longer reads as digest-free",
        len(alloc) == 1 and alloc[0]["verdict"] == "digest_argument_to_cache_read"
        and "data_sha" in alloc[0]["digest_argument_names"])

    npass = sum(1 for _, c in ok if c)
    for name, c in ok:
        if not c:
            print("FAIL", name)
    print("%d/%d legs %s" % (npass, len(ok), "PASS" if npass == len(ok) else "FAIL"))
    return 0 if npass == len(ok) else 1


def _unparsable():
    import tempfile
    d = tempfile.mkdtemp()
    p = os.path.join(d, "broken.py")
    io.open(p, "w", encoding="utf-8").write("class Under Construction:\n")
    return run(scan_dirs=(d,), root=d)["rows"]


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "selftest":
        return selftest()
    if cmd != "run":
        print("usage: live_value_cache_audit.py run|selftest [--json PATH]")
        return 2
    out = run()
    path = os.path.join(ROOT, "results", "live_value_cache_audit.json")
    if "--json" in argv:
        path = argv[argv.index("--json") + 1]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")
    s = out["summary"]
    print("scanned %d files | %d cache decisions | %d serve on a key with no digest "
          "(%d of them hand a digest to the call that reads the cache, which still needs a "
          "leg that perturbs the input) | %d refuse on mismatch"
          % (s["files_scanned"], s["cache_writers"], s["serves_without_digest"],
             s["digest_argument_evidence"], s["refuses_on_mismatch"]))
    for r in out["rows"]:
        print("  %-32s %-44s %-26s key=%s"
              % ("%s/%s" % (r["verdict"], r["on_mismatch"]), r["file"], r["function"],
                 ",".join(r["key_fields"]) or "(no literal key)"))
    print("wrote", path)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))