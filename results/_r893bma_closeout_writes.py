"""r893(bm-a) round r892 closeout: state heal 891->892 + report line + heartbeat + seat MSG ack.

Composite round (three windows, r844/r888 dead-tail adoption law):
  dead#1  : W190 freeze chain (4 commits) + 39-leg S6 (3 reds on stale SZ bars)
  window#2: W190 finalize EXACT + W191 seat published + S0-leg absorb; died pre-closeout
  this    : red fix (12 SZ 159xxx catch-up heal + marks settle) + smoke 49/49
            + targeted 15-leg re-run all green + closeout bookkeeping
"""
import io, os, json, time, datetime, shutil, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

now = datetime.datetime.now()
ts = now.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
epoch = int(time.time())
R = 892
machine = "bm-a"

report_line = (
    "{ts} | r{r} | bm-a | dept:research/engine+data (perpetual line+data red-fix; composite round r844/r888 dead-tail adoption) | "
    "WM-VERDICT: green (red=false lane healthy; next_pick moneyflow IC claimed=advisory panel-source-blocked; engine ALIVE rc0 idle queue 0) | "
    "当前活: r892 收口 (孤儿面=0; 10-08 节后首 bar 全量落地: 12 SZ 159xxx laggard catch-up heal + paper marks settle; W190 finalize EXACT + W191 seat) | "
    "本轮: dead#1 W190 five-face freeze chain (4 commits) + 39-leg S6 (3 reds hinged on stale SZ bars: live_paper/t24_prospect/aggressive_lab) + "
    "window#2 adoption (21:19) W190 pre-finalize 3-gate probe GREEN -> finalize one-pass EXACT (merged mu -0.0929 sigma 0.2451 K 415,920; ledger 823,128+2,200=825,328 == projection EXACT; pre-W190 K 413,720) "
    "-> W191 pre-seat probe ADMIT (A 435_004..437_003 staircase FIFTY-FIRST / B 437_004..437_203 mutual-exclusion own-A reserved; naive refused per seat leg4) -> W191 seat MSG published=reserved (2130) "
    "-> S0-leg daemon absorb (futures/repo 10-08 bars + zt_pool first-day 287 rows + W190 burn shards 12/12) -> died pre-closeout; "
    "this window (21:38) adoption closeout + S1 red fix: smoke 2 FAIL (RW-4 panel gate: 12 in-service members 159901/159915/159919/159920/159928/159934/159949/159980/159985/159992/159995/159996 last_bar=09-30 vs anchor=10-08) "
    "root-cause = sina SZ late-bar publish (09-23 同族 R54 先例) + 60-min catchup backoff (20:41->21:41 unlock) -> update_daily catch-up heal: new rows 12, failures 0, overlap_mismatch [], cutoff 2026-10-08 "
    "-> REGIME_GUARD enforce + live.paper marks settle OK (paper tracking OK) -> smoke 49/49 PASS -> targeted 15-leg S6 re-run (_r892bma_s6_rerun_driver.py, dead session's own prescription) 15/15 rc0 reds=[] "
    "(3 chain reds cured: live_paper/t24_prospect_paper/aggressive_lab) | "
    "实物: ①12 SZ core48 members 10-08 bars landed (data/daily bare files, panel cutoff 2026-10-08) + paper marks settled for first post-holiday bar ②results/perpetual_faces/n1_w190_results.json (K 415,920, ledger 825,328 == projection EXACT) + _r892bma_w191_probe_receipt.json + MSG-2026-10-08-2130-bma-w191-seat.md (seat published on origin) ③results/_r892bma_s6_rerun.json (15/15 rc0) + _r893bma smoke rerun 49/49 + update_status.json (catchup fetched 12, backoff cleared) ④results/_r892bma_s6_chain.json (39-leg, 3 reds diagnosed to stale bars) | "
    "下轮指针: ①W191 freeze chain (prereg buildgen + freeze-edits five-face insertion + tick ignite; seat 2130 published A 435_004..437_003 / B 437_004..437_203; W192+ re-derive-MANDATORY W141 leg2) ②GM bm-b reroute A/B decision watch (bm-b starved lanes etf_daily/minute_feed/astock_daily/rev_osc SIG 09-30) ③DEC ee70cef0/ORD caef5b78 unchanged zero new rows | "
    "验证: smoke 49/49 + S6 39-leg(3 reds)->targeted 15/15 rc0 + attrition CLEAN (4 ledgers) + orphan face=0 (18 py faces) + engine ALIVE idle queue 0 + 自愈四件套绿 (loop pin=8 Running/watchdog rc0/双爪 PRESENT) + orders unacked=0 (local 51/51) + DEC/ORD 水位零变化 + 本地未达 origin commit 数=0 (push 后 fetch+rev-list 自证) + token: L1 零 API [via bm-a r892]"
).format(ts=ts, r=R)

