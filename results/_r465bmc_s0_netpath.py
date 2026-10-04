"""r465 bm-c S0 pre-alignment netpath driver (r437/r440 + bm-a r673 mirror):
crash_fuse per-key max-merge (already staged by probe) -> land to live face ->
absorb 5 dirty faces -> merge origin/main -> resolve crash_fuse UU with ours
(max-merge supersedes origin older entries, zero-loss verified per key) ->
push_verify single-source. Fail-closed: any UU face outside the known
crash_fuse.json = abort (no auto-resolve of unknown faces). Assertions before
every commit gate; log file-out per r446 probe law."""
import datetime
import json
import os
import shutil
import subprocess
import sys

C = 0x08000000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FUSE = os.path.join(ROOT, "results", "crash_fuse.json")
MERGED = os.path.join(ROOT, "results", "_r465bmc_crash_fuse_merged.json")
LOG = os.path.join(ROOT, "results", "_r465bmc_s0_netpath_log.txt")
LANE = ["results/autofill_state.bm-c.json", "results/crash_fuse.bm-c.json",
        "results/saturation_engine/face_bm-c.json",
        "results/saturation_engine_state.bm-c.json"]
TRIO = ["scripts/fund_divlowvol_p1.py|run,--nulls",
        "scripts/fund_quality_p1.py|run,--nulls",
        "scripts/fund_value_p1.py|run,--nulls"]
THEME = "scripts/theme_judge_p1.py|run"
ORIGIN_NEWER_MIN = "2026-10-04 11:18:03"
WT_NEWER_MIN = "2026-10-04 11:20:04"

lines = []


def log(s):
    lines.append(s)
    print(s)


def git(*a):
    p = subprocess.run(["git"] + list(a), capture_output=True,
                       creationflags=C, cwd=ROOT)
    return p.returncode, (p.stdout or b"").decode("utf-8", "replace"), \
        (p.stderr or b"").decode("utf-8", "replace")


def ent_ts(e):
    return max(e.get("last_refusal_ts", "") or "", e.get("last_crash_ts", "") or "")


def verify_fuse(path=FUSE, label=""):
    with open(path, "rb") as f:
        obj = json.load(f)  # reparse gate
    sigs = obj["sigs"]
    for k in TRIO:
        e = sigs.get(k)
        assert e, "missing sig " + k
        assert ent_ts(e) >= ORIGIN_NEWER_MIN, "trio ts stale " + k + " " + ent_ts(e)
    e = sigs.get(THEME)
    assert e, "missing theme sig"
    assert ent_ts(e) >= WT_NEWER_MIN, "theme ts stale " + ent_ts(e)
    assert len(sigs) == 64, "sigs count " + str(len(sigs))
    assert len(obj["cleared"]) == 47, "cleared count " + str(len(obj["cleared"]))
    log("VERIFY_OK %s sigs=64 cleared=47 trio>=%s theme>=%s" % (label, ORIGIN_NEWER_MIN, WT_NEWER_MIN))
    return True


def main():
    log("r465 S0 netpath start " + datetime.datetime.now().isoformat(timespec="seconds"))
    verify_fuse(MERGED, "merged-staging")
    shutil.copyfile(MERGED, FUSE)
    verify_fuse(FUSE, "live-face")
    merged_cycles = 0
    for cycle in (1, 2):
        rc, out, err = git("add", "--", "results/crash_fuse.json", *LANE)
        assert rc == 0, "add fail " + err[:200]
        rc, out, err = git("commit", "-m",
                           "absorb r465 bm-c: daemon lane faces + crash_fuse per-key max-merge "
                           "(fund trio sigs origin-newer 11:18:03, theme_judge sig wt-newer 11:20:04, "
                           "64sigs/47cleared zero-loss reparse PASS) -- S0 pre-alignment r437")
        if rc != 0 and "nothing to commit" in (out + err):
            log("cycle %d absorb: nothing to commit" % cycle)
        else:
            assert rc == 0, "absorb commit fail " + (out + err)[:300]
            log("cycle %d absorb commit OK" % cycle)
        rc, out, err = git("merge", "origin/main", "--no-edit")
        if rc == 0:
            log("cycle %d MERGE CLEAN: " % cycle + (out or err).strip()[:160])
            merged_cycles = cycle
            break
        rc2, st, _ = git("status", "--porcelain")
        uu = [l[3:] for l in st.splitlines() if l.startswith("UU")]
        if not uu:
            log("cycle %d MERGE REFUSED no-UU: " % cycle + (out + err)[:300])
            continue
        log("cycle %d UU faces: %s" % (cycle, json.dumps(uu)))
        unknown = [u for u in uu if u != "results/crash_fuse.json"]
        assert not unknown, "UNKNOWN UU faces -- abort for canon resolution: " + repr(unknown)
        rc, out, err = git("checkout", "--ours", "--", "results/crash_fuse.json")
        assert rc == 0, "checkout --ours fail " + err[:200]
        verify_fuse(FUSE, "post-resolve")
        rc, out, err = git("add", "--", "results/crash_fuse.json")
        assert rc == 0, "re-add fail " + err[:200]
        rc, out, err = git("commit", "--no-edit")
        assert rc == 0, "merge commit fail " + (out + err)[:300]
        log("cycle %d merge commit OK (crash_fuse ours = max-merge superset)" % cycle)
        merged_cycles = cycle
        break
    assert merged_cycles >= 1, "merge never completed"
    verify_fuse(FUSE, "post-merge-final")
    pr = subprocess.run([sys.executable, "Tools/push_verify.py"],
                        capture_output=True, creationflags=C, cwd=ROOT)
    ptxt = (pr.stdout or b"").decode("utf-8", "replace") + " || " + \
        (pr.stderr or b"").decode("utf-8", "replace")
    log("PUSH_VERIFY_RC %d" % pr.returncode)
    log(ptxt.strip()[-400:])
    with open(LOG, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    sys.exit(pr.returncode if pr.returncode in (0, 1) else 2)


if __name__ == "__main__":
    main()
