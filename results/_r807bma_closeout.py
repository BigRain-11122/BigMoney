# -*- coding: utf-8 -*-
"""r807 bm-a closeout writer: state advance + heartbeat + RR line
(single-file fresh-read-modify-write per r109 targeted-commit law;
heartbeat epoch = python int(time.time()) per R170/R178; clock_read
T-separated per R262)."""
import json
import time
from datetime import datetime, timezone, timedelta

tz = timezone(timedelta(hours=8))
now = datetime.now(tz)
iso = now.isoformat(timespec="seconds")
epoch = int(time.time())

# --- state-bm-a.json ---------------------------------------------------------
sp = "state-bm-a.json"
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = 807
st["round"] = 807
st["loop_round"] = 807
st["last_round"] = 806
st["last_round_at"] = iso
st["last_round_ts"] = iso
st["last_run"] = iso
st["last_seen"] = iso
st["updated"] = iso
st["ts"] = iso
st["clock_read"] = iso
st["heartbeat_epoch_utc"] = epoch
st["last_heartbeat_epoch_utc"] = st.get("heartbeat_epoch_utc", epoch)
st["current_task"] = ("r808: W168 freeze half-window CONTINUATION: face probe "
                      "(_r807bma_w168_dump_faces.py head face already on disk; full probe "
                      "adapt r803 pattern) -> freeze edits 5-face (pf N1_BANDS[168] row A "
                      "384_404..386_403 staircase 27th E36 + n1 WAVE_CONFIGS[168] entry B "
                      "386_404..386_603 own-A leg2 + materializer 138..167 refresh + @CLMS@ "
                      "r807 attribution; TOK map adapt r805 W167->W168 with f61835690 "
                      "registered-row pairing) -> freeze_verify 8 legs -> freeze commit push "
                      "-> 2-tick ignite verify (r535 law) -> W168 finalize next window "
                      "(proj ledger 775,012 / K 367,520)")
st["did"] = ("r807 W168 prereg build one-window landed (xform W167->W168, banned gate ADMIT "
             "rc0, 46 needle assertions, pushed 32420fe9d rebased onto 62bc99927): S0 triple "
             "churn-absorb race loop resolved (daemon live-face ticks) + rebase clean x2 + "
             "S0.5 orders 163/163 double-sweep zero unacked + dual watermark moved and "
             "consumed (dec 635c3024->acc32216 D-20261007-01/02/03 zero new BigMoney dispatch; "
             "ord 9be6a74f->858d46c3 token row committee-domain) + D-20261002-06 main-file "
             "criterion MET at 27,396B (bm-c r651 mini-split adopted via rebase, headroom "
             "3,324B) + S1 smoke 48/48 + S2 boards zero open + S3 saturation engine alive "
             "idle + S6 38/38 rc0 128s + S7 four-piece green (loop pin=8 no-op first-fire "
             "04:08 + watchdog re-registered + both claws reinstalled + attrition CLEAN)")
st["last_action"] = "r807: W168 prereg build landed+pushed; freeze edits continuation"
st["next"] = ("r808 = W168 freeze edits 5-face (prereg on origin; gate _r806bma_w168_band_gate "
              "ADMIT + probe receipt + seat ceaf58908 all in-repo facts-source) -> dual "
              "selftest -> freeze commit push -> 2-tick ignite verify; then W168 finalize "
              "(proj ledger 775,012 / K 367,520); 10-07 12:00 D-06 closeout window")
st["notes"] = ("r807 = first session of the 03:4x-04:2x window (dead-r807-resolver forensics "
               "absorbed pre-pull; the 18-UU rebase it was built for never materialized -- "
               "current-window rebase resolved clean x2 with zero UU); W168 seat+probe+gate "
               "all landed by r806; prereg by r807; freeze edits = r808 continuation per "
               "two-session law (r797/r799) + 25min wrapper budget law")
st["last_decisions_sha"] = "acc322169eaa759a6ea34c65be35aa7eed7ea9b96dc0895dc7f4f682becdf2fd"
st["last_decisions_at"] = iso
st["last_decisions_ts"] = iso
st["last_decisions_src"] = ("group-tree origin blob (C:/Users/sjs20/Desktop/FluxGroup git show "
                            "origin/main:docs/decisions.md, r786 law; python sha256 raw bytes)")
st["last_decisions_seen"] = "2026-10-07"
st["last_orders_sha"] = "858d46c3587fda1726a3bbd5275e70e7d6af48391fbcafe04d78bc6a37bd4ea1"
st["last_orders_at"] = iso
st["latest_artifact"] = "research/PERPETUAL_N1_W168_PREREG.md @" + iso
st["verify"] = ("smoke 48/48; banned gate rc0; orders 163/163 double-sweep; decisions "
                "acc32216 + orders 858d46c3 watermarks synced; W168 prereg push delivered "
                "(62bc99927 fetch ahead0); heartbeat epoch int + clock T-sep self-checked")
json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(sp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"

# --- heartbeat fleet/machines/bm-a.json ---------------------------------------
hp = "fleet/machines/bm-a.json"
hb = json.load(open(hp, encoding="utf-8"))
hb["last_seen"] = iso
hb["ts"] = iso
hb["clock_read"] = iso
hb["heartbeat_epoch_utc"] = epoch
hb["current_task"] = st["current_task"]
hb["verdict"] = "alive: r807 W168 prereg landed (banned gate ADMIT); freeze edits next window"
hb["orders_ack"] = hb.get("orders_ack", [])
json.dump(hb, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
print("state + heartbeat written; epoch", epoch, "iso", iso)
