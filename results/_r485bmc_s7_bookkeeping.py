"""r485 bm-c S7 bookkeeping: round report line + HANDOVER 5x line +
state-bm-c.json + heartbeat + CODELY pit line. Programmatic json writes
with reparse self-check (r645 law); append-only marker gates (r679 law);
heartbeat epoch = python int (R170/R178); clock T-sep ISO (R262)."""
import datetime
import json
import os
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

now_dt = datetime.datetime.now().astimezone()
ts_line = now_dt.strftime("%Y-%m-%d %H:%M:%S")
ts_iso = now_dt.strftime("%Y-%m-%dT%H:%M:%S+08:00")
ts_short = now_dt.strftime("%H:%M:%S")
epoch = int(time.time())

# --- live facts (zero hand-copy) ---
ckpt_rows = 0
ck = os.path.join(ROOT, "results", "mass_trial", "w3_judge_shard_0of4.jsonl")
if os.path.exists(ck):
    with open(ck, encoding="utf-8") as fh:
        ckpt_rows = sum(1 for _ in fh)


def _proc_alive(pid):
    try:
        out = subprocess.run(
            ["tasklist", "/FO", "CSV"], capture_output=True, creationflags=0x08000000,
            timeout=30).stdout.decode("gbk", "replace")
        for ln in out.splitlines():
            parts = [p.strip('"') for p in ln.split('","')]
            if len(parts) > 1 and parts[1].isdigit() and int(parts[1]) == pid:
                return True
    except Exception:
        pass
    return False


burn_alive = _proc_alive(25540)

