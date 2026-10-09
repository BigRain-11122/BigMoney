# -*- coding: utf-8 -*-
# r917 bm-a closeout writes: round report line + state-bm-a.json + heartbeat.
# Multi-writer files: fresh-read-modify-write per 2026-10-06 law (no replace).
import json, io, time, datetime, subprocess, os

NOW = datetime.datetime.now().astimezone()
TS = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())

# ---------- fresh system metrics ----------
cores = os.cpu_count() or 32
ram_free_pct = ram_free_gb = None
try:
    import psutil
    vm = psutil.virtual_memory()
    ram_free_pct = round(vm.percent and (100 - vm.percent), 1)
    ram_free_gb = round(vm.available / 1024**3, 1)
except Exception:
    pass
vram_free_gb = None
try:
    r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                        "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=20)
    if r.returncode == 0 and r.stdout.strip():
        vram_free_gb = round(float(r.stdout.strip().splitlines()[0]) / 1024, 2)
except Exception:
    pass
if ram_free_pct is None:
    d = json.load(io.open("results/idle_trigger.bm-a.json", encoding="utf-8"))
    ram_free_pct = d.get("ram_free_pct"); ram_free_gb = d.get("ram_free_gb") or round((d.get("ram_free_pct") or 0) * 0.01 * 31.8, 1)
if vram_free_gb is None:
    d = json.load(io.open("results/idle_trigger.bm-a.json", encoding="utf-8"))
    vram_free_gb = d.get("vram_free_gb")

REPORT = ("2026-10-09T14:__MIN__:00+08:00 | r917 | bm-a | dept:research (S0 double rebase storm closeout + W198 finalize one-pass; N1 perpetual supply line) | "
          "WM-VERDICT: green (red=false lane healthy; engine ALIVE rc0 idle queue0 post-W198 finalize; DEC bd94a27b python-raw UNCHANGED zero action; "
          "ORD b6ea34b1->b38eaaf8 delta consumed = O-20261009-1430 fleet-comms order [HQ-executed, zero BigMoney dispatch action]; orders double-scan unacked=0; "
          "orphan faces=0) | "
          "CUR-ACT: inherited r916 mid-rebase (pick 1/3 staged 70 files, 12 UU resolved per canon) -> completed 3-pick replay with churn-absorb dance -> "
          "origin advanced again (bm-c r805/806 500d8e4d4+aaaedec96) -> second storm resolved (25 shared S6 faces + 7 engine/paper live faces, union/newest-ts/dict-union, "
          "marker-free-WT three-state law) -> W198 pre-finalize probe 13/13 GREEN -> finalize one-pass LANDED -> sec7/8 machine backfill | "
          "LAST-ARTIFACT: results/perpetual_faces/n1_w198_results.json (ledger 849,945 EXACT five-window streak = 847,745+2,200; K=433,520; four pred keys 4/4 PASS: "
          "mu |w-only -0.097125 vs merged -0.092800| =0.004325<0.02 / sigma 0.2450971 vs 0.2450943 =+0.0012%<10% / A full_sharpe_p95 0.3279 vs 0.3307 =0.0028<0.05 / "
          "skill_line_v2 K-lift +0.0000 [1.1878->1.1878]; se_mu chain 0.000373->0.000372; canon flip NOT performed per K2200 law) + research/PERPETUAL_N1_W198_PREREG.md sec7/8 backfilled "
          "+ results/_r917bma_w198_prefinalize_probe.json | "
          "NEXT-MILESTONE: 10-09 15:30 bars -> evening marks chain (REGIME_GUARD enforce + live.paper + t35_open_fill/t24 family) same day; PARKING-P1 burn due 10-14 12:00 (O-20261009-1105) | "
          "did: S0-1 anchored bm-a + orphan probe 0/16 faces + S0 double-storm canon closeout (r916 _r916bma_resolve_rebase.py 12-UU resolutions honored + "
          "_r917bma_rebase_pick2/pick3/origin_resolve/pick2/pick4 resolvers; push d4ea4b348 fetch+rev-list self-verified ahead=0) + S0.5 ORD watermark consume "
          "(b38eaaf8; new row O-20261009-1430 = bm-b offline CEO physical item + BigHouse repo absence -- zero BigMoney action; DEC bd94a27b unchanged) + "
          "S1 smoke 49/49 + S3 W198 finalize (honest disclosure: prereg sec0 projection text 433,540 = arithmetic typo +20 vs actual 433,520; "
          "prereg runtime-registry-derive immunity clause held, zero result impact, disclosed not rewritten) + treasure/methodology capture: zero new (routine wave, "
          "verbatim-roll reuse) + pit direct-write research/pit-git-resolver-rebase.md r917 entry (live-face three-state marker law) + "
          "S6 38-leg rc0 bad NONE (r916 driver reuse; panel 10-08 pre-15:30 honest no-op family; options-skip per O-20261009-1105) + "
          "attrition guard CLEAN + quartet GREEN (loop pin=8 no-op / watchdog registered / claws installed) | "
          "verify: smoke 49/49 + probe 13/13 GREEN_FINALIZE_READY + finalize ledger 849,945 EXACT + four keys 4/4 + S6 38 rc0 + push self-verified + "
          "local behind origin = 0 | "
          "next: evening marks chain after 15:30 bars; PARKING-P1 burn window opens 10-14 12:00"
          ).replace("__MIN__", "%02d" % NOW.minute)

