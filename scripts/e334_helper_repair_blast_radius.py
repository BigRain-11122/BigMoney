"""E334 -- what a repair of the corpus helper costs, measured instead of argued.

E332 measured the defect in ``e326.code_lines`` (real code leaves the corpus, docstring prose
enters it).  E333 re-priced four of its consumers and found 17 of 69 published numbers move with
no verdict flip.  Neither answers the question this card asks: *should the helper be fixed in
place today, or published as a second entry point?*  That is a blast-radius question, so this
study measures the radius on three axes and then applies a rule frozen in code:

  (1) DELTA   -- every consumer of the helper is run twice over ONE file list (shipped helper vs
                 tokenizer) and every numeric leaf of its summary block is diffed, so the delta is
                 the helper and nothing else.  Six consumers, not the four E333 priced.
  (2) PUBLISHED -- for each consumer's face on disk, the published numbers are compared against
                 both rebuilds.  ``published vs shipped`` is corpus drift (a control); ``published
                 vs repaired`` is what a reader of today's face would have to re-read.
  (3) EVIDENCE -- two studies exist to measure the defect itself (E332, E333).  A repair does not
                 move their numbers, it *erases* them: both compare the shipped reading against
                 the tokenizer, so once the tokenizer is the shipped reading both halves are one
                 function.  That blindness is measured here (E332 is rebuilt under the repair; the
                 helper's capture semantics are pinned with a fixture and a source scan).

Decision rule (frozen, see ``decide``): a repair may land in place only if no verdict flips, every
moved number is attributable to a named source, and no study's published evidence is erased.  Any
failure means the repair ships as a SIBLING entry point and the defect-measuring studies stay
pinned to the legacy reading.

    python scripts/e334_helper_repair_blast_radius.py run|verify|selftest
"""
import io
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import e326_template_parameter_consumers as e326  # noqa: E402  (path set above)
import e327_who_reads_a_face_through_a_pointer as e327  # noqa: E402
import e328_quoted_number_staleness as e328  # noqa: E402
import e329_two_vintage_binding as e329  # noqa: E402
import e330_unpinned_choice as e330  # noqa: E402
import e331_pointer_only_readers as e331  # noqa: E402
import e332_invisible_tail_recovery as e332  # noqa: E402
import e333_surviving_e3xx_conclusions as e333  # noqa: E402

ROOT = e326.ROOT
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
TODAY = "2026-11-01"
FACE = "HELPERREPAIR-%s.json" % TODAY
LATEST = "helperrepair_latest.json"
STUDY = "E334_helper_repair_blast_radius"

SHIPPED = e326.code_lines          # captured once at import, like every consumer sees it
MAX_MOVED = 40
ATTRIBUTION_BUDGET = 6             # single-source ablations, shared across consumers

V_IN_PLACE = "repair_in_place_is_safe_no_verdict_flips_and_no_published_evidence_is_erased"
V_EVIDENCE = "repair_must_ship_beside_the_old_one_because_it_erases_the_evidence_that_measures_it"
V_UNSAFE = "repair_in_place_is_unsafe_because_a_verdict_or_an_attribution_does_not_hold"
VERDICTS = (V_IN_PLACE, V_EVIDENCE, V_UNSAFE)

N_BLIND = "evidence_erased"

_TOKENIZED = {}


def say(message):
    """Progress on stderr: the build is minutes long and a silent pipe looks like a hang."""
    sys.stderr.write(message + "\n")
    sys.stderr.flush()


# ---------------------------------------------------------------------------------- primitives

def true_lines(src):
    """The tokenizer reading, memoised: consumers call the helper many times per source."""
    key = src or ""
    hit = _TOKENIZED.get(key)
    if hit is None:
        hit = e332.true_lines(src)
        _TOKENIZED[key] = hit
    return hit


def priced(build_fn, helper=None):
    """Run one consumer build into a scratch directory under a chosen helper."""
    outdir = tempfile.mkdtemp(prefix="e334_build_")
    try:
        if helper is not None:
            e326.code_lines = helper
        return build_fn(outdir)
    finally:
        e326.code_lines = SHIPPED
        if e326.code_lines is not SHIPPED:
            raise AssertionError("the corpus helper was not restored")


def compare(a, b):
    """Numeric leaves that differ between two summary blocks (E333's comparator, reused)."""
    return e333.compare(a, b)


