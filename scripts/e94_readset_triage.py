"""E94: triage the remaining E79-exposed census modes by their actual read set.

E79 flagged 33 census modes as *exposed* (they read the per-name loader, publish a
weight-``1/n`` number, and carry no ``raw=`` hook). E81 leg 5 then proved the flag is
necessary but not sufficient: the tilt decomposer reads the wide book yet is
structurally immune, because none of the repaired names is a ladder member and its
arithmetic never touches the wide book.

This tool answers the same question for every remaining exposed mode, mechanically,
without rewriting any published face:

  A  unscreened   -- the untouched universe the published face uses
  B  neutralise   -- the repaired universe (scripts/panel_screen.py, arm `neutralise`)
  C  perturb-ladder  -- 5 ladder members stepped +5% at the calendar midpoint
  D  perturb-repaired -- 5 repaired names stepped +5% at the calendar midpoint

B says whether the repaired prints are charged; D says whether those names enter the
arithmetic *at all*; C is the activity control that proves the diff machinery can see
a change on this mode. Every arm runs into a temp directory, so no face is replaced.

Per row the face publishes: reads_loader / read_set evidence / intersects_repaired /
charged_by_repair / verdict, plus the first changed paths of each arm.

Usage:
    python scripts/e94_readset_triage.py run       # write results/e79/triage-<cutoff>.json
    python scripts/e94_readset_triage.py selftest  # hermetic checks
"""

import json
import os
import shutil
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "scripts")
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)

MATRIX = os.path.join(ROOT, "results", "e44_midmonth", "FACESCREEN-20261021.json")
OUTDIR = os.path.join(ROOT, "results", "e79")

# Modes whose exposure was already closed by an E81 screened twin.
CLOSED = {
    "calcost": "screencalc",
    "era": "screenreg",
    "neutralrob": "screenrob",
    "tilt": "screentilt",
}

VOLATILE = {"generated", "generated_at", "generated_ts", "ts", "elapsed",
            "elapsed_sec", "runtime_sec", "wall_clock", "as_of_utc"}

PERTURB_FACTOR = 1.05


# ------------------------------------------------------------------ pure parts

def flatten(obj, prefix=""):
    """-> {path: scalar}. Volatile bookkeeping keys are dropped."""
    out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            if str(k).lower() in VOLATILE:
                continue
            out.update(flatten(v, "%s/%s" % (prefix, k)))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out.update(flatten(v, "%s[%d]" % (prefix, i)))
    else:
        out[prefix] = obj
    return out


def _same(a, b, tol=1e-9):
    if isinstance(a, bool) or isinstance(b, bool):
        return a is b or a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        if a == b:
            return True
        scale = max(1.0, abs(a), abs(b))
        return abs(a - b) <= tol * scale
    return a == b


def diff_faces(a, b, tol=1e-9, sample=6):
    """-> (n_changed, sample of changed paths). Compares flattened faces."""
    fa, fb = flatten(a), flatten(b)
    paths = sorted(set(fa) | set(fb))
    changed = [p for p in paths
               if p not in fa or p not in fb or not _same(fa[p], fb[p], tol)]
    return len(changed), changed[:sample]


def perturb(raw, names, date, factor=PERTURB_FACTOR):
    """Step `names` closes by `factor` from `date` on. Returns a new universe map.

    A step (not a single print) so a monthly book cannot average the change away and
    a rank-only read still sees a decisive move.
    """
    out = dict(raw)
    target = set(names)
    for sym in target:
        if sym not in raw:
            continue
        closes, amounts = raw[sym]
        new = {}
        for d, v in closes.items():
            new[d] = v * factor if (d >= date and v) else v
        out[sym] = (new, amounts)
    return out


def verdict_for(neutralise_changed, repaired_changed, ladder_changed):
    """Classify one mode from the three arm deltas (pure, selftest-tested)."""
    if neutralise_changed > 0:
        return "moves_under_repair", (
            "the repaired prints are charged: this face must be quoted with its screen arm")
    if repaired_changed > 0:
        return "reads_repaired_names_not_charged", (
            "repaired names enter the arithmetic, but neutralising their prints moves "
            "nothing on this face")
    if ladder_changed > 0:
        return "structurally_immune", (
            "price reads are ladder-local; the repaired names never enter the arithmetic")
    return "probe_blind", (
        "not even a 5% ladder step moves this face: it publishes no price arithmetic "
        "on the perturbed names and the immunity reading is unproven")


