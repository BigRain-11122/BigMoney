"""E294 -- which BAND-family studies census the LIVE face directory, and does any published verdict
depend on the universe it happened to see?

WHY THIS FACE EXISTS
--------------------
r1314 found the failure mode the hard way: every study in this family censuses its own siblings'
published faces, so the universe a face reads GROWS by one face each time another study publishes.
Four smoke legs went red in 2026-10-31 for a reason that was not a number -- the older faces had been
re-derived over a directory that had grown (E286 32 -> 34 faces, E281 27 -> 34, E282 55 -> 67).
Three studies were then frozen to their own vintage (scripts/e_band_family_vintage.py).

That fix answered "how do we stop the drift".  It did not answer the question underneath it:
for each study, is its published verdict a function of the universe it saw?  A verdict that flips
when 30 more faces appear is not a wider reading of the same fact -- it is a statement about the
directory.

WHAT IS MEASURED, AND WHAT IS NOT
---------------------------------
The universe is the ONLY thing varied.  A face is re-derived twice in the same process:
  * FROZEN -- the visible census is restricted to the faces that already existed when the face
    published (each face carries its own `generated` stamp, so this is mechanical), and
  * LIVE   -- the visible census is every BAND* face in results/state_tilt today.
Sibling faces loaded by NAME always come from the live directory in both readings: the family's
`load(name)` helpers take no outdir, so holding those fixed is fidelity, not a shortcut.  The face
discloses that in `varied` / `held_fixed`.

Not every study can be asked.  `build()` accepts `outdir` in some and nothing in others; a study
whose build takes no universe argument is reported `not_measurable` with the reason, never guessed
and never edited to fit the test.

THREE-WAY CLASSIFICATION (frozen before any number is read)
----------------------------------------------------------
A. reproduces_and_stable     frozen reading == published verdict AND live reading == published.
B. reproduces_and_flips      frozen == published, live != published.  The verdict is a function of
                             the universe; the published face is a reading of a directory, not of data.
C. does_not_reproduce        frozen != published.  The face has already drifted for some other
                             reason (r1316 / E243 family), so the universe question cannot be
                             answered for it here -- and the drift is disclosed, not attributed.
D. not_measurable            build() takes no universe argument (or raised); reason recorded.

VERDICT VOCABULARY (frozen)
---------------------------
verdict_depends_on_the_universe_it_saw      -- at least one frozen-reading face flips under the
                                               live directory (class B non-empty)
no_published_verdict_moves_with_the_universe-- class B empty while at least one face was measured
unmeasurable_before_the_universe_question   -- nothing could be varied at all

NO BILL: published faces are re-read and re-derived from them.  No draw stream, no band rebuild, no
engine, no network.  Nothing in results/state_tilt is written by the measurement -- the frozen
census is staged in a temporary directory, and the legs assert the published files are untouched.
"""
import ast
import glob
import io
import json
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e_band_family_vintage as vintage  # noqa: E402  (the freeze module this study reviews)

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
CUTOFF = "2026-10-29"
EVIDENCE_CUTOFF = "2026-10-29"
FACE = "BANDFROZEN-%s.json" % CUTOFF
LATEST = "bandfrozen_latest.json"
SELF_FACES = (FACE, LATEST)

STUDY = "E294_live_universe_drift"
SELF_MODULE = os.path.splitext(os.path.basename(__file__))[0]

# The census glob the family uses.  Anything wider is a study we cannot stage faithfully.
CENSUS_GLOB = "BAND*.json"

VERDICT_DEPENDS = "verdict_depends_on_the_universe_it_saw"
VERDICT_STABLE = "no_published_verdict_moves_with_the_universe"
VERDICT_UNMEASURABLE = "unmeasurable_before_the_universe_question"
VERDICTS = (VERDICT_DEPENDS, VERDICT_STABLE, VERDICT_UNMEASURABLE)