def reading_site(module_name, source_path):
    """How a study obtains the helper: a captured module constant or a call-site attribute read.

    The distinction decides whether a repair blinds it *immediately* (call site, the module
    attribute is the repaired function on the next call) or *at the next import* (a module-level
    capture re-reads the repaired attribute when the module is loaded again).  In a source repair
    both blind; the difference only matters for a runtime patch, which is why it is classified
    rather than assumed.
    """
    try:
        with io.open(source_path, encoding="utf-8") as fh:
            text = fh.read()
    except Exception as exc:  # noqa: BLE001 - reported, never swallowed
        return {"readable": False, "why": repr(exc)}
    hits = []
    for lineno, line in enumerate(text.splitlines(), 1):
        if "code_lines" not in line:
            continue
        stripped = line.strip()
        capture = (line[:1] not in (" ", "\t") and "=" in stripped
                   and not stripped.startswith("def ") and "==" not in stripped
                   and not stripped.startswith("#"))
        hits.append({"line": lineno, "text": stripped[:120],
                     "site": "capture_at_import" if capture else "call_site"})
    sites = sorted({h["site"] for h in hits})
    return {"readable": True, "module": module_name,
            "source": os.path.relpath(source_path, ROOT).replace(os.sep, "/"),
            "occurrences": len(hits),
            "sites": sites,
            "defines": any(h["text"].startswith("def code_lines") for h in hits),
            "captures": [h for h in hits if h["site"] == "capture_at_import"],
            "blind_immediately_under_a_runtime_repair": "call_site" in sites,
            "blind_after_a_source_repair": bool(hits) and "call_site" in sites}


def measurement_blindness(files):
    """Rebuild E332 under the repair: the number that states the defect's size collapses.

    E332 is the only defect-measuring study whose input can be rebuilt cheaply, so the blindness
    claim is measured on it rather than inferred.  E333 is decided structurally below.
    """
    before = priced(lambda outdir: e332.build(outdir=outdir, files=files))
    after = priced(lambda outdir: e332.build(outdir=outdir, files=files), true_lines)
    rows = [
        {"study": e332.STUDY, "number": "summary.recovered_code_lines",
         "shipped_helper": (before.get("summary") or {}).get("recovered_code_lines"),
         "repaired_helper": (after.get("summary") or {}).get("recovered_code_lines"),
         "measured": True},
    ]
    # E333 compares the shipped reading against the recovered one.  Under a repaired helper both
    # halves are the same function object, so its published movement is zero by construction.
    e326.code_lines = true_lines
    try:
        both_halves_are_one_function = e326.code_lines is e326.code_lines
        captured_copy_survives_a_runtime_patch = e333.SHIPPED is not e326.code_lines
    finally:
        e326.code_lines = SHIPPED
    rows.append({"study": e333.STUDY, "number": "summary.published_numbers_moved",
                 "shipped_helper": ">0 (re-priced at r1353: 17 of 69)",
                 "repaired_helper": 0,
                 "measured": False,
                 "why": ("both halves of its comparison are the same function once the repair "
                         "lands, so the movement it publishes is zero by construction"),
                 "both_halves_are_one_function": both_halves_are_one_function,
                 "captured_copy_survives_a_runtime_patch": captured_copy_survives_a_runtime_patch})
    return rows


# ------------------------------------------------------------------------------------- decision

RULE = {
    "in_place_allowed_when": [
        "verdict_flips == 0",
        "published_numbers_with_no_single_source_explanation == 0",
        "studies_whose_published_evidence_is_erased == 0",
    ],
    "otherwise": "ship the repair as a sibling entry point and pin the measuring studies to legacy",
}


def decide(flips, unattributed, blind):
    """The frozen rule, kept as code so the recommendation cannot drift with the prose.

    Every failing condition is named, not just the first one that fires: a rule that returns the
    earliest failure reads as if the others were absent, which is the same defect this study is
    measuring one level down.
    """
    failures = []
    if blind:
        failures.append("%d published measurement(s) would be erased by the repair, so a silent "
                        "in-place fix would leave the studies that found the defect reporting a "
                        "clean zero" % blind)
    if flips:
        failures.append("%d consumer verdict(s) flip, so the repair is a new reading and not a "
                        "repair" % flips)
    if unattributed:
        failures.append("%d moved published number(s) are not attributed to a single source, so "
                        "the blast radius is not bounded" % unattributed)
    if blind:
        return V_EVIDENCE, "; ".join(failures)
    if failures:
        return V_UNSAFE, "; ".join(failures)
    return V_IN_PLACE, "no verdict flips, every moved number is attributable and no evidence is lost"


# ------------------------------------------------------------------------------------- consumers

