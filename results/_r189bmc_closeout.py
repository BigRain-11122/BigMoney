"""r189 bm-c S7 closeout: inbox archive + state + heartbeat (json int epoch
discipline R170/R178/R262) + round report line."""
import io
import json
import os
import shutil
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())

# 1. inbox archive
msg = os.path.join(ROOT, "fleet", "inbox",
                   "MSG-20260929-0015-bm-a-ALL-W5-prereg-freeze.md")
proc_dir = os.path.join(ROOT, "fleet", "inbox", "processed")
if os.path.exists(msg):
    os.makedirs(proc_dir, exist_ok=True)
    shutil.move(msg, os.path.join(proc_dir, os.path.basename(msg)))
    print("inbox: MSG-20260929-0015 archived to processed/")

# quick machine readings (fail-soft)
cpu_pct, idle_ram = 0.0, 0.0
try:
    import psutil
    cpu_pct = round(psutil.cpu_percent(interval=1.0), 1)
    idle_ram = round(psutil.virtual_memory().available / (1024 ** 3), 1)
except Exception:
    pass
gpu_free = 10355
try:
    r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                         "--format=csv,noheader,nounits"],
                        capture_output=True, text=True, timeout=15)
    gpu_free = int(r.stdout.strip().splitlines()[0])
except Exception:
    pass

# 2. state file
sp = os.path.join(ROOT, "state-bm-c.json")
state = json.load(io.open(sp, encoding="utf-8"))
state.update({
    "round_no": 189,
    "updated": NOW,
    "last_round_ts": NOW,
    "last_round_at": "r189",
    "updated_at": NOW,
    "note": ("r189: dead-window r188 salvage (pool_worker mid-git-op guard "
             "D-02 + register pin-17 infinite-loop bugfix, selftest 17/17->"
             "union with bm-a r404-cont origin-blob fix 19/19, rebase "
             "conflict resolved as union, pushed bdf6af30) + fill_ladder "
             "prereg_frozen gate status-line authority fix (W5 FROZEN "
             "false-refused on narrative draft-era word, a73d7a9b; supply "
             "auto-arms when bm-a T-114 runner lands) + O-2210 worker-end "
             "receipt (Bigmoney-PoolWorker registered+Ready on bm-c)"),
    "did": ("S0-1 anchor bm-c -> S0 salvage-commit r188 legacy + pull --rebase "
            "(1 UU pool_worker.py -> union: origin S14/S15 + r188 legs "
            "renumbered S16-S19 -> selftest 19/19 -> push bdf6af30) -> S0.5 "
            "orders 122 real (README.md glob artifact excluded): unacked "
            "O-2026-09-28-2210-bm-a processed + acked (worker-end installed "
            "this window); decisions tail unchanged (D-06 last, reviewed "
            "r183/r184, zero new obligation) -> S1 smoke 26/26 -> S2 boards "
            "empty (job_list 0 + fleet zero open; T-114 W5 wave claimed by "
            "bm-a, not touched) -> S3 T-107 slice: fill_ladder gate "
            "false-negative fixed a73d7a9b (status-line authority) + live "
            "fire gate-reason progression prereg-draft->runner-not-built "
            "-> S4 pitlaw batch 70 (CODELY 9,523B<=10,240B) -> S6 36 legs "
            "nonzero=0 (_r189bmc_s6_chain.json; new-bar=False honest skip "
            "of bar-pending legs; all lane guards honest no-op; "
            "fund_premium pre-15:30 no-op; clock ORANGE_COOL sleeves=4 "
            "regen) -> S7 loop pin=5 no-op + claw IN_PLACE_MATCH + inbox "
            "MSG-0015 (bm-a W5 freeze decl) archived + state 189 + "
            "heartbeat"),
    "verify": ("pool_worker selftest 19/19 (union face) + fill_ladder "
               "selftest all-PASS (fixtures a/b/c) + live-fire W5 gate "
               "reason=runner-not-built (progression proof) + smoke 26/26 "
               "+ S6 chain 36 legs nonzero=0 + CODELY 9,523B + epoch int "
               "self-check below"),
    "next": ("r190 = watch bm-a T-114 W5 runner landing -> ladder auto-arms "
             "TRIAL-LABOR-W5-GENERATE (verify floor refill + first burn) + "
             "T-106 s3 event ledger / s4 chain integration slices + "
             "V3-TOURNAMENT waiting-face watch (RAM gate) + W5-JUDGE "
             "sequencing behind V3/GRID per r354 law"),
    "current_task": ("r189 closed: r188 salvage + gate fix landed; next = "
                     "W5 auto-arm watch + T-106 s3/s4"),
    "cpu_pct": cpu_pct, "idle_ram_gb": idle_ram,
    "gpu_free_vram_mib": gpu_free,
})
io.open(sp, "w", encoding="utf-8", newline="\n").write(
    json.dumps(state, ensure_ascii=False, indent=1))