# --- 1. round report main line ---
RR = os.path.join(ROOT, "round_reports-bm-c.md")
rr_raw = open(RR, encoding="utf-8", newline="").read()
assert rr_raw.count("\uff5cr485\uff5c") == 0, "r485 marker already present"
eol = "\r\n" if rr_raw.endswith("\r\n") else "\n"
main_line = (
    "2026-10-04 17:%s\uff5cr485\uff5cdept:\u7b56\u7565/\u7814\u7a76"
    "\uff08W3 judge \u6536\u517b+\u5165\u6c60+\u70b9\u706b\u8f6e\u00b7T-158 "
    "\u5728\u518c\uff09\uff5cwatermark verdict=\u7eff\uff08red=false\u00b7healthy\u00b7"
    "\u6c34\u4f4d\u63a2\u9488 py_low_board_clear \u540e\u6c60\u704c 4 \u5206\u7247="
    "\u4f9b\u7ed9\u6062\u590d\u6b63\u8def\uff09\uff5c\u5f53\u524d\u6d3b=W3 judge "
    "SHARD-0 \u70e7\u5f55\u5728\u98de\uff08pid 25540\u00b7judge --wave 3 --shard 0 "
    "--shards 4\u00b7195 cells\u00b7ckpt %d \u884c\u589e\u957f\u4e2d\u00b7CPU 100%%"
    "\u00b7burn_alive=%s\uff09\uff5c\u6700\u8fd1\u5b9e\u7269=results/mass_trial/"
    "w3_judge_state.json \u6536\u517b\uff08777 \u5224\u51b3\u683c=785-8 \u584c\u7f29 "
    "6 \u7c07\u00b7commit 150f36fb4\uff09+runnable_pool +4 \u6761\u76ee "
    "MASS-TRIAL-W3-JUDGE-SHARD-0..3\uff08commit bc73edd97\u00b7r678 \u5916\u79d1+"
    "\u4e32\u884c\u4f4d\u95e8\uff09+claim commit 9b2dc31eb @ 2026-10-04T17:0x+08:00"
    "\uff5c\u4e0b\u4e2a\u91cc\u7a0b\u7891=4/4 \u70e7\u6bd5\u2192judge-finalize --wave 3+"
    "\u6c60\u53cc\u7ffb\u540c\u7a97\uff08r668 \u5f8b\uff09\u226410-12\uff08O-2115\uff09"
    "\uff1bfund-trio finalize 10-05 10:30\uff08bm-b\uff09\uff1bO-2115/O-2030 "
    "\u9a8c\u6536 10-08\uff1b\u5f00\u5e02 10-09\uff08\u226448h\uff09\uff5cS0: pull "
    "--rebase \u88ab daemon treadmill \u963b\uff084 \u810f\u9762\uff09\u2192absorb "
    "150f36fb4\uff08churn+prep \u4ea7\u7269\u6536\u517b 25033 \u884c\uff09\u2192merge "
    "5d53b5c9e\uff08bm-b S6 churn 59 \u9762\u96f6\u4ea4\u96c6\u96f6 UU\uff09\u2192"
    "enrollment bc73edd97\u2192churn absorb ad7b27993\uff08settle EOL \u5f52\u4e00"
    "\u9762\uff09\u2192merge 2c5254577\uff08bm-b keepalive+bm-a r685/r687 yield "
    "\u5408\u6d41\u96f6 UU\uff09\u2192daemon claim 9b2dc31eb\u2192push_verify "
    "DELIVERED\uff5cS0.5: \u4ee4\u5dee\u96c6 0\uff08154/155\u00b7\u8f6e\u9996\u626b"
    "\u00b7ack \u591a 1=README \u5386\u53f2\u65e0\u5bb3\uff09\u00b7D-19 decisions "
    "4E5BE321+orders 68947C17 \u53cc MATCH\uff08Tools/d19_check.py \u5355\u6e90+"
    "_r458bmc per-key \u590d\u6838\uff09\u96f6\u6d88\u8d39\u00b7inbox 0\u2192MSG-1655 "
    "\u968f merge \u843d\u6811\uff08bm-a \u5e2d\u4f4d\u516c\u793a\u2192\u5176 r687 "
    "\u5df2\u81ea\u884c\u8ba9\u8def a6fc0132d=commit \u65f6\u95f4\u5e8f 16:34<16:42"
    "\u00b7\u5176 20287000 \u53cc\u767b\u8bb0 dropped unpushed\u00b7\u4e09 judge \u9762"
    "\u53d6\u672c\u673a canonical\u00b7seat \u5e72\u51c0\uff09\u2192\u79fb processed"
    "\uff5cS1 smoke 48/48\uff5cS2 \u677f\u7a7a\uff08job_list 0\u00b7fleet 0 open\u00b7"
    "45 claimed\uff09\uff5cS3: satengine rc0 \u6d3b\uff08Tools \u6ce8\u518c\u9762 "
    "r467 \u5f8b\uff09\u00b7\u6c34\u4f4d\u7eff\uff5c\u4e3b\u4ea7\u51fa=judge-prep "
    "\u6536\u517b\uff08prep PASS 1028s\u00b7census L/D==\u51bb\u7ed3\u00b7manifest "
    "PASS\uff09+4 \u5206\u7247\u5165\u6c60\uff08N_judge 777\u00b7i%%4 \u8def\u7531 "
    "195/194/194/194\u00b7host_gates=t18 \u6df1\u677f 48 parquet\u3014\u672c\u673a"
    "\u5728\u4f4d\u3015\u00b7anti-double \u95e8+\u4e32\u884c\u4f4d\u95e8\u5168 "
    "judge-family done\u00b7pool 372\u2192376\uff09+\u70b9\u706b\u94fe\uff08autofill "
    "17:01:02/17:03:02 \u4e24 tick claim_lost_yield=origin-pool-past-HEAD r351 "
    "\u8ba9\u8def session \u6536\u53e3\u6b63\u8def\u2192merge \u540e 17:04:44 tick "
    "launched\u00b7claim 9b2dc31eb \u5df2\u63a8 DELIVERED\u00b7SHARD-0 \u5728\u98de"
    "\uff09\uff5cS6 38/38 rc0 NON-ZERO=none\uff08dualrun ZERO-DRIFT streak 51\u00b7376 "
    "entries\u00b7compute_audit py 28%% \u8d77\u98de\u00b7update_daily \u91d1\u5468 "
    "no-op\u00b7clock_call ORANGE_COOL\u00b7fund_premium \u5468\u672b no-op\u00b7"
    "REPORT/LIVE-20261004 \u518d\u751f\uff09\uff5cS7: loop pin5 no-op+watchdog -Force+"
    "\u53cc\u722a LF \u5f52\u4e00\u91cd\u88c5\u00b7attrition CLEAN\uff084 ledgers\u00b7"
    "bm-a r685 \u9762 3 shrink healed \u6ce8\u8bb0\u7167\u5f55\uff09\u00b7orders "
    "\u6536\u5c3e\u4e8c\u626b\u96f6\u5dee\uff5cS4: \u4e00\u6761\u5751\u5f8b\u884c"
    "\uff08ser() EOL join \u4e0e\u5bbf\u4e3b\u4e0d\u4e00\u81f4=daemon settle \u5f52"
    "\u4e00 197 \u884c\u5047 diff\u00b7word-diff \u5b9a\u8c03\u6cd5\uff09\uff5c\u8bb0"
    "\u5206: 2\uff08\u6536\u517b+\u5165\u6c60+\u70b9\u706b=\u53ef\u8dd1\u53ef\u770b"
    "\u5b9e\u7269\u00b7\u975e\u7b49\u5f85\u6001\uff09\uff5c\u8bb0\u8d26\u9884\u7b97: "
    "5/5\uff08state+\u5fc3\u8df3+\u8f6e\u62a5+CODELY+HANDOVER 5x\uff09\uff5c\u672c"
    "\u5730\u672a\u8fbe origin commit \u6570: \u6536\u53e3 push \u540e push_verify "
    "\u81ea\u8bc1\uff5c\u4e0b\u8f6e\u6307\u9488=r486 \u2460watch SHARD-0 \u70e7\u6bd5"
    "\u2192\u6536\u517b checkpoint \u884c\u2192SHARD-{1..3} \u7eed\u70e7\uff08autofill "
    "\u81ea\u7eed\uff09\u24614/4 done\u2192judge-finalize --wave 3\uff08777-cell "
    "\u5b8c\u5907\u63a2\u9488+r482 id \u53bb\u91cd\u63a2\u9488 post-merge \u590d\u8dd1+"
    "\u6c60\u53cc\u7ffb\u540c\u7a97 r668+\u5b9d\u85cf\u6355\u83b7\u95ee\uff09\u2462"
    "fund-trio finalize 10-05 10:30\uff08bm-b \u6b63\u4e3b\u00b7\u89c2\u5bdf\u9762"
    "\uff09\u2463O-2115/O-2030 \u9a8c\u6536 10-08" % (ts_short, ckpt_rows, burn_alive))
