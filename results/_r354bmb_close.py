# -*- coding: utf-8 -*-
"""r354 bm-b closure: state.json round++ / heartbeat refresh (epoch int + clock T-sep) /
T-94 progress_r354 / round report line / CODELY.md pit-law append. Idempotent-safe single shot."""
import json, time, datetime, io

ROOT = r"C:\Users\Administrator\Desktop\Bigmoney"

# ---------- 1) state.json round_no 353 -> 354 ----------
sp = ROOT + r"\state.json"
s = json.load(open(sp, encoding="utf-8"))
assert s["machine_id"] == "bm-b", "identity guard"
s["round_no"] = 354
s["note"] = ("r354: governance-closure round (V2-P1 thread closed both sides: MSG-0220 archived + MSG-0232 receipt sent; "
             "claim face zero-residual confirmed at tip) + W2-A census burn no-kill continuing (11.2h wall, 4 workers "
             "full-load CPU-sampled 6s deltas) + JUDGE flip honestly deferred: gate cond(1) judge-prep SATISFIED "
             "(judge_state.json 01:48:34, census L 1253/1127/875 D 3104/2978/2726 == FROZEN_P5C) but cond(2) RAM>=4GB "
             "UNSTABLE (30s 3-sample 4.59/3.08/1.48GB decay; single-read gate crossing = false signal on co-tenant box) "
             "+ S6 30/30 rc=0 (no-new-bar cutoff 09-24, 3 bar-gated legs legally skipped) + smoke 25/25 + self-heal 3/3 "
             "(pin=2 no-op, watchdog re-reg, claw installed)")