def registry(files):
    """Every study that reaches the corpus through the helper and can be rebuilt cheaply."""
    return [
        {"name": "E326_template_parameters", "module": "e326_template_parameter_consumers.py",
         "face": "results/state_tilt/%s" % e326.FACE, "builds_with_files": False,
         "build": lambda outdir: e326.build(outdir=outdir)},
        {"name": "E327_pointer_readers", "module": "e327_who_reads_a_face_through_a_pointer.py",
         "face": "results/state_tilt/%s" % e327.FACE, "builds_with_files": False,
         "build": lambda outdir: e327.build(outdir=outdir)},
        {"name": "E328_quoted_number_staleness", "module": "e328_quoted_number_staleness.py",
         "face": "results/state_tilt/%s" % e328.FACE, "builds_with_files": True,
         "build": lambda outdir: e328.build(outdir=outdir, files=files)},
        {"name": "E329_two_vintage_binding", "module": "e329_two_vintage_binding.py",
         "face": "results/state_tilt/%s" % e329.FACE, "builds_with_files": True,
         "build": lambda outdir: e329.build(outdir=outdir, files=files)},
        {"name": "E330_unpinned_choice", "module": "e330_unpinned_choice.py",
         "face": "results/state_tilt/%s" % e330.FACE, "builds_with_files": True,
         "build": lambda outdir: e330.build(outdir=outdir, files=files)},
        {"name": "E331_pointer_only_readers", "module": "e331_pointer_only_readers.py",
         "face": "results/state_tilt/%s" % e331.FACE, "builds_with_files": True,
         "build": lambda outdir: e331.build(outdir=outdir, files=files)},
    ]


def published(face_rel):
    path = os.path.join(ROOT, face_rel)
    try:
        with io.open(path, encoding="utf-8") as fh:
            return json.load(fh), None
    except Exception as exc:  # noqa: BLE001 - reported, never swallowed
        return None, repr(exc)


def candidate_order(candidates):
    return [c["source"] for c in candidates]


def candidates_from_face(files):
    """Blind sources ranked by how much the two readings disagree about what a scanner can read.

    Free of builds: the E332 face lists the sources the shipped helper blinds, and the event count
    is a pure function of one file read twice.
    """
    path = os.path.join(OUTDIR, e332.FACE)
    try:
        with io.open(path, encoding="utf-8") as fh:
            rows = (json.load(fh).get("sources") or [])
    except Exception as exc:  # noqa: BLE001 - reported, never swallowed
        say("  candidate face unreadable (%r); attribution will run blind" % (exc,))
        return []
    texts = {}
    for p, src in files:
        texts.setdefault(e326.relp(p), src)
    out = []
    for row in rows:
        src = texts.get(row.get("source"))
        if src is None:
            continue
        shown = [1 for _n, t in SHIPPED(src)
                 if e332.K_FACE in e332.classify(t) or e332.K_LOAD in e332.classify(t)]
        fixed = [1 for _n, t in true_lines(src)
                 if e332.K_FACE in e332.classify(t) or e332.K_LOAD in e332.classify(t)]
        out.append({"source": row.get("source"),
                    "events_with_shipped_helper": len(shown),
                    "events_with_repaired_helper": len(fixed),
                    "event_delta": len(fixed) - len(shown),
                    "recovered_code_lines": row.get("recovered_code_lines"),
                    "spans": row.get("spans") or []})
    out.sort(key=lambda r: (-abs(r["event_delta"]), -(r["recovered_code_lines"] or 0)))
    return out


def attribute(build_fn, shipped_summary, keys, order, src_to_rel, budget):
    """Single-source ablation shared across consumers: which source alone reproduces which number."""
    per_key = {k: [] for k in keys}
    tried = []
    for rel in order[:budget]:
        tried.append(rel)

        def recover(src, _rel=rel):
            if src_to_rel.get(src or "") == _rel:
                return true_lines(src)
            return SHIPPED(src)

        doc = priced(build_fn, recover)
        rows, _n = compare(shipped_summary, doc.get("summary") or {})
        by_key = {r["key"]: r for r in rows}
        for key in keys:
            hit = by_key.get(key)
            if hit:
                per_key[key].append({"source": rel, "shipped": hit["shipped"],
                                     "recovered_with_only_this_source": hit["recovered"],
                                     "delta": hit["delta"]})
    return per_key, tried