with open(RR, "a", encoding="utf-8", newline="") as fh:
    fh.write(main_line + eol)
rr2 = open(RR, encoding="utf-8", newline="").read()
assert rr2.count("\uff5cr485\uff5c") == 1, "r485 marker count!=1"
print("ROUND REPORT OK (+1 line, ckpt=%d, burn_alive=%s)" % (ckpt_rows, burn_alive))

# --- 2. HANDOVER 5x line (insert after header) ---
HO = os.path.join(ROOT, "research", "HANDOVER.md")
ho_raw = open(HO, encoding="utf-8", newline="").read()
assert ho_raw.count("bm-c round 485 \u4e94\u500d\u6570\u6838\u5bf9") == 0
ho_eol = "\r\n" if ho_raw.endswith("\r\n") else "\n"
ho_lines = ho_raw.split(ho_eol)
assert ho_lines[0].startswith("# Bigmoney")
ho_line = (
    "> bm-c round 485 \u4e94\u500d\u6570\u6838\u5bf9\uff082026-10-04 17:1x\u00b7"
    "\u589e\u91cf\u7a97 r481-485 \u4e94\u8f6e\uff09\uff1a\u589e\u91cf\u7a97 "
    "r481-485=bm-c \u9762\uff08**MASS_TRIAL_W3 \u5168\u751f\u547d\u5468\u671f\u4e3b"
    "\u7ebf\uff1ascreen \u5165\u6c60\u2192\u70e7\u2192finalize\u2192judge \u51bb\u7ed3"
    "\u2192\u6536\u517b\u2192\u5165\u6c60\u2192\u70b9\u706b\u4e00\u7a97\u7ebf**\u2014"
    "\u2014r481 W3 screen 4 \u5206\u7247\u5165\u6c60\uff08n_rows 4909=4814 cand+75 "
    "ctrl+20 null\u00b7r678 \u5916\u79d1\u00b7anti-double \u95e8\uff09\uff1br482 "
    "\u5206\u7247\u70e7\u5f55+\u53cc claim \u63e1\u624b\uff08SHARD-0/2/3 \u4e24\u8f6e"
    "\u6536\u5272\u00b7pool_worker claim-by-file \u6b63\u8def\uff09+screen \u53cc\u70e7"
    "\u00d7finalize id \u53bb\u91cd\u7f3a\u5931\u5751\u5f8b\uff1br483 **W3 screen "
    "finalize complete=true \u6536\u53e3**\uff08785/4814 \u5b58\u6d3b 16.31%\u00b7"
    "\u4e09\u6ce2\u7a33\u6001\u00b7\u8de8\u6ce2\u574d\u7f29 1274>600 \u673a\u5236"
    "\u590d\u6838\u00b7\u8d26\u672c 646,799\u00b7\u516d\u5bf9\u8d26 4/6 \u5e26\u5185+2 "
    "\u51fa\u5e26\u62ab\u9732\uff09+\u8865\u7ffb\u56db\u8fde\u5f8b\uff1br484 **W3 s3 "
    "judge face FROZEN**\uff08\u00a79.1 append commit 2b41a3958 R99\u00b7\u79cd\u5b50 "
    "mass_trial_w3_judge=20285600 R250 \u4e00\u6b65\u5f8b\u00b7runner judge --wave 3 "
    "\u4e09\u5b50\u547d\u4ee4\u6269\u817f selftest 40/40\u00b7\u7981\u5411\u95f8\u590d"
    "\u8dd1\u6293 BAN-04 \u8bcd\u6cd5\u78b0\u649e\u2192\u300c\u683c\u9762\u300d\u7cbe"
    "\u786e\u5316 ADMIT\uff09+judge-prep \u5206\u79bb spawn+\u9501\u6587\u4ef6 "
    "add-then-reset \u5751\u5f8b\uff1br485=\u672c\u6838\u5bf9\u8f6e **prep \u6536\u517b"
    "+judge \u5165\u6c60+\u70b9\u706b\u5168\u94fe**\uff08judge-prep PASS 1028s\u00b7"
    "785\u2192777=|corr|\u22650.999 \u584c\u7f29 8 \u5458 6 \u7c07\u00b7\u6536\u517b "
    "150f36fb4\u2192+4 \u6c60\u6761\u76ee bc73edd97\u3014i%%4 \u8def\u7531 195/194/"
    "194/194\u00b7host_gates t18 \u6df1\u677f\u3015\u2192autofill \u4e24 tick r351 "
    "\u8ba9\u8def\u540e 17:04:44 launched\u00b7claim 9b2dc31eb DELIVERED\u00b7SHARD-0 "
    "burn pid 25540 \u5728\u98de\uff09+\u5e2d\u4f4d\u649e\u8f66\u51c0\u6536\u53e3"
    "\uff08bm-a 16:5x MSG-1655 \u8ba4\u9886\u540c\u7a97\u2192\u5176 r687 \u81ea\u884c"
    "\u8ba9\u8def a6fc0132d=commit \u65f6\u95f4\u5e8f\u00b7\u5176 20287000 \u53cc\u767b"
    "\u8bb0 dropped\u00b7\u672c\u673a\u96f6\u56de\u590d\u9762\uff09+ser() EOL join "
    "\u5751\u5f8b\uff09\u4ea7\u7269\u6e05\u5355\u6f02\u79fb=research/"
    "MASS_TRIAL_W3_PREREG.md \u00a79.1\u3014r484 \u51bb\u7ed3 2b41a3958\u3015+"
    "scripts/mass_trial_w1.py judge wave-3 \u817f+scripts/science_gates.py "
    "SEED_REGISTRY 20285600\u3014r484\u3015+results/mass_trial/w3_judge_state.json"
    "\u3014r485 \u6536\u517b\u00b7777 \u683c\u3015+results/runnable_pool.json +4 "
    "\u6761\u76ee\u3014r485 bc73edd97\u3015+results/mass_trial/w3_screen_summary.json "
    "\u53ca r685 \u6536\u53e3\u4ef6\u3014r483 finalize\u3015+results/_r48{1..5}bmc_* "
    "\u5de5\u4ef6\u65cf\uff08enroll/adopt/probe/s6_chain/log\uff09+docs/daily_report/"
    "REPORT-2026-10-04.*+docs/live_usage/LIVE-2026-10-04.* \u9010\u8f6e\u518d\u751f"
    "\u4ef6+CODELY.md \u5751\u5f8b r482/r483/r484/r485 \u5404 1 \u884c\uff1b\u7edf"
    "\u4e00\u94fe **646,799 \u5b9e\u8bfb**\uff08r484 \u51bb\u7ed3\u7a97 N_eff \u94fe"
    "\u5934\u5b9e\u8bfb\u00b7W3 judge finalize \u843d\u5730\u540e\u524d\u79fb\uff09"
    "\uff1borders 154/155 \u53cc\u626b\u96f6\u672a\u56de\u6267\u5168\u7a97\u7ef4\u6301"
    "\uff1bsmoke 48/48\uff1bD-19 4E5BE321/68947C17 \u53cc MATCH \u96f6\u6d88\u8d39"
    "\uff1b\u6c60\u6001=W3-JUDGE SHARD-0 in-flight\uff08bm-c burner\u00b7SHARD-{1..3} "
    "ready \u65e0\u4e3b\u5f85\u7eed\u70e7\uff09+FUND \u4e09\u65cf NULLS bm-b canonical "
    "\u5728\u98de\uff08finalize \u7a97 10-05 10:30 \u5f00\u00b7\u8ba9\u8def\u7981"
    "\u53cc\u70e7\uff09+board \u7a7a\uff1b\u6307\u9488\uff1a**W3 judge 4/4 \u70e7\u6bd5"
    "\u2192judge-finalize --wave 3\uff08777-cell \u5b8c\u5907+r482 id \u53bb\u91cd "
    "post-merge \u590d\u8dd1+\u6c60\u53cc\u7ffb\u540c\u7a97 r668+\u5b9d\u85cf\u6355"
    "\u83b7\u95ee+\u00a77/\u00a78 \u56de\u586b\u226410-12\uff09\u2192W3 \u5168\u6ce2"
    "\u6536\u7ebf\u2192fund-trio finalize 10-05..09\uff08bm-b\u00b7G-SEG frozen per "
    "O-0808\uff09+O-2115/O-2030 \u9a8c\u6536 10-08+\u5f00\u5e02 10-09 \u6570\u636e"
    "\u9053\u6062\u590d+\u6708\u754c\u9996\u8003 10-31**\uff1b\u4e0b\u4e00 5x=bm-c "
    "r490\u3002")
