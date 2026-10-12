# -*- coding: utf-8 -*-
# r951 closeout writer: state-bm-c.json + heartbeat + round report line
import json, time, io

NOW = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

DID = ("r951 (absorb continuation): (1) S0-1 anchor bm-c + round-zero probe py_faces=7 orphans=2 zero-kill "
       "(factory PID 37904 = i2v poller false-positive kept; album_serve kept); S0 state-sync commit ccf5c5221 "
       "+ pull --rebase up-to-date; (2) S0.5 dual-delta FALSE both hold (dec fb5825cb / ord a8d9efaf, unacked=0, "
       "probe rc0); (3) S1 smoke 49/49; S2 boards clear (jobs 0); satengine alive rc0; watermark red=false "
       "lane=healthy next_pick=claimed; (4) ABSORB dead r951 session (QC-r951.json 02:13: C02_v2 5.5 FAIL + "
       "C03 3.0 FAIL frame-level Kufic root cause + 12-frame pre-burn sweep ALL PASS + C02_v3 reshake submitted "
       "02:09:53 which landed) -- this session executed as r951 continuation per absorb precedent, counter "
       "951->952; (5) PRODUCT-1: 6-clip video QC verdicts (ffmpeg 4-6 frames/clip + PIL contact sheets + "
       "multimodal 4-eye): C02_v3 6.4 FAIL (origin healed, translucent liquid curtain remains t=2.1-2.9s, "
       "trajectory 5.5->5.5->6.4), C04 7.0 FAIL borderline (camera-drift concept deviation + hub wedge morph), "
       "C05 8.8 PASS locked, C06 6.5 FAIL (taffy chip 3.2s + dark mass 4.4s), C07 7.1 FAIL (zero sink motion + "
       "white horizon palette breach), C08 8.3 PASS locked; (6) PRODUCT-2: 4-clip reshake rider "
       "bmc_reshake_r951b.py launched background PID 27720 (sequential self-interleave submission; C02_v4 seed "
       "9209 SUBMITTED 03:05:10 behind burning R01; C04_v2/C06_v2/C07_v2 seeds 9210-9212 queue behind; "
       "positive-phrasing prompt fixes per QC dimensions); (7) PRODUCT-3: QC-r951b.json landed bmc dir; (8) C03 "
       "track decision: track-1 bm-a MSG dead-legged (never landed in any inbox, zero bm-a artifacts) -> "
       "track-2 self-regen ARMED as primary (post-drain model swap H3->Krea2, ~05:00-05:45; deathline "
       "discipline: if slip past ~05:30 disclose C03 FAIL at closeout, director decides retime/omit); (9) "
       "factory: C09 landed 03:0x + R01 burning + C02_v4 behind (index 30 rows); (10) S6 light: dualrun "
       "ZERO-DRIFT streak 44 + compute_audit FLAG pool_starvation/supply_floor structural (W227 armed RAM "
       "0.7G<4G gate, i2v deathline lane legitimate) + py_watermark insufficient_history honest + update_daily "
       "0 new rows pre-15:30 legal + market_regime ORANGE shadow rc0 + token delta 0; (11) S7: idle --worked "
       "cleared + attrition 4 CLEAN + loop pin=5 no-op + watchdog re-registered + precommit/prepush claws "
       "reinstalled + temp QC frames cleaned (regenerable); (12) state/heartbeat/report r951 write")

VERDICT = ("green: 6-clip QC verdicts landed (C05 8.8 + C08 8.3 PASS locked; C02_v3 6.4/C04 7.0/C06 6.5/C07 7.1 "
           "FAIL each with surgical reshake fix in rider) + reshake rider PID 27720 sequential self-interleave "
           "(C02_v4 submitted behind burning R01) + factory healthy (C09 landed, R01 burning, R02-R06 + 3 rider "
           "reshakes queued, index 30 rows, ETA drain ~05:00-05:45) + C03 track-2 self-regen armed post-drain + "
           "smoke 49/49 + dual-delta FALSE hold + dualrun streak 44; pool_starvation/supply_floor structural "
           "disclosed (W227 armed, RAM-gated, GPU deathline lane); no new bars until Tue 15:30")

