"""E613 -- do the ancestor-only swept faces have a sweeper that runs again?

E611 (r1635) priced the runner for the six faces a glob reaches by naming *their own* directory,
and found all six swept only by one-off round scripts.  E609's lane note seeded the other half:
76 of the 82 unread faces are reached only by a pattern that names an *ancestor* directory
(``results/**/*.json``), so the landing there is a generic sweep rather than a named one.

This study applies the same entry-point pricing to that population, and adds the thing that only
exists on the ancestor side: the sweeps are generic, so many faces collapse onto a handful of
modules.  The price is therefore published per module as well as per face -- a single unnamed
sweeper that carries 76 faces is a different fact from 76 separate one-off modules.

Population is machine-read from E609's face: every row graded ``names_an_ancestor_directory_only``
and, on it, only the sites that name a non-empty ancestor prefix shorter than the face's own
directory list (a depth-0 site such as ``*/**/*`` names nothing and is not an ancestor sweep).
Those sites' ``source`` files are the landing modules, then E611's classifier asks of each module
whether a scheduled task, a per-round chain or a smoke leg names its path.

Run:      python scripts/e613_ancestor_reruns.py run
Verify:   python scripts/e613_ancestor_reruns.py verify
Check:    python scripts/e613_ancestor_reruns.py check
Selftest: python scripts/e613_ancestor_reruns.py selftest
"""

import argparse
import io
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import e609_glob_reach as e609                                         # noqa: E402  (segments)
import e611_sweep_reruns as e611                                       # noqa: E402  (classifier)

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
SELF_STEM = "ANCESTORRERUNS"
OUT_PATH = os.path.join(OUTDIR, SELF_STEM + ".json")
E609_FACE = ("results", "state_tilt", "GLOBSWEEPREACH.json")
SELF_SKIP = ("e613_", "run_e613") + tuple(e611.SELF_SKIP)

C_SCHED = e611.C_SCHED
C_CHAIN = e611.C_CHAIN
C_SMOKE = e611.C_SMOKE
C_NONE = e611.C_NONE
CLASSES = e611.CLASSES

V_SOME = "at_least_one_ancestor_only_face_has_a_sweeper_an_entry_point_runs_again"
V_ALL_ONE_OFF = "every_ancestor_only_face_is_swept_only_by_modules_no_entry_point_names"
V_EMPTY = "the_population_is_empty"
VERDICT_VOCAB = (V_SOME, V_ALL_ONE_OFF, V_EMPTY)


# --------------------------------------------------------------------------- population
def _read_json(path):
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _ancestor_sites(face_rel, sites):
    """Sites naming a non-empty ancestor prefix, shorter than the face's own directory list."""
    parts = e609.segments(face_rel)
    total = len(parts) - 1
    out = []
    for s in sites or []:
        segs = s.get("naming_segments") or []
        depth = int(s.get("named_dir_depth") or 0)
        if not segs or depth < 1:
            continue            # a depth-0 site names nothing: it is a sweep, not an ancestor
        if total and depth < total:
            out.append(s)
    return out


def _e609_rows(root=None):
    root = root or ROOT
    face_path = os.path.join(root, *E609_FACE)
    if not os.path.exists(face_path):
        return None, "e609_face_absent"
    try:
        pub = _read_json(face_path)
    except (OSError, ValueError):
        return None, "e609_face_unreadable"
    return [r for r in pub.get("faces") or [] if r.get("class") == e609.C_PART], None


def population(root=None):
    rows, why = _e609_rows(root)
    if rows is None:
        return [], why
    pub = {"faces": rows}
    out = []
    for rec in pub.get("faces") or []:
        if rec.get("class") != e609.C_PART:
            continue
        rel = rec.get("face") or ""
        sites = _ancestor_sites(rel, rec.get("sites") or [])
        if not sites:
            continue
        out.append({"face": rel, "present": bool(rec.get("present")),
                    "disagreeing_series": rec.get("disagreeing_series"), "sites": sites})
    out.sort(key=lambda r: r["face"])
    return out, None


