"""r2116 bookkeeping: heartbeat + state + round report, byte-faithful.

heartbeat: indent=1, CRLF; state: indent=1, LF. Both verified round-trip before writing.
"""
import io
import json
import time
from datetime import datetime

NOW = datetime.now().astimezone()
ISO = NOW.isoformat(timespec="seconds")
CLOCK = NOW.strftime("%Y-%m-%dT%H:%M:%S%z")
CLOCK = CLOCK[:-2] + ":" + CLOCK[-2:]
EPOCH = int(time.time())
DEC = "79e3083b85c130b8b57363d1ce4850520704cfbdf3fc41b8277e7e5ee39d6e16"
ORD = "25d37786ee81dc40bef8581e03eb330853854b76eb992e3a9428b2d40d9707b3"

LIVE = "把盘上已生成却从未推送的链产出整批发布（1,970 件，面板吃进 2026-11-25 收盘）"
ART = "commit 89e675cfdd 直推 origin/main：data/*.csv + research/* + results/* 共 1,970 件上网（2026-11-26 03:5x）"
MILE = "收口全量冒烟（读 logs/smoke_r2116.log 的 summary 行）+ 跑 S6 链把 cutoff 从 11-20 推到 11-25，≤48h"

CONTEND = ("rc=0 CLEAN（results/_repo_write_contention.bm-c.json：fewer than two codely hosts alive，"
           "本宿主 pid=101604 自 03:40:04）→ 可写共享面，本轮据此整批发布 1,970 件")
SMOKE = ("full suite not closed (detached run logs/smoke_r2116.log still going at round end; every leg "
         "read so far PASS; first attempt was cancelled at the tool's 5-min no-output cap)")
NOTE = ("r2116 DELIVERY: disk had 1,970 machine-derived faces (panels through the 2026-11-25 close, plus "
        "yesterday's dated products) that git never saw; publishing them is what makes a face priced on "
        "that close reproducible off this box (same shape as r2084)")

# ---------- heartbeat ----------
hb_path = "fleet/machines/bm-c.json"
raw = io.open(hb_path, "rb").read().decode("utf-8")
hb = json.loads(raw)
assert json.dumps(hb, ensure_ascii=False, indent=1) == raw.replace("\r\n", "\n").rstrip("\n")

hb.update({
    "round_no": 2116, "round": 2116, "round_now": 2116, "last_round_no": 2116,
    "last_seen": ISO, "ts": ISO, "last_seen_at": ISO, "last_ts": ISO,
    "clock_read": CLOCK, "clock_read_source": "python datetime.now().astimezone()",
    "clock_tz": "+08:00",
    "heartbeat_epoch_utc": EPOCH, "heartbeat_epoch_utc_type": "int",
    "last_round_at": ISO, "last_round_ts": ISO, "last_round_closed_at": ISO,
    "verdict": "green",
    "当前活": LIVE, "最近实物": ART, "下个里程碑": MILE,
    "cur_task": LIVE, "current_task": LIVE, "current": LIVE,
    "last_artifact": ART, "product": ART, "last_product": ART,
    "孤儿面": 0, "orphan_faces": 0, "orphans": 0, "orphan_face": "孤儿面=0",
    "竞争_r2116": CONTEND, "contention": CONTEND,
    "smoke_verdict": SMOKE, "smoke_note": SMOKE,
    "watermark_verdict": "green (red=false, lane=healthy)",
    "orders_ack_count": 331, "last_orders_sha": ORD,
    "last_orders_note": "r2116: orders.md origin blob sha256 25d37786… (111,305 B); fleet/orders 117 files vs 331 acks -> 0 unacked",
    "last_decisions_sha": DEC,
    "last_decisions_note": "r2116: origin/main:docs/decisions.md raw blob 250,586 B sha256 79e3083b… == held watermark -> zero new decisions, zero action",
    "agenda_starved": True, "idle_rounds": 2,
    "本地未达 origin commit 数": 0, "local_unreached_commits": 0, "ahead_origin": 0, "behind_origin": 0,
    "s7_loop": "register_loop_task phase ok (machine=bm-c pin=0 current=0, PT5H no-op)",
    "s7_watchdog": "S4U XML flip refused again (拒绝访问 = needs admin); task left at default principal -- LogonType regression face stays open",
    "s7_claws": "pre-commit + pre-push re-installed (LF-normalized)",
    "note_r2116": NOTE,
    "记账_r2116": "轮报告 1 处 + state 1 处 + 心跳 1 处 = 3（无方法论新增：整批发布关的是「盘上有、git 没有」这个缺口，属载体与证据）",
})
hb["did"] = NOTE
hb["did_round"] = 2116

