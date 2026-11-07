#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A committed JSON face must parse, and must not carry the same key twice.

r1404 (bm-c).  The book's forward ledger (`results/etf_book_forward/LEDGER.json`) was
committed on 2026-11-07 with two defects that no existing gate could see:

* a missing comma between two elements of `drift.settled_bars` ("2026-11-06" then
  "2026-11-05"), so `json.load` raises and every reader of the ledger -- the order
  ticket, the CEO page, the settle audit, the carry re-derivation -- dies at open;
* the `drift` block carries `faces` and `max_abs` TWICE (an updated block spliced in
  front of the old one).  `json.loads` accepts duplicate keys silently and keeps the
  LAST, so even after the comma is fixed the file would report the OLD measurement as
  if it were the current one.

Both defects are the shape a line-level conflict resolution leaves behind on a file
that git does not parse. The pre-commit claw only looks for conflict markers, and a
missing comma or a repeated key carries none.

So this guard reads every tracked JSON face the way a reader would and asks two
questions per file: does it parse, and does any object repeat a key? The duplicate
scan uses `object_pairs_hook`, which is the only place Python shows you the pairs
before it drops one of them.

Usage:
    python Tools/json_face_guard.py                 # tracked results/**.json (default)
    python Tools/json_face_guard.py --all           # every tracked *.json
    python Tools/json_face_guard.py --paths a.json b.json
    python Tools/json_face_guard.py --selftest

Exit codes: 0 clean, 1 findings, 2 mechanism failure (git unreadable, etc.).
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIZE_CAP = 4 * 1024 * 1024          # a face over this is data, not a document
DEFAULT_PATHS = ["results"]


# ------------------------------------------------------------------ parsing
class _Dupes(object):
    """Collects duplicate-key paths while the document stays loadable."""

    def __init__(self):
        self.hits = []

    def hook(self, pairs):
        seen, out = set(), {}
        for k, v in pairs:
            if k in seen:
                self.hits.append(k)
            seen.add(k)
            out[k] = v
        return out


def read_text(path):
    """(text, bom, encoding). Every committed reader opens with encoding='utf-8', so a
    file that is UTF-16 on disk is a failure for them however well-formed it is."""
    with open(path, "rb") as f:
        raw = f.read()
    bom = raw.startswith(b"\xef\xbb\xbf")
    try:
        return raw.decode("utf-8-sig"), bom, "utf-8"
    except UnicodeDecodeError:
        for enc in ("utf-16", "utf-16-be", "utf-16-le"):
            try:
                return raw.decode(enc), bom, enc
            except (UnicodeDecodeError, UnicodeError):
                continue
        return None, bom, "undecodable"


def judge_bytes(raw, path, size=None):
    """One verdict for one byte string -- the only place the two questions are asked.

    Both readers (a file on disk, and the staged blob the commit will actually
    carry) come through here, so `--staged` cannot drift from the default scan.
    """
    doc = {"path": path, "size": len(raw) if size is None else size}
    if doc["size"] > SIZE_CAP:
        doc.update({"verdict": "skipped_too_large", "ok": None})
        return doc
    bom = raw.startswith(b"\xef\xbb\xbf")
    try:
        text, enc = raw.decode("utf-8-sig"), "utf-8"
    except UnicodeDecodeError:
        text = None
        for cand in ("utf-16", "utf-16-be", "utf-16-le"):
            try:
                text, enc = raw.decode(cand), cand
                break
            except (UnicodeDecodeError, UnicodeError):
                continue
        if text is None:
            enc = "undecodable"
    if text is None:
        doc.update({"verdict": "encoding", "ok": False,
                    "reason": "not decodable as utf-8 or utf-16"})
        return doc
    dupes = _Dupes()
    try:
        value = json.loads(text, object_pairs_hook=dupes.hook)
    except ValueError as exc:
        doc.update({
            "verdict": "parse_error", "ok": False,
            "line": getattr(exc, "lineno", None),
            "col": getattr(exc, "colno", None),
            "reason": getattr(exc, "msg", str(exc)),
        })
        return doc
    doc["bom"] = bom
    doc["root_type"] = type(value).__name__
    if enc != "utf-8":
        doc.update({"verdict": "encoding", "ok": False, "encoding": enc,
                    "reason": "committed as %s; every reader opens encoding='utf-8'" % enc})
        return doc
    if dupes.hits:
        doc.update({"verdict": "duplicate_keys", "ok": False,
                    "duplicate_keys": sorted(set(dupes.hits))})
        return doc
    doc.update({"verdict": "ok", "ok": True})
    return doc


