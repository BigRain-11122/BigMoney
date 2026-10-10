# -*- coding: utf-8 -*-
# r852 bm-c close books: state bump 852->853 + heartbeat + round report line
import json
import time
import datetime

NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())

activity = (
    "当前活: 守望窗（W209 freeze 待上游 W208 落链·M10 行+cron 9defca39 durable 在位·jman trainer 21288 在烧 CPU 32.0h ETA ~09:45-10:00）"
    "| 最近实物: pool-EOL 跨机裁定收口（perpetual_faces.py leg8 EOL 守卫迁 probe-vs-bytes·池字节面零触碰·双面机证 PASS）+ S6 43 腿 rc0 streak 28 + QA 证据包 r852 5/5 @ "
    + NOW
    + " | 下个里程碑: W209 freeze（W208 落链即 M10 自动执行）+ jman 完训验证三件 ~09:45-10:00（≤48h SLA）+ bm-b 复跑 pf selftest EOL 裁定绿回执"
)

did = (
    "r852 bm-c: (1) S0-1 anchor bm-c + round-zero probe py_faces=14 orphans=1 read-only (idle ComfyUI face same as r850/r851, no-kill); "
    "S0 HEAD==origin tip (efb3c2961) zero new commits -> W208 NOT landed one-line declaration (anti-rescan law); dirty face = own runtime 7 faces targeted absorb; "
    "(2) S0.5 probe ORD f90233c7 / DEC 68d13893 both zero-delta (unacked 0); "
    "(3) S1 smoke 49/49; S2 boards empty (job 0 / open tickets 0), queues drained state maintained from r851 honest re-verification; "
    "(4) PRIMARY PRODUCT = pool-EOL FLEET ADJUDICATION rendered and closed: bm-b r856 flag (pf selftest leg8 hardcoded CRLF assert red on byte-faithful LF checkout) "
    "adjudicated per pit-pool-edit r500 law (format face follows the writer) + r499 trailing / r307 indent migration family = Option A probe-vs-bytes guard "
    "(Option B producer-realignment rejected: whole-pool EOL rewrite hits the integral-rewrite prohibition); surgical fix scripts/perpetual_faces.py leg8 "
    "(crlf==crlf_bytes consistency assert), POOL BYTE-FACE UNTOUCHED; verified selftest 9/9 PASS (bm-c CRLF face) + dual-face probe "
    "(origin LF blob = bm-b byte-faithful view PASS + old hardcode would-red-on-LF confirmed = root cause closed); adjudication MSG published to fleet inbox "
    "(bm-b re-run confirm request + bm-a FYI); new pit law direct-written research/pit-pool-edit.md (autocrlf checkout-conversion false-green trap, +1023B, "
    "r747/r666 direct-write precedent, main file headroom 210B insufficient); "
    "(5) S6 43/43 rc0 (_r852bmc_s6_chain.ps1 r851 verbatim clone, DONE 04:52:08, dualrun streak 27->28; three flags all known-adjudicated faces: "
    "gpu_unauthorized=jman CEO-MV-order burn GPU100%, pool_starvation/supply_floor=seat chain W209/W211 awaiting M9 gate); QA charter pack 5/5 "
    "(qa/smoke-r852-bm-c.md + equity-curve-r852-bm-c.png); "
    "(6) jman 21288 alive CPU 32.0h (r851 29.9h) ETA ~09:45-10:00 unchanged; W209 waiting-upstream W208 (M10 cron 9defca39 durable verified via cron_list); "
    "W211 freeze-prep not due (W210 not approaching); "
    "(7) inbox 1 consumed (MSG-20261011-0412 bm-b N2-W18 draft declaration, lane CLEAR vs ours, moved to processed); S7 attrition 4 ledgers CLEAN; "
    "quartet green (loop pin=5 no-op first-fire 05:05, watchdog re-registered first-fire 04:57, dual claws LF-normalized installed); idle --worked "
    "(idle_rounds=0, NOT green-idle: VRAM 94MiB jman in-flight -> no backlog-claim obligation)"
)

verify = (
    "receipts: smoke 49/49 + results/_r852bmc_pool_eol_migration.json (dual-face machine proof) + results/_r852bmc_s6_log.txt (43/43 rc0 streak 28) "
    "+ qa/smoke-r852-bm-c.md (5/5 charter) + pit-pool-edit.md r852 law row (+1023B line 35) + MSG-20261011-0455-bmc-pooleol-adjudication.md "
    "+ attrition CLEAN (4 ledgers) + quartet green + idle --worked"
)

note = (
    "r852 = pool-EOL cross-machine adjudication close round: guard migrated to probe-vs-bytes (r499/r307 family completed on EOL face), "
    "pool byte-face untouched, dual-face proof PASS; S6 43/43 streak 28; QA pack 5/5; W208 still not landed (M10 armed); jman ETA ~09:45 unchanged."
)

next_ptr = (
    "r853: (1) W208 landing watch -> M10 auto-execute chain (freeze -> selftest default-wave -> pathspec push -> 2-cycle n1_w209 ignition -> MSG receipt + flip M10 + delete cron 9defca39); "
    "(2) bm-b pf selftest re-run confirm (pool-EOL adjudication green receipt face); "
    "(3) jman completion window ~09:45-10:00 (val_grid + LOOKBOARD_variant_640 + recovery-debt trio per O-20261010-0025, <=48h SLA); "
    "(4) W211 freeze-prep (read pit-engine-finalize.md FIRST; re-pull + re-verify universe face when W210 freeze approaches); "
    "(5) S0.5 standing composer; (6) 10-16 governance criteria on file"
)