ho_lines.insert(1, ho_line)
with open(HO, "w", encoding="utf-8", newline="") as fh:
    fh.write(ho_eol.join(ho_lines))
ho2 = open(HO, encoding="utf-8", newline="").read()
assert ho2.count("bm-c round 485 \u4e94\u500d\u6570\u6838\u5bf9") == 1
print("HANDOVER OK (5x line inserted at top)")

# --- 3. state-bm-c.json ---
ST = os.path.join(ROOT, "state-bm-c.json")
st = json.load(open(ST, encoding="utf-8"))
st["round_no"] = 485
st["last_round"] = ("r485 bm-c: W3 judge adoption+enrollment+ignition "
                    "(judge-prep PASS 1028s, 785->777 collapse 6 clusters; state "
                    "adopted 150f36fb4; +4 pool entries bc73edd97 N_judge=777 i%4 "
                    "195/194/194/194; autofill r351 defers x2 then 17:04:44 "
                    "launched, claim 9b2dc31eb DELIVERED, SHARD-0 burn pid 25540 "
                    "in-flight; bm-a seat MSG-1655 -> their r687 self-yield "
                    "a6fc0132d, seed 20287000 dropped unpushed)")
st["last_round_at"] = ts_iso
st["last_round_ts"] = ts_line
st["last_seen"] = ts_iso
st["updated"] = ts_iso
st["updated_at"] = ts_iso
st["heartbeat_epoch_utc"] = epoch
st["clock_read"] = ts_iso
st["current_task"] = (
    "\u5f53\u524d\u6d3b: W3 judge SHARD-0 \u70e7\u5f55\u5728\u98de\uff08pid 25540"
    "\u00b7195 cells\u00b7ckpt %d \u884c\u589e\u957f\u4e2d\u00b7CPU 100%%\uff09"
    "\u00b7SHARD-{1..3} ready \u5f85 autofill \u7eed\u70e7 | \u6700\u8fd1\u5b9e\u7269: "
    "results/mass_trial/w3_judge_state.json \u6536\u517b\uff08777 \u5224\u51b3\u683c"
    "\uff09+runnable_pool +4 \u6761\u76ee MASS-TRIAL-W3-JUDGE-SHARD-0..3\uff08bc73edd97"
    "\uff09+claim 9b2dc31eb DELIVERED @ %s | \u4e0b\u4e2a\u91cc\u7a0b\u7891: 4/4 "
    "\u70e7\u6bd5\u2192judge-finalize --wave 3+\u6c60\u53cc\u7ffb\u540c\u7a97\uff08"
    "r668\uff09\u226410-12\uff1bfund-trio finalize 10-05 10:30\uff08bm-b\uff09\uff1b"
    "\u9a8c\u6536 10-08\uff1b\u5f00\u5e02 10-09"
    % (ckpt_rows, ts_iso))
