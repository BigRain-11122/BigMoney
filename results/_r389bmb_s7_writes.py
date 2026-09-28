# r389 bm-b S7 bookkeeping: state round_no increment + heartbeat + round report line.
# r387 paradigm verbatim (proven unit-conversion formulas -- do NOT reinvent).
import json, os, time, datetime, subprocess

now_iso = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
now_short = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def ram_mb():
    # FreePhysicalMemory is in KB: KB//1024 = MB (r386 flip-script proven
    # formula -- do NOT reinvent; r387 first write omitted one /1024)
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
assert d["machine_id"] == "bm-b" and d["round_no"] == 388, (d["machine_id"], d["round_no"])
d["round_no"] = 389
d["note"] = (
    "r389: W3-JUDGE burn complete 513/513 (autofill claim 15:00:01 pid 4604, "
    "checkpoint last-write 15:13:44 clean exit) -> shard done-flip dual-face "
    "(shared+lane, 513/513 evidence asserted); judge-finalize detached pid "
    "28400 @15:21:53 log logs/w3_judge_finalize_r389.log (r386 detach law; "
    "first inline attempt 15:15 auto-killed by 5min no-output wall = r386 "
    "law re-hit, zero side effects verified: append_ledger pure + "
    "w3_judge.json absent = kill clean, rerun idempotent-safe) -> harvest "
    "next round; entry done-flip deferred to finalize receipt (r386 W2 "
    "precedent); S6 33 legs rc=0; smoke 25/25; orders 99/99 double-scan "
    "clean; post_review 0 unresolved NO = zero P0; next: W3 finalize "
    "harvest (w3_judge.json E[FP]/G2/family-PBO receipt) -> entry done-flip "
    "-> W3 intake slice build (prereg sec.6 mirror W2 cmd_intake face) -> "
    "intake live fire; serial queue behind W3 finalize: MASS x4 burns -> "
    "DC-V2 -> W4-JUDGE (r369 serial + r387 same-chain finalize serial law -- "
    "ALL judge-finalize runs DETACHED per r386, never inline); 15:30 new-bar "
    "dual lanes; CEO 48h report 09-29 22:45"
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
    "r389 done: W3-JUDGE burn 513/513 complete + shard done-flip dual-face "
    "(shared+lane) + judge-finalize DETACHED pid 28400 @15:21:53 burning "
    "(r386 detach law; inline 5min-wall re-hit documented zero-side-effects) "
    "-> next: w3_judge.json harvest + entry done-flip + W3 intake slice "
    "build (mirror W2 cmd_intake) + intake live fire; then serial queue "
    "MASS x4 -> DC-V2 -> W4-JUDGE (all finalizes DETACHED per r386 law, "
    "same-chain serial per r387); 15:30 new-bar dual lanes; CEO 48h report "
    "09-29 22:45"
)
h["verdict"] = (
    "healthy: smoke 25/25; orders 99/99 (S0.5+S7 double-scan zero unacked); "
    "S6 33 legs rc=0 (pre-15:30 collectors honest no-op; live_paper anchor "
    "OK enforce->2026-10-01 date-gate shadow; t35v PASS zero-pending; t24 "
    "22/22 drift 0; daily_report REPORT-20260928 landed); watermark probe "
    "verdict py_low_with_work_cands @15:22:26 = lawful (snapshot caught "
    "finalize detach +33s pre-CPU-ramp + r369 serial queue waiting behind "
    "W3 finalize in-flight; local_batch_running=true); post_review 3437 "
    "rows 0 unresolved NO = zero P0; W3-JUDGE chain: burn done, finalize "
    "in-flight pid 28400"
)
h["round_no"] = 389
h["loop_round"] = 389
h["round"] = 389
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
    f"{now_iso} | round 389 bm-b | dept:工程/舰队 (W3 判决链收割窗·finalize 分离烧判) | "
    "WM-VERDICT: 绿-合法串行等待(probe 15:22:26 py_low_with_work_cands=快照踩在 "
    "finalize detach+33s CPU 未起坡+r369 串行队列在 W3 判决后合法等待,local_batch_"
    "running=true pid 28400 在飞;红牌 red=false) | "
    "did: (1) S0-1 bm-b 锚定+S0 pull--rebase 被轮首脏阻(脏面=autofill_state+"
    "W3 checkpoint 本机车道产物非他机会话,非阻塞如实披露); (2) S0.5 轮首扫 99/99 "
    "零未回执+decisions.md 三路径缺位=零行审核披露+票板 0 open; (3) S1 smoke "
    "25/25; (4) S3 主闭环: W3-JUDGE burn watch=checkpoint 513/513 全行齐"
    "(幸存者 513 对账零 missing,runner pid 4604 15:13:44 clean exit)→judge-"
    "finalize 首跑内联 15:15 被 5min 无输出墙自动杀(r386 坑律再犯实录:冷层指针"
    "未先行;零副作用实证=append_ledger 纯函数账本虚拟+w3_judge.json 未落=kill "
    "零盘污重跑安全)→r386 分离律正解落地:pid 28400 @15:21:53 后台烧判(logs/"
    "w3_judge_finalize_r389.log,cpu 154s+ 爬坡健康)+串行律验明(W2 落 r387/W1 落 "
    "r388/无他 finalize 活进程)→W3-JUDGE shard done-flip 双面同步(shared+lane,"
    "r387 五十五批律;burn 证据 513/513 断言后翻转;entry done-flip 延至 finalize "
    "回执=r386 W2 先例); (5) S6 33 腿全 rc=0 68s:audit CLEAN/采集器 pre-15:30 "
    "诚实 no-op(lhb 节流+车道守卫 bm-a/bm-c 面)/astock_daily+rev_osc 本机双车道 "
    "幂等 no-op/fundamental fresh skip/b_layer 全过/live_paper 锚定 OK(enforce→"
    "日期门 2026-10-01 shadow 降级诚实)+t35v 0924 PASS 零例+t24a 22/22 drift0+"
    "t24b 0/22 诚实/aggr+alloc+grid 幂等/daily_report REPORT-0928 faces4/token "
    "L2 0 today; (6) post_review 3437 行 15 NO 全员后续 YES 闭环=0 未解零 P0; "
    "(7) S7: schtasks 双查在位(Loop 正在运行 pin=2 next 15:32 ✓·Watchdog 重 "
    "registered first-fire 15:40)+claw OK+state 389+心跳 epoch int 自证 | "
    "verify: smoke 25/25+S6 逐腿 rc=0+W3 checkpoint 513 行计对账+池双面翻转 "
    "json 重载复证(entry ready/shard done×2 面)+finalize 分离进程 cpu 爬坡实证"
    "+post_review NO 闭环对账 | 下轮: (a) W3 finalize(pid 28400)落地→w3_judge."
    "json 验收(n_judged 513/E[FP]=25.65 预期/G2 eligible/family PBO/gate-face "
    "judgment)→entry done-flip 双面→产品 commit→W3 intake slice 建(prereg §6 "
    "镜像 W2 cmd_intake 面: D6 绑定门+STRATEGY_LIBRARY+TRIAL-* 纸盘)→intake "
    "live fire; (b) 15:30 新 bar 窗本机双车道 astock_daily/rev_osc 实弹+live."
    "paper/t35/t24 三件套随新 bar; (c) 串行队列 W3 finalize 落地后: MASS x4 "
    "burns→DC-V2→W4-JUDGE(一切 judge-finalize 一律分离后台 r386 律+同链串行 "
    "r387 律); (d) CEO 48h 报告窗 09-29 22:45(bmb); marks/账本/SEED 本轮全 +0"
    "(w3_judge.json 未落=判词面未产生,finalize 落地轮补)\n"
)
with open(r"logs\iteration-loop\round_reports.md", "a", encoding="utf-8", newline="\n") as f:
    f.write(line)
print("round report line appended")
