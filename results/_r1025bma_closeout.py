# r1025 bm-a closeout: W255 MSG archive + d19 advance + state/heartbeat rewrite (gpu key convergence per O-20261017-0100 sec.2.2) + round report line
import subprocess, json, os, sys, shutil, datetime, time

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
CNW = 0x08000000
STATE = os.path.join(ROOT, "state-bm-a.json")
HB = os.path.join(ROOT, "fleet", "machines", "bm-a.json")
RR = os.path.join(ROOT, "round_reports-bm-a.md")
CHLOG = os.path.join(ROOT, "results", "_r1025bma_s6chain_rc.log")
TS = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())

def sh(args, cwd=ROOT):
    return subprocess.run(args, cwd=cwd, capture_output=True, creationflags=CNW)

def jload(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)

def jdump(obj, p):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)

# 0) wait for chain completion (max 240s)
log = ""
for _ in range(24):
    try:
        with open(CHLOG, encoding="utf-8", errors="replace") as f:
            log = f.read()
        if "chain done" in log:
            break
    except Exception:
        pass
    time.sleep(10)
chain_done_line = ""
bad = "?"
for ln in log.splitlines():
    if ln.startswith("=== chain done"):
        chain_done_line = ln
        bad = ln.split("bad_rc=")[1].split(" ")[0] if "bad_rc=" in ln else "?"
print("CHAIN_WAIT done_line=%r bad=%s" % (chain_done_line[:60], bad))

# 1) fresh reads
gpu_free = gpu_total = None
r = sh(["nvidia-smi", "--query-gpu=memory.free,memory.total", "--format=csv,noheader,nounits"])
if r.returncode == 0:
    parts = r.stdout.decode().strip().split(",")
    if len(parts) == 2:
        gpu_free, gpu_total = int(parts[0]), int(parts[1])
cpu = ram_free_gb = ram_free_pct = None
try:
    import psutil
    cpu = round(psutil.cpu_percent(interval=2), 1)
    vm = psutil.virtual_memory()
    ram_free_gb = round(vm.available / 2**30, 1)
    ram_free_pct = round(vm.available * 100.0 / vm.total, 1)
except Exception as e:
    print("psutil unavailable: %r" % e)
r = sh(["powershell", "-NoProfile", "-Command",
        "(Get-CimInstance Win32_Process -Filter \"Name='codely.exe'\").Count"])
codely_n = r.stdout.decode().strip()
print("FRESH gpu_free=%s gpu_total=%s cpu=%s ram=%s codely=%s" % (gpu_free, gpu_total, cpu, ram_free_gb, codely_n))

# 2) archive W255 seat MSG (ALL-broadcast consumed by bm-a: recorded, W256 derive waits W255 chain)
src = os.path.join(ROOT, "fleet", "inbox", "MSG-20261016-22xx-bmc-w255-seat.md")
dst = os.path.join(ROOT, "fleet", "inbox", "processed", "MSG-20261016-22xx-bmc-w255-seat.md")
os.makedirs(os.path.dirname(dst), exist_ok=True)
if os.path.exists(src):
    shutil.move(src, dst)
    print("W255_MSG archived")

# 3) d19 dual watermark advance (delta consumed this round: receipts + report line land same round)
r = subprocess.run([sys.executable, os.path.join("scripts", "d19_watermark.py"), "update", "--advance"],
                  cwd=ROOT, capture_output=True, creationflags=CNW)
print("D19 rc=%d out=%s" % (r.returncode, r.stdout.decode("utf-8", "replace").strip()[:200]))
if r.returncode != 0:
    print("D19 advance FAILED -- honest abort before state write")
    sys.exit(2)

# 4) state rewrite (fresh load AFTER d19 so its writes are preserved)
st = jload(STATE)
summary = (u"r1025 closed: CEO 三维分配执法轮 (O-20261017-0100/O-20261016-2347 双令 ack 执行) -- "
           u"(1) S0 stash3-ff-pop 拉 4 新 commit (闸修复 63943e50b 入树生效, census 验证 headless=3/interactive=0); "
           u"(2) POOL-0003 whisper 词锚复核回执已交 (card-lint 9/9; 19 锚件 reviewed: 10 词级 PASS + 9 行级旗标候 bm-b POOL-0018 + 0 fail = PASS_WITH_PENDING; 覆盖 16/41, 28 缺曲候 POOL-0018 滚动产出; 证据 results/_r1024bma_pool0003_anchor_review.json 随批上链; 死线 10-17 24:00 前达成); "
           u"(3) POOL-0013 软著A机14款收编上链 done (46 件=报审台账+第1-5批 → group origin f3bad1cd 首推即中, origin ancestry 验证过, 零删除 D-02 爪面安全; staged M 107 面确证已由 bc34c07 先行落链; 本地 46 副本字节恒等后隔离 .codely-cli/tmp/pool0013-quarantine-20261017T010849/manifest.json, treasure_guard prescan rc0; docs/orders.md 回执行同批落地); "
           u"(4) 心跳 gpu_* 15 互斥键收敛 (gpu_free_vram_mb 单键为准 + gpu_mode=llm 补键); "
           u"(5) 35B:8090 health=200 常设健康 (周六无让路面); "
           u"(6) O-20261016-2148 ack (候 join-report 零动作面) + O-20261016-2347 resume MSG 回执 (fleet/inbox/MSG-20261017-0128-bm-a-resume.md) + W255 席 MSG 记收归档 (bm-a W256 类派生候 W255 链落点火); "
           u"(7) D-19 双 delta 消费 (DEC d9940c44→881b6dcb: D-20261017-01 委员会修法包 v2 集团面零本司派工 + D-20261017-02 三维案=本班执行面; ORD 819dc928→e8e6ab1e: 三新令行 O-2148/O-2347/O-0100); "
           u"(8) S6 43 腿链 bad_rc=%s (周六无新 bar 面·papers 幂等 no-op)" % bad)
