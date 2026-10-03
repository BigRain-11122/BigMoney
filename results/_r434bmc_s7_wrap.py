# -*- coding: utf-8 -*-
"""r434 bm-c S7 wrap: T-162 progress line + state-bm-c.json + heartbeat +
round_reports-bm-c.md (load-modify-dump, preserves unknown fields).
Args: <cpu_pct> <idle_ram_gb> <gpu_free_vram_mib>. Epoch = python int
(R170/R178 law), clock_read = ISO 8601 T-separated (R262 law)."""
import json
import os
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())
CPU, RAM, GPU = sys.argv[1], sys.argv[2], int(sys.argv[3])

# preflight self-checks (zero-write demo evidence)
assert not os.path.exists(os.path.join(REPO, 'results', '_canon_sweep_last.json')), \
    'live hard-reject demo must be zero-write (no receipt expected)'

DID = (
    "r434 bm-c: WM 绿（watermark_red=false；py_low_with_work_cands 合法=MASS_TRIAL_W2-JUDGE finalize 烧批在飞=本机活工作面·deadline 10-06）。"
    "(1) O-2030 焊面余项1+3 全量 DELIVERED=焊面收口（主产出·T-162 progress_r434_bmc 已落）："
    "item1 canon 热冷整编驱动器 Tools/canon_sweep.py——probe（只读测量：面尺寸 vs 硬线〔CODELY.md 50KB 水位/pit-* 10KB 结构线〕+登记册分类+流水标记候选数·零写）；"
    "apply（内嵌门四步=treasure_guard 单源 import prescan 登记册命中 rc3 硬拒→隔离区安全快照〔manifest 兼容 treasure_guard assert〕→research/memory-archive/<YYYYMM>.md verbatim 追加〔冷层 append-only 方向〕→r444 范式指针行+零丢失断言〔迁移字节==归档字节/指针数==1/标记行清零/未匹配行逐字保留/快照恒等·FAIL 即回滚〕；--authorize 理由门≥8字+拒绝字节计数驱动清扫〔r504〕）；"
    "selftest 13/13 PASS（hermetic tempdir）；live probe rc0（11 面：CODELY.md 27,270B<51,200 水位未触发·9 pit 面 PROTECTED 超 10KB 结构线如实报告=在役律禁字节归档）；"
    "live 硬拒实弹 rc3（apply research/pit-data.md 在内嵌 prescan 拒·只读零写·_canon_sweep_last.json 不存在自证）。"
    "item3 per-runner finalize capture 注释 31 焊点=14 wave runner ×cmd_screen/judge_finalize+mass_trial_w1.py cmd_finalize/cmd_judge_finalize+W2 spawn wrapper——外科三段律（count==1→插入→target-line 断言）+py_compile 全过+全件复验；"
    "diff=25 insertions 0 deletions 纯注释零逻辑（在飞 W2 烧批进程内存态不受磁盘注释影响）；receipt results/_r434bmc_capture_weld.json。"
    "焊面全量=item1(r434)+item2(r433)+协议焊(r432) 齐·验收包证据 staged（10-08 窗）。"
    "(2) W2 FINALIZE BURN POLL：PID alive（cpu=11529s·mem 257MB 前进中）·probe AWAITING exit 3 诚实回执（落地轮 adopt·deadline <=10-06）。"
    "(3) S0 fetch 后 0 behind 0 ahead 零手术；S0.5 orders 152/152 零差集（S7 双扫同）；D-19 4167B784 MATCH；GORDERS 68947C17 MATCH 双水位零消费。"
    "(4) S1 smoke 47/47 PASS（_r434bmc_smoke_log.txt）；satengine rc0 活；S6 37/37 rc0 NON-ZERO=none（_r434bmc_s6_log.txt·dualrun ZERO-DRIFT streak 35·四 lane_io 面 stale-takeover derive〔bm-a 心跳 45min 陈旧<3h 免呈报 watch 续〕·周末+国庆假期采集腿诚实 no-op）。"
    "(5) S7：attrition CLEAN rc0（2 healed 注记照录）；claws/loop/watchdog 4/4（loop pin=5 零漂移）；inbox 0 件未读。"
    "五收口步捕获问：本批无新宝藏（纯接线无判决/冻结/名单面）→登记册零新行照实。登记簿零命中断言：本轮删除类动作 0 起（canon_sweep apply 仅 hermetic selftest+只读 rc3 硬拒 demo·仓内零写零删）·登记簿命中=0。"
    "本地未达 origin commit 数=0（push 后 fetch 自证）。"
)

