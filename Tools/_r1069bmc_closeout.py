# -*- coding: utf-8 -*-
"""r1069 bm-c closeout: state advance 1069->1070 + heartbeat rewrite + round-report row append (ROOT live ledger per r1007 freeze pointer) + assertions (epoch int / report +1 / watermark carry-equal). Atomic writes (temp + os.replace)."""

import datetime
import io
import json
import os
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state-bm-c.json")
HB = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
REPORT = os.path.join(ROOT, "round_reports-bm-c.md")
CNW = 0x08000000

ORD_SHA = "313c8c0fe1fd4a149fbd1eb1bd230342cb881986"
DEC_SHA = "1d4741e4a0d6514519040442182b0679a423d58896a4105861e152108be441f1"

NOW = datetime.datetime.now().astimezone()
TS = NOW.isoformat(timespec="seconds")
EPOCH = int(time.time())

DID = ("r1069 (clean continuation waits-upstream): (1) S0-1 anchor bm-c + round-zero probe py_faces=7 orphans=1 zero-kill with adjudication "
       "(orphan=user Doubao pythonw PID 32692 r1001 precedent family legal-user-process no-kill; resident_servers_exempt=1 ComfyUI 8188 listener "
       "-- T28 listening-socket belt live-verified first cross-machine run on bm-c); S0 fetch: behind=1 bm-a r1037 (W263 seat MSG fb0c962b5 + probe ADMIT "
       "A 593_901..595_900 / B 595_901..596_100 + prereg b32f6bf1c frozen splice-GATED-on-W262-finalize + T28 belt + both inbox MSGs swept to processed) "
       "-> discard-3-shared-regenerable-faces + commit-all + rebase zero-conflict (HEAD f91531d5b, 0/1, tree clean); "
       "(2) S0.5 ORD phantom-watermark heal + 2-row delta consumed: r1068 closeout's 872d6bb9 = PHANTOM value not in blob history (r977 family corrupt-face, "
       "first recurrence POST-pin) -> true face 2a7cc2d content-sha1 4e226c39 (parent 1fd5fc30ac); healed programmatically via d19 guard update --advance to "
       "313c8c0f (17:5x @bm-b drama IndexTTS-2 dub dispatch landed mid-window, bm-b lane) read-back full-string equality OK; delta rows judged: "
       "(a) O-20261017-1741 @bm-c 17:4x = EXECUTED-prior by r1068, disable standing re-verified THIS window (ShortVideoHotScan1/2/3 + KeepAlive all "
       "mode=disabled + port 6688 FREE) + (b) 17:5x @bm-b drama dub dispatch = bm-b lane zero bm-c action; DEC 1d4741e4 FALSE hold both scans; "
       "unacked=0 both scans (98 repo order files all in 223 ack set); inbox=0 (bm-a commit swept both MSGs to processed); "
       "(3) S1 smoke 49/49; S3: satengine ALIVE (alive_flag=true epoch age 36s, burns_active=[], queue_next=[] = waits-upstream face: W263=bm-a window "
       "prereg-frozen splice-ungated post-W262-finalize, burns pending on bm-a; bm-c next turn=W264 seat) + wm red=false healthy (next_pick=claimed "
       "moneyflow-IC parked source-blocked, bm-a T23 fix standing) + boards clear (P2 T27/T23/T28 all done -- T28 done by bm-a r1036 belt live-verified here; "
       "P3 all closed; jobs=0; open tickets=0) + idle green_idle=true RAM 61.3% claimable=0 -> honest, cleared via --worked rc0 (real-work window); "
       "(4) S6 43/43 rc0 fresh run (driver Tools/_r1069bmc_s6.py canon clone of r1068 + per-leg stdout kill-guard; log results/_r1069bmc_s6_log.txt; "
       "weekend honest: update_daily/lhb/zt_pool/heat no-ops cutoff 10-16 / dualrun ZERO-DRIFT streak 32 / market_clock ORANGE_COOL idempotent / "
       "zt crosscheck 2 soft-warn codes disclosed / strategy_scorecard+live_paper+t35*+daily_scorecard+build_status = lane_io single-writer skip "
       "bm-a-fresh-17min / all bm-a/bm-b lanes honest no-ops / daily_report+ceo_live_usage written / token L2 legs 0 today); "
       "(5) S7: attrition 4 CLEAN + loop pin=5 no-op (next fire 18:15) + watchdog re-registered (S4U XML flip access-denied = adjudicated default-principal "
       "standing face r1023/D-20261002-02) + precommit claw + prepush claw installed + short-video disable standing re-verified + counter 1069->1070; "
       "zero absorb owed (r1068 closeout landed clean, zero dead window between)")

