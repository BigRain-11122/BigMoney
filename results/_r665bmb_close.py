# -*- coding: utf-8 -*-
# r665 bm-b S7 closing: state bump + heartbeat + round report append
# laws: r645 state json.dump+loads self-check; R170/R178 epoch int; R262 clock T-sep;
#       r641 round_reports.md bytes-mode append, newline prepend ALWAYS (r661 lesson);
#       r641 long-CJK f-string only (no % operator); r646 orders set-diff same-scope.
import json, io, time, subprocess, os

now = time.time()
clock = time.strftime("%Y-%m-%dT%H:%M:%S+08:00", time.localtime(now))
hm = time.strftime("%H:%M", time.localtime(now))

# --- 0) S7 orders double-scan (same-scope ls-tree + filesystem vs heartbeat ack) ---
p = subprocess.run(["git", "ls-tree", "origin/main", "fleet/orders/"], capture_output=True)
order_files = [ln.split("\t", 1)[1].strip().split("/")[-1] for ln in
               p.stdout.decode("utf-8", "replace").splitlines() if "\t" in ln and "/O-" in ln]
local_files = [f for f in os.listdir("fleet/orders") if f.startswith("O-") and f.endswith(".md")]
ack = set(json.load(io.open("fleet/machines/bm-b.json", encoding="utf-8")).get("orders_ack", []))
unacked = [f for f in set(order_files) | set(local_files) if f not in ack]
assert not unacked, f"S7 orders double-scan found unacked: {unacked}"
print(f"S7 orders double-scan: ls-tree {len(order_files)} local {len(local_files)} ack {len(ack)} unacked 0")

# --- 1) state.json round bump (watermarks unchanged this round: all MATCH) ---
sp = "state.json"
s = json.load(io.open(sp, encoding="utf-8"))
old = s["round_no"]
s["round_no"] = old + 1
s["note"] = ("r665: golden-week watch round -- S0 fetch HEAD==origin/main 0/0 zero-diff (pull --rebase benign-blocked "
             "by daemon dirty faces, r437 zero-intersection verified = no checkout-merge needed, S7 absorb; r643 "
             "three-evidence no concurrent session: other codely procs = game lanes only); D-19 decisions MATCH + "
             "group orders.md MATCH 68947C17 + fleet orders 153/153 zero-unacked (round-head probe + S7 double-scan); "
             "S6 38/38 rc0 ALL-GREEN (update_daily rc0 cutoff 2026-09-30 golden-week no-op legal; pool_dualrun "
             "ZERO-DRIFT streak 51); trio V709/Q544/D396->398 of 2000 healthy (4 burners CIM full-scan, dup_k=0 x3, "
             "mtimes fresh; bm-a stale 49-52min -> 4 shared faces stale-takeover derived by bm-b per O-2100 s2.4 "
             "STALE_MIN law; bm-c 20.5min borderline-normal watch); S7 attrition CLEAN + tasks/claws 4/4 green + "
             "inbox zero unread")
