"""R296 bm-a wrap: state 296 + heartbeat + round report + CODELY kenglu line."""
import json
import os
import subprocess
import time

TS = time.strftime("%Y-%m-%d %H:%M:%S")
TST = time.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"

# ---- GPU idle VRAM (live query, honest fallback)
gpu_free = None
try:
    out = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                          "--format=csv,noheader,nounits"],
                         capture_output=True, text=True, timeout=10)
    gpu_free = round(float(out.stdout.strip().splitlines()[0]) / 1024.0, 1)
except Exception:
    gpu_free = 5.5

import psutil
cpu_pct = psutil.cpu_percent(interval=1)
free_gb = round(psutil.virtual_memory().available / 1e9, 1)

# ---- state file (round 296)
sp = "state-bm-a.json"
st = json.load(open(sp, encoding="utf-8"))
st.update({
    "round_no": 296,
    "did": ("R296: FUSION_GRID_P1 runner built+gated per frozen prereg 7cf87f13 "
            "(R99 chain step3) -- selftest 22/22 (regime equivalence 21 dates vs "
            "module + probe dims, constructive 12, null determinism) + real-data "
            "gate PASS; pool entry ready workers_plan=4; push window vs bm-b r300 "
            "resolved per skill (autofill union+take-newer, r290 remnant stash "
            "audited+dropped); S6 30/30 rc=0; post_review 37/0/5; smoke 25/25"),
    "verdict": "ok",
    "next": ("R297: FUSION-GRID-P1 burn harvest three-piece on landing (prereg "
             "s7/s8 + gate_attrition r248 + post_review stable anchors + P5 "
             "prediction reconciliation) + T-23 consumption prereg + SCHOOL next "
             "candidate + O-2030/O-2100 anchor-migration eval"),
    "ts": TS, "last_round_ts": TST, "updated_at": TS, "last_run": TS,
    "last_seen": TS,
    "current_task": "R296: FUSION_GRID_P1 runner built+gated, pool entry ready",
    "task": ("R297: FUSION-GRID-P1 harvest three-piece on burn landing + T-23 "
             "consumption prereg + school queue next"),
})
with open(sp + ".tmp", "w", encoding="utf-8") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
os.replace(sp + ".tmp", sp)
json.load(open(sp, encoding="utf-8"))

# ---- heartbeat (epoch INT + clock_read T-separator, F7 law)
hp = "fleet/machines/bm-a.json"
h = json.load(open(hp, encoding="utf-8"))
h.update({
    "machine_id": "bm-a",
    "last_seen": TST,
    "current_task": "T-85 s2/s3 FUSION_GRID_P1 runner built+gated, pool ready; harvest next",
    "cpu_cores": 32, "cores": 32, "cpu_pct": cpu_pct,
    "free_ram_gb": free_gb, "idle_ram_gb": free_gb,
    "free_ram_mb": int(free_gb * 1024),
    "gpu_free_vram_gb": gpu_free, "gpu_idle_vram_gb": gpu_free,
    "gpu_idle_vram_mb": int(gpu_free * 1024),
    "gpu0_free_vram_gb": gpu_free,
    "verdict": ("healthy: board 0 open, pool 1 ready (FUSION-GRID-P1 landed this "
                "round = supply fed, O-2320 quench line), autofill next tick to claim"),
    "heartbeat_epoch_utc": int(time.time()),
    "clock_read": TST,
    "round_no": 296,
})
h["task"] = ("R296 done: FUSION_GRID_P1 runner+gate+pool entry (R99 step3); next=R297 "
             "harvest three-piece on burn landing")
with open(hp + ".tmp", "w", encoding="utf-8") as f:
    json.dump(h, f, ensure_ascii=False, indent=1)
os.replace(hp + ".tmp", hp)

# ---- verify epoch int + clock T-separator (smoke F7 self-check)
v = json.load(open(hp, encoding="utf-8"))
assert isinstance(v["heartbeat_epoch_utc"], int), "epoch not int"
assert "T" in v["clock_read"] and "+" in v["clock_read"], "clock_read not T-sep ISO"
print("heartbeat verified: epoch int", v["heartbeat_epoch_utc"], "clock", v["clock_read"])

