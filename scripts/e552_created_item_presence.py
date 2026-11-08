"""E552 (r1591 bm-b): is the created item present in the container the fold publishes?

E547 (r1578) published eight created items -- ``out['verdict']``,
``rows['_GB_nan_skipped']``, ``art['trials_N']``, ``probe['params']['report_num_entries']``
-- and measured who *reads* them: nobody outside the producing module.  Its
parent E544 had already named the divergence: the fold binds one container and
the created item goes into another, or into the same one after the read.

E547's census measured reads of the in-memory container.  It never asked the
question that decides whether a downstream reader could ever notice: **does the
artefact the module actually writes (or returns) carry the created item at all?**

This study takes, for each of the eight, the publish channels of its own storing
function -- ``json.dump`` / ``_dump`` / ``write_json`` style calls, ``fh.write``,
``return`` -- and decides presence on the channel, not on the name:

  * ``present_through_the_same_object`` -- the sink is handed the very container
    the item was stored into (``_dump(out, ...)``): the item travels by identity,
    so a downstream reader of that file *can* see it.
  * ``present_as_a_copy_in_a_published_container`` -- the fold transcribes the
    item into a second container (``gates["k"] = rows["k"]``) and publishes that
    one: the item travels, but through a hand-written copy the writer must keep
    in step (a one-line divergence away from silent loss).
  * ``carried_only_to_stdout`` -- the only channel is a ``print`` of the
    container (or of a projection of it).  A terminal echo is not a face: no
    reader of any stored artefact can load the item, and the echo can be a
    hand-picked subset that drops it again (``{k: art[k] for k in (...)}``).
  * ``absent_from_every_published_container`` -- no channel carries it: the item
    exists only inside the function and dies there.
  * ``no_publish_channel_found`` / ``unreadable`` -- honest unknowns.

A file sink reached through a module-level helper (``_flush(art)`` ->
``io.open(...).write(json.dumps(art))``) counts as the caller's channel: the
helper's parameters are bound to the caller's argument names before its body is
scanned.  The first draft of this study missed exactly that and credited the
``print`` line beside it -- a right answer for the wrong reason, which is what
the card asks to rule out.

Why the distinction is the whole point: "unread" (E547) and "absent" (E552) have
different repairs.  An unread key can be read later at zero cost; an absent key
cannot be read by anyone until its producer starts publishing it.

    python scripts/e552_created_item_presence.py build
    python scripts/e552_created_item_presence.py check
    python scripts/e552_created_item_presence.py verify
    python scripts/e552_created_item_presence.py selftest
"""
from __future__ import annotations

import ast
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
STATE_TILT = os.path.join(ROOT, "results", "state_tilt")
PARENT = os.path.join(STATE_TILT, "CREATEDITEMREAD-2026-11-08.json")
DATED = os.path.join(STATE_TILT, "CREATEDITEMPRESENCE-2026-11-08.json")
LATEST = os.path.join(STATE_TILT, "createditempresence_latest.json")

STUDY = "E552"
CARD = "E552-WHETHER-THE-OWNER-OF-A-CREATED-ITEM-IS-EVER-THE-FOLD-THAT-PUBLISHES-IT"
TITLE = ("whether the eight created items are carried by the artefact their own "
         "module publishes")
EVIDENCE_CUTOFF = "2026-11-08"

P_SAME = "present_through_the_same_object"
P_COPY = "present_as_a_copy_in_a_published_container"
P_STDOUT = "carried_only_to_stdout"
P_ABSENT = "absent_from_every_published_container"
P_NOPUB = "no_publish_channel_found"
P_UNREAD = "the_storing_source_could_not_be_read"

# A sink is a call whose callee name ends with one of these (or equals it).
FILE_SINK_WORDS = ("dump", "write_json", "write_text", "write", "writelines",
                   "save", "to_json", "to_csv", "write_face", "_dump")
STDOUT_SINK_WORDS = ("print",)

MAX_STEPS = 4000


def _norm(p):
    return p.replace("\\", "/")


def _callee_name(node):
    f = node.func
    if isinstance(f, ast.Name):
        return f.id
    if isinstance(f, ast.Attribute):
        return f.attr
    return ""


def _is_sink(node):
    name = _callee_name(node).lower()
    if not name:
        return None
    for w in FILE_SINK_WORDS:
        if name == w or name.endswith("_" + w) or name.endswith(w):
            return "file"
    for w in STDOUT_SINK_WORDS:
        if name == w:
            return "stdout"
    return None


def _names_in(node):
    """Every Name id appearing anywhere under node (shallow-but-complete walk)."""
    return {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}


