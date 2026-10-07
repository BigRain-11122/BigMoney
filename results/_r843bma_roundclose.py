# -*- coding: utf-8 -*-
"""r843 bm-a round-close: state-bm-a.json + fleet/machines/bm-a.json
fresh read-modify-write (r10-06 law), epoch int law (R170/R178),
clock_read T-separator law (R262)."""
import io
import json
import time
import datetime

now_iso = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())
prev_state = json.load(io.open("state-bm-a.json", encoding="utf-8"))
prev_epoch = prev_state.get("last_heartbeat_epoch_utc")

state = prev_state
state["round_no"] = 843
state["round"] = 843
state["loop_round"] = "r843"
state["last_round"] = "r843"
state["current_task"] = ("W177 freeze landed (r843, five-face, self-ignited, "
                         "3/12+ burning); next = W177 finalize one-pass then "
                         "10-08 reopen data chain re-arm")
state["now_active"] = "W177 burning on engine (post-freeze); finalize next"
state["did"] = (
    "r843: W177 FREEZE five-face insertion landed + self-ignited -- "
    "pf N1_BANDS[177] row (A 404_204..406_203 staircase 37th E36 hops=1 / "
    "B 406_204..406_403 own-A mutual exclusion hops=1 per r841 probe ADMIT) + "
    "n1 WAVE_CONFIGS[177] entry + materializer block + PASS-claim four "
    "insertions via r834-bloodline buildgen S76 fact map (173 derived pair "
    "old-sides count-verified against physical W176 face dumps pre-emission; "
    "DRY full-gate one-pass zero-write first; AST gate green; malformed-window "
    "scans CLEAN); banned gate ADMIT 0 re-verified at freeze (r484 law); "
    "pf selftest 9/9 + n1 selftest green incl. W177 materializer leg "
    "(dep W17..W176 all present, ledger head 793,105, K 385,120); "
    "freeze commit c06cc230f pushed 403bcaac..c06cc230f behind-0/ahead-0 "
    "self-verified; engine tick self-ignited (active n1w177-2of12 -> tick "
    "ignited 3of12, shards_done 2->3, queue 8, product growth face per r325); "
    "S6 ~30 legs rc0 (dualrun ZERO-DRIFT streak 51; holiday no-op family "
    "cutoff 2026-09-30); S7 quartet green; ledger r843 line landed after "
    "tail-glue heal (no-trailing-CRLF merge caught + surgically split, "
    "1635 lines, numstat 2+/1- compliant); CODELY mini-increment (r842 S5 "
    "pit 704B verbatim out -> pit-protocol-lane.md + r843 glue pit 835B in, "
    "main 30,605B under line, receipt _r843bma_codely_increment.json)"
)
state["next"] = (
    "W177 finalize (await 12/12 shards on engine queue, then finalize "
    "one-pass per r839 precedent: ledger 793,105+2,200=795,305 proj / "
    "K 385,120+2,200=387,320 proj; window <=48h at engine burn rate); "
    "then 10-08 market-reopen data chain re-arm (first trading day after "
    "golden week -- daily panel reactivation, regime/clock refresh on live "
    "bars)"
)
state["last_action"] = ("W177 freeze landed: pf row + n1 entry/mat/claim; "
                        "engine self-ignited shard 3of12 in flight")
state["verify"] = (
    "probe ADMIT r841 receipt bands machine-read (A 404204_406203 / "
    "B 406204_406403); buildgen 173 pairs old-side dump-verified; DRY "
    "one-pass; banned gate ADMIT 0; pf 9/9 + n1 selftest green; "
    "commit c06cc230f push behind-0/ahead-0 fetch self-verified; "
    "engine ignite evidence = active_burns + shards_done_total growth "
    "(r325); smoke 48/48 (round start); S6 ~30 legs rc0; dualrun "
    "ZERO-DRIFT streak 51; attrition CLEAN; quartet green; orphan face=1 "
    "(read-only report); orders diff zero; decisions watermark 4c32527b "
    "identical zero-action; monthly legs discharged check (science_audit "
    "ran 10-05, BRIEF/SR-202609 present)"
)
state["latest_artifact"] = "scripts/perpetual_faces.py @W177 row (freeze commit c06cc230f)"
state["last_round_at"] = now_iso
state["last_round_ts"] = now_iso
state["last_run"] = now_iso
state["updated"] = now_iso
state["clock_read"] = now_iso
state["ts"] = now_iso
state["heartbeat_epoch_utc"] = epoch
state["last_heartbeat_epoch_utc"] = prev_epoch
io.open("state-bm-a.json", "w", encoding="utf-8").write(
    json.dumps(state, indent=1, ensure_ascii=False))
chk = json.load(io.open("state-bm-a.json", encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch not int"
assert "T" in chk["clock_read"], "clock_read not ISO-T"
print("state OK: round", chk["round_no"], "| epoch", chk["heartbeat_epoch_utc"],
      "| clock", chk["clock_read"])

# ---- heartbeat ----
hb = json.load(io.open("fleet/machines/bm-a.json", encoding="utf-8"))
hb["clock_read"] = now_iso
hb["last_seen"] = now_iso
hb["ts"] = now_iso
hb["last_heartbeat_epoch_utc"] = hb.get("heartbeat_epoch_utc")
hb["heartbeat_epoch_utc"] = epoch
hb["last_round"] = "r843"
hb["loop_round"] = "r843"
hb["round"] = 843
hb["round_no"] = 843
hb["last_action"] = ("W177 freeze five-face landed + engine self-ignited "
                     "(3/12 burning, queue 8)")
hb["now_active"] = "W177 burning (finalize next window); 10-08 reopen re-arm queued"
hb["task"] = ("W177 finalize when 12/12 shards done; 10-08 market-reopen "
              "data chain re-arm")
hb["current"] = "W177 freeze landed r843; burn in flight"
hb["current_task"] = ("W177 freeze landed (r843); next = W177 finalize "
                      "one-pass + 10-08 reopen data chain re-arm")
hb["latest_artifact"] = ("scripts/perpetual_faces.py @W177 row "
                         "(freeze commit c06cc230f, 2026-10-07T21:0x)")
hb["next_milestone"] = ("W177 finalize one-pass (ledger proj 795,305 / "
                        "K proj 387,320; window <=48h at engine burn rate) + "
                        "10-08 reopen data chain re-arm (next 1-2 windows)")
try:
    import psutil
    hb["cpu_pct"] = psutil.cpu_percent(interval=0.5)
    vm = psutil.virtual_memory()
    hb["ram_free_gb"] = round(vm.available / 2**30, 1)
    hb["free_ram_gb"] = hb["ram_free_gb"]
    hb["idle_ram_gb"] = hb["ram_free_gb"]
    hb["idle_ram_mb"] = int(hb["ram_free_gb"] * 1024)
except Exception as e:
    print("psutil metrics skipped:", e)
io.open("fleet/machines/bm-a.json", "w", encoding="utf-8").write(
    json.dumps(hb, indent=1, ensure_ascii=False))
chk2 = json.load(io.open("fleet/machines/bm-a.json", encoding="utf-8"))
assert isinstance(chk2["heartbeat_epoch_utc"], int), "hb epoch not int"
assert "T" in chk2["clock_read"], "hb clock_read not ISO-T"
print("heartbeat OK: epoch", chk2["heartbeat_epoch_utc"], "| clock",
      chk2["clock_read"], "| cpu", chk2.get("cpu_pct"), "| ram_free",
      chk2.get("ram_free_gb"))
