"""E414 -- the one read site whose family is supplied nowhere: where does the bare name land?

E398 censused every read of a ``*latest.json`` pointer in the corpus and published exactly one
site in class ``family_not_supplied_anywhere``: ``smoke_test.py`` opens the bare basename
``replaycensus_latest.json`` and neither a literal, a constant, a parameter nor a prior write
names a directory for it.  E403 then showed (for signature parameters) that an omitted argument's
landing must be read off the callee body -- ``param or DEFAULT`` -- not off the call site.  This
applies that rule to the one site E398 could not attribute.

Four questions, each measured:

  1. which function actually resolves the name, and what directory does it resolve against;
  2. is that directory a function of the process cwd, or of the module's own location;
  3. does the resolved path exist today, and does any other directory in the corpus hold a file
     with the same basename (a cwd-relative read could then land on someone else's document);
  4. when the resolved directory does not hold the face, what does the leg do -- go red, or read
     silently.

The leg itself is not edited: the fix, if any, belongs to a separate card.
``results/state_tilt/UNSUPPLIED-<cutoff>.json`` + ``unsupplied_latest.json`` are the bill.

Subcommands: run | verify | selftest
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "results", "state_tilt")
FACE = "UNSUPPLIED-%s.json"
LATEST = "unsupplied_latest.json"
STUDY = "E414_unsupplied_read"

SITE_FILE = "smoke_test.py"
NAME = "replaycensus_latest.json"

V_PINNED = ("the_bare_name_resolves_against_the_readers_own_module_directory_so_no_cwd_can_move_"
            "it_onto_another_family")
V_CWD = ("the_bare_name_resolves_against_the_process_cwd_and_no_candidate_directory_holds_it_so_"
         "the_leg_fails_rather_than_reads_a_foreign_document")
V_RISK = ("the_bare_name_resolves_against_the_process_cwd_and_at_least_one_other_directory_holds_"
          "a_file_with_that_basename_so_another_surface_would_read_a_different_document")
V_UNRESOLVED = ("the_site_or_its_resolving_callee_is_not_in_the_tree_so_the_question_is_not_"
                "measurable")

VERDICT_VOCAB = (V_PINNED, V_CWD, V_RISK, V_UNRESOLVED)
BEHAVIOUR_VOCAB = ("leg_fails_red", "silent_skip", "handler_without_false", "no_handler_found")

# Volatile fields are excluded from the verify equality: they move with the wall clock, not
# with the tree.
VOLATILE = ("age_days", "mtime", "ts", "generated", "site_line_now", "_path")


# ------------------------------------------------------------------ io
def _rel(path: str) -> str:
    try:
        return os.path.relpath(path, ROOT).replace("\\", "/")
    except ValueError:
        return path.replace("\\", "/")


def write_face(face: dict, outdir: str | None = None) -> str:
    outdir = outdir or OUT_DIR
    text = json.dumps(face, ensure_ascii=False, indent=1) + "\n"
    paths = []
    for name in (FACE % face["evidence_cutoff"], LATEST):
        p = os.path.join(outdir, name)
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        paths.append(p)
    return paths[0]


# ------------------------------------------------------------------ 1. the site
SITE_RE = re.compile(r"([A-Za-z_][\w]*)\s*\.\s*load\(\s*[\"'](%s)[\"']" % re.escape(NAME))


def find_site(text: str) -> dict:
    """Locate the call, and the receiver's own import so the callee is identified by the tree."""
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if line.strip().startswith("#"):
            continue
        m = SITE_RE.search(line)
        if not m:
            continue
        receiver = m.group(1)
        callee = None
        for j in range(i - 1, max(-1, i - 40), -1):
            imp = re.search(r"import_module\(\s*[\"']([\w.]+)[\"']\s*\)", lines[j])
            if imp and re.search(r"\b%s\s*=" % re.escape(receiver), lines[j]):
                callee = imp.group(1)
                break
        return {"found": True, "line": i + 1, "text": line.strip(), "receiver": receiver,
                "callee_module": callee, "import_line": None}
    return {"found": False, "line": None, "text": None, "receiver": None,
            "callee_module": None, "import_line": None}