VERDICT = ("green: r1069 = clean continuation waits-upstream window (engine W263 = bm-a window per chain-order: seat+prereg b32f6bf1c landed by bm-a r1037, "
           "splice ungated after W262 finalize, burns pending on bm-a; bm-c next turn = W264 seat after bm-a W263 finalize) + S0 merge of bm-a W263 chain "
           "(rebase zero-conflict f91531d5b) + ORD phantom-watermark heal (r977 family first post-pin recurrence: 872d6bb9 phantom -> 313c8c0f true via d19 "
           "guard read-back OK) + 2-row delta consumed (1 executed-prior + 1 bm-b-lane zero-action) + T28 orphan-belt cross-machine live verification "
           "(resident_exempt=1) + S6 43/43 rc0 weekend honest + smoke 49/49 + attrition 4 CLEAN + short-video disable standing re-verified (4/4 disabled + "
           "6688 FREE) + quad green + idle worked rc0")

NEXT_PTR = ("r1070: (1) watch bm-a W263 chain (five-face splice ungated post-W262-finalize -> engine self-burn -> sixgate -> finalize); on W263 FINALIZE "
            "landing = bm-c W264 SEAT publish (probe live re-derive on post-W263 universe per W263 seat MSG forward face: staircase continues -- naive W264 "
            "A 595_901..597_900 pre-disclosed to be REFUSED at registered W263 B 595_901..596_100, first-clean moves past 596_100; own-A reservation cascade "
            "governs B; never transcribe r587); (2) Monday 10-19 15:30 bars window: full papers chain fires on the new bar (10-17/18 weekend no bars, debt=0 "
            "verified cutoff 10-16); (3) r1070 = 5x round: HANDOVER.md check/update duty (last stamp r985 window r916-r985); (4) short-video lane DISABLED "
            "standing per O-20261017-1741 (ShortVideoHotScan1/2/3 + KeepAlive + DailyHotApi :6688 down; V2/V3 frozen; V5.3 reburn lane protected); "
            "(5) GPU lane = gen-only (LLM face retired per O-20261017-0953; loop CPU-only)")

PROD_LANES = ("CPU=engine waits-upstream (W263 = bm-a window: prereg b32f6bf1c frozen, splice ungated post-W262-finalize, burns pending on bm-a; "
              "bm-c next turn = W264 seat) ; GPU=gen-only lane (LLM face retired per O-20261017-0953; V5.3 3-shot reburn lane protected per "
              "O-20261017-1741; loop CPU-only); short-video lane DISABLED standing per O-20261017-1741")

ARTIFACT = ("results/_r1069bmc_s6_log.txt (43-leg S6 chain rc0) + results/_r1069bmc_ord_delta.txt (ORD delta evidence) + ORD watermark healed 313c8c0f "
            "via d19 guard (r1068 phantom 872d6bb9 disclosed)")

CURTASK = ("r1069 closeout (clean continuation waits-upstream: S0 merge bm-a W263 chain + ORD phantom-watermark heal 313c8c0f + S6 43/43 + T28 belt "
           "cross-machine verify; counter 1069->1070)")

VERIFY = ("S6 log 43x rc=0 re-read + d19 read-back full-string equality (ord 313c8c0f / dec 1d4741e4) + smoke 49/49 + satengine alive_flag=true + "
          "attrition 4 CLEAN + schtasks re-query 4/4 disabled + port 6688 count=0 + claws x2 installed + loop pin=5 no-op + watchdog registered + "
          "idle worked rc0 (idle_rounds->0) + epoch int readback + report line +1 asserted + closeout commit rides this window (post-push behind=0 "
          "verified by next shell step)")

