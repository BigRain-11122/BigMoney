"""E496 -- does E479's residue class survive the mode arm?

E483 (r1521) found that 18 of the 78 opener sites on E479's 36 latest-pointer twins are
write-mode opens: 11 are the publishing instrument writing its own twin, 7 are doctor harnesses
that write the face deliberately (and put it back).  E479 counted every ``open`` call carrying
the twin's name as an opener, so a twin whose opener set is the writer's own write plus legs was
never "opened only by a leg" -- the residue label is off.

This study re-derives E479's residue class for all 36 twins using READ-MODE openers only, and
publishes every class change with the site that caused it.  It then restates what a retirement
costs under the corrected reading:

  loses_its_last_reader        the twin was labelled leg-only/study only because a write-mode site
                               was counted as an opener; with reads only, nothing opens it
  writer_is_the_only_opener    the read-only residue is "only the script that writes it" -- the
                               remaining opener is a writer, so a retirement that keeps the face
                               keeps nothing readable
  never_leg_only               the twin had no non-producer READ at all: the 30 leg-only twins
                               price, minus the ones that were only ever written

Mode is read per site off the live tree (E483's resolver, not a name heuristic).  A site whose
source is absent, does not parse, or no longer carries an open call is published as its own
reading -- an unreadable site is not a read, and it is not a write either.

Run:      python scripts/e496_twin_mode.py run
Check:    python scripts/e496_twin_mode.py check     (tallies re-derive from the face)
Verify:   python scripts/e496_twin_mode.py verify    (re-derives from the live tree)
Selftest: python scripts/e496_twin_mode.py selftest
"""
import argparse
import io
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
if os.path.join(ROOT, "scripts") not in sys.path:
    sys.path.insert(0, os.path.join(ROOT, "scripts"))

import e479_twin_read as e479  # noqa: E402
import e483_leg_debt as e483  # noqa: E402

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE_NAME = "twinmode_latest.json"
DATED_PREFIX = "TWINMODE"
EVIDENCE_CUTOFF = "2026-11-07"
CARD = "E496-DOES-E479-S-RESIDUE-CLASS-SURVIVE-THE-MODE-ARM"

M_READ = e483.M_READ
M_WRITE = e483.M_WRITE
M_INDIRECT = e483.M_INDIRECT

LEG_CLASSES = (e479.C_SMOKE, e479.C_ROUND)
CONSUMER_CLASSES = (e479.C_STUDY, e479.C_SMOKE, e479.C_ROUND)

V_SURVIVES = ("every_leg_only_twin_stays_leg_only_when_only_read_mode_openers_count")
V_SHRINKS = ("some_leg_only_twins_were_only_ever_written_and_lose_their_last_reader_when_only_"
             "read_mode_openers_count")
V_EMPTY = "no_twin_to_re_read"
VERDICT_VOCAB = (V_SURVIVES, V_SHRINKS, V_EMPTY)


def _now():
    return time.strftime("%Y-%m-%dT%H:%M:%S+08:00", time.localtime())


def _rel(path):
    return os.path.relpath(path, ROOT).replace("\\", "/")


def _load_json(path):
    return json.load(io.open(path, "r", encoding="utf-8"))


def _write(face, root=None):
    root = root or ROOT
    outdir = os.path.join(root, "results", "state_tilt")
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    dated = os.path.join(outdir, "%s-%s.json" % (DATED_PREFIX, EVIDENCE_CUTOFF))
    latest = os.path.join(outdir, FACE_NAME)
    body = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=False)
    for path in (dated, latest):
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body)
            fh.write(u"\n")
    return dated, latest


# ------------------------------------------------------------------ mode measurement
def site_mode(source, line):
    """(mode, evidence) for one recorded opener site, read off the live tree."""
    got = e483.source_tree(source)
    if got is None:
        return M_INDIRECT, "the source is not on disk"
    if "error" in got:
        return M_INDIRECT, "the source does not parse: %s" % got["error"]
    call = e483.open_call_near(got["tree"], line)
    if call is None:
        return M_INDIRECT, "no open call carries this line"
    return e483.mode_of_site(got["tree"], line)