# --------------------------------------------------------------------------- corpus
def entry_corpora(root=None):
    """E611's entry corpora with this study's own files removed from the entry side."""
    corpus = e611.entry_corpora(root)
    return [e for e in corpus
            if not any(os.path.basename(e["source"]).startswith(s) for s in SELF_SKIP)]


# --------------------------------------------------------------------------- build
def _patterns_of(pop):
    """pattern -> faces it lands on (ancestor sites only)."""
    pats = {}
    for rec in pop:
        for s in rec["sites"]:
            pat = s.get("pattern")
            if not pat:
                continue
            row = pats.setdefault(pat, {"pattern": pat, "faces": [], "modules": []})
            if rec["face"] not in row["faces"]:
                row["faces"].append(rec["face"])
            src = s.get("source")
            if src and src not in row["modules"]:
                row["modules"].append(src)
    out = []
    for row in pats.values():
        row["faces"].sort()
        row["modules"].sort()
        row["faces_count"] = len(row["faces"])
        out.append(row)
    out.sort(key=lambda r: (-r["faces_count"], r["pattern"]))
    return out


def no_name_sweeps(root=None, corpus_texts=None):
    """Modules that touch these faces only through a pattern naming nothing (``*/**/*``).

    They are not ancestor sweeps, so they are not in the population -- but dropping them silently
    would undercount the landing set, so they are classified and published beside it.
    """
    root = root or ROOT
    rows, _why = _e609_rows(root)
    if rows is None:
        return [], 0, 0
    seen = {}
    dropped = 0
    for rec in rows:
        for s in rec.get("sites") or []:
            if (s.get("naming_segments") or []) or int(s.get("named_dir_depth") or 0) >= 1:
                continue
            dropped += 1
            src = s.get("source")
            if not src or not src.endswith(".py"):
                continue
            row = seen.setdefault(src, {"module": src, "faces": [], "patterns": []})
            if rec["face"] not in row["faces"]:
                row["faces"].append(rec["face"])
            pat = s.get("pattern")
            if pat and pat not in row["patterns"]:
                row["patterns"].append(pat)
    out = []
    links = 0
    corpus_texts = corpus_texts or []
    for src in sorted(seen):
        row = seen[src]
        links += len(row["faces"])
        cls = e611._classify(src, corpus_texts, root)
        out.append({"module": src,
                    "faces_count": len(row["faces"]),
                    "patterns": sorted(row["patterns"]),
                    "class": cls["class"],
                    "named_by": cls["named_by"],
                    "named_by_count": cls["named_by_count"],
                    "is_a_round_script": cls["is_a_round_script"],
                    "round_no": cls["round_no"]})
    return out, dropped, links


