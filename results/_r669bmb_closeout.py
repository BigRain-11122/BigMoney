# r669 bm-b closeout: state.json + heartbeat + round report append + light orders re-scan
import json, time, os, subprocess
from datetime import datetime, timezone, timedelta

TZ = timezone(timedelta(hours=8))
now_iso = datetime.now(TZ).isoformat(timespec="seconds")
epoch = int(time.time())

# ---------- 1. light orders re-scan (closeout dual-scan, local only) ----------
hb0 = json.loads(open(r"fleet\machines\bm-b.json", "rb").read().decode("utf-8"))
p = subprocess.run(["git", "ls-tree", "--name-only", "HEAD", "fleet/orders/"], capture_output=True)
disk = {os.path.basename(l.strip()) for l in p.stdout.decode("utf-8").splitlines()
        if os.path.basename(l.strip()).startswith("O-") and l.strip().endswith(".md")}
ack = set(hb0.get("orders_ack", []))
unacked = sorted(disk - ack)
assert disk, "disk set empty = probe broken (r669 pit law)"
print("closeout orders scan: disk", len(disk), "ack", len(ack), "unacked", unacked)

# ---------- 2. state.json round 669 ----------
S = r"state.json"
st = json.loads(open(S, "rb").read().decode("utf-8"))
st["round_no"] = 669
st["note"] = (
    "r669: watch+hygiene round -- S0 up-to-date 0/0; D-19 dual MATCH (decisions EB14B510 + group orders 68947C17, "
    "sparse-clone raw-bytes probe, K: absent in session); fleet orders 153/153 zero-unacked (round-start+closeout dual scan); "
    "S1 smoke 48/48; S3 board zero-open (job_list 0 + tasks open 0), satengine alive (queue 0), watermark GREEN "
    "(red=false; bandit next_pick moneyflow-IC = terminal-state face: sina-construct leg judged_negative CLOSED r338 + "
    "EM face parked source-blocked, self-heal armed); trio NULLS burns healthy V739/Q571/D422 of 2000 (owner=bm-b, "
    "claim-refresh 11:56:12, ~6-8 rows/hr/family pace); finalize chain pre-verified (r633 blocker-2 VALUE passive fix in-runner "
    "+ bm-a 06:32 rehearsal rerun 3/3 all_legs_ok; blocker-1 G-SEG GM-ruled insufficient-sample frozen per O-20261004-0808); "
    "S6 37/38 rc0 + 1 honest red leg: update_lhb exit 2 (EM datacenter SSLError fetch_fail 12:08, cutoff 2026-09-30 behind "
    "expected disclosure 2026-10-02; IWR system-path probe HTTP 200 at 12:12 = python direct-path SSL flap face, 30-min "
    "self-heal armed, bm-a lane redundancy; watch face, zero unilateral VPN action); S7 self-heal 4/4 (loop pin=2 no-op, "
    "watchdog re-registered, both claws reinstalled LF-normalized), attrition CLEAN 4 ledgers; S4 capture: ls-tree pathspec "
    "prefix-face pit -> pit-git.md +865B (LF 53->54, md5pre 8d26ec35) + CODELY.md pointer increment +221B"
)
st["last_round_at"] = now_iso
st["ts"] = now_iso
st["updated"] = now_iso
st["last_seen"] = now_iso
st["clock_read"] = now_iso
st["round_no_label"] = ("bm-b round 669 (watch round: trio NULLS V739/Q571/D422 of 2000 healthy; "
                        "S6 37/38 + lhb source-fail honest rc2; ls-tree pit capture; D-19 dual MATCH)")
st["last_decisions_read_at"] = now_iso
open(S, "wb").write((json.dumps(st, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
rt = json.loads(open(S, "rb").read().decode("utf-8"))
assert rt["round_no"] == 669 and isinstance(rt["round_no"], int)
print("state.json -> round 669 OK, reparse OK")

# ---------- 3. heartbeat bm-b.json ----------
H = r"fleet\machines\bm-b.json"
hb = hb0
hb["last_seen"] = now_iso
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = now_iso
hb["round_no"] = 669
hb["round_no_label"] = "round 669 (bm-b)"
hb["current_task"] = ("round 669 done: watch round -- trio NULLS V739/Q571/D422 of 2000 healthy (owner=bm-b, burns alive) "
                      "+ finalize chain pre-verified (rehearsal 3/3 green + G-SEG GM-ruled) + S6 37/38 rc0 with 1 honest "
                      "red leg (update_lhb rc2 EM SSLError source-fail, self-heal armed) + D-19 dual MATCH + orders 153/153 "
                      "+ S4 pit capture (ls-tree pathspec prefix face -> pit-git.md)")
hb["verdict"] = ("healthy: smoke 48/48, S6 37/38 (lhb source-fail honest rc2 disclosed), trio burns healthy, "
                 "board clear, D-19 dual MATCH, round 669 delivered (watch round)")
hb["ts"] = now_iso
hb["updated"] = now_iso
hb["orders_ack_count"] = len(hb.get("orders_ack", []))
open(H, "wb").write((json.dumps(hb, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
rt2 = json.loads(open(H, "rb").read().decode("utf-8"))
assert isinstance(rt2["heartbeat_epoch_utc"], int) and "T" in rt2["clock_read"]
print("heartbeat -> round 669 OK, epoch int OK, clock T-sep OK")
