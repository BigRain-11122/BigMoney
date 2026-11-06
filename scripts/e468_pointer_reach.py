"""E468 -- does a face whose pointer resolves only from its own directory ever get read?

E466 asked whether a pointer key NAMES a file and where it resolves from, and published the
answer in three bases: 27 pointer instances resolve from the repo root, 33 resolve **only** from
the pointing face's own directory, 4 only as an absolute path.  That was the end of the previous
question.  Nothing had asked the reverse: for a pointer that the repo root cannot follow, is there
any source in the tree that reaches the file at all -- and if there is, does it reach it by
knowing where the pointer lives, or by accident (a glob, a directory prefix)?

Three layers, each published apart, because a name is not a measurement (E207/E466):

  TARGET   the file the pointer names, spelled from the pointing face's own directory or as an
           absolute path, resolved to a repo-relative path so two faces naming the same file are
           the same target.
  SITES    every .py in the corpus that writes the exact string or only the target's basename.
           A naming site is not a reader: a source can carry the literal and never open it.
  REACH    how the site turns the literal into a path -- already repo-relative, joined to a repo
           root constant, joined to its own directory (__file__), absolute, a glob or directory
           prefix, or no base visible at all.

The residue is the answer: pointers only their own producer names, pointers only a glob or a
prefix lands on, pointers no source names, and pointers another reader does reach (the only
family that would contradict E466's premise).

Run:      python scripts/e468_pointer_reach.py run
Verify:   python scripts/e468_pointer_reach.py verify   (re-derives from the live tree)
Check:    python scripts/e468_pointer_reach.py check    (tallies re-derive from the face)
Selftest: python scripts/e468_pointer_reach.py selftest
"""

import argparse
import ast
import datetime
import io
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
if os.path.join(ROOT, "scripts") not in sys.path:
    sys.path.insert(0, os.path.join(ROOT, "scripts"))

import e451_prereg_digest as e451  # noqa: E402  (walk_py / read_text)
import e466_pointer_join as e466  # noqa: E402  (census / resolve_pointer / required_base)

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE_NAME = "pointerreach_latest.json"
DATED_PREFIX = "POINTERREACH"
CARD = "E468-DOES-A-FACE-WHOSE-POINTER-RESOLVES-ONLY-FROM-ITS-OWN-DIRECTORY-EVER-GET-READ"

SELF_SKIP = ("e461_", "e462_", "e463_", "e464_", "e466_", "e468_",
             "run_e461", "run_e462", "run_e463", "run_e464", "run_e466", "run_e468")
MAX_READ_BYTES = 2 * 1024 * 1024
WINDOW = 8

# ---- reach modes (how a naming site turns the literal into a path) --------------------------
R_LITERAL_ROOT = "the_literal_is_already_repo_relative"
R_WITH_ROOT = "the_site_joins_the_literal_to_a_repo_root_constant"
R_WITH_OWN_DIR = "the_site_joins_the_literal_to_its_own_directory"
R_ABSOLUTE = "the_literal_is_an_absolute_path"
R_GLOB = "the_site_names_a_glob_or_a_directory_prefix"
R_UNKNOWN = "the_site_shows_no_path_base"
REACH_MODES = (R_LITERAL_ROOT, R_WITH_ROOT, R_WITH_OWN_DIR, R_ABSOLUTE, R_GLOB, R_UNKNOWN)

ROOT_TOKENS = ("ROOT", "REPO_ROOT", "BASE_DIR", "HERE", "PARENT")
OWN_DIR_TOKENS = ("__file__",)

# ---- residues ------------------------------------------------------------------------------
Z_ONLY_PRODUCER = "only_the_pointing_faces_own_producer_names_it"
Z_TARGET_PRODUCER = "only_the_producer_of_the_target_file_names_it"
Z_SMOKE_ONLY = "only_a_smoke_or_runner_leg_names_it"
Z_GLOB_ONLY = "only_a_glob_or_directory_prefix_names_it"
Z_NO_SOURCE = "no_source_in_the_corpus_names_it"
Z_ROUND_SCRIPT = "only_a_one_off_round_script_names_it"
Z_OTHER_READER = "a_source_that_writes_neither_face_names_it"
RESIDUES = (Z_ONLY_PRODUCER, Z_TARGET_PRODUCER, Z_SMOKE_ONLY, Z_ROUND_SCRIPT,
            Z_GLOB_ONLY, Z_NO_SOURCE, Z_OTHER_READER)

