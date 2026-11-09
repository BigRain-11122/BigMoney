"""E611 -- does a glob that names a face ever run again?

E609 (r1634) published 82 faces that no literal opens, and priced how a glob reaches them: only 6
of the 82 are reached by a pattern that names their own directory, and the lane note E609 seeded
said the rest of the question out loud -- a landing that never runs again costs nothing.  This
study prices the runner, not the pattern.

The population is machine-read from E609's own face: every face graded ``names_the_directory`` and
the sites on it whose ``named_dir_depth`` reaches the face's full directory list.  Those sites'
``source`` files are the landing modules.  Each module is then asked one question, statically, with
no runner started and nothing rebuilt: is its path named by

  NAMED_BY_A_SCHEDULED_TASK   a PowerShell/cmd file that registers or runs a scheduled task
  NAMED_BY_A_LIVE_CHAIN       a per-round chain runner (Tools/s6_chain_*.py)
  NAMED_BY_A_SMOKE_LEG        smoke_test.py or a script that extracts one of its legs
  NAMED_BY_NOTHING            no entry point names it -- a one-off round script, or a file nobody
                              ever calls again

Priority is scheduled > chain > smoke: a module that a task runs is reachable whether or not a
smoke leg also names it.  For every face the answer is joined back: a face's own-directory sweepers
are re-running only when at least one of them is named by an entry point, so a face whose sweepers
are all NAMED_BY_NOTHING is a landing that will not happen again.

Run:      python scripts/e611_sweep_reruns.py run
Verify:   python scripts/e611_sweep_reruns.py verify
Check:    python scripts/e611_sweep_reruns.py check
Selftest: python scripts/e611_sweep_reruns.py selftest
"""

import argparse
import io
import json
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import e451_prereg_digest as e451                                      # noqa: E402  (read_text)
import e609_glob_reach as e609                                         # noqa: E402  (segments)

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
SELF_STEM = "SWEEPRERUNS"
OUT_PATH = os.path.join(OUTDIR, SELF_STEM + ".json")
E609_FACE = ("results", "state_tilt", "GLOBSWEEPREACH.json")
MAX_READ_BYTES = 1 << 20
SITES_PER_MODULE = 6
SELF_SKIP = ("e611_", "run_e611", "e609_", "run_e609")

C_SCHED = "named_by_a_scheduled_task"
C_CHAIN = "named_by_a_live_chain"
C_SMOKE = "named_by_a_smoke_leg"
C_NONE = "named_by_nothing"
CLASSES = (C_SCHED, C_CHAIN, C_SMOKE, C_NONE)
PRIORITY = {C_SCHED: 3, C_CHAIN: 2, C_SMOKE: 1, C_NONE: 0}

K_SCHED = "scheduled_task"
K_CHAIN = "live_chain"
K_SMOKE = "smoke_leg"
KINDS = (K_SCHED, K_CHAIN, K_SMOKE)

SCHEDULER_MARKERS = ("schtasks", "Register-ScheduledTask", "New-ScheduledTaskAction")
ROUND_RE = re.compile(r"^_r(\d+)")

V_RERUNS = "every_face_whose_own_directory_a_sweep_names_has_a_sweeper_an_entry_point_runs_again"
V_ONE_OFF = "at_least_one_face_is_swept_only_by_modules_no_entry_point_names"
V_EMPTY = "the_population_is_empty"
VERDICT_VOCAB = (V_RERUNS, V_ONE_OFF, V_EMPTY)


# --------------------------------------------------------------------------- population
def _read_json(path):
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _rel(path, root):
    return os.path.relpath(path, root).replace(os.sep, "/")


def _own_dir_sites(face_rel, sites):
    """The sites on one face whose named depth reaches the face's own directory list."""
    total = len(e609.segments(face_rel)) - 1
    out = []
    for s in sites or []:
        if not s.get("naming_segments"):
            continue
        if int(s.get("named_dir_depth") or 0) >= total and total:
            out.append(s)
    return out


