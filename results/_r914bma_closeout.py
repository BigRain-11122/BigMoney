# -*- coding: utf-8 -*-
"""r914 bm-a closeout: report-line heal+append, state 913->914, heartbeat
full refresh, inbox MSG archive, DEC/ORD full-hash watermark update."""
import datetime
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
GIT = r"C:\Program Files\Git\cmd\git.exe"
GRP = r"C:\Users\sjs20\Desktop\FluxGroup"

now = datetime.datetime.now().astimezone()
clock = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
stamp = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())
print("clock_read:", clock, "epoch:", epoch)


def sha_git_show(path):
    b = subprocess.run([GIT, "-C", GRP, "show", "origin/main:" + path],
                       capture_output=True).stdout
    return hashlib.sha256(b).hexdigest()


subprocess.run([GIT, "-C", GRP, "fetch", "origin"], capture_output=True)
DEC_SHA = sha_git_show("docs/decisions.md")
ORD_SHA = sha_git_show("docs/orders.md")
print("DEC", DEC_SHA[:8], "ORD", ORD_SHA[:8])

# --- resource best-effort refresh --------------------------------------
cpu_pct, ram_gb, vram_gb = None, None, None
try:
    import psutil
    cpu_pct = round(psutil.cpu_percent(interval=1.0), 1)
    vm = psutil.virtual_memory()
    ram_gb = round(vm.available / (1024 ** 3), 1)
except Exception as e:
    print("psutil unavailable:", str(e)[:60])
try:
    r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                        "--format=csv,noheader,nounits"],
                       capture_output=True)
    vram_gb = round(float(r.stdout.decode().strip().splitlines()[0]) / 1024, 2)
except Exception as e:
    print("nvidia-smi unavailable:", str(e)[:60])
print("cpu%%=%s ram_free=%s vram_free=%s" % (cpu_pct, ram_gb, vram_gb))

# --- 1) report line heal (r913 legacy->canonical) + r914 line -----------
legacy = io.open("logs/iteration-loop/round_reports-bm-a.md",
                 encoding="utf-8", newline="").read()
r913_lines = [ln for ln in legacy.splitlines()
              if ln.startswith("2026-10-09T11:41:35+08:00 | r913")]
assert len(r913_lines) == 1, "r913 line not found once: %d" % len(r913_lines)
r913_line = r913_lines[0]

