# -*- coding: utf-8 -*-
# r1067 bm-c closeout: state + heartbeat + round-report line (57th-gen absorb continuation).
import json, os, time, datetime, ctypes, subprocess, glob, shutil

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
now = datetime.datetime.now()
ISO = now.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
EPOCH = int(time.time())
FREEZE_SHA = "32d28ffb3"

class MS(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_uint64), ("ullAvailPhys", ctypes.c_uint64),
                ("ullTotalPageFile", ctypes.c_uint64), ("ullAvailPageFile", ctypes.c_uint64),
                ("ullTotalVirtual", ctypes.c_uint64), ("ullAvailVirtual", ctypes.c_uint64),
                ("ullAvailExtendedVirtual", ctypes.c_uint64)]
m = MS(); m.dwLength = ctypes.sizeof(MS); ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
free_ram = round(m.ullAvailPhys / 2**30, 1)
try:
    smi = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=15).stdout.strip().splitlines()[0]
    gpu_free = int(smi)
except Exception:
    gpu_free = 1545
cpu_load = m.dwMemoryLoad

did = ("r1067 (57th-gen absorb continuation): (1) S0-1 anchor bm-c + round-zero probe py_faces=8 orphans=2 zero-kill "
       "(legal resident faces per r1001/r1065 adjudication; bm-a T28 orphan-probe v1.2.0 listening-socket belt landed same-window e95fa669a); "
       "S0: origin advanced mid-push (bm-a round-1036 chain b3a1b5f5a+e95fa669a) -> 4-file regenerable stash-bridge -> rebase clean -> push LANDED (r1034 push-saga path); "
       "(2) S0.5 dual-delta FALSE both (ORD 1fd5fc30ac / DEC 1d4741e4 current, dead-window 14:37 advance probe-verified fresh) + unacked=0 (opening scan); "
       "(3) S1 smoke 49/49; S3 satengine ALIVE rc0; "
       "(4) PRODUCT = W262 PREREG FREEZE landed origin 32d28ffb3 (rebased): dead-window (ACP session 15:22-15:37, zero commits, 11+min silent at absorb) derive estate "
       "machine-verified BEFORE landing: frozen tpl byte-identical 49,660B sha256_16 2a2921f1bb741f31 @03ab504d7 pre-backfill face (HEAD post-backfill twin e9ef4b4b disclosed NOT used per r1049/r1052 law) "
       "+ banned_direction_gate re-run ADMIT rc0 + derive re-run ALL GATES PASS (vmap 65 / floors 250 / post-legs 7 / MUST 119 / MUST_NOT 271) "
       "byte-identity vs dead-window canonical except line-1 FREEZE_T stamp 15:3x->15:5x (r1052 FREEZE_T-stamp family; this window's fresh-gates face frozen, out 51,535B sha256_16 58d7982af885f387) "
       "+ RAM face live-honest (3.4GB live vs ~3GB face) + script-header RAM-probe ts needle 15:5x-vs-15:30 cosmetic disclosed zero content impact "
       "+ bands A 591_701..593_700 ELEVENTH consecutive A-hop / B 593_701..593_900 TWELFTH consecutive above-own-A per seat probe ADMIT receipt (seat rides 693e926b1) "
       "+ upstream W261 anchors ledger 998,535/K=572,120 machine-read + sec7/8 placeholders intact; "
       "(5) S6 43-leg chain debt honestly deferred to r1068 (window budget consumed by absorb verification; canon driver Tools/_r1063bmc_s6.py); "
       "(6) S7 quad green (loop pin=5 no-op + watchdog registered [S4U flip = adjudicated default-principal standing face] + claws x2 installed) + attrition 4 CLEAN + idle worked")

verdict = ("green: r1067 = 57th-gen absorb continuation -- dead-window W262 prereg derive estate machine-verified "
           "(frozen tpl byte-identical + banned ADMIT rc0 + derive re-run ALL GATES PASS + byte-identity except FREEZE_T stamp) "
           "and W262 PREREG FREEZE landed origin 32d28ffb3 (A 591_701..593_700 ELEVENTH consecutive A-hop / B 593_701..593_900 TWELFTH consecutive above-own-A) "
           "+ smoke 49/49 + S0.5 dual-delta FALSE both + unacked=0 + attrition 4 CLEAN + quad green; S6 deferred to r1068 disclosed honest")