V_EMPTY = "no_path_form_pointer_needs_a_base_other_than_the_repo_root"
V_ALWAYS_PRODUCER = "every_pointer_that_needs_another_base_is_named_only_by_a_producer"
V_SOME_OTHER = ("some_pointers_that_need_another_base_are_named_by_a_source_that_writes_"
                "neither_face")
V_SOME_GLOB = "some_pointers_that_need_another_base_are_named_only_through_a_glob"
V_SOME_NONE = "some_pointers_that_need_another_base_are_named_by_no_source_at_all"
VERDICT_VOCAB = (V_EMPTY, V_ALWAYS_PRODUCER, V_SOME_OTHER, V_SOME_GLOB, V_SOME_NONE)


def _load(path):
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _now():
    return datetime.datetime.now().astimezone()


def _today():
    return _now().strftime("%Y-%m-%d")


def _rel(root, path):
    return os.path.relpath(path, root).replace("\\", "/")


SKIP_DIRS = (".git", ".codely-cli", "_smoke", "_quarantine", "__pycache__", "node_modules")


def _walk_py(root):
    """Every .py under root, as paths relative to root (e451.walk_py hard-codes the repo root)."""
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if not name.endswith(".py"):
                continue
            rel = os.path.relpath(os.path.join(dirpath, name), root).replace("\\", "/")
            if any(os.path.basename(rel).startswith(s) for s in SELF_SKIP):
                continue
            out.append(rel)
    return sorted(out)


# ------------------------------------------------------------------ population


def target_of(value, face_rel, res):
    """The file the pointer names, as a repo-relative path (or None when it resolves nowhere)."""
    norm = res["normalised"]
    base = res["required_base"]
    if base == e466.B_OWN:
        return os.path.normpath(os.path.join(os.path.dirname(face_rel), norm)).replace("\\", "/")
    if base == e466.B_ABS:
        return os.path.normpath(norm).replace("\\", "/")
    if base == e466.B_ROOT:
        return os.path.normpath(norm).replace("\\", "/")
    return None


def population(root=None):
    """Every path-form pointer instance whose required base is not the repo root."""
    root = root or ROOT
    rows, meta = e466.census(root)
    out = []
    skipped_non_path = 0
    for row in rows:
        if e466.form_of(row["value"]) not in (e466.F_PATH, e466.F_PATH_NO_JSON):
            skipped_non_path += 1
            continue
        res = e466.resolve_pointer(row["value"], row["face"], root=root)
        if res["required_base"] == e466.B_ROOT:
            continue
        out.append({
            "face": row["face"],
            "key": row["key"],
            "value": row["value"],
            "spelling": res["spelling"],
            "required_base": res["required_base"],
            "target": target_of(row["value"], row["face"], res),
            "basename": os.path.basename(res["normalised"]),
        })
    out.sort(key=lambda r: (r["face"], r["key"]))
    return out, {"json_files_read": meta["json_files_read"],
                 "json_parse_errors": len(meta["parse_errors"]),
                 "pointer_instances": len(rows),
                 "non_path_pointer_instances": skipped_non_path}


# ------------------------------------------------------------------ corpus


def _string_sites(tree):
    """[(literal, lineno)] for every string constant in the module."""
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            out.append((node.value, getattr(node, "lineno", 0)))
    return out


def reach_mode(literal, lines, lineno):
    """How this site turns the literal into a path.  Reads the window, publishes the rule."""
    if os.path.isabs(literal) or (len(literal) > 2 and literal[1] == ":"):
        return R_ABSOLUTE
    if "*" in literal or "?" in literal:
        return R_GLOB
    lo = max(0, lineno - 1 - WINDOW)
    hi = min(len(lines), lineno + WINDOW)
    window = "\n".join(lines[lo:hi])
    if any(tok in window for tok in OWN_DIR_TOKENS):
        return R_WITH_OWN_DIR
    if any(tok in window for tok in ROOT_TOKENS):
        return R_WITH_ROOT
    if literal.replace("\\", "/").startswith(("results/", "docs/", "data/", "research/")):
        return R_LITERAL_ROOT
    return R_UNKNOWN