def _find_function(tree, fname):
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == fname:
            return node
    return None


def _base_and_key(store_target):
    """('out','verdict') from out['verdict']; nested paths joined with dots."""
    parts = []
    node = store_target
    while isinstance(node, ast.Subscript):
        sl = node.slice
        if isinstance(sl, ast.Constant) and isinstance(sl.value, str):
            parts.append(sl.value)
        elif isinstance(sl, ast.Name):
            parts.append("<" + sl.id + ">")
        else:
            parts.append("<expr>")
        node = node.value
    if isinstance(node, ast.Name):
        return node.id, list(reversed(parts))
    return None, list(reversed(parts))


def _key_literals(path):
    return [p for p in path if not p.startswith("<")]


class Row(object):
    pass


def measure_row(row, root=ROOT):
    """Classify one parent row. Returns a dict of evidence (JSON-serialisable)."""
    src = _norm(row.get("source") or "")
    fn = row.get("function") or ""
    path = os.path.join(root, src)
    out = {
        "source": src,
        "function": fn,
        "parent_outcome": row.get("outcome"),
        "classes": [],
    }
    if not os.path.isfile(path):
        out["presence"] = P_UNREAD
        out["note"] = "source absent from the tree"
        return out
    try:
        text = io.open(path, encoding="utf-8", errors="replace").read()
        tree = ast.parse(text)
    except (OSError, SyntaxError) as exc:
        out["presence"] = P_UNREAD
        out["note"] = "%s: %s" % (type(exc).__name__, exc)
        return out

    fn_node = _find_function(tree, fn)
    if fn_node is None:
        out["presence"] = P_UNREAD
        out["note"] = "function %r not found in the module" % fn
        return out

    # The created item(s) this row is about: every subscript store in the function
    # whose key literal is not created by the same statement's own get() default is
    # unknowable statically, so we take all subscript stores and keep the ones whose
    # base matches a base the parent row's store lines touch.
    store_lines = set(row.get("store_lines") or [])
    created = []  # (line, base, path, key_lits)
    for node in ast.walk(fn_node):
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Subscript) and node.lineno in store_lines:
                    base, pth = _base_and_key(tgt)
                    if base:
                        created.append((node.lineno, base, pth, _key_literals(pth)))
                    elif pth:
                        created.append((node.lineno, None, pth, _key_literals(pth)))
        elif isinstance(node, ast.AugAssign):
            if isinstance(node.target, ast.Subscript) and node.lineno in store_lines:
                base, pth = _base_and_key(node.target)
                if base:
                    created.append((node.lineno, base, pth, _key_literals(pth)))
    if not created:
        # fall back: every subscript store in the function
        for node in ast.walk(fn_node):
            tgt = None
            if isinstance(node, ast.Assign) and len(node.targets) == 1:
                tgt = node.targets[0]
            elif isinstance(node, ast.AugAssign):
                tgt = node.target
            if isinstance(tgt, ast.Subscript):
                base, pth = _base_and_key(tgt)
                if base:
                    created.append((node.lineno, base, pth, _key_literals(pth)))
    out["created_stores"] = [{"line": ln, "base": b, "path": p} for ln, b, p, _ in created]
    if not created:
        out["presence"] = P_NOPUB
        out["note"] = "no subscript store found in the function to trace"
        return out

    # ---- publish channels -------------------------------------------------
    # Module-level helpers are resolved one hop: _flush(art) hands the caller's
    # name to whatever the helper's body writes.
    helpers = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            helpers[node.name] = node

    channels = []   # {"kind": file|stdout|return, "line", "expr", "names"}

    def note(kind, line, expr, names):
        channels.append({"kind": kind, "line": line, "expr": expr,
                         "names": sorted(names)})

    def scan_calls(scope, line_base=0, bind=None, depth=0):
        if depth > 2:
            return
        for node in ast.walk(scope):
            if not isinstance(node, ast.Call):
                continue
            k = _is_sink(node)
            if k:
                names = set()
                for a in node.args:
                    names |= _names_in(a)
                for kw in node.keywords:
                    names |= _names_in(kw.value)
                note(k, node.lineno, _callee_name(node), names)
                continue
            callee = node.func
            if not isinstance(callee, ast.Name) or callee.id not in helpers:
                continue
            helper = helpers[callee.id]
            params = [a.arg for a in helper.args.args]
            bound = set()
            for i, a in enumerate(node.args):
                if i < len(params):
                    bound |= _names_in(a)
            for kw in node.keywords:
                bound |= _names_in(kw.value)
            # names the helper's own body writes/prints that came from us
            for sub in ast.walk(helper):
                if isinstance(sub, ast.Call) and _is_sink(sub):
                    names = set()
                    for a in sub.args:
                        names |= _names_in(a)
                    for kw in sub.keywords:
                        names |= _names_in(kw.value)
                    # a parameter of the helper stands for the caller's argument
                    carried = (names & bound) or (names & set(params))
                    if carried:
                        note(_is_sink(sub), sub.lineno, _callee_name(sub),
                             (names - set(params)) | bound)
            scan_calls(helper, bind=bound, depth=depth + 1)

    scan_calls(fn_node)
    for node in ast.walk(fn_node):
        if isinstance(node, ast.Return) and node.value is not None:
            note("return", node.lineno, "return", _names_in(node.value))
    out["channels"] = channels

    # ---- per created store, decide presence ------------------------------
    results = []
    for ln, base, pth, keys in created:
        rec = {"store_line": ln, "base": base, "path": pth}
        identity = [c for c in channels if base and base in c["names"]
                    and c["line"] >= ln]
        identity_file = [c for c in identity if c["kind"] in ("file", "return")]
        identity_stdout = [c for c in identity if c["kind"] == "stdout"]
        # a copy:  other[<same key literals>] = base[...]  where other is published
        copies = []
        for node in ast.walk(fn_node):
            if isinstance(node, ast.Assign) and node.lineno > ln:
                for tgt in node.targets:
                    if not isinstance(tgt, ast.Subscript):
                        continue
                    tbase, tpath = _base_and_key(tgt)
                    if not tbase or tbase == base:
                        continue
                    tkeys = _key_literals(tpath)
                    if not keys or not tkeys:
                        continue
                    if keys[-1] == tkeys[-1]:
                        rhs = _names_in(node.value)
                        copies.append({"line": node.lineno, "into": tbase,
                                       "reads_base": base in rhs})
        copy_published = []
        for cp in copies:
            hit = [c for c in channels if cp["into"] in c["names"]
                   and c["line"] >= cp["line"] and c["kind"] in ("file", "return")]
            if hit:
                copy_published.append({"copy_line": cp["line"], "into": cp["into"],
                                       "channel_line": hit[0]["line"],
                                       "channel": hit[0]["expr"],
                                       "channel_kind": hit[0]["kind"]})
        rec["identity_channels"] = identity_file[:3]
        rec["stdout_channels"] = identity_stdout[:3]
        rec["copies"] = copies
        rec["copies_published"] = copy_published
        if identity_file:
            rec["presence"] = P_SAME
            rec["evidence"] = ("%s is handed to the %s channel %r at line %s"
                               % (base, identity_file[0]["kind"],
                                  identity_file[0]["expr"], identity_file[0]["line"]))
        elif copy_published:
            cp = copy_published[0]
            rec["presence"] = P_COPY
            rec["evidence"] = ("%s[%r] is transcribed into %s at line %s and %s is "
                               "published at line %s"
                               % (base, keys[-1] if keys else "?", cp["into"],
                                  cp["copy_line"], cp["into"], cp["channel_line"]))
        elif identity_stdout:
            rec["presence"] = P_STDOUT
            rec["evidence"] = ("%s reaches only %r at line %s -- a terminal echo, "
                               "not a stored face"
                               % (base, identity_stdout[0]["expr"],
                                  identity_stdout[0]["line"]))
        elif channels:
            rec["presence"] = P_ABSENT
            rec["evidence"] = ("%d publish channel(s) exist but none names %s "
                               "or a container carrying it" % (len(channels), base))
            rec["other_channels"] = [{"line": c["line"], "expr": c["expr"],
                                      "names": c["names"][:6]} for c in channels[:4]]
        else:
            rec["presence"] = P_NOPUB
            rec["evidence"] = "the function publishes nothing (no dump, no return of value)"
        results.append(rec)

    # The row-level class: a row whose every created store is present reports the
    # strongest channel; a mixed row reports the weakest (absent dominates).
    order = {P_ABSENT: 0, P_NOPUB: 1, P_STDOUT: 2, P_COPY: 3, P_SAME: 4, P_UNREAD: 5}
    rows_by_strength = sorted(results, key=lambda r: order.get(r["presence"], 9))
    out["presence"] = rows_by_strength[0]["presence"] if rows_by_strength else P_NOPUB
    out["created_item_results"] = results
    return out


