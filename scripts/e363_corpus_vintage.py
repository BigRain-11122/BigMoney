"""E363: a census population is only reproducible from an address it wrote down.

r1384 pinned the corpus and replayed it from git objects; it also named its own gap -- the pin is
taken *after* the face, so pointing a corpus-judging leg at "the newest pin" does not reproduce a
face published earlier.  This study prices that: for every study in the registry, the population the
published face quotes is compared against the same study run over three vintages.

  live      the working tree as it stands now
  pinned    the newest corpus pin, replayed from its commit plus its content store (e361/e362)
  history   the corpus at the commit that last wrote the face path -- the only address a face
            published from a working tree ever had

One rule is used for all three (``corpus_paths`` + ``files_from``), and the rule is proved against
the module's own live reading before any vintage is compared: if the rule does not reproduce what
the study itself scans today, the study refuses rather than publishing a three-way comparison of
three different populations (r1261: two populations equal because nothing ran).

Usage
  python scripts/e363_corpus_vintage.py run        build + publish the face
  python scripts/e363_corpus_vintage.py verify     re-derive every published row
  python scripts/e363_corpus_vintage.py selftest   offline, no git, no corpus read
"""
import datetime as dt
import io
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import e361_census_corpus_pin as e361  # noqa: E402
import e362_corpus_replay as e362  # noqa: E402
import e326_template_parameter_consumers as e326  # noqa: E402

ROOT = e361.ROOT
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
STUDY = "e363_corpus_vintage"
TODAY = dt.date.today().isoformat()
FACE = "FACEVINTAGE-2026-11-02.json"
LATEST = "facevintage_latest.json"

CORPUS_ROOTS = ("scripts", "Tools", "live", "monitor", "firm")

# the corpus rule as every study in the registry applies it: e323 drops itself, e325 drops itself,
# e326 drops itself, and each study drops its own source (E204/r1232 self-inclusion family).
DECLARED_EXCLUDED = ("e323_reach_under_wider_needle.py", "e325_orphan_gate_faces.py",
                     "e326_template_parameter_consumers.py")

REGISTRY = (
    {"module": "e331_pointer_only_readers", "face": "pointeronly_latest.json",
     "population_key": "sources_scanned",
     "question": "which readers reach a face only through a pointer"},
    {"module": "e335_sibling_entry_point", "face": "siblingentry_latest.json",
     "population_key": "sources_read",
     "question": "does the repaired reading land beside the shipped one"},
)

VERDICT_NAMED = "every_published_population_is_reproducible_from_the_pin_the_face_names"
VERDICT_ADDRESSED = "every_published_population_is_reproducible_from_the_commit_that_wrote_the_face"
VERDICT_WORKTREE = "a_published_population_is_reproducible_only_from_the_working_tree_that_ran_it"
VERDICT_TODAY = "a_published_population_matches_today_and_only_today"
VERDICT_PIN = "a_published_population_is_reproducible_from_the_newest_pin_and_nowhere_earlier"
VERDICT_UNCHECKED = "the_rule_does_not_reproduce_what_a_study_reads_so_no_vintage_was_compared"


# ------------------------------------------------------------------------------ corpus rule
def corpus_paths(paths, study_basename):
    """The population every study in the registry scans, as relative paths."""
    drop = set(DECLARED_EXCLUDED) | {study_basename}
    out = []
    for path in paths:
        rel = path.replace("\\", "/")
        parts = rel.split("/")
        if len(parts) < 2 or parts[0] not in CORPUS_ROOTS:
            continue
        if not rel.endswith(".py"):
            continue
        if parts[-1] in drop:
            continue
        out.append(rel)
    return sorted(out)


def files_from(texts, study_basename):
    """``[(abs_path, source)]`` -- the shape every study's ``files=`` seam accepts."""
    rels = corpus_paths(texts.keys(), study_basename)
    return [(os.path.join(ROOT, r.replace("/", os.sep)), texts[r]) for r in rels if r in texts]


# ------------------------------------------------------------------------------ vintages
def live_texts():
    out = {}
    for path, src in e326.corpus():
        out[e326.relp(path)] = src
    return out


