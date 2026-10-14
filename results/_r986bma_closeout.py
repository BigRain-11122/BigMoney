# -*- coding: utf-8 -*-
# r986 bm-a closeout: state round_no 986 + heartbeat + round report line
import json, datetime, time, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
now_dt = datetime.datetime.now().astimezone()
now = now_dt.isoformat(timespec="seconds")
epoch = int(time.time())

# 1) state round_no 985 -> 986
sp = os.path.join(ROOT, "state-bm-a.json")
d = json.load(open(sp, encoding="utf-8"))
prev_round = d.get("round_no", 985)
d["round_no"] = 986
json.dump(d, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# 2) heartbeat
hp = os.path.join(ROOT, "fleet", "machines", "bm-a.json")
h = json.load(open(hp, encoding="utf-8"))
h["active"] = True
h["last_seen"] = now
h["current"] = ("r986: W240 seat REGISTERED (pre-seat probe rc0 ADMIT: A 545_501..547_500 seed-545_500 hop / "
                "B 540_804..541_003, both seed_admit_gate FREE, origin vacancy held; seat MSG-20261014-1325 "
                "published, 230th wave candidate, bm-a 123rd owned, queue-depth-2 supply; freeze waits-upstream "
                "W239 finalize M12) + D-19 DEC/ORD both consumed zero BigMoney directives watermark advanced + "
                "idle_trigger --worked (idle_rounds 2->0) + S6 41-leg chain detached")
h["current_task"] = h["current"]
h["idle_rounds"] = 0
h["agenda_starved"] = False
h["heartbeat_epoch_utc"] = epoch
h["clock_read"] = now
h["ts"] = now
h["verdict"] = ("green (red=false lane=healthy; satengine ALIVE queue0; W238 finalize LANDED ledger 947,935/K 521,520; "
                "W239 bm-c seat freeze-next unblocked post-W238-finalize; W240 seat REGISTERED bm-a r986 queue-depth-2; "
                "supply chain: W239 freeze -> W239 finalize -> W240 freeze next)")
json.dump(h, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# epoch int self-check
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "F7: epoch must be JSON int"
assert "T" in chk["clock_read"] and "+" in chk["clock_read"], "F7: clock_read T-separator"

# 3) round report line
rp = os.path.join(ROOT, "round_reports-bm-a.md")
line = (
    now + " | r986 | bm-a | dept:工程/舰队（W240 席位发布=S3 供给线主使命+D-19 双水位消费）| "
    "WM-VERDICT: green (red=false lane=healthy; satengine ALIVE queue0 idle->worked; supply chain: W239 freeze next "
    "(bm-c waits-upstream DISARMED post-W238-finalize) + W240 seat REGISTERED bm-a (this round, queue-depth-2)) | "
    "孤儿面=0 (round-zero probe 44 py faces) | "
    "S0: autostash pull ff 43893cd85 (bm-b r932 closeout; attrition face UU=轮转再生面 take-origin 弃本地陈扫) + "
    "D-19 DEC d9d8aa72/ORD 3095bc17 双 delta 消费全零 BigMoney 行=水位键推进零动作 (board L7..L89 零 pending 涉本司行) + "
    "S0.5 orders ack scan CLEAN (88 orders/90 acks/0 unacked/0 stale) | "
    "S1 smoke 49/49 PASS | "
    "S3 主使命 W240 席位: pre-seat probe _w240bma_20261014_probe.py rc0 ADMIT -- A 545_501..547_500 (naive 544_501..546_500 "
    "被 live SEED_REGISTRY 545_500 拒=注册尾上首例 seed-refusal 面·hops=1) / B 540_804..541_003 (W239-DECLARED B tail+1 干净·"
    "seed-decoupled gap 继承面·无 own-A 预留跳)，双带 seed_admit_gate rc0 FREE，origin 四查空悬保持；"
    "seat MSG-20261014-1325-bma-w240-seat 发布 (230th wave candidate, bm-a 123rd owned, depth-2: W239 declared+本候选; "
    "W240 freeze waits-upstream W239 finalize M12 物理依赖+watch armed) | "
    "S7: idle_trigger --worked (idle_rounds 2->0) + W238 finalize MSG 归档 processed + attrition guard CLEAN (4 ledgers) + "
    "S6 41-leg chain detached pid 34724 | "
    "最近实物: fleet/inbox/MSG-20261014-1325-bma-w240-seat.md + results/_w240bma_20261014_probe_receipt.json (13:25) | "
    "下个里程碑: W239 finalize 落地后 W240 freeze 五面拼接（bm-c freeze 窗在途·W240 freeze 窗 ≤48h）| "
    "本地未达 origin commit 数=0 (push+ls-tree 自证随收尾)"
)
with open(rp, "a", encoding="utf-8", newline="\n") as f:
    f.write("\n" + line + "\n")

print("closeout done: round 986, epoch", epoch, "prev", prev_round)
