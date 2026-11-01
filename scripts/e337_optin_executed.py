"""E337 -- execute the opt-in E336 only priced, and audit it against a drift control.

E336 refused to rank the six consumers but published a floor: E330 is cheapest on *both* readings
(0 numbers moved by the delta, 1 published number) and keeps its published verdict.  A
recommendation that names a floor is not a measurement of the opt-in, so this study takes the floor:
one consumer (scripts/e330_unpinned_choice.py) is moved onto ``e326.code_lines_tokenized``, its
published face is republished, and the before/after diff is published number by number.

The diff alone would lie, because the published face is not only stale with respect to the *reading*
-- it is also stale with respect to the *corpus*.  E330 counts its population over e326.corpus()
(every ``.py`` under scripts/Tools/live/monitor/firm), so any script that lands after the face was
written moves ``sources_scanned`` by one.  A naive before/after diff would bill that drift to the
reading.  So three builds are made over ONE file list:

    before    the archived published face, as a reader meets it today
    control   the shipped reading (e329._code_lines), today's corpus
    treatment the tokenized reading, today's corpus

  drift     = before  -> control    (what the corpus did, not the reading)
  total     = before  -> treatment  (what a reader must re-read)
  switch    = control -> treatment  (what the opt-in itself costs)

The switch is applied atomically and reverted when the card's two refusal conditions fire: the
republished face fails to re-verify, or the consumer's published verdict moves.  A revert restores
the source bytes and the archived face, so a refused run leaves the tree as it found it.

Usage:
    python scripts/e337_optin_executed.py run|verify|selftest
"""

import io
import json
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e326_template_parameter_consumers as e326  # noqa: E402  (path set above)
import e329_two_vintage_binding as e329  # noqa: E402

ROOT = e326.ROOT
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
TODAY = "2026-11-01"
FACE = "OPTINSWITCH-%s.json" % TODAY
LATEST = "optinswitch_latest.json"
STUDY = "E337_optin_executed"

CONSUMER_REL = "scripts/e330_unpinned_choice.py"
CONSUMER_MODULE = "e330_unpinned_choice"
CONSUMER_STUDY = "E330_unpinned_choice"
ARCHIVE = "OPTINSWITCH-before-UNPINNEDCHOICE-%s.json" % TODAY
SELF_REL = "scripts/e337_optin_executed.py"

# The one edit this study makes: a local accessor, so the opt-in stays in ONE consumer's file and
# e329's own binding (and every other reader of it) is untouched.
ANCHOR = "ROOT = e326.ROOT\n"
ACCESSOR = (
    "\n"
    "def _lines(src):\n"
    '    """E337 opt-in: this study reads the tokenized corpus (E335\'s landed sibling name).\n'
    "\n"
    "    The accessor is local on purpose: e329._code_lines keeps the shipped reading, so moving\n"
    "    this consumer cannot move anyone else by accident.\n"
    '    """\n'
    "    return e326.code_lines_tokenized(src)\n"
)
CALL_SITES = 4
OLD_CALL = "e329._code_lines("
NEW_CALL = "_lines("
MARKER = "E337 opt-in"
READING_NAME = "code_lines_tokenized"

TOL = 1e-9
MAX_EXAMPLES = 12

V_ADOPT = "one_consumer_moved_onto_the_tokenized_reading_and_its_republished_face_re_derives_with_the_verdict_intact"
V_REFUSE_VERDICT = "the_switch_was_reverted_because_the_consumers_published_verdict_moved"
V_REFUSE_VERIFY = "the_switch_was_reverted_because_the_republished_face_does_not_re_verify"
VERDICTS = (V_ADOPT, V_REFUSE_VERDICT, V_REFUSE_VERIFY)


def say(message):
    """Progress on stderr: three builds take tens of seconds and a silent pipe looks like a hang."""
    sys.stderr.write(message + "\n")
    sys.stderr.flush()


# ---------------------------------------------------------------------------------- the switch