def inspect(path):
    """One verdict per file on disk: parsed / parse error / duplicate keys / skip."""
    try:
        size = os.path.getsize(path)
    except OSError as exc:
        return {"path": path, "size": 0, "verdict": "unreadable", "ok": None,
                "reason": str(exc)}
    if size > SIZE_CAP:
        return {"path": path, "size": size, "verdict": "skipped_too_large", "ok": None}
    try:
        with open(path, "rb") as f:
            raw = f.read()
    except OSError as exc:
        return {"path": path, "size": size, "verdict": "unreadable", "ok": None,
                "reason": str(exc)}
    return judge_bytes(raw, path, size)


# ------------------------------------------------------------------ scanning
def tracked(pattern_args):
    cmd = ["git", "ls-files", "-z"] + pattern_args
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True)
    if p.returncode != 0:
        raise RuntimeError("git ls-files failed rc=%d: %s"
                           % (p.returncode, p.stderr.decode("utf-8", "replace")[:300]))
    names = [n for n in p.stdout.decode("utf-8", "replace").split("\0") if n]
    return names


def default_paths():
    """The faces people read. Scratch and per-round receipt dumps are named with a
    leading underscore by house convention (results/_r1403bmc_*.json) and are swept
    with --all instead, because a dump that is not a document is not a finding."""
    dirs = [d for d in DEFAULT_PATHS if os.path.isdir(os.path.join(ROOT, d))]
    names = [n for n in tracked(dirs) if n.lower().endswith(".json")]
    return [n for n in names if not os.path.basename(n).startswith("_")]


def all_paths():
    return [n for n in tracked([]) if n.lower().endswith(".json")]


def staged_paths():
    """Files this commit would add or modify -- what the hook must judge.

    A deleted path is not a face anyone will read, so it is not in scope.
    """
    p = subprocess.run(["git", "diff", "--cached", "--name-only", "-z",
                        "--diff-filter=ACMR"], cwd=ROOT, capture_output=True)
    if p.returncode != 0:
        raise RuntimeError("git diff --cached failed rc=%d: %s"
                           % (p.returncode, p.stderr.decode("utf-8", "replace")[:300]))
    names = [n for n in p.stdout.decode("utf-8", "replace").split("\0") if n]
    return [n for n in names if n.lower().endswith(".json")]


def read_index_blob(path):
    """The bytes the commit will carry, not the worktree copy beside them.

    The r1404 ledger defect was introduced by a resolution whose worktree file and
    staged blob were not the same text; judging the worktree would have passed a
    commit that shipped the broken one.
    """
    p = subprocess.run(["git", "show", ":" + path], cwd=ROOT, capture_output=True)
    if p.returncode != 0:
        raise RuntimeError("git show :%s failed rc=%d" % (path, p.returncode))
    return p.stdout


def scan_staged():
    """Same contract as scan(), read off the index."""
    rows = []
    for rel in staged_paths():
        try:
            raw = read_index_blob(rel)
        except RuntimeError as exc:
            rows.append({"path": rel, "verdict": "unreadable", "ok": None,
                         "reason": str(exc)})
            continue
        rows.append(judge_bytes(raw, rel))
    findings = [r for r in rows if r.get("ok") is False]
    skipped = [r for r in rows if r.get("ok") is None]
    return {
        "checked": len(rows),
        "clean": sum(1 for r in rows if r.get("ok") is True),
        "findings": findings,
        "skipped": skipped,
        "verdict": "CLEAN" if not findings else "FINDINGS",
    }


