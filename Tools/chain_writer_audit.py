"""Does every face the S6 chain only *checks* have something that *writes* it?

WHY THIS EXISTS: r1471 caught one by hand -- the execution ledger was read by a ticket and by
the CEO page, both consumers were green, and no leg on the chain ever wrote it, so the ticket
sized itself off a hand-run file from a previous world. r1594 found the second (the premium
subscription face sat on `check` only and printed CONFLICT_BETWEEN_RECEIPTS all night), and
r1618 fixed it by hanging a `premium_subscription_write` leg. Both were found by a person
reading a page. The chain already encodes the answer for 49 faces -- a leg entry with a third
element is "this check, and the leg that regenerates it" -- so the rest is mechanical: every
leg whose argv is a reader, with no writer for the same script and the same scope, is a face
whose freshness nothing on the chain is responsible for.

WHAT THIS CAN AND CANNOT SAY: it answers "is there a leg that regenerates this face", not
"is the writer's gate correct" and not "was the last write on time". A face can have a writer
leg and still be stale (a no-op gate that never opens, r1289), and a face with no writer can
be legitimately derived (a pure measurement over other faces' published rows -- those are the
NO_WRITER_MODE rows, disclosed rather than failed). The narrow claim is deliberate: it is the
cheap question, and a red here is exactly the r1471 shape -- the script knows how to write the
face, and the chain never asks it to.

USAGE:
    python Tools/chain_writer_audit.py             # report + write results/chain_writer_audit.json
    python Tools/chain_writer_audit.py --check     # rc1 when a face has a writer the chain never calls
    python Tools/chain_writer_audit.py --selftest  # offline invariants (no disk, no chain run)
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import re
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAIN = os.path.join(ROOT, "Tools", "s6_chain_bmc.py")
RESULTS = os.path.join(ROOT, "results")
OUT = os.path.join(RESULTS, "chain_writer_audit.json")

# A token that asks a script to *look* rather than *produce*. `explain`/`status`/`probe` are
# readers in this repo's own dialect (fill_ladder explain, py_watermark probe); `selftest` is
# offline and never publishes, so a face whose only leg is a selftest is in the same shape.
READER_TOKENS = {"check", "selftest", "status", "explain", "probe", "show", "verify"}

# What a token is when its reader suffix is removed. `--floor-check` and `--floor` are the same
# scope; `check` and a bare invocation are the same scope. Built from the repo's actual legs so
# a new "-check" flag does not need a new rule.
CHECK_SUFFIXES = ("-check",)

WRITER_MODES = {"run", "write", "refresh", "rebuild", "snapshot", "certify", "fetch", "build"}

JSON_LITERAL = re.compile(r"['\"]([A-Za-z0-9_\-\.]+\.json)['\"]")
SUB_CMD = re.compile(r"argv\[1\]\s*==\s*['\"]([A-Za-z0-9_\-]+)['\"]")
ADD_PARSER = re.compile(r"add_parser\(\s*['\"]([A-Za-z0-9_\-]+)['\"]")
ADD_ARG = re.compile(r"add_argument\(\s*['\"](--[A-Za-z0-9_\-]+)['\"]")
DEF_RUN = re.compile(r"^def\s+(run|write|build|refresh)\s*\(", re.M)


def strip_reader(token):
    """(token with its reader suffix removed, is_reader).

    The bare `--check` case must be answered BEFORE the suffix rule: `--check` ends with
    `-check`, and slicing six characters off it leaves a lone `-`, which silently became its
    own scope and kept 40 paired faces looking unpaired.
    """
    low = token.lower()
    if low in READER_TOKENS or low == "--check":
        return "", True
    for suf in CHECK_SUFFIXES:
        if low.endswith(suf):
            return token[: -len(suf)], True
    return token, False


def parse_head(head):
    """One argv -> {script, tokens, scope, reader}.

    Scope is the argv minus BOTH the reader part and the writer-mode token: `run`/`write` are
    the role, not the subject. Without this the writer leg keys on ("run") and never pairs with
    its own check -- which is how the first draft reported 84 reds, most of them paired faces.

    Flags are also dropped from the scope. `--no-fetch` / `--if-stale` / `--floor` are options
    on the same subject, so a writer that takes one still writes the face its check reads
    (measured: `premium_percentile_write --no-fetch` and `premium_subscription_write
    --if-stale` were both reported red against their own checks). The cost of dropping them is
    that a check flag with no writer twin of the same name still pairs with a differently
    flagged writer; that is the right trade for the question asked here -- is anything on the
    chain responsible for regenerating this face at all.
    """
    script = next((a for a in head if a.endswith(".py")), None)
    if script is None:
        return {"script": None, "tokens": tuple(head), "scope": tuple(head), "reader": False}
    idx = head.index(script)
    tokens = tuple(head[idx + 1:])
    scope, reader = [], False
    for tok in tokens:
        keep, is_reader = strip_reader(tok)
        reader = reader or is_reader
        if not keep:
            continue
        if not keep.startswith("-") and keep.lower() in WRITER_MODES:
            continue
        if keep.startswith("-"):
            continue
        scope.append(keep)
    return {"script": script, "tokens": tokens, "scope": tuple(scope), "reader": reader}


def parse_leg(entry):
    """One LEGS row -> [leg view, ...]. Third element (r1618 form) is the writer for this check."""
    name = entry[0]
    views = []
    for pos, head in enumerate(entry[1:]):
        view = parse_head(list(head))
        view["leg"] = name
        view["role_on_chain"] = ("check", "write")[pos] if len(entry) > 2 else (
            "check" if view["reader"] else "write")
        views.append(view)
    return views


def strip_reader_flag(flag):
    for suf in CHECK_SUFFIXES:
        if flag.lower().endswith(suf):
            return flag[: -len(suf)]
    return flag


def scan_modes(src):
    """What this script can be asked to do, read off its own source (heuristic, named as such).

    Returns {"subcommands": [...], "flags": [...], "bare_writes": bool}. `bare_writes` is the
    repo's dominant convention -- main() falls through to run()/build() when argv carries no
    subcommand -- and is what makes a check-only chain leg a gap rather than a design.
    """
    subs = sorted(set(SUB_CMD.findall(src)) | set(ADD_PARSER.findall(src)))
    flags = sorted(set(ADD_ARG.findall(src)))
    bare = bool(DEF_RUN.search(src)) or any(s in WRITER_MODES for s in subs)
    return {"subcommands": subs, "flags": flags,
            "bare_writes": bare, "writer_modes": [s for s in subs if s in WRITER_MODES]}


def artifact_names(src):
    """JSON files this script names. Underscore captures are excluded (repo scratch convention)."""
    names = []
    for raw in JSON_LITERAL.findall(src):
        if raw.startswith("_"):
            continue
        if raw not in names:
            names.append(raw)
    return tuple(names)


def audit(entries):
    """Pure: LEGS rows -> report. No disk reads (sources are supplied separately by run())."""
    views = [v for entry in entries for v in parse_leg(entry)]
    writers = {}
    readers = {}
    for v in views:
        if v["script"] is None:
            continue
        key = (v["script"], v["scope"])
        (readers if v["reader"] else writers).setdefault(key, []).append(v["leg"])
    findings = []
    for key, legs in sorted(readers.items()):
        if key in writers:
            continue
        findings.append({"script": key[0], "scope": list(key[1]), "legs": sorted(set(legs)),
                         "reason": "no writer leg for this script+scope on the chain"})
    return {
        "legs": len(entries),
        "pairs": sum(1 for e in entries if len(e) > 2),
        "reader_faces": len(readers),
        "writer_faces": len(writers),
        "paired": len([k for k in readers if k in writers]),
        "findings": findings,
    }


def artifact_ages(names, now=None, existing_only=False):
    """(name, exists, age_hours, cutoff) for each artifact under results/.

    A missing name is reported as exists=False / age_h=None, never as 0h: most of the names a
    script spells are fixtures ('latest.json', 'nope.json'), and an empty reading is not a
    young one (r1261 family).
    """
    now = time.time() if now is None else now
    rows = []
    for name in names:
        path = os.path.join(RESULTS, name)
        if not os.path.exists(path):
            if existing_only:
                continue
            rows.append({"artifact": name, "exists": False, "age_h": None, "cutoff": None})
            continue
        age = (now - os.path.getmtime(path)) / 3600.0
        cutoff = None
        try:
            with open(path, encoding="utf-8") as fh:
                doc = json.load(fh)
            if isinstance(doc, dict):
                for key in ("evidence_cutoff", "session", "nav_date", "base_bar", "asof"):
                    if isinstance(doc.get(key), (str, int, float)):
                        cutoff = doc[key]
                        break
        except Exception:
            cutoff = None
        rows.append({"artifact": name, "exists": True, "age_h": round(age, 1),
                     "cutoff": cutoff})
    rows.sort(key=lambda r: (r["age_h"] is None, -(r["age_h"] or 0)))
    return rows


def _source(script):
    path = os.path.join(ROOT, script)
    if not os.path.exists(path):
        return ""
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def classify(finding, src):
    """WRITER_MODE_EXISTS_NOT_ON_CHAIN (red) vs NO_WRITER_MODE (derived face, disclosed)."""
    modes = scan_modes(src)
    if modes["bare_writes"] or modes["writer_modes"]:
        verdict = "WRITER_MODE_EXISTS_NOT_ON_CHAIN"
    else:
        verdict = "NO_WRITER_MODE"
    return dict(finding, verdict=verdict, modes=modes, artifacts=artifact_names(src))


def load_entries(chain_path=CHAIN):
    with open(chain_path, encoding="utf-8") as fh:
        src = fh.read()
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "LEGS"
                                                for t in node.targets):
            return ast.literal_eval(node.value)
    raise SystemExit("LEGS not found in %s" % chain_path)


def run(out_path=OUT, chain_path=CHAIN, results_dir=None, now=None):
    global RESULTS
    if results_dir is not None:
        RESULTS = results_dir
    report = audit(load_entries(chain_path))
    for finding in report["findings"]:
        finding.update(classify(finding, _source(finding["script"])))
        finding["artifacts"] = artifact_ages(finding["artifacts"], now=now, existing_only=True)
    red = [f for f in report["findings"]
           if f["verdict"] == "WRITER_MODE_EXISTS_NOT_ON_CHAIN"]
    report.update({
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "chain": os.path.relpath(chain_path, ROOT),
        "red": len(red),
        "disclosed": len(report["findings"]) - len(red),
        # The debt the tree already carries, by face key (red AND disclosed: both are faces no
        # leg regenerates; they differ only in whether a writer exists to hang). The gate below
        # fails on a face that is NOT in this list -- a permanently red census teaches readers to
        # skip it (E318 family), and re-wiring 30 research decision faces in one round is not a
        # round.
        "known": sorted("%s %s" % (f["script"], " ".join(f["scope"]))
                        for f in report["findings"]),
        "verdict": "CHECK_WITHOUT_WRITER" if red else "EVERY_CHECKED_FACE_HAS_A_WRITER",
    })
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    return report


def check(out_path=OUT, chain_path=CHAIN):
    """Re-derive the census and fail only on debt that is NEW since the published face.

    A face that moved from red to paired is reported as FIXED (the baseline can be pruned next
    time the tool runs); a face that is red and not in the baseline is rc1 -- that is the 29th
    copy arriving. Nothing here reads the clock: the question is structural.
    """
    if not os.path.exists(out_path):
        print("check: no published face at %s" % out_path)
        return 1
    with open(out_path, encoding="utf-8") as fh:
        published = json.load(fh)
    fresh = audit(load_entries(chain_path))
    if fresh["legs"] != published.get("legs"):
        print("check: chain has %d legs, face says %s -- rerun the tool"
              % (fresh["legs"], published.get("legs")))
        return 1
    known = set(published.get("known", []))
    fresh_keys = {"%s %s" % (f["script"], " ".join(f["scope"])): f for f in fresh["findings"]}
    new = sorted(set(fresh_keys) - known)
    fixed = sorted(known - set(fresh_keys))
    for key in new:
        verdict = classify(fresh_keys[key], _source(fresh_keys[key]["script"]))["verdict"]
        print("NEW %s %s legs=%s" % (verdict, key, ",".join(fresh_keys[key]["legs"])))
    for key in fixed:
        print("FIXED %s (a writer leg now exists; rerun to prune the baseline)" % key)
    if new:
        print("check: %d check-only face(s) nobody on the chain regenerates, not in the baseline"
              % len(new))
        return 1
    print("check: %d faces checked, %d known check-only, %d newly paired"
          % (len(fresh_keys), len(set(fresh_keys) & known), len(fixed)))
    return 0


def selftest():
    failures = []

    def leg(name, ok, extra=""):
        print(("PASS " if ok else "FAIL ") + name + ((" " + extra) if not ok else ""))
        if not ok:
            failures.append(name)

    # 1. a check-only leg with no writer is a finding
    rep = audit([("a", ["python", "scripts/a.py", "check"])])
    leg("check without writer is a finding",
        bool(rep["findings"]) and rep["findings"][0]["script"] == "scripts/a.py")

    # 2. the r1618 three-element form pairs the check with its writer
    rep = audit([("s", ["python", "scripts/a.py", "check"],
                  ["python", "scripts/a.py", "run"])])
    leg("third element counts as the writer", not rep["findings"] and rep["pairs"] == 1)

    # 3. the writer-mode token is the role, not the scope (the first draft's 84 false reds)
    rep = audit([("w", ["python", "scripts/a.py", "run"]),
                 ("c", ["python", "scripts/a.py", "check"])])
    leg("run+check on one script pair up", not rep["findings"])

    # 4. a bare invocation is a writer, and it pairs with `check`
    rep = audit([("bare", ["python", "scripts/a.py"]),
                 ("chk", ["python", "scripts/a.py", "check"])])
    leg("bare invocation is a writer for check", not rep["findings"])

    # 5. --floor-check is the same scope as --floor
    rep = audit([("f1", ["python", "scripts/a.py", "--floor-check"]),
                 ("f2", ["python", "scripts/a.py", "--floor"])])
    leg("a -check flag shares its base flag's scope", not rep["findings"])

    # 6. different scopes are not a pair (blocks/voltail on one script)
    rep = audit([("b", ["python", "scripts/a.py", "blocks", "--check"]),
                 ("v", ["python", "scripts/a.py", "voltail"])])
    leg("differing scopes do not pair", len(rep["findings"]) == 1)

    # 7. selftest is a reader, not a writer
    rep = audit([("s", ["python", "scripts/a.py", "selftest"])])
    leg("selftest counts as a reader", len(rep["findings"]) == 1)

    # 8. writer-mode detection decides red vs disclosed
    writer_src = ("def main(argv):\n"
                  "    if len(argv) > 1 and argv[1] == 'check':\n        return check()\n"
                  "    out = os.path.join(E.PATHS.results_dir, 'a.json')\n    return run(out)\n"
                  "def run(out):\n    pass\n")
    reader_src = "def main(argv):\n    return check()\n\ndef check():\n    pass\n"
    leg("a script that can run() is a red", classify({}, writer_src)["verdict"]
        == "WRITER_MODE_EXISTS_NOT_ON_CHAIN")
    leg("a script that only checks is disclosed", classify({}, reader_src)["verdict"]
        == "NO_WRITER_MODE")

    # 9. artifacts: json literals, underscore captures excluded
    leg("artifact names skip scratch captures",
        artifact_names("open(os.path.join(d,'a.json')); x='_tmp.json'") == ("a.json",))

    # 10. a missing artifact is not an age of zero (r1261 family)
    rows = artifact_ages(("definitely_not_a_face_12345.json",), now=time.time())
    leg("missing artifact reports None, not 0h",
        rows[0]["exists"] is False and rows[0]["age_h"] is None)

    # 11. display order: the stalest existing face first (that is the one worth reading)
    oldest = artifact_ages(("chain_writer_audit.json", "etf_book_order.json"), now=time.time())
    exist = [r["age_h"] for r in oldest if r["exists"]]
    leg("existing artifacts are ordered oldest first", exist == sorted(exist, reverse=True))

    total = 11
    print("selftest %d/%d" % (total - len(failures), total))
    return 0 if not failures else 1

    # 9. a missing artifact is not an age of zero (r1261 family: an empty reading is not a good one)
    rows = artifact_ages(("definitely_not_a_face_12345.json",), now=time.time())
    leg("missing artifact reports None, not 0h", rows[0]["exists"] is False
        and rows[0]["age_h"] is None)

    total = 9 + 0
    print("selftest %d/%d" % (total - len(failures), total))
    return 0 if not failures else 1


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv[1:])
    if args.selftest:
        return selftest()
    if args.check:
        return check()
    report = run()
    print("%-46s %s" % ("verdict", report["verdict"]))
    print("%-46s %d legs (%d paired check+write)" % ("chain", report["legs"], report["pairs"]))
    print("%-46s %d faces checked, %d have a writer leg"
          % ("faces", report["reader_faces"], report["paired"]))
    print("%-46s %d red, %d disclosed" % ("check-only", report["red"], report["disclosed"]))
    for f in report["findings"]:
        arts = ", ".join("%s %s" % (a["artifact"],
                                    ("%sh" % a["age_h"]) if a["exists"] else "MISSING")
                         for a in f["artifacts"][:3])
        print("%-18s %-52s %s" % (f["verdict"], f["script"] + (
            " " + " ".join(f["scope"]) if f["scope"] else ""), arts))
    print("wrote", os.path.relpath(OUT, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