STATUS_STABLE = "reproduces_and_stable"
STATUS_FLIPS = "reproduces_and_flips"
STATUS_NO_REPRO = "does_not_reproduce"
STATUS_UNMEASURABLE = "not_measurable"
STATUSES = (STATUS_STABLE, STATUS_FLIPS, STATUS_NO_REPRO, STATUS_UNMEASURABLE)

# Keys a face may use to publish "which faces I saw".  First present list of strings wins.
UNIVERSE_KEYS = ("faces_censused", "census_faces", "universe_faces", "faces_used",
                 "faces_in_scope", "source_faces")


# ------------------------------------------------------------------ io
def _load(name, outdir=None):
    with io.open(os.path.join(outdir or OUTDIR, name), encoding="utf-8") as fh:
        return json.load(fh)


def _read_source(path):
    with io.open(path, encoding="utf-8-sig") as fh:
        return fh.read()


def live_names(outdir=None, pattern=CENSUS_GLOB, exclude=True):
    """The family census as the studies see it.

    Two disclosures ride on this one glob.  (a) The family's own glob is `BAND*.json`, and on this
    filesystem that is CASE-INSENSITIVE, so the `band*_latest.json` mirrors are in the census too --
    they always were, and narrowing the glob here would silently change every study's universe.
    (b) This study's own face starts with BAND as well; it is excluded from its own census, as E286
    did, so publishing this face does not shift the numbers it publishes.
    """
    base = outdir or OUTDIR
    names = sorted(os.path.basename(p) for p in glob.glob(os.path.join(base, pattern)))
    if exclude:
        names = [n for n in names if n not in SELF_FACES]
    return names


# ------------------------------------------------------------------ static read of a study
def module_strings(src):
    """Module-level `NAME = <string>` constants, resolving `"X-%s.json" % CUTOFF` one level deep."""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return {}
    consts = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        value = None
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            value = node.value.value
        elif (isinstance(node.value, ast.BinOp) and isinstance(node.value.op, ast.Mod)
              and isinstance(node.value.left, ast.Constant)
              and isinstance(node.value.right, (ast.Name, ast.Constant))):
            arg = (consts.get(node.value.right.id) if isinstance(node.value.right, ast.Name)
                   else node.value.right.value)
            if isinstance(arg, str):
                try:
                    value = node.value.left.value % arg
                except TypeError:
                    value = None
        if value is not None:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    consts[target.id] = value
    return consts


def build_signature(src, names=("build",)):
    """Parameter names of the first function in `names` the script defines; None when absent."""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return None
    for want in names:
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == want:
                return [a.arg for a in node.args.args]
    return None


# Parameters that mean "this entry point draws", i.e. it is not a reader of published faces.
DRAW_ARGS = ("seeds", "workers", "per", "draws", "n_draws", "rng", "resamples")

# Entry points in the order they are preferred.  `run` is only usable with save=False.
ENTRY_ORDER = ("build", "run")


def census_glob(src):
    """The literal glob the study censuses with; None when it does not glob at all."""
    hits = re.findall(r"glob\.glob\([^)]*?[\"']([^\"']+\.json)[\"']", src)
    return hits[0] if hits else None


def freeze_used(src):
    """True when the study routes its census through the vintage module.

    Call shape alone is not enough: e282 freezes through a local `_vintage_names(outdir)` wrapper that
    the call-site regex never sees.  Import plus any vintage recipe (a `vintage.` call or a local
    `*_vintage` helper) is the honest test.
    """
    if "e_band_family_vintage" not in src:
        return False
    return bool(re.search(r"vintage\.|_vintage", src))


def read_list(face):
    """(names, key) -- the universe this face published, when it stored one."""
    for key in UNIVERSE_KEYS:
        value = face.get(key)
        if isinstance(value, list) and value and all(isinstance(x, str) for x in value):
            return list(value), key
    for key in UNIVERSE_KEYS:
        for holder in ("census", "scope", "universe_vintage"):
            blk = face.get(holder)
            if not isinstance(blk, dict):
                continue
            value = blk.get(key)
            if isinstance(value, list) and value and all(isinstance(x, str) for x in value):
                return list(value), "%s.%s" % (holder, key)
    return None, None


