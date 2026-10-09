# -*- coding: utf-8 -*-
"""Tools/qa_rotation_probe.py -- T12: QA charter evidence rolling-window
rotation probe (state/queue/tech.md T12; TREASURE_PROTECTION_LAW s2 chain).

Surfaces (qa/ per-round evidence packs from scripts/qa_smoke_run.py):
  qa/smoke-r<N>[-<machine>].md          tracked, checklist evidence
  qa/equity-curve-r<N>[-<machine>].png  tracked, chart evidence
  qa/smoke-r<N>[-<machine>].log         gitignored (*.log), raw receipts
Named one-off deliverable evidence (mass-trial-report-*, trading-calendar-*
...) = keep-forever class, never in any rotation set.

Policy layers (each one is a hard gate, fail-closed):
  1. D-20261009-02 zero-rename law: untagged legacy pre-suffix packs are
     FROZEN -- never renamed, never rotated, report-only bucket.
  2. Rolling window per machine bucket: keep the newest K rounds (default
     30) per bucket; older churn-class files = rotation candidates.
  3. treasure_guard prescan (s2.1): registry hit over the candidate set =
     HARD REJECT exit 3, zero rotation.
  4. git_claw ownership face (D-20261002-04): tracked churn blobs are
     md prose / png binary -- they never carry JSON owner evidence, so a
     push deleting them is claw-blocked for every machine. Rotation of
     tracked candidates therefore requires the C-20261007-04 adjudication
     pattern (fleet-authorized rotation + --no-verify escape + receipt,
     r703 bm-c precedent): --rotate --adjudicated <case-ref>.
     Untracked (.log) candidates are local-disk class: plain --rotate.

Default run = read-only report -> results/qa_rotation_probe.json; no file
is moved. --rotate executes via the treasure_guard quarantine CLI (s2.2
legal deletion path, 7-day observation window) + manifest assert.

CLI (repo root):
  python Tools/qa_rotation_probe.py                 read-only report
  python Tools/qa_rotation_probe.py --window N      keep newest N rounds/bucket
  python Tools/qa_rotation_probe.py --rotate         rotate untracked candidates only
  python Tools/qa_rotation_probe.py --rotate --adjudicated C-XXXX-XX
                                                    also rotate tracked candidates
  python Tools/qa_rotation_probe.py selftest         hermetic (tempdir only)

Exit codes: 0 report/rotation done, 3 hard refuse (prescan hit / tracked
without adjudication / empty candidate set on --rotate), 2 mechanism fault.
"""
import argparse
import datetime
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
QA_DIR = os.path.join(ROOT, "qa")
REPORT = os.path.join(ROOT, "results", "qa_rotation_probe.json")
RECEIPT = os.path.join(ROOT, "results", "qa_rotation_receipt.json")

RX_ROUND = re.compile(
    r"^(smoke|equity-curve)-r(\d+)(?:-(bm-[abc]))?\.(md|png|log)$")
NO_WINDOW = 0x08000000 if os.name == "nt" else 0  # CREATE_NO_WINDOW (U060)

LEGACY = "legacy-untagged(D-20261009-02-frozen)"


def now_iso():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def _git_tracked(rel_dir):
    """Tracked path set under rel_dir (zero-window git, r317 discipline)."""
    r = subprocess.run(["git", "-C", ROOT, "ls-files", rel_dir],
                       capture_output=True, creationflags=NO_WINDOW)
    if r.returncode != 0:
        raise RuntimeError("git ls-files rc=%d" % r.returncode)
    return set(l.decode("utf-8", "replace").strip().replace("\\", "/")
               for l in r.stdout.splitlines() if l.strip())