def population(root=None):
    """Faces E609 graded names_the_directory, with the sites that name their own directory."""
    root = root or ROOT
    face_path = os.path.join(root, *E609_FACE)
    if not os.path.exists(face_path):
        return [], "e609_face_absent"
    try:
        pub = _read_json(face_path)
    except (OSError, ValueError):
        return [], "e609_face_unreadable"
    out = []
    for rec in pub.get("faces") or []:
        if rec.get("class") != e609.C_FULL:
            continue
        rel = rec.get("face") or ""
        sites = _own_dir_sites(rel, rec.get("sites") or [])
        if not sites:
            continue
        out.append({"face": rel, "present": bool(rec.get("present")),
                    "disagreeing_series": rec.get("disagreeing_series"), "sites": sites})
    out.sort(key=lambda r: r["face"])
    return out, None


# --------------------------------------------------------------------------- entry corpora
def _text(root, rel):
    path = os.path.join(root, rel.replace("/", os.sep))
    try:
        if os.path.getsize(path) > MAX_READ_BYTES:
            return None
        return e451.read_text(path)
    except (OSError, ValueError):
        return None


def _iter_files(root, subdir, suffix):
    base = os.path.join(root, subdir) if subdir else root
    if not os.path.isdir(base):
        return []
    out = []
    for name in sorted(os.listdir(base)):
        path = os.path.join(base, name)
        if os.path.isfile(path) and name.endswith(suffix):
            out.append(_rel(path, root))
    return out


def entry_corpora(root=None):
    """Every file that can make a module run again, with the kind of entry point it is.

    One hop only: a chain runner counts as a live entry point (it is executed every round) and a
    smoke leg counts as a leg, but nothing here follows a pointer file into another script.
    """
    root = root or ROOT
    out = []

    smoke = _iter_files(root, "", "smoke_test.py")
    smoke += _iter_files(root, "scripts", ".py")
    smoke = [r for r in smoke if r == "smoke_test.py" or os.path.basename(r).startswith("run_e")]
    for rel in smoke:
        if not any(os.path.basename(rel).startswith(s) for s in SELF_SKIP):
            out.append({"source": rel, "kind": K_SMOKE})

    chain = [r for r in _iter_files(root, "Tools", ".py")
             if os.path.basename(r).startswith("s6_chain")
             or ("chain" in os.path.basename(r) and not os.path.basename(r).startswith("_r"))]
    for rel in chain:
        out.append({"source": rel, "kind": K_CHAIN})

    candidates = _iter_files(root, "Tools", ".ps1") + _iter_files(root, "Tools", ".cmd")
    candidates += _iter_files(root, "", ".ps1") + _iter_files(root, "", ".cmd")
    for rel in candidates:
        if any(os.path.basename(rel).startswith(s) for s in SELF_SKIP):
            continue
        text = _text(root, rel) or ""
        low = text.lower()
        if any(m.lower() in low for m in SCHEDULER_MARKERS):
            out.append({"source": rel, "kind": K_SCHED})
    return out


# --------------------------------------------------------------------------- build
def _modules_of(pop):
    """module relpath -> the faces whose own directory its site names (one entry per module)."""
    mods = {}
    for rec in pop:
        for s in rec["sites"]:
            src = s.get("source")
            if not src or not src.endswith(".py"):
                continue
            m = mods.setdefault(src, {"module": src, "faces": [], "patterns": []})
            if rec["face"] not in m["faces"]:
                m["faces"].append(rec["face"])
            pat = s.get("pattern")
            if pat and pat not in m["patterns"]:
                m["patterns"].append(pat)
    for m in mods.values():
        m["faces"].sort()
        m["patterns"].sort()
    return mods