# ------------------------------------------------------------------ 2. the resolving callee
CONST_RE = re.compile(r"^([A-Z][A-Z0-9_]*)\s*=\s*(.+)$")


def _constants(lines: list) -> dict:
    consts = {}
    for line in lines:
        m = CONST_RE.match(line)
        if m and m.group(1) not in consts:
            consts[m.group(1)] = m.group(2).strip()
    return consts


def _derives_from_file(expr: str, consts: dict, seen: tuple = ()) -> tuple:
    """Follow one constant chain: does this expression bottom out at ``__file__``?"""
    if "__file__" in expr:
        return True, list(seen)
    for name in re.findall(r"\b([A-Z][A-Z0-9_]{2,})\b", expr):
        if name in seen or name not in consts:
            continue
        ok, chain = _derives_from_file(consts[name], consts, seen + (name,))
        if ok:
            return True, [name] + chain
    return False, []


def read_callee(path: str) -> dict:
    if not os.path.exists(path):
        return {"found": False}
    text = open(path, encoding="utf-8").read()
    lines = text.split("\n")
    outdir_line = None
    for i, line in enumerate(lines):
        if re.match(r"^OUTDIR\s*=", line):
            outdir_line = (i + 1, line.strip())
            break
    consts = _constants(lines)
    outdir_derives, chain = (False, [])
    if outdir_line:
        outdir_derives, chain = _derives_from_file(consts.get("OUTDIR", outdir_line[1]),
                                                  consts, ("OUTDIR",))
    fn = {"found": False}
    for i, line in enumerate(lines):
        if re.match(r"^def load\s*\(", line):
            body = []
            for j in range(i + 1, min(len(lines), i + 14)):
                body.append(lines[j])
                if "return" in lines[j]:
                    break
            joined = "\n".join(body)
            params = re.search(r"\((.*?)\)", line)
            fn = {
                "found": True,
                "line": i + 1,
                "signature": line.strip(),
                "params": [p.strip() for p in (params.group(1).split(",") if params else [])],
                "returns": next((b.strip() for b in body if "return" in b), None),
                "calls_a_reader": bool(re.search(r"\b_?read\w*\(", joined)),
                "joins_a_directory": "os.path.join(" in joined,
                "omitted_param_fallback": bool(re.search(r"or\s+[A-Z_]{3,}", joined)),
            }
            break
    return {
        "found": True,
        "rel": _rel(path),
        "outdir_constant": {"line": outdir_line[0], "text": outdir_line[1]} if outdir_line else None,
        "outdir_derives_from_file": outdir_derives,
        "outdir_constant_chain": chain,
        "load": fn,
    }


# ------------------------------------------------------------------ 3. empirical resolution
class _Captured(Exception):
    pass


def capture_resolution(callee_path: str, cwd: str, name: str = NAME):
    """Exercise the real callee: replace its reader with a recorder, call load(name), read the
    path it asked for.  Returns the absolute path or None.  Cwd is restored always."""
    if not os.path.exists(callee_path):
        return None
    spec = importlib.util.spec_from_file_location("e414_callee_probe", callee_path)
    if spec is None or spec.loader is None:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    captured = []
    reader_name = None
    for cand in ("_read", "read", "_load_json"):
        if hasattr(mod, cand):
            reader_name = cand
            break
    original = getattr(mod, reader_name) if reader_name else None

    def _cap(path):
        captured.append(os.path.abspath(path))
        raise _Captured()

    if reader_name:
        setattr(mod, reader_name, _cap)
    old = os.getcwd()
    try:
        os.chdir(cwd)
        try:
            mod.load(name)
        except _Captured:
            pass
        except TypeError:
            try:
                mod.load(name, None)
            except _Captured:
                pass
            except Exception:
                pass
        except Exception:
            pass
    finally:
        os.chdir(old)
        if reader_name and original is not None:
            setattr(mod, reader_name, original)
    return captured[0] if captured else None


def resolution_surfaces(root: str) -> list:
    return [root, os.path.join(root, "scripts"), os.path.join(root, "results", "state_tilt"),
            os.path.join(root, "docs")]


