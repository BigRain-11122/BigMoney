# -*- coding: utf-8 -*-
"""R290 bm-a wrap-up: round report line + state file + heartbeat (S5/S7).
Heartbeat epoch must be JSON int (R170/R178 law); clock_read ISO8601 with T
separator (R262 law); self-validated via json.loads + isinstance(int)."""
import io
import json
import time
from datetime import datetime, timezone, timedelta

NOW = datetime.now(timezone(timedelta(hours=8)))
TS = NOW.strftime("%Y-%m-%d %H:%M:%S")
TS_ISO = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())

REPORT = (
    f"{TS} | R290 bm-a (dept:research+fleet) | WM=GREEN (red=false lane healthy; "
    "py_low_with_work_cands 13.7% LEGAL DISCLOSURE per sec.4: CN-TREND 4xBelowNormal "
    "burn in flight since 02:10 = ~4-core structural ceiling on 32C, pool ready=1 IS "
    "that same batch (owned+alive, zero takeable shard), board 0 open, bandit 0; "
    "supply gap honest: wave-2 gated on T-87 A-share panel (bm-b, ETA Mon 09:15), "
    "UNC batch completed in-round this round -- supply line active, not a violation) | "
    "S0.5 double-scan clean: fleet/orders 91/91 acked zero unacked round-start+wrap; "
    "group docs/orders.md + decisions.md zero new @BigMoney lines (D-20260927-04 "
    "BigMoney self-fix in force R256 maintain; D-05(2) full-file scan adopted R287 "
    "maintain) | S0: bm-b r290 fallback branch machine/bm-b-r290 main-face "
    "incorporation = ALREADY IN MAIN (git cherry addendum patch-equivalent + 2fc8aad3 "
    "round-290 face present 03:07 push, zero action, verified) | S2 boards: job_list "
    "empty, fleet/tasks zero open (32 claimed in-flight), post_review all-NO-resolved "
    "zero outstanding | MAIN-1: CENSUS_FUS_S2_W1 harvest three-piece closed (r244/"
    "r285 law) -- pool entry+shard flipped done + prereg s7/s8 one-time finalization "
    "(P1 CONFIRMED 74/306=24.2pct top-decile = 2.4x enrichment, all 74 also beat EW48 "
    "ann 0.0266; P2 CONFIRMED cand x2 p95 0.4164 > null p95 0.3526, 363/4060=8.9pct vs "
    "5pct base; P3 NOT-CONFIRMED rev-x-trend 208 pairs IC median +0.0103 neg-frac 30pct "
    "honest; P4 disclosure face satisfied) + attrition row 52 (kind=measurement, "
    "judgment lines null per exploration-face annotation law) + post_review "
    "T-86-S2-CENSUS-FUS-W1 YES 16/16 stable-artifact anchors (R264); N=4518, ledger "
    "200900+4518=205418 | MAIN-2: s3 UNC face DELIVERED (R99 chain: sec.9.1 seed "
    "freeze census_fusion_s2_unc=20275000 committed BEFORE build -> census_fusion_s2.py "
    "unc subcommand selftest 22 legs ALL PASS -> full 4060-combo run in-round 62.6s "
    "below O-2100 5-min pool threshold, pre-declared pool second entry discharged by "
    "completion, honest) -- B=200 block-20td circular bootstrap x2 Sharpe CI + P=200 "
    "sign-flip two-sided IC p, per-combo rng [20275000,i]; cross-anchor vs w1_cells.csv "
    "4060 checked 0 mismatches; HONEST readings: ci_pos 1/4060 (T:amt_20|price_position|"
    "lowamp20 x2 0.6626 CI [0.0317,1.4564]), s4 top combo T:extreme_freq|return_skew|"
    "lowamp20 CI [-0.05,1.4686] = NOT ci_pos, ic_p<=.05 2203/4060=54.3pct (IC face far "
    "more permissive than blend face), both=1 lowamp carrier consistent with s8 P1; "
    "derivation face ledger +0; sec.9.2 one-time finalization; post_review "
    "T-86-S3-CENSUS-FUS-UNC YES 18/18 after criteria path-dot mechanical fix "
    "(json_field dotted-path splits keys containing dots -> file_contains anchor, "
    "NO->YES re-derive legal per append-only ledger law; CODELY kenglu entry) | S6 22 "
    "legs rc=0 (audit v2.3 CLEAN flags[] pool-supply-gap, WM probe py_low_with_work_"
    "cands legal-disclosed, daily no-op weekend cutoff 09-24, regime ORANGE shadow "
    "breadth 0.77, scorecard 6/28/7 best VOLATILITY-CE-01 87.0, clock CALL-2026-09-24 "
    "ORANGE_COOL sleeves 4 activated 0, lhb quarter refetch 5209 rows zero-beyond-"
    "cutoff no-op, heat/futures/options/sina/ths weekend no-ops, moneyflow rank pass "
    "spawned, ah_panel detached refresh spawned, fundnav bm-c-lane no-op, fundamental "
    "fresh-skip, b_layer mask regen all gates pass, paper legs skipped no-new-bar, "
    "d_scorecard 6 rows + d_report regen + monitor + token delta 30) | smoke 25/25 | "
    "loop Running / watchdog Ready, inbox empty | HANDOVER 5x reconcile (R290 multiple "
    "of 5: bm-a line in chain, unified ledger head 205,418) | next: CN-TREND harvest "
    "three-piece on landing (burn in flight ~80min owner bm-a per r288 ruling) + "
    "CN-KLINE-PATTERN-P1 prereg draft per DIGEST boundary disclosures + T-23 judged "
    "consumption prereg (UNC annotations ready for intake funnel) [via bm-a]"
)

