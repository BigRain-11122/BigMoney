# -*- coding: utf-8 -*-
"""r1141 bm-c closeout: state counter + heartbeat + round report row."""
import io, json, os, subprocess, time
from datetime import datetime, timezone, timedelta

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TZ = timezone(timedelta(hours=8))
NOW = datetime.now(TZ)
ISO = NOW.isoformat(timespec="seconds")
EPOCH = int(time.time())

TIP = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"], capture_output=True).stdout.decode().strip()


def load(p):
    return json.load(io.open(os.path.join(REPO, p), encoding="utf-8"))


def save(p, obj):
    io.open(os.path.join(REPO, p), "w", encoding="utf-8", newline="\n").write(
        json.dumps(obj, ensure_ascii=False, indent=1, sort_keys=True) + "\n")


st = load("state-bm-c.json")
st["round_no"] = 1142
st["round_no_label"] = "r1141 closeout -> counter 1142"
st["r1141_closeout_note"] = (
    "r1141: (1) S0-1 anchor bm-c (fleet/machine.json) + round-zero probe py_faces=5 orphans=0 zero-kill; "
    "S0 pull --rebase clean, worktree clean at open; (2) S0.5 dual-scan: DEC d5336c87 unchanged -> zero action; "
    "ORD stored face 9da3cb04 did NOT match origin content-sha1 6cec19c3 -> HEALED to 6cec19c3 (r977 pinned method: "
    "content-bytes sha1 of origin/main:docs/orders.md; the r1140 value 9da3cb04 was method/face inconsistent -- "
    "no new rows owed: tail rows are the 10-20 00:32 x2 @bm-a BigStream + 00:5x @bm-b bili, all zero BigMoney targets, "
    "already consumed r1140); unacked O files=0 (232 acks); (3) S1 smoke 49/49 PASS; (4) PRODUCT = W283 PREREG FREEZE: "
    "generator results/_r1141bmc_prereg_derive_w283.py (68 count-gated ordered substitutions, fail-closed residual+MUST/MUST_NOT gates) "
    "derived from the frozen W282 pre-run face (git show 7744416654:research/PERPETUAL_N1_W282_PREREG.md, r1049/r1052 law) -> "
    "research/PERPETUAL_N1_W283_PREREG.md 24,054 bytes / 64 lines; A 637_901..639_900 (33rd consecutive A-hop, base==W282 B tail+1 637_900+1 EXACT) / "
    "B 639_901..640_100 (34th above-own-A, base==own-A tail+1 639_900+1); chain K 618,320->620,520 proj, ledger 1,044,735->1,046,935 proj, "
    "n_eff 1,042,535->1,044,735, se_mu 0.000312; banned_direction_gate ADMIT rc0; (5) S6 light 10/10 rc0 (dualrun ZERO-DRIFT streak 51, "
    "461 entries; compute_audit FLAG pool_starvation+supply_floor=ready 0<floor 3 honest structural -- supply resumes at the W283 splice; "
    "watermark py_low_board_clear legal idle white-list; update_daily no-op cutoff 2026-10-19; regime ORANGE_COOL; clock CALL-2026-10-19 ORANGE_COOL; "
    "fund_premium pre-15:30 no-op; b_layer rc0; daily_report 5 faces; token delta=0, L2 legs 0 today); "
    "(6) S7: attrition 4 ledger files CLEAN (1 historical heal noted); loop pin=5 no-op; watchdog re-registered (S4U flip access-denied -> "
    "default principal, same known elevation face as r1138/r1139); both claws reinstalled; (7) window pit: ORD watermark face inconsistency "
    "(state stored a sha that no longer matched any origin content face) -- healed by recomputing with the pinned content-bytes sha1 method "
    "and disclosing zero row debt instead of re-consuming."
)
st["recent_artifact"] = "research/PERPETUAL_N1_W283_PREREG.md"
st["verdict"] = "green r1141 product window: W283 PREREG FREEZE (A 637_901..639_900 / B 639_901..640_100) + banned gate ADMIT rc0"
st["verify"] = ("derive gates 68/68 rules count-asserted, zero residual, zero MUST_NOT | banned ADMIT rc0 | smoke 49/49 | satengine rc0 "
                "| S6 10/10 rc0 | attrition 4 CLEAN | orphan face=0 | unacked=0 | local-not-origin commits=0")
st["last_orders_sha"] = "6cec19c30bf7"
st["last_orders_sha_note"] = (
    "r1141: stored r1140 value 9da3cb04 was face-inconsistent vs origin content-sha1 6cec19c3; recomputed with the pinned "
    "content-bytes sha1 method (r977). Tail rows 10-20 00:32 x2 + 00:5x already consumed r1140, zero rows owed."
)
st["sync"] = {"origin_tip": TIP, "ts": ISO}
st["ts"] = ISO
st["updated"] = ISO
st["updated_at"] = ISO
st["ram_free_gb"] = 3.6
save("state-bm-c.json", st)

hb = load("fleet/machines/bm-c.json")
hb["last_seen"] = ISO
hb["ts"] = ISO
hb["clock_read"] = ISO
hb["heartbeat_epoch_utc"] = EPOCH
hb["current_task"] = "r1141 W283 prereg freeze landed; next = W283 five-face splice (pf/n1 WAVE_CONFIGS)"
hb["verdict"] = st["verdict"]
hb["cpu_cores"] = 32
hb["free_ram_gb"] = 3.6
hb["gpu_free_vram_gb"] = 13.9
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
save("fleet/machines/bm-c.json", hb)

row = ("%s | r1141 | S0 anchor bm-c + probe orphans=0 | S0.5 dec FALSE, ORD watermark healed to 6cec19c3 (pinned content-sha1, zero rows owed) | "
       "unacked=0 | **PRODUCT = W283 PREREG FREEZE**: research/PERPETUAL_N1_W283_PREREG.md (24,054B/64 lines) derived from frozen W282 pre-run face "
       "(7744416654) by results/_r1141bmc_prereg_derive_w283.py -- 68 count-gated rules, zero residual; A **637_901..639_900** (33rd A-hop, base==637_900+1) / "
       "B **639_901..640_100** (34th above-own-A, base==639_900+1); chain K 618,320->620,520 proj / ledger 1,044,735->1,046,935 proj / n_eff 1,042,535->1,044,735; "
       "banned_direction_gate ADMIT rc0 | verify: smoke 49/49, satengine rc0, S6 10/10 rc0, attrition 4 CLEAN, orphan face=0 | "
       "next pointer = W283 five-face splice (pf/n1 WAVE_CONFIGS + 12/12 engine burn) | local-not-origin commits=0\n")
p = os.path.join(REPO, "round_reports-bm-c.md")
old = io.open(p, encoding="utf-8", newline="").read()
if not old.endswith("\n"):
    old += "\n"
io.open(p, "w", encoding="utf-8", newline="").write(old + row)
print("closeout written", ISO, TIP[:12])