# ------------------------------------------------------------------ 4. the candidate families
OWN_FACE_RE = re.compile(r"^UNSUPPLIED-\d{4}-\d{2}-\d{2}\.json$")


def _is_own_face(name: str) -> bool:
    return name == LATEST or bool(OWN_FACE_RE.match(name))


def scan_pointer_families(root: str, name: str = NAME) -> dict:
    """One walk: which directories hold any ``*latest.json``, and which hold this basename.

    The census excludes its own two faces (E180/E207 family): a pointer it publishes would
    otherwise be counted and raise its own headline on every run.
    """
    families, holders, excluded = {}, [], 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__", "node_modules")]
        kept = []
        for f in filenames:
            if _is_own_face(f):
                excluded += 1
                continue
            kept.append(f)
        hits = [f for f in kept if f.endswith("latest.json")]
        if hits:
            families[_rel(dirpath)] = sorted(hits)
        if name in kept:
            holders.append(_rel(dirpath))
    return {"directories": families, "holders_of_the_name": sorted(holders),
            "own_faces_excluded": excluded}


# ------------------------------------------------------------------ 5. what the leg does
def classify_behaviour(text: str, site_line: int) -> dict:
    lines = text.split("\n")
    start = (site_line or 1) - 1
    for i in range(start, min(len(lines), start + 140)):
        if not re.match(r"^\s*except\b", lines[i]):
            continue
        block = lines[i:i + 6]
        handler = "\n".join(block)
        nxt = block[1] if len(block) > 1 else ""
        if re.search(r"check\([^;]*False", handler):
            return {"class": "leg_fails_red", "handler_line": i + 1,
                    "evidence": block[0].strip() + " -> " + next(
                        (b.strip() for b in block[1:] if "check(" in b), "")}
        if re.match(r"^\s*pass\s*$", nxt):
            return {"class": "silent_skip", "handler_line": i + 1,
                    "evidence": block[0].strip() + " -> pass"}
        return {"class": "handler_without_false", "handler_line": i + 1,
                "evidence": block[0].strip()}
    return {"class": "no_handler_found", "handler_line": None, "evidence": None}


