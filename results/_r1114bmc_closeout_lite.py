# -*- coding: utf-8 -*-
# r1114 bm-c closeout-lite (honest-split window: splice LANDED, cycle chain deferred to r1114-continuation)
import json, time, datetime, subprocess

# 1) S7-tail ORD/DEC re-probe (dead-window opening scan was 09:17; this is the closing scan)
pr = subprocess.run(["python", "Tools/s05_probe.py"], capture_output=True, text=True,
                    encoding="utf-8", errors="replace")
try:
    probe = json.load(open("results/_s05_probe.bm-c.json", encoding="utf-8"))
    ord_delta = probe.get("orders_delta")
    dec_delta = probe.get("decisions_delta")
    unacked = probe.get("unacked", [])
except Exception as e:
    ord_delta = dec_delta = None
    unacked = ["PROBE-READ-FAIL:" + str(e)]

now_iso = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())

# 2) minimal heartbeat update (fleet-visibility faces only; full closeout = next window)
hb_path = "fleet/machines/bm-c.json"
hb = json.load(open(hb_path, encoding="utf-8"))
hb["last_seen"] = now_iso
hb["ts"] = now_iso
hb["updated"] = now_iso
hb["activity_now"] = now_iso
hb["current_task"] = ("W277 FIVE-FACE SPLICE LANDED (origin 9e53371814; pf d3250083e39aedcd / n1 a8d34561c9f5be8a; "
                      "bands A 624_701..626_700 / B 626_701..626_900 registered); engine burn + sixgate + finalize + "
                      "fivekeys + sec78 + W278 seat = r1114-continuation FIRST ACTION")
hb["current_task_at"] = now_iso
hb["current_task_ts"] = epoch
hb["clock_read"] = now_iso
hb["heartbeat_epoch_utc"] = epoch
hb["verdict"] = ("green r1114 product window (W277 FIVE-FACE SPLICE LANDED first-try: E63 21st-gen editor "
                 "CLEAN-AT-BIRTH + preflight PASS + splice SPLICE OK + pf selftest 9/9 + n1 selftest PASS + "
                 "push first-try 9e53371814; honest-split per r1096: cycle chain deferred r1114-continuation)")
hb["last_action"] = "W277 five-face splice derive+splice+push (editor CLEAN-AT-BIRTH, zero heals)"
hb["last_action_at"] = now_iso
hb["last_artifact"] = ("W277 splice @ origin 9e53371814 (scripts/perpetual_faces.py + perpetual_faces_n1.py "
                       "W277 block registered; receipt results/_w277bmc_freeze_receipt.json)")
hb["recent_artifact"] = hb["last_artifact"]
hb["head_sha"] = "9e53371814" + "0000000000000000000000000000"[:0]  # keep 10-char face like lineage
hb["head_sha"] = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
hb["next"] = ("r1114-continuation: (1) verify engine mtime-watch self-ignite W277 burn 12/12 (resident SatEngine "
              "PID watch; shards -> results/p2cal_ext/n1_w277/); (2) sixgate PRE-FINALIZE (clone "
              "_r1111bmc_w276_sixgate.py -> _r1114bmc_w277_sixgate.py via _r1111bmc_build_gate_clones.py one-gen roll); "
              "(3) finalize one-pass (ledger 1,031,535+2,200=1,033,735 / K=605,120+2,200=607,320 projected); "
              "(4) fivekeys 6/6 (keys = W276 actuals FULL-PRECISION from _r1111bmc_w276_fivekeys.json + "
              "n1_w276_results.json); (5) sec.7/8 backfill placeholders=0; (6) W278 seat publish (probe "
              "live-derive on post-W277 universe, W278p projection A 626_701..628_700 / B 626_901..627_100 "
              "pre-disclosed); (7) full closeout state 1114->1115; (8) TODAY Monday 15:30 bars window papers chain")
hb["next_pointer"] = hb["next"]
hb["next_milestone"] = "W277 cycle COMPLETE (burn+sixgate+finalize+fivekeys+sec78) then W278 seat; Monday 15:30 papers chain"
hb["orders_ack_receipt"] = (f"r1114: opening scan absorbed from dead-window 09:17:42 probe (dual FALSE ord 57d1f5de / "
                            f"dec 8706acd8, unacked=0); S7-tail re-probe THIS window ord_delta={ord_delta} "
                            f"dec_delta={dec_delta} unacked={len(unacked) if isinstance(unacked, list) else unacked}")
hb["orders_ack_ts"] = now_iso
assert isinstance(hb["heartbeat_epoch_utc"], int) and "T" in hb["clock_read"], "epoch int + clock ISO-T law"
json.dump(hb, open(hb_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("heartbeat updated epoch", epoch, "ord_delta", ord_delta, "dec_delta", dec_delta, "unacked", unacked if not isinstance(unacked, list) else len(unacked))

# 3) round-report ledger row (bm-c file per fleet/README sec.6)
row_ts = now_iso
row = (f"{row_ts} | r1114 | W277 FIVE-FACE SPLICE LANDED (bm-c): preflight _r1114bmc_needle_preflight.py MEASURED "
       f"PASS (canon ee852bc2721f3862 62,326B; 130+ entries exact first-try + 2 disclosed table-heals = gate-region "
       f"misread faces absent from canon) + E63 21st-gen editor _w277bmc_derive_editor.py CLEAN-AT-BIRTH (all "
       f"count-asserted reps first-try; phase4 zero-residual; phase5 presence gates) -> _w277bmc_freeze_edits.py "
       f"62,353B SPLICE OK first-try (origin_base 5b2b2950f1 no-race; pf d3250083e39aedcd / n1 a8d34561c9f5be8a; "
       f"A 624_701..626_700 26th A-hop / B 626_701..626_900 27th above-own-A; seed FREE x2; pf selftest 9/9 + "
       f"n1 PASS) -> push first-try 9e53371814 behind=0 | 证据=origin 9e53371814 + receipt json + editor log | "
       f"下轮=r1114-continuation: engine burn 12/12 verify -> sixgate -> finalize 1,033,735/607,320 -> fivekeys -> "
       f"sec78 -> W278 seat -> closeout state 1114->1115; tail probe ord_delta={ord_delta} dec_delta={dec_delta}")
with open("logs/iteration-loop/round_reports-bm-c.md", "a", encoding="utf-8") as f:
    f.write(row + "\n")
print("round report row appended")