def build(root=None, write=False):
    root = root or ROOT
    pop, why = population(root)
    corpus = entry_corpora(root)
    corpus_texts = []
    for e in corpus:
        text = e611._text(root, e["source"])
        if text:
            corpus_texts.append((e["source"], e["kind"], text))

    mods = e611._modules_of(pop)
    module_rows = [e611._classify(rel, corpus_texts, root) for rel in sorted(mods)]
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

    patterns = _patterns_of(pop)
    for row in patterns:
        rows = [by_module[m] for m in row["modules"] if m in by_module]
        row["sweepers_an_entry_point_runs_again"] = [r["module"] for r in rows
                                                     if r["class"] != C_NONE]
        row["carried_only_by_a_one_off"] = bool(rows) and not row[
            "sweepers_an_entry_point_runs_again"]

    no_name, no_name_sites, no_name_links = no_name_sweeps(root, corpus_texts)

    counts = {c: 0 for c in CLASSES}
    for r in module_rows:
        counts[r["class"]] += 1
    counts["modules"] = len(module_rows)
    counts["modules_on_checkout"] = sum(1 for r in module_rows if r["on_checkout"])
    counts["round_scripts"] = sum(1 for r in module_rows if r["is_a_round_script"])
    counts["round_scripts_nothing_names"] = sum(
        1 for r in module_rows if r["is_a_round_script"] and r["class"] == C_NONE)
    counts["faces"] = len(faces)
    counts["faces_with_only_a_one_off_sweeper"] = sum(1 for f in faces if f["only_a_one_off"])
    counts["faces_with_a_sweeper_an_entry_point_runs_again"] = sum(
        1 for f in faces if f["sweepers_an_entry_point_runs_again"])
    counts["distinct_patterns"] = len(patterns)
    counts["patterns_carried_only_by_a_one_off"] = sum(
        1 for p in patterns if p["carried_only_by_a_one_off"])
    counts["faces_carried_by_the_largest_pattern"] = (
        patterns[0]["faces_count"] if patterns else 0)
    counts["sweepers_per_face_max"] = max((len({s.get("source") for s in rec["sites"]
                                                if s.get("source")}) for rec in pop), default=0)
    counts["entry_files"] = len(corpus)
    for k in e611.KINDS:
        counts["entry_files_" + k] = sum(1 for e in corpus if e["kind"] == k)
    counts["no_name_modules"] = len(no_name)
    counts["no_name_sites_dropped"] = no_name_sites
    counts["no_name_face_links"] = no_name_links
    counts["no_name_modules_an_entry_point_runs_again"] = sum(
        1 for r in no_name if r["class"] != C_NONE)
    counts["no_name_modules_that_are_round_scripts"] = sum(
        1 for r in no_name if r["is_a_round_script"])

    face = {
        "study": "E613_ancestor_reruns",
        "card": "E613-WHETHER-THE-ANCESTOR-ONLY-SWEPT-FACES-HAVE-A-SWEEPER-THAT-RUNS-AGAIN",
        "evidence_cutoff": _cutoff(pop),
        "population_source": "results/state_tilt/GLOBSWEEPREACH.json (E609 faces graded "
                             "names_an_ancestor_directory_only, ancestor sites only)",
        "population_note": why or "read from the published E609 face",
        "class_vocabulary": list(CLASSES),
        "counts": counts,
        "modules": module_rows,
        "patterns": patterns,
        "no_name_sweeps": no_name,
        "faces": faces,
        "verdict": verdict_from(counts),
        "answer": answer_sentence(counts, patterns, no_name),
        "limits": [
            "an ancestor site is a bounded pattern whose named prefix is non-empty and shorter "
            "than the face's own directory list; a depth-0 site (``*/**/*``) names nothing and is "
            "excluded, so a face swept only that way would not enter this population",
            "the sweeps here are generic by construction: one pattern can carry every face under "
            "an ancestor, so a module named by an entry point reaches these faces only "
            "incidentally -- this face prices reachability of the sweeper, not that the sweep "
            "reads any particular face",
            "one hop only: the entry-point class comes from E611's classifier (module basename "
            "appearing in an entry file), so a reference composed from a string is a miss",
            "a smoke leg counts as an entry point because it runs whenever the suite runs, and "
            "the full suite is not run every round (r1499)",
            "the population is machine-read from E609's published face; a stale E609 face would "
            "be graded as published, and population_note says where it came from",
            "modules that touch these faces only through a pattern naming nothing (``*/**/*``) "
            "are excluded from the population because they name no ancestor, and are published "
            "beside it in no_name_sweeps with their own entry-point class so a dropped non-round "
            "script stays visible",
        ],
    }
    pr = face_problems(face)
    if write and not pr:
        write_face(face)
    return face, pr


def _cutoff(pop):
    best = ""
    for rec in pop:
        for m in e609.re.finditer(r"(20\d\d-\d\d-\d\d)", rec["face"]):
            if m.group(1) > best:
                best = m.group(1)
    return best or "no-date-in-population"