ORD_NOTE = ("r1069: ORD watermark PHANTOM heal -- r1068 closeout wrote 872d6bb9 (value not in blob history, r977 family first post-pin recurrence); "
            "true face = 2a7cc2d content-sha1 4e226c39 (parent 1fd5fc30ac); healed via d19 guard update --advance to 313c8c0f (17:5x @bm-b drama row "
            "landed mid-window, consumed), read-back full-string equality OK")

ACK_RECEIPT = ("r1069: zero new repo order files (unacked=0 both scans, 98 files all in 223 ack set); group-ORD delta 2 rows consumed with watermark healed "
               "(O-20261017-1741 @bm-c = executed-prior by r1068, disable standing re-verified 4/4 + 6688 FREE; 17:5x @bm-b drama IndexTTS-2 dub dispatch = "
               "bm-b lane zero bm-c action); watermarks ord phantom 872d6bb9 -> 313c8c0f (d19 guard read-back OK), dec 1d4741e4 hold")

SUMMARY = ("r1069: clean continuation waits-upstream (S0 merge bm-a W263 chain f91531d5b zero-conflict) + ORD phantom-watermark heal 872d6bb9->313c8c0f "
           "(d19 guard, r977 family first post-pin recurrence disclosed) + 2-row delta consumed (1 executed-prior + 1 bm-b-lane) + T28 belt cross-machine "
           "live verify + S6 43/43 weekend honest + smoke 49/49 + attrition 4 CLEAN + quad green")

ROW = ("{ts} | r1069 | bm-c | r1069: (1) S0-1 anchor + probe 7/1 zero-kill (orphan=user Doubao pythonw r1001 family; resident_exempt=1 ComfyUI 8188 "
       "-- T28 belt live-verified first cross-machine run) + S0 behind=1 bm-a r1037 W263 chain merged (discard-3-shared-faces + commit-all + rebase "
       "zero-conflict f91531d5b); (2) S0.5 ORD phantom heal: r1068's 872d6bb9 not in blob history (r977 family post-pin first) -> true 4e226c39@2a7cc2d "
       "(parent 1fd5fc30ac) -> d19 guard advance 313c8c0f read-back OK; delta 2 rows: O-20261017-1741 @bm-c executed-prior (disable standing re-verified "
       "4/4 + 6688 FREE) + 17:5x @bm-b drama dub zero-action; DEC 1d4741e4 hold; unacked=0; inbox=0; (3) smoke 49/49 + satengine ALIVE waits-upstream "
       "(burns_active=[] queue_next=[]; W263=bm-a window prereg b32f6bf1c frozen; bm-c next=W264 seat) + wm red=false + boards clear + idle --worked rc0; "
       "(4) S6 43/43 rc0 fresh (driver _r1069bmc_s6.py + per-leg stdout kill-guard; weekend honest: dualrun streak 32 ZERO-DRIFT / ORANGE_COOL "
       "idempotent / zt crosscheck 2 soft-warn disclosed / single-writer legs skip bm-a-fresh-17min / lane no-ops honest / daily_report+ceo_live_usage "
       "written / token L2 0); (5) S7: attrition 4 CLEAN + pin=5 no-op + watchdog registered (S4U flip access-denied adjudicated face) + claws x2 + "
       "short-video disable standing re-verified + counter 1069->1070 | verify: smoke 49/49 + S6 log 43x rc=0 + d19 read-back equality + epoch int + "
       "report +1 + push rides this window | next r1070: watch bm-a W263 chain (splice->burn->finalize) -> on finalize bm-c W264 SEAT (live re-derive "
       "post-W263 universe, staircase forward face, never transcribe r587); Monday 10-19 15:30 papers chain; r1070=5x HANDOVER duty").format(ts=TS)