st["next"] = ("(a) r486: watch SHARD-0 burn -> adopt w3_judge_shard_0of4.jsonl rows "
              "-> done-flip shard+entry per r488/r489 (burner-side duty, autofill "
              "keepalive holds claim); SHARD-{1,2,3} auto-burn via autofill ticks "
              "(195/194/194/194 cells). (b) after 4/4 done: judge-finalize --wave 3 "
              "(777-cell completeness probe + r482 id-dedup probe post-merge re-run "
              "+ single-shot ledger + w3_judge.json + pool dual-flip same window per "
              "r668 + treasure-capture question + sec.7/8 backfill; 48h CEO report "
              "clock starts). (c) fund-trio finalize 10-05 10:30 (bm-b owner, watch "
              "only). (d) O-2115/O-2030 acceptance 10-08. (e) market reopen 10-09.")
st["did"] = ("r485 bm-c W3 judge ignition round: (1) S0 pull blocked by daemon "
             "treadmill -> absorb 150f36fb4 (churn + w3_judge_state.json adoption, "
             "777 cells, prep PASS 1028s) -> merge 5d53b5c9e (bm-b S6 churn 59 "
             "faces zero-intersection zero-UU); (2) MAIN PRODUCT: W3-JUDGE "
             "enrollment +4 shards bc73edd97 (raw-text surgical r678 + anti-double "
             "gate + serial-position gate all-judge-family-done; N_judge=777 i%4 "
             "195/194/194/194; host_gates t18 deep cache present locally; pool "
             "372->376); (3) seat collision CLEAN: bm-a MSG-1655 claim -> their "
             "r687 self-yield a6fc0132d merged (commit-time law, their 20287000 "
             "dual seed dropped unpushed, three judge faces ours-canonical) -> "
             "MSG moved to processed; (4) ignition chain: autofill ticks 17:01:02/"
             "17:03:02 claim_lost_yield (origin-pool-past-HEAD r351 defer, session "
             "reconcile duty) -> churn absorb ad7b27993 + merge 2c5254577 (bm-b "
             "keepalive + bm-a r685/r687) -> tick 17:04:44 launched, daemon claim "
             "commit 9b2dc31eb (r199 launch-claim + r290 self-commit), push_verify "
             "DELIVERED tip 9b2dc31eb, burn pid 25540 judge --wave 3 --shard 0 "
             "alive, ckpt growing; (5) S1 smoke 48/48; S2 boards empty; S3 "
             "satengine rc0 alive (Tools face), watermark green; (6) S0.5 orders "
             "154/155 zero-unacked, D-19 double MATCH, inbox 0; (7) S6 38/38 rc0 "
             "(dualrun streak 51, 376 entries); (8) S7 quartet green + attrition "
             "CLEAN + HANDOVER 5x (r481-485).")
