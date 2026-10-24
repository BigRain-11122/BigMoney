# -*- coding: utf-8 -*-
"""r1216 bm-c closeout: round report + state + heartbeat."""
import io
import json
import time
from datetime import datetime, timezone, timedelta

TZ = timezone(timedelta(hours=8))
now = datetime.now(TZ)
ts = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
round_no = 1216

ROW = (
    "2026-10-24T23:1x+08:00 | r1216 | W318 PREREG FROZEN (canon-clone of the W317 POST-RUN face "
    "231c6f902f:research/PERPETUAL_N1_W317_PREREG.md, 29,002B / 75 lines / sha16 8c22d023eb2f2668) -> "
    "research/PERPETUAL_N1_W318_PREREG.md (28,796B / 75 lines / sha16 c77e004753fb06fc); 45 count-asserted keys, "
    "90 band tokens rolled +2200 (A 714_901..716_900 / B 716_901..717_100, naive A continuation 714_701..716_700, "
    "W319p A 716_901..718_900 / B 717_101..717_300), 4 cumulative chains (se_mu narrowing / A-B 1-hop list / "
    "own-turn rotation / RAM freeze chain) parked and EXTENDED not rolled, sec.7 taken VERBATIM from the post-W317-finalize "
    "face, sec.8 rebuilt for the W319 projections; banned_direction_gate ADMIT rc0 zero matches; generator is idempotent. "
    "S0: HEAD==origin on open (0 behind / 0 ahead); dirty set = 3 S6-regenerated products (machine-health / attrition scan / "
    "orphan probe, committed with this round) + 13 untracked _w315 scratch files (left alone). "
    "S0.5 D-19: orders unacked=0 (109 files / 234 acks); decisions raw-blob sha256 3143a3ce2b711a47 and orders content face "
    "8ff7de47df154ffa both UNCHANGED vs stored watermarks => zero decision/order rows owed. S1 smoke 57/57 PASS. "
    "round-zero orphan probe py_faces=5 orphans=0 resident_servers=2 killed=[]; saturation engine status rc0 (queue idle, "
    "W317 12/12 adopted, bids empty = honest). S7 attrition guard 4 ledger files CLEAN (3 historical shrinks healed); "
    "scheduled tasks NOT re-registered per the 2026-10-17 CEO cleanup order; git claws present. "
    "PIT (two clone findings, both caught before canon): (1) a NUM key carrying a wave token must be written in POST-bump form "
    "('r1211/r1212/r1213 W317', not ...W316) because the count table runs AFTER wave_bump -- the first derive run died on a "
    "zero-hit key (r1211 second instance of this family); (2) two of the eight r1214 literals in the source are seat-provenance "
    "phrases that must map to the SEAT window (r1215), not to this window (r1216), so a blanket r1214->r1216 pass silently "
    "mis-attributes the seat -- they are parked as longer keys that win the single-pass alternation. "
    "| CEO face: 当前活=W318 prereg frozen, splice unblocked; 最近实物=research/PERPETUAL_N1_W318_PREREG.md (2026-10-24 23:1x); "
    "下个里程碑=W318 five-face splice + 12/12 shard burn (<=48h) "
    "| watermark verdict: GREEN (red=false, lane healthy, board clear) "
    "| local-not-on-origin commits=0 (post-push self-proof) | registry sweep zero-hit | dept:research/engineering"
)

with io.open("round_reports-bm-c.md", "a", encoding="utf-8", newline="") as f:
    f.write("\n" + ROW + "\n")

# ---- state
st = json.load(io.open("state-bm-c.json", encoding="utf-8"))
st["round"] = round_no
st["round_no"] = round_no
st["round_no_label"] = "r1216 W318 prereg frozen -> next r1217 splice"
st["last_round"] = round_no
st["last_round_label"] = "r1216"
st["recent_artifact"] = "research/PERPETUAL_N1_W318_PREREG.md"
st["latest_artifact"] = "research/PERPETUAL_N1_W318_PREREG.md"
st["updated"] = now.strftime("%Y-%m-%d %H:%M:%S")
st["updated_at"] = ts
st["ts"] = ts
st["status"] = "green"
st["verdict"] = "GREEN"
st["verify"] = ("W318 prereg frozen (sha16 c77e004753fb06fc) | banned gate ADMIT | smoke 57/57 | "
                "attrition CLEAN | orphan 0 | engine queue idle (W317 12/12 adopted)")
