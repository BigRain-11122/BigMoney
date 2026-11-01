"""E335 -- land E334's frozen recommendation as a sibling entry point, and prove it is inert.

E334 priced a repair of ``e326.code_lines`` and its frozen rule sent the repair to a *sibling*
entry point: the shipped reading stays bound under an explicit legacy name (E332 and E333 exist to
measure its defect, and a silent repair erases their evidence), the tokenizer reading is exported
under a new name, and no consumer is switched.  This card is the landing, and the landing is only
worth anything if it can be shown that nothing moved:

  (a) COEXIST    -- both readings exist, bound as described, and disagree on named sources over the
                    corpus E334 used (a name that agrees everywhere is an alias, not a second
                    reading).
  (b) RE-DERIVE  -- every source E334 published a delta for is recomputed *through the new name*
                    and compared to the published numbers at 1e-9.  This is the check that the new
                    entry point is the reading E334 priced and not a lookalike.
  (c) INERT      -- no module rebinds the legacy name, and no consumer reads the new one.  Both are
                    source scans, because the failure this card guards against is a future edit,
                    not today's state, and a runtime probe cannot see a future edit.

Decision rule (frozen, see ``decide``): the landing is inert only if all three hold.  Any failure is
named, not summarised -- a rule that reports only its first failing condition reads as if the other
inputs were absent (E334 pit 1).

    python scripts/e335_sibling_entry_point.py run|verify|selftest
"""
import ast
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import e326_template_parameter_consumers as e326  # noqa: E402  (path set above)
import e332_invisible_tail_recovery as e332  # noqa: E402
import e334_helper_repair_blast_radius as e334  # noqa: E402

ROOT = e326.ROOT
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
TODAY = "2026-11-01"
FACE = "SIBLINGENTRY-%s.json" % TODAY
LATEST = "siblingentry_latest.json"
STUDY = "E335_sibling_entry_point"
E334_FACE = e334.FACE
TOL = 1e-9

E326_REL = "scripts/e326_template_parameter_consumers.py"
SELF_REL = "scripts/e335_sibling_entry_point.py"
LEGACY = "code_lines_legacy"
NEW = "code_lines_tokenized"

# A rebind is a NAME being pointed somewhere else; a use is the new name appearing at all.
SETATTR = re.compile(r"setattr\s*\(\s*e326[\w.]*\s*,\s*[\"']code_lines")
USE_NEW = re.compile(r"\bcode_lines_tokenized\b")

V_INERT = "sibling_entry_point_lands_inert_legacy_pinned_new_name_unread_and_e334_delta_reproduces"
V_DIRTY = "sibling_entry_point_is_not_inert_because_a_name_moved_or_a_consumer_switched"
V_LOOKALIKE = "the_new_name_is_not_the_reading_e334_priced_because_the_published_delta_does_not_reproduce"
VERDICTS = (V_INERT, V_DIRTY, V_LOOKALIKE)

MAX_EXAMPLES = 8


def say(message):
    sys.stderr.write(message + "\n")
    sys.stderr.flush()


# ---------------------------------------------------------------------------------- primitives

def corpus_texts(files=None):
    """``rel_path -> source`` over the corpus E334 priced against (one file list, one reading)."""
    out = {}
    for path, src in (files if files is not None else e326.corpus()):
        out.setdefault(e326.relp(path), src)
    return out


def readings(src):
    """Both readings of one source, as ``(shipped, tokenized)`` line lists."""
    return e326.code_lines(src), e326.code_lines_tokenized(src)


def face_events(lines):
    """E334's event count: lines a scanner can see that name a face or load something."""
    return sum(1 for _n, t in lines
               if e332.K_FACE in e332.classify(t) or e332.K_LOAD in e332.classify(t))


def recovered(texts, rel):
    """Blind code lines in one source, exactly as E332 counted them (helper spans, no re-definition)."""
    src = texts.get(rel) or ""
    return sum(span[2] for span in e332.helper_blind_spans(src, [n for n, _t in e326.code_lines(src)]))