def _classify(module_rel, corpus_texts, root):
    hits = []
    for rel, kind, text in corpus_texts:
        base = os.path.basename(module_rel)
        if base and base in text:
            hits.append({"source": rel, "kind": kind})
    if hits:
        cls = max((h["kind"] for h in hits), key=lambda k: 0)  # replaced below
        best = None
        for h in hits:
            cand = {K_SCHED: C_SCHED, K_CHAIN: C_CHAIN, K_SMOKE: C_SMOKE}[h["kind"]]
            if best is None or PRIORITY[cand] > PRIORITY[best]:
                best = cand
        cls = best
    else:
        cls = C_NONE
    base = os.path.basename(module_rel)
    m = ROUND_RE.match(base)
    return {
        "module": module_rel,
        "class": cls,
        "is_a_round_script": bool(m),
        "round_no": int(m.group(1)) if m else None,
        "on_checkout": os.path.exists(os.path.join(root, module_rel.replace("/", os.sep))),
        "named_by": sorted(hits, key=lambda h: (h["kind"], h["source"]))[:SITES_PER_MODULE],
        "named_by_count": len(hits),
    }


def build(root=None, write=False):
    root = root or ROOT
    pop, why = population(root)
    corpus = entry_corpora(root)
    corpus_texts = []
    for e in corpus:
        text = _text(root, e["source"])
        if text:
            corpus_texts.append((e["source"], e["kind"], text))

    mods = _modules_of(pop)
    module_rows = [_classify(rel, corpus_texts, root) for rel in sorted(mods)]
    by_module = {r["module"]: r for r in module_rows}

    faces = []
    for rec in pop:
        sweepers = sorted({s.get("source") for s in rec["sites"]
                           if s.get("source") and s.get("source").endswith(".py")})
        rows = [by_module[m] for m in sweepers if m in by_module]
        rerunning = [r["module"] for r in rows if r["class"] != C_NONE]
        faces.append({
            "face": rec["face"],
            "present": rec["present"],
            "disagreeing_series": rec["disagreeing_series"],
            "sweepers": sweepers,
            "sweepers_an_entry_point_runs_again": rerunning,
            "only_a_one_off": bool(rows) and not rerunning,
            "classes": sorted({r["class"] for r in rows}),
        })

    counts = {c: 0 for c in CLASSES}
    for r in module_rows:
        counts[r["class"]] += 1
    counts["modules"] = len(module_rows)
    counts["modules_on_checkout"] = sum(1 for r in module_rows if r["on_checkout"])
    counts["round_scripts"] = sum(1 for r in module_rows if r["is_a_round_script"])
    counts["round_scripts_nothing_names"] = sum(
        1 for r in module_rows if r["is_a_round_script"] and r["class"] == C_NONE)
    counts["modules_named_by_more_than_one_kind"] = sum(
        1 for r in module_rows if len({h["kind"] for h in r["named_by"]}) > 1)
    counts["faces"] = len(faces)
    counts["faces_with_only_a_one_off_sweeper"] = sum(1 for f in faces if f["only_a_one_off"])
    counts["faces_with_a_sweeper_an_entry_point_runs_again"] = sum(
        1 for f in faces if f["sweepers_an_entry_point_runs_again"])
    counts["entry_files"] = len(corpus)
    for k in KINDS:
        counts["entry_files_" + k] = sum(1 for e in corpus if e["kind"] == k)

    face = {
        "study": "E611_sweep_reruns",
        "card": "E611-WHETHER-A-GLOB-THAT-NAMES-A-FACE-EVER-RUNS-AGAIN",
        "evidence_cutoff": _cutoff(pop),
        "population_source": "results/state_tilt/GLOBSWEEPREACH.json (E609 faces graded "
                             "names_the_directory, own-directory sites only)",
        "population_note": why or "read from the published E609 face",
        "class_vocabulary": list(CLASSES),
        "entry_kind_vocabulary": list(KINDS),
        "counts": counts,
        "modules": module_rows,
        "faces": faces,
        "verdict": verdict_from(counts),
        "answer": answer_sentence(counts),
        "limits": [
            "one hop only: a module named by Tools/s6_chain_*.py is reachable because that chain "
            "runs every round, but nothing here follows a pointer from one script into another, "
            "so a module named only by a script that itself never runs is graded NAMED_BY_NOTHING",
            "reach is decided by the module's bare basename appearing in an entry file's text. A "
            "reference built from a composed string this scan does not resolve is published as a "
            "miss, not as a run",
            "an entry file is a scheduled-task definition only when it carries one of %r; a task "
            "registered from outside the repo cannot be seen here"
            % (SCHEDULER_MARKERS,),
            "a smoke leg counts as an entry point because it is executed whenever the suite runs, "
            "and the full suite is not run every round (r1499) -- the class says the leg exists, "
            "not that it ran this window",
            "the population is E609's published six faces. It is machine-read, so a stale E609 "
            "face would be graded as published; population_note says where it came from",
            "at most %d naming entry files per module are published; the count is complete even "
            "when the list is truncated" % SITES_PER_MODULE,
        ],
    }
    pr = face_problems(face)
    if write and not pr:
        write_face(face)
    return face, pr


