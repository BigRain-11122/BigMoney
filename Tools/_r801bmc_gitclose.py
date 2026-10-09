# -*- coding: utf-8 -*-
"""r801 bm-c git closeout: targeted add (own faces only) -> commit ->
fetch -> rebase-absorb behind -> push (CAS semantics; branch fallback per
D-20260925-01-3) -> fetch-verify -> post-push state sync fields.
Laws: r642 clean-tree no-autostash, r863 churn window, r794 targeted add,
r801/r723 stdout contract (stdout-only porcelain reads)."""
import json
import os
import subprocess
import sys
import time

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
ROUND = 801
MSG = ("round 801: dead-session adoption closeout + CEO-order-3 design doc v0.1 "
       "(PARKING_P1 engine leg) + QA r801 5/5 + S6 40/40 (22nd green) + DEC/ORD "
       "consumed (D-20261009-04 bigmoney items closed, 4 si-mian flips) [via bm-c]")


def git(args, want_err=False):
    p = subprocess.run(["git", "-C", REPO] + args, capture_output=True,
                       creationflags=CNW)
    out = p.stdout.decode("utf-8", "replace")
    err = p.stderr.decode("utf-8", "replace")
    return p.returncode, (out + (("\n[stderr]\n" + err) if want_err else "")), err


def status_list():
    rc, out, _ = git(["status", "--porcelain=v1"])
    files = []
    for line in out.splitlines():
        if not line.strip():
            continue
        st, path = line[:2], line[3:].strip().strip('"')
        files.append((st, path))
    return rc, files


# --- classify: every dirty face must be bm-c-owned ---
rc, files = status_list()
foreign = [p for st, p in files if p.startswith("Money02/") or p.startswith("legacy/")]
if foreign:
    print("FOREIGN faces present, ABORT: %s" % foreign)
    sys.exit(2)
paths = [p for _, p in files]
print("dirty_n=%d (all own classification)" % len(paths))

# --- targeted add + commit (retry once on index race with autofill r290) ---
for attempt in (1, 2):
    if paths:
        rc, out, err = git(["add", "--"] + paths, want_err=True)
        if rc != 0:
            print("add attempt %d rc=%d: %s" % (attempt, rc, out[-400:]))
            time.sleep(3)
            rc, files2 = status_list()
            paths = [p for _, p in files2]
            continue
    rc, out, err = git(["commit", "-m", MSG], want_err=True)
    if rc == 0:
        rc2, head, _ = git(["rev-parse", "--short", "HEAD"])
        print("commit ok: %s" % head.strip())
        break
    print("commit attempt %d rc=%d: %s" % (attempt, rc, out[-500:]))
    time.sleep(3)
    rc, files2 = status_list()
    paths = [p for _, p in files2 if not p.startswith("results/_r801bmc_close")]
else:
    print("commit FAILED after retries")
    sys.exit(3)

# --- fetch + absorb behind (clean tree; churn-wave quick absorb if dirty) ---
def absorb_and_push(tag):
    for _ in range(3):
        rc, out, _ = git(["fetch", "origin"])
        rc, cnt, _ = git(["rev-list", "--count", "main..origin/main"])
        behind = int(cnt.strip() or 0)
        if behind == 0:
            break
        # tree must be clean for rebase (r642); churn-dirt -> quick absorb commit
        rc, st, _ = git(["status", "--porcelain=v1"])
        if st.strip():
            dirt = [l[3:].strip().strip('"') for l in st.splitlines() if l.strip()]
            git(["add", "--"] + dirt)
            git(["commit", "-m", "round 801: absorb daemon live faces (churn wave, pre-rebase) [via bm-c]"])
        rc, out, err = git(["pull", "--rebase"], want_err=True)
        if rc != 0:
            rc, uu, _ = git(["ls-files", "-u"])
            if uu.strip():
                print("REBASE UU faces -- resolver required, ABORT push for manual step")
                print(uu)
                sys.exit(4)
            print("rebase rc=%d: %s" % (rc, out[-400:]))
            sys.exit(5)
        rc2, head, _ = git(["rev-parse", "--short", "HEAD"])
        print("[%s] absorbed behind=%d, tip=%s" % (tag, behind, head.strip()))
    # push (plain push = CAS semantics: fails if origin moved meanwhile)
    rc, out, err = git(["push", "origin", "main"], want_err=True)
    if rc == 0:
        return True, out
    print("push rejected: %s" % out[-400:])
    return False, out


ok, _ = absorb_and_push("try1")
if not ok:
    ok, _ = absorb_and_push("try2")
if not ok:
    # law fallback: push origin machine/bm-c-r801 branch, note in report
    rc, out, err = git(["push", "origin", "main:refs/heads/machine/bm-c-r801"], want_err=True)
    print("branch fallback rc=%d: %s" % (rc, out[-300:]))
    sys.exit(6)

# --- delivery self-verify (push+fetch, ahead/behind must be 0/0) ---
git(["fetch", "origin"])
rc, ab, _ = git(["rev-list", "--left-right", "--count", "main...origin/main"])
ahead, behind = [int(x) for x in ab.split()]
rc, head, _ = git(["rev-parse", "HEAD"])
head = head.strip()
print("DELIVERY: ahead=%d behind=%d head=%s" % (ahead, behind, head[:10]))
if ahead != 0 or behind != 0:
    print("delivery NOT clean")
    sys.exit(7)

# --- post-push state sync fields (stay in tree; next-round S0 absorbs) ---
NOW = time.strftime("%Y-%m-%dT%H:%M:%S+08:00", time.localtime())
sp = os.path.join(REPO, "state-bm-c.json")
d = json.load(open(sp, encoding="utf-8"))
d["head_sha"] = head[:10]
d["last_pulled_at"] = NOW
d["sync"] = {"ahead": 0, "behind": 0, "last_push_ts": NOW,
             "note": ("r801 post-push delivery self-verified ahead=0/behind=0 via "
                      "fetch+rev-list; two-wave adoption round: 11:55 session "
                      "(r800 estate absorb 7e75ee831 + 19-UU rebase resolve) died "
                      "mid-S7 12:04; 12:15 session finished closeout (design doc "
                      "v0.1 + QA + commit + push)")}
with open(sp, "w", encoding="utf-8") as fh:
    json.dump(d, fh, indent=1, ensure_ascii=False)
print("state sync fields written (post-push, in-tree per pattern)")