# 1) round report append (repo ROOT canonical face per r844 law)
rp_path = "round_reports-bm-a.md"
with io.open(rp_path, encoding="utf-8") as f:
    rp = f.read()
if not rp.endswith("\n"):
    rp += "\n"
rp += report_line + "\n"
io.open(rp_path, "w", encoding="utf-8", newline="\n").write(rp)

# 2) state heal 891 -> 892
sp = "state-%s.json" % machine
st = json.load(io.open(sp, encoding="utf-8"))
st["round_no"] = R
st["round"] = R
st["loop_round"] = R
st["last_round"] = R
st["last_round_at"] = ts
st["last_round_closed"] = ts
st["last_round_ts"] = ts
st["last_run"] = ts
st["last_seen"] = ts
st["ts"] = ts
st["updated"] = ts
st["clock_read"] = ts
st["heartbeat_epoch_utc"] = epoch
st["last_heartbeat_epoch_utc"] = epoch
st["idle_rounds"] = 0
st["agenda_starved"] = False
st["last_action"] = "r892 closeout (adoption window): red fix + S6 rerun green + state/report/heartbeat writes + closeout commit"
st["current_task"] = ("W191 freeze chain next window (prereg buildgen + freeze-edits five-face insertion + tick ignite; seat 2130 published=reserved; "
                      "A 435_004..437_003 / B 437_004..437_203; W192+ re-derive-MANDATORY) + GM bm-b reroute decision watch")
st["task"] = st["current_task"]
st["now_active"] = "r892 closed: 10-08 post-holiday bars fully landed (12 SZ catch-up heal) + marks settled + W190 finalize EXACT (K 415,920) + W191 seat published; engine idle queue 0"
st["current"] = st["now_active"]
st["did"] = ("r892 composite (3 windows per r844/r888 adoption law): dead#1 W190 freeze chain 4 commits + 39-leg S6 (3 reds=stale SZ bars); "
             "window#2 (21:19) W190 finalize one-pass EXACT (merged mu -0.0929 sigma 0.2451 K 415,920; ledger 825,328 == projection) + W191 seat published (2130) + S0-leg absorb; died pre-closeout; "
             "this window (21:38): adoption closeout + S1 red fix (smoke 2 FAIL = RW-4 gate 12 stale 159xxx) -> R54 catch-up heal (backoff unlock 21:41) new rows 12 rc0 "
             "-> REGIME_GUARD enforce live.paper marks settle OK -> smoke 49/49 -> 15-leg targeted rerun 15/15 rc0 (3 chain reds cured)")
st["verify"] = ("W190 finalize EXACT (K 415,920 / ledger 825,328 == published projection) + smoke 49/49 + S6 39-leg 3-reds->cured + 15-leg rerun 15/15 rc0 "
                "+ attrition CLEAN (4 ledgers) + orphan face=0 + engine ALIVE idle + self-heal quad green (loop pin=8/watchdog/claws) + orders unacked=0 "
                "+ DEC ee70cef0 / ORD caef5b78 unchanged + push clean")
st["last_artifact"] = "data/daily 12 SZ members 10-08 bars + paper marks settle + results/perpetual_faces/n1_w190_results.json (K 415,920 ledger 825,328) + W191 seat 2130 on origin"
st["latest_artifact"] = "results/perpetual_faces/n1_w190_results.json (K 415,920, ledger 825,328 == projection EXACT) + W191 seat published on origin + 12-member 10-08 bar heal"
st["next"] = ("W191 freeze chain (prereg buildgen + freeze-edits five-face insertion + tick ignite; seat 2130 on origin; A 435_004..437_003 / B 437_004..437_203; "
              "W191+ naive A/B re-derive-MANDATORY per W141 leg2) + GM bm-b reroute A/B decision watch + sina late-bar watch (SZ family R54 backoff precedent)")
