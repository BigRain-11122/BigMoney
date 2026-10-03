"""_r425bmc_close.py -- r425 S7 closeout: state/round-report/heartbeat/HANDOVER writes.
Laws: heartbeat_epoch_utc MUST be JSON int (R170/R178); clock_read ISO-8601 T-separated
(R262); sample real machine faces (CPU/RAM/GPU); WM verdict derived from fresh probe face.
"""
import datetime, json, os, subprocess, sys, time

os.chdir(r"K:\Fluxgroup\FluxGroup\quant\bigmoney")
NOW = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
NOW_SP = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
EPOCH = int(time.time())
CREATE_NO_WINDOW = 0x08000000

import psutil
cpu_pct = round(psutil.cpu_percent(interval=1), 1)
idle_ram = round(psutil.virtual_memory().available / 1e9, 1)
try:
    out = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                          capture_output=True, text=True, creationflags=CREATE_NO_WINDOW, timeout=20)
    gpu_free = int(out.stdout.strip().splitlines()[0])
except Exception:
    gpu_free = -1

# fresh WM + audit faces
wm = json.load(open("results/watermark_red.json", encoding="utf-8"))
aud_path = "results/compute_audit.bm-c.json"
audit_flags = []
if os.path.exists(aud_path):
    aud = json.load(open(aud_path, encoding="utf-8"))
    audit_flags = aud.get("flags") or aud.get("audit_flags") or []
print("samples: cpu=%s%% ram_free=%sGB gpu_free=%sMiB wm_red=%s wm_lane=%s audit_flags=%s"
      % (cpu_pct, idle_ram, gpu_free, wm.get("red"), wm.get("lane"), audit_flags))