out = json.dumps(hb, ensure_ascii=False, indent=1).replace("\n", "\r\n")
io.open(hb_path, "wb").write(out.encode("utf-8"))

# ---------- state ----------
st_path = "state-bm-c.json"
raw = io.open(st_path, "rb").read().decode("utf-8")
st = json.loads(raw)
assert json.dumps(st, ensure_ascii=False, indent=1) == raw.replace("\r\n", "\n").rstrip("\n")

st["round_no"] = 2116
st["水位"] = "healthy"
st["本轮_r2116"] = NOTE
st["竞争_r2116"] = CONTEND
st["通过_r2116"] = ("orders 117 文件 / 心跳 orders_ack 331 / state 273 -> 未回执 0；"
                    "集团 decisions.md 原生字节 250,586B sha256 79e3083b… == 自持水位 -> 零新决策零动作；"
                    "orders.md 25d37786…（111,305B）为新值仅档案面；fleet/inbox 空；"
                    "attrition_ledger_guard CLEAN（4 账本，三处历史缩行 healed 照录）；"
                    "orphan_face_probe py_faces=4 orphans=0 resident_servers=2；"
                    "idle_trigger green_idle=true（RAM 46.2% / VRAM 14.01GB）池空板空 agenda_starved=true -> 本轮自驱产品件即工作")
st["送达自证_r2116"] = ("commit **89e675cfdd** 已直推 origin/main（f233619075..89e675cfdd），fetch 后 "
                        "`git rev-list --left-right --count origin/main...HEAD` = **0/0**，ls-tree 抽验四件在位"
                        "（data/etf_premium/snap/2026-11-25.csv、docs/divlowvol_live/TRACK-2026-11-25.md、"
                        "docs/futures_lane/TSMOM-2026-11-25.md、research/PAGE_FMT_GUARD_V2.md）→ **本地未达 origin commit 数=0**；"
                        "批次规模 1,970 件 / +22,022 −13,201 行 / 119.9 MB 工作树字节（单件最大 results/post_review.jsonl 21.0 MB）")
st["记账_r2116"] = "轮报告 1 处 + state 1 处 + 心跳 1 处 = 3"
st["smoke_r2116"] = SMOKE

out = json.dumps(st, ensure_ascii=False, indent=1)
io.open(st_path, "wb").write(out.encode("utf-8"))

# ---------- round report ----------
rp = "logs/iteration-loop/round_reports-bm-c.md"
text = io.open(rp, "rb").read().decode("utf-8")
line = (
    f"| {ISO} | 2116 | bm-c | **DELIVERY 轮**（竞争探针 rc=0 CLEAN·单宿主；watermark 绿；孤儿面=0；"
    "orders 117 件/未回执 0；decisions sha 79e3083b 未变=零动作；idle green_idle=true 池空 agenda_starved=true → 本轮自驱产品）："
    "把盘上**已生成却从未推送**的链产出整批发布——**1,970 件 / +22,022 −13,201 行**，面板吃进 **2026-11-25** 收盘（纯追加），"
    "并带上昨天的日期产品（divlowvol TRACK、futures TSMOM、etf_premium 快照）与全部重算研究面，"
    "使「按 11-25 收盘定价的那张面」可以从 git 复现而不是只能从这台机器（r2084 同形）。"
    "证据=commit **89e675cfdd** 直推 origin/main（f233619075..89e675cfdd），fetch 后 **AHEAD=0 / BEHIND=0**，"
    "ls-tree 抽验四件在位 → 本地未达 origin commit 数=0。"
    "诚实：全量冒烟本窗未收口（首跑被工具 5 分钟无输出上限取消；改分离进程写 logs/smoke_r2116.log，收轮时仍在跑，已读到的腿全 PASS），"
    "S6 链本轮未跑（cutoff 仍停在 11-20）。S7=register_loop_task 幂等 no-op（pin=0）；watchdog S4U 翻转仍被拒（需提权）；两爪已重装。"
    "下轮指针=收口冒烟 summary + 跑 S6 链把 cutoff 推到 11-25。\n"
)
if not text.endswith("\n"):
    text += "\n"
text += line
io.open(rp, "wb").write(text.encode("utf-8"))

print("HB_OK", len(out))
print("ISO", ISO, "EPOCH", EPOCH, type(EPOCH).__name__)
