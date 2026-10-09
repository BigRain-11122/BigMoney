# -*- coding: utf-8 -*-
# r920 closeout: seat-msg self-consume -> processed/ + round report append + state bump + heartbeat update
import json, os, shutil, datetime, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
now = datetime.datetime.now().astimezone()
ts = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(now.timestamp())

# --- 1. seat MSG self-consume -> processed/ (own publication, r809 precedent) ---
seat = "fleet/inbox/MSG-2026-10-09-1645-bma-w200-seat.md"
proc = os.path.join("fleet", "inbox", "processed", os.path.basename(seat))
if os.path.exists(seat):
    shutil.move(seat, proc)
    print("seat MSG -> processed:", proc)

# --- 2. round report append (fresh-read single-file write, multi-writer law) ---
report_line = (
    f"{ts} | r920 | S6 evening chain receipt verify PASS (38/38 rc0 bad_legs NONE; "
    "panel 10-08 sina late-bar honest no-op, self-heal leg retried 0 new rows) + "
    "W199 engine self-burn verified 12/12 (checkpoint valid, real burn data n=166+ "
    "families faces, evidence_cutoff 2026-09-22) + W199 finalize ONE-PASS LANDED "
    "(ledger 849,945+2,200=852,145 EXACT, merged pool K=435,720 EXACT, skill_line_v2 "
    "@n_eff 1.188->1.1881; results/perpetual_faces/n1_w199_results.json pushed "
    "c19c67450) + W200 SEAT CHAIN WINDOW OPENED: pre-seat probe rc0 ADMIT "
    "(A 454_804..456_803 hops=1 staircase SIXTIETH instance E36 + B 456_804..457_003 "
    "hops=1 own-A reserved walk W141; full universe conflict scan 0; origin vacancy "
    "verified) + seat MSG published=reserved on origin 143fcfe1b "
    "(MSG-2026-10-09-1645-bma-w200-seat.md; anchor W199 finalize actuals per r590 "
    "zero roll-forward) | S0: daemon churn absorb x3 commits + push-race resolution "
    "(claw blocked stale-pool replay twice vs bm-c autofill treadmill "
    "b64d619e4/5cd5b32f3; r863 escape backup->clean->rebase->push->restore applied; "
    "update_status.json UU take-newer 16:24:33 vs 16:23:42; delivery self-verified "
    "0/0 fetch+rev-list) | S0.5 unacked=0 full-name compare (55/55; scanner copy "
    "regression o[:-3] caught & fixed same-window); DEC bd94a27b/ORD b38eaaf8 "
    "UNCHANGED zero delta | S1 smoke 49/49 PASS | watermark green red=false "
    "next_pick claimed moneyflow | engine ALIVE idle | attrition scan CLEAN "
    "(healed shrink rows noted) | claws both present & identical | orphan_faces=0 "
    "| idle verdict not-GREEN (VRAM 0.5GB < 6GB threshold; substantial work this "
    "round = W199 finalize + W200 seat, exempt) | next: W200 five-face freeze "
    "window (seat published, freeze due <=24h seat law; W200 freezer MUST re-derive "
    "post-W199 universe + own-A reservation per W141/E36); PARKING-P1 burn due "
    "10-14 12:00 (O-20261009-1105) not yet due; sina 10-09 bar late watch next "
    "round self-heal | artifact: n1_w199_results.json 1,288,078B + "
    "_r920bma_w200_probe.py/receipt + seat MSG"
)
with open("round_reports-bm-a.md", "r", encoding="utf-8") as f:
    rpt = f.read()
if not rpt.endswith("\n"):
    rpt += "\n"
rpt += report_line + "\n"
with open("round_reports-bm-a.md", "w", encoding="utf-8", newline="") as f:
    f.write(rpt)
print("round report appended, +1 line")

# --- 3. state bump (fresh read -> write) ---
sp = "state-bm-a.json"
with open(sp, "rb") as f:
    st = json.loads(f.read().decode("utf-8-sig"))
