# r403 bm-b round ledger faces: report line + state + heartbeat (bytes-safe UTF-8)
import json, time, io

now = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())

report_line = (
    now + " | r403 bm-b | dept:\u5de5\u7a0b/\u8230\u961f "
    "(\u6b7b\u4f1a\u8bdd 01:42 \u810f\u6c34\u6536\u53e3+\u6740\u96f6\u8fdb\u5c55\u50f5\u5c38\u94fe+PEP701 "
    "\u4fee\u590d\u9a8c\u8bc1+T-115 \u4e8c\u673a\u9a8c\u8bc1+\u70ed\u51b7\u6574\u7f16) | "
    "WM-VERDICT: \u7eff\u724c red=false lane=healthy @02:20 "
    "probe=py_low_with_work_cands \u5408\u6cd5\uff08\u677f\u5168\u95ed\u73af+\u672c\u673a astock refresh "
    "\u5728\u98de\uff085222\u80a1 2.5s \u9650\u901f\u7f51\u7edc\u578b\u4f4e py CPU \u975e idle\uff09 | "
    "did: (1) S0-1 bm-b \u951a\u5b9a; S0 pull --rebase FF b424baf4e; \u8f6e\u9996\u810f=01:42 \u6b7b\u4f1a\u8bdd"
    "\uff0825min \u9884\u7b97\u6740\u624b 02:07:01 \u8bc1\u636e=run_20260929_014201.log+round_*.out "
    "\u5c3e\uff09stranded \u4ea7\u7269\u2192\u8fdb\u7a0b\u9762\u63a2\u8bc1\u672c\u4f1a\u8bdd\u552f\u4e00 Bigmoney "
    "\u4f1a\u8bdd\u2192\u6309 r398 \u5148\u4f8b\u810f\u6c34\u6536\u53e3\u672c\u7a97\u6267\u884c; "
    "(2) \u6740\u96f6\u8fdb\u5c55\u50f5\u5c38=r401 \u6b8b\u7559\u94fe runner pid19188\uff0876min "
    "TotalCPU=78ms\u3001delta=0=stdout \u6b7b\u7ba1\u9053\u6302\u6b7b\u96f6\u4ea7\u7269\uff0c01:59-02:00 "
    "S6 \u9762\u5199\u5165\u5f52\u56e0\u52d8\u8bef=\u6b7b\u4f1a\u8bdd Batch A\uff09; astock refresh "
    "pid7644 \u91c7\u8bc1\u6d3b\u8dc3\u7559\u8dd1 ETA~04:30; (3) S0.5 \u9996\u626b: orders 122/122 "
    "\u96f6\u5dee\u96c6+decisions.md \u7f3a\u4f4d=P-32 \u8bda\u5b9e no-op; (4) S1 smoke 26/26; "
    "(5) S2 \u53cc\u677f: job_list \u7a7a+\u7968\u677f\u65e0 open\uff08T-115 done bm-a r407 \u843d\u5730"
    "\u7555\u8ba4\uff09; WM next_pick=claimed \u5408\u6cd5 parked; (6) \u4e3b\u69fd=\u6b7b\u4f1a\u8bdd"
    "\u9057\u4ea7\u4e09\u9762\u6536\u53e3: \u2460ceo_live_usage.py PEP-701 3.11 \u8bed\u6cd5\u6b7b"
    "\uff08HEAD ast.parse \u5b9e\u8bc1 f-string unmatched\uff09\u2192\u6b7b\u4f1a\u8bdd 3.11-safe "
    "\u4fee\u590d\u672c\u4f1a\u8bdd\u590d\u9a8c=py_compile OK+run rc=0 LIVE-2026-09-29 \u518d\u751f"
    "\uff08ORANGE cap50% 6\u5458 4\u94fe\u884c\uff09+\u8f93\u51fa\u5b57\u8282\u7b49\u4ef7\u5b9e\u8bc1"
    "\uff08git diff=\u4ec5 generated \u6233\uff09\u2461T-115 \u4e8c\u673a\u9a8c\u8bc1\u590d\u8dd1"
    "=pool_worker selftest 25/25 PASS+--dry rc=0\uff08nothing claimable \u6c60\u8bda\u5b9e\uff09"
    "\u2462V3-TOUR flip \u95e8\u590d\u67e5=runner \u4ecd\u672a\u5efa\uff08bm-c \u4ea4\u4ed8 pending "
    "\u5fc3\u8df3 01:22\uff09\u5408\u6cd5 waiting \u96f6\u52a8\u4f5c; (7) S6 \u8f7b\u9762 12 \u817f"
    "\u5168 rc=0\uff08audit FLAG:supply_gap/supply_floor standing ready1<3 streak579.5min \u4f9b\u7ed9"
    "\u54cd\u5e94\u5728\u98de=W5 generate bm-a autofill 01:40/01:50 \u53cc\u53d1+V3 bm-c runner "
    "pending|wm probe \u5408\u6cd5|update_daily 0 \u65b0\u884c cutoff 09-28|regime|clock "
    "CALL-2026-09-28 ORANGE_COOL activated0|rev_osc honest no-op \u9762\u677f incomplete "
    "cutoff09-24 \u7b49 astock|minute_feed pre-09:15 no-op|token delta=0|\u5176\u4f59\u9762"
    "=bm-a r407 36\u817f 01:20+\u6b7b\u4f1a\u8bdd Batch A 01:59 \u53cc\u8986\u76d6\u4e0d\u91cd\u590d"
    "\uff09; (8) S4 \u5751\u5f8b\u4e03\u5341\u56db\u6279\uff08CPU-delta \u63a2\u9488\u5f52\u56e0\u5f8b"
    "\uff09+\u70ed\u51b7\u6574\u7f16\uff08CODELY 9987B\u21926284B\u226410KB \u884c\u7ea7\u96f6\u4e22\u5931"
    "\u6821\u9a8c PASS 4\u6279 verbatim\u2192archive r403 \u7a97\u6279\u8282\uff09 | "
    "evidence: round_20260929_014201.out \u6b7b\u4f1a\u8bdd\u8f68\u8ff9+pool_worker selftest "
    "25/25+smoke 26/26+LIVE-2026-09-29 \u518d\u751f+RECONSOLIDATION GATE PASS | "
    "next: (a) astock refresh ETA~04:30 \u2192rev_osc \u9762\u677f cutoff \u63a8\u8fdb=SIG/BARS "
    "\u5bfc\u51fa\u89e3\u9501 (b) W5 generate bm-a \u5728\u98de watch\u2192W5-JUDGE \u6392\u961f\u9996\u4f4d "
    "(c) V3-TOUR runner bm-c \u4ea4\u4ed8 watch\u2192flip \u95e8\u4e8c\u6761+RAM \u4e09\u91c7\u6837 "
    "(d) CEO 48h \u5343\u4eba\u8bd5\u7528\u671f\u62a5\u544a\u7a97 09-29 22:45 (e) \u4e0b\u8f6e S0.5 "
    "\u53cc\u626b\u6536\u5c3e | marks/\u8d26\u672c/SEED \u672c\u8f6e +0"
)

