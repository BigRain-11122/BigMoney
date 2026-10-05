"""r724 bm-a close: state + heartbeat + ledger-line update (byte-safe utf-8).
Vitals sampled live: cpu 0.7% / ram 48.3GB / gpu free 1701MB (uv-python MCP
host context holds ~10.3GB VRAM, known-benign r718/r721 face)."""
import datetime
import json
import os
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
now = datetime.datetime.now().astimezone()
now_iso = now.isoformat(timespec="seconds")
epoch = int(time.time())

# ---------- state-bm-a.json ----------
sp = os.path.join(ROOT, "state-bm-a.json")
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = 725
st["round"] = "r724"
st["last_round"] = "r724"
st["loop_round"] = st.get("loop_round", 589) + 1
st["did"] = ("r724: golden-week steady-state watch round (S6 38 legs rc0 chain re-run + "
             "W16 burn-chain watch + trio/O-1440/perpetual faces re-verified green) -- "
             "W16 GENERATE auto-release gate confirmed armed (fill_ladder floor=3 satisfied "
             "by FUND trio, no-op; trio=bm-b canonical 3-lane live burn per heartbeat+readiness "
             "doc; W16 generate one-shot gate self-protects so no pre-run probe possible by design); "
             "O-1440 idle-order face re-verified receipted (r681: 8 tickets 157-164 zero-open + "
             "trio live-burn evidence); N2/N4 generator scripts in place (perpetual_faces verdict: "
             "live supply, no action); py_watermark verdict=py_low_board_clear (legal idle whitelist); "
             "S6 38 legs rc0 (dualrun ZERO-DRIFT streak 26; audit flags gpu_unauthorized+supply_gap "
             "= same known-benign r718/r721/r722 faces, rogue=uv-python external session); "
             "S7 quartet green + attrition CLEAN 4 ledgers + orders 154/154 double-scan + "
             "D-19 MATCH d14dcc74 zero consumption")
st["current_task"] = ("r725 next: 5x HANDOVER block (round_no hits multiple of 5) + W16 burn-chain "
                      "watch (GENERATE auto-enqueues via fill_ladder when floor drops after FUND trio "
                      "NULLS finalize bm-b 10-05..09 per O-2115; then GENERATE->SCREEN->JUDGE->s4 intake "
                      "per consumer_plan); W119 finalize on W118 landing (bm-b wave, FAIL-CLOSED watch); "
                      "10-08 reopen window legs (external run-11/run-7 + marks resume + REGIME_GUARD v3 "
                      "first-new-bar); golden-week watch")
st["last_action"] = ("r724: steady-state watch + S6 38 rc0 (dualrun streak 26) + quartet/attrition/orders/"
                     "D-19 green; no legal bm-a burn work (trio=bm-b canonical, W16=floor-gated, "
                     "board clear)")
st["last_round_at"] = now_iso
st["last_round_ts"] = now_iso
st["last_run"] = now_iso
st["updated"] = now_iso
st["next"] = ("r725: 5x HANDOVER block + W16 burn-chain watch + 10-08 reopen legs prep-check; "
              "golden-week watch")
st["notes"] = ("r724 notes: steady-state watch round per product-law waiting-form (wait object=bm-b "
               "trio finalize, in flight V1294/Q1045/D836 at bm-b r724 probe); r723 session left "
               "state did/last_round stale at r722 (round_no correct at 724) -- healed this round "
               "with honest full-state write; no memory append (no new pit per four-question gate); "
               "no METHODOLOGY/treasure registry append (no finalize/closure step this round)")
st["verify"] = ("S6 38 rc0 (log results/_r724bma_s6_log.txt) + WM py_low_board_clear + smoke 48/48 "
                "(round start) + D-19 MATCH d14dcc74 + orders 154/154 double-scan + attrition CLEAN "
                "+ quartet green (loop pin=8 no-op, watchdog re-reg, claws identical) + fill_ladder "
                "floor=3 no-op + perpetual_faces verdict no-action + push delivery self-check")
json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---------- fleet/machines/bm-a.json heartbeat ----------
hp = os.path.join(ROOT, "fleet", "machines", "bm-a.json")
h = json.load(open(hp, encoding="utf-8"))
h["machine_id"] = "bm-a"
h["last_seen"] = now_iso
h["heartbeat_epoch_utc"] = epoch
h["clock_read"] = now_iso
h["last_heartbeat_epoch_utc"] = h.get("heartbeat_epoch_utc", epoch)
h["cpu_pct"] = 0.7
h["cpu_load_pct"] = 0.7
h["cpu_util_pct"] = 0.7
h["cores"] = 32
h["cpu_cores"] = 32
h["ram_free_gb"] = 48.3
h["free_ram_gb"] = 48.3
h["idle_ram_gb"] = 48.3
h["gpu_free_vram_gb"] = 1.7
h["gpu0_free_vram_gb"] = 1.7
h["gpu_idle_vram_gb"] = 1.7
h["verdict"] = ("GREEN holiday-idle (py 0.7% legal board-clear per WM verdict; satengine alive; "
                "trio bm-b 3-lane live burn; W16 armed auto-release)")
h["current_task"] = st["current_task"]
h["task"] = st["current_task"]
h["current"] = "golden-week watch: W16 burn-chain + trio finalize (bm-b) + 10-08 reopen prep"
h["now_active"] = "golden-week watch (no new bars; S6 legs honest no-op)"
h["last_action"] = st["last_action"]
h["last_round"] = "r724"
h["round_no"] = 725
h["loop_round"] = st["loop_round"]
h["last_run"] = now_iso
h["latest_artifact"] = ("results/_r724bma_s6_log.txt (38 legs rc0, dualrun ZERO-DRIFT streak 26) "
                        "@ " + now_iso)
h["next_milestone"] = ("W16 GENERATE auto-release on FUND trio finalize (bm-b 10-05..09, watch <=10-09); "
                       "10-08 reopen window legs (run-11/run-7+marks+REGIME_GUARD v3 first-new-bar)")
h["health"] = "green"
json.dump(h, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# readback assertions (R170/R178 law: epoch must be JSON int)
hb = json.load(open(hp, encoding="utf-8"))
assert isinstance(hb["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in hb["clock_read"] and "+" in hb["clock_read"], "clock_read must be ISO-T"
print("state+heartbeat updated:", now_iso, "| epoch:", epoch, "| readback assertions PASS")