st["round_no"] = 920
st["round"] = 920
st["loop_round"] = 920
st["last_round"] = 919
st["last_round_at"] = "2026-10-09T15:59:52+08:00"
st["last_round_closed"] = ts
st["ts"] = ts
st["updated"] = ts
st["clock_read"] = ts
st["now_active"] = "r920 closing: W199 finalize landed (852,145/K435,720) + W200 seat published (A 454_804..456_803 + B 456_804..457_003 staircase SIXTIETH)"
st["current"] = st["now_active"]
st["current_task"] = "r921: W200 five-face freeze window (seat law <=24h; post-W199 re-derive + own-A reservation W141/E36); sina 10-09 bar late watch self-heal; PARKING-P1 burn due 10-14 12:00 (O-20261009-1105)"
st["task"] = st["current_task"]
st["next"] = st["current_task"]
st["next_milestone"] = "r921: W200 five-face freeze + ignition chain; PARKING-P1 burn due 10-14 12:00"
st["did"] = ("r920: S6 38-leg chain receipt verified all-green + W199 engine self-burn 12/12 "
             "verified + W199 finalize one-pass landed (852,145/K435,720/skill 1.1881, pushed "
             "c19c67450) + W200 seat chain window opened (probe rc0 ADMIT A 454_804..456_803 + B "
             "456_804..457_003 staircase SIXTIETH, seat MSG published origin 143fcfe1b)")
st["last_artifact"] = ("r920 products: results/perpetual_faces/n1_w199_results.json 1,288,078B "
                       "(ledger 852,145) + results/_r920bma_w200_probe.py + "
                       "results/_r920bma_w200_probe_receipt.json (rc0 ADMIT) + "
                       "fleet/inbox/processed/MSG-2026-10-09-1645-bma-w200-seat.md (published "
                       "origin 143fcfe1b)")
st["latest_artifact"] = st["last_artifact"]
st["last_action"] = "r920 closeout: W199 finalize landed + W200 seat published; delivery 0/0"
st["verdict"] = "green (r920: W199 finalize one-pass 852,145/K435,720 + W200 seat published; smoke 49/49; watermark green; engine ALIVE; attrition CLEAN; push self-verified 0/0)"
st["verify"] = st["verdict"]
st["orphan_faces"] = 0
st["idle_rounds"] = 0
st["agenda_starved"] = False
st["heartbeat_epoch_utc"] = epoch
st["last_heartbeat_epoch_utc"] = epoch
st["last_run"] = ts
st["last_seen"] = ts
st["push_verified"] = {"ts": ts, "origin_tip": "143fcfe1b", "ahead_behind": "0/0",
                       "note": "r920 seat push self-verified post-push fetch+rev-list"}
st["sync"] = st["push_verified"]
st["last_decisions_seen"] = "r920 S0.5 scan: DEC bd94a27b UNCHANGED vs r919 consumption -- zero delta; zero action"
st["last_orders_seen"] = "r920 S0.5 scan: ORD b38eaaf8 UNCHANGED vs r919 consumption -- unacked=0 (full-name compare fixed in-window); zero action"
st["last_decisions_at"] = ts
st["last_orders_at"] = ts
with open(sp, "w", encoding="utf-8", newline="") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
print("state bumped: round_no", st["round_no"])

# --- 4. heartbeat (own machine file only) ---
hp = os.path.join("fleet", "machines", "bm-a.json")
with open(hp, "rb") as f:
    hb = json.loads(f.read().decode("utf-8-sig"))
hb["last_seen"] = ts
hb["ts"] = ts
hb["clock_read"] = ts
hb["heartbeat_epoch_utc"] = epoch
hb["last_heartbeat_epoch_utc"] = epoch
hb["current_task"] = st["current_task"]
hb["verdict"] = st["verdict"]
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
with open(hp, "w", encoding="utf-8", newline="") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
reread = json.load(open(hp, encoding="utf-8-sig"))
assert isinstance(reread.get("heartbeat_epoch_utc"), int), "epoch must be int (R170/R178 law)"
print("heartbeat written; epoch int verified:", reread["heartbeat_epoch_utc"])