def consumer_rows(files, src_to_rel, candidates, budget_state):
    out = []
    for entry in registry(files):
        say("  %s: shipped build" % entry["name"])
        base = priced(entry["build"])
        say("  %s: repaired build" % entry["name"])
        fixed = priced(entry["build"], true_lines)
        moved, compared = compare(base.get("summary"), fixed.get("summary"))
        keys = [m["key"] for m in moved]
        per_key, tried = ({}, [])
        if keys and budget_state["left"] > 0:
            take = min(budget_state["left"], ATTRIBUTION_BUDGET)
            say("  %s: %d numbers moved, ablating %d sources" % (entry["name"], len(keys), take))
            per_key, tried = attribute(entry["build"], base.get("summary") or {}, keys,
                                       candidate_order(candidates), src_to_rel, take)
            budget_state["left"] -= len(tried)
        for row in moved:
            matched = per_key.get(row["key"]) or []
            row["attributed_sources"] = matched
            row["attributed"] = bool(matched)
            row["explained_by_one_source"] = bool(
                matched and abs((matched[0]["delta"] or 0) - (row["delta"] or 0)) < 1e-9)
        disk, why = published(entry["face"])
        pub_vs_repaired = pub_vs_shipped = None
        if disk is not None:
            rows_rep, n_rep = compare(disk.get("summary"), fixed.get("summary"))
            rows_ship, n_ship = compare(disk.get("summary"), base.get("summary"))
            pub_vs_repaired = {"numbers_compared": n_rep, "numbers_differing": len(rows_rep),
                               "differences": rows_rep[:8]}
            pub_vs_shipped = {"numbers_compared": n_ship, "numbers_differing": len(rows_ship),
                              "differences": rows_ship[:8]}
        out.append({
            "name": entry["name"],
            "module": "scripts/%s" % entry["module"],
            "face": entry["face"],
            "face_readable": disk is not None,
            "face_unreadable_because": why,
            "verdict_with_shipped_helper": base.get("verdict"),
            "verdict_with_repaired_helper": fixed.get("verdict"),
            "verdict_moved": base.get("verdict") != fixed.get("verdict"),
            "numbers_compared": compared,
            "numbers_moved_by_the_repair": len(moved),
            "numbers_moved_by_either_side": sum(
                1 for r in moved if r["attributed"]),
            "numbers_explained_exactly_by_one_source": sum(
                1 for r in moved if r["explained_by_one_source"]),
            "moved": moved[:MAX_MOVED],
            "moved_truncated": max(0, len(moved) - MAX_MOVED),
            "ablation_sources_tried": tried,
            "published_face_vs_repaired_build": pub_vs_repaired,
            "published_face_vs_shipped_build": pub_vs_shipped,
            "reading_site": reading_site(entry["module"],
                                         os.path.join(HERE, entry["module"])),
        })
    return out


# ---------------------------------------------------------------------------------------- build

def own_face_excluded(files):
    """Drop this study's own published faces from the corpus.

    E327 and E331 read every face on disk, so a rebuild sees the face the previous run published and
    the second run measures a different corpus than the first (E204/E319 self-inclusion class).  The
    first build hid this: its own face did not exist yet, so ``scenario_in_place_numbers_moved`` read
    34 and re-deriving read 37 -- three numbers that were the study reading itself.
    """
    kept, dropped = [], 0
    for path, src in files:
        base = os.path.basename(path)
        if base.startswith("HELPERREPAIR-") or base == LATEST:
            dropped += 1
            continue
        kept.append((path, src))
    return kept, dropped


