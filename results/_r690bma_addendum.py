# -*- coding: utf-8 -*-
"""r690 bm-a round report addendum (closeout waves; bytes append, marker idempotence)."""
REPORT = "round_reports-bm-a.md"
marker = "| r690 (bm-a) addendum"
raw = open(REPORT, "rb").read()
assert raw.count(marker.encode("utf-8")) == 0, "addendum already present"

line = (
"2026-10-04T18:4x+08:00 | r690 (bm-a) addendum | CLOSEOUT WAVES (three push-race waves, zero "
"--no-verify, both claw-blocks honored): wave-1 = closeout push rejected twice (bm-b/bm-c "
"treadmill) -> merge origin -> 15 S6 regen faces UU (bm-b wave) -> per-face ts resolver "
"(_r690bma_merge_resolve.py·12 ours-newer 18:2x + LIVE md twins aligned ours + crash_fuse "
"theirs) -> merge commit 1428b683b; wave-2 = pre-push claw BLOCK #1 (7x _r488bmc_* "
"no-owner-evidence = bm-c r488 wave landed origin AFTER my fetch = deletion-set FALSE face, "
"claw working as designed, r689 addendum-2 same-type) -> fetch+merge absorb wave -> 1 UU "
"update_status.json resolved theirs 18:27:59 newer (_r690bma_merge_resolve2.py) -> commit; "
"wave-3 = leg-2 merge carried 13 MORE UU regen faces (bm-c r488 S6 regen wave ts "
"18:27:5x-18:29:47 uniformly newer than my 18:26-18:28 run) -> all-13 theirs per ts-freshness "
"(_r690bma_merge_resolve3.json·zero-loss regen snapshots·json reparse proof per face) -> "
"merge 87b71c60e -> PUSH DELIVERED 1906d7ae6..87b71c60e (ahead=0, ls-remote==HEAD "
"self-proof) | 自犯自愈实录: wave-2 merge 报文被 Select-Object -Last 2 截断=只显 1 条 CONFLICT "
"行，实际 14 UU（r657-①管道尾窗律重犯·markers 全仓扫当场抓回·零 staged 污染零 origin 伤害）| "
"记分修正: r690 final = 2 (等待态值守 + 收口三波 canon 解面=可验证协调/证据实物；判决产品仍在飞 "
"bm-c 手) | 本地未达 origin commit 数: 0 (DELIVERED 87b71c60e 自证) | 登记簿零命中断言: 本轮零清扫/零归档/"
"零删除/零恢复类动作 (probes read-only + regen faces + MSG 落盘) | 承接判定: 无新方法论 (per-face "
"ts resolver=r440/r461/r484 既有律复用；claw 假删除面=r689 addendum-2 既有型复发自愈)"
)
with open(REPORT, "ab") as fh:
    fh.write(line.encode("utf-8"))
    fh.write(b"\n")
check = open(REPORT, "rb").read()
assert check.count(marker.encode("utf-8")) == 1
print("addendum appended OK")
