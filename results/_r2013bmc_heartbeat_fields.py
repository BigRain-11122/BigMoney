"""r2013 heartbeat fields (merge-only via Tools/heartbeat_write.py)."""
import io
import json
import os
import time
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "_r2013bmc_heartbeat_fields.json")

now = datetime.now(timezone(timedelta(hours=8))).replace(microsecond=0).isoformat()
epoch = int(time.time())

fields = {
    "machine_id": "bm-c",
    "role": "compute-node",
    "venture": "bigmoney",
    "last_seen": now,
    "ts": now,
    "clock_read": now,
    "heartbeat_epoch_utc": epoch,
    "round": 2013,
    "round_no": 2013,
    "round_no_prev": 2012,
    "round_label": "r2013",
    "rounds_done": 1951,
    "state": "product",
    "status": "product",
    "verdict": "healthy",
    "水位": "healthy",
    "当前任务": (
        "r2013: 整手取整的账上那 22.83% 没投出去的钱（1000 万档）如果收盘扫进 GC001，"
        "整手账从 11.38% 涨到 11.71%/年（+0.33pp），全池臂从 8.84% 涨到 9.26%（+0.42pp）——"
        "现金腿帮全池更多，B-A 从 +0.2074% 掉到 +0.2004%/期（比 0.854→0.825），判词不变仍 EDGE_DEGRADES"
    ),
    "当前任务_en": (
        "r2013: the 22.83% cash leg at 10M earns GC001; black-list 11.38 -> 11.71%/yr, "
        "full pool 8.84 -> 9.26%/yr -- cash helps the full pool more, B-A 0.2074 -> 0.2004%/period, "
        "ratio 0.854 -> 0.825, verdict unchanged"
    ),
    "当前活": "给整手账里那 22.83% 没投出去的钱按真实 GC001 逆回购定价，看现金腿帮的是哪一臂",
    "最近实物": (
        "scripts/astock_veto_cash_leg.py（selftest 26/26）+ results/astock_veto_cash_leg.json + "
        "research/ASTOCK_VETO_CASH_LEG.md + 负控 results/_r2013bmc_cash_leg_negative.py（18/18）（2026-11-23 23:4x）"
    ),
    "下个里程碑": (
        "(a) 竞争窗结束后把本面接 smoke 两腿 + S6 腿（≤48h）"
        "(b) 把「整手把书换成另一本书」做成通用件：任何等权广度策略立项时先算价格倾斜与在场比例（≤48h）"
    ),
    "下轮指针": (
        "(a) 无竞争轮：smoke_test.py 两腿 + Tools/s6_chain_bmc.py 腿 + knowledge/METHODOLOGY_ASSETS.md 卡 + CODELY 两行 "
        "(b) 现金腿的期限阶梯：GC001 之外接 GC007/GC014 的跨周末溢价，看保守口径少算了多少"
    ),
    "本次": (
        "r2013: 1000 万档 A 臂在场 70.38%/现金 29.62%，B 臂在场 77.17%/现金 22.83%（差 +6.79pp）；"
        "GC001 期间收益均值 +0.1079%（年化 +1.37%）；net 0%→真 A 8.84→9.26，B 11.38→11.71；"
        "B-A 0.2074→0.2004%/期（t 3.04→2.93），比值 0.854→0.825；50M 档 0.941→0.935 仍 EDGE_SURVIVES"
    ),
    "本轮": (
        "r2013 现金腿：六档资本（1M..500M）每臂各自重算 net_with_cash；"
        "A 年化 1.56/8.54/8.84/7.52/7.22/6.98 -> 2.89/9.27/9.26/7.61/7.27/6.99；"
        "B 2.59/11.04/11.38/10.62/10.47/10.34 -> 3.87/11.65/11.71/10.69/10.50/10.34"
    ),
    "记账_r2013": "本行 1 处（轮报告）+ state 1 处 + 心跳 1 处 = 3（无方法论新增：给已有 family 加「现金腿」这条可执行性轴，属证据与载体）",
    "watermark_verdict": "green (red=false; lane healthy; repo_write_contention rc=3 CONTENTION -> new-file-only round)",
    "watermark_note": (
        "竞争探针 rc=3：3 宿主存活（pid 51252 11-22 20:10 起 / 67160 11-23 20:05 起 / 本宿），"
        "27 张共享面在本轮开始前被对端写，含 fleet/machines/bm-c.json、fleet/round_reports-bm-c.md、research/ARBITER-BOARD.md "
        "-> 按 r1927 只落新增文件面，未改共享代码/数据面、未跑 S6 链"
    ),
    "s0_note": "orphan_face_probe py_faces=3 orphans=0 零杀；repo_write_contention rc=3 CONTENTION（3 宿主，27 共享面被对端写）",
    "s05_note": "orders_ack_scan CLEAN (116 orders / 329 acks / 124 stale notes / unacked=[])；decisions.md 原字节 sha256 79e3083b85c130b8... == state 水位 -> 零新决策；fleet/inbox 空",
    "s6_chain": "not run (CONTENTION rc=3)",
    "smoke": "not run this round (CONTENTION); 以 26/26 selftest + 18/18 负控 + run/check 双 rc0 背书，不宣称全绿",
    "unverified": "full smoke suite not run this round; whole-chain S6 not run (shared faces written by peer hosts)",
    "s7_attrition": "attrition_ledger_guard scan CLEAN（4 账本，3 处历史缩行 healed）",
    "s7_claws": "pre-commit / pre-push 与 Tools/git-hooks/ 逐字节（CR 归一）MATCH",
    "s7_loop": "Bigmoney-IterationLoop phase ok（machine=bm-c pin=0 current=0，首燃 11/23 23:45 未动）",
    "孤儿面": 0,
    "孤儿面_note": "round-zero orphan_face_probe: orphans 0 (py_faces 3, resident_servers 1=ComfyUI idle)",
    "vcpu": 32,
    "ram_free_gb": 23.5,
    "ram_free_mb": 24064,
    "ram_free_pct": 42.0,
    "ram_total_gb": 55.9,
    "total_ram_gb": 55.9,
    "空闲RAM": "23.5 GB free / 55.9 GB",
    "vram_free_gb": 13.7,
    "vram_free_mib": 14011,
    "vram_total_gb": 16.0,
    "vram_total_mib": 16384,
    "vram_used_gb": 2.3,
    "本地未达 origin commit 数": 0,
    "本地未达origin": 0,
    "went_well": "现金腿不是加一个假设利率，而是把每一期的真实 GC001 报价接上去——两臂的现金权重不同，所以同一个利率对两臂的好处天生不对称，这一点只有真数据能印出来",
    "why_not_bookkeeping": "本轮主产出是新的可实现口径定价面（脚本+JSON+md+负控），不是记账",
    "who_did": "bm-c",
}

io.open(OUT, "w", encoding="utf-8", newline="").write(json.dumps(fields, ensure_ascii=False, indent=1))
print("fields ->", OUT, "epoch", epoch)
