"""E399 -- which published keys name no file, and would a wider index find it?

E397 resolved the whole published key population and published
``names_resolved_to_no_file = 98`` as a bare residual.  A count of names that resolve to nothing is
not a claim about the instrument until you ask *why* each one resolves to nothing, because "no file"
has several different meanings:

  * the file exists but the resolver's index skips its tree (E383's ``SKIP_DIRS`` drops ``Money02``,
    ``legacy``, ``media``, ``.codely-cli``) -- an instrument gap;
  * the name is a template/glob (``FOO-%s.json``) -- never a literal path;
  * the name is a bare token (``arm``) -- never a path;
  * the name is a bare BASENAME (``bad.json``, ``cells.jsonl``) -- a fragment whose directory is
    supplied by a runtime variable at the one site that writes it, so "resolves to no file" is its
    normal state and not a defect;
  * the name is repo-relative and names an absent file -- a real attrition claim, split further by
    whether its directory exists, and by whether the "directory" is in fact a FILE;
  * the name is a directory, an absolute path outside the repo, or a deletion in git history.

So the study runs these arms over every unresolved name:

  A0  the baseline resolver actually in use (``e383._resolve`` with ``SKIP_DIRS``);
  A1  a wider index -- same suffix rule, only ``.git``/``__pycache__`` skipped;
  A2  git history -- off by default and published as unavailable when it cannot run (this clone is a
      promisor/partial clone: any history walk starts a lazy fetch and wedges, r1224 family);
  A3  form -- repo-relative path vs bare basename vs bare token vs template;
  A4  neighbourhood -- for a repo-relative absence: does the directory exist, does the parent path
      exist as a FILE (a join that can never produce a face), and is there a same-stem sibling under
      another date (the "date-shifted republish" hypothesis)?

The bill is the per-name class list, not a count.  No published face, pointer or key is edited.

Usage:
  python scripts/e399_unresolved_names.py run       # build the face
  python scripts/e399_unresolved_names.py verify    # re-derive every row from the tree
  python scripts/e399_unresolved_names.py selftest  # offline fixture legs
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e383_shared_key_collision as e383  # noqa: E402
import e397_walk_ambiguity as e397  # noqa: E402

TODAY = "2026-11-04"
FACE = "UNRESOLVED-%s.json" % TODAY
LATEST = "unresolved_latest.json"
PUBLISHED_DIR = os.path.join(ROOT, "results", "state_tilt")
STUDY = "E399_unresolved_names"
SELF_REL = "scripts/e399_unresolved_names.py"
SIBLING_FACE = "WALKAMBIG-2026-11-03.json"

WIDE_SKIP = frozenset((".git", "__pycache__"))
NARROW_SKIP = tuple(sorted(e383.SKIP_DIRS))

CL_WIDER = "found_by_an_index_that_does_not_skip_a_tree"
CL_HISTORY = "absent_from_disk_but_git_history_records_a_deletion"
CL_TEMPLATE = "template_or_glob_not_a_literal_path"
CL_ABSOLUTE = "absolute_path_outside_the_repo_and_absent"
CL_DIRECTORY = "names_a_directory_not_a_file"
CL_NOT_PATH = "bare_token_not_shaped_like_a_path"
CL_FRAGMENT = "bare_basename_whose_directory_is_a_runtime_variable"
CL_DIR_IS_A_FILE = "repo_relative_but_its_directory_path_is_a_file"
CL_ABSENT_DIR = "repo_relative_and_its_directory_does_not_exist"
CL_ABSENT = "repo_relative_inside_an_existing_directory_but_no_file"

CLASSES = (CL_WIDER, CL_HISTORY, CL_TEMPLATE, CL_ABSOLUTE, CL_DIRECTORY, CL_NOT_PATH,
           CL_FRAGMENT, CL_DIR_IS_A_FILE, CL_ABSENT_DIR, CL_ABSENT)

TEMPLATE_META = ("%s", "{", "}", "*", "?", "<", ">", "$", "+")
PATH_EXT = (".json", ".jsonl", ".csv", ".parquet", ".md", ".py", ".txt", ".log", ".html", ".js")
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")

V_INSTRUMENT = ("every_unresolved_name_is_found_by_an_index_that_does_not_skip_a_tree_so_the_"
                "residual_is_the_instruments_skip_list")
V_NOT_A_PATH = ("every_unresolved_name_is_a_template_a_token_or_a_bare_basename_fragment_so_no_"
                "published_face_is_missing_and_the_key_population_is_inflated_by_fragments")
V_ABSENT = ("every_unresolved_name_is_a_repo_relative_path_naming_an_absent_file_inside_a_"
            "directory_that_exists_so_the_residual_is_attrition_of_published_faces")
V_HISTORY = ("every_unresolved_name_is_a_file_that_history_records_as_deleted_so_the_residual_is_"
             "attrition_not_an_index_gap")
V_MIXED = ("the_unresolved_names_split_across_instrument_fragments_and_real_absences_so_the_"
           "residual_is_several_bills_and_must_be_published_per_class")
V_UNMEASURED = ("the_residual_is_classified_but_the_deletion_arm_could_not_run_on_this_partial_"
                "clone_so_the_absences_inside_existing_directories_stay_unattributed")
V_EMPTY = "no_published_key_resolved_to_nothing_so_there_is_no_residual_to_price"


def say(message):
    print(message, flush=True)


# --------------------------------------------------------------------------- indexes

_WIDE = None


def _wide_index():
    """``{basename: [posix paths]}`` over the tree minus only ``WIDE_SKIP``."""
    global _WIDE
    if _WIDE is None:
        index = {}
        for dirpath, dirnames, filenames in os.walk(ROOT):
            dirnames[:] = [d for d in dirnames if d not in WIDE_SKIP]
            rel_dir = os.path.relpath(dirpath, ROOT).replace("\\", "/")
            for name in filenames:
                rel = name if rel_dir == "." else rel_dir + "/" + name
                index.setdefault(name, []).append(rel)
        _WIDE = index
    return _WIDE


def wide_resolve(value):
    """Every repo-relative file a folded value names, using the wider index (A1)."""
    v = e383._norm(value)
    if not v:
        return []
    if is_absolute(v):
        path = os.path.normpath(v)
        if not os.path.isfile(path):
            return []
        try:
            return [os.path.relpath(path, ROOT).replace("\\", "/")]
        except ValueError:
            return []
    base = v.rsplit("/", 1)[-1]
    return sorted({rel for rel in _wide_index().get(base, ())
                   if rel == v or rel.endswith("/" + v)})


def deleted_paths(timeout=90):
    """Every path git's history records as deleted (A2), in one bounded pass -- off by default.

    This arm is OFF and that is a measurement.  ``--all`` wedged the round: this repo is a partial
    (promisor) clone, so touching a ref whose trees are not materialised starts a lazy
    ``git fetch``/``index-pack`` that never returns (r1224 family).  Pinning to ``HEAD`` did not
    help -- the same lazy fetch fires and left two orphan fetches behind.  So the arm runs only
    when ``BIGMONEY_E399_HISTORY=1`` is set on a complete clone; otherwise it is published as
    ``available: False`` with the reason, because an arm that did not run must never read as
    "no deletions".
    """
    if os.environ.get("BIGMONEY_E399_HISTORY") != "1":
        return {"available": False,
                "why": ("not attempted: this clone is a promisor/partial clone, so any history walk "
                        "starts a lazy fetch (r1224 family); set BIGMONEY_E399_HISTORY=1 on a "
                        "complete clone to run it"),
                "paths": set()}
    cmd = ["git", "-c", "core.fsmonitor=false", "log", "--diff-filter=D", "--name-only",
           "--pretty=format:", "HEAD"]
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GIT_OPTIONAL_LOCKS="0")
    try:
        out = subprocess.run(cmd, cwd=ROOT, capture_output=True, timeout=timeout, env=env)
    except subprocess.TimeoutExpired:
        return {"available": False, "why": "git log timed out after %ds" % timeout, "paths": set()}
    except OSError as exc:
        return {"available": False, "why": str(exc), "paths": set()}
    if out.returncode != 0:
        return {"available": False, "why": "git log rc=%d" % out.returncode, "paths": set()}
    text = out.stdout.decode("utf-8", "replace")
    paths = {ln.strip().replace("\\", "/") for ln in text.splitlines() if ln.strip()}
    return {"available": True, "why": "", "paths": paths}


def history_hit(norm, paths):
    """The deleted path this name matches, or ``None`` (exact path first, then by suffix)."""
    if not norm:
        return None
    if norm in paths:
        return norm
    tail = "/" + norm
    for p in paths:
        if p.endswith(tail):
            return p
    return None


# --------------------------------------------------------------------------- form (A3)

FORM_REPO_RELATIVE = "repo_relative_path"
FORM_BARE_BASENAME = "bare_basename_fragment"
FORM_BARE_TOKEN = "bare_token"
FORM_TEMPLATE = "template_or_glob"
FORM_ABSOLUTE = "absolute_path"


def is_absolute(value):
    v = (value or "").strip()
    return (len(v) > 1 and v[1] == ":") or v.startswith("/")


def form_of(norm):
    """What kind of thing the string is, before asking whether a file answers to it."""
    if not norm:
        return FORM_BARE_TOKEN
    if any(meta in norm for meta in TEMPLATE_META):
        return FORM_TEMPLATE
    if is_absolute(norm):
        return FORM_ABSOLUTE
    if "/" in norm:
        return FORM_REPO_RELATIVE
    if norm.lower().endswith(PATH_EXT):
        return FORM_BARE_BASENAME
    return FORM_BARE_TOKEN


def neighbourhood(norm):
    """A4: facts about where a repo-relative absence would have lived."""
    facts = {"parent_exists": False, "parent_is_a_file": False,
             "same_stem_other_date": [], "parent_dir": None}
    if not norm or "/" not in norm:
        return facts
    parent = norm.rsplit("/", 1)[0]
    facts["parent_dir"] = parent
    target = os.path.join(ROOT, parent.replace("/", os.sep))
    facts["parent_exists"] = os.path.isdir(target)
    facts["parent_is_a_file"] = os.path.isfile(target)
    stem = norm.rsplit("/", 1)[-1]
    bare = DATE_RE.sub("", stem)
    if facts["parent_exists"] and bare != stem:
        try:
            names = os.listdir(target)
        except OSError:
            names = []
        for cand in names:
            if DATE_RE.sub("", cand) == bare and cand != stem:
                facts["same_stem_other_date"].append(cand)
    return facts


# --------------------------------------------------------------------------- classification

def classify_unresolved(facts):
    """One class per unresolved name, from facts only (pure: the selftest drives it directly).

    ``facts`` keys: ``norm``, ``wide_files``, ``history_path``, ``is_directory``, ``form``,
    ``parent_exists``, ``parent_is_a_file``.  Order is the bill order: an index that could see the
    file beats everything (the name was always a file and only the instrument was narrow), and a
    string that is not a path claim at all beats any statement about absent files.
    """
    if facts.get("wide_files"):
        return CL_WIDER
    if facts.get("history_path"):
        return CL_HISTORY
    form = facts.get("form")
    if form == FORM_ABSOLUTE:
        return CL_ABSOLUTE
    if facts.get("is_directory"):
        return CL_DIRECTORY
    if form == FORM_TEMPLATE:
        return CL_TEMPLATE
    if form == FORM_BARE_TOKEN:
        return CL_NOT_PATH
    if form == FORM_BARE_BASENAME:
        return CL_FRAGMENT
    if facts.get("parent_is_a_file"):
        return CL_DIR_IS_A_FILE
    if not facts.get("parent_exists"):
        return CL_ABSENT_DIR
    return CL_ABSENT


def hidden_by_trees(files):
    """Which of the trees the baseline index skips hold these files."""
    tops = {}
    for f in files:
        parts = [p for p in f.replace("\\", "/").split("/") if p]
        if not parts:
            continue
        for skip in NARROW_SKIP:
            if skip in parts[:-1]:
                tops[skip] = tops.get(skip, 0) + 1
                break
    return tops


def name_row(key, history):
    norm = e383._norm(key or "")
    base_files = e383._resolve(norm)
    wide_files = wide_resolve(norm)
    hist = history_hit(norm, history["paths"]) if history["available"] else None
    form = form_of(norm)
    nb = neighbourhood(norm) if form == FORM_REPO_RELATIVE else {
        "parent_exists": False, "parent_is_a_file": False, "same_stem_other_date": [],
        "parent_dir": None}
    target = os.path.join(ROOT, norm.replace("/", os.sep)) if norm else ""
    is_dir = bool(norm) and os.path.isdir(target)
    facts = {
        "norm": norm,
        "wide_files": wide_files,
        "history_path": hist,
        "is_directory": is_dir,
        "form": form,
        "parent_exists": nb["parent_exists"],
        "parent_is_a_file": nb["parent_is_a_file"],
    }
    row = {
        "key": key,
        "norm": norm,
        "form": form,
        "n_files_baseline": len(base_files),
        "n_files_wider": len(wide_files),
        "wide_files": wide_files[:4],
        "history_path": hist,
        "history_arm_ran": history["available"],
        "is_directory": is_dir,
        "parent_dir": nb["parent_dir"],
        "parent_exists": nb["parent_exists"],
        "parent_is_a_file": nb["parent_is_a_file"],
        "same_stem_other_date": nb["same_stem_other_date"][:4],
        "class": classify_unresolved(facts),
    }
    if wide_files:
        row["hidden_by"] = hidden_by_trees(wide_files)
    return row


def decide(summary):
    """The verdict is recomputed from the summary, never written by hand."""
    unresolved = summary.get("names_resolving_to_no_file") or 0
    if not unresolved:
        return V_EMPTY
    by_class = summary.get("by_class") or {}

    def n(klass):
        return by_class.get(klass, 0)

    if n(CL_WIDER) == unresolved:
        return V_INSTRUMENT
    not_a_path = n(CL_TEMPLATE) + n(CL_NOT_PATH) + n(CL_FRAGMENT) + n(CL_ABSOLUTE) + n(CL_DIRECTORY)
    if n(CL_WIDER) == 0 and not_a_path == unresolved:
        return V_NOT_A_PATH
    if not summary.get("history_arm_available") and n(CL_ABSENT):
        return V_UNMEASURED
    if n(CL_ABSENT) == unresolved:
        return V_ABSENT
    if n(CL_HISTORY) == unresolved:
        return V_HISTORY
    return V_MIXED


def sibling_check(rows):
    """Compare the residual with E397's published count on its own cutoff (r1225 family)."""
    path = os.path.join(PUBLISHED_DIR, SIBLING_FACE)
    if not os.path.exists(path):
        return {"available": False, "why": "sibling face %s is absent" % SIBLING_FACE}
    with open(path, "r", encoding="utf-8") as fh:
        sib = json.load(fh)
    published = ((sib.get("summary") or {}).get("names_resolved_to_no_file"))
    return {
        "available": True,
        "sibling": SIBLING_FACE,
        "same_cutoff": sib.get("evidence_cutoff") == TODAY,
        "published_unresolved": published,
        "recomputed_unresolved": len(rows),
        "agree": published == len(rows),
    }


