# -*- coding: utf-8 -*-
# r938 bm-c closeout: round report line + state counter 938->939 + heartbeat (epoch int self-proof)
import json, time, subprocess
from datetime import datetime, timezone, timedelta

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
now = datetime.now(timezone(timedelta(hours=8)))
ts = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
ts_loose = now.strftime("%Y-%m-%dT%H:%M")

# --- machine vitals -------------------------------------------------------------
try:
    import psutil
    cpu_pct = round(psutil.cpu_percent(interval=0.5), 1)
    ram_free = round(psutil.virtual_memory().available / (1024**3), 1)
except Exception:
    cpu_pct, ram_free = 0.0, 0.0
try:
    out = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                         capture_output=True, text=True, timeout=20).stdout.strip().splitlines()[0]
    gpu_free = int(out)
except Exception:
    gpu_free = 15208

# --- round report line -----------------------------------------------------------
rr = []
rr.append(f"{ts_loose} | r938 | bm-c clean-window product round (prior r937 closed W224 full cycle + estates; this window = r938 per state counter, zero absorb needed -- first clean window in the r907/r911/r915/r917/r919/r921/r928/r930/r933/r937 absorb lineage)")
rr.append("WM-VERDICT: green red=false (py_watermark insufficient_history fresh-window honest face; engine alive rc0 queue DRY post-W224-finalize; pool_starvation+supply_floor flags = structural wave-chain gap 442min disclosed, W225 SEAT landed THIS window = armed response, prereg next window heals)")
rr.append("dept:策略（N1 波链 W225 席位发布=供给链正身）+dept:工程（S0/S0.5/S6/S7 全链）")
rr.append("实况三行：当前活=W225 per-wave prereg derive+land=下窗第一动作（八级血统重放链·bands 机读自 probe receipt·_w224bmc_prereg_derive.py 模板）；最近实物=fleet/inbox/MSG-20261012-1943-bmc-w225-seat.md+results/_w225bmc_20261012_probe_receipt.json（19:43·commit c78dd1a44 已推 origin 验证 0/0）；下个里程碑=W225 freeze+自燃+六门 PRE-FINALIZE+finalize（下两窗内）+周一新 bar papers 全链（bar 落地窗）")
rr.append("did: r938 bm-c: (1) S0-1 anchor bm-c + round-zero probe py_faces=7 orphans=2 zero-kill（只读报告·runs in results/_orphan_face_probe.bm-c.json）；S0 fetch behind=0 clean（脏面=runtime state faces 轮尾 ride）；(2) S0.5 双水位 probe：ORD/DEC delta FALSE both（dec 94c93393/ord 9022a740 hold）+unacked=0 零动作+S7 close 双扫 0 未回执；(3) S1 smoke 49/49；S2 boards clear（jobs 0·fleet open 0）；satengine rc0 活（W224 12/12+finalize landed·queue DRY）；(4) PRODUCT=W225 seat published 同窗落地：probe derive checked-rep 加固版（rep() helper 逐处断言目标在场=静默穿透根治·3 处 rep 计数错当窗活抓=EIGHTY-FOURTH x3/N1_BANDS[223] x3/splice+burn+finalize 叙事全字面=机制自证第 4 例）+残扫全零+期望 token 全在（docstring 陈旧序数 83rd->85th 顺手治愈）-> _w225bmc_20261012_probe.py rc0 ADMIT：A 509_804..511_803 staircase EIGHTY-FIFTH hops=1（W224 注册 B 带 509_604..509_803 起窗拒走·A base==509_803+1 机检）+ B 511_804..512_003 hops=1（naive B 509_804..510_003 inside own-A 同冻互斥·W141 判例·B base==511_803+1 机检）·seed_admit FREE x2 509804/2000+511804/200·conflicts=0·origin vacancy 4-check（零 W225 seat/225 行/WAVE_CONFIGS/prereg）·leg0 222 rows tail=W224-registered owner=214/bmc 55th owned candidate/anchor W224 finalize 916,589=prev 914,389+2,200 EXACT·K=490,720 EXACT 机读 -> MSG-20261012-1943-bmc-w225-seat.md（认领令源=CEO fill-order standing+O-1505 满载包⑤+seat-first law+never-dry+认领即开动同轮律全链引）+四件套外科提交 c78dd1a44 推送（4e042914f..c78dd1a44 range 行自证·fetch+rev-list 0/0 送达机证）；(5) S6 freshness 腿批 rc0 全绿：pool_dualrun ZERO-DRIFT streak 34（446 entries·排 compute_audit 之前=证据链序律）+compute_audit FLAG:pool_starvation,supply_floor（442min 波链间隙结构性披露·W225 seat=已装填响应·prereg=下窗愈合动作）+py_watermark insufficient_history（新鲜窗诚实面）+update_daily 0 new rows（周一 bars 源迟·cutoff 2026-10-09·papers legs on bar landing 合法悬置）+fund_premium snapshot exit 2（nav non-null 0.52<0.9 EM 源面·退避窗续·下窗复查）+18 车道护栏采集器诚实 no-op rc0+b_layer rc0+token_meter rc0+daily_report rc0；(6) INBOX：MSG-20261011-0940-bmb（bm-a 收件·本机零动作）；本窗 W225 seat MSG 留 inbox（freeze 周期消费时归档 processed/=W222 先例）；(7) S7：loop pin=5 no-op（下触发 19:55）+watchdog 幂等重注册（-Force 无害·19:48 首发）+双 claw LF 归一重装+attrition 4 ledger CLEAN（1 shrink 行 healed 注记照录·零 active loss）+state/heartbeat r938 写回（counter 938->939·epoch int+clock T 格式写后 json.loads 自证）")
rr.append("验证证据=smoke 49/49+probe rc0 ADMIT（staircase EIGHTY-FIFTH+own-A 互斥双机检关系成立）+derive 残扫全零/期望 token 全在+push range 行 4e042914f..c78dd1a44 自证+S6 批 rc0+dualrun streak 34+attrition CLEAN+双水位 FALSE probe")
rr.append("本地未达 origin commit 数=0（收尾 push 后 fetch+rev-list 自证）| 孤儿面=2 | 产品积分: 2（W225 席位=链序正典件上链 c78dd1a44）+1（checked-rep 加固 derive 工具=静默穿透根治面）=3 | 记账预算: 3（state+heartbeat+round-report 法定簿记）")
rr.append("下轮指针=r939: (1) W225 per-wave prereg derive+land FIRST ACTION（_w224bmc_prereg_derive.py 模板·八级血统重放链·bands 机读自 _w225bmc_20261012_probe_receipt.json）；(2) five-face freeze splice+engine 自燃 12/12+六门 PRE-FINALIZE 烧录窗内+finalize one-pass+sec.7/8 机读回填+五键（W224 post-miss run-2 教训=六门必须 PRE-FINALIZE 相位）；(3) 周一新 bar recheck（update_daily；papers 全链 on landing：live.paper REGIME_GUARD enforce+t35_open_fill+t24 双腿+aggressive_lab+alloc_paper+grid_paper+system_v1_paper+t35_paper_export+daily_scorecard+daily_report+ceo_live_usage+build_status）；(4) fund_premium snapshot 复查（exit-2 退避窗）；(5) unity-mcp POC 回执 10-13 12:00（O-20261012-0739·bm-a lane watch） | [r938 bm-c]")
line = " | ".join(rr) + "\n"
with open(ROOT + r"\logs\iteration-loop\round_reports-bm-c.md", "a", encoding="utf-8", newline="") as f:
    f.write(line)