artifact = (u"results/_r1025bma_pool0013_receipt.json (46 件收编+quarantine manifest) + results/_r1024bma_pool0003_anchor_review.json (19 件复核回执) + group origin f3bad1cd (软著 46 件+orders 回执行) + results/_r1025bma_s6chain_rc.log (43 腿) + fleet/orders/O-20261017-0100-bm-c.md 回执节")
verdict = (u"green-full-work (watermark=绿 insufficient_history 观察窗 red=false; smoke 49/49; satengine ALIVE rc0 队列 0 候链; 三维令全件执行: POOL-0003 回执+POOL-0013 done+gpu 键收敛+35B=200; 孤儿面=1 mcp-bridge read-only; 周六夜窗满载合法)")
verify = (u"smoke 49/49 + orphan 1/11 read-only 零杀 + satengine status rc0 + S6 43 腿 bad=%s (log) + POOL-0003 card-lint 9/9 + POOL-0013 origin_verified=true (f3bad1cd) + treasure_guard prescan rc0 登记簿零命中 + d19 update --advance 双水位 + 心跳 epoch int 回读" % bad)
nxt = (u"r1026+: (a) W255 链落 (bm-c finalize 后) → bm-a W256 类 own-wave 派生首动作 (probe live re-derive; W255 B 带 578_301..578_500 将拒 naive W256 A 起点, 席位 MSG 下一位 freezer 义务已记); (b) POOL-0018 bm-b 词级滚动产出到 → POOL-0003 复审窗 + 28 缺曲覆盖补齐; (c) moneyflow 面板自愈观察 → IC reference 批点火候; (d) bm-d join-report 落地即接线 (O-2148 §三); (e) push readback commit2 落地后 sync/push_verified 块回读")

st.update({
    "round_no": 1025, "round": 1025, "loop_round": 1025,
    "last_round": 1025, "last_round_at": TS, "last_round_closed": TS, "last_round_ts": TS,
    "last_run": TS, "last_seen": TS, "ts": TS, "updated": TS, "updated_at": TS,
    "clock_read": TS, "last_action_at": TS,
    "current": summary, "did": summary, "task": u"O-20261017-0100 三维分配执法轮 (双令 ack + POOL-0003 回执 + POOL-0013 收编 + gpu 键收敛 + S6)",
    "current_task": st["task"],
    "last_action": u"r1025: 三维令执行 (POOL-0003 回执 + POOL-0013 收编 group f3bad1cd + gpu 键收敛) + S6 43 腿 + D-19 双消费 + 三令 ack",
    "last_artifact": artifact, "latest_artifact": artifact, "recent_artifact": artifact,
    "next": nxt, "now_active": u"bm-a full-work (CEO O-20261016-1950 + O-20261017-0100 三维分配执法毕); engine-lane = sequence-wait bm-c W255 chain (bm-a W256 类派生候链落点火); 35B:8090 常设 health 200; 夜窗满载合法",
    "verdict": verdict, "verify": verify,
    "idle_rounds": 0, "orphan_face": 1, "orphan_faces": 1, "orphan_killed": 0,
    "heartbeat_epoch_utc": EPOCH, "last_heartbeat_epoch_utc": EPOCH,
    "push_verified": {"ts": TS, "origin_tip": "pending", "note": "r1025: commit1+push then readback commit2 (same-round verification)"},
    "sync": {"ts": TS, "origin_tip": "pending", "ahead_behind": "pending", "note": "r1025: readback commit2 follows"},
    "last_orders_seen": u"r1025: ORD 819dc928→e8e6ab1e consumed (三新令行: O-20261016-2148 bm-d 准备令 / O-20261016-2347 resume 广播 / O-20261017-0100 三维分配令; 全部 ack+执行)",
    "last_decisions_seen": u"r1025: DEC d9940c44→881b6dcb consumed (D-20261017-01 委员会修法包 v2 集团面零本司派工; D-20261017-02 三维资源案=本班 O-0100 执行面)",
    "last_orders_at": TS, "last_decisions_at": TS,
})
st["next_milestone"] = u"POOL-0018 词级滚动到货 → POOL-0003 复审+28 缺曲覆盖; W255 链落 → bm-a W256 派生点火 (窗 ≤2026-10-18)"
jdump(st, STATE)
print("STATE written round_no=1025")