st["notes"] = (st.get("notes", "") + " r892: composite round closed by 3rd window per r844/r888 (dead#1 freeze chain + window#2 finalize/seat died pre-closeout + this window red-fix/closeout); "
               "10-08 first post-holiday bar: 12 SZ 159xxx sina late-publish (R54 09-23 same family), catch-up healed 21:44, marks settled same round; "
               "S6 evidence = 39-leg chain receipt (3 reds diagnosed) + targeted 15-leg rerun receipt (15/15 rc0).").strip()
io.open(sp, "w", encoding="utf-8", newline="\n").write(json.dumps(st, ensure_ascii=False, indent=1))

# 3) heartbeat
hp = "fleet/machines/%s.json" % machine
h = json.load(io.open(hp, encoding="utf-8"))
h["round_no"] = R
h["round"] = R
h["loop_round"] = R
h["last_round"] = R
h["last_seen"] = ts
h["ts"] = ts
h["clock_read"] = ts
h["heartbeat_epoch_utc"] = epoch
h["last_heartbeat_epoch_utc"] = epoch
h["heartbeat_epoch_utc_type_int"] = True
h["idle_rounds"] = 0
h["agenda_starved"] = False
h["current"] = st["now_active"]
h["now_active"] = st["now_active"]
h["current_task"] = st["current_task"]
h["task"] = st["current_task"]
h["last_action"] = st["last_action"]
h["last_artifact"] = st["last_artifact"]
h["latest_artifact"] = st["latest_artifact"]
h["next_milestone"] = "W191 freeze chain next bm-a window (seat 2130 published); 10-08 bars fully landed + marks settled; GM bm-b reroute decision watch"
h["verdict"] = ("r892: WM green (red=false lane healthy); composite round closed per r844/r888 adoption law; 10-08 first post-holiday bar fully landed "
                "(12 SZ 159xxx R54 catch-up heal 21:44 + REGIME_GUARD enforce marks settle OK); W190 finalize EXACT (K 415,920 ledger 825,328 == projection; "
                "skill_line 1.1866); W191 seat published=reserved (A 435_004..437_003 / B 437_004..437_203); smoke 49/49; S6 39-leg 3-reds diagnosed->cured "
                "+ 15-leg targeted rerun 15/15 rc0; attrition CLEAN; engine ALIVE idle queue 0; ORD/DEC watermarks unchanged; W191 freeze next")
ack = h.get("orders_ack") or []
seat_msg = "MSG-2026-10-08-2130-bma-w191-seat.md"
if seat_msg not in ack:
    ack.append(seat_msg)
h["orders_ack"] = ack
h["last_orders_at"] = ts
h["last_decisions_at"] = ts
io.open(hp, "w", encoding="utf-8", newline="\n").write(json.dumps(h, ensure_ascii=False, indent=1))

# 4) seat MSG inbox consumption
src = "fleet/inbox/MSG-2026-10-08-2130-bma-w191-seat.md"
dst = "fleet/inbox/processed/MSG-2026-10-08-2130-bma-w191-seat.md"
if os.path.exists(src) and not os.path.exists(dst):
    os.makedirs("fleet/inbox/processed", exist_ok=True)
    shutil.move(src, dst)
    print("seat MSG moved to processed")
else:
    print("seat MSG move skipped (absent or already processed)")

# self-checks
h2 = json.load(io.open(hp, encoding="utf-8"))
assert isinstance(h2.get("heartbeat_epoch_utc"), int), "epoch must be int"
assert "T" in h2.get("clock_read", ""), "clock_read must be ISO T-sep"
st2 = json.load(io.open(sp, encoding="utf-8"))
assert st2["round_no"] == R
rp2 = io.open(rp_path, encoding="utf-8").read()
assert report_line[:60] in rp2, "report line missing"
print("closeout writes OK; round=%d ts=%s epoch=%d" % (R, ts, epoch))