def measure_row(row):
    """Per-site modes and both residue readings for one twin."""
    twin = row.get("twin")
    producers = list(row.get("producers") or [])
    sites = []
    for s in row.get("counting_openers") or []:
        mode, why = site_mode(s.get("source"), s.get("line") or 0)
        sites.append({
            "source": s.get("source"),
            "line": s.get("line"),
            "literal": s.get("literal"),
            "match": s.get("match"),
            "mode": mode,
            "mode_evidence": why,
            "role": e483.role_of(s.get("source")),
            "is_producer": s.get("source") in producers,
        })
    reads = [s for s in sites if s["mode"] == M_READ]
    writes = [s for s in sites if s["mode"] == M_WRITE]
    unresolved = [s for s in sites if s["mode"] == M_INDIRECT]
    # globs are mode-free (a glob pattern cannot write), so they carry over unchanged
    globs = [{"source": g.get("source"), "line": g.get("line"),
              "pattern": g.get("pattern")}
             for g in (row.get("_globs") or [])]
    read_only = e479.class_of(reads, globs, producers)
    baseline = row.get("residue")
    return {
        "twin": twin,
        "twin_basename": os.path.basename(twin or ""),
        "family_dir": row.get("family_dir"),
        "members": row.get("members"),
        "bytes": row.get("bytes"),
        "baseline_residue": baseline,
        "read_only_residue": read_only,
        "class_changed": baseline != read_only,
        "opener_sites": len(sites),
        "read_sites": len(reads),
        "write_sites": len(writes),
        "unresolved_sites": len(unresolved),
        "producer_write_sites": sum(1 for s in writes if s["is_producer"]),
        "write_sites_not_from_a_listed_producer": sum(1 for s in writes
                                                      if not s["is_producer"]),
        "write_sites_from_a_leg_role_source": sum(
            1 for s in writes if s["role"] in (e483.S_SUITE, e483.S_RUNNER)),
        "write_sites_by_role": _by_role(writes),
        "loses_its_last_reader": bool(baseline in CONSUMER_CLASSES
                                      and read_only not in CONSUMER_CLASSES),
        "writer_is_the_only_remaining_opener": read_only == e479.C_PRODUCER and bool(writes),
        "non_producer_reads": sum(1 for s in reads if not s["is_producer"]),
        "sites": sites,
        "unresolved": unresolved,
        "cause": [{"source": s["source"], "line": s["line"], "mode": s["mode"],
                   "mode_evidence": s["mode_evidence"],
                   "is_producer": s["is_producer"]}
                  for s in sites if s["mode"] != M_READ],
        "producers": producers,
    }


def _by_role(sites):
    out = {}
    for s in sites:
        out[s.get("role")] = out.get(s.get("role"), 0) + 1
    return {k: out[k] for k in sorted(out)}


def _cross_check_vs_e483(rows):
    """Reconcile this study's mode totals against E483's published ones, on E483's population.

    E483 measured the 30 leg-only twins; this study measures all 36.  The whole-tree totals
    therefore differ by construction, so the comparison is made on the 30-twin subset and the
    E483 numbers are machine-read from its face (never restated from the card).
    """
    path = os.path.join(OUTDIR, "legdebt_latest.json")
    subset = [r for r in rows if r["baseline_residue"] == e479.C_SMOKE]
    got = {
        "source_face": "results/state_tilt/legdebt_latest.json (E483)",
        "population_note": ("E483 measured the 30 leg-only twins; this study measures all 36, "
                            "so whole-tree site totals differ by construction.  Compared here "
                            "on the 30-twin subset E483 measured."),
        "subset_twins": len(subset),
        "subset_read_sites": sum(r["read_sites"] for r in subset),
        "subset_write_sites": sum(r["write_sites"] for r in subset),
        "subset_indirect_sites": sum(r["unresolved_sites"] for r in subset),
        "subset_sites": sum(r["opener_sites"] for r in subset),
        "available": False,
        "agrees": None,
    }
    if not os.path.exists(path):
        return got
    try:
        face = _load_json(path)
    except (OSError, ValueError):
        return got
    s = face.get("summary") or {}
    modes = s.get("sites_by_mode") or {}
    got["available"] = True
    got["e483_twins"] = s.get("twins_in_population")
    got["e483_sites_in_population"] = s.get("sites_in_population")
    got["e483_read_sites"] = modes.get(M_READ)
    got["e483_write_sites"] = modes.get(M_WRITE)
    got["e483_indirect_sites"] = modes.get(M_INDIRECT)
    got["agrees"] = (got["e483_read_sites"] == got["subset_read_sites"]
                     and got["e483_write_sites"] == got["subset_write_sites"]
                     and got["e483_indirect_sites"] == got["subset_indirect_sites"])
    got["deltas"] = {
        "read": (got["subset_read_sites"] - (got["e483_read_sites"] or 0)),
        "write": (got["subset_write_sites"] - (got["e483_write_sites"] or 0)),
        "indirect": (got["subset_indirect_sites"] - (got["e483_indirect_sites"] or 0)),
    }
    return got


