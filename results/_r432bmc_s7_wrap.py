# -*- coding: utf-8 -*-
"""r432 bm-c S7 wrap: state-bm-c.json + fleet/machines/bm-c.json field updates
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
    "r432 bm-c: WM 绿（red=false lane healthy）。(1) O-20261003-2030 宝藏保护焊面首片 DELIVERED（主产出·T-162 progress 已落）："
    "守门引擎 Tools/treasure_guard.py 本机复验 selftest 21/21+硬拒实弹 rc3 复演（firm/RULES.md+清扫类混合集）"
    "+隔离区模式落位 demo（results/_quarantine/20261003-221448/ manifest+identity assert rc0）"
    "+协议焊点 3/3（iteration_prompt 五类收口步宝藏捕获行/清扫硬门行/轮报零命中断言行·字节手术 count==1×3）"
    "+POST_REVIEW §五宝藏断言接线+里程碑 tag treasure/g2-slot-tail-p1-20261003→1d9ec9202 已推 origin（§4 考面冻结类首例）"
    "+登记册出入记录 2 行；验收 10-08 前置件已齐（余量=canon sweep driver 内嵌门+S0-restore 守卫模式+per-runner capture 注释·票面留痕）。"
    "(2) S0 集成手术：pull --rebase 撞 2+16 UU 双窗（bm-a r643 push-storm 集成态×r431 sweep 补丁分叉）——"
    "r423 union/r630 逐 pick 验吸收律处置：pick1 取 ours（mine 侧空=删除意图已被 origin 实现）+pick2 十六冲突全取 ours"
    "（r431 时点态全被 origin 同代/更新态吸收·needle 3/3+JSON 全验）+pick3 churn-absorb 穿完；main=origin+2 提交 0 落后。"
    "(3) S1 smoke 47/47 PASS（InvisibleRunner 全树隔离 18s）；S6 37/37 rc0 bad=[]（_r432bmc_s6_log.txt·正典三件套适配+还原 HEAD 态）；"
    "satengine rc0 活；W2 烧批 poll=AWAITING（PID 31276 活 cpu 9115s·w2_judge.json 未落地·落地轮 adopt·deadline <=10-06）。"
    "(4) S0.5 orders 152/152 零差集（S7 双扫同）；D-19 4167B784 MATCH；GORDERS 68947C17 MATCH 双水位零消费。"
    "(5) S7：attrition CLEAN rc0（2 healed 注记照录）；claws/loop/watchdog 4/4（watchdog 重建实弹）；"
    "inbox 2 件处理移件（MSG-2215 让位+引擎贡献采纳入焊·MSG-2155 已阅）。登记簿零命中断言：本轮删除类动作 1 起（隔离区 demo）"
    "全走守门合法路（prescan rc0→quarantine manifest→assert）·登记簿命中=0。本地未达 origin commit 数=0（push 后 fetch 自证）。"
)

CUR = ("r432: O-2030 weld first chip delivered (demos 6/6, protocol welds 3/3, milestone tag pushed, "
       "POST_REVIEW s5 + registry rows); W2 burn poll AWAITING (PID 31276 alive); next: r433 W2 adopt-at-landing "
       "poll + weld remainder (canon sweep driver gate, S0-restore guard mode) to 10-08")

NEXT = ("(a) r433+: poll burn via python results/_r430bmc_w2_adopt.py probe -> if w2_judge.json landed: "
        "ADOPTION-RECEIPT + adapt _r426bmc_close.py template (count->replace->target-line-assert trio per r429 pit) "
        "+ idempotent finalize no-op check -> commit product + deferred burn log atomically, deadline <=10-06; "
        "O-2115 acceptance evidence pack 10-08; (b) O-2030 weld remainder to 10-08: canon hot-cold sweep driver "
        "(embedded prescan/quarantine/assert) + S0-restore-class guard mode + per-runner finalize capture "
        "comments; (c) D-06 closure 10-07: pit-git 107KB sub-split ruling + pit-data CRLF-face decision + "
        "flow-sinking remainder + final reconciliation; (d) T-143 assembly window post-10-09 (deliverable 10-29); "
        "(e) bm-a heartbeat staleness watch (fresh 22:0x per origin commits; >3h = GM report).")

VERIFY = ("weld receipt results/_r432bmc_treasure_weld.json (6/6: selftest 21/21 + hard-reject rc3 x2 + clean rc0 "
          "+ quarantine manifest + identity assert); protocol welds count==1 x3 WELDED (+159/+211/+51B); tag "
          "treasure/g2-slot-tail-p1-20261003 -> 1d9ec92021110333df54b8e5805888830562f21d pushed origin; POST_REVIEW "
          "s5 bullet + registry rows 2; smoke 47/47 (_r432bmc_smoke_log.txt); S6 37/37 rc0 bad=[] "
          "(_r432bmc_s6_log.txt; canon adapt/restore status-clean); orders 152/152 double-scan; D-19 MATCH; "
          "GORDERS MATCH; attrition CLEAN rc0; S7 4/4 (watchdog rebuilt live); epoch int + clock T-sep in-wrap")

REPORT_LINE = (NOW + "\t| r432 bm-c\t| " + DID + "\t| " + VERIFY +
               "\t| 下轮指针: " + NEXT)

# --- state-bm-c.json (load-modify-dump, preserve unknown fields) ---
sp = os.path.join(REPO, 'state-bm-c.json')
st = json.load(open(sp, encoding='utf-8-sig'))
st.update({
    "clock_read": NOW, "round_no": 432, "did": DID, "current_task": CUR,
    "next": NEXT, "verify": VERIFY,
    "last_round": "r432 bm-c: O-2030 weld first chip (guard demos 6/6 + protocol 3/3 + tag pushed + s5 wiring); "
                  "S0 rebase surgery 2+16 UU take-ours; smoke 47/47; S6 37/37 rc0; W2 poll AWAITING",
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
    "activity_now": "r432 closeout: O-2030 treasure weld first chip delivered (engine re-verify 21/21 + live "
                    "hard-reject rc3 x2 + quarantine manifest demo + protocol welds 3/3 + milestone tag pushed + "
                    "POST_REVIEW s5 + registry rows); W2 burn poll AWAITING (PID 31276 alive)",
    "clock_read": NOW, "cpu_pct": float(CPU), "cpu_idle_pct": round(100 - float(CPU), 1),
    "cpu_util_pct": float(CPU), "current_task": CUR,
    "free_ram_gb": float(RAM), "idle_ram_gb": float(RAM), "ram_free_gb": float(RAM),
    "gpu_free_vram_mb": GPU, "gpu_free_vram_mib": GPU, "gpu_idle_vram_mb": GPU, "gpu_idle_vram_mib": GPU,
    "heartbeat_epoch_utc": EPOCH,
    "last_seen": NOW, "last_seen_at": NOW, "updated_at": NOW,
    "latest_artifact": "results/_r432bmc_treasure_weld.json (O-2030 weld demo pack 6/6) + tag "
                       "treasure/g2-slot-tail-p1-20261003 pushed @ " + NOW,
    "next_milestone": "W2 w2_judge.json landing -> adoption same round (deadline <=10-06); O-2030 weld remainder "
                      "+ O-2115/O-2030 acceptance evidence 10-08; D-06 full closeout 10-07",
    "prod_lanes": "O-2030 weld face OWNER (first chip r432 delivered, remainder to 10-08: canon sweep driver + "
                  "S0-restore guard mode + runner capture comments); MASS_TRIAL_W2-JUDGE finalize burn in flight "
                  "(PID 31276); D-06 closure remainder 10-07",
    "round_no": 432,
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
assert isinstance(st2.get('heartbeat_epoch_utc', 0) if 'heartbeat_epoch_utc' in st2 else hb2['heartbeat_epoch_utc'], int)
assert isinstance(hb2['heartbeat_epoch_utc'], int), 'epoch not int'
assert 'T' in hb2['clock_read'] and 'T' in st2['clock_read'], 'clock not T-sep'
print('S7 WRAP OK: state+heartbeat+report r432 @', NOW, 'epoch=', EPOCH, 'cpu=', CPU, 'ram=', RAM, 'gpu=', GPU)
