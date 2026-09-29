# -*- coding: utf-8 -*-
"""r435 bm-a round close: state/heartbeat/round-report/CODELY lesson 113/HANDOVER 5x row/MSG archive."""
import json, time, shutil, os, datetime
import psutil

os.chdir(r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney")
ts_full = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())
cpu = psutil.cpu_percent(interval=0.5)
free_ram = round(psutil.virtual_memory().available / (1024**3), 1)

def eol_of(data: bytes) -> bytes:
    return b"\r\n" if b"\r\n" in data else b"\n"

def append_line(path: str, line: str):
    with open(path, "rb") as f:
        data = f.read()
    eol = eol_of(data)
    sep = b"" if data.endswith(b"\n") else eol
    with open(path, "ab") as f:
        f.write(sep + line.encode("utf-8") + eol)

# 1) state-bm-a.json
state = {
 "round_no": 435,
 "did": ("r435: P0 rescue round -- machine reboot 15:34 killed 15:18 round mid-A7-freeze (orphan prereg+runner+seed uncommitted); "
         "eCloud (tianyi desktop backup, desktopBackupTimingWay=2, autostart 15:34:56) post-boot pass 15:35:17 MOVED 12 tracked files to "
         "'X的冲突文件 <fullwidth-colon-ts>' backups then DELETED originals, 15:42:03 re-enforced on restored state*.json+REPORT pair "
         "(reflog zero git ops = pure filesystem enforcement, git objects intact) -> emergency stop eCloud processes (reversible, evidence "
         "preserved) + git checkout restore 12 files zero-loss + stale 09-28 autostash left in place (r431 ruling stands); "
         "A7 orphan chain verified complete -> freeze commit 92a7b33fb (prereg+runner+seed t101_v4_a7_scrnull=20309000+F-04 MSG) -> "
         "live-fire 10/10 KILL LINE_CLOSE: oos_excess -0.12~-2.54%/yr all negative + maxdd -48.6~-74.5% all break -35% + L1 risk-off exposure "
         "3.2% = structural beta face (vs_bh corr 0.9984 pre-declared) + L2 2.1% whipsaw; P4 FALSIFIED: OOS-era GC001 spikes (year/quarter-end "
         "seasonal) fully decouple from equity bear -> gate fires wrong windows, zero bear protection (510300|L1 bear oos -16.0%/yr); "
         "P5 FALSIFIED: IS -0.84%/yr incl 2013-06 crunch window; D6 vs carry family 0.0154 ACCEPT as predicted; "
         "first-run pandas3 cross-calendar boolean-mask crash fixed positional (zero-burn window r251/r280 precedent, criteria untouched); "
         "prereg sec7/sec8 backfill + gate_attrition row 72 + F-04 MSG archived to processed/"),
 "verify": ("smoke 26/26; S6 28 legs rc=0 + 4 trigger-gated legit-skip (no new bar cutoff 2026-09-28); dualrun ZERO-DRIFT streak 16/3; "
            "WM insufficient_history (post-reboot series rebuild honest); regime ORANGE; clock ORANGE_COOL sleeves=4 act=0; "
            "REPORT-2026-09-29 faces=5 + LIVE-2026-09-29 ORANGE cap=50% COOL regen; token delta=0; orders 122/122 double-scan zero-unacked; "
            "decisions C-20260929-01/02 receipts (BM faces already wired: token_meter api_reason + pool three-verify + CEO-machine CPU 10% reserve) "
            "+ D-20260929-07 in-prompt executing; ledger 341,063+10 -> 341,073 linear; eCloud procs=0 at 15:47 -- resumption risk on next reboot flagged"),
 "next": ("r436: (a) W9-after grammar supply draft (trial-labor standing line, board empty); (b) A1 C1 dual-thermometer arm bm-b-lane follow-up; "
          "(c) 10-01 month-first triple + pool wave-1 flip quiet window; (d) eCloud reconfiguration CEO action item (exclude repo from desktop "
          "backup sync or reconcile cloud copy -- next reboot resumes destruction otherwise); next 5x=bm-a r440"),
 "last_round_at": ts_full,
 "current_task": "r435 closed: A7 liquidity defensive gate LINE_CLOSE 10/10 via crashed-round rescue + eCloud sync-storm emergency stop; next=r436 W9-after grammar supply",
 "updated": ts_full,
 "round": 435, "loop_round": 435, "last_round": 434,
 "last_round_ts": "2026-09-29T15:12:21+08:00",
}
with open("state-bm-a.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(state, f, ensure_ascii=False, indent=1)

# 2) heartbeat bm-a
hb = json.load(open("fleet/machines/bm-a.json", encoding="utf-8"))
hb.update({
 "last_seen": ts_full,
 "current_task": state["current_task"],
 "cpu_pct": cpu, "cpu_util_pct": cpu,
 "free_ram_gb": free_ram, "idle_ram_gb": free_ram,
 "verdict": "healthy",
 "heartbeat_epoch_utc": epoch,
 "clock_read": datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S.%f+08:00"),
 "round_no": 435, "round": 435, "loop_round": 435,
 "task": "r435-a7-prescreen-line-close-and-ecloud-rescue",
})
with open("fleet/machines/bm-a.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
assert isinstance(json.load(open("fleet/machines/bm-a.json", encoding="utf-8"))["heartbeat_epoch_utc"], int), "epoch must be int"

# 3) round report row
row = ("| 2026-09-29 15:5x | r435 | P0 抢救轮：15:34 机器重启杀死 15:18 轮（A7 冻结成孤产）+15:35:17 eCloud 天翼云盘桌面备份同步风暴摧毁工作树"
       "（12 跟踪件移存「的冲突文件」备份后删原件、15:42:03 对复原件二次执法、reflog 零 git 操作=纯文件系统行为）→紧急止损 Stop-Process eCloud（可逆）→"
       "git checkout 复原 12 件零丢失（09-28 旧 autostash 留置照 r431 裁定）→A7 孤产验证完整→冻结 commit 92a7b33fb→跑批 10/10 KILL 线关闭"
       "（OOS 超额全负 −0.12~−2.54%/yr+maxdd 全破 −35%+L1 开仓率 3.2%=vs_bh 0.9984 结构性 beta 面；P4 证伪=OOS 世代 GC001 尖峰与权益 bear 完全解耦→"
       "bear 段零避损 −16.0%/yr；P5 证伪=IS 同负 −0.84%/yr；D6 vs carry 0.0154 ACCEPT 如预测）→首跑 pandas3 跨日历掩码崩溃修复（位置掩码化·"
       "零格已烧修正窗 r251/r280 先例·判据零触碰）→§7/§8 回填+attrition 72+MSG 归 processed | smoke 26/26；S6 28 腿 rc=0+4 触发门控合法跳（无新 bar "
       "cutoff 09-28）；dualrun ZERO-DRIFT 16/3；WM insufficient_history（重启后序列重建诚实态）；regime ORANGE；clock ORANGE_COOL；"
       "REPORT+LIVE-0929 再生（ORANGE·50%帽·COOL）；token delta=0；orders 122/122 双扫零未回执；decisions C-01/C-02/D-07 回执（BM 面既有接线合规）；"
       "账本 341,063+10→341,073 | r436：(a) W9 后备语法供给起草（板空常设线）(b) A1 双温度计 bm-b 侧 follow-up (c) 10-01 月首轮三件套+池 flip 静默窗；"
       "eCloud 重新配置=CEO 待办（下次重启自启必复发——须排除本仓目录或对账云端副本）；下次 5x=bm-a r440 |")
append_line("logs/iteration-loop/round_reports-bm-a.md", row)

# 4) CODELY.md lesson 113 (eCloud desktop-backup sync storm)
lesson = ("- [2026-09-29 15:5x r435 bm-a] 坑律一一三批（云盘桌面备份同步风暴杀树律·15:34 重启实弹）：机器 15:34 重启→eCloud（天翼云盘 com.dlife·"
          "desktopBackupTimingWay=2 桌面备份）自启 15:34:56→21 秒后对桌面内本仓 12 跟踪件执行「移存为『X的冲突文件 全角冒号时间戳』副本后删除原文件」，"
          "15:42:03 对 git checkout 复原件二次执法（state*.json+REPORT 对反复追杀）；reflog 零 git 操作=纯文件系统行为（git 物件零伤，全部可 checkout "
          "复原零丢失）。How to apply：①树内文件无端消失先查「的冲突文件」备份名+git reflog（git 无痕=外部同步器执法非 git 事故）；②止血=Stop-Process "
          "eCloud（可逆·不删任何数据）→git checkout -- 逐件复原；③根治=CEO 待办：eCloud 同步范围排除本仓目录或对账云端副本——下次重启自启必复发；"
          "④09-28 旧 autostash（stash@{0}）为 r431 已裁定留置件，勿动勿套用。")
append_line("CODELY.md", lesson)
append_line("CODELY.md", (" (round 435: machine reboot killed 15:18 round mid-freeze; eCloud desktop-backup sync storm shredded working tree 12 files "
                          "-> emergency stop + zero-loss restore + A7 full-chain same-round closure 10/10 KILL LINE_CLOSE; ledger 341,073; attrition 72) [via bm-a]"))

# 5) HANDOVER 5x row (R210 anchor-insert before previous bm-a check line)
p = "research/HANDOVER.md"
data = open(p, "rb").read()
eol = eol_of(data)
anchor = "bm-a round 430".encode("utf-8")
idx = data.find(anchor)
assert idx > 0, "HANDOVER anchor not found"
line_beg = data.rfind(b"\n", 0, idx) + 1
hrow = ("> bm-a round 435 五轮数核对（2026-09-29 15:5x）：增量窗 R431-435=bm-a 侧（**重启+云盘风暴 P0 抢救+A7 供线全链**——r431 S0 双 rebase 16-UU "
        "正典解+T-102 lane-4 论坛 digest 四波收口；r432 pit-93 merge-back 落地+T-102 v0.2 FINALIZED（A1-A8 臂表）+四车道基准波全关；r433 A2-PRESCREEN "
        "实弹 1 存活/9 判负+同门换用法反向证伪例+D6 beta 同源 REJECT；r434 A2-CORRSOURCE BETA_SAME_SOURCE→A2 臂 LINE_CLOSE 10/10 全 resolved+坑律 112 "
        "账本返回值律+水位线重整（CODELY.md 7,410B）；r435=本核对轮 **15:34 机器重启杀死 15:18 轮（A7 冻结孤产）+eCloud 桌面备份同步风暴摧毁工作树 12 件"
        "→紧急止损+零丢失复原→A7 全链同轮闭环**：冻结 commit 92a7b33fb→跑批 10/10 KILL 线关闭（OOS 压力-bear 解耦=P4 证伪·IS 同负=P5 证伪·D6 vs carry "
        "0.0154 ACCEPT）→坑律 113 云盘杀树律+首跑 pandas3 跨日历掩码修复（零格已烧窗）→attrition 72→账本 341,073 实读）。产物清单漂移="
        "research/T-101-V4-A7-PRESCREEN_PREREG.md（§7/§8 已回填）+scripts/t101_v4_a7_prescreen.py+results/t101_v4_a7_prescreen.json+csv+"
        "gate_attrition.bm-a.json 72 行+SEED_REGISTRY t101_v4_a7_scrnull=20309000+fleet/inbox/processed/ F-04 闭环件；orders 122/122 双扫零未回执；"
        "smoke 26/26；指针：W9 后备语法供给起草（板空常设线）+A1 双温度计 bm-b 侧+10-01 月首轮三件套与池 flip 静默窗+**eCloud 重新配置=CEO 待办"
        "（重启必复发）**；下一 5x=bm-a r440。" + eol.decode())
open(p, "wb").write(data[:line_beg] + hrow.encode("utf-8") + data[line_beg:])

# 6) F-04 MSG -> processed/
src = "fleet/inbox/MSG-20260929-1535-bma-t101v4-a7-prescreen.md"
dst = "fleet/inbox/processed/MSG-20260929-1535-bma-t101v4-a7-prescreen.md"
if os.path.exists(src):
    shutil.move(src, dst)
    print("MSG archived -> processed/")

# self-verify
for p2 in ("state-bm-a.json", "fleet/machines/bm-a.json", "results/gate_attrition.bm-a.json", "results/t101_v4_a7_prescreen.json"):
    json.load(open(p2, encoding="utf-8"))
    print("parse-ok", p2)
print("epoch_int_ok", isinstance(epoch, int), "| cpu", cpu, "| free_ram", free_ram, "| ts", ts_full)