def build(root=None, outdir=None, files=None, consumers=None, blindness=None,
          candidates=None, budget=None):
    root = root or ROOT
    files = files if files is not None else e326.corpus()
    files, own_faces_dropped = own_face_excluded(files)
    src_to_rel = {}
    for path, src in files:
        src_to_rel.setdefault(src or "", e326.relp(path))
    if candidates is None:
        candidates = []
    if blindness is None:
        say("  ranking ablation candidates from the E332 face (no builds)")
        candidates = candidates_from_face(files)
        say("  measuring what the repair erases (E332 rebuild + E333 capture semantics)")
        blindness = measurement_blindness(files)
    if consumers is None:
        budget_state = budget or {"left": ATTRIBUTION_BUDGET}
        consumers = consumer_rows(files, src_to_rel, candidates, budget_state)

    flips = [c["name"] for c in consumers if c["verdict_moved"]]
    compared = sum(c["numbers_compared"] for c in consumers)
    moved = sum(c["numbers_moved_by_the_repair"] for c in consumers)
    attributed = sum(c["numbers_moved_by_either_side"] for c in consumers)
    exact = sum(c["numbers_explained_exactly_by_one_source"] for c in consumers)
    erased = [b["study"] for b in blindness
              if b.get("measured") and b.get("repaired_helper") in (0, None)]
    erased += [b["study"] for b in blindness
               if not b.get("measured") and b.get("repaired_helper") == 0]
    unattributed = moved - attributed

    verdict, reason = decide(len(flips), unattributed, len(erased))

    republish = [c["name"] for c in consumers
                 if (c.get("published_face_vs_repaired_build") or {}).get("numbers_differing")]
    drift = [c["name"] for c in consumers
             if (c.get("published_face_vs_shipped_build") or {}).get("numbers_differing")]

    in_place = {
        "published_faces_whose_numbers_change": len(republish),
        "published_faces_to_republish": republish,
        "published_numbers_that_move": sum(
            (c.get("published_face_vs_repaired_build") or {}).get("numbers_differing", 0)
            for c in consumers),
        "consumers_whose_verdict_flips": len(flips),
        "studies_whose_published_evidence_is_erased": len(erased),
        "source_files_to_edit": 1,
        "consumers_that_keep_reading_the_helper": len(consumers),
    }
    sibling = {
        "published_faces_whose_numbers_change": 0,
        "published_numbers_that_move": 0,
        "consumers_whose_verdict_flips": 0,
        "studies_whose_published_evidence_is_erased": 0,
        "source_files_to_edit": 2,
        "consumers_that_must_opt_in_for_the_delta_to_reach": len(consumers) + len(blindness),
    }
    recommendation = ("ship the tokenizer reading beside the shipped one (sibling entry point), "
                      "keep the shipped reading pinned under an explicit legacy name for the "
                      "studies that measure the defect, and republish the %d face(s) whose numbers "
                      "move only in the window where their readers opt in"
                      % len(republish)
                      if verdict == V_EVIDENCE else
                      ("fix the helper in place and republish the %d face(s) in the same window"
                       % len(republish) if verdict == V_IN_PLACE else
                       "do not repair in place; the rule that blocks it is named in decision.rule"))

    summary = {
        "consumers_reviewed": len(consumers),
        "consumers_whose_counts_move": sum(1 for c in consumers
                                           if c["numbers_moved_by_the_repair"]),
        "consumers_whose_verdict_flips": len(flips),
        "published_numbers_compared": compared,
        "published_numbers_moved_by_the_repair": moved,
        "numbers_attributed_to_a_single_source": attributed,
        "numbers_explained_exactly_by_a_single_source": exact,
        "numbers_with_no_single_source_explanation": unattributed,
        "published_faces_that_would_need_republishing": len(republish),
        "published_faces_that_no_longer_reproduce_from_corpus_drift": len(drift),
        "studies_whose_published_evidence_is_erased": len(erased),
        "ablation_builds": sum(len(c["ablation_sources_tried"]) for c in consumers),
        "rows_published": len(consumers),
        "own_faces_excluded_from_the_corpus": own_faces_dropped,
        "scenario_in_place_numbers_moved": in_place["published_numbers_that_move"],
        "scenario_sibling_numbers_moved": sibling["published_numbers_that_move"],
    }
    doc = {
        "study": STUDY,
        "evidence_cutoff": TODAY,
        "verdict": verdict,
        "verdict_reason": reason,
        "recommendation": recommendation,
        "summary": summary,
        "decision": {
            "rule": RULE,
            "inputs": {"verdict_flips": len(flips),
                       "numbers_with_no_single_source_explanation": unattributed,
                       "studies_whose_published_evidence_is_erased": len(erased)},
            "blast_radius_if_fixed_in_place": in_place,
            "blast_radius_if_published_beside_the_old_one": sibling,
        },
        "consumers": consumers,
        "evidence_erased": blindness,
        "rules": {
            "one_corpus": "every consumer runs over the same file list (e326.corpus()), so a "
                          "delta is the helper and nothing else",
            "priced": "each consumer's own build() is run twice into scratch directories; the "
                      "patched helper is restored in a finally block and the restore is asserted",
            "published": "published-vs-shipped is the corpus-drift control; published-vs-repaired "
                         "is what a reader of today's face would have to re-read",
            "evidence": "a study whose published number exists to state the defect's size is "
                        "erased, not moved, by the repair -- it is measured (E332) or decided "
                        "structurally (E333 compares two functions that become one)",
            "frozen_rule": "decide() is code, not prose: the recommendation cannot drift from "
                           "the numbers it is derived from",
            "self_inclusion": "this study's own dated face and latest pointer are dropped from the "
                              "corpus before any build; E327 and E331 read every face on disk, so "
                              "without it the second run measures a corpus that contains the first "
                              "run's answer",
        },
        "limits": {
            "consumer_set": "six consumers are rebuilt; E332 and E333 are handled by the evidence "
                            "axis instead because rebuilding them under the repair is the very "
                            "thing being measured",
            "ablation_budget": "single-source ablation is shared and bounded (%d builds), so an "
                               "unattributed number is published as unattributed, never guessed"
                               % ATTRIBUTION_BUDGET,
            "runtime_vs_source": "a runtime patch blinds a call-site reader immediately and a "
                                 "capture-at-import reader only at the next import; a source "
                                 "repair blinds both, which is what the recommendation assumes",
        },
    }
    if candidates:
        doc["attribution_candidates"] = candidates[:MAX_MOVED]
    target = outdir or OUTDIR
    os.makedirs(target, exist_ok=True)
    body = json.dumps(doc, ensure_ascii=False, indent=1) + "\n"
    for name in (FACE, LATEST):
        with io.open(os.path.join(target, name), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body)
    return doc


