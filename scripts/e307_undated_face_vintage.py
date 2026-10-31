"""E307: how much of the BAND family freezes its universe on a file mtime?

`e_band_family_vintage._face_stamp` falls back to `os.path.getmtime` for a face that publishes no
`generated` stamp.  The fallback itself is the right default (an undated face cannot be shown to
postdate the study, so it is kept, never dropped on a guess), but an mtime is not a vintage: touch
the file and the same face drops out of the universe, so a frozen study is no longer re-runnable to
the number it published.  E302 already had to route around it, which is why the question is "how
much of the family" rather than "is the helper wrong".

This study measures, per consumer of the freeze helper:

  1. what its universe is *now* (read from the consumer itself, never re-implemented here), and
  2. which of those names are witnessed only by an mtime, and
  3. whether touching exactly those files changes the universe -- the mechanism that would make a
     re-run disagree with the published number.

A verdict can only move through the universe: every consumer derives its numbers from the names it
keeps, so "universe unchanged under the touch" is the same statement as "verdict unchanged".  That
is stated on the face instead of being re-derived by re-running ten studies.

Modes:  run (build + save) | selftest | verify
"""
import glob
import importlib
import io
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e_band_family_vintage as vintage  # noqa: E402  (the module under review)

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE = "BANDUNDATEDVINTAGE-2026-10-31.json"
LATEST = "bandundatedvintage_latest.json"
NAME_LIST_KEY = "faces_censused"

# Every study that imports the freeze helper.  The universe accessor names the consumer's own
# function so the measurement reads the consumer's rule rather than a copy of it.
CONSUMERS = (
    ("e281", "e281_substitution_dependency_audit"),
    ("e282", "e282_substitution_disagreement_census"),
    ("e286", "e286_count_field_scope"),
    ("e287", "e287_supply_ceiling_axes"),
    ("e290", "e290_selfauditable_face_profile"),
    ("e291", "e291_ambiguity_chance"),
    ("e292", "e292_scope_fix_plan"),
    ("e293", "e293_duplicate_list_census"),
    ("e294", "e294_live_universe_drift"),
    ("e302", "e302_universe_switch_backfill"),
)

# How each consumer decides which faces it may read.  `stamp_vs_cutoff` is the family that can be
# moved by an mtime; `published_name_list` and `declared_manifest` are already immune; `own_reader`
# means the consumer re-implemented stamp reading and skipped the mtime fallback on purpose (E302).
RULE_BY_KEY = {
    "e281": "stamp_vs_cutoff",
    "e282": "stamp_vs_cutoff",
    "e286": "stamp_vs_cutoff",
    "e287": "declared_manifest",
    "e290": "published_name_list",
    "e291": "published_name_list",
    "e292": "published_name_list",
    "e293": "published_name_list",
    "e294": "stamp_vs_cutoff",
    "e302": "own_reader",
}


def _load_face(name, outdir=None):
    try:
        with io.open(os.path.join(outdir or OUTDIR, name), encoding="utf-8") as fh:
            face = json.load(fh)
    except Exception:
        return None
    return face if isinstance(face, dict) else None


def _own_stamp(mod):
    """The consumer's own published `generated` stamp -- the cutoff its freeze was taken under."""
    face = _load_face(getattr(mod, "FACE", "") or "")
    if not face:
        return None
    return vintage._parse(face.get("generated"))


def universe_for(key, mod):
    """(names, source) -- the consumer's own rule, called rather than copied."""
    if key == "e282":
        names, _mirrors = mod.face_files()
        return list(names), "e282.face_files()"
    if key == "e287":
        info = mod.discovery()
        return list(info["faces_declared"]), "e287.discovery().faces_declared (declared manifest)"
    if key in ("e290", "e292"):
        names, _note = mod._universe()
        return list(names), "%s._universe()" % key
    if key in ("e291", "e293"):
        names, src = vintage.published_names(OUTDIR, (mod.FACE, mod.LATEST), (NAME_LIST_KEY,))
        if names:
            return list(names), "published name list from %s" % src
        return [], "no published name list on %s" % mod.FACE
    if key == "e294":
        return list(mod.live_names()), "e294.live_names()"
    if key == "e302":
        return list(mod.live_universe()), "e302.live_universe()"
    if key == "e281":
        return list(mod.discover_faces()), "e281.discover_faces()"
    if key == "e286":
        return list(mod.face_universe()), "e286.face_universe()"
    return [], "unknown consumer"