# --------------------------------------------------------------------------- build / verify

def build(write_face=True, sources=None):
    say("resolving the published key population")
    pop = e397.population(sources)
    keys = pop["keys"]
    say("keys=%d (read half %d, write-only %d)"
        % (len(keys), len(pop["read_half"]), len(pop["write_only"])))

    history = deleted_paths()
    say("history arm: available=%s deleted_paths=%d"
        % (history["available"], len(history["paths"])))

    rows = [name_row(k, history) for k in keys]
    resolved = [r for r in rows if r["n_files_baseline"] > 0]
    unresolved = [r for r in rows if r["n_files_baseline"] == 0]
    say("names_resolving_to_no_file=%d" % len(unresolved))

    by_class = {}
    for row in unresolved:
        by_class[row["class"]] = by_class.get(row["class"], 0) + 1
    by_form = {}
    for row in unresolved:
        by_form[row["form"]] = by_form.get(row["form"], 0) + 1

    hidden = {}
    for row in unresolved:
        for top, count in (row.get("hidden_by") or {}).items():
            hidden[top] = hidden.get(top, 0) + count

    dated = [r["norm"] for r in unresolved if r.get("same_stem_other_date")]

    def n(klass):
        return by_class.get(klass, 0)

    summary = {
        "keys_total": len(rows),
        "keys_read_half": len(pop["read_half"]),
        "keys_write_only": len(pop["write_only"]),
        "names_resolving_to_no_file": len(unresolved),
        "names_resolved_to_one_or_more_files": len(resolved),
        "names_found_by_a_wider_index": n(CL_WIDER),
        "names_found_only_in_git_history": n(CL_HISTORY),
        "names_that_were_never_path_claims": (n(CL_TEMPLATE) + n(CL_NOT_PATH) + n(CL_FRAGMENT)
                                              + n(CL_ABSOLUTE) + n(CL_DIRECTORY)),
        "names_that_are_basename_fragments_only": n(CL_FRAGMENT),
        "names_that_are_real_repo_relative_absences": (n(CL_ABSENT) + n(CL_ABSENT_DIR)
                                                       + n(CL_DIR_IS_A_FILE)),
        "names_whose_directory_path_is_a_file": n(CL_DIR_IS_A_FILE),
        "names_absent_inside_an_existing_directory": n(CL_ABSENT),
        "names_absent_because_the_directory_does_not_exist": n(CL_ABSENT_DIR),
        "names_with_a_same_stem_sibling_under_another_date": len(dated),
        "by_class": by_class,
        "by_form": by_form,
        "classes_sum_to_the_residual": sum(by_class.values()) == len(unresolved),
        "share_of_population_unresolved": (round(len(unresolved) / len(rows), 4) if rows else None),
        "trees_that_hide_the_names": hidden,
        "history_arm_available": history["available"],
        "history_arm_why": history["why"],
        "history_deleted_paths": len(history["paths"]),
        "corpus_sources": pop.get("sources"),
        "corpus_parsed": pop.get("parsed"),
        "narrow_index_skips": list(NARROW_SKIP),
        "wide_index_skips": sorted(WIDE_SKIP),
    }
    summary["verdict"] = decide(summary)

    face = {
        "study": STUDY,
        "evidence_cutoff": TODAY,
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "source": SELF_REL,
        "arms": {
            "A0_baseline_resolver": {"kind": "suffix index", "skips": list(NARROW_SKIP)},
            "A1_wider_index": {"kind": "suffix index", "skips": sorted(WIDE_SKIP)},
            "A2_git_history": {"kind": "git log --diff-filter=D --name-only", "ran": history["available"],
                               "why": history["why"]},
            "A3_form": {"repo_relative": "has a slash", "bare_basename": "no slash, known extension",
                        "bare_token": "no slash, no extension",
                        "template": list(TEMPLATE_META), "absolute": "drive letter or leading /"},
            "A4_neighbourhood": {"asks": ["parent_exists", "parent_is_a_file",
                                          "same_stem_other_date"]},
        },
        "summary": summary,
        "verdict": summary["verdict"],
        "rows": [r for r in unresolved[:140]],
        "resolved_arm_sizes": {
            "names_with_one_file": sum(1 for r in resolved if r["n_files_baseline"] == 1),
            "names_with_two_or_more": sum(1 for r in resolved if r["n_files_baseline"] > 1),
        },
        "sibling_check": sibling_check(unresolved),
        "bounds": {
            "measured": ("each published key with no file in the baseline resolver tested against a "
                         "wider index (only .git/__pycache__ skipped), a form test (path vs "
                         "basename vs token vs template vs absolute), and a neighbourhood test for "
                         "repo-relative absences (directory exists, directory path is a file, "
                         "same-stem sibling under another date)"),
            "not_measured": ("whether a consumer of an unresolved name would find its file by "
                             "another cwd-relative base (E383's suffix rule is the weakest claim "
                             "that still distinguishes two files); git history (arm off -- see "
                             "A2.why)"),
            "no_rewrites": "no published face, pointer or key is edited here",
        },
    }
    say("verdict: %s" % summary["verdict"])
    if write_face:
        _write(face)
    return face


