"""r807 bm-b S7 closeout: heartbeat + state + round report line."""
import io
import json
import subprocess
import time

TS = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())


def sh(*args):
    return subprocess.run(args, capture_output=True, text=True).stdout.strip()


def free_ram_gb():
    try:
        import psutil
        return round(psutil.virtual_memory().available / 2**30, 2)
    except Exception:
        return None


def gpu_free_mb():
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.free",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True).stdout.strip().splitlines()[0]
        return int(out)
    except Exception:
        return None


def ahead_behind():
    ab = sh("git", "rev-list", "--left-right", "--count",
            "origin/main...HEAD")
    behind, ahead = (int(x) for x in ab.split()) if ab else (0, 0)
    return ahead, behind


# ---------------- heartbeat ----------------
HB = "fleet/machines/bm-b.json"
hb = json.load(io.open(HB, encoding="utf-8"))
hb.update({
    "round": 807, "round_no": 807,
    "now_active": "r807: trio finalize x3 absorbed (insufficient-sample "
                  "single-read r638) + ledger fork re-anchored 825328->831336 "
                  "+ legs 25-28 re-armed rc0x4 + S6 w4 chain in-flight",
    "current_task": "S6 w4 chain absorb on completion (astock refresh ~03:30) "
                    "+ quality family NAV-pathology probe + ex-date joint "
                    "probe (divlowvol over-band face)",
    "task": "absorb/closeout",
    "latest_artifact": "results/fund_trio_p1_ledger_reanchor.json "
                       "(ledger head 831,336; receipt "
                       "_r807bmb_ledger_reanchor_receipt.json) + 3x prereg "
                       "SS7/SS8 backfill @01:0x",
    "next_milestone": "S6 w4 legs 16-35 + QA r806 auto-complete ~03:30 "
                      "(absorb next round) + divlowvol ex-date probe <=10-10 "
                      "12:00 + quality NAV pathology triage <=10-10 12:00",
    "verdict": "healthy-absorb-complete",
    "last_action": "r807 absorb round: prereg backfills + attrition rows + "
                   "O-2315 receipt + O-2358 claim reland + push sync closure "
                   "(O-20261009-0024)",
    "last_round_at": TS, "last_seen": TS, "updated": TS, "ts": TS,
    "clock_read": TS,
    "heartbeat_epoch_utc": EPOCH,
    "cpu_cores": 16,
    "free_ram_gb": free_ram_gb(),
    "gpu_free_vram_mb": gpu_free_mb(),
    "orphan_faces": 1,
    "orphan_face_note": "pid 25464 = r806 closeout driver awaiting its ACTIVE "
                        "astock refresh child (pid 13992 cpu_delta 4.7) = "
                        "lawful wait chain, not adopt-killed; products "
                        "absorbed this round; driver completes on its own",
    "idle_rounds": 0, "agenda_starved": False,
})
ahead, behind = ahead_behind()
hb["sync"] = {"ahead": ahead, "behind": behind,
              "last_push_ts": hb.get("sync", {}).get("last_push_ts"),
              "note": "O-20261009-0024 sec1-4 sync face; this write is "
                      "pre-push, post-push refresh follows in-round"}
for oid in ("O-20261008-2315-bm-c.md", "O-20261008-2323-bm-b.md",
            "O-20261009-0024-bm-b.md"):
    if oid not in hb["orders_ack"]:
        hb["orders_ack"].append(oid)
hb["orders_ack_count"] = len(hb["orders_ack"])
assert isinstance(hb["heartbeat_epoch_utc"], int)
io.open(HB, "w", encoding="utf-8", newline="\n").write(
    json.dumps(hb, ensure_ascii=False, indent=1) + "\n")
print("HB_OK epoch_int=%s ack=%d ahead=%d behind=%d"
      % (isinstance(hb["heartbeat_epoch_utc"], int),
         hb["orders_ack_count"], ahead, behind))