def family_scripts():
    """Source-scan membership: a study is in the family when it globs BAND*.json or freezes a census.

    Membership is decided by BEHAVIOUR, not by a path literal: filtering on the string 'state_tilt'
    misses every study that takes OUTDIR from a sibling -- exactly the frozen ones.  Nothing is
    imported here; a study that hangs on import must not be able to hang the census.
    """
    out = []
    for path in sorted(glob.glob(os.path.join(HERE, "e2*.py"))):
        name = os.path.basename(path)
        if os.path.splitext(name)[0] == SELF_MODULE:
            continue   # a census of the directory cannot include the census that lists it
        try:
            src = _read_source(path)
        except Exception:
            continue
        pattern = census_glob(src)
        if not pattern and "e_band_family_vintage" not in src:
            continue
        out.append({
            "script": name,
            "module": os.path.splitext(name)[0],
            "glob": pattern or CENSUS_GLOB,
            "frozen_in_code": freeze_used(src),
            "build": build_signature(src, ("build",)),
            "run": build_signature(src, ("run",)),
        })
    return out


def directory_shape():
    """How big the family is, and how much of it can even be universe-dependent.

    Only studies that census the directory (glob it) can move when the directory grows.  The rest
    read named sibling faces, which are pinned by name and therefore vintage-stable by construction --
    worth saying out loud, because "the family" and "the part of it this question can touch" are two
    different sizes.
    """
    census, named = [], []
    for path in sorted(glob.glob(os.path.join(HERE, "e2*.py"))):
        name = os.path.basename(path)
        if os.path.splitext(name)[0] == SELF_MODULE:
            continue
        try:
            src = _read_source(path)
        except Exception:
            continue
        if census_glob(src) or "e_band_family_vintage" in src:
            census.append(name)
        elif re.search(r"(load|_safe_load)\(", src) and "e2" in src:
            named.append(name)
    return {"family_scripts": len(census) + len(named),
            "census_the_directory": len(census),
            "read_named_faces_only": len(named),
            "census_scripts": census}


def candidates(outdir=None):
    """Back-compat: the family scripts, resolved (FACE known) by the child measurement."""
    return family_scripts()


def entry_point(cand):
    """(kind, params, refusal) -- the cheapest function that re-derives the face without saving.

    `build()` never writes.  `run()` is accepted only with an explicit `save` switch that we set to
    False, and never when its parameters include a draw stream: re-deriving a published face must
    not draw.
    """
    if cand["build"] is not None:
        params = list(cand["build"])
        if "outdir" in params or "extend" in params:
            return "build", params, None
        return None, params, "build(%s) takes no universe argument" % ", ".join(params)
    if cand["run"] is not None:
        params = list(cand["run"])
        draws = [p for p in params if p in DRAW_ARGS]
        if draws:
            return None, params, "its only entry point draws (run(%s)) -- no bill" % ", ".join(params)
        if "outdir" not in params and "extend" not in params:
            return None, params, "run(%s) takes no universe argument" % ", ".join(params)
        if "save" not in params:
            return None, params, "run(%s) cannot be asked to not save" % ", ".join(params)
        return "run", params, None
    return None, [], "the script exposes neither build() nor run()"


# ------------------------------------------------------------------ measurement
def stage(names, outdir=None):
    """A temporary census directory holding exactly `names` -- the only thing the study can see."""
    tmp = tempfile.mkdtemp(prefix="e294-")
    base = outdir or OUTDIR
    for name in names:
        src = os.path.join(base, name)
        if os.path.isfile(src):
            shutil.copy2(src, os.path.join(tmp, name))
    return tmp


def _mtimes(base):
    """mtime snapshot of the published face directory -- evidence that measuring writes nothing."""
    out = {}
    for path in glob.glob(os.path.join(base, "*.json")):
        try:
            out[os.path.basename(path)] = os.path.getmtime(path)
        except OSError:
            pass
    return out


MEASURE_TIMEOUT = int(os.environ.get("E294_TIMEOUT", "120"))