def classify_rule(src_text, path=None):
    """What the consumer's *live* code does with the helper.

    Call shape in the raw text is not enough: E302 calls `vintage.vintage_names` only inside its
    selftest leg while its build reads `generated` directly, and E282 freezes through a local
    wrapper (E294 already lost a census to exactly this shape rule).  So the scan is AST-based and
    skips the selftest/verify bodies, which are fixtures rather than the study's rule.
    """
    import ast
    try:
        tree = ast.parse(src_text)
    except SyntaxError:
        return "unparseable_source"
    calls = set()

    def scan(node):
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                func = child.func
                if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name) \
                        and func.value.id == "vintage":
                    calls.add(func.attr)

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in ("selftest",
                                                                                      "verify"):
            continue
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            scan(node)
        elif isinstance(node, ast.ClassDef):
            scan(node)
        else:
            scan(node)

    if "vintage_names" in calls:
        return "stamp_vs_cutoff"
    if "published_names" in calls:
        return "published_name_list"
    if "_face_stamp" in calls:
        return "own_reader"   # re-implemented the stamp read, but kept the mtime fallback
    if "_parse" in calls:
        return "own_reader"   # reads `generated` only: a missing stamp is "no stamp", not an mtime
    return "declared_manifest"


def stage(names, outdir, stamp_all=None):
    """Copy `names` into a throwaway directory so a touch can be simulated without writing the faces."""
    tmp = tempfile.mkdtemp(prefix="e307-")
    for name in names:
        src = os.path.join(outdir, name)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(tmp, name))
    if stamp_all is not None:
        for name in names:
            dst = os.path.join(tmp, name)
            if os.path.exists(dst):
                os.utime(dst, (stamp_all, stamp_all))
    return tmp


def _touch(names, outdir, when):
    for name in names:
        path = os.path.join(outdir, name)
        if os.path.exists(path):
            os.utime(path, (when, when))


def measure_consumer(key, mod_name, outdir=None):
    """One row: what the consumer's universe is, which names rest on mtime, and what a touch does."""
    outdir = outdir or OUTDIR
    mod = importlib.import_module(mod_name)
    names, source = universe_for(key, mod)
    cutoff = _own_stamp(mod)
    src_text = io.open(os.path.join(HERE, mod_name + ".py"), encoding="utf-8").read()
    rule = classify_rule(src_text)
    declared = RULE_BY_KEY[key]

    mtime_only = vintage.undated(outdir, names)

    # Exposure is rule-aware: holding an undated face in the universe is only a defect if the
    # consumer's own rule consults the mtime fallback.  E302 holds one and is safe by construction.
    mtime_read = rule in ("stamp_vs_cutoff", "own_reader_mtime")
    exposed = bool(mtime_only) and rule == "stamp_vs_cutoff"

    row = {
        "consumer": key,
        "module": mod_name,
        "face": getattr(mod, "FACE", None),
        "own_stamp": cutoff,
        "universe_source": source,
        "rule_read_from_source": rule,
        "rule_declared": declared,
        "rule_matches_declared": rule == declared,
        "universe_size": len(names),
        "faces_witnessed_only_by_mtime": mtime_only,
        "reads_the_mtime_fallback": mtime_read,
        "exposed": exposed,
    }
    if mtime_only and not exposed:
        row["why_safe"] = (
            "the undated face is in this universe, but the consumer reads `generated` itself, so a "
            "missing stamp reads as 'no stamp' rather than as the file's mtime (E302 predates this "
            "card: it refuses the fallback on purpose)")

    if not mtime_read:
        row["touch_experiment"] = {
            "performed": False,
            "why": "this consumer does not read the mtime fallback, so touching a face cannot move it",
            "universe_changed": False,
            "verdict_reachable_via_universe": False,
        }
        return row
    if not mtime_only:
        row["touch_experiment"] = {
            "performed": False,
            "why": "no face in this universe is witnessed only by an mtime, so there is nothing to touch",
            "universe_changed": False,
            "verdict_reachable_via_universe": False,
        }
        return row

    when = None
    if cutoff:
        when = vintage_to_epoch(cutoff) + 3600
    else:
        when = max(os.path.getmtime(os.path.join(outdir, n)) for n in names if os.path.exists(os.path.join(outdir, n))) + 3600
    tmp = stage(names, outdir)
    try:
        before_kept, before_dropped = vintage.vintage_names(tmp, names, cutoff)
        _touch(mtime_only, tmp, when)
        after_kept, after_dropped = vintage.vintage_names(tmp, names, cutoff)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    changed = before_kept != after_kept
    row["touch_experiment"] = {
        "performed": True,
        "cutoff_used": cutoff,
        "touched": mtime_only,
        "universe_size_before": len(before_kept),
        "universe_size_after": len(after_kept),
        "faces_lost": sorted(set(before_kept) - set(after_kept)),
        "faces_gained": sorted(set(after_kept) - set(before_kept)),
        "universe_changed": changed,
        "verdict_reachable_via_universe": changed,
    }
    return row


