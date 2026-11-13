"""Re-derive the phase-atlas arm faces onto ONE world, and prove that they are.

WHY (r1179 bm-a): the arm faces are produced by separate 280-cell sweeps, hours or days
apart.  The arms audit (`etf_book_phase_atlas_arms.py`) compares their bands with each
other, and until r1179 no face could say which panel it had priced -- so a band measured
on one world could sit beside a band measured on another and read as a rule effect (E293).
The atlas now stamps `panel` on every face; this runner is the consumer of that stamp:

  * it rebuilds a group of arms, one atlas sweep per arm, using the ARM list and the
    DECLARED knob table of the audit itself (single source -- no second copy of the
    mapping), so an arm can never be rebuilt with a different knob than the one it is
    audited under;
  * it then asserts that every face it just wrote carries the SAME panel digest.  A
    group that leaves the family split across two worlds fails here instead of quietly
    producing a comparison the audit would have read as a result;
  * it finishes by running the audit's own `--check`, so "the arm set is coherent" is
    decided by the published criterion, not by this runner's opinion.

Groups (each is one pool unit; the three together put the whole family on one panel):
    buffer  = buffer_k02 .05 .10 .20 .40
    cost    = cost0 .05 .20 .40
    combo   = base (production toll) + buffer_k05_cost20

Usage:
    python scripts/etf_book_atlas_arms_rebuild.py run --only=buffer [--workers=8]
    python scripts/etf_book_atlas_arms_rebuild.py --selftest
"""

from __future__ import annotations

import io
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import etf_book_phase_atlas_arms as AUDIT  # arm list + declared knobs (single source)

GROUPS = {
    "buffer": ["buffer_k02", "buffer_k05", "buffer_k10", "buffer_k20", "buffer_k40"],
    "cost": ["cost0", "cost05", "cost20", "cost40"],
    "combo": ["base", "buffer_k05_cost20"],
    # one group = one world. A knob family rebuilt on its own leaves the FAMILY split across
    # two panels, and the arms audit (correctly) reports the older faces as stale -- so the
    # pool unit is the whole set, not a third of it. r1179 lost one burn to learning this.
    "all": ["base", "buffer_k02", "buffer_k05", "buffer_k10", "buffer_k20", "buffer_k40",
            "cost0", "cost05", "cost20", "cost40", "buffer_k05_cost20"],
}

BASE_FACE = AUDIT.BASE
RECEIPT = os.path.join(ROOT, "results", "etf_book_atlas_arms_rebuild.json")
ATLAS = os.path.join("scripts", "etf_book_phase_atlas.py")


def face_for(arm):
    """The repo-relative face path an arm writes (base = the production-toll face)."""
    if arm == "base":
        return BASE_FACE
    return AUDIT.ARMS[arm][0]


def command_for(arm, workers=None, out=None):
    """The atlas command line that produces `arm`, built from the audit's declared knob."""
    cmd = [sys.executable, ATLAS, "run"]
    if workers:
        cmd.append("--workers=%d" % int(workers))
    knob = AUDIT.DECLARED.get(arm) or {}
    if "buffer_k" in knob:
        cmd.append("--k=%g" % knob["buffer_k"])
    if "cost" in knob:
        cmd.append("--cost=%g" % knob["cost"])
    cmd.append("--out=%s" % (out or os.path.relpath(face_for(arm), ROOT)).replace("\\", "/"))
    return cmd


def digests(faces):
    """Read the panel digest of each face; a face without one is reported, never assumed.

    Returns {"stamped": {face: digest}, "unstamped": [...], "absent": [...]}.
    """
    stamped, unstamped, absent = {}, [], []
    for face in faces:
        path = face if os.path.isabs(face) else os.path.join(ROOT, face)
        if not os.path.exists(path):
            absent.append(face)
            continue
        try:
            with io.open(path, encoding="utf-8") as fh:
                payload = json.load(fh) or {}
        except Exception:
            absent.append(face)
            continue
        dig = (payload.get("panel") or {}).get("digest")
        if dig:
            stamped[face] = dig
        else:
            unstamped.append(face)
    return {"stamped": stamped, "unstamped": unstamped, "absent": absent}


def verdict(reading):
    """One sentence a reader can act on: are these faces one world or several?"""
    worlds = sorted(set(reading["stamped"].values()))
    if reading["absent"]:
        return "INCOMPLETE", "%d face(s) absent" % len(reading["absent"])
    if reading["unstamped"]:
        return "UNSTAMPED", "%d face(s) predate the panel stamp" % len(reading["unstamped"])
    if len(worlds) > 1:
        return "SPLIT_WORLDS", "%d faces, %d panels" % (len(reading["stamped"]), len(worlds))
    if not worlds:
        return "EMPTY", "no faces to compare"
    return "ONE_WORLD", "all %d faces priced %s" % (len(reading["stamped"]), worlds[0])