def blank_row(cand):
    """Every row carries the same keys, so a reader never has to test for the shape of a failure."""
    return {
        "script": cand["script"], "face": None, "census_glob": cand.get("glob"),
        "frozen_in_code": cand.get("frozen_in_code"), "build_args": cand.get("build"),
        "run_args": cand.get("run"), "published_verdict": None, "face_generated": None,
        "universe_published_key": None, "faces_published_used": None,
        "faces_in_directory_now": None, "faces_kept_by_stamp": None,
        "faces_dropped_as_later": None, "faces_gained_since_publish": None,
        "entry_point": None, "varied": None, "frozen_verdict": None, "live_verdict": None,
        "published_files_touched": [], "status": STATUS_UNMEASURABLE, "reason": None,
    }


def measure_isolated(cand, outdir=None):
    """Run one study's measurement in a CHILD process.

    A study in this family can be slow or can wedge (a full census over 1,700 bars, a module that
    reaches for the network on import).  In-process that hang takes the whole census with it -- which
    is what happened on the first build of this face.  Each study therefore gets its own process and
    a wall-clock cap, and a cap that fires is reported rather than hidden.
    """
    import subprocess
    cmd = [sys.executable, os.path.abspath(__file__), "measure", cand["script"]]
    if outdir:
        cmd.append(outdir)
    blank = blank_row(cand)
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=MEASURE_TIMEOUT,
                              cwd=ROOT, errors="replace")
    except subprocess.TimeoutExpired:
        blank.update(status=STATUS_UNMEASURABLE,
                     reason="measurement exceeded the %ds cap" % MEASURE_TIMEOUT)
        return blank
    if proc.returncode != 0:
        tail = (proc.stderr or "").strip().splitlines()[-1:] or ["no stderr"]
        blank.update(status=STATUS_UNMEASURABLE,
                     reason="child exited %d: %s" % (proc.returncode, tail[0][:160]))
        return blank
    payload = None
    for line in reversed((proc.stdout or "").splitlines()):
        line = line.strip()
        if line.startswith("{"):
            try:
                payload = json.loads(line)
                break
            except Exception:
                continue
    if not isinstance(payload, dict):
        blank.update(status=STATUS_UNMEASURABLE, reason="child produced no readable row")
        return blank
    if payload.get("skip"):
        return None
    return payload


def measure_all(outdir=None):
    base = outdir or OUTDIR
    rows = []
    for cand in family_scripts():
        row = measure_isolated(cand, base)
        if row is None:
            continue
        rows.append(row)
    return rows


