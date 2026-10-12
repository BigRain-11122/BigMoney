# r952 closeout: append round report line (tail-anchored) + state/heartbeat updates
import json, time, datetime

# ---- round report line ----
RP = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\logs\iteration-loop\round_reports-bm-c.md"
with open(RP, encoding="utf-8") as f:
    lines = f.read().splitlines()
assert lines and lines[-1].strip().startswith("2026-10-13T03:08:25") and "r951" in lines[-1], "tail anchor drift: " + (lines[-1][:80] if lines else "EMPTY")

now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
row = now + " | r952 | bm-c harvest patrol: 3-clip QC verdicts (R01_war_later 8.0 PASS locked / C02_sand_bury_v4 7.3 FAIL disclosed trajectory 5.5/5.5/6.4/7.3 / C09_oath_weather 3.5 FAIL CRITICAL zero-humans frame-level) + C09 merged into track-2 frame-regen batch with C03 + factory R02 burning rider C04_v2 burning (R03-R06 + C06_v2/C07_v2 queued, drain ~04:30-05:00) | smoke 49/49 + ORD delta TRUE consumed a8d9efaf->ce3cfa1d (single row 10-13 03:3x MiniMax midnight-jam Seedance rescue wave 15/15 cloud-lane bm-a exec; bm-c face=local line 15/21 confirmed zero new action; dec fb5825cb FALSE hold; unacked=0) + dualrun streak 45 + compute_audit FLAG structural disclosed (pool_starvation/supply_floor W227 RAM-gated 1.4G<4G i2v deathline lane legitimate per O-2330-2) + py_watermark py_low_with_work_cands (legal occupant = i2v local batch) + attrition 4 CLEAN + S7 quad green (pin=5 no-op + watchdog + claws x2) | r953: (1) R02-R06 + C04_v2/C06_v2/C07_v2 landing QC per patrol law; (2) post-drain track-2: model swap H3->Krea2 + regen C03 (PROPS wedge) + C09 (two-person oath meander<=30%) frames + i2v both -- deathline discipline if past ~05:30 disclose FAIL; (3) 06:30 closeout tally 21/21 + index final push; (4) W227 seat first action after RAM relief (>=4G); (5) Tue 15:30 new-bar papers full chain | [r952 bm-c]"
with open(RP, "a", encoding="utf-8", newline="\n") as f:
    f.write(row + "\n")
print("RP appended")

# ---- state update ----
ST = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\state-bm-c.json"
d = json.load(open(ST, encoding="utf-8"))
d["round_no"] = 953
d["last_round"] = 952
d["round_no_label"] = "r952"
d["loop_round"] = 952
ts = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())
for k in ["clock_read", "ts", "updated", "updated_at", "last_seen", "last_round_at", "last_round_closed", "last_action_at", "last_run_at", "last_pulled_at", "now_active_ts", "last_decisions_seen", "last_orders_seen"]:
    if k in d: d[k] = ts