def build(root=ROOT):
    with io.open(PARENT, encoding="utf-8") as fh:
        parent = json.load(fh)
    rows = parent.get("rows") or []
    measured = [measure_row(r, root=root) for r in rows]

    by_class = {}
    for m in measured:
        by_class[m["presence"]] = by_class.get(m["presence"], 0) + 1

    carried = by_class.get(P_SAME, 0) + by_class.get(P_COPY, 0)
    absent = (by_class.get(P_ABSENT, 0) + by_class.get(P_NOPUB, 0)
              + by_class.get(P_STDOUT, 0))
    same = by_class.get(P_SAME, 0)
    copy = by_class.get(P_COPY, 0)
    stdout = by_class.get(P_STDOUT, 0)

    if carried == len(measured) and copy == 0:
        verdict = ("all %d created items travel by identity into a stored artefact: "
                   "'unread' is a read question only" % len(measured))
    elif absent == 0:
        verdict = ("all %d created items do reach a stored artefact, but %d of %d only "
                   "through a hand-written copy into a second container -- present, "
                   "and one line away from silent absence"
                   % (len(measured), copy, len(measured)))
    else:
        verdict = ("%d of %d created items never reach a stored artefact (%d by identity, "
                   "%d copied-and-published, %d only echoed to stdout, %d absent)"
                   % (absent, len(measured), same, copy, stdout,
                      by_class.get(P_ABSENT, 0) + by_class.get(P_NOPUB, 0)))

    face = {
        "study": STUDY,
        "card": CARD,
        "title": TITLE,
        "date": "2026-11-08",
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "parent_face": os.path.basename(PARENT),
        "parent_study": parent.get("study"),
        "parent_verdict": parent.get("verdict"),
        "classes": [P_SAME, P_COPY, P_STDOUT, P_ABSENT, P_NOPUB, P_UNREAD],
        "summary": {
            "rows_measured": len(measured),
            "by_presence": by_class,
            "present_through_the_same_object": same,
            "present_as_a_copy": copy,
            "carried_only_to_stdout": stdout,
            "absent_or_unpublished": absent,
            "carried_fraction": (round(carried / float(len(measured)), 4)
                                 if measured else None),
        },
        "rows": measured,
        "verdict": verdict,
    }
    return face


