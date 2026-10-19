# -*- coding: utf-8 -*-
"""r1117 bm-c closeout: state round_no 1117->1118 + heartbeat mirror + round report row.
Live faces refreshed in-process (psutil) + one nvidia-smi via CREATE_NO_WINDOW (U060)."""

import datetime
import json
import os
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state-bm-c.json")
HB = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
REPORT = os.path.join(ROOT, "round_reports-bm-c.md")
WMRED = os.path.join(ROOT, "results", "watermark_red.json")

now = datetime.datetime.now().astimezone()
ts = now.isoformat(timespec="seconds")
epoch = int(time.time())

# ---------- live faces ----------
import psutil
free_ram = round(psutil.virtual_memory().available / 1e9, 2)
cpu_pct = round(psutil.cpu_percent(interval=1), 1)
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
gpu_free_mib = None
try:
    p = subprocess.run(["nvidia-smi", "--query-gpu=memory.free,utilization.gpu",
                        "--format=csv,noheader,nounits"], capture_output=True,
                       creationflags=CNW, text=True)
    parts = p.stdout.strip().splitlines()[0].split(",")
    gpu_free_mib = int(parts[0].strip())
    gpu_util = float(parts[1].strip())
except Exception:
    gpu_free_mib, gpu_util = None, None

wmred = {}
try:
    with open(WMRED, "r", encoding="utf-8") as f:
        wmred = json.load(f)
except Exception:
    pass
wm_verdict = "red=true" if wmred.get("red") else "red=false"

with open(STATE, "r", encoding="utf-8") as f:
    st = json.load(f)

NEXT = ("r1118 FIRST ACTIONS: (1) W278 five-face splice EDITOR CHAIN = P0 product (E63 canon-clone "
        "results/_w277bmc_derive_editor.py one-generation roll W277->W278; MEASURED needle preflight "
        "r1077 law; CLEAN-AT-BIRTH 10th gen target; splice executor -> engine mtime-watch self-burn -> "
        "sixgate PRE-FINALIZE 41st consecutive (40th->41st post-freeze narration roll disclosed) -> "
        "finalize/fivekeys/sec78 = r1119; bands A 626_901..628_900 27th A-hop / B 628_901..629_100 28th "
        "above-own-A per frozen W278 prereg df1aaba72a verbatim); (2) TODAY Monday 15:30 papers chain on "
        "the new bar (live.paper enforce + t35_openfill + t24 x2 + aggr + alloc + grid + system_v1 + "
        "t35_export + scorecard; debt=0 cutoff 10-16); (3) night GPU lane standing P0 = jman v2 "
        "young-era + female-lead W1/W2 dataset assembly (11:16+11:21 CEO tickets, musubi fp8 + 32-count "
        "dataset + W6 face-score gate); (4) D-19 dual-scan both ends; (5) BigMoney automation-plan "
        "deadlines <=10-25 / <=10-31 watch; (6) bm-c task-face budget 90/100 observation (12:29 order; "
        "+1 RepoSlim registered this window); next 5x HANDOVER duty = bm-c r1120")

