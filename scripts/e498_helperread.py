"""E498 -- which helpers hide readers across the other families.

E497 (r1523) found that the one twin E496 called never opened is in fact read by three S6 chain
producers, all through an in-module helper that opens its own parameter.  The arm that found them
is generic: it does not know anything about the CALL family.  So the obvious next question is
whether the same blindness applies to the rest of the population an earlier residue study called
unread -- and the only honest way to ask it is to re-measure that population with the helper arm
switched on.

Population  the 36 latest-pointer twins frozen by E479 and re-classed by E496 (mode arm only).
            This study does NOT re-scan every face in the tree; it re-measures the same 36 with a
            third arm, so the class deltas are directly comparable to E496's.
Arms        A. a literal at an opener (E479/E483/E496's arm, reproduced by e497.scan)
            B. a path folded out of a name and handed to an in-module function that opens it
            C. the lane face key handed to lane_io (not applicable here -- no member is a lane)
Reading     per twin: baseline class (E496 read-only arm) -> class under the helper arm, plus the
            helper functions that supply the new readers and the sites that call them.

The measurement is reused, not reimplemented: e497.scan() already carries all three arms, so this
module only swaps its population, its candidate-token prefilter and its family globs, and asserts
in the selftest that the swap did not loosen the arm it is inheriting.

Run:      python scripts/e498_helperread.py run
Check:    python scripts/e498_helperread.py check     (tallies re-derive from the face)
Verify:   python scripts/e498_helperread.py verify    (re-derives from the live tree)
Selftest: python scripts/e498_helperread.py selftest
"""
import argparse
import io
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (ROOT, os.path.join(ROOT, "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import e497_twindead as e497  # noqa: E402
import e483_leg_debt as e483  # noqa: E402

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE_NAME = "helperread_latest.json"
DATE_STAMP = "2026-11-07"
CARD = "E498-WHICH-HELPERS-HIDE-READERS-ACROSS-THE-OTHER-FAMILIES"
PARENT_FACE = "twinmode_latest.json"            # E496
RESIDUE_FACE = "twinread_latest.json"           # E479

M_READ = e483.M_READ
M_WRITE = e483.M_WRITE

# reading of one twin under the helper arm
R_READ_HELPER = "read_by_a_site_that_hands_its_path_to_an_in_module_helper"
R_READ_SOMEWHERE = "read_by_at_least_one_site_under_the_helper_arm"
R_NO_READER = "no_reading_site_even_with_the_helper_arm"
READINGS = (R_READ_HELPER, R_READ_SOMEWHERE, R_NO_READER)

V_LIVE = "the_helper_arm_turns_part_of_the_unread_population_into_read_twins"
V_NONE = "no_twin_in_the_population_gains_a_reader_from_the_helper_arm"
V_ALL = "every_twin_already_had_a_reader_before_the_helper_arm"
VERDICT_VOCAB = (V_LIVE, V_NONE, V_ALL)


def _now():
    return time.strftime("%Y-%m-%dT%H:%M:%S+08:00", time.localtime())


def _load_json(path):
    return json.load(io.open(path, "r", encoding="utf-8"))


# ------------------------------------------------------------------- population
def population(root=None):
    """The 36 twins E479 froze, with E496's read-only class carried along as the baseline."""
    root = root or ROOT
    face = _load_json(os.path.join(root, "results", "state_tilt", PARENT_FACE))
    rows = []
    for r in face.get("rows") or []:
        twin = r.get("twin")
        if not twin:
            continue
        abs_path = os.path.join(root, twin.replace("/", os.sep))
        rows.append({
            "member": twin,
            "basename": os.path.basename(twin),
            # e497.scan() reads "kind" only to look a member up in its lane-helper table; none of
            # these twins is a lane, so the neutral kind is the honest one.
            "kind": e497.K_OTHER,
            "family_dir": r.get("family_dir"),
            "members": r.get("members"),
            "bytes_on_disk": (os.path.getsize(abs_path) if os.path.exists(abs_path) else 0),
            "baseline_read_only_class": r.get("read_only_residue"),
            "baseline_opener_sites": r.get("opener_sites"),
            "baseline_read_sites": r.get("read_sites"),
            "members_named_by_the_family": r.get("members"),
        })
    return rows


def apply_arm(root=None):
    """Point e497's scan at this population, then put the module back.

    Two things must change and nothing else: the candidate-token prefilter (otherwise 35 of the 36
    twins are filtered out before the scan starts) and the family glob/prefix pair (otherwise the
    CALL family's '.md' writers are collected as if they belonged to these twins).  Everything the
    helper arm does -- folding a name, finding the function that opens its parameter -- is
    inherited untouched, and the selftest pins that.
    """
    root = root or ROOT
    keep = (e497.CANDIDATE_TOKENS, e497.FAMILY_DIR, e497.LITERAL_FAMILY_PREFIX, e497.SELF_PREFIX)
    members = population(root)
    toks = set()
    for m in members:
        stem = os.path.splitext(m["basename"])[0].lower()
        toks.add(stem)
        if m["family_dir"]:
            toks.add(m["family_dir"].split("/")[-1].lower())
    e497.CANDIDATE_TOKENS = tuple(sorted(toks))
    e497.FAMILY_DIR = "results/__no_family__"
    e497.LITERAL_FAMILY_PREFIX = "__NO_PREFIX__"
    e497.SELF_PREFIX = tuple(keep[3]) + ("e498_", "run_e498", "_e498")
    return members, keep, sorted(toks)


def restore(keep):
    e497.CANDIDATE_TOKENS, e497.FAMILY_DIR, e497.LITERAL_FAMILY_PREFIX, e497.SELF_PREFIX = keep


# ------------------------------------------------------------------- measure
def measure(root=None):
    root = root or ROOT
    members, keep, toks = apply_arm(root)
    try:
        sites, meta = e497.scan(members, root=root)
    finally:
        restore(keep)
    rows = []
    for m in members:
        got = sites.get(m["member"]) or []
        reads = [s for s in got if s.get("mode") == M_READ]
        writes = [s for s in got if s.get("mode") == M_WRITE]
        helper_reads = [s for s in reads if s.get("tier") == e497.T_HELPER]
        helpers = sorted({s.get("helper") for s in helper_reads if s.get("helper")})
        if helper_reads and len(helper_reads) == len(reads):
            reading = R_READ_HELPER
        elif reads:
            reading = R_READ_SOMEWHERE
        else:
            reading = R_NO_READER
        rows.append({
            "twin": m["member"],
            "family_dir": m["family_dir"],
            "members": m["members"],
            "bytes_on_disk": m["bytes_on_disk"],
            "baseline_read_only_class": m["baseline_read_only_class"],
            "baseline_read_sites": m["baseline_read_sites"],
            "reading": reading,
            "gained_a_reader": bool(reads) and not (m["baseline_read_sites"] or 0),
            "class_changed": (reading != R_NO_READER) and not (m["baseline_read_sites"] or 0),
            "read_sites": len(reads),
            "helper_read_sites": len(helper_reads),
            "write_sites": len(writes),
            "helpers": helpers,
            "helper_sites": [{"source": s.get("source"), "line": s.get("line"),
                              "helper": s.get("helper"),
                              "literal": s.get("literal")} for s in helper_reads],
        })
    return rows, meta, toks


def summary_of(rows, meta):
    gained = [r for r in rows if r["gained_a_reader"]]
    helper_only = [r for r in rows if r["reading"] == R_READ_HELPER]
    no_reader = [r for r in rows if r["reading"] == R_NO_READER]
    helpers = {}
    for r in rows:
        for h in r["helpers"]:
            helpers[h] = helpers.get(h, 0) + 1
    added_sites = sum(max(0, (r["read_sites"] or 0) - (r["baseline_read_sites"] or 0))
                      for r in rows)
    with_extra = [r for r in rows
                  if (r["read_sites"] or 0) > (r["baseline_read_sites"] or 0)]
    return {
        "twins_in_the_population": len(rows),
        "gained_a_reader_under_the_helper_arm": len(gained),
        "twins_that_gain_extra_read_sites_but_were_already_read": len(with_extra) - len(gained),
        "read_sites_invisible_to_a_literal_census": added_sites,
        "helper_read_sites": sum(r["helper_read_sites"] for r in rows),
        "read_only_through_a_helper": len(helper_only),
        "still_no_reader": len(no_reader),
        "baseline_unread": len([r for r in rows if not (r["baseline_read_sites"] or 0)]),
        "helpers_that_supply_the_new_readers": helpers,
        "twins_gaining_a_reader": [r["twin"] for r in gained],
        "twins_still_unread": [r["twin"] for r in no_reader],
        "sources_scanned_with_a_tree": meta.get("sources_scanned_with_a_tree"),
        "sources_with_a_family_candidate": meta.get("sources_with_a_family_candidate"),
        "candidate_tokens": meta.get("candidate_tokens"),
    }


def verdict_of(summary):
    if not summary["twins_in_the_population"]:
        return V_NONE
    if summary["gained_a_reader_under_the_helper_arm"]:
        return V_LIVE
    if summary["baseline_unread"] == 0:
        return V_ALL
    return V_NONE


def build(root=None):
    root = root or ROOT
    rows, meta, toks = measure(root)
    summary = summary_of(rows, meta)
    verdict = verdict_of(summary)
    return {
        "study": "E498",
        "card": CARD,
        "title": ("Which helpers hide readers across the other families -- the 36 frozen twins "
                  "re-measured with E497's helper arm"),
        "generated": _now(),
        "evidence_cutoff": DATE_STAMP,
        "source_faces": {"population": "results/state_tilt/%s (E496)" % PARENT_FACE,
                         "residue": "results/state_tilt/%s (E479)" % RESIDUE_FACE,
                         "arm": "scripts/e497_twindead.py (E497)"},
        "population_meta": {
            "rule": "the twins E479 froze and E496 re-classed with the mode arm",
            "size": summary["twins_in_the_population"],
            "bound": ("this re-measures those 36 twins only; it is not a census of every face in "
                      "the tree, and a twin that gains no reader here is not thereby declared dead "
                      "-- only that no helper in the corpus opens it"),
        },
        "scan_meta": {"candidate_tokens": toks,
                      "sources_scanned_with_a_tree": meta.get("sources_scanned_with_a_tree"),
                      "sources_with_a_family_candidate":
                          meta.get("sources_with_a_family_candidate"),
                      "sources_skipped_unreadable_or_oversize":
                          meta.get("sources_skipped_unreadable_or_oversize"),
                      "glob_and_composed_arms": "disabled for this population (no family prefix)"},
        "verdict": verdict,
        "verdict_vocab": list(VERDICT_VOCAB),
        "summary": summary,
        "rows": rows,
        "class_changes": [{"twin": r["twin"],
                           "from": r["baseline_read_only_class"],
                           "to": r["reading"],
                           "helpers": r["helpers"]}
                          for r in rows if r["gained_a_reader"]],
        "reading": ("E496 asked what happens when a write-mode opener is not counted as a reader; "
                    "this asks what happens when an opener is not visible at all because the path "
                    "was handed to a helper.  Both arms re-derive the same 36 twins so the class "
                    "deltas are comparable."),
    }


def _write(face, root=None):
    root = root or ROOT
    os.makedirs(os.path.join(root, "results", "state_tilt"), exist_ok=True)
    dated = os.path.join(root, "results", "state_tilt",
                         "HELPERREAD-%s.json" % DATE_STAMP.replace("-", ""))
    latest = os.path.join(root, "results", "state_tilt", FACE_NAME)
    for path in (dated, latest):
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
    return dated, latest


# ------------------------------------------------------------------- check / verify
def tally_problems(face):
    problems = []
    rows = face.get("rows") or []
    summary = face.get("summary") or {}
    gained = [r for r in rows if r.get("gained_a_reader")]
    if summary.get("twins_in_the_population") != len(rows):
        problems.append("the population size does not equal the row count")
    if summary.get("gained_a_reader_under_the_helper_arm") != len(gained):
        problems.append("the gained-a-reader count does not re-derive from the rows")
    added = sum(max(0, (r.get("read_sites") or 0) - (r.get("baseline_read_sites") or 0))
                for r in rows)
    if summary.get("read_sites_invisible_to_a_literal_census") != added:
        problems.append("the invisible-read-site count does not re-derive from the rows")
    helper_total = sum(r.get("helper_read_sites") or 0 for r in rows)
    if summary.get("helper_read_sites") != helper_total:
        problems.append("the helper read-site count does not re-derive from the rows")
    for r in rows:
        reads = r.get("read_sites") or 0
        if r.get("gained_a_reader") and not reads:
            problems.append("%s is claimed to have gained a reader but has no read site"
                            % r.get("twin"))
        if r.get("gained_a_reader") and (r.get("baseline_read_sites") or 0):
            problems.append("%s already had a reader before the arm" % r.get("twin"))
        if r.get("reading") == R_READ_HELPER and not (r.get("helper_read_sites") or 0):
            problems.append("%s is called helper-only but has no helper read site" % r.get("twin"))
        if r.get("reading") == R_NO_READER and reads:
            problems.append("%s is called unread but carries %d read sites"
                            % (r.get("twin"), reads))
    if face.get("verdict") != verdict_of(summary):
        problems.append("the verdict does not re-derive from the summary")
    return problems


def check(face=None, root=None):
    root = root or ROOT
    if face is None:
        face = _load_json(os.path.join(root, "results", "state_tilt", FACE_NAME))
    problems = tally_problems(face)
    print(json.dumps({"problems": problems, "rows": len(face.get("rows") or [])},
                     ensure_ascii=False))
    return 0 if not problems else 1


def verify(root=None):
    """Re-derive from the live tree and compare the two things a rebuild must not change."""
    root = root or ROOT
    stored = _load_json(os.path.join(root, "results", "state_tilt", FACE_NAME))
    fresh = build(root)
    problems = []
    for key in ("verdict", "summary", "class_changes", "rows"):
        if stored.get(key) != fresh.get(key):
            problems.append("%s does not re-derive" % key)
    problems.extend(tally_problems(fresh))
    print(json.dumps({"problems": problems,
                      "verdict": fresh["verdict"],
                      "gained": fresh["summary"]["gained_a_reader_under_the_helper_arm"]},
                     ensure_ascii=False))
    return 0 if not problems else 1


# ------------------------------------------------------------------- selftest
def _fixture_tree():
    """A two-twin world where one twin is readable ONLY through a helper."""
    import tempfile
    tmp = tempfile.mkdtemp(prefix="e498_")
    os.makedirs(os.path.join(tmp, "results", "state_tilt"))
    os.makedirs(os.path.join(tmp, "data", "famA"))
    os.makedirs(os.path.join(tmp, "data", "famB"))
    for rel in ("data/famA/a_latest.json", "data/famB/b_latest.json"):
        with io.open(os.path.join(tmp, rel.replace("/", os.sep)), "w", encoding="utf-8") as fh:
            fh.write("{}")
    with io.open(os.path.join(tmp, "results", "state_tilt", PARENT_FACE), "w",
                 encoding="utf-8") as fh:
        json.dump({"rows": [
            {"twin": "data/famA/a_latest.json", "family_dir": "data/famA", "members": 1,
             "read_only_residue": R_NO_READER, "read_sites": 0, "opener_sites": 1},
            {"twin": "data/famB/b_latest.json", "family_dir": "data/famB", "members": 1,
             "read_only_residue": R_NO_READER, "read_sites": 0, "opener_sites": 0},
        ]}, fh)
    with io.open(os.path.join(tmp, "reader.py"), "w", encoding="utf-8") as fh:
        fh.write("PATH_A = 'data/famA/a_latest.json'\n"
                 "def _read_json(p):\n"
                 "    with open(p) as fh:\n"
                 "        return fh.read()\n"
                 "def use():\n"
                 "    return _read_json(PATH_A)\n")
    return tmp


def selftest():
    legs = []

    def leg(name, ok):
        legs.append({"leg": name, "ok": bool(ok)})

    good = build()
    leg("face builds", good.get("verdict") in VERDICT_VOCAB)
    leg("check on the stored face is clean", check() == 0)
    leg("tallies re-derive", tally_problems(good) == [])

    # a doctored face must be caught
    bad = json.loads(json.dumps(good))
    if bad["rows"]:
        bad["rows"][0]["gained_a_reader"] = True
        bad["rows"][0]["baseline_read_sites"] = 3
        bad["rows"][0]["read_sites"] = 0
    leg("a doctored row is caught", bool(tally_problems(bad)))

    bad2 = json.loads(json.dumps(good))
    bad2["verdict"] = (V_NONE if good["verdict"] != V_NONE else V_ALL)
    leg("a doctored verdict is caught", bool(tally_problems(bad2)))

    # the arm really is inherited, not reimplemented: the helper that opens its parameter is found
    tmp = _fixture_tree()
    keep = (e497.CANDIDATE_TOKENS, e497.FAMILY_DIR, e497.LITERAL_FAMILY_PREFIX, e497.SELF_PREFIX)
    kept_root = e483.ROOT
    kept_cache = dict(e483._cache)
    try:
        members, keep2, _toks = apply_arm(tmp)
        # the inherited scanner resolves a repo-relative path against ITS module ROOT, so a
        # fixture tree is invisible until that too is repointed -- otherwise every fixture source
        # fails to load and the "no reader" answer is an artefact of the path, not of the tree.
        e483.ROOT = tmp
        e483._cache.clear()
        sites, meta = e497.scan(members, root=tmp)
    finally:
        restore(keep)
        e483.ROOT = kept_root
        e483._cache.clear()
        e483._cache.update(kept_cache)
    a = sites.get("data/famA/a_latest.json") or []
    b = sites.get("data/famB/b_latest.json") or []
    leg("fixture: the helper read is attributed to the twin it opens",
        any(s.get("tier") == e497.T_HELPER and s.get("mode") == M_READ for s in a))
    leg("fixture: the twin nobody opens stays unread",
        not any(s.get("mode") == M_READ for s in b))
    leg("fixture: the helper is named", any(s.get("helper") == "_read_json" for s in a))

    # the prefilter swap must not be silent: tokens come from the population
    m2 = population()
    toks = set()
    for m in m2:
        toks.add(os.path.splitext(m["basename"])[0].lower())
        if m["family_dir"]:
            toks.add(m["family_dir"].split("/")[-1].lower())
    _members, keep3, used = apply_arm()
    restore(keep3)
    leg("candidate tokens are derived from the population", set(used) == toks)

    passed = len([l for l in legs if l["ok"]])
    print(json.dumps({"selftest": "%d/%d" % (passed, len(legs)), "legs": legs}, ensure_ascii=False))
    return 0 if passed == len(legs) else 1


# ------------------------------------------------------------------- entry
def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", nargs="?", default="run",
                    choices=["run", "check", "verify", "selftest", "show"])
    args = ap.parse_args(argv)
    if args.cmd == "run":
        face = build()
        dated, latest = _write(face)
        print(json.dumps({"face": os.path.relpath(dated, ROOT).replace("\\", "/"),
                          "verdict": face["verdict"],
                          "summary": {k: v for k, v in face["summary"].items()
                                      if not isinstance(v, list)}},
                         ensure_ascii=False))
        return 0
    if args.cmd == "check":
        return check()
    if args.cmd == "verify":
        return verify()
    if args.cmd == "selftest":
        return selftest()
    face = _load_json(os.path.join(OUTDIR, FACE_NAME))
    print(json.dumps(face.get("summary"), ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())