def classify_qa_dir(qa_dir):
    """Split qa/ files into churn round entries and named keep-forever set.

    Returns (entries, named) where entries = [dict(kind, round_no, machine,
    fname)] and named = sorted filename list (never rotatable).
    """
    entries, named = [], []
    for fname in sorted(os.listdir(qa_dir)):
        if not os.path.isfile(os.path.join(qa_dir, fname)):
            continue
        m = RX_ROUND.match(fname)
        if m:
            entries.append({
                "kind": m.group(1),            # smoke | equity-curve
                "round_no": int(m.group(2)),
                "machine": m.group(3) or None,  # bm-a/bm-b/bm-c or legacy
                "fname": fname,
            })
        else:
            named.append(fname)
    return entries, named


def rotation_plan(entries, window, tracked):
    """Per-bucket rolling-window plan. Buckets: per machine suffix + legacy
    frozen bucket (D-20261009-02 zero-rename law = never rotatable)."""
    buckets = {}
    for e in entries:
        buckets.setdefault(e["machine"] or LEGACY, []).append(e)
    plan = {}
    for key, items in buckets.items():
        rounds = sorted({e["round_no"] for e in items})
        cutoff = rounds[-window] if len(rounds) >= window else rounds[0]
        rot = [e for e in items if e["round_no"] < cutoff]
        keep = [e for e in items if e["round_no"] >= cutoff]
        if key == LEGACY:
            # frozen law: legacy packs stay as-is, zero rename
            rot, keep = [], items
        rot_rel = ["qa/" + e["fname"] for e in rot]
        plan[key] = {
            "files_total": len(items),
            "round_min": rounds[0],
            "round_max": rounds[-1],
            "window_keep": len(keep),
            "rotate_tracked": sorted(p for p in rot_rel if p in tracked),
            "rotate_untracked": sorted(p for p in rot_rel if p not in tracked),
            "frozen": key == LEGACY,
        }
    return plan


def prescan_hits(paths):
    """treasure_guard s2.1 prescan over the candidate set (single source:
    import the guard module, never re-implement matching)."""
    sys.path.insert(0, HERE)
    import treasure_guard
    fam, ex, gl = treasure_guard.load_registry(ROOT)
    return treasure_guard.hits_of(paths, fam, ex, gl)


def build_report(window):
    tracked = _git_tracked("qa")
    entries, named = classify_qa_dir(QA_DIR)
    plan = rotation_plan(entries, window, tracked)
    rot_tracked = sorted(p for b in plan.values()
                         for p in b["rotate_tracked"])
    rot_untracked = sorted(p for b in plan.values()
                           for p in b["rotate_untracked"])
    hits = prescan_hits(rot_tracked + rot_untracked)
    return {
        "ts": now_iso(),
        "law_refs": ["state/queue/tech.md T12",
                     "TREASURE_PROTECTION_LAW s2",
                     "D-20261009-02 zero-rename (legacy frozen)",
                     "D-20261002-04 claw (tracked churn = no-owner class)",
                     "C-20261007-04 adjudication pattern (r703 bm-c)"],
        "qa_files_total": len(entries) + len(named),
        "named_keep_forever": len(named),
        "window_rounds_per_bucket": window,
        "buckets": plan,
        "rotate_tracked_total": len(rot_tracked),
        "rotate_untracked_total": len(rot_untracked),
        "rotate_tracked_paths": rot_tracked,
        "rotate_untracked_paths": rot_untracked,
        "prescan_hits": hits,
        "claw_note": ("tracked churn blobs (md prose/png binary) carry no "
                      "JSON owner evidence -> git_claw blocks any push "
                      "deleting them (all machines); rotation of tracked "
                      "candidates needs the C-20261007-04 adjudication "
                      "pattern + --no-verify escape + receipt (r703 bm-c)"),
        "rotate_executed": False,
    }