def build(root=None):
    root = root or ROOT
    pop, pop_meta = e479.population(root)
    sites, site_meta = e479.scan(pop, root)
    base_rows = e479.classify(pop, sites, root)
    for row in base_rows:
        twins_sites = sites.get(row["twin"]) or {}
        row["_globs"] = twins_sites.get("globs") or []
    rows = [measure_row(r) for r in base_rows]

    baseline_counts = {}
    read_only_counts = {}
    for k in e479.RESIDUE_VOCAB:
        baseline_counts[k] = 0
        read_only_counts[k] = 0
    for r in rows:
        baseline_counts[r["baseline_residue"]] = baseline_counts.get(r["baseline_residue"], 0) + 1
        read_only_counts[r["read_only_residue"]] = read_only_counts.get(r["read_only_residue"], 0) + 1

    leg_only_baseline = [r for r in rows if r["baseline_residue"] == e479.C_SMOKE]
    leg_only_after = [r for r in rows if r["read_only_residue"] == e479.C_SMOKE]
    changed = [r for r in rows if r["class_changed"]]
    lost_reader = [r for r in rows if r["loses_its_last_reader"]]
    writer_only = [r for r in rows if r["writer_is_the_only_remaining_opener"]]

    read_sites = sum(r["read_sites"] for r in rows)
    write_sites = sum(r["write_sites"] for r in rows)
    unresolved_sites = sum(r["unresolved_sites"] for r in rows)

    # a twin that was called leg-only but whose non-producer openers are ALL writes has no
    # reader in the baseline either -- the label, not the retirement, is what was wrong there.
    never_leg_only = [r for r in rows
                      if r["baseline_residue"] in LEG_CLASSES
                      and r["read_only_residue"] not in LEG_CLASSES]
    twins_with_a_write_only_opener_set = [
        r for r in rows if r["opener_sites"] and not r["read_sites"]]

    verdict = V_EMPTY if not rows else (V_SHRINKS if lost_reader else V_SURVIVES)
    cross = _cross_check_vs_e483(rows)

    summary = {
        "twins_in_the_population": len(rows),
        "baseline_residue_counts": baseline_counts,
        "read_only_residue_counts": read_only_counts,
        "twins_whose_class_changed": len(changed),
        "twins_labelled_leg_only_in_the_baseline": len(leg_only_baseline),
        "twins_labelled_leg_only_with_reads_only": len(leg_only_after),
        "leg_only_label_survived": len(leg_only_after) == len(leg_only_baseline),
        "twins_that_lose_their_last_reader": len(lost_reader),
        "twins_where_the_writer_is_the_only_remaining_opener": len(writer_only),
        "leg_labelled_twins_that_were_never_leg_only": len(never_leg_only),
        "twins_whose_opener_set_is_writes_only": len(twins_with_a_write_only_opener_set),
        "opener_sites": read_sites + write_sites + unresolved_sites,
        "read_sites": read_sites,
        "write_sites": write_sites,
        "unresolved_sites": unresolved_sites,
        "producer_write_sites": sum(r["producer_write_sites"] for r in rows),
        "write_sites_not_from_a_listed_producer": sum(
            r["write_sites_not_from_a_listed_producer"] for r in rows),
        "write_sites_from_a_leg_role_source": sum(
            r["write_sites_from_a_leg_role_source"] for r in rows),
        "write_sites_by_role": _by_role([s for r in rows for s in r["sites"]
                                         if s["mode"] == M_WRITE]),
        "twins_where_a_leg_role_source_writes_it": sum(
            1 for r in rows if r["write_sites_from_a_leg_role_source"]),
        "mode_totals_agree_with_e483_on_the_30_twin_subset": cross["agrees"],
        "twins_with_an_unresolved_site": sum(1 for r in rows if r["unresolved_sites"]),
        "members_behind_the_retirable_twins_baseline": sum(
            r["members"] or 0 for r in rows
            if r["baseline_residue"] in e479.RETIRABLE_WHOLE),
        "members_behind_the_retirable_twins_reads_only": sum(
            r["members"] or 0 for r in rows
            if r["read_only_residue"] in e479.RETIRABLE_WHOLE),
        "bytes_behind_the_retirable_twins_baseline": sum(
            r["bytes"] or 0 for r in rows
            if r["baseline_residue"] in e479.RETIRABLE_WHOLE),
        "bytes_behind_the_retirable_twins_reads_only": sum(
            r["bytes"] or 0 for r in rows
            if r["read_only_residue"] in e479.RETIRABLE_WHOLE),
    }

    face = {
        "study": "E496",
        "card": CARD,
        "title": ("Does E479's residue class survive the mode arm -- with write-mode openers "
                  "removed, which twins were never leg-only and what does a retirement cost"),
        "generated": _now(),
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "source_faces": {
            "population_and_residue": "results/state_tilt/twinread_latest.json (E479)",
            "opener_modes": "results/state_tilt/legdebt_latest.json (E483)",
        },
        "population_meta": pop_meta,
        "site_meta": site_meta,
        "verdict": verdict,
        "verdict_vocab": list(VERDICT_VOCAB),
        "summary": summary,
        "cross_check_vs_e483": cross,
        "rows": rows,
        "class_changes": [
            {"twin": r["twin"], "from": r["baseline_residue"], "to": r["read_only_residue"],
             "cause": r["cause"],
             "members": r["members"], "bytes": r["bytes"]}
            for r in changed
        ],
        "reading": (
            "Mode is resolved per site off the live tree (E483's resolver).  A write-mode open is "
            "not a reader: a twin whose opener set is the writer's write plus legs was never "
            "'opened only by a leg'.  Unresolved sites are published as their own reading -- they "
            "are counted neither as reads nor as writes, so a twin whose only openers are "
            "unresolved is reported as such rather than being retired on a guess."
        ),
    }
    return face


