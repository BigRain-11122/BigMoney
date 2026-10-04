import json, os, time
from datetime import datetime

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
now = time.time()
epoch = int(now)
clock = datetime.now().astimezone().isoformat(timespec="seconds")

# --- 1. round report append (bytes mode, mixed-encoding history file, r641 law) ---
rr = os.path.join(R, "logs", "iteration-loop", "round_reports.md")
line = (
    "%s | round 657 (bm-b) | dept:\u5de5\u7a0b/\u8235\u961f \u5168\u7eff\u503c\u5b88\u8f6e: S0 origin==HEAD \u6811\u810f7\u4ef6\u5747\u672c\u673adaemon\u6d3b\u70e7\u9762(r656 tip 2ad690d2f, \u96f6behind); S0.5 \u4ee4\u5dee\u96c6\u96f6\u65b0\u4ee4(O-0808\u5df2ack); D-19 \u53ccMATCH\u96f6\u6d88\u8d39(decisions/orders sha \u6052\u7b49, sparse clone \u76f4\u8bfb origin blob \u914d\u65b9\u56e0K:/\u672c\u673a\u5b9e\u5f84C:\\Fluxgroup\\FluxGroup\u65e0.git\u4e0d\u53ef\u7528, r631\u5f8b); S1 smoke 48/48; S2 \u677f\u5168\u95ed\u73af\u96f6open\u7968; S3 \u95e8\u5e8f\u5168\u7eff(WM red=false\u3001\u5f15\u64cealive rc0 idle\u3001trio\u5728\u98de\u2192\u5e38\u8bbe\u7ebf\u4e0d\u89e6\u53d1\u65b0\u6279); S6 34 legs rc0 fail=0(dualrun streak49\u3001\u9884\u671fbar\u65e5=09-30\u56fd\u5e86\u4f11\u5e02\u65e0\u65b0bar\u2192live.paper\u65cf\u6761\u4ef6\u817f\u4e0d\u89e6\u53d1\u3001CALL-2026-09-30 ORANGE_COOL\u3001LIVE-20261004+REPORT-20261004\u5237\u65b0); trio liveness V650/D355/Q495(+5/+5/+6)pids\u5168\u6d3b; S7 \u56db\u4ef6\u5957\u81ea\u6108\u5168no-op/installed\u3001attrition CLEAN\u3001pin=2 | \u8bc1\u636e=S6\u94fe34rc0+trio\u63a2\u9488pids alive+attrition\u626b\u63cfCLEAN\u884c | \u4e0b\u8f6e\u6307\u9488: trio\u70e7\u6279finalize\u7a9710-05..10-09 mechanical_ready\u5373\u6536\u53e3\u5224\u51b3; \u672c\u5730\u672a\u8fbeorigin commit\u6570=0(commit\u540epush_verify\u81ea\u8bc1\u884c\u89c1\u4e0b) | token: L2\u672c\u57302\u817f\u4eca\u65e5(~5892 tok)\u96f6\u4e91\u7aef\n" % clock
)
with open(rr, "ab") as f:
    f.write(line.encode("utf-8"))
print("round_report appended")

# --- 2. state.json update (programmatic write + self-verify, r645 law) ---
sp = os.path.join(R, "state.json")
st = json.loads(open(sp, "rb").read().decode("utf-8"))
st["round_no"] = 657
st["round_no_label"] = "round 657 (bm-b)"
st["note"] = ("r657: all-green watch round -- origin==HEAD zero behind (dirty 7 faces all local daemon burn faces); "
              "orders delta zero (O-0808 acked); D-19 double MATCH zero-consume via sparse-clone origin-blob read "
              "(K: and C:\\Fluxgroup\\FluxGroup\\FluxGroup real-path unavailable per r631, C:\\Fluxgroup\\FluxGroup has no .git); "
              "S1 48/48; S2 zero open tickets; S3 gates green, WM red=false, engine alive rc0 idle, trio in flight -> no new trial batch; "
              "S6 34 legs rc0 fail=0 (dualrun streak 49; expected bar date 2026-09-30 holiday-closed, no new bar -> live.paper conditional legs not triggered; "
              "CALL-2026-09-30 ORANGE_COOL; LIVE-2026-10-04 + REPORT-2026-10-04 refreshed); trio liveness V650/D355/Q495 (+5/+5/+6 since r656) pids alive; "
              "S7 pins/watchdog/claws self-healed, attrition CLEAN")
st["last_round_at"] = clock
st["ts"] = clock
st["updated"] = clock
st["last_seen"] = clock
st["clock_read"] = clock
st["last_decisions_read_at"] = clock
with open(sp, "w", encoding="utf-8") as f:
    json.dump(st, f, indent=1, ensure_ascii=False)
print("state written")

# --- 3. heartbeat update (programmatic + int-epoch self-verify) ---
hp = os.path.join(R, "fleet", "machines", "bm-b.json")
hb = json.loads(open(hp, "rb").read().decode("utf-8"))
hb["last_seen"] = clock
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = clock
hb["round_no"] = 657
hb["round_no_label"] = "round 657 (bm-b)"
hb["current_task"] = ("FUND trio NULLS burn watch (V650/D355/Q495 of 2000 advancing, pids 34396/57116/30208 alive; finalize window 10-05..10-09, fires on mechanical_ready) "
                      "+ r657: all-green watch round, S6 34 legs rc0, zero new orders, D-19 double MATCH")
hb["verdict"] = ("GREEN (smoke 48/48; orders delta zero; D-19 double MATCH zero-consume; WM red=false; engine alive rc0 idle; "
                 "S6 34 legs rc0 fail=0 dualrun streak 49; trio V650/D355/Q495 advancing pids alive; attrition CLEAN; claws/pins no-op; zero cloud token)")
hb["ts"] = clock
hb["updated"] = clock
try:
    import psutil
    hb["cpu_util_pct"] = round(psutil.cpu_percent(interval=1), 1)
    vm = psutil.virtual_memory()
    hb["free_ram_gb"] = round(vm.available / (1024 ** 3), 2)
    hb["idle_ram_gb"] = hb["free_ram_gb"]
    hb["ram_avail_gb"] = hb["free_ram_gb"]
    print("psutil sampled cpu=%.1f ram=%.2f" % (hb["cpu_util_pct"], hb["free_ram_gb"]))
except Exception as e:
    print("psutil unavailable, kept old resource fields:", e)
with open(hp, "w", encoding="utf-8") as f:
    json.dump(hb, f, indent=1, ensure_ascii=False)
print("heartbeat written")

# --- 4. self-verify (json.loads + int epoch + T-separated clock, R170/R178/R262 laws) ---
for p, key in [(sp, None), (hp, "heartbeat_epoch_utc")]:
    d = json.loads(open(p, "rb").read().decode("utf-8"))
    if key:
        assert isinstance(d[key], int), "epoch not int"
    assert "T" in d["clock_read"] and " " not in d["clock_read"], "clock not T-separated"
print("SELF-VERIFY PASS: both files parse, epoch int, clock T-separated")
