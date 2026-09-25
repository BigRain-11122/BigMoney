# -*- coding: utf-8 -*-
"""r224 (bm-b) S7 closeout: state.json, heartbeat, round report append.
All writes byte-safe (no PS redirection, r209 law); epoch must be JSON int
(R170/R178 double-offence law); parse-verify after every write (r185 law).
"""
import datetime
import json
import time

now = datetime.datetime.now()
ts = now.strftime("%Y-%m-%d %H:%M")
iso = now.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
epoch = int(time.time())
assert isinstance(epoch, int)

# ---- 1. state.json (bm-b own file) ----
sp = "logs/iteration-loop/state.json"
st = json.load(open(sp, encoding="utf-8"))
assert st["round_no"] == 223, st["round_no"]
st.update({
    "round_no": 224,
    "did": ("P-1e MCLOSETR nulls shard harvest-verified + pool flip done "
            "(mask bit-match 16638518 production-form probe, seed band "
            "67050-67100, equiv 2.2e-16; flip 04:57 before 05:00 tick = "
            "zero no-op re-fire waste, r203 pool-flip-is-round-work) + S0 "
            "autofill_state stash-pop UU resolved via bm-a R218 "
            "conflict-resolve skill (classifier + mixed-dict+ledger recipe, "
            "CRLF producer mirror)"),
    "verdict": "green",
    "next": ("r225: P-1e harvest watch (MARC dispatched at 05:00 tick, est "
             "~05:32 landing; CELLS after; on 4/4 = finalize fail-closed + "
             "judgement table + factor ledger +157 + prereg sec7/8 backfill; "
             "0 survivor = honest line-close); 09-28 Monday new-bar full "
             "chain; EM push2his south re-probe daylight 12:00-13:40; bm-c "
             "noon window 09-28 15:30 (T-16 NAV eval)"),
    "current_task": ("P-1e batch 2/4 done (MCLOSE+MCLOSETR flipped; MARC "
                     "dispatching 05:00, CELLS queued); r225+ harvests on 4/4"),
    "last_round_ts": "2026-09-26 04:25",
    "last_result": ("exit 0 all legs (17 run + 7 new-bar-gated weekend skip: "
                    "cutoff 09-24, next bar 09-28); MCLOSETR flipped r224"),
    "last_tick": ts,
    "updated_at": ts,
    "last_seen": ts,
    "ts": ts,
    "last_ts": ts,
    "last_run": iso,
    "last_round_at": ts,
})
raw = json.dumps(st, ensure_ascii=False, indent=1)
with open(sp, "wb") as f:
    f.write(raw.replace("\n", "\r\n").encode("utf-8"))
chk = json.load(open(sp, encoding="utf-8"))
assert chk["round_no"] == 224
print("state.json OK: round_no", chk["round_no"])

# ---- 2. heartbeat fleet/machines/bm-b.json ----
hp = "fleet/machines/bm-b.json"
h = json.load(open(hp, encoding="utf-8"))
h.update({
    "last_seen": ts,
    "heartbeat_epoch_utc": epoch,
    "clock_read": iso,
    "current_task": ("r224: P-1e MCLOSETR flipped done 2/4; MARC/CELLS on "
                     "autofill cadence; harvest finalize on 4/4"),
    "cpu_cores": 16,
    "cores": 16,
    "free_ram_gb": 11.3,
    "idle_ram_gb": 11.3,
    "total_ram_gb": 23.9,
    "gpu_free_vram_gb": 2.4,
    "gpu_free_vram_mb": 2413,
    "cpu_util_pct": 7.0,
    "round_no": 224,
    "verdict": "green",
})
raw = json.dumps(h, ensure_ascii=False, indent=1)
with open(hp, "wb") as f:
    f.write(raw.replace("\n", "\r\n").encode("utf-8"))
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), \
    "EPOCH NOT INT (F7 red, R170/R178 law)"
print("heartbeat OK: epoch", chk["heartbeat_epoch_utc"], "type",
      type(chk["heartbeat_epoch_utc"]).__name__)