def answer_sentence(counts, patterns, no_name=None):
    total = counts.get("faces") or 0
    if not total:
        return "the population is empty, so no ancestor landing is priced"
    lead = patterns[0] if patterns else None
    tail = ""
    if lead:
        tail = (" The largest single pattern is %s, which carries %d of %d faces."
                % (lead["pattern"], lead["faces_count"], total))
    rerun = [r for r in (no_name or []) if r.get("class") != C_NONE]
    outside = ""
    if rerun:
        top = max(rerun, key=lambda r: int(r.get("faces_count") or 0))
        outside = (" One module outside the ancestor population does run again -- %s (%s) reaches "
                   "%d of the %d faces, but only through a pattern that names nothing (%s), so it "
                   "is not an ancestor sweep."
                   % (top["module"], top["class"], top["faces_count"], total,
                      (top["patterns"] or ["?"])[0]))
    return ("of %d faces reached only by a glob that names an ancestor directory, %d carry at "
            "least one sweeper an entry point runs again and %d are swept only by modules nothing "
            "names -- but they collapse onto %d landing modules, so %d of the %d faces rest on "
            "%d distinct sweeps.%s Also, %d modules touch the same faces only through a pattern "
            "that names nothing (%d of them entry-point-named, %d of them round scripts).%s"
            % (total, counts.get("faces_with_a_sweeper_an_entry_point_runs_again", 0),
               counts.get("faces_with_only_a_one_off_sweeper", 0),
               counts.get("modules", 0), counts.get("faces_carried_by_the_largest_pattern", 0),
               total, counts.get("distinct_patterns", 0), tail,
               counts.get("no_name_modules", 0),
               counts.get("no_name_modules_an_entry_point_runs_again", 0),
               counts.get("no_name_modules_that_are_round_scripts", 0), outside))


