# -*- coding: utf-8 -*-
"""r807(2nd) bm-c half-open rebase recovery driver (r867->r868 twin case).

Situation (triage facts 2026-10-09 15:0x):
- Predecessor r807 session died 14:48:43 mid-rebase: 6 picks onto d4ea4b348,
  picks 1-2 applied (rewritten 84520f9a3/638d6325f), stopped AT pick 3
  (036d001d autofill tick keepalive) with conflict resolved+staged but
  continue never run (r867 death form).
- My round-start S0 absorb then blindly add+commit -> 0e90e21b2 landed ON the
  stopped pick position = became pick-3 carrier (r868 blind-commit form;
  content superset: predecessor's staged trio resolution + 8 own absorb
  faces; message mismatch = r685 tolerable carrier, disclosed in report).
- Remaining todo picks 4-6 = predecessor's r807 PRODUCT (T2 dashboard
  3-face wiring + ORD receipts + S6 40/40 + QA 5/5) + two s0-tail absorbs.
  r624 quit would LOSE them -> sequencer must be driven to completion.

Recovery law choreography:
- reset --soft HEAD~1 (undo carrier commit; content stays staged);
- add -A + rebase --continue ATOMICALLY back-to-back in-process (r787/r516-2
  law) -> commit_staged_changes re-creates pick 3 with ORIGINAL author-script
  + message, advances through picks 4-6;
- per-stop UU resolution = r805 resolver machinery IMPORTED (reuse-not-rebuild
  law): sha channel reads (r648), marker hard gate (r648/r804), deep-ts
  newer-wins, tie->stage2 (r794), ledger/union faces, targeted add (r794);
- empty-commit refuse -> r808 three-step (author-script env + commit -F
  message) then continue; repeated refuse -> report and stop (no blind loops).
Exit: 0 recovered | 2 mechanism failure (r705 hard gates never print-only)."""
import importlib.util
import json
import os
import subprocess
import sys
import datetime as dt

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREATE = 0x08000000
RM = os.path.join(ROOT, ".git", "rebase-merge")
RECEIPT = os.path.join(ROOT, "results", "_r807bmc_rebase_recover.json")

EXPECT_HEAD = "0e90e21b20173decda43107c081d6d894f34a1cf"
EXPECT_PARENT = "638d6325f"
EXPECT_STOPPED = "036d001d14514270b5fe0373546118b4babb992a"
TRIO = ("results/autofill_state.bm-c.json",
        "results/saturation_engine/face_bm-c.json",
        "results/saturation_engine_state.bm-c.json")


def git(args, env=None):
    e = dict(os.environ)
    e["PYTHONUTF8"] = "1"
    if env:
        e.update(env)
    p = subprocess.run(["git", "-C", ROOT] + args, capture_output=True,
                       creationflags=CREATE, env=e)
    return (p.returncode, (p.stdout or b"").decode("utf-8", "replace"),
            (p.stderr or b"").decode("utf-8", "replace"))


