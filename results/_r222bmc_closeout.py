import json, time, datetime, os

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

# 1) append round report line (pitlaw-109: python-append channel)
tmp = os.path.join(ROOT, "results", "_r222bmc_reportline.tmp")
with open(tmp, encoding="utf-8") as fh:
    line = fh.read()
rp = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
with open(rp, "a", encoding="utf-8", newline="\n") as fh:
    fh.write(line)
os.remove(tmp)

# 2) state-bm-c.json -> round 222
st_path = os.path.join(ROOT, "state-bm-c.json")
with open(st_path, encoding="utf-8") as fh:
    st = json.load(fh)
now = "2026-09-29T14:35:30+08:00"
st["round_no"] = 222
st["updated"] = now
st["note"] = ("r222: S6 37-leg all-green receipt + dev-queue full-clear verification "
              "(Optuna/town/J-line all delivered confirmed) + W8 bm-b-lane watch legal-idle")
st["last_round_ts"] = now
st["last_round_at"] = "r222"
st["did"] = ("S0 stash-dance pull ff (bm-a r431 T-102 four-lane wave-close + escape addendum landed) "
             "-> S0.5 orders 122/122 zero-diff + decisions D-20260929-02 receipt already closed (F-20260929-01 bm-a r406 in-tree, zero dup) "
             "-> S1 smoke 26/26 -> S2 boards 0 open + inbox 0 unread "
             "-> S3 trial-labor line: W8 chain bm-b lane in-flight (GENERATE done n=2834; SCREEN ready owner bm-b 13:50:04, stall 828 rows, bm-b r429 self-heal; bm-b hb 14:13:35 alive) "
             "+ W9 AMP berth held by W8-consumption gate + dev-queue PLAN sec.7 / STRATEGY_LIBRARY live-read verify all-closed (Optuna skeleton flip-note + REPO-CALENDAR intake + fee-recheck in-library) = legal-idle "
             "-> S6 37 legs rc=0 all green (dualrun ZERO-DRIFT streak 29/3; audit flags supply_gap+supply_floor honest=W8 sole ready bm-b lane; WM py_low_board_clear; "
             "regime ORANGE breadth 0.83 shadow; scorecard 6/28/7 + t35_export 09-28 + daily_scorecard + dashboard_status = bm-a hb stale 25min O-2100 s2.4 stale-takeover legal; "
             "clock CALL-09-28 ORANGE_COOL sleeves4 act0; LHB no-op; 13 lane-guard legs honest no-op; fund_premium (bmc lane) pre-15:30 no-op; fundamental fresh-skip; "
             "b_layer 5222/3517 gates 5/5; aggr/grid marks cutoff-idempotent; REPORT+LIVE 09-29 faces regenerated; token delta 0) "
             "-> S7 pin=5 no-op + watchdog re-register + claw MATCH + heartbeat int-epoch")
st["verify"] = ("smoke 26/26; 37 legs rc=0 per-leg; dualrun streak 29/3; orders 122/122 programmatic; "
                "bm-a takeover legality last_seen 14:05:46 vs chain 14:31 stale 25min>20min line")
st["next"] = ("(a) post-15:30 new-bar window: paper chain non-no-op + fund_premium 15:30 snapshot (bm-c lane); "
              "(b) W8 SCREEN/JUDGE full-chain consumption watch -> W9 draft window opens (any healthy machine, pool entry lane_owner per pit-103); "
              "(c) 10-01 month-first-round trio (science_audit/monthly_briefing/self_review) + REGIME_GUARD v3 date-gate auto-activation hands-off; "
              "(d) next 5x HANDOVER = bm-c r225; (e) bm-a machine/bm-a-r431 escape branch self-merge watch (pit-93, do not merge for them)")
st["current_task"] = ("r222: S6 37-leg all-green + dev-queue full-clear verify; W8 bm-b-lane watch "
                      "(SCREEN stall 828/3034 self-heal), W9 gated; 15:30 window next")
st["updated_at"] = now
with open(st_path, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1)

# 3) heartbeat fleet/machines/bm-c.json
hb_path = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
with open(hb_path, encoding="utf-8") as fh:
    hb = json.load(fh)
hb["last_seen"] = now
hb["clock_read"] = now
hb["heartbeat_epoch_utc"] = int(time.time())
hb["current_task"] = st["current_task"]
hb["verdict"] = "green: S6 37 legs rc=0; legal-idle (W8 bm-b lane in-flight, W9 gated on W8 consumption; dev queue full-clear verified)"
import psutil
hb["cpu_pct"] = round(psutil.cpu_percent(interval=0.5), 1)
hb["idle_ram_gb"] = round(psutil.virtual_memory().available / (1024**3), 1)
try:
    import subprocess
    out = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                         capture_output=True, text=True)
    hb["gpu_free_vram_mib"] = int(out.stdout.strip().splitlines()[0])
except Exception:
    pass
with open(hb_path, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)

# self-assertions
with open(hb_path, encoding="utf-8") as fh:
    hb2 = json.load(fh)
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in hb2["clock_read"], "clock_read must be T-separated"
with open(st_path, encoding="utf-8") as fh:
    st2 = json.load(fh)
assert st2["round_no"] == 222
print("report appended; state 222; hb epoch", hb2["heartbeat_epoch_utc"], type(hb2["heartbeat_epoch_utc"]).__name__,
      "| cpu", hb2["cpu_pct"], "| ram", hb2["idle_ram_gb"], "| gpu", hb2["gpu_free_vram_mib"])