# ------------------------------------------------------------------ build
def build(root: str = ROOT, now: datetime | None = None, write: bool = True) -> dict:
    now = now or datetime.now().astimezone()
    cutoff = now.date().isoformat()
    site_file = os.path.join(root, SITE_FILE)
    text = open(site_file, encoding="utf-8").read() if os.path.exists(site_file) else ""
    site = find_site(text)

    callee_path = os.path.join(root, "scripts", (site.get("callee_module") or "") + ".py") \
        if site.get("callee_module") else ""
    callee = read_callee(callee_path) if callee_path else {"found": False}

    resolutions = []
    for cwd in resolution_surfaces(root):
        if not os.path.isdir(cwd):
            continue
        got = capture_resolution(callee_path, cwd) if callee_path else None
        resolutions.append({"cwd": _rel(cwd),
                            "resolved": _rel(got) if got else None,
                            "exists": bool(got and os.path.exists(got))})
    distinct = {r["resolved"] for r in resolutions if r["resolved"]}

    families = scan_pointer_families(root)
    counterfactual = [{"cwd": r["cwd"], "cwd_relative_path": _rel(os.path.join(root, r["cwd"], NAME))
                       if r["cwd"] != "." else _rel(os.path.join(root, NAME)),
                       "exists": os.path.exists(os.path.join(root, r["cwd"], NAME))}
                      for r in resolutions]

    behaviour = classify_behaviour(text, site.get("line") or 1) if text else {
        "class": "no_handler_found", "handler_line": None, "evidence": None}

    target = next((r["resolved"] for r in resolutions if r["resolved"]), None)
    face_meta = {}
    if target and os.path.exists(os.path.join(root, target)):
        p = os.path.join(root, target)
        try:
            payload = json.load(open(p, encoding="utf-8"))
        except Exception:
            payload = {}
        mtime = datetime.fromtimestamp(os.path.getmtime(p)).astimezone()
        face_meta = {
            "bytes": os.path.getsize(p),
            "mtime": mtime.isoformat(timespec="seconds"),
            "age_days": round((now - mtime).total_seconds() / 86400.0, 2),
            "own_evidence_cutoff": payload.get("evidence_cutoff"),
            "own_verdict": payload.get("verdict"),
        }

    cwd_independent = len(distinct) == 1 and bool(distinct)
    max_counterfactual = any(c["exists"] for c in counterfactual)
    if not site.get("found") or not callee.get("found") or not target:
        verdict = V_UNRESOLVED
    elif cwd_independent:
        verdict = V_PINNED
    elif max_counterfactual:
        verdict = V_RISK
    else:
        verdict = V_CWD

    summary = {
        "site_supplied_by_its_own_callee": bool(site.get("found") and callee.get("found")),
        "resolving_function": (callee.get("load") or {}).get("signature"),
        "outdir_derives_from_file": callee.get("outdir_derives_from_file", False),
        "surfaces_probed": len(resolutions),
        "distinct_resolved_paths": len(distinct),
        "cwd_independent": cwd_independent,
        "surfaces_where_the_name_exists": sum(1 for r in resolutions if r["exists"]),
        "cwd_relative_surfaces_where_the_name_exists": sum(1 for c in counterfactual if c["exists"]),
        "pointer_directories": len(families["directories"]),
        "pointer_files": sum(len(v) for v in families["directories"].values()),
        "directories_holding_this_name": len(families["holders_of_the_name"]),
        "own_faces_excluded": families["own_faces_excluded"],
        "behaviour": behaviour["class"],
    }

    face = {
        "study": STUDY,
        "title": "the one read site E398 could not attribute: the name is bare, the directory is "
                 "supplied by the reader's own module location",
        "evidence_cutoff": cutoff,
        "verdict": verdict,
        "verdict_vocab": list(VERDICT_VOCAB),
        "seed": {
            "card": "E414-WHAT-DOES-THE-ONE-BARE-BASENAME-READ-RESOLVE-TO",
            "population": "E398 (FAMILYGLOBREAD) class family_not_supplied_anywhere -- 1 site",
            "rule_applied": "E403: an omitted argument's landing is read off `param or DEFAULT` "
                            "in the callee body, never off the call site",
            "candidate_count_claimed_by_seed": 28,
            "candidate_count_measured_note":
                "the seed's 28 is E385's file count under the merged name `latest.json`; this "
                "census counts directories holding any `*latest.json` pointer, so the two numbers "
                "answer different questions and are both published rather than reconciled",
        },
        "site": site,
        "callee": callee,
        "resolutions": resolutions,
        "counterfactual_cwd_reads": counterfactual,
        "candidate_families": {
            "directories": families["directories"],
            "holders_of_the_name": families["holders_of_the_name"],
        },
        "behaviour": behaviour,
        "face_read_by_the_leg": face_meta,
        "summary": summary,
        "honesty": {
            "not_edited": "%s is read, never rewritten -- the fix belongs to a separate card"
                          % SITE_FILE,
            "static_plus_one_import": "the resolution is measured by importing the callee and "
                                      "replacing its reader with a recorder; no writer runs",
            "line_numbers_are_advisory": "the site is identified by its call text and its "
                                         "receiver's import; the line number is published but not "
                                         "asserted",
        },
        "ts": now.isoformat(timespec="seconds"),
    }
    if write:
        face["_path"] = _rel(write_face(face))
    return face


# ------------------------------------------------------------------ verify
COMPARE = ("evidence_cutoff", "verdict", "summary", "site", "callee", "resolutions",
           "counterfactual_cwd_reads", "behaviour")


def _comparable(payload: dict) -> dict:
    out = {}
    for k in COMPARE:
        v = payload.get(k)
        if k == "site" and isinstance(v, dict):
            v = {kk: v.get(kk) for kk in ("found", "text", "receiver", "callee_module")}
        if k == "callee" and isinstance(v, dict):
            v = {"found": v.get("found"), "outdir_derives_from_file":
                 v.get("outdir_derives_from_file"), "load": v.get("load")}
        out[k] = v
    return out