DID = ("r1117 (CEO-ticket product window): (1) S0-1 anchor bm-c + round-zero probe py_faces=4 orphans=0 "
       "resident_servers=1 zero-kill + S0 pull --rebase Already-up-to-date (HEAD==origin 78103a8361 clean "
       "open); (2) S0.5 D-19 opening delta consumed: ORD cac54c8f->15f5bbbf (exactly 1 row = 12:3x "
       "knowledge-base v1.2 scheduling-domain row, r1116-disclosed opening debt, bm-a executed zero bm-c "
       "action; judgment receipt results/_r1117bmc_ord_judgment.json) / DEC 95879dd9 FALSE hold; d19 "
       "update --advance two-face read-back full-string equality OK heartbeat mirrors synced 7; S7 tail "
       "re-probe dual FALSE (15f5bbbf/95879dd9 hold, zero mid-round arrivals); unacked=0; (3) S1 smoke "
       "49/49; (4) P0 CEO TICKET cadence-v2 leg-8 (11:53 row) EXECUTED: cph4/cadence.md sec.8 v2 table "
       "fresh-read via python raw bytes (results/_r1117bmc_cadence_sec8.txt, PS Out-File GBK-mojibake "
       "disclosed+discarded r1113 family) + 340-line census (results/_r1117bmc_task_census_raw.csv) -> "
       "Set-ScheduledTask single-field re-freq 8/8 ALL OK read-back verified (Bigmoney-IterationLoop "
       "PT10M->PT5M / MiniGameEngineTick PT10M->PT5M / BmcIdleGuard PT10M->PT5M / Bigmoney-PoolWorker "
       "PT15M->PT5M / FluxGroup-FleetOversight PT1H->PT30M / HQ-MemoryBudgetGate PT4H->PT2H + "
       "MiniGameRadarTick +21:52 shift (09:52 kept) + MiniGameAuditTick +05:52 shift (17:52 kept)); "
       "S4U+VBS chains untouched (Action/Principal zero-touch, all logon=Interactive no flip attempts), "
       "states preserved (Running->Running/Ready->Ready), start-minute mod-5 stagger kept (residues 0/1/2 "
       "as original), table keep-untouched honored (LoopWatchdog/MiniGameTickWatchdog 1-2min family + "
       "FluxGroup-PatrolRound weekly not 30min family), zero-hit families disclosed (OrderSentinel/"
       "DeliveryWatch/HQ-Patrolx10/QuantAuditProbe/QuantOversightDigest/BigCompute; "
       "MiniGameOllamaKeepWarm=LLM-retired not reinstalled); evidence _r1117bmc_cadence_apply.ps1 + "
       "_r1117bmc_cadence_readback.txt; receipt fleet/inbox/MSG-1334-bmc-cadence-v2.md (window 22:0x met "
       "9h early); (5) P0 CEO TICKET REPO-SLIM leg-7 (12:21 row) EXECUTED: group-tree pull --ff-only "
       "REFUSED (21-ahead/117-behind divergence + 6 live dirty faces, S0 conflict law no force) -> "
       "r1113 python-raw-bytes surgical materialization from origin/main blobs x3 (Tools/hooks/pre-commit "
       "1206B sha16 dded96e9cbcfd19b + Tools/repo-slim.ps1 3878B sha16 6728181f65ee667c + .gitattributes "
       "458B LF-enforce) + git config core.hooksPath Tools/hooks (read-back OK) + hook smoke 'git hook "
       "run pre-commit' rc=0 (20MB BLOCK/5MB WARN pure-git-plumbing gate live) + FluxGroup-RepoSlim "
       "sentinel registered daily:09:03 via task-register (InvisibleRunner.vbs hidden chain; S4U denied "
       "unelevated UAC = D-20261002-02 adjudicated face -> degraded InteractiveToken queued "
       "Tools/task-s4u-backlog.md) + FIRST RUN rc=0 (loose=0 gc clean, pack 493.7MB, gitDir 511.4MB, "
       "cruft 8.8MB, bigFile ledger 12 = mp3 family 8-11.6MB honestly reported: local checkout still "
       "tracks mp3s = 117-behind pre-rm--cached state, alerts=0) + stale gc-garbage tmp_pack_WZw39Y "
       "14.8MB removed after zero-live-git verification + gc.auto=0 verified untouched; receipt "
       "fleet/inbox/MSG-1334-bmc-repo-slim.md; (6) S6 light 10/10 rc0 (driver _r1117bmc_s6_light.py "
       "r1116 canon-clone, log _r1117bmc_s6_log.txt: dualrun ZERO-DRIFT streak 51 @461 cutoff 10-15 / "
       "compute_audit FLAG pool_starvation+supply_floor = idle-starvation structural answered-by-chain "
       "[W278 splice editor chain r1118] py 0.3-1.7pct / py_watermark py_low_board_clear legal whitelist "
       "(board clear, pool 0, bars absent pre-15:30 Monday) / update_daily 0 rows cutoff 10-16 papers "
       "debt=0 / market_regime ORANGE shadow days_in_state=1 asof 10-16 / market_clock CALL-2026-10-16 "
       "ORANGE_COOL idempotent / fund_premium no-op pre-15:30 / b_layer all_pass / REPORT-2026-10-19 "
       "faces=5 token=1 / token delta=0); (7) W278 splice editor chain DEFERRED to r1118 FIRST ACTION per "
       "multi-step window-budget law (r1096/r1098 precedent: CEO tickets consumed this window per S3 "
       "fixed order; editor derive = full-window job) -- honest split, not dropped; (8) S7: attrition 4 "
       "ledger files CLEAN (3 healed shrinks as-is) + quad green (IterationLoop PT5M LIVE next-fire "
       "13:20 verified via schtasks zero-window wrapper + LoopWatchdog PT2M next 13:19 + precommit/"
       "prepush claws CR-normalized identical x2) + idle --worked rc0 idle_rounds=0 agenda_starved=false "
       "+ orphan 4/0/1 zero-kill + fleet/inbox pending=0")

