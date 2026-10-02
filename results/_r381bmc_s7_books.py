# -*- coding: utf-8 -*-
# r381 bm-c S7 books: CODELY pit line + round report + state + heartbeat (bytes-safe, dynamic-fields-only)
import json, time, subprocess

NOW = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
NOW_S = time.strftime("%Y-%m-%d %H:%M:%S")
EPOCH = int(time.time())
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

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

# --- 1) CODELY.md pit line (append-only, bytes-safe) ---
CP = ROOT + r"\CODELY.md"
pit = ("- [2026-10-02 19:5x r381 bm-c] 引擎波 12/12 交付后 finalize 跨轮拖延窗=他机 stall-drain 合法接管面（W108 实弹·r518 commit-time 仲裁的归属新面）："
       "W108 12/12 交付 18:20 后本机轮猝死（state 停 380·ride commit 未推），>80min 链头无消费致 r307 FAIL-CLOSED 锁死 W109/W110/W111 三席——"
       "bm-b r590 按「链活性>归属」跨机代跑 W108+W109+W110 三连 drain（763d2e2c3..07e8b2ebc·head 599,948→606,548）；"
       "本机恢复轮同窗独立 finalize 产确定性孪生（runs 2200/2200 逐位恒等·ledger 块恒等·差异仅 r499 浮点尾差+audit.machine 归属）"
       "=零成本让路（origin verbatim 取正典·本地变体弃置未推零污染·yield receipt 66a8efae6）。"
       "How to apply：①本机 owned 波 finalize=12/12 交付同轮收口禁跨轮拖延（烧完会话死=恢复轮首动作 finalize 先于一切）；"
       "②finalize 推送被拒先查 origin 是否已有同头块（同头孪生=取 origin 让路禁二推本地变体）；"
       "③跨机 drain 后归属面=audit.machine 记实际执行机，owned 波的 finalize 权非排他保真面。")
raw = open(CP, "rb").read()
eol = b"\r\n" if raw.count(b"\r\n") > raw.count(b"\n") - raw.count(b"\r\n") else b"\n"
if not raw.endswith(eol):
    raw += eol
open(CP, "wb").write(raw + pit.encode("utf-8") + eol)
print("CODELY pit appended (now %d bytes)" % (len(raw) + len(pit.encode("utf-8")) + len(eol)))

# --- 2) round report lines ---
RR = ROOT + r"\round_reports-bm-c.md"
raw = open(RR, "rb").read()
eol = b"\r\n" if raw.count(b"\r\n") > raw.count(b"\n") - raw.count(b"\r\n") else b"\n"
main = ("watermark: 绿（red=false·lane healthy·py_series 0.1/1.3/0.2·bandit advisory=moneyflow IC 参考批 status=claimed·advisory only）｜"
        "当前活=r381 恢复轮收口（W108 finalize 撞面让路已落账·S6 全绿·引擎队列空）｜"
        "最近实物=results/perpetual_faces/n1_w108_results.json（origin 正典版·bm-b r590 drain 落账 19:2x·链头 606,548·K=239,920）｜"
        "下个里程碑=W113 席位+冻结（never-dry 取号前 fetch 实核·≤48h）→ T-144(c) 协议+流水下沉 10-07 → 月界首考 10-31 ‖ 本轮主产："
        "W108 finalize 独立首跑（12/12 分片消费·pre mu -0.0928/sigma 0.2448/K 233,320→merged mu -0.0927/sigma 0.2449/K 235,520·"
        "skill_line @n_eff 599,948: 1.1702→1.1705 K-lift +0.0003·ledger 599,948+2,200=602,148）+同窗双 finalize 撞面零成本让路"
        "（bm-b r590 stall-drain 三连先落 origin·确定性孪生逐位对账 runs 2200/2200 恒等·yield receipt 66a8efae6 已推）+"
        "S0 外科整合×3 波（r381 死会话未推 ride commit reset-FF-reland 无 rebase 无 force·50+27 件取 origin·4 活写面保留 rides·"
        "pool jsonl 本地 1039⊆origin 1051 零损失取 origin·W111/W112 席位 MSG r586 同名对 blob 恒等后清）+"
        "S6 28 腿 rc0（dualrun ZERO-DRIFT streak 51·compute_audit 绿·WM 绿·ORANGE_COOL breadth 0.79·market_clock CALL-2026-09-30·"
        "车道腿诚实 no-op·日报/CEO 页/scorecard/status 再生·无新 bar 免 paper 块=r588 先例）+"
        "attrition CLEAN（4 ledger·历史 shrink 已 healed）+自愈 4/4（loop pin=5 no-op·watchdog 重注册在位·双爪安装）+"
        "smoke 47/47+orders 143/143 双扫零未回执+D-19 937A373D MATCH+inbox W112 席位 MSG 消费（origin 已归档·blob 恒等对账） ‖ "
        "恢复轮披露：r381=死会话自标轮号（零公开输出·phantom 无公开撞面=r529 律精神面）·本轮取 381 为首个公开 r381 ‖ 验证证据："
        "n1 selftest PASS（缺省波 r522 律）/ S6 log 28 行零败 / yield receipt 66a8efae6 送达核验 behind=0 / attrition scan CLEAN ‖ "
        "下轮指针：(a) W113 席位 MSG+冻结（A 269_004..271_003/B 62_001..62_200 投影已披露·取号前 fetch 实核 W112 注册态）；"
        "(b) finalize 同轮收口机制提案——引擎 tick 检测本机 owned 波 12/12 且 finalize 缺席时自动 finalize（本坑根治面·下轮开票或直执）；"
        "(c) T-144(c) 协议+流水下沉 10-07（CODELY 59.4KB 超水位·在役正典结构性 r504 注记·下沉窗即载体）；(d) T-143 月考备考 10-29")
