"""R113 bm-c round-close bookkeeping: state + heartbeat + round report line."""
import json
import time
import datetime

NOW_LOCAL = datetime.datetime.now().astimezone().replace(microsecond=0)
CLOCK = NOW_LOCAL.isoformat()            # T-separated, +08:00 offset
EPOCH = int(time.time())                  # JSON int (R170/R178 law)

STATE_NOTE = ("r113: CEO-order round O-2245/O-2250 both executed. T-94 claimed "
              "same-round per immediate law, s1 full loop done in-round "
              "(prereg freeze + SEED 20920000 + trial_wave_gen engine + 1000/1000 "
              "candidates selftest 3/3 + grammar registry); push revealed bm-b "
              "claim-collision (61703dd5 22:49:09 origin-first vs bmc 22:52) -> "
              "sec.4 commit-time yield: artifacts preserved origin/machine/"
              "bm-c-r113, main reset, MSG-2261 receipt pushed, adoption = bm-b "
              "sole call. r239 fetch-atomic-window law row (batch-35 CODELY "
              "8,646B). S6 30/30 rc=0 Sunday no-op family. Smoke 25/25.")

REPORT = (
    "2026-09-27T23:3x+08:00｜R113｜bm-c (dept:strategy+research yield-close; "
    "engineering+fleet)｜WM verdict: green (red=false lane healthy; probe 22:55 "
    "py 0.1% py_low_board_clear legal-idle Sunday night: board 0 open (T-94 "
    "claimed bm-b in-flight), bandit 0, bars_present=false, pool supply-gap W2A "
    "ready + W2B waiting both bm-b lanes R31 not claimable; audit v2.3 CLEAN "
    "flags=[])｜S0-1 identity bm-c anchored via machine.json (r98 law)｜S0 pull "
    "'already up to date' 22:50 clean tree (pre-bmb-claim-landing window "
    "disclosed)｜S0.5 orders set-diff 98-96=2 unacked BOTH EXECUTED: O-2245 "
    "千人试用期令 -> T-94 claimed+started same round per CEO immediate law (s1 "
    "full loop in-round: TRIAL_WAVE1_PREREG freeze commit -> SEED_REGISTRY "
    "20920000 rg-zero-hit -> trial_wave_gen.py -> gen 1000/1000 (500/family "
    "zero-collision zero-shortfall) -> selftest 3/3 -> GRAMMAR_REGISTRY WAVE-1) "
    "+ O-2250 TRIAL_LABOR_LAW verified in-tree (v1.0 read + S3 standing line "
    "consumed); decisions.md D-20260927-09 BigMoney face executed-closed bmc "
    "r84 maintained, D-06/07/08/10 not-our-lane, C-01 window 09-29 12:00 "
    "not-our-seat｜PUSH COLLISION: bm-b 61703dd5 claim 22:49:09 origin-first "
    "vs bmc bf7c2090 22:52 -> sec.4 commit-time yield: rebase --abort -> 4 "
    "commits preserved origin/machine/bm-c-r113 -> main reset origin/main -> "
    "MSG-2261 yield receipt pushed 5a7a1fab (adoption = bm-b sole call, reuse "
    "law, zero pressure)｜r239 fetch-immediately-before-claim violation "
    "self-caught (S0 pull != claim-time fetch; 3-min survey race window) -> "
    "batch-35 law row｜S1 smoke 25/25｜S2 job_list 0 + board T-94 "
    "open->claimed->yielded + pool 80 (78 done + W2A ready + W2B waiting, both "
    "bm-b lanes)｜S3 CEO immediate executed-then-yielded same round (claim+start "
    "law + collision law both honored; zero re-queue of T-94)｜S6 30/30 rc=0 "
    "(5 invocation-side subcommand fixes mine: options/sina_mf/astock/ths 'gate' "
    "+ ah bare-arg zero-arg run; 10 lane-guards honest stdout-only no-ops; "
    "weekend family: daily 0-new cutoff 09-24, regime ORANGE shadow 0.77, "
    "clock CALL-09-24 ORANGE_COOL idempotent, lhb no-op, heat weekend, futures "
    "cutoff-covers, fund_premium weekend no-op Mon 15:30 armed, fundamental "
    "13.5h fresh skip, b_layer regen pass, scorecard 6+28+7, daily_scorecard "
    "6/6, REPORT-2026-09-27 faces=4, build_status 432combos/0pass 5/7, token "
    "L2 1 leg local)｜S4 memory four-gate: 1 new law line (r239) + CODELY "
    "10,322B>10KB over-line at append window -> batch-35 in-window archival "
    "(batch-34 number yielded to origin bm-b r346 per r176) 8,646B<10KB "
    "zero-loss 6/6 via _r113bmc_codely_archive.py｜S7: schtasks Loop Running + "
    "Watchdog Ready 23:10 + claw CR-identical + state r113 + heartbeat "
    "epoch-int + T-clock; inbox MSG-2240 bmb->bma not-our-lane left for "
    "addressee, own MSG-2260/2261 standing for addressees｜next: (1) T-94 s2/s3 "
    "pool shards bm-c standing-ready post bm-b s1 products (2) Mon 09-28 15:30 "
    "fund_premium first snapshot bm-c lane (3) Mon 09:15 T-91 s3 first-marks "
    "bm-a (4) Mon 15:30+ astock bm-b (5) C-01 vote archival 09-29 12:00 (6) "
    "r115 next 5x HANDOVER｜evidence: origin/machine/bm-c-r113 + MSG-2261 + "
    "smoke 25/25 + S6 30/30 rc=0 + orders 98/98 + CODELY 8,646B batch-35 + "
    "state round_no=113 [via bm-c]"
)