# 5) heartbeat rewrite with gpu key convergence
hb = jload(HB)
LEGACY_GPU = ["free_vram_gb", "gpu0_free_vram_gb", "gpu_free_vram", "gpu_free_vram_gb",
              "gpu_free_vram_mib", "gpu_idle_vram", "gpu_idle_vram_gb", "gpu_idle_vram_mb",
              "gpu_idle_vram_mib", "gpu_vram_free_gb", "idle_gpu_vram_gb", "idle_vram_gb",
              "vram_free_gb", "vram_free_mb"]
removed = [k for k in LEGACY_GPU if k in hb]
for k in removed:
    del hb[k]
if gpu_free is not None:
    hb["gpu_free_vram_mb"] = gpu_free
    hb["gpu_total_vram_mb"] = gpu_total
hb["gpu_mode"] = "llm"
hb["gpu_mode_note"] = u"诚实注记: bm-a 无双模烧制车道; gpu_mode=llm 表 35B:8090 常驻 GPU-offload (~3G) + CEO 桌面应用共存, 无 gen 烧批在飞 (satengine 队列 0); O-20261017-0100 §2.2 维度清单 v1 收敛"
hb["gpu_source_note"] = u"nvidia-smi live read %s (CEO working machine, honest %s MiB free)" % (TS, gpu_free)
if cpu is not None:
    hb["cpu_pct"] = cpu
    hb["cpu_total_pct"] = cpu
    hb["cpu_util_pct"] = cpu
    hb["cpu_load_pct"] = cpu
if ram_free_gb is not None:
    hb["free_ram_gb"] = ram_free_gb
    hb["ram_free_gb"] = ram_free_gb
    hb["free_ram_pct"] = ram_free_pct
    hb["ram_free_pct"] = ram_free_pct
    hb["idle_ram_gb"] = ram_free_gb
acks = hb.get("orders_ack", [])
for f in ["O-20261016-2148-bm-a.md", "O-20261016-2347-bm-c.md", "O-20261017-0100-bm-c.md"]:
    if f not in acks:
        acks.append(f)
hb["orders_ack"] = acks
hb["orders_ack_note"] = u"r1025: +3 acks (O-20261016-2148 bm-d 准备令 ack 候 join-report 零动作面 / O-20261016-2347 resume 广播=MSG-20261017-0128-bm-a-resume.md 回执 / O-20261017-0100 三维分配令=回执节落地+全件执行: 闸修复拉入+POOL-0003 回执+POOL-0013 done+gpu 键收敛+35B=200)"
hb["current"] = summary
hb["did"] = summary
hb["task"] = st["task"]
hb["current_task"] = st["task"]
hb["last_action"] = st["last_action"]
hb["last_artifact"] = artifact
hb["latest_artifact"] = artifact
hb["recent_artifact"] = artifact
hb["next"] = nxt
hb["now_active"] = st["now_active"]
hb["verdict"] = verdict
hb["next_milestone"] = st["next_milestone"]
hb["round_no"] = 1025
hb["round"] = 1025
hb["loop_round"] = 1025
hb["last_round"] = "r1025"
hb["last_round_at"] = TS
hb["last_seen"] = TS
hb["ts"] = TS
hb["updated"] = TS
hb["updated_at"] = TS
hb["clock_read"] = TS
hb["heartbeat_epoch_utc"] = EPOCH
hb["last_heartbeat_epoch_utc"] = EPOCH
hb["heartbeat_epoch_utc_type_int"] = isinstance(hb["heartbeat_epoch_utc"], int)
hb["health"] = "green"
hb["active"] = True
hb["now_active"] = st["now_active"]
hb["codely_live_count"] = int(codely_n) if codely_n.isdigit() else hb.get("codely_live_count", 0)
hb["codely_live_count_note"] = u"r1025 %s census: post-gate-fix headless-only count=%s (interactive windows=0, 豁免面生效)" % (TS[:16], hb["codely_live_count"])
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
jdump(hb, HB)
# self-check
hb2 = jload(HB)
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be int (smoke F7)"
assert "T" in hb2["clock_read"], "clock_read must be ISO T-separated (smoke F7)"
print("HB written: gpu keys removed=%s gpu_free_vram_mb=%s gpu_mode=%s acks=%d epoch_int=%s" % (
    len(removed), hb2.get("gpu_free_vram_mb"), hb2.get("gpu_mode"), len(hb2["orders_ack"]),
    isinstance(hb2["heartbeat_epoch_utc"], int)))

# 6) round report line
line = (u"%s | r1025 bm-a (dept:舰队-CEO三维分配执法轮+数据-S6维护) | WM-VERDICT: 绿 (red=false; insufficient_history 观察窗) | "
        u"当前活: %s | "
        u"最近实物: %s | "
        u"下个里程碑: %s | "
        u"验证: %s | "
        u"本地未达 origin commit 数: commit1 push 后 readback=commit2 同窗落值 | "
        u"下轮指针: %s") % (TS, summary[:1200], artifact, st["next_milestone"], verify, nxt)
with open(RR, "a", encoding="utf-8") as f:
    f.write(line + "\n")
print("ROUND_REPORT appended")
print("CLOSEOUT_DONE")
