"""E500 -- is the strict rule's non-movement an agreement or an unfilled gap?

E499 (r1525) priced the 90 read sites E498's helper arm attributes to E479's 36 frozen twins and
recomputed retirement twice: every read site counts (E479's rule) versus only re-deriving and
pinning sites count (the card's strict rule).  One twin moved to retirable; 35 did not move at
all.  A status that does not move is not evidence: it can mean the strict rule agrees, or it can
mean the sites that would have decided the question were never in the priced set.

This study takes the 35 twins that did not move and re-scans them over the live tree, then prices
every site that is not one of E499's priced read sites.  Two things come out of that, and the
second is the one that was never published:

  * a residual site can be a read the parent arm never reached.  If one of them counts as a
    reader under the strict rule, the twin's "did not move" was a gap: the priced set was
    incomplete, not decisive.  Published as its own verdict, and the move is named twin by twin.
  * a residual site is usually a *writer*: the block that composes and writes the very face the
    retirement rule is talking about.  No arm in the E479/E499 lineage counts a writer -- the
    rule is about readers -- so a twin can be "kept" purely because a stranger reads it while its
    own producer is invisible to every arm.  That is the census this study publishes: which of
    the non-moved twins still have a live producer, and how many bytes ride on a face whose only
    uncompiled party is the code that writes it.

The pool question is answered literally and with its mechanism word: no twin is kept alive *only*
by sites that just open the file under the strict rule -- not because the tree lacks such sites,
but because a site that only opens the file is one of the classes the strict rule never counts.
The corresponding count under E479's parent rule (where opening a file is enough) is published
beside it so the two readings cannot be confused.

Run:      python scripts/e500_strictgap.py run
Check:    python scripts/e500_strictgap.py check     (tallies re-derive from the face)
Verify:   python scripts/e500_strictgap.py verify    (re-derives from the live tree)
Selftest: python scripts/e500_strictgap.py selftest
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

import e483_leg_debt as e483  # noqa: E402
import e497_twindead as e497  # noqa: E402
import e498_helperread as e498  # noqa: E402
import e499_helperprice as e499  # noqa: E402

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE_NAME = "strictgap_latest.json"
DATED_PREFIX = "STRICTGAP"
DATE_STAMP = "2026-11-07"
CARD = "E500-DOES-THE-STRICT-RULE-AGREE-OR-LEAVE-A-GAP-ON-THE-TWINS-THAT-DID-NOT-MOVE"

PARENT_FACE = "helperprice_latest.json"          # E499
RESIDUE_FACE = "twinread_latest.json"            # E479 (members / bytes / retirement split)

COUNTS_AS_A_READER = tuple(e499.COUNTS_AS_A_READER)      # re-derive or pin
ONLY_OPENS_THE_FILE = (e483.D_EXISTS, e483.D_NO_FIELD)
READ_MODES = (e483.M_READ,)
WRITE_MODES = (e483.M_WRITE,)

L_AGREEMENT = "kept_by_a_reader_that_re_derives_or_pins_and_no_remaining_read_site"
L_VACUOUS = "retirable_under_both_rules_because_no_read_site_was_ever_attributed"
L_GAP = "a_remaining_read_site_was_never_priced"
L_MOVED = "kept_only_because_a_remaining_read_site_counts_as_a_reader"
LABEL_VOCAB = (L_AGREEMENT, L_VACUOUS, L_GAP, L_MOVED)

V_GAP_MOVES = ("repricing_the_remaining_sites_keeps_alive_a_twin_the_priced_set_had_retired")
V_GAP_UNPRICED = "no_status_moves_but_a_remaining_read_site_was_never_priced"
V_AGREE = "every_remaining_site_on_these_twins_is_a_writer_that_no_retirement_arm_counts"
V_EMPTY = "no_twin_in_the_population_has_a_site_outside_the_priced_set"
VERDICT_VOCAB = (V_GAP_MOVES, V_GAP_UNPRICED, V_AGREE, V_EMPTY)


def _now():
    return time.strftime("%Y-%m-%dT%H:%M:%S+08:00", time.localtime())


def _load_json(path):
    return json.load(io.open(path, "r", encoding="utf-8"))


# ------------------------------------------------------------------------------- population
def non_moved(face):
    """The twins whose retirement status is the same under E479's rule and E499's strict rule.

    Re-derived from the rows, not copied from E499's ``moved`` list: a twin is kept under a
    counting set when at least one of its priced sites is in that set.  The parent rule counts
    every read site it has, so a twin with no site at all is retirable under both rules -- equal
    status there is emptiness, not agreement, and it is published as its own class.
    """
    out = []
    for r in face.get("rows") or []:
        sites = r.get("sites") or []
        kept_strict = any(s.get("price") in COUNTS_AS_A_READER for s in sites)
        kept_parent = bool(sites)
        if kept_strict == kept_parent:
            out.append({"row": r,
                        "kept_strict": kept_strict,
                        "kept_parent": kept_parent,
                        "kept_only_by_opening": bool(sites) and not kept_strict and
                        all(s.get("price") in ONLY_OPENS_THE_FILE for s in sites)})
    return out


# ------------------------------------------------------------------------------- measure
def price_residue(population, root=None):
    """Every site on a non-moved twin that E499 did not price, with what it does."""
    root = root or ROOT
    members, keep, toks = e498.apply_arm(root)
    want = {p["row"]["twin"] for p in population}
    # a census must not count its own sources (E180/E207 family); the E499 lesson applies again
    # one file further out: this module and its leg runner would otherwise enter the scan and
    # move the source count under the face they just published.
    e497.SELF_PREFIX = tuple(e497.SELF_PREFIX) + ("e499_", "run_e499", "_e499",
                                                  "e500_", "run_e500", "_e500")
    try:
        sites, meta = e497.scan([m for m in members if m["member"] in want], root=root)
    finally:
        e498.restore(keep)
    return sites, meta, toks


def measure(root=None):
    root = root or ROOT
    parent = _load_json(os.path.join(root, "results", "state_tilt", PARENT_FACE))
    population = non_moved(parent)
    sites, meta, toks = price_residue(population, root)
    rows = []
    for p in population:
        r = p["row"]
        twin = r["twin"]
        priced = {(s.get("source"), s.get("line")) for s in (r.get("sites") or [])}
        residual = [s for s in (sites.get(twin) or [])
                    if (s.get("source"), s.get("line")) not in priced]
        priced_sites = []
        for s in residual:
            if s.get("mode") in READ_MODES:
                got = e499.price_site(s.get("source"), s.get("line"))
                priced_sites.append({
                    "source": s.get("source"), "line": s.get("line"),
                    "mode": s.get("mode"), "tier": s.get("tier"),
                    "literal": s.get("literal"), "match": s.get("match"),
                    "price": got["price"], "block": got.get("block"),
                    "payload_roots": got.get("payload_roots"),
                    "evidence": got.get("evidence"),
                })
        writers = []
        for s in residual:
            if s.get("mode") in WRITE_MODES:
                writers.append({"source": s.get("source"), "line": s.get("line"),
                                "mode": s.get("mode"), "tier": s.get("tier"),
                                "literal": s.get("literal"), "match": s.get("match"),
                                "role": s.get("role"),
                                "attribution": s.get("attribution")})
        counting_residual = [s for s in priced_sites if s.get("price") in COUNTS_AS_A_READER]
        kept_after = p["kept_strict"] or bool(counting_residual)
        if counting_residual and not p["kept_strict"]:
            label = L_MOVED
        elif priced_sites:
            label = L_GAP
        elif p["kept_strict"]:
            label = L_AGREEMENT
        else:
            label = L_VACUOUS
        rows.append({
            "twin": twin,
            "family_dir": r.get("family_dir"),
            "members": r.get("members"),
            "bytes_on_disk": r.get("bytes_on_disk"),
            "kept_under_the_priced_set": p["kept_strict"],
            "priced_read_sites": len(r.get("sites") or []),
            "residual_sites": len(residual),
            "residual_read_sites": len(priced_sites),
            "residual_writer_sites": len(writers),
            "residual_reads_that_count_as_a_reader": len(counting_residual),
            "kept_after_repricing_the_residue": kept_after,
            "status_moves": kept_after != p["kept_strict"],
            "label": label,
            "read_residue": priced_sites,
            "writers": writers,
            "writer_faces": sorted({w["source"] for w in writers}),
        })
    return rows, meta, toks, parent


# ------------------------------------------------------------------------------- summary
def _by_label(rows, label):
    return [r["twin"] for r in rows if r["label"] == label]


def summary_of(rows, meta, parent):
    moved_priced = parent.get("summary") or {}
    readable = [r for r in rows if (r.get("priced_read_sites") or 0)]
    with_writer = [r for r in rows if r.get("residual_writer_sites")]
    # the corresponding count under E479's parent rule: a site that only opens the file is
    # enough there, so ask E499's own row whether every priced site is such a site.  Under the
    # strict rule the count is zero by construction -- the classes it counts exclude those two --
    # which is a fact about the rule, published as a mechanism word rather than as a measurement.
    parent = parent or {}
    only_opening_parent = []
    for r in (parent.get("rows") or []):
        if r["twin"] not in {x["twin"] for x in rows}:
            continue
        sites = r.get("sites") or []
        if sites and all(s.get("price") in ONLY_OPENS_THE_FILE for s in sites):
            only_opening_parent.append(r["twin"])
    return {
        "twins_in_the_population": len(rows),
        "twins_kept_under_the_priced_set": len([r for r in rows
                                                if r.get("kept_under_the_priced_set")]),
        "twins_retirable_under_the_priced_set": len([r for r in rows
                                                     if not r.get("kept_under_the_priced_set")]),
        "twins_that_had_a_read_site_at_all": len(readable),
        "priced_read_sites_inherited": sum(r.get("priced_read_sites") or 0 for r in rows),
        "residual_sites_scanned": sum(r.get("residual_sites") or 0 for r in rows),
        "residual_read_sites": sum(r.get("residual_read_sites") or 0 for r in rows),
        "residual_writer_sites": sum(r.get("residual_writer_sites") or 0 for r in rows),
        "residual_sites_by_mode": _modes(rows),
        "twins_with_a_residual_read_site": _by_label(rows, L_GAP) + _by_label(rows, L_MOVED),
        "twins_with_a_live_producer": [r["twin"] for r in with_writer],
        "twins_whose_producer_was_never_priced": len(with_writer),
        "bytes_written_by_a_producer_no_arm_counts":
            sum(r.get("bytes_on_disk") or 0 for r in with_writer),
        "twins_kept_only_by_sites_that_just_open_the_file_under_the_strict_rule":
            0,
        "twins_kept_only_by_sites_that_just_open_the_file_mechanism": (
            "the_strict_rule_counts_only_re_deriving_and_pinning_sites_so_a_site_that_just_opens"
            "_the_file_never_keeps_a_twin_alive"),
        "twins_kept_only_by_sites_that_just_open_the_file_under_the_parent_rule":
            len(only_opening_parent),
        "twins_kept_only_by_sites_that_just_open_the_file_under_the_parent_rule_named":
            only_opening_parent,
        "status_moves_under_repricing": [r["twin"] for r in rows if r.get("status_moves")],
        "label_counts": _labels(rows),
        "twins_whose_non_movement_is_vacuous": _by_label(rows, L_VACUOUS),
        "priced_set_from": "results/state_tilt/%s (E499: %d read sites)" % (
            PARENT_FACE, moved_priced.get("read_sites_priced") or 0),
        "sources_scanned_with_a_tree": meta.get("sources_scanned_with_a_tree"),
    }


def _labels(rows):
    out = {}
    for r in rows:
        out[r["label"]] = out.get(r["label"], 0) + 1
    return out


def _modes(rows):
    out = {}
    for r in rows:
        for s in (r.get("read_residue") or []):
            out[s["mode"]] = out.get(s["mode"], 0) + 1
        for s in (r.get("writers") or []):
            out[s["mode"]] = out.get(s["mode"], 0) + 1
    return out


def verdict_of(summary):
    if not summary["residual_sites_scanned"]:
        return V_EMPTY
    if summary["status_moves_under_repricing"]:
        return V_GAP_MOVES
    if summary["residual_read_sites"]:
        return V_GAP_UNPRICED
    return V_AGREE


def build(root=None):
    root = root or ROOT
    rows, meta, toks, parent = measure(root)
    summary = summary_of(rows, meta, parent)
    return {
        "study": "E500",
        "card": CARD,
        "title": ("Does the strict rule agree or leave a gap on the twins whose retirement status "
                  "did not move -- price every site outside E499's priced set"),
        "generated": _now(),
        "evidence_cutoff": DATE_STAMP,
        "source_faces": {"priced_set": "results/state_tilt/%s (E499)" % PARENT_FACE,
                         "population": "results/state_tilt/%s (E479)" % RESIDUE_FACE,
                         "arm": "scripts/e497_twindead.py (E497)",
                         "price_vocabulary": "scripts/e483_leg_debt.py (E483)",
                         "price_of_a_residual_site": "scripts/e499_helperprice.py (E499)"},
        "population_meta": {
            "rule": ("twins whose retirement status is identical under E479's rule (every read "
                     "site counts) and E499's strict rule (only re-deriving and pinning count)"),
            "size": summary["twins_in_the_population"],
            "bound": ("'did not move' is not evidence on its own: %d of the %d are kept by a "
                      "reader that re-derives or pins, %d are retirable under both rules because "
                      "no read site was ever attributed to them -- equal status from emptiness is "
                      "published as its own class, never as agreement"
                      % (summary["twins_kept_under_the_priced_set"],
                         summary["twins_in_the_population"],
                         summary["twins_retirable_under_the_priced_set"])),
        },
        "residue_meta": {
            "rule": ("every site E497 attributes to these twins that is not one of E499's priced "
                     "read sites, priced by the same classifier E499 used"),
            "counting_classes": list(COUNTS_AS_A_READER),
            "write_sites": ("a writer is not a reader: no arm in this lineage counts the block "
                            "that composes and writes the face, so a twin can look unread and "
                            "unretirable at the same time"),
            "candidate_tokens": toks,
        },
        "verdict": verdict_of(summary),
        "verdict_vocab": list(VERDICT_VOCAB),
        "summary": summary,
        "rows": rows,
        "reading": ("If every remaining site on these twins is a writer, the non-movement is an "
                    "agreement on the read axis and the unpriced party is the producer.  If a "
                    "remaining site is a reader, the priced set was incomplete and the twin's "
                    "status was decided on a population that did not include it."),
    }


def _write(face, root=None):
    root = root or ROOT
    os.makedirs(os.path.join(root, "results", "state_tilt"), exist_ok=True)
    dated = os.path.join(root, "results", "state_tilt",
                         "%s-%s.json" % (DATED_PREFIX, DATE_STAMP.replace("-", "")))
    latest = os.path.join(root, "results", "state_tilt", FACE_NAME)
    for path in (dated, latest):
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
    return dated, latest


# ------------------------------------------------------------------------------- check
def tally_problems(face):
    problems = []
    rows = face.get("rows") or []
    summary = face.get("summary") or {}
    if summary.get("twins_in_the_population") != len(rows):
        problems.append("the population size does not equal the row count")
    if summary.get("residual_sites_scanned") != sum(r.get("residual_sites") or 0 for r in rows):
        problems.append("the residual-site count does not re-derive from the rows")
    if summary.get("residual_read_sites") != sum(len(r.get("read_residue") or []) for r in rows):
        problems.append("the residual-read count does not re-derive from the rows")
    if summary.get("residual_writer_sites") != sum(len(r.get("writers") or []) for r in rows):
        problems.append("the residual-writer count does not re-derive from the rows")
    if summary.get("residual_sites_by_mode") != _modes(rows):
        problems.append("the residual mode tally does not re-derive from the rows")
    if summary.get("label_counts") != _labels(rows):
        problems.append("the label tally does not re-derive from the rows")
    if sorted(summary.get("status_moves_under_repricing") or []) != \
            sorted(r["twin"] for r in rows if r.get("status_moves")):
        problems.append("the move list does not re-derive from the rows")
    if sorted(summary.get("twins_whose_non_movement_is_vacuous") or []) != \
            sorted(_by_label(rows, L_VACUOUS)):
        problems.append("the vacuous list does not re-derive from the rows")
    if sorted(summary.get("twins_with_a_live_producer") or []) != \
            sorted(r["twin"] for r in rows if r.get("residual_writer_sites")):
        problems.append("the producer list does not re-derive from the rows")
    for r in rows:
        if (r.get("residual_read_sites") or 0) != len(r.get("read_residue") or []):
            problems.append("%s: the residual-read count does not equal its list" % r.get("twin"))
        if (r.get("residual_writer_sites") or 0) != len(r.get("writers") or []):
            problems.append("%s: the writer count does not equal its list" % r.get("twin"))
        if (r.get("residual_sites") or 0) != ((r.get("residual_read_sites") or 0) +
                                              (r.get("residual_writer_sites") or 0)):
            problems.append("%s: the residual total does not add up" % r.get("twin"))
        if r.get("label") not in LABEL_VOCAB:
            problems.append("%s: %s is outside the label vocabulary"
                            % (r.get("twin"), r.get("label")))
        for s in (r.get("read_residue") or []):
            if s.get("price") not in e499.PRICE_VOCAB:
                problems.append("%s: %s is outside the price vocabulary"
                                % (r.get("twin"), s.get("price")))
        counting = [s for s in (r.get("read_residue") or [])
                    if s.get("price") in COUNTS_AS_A_READER]
        if (r.get("residual_reads_that_count_as_a_reader") or 0) != len(counting):
            problems.append("%s: the counting-residual count does not re-derive" % r.get("twin"))
        kept_after = bool(r.get("kept_under_the_priced_set")) or bool(counting)
        if bool(r.get("kept_after_repricing_the_residue")) != kept_after:
            problems.append("%s: the post-repricing status does not re-derive" % r.get("twin"))
        if bool(r.get("status_moves")) != (kept_after != bool(r.get("kept_under_the_priced_set"))):
            problems.append("%s: the move flag does not re-derive" % r.get("twin"))
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
    root = root or ROOT
    stored = _load_json(os.path.join(root, "results", "state_tilt", FACE_NAME))
    fresh = build(root)
    problems = [k + " does not re-derive" for k in ("verdict", "summary", "rows")
                if stored.get(k) != fresh.get(k)]
    problems.extend(tally_problems(fresh))
    print(json.dumps({"problems": problems,
                      "verdict": fresh["verdict"],
                      "residual": fresh["summary"]["residual_sites_scanned"],
                      "producers": fresh["summary"]["twins_whose_producer_was_never_priced"]},
                     ensure_ascii=False))
    return 0 if not problems else 1


# ------------------------------------------------------------------------------- selftest
def _fixture_face():
    """A three-twin world whose priced set is deliberately incomplete.

    kept_twin      has one pinning read site (agreement)
    empty_twin     has no site at all (vacuous non-movement)
    orphan_twin    is retirable under the priced set, but a writer and a reader exist outside it
    """
    pin = e483.D_PIN
    rederive = e483.D_REDERIVE
    return {
        "study": "E499",
        "rows": [
            {"twin": "fam/kept_latest.json", "family_dir": "fam", "members": 2,
             "bytes_on_disk": 10, "priced_read_sites": 1,
             "sites": [{"source": "r.py", "line": 10, "price": pin, "tier": e497.T_DIRECT}]},
            {"twin": "fam/empty_latest.json", "family_dir": "fam", "members": 1,
             "bytes_on_disk": 20, "priced_read_sites": 0, "sites": []},
            {"twin": "fam/orphan_latest.json", "family_dir": "fam", "members": 3,
             "bytes_on_disk": 30, "priced_read_sites": 0, "sites": []},
            {"twin": "fam/moved_latest.json", "family_dir": "fam", "members": 1,
             "bytes_on_disk": 40, "priced_read_sites": 1,
             "sites": [{"source": "r.py", "line": 99, "price": e483.D_PRESENCE,
                        "tier": e497.T_DIRECT}]},
        ],
        "summary": {"twins_moving": ["fam/moved_latest.json"], "read_sites_priced": 2},
    }


def _fixture_population():
    """Rows are built by run_census() so the fixture exercises the same code path as the tree."""
    return [
        {"twin": "fam/kept_latest.json",
         "sites": [{"source": "r.py", "line": 10}],
         "scan": [{"source": "w.py", "line": 3, "mode": e483.M_WRITE,
                   "tier": e497.T_DIRECT, "literal": "fam/kept_latest.json"}]},
        {"twin": "fam/empty_latest.json", "sites": [], "scan": []},
        {"twin": "fam/orphan_latest.json", "sites": [],
         "scan": [{"source": "w.py", "line": 7, "mode": e483.M_WRITE,
                   "tier": e497.T_DIRECT, "literal": "fam/orphan_latest.json"}]},
    ]


def _classify_row(p, residual, priced_reads):
    """The row-level classification, extracted so a fixture can drive it without a live tree."""
    counting = [s for s in priced_reads if s.get("price") in COUNTS_AS_A_READER]
    kept_after = p["kept_strict"] or bool(counting)
    if counting and not p["kept_strict"]:
        label = L_MOVED
    elif priced_reads:
        label = L_GAP
    elif p["kept_strict"]:
        label = L_AGREEMENT
    else:
        label = L_VACUOUS
    return kept_after, label


def _doctor_with_a_bad_price(face):
    """A face whose only defect is one residual price outside the vocabulary.

    The live face may contain no residual read site at all (that is one of its answers), so a leg
    that doctors ``read_residue[0]`` on the live rows silently asserts nothing.  This builds the
    row, then re-derives every aggregate the check re-computes, so the sole reported problem is the
    vocabulary one -- a doctor that trips several checks would prove nothing about this one.
    """
    bad = json.loads(json.dumps(face))
    rows = bad.get("rows") or []
    if not rows:
        return None
    r = rows[0]
    r["read_residue"] = [{"source": "doctor.py", "line": 1,
                          "mode": e483.M_READ, "tier": e497.T_DIRECT,
                          "literal": r.get("twin"), "price": "reads_it_somehow"}]
    r["residual_read_sites"] = 1
    r["residual_sites"] = (r.get("residual_writer_sites") or 0) + 1
    s = bad.setdefault("summary", {})
    s["residual_sites_scanned"] = sum(x.get("residual_sites") or 0 for x in rows)
    s["residual_read_sites"] = sum(len(x.get("read_residue") or []) for x in rows)
    s["residual_writer_sites"] = sum(len(x.get("writers") or []) for x in rows)
    s["residual_sites_by_mode"] = _modes(rows)
    s["label_counts"] = _labels(rows)
    s["twins_with_a_residual_read_site"] = _by_label(rows, L_GAP) + _by_label(rows, L_MOVED)
    s["status_moves_under_repricing"] = [x["twin"] for x in rows if x.get("status_moves")]
    bad["verdict"] = verdict_of(s)
    return bad


def selftest():
    legs = []

    def leg(name, ok, detail=""):
        legs.append({"leg": name, "ok": bool(ok), "detail": detail})

    # ---- population: emptiness is not agreement
    face = _fixture_face()
    pop = non_moved(face)
    twins = sorted(p["row"]["twin"] for p in pop)
    leg("the moved twin is not in the population",
        "fam/moved_latest.json" not in twins, json.dumps(twins))
    leg("a twin with no read site is in the population (same status both rules)",
        "fam/empty_latest.json" in twins)
    leg("the kept twin is in the population", "fam/kept_latest.json" in twins)
    labels = {p["row"]["twin"]: _classify_row(p, None, [])[1] for p in pop}
    leg("the twin with no site is labelled vacuous, not agreement",
        labels["fam/empty_latest.json"] == L_VACUOUS, labels["fam/empty_latest.json"])
    leg("the twin with a pinning site is labelled agreement",
        labels["fam/kept_latest.json"] == L_AGREEMENT, labels["fam/kept_latest.json"])

    # ---- the residue decides a retirable twin, and a writer alone does not
    p_orphan = [p for p in pop if p["row"]["twin"] == "fam/orphan_latest.json"][0]
    kept_after, label = _classify_row(p_orphan, None,
                                      [{"price": e483.D_REDERIVE}])
    leg("a residual reader that re-derives keeps a retirable twin alive",
        kept_after is True and label == L_MOVED, "%s/%s" % (kept_after, label))
    kept_after2, label2 = _classify_row(p_orphan, None,
                                        [{"price": e483.D_EXISTS}])
    leg("a residual site that only opens the file does not keep it alive",
        kept_after2 is False and label2 == L_GAP, "%s/%s" % (kept_after2, label2))

    # ---- the mechanism word is a claim about the rule, not about the tree
    leg("the strict rule never counts an only-open-the-file site",
        e483.D_EXISTS not in COUNTS_AS_A_READER and e483.D_NO_FIELD not in COUNTS_AS_A_READER)

    # ---- the live face
    good = build()
    leg("face builds", good.get("verdict") in VERDICT_VOCAB)
    leg("tallies re-derive", tally_problems(good) == [], json.dumps(tally_problems(good))[:200])
    leg("check on the stored face is clean", check() == 0)
    s = good["summary"]
    leg("every twin in the population carries a row",
        s["twins_in_the_population"] == len(good["rows"]))
    leg("the kept and retirable split adds up to the population",
        s["twins_kept_under_the_priced_set"] + s["twins_retirable_under_the_priced_set"]
        == s["twins_in_the_population"])
    leg("the residual total is exactly its read part plus its writer part",
        s["residual_sites_scanned"] == s["residual_read_sites"] + s["residual_writer_sites"])

    bad = json.loads(json.dumps(good))
    if bad["rows"]:
        bad["rows"][0]["residual_sites"] = (bad["rows"][0].get("residual_sites") or 0) + 1
    leg("a doctored residual count is caught", bool(tally_problems(bad)))

    bad2 = json.loads(json.dumps(good))
    bad2["verdict"] = (V_AGREE if good["verdict"] != V_AGREE else V_GAP_UNPRICED)
    leg("a doctored verdict is caught", bool(tally_problems(bad2)))

    bad3 = json.loads(json.dumps(good))
    if bad3["rows"]:
        bad3["rows"][0]["label"] = "agreement_probably"
    leg("a label outside the vocabulary is caught", bool(tally_problems(bad3)))

    bad4 = _doctor_with_a_bad_price(good)
    probs4 = tally_problems(bad4) if bad4 else ["the live face has no row to doctor"]
    leg("a residual price outside the vocabulary is caught, and nothing else is",
        probs4 and all("outside the price vocabulary" in p for p in probs4), json.dumps(probs4))

    passed = len([l for l in legs if l["ok"]])
    print(json.dumps({"selftest": "%d/%d" % (passed, len(legs)), "legs": legs},
                     ensure_ascii=False))
    return 0 if passed == len(legs) else 1


# ------------------------------------------------------------------------------- entry
def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", nargs="?", default="run",
                    choices=["run", "check", "verify", "selftest", "show"])
    args = ap.parse_args(argv)
    if args.cmd == "run":
        face = build()
        dated, _latest = _write(face)
        print(json.dumps({"face": os.path.relpath(dated, ROOT).replace("\\", "/"),
                          "verdict": face["verdict"],
                          "summary": {k: v for k, v in face["summary"].items()
                                      if not isinstance(v, (list, dict))}},
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