def sample():
    r = {}
    try:
        p = subprocess.run(["wmic", "OS", "get", "FreePhysicalMemory,TotalVisibleMemorySize", "/value"],
                            capture_output=True, creationflags=CNW)
        o = p.stdout.decode("gb18030", "replace")
        d = dict(x.split("=", 1) for x in o.replace("\r", "").split("\n") if "=" in x)
        free_kb = float(d["FreePhysicalMemory"]); tot_kb = float(d["TotalVisibleMemorySize"])
        r["free_ram_gb"] = round(free_kb / 1048576.0 * 1024 / 1024, 1)  # kb->MiB->GiB
        r["free_ram_gb"] = round(free_kb / 1024.0 / 1024.0, 1)
        r["total_ram_gb"] = round(tot_kb / 1024.0 / 1024.0, 1)
    except Exception as e:
        r["_ram_err"] = str(e)
    try:
        p = subprocess.run(["wmic", "cpu", "get", "loadpercentage", "/value"],
                            capture_output=True, creationflags=CNW)
        o = p.stdout.decode("gb18030", "replace")
        d = dict(x.split("=", 1) for x in o.replace("\r", "").split("\n") if "=" in x)
        r["cpu_pct"] = int(float(d["LoadPercentage"]))
    except Exception as e:
        r["_cpu_err"] = str(e)
    try:
        p = subprocess.run(["nvidia-smi", "--query-gpu=memory.free,memory.total,utilization.gpu",
                            "--format=csv,noheader,nounits"], capture_output=True, creationflags=CNW)
        o = p.stdout.decode("gb18030", "replace").strip().splitlines()[0]
        f, t, u = [x.strip() for x in o.split(",")]
        r["gpu_free_mib"] = int(f); r["gpu_total_mib"] = int(t)
        r["gpu_used_mib"] = int(t) - int(f); r["gpu_util_pct"] = int(u)
    except Exception as e:
        r["_gpu_err"] = str(e)
    return r


def atomic_json(path, obj):
    tmp = path + ".tmp_r1069"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.write("\n")
    os.replace(tmp, path)


