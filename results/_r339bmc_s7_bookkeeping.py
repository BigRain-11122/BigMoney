"""r339 bm-c S7 bookkeeping: state + heartbeat + round report + CODELY pit entry.

Format law (r289/r500): detect EOL + indent of existing JSON files and
mirror them on rewrite; git diff --stat surgical assertion after.
"""
import json, os, subprocess, time, datetime
import psutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW_EPOCH = int(time.time())
CLOCK = datetime.datetime.now().astimezone().isoformat(timespec="seconds")

# --- fresh system stats (r319 law: prime psutil before sampling) -----------
_ = psutil.cpu_percent(interval=None)
time.sleep(1.2)
CPU_PCT = round(psutil.cpu_percent(interval=None), 1)
RAM_FREE = round(psutil.virtual_memory().available / (1024 ** 3), 1)
GPU_FREE = None
try:
    out = subprocess.check_output(
        ["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
        creationflags=subprocess.CREATE_NO_WINDOW, timeout=20)
    GPU_FREE = int(float(out.decode().strip().splitlines()[0]))
except Exception as e:
    print("GPU read fail (honest):", e)

print(f"STATS cpu={CPU_PCT}% ram_free={RAM_FREE}GB gpu_free={GPU_FREE}MiB "
      f"epoch={NOW_EPOCH} clock={CLOCK}")

def detect_eol(path):
    raw = open(path, "rb").read()
    return "\r\n" if b"\r\n" in raw[:4000] else "\n"

def detect_indent(path):
    for line in open(path, "rb").read().decode("utf-8", errors="replace").split("\n"):
        s = line.strip()
        if s.startswith('"'):
            return len(line) - len(line.lstrip(" "))
    return 1

def rewrite_json(path, obj):
    eol = detect_eol(path)
    ind = detect_indent(path)
    s = json.dumps(obj, ensure_ascii=False, indent=ind)
    if eol == "\r\n":
        s = s.replace("\n", "\r\n")
    with open(path, "wb") as f:
        f.write(s.encode("utf-8"))
    print(f"REWRITTEN {path} (indent={ind}, eol={'CRLF' if eol == chr(13) + chr(10) else 'LF'})")

# --- 1. state-bm-c.json -----------------------------------------------------
sp = os.path.join(ROOT, "state-bm-c.json")
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = 339
st["last_round_at"] = "r339"
st["last_round_ts"] = CLOCK
st["updated"] = CLOCK
st["cpu_pct"] = CPU_PCT
st["idle_ram_gb"] = RAM_FREE
st["gpu_free_vram_mib"] = GPU_FREE
st["verify"] = ("r339: W32 frozen+burned 12/12 same round (21st engine wave, bm-c 7th "
                "owned; A 107_004..109_003 + B 41_401..41_600 both-tails arithmetic "
                "no-skip; banned-gate ADMIT + band-gate ADMIT 29-row scan + n1 "
                "selftest W32 face + engine selftest 36/36; freeze commit 29e3a7e5b "
                "on origin dfad4758c, delivery ls-tree verified; r330 kill-restart "
                "cycle: old frozen-view pid 17472 killed, rescan zero, new instance "
                "pid 34328 ignited, 12/12 shards 23:19; engine appender pushed 6 "
                "(beb943c68), append_pending=3) + T-131 monitoring healthy "
                "(452/5229, pid 33316, ~17h ETA, quarantine 0) + S6 37 legs rc0 "
                "(dualrun streak 25/3, audit CLEAN, smoke 47/47) + D-19 MATCH "
                "(753f99e8)")
st["did"] = ("r339 W32 freeze (never-dry standing step, rotation slot W29+3=bm-c, "
             "r511 origin table-tail lock verified) + W32 12/12 engine burn same "
             "window + S6 chain + bookkeeping")
st["current_task"] = ("W32 finalize pending (12/12 burned on disk, engine appender "
                      "batching remaining 3 shards; finalize next round with r310 "
                      "origin-completeness gate, prev=432,748 live-head derive); "
                      "T-131 backfill in flight (452/5229 at 23:08, ~17h ETA); "
                      "T-134 s2 pick9 evidence-order rescan pending; W33=bm-a slot "
                      "observation")
st["next"] = ("(r340)(a) W32 finalize (ls-tree 12/12 on origin + K=68,320 expected "
              "+ prev derive 432,748 + S5 4/4 + §7/§8 backfill one-pass, r538 "
              "no-blind-rerun law); (b) T-131 backfill monitoring (three-face + "
              "quarantine); (c) T-134 s2 ninth-item evidence-order rescan (r304 "
              "law, remaining 30 single_core); (d) W33=bm-a slot observation (W33+ "
              "projection A 109_004..111_003 / B 41_601..41_800 both CLEAN per "
              "r339 gate receipt); (e) month-boundary first exam 10-31")
st["heartbeat_epoch_utc"] = NOW_EPOCH
st["clock_read"] = CLOCK
st["note"] = ("r339: W32 freeze->burn same-round closed loop (freeze 23:1x, 12/12 "
              "burned 23:19, ~4min wall). Engine restart executed per r330 "
              "three-action law (kill old frozen-view instance 17472 -> rescan "
              "zero -> schtasks fire new instance 34328 at 23:18:01). Engine "
              "appender live: 6 W32 shards pushed (beb943c68), 3 pending next "
              "batch window. W32 finalize = next round (needs 12/12 on origin). "
              "T-131 healthy (resurrected r338, now 452/5229). One transient "
              "git-batch anomaly this round: 4-command wrapper batch returned "
              "empty rc1 (suspected engine-appender index.lock contention "
              "window); stepwise retry clean, git log verified zero half-state "
              "before replay.")
st["last_ts"] = CLOCK
st["last_decisions_read_at"] = CLOCK
st["last_round"] = "2026-10-01 r339 bm-c: W32 freeze + 12/12 engine burn same round + S6 chain"
st["last_seen"] = CLOCK
rewrite_json(sp, st)

# --- 2. heartbeat fleet/machines/bm-c.json ----------------------------------
hp = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
hb = json.load(open(hp, encoding="utf-8"))
hb["cpu_util_pct"] = CPU_PCT
hb["free_ram_gb"] = RAM_FREE
hb["gpu_free_vram_mb"] = GPU_FREE
hb["gpu_free_vram_mib"] = GPU_FREE
hb["gpu_vram_free_mb"] = GPU_FREE
hb["gpu_idle_vram_mb"] = GPU_FREE
hb["gpu_idle_vram_mib"] = GPU_FREE
hb["idle_ram_gb"] = RAM_FREE
hb["ram_free_gb"] = RAM_FREE
hb["round_no"] = 339
hb["updated_at"] = CLOCK
hb["last_seen"] = CLOCK
hb["last_seen_at"] = CLOCK
hb["current_task"] = ("W32 burned 12/12 (finalize next round); T-131 fund_history "
                      "backfill in flight (452/5229, ~17h ETA); T-134 s2 pick9 "
                      "pending")
hb["verdict"] = ("loaded_ok (T-131 backfill + W32 engine burn in flight; W32 12/12 "
                 "burned same-round, appender batching; board: zero unclaimed "
                 "tickets; W33=bm-a rotation slot not freezable by bm-c)")
hb["prod_lanes"] = ("r339: W32 frozen+burned 12/12 same round (21st engine wave, "
                    "A 107_004..109_003 + B 41_401..41_600, ADMIT receipt "
                    "_r339bmc_w32_band_gate.py; 6 shards pushed beb943c68, 3 "
                    "pending appender batch) + W26/W29 bm-c finalizes landed "
                    "(K=55,120/61,720; ledger chain 432,748 at W31)")
hb["activity_now"] = ("W32 freeze + 12/12 engine burn (23:11-23:19, one-pass "
                      "closed loop per r330 kill-restart law); T-131 backfill "
                      "resumed r338 continues (452/5229)")
hb["latest_artifact"] = ("results/p2cal_ext/n1_w32/shard-0..11-of-12.json 12/12 "
                        "burned (23:19:37) + research/PERPETUAL_N1_W32_PREREG.md "
                        "frozen + results/_r339bmc_w32_band_gate.py ADMIT "
                        "(2026-10-01T23:1x)")
hb["next_milestone"] = ("W32 finalize (K=68,320 expected, prev 432,748 derive, "
                        "next round <=1h); T-131 backfill complete (~17h, "
                        "10-02 afternoon); month-boundary first exam 10-31")
hb["heartbeat_epoch_utc"] = NOW_EPOCH
hb["clock_read"] = CLOCK
hb["health"] = "ok"
hb["cpu_pct"] = CPU_PCT
hb["cpu_idle_pct"] = round(100 - CPU_PCT, 1)
hb["cpu_cores"] = 32
rewrite_json(hp, hb)

# --- 3. round report append --------------------------------------------------
rr = os.path.join(ROOT, "round_reports-bm-c.md")
line = (
    "2026-10-01T23:4x+08:00｜r339｜dept:研究（W32 冻结+同窗烧录）+dept:工程（S6 链+簿记）｜"
    "watermark verdict=loaded_ok→绿（py 85.5%·T-131 回填+W32 引擎烧录双在飞）｜"
    "主产出=**W32 引擎波冻结+12/12 同窗烧毕**（第 21 枚引擎波·bm-c 第 7 枚自有波·轮值律 W29+3=32·"
    "表尾锁 fetch 实核 origin 无 W32 行〔r511〕·A=107_004..109_003/B=41_401..41_600 双尾算术零跳位"
    "〔==W31 行 W32+ 警示投影逐位吻合·机闸 derive r535 律〕·banned-gate ADMIT rc0·band-gate ADMIT rc0"
    "〔29 行全扫描+探针簇 95_000..95_003 r335 腿+N3-R1 70_000..70_005 腿+W33+ 投影双净空〕·"
    "prereg §0-§6 冻结〔§5 锚=W31 实测 mu −0.09153/sigma 0.24447/A p95 0.3074/K-lift −0.0012〕·"
    "selftest 三面绿〔n1 runner PASS 含新增 W32 face 腿·engine 36/36〕·commit 29e3a7e5b 推 origin "
    "dfad4758c·送达核验 ls-tree 三件 ✓）+r330 三动作律执行（杀旧冻结视图实例 pid 17472→重扫零→"
    "schtasks fire 新实例 pid 34308→点火验证=产物增长面 12/12 shards 23:19:37 同窗烧毕·"
    "engine appender 已推 6 件〔beb943c68 push_rc=0〕append_pending=3）｜"
    "T-131 监控三面健康（452/5229 symbols·+63 vs r338·pid 33316 alive·12.9s/sym·ETA≈17h·quarantine 0）｜"
    "S6 37 腿 rc0（dualrun ZERO-DRIFT streak 25/3·compute_audit CLEAN burning-healthy〔py 86.7%〕·"
    "wm probe loaded_ok·车道守卫 bm-a/bm-b 17 腿诚实 no-op·host 守卫件 bm-a 心跳新鲜放行跳过·"
    "REPORT/LIVE-2026-10-01 再生〔ORANGE/50% cap/COOL〕·b_layer mask 4 gates PASS·attrition CLEAN〔2 处 healed 注记〕·"
    "token 0 today）｜S0.5 令差集 EMPTY（143 全 ack）·D-19 决策水位 753f99e8 MATCH-unchanged（raw-blob python 法）｜"
    "S1 smoke 47/47｜工程观察=多命令 wrapper 批一次整批零输出 rc1（疑引擎 appender index.lock 竞态窗）·"
    "git log 核实零半落后分步重跑全绿（CODELY 坑律已录）｜实况三行（CEO 过程可见面）："
    "当前活=W32 finalize 待办（12/12 烧毕·appender 批推余 3 件）+T-131 基本面回填续拉（452→5229）｜"
    "最近实物=results/p2cal_ext/n1_w32/shard-0..11 12/12（23:19）+research/PERPETUAL_N1_W32_PREREG.md｜"
    "下个里程碑=W32 finalize（K=68,320 预期·下轮窗≤1h）+T-131 回填完成（≈17h）+10-31 月界首考｜"
    "产品分=2（冻结+烧录+ADMIT 回执=能跑能看实物）｜本地未达 origin commit 数=收尾 push 后 fetch 自证"
)
with open(rr, "ab") as f:
    raw = open(rr, "rb").read()
    eol = b"\r\n" if b"\r\n" in raw[-200:] else b"\n"
    if not raw.endswith(b"\n"):
        f.write(eol)
    f.write(line.encode("utf-8") + eol)
print("ROUND_REPORT appended (r339)")

# --- 4. CODELY.md pit entry --------------------------------------------------
cm = os.path.join(ROOT, "CODELY.md")
pit = (
    "- [2026-10-01 23:4x r339 bm-c] silent-git 包装器多命令 PS 批调用整批零输出 rc1 坑"
    "（W32 冻结推送窗实弹·同窗同命令分步重跑全绿=瞬态面）：`& $g add..; & $g commit..; "
    "& $g pull..; & $g push` 四连发一次整批零回显 rc1（无 git 报错文本无 PS 报错）——"
    "疑因=本机常驻引擎 appender 同窗 git add/commit 持 index.lock 竞态（与 r320 CRT 引号坑不同族："
    "该坑有报错文本，本坑零输出；与 r523 活烧窗车道件脏树律同族=引擎并发 git 面）。"
    "处置=先 git log/status 核实零半落零吞件，再分步重跑即收敛（本例 ride commit/pull/push 分步全过）。"
    "How to apply：引擎在役期一切多命令 wrapper 批遇整批空输出 rc1，勿诊断螺旋勿重发明——"
    "git log 三面核实后分步重放；根治面（appender 与轮会话 git 串行化）留 HQ-FEEDBACK 候选。\n"
)
with open(cm, "ab") as f:
    raw = open(cm, "rb").read()
    eol = b"\r\n" if b"\r\n" in raw[-200:] else b"\n"
    if not raw.endswith(b"\n"):
        f.write(eol)
    f.write(pit.encode("utf-8") + eol)
print("CODELY pit entry appended")
print("BOOKKEEPING DONE")
