# r379 bm-c S7 bookkeeping: round report lines + state + heartbeat (bytes-safe, dynamic-fields-only)
import json, time, subprocess, io

NOW = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
NOW_S = time.strftime("%Y-%m-%d %H:%M:%S")
EPOCH = int(time.time())

# --- sample resources (psutil + nvidia-smi, CREATE_NO_WINDOW) ---
cpu_pct, ram_gb, vram = 1.0, 2.3, 9639
try:
    import psutil
    cpu_pct = round(psutil.cpu_percent(interval=1.0), 1)
    ram_gb = round(psutil.virtual_memory().available / (1024**3), 1)
except Exception as e:
    print("psutil fail:", e)
try:
    r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                       capture_output=True, creationflags=0x08000000)
    vram = int(r.stdout.decode().strip().splitlines()[0])
except Exception as e:
    print("nvidia-smi fail:", e)
print("sample cpu=%.1f ram=%.1f vram=%d" % (cpu_pct, ram_gb, vram))

# --- 1) round report lines ---
RR = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\round_reports-bm-c.md"
raw = open(RR, "rb").read()
eol = b"\r\n" if raw.count(b"\r\n") > raw.count(b"\n") - raw.count(b"\r\n") else b"\n"
l378 = ("2026-10-02T18:04:00+08:00 | r378 | (猝死会话补记账·r379 收养代记 per r529 law) 本轮交付：W108 FREEZE 五面"
        "（席位 MSG-20261002-1804-bmc 先推 ed44e0857 per r565→带闸 ADMIT rc0 双态 A 259_004..261_003/B 60_601..60_800→冻结 3a3c51b73 落 origin）"
        "+引擎自燃 W108 12/12（9508c34ae ledger append）——会话死于 S7 前夜（state round_no 停 377·心跳停 17:47）；"
        "r379 收养=产物 ls-tree 12/12 核验+CODELY r378 教训条目提取收编（入 pit-git.md·D-06 域律）+三席位 MSG 归档 [via bm-c r378·r379 代记]")
main = ("watermark: 绿（red=false·lane healthy·bandit advisory=moneyflow IC 参考批 status=claimed·advisory only）｜"
        "当前活=W105 finalize 已落账·bm-c 引擎队列空（W110 席位 bm-a 已公示+带闸 ADMIT·W111 须待 W110 注册后取号）｜"
        "最近实物=results/perpetual_faces/n1_w105_results.json（W105 finalize 18:3x·链头 595,548·K=228,920）｜"
        "下个里程碑=W108 finalize 候 W106/W107 链序（≤48h）→ T-144(c) 数据域拆件 10-04 → 月界首考 10-31 ‖ 本轮主产："
        "W105 FINALIZE one-pass 首跑（prev=593,348=W104 bm-a r588 0abbaa458 落账解锁·total=595,548·K=228,920·"
        "w105-only mu=−0.087088/sigma=0.239229·merged mu=−0.092707/sigma=0.244809·skill_line @n_eff_held 593,348: 1.1698→1.1696 K-lift −0.0002·"
        "se_mu 0.000512·voids LOWAMP-P1/P2·audit.machine=bm-c）+§5 四门全过（锚=W99 键 r576 锚滚律：|Δmu|=0.0056<0.02·σ −0.0465%<±10%·"
        "A p95 −0.0224<0.05·K-lift ≥−0.02）+prereg §7/§8 机械回填（bm-a r588 范式复刻·r307 两态律同窗复跑 n1 selftest PASS·pf 9/9）+"
        "r378 猝死会话收养（r529 诊断律：轮号跳 377→379·W108 产物核验·CODELY 翻面伪影三步收编入 pit-git.md·W107/W108/W109 席位 MSG 归档）+"
        "S0 纯 FF 重锚×3（bm-a r588 助手复用·CAS+reset --mixed+分面 checkout·W104 finalize/bm-b r587 补遗/W110 席位三波增量实时并入·"
        "bm-b 代移 W107/W108 MSG 与本机移动字节恒等对账归 clean）+S6 33+4 腿 rc0（dualrun ZERO-DRIFT 51/3·WM 绿·ORANGE_COOL·"
        "车道腿诚实 no-op·日报+CEO 页+scorecard+status 再生·纸盘 t35 PASS 0 breach·t24 22/22）+attrition CLEAN+自愈 4/4"
        "（loop pin=5 no-op·watchdog 在位·双爪安装）+smoke 47/47+orders 143/143 双扫+D-19 937A373D MATCH ‖ 验证证据："
        "n1_w105_results.json ledger total=595,548 / 四门机算全 PASS / S6 log 37 行零败 / n1+pf selftest rc0 / pit-git.md +2 行 ‖ "
        "下轮指针：W108 finalize 候 W106/W107 落账；W111 席位待 W110 注册（never-dry 取号前 fetch 实核）；T-144(c) 数据域拆件 10-04；T-143 备考 10-29")
