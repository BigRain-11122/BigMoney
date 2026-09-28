import json, time, datetime

NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
TS = time.strftime("%Y-%m-%d %H:%M:%S")

# --- 1. state-bm-a.json: round 409 ---
st = json.load(open("state-bm-a.json", encoding="utf-8"))
st["round_no"] = 409
st["round"] = 409
st["loop_round"] = 409
st["did"] = ("r409: W5 SCREEN-FINALIZE closure: burn-watch found bm-c autofill claim (02:15:39) + checkpoint carry-over 36ee7afd 4,126/4,126 complete -> "
             "MSG-20260929-0235 dual-signal claim declared+pushed (D-20260929-02 law; fetch-first origin=36ee7afd) -> screen-finalize LANDED "
             "(3926 distinct + 200 nulls, null median 0.4972 / p95 0.5164 / survivors 372=9.48%, prereg sec.5-2 ALL three bands PASS; "
             "ledger TRIAL_LAB_W5_SCREEN 324489+4126=328615 linear) -> pool surgery: SCREEN ready->done + W5-JUDGE entered waiting "
             "(lane bm-b deep-panel physical law; flip gates judge-prep-on-bm-b + RAM r354 + serial-position re-confirm; 48h CEO clock at judge-finalize) "
             "+ S6 36 legs rc=0 nonzero=[]")
st["verify"] = ("smoke 26/26; finalize gates fail-closed honored (4126/4126 cells present); prereg bands machine-verified PASS; "
                "pool JSON round-trip; core push LANDED 7640a160 (rebase over bm-b r403 stranded closeout, zero conflict); S6 36/36 rc=0")
st["next"] = ("(1) W5-JUDGE flip watch on bm-b (judge-prep + RAM 3-sample) -> judge burn -> judge-finalize (48h CEO report clock) -> intake slice; "
              "(2) 10-01 month-first triple fire (science_audit+monthly_briefing+self_review SR6) + REGIME_GUARD v3 date gate opens; "
              "(3) next 5x=r410 HANDOVER check; (4) moneyflow IC batch next_pick claimed, panel source-blocked self-heal watch")