st["verify"] = ("adoption evidence = results/mass_trial/w3_judge_state.json "
                "(batch MASS_TRIAL_W3_JUDGE, n_judge_cells 777 == len(kept), "
                "candidates sha16 d0fc84b31113d572 == sha256(w3_candidates)[:16], "
                "census L/D == frozen) + commit 150f36fb4; enrollment evidence = "
                "results/_r485bmc_w3_judge_enroll.json (reparse + difflib removed==2 "
                "+ anti-double + serial-position) + commit bc73edd97; ignition "
                "evidence = autofill_state.bm-c.json last_tick verdict=launched "
                "pid 25540 + checkpoint rows %d growing + claim commit 9b2dc31eb "
                "push_verify DELIVERED (ahead=0/behind=0); seat yield = merge "
                "a6fc0132d in HEAD ancestry (merge-base --is-ancestor rc0); S6 = "
                "results/_r485bmc_s6_log.txt 38/38 rc0; S7 = attrition CLEAN + "
                "loop pin5 + claws reinstalled; state json.loads self-check + "
                "heartbeat epoch int + clock T-sep POST-WRITE (this script)"
                % ckpt_rows)
with open(ST, "w", encoding="utf-8", newline="") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1)
st2 = json.loads(open(ST, encoding="utf-8").read())
assert st2["round_no"] == 485 and isinstance(st2["heartbeat_epoch_utc"], int)
assert "T" in st2["clock_read"] and "+" in st2["clock_read"]
print("STATE OK (round_no=485, epoch=%d int, clock T-sep)" % epoch)