def rotation_gate(rep, adjudicated):
    """Pure fail-closed gate for --rotate. Returns (rc, msg)."""
    if rep["prescan_hits"]:
        return 3, ("HARD REFUSE: treasure registry hit over rotation set: "
                   + ", ".join(rep["prescan_hits"][:5]))
    if rep["rotate_tracked_paths"] and not adjudicated:
        return 3, ("HARD REFUSE: %d tracked candidate(s) without "
                   "--adjudicated <case-ref> (C-20261007-04 pattern "
                   "required; claw will block the deletion push otherwise)"
                   % len(rep["rotate_tracked_paths"]))
    if not (rep["rotate_tracked_paths"] or rep["rotate_untracked_paths"]):
        return 3, "nothing to rotate: candidate set empty"
    return 0, "gated-ok"


def execute_rotation(rep, adjudicated):
    """Quarantine-path rotation via the treasure_guard CLI + manifest
    assert (s2.2/s2.3 single source)."""
    rc, msg = rotation_gate(rep, adjudicated)
    if rc != 0:
        print(msg)
        return rc
    candidates = rep["rotate_tracked_paths"] + rep["rotate_untracked_paths"]
    reason = ("qa rolling-window rotation (T12 probe, window %d) %s"
              % (rep["window_rounds_per_bucket"],
                 "adjudicated=" + adjudicated if adjudicated
                 else "untracked-only"))
    q = subprocess.run(
        [sys.executable, os.path.join(HERE, "treasure_guard.py"),
         "quarantine"] + candidates + ["--reason", reason],
        capture_output=True, creationflags=NO_WINDOW)
    out = (q.stdout or b"").decode("utf-8", "replace")
    print(out)
    if q.returncode != 0:
        print("treasure_guard quarantine rc=%d" % q.returncode)
        return 2
    m = re.search(r"manifest: (\S+)", out)
    manifest = m.group(1) if m else None
    if manifest:
        a = subprocess.run(
            [sys.executable, os.path.join(HERE, "treasure_guard.py"),
             "assert", "--manifest", manifest],
            capture_output=True, creationflags=NO_WINDOW)
        print((a.stdout or b"").decode("utf-8", "replace"))
        if a.returncode != 0:
            return 2
    receipt = {
        "ts": rep["ts"],
        "moved": len(candidates),
        "adjudicated": adjudicated,
        "paths": candidates,
        "manifest": manifest,
        "claw_push_note": ("push deleting tracked candidates WILL hit the "
                           "pre-push claw -> escape hatch git push "
                           "--no-verify + round-report line + receipt "
                           "(r703 bm-c pattern)")
                          if rep["rotate_tracked_paths"]
                          else "untracked-only rotation: no claw surface",
    }
    with open(RECEIPT, "w", encoding="utf-8") as fh:
        json.dump(receipt, fh, ensure_ascii=True, indent=1)
    print("rotation receipt:", os.path.relpath(RECEIPT, ROOT))
    return 0


def _bytes_of(paths):
    tot = 0
    for p in paths:
        fp = os.path.join(ROOT, p)
        if os.path.isfile(fp):
            tot += os.path.getsize(fp)
    return tot