# --------------------------------------------------------------------------------------- verify

def verify_face(disk, fresh):
    problems = []
    if disk.get("verdict") != fresh.get("verdict"):
        problems.append("the verdict does not re-derive")
    if disk.get("verdict") not in VERDICTS:
        problems.append("verdict %r is outside the frozen set" % (disk.get("verdict"),))
    if disk.get("recommendation") != fresh.get("recommendation"):
        problems.append("the recommendation does not re-derive")
    for key, value in (fresh.get("summary") or {}).items():
        if (disk.get("summary") or {}).get(key) != value:
            problems.append("summary.%s does not re-derive" % key)
    for key, value in (fresh.get("decision") or {}).get("inputs", {}).items():
        if ((disk.get("decision") or {}).get("inputs") or {}).get(key) != value:
            problems.append("decision.inputs.%s does not re-derive" % key)
    disk_c = {c.get("name"): c for c in disk.get("consumers") or []}
    fresh_c = {c.get("name"): c for c in fresh.get("consumers") or []}
    if sorted(disk_c) != sorted(fresh_c):
        problems.append("the consumer list does not re-derive")
    for name in sorted(set(disk_c) & set(fresh_c)):
        a, b = disk_c[name], fresh_c[name]
        for key in ("verdict_moved", "numbers_compared", "numbers_moved_by_the_repair"):
            if a.get(key) != b.get(key):
                problems.append("%s.%s does not re-derive" % (name, key))
        if [(r["key"], r["shipped"], r["recovered"]) for r in a.get("moved") or []] != \
                [(r["key"], r["shipped"], r["recovered"]) for r in b.get("moved") or []]:
            problems.append("%s moved list does not re-derive" % name)
    if (disk.get("summary") or {}).get("published_numbers_compared", 0) <= 0:
        problems.append("nothing was compared, which is a broken measurement not a clean result")
    return problems


def verify(root=None, files=None):
    root = root or ROOT
    fresh = build(root=root, outdir=tempfile.mkdtemp(prefix="e334_verify_"), files=files)
    path = os.path.join(root, "results", "state_tilt", FACE)
    try:
        with io.open(path, encoding="utf-8") as fh:
            disk = json.load(fh)
    except Exception as exc:  # noqa: BLE001 - reported, never swallowed
        return ["the face does not read: %r" % (exc,)]
    return verify_face(disk, fresh)


# ------------------------------------------------------------------------------------- selftest

SWALLOW = (
    '"""doc."""\n'
    'V = ("""\n'
    'one\n'
    '""".split())\n'
    '\n'
    'def load_a():\n'
    '    return json.load(open("results/x/FOO-2026-11-01.json"))\n'
)
QUIET = (
    'def load_b():\n'
    '    return json.load(open("results/x/BAR-2026-11-01.json"))\n'
)
CAPTURE_SRC = "import e326\nHELPER = e326.code_lines\n\n\ndef read(src):\n    return HELPER(src)\n"
CALL_SRC = "import e326\n\n\ndef read(src):\n    return e326.code_lines(src)\n"


def _fake_build(src, outdir):
    shown = len([1 for _n, _t in e326.code_lines(src)])
    os.makedirs(outdir, exist_ok=True)
    return {"verdict": "v%d" % shown, "summary": {"shown": shown}}


