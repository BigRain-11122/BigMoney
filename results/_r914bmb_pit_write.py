# r914 bm-b: direct-write new pit to research/pit-spawn.md (r666 precedent, family=root cause home)
# + round-report rider line (delivery self-proof + stash note). Post-split convention.
import hashlib

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
PIT = ROOT + r"\research\pit-spawn.md"
REP = ROOT + r"\logs\iteration-loop\round_reports.md"

entry = (
"- [2026-10-13 03:5x r914 bm-b] **长批重定向日志锁柄封死 rebase/checkout 面（正法=merge in-place 整合+per-face 解冲突）**："
"pythonw 以 Start-Process -RedirectStandardOutput 起长批（README-RUN 正法形态的暗面）=进程终身持日志文件句柄→"
"批在飞期间凡需改写该文件于工作树的 git 操作全灭：rebase 起手 checkout 报 'unable to unlink ... Invalid argument'、"
"反复 'cannot pull with rebase: You have unstaged changes' 死环（rider 即收即被 15s tick 再污）、stash push 与 pop 双拒"
"（pop 后 'stash entry kept' 遗留）；skip-worktree 掩码也救不了 rebase（HEAD vs origin 两版内容差仍拒 'would be overwritten by checkout'）。"
"正法=git merge origin/main in-place：锁柄文件为我方独改面→merge 结果==HEAD 版=零工作树触碰，锁柄不参与写入；"
"合并冲突按面语义逐面解（fleet/machine-health.json=每机 oversight 单槽互覆写竞态→union 双机条目保零丢失；"
"纯证据面 _attrition_guard_scan/_r686bmb_d19_check/compute_audit=newer-wins 取 HEAD）——勿整树 --ours 一刀切。"
"How to apply：长批重定向日志面=轮内只 commit 快照勿 stash 勿 pop；'cannot pull with rebase' 死环+unlink 拒=判锁柄→"
"转 merge in-place 整合（同守禁强推律·pre-push 爪对陈旧基座推送的删除集拦截是正确防线勿绕）。"
)

acc = (
"> 直写行（r914 bm-b·post-split convention direct-write·根因归族=spawn 持柄族而非 git 域件〔pit-git.md 余量 1256B 不足装〕）："
"+1 条（长批重定向日志锁柄封死 rebase 面·merge in-place 正法）路追加核 %d B（LF blob 净·md5=%s）；件尾整行追加·件内对账行为准。\n"
)

blob = entry.encode("utf-8")
md5 = hashlib.md5(blob).hexdigest()
size = len(blob)

with open(PIT, "a", encoding="utf-8", newline="\n") as f:
    f.write(entry + "\n")
    f.write(acc % (size, md5))

rider = (
"2026-10-13T04:05+08:00 | r914 rider3 [dept:eng/fleet] | DELIVERY SELF-PROOF: push 253da50b6 landed on origin/main, "
"post-push fetch+rev-list behind=0 ahead=0 (zero unreached) -- NOTE path taken: rebase physically blocked by i2v driver's "
"redirected-log file handle (unlink refused), integrated via git merge in-place + per-face conflict resolution "
"(machine-health union bmb+bmc / 3 evidence faces newer-wins); new pit direct-written to research/pit-spawn.md per r666 "
"precedent; stash@{0} 'r914 lane churn' left in place (obsolete driver-log snapshot, safe to drop next round after "
"batch exit); remote URL shows 'repository moved' notice (bigmoney->BigMoney, redirect works, harmless). | "
"evidence: git push output f3aceee73..253da50b6 + rev-list 0/0 | next: r915 as recorded in r914 line\n"
)
with open(REP, "a", encoding="utf-8", newline="\n") as f:
    f.write(rider)

import os
print("PIT_APPENDED bytes=%d md5=%s" % (size, md5))
print("PIT_FILE_SIZE=%d" % os.path.getsize(PIT))
print("RIDER_APPENDED")