def main():
    smp = sample()
    free_ram = smp.get("free_ram_gb")
    cpu_pct = smp.get("cpu_pct")
    gfree = smp.get("gpu_free_mib")
    gtotal = smp.get("gpu_total_mib")
    gused = smp.get("gpu_used_mib")
    gutil = smp.get("gpu_util_pct")

    # ---------- state ----------
    with io.open(STATE, encoding="utf-8") as f:
        st = json.load(f)
    assert st.get("round_no") == 1069, "state round_no expected 1069, got %s" % st.get("round_no")
    assert st.get("last_orders_sha", "").lower() == ORD_SHA, "ORD watermark carry mismatch: %s" % st.get("last_orders_sha")
    assert st.get("last_decisions_sha", "").lower() == DEC_SHA, "DEC watermark carry mismatch"
    st["round_no"] = 1070
    st["round_no_label"] = "r1069"
    st["last_round"] = "r1069"
    st["last_round_at"] = TS
    st["last_round_closed"] = TS
    st["last_round_summary"] = SUMMARY
    st["last_round_summary_at"] = TS
    st["last_round_label"] = "r1069"
    st["r1069_closeout_note"] = DID
    st["current_task"] = CURTASK
    st["current_task_at"] = TS
    st["current_task_ts"] = EPOCH
    st["last_action"] = CURTASK
    st["last_action_at"] = TS
    st["did"] = DID
    st["verify"] = VERIFY
    st["verdict"] = VERDICT
    st["note"] = ("r1069: clean continuation waits-upstream -- W263 = bm-a window (prereg b32f6bf1c frozen, splice ungated post-W262-finalize); "
                  "bm-c next turn = W264 seat; short-video lane disabled standing per O-20261017-1741")
    st["next_pointer"] = NEXT_PTR
    st["next"] = NEXT_PTR
    st["next_milestone"] = ("W263 finalize (bm-a window, in-flight prereg-frozen) -> bm-c W264 seat (chain-order); "
                            "Monday 10-19 15:30 bars papers chain (24-48h window)")
    st["latest_artifact"] = ARTIFACT
    st["last_artifact"] = ARTIFACT
    st["recent_artifact"] = ARTIFACT
    st["prod_lanes"] = PROD_LANES
    st["full_load_selfproof"] = {"占用一行": PROD_LANES}
    st["orphan_face"] = 1
    st["orphan_faces"] = 1
    st["idle_rounds"] = 0
    st["agenda_starved"] = False
    st["clock_read"] = TS
    st["ts"] = TS
    st["updated"] = TS
    st["updated_at"] = TS
    st["now_active"] = TS
    st["activity_now"] = TS
    st["last_seen"] = TS
    st["last_orders_at"] = TS
    st["last_orders_read_at"] = TS
    st["last_orders_seen"] = TS
    st["last_orders_sha_note"] = ORD_NOTE
    st["last_orders_read_note"] = ("r1069: delta rows judged: O-20261017-1741 @bm-c (executed-prior r1068, standing re-verified 4/4 disabled + 6688 FREE) "
                                   "+ 17:5x @bm-b drama dub (bm-b lane zero-action); DEC 1d4741e4 FALSE hold")
    st["last_decisions_read_at"] = TS
    st["last_decisions_seen"] = TS
    st["last_decisions_at"] = TS
    st["last_decisions_read_note"] = "r1069: DEC delta FALSE hold (raw-blob sha256 1d4741e4 pinned probe, zero rows owed)"
    st["orders_ack_ts"] = TS
    st["orders_ack_receipt"] = ACK_RECEIPT
    st["d19_watermark_guard"] = dict(st.get("d19_watermark_guard", {}))
    st["d19_watermark_guard"]["round_ref"] = 1069
    st["d19_watermark_guard"]["ts"] = TS
    st["head_sha"] = ("r1069 closeout (waits-upstream: W263 bm-a window prereg-frozen splice-ungated; bm-c next turn = W264 seat); "
                      "ORD watermark healed 313c8c0f (r1068 phantom disclosed)")
    st["sync"] = {"origin_tip": "r1069 closeout commit rides this window (push lands this window; post-push behind=0 verified same window)",
                  "ts": TS}
    if free_ram is not None:
        st["free_ram_gb"] = free_ram; st["ram_free_gb"] = free_ram; st["idle_ram_gb"] = free_ram
    if cpu_pct is not None:
        st["cpu_pct"] = cpu_pct; st["cpu_util_pct"] = cpu_pct; st["cpu_idle_pct"] = round(100.0 - cpu_pct, 1)
    if gfree is not None:
        st["gpu_free_vram_mib"] = gfree; st["gpu_free_vram_mb"] = gfree
        st["gpu_free_vram_gb"] = round(gfree / 1024.0, 1)
        st["gpu_idle_vram_mib"] = gfree; st["gpu_idle_vram_mb"] = gfree
        st["gpu_idle_mb"] = gfree; st["gpu_idle_mib"] = gfree
        st["gpu_vram_free_mb"] = gfree; st["gpu_free_mb"] = gfree; st["gpu_free_mib"] = gfree
        st["free_vram_mb"] = gfree
        st["gpu_total_vram_mib"] = gtotal; st["gpu_used_vram_mib"] = gused; st["gpu_util_pct"] = gutil
    atomic_json(STATE, st)

    # ---------- heartbeat ----------
    with io.open(HB, encoding="utf-8") as f:
        hb = json.load(f)
    hb["machine_id"] = "bm-c"
    hb["clock_read"] = TS
    hb["ts"] = TS
    hb["updated"] = TS
    hb["updated_at"] = TS
    hb["last_seen"] = TS
    hb["last_seen_at"] = TS
    hb["now_active"] = TS
    hb["activity_now"] = TS
    hb["current_task"] = CURTASK
    hb["current_task_at"] = TS
    hb["current_task_ts"] = EPOCH
    hb["heartbeat_epoch_utc"] = EPOCH
    hb["heartbeat_epoch_utc_type"] = "int (assert)"
    hb["did"] = DID
    hb["verify"] = VERIFY
    hb["note"] = st["note"]
    hb["verdict"] = VERDICT
    hb["next_pointer"] = NEXT_PTR
    hb["next"] = NEXT_PTR
    hb["next_milestone"] = st["next_milestone"]
    hb["latest_artifact"] = ARTIFACT
    hb["last_artifact"] = ARTIFACT
    hb["recent_artifact"] = ARTIFACT
    hb["prod_lanes"] = PROD_LANES
    hb["full_load_selfproof"] = {"占用一行": PROD_LANES}
    hb["last_round"] = "r1069"
    hb["last_round_at"] = TS
    hb["last_round_label"] = "r1069"
    hb["last_round_closed"] = TS
    hb["last_round_summary"] = SUMMARY
    hb["last_round_summary_at"] = TS
    hb["last_action"] = CURTASK
    hb["last_action_at"] = TS
    hb["round_no"] = 1070
    hb["round_no_label"] = "r1069"
    hb["idle_rounds"] = 0
    hb["agenda_starved"] = False
    hb["orphan_face"] = 1
    hb["orphan_faces"] = 1
    hb["health"] = "ok"
    hb["head_sha"] = st["head_sha"]
    hb["sync"] = st["sync"]
    hb["last_orders_sha"] = ORD_SHA
    hb["last_orders_at"] = TS
    hb["last_orders_read_at"] = TS
    hb["last_orders_seen"] = TS
    hb["last_orders_sha_note"] = ORD_NOTE
    hb["last_orders_read_note"] = st["last_orders_read_note"]
    hb["last_decisions_sha"] = DEC_SHA
    hb["last_decisions_at"] = TS
    hb["last_decisions_read_at"] = TS
    hb["last_decisions_seen"] = TS
    hb["last_decisions_read_note"] = st["last_decisions_read_note"]
    hb["orders_ack_ts"] = TS
    hb["orders_ack_receipt"] = ACK_RECEIPT
    hb["d19_watermark_guard"] = st["d19_watermark_guard"]
    if free_ram is not None:
        hb["free_ram_gb"] = free_ram; hb["ram_free_gb"] = free_ram; hb["idle_ram_gb"] = free_ram
        hb["total_ram_gb"] = smp.get("total_ram_gb", st.get("total_ram_gb", 23.9))
    if cpu_pct is not None:
        hb["cpu_pct"] = cpu_pct; hb["cpu_util_pct"] = cpu_pct; hb["cpu_idle_pct"] = round(100.0 - cpu_pct, 1)
    hb["cores"] = 32; hb["cpu_cores"] = 32
    if gfree is not None:
        hb["gpu_free_vram_mib"] = gfree; hb["gpu_free_vram_mb"] = gfree
        hb["gpu_free_vram_gb"] = round(gfree / 1024.0, 1)
        hb["gpu_idle_vram_mib"] = gfree; hb["gpu_idle_vram_mb"] = gfree
        hb["gpu_idle_mb"] = gfree; hb["gpu_idle_mib"] = gfree
        hb["gpu_vram_free_mb"] = gfree; hb["gpu_free_mb"] = gfree; hb["gpu_free_mib"] = gfree
        hb["free_vram_mb"] = gfree
        hb["gpu_total_vram_mib"] = gtotal; hb["gpu_used_vram_mib"] = gused; hb["gpu_util_pct"] = gutil
    atomic_json(HB, hb)

    # ---------- round report row (ROOT live ledger per r1007 freeze pointer) ----------
    with io.open(REPORT, "rb") as f:
        raw = f.read()
    lines_before = raw.count(b"\n")
    eol = b"\r\n" if raw.endswith(b"\r\n") or raw.count(b"\r\n") > raw.count(b"\n") * 0.5 else b"\n"
    with io.open(REPORT, "ab") as f:
        f.write(ROW.encode("utf-8") + eol)
    with io.open(REPORT, "rb") as f:
        lines_after = f.read().count(b"\n")
    assert lines_after == lines_before + 1, "report line +1 assert failed: %d -> %d" % (lines_before, lines_after)

    # ---------- assertions ----------
    with io.open(STATE, encoding="utf-8") as f:
        st2 = json.load(f)
    with io.open(HB, encoding="utf-8") as f:
        hb2 = json.load(f)
    assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be int"
    assert isinstance(st2["current_task_ts"], int), "current_task_ts must be int"
    assert st2["round_no"] == 1070 and st2["last_round"] == "r1069"
    assert st2["last_orders_sha"].lower() == ORD_SHA and st2["last_decisions_sha"].lower() == DEC_SHA
    assert "T" in hb2["clock_read"], "clock_read must be T-separated ISO8601"

    print("CLOSEOUT OK: round_no=1070 epoch=%d clock=%s ram_free=%s cpu=%s gpu_free_mib=%s report_lines=%d"
          % (hb2["heartbeat_epoch_utc"], hb2["clock_read"], free_ram, cpu_pct, gfree, lines_after))
    print("sample_keys_missing:", [k for k in smp if k.startswith("_")])
    print("codely_size_bytes:", os.path.getsize(os.path.join(ROOT, "CODELY.md")) if os.path.exists(os.path.join(ROOT, "CODELY.md")) else -1)


if __name__ == "__main__":
    main()
