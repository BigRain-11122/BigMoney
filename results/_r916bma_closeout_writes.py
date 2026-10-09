# -*- coding: utf-8 -*-
# r916 bm-a closeout writes: seat MSG self-ack archive + state 915->916 +
# heartbeat refresh + report line + methodology card append (fresh
# read-modify-write per multi-writer law; epoch int + clock_read T-format).
import json, time, datetime, os, shutil

NOW = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
EPOCH = int(time.time())

# --- seat MSG self-ack archive (S7 inbox-processing law; W196-style
# archive-pending pattern honored at this freeze-window closeout) ---
SRC = 'fleet/inbox/MSG-2026-10-09-1355-bma-w198-seat.md'
DST = 'fleet/inbox/processed/MSG-2026-10-09-1355-bma-w198-seat.md'
assert os.path.exists(SRC), 'seat MSG missing from inbox/'
assert not os.path.exists(DST), 'seat MSG double-present'
shutil.move(SRC, DST)
assert os.path.exists(DST) and not os.path.exists(SRC)
print('seat MSG archived inbox->processed')

# --- state ---
sp = 'state-bm-a.json'
st = json.load(open(sp, encoding='utf-8'))
st['round_no'] = 916
st['round'] = 916
st['loop_round'] = 916
st['last_round'] = 915
st['clock_read'] = NOW
st['ts'] = NOW
st['updated'] = NOW
st['last_seen'] = NOW
st['last_round_at'] = NOW
st['last_round_closed'] = NOW
st['last_round_ts'] = NOW
st['last_run'] = NOW
st['heartbeat_epoch_utc'] = EPOCH
st['last_heartbeat_epoch_utc'] = EPOCH
st['idle_rounds'] = 0
st['agenda_starved'] = False
st['did'] = ("r916: W198 prereg BUILD LANDED (research/PERPETUAL_N1_W198_PREREG.md 21,395B via "
             "buildgen two-gen eval chain r914 BACK AST-extract, zero transcription; anchor=W197 "
             "finalize actuals 847,745/431,320 per r590; bands A 450_404..452_403 staircase "
             "FIFTY-EIGHTH + B 452_404..452_603 W141 mutual-exclusion; REG_N 195 zero-overlap) + "
             "W198 five-face FREEZE LANDED (pf N1_BANDS[198] + n1 WAVE_CONFIGS[198] + materializer "
             "face + selftest claim + seat archive-pending face; 92+35+21+11 derived pairs + 5+4 "
             "archive pairs count-asserted; r912 AST triples + r915 AST RULES two-gen chain "
             "zero-transcription; registry 195->196 rows, W197/W196/W195 byte-intact post-import) + "
             "engine self-burn IGNITED tick 14:11 (n1w198-1of12 pid=10960; in flight at closeout) "
             "+ S6 38-leg rc0 bad NONE + seat MSG self-ack archived")
st['last_action'] = 'r916 closeout: W198 prereg build + five-face freeze landed; burn in flight; push self-verified'
st['current'] = 'r916 closed: W198 prereg build + five-face freeze landed; engine self-burn in flight'
st['now_active'] = st['current']
st['current_task'] = ("r917: W198 burn 12/12 -> finalize one-pass (four pred keys vs W197 actuals "
                      "anchor 847,745/431,320 per r590) + sec7/8 machine backfill + 10-09 15:30 "
                      "bars -> evening marks chain (REGIME_GUARD enforce + live.paper + t35/t24 "
                      "family); PARKING-P1 burn due 10-14 12:00 (O-20261009-1105)")
st['task'] = st['current_task']
st['next'] = st['current_task']
st['next_milestone'] = st['current_task']
st['last_artifact'] = ("r916 products: research/PERPETUAL_N1_W198_PREREG.md (21,395B, anchor W197 "
                       "actuals, A 450_404..452_403 FIFTY-EIGHTH staircase + B 452_404..452_603) + "
                       "scripts/perpetual_faces.py N1_BANDS[198] + scripts/perpetual_faces_n1.py "
                       "WAVE_CONFIGS[198]/materializer face + "
                       "results/_r916bma_w198_freeze_receipt.json + burn shards "
                       "results/p2cal_ext/n1_w198/ (in flight)")
