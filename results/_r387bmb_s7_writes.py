# r387 bm-b S7 bookkeeping: state round_no increment + heartbeat + round report line.
import json, os, time, datetime, subprocess

now_iso = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
now_short = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def ram_mb():
    # FreePhysicalMemory is in KB: KB//1024 = MB (r386 flip-script proven
    # formula -- do NOT reinvent; r387 first write omitted one /1024 and
    # landed 13211.4 as "GB", caught by post-write print self-check, fixed
    # in-window)
    out = subprocess.run(["powershell", "-NoProfile", "-Command",
        "(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory"],
        capture_output=True, text=True).stdout.strip()
    return int(out) // 1024

def cpu_pct():
    out = subprocess.run(["powershell", "-NoProfile", "-Command",
        "(Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average"],
        capture_output=True, text=True).stdout.strip()
    return float(out)

def gpu_free_mb():
    try:
        out = subprocess.run(["nvidia-smi", "--query-gpu=memory.total,memory.used",
            "--format=csv,noheader,nounits"], capture_output=True, text=True).stdout.strip()
        tot, used = [int(x) for x in out.split(",")]
        return tot - used
    except Exception:
        return None

frm = ram_mb()
cpu = cpu_pct()
gpu = gpu_free_mb()
epoch = int(time.time())