NEXT = ("r952: (1) i2v harvest patrol: R-series landings + rider reshake landings QC per patrol law (<7.5 "
        "reshake); (2) C03 track-2: after batch drain (~05:00-05:45) model swap H3->Krea2 + frame regen (PROPS "
        "wedge anchor) + i2v C03_v2 -- if drain slips past ~05:30, disclose C03 FAIL at closeout; (3) 06:30 "
        "closeout checklist: 21/21 tally + final QC sweep + index final commit+push; (4) W227 seat "
        "probe+publish FIRST ACTION after RAM relief (free_ram>=4G; probe script "
        "results/_w227bmc_probe_derive.py on disk); (5) Tue 15:30 new-bar papers full chain + update family")

CURTASK = ("r951: 6-clip QC verdicts (C05 8.8 PASS / C08 8.3 PASS / C02_v3 6.4 / C04 7.0 / C06 6.5 / C07 7.1 "
           "FAIL) + 4-clip reshake rider PID 27720 (C02_v4 burning behind R01) + C03 track-2 armed")

ARTIFACT = ("QC-r951b.json (bmc dir, 6 verdicts + rider + C03 track decision) + bmc_reshake_r951b.py + "
            "I2V-URL-INDEX 30 rows (C09+R01 in flight) + results/_r951bmc_qc_sheet{1,2}.png")

PROD = ("GPU=CEO deathline i2v 21-shot batch: 15/21 landed (N01-N07+C02-C09 + reshakes v2/v3) + R01 burning "
        "+ C02_v4 rider behind + R02-R06 + C04/C06/C07 v2 self-interleaved, factory PID 37904 INT8 768P, "
        "06:30 closeout 08:30 CEO screen; CPU=N1 W226 complete, W227 seat RAM-arbitration-deferred per "
        "O-20261012-2330-2 (i2v priority, freeRAM 0.7G < 4G gate)")

R951_NOTE = ("r951 absorb note: prior dead session (labeled r951, died ~02:2x post-QC pre-closeout; heartbeat "
             "still r950, counter still 951) executed: C02_v2 + C03 video QC verdicts (QC-r951.json), 12-frame "
             "pre-burn sweep of C04-C09+R01-R06 vs PROPS cuneiform canon (0 hard fails, 3 ADVISORY), C02_v3 "
             "reshake submission 02:09:53 (landed), and PLANNED a bm-a MSG (never landed in any inbox) + C03 "
             "dual-track; this session absorbed per bm-c r894/r897/r907 absorb precedent: executed as r951 "
             "continuation, advanced counter 951->952; zero double-count: S0.5 dual-delta FALSE this window "
             "(dec fb5825cb / ord a8d9efaf both current)")

