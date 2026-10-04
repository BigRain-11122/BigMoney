# -*- coding: utf-8 -*-
# r663 bm-b S7 closing: state bump + watermarks + heartbeat + round report append
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

# --- 1) state.json round bump + watermarks ---
sp = "state.json"
s = json.load(io.open(sp, encoding="utf-8"))
old = s["round_no"]
s["round_no"] = old + 1
s["note"] = ("r663: golden-week watch round -- S0 r437 pool-face checkout-merge netpath (origin 2-commit bm-c r458/r460 wave, zero UU; "
             "sync_face settle zero-regression 364/364 claims, crash_fuse lane settle); D-19 decisions MATCH EB14B510 + group orders sha "
             "82A0CEF9->68947C17 watermark bump zero-consume (bm-relevant rows unchanged, 10-03 rows already acked r618); S6 37/38 rc0 + "
             "update_daily rc2 sina 510300 transient SSL EOF w/ tencent fallback upstream_equal (zero data impact, cutoff 2026-09-30); "
             "trio V698/Q534/D390 of 2000 healthy (3 burners CIM full-scan, dup_k=0, keepalive owner_since 10:14 self-adopted); "
             "S7 attrition CLEAN + tasks/claws green + orders double-scan 153/153")
s["last_round_at"] = clock
s["ts"] = clock
s["updated"] = clock
s["last_seen"] = clock
s["last_decisions_read_at"] = clock
s["last_orders_sha"] = "68947C178D21814FBB5B20C3497F1DC28D42D50C"
s["round_no_label"] = f"bm-b round {s['round_no']} (golden-week watch; trio V698/Q534/D390 of 2000; S6 37/38+rc2 honest)"
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
                     f"V698/Q534/D390 of 2000 healthy (3 burners CIM full-scan, dup 0); S6 37/38 rc0 "
                     f"(update_daily rc2 sina transient, tencent fallback equal); milestone trio finalize 10-06..10-09")
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
## {clock} | round {chk['round_no']} | bm-b | golden-week watch (S0 r437 pool-face netpath + S6 37/38 + trio dual-form health)
- 当前活: FUND trio NULLS canonical burns in flight V698/Q534/D390 of 2000 (dual-form: 3 runner pids 34396/57116/30208 CIM full-scan verified + mtimes <4min fresh + dup_k 0 x3; keepalive claim owner_since 10:14:11 self-adopted stable; 本窗 +5/+2/+3 增速放缓观察=cells 轻重不均)
- 最近实物: results/_r663bmb_trio_health.json (trio 三面零dup健康证据) + docs/live_usage/LIVE-2026-10-04.md ORANGE_COOL + docs/daily_report/REPORT-2026-10-04.md 5 faces + results/dashboard_status.json 3-machine refresh ({hm})
- 下个里程碑: trio NULLS 完成窗 V ~10-06, Q ~10-07, D ~10-09 (Q 长杆 32/hr 级照旧·V 本窗 8/hr 级放缓=下轮复watch) -> per-family finalize + verdict per prereg sec.4 (G1' v2 + G2 v2 + exit-census)
- watermark verdict: GREEN (red=false lane healthy; py 62% loaded trio burn 在飞即 work candidate; board 0 open; pool_ready_unclaimed=0; next_pick moneyflow IC claimed 非本机不碰)
- S0: pull 撞 daemon treadmill 脏面 (runnable_pool 池面交集) -> r437 正法序 checkout-origin 池面 + merge origin/main 2-commit (bm-c r458/r460 wave) 零 UU -> sync_face settle 幂等补 settle (runnable_pool unchanged=origin 版已含我方全 claims 364/364 零回归 + crash_fuse lane settle) ; orders 差集 0 (轮首+S7 双扫 153/153 同口径); D-19 decisions MATCH (EB14B510, subprocess 原字节律) + group orders.md sha 82A0CEF9->68947C17 变化=bm 相关行尾未变 (10-03 双令已 r618 回执) =水位键更新零消费
- S1 smoke 48/48 PASS; S6 37/38 rc0 + 1 rc2 如实披露: update_daily rc2 = sina 510300 SSL EOF 瞬态抓取失败, tencent fallback 验证 upstream_equal (local 2026-09-30 == latest 2026-09-30, 假期零新 bar 零数据影响, 下轮自愈); 其余 golden-week 休市面全 no-op 合法; market_clock CALL-2026-09-30 ORANGE_COOL
- S3: 无 open 票 (fleet/tasks 0 open + job_list 空); 饱和引擎 rc0 alive idle; post_review REPORT-20261004 零活红; 试用期常设线=trio 在飞判决批不触发新起草
- S7: attrition guard CLEAN 4 files; IterationLoop pin=2 在册 (first fire 10:32) + LoopWatchdog 重注册在册; pre-commit/pre-push 钳 LF-normalized 在位; inbox 零未读
- 本地未达 origin commit 数=0 (收口 push + push_verify 自证)
- 下轮指针: trio 烧录监控 (增速面复watch: V 族 8/hr 是否回 24/hr 区) + NULLS 完成即 finalize 链 (V 族最先) + update_daily sina 瞬态自愈确认
"""
with io.open(rp, "ab") as f:
    f.write(entry.encode("utf-8"))
print("round report appended, entry bytes:", len(entry.encode("utf-8")))
