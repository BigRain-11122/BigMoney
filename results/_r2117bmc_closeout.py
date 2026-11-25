# -*- coding: utf-8 -*-
"""r2117 closeout: bookkeeping only (round report row, state, heartbeat).

Every write round-trips through load->dump->compare so a formatting drift cannot silently
bury a concurrent field (r2043/r2090 family): state and heartbeat are both indent=1 + CRLF,
and state ends with one extra CRLF.
"""
import io
import json
import os
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

ROUND = 2117
NOW = "2026-11-26T05:05:00+08:00"

REPORT = "logs/iteration-loop/round_reports-bm-c.md"
STATE = "state-bm-c.json"
HB = "fleet/machines/bm-c.json"


def load(path):
    raw = io.open(path, "rb").read()
    return json.loads(raw.decode("utf-8")), raw


def dump(path, obj, crlf=True, extra_newline=False):
    text = json.dumps(obj, ensure_ascii=False, indent=1)
    if extra_newline:
        text += "\n"
    if crlf:
        text = text.replace("\n", "\r\n")
    io.open(path, "wb").write(text.encode("utf-8"))


def same_shape(old_raw, path, obj, crlf=True, extra_newline=False):
    """Round-trip: re-serialise the OBJECT WE LOADED and require the bytes back."""
    tmp = path + ".roundtrip"
    dump(tmp, obj, crlf=crlf, extra_newline=extra_newline)
    got = io.open(tmp, "rb").read()
    os.remove(tmp)
    return got == old_raw


# ---------------------------------------------------------------- state
st, st_raw = load(STATE)
if not same_shape(st_raw, STATE, st, crlf=False):
    raise SystemExit("state round-trip mismatch -- refusing to write (format drift)")
st["round_no"] = ROUND
st["本轮_r2117"] = (
    "r2117 PRODUCT: the minute panel got its first reader (it had a writer since 2026-09-15 and "
    "no consumer anywhere -- product on disk, r1108 family). New face scripts/minute_feed_first_reader.py "
    "audits the delivery, prices the 10:00-instead-of-open fill, and sizes the intraday-reversal "
    "question the block board still files as data-blocked. Findings: no 09:30 auction print exists "
    "in any of the 44 full sessions (so the panel cannot price the fill the book actually assumes); "
    "14:58/14:59 are routinely missing; waiting 30 minutes averaged -12.9bp per session with sd "
    "63.7bp on n=44 sessions (t=-1.35) -- a dispersion fact, not a timing edge; the reversal slopes "
    "(-0.56/-0.58 on the two broad ETFs, ~0.1-0.2 elsewhere, n=44 each) cannot clear a five-test "
    "correction, and a 5bp/session claim would need 1,600+ sessions per symbol."
)
st["竞争_r2117"] = (
    "rc=0 CLEAN (results/_repo_write_contention.bm-c.json: fewer than two codely hosts alive; "
    "this host pid=19496 from 04:40:04). Separate from that, Tools/s6_chain_bmc.py round 2117 was "
    "already in flight (started 04:15:16 by the loop task, pid 80572 pythonw) and kept rewriting "
    "shared faces through the round -- so this window published new files only and did not run a "
    "second chain."
)
st["通过_r2117"] = (
    "orders 117 files / heartbeat orders_ack 331 / state 273 -> unacked 0 (stale_acks only the "
    "pre-2026-10-26 lane broadcasts, r2066 precedent); fleet group decisions.md raw bytes 250,586B "
    "sha256 79e3083b85c130b8... == own watermark -> zero new decisions, zero action; fleet/inbox "
    "empty; orphan_face_probe py_faces=6 orphans=0 resident_servers=2; idle_trigger green_idle=false "
    "(s6_chain_running=1) so the starved-agenda self-drive clause did not apply."
)
st["smoke_r2117"] = (
    "full suite run 04:43-04:5x overlapped the in-flight chain and ended with 8 red legs; re-running "
    "two of them after the chain moved on (etf_label_census 20/20, etf_book_capacity_ticket 14/14) "
    "proves the class: faces were being rewritten while the comparison legs read them. One red is "
    "NOT that class and is carried as next round's P0: etf_book_supply_gate_decision 19/21 with "
    "CHECK FAIL drift=money_constructions_that_are_gifts/cross_receipt_agreement/sources -- the "
    "year-gate wrapper was re-derived at cutoff 2026-11-25 and now reads CONDITIONAL for "
    "ticket_construction_plain_plus_overlay because Y4_top2_share fails (top-2 years 78.35% of the "
    "annual sum against a 70% cap), while the frozen caliber receipt (cutoff 2026-11-06, caliber A) "
    "still reads ADMIT, and leg L13b hard-codes that ADMIT. The ticket faces currently publish "
    "TRADABLE_AT_1000000 on cutoff 2026-11-24, i.e. a size priced on a permission that moved at the "
    "11-25 close. Next round must decide which receipt is authoritative on the 11-25 evidence and "
    "re-say the ticket's size -- not relax the leg."
)
st["记账_r2117"] = "轮报告 1 处 + state 1 处 + 心跳 1 处 = 3（方法论卡锁存待无竞争轮）"
dump(STATE, st, crlf=False)

