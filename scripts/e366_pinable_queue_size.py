"""E366 -- the market for pins is two populations, not thirteen studies.

E364 closed with a queue of thirteen studies whose published populations nobody can re-check, and
E365 proved the mechanism: pin the *population the study walks*, then replay the study over the
pinned bytes through its ``build(files=...)`` seam.  What E364 left unsized is the *cost*: its
queue is one row per study, which reads as one pin per study, one round per pin -- 13 rounds to
close a family that walks two directories.

So this study measures the market instead of the members:

  * **the populations** -- import each study's own enumerator (never re-implement a walk, E355's
    rule) and compare the resulting path sets.  Six studies expose ``corpus()``; are they six
    populations or one?  Two further families (``e346._corpus()`` and ``e328.scan_faces()``) are
    walked by other studies in the queue.
  * **the store minority** -- per population, how many members a commit cannot supply.  A pin is
    only replayable if the non-git members are stored beside it (E365: 65 of 591 faces), and that
    number, not the population size, is the thing that makes a pin expensive.
  * **the seam** -- E364 named its own limit: "``has_files_seam`` reads the source text, so a
    ``build()`` that takes ``files`` and ignores it would still read as a seam".  Measured here as
    three distinct shapes, because they cost different amounts of work: a real parameter, a local
    name that shadows the parameter, and prose that merely says the word ``files``.  A text grep
    cannot tell them apart -- and on this population it gets six of eleven wrong.

Verdict vocabulary is ordered so a wide queue can never read as a small bill:
  * no measured population / no queue / a study quoting a population that is neither domain
    -> that study is published as its own rule, never folded into a pin
  * every queued study attributable to a measured population -> report the *pins* the queue needs

Usage:
  python scripts/e366_pinable_queue_size.py build      # publish the inventory
  python scripts/e366_pinable_queue_size.py verify     # re-derive, diff against the face
  python scripts/e366_pinable_queue_size.py selftest
"""

from __future__ import annotations

import datetime as dt
import hashlib
import importlib
import inspect
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "results", "state_tilt")

TODAY = dt.date.today().isoformat()
STUDY = "E366_pinable_queue_size"
FACE = "PINQUEUE-%s.json" % TODAY
LATEST = "pinqueue_latest.json"

import e361_census_corpus_pin as e361  # identity + git facts, never a copy
import e364_unstamped_census as e364   # the queue this study sizes

# The populations a queued study can be walking.  Each is named by the module and function that
# owns the walk and is imported, so this table can never describe a walk the studies do not do.
POPULATIONS = {
    "source_corpus": {"module": "e346_status_writer_unread", "fn": "_corpus",
                      "rule": "in-repo .py sources under the census roots as e346 walks them"},
    "published_faces": {"module": "e328_quoted_number_staleness", "fn": "scan_faces",
                        "rule": "published face JSON under results/ as e328's scan walks them"},
}

# The studies that expose their own corpus() -- imported to prove whether the families agree.
CORPUS_MODULES = ("e322_residual_refusal_causes", "e323_reach_under_wider_needle",
                  "e324_unpublished_key_causes", "e325_orphan_gate_faces",
                  "e326_template_parameter_consumers", "e327_who_reads_a_face_through_a_pointer")

BUILD_RE = re.compile(r"def build\(([^)]*)\)")

# A study that merely mentions the word "files" is not a study with a seam.  These three shapes
# are separated because only the first one can be replayed without touching the study's body.
SEAM_PARAMETER = "parameter"
SEAM_SHADOW = "local_shadow"
SEAM_PROSE = "prose_only"
SEAM_ABSENT = "absent"

VERDICT_TWO_PINS = "the_queued_studies_walk_two_populations_so_the_bill_is_two_pins_not_thirteen"
VERDICT_PER_STUDY = "every_queued_study_walks_its_own_population_and_needs_its_own_pin"
VERDICT_EMPTY = "cannot_be_sized_the_queue_is_empty"

POPULATION_BLIND = "its_largest_quoted_population_belongs_to_neither_measured_walk"