# ------------------------------------------------------------------ check / verify
def tally_problems(face):
    problems = []
    rows = face.get("rows") or []
    summary = face.get("summary") or {}

    def recount(key, fn):
        got = sum(1 for r in rows if fn(r))
        want = summary.get(key)
        if want is not None and want != got:
            problems.append("%s: face=%r re-derived=%r" % (key, want, got))

    recount("twins_whose_class_changed", lambda r: r.get("class_changed"))
    recount("twins_that_lose_their_last_reader", lambda r: r.get("loses_its_last_reader"))
    recount("twins_where_the_writer_is_the_only_remaining_opener",
            lambda r: r.get("writer_is_the_only_remaining_opener"))
    recount("twins_labelled_leg_only_in_the_baseline",
            lambda r: r.get("baseline_residue") == e479.C_SMOKE)
    recount("twins_labelled_leg_only_with_reads_only",
            lambda r: r.get("read_only_residue") == e479.C_SMOKE)
    recount("twins_whose_opener_set_is_writes_only",
            lambda r: (r.get("opener_sites") or 0) and not (r.get("read_sites") or 0))

    for key, field in (("read_sites", "read_sites"), ("write_sites", "write_sites"),
                       ("unresolved_sites", "unresolved_sites"),
                       ("opener_sites", "opener_sites")):
        got = sum(r.get(field) or 0 for r in rows)
        if summary.get(key) is not None and summary[key] != got:
            problems.append("%s: face=%r re-derived=%r" % (key, summary[key], got))

    for r in rows:
        total = (r.get("read_sites") or 0) + (r.get("write_sites") or 0) + \
                (r.get("unresolved_sites") or 0)
        if total != (r.get("opener_sites") or 0):
            problems.append("%s: site modes do not sum to opener_sites" % r.get("twin"))
        roles = r.get("write_sites_by_role") or {}
        if sum(roles.values()) != (r.get("write_sites") or 0):
            problems.append("%s: write roles do not sum to write_sites" % r.get("twin"))
        if r.get("read_only_residue") == e479.C_PRODUCER and not (r.get("write_sites") or 0):
            problems.append("%s: reads-only residue says producer but no write site"
                            % r.get("twin"))

    recount("leg_labelled_twins_that_were_never_leg_only",
            lambda r: (r.get("baseline_residue") in LEG_CLASSES
                       and r.get("read_only_residue") not in LEG_CLASSES))

    if face.get("verdict") not in VERDICT_VOCAB:
        problems.append("verdict not in vocabulary: %r" % face.get("verdict"))
    changed = [r for r in rows if r.get("class_changed")]
    if len(changed) != len(face.get("class_changes") or []):
        problems.append("class_changes length %d != changed rows %d"
                        % (len(face.get("class_changes") or []), len(changed)))
    return problems


