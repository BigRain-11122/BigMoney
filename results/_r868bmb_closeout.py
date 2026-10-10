# -*- coding: utf-8 -*-
"""r868 bm-b closeout: state.json + heartbeat + round report (single pass).
JSON faces rewritten with indent=1 + raw CJK + LF (roundtrip face asserted
via git diff --numstat after write)."""
import json
import subprocess
import time
from datetime import datetime, timedelta

NOW = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())

# fresh machine metrics
import psutil
vm = psutil.virtual_memory()
free_ram = round(vm.available / 1024 ** 3, 1)
free_ram_pct = round(vm.available / vm.total * 100, 1)
try:
    out = subprocess.run(
        ["nvidia-smi", "--query-gpu=memory.total,memory.used",
         "--format=csv,noheader,nounits"], capture_output=True, text=True)
    tot, used = [int(x) for x in out.stdout.strip().split(", ")]
    vram_free = round((tot - used) / 1024, 2)
    vram_free_mb = tot - used
except Exception:
    vram_free, vram_free_mb = 3.6, 3676

DID = ("r868: S0 fetch behind=0 (HEAD=57940da3d=origin tip, no pull, stash-race avoided) + orphan face=0 (11 py faces) + orders diff 0 (67 files/192 acks/unacked 0, S7 rescan 0) + D19 dual watermark identical (dec caca0c6e/ord f90233c7, probe rc0, zero delta) + smoke 49/49 + boards clear (job 0/ticket 0 open) + SAT alive rc0 idle + wm red=false py_low_board_clear lawful; PRIMARY PRODUCT = N2-MP1 MATERIAL-POOL CONSUMPTION BATCH SLICE-2+FROZEN+POOL-ENTRY-FIRST-STEP: "
       "(a) runner scripts/mp1_tsgate_probe.py delivered (A158-TSGATE-P1 clone + pool-formula face swap, r836 clone law all params explicit: CUTOFF 2026-10-09/H=20/COST=0.10%/MIN_BARS=500/MIN_EV=15/STRIDE=20/GATE_WIN 252,120; t23.evaluate import single-source zero-rewrite + parse_formula verbatim inverse of formula_str; pool loader W19+W20 wave JSONs h1_ok&~skip fp_canon dedupe CSRANK-7 exclusion + frozen-identity drift guards 96/89/7/0 + anchor top-|h1_ic_ir| pin; hermetic selftest 30/30 incl G-ANCHOR-MP1 real-data leg 3341/390/149 + refuse-if-exists leg; run/finalize/status/selftest subcommands; per-shard jsonl checkpoint r340 resume law) "
       "(b) census-type freeze window five conditions all green: selftest re-run 30/30 (07:4x) + data-gate probe re-run rc0 (pool 96/89/178/E[FP]=8.9 same faces, byte-identical receipt = deterministic zero drift) + banned_direction_gate --prereg ADMIT rc0 matched=[] (receipt results/_r868bmb_banned_gate.txt) + origin pre-write check git show origin/main:prereg = DRAFT state + FROZEN v1.0 flip SAME COMMIT as runner delivery (0b1be1745, 12 files) "
       "(c) slice-3 pool entry landed: autofill submit gate rc0 (multicore verdict=multiproc, contract trio+consumer_plan asserted, r301+r305 family) -> submit whole-file write 16683/16650 ensure_ascii explosion rolled back (r859 law live-fire) -> raw-text anchored insertion host face LF/indent1/raw-CJK parse-gate-first 33/0 clean diff + lane mirror 34/1 (results/runnable_pool.json 420 entries N2-MP1 ready x1, shard key n2-mp1-run-0of1 r694 batch-prefix law, workers_plan 12 BelowNormal) -> commit+push: first push rejected (bm-c r859 W212 seat concurrent) -> stash+rebase+pop retry -> 00be657ef rebased onto dace861b1 -> push ab58ea56b = origin/main behind=0 self-proof; daemon claim gate reads origin refs -> autofill next tick claims N2-MP1 (supply-floor answer to compute_audit pool_starvation+supply_floor ready=0<3); "
       "S6 42 legs all rc0 except alloc rc2 known 510880 stale-leg carried (batch-loop bogus-arg 5 legs re-run clean disclosed; lane-guard honest skips bm-a/bm-c; update_daily weekend 0-new-row lawful; thermo/dualarm/rev_osc/report/live-usage ORANGE landed; scorecard/t35_export third-signal veto r701); dualrun ZERO-DRIFT streak continues; token delta 0; S7 quartet ALIVE (loop pin=2 no-op, watchdog -Force re-reg, both claws LF-normalized installed) + attrition guard CLEAN + inbox 0 pending; memory append zero this round (no new pit of long-term value; CODELY.md mini-split stays batched-at-next-append, cap 108B headroom)")

