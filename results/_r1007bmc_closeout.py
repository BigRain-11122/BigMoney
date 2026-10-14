# r1007 closeout: state-bm-c.json + heartbeat update (key-level, JSON load-modify-dump)
import json, io, time, datetime

now_iso = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
now_epoch = int(time.time())
r = "r1007"

state_path = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\state-bm-c.json"
d = json.load(io.open(state_path, encoding="utf-8"))

d["round_no"] = 1008
d["last_round"] = r
d["last_round_at"] = now_iso
d["last_round_ts"] = time.time()
d["last_seen"] = now_iso
d["last_seen_at"] = now_iso
d["ts"] = now_iso
d["updated"] = now_iso
d["updated_at"] = now_iso
d["last_round_closed"] = now_iso
d["last_round_label"] = r
d["now_active"] = now_iso + " | " + r + " | bm-c: ledger path-split heal + wave2 watch (25/39, D04 burning) + W242/bars wait | counter 1007->1008"
d["activity_now"] = d["now_active"]
d["last_action"] = r + " closeout (ledger path-split 5th heal + claws reinstall + S6 chain green)"
d["last_action_at"] = now_iso
d["current_task"] = "wave2 harvest watch (25/39 saved, runner PID 24076, ETA ~22:20) + W242 finalize watch (bm-a) + bars re-probe"
d["current_task_at"] = now_iso
d["current_task_ts"] = now_epoch
d["last_round_summary"] = (r + ": wait-state watch window + REAL products: ledger path-split 5th instance HEALED "
  "(6 rows union verbatim to canonical + r1003-05 marker + orphan freeze pointer, receipt _r1007bmc_ledger_heal_receipt) + "
  "claws x2 reinstalled (CR-norm TRUE) + S6 all-green (dualrun streak 51, daily_report faces=5) + wave2 watch 25/39 healthy; "
  "counter 1007->1008")
d["last_round_summary_at"] = now_iso
d["last_artifact"] = (r + ": ledger path-split heal receipt results/_r1007bmc_ledger_heal_receipt.json + canonical r996-r1006 rows restored")
d["latest_artifact"] = d["last_artifact"]
d["recent_artifact"] = "r1006: W241 finalize estate af6ec72f9; r1007: ledger path-split heal + canonical restore"
d["next"] = ("r1008: (1) wave2 39/39 harvest face (CDN re-upload UPLOAD_FAIL_OR_SKIPPED + q88 board + orders receipt + "
  "poke bm-a assembly station -- CEO 1855 night order top priority, tonight full-local cut); (2) W242 finalize watch "
  "(bm-a chain; on landing -> W243 seat probe per seat-first law); (3) bars re-probe -> papers FULL CHAIN when 10-14 "
  "bar lands on sina; (4) MF-IC-P1 parked bm-a collector lane (standing relay)")
d["next_pointer"] = d["next"]
d["next_milestone"] = ("wave2 39/39 harvest + CDN ~22:20-22:40; W242 finalize->W243 seat (bm-a chain, <=48h); "
  "10-15 morning CEO MV finished-cut deathline (bm-a assembly consumes our wave2 clips)")
d["verdict"] = ("green: " + r + " = WATCH window (wave2 runner healthy 25/39+14 queued, GPU=MV night-order top priority legal burn; "
  "W242 upstream bm-a; bars sina-late debt=0) + PRODUCT window (ledger path-split 5th healed verbatim 6 rows + claws reinstalled "
  "+ S6 chain green); smoke 49/49 + dualrun streak 51 + attrition 4 CLEAN + satengine ALIVE + orphan 2/2 legal zero-kill")
d["did"] = d["last_round_summary"]
d["prod_lanes"] = ("CPU=N1 W241 CLOSED (af6ec72f9); W242=bm-a SEAT in-flight (chain theirs per seat-first); MF-IC-P1 parked bm-a lane; "
  "GPU=MV V3 wave2 burning (25/39 saved + 14 queued, runner PID 24076, ~10min/clip, harvest ~22:20, CEO 1855 top priority)")
d["verify"] = ("receipts: heal verbatim_assert=true + smoke 49/49 + dualrun streak 51 + attrition 4 CLEAN + claws CR-norm TRUE "
  "+ orphan face=2 legal + satengine alive + wm red=false + S7 quad green + probe unacked=0")
d["idle_rounds"] = 0
d["agenda_starved"] = False
d["heartbeat_epoch_utc"] = now_epoch
d["clock_read"] = now_iso

io.open(state_path, "w", encoding="utf-8", newline="").write(json.dumps(d, ensure_ascii=False, indent=1))

# heartbeat
hb_path = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\fleet\machines\bm-c.json"
h = json.load(io.open(hb_path, encoding="utf-8"))
h["last_seen"] = now_iso
h["ts"] = now_iso
h["updated"] = now_iso
h["heartbeat_epoch_utc"] = now_epoch
h["clock_read"] = now_iso
h["current_task"] = d["current_task"]
h["current_task_at"] = now_iso
h["last_round"] = r
h["last_round_at"] = now_iso
h["verdict"] = "green (see state-bm-c.json r1007)"
h["idle_rounds"] = 0
h["agenda_starved"] = False
io.open(hb_path, "w", encoding="utf-8", newline="").write(json.dumps(h, ensure_ascii=False, indent=1))

# self-assert: epoch int type + clock T-separator
chk = json.load(io.open(state_path, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in chk["clock_read"] and "+" in chk["clock_read"], "clock_read must be ISO8601 T-sep"
print("state+heartbeat written; round_no=", chk["round_no"], "epoch_int=", isinstance(chk["heartbeat_epoch_utc"], int),
      "clock=", chk["clock_read"])
