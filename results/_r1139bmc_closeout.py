# -*- coding: utf-8 -*-
# bm-c r1139 closeout: state counter advance + heartbeat + round report row.
import json, os, subprocess, time
from datetime import datetime, timezone, timedelta

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
now = datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=8)))
ts = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())

head = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"], capture_output=True).stdout.decode().strip()

sp = os.path.join(REPO, "state-bm-c.json")
s = json.load(open(sp, encoding="utf-8"))
prev = s["round_no"]
s["round_no"] = prev + 1
s["ts"] = ts
s["updated"] = ts
s["updated_at"] = ts
s["verdict"] = ("green r1139 product window: W282 CYCLE COMPLETE (sixgate 45th ALL PASS / finalize "
                "1,044,735 / K 618,320 EXACT / fivekeys 6/6 / sec.7+8 backfilled)")
s["recent_artifact"] = "results/perpetual_faces/n1_w282_results.json"
s["last_artifact"] = "results/perpetual_faces/n1_w282_results.json"
s["sync"] = {"origin_tip": head, "ts": ts}
s["verify"] = ("sixgate ALL PASS 45th | finalize ledger 1,044,735 K 618,320 exact | fivekeys 6/6 | "
               "smoke 49/49 | satengine rc0 burns=[] queue=[] | S6 10/10 rc0 | attrition 4 CLEAN | "
               "orphan face=0 | S0.5 dual-delta FALSE both scans | local-not-origin commits=0")
s["r1139_closeout_note"] = (
    "r1139: (1) S0-1 anchor bm-c + round-zero probe py_faces=4 orphans=0 zero-kill; S0 fetch clean (no rebase owed at open); "
    "(2) S0.5 dual-delta FALSE both scans (ord 6cec19c3 / dec d5336c87 hold per state keys; unacked=0, 232 acks; "
    "inbox MSG-0415-bmb-bma + MSG-2351-bmb both addressed @bm-a, left in place); (3) S1 smoke 49/49; "
    "(4) PRODUCT = W282 CYCLE COMPLETE: sixgate 45th consecutive PRE-FINALIZE ALL PASS "
    "(results/_r1139bmc_w282_sixgate.json -- splice 01fe28eec2 CR-normalized worktree==landed blob, setwave 282:1/281:1/280:1 "
    "segment-scoped birth-station gates, shards 12/12 all >100KB, banned ADMIT rc0, pf/n1 selftest rc0, seed_admit FREE x2) "
    "-> finalize one-pass EXACT ledger 1,042,535+2,200=1,044,735 / K 616,120+2,200=618,320 (merged mu -0.09281590, "
    "sigma 0.24506546, se_mu 0.000312) -> fivekeys 6/6 PASS (results/_r1139bmc_w282_fivekeys.json; key3 A p95 0.3228->0.3075, "
    "key4 K-lift +0.0000, n_eff held 1,042,535) -> prereg sec.7/8 placeholders backfilled machine-read (zero transcription); "
    "(5) S6 light 10/10 rc0 (dualrun ZERO-DRIFT streak 51; watermark loaded_ok py 17.2% window avg 44.2%; update_daily no-op "
    "bars_present=false; regime/clock/fund_premium/b_layer/report/token rc0, token delta=0); (6) S7: attrition 4 CLEAN "
    "(3 historical heals noted); pin=5 no-op; watchdog re-registered (S4U flip access-denied -> default principal, exact same "
    "regression face as r1138, elevation needed); both claws reinstalled MATCH; (7) same-window PIT: sixgate subprocess "
    "text=True under GBK console threw reader-thread UnicodeDecodeError on child stderr byte 0xa0 -- verdict unaffected but "
    "evidence tails were empty; healed by explicit encoding='utf-8', errors='replace' (results/_r1139bmc_patch_sixgate_enc.py) "
    "and re-ran to clean tails -- pit-encoding family, generalize to every new subprocess text capture"
)

json.dump(s, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

hp = os.path.join(REPO, "fleet", "machines", "bm-c.json")
h = json.load(open(hp, encoding="utf-8"))
h["last_seen"] = ts
h["ts"] = ts
h["clock_read"] = ts
h["heartbeat_epoch_utc"] = epoch
h["current_task"] = "W282 cycle complete; engine idle (burns=[] queue=[]); next seat W283"
h["verdict"] = "green: W282 finalize one-pass exact (ledger 1,044,735 / K 618,320)"
h["cpu_cores"] = 32
h["ram_free_gb"] = 3.32
h["gpu_free_vram_gb"] = 13.76
h["idle_rounds"] = 0
h["agenda_starved"] = False
h["did"] = ("W282 sixgate 45th ALL PASS + finalize one-pass 1,044,735/618,320 EXACT + fivekeys 6/6 + prereg sec.7/8 backfill")
h["next"] = "r1140 = W283 SEAT (probe ADMIT on post-W282 271+2-owner universe, naive A 637_701 refused by registered W282 B; must re-derive)"
json.dump(h, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

row = (
    f"{ts} | r1139 | P0=W282 CYCLE COMPLETE: sixgate 45th consecutive PRE-FINALIZE ALL PASS "
    f"(results/_r1139bmc_w282_sixgate.json; splice 01fe28eec2 CR-normalized identity, setwave 282/281/280 segment gates, "
    f"shards 12/12 >100KB, banned ADMIT rc0, pf/n1 selftest rc0, seed_admit FREE x2) -> finalize one-pass "
    f"**ledger 1,044,735 / K=618,320 EXACT** (merged mu -0.09281590 sigma 0.24506546 se_mu 0.000312) -> fivekeys **6/6 ALL PASS** "
    f"(key3 A p95 0.3228->0.3075 / key4 K-lift +0.0000 / n_eff held 1,042,535) -> prereg sec.7/8 machine-read backfill "
    f"(placeholders zero-transcription) | verify: smoke 49/49, satengine rc0, S6 10/10 rc0 (dualrun streak 51 drift=false), "
    f"attrition 4 CLEAN, orphan face=0, push delivered 8b5730bec4 behind=0, local-not-origin=0 | "
    f"current=W282 cycle closed, engine idle | 最近实物=results/perpetual_faces/n1_w282_results.json ({ts}) | "
    f"next=r1140 W283 SEAT probe (post-W282 universe re-derive; naive A 637_701 refused by registered W282 B) <=48h"
)
with open(os.path.join(REPO, "round_reports-bm-c.md"), "a", encoding="utf-8", newline="") as f:
    f.write(row + "\n")

assert isinstance(h["heartbeat_epoch_utc"], int)
print("state round_no", prev, "->", s["round_no"], "| heartbeat epoch", epoch, "| report row appended")