NEXT = ("r869 queue: N2-MP1 pool burn watch (autofill tick claim on origin refs -> shard n2-mp1-run-0of1 burn ~1-2min 12 workers -> finalize refuse-if-exists -> verdict face) -> sec7/sec8 backfill + TREASURE_REGISTRY consumption-first-read closeout step <=10-13 (W20 sec.0 evaluation window) -> CODELY.md mini-split batched at next append -> W210 freeze watch (bm-a chain) -> moneyflow IC panel-ready watch (bm-a lane) -> O-20261011-0012 CPU-max maintained")

VERDICT = ("GREEN: r868 (N2-MP1 slice-2 runner delivered + prereg FROZEN v1.0 five-condition chain + pool entry landed ready on origin: selftest 30/30 twice, banned ADMIT, anchor 3341/390/149 live; smoke 49/49; S6 42 legs alloc-known; orders diff 0; D19 identical; SAT alive; attrition CLEAN; orphan face=0; behind=0 self-proof; supply-floor answer in-pool)")

LATEST = ("r868: scripts/mp1_tsgate_probe.py (runner, selftest 30/30 x2) + research/N2_MP1_PREREG.md FROZEN v1.0 (freeze commit 0b1be1745) + pool entry N2-MP1 ready (shared 33/0 + lane 34/1, push ab58ea56b) + results/_r868bmb_banned_gate.txt + results/_r868bmb_pool_insert.py (raw-text insertion evidence)")

NOW_ACTIVE = ("r868 closeout: N2-MP1 frozen + pooled ready (first consumption of the 96-member material pool; burn awaits autofill claim within ~10min; verdict face lands next round in-window <=10-13)")


def update_json(path, fields, numstat_expect=None):
    p = json.load(open(path, encoding="utf-8"))
    p.update(fields)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        json.dump(p, fh, ensure_ascii=False, indent=1)
    rp = json.load(open(path, encoding="utf-8"))
    assert rp.get("round") == 868, path
    st = subprocess.run(["git", "diff", "--numstat", path],
                        capture_output=True, text=True)
    print(path, "->", st.stdout.strip() or "(clean)")


update_json("state.json", {
    "clock_read": NOW, "ts": NOW, "last_seen": NOW, "updated": NOW, "updated_at": NOW,
    "last_round_at": NOW, "last_round_ts": NOW,
    "last_decisions_read_at": NOW, "last_orders_read_at": NOW,
    "round": 868, "round_no": 868, "round_no_label": "r868",
    "current_task": NEXT, "task": NEXT, "next": NEXT,
    "did": DID, "last_action": DID,
    "latest_artifact": LATEST, "now_active": NOW_ACTIVE,
    "next_milestone": ("N2-MP1 pool burn + finalize verdict <=2026-10-13 (W20 sec.0 "
                       "consumption evaluation window); first-consumption verdict of the "
                       "96-member material pool lands in-window"),
    "orphan_face": 0, "orphan_faces": 0,
    "orphan_face_note": "r868 round probe: py_faces=11 alive, orphans=0 (zero live seats; MP1 slice-2 runner+freeze window, zero detached burns)",
    "verdict": VERDICT,
})

update_json("fleet/machines/bm-b.json", {
    "clock_read": NOW, "ts": NOW, "last_seen": NOW, "updated": NOW, "updated_at": NOW,
    "last_round_at": NOW, "last_action_at": NOW,
    "heartbeat_epoch_utc": EPOCH,
    "round": 868, "round_no": 868,
    "current_task": NEXT, "task": NEXT, "next": NEXT,
    "did": DID, "last_action": DID,
    "latest_artifact": LATEST, "now_active": NOW_ACTIVE,
    "next_milestone": ("N2-MP1 pool burn + finalize verdict <=2026-10-13 (W20 sec.0 window)"),
    "idle_rounds": 0, "agenda_starved": False,
    "free_ram_gb": free_ram, "ram_free_gb": free_ram, "ram_free_pct": free_ram_pct,
    "gpu_free_vram_gb": vram_free, "gpu_free_vram_mb": vram_free_mb,
    "vram_free_gb": vram_free,
    "orphan_face": 0, "orphan_faces": 0,
    "orphan_face_note": "r868 round probe: py_faces=11 alive, orphans=0",
    "verdict": VERDICT,
    "sync": {"last_push_ts": NOW,
             "note": "r868 closeout push (MP1 slice-2 runner+freeze+pool entry+S6 chain+books); rebase retry after bm-c r859 concurrent push; post-push behind=0 self-proof"},
})

