import json
import os
import subprocess
import time
from datetime import datetime, timezone, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
now = datetime.now(timezone(timedelta(hours=8)))
ts = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())

cpu_pct, free_ram, gpu_free = 0.0, 0.0, 0.0
try:
    import psutil
    cpu_pct = round(psutil.cpu_percent(interval=1.0), 1)
    free_ram = round(psutil.virtual_memory().available / (1024 ** 3), 1)
except Exception:
    pass
try:
    out = subprocess.check_output(
        ["nvidia-smi", "--query-gpu=memory.free",
         "--format=csv,noheader,nounits"], stderr=subprocess.DEVNULL)
    gpu_free = round(float(out.decode().splitlines()[0].strip()) / 1024, 1)
except Exception:
    pass

# --- T-141 slice claim (CEO immediate law: claim same round) ---
tp = os.path.join(ROOT, "fleet", "tasks", "T-2026-10-01-141-P1.json")
t = json.load(open(tp, encoding="utf-8"))
t["progress"] = (
    "s1(bm-b engine-core instance)+s3(bm-b CEO-face/round-zero instance) "
    "claimed by bm-b r507 @ " + ts + " (law v1.0 read receipt: sec.1 local "
    "perpetual queue N1-N4 frozen-prereg-authorized generators, sec.3 "
    "PreIgnitionChecks r316-hardened, sec.4 round-zero watchdog, sec.5 "
    "bm-b full-core profile); build starts r508 first action (engine "
    "skeleton + N1 generator port reusing perpetual_faces machinery); "
    "s2 ledger-conversion open first-claim (lane-free).")
with open(tp, "w", encoding="utf-8") as f:
    json.dump(t, f, ensure_ascii=False, indent=1)
print("T-141 slice claim landed")

# --- heartbeat: orders_ack +2 + refresh ---
hp = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
hb = json.load(open(hp, encoding="utf-8"))
hb["last_seen"] = ts
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = ts
hb["current_task"] = (
    "r507 close: N1-W9 SHARD-0 burning (daemon pid 55796, 12-shard queue "
    "auto-fill); O-1410+O-1420 acked same-round; T-141 s1+s3 (bm-b engine "
    "instances) claimed, build starts r508")
hb["free_ram_gb"] = free_ram
hb["gpu_free_vram_gb"] = gpu_free
hb["cpu_util_pct"] = cpu_pct
hb["round_no"] = 507
hb["verdict"] = (
    "r507: (1) N1-W9 wave IGNITED AND BURNING (supply fired on settled "
    "pool, 12 shards materialized, daemon claim+launch 14:24:28 "
    "pid=55796 target_met=True -- O-1332 sec.1.2 chain closed); (2) pool "
    "shared-face settled via S6 compute_audit sync_face: LOWAMP-P2-NULLS "
    "ghost-ready healed 18/18 done -> bm-a finalize gate unblocked; (3) "
    "O-1410 saturation-engine order acked + T-141 s1/s3 claimed (bm-b "
    "instances), O-1420 acked (sec.3.3: bm-b no action required); (4) "
    "16-UU peak-window cherry-pick batch canon-resolved zero-loss "
    "(docs/live snapshots take-new, lane-backed faces + pool via "
    "sync_face merged-view, crash_fuse take origin clear side); S6 34 "
    "legs rc0, smoke 47/47, attrition CLEAN")
for o in ["O-20261001-1410-bm-c.md", "O-20261001-1420-bm-c.md"]:
    if o not in hb.get("orders_ack", []):
        hb["orders_ack"].append(o)
