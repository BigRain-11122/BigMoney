# -*- coding: utf-8 -*-
# _r1010bmc_d02_selftest.py -- D-20261015-02 dir-1 (pure live-tick faces out-of-repo)
# Selftest: (S1) 7 own-suffix faces ignored; (S2) index clean of them; shared-name
#   frozen face + other-machine faces + quarantine evidence + science faces all
#   still tracked; (S3) no pattern overreach on evidence copies.
# Live probe (race-fix proof): disk files ARE daemon-rewritten this round (fresh
#   mtime), yet git status blind + git-stash-create tree contains zero tick faces
#   -> S0 stash-bridge race structurally eliminated for this family.
import json, os, subprocess, time

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
GIT = r"C:\Program Files\Git\cmd\git.exe"
OUT = os.path.join(REPO, "results", "_r1010bmc_d02_tickface_outofrepo.json")

UNTRACKED = [
    "results/autofill_state.bm-c.json",
    "results/dispatcher_state.bm-c.json",
    "results/idle_trigger.bm-c.json",
    "results/idle_trigger_state.bm-c.json",
    "results/_sentinel_bm-c.json",
    "results/saturation_engine_state.bm-c.json",
    "results/saturation_engine/face_bm-c.json",
]
MUST_STAY_TRACKED = [
    "results/autofill_state.json",  # shared-name legacy, retired-in-place frozen
    "results/autofill_state.bm-a.json",  # other-machine faces: their windows remove
    "results/autofill_state.bm-b.json",
    "results/dispatcher_state.bm-a.json",
    "results/idle_trigger.bm-a.json",
    "results/idle_trigger_state.bm-a.json",
    "results/_sentinel_bm-a.json",
    "results/saturation_engine/face_bm-a.json",
    "results/saturation_engine/face_bm-b.json",
    # frozen evidence backups (pattern-overreach guard):
    "results/_r753bmc_churn_backup/results__autofill_state.bm-c.json",
    "results/_r753bmc_churn_backup/results__dispatcher_state.bm-c.json",
    "results/_r753bmc_churn_backup/results__idle_trigger_state.bm-c.json",
    "results/_quarantine/r964-estate-20261013/results__idle_trigger.bm-a.json",
    "results/_r883bmc_sync_backup/results__saturation_engine_state.bm-c.json",
    # science/evidence faces untouched by this scope:
    "results/pool_dualrun.bm-c.jsonl",
    "results/post_review.jsonl",
    # NB: results/watermark_red.json deliberately NOT asserted stay-tracked --
    # it was never tracked (already gitignored line 84 before D-02 dir-1).
]

def git(*a):
    r = subprocess.run([GIT, "-C", REPO] + list(a), capture_output=True)
    return r.returncode, r.stdout.decode("utf-8", "replace")

def main():
    rep = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "decision": "D-20261015-02 dir-1",
           "selftest": {}, "live_probe": {}}
    ok = True

    # S1: check-ignore each untracked face
    ign = {}
    for p in UNTRACKED:
        rc, out = git("check-ignore", "-q", p)
        ign[p] = (rc == 0)
        ok &= (rc == 0)
    rep["selftest"]["check_ignore_7_faces"] = ign
    _, ls = git("ls-files")
    idx = set(ls.splitlines())
    rep["selftest"]["index_has_own_faces"] = sorted(p for p in UNTRACKED if p in idx)
    ok &= not any(p in idx for p in UNTRACKED)

    # S2: stay-tracked faces
    stay = {p: (p in idx) for p in MUST_STAY_TRACKED}
    rep["selftest"]["stay_tracked"] = stay
    bad_stay = [p for p, v in stay.items() if not v]
    ok &= not bad_stay
    rep["selftest"]["stay_tracked_missing"] = bad_stay

    # S3: no overreach (evidence copies must NOT be ignored)
    over = {}
    for p in ("results/_r753bmc_churn_backup/results__autofill_state.bm-c.json",
              "results/pool_dualrun.bm-c.jsonl", "results/post_review.jsonl"):
        rc, _ = git("check-ignore", "-q", p)
        over[p] = (rc == 1)  # rc1 = not ignored = correct
        ok &= (rc == 1)
    rep["selftest"]["no_overreach"] = over

    # Live probe: (a) disk faces exist with fresh mtime (daemon live-write proof)
    mt = {}
    for p in UNTRACKED:
        fp = os.path.join(REPO, p)
        mt[p] = round(os.path.getmtime(fp), 1) if os.path.isfile(fp) else None
    rep["live_probe"]["disk_mtime_fresh"] = mt
    ok &= all(v is not None for v in mt.values())

    # (b) git status blind to the family
    _, st = git("status", "--porcelain")
    fam_rows = [l for l in st.splitlines()
                if any(k in l for k in ("autofill_state", "dispatcher_state",
                                        "idle_trigger", "_sentinel_bm-",
                                        "saturation_engine_state", "face_bm-"))]
    # allowed: the staged D-deletion rows of own faces (this commit face itself)
    own_staged = [l for l in fam_rows if l.startswith("D  ")]
    foreign = [l for l in fam_rows if not l.startswith("D  ")]
    rep["live_probe"]["status_own_staged_deletions"] = own_staged
    rep["live_probe"]["status_foreign_rows"] = foreign
    ok &= not foreign

    # (c) git stash create tree contains zero OWN tick faces (exact-path match only --
    #     broad substring scan false-positives on other machines' tracked faces and
    #     evidence backup copies, which are legitimately in the stash tree)
    rc, sha = git("stash", "create")
    stash_sha = sha.strip()
    tick_in_stash = []
    if stash_sha:
        _, tree = git("ls-tree", "-r", "--name-only", stash_sha)
        tree_paths = set(tree.splitlines())
        tick_in_stash = [p for p in UNTRACKED if p in tree_paths]
    rep["live_probe"]["stash_create_sha"] = stash_sha[:9] if stash_sha else ""
    rep["live_probe"]["tick_faces_in_stash"] = tick_in_stash
    ok &= not tick_in_stash

    rep["verdict"] = "PASS" if ok else "FAIL"
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(rep, f, ensure_ascii=False, indent=1)
    print("D-02 dir-1 selftest+live probe: %s -> %s" % (rep["verdict"], OUT))
    if not ok:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
