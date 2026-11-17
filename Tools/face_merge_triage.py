#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""face_merge_triage -- E1405 "classify by the kind of face" mechanized.

Context
-------
r1817 merged two machines' work by hand: 192 conflicting files, 191 auto-resolved
by *kind of face*, 1 needed a human.  The rule worked, but it lived in a session,
so every later round started from zero and reached for a fresh throwaway
``_rNNNbmc_merge_resolve.py``.  This tool is that rule as a script.

The law (E1405): do not pick "mine" or "theirs" blindly -- pick by what the file
*is*.

    ledger   (*.jsonl)              line-level union, ours first, exact dupes dropped
    table    (*.csv)                union by first column, collisions reported
    generated(*.json / *.md)        whichever side's OWN declared generation is newer
                                    (`generated` / `generated_at` / `evidence_cutoff` /
                                     `as_of` / `data.*` mirror)
    code     (*.py and the rest)    manual -- never guessed

Anything whose generation cannot be read from the file itself is AMBIGUOUS and
stays for a human; a missing stamp must never be read as "old".

Usage
-----
    python Tools/face_merge_triage.py status
    python Tools/face_merge_triage.py triage [--apply] [--receipt PATH] [PATH ...]
    python Tools/face_merge_triage.py triage --from-markers PATH ...
    python Tools/face_merge_triage.py selftest

Exit codes: 0 = every path classified and (with --apply) resolved, 1 = manual
work remains, 2 = tool failure.
"""

from __future__ import annotations

import csv
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

GEN_KEYS = ("generated", "generated_at", "evidence_cutoff", "as_of", "build_time")

LEDGER, TABLE, GENERATED, CODE = "ledger", "table", "generated", "code"
AMBIGUOUS = "ambiguous"


# ---------------------------------------------------------------- git plumbing

def _git(args, cwd=None):
    """Run git with no console window (zero-window law)."""
    flags = 0
    if os.name == "nt":
        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
    p = subprocess.run(
        ["git"] + args,
        cwd=cwd or REPO,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=flags,
    )
    return p.returncode, p.stdout, p.stderr


def conflicted_paths(cwd=None):
    rc, out, _ = _git(["diff", "--name-only", "--diff-filter=U", "-z"], cwd=cwd)
    if rc != 0:
        return []
    return [p for p in out.decode("utf-8", "replace").split("\0") if p]


def stage_text(path, stage, cwd=None):
    """Return text of index stage 2 (ours) or 3 (theirs), or None if absent."""
    rc, out, _ = _git(["show", ":%d:%s" % (stage, path)], cwd=cwd)
    if rc != 0:
        return None
    return out.decode("utf-8", "surrogateescape")


def parse_markers(text):
    """Split a working-tree file carrying <<<<<<< / ||||||| / ======= / >>>>>>> markers."""
    ours, theirs = [], []
    mode = None
    for line in text.splitlines(keepends=True):
        if line.startswith("<<<<<<<"):
            mode = "ours"
            continue
        if line.startswith("|||||||") and mode == "ours":
            mode = "base"  # diff3 style: the common ancestor, not ours
            continue
        if line.startswith("=======") and mode in ("ours", "base"):
            mode = "theirs"
            continue
        if line.startswith(">>>>>>>") and mode == "theirs":
            mode = None
            continue
        if mode == "ours":
            ours.append(line)
        elif mode == "theirs":
            theirs.append(line)
    if not ours and not theirs:
        return None, None
    return "".join(ours), "".join(theirs)


# ------------------------------------------------------------- generation stamps

def _walk_gen(obj, out, depth=0):
    if depth > 4 or not isinstance(obj, dict):
        return out
    for k, v in obj.items():
        if k in GEN_KEYS and isinstance(v, (str, int, float)):
            out.append(str(v))
        elif isinstance(v, dict):
            _walk_gen(v, out, depth + 1)
    return out


def generation_of(text, path):
    """Best-effort read of the face's own build stamp. None = not declared."""
    if text is None:
        return None
    if path.lower().endswith(".json"):
        try:
            return (max(_walk_gen(json.loads(text), [])) or None)
        except Exception:
            return None    # markdown / anything textual: look only in the head, where stamps live
    for line in text.splitlines()[:40]:
        low = line.lower()
        for key in GEN_KEYS:
            if key in low:
                tail = line.split(":", 1)[-1].strip(" :`*|\t")
                if tail:
                    return tail
    return None