# --- state-bm-c.json (LF, indent=1, trailing NL, roundtrip-identical) ---
sb = open("state-bm-c.json", "rb").read()
st = json.loads(sb.decode("utf-8"))
st["round_no"] = 853
st["loop_round"] = 852
st["last_round"] = 852
for k in ("clock_read", "current_task_at", "last_round_at", "last_seen", "last_seen_at",
          "last_ts", "last_run_at", "last_round_closed", "last_round_at_legacy",
          "last_action_at", "last_round_summary_at", "last_orders_read_at", "ts",
          "updated", "updated_at", "current_task_ts", "last_orders_at", "last_pulled_at"):
    if k in st:
        st[k] = NOW
st["last_round_ts"] = NOW
st["heartbeat_epoch_utc"] = EPOCH
st["cpu_pct"] = 26
st["cpu_idle_pct"] = 74
st["cpu_util_pct"] = 26
st["free_ram_gb"] = 0.5
st["ram_free_gb"] = 0.5
st["idle_ram_gb"] = 0.5
for k in ("gpu_free_vram_mib", "gpu_free_vram_mb", "gpu_free_mib", "gpu_idle_vram_mb",
          "gpu_idle_vram_mib", "gpu_idle_mib", "gpu_vram_free_mb"):
    if k in st:
        st[k] = 94
st["gpu_idle_mb"] = 16291
st["current_task"] = activity
st["activity_now"] = activity
st["did"] = did
st["note"] = note
st["verify"] = verify
st["verdict"] = ("r852 close: pool-EOL cross-machine adjudication rendered+closed (guard probe-vs-bytes migration, "
                 "pool byte-face untouched, dual-face proof PASS, MSG broadcast) + S6 43/43 rc0 (streak 28) + QA pack 5/5 "
                 "+ smoke 49/49 + M10 armed waiting W208 + jman alive (CPU 32.0h, ETA ~09:45)")
st["last_round_summary"] = ("r852 close: pool-EOL adjudication closed (probe-vs-bytes migration + dual-face proof) + S6 43/43 streak 28 "
                            "+ QA 5/5 + M10 armed + jman ETA ~09:45")
st["last_action"] = "r852 pool-EOL adjudication + EOL guard migration + S6 43-leg chain (streak 28) + QA pack + books"
st["next_pointer"] = next_ptr
st["next"] = next_ptr
st["next_milestone"] = ("r853: W209 freeze on W208 landing (M10 auto-execute, cron armed) + jman completion window ~09:45-10:00 "
                        "(val_grid + LOOKBOARD_variant_640 + recovery-debt trio) <=48h + bm-b EOL re-run confirm")
st["latest_artifact"] = "DELIVERED perpetual_faces.py leg8 EOL guard migration (probe-vs-bytes, pool byte-face untouched) + dual-face proof _r852bmc_pool_eol_migration.json"
st["last_artifact"] = st["latest_artifact"]
st["recent_artifact"] = st["latest_artifact"]
st["orphan_face"] = 1
st["orphan_faces"] = 1
st["idle_rounds"] = 0
st["agenda_starved"] = False
st["round_no_label"] = "r852"
st["health"] = "ok"
out = json.dumps(st, ensure_ascii=False, indent=1) + "\n"
open("state-bm-c.json", "wb").write(out.encode("utf-8"))
chk = json.loads(open("state-bm-c.json", "rb").read().decode("utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int) and chk["round_no"] == 853

# --- fleet/machines/bm-c.json (CRLF, indent=1, no trailing NL) ---
hb = open("fleet/machines/bm-c.json", "rb").read()
h = json.loads(hb.decode("utf-8"))
h["last_seen"] = NOW
h["ts"] = NOW
for k in list(h):
    if k.endswith("_at") and isinstance(h[k], str) and "2026-10-11T04:38" in h[k]:
        h[k] = NOW
h["heartbeat_epoch_utc"] = EPOCH
h["clock_read"] = NOW
h["cpu_pct"] = 26
h["cpu_cores"] = 32
h["free_ram_gb"] = 0.5
h["idle_ram_gb"] = 0.5
h["ram_free_gb"] = 0.5
for k in list(h):
    if "gpu_free" in k or ("gpu_idle" in k and "mb" not in k.replace("mib", "")):
        if isinstance(h[k], int):
            h[k] = 94
h["gpu_idle_mb"] = 16291
h["current_task"] = activity
h["verdict"] = ("r852 close: pool-EOL adjudication closed (probe-vs-bytes guard migration, dual-face proof PASS, MSG broadcast) "
                "+ S6 43/43 rc0 streak 28 + QA 5/5 + W208-watch (M10 armed) + jman alive ETA ~09:45")
h["idle_rounds"] = 0
h["agenda_starved"] = False
h["last_round"] = 852
h["last_round_at"] = NOW
hout = json.dumps(h, ensure_ascii=False, indent=1).replace("\n", "\r\n")
open("fleet/machines/bm-c.json", "wb").write(hout.encode("utf-8"))
chk2 = json.loads(open("fleet/machines/bm-c.json", "rb").read().decode("utf-8"))
assert isinstance(chk2["heartbeat_epoch_utc"], int)
assert "T" in chk2["clock_read"] and "+08:00" in chk2["clock_read"]

print("state round_no -> 853, heartbeat epoch int OK, ts=" + NOW)
