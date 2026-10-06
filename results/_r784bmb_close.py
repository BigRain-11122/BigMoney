# r784 bm-b close-out: state honest-jump write (781->784 per r714 law), heartbeat refresh,
# ledger rows append (r782/r783 POST-MORTEM BACKFILL + r784 close row).
# ASCII-only comments per house script discipline; CJK only in row content (UTF-8 file I/O).
import json, time, datetime, os

NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())
TS = NOW  # same source, same instant (fleet-audit law)

# ---------- state.json ----------
with open("state.json", encoding="utf-8") as f:
    st = json.load(f)
st["round_no"] = 784
st["note"] = ("r784: dead r782/r783 absorb close-out (r782: S6 chain 35 rc0 + QA pack r782 5/5, died pre-commit; "
              "r783: D-06 CODELY main-rebound committed 168b12a23 + S0-2 merge absorb ce1e36fe7 + S6 REGEN 35 rc0, "
              "died post-chain pre-S7 -> state stayed 781) + state honest jump 781->784 per r714 law "
              "+ D-19 dec MATCH / ord delta 3 rows consumed zero-BM-action, watermark 631E5DF2->6F3AC292 "
              "+ review-llm_assist 5 findings triaged all-no-change (2 false/2 design/1 guarded) "
              "+ llm_assist local-fallback leg FIRST LIVE EVIDENCE under C gaming-pause (selftest route=local rc0) "
              "+ QA pack r784 5/5 detached --round 784 per r758 law + worksnap quarantine per TREASURE sec2")
st["last_round_at"] = NOW
st["ts"] = TS
st["updated"] = TS
st["last_seen"] = TS
st["clock_read"] = TS
st["last_round_ts"] = TS
st["round_no_label"] = "r784"
st["last_orders_sha"] = "6F3AC292C93EACC795413B507772A338B761458D45AC31D9D9D2FF1FB017DA42"
st["last_orders_read_at"] = TS
st["last_orders_sha_note"] = ("r784: ord delta 3 rows consumed via _r784bmb_d19_read.py (r781 verbatim lineage, r631 "
                              "sparse-clone recipe): 19:0x mobilization already-executed + 19:1x C gaming-pause + "
                              "20:3x CEO trigger-word law -- all zero BigMoney dispatch; dec A44C39E0 MATCH unchanged")
st["did"] = ("r784: churn-absorb dead r782/r783 tails + pull-race x2 -> r761 defer-to-push law + orders 159/159 "
             "+ D-19 dual consumed (ord +3 rows) + smoke 48/48 + QA pack r784 5/5 + triage 5 findings zero-change "
             "+ llm_assist fallback live verify + S7 quartet 4/4 + attrition CLEAN + worksnap quarantine")
st["verdict"] = ("green: dead r782/r783 absorbed clean; Q 1778/D 1467 burns alive dup_k=0; review triage closed "
                 "zero-change; orders zero unacked; integration behind-6 deferred to S7 push path per r761 law")
st["current_task"] = ("r784 closed; next = trio Q finalize watch ~10-07 morning / D ~10-07 evening + D-06 group "
                      "closeout 10-07 12:00 + market reopen 10-08")
st["next"] = ("(1) D-06 group closeout 10-07 12:00 (CODELY 30.6KB post r783 re-scan, all pit files <=30KB sweep); "
              "(2) trio watch: Q eta ~9.7h ~10-07 morning, D eta ~25.6h ~10-07 evening -> first-to-2000 finalize "
              "round same-window pool dual-flip per r668 law, window 10-05..10-09, G4 PENDING r638 fallback armed; "
              "(3) market reopen 10-08: S6 legs 25-28 resume + REGIME_GUARD v3 first new bar enforce; "
              "(4) LLM-via-C supply resumes when CEO ends gaming window (route auto-repins keep_alive=-1)")