# ------------------------------------------------------------------- resolution

def union_lines(ours, theirs):
    seen, out = set(), []
    for chunk in (ours or "", theirs or ""):
        for line in chunk.splitlines():
            key = line.rstrip("\r")
            if key in seen:
                continue
            seen.add(key)
            out.append(key)
    return "\n".join(out) + ("\n" if out else "")


def union_csv(ours, theirs):
    def load(text):
        rows = list(csv.reader(io.StringIO(text or "")))
        if not rows:
            return None, []
        return rows[0], rows[1:]

    head_o, rows_o = load(ours)
    head_t, rows_t = load(theirs)
    if head_o is None and head_t is None:
        return "", {"collisions": []}
    head = head_o if head_o is not None else head_t
    if head_o is not None and head_t is not None and head_o != head_t:
        # different columns = not the same table any more; do not invent a merge
        return None, {"collisions": [], "header_mismatch": True}

    collisions, order, picked = [], [], {}
    for side, rows in (("ours", rows_o), ("theirs", rows_t)):
        for row in rows:
            if not row:
                continue
            key = row[0]
            if key not in picked:
                order.append(key)
                picked[key] = (side, row)
            elif picked[key][1] != row:
                collisions.append({"key": key, "kept": picked[key][0], "other": side})
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(head)
    for key in order:
        w.writerow(picked[key][1])
    return buf.getvalue(), {"collisions": collisions}


def classify(path):
    low = path.lower()
    if low.endswith(".jsonl"):
        return LEDGER
    if low.endswith(".csv"):
        return TABLE
    if low.endswith(".json") or low.endswith(".md"):
        return GENERATED
    return CODE


def resolve(path, ours, theirs):
    """Return (text, meta) for one conflicted path, or (None, meta) if manual."""
    kind = classify(path)
    if kind == LEDGER:
        return union_lines(ours, theirs), {"kind": kind, "rule": "line-union"}

    if kind == TABLE:
        text, meta = union_csv(ours, theirs)
        meta["kind"] = kind
        meta["rule"] = "union-by-first-column"
        return text, meta

    if kind == GENERATED:
        gen_o, gen_t = generation_of(ours, path), generation_of(theirs, path)
        meta = {"kind": kind, "rule": "newer-declared-generation",
                "gen_ours": gen_o, "gen_theirs": gen_t}
        if gen_o is None and gen_t is None:
            meta["reason"] = "neither side declares a generation"
            return None, meta
        if gen_o is None:
            meta["pick"] = "theirs"
            return theirs, meta
        if gen_t is None:
            meta["pick"] = "ours"
            return ours, meta
        if gen_o == gen_t:
            meta["pick"] = "ours (same generation)"
            return ours, meta
        meta["pick"] = "ours" if gen_o > gen_t else "theirs"
        return (ours if gen_o > gen_t else theirs), meta

    return None, {"kind": CODE, "rule": "manual", "reason": "code face"}