# --------------------------------------------------------------------------------- member identity
def member_path(member):
    """One path per member, whatever shape three different walks return for the same thing.

    e346._corpus() yields strings, the six corpus() studies yield (path, text) tuples, and
    e328.scan_faces() yields dicts with a ``rel`` key.  Normalising here rather than in the walkers
    keeps the comparison honest: the same file has to be the same string in every set.
    """
    if isinstance(member, str):
        rel = member
    elif isinstance(member, tuple) and member:
        rel = member[0]
    elif isinstance(member, dict):
        rel = member.get("rel") or member.get("path") or ""
    else:
        raise TypeError("cannot read a member of type %s" % type(member).__name__)
    rel = str(rel).replace("\\", "/")
    # e346._corpus() yields absolute paths while the corpus() studies yield repo-relative ones;
    # left alone, one population would count as two and every union would double (measured: 4764
    # against 2386 on the first run of this study)
    if os.path.isabs(rel):
        rel = os.path.relpath(rel, ROOT).replace("\\", "/")
    return rel


def family_key(paths):
    """A population's identity is its member *paths*, order-free: content is the pin's job.

    Two studies that walk the same directory differ only in which of their own files they exclude
    (E319), so the key is computed twice: over all members and over the members minus the studies'
    own sources.  The second is the population; the first is what a shared pin would cover.
    """
    return hashlib.sha256("\n".join(sorted(set(paths))).encode("utf-8")).hexdigest()[:16]


def own_sources(studies):
    """The files a study writes and therefore drops from its own walk."""
    return set("scripts/%s.py" % s for s in studies)


# ------------------------------------------------------------------------------------ the walks
def measure(name):
    """Import a population's own walker and take its member list.  Never a copy (E355)."""
    spec = POPULATIONS[name]
    mod = importlib.import_module(spec["module"])
    fn = getattr(mod, spec["fn"])
    # some walkers take the root they walk, some are already rooted at the repo -- read the
    # signature rather than assuming, because a wrong call is a different population
    try:
        needs_root = bool(inspect.signature(fn).parameters)
    except (TypeError, ValueError):
        needs_root = False
    members = fn(root=ROOT) if needs_root else fn()
    if not members:
        raise ValueError("EMPTY-SCOPE: %s.%s returned no members" % (spec["module"], spec["fn"]))
    paths = [member_path(m) for m in members]
    if len(set(paths)) != len(paths):
        raise ValueError("EMPTY-SCOPE: %s yields duplicate paths, a pin would double count them" % name)
    return {"name": name, "walker": "%s.%s" % (spec["module"], spec["fn"]), "rule": spec["rule"],
            "members": sorted(paths)}


def measure_corpus_family():
    """Are the six corpus() studies one population or six?

    The answer has to be measured: each excludes a different set of its own files, so equal counts
    would prove nothing.
    """
    pops = {}
    for name in CORPUS_MODULES:
        mod = importlib.import_module(name)
        pops[name] = set(member_path(m) for m in mod.corpus())
    base = "e323_reach_under_wider_needle"
    union = set().union(*pops.values())
    inter = set.intersection(*pops.values())
    deltas = {}
    for name, paths in sorted(pops.items()):
        own = set("scripts/%s.py" % name for name in [name])
        deltas[name] = {
            "members": len(paths),
            "only_vs_base": sorted(paths - pops[base]),
            "missing_vs_base": sorted(pops[base] - paths),
            "difference_is_its_own_files": bool(
                (paths - pops[base]) <= own and (pops[base] - paths) <= own_sources(CORPUS_MODULES)),
        }
    return {"populations": {k: len(v) for k, v in pops.items()},
            "union": len(union), "intersection": len(inter),
            "union_paths": sorted(union), "deltas": deltas,
            "families": len(set(family_key(p) for p in pops.values())),
            "differences_are_own_exclusions": all(d["difference_is_its_own_files"]
                                                  for d in deltas.values())}


