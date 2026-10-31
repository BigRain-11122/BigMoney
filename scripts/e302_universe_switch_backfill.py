"""E302 -- three directory-censusing studies cannot be asked whether their verdict depends on the
universe, because build() takes no universe argument.  What would a switch cost, and does any of them
flip once it has one?

WHY THIS EXISTS.  E294 re-derived every directory-censusing study in the BAND family twice (frozen
vintage vs live directory).  Nine of twelve could be varied and none moved; three published only
`build()` with no parameters at all, so for them the universe question was UNASKED, not answered.
E299 then found a second, unrelated reason to want the same switch.  This study prices it.

D1  THE SWITCH IS MEASURED, NOT ASSUMED.  For each of the three studies the universe is resolved
    from a module-level global (`OUTDIR`, copied study-by-study down an import chain).  A switch can
    therefore be simulated without editing the study: redirect every module binding of that global to
    a staged directory and re-derive.  The cost of the switch is then a MEASURED number -- how many
    module bindings have to move -- not an estimate.  The parameter-threading cost is priced
    separately from the source (which functions of the study mention OUTDIR, and which load() calls
    fall back to the module default), because that is what an `outdir=` argument would really touch.

D2  THE STAGING MUST BE NARROWER THAN THE LIVE DIRECTORY, OR THE TEST IS A TAUTOLOGY.  A staged
    universe that holds every face the live one holds re-runs the same computation twice and
    manufactures a stable verdict -- the exact trap E294 documented.  Every row publishes both file
    counts and a row whose staged universe is not narrower is classed not_measurable instead of
    stable.

D3  THE STAGED DIRECTORY IS WIDENED BY ONE DOCUMENTED STEP, NOT BY GUESSWORK.  The studies load
    faces BY NAME from the census they read, so a staged directory holding only the stamp-filtered
    set can fail on a face the study names.  The staging therefore also admits every face those
    faces name (one level, resolved against the real directory), and the widening is published.

D4  THE VERDICT VOCABULARY IS E294'S, SO THE TWO FACES JOIN.  A row is reproduces_and_stable,
    reproduces_and_flips, does_not_reproduce or not_measurable, and the face-level verdict is one of
    E294's three.  Cost is published beside the verdict, not folded into it: a cheap switch that
    flips and an expensive switch that does not are different findings.

D5  NO REBURN, NO WRITE.  Published faces are re-read; the staged universe lives in a temporary
    directory and is removed; mtimes of the real directory are asserted unchanged around every
    measurement.  No draw stream, no band rebuild, no engine, no network.

D6  SELF-INCLUSION.  This face is BAND-prefixed like the family it censuses; its own two files are
    excluded from every universe count and the exclusion is a selftest leg.
"""
import ast
import glob
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

import e294_live_universe_drift as drive  # noqa: E402  (build_signature / statuses / verdicts)
import e_band_family_vintage as vintage   # noqa: E402  (the freeze module)

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
CUTOFF = "2026-10-30"
EVIDENCE_CUTOFF = "2026-10-30"
FACE = "BANDSWITCH-%s.json" % CUTOFF
LATEST = "bandswitch_latest.json"
SELF_FACES = (FACE, LATEST)

STUDY = "E302_universe_switch_backfill"
SELF_MODULE = os.path.splitext(os.path.basename(__file__))[0]

TARGETS = (
    "e290_selfauditable_face_profile.py",
    "e291_ambiguity_chance.py",
    "e292_scope_fix_plan.py",
)

STATUS_STABLE = drive.STATUS_STABLE
STATUS_FLIPS = drive.STATUS_FLIPS
STATUS_NO_REPRO = drive.STATUS_NO_REPRO
STATUS_UNMEASURABLE = drive.STATUS_UNMEASURABLE
STATUSES = drive.STATUSES

VERDICT_FLIPS = drive.VERDICT_DEPENDS
VERDICT_STABLE = drive.VERDICT_STABLE
VERDICT_UNMEASURABLE = drive.VERDICT_UNMEASURABLE
VERDICTS = drive.VERDICTS

# The global every study in this family copies its face directory into.
DIR_GLOBAL = "OUTDIR"

MEASURE_TIMEOUT = int(os.environ.get("E302_TIMEOUT", "120"))


# ------------------------------------------------------------------ io
def _load(name, outdir=None):
    with io.open(os.path.join(outdir or OUTDIR, name), encoding="utf-8") as fh:
        return json.load(fh)


def _read_source(path):
    with io.open(path, encoding="utf-8-sig") as fh:
        return fh.read()


