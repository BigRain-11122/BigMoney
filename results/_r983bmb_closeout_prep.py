# r983 closeout prep: state.json + heartbeat + round-report row (binary-safe append).
# r962 law: round_reports.md mixed-encoding -> append-only mode ('ab') never full-read.
import ctypes
import datetime
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(datetime.datetime.now().timestamp())


def free_ram_gb():
    class MEM(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
    m = MEM()
    m.dwLength = ctypes.sizeof(MEM)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return round(m.ullAvailPhys / (1 << 30), 1)


VRAM_FREE_MB = 3970  # idle_trigger.bm-b.json 16:37 face (vram_free_gb 3.97)
RAM = free_ram_gb()

DID = ("r983: (a) C-r982 receipt consumed (430a9878a ancestor of origin rc=0; origin +1 = bm-a r1019 orphan probe face, "
       "zero bm-b dispatch) (b) D-19 dual-sha probe: decisions full sha256 UNCHANGED (ab3f0cc9 identical); orders "
       "GENUINE delta sha1 1835852b->7604cf77 = 3 new rows (10-15 16:0x CEO V3 成片三连反馈 @导演席/字幕线/深研波 + "
       "16:2x dual-wave expansion + 16:4x genre-matrix third wave) = ALL MV/media domain, zero bm-b action; earlier "
       "@bm-b dispatches verified already-receipted (O-20261015-1055 = r975, O-20261015-1250-5 = r979 five-piece); "
       "watermarks updated dec ab3f0cc9 / ord 7604cf77; MSG-1608-bma-w247-seat read (bm-a seat publication, "
       "informational, zero bm-b action) (c) MAIN DEBT PAID - CODELY.md hot-cold reorganization (state.next item 0): "
       "78,033B->17,577B (-77%, under 30,720B cap AND 50KB watermark); structure diagnosis = whole-file DOUBLE-WRITE "
       "corruption (BlockB 31,065B CRLF-variant duplicate removed under CR-normalized identity assertion) + r947-r982 "
       "recovery flow entries 18 rows verbatim migrated to archive 202610.md r983 窗批节 + mini-split provenance 20 "
       "rows + old cold-pointer 5 rows merged into 3 compact routing rows; all-zero-loss assertions PASS (4 blocks "
       "verbatim-in-arch, retained rows verbatim, byte-math identity 63,296 removed + 2,840 added = exact); receipt="
       "results/_r983bmb_codely_minisplit.json; prescan rc3 double-hit = memory/pit-law class, D-20260206 authorized "
       "migration face (d) smoke 49/49 PASS (e) sat engine alive (status rc=0, queue idle) (f) S6 39 legs ALL GREEN "
       "(_r983bmb_s6chain.log; NEWBAR gate cutoff=2026-10-14 - 10-15 sina late-bar face continues, newbar legs "
       "skipped, next round picks up) (g) S8 GREEN-IDLE gate: backlog sole claimable line = BigHouse seat (bm-c "
       "agenda, yield per seat law) -> local self-drive pool W005 claimed+ignited via bmb-claim-ignite.ps1 (pid "
       "27324 died post-ignite - claims-ledger GetContent ordering bug noted); W005 media-scan completed in-process "
       "(189 files 171.2MB census -> work-done/W005-media-scan.md); idle_trigger --worked declared, idle_rounds=0 "
       "(h) orphan face = 0 (14 py faces probed) (i) S7 quad green + LogonType spot-check 3 tasks all S4U zero "
       "regression (j) astock refresh in flight (worker 8380, panel cutoff 10-13, per_files 5219; completion package "
       "next round per ETA ~17:35)")

VERDICT = ("GREEN-production-win: CODELY.md 78,033B->17,577B watermark debt PAID (double-write dedup + 18 flow "
           "entries archived verbatim + 25 history rows merged, zero-loss PASS); D-19 orders delta consumed (3 rows "
           "MV-domain zero-action); S6 39 legs green; S8 W005 delivered; smoke 49/49; LogonType zero regression")

NEXT = ("r984: 1) astock refresh completion watch -> data churn completion package push (worker 8380, ETA ~17:35) "
        "2) C-r983 receipt consume 3) D-19 dual-sha re-probe (r984 cadence) 4) update_daily 10-15 late-bar pickup "
        "check (newbar-gated legs follow) 5) CODELY.md pit-domain re-scan follow-up (r747 范式·r947-r982 坑律域件"
        "归位候选: r950/r953/r955/r959/r960/r982 -> git 族件, r962 -> encoding, r973 -> tooling, r968/r974 -> "
        "protocol) 6) S8 gate (W006 animatic residual report open in local pool) 7) r983 addendum row lands with "
        "r984 push face")

# ---- state.json ----
sp = os.path.join(ROOT, "state.json")
s = json.load(open(sp, encoding="utf-8"))
s["round"] = 983
s["round_no"] = 983
s["round_no_label"] = "r983"
s["clock_read"] = NOW
s["ts"] = NOW
s["updated"] = NOW
s["updated_at"] = NOW
s["last_round_at"] = NOW
s["last_round_ts"] = NOW
s["last_seen"] = NOW
s["last_action_at"] = NOW
s["last_decisions_at"] = NOW
s["last_decisions_read_at"] = NOW
s["last_decisions_sha"] = "ab3f0cc9"
s["last_orders_at"] = NOW
s["last_orders_read_at"] = NOW
s["last_orders_sha"] = "7604cf77"
s["last_orders_sha_probe"] = "7604cf77925b9de47ef800d272d9a734b13fe9f1"
s["last_orders_probe_at"] = NOW
s["last_orders_sha_probe_note"] = ("r983: GENUINE delta - orders blob sha1 1835852b->7604cf77 (direct hashlib.sha1 "
                                   "over fresh git-show dump); delta = 3 rows all MV/media domain (16:0x/16:2x/"
                                   "16:4x), zero bm-b action consumed")
s["last_decisions_sha_probe"] = ("ab3f0cc9f4cb9bbb1f23c5e5a98bd5bed540a272b0b111bb481120ea7e0ba8fd")
s["last_decisions_probe_at"] = NOW
s["decisions_delta_pending"] = False
s["orders_delta_pending"] = False
s["d19_probe_due"] = False
s["d19_probe_due_note"] = ("r983 round-start probe consumed (decisions unchanged ab3f0cc9; orders GENUINE delta "
                            "3b1ca198->...->7604cf77 = 3 MV-domain rows zero action); next probe = r984 cadence")
s["current_task"] = "r983: CODELY.md watermark debt hot-cold reorganization + D-19 + S6 + S8 W005"
s["task"] = s["current_task"]
s["current"] = "r983: CODELY 78KB->17.6KB reorg + D-19 3-row delta + S6 green + S8 W005"
s["did"] = DID
s["last_action"] = ("r983: CODELY.md 78,033B->17,577B reorg (double-write dedup + 18 flow entries archived + 25 "
                    "history rows merged, zero-loss PASS) + D-19 orders delta consumed + S6 39 legs green + S8 W005")
s["now_active"] = ("r983: live faces = astock backfill worker 8380 (refresh marching, ETA ~17:35 completion "
                   "package); local pool W006 open (next S8 candidate); i2v line CLOSED; GPU keepwarm standing")
s["next"] = NEXT
s["next_milestone"] = ("astock rebuild completion package ~17:35-18:00 today (window <=48h); CODELY.md watermark "
                       "debt PAID this round (78,033B->17,577B)")
s["verdict"] = VERDICT
s["orphan_face"] = 0
s["orphan_face_note"] = "r983 probe: 14 py faces, 0 orphans (zero flags)"
s["orphan_faces"] = 0
s["sat_engine"] = {"status": "alive (live-probed rc=0 this round: status exit 0, queue 0, verdict idle)",
                   "checked_at": NOW}
s["heartbeat_epoch_utc_face"] = "bm-b.json updated this round (epoch int verified)"
json.dump(s, open(sp, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)

# ---- heartbeat ----
hp = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
h = json.load(open(hp, encoding="utf-8"))
h["last_seen"] = NOW
h["ts"] = NOW
h["clock_read"] = NOW
h["heartbeat_epoch_utc"] = EPOCH
h["task"] = s["current_task"]
h["did"] = DID
h["verdict"] = VERDICT
h["cpu_cores"] = 16
h["free_ram_gb"] = RAM
h["gpu_free_vram_mb"] = VRAM_FREE_MB
h["idle_rounds"] = 0
h["agenda_starved"] = False
h["orders_ack"] = ("r983: D-19 orders GENUINE delta consumed - 3 rows (sha1 1835852b->7604cf77: 10-15 16:0x CEO V3 "
                   "终审三连反馈 @导演席/@bm-a 字幕线/深研波 + 16:2x dual-wave + 16:4x genre-matrix third wave) = "
                   "ALL MV/media domain, zero bm-b action; decisions sha256 unchanged (ab3f0cc9); earlier @bm-b "
                   "dispatches re-verified already-receipted (O-20261015-1055=r975, O-20261015-1250-5=r979); "
                   "MSG-20261015-1608-bma-w247-seat read informational (bm-a own seat publication, zero bm-b "
                   "action); own orders O-20261015-0025/0906/0915/0952 + own MSGs 0104/0825/0952/1608 all standing "
                   "on origin | r982: (see prior ack - i2v 53/53 complete receipt MSG-1608 delivered; orders delta "
                   "1 row Qwen v3 wrap-up zero-action consumed)")
h["note"] = ("r983: CODELY.md 78,033B->17,577B watermark debt PAID (reorg receipt _r983bmb_codely_minisplit.json "
             "rides this push); W005 media-scan delivered (work-done face, sentinel closes next tick); astock "
             "refresh in flight (completion package next round); docs faces written local NOT pushed (anti-"
             "regression vs bm-a derive window, r982 policy); orphan face=0")
json.dump(h, open(hp, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178 law)"

# ---- round report row (append-only, binary face per r962 law) ----
ROW = ("\n%s | r983 | CODELY.md 水位债热冷整编当窗清偿（主件 78,033B→17,577B=-77%%·双写去重 31,065B CRLF 变体块 "
       "CR 归一恒等断言去除·r947-r982 恢复期流水判例 18 条 verbatim 迁 archive 202610.md『热冷整编 2026-10-15 "
       "r983 bm-b 窗批』节·mini-split 史行 20 行+旧冷指针 5 行合并 3 紧凑路由行·四块 verbatim-in-arch+保留面恒等+"
       "字节恒等式全 PASS·receipt=results/_r983bmb_codely_minisplit.json·prescan rc3 双命中=记忆类 D-20260206 授权迁移面）"
       "+D-19 双 sha 增量消费（dec ab3f0cc9 恒等·ord sha1 1835852b→7604cf77=3 行全 MV 域零动作·水位更新）+S6 39 腿全绿"
       "（NEWBAR 门 cutoff=10-14 sina 迟 bar·newbar 腿跳过候下轮）+S8 GREEN-IDLE：backlog 唯一可领行=BigHouse 席"
       "（bm-c 议程·让路律）→本地池 W005 认领点火+进程内补完（media-scan 189 件 171.2MB→work-done/W005-media-scan.md·"
       "--worked 声明 idle_rounds=0·哨兵 v3.0 下拍收口）+smoke 49/49+sat engine 活+孤儿面=0+S7 四件套+LogonType 三任务 "
       "S4U 零回归+astock refresh 在飞（worker 8380·ETA ~17:35 完成包候 r984） | 验证：smoke 49/49 PASS·_r983bmb_"
       "codely_minisplit.json verdict=PASS 全断言绿·_r983bmb_s6chain.log legs=39 nonzero=0·Get-ScheduledTask 三任务 "
       "LogonType=S4U | 下轮指针：astock 完成包推送+r983 附加行随 r984 面+CODELY 坑律域件回扫（r747 范式）+S8 W006\n"
       % NOW)
rp = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
with open(rp, "ab") as f:
    f.write(ROW.encode("utf-8"))

print("closeout prep done: state r983 / heartbeat epoch=%d int-verified / report row appended (%dB)" % (
    EPOCH, len(ROW.encode("utf-8"))))
