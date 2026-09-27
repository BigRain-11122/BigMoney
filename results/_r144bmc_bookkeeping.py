# results/_r144bmc_bookkeeping.py -- R144 S5/S7 ledger writes (bm-c)
# In-memory assembly -> single atomic write per face (r365 law); JSON epoch
# INT (R170/R178), clock_read T-separator (R262), orders_ack preserved.
import json
import os
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
now = time.time()
epoch = int(now)
clock = time.strftime("%Y-%m-%dTH:%M:%S+08:00", time.gmtime(now + 8 * 3600))

# --- S5 round report append ---
RP = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
line = (
    "2026-09-28T07:32:00+08:00（钟读实测）｜R144｜bm-c (dept:舰队 storm + 工程维护链)｜"
    "WM verdict: green (probe 07:24:08 py_low_board_clear 合法白名单: 板 0 open+job 0+"
    "bandit 0+bars_present false; pool_ready=1=W2-JUDGE gate-hold 非可跑面)｜"
    "S0=r143 push-storm discharge 闭环: pull --rebase 撞 9-UU（First 20 截断只见 6 面·"
    "3 面漏至 add 段暴露=r144 新坑律）-> 7 注册面 merge_lane_views resolve 全 canon + "
    "CODELY/archive r384 双向覆盖并集（批33 同窗撞号=origin r389 bm-a 窗先落·我侧让路注记"
    "零内容损失）+ 批34 折（union 10895B 超线->9002B）-> 双 pick 落地 edc0e3f7+694d0a0a "
    "-> push LANDED + reconcile 13 面全零漂移; S0.5=orders 99/99 差集空（r136 后缀归一）·"
    "decisions 无新行·MSG-0725 收执归档; S1=smoke 25/25; S6=25 动作全 rc=0（audit CLEAN·"
    "regime breadth 0.77 trigger·clock ORANGE_COOL sleeves=4 activated=0·12 采集 gate "
    "诚实 no-op·fundamental 22h fresh skip·daily_report 4 面再生）; S4=CODELY 双坑律入热"
    "（截断藏面 + PS BOM 剥除 r361 变体·实弹捕获回植复检 1+/0-）+ 批35 折（10258B->8752B）; "
    "S7=三检绿（loop pin5 no-op/watchdog 07:40/claw 重装）｜验证=push landed 694d0a0a+"
    "13 面零漂移+smoke 全绿｜下轮指针: census bm-b ETA~10:30 -> RAM 门 3 采后 bm-b flip "
    "W2-JUDGE（勿抢 lane_owner）; 本机 py 低=合法待命; 15:30 后 fund_premium snapshot+"
    "intraday 采集窗"
)
with open(RP, "rb") as fh:
    rp = fh.read()
rp.decode("utf-8")
rp += line.encode() + b"\n"
with open(RP, "wb") as fh:
    fh.write(rp)

# --- state file: round 143 -> 144 ---
SP = os.path.join(ROOT, "state-bm-c.json")
state = {
    "machine_id": "bm-c",
    "round_no": 144,
    "updated": clock,
    "note": ("r144: r143 push-storm DISCHARGED (9-UU canon-resolved: 7 registry "
             "faces via merge_lane_views resolve + CODELY/archive r384 coverage "
             "union + batch-33 same-window yield-note; both picks landed "
             "edc0e3f7+694d0a0a, push LANDED, reconcile 13/13 zero-drift) + "
             "CODELY watermark double-fold (b34 r141/r142 10895->9002B; b35 "
             "r389CRLF/r365 10258->8752B) + 2 new pitlaws (truncation-hides-UU + "
             "PS BOM-strip r361 variant, BOM restored byte-face) + S6 25 legs "
             "rc=0 + smoke 25/25 + orders 99/99 + MSG-0725 archived + W2-JUDGE "
             "gate-hold honored (bm-b flip owner, census ETA ~10:30)"),
    "last_round_ts": clock,
    "updated_at": clock[:10] + " " + clock[11:16],
}
blob = json.dumps(state, ensure_ascii=False, indent=1)
with open(SP, "wb") as fh:
    fh.write(blob.encode() + b"\n")

# --- heartbeat: preserve orders_ack + peers, update my fields ---
HP = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
with open(HP, "r", encoding="utf-8") as fh:
    hb = json.load(fh)
hb["last_seen"] = clock
hb["current_task"] = "r144 done: push-storm discharge closed (push landed 694d0a0a); legal-idle await W2-JUDGE flip (bm-b owner)"
hb["cpu_cores"] = 32
hb["free_ram_gb"] = 6.1
hb["gpu_free_vram_mb"] = 10335
hb["verdict"] = "py_low_board_clear legal-idle (pool=W2-JUDGE gate-hold; census burn bm-b ETA ~10:30)"
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = clock
assert isinstance(hb["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in hb["clock_read"], "clock_read must be T-separated"
with open(HP, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)
    fh.write("\n")

# post-write self-verify
with open(HP, "r", encoding="utf-8") as fh:
    back = json.load(fh)
assert isinstance(back["heartbeat_epoch_utc"], int)
assert len(back.get("orders_ack", [])) == 99, f"orders_ack lost: {len(back.get('orders_ack', []))}"
with open(SP, "r", encoding="utf-8") as fh:
    json.load(fh)
print(f"report R144 line appended ({len(line)} chars); state round_no=144; "
      f"heartbeat epoch={epoch} int, clock={clock}, orders_ack=99 preserved")