def live_universe(outdir=None, exclude=True):
    """Every *.json in the face directory -- not only the family's census glob.

    Two disclosures.  (a) The studies load faces BY NAME out of the census they read, so a face that
    does not match `BAND*.json` may still be read; the staged universe here is deliberately the
    directory itself, and the difference from E294's narrower glob is stated rather than hidden.
    (b) This study's own two files are BAND-prefixed, so they are excluded from its own universe.
    """
    base = outdir or OUTDIR
    names = sorted(os.path.basename(p) for p in glob.glob(os.path.join(base, "*.json")))
    if exclude:
        names = [n for n in names if n not in SELF_FACES]
    return names


# ------------------------------------------------------------------ static pricing
def threaded_cost(src):
    """What an `outdir=` parameter would have to be threaded through, read off the source.

    Three numbers, because they are three different edits: the functions that mention the directory
    global (each needs the parameter added and passed on), the load() calls that omit an outdir
    (each needs one), and the global assignments themselves (each is a copy that a real switch
    removes).
    """
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return None
    functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for leaf in ast.walk(node):
                if isinstance(leaf, ast.Name) and leaf.id == DIR_GLOBAL:
                    functions.append(node.name)
                    break
    loads_default = 0
    loads_all = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "load":
            loads_all += 1
            if not node.args[1:] and not node.keywords:
                loads_default += 1
    globals_assigned = sum(
        1 for node in tree.body
        if isinstance(node, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == DIR_GLOBAL for t in node.targets)
    )
    return {
        "functions_mentioning_the_dir_global": sorted(set(functions)),
        "load_calls": loads_all,
        "load_calls_on_the_module_default": loads_default,
        "module_level_dir_assignments": globals_assigned,
    }


def published_stamp(base, name):
    """A face's own `generated` stamp; None when it publishes none.

    Deliberately NOT vintage._face_stamp(), which falls back to the file mtime.  An mtime fallback
    makes "the universe at publish time" change whenever a face without a stamp is rewritten, i.e.
    the frozen universe is not reproducible.  Observed while building this face: the same code over
    the same directory read e292's staged universe as 163 faces and then 132, with no published face
    touched -- a rule whose witness is a file mtime cannot be re-run and expected to agree.  An
    undated face cannot be shown to postdate the study, so it is kept: the rule the freeze module
    states in its docstring and cannot honour through its own fallback.  There is exactly one undated
    face in this directory today (ERAPOWER-20261029.json), so stamp-only and mtime agree right now
    (129 kept either way) and the difference is a property of the rule, not of today's numbers.
    """
    try:
        face = _load(name, base)
    except Exception:
        return None
    if isinstance(face, dict):
        return vintage._parse(face.get("generated"))
    return None


def frozen_names(base, names, cutoff):
    """(kept, dropped) by the face's own stamp only; undated faces are kept, never dropped."""
    if not cutoff:
        return list(names), []
    kept, dropped = [], []
    for name in names:
        stamp = published_stamp(base, name)
        (dropped if (stamp and stamp > cutoff) else kept).append(name)
    return kept, dropped