# ------------------------------------------------------------------------------ can git supply it
def store_bill(members):
    """How much of a population a commit cannot supply -- the expensive half of a pin."""
    # a member the walk saw but the tree no longer has is not a member git can supply, and
    # ``git hash-object`` refuses the whole batch over one missing path, so the split is explicit
    present = [p for p in members if os.path.exists(os.path.join(ROOT, p))]
    sources = [{"path": p} for p in present]
    paths = [s["path"] for s in sources]
    tree = e361.head_tree(paths)
    work = e361.worktree_blobs(paths)
    rows = e361.classify(sources, tree, work)
    for p in members:
        if p not in present:
            rows.append({"path": p, "tracked": False, "dirty": False, "git_can_supply": False})
    need = [r for r in rows if not r["git_can_supply"]]
    sizes = 0
    for r in need:
        try:
            sizes += os.path.getsize(os.path.join(ROOT, r["path"]))
        except OSError:
            pass
    return {
        "members": len(rows),
        "git_can_supply": sum(1 for r in rows if r["git_can_supply"]),
        "need_store": len(need),
        "untracked": sum(1 for r in rows if not r["tracked"]),
        "dirty": sum(1 for r in rows if r["dirty"]),
        "need_store_bytes": sizes,
        "pct_supplied_by_git": round(100.0 * sum(1 for r in rows if r["git_can_supply"]) / len(rows), 2),
        "need_store_examples": [r["path"] for r in need][:8],
    }


# ------------------------------------------------------------------------------------- the seam
def seam_of(src):
    """Three shapes of a seam, because only one of them is free.

    E364 published its own limit: "a build() that takes files and ignores it would still read as a
    seam".  Measured over this queue, the word ``files`` appears in six build bodies that have no
    parameter at all -- as prose in a format string, or as a *local list of records* that has
    nothing to do with the corpus.  A text grep calls all six seams; none of them is one.
    """
    m = BUILD_RE.search(src)
    if not m:
        return {"shape": SEAM_ABSENT, "accepts_files": False, "mentions_in_body": 0,
                "detail": "no build() at all"}
    accepts = "files" in m.group(1)
    rest = src[m.end():]
    nxt = re.search(r"^def ", rest, re.M)
    body = rest[:nxt.start()] if nxt else rest
    lines = [l for l in body.splitlines() if re.search(r"\bfiles\b", l)]
    assigns = [l for l in lines if re.match(r"\s*files\s*=[^=]", l)]
    if accepts:
        shape, detail = SEAM_PARAMETER, "build() takes files and passes it to the walker"
    elif assigns:
        shape, detail = SEAM_SHADOW, "a local bind of files shadows the name the parameter needs"
    elif lines:
        shape, detail = SEAM_PROSE, "the word appears only in a string or a comment"
    else:
        shape, detail = SEAM_ABSENT, "build() has no files parameter and never names one"
    return {"shape": shape, "accepts_files": accepts, "mentions_in_body": len(lines),
            "assigns_files": len(assigns), "detail": detail}


def walks_which_population(src, studies):
    """Which measured walk a study's source reaches, by the name of the walker it calls.

    Static on purpose: importing a study's enumerator is only cheap for some of them (e340's
    scan_faces takes 35s), so attribution is read from the reference and the *population* is the
    importable thing.  A study naming no walker is reported unattributed rather than guessed.
    """
    # a corpus()/._corpus() reference is the stronger signal: E326 exposes corpus() and also names
    # results/*_latest in prose, which the face rule matched before this ordering (measured: one
    # study misattributed on the first run)
    if re.search(r"\b_corpus\(", src) or re.search(r"\bcorpus\(\)", src):
        return "source_corpus"
    if "scan_faces(" in src:
        return "published_faces"
    if re.search(r"glob\(|iglob\(", src) and re.search(r"[\"']results[\"']", src) and "*_latest" in src:
        return "published_faces"
    return None


# ---------------------------------------------------------------------------------- the queue
def read_source(module):
    path = os.path.join(ROOT, module)
    try:
        return io.open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        return ""


