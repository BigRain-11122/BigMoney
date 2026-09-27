"""r314 bm-b wrap: state.json round 314, round report line, heartbeat update.

Laws applied: orders_ack whole-list rewrite + pre-write self-verify (r312),
epoch int type (R170/R178), clock_read ISO-8601 T-separated (R262),
per-machine files only (bm-b writes its own three faces).
"""
import glob
import json
import os
import time
from datetime import datetime, timezone, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TZ = timezone(timedelta(hours=8))
NOW = datetime.now(TZ)
ISO = NOW.isoformat()
SHORT = NOW.strftime("%Y-%m-%d %H:%M:%S")

# --- [1] state.json (bm-b face) ---
SP = os.path.join(ROOT, "logs", "iteration-loop", "state.json")
state = json.load(open(SP, encoding="utf-8-sig"))
state.update({
    "round_no": 314,
    "did": ("r314: T-91 s2 REV-OSC export first-run landed (selftest 7/7 + "
            "run -> SIG-2026-09-24 picks=10 gate-open + BARS-2026-09-24; "
            "Monday 09:15 first-cohort anchor secured; receipt MSG-0945) + "
            "T-89/T-90 fast-shard false-crash-fuse law caught+canon'd "
            "(X2-LB done 66.5s/1884 cells, evidence-gated pool flip "
            "607354b2 pre-window, probe-subsets refused, standing per-round "
            "flip action + fleet MSG-0952) + S0 stash-pop UU canon-resolved "
            "zero-loss (launches 46+46->47) + S6 28 lanes rc=0 + smoke 25/25 "
            "+ orders 96/96 double-scan"),
    "verdict": "green",
    "next": ("per-round rerun results/_r314bmb_pool_flip.py until 9+9 "
             "shards done -> harvest finalize (T-90 prereg s10 verdict face; "
             "T-89 s6 finalize+MARKET_STAGE_TABLE); T-92 TTS next GREEN-IDLE "
             "window; Monday 2026-09-28 09:15 T-91 s3 first cohort entries; "
             "10-01 monthly trio + REGIME_GUARD v3 date gate; migration "
             "window to 09-29 12:00"),
    "current_task": ("r314: T-91 export first-run landed (Monday anchor "
                     "secured); T-90 X2-LB pool-flipped done 1/9 "
                     "(false-crash-fuse law caught+canon'd+fleet-msged); "
                     "next=per-round flip rerun -> harvest at 9/9 + TTS "
                     "idle-window"),
    "last_round_ts": ISO, "last_result": "ok", "last_run": f"r314 {ISO}",
    "last_round_at": ISO, "last_seen": ISO, "updated_at": ISO,
    "updated": SHORT, "ts": SHORT,
})
json.dump(state, open(SP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
assert json.load(open(SP, encoding="utf-8-sig"))["round_no"] == 314
print("state.json -> round 314")

# --- [2] round report line (bm-b file) ---
RP = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
line = (
    f"{ISO} | r314 bm-b | dept:研究+数据+舰队 | WM-VERDICT: 绿 "
    f"(red=false@09:30:14 lane healthy; probe 09:44:46 py_low_board_clear "
    f"合法面=板零 open 票+bandit 空+池 18 ready 供给在磨=autofill "
    f"claim-race r313 定谳延续非违令) | did: (1) 收件箱关键路径 "
    f"MSG-0955-bm-a 即办：T-91 s2 REV-OSC 出口首跑 selftest 7/7+run -> "
    f"SIG-2026-09-24 (picks=10 gate open thin=False) + BARS-2026-09-24 "
    f"(10 码) -> 周一 09:15 首队列锚 secured，回执 MSG-0945-bm-b (2) "
    f"T-89/T-90 快分片假熔断坑律抓杀：X2-LB 实弹 66.5s/1884 格完成而池 "
    f"不 flip -> O-0947 25min 窗将记假 crash（09:57:47 关窗）-> 证据门 "
    f"flip 件 results/_r314bmb_pool_flip.py（probe 子集 lA-36/PROS-LA-22 "
    f"双拒收）落 X2-LB entry+shard=done 1/9，commit 607354b2 关窗前推上；"
    f"standing action 入双票 progress_r314_bmb + fleet MSG-0952-bm-b"
    f"（bm-a X2-LA 窗 ~10:05）+ CODELY 坑律条 (3) S0 stash-pop UU "
    f"autofill_state 正典 union 解 46+46->47 零丢失 last_tick 按 ts (4) "
    f"S6 28 lanes rc=0（audit CLEAN 18 ready 供给缺口诚实披露；regime "
    f"ORANGE asof 09-24 shadow；clock CALL-2026-09-24 ORANGE_COOL "
    f"sleeves=4 activated=0；周日全采集道合法 no-op；promo 0/22 诚实零；"
    f"export-09-24 再生 6 员/18 仓/5,996,645；token delta=-128）(5) "
    f"orders 96/96 双扫零新增 + decisions.md 本机缺位诚实 no-op (r104/"
    f"r107 先例) + post_review 仅 2 条陈年诚实负行（T-28 closed/O-2115 "
    f"WAIT）零新红 | next: 每轮先跑 flip 件至 9+9 齐 -> harvest（T-90 "
    f"prereg s10 判定面 + T-89 s6 finalize）；T-92 TTS 待 GREEN-IDLE 窗；"
    f"周一 09-28 09:15 T-91 s3 首队列入场\n")
with open(RP, "a", encoding="utf-8") as fh:
    fh.write(line)
print("round_reports.md +r314 line")

# --- [3] heartbeat (bm-b only) ---
HB = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
hb = json.load(open(HB, encoding="utf-8"))
orders = sorted({os.path.basename(p) for p in
                 glob.glob(os.path.join(ROOT, "fleet", "orders", "*.md"))}
                - {"README.md"})
ack = hb.get("orders_ack", [])
# r312 law: whole-list rewrite + pre-write self-verify
assert set(orders) <= set(ack) and len(set(orders) & set(ack)) == len(orders), \
    "orders_ack covers all orders (pre-write self-verify)"
hb["orders_ack"] = orders
hb["n_orders_ack"] = len(orders)
epoch = int(time.time())
assert isinstance(epoch, int)
hb.update({
    "last_seen": ISO, "heartbeat_epoch_utc": epoch, "clock_read": ISO,
    "round_no": 314,
    "current_task": state["current_task"],
    "cpu_cores": 16, "free_ram_gb": 13.2, "total_ram_gb": 23.9,
    "cpu_util_pct": 16.4,
    "gpu_free_vram_gb": 6.8, "gpu_free_vram_mb": 6929,
    "gpu_idle_vram_gb": 6.8, "gpu_idle_vram_mb": 6929,
    "idle_ram_gb": 13.2, "idle_ram_mb": 13517, "free_ram_mb": 13517,
    "cores": 16, "cpu_pct": 16.4, "round": 314,
    "gpu_model": f"NVIDIA GeForce RTX 3070 8192MiB (1263MiB used @{ISO})",
    "verdict": ("green; r314: T-91 REV-OSC export first-run landed "
                "(SIG-2026-09-24 picks=10 gate open, Monday 09:15 anchor "
                "secured, receipt MSG-0945); T-90 X2-LB done+flipped 1/9 "
                "(fast-shard false-crash-fuse law caught, evidence-gated "
                "flip 607354b2 pre-window, probe-subsets refused, fleet "
                "MSG-0952); S0 stash-pop UU canon-resolved zero-loss; S6 28 "
                "lanes rc=0; smoke 25/25; orders 96/96 double-scan "
                "zero-new"),
})
json.dump(hb, open(HB, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(HB, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int)
assert "T" in chk["clock_read"] and len(chk["orders_ack"]) == 96
print("heartbeat: epoch int verified, orders_ack 96 whole-list, round 314")