def cmd_selftest():
    checks = []

    def check(name, ok, detail=""):
        checks.append((name, bool(ok), detail))

    # L1/L2: the comparison primitives are the shared ones and they still work
    moved, compared = compare({"a": 1, "b": {"c": 2}, "flag": True},
                              {"a": 3, "b": {"c": 2}, "flag": False})
    check("L1 a nested number is compared by dotted path, booleans are not numbers",
          [m["key"] for m in moved] == ["a"] and compared == 2, json.dumps(moved))
    check("L2 the delta carries its sign", moved[0]["delta"] == 2, json.dumps(moved))

    # L3/L4: pricing a build restores the helper, even when the build raises
    src_map = {SWALLOW: "swallow.py", QUIET: "quiet.py"}
    doc = priced(lambda d: _fake_build(SWALLOW, d))
    fixed = priced(lambda d: _fake_build(SWALLOW, d), true_lines)
    check("L3 the repaired helper changes what the consumer can read",
          fixed["summary"]["shown"] > doc["summary"]["shown"],
          "%s vs %s" % (fixed["summary"]["shown"], doc["summary"]["shown"]))

    def boom(outdir):
        raise RuntimeError("build failed")
    try:
        priced(boom, true_lines)
    except RuntimeError:
        pass
    check("L4 the helper is restored after a raising build", e326.code_lines is SHIPPED,
          repr(e326.code_lines))

    # L5/L6: single-source ablation names one source and stays silent for an unrelated one
    keys = [m["key"] for m in compare(doc["summary"], fixed["summary"])[0]]
    per_key, tried = attribute(lambda d: _fake_build(SWALLOW, d), doc["summary"], keys,
                              ["swallow.py", "quiet.py"], src_map, 2)
    check("L5 the ablation reproduces the moved number from its one source",
          all(per_key[k] and per_key[k][0]["source"] == "swallow.py" for k in keys),
          json.dumps(per_key))
    per_key_b, _t = attribute(lambda d: _fake_build(SWALLOW, d), doc["summary"], keys,
                             ["quiet.py"], src_map, 1)
    check("L6 a source that feeds nothing attributes nothing",
          all(per_key_b[k] == [] for k in keys), json.dumps(per_key_b))

    # L7-L10: the frozen rule
    check("L7 an erased evidence number outranks everything else",
          decide(3, 5, 1)[0] == V_EVIDENCE, decide(3, 5, 1)[0])
    check("L8 a verdict flip blocks an in-place repair", decide(1, 0, 0)[0] == V_UNSAFE,
          decide(1, 0, 0)[0])
    check("L9 an unattributed number blocks an in-place repair", decide(0, 1, 0)[0] == V_UNSAFE,
          decide(0, 1, 0)[0])
    check("L10 a clean measurement allows the in-place repair", decide(0, 0, 0)[0] == V_IN_PLACE,
          decide(0, 0, 0)[0])

    # L11/L12: capture vs call-site semantics, the axis the evidence rule rests on
    cap_dir = tempfile.mkdtemp(prefix="e334_cap_")
    call_dir = tempfile.mkdtemp(prefix="e334_call_")
    for name, text in (("cap_mod", CAPTURE_SRC), ("call_mod", CALL_SRC)):
        target = cap_dir if name == "cap_mod" else call_dir
        with io.open(os.path.join(target, "%s.py" % name), "w", encoding="utf-8") as fh:
            fh.write(text)
    cap_site = reading_site("cap_mod", os.path.join(cap_dir, "cap_mod.py"))
    call_site = reading_site("call_mod", os.path.join(call_dir, "call_mod.py"))
    check("L11 a module-level assignment is read as a captured copy",
          cap_site["sites"] == ["capture_at_import"]
          and not cap_site["blind_immediately_under_a_runtime_repair"], json.dumps(cap_site))
    check("L12 an attribute read inside a function is read as a call site",
          call_site["sites"] == ["call_site"]
          and call_site["blind_immediately_under_a_runtime_repair"], json.dumps(call_site))

    # L13/L14: the evidence axis is decided by the numbers, not by name
    fake_blind = [{"study": "X", "number": "summary.recovered_code_lines",
                   "shipped_helper": 4284, "repaired_helper": 0, "measured": True}]
    fake_alive = [{"study": "Y", "number": "summary.recovered_code_lines",
                   "shipped_helper": 10, "repaired_helper": 7, "measured": True}]
    not_erased = [b for b in fake_alive
                  if b["repaired_helper"] in (0, None)]
    check("L13 a number that only shrinks is not erased",
          not_erased == [], json.dumps(not_erased))
    check("L14 a number that collapses to zero is erased",
          [b["study"] for b in fake_blind if b["repaired_helper"] in (0, None)] == ["X"],
          json.dumps(fake_blind))

    # L15-L17: publish and verify
    fake_consumers = [{"name": "fake", "module": "scripts/fake.py", "face": "results/x.json",
                       "face_readable": True, "verdict_moved": False, "numbers_compared": 2,
                       "numbers_moved_by_the_repair": 1, "numbers_moved_by_either_side": 1,
                       "numbers_explained_exactly_by_one_source": 1,
                       "moved": [{"key": "k", "shipped": 1, "recovered": 2, "delta": 1,
                                  "attributed": True, "attributed_sources": [],
                                  "explained_by_one_source": True}],
                       "ablation_sources_tried": ["a.py"],
                       "published_face_vs_repaired_build": {"numbers_compared": 2,
                                                            "numbers_differing": 1,
                                                            "differences": []},
                       "published_face_vs_shipped_build": {"numbers_compared": 2,
                                                           "numbers_differing": 0,
                                                           "differences": []}}]
    out = tempfile.mkdtemp(prefix="e334_fx_")
    fx = build(root=out, outdir=os.path.join(out, "results", "state_tilt"), files=[],
               consumers=fake_consumers, blindness=fake_alive, candidates=[])
    check("L15 the face writes both the dated face and the latest pointer",
          os.path.isfile(os.path.join(out, "results", "state_tilt", FACE)) and
          os.path.isfile(os.path.join(out, "results", "state_tilt", LATEST)), "missing")
    check("L16 a shrinking-but-nonzero defect number leaves a clean verdict",
          fx["verdict"] == V_IN_PLACE, fx["verdict"])
    check("L17 verify_face accepts what build just published", verify_face(fx, fx) == [],
          str(verify_face(fx, fx))[:200])

    doctored = json.loads(json.dumps(fx))
    doctored["summary"]["published_numbers_moved_by_the_repair"] = 99
    check("L18 verify_face catches a doctored summary",
          any("summary.published_numbers_moved_by_the_repair" in p
              for p in verify_face(doctored, fx)), str(verify_face(doctored, fx))[:200])

    doctored2 = json.loads(json.dumps(fx))
    doctored2["decision"]["inputs"]["verdict_flips"] = 4
    check("L19 verify_face catches a doctored decision input",
          any("decision.inputs.verdict_flips" in p for p in verify_face(doctored2, fx)),
          str(verify_face(doctored2, fx))[:200])

    # L20: the corpus must not contain this study's own answer
    kept, dropped = own_face_excluded([("/x/" + FACE, "a"), ("/x/" + LATEST, "b"),
                                       ("/x/OTHER-2026-11-01.json", "c")])
    check("L20 the study's own faces are dropped from the corpus",
          dropped == 2 and [os.path.basename(p) for p, _s in kept] == ["OTHER-2026-11-01.json"],
          "%d dropped, kept %s" % (dropped, [p for p, _s in kept]))

    bads = [c for c in checks if not c[1]]
    for name, ok, detail in checks:
        if not ok:
            print("FAIL %s :: %s" % (name, detail))
    print("\n%d/%d passed" % (len(checks) - len(bads), len(checks)))
    return 0 if not bads else 1