d["heartbeat_epoch_utc"] = epoch
d["last_ts"] = epoch
d["last_round_ts"] = epoch
d["last_orders_sha"] = "ce3cfa1dc1f8dcf6ae0e40cfe9e7740fdfe5b6cd962c4fcd0934fbb015e3518b"
d["last_orders_sha_method"] = "sha256 origin blob fresh-read r952 (Seedance rescue row consumed, zero BigMoney action)"
d["last_orders_read_at"] = ts
d["last_orders_read_note"] = "r952: ORD delta TRUE consumed (a8d9efaf->ce3cfa1d, 1 row: 10-13 03:3x MiniMax jam verdict + Seedance rescue wave, cloud lane bm-a exec, bm-c local line confirmed)"
d["orders_ack_receipt"] = "r952: ORD delta TRUE consumed (ce3cfa1d), single row Seedance rescue cloud-lane, zero bm-c action owed; unacked=0; dec fb5825cb FALSE hold"
d["last_round_summary"] = "r952: harvest QC R01 8.0 PASS locked / C02_v4 7.3 FAIL disclosed (director fallback pre-decision) / C09 3.5 FAIL critical (frame-level zero-humans, pre-burn ADVISORY materialized) -> C09 merged into C03 track-2 regen batch"
d["last_round_summary_at"] = ts
d["current_task"] = "r952: harvest QC done (R01 PASS locked; C02_v4 7.3 disclosed; C09 3.5 frame-level) + C09->track-2 regen batch merge + factory R02 burning rider C04_v2 burning"
d["current_task_at"] = ts
d["last_action"] = "r952 closeout (QC-r952.json + sheets + watermark ORD advance + S6 light + S7 quad)"
d["last_action_at"] = ts
d["latest_artifact"] = "bmc/QC-r952.json (3 verdicts + C09 root-cause + assembly slot state) + results/_r952bmc_qc_sheet{1,2}.png + results/_r952bmc_qc_extract.py"
d["last_artifact"] = d["latest_artifact"]
d["recent_artifact"] = d["latest_artifact"]
d["activity_now"] = "2026-10-13 03:3x | r952 | bm-c: harvest QC (R01 8.0 PASS locked / C02_v4 7.3 disclosed / C09 3.5 frame-level FAIL) + C09 merged into track-2 regen; counter 952->953"
d["now_active"] = d["activity_now"]
d["next"] = ("r953: (1) R02-R06 + C04_v2/C06_v2/C07_v2 landing QC per patrol law (<7.5 reshake); "
             "(2) post-drain track-2: model swap H3->Krea2 + regen C03 (PROPS wedge anchor) + C09 (two-person mid-shot oath, meander wall background <=30%) + swap back + i2v both -- deathline: past ~05:30 disclose C03/C09 FAIL at closeout, director decides retime/omit; "
             "(3) 06:30 closeout checklist: 21/21 tally + final QC sweep + index final commit+push; "
             "(4) W227 seat probe+publish FIRST ACTION after RAM relief (free_ram>=4G; probe script results/_w227bmc_probe_derive.py on disk); "
             "(5) Tue 15:30 new-bar papers full chain + update family")
d["next_pointer"] = d["next"]
d["next_milestone"] = "R-series+rider drain ~04:30-05:00 -> track-2 C03+C09 frame regen + i2v -> 06:30 closeout tally (21/21 + index final push) -> bm-a 07:00 assembly -> 08:30 CEO screen (deathline) + W227 seat after RAM relief"
d["verdict"] = ("green: 3-clip harvest QC verdicts landed (R01_war_later 8.0 PASS locked; C02_sand_bury_v4 7.3 FAIL disclosed per pre-decision, director falls back to best segment/trim; "
                "C09_oath_weather 3.5 FAIL CRITICAL frame-level zero-humans -> merged into track-2 regen batch with C03) + factory healthy (R02 burning 792s, rider C04_v2 burning 361s, R03-R06 + C06_v2/C07_v2 queued, drain ~04:30-05:00) + "
                "smoke 49/49 + ORD delta consumed (Seedance rescue row, cloud-lane informational) + dualrun streak 45 + attrition CLEAN + S7 quad green; "
                "pool_starvation/supply_floor structural disclosed (W227 armed RAM-gated 1.4G<4G, i2v deathline lane legitimate per O-20261012-2330-2); no new bars until Tue 15:30")