print("state: round_no=189 written")

# 3. heartbeat
hp = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
hb = json.load(io.open(hp, encoding="utf-8"))
if "O-2026-09-28-2210-bm-a.md" not in hb.get("orders_ack", []):
    hb["orders_ack"].append("O-2026-09-28-2210-bm-a.md")
hb.update({
    "last_seen": NOW,
    "heartbeat_epoch_utc": EPOCH,
    "clock_read": NOW,
    "current_task": ("r189 closed: dead-window r188 salvage pushed "
                     "(pool_worker guard + pin bugfix, union 19/19) + "
                     "fill_ladder W5 gate false-negative fixed (supply "
                     "auto-arms on runner); W5 wave owned by bm-a T-114"),
    "cpu_util_pct": cpu_pct, "free_ram_gb": idle_ram,
    "gpu_free_vram_mb": gpu_free, "verdict": "healthy",
    "round_no": 189, "updated_at": NOW,
    "prod_lanes": ("BigMoney-compute-node: T-106 national-team s3/s4 next "
                   "slices | supply ladder: W5-GENERATE gate unblocked "
                   "(prereg FROZEN recognized r189, auto-arms on bm-a "
                   "runner; catalog 5 entries, 4 burned/closed) | judge "
                   "family: INNOVATION-QUOTA-W2 G1 FAIL closed r187, W5 "
                   "next wave bm-a-owned | O-2210 worker-end: "
                   "Bigmoney-PoolWorker registered+Ready (15min :02 sweeps, "
                   "mid-git-op guard live) | C-family single-writer faces: "
                   "bm-a alive again (r404/405), takeover window closed | "
                   "MiniGame image main line in-service (ComfyUI RTX3070 "
                   "16GB) | cloud antenna U218 (TJGenerators, bm-c only)"),
})
io.open(hp, "w", encoding="utf-8", newline="\n").write(
    json.dumps(hb, ensure_ascii=False, indent=1))