def selftest():
    """Hermetic: tempdir fixtures + pure functions only; zero
    company-repo mutation, zero quarantine of real files."""
    fails = []
    n = [0]

    def leg(name, cond):
        n[0] += 1
        print("  [%s] %s" % ("PASS" if cond else "FAIL", name))
        if not cond:
            fails.append(name)

    with tempfile.TemporaryDirectory() as td:
        qd = os.path.join(td, "qa")
        os.makedirs(qd)
        fx = [
            "smoke-r100.md", "equity-curve-r100.png", "smoke-r100.log",
            "smoke-r101-bm-b.md", "equity-curve-r101-bm-b.png",
            "smoke-r131-bm-b.md", "equity-curve-r131-bm-b.png",
            "smoke-r131-bm-b.log",
            "smoke-r200-bm-c.md", "equity-curve-r200-bm-c.png",
            "smoke-r201-bm-c.md", "equity-curve-r201-bm-c.png",
            "smoke-r230-bm-c.md", "equity-curve-r230-bm-c.png",
            "smoke-r890-bm-a.md", "equity-curve-r890-bm-a.png",
            "smoke-r891-bm-a.md", "equity-curve-r891-bm-a.png",
            "mass-trial-report-r712.md", "trading-calendar-r715.md",
            "sina-mf-ic-census-r718.md", "open-market-readiness-r714.md",
        ]
        for f in fx:
            with open(os.path.join(qd, f), "w", encoding="utf-8") as fh:
                fh.write("x")
        entries, named = classify_qa_dir(qd)
        leg("named keep-forever isolated (4)",
            sorted(named) == ["mass-trial-report-r712.md",
                              "open-market-readiness-r714.md",
                              "sina-mf-ic-census-r718.md",
                              "trading-calendar-r715.md"])
        by_key = {}
        for e in entries:
            by_key.setdefault(e["machine"] or LEGACY, []).append(e)
        leg("legacy bucket collects untagged", len(by_key[LEGACY]) == 3)
        leg("machine buckets split (bm-b incl. .log)",
            len(by_key["bm-b"]) == 5 and len(by_key["bm-c"]) == 6
            and len(by_key["bm-a"]) == 4)
        tracked = {"qa/smoke-r101-bm-b.md", "qa/equity-curve-r101-bm-b.png",
                   "qa/smoke-r131-bm-b.md", "qa/equity-curve-r131-bm-b.png",
                   "qa/smoke-r200-bm-c.md", "qa/equity-curve-r200-bm-c.png",
                   "qa/smoke-r201-bm-c.md", "qa/equity-curve-r201-bm-c.png",
                   "qa/smoke-r230-bm-c.md", "qa/equity-curve-r230-bm-c.png",
                   "qa/smoke-r890-bm-a.md", "qa/equity-curve-r890-bm-a.png",
                   "qa/smoke-r891-bm-a.md", "qa/equity-curve-r891-bm-a.png"}
        plan = rotation_plan(entries, 30, tracked)
        leg("legacy frozen: zero rotation despite old rounds",
            plan[LEGACY]["frozen"] and plan[LEGACY]["rotate_tracked"] == []
            and plan[LEGACY]["rotate_untracked"] == []
            and plan[LEGACY]["files_total"] == 3)
        leg("small buckets fully inside window (bm-b/bm-a)",
            plan["bm-b"]["rotate_tracked"] == []
            and plan["bm-a"]["rotate_tracked"] == [])
        leg("sparse bucket (3 rounds < window) keeps all, zero rotation",
            plan["bm-c"]["rotate_tracked"] == []
            and plan["bm-c"]["window_keep"] == 6)
        leg("untracked log lands in local-disk class",
            plan["bm-b"]["rotate_untracked"] == []
            and "qa/smoke-r131-bm-b.log" not in tracked)
        plan10 = rotation_plan(entries, 10, tracked)
        leg("window=10 keeps every sparse bucket (round gaps < window)",
            all(not plan10[k]["rotate_tracked"] for k in plan10
                if k != LEGACY))
        for i in range(1, 41):
            with open(os.path.join(qd, "smoke-r%03d-bm-b.md" % i), "w",
                      encoding="utf-8") as fh:
                fh.write("x")
        entries2, _ = classify_qa_dir(qd)
        tracked2 = set(tracked)
        for i in range(1, 41):
            tracked2.add("qa/smoke-r%03d-bm-b.md" % i)
        plan2 = rotation_plan(entries2, 30, tracked2)
        leg("dense bucket: 42 rounds -> newest-30 window, oldest 12 rotated",
            plan2["bm-b"]["rotate_tracked"] ==
            sorted("qa/smoke-r%03d-bm-b.md" % i for i in range(1, 13))
            and plan2["bm-b"]["window_keep"] == 33)

        # prescan matcher legs (fixture registry, real treasure_guard source)
        sys.path.insert(0, HERE)
        import treasure_guard
        fam, ex, gl = treasure_guard.parse_registry(
            "| results/lowamp_p1/ lowamp_p2/ | verdicts |\n"
            "| knowledge/market_rules*.md | rules |\n")
        leg("prescan matcher: registry family hit detected",
            treasure_guard.hits_of(
                ["qa/smoke-r100.md", "results/lowamp_p1/x.json"],
                fam, ex, gl) == ["results/lowamp_p1/x.json"])
        leg("prescan matcher: qa churn clean vs fixture registry",
            treasure_guard.hits_of(
                ["qa/smoke-r100.md", "qa/equity-curve-r200-bm-c.png"],
                fam, ex, gl) == [])

        # rotation gate legs (pure, fail-closed order: prescan > adjudication
        # > empty-set)
        rep_hit = {"prescan_hits": ["results/lowamp_p1/x.json"],
                   "rotate_tracked_paths": [], "rotate_untracked_paths": []}
        leg("gate: prescan hit refuses (rc3) even with adjudication",
            rotation_gate(rep_hit, "C-20261007-04")[0] == 3)
        rep_tracked = {"prescan_hits": [],
                       "rotate_tracked_paths": ["qa/smoke-r200-bm-c.md"],
                       "rotate_untracked_paths": []}
        leg("gate: tracked candidates without adjudication refuse (rc3)",
            rotation_gate(rep_tracked, None)[0] == 3)
        leg("gate: tracked candidates with adjudication pass (rc0)",
            rotation_gate(rep_tracked, "C-20261007-04")[0] == 0)
        rep_untracked = {"prescan_hits": [], "rotate_tracked_paths": [],
                         "rotate_untracked_paths": ["qa/smoke-r100.log"]}
        leg("gate: untracked-only passes without adjudication (rc0)",
            rotation_gate(rep_untracked, None)[0] == 0)
        rep_empty = {"prescan_hits": [], "rotate_tracked_paths": [],
                     "rotate_untracked_paths": []}
        leg("gate: empty candidate set refuses (rc3)",
            rotation_gate(rep_empty, None)[0] == 3)

    print("selftest: %d/%d PASS" % (n[0] - len(fails), n[0]))
    if fails:
        print("FAIL: %r" % fails)
    return 1 if fails else 0


