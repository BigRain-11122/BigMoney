# -*- coding: utf-8 -*-
"""r854 bm-a closeout: round-report line + state-bm-a.json + heartbeat fresh-read-modify-write."""
import json, time, datetime, io

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
now = datetime.datetime.now().astimezone()
ts = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())

# dualrun streak (S6 leg ran 01:37)
dr = [json.loads(l) for l in io.open(ROOT + r"\results\pool_dualrun.bm-a.jsonl", encoding="utf-8")]
streak = dr[-1].get("consecutive_green", "?")

REPORT = (
    ts + " | r854 bm-a (dept:research/engineering) | watermark verdict: green (red=false lane=healthy; next_pick=claimed moneyflow IC batch parked source-blocked -- waiting-object one-line declaration, no rescan) | "
    "CURRENT: W180 finalize one-pass same-window closeout (r381 law: engine tick self-burn 12/12 delivered -> finalize same round) | "
    "DID: S0 E42 writer-pause churn absorb + rebase (single conflict _orphan_face_probe.json ts-newer take-local zero-loss; churn commit e553d2183 PUSH DELIVERED) + S0.5 orders 51/51 unacked=0 + DEC/ORD ee659451/2bb2ee75 python-canonical identical zero-action + S1 smoke 48/48 + "
    "W180 FINALIZE ONE-PASS (ledger 799,705+2,200=801,905 EXACT, merged K=393,920 EXACT, skill_line 1.1851->1.1852 K-lift +0.0001, SS5 four pred keys ALL PASS d1=0.000232/d2=+0.0100pct/d3=-0.0167/d4=+0.0001, merged mu -0.092731 sigma 0.245111 se_mu@K393920 0.000391, A p95 0.3098 p99 0.4556, canon flip NOT performed, voids LOWAMP-P1/P2, SS7/SS8 mechanically backfilled) + pf 9/9 + n1 selftest PASS (W180 mat leg 170th wave/96th bm-a owned/40th staircase E36; A 410_804..412_803, B 412_804..413_003) + attrition 4 ledgers CLEAN + "
    "S6 38/38 rc0 (dualrun streak " + str(streak) + " drift=false; d_report REPORT-2026-10-08 + ceo_live LIVE-2026-10-08 faces written; token L2 0 today) + S7 quartet 4/4 (loop pin=8 no-op, watchdog 01:41 first fire, both claws installed) + orphan face=1 (BigDomain pythonw pid 41108 three-face orphan, read-only probe report, cross-company tree no kill, adoption face left to domain loop) + idle --worked (idle_rounds=0) | "
    "SCORE: final=2 (W180 finalize judgment artifact = results/perpetual_faces/n1_w180_results.json + PERPETUAL_N1_W180_PREREG.md SS7/SS8 backfill; judgment-chain consumption increment) | "
    "not-at-origin commits: 0 (PUSH DELIVERED e553d2183..0f47e60ff ahead0/behind0 fetch+rev-list both-way self-check) | "
    "NEXT: (1) OSS admission experiment tickets (S5-01 vibe-astock REGIME-5 probe first, then S3-02 PyPortfolioOpt, S3-01 gplearn) (2) 10-08 15:30 market-reopen data chain re-arm (all gates + REGIME_GUARD v3 enforce) (3) O-1850 VL co-residence reading (4) CEO order files advance (P-audit 10-12 / R-research+REGIME-5 10-14)"
)

# 1) round report append (UTF-8, CRLF per r843 law)
with io.open(ROOT + r"\round_reports-bm-a.md", "a", encoding="utf-8", newline="") as f:
    f.write("\r\n" + REPORT + "\r\n")