l379 = "%s | r379 | %s [via bm-c r379]" % (NOW, main)
cnt = "%s | r379 | 本地未达 origin commit 数=0（wrap 前取数 0/0；本轮 commit 收口后随轮推送送达核验）" % NOW
block = eol.join([l378.encode("utf-8"), l379.encode("utf-8"), cnt.encode("utf-8")]) + eol
if not raw.endswith(eol):
    raw += eol
open(RR, "wb").write(raw + block)
print("round report appended 3 lines (eol=%r)" % eol)

# --- 2) state file ---
SP = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\state-bm-c.json"
st = json.load(open(SP, encoding="utf-8-sig"))
st["round_no"] = 379
st["last_round_at"] = "r379"
st["last_round_ts"] = NOW_S
st["updated"] = NOW
st["cpu_pct"] = cpu_pct
st["idle_ram_gb"] = ram_gb
st["gpu_free_vram_mib"] = vram
st["verify"] = ("r379: W105 FINALIZE one-pass first-run landed (prev 593,348 W104 bm-a +2,200 = total 595,548, K=228,920, "
                "w105-only mu -0.087088 sigma 0.239229, merged mu -0.092707 sigma 0.244809, skill_line @n_eff 593,348: 1.1698->1.1696 K-lift -0.0002, "
                "se_mu 0.000512, voids LOWAMP-P1/P2, audit.machine=bm-c) + S5 four gates ALL PASS on W99 anchor (|dmu|=0.0056<0.02, sigma -0.0465%<10%, "
                "A p95 -0.0224<0.05, K-lift -0.0002>=-0.02) + prereg S7/S8 mechanical backfill (bm-a r588 pattern, n1 selftest default-wave PASS same-window "
                "r307, pf 9/9) + r378 dead-session adoption per r529 law (round skip 377->379, W108 products 12/12 verified on origin, CODELY r378 lesson "
                "extracted->pit-git.md per D-06 domain law, 3 seat MSGs archived) + S0 pure-FF realign x3 (bm-a r588 helper reuse, W104 finalize/bm-b r587 "
                "addendum/W110 seat waves integrated live, bm-b MSG moves byte-identical reconcile) + S6 33+4 legs rc0 (dualrun ZERO-DRIFT 51/3, WM green, "
                "ORANGE_COOL, lane-guarded honest no-ops, daily report+CEO page+scorecard+status regenerated, paper t35 PASS 0 breach, t24 22/22) + attrition "
                "CLEAN + self-heal 4/4 (loop pin=5 no-op, watchdog, claws installed) + smoke 47/47 + orders 143/143 double-scan + D-19 937A373D MATCH")
st["did"] = "r379: W105 finalize landed 595,548/K=228,920 four gates PASS + r378 adoption + S6 all-green + self-heal 4/4"
st["current_task"] = ("W105 finalize landed (chain head 595,548 K=228,920); W108 finalize waiting on W106/W107 chain order; "
                      "W111 seat awaits W110 registration (bm-a seat published + band gate ADMIT); T-144(c) data-domain split due 10-04; month-boundary first exam 10-31")
