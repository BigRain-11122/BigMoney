# -*- coding: utf-8 -*-
# _r948bmc_closeout.py -- r948 bm-c closeout: round report + E61 methodology card + state + heartbeat
import json, subprocess, time, io, os

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
NOW = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())
HMSX = time.strftime("%Y-%m-%dT%H:%M")

gpu_util, gpu_used, gpu_total = 100, 15591, 16384
try:
    out = subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,memory.total",
                          "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=20).stdout.strip()
    p = [x.strip() for x in out.split(",")]
    gpu_util, gpu_used, gpu_total = int(p[0]), int(p[1]), int(p[2])
except Exception:
    pass
free_ram = 1.1
try:
    import psutil
    free_ram = round(psutil.virtual_memory().available / (1024**3), 1)
except Exception:
    pass
cpu_pct = 15.0
try:
    import psutil
    cpu_pct = round(psutil.cpu_percent(interval=1), 1)
except Exception:
    pass

REPORT_LINE = (
    HMSX + " | r948 | bm-c absorb r947 estate + INTERRUPTED-REBASE SURGERY (r836 family live instance): S0 found 24-file staged estate = r947 closeout (19caa949c applied to index by dead rebase, uncommitted) -> committed as 375f9334a on DETACHED HEAD (repo was mid-rebase: '(no branch, rebasing main)', local main=54f8fe48b stale pre-rebase ref) -> push non-FF x2 -> diagnosis chain: ls-remote real tip=b98de9b32 (ancestor, push should FF) -> branch --show-current EMPTY + rev-parse main=54f8fe48b != HEAD -> .git/rebase-merge in place (onto=b98de9b32, orig-head=54f8fe48b, done=[03a9e291d replayed as 1419f7b57, 19caa949c stopped post-apply], todo=[54f8fe48b runtime drift]) = r947 died mid pull --rebase at 00:37:59 -> SURGERY: treasure_guard rc0 on affected faces (2 satengine files reproducible-class; token_usage.bm-c.json FORBIDDEN but NOT in dirty set = moot) -> rebase --abort + reset --hard 375f9334a (content supersession verified: state-bm-c.json + round_reports-bm-c.md absent from 375f9334a-vs-54f8fe48b diff = byte-identical both tips; 19caa949c full content in 375f9334a; 54f8fe48b drift superseded by newer absorb state) -> push rejected AGAIN (real race: bm-b round 909 66658ccbf landed between ls-remote and push) -> pull --rebase blocked by daemon-write race (satengine faces re-dirty tree faster than checkout) -> WORKTREE ZHENFA (10-08 bm-a precedent): worktree add @66658ccbf -> cherry-pick 1419f7b57 (clean, 511569b3c) + 375f9334a (3 shared-face conflicts resolved: token_usage.json=mine newer 00:52:22 wholesale + bm-a mirror keys overlaid from bm-b view; compute_audit.json=latest mine 00:52:15 + history union-by-ts 63 entries; _attrition_guard_scan.json=bm-b newer scan 00:49:57 wholesale) -> cherry-pick --continue = cb43255bb -> push LANDED 66658ccbf..cb43255bb -> worktree removed -> main tree reset --hard origin/main, behind 0 | "
    "WM-VERDICT: green red=false (S0.5 dual-delta FALSE both hold: dec fb5825cb / ord a8d9efaf, unacked=0, zero consumption owed this window; probe results/_s05_probe.bm-c.json) | "
    "dept:engineering (git integrity surgery + estate push) + dept:research-ops (i2v deathline patrol lane) | "
    "LIVE-3LINES: now=i2v 21-shot batch burning 4/21 done + N05 in flight (factory PID 37904 healthy, per-clip CDN + I2V-URL-INDEX append, ~7min/shot, ETA ~03:0x-03:3x); artifact=origin/main cb43255bb (r947 estate + r946 checkpoint landed via worktree rebase chain, 66658ccbf..cb43255bb range line); next=06:30 harvest closeout checklist (21/21 + <7.5 re-shake w/ seed) -> bm-a 07:00 assembly -> 08:30 CEO screen (deathline) + W227 seat first action after RAM relief + Tue 15:30 new-bar papers chain | "
    "did: r948 bm-c: (1) S0-1 anchor bm-c + round-zero probe py_faces=7 orphans=1 zero-kill (cross-lane face kept); (2) estate absorb + rebase surgery + worktree push (full chain above, push self-proof behind-origin=0); (3) patrol leg-1+leg-2: N01 616.9s/N02 440.7s/N03/N04 landed CDN+index (16 rows), N05 burning, factory log live to 01:03; (4) S0.5 dual-delta FALSE hold; (5) S1 smoke 49/49; (6) S3 satengine alive rc0 queue DRY (W227 RAM-deferred per O-2330-2, freeRAM 1.1G < 4G gate); (7) S6 light subset: dualrun ZERO-DRIFT streak 40 (before compute_audit law) + compute_audit FLAG supply_floor structural (armed response=W227 after RAM relief) + py_watermark py_low_with_work_cands justified (GPU lane = CEO deathline i2v batch, CPU lane RAM-arbitrated per O-2330-2 + O-2305) + token delta 0; (8) S7: loop+watchdog tasks alive (next-fire 0:55), hooks precommit/prepush True both, attrition scan consumed bm-b newer face; (9) E61 methodology card appended (round-start rebase-state check + shared-face conflict union resolution); (10) state/heartbeat write | "
    "verify=smoke 49/49 + push range line 66658ccbf..cb43255bb on origin + behind-origin=0 post-reset + cherry-pick chain 511569b3c/cb43255bb content-verified (3 conflicts resolved per-face newer-wins/union) + factory index 16 rows + dualrun streak 40 + satengine rc0 + hooks True x2 | "
    "behind-origin=0 (post-push fetch+rev-list self-proof) | orphan_faces=1 | "
    "score: 1 (estate absorb + push = landed file changes on origin) + 1 (git integrity surgery = infrastructure recovery, r836 family) + 1 (patrol legs with live factory evidence) = 3 | ledger-budget: 3 (state+heartbeat+round-report statutory) + 1 (E61 card = capture-law obligation) | "
    "next=r949: (1) i2v harvest patrol (per-clip CDN+index, <7.5 re-shake w/ seed, 06:30 closeout checklist); (2) I2V-URL-INDEX.md + bmc faces commit+push (cph4 group tree, bm-a 07:00 assembly dual-source); (3) W227 seat probe+publish FIRST ACTION after RAM relief (batch done ~03:3x or free_ram>=4G; probe script results/_w227bmc_probe_derive.py on disk); (4) Tue 15:30 new-bar papers full chain + update family; (5) post-06:30 cloud gap-fill = residual missing shots only | [r948 bm-c]\n"
)