json.dump(s, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("state.json round_no ->", s["round_no"])

# ---------- 2) heartbeat bm-b.json ----------
hp = ROOT + r"\fleet\machines\bm-b.json"
h = json.load(open(hp, encoding="utf-8"))
now = datetime.datetime.now().astimezone()
epoch = int(time.time())
import psutil
vm = psutil.virtual_memory()
free_gb = round(vm.available / 1024**3, 2)
cpu_pct = psutil.cpu_percent(interval=1.5)
h["machine_id"] = "bm-b"
h["last_seen"] = now.isoformat(timespec="seconds")
h["heartbeat_epoch_utc"] = epoch          # JSON int by construction
h["clock_read"] = now.isoformat(timespec="seconds")   # ISO 8601 with T separator
h["current_task"] = ("r354 governance closure landed: V2-P1 claim face closed both sides (MSG-0220 archived + MSG-0232 receipt) "
                     "+ JUDGE/TRIAL-JUDGE/W2B/V2-P1-launch RAM gate honestly closed (3-sample 4.59/3.08/1.48GB decay evidence) "
                     "+ W2-A 11h+ no-kill sole legal occupant; next r355 = W2-A finalize harvest window + stable-RAM>=4GB JUDGE flip "
                     "+ Monday 09:15 T-91 s3 / 15:30 T-87 new-bar chain; CEO 48h clock 09-29 22:45 owner bm-b")
h["cpu_cores"] = 16
h["free_ram_gb"] = free_gb
h["total_ram_gb"] = round(vm.total / 1024**3, 1)
h["cpu_util_pct"] = cpu_pct
h["gpu_free_vram_gb"] = 6.9
h["round_no"] = 354
h["verdict"] = ("green: W2-A 4-worker no-kill sole legal occupant (11.2h, CEO census O-2320); RAM gate honest-closed for "
                "JUDGE/W2B/V2-P1-heavy faces (3-sample decay evidence, single-read crossing rejected); judges queued behind gate")
# legacy mirror fields kept in sync (F7-family consistency)
h["cores"] = 16
h["idle_ram_gb"] = free_gb
h["gpu_free_vram_mb"] = 6900
h["idle_ram_mb"] = int(free_gb * 1024)
h["gpu_idle_vram_mb"] = 6900
h["gpu_idle_vram_gb"] = 6.9
h["cpu_pct"] = cpu_pct
h["round"] = 354
h["free_ram_mb"] = int(free_gb * 1024)
h["loop_round"] = 354
json.dump(h, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
# post-write self-verify per law
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in chk["clock_read"], "clock_read must be T-separated"
print("heartbeat: epoch=", chk["heartbeat_epoch_utc"], "int-verified; clock=", chk["clock_read"], "; free_gb=", free_gb, "cpu=", cpu_pct)

# ---------- 3) T-94 progress_r354 ----------
tp = ROOT + r"\fleet\tasks\T-2026-09-27-94-P1.json"
t = json.load(open(tp, encoding="utf-8"))
t["progress_r354"] = ("bm-b r354 (T-94 owner, governance-closure face): (a) V2-P1 yield-thread fully closed both sides "
                      "(bm-c MSG-0220 archived + our MSG-0232 receipt sent; claim face zero-residual, lane_owner=bm-b intact at tip 9595c9f4). "
                      "(b) JUDGE flip honestly DEFERRED with evidence: TRIAL-LABOR-W1-JUDGE gate cond(1) judge-prep satisfied "
                      "(judge_state.json 01:48:34 census==FROZEN_P5C dual-leg verified) but cond(2) RAM>=4GB unstable -- 30s 3-sample "
                      "4.59/3.08/1.48GB decay = single-read crossing false signal (co-tenant Minigame lanes); flip executor stays "
                      "bm-b round on first STABLE >=4GB window (expected post W2-A finalize); MASS-TRIAL-W1-JUDGE-SHARD-0..3 stay "
                      "waiting per frozen sec.9.1 CPU ordering behind W2A/W2B+wave-1b SCREEN. (c) W2-A census burn 11.2h no-kill "
                      "continuing (5 procs alive, workers ~36.4k CPU-sec each, 6s delta full-load). (d) CEO 48h report clock "
                      "09-29 22:45 owner bm-b unchanged; judgment results land when RAM unlocks.")
json.dump(t, open(tp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("T-94 progress_r354 appended")

# ---------- 4) round report line ----------
rp = ROOT + r"\logs\iteration-loop\round_reports.md"
line = (now.isoformat(timespec="seconds") + " | round 354 bm-b | dept:工程+舰队(+策略:T-94 owner 维持面) | "
        "WM-VERDICT: green (watermark_red red=false@02:20:21 lane healthy; probe 02:26 py_low_with_work_cands=合法面: "
        "W2-A census burn 4-worker BelowNormal 唯一在烧 no-kill + 板0 open+bandit 空+池候全卡 RAM 门=合法白名单延续 r353 裁定) | "
        "did: (1) S0-1 锚定 bm-b; S0 stash→pull --rebase 干净落地 (bm-c r124 9595c9f4 + autofill tick 自提交 83d9fbdc rebase 并链, 本地领先1推平); "
        "(2) S0.5 轮首全扫 orders 99/99 零差集 + 集团 decisions.md 三路缺位诚实 no-op; (3) S1 smoke 25/25; (4) S2 双板 0 open (job_list 空+tasks 无 open); "
        "(5) S3 主活=治理链收口回执轮: MSG-0220(bm-c V2-P1 self-yield 闭案)归档+回执 MSG-0232 发出 (claim face 双侧闭案+judge-prep 8ea5d088 收讫+吞面向量互律) "
        "+ W2-A 烧批 CPU 采样双验 (4 workers 各 ~36.4k CPUsec, 6s delta 5-6s 满负荷, 11.2h wall, no-kill 持续, w2a_results.json 未落=finalize 未到窗) "
        "+ **JUDGE 翻面门诚实裁定**: 4.59GB 单读触线→30s 三采样 4.59/3.08/1.48 衰减=条件(2)不稳不满足, TRIAL-LABOR-W1-JUDGE 翻面诚实推迟 "
        "(条件(1) judge-prep 已满足=judge_state 01:48:34 census==FROZEN_P5C 双腿实证; 翻面执行体=本机轮不变), "
        "MASS-TRIAL-W1-JUDGE-SHARD-0..3 按 sec.9.1 冻结排序 (W2A/W2B+wave-1b SCREEN 之后) 继续等待, 禁单读翻面坑律入册 S4; "
        "(6) S6 30/30 rc=0 (无新 bar cutoff 09-24→live.paper+t35_open_fill+t24_prospect_paper 三门控腿合法跳过; audit CLEAN pool-supply-gap "
        "pool_ready=2; probe py_low_with_work_cands=RAM 门归因; daily 0 行合法; regime ORANGE shadow; scorecard 6+28+7 S=2 A=4; "
        "clock CALL-09-24 ORANGE_COOL sleeves=4 幂等; 8 车道护栏 no-op; astock+rev_osc 本机双道 no-op fresh; fundamental fresh; "
        "b_layer 5 门全过; promo 0/22 诚实 NOT-ELIGIBLE; aggr/alloc/grid 幂等 no-op; sysv1 bm-a 道 no-op; export 09-24; "
        "dscore 6; dreport faces=4; build_status; token delta=0) ; (7) inbox 1 件归档+1 回执发出; "
        "(8) S7 自愈 3/3 (pin=2 no-op 核对+watchdog 幂等重注册+pre-commit claw LF 归一装定) + schtasks 三任务在册 (IterLoop=本会话/Autofill tick 02:30 实例在飞/Watchdog 就绪) | "
        "evidence: smoke 25/25 + S6 30x rc=0 + MSG-0232 落盘 + RAM 三采样实录 (4.59/3.08/1.48) + psutil CPU delta 双验 + "
        "orders 程序化差集零 + epoch int 自证 + commit 见本轮 push | "
        "next: (a) W2-A finalize 收割窗 (w2a_results.json 落地→r312 done-flip 池面+T-86 bm-a 票面回执+W2B dep(2)+RAM 解锁面); "
        "(b) 稳定 RAM>=4GB 窗 JUDGE×4+TRIAL-JUDGE 翻面 (三采样稳定性证据门槛); (c) 周一 09:15 T-91 s3 首队列 + 15:30 T-87 astock 首增量 new-bar 全链 "
        "(update_daily→live.paper REGIME_GUARD v3 enforce→t35v→t24→aggr→grid→export→scorecard→daily_report); "
        "(d) CEO 48h 报钟 09-29 22:45 owner bm-b; (e) 10-01 月首轮三件套 (science_audit/monthly_briefing/self_review)+REGIME_GUARD v3 日期门 [r354 bm-b]\n")
with io.open(rp, "a", encoding="utf-8") as f:
    f.write(line)
print("round report line appended,", len(line), "chars")

# ---------- 5) CODELY.md pit-law append (four-question gate passed: near-miss lesson, reusable, one matter, <1.5KB) ----------
cp = ROOT + r"\CODELY.md"
pit = ("- [2026-09-28 02:3x r354 bm-b] 坑律：**RAM 门控翻面禁凭单读**——共栖机（bm-b 与 Minigame 三车道同盒）空闲 RAM 30 秒内实测 "
       "4.59→3.08→1.48GB 三采样衰减；单读过线即翻 JUDGE（双腿面板 initargs 重批）会把 no-kill 在烧面推进 OOM 胁迫窗。"
       "正典=RAM≥N GB 类翻面/launch 门须**≥3 采样跨 ≥30s 全过线**才准动（tick 侧 worker_cap 属 launch 时第二道守卫，不豁免翻面稳定性证据）；"
       "单读过线=记三采样证据、诚实推迟到下一轮。姊妹面=r352「RAM 0.72-6.3GB 波动」观察未成律、本条升格。How to apply：任何 waiting 池条目 "
       "data_gates 含 RAM 阈值时，翻面前先三采样；不满足即推迟并留证据入票面 progress。\n")
with io.open(cp, "a", encoding="utf-8") as f:
    f.write(pit)
print("CODELY.md pit-law appended,", len(pit), "chars; size check:")
import os
print("  CODELY.md bytes =", os.path.getsize(cp), "(<50KB no reorg trigger)" if os.path.getsize(cp) < 50*1024 else "(!! >50KB reorg trigger)")
print("ALL CLOSURE WRITES DONE")