def surface(src):
    """The switched source and whether anything had to change.

    Idempotent by construction: an already-switched file carries the marker and is returned as is.
    A source that does not look like the consumer is refused rather than edited blindly -- the
    anchor and the call-site count are this study's only assumptions about someone else's file.
    """
    if MARKER in src:
        return src, False
    if ANCHOR not in src:
        raise ValueError("the consumer no longer carries the anchor %r" % (ANCHOR,))
    if src.count(OLD_CALL) != CALL_SITES:
        raise ValueError("expected %d call sites, found %d"
                         % (CALL_SITES, src.count(OLD_CALL)))
    out = src.replace(OLD_CALL, NEW_CALL, CALL_SITES)
    out = out.replace(ANCHOR, ANCHOR + ACCESSOR, 1)
    if MARKER not in out or out.count("def _lines(") != 1:
        raise ValueError("the switch did not land as one accessor")
    return out, True


def consumer_path(root=None):
    return os.path.join(root or ROOT, CONSUMER_REL)


def read_text(path):
    with io.open(path, encoding="utf-8", newline="") as fh:
        return fh.read()


def write_text(path, text):
    with io.open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)


def archive_face(doc, root=None):
    """The pre-switch face, kept once.  Never overwritten: on a re-run it *is* the before arm."""
    path = os.path.join(root or ROOT, "results", "state_tilt", ARCHIVE)
    if os.path.exists(path):
        return path, False
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, indent=1, sort_keys=False)
        fh.write("\n")
    return path, True


def load_face(rel, root=None):
    try:
        with io.open(os.path.join(root or ROOT, rel), encoding="utf-8") as fh:
            return json.load(fh), None
    except Exception as exc:  # noqa: BLE001 - reported, never swallowed
        return None, repr(exc)


def consumer_module(fresh=False):
    """The consumer module, imported (or reloaded) so the on-disk switch is what runs."""
    import importlib
    module = sys.modules.get(CONSUMER_MODULE)
    if module is None:
        module = importlib.import_module(CONSUMER_MODULE)
    elif fresh:
        module = importlib.reload(module)
    return module


# ------------------------------------------------------------------------------------- the maths

def leaves(doc, prefix=""):
    """Numeric leaves of a published block, keyed by dotted path (bools are not measurements)."""
    out = {}
    if isinstance(doc, dict):
        for key, value in doc.items():
            out.update(leaves(value, "%s.%s" % (prefix, key) if prefix else str(key)))
    elif isinstance(doc, list):
        for index, value in enumerate(doc):
            out.update(leaves(value, "%s[%d]" % (prefix, index)))
    elif isinstance(doc, (int, float)) and not isinstance(doc, bool):
        out[prefix] = doc
    return out


def numeric_diff(before, after):
    """Every number that moved between two summary blocks, with both readings and the delta."""
    left, right = leaves(before or {}), leaves(after or {})
    compared = [key for key in left if key in right]
    rows = []
    for key in sorted(compared):
        if abs(float(left[key]) - float(right[key])) > TOL:
            rows.append({"key": key, "before": left[key], "after": right[key],
                         "delta": round(float(right[key]) - float(left[key]), 12)})
    return rows, len(compared)


def row_signature(doc):
    """The structural half of a consumer face: what was decided, where, and with which flag."""
    return [(r.get("source"), r.get("line"), r.get("class"), r.get("decider"),
             r.get("pinned"), r.get("swap_changes_today")) for r in (doc.get("rows") or [])]


def _sources(root):
    out = {}
    for sub in ("scripts", "Tools"):
        base = os.path.join(root, sub)
        if not os.path.isdir(base):
            continue
        for name in sorted(os.listdir(base)):
            if not name.endswith(".py"):
                continue
            rel = "%s/%s" % (sub, name)
            try:
                out[rel] = read_text(os.path.join(base, name))
            except Exception:  # noqa: BLE001 - a source we cannot read is not a reader
                continue
    return out


