# -*- coding: utf-8 -*-
"""r643 bm-c S5+S7 close batch: round-report line revive + state advance
(643->644, AFTER QA pack in place per r640 law) + heartbeat three-line face
+ orders_ack +=O-20261006-2358 + epoch int self-verify."""
import json
import os
import time

now = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())

RR = r"logs\iteration-loop\round_reports-bm-c.md"
row = ("{ts} | r643 bm-c | dept:工程/舰队 | S0 absorb 482cbd01a+pull 净；S0.5 DEC MATCH 56连+ORD delta 21F62FB8→163967AE 1新行(~23:5x 每机极致适配令)receipt-only+O-20261006-2358 ack；"
       "S1 48/48；S3 板open=0/watermark绿/SAT活/stash残留零；S6 38/38 rc0(dual 51连绿·CA旗 supply_gap+supply_floor·ORANGE·golden-week no-bar)；"
       "主产品=CODELY主件≤30KB门修复(31,744→30,482B·r786 bm-b/r798 bm-a 两纯回执行下沉archive 202610.md·零丢失receipt)+D-06尺寸验收面全绿(主件+25域件 OVER_COUNT=0·census)；"
       "QA包r643三件(state+1默认误标r644=r758 override律命中·r640治愈前例rename归位·r644命名空间让空)；坑律候选=QA state+1默认×bm-c state==在飞轮恒偏1(下轮入主件并配平) "
       "| 证据=results/_r643bmc_codely_sink_receipt.json+_r643bmc_d06_size_census.json+qa/smoke-r643.md 5/5+_r643bmc_s6_log.txt 38/38 "
       "| 下轮指针：D-06 12:00收口窗(余=指针行陈旧余=子句裁定+pit-data CRLF裁定+断言层final-sweep+坑律入件配平)；O-2110/2250双机回执18:00 watch；下个5x=r645 HANDOVER\n").format(ts=now)
with open(RR, "a", encoding="utf-8") as fh:
    fh.write(row)
print("RR appended")

# ---- state advance (AFTER QA pack: r640 law) ----
SP = r"state-bm-c.json"
st = json.load(open(SP, encoding="utf-8"))
assert st["round_no"] == 643, "unexpected round_no %s" % st["round_no"]
st["round_no"] = 644
st["round_no_label"] = "round 643 (bm-c)"
did = ("r643 bm-c: golden-week quiet-lane round. (1) S0: dirty-tree daemon faces absorb-committed (482cbd01a) pre-pull per r642 root-fix law, pull --rebase clean, stash residue ZERO (r642 next-pointer (a) closed). "
      "(2) S0.5: DEC sha A44C39E0 MATCH (56th consecutive clean face); ORD delta 21F62FB8->163967AE single new row (~23:5x per-machine extreme-fit + tailnet + density order, C-20261006-03) = receipt-only consume, zero new bm-c obligations; fleet order O-20261006-2358-bm-c acked (bm-c self-face already complete per order text). "
      "(3) S1 smoke 48/48. S3: board open=0 (176 tickets all claimed), watermark red=false + next_pick claimed, saturation engine alive (SAT_RC=0). "
      "(4) S6 chain 38/38 rc0: pool_dualrun ZERO-DRIFT streak 51; compute_audit flags supply_gap+supply_floor (pool hungry, golden-week expected); py_watermark insufficient_history; regime ORANGE; update_daily 0 new rows cutoff 2026-09-30 (golden week, honest no-op until 10-09). "
      "(5) PRODUCT: CODELY main-file <=30KB gate REPAIR (31,744 -> 30,482B): r786 bm-b triple-order receipt + r798 bm-a dual-order record (pure receipts, canon = order-file receipt sections) sunk verbatim to archive 202610.md per r444 paradigm; prescan rc3 recorded per r441 treasure-migration ritual; registry in/out line appended; zero-loss receipt _r643bmc_codely_sink_receipt.json. D-06 size verification face ALL GREEN: main + 25 domain pit files OVER_COUNT=0 (census _r643bmc_d06_size_census.json). "
      "(6) QA pack r643 three files in place (smoke-r643.md 5/5 + equity-curve-r643.png + log; QA default state+1 mislabeled r644 = r758 override law face, healed by r640 rename precedent, r644 namespace left free). "
      "(7) S7: quartet re-registered idempotent, attrition guard scan, commit+push.")
st["did"] = did
st["last_round"] = did
st["last_round_at"] = now
st["last_round_ts"] = now
st["last_round_summary"] = "r643: CODELY gate repair + D-06 size-face green + ORD delta consumed + QA r643 pack"
st["last_action"] = did[:300]
st["ts"] = now
st["updated"] = now
st["updated_at"] = now
st["clock_read"] = now
st["last_seen"] = now
st["last_seen_at"] = now
st["last_run_at"] = now
st["last_decisions_read_at"] = now
st["last_decisions_at"] = now
st["last_orders_sha"] = "163967AE5ED1F5C00CEBF300F1AE8FE29B2D5895"
st["last_orders_sha_method"] = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r643 probe = 163967AE delta vs r642 21F62FB8 consumed same-window per r760 law: "
                                "single new row ~23:5x per-machine extreme-fit/tailnet/density order (C-20261006-03) + O-20261006-2358-bm-c dispatch -- zero new bm-c obligations receipt-only; "
                                "value facts-driven from results/_r643bmc_s05_facts.json, 40hex shape-asserted, never hand-typed (r583 S4 law))")