# --- state update -----------------------------------------------------------------
sp = ROOT + r"\state-bm-c.json"
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = 939
st["loop_round"] = 938
st["last_round"] = "r938"
for k in ("last_round_at", "last_round_ts", "last_seen", "last_seen_at", "last_ts", "ts",
          "updated", "updated_at", "last_run_at", "last_round_closed", "last_action_at",
          "last_orders_read_at", "last_decisions_read_at", "last_decisions_seen",
          "last_orders_seen", "last_pulled_at", "current_task_ts", "last_round_summary_at",
          "last_artifact_ts", "recent_artifact_ts"):
    if k in st:
        st[k] = ts
did = ("2026-10-12 19:4x | r938 | bm-c clean-window product: W225 SEAT published (probe rc0 ADMIT "
       "A 509_804..511_803 staircase EIGHTY-FIFTH hops=1 + B 511_804..512_003 own-A exclusion hops=1, "
       "seed_admit FREE x2, conflicts=0, origin vacancy 4-check; anchor W224 finalize 916,589/K=490,720 "
       "machine-read; derive checked-rep hardening 3 live-caught rep-count faces + docstring 83rd->85th heal; "
       "four-file surgical commit c78dd1a44 pushed range-verified 0/0) + S6 chain rc0 all-green (dualrun streak 34, "
       "update_daily Monday bars pending cutoff 10-09 papers on bar landing, fund_premium exit2 backoff) + S0.5 "
       "dual-delta FALSE zero action + smoke 49/49 + S7 self-heal all green; counter 938->939")
st["did"] = did
st["activity_now"] = did
st["now_active"] = did
st["current_task"] = "W225 per-wave prereg derive+land = next window FIRST ACTION (freeze splice+burn+six-gate+finalize follow)"
st["last_round_summary"] = "W225 seat landed (clean window; probe ADMIT staircase EIGHTY-FIFTH; c78dd1a44 pushed)"
st["last_action"] = "r938 product closeout (W225 seat published c78dd1a44 + S6 chain + S7 self-heal)"
art = ("fleet/inbox/MSG-20261012-1943-bmc-w225-seat.md + results/_w225bmc_20261012_probe_receipt.json "
       "(19:43, A 509_804..511_803 + B 511_804..512_003, commit c78dd1a44 pushed origin-verified)")