def check(face=None):
    if face is None:
        path = os.path.join(OUTDIR, FACE_NAME)
        if not os.path.exists(path):
            raise SystemExit("no face at %s" % path)
        face = _load_json(path)
    problems = tally_problems(face)
    if problems:
        print("CHECK FAIL: %d problem(s)" % len(problems))
        for p in problems[:20]:
            print("  -", p)
        return 2
    print("CHECK OK: %d rows, verdict=%s"
          % (len(face.get("rows") or []), face.get("verdict")))
    return 0


def verify():
    live = build()
    path = os.path.join(OUTDIR, FACE_NAME)
    if not os.path.exists(path):
        raise SystemExit("no face at %s" % path)
    published = _load_json(path)
    problems = tally_problems(live)
    a = live.get("summary") or {}
    b = published.get("summary") or {}
    for key in sorted(set(a) | set(b)):
        if a.get(key) != b.get(key):
            problems.append("summary.%s: published=%r live=%r" % (key, b.get(key), a.get(key)))
    if live.get("verdict") != published.get("verdict"):
        problems.append("verdict: published=%r live=%r"
                        % (published.get("verdict"), live.get("verdict")))
    if problems:
        print("VERIFY FAIL: %d problem(s)" % len(problems))
        for p in problems[:20]:
            print("  -", p)
        return 2
    print("VERIFY OK: re-derived from the live tree")
    return 0


# ------------------------------------------------------------------ selftest
def _fixture_row(baseline, read_only):
    return {"baseline_residue": baseline, "read_only_residue": read_only,
            "class_changed": baseline != read_only,
            "loses_its_last_reader": (baseline in CONSUMER_CLASSES
                                      and read_only not in CONSUMER_CLASSES),
            "writer_is_the_only_remaining_opener": read_only == e479.C_PRODUCER,
            "opener_sites": 1, "read_sites": 1, "write_sites": 0, "unresolved_sites": 0}


