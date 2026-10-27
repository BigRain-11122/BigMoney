"""E109 -- screened-consumer sweep after the E108 repair-factor fix.

E108 patched ``panel_screen.split_events`` so the forward-adjustment factor is
the cancelling ``1/(1+r)`` on **every** split event, then re-derived the seven
gap-arm legs (midlevels / gaparmendgrid / gaparmfamily / gaplimit / gaptop3 /
heldsplit / repairstep). Every other census leg that joins a ``neutralise`` or
``neutralise_int`` arm still carries the old folded-ratio factor on its upward
prints, and nothing in the repo says which of them was actually affected.

This tool answers that by burning each remaining leg **twice on today's panel**:
once with the old factor restored (the legacy arm) and once with the fixed code
(the shipped arm). The panel is held constant, so the diff between the two arms
is the factor and nothing else -- the same discipline E108 used for its control,
applied as the primary measurement instead of a sanity check.

Usage:
    python scripts/e109_repairsweep.py sweep [--publish]
    python scripts/e109_repairsweep.py burn <leg> <legacy|fixed>   (internal)
    python scripts/e109_repairsweep.py selftest

``--publish`` also copies the fixed-arm faces back into their normal results/
directories under the today's-cutoff filename, so the repo carries the corrected
numbers rather than only the diff.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

# legs whose published numbers come off a neutralise / neutralise_int arm and
# were NOT re-derived by E108 (ticket target list, r1172)
LEGS = ["midscreen", "churngap", "robustchurn", "churnse", "singleprint",
        "topnames", "loodist", "screenspread", "screentilt", "screenwide",
        "screenweek", "screenreg", "gapsplit", "burncontrol"]

# every results/ subdir any of those legs writes into
DIRS = ["e44_midmonth", "e42_spread_size_neutral", "e42_tilt_era",
        "e43_neutral_robust"]

OUT_FACE = lambda cutoff: os.path.join(ROOT, "results", "e44_midmonth",
                                       "REPAIRSWEEP-%s.json"
                                       % cutoff.replace("-", ""))


def _sha1(path):
    h = hashlib.sha1()
    with io.open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def snapshot():
    """{relative-path-under-results: sha1} for every json in the swept dirs."""
    snap = {}
    for d in DIRS:
        base = os.path.join(ROOT, "results", d)
        if not os.path.isdir(base):
            continue
        for name in sorted(os.listdir(base)):
            if not name.endswith(".json"):
                continue
            p = os.path.join(base, name)
            snap["%s/%s" % (d, name)] = _sha1(p)
    return snap


def harvest(before, arm_dir, publish=False):
    """Move every new-or-changed face into ``arm_dir``; return their rel paths.

    Moving rather than copying is what lets the second arm write the same
    filename freshly instead of reading the first arm's output back off disk.
    """
    os.makedirs(arm_dir, exist_ok=True)
    after = snapshot()
    touched = sorted(k for k, v in after.items() if before.get(k) != v)
    for rel in touched:
        src = os.path.join(ROOT, "results", rel.replace("/", os.sep))
        flat = rel.replace("/", "__")
        dst = os.path.join(arm_dir, flat)
        shutil.move(src, dst)
        if publish:
            shutil.copy2(dst, src)
    return touched


def _driver(leg, arm):
    """One burn in a fresh interpreter so the monkeypatch cannot leak arms."""
    if arm == "legacy":
        code = ("import sys;sys.path.insert(0, r'%s');"
                "import e108_repairfix as e;"
                "sys.exit(e.run_leg('%s', legacy=True))"
                % (os.path.join(ROOT, "scripts"), leg))
    else:
        code = ("import sys;sys.path.insert(0, r'%s');"
                "import e39_panel_census as e;"
                "sys.exit(e.main(['%s']))"
                % (os.path.join(ROOT, "scripts"), leg))
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    r = subprocess.run([sys.executable, "-c", code], cwd=ROOT, env=env,
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=3600)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def _rank_key(row):
    return -(row.get("numbers_carried") or 0)


def sweep(publish=False, legs=None):
    import e108_repairfix as fx
    legs = legs or LEGS
    work = tempfile.mkdtemp(prefix="e109_sweep_")
    rows = []
    try:
        for leg in legs:
            legacy_dir = os.path.join(work, leg, "legacy")
            fixed_dir = os.path.join(work, leg, "fixed")
            # snapshot per arm: the arm's own output is moved out before the
            # next arm starts, so a leftover face from an earlier session can
            # never mask the burn (a single pre-loop snapshot did exactly that
            # to churngap, whose fixed face was already on disk from a trial)
            print("burn %s legacy ..." % leg, flush=True)
            snap = snapshot()
            rc_l, out_l = _driver(leg, "legacy")
            touched_l = harvest(snap, legacy_dir)
            print("burn %s legacy rc=%s faces=%d | fixed ..."
                  % (leg, rc_l, len(touched_l)), flush=True)
            snap = snapshot()
            rc_f, out_f = _driver(leg, "fixed")
            touched_f = harvest(snap, fixed_dir, publish=publish)
            faces = fx.diff_faces(legacy_dir, fixed_dir) if touched_f else []
            print("burn %s done fixed rc=%s faces=%d" % (leg, rc_f, len(touched_f)),
                  flush=True)
            carried = sum(int(f.get("numeric_leaves") or 0) for f in faces)
            moved = sum(int(f.get("numeric_moved") or 0) for f in faces)
            rows.append({
                "leg": leg,
                "rc_legacy": rc_l,
                "rc_fixed": rc_f,
                "faces_written_legacy": touched_l,
                "faces_written_fixed": touched_f,
                "numbers_carried": carried,
                "numbers_moved": moved,
                "leg_verdict": ("no_face" if not touched_f else
                                "factor_moved" if moved else "bit_identical"),
                "faces": faces,
                "stdout_tail": (out_f.strip().splitlines()[-2:]
                                if out_f.strip() else []),
            })
    finally:
        shutil.rmtree(work, ignore_errors=True)
    rows.sort(key=_rank_key)
    cutoff = None
    for r in rows:
        for f in r["faces_written_fixed"]:
            for tok in f.split("__")[-1].replace(".json", "").split("-"):
                if len(tok) == 8 and tok.isdigit():
                    cutoff = "%s-%s-%s" % (tok[:4], tok[4:6], tok[6:])
        if cutoff:
            break
    # a partial batch must not erase legs burned in an earlier batch: merge by
    # leg name against whatever the face on disk already carries
    merged = list(rows)
    try:
        prev = json.load(io.open(OUT_FACE(cutoff or "2026-10-26"), encoding="utf-8"))
        done = {r["leg"] for r in rows}
        merged += [r for r in (prev.get("rows") or []) if r.get("leg") not in done]
        merged.sort(key=_rank_key)
    except Exception:
        pass
    payload = {
        "tool": "scripts/e109_repairsweep.py",
        "study": "E109 screened-consumer sweep: every remaining leg that joins a "
                 "neutralise/neutralise_int arm, burned with the old folded-ratio "
                 "factor (legacy arm) and the E108 cancelling factor (shipped arm) "
                 "on the SAME panel, so the delta is the factor and not panel drift",
        "evidence_cutoff": cutoff or "2026-10-26",
        "panel": "data/daily core48 + data/astock_daily/per, panel held constant "
                 "between the two arms of every leg",
        "legs": [r["leg"] for r in merged],
        "rows": merged,
        "ranking": [{"leg": r["leg"],
                     "numbers_carried": r["numbers_carried"],
                     "numbers_moved": r["numbers_moved"],
                     "leg_verdict": r["leg_verdict"]} for r in merged],
        "totals": {
            "legs_burned": len(merged),
            "legs_moved": sum(1 for r in merged if r["numbers_moved"]),
            "numbers_carried": sum(r["numbers_carried"] for r in merged),
            "numbers_moved": sum(r["numbers_moved"] for r in merged),
            "legs_with_no_face": [r["leg"] for r in merged
                                  if r["leg_verdict"] == "no_face"],
        },
        "law_ref": "DIGEST-20261027-e108-repair-factor-sign.md remaining scope; "
                   "E108 control discipline (legacy arm) as the primary measurement",
    }
    return payload


def selftest():
    global ROOT, DIRS
    ok = 0
    assert len(LEGS) == len(set(LEGS)) == 14, "leg list must be the 14 unique legs"
    assert "e44_midmonth" in DIRS and len(DIRS) == 4
    ok += 1
    # harvest: move-not-copy, and a same-name second arm must not see the first
    with tempfile.TemporaryDirectory() as td:
        d = os.path.join(td, "results", "e44_midmonth")
        os.makedirs(d)
        p = os.path.join(d, "FACE-20260101.json")
        io.open(p, "w", encoding="utf-8", newline="\n").write('{"a": 1}')
        _r, _d = ROOT, DIRS
        ROOT, DIRS = td, ["e44_midmonth"]
        try:
            base = snapshot()
            assert base == {"e44_midmonth/FACE-20260101.json": _sha1(p)}, base
            # unchanged face is not harvested
            arm = os.path.join(td, "arm0")
            assert harvest(base, arm) == [] and os.path.exists(p)
            # a rewrite is harvested (moved out) and flagged
            io.open(p, "w", encoding="utf-8", newline="\n").write('{"a": 2}')
            arm1 = os.path.join(td, "arm1")
            touched = harvest(base, arm1)
            assert touched == ["e44_midmonth/FACE-20260101.json"], touched
            assert not os.path.exists(p), "harvest must MOVE the face out"
            assert os.path.exists(os.path.join(arm1, "e44_midmonth__FACE-20260101.json"))
            # the second arm can now write the same filename cleanly
            io.open(p, "w", encoding="utf-8", newline="\n").write('{"a": 3}')
            arm2 = os.path.join(td, "arm2")
            assert harvest(base, arm2) == ["e44_midmonth/FACE-20260101.json"]
            # publish puts the arm copy back where consumers look for it
            io.open(p, "w", encoding="utf-8", newline="\n").write('{"a": 3}')
            base2 = snapshot()
            io.open(p, "w", encoding="utf-8", newline="\n").write('{"a": 4}')
            harvest(base2, os.path.join(td, "arm3"), publish=True)
            assert json.load(io.open(p, encoding="utf-8")) == {"a": 4}, "publish"
        finally:
            ROOT, DIRS = _r, _d
    ok += 1
    # ranking is by numbers carried, descending (the ticket's ordering rule)
    rows = [{"leg": "b", "numbers_carried": 3}, {"leg": "a", "numbers_carried": 9}]
    rows.sort(key=_rank_key)
    assert [r["leg"] for r in rows] == ["a", "b"]
    ok += 1
    print("e109 selftest: %d/%d PASS" % (ok, 3))
    return 0


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    if argv[0] == "selftest":
        return selftest()
    if argv[0] == "burn":
        rc, out = _driver(argv[1], argv[2])
        print(out[-4000:])
        return rc
    if argv[0] == "sweep":
        publish = "--publish" in argv
        legs = None
        if "--legs" in argv:
            legs = argv[argv.index("--legs") + 1].split(",")
        payload = sweep(publish=publish, legs=legs)
        txt = json.dumps(payload, ensure_ascii=False, indent=1)
        p = OUT_FACE(payload["evidence_cutoff"])
        with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(txt + "\n")
        print(json.dumps({"face": os.path.relpath(p, ROOT),
                          "ranking": payload["ranking"],
                          "totals": payload["totals"]}, ensure_ascii=False))
        return 0
    print("unknown command %r" % argv[0])
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))