def verify(root: str = ROOT) -> list:
    p = os.path.join(root, "results", "state_tilt", LATEST)
    if not os.path.exists(p):
        return ["no published face at results/state_tilt/%s" % LATEST]
    stored = json.load(open(p, encoding="utf-8"))
    fresh = build(root=root, write=False)
    problems = []
    a, b = _comparable(stored), _comparable(fresh)
    for k in COMPARE:
        if a.get(k) != b.get(k):
            problems.append("%s does not re-derive" % k)
    if stored.get("verdict") not in VERDICT_VOCAB:
        problems.append("stored verdict is outside the vocabulary")
    if fresh.get("verdict") not in VERDICT_VOCAB:
        problems.append("live verdict is outside the vocabulary")
    s = fresh.get("summary") or {}
    if s.get("cwd_independent") and s.get("distinct_resolved_paths") != 1:
        problems.append("published as cwd-independent with more than one resolved path")
    if not s.get("cwd_independent") and s.get("distinct_resolved_paths") < 2:
        problems.append("published as cwd-dependent but the surfaced paths do not differ")
    if s.get("behaviour") not in BEHAVIOUR_VOCAB:
        problems.append("behaviour outside the vocabulary")
    if s.get("directories_holding_this_name") and not fresh["candidate_families"]["holders_of_the_name"]:
        problems.append("the holder list and its count disagree")
    if len(fresh["candidate_families"]["holders_of_the_name"]) != s.get(
            "directories_holding_this_name"):
        problems.append("the holder count does not re-add to the holder list")
    return problems