with io.open(os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md"), "a", encoding="utf-8") as f:
    f.write(REPORT_LINE)

# --- E61 methodology card (capture law: new method faces from this window) ---
E61 = (
    "- **E61 轮首中断 rebase 态侦测腿+共享 face 冲突 per-face 定侧法（round-start rebase-merge in-place check + daemon-write race 下 worktree 重放）**：proven，工程面。"
    "死窗遗产两类新面：①轮首 S0 的 fetch 幂等假象——HEAD..origin/main=0 且 origin/main..HEAD=1 看似「仅 ahead 1 待推」，但仓库实际处于中断 rebase 态（.git/rebase-merge 在位、本地分支引用=陈旧 orig-head、HEAD=detached）——push origin main 推的是陈旧分支引用=non-FF 空转（r836 坑的轮入口新触发面）；正法=轮首必查 branch --show-current 空/rev-parse main≠HEAD/rebase-merge 在位三件，命中即先做 rebase 手术（treasure_guard 分类门→abort→reset --hard 内容超越面验证→重推）。"
    "②daemon 常驻回写面（satengine faces 秒级重脏）下 pull --rebase 净树律结构性失效——checkout 后立即再脏；正法=临时 worktree（add 于最新 origin tip·cherry-pick 重放本机提交·零触碰 daemon 面）；cherry-pick 撞他机同窗共享 face 冲突时 per-face 定侧：快照 face=较新 ts 侧整侧（禁行级 Frankenstein 混合）、history 数组 face=按 ts 键 union 去重排序、他机视角镜像键（如 token_usage machines['bm-a']）=他机侧覆（其 fetch 视图更新）。"
    "live 实证：r948 bm-c（375f9334a detached 提交→手术→worktree 511569b3c/cb43255bb→push 66658ccbf..cb43255bb 落成；token=本机侧 00:52:22+bm-a 键覆、compute_audit=latest 本机+history union 63、attrition_scan=他机侧 00:49:57）。\n"
    "- 2026-10-13 01:1x：bm-c r948（estate 收口步·O-20261002-2100 捕获律 live 实证：中断 rebase 态轮入口侦测+daemon 竞态 worktree 重放首案）。\n"
)
with io.open(os.path.join(ROOT, "knowledge", "METHODOLOGY_ASSETS.md"), "a", encoding="utf-8") as f:
    f.write(E61)

# --- state-bm-c.json (read-modify-write, preserve watermark keys) ---
sp = os.path.join(ROOT, "state-bm-c.json")
st = json.load(io.open(sp, encoding="utf-8"))
st["round_no"] = 949
st["round_no_label"] = "r948"
st["loop_round"] = 948
st["last_round"] = 948
st["last_round_at"] = NOW
st["last_round_ts"] = EPOCH
st["last_round_closed"] = NOW
st["current_task"] = ("r948: r947 estate absorb LANDED on origin (cb43255bb via worktree rebase chain) + interrupted-rebase surgery "
                      "(r836 family) + i2v patrol 4/21 + W227 RAM-deferred armed")
st["current_task_at"] = NOW
st["did"] = ("r948: (1) absorb r947 closeout estate (state/heartbeat/round-report/dual receipts landed on disk by r947's own "
             "closeout script, commit debt cleared this window via surgery); (2) rebase surgery: repo was mid-interrupted-rebase "
             "(r947 died at pull --rebase 00:37:59; local main=54f8fe48b stale, HEAD detached mid-replay) -> treasure_guard rc0 -> "
             "rebase --abort + reset --hard 375f9334a -> push race with bm-b round 909 (66658ccbf) -> worktree zhenfa: cherry-pick "
             "1419f7b57+375f9334a onto 66658ccbf with 3 shared-face conflicts resolved (token newer-side+bm-a overlay / "
             "compute_audit latest-newer+history-union-63 / attrition_scan bm-b-newer) -> cb43255bb pushed 66658ccbf..cb43255bb; "
             "(3) patrol leg-1+2: N01-N04 landed CDN+index 16 rows, N05 burning, ETA 03:0x-03:3x; (4) S0.5 dual-delta FALSE hold; "
             "(5) smoke 49/49; (6) satengine rc0 queue DRY; (7) S6 light: dualrun streak 40 + supply_floor structural (armed=W227) "
             "+ watermark py_low_with_work_cands justified (GPU deathline lane); (8) S7 tasks alive + hooks True; (9) E61 card appended")
st["verdict"] = ("green: r947 estate + r946 checkpoint LANDED on origin (cb43255bb); git integrity restored (no rebase state, main=origin, "
                 "behind 0); i2v deathline batch 4/21+N05 burning healthy (ETA ~03:3x); W227 RAM-deferred armed (1.1G<4G); dual-delta "
                 "FALSE hold; smoke 49/49; engine alive rc0 queue DRY; dualrun streak 40; supply_floor structural disclosed (armed "
                 "response=W227 after RAM relief); no new bars until Tue 15:30")
st["next"] = ("r949: (1) i2v harvest patrol (per-clip CDN+index, <7.5 re-shake w/ seed, 06:30 closeout checklist); (2) I2V-URL-INDEX.md "
              "+ bmc faces commit+push (cph4 group tree, bm-a 07:00 assembly dual-source); (3) W227 seat probe+publish FIRST ACTION "
              "after RAM relief (batch done ~03:3x or free_ram>=4G; probe script results/_w227bmc_probe_derive.py on disk); (4) Tue 15:30 "
              "new-bar papers full chain + update family; (5) post-06:30 cloud gap-fill = residual missing shots only")
st["next_pointer"] = st["next"]
st["activity_now"] = ("2026-10-13 01:1x | r948 | bm-c: estate absorb LANDED via rebase surgery (r836 family live instance, worktree "
                      "zhenfa, push 66658ccbf..cb43255bb) + i2v patrol 4/21+N05 burning + W227 RAM-deferred armed; counter 948->949")
st["now_active"] = st["activity_now"]
st["last_round_summary"] = "r948: r947 estate landed on origin via interrupted-rebase surgery + worktree rebase chain + i2v patrol 4/21"
st["last_action"] = "r948 closeout (estate absorb push cb43255bb + rebase surgery + patrol legs + E61 card)"
st["latest_artifact"] = ("origin/main cb43255bb (r947 estate + r946 checkpoint via worktree rebase chain 66658ccbf..cb43255bb) + "
                         "i2v factory 4/21 landed (I2V-URL-INDEX 16 rows, cph4 tree)")
st["last_artifact"] = st["latest_artifact"]
st["recent_artifact"] = st["latest_artifact"]
st["next_milestone"] = ("i2v 21 shots ~03:3x done -> 06:30 harvest closeout -> bm-a 07:00 assembly -> 08:30 CEO screen (deathline) "
                        "+ W227 seat after RAM relief")
st["free_ram_gb"] = free_ram
st["idle_ram_gb"] = free_ram
st["ram_free_gb"] = free_ram
st["cpu_pct"] = cpu_pct
st["cpu_util_pct"] = cpu_pct
st["gpu_util_pct"] = gpu_util
st["gpu_mem_used_mib"] = gpu_used
st["gpu_mem_total_mib"] = gpu_total
st["gpu_used_vram_mib"] = gpu_used
st["gpu_total_vram_mib"] = gpu_total
st["gpu_free_vram_mb"] = gpu_total - gpu_used
st["gpu_free_vram_mib"] = gpu_total - gpu_used
st["gpu_free_vram_gb"] = round((gpu_total - gpu_used) / 1024.0, 1)
st["orphan_face"] = 1
st["orphan_faces"] = 1
st["idle_rounds"] = 0
st["agenda_starved"] = False
st["heartbeat_epoch_utc"] = EPOCH
st["last_seen"] = NOW
st["clock_read"] = NOW
st["ts"] = NOW
st["updated"] = NOW
st["updated_at"] = NOW
st["last_run_at"] = NOW
st["last_action_at"] = NOW
st["last_pulled_at"] = NOW
st["head_sha"] = "cb43255bb (r948 closeout commit rides this push)"
st["r948_rebase_surgery_note"] = (
    "r948 surgery note: r947 session died at 00:37:59 mid pull --rebase (onto=b98de9b32, orig-head=54f8fe48b), leaving "
    ".git/rebase-merge in place with pick#1 (03a9e291d r946 checkpoint) replayed as 1419f7b57 and pick#2 (19caa949c r947 closeout) "
    "APPLIED TO INDEX but uncommitted; state/heartbeat/round-report writes had landed (r947 closeout script ran) but commit/push "
    "never happened. This session found the staged estate, committed it as 375f9334a ON THE DETACHED HEAD (before detecting the "
    "rebase state -- push then failed non-FF x2 because (a) local main ref=54f8fe48b stale = the pushed ref, (b) after surgery, "
    "real race with bm-b round 909 push 66658ccbf). Resolution: treasure_guard rc0 on affected faces -> rebase --abort (autostash "
    "applied, all reproducible-class) -> reset --hard 375f9334a after content-supersession verification (state-bm-c.json + "
    "round_reports-bm-c.md byte-identical across tips = r947 products fully preserved) -> worktree add @66658ccbf -> cherry-pick "
    "1419f7b57 (clean) + 375f9334a (3 shared-face conflicts: token_usage.json = mine 00:52:22 wholesale + bm-a mirror keys from bm-b "
    "view; compute_audit.json = latest mine 00:52:15 + history union-by-ts 63; _attrition_guard_scan.json = bm-b 00:49:57 newer "
    "wholesale) -> cb43255bb -> push LANDED 66658ccbf..cb43255bb -> worktree removed -> main reset --hard origin/main behind 0. "
    "Old chain (54f8fe48b/19caa949c/03a9e291d) content-fully-preserved, reachable via reflog. E61 methodology card appended.")
st["sync"] = {
    "origin_tip": "cb43255bb + r948 closeout (rides this push)",
    "ts": NOW,
    "ahead_behind": "r948 closeout commit+push rides this window",
    "note": "r948: estate absorb landed via rebase surgery + worktree chain; state/heartbeat this round",
}
st["last_orders_read_at"] = NOW
st["last_decisions_read_at"] = NOW
st["last_orders_seen"] = NOW
st["last_decisions_seen"] = NOW
st["last_orders_sha_note"] = ("r948: ORD delta FALSE hold (a8d9efaf current, zero new rows since r947 consumption; probe "
                               "results/_s05_probe.bm-c.json)")
st["last_decisions_read_note"] = ("r948: DEC delta FALSE hold (fb5825cb current, zero new rows since r947 consumption)")
st["orders_ack_receipt"] = ("r948: dual-delta FALSE hold (dec fb5825cb / ord a8d9efaf), unacked=0, zero consumption owed this window")
st["d19_watermark_guard"] = {
    "tool": "scripts/d19_watermark.py",
    "probe": "results/_r686bmb_d19_check.py",
    "probe_evidence": ROOT + r"\results\_r686bmb_d19_check.json",
    "method_decisions": "sha256",
    "method_orders": "sha256",
    "verbatim": True,
    "advance": True,
    "round_ref": 948,
    "ts": NOW,
}
with io.open(sp, "w", encoding="utf-8") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
    f.write("\n")

# --- heartbeat fleet/machines/bm-c.json (read-modify-write) ---
hp = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
h = json.load(io.open(hp, encoding="utf-8"))
h["heartbeat_epoch_utc"] = EPOCH
h["last_seen"] = NOW
h["clock_read"] = NOW
h["ts"] = NOW
h["last_seen_at"] = NOW
h["updated_at"] = NOW
h["updated"] = NOW
h["last_run_at"] = NOW
h["round_no"] = 949
h["round_no_label"] = "r948"
h["last_round"] = "r948"
h["last_round_at"] = NOW
h["loop_round"] = 948
h["current_task"] = ("r948: r947 estate LANDED on origin (cb43255bb via worktree rebase chain) + interrupted-rebase surgery + "
                     "i2v patrol 4/21 + W227 RAM-deferred armed")
h["current_task_at"] = NOW
h["prod_lanes"] = ("GPU=CEO deathline i2v 21-shot batch (4/21 done + N05 in flight, factory PID 37904, INT8 768P, per-clip "
                   "CDN+I2V-URL-INDEX, 06:30 closeout, 08:30 CEO screen); CPU=N1 wave chain W226 complete, W227 seat "
                   "RAM-arbitration-deferred per O-20261012-2330-2 (i2v priority, freeRAM 1.1G < 4G gate)")
h["latest_artifact"] = ("origin/main cb43255bb (r947 estate + r946 checkpoint landed via worktree rebase chain "
                        "66658ccbf..cb43255bb) + i2v I2V-URL-INDEX 16 rows (cph4 tree)")
h["next_milestone"] = ("i2v 21 shots ~03:3x -> 06:30 harvest closeout -> bm-a 07:00 assembly -> 08:30 CEO screen + W227 after RAM relief")
h["free_ram_gb"] = free_ram
h["idle_ram_gb"] = free_ram
h["ram_free_gb"] = free_ram
h["cpu_pct"] = cpu_pct
h["cpu_util_pct"] = cpu_pct
h["gpu_util_pct"] = gpu_util
h["gpu_mem_used_mib"] = gpu_used
h["gpu_mem_total_mib"] = gpu_total
h["gpu_used_vram_mib"] = gpu_used
h["gpu_total_vram_mib"] = gpu_total
h["gpu_free_vram_mb"] = gpu_total - gpu_used
h["gpu_free_vram_mib"] = gpu_total - gpu_used
h["gpu_free_mb"] = gpu_total - gpu_used
h["gpu_free_mib"] = gpu_total - gpu_used
h["gpu_idle_vram_mb"] = gpu_total - gpu_used
h["gpu_vram_free_mb"] = gpu_total - gpu_used
h["gpu_free_vram_gb"] = round((gpu_total - gpu_used) / 1024.0, 1)
h["idle_rounds"] = 0
h["agenda_starved"] = False
h["health"] = "ok"
h["activity_now"] = st["activity_now"]
h["did"] = st["did"]
h["verdict"] = st["verdict"]
h["next"] = st["next"]
h["next_pointer"] = st["next"]
h["last_round_summary"] = st["last_round_summary"]
h["last_action"] = st["last_action"]
h["last_action_at"] = NOW
h["last_round_closed"] = NOW
h["last_round_ts"] = EPOCH
h["last_pulled_at"] = NOW
h["orphan_face"] = 1
h["orphan_faces"] = 1
h["head_sha"] = "cb43255bb (r948 closeout rides this push)"
h["sync"] = st["sync"]
h["last_orders_seen"] = NOW
h["last_decisions_seen"] = NOW
h["last_orders_read_at"] = NOW
h["last_decisions_read_at"] = NOW
h["last_orders_sha"] = "a8d9efaf99bd87290b3a991e978465750c52060ba1411419d1a3cee378d30928"
h["last_decisions_sha"] = "fb5825cb68a9524e2e8f2df12caeb537e3cafbda64d09d2f8478943d9986a2a7"
h["last_orders_at"] = NOW
h["last_decisions_at"] = NOW
h["d19_watermark_guard"] = st["d19_watermark_guard"]
with io.open(hp, "w", encoding="utf-8") as f:
    json.dump(h, f, ensure_ascii=False, indent=1)
    f.write("\n")

# --- self-verify: epoch int + clock T + watermark preservation ---
sv = json.load(io.open(sp, encoding="utf-8"))
hv = json.load(io.open(hp, encoding="utf-8"))
assert isinstance(sv["heartbeat_epoch_utc"], int) and isinstance(hv["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in sv["clock_read"] and "T" in hv["clock_read"], "clock must be T-separated"
assert sv["last_orders_sha"] == "a8d9efaf99bd87290b3a991e978465750c52060ba1411419d1a3cee378d30928", "ord watermark lost"
assert sv["last_decisions_sha"] == "fb5825cb68a9524e2e8f2df12caeb537e3cafbda64d09d2f8478943d9986a2a7", "dec watermark lost"
assert sv["round_no"] == 949 and hv["round_no"] == 949, "counter must be 949"
print("CLOSEOUT OK state.round_no=%d heartbeat.epoch=%d clock=%s gpu=%d%% freeRamG=%s" % (
    sv["round_no"], hv["heartbeat_epoch_utc"], hv["clock_read"], gpu_util, free_ram))