with open("state.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
    f.write("\n")

# ---------- heartbeat fleet/machines/bm-b.json ----------
with open(os.path.join("fleet", "machines", "bm-b.json"), encoding="utf-8") as f:
    hb = json.load(f)
hb["last_seen"] = NOW
hb["heartbeat_epoch_utc"] = EPOCH
hb["clock_read"] = TS
hb["ts"] = TS
hb["updated"] = TS
hb["last_round_at"] = NOW
hb["round_no"] = 784
hb["round"] = 784
hb["free_ram_gb"] = 7.29
hb["gpu_free_vram_gb"] = 3.656
hb["gpu_free_vram_mb"] = 3656
hb["last_action"] = ("r784 closed: dead r782/r783 absorb (S6 regen 16 faces + QA pack r782 + workfiles) + D-19 ord +3 rows "
                     "consumed zero-BM-action + QA pack r784 5/5 + review 5-findings triage all-no-change + llm_assist "
                     "local-fallback live-verified (C gaming-pause) + smoke 48/48")
hb["now_active"] = ("FUND trio NULLS judgment batch: V COMPLETE 2000/2000; Q 1778/2000 D 1467/2000 alive burning dup_k=0 "
                    "(Q eta ~10-07 morning, D ~10-07 evening); trio finalize window 10-05..10-09, G1 pending Q+D, "
                    "G4 governance pending r638 fallback armed")
hb["latest_artifact"] = ("qa/smoke-r784.md + qa/equity-curve-r784.png QA pack 5/5 @22:2x (93 trades determinism=True, "
                         "detached --round 784) + llm_assist.py local-fallback live evidence @22:1x (route=local selftest rc0 "
                         "under C gaming-pause) + research/auto/review-llm_assist-20261006.md triage verdict appended")
hb["next_milestone"] = ("trio Q finalize ~10-07 morning / D ~10-07 evening-10-08 (first-to-2000 same-window pool dual-flip per "
                        "r668 law); D-06 group closeout 10-07 12:00; market reopen 10-08 (S6 legs 25-28 + REGIME_GUARD v3 "
                        "first new bar)")
hb["task"] = "FUND trio NULLS judgment batch lane (V done; Q/D burn watch) + D-06 closeout prep"
hb["verdict"] = ("green: r784 closed (dead-session absorb + QA pack r784 + D-19 consumed); Q 1778/D 1467 burns alive; "
                 "review triage zero-change; orders 159/159")
with open(os.path.join("fleet", "machines", "bm-b.json"), "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
    f.write("\n")

# ---------- ledger rows ----------
LED = os.path.join("logs", "iteration-loop", "round_reports.md")
row782 = ("2026-10-06T21:0x+08:00 | round 782 (bm-b, POST-MORTEM BACKFILL per r714 law -- session died pre-commit "
          "post-chain, row backfilled by r784 from absorbed products) | S6 chain 35 legs rc0 20:53-20:58 "
          "(results/_r782bmb_s6_chain.log, legs 25-28 golden-week honest-skip) + QA pack r782 5/5 21:40 "
          "(93 trades determinism=True, qa/smoke-r782.md; detached runner survived session death, r640 order law intact) "
          "| all products landed via r784 churn-absorb | product score 0 for this disclosure row (products credited to "
          "absorb window per r620 law)")
row783 = ("2026-10-06T21:2x+08:00 | round 783 (bm-b, POST-MORTEM BACKFILL per r714 law -- session died post-chain-regen "
          "pre-S7, state stayed 781; row backfilled by r784 from commits 168b12a23/ce1e36fe7 + regen log) | "
          "S0-1: D-06 main-rebound incremental re-scan committed 168b12a23 (CODELY 31854->30600B <=30KB line, 2 hot pit "
          "entries verbatim-migrated r782-worksnap-trio -> pit-git-resolver.md 1129B sha16 3e36394b + r639-lineage-stepper "
          "-> pit-lineage-legdiff.md 944B sha16 53b80791b, receipt _r783bmb_codely_increment.json) | S0-2: merge absorb "
          "ce1e36fe7 (origin 3: bm-c r640 close + push-retry + S4 QA-race pit vs local 2, auto-merge clean 0 UU, bm-c batch-4 "
          "subsumes bm-b D-06 sweep, 16 dirty blockers worksnap-guarded theirs-wins, 5 bm-b append-only ledgers "
          "byte-untouched) | S0.5: D-19 dec A44C39E0 MATCH + ord delta 2 rows consumed (C-machine game-window pause + "
          "CEO trigger-word law, zero BigMoney dispatch; watermark write eaten by session death -> r784 re-read covered 3 "
          "rows incl 19:0x mobilization, all executed-zero-BM-action, watermark advanced by r784) | S6: full REGEN chain 35 "
          "legs rc0 21:44-21:57 (results/_r782bmb_s6_regen.log, absorb round own re-run) + leg39 trio probe V2000/Q1778/D1467 "
          "dup_k=0 x3 integrity True | died post-chain pre-QA-commit pre-state-write; tail products (16 shared regen faces) "
          "landed via r784 churn-absorb | product score 1 (D-06 CODELY re-scan + merge absorb committed in-life; chain "
          "products credited to r784 absorb window)")
row784 = ("2026-10-06T22:3x+08:00 | round 784 (bm-b, dept:engineering, dead r782/r783 absorb close-out + review-5-findings "
          "triage + QA pack r784 round) | [watermark verdict: GREEN (red=false lane healthy; satengine alive rc0 idle "
          "queue_depth=0; board 0 open jobs both boards (job_list empty + fleet tasks 172 tickets zero status=open "
          "mechanical scan); trio-in-flight Q1778/D1467 = trial-labor line satisfied; trio burns own the lane + zero "
          "board/bandit faces = zero new drafting legal)] | CEO three-line: current-work = FUND trio NULLS judgment batch V "
          "COMPLETE 2000/2000 + Q 1778/2000 D 1467/2000 alive burning dup_k=0 (probe 21:57 face, Q rate 0.38/min eta ~9.7h "
          "~10-07 morning revised from r781 23:3x optimistic face, D eta ~25.6h ~10-07 evening) | latest-artifact = "
          "qa/smoke-r784.md + qa/equity-curve-r784.png (QA charter pack 5/5: 3 syms x 800 bars real backtest 93 trades "
          "determinism=True sharpe 0.1586, detached ignite PID 53716 --round 784 explicit per r758 law, terminal-state "
          "polled per r640 law before close) + llm_assist local-fallback leg FIRST LIVE EVIDENCE (C endpoint unreachable "
          "per C-machine gaming-pause order -> local fallback -> selftest gen=PASS rc0 route=local; orders row-2 'bm-b "
          "fallback in place' claim now verified-live) + review-llm_assist 5 findings triage verdict appended to "
          "research/auto/review-llm_assist-20261006.md (all 5 adjudicated no-change: 2 false vs actual code / 2 "
          "design-correct-keep / 1 already-guarded-by-selftest-leg; human-verified line-by-line) | next-milestone = trio Q "
          "finalize ~10-07 morning + D ~10-07 evening/10-08 (finalize window 10-05..10-09, G1 burn_complete pending Q+D, "
          "G4 PENDING r638 fallback armed) + D-06 group closeout report 10-07 12:00 + market reopen 10-08 (S6 legs 25-28 "
          "resume + REGIME_GUARD v3 first new bar) | S0: identity=bm-b anchored (machine.json first-read); churn-absorb "
          "commit landed dead r782/r783 tails (16 shared regen faces + QA pack r782 + d19/qa/worksnap workfiles + daemon "
          "live churn); pull --rebase blocked twice by live daemon faces re-writing within seconds (stash-race) -> r761 "
          "no-resolve law -> integration deferred to S7 push-merge path; origin behind-6 verified = bm-a r794/r795 W165 "
          "faces + bm-c r641 lineage re-walk; fleet/orders zero new files on origin side | S0.5: orders 159/159 zero "
          "unacked (full-set diff); D-19 dual read (verbatim lineage _r781bmb_d19_read.py -> _r784bmb_, r631 sparse-clone "
          "recipe, rc-signal contract intact): dec A44C39E0 MATCH unchanged; ord CHANGED -> delta 3 rows consumed (19:0x "
          "full-mobilization already-executed + 19:1x C-machine gaming-pause + 20:3x CEO trigger-word law C-machine "
          "scripting -- all zero BigMoney dispatch, rows group-side executed); watermark advanced 631E5DF2->6F3AC292 "
          "written in state this round | S1: smoke 48/48 | S3: satengine alive rc0 idle 0; watermark red=false "
          "next_pick=claimed advisory consumed as-is (moneyflow IC panel parked source-blocked bm-a lane legal); boards 0 "
          "open; review 5-findings triage = r781 next-pointer discharged same-round (zero code change, evidence-based "
          "adjudication; anti-overengineering law honored -- no cosmetic churn for score) | S6: dead-session REGEN chain "
          "35/35 rc0 21:44-21:57 absorbed as-is (third chain run within 60min = avoided per compute-audit white-run law; "
          "products idempotent-fresh, per-leg evidence results/_r782bmb_s6_regen.log; legs 25-28 golden-week honest-skip "
          "cutoff 2026-09-30 unchanged, reopen 10-08) | S7: quartet 4/4 (loop pin=2 no-op first-fire 22:22 + watchdog "
          "registered 22:20 + precommit/prepush claws LF-normalized content-match) + attrition guard CLEAN (4 ledgers, "
          "healed rows historical) + worksnap quarantine per TREASURE_PROTECTION_LAW sec2 (prescan rc0 zero-hits, 18 files "
          "723,462B, manifest-r784.json, manifest-disk byte-identity assert PASS, observation window to 10-13, source "
          "dirs removed) | verification: smoke 48/48 + QA pack r784 5/5 + llm_assist selftest rc0 route=local live + "
          "attrition CLEAN + D-19 dual consumed + state epoch int self-verified | treasure zero-hit claim: worksnap "
          "prescan rc0 zero-hits (only sweep action this round; quarantined-not-deleted per law) | local "
          "undelivered-to-origin commit count: PENDING_FILL_R784 | product score 2 (QA pack r784 real-backtest evidence + "
          "dead-session product absorb landed + fallback-leg live verification + triage closure same-round)")

with open(LED, "rb") as f:
    data = f.read()
prefix = b""
if data and not data.endswith(b"\n"):
    prefix = b"\n"
with open(LED, "ab") as f:
    f.write(prefix + ("\n".join([row782, row783, row784]) + "\n").encode("utf-8"))

# ---------- self-verify ----------
with open(os.path.join("fleet", "machines", "bm-b.json"), encoding="utf-8") as f:
    hb2 = json.load(f)
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be int (R178 law)"
assert hb2["clock_read"] == hb2["ts"] == hb2["last_seen"]
with open("state.json", encoding="utf-8") as f:
    st2 = json.load(f)
assert st2["round_no"] == 784 and st2["last_orders_sha"].startswith("6F3AC292")
with open(LED, encoding="utf-8") as f:
    tail = f.read()
assert row784[:40] in tail and tail.endswith("\n")
print("CLOSE-WRITE OK: state 784, epoch int", hb2["heartbeat_epoch_utc"], ", ledger rows x3 appended, tail-newline law OK")