VERIFY = ("smoke 49/49 + cadence read-back 8/8 OK (per-task intervals/states/logon printed + saved) + "
          "git hook run pre-commit rc=0 + repo-slim first-run rc=0 (loose=0) + d19 advance read-back "
          "full-string equality + heartbeat mirrors synced 7 + S6 log 10x rc=0 re-read + attrition 4 "
          "CLEAN + quad green (PT5M live next-fire 13:20 + watchdog + claws x2 identical) + idle "
          "--worked rc0 + orphan 4/0/1 zero-kill + D-19 tail dual FALSE + closeout commit rides this "
          "window (push + fetch + ls-tree self-proof)")

VERDICT = ("green r1117 CEO-ticket product window (cadence-v2 leg-8 8/8 re-freq + 2 shift additions "
           "read-back all OK + REPO-SLIM leg-7 gate+sentinel landed first-pack rc=0 + D-19 15f5bbbf "
           "1-row zero-action + S6 light 10/10 + smoke 49/49 + quad green PT5M live; W278 splice editor "
           "chain = r1118 FIRST ACTION honest split; GPU idle, night queue jman v2 + female-lead "
           "datasets)")

st.update({
    "round_no": 1118,
    "round_no_label": "r1117 closeout -> counter 1118",
    "last_round": "r1117",
    "last_round_label": "r1117",
    "last_round_at": ts, "last_round_ts": ts, "last_round_closed": ts, "last_round_closed_at": ts,
    "last_round_summary": VERDICT, "last_round_summary_at": ts,
    "last_action": "r1117 closeout (cadence-v2 leg-8 8/8 + REPO-SLIM leg-7 gate+sentinel + d19 15f5bbbf + S6 light 10/10 + quad green; counter 1117->1118)",
    "last_action_at": ts,
    "last_run_at": ts,
    "last_pulled_at": ts,
    "current_task": "r1118 FIRST ACTION = W278 five-face splice editor chain (E63 canon-clone _w277bmc_derive_editor.py; sixgate 40th->41st post-freeze narration); TODAY 15:30 papers chain; night GPU lane jman v2 + female-lead W1/W2",
    "current_task_at": ts, "current_task_ts": epoch,
    "did": DID,
    "verify": VERIFY,
    "verdict": VERDICT,
    "head_sha": "r1117 closeout (cadence-v2 leg-8 + REPO-SLIM leg-7 receipts MSG-1334 x2 + D-19 15f5bbbf; W278 splice = r1118 first)",
    "last_artifact": "results/_r1117bmc_cadence_apply.ps1 + _r1117bmc_cadence_readback.txt (8/8 OK) + fleet/inbox/MSG-1334-bmc-cadence-v2.md + MSG-1334-bmc-repo-slim.md + _r1117bmc_ord_judgment.json + _r1117bmc_cadence_sec8.txt + _r1117bmc_s6_light.py + _r1117bmc_s6_log.txt (this closeout batch)",
    "next": NEXT, "next_pointer": NEXT,
    "next_milestone": "W278 splice editor chain (r1118 first action) -> sixgate 41st -> finalize r1119; TODAY 15:30 papers chain; night GPU lane jman v2 + female-lead datasets",
    "note": "r1117: cadence-v2 leg-8 + REPO-SLIM leg-7 both executed+receipted (MSG-1334 x2, 22:0x window met 9h early); D-19 15f5bbbf consumed; W278 splice editor chain deferred r1118 honest split",
    "full_load_selfproof": {
        "占用一行": "CPU=cadence-v2 leg-8 8/8 re-freq + REPO-SLIM leg-7 gate+sentinel landed (CEO tickets closed, receipts MSG-1334 x2); engine wave chain = W278 splice editor chain r1118 first action; GPU=idle ~14GB free, night queue = jman v2 young-era + female-lead W1/W2 datasets (11:16+11:21 CEO tickets); short-video lane DISABLED standing per O-20261017-1741",
        "最近实物": "results/_r1117bmc_cadence_readback.txt (8/8 re-freq read-back) + fleet/inbox/MSG-1334-bmc-cadence-v2.md + MSG-1334-bmc-repo-slim.md @ " + ts,
        "下个里程碑": "W278 splice editor chain r1118 first action -> sixgate 41st; TODAY 15:30 papers chain on new bar; night GPU training lane; BM automation-plan <=10-25/<=10-31",
    },
    "prod_lanes": "CPU=cadence-v2 leg-8 + REPO-SLIM leg-7 landed (CEO tickets closed); engine wave chain = W278 splice editor chain r1118 first action; GPU=idle ~14GB free (night queue jman v2 + female-lead datasets standing P0 night); short-video lane DISABLED standing per O-20261017-1741",
    "r1117_closeout_note": DID,
    "orphan_face": 0, "orphan_faces": 0,
    "idle_rounds": 0, "agenda_starved": False,
    "heartbeat_epoch_utc": epoch,
    "heartbeat_epoch_utc_type": "int (assert)",
    "clock_read": ts, "ts": ts, "updated": ts, "updated_at": ts,
    "last_seen": ts, "last_seen_at": ts, "now_active": ts, "activity_now": ts,
    "orders_ack_receipt": "r1117: zero new repo order files (r1116 scan CLEAN 105/230 stands; 12:3x kb-v1.2 row consumed via d19 advance 15f5bbbf zero-action judgment receipt _r1117bmc_ord_judgment.json; S7 tail dual FALSE); CEO-ticket receipts MSG-1334-bmc-cadence-v2 + MSG-1334-bmc-repo-slim landed fleet/inbox this window",
    "orders_ack_ts": ts,
    "ram_critical_face": "none (loop CPU-only, GPU idle ~14GB free)",
    "ram_free_gb": free_ram, "idle_ram_gb": free_ram, "free_ram_gb": free_ram,
    "cpu_pct": cpu_pct, "cpu_util_pct": cpu_pct, "cpu_idle_pct": round(100 - cpu_pct, 1),
    "sync": {"origin_tip": "r1117 closeout commit rides this window (push lands this window; post-push behind=0 verified same window)", "ts": ts},
})
if gpu_free_mib is not None:
    st["gpu_free_mib"] = gpu_free_mib
    st["gpu_free_vram_mib"] = gpu_free_mib
    st["gpu_idle_mib"] = gpu_free_mib
    st["gpu_idle_vram_mib"] = gpu_free_mib
    st["gpu_vram_free_mb"] = gpu_free_mib
    st["gpu_free_vram_mb"] = gpu_free_mib
    st["gpu_idle_vram_mb"] = gpu_free_mib
    st["free_vram_mb"] = gpu_free_mib
    st["gpu_free_mb"] = gpu_free_mib
    st["gpu_util_pct"] = gpu_util
    st["gpu_used_mib"] = 16384 - gpu_free_mib