def verdict_from(counts):
    if not counts.get("faces"):
        return V_EMPTY
    if counts.get("faces_with_a_sweeper_an_entry_point_runs_again"):
        return V_SOME
    return V_ALL_ONE_OFF


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
    patterns = face.get("patterns") or []
    if not modules and counts.get("modules"):
        p.append("counts.modules says %r but the face publishes no module rows"
                 % counts.get("modules"))
    if not faces:
        p.append("the face publishes no faces")
    if not patterns:
        p.append("the face publishes no pattern rows")

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
        if named - set(e611.KINDS):
            p.append("module %s is named by an unknown entry kind %r"
                     % (rec.get("module"), sorted(named - set(e611.KINDS))))
            break
        if cls == C_NONE and named:
            p.append("module %s grades NAMED_BY_NOTHING but publishes entry hits"
                     % rec.get("module"))
            break
        if cls != C_NONE:
            want = {e611.K_SCHED: C_SCHED, e611.K_CHAIN: C_CHAIN, e611.K_SMOKE: C_SMOKE}
            best = max((want[k] for k in named), key=lambda c: e611.PRIORITY[c], default=C_NONE)
            if best != cls:
                p.append("module %s grades %r but its entry hits say %r"
                         % (rec.get("module"), cls, best))
                break
        if rec.get("is_a_round_script") != bool(e611.ROUND_RE.match(
                str(os.path.basename(rec.get("module") or "")))):
            p.append("module %s disagrees with the round-script rule" % rec.get("module"))
            break
    for c in CLASSES:
        if counts.get(c, 0) != tally.get(c, 0):
            p.append("counts.%s says %r but the rows say %d" % (c, counts.get(c), tally.get(c, 0)))
    if counts.get("modules") != len(modules):
        p.append("counts.modules says %r but the face publishes %d rows"
                 % (counts.get("modules"), len(modules)))
    if counts.get("round_scripts") != sum(1 for r in modules if r.get("is_a_round_script")):
        p.append("counts.round_scripts does not re-derive")
    if counts.get("round_scripts_nothing_names") != sum(
            1 for r in modules if r.get("is_a_round_script") and r.get("class") == C_NONE):
        p.append("counts.round_scripts_nothing_names does not re-derive")
    if counts.get("modules_on_checkout") != sum(1 for r in modules if r.get("on_checkout")):
        p.append("counts.modules_on_checkout does not re-derive")

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

    for row in patterns:
        rows = [by_module[m] for m in row.get("modules") or [] if m in by_module]
        rerun = [r["module"] for r in rows if r["class"] != C_NONE]
        if row.get("sweepers_an_entry_point_runs_again") != rerun:
            p.append("pattern %s publishes re-running sweepers that do not re-derive"
                     % row.get("pattern"))
            break
        if bool(row.get("carried_only_by_a_one_off")) != (bool(rows) and not rerun):
            p.append("pattern %s publishes carried_only_by_a_one_off that does not re-derive"
                     % row.get("pattern"))
            break
        if int(row.get("faces_count") or 0) != len(row.get("faces") or []):
            p.append("pattern %s publishes faces_count %r beside %d faces"
                     % (row.get("pattern"), row.get("faces_count"),
                        len(row.get("faces") or [])))
            break
    covered = {}
    for row in patterns:
        for f in row.get("faces") or []:
            covered[f] = covered.get(f, 0) + 1
    missing = [f.get("face") for f in faces if f.get("face") not in covered]
    if missing:
        p.append("%d faces are published but sit under no pattern row (first: %s)"
                 % (len(missing), missing[0]))
    if counts.get("distinct_patterns") != len(patterns):
        p.append("counts.distinct_patterns says %r but the face publishes %d rows"
                 % (counts.get("distinct_patterns"), len(patterns)))
    if counts.get("patterns_carried_only_by_a_one_off") != sum(
            1 for r in patterns if r.get("carried_only_by_a_one_off")):
        p.append("counts.patterns_carried_only_by_a_one_off does not re-derive")
    want_lead = max((int(r.get("faces_count") or 0) for r in patterns), default=0)
    if int(counts.get("faces_carried_by_the_largest_pattern") or 0) != want_lead:
        p.append("counts.faces_carried_by_the_largest_pattern does not re-derive")
    no_name = face.get("no_name_sweeps") or []
    for row in no_name:
        if row.get("class") not in CLASSES:
            p.append("no-name module %s carries an unknown class %r"
                     % (row.get("module"), row.get("class")))
            break
        if row.get("class") == C_NONE and row.get("named_by"):
            p.append("no-name module %s grades NAMED_BY_NOTHING but publishes entry hits"
                     % row.get("module"))
            break
        if int(row.get("named_by_count") or 0) < len(row.get("named_by") or []):
            p.append("no-name module %s publishes more hits than its count"
                     % row.get("module"))
            break
    if counts.get("no_name_modules") != len(no_name):
        p.append("counts.no_name_modules says %r but the face publishes %d rows"
                 % (counts.get("no_name_modules"), len(no_name)))
    if counts.get("no_name_modules_an_entry_point_runs_again") != sum(
            1 for r in no_name if r.get("class") != C_NONE):
        p.append("counts.no_name_modules_an_entry_point_runs_again does not re-derive")
    if counts.get("no_name_modules_that_are_round_scripts") != sum(
            1 for r in no_name if r.get("is_a_round_script")):
        p.append("counts.no_name_modules_that_are_round_scripts does not re-derive")
    if int(counts.get("no_name_face_links") or 0) < len(no_name):
        p.append("counts.no_name_face_links is smaller than the number of no-name modules")
    if face.get("verdict") != verdict_from(counts):
        p.append("verdict %r does not re-derive from the counts (rule says %r)"
                 % (face.get("verdict"), verdict_from(counts)))
    if not face.get("answer"):
        p.append("the face carries no answer sentence")
    return p