CUR = ("r434: O-2030 weld face COMPLETE (item1 canon sweep driver + item3 per-runner capture comments delivered; "
       "item2 was r433); W2 burn poll AWAITING (PID alive, cpu advancing); next: r435 W2 adopt-at-landing poll + "
       "O-2030 acceptance evidence pack 10-08")

NEXT = ("(a) r435+: poll burn via python results/_r430bmc_w2_adopt.py probe -> if w2_judge.json landed: "
        "ADOPTION-RECEIPT + adapt _r426bmc_close.py template (count->replace->target-line-assert trio per r429 pit) "
        "+ idempotent finalize no-op check -> commit product + deferred burn log atomically, deadline <=10-06; "
        "W2 landing = first 判决-finalize capture-point example for the 10-08 acceptance pack; "
        "(b) O-2030 acceptance evidence pack assembly 10-08: weld face complete r434 (items 1+2+3), demo receipts "
        "r432/r433/r434 + milestone tag + protocol welds + five-collection-point first examples; "
        "(c) D-06 closure 10-07: pit-git 107KB sub-split ruling + pit-data CRLF-face decision + flow-sinking "
        "remainder (canon_sweep apply face ready, GM-ruling gated) + final reconciliation; "
        "(d) T-143 assembly window post-10-09 (deliverable 10-29); "
        "(e) bm-a heartbeat staleness watch (45min stale at 22:54; >3h = GM report).")

VERIFY = ("canon_sweep selftest 13/13 + live probe rc0 (11 faces, CODELY 27,270B<51,200) + live hard-reject rc3 "
          "zero-write (no _canon_sweep_last.json + no new quarantine dir); capture weld receipt "
          "results/_r434bmc_capture_weld.json (17 files / 31 anchors / 25+/0- / py_compile ok / global re-verify OK); "
          "T-162 progress_r434_bmc appended (json re-parse OK); smoke 47/47 (_r434bmc_smoke_log.txt); "
          "S6 37/37 rc0 NON-ZERO=none (_r434bmc_s6_log.txt; dualrun streak 35); orders 152/152 double-scan; "
          "D-19 MATCH; GORDERS MATCH; attrition CLEAN rc0; S7 4/4 (loop pin=5 no-drift); inbox 0; "
          "epoch int + clock T-sep in-wrap")

REPORT_LINE = (NOW + "\t| r434 bm-c\t| " + DID + "\t| " + VERIFY +
               "\t| 下轮指针: " + NEXT)

PROGRESS = (
    "weld remainder item1+item3 DELIVERED r434 = WELD FACE COMPLETE. "
    "(item1) Tools/canon_sweep.py hot-cold sweep driver with embedded gate: probe (report-only sizes vs hard lines + registry class + flow-marker candidates, zero writes) / apply (embedded prescan rc3 via treasure_guard single-source import -> quarantine safety snapshot (manifest compatible with guard assert) -> verbatim cold-layer append research/memory-archive/<YYYYMM>.md -> r444 pointer line -> zero-loss assert with rollback; --authorize reason gate; byte-count sweeps refused per r504) / selftest 13/13 hermetic; "
    "live probe rc0 (CODELY.md 27,270B under 51,200 watermark; 9 pit faces PROTECTED, over-line reported-only = in-service law never archived for bytes); "
    "live hard-reject demo rc3 on research/pit-data.md (rejected at embedded prescan, zero writes). "
    "(item3) 31 per-runner finalize capture comments: 14 trial_labor_w*.py x (cmd_screen_finalize + cmd_judge_finalize) + mass_trial_w1.py x (cmd_finalize + cmd_judge_finalize) + Tools/_r426bmc_w2_judge_finalize.py spawn() -- surgical trio (count==1 -> insert -> target-line assert) + py_compile all pass, diff comment-only 25+/0- (in-flight W2 burn unaffected: module already loaded, comments zero-logic) -> results/_r434bmc_capture_weld.json. "
    "Weld face now complete: r432 protocol welds + r433 item2 restore guard + r434 item1+item3; acceptance pack evidence staged for 10-08 (demo receipts, milestone tag, five-point first examples pending first closeouts e.g. W2 landing)."
)