def _cutoff(pop):
    best = ""
    for rec in pop:
        for m in re.finditer(r"(20\d\d-\d\d-\d\d)", rec["face"]):
            if m.group(1) > best:
                best = m.group(1)
    return best or "no-date-in-population"


def answer_sentence(counts):
    total = counts.get("faces") or 0
    if not total:
        return "the population is empty, so no landing is priced"
    return ("of %d faces whose own directory a glob names, %d carry at least one sweeper an entry "
            "point runs again and %d are swept only by modules nothing names (%d of %d landing "
            "modules are round scripts and %d of those are named by nothing at all)."
            % (total, counts.get("faces_with_a_sweeper_an_entry_point_runs_again", 0),
               counts.get("faces_with_only_a_one_off_sweeper", 0),
               counts.get("round_scripts", 0), counts.get("modules", 0),
               counts.get("round_scripts_nothing_names", 0)))


def verdict_from(counts):
    if not counts.get("faces"):
        return V_EMPTY
    if counts.get("faces_with_only_a_one_off_sweeper"):
        return V_ONE_OFF
    return V_RERUNS


def write_face(face):
    os.makedirs(OUTDIR, exist_ok=True)
    body = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    for path in (OUT_PATH, os.path.join(OUTDIR, SELF_STEM + "-latest.json")):
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body)


