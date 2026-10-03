# -*- coding: utf-8 -*-
"""r433 bm-c S7 wrap: state-bm-c.json + fleet/machines/bm-c.json field updates
(load-modify-dump, preserves unknown fields) + round_reports-bm-c.md append.
Args: <cpu_pct> <idle_ram_gb> <gpu_free_vram_mib>. Epoch = python int (R170/R178
law), clock_read = ISO 8601 T-separated (R262 law)."""
import json
import os
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())
CPU, RAM, GPU = sys.argv[1], sys.argv[2], int(sys.argv[3])

DID = (
    "r433 bm-c: WM 绿（red=false lane healthy）。(1) O-2030 焊面余项2 S0-restore 分类守卫门 DELIVERED（主产出·T-162 "
    "progress_r433 已落）：Tools/treasure_guard.py 新增 restore 子命令=律 §2.4 恢复分类门——登记簿命中或记忆(CODELY.md)"
    "/state 账本/轮报/票面(fleet orders|tasks|machines|inbox)/append-only 台账(gate_attrition|pool_dualrun|token_usage"
    "|watermark)类=rc3 硬拒（只可行级 union 或先摘录存旁），可再生工件（探针/daemon live-wins 态面/代码面）=rc0 放行；"
    "锚定式样法不误捕 saturation_engine_state.bm-c.json（daemon live-wins 面保持可恢复=关键负判别腿）；"
    "selftest 21→40 腿全 PASS rc0（+19 新腿：14 禁恢类+4 可恢类+1 混合集拆分）；live-fire 双 demo（只读零写）："
    "混合集 rc3 硬拒（CODELY.md=memory+state-bm-c.json=state-ledger+fleet/machines/bm-c.json=ticket-face 三禁+双可恢列示）"
    "+净集 rc0；receipt results/_r433bmc_restore_guard_demo.json；协议焊点 s0_restore_gate 入 iteration_prompt S0 律节"
    "（+344B·count==1 字节手术·_r433bmc_prompt_weld.py·焊后 gate 引用计数 1 复核）；焊面余量=item1 canon sweep driver"
    "+item3 per-runner capture 注释（10-08 窗）。(2) W2 FINALIZE BURN POLL：PID 31276 alive（cpu 10418s·mem 261MB）"
    "·probe AWAITING exit 3 诚实回执（落地轮 adopt·deadline <=10-06·O-2115 acceptance 10-08）。"
    "(3) S0：fetch 后 0 behind 0 ahead 零手术；S0.5 orders 152/152 零差集（S7 双扫同）；D-19 4167B784 MATCH；"
    "GORDERS 68947C17 MATCH 双水位零消费。(4) S1 smoke 47/47 PASS（_r433bmc_smoke_log.txt）；satengine rc0 活；"
    "S6 37/37 rc0 bad=[]（_r433bmc_s6_log.txt·dualrun ZERO-DRIFT streak 34·t35_open_fill_verify/t35_paper_export/"
    "daily_scorecard/build_status 四 lane_io 面按 O-2100 s2.4 stale-takeover derive（bm-a 心跳 24min 陈旧）"
    "·周末各采集腿诚实 no-op）。(5) S7：attrition CLEAN rc0（4 healed 注记照录）；claws/loop/watchdog 4/4"
    "（loop pin=5 零漂移）；inbox 0 件未读。五收口步捕获问：本批无新宝藏（纯接线无判决/冻结/名单面）→登记册零新行照实。"
    "登记簿零命中断言：本轮删除类动作 0 起（restore demo 只读分类面零写零删）·登记簿命中=0。"
    "本地未达 origin commit 数=0（push 后 fetch 自证）。"
)

CUR = ("r433: O-2030 weld item2 S0-restore guard mode delivered (restore subcommand, selftest 40/40, live rc3+rc0 "
       "demos, protocol weld); W2 burn poll AWAITING (PID 31276 alive); next: r434 W2 adopt-at-landing poll + "
       "weld remainder (canon sweep driver, per-runner capture comments) to 10-08")