# ---------------- state ----------------
ST = "state.json"
st = json.load(io.open(ST, encoding="utf-8"))
st.update({
    "machine_id": "bm-b", "round_no": 807, "round_no_label": "r807",
    "note": "r807: trio finalize absorb round. Verdicts insufficient-sample "
            "x3 (G-SEG chop 14/50 structural, single-read r638); ledger fork "
            "detected+healed (stale-tree prev 790905 vs live head 825328; "
            "additive re-anchor FUND-TRIO-REANCHOR-R807 -> head 831336, "
            "trio 6008 counted once); prereg SS7/SS8 backfilled x3; "
            "attrition rows x3 (guard CLEAN); legs 25-28 re-armed rc0x4 on "
            "10-08 reopen bar; O-2315 receipt + O-2358 claim reland; "
            "O-20261009-0024 sync law adopted",
    "last_round_at": TS, "ts": TS, "updated": TS, "last_seen": TS,
    "clock_read": TS, "updated_at": TS,
    "last_round_ts": st.get("last_round_ts"),
    "did": "r807: (1) S0 identity bm-b; churn-absorb own daemon faces; pull "
           "--rebase up-to-date (r806 push had landed 00:33, undelivered=1 "
           "note was stale). (2) S0.5: orders diff -> O-2315 bm-b receipt "
           "written (resume=维持全力), O-2323 acked (executed by r806+this "
           "round), O-20261009-0024 sync law executed (fetch->integrate->"
           "push closure + heartbeat sync fields); O-20261006-2358 s8.2 "
           "trio-burn self-claim relanded on backlog T-94 (r806 claim died "
           "in wrapper-beheading, never hit git); D-19 dual read MATCH both "
           "faces at group-tree last-fetched refs (fetch transient-failed "
           "schannel, facts _r807bmb_d19_read.json, fail-open). (3) MAIN "
           "PRODUCT: trio finalize absorption -- verdicts insufficient-"
           "sample x3 (G-SEG bear70/bull65/chop14/na246; single-read r638 "
           "law); append_ledger verify exposed REAL FORK: trio finalized on "
           "network-blocked stale tree (prev 790905 freeze-era) while fleet "
           "head advanced to 825328 (W177..W190) -> 6008 trials invisible "
           "to ledger_head() -> healed via additive re-anchor row (canonical "
           "append_ledger, fresh batch FUND-TRIO-REANCHOR-R807, head now "
           "831336, single-count, superseded branch totals documented); "
           "prereg SS7 post-run evidence + SS8 postmortems backfilled x3 "
           "(quality family NAV negative-crossing pathology disclosed, "
           "rolling 3/5/10y figures marked unreadable artifacts; "
           "divlowvol over-band -> ex-date probe follow-up per its own "
           "SS5(a) law); gate_attrition rows x3 (guard scan CLEAN). (4) "
           "legs 25-28 re-arm on 10-08 reopen bar: update_etf_daily 5/5 +1 "
           "row -> REGIME_GUARD v3 enforce live.paper 5 members anchored "
           "rc0 -> t35_open_fill PASS (zero-pending honest) -> t24 "
           "prospect paper 22/22 -> promotion gate 0/22 NOT-ELIGIBLE "
           "honest. (5) S1 smoke 49/49; satengine alive rc0 idle; watermark "
           "red=false insufficient_history n=1 legal reset; py probe "
           "local_batch_running=true (astock refresh 5217-stock in-flight, "
           "ETA ~03:30, S6 w4 chain legs 16-35 + QA r806 auto-complete "
           "await). (6) S7: orphan probe 1 face = lawful wait chain (pid "
           "25464 driver awaiting active astock child), read-only no kill; "
           "pit entry direct-write pit-protocol-judge.md (stale-tree "
           "finalize fork law) + CODELY pointer.",
    "verdict": "green: smoke 49/49; legs 25-28 rc0x4; ledger head 831336 "
               "single-chain; attrition guard CLEAN; orders acked +3; "
               "satengine alive idle; orphan=1 lawful-wait; S6 w4 chain "
               "in-flight (astock refresh)",
    "current_task": "r807 closed; next = S6 w4 completion absorb (r808) + "
                    "QA r806 pack absorb + divlowvol ex-date probe + quality "
                    "NAV pathology triage + 5x HANDOVER r810",
    "next": "(1) absorb S6 w4 chain legs 16-35 rc faces + QA r806 pack "
            "(~03:30 window); (2) divlowvol ex-date joint probe (over-band "
            "face, prereg SS5(a) mandated, <=10-10 12:00); (3) quality "
            "family NAV-pathology triage (max_dd -1.1454 negative-crossing, "
            "engineering probe, <=10-10 12:00); (4) D-19 group-tree re-fetch "
            "when network stabilizes (transient schannel fail); (5) 5x "
            "HANDOVER at r810",
})
io.open(ST, "w", encoding="utf-8", newline="\n").write(
    json.dumps(st, ensure_ascii=False, indent=1) + "\n")