st['latest_artifact'] = st['last_artifact']
st['verify'] = ("smoke 49/49 + pf selftest 9/9 + n1 selftest PASS incl W198 face live + freeze "
                "dry-run PASS all gates + --write LANDED (92+35+21+11+5+4 pairs count-asserted, "
                "stale sweeps clean, AST+py_compile, post-import rows 196 cfg198 EXACT) + engine "
                "tick ignited n1w198 pid=10960 + S6 38-leg rc0 bad NONE (panel 10-08 pre-15:30 "
                "honest no-op family; options-skip honored per O-20261009-1105) + attrition CLEAN "
                "+ quartet GREEN (loop pin=8 no-op / watchdog Ready / claws installed) + "
                "DEC/ORD python-raw bd94a27b/b6ea34b1 UNCHANGED zero-action")
st['last_decisions_sha'] = 'bd94a27ba4ac39bc9a05037ddcfaf693cd78126aa6189711e8f7f1848a8ac522'
st['last_orders_sha'] = 'b6ea34b1e96d176002bdd2bad666b0c5a4ec07e2308b2aeccece93f5b4c5b202'
st['last_decisions_at'] = NOW
st['last_decisions_ts'] = NOW
st['last_orders_at'] = NOW
st['last_orders_ts'] = NOW
st['last_decisions_seen'] = ("r916 recompute: DEC bd94a27b UNCHANGED vs r915 consumption -- zero "
                             "delta; zero new BigMoney action")
st['last_orders_seen'] = ("r916 recompute: ORD b6ea34b1 UNCHANGED vs r915 consumption -- zero "
                          "delta; zero new BigMoney-dispatch action")