def coexist(texts):
    """(a) Both readings bound as the card asks, and the sources where they actually differ."""
    names = {"shipped": hasattr(e326, "code_lines"),
             "legacy": hasattr(e326, LEGACY),
             "new": hasattr(e326, NEW)}
    legacy_is_shipped = getattr(e326, LEGACY, None) is getattr(e326, "code_lines", None)
    new_is_tokenizer = (getattr(e326, NEW, None) is not None
                        and getattr(e326, NEW).__name__ == NEW)
    differing = []
    for rel in sorted(texts):
        shipped, token = readings(texts[rel])
        if [n for n, _t in shipped] != [n for n, _t in token]:
            differing.append({"source": rel,
                              "lines_shipped": len(shipped),
                              "lines_tokenized": len(token),
                              "delta": len(token) - len(shipped)})
    differing.sort(key=lambda r: (-abs(r["delta"]), r["source"]))
    return {"names_present": names,
            "legacy_is_the_shipped_function": legacy_is_shipped,
            "new_name_is_exported": new_is_tokenizer,
            "sources_read": len(texts),
            "sources_where_the_readings_differ": len(differing),
            "named_examples": differing[:MAX_EXAMPLES],
            "differing": differing}


def redelta(texts, published=None):
    """(b) E334's per-source delta recomputed through the NEW name, at 1e-9."""
    doc = published if published is not None else load_json(E334_FACE)
    rows, worst, reproduced = [], 0.0, 0
    for cand in (doc.get("attribution_candidates") or []):
        rel = cand.get("source")
        if rel not in texts:
            rows.append({"source": rel, "status": "source_absent_from_corpus",
                         "published": cand, "recomputed": None, "abs_diff": None})
            continue
        shipped, token = readings(texts[rel])
        got = {"events_with_shipped_helper": face_events(shipped),
               "events_with_repaired_helper": face_events(token),
               "recovered_code_lines": recovered(texts, rel)}
        got["event_delta"] = got["events_with_repaired_helper"] - got["events_with_shipped_helper"]
        diffs = []
        for key in ("events_with_shipped_helper", "events_with_repaired_helper",
                    "event_delta", "recovered_code_lines"):
            want = cand.get(key)
            if isinstance(want, (int, float)) and not isinstance(want, bool):
                diffs.append(abs(float(got[key]) - float(want)))
        worst_row = max(diffs) if diffs else 0.0
        worst = max(worst, worst_row)
        ok = worst_row <= TOL
        reproduced += 1 if ok else 0
        rows.append({"source": rel, "status": "reproduced" if ok else "moved",
                     "published": {k: cand.get(k) for k in got},
                     "recomputed": got, "abs_diff": worst_row})
    return {"tolerance": TOL,
            "candidates_published": len(doc.get("attribution_candidates") or []),
            "candidates_reproduced": reproduced,
            "max_abs_diff": worst,
            "reproduced_via": NEW,
            "rows": rows,
            "e334_verdict": doc.get("verdict")}


def _enclosing_scopes(tree):
    """``id(node) -> the function (or module) that owns the statement``, for restore judgement."""
    owner = {}

    def walk(node, scope):
        owner[id(node)] = scope
        for child in ast.iter_child_nodes(node):
            walk(child, node if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) else scope)

    walk(tree, tree)
    return owner


def _restored_targets(scope):
    """Attribute names this scope restores inside a ``finally`` block."""
    out = set()
    for node in ast.walk(scope):
        if not isinstance(node, ast.Try):
            continue
        for stmt in node.finalbody:
            for sub in ast.walk(stmt):
                if isinstance(sub, ast.Assign) and isinstance(sub.value, ast.Name):
                    for target in sub.targets:
                        if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name):
                            out.add(target.attr)
    return out


def _reading_rebinds(rel, src):
    """Splits assignments to a reading name into scoped patches and permanent rebinds.

    E332, E333 and E334 all patch ``e326.code_lines`` on purpose and restore it in a ``finally``;
    calling those a rebind would fail the landing on the very studies it exists to protect.  A
    *permanent* rebind is one no enclosing scope restores -- that is the shape the card refuses.
    """
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return [], []
    owner = _enclosing_scopes(tree)
    scoped, permanent = [], []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        names = [t.attr for t in node.targets
                 if isinstance(t, ast.Attribute) and t.attr in ("code_lines", LEGACY, NEW)
                 and isinstance(t.value, ast.Name)]
        if not names:
            continue
        scope = owner.get(id(node), tree)
        restored = _restored_targets(scope) | _restored_targets(tree)
        row = {"source": rel, "line": node.lineno, "name": names[0]}
        (scoped if names[0] in restored else permanent).append(row)
    return scoped, permanent