with io.open("round_reports-bm-a.md", "a", encoding="utf-8", newline="") as f:
    f.write(REPORT + "\n")
print("report line appended")

# ---------- state-bm-a.json ----------
p = "state-bm-a.json"
st = json.load(io.open(p, encoding="utf-8"))
st["last_round"] = 916
st["round_no"] = 917
st["round"] = 917
st["loop_round"] = 917
for k in ("ts", "updated", "last_seen", "last_run", "last_round_at", "last_round_ts",
          "last_round_closed", "last_orders_at", "last_decisions_at", "clock_read"):
    st[k] = TS
st["current_task"] = ("r918: 10-09 15:30 bars -> evening marks chain (REGIME_GUARD enforce + live.paper + t35/t24 family + evening S6 rerun); "
                      "PARKING-P1 burn due 10-14 12:00 (O-20261009-1105)")
st["task"] = st["current_task"]
st["next"] = st["current_task"]
st["next_milestone"] = st["current_task"]
st["did"] = ("r917: S0 double rebase storm closeout (r916 inherited pick-1/3 + origin bm-c r805/806 advance; 12+25+7+4 faces union/newest-ts canon; "
             "push d4ea4b348 self-verified) + W198 finalize one-pass (probe 13/13 GREEN; ledger 849,945 EXACT; K=433,520; four pred keys 4/4 PASS; "
             "sec7/8 machine backfill; honest projection-typo disclosure) + S6 38-leg rc0 bad NONE + attrition CLEAN + quartet GREEN")
st["current"] = "r917 closed: W198 finalize landed (ledger 849,945 EXACT, four keys 4/4); S0 double storm resolved"
st["now_active"] = st["current"]
st["last_action"] = "r917 closeout: W198 finalize + sec7/8 backfill + S0 storms closed; push self-verified"
artifact = ("r917 products: results/perpetual_faces/n1_w198_results.json (ledger 849,945 EXACT, K=433,520, four keys 4/4) + "
            "research/PERPETUAL_N1_W198_PREREG.md sec7/8 backfilled + results/_r917bma_w198_prefinalize_probe.json + "
            "research/pit-git-resolver-rebase.md r917 entry")
st["last_artifact"] = artifact
st["latest_artifact"] = artifact
st["last_round_at_"] = "2026-10-09T14:17:17+08:00"
st["verify"] = ("smoke 49/49 + pre-finalize probe 13/13 GREEN + finalize ledger 849,945 EXACT (847,745+2,200) + four pred keys 4/4 PASS + "
                "S6 38-leg rc0 bad NONE + attrition CLEAN + quartet GREEN + DEC bd94a27b/ORD b38eaaf8 python-raw consumed + push fetch+rev-list self-verified")