def measure_one(cand, outdir=None):
    """Re-derive the study twice (frozen universe, live universe) and classify the verdict."""
    base = outdir or OUTDIR
    row = blank_row(cand)
    try:
        mod = __import__(cand.get("module") or os.path.splitext(cand["script"])[0])
    except Exception as exc:
        row["status"] = STATUS_UNMEASURABLE
        row["reason"] = "import failed: %s: %s" % (type(exc).__name__, exc)
        row["face"] = None
        row["published_verdict"] = None
        return row
    face_name = getattr(mod, "FACE", None)
    if not isinstance(face_name, str) or not os.path.isfile(os.path.join(base, face_name)):
        row["status"] = STATUS_UNMEASURABLE
        row["reason"] = "no published face of its own in results/state_tilt (FACE=%r)" % (face_name,)
        row["face"] = face_name if isinstance(face_name, str) else None
        row["published_verdict"] = None
        return row
    cand = dict(cand)
    cand["face"] = face_name
    row["face"] = face_name
    face = _load(face_name, base)
    row["published_verdict"] = face.get("verdict")
    stamp = vintage._parse(face.get("generated")) if isinstance(face, dict) else None
    row["face_generated"] = stamp

    live = live_names(base, cand["glob"] or CENSUS_GLOB)
    published_names, published_key = read_list(face) if isinstance(face, dict) else (None, None)
    row["universe_published_key"] = published_key
    row["faces_published_used"] = len(published_names) if published_names else None
    row["faces_in_directory_now"] = len(live)

    kept, dropped = vintage.vintage_names(base, live, stamp)
    row["faces_kept_by_stamp"] = len(kept)
    row["faces_dropped_as_later"] = len(dropped)
    row["faces_gained_since_publish"] = len(live) - len(kept)

    kind, params, refusal = entry_point(cand)
    row["entry_point"] = kind
    if refusal:
        row["status"] = STATUS_UNMEASURABLE
        row["reason"] = refusal
        return row

    def call(universe_dir, extend):
        if kind == "build":
            kwargs = {}
            if "extend" in params:
                kwargs["extend"] = extend
            for key, value in (("outdir", universe_dir), ("save", False)):
                if key in params:
                    kwargs[key] = value
            return mod.build(**kwargs)
        kwargs = {}
        if "extend" in params:
            kwargs["extend"] = extend
        if "save" in params:
            kwargs["save"] = False
        if "outdir" in params:
            kwargs["outdir"] = universe_dir
        return mod.run(**kwargs)

    before = _mtimes(base)
    frozen_reading = live_reading = None
    tmp = None
    try:
        if "extend" in params:
            # The study owns the freeze switch: extend=False honours its vintage, extend=True is the
            # live directory.  (Passing outdir=staging here would run the SAME computation twice and
            # manufacture a stable verdict -- the tautology E294 exists to catch.)
            frozen_reading = call(base, False)
            live_reading = call(base, True)
            row["varied"] = "%s(extend=False, freeze on) vs %s(extend=True, live directory)" % (kind, kind)
        else:
            tmp = stage(kept, base)
            frozen_reading = call(tmp, False)
            live_reading = call(base, False)
            row["varied"] = "%s(outdir=frozen staging) vs %s(outdir=live)" % (kind, kind)
        row["distinct_measurements"] = row["varied"] is not None
    except Exception as exc:
        row["status"] = STATUS_UNMEASURABLE
        row["reason"] = "%s raised: %s: %s" % (kind, type(exc).__name__, exc)
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
                         "question cannot be answered for this face")
    elif row["live_verdict"] != published:
        row["status"] = STATUS_FLIPS
        row["reason"] = "the verdict moves when the directory grows"
    else:
        row["status"] = STATUS_STABLE
        row["reason"] = "same verdict under both universes"
    return row


# ------------------------------------------------------------------ summary / verdict
def summarise(rows):
    counts = {}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    flips = [r for r in rows if r["status"] == STATUS_FLIPS]
    measured = [r for r in rows if r["status"] in (STATUS_STABLE, STATUS_FLIPS, STATUS_NO_REPRO)]
    ranked = sorted(measured + [r for r in rows if r["status"] == STATUS_UNMEASURABLE],
                    key=lambda r: (-(r.get("faces_gained_since_publish") or 0), r["script"]))
    return {
        "studies_censused": len(rows),
        "status_counts": counts,
        "measured": len(measured),
        "unmeasurable": counts.get(STATUS_UNMEASURABLE, 0),
        "flipping": [{"script": r["script"], "face": r["face"],
                      "published": r["published_verdict"], "live": r["live_verdict"],
                      "faces_gained": r["faces_gained_since_publish"]} for r in flips],
        "no_reproduction": [{"script": r["script"], "face": r["face"],
                             "published": r["published_verdict"],
                             "frozen": r["frozen_verdict"]}
                            for r in rows if r["status"] == STATUS_NO_REPRO],
        "frozen_in_code": sorted(r["script"] for r in rows if r["frozen_in_code"]),
        "unfrozen_in_code": sorted(r["script"] for r in rows if not r["frozen_in_code"]),
        "ranking_by_faces_gained": [
            {"script": r["script"], "faces_gained": r.get("faces_gained_since_publish"),
             "status": r["status"]} for r in ranked],
    }


def verdict_of(summary):
    if summary["flipping"]:
        return VERDICT_DEPENDS
    if summary["measured"]:
        return VERDICT_STABLE
    return VERDICT_UNMEASURABLE