def selftest():
    bad = []
    total = [0]

    def t(name, cond, detail=""):
        total[0] += 1
        if not cond:
            bad.append("%s %s" % (name, detail))

    # 1. the read-only re-read uses e479's own class_of, so an empty opener set cannot come
    #    back as a leg class
    t("empty-reads-is-not-a-consumer",
      e479.class_of([], [], []) == e479.C_NEVER,
      e479.class_of([], [], []))
    # 2. removing the only leg read moves a smoke-labelled twin to "never opened"
    reads = [{"source": "smoke_test.py", "line": 1}]
    t("smoke-read-keeps-the-leg-label",
      e479.class_of(reads, [], ["scripts/x.py"]) == e479.C_SMOKE,
      e479.class_of(reads, [], ["scripts/x.py"]))
    t("no-reads-moves-to-never",
      e479.class_of([], [], ["scripts/x.py"]) == e479.C_NEVER,
      e479.class_of([], [], ["scripts/x.py"]))
    # 3. a writer-only opener set reads as producer, and only a write site earns that label
    prod = [{"source": "scripts/x.py", "line": 3}]
    t("producer-only-is-producer",
      e479.class_of(prod, [], ["scripts/x.py"]) == e479.C_PRODUCER,
      e479.class_of(prod, [], ["scripts/x.py"]))
    # 4. the derived flags
    r = _fixture_row(e479.C_SMOKE, e479.C_NEVER)
    t("loses-last-reader-flag", r["loses_its_last_reader"] is True)
    t("class-changed-flag", r["class_changed"] is True)
    r = _fixture_row(e479.C_SMOKE, e479.C_SMOKE)
    t("unchanged-keeps-flag-false",
      r["class_changed"] is False and r["loses_its_last_reader"] is False)
    r = _fixture_row(e479.C_SMOKE, e479.C_PRODUCER)
    t("writer-only-flag", r["writer_is_the_only_remaining_opener"] is True)
    # 5. tally legs fire on a doctored face
    good = {"verdict": V_SURVIVES,
            "summary": {"twins_whose_class_changed": 0, "read_sites": 1,
                        "write_sites": 0, "unresolved_sites": 0, "opener_sites": 1,
                        "twins_that_lose_their_last_reader": 0,
                        "twins_where_the_writer_is_the_only_remaining_opener": 0,
                        "twins_labelled_leg_only_in_the_baseline": 1,
                        "twins_labelled_leg_only_with_reads_only": 1,
                        "twins_whose_opener_set_is_writes_only": 0,
                        "leg_labelled_twins_that_were_never_leg_only": 0},
            "rows": [_fixture_row(e479.C_SMOKE, e479.C_SMOKE)],
            "class_changes": []}
    t("tallies-clean-face", tally_problems(good) == [], tally_problems(good))
    doctored = json.loads(json.dumps(good))
    doctored["summary"]["twins_whose_class_changed"] = 5
    t("tallies-catch-doctored-count", bool(tally_problems(doctored)))
    doctored2 = json.loads(json.dumps(good))
    doctored2["summary"]["read_sites"] = 9
    t("tallies-catch-site-sum", bool(tally_problems(doctored2)))
    doctored3 = json.loads(json.dumps(good))
    doctored3["verdict"] = "made_up"
    t("tallies-catch-bad-verdict", bool(tally_problems(doctored3)))
    # 6. a producer residue with no write site is a contradiction the check must catch
    doctored4 = json.loads(json.dumps(good))
    doctored4["rows"] = [_fixture_row(e479.C_SMOKE, e479.C_PRODUCER)]
    doctored4["summary"].update({"twins_whose_class_changed": 1,
                                 "twins_that_lose_their_last_reader": 1,
                                 "twins_labelled_leg_only_in_the_baseline": 1,
                                 "leg_labelled_twins_that_were_never_leg_only": 1,
                                 "twins_where_the_writer_is_the_only_remaining_opener": 1})
    t("tallies-catch-producer-without-a-write", bool(tally_problems(doctored4)))
    # 7. mode vocabulary is E483's, not a local re-spelling
    t("mode-vocabulary-shared",
      (M_READ, M_WRITE, M_INDIRECT) == e483.MODE_VOCAB,
      (M_READ, M_WRITE, M_INDIRECT))
    # 8. an absent source is unresolved, never a read
    mode, _why = site_mode("scripts/_e496_no_such_source_xyz.py", 1)
    t("absent-source-is-unresolved", mode == M_INDIRECT, mode)

    if bad:
        print("SELFTEST FAIL: %d of %d" % (len(bad), total[0]))
        for b in bad:
            print("  -", b)
        return 2
    print("SELFTEST OK: %d/%d" % (total[0], total[0]))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="E496 twin residue under the mode arm")
    ap.add_argument("cmd", nargs="?", default="run",
                    choices=("run", "check", "verify", "selftest"))
    args = ap.parse_args(argv)
    if args.cmd == "run":
        face = build()
        dated, latest = _write(face)
        s = face["summary"]
        print("E496: %d twins, %d class changes, %d lose their last reader, verdict=%s"
              % (s["twins_in_the_population"], s["twins_whose_class_changed"],
                 s["twins_that_lose_their_last_reader"], face["verdict"]))
        print("wrote", _rel(dated), "+", _rel(latest))
        return check(face)
    if args.cmd == "check":
        return check()
    if args.cmd == "verify":
        return verify()
    return selftest()


if __name__ == "__main__":
    sys.exit(main())