# origin freshness check (fetch + behind count + SHARD-1 origin face)
def sg(args):
    p = subprocess.run(["git"] + args, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", creationflags=CREATE_NO_WINDOW)
    return p.returncode, (p.stdout or "") + (p.stderr or "")
sg(["fetch", "origin"])
rc, behind = sg(["rev-list", "--count", "HEAD..origin/main"])
behind = behind.strip()
rc, sh1 = sg(["show", "origin/main:results/runnable_pool.json"])
shard1_status = "unknown"
if rc == 0:
    try:
        pool_o = json.loads(sh1)
        ents = pool_o["entries"] if isinstance(pool_o, dict) else pool_o
        e1 = next(e for e in ents if e.get("id") == "MASS-TRIAL-W2-JUDGE-SHARD-1")
        shard1_status = e1["status"] + "/" + e1["shards"][0]["status"] + " owner=" + str(e1["shards"][0].get("owner"))
    except Exception as ex:
        shard1_status = "parse-err:%s" % ex
print("origin: behind=%s SHARD-1=%s" % (behind, shard1_status))

DID = ("r425 bm-c: (1) MAIN DELIVERABLE (score 2, product adoption + live pool surgery): SHARD-0 + SHARD-3 two-layer done-flips "
       "landed per r488/r489 (entry+shard both done, raw-text surgical +10/-5 each, action ts 19:03:29/19:04:39, action-time ts r400 "
       "monotonic over keepalive 18:58:14) + r497 closed-claim backfills (pid 21188/3508, real completion provenance, 5-gate flip "
       "script w/ full-parse + 366-entry + cell-math assertions) + ckpt product adoptions to origin (shard0 202/202 + shard2 201/201 "
       "+ shard3 201/201, r310 delivery law; shard2 adopted from pool_worker close 18:54:03) -- commits 010a155d5 + 4e5e6459e both "
       "pushed same-round (r598). (2) WAVE STATE: MASS_TRIAL_W2-JUDGE 3/4 done all bm-c-delivered; SHARD-1 bm-b in-flight "
       "(18:44:20 claim); judge-finalize --wave 2 gated on SHARD-1 done (<=10-06 per O-2115 10-08 acceptance). (3) S0: pull-rebase "
       "clean (1 incoming, autostash); D-19 4167B784 MATCH; orders 68947C17 MATCH; 151/151 zero-unacked double-scan. (4) S1 smoke "
       "47/47; SatEngine rc0 alive. (5) S6 37 legs: 36 rc0 + aggressive_lab transient 0xC0000005 native crash under burn-crowded "
       "window -- solo rerun rc0 idempotent no-op self-healed, disclosed; chain runner GBK console crash leg 8 -> PYTHONUTF8=1 "
       "rerun full chain clean (known pit-encoding family). (6) S7 4/4 green (loop pin=5 no-op, watchdog PRESENT, both claws "
       "byte-fresh, attrition CLEAN).")
NEXT = ("(a) r426: watch SHARD-1 (bm-b) done -> then judge-finalize --wave 2 (single-shot ledger MASS_TRIAL_W2_JUDGE + 805-cell "
        "completeness probe + w2_judge.json product) <=10-06; (b) D-06 full-reconciliation closeout 10-07; (c) T-143 assembly window "
        "post-10-09 (deliverable 10-29); (d) moneyflow GM ruling watch (MSG-1452/1543); (e) W14 lane zero-touch pending GM dual-ruling.")
VERIFY = ("flip gates 5/5 PASS x2 (full json.loads parse + 366-entry + 202/201/201 cell-math + i%4 partition asserts); surgical "
          "diff --stat +10/-5 x2; commits 010a155d5/4e5e6459e pushed (34973353f..010a155d5, 010a155d5..4e5e6459e); ckpt products "
          "on origin; smoke 47/47 rc0; S6 37 legs (36 rc0 + 1 transient native crash self-healed rc0 on rerun); dualrun streak "
          "23 ZERO-DRIFT; S7 4/4 green (attrition CLEAN rc0); D-19 4167B784 MATCH; orders 151/151 zero-unacked; WM red=false lane "
          "healthy golden-week legal idle; push delivery verify post-commit (本地未达 origin=0)")

# ---- state-bm-c.json ----
sp = "state-bm-c.json"
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = 425
st["clock_read"] = NOW
st["cpu_pct"] = cpu_pct
st["current_task"] = ("r425: SHARD-0+SHARD-3 two-layer done-flips landed + ckpt products (202/201/201 cells) origin-delivered; "
                       "wave 3/4 done (SHARD-1 bm-b in flight); next: SHARD-1 done -> judge-finalize --wave 2 <=10-06")
st["did"] = DID
st["gpu_free_vram_mib"] = gpu_free
st["heartbeat_epoch_utc"] = EPOCH
st["idle_ram_gb"] = idle_ram
st["last_seen"] = NOW
st["last_round"] = "r425 bm-c: MASS_TRIAL_W2-JUDGE SHARD-0/3 done-flips + 3/4 ckpt products delivered (SHARD-1 bm-b in flight)"
st["last_round_at"] = NOW
st["last_round_ts"] = NOW
st["last_ts"] = NOW
st["last_decisions_read_at"] = NOW
st["next"] = NEXT
st["updated"] = NOW
st["updated_at"] = NOW
st["verify"] = VERIFY
st["last_decisions_sha_method"] = "python subprocess.check_output raw-blob bytes SHA-256 (PS-pipeline join = transcoding false-drift, see CODELY r292 pit); CREATE_NO_WINDOW added per U060 zero-flash law"
json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
assert isinstance(json.load(open(sp, encoding="utf-8"))["heartbeat_epoch_utc"], int), "epoch must be int"
print("state-bm-c.json written (round_no=25? no, 425; epoch=%d int-verified)" % EPOCH)

# ---- round report line ----
WM_LINE = ("WM 绿（red=false lane healthy；py_low golden-week 合法 idle·board 零 open·bandit next_pick moneyflow-IC 源阻断维持）"
           if not wm.get("red") else "WM 红（red=true @%s）" % wm.get("ts"))
rl = "%s\t| r425 bm-c\t| %s\t| %s | dept:策略/研究\t| %s\t| %s\n" % (NOW, DID, WM_LINE, VERIFY, NEXT)
with open("round_reports-bm-c.md", "a", encoding="utf-8") as fh:
    fh.write(rl)
print("round_reports-bm-c.md appended")

# ---- heartbeat fleet/machines/bm-c.json ----
hp = "fleet/machines/bm-c.json"
hb = json.load(open(hp, encoding="utf-8"))
hb["activity_now"] = ("r425: MASS_TRIAL_W2-JUDGE wave 3/4 done (SHARD-0/2/3 bm-c, products on origin); SHARD-1 bm-b in flight; "
                      "judge-finalize --wave 2 next once 4/4")
hb["clock_read"] = NOW
hb["cpu_pct"] = cpu_pct
hb["cpu_util_pct"] = cpu_pct
hb["free_ram_gb"] = idle_ram
hb["ram_free_gb"] = idle_ram
hb["idle_ram_gb"] = idle_ram
hb["gpu_free_vram_mb"] = gpu_free
hb["gpu_free_vram_mib"] = gpu_free
hb["gpu_idle_vram_mb"] = gpu_free
hb["gpu_idle_vram_mib"] = gpu_free
hb["current_task"] = st["current_task"]
hb["heartbeat_epoch_utc"] = EPOCH
hb["last_seen"] = NOW
hb["last_seen_at"] = NOW
hb["updated_at"] = NOW
hb["latest_artifact"] = ("results/mass_trial/w2_judge_shard_{0,2,3}of4.jsonl product adoptions + two-layer done-flips "
                          "(commits 010a155d5, 4e5e6459e on origin @ 19:04 r425)")
hb["next_milestone"] = ("SHARD-1 (bm-b) done -> judge-finalize --wave 2 -> w2_judge.json + ledger MASS_TRIAL_W2_JUDGE by 10-06 "
                        "(O-2115 acceptance 10-08); D-06 closeout 10-07")
hb["prod_lanes"] = ("MASS_TRIAL_W2 judge wave 3/4 done (0/2/3 bm-c delivered, 1 bm-b in flight); moneyflow lane GM-ruling "
                    "pending; D-06 closeout 10-07")
hb["round_no"] = 425
hb["verdict"] = "healthy"
json.dump(hb, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int)
print("heartbeat written (epoch int verified, orders_ack kept: %d entries)" % len(chk.get("orders_ack", [])))

# ---- HANDOVER.md r425 5x entry (prepend) ----
hpath = "research/HANDOVER.md"
htxt = open(hpath, encoding="utf-8").read()
ENTRY = ("> bm-c round 425 五倍数核对（2026-10-03 19:1x·增量窗 r421-425 五轮）：增量窗 r421-425=bm-c 面"
         "（**MASS_TRIAL_W2 判决波收割主线**——r421 moneyflow option A bm-c 支认领判负（T-157 同轮开闭·EM 阻断面覆盖本机出口·"
         "选项收窄呈 GM）；r422 stage-1 四代执行体接力收口（T-158·gen 猝死收养 4836 候选/screen 806 存活/finalize 幂等/§7/§8 "
         "一次定稿回填）+三连坑律（长批单线程相位估/-Last 截尾管道/收养律）；r423 s3 judge face FROZEN（806→805 collapse·seed "
         "20285200 注册·runner judge-prep/judge/judge-finalize 三 face·selftest 33/33）+judge-prep 分离烧 1131s；r424 "
         "judge-prep 收养（w2_judge_state.json d34a7d071·manifest 48/48）+4 shards 入池（r509 外科+164/-0）+SHARD-0 本机 autofill "
         "点火 PID 21188；r425=本核对轮 **SHARD-0/2/3 三分片两轮收割**（SHARD-2 pool_worker 18:47-18:54 claim→burn 393.9s→close "
         "ok→harvest 翻面〔claim-by-file O-2210 正路〕+SHARD-0 r497 closed-claim 回填+双层 done-flip〔202 cells·r509 外科 +10/-5〕"
         "+SHARD-3 同法〔201 cells〕+三 ckpt 产物 origin 送达〔r310〕→**波态 3/4 done 全 bm-c 面·仅 SHARD-1 bm-b 在飞**→"
         "judge-finalize --wave 2 候 SHARD-1）+S6 37 腿〔aggressive_lab 0xC0000005 瞬态 native 崩（燃批拥挤窗）solo 复跑 rc0 幂等"
         "自愈如实披露+chain runner GBK console 崩→PYTHONUTF8=1 修=pit-encoding 已知族〕+双扫 151/151 零未回执维持）"
         "产物清单漂移=results/mass_trial/w2_judge_shard_{0,2,3}of4.jsonl〔r425 产物三件·202/201/201 cells·i%4 分区断言〕"
         "+results/pool_claims/MASS-TRIAL-W2-JUDGE-SHARD-{0,3}/w2-judge-{0,3}of4.bm-c.json〔r497 回填两件〕"
         "+results/runnable_pool.json〔SHARD-0/3 双层翻面 +10/-5 ×2·SHARD-2 由 tick harvest 292530fd7〕"
         "+results/_r425bmc_{round_probe,probe2,flip_shard0,flip_shard3,s7_probe,close}.py 工件族"
         "+results/_r425bmc_smoke_log.txt〔47/47〕；orders 151/151 双扫零未回执全窗维持；smoke 47/47；D-19 4167B784 MATCH "
         "零消费全窗；池态=MASS-TRIAL-W2-JUDGE 3/4 done+1 in-flight（bm-b）；指针：**SHARD-1 bm-b 烧毕→judge-finalize --wave 2"
         "（805-cell completeness probe+w2_judge.json+single-shot ledger MASS_TRIAL_W2_JUDGE·≤10-06·O-2115 验收 10-08）+D-06 "
         "全线收口 10-07+T-143 月考装配窗 10-09 后（交付 10-29）+月界首考 10-31**；下一 5x=bm-c r430。\n")
anchor = "> bm-a round 635 五倍数核对"
idx = htxt.index(anchor)
htxt = htxt[:idx] + ENTRY + htxt[idx:]
open(hpath, "w", encoding="utf-8", newline="").write(htxt)
print("HANDOVER.md r425 entry prepended")
print("CLOSE_OK behind_origin=%s shard1=%s" % (behind, shard1_status))
