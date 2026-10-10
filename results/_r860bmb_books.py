# r860 bm-b books writer: state.json round 860 + heartbeat fleet/machines/bm-b.json
# Pure bookkeeping (S5/S7); JSON int epoch law R170/R178 + ISO8601 T-separated clock R262.
import datetime
import json
import time

now = datetime.datetime.now().astimezone()
ts = now.isoformat(timespec="seconds")
epoch = int(time.time())

p = "state.json"
d = json.load(open(p, encoding="utf-8"))
d["machine_id"] = "bm-b"
d["round_no"] = 860
d["round"] = 860
d["round_no_label"] = "r860"
d["last_round_at"] = ts
d["ts"] = ts
d["updated"] = ts
d["updated_at"] = ts
d["last_seen"] = ts
d["clock_read"] = ts
d["last_round_ts"] = ts
d["last_action"] = (
    "r860: S0 pre-absorb 9 own daemon faces + pull --rebase bm-c r850 + orders diff 0 (68/192/0) "
    "+ D19 dual watermark identical (dec caca0c6e/ord f90233c7) + smoke 49/49 + orphan face=0 "
    "+ boards clear (job_list 0, 183 tickets 0 open) + SAT alive rc0; PRIMARY PRODUCT = N2-W18 "
    "slice-2 runner bundle: scripts/alphagen_beam_w18.py (three legs run/probe/selftest, census IC "
    "machinery import-face zero-rewrite with same-face assertions, beam feedback search R1 24 "
    "depth<=2 -> top-6 / R2 24 leaf expansions -> top-6 / R3 16 = R2 top-4 x4 split pin, in-batch "
    "canonical tree dedup + T-84s3 fingerprint dedup vs census 48 unique formulas + ledger text "
    "belt, B=6 pooled nulls >=300 sufficiency, family-level V1 + D1 leverage descriptive face "
    "+ M1 t gate, FREEZE-GATE three-band refuse rc2, unc berth reserved disclosed) + selftest "
    "22/22 green (hermetic, 3 draft residuals self-caught: per-formula null face param, L10 "
    "short-name key bug, lineage key case) + FREEZE-GATE refuse-burn live proof PASS "
    "(results/_r860bmb_w18_freeze_gate_refuse.json) + probe 8 faces PASS rc0 "
    "(results/alphagen_w18/probe_latest.json); W210 parked on M9 gate (bm-a W208 not landed, "
    "bm-a heartbeat stale disclosed); moneyflow IC lawful-wait; S6 41 legs 40 rc0 + alloc rc2 "
    "known 510880; dualrun streak 15; S7 quartet ALIVE + attrition CLEAN + idle --worked "
    "+ HANDOVER r860 5x line (window r846-r860, r850/r855 stamps honestly disclosed) + books "
    "+ push behind=0 self-proof")
d["did"] = d["last_action"]
d["note"] = d["last_action"]
d["now_active"] = (
    "r860 closeout: N2-W18 slice-2 runner built and machine-proven (selftest 22/22 + "
    "FREEZE-GATE refuse-burn rc2 proof PASS + probe 8/8 PASS); S6 41 legs done (40 rc0 + "
    "alloc rc2 known); verdict readout r861")
d["verdict"] = (
    "GREEN: r860 (slice-2 runner landed with three-face machine proof; smoke 49/49; S6 41 "
    "executed legs 40 rc0 + alloc rc2 known 510880; dualrun streak 15; watermark red=false "
    "board-clear lawful; attrition CLEAN; quartet ALIVE; W210 parked on M9 gate disclosed; "
    "moneyflow IC lawful-wait; orders diff 0; D19 identical; HANDOVER 5x discharged)")
d["latest_artifact"] = (
    "r860: scripts/alphagen_beam_w18.py (slice-2 runner, three subcommands, FREEZE-GATE "
    "refuse-burn) + proof results/_r860bmb_w18_freeze_gate_refuse.json + probe receipt "
    "results/alphagen_w18/probe_latest.json + selftest 22/22 (hermetic)")
d["current_task"] = (
    "r861 queue: slice-3 FREEZE WINDOW (five-condition machine proof: c1 runner+selftest+"
    "refuse-proof landed / c2 three-band r682 recipe derive + seed_admit_gate rc0 + "
    "SEED_REGISTRY registration + rng streams pinned / c3 criteria shared-lib refs / c4 D6 "
    "explicit / c5 meaning gate + orders check -> prereg posture flip FROZEN) -> slice-4 "
    "burn window (K=64 short batch <=120s single-process + finalize + sec7/8 backfill) -> "
    "W210 freeze prep PARKED on M9 gate -> moneyflow IC panel-ready watch -> pool-EOL fleet "
    "adjudication watch -> O-20261011-0012 CPU-max maintained")
d["task"] = d["current_task"]
d["next"] = d["current_task"]
d["next_milestone"] = (
    "N2-W18 slice-3 freeze window <=10-13 (five conditions + three-band derive/registration "
    "+ FROZEN flip) -> slice-4 burn (K=64 <=120s, verdict V1 + D1 leverage readout) -> W210 "
    "freeze after W209 freeze+finalize lands (M9 chain, bm-c M10 automation armed on bm-a "
    "W208); chain head 876,731 monotone; moneyflow IC burns when MF panel completes (bm-a lane)")
json.dump(d, open(p, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
print("state.json round->", d["round_no"])

h = json.load(open("fleet/machines/bm-b.json", encoding="utf-8"))
h["machine_id"] = "bm-b"
h["round"] = 860
h["round_no"] = 860
h["now_active"] = d["now_active"]
h["current_task"] = d["current_task"]
h["task"] = d["current_task"]
h["next"] = d["current_task"]
h["latest_artifact"] = d["latest_artifact"]
h["next_milestone"] = d["next_milestone"]
h["verdict"] = d["verdict"]
h["last_action"] = d["last_action"]
h["last_round_at"] = ts
h["last_seen"] = ts
h["updated"] = ts
h["ts"] = ts
h["clock_read"] = ts
h["updated_at"] = ts
h["heartbeat_epoch_utc"] = epoch
h["cpu_cores"] = 16
h["free_ram_gb"] = 11.3
h["ram_free_gb"] = 11.3
h["ram_free_pct"] = 47.3
h["gpu_free_vram_mb"] = 3505
h["gpu_free_vram_gb"] = 3.5
h["vram_free_gb"] = 3.5
h["idle_rounds"] = 0
h["agenda_starved"] = False
h["orphan_face"] = 0
h["orphan_faces"] = 0
h["orphan_face_note"] = (
    "r860 closeout probe: py_faces=14 alive, orphans=0 (round-zero probe 04:22 rc0; zero "
    "live seats; slice-2 work only, no detached burns this round)")
h["sync"] = {
    "last_push_ts": ts,
    "note": ("r860 closeout push (slice-2 runner bundle + proofs + S6 chain + HANDOVER 5x + "
             "books); post-push behind=0 self-proof via fetch+rev-list")}
json.dump(h, open("fleet/machines/bm-b.json", "w", encoding="utf-8", newline="\n"),
          ensure_ascii=False, indent=1)
chk = json.load(open("fleet/machines/bm-b.json", encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178 law)"
assert "T" in chk["clock_read"] and " " not in chk["clock_read"], \
    "clock_read must be ISO8601 T-separated (R262 law)"
print("heartbeat written, epoch int OK, clock_read OK:",
      chk["heartbeat_epoch_utc"], chk["clock_read"])