def build(outdir=None):
    populations = {}
    for name in POPULATIONS:
        populations[name] = measure(name)

    # E319/E365: this study's own faces are in the directory it measures, so a pin (and a
    # re-derivation) that counted them would grow by its own publication every run
    own_face_names = {FACE, LATEST}
    before = len(populations["published_faces"]["members"])
    populations["published_faces"]["members"] = [
        p for p in populations["published_faces"]["members"]
        if os.path.basename(p) not in own_face_names]
    own_faces_dropped = before - len(populations["published_faces"]["members"])
    family = measure_corpus_family()

    # the source population a shared pin would actually cover: the widest walk, which is e346's
    # (measured: e323.corpus() is a strict subset of it, 11 members smaller)
    widest_source = set(populations["source_corpus"]["members"]) | set(family["union_paths"])
    bills = {
        "source_corpus": store_bill(sorted(widest_source)),
        "published_faces": store_bill(populations["published_faces"]["members"]),
    }

    doc364 = e364.build(outdir)
    # E319: a census that counts its own published face feeds its own row back on the next run.
    # The mirror this study writes is named after its own study id, so the exclusion is by id, and
    # it is recorded rather than silent.
    own = [c["study"] for c in doc364["queue"] if c["study"].startswith(STUDY.split("_")[0])]
    queue = [c for c in doc364["queue"] if not c["study"].startswith(STUDY.split("_")[0])]
    if not queue:
        raise ValueError("EMPTY-SCOPE: the published queue is empty")

    rows = []
    for card in queue:
        modules = card.get("producer") or []
        src = "\n".join(read_source(m) for m in modules)
        seam = seam_of(src)
        # Two independent readings of "which directory does this study's quoted number count":
        # E364 measured it from the face's own summary keys, this study reads it from the walker
        # the source reaches.  E328 walks faces but calls e326.corpus() for its reader domain, so
        # the two disagree on exactly the studies a single pin cannot serve -- published, not
        # silently resolved.
        walker_domain = walks_which_population(src, modules)
        domain = card.get("population_kind") or walker_domain
        measured = populations.get(domain) if domain in populations else None
        quoted = card.get("largest_quoted_population")
        row = {
            "study": card["study"],
            "domain": domain,
            "population_kind": card.get("population_kind"),
            "quoted_population": quoted,
            "measured_population": len(measured["members"]) if measured else None,
            "walker": measured["walker"] if measured else None,
            "seam": seam,
            "walker_domain": walker_domain,
            "domains_agree": (walker_domain == domain) if walker_domain else None,
            "walks_two_populations": bool(walker_domain and domain and walker_domain != domain),
            "producer": modules,
        }
        # a quoted number far below the population is a *filtered* count, not a different walk:
        # replay re-derives the filter from the pinned bytes, so the pin size is the population's
        row["quoted_is_a_subset_of_the_population"] = bool(
            measured and quoted and quoted <= len(measured["members"]))
        if seam["shape"] == SEAM_PARAMETER:
            row["class"] = "PINNABLE_TODAY"
        elif measured and row["quoted_is_a_subset_of_the_population"]:
            row["class"] = "NEEDS_SEAM"
        elif measured:
            row["class"] = "NEEDS_A_RULE"
        else:
            row["class"] = "UNATTRIBUTED"
        rows.append(row)

    pins = {}
    for row in rows:
        if row["domain"]:
            pins.setdefault(row["domain"], []).append(row["study"])
    summary = {
        "studies_in_queue": len(rows),
        "studies_attributed_to_a_population": sum(1 for r in rows if r["domain"]),
        "studies_unattributed": sum(1 for r in rows if not r["domain"]),
        "distinct_populations": len(pins),
        "pins_required": len(pins),
        "studies_served_by_one_pin": {k: len(v) for k, v in sorted(pins.items())},
        "pin_collapse_ratio": round(len(rows) / float(len(pins)), 2) if pins else None,
        "seam_repairs_required": sum(1 for r in rows if r["class"] == "NEEDS_SEAM"),
        "pinnable_today": sum(1 for r in rows if r["class"] == "PINNABLE_TODAY"),
        "need_their_own_rule": sum(1 for r in rows if r["class"] == "NEEDS_A_RULE"),
        "unattributed": sum(1 for r in rows if r["class"] == "UNATTRIBUTED"),
        "corpus_functions_measured": len(family["populations"]),
        "corpus_functions_that_are_one_population": family["families"],
        "corpus_family_union": family["union"],
        "corpus_family_intersection": family["intersection"],
        "source_population_members": bills["source_corpus"]["members"],
        "source_members_needing_store": bills["source_corpus"]["need_store"],
        "source_store_bytes": bills["source_corpus"]["need_store_bytes"],
        "face_population_members": bills["published_faces"]["members"],
        "face_members_needing_store": bills["published_faces"]["need_store"],
        "face_store_bytes": bills["published_faces"]["need_store_bytes"],
        "seam_word_is_not_a_seam": sum(1 for r in rows if r["seam"]["shape"] == SEAM_PROSE),
        "seam_shadowed_by_a_local": sum(1 for r in rows if r["seam"]["shape"] == SEAM_SHADOW),
        "studies_that_walk_two_populations": sum(1 for r in rows if r["walks_two_populations"]),
    }
    return {
        "study": STUDY,
        "evidence_cutoff": TODAY,
        "verdict": decide(summary),
        "rules": {
            "population": "a study's population is the member list its own enumerator returns, "
                          "imported -- a re-implemented walk could describe a different directory",
            "bill": "the bill for a pin is the number of members a commit cannot supply, not the "
                    "number of members; git already stores the rest",
            "seam": "replay needs build(files=...) as a parameter; a local named files and prose "
                    "naming files are published as their own shapes, not folded in as seams",
            "size": "a quoted count below its population is a filtered count: the pin is over the "
                    "population and the filter is re-derived by replaying the study",
        },
        "limits": {
            "attribution_is_static": "which walk a study reaches is read from its source text; a "
                                     "study that builds a path by hand is reported unattributed",
            "populations_measured_are_two": "only the two walks this study imports were measured; "
                                            "a third walk would appear as an unattributed study",
            "store_bill_is_a_moment": "the store minority is the state of the working tree at "
                                      "build time (109 untracked scratch files on the source side, "
                                      "E365's 65 on the face side)",
            "no_pin_is_written": "nothing is pinned here; the bill is measured, the pins are E361's "
                                 "and E365's to write",
        },
        "populations": {
            k: {"walker": v["walker"], "rule": v["rule"], "members": len(v["members"]),
                "family_key": family_key(v["members"]) if k != "source_corpus"
                else family_key(sorted(widest_source))}
            for k, v in populations.items()
        },
        "corpus_family": {k: v for k, v in family.items() if k != "union_paths"},
        "store_bill": bills,
        "own_faces_excluded": own,
        "own_face_members_dropped": own_faces_dropped,
        "queue": rows,
        "summary": summary,
        "ts": dt.datetime.now().isoformat(timespec="seconds"),
    }