with open(hp, "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int)
print("heartbeat ok, orders_ack n =", len(chk["orders_ack"]))

# --- state.json note refresh ---
sp = os.path.join(ROOT, "state.json")
st = json.load(open(sp, encoding="utf-8"))
st["note"] = (
    "r507: pool settle heals NULLS ghost (18/18) + N1-W9 supply FIRED and "
    "daemon burning SHARD-0 (pid 55796, 12-shard queue) + O-1410/O-1420 "
    "acked + T-141 s1+s3 claimed (bm-b engine build starts r508) + 16-UU "
    "peak-window conflict batch canon-resolved zero-loss + S6 34 rc0 + "
    "smoke 47/47")
st["last_round_at"] = ts
st["ts"] = ts
st["updated"] = ts
st["updated_at"] = ts
with open(sp, "w", encoding="utf-8") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
print("state ok")

# --- round report line ---
rp = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
line = (
    "2026-10-01T14:31:00+08:00 | r507 bm-b | dept:研究/工程 | "
    "[watermark verdict: 14:14 probe insufficient_history n=1（机面 py "
    "0.4%·板全闭环+W14 治理停车=合法闲）·audit 14:13 FLAG:supply_floor"
    "（ready 0<3·本轮窗内供给点火治愈）] | 本轮主产出（实物）: (1) "
    "N1-W9 波点火在烧：S6 compute_audit sync_face settle 愈合 "
    "LOWAMP-P2-NULLS 幽灵 ready（共享面 18/18 done·finalize 门解锁 "
    "bm-a 道）→ perpetual_faces supply live==0 触发→12 分片物化→daemon "
    "14:24:28 claim n1w9-0of12 owner=bm-b+C8 LAUNCH pid=55796（latency "
    "9.9min target_met=True·O-1332 §1.2 链闭环）(2) 双新令 S0.5/S7 双扫"
    "收讫：O-1410 算力根治令 ack+T-141 建造票 bm-b 切片同轮认领（s1+s3 "
    "本机实例·律 v1.0 读毕回执·r508 开工）；O-1420 §3.3 明文 bm-b 无需"
    "动作=纯 ack（两令入 orders_ack）(3) 16-UU 峰窗 cherry-pick 撞车批"
    "正典解（origin 双跳：bm-c rev-p2-nulls 认领+bm-a r519 REV-P2 产"
    "品）：分类器 7 classified+9 UNKNOWN 手工定性=docs/LIVE×6+attrition"
    "/b_layer 取新（:3 14:16>origin 14:02）·6 lane 孪生面+池=写回可解"
    "析态+sync_face 合并律重derive（REFINE-BENCH-REV-P2-NULLS bm-c 认领"
    "/W14 park/LOWAMP-P2 18/18/W9 12 全零丢失断言过）·crash_fuse 取 "
    ":2（bm-c code_changed 自动清律 14:02:41>本机 refusal 面 14:02:06）"
    "·r501/r507 净路族全谱系复用（commit -C/rebase --quit/cherry-pick/"
    "update-ref/checkout） | 验证: S1 47/47·S6 34 腿 rc0（reconcile "
    "DRIFT 先录 streak 重置→settle 后愈·clock ORANGE_COOL cap50·REPORT/"
    "LIVE 2026-10-01 再生·token delta=0）·attrition CLEAN（healed 照录）"
    "·schtasks pin=2 no-op 14:18/watchdog S4U 14:19/claw MATCH·D-19 "
    "753F99E8 MATCH-unchanged（python raw-bytes·temp partial clone）·"
    "post_review ✗=0·本地未达 origin commit 数=0（45617b850 fetch 自证）"
    " | 坑律: 供给写入面×池冲突基底选错坑（supply 实写共享面 lane 零承"
    "载·:2 基底丢 W9 断言当场抓回·:3 基底+lane union 正解）已入 CODELY "
    "| inbox: MSG-1331（LAT3-DEEP-X2 bm-c forensics——本机 13:22 烧毕 "
    "done 无 crash·数据前置本机过）+MSG-1345（NULLS kill-advice——r506 "
    "已让路 kill·300 行 union 面留存）双件处置入 processed | 下轮指"
    "针: (1) T-141 s1+s3 建造开工（引擎骨架+N1 生成器移植 perpetual_"
    "faces 机器复用·CEO immediate 律=r508 首动作）(2) W9 12 分片烧录监"
    "控（daemon 自动续批）(3) CODELY.md 55.5KB>50KB 水位：bm-b 自有条"
    "目全在役坑律零流水可掏（r504 结构性注记）·阈值重锚=集团/GM 裁定"
    "面已入报告 | executive 三行实况: 当前活=N1-W9 SHARD-0 在烧（pid "
    "55796·12 分片队列）；最近实物=PERPETUAL-N1-W9-SHARD-0..11 物化+"
    "claim+LAUNCH@14:24（origin 45617b850 在案）；下个里程碑=T-141 bm-b"
    "引擎落地（窗 ≤48h·O-1410 验收 2026-10-08）+W9 finalize（烧毕即 "
    "finalize·窗 ≤8h） [via bm-b]\n")
with open(rp, "a", encoding="utf-8") as f:
    f.write(line)
print("round report line appended")

# --- CODELY.md S4 memory line ---
cp = os.path.join(ROOT, "CODELY.md")
mem = (
    "- [2026-10-01 14:3x r507 bm-b] 供给写入面×池冲突基底选错坑（N1-W9 "
    "供给重放实弹·16-UU 批池面姊妹坑）：perpetual_faces.py supply 的"
    "「single-writer lane write」实写共享面 runnable_pool.json（lane 孪"
    "生零承载——产物 commit 实证 shared=12 条 W9/lane=0 条）；池冲突解"
    "以 :2（origin 侧）为基底+sync_face 重derive=从 lane 找不回 W9（断"
    "言当场抓回）·正解=:3（含供给 payload 侧）为基底+sync_face 并入 "
    "origin 增量（对侧增量在场性先证：bm-c 认领在 bm-c lane 2 处在案）"
    "。姊妹面：perpetual_faces._pool_live_count 读共享面（POOL_PATH）"
    "非合并视图——lane done+共享 ready 漂移=供给停摆假 live（本轮 LOWAMP"
    "-P2-NULLS 幽灵即实例），compute_audit sync_face settle 即愈（S6 "
    "reconcile 先行顺序律为此设计）。How to apply：池面冲突选基底前必"
    "逐侧清点本方独有 payload（entry 计数断言）——共享面承载的写入（供"
    "给/手工登记）lane 不镜像、sync_face 只能并回 lane 有的；基底=含 "
    "payload 侧，对侧增量走 lane union；诊断供给停摆必三面对账（共享面"
    "×lane×合并视图）。\n")
with open(cp, "a", encoding="utf-8") as f:
    f.write(mem)
print("CODELY memory appended, size =", os.path.getsize(cp))
print("CLOSE2_OK")