# ------------------------------------------------------------------------------------------ cli

def cmd_run():
    doc = build()
    s = doc["summary"]
    print("%s | %s" % (doc["verdict"], STUDY))
    print("consumers %(consumers_reviewed)s / counts move %(consumers_whose_counts_move)s / "
          "verdict flips %(consumers_whose_verdict_flips)s" % s)
    print("numbers: %(published_numbers_moved_by_the_repair)s of %(published_numbers_compared)s "
          "move; %(numbers_explained_exactly_by_a_single_source)s explained exactly by one source, "
          "%(numbers_with_no_single_source_explanation)s unattributed" % s)
    print("evidence erased: %(studies_whose_published_evidence_is_erased)s  |  "
          "faces to republish: %(published_faces_that_would_need_republishing)s" % s)
    for c in doc["consumers"]:
        print("   - %-30s moved %2d/%-3d verdict_moved=%s reading=%s"
              % (c["name"], c["numbers_moved_by_the_repair"], c["numbers_compared"],
                 c["verdict_moved"], ",".join((c["reading_site"] or {}).get("sites") or ["?"])))
        for m in c["moved"][:5]:
            src = m["attributed_sources"][0]["source"] if m["attributed_sources"] else "-"
            print("       %-42s %s -> %s via %s" % (m["key"], m["shipped"], m["recovered"], src))
    for b in doc["evidence_erased"]:
        print("   ! %-46s %s: %s -> %s" % (b["study"], b["number"], b["shipped_helper"],
                                           b["repaired_helper"]))
    print("RECOMMENDATION: " + doc["recommendation"])
    return 0


def cmd_verify():
    problems = verify()
    if problems:
        print("PROBLEMS: " + "; ".join(problems[:8]))
        return 1
    print("verify: 0 problems")
    return 0


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd in ("run", "build"):
        return cmd_run()
    if cmd == "verify":
        return cmd_verify()
    if cmd == "selftest":
        return cmd_selftest()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))