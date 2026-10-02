# r593 bm-b: S5 round ledger + state + heartbeat writes
# r583 law: heartbeat/state list-type fields (orders_ack) carried verbatim
# from existing file; only dynamic fields updated.
import json, time, datetime as dt

now = dt.datetime.now().astimezone()
stamp = now.strftime("%Y-%m-%dT%H:%M") + "+08:00"
epoch = int(time.time())

REPORT_LINE = (
    f"| {stamp} | round 593 (bm-b) | WM verdict: GREEN (red=false lane=healthy; SatEngine alive "
    "queue 0 idle; board full all-claimed; pool 323 done/1 waiting=W14-GENERATE GM-parked; engine "
    "lane legal rotation-wait: W113 bm-c 12/12 delivered finalize pending within stall window, W114 "
    "bm-a seated freeze pending, bm-b next seatable W115 blocked on W114 registration) | PRODUCT "
    "(dept:研究/工程, J10 line): dashboard.html perpetual N1 engine-wave chain panel landed -- the "
    "main production line had zero wave-chain visibility on the distributed monitor; additive face "
    "monitor/build_status.py _engine_wave_state() on single sources only (perpetual_faces.N1_BANDS "
    "R250 + results/p2cal_ext shard products + perpetual_faces finalize ledger/merged + fleet seat "
    "MSGs; next_registration=114 vs next_seatable=115 semantic split fixed in-round); verify = face "
    "probe 15 asserts + full build() + Edge headless dump-dom 9/9 PASS (N1 row: 注册尾 W113 · 链头 "
    "610948 · K 244320 · mu -0.0928 σ 0.2449 · W113 12/12片 账待落 · 前席 W114 bm-a · 下一可席 "
    "W115); dashboard_status.json/js stale-takeover write legal (bm-a heartbeat 38.2min > 20min, "
    "r378) now carrying engine_wave live on disk | S6 35 legs rc0 (dualrun ZERO-DRIFT streak 37/3; "
    "t35 export + dscorecard stale-takeover derive legal; Golden-Week data legs idempotent no-op; "
    "prosppromo eligible=0/22 honest) | smoke 47/47 after edits; attrition guard CLEAN 4 ledgers; "
    "W114 seat MSG consumed+archived (cross-verified vs N1_BANDS+shard face; next_seatable 115 "
    "consistent with bm-a W115+ projection disclosure, never transcribed r587); D-19 honest skip "
    "r481 special; orders 143/143 double-scan zero-pending; CODELY.md +1 pit entry (subprocess GBK "
    "capture crash law) | next: W115 pre-seat probe when W114 registers (first-free-number law), "
    "moneyflow IC still source-blocked, W14-GENERATE GM-parked, paper Golden-Week no-new-bar block"
)

with open(r"logs\iteration-loop\round_reports.md", "a", encoding="utf-8") as f:
    f.write("\n" + REPORT_LINE + "\n")

# state.json: round_no +1, dynamic fields only
p = r"state.json"
st = json.load(open(p, encoding="utf-8"))
assert st["round_no"] == 592, st["round_no"]
st["round_no"] = 593
st["note"] = ("r593: J10 increment -- perpetual N1 engine-wave chain panel on dashboard.html + "
              "build_status _engine_wave_state() additive face (single-source: N1_BANDS/shards/"
              "finalize-ledger/seat-MSGs; next_registration 114 vs next_seatable 115); face probe "
              "15 asserts + build() + Edge dump-dom 9/9 PASS; dashboard_status stale-takeover "
              "write legal (bm-a hb 38.2min); S6 35 legs rc0 (dualrun streak 37/3); smoke 47/47; "
              "attrition CLEAN; W114 seat MSG archived; orders 143/143; waiting lanes: W115 seat "
              "blocked on W114 registration, W113 finalize bm-c pending in stall window, moneyflow "
              "source-blocked, W14 GM-parked, paper Golden-Week block")
for k in ("last_round_at", "last_round_ts", "ts", "updated", "updated_at"):
    st[k] = now.isoformat(timespec="seconds")
json.dump(st, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# heartbeat: load -> dynamic fields only (orders_ack carried verbatim, r583)
hp = r"fleet\machines\bm-b.json"
hb = json.load(open(hp, encoding="utf-8"))
ack = hb.get("orders_ack")
hb["last_seen"] = now.strftime("%Y-%m-%d %H:%M:%S")
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = now.isoformat(timespec="seconds")
hb["verdict"] = ("product round: J10 dashboard N1 wave-chain panel landed (注册尾 W113 · 链头 610,948 "
                 "· K 244,320 · W113 12/12片账待落 · 前席 W114 bm-a · 下一可席 W115 -- Edge render "
                 "9/9); engine lane legal rotation-wait (W115 blocked on W114 registration); "
                 "moneyflow IC panel-blocked source conn-level; W14-GENERATE GM-parked; paper "
                 "Golden-Week no-new-bar block; orders 143/143 ack both scans")
hb["current_task"] = ("J10 dashboard engine-wave panel landed r593; next milestone: W115 seat+freeze "
                      "when W114 registers (window <=48h)")
for k in ("ts", "updated", "updated_at"):
    hb[k] = now.isoformat(timespec="seconds")
json.dump(hb, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# post-write self-verify (R170/R178 law: epoch must be JSON int)
hb2 = json.load(open(hp, encoding="utf-8"))
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch not int!"
assert hb2.get("orders_ack") == ack and len(ack) == 143, (len(ack or []),)
print("state round 593 + report line + heartbeat written; epoch int OK; orders_ack", len(ack), "carried")