# --- T-162 progress line (ticket face) ---
tp = os.path.join(REPO, 'fleet', 'tasks', 'T-2026-10-03-162-P1.json')
t = json.load(open(tp, encoding='utf-8-sig'))
t['progress_r434_bmc'] = PROGRESS
with open(tp, 'w', encoding='utf-8', newline='') as f:
    json.dump(t, f, ensure_ascii=False, indent=1)

# --- state-bm-c.json (load-modify-dump, preserve unknown fields) ---
sp = os.path.join(REPO, 'state-bm-c.json')
st = json.load(open(sp, encoding='utf-8-sig'))
st.update({
    "clock_read": NOW, "round_no": 434, "did": DID, "current_task": CUR,
    "next": NEXT, "verify": VERIFY,
    "last_round": "r434 bm-c: O-2030 weld face COMPLETE (canon sweep driver + 31 capture comments); W2 poll AWAITING; smoke 47/47; S6 37/37 rc0",
    "last_round_at": NOW, "last_round_ts": NOW, "last_seen": NOW, "last_ts": NOW,
    "last_decisions_read_at": NOW, "updated": NOW, "updated_at": NOW,
    "cpu_pct": float(CPU), "idle_ram_gb": float(RAM), "gpu_free_vram_mib": GPU,
})
with open(sp, 'w', encoding='utf-8', newline='') as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

# --- heartbeat fleet/machines/bm-c.json ---
hp = os.path.join(REPO, 'fleet', 'machines', 'bm-c.json')
hb = json.load(open(hp, encoding='utf-8-sig'))
hb.update({
    "activity_now": "r434: O-2030 weld face COMPLETE -- canon_sweep.py driver (probe/apply/selftest, embedded treasure gate, 13/13) + 31 per-runner finalize capture comments; W2 burn poll AWAITING (PID alive, cpu advancing)",
    "clock_read": NOW, "cpu_pct": float(CPU), "cpu_idle_pct": round(100 - float(CPU), 1),
    "cpu_util_pct": float(CPU), "current_task": CUR,
    "free_ram_gb": float(RAM), "idle_ram_gb": float(RAM), "ram_free_gb": float(RAM),
    "gpu_free_vram_mb": GPU, "gpu_free_vram_mib": GPU, "gpu_idle_vram_mb": GPU, "gpu_idle_vram_mib": GPU,
    "heartbeat_epoch_utc": EPOCH,
    "last_seen": NOW, "last_seen_at": NOW, "updated_at": NOW,
    "latest_artifact": "Tools/canon_sweep.py (O-2030 item1 hot-cold sweep driver, embedded gate) + results/_r434bmc_capture_weld.json (item3, 31 weld points) @ " + NOW,
    "next_milestone": "W2 w2_judge.json landing -> adoption same round (deadline <=10-06, first 判决-finalize capture example); O-2030/O-2115 acceptance evidence pack 10-08 (weld face complete r434); D-06 full closeout 10-07",
    "prod_lanes": "O-2030 weld face COMPLETE r434 (items 1+2+3 all delivered; acceptance pack 10-08); MASS_TRIAL_W2-JUDGE finalize burn in flight (PID 31276); D-06 closure remainder 10-07",
    "round_no": 434,
})
with open(hp, 'w', encoding='utf-8', newline='') as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

# --- round report append ---
rp = os.path.join(REPO, 'round_reports-bm-c.md')
with open(rp, 'ab') as f:
    f.write((REPORT_LINE + "\n").encode('utf-8'))

# --- self-verification: epoch int + clock T-sep + json re-parse (R170/R178/R262) ---
st2 = json.load(open(sp, encoding='utf-8-sig'))
hb2 = json.load(open(hp, encoding='utf-8-sig'))
t2 = json.load(open(tp, encoding='utf-8-sig'))
assert isinstance(hb2['heartbeat_epoch_utc'], int), 'epoch not int'
assert 'T' in hb2['clock_read'] and 'T' in st2['clock_read'], 'clock not T-sep'
assert 'progress_r434_bmc' in t2, 'T-162 progress line missing'
print('S7 WRAP OK: state+heartbeat+report r434 @', NOW, 'epoch=', EPOCH, 'cpu=', CPU, 'ram=', RAM, 'gpu=', GPU)
