# -*- coding: utf-8 -*-
# r611 bm-a r589 unwind-FF-reland loop: push rejected (origin advanced 2 =
# bm-c r399/r400). Sequence: reset --mixed HEAD~1 -> per-face restore ->
# ff-only merge (fresh rev-parse r593 law) -> idempotent re-apply (wiring
# script + E15 append) -> regen build_status -> re-add/re-commit/push.
# Shared derive faces taken origin-verbatim (bm-c fresher regen);
# append-only faces union via idempotent anchored re-apply (E15/r611 law).
import os
import subprocess
import sys

PY = sys.executable
ROOT = os.getcwd()


def git(args, **kw):
    r = subprocess.run(["git"] + args, capture_output=True,
                       encoding="utf-8", errors="replace", cwd=ROOT, **kw)
    if r.returncode != 0:
        print("GIT FAIL:", args, "\nSTDERR:", (r.stderr or "")[-500:])
        sys.exit(1)
    return r.stdout


def git_ok(args):
    r = subprocess.run(["git"] + args, capture_output=True,
                       encoding="utf-8", errors="replace", cwd=ROOT)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


# 0. sanity: exactly one unpushed commit
ahead = git(["rev-list", "--count", "origin/main..HEAD"]).strip()
assert ahead == "1", "expected exactly 1 unpushed commit, got %r" % ahead
my_commit = git(["rev-parse", "HEAD"]).strip()
print("unpushed commit:", my_commit[:12])

# 1. unwind
print(git(["reset", "--mixed", "HEAD~1"]).strip() or "reset done")

# 2. compute sets
origin_side = set(git(["diff", "--name-only", "HEAD", "origin/main"]).split())
porc = git_ok(["status", "--porcelain"])[1]
tracked_dirty, untracked = set(), set()
for line in porc.splitlines():
    if not line.strip():
        continue
    st, path = line[:2], line[3:].strip()
    if st.strip() == "??":
        untracked.add(path)
    else:
        tracked_dirty.add(path)
print("origin_side:", len(origin_side), "tracked_dirty:", len(tracked_dirty),
      "untracked:", len(untracked))

conflict_tracked = sorted(tracked_dirty & origin_side)
clash_untracked = sorted(untracked & origin_side)
print("conflict_tracked:", conflict_tracked)
print("clash_untracked:", clash_untracked)

# 3. restore conflict tracked to base (clean for FF; mine re-applied later
#    via idempotent wiring for code/law faces, origin stands for derive faces)
if conflict_tracked:
    print(git_ok(["checkout", "--"] + conflict_tracked)[1].strip() or "checkout ok")

# 4. remove untracked clash files (both-new in window; take origin version)
for p in clash_untracked:
    os.remove(p)
    print("removed local untracked clash:", p)

# 5. ff-only merge with execution-time fresh rev (r593 law)
rev = git(["rev-parse", "origin/main"]).strip()
print("ff target:", rev)
rc, out = git_ok(["merge", "--ff-only", rev])
print("merge:", out.strip()[-200:])

# 6. idempotent re-apply of my faces (wiring: iteration_prompt law +
#    build_status func/wire + dashboard render; skips already-present)
r = subprocess.run([PY, r"results\_r611bma_family_verdict_wiring.py"],
                   capture_output=True, encoding="utf-8", errors="replace",
                   cwd=ROOT)
print("wiring re-apply rc=%d" % r.returncode)
print((r.stdout or "").strip())

# 7. E15 append re-apply if absent (union with bm-c same-window cards)
p = os.path.join("knowledge", "METHODOLOGY_ASSETS.md")
with open(p, "rb") as f:
    data = f.read()
if b"**E15 reland" not in data:
    CARD = (
        "- **E15 reland/外科重放环共享池面=per-face max-merge vs origin blob 律**"
        "（proven）：撤-FF-重落/外科重放环的 payload 含共享池面"
        "（runnable_pool.json/crash_fuse.json/pool 车道镜像族）时禁整文件重放"
        "——环内工作树快照天然滞后于中窗 origin 前进（他机 keepalive/settle "
        "同窗竞态），整文件重放=把陈旧 owner_since/cleared_ts 时间戳写回鲜基"
        "（实弹：NULLS owner_since 05:48:07→05:28:07 回退 20min→破 20min "
        "stale-claim 接管门→7.6min 假接管评估窗·crash fuse 侥幸拦截零双烧）。"
        "正法两选一=①重放前对该面 per-face max-merge vs origin blob"
        "（时间戳字段 newer-wins）②重放后立刻 python scripts\\merge_lane_views.py"
        " sync_face 幂等补 settle（newer-wins 已内建）；护栏三件=迭代律行"
        "（iteration_prompt S0）+认领面 origin-ref 前读双查（r608 daemon 腿）"
        "+push 前 owner_since 单调门（bm-c 爪域提案②·r400 已落地）。证据："
        "MSG-2026-10-03-0612 事故通报+bm-a r611 立法实弹"
        "（origin NULLS 复核 2026-10-03 06:18:07 新鲜·iteration_prompt S0 律行落地）。\r\n"
        "- 2026-10-03 06:4x（bm-a r611·MSG-0612 提案①受理·reland 环重放补落）："
        "捕获律 append E15 reland 共享池面 max-merge 律（MSG-2026-10-03-0612 "
        "实弹事故·提案① bm-a 面·r589 环内 union 重放）。\r\n"
    ).encode("utf-8")
    with open(p, "ab") as f:
        f.write(CARD)
    print("E15 re-appended +%d" % len(CARD))
else:
    print("E15 already present")

# 8. regen build_status on merged tree (family_verdicts face + fresh numbers)
r = subprocess.run([PY, "-m", "monitor.build_status"],
                   capture_output=True, encoding="utf-8", errors="replace",
                   cwd=ROOT)
print("build_status rc=%d :: %s" % (r.returncode, (r.stdout or "").strip()[-120:]))
assert r.returncode == 0

# 9. re-add + staged-D assertion (only the intentional MSG-0612 paired move)
git(["add", "-A"])
porc2 = git_ok(["status", "--porcelain", "--untracked-files=no"])[1]
d_lines = [l for l in porc2.splitlines() if "D" in l[:2] and l.strip()]
print("staged D lines:", d_lines)
for l in d_lines:
    assert "MSG-2026-10-03-0612-bmb-all" in l, "unexpected D row: %r" % l
print("D assertion PASS (paired move only)")
print("RELAND LOOP PREP DONE")