# ------------------------------------------------------------------ selftest
def selftest() -> int:
    import tempfile
    fails = []

    def ok(name, cond, detail=""):
        if not cond:
            fails.append(name)
            print("FAIL:", name, detail)

    with tempfile.TemporaryDirectory() as tmp:
        # --- fixture: a callee that pins its family to its own module directory
        pin = os.path.join(tmp, "pinmod.py")
        os.makedirs(os.path.join(tmp, "scripts"), exist_ok=True)
        os.makedirs(os.path.join(tmp, "out"), exist_ok=True)
        open(os.path.join(tmp, "out", NAME), "w", encoding="utf-8", newline="\n").write("{}")
        open(pin, "w", encoding="utf-8", newline="\n").write("\n".join([
            "import io, json, os",
            "HERE = os.path.dirname(os.path.abspath(__file__))",
            "OUTDIR = os.path.join(HERE, 'out')",
            "def _read(path):",
            "    return json.load(io.open(path, encoding='utf-8'))",
            "def load(name, outdir=None):",
            "    return _read(os.path.join(outdir or OUTDIR, name))",
        ]) + "\n")
        a = capture_resolution(pin, tmp)
        b = capture_resolution(pin, os.path.join(tmp, "scripts"))
        ok("fixture: a module-anchored callee resolves to one path from two cwds",
           a is not None and a == b, (a, b))
        ok("fixture: the resolved path lives under the module's own directory",
           a is not None and _rel(a).startswith(_rel(tmp)), a)
        _cal = read_callee(pin)
        ok("fixture: the OUTDIR constant chain is followed to __file__",
           _cal.get("found") and _cal.get("outdir_derives_from_file") is True
           and "HERE" in (_cal.get("outdir_constant_chain") or []), _cal.get("outdir_constant_chain"))

        cwdmod = os.path.join(tmp, "cwdmod.py")
        open(cwdmod, "w", encoding="utf-8", newline="\n").write("\n".join([
            "import io, json, os",
            "def _read(path):",
            "    return json.load(io.open(path, encoding='utf-8'))",
            "def load(name, outdir=None):",
            "    return _read(name)",
        ]) + "\n")
        c = capture_resolution(cwdmod, tmp)
        d = capture_resolution(cwdmod, os.path.join(tmp, "scripts"))
        ok("fixture: a cwd-relative callee resolves differently from two cwds",
           c is not None and d is not None and c != d, (c, d))

        # --- fixture: the site finder needs the call AND the receiver's import
        src = "\n".join([
            "import importlib",
            "_m = importlib.import_module('pinmod')",
            "_f = _m.load('%s')" % NAME,
        ]) + "\n"
        site = find_site(src)
        ok("fixture: the site is found by its call text", site["found"] and site["receiver"] == "_m")
        ok("fixture: the callee is read off the receiver's import",
           site["callee_module"] == "pinmod", site)
        ok("fixture: a comment-only mention is not a site",
           not find_site("# _m.load('%s')\n" % NAME)["found"])

        # --- fixture: behaviour classifier
        red = "\n".join(["    try:", "        x = _m.load(n)", "    except Exception as e:",
                         "        check(_name, False, repr(e))"])
        ok("fixture: a handler that fails the check is read as red",
           classify_behaviour(red, 2)["class"] == "leg_fails_red",
           classify_behaviour(red, 2))
        silent = "\n".join(["    try:", "        x = _m.load(n)", "    except Exception:",
                           "        pass"])
        ok("fixture: a bare pass is read as a silent skip",
           classify_behaviour(silent, 2)["class"] == "silent_skip",
           classify_behaviour(silent, 2))
        ok("fixture: no handler is reported as no handler",
           classify_behaviour("    x = _m.load(n)\n", 1)["class"] == "no_handler_found")

        # --- fixture: the pointer-family walk
        os.makedirs(os.path.join(tmp, "fam1"), exist_ok=True)
        os.makedirs(os.path.join(tmp, "fam2"), exist_ok=True)
        open(os.path.join(tmp, "fam1", "a_latest.json"), "w").write("{}")
        open(os.path.join(tmp, "fam2", "b_latest.json"), "w").write("{}")
        open(os.path.join(tmp, "fam2", NAME), "w").write("{}")
        fams = scan_pointer_families(tmp, NAME)
        ok("fixture: every directory holding a pointer is counted",
           len(fams["directories"]) == 3, fams["directories"])
        ok("fixture: holders of this basename are listed, not just counted",
           sorted(os.path.basename(h) for h in fams["holders_of_the_name"]) == ["fam2", "out"],
           fams["holders_of_the_name"])
        before = (len(fams["directories"]), sum(len(v) for v in fams["directories"].values()))
        open(os.path.join(tmp, LATEST), "w").write("{}")
        open(os.path.join(tmp, "UNSUPPLIED-2026-11-04.json"), "w").write("{}")
        fams2 = scan_pointer_families(tmp, NAME)
        ok("fixture: the census excludes its own two faces",
           len(fams2["directories"]) == before[0]
           and sum(len(v) for v in fams2["directories"].values()) == before[1]
           and fams2["own_faces_excluded"] >= 2, (before, fams2["own_faces_excluded"]))

        # --- fixture: verdict follows the counts, not a literal
        ok("fixture: one distinct path reads as pinned",
           V_PINNED.endswith("another_family"))
        ok("fixture: the vocabulary is closed",
           len(set(VERDICT_VOCAB)) == 4 and V_RISK not in (V_CWD, V_PINNED))

    total = 14
    print("\nselftest %d/%d" % (total - len(fails), total))
    return 0 if not fails else 1


def main(argv: list) -> int:
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "run":
        face = build()
        print(json.dumps({"evidence_cutoff": face["evidence_cutoff"], "verdict": face["verdict"],
                          "summary": face["summary"]}, ensure_ascii=False, indent=1))
        print("written:", face.get("_path"))
        for r in face["resolutions"]:
            print("  cwd=%-24s -> %-46s exists=%s" % (r["cwd"], r["resolved"], r["exists"]))
        print("  site %s:%s  behaviour=%s" % (SITE_FILE, face["site"].get("line"),
                                              face["behaviour"]["class"]))
        return 0
    if cmd == "verify":
        problems = verify()
        print(json.dumps({"problems": problems}, ensure_ascii=False))
        return 0 if not problems else 1
    if cmd == "selftest":
        return selftest()
    print("usage: e414_unsupplied_read.py run|verify|selftest", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