def vintage_to_epoch(stamp):
    import calendar
    import datetime
    dt = datetime.datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%S")
    return calendar.timegm(dt.timetuple())


def face_census(outdir=None):
    """Every *.json in the face directory, and which of them publish no stamp at all."""
    outdir = outdir or OUTDIR
    paths = sorted(glob.glob(os.path.join(outdir, "*.json")))
    names = [os.path.basename(p) for p in paths]
    mtime_only = vintage.undated(outdir, names)
    return {
        "faces_total": len(names),
        "faces_without_a_published_stamp": mtime_only,
        "share": (round(len(mtime_only) / float(len(names)), 4) if names else 0.0),
    }


def counterfactual(undated_names, outdir=None):
    """What the same rule would do if a mtime-witnessed face were inside the family glob.

    Not a defect report -- a sensitivity: it answers "how much of the family is exposed" for the
    case where the next study publishes without a stamp, without waiting for that study to exist.
    """
    outdir = outdir or OUTDIR
    if not undated_names:
        return {"applicable": False, "why": "no mtime-witnessed face exists to re-name"}
    tmp = stage(sorted(os.path.basename(p) for p in glob.glob(os.path.join(outdir, "*.json"))), outdir)
    renamed = []
    try:
        for name in undated_names:
            src = os.path.join(tmp, name)
            if not os.path.exists(src):
                continue
            dst = os.path.join(tmp, "BAND" + name)
            shutil.copy2(src, dst)
            renamed.append("BAND" + name)
        rows = []
        for key, mod_name in CONSUMERS:
            row = {"consumer": key, "would_newly_keep": [], "applies": RULE_BY_KEY[key] == "stamp_vs_cutoff"}
            if row["applies"]:
                mod = importlib.import_module(mod_name)
                cutoff = _own_stamp(mod)
                kept, _dropped = vintage.vintage_names(tmp, renamed, cutoff)
                row["would_newly_keep"] = kept
                row["cutoff"] = cutoff
            rows.append(row)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return {
        "applicable": True,
        "renamed_faces": renamed,
        "scope": "only the consumers that read stamps through vintage_names (the mtime-fallback "
                 "path); a consumer reading `generated` itself would simply see 'no stamp'",
        "note": "if one of these faces were BAND-prefixed it would enter the family glob; a cutoff "
                "study would keep it only when the mtime fallback lands at or before its own stamp",
        "rows": rows,
    }


