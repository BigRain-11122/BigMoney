# -*- coding: utf-8 -*-
"""r813 bm-a takeover closeout: state increment + heartbeat + round report.

Single fresh read-modify-write per face (multi-writer file law: no replace-tool
appends on shared ledgers). Self-assertions: epoch int type, clock_read
T-separator, json roundtrip.
"""
import json
import time
from datetime import datetime, timezone, timedelta

NOW = datetime.now(timezone(timedelta(hours=8)))
TS = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())
R = 813


def cpu_ram():
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=1.0)
        ram = round(psutil.virtual_memory().available / (1024 ** 3), 1)
        return cpu, ram
    except Exception:
        return None, None


def gpu_free():
    try:
        import subprocess
        r = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.free",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=10)
        return round(float(r.stdout.strip().splitlines()[0]) / 1024, 1)
    except Exception:
        return None


CPU, RAM = cpu_ram()
GPU = gpu_free()

# ---- state-<id>.json -------------------------------------------------------
sp = "state-bm-a.json"
s = json.load(open(sp, encoding="utf-8"))
s.update({
    "round_no": R, "round": R, "loop_round": R, "last_round": "r813",
    "last_round_at": TS, "last_round_ts": EPOCH,
    "updated": TS, "ts": TS, "clock_read": TS, "last_seen": TS,
    "last_run": TS,
    "heartbeat_epoch_utc": EPOCH,
    "last_heartbeat_epoch_utc": s.get("heartbeat_epoch_utc", EPOCH),
    "did": ("r813 takeover closeout (dead-r813 session died post-push "
            "pre-S7; same-label takeover per r794 precedent): S0 5x "
            "churn-absorb + 29-UU rebase storm resolved per "
            "bigmoney-conflict-resolve skill (19/19 resolver + 6 ALL_FACES "
            "merge_lane_views, zero-loss) + S0.5 orders 163/163 zero-unack + "
            "DEC watermark consumed + S1 smoke 48/48 + S3 P0 W170 finalize "
            "one-pass (ledger 777,212->779,412 EXACT, K 371,920 EXACT, "
            "skill_line 1.1841->1.184) + sec7/sec8 same-window backfill + "
            "S6 38/38 rc0 (102s) + inbox 2 processed (w170-seat self-ack "
            "due + bmc-ALL trio-stall concur wait-bm-b)"),
    "current_task": ("r813 closed: W170 finalize landed origin 6c340dca4 "
                     "(bm-a 86th owned wave, 160th engine wave); W1..W170 "
                     "chain closed zero in-flight seats"),
    "last_action": ("W170 finalize one-pass + takeover closeout; next "
                    "r814 = W171 seat chain"),
    "next": ("r814 = W171 seat chain (pre-seat probe on post-W170 universe "
             "re-derive-MANDATORY: proj A 390_804..392_803 / B 391_004.."
             "391_203, naive-B-inside-naive-A same-window mutual-exclusion "
             "leg2, staircase A-hops-prior-B 30th instance pending machine "
             "verify) -> W171 freeze -> burn -> finalize (proj ledger "
             "781,612 / K 374,120); D-20261002-06 window 10-09 00:00 "
             "(CODELY main file 29,707B <=30,720B met, maintain)"),
    "verify": ("W170 finalize one-pass rc0 12/12 shards FAIL-CLOSED guards "
               "green; three-constant gate: ledger 779,412 EXACT proj hit / "
               "K 371,920 EXACT / skill_line 1.184 honest; S5 four "
               "prediction keys all pass (mu diff 0.0002<0.02, sigma "
               "-0.86%<10%, A p95 diff -0.0358<0.05, K-lift -0.0001<=0.02); "
               "smoke 48/48; S6 38/38 rc0 dualrun streak 51; engine alive "
               "rc0 (W170 burn 12/12 self-ignited 08:00:17..08:10:17); "
               "orders 163/163 zero unacked; attrition guard CLEAN; "
               "decisions watermark 77ffc880 consumed (D-20261002-06 "
               "criterion met locally 29,707B)"),
    "latest_artifact": ("results/perpetual_faces/n1_w170_results.json "
                        f"@{TS}"),
    "last_decisions_sha": ("77ffc880dbdfffd349e21ddf31f63a466c90d2b6"
                           "7927e7353a79b173218c8ce3"),
    "last_decisions_at": TS,
    "last_decisions_ts": TS,
    "last_orders_sha": ("f1b0cc59cffaad63b470ea4f079efda743b38736109"
                        "a45d13ebda9356ecd1ee8"),
    "last_orders_at": TS,
    "last_decisions_seen": "2026-10-07",
    "notes": ("r813 = takeover window (freeze session died post-push "
              "pre-S7, takeover same-label per r794 precedent); golden-"
              "week: engine idle verdict legal, market re-opens 10-09; "
              "bm-b dark 06:40.. revived evidence 08:12/08:16 keepalives "
              "(trio watch per bmc r663); round_reports r795..r812 lines "
              "missing on this file = dead-session windows (content in "
              "git log + state history)"),
})
json.dump(s, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
back = json.load(open(sp, encoding="utf-8"))
assert isinstance(back["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in back["clock_read"], "clock_read must be T-separated"

# ---- heartbeat fleet/machines/bm-a.json -------------------------------------
hp = "fleet/machines/bm-a.json"
h = json.load(open(hp, encoding="utf-8"))
h.update({
    "clock_read": TS, "ts": TS, "last_seen": TS, "last_run": TS,
    "heartbeat_epoch_utc": EPOCH,
    "last_heartbeat_epoch_utc": h.get("heartbeat_epoch_utc", EPOCH),
    "round": R, "round_no": R, "last_round": R,
    "current_task": ("r813 closed (takeover): W170 finalize landed; next "
                     "r814 = W171 seat chain"),
    "last_action": ("r813: W170 finalize one-pass (ledger 779,412 / K "
                    "371,920 EXACT) + 29-UU rebase-storm resolve + "
                    "takeover closeout"),
    "now_active": ("perpetual N1 line W1..W170 closed (ledger 779,412, K "
                   "371,920, zero in-flight seats); W171 seat chain next"),
    "latest_artifact": f"results/perpetual_faces/n1_w170_results.json @{TS}",
    "next_milestone": ("W171 seat+freeze+burn+finalize (proj ledger 781,612 "
                       "/ K 374,120, window<=48h); D-20261002-06 CODELY "
                       "main window 10-09 00:00 (29,707B met, maintain)"),
    "verdict": "green",
    "health": "ok",
})
if CPU is not None:
    for k in ("cpu_pct", "cpu_util_pct", "cpu_load_pct"):
        h[k] = CPU
if RAM is not None:
    h["free_ram_gb"] = RAM
    h["ram_free_gb"] = RAM
    h["idle_ram_gb"] = RAM
    h["idle_ram_mb"] = int(RAM * 1024)
if GPU is not None:
    for k in ("gpu0_free_vram_gb", "gpu_idle_vram_gb", "gpu_free_vram_gb",
              "gpu_vram_free_gb", "idle_gpu_vram_gb"):
        h[k] = GPU
    h["gpu_idle_vram_mib"] = int(GPU * 1024)
    h["gpu_free_vram_mib"] = int(GPU * 1024)
    h["gpu_free_vram_mb"] = int(GPU * 1024)
    h["gpu_idle_vram_mb"] = int(GPU * 1024)
json.dump(h, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
back = json.load(open(hp, encoding="utf-8"))
assert isinstance(back["heartbeat_epoch_utc"], int), "hb epoch must be int"
assert "T" in back["clock_read"], "hb clock_read must be T-separated"

# ---- round report append ----------------------------------------------------
rp = "fleet/round_reports-bm-a.md"
line = (
    f"{TS} | r813 | bm-a takeover of timeout-killed r813 closeout (dead "
    "session: W170 freeze pushed 08:00:02 then died pre-S7; same-label "
    "takeover r794 precedent): S0 5x churn-absorb + pull --rebase 29-UU "
    "storm resolved per bigmoney-conflict-resolve skill (classifier 24+5 "
    "UNKNOWN manual-classed; resolver _r813bma_resolve.py 19/19 snapshot "
    "deep-ts take-new + twins same-side byte-copy + x2_watch line-union "
    "839 zero-loss; 6 ALL_FACES via merge_lane_views resolve r377 canon) "
    "+ S0.5 orders 163/163 zero-unack + DEC watermark consumed sha "
    "77ffc880 (D-20261002-06 10-09 window: CODELY main file 29,707B "
    "<=30,720B criterion MET) + S1 smoke 48/48 + S3 saturation engine "
    "alive rc0 (W170 burn self-ignited post-freeze 12/12 shards "
    "08:00:17..08:10:17) + P0 W170 finalize one-pass (ledger 777,212->"
    "779,412 EXACT projection hit / K 369,720->371,920 EXACT / "
    "skill_line 1.1841->1.184 delta -0.0001 honest / A p95 0.2931 diff "
    "-0.0358<0.05 / se_mu 0.000402 / S5 four prediction keys all pass) "
    "+ PERPETUAL_N1_W170_PREREG sec7/sec8 same-window backfill (W169 "
    "precedent law) + S6 38/38 rc0 (102s, dualrun streak 51, golden-week "
    "no-ops honest) + inbox 2 processed (w170-seat self-ack due at "
    "finalize window + MSG-0801-bmc-ALL trio-stall consumed: concur "
    "wait-bm-b default, bm-a daemon keep-block refusals 1494/1022 = "
    "correct anti-poison face no action, bm-b revival evidence 08:12/"
    "08:16 origin keepalives) | evidence: results/perpetual_faces/"
    "n1_w170_results.json + research/PERPETUAL_N1_W170_PREREG.md sec7/8 "
    "+ results/_r813bma_resolve.py + commits 925b3657c/0db4bb555/"
    "6c340dca4 push-verified | next: r814 = W171 seat chain (probe "
    "post-W170 universe re-derive-MANDATORY proj A 390_804..392_803 / B "
    "391_004..391_203, naive-B-inside-naive-A leg2) -> W171 freeze -> "
    "burn -> finalize (proj ledger 781,612 / K 374,120); honesty note: "
    "round_reports r795..r812 lines absent on this file = dead-session "
    "windows, content preserved in git log + state history | "
    "本地未达 origin commit 数=0 (push+fetch 自证)"
    "\n")
with open(rp, "a", encoding="utf-8") as f:
    f.write(line)
print(f"closeout written: state r{R}, heartbeat epoch {EPOCH}, "
      f"round report 1 line, cpu={CPU} ram={RAM} gpu={GPU}")