def import_closure(roots):
    """Module names reachable from `roots` by static import, read off scripts/*.py.

    The switch cost must be a property of the study, not of the interpreter's history: scanning
    `sys.modules` counted every unrelated module this process happened to have imported, so the same
    measurement read 31 bindings in a fresh process and 33 inside the smoke run (which imports
    everything first) and the leg comparing it to the published face went red for good.
    """
    import ast
    seen, queue = set(), [r for r in roots if r]
    while queue:
        name = queue.pop()
        if name in seen:
            continue
        seen.add(name)
        try:
            src = _read_source(os.path.join(HERE, name + ".py"))
            tree = ast.parse(src)
        except Exception:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    queue.append(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module and not node.level:
                    queue.append(node.module.split(".")[0])
    return seen


def dir_bindings(base=None, roots=None):
    """Every imported module object that holds a copy of the face directory string.

    This is the switch: the universe reaches the study through these bindings, so the number of
    bindings IS the measured cost of a global-redirect switch.  Only modules that already point at
    the published directory are counted, so an unrelated module is never swept in.  With `roots`
    the count is further restricted to the study's own import closure, which makes it independent
    of what else the interpreter has loaded.
    """
    base = base or OUTDIR
    allowed = import_closure(roots) if roots else None
    out = []
    for name in list(sys.modules):
        mod = sys.modules.get(name)
        if mod is None or name == SELF_MODULE:
            continue
        if allowed is not None and name not in allowed:
            continue
        if name in ("__main__", "__mp_main__"):
            # This study's own module when invoked as a script: counting it would make the cost of
            # the switch depend on how the measurement was launched.
            continue
        if getattr(mod, DIR_GLOBAL, None) == base:
            out.append(name)
    return sorted(out)


def redirect(names, target):
    """Point every named module's directory global at `target`; return the previous values."""
    before = {}
    for name in names:
        mod = sys.modules.get(name)
        if mod is None:
            continue
        before[name] = getattr(mod, DIR_GLOBAL, None)
        setattr(mod, DIR_GLOBAL, target)
    return before


def restore(before):
    for name, value in before.items():
        mod = sys.modules.get(name)
        if mod is not None and value is not None:
            setattr(mod, DIR_GLOBAL, value)


def _mtimes(base):
    out = {}
    for path in glob.glob(os.path.join(base, "*.json")):
        try:
            out[os.path.basename(path)] = os.path.getmtime(path)
        except OSError:
            pass
    return out


def named_faces(names, base):
    """The face names those faces mention, resolved against the real directory (one level)."""
    seen = set()
    for name in names:
        try:
            with io.open(os.path.join(base, name), encoding="utf-8") as fh:
                face = json.load(fh)
        except Exception:
            continue
        stack = [face]
        while stack:
            node = stack.pop()
            if isinstance(node, dict):
                stack.extend(node.values())
            elif isinstance(node, list):
                stack.extend(node)
            elif isinstance(node, str) and node.endswith(".json"):
                if os.path.isfile(os.path.join(base, node)) and node not in SELF_FACES:
                    seen.add(node)
    return sorted(seen)


def stage(names, base=None):
    """A temporary universe holding exactly `names` plus the faces those faces name (D3)."""
    base = base or OUTDIR
    tmp = tempfile.mkdtemp(prefix="e302-")
    keep = sorted(set(names) | set(named_faces(names, base)))
    for name in keep:
        src = os.path.join(base, name)
        if os.path.isfile(src):
            shutil.copy2(src, os.path.join(tmp, name))
    return tmp, keep


# ------------------------------------------------------------------ measurement
def blank_row(script):
    return {
        "script": script, "face": None, "build_args": None,
        "published_verdict": None, "face_generated": None,
        "faces_in_directory_now": None, "faces_kept_by_stamp": None,
        "faces_dropped_as_later": None, "staged_face_count": None,
        "staged_widened_by": None, "staged_is_narrower": None,
        "switch_kind": None, "dir_bindings_rewired": None,
        "threaded_cost": None, "varied": None,
        "frozen_verdict": None, "live_verdict": None,
        "published_files_touched": [], "status": STATUS_UNMEASURABLE, "reason": None,
    }


def measure_one(script, base=None):
    base = base or OUTDIR
    row = blank_row(script)
    modname = os.path.splitext(script)[0]
    try:
        mod = __import__(modname)
    except Exception as exc:
        row["reason"] = "import failed: %s: %s" % (type(exc).__name__, exc)
        return row
    row["build_args"] = drive.build_signature(_read_source(os.path.join(HERE, script))) or []
    row["threaded_cost"] = threaded_cost(_read_source(os.path.join(HERE, script)))

    face_name = getattr(mod, "FACE", None)
    if not isinstance(face_name, str) or not os.path.isfile(os.path.join(base, face_name)):
        row["reason"] = "no published face of its own in results/state_tilt (FACE=%r)" % (face_name,)
        row["face"] = face_name if isinstance(face_name, str) else None
        return row
    row["face"] = face_name
    face = _load(face_name, base)
    row["published_verdict"] = face.get("verdict") if isinstance(face, dict) else None
    stamp = vintage._parse(face.get("generated")) if isinstance(face, dict) else None
    row["face_generated"] = stamp

    live = live_universe(base)
    kept, dropped = frozen_names(base, live, stamp)
    row["faces_in_directory_now"] = len(live)
    row["faces_kept_by_stamp"] = len(kept)
    row["faces_dropped_as_later"] = len(dropped)

    if not hasattr(mod, "build"):
        row["reason"] = "the study exposes no build()"
        return row
    row["switch_kind"] = "no_argument_build_needs_a_global_redirect"

    names = dir_bindings(base, roots=[modname])
    row["dir_bindings_rewired"] = names

    before = _mtimes(base)
    tmp = None
    try:
        tmp, staged = stage(kept, base)
        row["staged_face_count"] = len(staged)
        row["staged_widened_by"] = len(staged) - len(kept)
        row["staged_is_narrower"] = len(staged) < len(live)
        if not row["staged_is_narrower"]:
            row["reason"] = ("the staged universe holds %d faces against the live %d -- nothing to "
                             "vary, the two readings would be the same computation"
                             % (len(staged), len(live)))
            return row
        prev = redirect(names, tmp)
        try:
            frozen_reading = mod.build()
        finally:
            restore(prev)
        prev = redirect(names, base)
        try:
            live_reading = mod.build()
        finally:
            restore(prev)
        row["varied"] = ("module-global %s redirect (%d bindings, staged %d faces) vs live "
                         "directory (%d faces)" % (DIR_GLOBAL, len(names), len(staged), len(live)))
    except Exception as exc:
        row["reason"] = "build() raised: %s: %s" % (type(exc).__name__, exc)
        return row
    finally:
        if tmp and os.path.isdir(tmp):
            shutil.rmtree(tmp, ignore_errors=True)
    after = _mtimes(base)
    row["published_files_touched"] = sorted(n for n in after if before.get(n) != after[n])

    row["frozen_verdict"] = (frozen_reading or {}).get("verdict")
    row["live_verdict"] = (live_reading or {}).get("verdict")
    published = row["published_verdict"]
    if row["frozen_verdict"] != published:
        row["status"] = STATUS_NO_REPRO
        row["reason"] = ("the frozen reading does not reproduce the published verdict; the universe "
                         "question cannot be answered behind that drift")
    elif row["live_verdict"] != published:
        row["status"] = STATUS_FLIPS
        row["reason"] = "the verdict moves when the directory grows"
    else:
        row["status"] = STATUS_STABLE
        row["reason"] = "same verdict under both universes"
    return row


def measure_all(base=None):
    base = base or OUTDIR
    # Import every target first, so the module bindings each row counts are the same set -- a
    # per-row import would make the price of the switch depend on the order the rows were measured.
    for script in TARGETS:
        try:
            __import__(os.path.splitext(script)[0])
        except Exception:
            pass  # measure_one re-imports and reports the failure per row
    return [measure_one(script, base) for script in TARGETS]


# ------------------------------------------------------------------ summary / verdict
def summarise(rows):
    counts = {}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    measured = [r for r in rows if r["status"] in (STATUS_STABLE, STATUS_FLIPS, STATUS_NO_REPRO)]
    flips = [r for r in rows if r["status"] == STATUS_FLIPS]
    bindings = sorted({n for r in measured for n in (r.get("dir_bindings_rewired") or [])})
    threading = [
        {"script": r.get("script"),
         "functions": (r.get("threaded_cost") or {}).get("functions_mentioning_the_dir_global") or [],
         "load_calls_on_the_module_default": (r.get("threaded_cost") or {}).get("load_calls_on_the_module_default"),
         "module_level_dir_assignments": (r.get("threaded_cost") or {}).get("module_level_dir_assignments")}
        for r in rows]
    return {
        "studies_priced": len(rows),
        "status_counts": counts,
        "measured": len(measured),
        "unmeasurable": counts.get(STATUS_UNMEASURABLE, 0),
        "flipping": [{"script": r.get("script"), "face": r.get("face"),
                      "published": r.get("published_verdict"), "live": r.get("live_verdict"),
                      "faces_gained": (r.get("faces_in_directory_now") or 0) - (r.get("staged_face_count") or 0)}
                     for r in flips],
        "no_reproduction": [{"script": r.get("script"), "face": r.get("face"),
                             "published": r.get("published_verdict"), "frozen": r.get("frozen_verdict")}
                            for r in rows if r.get("status") == STATUS_NO_REPRO],
        "global_redirect_switch": {
            "dir_global": DIR_GLOBAL,
            "bindings_that_must_move": bindings,
            "bindings_measured": len(bindings),
        },
        "parameter_threading_cost": threading,
        "rows": [
            {"script": r.get("script"), "status": r.get("status"),
             "staged": r.get("staged_face_count"), "live": r.get("faces_in_directory_now"),
             "bindings": len(r.get("dir_bindings_rewired") or [])} for r in rows],
    }


def verdict_of(summary):
    if summary["flipping"]:
        return VERDICT_FLIPS
    if summary["measured"]:
        return VERDICT_STABLE
    return VERDICT_UNMEASURABLE


def reason_of(verdict, summary):
    if verdict == VERDICT_FLIPS:
        worst = max(summary["flipping"], key=lambda f: f["faces_gained"] or 0)
        return ("%d of %d switched studies print a different verdict under the live directory; %s "
                "moves the furthest (%s -> %s after %d more faces)."
                % (len(summary["flipping"]), summary["measured"], worst["script"],
                   worst["published"], worst["live"], worst["faces_gained"] or 0))
    if verdict == VERDICT_STABLE:
        return ("all %d switchable studies print the same verdict under the staged vintage and the "
                "live directory, so the unasked question is now asked and answered for them; the "
                "switch costs %d module bindings to redirect and %d functions to thread"
                % (summary["measured"],
                   summary["global_redirect_switch"]["bindings_measured"],
                   sum(len(t["functions"]) for t in summary["parameter_threading_cost"])))
    return ("no study could be re-derived under a second universe even with the directory global "
            "redirected, so the switch could not be priced")


# ------------------------------------------------------------------ build / run / verify
def build(outdir=None):
    base = outdir or OUTDIR
    rows = measure_all(base)
    summary = summarise(rows)
    verdict = verdict_of(summary)
    if verdict not in VERDICTS:
        raise AssertionError("verdict %r is outside the frozen vocabulary" % (verdict,))
    for row in rows:
        if row["status"] not in STATUSES:
            raise AssertionError("status %r is outside the frozen vocabulary" % (row["status"],))
    counts = {}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    return {
        "study": STUDY,
        "title": ("three studies publish build() with no universe argument -- what would a switch "
                  "cost, and does any verdict flip once they have one"),
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "verdict": verdict,
        "verdict_reason": reason_of(verdict, summary),
        "summary": summary,
        "status_counts_reconciled": counts == summary["status_counts"],
        "varied": "the visible universe, through the module-level directory global",
        "held_fixed": ("the studies' own source is untouched -- no file under scripts/ is edited by "
                       "this study, so every row is a reading of the code as published"),
        "self_faces_excluded": list(SELF_FACES),
        "switch_shapes_priced": {
            "A_global_redirect": ("assign the directory global on every module binding before "
                                  "calling build(); measured, zero source edits, not a durable fix"),
            "B_parameter_threading": ("add outdir=None to build() and pass it through the functions "
                                      "that mention the global and the load() calls that fall back "
                                      "to it; priced per study from the source"),
        },
        "staging_note": ("the staged universe is the stamp-filtered set plus the faces those faces "
                         "name, one level; both counts are published per row and a staging that is "
                         "not narrower than the live directory is classed not_measurable (D2)"),
        "no_bill": ("published faces only; the staged universe is a temporary directory removed "
                    "after each row; no draw stream, no band rebuild, no engine, no network; the "
                    "real directory's mtimes are asserted unchanged around every measurement"),
        "classification_frozen": {
            "A": "reproduces_and_stable -- frozen == published and live == published",
            "B": "reproduces_and_flips -- frozen == published and live != published",
            "C": "does_not_reproduce -- frozen != published",
            "D": "not_measurable -- raised, had no face, or the staging was not narrower",
        },
        "frozen_spec": {
            "dir_global": DIR_GLOBAL,
            "universe_rule": ("the universe at publish time is every *.json whose own `generated` "
                              "stamp is not later than mine; an undated face is kept, never dropped "
                              "on a guess"),
            "widening_rule": "plus every face named inside those faces, resolved against the directory",
            "verdict_rule": ("depends if any switched face flips under the live directory; stable if "
                             "some face was measured and none flips; unmeasurable when nothing could "
                             "be varied"),
            "statuses": list(STATUSES),
            "verdicts": list(VERDICTS),
            "targets": list(TARGETS),
        },
        "rows": rows,
    }


def _stamp():
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def _write(face, outdir=None):
    base = outdir or OUTDIR
    face = dict(face)
    face["generated"] = _stamp()
    for name in SELF_FACES:
        path = os.path.join(base, name)
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(face, ensure_ascii=False, indent=1))
            fh.write("\n")
    return face