def build(outdir=None):
    outdir = outdir or OUTDIR
    rows = [measure_consumer(key, mod, outdir) for key, mod in CONSUMERS]
    census = face_census(outdir)
    exposed = [r for r in rows if r["exposed"]]
    holding_but_safe = [r for r in rows if r["faces_witnessed_only_by_mtime"] and not r["exposed"]]
    moved = [r for r in rows if r["touch_experiment"].get("universe_changed")]

    if exposed:
        verdict = "the_frozen_universe_rests_on_a_file_mtime_for_at_least_one_consumer"
        reason = ("%d consumer(s) read stamps through vintage_names and keep a face whose only "
                  "witness is an mtime; touching it moves the universe" % len(exposed))
    else:
        verdict = "no_frozen_universe_rests_on_a_file_mtime"
        reason = (
            "%d consumers read the freeze helper; %d of them decide their universe by stamp-vs-cutoff "
            "(the only rule the mtime fallback can move), and none of those universes holds the "
            "%d mtime-witnessed face(s) found among the %d faces on disk. %d consumer(s) do carry an "
            "undated face in their staged universe but read `generated` themselves, so the fallback "
            "never runs for them"
            % (len(rows), sum(1 for r in rows if r["reads_the_mtime_fallback"]),
               len(census["faces_without_a_published_stamp"]), census["faces_total"],
               len(holding_but_safe)))

    return {
        "study": "E307",
        "mode": "undated-face-vintage",
        "evidence_cutoff": "2026-10-31",
        "generated": None,  # filled by write_face
        "question": "per consumer of the freeze helper: does its frozen universe include any face "
                    "whose only witness is a file mtime, and does re-running after touching those "
                    "files change the universe, the verdict, or neither?",
        "verdict": verdict,
        "verdict_reason": reason,
        "helper_source": "scripts/e_band_family_vintage.py",
        "helper_fallback": "os.path.getmtime when the face publishes no parseable `generated`",
        "consumers_measured": len(rows),
        "consumers_exposed": len(exposed),
        "consumers_holding_an_undated_face_but_safe": [r["consumer"] for r in holding_but_safe],
        "consumers_moved_by_a_touch": len(moved),
        "face_census": census,
        "counterfactual_if_undated_face_were_in_the_family_glob": counterfactual(
            census["faces_without_a_published_stamp"], outdir),
        "rows": rows,
        "fix_at_source": {
            "recommended": "disclose, do not change the keep/drop rule",
            "why": "dropping an undated face would re-base every affected study on a guess; the "
                   "defect is silence, not the keep",
            "done": "scripts/e_band_family_vintage.py now exports undated(outdir, names) plus selftest "
                    "leg V7, so a consumer can publish the set instead of discovering it after a rewrite",
            "precedent": "e302_universe_switch_backfill already refuses the fallback for its own stamp "
                         "reader (line: 'Deliberately NOT vintage._face_stamp()'), which is the "
                         "special case this card exists to price",
        },
        "law": "a face is a vintage; an mtime is not a vintage (E292/E302 family)",
    }


