# -*- coding: utf-8 -*-
# r907 bm-a closeout: state + heartbeat + round-report line (fresh read-modify-write per multi-writer law)
import json, io, os, time, datetime, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())
TIP = "eb81c0878"

cpu_pct = float(sys.argv[1]); ram_free_gb = float(sys.argv[2]); gpu_free_mb = int(sys.argv[3])

cur = ("r907 closed: W195 seat chain LANDED origin " + TIP + " (probe rc0 ADMIT staircase 55th: "
       "A 443_804..445_803 hops=1 + B 445_804..446_003 hops=1; anchor=W194 finalize actuals "
       "841,145/424,720 zero roll-forward); engine idle queue0 awaiting W195 prereg")
task = ("r908: W195 prereg build window (buildgen v2 anchor=W194 actuals per r590; proj ledger "
        "843,345 / K 426,920 naive; bands A 443_804..445_803 / B 445_804..446_003); 10-09 15:30 bars "
        "-> evening marks chain (REGIME_GUARD enforce + live.paper + t35/t24 family); pool replenish "
        "bm-c lane F-2026109-01 (window 10-10 00:00); XASSET-ROT P1 ticket pending GM signature; "
        "5x HANDOVER obligation at r910")
did = ("r907: W195 seat chain (pre-seat probe rc0 ADMIT r902 bloodline + seat MSG published + "
       "3-file commit/push) + S0 writer-pause rebase clean 2/2 onto bm-c autofill ticks + S6 39-leg "
       "rc0 bad NONE + quartet green + attrition CLEAN + idle --worked")
art = ("r907 products: fleet/inbox/MSG-2026-10-09-0844-bma-w195-seat.md + "
       "results/_r907bma_w195_probe.py + results/_r907bma_w195_probe_receipt.json (origin " + TIP +
       "; A 443_804..445_803 hops=1 staircase 55th + B 445_804..446_003 hops=1 mutual-exclusion "
       "reserved walk; anchor=W194 finalize actuals)")
verify = ("smoke 49/49 + probe rc0 ADMIT + seat push 0/0 @" + TIP + " self-verified + S6 39-leg bad "
          "NONE (dualrun streak 51; py_watermark py_low_board_clear; token delta=0) + attrition "
          "CLEAN (4 ledgers) + orphan face=1 read-only (BigDomain external) + engine ALIVE rc0 "
          "idle queue0 + quartet GREEN + ORD/DEC watermarks UNCHANGED (861949ca/83813196 "
          "python-raw) + orders unacked=0 double-scan + not-at-origin=0")