d["idle_rounds"] = 0
d["agenda_starved"] = False
d["free_ram_gb"] = 1.4
d["ram_free_gb"] = 1.4
d["idle_ram_gb"] = 1.4
d["gpu_free_vram_mib"] = 779
d["gpu_free_vram_mb"] = 779
d["gpu_free_vram_gb"] = 0.8
d["gpu_mem_used_mib"] = 15605
d["gpu_used_vram_mib"] = 15605
d["gpu_util_pct"] = 100
d["prod_lanes"] = ("GPU=CEO deathline i2v 21-shot batch: 16/21 landed+QC'd (N01-N07 7/7 + C02-C09 + reshakes v2/v3/v4) + R01 landed 8.0 PASS + R02 burning + R03-R06 queued + rider C04_v2 burning + C06_v2/C07_v2 queued, factory PID 37904 INT8 768P; "
                   "C02 best-of v4 7.3 disclosed (assembly fallback = director segment/trim); C03+C09 track-2 frame-regen batch armed post-drain; 06:30 closeout 08:30 CEO screen; "
                   "CPU=N1 W226 complete, W227 seat RAM-arbitration-deferred per O-20261012-2330-2 (i2v priority, freeRAM 1.4G < 4G gate)")
d["r952_closeout_note"] = ("r952: (1) S0-1 anchor bm-c + round-zero probe py_faces=10 orphans=2 zero-kill; state-sync commit 0087dcf85 + pull --rebase up-to-date; "
                           "(2) S0.5 ORD delta TRUE consumed (a8d9efaf->ce3cfa1d single row = MiniMax midnight-jam verdict + Seedance rescue wave 15/15, cloud-lane bm-a director exec, bm-c local line 15/21 face confirmed, zero new bm-c action; dec fb5825cb FALSE hold; unacked=0); "
                           "(3) S1 smoke 49/49; S2 boards clear (jobs 0); (4) harvest QC: R01 8.0 PASS locked / C02_v4 7.3 FAIL disclosed (translucent gauze persists over carving, gold hairline, curly pseudo-cuneiform; trajectory 5.5/5.5/6.4/7.3; per QC-r951b pre-decision no v5, director falls back) / C09 3.5 FAIL CRITICAL (zero humans all frames; source frame verified 0 people; pre-burn meander-decor ADVISORY materialized; same class as C03); "
                           "(5) C09 merged into track-2 regen batch (post-drain swap H3->Krea2 + C09 two-person oath frame + C03 PROPS wedge frame + i2v both; deathline discipline shared); (6) QC-r952.json + 2 contact sheets + extract script landed; (7) S6 light: dualrun streak 45 + audit FLAG structural + wm py_low_with_work_cands legal; (8) S7 quad green; attrition 4 CLEAN; counter 952->953")
with open(ST, "w", encoding="utf-8") as f:
    json.dump(d, f, ensure_ascii=False, indent=1)
print("state written, epoch int check:", isinstance(d["heartbeat_epoch_utc"], int))

# ---- heartbeat ----
HB = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\fleet\machines\bm-c.json"
h = json.load(open(HB, encoding="utf-8"))
h["machine_id"] = "bm-c"
h["last_seen"] = ts
h["ts"] = ts
h["heartbeat_epoch_utc"] = epoch
h["clock_read"] = ts
h["current_task"] = "r952: harvest QC done (R01 8.0 PASS / C02_v4 7.3 disclosed / C09 3.5 frame-level FAIL -> track-2 regen merge) + factory R02 burning + rider C04_v2 burning"
h["verdict"] = "green: i2v deathline batch in flight (16/21 landed+QC'd, R02 burning, drain ~04:30-05:00) + C03+C09 track-2 regen armed + boards clear + smoke 49/49"
h["cpu_cores"] = 32
h["free_ram_gb"] = 1.4
h["gpu_free_vram_mb"] = 779
h["gpu_util_pct"] = 100
h["idle_rounds"] = 0
h["agenda_starved"] = False
h["round_no"] = 953
h["loop_round"] = 952
h["last_round_summary"] = "r952: harvest QC R01 PASS locked / C02_v4 7.3 disclosed / C09 3.5 frame-level FAIL -> track-2 regen batch merge (with C03)"
h["now_active"] = d["activity_now"]
h["next"] = d["next"]
h["latest_artifact"] = d["latest_artifact"]
with open(HB, "w", encoding="utf-8") as f:
    json.dump(h, f, ensure_ascii=False, indent=1)
print("heartbeat written, epoch int check:", isinstance(h["heartbeat_epoch_utc"], int))