# ---------------------------------------------------------------- heartbeat
hb, hb_raw = load(HB)
if not same_shape(hb_raw, HB, hb):
    raise SystemExit("heartbeat round-trip mismatch -- refusing to write (format drift)")
epoch = int(time.time())
hb["last_seen"] = NOW
hb["activity_now"] = (
    "r2117: the minute panel got its first reader (audit + 10:00-vs-open fill ladder + reversal "
    "power ceiling); chain 2117 published in flight, so new files only"
)
hb["activity_now_round"] = ROUND
hb["activity"] = "product"
hb["clock_read"] = NOW
hb["ts"] = NOW
hb["heartbeat_epoch_utc"] = epoch
hb["ahead_origin"] = 0
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["orphan_faces"] = 0
hb["verdict"] = "round 2117 product landed; one substantive red carried (supply-gate ticket permission moved at the 11-25 close)"
dump(HB, hb)
assert isinstance(json.loads(io.open(HB, "rb").read().decode("utf-8"))["heartbeat_epoch_utc"], int)

# ---------------------------------------------------------------- round report
row = (
    "| 2026-11-26T05:05:00+08:00 | 2117 | bm-c | "
    "**PRODUCT 轮**（竞争 rc=0 CLEAN·单宿主；但 S6 链 r2117 自 04:15 起已在跑，整轮重写共享面 → "
    "本窗只落新增文件面、不跑第二条链；watermark 绿 red=false lane=healthy；孤儿面=0；"
    "orders 117/未回执 0；decisions sha 79e3083b 未变=零动作）："
    "**分钟面板拿到第一个读者**——`data/minute_feed/` 自 2026-09-15 有写手、全仓无任何消费者（r1108 族"
    "「有产无读」）。新面 `scripts/minute_feed_first_reader.py`（selftest 12/12，`--check` 直接问 CSV，"
    "漂移说 STALE、算错说 CHECK FAILED 且不带 STALE 字样）：①**交付审计**——9 个符号、5 个深符号各 44 个完整"
    " session，**全部 44 个 session 都没有 09:30 竞价打印**（面板永远价不到书真正成交那一笔），14:58/14:59 "
    "例行缺失；②**执行阶梯**（5 深符号先 session 内平均，n=44 而非虚高的 252）：等到 10:00 平均 −12.94bp、"
    "sd 63.73bp、t=−1.35 —— 是离散度事实，不是择时优势；③**被看板判「数据阻塞」的问题定价**：首半小时→当日"
    "剩余 的斜率 −0.56（t=−2.58）/ −0.58（t=−1.82）/ 其余 ~+0.1~0.2，五条同时测过不了校正线；"
    "5bp/session 的论断每符号还需 1,600+ 个 session。已接线为链腿 `minute_feed_first_reader`（check+STALE 才付 refresh）。"
    "**另起 P0（下一轮）**：冒烟 8 红里 7 条复跑即绿（面在动族：etf_label_census 20/20、etf_book_capacity_ticket 14/14），"
    "但 `etf_book_supply_gate_decision` 是真红——year-gate wrapper 在 11-25 收盘重算后对该票构造读 CONDITIONAL"
    "（Y4：前两年占年度和 78.35% > 70% 上限），而冻结的 caliber 收据（cutoff 11-06/A）仍读 ADMIT，"
    "L13b 又把 ADMIT 写死；票面此刻仍按 11-24 发布 TRADABLE_AT_1000000 = **尺寸建立在一个今天已翻面的许可上**。"
    "下一轮必须先定哪张收据对 11-25 证据有权威再改尺寸，禁放宽腿。 |\n"
)
with io.open(REPORT, "ab") as f:
    f.write(row.encode("utf-8"))
print("closeout written: state+heartbeat+report (round %d, epoch %d int=%s)"
      % (ROUND, epoch, isinstance(epoch, int)))