st['last_decisions_src'] = 'group origin/main via C: real-path (C:/Users/sjs20/Desktop/FluxGroup) fetch + git show (python subprocess raw-bytes canonical)'
json.dump(st, open(sp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('state 915->916 written, epoch int', EPOCH)

# --- heartbeat ---
it = json.load(open('results/idle_trigger.bm-a.json', encoding='utf-8'))
hp = 'fleet/machines/bm-a.json'
hb = json.load(open(hp, encoding='utf-8'))
hb['last_seen'] = NOW
hb['ts'] = NOW
hb['clock_read'] = NOW
hb['heartbeat_epoch_utc'] = EPOCH
hb['current_task'] = st['current_task']
hb['cpu_cores'] = os.cpu_count()
hb['ram_free_pct'] = it.get('ram_free_pct')
hb['vram_free_gb'] = it.get('vram_free_gb')
hb['idle_rounds'] = 0
hb['agenda_starved'] = False
hb['verdict'] = 'green (r916 closed: W198 prereg build + five-face freeze landed; engine burn in flight)'
json.dump(hb, open(hp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
chk = json.load(open(hp, encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be JSON int'
assert 'T' in chk['clock_read'], 'clock_read must be T-delimited ISO8601'
print('heartbeat written; epoch-int self-verified; clock T-format verified')

# --- methodology card append (capture law: new method this batch) ---
MP = 'knowledge/METHODOLOGY_ASSETS.md'
card = ("- r916 bm-a [freeze-edit pair two-gen chain]: when the immediately-prior freeze script "
        "carries curated RULES_* 2-tuples but NOT the R/RC/RP/RQ (old,new,cnt) triple lists, "
        "reconstruct the live-fragment old sides via two-gen AST eval: prior-prior script's "
        "triples (r912) new-side -> apply prior script's RULES (r915) = live W-1 text = this "
        "build's old side -> apply this wave's curated RULES = new side (r587 zero-transcription "
        "preserved end-to-end; DROP_IF filter + archive pairs machine-rolled from the prior "
        "script's MAT_ARCHIVE/PF_ARCHIVE both sides). Proof: _r916bma_w198_freeze_edits.py "
        "92+35+21+11 pairs count-asserted first-run dry-run PASS.\n")
with open(MP, 'a', encoding='utf-8', newline='') as f:
    f.write(card)
print('methodology card appended')

# --- report line (canonical ROOT) ---
line = (NOW + " | r916 | bm-a | dept:research (W198 prereg build + five-face freeze; N1 perpetual "
        "supply line) | WM-VERDICT: green (red=false lane healthy; engine ALIVE ignited n1w198 "
        "pid=10960 burn in flight; DEC bd94a27b/ORD b6ea34b1 python-raw UNCHANGED zero re-consume "
        "zero action; orders double-scan unacked=0) | CUR-ACT: W198 prereg BUILD + five-face "
        "FREEZE LANDED same window + engine self-burn ignited 14:11 (7/12 in flight at closeout; "
        "finalize = next round once 12/12) | LAST-ARTIFACT: research/PERPETUAL_N1_W198_PREREG.md "
        "(21,395B buildgen two-gen eval chain, anchor=W197 actuals 847,745/431,320 per r590, A "
        "450_404..452_403 staircase FIFTY-EIGHTH hops=1 + B 452_404..452_603 W141 reserved-walk "
        "hops=1) + scripts/perpetual_faces.py N1_BANDS[198] + n1 WAVE_CONFIGS[198] + materializer "
        "face (registry 195->196; W197/W196/W195 byte-intact post-import; pf selftest 9/9 + n1 "
        "selftest PASS incl W198 face live) + results/_r916bma_w198_freeze_receipt.json | "
        "NEXT-MILESTONE: r917=W198 finalize one-pass (four pred keys vs W197 anchor; sec7/8 "
        "machine backfill) once burn 12/12; 10-09 15:30 bars -> evening marks chain; PARKING-P1 "
        "burn due 10-14 12:00 | did: S0-1 anchored bm-a + orphan probe 0 (25 py faces read-only) + "
        "S0 fetch 0/0 clean + S0.5 DEC/ORD python-raw recompute UNCHANGED (bd94a27b/b6ea34b1 same "
        "hash as r915 consumption) + orders scan zero new O-files + S1 smoke 49/49 + S3 W198 "
        "prereg buildgen (r914 BACK AST eval two-gen chain + live fact re-asserts from "
        "n1_w197_results.json + probe receipt leg0-4 machine-read + origin vacancy -S probe + "
        "seat sha 525630e39 ancestor; src blob = 363cd51df freeze-time byte-verbatim per r877 "
        "law 4) -> five-face freeze edits (r915 bloodline one-gen roll + r912 AST triples + "
        "r915 AST RULES two-gen chain for pair old-sides; archive-pending face = r912 W196-style "
        "pattern machine-rolled r912->r916/W196->W198; dry-run PASS all gates -> --write LANDED "
        "n1-first-then-pf r666 safe order) -> pf selftest 9/9 + n1 selftest PASS (W198 face "
        "live) -> engine tick ignited n1w198-1of12 pid=10960 ledger_flush=1 + S6 38-leg rc0 bad "
        "NONE (_r916bma_s6_driver.py r900 bloodline rolled; new_bar=False panel 10-08 "
        "pre-15:30 honest no-op family; options-skip honored per O-20261009-1105 sec1.2) + S7 "
        "quartet GREEN (loop pin=8 no-op first-fire 14:18 / watchdog Ready / claws installed) + "
        "attrition CLEAN (4 ledgers; 588d4c160 shrink healed note historical) + seat MSG "
        "self-ack archived inbox->processed (W196-style archive-pending face closed per S7 law) "
        "+ methodology card appended (freeze-edit pair two-gen chain) | verification: smoke 49/49 "
        "+ pf 9/9 + n1 selftest PASS + freeze --write PASS 5/5 segments + engine ignition "
        "confirmed + S6 bad NONE + attrition CLEAN + quartet GREEN | scoring: 2 (prereg file + "
        "registry five-face + freeze receipt = runnable/visible/usable artifacts; supply line "
        "zero-gap) | bookkeeping: 5/5 (state + report line + heartbeat + S6 receipt + "
        "methodology card) | treasure-capture: 1 new method (freeze-edit pair two-gen chain -> "
        "METHODOLOGY_ASSETS card appended; TREASURE_REGISTRY zero add = no new treasure class) | "
        "orphan_face=0 | unacked_orders=0 | local_vs_origin=0 | token: L1 zero API (token_meter "
        "delta=0) | [r916 bm-a]")
with open('round_reports-bm-a.md', 'a', encoding='utf-8', newline='') as f:
    f.write(line + '\r\n')
print('report line appended (canonical ROOT)')