s["last_round_at"] = clock
s["ts"] = clock
s["updated"] = clock
s["last_seen"] = clock
s["last_decisions_read_at"] = clock
s["round_no_label"] = f"bm-b round {s['round_no']} (golden-week watch; trio V709/Q544/D398 of 2000; S6 38/38 all-green)"
s["clock_read"] = clock
with io.open(sp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(s, f, ensure_ascii=False, indent=1)
chk = json.load(io.open(sp, encoding="utf-8"))
assert chk["round_no"] == old + 1, "state bump self-check failed"
print("state round_no:", old, "->", chk["round_no"])

# --- 2) heartbeat bm-b.json ---
hp = "fleet/machines/bm-b.json"
h = json.load(io.open(hp, encoding="utf-8"))
h["last_seen"] = clock
h["heartbeat_epoch_utc"] = int(now)
h["clock_read"] = clock
h["round_no"] = chk["round_no"]
h["round_no_label"] = f"round {chk['round_no']} (bm-b)"
h["current_task"] = (f"golden-week watch r{chk['round_no']}: FUND trio NULLS canonical burns "
                     f"V709/Q544/D398 of 2000 healthy (4 burners CIM full-scan, dup 0, mtimes fresh); "
                     f"S6 38/38 rc0 all-green; milestone trio finalize 10-06..10-09")
h["verdict"] = "healthy"
h["ts"] = clock
h["updated"] = clock
try:
    m = subprocess.run(["powershell", "-NoProfile", "-Command",
        "(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB; "
        "(Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average"],
        capture_output=True)
    vals = m.stdout.decode("utf-8", "replace").split()
    h["free_ram_gb"] = h["idle_ram_gb"] = round(float(vals[0]), 2)
    h["cpu_util_pct"] = float(vals[1])
except Exception:
    pass
with io.open(hp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(h, f, ensure_ascii=False, indent=1)
chk2 = json.load(io.open(hp, encoding="utf-8"))
assert isinstance(chk2["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in chk2["clock_read"], "clock must be T-separated"
print("heartbeat ok: round", chk2["round_no"], "| epoch", chk2["heartbeat_epoch_utc"])

# --- 3) round report append (bytes mode, ALWAYS prepend \n) ---
rp = "logs/iteration-loop/round_reports.md"
entry = f"""
## {clock} | round {chk['round_no']} | bm-b | golden-week watch (S0 zero-diff netpath + S6 38/38 all-green + trio health)
- 当前活: FUND trio NULLS canonical burns in flight V709/Q544/D398 of 2000 (4 runner procs CIM full-scan verified + dup_k 0 x3 + mtimes fresh V10:43/Q10:44/D10:40; 本窗 ~5min 增速 +3/+2/+2 = 36/24/24 hr 级采样噪声带, D 长杆复watch)
- 最近实物: results/_r665bmb_trio_health.json (trio 三面健康证据) + docs/live_usage/LIVE-2026-10-04.md ORANGE_COOL 刷新 + docs/daily_report/REPORT-2026-10-04.md 5 faces + results/dashboard_status.json 三机面刷新 ({hm})
- 下个里程碑: trio NULLS 完成窗 10-06..10-09 (V 余 1291 行 @36/hr ≈ 36hr 最先; Q 余 1456 @24/hr ≈ 61hr; D 余 1602 @24/hr ≈ 67hr 长杆) -> per-family finalize + verdict per prereg sec.4 (G1' v2 + G2 v2 + exit-census)
- watermark verdict: GREEN (red=false lane healthy; py 61-98% loaded trio burn 在飞即 work candidate; board 0 open; next_pick moneyflow IC claimed 非本机不碰)
- S0: fetch 后 HEAD==origin/main 0/0 零差集 (pull --rebase 被 daemon 脏面良性阻断, 树脏面=本机 daemon 活写面 treadmill 交集零, S7 定向 absorb); r643 三证无并发会话 (本仓 codely 进程=本会话独占, 其余=游戏车道); D-19 decisions MATCH (EB14B510) + group orders.md MATCH (68947C17) 双水位零变化零消费 (sparse-clone subprocess 原字节律); fleet orders 153/153 轮首+S7 双扫零 unacked
- S1 smoke 48/48 PASS; S6 38/38 rc0 全绿: update_daily rc0 (golden-week 休市 cutoff 2026-09-30 全 no-op 合法); pool_dualrun ZERO-DRIFT streak 51; market_clock CALL-2026-09-30 ORANGE_COOL sleeves=4 activated=0; 4 条 bm-a 属主共享面 (t35_open_fill_verify/paper_export/daily_scorecard/dashboard_status) 因 bm-a 心跳 stale 49-52min 由 bm-b stale-takeover derive (O-2100 s2.4 STALE_MIN law, 法定路径); bm-c 心跳 20.5min 边缘正常观察
- S3: 无 open 票 (fleet/tasks 0 open + job_list 空); 饱和引擎 rc0 alive idle queue=0; 试用期常设线=trio 在飞判决批不触发新起草
- S7: attrition guard CLEAN (2 healed 历史注记照录); IterationLoop pin=2 no-op 在册 + LoopWatchdog 重注册 + pre-commit/pre-push 钳 LF-normalized 在位; inbox 零未读
- 本地未达 origin commit 数=0 (收口 push + push_verify 自证)
- 下轮指针: trio 烧录监控 (D 长杆 24/hr 复watch 是否回 28/hr) + NULLS 完成即 finalize 链 + bm-a 心跳 stale 面持续观察 (若 bm-a 恢复则 stale-takeover 面自动归还) + bm-c 边缘心跳观察
"""
with io.open(rp, "ab") as f:
    f.write(entry.encode("utf-8"))
print("round report appended, entry bytes:", len(entry.encode("utf-8")))