# ---- 3. round report append (byte-safe) ----
line = (
    "2026-09-26 05:0x | r224 bm-b (dept:工程+研究) | "
    "WM-VERDICT: 绿：red=false@04:55 lane healthy；probe 04:55 py_low_board_clear="
    "合法 idle 白名单实证：票 0 open+bandit 0+bars 在位+pool 2 ready（MARC/CELLS="
    "autofill 非轮面）；audit 04:55 CLEAN pool_ready=2 supply-gap 非饥饿 | "
    "S0: 身份 machine.json=bm-b（r191 律）；轮首脏=本机 watchdog autofill_state tick"
    "产物→stash→pull --rebase 吸收 bm-a R218（conflict-resolve skill 落地面首消费："
    "classify_conflicts.py 先跑=1-UU 全分类零 UNKNOWN→mixed-dict+ledger 配方手解 "
    "_r218b_resolve.py：launches 50+50→union 51→cap50 零丢失、last_tick 04:50:01 "
    "取新 dict 整赋值 r203 律、行尾探 stage3 生产者 CRLF 同风格写回 r223 律、parse 过"
    "才 add r185 律；stash drop 零残留） | "
    "S0.5: orders 74/74 轮首+收尾双扫零未回执（token 全文件名口径 r220 律）；"
    "decisions.md 候选根全缺位诚实 no-op（七连先例）；inbox 零他机未读 | "
    "S1: smoke 25/25 | "
    "S3 主交付: **P-1e MCLOSETR nulls 分片收割验证+池翻面 done（r203 "
    "pool-flip-is-round-work）**——产物 ~04:52 落地（pid24824 已退，elapsed 1902.8s"
    "≈32min/片预估吻合）：n_nulls=50/per_h 3-col/equiv 2.22e-16 PASS/seed_band "
    "67050-67100=prereg 连续账本位/mask_cells 16638518==_r224_mask_probe.py 生产装载"
    "形态配对探针位咬合（close+tr 装载→M_close+M_close_tr 双 mask=r221 装载形态律、"
    "share 0.3624）；翻面 _r224_flip.py fail-closed 五腿全过→entry+shard done+"
    "done_flip 证据块（镜像 r222 格式）；commit 42c0d4b0 已推；**E1 坑自捕：分片已落地"
    "未翻面窗口=r180 done-skip 盲区（runner 已死非 alive+owner 本机 fresh+shard 仍 "
    "ready→autofill 每 tick 重复发射幂等空转+claim 垃圾 commit+MARC/CELLS 整窗饿死），"
    "04:52 落地→04:57 翻面→05:00 tick 零浪费实证**；status 面：nulls 2/3 cells 0/7 "
    "final=False（4/4 收割待 MARC ~05:32+CELLS 随后落地） | "
    "S4: 1 坑律入册（landed≠flipped 窗口饥饿机制+r203 补篇）水位 19.4KB<50KB 无整编"
    "触发 | "
    "S6: 17 腿全绿+7 新 bar 腿合法跳过（周末 cutoff 09-24→下 bar 09-28）：audit "
    "CLEAN/probe py_low_board_clear/daily 周末 0 新行/regime ORANGE d2 shadow 四连"
    "（hs300<MA200+breadth 0.77）/lhb 30min 节流 no-op/heat 周末 no-op/futures 零网络"
    "no-op/options+mf+ths+ah=bm-a 车道+fp=bm-c 车道 R31 诚实 no-op/fundamental 7.7h "
    "新鲜跳过/blf 四门过 5222/3517/scorecard 6 员/build_status OK/token delta=5 | "
    "S7: schtasks 三任务健康（IterationLoop 运行中=本实例+Autofill/Watchdog 就绪 "
    "05:00=R49 律零重建）；orders 收尾复扫 74/74 零未回执；inbox 零未读；state "
    "223→224；心跳 epoch python int 自证 | "
    "下轮指针: ①P-1e 4/4 收割窗（MARC 05:00 tick 发射→~05:32 落地、CELLS 随后 "
    "tick→est 4-5min；4/4 落后收割轮做 finalize fail-closed+判定面+因子账本 +157 "
    "append_ledger embed+prereg §7/§8 回填，0 幸存=诚实线收）→②09-28 周一新 bar 全链"
    "（update_daily→live.paper REGIME_GUARD v3 enforce→t35verify→t24×2→aggr/alloc→"
    "export/scorecard）→③EM push2his 南向 re-probe 白日窗 12:00-13:40→④bm-c 午窗 "
    "09-28 15:30（T-16 NAV 接管评估）→⑤T-54 B2 侧给等待同窗（T-49 C2 结局/T-53 "
    "s2-5 侧给后组批）\n"
)
with open("logs/iteration-loop/round_reports.md", "ab") as f:
    f.write(line.encode("utf-8"))
print("round report appended:", len(line.encode("utf-8")), "bytes")
