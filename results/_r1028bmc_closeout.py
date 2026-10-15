# -*- coding: utf-8 -*-
"""r1028 bm-c closeout writer: state + heartbeat + round report row.
Append-only report (r962 law); surgical state/heartbeat key updates;
epoch int assertion (R170/R178 law)."""
import datetime
import json
import os
import time

if True:
    try:
        import sys
        if sys.stdout:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW_ISO = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
EPOCH = int(time.time())

REPORT_ROW = (
    f"{NOW_ISO} | r1028 | bm-c | r1028: (1) S0-1 anchor + round-zero probe "
    "py_faces=5 orphans=2 zero-kill + S0 ff-merge 9d606b54b (bm-b r979 + "
    "bm-a r1017, zero dirty-overlap, clean tree merge); (2) S0.5 "
    "dual-delta FALSE both (ord 3b1ca198 / dec ab3f0cc9 hold, unacked=0); "
    "(3) S1 smoke 49/49; (4) PRODUCT = W20 funnel 4/5+5/5-head absorb: "
    "dead-window runner-build estate (14:10-14:20, died pre-commit) "
    "machine-verified BEFORE landing -- runner scripts/trial_labor_w20.py "
    "(106,890B, tl1/tl2/tl16/tl17/tl18 import-face lineage + G-face "
    "battery + r446 three-command law in docstring) + selftest 20/20 "
    "PASS hermetic + status gates A9/G-ROSTER/G-SEEDS PASS + grammar "
    "w20_grammar.json sha ff00b0896b088b5a == frozen == TRIAL_GRAMMAR_"
    "LEDGER W20 row (13+6+12=31 cells, seeds 20650000/20650500/20651000) "
    "+ candidates n_cells=31 census + prep_state G-battery 8/8 PASS with "
    "1253 starts passive_6m_ret complete (screen-prep identity first-run "
    "by dead window, verified this window) -> RUNNER LANDED per prereg "
    "sec.8 (grammar/generate/screen-prep real-data identity faces all "
    "exercised) + GENERATE consumed + pool surgery dual-file: TRIAL-"
    "LABOR-W20-GENERATE ready->done (flip frees autofill from refused "
    "same-grammar re-burn; readback-verified) + 4 SCREEN shards enrolled "
    "(TRIAL-LABOR-W20-SCREEN-SHARD-0..3, runner_args screen k 4, stride "
    "i%4 of 231 cells = 31 cand + 200 nulls, lane-pinned bm-c per r429 "
    "machine-local checkpoint law -- screen-finalize reads local "
    "CKPT_DIR; RAM gate 4GB r354 park-honest at 1.2GB free enrollment-"
    "time, autofill Bigmoney-Autofill retries when night window frees "
    "RAM); (5) S3: satengine ALIVE rc0 (Tools face; scripts-path = no-"
    "state honest, bm-c registered task = Tools path) + idle green_idle="
    "false RAM-gate honest (ram_free_pct 4.6, U256 w001/w003 claims stay "
    "deferred) + MV V4 lane: no bm-a director-review row on origin as "
    "of 14:35 (i2v INT8 768P batch stays gated, structural-wait honest) "
    "+ sentinel_bm-c.py foreign edit re-checked (origin still v1.0, "
    "bm-b's in-flight face stays uncommitted); (6) S6 light (pre-15:30 "
    "bars not due, full chain = next window post-15:30): dualrun ZERO-"
    "DRIFT streak 51 (461 entries, 4 new W20 shards dual-file "
    "reconciled) + compute_audit FLAG ignition_sla (fresh-enrollment "
    "observation face, answered-by-design: autofill claim + RAM park "
    "law; supply_floor 4>=3) + py_watermark insufficient_history fresh "
    "window (bars_present=false, pool_ready=4 all W20 screen) + token "
    "delta=0; (7) S7: attrition 4 CLEAN + quad green (loop pin=5 no-op "
    "next 14:45, watchdog 14:40, pre-commit claw + pre-push claw "
    "installed) | verify: selftest 20/20 + smoke 49/49 + status gates "
    "PASS + grammar sha frozen-match + prep G-battery 8/8 + pool "
    "readback-verify PASS (dual-file generate done + 4 shards ready) + "
    "dualrun streak 51 + attrition CLEAN + quad green | r1029: (1) W20 "
    "SCREEN watch -- autofill claims shards on RAM free (night window), "
    "burn complete -> screen-finalize (bm-c local) -> survivors -> "
    "judge-prep/judge/judge-finalize family blocks -> intake -> sec.7 "
    "backfill + 48h CEO clock + attrition 2 rows; (2) bars 10-15 due "
    "15:30 -> update_daily -> papers full chain (live.paper REGIME_GUARD "
    "enforce + t35 + t24 x2 + aggr/alloc/grid/system_v1 + export + "
    "faces); (3) MV V4 i2v batch on bm-a director review; (4) U256 "
    "claims on RAM gate open; (5) counter 1028->1029"
)