def _write(face):
    os.makedirs(PUBLISHED_DIR, exist_ok=True)
    for name in (FACE, LATEST):
        path = os.path.join(PUBLISHED_DIR, name)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
    say("wrote %s and %s" % (FACE, LATEST))


def verify():
    """Re-derive every published row from the tree as it stands."""
    problems = []
    path = os.path.join(PUBLISHED_DIR, FACE)
    if not os.path.exists(path):
        say("verify problems=['face is absent']")
        return ["face is absent"]
    with open(path, "r", encoding="utf-8") as fh:
        face = json.load(fh)
    summary = face.get("summary") or {}
    if face.get("evidence_cutoff") != TODAY:
        problems.append("evidence_cutoff moved")
    by_class = summary.get("by_class") or {}
    residual = summary.get("names_resolving_to_no_file")

    if sum(by_class.values()) != residual:
        problems.append("classes sum to %d but the residual is %s"
                        % (sum(by_class.values()), residual))
    unknown = sorted(set(by_class) - set(CLASSES))
    if unknown:
        problems.append("classes outside the frozen set: %s" % unknown)
    if decide(summary) != summary.get("verdict"):
        problems.append("verdict does not re-derive from the summary")
    if residual and (summary.get("names_found_by_a_wider_index") or 0) != by_class.get(CL_WIDER, 0):
        problems.append("wider-index count does not equal its class")

    history = deleted_paths()
    for row in face.get("rows") or []:
        key = row["key"]
        norm = e383._norm(key)
        base = e383._resolve(norm)
        if base:
            problems.append("%s: the baseline resolver now finds %d file(s)" % (key, len(base)))
            continue
        wide = wide_resolve(norm)
        if len(wide) != row["n_files_wider"]:
            problems.append("%s: wider index found %d, published %d"
                            % (key, len(wide), row["n_files_wider"]))
        form = form_of(norm)
        nb = neighbourhood(norm) if form == FORM_REPO_RELATIVE else {
            "parent_exists": False, "parent_is_a_file": False}
        facts = {
            "norm": norm,
            "wide_files": wide,
            "history_path": history_hit(norm, history["paths"]) if history["available"] else None,
            "is_directory": os.path.isdir(os.path.join(ROOT, norm.replace("/", os.sep)))
            if norm else False,
            "form": form,
            "parent_exists": nb["parent_exists"],
            "parent_is_a_file": nb["parent_is_a_file"],
        }
        again = classify_unresolved(facts)
        if again != row.get("class"):
            problems.append("%s: class %r re-derives %r" % (key, row.get("class"), again))

    say("verify problems=%s" % json.dumps(problems[:10], ensure_ascii=False))
    return problems