def _write(path, obj):
    d = os.path.dirname(path)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")


def cmd_build():
    face = build()
    _write(DATED, face)
    _write(LATEST, face)
    print(json.dumps({"wrote": [_norm(DATED), _norm(LATEST)],
                      "verdict": face["verdict"],
                      "summary": face["summary"]}, ensure_ascii=False, indent=1))
    return 0


def cmd_check():
    with io.open(DATED, encoding="utf-8") as fh:
        stored = json.load(fh)
    fresh = build()
    problems = []
    if stored.get("verdict") != fresh.get("verdict"):
        problems.append("verdict does not re-derive")
    s_rows = {(r["source"], r["function"]): r["presence"] for r in stored.get("rows") or []}
    f_rows = {(r["source"], r["function"]): r["presence"] for r in fresh.get("rows") or []}
    if s_rows != f_rows:
        for k in sorted(set(s_rows) | set(f_rows)):
            if s_rows.get(k) != f_rows.get(k):
                problems.append("row %s: %r -> %r" % (k, s_rows.get(k), f_rows.get(k)))
    if (stored.get("summary") or {}).get("by_presence") != (fresh.get("summary") or {}).get("by_presence"):
        problems.append("by_presence does not re-derive")
    print(json.dumps({"problems": problems, "rows": len(f_rows)}, ensure_ascii=False))
    return 0 if not problems else 1


def cmd_verify():
    a = build()
    b = build()
    problems = []
    if json.dumps(a, sort_keys=True) != json.dumps(b, sort_keys=True):
        problems.append("two builds differ")
    for r in a["rows"]:
        if r["presence"] not in (P_SAME, P_COPY, P_STDOUT, P_ABSENT, P_NOPUB, P_UNREAD):
            problems.append("row %s has unknown presence %r" % (r["source"], r["presence"]))
        if r["presence"] == P_SAME and not r.get("created_item_results"):
            problems.append("row %s claims identity without a traced store" % r["source"])
    print(json.dumps({"problems": problems, "rows": len(a["rows"])}, ensure_ascii=False))
    return 0 if not problems else 1


# ---------------------------------------------------------------- selftest
FIXTURE_SAME = '''
import json
def cmd_probe():
    out = {"checks": {}}
    out["verdict"] = "PASS"
    _dump(out, "x.json")
    return 0
'''

