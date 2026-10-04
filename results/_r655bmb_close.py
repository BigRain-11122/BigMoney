# -*- coding: utf-8 -*-
"""r655 bm-b closeout: state.json round increment + heartbeat + round report
append. Programmatic writes only (json.dump), json.loads self-verify after
every write (r645 trailing-comma law; R170/R178 epoch-int law)."""
import datetime
import json
import os
import subprocess

RB = os.getcwd()
NOW = datetime.datetime.now().astimezone().replace(microsecond=0)
CLOCK = NOW.isoformat()
EPOCH = int(NOW.timestamp())


def jload(p):
    with open(p, "rb") as f:
        return json.loads(f.read().decode("utf-8"))


def jdump(p, obj):
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=True, indent=1)
        f.write("\n")
    jload(p)  # self-verify parse


# ---------- 1) round report append (mixed-encoding file: utf-8, no CRLF xlation) ----------
block = f"""{CLOCK} | round 655 (bm-b, dept:工程/研究+数据): watermark verdict=GREEN (red=false; engine alive rc0 idle; dualrun ZERO-DRIFT streak 47; py 62-86% 三族烧批占用合法)
当前活: FUND 三族 NULLS 烧录在飞 Q480/V634/D343 of 2000 推进 dup_k=0 三 pid 实活（34396/57116/30208）；readiness r655 复跑 07:34（60s 双采样：D 窗内 1.00/min·Q/V lumpy 零速窗如实记）+ 30min 趋势 ~0.33-0.40/min/族 → ETA V~10-06 14:00/Q~10-07 12:00/D~10-07 20:00 全落 finalize 窗 10-05..10-09 且早于 10-09 12:00 提速评估线 → 按 r647 既定决策续 watch 不提速；G-SEG GM 裁决 G4 PENDING 等待态一行声明不重扫·r638 insufficient-sample fallback armed
最近实物: ①P2 自动复盘点火复线 research/auto/retro-20261004.md 07:42 落盘（自 09-27 dormant 根因定谳=llm_assist retro 腿 prompt 随账本增长撑爆 NUM_CTX 8192〔实测 8715 tok exceed_context_size_error〕——单行修 dashboard chunk 3000→1800 后 retro GREEN·本地 L1 零 cloud token）②readiness 探针刷新 results/finalize_trio_readiness.json 07:34（Q480/V634/D343 dup_k=0·G1=F·G2/G3=T〔bm-a r662 06:14:56 演练 x3 消费·age 0.0d〕·G4=PENDING·mechanical_ready=false）③S6 34 腿 rc0（dualrun streak 47·update_lhb 真拉取 11/11·REPORT/LIVE-20261004 当日幂等再生）
下个里程碑: 三族烧满 2000 → mechanical_ready=true → finalize+E1 判决落窗 10-05..10-09（V 最早 ~10-06 14:00 实测趋势 ETA；G-SEG 无裁决走 r638 单读判决）；窗 ≤48h 首查=烧录完成度+G4 裁定面
做了什么: S0 轮首脏=daemon treadmill 8 面 → absorb 92fc45ef9 + merge origin bm-c r450 波 d7892a844（dirty∩origin 交集空·r437 treadmill merge 律·merge 后 marker 双查净）；S0.5 令双扫 152/152 零差（basename 同口径）+ D-19 sparse-clone fallback 双 MATCH 零消费（K:/C: 集团树双缺 .git·r631 配方·decisions=EB14B510/orders=82A0CEF9）；S1 47/47；S2 板 165 票 0 open·job_list 空；S3 门全绿（WM red=false·engine alive rc0 idle·next_pick moneyflow IC claimed-by-other 不碰·三族烧批在飞=常设线满足）+ inbox 5 件重验零债（bm-a r659 已搬 processed/：MSG-0135 两面回执消费〔decisions 回退=瞬态自愈 append-only 完好·post_review 已绿〕·W115 unpark/THEME_PERSIST/G2_SLOT_MON_P2 三认领声明均他机线零重叠）+ 假并发警报闭案（r643 三证：.out 转录自匹配=本人即 07:22 tick·PS 双 Format-Table 空首表错读坑入册）+ P2 retro 复线修复与点火；S6 34 腿 rc0（周末/国庆 no-op 族诚实·条件三件套跳过 latest=2026-09-30·t35_export/daily_scorecard/build_status stale-takeover derive per STALE_MIN law〔bm-a 心跳 80min 陈旧〕）；S7 loop pin=2 no-op+watchdog 07:44 首发注册+双爪重装幂等+attrition 4 ledger CLEAN+post_review 官方 run YES=45/NO=0/WAIT=5
验证证据: S6 per-leg 探针清单 34/34 rc=0（evidence results/_r655bmb_s6_evidence.txt）；smoke 47/47；dualrun ZERO-DRIFT streak 47（366 entries）；readiness 探针 07:34 实弹 JSON（elapsed 60.0s·dup_k=0 x3）；BURNPROC pids 34396/57116/30208 三活实证；retro 腿 GREEN（retro-20261004.md 落盘+llm_assist py_compile rc0）；post_review YES=45 NO=0；attrition scan CLEAN（results/_attrition_guard_scan.json）；令双扫+S7 复扫 152/152 零差·D-19 双 MATCH；token delta=0（cloud）·L2 本地腿 2 today；state/心跳 json.loads 双自证 epoch int·clock T 分隔
下轮指针: r656 = 续烧看位 watch+readiness 复跑（mechanical_ready=true 且烧尽 → 执行三族 finalize+E1；G-SEG 无裁决走 r638 fallback）；D/Q lumpy 节奏观察续行，任一族 ETA>10-09 12:00 即走合规护栏（非可数文件地方动作 r630 / redo-k-lo/hi 切片 r611）；W14-GENERATE 治理停泊待 GM 解冻一行声明；retro 复线健康纳入 watch（若再 dormant 先实测腿尺寸勿假设）
本地未达 origin commit 数=0（以收尾 push_verify 输出为准；失败则 addendum 留痕）
"""
p = "logs/iteration-loop/round_reports.md"
with open(p, "a", encoding="utf-8", newline="") as f:
    f.write(block + "\n")