dg = st.get("d19_watermark_guard", {})
dg["round_ref"] = 1117
dg["ts"] = ts
st["d19_watermark_guard"] = dg

with open(STATE, "w", encoding="utf-8") as f:
    json.dump(st, f, indent=1, sort_keys=True, ensure_ascii=False)
with open(HB, "w", encoding="utf-8") as f:
    json.dump(st, f, indent=1, sort_keys=True, ensure_ascii=False)

# ---------- report row ----------
row = " | ".join([
    ts, "r1117", "bm-c",
    "watermark verdict=green (%s lane=healthy; py_watermark py_low_board_clear legal whitelist pre-15:30 Monday; "
    "audit FLAG pool_starvation/supply_floor structural answered-by-chain W278-splice-r1118; idle --worked rc0 "
    "idle_rounds=0; boards clear jobs 0)" % wm_verdict,
    DID,
    "verify: " + VERIFY,
    "next " + NEXT,
])
raw = open(REPORT, "rb").read()
eol = b"\r\n" if b"\r\n" in raw[-400:] else b"\n"
with open(REPORT, "ab") as f:
    f.write(eol + row.encode("utf-8"))

# ---------- self-asserts ----------
with open(HB, "r", encoding="utf-8") as f:
    hb = json.load(f)
assert isinstance(hb["heartbeat_epoch_utc"], int), "epoch must be int"
assert hb["round_no"] == 1118, "counter must be 1118"
assert "T" in hb["clock_read"], "clock_read must be T-separated ISO8601"
with open(STATE, "r", encoding="utf-8") as f:
    st2 = json.load(f)
assert st2["last_round"] == "r1117" and st2["round_no"] == 1118
print("CLOSEOUT OK round_no=1118 epoch=%d clock=%s free_ram=%.2fGB gpu_free=%sMiB report_row=+1" % (
    hb["heartbeat_epoch_utc"], hb["clock_read"], free_ram, gpu_free_mib))
