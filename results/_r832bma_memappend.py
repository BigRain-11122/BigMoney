# -*- coding: utf-8 -*-
"""r832 S4 memory writes (multi-writer files: python fresh-read-modify-write law).
1) METHODOLOGY_ASSETS.md card E42 (writer-pause window method)
2) CODELY.md one pit line (rebase vs continuous daemon writers)
Also: treasure-check = zero new treasure (staircase 36th = E36 already registered)."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- 1. METHODOLOGY_ASSETS.md card E42 ---------------------------------------
mp = os.path.join(ROOT, "knowledge", "METHODOLOGY_ASSETS.md")
m = open(mp, encoding="utf-8").read()
card = """

## E42 — Writer-Pause Window（daemon 活写阻断 rebase 的让路法）

**场景**：三机共享仓 pull --rebase 时，本机后台 daemon（饱和引擎烧分片/autofill/pool_worker/
dispatcher）以分钟级持续写 tracked 共享面文件。`git rebase --continue` 需要净树，
活写使 pick 反复失败并进入 reschedule 循环（done 文件堆积重复 pick 项、msgnum/end 失配、
"staged changes"/"must edit merge conflicts" 提示误导）。

**方法**：
1. 诊断面：`git diff --name-only` + 文件 mtime 连续观测确认 daemon 是写入源；
   `git status` 提示 "you have staged changes ... git commit" = editing-stop 态真错误
   （被 Select-Object 截断吃掉时用 Out-String 全量打印拿真错误）。
2. 让路面：临时 Disable 本机 4 个写盘计划任务（SatEngine/Autofill/PoolWorker/
   ResidentDispatcher，经 Invoke-SilentExe 包装·U060 零窗律）；
3. 静窗内完成 absorb+continue+冲突解（22-UU 批=ALL_FACES resolver+手解件）；
4. rebase 落地后立即 ENABLE 全部恢复（队列态在文件面持久，暂停只延迟烧录零损失）；
5. untracked 撞重放（引擎新写分片）按 r220 律 TEMP 暂移，回移前与重放侧做
   EQUAL-EXCEPT-ELAPSED 断言（确定性再烧=科学面恒等，仅 wall-clock 元数据差）。

**判据/先例**：r832 bm-a 实弹（W175 烧录期 origin 双机抢道 rebase 全链治愈，behind 0 送达）；
禁用于 CEO 用机让路律场景（那是 machine-state.ps1 -Mode pause 的域）。
"""
if "E42" not in m:
    open(mp, "a", encoding="utf-8").write(card)
    print("METHODOLOGY_ASSETS: E42 card appended")
else:
    print("METHODOLOGY_ASSETS: E42 already present, skip")

# --- 2. CODELY.md pit line (one line, entry-gate four-questions passed) --------
cp = os.path.join(ROOT, "CODELY.md")
c = open(cp, encoding="utf-8").read()
pit = ("\n- [2026-10-07 16:3x r832 bm-a] **daemon 活写阻断 rebase 的 writer-pause 让路法（r832 S0 实弹·S6 22-UU 批治愈）**：共享仓 rebase 期间本机 daemon 分钟级活写 tracked 面（引擎烧分片 tick 级写 face/ledger）→ pick 反复失败进 reschedule 循环（done 文件重复堆积+「staged changes」提示真错误被管道截断吞掉）；正法=临时 Disable 本机写盘 schtasks（SatEngine/Autofill/PoolWorker/ResidentDispatcher·经 Invoke-SilentExe）静窗完成 rebase 后立即 ENABLE（队列态文件面持久零损失·E42 卡）；untracked 撞重放按 r220 TEMP 暂移+回移前 EQUAL-EXCEPT-ELAPSED 断言（确定性再烧仅 wall-clock 差）。How to apply：rebase continue 连续假冲突报先查 daemon mtime 连续性；诊断用 Out-String 全量打印勿 Select-Object 截断。\n")
if "writer-pause" not in c:
    open(cp, "a", encoding="utf-8").write(pit)
    print("CODELY: pit line appended")
else:
    print("CODELY: pit already present, skip")