# --------------------------------------------------------------------------- selftest
def _fixture(files, faces):
    """Throw-away repo.  files = {relpath: text}; faces = {relpath: [ancestor site sources]}."""
    tmp = tempfile.mkdtemp(prefix="e613_")
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
        ancestor = dirs[:1]
        rows.append({"face": rel, "present": True, "disagreeing_series": 1,
                     "class": e609.C_PART,
                     "sites": [{"source": src, "line": 1,
                                "pattern": "/".join(ancestor + ["**", "*"]),
                                "score": len(ancestor), "naming_segments": ancestor,
                                "named_dir_depth": len(ancestor)}
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

    # 1. one face, one round-script sweeper nothing names -> ALL_ONE_OFF
    tmp = _fixture({"results/_r700_sweep.py": ""},
                   {"results/paper/A_paper.json": ["results/_r700_sweep.py"]})
    try:
        face, pr = build(root=tmp, write=False)
        leg("ancestor fixture builds a face", not pr, str(pr))
        leg("population reads the ancestor row",
            face["counts"]["faces"] == 1 and face["counts"]["modules"] == 1, str(face["counts"]))
        leg("the round-script sweeper is NAMED_BY_NOTHING",
            face["modules"][0]["class"] == C_NONE, str(face["modules"][0]))
        leg("the only face is only_a_one_off", face["faces"][0]["only_a_one_off"] is True,
            str(face["faces"][0]))
        leg("verdict is ALL_ONE_OFF", face["verdict"] == V_ALL_ONE_OFF, face["verdict"])
        leg("the one pattern is carried only by a one-off",
            face["patterns"][0]["carried_only_by_a_one_off"] is True, str(face["patterns"][0]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 2. a chain-named sweeper -> SOME
    tmp = _fixture({"Tools/s6_chain_bmb.py": 'LEGS = [["python", "results/_r701_sweep.py"]]\n',
                    "results/_r701_sweep.py": ""},
                   {"results/paper/B_paper.json": ["results/_r701_sweep.py"]})
    try:
        face, pr = build(root=tmp, write=False)
        leg("a chain-named sweeper grades LIVE_CHAIN",
            face["modules"][0]["class"] == C_CHAIN, str(face["modules"][0]))
        leg("one re-running sweeper keeps its face off only_a_one_off",
            face["faces"][0]["only_a_one_off"] is False, str(face["faces"][0]))
        leg("verdict is SOME when a face has a re-running sweeper",
            face["verdict"] == V_SOME, face["verdict"])
        leg("guard accepts the chain fixture", not pr, str(pr))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 3. a scheduled task outranks a smoke leg for the same module (E611's priority, reused)
    tmp = _fixture({"smoke_test.py": "# results/_r702_both.py\n",
                    "Tools/register_x.ps1": 'schtasks /create /tr "python results/_r702_both.py"\n',
                    "results/_r702_both.py": ""},
                   {"results/paper/C_paper.json": ["results/_r702_both.py"]})
    try:
        face, _pr = build(root=tmp, write=False)
        leg("scheduled outranks smoke for the same ancestor sweeper",
            face["modules"][0]["class"] == C_SCHED, str(face["modules"][0]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 4. many faces on one pattern collapse to one sweeper
    tmp = _fixture({"results/_r703_sweep.py": ""},
                   {"results/paper/D1.json": ["results/_r703_sweep.py"],
                    "results/paper/D2.json": ["results/_r703_sweep.py"],
                    "results/paper/D3.json": ["results/_r703_sweep.py"]})
    try:
        face, pr = build(root=tmp, write=False)
        leg("three faces collapse onto one landing module",
            face["counts"]["faces"] == 3 and face["counts"]["modules"] == 1,
            str(face["counts"]))
        leg("they share one distinct pattern", face["counts"]["distinct_patterns"] == 1,
            str(face["counts"]))
        leg("the largest pattern carries all three faces",
            face["counts"]["faces_carried_by_the_largest_pattern"] == 3, str(face["counts"]))
        leg("the pattern row lists all three faces",
            face["patterns"][0]["faces_count"] == 3, str(face["patterns"][0]))
        leg("guard accepts the collapse fixture", not pr, str(pr))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 5. C_FULL rows are not this population
    tmp = _fixture({"results/paper/E_paper.json": "", "results/_r704_sweep.py": ""},
                   {})
    try:
        p = os.path.join(tmp, "results", "state_tilt", "GLOBSWEEPREACH.json")
        with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
            json.dump({"faces": [{"face": "results/paper/E_paper.json", "present": True,
                                  "disagreeing_series": 1, "class": e609.C_FULL,
                                  "sites": [{"source": "results/_r704_sweep.py", "line": 1,
                                             "pattern": "results/paper/*", "score": 2,
                                             "naming_segments": ["results", "paper"],
                                             "named_dir_depth": 2}]}]}, fh)
        face, pr = build(root=tmp, write=False)
        leg("a names_the_directory row is not in the ancestor population",
            face["counts"]["faces"] == 0, str(face["counts"]))
        leg("an empty population is graded EMPTY", face["verdict"] == V_EMPTY, face["verdict"])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 6. a depth-0 site is not an ancestor sweep
    leg("a depth-0 site is not an ancestor site",
        _ancestor_sites("results/paper/F.json",
                        [{"naming_segments": [], "named_dir_depth": 0,
                          "source": "results/_r705_x.py"}]) == [])
    leg("a depth-1 site on a two-deep face is an ancestor site",
        len(_ancestor_sites("results/paper/F.json",
                            [{"naming_segments": ["results"], "named_dir_depth": 1,
                              "source": "results/_r705_x.py"}])) == 1)
    leg("a site naming the full directory is not an ancestor site",
        _ancestor_sites("results/paper/F.json",
                        [{"naming_segments": ["results", "paper"], "named_dir_depth": 2,
                          "source": "results/_r705_x.py"}]) == [])
    leg("a top-level face has no ancestor site to declare",
        _ancestor_sites("F.json", [{"naming_segments": ["results"], "named_dir_depth": 1,
                                    "source": "results/_r705_x.py"}]) == [])

    # 7. the study's own legs are not entry points
    tmp = _fixture({"scripts/run_e613_smoke_leg.py": "# results/_r706_x.py\n",
                    "scripts/e613_ancestor_reruns.py": "# results/_r706_x.py\n",
                    "results/_r706_x.py": ""},
                   {"results/paper/G.json": ["results/_r706_x.py"]})
    try:
        face, _pr = build(root=tmp, write=False)
        leg("this study's own files do not name a sweeper",
            face["modules"][0]["class"] == C_NONE, str(face["modules"][0]))
        leg("its own legs are not counted as entry files",
            face["counts"]["entry_files_smoke_leg"] == 0, str(face["counts"]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 8. the guard can go red
    tmp = _fixture({"results/_r707_sweep.py": ""},
                   {"results/paper/H.json": ["results/_r707_sweep.py"]})
    try:
        face, _ = build(root=tmp, write=False)
        bad = json.loads(json.dumps(face))
        bad["counts"]["faces_with_only_a_one_off_sweeper"] = 0
        leg("the guard rejects a face count that does not re-derive", bool(face_problems(bad)))
        bad2 = json.loads(json.dumps(face))
        bad2["modules"][0]["class"] = C_SMOKE
        leg("the guard rejects a class its entry hits do not support", bool(face_problems(bad2)))
        bad3 = json.loads(json.dumps(face))
        bad3["verdict"] = V_SOME
        leg("the guard rejects a verdict that does not follow the counts", bool(face_problems(bad3)))
        bad4 = json.loads(json.dumps(face))
        bad4["patterns"][0]["faces"] = []
        bad4["patterns"][0]["faces_count"] = 0
        leg("the guard rejects a face that sits under no pattern row", bool(face_problems(bad4)))
        bad5 = json.loads(json.dumps(face))
        bad5["counts"]["faces_carried_by_the_largest_pattern"] = 7
        leg("the guard rejects a largest-pattern count that does not re-derive",
            bool(face_problems(bad5)))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 9. a depth-0 sweeper is excluded from the population but still published
    tmp = _fixture({"results/_r708_sweep.py": "",
                    "scripts/e397_live_study.py": ""},
                   {"results/paper/I.json": []})
    try:
        p = os.path.join(tmp, "results", "state_tilt", "GLOBSWEEPREACH.json")
        with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
            json.dump({"faces": [{"face": "results/paper/I.json", "present": True,
                                  "disagreeing_series": 1, "class": e609.C_PART,
                                  "sites": [{"source": "results/_r708_sweep.py", "line": 1,
                                             "pattern": "*/**/*", "score": 0,
                                             "naming_segments": [], "named_dir_depth": 0},
                                            {"source": "scripts/e397_live_study.py", "line": 2,
                                             "pattern": "*/**/*.json", "score": 0,
                                             "naming_segments": [], "named_dir_depth": 0},
                                            {"source": "results/_r709_ancestor.py", "line": 3,
                                             "pattern": "results/**/*.json", "score": 1,
                                             "naming_segments": ["results"],
                                             "named_dir_depth": 1}]}]}, fh)
        face, pr = build(root=tmp, write=False)
        leg("the depth-0 sweeper stays out of the population",
            [m["module"] for m in face["modules"]] == ["results/_r709_ancestor.py"],
            str([m["module"] for m in face["modules"]]))
        leg("two depth-0 sites are published as dropped",
            face["counts"]["no_name_sites_dropped"] == 2, str(face["counts"]))
        leg("both depth-0 modules are published beside the population",
            face["counts"]["no_name_modules"] == 2, str(face["counts"]))
        leg("a dropped module is still asked whether an entry point names it",
            all("class" in r for r in face["no_name_sweeps"]), str(face["no_name_sweeps"]))
        leg("guard accepts the exclusion fixture", not pr, str(pr))
        bad6 = json.loads(json.dumps(face))
        bad6["counts"]["no_name_modules"] = 1
        leg("the guard rejects a no-name module count that does not re-derive",
            bool(face_problems(bad6)))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 10. boundary rules
    leg("_r99 is a round script", bool(e611.ROUND_RE.match("_r99_x.py")))
    leg("e613_ is not a round script", not e611.ROUND_RE.match("e613_ancestor_reruns.py"))

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
    print("faces=%d modules=%d patterns=%d by_class=%s"
          % (c["faces"], c["modules"], c["distinct_patterns"],
             json.dumps({k: c.get(k, 0) for k in CLASSES}, sort_keys=True)))
    print("faces_only_one_off=%d faces_rerunning=%d round_scripts=%d round_scripts_unrun=%d "
          "largest_pattern_faces=%d"
          % (c["faces_with_only_a_one_off_sweeper"],
             c["faces_with_a_sweeper_an_entry_point_runs_again"],
             c["round_scripts"], c["round_scripts_nothing_names"],
             c["faces_carried_by_the_largest_pattern"]))
    print("no_name_modules=%d named_by_an_entry=%d round_scripts=%d sites_dropped=%d"
          % (c["no_name_modules"], c["no_name_modules_an_entry_point_runs_again"],
             c["no_name_modules_that_are_round_scripts"], c["no_name_sites_dropped"]))
    print("verdict=" + face["verdict"])
    print("answer=" + face["answer"])
    if cmd in ("check", "verify"):
        pr = face_problems(face)
        print("problems=%s" % json.dumps(pr, ensure_ascii=False))
        return 0 if not pr else 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))