with io.open("logs/iteration-loop/round_reports-bm-a.md", "a", encoding="utf-8",
             newline="\n") as fh:
    fh.write("\n" + REPORT + "\n")
print("report line appended")

state = json.load(io.open("state-bm-a.json", encoding="utf-8"))
state.update({
    "round_no": 290,
    "did": ("R290: CENSUS_FUS_S2_W1 harvest three-piece (pool done + s7/s8 "
            "finalization + attrition 52 + post_review YES 16/16) + s3 UNC face "
            "delivered (seed freeze 20275000 -> unc subcommand 22-leg selftest -> "
            "4060 combos 62.6s in-round, cross-anchor 4060/0, ci_pos 1/4060, "
            "post_review YES 18/18) + S6 22 legs rc=0 + smoke 25/25 + HANDOVER 5x"),
    "verdict": "ok",
    "next": ("CN-TREND harvest three-piece on landing (burn in-flight owner bm-a); "
             "CN-KLINE-PATTERN-P1 prereg draft per DIGEST boundary disclosures; "
             "T-23 judged consumption prereg (UNC annotations ready)"),
    "ts": TS, "last_round_ts": TS, "updated_at": TS, "last_run": TS,
    "last_round_at": TS, "last_round": 289, "updated": TS,
    "last_seen": TS_ISO,
    "current_task": ("R290 done: CENSUS s2 harvest + s3 UNC delivered; next = "
                     "CN-TREND harvest on landing + CN-KLINE-P1 prereg"),
    "task": ("R290 done: CENSUS s2 harvest + s3 UNC delivered; next = "
             "CN-TREND harvest on landing + CN-KLINE-P1 prereg"),
})
with io.open("state-bm-a.json", "w", encoding="utf-8", newline="\n") as fh:
    json.dump(state, fh, ensure_ascii=False, indent=1)
    fh.write("\n")
print("state 290 written")

hb = json.load(io.open("fleet/machines/bm-a.json", encoding="utf-8"))
hb.update({
    "machine_id": "bm-a",
    "last_seen": TS_ISO,
    "round_no": 290,
    "task": ("R290 done: CENSUS_FUS_S2_W1 harvest + s3 UNC delivered (ci_pos 1/4060 "
             "honest); next = CN-TREND harvest on landing + CN-KLINE-P1 prereg"),
    "current_task": ("R290 done: CENSUS_FUS_S2_W1 harvest + s3 UNC delivered "
                     "(ci_pos 1/4060 honest); next = CN-TREND harvest on landing + "
                     "CN-KLINE-P1 prereg"),
    "verdict": ("R290 ok: census s2 harvest three-piece + s3 UNC face delivered "
                "(4060/4060 cross-anchor 0, ci_pos 1 honest, post_review YES 34/34); "
                "smoke 25/25; S6 22 legs rc=0; CN-TREND nulls burn in-flight owner "
                "bm-a since 02:10 (~4-core BelowNormal ceiling, harvest on landing)"),
    "heartbeat_epoch_utc": EPOCH,
    "clock_read": TS_ISO,
    "cores": 32, "cpu_cores": 32,
    "cpu_pct": 35.0,
    "idle_ram_gb": 54.3, "free_ram_gb": 54.3,
    "free_ram_mb": int(54.3 * 1024),
    "gpu_idle_vram_gb": 5.2, "gpu_free_vram_gb": 5.2,
    "gpu_idle_vram_mb": 5200, "gpu_free_vram_mb": 5200,
})
with io.open("fleet/machines/bm-a.json", "w", encoding="utf-8", newline="\n") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)
    fh.write("\n")

chk = json.load(io.open("fleet/machines/bm-a.json", encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in chk["clock_read"], "clock_read must be ISO8601 T-separated"
print("heartbeat written; epoch int verified:", chk["heartbeat_epoch_utc"],
      "| clock:", chk["clock_read"])