print("STATE_OK round=807")

# ---------------- round report ----------------
RR = "logs/iteration-loop/round_reports.md"
line = (
    "%s | r807 bm-b | WM-VERDICT: green (red=false lane healthy; probe "
    "insufficient_history n=1 new-window legal reset r738 precedent; "
    "local_batch_running=true astock 5217-stock refresh in-flight) | "
    "孤儿面=1 (pid 25464 r806 closeout driver awaiting ACTIVE astock child "
    "13992 cpu 4.7 = lawful wait chain, read-only no kill, products "
    "absorbed) | did: TRIO FINALIZE ABSORB = milestone product closed: "
    "verdicts insufficient-sample x3 (G-SEG chop 14/50 structural face "
    "bear70/bull65/chop14/na246, single-read r638, no re-run); append_ledger "
    "verify exposed REAL FORK (finalize on network-blocked stale tree prev "
    "790905 vs fleet head 825328 W177..W190; 6008 trials invisible to "
    "ledger_head max-total semantics) -> HEALED via canonical additive "
    "re-anchor FUND-TRIO-REANCHOR-R807 (append_ledger fresh-batch channel, "
    "prev auto-derived 825328 -> head 831336, single-count, superseded "
    "branch totals documented never-re-add; receipt "
    "results/_r807bmb_ledger_reanchor_receipt.json); prereg SS7/SS8 "
    "backfilled x3 (divlowvol sharpe 0.8941 over-band -> ex-date probe "
    "follow-up per SS5(a); quality NAV negative-crossing pathology "
    "disclosed max_dd -1.1454 rolling figures unreadable artifacts; value "
    "in-band 0.3809 but M1/DSR/PBO red); gate_attrition x3 rows + guard "
    "scan CLEAN; S0.5: O-2315 bm-b receipt written (维持全力), O-2323+"
    "O-20261009-0024 acked (sync law adopted: fetch->push closure + "
    "heartbeat sync fields), O-20261006-2358 s8.2 self-claim relanded "
    "backlog T-94 (r806 claim died in beheading never hit git), D-19 dual "
    "MATCH at group-tree last-fetched refs (fetch transient schannel fail, "
    "fail-open, re-fetch next round); legs 25-28 re-arm on 10-08 reopen "
    "bar: etf_daily 5/5 +1 -> REGIME_GUARD v3 enforce live.paper 5 members "
    "rc0 -> t35 PASS zero-pending -> t24 22/22 -> promotion 0/22 honest "
    "NOT-ELIGIBLE; S1 smoke 49/49; satengine alive idle rc0 | evidence: "
    "results/fund_trio_p1_ledger_reanchor.json + _r807bmb_ledger_reanchor_"
    "receipt.json + results/_r807bmb_d19_read.json + _attrition_guard_scan."
    "json (CLEAN) + results/etf_daily_pull_status.json + results/"
    "t35_open_fill_verify.json | 本地未达 origin commit 数=push 收口见 "
    "r807 addendum | next: S6 w4 completion absorb (astock ETA ~03:30 + "
    "QA r806 pack) + divlowvol ex-date probe + quality NAV pathology "
    "triage (both <=10-10 12:00) + 5x HANDOVER r810\n" % TS
)
with io.open(RR, "a", encoding="utf-8", newline="\n") as fh:
    fh.write(line)
print("RR_OK")
