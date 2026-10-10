# -*- coding: utf-8 -*-
# r857 bm-b heartbeat closeout: round 856 -> 857, real-clock stamps, int epoch.
import json, time

P = "fleet/machines/bm-b.json"
d = json.load(open(P, encoding="utf-8"))
now = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())

d["round"] = 857
d["round_no"] = 857
d["now_active"] = ("r857 closeout: W207 FINALIZE landed (ledger 870,371+2,200=872,571, merged pool K=453,320, mu=-0.0927 sigma=0.2451, K-lift -0.0001; product n1_w207_results.json + finalize MSG-20261011-0316 published) + W210 SEAT published=reserved (A 476_804..478_803 / B 478_804..479_003, probe rc0 ADMIT, staircase 70th live-fired as W209 seat projected); T23 watcher readout carries to r858 (window ends 03:27:24 after closeout)")
d["current_task"] = ("r858 queue: T23 watcher receipt readout (fired -> census burn watch -> holds verdict <=10-11 06:00; timeout -> quarantine carryover + re-arm: move stale receipt before re-spawn per single-flight law) -> W210 freeze prep PARKED on M9 gate (W209 freeze+finalize pending bm-c side; W210 prereg draft admissible now) -> holds: N2 U3(1) prereg / G2 fallback -> moneyflow IC unlock parked (astock complete flip precondition) -> pool-EOL fleet adjudication watch -> O-20261011-0012 CPU-max maintained (engine queue dry until W209 gate opens; T23 astock tail = current CPU contribution) -> W18 drain-gated (bm-a owns w17-judge)")
d["task"] = d["current_task"]
d["next"] = d["current_task"]
d["latest_artifact"] = ("r857: results/perpetual_faces/n1_w207_results.json (W207 finalize, ledger 872,571/K 453,320) + fleet/inbox/MSG-20261011-0316-bmb-w207-finalize.md (M9 gate advance) + fleet/inbox/MSG-20261011-0319-bmb-w210-seat.md (W210 seat reserved, A 476_804..478_803/B 478_804..479_003) + results/_w210bmb_20261011_probe_receipt.json (pre-seat probe rc0 ADMIT)")
d["next_milestone"] = ("T23 census_holds verdict <=10-11 06:00 (watcher window ends 03:27:24 -> r858 reads receipt) -> W208/W209 freezes (bm-a/bm-c) then W210 freeze-prep when M9 gate opens; chain head=872,571; pool-EOL fleet adjudication pending")
d["verdict"] = ("GREEN: r857 (W207 finalize = primary product landed+verified ledger head 872,571 exact +2,200; W210 seat = second product queue-deepen landed; smoke 49/49; S6 40/41 rc0 + alloc rc2 known 510880 P5 slot; tasks ALIVE; attrition CLEAN; round-report append surgery incident caught+repaired in-window byte-identical, pit direct-written pit-encoding.md)")
d["last_action"] = ("r857: S0 fetch+FF merge d31f4eaa1->e989c03eb (bm-c r847 W209 seat) + orders diff zero both scans (68/192/0) + D19 dual watermark identical (dec caca0c6e/ord f90233c7) + smoke 49/49 + orphan 1 (T23 watcher intentional seat); S2 board clear (job 0, ticket 0 open, watermark green next_pick=claimed moneyflow IC parked); S3 W207 12/12 burn done @02:51:04 -> FINALIZE LANDED (ledger 870,371+2,200=872,571, K 451,120+2,200=453,320, merged mu=-0.0927 sigma=0.2451, skill_line_v2 K-lift -0.0001, voids LOWAMP-P1/P2, evidence_cutoff=2026-09-22) + finalize MSG published (M9 gate advance W208/W209 freezers, W209 anchor->W207 finalize actuals + freeze-time guard mandate) + W210 SEAT published (probe _w210bmb_20261011_probe.py rc0 ADMIT: A 476_804..478_803 hops=1 staircase 70th + B 478_804..479_003 hops=1 own-A mutual exclusion; W208+W209 declared bands origin-text-verified injected; seed_admit_gate both FREE; conflicts 0; vacancy four-check held; W211+ projection logged; freeze GATED on W209 freeze+finalize per M9 chain-order); T23 watcher alive to 03:27:24 (astock 5219/5229 refresh incomplete) -> readout carries to r858 per receipt design; S6 41 legs 40 rc0 + alloc rc2 known (verbatim clone _r857bmb_s6chain.ps1); S7 quartet ALIVE (loop pin=2 no-op, watchdog idempotent re-register, dual claws identical) + attrition CLEAN (4 ledger files, 3 healed history notes) + idle --worked; round-report append surgery incident (replace old_string hit r856 addendum line prefix + EOL normalization of 2 LF lines) caught by self-check, restored via git checkout (zero other local deltas), re-appended byte-face, git diff -U0 = exactly 1 insertion; pit entry 883B direct-written research/pit-encoding.md per r666 exception (main CODELY.md 30,510B red-line); commit+push behind=0 self-proof")
d["did"] = d["last_action"]
d["last_round_at"] = now
d["last_seen"] = now
d["updated"] = now
d["updated_at"] = now
d["ts"] = now
d["clock_read"] = now
d["heartbeat_epoch_utc"] = epoch
d["cpu_cores"] = 16
d["free_ram_gb"] = 11.9
d["ram_free_gb"] = 11.9
d["ram_free_pct"] = 41.2
d["gpu_free_vram_mb"] = 3512
d["gpu_free_vram_gb"] = 3.5
d["vram_free_gb"] = 3.5
d["idle_rounds"] = 0
d["agenda_starved"] = False
d["orphan_faces"] = 1
d["orphan_face_note"] = ("round-zero probe 03:04 py_faces=9 orphans=1 (pid23124 = r854 T23 autofire watcher, intentional detached seat mid-mission to 03:27:24; three-face positive incl. cpu-stalled = sleep-between-polls artifact, poll log alive 03:12:28; read-only probe, not collected per mission-arm law; readout carries to r858)")
d["sync"] = {"last_push_ts": now, "note": "r857 closeout push (W207 finalize + W210 seat + round report + heartbeat); post-push behind=0 self-proof via fetch+ls-remote"}

json.dump(d, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(P, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert chk["round_no"] == 857
print("heartbeat ok: round=857 epoch=%d clock=%s" % (chk["heartbeat_epoch_utc"], chk["clock_read"]))