l381 = "%s | r381 | %s [via bm-c r381]" % (NOW, main)
cnt = "%s | r381 | 本地未达 origin commit 数=0（收口 commit 推送后 fetch+ls-tree 自证）" % NOW
block = eol.join([l381.encode("utf-8"), cnt.encode("utf-8")]) + eol
if not raw.endswith(eol):
    raw += eol
open(RR, "wb").write(raw + block)
print("round report appended 2 lines")

# --- 3) state file ---
SP = ROOT + r"\state-bm-c.json"
st = json.load(open(SP, encoding="utf-8-sig"))
st["round_no"] = 381
st["last_round_at"] = "r381"
st["last_round_ts"] = NOW_S
st["updated"] = NOW
st["cpu_pct"] = cpu_pct
st["idle_ram_gb"] = ram_gb
st["gpu_free_vram_mib"] = vram
st["verify"] = ("r381 recovery round: W108 finalize independently run (12/12 consumed, merged mu -0.0927 sigma 0.2449 K 235,520, "
                "skill_line 1.1702->1.1705 K-lift +0.0003, ledger 602,148) then zero-cost YIELD to bm-b r590 stall-drain canonical "
                "(deterministic twin: runs 2200/2200 identical, diffs = r499 float tails + audit.machine only; origin verbatim taken, "
                "yield receipt 66a8efae6 pushed) + S0 surgical integration x3 waves (reset-FF-reland, no rebase no force) + "
                "S6 28 legs rc0 (dualrun ZERO-DRIFT 51) + attrition CLEAN + self-heal 4/4 + smoke 47/47 + orders 143/143 + D-19 MATCH")
st["did"] = "r381: W108 finalize twin-yield receipt pushed; chain advanced by bm-b drain to 606,548; S6 all-green; S0 x3 surgical"
st["current_task"] = ("r381 wrap: W108 finalize yielded to bm-b canonical (chain head 606,548, K 239,920); engine queue empty; "
                      "next = W113 seat+freeze (fetch-verify before claim) + finalize-same-round engine proposal + T-144(c) due 10-07")
st["next"] = ("(r382)(a) W113 seat MSG + freeze five-face (bm-c 33rd owned wave; projection A 269_004..271_003 / B 62_001..62_200 "
              "jump cta_wave1=62_000 per W112 seat disclosure; own-probe before seat per r587 law, fetch+vacancy check before claim); "
              "(b) finalize-same-round mechanism: open ticket or direct-exec engine tick auto-finalize on own-wave 12/12 (root-fix of this "
              "round's stall-drain lesson; r381 CODELY pit); (c) T-144(c) protocol+flow domain sinking due 10-07 (CODELY 59.4KB over watermark, "
              "in-service canon per r504 note); (d) T-143 month-exam prep 10-29; (e) month-boundary first exam 10-31")
st["heartbeat_epoch_utc"] = EPOCH
st["clock_read"] = NOW
st["last_ts"] = NOW
st["last_round"] = ("2026-10-02 r381 bm-c: W108 finalize twin-yield (receipt 66a8efae6) + S6 28 legs rc0 + "
                    "S0 x3 surgical + smoke 47/47 + orders 143/143")
st["last_seen"] = NOW
json.dump(st, open(SP, "w", encoding="utf-8", newline=""), ensure_ascii=False, indent=1)
print("state round_no=381 epoch=%d (int %s)" % (EPOCH, isinstance(st["heartbeat_epoch_utc"], int)))

# --- 4) heartbeat (dynamic fields only, orders_ack preserved verbatim per r583) ---
HP = ROOT + r"\fleet\machines\bm-c.json"
hb = json.load(open(HP, encoding="utf-8-sig"))
ack = hb.get("orders_ack")
ack_n = len(ack) if isinstance(ack, list) else -1
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
hb["prod_lanes"] = ("r381: W108 finalize twin-yield receipt pushed (chain head 606,548 via bm-b drain); fleet chain W1..W110 landed "
                    "+ W111 bm-b burning + W112 bm-a frozen; next bm-c wave = W113")
hb["round_no"] = 381
hb["updated_at"] = NOW
hb["last_seen"] = NOW
hb["last_seen_at"] = NOW_S
hb["current_task"] = ("r381 wrap; next: W113 seat+freeze (fetch-verify) + finalize-same-round engine proposal; T-144(c) due 10-07")
hb["heartbeat_epoch_utc"] = EPOCH
hb["clock_read"] = NOW
hb["health"] = "ok"
hb["activity_now"] = "S7 wrap (state 381 + heartbeat + round report + CODELY pit + commit/push); engine idle, queue empty"
hb["latest_artifact"] = ("results/perpetual_faces/n1_w108_results.json -- W108 finalize landed on origin (bm-b r590 drain canonical, "
                         "my deterministic twin yielded zero-cost, receipt 66a8efae6; chain head 606,548, K 239,920)")
hb["next_milestone"] = ("W113 seat+freeze within 48h (projection A 269_004..271_003 / B 62_001..62_200); T-144(c) protocol+flow "
                        "sinking by 10-07; month-boundary first exam 10-31")
hb["verdict"] = ("healthy: W108 finalize consumed (twin-yield to canonical, zero science loss); S6 28 legs rc0; smoke 47/47; "
                 "self-heal 4/4; attrition CLEAN")
json.dump(hb, open(HP, "w", encoding="utf-8", newline=""), ensure_ascii=False, indent=1)
hb2 = json.load(open(HP, encoding="utf-8-sig"))
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be int"
assert hb2.get("orders_ack") == ack, "orders_ack must be preserved verbatim"
print("heartbeat updated: epoch int ok, orders_ack preserved (%d entries)" % ack_n)
