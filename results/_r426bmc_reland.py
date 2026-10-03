# -*- coding: utf-8 -*-
"""r426 bm-c surgical re-land: push-collision + open-handle-blocked rebase pick heal.

Facts: commit 9bbe943638 (r426 closeout) built on 7868c927a; origin advanced to
bm-a r639+addendum. pull --rebase pick blocked by
results/_r426bmc_w2_judge_finalize_log.txt held OPEN by the live detached
judge-finalize burn (unlink EINVAL at base checkout -> file survives as
untracked -> pick refuses to overwrite). No content was merged; pick was
rescheduled and aborted.

Law path: r630 isolated-worktree net lane (origin base checkout + per-face
origin/mine triage: intersection -> origin newer-wins for shared regen faces;
mine-only -> mine) + r624 rebase --quit detached-HEAD heal (branch -f +
checkout). The log receipt is DEFERRED to r427 (open handle; identical 1-line
content on disk; burn releases it at completion).
"""
import datetime
import json
import os
import subprocess
import sys

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
WT = r"K:\Fluxgroup\FluxGroup\quant\_r426bmc_wt"
MINE = "9bbe943638d72de57699727d1ba0364c05cd9089"
LOG = "results/_r426bmc_w2_judge_finalize_log.txt"
MSG = ("round 426 closeout (bm-c): dead-session adoption -- wave-2 judge 4/4 flip "
       "re-verified (805/805 rows on origin; SHARD-1 bb9a5882e) + judge-finalize "
       "burn in flight (detached 19:28:59, r427 polls+adopts) + S0 integrate "
       "(11-commit FF 7868c927a + bm-a r639 pair re-land triage) + smoke 47/47 + "
       "S6 37 legs rc0 + S7 4/4 green + CODELY r426 flash-guard law "
       "(re-landed on origin tip via isolated worktree r630 net lane; "
       "finalize-log receipt deferred to r427 per open-handle) [via bm-c]")


def git(args, cwd=REPO, check=True):
    # NO creationflags: parent chain holds the loop's hidden console; commit/push
    # hooks MUST inherit it (r426 flash-guard law).
    p = subprocess.run(["git"] + args, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", cwd=cwd)
    if check and p.returncode != 0:
        sys.exit("GIT FAIL %s -> %s" % (args[:4], (p.stdout or "") + (p.stderr or "")))
    return p.returncode, (p.stdout or "") + (p.stderr or "")


# 0) preconditions: detached mid-rebase, tip known
rc, out = git(["rev-parse", "origin/main"])
tip = out.strip()
rc, out = git(["rev-parse", "--abbrev-ref", "HEAD"])
assert out.strip() == "HEAD", "expected detached HEAD, got %s" % out.strip()
assert os.path.isdir(os.path.join(REPO, ".git", "rebase-merge")), "rebase state gone"
rc, out = git(["merge-base", MINE, tip])
pre = out.strip()
print("PRECONDITIONS ok: mine=%s base(pre)=%s tip=%s" % (MINE[:9], pre[:9], tip[:9]))

# 1) quit the dead rebase (r624 law)
git(["rebase", "--quit"])
print("rebase --quit done")

# 2) face triage (mechanical, no per-file judgment)
_, my_raw = git(["diff-tree", "--no-commit-id", "--name-only", "-r", pre, MINE])
_, bma_raw = git(["diff-tree", "--no-commit-id", "--name-only", "-r", pre, tip])
my = set(l.strip() for l in my_raw.splitlines() if l.strip())
bma = set(l.strip() for l in bma_raw.splitlines() if l.strip())
take_origin = sorted(my & bma)
take_mine = sorted(my - bma - {LOG})
print("TRIAGE: my=%d bma=%d take_origin=%d take_mine=%d (log deferred)"
      % (len(my), len(bma), len(take_origin), len(take_mine)))
print("TAKE_ORIGIN: %s" % json.dumps(take_origin))
print("TAKE_MINE: %s" % json.dumps(take_mine))

# 3) isolated worktree at tip
if os.path.exists(WT):
    git(["worktree", "remove", "--force", WT], check=False)
git(["worktree", "add", "--detach", WT, tip])
print("worktree ready at tip")

# 4) materialize my faces into worktree (from MY commit blobs)
if take_mine:
    git(["checkout", MINE, "--"] + take_mine, cwd=WT)

# 5) round-report addendum (leave-trace, r639 addendum precedent)
ts = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
add = ("%s addendum: push撞拒+rebase pick 被在飞烧批握持的 log 开放句柄挡停（unlink EINVAL）"
       "→ r630 隔离 worktree 净路重落（take-origin %d 件=bm-a r639 CEO 面·origin 新者胜；"
       "take-mine %d 件=本机面+收据+state 件；log 收据件让位烧批柄·随 r427 产品批入册）"
       "+ branch -f/checkout 治愈 + delivery 自证 [via bm-c]\n")
with open(os.path.join(WT, "round_reports-bm-c.md"), "a", encoding="utf-8") as fh:
    fh.write(add % (ts, len(take_origin), len(take_mine)))

# 6) commit in worktree (hooks run in inherited hidden console)
git(["add", "-A"], cwd=WT)
git(["commit", "-m", MSG], cwd=WT)
_, sha2 = git(["rev-parse", "HEAD"], cwd=WT)
sha2 = sha2.strip()
print("RELANDED %s" % sha2)

# 7) push (fast-forward from tip; CAS semantics)
rc, out = git(["push", "origin", "HEAD:main"], cwd=WT, check=False)
print("PUSH rc=%d %s" % (rc, out.strip()[:300]))
if rc != 0:
    sys.exit("PUSH REJECTED -- worktree kept at %s for manual redo" % WT)

# 8) heal main repo (r624 detached-HEAD law)
git(["checkout", "--", "results/saturation_engine/face_bm-c.json"], check=False)
git(["branch", "-f", "main", sha2])
git(["checkout", "main"])
git(["worktree", "remove", "--force", WT], check=False)

# 9) delivery self-verify + post-heal status
git(["fetch", "origin"])
_, cnt = git(["rev-list", "--count", "HEAD..origin/main"])
_, st = git(["status", "--porcelain"])
print("DELIVERY behind=%s" % cnt.strip())
print("POST-HEAL STATUS:\n%s" % st)
print("RELAND_OK sha2=%s" % sha2)