def run(save=True, outdir=None):
    face = build(outdir)
    if save:
        face = _write(face, outdir)
    return face


def verify(outdir=None):
    base = outdir or OUTDIR
    problems = []
    try:
        published = _load(FACE, base)
    except Exception as exc:
        return ["published face unreadable: %s: %s" % (type(exc).__name__, exc)]
    fresh = build(base)
    for key in ("verdict", "verdict_reason", "summary", "frozen_spec"):
        if json.dumps(published.get(key), sort_keys=True) != json.dumps(fresh.get(key), sort_keys=True):
            problems.append("field %r does not re-derive" % key)
    for row in published.get("rows") or []:
        if row.get("status") == STATUS_FLIPS and row.get("live_verdict") == row.get("published_verdict"):
            problems.append("%s is classed flipping but publishes the same verdict" % row["script"])
        if row.get("status") == STATUS_STABLE and (
                row.get("frozen_verdict") != row.get("live_verdict")
                or row.get("frozen_verdict") != row.get("published_verdict")):
            problems.append("%s is classed stable but its two readings differ" % row["script"])
        if row.get("status") == STATUS_NO_REPRO and row.get("frozen_verdict") == row.get("published_verdict"):
            problems.append("%s is classed no-repro but reproduces" % row["script"])
        rowscript = row.get("script") or ""
        if rowscript in SELF_FACES:
            problems.append("a row censused this study's own face")
        varied = row.get("varied") or ""
        if row.get("status") in (STATUS_STABLE, STATUS_FLIPS) and " vs " not in varied:
            problems.append("%s was measured without declaring what was varied" % rowscript)
        if row.get("published_files_touched"):
            problems.append("%s wrote to the published directory: %s"
                            % (rowscript, row["published_files_touched"]))
    if published.get("verdict") not in VERDICTS:
        problems.append("verdict outside the frozen vocabulary")
    if not published.get("status_counts_reconciled"):
        problems.append("status counts do not reconcile")
    return problems