st["next"] = "r1217: W318 five-face splice (registry row 318 + WAVE_CONFIGS + N1_BANDS) -> engine 12/12"
st["next_action"] = "W318 five-face splice off _w317bmc_freeze_edits.py, then engine self-ignite"
st["current_task"] = "W318 prereg frozen; splice next"
st["current_task_at"] = ts
st["last_decisions_read_at"] = ts
st["last_decisions_read_note"] = ("r1216: DEC delta FALSE (raw-blob sha256 3143a3ce); ord content face 8ff7de47 hold; "
                                  "zero decision/order rows owed")
st["last_orders_read_at"] = ts
st["last_orders_read_note"] = "r1216: unacked orders=0 (109 files vs 234 acks)"
st["r1216_closeout_note"] = (
    "r1216: W318 prereg frozen in one window off the W317 post-run face 231c6f902f (28,796B/75 lines/sha16 c77e004753fb06fc); "
    "45 keys + 90 band tokens +2200 + 4 parked chains extended; banned gate ADMIT; smoke 57/57; zero S0.5 delta; "
    "no burn this window (engine burns only after the splice).")
io.open("state-bm-c.json", "w", encoding="utf-8", newline="").write(
    json.dumps(st, ensure_ascii=False, indent=1))

# ---- heartbeat
hb = json.load(io.open("fleet/machines/bm-c.json", encoding="utf-8"))
hb["last_seen"] = ts
hb["ts"] = ts
hb["clock_read"] = ts
hb["heartbeat_epoch_utc"] = int(time.time())
hb["did"] = ("r1216: W318 prereg frozen (canon-clone off W317 post-run face; 45 keys / 90 band tokens +2200 / "
             "4 chains extended; banned gate ADMIT)")
hb["did_round"] = round_no
hb["current"] = "r1216 closed: W318 prereg frozen at the chain head; engine idle until the five-face splice"
hb["current_task"] = "W318 prereg frozen; five-face splice next"
hb["current_task_at"] = ts
hb["next"] = "r1217: W318 five-face splice (registry row 318 / WAVE_CONFIGS / N1_BANDS) -> engine 12/12"
hb["next_pointer"] = "r1217 W318 five-face splice (editor off _w317bmc_freeze_edits.py)"
hb["next_milestone"] = "W318 registered and 12/12 shards burned, then finalize (<=48h)"
hb["last_artifact"] = "research/PERPETUAL_N1_W318_PREREG.md"
hb["last_artifact_at"] = ts
hb["recent_artifact"] = "research/PERPETUAL_N1_W318_PREREG.md"
hb["latest_artifact"] = "research/PERPETUAL_N1_W318_PREREG.md"
hb["round"] = round_no
hb["round_no"] = round_no
hb["round_no_label"] = "r1216 W318 prereg frozen -> next r1217 splice"
hb["last_round"] = round_no
hb["last_round_at"] = ts
hb["last_round_closed"] = round_no
hb["last_round_closed_at"] = ts
hb["last_round_label"] = "r1216"
hb["last_round_summary"] = (
    "r1216 | W318 PREREG FROZEN: canon-clone of the W317 post-run face (231c6f902f) -> "
    "research/PERPETUAL_N1_W318_PREREG.md 28,796B/75 lines/sha16 c77e004753fb06fc; 45 keys + 90 band tokens +2200 "
    "(A 714_901..716_900 / B 716_901..717_100) + 4 chains extended; banned gate ADMIT; smoke 57/57; zero S0.5 delta.")
hb["last_round_summary_at"] = ts
hb["verdict"] = "GREEN"
hb["status"] = "green"
hb["health"] = "green"
hb["verify"] = ("W318 prereg sha16 c77e004753fb06fc | banned ADMIT | smoke 57/57 | attrition CLEAN | orphan 0 | "
                "engine queue idle")
hb["ram_free_gb"] = 3.8
hb["idle_ram_gb"] = 3.8
hb["gpu_util_pct"] = 8
hb["gpu_mem_used_mib"] = 3259
hb["gpu_mem_total_mib"] = 16384
hb["gpu_free_mem_mib"] = 16384 - 3259
hb["gpu_face"] = "idle -- 3259/16384 MiB at 8% util; n1 engine is CPU-only, no GPU claim"
hb["cpu_pct"] = 28.0
hb["cpu_idle_pct"] = 72.0
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["pending"] = []
io.open("fleet/machines/bm-c.json", "w", encoding="utf-8", newline="").write(
    json.dumps(hb, ensure_ascii=False, indent=1))

# self-proof
d = json.load(io.open("fleet/machines/bm-c.json", encoding="utf-8"))
assert isinstance(d["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in d["clock_read"], "clock_read must be T-separated"
print("CLOSEOUT OK", ts, "epoch", d["heartbeat_epoch_utc"], "round", d["round"])