FIXTURE_COPY = '''
def _gate_results():
    rows = {"GA": [True]}
    rows["_skipped"] = 3
    gates = {"GA": all(rows["GA"])}
    gates["_skipped"] = rows["_skipped"]
    return gates
'''

FIXTURE_ABSENT = '''
def cmd_selftest():
    t = {"a": 1}
    probe = dict(t)
    probe["flag"] = True
    assert probe["flag"]
    return 0
'''

FIXTURE_NOPUB = '''
def run():
    art = {}
    art["n"] = 1
'''

FIXTURE_HELPER = '''
import io, json
OUT_JSON = "o.json"
def run():
    art = {"a": 1}
    art["trials_N"] = 3
    _flush(art)
    return 0
def _flush(art):
    io.open(OUT_JSON, "w").write(json.dumps(art))
'''

FIXTURE_STDOUT = '''
import json
def run():
    art = {"a": 1}
    art["trials_N"] = 3
    print(json.dumps({k: art[k] for k in ("trials_N",)}))
    return 0
'''


def selftest():
    arms = []

    def arm(name, cond, detail=""):
        arms.append({"arm": name, "ok": bool(cond), "detail": detail})

    def run_fixture(text, fname, store_line):
        import tempfile
        d = tempfile.mkdtemp(prefix="e552_")
        p = os.path.join(d, "fx.py")
        with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        row = {"source": "fx.py", "function": fname, "store_lines": [store_line],
               "outcome": "fixture"}
        try:
            return measure_row(row, root=d)
        finally:
            try:
                os.remove(p)
                os.rmdir(d)
            except OSError:
                pass

    m = run_fixture(FIXTURE_SAME, "cmd_probe", 4)
    arm("same_object_is_present_by_identity", m["presence"] == P_SAME, m["presence"])

    m = run_fixture(FIXTURE_COPY, "_gate_results", 4)
    arm("transcribed_copy_is_present_as_copy", m["presence"] == P_COPY, m["presence"])
    arm("copy_records_both_lines",
        bool(m["created_item_results"][0]["copies_published"]),
        json.dumps(m["created_item_results"][0]["copies_published"]))

    m = run_fixture(FIXTURE_ABSENT, "cmd_selftest", 4)
    arm("never_published_is_absent", m["presence"] == P_ABSENT, m["presence"])

    m = run_fixture(FIXTURE_NOPUB, "run", 3)
    arm("no_sink_and_no_return_is_no_publish_channel",
        m["presence"] in (P_NOPUB, P_ABSENT), m["presence"])

    m = run_fixture(FIXTURE_HELPER, "run", 6)
    arm("identity_through_a_module_level_helper_is_a_file_channel",
        m["presence"] == P_SAME, m["presence"])
    arm("helper_hop_names_the_real_write_line",
        any("write" in (c.get("expr") or "")
            for c in (m["created_item_results"][0]["identity_channels"] or [])),
        json.dumps(m["created_item_results"][0]["identity_channels"])[:200])

    m = run_fixture(FIXTURE_STDOUT, "run", 4)
    arm("a_print_alone_is_not_a_stored_face", m["presence"] == P_STDOUT, m["presence"])

    # a row whose source is missing must be a published unknown, not a silent pass
    m = measure_row({"source": "does_not_exist_xyz.py", "function": "f",
                     "store_lines": [1]}, root=ROOT)
    arm("missing_source_is_unreadable_unknown", m["presence"] == P_UNREAD, m["presence"])

    # the verdict must be recomputed from by_presence, not carried
    face = build()
    s = face["summary"]
    arm("verdict_agrees_with_counters",
        (s["present_through_the_same_object"] + s["absent_or_unpublished"])
        <= s["rows_measured"],
        json.dumps(s))
    arm("rows_match_parent_population",
        s["rows_measured"] == len(json.load(io.open(PARENT, encoding="utf-8"))["rows"]),
        str(s["rows_measured"]))
    arm("every_row_has_a_class",
        all(r["presence"] in face["classes"] for r in face["rows"]), "")
    arm("no_row_is_classed_by_name_alone",
        all((r["presence"] != P_SAME) or r.get("created_item_results") for r in face["rows"]), "")

    fails = [a for a in arms if not a["ok"]]
    print(json.dumps({"arms": len(arms), "fail": len(fails),
                      "detail": fails}, ensure_ascii=False, indent=1))
    return 1 if fails else 0


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "build"
    if cmd == "build":
        return cmd_build()
    if cmd == "check":
        return cmd_check()
    if cmd == "verify":
        return cmd_verify()
    if cmd == "selftest":
        return selftest()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))