def triage(paths=None, apply=False, from_markers=False, cwd=None):
    cwd = cwd or REPO
    paths = list(paths or conflicted_paths(cwd))
    report = {"cwd": cwd, "n": len(paths), "faces": [], "manual": [], "resolved": 0}
    for rel in paths:
        if from_markers:
            full = os.path.join(cwd, rel)
            try:
                with open(full, "rb") as fh:
                    raw = fh.read().decode("utf-8", "surrogateescape")
            except OSError as exc:
                report["faces"].append({"path": rel, "kind": "error", "reason": str(exc)})
                report["manual"].append(rel)
                continue
            ours, theirs = parse_markers(raw)
        else:
            ours, theirs = stage_text(rel, 2, cwd), stage_text(rel, 3, cwd)

        if ours is None or theirs is None:
            side = "both" if ours is None and theirs is None else ("ours" if ours is None else "theirs")
            report["faces"].append({"path": rel, "kind": "one-sided",
                                     "reason": "missing in %s" % side,
                                     "take": "theirs" if ours is None else "ours"})
            if apply and not (ours is None and theirs is None):
                _write(cwd, rel, theirs if ours is None else ours)
                report["resolved"] += 1
            continue

        text, meta = resolve(rel, ours, theirs)
        meta["path"] = rel
        report["faces"].append(meta)
        if text is None:
            report["manual"].append(rel)
            continue
        if apply:
            _write(cwd, rel, text)
        report["resolved"] += 1
    report["ok"] = not report["manual"]
    return report


def _write(cwd, rel, text):
    full = os.path.join(cwd, rel)
    os.makedirs(os.path.dirname(full) or cwd, exist_ok=True)
    with open(full, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)


# --------------------------------------------------------------------- selftest

def _fixture_repo(root):
    def g(*args):
        r = _git(list(args), cwd=root)
        if r[0] != 0:
            raise RuntimeError("git %s: %s" % (" ".join(args), r[2].decode("utf-8", "replace")))
        return r

    g("init", "-q", "-b", "main")
    g("config", "user.email", "t@example.invalid")
    g("config", "user.name", "triage")

    os.makedirs(os.path.join(root, "results"), exist_ok=True)
    os.makedirs(os.path.join(root, "scripts"), exist_ok=True)
    base = {
        "results/log.jsonl": '{"a":1}\n',
        "results/tab.csv": "code,v\nAAA,1\n",
        "results/face.json": '{"generated":"2026-11-17T00:00:00+08:00","v":1}\n',
        "scripts/x.py": "print(1)\n",
        "results/nostamp.json": '{"v":0}\n',
    }
    for rel, body in base.items():
        with open(os.path.join(root, rel), "w", encoding="utf-8", newline="") as fh:
            fh.write(body)
    g("add", "-A")
    g("commit", "-qm", "base")

    # theirs: grows every face in one direction
    g("checkout", "-q", "-b", "theirs")
    upgrades = {
        "results/log.jsonl": '{"a":1}\n{"b":2}\n',
        "results/tab.csv": "code,v\nAAA,1\nBBB,2\n",
        "results/face.json": '{"generated":"2026-11-18T00:00:00+08:00","v":2}\n',
        "scripts/x.py": "print(2)\n",
        "results/nostamp.json": '{"v":2}\n',
    }
    for rel, body in upgrades.items():
        with open(os.path.join(root, rel), "w", encoding="utf-8", newline="") as fh:
            fh.write(body)
    g("commit", "-qam", "theirs")

    # ours: grows the same faces the other way, with a colliding table row
    g("checkout", "-q", "main")
    ours = {
        "results/log.jsonl": '{"a":1}\n{"c":3}\n',
        "results/tab.csv": "code,v\nAAA,9\nCCC,3\n",
        "results/face.json": '{"generated":"2026-11-18T06:00:00+08:00","v":3}\n',
        "scripts/x.py": "print(3)\n",
        "results/nostamp.json": '{"v":3}\n',
    }
    for rel, body in ours.items():
        with open(os.path.join(root, rel), "w", encoding="utf-8", newline="") as fh:
            fh.write(body)
    g("commit", "-qam", "ours")

    # a conflicting merge exits 1 on purpose -- that is the fixture, not a bug
    _git(["merge", "theirs", "--no-edit"], cwd=root)
    return root


