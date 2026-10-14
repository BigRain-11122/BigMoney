# r935 bm-b closeout: state.json + heartbeat update (JSON round-trip, key-preserve)
import json, io, time
from datetime import datetime, timezone, timedelta

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
CST = timezone(timedelta(hours=8))
now = datetime.now(CST)
iso = now.isoformat(timespec="seconds")
epoch = int(time.time())

# --- state.json ---
sp = ROOT + r"\state.json"
s = json.load(io.open(sp, encoding="utf-8"))
s["round_no"] = 935
s["round"] = 935
s["round_no_label"] = "r935"
s["clock_read"] = iso
s["ts"] = iso
s["updated"] = iso
s["updated_at"] = iso
s["last_seen"] = iso
s["last_round_at"] = iso
s["last_round_ts"] = iso
s["last_action_at"] = iso
s["last_action"] = "r935: W19 judge-finalize landed whole-package closeout -- landing verify (PID 17108 exited 13:49:47, products 3/3) + s4 intake lawful-zero (n_eligible 0) + products commit 223720adb push 42b6f6111 (48h CEO clock started 13:49, due 10-16) + prereg sec.7/8 backfilled (6/6 prediction HIT, four-wave calibration best) + attrition dual rows (SCREEN 546 / JUDGE 112, guard CLEAN) + TREASURE row + METHODOLOGY E66 (three-wave determinism cross-gate) + S6 chain 41/41 green (dualrun streak 20)"
s["did"] = "r935 bm-b (W19 landing closeout round): (1) S0 rebase-first lesson: push blocked by pre-push claw on stale base (behind 4 = bm-a/bm-c commits) -> bookkeeping commit + pull --rebase + push landed 42b6f6111 behind=0; (2) S0.5 orders 0 unacked (88/213 CLEAN); D-19 dual-watermark EQUAL zero-action (dec d9d8aa72 ord 179ac0f4); (3) S1 smoke 49/49; SatEngine alive idle; orphan probe 0 (py_faces=13); (4) W19 whole-package: n_judged 112, G1 0, G2-v2 0, eligible_reform 0, onboard 0 (lawful-zero), E[FP]=5.6 vs 0, paired deltas daily +0.0942 p=0.01 / weekly -0.2808 p=0.358, zvx 8; three-axis X/S/T adjudication CLOSED (future GENERATE = entry x filter only); (5) S6 41/41 rc0 96.7s: dualrun streak 20, compute_audit flags pool_starvation/supply_floor structural (refill = W20 enrollment), pywm py_low_board_clear, thermo DONE, minute_feed intraday +rows, daily_report+LIVE refreshed, token +0; (6) S7: attrition rows appended + guard CLEAN, treasure+e66 cards, claws installed, loop pin ok"
s["current_task"] = "r935: W19 landing closeout complete; r936 first act = W20 enrollment slice-1 (tick-stock-panel 18-strategy per-family collision census -> surviving entry families roster)"
s["task"] = s["current_task"]
s["now_active"] = "W19 closeout landed (three-axis adjudication chain closed); no in-flight burns; SatEngine ticking idle; supply floor 0/3 refill = W20 enrollment (next round slice-1)"
s["latest_artifact"] = "W19 judge products pushed 42b6f6111 (w19_judge.json + w19_reform_face.json + w19_paired_deltas.json + w19_intake.json, 13:49 landing) + prereg sec.7/8 backfill + TREASURE row + E66 card"
s["next"] = "r936: (a) W20 enrollment slice-1 FIRST ACT: catalog #7 tick-stock-panel (在册优先吃 top unconsumed supply per EXCLUSION_BOOK-legal ranking; NOT alphagen-RL per E17 closure) -- read repos/ tick-stock-panel 18 strategies, per-family collision check vs EXCLUSION_BOOK N1-N7 + CLOSED_FAMILIES 9 keys (海龟->N4-5 closed / 配对->account-infeasible / momentum variants->N4-1+MOM domain line closed), roster surviving families as NEW entry grammar faces (X=template_default S=as-burned T=daily_signal per three-axis canon), -> funnel 1/5 W20 candidate prereg draft (PREREG_TEMPLATE, consumer_plan, exit-axis explicit gate, queue_seed_gate check + T-18 collision probe before freeze); (b) S6 15:30 window today: update_daily new bar -> live.paper REGIME_GUARD=enforce + t35_open_fill_verify + t24 legs + minute_feed; (c) standing: GPU PSU-swap MODE=pause (i2v 27/53 held), unity POC editor window, bili-reply CEO cookie+aid, 48h CEO W19 report due 2026-10-16 13:49 (draft in next round window)"
s["next_milestone"] = "W20 enrollment chain start (slice-1 collision census -> candidate draft -> freeze -> GENERATE -> SCREEN pool refill 0->3); 48h CEO W19 report due 2026-10-16 13:49; S6 15:30 data window today"
s["note"] = "r935: W19 landing closeout round (product round by construction: judge products + sec.7/8 + treasure + E66); three-axis X/S/T adjudication CLOSED = future GENERATE needs entry x filter faces only"
s["verdict"] = "GREEN: W19 judge landed lawful-zero whole-package closeout (smoke 49/49; dualrun streak 20; attrition CLEAN; orders 0 unacked; D-19 zero-delta; 48h CEO clock running due 10-16 13:49); flags = supply_floor/pool_starvation structural (refill = W20 enrollment slice-1 next round) + GPU PSU-deferred standing (MODE=pause)"
s["orphan_face"] = 0
s["orphan_faces"] = 0
s["orphan_face_note"] = "r935 probe 13:5x: py_faces=13 orphans=0 killed=[]"
s["d19_watermark_guard"]["round_ref"] = 935
s["d19_watermark_guard"]["ts"] = iso
s["last_decisions_at"] = iso
s["last_decisions_read_at"] = iso
s["last_orders_at"] = iso
s["last_orders_read_at"] = iso
s["last_decisions_sha_method"] = "r935: verify structural_ok=true both watermarks EQUAL (dec d9d8aa72 ord 179ac0f4 unchanged post-rebase; origin commits bm-a/bm-c touched no docs/decisions.md orders.md)"
s["last_orders_sha_note"] = "r935: orders static (behind=0 after rebase+push; 88 O-files 0 unacked vs 213 acks, scan CLEAN 124 stale notes)"
s["sync"] = {"last_push_ts": iso, "note": "r935 closeout commit+push follows this write; delivery self-proof via fetch+rev-list after push"}
with io.open(sp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(s, f, ensure_ascii=False, indent=1)
    f.write("\n")
print("state.json r935 written")

# --- heartbeat fleet/machines/bm-b.json ---
hp = ROOT + r"\fleet\machines\bm-b.json"
h = json.load(io.open(hp, encoding="utf-8"))
h["last_seen"] = iso
h["ts"] = iso
h["current_task"] = s["current_task"]
h["verdict"] = "GREEN"
h["heartbeat_epoch_utc"] = epoch
h["clock_read"] = iso
h.setdefault("idle_rounds", 0)
h["agenda_starved"] = False
h["note"] = "r935 W19 landing closeout (products pushed 42b6f6111); next = W20 enrollment slice-1"
with io.open(hp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(h, f, ensure_ascii=False, indent=1)
    f.write("\n")
ok = isinstance(h.get("heartbeat_epoch_utc"), int)
print("heartbeat written, epoch int check:", ok, epoch)
