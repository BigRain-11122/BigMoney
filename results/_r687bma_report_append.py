# -*- coding: utf-8 -*-
"""r687 bm-a round report line append (marker count==0 idempotence gate per
r679 law; single line, fixed fields)."""
import io

REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
PATH = REPO + r"\round_reports-bm-a.md"
MARK = "| r687 (bm-a) |"

with io.open(PATH, "rb") as f:
    raw = f.read()
cnt = raw.decode("utf-8", "replace").count(MARK)
assert cnt == 0, "r687 marker already present (%d)" % cnt

line = (
    "2026-10-04T17:1x+08:00 | r687 (bm-a) | watermark=green (red=false; satengine "
    "alive rc0 queue0 verdict=idle; py_watermark py_low golden-week legal "
    "board-clear idle; compute_audit CLEAN; pool dualrun ZERO-DRIFT streak 51 "
    "@cutoff 16:41:0x) | 当前活: W3 s3 judge seat YIELDED to bm-c r484 freeze "
    "(dual-freeze 16:34 vs 16:42 collision resolved per commit-time 让路律; "
    "bm-c judge-prep detached 16:35 in-flight -- tickets then pool burn) | "
    "最近实物: merge a6fc0132d DELIVERED (3 judge faces theirs-canonical + "
    "CODELY union +2 lines; probes _r687bma_pool_face_probe/_s05_scan/"
    "_d19_check; adopted-face selftests mass_trial_w1 40/40 + science_gates "
    "69/69; S6 37/37 rc0 86.9s _r687bma_s6_log.txt) @ 2026-10-04T17:0x | "
    "下个里程碑: W3 judge pool tickets + three-machine autofill shard burns "
    "(bm-a runner face verified green, window <=48h) + W117 finalize the "
    "round bm-b W116 finalize lands + fund-trio NULLS finalize 10-05..09 "
    "(bm-b canonical) | DONE-1 S0: dual-wave integration -- dead r685/r686 "
    "session adopted (r685 W3 screen finalize + r686 superseded judge "
    "freeze); 24 intersection faces origin-verbatim pre-alignment absorb "
    "(pool probe r474: 0 owner_since regressions; 4 stale W3-JUDGE tickets "
    "dropped unpushed ownerless never-ignited) + merge 15-commit wave 4 UU "
    "canon-resolved + push_verify DELIVERED | DONE-2 S0.5: orders 154/154 "
    "zero-unacked (same-form full-name set-diff) + D-19 dual MATCH "
    "(decisions 4e5be321 / group-orders 82a0cef9; K: absent S4U -> "
    "sparse-clone raw-blob ssh-first r631/r677 recipe) | DONE-3 S1: smoke "
    "48/48 | DONE-4 S2/S3: board 45/45 claimed zero-open; adopted-face "
    "verification closure (selftest 40/40 + 69/69 via -m canonical form "
    "r683 law); satengine alive rc0; W117 finalize still GATED on bm-b W116 "
    "(rehearsal r684 FAIL-CLOSED verified); fund trio bm-b in-flight V853/"
    "Q668/D507 | DONE-5 S6: 37/37 rc0 86.9s (live.paper golden-week no-new-"
    "bar honest skip r660 precedent) | DONE-6 S7: self-heal 4/4 (loop pin=8 "
    "no-op + watchdog re-reg + both claws re-installed) + attrition CLEAN "
    "4 ledgers + MSG yield notice MSG-2026-10-04-1712 + seat MSG-1655 "
    "archived to processed | 记分: 2 (collision-unblock merge + adopted-"
    "face burn-readiness verification = runnable/visible artifacts; probes + "
    "S6 38-leg products) | 记账预算: 4/5 (state + heartbeat + report + "
    "CODELY 1 line) | 本地未达 origin commit 数: 0 (closeout push_verify "
    "self-proof) | 登记册零命中断言: 本轮零清扫/归档/删除/恢复类动作 "
    "(treasure_guard 零调用; inbox seat-MSG archive = 协调面移动非清扫) | "
    "宝藏捕获: 无 (merge resolution per existing laws, no new methodology) | "
    "下轮指针: ①origin probe W3 judge pool tickets (bm-c prep landed?) -> "
    "autofill claims shards -> id-dup probe same-window per r482/r685 before "
    "any finalize ②W116 finalize watch -> W117 finalize single-shot ③fund "
    "trio finalize watch 10-05..09 ④10-06+ style-rotation next-wave drafting "
    "(needs bm-b astock_daily panel)"
)
with io.open(PATH, "a", encoding="utf-8", newline="") as f:
    f.write("\n" + line + "\n")
raw2 = io.open(PATH, "rb").read().decode("utf-8", "replace")
assert raw2.count(MARK) == 1, "marker count must be exactly 1 after append"
print("report appended, marker count 1 OK")