# --------------------------------------------------------------------------- selftest

def selftest():
    legs = []

    def leg(name, ok, detail=""):
        legs.append((name, bool(ok), detail))

    # 1. form: the distinction the study turns on
    leg("form: slash -> repo relative", form_of("results/x/F-2026-01-01.json") == FORM_REPO_RELATIVE)
    leg("form: no slash + extension -> a fragment, not a path",
        form_of("bad.json") == FORM_BARE_BASENAME)
    leg("form: no slash + no extension -> a token", form_of("arm") == FORM_BARE_TOKEN)
    leg("form: template wins over everything",
        form_of("results/FOO-%s.json") == FORM_TEMPLATE)
    leg("form: absolute is its own form",
        form_of("K:/x/y.json") == FORM_ABSOLUTE and form_of("/x/y.json") == FORM_ABSOLUTE)
    leg("form: every string lands in a frozen form",
        all(form_of(s) in (FORM_REPO_RELATIVE, FORM_BARE_BASENAME, FORM_BARE_TOKEN, FORM_TEMPLATE,
                           FORM_ABSOLUTE) for s in ("a/b.json", "b.json", "b", "b-%s.json", "K:/b")))

    # 2. classification: every class reachable, in the published order
    leg("class: wider index beats every other explanation",
        classify_unresolved({"norm": "Money02/a/x.json", "wide_files": ["Money02/a/x.json"],
                             "form": FORM_REPO_RELATIVE}) == CL_WIDER)
    leg("class: history before form",
        classify_unresolved({"norm": "results/x.json", "history_path": "results/x.json",
                             "form": FORM_REPO_RELATIVE}) == CL_HISTORY)
    leg("class: a fragment is not an absence",
        classify_unresolved({"norm": "bad.json", "form": FORM_BARE_BASENAME}) == CL_FRAGMENT)
    leg("class: a token is not a path",
        classify_unresolved({"norm": "arm", "form": FORM_BARE_TOKEN}) == CL_NOT_PATH)
    leg("class: a template is not a path",
        classify_unresolved({"norm": "results/FOO-%s.json", "form": FORM_TEMPLATE}) == CL_TEMPLATE)
    leg("class: a directory is not a file",
        classify_unresolved({"norm": "results/state_tilt", "form": FORM_REPO_RELATIVE,
                             "is_directory": True}) == CL_DIRECTORY)
    leg("class: a parent that is a file can never yield a face",
        classify_unresolved({"norm": "results/a.json.tmp/x.json", "form": FORM_REPO_RELATIVE,
                             "parent_exists": False, "parent_is_a_file": True}) == CL_DIR_IS_A_FILE)
    leg("class: a missing directory outranks a missing file",
        classify_unresolved({"norm": "data/newdir/x.json", "form": FORM_REPO_RELATIVE,
                             "parent_exists": False}) == CL_ABSENT_DIR)
    leg("class: a real absence inside an existing directory",
        classify_unresolved({"norm": "results/x.json", "form": FORM_REPO_RELATIVE,
                             "parent_exists": True}) == CL_ABSENT)
    leg("class: ten classes, no duplicates",
        len(CLASSES) == 10 and len(set(CLASSES)) == 10)

    # 3. history matching
    paths = {"results/A-2025.json", "deep/dir/B.json"}
    leg("history: exact path wins",
        history_hit("results/A-2025.json", paths) == "results/A-2025.json")
    leg("history: suffix match finds a deletion elsewhere",
        history_hit("dir/B.json", paths) == "deep/dir/B.json")
    leg("history: an unrelated name is not a hit", history_hit("results/Z.json", paths) is None)

    # 4. attribution of the hiding trees
    leg("hidden_by: names the skipped tree, not the file",
        hidden_by_trees(["legacy/x/F.json", "media/y.json", "results/z.json"])
        == {"legacy": 1, "media": 1})

    # 5. verdict recomputation
    leg("verdict: all found wider -> instrument",
        decide({"names_resolving_to_no_file": 3, "history_arm_available": False,
                "by_class": {CL_WIDER: 3}}) == V_INSTRUMENT)
    leg("verdict: fragments+templates+tokens -> the key set is inflated",
        decide({"names_resolving_to_no_file": 4, "history_arm_available": False,
                "by_class": {CL_FRAGMENT: 2, CL_TEMPLATE: 1, CL_NOT_PATH: 1}}) == V_NOT_A_PATH)
    leg("verdict: only real absences, arm ran -> attrition",
        decide({"names_resolving_to_no_file": 2, "history_arm_available": True,
                "by_class": {CL_ABSENT: 2}}) == V_ABSENT)
    leg("verdict: an arm that did not run is disclosed, not read as zero deletions",
        decide({"names_resolving_to_no_file": 2, "history_arm_available": False,
                "by_class": {CL_FRAGMENT: 1, CL_ABSENT: 1}}) == V_UNMEASURED)
    leg("verdict: with the arm run the same split is mixed",
        decide({"names_resolving_to_no_file": 2, "history_arm_available": True,
                "by_class": {CL_FRAGMENT: 1, CL_ABSENT: 1}}) == V_MIXED)
    leg("verdict: history-only residual",
        decide({"names_resolving_to_no_file": 2, "history_arm_available": True,
                "by_class": {CL_HISTORY: 2}}) == V_HISTORY)
    leg("verdict: empty residual makes no claim",
        decide({"names_resolving_to_no_file": 0, "history_arm_available": False,
                "by_class": {}}) == V_EMPTY)

    # 6. the date-shift hypothesis is a measurement, not an assumption
    leg("neighbourhood: a dated stem only matches the same stem under another date",
        DATE_RE.sub("", "FACE-2026-01-01.json") == DATE_RE.sub("", "FACE-2026-05-05.json")
        and DATE_RE.sub("", "FACE-2026-01-01.json") != DATE_RE.sub("", "OTHER-2026-01-01.json"))

    bad = [l for l in legs if not l[1]]
    for name, ok, detail in legs:
        say("%s %s%s" % ("PASS" if ok else "FAIL", name, (" | " + detail) if detail else ""))
    say("%d/%d legs passed" % (len(legs) - len(bad), len(legs)))
    return 1 if bad else 0


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd in ("run", "build"):
        build(True)
        return 0
    if cmd == "verify":
        return 1 if verify() else 0
    if cmd == "selftest":
        return selftest()
    say("usage: run | verify | selftest")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))