def reason_of(verdict, summary):
    if verdict == VERDICT_DEPENDS:
        worst = max(summary["flipping"], key=lambda f: f["faces_gained"] or 0)
        return ("%d of %d measured studies print a different verdict under the live directory; %s "
                "moves the furthest (%s -> %s after %d more faces). A verdict that moves is a "
                "reading of the directory, not of the data."
                % (len(summary["flipping"]), summary["measured"], worst["script"],
                   worst["published"], worst["live"], worst["faces_gained"] or 0))
    if verdict == VERDICT_STABLE:
        return ("all %d measured studies print the same verdict under the published vintage and the "
                "live directory; %d could not be varied at all and are named with their reason"
                % (summary["measured"], summary["unmeasurable"]))
    return ("no study in the family could be re-derived under a second universe without editing its "
            "code, so the universe question is unasked rather than answered")


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
        "title": ("which BAND-family studies census the live directory, how many faces each would "
                  "gain if re-derived today, and does any published verdict depend on it"),
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "verdict": verdict,
        "verdict_reason": reason_of(verdict, summary),
        "summary": summary,
        "status_counts_reconciled": counts == summary["status_counts"],
        "varied": "the visible census universe",
        "held_fixed": ("every face loaded by name comes from the live directory in both readings -- "
                       "the family's load(name) helpers take no outdir"),
        "self_faces_excluded": list(SELF_FACES),
        "directory_shape": directory_shape(),
        "glob_case_note": ("the family's census glob is `BAND*.json` and globbing is case-insensitive "
                           "on this filesystem, so `band*_latest.json` mirrors are inside every "
                           "study's universe; narrowing it here would change all of them"),
        "isolation_note": ("each study is measured in its own process under a %ds cap; a study that "
                           "does not answer is reported, not silently dropped" % MEASURE_TIMEOUT),
        "classification_frozen": {
            "A": "reproduces_and_stable -- frozen == published and live == published",
            "B": "reproduces_and_flips -- frozen == published and live != published",
            "C": "does_not_reproduce -- frozen != published (drift from another cause, not attributed)",
            "D": "not_measurable -- build() takes no universe argument, or raised",
        },
        "no_bill": ("published faces only; the frozen census is staged in a temporary directory and "
                    "removed; no draw stream, no band rebuild, no engine, no network; nothing in "
                    "results/state_tilt is written by the measurement"),
        "rows": rows,
        "frozen_spec": {
            "census_glob": CENSUS_GLOB,
            "universe_rule": ("the universe at publish time is the faces whose own `generated` stamp "
                              "is not later than mine; an undated face is kept, never dropped on a "
                              "guess"),
            "face_universe_keys": list(UNIVERSE_KEYS),
            "verdict_rule": ("depends if any measured face flips under the live directory; stable if "
                             "some face was measured and none flips; unmeasurable when no face could "
                             "be varied"),
            "statuses": list(STATUSES),
            "verdicts": list(VERDICTS),
        },
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
    """Re-derive and compare with the published face; metadata (generated) is ignored."""
    base = outdir or OUTDIR
    problems = []
    try:
        published = _load(FACE, base)
    except Exception as exc:
        return ["published face unreadable: %s: %s" % (type(exc).__name__, exc)]
    fresh = build(base)
    for key in ("verdict", "verdict_reason", "summary", "rows", "frozen_spec"):
        if json.dumps(published.get(key), sort_keys=True) != json.dumps(fresh.get(key), sort_keys=True):
            problems.append("field %r does not re-derive" % key)
    for row in published.get("rows") or []:
        if row.get("status") == STATUS_FLIPS:
            if row.get("live_verdict") == row.get("published_verdict"):
                problems.append("%s is classed flipping but publishes the same verdict" % row["script"])
        if row.get("status") == STATUS_STABLE:
            if (row.get("frozen_verdict") != row.get("live_verdict")
                    or row.get("frozen_verdict") != row.get("published_verdict")):
                problems.append("%s is classed stable but its two readings differ" % row["script"])
        if row.get("status") == STATUS_NO_REPRO:
            if row.get("frozen_verdict") == row.get("published_verdict"):
                problems.append("%s is classed no-repro but reproduces" % row["script"])
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

    src = 'CUTOFF = "2026-10-29"\nFACE = "BANDFOO-%s.json" % CUTOFF\n'
    leg("L1 a %%-formatted FACE constant resolves", module_strings(src).get("FACE") == "BANDFOO-2026-10-29.json",
        module_strings(src))

    leg("L2 build() parameter names are read from the source",
        build_signature("def build(outdir=None, extend=False):\n    pass\n") == ["outdir", "extend"],
        build_signature("def build(outdir=None, extend=False):\n    pass\n"))
    leg("L3 a script with no build() reads as None", build_signature("x = 1\n") is None)

    s = 'import glob\nfor p in glob.glob(os.path.join(OUTDIR, "BAND*.json")): pass\n'
    leg("L4 the census glob is read as a literal", census_glob(s) == "BAND*.json", census_glob(s))
    leg("L5 a study calling vintage.vintage_names is classed frozen",
        freeze_used('import e_band_family_vintage as vintage\nvintage.vintage_names(a,b,c)\n'))
    leg("L6 a study that never calls the freeze is not classed frozen", not freeze_used('import glob\n'))

    face = {"faces_censused": ["A.json", "B.json"]}
    names, key = read_list(face)
    leg("L7 a published name list is found with its key", names == ["A.json", "B.json"] and key == "faces_censused",
        (names, key))
    names2, key2 = read_list({"universe_vintage": {"faces_used": ["X.json"]}})
    leg("L8 a nested name list is found and names its path", names2 == ["X.json"] and key2 == "universe_vintage.faces_used",
        (names2, key2))
    leg("L9 a face with no name list yields (None, None)", read_list({"verdict": "x"}) == (None, None))

    def classify(published, frozen, live):
        if frozen != published:
            return STATUS_NO_REPRO
        if live != published:
            return STATUS_FLIPS
        return STATUS_STABLE

    leg("L10 the three-way rule: stable", classify("v", "v", "v") == STATUS_STABLE)
    leg("L11 the three-way rule: flips", classify("v", "v", "w") == STATUS_FLIPS)
    leg("L12 the three-way rule: does not reproduce (attribution refused)",
        classify("v", "w", "w") == STATUS_NO_REPRO)

    summary = {"measured": 2, "unmeasurable": 0, "status_counts": {},
               "flipping": [{"script": "x", "face": "f", "published": "a", "live": "b", "faces_gained": 3}]}
    leg("L13 a single flip decides the face verdict", verdict_of(summary) == VERDICT_DEPENDS)
    leg("L14 an empty flip list with measurements is stable",
        verdict_of({"measured": 2, "unmeasurable": 0, "status_counts": {}, "flipping": []}) == VERDICT_STABLE)
    leg("L15 nothing measured is unmeasurable, not stable",
        verdict_of({"measured": 0, "unmeasurable": 4, "status_counts": {}, "flipping": []}) == VERDICT_UNMEASURABLE)

    # A staged census really is narrower than the live one, and the staging is removed.
    tmp = tempfile.mkdtemp(prefix="e294-leg-")
    try:
        for name in ("BANDX-2026-10-29.json", "BANDY-2026-10-29.json"):
            with io.open(os.path.join(tmp, name), "w", encoding="utf-8") as fh:
                fh.write("{}")
        staged = stage(["BANDX-2026-10-29.json"], tmp)
        try:
            leg("L16 a staged census holds exactly the frozen universe",
                sorted(os.listdir(staged)) == ["BANDX-2026-10-29.json"], os.listdir(staged))
            leg("L17 the live census is the wider one", len(live_names(tmp)) == 2, live_names(tmp))
        finally:
            shutil.rmtree(staged, ignore_errors=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # The published faces are untouched by a measurement.
    before = {name: os.path.getmtime(os.path.join(OUTDIR, name)) for name in live_names()}
    build(OUTDIR)
    after = {name: os.path.getmtime(os.path.join(OUTDIR, name)) for name in live_names()}
    leg("L18 measuring writes nothing into results/state_tilt", before == after,
        [n for n in before if before[n] != after[n]])

    face_now = build(OUTDIR)
    rows = face_now["rows"]
    leg("L19 every row carries published and live side by side when it was measured",
        all(("published_verdict" in r and "live_verdict" in r) for r in rows
            if r["status"] != STATUS_UNMEASURABLE), "")
    leg("L20 every not_measurable row names its reason",
        all(r.get("reason") for r in rows if r["status"] == STATUS_UNMEASURABLE), "")
    leg("L21 no row claims a negative faces gained",
        all((r.get("faces_gained_since_publish") or 0) >= 0 for r in rows), "")
    counts = {}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    leg("L22 the status counts reconcile with the row list", counts == face_now["summary"]["status_counts"], counts)
    leg("L23 the decided verdict is inside the frozen vocabulary", face_now["verdict"] in VERDICTS, face_now["verdict"])
    leg("L24 the face disclaims billing", bool(face_now.get("no_bill")))
    leg("L25 the face says what was held fixed", "load(name)" in (face_now.get("held_fixed") or ""))
    unpublished = [r for r in rows if r["faces_published_used"] is None]
    leg("L26 a face that publishes no universe list is disclosed rather than assumed",
        all(r["universe_published_key"] is None for r in unpublished), len(unpublished))
    leg("L27 the census never includes the script that runs it",
        all(r["script"] != os.path.basename(__file__) for r in rows),
        [r["script"] for r in rows if r["script"] == os.path.basename(__file__)])
    shape = face_now.get("directory_shape") or {}
    leg("L28 the family shape says how much of the family the question can even reach",
        shape.get("census_the_directory") == len(rows)
        and shape.get("family_scripts", 0) >= shape.get("census_the_directory", 0), shape)
    leg("L29 no measurement touched a published file",
        all(not r.get("published_files_touched") for r in rows),
        [r["script"] for r in rows if r.get("published_files_touched")])
    leg("L30 every measured row names two different calls, so 'stable' cannot be two identical runs",
        all((" vs " in (r.get("varied") or "")) for r in rows
            if r["status"] in (STATUS_STABLE, STATUS_FLIPS, STATUS_NO_REPRO)),
        [r["script"] for r in rows
         if r["status"] in (STATUS_STABLE, STATUS_FLIPS, STATUS_NO_REPRO) and " vs " not in (r.get("varied") or "")])
    return legs


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    mode = argv[0] if argv else "run"
    if mode == "run":
        face = run()
        print("verdict %s" % face["verdict"])
        print("written results/state_tilt/%s" % FACE)
        return 0
    if mode == "verify":
        problems = verify()
        for problem in problems:
            print("PROBLEM %s" % problem)
        print("problems=%d" % len(problems))
        return 0 if not problems else 1
    if mode == "selftest":
        legs = selftest()
        failed = [l for l in legs if not l[0]]
        for ok, name, detail in legs:
            if not ok:
                print("FAIL %s %s" % (name, detail))
        print("selftest %d/%d" % (len(legs) - len(failed), len(legs)))
        return 0 if not failed else 1
    if mode == "measure":
        script = argv[1]
        base = argv[2] if len(argv) > 2 else OUTDIR
        cands = [c for c in family_scripts() if c["script"] == script]
        if not cands:
            print(json.dumps({"skip": "not a family script"}))
            return 0
        row = measure_one(cands[0], base)
        if row.get("face") is None and row.get("status") == STATUS_UNMEASURABLE \
                and "no published face" in (row.get("reason") or ""):
            print(json.dumps({"skip": row["reason"]}))
            return 0
        print(json.dumps(row, ensure_ascii=False))
        return 0
    print("usage: e294_live_universe_drift.py [run|verify|selftest|measure <script>]")
    return 2


if __name__ == "__main__":
    sys.exit(main())