R914 = (
    stamp + " | r914 | bm-a | dept:research (r914 dead-session estate "
    "absorption + W197 prereg build + PARKING-P1 frozen [dead-session "
    "product]; N1 perpetual supply line) | WM-VERDICT: green (red=false "
    "lane healthy; engine ALIVE rc0 idle queue0; DEC 26804c8a/ORD 9f33d953 "
    "python-raw consumed -- D-20261009-04 bigmoney items ALL closed by "
    "bm-c r801 zero re-execution anti-dup law [F-20260926-04 T-70 "
    "evidence / F-2026109-01+03 pool replenish window 10-10 bm-c lane / "
    "F-02 QA suffix receipt]; D-20261009-02 QA suffix law consumed r909; "
    "10-09 ORD MV row = BigStream domain non-BigMoney; orders double-scan "
    "unacked=0 [README non-order face]) | CUR-ACT: r914 dead-session "
    "estate absorbed (its 3 product commits landed origin pre-death: "
    "round-914 absorb 121d29e71 + W197 seat c59843acb + PARKING-P1 prereg "
    "FROZEN b904a0a0e) + this window W197 prereg build LANDED same round | "
    "LAST-ARTIFACT: research/PERPETUAL_N1_W197_PREREG.md @ origin 363cd51df "
    "(21,193B/64-line CRLF; bands A 448_204..450_203 staircase "
    "FIFTY-SEVENTH + B 450_204..450_403 W141 mutual-exclusion; "
    "anchor=W196 finalize actuals 845,545/429,120 per r590; proj ledger "
    "847,745/K 431,320 naive; REG_N 195 band zero-overlap; banned-gate "
    "ADMIT rc0) + research/PARKING_P1_PREREG.md @ b904a0a0e (dead-session "
    "12:11; three-arm A treasury/B cb-ETF/C cash-baseline 24 cells; due "
    "10-14 12:00 met early) | NEXT-MILESTONE: r915=W197 five-face freeze "
    "(r912/r909 bloodline direct-author roll: pf N1_BANDS[197] + n1 "
    "WAVE_CONFIGS[197] + materializer face; engine self-ignite 2-tick "
    "r535; window <=24h from seat 11:59) + 10-09 15:30 bars -> evening "
    "marks chain (REGIME_GUARD enforce + live.paper + t35/t24 family); "
    "PARKING-P1 burn due 10-14 12:00; 月界首考 10-31 | did: S0-1 anchored "
    "bm-a + orphan probe 0 (32 py faces 0 orphans, read-only) + S0 fetch "
    "0/0 + dead-estate diagnosis (3 commits on origin 11:55-12:11, "
    "closeout unwritten -> this window completes per r899 law) + push "
    "race vs bm-c r800/801 (14-commit advance) resolved: churn-absorb "
    "afecd821f + rebase onto 5dea67a32 + 5-UU shared regen faces via "
    "_r914bma_resolve.py (3 take-mine newer-wins 12:1x vs 12:02 + regime "
    "triggers/transitions/history union zero-loss + compute_audit "
    "history-union 201+201->203 zero-loss latest MINE) + rebase-continue "
    "zero-UU refusal x2 (EngineTick saturation-face unstaged churn "
    "window) cured by atomic add -u + continue same-shell per r787 law + "
    "push 5dea67a32..056507483 0/0 self-verified + S0.5 orders double-scan "
    "unacked=0 (56 files vs 192 ack) + 2 inbox MSGs (w197-seat + "
    "parking-p1-claim) self-acked archived processed + DEC/ORD python-raw "
    "recompute CHANGED consumed zero-new-BigMoney-action + S1 smoke 49/49 "
    "+ S2 boards empty (job_list 0; no unclaimed tickets) + S3 main "
    "product W197 prereg build: buildgen _r914bma_w197_buildgen.py (r911 "
    "bloodline rolled one generation: live facts ALL GREEN -- probe r914 "
    "ADMIT leg0 194 rows tail=W196 ordinal 187 bma_ordinal 112 + W196 "
    "actuals asserted from n1_w196_results.json [K 429,120/ledger "
    "845,545/mu -0.0928/w-only -0.0904/sigma 0.245081/p95 0.3267/K-lift "
    "+0.0001/line 1.1874->1.1875/se_mu 0.000374] + W195/W196 freeze "
    "hashes b9b962672/02cf6b44d pickaxe + seat c59843acb + W197 origin "
    "vacancy + REG_N 195 zero-overlap + BACK196 old sides 40 pairs "
    "machine-extracted via ast eval two-generation chain [BACK195 from "
    "r908 BACK with W194 actuals; BACK196 from r911 BACK with W195 "
    "actuals] zero transcribe + DRY 40/40 count==1 progressive + stale "
    "sweep 40+ CLEAN + chain-mid legal asserts) -> driver emitted "
    "_r914bma_w197_prereg_build.py 24,519B -> prereg written 21,193B "
    "CRLF roundtrip assert -> banned_direction_gate ADMIT rc0 zero hits "
    "-> product commit 363cd51df (rebased) + S6 38-leg rc0 bad NONE "
    "(_r914bma_s6_driver.py r900 bloodline rolled: update_options leg "
    "SKIPPED per CEO kill order O-20261009-1105 sec1.2 r913 precedent; "
    "new_bar=False panel 10-08 pre-15:30 honest no-op family; dualrun "
    "ZERO-DRIFT streak 51 418 entries; strategy_scorecard 72.7s; "
    "REPORT/LIVE-2026-10-09 + scorecards + dashboards regenerated; "
    "collectors no-op/throttled; token L2 0) + S7 engine ALIVE rc0 idle "
    "queue0 + attrition CLEAN (4 ledgers, healed notes historical) + "
    "quartet GREEN (loop pin=8 no-op first-fire 12:48 / watchdog "
    "re-registered -Force 12:41 / precommit+prepush claws installed "
    "LF-normalized) + idle_trigger --worked + state 913->914 + heartbeat "
    "refresh epoch-int self-verified + r913 report line relocated "
    "legacy->canonical ROOT (dead-session misplacement heal, content in "
    "git history both faces) | verification: smoke 49/49 + buildgen "
    "facts ALL GREEN + DRY 40/40 + gate rc0 + driver post-transform "
    "asserts PASS + S6 bad NONE + attrition CLEAN + quartet GREEN + "
    "engine ALIVE rc0 + push 0/0 @ 056507483 self-verified (post-push "
    "fetch+rev-list) | scoring: 2 (W197 prereg = runnable science "
    "artifact on origin; PARKING-P1 frozen prereg = dead-session product "
    "landed; supply line continuous) | bookkeeping: 5/5 (state + report "
    "lines [r913 heal + r914] + heartbeat + inbox archive + S6 receipt) "
    "| treasure-capture: no new method no new treasure (buildgen = "
    "r911/r908/r904 bloodline verbatim one-generation roll; 5-UU "
    "resolution = r907/r910 face-law reuse; rebase-continue churn window "
    "= r787 atomic law as canon'd; TREASURE/METHODOLOGY zero append) | "
    "orphan_face=0 | unacked_orders=0 | local_vs_origin=0 | token: L1 "
    "zero API (token_meter delta=0) | [r914 bm-a]")