def downstream_studies(root=None):
    """Who rebuilds the consumer's published face, directly and one import further.

    A study that merely imports the consumer's module is not downstream of its *face*, so the needle
    is the face reference itself (``e330.FACE`` or the filename).  One hop is followed because a
    registry hides the reference: E336 reads this face only through E334's registry, so a direct-only
    scan would report the study that ranked it as unaffected.  The cascade E336's per-consumer reading
    measured could not see either hop, because that reading compared ONE face at a time.
    """
    root = root or ROOT
    texts = _sources(root)
    needles = ("UNPINNEDCHOICE", "e330.FACE")
    direct = sorted(rel for rel, src in texts.items()
                    if rel not in (CONSUMER_REL, SELF_REL) and any(n in src for n in needles))
    modules = {".".join(os.path.basename(rel).split(".")[:-1]) for rel in direct}
    imports = [re.compile(r"^\s*(?:import|from)\s+%s\b" % re.escape(m), re.M)
               for m in sorted(modules)]
    further = sorted(rel for rel, src in texts.items()
                     if rel not in direct and rel not in (CONSUMER_REL, SELF_REL)
                     and any(rx.search(src or "") for rx in imports))
    return {"direct": direct, "one_hop_further": further}


def decide(problems, before_verdict, after_verdict):
    """The frozen rule.  A moved verdict outranks a failed re-derivation; both revert."""
    if before_verdict is None or after_verdict is None:
        return V_REFUSE_VERIFY, "one of the two faces is unreadable, so the comparison is blind"
    if before_verdict != after_verdict:
        return V_REFUSE_VERDICT, ("the published verdict moved (%r -> %r), and a switch that "
                                  "changes what the face says is not a free lunch"
                                  % (before_verdict, after_verdict))
    if problems:
        return V_REFUSE_VERIFY, ("the republished face does not re-verify: %s"
                                 % "; ".join(problems[:4]))
    return V_ADOPT, ("the republished face re-derives over today's corpus with its verdict intact, "
                     "so the switch is in and the diff below is what a reader pays")


# ---------------------------------------------------------------------------------------- build