def scan(paths):
    rows = [inspect(os.path.join(ROOT, p)) for p in paths]
    findings = [r for r in rows if r.get("ok") is False]
    skipped = [r for r in rows if r.get("ok") is None]
    return {
        "checked": len(rows),
        "clean": sum(1 for r in rows if r.get("ok") is True),
        "findings": findings,
        "skipped": skipped,
        "verdict": "CLEAN" if not findings else "FINDINGS",
    }


# ------------------------------------------------------------------ selftest
def _selftest():
    import tempfile

    legs = []

    def leg(name, got, want):
        ok = got == want
        legs.append({"leg": name, "ok": ok, "got": got, "want": want})

    def probe(text, name="f.json"):
        d = tempfile.mkdtemp(prefix="jsonface_")
        p = os.path.join(d, name)
        with open(p, "w", encoding="utf-8") as f:
            f.write(text)
        return inspect(p)

    # L1 a well-formed face reads clean.
    leg("valid json -> ok", probe('{"a": 1, "b": [1, 2]}')["verdict"], "ok")
    # L2 the exact defect that broke the ledger: two list elements with no comma.
    r = probe('{"settled_bars": ["2026-11-06" "2026-11-05"]}')
    leg("missing comma between list elements -> parse_error", r["verdict"], "parse_error")
    leg("parse error carries the line", r["line"], 1)
    # L3 duplicate keys are accepted by json, so they must be caught explicitly.
    leg("duplicate key at root -> duplicate_keys",
        probe('{"faces": [], "max_abs": 0.0, "faces": ["x"], "max_abs": 1.2}')["verdict"],
        "duplicate_keys")
    leg("duplicate key named",
        probe('{"faces": [], "faces": ["x"]}')["duplicate_keys"], ["faces"])
    # L4 a duplicate nested two levels down is still found (the ledger's own shape).
    leg("nested duplicate found",
        probe('{"drift": {"checked_bars": 11, "max_abs": 0.0, "max_abs": 1.16e-06}}')
        ["verdict"], "duplicate_keys")
    # L5 the same key in two SIBLING objects is not a duplicate.
    leg("same key in sibling objects is clean",
        probe('{"a": {"x": 1}, "b": {"x": 2}}')["verdict"], "ok")
    # L6 a BOM is reported, not silently tolerated as a difference nobody sees.
    leg("bom detected", probe('\ufeff{"a": 1}')["bom"], True)
    # L7 an array root parses but is named, so a "document" that is a list is visible.
    leg("array root named", probe('[1, 2, 3]')["root_type"], "list")
    # L8 determinism: the same bytes give the same verdict and nothing else moves.
    text = '{"drift": {"faces": [], "faces": []}}'
    a, b = probe(text), probe(text)
    for k in ("path",):
        a.pop(k, None)
        b.pop(k, None)
    leg("deterministic", a, b)
    # L9 an empty file is a finding, not a pass -- "no content" is not "no problem".
    leg("empty file -> parse_error", probe("")["verdict"], "parse_error")
    # L10 a well-formed UTF-16 face still fails, because every committed reader opens
    # encoding='utf-8' -- "it parses for me" is not the reader's experience.
    d = tempfile.mkdtemp(prefix="jsonface16_")
    p16 = os.path.join(d, "u16.json")
    with open(p16, "wb") as f:
        f.write('{"a": 1}'.encode("utf-16"))
    leg("utf-16 face -> encoding finding", inspect(p16)["verdict"], "encoding")

    # ---- L11..L14: the staged reader judges the INDEX, not the worktree beside it --
    global ROOT
    repo = tempfile.mkdtemp(prefix="jsonface_staged_")
    keep = ROOT
    try:
        subprocess.run(["git", "init", "-q"], cwd=repo, capture_output=True)
        ROOT = repo

        def _stage(name, text):
            with open(os.path.join(repo, name), "w", encoding="utf-8") as f:
                f.write(text)
            subprocess.run(["git", "add", "-f", name], cwd=repo, capture_output=True)

        _stage("good.json", '{"a": 1}')
        d_good = scan_staged()
        leg("a staged valid face is clean", (d_good["verdict"], d_good["checked"]),
            ("CLEAN", 1))

        _stage("twin.json", '{"drift": {"max_abs": 0.0, "max_abs": 1.16e-06}}')
        d_bad = scan_staged()
        leg("a staged duplicate key blocks", d_bad["verdict"], "FINDINGS")
        leg("the blocked file is named",
            [f["path"] for f in d_bad["findings"]], ["twin.json"])

        # The whole reason for reading the index: the worktree copy can already be
        # repaired while the commit still carries the broken blob.
        with open(os.path.join(repo, "twin.json"), "w", encoding="utf-8") as f:
            f.write('{"drift": {"max_abs": 1.16e-06}}')
        leg("a repaired worktree does not clear the staged finding",
            scan_staged()["verdict"], "FINDINGS")

        subprocess.run(["git", "rm", "-q", "--cached", "-f", "twin.json"], cwd=repo,
                       capture_output=True)
        os.remove(os.path.join(repo, "twin.json"))
        leg("a removal is not a face to judge", scan_staged()["verdict"], "CLEAN")

        # A non-JSON staged file is out of scope (this guard is not a linter).
        _stage("notes.md", "# not a face\n")
        leg("non-json staged files are ignored",
            (scan_staged()["verdict"], scan_staged()["checked"]), ("CLEAN", 1))
    finally:
        ROOT = keep

    ok = sum(1 for l in legs if l["ok"])
    for l in legs:
        print("[%s] %s" % ("PASS" if l["ok"] else "FAIL", l["leg"]))
        if not l["ok"]:
            print("   got=%r want=%r" % (l["got"], l["want"]))
    print("SELFTEST %d/%d legs" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


# ------------------------------------------------------------------ main
def main(argv):
    if "--selftest" in argv:
        return _selftest()
    try:
        if "--staged" in argv:
            doc = scan_staged()
            doc["scope"] = "staged"
            # The hook runs this on every commit: say nothing when there is nothing
            # to say, so a clean commit's output stays the user's own.
            if doc["verdict"] == "CLEAN":
                return 0
            print("json_face_guard: the staged JSON face(s) below will not open")
            for f in doc["findings"]:
                print("  %-14s %s%s" % (
                    f["verdict"], f["path"],
                    (" line %s: %s" % (f.get("line"), f.get("reason")))
                    if f["verdict"] == "parse_error" else
                    (" keys %s" % ",".join(f.get("duplicate_keys") or []))))
            return 1
        if "--all" in argv:
            paths = all_paths()
        elif "--paths" in argv:
            paths = argv[argv.index("--paths") + 1:]
        else:
            paths = default_paths()
    except RuntimeError as exc:
        print("MECHANISM %s" % exc)
        return 2
    doc = scan(paths)
    doc["scope"] = "all" if "--all" in argv else ("paths" if "--paths" in argv else "results")
    print(json.dumps({k: doc[k] for k in ("scope", "checked", "clean", "verdict")},
                     ensure_ascii=False))
    for f in doc["findings"]:
        print("  %-8s %s%s" % (f["verdict"], f["path"],
                               (" line %s: %s" % (f.get("line"), f.get("reason"))) if
                               f["verdict"] == "parse_error" else
                               (" keys %s" % ",".join(f.get("duplicate_keys") or []))))
    if doc["skipped"]:
        print("  skipped %d file(s) over %d bytes or unreadable" % (len(doc["skipped"]), SIZE_CAP))
    return 0 if doc["verdict"] == "CLEAN" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))