# --- state file (round_no +1) ---
with open("state-bm-c.json", encoding="utf-8") as f:
    st = json.load(f)
st["round_no"] = 113
st["updated"] = NOW_LOCAL.strftime("%Y-%m-%dT%H:%M")
st["note"] = STATE_NOTE
with open("state-bm-c.json", "w", encoding="utf-8") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

# --- heartbeat ---
with open("fleet/machines/bm-c.json", encoding="utf-8") as f:
    hb = json.load(f)
ack = set(hb.get("orders_ack", []))
ack.add("O-2026-09-27-2245-bm-a.md")
ack.add("O-2026-09-27-2250-bm-a.md")
hb["orders_ack"] = sorted(ack)
hb["last_seen"] = CLOCK
hb["heartbeat_epoch_utc"] = EPOCH
hb["clock_read"] = CLOCK
hb["current_task"] = ("r113 closed: T-94 CEO-order claim-collision yield to "
                      "bm-b (sec.4 commit-time, s1 artifacts preserved "
                      "machine/bm-c-r113 + MSG-2261 handover) + S6 30/30 + "
                      "CODELY batch-35 8,646B; Mon 15:30 fund_premium "
                      "first-snapshot armed (bm-c lane)")
hb["round_no"] = 113
hb["verdict"] = ("healthy green-idle Sunday night (orders 98/98 acked, smoke "
                 "25/25, S6 30/30 rc=0, board 0 open T-94 claimed bm-b "
                 "in-flight, pool W2A/W2B bm-b lanes not claimable; r239 law "
                 "row batch-35; standing-ready for T-94 s2/s3 shards post "
                 "bm-b s1)")
hb["updated_at"] = CLOCK
with open("fleet/machines/bm-c.json", "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

# verify epoch int law + T-clock law (smoke F7 face)
with open("fleet/machines/bm-c.json", encoding="utf-8") as f:
    hb2 = json.load(f)
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in hb2["clock_read"], "clock_read must be T-separated"
print("heartbeat verify: epoch int ok,", hb2["heartbeat_epoch_utc"],
      "clock", hb2["clock_read"])

# --- round report line ---
with open("logs/iteration-loop/round_reports-bm-c.md", "a", encoding="utf-8",
          newline="") as f:
    f.write(REPORT.replace("23:3x", NOW_LOCAL.strftime("%H:%M")) + "\n")
print("round report R113 line appended")