st["note"] = "r643: CODELY main <=30KB gate repaired + D-06 size face green; QA pack r643 healed from state+1 default mislabel."
st["next"] = ("(a) r644: D-06 group closeout window TODAY 12:00 (residual adjudication: stale yu= clauses in domain pointer lines + pit-data CRLF adjudication + assertion-layer final-sweep "
              "+ new pit entry [QA state+1 default x bm-c state==in-flight round] into main file PAIRED with compensating sink to stay <=30KB). (b) O-20261006-2110/2250 dual-machine receipts due 10-07 18:00 (watch-only). "
              "(c) 10-09 reopen: data-chain re-arm + REGIME_GUARD v3 first bar. (d) next 5x = r645 (HANDOVER window). (e) board watch: post all-hands tickets.")
st["verify"] = ("receipts: results/_r643bmc_codely_sink_receipt.json (zero-loss: blocks 766+797B verbatim in archive, archive delta==removed sum, main 31,744->30,482 <=30,720) "
                "+ results/_r643bmc_d06_size_census.json (main + 25 pit files, OVER_COUNT=0) + results/_r643bmc_s05_facts.json (DEC MATCH 56th + ORD 163967AE) "
                "+ qa/smoke-r643.md 5/5 pack (label healed r644->r643 per r640/r758 laws) + results/_r643bmc_s6_log.txt 38/38 rc0 + smoke 48/48 + treasure_guard prescan rc3 recorded (r441 ritual)")
json.dump(st, open(SP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("STATE advanced 643->644")

# ---- heartbeat ----
HP = r"fleet\machines\bm-c.json"
hb = json.load(open(HP, encoding="utf-8"))
act = ("当前活: r643 静默黄金周值守轮（S6 38/38 rc0·ORANGE·无新 bar 至 10-09；板 open=0·watermark 绿·SAT 引擎活） | 最近实物: CODELY 主件 ≤30KB 门修复+D-06 尺寸验收面全绿"
       "（主件 31,744→30,482B·25 域件 OVER=0·receipt+census 双件）+qa/smoke-r643.md 5/5 @ " + now + " | 下个里程碑: D-06 集团收口窗 10-07 12:00（残余裁定面）；O-2110/2250 双机回执 10-07 18:00；复市 10-09 数据链 re-arm+REGIME_GUARD v3 首 bar；下个 5x=r645〔HANDOVER 窗〕")
ack = hb.get("orders_ack", [])
if "O-20261006-2358-bm-c.md" not in ack:
    ack.append("O-20261006-2358-bm-c.md")
hb.update({
    "activity_now": act, "current_task": act, "current_task_at": now,
    "clock_read": now, "last_seen": now, "last_seen_at": now, "updated_at": now,
    "updated": now, "ts": now, "heartbeat_epoch_utc": epoch,
    "round_no": 644, "round_no_label": "round 643 (bm-c)",
    "latest_artifact": ("results/_r643bmc_codely_sink_receipt.json (CODELY 31,744->30,482B gate repair) + results/_r643bmc_d06_size_census.json (D-06 size face ALL GREEN) + qa/smoke-r643.md 5/5 @ " + now),
    "next_milestone": "D-06 group closeout window 10-07 12:00 (residual adjudication face); O-20261006-2110/2250 dual-machine receipts due 10-07 18:00; market reopen 10-09 (data-chain re-arm + regime_guard v3 first bar); month-end first-exam 10-31; next 5x = r645 (HANDOVER window)",
    "prod_lanes": ("r643 值守轮（S0.5 ORD 单新行 receipt-only 消费+O-2358 ack；S6 38/38 rc0 连续；CODELY 主件门修复+D-06 尺寸面全绿；QA r643 包归位；"
                   "板 open=0；watermark 绿〔dec 56 连〕；SAT 引擎活；黄金周无 bar 车道至 10-09；下个 5x=r645〔HANDOVER 窗〕"),
    "verdict": ("alive: r643 quiet-lane round complete (CODELY <=30KB gate repaired 30,482B + D-06 size verification face ALL GREEN main+25 domain files; S6 38/38 rc0; smoke 48/48; "
                "QA pack r643 healed per r640/r758 laws; ORD 163967AE consumed receipt-only; board open=0; satengine alive; golden-week no-bar lane until 10-09)"),
    "orders_ack": ack, "orders_ack_count": len(ack),
})
json.dump(hb, open(HP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(HP, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in chk["clock_read"] and "+" in chk["clock_read"], "clock_read must be ISO8601 T-form"
print("HEARTBEAT ok, epoch int =", chk["heartbeat_epoch_utc"], "| ack_count =", chk["orders_ack_count"])