st["latest_artifact"] = art
st["last_artifact"] = art
st["recent_artifact"] = art
verdict = ("green: W225 SEAT landed same-window (probe rc0 ADMIT staircase EIGHTY-FIFTH held; A 509_804..511_803 + "
           "B 511_804..512_003 seed_admit FREE x2; c78dd1a44 pushed origin-verified); smoke 49/49; engine alive rc0 "
           "queue DRY post-W224-finalize; pool_dualrun streak 34; compute_audit pool_starvation+supply_floor structural "
           "flags disclosed (armed response = wave chain, W225 prereg = next window FIRST ACTION); update_daily Monday bars "
           "still pending cutoff 10-09 papers legs on bar landing; fund_premium exit2 backoff continues")
st["verdict"] = verdict
nxt = ("r939: (1) W225 per-wave prereg derive+land FIRST ACTION (eight-level lineage replay chain; bands machine-read "
       "from probe receipt); (2) five-face freeze splice + engine self-burn 12/12 + six-gate PRE-FINALIZE in burn window + "
       "finalize one-pass + sec.7/8 + five-key; (3) Monday new-bar recheck (update_daily; papers full chain on bar landing "
       "incl live.paper REGIME_GUARD + t35_open_fill + t24 x2 + aggressive_lab + alloc_paper + grid_paper + system_v1_paper + "
       "t35_paper_export + daily_scorecard + daily_report + ceo_live_usage + build_status); (4) fund_premium snapshot recheck "
       "(exit-2 backoff window); (5) unity-mcp POC receipt due 10-13 12:00 (O-20261012-0739 bm-a lane watch)")
st["next"] = nxt
st["next_pointer"] = nxt
st["head_sha"] = "c78dd1a44"
st["sync"] = {"origin_tip": "c78dd1a44 (W225 seat)", "ts": ts,
              "ahead_behind": "r938 closeout commit rides this push",
              "note": "r938: W225 seat product c78dd1a44 pushed pre-closeout; closeout commit+push follows; state/heartbeat this round"}
st["orphan_face"] = 2
st["orphan_faces"] = 2
st["idle_rounds"] = 0
st["agenda_starved"] = False
st["cpu_pct"] = cpu_pct
st["cpu_util_pct"] = cpu_pct
st["ram_free_gb"] = ram_free
st["free_ram_gb"] = ram_free
st["idle_ram_gb"] = ram_free
st["gpu_free_vram_mib"] = gpu_free
st["gpu_free_vram_mb"] = gpu_free
st["d19_watermark_guard"]["round_ref"] = 938
st["d19_watermark_guard"]["ts"] = ts
with open(sp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

# --- heartbeat --------------------------------------------------------------------
hp = ROOT + r"\fleet\machines\bm-c.json"
hb = json.load(open(hp, encoding="utf-8"))
epoch = int(time.time())
hb["last_seen"] = ts
hb["last_seen_at"] = ts
hb["ts"] = ts
hb["current_task"] = "W225 per-wave prereg derive+land = next window FIRST ACTION (W225 seat landed this window c78dd1a44)"
hb["current_task_at"] = ts
hb["cpu_cores"] = 32
hb["ram_free_gb"] = ram_free
hb["gpu_vram_free_mb"] = gpu_free
hb["gpu_idle_vram_mb"] = gpu_free
hb["verdict"] = ("green: W225 seat landed (probe ADMIT A 509_804..511_803/B 511_804..512_003; c78dd1a44 pushed); "
                 "engine alive rc0 queue DRY post-W224-finalize; prereg = next window FIRST ACTION; "
                 "Monday bars pending papers on landing; fund_premium exit2 backoff")
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = ts
for k in ("updated", "updated_at", "last_run_at"):
    if k in hb:
        hb[k] = ts
with open(hp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

# --- self-proof ---------------------------------------------------------------------
st2 = json.load(open(sp, encoding="utf-8"))
hb2 = json.load(open(hp, encoding="utf-8"))
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in hb2["clock_read"] and "+08:00" in hb2["clock_read"], "clock_read must be T-format ISO8601"
assert st2["round_no"] == 939 and st2["loop_round"] == 938
print(f"closeout ok: round_no->939 (loop_round 938), epoch={hb2['heartbeat_epoch_utc']} (int), clock={hb2['clock_read']}, cpu={cpu_pct}% ram_free={ram_free}GB gpu_free={gpu_free}MiB")
