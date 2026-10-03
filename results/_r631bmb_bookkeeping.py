# -*- coding: utf-8 -*-
# r631 bm-b bookkeeping: state.json + round report line + heartbeat + post-write verify
import json, time, datetime, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

now = datetime.datetime.now().astimezone()
ts = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())
os_ram_gb = 3.81  # sampled 20:0x via Win32_OperatingSystem
gpu_free_mib = 2283

# --- state.json ---
s = json.load(open("state.json", encoding="utf-8"))
s["round_no"] = 631
s["round_no_label"] = "round 631 (bm-b)"
s["note"] = ("r631: S0 dead-session legacy adoption + full origin integration: r630 closeout bookkeeping "
             "(report/state/heartbeat/CODELY/HANDOVER/MSG-2005/S6 tools) + daemon churn absorbed into adoption commit -> "
             "rebase onto origin/main (bm-a r638 4 commits) -> 19 UU derive/status faces resolved clean-side origin "
             "(pool entries 366/366 semantically identical, zero face divergence) -> marker full-scan NONE -> push 2c6bcf783 "
             "main==origin delivery-proven; S0.5 orders 151/151 zero-unacked + D-19 MATCH 4167b784 via lane-side temp "
             "sparse-clone recipe (K: group tree invisible to S4U lane sessions); smoke 47/47; engine alive rc0 idle; "
             "S6 34 legs 33 rc0 + update_lhb rc2 transient source fail (rerun=30min-throttle no-op self-heal, retry next round); "
             "S7 registers/claws/attrition CLEAN (pin=2 no-op); NULLS trio V355/D133/Q242 of 2000 in flight "
             "(RAM 3.81GB<4GB no new claims; W2-JUDGE-SHARD-2/3 ready face stays unclaimed per shared-machine bar)")
for k in ("last_round_at", "last_round_ts", "ts", "updated", "updated_at", "last_seen"):
    s[k] = ts