# --- 4. heartbeat fleet/machines/bm-c.json ---
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
hb["activity_now"] = ("W3 judge SHARD-0 burn in-flight (pid 25540, 195 cells, ckpt "
                      "%d rows growing, CPU 100%); SHARD-{1..3} ready awaiting "
                      "autofill; bm-a seat-yield merged (r687 a6fc0132d); S6 38/38; "
                      "orders zero-unacked; D-19 double MATCH" % ckpt_rows)
hb["current_task"] = st["current_task"]
hb["latest_artifact"] = ("results/mass_trial/w3_judge_state.json (adoption) + "
                         "results/runnable_pool.json +4 MASS-TRIAL-W3-JUDGE-SHARD "
                         "(bc73edd97) + claim 9b2dc31eb (DELIVERED)")
hb["next_milestone"] = ("4/4 judge shards burned -> judge-finalize --wave 3 + pool "
                        "dual-flip same window (r668) <=10-12; fund-trio finalize "
                        "10-05 10:30 (bm-b); acceptance 10-08; market reopen 10-09")
hb["prod_lanes"] = ("W3-JUDGE lane: SHARD-0 in-flight bm-c burner, SHARD-{1..3} "
                    "ready unclaimed (autofill continues); FUND trio NULLS bm-b "
                    "in-flight (watch only); boards empty; no new orders")