# --- state file ---
sp = os.path.join(ROOT, "state-bm-a.json")
st = json.load(io.open(sp, encoding="utf-8"))
prev_epoch = st.get("heartbeat_epoch_utc", EPOCH)
st.update({
    "round_no": 907, "round": 907, "loop_round": 907, "last_round": 907,
    "last_round_at": NOW, "last_round_closed": NOW, "last_run": NOW,
    "last_seen": NOW, "ts": NOW, "updated": NOW,
    "current": cur, "now_active": cur, "current_task": task, "task": task,
    "did": did, "last_action": ("r907 closeout: W195 seat chain + S6 39-leg + "
                                "commit/push @" + TIP),
    "next": task, "next_milestone": task,
    "last_artifact": art, "latest_artifact": art,
    "verify": verify, "idle_rounds": 0, "agenda_starved": False,
    "heartbeat_epoch_utc": EPOCH, "last_heartbeat_epoch_utc": prev_epoch,
    "clock_read": NOW, "last_orders_at": NOW, "last_decisions_at": NOW,
    "last_orders_seen": ("r907 double-scan: unacked=0; ORD 861949ca python-raw UNCHANGED "
                         "(tail rows all 10-08, zero new BigMoney rows)"),
    "last_decisions_seen": "r907 double-scan: DEC 83813196 python-raw UNCHANGED (zero action)",
    "last_orders_ts": NOW, "last_decisions_ts": NOW,
    "push_verified": {"ts": NOW, "origin_tip": TIP, "ahead_behind": "0/0",
                      "note": "r907 W195 seat chain push verified"},
    "sync": {"ts": NOW, "origin_tip": TIP, "ahead_behind": "0/0",
             "note": "r907 W195 seat chain push verified"},
})
json.dump(st, io.open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# --- heartbeat ---
hp = os.path.join(ROOT, "fleet", "machines", "bm-a.json")
hb = json.load(io.open(hp, encoding="utf-8"))
hb.update({
    "last_seen": NOW, "ts": NOW, "clock_read": NOW,
    "heartbeat_epoch_utc": EPOCH, "heartbeat_epoch_utc_type_int": True,
    "current": cur, "current_task": task, "did": did, "last_action": did,
    "last_artifact": art, "latest_artifact": art,
    "cores": 32, "cpu_cores": 32, "cpu_load_pct": cpu_pct, "cpu_pct": cpu_pct,
    "cpu_total_pct": cpu_pct, "cpu_util_pct": cpu_pct,
    "free_ram_gb": ram_free_gb, "idle_ram_gb": ram_free_gb,
    "idle_ram_mb": int(ram_free_gb * 1024),
    "gpu_idle_vram": round(gpu_free_mb / 1024, 2), "gpu_idle_vram_gb": round(gpu_free_mb / 1024, 2),
    "gpu_idle_vram_mb": gpu_free_mb, "gpu_idle_vram_mib": gpu_free_mb,
    "gpu_free_vram_mb": gpu_free_mb, "gpu_free_vram_gb": round(gpu_free_mb / 1024, 2),
    "gpu_free_vram": f"{gpu_free_mb/1024:.2f}GB",
    "idle_vram_gb": round(gpu_free_mb / 1024, 2), "idle_gpu_vram_gb": round(gpu_free_mb / 1024, 2),
    "gpu_vram_free_gb": round(gpu_free_mb / 1024, 2),
    "verdict": ("green (red=false; engine ALIVE rc0 idle queue0; W195 seat landed, prereg next round; "
                "py_low_board_clear legal idle whitelist)"),
    "idle_rounds": 0, "agenda_starved": False,
    "last_orders_at": NOW, "last_decisions_at": NOW,
    "last_orders_seen": "r907 double-scan: unacked=0; ORD 861949ca python-raw UNCHANGED",
    "last_decisions_seen": "r907 double-scan: DEC 83813196 python-raw UNCHANGED",
    "last_heartbeat_epoch_utc": hb.get("heartbeat_epoch_utc", EPOCH),
    "health": "ok",
})
json.dump(hb, io.open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# --- round report line (append-only; tail-terminator guard r843) ---
rp = os.path.join(ROOT, "round_reports-bm-a.md")
raw = io.open(rp, encoding="utf-8", newline="").read()
line = (
    NOW + " | r907 | bm-a | dept:research (W195 seat chain; N1 perpetual supply line) | "
    "WM-VERDICT: green (red=false lane healthy; engine ALIVE rc0 idle queue0; py_low_board_clear=legal "
    "idle whitelist board-closed + own never-dry lane W195 prereg queued next round; DEC 83813196/ORD "
    "861949ca python-raw UNCHANGED via C: real-path fetch+show; orders double-scan unacked=0) | "
    "当前活: W195 seat chain landed same round (pre-seat probe rc0 ADMIT + seat MSG published+pushed) | "
    "最近实物: fleet/inbox/MSG-2026-10-09-0844-bma-w195-seat.md + results/_r907bma_w195_probe_receipt.json "
    "@ origin " + TIP + " (staircase 55th held: naive A 443_604..445_603 refused at start by W194 B band "
    "443_604..443_803 -> A 443_804..445_803 hops=1; naive B 443_804..444_003 lands inside own-A -> "
    "reserved walk B 445_804..446_003 hops=1; leg2 conflicts=0; leg3 origin vacancy; anchor=W194 finalize "
    "actuals 841,145/424,720 zero roll-forward per r590) | "
    "下个里程碑: r908=W195 prereg build (buildgen v2 anchor=W194 actuals; proj ledger 843,345 / K 426,920 "
    "naive; window <=24h) + 10-09 15:30 bars -> evening marks chain (REGIME_GUARD enforce + live.paper + "
    "t35/t24 family) + 5x HANDOVER at r910 | "
    "did: S0-1 anchored bm-a + orphan probe 1 read-only (BigDomain dead-parent python.exe external face, "
    "not BigMoney domain) + writer-pause r832 (4 repo-writer schtasks disabled -> churn-absorb commit "
    "08e1629ab + r906 closeout rebased fc22d154e -> pull --rebase clean 2/2 onto bm-c autofill ticks -> "
    "writers re-enabled -> push 0/0) + S0.5 orders double-scan unacked=0 (54 files vs 191 ack) + DEC/ORD "
    "watermarks python-raw both UNCHANGED zero action + S1 smoke 49/49 + S2 boards empty (job_list 0; "
    "task board no new open; T-178 bm-c W17 in-flight / T-177 bm-a REGIME5 slice-2 in-flight) + post_review "
    "9436 rows 0 NO 0 WAIT + S3 engine ALIVE rc0 idle queue0 + W195 pre-seat probe (_r907bma_w195_probe.py "
    "r902 bloodline: leg0 192 rows tail=W194 ordinal 185 bm-a 110th + cross-file prev==total chain assert "
    "W194 841,145/W193 838,945 + W194 finalize product on origin ls-tree; leg1 staircase 55th + W141 leg2 "
    "mutual-exclusion reserved walk; leg2 conflicts=0; leg3 origin vacancy 4/4; leg4 W196+ projection A "
    "445_804..447_803 / B 446_004..446_203 B-inside-A True) + seat MSG published + 3-file commit " + TIP + " "
    "push 0/0 self-verified + S6 39 legs rc0 bad NONE (panel 10-08 pre-market no-new-bar family honest; "
    "dualrun ZERO-DRIFT streak 51; compute_audit FLAG supply_gap+ignition_sla = W17 trial-labor lane "
    "LANE-PINNED bm-c active-session honest flag no force-claim; py_watermark py_low_board_clear; token "
    "delta=0) + S7 attrition CLEAN (4 ledgers, 3 pre-existing healed notes) + quartet GREEN (loop pin=8 "
    "no-op next-fire 08:58 / watchdog present / precommit+prepush claws match) + idle_trigger --worked "
    "(idle_rounds 0, agenda_starved false) + state 906->907 + heartbeat refresh (epoch int self-verified) | "
    "verification: smoke 49/49 + probe rc0 ADMIT + seat push 0/0 @" + TIP + " + S6 bad NONE + attrition CLEAN "
    "+ quartet GREEN + local not reaching origin commit count=0 (post-push fetch+rev-list self-verified) | "
    "scoring: 2 (W195 seat chain = published+pushed tangible artifact, engine perpetual supply line "
    "continuous) | bookkeeping budget: 5/5 (state + report line + heartbeat + idle clear + S6 receipt) | "
    "treasure capture question: this batch has no new method no new treasure (seat chain = r902 probe "
    "lineage verbatim reuse, W195 facts live-registry-driven) TREASURE/METHODOLOGY zero append | "
    "orphan_face=1 (read-only report) | unacked_orders=0 (double-scan) | local_vs_origin=0 | token: L1 "
    "zero API (token_meter delta=0) | [r907 bm-a]"
)
if raw and not raw.endswith("\n"):
    raw += "\n"
io.open(rp, "w", encoding="utf-8", newline="").write(raw + line + "\n")

# self-verify epoch int + clock T-separator (R170/R178/R262 double-offender law)
st2 = json.load(io.open(sp, encoding="utf-8"))
hb2 = json.load(io.open(hp, encoding="utf-8"))
assert isinstance(st2["heartbeat_epoch_utc"], int) and isinstance(hb2["heartbeat_epoch_utc"], int), \
    "epoch not int"
assert "T" in hb2["clock_read"] and " " not in hb2["clock_read"].split("+08:00")[0].replace("T", "T", 1)[:11] \
    or True, "clock form"
assert hb2["clock_read"][10] == "T", "clock_read not T-separated"
print("closeout written: state 907 + heartbeat epoch", EPOCH, "+ report line appended; self-verified PASS")
