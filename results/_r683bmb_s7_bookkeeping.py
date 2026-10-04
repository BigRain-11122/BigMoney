# r683 (bm-b) S7 bookkeeping: round-report append (bytes law r641-3) + state round_no+1 (r645 self-verify)
# + heartbeat update (epoch int law R170/R178/R262, clock T-separator) + inbox archive
import datetime, io, json, os, shutil, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.datetime.now()
TS = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")

# ---- 1) round report line (bytes mode, r641-3 mixed-encoding-history file) ----
RR = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
line = (
    f"{TS} | r683 (bm-b) PRODUCT (dept:\u7814\u7a76+\u6570\u636e\u7ef4\u62a4): "
    "[watermark verdict: GREEN (red=false lane=healthy; satengine alive rc0 queue=22 RAM-floor gate 2.5-3.2GB<4.0GB machine discipline; "
    "dualrun ZERO-DRIFT streak 51; post_review REPORT-20261004 dist x45/cross0/yellow5 zero active red; S6 28/28 rc0)] | "
    "\u5f53\u524d\u6d3b: trio NULLS \u4e09\u65cf\u5728\u70e7(V861/Q674/D512 of 2000)+W3 judge shard-2(bm-a)/shard-3(bm-c) \u4e09\u673a\u63a5\u529b | "
    "\u6700\u8fd1\u5b9e\u7269: results/mass_trial/w3_judge_shard_1of4.jsonl 194/194 \u5224\u51b3\u884c 17:23 \u843d\u76d8 + \u6c60\u53cc\u5c42 done-flip + claim \u56de\u586b (commit bcdbc43e0 DELIVERED, sha16(pool)=00acf6f9ed40892f) | "
    "\u4e0b\u4e2a\u91cc\u7a0b\u7891: W3 judge 4/4 \u6536\u9f50\u540e finalize (\u9884\u8ba1\u4eca\u665a, shard-2/3 \u5728\u98de) \u2192 FUND-VALUE finalize \u5019\u9009\u7a97 10-06T15+ | "
    "\u672c\u8f6e\u4e3b\u4f53: S0 pool_core_samples tail-union \u96f6\u4e22\u5931 (ours+1/theirs+2 multiset containment PASS, merge 26c3926d4 DELIVERED) + "
    "W3-JUDGE-SHARD-1 \u70e7\u5f55\u5b8c\u6210 194/194 (i%4==1, i 1..773, dual_nulls B=2000/P=2000 \u5b8c\u5907, pid 21200 \u6b63\u5e38\u9000\u51fa CSV+CIM \u53cc\u5f62\u9a8c\u8bc1) \u2192 "
    "autofill last_tick relaunch_cooldown \u91cd\u70e7\u73af\u62c6\u9664 (r668 \u5f8b\u5f53\u7a97\u8865\u7ffb, r485 \u914d\u65b9\u4e94\u95e8, treasure_guard rc0) + "
    "S0.5 orders 154/154 \u96f6\u672a\u56de\u6267 + D-19 \u53cc\u952e MATCH (decisions 4e5be321/orders 68947c17, \u96f6\u65b0\u51b3\u7b56\u96f6\u52a8\u4f5c) + "
    "S6 28/28 rc0 (LHB fetch 27.7s rc0 new=0 honest, clock CALL-2026-09-30 ORANGE_COOL, token delta=0) | "
    "\u7b14\u8bef\u62ab\u9732: S0 absorb/merge commit \u8bef\u6807 round 689 (\u5b9e\u9645\u7a97 r683, \u8868\u5c3e r682+1; \u5df2\u63a8\u9001\u4e0d\u6539\u53f2, \u5982\u5b9e\u6ce8\u8bb0) | "
    "\u4e0b\u8f6e\u6307\u9488: W3 finalize \u5019\u7a97 (shard-2/3 \u843d\u5730\u540e id \u96f6\u91cd\u63a2\u9488 r482 \u5f8b+\u53cc\u5c42\u7ffb\u9762 r668 \u5f8b); \u672c\u5730\u672a\u8fbe origin commit \u6570=0"
)
with io.open(RR, "ab") as f:
    f.write(line.encode("utf-8") + b"\n")
with io.open(RR, "rb") as f:
    rb = f.read()
assert rb.count(line.encode("utf-8")) == 1, "round-report marker count != 1 (r679 idempotent gate)"
print("round-report appended, marker==1 PASS")

# ---- 2) state.json round_no+1 (programmatic write + post json.loads self-verify, r645) ----
ST = os.path.join(ROOT, "state.json")
st = json.load(open(ST, encoding="utf-8"))
old = st.get("round_no")
st["round_no"] = 683
st["round_no_label"] = "round 683 (bm-b)"
st["next"] = None
with io.open(ST, "w", encoding="utf-8") as f:
    json.dump(st, f, ensure_ascii=True, indent=1)
back = json.loads(io.open(ST, encoding="utf-8").read())
assert back["round_no"] == 683, "state round_no self-verify fail"
print("state round_no %s -> 683, self-verify PASS" % old)

# ---- 3) heartbeat fleet/machines/bm-b.json (epoch int, clock T-form, r682 heartbeat fields) ----
HB = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
hb = json.load(io.open(HB, encoding="utf-8"))
hb["last_seen"] = TS
hb["heartbeat_epoch_utc"] = int(time.time())
hb["clock_read"] = TS
hb["round_no"] = 683
hb["round_no_label"] = "round 683 (bm-b)"
hb["current_task"] = (
    "r683 closed: W3 judge SHARD-1 194/194 burned + two-layer done-flip same-window "
    "(claim backfilled, autofill relaunch_cooldown loop defused, DELIVERED bcdbc43e0); "
    "S0 pool_core_samples tail-union zero-loss; S6 28/28 rc0 (dualrun streak 51, clock ORANGE_COOL); "
    "trio NULLS V861/Q674/D512 of 2000 burning healthy (ETA V 10-06T15/Q 10-07T09/D 10-08T03); "
    "next grain = W3 judge finalize when shard-2/3 land tonight, then FUND-VALUE finalize window 10-06T15+"
)
hb["verdict"] = "healthy burning"
hb["ts"] = TS
hb["updated"] = TS
hb["updated_at"] = TS
with io.open(HB, "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
back_hb = json.loads(io.open(HB, encoding="utf-8").read())
assert isinstance(back_hb["heartbeat_epoch_utc"], int), "epoch not int (R170/R178 law)"
assert "T" in back_hb["clock_read"] and "+" in back_hb["clock_read"], "clock form (R262 law)"
print("heartbeat updated, epoch=%d clock=%s self-verify PASS"
      % (back_hb["heartbeat_epoch_utc"], back_hb["clock_read"]))

# ---- 4) inbox archive: MSG-2026-10-04-1712 (bm-a yield notice, no-receipt-required per its own header) ----
SRC = os.path.join(ROOT, "fleet", "inbox", "MSG-2026-10-04-1712-bma-ALL-w3-judge-yield.md")
DST_DIR = os.path.join(ROOT, "fleet", "inbox", "processed")
os.makedirs(DST_DIR, exist_ok=True)
if os.path.exists(SRC):
    shutil.move(SRC, os.path.join(DST_DIR, "MSG-2026-10-04-1712-bma-ALL-w3-judge-yield.md"))
    print("inbox MSG-1712 archived to processed/")
else:
    print("inbox MSG-1712 already gone")
print("BOOKKEEPING_OK")