def inertness(texts, allowed=(E326_REL, SELF_REL)):
    """(c) No permanent rebind of a reading name, no consumer of the new one, outside the landing."""
    rebinds, scoped, optins = [], [], []
    for rel in sorted(texts):
        if not rel.endswith(".py") or rel in allowed:
            continue
        hits_scoped, hits_permanent = _reading_rebinds(rel, texts[rel])
        scoped.extend(hits_scoped)
        rebinds.extend(hits_permanent)
        for lineno, line in enumerate((texts[rel] or "").splitlines(), 1):
            text = line.strip()
            if not text or text.startswith("#"):
                continue
            if SETATTR.search(text):
                rebinds.append({"source": rel, "line": lineno, "name": "setattr"})
            if USE_NEW.search(text):
                optins.append({"source": rel, "line": lineno, "text": text[:200]})
    live = getattr(e326, LEGACY) is getattr(e326, "code_lines")
    return {"allowed_files": list(allowed),
            "rebinds": rebinds,
            "scoped_patches_restored_in_a_finally": scoped,
            "consumers_of_the_new_name": optins,
            "the_module_binding_is_still_the_shipped_function": live,
            "clean": not rebinds and not optins and live,
            "method": "AST scan: an assignment no enclosing scope restores in a finally is a "
                      "permanent rebind; the module binding is also checked at runtime, which is "
                      "what a future edit in a module we never import would break"}


def decide(delta_ok, rebinds, optins, coexist_ok):
    """Frozen rule: every failing condition is named, never just the first (E334 pit 1)."""
    failed = []
    if not coexist_ok:
        failed.append("the_two_readings_do_not_coexist_as_described")
    if not delta_ok:
        failed.append("the_published_delta_does_not_reproduce_through_the_new_name")
    if rebinds:
        failed.append("%d_module(s)_rebind_a_reading_name" % len(rebinds))
    if optins:
        failed.append("%d_consumer(s)_read_the_new_name" % len(optins))
    if not failed:
        return V_INERT, "both readings coexist and differ, E334's delta reproduces, nothing moved"
    verdict = V_DIRTY if (rebinds or optins or not coexist_ok) else V_LOOKALIKE
    return verdict, "; ".join(failed)


# ---------------------------------------------------------------------------------- io

def load_json(rel):
    with io.open(os.path.join(OUTDIR, rel), encoding="utf-8") as fh:
        return json.load(fh)


def e326_face_state():
    """What the landing actually changed in e326: the three names and the line each lives on."""
    path = os.path.join(ROOT, E326_REL)
    with io.open(path, encoding="utf-8") as fh:
        src = fh.read()
    tree = ast.parse(src)
    rows = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in ("code_lines", NEW):
            rows.append({"name": node.name, "line": node.lineno, "kind": "function"})
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == LEGACY:
                    rows.append({"name": LEGACY, "line": node.lineno, "kind": "alias"})
    return {"source": E326_REL, "bindings": rows}