def load_resolver():
    spec = importlib.util.spec_from_file_location(
        "r805_resolver", os.path.join(ROOT, "Tools", "_r805bmc_resolver.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def uu_faces():
    rc, out, _ = git(["ls-files", "-u"])
    faces = {}
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) != 2:
            continue
        f = parts[0].split()
        stage = int(f[2])
        faces.setdefault(parts[1], {})[stage] = f[1]
    return faces


def read_file(path):
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read().strip()


def main():
    r = {"round": "r807-recover", "steps": [], "uu_stops": 0, "notes": []}

    # --- sanity gates ---
    assert os.path.isdir(RM), "rebase-merge missing: not in half-open state"
    stopped = read_file(os.path.join(RM, "stopped-sha"))
    assert stopped == EXPECT_STOPPED, "unexpected stopped-sha %s" % stopped
    rc, out, _ = git(["rev-parse", "HEAD"])
    head = out.strip()
    assert head == EXPECT_HEAD, "HEAD moved: %s" % head
    rc, out, _ = git(["rev-parse", "HEAD~1"])
    parent = out.strip()
    assert parent.startswith(EXPECT_PARENT), "unexpected parent %s" % parent
    assert not uu_faces(), "UU non-empty before recovery start"
    r["sanity"] = "OK head=%s parent=%s stopped=%s" % (
        head[:9], parent[:9], stopped[:9])

    # --- marker scan on carrier commit's trio blobs (r648 hard gate) ---
    marker_hits = []
    for p in TRIO:
        rc, out, _ = git(["show", "HEAD:%s" % p])
        if any(m in out.encode("utf-8", "replace") for m in
               (b"<<<<<<<", b">>>>>>>")):
            marker_hits.append(p)
    r["carrier_marker_hits"] = marker_hits
    if marker_hits:
        r["notes"].append("carrier blobs carried markers; add -A restages "
                          "fresh live worktree versions (self-heal face)")

    # --- reset --soft: carrier commit undone, content stays staged ---
    rc, out, err = git(["reset", "--soft", "HEAD~1"])
    assert rc == 0, "reset --soft rc=%d %s" % (rc, err[:200])
    r["steps"].append("reset --soft -> HEAD=%s" % parent[:9])

    # --- atomic add -A + continue (r787/r516-2) ---
    rc1, o1, e1 = git(["add", "-A"])
    rc2, o2, e2 = git(["rebase", "--continue"])
    r["steps"].append("add-A rc=%d; continue-1 rc=%d out=%r" % (
        rc1, rc2, (e2 or o2)[:300]))
    last_out = e2 or o2

    # --- drive to completion ---
    guard = 0
    while os.path.isdir(RM) and guard < 10:
        guard += 1
        faces = uu_faces()
        if faces:
            r["uu_stops"] += 1
            mod = load_resolver()
            receipt = {"round": "r807-recover", "replay": "pick-window",
                       "decisions": {}, "staged": [], "gates": {}}
            resolved = {}
            for path in sorted(faces):
                s = faces[path]
                b2 = mod.git(["cat-file", "-p", s[2]])
                b3 = mod.git(["cat-file", "-p", s[3]])
                resolved[path] = mod.resolve_face(path, b2, b3, receipt)
            bad = []
            for path, blob in resolved.items():
                if mod.has_markers(blob):
                    bad.append("markers:%s" % path)
                if path.endswith(".json"):
                    try:
                        json.loads(blob.decode("utf-8", "replace"))
                    except ValueError as ex:
                        bad.append("json:%s:%s" % (path, ex))
            if bad:
                r["gates_fail"] = bad
                with open(RECEIPT, "w", encoding="utf-8", newline="\n") as fh:
                    json.dump(r, fh, ensure_ascii=False, indent=1)
                print("RESOLVE_VERIFY_FAIL: %s" % bad)
                return 2
            for path, blob in resolved.items():
                with open(os.path.join(ROOT, *path.split("/")), "wb") as fh:
                    fh.write(blob)
            rc, out, err = git(["add"] + list(resolved) + ["-A"])
            r["steps"].append("stop#%d resolved %d faces -> add rc=%d"
                              % (guard, len(resolved), rc))
            rc, out, err = git(["rebase", "--continue"])
            r["steps"].append("stop#%d continue rc=%d out=%r"
                              % (guard, rc, (err or out)[:200]))
            last_out = err or out
            continue
        # UU empty: empty-commit refuse -> r808 three-step; churn -> add -A
        if "no changes added" in last_out or "nothing to commit" in last_out:
            env = {}
            for line in read_file(os.path.join(RM, "author-script")).splitlines():
                if "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    if k in ("GIT_AUTHOR_NAME", "GIT_AUTHOR_EMAIL",
                             "GIT_AUTHOR_DATE"):
                        env[k] = v.strip().strip("'")
            rc, out, err = git(["commit", "-F", os.path.join(RM, "message")],
                               env=env)
            r["steps"].append("r808 three-step commit rc=%d %s" % (
                rc, (err or out)[:150]))
            rc, out, err = git(["rebase", "--continue"])
            r["steps"].append("post-threestep continue rc=%d %r" % (
                rc, (err or out)[:200]))
            last_out = err or out
            if rc != 0 and not os.path.isdir(RM):
                break
            continue
        rc1, o1, e1 = git(["add", "-A"])
        rc2, o2, e2 = git(["rebase", "--continue"])
        r["steps"].append("stop#%d churn-absorb add rc=%d continue rc=%d %r"
                          % (guard, rc1, rc2, (e2 or o2)[:200]))
        last_out = e2 or o2
        if rc2 != 0 and not os.path.isdir(RM):
            break

    r["completed"] = not os.path.isdir(RM)
    rc, out, _ = git(["rev-parse", "HEAD"])
    r["final_head"] = out.strip()
    rc, out, _ = git(["log", "--oneline", "-10"])
    r["final_log"] = out.strip()
    rc, out, _ = git(["status", "--porcelain"])
    r["final_dirty"] = out.strip()
    rc, out, _ = git(["rev-list", "--left-right", "--count",
                      "HEAD...origin/main"])
    r["ahead_behind"] = out.strip()
    with open(RECEIPT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(r, fh, ensure_ascii=False, indent=1)
    print(json.dumps({k: r[k] for k in
                      ("sanity", "completed", "uu_stops", "final_head",
                       "ahead_behind")}, ensure_ascii=False, indent=1))
    print("\n".join(r["steps"]))
    print("FINAL-LOG:\n" + r["final_log"])
    return 0 if r["completed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