DID = ("r1028 bm-c: (1) S0-1 anchor bm-c + round-zero probe py_faces=5 "
       "orphans=2 zero-kill + S0 ff-merge 9d606b54b (bm-b r979 + bm-a "
       "r1017 estate, zero dirty overlap); (2) S0.5 dual-delta FALSE "
       "both (ord 3b1ca198 / dec ab3f0cc9 hold, unacked=0); (3) S1 "
       "smoke 49/49; (4) PRODUCT: W20 dead-window runner estate "
       "(14:10-14:20) absorbed verbatim per bm-c absorb lineage (31st "
       "instance) -- machine-verified BEFORE landing: runner selftest "
       "20/20 hermetic + status gates A9/G-ROSTER/G-SEEDS PASS + "
       "grammar sha ff00b0896b088b5a == frozen + candidates 31 cells "
       "(13 dd_rung_entry/6 near_52w_high/12 turnover_regime) + "
       "prep_state G-battery 8/8 PASS 1253 starts -> RUNNER LANDED "
       "(funnel 4/5 closed, r446 three-command identity law satisfied: "
       "grammar/generate/screen-prep all real-data first-runs) + "
       "GENERATE consumed (TRIAL_GRAMMAR_LEDGER W20 row landed this "
       "commit) + pool surgery dual-file: TRIAL-LABOR-W20-GENERATE "
       "flipped done (same-grammar rerun refusal = idempotence by "
       "design; flip frees autofill) + 4 SCREEN shards enrolled (SHARD-0.."
       "3, stride i%4 of 231, lane-pinned bm-c r429 checkpoint locality, "
       "RAM gate 4GB park-honest at 1.2GB free -- autofill retries on "
       "night-window RAM free); (5) S3: satengine ALIVE rc0 + idle "
       "green_idle=false RAM-gate honest (4.6%) + U256 deferred + MV V4 "
       "no bm-a director-review row yet (structural wait) + sentinel "
       "foreign edit re-checked (origin v1.0, stays bm-b's uncommitted); "
       "(6) S6 light: dualrun ZERO-DRIFT streak 51 + audit FLAG "
       "ignition_sla (fresh-enrollment face answered-by-design) + wm "
       "insufficient_history (bars due 15:30) + token delta=0; (7) S7 "
       "attrition 4 CLEAN + quad green + counter 1028->1029")

VERDICT = ("green: W20 runner LANDED (funnel 4/5, dead-window estate "
           "absorbed+verified: selftest 20/20 + gates PASS + grammar "
           "sha frozen-match) + GENERATE consumed + SCREEN 4 shards "
           "enrolled lane-pinned bm-c (RAM gate 1.2GB<4GB park-honest, "
           "autofill retries on night-window free) -> screen-finalize "
           "next after burn; bars 10-15 due 15:30 -> papers full chain "
           "next window; MV V4 i2v still gated on bm-a director review "
           "(structural wait); U256 claims RAM-gate deferred honest")