st["last_round_at"] = NOW
st["current_task"] = "r409: W5 screen-finalize landed + JUDGE entered; watch bm-b judge-prep flip"
st["updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
json.dump(st, open("state-bm-a.json", "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)

# --- 2. round report line ---
line = (f"{NOW} | R409 bm-a (dept:策略+研究·W5 screen-finalize 收口轮) | "
        "WM first-line verdict: green (red=false; probe 02:40 py_low py 3.6-8.3% -- legal-idle: W5-SCREEN claimed by bm-c autofill tick 02:15:39 (fresh) = lane yield correct; "
        "W5-JUDGE now waiting lane=bm-b (physical deep-panel law) = no takeable shard on bm-a; board 0 open + bandit 0; cpu_total 71-81% = OTHER session census burn not repo face) | "
        "did: S0-1 anchor bm-a + S0 pull (stash-dance for autofill_state.bm-a.json local tick file, zero conflict) + S0.5 orders full-name diff 122/122 zero unacked (双扫) + "
        "decisions zero new rows (D-20260929-02 both legs standing receipted r406/r407; this round MSG-0235 honored the protocol face) + S1 smoke 26/26 + S2 双板 job_list 0 + fleet 0 open "
        "+ S3 MAIN CLOSURE **W5-SCREEN finalize trio**: (1) burn-watch -- autofill tick 02:30 pool_empty_or_busy diagnosed = bm-c shard claim owner_since 02:15:35 fresh (T-115 origin-claims verdict live-fire proof) "
        "+ checkpoint carry-over 36ee7afd landed 4,126/4,126 rows (3,926 distinct + 200 nulls complete, burn ~10min vs 12.3min W4 precedent); "
        "(2) **claim dual-signal** (D-20260929-02/r239 family): fetch-first origin==36ee7afd -> MSG-20260929-0235-bm-a-ALL-W5-screen-finalize-claim.md declared+committed+pushed 0955fbcc "
        "(single-writer ledger face anti-collision; T-114 owner bm-a r405; bm-c burn credit acknowledged in-body); "
        "(3) **screen-finalize LANDED** rc=0: 3926 distinct + 200 nulls, null median 0.4972 (<0.50 band) / p95 0.5164 (in [0.42,0.62]) / survivors 372 = 9.48% (in [2%,15%] -> [100,750]) "
        "**prereg sec.5-2 ALL three bands machine-verified PASS**; ledger TRIAL_LAB_W5_SCREEN prev 324,489 + 4,126 = **328,615 linear** (data-driven chain head = w5_screen.json); "
        "products w5_screen.json (evidence_cutoff 2026-09-22 + grammar 29720178c39425de anchored) + w5_screen_cells.csv 610KB; yang-segmented survival: none 12.2% vs first_yang 6.6% "
        "(gate x vol x yang 18-cell interaction face disclosed in-product); "
        "(4) **pool surgery** (Tools/_r409bma_w5_pool_flip.py, JSON round-trip self-verified): TRIAL-LABOR-W5-SCREEN ready->done (shard done + burn credit bm-c + finalize receipt) "
        "+ **TRIAL-LABOR-W5-JUDGE entered waiting** (mirror W4-JUDGE shape: lane_owner=bm-b deep-panel physical law, judge-prep-on-bm-b + RAM r354 three-sample + serial-position re-confirm flip gates, "
        "runner judge-0of1 shard, checkpoint face W1 law, 372 judged cells = batch_trials literal at finalize, 48h CEO report clock starts at judge-finalize); "
        "+ push storm: core push rejected (bm-b r403 stranded closeout landed mid-window) -> pull --rebase clean -> push LANDED ab4f98fb..7640a160 || "
        "S6 36 legs rc=0 nonzero=[] (audit v2.4.1 py 8.3%/cpu 71%; probe py_low legal; daily no-op cutoff 09-28; regime ORANGE breadth 0.83 shadow; scorecard 6/28/7 16s; "
        "clock CALL-0928 ORANGE_COOL sleeves4 act0; lhb/heat/futures/repo/options cutoff-covered zero-network; MF spawn rank pass; sinaMF 20td window; "
        "astock/etf/revosc/minfeed/alloc/fundprem six lane-guards honest no-op; ths same-day idempotent; AH refresh spawn detached; fundamental 16.8h fresh-skip; blf all_pass; "
        "live_paper OK shadow 10-01 gate; t35v PASS zero-pending; t24 22/22 drift0 + promotion 0/22 honest; aggr/grid/sysv1 idempotent marks@cutoff; t35e 09-28; "
        "daily_scorecard 6 traders; REPORT-0929 faces4 token1; LIVE-0929 ORANGE cap50%; build 432combos; token L2 delta=0) || "
        "S7: schtasks Loop Running pin=8 + Watchdog + claw checks queued post-commit; inbox 净 (own MSG-0235 left for rival machines) || "
        f"verify: smoke 26/26 + finalize gates + prereg bands PASS + pool round-trip + push LANDED + S6 36/36 + orders double-scan zero | "
        "next: (1) W5-JUDGE flip watch (bm-b judge-prep + RAM) -> judge-finalize -> intake; (2) 10-01 month-first triple fire + REGIME_GUARD v3 opens; (3) next 5x=r410 HANDOVER\n")
with open("logs/iteration-loop/round_reports-bm-a.md", "a", encoding="utf-8", newline="\n") as fh:
    fh.write(line)

# --- 3. heartbeat fleet/machines/bm-a.json ---
hb = json.load(open("fleet/machines/bm-a.json", encoding="utf-8"))
hb["last_seen"] = NOW
hb["current_task"] = "r409: W5 screen-finalize landed (survivors 372, bands PASS, ledger 328615) + JUDGE entered waiting; watch bm-b judge-prep flip"
hb["verdict"] = ("green; W5-SCREEN chain closed: bm-c burn 4126/4126 + bm-a finalize (bands PASS, survivors 372) -> W5-JUDGE waiting lane=bm-b (judge-prep+RAM flip gates); "
                 "board 0 open; orders 122/122 acked (double-scan)")
hb["heartbeat_epoch_utc"] = int(time.time())
hb["clock_read"] = NOW
json.dump(hb, open("fleet/machines/bm-a.json", "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)

# --- 4. T-114 ticket progress ---
tp = "fleet/tasks/T-2026-09-29-114-P1.json"
t = json.load(open(tp, encoding="utf-8"))
t["progress_r409"] = ("r409 bm-a: SCREEN-FINALIZE LANDED per MSG-20260929-0235 claim (dual-signal D-20260929-02): bm-c autofill burn credit (claim 02:15:39, "
                      "checkpoint carry-over 36ee7afd 4,126/4,126) + bm-a finalize 02:38 -- 3926 distinct + 200 nulls, null median 0.4972 / p95 0.5164 / "
                      "survivors 372 (9.48%), prereg sec.5-2 ALL bands PASS; ledger TRIAL_LAB_W5_SCREEN 324,489+4,126=328,615 linear; "
                      "products w5_screen.json + w5_screen_cells.csv + segmented survival faces in-product; pool SCREEN done-flip + "
                      "TRIAL-LABOR-W5-JUDGE entered waiting (lane bm-b physical law; judge-prep + RAM r354 + serial re-confirm flip gates; "
                      "batch_trials at finalize = survivors 372 literal; 48h CEO report clock starts at judge-finalize). Next slice = judge on bm-b flip.")
json.dump(t, open(tp, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)

# self-verify
st2 = json.load(open("state-bm-a.json", encoding="utf-8"))
hb2 = json.load(open("fleet/machines/bm-a.json", encoding="utf-8"))
assert st2["round_no"] == 409
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be int (R170/R178 law)"
assert "T" in hb2["clock_read"] and "+" in hb2["clock_read"], "clock_read T-separator law (R262)"
print("closeout OK: state 409, report line appended, heartbeat epoch", hb2["heartbeat_epoch_utc"], "clock", hb2["clock_read"], "ticket progress_r409 written")
