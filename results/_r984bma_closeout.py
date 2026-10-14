# -*- coding: utf-8 -*-
# r984 bm-a closeout: state + heartbeat + round report (fresh-read-modify-write law)
import json, time, datetime

now = datetime.datetime.now().astimezone()
iso = now.strftime("%Y-%m-%dT%H:%M:%S") + now.strftime("%z")[:3] + ":" + now.strftime("%z")[3:]
epoch = int(time.time())

# --- state-bm-a.json ---
sp = r"fleet\machines\..\state-bm-a.json"
import os
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sp = os.path.join(REPO, "state-bm-a.json")
s = json.load(open(sp, encoding="utf-8"))
s["round_no"] = 984
s["round"] = 984
s["current"] = "r984: W238 five-face splice LANDED 50fa77623 + engine self-burn in flight"
s["next"] = "r985: W238 burn 12/12 absorb -> PRE-FINALIZE six-gate -> finalize one-pass (window <=48h); S6 chain r984 products absorb"
json.dump(s, open(sp, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

# --- heartbeat fleet/machines/bm-a.json ---
hp = os.path.join(REPO, "fleet", "machines", "bm-a.json")
h = json.load(open(hp, encoding="utf-8"))
h["active"] = True
h["now_active"] = True
h["clock_read"] = iso
h["ts"] = iso
h["last_seen"] = iso
h["updated_at"] = iso
h["heartbeat_epoch_utc"] = epoch
h["last_heartbeat_epoch_utc"] = epoch
h["heartbeat_epoch_utc_type_int"] = True
h["last_round"] = 984
h["last_round_at"] = iso
h["round"] = 984
h["round_no"] = 984
h["last_round_closed"] = 984
h["current"] = "r984: W238 five-face splice LANDED 50fa77623 (engine self-burn 7/12+ in flight) + S6 41-leg chain detached pid 49968 + 3 orders acked (0942/0948/0949) + DEC/ORD dual-delta consumed"
h["current_task"] = h["current"]
h["task"] = h["current"]
h["last_action"] = "W238 five-face freeze splice + engine ignition + orders ack + D-19/ORD watermark refresh"
h["last_artifact"] = "W238 splice commit 50fa77623 on origin (bands A 538_404..540_403 / B 540_404..540_603; freeze receipt results/_w238bma_freeze_receipt.json; pf selftest 9/9 + n1 selftest PASS)"
h["recent_artifact"] = h["last_artifact"]
h["latest_artifact"] = h["last_artifact"]
h["next"] = "W238 burn 12/12 -> PRE-FINALIZE six-gate (standing law) -> finalize one-pass (window <=48h); bars 15:30 today -> S6 full chain + papers; W239+ seat-chain queue-deepen per O-20261011-0012 sec.ii"
h["next_milestone"] = h["next"]
h["did"] = "r984: S0.5 3-order ack (O-0942/0948 bm-b knowledge-face; O-0949 bm-a receipt r980 already in order file) + D-19/ORD dual-delta TRUE consumed (DEC 47e3a8d0: D-20261013-01/02 + D-20261014-01..05 all zero BigMoney action rows; ORD 7d2f4acc: tail rows zero BigMoney) + S1 smoke 49/49 + W238 splice editor derived from W237 template (count-asserted ordered transform, 7 pattern fixes fail-closed) + splice LANDED + selftests green + commit 50fa77623 pushed verified (range line + ls-tree) + engine self-ignite tick verified (ignited:n1w238-3of12 pid=45020 -> 7/12 shards at closeout) + S6 41-leg chain detached pid 49968"
h["last_decisions_sha"] = "47e3a8d0a854284728feefc7b38a54e6ff275f056d3888da5a26214011ff7ee7"
h["last_decisions_seen"] = "r984: DEC dual-delta TRUE consumed (D-20261013-01/02 + D-20261014-01..05; zero BigMoney action rows: 04/05 = HQ-executed group Phase-1 law-slimming)"
h["last_decisions_at"] = iso
h["last_decisions_read_at"] = iso
h["last_decisions_ts"] = iso
h["last_orders_sha"] = "7d2f4accf36cd0cbd6b7464a7ac802d6997fe7fd86c2a346a71365e1d36e88b9"
h["last_orders_seen"] = "r984: ORD dual-delta TRUE consumed (tail rows 10-14 11:0x..12:2x all non-BigMoney: MV production / bm-b lane / bm-c GPU lane / CEO proxy seat / law-slimming)"
h["last_orders_at"] = iso
h["last_orders_read_at"] = iso
h["last_orders_ts"] = iso
ack = h.get("orders_ack") or []
for o in ("O-20261014-0942-bm-b.md", "O-20261014-0948-bm-b.md", "O-20261014-0949-bm-b.md"):
    if o not in ack:
        ack.append(o)
h["orders_ack"] = ack
h["orders_ack_note"] = "r984: 3-order ack (0942/0948 knowledge-face bm-b machine orders; 0949 fleet-wide fill-order -- bm-a receipt already recorded in order file by r980 same-window, orders_ack caught up this round)"
h["idle_rounds"] = 0
h["agenda_starved"] = False
h["orphan_face"] = 0
h["orphan_faces"] = 0
h["orphan_killed"] = 0
h["verdict"] = "green (red=false lane=healthy; engine ALIVE ignited:n1w238 burn in flight 7/12 at closeout; W238 splice 50fa77623 on origin; S6 chain detached pid 49968)"
h["last_round_ts"] = iso
json.dump(h, open(hp, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

# verify epoch int type
h2 = json.load(open(hp, encoding="utf-8"))
assert isinstance(h2["heartbeat_epoch_utc"], int), "epoch must be JSON int"

# --- round report append ---
rp = os.path.join(REPO, "round_reports-bm-a.md")
line = (f"{iso} | r984 | S0.5 3令ack(0942/0948知会面+0949回执r980已落令内) + DEC/ORD双delta TRUE消费(47e3a8d0/7d2f4acc·"
        f"新行D-20261013-01/02+D-20261014-01..05全零BigMoney行动面=水位键更新零动作) + S1 smoke 49/49 PASS + "
        f"S3主使命W238五面冻结拼接LANDED：派生脚本_w238bma_derive_editor.py从W237模板计数断言有序变换(7处pattern修复fail-closed法)"
        f"→拼接编辑器_w238bma_freeze_edits.py跑通→pf selftest 9/9+n1 selftest PASS→commit 50fa77623推送验达(range行+ls-tree双件+未达0)"
        f"→引擎tick自燃ignited:n1w238-3of12 pid45020→closeout时7/12分片+队列4 | 证据=freeze receipt _w238bma_freeze_receipt.json"
        f"(bands A538_404..540_403/B540_404..540_603·staircase 98th·upstream W237 945,189/K519,320锚全过·gate0.5 owner rows 227/"
        f"bma 121=122nd EXACT) | 下轮指针=W238烧毕12/12→PRE-FINALIZE六门(standing law)→finalize one-pass(窗≤48h)+S6链产物absorb+bars 15:30全链\n")
with open(rp, "a", encoding="utf-8") as f:
    f.write(line)
print("CLOSEOUT OK: state round_no=984, heartbeat epoch=%d (int verified), orders_ack=%d, round report appended" % (epoch, len(ack)))
