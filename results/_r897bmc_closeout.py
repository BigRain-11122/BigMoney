# -*- coding: utf-8 -*-
# r897 bm-c closeout: absorb dead r896 (post-commit/push/report, pre-closeout)
# per bm-b r898 / r894 absorb precedent. Counter 896->898 (double advance).
import json, time, datetime, subprocess, io, os

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
STATE = os.path.join(ROOT, "state-bm-c.json")
HEART = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
REPORT = os.path.join(ROOT, "round_reports-bm-c.md")

now = datetime.datetime.now().astimezone()
now_iso = now.isoformat(timespec="seconds")  # T-separated with offset
epoch = int(time.time())

def rd(p):
    return json.load(io.open(p, "r", encoding="utf-8"))

def wr(p, d):
    with io.open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
        f.write("\n")

# ---- fresh machine stats ----
ram_free_gb = None; cpu_pct = None; total_ram_gb = None
try:
    import psutil
    vm = psutil.virtual_memory()
    total_ram_gb = round(vm.total / 1024**3, 1)
    ram_free_gb = round(vm.available / 1024**3, 2)
    cpu_pct = round(psutil.cpu_percent(interval=1.0), 1)
except Exception:
    pass
gpu_free_mb = None
try:
    out = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                         capture_output=True, timeout=20).stdout.decode().strip().splitlines()
    gpu_free_mb = int(out[0])
except Exception:
    pass

NEXT = ("r898: (1) MV XQ-24 completion harvest watch (5/25 landed, XQ08 burning, interactive window owns; "
        "XQ02 re-burn pending wardrobe redo; harvest + receipt into O-2126 when lane completes); "
        "(2) unity-mcp POC execution post-lane (queued by r896 recon, receipt <=10-13 12:00 via fleet/inbox); "
        "(3) W210 (bm-b) finalize -> M11/cron auto W211 freeze -> n1_w211 burn; "
        "(4) Monday 15:30 first new-bar window: update_daily + live.paper + t35_open_fill_verify + t24 legs")

DID = ("r897 bm-c: (1) S0-1 anchor bm-c + round-zero probe py_faces=7 orphans=1 zero-kill (MV-lane infra kept); "
       "(2) S0 fetch 0/0 clean no rebase; (3) ABSORB: prior invocation ran full round as r896 "
       "(committed+pushed e13bb3ee9 + report 23:49:30 + O-2333 unity-mcp POC recon acked) then died pre-closeout "
       "(state still 896, heartbeat partial) -> this session = r897 per bm-b r898/r894 absorb precedent, "
       "counter 896->898 double-advance so next session = r898; r896 S6 38/38 chain absorbed as this round S6 evidence "
       "(no re-run: idempotent + 10-12 date rollover protects daily faces); (4) S0.5 fleet orders unacked=0; "
       "ORD group delta TRUE x2 -> consumed 3 new rows ALL BigStream faces zero BigMoney repo action "
       "(23:1x harvest-landing order + 23:5x colorist-seat law + 10-12 00:0x wardrobe-seat law), "
       "watermark advanced 0513e9e7->5de45af4 (S0.5 leg) then ->6d1ee551 (S7 close double-scan caught 00:0x row); "
       "0513e9e7 verified real via git blob history scan (content @ 54688f643e 23:01:33, corrupt-face recurrence guard PASS); "
       "DEC unchanged eb14c441 zero action; (5) S1 smoke 49/49; boards clear (jobs 0, fleet open 0, P2 empty, "
       "P3 head E17 bm-b yielded, backlog row12 BigHouse=bm-b agenda); satengine alive rc0 (heartbeat age 7.8s, "
       "queue/burns empty, W211 armed behind W210 bm-b structural wait, freeze edits ready + cron 847675d7 alive); "
       "watermark red=false; idle NOT green-idle (RAM gate + vram disclosure-only); (6) S6 absorbed 38/38 rc0 "
       "(dualrun ZERO-DRIFT streak 11, update_daily Sunday no-op cutoff 10-09, market_clock ORANGE_COOL sleeves=4, "
       "REPORT/LIVE-2026-10-11 re-derived, 7 disclosed skips); post_review REPORT-20261012 backfill landed 00:00:20 "
       "45gr/0X/5yellow = zero P0 debt; (7) MV watch: KF v2.3 BICYCLE reshake 6/6 frames landed (XQ02 wardrobe-law redo 00:01:52), "
       "clips-local-768 5/25 mp4 (V2_KFL+XQ28+XQ02+XQ05+XQ07), burn client alive in-flight XQ08, zero fails; "
       "(8) S7: idle --worked + attrition guard 4 CLEAN + loop pin=5 no-op (next fire 00:15) + watchdog re-registered (00:07) "
       "+ precommit/prepush claws re-installed + S7 close double-scan consumed 00:0x row")