st["idle_rounds"] = 0
st["agenda_starved"] = False
st["orphan_faces"] = 0
st["last_orders_sha"] = "b38eaaf8aec9e64c" + "00000000000000000000000000000000"[:32]
# full sha for orders watermark (r917 consumption)
import hashlib, subprocess as sp
G = r"C:\Program Files\Git\cmd\git.exe"
R = r"C:\Users\sjs20\Desktop\FluxGroup"
b = sp.run([G, "-C", R, "show", "origin/main:docs/orders.md"], capture_output=True).stdout
st["last_orders_sha"] = hashlib.sha256(b).hexdigest()
st["last_orders_seen"] = "r917 recompute: ORD b38eaaf8 delta vs r916 b6ea34b1 = new row O-20261009-1430 (fleet Tailscale comms; HQ-executed; zero BigMoney dispatch action); consumed"
st["last_orders_ts"] = TS
st["last_decisions_seen"] = "r917 recompute: DEC bd94a27b UNCHANGED vs r916 consumption -- zero delta; zero action"
st["last_decisions_ts"] = TS
st["heartbeat_epoch_utc"] = EPOCH
st["last_heartbeat_epoch_utc"] = EPOCH
st["push_verified"] = {"ts": TS, "origin_tip": "d4ea4b348", "ahead_behind": "0/0",
                      "note": "r917 closeout: S0 double-storm integration push self-verified post-push fetch+rev-list"}
st["sync"] = st["push_verified"]
json.dump(st, io.open(p, "w", encoding="utf-8", newline=""), ensure_ascii=False, indent=1)
print("state written")

# ---------- heartbeat ----------
p = "fleet/machines/bm-a.json"
hb = json.load(io.open(p, encoding="utf-8"))
hb["round_no"] = 917
hb["round"] = 917
hb["loop_round"] = 917
hb["last_round"] = 916
for k in ("ts", "last_seen", "last_run", "last_orders_at", "last_decisions_at", "clock_read"):
    hb[k] = TS
hb["current_task"] = st["current_task"]
hb["current"] = st["current"]
hb["now_active"] = st["current"]
hb["did"] = st["did"]
hb["last_action"] = st["last_action"]
hb["last_artifact"] = artifact
hb["latest_artifact"] = artifact
hb["next"] = st["current_task"]
hb["next_milestone"] = st["current_task"]
hb["verdict"] = "green (r917 closed: W198 finalize landed 849,945 EXACT four keys 4/4; S0 double storm closed)"
hb["cores"] = cores
hb["cpu_cores"] = cores
hb["ram_free_pct"] = ram_free_pct
hb["free_ram_pct"] = ram_free_pct
hb["ram_free_gb"] = ram_free_gb
hb["free_ram_gb"] = ram_free_gb
hb["idle_ram_gb"] = ram_free_gb
hb["vram_free_gb"] = vram_free_gb
hb["gpu_free_vram_gb"] = vram_free_gb
hb["gpu0_free_vram_gb"] = vram_free_gb
hb["idle_vram_gb"] = vram_free_gb
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["orphan_faces"] = 0
hb["heartbeat_epoch_utc"] = EPOCH
hb["heartbeat_epoch_utc_type_int"] = isinstance(EPOCH, int)
hb["last_heartbeat_epoch_utc"] = EPOCH
hb["last_orders_sha"] = st["last_orders_sha"]
hb["last_orders_seen"] = st["last_orders_seen"]
hb["last_decisions_sha"] = st.get("last_decisions_sha")
hb["last_decisions_seen"] = st["last_decisions_seen"]
oa = hb.get("orders_ack") or []
for f in ("O-20261009-1105-bm-a.md",):
    if f not in oa:
        oa.append(f)
hb["orders_ack"] = oa
hb["push_verified"] = st["push_verified"]
hb["sync"] = st["sync"]
json.dump(hb, io.open(p, "w", encoding="utf-8", newline=""), ensure_ascii=False, indent=1)

# post-write self-assert (R170/R178 law: epoch must be JSON int)
chk = json.load(io.open(p, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch not int"
assert isinstance(chk["idle_rounds"], int), "idle_rounds not int"
assert isinstance(chk["agenda_starved"], bool), "agenda_starved not bool"
assert "T" in chk["clock_read"], "clock_read not T-separated"
print("heartbeat written + self-asserted (epoch int=%d)" % EPOCH)
print("metrics: cores=%s ram_free=%s%%/%sGB vram_free=%sGB" % (cores, ram_free_pct, ram_free_gb, vram_free_gb))