p = "logs/iteration-loop/round_reports.md"
with io.open(p, "a", encoding="utf-8", newline="\n") as f:
    if not io.open(p, encoding="utf-8", newline="").read().endswith("\n"):
        f.write("\n")
    f.write(report_line + "\n")

s = json.load(io.open("state.json", encoding="utf-8"))
s["round_no"] = 403
s["note"] = ("r403: dead-01:42-session dehydration closeout (PEP-701 ceo_live_usage fix verified "
             "byte-equivalent + T-115 second-machine verify 25/25 + Batch-A S6 salvage) + zero-progress "
             "zombie chain killed (CPU-delta law batch-74) + CODELY hot-cold reconsolidation "
             "9987B->6284B; astock refresh in flight ETA~04:30; V3-TOUR runner still pending bm-c")
s["last_round_at"] = now
s["last_round_ts"] = now
json.dump(s, io.open("state.json", "w", encoding="utf-8", newline="\n"),
          ensure_ascii=False, indent=1)

h = json.load(io.open("fleet/machines/bm-b.json", encoding="utf-8"))
h["last_seen"] = now
h["heartbeat_epoch_utc"] = epoch
h["clock_read"] = now
h["round_no"] = 403
h["round"] = 403
h["loop_round"] = 403
h["current_task"] = ("r403 done: dead-01:42-session dehydration (PEP-701 fix verify + T-115 "
                     "second-machine verify + S6 Batch A salvage) + zombie chain killed + CODELY "
                     "reconsolidation 6284B; next: astock refresh ETA~04:30 -> rev_osc unlock; "
                     "W5 generate watch; V3-TOUR runner wait (bm-c); CEO 48h report 09-29 22:45")
h["verdict"] = ("healthy: smoke 26/26; WM green red=false py_low_with_work_cands lawful "
                "(astock refresh in-flight + board fully closed); audit supply_floor standing "
                "with in-flight supply response (W5 bm-a + V3 runner bm-c); orders ack 122/122")
json.dump(h, io.open("fleet/machines/bm-b.json", "w", encoding="utf-8", newline="\n"),
          ensure_ascii=False, indent=1)

# post-write self-verify: epoch must be JSON int (R170/R178 law), clock T-separated (R262)
h2 = json.load(io.open("fleet/machines/bm-b.json", encoding="utf-8"))
assert isinstance(h2["heartbeat_epoch_utc"], int), "epoch not int = smoke F7 red"
assert "T" in h2["clock_read"] and " " not in h2["clock_read"], "clock not T-separated"
print("ledger faces written; epoch:", h2["heartbeat_epoch_utc"], "clock:", h2["clock_read"])
