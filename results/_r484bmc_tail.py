"""r484 bm-c final tail: supplementary round-report line + CODELY pit line
(locked-log-blocks-rebase / add-then-reset technique), marker-gated appends."""
import datetime
import os

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CODELY = os.path.join(REPO, "CODELY.md")
REPORT = os.path.join(REPO, "round_reports-bm-c.md")

now_iso = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
now_ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 1. CODELY pit line (marker gate: r484bm-c tail marker)
codely = open(CODELY, "rb").read().decode("utf-8")
assert codely.count("r484 bm-c") == 1, f"expected 1 r484 entry, got {codely.count('r484 bm-c')}"
pit = ("- [2026-10-04 17:1x r484 bm-c] 活进程持握日志文件阻塞 rebase/reset 坑+add-then-reset 技法"
       "（收口窗实弹：judge-prep 分离子进程以追加模式持握自日志句柄，push-race 后 pull --rebase 的"
       " pick/abort/reset --hard 全序列在该文件上 unlink 失败〔Invalid argument·Windows 删除共享位〕"
       "——untracked+locked 文件卡死整棵树手术；r624 治愈律〔rebase --quit+symbolic-ref+branch -f〕"
       "只救 aftermath 不解锁文件。正法=①blob 恒等时先 `git add <锁文件>`（add=只读·index 获与目标"
       "一致的 stat 缓存）→ `reset --hard` 对该路径零写零删需求即通过；②净路选择=r437 ④ merge 合法"
       "优于 rebase（三方 merge 不触单侧独有文件）；③收口窗 UU=r440 per-face ts 探针 newer-wins"
       "（本窗反直觉：双机同 canon S6 链 13min 偏移·ours 16:35 vs theirs 16:22=29 面 ours 胜·禁凭"
       "「origin 必新」直觉盲取 theirs）。How to apply：分离 spawn 长批的自日志文件=潜在 git 树手术"
       "阻塞面，收口 push-race 窗先探活进程；树手术撞锁文件按 add-then-reset 技法+merge 净路，"
       "禁反复 abort/reset 重试。\n")
with open(CODELY, "ab") as f:
    f.write(pit.encode("utf-8"))
codely2 = open(CODELY, "rb").read().decode("utf-8")
assert codely2.count("r484 bm-c") == 2
print("CODELY pit line appended (2 r484 entries total)")

# 2. round report supplementary line (marker gate)
rep = open(REPORT, "rb").read().decode("utf-8")
assert rep.count("r484 bm-c S7-close") == 1
supp = (
    f"{now_iso}｜r484 bm-c 收口补行（push-race 后半场实录·零 origin 伤害·全程 claw 零 --no-verify）"
    "｜close commit 66bdc7d07 首推被拒（origin 窗内进 2：bm-b r288 keepalive 8e740ca69+其 merge "
    "b67966f6e 已并我冻结件）→pull --rebase 三连被 daemon treadmill（autofill/saturation 40s 复写）"
    "与 prep 活进程锁日志文件卡死（unlink Invalid argument·pick/abort/reset 全阻）→r624 治愈律"
    "（rebase --quit+symbolic-ref 重挂 main=a3a4b56b8 完好）+add-then-reset 技法（锁文件 blob 恒等"
    "先 add 建 stat 缓存→reset --hard 零 unlink 通过）→r437 ④ merge 净路：30 UU=r440 per-face ts "
    "探针 newer-wins（29 S6 再生面 ours 16:35 vs theirs r686 16:22·反直觉禁盲取 theirs）+token "
    "per-key union side_pick=2（r456 律）+CODELY 块级 union（theirs 全文+我 1 真新增行·r675 配方）"
    "→merge commit 91abdbb45→push_verify DELIVERED tip==remote ahead=0/behind=0｜新坑律 2 条入 "
    "CODELY（追加节冻结复跑禁向闸+锁文件 add-then-reset）｜prep 态=分离在飞（日志块缓冲零追加="
    "尾部单行打印正常面·产物 w3_judge_state.json 未落=带外·r485 收养先例不变）"
    "｜本地未达 origin commit 数=0（push_verify 实证）\n")
with open(REPORT, "ab") as f:
    f.write(supp.encode("utf-8"))
rep2 = open(REPORT, "rb").read().decode("utf-8")
assert rep2.count("r484 bm-c 收口补行") == 1
print("round report supplementary line appended")
print("TAIL_DONE")