def build(root=None, outdir=None):
    """Switch, republish, verify, and publish the diff -- reverting if either refusal condition fires."""
    root = root or ROOT
    path = consumer_path(root)
    before_src = read_text(path)

    module = consumer_module()
    consumer_face_rel = "results/state_tilt/%s" % module.FACE
    archive_rel = "results/state_tilt/%s" % ARCHIVE
    published, published_why = load_face(consumer_face_rel, root)
    if published is None:
        raise AssertionError("the consumer's published face does not read (%r); publish it with "
                             "its own `run` before opting in" % (published_why,))
    archive_path, newly_archived = archive_face(published, root)
    before, archived_why = load_face(archive_rel, root)
    if before is None:
        raise AssertionError("the before-face archive does not read (%r)" % (archived_why,))

    switched_src, changed = surface(before_src)
    if not changed:
        say("  the consumer is already switched; measuring, not moving")
    else:
        say("  switching %s onto %s" % (CONSUMER_REL, READING_NAME))
        write_text(path, switched_src)
        module = consumer_module(fresh=True)

    say("  treatment build (tokenized reading, today's corpus)")
    treatment = module.build()
    published_rel = consumer_face_rel

    say("  re-verifying the republished face (one more build)")
    problems = module.verify()

    verdict, reason = decide(problems, before.get("verdict"), treatment.get("verdict"))
    reverted = False
    if verdict != V_ADOPT:
        say("  reverting: %s" % reason)
        write_text(path, before_src)
        module = consumer_module(fresh=True)
        module.build()  # restores both the dated face and the latest pointer from the source
        reverted = True

    say("  control build (shipped reading, today's corpus)")
    had_accessor = hasattr(module, "_lines")
    shipped_accessor = getattr(module, "_lines", None)
    try:
        if had_accessor:
            module._lines = e329._code_lines
        control = module.build(outdir=tempfile.mkdtemp(prefix="e337_control_"))
    finally:
        if had_accessor:
            module._lines = shipped_accessor
            if module._lines is not shipped_accessor:
                raise AssertionError("the consumer accessor was not restored")
        elif hasattr(module, "_lines"):
            del module._lines

    drift, drift_compared = numeric_diff(before.get("summary"), control.get("summary"))
    total, total_compared = numeric_diff(before.get("summary"), treatment.get("summary"))
    switch, switch_compared = numeric_diff(control.get("summary"), treatment.get("summary"))
    rows_change = row_signature(control) != row_signature(treatment)
    downstream = downstream_studies(root)

    summary = {
        "consumer": CONSUMER_STUDY,
        "consumer_source": CONSUMER_REL,
        "reading_switched_to": READING_NAME,
        "numbers_compared_drift": drift_compared,
        "numbers_moved_by_corpus_drift": len(drift),
        "numbers_compared_total": total_compared,
        "numbers_moved_before_to_republished": len(total),
        "numbers_compared_switch": switch_compared,
        "numbers_moved_by_the_opt_in": len(switch),
        "switched_source_entries": sum(1 for r in switch if r["key"] == "sources_scanned"),
        "rows_compared": len(row_signature(control)),
        "decision_rows_changed_by_the_reading": int(rows_change),
        "verdict_before": before.get("verdict"),
        "verdict_republished": treatment.get("verdict"),
        "verdict_unchanged": before.get("verdict") == treatment.get("verdict"),
        "sources_scanned_before": (before.get("summary") or {}).get("sources_scanned"),
        "sources_scanned_republished": (treatment.get("summary") or {}).get("sources_scanned"),
        "sources_scanned_control": (control.get("summary") or {}).get("sources_scanned"),
        "verify_problems": len(problems),
        "reverted": bool(reverted),
        "downstream_studies_that_rebuild_this_face": len(downstream["direct"]),
        "downstream_studies_one_hop_further": len(downstream["one_hop_further"]),
        "before_face_archived_this_run": bool(newly_archived),
        "drift_is_the_corpus_not_the_reading": True,
    }
    doc = {
        "study": STUDY,
        "evidence_cutoff": TODAY,
        "verdict": verdict,
        "verdict_reason": reason,
        "summary": summary,
        "decision": {
            "rule": {
                "adopt_if": ["the republished face re-verifies with zero problems",
                             "the consumer's published verdict is unchanged"],
                "otherwise": "restore the source bytes and the archived face; the tree is as found",
                "why_two_arms": ("a bare before/after diff bills corpus growth to the reading, so the "
                                 "shipped reading is rebuilt over TODAY's corpus as a control"),
            },
            "inputs": {
                "verify_problems": len(problems),
                "verdict_changed": before.get("verdict") != treatment.get("verdict"),
                "switched": bool(getattr(module, "_lines", None) is not None) and not reverted,
            },
            "verdict_options": list(VERDICTS),
        },
        "diff": {
            "drift_before_to_control": {"compared": drift_compared, "rows": drift[:MAX_EXAMPLES],
                                        "moved": len(drift),
                                        "truncated": max(0, len(drift) - MAX_EXAMPLES)},
            "total_before_to_republished": {"compared": total_compared,
                                            "rows": total[:MAX_EXAMPLES], "moved": len(total),
                                            "truncated": max(0, len(total) - MAX_EXAMPLES)},
            "switch_control_to_republished": {"compared": switch_compared,
                                              "rows": switch[:MAX_EXAMPLES], "moved": len(switch),
                                              "truncated": max(0, len(switch) - MAX_EXAMPLES)},
        },
        "before_face": {"face": "results/state_tilt/%s" % ARCHIVE,
                        "verdict": before.get("verdict"),
                        "summary": before.get("summary")},
        "republished_face": {"face": published_rel, "verdict": treatment.get("verdict"),
                             "summary": treatment.get("summary")},
        "control_face": {"reading": "e329._code_lines (shipped)",
                         "summary": control.get("summary")},
        "optin_allowlist": ([{"consumer": CONSUMER_REL, "study": SELF_REL,
                              "face": "results/state_tilt/%s" % FACE, "adopted": True}]
                            if verdict == V_ADOPT else []),
        "downstream_studies": downstream,
        "rules": {
            "one_corpus": "control and treatment differ by the accessor only, both over today's "
                          "e326.corpus()",
            "local_accessor": "the switch is one accessor in the consumer's own file; e329's "
                              "binding and every other reader of it stay on the shipped reading",
            "refusal_is_atomic": "a refused switch restores the source bytes and the archived face",
            "diff_is_three_arms": "drift (corpus), total (reader's cost), switch (the opt-in)",
            "one_hop_is_a_graph_edge": "a study that imports a direct reader is listed one hop "
                                       "further; an import is an edge, not proof that the face is "
                                       "read (E335 imports E334 for its own reasons), so the list is "
                                       "a superset to inspect rather than a count of work",
            "frozen_rule": "decide() is code: a moved verdict outranks a failed re-derivation",
        },
        "limits": {
            "one_consumer": "only E330 moves; the other five E336 priced are untouched",
            "green_window": ("this face re-derives only while scripts/Tools/live/monitor/firm hold "
                             "exactly %s python sources: the population is the corpus, so the next "
                             "landed script moves sources_scanned by one and every census face "
                             "published today must be rebuilt"
                             % ((treatment.get("summary") or {}).get("sources_scanned"),)),
            "rows_not_numbers": ("decision rows are compared structurally (source/line/class/"
                                 "decider/pinned/swap flag), not as numbers"),
            "cascade_is_disclosed_not_repaired": ("the studies in downstream_studies.direct rebuild this "
                                                  "face from its published numbers, and the ones in "
                                                  "one_hop_further reach it through another study's "
                                                  "registry; republishing them is a separate batch "
                                                  "and is counted rather than claimed"),
        },
    }
    target = outdir or OUTDIR
    if not os.path.isdir(target):
        os.makedirs(target)
    with io.open(os.path.join(target, FACE), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    mirror = dict(doc)
    mirror["face"] = FACE
    with io.open(os.path.join(target, LATEST), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(mirror, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    return doc


# --------------------------------------------------------------------------------------- verify

def verify_face(disk, fresh):
    problems = []
    if disk.get("verdict") != fresh.get("verdict"):
        problems.append("the verdict does not re-derive")
    if disk.get("verdict") not in VERDICTS:
        problems.append("verdict %r is outside the frozen set" % (disk.get("verdict"),))
    for key in ("numbers_moved_by_the_opt_in", "numbers_moved_by_corpus_drift",
                "numbers_moved_before_to_republished", "decision_rows_changed_by_the_reading",
                "verdict_before", "verdict_republished", "rows_compared",
                "sources_scanned_republished"):
        if (disk.get("summary") or {}).get(key) != (fresh.get("summary") or {}).get(key):
            problems.append("summary.%s does not re-derive" % key)
    for arm in ("drift_before_to_control", "total_before_to_republished",
                "switch_control_to_republished"):
        a = (disk.get("diff") or {}).get(arm) or {}
        b = (fresh.get("diff") or {}).get(arm) or {}
        if a.get("moved") != b.get("moved"):
            problems.append("diff.%s.moved does not re-derive" % arm)
    disk_rows = [(r.get("key"), r.get("delta")) for r in
                 ((disk.get("diff") or {}).get("switch_control_to_republished") or {}).get("rows") or []]
    fresh_rows = [(r.get("key"), r.get("delta")) for r in
                  ((fresh.get("diff") or {}).get("switch_control_to_republished") or {}).get("rows") or []]
    if disk_rows != fresh_rows:
        problems.append("the switch arm's rows do not re-derive")
    if (disk.get("optin_allowlist") or []) != (fresh.get("optin_allowlist") or []):
        problems.append("the opt-in allowlist does not re-derive")
    if disk.get("downstream_studies") != fresh.get("downstream_studies"):
        problems.append("the downstream study list does not re-derive")
    if disk.get("verdict") == V_ADOPT and not disk.get("optin_allowlist"):
        problems.append("an adopted switch published no allowlist entry")
    if disk.get("verdict") != V_ADOPT and disk.get("optin_allowlist"):
        problems.append("a refused switch published an allowlist entry")
    return problems


def verify(root=None):
    root = root or ROOT
    fresh = build(root=root, outdir=tempfile.mkdtemp(prefix="e337_verify_"))
    disk, why = load_face("results/state_tilt/%s" % FACE, root)
    if disk is None:
        return ["the face does not read: %s" % (why,)]
    problems = verify_face(disk, fresh)
    # A verify run rebuilds every arm; the tree must be left switched iff the verdict says so.
    src = read_text(consumer_path(root))
    switched = MARKER in src
    if switched != (disk.get("verdict") == V_ADOPT):
        problems.append("the source state disagrees with the published verdict")
    return problems


# ------------------------------------------------------------------------------------- selftest

FX_CONSUMER = (
    '"""fixture."""\n'
    'import io\n'
    'import e326_template_parameter_consumers as e326\n'
    'import e329_two_vintage_binding as e329\n'
    '\n'
    'ROOT = e326.ROOT\n'
    'FACE = "X.json"\n'
    '\n'
    'def a(src):\n'
    '    return [t for _n, t in e329._code_lines(src)]\n'
    '\n'
    'def b(src):\n'
    '    lines = e329._code_lines(src)\n'
    '    return lines\n'
    '\n'
    'def c(src):\n'
    '    return e329._code_lines(src)[:3]\n'
    '\n'
    'def d(src):\n'
    '    for _n, t in e329._code_lines(src):\n'
    '        print(t)\n'
)


def cmd_selftest():
    checks = []

    def check(name, ok, detail=""):
        checks.append((name, bool(ok), detail))

    switched, changed = surface(FX_CONSUMER)
    check("L1 the fixture switches and reports the change", changed and MARKER in switched,
          "%s" % changed)
    check("L2 every call site moved to the local accessor and none is left",
          switched.count(NEW_CALL) == CALL_SITES + 1 and OLD_CALL not in switched,
          "calls=%d (call sites %d + the definition)" % (switched.count(NEW_CALL), CALL_SITES))
    check("L3 exactly one accessor landed", switched.count("def _lines(") == 1, "")
    again, changed_again = surface(switched)
    check("L4 the switch is idempotent", again == switched and not changed_again, "")
    try:
        surface(FX_CONSUMER.replace("ROOT = e326.ROOT\n", ""))
        refused = False
    except ValueError:
        refused = True
    check("L5 a source without the anchor is refused, never edited blindly", refused, "")
    try:
        surface(FX_CONSUMER.replace("e329._code_lines(", "e329._lines("))
        refused = False
    except ValueError:
        refused = True
    check("L6 a call-site count that does not match is refused", refused, "")

    before = {"sources_scanned": 100, "decisions": 4, "share": 0.5, "flag": True}
    after = {"sources_scanned": 101, "decisions": 4, "share": 0.5 + 1e-12, "flag": False}
    rows, compared = numeric_diff(before, after)
    check("L7 a moved number is published with both readings and its delta",
          rows == [{"key": "sources_scanned", "before": 100, "after": 101, "delta": 1}], str(rows))
    check("L8 a difference under tolerance and a bool are not measurements",
          compared == 3 and all(r["key"] != "share" and r["key"] != "flag" for r in rows),
          "compared=%d" % compared)

    check("L9 a moved verdict is refused before the verify condition",
          decide(["x"], "v1", "v2")[0] == V_REFUSE_VERDICT, decide(["x"], "v1", "v2")[0])
    check("L10 a failed re-derivation is refused when the verdict holds",
          decide(["x"], "v1", "v1")[0] == V_REFUSE_VERIFY, decide(["x"], "v1", "v1")[0])
    check("L11 a clean run adopts",
          decide([], "v1", "v1")[0] == V_ADOPT, decide([], "v1", "v1")[0])
    check("L12 an unreadable face is blind, not clean",
          decide([], None, "v1")[0] == V_REFUSE_VERIFY, decide([], None, "v1")[0])

    doc = {"a": {"b": 3}, "c": [{"d": 4.5}], "e": "text"}
    check("L13 leaves walk nested dicts and lists, ignoring text",
          leaves(doc) == {"a.b": 3, "c[0].d": 4.5}, str(leaves(doc)))

    sig = row_signature({"rows": [{"source": "s", "line": 1, "class": "c", "decider": "d",
                                   "pinned": True, "swap_changes_today": False}]})
    check("L14 the row signature is the structural half of the face",
          sig == [("s", 1, "c", "d", True, False)], str(sig))

    # L15/L16: the live tree.  The consumer must be in the state its face claims, and that face
    # must re-derive -- a switch that only *says* it re-verifies is exactly what this card refuses.
    src = read_text(consumer_path())
    disk, why = load_face("results/state_tilt/%s" % FACE)
    check("L15 the consumer's accessor state matches the published verdict",
          disk is not None and (MARKER in src) == (disk.get("verdict") == V_ADOPT),
          "face=%s why=%s" % (None if disk is None else disk.get("verdict"), why))
    problems = verify(ROOT) if disk is not None else ["no face"]
    check("L16 the published face re-derives over today's corpus", not problems,
          "; ".join(problems[:4])[:200])

    down = downstream_studies()
    check("L17 the downstream list names at least one study that rebuilds this face",
          len(down["direct"]) >= 1, str(down["direct"][:4]))
    check("L18 an indirect reader is found one hop further, not lost",
          all(rel not in down["direct"] for rel in down["one_hop_further"]),
          str(down["one_hop_further"][:4]))

    for name, ok, detail in checks:
        print("%s %s%s" % ("PASS" if ok else "FAIL", name, "" if ok else " | " + str(detail)))
    failed = [name for name, ok, _d in checks if not ok]
    print("selftest %d/%d" % (len(checks) - len(failed), len(checks)))
    return 0 if not failed else 1


# ------------------------------------------------------------------------------------------ cli

def cmd_run():
    doc = build()
    s = doc["summary"]
    print("%s -> %s" % (STUDY, os.path.join(OUTDIR, FACE)))
    print("verdict: %s" % doc["verdict"])
    print("verdict %s -> %s | re-verify problems %s | reverted %s"
          % (s["verdict_before"], s["verdict_republished"], s["verify_problems"], s["reverted"]))
    print("drift %s | total %s | the opt-in itself %s number(s) over %s compared"
          % (s["numbers_moved_by_corpus_drift"], s["numbers_moved_before_to_republished"],
             s["numbers_moved_by_the_opt_in"], s["numbers_compared_switch"]))
    print("sources %s -> %s | decision rows changed %s | downstream studies %s"
          % (s["sources_scanned_before"], s["sources_scanned_republished"],
             s["decision_rows_changed_by_the_reading"],
             s["downstream_studies_that_rebuild_this_face"]))
    return 0 if doc["verdict"] == V_ADOPT else 1


def cmd_verify():
    problems = verify()
    if problems:
        print("PROBLEMS: " + "; ".join(problems[:8]))
        return 1
    print("verify: 0 problems")
    return 0


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "run":
        return cmd_run()
    if cmd == "verify":
        return cmd_verify()
    if cmd == "selftest":
        return cmd_selftest()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))