def naming_sites(pop, root=None):
    """{target: [site]} -- every source that writes the exact string or only the basename."""
    root = root or ROOT
    exact = {}      # normalised literal -> target
    basenames = {}  # basename -> [target]
    for rec in pop:
        if not rec["target"]:
            continue
        exact.setdefault(rec["value"].replace("\\", "/").strip(), rec["target"])
        basenames.setdefault(rec["basename"], []).append(rec["target"])
    needles = set(basenames) | set(exact)
    found = {t: [] for t in set(exact.values())}
    scanned = 0
    for rel in _walk_py(root):
        base = os.path.basename(rel)
        if any(base.startswith(s) for s in SELF_SKIP):
            continue
        path = os.path.join(root, rel)
        try:
            if os.path.getsize(path) > MAX_READ_BYTES:
                continue
            text = e451.read_text(path)
        except (OSError, ValueError):
            continue
        if not any(n in text for n in needles):
            continue
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        scanned += 1
        lines = text.splitlines()
        for literal, lineno in _string_sites(tree):
            norm = literal.replace("\\", "/").strip()
            hit = exact.get(norm)
            how = "exact_string"
            if hit is None and os.path.basename(norm) in basenames:
                how = "basename_only"
                cand = basenames[os.path.basename(norm)]
                hit = cand[0] if len(cand) == 1 else None
                if len(cand) > 1:
                    continue
            if hit is None:
                continue
            found.setdefault(hit, []).append({
                "source": rel,
                "line": lineno,
                "literal": literal,
                "matched": how,
                "reach": reach_mode(literal, lines, lineno),
            })
    for t in found:
        found[t].sort(key=lambda s: (s["source"], s["line"]))
    return found, {"sources_scanned_with_a_candidate": scanned,
                   "distinct_needles": len(needles)}


def producer_map(root=None):
    """face stem -> sources that write it (E464 write_sites: an output literal, not a name hit).

    e464.write_sites returns the face STEM a write site composes (e.g. "up" for up.json), so the
    lookup is by stem.  Two faces in different directories that share a stem are indistinguishable
    here and are published as a method limit.
    """
    root = root or ROOT
    out = {}
    for rel in _walk_py(root):
        base = os.path.basename(rel)
        if any(base.startswith(s) for s in SELF_SKIP):
            continue
        path = os.path.join(root, rel)
        try:
            if os.path.getsize(path) > MAX_READ_BYTES:
                continue
            body = e451.read_text(path)
            tree = ast.parse(body)
        except (SyntaxError, ValueError, OSError):
            continue
        for stem in e466.e464.write_sites(tree):
            out.setdefault(stem, set()).add(rel)
    return {k: sorted(v) for k, v in out.items()}


def _alias_stems(stem):
    """A face and its "_latest" twin are one face; e464 names the write site by the base stem."""
    out = {stem}
    if stem.endswith("_latest"):
        out.add(stem[:-len("_latest")])
    else:
        out.add(stem + "_latest")
    return out


def residue_of(row, sites, producers):
    """Which family names the target, in precedence order of how much it would prove.

    A site that WRITES the target file is named here on purpose: the upstream producer spells its
    own output, and that is not a reader following the pointer (E468's whole question).  A smoke
    or runner leg names a face to assert on it and is published apart for the same reason.
    """
    if not sites:
        return Z_NO_SOURCE
    if all(s["source"] in producers for s in sites):
        return Z_ONLY_PRODUCER
    outsiders = [s for s in sites if s["source"] not in producers]
    if all(s.get("writes_the_target_it_names") for s in outsiders):
        return Z_TARGET_PRODUCER
    rest = [s for s in outsiders if not s.get("writes_the_target_it_names")]
    if all(s.get("is_a_smoke_or_runner_leg") for s in rest):
        return Z_SMOKE_ONLY
    if all(s.get("is_a_one_off_round_script") for s in rest):
        return Z_ROUND_SCRIPT
    if all(s["reach"] == R_GLOB for s in rest):
        return Z_GLOB_ONLY
    return Z_OTHER_READER


def verdict_for(summary):
    n = summary["pointers_needing_another_base"]
    if n == 0:
        return V_EMPTY
    by = summary["residue_classes"]
    if by.get(Z_OTHER_READER):
        return V_SOME_OTHER
    if by.get(Z_ONLY_PRODUCER, 0) + by.get(Z_TARGET_PRODUCER, 0) + by.get(Z_SMOKE_ONLY, 0) \
            + by.get(Z_ROUND_SCRIPT, 0) == n:
        return V_ALWAYS_PRODUCER
    if by.get(Z_GLOB_ONLY):
        return V_SOME_GLOB
    if by.get(Z_NO_SOURCE):
        return V_SOME_NONE
    return V_ALWAYS_PRODUCER