def read_set_label(neutralise_changed, repaired_changed, ladder_changed):
    """Name the read set from the three arm deltas (pure, selftest-tested).

    The 5-name step only proves a *name-level* read; the repair arm proves the face
    reads the wide book *in aggregate*. Report whichever channels actually moved,
    and never print "no price arithmetic" on a face the repair arm moves -- an
    aggregate-weighted book can absorb a 5% step on five names and still change.
    """
    if repaired_changed > 0 and ladder_changed > 0:
        return "wide per-name prices + ladder marks"
    if repaired_changed > 0:
        return "wide per-name prices"
    if ladder_changed > 0:
        if neutralise_changed > 0:
            return ("ladder marks only (wide book also enters through aggregates: "
                    "the repair arm moves it)")
        return "ladder marks only"
    if neutralise_changed > 0:
        return ("wide-book aggregates only: a 5-name step is blind, the repair arm "
                "moves it")
    return "no price arithmetic on the probed names"


def probe_units(rows, closed=CLOSED):
    """Exposed rows -> one probe per runner (default args), keeping every mode row."""
    units, by_runner = [], {}
    for r in rows:
        if r.get("status") != "exposed" or r.get("mode") in closed:
            continue
        runner = r.get("runner")
        if runner not in by_runner:
            unit = {"runner": runner, "modes": [], "faces": []}
            by_runner[runner] = unit
            units.append(unit)
        by_runner[runner]["modes"].append(r.get("mode"))
        if r.get("face_on_disk"):
            by_runner[runner]["faces"].append(r["face_on_disk"])
    return units


# ------------------------------------------------------------------ live probes

def _load_matrix(path=MATRIX):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _payloads(outdir):
    out = {}
    for name in sorted(os.listdir(outdir)):
        if not name.lower().endswith(".json"):
            continue
        try:
            with open(os.path.join(outdir, name), encoding="utf-8") as fh:
                out[name] = json.load(fh)
        except (OSError, ValueError) as ex:
            out[name] = {"_unreadable": str(ex)}
    return out