print("round report appended")

# ---------- 2) state.json ----------
sp = os.path.join(RB, "state.json")
st = jload(sp)
st["round_no"] = st.get("round_no", 0) + 1
st["round_no_label"] = "round %d (bm-b)" % st["round_no"]
st["note"] = ("r655: P2 retro line revival + trio watch -- S0 absorb+merge bm-c r450 wave "
              "(empty intersection, r437 law); S0.5 orders 152/152 + D-19 double MATCH zero-consume "
              "(sparse-clone fallback, K:/C: group trees both absent .git); S1 47/47; S2 board 0 open; "
              "S3 gates green (WM red=false; engine alive rc0 idle; next_pick claimed-by-other; trio "
              "burns in-flight satisfy trial-labor line); inbox 5 re-verified zero-debt (bm-a r659 moved "
              "them; MSG-0135 receipts consumed); r643 false-concurrency alarm closed (I am the 07:22 "
              "tick; PS dual Format-Table empty-first-table misread pit logged); P2 retro root-caused "
              "(prompt 8715tok > NUM_CTX 8192 since ledger growth = dormant since 09-27) + one-line fix "
              "(dashboard chunk 3000->1800) + retro-20261004.md landed via local L1; readiness probe "
              "07:34 Q480/V634/D343 dup_k=0 G1=F G2/G3=T (bm-a r662 rehearsal consumed, age 0.0d) "
              "G4=PENDING, 30-min trend ETAs V~10-06 14:00/Q~10-07 12:00/D~10-07 20:00 all in-window, "
              "watch continues per r647; S6 34 legs rc0 (dualrun streak 47; LHB real fetch 11/11; "
              "weekend no-op family; stale-takeover derive per STALE_MIN law); post_review YES=45/NO=0; "
              "attrition CLEAN; S7 pin=2 no-op + watchdog + claws reinstalled").replace('"', "")
st["last_round_at"] = st["ts"] = st["updated"] = st["last_seen"] = st["clock_read"] = CLOCK
jdump(sp, st)
print("state.json round_no =", st["round_no"])

# ---------- 3) heartbeat ----------
hp = os.path.join(RB, "fleet", "machines", "bm-b.json")
h = jload(hp)
h["round_no"] = st["round_no"]
h["round_no_label"] = st["round_no_label"]
h["last_seen"] = h["ts"] = h["updated"] = h["clock_read"] = CLOCK
h["heartbeat_epoch_utc"] = EPOCH
h["current_task"] = ("FUND trio NULLS burn watch (Q480/V634/D343 of 2000 advancing dup_k=0 pids "
                     "34396/57116/30208 alive, trend ETA V~10-06 14:00/Q~10-07 12:00/D~10-07 20:00 all "
                     "in finalize window 10-05..10-09; finalize fires on mechanical_ready w/ r638 "
                     "fallback; G-SEG GM ruling G4 PENDING) + r655: P2 retro line revived (ctx-overflow "
                     "root cause fixed, retro-20261004.md landed), readiness probe 07:34, S6 34 legs rc0")
h["verdict"] = ("GREEN (smoke 47/47; D-19 decisions+group-orders double MATCH zero-consume; fleet orders "
                "152/152 double-scan zero-diff; WM red=false; engine alive rc0 idle; dualrun ZERO-DRIFT "
                "streak 47; S6 34 legs rc0; post_review YES=45/NO=0; attrition CLEAN; trio burns healthy "
                "dup_k=0 x3 pids alive; P2 retro line revived via local L1 zero cloud token)")
try:
    import psutil
    vm = psutil.virtual_memory()
    h["free_ram_gb"] = h["idle_ram_gb"] = h["ram_free_gb"] = h["ram_avail_gb"] = round(vm.available / 1e9, 2)
    h["total_ram_gb"] = h["ram_gb"] = round(vm.total / 1e9, 2)
    h["cpu_util_pct"] = psutil.cpu_percent(interval=0.5)
except Exception:
    pass
try:
    r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                       capture_output=True, text=True, timeout=10,
                       creationflags=0x08000000)
    mib = int((r.stdout or "").strip().splitlines()[0])
    h["gpu_idle_vram_gb"] = h["gpu_free_vram_gb"] = round(mib / 1024.0, 2)
    h["gpu_idle_vram_mb"] = h["gpu_free_vram_mb"] = mib
    h["gpu_vram_free"] = mib
    h["gpu_free_vram_mib"] = mib
except Exception:
    pass
jdump(hp, h)
back = jload(hp)
assert isinstance(back["heartbeat_epoch_utc"], int), "epoch not int"
assert "T" in back["clock_read"], "clock not T-separated"
print("heartbeat updated; epoch int + clock T verified")