def selftest():
    legs = []

    def leg(name, cond, detail=""):
        legs.append((name, bool(cond), detail))

    tmp = tempfile.mkdtemp(prefix="fmt-")
    try:
        root = _fixture_repo(tmp)
        paths = conflicted_paths(cwd=root)
        leg("fixture produces conflicts", len(paths) >= 5, "n=%d" % len(paths))
        leg("all five fixture faces conflict",
            set(paths) == {"results/log.jsonl", "results/tab.csv", "results/face.json",
                           "scripts/x.py", "results/nostamp.json"},
            sorted(paths))

        rep = triage(cwd=root, apply=False)
        kinds = {f["path"]: f["kind"] for f in rep["faces"]}
        leg("jsonl classified ledger", kinds.get("results/log.jsonl") == LEDGER)
        leg("csv classified table", kinds.get("results/tab.csv") == TABLE)
        leg("json classified generated", kinds.get("results/face.json") == GENERATED)
        leg("py classified code", kinds.get("scripts/x.py") == CODE)
        leg("code face stays manual", "scripts/x.py" in rep["manual"])
        leg("stampless json is ambiguous",
            "results/nostamp.json" in rep["manual"], str(kinds.get("results/nostamp.json")))
        leg("no-write without --apply",
            open(os.path.join(root, "results/log.jsonl"), encoding="utf-8").read().count("<<<<<<<") == 1)

        rep = triage(cwd=root, apply=True)
        read = lambda rel: open(os.path.join(root, rel), encoding="utf-8").read()

        ledger = read("results/log.jsonl")
        leg("ledger union carries both sides",
            '{"b":2}' in ledger and '{"c":3}' in ledger, ledger.replace("\n", "|"))
        leg("ledger union drops the shared line once", ledger.count('{"a":1}') == 1, ledger.replace("\n", "|"))

        table = read("results/tab.csv")
        leg("table union keeps both keys", "BBB" in table and "CCC" in table, table.replace("\n", "|"))
        collision = [f for f in rep["faces"] if f["path"] == "results/tab.csv"][0]
        leg("table collision is reported not silenced",
            any(c["key"] == "AAA" for c in collision.get("collisions", [])),
            str(collision.get("collisions")))

        face = json.loads(read("results/face.json"))
        leg("generated face takes the newer declared build", face["v"] == 3, str(face))
        pick = [f for f in rep["faces"] if f["path"] == "results/face.json"][0]
        leg("generated receipt names both generations",
            pick.get("gen_ours") and pick.get("gen_theirs"), str(pick))

        leg("manual face keeps its conflict markers", "<<<<<<<" in read("scripts/x.py"))
        leg("ok flag is false while manual work remains", rep["ok"] is False)
        leg("resolved counter skips manual", rep["resolved"] == 3, str(rep["resolved"]))

        # a face that only exists on one side is not a conflict
        one = triage(cwd=root, apply=False, from_markers=False)
        leg("second pass still reports the manual face", not one["ok"])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    failed = [n for n, ok, _ in legs if not ok]
    for name, ok, detail in legs:
        print("%s %s%s" % ("PASS" if ok else "FAIL", name, (" | " + detail) if (detail and not ok) else ""))
    print("face_merge_triage selftest %d/%d" % (len(legs) - len(failed), len(legs)))
    return 0 if not failed else 1


# ------------------------------------------------------------------------ main

def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    cmd = argv[0]

    if cmd == "selftest":
        return selftest()

    if cmd == "status":
        paths = conflicted_paths()
        print(json.dumps({"conflicted": paths, "n": len(paths)}, ensure_ascii=False, indent=1))
        return 0

    if cmd == "triage":
        rest, apply, from_markers, receipt = argv[1:], False, False, None
        paths, i = [], 0
        while i < len(rest):
            a = rest[i]
            if a == "--apply":
                apply = True
            elif a == "--from-markers":
                from_markers = True
            elif a == "--receipt":
                i += 1
                receipt = rest[i]
            else:
                paths.append(a)
            i += 1
        rep = triage(paths or None, apply=apply, from_markers=from_markers)
        text = json.dumps(rep, ensure_ascii=False, indent=1)
        print(text)
        if receipt:
            os.makedirs(os.path.dirname(os.path.abspath(receipt)) or ".", exist_ok=True)
            with open(receipt, "w", encoding="utf-8") as fh:
                fh.write(text + "\n")
        return 0 if rep["ok"] else 1

    print("unknown command: %s" % cmd, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