def _run_arm(runner_fn, raw, date, extra_perturb=(), factor=PERTURB_FACTOR):
    """Run one arm in a temp dir with e27.load_universe pinned to `raw`.

    The census runners *return* their face and ``main()`` writes it, so the probe
    reads the return value and never touches results/. A runner that writes into
    ``outdir`` itself is covered by the temp-dir scan fallback.
    """
    import e27_universe_expansion as e27
    saved = e27.load_universe
    tmp = tempfile.mkdtemp(prefix="e94_arm_")
    if extra_perturb:
        raw = perturb(raw, extra_perturb, date, factor)
    try:
        e27.load_universe = lambda *a, **k: raw
        ret = runner_fn(tmp)
    finally:
        e27.load_universe = saved
    try:
        if isinstance(ret, dict):
            return {"returned": ret}
        if isinstance(ret, list):
            return {"returned": {"rows": ret}}
        return _payloads(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def run(outdir=OUTDIR, matrix=MATRIX, log=print):
    import e24_ladder_weighting as base
    import e27_universe_expansion as e27
    import panel_screen
    import e39_panel_census as C

    t0 = time.time()
    raw = e27.load_universe()
    cal = base.load_panel()[0]
    repaired, report = panel_screen.screen_universe(raw, mode="neutralise", cal=cal)
    repaired_names = sorted(r["name"] for r in report["names"]
                            if r["action"] != "kept-gapped-only")
    screened, _rep_int = panel_screen.screen_universe(
        raw, mode="neutralise_int", cal=cal)
    int_names = sorted(r["name"] for r in _rep_int["names"]
                       if r["action"] != "kept-gapped-only")
    ladder = list(base.LADDER)
    ladder_rep = sorted(set(ladder) & set(repaired_names))
    date = cal[len(cal) // 2]
    probe_rep = repaired_names[:5]
    log("universe=%d repaired=%d integer-only=%d ladder∩repaired=%d midpoint=%s"
        % (len(raw), len(repaired_names), len(int_names), len(ladder_rep), date))

    mat = _load_matrix(matrix)
    rows = mat.get("legs", [])
    units = probe_units(rows)
    log("probe units=%d (exposed rows=%d)" % (
        len(units), sum(1 for r in rows if r.get("status") == "exposed")))

    probe = {}
    for unit in units:
        fn = getattr(C, unit["runner"], None)
        if fn is None:
            unit["error"] = "runner not found in census module"
            continue
        arms = {}
        arms["unscreened"] = _run_arm(fn, raw, date)
        arms["neutralise"] = _run_arm(fn, screened, date)
        arms["perturb_ladder"] = _run_arm(fn, raw, date, extra_perturb=ladder)
        arms["perturb_repaired"] = _run_arm(fn, raw, date, extra_perturb=probe_rep)
        n_neu, s_neu = 0, []
        n_lad, s_lad = 0, []
        n_rep, s_rep = 0, []
        for face in arms["unscreened"]:
            base_face = arms["unscreened"].get(face)
            for arm, (cnt, smp) in (
                    ("neutralise", (n_neu, s_neu)),
                    ("perturb_ladder", (n_lad, s_lad)),
                    ("perturb_repaired", (n_rep, s_rep))):
                other = arms[arm].get(face)
                if other is None:
                    continue
                c, s = diff_faces(base_face, other)
                if arm == "neutralise":
                    n_neu += c
                    s_neu.extend(s)
                elif arm == "perturb_ladder":
                    n_lad += c
                    s_lad.extend(s)
                else:
                    n_rep += c
                    s_rep.extend(s)
        probe[unit["runner"]] = {
            "faces": sorted(arms["unscreened"]),
            "neutralise_changed": n_neu,
            "perturb_ladder_changed": n_lad,
            "perturb_repaired_changed": n_rep,
            "samples": {"neutralise": s_neu[:6], "perturb_ladder": s_lad[:6],
                        "perturb_repaired": s_rep[:6]},
        }
        log("%-22s neu=%-5d ladder=%-5d repaired=%-5d faces=%d"
            % (unit["runner"], n_neu, n_lad, n_rep, len(arms["unscreened"])))

    out_rows = []
    for r in rows:
        if r.get("status") != "exposed":
            continue
        mode = r.get("mode")
        runner = r.get("runner")
        p = probe.get(runner)
        if mode in CLOSED:
            out_rows.append({
                "mode": mode, "runner": runner,
                "reads_loader": bool(r.get("reads_per_name_loader")),
                "read_set": "closed by the E81 screened twin `%s`" % CLOSED[mode],
                "intersects_repaired": None,
                "charged_by_repair": None,
                "verdict": "closed",
                "evidence": {"face_on_disk": r.get("face_on_disk")},
            })
            continue
        if not p:
            out_rows.append({
                "mode": mode, "runner": runner,
                "reads_loader": bool(r.get("reads_per_name_loader")),
                "read_set": "unprobed", "intersects_repaired": None,
                "charged_by_repair": None, "verdict": "probe_error",
                "evidence": {"face_on_disk": r.get("face_on_disk")},
            })
            continue
        verdict, note = verdict_for(p["neutralise_changed"],
                                    p["perturb_repaired_changed"],
                                    p["perturb_ladder_changed"])
        read_set = read_set_label(p["neutralise_changed"],
                                  p["perturb_repaired_changed"],
                                  p["perturb_ladder_changed"])
        out_rows.append({
            "mode": mode,
            "runner": runner,
            "reads_loader": bool(r.get("reads_per_name_loader")),
            "read_set": read_set,
            "intersects_repaired": bool(p["perturb_repaired_changed"] > 0),
            "charged_by_repair": bool(p["neutralise_changed"] > 0),
            "verdict": verdict,
            "note": note,
            "evidence": {
                "face_on_disk": r.get("face_on_disk"),
                "evidence_cutoff": r.get("evidence_cutoff"),
                "neutralise_changed": p["neutralise_changed"],
                "perturb_ladder_changed": p["perturb_ladder_changed"],
                "perturb_repaired_changed": p["perturb_repaired_changed"],
                "samples": p["samples"],
                "faces_probed": p["faces"],
            },
        })

    counts = {}
    for row in out_rows:
        counts[row["verdict"]] = counts.get(row["verdict"], 0) + 1
    face = {
        "study": "e94_exposure_readset_triage",
        "evidence_cutoff": cal[-1],
        "spec": {
            "arms": ["unscreened", "neutralise", "perturb_ladder", "perturb_repaired"],
            "screen_module": "scripts/panel_screen.py",
            "screen_mode": "neutralise",
            "perturb": {"names": 5, "step_pct": 100.0 * (PERTURB_FACTOR - 1.0),
                        "from": date, "kind": "step, not a single print"},
            "closed_modes": CLOSED,
            "loader_pin": "e27_universe_expansion.load_universe patched per arm; "
                          "every arm writes into a temp dir, published faces untouched",
            "comparison": "flattened JSON leaf paths, 1e-9 relative tolerance, "
                          "volatile keys dropped: %s" % sorted(VOLATILE),
        },
        "universe": {
            "names": len(raw),
            "repaired_neutralise": len(repaired_names),
            "repaired_integer_only": len(int_names),
            "repaired_sample": repaired_names[:10],
            "ladder_overlap": ladder_rep,
            "midpoint_session": date,
            "probe_names": probe_rep,
        },
        "rows": out_rows,
        "summary": {
            "rows": len(out_rows),
            "probe_units": len(units),
            "verdicts": counts,
            "charged_by_repair_modes": sorted(
                r["mode"] for r in out_rows if r.get("charged_by_repair")),
            "structurally_immune_modes": sorted(
                r["mode"] for r in out_rows if r["verdict"] == "structurally_immune"),
            "unproven_modes": sorted(
                r["mode"] for r in out_rows if r["verdict"] == "probe_blind"),
        },
        "honest": [
            "a 5% step on five names is a lower bound on sensitivity: a mode that "
            "averages over a wide book can absorb one name's move, so 'repaired' "
            "hits are detected more reliably than they are sized",
            "arm B repairs only the `neutralise` arm; `neutralise_int` (67 names, the "
            "conservative branch) is a subset, so a mode that is clean under B is "
            "clean under it too, but not vice versa",
            "no published face is regenerated and no ledger row is written: this is a "
            "triage of read sets, not a re-derivation of any level",
            "modes sharing one runner are probed once (default arguments); a published "
            "face produced with non-default arguments could still differ",
        ],
        "elapsed_sec": round(time.time() - t0, 1),
    }
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "triage-%s.json" % cal[-1].replace("-", ""))
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    log("wrote %s (%d rows, %.1fs)" % (
        os.path.relpath(path, ROOT).replace("\\", "/"), len(out_rows),
        face["elapsed_sec"]))
    return face, path


# ------------------------------------------------------------------ selftest

def selftest():
    ok = []

    def leg(name, want, got, extra=""):
        ok.append((name, want == got, want, got, extra))

    a = {"x": 1, "nested": {"v": 2.0, "list": [1, 2, 3]}, "generated": "t1"}
    b = {"x": 1, "nested": {"v": 2.0, "list": [1, 2, 3]}, "generated": "t2"}
    leg("L1 identical faces diff to zero (volatile keys dropped)", 0,
        diff_faces(a, b)[0])
    c = {"x": 1, "nested": {"v": 2.5, "list": [1, 2, 3]}, "generated": "t1"}
    n, sample = diff_faces(a, c)
    leg("L2 a numeric change is detected at its path", 1, n)
    leg("L3 the changed path is named", "/nested/v", sample[0])
    d = {"x": 1, "nested": {"v": 2.0, "list": [1, 2]}}
    leg("L4 a dropped list element counts as a change", True, diff_faces(a, d)[0] > 0)
    leg("L5 tolerance swallows float noise", 0,
        diff_faces({"v": 1.0}, {"v": 1.0 + 1e-12})[0])

    raw = {"a": ({"2020-01-01": 10.0, "2020-02-01": 10.0}, {}),
           "b": ({"2020-01-01": 5.0, "2020-02-01": 5.0}, {})}
    p = perturb(raw, ["a"], "2020-02-01", 1.05)
    leg("L6 perturb steps only from the given date", (10.0, 10.5),
        (p["a"][0]["2020-01-01"], p["a"][0]["2020-02-01"]))
    leg("L7 perturb leaves other names alone", 5.0, p["b"][0]["2020-02-01"])
    leg("L8 perturb does not mutate the input universe", 10.0,
        raw["a"][0]["2020-02-01"])

    leg("L9 verdict: repair charges the face", "moves_under_repair",
        verdict_for(3, 3, 2)[0])
    leg("L10 verdict: names read but not charged", "reads_repaired_names_not_charged",
        verdict_for(0, 4, 4)[0])
    leg("L11 verdict: structural immunity needs the ladder control",
        "structurally_immune", verdict_for(0, 0, 7)[0])
    leg("L12 verdict: no response to any arm is unproven, never immune",
        "probe_blind", verdict_for(0, 0, 0)[0])

    rows = [
        {"mode": "a", "runner": "run_x", "status": "exposed"},
        {"mode": "b", "runner": "run_x", "status": "exposed"},
        {"mode": "c", "runner": "run_y", "status": "exposed"},
        {"mode": "clean1", "runner": "run_z", "status": "clean"},
    ]
    units = probe_units(rows, closed={"c": "screen_c"})
    leg("L13 one probe per runner, closed modes skipped", 1, len(units))
    leg("L14 aliases keep both mode rows on one probe", ["a", "b"], units[0]["modes"])

    leg("L15 volatile key list is not empty", True, bool(VOLATILE))

    leg("L16 read set: both channels named when both move",
        "wide per-name prices + ladder marks", read_set_label(9, 3, 2))
    leg("L17 read set: a repair-only face is never called blind",
        "wide-book aggregates only: a 5-name step is blind, the repair arm moves it",
        read_set_label(20, 0, 0))
    leg("L18 read set: ladder-local face keeps its aggregate witness",
        "ladder marks only (wide book also enters through aggregates: the repair arm "
        "moves it)", read_set_label(4, 0, 3))
    leg("L19 read set: silence on every arm stays honest",
        "no price arithmetic on the probed names", read_set_label(0, 0, 0))

    passed = sum(1 for r in ok if r[1])
    for name, good, want, got, extra in ok:
        if not good:
            print("FAIL %s: want=%r got=%r %s" % (name, want, got, extra))
    print("selftest %d/%d" % (passed, len(ok)))
    return 0 if passed == len(ok) else 1


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "run":
        run()
    elif cmd == "selftest":
        return selftest()
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))