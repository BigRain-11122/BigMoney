"""r446 bm-b closure writer: round report line + state.json 446 +
heartbeat bm-b.json (int epoch + T-sep clock, smoke F7 fields)."""

import json
import time

NOW = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())

REPORT_LINE = (
    NOW + " | r446 bm-b | WM-VERDICT: red=false @04:30 probe "
    "(py_low_with_work_cands legal-load: astock refresh lock alive + "
    "W12 SCREEN/JUDGE pool chain in-flight; next_pick=moneyflow IC "
    "claimed) | CURRENT: W12 SCREEN finalize landed + JUDGE pool-armed "
    "| ARTIFACT: results/trial_labor_w12/w12_screen.json @04:33 (null "
    "p95 0.5132 IN [0.50,0.52], survivors 188/859=21.88%, ledger "
    "354,024->355,083 linear) + judge_state.json @04:35 + pool flips "
    "(SCREEN=done, JUDGE=ready) | MILESTONE: W12 JUDGE burn via "
    "autofill tick (~04:40 ignition, 188 cells ETA ~30min) -> "
    "judge-finalize -> intake D6 -> CEO-REPORT-WAVE12 48h window (by "
    "2026-10-02 04:00); W13 berth=bm-a declared window (anti-dup "
    "yield) | did: (1) dead r446 session adoption per r240 law "
    "(forensics: single lineage -- 04:02 tick session W5-backfill "
    "commit 3606e2d82 + axis fix 04:05:27 + screen-prep 04:05:49 + "
    "SCREEN pool arm 04:10:04, autofill r290 self-commit c84f70c6f "
    "04:10:08, burn 04:10-04:13:00 1059/1059 complete, stream-timeout "
    "death, state not advanced -> this round = r446 continuation; pool "
    "entered_at 04:22:00 dead-session stamp anomaly noted not "
    "rewritten); (2) screen-finalize NameError surgical residual #2 "
    "(gvvvsktsams_seg 9-tuple seg-dict init miss) 1-line mechanical "
    "fix + selftest 48/48 re-verified -> finalize landed: 859+200="
    "1059 cells, null p95 0.5132 IN band, survivors 188/859=21.88%, "
    "ledger 354,024+1,059=355,083 linear; RESEARCH FACTS: first "
    "RSQR-axis screen face rsqr10_hi 26.35% ~ none 25.43% > rsqr20_hi "
    "8.15% toxic-low face (10/20 asymmetry mirrors STD); std10_hi "
    "30.64%>none 20.00%>std20_hi 18.98% W11 replication; mom_oversold "
    "23.81% vs none 20.89% = 1.14x continuation weakening lineage "
    "W10 1.88x -> W11 1.25x -> W12 1.14x; (3) judge-prep KeyError "
    "rsqr slope_sign_split per-leg disclosure key missing -> full-"
    "face sec.2(e) computation mirror added (additive disclosure, "
    "zero judgment-line touch, BETA20 same frozen runner; L leg "
    "85up/78dn) -> judge-prep PASS (manifest 48 members, census L/D "
    "frozen, survivors 188, rsqr meta L 163open/1348closed decidable "
    "1511); (4) pool bookkeeping: TRIAL-LABOR-W12-SCREEN -> done "
    "(result_ref+done_at+shard done) + TRIAL-LABOR-W12-JUDGE "
    "enqueued ready (W11-JUDGE field pattern, host_gates 5383 "
    "parquet verified at submission); (5) S6 dead-session sweep "
    "adopted wholesale (04:00-04:13: update_status exit0 + etf/"
    "futures/lhb fresh + REPORT/LIVE-0930 landed; scorecard/dashboard "
    "04:11/04:14 writes = O-2100 s2.4 STALE_MIN legal takeover bm-a "
    "heartbeat stale 81min r443 precedent) + this-session legs: smoke "
    "26/26 + attrition guard 4 ledgers CLEAN + watermark probe "
    "fresh; (6) S0.5 orders 122/122 zero new; decisions.md face "
    "absent on this machine = zero action; (7) task board zero open "
    "(T-124 wave ticket = bm-b lane) | verify: smoke 26/26 PASS + "
    "selftest 48/48 PASS (both post-fix runs green) + shard 1059/"
    "1059 lines==objects (r443 law) + AB set == candidates set 859 "
    "exact + trials_ledger 354,024+1,059=355,083 linear + grammar "
    "pin 67c86c9cf4ef1ca7 == FROZEN identity + guard scan CLEAN + "
    "pool flip read-back asserted + judge-prep PASS all gates | "
    "next: JUDGE burn watch (autofill ignition) -> judge-finalize -> "
    "intake -> CEO-REPORT-WAVE12; astock respawn observation window "
    "(pid27440 laggard catch-up); lhb r229 family continued "
    "observation [via bm-b]"
    )

