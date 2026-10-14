"""D-20261015-02 (council dispatch; F-20261014-01/02) bm-c leg selftest.

bm-c leg executed in commit 5b174a247 (gitignore + 7 own-face index
removals, disk files stay live-wins); this file is the selftest+live-probe
receipt the dispatch requires (回执窗 10-17 00:00):
  S1  the 22 explicit family patterns + generic blocks present in
      .gitignore canon (incl. the history_bm-*.jsonl generic line
      closing the bm-c history gap added this round)
  S2  the 7 bm-c-owned faces untracked (git ls-files) AND ignored
      (git check-ignore) AND still on disk (zero producer change)
  S3  shared-name legacy face results/autofill_state.json STAYS tracked
      (retired-in-place frozen, F-20261008-02 law)
  S4  _machine_health_union() parses the union ledger into per-machine rows
  S5  _engine_face_state() union fallback: with no local face files,
      rows come from the machine-health union (source=
      machine_health_union, py_cpu_pct honest None)
  S6  live merge: own machine (bm-c) live row present with engine_alive
      bool and source=live_face

Usage: python results/d20261015_02_tickface/selftest_bm-c.py
Exit 0 = all legs PASS; 1 = any FAIL (printed).
"""
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

FAMILY_PATTERNS = [
    "results/autofill_state.bm-a.json",
    "results/autofill_state.bm-b.json",
    "results/autofill_state.bm-c.json",
    "results/_sentinel_bm-a.json",
    "results/_sentinel_bm-c.json",
    "results/dispatcher_state.bm-a.json",
    "results/dispatcher_state.bm-c.json",
    "results/idle_trigger.bm-a.json",
    "results/idle_trigger.bm-b.json",
    "results/idle_trigger.bm-c.json",
    "results/idle_trigger_state.bm-a.json",
    "results/idle_trigger_state.bm-b.json",
    "results/idle_trigger_state.bm-c.json",
    "results/saturation_engine/state_bm-a.json",
    "results/saturation_engine/state_bm-b.json",
    "results/saturation_engine/state_bm-c.json",
    "results/saturation_engine/face_bm-a.json",
    "results/saturation_engine/face_bm-b.json",
    "results/saturation_engine/face_bm-c.json",
    "results/saturation_engine/history_bm-a.jsonl",
    "results/saturation_engine/history_bm-b.jsonl",
    "results/saturation_engine/history_bm-*.jsonl",
    "results/saturation_engine_state.bm-c.json",
]

# bm-c-owned live-tick faces removed from index by 5b174a247
# (saturation_engine/state_bm-c.json + history_bm-c.jsonl never existed
# on this machine -- honest zero, not part of this leg's removals)
OWN_FACES = [
    "results/autofill_state.bm-c.json",
    "results/_sentinel_bm-c.json",
    "results/dispatcher_state.bm-c.json",
    "results/idle_trigger.bm-c.json",
    "results/idle_trigger_state.bm-c.json",
    "results/saturation_engine/face_bm-c.json",
    "results/saturation_engine_state.bm-c.json",
]

MACHINE = "bm-c"


def _leg(name, ok, note=""):
    print(("[PASS] " if ok else "[FAIL] ") + name + (" | " + note if note else ""))
    return ok


def main() -> int:
    results = []

    # S1 canon block present (explicit + generic patterns)
    gi = open(os.path.join(ROOT, ".gitignore"), encoding="utf-8").read()
    missing = [p for p in FAMILY_PATTERNS if p not in gi]
    results.append(_leg("S1 gitignore canon: %d/%d family patterns"
                        % (len(FAMILY_PATTERNS) - len(missing),
                           len(FAMILY_PATTERNS)),
                        not missing, "missing=" + ",".join(missing)))

    # S2 own faces untracked + ignored + on disk
    untracked, ignored, on_disk = [], [], []
    for p in OWN_FACES:
        r = subprocess.run(["git", "-C", ROOT, "ls-files", "--", p],
                           capture_output=True)
        untracked.append(r.stdout.strip() == b"")
        r = subprocess.run(["git", "-C", ROOT, "check-ignore", "-q", p],
                           capture_output=True)
        ignored.append(r.returncode == 0)
        on_disk.append(os.path.exists(os.path.join(ROOT, p)))
    results.append(_leg("S2 own 7 faces untracked+ignored+on-disk",
                        all(untracked) and all(ignored) and all(on_disk),
                        "untracked=%d/7 ignored=%d/7 on_disk=%d/7"
                        % (sum(untracked), sum(ignored), sum(on_disk))))

    # S3 shared-name legacy stays tracked (frozen)
    r = subprocess.run(["git", "-C", ROOT, "ls-files",
                        "--error-unmatch", "results/autofill_state.json"],
                       capture_output=True)
    results.append(_leg("S3 legacy shared autofill_state.json still tracked "
                       "(retired-in-place frozen)", r.returncode == 0))

    # S4 union parser
    from monitor import build_status as bs
    union = bs._machine_health_union()
    ok4 = isinstance(union, dict) and len(union) >= 1
    note4 = "machines=" + ",".join(sorted(union.keys()))
    results.append(_leg("S4 machine-health union rows parsed", ok4, note4))

    # S5 union fallback with no local face files (post-rollout simulation)
    saved = bs.PATHS.results_dir
    with tempfile.TemporaryDirectory() as td:
        os.makedirs(os.path.join(td, "saturation_engine"), exist_ok=True)
        bs.PATHS.results_dir = td
        try:
            st = bs._engine_face_state()
        finally:
            bs.PATHS.results_dir = saved
    ok5 = bool(st.get("present")) and bool(st.get("rows")) and all(
        r.get("source") == "machine_health_union" for r in st["rows"])
    results.append(_leg("S5 union fallback rows (no local face files)", ok5,
                        "rows=%d total=%d" % (len(st.get("rows") or []),
                                              st.get("machines_total") or 0)))

    # S6 live merge (current checkout) -- own machine row
    live = bs._engine_face_state()
    own = [r for r in live.get("rows", [])
           if r.get("machine_id") == MACHINE]
    ok6 = (live.get("present") and live.get("machines_total", 0) >= 1
           and own and isinstance(own[0].get("engine_alive"), bool)
           and own[0].get("source") == "live_face")
    results.append(_leg("S6 live merge: own row live_face+bool alive", ok6,
                        "total=%d alive=%d own_source=%s"
                        % (live.get("machines_total", 0),
                           live.get("machines_alive", 0),
                           own[0].get("source") if own else "none")))

    verdict = {"ts_pass": __import__("datetime").datetime.now().isoformat(
                   timespec="seconds"),
               "machine": MACHINE, "leg_commit": "5b174a247",
               "legs": len(results), "pass": sum(results),
               "verdict": "PASS" if all(results) else "FAIL"}
    outp = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "selftest_bm-c.json")
    with open(outp, "w", encoding="utf-8") as f:
        json.dump(verdict, f, ensure_ascii=False, indent=1)
    print("selftest verdict:", verdict["verdict"],
          "(%d/%d)" % (verdict["pass"], verdict["legs"]))
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