COMMON = {
    "round_no": 952, "round_no_label": "r951", "last_round": 951, "loop_round": 951,
    "last_round_at": NOW, "last_seen": NOW, "ts": NOW, "updated": NOW, "updated_at": NOW,
    "clock_read": NOW, "last_round_closed": NOW, "last_action_at": NOW,
    "last_round_summary_at": NOW, "current_task_at": NOW, "last_run_at": NOW,
    "last_pulled_at": NOW, "last_round_ts": EPOCH, "heartbeat_epoch_utc": EPOCH,
    "current_task": CURTASK, "did": DID, "verdict": VERDICT, "next": NEXT, "next_pointer": NEXT,
    "latest_artifact": ARTIFACT, "last_artifact": ARTIFACT, "recent_artifact": ARTIFACT,
    "next_milestone": ("R-series + rider reshakes drain ~05:00-05:45 -> C03 track-2 regen+QC -> 06:30 closeout "
                       "tally (21/21 + final QC + index commit) -> bm-a 07:00 assembly -> 08:30 CEO screen "
                       "(deathline) + W227 seat after RAM relief"),
    "prod_lanes": PROD, "orphan_face": 2, "orphan_faces": 2,
    "activity_now": ("2026-10-13 03:0x | r951 | bm-c: 6-clip QC (C05 8.8/C08 8.3 PASS; C02_v3 6.4/C04 7.0/C06 "
                     "6.5/C07 7.1 FAIL) + 4-reshake rider PID 27720 (C02_v4 submitted) + C03 track-2 armed; "
                     "counter 951->952"),
    "now_active": ("2026-10-13 03:0x | r951 | bm-c: 6-clip QC (C05 8.8/C08 8.3 PASS; C02_v3 6.4/C04 7.0/C06 "
                   "6.5/C07 7.1 FAIL) + 4-reshake rider PID 27720 (C02_v4 submitted) + C03 track-2 armed; "
                   "counter 951->952"),
    "last_round_summary": ("r951: 6-clip QC (2 PASS locked / 4 FAIL surgical-reshake) + 4-clip reshake rider "
                          "launched + C03 track-2 armed + factory C09 landed R01 burning"),
    "last_action": "r951 closeout (QC-r951b receipts + reshake rider launch + C03 track decision + S6 light + S7 quad)",
    "orders_ack_receipt": "r951: dual-delta FALSE hold (dec fb5825cb / ord a8d9efaf), unacked=0, zero consumption owed this window",
    "r951_absorb_note": R951_NOTE,
    "free_ram_gb": 0.7, "ram_free_gb": 0.7, "idle_ram_gb": 0.7,
    "gpu_free_vram_mb": 3679, "gpu_free_vram_mib": 3679, "gpu_vram_free_mb": 3679,
    "gpu_idle_vram_mb": 3679, "gpu_idle_vram_mib": 3679, "gpu_free_mib": 3679, "gpu_free_mb": 3679,
    "gpu_used_vram_mib": 12705, "gpu_mem_used_mib": 12705, "gpu_util_pct": 100,
    "cpu_pct": 28.0, "cpu_util_pct": 28.0, "cpu_idle_pct": 72.0,
    "idle_rounds": 0, "agenda_starved": False, "health": "ok",
    "last_orders_sha_note": "r951: ORD delta FALSE hold (a8d9efaf current, zero new rows)",
    "last_decisions_read_note": "r951: DEC delta FALSE hold (fb5825cb current)",
    "last_orders_seen": NOW, "last_decisions_seen": NOW,
}

for path in (ROOT + r"\state-bm-c.json", ROOT + r"\fleet\machines\bm-c.json"):
    with io.open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    data.update(COMMON)
    if "machine_id" not in data:
        data["machine_id"] = "bm-c"
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print("WROTE", path, "round_no=", data["round_no"], "epoch_int=", isinstance(data["heartbeat_epoch_utc"], int))

line = ("%s | r951 | absorb r951 dead session + 6-clip QC (C05 8.8/C08 8.3 PASS locked; C02_v3 6.4/C04 7.0/"
        "C06 6.5/C07 7.1 FAIL) + 4-reshake rider PID 27720 (C02_v4 submitted behind R01) + C03 track-2 armed "
        "(post-drain self-regen) + factory C09 landed R01 burning index 30 | smoke 49/49 + dual-delta FALSE "
        "(dec fb5825cb/ord a8d9efaf) + dualrun streak 44 + S6 light rc0 (audit FLAG structural disclosed) + "
        "attrition 4 CLEAN + 孤儿面=2 zero-kill | r952: R-series+rider QC patrol + C03 post-drain regen + 06:30 "
        "closeout tally + W227 after RAM relief\n" % NOW)
with io.open(ROOT + r"\logs\iteration-loop\round_reports-bm-c.md", "a", encoding="utf-8") as f:
    f.write(line)
print("REPORT_APPENDED")