VERDICT = ("green: absorb-closeout round -- dead r896 absorbed (its commit e13bb3ee9 + report already delivered), "
           "ORD watermark double-advanced 0513e9e7->6d1ee551 (3 new rows all BigStream-only, zero BigMoney action), "
           "S6 38/38 rc0 absorbed, post_review 20261012 zero-X, boards clear, orphans=1 MV-lane infra kept, "
           "GPU/RAM yielded to MV CEO-priority i2v burn (XQ08 in flight), W211 structural wait on W210 (bm-b)")

NOW_ACTIVE = ("r897: MV album i2v fresh-frames burn ACTIVE (5/25 clips, XQ08 in flight, interactive window owns) + "
              "unity-mcp POC queued post-lane (receipt <=10-13); W211 armed behind W210 (bm-b); BigMoney watch face")

ARTIFACT = ("results/post_review/REPORT-20261012.md (45 pass/0 fail/5 watch, 2026-10-12 00:00:20) + "
            "docs/daily_report/REPORT-2026-10-11.md + docs/live_usage/LIVE-2026-10-11.md (S6 re-derived)")

ABSORB_NOTE = ("r897 absorb: prior invocation executed a FULL round as r896 (probe/smoke/S6 38-38/O-2333 POC recon/"
               "report 23:49:30/commit e13bb3ee9 pushed) then died pre-closeout (state round_no still 896, last_round "
               "still 895, heartbeat partial: epoch+ack updated but round fields not) -- this session absorbed per "
               "bm-b r898 / bm-c r894 absorb precedent; executed as r897, counter advanced 896->898 so next session = r898; "
               "zero double-count: r896's ORD probe ran pre-23:37-commit so its 3 late rows fell to this session (consumed + advanced twice)")

CUR_TASK = "r897 closeout: absorb dead r896 + ORD 3-row double-advance + S7 quad self-heal + MV XQ harvest watch"

# ---- state file ----
st = rd(STATE)
st["round_no"] = 898
st["round_no_label"] = "r897"
st["loop_round"] = 897
st["last_round"] = 897
for k in ("last_round_at", "last_round_closed", "last_round_ts", "clock_read", "ts", "updated", "updated_at",
          "last_seen", "last_seen_at", "current_task_at", "last_action_at", "last_orders_at",
          "last_orders_read_at", "last_decisions_read_at", "last_decisions_at", "last_round_summary_at"):
    st[k] = now_iso
st["current_task"] = CUR_TASK
st["did"] = DID
st["note"] = DID
st["verdict"] = VERDICT
st["last_round_summary"] = DID
st["last_action"] = "r897 absorb closeout (dead r896 absorb + ORD double-advance 0513e9e7->6d1ee551 + quad self-heal)"
st["next"] = NEXT
st["next_pointer"] = NEXT
st["next_milestone"] = NEXT
st["now_active"] = NOW_ACTIVE
st["activity_now"] = NOW_ACTIVE
st["latest_artifact"] = ARTIFACT
st["last_artifact"] = ARTIFACT
st["recent_artifact"] = ARTIFACT
st["last_orders_sha_note"] = ("r897 double-advanced: 0513e9e7->5de45af4 (S0.5, 2 rows) then ->6d1ee551 (S7 close "
                              "double-scan, 00:0x wardrobe row) via d19_watermark update --advance legal path, "
                              "facts-driven from _s05_probe.bm-c.json, read-back full-string equality OK both legs; "
                              "all 3 new rows BigStream-only, zero BigMoney repo action; 0513e9e7 provenance verified "
                              "vs git blob history (54688f643e) before consuming")
st["orphan_face"] = 1
st["orphan_faces"] = 1
st["idle_rounds"] = 0
st["agenda_starved"] = False
st["r897_absorb_note"] = ABSORB_NOTE
if total_ram_gb: st["total_ram_gb"] = total_ram_gb
if ram_free_gb is not None:
    st["free_ram_gb"] = ram_free_gb; st["idle_ram_gb"] = ram_free_gb; st["ram_free_gb"] = ram_free_gb
if cpu_pct is not None:
    st["cpu_pct"] = cpu_pct; st["cpu_util_pct"] = cpu_pct; st["cpu_idle_pct"] = round(100 - cpu_pct, 1)
if gpu_free_mb is not None:
    st["gpu_free_vram_mb"] = gpu_free_mb; st["gpu_free_vram_mib"] = gpu_free_mb
    st["gpu_free_mb"] = gpu_free_mb; st["gpu_free_mib"] = gpu_free_mb
    st["gpu_free_vram_gb"] = round(gpu_free_mb / 1024, 2)
st["verify"] = ("receipts: smoke 49/49 + S6 38/38 rc0 (_r896bmc_s6_log.txt absorbed) + dualrun streak 11 + "
                "attrition 4 CLEAN + ORD double-advance read-back OK x2 + post_review 20261012 zero-X + push self-proof below")
st["head_sha"] = "e13bb3ee9"
st["last_pulled_at"] = now_iso
st["sync"] = {"ahead_behind": "r897 closeout commit rides this push", "origin_tip": "pending",
              "ts": now_iso, "note": "r897 absorb closeout commit+push this round; rev-list self-proof logged in round report"}