def main(argv):
    ap = argparse.ArgumentParser(description="QA evidence rotation probe (T12)")
    ap.add_argument("subcommand", nargs="?", default="probe",
                    choices=["probe", "selftest"])
    ap.add_argument("--window", type=int, default=30)
    ap.add_argument("--rotate", action="store_true")
    ap.add_argument("--adjudicated", default=None)
    a = ap.parse_args(argv)
    if a.subcommand == "selftest":
        return selftest()
    if not os.path.isdir(QA_DIR):
        print("qa/ missing:", QA_DIR)
        return 2
    try:
        rep = build_report(a.window)
    except Exception as exc:
        print("mechanism fault: %r" % (exc,))
        return 2
    rep["rotate_bytes_tracked"] = _bytes_of(rep["rotate_tracked_paths"])
    rep["rotate_bytes_untracked"] = _bytes_of(rep["rotate_untracked_paths"])
    with open(REPORT, "w", encoding="utf-8") as fh:
        json.dump(rep, fh, ensure_ascii=True, indent=1)
    print("qa_rotation_probe: files=%d named=%d rot_tracked=%d (%dB) "
          "rot_untracked=%d (%dB) prescan_hits=%d report=%s"
          % (rep["qa_files_total"], rep["named_keep_forever"],
             rep["rotate_tracked_total"], rep["rotate_bytes_tracked"],
             rep["rotate_untracked_total"], rep["rotate_bytes_untracked"],
             len(rep["prescan_hits"]), os.path.relpath(REPORT, ROOT)))
    if a.rotate:
        return execute_rotation(rep, a.adjudicated)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