rep_path = "round_reports-bm-a.md"
rep = io.open(rep_path, encoding="utf-8", newline="").read()
assert "r914 bm-a]" not in rep, "r914 line already present"
assert rep.count("\r\n") > 0, "ROOT report expected CRLF"
assert not rep.endswith("\n") or rep.endswith("\r\n")
if not rep.endswith("\r\n"):
    rep += "\r\n"
rep += r913_line + "\r\n" + R914 + "\r\n"
io.open(rep_path, "w", encoding="utf-8", newline="").write(rep)
print("report: r913 healed + r914 appended; bytes now",
      len(rep.encode("utf-8")))

# --- 2) inbox MSG archive -------------------------------------------------
for m in ("MSG-2026-10-09-1159-bma-w197-seat.md",
          "MSG-2026-10-09-1205-bma-parking-p1-claim.md"):
    src = os.path.join("fleet/inbox", m)
    dst = os.path.join("fleet/inbox/processed", m)
    assert os.path.exists(src), src
    shutil.move(src, dst)
    print("archived", m)

# --- 3) state update ------------------------------------------------------
st = json.load(io.open("state-bm-a.json", encoding="utf-8"))
st["round_no"] = 914
st["round"] = 914
st["loop_round"] = 914
st["last_round"] = 913
st["clock_read"] = clock
st["ts"] = stamp
st["updated"] = stamp
st["last_round_at"] = stamp
st["last_round_ts"] = stamp
st["last_run"] = stamp
st["last_seen"] = stamp
st["last_round_closed"] = stamp
st["did"] = (
    "r914: dead-session estate absorbed (3 commits on origin pre-death: "
    "absorb 121d29e71 + W197 seat c59843acb + PARKING-P1 FROZEN "
    "b904a0a0e) + W197 prereg build LANDED (363cd51df; buildgen DRY "
    "40/40; anchor W196 845,545/429,120; bands A 448_204..450_203 "
    "staircase 57th / B 450_204..450_403; banned-gate ADMIT) + "
    "rebase 5-UU face-law resolve + push 0/0 @ 056507483 + S6 38-leg "
    "rc0 (options-skip honored) + S7 quartet green + DEC/ORD consumed "
    "26804c8a/9f33d953 (zero new BigMoney action) + r913 report line "
    "healed to canonical ROOT")
st["last_action"] = "r914 closeout: W197 prereg build + estate absorb + push 0/0"
st["last_artifact"] = (
    "r914 products: research/PERPETUAL_N1_W197_PREREG.md (363cd51df) + "
    "research/PARKING_P1_PREREG.md (b904a0a0e, dead-session) + "
    "results/_r914bma_w197_* buildgen/driver/src family")
st["latest_artifact"] = st["last_artifact"]
st["current"] = ("r914 closed: dead-estate absorbed + W197 prereg built "
                 "+ PARKING-P1 frozen; next = W197 five-face freeze")
st["now_active"] = st["current"]
st["current_task"] = (
    "r915: W197 five-face freeze (r912/r909 bloodline direct-author roll: "
    "pf N1_BANDS[197] a=448_204..450_203 b_exit=450_204..450_403 + n1 "
    "WAVE_CONFIGS[197] + materializer face + selftest claim; engine "
    "self-ignite 2-tick r535; window <=24h from seat 11:59) + 10-09 "
    "15:30 bars -> evening marks chain (REGIME_GUARD enforce + live.paper "
    "+ t35/t24 family); PARKING-P1 burn due 10-14 12:00 (O-20261009-1105)")
st["task"] = st["current_task"]
st["next"] = st["current_task"]
st["next_milestone"] = st["current_task"]
st["heartbeat_epoch_utc"] = epoch
st["last_heartbeat_epoch_utc"] = st.get("heartbeat_epoch_utc", epoch)
st["last_decisions_sha"] = DEC_SHA
st["last_orders_sha"] = ORD_SHA
st["last_decisions_at"] = stamp
st["last_orders_at"] = stamp
st["last_decisions_ts"] = stamp
st["last_orders_ts"] = stamp
st["last_decisions_seen"] = (
    "r914 recompute: DEC 26804c8a CHANGED consumed -- D-20261009-04 "
    "bigmoney items ALL closed by bm-c r801 (anti-dup zero re-execution); "
    "D-20261009-02 QA suffix law consumed r909; zero new BigMoney action")
st["last_orders_seen"] = (
    "r914 recompute: ORD 9f33d953 CHANGED consumed -- 10-09 new rows = MV "
    "domain (BigStream, non-BigMoney); bigmoney dispatch faces all closed")
st["last_decisions_src"] = ("group origin/main via C: real-path "
                            "(C:/Users/sjs20/Desktop/FluxGroup) fetch + "
                            "git show (python subprocess raw-bytes "
                            "canonical)")