chk = json.load(io.open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch not int"
assert "T" in chk["clock_read"] and "+" in chk["clock_read"], "clock format"
print("heartbeat: written, epoch int verified =",
      chk["heartbeat_epoch_utc"])

# 4. round report line
rp = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
line = (
    f"\n{NOW} | round 189 bm-c (r188 死窗抢救轮) | dept:工程/舰队 joint (T-107 "
    "supply-mechanism slice) | WM-VERDICT: 绿 (00:29 probe red=false lane "
    "healthy; next_pick=claimed moneyflow IC 面板 parked 自愈中; 池 0 ready+2 "
    "gated-waiting=供给地板 0<3 饿死面本轮回执如下) | did: (1) S0-1 锚定 "
    "bm-c→探测 r188 死窗遗产（Tools 双修复 2-6min 新鲜度+零存活迭代进程=死窗 "
    "非并发会话）→selftest 17/17 先行→salvage commit→pull --rebase 撞 1 UU "
    "（bm-a r404-cont 同文件 origin-blob 读面修复）→union 并集解（origin "
    "S14/S15 保位+抢救腿 S14-S17→S16-S19 重编号）→pool_worker selftest "
    "19/19→push bdf6af30；r188 双修复=pool_worker mid-git-op 守卫"
    "（D-20260928-02·rebase/merge/index.lock 让路）+register pin-17 无限循环"
    "值域修复（Minute%15 域 0..14·17→2 相位余数·Bigmoney-PoolWorker 已注册"
    "Ready 00:32 sweeps）；(2) S0.5 orders 差集 122 实（README.md=glob 伪 "
    "order 排除）：O-2026-09-28-2210 未回执→本窗处理+回执=工人端已装（本 "
    "salvage 即 bm-c 工人端落地·三律全合规）→orders_ack +1；decisions 尾零新行"
    "（D-06 last·r183/184 已审·零义务）；(3) S1 smoke 26/26；(4) S2 双板清"
    "（job_list 0+fleet 零 open·T-114 W5 波 bm-a 认领未碰）；(5) S3 主交付"
    "=T-107 fill_ladder prereg_frozen 门状态行权威修复 a73d7a9b——live-fire "
    "假阴实证：W5 prereg 被 bm-a r405 冻结（状态域 FROZEN）但 r162 血统叙述"
    "段历史词「冻结挂起」被朴素子串扫描误拒→供给地板 0<3 饿死（CEO 三令饱和"
    "失败模式）；修复=显式【状态：…】域权威（FROZEN 即过）+无状态域回退 r176 "
    "marker 扫描+hermetic fixture a/b/c；live fire 门理由推进 "
    "prereg-draft→runner-not-built（bm-a T-114 下轮建 runner 即自动入池=机"
    "制闭环实证）；(6) S4 坑律七十批入册（CODELY 9,523B≤10,240B 硬线过）；"
    "(7) S6 36 腿 nonzero=0（results/_r189bmc_s6_chain.json：new-bar=False "
    "诚实跳过 bar-pending 三腿·15 车道守卫腿诚实 no-op·fund_premium "
    "pre-15:30 no-op·clock ORANGE_COOL sleeves=4 同日幂等再生·daily_report "
    "REPORT-202609-29 落盘·token delta=0）；(8) S7 loop pin=5 no-op+claw "
    "IN_PLACE_MATCH+inbox MSG-20260929-0015（bm-a W5 冻结声明·与树实证一致"
    "：prereg FROZEN+SEED 三键+T-114 认领+runner 未建）归档 processed+"
    "state 189+心跳 epoch int 自证 | backfill: r185-188 轮账缺行补记——"
    "r185/r186 死窗（r186 池半翻转 22:58+第 6 崩 23:10·由 r187 抢救定谳："
    "INNOVATION-QUOTA-W2 双格 G1 FAIL 判负关单+T-106 s2 PDF 持有人腿完成"
    "39/39）；r187 抢救轮（commits 733ca59b/159620bc·心跳 23:37 写·state 未"
    "及写=本轮补 189）；r188 死窗（register pin-17 挂死疑因·遗产双修复由本"
    "轮抢救上链） | verify: pool_worker 19/19+fill_ladder fixtures all-PASS"
    "+smoke 26/26+S6 36 腿 nonzero=0+salvage push bdf6af30+gate 修复 push "
    "a73d7a9b+orders 差集清零+epoch isinstance(int) | next: r190 = bm-a "
    "T-114 W5 runner 落地 watch（ladder 自动入池+首烧验证）+T-106 s3 事件账"
    "本/s4 链接线切片+V3-TOURNAMENT waiting 面 watch（RAM 门）+W5-JUDGE 序"
    "门（r354·排 V3/GRID 后） [via bm-c]\n")
with io.open(rp, "a", encoding="utf-8", newline="\n") as fh:
    fh.write(line)
print("round report: r189 line appended")