hb["verdict"] = st["last_round"]
with open(HB, "w", encoding="utf-8", newline="") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)
hb2 = json.loads(open(HB, encoding="utf-8").read())
assert hb2["round_no"] == 485 and isinstance(hb2["heartbeat_epoch_utc"], int)
assert "T" in hb2["clock_read"]
print("HEARTBEAT OK (epoch=%d int)" % epoch)

# --- 5. CODELY.md pit line ---
CO = os.path.join(ROOT, "CODELY.md")
co_raw = open(CO, encoding="utf-8", newline="").read()
assert co_raw.count("r485 bm-c] \u5165\u6c60\u811a\u672c") == 0
co_eol = "\r\n" if co_raw.endswith("\r\n") else "\n"
co_line = (
    "- [2026-10-04 17:1x r485 bm-c] \u5165\u6c60\u811a\u672c ser() \u884c\u8fde"
    "\u63a5 EOL \u4e0e\u5bbf\u4e3b\u6587\u4ef6\u4e0d\u4e00\u81f4\u5751\uff08r481 "
    "\u8303\u5f0f\u955c\u50cf\u5b9e\u5f39\uff1arunnable_pool.json=CRLF \u5bbf\u4e3b"
    "\u800c ser() \u7684 json.dumps \u884c\u8fde\u63a5\u7528 \\n\u2192\u63d2\u5165"
    "\u5757\u5185\u90e8\u6df7 LF\u9762\uff0cdaemon settle \u4e0b\u8f6e\u5199\u56de"
    "\u65f6\u6574\u5757\u5f52\u4e00 CRLF=\u4e0b\u8f6e churn absorb \u51fa 197 \u884c"
    "\u5168\u5757\u5047 diff\uff08word-diff \u5168 ~ =EOL-only \u5b9a\u8c23\u6cd5"
    "\u00b7\u8bed\u4e49\u96f6\u53d8\u5316\u96f6\u4f24\u5bb3\uff09\uff0c\u4f46\u6536"
    "\u53e3\u7a97\u591a\u4ed8\u4e00\u8f6e\u300c\u771f\u5dee\u5f02\u5b9a\u4f4d\u300d"
    "\u8bca\u65ad\u6210\u672c\u3002How to apply\uff1a\u6c60\u9762/\u5171\u4eab "
    "json \u884c\u7ea7\u624b\u672f\u7684\u884c\u8fde\u63a5\u4e00\u5f8b\u7528\u63a2"
    "\u6d4b\u5230\u7684\u5bbf\u4e3b eol\uff08ser() \u6539 eol+\"  \".join \u5f62\uff09"
    "\uff1b\u6536\u53e3\u7a97\u89c1\u5927\u5757\u5047 diff \u5148\u8dd1 word-diff "
    "\u5b9a\u8c23 EOL-only \u518d\u5b9a\u771f\u5dee\u5f02\uff08r641 \u590d\u73b0"
    "\u8bc1\u4f2a\u5f8b\u65cf\u9762\uff09\u3002")
with open(CO, "a", encoding="utf-8", newline="") as fh:
    fh.write(co_line + co_eol)
co2 = open(CO, encoding="utf-8", newline="").read()
assert co2.count("r485 bm-c] \u5165\u6c60\u811a\u672c") == 1
print("CODELY OK (+1 pit line)")
print("BOOKKEEPING ALL OK")