# --------------------------------------------------------------------------- guard
def face_problems(face):
    p = []
    if not isinstance(face, dict) or "counts" not in face:
        return ["the face carries no counts block"]
    counts = face["counts"]
    modules = face.get("modules") or []
    faces = face.get("faces") or []
    if not modules and counts.get("modules"):
        p.append("counts.modules says %r but the face publishes no module rows"
                 % counts.get("modules"))
    if not faces:
        p.append("the face publishes no faces")

    tally = {}
    by_module = {}
    for rec in modules:
        cls = rec.get("class")
        if cls not in CLASSES:
            p.append("module %s carries an unknown class %r" % (rec.get("module"), cls))
            break
        tally[cls] = tally.get(cls, 0) + 1
        by_module[rec.get("module")] = rec
        named = {h.get("kind") for h in rec.get("named_by") or []}
        if named - set(KINDS):
            p.append("module %s is named by an unknown entry kind %r"
                     % (rec.get("module"), sorted(named - set(KINDS))))
            break
        if cls == C_NONE and named:
            p.append("module %s grades NAMED_BY_NOTHING but publishes entry hits"
                     % rec.get("module"))
            break
        if cls != C_NONE:
            want = {K_SCHED: C_SCHED, K_CHAIN: C_CHAIN, K_SMOKE: C_SMOKE}
            best = max((want[k] for k in named), key=lambda c: PRIORITY[c], default=C_NONE)
            if best != cls:
                p.append("module %s grades %r but its entry hits say %r"
                         % (rec.get("module"), cls, best))
                break
        if rec.get("is_a_round_script") != bool(ROUND_RE.match(
                str(os.path.basename(rec.get("module") or "")))):
            p.append("module %s disagrees with the round-script rule" % rec.get("module"))
            break
    for c in CLASSES:
        if counts.get(c, 0) != tally.get(c, 0):
            p.append("counts.%s says %r but the rows say %d" % (c, counts.get(c), tally.get(c, 0)))
    if counts.get("modules") != len(modules):
        p.append("counts.modules says %r but the face publishes %d rows"
                 % (counts.get("modules"), len(modules)))

    for rec in faces:
        rows = [by_module[m] for m in rec.get("sweepers") or [] if m in by_module]
        rerunning = [r["module"] for r in rows if r["class"] != C_NONE]
        if rec.get("sweepers_an_entry_point_runs_again") != rerunning:
            p.append("face %s publishes re-running sweepers that do not re-derive from the modules"
                     % rec.get("face"))
            break
        if bool(rec.get("only_a_one_off")) != (bool(rows) and not rerunning):
            p.append("face %s publishes only_a_one_off that does not re-derive" % rec.get("face"))
            break
    if counts.get("faces") != len(faces):
        p.append("counts.faces says %r but the face publishes %d rows"
                 % (counts.get("faces"), len(faces)))
    if counts.get("faces_with_only_a_one_off_sweeper") != sum(
            1 for f in faces if f.get("only_a_one_off")):
        p.append("counts.faces_with_only_a_one_off_sweeper does not re-derive")
    if counts.get("faces_with_a_sweeper_an_entry_point_runs_again") != sum(
            1 for f in faces if f.get("sweepers_an_entry_point_runs_again")):
        p.append("counts.faces_with_a_sweeper_an_entry_point_runs_again does not re-derive")
    if counts.get("round_scripts") != sum(1 for r in modules if r.get("is_a_round_script")):
        p.append("counts.round_scripts does not re-derive")
    if face.get("verdict") != verdict_from(counts):
        p.append("verdict %r does not re-derive from the counts (rule says %r)"
                 % (face.get("verdict"), verdict_from(counts)))
    if not face.get("answer"):
        p.append("the face carries no answer sentence")
    return p


# --------------------------------------------------------------------------- selftest
def _fixture(files, faces):
    """Throw-away repo.  files = {relpath: text}; faces = {relpath: [own-directory site sources]}."""
    tmp = tempfile.mkdtemp(prefix="e611_")
    for rel, text in files.items():
        path = os.path.join(tmp, rel.replace("/", os.sep))
        os.makedirs(os.path.dirname(path) or tmp, exist_ok=True)
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
    rows = []
    for rel, sources in faces.items():
        path = os.path.join(tmp, rel.replace("/", os.sep))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("{}\n")
        dirs = e609.segments(rel)[:-1]
        rows.append({"face": rel, "present": True, "disagreeing_series": 1,
                     "class": e609.C_FULL,
                     "sites": [{"source": src, "line": 1,
                                "pattern": "/".join(dirs + ["*"]), "score": len(dirs),
                                "naming_segments": dirs, "named_dir_depth": len(dirs)}
                               for src in sources]})
    p = os.path.join(tmp, "results", "state_tilt", "GLOBSWEEPREACH.json")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"faces": rows}, fh)
    return tmp