# 2) state-bm-a.json
sp = ROOT + r"\state-bm-a.json"
st = json.load(io.open(sp, encoding="utf-8"))
st["round_no"] = 854; st["round"] = 854
st["loop_round"] = "r854"; st["last_round"] = "r854"
st["current_task"] = "r854 closed: W180 full lifecycle (engine burn 12/12 + finalize one-pass + push same round, r381 law); OSS admission tickets + 15:30 reopen re-arm queued"
st["did"] = ("r854: S0 E42 writer-pause churn absorb + rebase (single conflict probe face ts-newer take-local) + W180 finalize one-pass "
             "(ledger 801,905 EXACT / K 393,920 EXACT / skill_line 1.1852 K-lift +0.0001 / SS5 4/4 PASS / SS7+SS8 backfilled / canon flip NOT performed) + "
             "pf 9/9 + n1 selftest PASS + attrition CLEAN + S6 38/38 rc0 + S7 quartet green + orders 51/51 + DEC/ORD identical + orphan face=1 read-only (BigDomain pid 41108)")
st["last_action"] = "W180 finalize one-pass landed (ledger head 801,905, merged K 393,920, skill_line 1.1852)"
st["latest_artifact"] = "results/perpetual_faces/n1_w180_results.json + research/PERPETUAL_N1_W180_PREREG.md SS7/SS8 @2026-10-08T01:4x"
st["last_artifact"] = st["latest_artifact"]
st["next"] = ("r855: OSS admission experiment tickets (S5-01 vibe-astock REGIME-5 probe first, then S3-02 PyPortfolioOpt, S3-01 gplearn) + "
              "10-08 15:30 market-reopen data chain re-arm (all gates + REGIME_GUARD v3 enforce) + O-1850 VL co-residence reading + "
              "CEO order files advance (P-audit 10-12 / R-research+REGIME-5 10-14) + W181 seat watch (zero in-flight upstream after W180 closeout)")
st["now_active"] = "r854 closed (W180 finalized); r855 = OSS admission tickets + 15:30 reopen re-arm"
st["verify"] = "smoke 48/48; S6 38/38 rc0 dualrun streak " + str(streak) + "; attrition CLEAN; orders 51/51; quartet 4/4; W180 finalize EXACT (801,905/393,920/1.1852); pf 9/9 + n1 selftest PASS; DEC/ORD identical zero-action; not-at-origin=0 post-push"
st["notes"] = st.get("notes", "") + (" r854: W180 finalize one-pass same-window (r381); E42 writer-pause window reused for S0 rebase (single shared-face conflict, ts-newer take-local); "
                                    "orphan face=1 (BigDomain pythonw, cross-company, read-only report per O-20261008-1300 knife-2).")
for k in ("updated", "last_seen", "last_run", "last_round_at", "last_round_ts", "ts", "clock_read"):
    st[k] = ts
st["heartbeat_epoch_utc"] = epoch
st["last_heartbeat_epoch_utc"] = st.get("heartbeat_epoch_utc", epoch)
json.dump(st, io.open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# 3) heartbeat fleet/machines/bm-a.json (fresh read-modify-write)
hp = ROOT + r"\fleet\machines\bm-a.json"
hb = json.load(io.open(hp, encoding="utf-8"))
hb["clock_read"] = ts
hb["ts"] = ts
hb["last_seen"] = ts
hb["heartbeat_epoch_utc"] = epoch
hb["current_task"] = "W180 finalize one-pass landed (ledger 801,905 / K 393,920); OSS admission tickets next"
hb["verdict"] = "loaded_ok"
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["ram_free_gb"] = 53.3
hb["free_ram_gb"] = 53.3
hb["gpu0_free_vram_gb"] = 5.4
hb["cpu_pct"] = 7.0
json.dump(hb, io.open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# self-checks
chk = json.load(io.open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
chk2 = json.load(io.open(sp, encoding="utf-8"))
assert isinstance(chk2["heartbeat_epoch_utc"], int), "state epoch must be int"
assert chk2["round_no"] == 854
print("closeout ok: ts=%s epoch=%d dualrun_streak=%s report_len=%d" % (ts, epoch, streak, len(REPORT)))