st["last_round_closed"] = now_iso
st["d19_watermark_guard"] = {"tool": "scripts/d19_watermark.py", "probe": "results/_r686bmb_d19_check.py",
                             "probe_evidence": "K:\\Fluxgroup\\FluxGroup\\quant\\bigmoney\\results\\_r686bmb_d19_check.json",
                             "method_decisions": "sha256", "method_orders": "sha1", "verbatim": True,
                             "advance": True, "round_ref": 897, "ts": now_iso}
wr(STATE, st)
print("state written: round_no=898 last_round=897 label=r897")

# ---- heartbeat ----
hb = rd(HEART)
hb["round_no"] = 898
hb["round_no_label"] = "r897"
hb["last_round"] = 897
hb["last_round_at"] = now_iso
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = now_iso
hb["ts"] = now_iso
hb["last_seen"] = now_iso
hb["last_seen_at"] = now_iso
hb["updated"] = now_iso
hb["updated_at"] = now_iso
hb["current_task"] = CUR_TASK
hb["current_task_ts"] = now_iso
hb["did"] = DID
hb["last_round_summary"] = DID
hb["last_round_summary_at"] = now_iso
hb["verdict"] = VERDICT
hb["next"] = NEXT
hb["next_pointer"] = NEXT
hb["next_milestone"] = NEXT
hb["now_active"] = NOW_ACTIVE
hb["activity_now"] = NOW_ACTIVE
hb["latest_artifact"] = ARTIFACT
hb["last_artifact"] = ARTIFACT
hb["recent_artifact"] = ARTIFACT
hb["last_action"] = "r897 absorb closeout (dead r896 absorb + ORD double-advance + quad self-heal)"
hb["last_action_at"] = now_iso
hb["prod_lanes"] = ("GPU=MV album i2v fresh-frames burn ACTIVE (XQ08 in flight, interactive window owns); "
                    "CPU=W211 armed behind W210 (bm-b) structural wait + RAM gate on heavy batches")
hb["last_round_closed"] = now_iso
hb["loop_round"] = 897
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["health"] = "ok"
hb["orphan_face"] = "orphans=1 (MV-lane infra KEPT: burn client + ComfyUI :8188, zero-kill per MV-lane domain)"
hb["orphan_faces"] = 1
hb["last_orders_sha"] = "6d1ee551800e259644a8085f0e8368c6fa4d10cb"
hb["last_orders_at"] = now_iso
hb["last_orders_sha_note"] = ("r897 double-advanced 0513e9e7->5de45af4->6d1ee551 (3 BigStream-only rows, "
                              "zero BigMoney action; 0513e9e7 provenance verified vs git blob history before consuming)")
hb["verify"] = ("receipts: smoke 49/49 + S6 38/38 rc0 (absorbed) + attrition 4 CLEAN + ORD double-advance "
                "read-back OK + post_review 20261012 zero-X + push self-proof below")
hb["last_round_ts"] = now_iso
if total_ram_gb: hb["total_ram_gb"] = total_ram_gb
if ram_free_gb is not None:
    hb["free_ram_gb"] = ram_free_gb; hb["idle_ram_gb"] = ram_free_gb; hb["ram_free_gb"] = ram_free_gb
if cpu_pct is not None:
    hb["cpu_pct"] = cpu_pct; hb["cpu_util_pct"] = cpu_pct; hb["cpu_idle_pct"] = round(100 - cpu_pct, 1)
if gpu_free_mb is not None:
    hb["gpu_free_vram_mb"] = gpu_free_mb; hb["gpu_free_vram_mib"] = gpu_free_mb
    hb["gpu_free_mb"] = gpu_free_mb; hb["gpu_free_mib"] = gpu_free_mb
    hb["gpu_free_vram_gb"] = round(gpu_free_mb / 1024, 2)
wr(HEART, hb)

# epoch int self-proof (R170/R178 law)
hb2 = rd(HEART)
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in hb2["clock_read"], "clock_read must be T-separated"
print("heartbeat written: epoch=%d (int OK) clock=%s" % (hb2["heartbeat_epoch_utc"], hb2["clock_read"]))

# ---- round report append ----
line = "%s | r897 | bm-c | %s | evidence: smoke 49/49 + S6 38/38 rc0 (_r896bmc_s6_log.txt absorbed) + dualrun streak 11 + attrition 4 CLEAN + ORD double-advance 0513e9e7->5de45af4->6d1ee551 read-back OK x2 (3 rows BigStream-only) + 0513e9e7 blob-history verify PASS (54688f643e) + post_review 20261012 zero-X backfill + MV clips 5/25 reshake 6/6 light-read + push range self-proof below | next: %s | [r897 bm-c]\n" % (now_iso, DID, NEXT)
with io.open(REPORT, "a", encoding="utf-8", newline="\n") as f:
    f.write(line)
print("round report r897 appended")
print("STATS: ram_free=%.2fGB cpu=%.1f%% gpu_free=%sMB" % (ram_free_gb or -1, cpu_pct or -1, gpu_free_mb))