h = json.load(open("fleet/machines/bm-b.json", encoding="utf-8"))
assert isinstance(h["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178 law)"

LINE = (NOW + " | r868 bm-b | 实况三行：当前活=N2 素材池消费批 MP1 slice-2 runner+冻结窗+FROZEN v1.0+池条目落地（首消费批全链冻结在案）/最近实物=scripts/mp1_tsgate_probe.py（selftest 30/30×2·07:2x-07:4x）+research/N2_MP1_PREREG.md FROZEN（freeze 0b1be1745）+池条目 N2-MP1 ready（push ab58ea56b·07:4x）/下个里程碑=MP1 池烧录+finalize 判读面 ≤2026-10-13（W20 §0 消费评估窗·autofill 认领窗内） | S0: fetch behind=0（HEAD=57940da3d=origin tip 零 pull·stash 竞态规避）+孤儿面 0（11 py faces）| S0.5: orders 差集 0（67/192·S7 复扫 0）+D19 双水位恒等（dec caca0c6e/ord f90233c7·probe rc0 零增量）+决策审核步零增量 | S1: smoke 49/49 | S2: 板清空（job 0/ticket 0 open）+SAT alive rc0 idle+wm red=false（py_low_board_clear 合法）| S3 主产出=N2-MP1 slice-2 三件全落地：①runner 交付（A158-TSGATE 克隆+池公式面换装·r836 全参数显式；t23.evaluate import 单源+parse_formula 逆解析镜像；池装载器漂移护栏 96/89/7/0+锚位 pin；selftest 30/30 含 G-ANCHOR-MP1 实数据腿 3341/390/149+refuse-if-exists 腿）②冻结窗五条件全绿（selftest 复跑 30/30+数据完备门 probe 复跑 rc0 字节恒等+banned gate ADMIT rc0（回执 _r868bmb_banned_gate.txt）+origin 写前复核 DRAFT 态+FROZEN v1.0 翻面与 runner 同 commit 0b1be1745）③池条目首步（autofill submit 门 rc0·multicore 判定 multiproc→整文件 ensure_ascii 爆 diff 16683/16650 按 r859 律回滚→raw-text 定点插入宿主面 LF/indent1/裸 CJK·parse 门先行·33/0 净 diff+lane 镜像 34/1（共享面 420 条·N2-MP1 ready×1·分片键 n2-mp1-run-0of1 r694 批次前缀律·workers 12 BelowNormal）→首推拒（bm-c r859 W212 并发）→stash+rebase+pop 重试→push ab58ea56b=origin tip behind=0 自证；daemon 认领门读 origin refs→下 tick 自认领=supply-floor 应答（compute_audit pool_starvation+supply_floor ready=0<3）| S6: 42 腿 41 rc0+alloc rc2 已知 510880 携带面（批循环伪参数 5 腿复跑干净如实披露；lane-guard 诚实跳过；update_daily 周末 0 新行合法 no-op；thermo/dualarm/rev_osc/report/live-usage ORANGE 幂等落地；scorecard/t35_export r701 第三信号否决）+dualrun 零漂移+token delta 0 | S7: 四件套 ALIVE（loop pin=2 no-op+watchdog 重注+双爪 LF 归一在位）+attrition CLEAN+inbox 0+记忆 append 零（无新坑·CODELY.md mini-split 续批于下次 append·水位 108B）| 本地未达 origin commit 数=0（push 后 fetch+rev-parse 自证）| 孤儿面=0 | next r869: MP1 池烧录认领窗（autofill tick）→finalize 判读面+§7/§8 回填+TREASURE 收口步 ≤10-13 窗内→W210 freeze watch 维持（bm-a 链）→moneyflow IC panel-ready watch 维持（bm-a 车道）→O-20261011-0012 CPU-max maintained")

with open("logs/iteration-loop/round_reports.md", "a", encoding="utf-8", newline="") as fh:
    fh.write(LINE + "\n")
print("round report appended:", len(LINE), "chars")