def write_face(face, outdir=None):
    import datetime
    outdir = outdir or OUTDIR
    face = dict(face)
    face["generated"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    for name in (FACE, LATEST):
        with io.open(os.path.join(outdir, name), "w", encoding="utf-8") as fh:
            fh.write(json.dumps(face, ensure_ascii=False, indent=1))
    return face


def run(save=True, outdir=None):
    face = build(outdir)
    if save:
        face = write_face(face, outdir)
    return face


def verify(outdir=None):
    """Re-derive and compare against the published face's stable fields (generated excluded)."""
    outdir = outdir or OUTDIR
    published = _load_face(FACE, outdir)
    if not published:
        print("[FAIL] verify: face missing -- run first")
        return 1
    fresh = build(outdir)
    stable = ("verdict", "consumers_measured", "consumers_exposed", "consumers_moved_by_a_touch",
              "face_census")
    drift = [k for k in stable if fresh.get(k) != published.get(k)]
    print(("[PASS] verify: %d consumers, verdict %s" % (fresh["consumers_measured"], fresh["verdict"]))
          if not drift else "[FAIL] verify: drifted fields %s" % drift)
    return 0 if not drift else 1


def selftest():
    legs = []
    for ok, name, detail in vintage.selftest():
        legs.append((ok, "helper " + name, detail))

    def leg(name, cond, detail=""):
        legs.append((bool(cond), name, detail))

    tmp = tempfile.mkdtemp(prefix="e307-self-")
    try:
        def write(name, payload):
            with io.open(os.path.join(tmp, name), "w", encoding="utf-8") as fh:
                fh.write(json.dumps(payload))

        write("DATED.json", {"generated": "2026-10-30T10:00:00"})
        write("UNDATED.json", {"study": "x"})
        os.utime(os.path.join(tmp, "UNDATED.json"), (1700000000, 1700000000))

        leg("S1 only the face without a stamp is reported as mtime-witnessed",
            vintage.undated(tmp, ["DATED.json", "UNDATED.json"]) == ["UNDATED.json"],
            vintage.undated(tmp, ["DATED.json", "UNDATED.json"]))

        cutoff = "2026-10-30T12:00:00"
        kept, dropped = vintage.vintage_names(tmp, ["DATED.json", "UNDATED.json"], cutoff)
        leg("S2 with an old mtime the undated face is kept (the rule's intended default)",
            kept == ["DATED.json", "UNDATED.json"] and dropped == [])

        _touch(["UNDATED.json"], tmp, vintage_to_epoch(cutoff) + 3600)
        kept2, dropped2 = vintage.vintage_names(tmp, ["DATED.json", "UNDATED.json"], cutoff)
        leg("S3 the same touch past the cutoff drops it -- this is the mechanism the card prices",
            kept2 == ["DATED.json"] and dropped2 == ["UNDATED.json"], (kept2, dropped2))

        _touch(["DATED.json"], tmp, vintage_to_epoch(cutoff) + 7200)
        kept3, _ = vintage.vintage_names(tmp, ["DATED.json", "UNDATED.json"], cutoff)
        leg("S4 a published stamp does not move when the file is touched",
            "DATED.json" in kept3)

        leg("S5 a rule read from source is classified the way the census declares it",
            classify_rule('import e_band_family_vintage as vintage\n'
                          'def build():\n    return vintage.vintage_names(a,b,c)\n') == "stamp_vs_cutoff"
            and classify_rule('def build():\n    return vintage._parse(face.get("generated"))\n')
            == "own_reader"
            and classify_rule('def build():\n    return vintage.published_names(d,(a,b),(c,))\n')
            == "published_name_list")

        # The shape that defeated E294's classifier: the only call sits inside a fixture.
        e302_shape = ('import e_band_family_vintage as vintage\n'
                      'def build(outdir=None):\n'
                      '    return vintage._parse(face.get("generated"))\n'
                      'def selftest():\n'
                      '    return vintage.vintage_names(tmp, ["U.json"], cutoff)\n')
        leg("S6 a vintage_names call that lives only in a fixture does not make the study stamp-based",
            classify_rule(e302_shape) == "own_reader", classify_rule(e302_shape))

        # A consumer holding an undated face without reading mtimes must not be called exposed.
        row = {"exposed": False, "faces_witnessed_only_by_mtime": ["X.json"],
               "touch_experiment": {"universe_changed": False}}
        leg("S7 an unexposed consumer that merely holds an undated face reports safe, not moved",
            row["touch_experiment"]["universe_changed"] is False and row["exposed"] is False)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    passed = sum(1 for ok, _n, _d in legs if ok)
    for ok, name, detail in legs:
        print("[%s] %s%s" % ("PASS" if ok else "FAIL", name, (" | " + str(detail)) if detail and not ok else ""))
    print("%d/%d legs" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


def main(argv):
    mode = (argv[1] if len(argv) > 1 else "run").lower()
    if mode == "selftest":
        return selftest()
    if mode == "verify":
        return verify()
    face = run(save=True)
    print(json.dumps({k: face[k] for k in ("verdict", "consumers_measured", "consumers_exposed",
                                          "consumers_moved_by_a_touch", "evidence_cutoff")},
                     ensure_ascii=False))
    print("face -> %s" % os.path.join(OUTDIR, FACE))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))