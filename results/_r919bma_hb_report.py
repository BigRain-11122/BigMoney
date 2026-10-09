# r919 bm-a heartbeat + round report append (fresh read-modify-write / append-only)
import json, datetime, time, os

REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
now_iso = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())

# --- heartbeat fleet/machines/bm-a.json ---
HP = os.path.join(REPO, "fleet", "machines", "bm-a.json")
with open(HP, "rb") as f:
    h = json.loads(f.read().decode("utf-8-sig"))
h.update({
    "ts": now_iso, "clock_read": now_iso, "last_seen": now_iso,
    "heartbeat_epoch_utc": epoch,
    "current_task": ("r920: S6 evening chain receipt verify + W199 engine ignition verify + "
                     "PARKING-P1 burn due 10-14 12:00 (O-20261009-1105)"),
    "current": "r919 closed: dead-session estate takeover (W199 freeze on origin b8a9a9112); S6 evening chain in flight",
    "last_action": "r919: estate takeover + zero-overlap rebase push 0/0; S6 38-leg evening chain running",
    "idle_rounds": 0, "agenda_starved": False,
    "verdict": "green (r919 estate takeover landed; smoke 49/49; engine ALIVE; S6 evening chain in flight)",
})
with open(HP, "w", encoding="utf-8", newline="") as f:
    json.dump(h, f, ensure_ascii=False, indent=1)
chk = json.loads(open(HP, encoding="utf-8-sig").read())
assert isinstance(chk["heartbeat_epoch_utc"], int)
assert "T" in chk["clock_read"]
print("heartbeat OK epoch int")

# --- round report line append (fresh tail-anchor per race law) ---
RP = os.path.join(REPO, "round_reports-bm-a.md")
line = ("| " + now_iso + " | r919 | dead-session estate takeover (r899 precedent, process census sole BigMoney loop + 2 unpushed "
        "commits + zero closeout): W199 prereg BUILD + five-face FREEZE (d372c9c1e) + n1_w199 12 shards absorbed, "
        "r832 writer-pause window (4 writer schtasks disable/enable), zero-overlap rebase onto bm-c 11-commit wave, "
        "push b8a9a9112 self-verified 0/0; S0.5 unacked=0 (scanner .md-suffix bug fixed) + DEC/ORD UNCHANGED; "
        "S1 smoke 49/49; watermark green; engine ALIVE (W199 ignition pending next tick); S6 38-leg evening chain "
        "driver launched PID 70404 (receipt lands this window) | orphan_faces=0; attrition CLEAN; quartet GREEN "
        "(pin=8/watchdog/claws); idle --worked 0 | r920: chain receipt verify + W199 ignition verify + PARKING-P1 due 10-14 |\n")
with open(RP, "a", encoding="utf-8", newline="") as f:
    f.write(line)
print("round report line appended")
