"""r485 bm-c S7 bookkeeping part 2: heartbeat (fixed % bug), state refresh
with post-flip facts, CODELY pit line. Part 1 (round report + HANDOVER +
state core) already landed; heartbeat write died on a % escape bug -> this
script completes it. Programmatic json + reparse self-check."""
import datetime
import json
import os
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

now_dt = datetime.datetime.now().astimezone()
ts_line = now_dt.strftime("%Y-%m-%d %H:%M:%S")
ts_iso = now_dt.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())

CT = ("当前活: W3 judge SHARD-0 烧毕+双层 done-flip 收口（195/195·claim 17:04:51→flip "
      "17:11:50）·SHARD-{1,2,3} ready 待 autofill 续烧 | 最近实物: results/mass_trial/"
      "w3_judge_shard_0of4.jsonl（195 格产物·随收口 commit 入库 r310）+runnable_pool "
      "SHARD-0 双翻（17:11:50）+入池 bc73edd97+claim 9b2dc31eb @ " + ts_iso +
      " | 下个里程碑: SHARD-{1,2,3} 续烧→4/4→judge-finalize --wave 3+池双翻同窗（r668）"
      "≤10-12；fund-trio finalize 10-05 10:30（bm-b）；验收 10-08；开市 10-09")

# --- state refresh (post-flip facts) ---
ST = os.path.join(ROOT, "state-bm-c.json")
st = json.load(open(ST, encoding="utf-8"))
st["last_round"] = ("r485 bm-c: W3 judge adoption+enrollment+SHARD-0 ignition+"
                    "done-flip same window (prep PASS 1028s, 785->777 collapse 6 "
                    "clusters, adopted 150f36fb4; +4 pool entries bc73edd97 N_judge=777 "
                    "i%4 195/194/194/194; autofill r351 defers x2 then 17:04:44 "
                    "launched, claim 9b2dc31eb DELIVERED; SHARD-0 burn pid 25540 "
                    "195/195 rows complete, two-layer done-flip 17:11:50 + claim "
                    "backfill + ckpt committed; bm-a seat MSG-1655 -> their r687 "
                    "self-yield a6fc0132d, seed 20287000 dropped unpushed)")
st["current_task"] = CT
st["did"] = ("r485 bm-c W3 judge ignition round: (1) S0 pull blocked by daemon "
             "treadmill -> absorb 150f36fb4 (churn + w3_judge_state.json adoption, "
             "777 cells) -> merge 5d53b5c9e (bm-b S6 churn 59 faces zero-UU); (2) "
             "MAIN PRODUCT: W3-JUDGE enrollment +4 shards bc73edd97 (raw-text "
             "surgical r678 + anti-double + serial-position gates; N_judge=777 i%4 "
             "195/194/194/194; pool 372->376); (3) seat collision CLEAN: bm-a "
             "MSG-1655 -> their r687 self-yield a6fc0132d merged (commit-time law, "
             "20287000 dropped unpushed) -> MSG moved to processed; (4) ignition: "
             "autofill ticks 17:01:02/17:03:02 claim_lost_yield (origin-pool-past-"
             "HEAD r351 defer) -> churn absorb ad7b27993 + merge 2c5254577 -> tick "
             "17:04:44 launched, claim commit 9b2dc31eb, push_verify DELIVERED; "
             "(5) SHARD-0 burn pid 25540 completed 195/195 rows in-window (ckpt "
             "mtime 17:10:31) -> two-layer done-flip 17:11:50 (_r485bmc_w3_shard0_flip."
             "py: gates 1-4 PASS + claim backfill w3-judge-0of4.bm-c.json + disk "
             "re-verify sha16=1bbebdff2a41a4cc + round-report/HANDOVER wording "
             "surgery); (6) S1 smoke 48/48; S2 boards empty; S3 satengine rc0 + "
             "watermark green; (7) S0.5 orders 154/155 zero-unacked, D-19 double "
             "MATCH, inbox 0; (8) S6 38/38 rc0 (dualrun streak 51, 376 entries); "
             "(9) S7 quartet green + attrition CLEAN + HANDOVER 5x (r481-485).")
st["verify"] = ("adoption = w3_judge_state.json (n_judge_cells 777 == len(kept); "
                "candidates sha16 d0fc84b31113d572 cross-checked) + 150f36fb4; "
                "enrollment = results/_r485bmc_w3_judge_enroll.json (reparse + "
                "difflib removed==2) + bc73edd97; ignition = autofill last_tick "
                "verdict=launched pid 25540 + claim 9b2dc31eb push_verify DELIVERED; "
                "SHARD-0 flip = _r485bmc_w3_shard0_flip.py gates 1-4 PASS (195/195 "
                "unique i%4==0 rows, crash-fuse clean, pre/post semantic asserts, "
                "disk re-verify, sibling shards untouched, 376 entries) + claim file "
                "state=closed; seat yield = a6fc0132d in HEAD ancestry rc0; S6 = "
                "results/_r485bmc_s6_log.txt 38/38 rc0; state json.loads self-check "
                "+ heartbeat epoch int + clock T-sep POST-WRITE (this script)")
st["next"] = ("(a) r486: SHARD-{1,2,3} continue burn via autofill ticks (claim-by-"
              "file; multi-machine shard-claim legal; ckpt resume idempotent). "
              "(b) after 4/4 done: judge-finalize --wave 3 (777-cell completeness "
              "probe + r482 id-dedup probe post-merge re-run + single-shot ledger + "
              "w3_judge.json G1/G2/DSR/PBO/E[FP] + pool dual-flip same window r668 "
              "+ treasure-capture question + sec.7/8 backfill; 48h CEO report clock "
              "starts). (c) fund-trio finalize 10-05 10:30 (bm-b owner, watch only). "
              "(d) O-2115/O-2030 acceptance 10-08. (e) market reopen 10-09.")