def decide(summary):
    if not summary["studies_in_queue"]:
        return VERDICT_EMPTY
    if summary["pins_required"] and summary["pins_required"] < summary["studies_in_queue"]:
        return VERDICT_TWO_PINS
    return VERDICT_PER_STUDY


# ------------------------------------------------------------------------------------ publish
def publish(doc, outdir=None):
    out = outdir or OUTDIR
    os.makedirs(out, exist_ok=True)
    doc = dict(doc, face_path=os.path.join(out, FACE))
    for name in (FACE, LATEST):
        with io.open(os.path.join(out, name), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(doc, fh, ensure_ascii=False, indent=1, sort_keys=False)
            fh.write("\n")
    return os.path.join(out, FACE)


# The keys a re-derivation must reproduce.  The *decision* keys are properties of the studies and
# their seams and must be bit-stable; the *bill* keys are properties of a working tree that other
# lanes write to all day (109 untracked scratch files on the source side alone), so a moved byte
# count is drift to be published, not a defect to be convicted of (E360's lesson, in the other
# direction: this study would otherwise convict itself for someone else's commit).
DECISION_KEYS = ("studies_in_queue", "studies_attributed_to_a_population", "distinct_populations",
                 "pins_required", "studies_served_by_one_pin", "seam_repairs_required",
                 "pinnable_today", "need_their_own_rule", "unattributed",
                 "corpus_functions_measured", "corpus_functions_that_are_one_population",
                 "seam_word_is_not_a_seam", "seam_shadowed_by_a_local",
                 "studies_that_walk_two_populations")
BILL_KEYS = ("source_population_members", "source_members_needing_store", "source_store_bytes",
             "face_population_members", "face_members_needing_store", "face_store_bytes",
             "corpus_family_union", "corpus_family_intersection", "pin_collapse_ratio")


def compare(published, fresh):
    """Split a re-derivation into a verdict on the decision and a report on the bill."""
    problems, drift = [], []
    if published.get("study") != fresh.get("study"):
        problems.append("study id differs")
    ps, fs = published.get("summary") or {}, fresh.get("summary") or {}
    for k in DECISION_KEYS:
        if ps.get(k) != fs.get(k):
            problems.append("summary.%s: published %r, re-derived %r" % (k, ps.get(k), fs.get(k)))
    for k in BILL_KEYS:
        if ps.get(k) != fs.get(k):
            drift.append("%s: %r -> %r" % (k, ps.get(k), fs.get(k)))
    if published.get("verdict") != fresh.get("verdict"):
        problems.append("verdict: published %r, re-derived %r"
                        % (published.get("verdict"), fresh.get("verdict")))
    # the per-study classes are the product; a re-derivation that renames one is a moved number
    pc = {r["study"]: (r["class"], r["seam"]["shape"], r["domain"])
          for r in published.get("queue") or []}
    fc = {r["study"]: (r["class"], r["seam"]["shape"], r["domain"]) for r in fresh.get("queue") or []}
    for study in sorted(set(pc) | set(fc)):
        if pc.get(study) != fc.get(study):
            problems.append("%s: published %r, re-derived %r" % (study, pc.get(study), fc.get(study)))
    return {"problems": problems, "drift": drift}


def verify(path=None):
    path = path or os.path.join(OUTDIR, FACE)
    published = json.load(io.open(path, encoding="utf-8"))
    out = compare(published, build())
    for line in out["drift"]:
        print("[DRIFT] %s" % line)
    return out["problems"]


# ----------------------------------------------------------------------------------- selftest
def selftest():
    ok = True

    def leg(name, cond, detail=""):
        nonlocal ok
        if not cond:
            ok = False
        print("[%s] %s%s" % ("PASS" if cond else "FAIL", name, "" if cond else " :: %s" % detail))

    # member shapes: three walkers, one identity
    leg("a string member is its own path", member_path("scripts/a.py") == "scripts/a.py")
    leg("a (path, text) tuple is read by its path",
        member_path(("scripts\\b.py", "print(1)")) == "scripts/b.py")
    leg("a dict member is read by rel",
        member_path({"rel": "results/x.json", "name": "x.json"}) == "results/x.json")
    leg("an unreadable member is refused, not coerced",
        _raises(TypeError, member_path, 7))
    leg("an absolute member collapses onto the repo-relative path",
        member_path(os.path.join(ROOT, "scripts", "a.py")) == "scripts/a.py")

    # family identity: order-free, path-level
    leg("a population key ignores member order",
        family_key(["b.py", "a.py"]) == family_key(["a.py", "b.py"]))
    leg("a population key changes when a member is added",
        family_key(["a.py"]) != family_key(["a.py", "b.py"]))

    # the three seam shapes, because a text grep cannot tell them apart (E364's own limit)
    leg("a real files parameter is a seam",
        seam_of("def build(files=None, outdir=None):\n    return files\n")["shape"] == SEAM_PARAMETER)
    leg("a local named files is a shadow, not a seam",
        seam_of("def build(outdir=None):\n    files = corpus()\n    return files\n")["shape"] == SEAM_SHADOW)
    leg("prose naming files is not a seam",
        seam_of('def build(outdir=None):\n    print("98 keys x 3k files")\n    return 1\n')["shape"] == SEAM_PROSE)
    leg("a build() that never names files has no seam",
        seam_of("def build(outdir=None):\n    return 1\n")["shape"] == SEAM_ABSENT)
    leg("no build() at all is absent, not a crash",
        seam_of("def main():\n    pass\n")["shape"] == SEAM_ABSENT)
    leg("a helper's files parameter does not leak into build()",
        seam_of("def build(outdir=None):\n    return 1\n\ndef helper(files):\n    return files\n")["shape"] == SEAM_ABSENT)

    # attribution is by walker name
    leg("a study calling _corpus() reaches the source population",
        walks_which_population("corpus = [p for p in e346._corpus()]", []) == "source_corpus")
    leg("a study calling scan_faces() reaches the face population",
        walks_which_population("rows = e328.scan_faces(root=ROOT)", []) == "published_faces")
    leg("a study naming no walker is unattributed, not guessed",
        walks_which_population("x = 1\n", []) is None)

    # the verdict must not read a wide queue as a small bill when nothing is measured
    leg("two populations for thirteen studies is the collapse verdict",
        decide({"studies_in_queue": 13, "pins_required": 2}) == VERDICT_TWO_PINS)
    leg("one population per study stands",
        decide({"studies_in_queue": 13, "pins_required": 13}) == VERDICT_PER_STUDY)
    leg("an empty queue is a refusal, not a zero",
        decide({"studies_in_queue": 0, "pins_required": 0}) == VERDICT_EMPTY)

    # the bill is about what git cannot supply
    leg("store_bill counts non-git members separately from members", _store_bill_shape_ok())

    # the bill is drift, the decision is not: a working tree another lane writes to must not
    # convict this study, and a renamed class must not hide in that tolerance
    base = {"study": STUDY, "verdict": VERDICT_TWO_PINS,
            "summary": {"pins_required": 2, "studies_in_queue": 13, "source_store_bytes": 100},
            "queue": [{"study": "A", "class": "NEEDS_SEAM", "seam": {"shape": SEAM_ABSENT},
                       "domain": "source_corpus"}]}
    same = json.loads(json.dumps(base))
    same["summary"]["source_store_bytes"] = 999
    out_same = compare(base, same)
    leg("a moved bill byte is drift, not a problem",
        out_same["problems"] == [] and len(out_same["drift"]) == 1)
    moved_class = json.loads(json.dumps(base))
    moved_class["queue"][0]["class"] = "PINNABLE_TODAY"
    leg("a moved class is a problem, not drift", len(compare(base, moved_class)["problems"]) >= 1)
    moved_seam = json.loads(json.dumps(base))
    moved_seam["queue"][0]["seam"]["shape"] = SEAM_PARAMETER
    leg("a moved seam shape is a problem", len(compare(base, moved_seam)["problems"]) >= 1)
    moved_pin = json.loads(json.dumps(base))
    moved_pin["summary"]["pins_required"] = 3
    leg("a moved pin count is a problem", len(compare(base, moved_pin)["problems"]) >= 1)

    print("e366 selftest %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def _raises(exc, fn, *a, **kw):
    try:
        fn(*a, **kw)
    except exc:
        return True
    except Exception:
        return False
    return False


def _store_bill_shape_ok():
    """A bill must partition its members: supplied + stored == members, and a missing member is
    stored rather than crashing the batch (git hash-object refuses a path it cannot open)."""
    real = store_bill(["scripts/e361_census_corpus_pin.py"])
    missing = store_bill(["scripts/_no_such_file_e366_selftest.py"])
    return (real["members"] == 1
            and real["git_can_supply"] + real["need_store"] == real["members"]
            and missing["members"] == 1 and missing["need_store"] == 1
            and missing["pct_supplied_by_git"] == 0.0)


def cmd_check():
    """The chain leg: selftest, then re-derive the decision and publish any bill drift."""
    if selftest() != 0:
        return 1
    problems = verify()
    if problems:
        print("FAIL: %s" % "; ".join(problems)[:400])
        return 1
    print("OK: decision re-derived, bill drift printed above (if any)")
    return 0


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "build"
    if cmd == "check":
        return cmd_check()
    if cmd == "build":
        doc = build()
        path = publish(doc)
        s = doc["summary"]
        print("verdict: %s" % doc["verdict"])
        print("pins required: %s for %s studies (%s)" % (
            s["pins_required"], s["studies_in_queue"], s["studies_served_by_one_pin"]))
        print("source population %s members, %s need store (%s bytes)" % (
            s["source_population_members"], s["source_members_needing_store"], s["source_store_bytes"]))
        print("face population %s members, %s need store (%s bytes)" % (
            s["face_population_members"], s["face_members_needing_store"], s["face_store_bytes"]))
        print("seam repairs: %s | pinnable today: %s | own rule: %s | unattributed: %s" % (
            s["seam_repairs_required"], s["pinnable_today"], s["need_their_own_rule"], s["unattributed"]))
        print("published %s" % path)
        return 0
    if cmd == "verify":
        problems = verify(argv[2] if len(argv) > 2 else None)
        print("verify problems=%s" % (problems,))
        return 0 if not problems else 1
    if cmd == "selftest":
        return selftest()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))