# ------------------------------------------------------------------ build


def build(write=True, root=None):
    root = root or ROOT
    pop, meta = population(root)
    sites, site_meta = naming_sites(pop, root)
    producers = producer_map(root)

    smoke_names = ("smoke_test.py", "run_e")
    rows = []
    for rec in pop:
        tgt = rec["target"]
        mine = sites.get(tgt, []) if tgt else []
        target_stem = os.path.splitext(os.path.basename(tgt))[0] if tgt else ""
        writers_of_target = sorted({src for stem in _alias_stems(target_stem)
                                     for src in producers.get(stem, [])})
        for site in mine:
            site["writes_the_target_it_names"] = site["source"] in writers_of_target
            site["is_a_smoke_or_runner_leg"] = any(
                os.path.basename(site["source"]).startswith(n) for n in smoke_names)
            site["is_a_one_off_round_script"] = os.path.basename(site["source"]).startswith("_")
        producers_of_face = producers.get(os.path.splitext(os.path.basename(rec["face"]))[0], [])
        rows.append({
            "face": rec["face"],
            "key": rec["key"],
            "value": rec["value"],
            "spelling": rec["spelling"],
            "required_base": rec["required_base"],
            "target": tgt,
            "basename": rec["basename"],
            "target_exists_on_disk_at_that_repo_relative_path": os.path.isfile(os.path.join(root, tgt)) if tgt else False,
            "producers_of_the_pointing_face": producers_of_face,
            "naming_sites": mine,
            "residue": residue_of(rec, mine, producers_of_face),
        })

    by_base, by_reach, by_residue, by_spelling = {}, {}, {}, {}
    for r in rows:
        by_base[r["required_base"]] = by_base.get(r["required_base"], 0) + 1
        by_spelling[r["spelling"]] = by_spelling.get(r["spelling"], 0) + 1
        by_residue[r["residue"]] = by_residue.get(r["residue"], 0) + 1
        for s in r["naming_sites"]:
            by_reach[s["reach"]] = by_reach.get(s["reach"], 0) + 1
    sites_total = sum(len(r["naming_sites"]) for r in rows)

    summary = {
        "card": CARD,
        "pointer_instances_in_the_tree": meta["pointer_instances"],
        "non_path_pointer_instances": meta["non_path_pointer_instances"],
        "pointers_needing_another_base": len(rows),
        "pointers_by_required_base": by_base,
        "pointers_by_spelling": by_spelling,
        "pointers_whose_target_exists_on_disk": sum(1 for r in rows if r["target_exists_on_disk_at_that_repo_relative_path"]),
        "pointers_with_no_naming_site": sum(1 for r in rows if not r["naming_sites"]),
        "naming_sites_total": sites_total,
        "naming_sites_by_reach_mode": by_reach,
        "naming_sites_by_match": {"exact_string": sum(1 for r in rows for s in r["naming_sites"]
                                                      if s["matched"] == "exact_string"),
                                  "basename_only": sum(1 for r in rows for s in r["naming_sites"]
                                                       if s["matched"] == "basename_only")},
        "residue_classes": by_residue,
        "distinct_targets": len({r["target"] for r in rows if r["target"]}),
        "naming_sites_that_write_the_target_they_name":
            sum(1 for r in rows for s in r["naming_sites"] if s["writes_the_target_it_names"]),
        "naming_sites_in_a_smoke_or_runner_leg":
            sum(1 for r in rows for s in r["naming_sites"] if s["is_a_smoke_or_runner_leg"]),
        "naming_sites_in_a_one_off_round_script":
            sum(1 for r in rows for s in r["naming_sites"] if s["is_a_one_off_round_script"]),
    }
    face = {
        "card": CARD,
        "study": "E468_pointer_reach",
        "title": "a pointer the repo root cannot follow is named by its own producer or by nobody",
        "evidence_cutoff": _today(),
        "population_source": "results/state_tilt/pointerjoin_latest.json (E466 census, re-derived)",
        "verdict": verdict_for(summary),
        "verdict_vocab": list(VERDICT_VOCAB),
        "reach_modes": list(REACH_MODES),
        "residue_classes": list(RESIDUES),
        "summary": summary,
        "rows": rows,
        "method_limits": [
            "a naming site is a string constant equal to the pointer value or to the target's "
            "basename; a source that builds the same path from pieces is not counted (E436: "
            "composers recompose from the parent, they do not carry the literal)",
            "reach mode is read from an 8-line window around the literal; it says which base the "
            "site could use, not that the site opens this particular file",
            "the corpus is this machine's working tree; a reader outside it (the console app, a "
            "notebook) is not in the population",
            "own outputs (e461..e468 and their runners) are excluded so the census cannot count "
            "itself",
        ],
    }
    payload = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=False)
    if write:
        if not os.path.isdir(OUTDIR):
            os.makedirs(OUTDIR)
        dated = os.path.join(OUTDIR, "%s-%s.json" % (DATED_PREFIX, _today()))
        with io.open(dated, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(payload + "\n")
        with io.open(os.path.join(OUTDIR, FACE_NAME), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(payload + "\n")
        return face, [dated, os.path.join(OUTDIR, FACE_NAME)]
    return face, []


# ------------------------------------------------------------------ checks


def _recompute_tallies(face):
    rows = face["rows"]
    by_residue = {}
    for r in rows:
        by_residue[r["residue"]] = by_residue.get(r["residue"], 0) + 1
    return {
        "pointers_needing_another_base": len(rows),
        "naming_sites_total": sum(len(r["naming_sites"]) for r in rows),
        "pointers_with_no_naming_site": sum(1 for r in rows if not r["naming_sites"]),
        "residue_classes": by_residue,
        "verdict": verdict_for(face["summary"]),
    }


def row_problems(face):
    """Every row's residue re-derived from its own naming sites (not from its own label)."""
    bad = []
    for row in face.get("rows") or []:
        want = residue_of(row, row.get("naming_sites") or [],
                          row.get("producers_of_the_pointing_face") or [])
        if want != row.get("residue"):
            bad.append("%s: published residue %r, its sites say %r"
                       % (row.get("face"), row.get("residue"), want))
    return bad


def check():
    face = _load(os.path.join(OUTDIR, FACE_NAME))
    got = _recompute_tallies(face)
    problems = list(row_problems(face))
    if face.get("verdict") not in VERDICT_VOCAB:
        problems.append("verdict outside the frozen vocabulary: %r" % (face.get("verdict"),))
    for cls in (face["summary"].get("residue_classes") or {}):
        if cls not in RESIDUES:
            problems.append("residue class outside the frozen vocabulary: %r" % (cls,))
    for key in ("pointers_needing_another_base", "naming_sites_total",
                "pointers_with_no_naming_site", "residue_classes"):
        if got[key] != face["summary"][key]:
            problems.append("%s: %r != %r" % (key, got[key], face["summary"][key]))
    if got["verdict"] != face["verdict"]:
        problems.append("verdict: %s != %s" % (got["verdict"], face["verdict"]))
    print(json.dumps({"problems": problems, "tallies": got}, ensure_ascii=False, indent=1))
    return 0 if not problems else 1


def verify():
    face, _ = build(write=False)
    on_disk = _load(os.path.join(OUTDIR, FACE_NAME))
    problems = []
    for key in ("pointers_needing_another_base", "naming_sites_total",
                "residue_classes", "verdict", "naming_sites_by_reach_mode"):
        if face["summary"].get(key) != on_disk["summary"].get(key):
            problems.append("%s: fresh %r != published %r"
                            % (key, face["summary"].get(key), on_disk["summary"].get(key)))
    print(json.dumps({"problems": problems,
                      "fresh": face["summary"]["pointers_needing_another_base"],
                      "published": on_disk["summary"]["pointers_needing_another_base"]},
                     ensure_ascii=False, indent=1))
    return 0 if not problems else 1


# ------------------------------------------------------------------ selftest


def _fixture(tmp):
    os.makedirs(os.path.join(tmp, "results", "faces"))
    os.makedirs(os.path.join(tmp, "results", "other"))
    os.makedirs(os.path.join(tmp, "scripts"))
    # a face that points at a bare filename sitting beside it
    with io.open(os.path.join(tmp, "results", "faces", "up.json"), "w", encoding="utf-8") as fh:
        json.dump({"face": "sibling.json"}, fh)
    with io.open(os.path.join(tmp, "results", "faces", "sibling.json"), "w", encoding="utf-8") as fh:
        json.dump({"ok": True}, fh)
    # the producer of up.json names the bare literal and joins its own directory
    with io.open(os.path.join(tmp, "scripts", "prod_up.py"), "w", encoding="utf-8") as fh:
        fh.write("import os, json\nHERE = os.path.dirname(os.path.abspath(__file__))\n"
                 "def build():\n"
                 "    p = os.path.join(HERE, '..', 'results', 'faces', 'up.json')\n"
                 "    json.dump({'face': 'sibling.json'}, open(p, 'w'))\n")
    # an unrelated reader that reaches the same basename through a glob
    with io.open(os.path.join(tmp, "scripts", "other_reader.py"), "w", encoding="utf-8") as fh:
        fh.write("import glob\nfor p in glob.glob('results/**/*.json'):\n    pass\n"
                 "NAME = 'sibling.json'\n")
    return tmp


def selftest():
    legs = []

    def leg(name, ok, detail=""):
        legs.append({"leg": name, "ok": bool(ok), "detail": str(detail)[:200]})

    with tempfile.TemporaryDirectory() as tmp:
        _fixture(tmp)
        pop, meta = population(tmp)
        leg("population finds the bare pointer", len(pop) == 1 and pop[0]["value"] == "sibling.json",
            pop)
        leg("target is spelled from the pointing face's own directory",
            pop and pop[0]["target"] == "results/faces/sibling.json", pop and pop[0]["target"])
        leg("required base is the own directory",
            pop and pop[0]["required_base"] == e466.B_OWN, pop and pop[0]["required_base"])
        sites, _ = naming_sites(pop, tmp)
        tgt = "results/faces/sibling.json"
        leg("both naming sources are found", len(sites.get(tgt, [])) == 2, sites.get(tgt))
        modes = {s["source"]: s["reach"] for s in sites.get(tgt, [])}
        leg("producer site joins its own directory",
            modes.get("scripts/prod_up.py") == R_WITH_OWN_DIR, modes)
        leg("a reader with no base in the window is not called a glob",
            modes.get("scripts/other_reader.py") == R_UNKNOWN, modes)
        leg("a glob literal is classified as a glob",
            reach_mode("results/**/*.json", ["X = 1"], 1) == R_GLOB)
        prod = producer_map(tmp)
        leg("producer map ties up.json to its writer",
            "scripts/prod_up.py" in prod.get("up", []), prod)
        row = {"face": "results/faces/up.json"}
        leg("an outside reader is not classed as the producer",
            residue_of(row, sites.get(tgt, []), ["scripts/prod_up.py"]) == Z_OTHER_READER)
        leg("no naming site is its own class",
            residue_of(row, [], []) == Z_NO_SOURCE)
        leg("only the producer names it",
            residue_of(row, [s for s in sites.get(tgt, []) if s["source"] == "scripts/prod_up.py"],
                       ["scripts/prod_up.py"]) == Z_ONLY_PRODUCER)
        leg("reach mode reads the window, not the file name",
            reach_mode("results/faces/sibling.json", ["X = 1"], 1) == R_LITERAL_ROOT)
        leg("an absolute literal is absolute",
            reach_mode("/tmp/x.json", ["X = 1"], 1) == R_ABSOLUTE)
        face, _ = build(write=False, root=tmp)
        tallies = _recompute_tallies(face)
        leg("tallies re-derive from the rows",
            tallies["pointers_needing_another_base"] == len(face["rows"])
            and tallies["verdict"] == face["verdict"])
        again, _ = build(write=False, root=tmp)
        leg("build is deterministic", json.dumps(face, sort_keys=True) == json.dumps(again, sort_keys=True))

    bad = [l for l in legs if not l["ok"]]
    print(json.dumps({"legs": legs, "passed": len(legs) - len(bad), "failed": len(bad)},
                     ensure_ascii=False, indent=1))
    return 0 if not bad else 1


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "run":
        face, paths = build(write=True)
        bad = _recompute_tallies(face)
        print(json.dumps({"wrote": paths, "summary": face["summary"], "verdict": face["verdict"]},
                         ensure_ascii=False, indent=1))
        return 0
    if cmd == "verify":
        return verify()
    if cmd == "check":
        return check()
    if cmd == "selftest":
        return selftest()
    print("unknown command: %s" % cmd)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))