NEXT = ("(a) r434+: poll burn via python results/_r430bmc_w2_adopt.py probe -> if w2_judge.json landed: "
        "ADOPTION-RECEIPT + adapt _r426bmc_close.py template (count->replace->target-line-assert trio per r429 pit) "
        "+ idempotent finalize no-op check -> commit product + deferred burn log atomically, deadline <=10-06; "
        "O-2115 acceptance evidence pack 10-08; (b) O-2030 weld remainder to 10-08: item1 canon hot-cold sweep "
        "driver (embedded prescan/quarantine/assert) + item3 per-runner finalize capture comments (item2 "
        "restore-guard DONE r433); (c) D-06 closure 10-07: pit-git 107KB sub-split ruling + pit-data CRLF-face "
        "decision + flow-sinking remainder + final reconciliation; (d) T-143 assembly window post-10-09 "
        "(deliverable 10-29); (e) bm-a heartbeat staleness watch (S6 stale-takeover observed 24min stale at 22:33; "
        ">3h = GM report).")

VERIFY = ("restore-mode receipt results/_r433bmc_restore_guard_demo.json (selftest 40/40 + mixed-set rc3 + "
          "clean-set rc0, read-only); protocol weld s0_restore_gate count==1 (+344B); T-162 progress_r433_bmc "
          "appended (json re-parse OK); smoke 47/47 (_r433bmc_smoke_log.txt); S6 37/37 rc0 bad=[] "
          "(_r433bmc_s6_log.txt; dualrun streak 34); orders 152/152 double-scan; D-19 MATCH; GORDERS MATCH; "
          "attrition CLEAN rc0; S7 4/4 (loop pin=5 no-drift); epoch int + clock T-sep in-wrap")

REPORT_LINE = (NOW + "\t| r433 bm-c\t| " + DID + "\t| " + VERIFY +
               "\t| 下轮指针: " + NEXT)

# --- state-bm-c.json (load-modify-dump, preserve unknown fields) ---
sp = os.path.join(REPO, 'state-bm-c.json')
st = json.load(open(sp, encoding='utf-8-sig'))
st.update({
    "clock_read": NOW, "round_no": 433, "did": DID, "current_task": CUR,
    "next": NEXT, "verify": VERIFY,
    "last_round": "r433 bm-c: O-2030 weld item2 S0-restore guard mode (restore subcommand 40/40 + live demos + "
                  "protocol weld); W2 poll AWAITING; smoke 47/47; S6 37/37 rc0",
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
    "activity_now": "r433: O-2030 weld item2 delivered -- treasure_guard restore subcommand (S0-restore-class "
                   "gate, LAW s2.4): selftest 40/40, live mixed-set rc3 hard-reject + clean-set rc0 demos, "
                   "protocol weld s0_restore_gate; W2 burn poll AWAITING (PID 31276 alive)",
    "clock_read": NOW, "cpu_pct": float(CPU), "cpu_idle_pct": round(100 - float(CPU), 1),
    "cpu_util_pct": float(CPU), "current_task": CUR,
    "free_ram_gb": float(RAM), "idle_ram_gb": float(RAM), "ram_free_gb": float(RAM),
    "gpu_free_vram_mb": GPU, "gpu_free_vram_mib": GPU, "gpu_idle_vram_mb": GPU, "gpu_idle_vram_mib": GPU,
    "heartbeat_epoch_utc": EPOCH,
    "last_seen": NOW, "last_seen_at": NOW, "updated_at": NOW,
    "latest_artifact": "results/_r433bmc_restore_guard_demo.json (S0-restore guard mode receipt: selftest 40/40 "
                       "+ live rc3/rc0 demos) + Tools/treasure_guard.py restore mode @ " + NOW,
    "next_milestone": "W2 w2_judge.json landing -> adoption same round (deadline <=10-06); O-2030 weld remainder "
                      "(canon sweep driver + per-runner capture comments) + O-2115/O-2030 acceptance evidence "
                      "10-08; D-06 full closeout 10-07",
    "prod_lanes": "O-2030 weld face OWNER (item2 S0-restore guard DONE r433; remaining to 10-08: item1 canon "
                  "sweep driver + item3 per-runner capture comments); MASS_TRIAL_W2-JUDGE finalize burn in flight "
                  "(PID 31276); D-06 closure remainder 10-07",
    "round_no": 433,
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
assert isinstance(hb2['heartbeat_epoch_utc'], int), 'epoch not int'
assert 'T' in hb2['clock_read'] and 'T' in st2['clock_read'], 'clock not T-sep'
print('S7 WRAP OK: state+heartbeat+report r433 @', NOW, 'epoch=', EPOCH, 'cpu=', CPU, 'ram=', RAM, 'gpu=', GPU)