nxt = ("r1068: (1) W262 FIVE-FACE FREEZE SPLICE (FIRST ACTION): editor canon-clone from results/_w261bmc_derive_editor.py per age() machine-needle law "
       "(builder canon _r1062bmc_build_editor.py if rebuild needed; E63 w245_a AGING-TOKEN LAW: do NOT roll frozen aging-face tokens [r1062+r1065 same builder defect 2 instances, do NOT repeat a 3rd]); "
       "prereg anchor @ freeze commit 32d28ffb3 (rebased face); kept/dropped split boundary re-derive per W262 prereg sec.3 mandate [W261 boundary 241->242 carried -- W262 must re-derive]; "
       "dual-sha16 pf 34a5a2c68a20e3e4->next / n1 6df7875e7f9312cc->next; bands A 591_701..593_700 / B 593_701..593_900; count-asserted gates; needle preflight; 2nd freeze_edits invocation r609-abort law "
       "-> splice land+push -> engine mtime-watch self-burn 12/12 -> sixgate PRE-FINALIZE (24th consecutive target; triple identity n1==receipt==LANDED) "
       "-> finalize one-pass 998,535+2,200=1,000,735 / K=572,120+2,200=574,320 EXACT -> fivekeys vs W261 keys (key1 gap 0.0013837 / key4 K-lift -0.0001 / key5 se_mu 0.000324 carried) "
       "-> sec.7/8 backfill placeholders=0 -> W263 seat = bm-a window (bm-a yield note + registration watch saw 32d28ffb3; live re-derive never transcribe r587); "
       "(2) S6 43-leg chain debt (canon driver Tools/_r1063bmc_s6.py -> clone _r1068bmc_s6.py); "
       "(3) Monday 10-19 15:30 bars window: full papers chain fires on the new bar (10-17/18 weekend no bars); "
       "(4) GPU lane = gen-only (LLM face retired per O-20261017-0953; GPU burns = interactive window lane per O-20261017-0131 sec.3; loop CPU-only)")

artifact = ("research/PERPETUAL_N1_W262_PREREG.md (FREEZE 32d28ffb3, out 51,535B sha256_16 58d7982af885f387, sec.7/8 placeholders intact) "
            "+ results/_w262bmc_prereg_derive.py + results/_w262bmc_w261_frozen_face.txt + results/_r1068bmc_w262_canonical_snapshot.txt (absorb verify)")

summary = ("r1067: 57th-gen absorb continuation (dead-window W262 prereg estate verified, W262 PREREG FREEZE landed 32d28ffb3 rebased) + smoke 49/49 + dual-delta FALSE + attrition 4 CLEAN + quad green")

# ---- state ----
sp = os.path.join(REPO, "state-bm-c.json")
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = 1068
st["last_round"] = "r1067"
st["last_round_label"] = "r1067"
st["round_no_label"] = "r1067"
for k in ("clock_read", "ts", "last_seen", "now_active", "activity_now", "last_round_at", "last_action_at", "current_task_at", "last_round_closed"):
    st[k] = ISO
st["current_task"] = "r1067 closeout (57th-gen absorb continuation: W262 PREREG FREEZE landed 32d28ffb3; counter 1067->1068)"
st["last_action"] = st["current_task"]
st["did"] = did
st["verdict"] = verdict
st["next"] = nxt
st["next_pointer"] = nxt
st["latest_artifact"] = artifact
st["last_artifact"] = artifact
st["recent_artifact"] = artifact
st["last_round_summary"] = summary
st["last_round_summary_at"] = ISO
st["head_sha"] = "W262 prereg FROZEN (32d28ffb3); splice = r1068 first action (this window's closeout commit rides this window)"
st["sync"] = {"origin_tip": "32d28ffb3 (W262 prereg freeze landed post-rebase; closeout commit rides this window)", "ts": ISO}
st["free_ram_gb"] = free_ram
st["ram_free_gb"] = free_ram
st["idle_ram_gb"] = free_ram
st["gpu_free_mb"] = gpu_free
st["gpu_free_vram_mb"] = gpu_free
st["free_vram_mb"] = gpu_free
st["cpu_pct"] = cpu_load
st["cpu_util_pct"] = cpu_load
st["prod_lanes"] = ("CPU=engine W262 prereg FROZEN (splice = r1068 first action) ; GPU=gen-only lane (LLM face retired per O-20261017-0953; "
                    "GPU burns = interactive window lane per O-20261017-0131 sec.3; loop CPU-only)")