st["heartbeat_epoch_utc"] = epoch
st["clock_read"] = ts_iso
st["last_seen"] = ts_iso
st["updated"] = ts_iso
st["updated_at"] = ts_iso
with open(ST, "w", encoding="utf-8", newline="") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1)
st2 = json.loads(open(ST, encoding="utf-8").read())
assert st2["round_no"] == 485 and isinstance(st2["heartbeat_epoch_utc"], int)
assert "T" in st2["clock_read"] and "195/195" in st2["last_round"]
print("STATE REFRESH OK")

# --- heartbeat (fixed formatting: f-strings, no % ambiguity) ---
HB = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
hb = json.load(open(HB, encoding="utf-8"))
hb["round_no"] = 485
hb["round_no_label"] = "r485"
hb["last_seen"] = ts_iso
hb["updated_at"] = ts_iso
hb["updated"] = ts_iso
hb["ts"] = ts_line
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = ts_iso
hb["current_task"] = CT
hb["activity_now"] = ("W3 judge SHARD-0 burned+flipped same window (195/195 rows, "
                      "two-layer done 17:11:50, claim backfilled); SHARD-{1,2,3} "
                      "ready awaiting autofill ticks; bm-a seat-yield merged "
                      "(r687 a6fc0132d); S6 38/38 rc0; orders zero-unacked; D-19 "
                      "double MATCH")
hb["latest_artifact"] = ("results/mass_trial/w3_judge_shard_0of4.jsonl (195-cell "
                         "product, committed) + results/runnable_pool.json "
                         "MASS-TRIAL-W3-JUDGE-SHARD-0 done (+4 enrolled bc73edd97) "
                         "+ results/pool_claims/MASS-TRIAL-W3-JUDGE-SHARD-0/"
                         "w3-judge-0of4.bm-c.json (closed)")
hb["next_milestone"] = ("SHARD-{1,2,3} burn -> 4/4 -> judge-finalize --wave 3 + "
                        "pool dual-flip same window (r668) <=10-12; fund-trio "
                        "finalize 10-05 10:30 (bm-b); acceptance 10-08; market "
                        "reopen 10-09")
hb["prod_lanes"] = ("W3-JUDGE lane: SHARD-0 done (bm-c), SHARD-{1,2,3} ready "
                    "unclaimed (autofill continues); FUND trio NULLS bm-b "
                    "in-flight (watch only); boards empty; no new orders")
hb["verdict"] = st["last_round"]
with open(HB, "w", encoding="utf-8", newline="") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)
hb2 = json.loads(open(HB, encoding="utf-8").read())
assert hb2["round_no"] == 485 and isinstance(hb2["heartbeat_epoch_utc"], int)
assert "T" in hb2["clock_read"]
print("HEARTBEAT OK (epoch=%d)" % epoch)

# --- CODELY.md pit line ---
CO = os.path.join(ROOT, "CODELY.md")
co_raw = open(CO, encoding="utf-8", newline="").read()
marker = "r485 bm-c] \u5165\u6c60\u811a\u672c"
assert co_raw.count(marker) == 0, "CODELY r485 line already present"
co_eol = "\r\n" if co_raw.endswith("\r\n") else "\n"
co_line = (
    "- [2026-10-04 17:1x r485 bm-c] \u5165\u6c60\u811a\u672c ser() \u884c\u8fde"
    "\u63a5 EOL \u4e0e\u5bbf\u4e3b\u6587\u4ef6\u4e0d\u4e00\u81f4\u5751\uff08r481 "
    "\u8303\u5f0f\u955c\u50cf\u5b9e\u5f39\uff1arunnable_pool.json=CRLF \u5bbf\u4e3b"
    "\u800c ser() \u7684 json.dumps \u884c\u8fde\u63a5\u7528 LF\u2192\u63d2\u5165"
    "\u5757\u5185\u90e8\u6df7 EOL\u9762\uff0c\u4e0b\u8f6e daemon settle \u5199"
    "\u56de\u65f6\u6574\u5757\u5f52\u4e00 CRLF=churn absorb \u51fa 197 \u884c"
    "\u5168\u5757\u5047 diff\uff08word-diff \u5168 ~ =EOL-only \u5b9a\u8c23\u6cd5"
    "\u00b7\u8bed\u4e49\u96f6\u53d8\u5316\u96f6\u4f24\u5bb3\uff09\uff0c\u4f46\u6536"
    "\u53e3\u7a97\u591a\u4ed8\u4e00\u8f6e\u300c\u771f\u5dee\u5f02\u5b9a\u4f4d\u300d"
    "\u8bca\u65ad\u6210\u672c\u3002How to apply\uff1a\u6c60\u9762/\u5171\u4eab json "
    "\u884c\u7ea7\u624b\u672f\u7684\u884c\u8fde\u63a5\u4e00\u5f8b\u7528\u63a2\u6d4b"
    "\u5230\u7684\u5bbf\u4e3b eol\uff08ser() \u6539 eol+\"  \".join \u5f62\uff09"
    "\uff1b\u6536\u53e3\u7a97\u89c1\u5927\u5757\u5047 diff \u5148\u8dd1 word-diff "
    "\u5b9a\u8c23 EOL-only \u518d\u5b9a\u771f\u5dee\u5f02\uff08r641 \u590d\u73b0"
    "\u8bc1\u4f2a\u5f8b\u65cf\u9762\uff09\u3002")
with open(CO, "a", encoding="utf-8", newline="") as fh:
    fh.write(co_line + co_eol)
co2 = open(CO, encoding="utf-8", newline="").read()
assert co2.count(marker) == 1
print("CODELY OK (+1 pit line)")
print("BOOKKEEPING2 ALL OK")