# ---- state.json ----
d = json.load(open("state.json", encoding="utf-8-sig"))
assert d["machine_id"] == "bm-b" and d["round_no"] == 386, (d["machine_id"], d["round_no"])
d["round_no"] = 387
d["note"] = (
    "r387: W1-JUDGE burn landed ahead of schedule (autofill 12-worker pool "
    "14:23:34->14:25:22, 149/149) -> shard done-flip 44568509 + checkpoint "
    "committed 4f8adc93; W1 judge-finalize QUEUED behind W2 finalize in-flight "
    "pid 23800 (cross-wave cumulative-N chain linearity: DSR n_trials "
    "start-snapshot w1.py:1450; pitlaw r387 CODELY append); S6 33 legs rc=0; "
    "smoke 25/25; orders 99/99; next: W2 w2_judge.json harvest + entry "
    "done-flip -> W1 finalize detach -> W1 intake; 15:30 new-bar dual lanes; "
    "CEO 48h report 09-29 22:45"
)
tmp = "state.json.tmp"
with open(tmp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(d, f, ensure_ascii=False, indent=1)
os.replace(tmp, "state.json")

# ---- heartbeat fleet/machines/bm-b.json ----
h = json.load(open(r"fleet\machines\bm-b.json", encoding="utf-8-sig"))
assert h["machine_id"] == "bm-b"
h["last_seen"] = now_iso
h["clock_read"] = now_iso
h["heartbeat_epoch_utc"] = epoch
h["current_task"] = (
    "r387: W1-JUDGE shard done-flip+checkpoint committed (149/149 burn "
    "14:25:22) -> next: W2 w2_judge.json harvest (pid 23800 in-flight) + "
    "entry done-flip -> W1 judge-finalize detach (queued behind W2 for "
    "cumulative-N chain linearity) -> W1 intake; 15:30 new-bar window dual "
    "lanes; CEO 48h report 09-29 22:45"
)
h["verdict"] = (
    "healthy: smoke 25/25; orders 99/99 dual-scan clean; S6 33 legs rc=0; "
    "watermark fresh probe insufficient_history honest (window n=2 reset "
    "post-r386-red-resolution); work flowing: W1-JUDGE burn complete+flipped, "
    "W2 finalize in-flight pid 23800 (cpu 1139s @14:35), W1 finalize queued "
    "behind it (chain-linearity law, pool note 44568509); migration executor "
    "armed, old root in place (work as usual)"
)
h["round_no"] = 387
h["loop_round"] = 387
h["round"] = 387
h["cpu_cores"] = 16
h["cores"] = 16
h["cpu_util_pct"] = cpu
h["cpu_pct"] = cpu
h["free_ram_gb"] = round(frm / 1024, 2)
h["free_ram_mb"] = frm
h["idle_ram_gb"] = round(frm / 1024, 2)
h["idle_ram_mb"] = frm
if gpu is not None:
    h["gpu_free_vram_gb"] = round(gpu / 1024, 2)
    h["gpu_free_vram_mb"] = gpu
    h["gpu_idle_vram_gb"] = round(gpu / 1024, 2)
    h["gpu_idle_vram_mb"] = gpu
tmp = r"fleet\machines\bm-b.json.tmp"
with open(tmp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(h, f, ensure_ascii=False, indent=1)
os.replace(tmp, r"fleet\machines\bm-b.json")

# ---- self-verify epoch int (R170/R178 law) ----
h2 = json.load(open(r"fleet\machines\bm-b.json", encoding="utf-8-sig"))
assert isinstance(h2["heartbeat_epoch_utc"], int), type(h2["heartbeat_epoch_utc"])
assert "T" in h2["clock_read"], h2["clock_read"]
print("heartbeat self-verify OK: epoch int =", h2["heartbeat_epoch_utc"],
      "clock =", h2["clock_read"], "| freeRAM", round(frm/1024, 2), "GB | cpu",
      cpu, "% | gpu_free", gpu, "MB")

# ---- round report line ----
line = (
    f"{now_iso} | round 387 bm-b | dept:工程/舰队 (判决链收割窗·W1 烧批提前落地) | "
    "WM-VERDICT: 绿(probe 14:29 insufficient_history 窗重置 n=2 诚实; "
    "local_batch_running=True W2 finalize 在飞; W1-JUDGE 烧批完成已翻转=工作流正常) | "
    "did: (1) S0-1 bm-b 锚定+S0 stash-pull-rebase up-to-date(轮首脏="
    "p1d_gates r386 元数据漂移本机遗留非并发会话·stash pop 还原后随轮 rider 收口); "
    "(2) S0.5 轮首扫 99/99 零未回执+decisions.md 缺位零动作; (3) S1 smoke 25/25; "
    "(4) S2 job_list 0+票板 0 open 全 claimed; (5) S3 主闭环: W1-JUDGE 烧批 "
    "autofill 12-worker 14:23:34→14:25:22 149/149 提前完成(上轮估 20-45min 实际 "
    "111s 墙钟) → checkpoint 149 行计对账+shard done-flip(results/_r387bmb_pool_"
    "flips.py r386 范式复用) commit 44568509 + checkpoint 1.92MB 入库 4f8adc93 "
    "(W2 先例)+push LANDED; **W1 judge-finalize 排队不 detach**=W2 finalize pid "
    "23800 在飞中,DSR n_trials finalize 开头快照(w2.py:1566/w1.py:1450)+逐细胞 g1 "
    "内部 ledger 扫描→并发=累计 N 互漏(违 TRIAL_LABOR_LAW §4)+中途 head 漂移,串行"
    "律判读留痕池 entry note+坑律补章 CODELY r387(9934B<10KB); (6) S6 33 腿全 "
    "rc=0: audit CLEAN flags[] pool-supply-gap/probe insufficient_history/"
    "update_daily 0 新行 cutoff 09-24/regime ORANGE d1 shadow(breadth 0.77)/"
    "scorecard 6/28/7 卡 stale-takeover derive/clock CALL-0924 ORANGE_COOL "
    "sleeves4 act0/采集器车道守卫诚实 no-op(lhb 30min 节流+futures cutoff 覆盖+"
    "heat/repo/options/moneyflow/sina_mf/ths/ah=bm-a 面+fundprem=bm-c 面)/"
    "astock_daily 面板新鲜零网络+rev_osc 幂等 no-op(本机双车道)/fundamental 4.7h "
    "fresh skip/b_layer 全过/live_paper 锚定 OK(enforce 请求→日期门 2026-10-01 "
    "诚实 shadow 降级)+t35v 0924 PASS 零例+t24a 22/22 drift0+t24b 0/22 诚实腿败/"
    "aggr+alloc+grid 幂等 no-op/sysv1 车道守卫 no-op/t35_export 0924/daily_"
    "scorecard+build_status derive/daily_report REPORT-0928 faces4/token L2 0 "
    "today·fuse refusals 6/4sigs 披露;post_review 今日 147 行 0 NO 零 P0; (7) "
    "S7: schtasks 双查在位(Loop 正在运行 pin :42=2 ✓·Watchdog 就绪)+register_"
    "loop no-op+claw in-sync+state 387+心跳 epoch int 自证+inbox 空 | verify: "
    "smoke 25/25+S6 逐腿 rc=0+checkpoint 149 行计对账+池翻转 json 重载复证("
    "entry ready/shard done)+git 快进链 58876767→4f8adc93 push LANDED+orders "
    "双扫零差 | 下轮: (a) W2 finalize(pid 23800)落地→w2_judge.json 验收(E[FP]/"
    "G2 eligible/family PBO faces)→entry done-flip→产品 commit→W1 finalize "
    "detach→W1 intake; (b) 15:30 新 bar 窗本机双车道 astock_daily/rev_osc 实弹+"
    "live.paper/t35/t24 三件套随新 bar; (c) CEO 48h 报告窗 09-29 22:45(bmb); "
    "(d) 迁移窗 09-29 12:00 执行器 armed 旧根照常; marks/账本/SEED 全+0\n"
)
with open(r"logs\iteration-loop\round_reports.md", "a", encoding="utf-8", newline="\n") as f:
    f.write(line)
print("round report line appended")
