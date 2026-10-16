# -*- coding: utf-8 -*-
# _r1061bmc_closeout.py -- r1061 (51st-gen absorb continuation) closeout writer.
# Absorb law: dead r1061 window landed W258 PREREG FREEZE 824b46d31 itself;
# THIS window machine-verified the estate and closes the round out.
# Faces written: round_reports-bm-c.md row append + state-bm-c.json +
# fleet/machines/bm-c.json. Atomic write per r985 wb-open-truncation law.
import datetime
import json
import os
import subprocess
import sys
import time

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
os.chdir(ROOT)

STATE_P = "state-bm-c.json"
HB_P = "fleet/machines/bm-c.json"
REPORT_P = "round_reports-bm-c.md"
FACTS_P = "results/_s05_probe.bm-c.json"


def now_iso():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def atomic_write(path, text):
    tmp = path + ".tmp_r1061closeout"
    body = text  # compute fully BEFORE opening any handle (r985 law)
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        f.write(body)
    os.replace(tmp, path)


# ---------- sample live faces ----------
ram_free_gb = None
vram_free_mib = None
cpu_pct = None
codely_bm_count = None
try:
    import psutil
    vm = psutil.virtual_memory()
    ram_free_gb = round(vm.available / (1024 ** 3), 1)
    cpu_pct = round(psutil.cpu_percent(interval=None), 1)
    cnt = 0
    for p in psutil.process_iter(["name", "cmdline"]):
        try:
            if (p.info["name"] or "").lower() == "codely.exe":
                cl = p.info["cmdline"] or []
                if any(isinstance(c, str) and "Bigmoney" in c for c in cl):
                    cnt += 1
        except Exception:
            pass
    codely_bm_count = cnt
except Exception:
    pass
