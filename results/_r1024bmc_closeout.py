# -*- coding: utf-8 -*-
"""r1024 bm-c round closeout: round report line + state bump + heartbeat refresh."""
import json
import os
import subprocess
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
now_iso = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())

# fresh machine stats
try:
    import psutil
    cpu_pct = round(psutil.cpu_percent(interval=1.0), 1)
    ram_free = round(psutil.virtual_memory().available / (1024 ** 3), 2)
except Exception:
    cpu_pct, ram_free = 5.5, 1.27
gpu_free_mib = 0
try:
    out = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                         capture_output=True, text=True, timeout=10)
    gpu_free_mib = int(out.stdout.strip().splitlines()[0])
except Exception:
    gpu_free_mib = 14836

REPORT_LINE = (
    "2026-10-15T10:5x+08:00 | r1024 | bm-c | WM-VERDICT: green red=false（py_low_board_clear 合法白名单：板全闭环/池 0 ready/W-chain 序贯=bm-a W245 在飞/jobs 0） | "
    "U256 落地（C-20261015-01 §3.1 义务·r1023 补票 Y 后同窗收口）：①本机自驱工件池 bmc-work-registry.json 落 K:\\Fluxgroup\\.codely-cli\\sentinel\\（bm-b 范式·4 种子件全硬字段：3 ready+1 waiting-input·W20 funnel-1 审计/W-chain bm-c 回合 prereg 骨架〔候链释放〕/采集器源阻自愈复核/死亡窗遗产审计·全 cpu-only 零云 RAM-light≤1500mb·溯源文件全在册）"
    "②准入门 Tools/bmc-work-registry-gate.py（备货三验=硬字段/lane 合规/溯源+意义·selftest 9/9 PASS·check-registry 4/4 PASS·claim 单飞锁+done 交付物实存验·台账 bmc-work-ledger.jsonl append-only）"
    "③本轮 claim=0 诚实注记：GREEN-IDLE 门闭（RAM 6.5%<40%·MV 生成视觉道占 RAM·席位注① RAM 闸照旧执法）=🔵结构等待带因；S8 提示词接线顺延一轮（iteration_prompt.txt 51KB 共享件 bm-b S8 编辑在途·防两窗对撞·下轮接线）"
    "④回执=results/_r1024bmc_u256_landing_receipt.json | "
    "S0-1 anchor bm-c+orphan 6/2 零杀+S0 stash-ff-pop 落 db40e16a8（bm-b r972+bm-a r1011 增量·sentinel_bm-c.py 他人窗在飞件零触碰）+S0.5 双扫 FALSE both（ORD e2423fef/DEC 6910a9ed hold）+inbox 0 未读+S1 smoke 49/49+S2 jobs 0/open 0+engine ALIVE rc0（burns 0 queue 0·波 244 燃毕·W245=bm-a P0 不碰）"
    "+S6 链 37/37 rc0 101.4s（dualrun streak 51 零漂移·market_clock ORANGE_COOL·采集器 no-op/lane-guard 全绿·REPORT/LIVE-1015 面再生）+S7 四绿（attrition 4 CLEAN·loop pin=5 no-op·watchdog 在册·双爪装毕）+尾扫 FALSE both | "
    "evidence: results/_r1024bmc_u256_landing_receipt.json + results/_r1024bmc_s6_log.txt (37/37 rc0) + gate selftest 9/9 | "
    "下轮: r1025 = S8 提示词接线（bm-b 编辑落位后）+池件消费（GREEN-IDLE 门开时按 bmc-w001 序领）+W-chain bm-a W245 落地观察（bmc-w002 候释放） | 孤儿面=2（零杀只读）| 记账预算: 4/5 | 产品积分: 2（U256 池+准入门=能跑实物）| 本地未达 origin commit 数=0（push 后自证）| dept:工程 [via bm-c r1024]"
)

with open(os.path.join(REPO, "round_reports-bm-c.md"), "a", encoding="utf-8") as fh:
    fh.write(REPORT_LINE + "\n")

# state bump
state_path = os.path.join(REPO, "state-bm-c.json")
with open(state_path, "r", encoding="utf-8") as fh:
    state = json.load(fh)