s["last_decisions_sha"] = "4167b7841a5b2b889fa8f8d27b81286faae39b340e786609998431ee6fd46d26"
s["last_decisions_at"] = ts
json.dump(s, open("state.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# --- round report line ---
line = ("2026-10-03T20:1x+08:00 | R631 bm-b (dept:\u5de5\u7a0b:S0 \u96c6\u6210\u6536\u53e3+S6 \u7ef4\u62a4\u94fe) | "
        "watermark verdict: GREEN (red=false; WM py_low_with_work_cands \u70b9\u540d: \u539f\u56e0=RAM 3.81GB<4GB "
        "\u5171\u4eab\u673a\u53cc\u516c\u53f8\u95f8+NULLS \u4e09\u70e7\u5173\u952e\u8def\u5f84\u5360\u7528, \u6c60 ready \u9762 W2-JUDGE-SHARD-2/3 "
        "\u4e0d\u8ba4\u9886, \u6574\u6539=RAM\u22654GB \u7a97\u6062\u590d\u8ba4\u9886; dualrun ZERO-DRIFT streak 21; smoke 47/47) | "
        "\u5f53\u524d\u6d3b: FUND \u4e09\u65cf NULLS \u70e7\u5f55\u5728\u98de V355/D133/Q242 of 2000 (\u7ef4\u6301 ~10-15/h/\u65cf, "
        "ETA V 10-05/06\u00b7D 10-08/09) | \u6700\u8fd1\u5b9e\u7269: r630 \u6b7b\u4f1a\u8bdd\u9057\u4ea7\u6536\u517b+origin \u5168\u91cf\u96c6\u6210\u843d\u5730 "
        "commit 2c6bcf783 main==origin (19 UU \u9762\u5168\u4e3a\u786e\u5b9a\u6027 derive/status \u9762\u6309 clean-side \u53d6 origin \u4fa7, "
        "\u6c60\u9762 entries 366/366 \u8bed\u4e49\u5168\u540c\u96f6\u5206\u6b67; marker \u5168\u4ed3\u626b NONE) + S6 34 \u817f "
        "(LIVE-2026-10-03/REPORT-2026-10-03/dashboard/scorecard \u518d\u751f + t35_paper_export/daily_scorecard/"
        "dashboard \u4e09\u9762 stale-takeover STALE_MIN 22min \u5408\u6cd5\u4ee3\u7b14) @20:1x | "
        "\u4e0b\u4e2a\u91cc\u7a0b\u7891: 10-06 finalize \u7a97\u524d\u7f6e\u96f6\u963b\u585e\u7ef4\u6301 (NULLS \u9996\u65cf\u8fbe 2000 \u540e finalize+\u5224\u51b3\u94fe, "
        "V ETA 10-05/06, \u7a97\u5185<=48h) | did: S0 \u8f6e\u9996\u6b7b\u6811\u6536\u517b (r630 \u7c3f\u8bb0\u9057\u4ea7+churn absorb \u63d0\u4ea4 -> "
        "rebase origin 4 commit -> 19 UU clean-side -> marker \u626b NONE -> push \u9001\u8fbe 2c6bcf783); S0.5 \u4ee4\u724c 151/151 "
        "\u53cc\u626b\u96f6\u672a\u56de\u6267 + D-19 \u6c34\u4f4d MATCH 4167b784 \u96f6\u52a8\u4f5c (\u8f66\u9053\u9762\u65e0 K: \u96c6\u56e2\u6811=\u4e34\u65f6 sparse clone "
        "\u76f4\u8bfb origin blob \u914d\u65b9, \u5751\u5f8b\u5165 CODELY); S1 smoke 47/47; S3 \u5f15\u64ce\u6d3b rc0 idle; S6 34 \u817f 1 \u975e0="
        "update_lhb rc2 \u77ac\u6001\u6e90\u5931\u8d25 (3/11 \u4e2d\u65ad -> \u91cd\u8dd1 30min \u8282\u6d41 no-op \u81ea\u6108, \u4e0b\u8f6e\u94fe\u81ea\u52a8\u91cd\u8bd5, "
        "\u5982\u5b9e\u4e0a\u62a5\u52ff\u63a9\u76d6); S7 \u6ce8\u518c\u5668\u5168\u7eff (pin=2 no-op/watchdog/\u53cc\u722a LF \u5f52\u4e00\u81f4) + attrition CLEAN | "
        "\u9a8c\u8bc1: smoke 47/47; S6 33/34 rc0 + 1 rc2 \u62ab\u9732; \u9001\u8fbe\u81ea\u8bc1 main==origin==2c6bcf783 \u672a\u8fbe=0 | "
        "\u672c\u5730\u672a\u8fbe origin commit \u6570=0 | \u4e0b\u8f6e\u6307\u9488: NULLS \u4e09\u65cf\u76d1\u89c6 (RAM\u22654GB \u7a97\u6062\u590d "
        "W2-JUDGE-SHARD-2/3 \u8ba4\u9886); update_lhb \u8282\u6d41\u7a97\u540e\u91cd\u8bd5; 10-06 finalize \u524d\u7f6e\u9884\u6f14\u91cd\u8dd1\u786e\u8ba4\u5168\u7eff\u7ef4\u6301\n")
with open("logs/iteration-loop/round_reports.md", "a", encoding="utf-8") as f:
    f.write(line)

# --- heartbeat bm-b ---
h = json.load(open("fleet/machines/bm-b.json", encoding="utf-8"))
h["last_seen"] = ts
h["heartbeat_epoch_utc"] = epoch
h["clock_read"] = ts
h["round_no"] = 631
h["round_no_label"] = "round 631 (bm-b)"
h["current_task"] = "FUND trio NULLS burn watch (V355/D133/Q242 of 2000) + 10-06 finalize pre-window zero-blocker watch"
h["verdict"] = ("GREEN (r630 legacy adopted + origin integrated 2c6bcf783 delivery-proven; burns healthy; smoke 47/47; "
                "S6 33/34 rc0 + lhb rc2 transient disclosed; py_low_with_work_cands: RAM 3.81GB<4GB bar holds new claims)")
h["ts"] = ts
h["updated"] = ts
h["updated_at"] = ts
h["cpu_cores"] = 16
h["idle_ram_gb"] = os_ram_gb
h["gpu_free_vram_mib"] = gpu_free_mib
json.dump(h, open("fleet/machines/bm-b.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# --- post-write self-verify (R170/R178: epoch must be int) ---
sv = json.load(open("fleet/machines/bm-b.json", encoding="utf-8"))
assert isinstance(sv["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in sv["clock_read"], "clock_read must be T-separated"
st = json.load(open("state.json", encoding="utf-8"))
assert st["round_no"] == 631
print("bookkeeping OK: state round_no=631; heartbeat epoch=%d int; clock=%s" % (sv["heartbeat_epoch_utc"], sv["clock_read"]))