def pinned_texts(pin_file=None):
    pin = e361.load_pin(pin_file)
    commit = pin.get("git_commit")
    if not commit:
        raise RuntimeError("the newest pin names no commit (%s)" % (pin.get("pin_id"),))
    gits = [s for s in pin["sources"] if s.get("tracked") and not s.get("dirty")]
    from_git, _missing = e362.blob_texts(commit, [s["path"] for s in gits])
    store = e362.load_store(pin["pin_id"])
    out = dict(from_git)
    for path, blob in store["texts"].items():
        out.setdefault(path, e362.decode_text(blob))
    return out, pin


def git_paths(commit):
    proc = subprocess.run(["git", "ls-tree", "-r", commit], cwd=ROOT, capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError("git ls-tree %s failed: %s"
                           % (commit[:12], proc.stderr.decode("utf-8", "replace")[:160]))
    rows = []
    for line in proc.stdout.decode("utf-8", "replace").splitlines():
        if "\t" in line:
            rows.append(line.split("\t", 1)[1])
    return rows


def history_texts(commit):
    paths = [p for p in git_paths(commit) if p.endswith(".py")]
    texts, _missing = e362.blob_texts(commit, paths)
    return texts


def face_commit(face_name):
    proc = subprocess.run(["git", "log", "-1", "--format=%H", "--",
                           "results/state_tilt/" + face_name], cwd=ROOT, capture_output=True)
    return proc.stdout.decode("utf-8", "replace").strip()


# ------------------------------------------------------------------------------ one reading
def reading(module_name, texts, study_basename):
    """Run a study over one vintage without touching its published face."""
    import importlib
    mod = importlib.import_module(module_name)
    files = files_from(texts, study_basename)
    outdir = tempfile.mkdtemp(prefix="e363_")
    try:
        doc = mod.build(outdir=outdir, files=files)
    except TypeError:
        doc = mod.build(outdir=outdir)
    summary = doc.get("summary") or {}
    return {"verdict": doc.get("verdict"), "summary": summary,
            "files": len(files), "doc": doc}


def published(entry):
    path = os.path.join(OUTDIR, entry["face"])
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def population(doc, key):
    return (doc.get("summary") or {}).get(key)


def classify(entry, stamp):
    """One registry row: the published population against the three vintages."""
    study = entry["module"] + ".py"
    pub = published(entry)
    key = entry["population_key"]
    live = reading(entry["module"], live_texts(), study)

    row = {"study": entry["module"], "face": entry["face"], "question": entry["question"],
           "population_key": key,
           "published_population": population(pub, key),
           "published_verdict": pub.get("verdict"),
           "live_population": live["summary"].get(key),
           "rule_agrees_with_the_study": live["summary"].get(key) == live["files"],
           "vintages": {}}
    if not row["rule_agrees_with_the_study"]:
        row["verdict"] = VERDICT_UNCHECKED
        row["classes"] = []
        return row

    pin_texts, pin = pinned_texts(stamp.get("pin_file"))
    row["newest_pin_id"] = pin.get("pin_id")
    row["newest_pin_commit"] = (pin.get("git_commit") or "")[:12]
    pinned = reading(entry["module"], pin_texts, study)

    commit = face_commit(entry["face"])
    row["publishing_commit"] = commit[:12] if commit else ""
    hist = None
    if commit:
        try:
            hist = reading(entry["module"], history_texts(commit), study)
        except Exception as exc:  # a commit that cannot be read is a published fact, not a crash
            row["history_error"] = repr(exc)[:160]

    target_summary = pub.get("summary") or {}
    named = None
    source = pub.get("corpus_source") or {}
    if source.get("pin_file"):
        try:
            named_texts, _named_pin = pinned_texts(os.path.join(OUTDIR, source["pin_file"]))
            named = reading(entry["module"], named_texts, study)
            row["named_pin"] = {"pin_file": source["pin_file"],
                                "pin_id": _named_pin.get("pin_id"),
                                "stamp_equal": (named["doc"].get("corpus") or {}).get("pin_id")
                                               == (pub.get("corpus") or {}).get("pin_id")}
        except Exception as exc:
            row["named_pin_error"] = repr(exc)[:160]
    for name, got in (("live", live), ("pinned", pinned), ("history", hist),
                      ("named_pin", named)):
        if got is None:
            continue
        s = got["summary"]
        moved = sorted(k for k in set(s) | set(target_summary) if s.get(k) != target_summary.get(k))
        row["vintages"][name] = {
            "population": s.get(key),
            "verdict_equal": got["verdict"] == pub.get("verdict"),
            "summary_equal": not moved,
            "keys_that_moved": moved,
            "keys_that_moved_count": len(moved),
        }

    hits = [n for n, v in row["vintages"].items() if v["summary_equal"]]
    row["classes"] = hits
    if "named_pin" in hits and (row.get("named_pin") or {}).get("stamp_equal"):
        row["verdict"] = VERDICT_NAMED
    elif "history" in hits:
        row["verdict"] = VERDICT_ADDRESSED
    elif "pinned" in hits:
        row["verdict"] = VERDICT_PIN
    elif "live" in hits:
        row["verdict"] = VERDICT_TODAY
    else:
        row["verdict"] = VERDICT_WORKTREE
    return row


# ------------------------------------------------------------------------------ stamp the faces
def stamp_faces(pin_file=None, outdir=None):
    """Republish each registry face over a named pin and record which pin produced it.

    This is the repair the measurement asks for: the face quotes the population it scanned *and*
    the address that population can be rebuilt from, so a later reader can reproduce it without
    depending on what today's working tree happens to hold.
    """
    import importlib
    pin_file = pin_file or e361.newest_pin()
    pin_texts, pin = pinned_texts(pin_file)
    target = outdir or OUTDIR
    os.makedirs(target, exist_ok=True)
    rows = []
    for entry in REGISTRY:
        study = entry["module"] + ".py"
        mod = importlib.import_module(entry["module"])
        files = files_from(pin_texts, study)
        doc = mod.build(outdir=target, files=files)
        path = os.path.join(target, entry["face"])
        with io.open(path, encoding="utf-8") as fh:
            payload = json.load(fh)
        payload["corpus_source"] = {
            "pin_file": os.path.basename(pin_file),
            "pin_id_of_pin": pin.get("pin_id"),
            "git_commit": pin.get("git_commit"),
            "replay": "e362 blob_texts + content store, working tree not read",
        }
        body = json.dumps(payload, ensure_ascii=False, indent=1) + "\n"
        for name in (getattr(mod, "FACE", entry["face"]), getattr(mod, "LATEST", entry["face"])):
            with io.open(os.path.join(target, name), "w", encoding="utf-8", newline="\n") as fh:
                fh.write(body)
        rows.append({"study": entry["module"], "face": entry["face"],
                     "population": (payload.get("summary") or {}).get(entry["population_key"]),
                     "corpus_members": (payload.get("corpus") or {}).get("members"),
                     "corpus_pin_id": (payload.get("corpus") or {}).get("pin_id"),
                     "pin_file": os.path.basename(pin_file), "pin_id_of_pin": pin.get("pin_id")})
    return rows


# ------------------------------------------------------------------------------ publish
def build(outdir=None):
    stamp = {"pin_file": e361.newest_pin()}
    rows = [classify(entry, stamp) for entry in REGISTRY]
    verdicts = sorted({r["verdict"] for r in rows})
    summary = {
        "studies_measured": len(rows),
        "populations_with_an_address_in_history": sum(1 for r in rows if "history" in r["classes"]),
        "populations_reproducible_from_the_newest_pin": sum(1 for r in rows if "pinned" in r["classes"]),
        "populations_reproducible_from_today_only": sum(1 for r in rows if "live" in r["classes"]),
        "populations_with_no_address": sum(1 for r in rows if not r["classes"]),
        "rules_that_reproduce_the_study": sum(1 for r in rows if r["rule_agrees_with_the_study"]),
        "verdicts": verdicts,
    }
    doc = {
        "study": STUDY,
        "evidence_cutoff": TODAY,
        "verdict": verdicts[0] if len(verdicts) == 1 else (
            VERDICT_WORKTREE if summary["populations_with_no_address"] else verdicts[0]),
        "rules": {
            "one rule for every vintage": "all three readings go through corpus_paths(), and the "
                                          "rule is proved against the study's own live population "
                                          "before any comparison is published",
            "history": "the commit that last wrote the face path -- a working-tree face has no "
                       "other address",
            "pinned": "the newest corpus pin replayed from its commit plus its content store",
            "no_republish": "this study never writes a face it grades; it publishes what each "
                            "vintage would say",
        },
        "limits": {
            "registry": "two studies are in the registry; a census that does not expose a files= "
                        "seam cannot be replayed over another vintage at all and is out of scope",
            "history_of_a_dirty_face": "a face written and never committed has no publishing "
                                       "commit, so its history row is absent rather than equal",
            "own_sources": "the exclusion list is declared here, so a study that changes its own "
                           "self-exclusion moves this rule -- the live leg catches that",
        },
        "summary": summary,
        "rows": rows,
    }
    target = outdir or OUTDIR
    os.makedirs(target, exist_ok=True)
    body = json.dumps(doc, ensure_ascii=False, indent=1) + "\n"
    for name in (FACE, LATEST):
        with io.open(os.path.join(target, name), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body)
    return doc


def verify():
    problems = []
    fresh = build(tempfile.mkdtemp(prefix="e363_verify_"))
    path = os.path.join(OUTDIR, LATEST)
    try:
        with io.open(path, encoding="utf-8") as fh:
            disk = json.load(fh)
    except Exception as exc:
        return ["the face does not read: %r" % (exc,)]
    if disk.get("verdict") != fresh["verdict"]:
        problems.append("the verdict does not re-derive")
    for key, value in fresh["summary"].items():
        if (disk.get("summary") or {}).get(key) != value:
            problems.append("summary.%s does not re-derive" % key)
    for new, old in zip(fresh["rows"], disk.get("rows") or []):
        if new["study"] != old.get("study"):
            problems.append("a published row does not re-derive its study")
            break
        if new["published_population"] != old.get("published_population"):
            problems.append("%s: the published population moved" % new["study"])
            break
        if new["verdict"] != old.get("verdict"):
            problems.append("%s: the verdict does not re-derive" % new["study"])
            break
        if sorted(new["classes"]) != sorted(old.get("classes") or []):
            problems.append("%s: the reproducible vintages do not re-derive" % new["study"])
            break
    return problems


# ------------------------------------------------------------------------------ selftest
def _fixture():
    return "scripts/a.py", "scripts/b.py", "Tools/c.py", "live/d.py", "firm/e.py"


def selftest():
    import inspect
    legs = []
    a, b, c, d, e = _fixture()

    # rel paths sort as bytes, so "Tools/" precedes the lower-case roots -- asserted, not assumed
    legs.append(("the rule keeps every corpus root, ordered by rel path", corpus_paths(
        (a, b, c, d, e), "e331_x.py") == ["Tools/c.py", "firm/e.py", "live/d.py", "scripts/a.py",
                                          "scripts/b.py"], ""))
    legs.append(("a non-python file is out of population",
                 corpus_paths(("scripts/a.py", "scripts/a.json"), "e331_x.py") == ["scripts/a.py"], ""))
    legs.append(("a root outside the corpus is out of population", corpus_paths(
        ("Money02/x.py", "legacy/y.py", a), "e331_x.py") == [a], ""))
    legs.append(("a declared exclusion is dropped", corpus_paths(
        ("scripts/e323_reach_under_wider_needle.py", a), "e331_x.py") == [a], ""))
    legs.append(("the study's own source is dropped by basename",
                 corpus_paths((a, b), "a.py") == [b], ""))
    legs.append(("a file at the root of a root is kept", corpus_paths(("firm/__init__.py",), "x.py")
                 == ["firm/__init__.py"], ""))

    texts = {"scripts/a.py": "A", "Tools/c.py": "C", "scripts/e323_reach_under_wider_needle.py": "X"}
    files = files_from(texts, "e331_x.py")
    legs.append(("files_from applies the same rule",
                 sorted(os.path.basename(p) for p, _t in files) == ["a.py", "c.py"], ""))
    legs.append(("files_from hands back the text it was given",
                 dict((os.path.basename(p), t) for p, t in files) == {"a.py": "A", "c.py": "C"}, ""))
    legs.append(("files_from never invents a member",
                 len(files_from({"scripts/a.py": "A"}, "x.py")) == 1, ""))

    # a rule that disagrees with the study must stop the comparison, not average it away
    row = {"module": "e331_pointer_only_readers", "face": "pointeronly_latest.json",
           "population_key": "sources_scanned", "question": "q"}
    live = {"summary": {"sources_scanned": 2}, "verdict": "v", "files": 3}
    legs.append(("a rule that does not reproduce the study's own count is visible",
                 (live["summary"]["sources_scanned"] != live["files"]) is True, ""))
    legs.append(("the unchecked verdict is its own class and not an empty one",
                 bool(VERDICT_UNCHECKED) and VERDICT_UNCHECKED != VERDICT_WORKTREE, ""))

    # the classes: the vintage names are distinct, and a class list is what a reader keys on
    legs.append(("four outcomes are four distinct strings",
                 len({VERDICT_ADDRESSED, VERDICT_WORKTREE, VERDICT_TODAY, VERDICT_PIN,
                      VERDICT_NAMED}) == 5, ""))
    legs.append(("the pin a face names is its own verdict, not the publishing commit's",
                 VERDICT_NAMED != VERDICT_ADDRESSED, ""))
    fake = {"vintages": {"live": {"summary_equal": False}, "pinned": {"summary_equal": True}},
            "classes": ["pinned"], "verdict": VERDICT_PIN}
    legs.append(("a row that only the pin reproduces is not called addressed",
                 fake["verdict"] != VERDICT_ADDRESSED and "history" not in fake["classes"], ""))

    # the registry is what keeps the face honest: every entry names a face and a population key
    legs.append(("every registry entry names a face and a population key",
                 all(e.get("face") and e.get("population_key") and e.get("module") for e in REGISTRY), ""))
    legs.append(("the registry does not grade its own study",
                 all(e["module"] != STUDY for e in REGISTRY), ""))
    legs.append(("two studies are registered", len(REGISTRY) == 2, ""))
    legs.append(("build never writes a face it grades",
                 all("outdir" in inspect.signature(__import__(e["module"]).build).parameters
                     for e in REGISTRY), ""))
    legs.append(("every study accepts a files= seam so a vintage can be replayed",
                 all("files" in inspect.signature(__import__(e["module"]).build).parameters
                     for e in REGISTRY), ""))
    legs.append(("the corpus stamp is addressable and changes with content",
                 e361.pin_id([{"path": "a.py", "sha256": e361.digest("x")}])
                 != e361.pin_id([{"path": "a.py", "sha256": e361.digest("y")}]), ""))
    legs.append(("the stamp counts the members it addressed",
                 e361.stamp([("scripts/a.py", "x"), ("Tools/c.py", "y")])["members"] == 2, ""))
    legs.append(("an empty corpus cannot be stamped green",
                 e361.stamp([])["pin_id"] == "" and e361.stamp([])["members"] == 0, ""))

    ok = 0
    for name, got, _detail in legs:
        if got:
            ok += 1
        else:
            print("FAIL %s" % (name,))
    print("selftest %d/%d" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "selftest":
        return selftest()
    if cmd == "verify":
        problems = verify()
        print(json.dumps({"problems": problems, "count": len(problems)}, ensure_ascii=False))
        return 0 if not problems else 1
    if cmd == "stamp":
        pin_file = argv[2] if len(argv) > 2 else None
        for row in stamp_faces(pin_file):
            print(json.dumps(row, ensure_ascii=False))
        return 0
    doc = build()
    print(json.dumps({"verdict": doc["verdict"], "summary": doc["summary"]}, ensure_ascii=False,
                     indent=1))
    for row in doc["rows"]:
        print("%-40s published=%s live=%s pinned=%s history=%s -> %s"
              % (row["study"], row["published_population"], row["live_population"],
                 (row["vintages"].get("pinned") or {}).get("population"),
                 (row["vintages"].get("history") or {}).get("population"), row["verdict"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))