NEXT = ("r1029: (1) W20 SCREEN watch: autofill claims SHARD-0..3 on RAM "
        "free (night window) -> burn complete (231/231 rows in CKPT_DIR) "
        "-> screen-finalize (bm-c local, needs 31 cand + 200 nulls) -> "
        "survivors + family axe -> judge-prep/judge/judge-finalize "
        "(family blocks, dual-nulls B=2000/P=2000) -> intake -> sec.7 "
        "backfill + 48h CEO clock + attrition 2 rows; (2) bars 10-15 due "
        "15:30 -> update_daily gate -> papers full chain; (3) MV V4: "
        "watch bm-a director review of JAY-REDO-KF-BOARD-r1025.jpg -> "
        "i2v INT8 768P full batch (batch-sampling law O-20261014-1325); "
        "(4) U256 bmc-w001/w003 claims on RAM gate open; (5) S8 prompt "
        "wiring: sentinel_bm-c.py foreign edit watch (origin still v1.0)")

ARTIFACT = ("r1028: W20 runner landed (scripts/trial_labor_w20.py + "
            "results/trial_labor_w20/{w20_grammar.json,w20_candidates."
            "json,prep_state.json} estate) + TRIAL_GRAMMAR_LEDGER W20 "
            "row + dual-file pool surgery (GENERATE done flip + 4 "
            "SCREEN shards) + results/_r1028bmc_w20_pool_surgery.py "
            "(this commit)")

PROD_LANES = ("CPU=W20 SCREEN 4 shards ready lane-pinned bm-c (autofill "
              "burn on RAM free, night window) -> screen-finalize next ; "
              "GPU=MV V4 POOL-0014 awaiting bm-a director review -> i2v "
              "INT8 768P full batch next ; N1=W246 bm-a seat in-flight "
              "(chain theirs) ; U256 w001/w003 = RAM gate deferred ; "
              "MEMORY-GATE=HQ-MemoryBudgetGate armed 4h (bm-c leg closed "
              "r1027)")

SELFPROOF = {
    "占用一行": ("CPU=W20 SCREEN 4 shards enrolled (autofill burns on RAM "
                "free; RAM gate 1.2GB<4GB park-honest) ; GPU=MV 车道候 "
                "bm-a 导演席批 (POOL-0014 KF 14/14+LOOKBOARD 已交付) + "
                "ComfyUI 常驻 + album serve"),
    "当前活": "r1028 W20 runner absorb closeout (selftest 20/20 + pool surgery + SCREEN 4 shards enrolled)",
    "最近实物": ("scripts/trial_labor_w20.py + results/trial_labor_w20/ "
                "三件 + TRIAL_GRAMMAR_LEDGER W20 行 + 双文件池 4 SCREEN "
                "shard 条目（14:34·本窗 commit）"),
    "下个交付物": ("W20 SCREEN 烧完→screen-finalize→judge→intake（夜窗 RAM "
                  "释后 autofill 烧）+ bars 15:30 papers 全链（窗≤48h）"),
    "队列水位": ("池 ready=4（全 W20 screen·lane bm-c）·N1 引擎 0 在烧"
                "（W246 bm-a 在飞）·U256 候 RAM 门·P2/P3 空·jobs 0"),
}

STATE_NOTE = ("r1028: W20 runner-build estate absorbed (31st absorb "
              "instance: dead window 14:10-14:20 built runner + ran "
              "grammar/generate/screen-prep, died pre-commit; this "
              "window machine-verified (selftest 20/20 + gates + sha "
              "frozen-match) and landed it) + GENERATE pool flip done + "
              "4 SCREEN shards enrolled (RAM-park honest) | bars 10-15 "
              "due 15:30 -> papers full chain next window | W20 checkpoint "
              "dir = machine-local gitignored r429")