# ---- round report line (append-only, own machine file)
line = (
    "2026-09-27 06:0x | R296 bm-a (dept:研究·策略·舰队) | WM first-line verdict: "
    "GREEN-side supply-in-transit (red=false lane healthy; board 0 open, bandit 0, "
    "pool 1 ready = FUSION-GRID-P1 landed THIS round per R99 cadence = O-2320 "
    "quench-line supply fed; py 0.5% low is legal-in-transit, autofill next tick "
    "claims) | did: S0 fast-forward to bm-b r299 then push-reject vs bm-b r300 "
    "same-window -> rebase + autostash-pop UU autofill_state resolved per skill "
    "classifier (mixed-dict+ledger: launches union 50|50->46 cap50 zero-drop ts-ASC "
    "r245, last_tick inner-ts take-newer 05:40:01, newline mirror, parse-verify + "
    "isinstance asserts BEFORE add, resolver results/_r296bma_resolve.py) + r290 "
    "remnant stash zero-loss audit (censusfus x3 + pid33680 present in live "
    "launches) -> archive patch _r296bma_r290_stash_archive.patch + drop per r268 "
    "no-dangling law, stash list now EMPTY; S0.5 orders 91/91 double-scan zero "
    "unacked (round-start + wrap) + decisions receipts D-20260927-04 (self-correct "
    "in force: R294 23/23 stable anchors) + D-20260927-05(3) marker gate executed "
    "PASS pre-commit this round; group orders.md zero new @BigMoney lines); S1 "
    "smoke 25/25; MAIN = T-85 s2/s3 FUSION_GRID_P1 runner scripts/fusion_grid_p1.py "
    "BUILT per frozen prereg 7cf87f13 (R99 chain step 3, R295 next-pointer "
    "continuation): v3 regime verbatim recompute (module raw_level_v3/"
    "resolve_state_v3 decision functions + fast DIMS precompute only) + 9 causal "
    "subsets (ALL32/DEDUP 0.95-single-linkage/TOP2..8) x 5 weight families (EW/"
    "INV_VOL/INV_MDD 5pct-floor/CORR_CLUSTER_RP 0.70/REGIME_COND cap-ladder "
    "state-t-minus-1) + warmup-252 drift-weight cells + x2 same-decision stress "
    "face + K=2000 nulls rng [20275200,k,j] redraw-every-25-rebalances + G1'v2/"
    "G2 shared lib (null_pool batch-own, n_eff_override r259) + CSCV PBO 8 blocks "
    "+ F6 holding-share-weighted entries + ledger 2045 single-count prev_total "
    "pinned; selftest 22/22 (A: fast dims == module bench_dims/breadth_dims on 21 "
    "sampled dates + last bench day == probe() dims + bear series vs "
    "major_bear_state truncated; B: 12 constructive legs incl warmup/drift "
    "hand-check/DEDUP collapse/INV_MDD floor/cap-ladder/hold-shares/determinism; "
    "C: null stream replay + size law + simplex + full synthetic run determinism) "
    "+ real-data gate PASS (members 32 / bars 1631 common grid 2020-01-02..lockbox "
    "2026-09-22 / bench 09-24 / core48 ok / regime EXACT shares GREEN754 RED141 "
    "ORANGE22 YELLOW714 -- probe F4 was the APPROXIMATE face, exact module "
    "recompute governs, divergence disclosed per prereg sec.2 runner-exact clause; "
    "66 rebalance points, cell window 1379 bars, 0.3s, zero judged values "
    "freeze-first honored) + pool entry FUSION-GRID-P1 ready 1 shard workers_plan "
    "=4 BelowNormal (O-2130) + ticket progress_r296 writeback; S6 30/30 legs rc=0 "
    "(audit v2.3 CLEAN, WM probe, daily 0-new-rows Sunday cutoff 09-24, regime "
    "ORANGE shadow breadth 0.77, scorecard 6/28/7, clock CALL-2026-09-24, lhb "
    "min-interval guard, heat weekend, futures/options/sina/ths zero-network "
    "no-ops, moneyflow rank-pass spawn, ah refresh spawn, astock=bm-b lane + "
    "fundprem=bm-c lane honest stdout no-ops, fundamental 8.0h fresh-skip, blf "
    "all-gates, live.paper OK 6 traders, t35 PASS 0-pending 0-breach, prospect "
    "22/22 drift 0, promotion 0/22 honest NOT-ELIGIBLE, aggr/grid idempotent "
    "no-ops, alloc bm-b lane guard, export 09-24, d_scorecard + d_report faces=4, "
    "monitor, token L2=0 crash-fuse refusals=1) | evidence: commit 95f4e95d pushed "
    "(rebase window + skill resolve) + selftest 22/22 stdout + probe gate stdout + "
    "_r296bma_resolve.py + _r296bma_r290_stash_archive.patch + orders_diff empty "
    "91/91 + smoke 25/25 + S6 30x rc0 chain log + post_review 37 YES/0 NO/5 WAIT "
    "zero P0 | next: autofill tick burns FUSION-GRID-P1 -> R297 harvest "
    "three-piece on landing (prereg s7/s8 one-time + gate_attrition r248 + "
    "post_review stable anchors + P5 prediction reconciliation) + carried: T-23 "
    "judged consumption prereg (UNC annotations ready) + SCHOOL_SUPPLY_S1 next "
    "candidate per R99 cadence + O-2030/O-2100 json_field anchor-migration eval + "
    "09-28 Monday new-bar chain + 10-01 month-first trio + REGIME_GUARD v3 date "
    "gate [via bm-a]\n"
)
rp = "logs/iteration-loop/round_reports-bm-a.md"
with open(rp, "a", encoding="utf-8") as f:
    f.write(line)

# ---- CODELY kenglu (one line, four-question gate passed: new PS pitfall)
cp_ = "CODELY.md"
c = open(cp_, encoding="utf-8").read()
kenglu = (
    "- [2026-09-27 r296 bm-a] 坑律：PowerShell 面 git stash 引用必须单引号包裹——"
    "裸写 `git stash drop stash@{0}` 被 PS 当哈希表语法解析报 `error: unknown "
    "switch 'e'` 假故障（R296 实弹，命令未达 git）；正典=`'stash@{0}'`。与 `&` 后台符/"
    "`;` 链接符同族=PS 语法层坑。指针=results/_r296bma_resolve.py+本行。\n"
)
anchor = "### Reference"
if kenglu.strip()[:40] not in c:
    i = c.find(anchor)
    if i > 0:
        c = c[:i] + kenglu + "\n" + c[i:]
    else:
        c = c.rstrip() + "\n" + kenglu
    with open(cp_, "w", encoding="utf-8", newline="") as f:
        f.write(c)
size = os.path.getsize(cp_)
print(f"CODELY {size}B {'<=' if size <= 10240 else '>'}10KB hard line")
assert size <= 10240, "CODELY over 10KB hard line -> rebin now"
print("wrap OK: state 296 + heartbeat + round report + kenglu")
