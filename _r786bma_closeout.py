# -*- coding: utf-8 -*-
"""r786 bm-a S5+S7 closeout: state file, heartbeat, RR lines (fresh read-modify-write)."""
import json, time, datetime, io

now_dt = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
ts = now_dt.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())

# ---------- 1) state-bm-a.json (root) ----------
SP = r"state-bm-a.json"
st = json.load(io.open(SP, encoding="utf-8"))
prev_round = st["round_no"]
assert prev_round == 784, prev_round
st["round_no"] = 786            # absorb dead-r785 (S7 tail lost) + this round r786
st["round"] = 786
st["loop_round"] = st.get("loop_round", 600) + 1
st["last_round"] = "r786"
st["last_round_at"] = ts
st["last_round_ts"] = "2026-10-06T17:2x"
st["current_task"] = ("W162 seat+freeze window next session (W161 finalize landed r786; "
                      "never-dry seat/freeze per r781 double-file lineage)")
st["did"] = ("r786: W161 finalize ONE-PASS (ledger 757,412 -> 759,612 +2,200, K=349,920 -> 352,120 "
             "matching prereg projection; skill_line_v2 1.1825 -> 1.1827 K-lift +0.0002; r708 pre-flight "
             "live-probe+file-probe double green, r381 same-round finalize law) + W161 prereg sec7/sec8 "
             "same-window backfill (four sec5 prediction keys all machine-PASS) + dead-r785 S7 tail "
             "absorbed into state 784->786 (r785 freeze+ignition landed on origin 678a07d4f, died pre-S5/S7) "
             "+ MSG-1735 bm-c watermark divergence resolved both faces (dec 512dc730=local-face hash "
             "corrected to origin blob a44c39e0, content fully consumed; ord 3e8c73e3=SHA-256 current "
             "blob MATCH, algorithm-mismatch false alarm) + reply MSG-175x published + S6 38/38 rc0 126.2s")
st["last_action"] = ("r786 closeout: W161 finalize + prereg backfill + dead-r785 absorption + "
                     "WM key correction + heartbeat + state 786 + RR lines")
st["next"] = ("r787: (a) W162 seat publish + freeze (never-dry line; A naive 371_004..373_003 will be "
              "refused at its own start by the registered W161 B band 371_004..371_203 -- staircase 21st "
              "anticipated, re-derive MANDATORY on post-W161 universe + own-A reservation when deriving B; "
              "r781 double-file freeze+verify lineage, r773 pit-law compliance) -> ignition (b) 10-07 "
              "12:00 D-06 closeout window (pit-data CRLF adjudication + remaining sub-split legs) "
              "(c) T-173 first-version report due 10-08 noon (in flight) (d) 5x=r790 HANDOVER check")
st["last_decisions_sha"] = "a44c39e01f9781be981e208a48d852f6bcef44709d004128591a88df13c62efb"
st["last_decisions_at"] = ts
st["last_decisions_ts"] = "2026-10-06T17:2x"
st["last_orders_at"] = ts
st["last_orders_sha"] = "3e8c73e33922a1b52cde992ffe61ef7e9258f21f76bea179b6895e83adb16b4d"
st["heartbeat_epoch_utc"] = epoch
st["last_seen"] = "2026-10-06 17:4x"
st["ts"] = ts
st["updated"] = ts
st["latest_artifact"] = ("results/perpetual_faces/n1_w161_results.json + "
                         "research/PERPETUAL_N1_W161_PREREG.md sec7/sec8 @2026-10-06T17:2x")
st["verify"] = ("smoke 48/48; W161 finalize: ledger_head 759,612 == prev+2,200, K=352,120 == projection; "
                "n1 selftest PASS + pf selftest 9/9; S6 38/38 rc0 (facts results/_r786bma_s6_facts.json); "
                "attrition guard CLEAN 4 ledgers; orders 158/158 zero unacked; decisions watermark "
                "a44c39e0 re-derived from origin raw blob (K: absent, C: fallback canonical per D-20261004-02(3)); "
                "orders 3e8c73e3 == current origin blob SHA-256 double-verified; loop pin=8 no-op + "
                "watchdog re-registered + claws content-match")
st["notes"] = (st.get("notes", "") + " | r786: WM probe-method incident closed (r785 dec hash 512dc730 was a "
              "local face, not origin blob; corrected to a44c39e0 with content-consumption intact; "
              "cross-machine key comparisons must state hash algorithm).")
io.open(SP, "w", encoding="utf-8", newline="\n").write(json.dumps(st, ensure_ascii=False, indent=1))
print("state round", prev_round, "->", st["round_no"])

# ---------- 2) heartbeat fleet/machines/bm-a.json ----------
HP = r"fleet\machines\bm-a.json"
hb = json.load(io.open(HP, encoding="utf-8"))
hb["heartbeat_epoch_utc"] = epoch
hb["last_heartbeat_epoch_utc"] = st.get("last_heartbeat_epoch_utc", 1791275878)
hb["clock_read"] = ts
hb["ts"] = ts
hb["last_seen"] = ts
hb["last_round"] = "r786"
hb["round"] = 786
hb["round_no"] = 786
hb["loop_round"] = st["loop_round"]
hb["health"] = "ok"
hb["now_active"] = ("W161 finalize landed (ledger 759,612, K=352,120, skill 1.1827); "
                    "engine idle queue empty; W162 seat+freeze window next session")
hb["latest_artifact"] = "results/perpetual_faces/n1_w161_results.json (W161 finalize verdict, 2026-10-06T17:2x)"
hb["next_milestone"] = ("W162 seat+freeze+ignite (never-dry, window <=24h) + 10-07 D-06 closeout 12:00 "
                        "+ T-173 report due 10-08 noon")
hb["last_action"] = ("r786: W161 finalize one-pass (ledger 757,412->759,612, K=352,120, skill 1.1825->1.1827) "
                     "+ dead-r785 S7 tail absorption + WM key correction (dec->a44c39e0)")
hb["task"] = "r786 W161 finalize done; next = W162 freeze window + 10-07 D-06 closeout"
hb["verdict"] = ("green: W161 finalize landed one-pass (r381 same-round law), engine alive idle, "
                 "smoke 48/48, S6 38/38 rc0, attrition CLEAN, orders 158/158 acked")
hb["current"] = "W161 finalized; engine idle"
hb["current_task"] = hb["task"]
io.open(HP, "w", encoding="utf-8", newline="\n").write(json.dumps(hb, ensure_ascii=False, indent=1))
chk = json.load(io.open(HP, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in chk["clock_read"] and "+08:00" in chk["clock_read"], "clock_read T-separator law"
print("heartbeat ok: epoch int", chk["heartbeat_epoch_utc"], chk["clock_read"])