def upd(d, **kv):
    d.update(kv)
    return d


def main():
    # --- state-bm-c.json ---
    sp = os.path.join(ROOT, "state-bm-c.json")
    with open(sp, encoding="utf-8") as fh:
        st = json.load(fh)
    upd(st,
        clock_read=NOW_ISO, ts=NOW_ISO, updated=NOW_ISO, updated_at=NOW_ISO,
        last_seen=NOW_ISO, last_seen_at=NOW_ISO, last_round_at=NOW_ISO,
        last_round_closed=NOW_ISO, last_action_at=NOW_ISO,
        current_task_at=NOW_ISO, last_orders_seen=NOW_ISO,
        last_orders_read_at=NOW_ISO, last_decisions_seen=NOW_ISO,
        last_decisions_read_at=NOW_ISO, last_decisions_at=NOW_ISO,
        last_round_summary_at=NOW_ISO, last_round_ts=NOW_ISO,
        current_task="r1028 closeout: W20 runner-build estate absorbed+landed (funnel 4/5 closed) + GENERATE flip + 4 SCREEN shards enrolled (RAM-park honest)",
        did=DID, verdict=VERDICT, note=STATE_NOTE, next=NEXT, next_pointer=NEXT,
        last_round="r1028", last_round_label="r1028", round_no_label="r1028",
        round_no=1029, loop_round=st.get("loop_round", 993),
        last_round_summary="r1028: W20 runner landed (dead-window estate absorbed+verified: selftest 20/20 + grammar sha frozen-match + G-battery 8/8) + GENERATE consumed + 4 SCREEN shards enrolled (RAM-park honest) + S6 light + S7 quad green",
        last_action="r1028 closeout (W20 runner absorb + GENERATE flip + SCREEN shard enrollment)",
        latest_artifact=ARTIFACT, last_artifact=ARTIFACT,
        recent_artifact=ARTIFACT, next_milestone="r1029+: W20 screen burn (autofill on RAM free) -> screen-finalize -> judge -> intake; bars 15:30 papers full chain",
        prod_lanes=PROD_LANES,
        full_load_selfproof=SELFPROOF,
        activity_now=f"{NOW_ISO} | r1028 | bm-c: W20 runner absorb closeout (selftest 20/20 + GENERATE flip + 4 SCREEN shards) | counter 1028->1029 (r1028 exec)",
        now_active=f"{NOW_ISO} | r1028 | bm-c: W20 runner absorb closeout (selftest 20/20 + GENERATE flip + 4 SCREEN shards) | counter 1028->1029 (r1028 exec)",
        verify="receipts: W20 selftest 20/20 + smoke 49/49 + status gates PASS + grammar sha ff00b0896b088b5a frozen-match + candidates n_cells=31 + prep G-battery 8/8 (1253 starts) + pool readback-verify PASS dual-file + dualrun ZERO-DRIFT streak 51 + attrition 4 CLEAN + quad green + orphan face=2 zero-kill",
        heartbeat_epoch_utc=EPOCH,
        r1028_closeout_note=("r1028 closeout: clean continuation absorb window (31st "
                            "instance, dead window 14:10-14:20 self-labeled r1028 built "
                            "runner+grammar+generate+screen-prep, died pre-commit with "
                            "zero own commits; state counter was 1028 at open, executed "
                            "as r1028 per counter, advanced 1028->1029 so next session "
                            "=r1029; zero double-count: S0.5 dual-delta FALSE this "
                            "window (ord 3b1ca198/dec ab3f0cc9 current, zero rows owed)"),
        orphan_face=2, orphan_faces=2,
        head_sha="bigmoney closeout commit rides this window",
        )
    st["d19_watermark_guard"]["ts"] = NOW_ISO
    st["d19_watermark_guard"]["round_ref"] = 1029
    with open(sp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(st, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    chk = json.load(open(sp, encoding="utf-8"))
    assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
    assert chk["round_no"] == 1029

    # --- heartbeat fleet/machines/bm-c.json ---
    hp = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
    with open(hp, encoding="utf-8") as fh:
        hb = json.load(fh)
    upd(hb,
        last_seen=NOW_ISO, ts=NOW_ISO, updated=NOW_ISO, updated_at=NOW_ISO,
        last_seen_at=NOW_ISO, last_round_at=NOW_ISO, last_action_at=NOW_ISO,
        current_task_at=NOW_ISO, current_task_ts=EPOCH,
        current_task="r1028 closeout: W20 runner-build estate absorbed+landed (funnel 4/5 closed) + GENERATE flip + 4 SCREEN shards enrolled (RAM-park honest)",
        did=DID, verdict=VERDICT, note=STATE_NOTE, next=NEXT, next_pointer=NEXT,
        last_round="r1028", last_round_label="r1028", round_no_label="r1028",
        last_round_summary="r1028: W20 runner landed (dead-window estate absorbed+verified) + GENERATE consumed + 4 SCREEN shards enrolled (RAM-park honest) + S6 light + S7 quad green",
        last_action="r1028 closeout (W20 runner absorb + GENERATE flip + SCREEN shard enrollment)",
        latest_artifact=ARTIFACT, last_artifact=ARTIFACT, recent_artifact=ARTIFACT,
        next_milestone="r1029+: W20 screen burn (autofill on RAM free) -> screen-finalize -> judge -> intake; bars 15:30 papers full chain",
        prod_lanes=PROD_LANES, full_load_selfproof=SELFPROOF,
        activity_now=f"{NOW_ISO} | r1028 | bm-c: W20 runner absorb closeout (selftest 20/20 + GENERATE flip + 4 SCREEN shards) | counter 1028->1029 (r1028 exec)",
        now_active=f"{NOW_ISO} | r1028 | bm-c: W20 runner absorb closeout (selftest 20/20 + GENERATE flip + 4 SCREEN shards) | counter 1028->1029 (r1028 exec)",
        verify="receipts: W20 selftest 20/20 + smoke 49/49 + status gates PASS + grammar sha frozen-match + pool readback-verify PASS dual-file + dualrun streak 51 + attrition CLEAN + quad green",
        heartbeat_epoch_utc=EPOCH,
        idle_rounds=0, agenda_starved=False,
        orphan_face=2, orphan_faces=2,
        cpu_pct=9.0, cpu_util_pct=9.0, cpu_idle_pct=91.0,
        free_ram_gb=1.2, ram_free_gb=1.2, idle_ram_gb=1.2,
        gpu_free_vram_mib=15063, gpu_free_vram_mb=15063,
        gpu_free_mib=15150, gpu_free_mb=15150,
        gpu_idle_vram_mib=15063, gpu_idle_vram_mb=15063,
        gpu_idle_mib=15063, gpu_idle_mb=15063,
        gpu_vram_free_mb=15063, free_vram_mb=15063,
        gpu_util_pct=1.0,
        head_sha="bigmoney closeout commit rides this window",
        )
    hb["d19_watermark_guard"]["ts"] = NOW_ISO
    hb["d19_watermark_guard"]["round_ref"] = 1029
    with open(hp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(hb, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    chk = json.load(open(hp, encoding="utf-8"))
    assert isinstance(chk["heartbeat_epoch_utc"], int), "hb epoch must be int"

    # --- round report (append-only, binary-safe per r962 law) ---
    rp = os.path.join(ROOT, "round_reports-bm-c.md")
    with open(rp, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(REPORT_ROW + "\n")
    print(json.dumps({"now": NOW_ISO, "epoch": EPOCH,
                      "state_round_no": 1029,
                      "report_row_bytes": len(REPORT_ROW.encode('utf-8'))},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