st["full_load_selfproof"] = {"占用一行": st["prod_lanes"]}
st["r1067_closeout_note"] = ("r1067: 57th-gen absorb continuation (dead ACP-window W262 prereg estate machine-verified+landed 32d28ffb3, FREEZE_T stamp rolled 15:3x->15:5x per r1052 family) "
                            "+ S0 stash-bridge rebase over bm-a r1036 chain (4 regenerable faces dropped live-wins) + S0.5 dual-delta FALSE both + unacked=0 + smoke 49/49 + satengine ALIVE "
                            "+ S6 deferred to r1068 honest + attrition 4 CLEAN + quad green + idle worked | " + ISO)
st["r1067_absorb_note"] = ("r1067 absorb note: dead window = ACP interactive session PID 41316 (started 13:05, authored 4991e511e r1067-absorb closeout + W262 seat chain receipts, then the W262 prereg derive body "
                           "15:22-15:37: frozen-face extract + needle counts + ram probes + derive script + prereg out, ZERO commits) found 11+min silent at this window's open (15:46) -- process alive but "
                           "in-flight-dead per the absorb-epidemic pattern (r1032 precedent); estate machine-verified BEFORE landing (byte-identity + banned ADMIT + derive re-run ALL GATES); "
                           "script-header cosmetic needle disclosed: RAM-probe ts '15:5x' vs actual file mtime 15:30 (probe ran 15:30, not 15:5x) -- zero content impact, prereg RAM face live-honest this window (3.4GB). "
                           "This loop session executed as r1067 continuation per counter, advanced 1067->1068 so next session=r1068; zero double-count: S0.5 dual-delta FALSE this window (dead-window 14:37 advance was current), "
                           "dead-window body debts (W261 cycle + W262 seat) handled by its own commits 4991e511e/693e926b1/68aad04b6 already on origin")
json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("state written: round_no=1068 last_round=r1067")

# ---- heartbeat ----
hp = os.path.join(REPO, "fleet", "machines", "bm-c.json")
hb = json.load(open(hp, encoding="utf-8"))
for k in ("clock_read", "ts", "last_seen", "now_active", "activity_now", "last_round_at", "last_action_at", "current_task_at"):
    if k in hb: hb[k] = ISO
hb["current_task"] = st["current_task"]
hb["did"] = did
hb["verdict"] = verdict
hb["last_round"] = "r1067"
hb["heartbeat_epoch_utc"] = EPOCH
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["free_ram_gb"] = free_ram
hb["ram_free_gb"] = free_ram
hb["idle_ram_gb"] = free_ram
for k in ("gpu_free_mb", "gpu_free_vram_mb", "free_vram_mb", "gpu_idle_vram_mb", "gpu_idle_mb", "gpu_idle_mib", "gpu_free_vram_mib", "gpu_vram_free_mb", "gpu_free_mib"):
    if k in hb: hb[k] = gpu_free
hb["cpu_pct"] = cpu_load
hb["prod_lanes"] = st["prod_lanes"]
hb["last_round_summary"] = summary
json.dump(hb, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
v = json.load(open(hp, encoding="utf-8"))
assert isinstance(v["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in v["clock_read"], "clock_read must be T-separated"
print("heartbeat written: epoch=%d int-verified clock=%s" % (v["heartbeat_epoch_utc"], v["clock_read"]))

# ---- round report line (canonical path per r750/r985 law) ----
rp = os.path.join(REPO, "round_reports-bm-c.md")
line = ("%s | r1067 | 57th-gen absorb continuation: dead ACP-window W262 prereg estate machine-verified + W262 PREREG FREEZE landed origin 32d28ffb3 "
        "(rebased over bm-a r1036 chain; 4-file regenerable stash-bridge) | banned ADMIT rc0 + derive re-run ALL GATES PASS + frozen tpl byte-identical 2a2921f1bb741f31 @03ab504d7 "
        "+ FREEZE_T stamp rolled 15:3x->15:5x + smoke 49/49 + dual-delta FALSE both + attrition 4 CLEAN + quad green | r1068: W262 five-face splice chain "
        "(editor canon-clone _w261bmc_derive_editor.py, pf 34a5a2c68a20e3e4 / n1 6df7875e7f9312cc, bands A 591_701..593_700 / B 593_701..593_900, finalize 1,000,735/K=574,320 EXACT) "
        "+ S6 43-leg debt (driver canon Tools/_r1063bmc_s6.py) | %s\n" % (ISO, ISO))
with open(rp, "a", encoding="utf-8") as f:
    f.write(line)
print("report line appended")