AUDIT_SCRIPT = os.path.join(ROOT, "scripts", "etf_book_phase_atlas_arms.py")


def audit_steps(group):
    """Which audit runs this unit must do afterwards.

    r1181: proving the faces are one world is only half the job -- the arms face
    that HOLDS the per-cell verdicts is a separate artifact built FROM those
    source faces. Rebuilding eleven faces on one panel and only `--check`-ing
    left the published comparison on the old world: the check honestly answered
    "face is stale ... cutoff 2026-10-29" while the family had already been made
    uniform (2026-10-31 live: receipt verdict ONE_WORLD / audit_check_rc 2, and
    the ten withheld labels stayed withheld). A partial group only checks (it is
    genuinely stale by design); the `all` group must republish and then check.
    """
    if group == "all":
        return [[], ["--check"]]
    return [["--check"]]


def success(group, kind, publish_rc, check_rc):
    """r1181: the family unit is done only when the reader's face is rebuilt."""
    if kind != "ONE_WORLD":
        return False
    if group == "all":
        return publish_rc == 0 and check_rc == 0
    return True


def run(group, workers=None):
    arms = GROUPS[group]
    written = []
    for arm in arms:
        cmd = command_for(arm, workers=workers)
        print("[rebuild] %s -> %s" % (arm, cmd[-1]), flush=True)
        rc = subprocess.call(cmd, cwd=ROOT)
        print("[rebuild] %s rc=%d" % (arm, rc), flush=True)
        written.append(os.path.relpath(face_for(arm), ROOT).replace("\\", "/"))
    reading = digests(written)
    kind, detail = verdict(reading)
    publish_rc, audit_rc = None, None
    for step in audit_steps(group):
        label = " ".join(step) or "(publish)"
        print("[rebuild] audit %s" % label, flush=True)
        rc = subprocess.call([sys.executable, AUDIT_SCRIPT] + step, cwd=ROOT)
        print("[rebuild] audit %s rc=%d" % (label, rc), flush=True)
        if step == []:
            publish_rc = rc
        else:
            audit_rc = rc
    ok = success(group, kind, publish_rc, audit_rc)
    out = {"group": group, "arms": arms, "faces": written, "panel": reading,
           "verdict": kind, "detail": detail,
           "audit_publish_rc": publish_rc, "audit_check_rc": audit_rc,
           "audit_steps": [" ".join(s) or "(publish)" for s in audit_steps(group)],
           "success": ok,
           "stamp_law": "every face in a rebuilt group must price one panel (r1179)",
           "publish_law": ("the `all` unit also republishes the arms face and then "
                           "checks it (r1181): a rebuilt family behind a stale "
                           "comparison face is still unread")}
    with io.open(RECEIPT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print("[rebuild] %s: %s (%s); publish rc=%s check rc=%s -> %s"
          % (group, kind, detail, publish_rc, audit_rc,
             "OK" if ok else "NOT DONE"), flush=True)
    # a partial rebuild of the family is honestly "stale", and making that fatal
    # would fail every unit except the last one. The `all` group has nothing
    # behind it: it must leave a reader-usable, checked arms face (r1181).
    return 0 if ok else 2


SPANNING = os.path.join(ROOT, "results", "etf_book_spanning.json")
NEEDS_REBUILD = ("missing", "behind", "content", "unstamped")


def _face_stamp(path):
    """(bar, digest) a face says it was priced on; (None, None) when unreadable.

    Read off the face's own `panel` block -- the block r1179 added so that a band
    measured on one world could not sit beside a band measured on another.
    """
    p = path if os.path.isabs(path) else os.path.join(ROOT, path)
    if not os.path.exists(p):
        return None, None
    try:
        with io.open(p, encoding="utf-8") as fh:
            panel = (json.load(fh) or {}).get("panel") or {}
    except Exception:
        return None, None
    bar = str(panel.get("last") or "")[:10] or None
    return bar, (panel.get("digest") or None)


def world_bar(path=SPANNING):
    """The bar this family must be priced on, read off the panel's own publisher.

    r1631: `etf_book_spanning` loads the identical panel and publishes its last
    bar, which is what r1630 used for the pre-2020 face -- never a clock and never
    a file mtime (r1371: a gate that measures the filesystem measures the wrong
    thing). A missing publisher is not evidence of freshness, so the fallback is
    the NEWEST bar among the family's own faces, and the reading says which source
    it used instead of assuming the family is current.
    """
    p = path if os.path.isabs(path) else os.path.join(ROOT, path)
    try:
        with io.open(p, encoding="utf-8") as fh:
            bar = ((json.load(fh) or {}).get("panel") or {}).get("last_bar")
        if bar:
            return str(bar)[:10], "spanning"
    except Exception:
        pass
    return None, "faces(newest)"


def _display(face):
    """Repo-relative when it can be, absolute otherwise.

    r1631: `os.path.relpath` raises ValueError across drives, and this file's own
    selftest builds fixtures under %TEMP% (C:) while the repo lives on K: -- the
    same cross-drive crash that has now bitten four published tools (r1371/r1375/
    r1594). A display path must never be able to abort a run.
    """
    try:
        return os.path.relpath(face, ROOT).replace("\\", "/")
    except ValueError:
        return face


def family_state(world=None, faces=None, source=None):
    """One row per arm: which world it was priced on, and whether that is this one.

    The question is cheap on purpose -- bar identity plus the published digest --
    because the repair it gates costs ~200s per arm. A digest disagreement at the
    SAME bar is named `content` (a panel repaired in place) and is still repaired;
    a face ahead of the world is `ahead` and must not be rebuilt (rebuilding it
    would publish older numbers under a newer file name, r1630).
    """
    if faces is None:
        faces = [face_for(a) for a in GROUPS["all"]]
    if world is None:
        world, source = world_bar()
    stamps = [_face_stamp(f) for f in faces]
    if not world:
        bars = [b for b, _d in stamps if b]
        world = max(bars) if bars else None
        source = source or "faces(newest)"
    digs = [d for (b, d) in stamps if world and b == world and d]
    modal = max(sorted(set(digs)), key=digs.count) if digs else None
    rows = []
    for arm, face, (bar, dig) in zip(GROUPS["all"], faces, stamps):
        if not bar:
            status = "missing"
        elif world and bar < world:
            status = "behind"
        elif world and bar > world:
            status = "ahead"
        elif modal and dig and dig != modal:
            status = "content"
        elif modal and not dig:
            status = "unstamped"
        else:
            status = "ok"
        rows.append({"arm": arm, "face": _display(face),
                     "bar": bar, "digest": dig, "status": status})
    return {"world": world, "world_source": source or "spanning", "modal": modal, "rows": rows}


def check_world(faces=None, world=None):
    """Is the whole family priced on one world? Red, with names, when it is not.

    r1631 live: the atlas `--check` re-derives its own 280 rows and the arms
    `--check` re-derives its own labels, so after r1630 moved five cost arms to
    2026-11-12 the two faces still printed CHECK OK while the comparison between
    them said MIXED_WORLDS -- a withheld verdict that no leg could lift (r1471:
    a reader leg going green proves nothing about a writer existing).
    """
    st = family_state(world=world, faces=faces)
    stale = [r for r in st["rows"] if r["status"] in NEEDS_REBUILD]
    ahead = [r for r in st["rows"] if r["status"] == "ahead"]
    if stale:
        print("stale: %d of %d arm faces are not on world %s (bar %s) -- %s"
              % (len(stale), len(st["rows"]), st["modal"] or "-", st["world"],
                 ", ".join("%s@%s/%s" % (r["arm"], r["bar"] or "-", r["status"]) for r in stale)))
        if ahead:
            print("  ahead of the world, not rebuilt: %s"
                  % ", ".join("%s@%s" % (r["arm"], r["bar"]) for r in ahead))
        return 2
    if ahead:
        print("stale: the publisher etf_book_spanning is behind the family (its bar %s) -- "
              "a rebuild would publish older numbers under newer names" % st["world"])
        return 2
    print("CHECK OK: %d arm faces priced one world %s (bar %s, %s)"
          % (len(st["rows"]), st["modal"] or "unstamped", st["world"], st["world_source"]))
    return 0


def refresh(budget=620.0, workers=None, faces=None, run_one=None, audit_run=None, world=None):
    """Re-price only the arms that are not on the current world, within a budget.

    One atlas sweep is ~200s (280 cells, one process pool per arm) and the chain
    leg that pays this has a 900s timeout, so the gate rebuilds what fits, then
    republishes the arms face and re-checks; whatever is left stays named and red
    for the next run. A family already on the world costs 0.0s and rebuilds
    nothing (that is the whole point of asking the world question first).
    """
    t0 = time.time()
    st = family_state(world=world, faces=faces)
    todo = [r for r in st["rows"] if r["status"] in NEEDS_REBUILD]
    ahead = [r for r in st["rows"] if r["status"] == "ahead"]
    call = run_one or (lambda c: subprocess.call(c, cwd=ROOT))
    done, left = [], []
    for i, r in enumerate(todo):
        if done and (time.time() - t0) > budget:
            left.extend(x["arm"] for x in todo[i:])
            break
        cmd = command_for(r["arm"], workers=workers)
        print("[refresh] %s (%s@%s) -> %s" % (r["arm"], r["status"], r["bar"] or "-", cmd[-1]),
              flush=True)
        try:
            rc = call(cmd)
        except Exception as exc:      # a failed sweep is reported, never crashed past
            print("[refresh] %s raised %r" % (r["arm"], exc), flush=True)
            rc = 1
        print("[refresh] %s rc=%s" % (r["arm"], rc), flush=True)
        (done if rc == 0 else left).append(r["arm"])
    publish_rc = check_rc = None
    acall = audit_run or (lambda a: subprocess.call(a, cwd=ROOT))
    if done:
        print("[refresh] audit publish", flush=True)
        publish_rc = acall([sys.executable, AUDIT_SCRIPT])
        print("[refresh] audit --check", flush=True)
        check_rc = acall([sys.executable, AUDIT_SCRIPT, "--check"])
    after = family_state(world=world, faces=faces)
    remaining = [r["arm"] for r in after["rows"] if r["status"] in NEEDS_REBUILD]
    if not todo:
        status = "UPSTREAM_BEHIND" if ahead else "REFRESH_NOOP"
    elif remaining:
        status = "PARTIAL"
    else:
        status = "REBUILT"
    out = {"mode": "refresh", "status": status, "world": st["world"],
           "world_source": st["world_source"], "modal": st["modal"],
           "rebuilt": done, "left": left or remaining, "ahead": [r["arm"] for r in ahead],
           "audit_publish_rc": publish_rc, "audit_check_rc": check_rc,
           "elapsed_sec": round(time.time() - t0, 1)}
    print(json.dumps(out, ensure_ascii=False), flush=True)
    if status == "REFRESH_NOOP":
        return 0
    if status == "REBUILT":
        return 0 if check_rc == 0 else 2
    return 2


def selftest():
    bad = []
    # `all` is the pool unit (one family, one world); the knob groups are the parts it covers.
    knob_groups = {g: arms for g, arms in GROUPS.items() if g != "all"}
    seen = {}
    for group, arms in knob_groups.items():
        for arm in arms:
            if arm != "base" and arm not in AUDIT.ARMS:
                bad.append("%s/%s is not an arm the audit knows" % (group, arm))
            seen[arm] = seen.get(arm, 0) + 1
    for arm, n in seen.items():
        if n != 1:
            bad.append("%s appears in %d knob groups" % (arm, n))
    covered = set()
    for arms in knob_groups.values():
        covered.update(arms)
    if set(GROUPS["all"]) != covered:
        bad.append("the all group is not exactly the union of the knob groups")
    for arm in AUDIT.ARMS:
        if arm not in GROUPS["all"]:
            bad.append("%s is audited but no rebuild covers it" % arm)
    # the knob in the command line is the knob the audit declares
    for arm in ("buffer_k05", "cost20", "buffer_k05_cost20", "cost0"):
        cmd = " ".join(command_for(arm))
        for key, val in (AUDIT.DECLARED.get(arm) or {}).items():
            flag = "--k=%g" % val if key == "buffer_k" else "--cost=%g" % val
            if flag not in cmd:
                bad.append("%s does not pass %s" % (arm, flag))
    if "--k=" in " ".join(command_for("cost20")):
        bad.append("a cost arm must not set the buffer knob")
    # a mixed family is SPLIT_WORLDS, a uniform one is ONE_WORLD, an unstamped face is named
    split = {"stamped": {"a": "1111222233334444", "b": "5555666677778888"},
             "unstamped": [], "absent": []}
    same = {"stamped": {"a": "1111222233334444", "b": "1111222233334444"},
            "unstamped": [], "absent": []}
    old = {"stamped": {"a": "1111222233334444"}, "unstamped": ["c"], "absent": []}
    miss = {"stamped": {}, "unstamped": [], "absent": ["d"]}
    if verdict(split)[0] != "SPLIT_WORLDS":
        bad.append("two panels in one family is not reported as split")
    if verdict(same)[0] != "ONE_WORLD":
        bad.append("a uniform family is not reported as one world")
    if verdict(old)[0] != "UNSTAMPED":
        bad.append("a face without a stamp is silently accepted")
    if verdict(miss)[0] != "INCOMPLETE":
        bad.append("an absent face is not reported as incomplete")
    # an absent face is never invented as stamped
    if digests(["results/__no_such_face__.json"])["stamped"]:
        bad.append("a missing file was read as a stamped face")
    # r1181: the family unit must republish the reader's face, then check it;
    # a partial unit only checks (it is stale by design).
    if audit_steps("all") != [[], ["--check"]]:
        bad.append("the all group does not republish the arms face before checking")
    if audit_steps("buffer") != [["--check"]]:
        bad.append("a partial group must not republish the family face")
    if not success("all", "ONE_WORLD", 0, 0):
        bad.append("a republished + checked family does not count as done")
    if success("all", "ONE_WORLD", 0, 2):
        bad.append("a stale arms face still counts as done")
    if success("all", "ONE_WORLD", 2, 0):
        bad.append("a failed publish still counts as done")
    if not success("buffer", "ONE_WORLD", None, 2):
        bad.append("a partial group is judged by its own coherence, not the family's")
    if success("all", "SPLIT_WORLDS", 0, 0):
        bad.append("a split family counts as done")
    # r1631: the world gate. The two existing checks re-derive only their own numbers, so
    # they were green while the family sat on two panels; this gate asks the world question
    # and names what it cannot fix (a face ahead of its own publisher).
    import tempfile
    td = tempfile.mkdtemp(prefix="atlasworld")
    names = GROUPS["all"]

    def _mk(name, bar, dig):
        p = os.path.join(td, name)
        with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps({"panel": {"last": bar, "digest": dig}}))
        return p

    old, new = "2026-11-06", "2026-11-12"
    mix = [_mk("m%d.json" % i, old if i < 6 else new, "aaaa1111bbbb2222" if i < 6 else "cccc3333dddd4444")
           for i in range(len(names))]
    st = family_state(world=new, faces=mix)
    if [r["status"] for r in st["rows"]].count("behind") != 6:
        bad.append("six faces on an older bar are not reported behind")
    if st["modal"] != "cccc3333dddd4444":
        bad.append("the world digest is not the one the faces on that bar agree on")
    if check_world(faces=mix, world=new) == 0:
        bad.append("a family split across two panels passes the world check")
    uni = [_mk("u%d.json" % i, new, "cccc3333dddd4444") for i in range(len(names))]
    if any(r["status"] != "ok" for r in family_state(world=new, faces=uni)["rows"]):
        bad.append("a face on the world bar is not read as current")
    if check_world(faces=uni, world=new) != 0:
        bad.append("a one-world family fails the world check")
    cont = list(uni)
    cont[3] = _mk("c.json", new, "eeee5555ffff6666")
    if family_state(world=new, faces=cont)["rows"][3]["status"] != "content":
        bad.append("same bar with a different digest is not named a content mismatch")
    ah = list(uni)
    ah[0] = _mk("a.json", "2026-11-13", "cccc3333dddd4444")
    if family_state(world=new, faces=ah)["rows"][0]["status"] != "ahead":
        bad.append("a face ahead of the publisher is not named ahead")
    if check_world(faces=ah, world=new) == 0:
        bad.append("a publisher behind the family is not red")
    # a family already on the world costs nothing: the gate's whole point
    sweeps = []
    if refresh(faces=uni, world=new, run_one=lambda c: sweeps.append(c) or 0,
               audit_run=lambda a: sweeps.append(a) or 0) != 0 or sweeps:
        bad.append("a one-world family paid for a sweep")
    # and a budget that cannot fit the whole family returns PARTIAL instead of overrunning
    left = refresh(budget=0, faces=mix, run_one=lambda c: 0, audit_run=lambda a: 0)
    if left != 2:
        bad.append("an unfinished family is not red")
    n_legs = 16 + 8  # 9 pre-r1181 + 7 publish-contract + the 8 world-gate legs above
    for b in bad:
        print("[FAIL] %s" % b)
    print("selftest: %d legs, %d failed" % (n_legs, len(bad)))
    return 0 if not bad else 1


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if "--check-world" in argv:
        return check_world()
    group = "buffer"
    workers = None
    budget = 620.0
    do_refresh = "refresh" in argv
    for a in argv:
        if a.startswith("--only="):
            group = a.split("=", 1)[1]
        elif a.startswith("--workers="):
            workers = int(a.split("=", 1)[1])
        elif a.startswith("--budget="):
            budget = float(a.split("=", 1)[1])
    if do_refresh:
        return refresh(budget=budget, workers=workers)
    if group not in GROUPS:
        print("unknown group %r; one of %s" % (group, ",".join(GROUPS)))
        return 2
    return run(group, workers=workers)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))