def build(outdir=None):
    texts = corpus_texts()
    coex = coexist(texts)
    delta = redelta(texts)
    inert = inertness(texts)
    coexist_ok = (all(coex["names_present"].values())
                  and coex["legacy_is_the_shipped_function"]
                  and coex["new_name_is_exported"]
                  and coex["sources_where_the_readings_differ"] > 0)
    delta_ok = (delta["candidates_published"] > 0
                and delta["candidates_reproduced"] == delta["candidates_published"]
                and delta["max_abs_diff"] <= TOL)
    verdict, reason = decide(delta_ok, inert["rebinds"], inert["consumers_of_the_new_name"],
                             coexist_ok)
    doc = {
        "study": STUDY,
        "evidence_cutoff": TODAY,
        "verdict": verdict,
        "verdict_reason": reason,
        "recommendation": "the tokenizer reading is available as a sibling entry point; switching a "
                          "consumer is a separate decision with its own republish cost (E334)",
        "summary": {
            "reading_names_added": 2,
            "consumers_switched": 0,
            "sources_read": coex["sources_read"],
            "sources_where_the_readings_differ": coex["sources_where_the_readings_differ"],
            "e334_delta_candidates_published": delta["candidates_published"],
            "e334_delta_candidates_reproduced": delta["candidates_reproduced"],
            "max_abs_diff_vs_published": delta["max_abs_diff"],
            "modules_that_rebind_a_reading_name": len(inert["rebinds"]),
            "studies_that_patch_and_restore_in_a_finally": len(inert["scoped_patches_restored_in_a_finally"]),
            "consumers_of_the_new_name": len(inert["consumers_of_the_new_name"]),
        },
        "decision": {"rule": {"inert_if": "all three axes hold",
                              "otherwise": "name every failing condition and do not claim a landing"},
                     "inputs": {"coexist_ok": coexist_ok, "delta_ok": delta_ok,
                                "rebinds": len(inert["rebinds"]),
                                "consumers_of_the_new_name": len(inert["consumers_of_the_new_name"])},
                     "verdict_options": list(VERDICTS)},
        "coexistence": {k: v for k, v in coex.items() if k != "differing"},
        "differing_sources": coex["differing"][:MAX_EXAMPLES],
        "differing_sources_total": coex["sources_where_the_readings_differ"],
        "differing_sources_truncated":
            max(0, coex["sources_where_the_readings_differ"] - MAX_EXAMPLES),
        "rederived_delta": {k: v for k, v in delta.items() if k != "rows"},
        "rederived_rows": delta["rows"],
        "inertness": inert,
        "e326_bindings": e326_face_state(),
        "rules": {
            "one_corpus": "every number is computed over e326.corpus(), the file list E334 priced, "
                          "so a delta here is the helper and nothing else",
            "pinned_not_copied": "code_lines_legacy is an alias, not a copy: a copy would freeze "
                                 "silently against the shipped function",
            "new_name_is_the_repaired_half": "code_lines_tokenized delegates to e332.true_lines, the "
                                             "very reading E332 counts as the repaired half, so the "
                                             "two cannot drift",
            "inertness_is_a_source_scan": "the failure mode is a future edit; a runtime probe cannot "
                                          "see one",
            "frozen_rule": "decide() is code, not prose, and names every failing condition",
        },
        "limits": {
            "no_consumer_switched": "E334 priced the switch as a separate, larger decision (6 faces / "
                                    "37 numbers); this card lands the shape only",
            "corpus_is_a_snapshot": "the coexist delta is a fact about this tree; the ration and "
                                    "re-derivation are recomputed each run",
            "self_exclusion": "the landing's own script and e326 are the only files allowed to name "
                              "the new reading",
        },
    }
    target = outdir or OUTDIR
    if not os.path.isdir(target):
        os.makedirs(target)
    path = os.path.join(target, FACE)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    latest = os.path.join(target, LATEST)
    mirror = dict(doc)
    mirror["face"] = FACE
    with io.open(latest, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(mirror, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    return doc


# ---------------------------------------------------------------------------------- commands

def cmd_run():
    doc = build()
    s = doc["summary"]
    print("%s -> %s" % (STUDY, os.path.join(OUTDIR, FACE)))
    print("verdict: %s" % doc["verdict"])
    print("readings differ on %d of %d sources | E334 delta reproduced %d/%d (max abs diff %.3g)"
          % (s["sources_where_the_readings_differ"], s["sources_read"],
             s["e334_delta_candidates_reproduced"], s["e334_delta_candidates_published"],
             s["max_abs_diff_vs_published"]))
    print("rebinds %d | consumers of the new name %d"
          % (s["modules_that_rebind_a_reading_name"], s["consumers_of_the_new_name"]))
    return 0 if doc["verdict"] == V_INERT else 1


def cmd_verify():
    problems = []
    on_disk = load_json(FACE)
    fresh = build()
    for key in ("verdict", "summary", "differing_sources", "differing_sources_total",
                "differing_sources_truncated", "rederived_delta", "inertness",
                "e326_bindings", "coexistence"):
        if on_disk.get(key) != fresh.get(key):
            problems.append(key)
    if on_disk.get("study") != STUDY:
        problems.append("study")
    print("verify problems=%s" % (problems,))
    return 0 if not problems else 1


# ---------------------------------------------------------------------------------- selftest

def _fixture():
    return ('"""Docstring with a closed delimiter on its own line."""\n'
            "import os\n"
            'TEXT = ("""\n'
            "first\n"
            'last""".split())\n'
            "def f():\n"
            "    return TEXT\n")


def cmd_selftest():
    checks = []

    def leg(name, fn):
        try:
            fn()
            checks.append((name, True, ""))
        except AssertionError as exc:
            checks.append((name, False, str(exc)))

    def l1_both_readings_exist():
        assert callable(e326.code_lines) and callable(getattr(e326, NEW))
        assert getattr(e326, LEGACY) is e326.code_lines

    def l2_new_name_is_the_tokenizer_reading():
        src = _fixture()
        assert e326.code_lines_tokenized(src) == e332.true_lines(src)

    def l3_readings_differ_on_the_fixture():
        src = _fixture()
        shipped = [t for _n, t in e326.code_lines(src)]
        token = [t for _n, t in e326.code_lines_tokenized(src)]
        assert shipped != token, (shipped, token)

    def l4_shipped_reading_unchanged_by_the_landing():
        src = "import os\nx = 1\ny = x + 1\n"
        assert e326.code_lines(src) == [(1, "import os"), (2, "x = 1"), (3, "y = x + 1")]
        assert getattr(e326, LEGACY)(src) == e326.code_lines(src)

    def l5_tokenized_is_ordered_pairs():
        out = e326.code_lines_tokenized(_fixture())
        assert all(isinstance(r, tuple) and len(r) == 2 for r in out)
        assert [n for n, _t in out] == sorted(n for n, _t in out)
        assert all(t and t == t.strip() for _n, t in out)

    def l6_coexist_requires_a_real_difference():
        texts = {"a.py": _fixture()}
        ok = coexist(texts)
        assert ok["sources_where_the_readings_differ"] == 1, ok["sources_where_the_readings_differ"]
        same = coexist({"b.py": "x = 1\n"})
        assert same["sources_where_the_readings_differ"] == 0

    def l7_redelta_reproduces_a_truthful_row():
        texts = {"a.py": _fixture()}
        shipped, token = readings(texts["a.py"])
        row = {"source": "a.py",
               "events_with_shipped_helper": face_events(shipped),
               "events_with_repaired_helper": face_events(token),
               "event_delta": face_events(token) - face_events(shipped),
               "recovered_code_lines": recovered(texts, "a.py")}
        got = redelta(texts, {"attribution_candidates": [row]})
        assert got["candidates_reproduced"] == 1, got
        assert got["max_abs_diff"] <= TOL

    def l8_redelta_catches_a_moved_number():
        texts = {"a.py": _fixture()}
        row = {"source": "a.py", "events_with_shipped_helper": 99,
               "events_with_repaired_helper": 0, "event_delta": -99,
               "recovered_code_lines": 0}
        got = redelta(texts, {"attribution_candidates": [row]})
        assert got["candidates_reproduced"] == 0
        assert got["max_abs_diff"] > TOL

    def l9_redelta_names_a_missing_source():
        got = redelta({}, {"attribution_candidates": [{"source": "gone.py"}]})
        assert got["rows"][0]["status"] == "source_absent_from_corpus"
        assert got["candidates_reproduced"] == 0

    def l10_inertness_catches_a_rebind():
        texts = {"scripts/x.py": "import e326_template_parameter_consumers as e326\n"
                                 "e326.code_lines = other\n"}
        got = inertness(texts)
        assert len(got["rebinds"]) == 1, got
        assert not got["clean"]

    def l11_inertness_catches_setattr():
        got = inertness({"scripts/y.py": "setattr(e326, 'code_lines', f)\n"})
        assert len(got["rebinds"]) == 1, got

    def l12_inertness_catches_a_silent_consumer():
        got = inertness({"scripts/z.py": "from e326_template_parameter_consumers import "
                                         "code_lines_tokenized\n"})
        assert len(got["consumers_of_the_new_name"]) == 1, got

    def l13_inertness_allows_the_landing_itself():
        got = inertness({E326_REL: "code_lines_tokenized = 1\n",
                         SELF_REL: "code_lines_tokenized()\n"})
        assert got["clean"], got

    def l14_ignores_comments_and_strings_by_line():
        got = inertness({"scripts/w.py": "# code_lines_tokenized is mentioned here\n"})
        assert got["clean"], got

    def l15_decide_names_every_failing_condition():
        verdict, reason = decide(False, [{"a": 1}], [{"b": 2}], False)
        assert verdict == V_DIRTY
        for fragment in ("coexist", "reproduce", "rebind", "read_the_new_name"):
            assert fragment in reason, reason

    def l16_decide_is_frozen_on_the_good_path():
        verdict, reason = decide(True, [], [], True)
        assert verdict == V_INERT and reason

    def l17_decide_separates_a_lookalike():
        verdict, _reason = decide(False, [], [], True)
        assert verdict == V_LOOKALIKE

    def l18_bindings_read_from_the_module_source():
        got = e326_face_state()
        names = {row["name"] for row in got["bindings"]}
        assert names == {"code_lines", NEW, LEGACY}, names

    def l19_a_scoped_patch_is_not_a_rebind():
        src = ("import e326_template_parameter_consumers as e326\n"
               "SHIPPED = e326.code_lines\n"
               "def read(f):\n"
               "    e326.code_lines = f\n"
               "    try:\n"
               "        return 1\n"
               "    finally:\n"
               "        e326.code_lines = SHIPPED\n")
        got = inertness({"scripts/p.py": src})
        assert got["clean"], got
        assert 4 in [row["line"] for row in got["scoped_patches_restored_in_a_finally"]], got

    def l20_an_unrestored_patch_is_a_rebind():
        src = ("import e326_template_parameter_consumers as e326\n"
               "SHIPPED = e326.code_lines\n"
               "e326.code_lines = lambda s: []\n")
        got = inertness({"scripts/q.py": src})
        assert len(got["rebinds"]) == 1, got
        assert not got["clean"]

    for name, fn in (
        ("L1 both readings exist and the legacy name is the shipped function", l1_both_readings_exist),
        ("L2 the new name is the tokenizer reading", l2_new_name_is_the_tokenizer_reading),
        ("L3 the two readings differ on a fixture", l3_readings_differ_on_the_fixture),
        ("L4 the shipped reading is unchanged by the landing", l4_shipped_reading_unchanged_by_the_landing),
        ("L5 the tokenized reading is ordered stripped pairs", l5_tokenized_is_ordered_pairs),
        ("L6 coexist needs a real difference", l6_coexist_requires_a_real_difference),
        ("L7 re-derivation reproduces a truthful row", l7_redelta_reproduces_a_truthful_row),
        ("L8 re-derivation catches a moved number", l8_redelta_catches_a_moved_number),
        ("L9 re-derivation names a missing source", l9_redelta_names_a_missing_source),
        ("L10 a rebind is caught", l10_inertness_catches_a_rebind),
        ("L11 setattr() rebind is caught", l11_inertness_catches_setattr),
        ("L12 a silent consumer is caught", l12_inertness_catches_a_silent_consumer),
        ("L13 the landing itself may name the reading", l13_inertness_allows_the_landing_itself),
        ("L14 comment mentions are not consumers", l14_ignores_comments_and_strings_by_line),
        ("L15 decide() names every failing condition", l15_decide_names_every_failing_condition),
        ("L16 decide() is frozen on the good path", l16_decide_is_frozen_on_the_good_path),
        ("L17 decide() separates a lookalike", l17_decide_separates_a_lookalike),
        ("L18 bindings come from the module source", l18_bindings_read_from_the_module_source),
        ("L19 a finally-restored patch is not a rebind", l19_a_scoped_patch_is_not_a_rebind),
        ("L20 an unrestored patch is a rebind", l20_an_unrestored_patch_is_a_rebind),
    ):
        leg(name, fn)
    passed = sum(1 for _n, ok, _w in checks if ok)
    for name, ok, why in checks:
        print("%s %s%s" % ("PASS" if ok else "FAIL", name, "" if ok else " -- " + why))
    print("%s selftest %d/%d" % (STUDY, passed, len(checks)))
    return 0 if passed == len(checks) else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "run":
        return cmd_run()
    if cmd == "verify":
        return cmd_verify()
    if cmd == "selftest":
        return cmd_selftest()
    say("usage: e335_sibling_entry_point.py run|verify|selftest")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))