with open("logs/iteration-loop/round_reports.md", "a",
          encoding="utf-8") as f:
    f.write(REPORT_LINE + "\n")

state = json.load(open("state.json", encoding="utf-8"))
state["round_no"] = 446
state["note"] = (
    "r446 CLOSED (dead-session adoption + continuation per r240): "
    "W12 SCREEN finalize LANDED (surgical NameError fix #2 "
    "gvvvsktsams_seg init miss) -- 1059/1059 cells, null p95 0.5132 "
    "IN [0.50,0.52], survivors 188/859=21.88%, ledger 355,083 "
    "linear; RESEARCH FACTS: rsqr20_hi 8.15% toxic face (first "
    "RSQR-axis screen), std10/std20 asymmetry replication, mom "
    "1.14x weakening lineage; judge-prep PASS (per-leg slope-sign "
    "disclosure mirror fix, L 85up/78dn) + TRIAL-LABOR-W12-JUDGE "
    "pool-armed ready (host_gates 5383 parquet); dead r446 "
    "forensics: axis fix 04:05 + prep + SCREEN arm 04:10 + autofill "
    "burn 1059 complete 04:13, stream-timeout death, pool "
    "entered_at 04:22:00 anomaly noted; S6 sweep adopted (STALE_MIN "
    "takeover legal); smoke 26/26, attrition CLEAN, orders 122/122. "
    "NEXT: W12 JUDGE burn via autofill -> judge-finalize -> intake "
    "D6 -> CEO-REPORT-WAVE12 (48h by 2026-10-02 04:00); W13 berth="
    "bm-a (anti-dup yield).")
state["last_round_at"] = NOW
state["last_round_ts"] = "r446"
state["ts"] = NOW
state["updated"] = NOW
with open("state.json", "w", encoding="utf-8") as f:
    json.dump(state, f, ensure_ascii=False, indent=1)

hb = json.load(open("fleet/machines/bm-b.json", encoding="utf-8"))
hb["last_seen"] = NOW
hb["heartbeat_epoch_utc"] = EPOCH
hb["clock_read"] = NOW
hb["current_task"] = (
    "r446 CLOSED: W12 SCREEN finalize landed (null p95 0.5132, "
    "survivors 188/859, ledger 355,083) + judge-prep PASS + JUDGE "
    "pool-armed ready -- autofill burn next tick -- NEXT: W12 "
    "judge-finalize -> intake D6 -> CEO-REPORT-WAVE12 (48h by "
    "2026-10-02); W13 berth=bm-a window")
hb["cpu_cores"] = 16
hb["free_ram_gb"] = 5.6
hb["gpu_free_vram_gb"] = 2.0
hb["round_no"] = 446
hb["round"] = 446
hb["loop_round"] = 446
hb["ram_free_gb"] = 5.6
hb["idle_ram_gb"] = 5.6
hb["gpu_free_vram_mb"] = 2042
hb["gpu_idle_vram_gb"] = 2.0
hb["last_round_at"] = NOW
hb["verdict"] = "healthy"
with open("fleet/machines/bm-b.json", "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

# verification: epoch int + clock T-separator (smoke F7 law)
hb2 = json.load(open("fleet/machines/bm-b.json", encoding="utf-8"))
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in hb2["clock_read"], "clock must be T-separated"
print("closure files written:", NOW, "epoch:", hb2["heartbeat_epoch_utc"])