def selftest():
    legs = []

    def leg(name, cond, note=""):
        legs.append({"leg": name, "ok": bool(cond), "note": note})

    # 1. a module only a smoke leg names
    tmp = _fixture({"smoke_test.py": "# runs results/_r100_scan.py\n",
                    "scripts/run_e611_smoke_leg.py": "# extract\n",
                    "results/_r100_scan.py": "",
                    "results/_r101_orphan.py": ""},
                   {"results/paper/A_paper.json": ["results/_r100_scan.py",
                                                   "results/_r101_orphan.py"]})
    try:
        face, pr = build(root=tmp, write=False)
        by = {m["module"]: m for m in face["modules"]}
        leg("smoke fixture builds a face", not pr, str(pr))
        leg("a module a smoke leg names is NAMED_BY_A_SMOKE_LEG",
            by["results/_r100_scan.py"]["class"] == C_SMOKE, str(by.get("results/_r100_scan.py")))
        leg("a module nothing names is NAMED_BY_NOTHING",
            by["results/_r101_orphan.py"]["class"] == C_NONE, str(by.get("results/_r101_orphan.py")))
        leg("the smoke leg file itself is in the corpus while this study's own leg is skipped",
            face["counts"]["entry_files_smoke_leg"] == 1, str(face["counts"]))
        leg("a face with one re-running sweeper is not only_a_one_off",
            face["faces"][0]["only_a_one_off"] is False, str(face["faces"][0]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 2. the three named kinds and one unnamed module side by side
    tmp = _fixture({
        "smoke_test.py": "# runs results/_r201_by_smoke.py\n",
        "Tools/s6_chain_bmb.py": 'LEGS = [["python", "results/_r202_by_chain.py"]]\n',
        "Tools/register_loop_task.ps1": 'schtasks /create /tn X /tr "python '
                                        'results/_r203_by_task.py"\n',
        "results/_r201_by_smoke.py": "",
        "results/_r202_by_chain.py": "",
        "results/_r203_by_task.py": "",
        "results/_r204_nobody.py": "",
    }, {"results/paper/B_paper.json": ["results/_r201_by_smoke.py", "results/_r202_by_chain.py",
                                       "results/_r203_by_task.py", "results/_r204_nobody.py"]})
    try:
        face, pr = build(root=tmp, write=False)
        by = {m["module"]: m for m in face["modules"]}
        leg("smoke-named module is NAMED_BY_A_SMOKE_LEG",
            by["results/_r201_by_smoke.py"]["class"] == C_SMOKE,
            str(by["results/_r201_by_smoke.py"]["class"]))
        leg("chain-named module is NAMED_BY_A_LIVE_CHAIN",
            by["results/_r202_by_chain.py"]["class"] == C_CHAIN,
            str(by["results/_r202_by_chain.py"]["class"]))
        leg("task-named module is NAMED_BY_A_SCHEDULED_TASK",
            by["results/_r203_by_task.py"]["class"] == C_SCHED,
            str(by["results/_r203_by_task.py"]["class"]))
        leg("unreferenced round script is NAMED_BY_NOTHING",
            by["results/_r204_nobody.py"]["class"] == C_NONE,
            str(by["results/_r204_nobody.py"]["class"]))
        leg("a round script is flagged as one with its number",
            by["results/_r204_nobody.py"]["is_a_round_script"] is True
            and by["results/_r204_nobody.py"]["round_no"] == 204,
            str(by["results/_r204_nobody.py"]))
        leg("verdict is RERUNS when the face has a re-running sweeper",
            face["verdict"] == V_RERUNS, face["verdict"])
        leg("guard accepts the mixed fixture", not pr, str(pr))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 3. a face whose only sweeper is a one-off -> verdict ONE_OFF
    tmp = _fixture({"results/_r300_orphan.py": "", "Tools/s6_chain_bmb.py": "LEGS = []\n"},
                   {"results/paper/C_paper.json": ["results/_r300_orphan.py"]})
    try:
        face, pr = build(root=tmp, write=False)
        leg("a face swept only by an unnamed module is only_a_one_off",
            face["faces"][0]["only_a_one_off"] is True, str(face["faces"][0]))
        leg("counts.faces_with_only_a_one_off_sweeper is 1",
            face["counts"]["faces_with_only_a_one_off_sweeper"] == 1,
            str(face["counts"]))
        leg("verdict is ONE_OFF", face["verdict"] == V_ONE_OFF, face["verdict"])
        leg("orphan fixture face problems empty", not pr, str(pr))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 4. priority: a module named by both a task and a smoke leg grades scheduled
    tmp = _fixture({
        "smoke_test.py": "# results/_r400_both.py\n",
        "Tools/register_x.ps1": 'schtasks /create /tr "python results/_r400_both.py"\n',
        "results/_r400_both.py": "",
    }, {"results/paper/D_paper.json": ["results/_r400_both.py"]})
    try:
        face, _pr = build(root=tmp, write=False)
        by = {m["module"]: m for m in face["modules"]}
        leg("scheduled outranks smoke for the same module",
            by["results/_r400_both.py"]["class"] == C_SCHED,
            str(by["results/_r400_both.py"]))
        leg("the multi-kind module is counted",
            face["counts"]["modules_named_by_more_than_one_kind"] == 1,
            str(face["counts"]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 5. boundary rules that do not depend on the tree
    leg("_r99 is a round script", bool(ROUND_RE.match("_r99_x.py")))
    leg("e611_ is not a round script", not ROUND_RE.match("e611_sweep_reruns.py"))
    leg("own-dir sites need the full directory depth",
        len(_own_dir_sites("a/b/c.json", [{"naming_segments": ["a"], "named_dir_depth": 1}])) == 0)
    leg("own-dir sites accept the full depth",
        len(_own_dir_sites("a/b/c.json", [{"naming_segments": ["a", "b"],
                                           "named_dir_depth": 2}])) == 1)
    leg("a site naming nothing is never an own-directory site",
        len(_own_dir_sites("a/c.json", [{"naming_segments": [], "named_dir_depth": 1}])) == 0)

    # 6. the guard can go red
    tmp = _fixture({"results/_r500_a.py": ""},
                   {"results/paper/E_paper.json": ["results/_r500_a.py"]})
    try:
        face, _ = build(root=tmp, write=False)
        bad = json.loads(json.dumps(face))
        bad["counts"]["faces_with_only_a_one_off_sweeper"] = 0
        leg("the guard rejects a face count that does not re-derive", bool(face_problems(bad)))
        bad2 = json.loads(json.dumps(face))
        bad2["modules"][0]["class"] = C_SMOKE
        leg("the guard rejects a class its entry hits do not support", bool(face_problems(bad2)))
        bad3 = json.loads(json.dumps(face))
        bad3["verdict"] = V_RERUNS
        leg("the guard rejects a verdict that does not follow the counts", bool(face_problems(bad3)))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    failures = [x for x in legs if not x["ok"]]
    print(json.dumps({"legs": len(legs), "failed": len(failures), "detail": failures},
                     ensure_ascii=False, indent=1))
    return 0 if not failures else 1


# --------------------------------------------------------------------------- cli
def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="build")
    args = ap.parse_args(argv[1:])
    cmd = args.cmd.lower()
    if cmd == "selftest":
        return selftest()
    face, problems = build(write=(cmd in ("build", "run")))
    if problems:
        print("PROBLEMS: " + "; ".join(problems))
        return 1
    c = face["counts"]
    print("faces=%d modules=%d by_class=%s"
          % (c["faces"], c["modules"],
             json.dumps({k: c.get(k, 0) for k in CLASSES}, sort_keys=True)))
    print("faces_only_one_off=%d round_scripts=%d round_scripts_unrun=%d entry_files=%d"
          % (c["faces_with_only_a_one_off_sweeper"], c["round_scripts"],
             c["round_scripts_nothing_names"], c["entry_files"]))
    print("verdict=" + face["verdict"])
    print("answer=" + face["answer"])
    if cmd in ("check", "verify"):
        pr = face_problems(face)
        print("problems=%s" % json.dumps(pr, ensure_ascii=False))
        return 0 if not pr else 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))