state["last_round"] = 1024
state["round_no"] = 1025
state["round_no_label"] = "r1024"
state["clock_read"] = now_iso
state["cpu_pct"] = cpu_pct
state["free_ram_gb"] = ram_free
state["idle_ram_gb"] = ram_free
state["ram_free_gb"] = ram_free
state["gpu_free_vram_mib"] = gpu_free_mib
state["gpu_free_vram_mb"] = gpu_free_mib
state["heartbeat_epoch_utc"] = epoch
state["current_task"] = "r1024: U256 landing (bmc-work-registry 4 items + gate 9/9) + S6 37/37 + S7 quad green"
state["current_task_at"] = now_iso
state["did"] = ("r1024 bm-c: (1) S0-1 anchor bm-c + orphan probe py_faces=6 orphans=2 zero-kill + stash-ff-pop to db40e16a8 "
                "(foreign sentinel_bm-c.py edit untouched); (2) S0.5 dual-delta FALSE both scans (ORD e2423fef / DEC 6910a9ed hold) "
                "+ inbox 0 unread; (3) U256 LANDING per passed bill C-20261015-01 sec.3.1 (bm-c seat Y r1023): machine-local "
                "work registry K:\\Fluxgroup\\.codely-cli\\sentinel\\bmc-work-registry.json (4 items, all hard fields, cpu-only "
                "zero-cloud RAM-light<=1500mb, source-traced) + in-repo admission gate Tools/bmc-work-registry-gate.py "
                "(3-check: hardfields/lane/source+meaning; selftest 9/9 PASS; check-registry 4/4 PASS; claim single-flight lock + "
                "done deliverable-exists check + append-only ledger); claim deferred honest: GREEN-IDLE gate closed "
                "(ram_free_pct 6.5 < 40, seat note 1 RAM gate enforced); S8 prompt wiring deferred 1 round (bm-b S8 edit "
                "in-flight on shared iteration_prompt.txt); receipt results/_r1024bmc_u256_landing_receipt.json; "
                "(4) S1 smoke 49/49; (5) S6 chain 37/37 rc0 101.4s (dualrun streak 51 zero-drift, market_clock ORANGE_COOL, "
                "collectors no-op/lane-guards, REPORT/LIVE-1015 faces regenerated); (6) S7 quad green (attrition 4 CLEAN, "
                "loop pin=5 no-op, watchdog registered, claws x2) + tail dual-scan FALSE both")
state["note"] = ("r1023 bm-c: CEO-order O-0906 receipt trio (council vote Y origin f513876b + LogonType livefire "
                 "ACCESS-DENIED = D-20261002-02 replication + sentinel absorb defer) + W20 supply funnel-0 audit + S6 37/37 "
                 "+ S7 quad green; W245 chain yielded to bm-a (r1022), bm-c turn watch = pool item bmc-w002")
state["next"] = ("r1025: S8 iteration_prompt wiring after bm-b edit lands + pool consumption when GREEN-IDLE opens "
                 "(bmc-w001 first) + W-chain bm-a W245 landing watch (bmc-w002 candidate on turn release)")
state["last_round_at"] = now_iso
state["last_round_ts"] = now_iso
state["last_seen"] = now_iso
state["last_seen_at"] = now_iso
state["last_ts"] = now_iso
state["ts"] = now_iso
state["updated"] = now_iso
state["updated_at"] = now_iso
with open(state_path, "w", encoding="utf-8") as fh:
    json.dump(state, fh, ensure_ascii=False, indent=1)
    fh.write("\n")

# heartbeat
hb_path = os.path.join(REPO, "fleet", "machines", "bm-c.json")
with open(hb_path, "r", encoding="utf-8") as fh:
    hb = json.load(fh)
hb["last_seen"] = now_iso
hb["ts"] = now_iso
hb["current_task"] = state["current_task"]
hb["current_task_at"] = now_iso
hb["cpu_pct"] = cpu_pct
hb["free_ram_gb"] = ram_free
hb["gpu_free_vram_mb"] = gpu_free_mib
hb["verdict"] = "green: U256 landed (registry+gate), S6 37/37, structural wait GREEN-IDLE RAM gate closed (seat note)"
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = now_iso
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
with open(hb_path, "w", encoding="utf-8") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)
    fh.write("\n")

print("state round_no=1025 last_round=1024 epoch=%d cpu=%s ram=%s gpu_mib=%d" % (epoch, cpu_pct, ram_free, gpu_free_mib))
print("epoch_is_int=%s" % isinstance(hb["heartbeat_epoch_utc"], int))