st["idle_rounds"] = 0
st["agenda_starved"] = False
st["verify"] = (
    "smoke 49/49 + buildgen facts ALL GREEN + DRY 40/40 + driver "
    "post-transform asserts PASS + banned-gate ADMIT rc0 + S6 38-leg bad "
    "NONE (options-skip honored) + attrition CLEAN + quartet GREEN + "
    "engine ALIVE rc0 idle + push 0/0 @ 056507483 self-verified + "
    "DEC/ORD python-raw consumed (26804c8a/9f33d953)")
st["sync"] = {"ts": stamp, "origin_tip": "056507483",
              "ahead_behind": "0/0",
              "note": "r914 mid-round push race resolved (churn-absorb + "
                      "rebase 5-UU face-law); closeout push this window"}
st["push_verified"] = {"ts": "TBD-closeout-push", "origin_tip": "TBD",
                       "ahead_behind": "0/0",
                       "note": "r914 closeout push (final commit pending "
                               "this writer)"}
json.dump(st, io.open("state-bm-a.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("state: round_no ->", st["round_no"])

# --- 4) heartbeat update --------------------------------------------------
hb = json.load(io.open("fleet/machines/bm-a.json", encoding="utf-8"))
hb["clock_read"] = clock
hb["ts"] = stamp
hb["last_seen"] = stamp
hb["last_run"] = stamp
hb["heartbeat_epoch_utc"] = epoch
hb["last_heartbeat_epoch_utc"] = st["last_heartbeat_epoch_utc"]
hb["round_no"] = 914
hb["round"] = 914
hb["loop_round"] = 914
hb["last_round"] = 913
hb["current"] = st["current"]
hb["now_active"] = st["current"]
hb["current_task"] = st["current_task"]
hb["task"] = st["current_task"]
hb["next"] = st["current_task"]
hb["next_milestone"] = st["current_task"]
hb["did"] = st["did"]
hb["last_action"] = st["last_action"]
hb["last_artifact"] = st["last_artifact"]
hb["latest_artifact"] = st["last_artifact"]
hb["last_decisions_sha"] = DEC_SHA
hb["last_orders_sha"] = ORD_SHA
hb["last_decisions_at"] = stamp
hb["last_orders_at"] = stamp
hb["last_decisions_seen"] = st["last_decisions_seen"]
hb["last_orders_seen"] = st["last_orders_seen"]
hb["verdict"] = ("green (red=false; engine ALIVE rc0 idle queue0; "
                 "py_low_board_clear legal idle whitelist + own "
                 "never-dry lane W197 five-face freeze queued next "
                 "round; ORD/DEC python-raw consumed "
                 "26804c8a/9f33d953 zero new BigMoney action)")
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["orphan_faces"] = 0
hb["orphan_killed"] = 0
for m in ("MSG-2026-10-09-1159-bma-w197-seat.md",
          "MSG-2026-10-09-1205-bma-parking-p1-claim.md"):
    if m not in hb["orders_ack"]:
        hb["orders_ack"].append(m)
if cpu_pct is not None:
    for k in ("cpu_pct", "cpu_load_pct", "cpu_total_pct", "cpu_util_pct"):
        hb[k] = cpu_pct
if ram_gb is not None:
    hb["free_ram_gb"] = ram_gb
    hb["idle_ram_gb"] = ram_gb
    hb["ram_free_gb"] = ram_gb
if vram_gb is not None:
    for k in ("gpu_free_vram_gb", "gpu_idle_vram_gb", "vram_free_gb",
              "gpu_vram_free_gb", "idle_vram_gb", "idle_gpu_vram_gb",
              "gpu_free_vram", "gpu_idle_vram"):
        hb[k] = vram_gb
    hb["gpu_free_vram_mb"] = int(vram_gb * 1024)
    hb["gpu_idle_vram_mb"] = int(vram_gb * 1024)
    hb["vram_free_mb"] = int(vram_gb * 1024)
json.dump(hb, io.open("fleet/machines/bm-a.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

# --- self-checks -----------------------------------------------------------
hb2 = json.load(io.open("fleet/machines/bm-a.json", encoding="utf-8"))
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch not int!"
assert "T" in hb2["clock_read"] and "+" in hb2["clock_read"], "clock fmt"
st2 = json.load(io.open("state-bm-a.json", encoding="utf-8"))
assert st2["round_no"] == 914 and isinstance(st2["heartbeat_epoch_utc"], int)
rep2 = io.open(rep_path, encoding="utf-8", newline="").read()
assert rep2.count("[r914 bm-a]") == 1 and rep2.count("[r913 bm-a]") == 1
assert "[r910 bm-a]" in rep2
print("self-checks PASS: epoch int, clock T-fmt, round 914, report lines")
print("closeout writes complete")