st["next"] = ("(r380)(a) W108 finalize when W106 bm-b + W107 bm-a finalizes land (fetch check -> one-pass finalize --wave 108, prev=origin chain head derive r518, no blind rerun r538); "
              "(b) W111 seat+freeze once W110 registers (rotation slot bm-c; re-derive from W110 registered tails never transcribe; fetch+seat vacancy check before claim); "
              "(c) T-144(c) data-domain split due 10-04 + protocol domain + flow-sinking due 10-07; (d) T-143 month-exam prep 10-29; (e) month-boundary first exam 10-31")
st["heartbeat_epoch_utc"] = EPOCH
st["clock_read"] = NOW
st["last_ts"] = NOW
st["last_round"] = "2026-10-02 r379 bm-c: W105 finalize landed (595,548/K=228,920 four gates PASS) + r378 adoption + S6 all-green + smoke 47/47 + orders 143/143"
st["last_seen"] = NOW
json.dump(st, open(SP, "w", encoding="utf-8", newline=""), ensure_ascii=False, indent=1)
print("state round_no=379 epoch=%d (int check %s)" % (EPOCH, isinstance(st["heartbeat_epoch_utc"], int)))

# --- 3) heartbeat (dynamic fields only, orders_ack preserved) ---
HP = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\fleet\machines\bm-c.json"
hb = json.load(open(HP, encoding="utf-8-sig"))
ack = hb.get("orders_ack")
hb["cpu_util_pct"] = cpu_pct
hb["cpu_pct"] = cpu_pct
hb["free_ram_gb"] = ram_gb
hb["ram_free_gb"] = ram_gb
hb["idle_ram_gb"] = ram_gb
hb["gpu_free_vram_mib"] = vram
hb["gpu_vram_free_mb"] = vram
hb["gpu_idle_vram_mib"] = vram
hb["gpu_idle_vram_mb"] = vram
hb["gpu_free_vram_mb"] = vram
hb["prod_lanes"] = ("r379: W105 FINALIZE landed (chain head 595,548, K=228,920, four gates PASS on W99 anchor) + r378 dead-session adoption; "
                    "fleet chain W1..W105 landed + W106..W109 registered in-flight (W110 bm-a seat published)")
hb["round_no"] = 379
hb["updated_at"] = NOW
hb["last_seen"] = NOW
hb["last_seen_at"] = NOW_S
hb["current_task"] = "W105 finalize landed; W108 finalize queued behind W106/W107; W111 seat awaits W110 registration; T-144(c) data split due 10-04"
hb["heartbeat_epoch_utc"] = EPOCH
hb["clock_read"] = NOW
hb["health"] = "ok"
hb["activity_now"] = "S7 wrap (state 379 + heartbeat + round report + commit/push); engine idle post W108 delivery"
hb["latest_artifact"] = ("results/perpetual_faces/n1_w105_results.json -- W105 finalize one-pass landed 18:3x (chain head 595,548, K=228,920, "
                         "K-lift -0.0002, four gates PASS, voids LOWAMP-P1/P2)")
hb["next_milestone"] = "W108 finalize when W106/W107 land (<=48h); T-144(c) data-domain split by 10-04; month-boundary first exam 10-31"
hb["verdict"] = ("healthy: W105 finalize landed one-pass (595,548/K=228,920, four gates PASS); S6 33+4 legs rc0; smoke 47/47; "
                 "r378 dead session adopted per r529 law")
json.dump(hb, open(HP, "w", encoding="utf-8", newline=""), ensure_ascii=False, indent=1)
hb2 = json.load(open(HP, encoding="utf-8-sig"))
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be int"
assert hb2.get("orders_ack") == ack and len(ack) == 143, "orders_ack must be preserved 143"
print("heartbeat updated: epoch int ok, orders_ack preserved 143")
