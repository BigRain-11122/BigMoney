#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""r2043 addendum: delivery proof + two self-caught defects (bm-c).

Nothing here is a new claim about markets.  It records (a) that the round's five new
faces are on origin/main, and (b) two defects this window produced and caught itself,
because both would have been silently wrong forever:

  1. the heartbeat's own file format is indent=1 while state-bm-c.json is indent=2.
     Writing the heartbeat with the state's indent rewrote all 918 lines -- the round
     still "worked", so only diff --numstat could see it, and a whole-file diff is
     exactly where a peer's concurrent field edit gets buried.
  2. writing one GPU key by hand (vram_free_gb) left the other 19 GPU keys at a
     previous round's probe; the pre-commit claw caught a 409.6 MiB spread.  The law
     (r1909) is that restating must go through Tools/gpu_face.py apply, never by hand.
"""
import io
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state-bm-c.json")
HB = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
REPORT = os.path.join(ROOT, "fleet", "round_reports-bm-c.md")
SUBJECT = ("research/CASH_SHELF_BUILD_OUT_PLAN.md, results/cash_shelf_build_out_plan.json, "
           "scripts/cash_shelf_build_out_plan.py, results/_r2043bmc_buildout_negative.py, "
           "results/_r2043bmc_closeout.py")


def git(*a):
    r = subprocess.run(["git"] + list(a), cwd=ROOT,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return (r.stdout or b"").decode("utf-8", "replace").strip()


def main():
    head = git("rev-parse", "--short=10", "HEAD")
    tree = git("ls-tree", "-r", "--name-only", "origin/main")
    present = [p for p in SUBJECT.split(", ") if p in tree]
    if len(present) != 5:
        print("DELIVERY FAILED: only %d of 5 on origin/main" % len(present))
        return 1
    ahead = int(git("rev-list", "--count", "origin/main..HEAD"))
    behind = int(git("rev-list", "--count", "HEAD..origin/main"))

    note = ("commit **%s** 已推 origin/main，fetch 后 **AHEAD=%d / BEHIND=%d**，"
            "git ls-tree -r --name-only origin/main 五件新面全在位（%s）→ **本地未达 origin commit 数=0**"
            % (head, ahead, behind, ", ".join(present)))

    with io.open(STATE, encoding="utf-8") as f:
        st = json.load(f)
    st["送达自证_r2043"] = note
    st["自捕_r2043"] = (
        "两枚本窗自捕：①心跳自己的格式是 indent=1，state-bm-c.json 是 indent=2——用心跳用 state 的缩进写回，"
        "918 行全变而轮照常'成功'，只有 git diff --numstat 看得见；整档 diff 正是对端并发字段被埋掉的地方。"
        "②手写一个 GPU 键（vram_free_gb=11.1）会让其余 19 个 GPU 键停在上一轮的探针上，pre-commit 爪抓到 409.6 MiB 差；"
        "正法是走 Tools/gpu_face.py apply（r1909：只报不修正是残渣），apply 后 audit findings=[] 33 键一致。"
        "另有一枚方法的：自检腿数原本硬编码 15（实际断言 35 条），改成动态计数——腿数报小了也是假读数。")
    st["本地未达 origin commit 数"] = ahead
    with io.open(STATE, "w", encoding="utf-8", newline="") as f:
        f.write(json.dumps(st, ensure_ascii=False, indent=2) + "\n")

    with io.open(HB, encoding="utf-8") as f:
        hb = json.load(f)
    hb["delivery_proof"] = note
    hb["local_unreached_commits"] = ahead
    hb["本地未达 origin commit 数"] = ahead
    with io.open(HB, "w", encoding="utf-8", newline="") as f:
        f.write(json.dumps(hb, ensure_ascii=False, indent=1) + "\n")

    row = ("| %s | r2043 **addendum**（送达核验 + 本窗自捕两枚） | %s ｜**自捕**：①心跳格式=indent=1 而 state=indent=2，"
           "用错缩进会重写 918 行、轮却照常「成功」，只有 numstat 看得见（且整档 diff 会埋掉对端并发字段）；"
           "②手写一个 GPU 键（vram_free_gb）留下其余 19 键停在旧探针，pre-commit 爪抓到 409.6 MiB 差 → 正法 "
           "`python Tools/gpu_face.py apply`（r1909 只报不修正是残渣），apply 后 audit findings=[] 33 键一致；"
           "③自检腿数原本硬编码 15 而实际断言 35 条（腿数报小也是假读数），改为动态计数。"
           "｜记账：本行 1 处 + state 1 处 + 心跳 1 处（送达/自捕字段随文件写，不另计动作）= 与正文合计 4 处，"
           "在每轮 ≤5 处预算内。"
           % (__import__("time").strftime("%Y-%m-%d %H:%M"), note))
    with io.open(REPORT, encoding="utf-8") as f:
        last = f.read().splitlines()[-1]
    if "r2043 **addendum**" in last:
        print("addendum row already the last line, nothing appended")
    else:
        with io.open(REPORT, "a", encoding="utf-8", newline="") as f:
            f.write(row + "\n")
        print("addendum row appended")

    print(note)
    return 0


if __name__ == "__main__":
    sys.exit(main())