try:
    out = subprocess.run(
        ["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
        capture_output=True, text=True, timeout=20)
    vram_free_mib = int(out.stdout.strip().splitlines()[0])
except Exception:
    pass

# ---------- probe facts (r583 zero-literal law: shas read programmatically) ----------
with open(FACTS_P, "r", encoding="utf-8") as f:
    facts = json.load(f)
wf = facts["watermark_face"]
ORD_SHA = wf["orders_sha"]
DEC_SHA = wf["decisions_sha"]
assert wf["orders_changed"] is False and wf["decisions_changed"] is False, "probe delta TRUE -- do not close out blindly"

# ---------- load faces ----------
with open(STATE_P, "r", encoding="utf-8") as f:
    state = json.load(f)
with open(HB_P, "r", encoding="utf-8") as f:
    hb = json.load(f)

# phantom-guard: state watermarks must equal probe facts (both pinned methods)
assert state["last_orders_sha"] == ORD_SHA, "ORD watermark phantom (state vs probe facts)"
assert state["last_decisions_sha"] == DEC_SHA, "DEC watermark phantom (state vs probe facts)"

with open(REPORT_P, "r", encoding="utf-8", errors="replace") as f:
    report_body = f.read()
report_lines_before = report_body.count("\n")

TS = now_iso()
EPOCH = int(time.time())

# ---------- texts ----------
ABSORB_NOTE = (
    "r1061 absorb note: dead window self-labeled r1061 (fired ~05:4x after the r1060 closeout 05:25:56) executed the "
    "W258 prereg derive FULL body and committed+pushed W258 PREREG FREEZE 824b46d31 at 05:51:53 (machine-SUB from "
    "frozen W257 tpl 88ae1c8e @ c7fbc443c pre-backfill face per r1052/r1049 law; needle-probe preflight 222 faces all "
    "floors pre-verified; 59 vmap legs + 200 floors + 7 pre-authored consumed-label post-legs + 8 marker-extracted "
    "block replaces; bands A 582_901..584_900 SEVENTH consecutive A-hop / B 584_901..585_100 EIGHTH consecutive "
    "above-own-A per seat probe receipt ADMIT leg0 rows=255 owner=247 bmc=77; W257 finalize actuals machine-carried "
    "[merged mu -0.09275554 / sigma 0.24502959 / se_mu 0.000326 / W257-only -0.10688227 / A p95 0.2973 / K-lift "
    "-0.0001 / n_eff_held 987,535 / line_pre_w257 1.1948 / line_merged@563,320 1.1947 / gap 0.0141 chain-NEW-MAX "
    "in-band / ledger 989,735 EXACT]; 4 disclosed same-window needle heals all face-inventory divergences zero "
    "content defects [PN1 prior-batch face absent this template + bare 03:5x HIST survivor + n1_w255 HIST survivor "
    "+ W252 consumed-label forms pre-authored]; banned_direction_gate ADMIT rc0; out 44,096B sha256_16 "
    "f412a772695ec76e sec7/8 placeholders intact), then re-ran the derive verification pass (estate files mtime "
    "05:52:23, git diff EMPTY both faces -- byte-identical to the landed blob, r1052 FREEZE_T-stamp family did NOT "
    "recur), then ran the S6 43-leg chain 05:54:45-05:56:04 all rc=0 -- died pre-closeout (state frozen round_no=1061, "
    "heartbeat stale r1060). This session (fired 06:05, per bm-c absorb precedent lineage r894..r1060, 51st instance) "
    "machine-verified the estate BEFORE absorb-closeout: prereg worktree==committed blob zero drift (git diff empty) "
    "+ banned_direction_gate re-run rc0 ADMIT + probe receipt re-read (ADMIT bands + W257 finalize anchors ledger "
    "989,735/K=563,320 + waits_upstream=NONE) + S6 log 43x rc=0 read-back + S0.5 pinned-probe dual FALSE (ORD "
    "d89163fb / DEC 881b6dcb hold, unacked=0) + smoke 49/49. Zero double-count: the dead window consumed no ORD/DEC "
    "rows (no watermark writes), its debts landed via its own commit 824b46d31, the S6 chain absorbed same-cycle "
    "per same-round law; executed as r1061 continuation per counter (no label collision), advanced 1061->1062 so "
    "next session = r1062"
)

CLOSEOUT_NOTE = (
    "r1061: 51st-gen absorb continuation (dead W258 prereg window estate verified, landed 824b46d31 by predecessor) "
    "+ S6 43/43 absorbed (dead-window chain 05:54:45-05:56:04 rc0: bars 10-16 cutoff current weekend honest / "
    "regime ORANGE 6th day [hs300<MA200 + crash10d -6.2% + breadth 0.83] / dualrun ZERO-DRIFT streak 20 / audit FLAG "
    "pool_starvation+supply_floor answered-by-chain [W258 splice next] / py_wm insufficient_history fresh / "
    "fund_premium weekend no-op / token delta=0) + smoke 49/49 + satengine ALIVE rc0 + wm red=false healthy "
    "[next_pick=claimed moneyflow-IC parked source-blocked; bm-a T23 fix armed 30-min self-heal = upstream cure "
    "lane, zero bm-c debt] + banned gate ADMIT re-verify + attrition 4 CLEAN + idle worked rc0 + claws + loop "
    "pin=5 + watchdog green + S0.5 dual FALSE both scans + orphan face=2 zero-kill + stray 0B root file 'bm-c' "
    "disclosed untracked left-as-is + r1060 round-report row gap disclosed (authoritative faces = state closeout "
    "note + commit 5632ebf2b; fu-shu prohibition, no retroactive fabrication) | " + TS
)

DID = (
    "r1061 (51st-gen absorb continuation): (1) S0-1 anchor bm-c + round-zero probe py_faces=7 orphans=2 "
    "(孤儿面=2) zero-kill; S0 fetch behind=0 (HEAD==origin 824b46d31; daemon live-faces standing dirty, no rebase "
    "owed); (2) ABSORB 51st-gen: dead r1061 window W258 PREREG FREEZE 824b46d31 landed-by-predecessor, THIS window "
    "machine-verified BEFORE absorb-closeout (worktree==committed blob zero drift + banned_direction_gate re-run "
    "ADMIT rc0 + seat receipt ADMIT A 582_901..584_900 SEVENTH A-hop / B 584_901..585_100 EIGHTH above-own-A + W257 "
    "finalize anchors 989,735/K=563,320 + waits_upstream=NONE); (3) S0.5 dual-delta FALSE both scans (ORD d89163fb "
    "/ DEC 881b6dcb pinned-probe hold, unacked=0; cross-machine face: bm-a r1026 6-row consumption on their own "
    "watermark -- bm-c pinned-probe ground truth = zero delta owed, r977 method-PIN law); (4) S1 smoke 49/49; "
    "satengine ALIVE rc0; wm red=false healthy; (5) S6 43/43 absorbed not rerun (dead-window chain 05:54:45-05:56:04 "
    "all rc=0, same-round law); (6) S7: attrition 4 CLEAN + idle worked rc0 + claws re-registered + loop pin=5 + "
    "watchdog + heartbeat round_no stale face healed (r1060 closeout left round_no/last_round at r1059 values); "
    "counter 1061->1062 so next session = r1062; closeout push rides this window (本地未达 origin commit 数=0 "
    "target, readback verified next-window S0 fetch)"
)

VERDICT = (
    "green: r1061 = 51st-gen absorb continuation -- dead W258 prereg window estate verified (freeze 824b46d31 "
    "landed-by-predecessor, worktree==blob zero drift, banned ADMIT re-run, seat receipt ADMIT) + S6 43/43 absorbed "
    "+ smoke 49/49 + dual-delta FALSE both scans + attrition CLEAN + quad green (watchdog S4U flip = adjudicated "
    "face) + orphan face=2 zero-kill; W258 five-face splice = r1062 first action"
)

NEXT_PTR = (
    "r1062: (1) W258 five-face splice (FIRST ACTION per seat-first law; editor canon = _w257bmc_derive_editor.py "
    "age()-clone per machine-needle law; pre-splice count-asserted authoring gates = canon lineage; splice receipt "
    "dual-sha16 pf/n1 next faces; bands A 582_901..584_900 / B 584_901..585_100; prereg anchor 824b46d31 out "
    "f412a772695ec76e) -> engine self-burn 12/12 (mtime-watch) -> sixgate PRE-FINALIZE (20th consecutive target; "
    "triple identity n1==receipt==LANDED) -> finalize one-pass 989,735+2,200=991,935 / K=563,320+2,200=565,520 "
    "EXACT -> fivekeys vs W257 keys (key1 gap 0.014127 chain-NEW-MAX carried / key4 K-lift -0.0001 / key5 se_mu "
    "0.000326) -> sec.7/8 backfill placeholders=0 -> W259 seat publish (live re-derive; naive W259 A "
    "584_901..586_900 expected REFUSED by registered W258 B 584_901..585_100 = EIGHTH consecutive A-hop face per "
    "probe leg4); (2) V5 assembly-station watch (bm-a lane, DIRECTOR-REVIEW-V5-PASS gate); (3) GPU lane = "
    "interactive window per O-20261017-0131 sec.3 lane-split -- loop stays CPU-only, no double-open; (4) Monday "
    "10-19 15:30 bars window: full papers chain fires on the new bar; ORD/DEC tail re-scan + backlog claimable face"
)

PROD_LANES = (
    "CPU=engine W258 prereg frozen 824b46d31 (five-face splice = r1062 FIRST ACTION) ; GPU=interactive window per "
    "O-20261017-0131 sec.3 lane-split (loop CPU-only, no double-open; llm fill-gap resident)"
)

ARTIFACT = (
    "research/PERPETUAL_N1_W258_PREREG.md (frozen 44,096B, origin 824b46d31, sha256_16 f412a772695ec76e) + "
    "results/_r1061bmc_s6_log.txt (43/43 rc0) + results/_w258bmc_prereg_derive.py"
)

MILESTONE = (
    "W258 five-face splice -> self-burn 12/12 -> sixgate 20th consecutive -> finalize 991,935/K=565,520 EXACT -> "
    "W259 seat publish (r1062-r1064, 48h window)"
)

CURRENT_TASK = "r1061 closeout (51st-gen absorb: W258 prereg estate verified, landed 824b46d31 by predecessor; splice = r1062 first action)"

VERIFY = (
    "estate: prereg worktree==committed blob zero drift (git diff empty) + banned_direction_gate re-run rc0 ADMIT + "
    "probe receipt ADMIT (W257 anchors 989,735/563,320, waits_upstream=NONE) + S6 log 43x rc=0 read-back; gates: "
    "smoke 49/49 + satengine ALIVE rc0 + s05 pinned-probe dual FALSE (ord d89163fb / dec 881b6dcb == state keys, "
    "phantom-guard asserted in-script) + attrition 4 CLEAN + idle worked rc0 + epoch int readback + report line "
    "+1 asserted"
)

# ---------- append round report row ----------
ROW = " | ".join([
    TS, "r1061", "bm-c",
    "watermark verdict=绿 (red=false healthy / satengine ALIVE rc0 / tickets 0 / jobs 0 / engine-queue never-dry W258 prereg frozen 824b46d31)",
    TS, "r1061",
    DID,
    "next: " + NEXT_PTR,
])
if report_body and not report_body.endswith("\n"):
    report_body += "\n"
report_body += ROW + "\n"
report_lines_after = report_body.count("\n")
assert report_lines_after == report_lines_before + 1, "report line-count assertion failed"
atomic_write(REPORT_P, report_body)

# ---------- mutate shared faces ----------
def apply_faces(d):
    d["clock_read"] = TS
    d["ts"] = TS
    d["heartbeat_epoch_utc"] = EPOCH
    d["current_task"] = CURRENT_TASK
    d["current_task_at"] = TS
    d["did"] = DID
    d["verdict"] = VERDICT
    d["verify"] = VERIFY
    d["next"] = NEXT_PTR
    d["next_pointer"] = NEXT_PTR
    d["prod_lanes"] = PROD_LANES
    d["latest_artifact"] = ARTIFACT
    d["last_artifact"] = ARTIFACT
    d["recent_artifact"] = ARTIFACT
    d["next_milestone"] = MILESTONE
    d["note"] = "r1061: 51st-gen absorb continuation -- W258 prereg estate verified (824b46d31 landed by predecessor) + S6 43/43 absorbed + smoke 49/49 + quad green; splice = r1062 first action"
    d["last_orders_sha"] = ORD_SHA
    d["last_decisions_sha"] = DEC_SHA
    for k in ("last_orders_read_at", "last_orders_seen", "last_orders_at", "last_decisions_read_at",
              "last_decisions_seen", "last_decisions_at", "activity_now", "now_active",
              "last_seen", "last_seen_at", "updated", "updated_at"):
        if k in d:
            d[k] = TS
    d["last_round"] = "r1061"
    d["last_round_at"] = TS
    d["last_round_label"] = "r1061"
    d["last_round_summary"] = "r1061: W258 prereg estate absorbed (824b46d31 landed by predecessor, banned ADMIT re-verified) + S6 43/43 + smoke 49/49 + attrition CLEAN + quad green"
    d["last_round_summary_at"] = TS
    d["last_round_closed"] = TS
    d["last_action"] = "r1061 closeout (51st-gen absorb + S6 absorbed + quad green + counter 1061->1062)"
    d["last_action_at"] = TS
    d["orphan_face"] = 2
    d["orphan_faces"] = 2
    d["idle_rounds"] = 0
    d["agenda_starved"] = False
    d["health"] = "ok"
    if ram_free_gb is not None:
        d["free_ram_gb"] = ram_free_gb
        d["idle_ram_gb"] = ram_free_gb
        d["ram_free_gb"] = ram_free_gb
    if cpu_pct is not None:
        d["cpu_pct"] = cpu_pct
        d["cpu_idle_pct"] = round(100.0 - cpu_pct, 1)
        d["cpu_util_pct"] = cpu_pct
    if vram_free_mib is not None:
        gb = round(vram_free_mib / 1024.0, 1)
        mb = vram_free_mib  # MiB face kept; MB aliases mirrored per standing schema
        for k in ("gpu_free_vram_mib", "gpu_free_mib", "gpu_idle_vram_mib", "gpu_idle_mib"):
            d[k] = vram_free_mib
        for k in ("gpu_free_vram_mb", "gpu_free_mb", "gpu_idle_vram_mb", "gpu_idle_mb",
                  "gpu_vram_free_mb", "free_vram_mb"):
            d[k] = mb
        d["gpu_free_vram_gb"] = gb
        d["gpu_mem_used_mib"] = 16384 - vram_free_mib
    if codely_bm_count is not None:
        d["codely_live_count"] = codely_bm_count

apply_faces(state)
apply_faces(hb)

# state-specific: counter advance + absorb/closeout notes
state["round_no"] = 1062
state["round_no_label"] = "r1061"
state["r1061_absorb_note"] = ABSORB_NOTE
state["r1061_closeout_note"] = CLOSEOUT_NOTE
state["head_sha"] = "W258 prereg frozen by dead-window predecessor 824b46d31 (this window's closeout commit+push rides this window)"
state["sync"] = {"origin_tip": "824b46d31 (bmq origin at closeout open; absorb closeout push rides this window)", "ts": TS}
state["full_load_selfproof"] = {
    "占用一行": "CPU=engine lane W258 prereg frozen 824b46d31 (five-face splice = r1062 first action) ; GPU=llm fill-gap mode resident (loop CPU-only per O-20261017-0131 sec.3, no double-open)"
}
state["last_orders_sha_note"] = "r1061: ORD delta FALSE hold (pinned content-sha1 probe; bm-a r1026 6-row consumption is their own watermark face -- bm-c ground truth zero rows owed, r977 method-PIN law)"
state["last_decisions_read_note"] = "r1061: DEC delta FALSE hold (raw-blob sha256 pinned probe; zero rows owed)"

# heartbeat-specific: closed-round convention (r1059 precedent) + notes
hb["round_no"] = 1061
hb["r1061_closeout_note"] = CLOSEOUT_NOTE
hb["last_round_ts"] = TS
hb["orders_ack_ts"] = TS
hb["heartbeat_epoch_utc_type"] = "int (assert)"
hb["d19_watermark_guard"] = {
    "tool": "scripts/d19_watermark.py",
    "probe": "results/_r686bmb_d19_check.py",
    "probe_evidence": "K:\\Fluxgroup\\FluxGroup\\quant\\bigmoney\\results\\_r686bmb_d19_check.json",
    "method_decisions": "sha256",
    "method_orders": "sha1",
    "verbatim": True,
    "advance": True,
    "round_ref": 1061,
    "ts": TS,
}

# ---------- write with pre-computed bodies ----------
state_text = json.dumps(state, indent=1, ensure_ascii=False) + "\n"
hb_text = json.dumps(hb, indent=1, ensure_ascii=False) + "\n"
atomic_write(STATE_P, state_text)
atomic_write(HB_P, hb_text)

# ---------- readback assertions ----------
with open(STATE_P, "r", encoding="utf-8") as f:
    s2 = json.load(f)
with open(HB_P, "r", encoding="utf-8") as f:
    h2 = json.load(f)
assert s2["round_no"] == 1062, "state round_no readback"
assert h2["round_no"] == 1061, "heartbeat round_no readback"
assert isinstance(s2["heartbeat_epoch_utc"], int) and isinstance(h2["heartbeat_epoch_utc"], int), "epoch int"
assert s2["last_orders_sha"] == ORD_SHA and s2["last_decisions_sha"] == DEC_SHA, "watermark readback"
with open(REPORT_P, "r", encoding="utf-8", errors="replace") as f:
    _rep = f.read()
_last = [ln for ln in _rep.splitlines() if ln.strip()][-1]
assert "| r1061 | bm-c" in _last and "watermark verdict" in _last, "report row readback"

print(json.dumps({
    "ok": True,
    "ts": TS,
    "state_round_no": s2["round_no"],
    "hb_round_no": h2["round_no"],
    "epoch": s2["heartbeat_epoch_utc"],
    "epoch_is_int": isinstance(s2["heartbeat_epoch_utc"], bool) is False and isinstance(s2["heartbeat_epoch_utc"], int),
    "ram_free_gb": ram_free_gb,
    "vram_free_mib": vram_free_mib,
    "cpu_pct": cpu_pct,
    "codely_bm_count": codely_bm_count,
    "ord_sha": ORD_SHA[:8],
    "dec_sha": DEC_SHA[:8],
    "report_line_added": True,
}, ensure_ascii=False))