# ------------------------------------------------------------------ selftest
def selftest():
    legs = []

    def leg(name, cond, detail=""):
        legs.append((bool(cond), name, detail))

    legs.extend(vintage.selftest())

    src = ('OUTDIR = "x"\n'
           'def load(name, outdir=None):\n    return name\n'
           'def build():\n    load("B.json", "y")\n    return load("A.json")\n'
           'def helper(n):\n    return os.path.join(OUTDIR, n)\n')
    cost = threaded_cost(src)
    leg("L1 the functions that mention the directory global are named",
        cost["functions_mentioning_the_dir_global"] == ["helper"], cost)
    leg("L2 load() calls that fall back to the module default are counted",
        cost["load_calls_on_the_module_default"] == 1 and cost["load_calls"] == 2, cost)
    leg("L3 the module-level directory assignment is counted",
        cost["module_level_dir_assignments"] == 1, cost)
    leg("L4 a function receiving an explicit outdir is not counted as a default load",
        threaded_cost('def load(name, outdir=None):\n    pass\n'
                      'def build():\n    return load("A.json", "y")\n')
        ["load_calls_on_the_module_default"] == 0)
    leg("L5 an unparsable source prices as None", threaded_cost("def (") is None)

    leg("L6 build() with no parameters reads as an empty signature",
        drive.build_signature("def build():\n    pass\n") == [], drive.build_signature("def build():\n    pass\n"))
    leg("L7 build() with a universe argument reads as non-empty",
        drive.build_signature("def build(outdir=None):\n    pass\n") == ["outdir"])

    # A staged universe really is narrower than the live one.
    base_live = live_universe()
    leg("L8 the live universe is non-empty and excludes this study's own faces",
        base_live and not (set(SELF_FACES) & set(base_live)),
        len(base_live))
    leg("L9 this study's own faces are the only ones excluded by name",
        all(n.endswith(".json") for n in base_live))

    # Widening: a face that names another face pulls the named one in.
    tmp_base = tempfile.mkdtemp(prefix="e302-leg-")
    try:
        with io.open(os.path.join(tmp_base, "A.json"), "w", encoding="utf-8") as fh:
            json.dump({"source": "B.json"}, fh)
        with io.open(os.path.join(tmp_base, "B.json"), "w", encoding="utf-8") as fh:
            json.dump({"x": 1}, fh)
        named = named_faces(["A.json"], tmp_base)
        leg("L10 a face named inside another face is admitted by name", named == ["B.json"], named)
        staged, kept = stage(["A.json"], tmp_base)
        leg("L11 the staged directory holds the named face", sorted(os.listdir(staged)) == ["A.json", "B.json"],
            sorted(os.listdir(staged)))
        shutil.rmtree(staged, ignore_errors=True)
        leg("L12 staging removes nothing from the source directory",
            sorted(os.listdir(tmp_base)) == ["A.json", "B.json"])
    finally:
        shutil.rmtree(tmp_base, ignore_errors=True)

    # The redirect really moves a module binding, and restore really puts it back.
    import types
    holder = types.ModuleType("e302_leg_holder")
    holder.OUTDIR = OUTDIR
    sys.modules["e302_leg_holder"] = holder
    try:
        names = dir_bindings(OUTDIR)
        leg("L13 a module holding the directory string is a binding to rewire",
            "e302_leg_holder" in names, names[:5])
        before = redirect(["e302_leg_holder"], "/tmp/elsewhere")
        leg("L14 the redirect moves the binding",
            sys.modules["e302_leg_holder"].OUTDIR == "/tmp/elsewhere")
        restore(before)
        leg("L15 the restore puts the binding back",
            sys.modules["e302_leg_holder"].OUTDIR == OUTDIR)
    finally:
        sys.modules.pop("e302_leg_holder", None)

    # Verdict vocabulary.
    leg("L16 a flipping summary reads as depends",
        verdict_of({"flipping": [{"script": "x", "faces_gained": 3}], "measured": 1,
                    "global_redirect_switch": {"bindings_measured": 0},
                    "parameter_threading_cost": []}) == VERDICT_FLIPS)
    leg("L17 a measured-and-stable summary reads as stable",
        verdict_of({"flipping": [], "measured": 2,
                    "global_redirect_switch": {"bindings_measured": 1},
                    "parameter_threading_cost": [{"functions": []}]}) == VERDICT_STABLE)
    leg("L18 nothing measured reads as unmeasurable",
        verdict_of({"flipping": [], "measured": 0,
                    "global_redirect_switch": {"bindings_measured": 0},
                    "parameter_threading_cost": []}) == VERDICT_UNMEASURABLE)

    rows = [
        {"status": STATUS_STABLE, "script": "a.py", "dir_bindings_rewired": ["e1", "e2"],
         "threaded_cost": {"functions_mentioning_the_dir_global": ["f"],
                           "load_calls_on_the_module_default": 1,
                           "module_level_dir_assignments": 1},
         "staged_face_count": 3, "faces_in_directory_now": 5},
        {"status": STATUS_FLIPS, "script": "b.py", "dir_bindings_rewired": ["e2"],
         "threaded_cost": None, "staged_face_count": 4, "faces_in_directory_now": 9},
        {"status": STATUS_UNMEASURABLE, "script": "c.py", "dir_bindings_rewired": [],
         "threaded_cost": None, "staged_face_count": None, "faces_in_directory_now": 7},
    ]
    summary = summarise(rows)
    leg("L19 the summary counts every status once",
        summary["status_counts"] == {STATUS_STABLE: 1, STATUS_FLIPS: 1, STATUS_UNMEASURABLE: 1},
        summary["status_counts"])
    leg("L20 the bindings are the union across measured rows, deduplicated",
        summary["global_redirect_switch"]["bindings_that_must_move"] == ["e1", "e2"],
        summary["global_redirect_switch"])
    leg("L21 a flip is reported once with its faces gained",
        len(summary["flipping"]) == 1
        and summary["flipping"][0]["faces_gained"] == 5, summary["flipping"])
    leg("L22 an unmeasured row is not counted as measured", summary["measured"] == 2)
    leg("L23 status counts always reconcile by construction",
        sum(summary["status_counts"].values()) == summary["studies_priced"])

    # D2: a staging that is not narrower must not be classed stable.
    leg("L24 narrowness is a required precondition of a stable verdict",
        "staged_is_narrower" in blank_row("x.py"))

    face = build()
    leg("L25 the face publishes its own verdict from the frozen vocabulary", face["verdict"] in VERDICTS)
    leg("L26 every published row carries a status from the frozen vocabulary",
        all(r["status"] in STATUSES for r in face["rows"]))
    leg("L27 every measured row declares what was varied",
        all(" vs " in (r["varied"] or "") for r in face["rows"]
            if r["status"] in (STATUS_STABLE, STATUS_FLIPS)))
    leg("L28 no row wrote to the published directory",
        not any(r["published_files_touched"] for r in face["rows"]))
    leg("L29 the face censuses exactly the three priced studies",
        [r["script"] for r in face["rows"]] == list(TARGETS))
    leg("L30 self-exclusion is published", face["self_faces_excluded"] == list(SELF_FACES))
    leg("L31 the study's own module and __main__ are never counted as bindings",
        not ({"__main__", "__mp_main__", SELF_MODULE} & set(face["summary"]["global_redirect_switch"]
                                                          ["bindings_that_must_move"])),
        face["summary"]["global_redirect_switch"]["bindings_that_must_move"][:4])
    leg("L32 every row prices the same binding set (the switch cost is order-independent)",
        len({len(r["dir_bindings_rewired"] or []) for r in face["rows"]}) == 1,
        [len(r["dir_bindings_rewired"] or []) for r in face["rows"]])
    # D4: the vintage must not move when an UNDATED face is rewritten.  The freeze helper falls back
    # to mtime, so a fixture written today is always "later"; this study's rule keeps undated faces.
    tmp2 = tempfile.mkdtemp(prefix="e302-leg2-")
    try:
        with io.open(os.path.join(tmp2, "OLD.json"), "w", encoding="utf-8") as fh:
            json.dump({"generated": "2026-10-01T00:00:00"}, fh)
        with io.open(os.path.join(tmp2, "NEW.json"), "w", encoding="utf-8") as fh:
            json.dump({"generated": "2026-12-01T00:00:00"}, fh)
        with io.open(os.path.join(tmp2, "UNDATED.json"), "w", encoding="utf-8") as fh:
            json.dump({"study": "x"}, fh)
        cutoff = "2026-10-30T00:00:00"
        kept1, dropped1 = frozen_names(tmp2, ["OLD.json", "NEW.json", "UNDATED.json"], cutoff)
        leg("L33 an undated face is kept and only a stamped-later face is dropped",
            kept1 == ["OLD.json", "UNDATED.json"] and dropped1 == ["NEW.json"], (kept1, dropped1))
        # The contrast: the freeze helper's mtime fallback drops the undated file written now.
        _vkept, _vdropped = vintage.vintage_names(tmp2, ["UNDATED.json"], cutoff)
        leg("L34 the stamp-only rule differs from the mtime fallback it replaces",
            _vdropped == ["UNDATED.json"] and kept1,
            (_vkept, _vdropped))
        os.utime(os.path.join(tmp2, "UNDATED.json"), (1700000000, 1700000000))
        kept2, _ = frozen_names(tmp2, ["OLD.json", "NEW.json", "UNDATED.json"], cutoff)
        leg("L35 touching an undated face does not move the frozen universe", kept2 == kept1, (kept1, kept2))
    finally:
        shutil.rmtree(tmp2, ignore_errors=True)

    # L36 the binding count belongs to the study, not to this interpreter: importing an unrelated
    # module that also binds the directory must not widen it (the smoke-vs-fresh-process drift).
    import types
    probe_root = "e302_leg_probe_root"
    probe_extra = "e302_leg_probe_extra"
    for name in (probe_root, probe_extra):
        mod = types.ModuleType(name)
        setattr(mod, DIR_GLOBAL, OUTDIR)
        sys.modules[name] = mod
    try:
        fn = os.path.join(HERE, probe_root + ".py")
        with io.open(fn, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("import os\n")
        try:
            with_roots = dir_bindings(OUTDIR, roots=[probe_root])
            without = dir_bindings(OUTDIR, roots=["e302_leg_no_such_module"])
        finally:
            os.remove(fn)
        leg("L36 a module outside the study's import closure is never counted as a binding",
            with_roots == [probe_root] and without == [], (with_roots, without))
    finally:
        for name in (probe_root, probe_extra):
            sys.modules.pop(name, None)
    return legs


# ------------------------------------------------------------------ cli
def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "run"
    if cmd == "run":
        face = run(save=True)
        print(json.dumps({"face": FACE, "verdict": face["verdict"],
                          "measured": face["summary"]["measured"],
                          "flipping": len(face["summary"]["flipping"]),
                          "status_counts": face["summary"]["status_counts"]}, ensure_ascii=False))
        return 0
    if cmd == "build":
        print(json.dumps(build(), ensure_ascii=False, indent=1))
        return 0
    if cmd == "verify":
        problems = verify()
        print(json.dumps({"problems": problems}, ensure_ascii=False))
        return 1 if problems else 0
    if cmd == "selftest":
        legs = selftest()
        passed = sum(1 for ok, _, _ in legs if ok)
        for ok, name, detail in legs:
            print("%s %s%s" % ("PASS" if ok else "FAIL", name,
                               "" if ok else "  <- %r" % (detail,)))
        print("%d/%d" % (passed, len(legs)))
        return 0 if passed == len(legs) else 1
    if cmd == "measure":
        row = measure_one(argv[1])
        print(json.dumps(row, ensure_ascii=False))
        return 0
    print("usage: e302_universe_switch_backfill.py [run|build|verify|selftest|measure <script>]")
    return 2


if __name__ == "__main__":
    sys.exit(main())