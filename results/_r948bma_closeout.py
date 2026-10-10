"""r948 bm-a closeout: state + heartbeat refresh (script-driven, load-modify-write
per r818 heartbeat law; fresh read, field-level update, no whole-file retype)."""
import datetime as dt
import json
import os
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
now_iso = dt.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())

# --- state-bm-a.json: round 947 -> 948
sp = os.path.join(ROOT, "state-bm-a.json")
s = json.load(open(sp, encoding="utf-8"))
s["round_no"] = 948
s["last_round"] = 947
s["last_round_at"] = now_iso
s["last_round_closed"] = now_iso
s["clock_read"] = now_iso
s["heartbeat_epoch_utc"] = epoch
s["last_heartbeat_epoch_utc"] = s.get("heartbeat_epoch_utc", epoch)
s["current_task"] = ("r948: E4 OMO liquidity face probe closed (P3 head consumed; primary OMO daily-ops feed "
                     "source-unreached = data-debt; monthly policy face + daily response faces buildable; "
                     "REPO_PANEL linkage quantified) + W205 watch (W204 bm-c seat not yet frozen)")
s["did"] = ("r948: E4 probe scripts/omo_liquidity_probe.py (selftest 7/7, 6 faces 8 requests) + evidence "
            "results/shortline/omo_liquidity_probe.json + digest DIGEST-20261010-omo-liquidity-face.md + queue "
            "consumption line; S0 14-UU rebase take-newer-by-ts canon-resolved onto bm-b r824")
s["last_action"] = "r948 closeout: E4 P3-queue head consumed (probe+digest+queue line)"
s["last_artifact"] = ("research/digests/DIGEST-20261010-omo-liquidity-face.md + "
                      "results/shortline/omo_liquidity_probe.json (09:2x)")
s["idle_rounds"] = 0
s["agenda_starved"] = False
s["last_orders_seen"] = "r948 scan zero unacked (60 files vs 199 ack, ORD 0ddb01d9 unchanged)"
s["last_decisions_seen"] = "D-20261010-01/02/03 hash b87a92b1 MATCH r945-r948 scans; zero new BigMoney dispatch"
s["last_orders_at"] = dt.date.today().isoformat()
s["last_decisions_at"] = dt.date.today().isoformat()
with open(sp, "w", encoding="utf-8", newline="") as f:
    json.dump(s, f, ensure_ascii=False, indent=1)
print("state round_no ->", s["round_no"])

# --- heartbeat fleet/machines/bm-a.json: field-level refresh
hp = os.path.join(ROOT, "fleet", "machines", "bm-a.json")
h = json.load(open(hp, encoding="utf-8"))
h["last_seen"] = now_iso
h["ts"] = now_iso
h["clock_read"] = now_iso
h["heartbeat_epoch_utc"] = epoch
h["round_no"] = 948
h["round"] = 948
h["loop_round"] = 948
h["last_round"] = 947
h["last_round_at"] = now_iso
h["verdict"] = "GREEN-IDLE worked-clear (E4 probe product round)"
h["idle_rounds"] = 0
h["agenda_starved"] = False
h["current"] = ("r948: E4 OMO liquidity face probe closed (P3 head consumed) + W205 watch "
                "(W204 bm-c seat not yet frozen, structural wait) + B-pool awaits bm-c jsl scanner >=10-16")
h["task"] = h["current"]
h["now_active"] = h["current"]
h["last_action"] = "r948 closeout: E4 P3-queue head consumed (probe+digest+queue line)"
h["last_artifact"] = ("research/digests/DIGEST-20261010-omo-liquidity-face.md + "
                      "results/shortline/omo_liquidity_probe.json (09:2x)")
h["latest_artifact"] = h["last_artifact"]
h["recent_artifact"] = h["last_artifact"]
h["next"] = ("r949: bm-c W204 first-burn watch -> bm-a W205 seat chain; E6 P3 head (micro-cap factor "
             "external scan) 48h cadence; PARKING-P1 closed; month-exam 10-31 (T-143 assembly 10-29)")
h["next_milestone"] = h["next"]
h["notes"] = ("r948: E4 verdict = OMO daily net-injection ops feed source-unreached (EM reportName unknown, "
              "3 candidates honestly excluded) BUT liquidity composite face buildable: monthly PBOC balance "
              "sheet (33y, alive to 2026.8) + daily FDR001 fixing (>=2020 via year-chunked chinamoney FrrHis; "
              "wide-span trap disclosed) + Shibor 11.5y; REPO_PANEL linkage quantified (month-end +1.07pp; "
              "exchange-vs-bank spread 2020 +67.9bp vs current -6.5bp regime flip)")
with open(hp, "w", encoding="utf-8", newline="") as f:
    json.dump(h, f, ensure_ascii=False, indent=1)

# epoch int self-verify
h2 = json.load(open(hp, encoding="utf-8"))
assert isinstance(h2["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in h2["clock_read"], "clock_read must be T-separated"
print("heartbeat refreshed, epoch int verified:", h2["heartbeat_epoch_utc"])
