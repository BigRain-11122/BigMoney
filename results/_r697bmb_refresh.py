# r697 bm-b final refresh: post-push fleet-state evolution (N2 12/12 + finalize
# seat bm-a + CONTEST claimed by bm-a) -> heartbeat/state honest update +
# MSG-2215 processed move. -*- coding: utf-8 -*-
import json
import os
import shutil
import time
from datetime import datetime, timezone, timedelta

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
STATE = ROOT + r"\state.json"
HB = ROOT + r"\fleet\machines\bm-b.json"
MSG = ROOT + r"\fleet\inbox\MSG-2026-10-04-2215-bma-ALL.md"
PROCD = ROOT + r"\fleet\inbox\processed"

tz = timezone(timedelta(hours=8))
clock = datetime.now(tz).strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())

hb = json.load(open(HB, encoding="utf-8"))
hb["last_seen"] = clock
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = clock
hb["ts"] = clock
hb["updated"] = clock
hb["updated_at"] = clock
hb["current_task"] = ("r697 closed+DELIVERED (a8e55882d): holiday maintenance round; N2-W15 12/12 done in "
                      "window (my SHARD-2 in flight, finalize seat=bm-a MSG-2215), CONTEST-RC claimed by "
                      "bm-a 22:12:07 (its RAM window open, B-plan staging served); next = 10-05 morning "
                      "W3 judge landing watch (bm-c seat ETA ~02:00) + N2-W15 judge-stage prereg drafting "
                      "window (per MSG-2215: next healthy-machine round) + trio V/Q/D closes 10-06..08")
hb["verdict"] = ("healthy burning (trio NULLS three-family in flight RAM-held to 10-06T17 + N2-W15 SHARD-2 "
                 "in flight; N2 screen-finalize bm-a seat; CONTEST-RC bm-a claimed; W3 judge bm-c in flight; "
                 "py_low_with_work_cands = legal RAM-gated window per r691 cap law)")
json.dump(hb, open(HB, "w", encoding="utf-8"), ensure_ascii=True, indent=1)

st = json.load(open(STATE, encoding="utf-8"))
st["next"] = ("(a) 10-05 morning round: W3 judge landing watch (bm-c respawn pid 26052 ETA ~02:00, bm-c seat, "
              "verify chain _r487bmc_w3_judge_verify.py); (b) N2-W15 judge-stage prereg drafting window = next "
              "healthy-machine round (bm-a MSG-2215 declares screen-finalize seat, judge not claimed); "
              "(c) trio NULLS V close ~10-06T17 / Q 10-07T11 / D 10-08T0x -> RAM window -> remaining local "
              "queue; (d) CONTEST-RC burn watch (bm-a claimed 22:12:07, anchor+mirror phases); "
              "(e) update_lhb min-interval retry re-verify next round; (f) 10-09 post-holiday data-chain check")
st["last_seen"] = clock
st["ts"] = clock
st["updated"] = clock
st["last_round_at"] = clock
st["clock_read"] = clock
st["note"] = ("r697: holiday maintenance round; two claw catches (local-behind x2, r648 heal zero --no-verify) "
              "+ 18-UU S6 same-window merge resolved (ts-newer-wins ours-fresh + twins locked + token union); "
              "DELIVERED a8e55882d; N2-W15 12/12 done + CONTEST-RC bm-a claim absorbed same window")
json.dump(st, open(STATE, "w", encoding="utf-8"), ensure_ascii=True, indent=1)

if os.path.exists(MSG):
    shutil.move(MSG, os.path.join(PROCD, os.path.basename(MSG)))

# self-verify
h2 = json.loads(open(HB, encoding="utf-8").read())
assert isinstance(h2["heartbeat_epoch_utc"], int)
json.loads(open(STATE, encoding="utf-8").read())
assert not os.path.exists(MSG)
print("OK r697 final refresh clock=%s epoch=%d msg_moved=1" % (clock, epoch))
